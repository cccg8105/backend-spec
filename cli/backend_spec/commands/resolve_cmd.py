import datetime
import re
import subprocess
from pathlib import Path

from backend_spec.commands.sync_index_cmd import run_sync_index
from backend_spec.detector.version_extractor import (
    compare_versions,
    compute_next_milestone,
    extract_version,
    update_version,
)


def run_resolve(
    project_root: Path,
    req_id: str,
    auto_bump: bool = False,
    force_version: bool = False,
) -> bool:
    project_root = Path(project_root).resolve()
    docs_dir = project_root / "docs"
    pending_file = docs_dir / "backlog" / "pending.md"
    changelog_file = docs_dir / "backlog" / "changelog.md"

    if not pending_file.exists() or not changelog_file.exists():
        print("❌ Error: docs/backlog/pending.md o changelog.md no encontrados.")
        return False

    pending_content = pending_file.read_text(encoding="utf-8")

    pattern = rf"(###\s*\[{re.escape(req_id)}\].*?)(?=###\s*\[REQ-|\Z)"
    match = re.search(pattern, pending_content, re.DOTALL)

    if not match:
        print(f"❌ Error: Requerimiento {req_id} no encontrado en pending.md.")
        return False

    req_block = match.group(1).strip()
    # Retirar separadores '---' sobrantes al final del bloque capturado
    req_block = re.sub(r"(?:\r?\n---\s*)+\Z", "", req_block).strip()

    v_match = re.search(r"-\s*\*\*Versión Objetivo:\*\*\s*`?([^\n`]+)`?", req_block)
    target_version = v_match.group(1).strip() if v_match else "v0.1.0"
    if not target_version.startswith("v"):
        target_version = f"v{target_version}"

    # 1. Remover de pending.md y sincronizar índice de backlog
    new_pending = pending_content[: match.start()] + pending_content[match.end() :]
    new_pending = re.sub(r"\n{3,}", "\n\n", new_pending).rstrip() + "\n"
    pending_file.write_text(new_pending, encoding="utf-8")
    print(f"✔ Requerimiento {req_id} retirado de docs/backlog/pending.md")

    run_sync_index(project_root)

    # 2. Agregar a changelog.md SIN duplicar cabecera ### [REQ-ID]
    changelog_content = changelog_file.read_text(encoding="utf-8")
    today = datetime.date.today().isoformat()

    resolved_block = re.sub(r"-\s*\[ \]", "- [x]", req_block)
    # Inyectar fecha de resolución tras la primera línea de encabezado ### [REQ-ID]
    lines = resolved_block.splitlines()
    if lines:
        lines.insert(1, f"- **Fecha de Resolución:** `{today}`")
        resolved_block = "\n".join(lines)

    version_header_regex = rf"^##\s+Release\s+{re.escape(target_version)}\b[^\n]*"
    header_match = re.search(version_header_regex, changelog_content, re.MULTILINE)
    if header_match:
        end_pos = header_match.end()
        updated_changelog = (
            changelog_content[:end_pos]
            + f"\n\n{resolved_block}\n"
            + changelog_content[end_pos:]
        )
    else:
        new_release_section = (
            f"\n\n---\n\n## Release {target_version} (Actualizado: {today})\n\n"
            f"{resolved_block}\n"
        )
        updated_changelog = changelog_content.rstrip() + new_release_section

    changelog_file.write_text(updated_changelog, encoding="utf-8")
    print(f"✔ Requerimiento {req_id} registrado en docs/backlog/changelog.md")

    # 3. Sincronizar archivo de versión SOLO cuando auto_bump=True
    if auto_bump:
        config_file = project_root / ".spec" / "config.yaml"
        if config_file.exists():
            config_text = config_file.read_text(encoding="utf-8")
            path_match = re.search(r'^\s*path:\s*["\']?([^"\'\r\n]+)["\']?', config_text, re.MULTILINE)
            format_match = re.search(r'^\s*format:\s*["\']?([^"\'\r\n]+)["\']?', config_text, re.MULTILINE)
            scheme_match = re.search(r'^versioning_scheme:\s*["\']?([^"\'\r\n]+)["\']?', config_text, re.MULTILINE)
            scheme = scheme_match.group(1).strip() if scheme_match else "semver"

            if path_match and format_match:
                manifest_path = project_root / path_match.group(1).strip()
                manifest_fmt = format_match.group(1).strip()
                clean_ver = target_version.lstrip("vV")

                current_manifest_ver = extract_version(manifest_path, manifest_fmt)
                if (
                    current_manifest_ver
                    and compare_versions(clean_ver, current_manifest_ver) < 0
                    and not force_version
                ):
                    print(
                        f"⚠️  Protección anti-downgrade: la versión objetivo ({clean_ver}) es menor "
                        f"que la versión actual del manifiesto ({current_manifest_ver}). "
                        f"No se modificó {manifest_path.name} (usa --force-version para forzar)."
                    )
                else:
                    if manifest_path.exists() or manifest_fmt == "plain":
                        if update_version(manifest_path, manifest_fmt, clean_ver):
                            print(f"✔ Manifiesto {manifest_path.name} actualizado a la versión {clean_ver}")
                    next_ms = compute_next_milestone(clean_ver, scheme)
                    updated_cfg = re.sub(
                        r'^current_version:\s*["\']?[^"\'\r\n]+["\']?',
                        f'current_version: "{clean_ver}"',
                        config_text,
                        flags=re.MULTILINE,
                    )
                    updated_cfg = re.sub(
                        r'^current_milestone:\s*["\']?[^"\'\r\n]+["\']?',
                        f'current_milestone: "{next_ms}"',
                        updated_cfg,
                        flags=re.MULTILINE,
                    )
                    config_file.write_text(updated_cfg, encoding="utf-8")

    # 4. Sincronizar grafo de conocimiento si existe graphify-out/
    graphify_out = project_root / "graphify-out"
    if graphify_out.exists():
        try:
            res = subprocess.run(
                ["graphify", "update"],
                cwd=str(project_root),
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=30,
            )
            if res.returncode == 0:
                print("✔ Grafo de conocimiento graphify-out/ actualizado con 'graphify update'.")
            else:
                print(
                    "⚠️  No se pudo actualizar graphify-out/ automáticamente "
                    f"(código {res.returncode}). Ejecuta 'graphify update' o '/graphify . --update'."
                )
        except FileNotFoundError:
            print(
                "ℹ️  Directorio graphify-out/ detectado, pero 'graphify' no está en PATH. "
                "Recuerda ejecutar '/graphify . --update' desde tu agente."
            )
        except Exception as exc:
            print(f"⚠️  Aviso al invocar 'graphify update': {exc}")

    print(f"\n🎉 ¡{req_id} resuelto y auditado correctamente!\n")
    return True
