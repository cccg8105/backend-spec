import datetime
import os
import re
import shutil
import stat
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

from backend_spec.commands.check_cmd import run_check
from backend_spec.commands.sync_index_cmd import run_sync_index
from backend_spec.detector.ecosystem_detector import detect_ecosystem, ECOSYSTEM_SIGNATURES
from backend_spec.detector.version_extractor import extract_version
from backend_spec.validator.schema_validator import locate_framework_asset

HARNESS_DETECTION_PATHS = {
    "antigravity": [Path(".gemini/rules/backend-spec.md"), Path(".gemini/skills/backend-spec")],
    "cursor": [Path(".cursor/rules/backend-spec.mdc"), Path(".cursor/commands")],
    "claude": [Path("CLAUDE.md"), Path(".claude/commands")],
    "windsurf": [Path(".windsurfrules"), Path(".windsurf/workflows")],
}


def _detect_installed_harnesses(target_dir: Path) -> List[str]:
    detected = []
    for h_name, paths in HARNESS_DETECTION_PATHS.items():
        if any((target_dir / p).exists() for p in paths):
            detected.append(h_name)
    return detected


def _update_managed_markdown(dest_path: Path, template_path: Path, dry_run: bool = False) -> str:
    template_content = template_path.read_text(encoding="utf-8")
    tmpl_match = re.search(
        r"<!-- BACKEND-SPEC:START -->(.*?)<!-- BACKEND-SPEC:END -->",
        template_content,
        re.DOTALL,
    )
    new_managed_block = tmpl_match.group(1).strip() if tmpl_match else template_content.strip()
    full_managed_section = f"<!-- BACKEND-SPEC:START -->\n{new_managed_block}\n<!-- BACKEND-SPEC:END -->"

    if not dest_path.exists():
        if not dry_run:
            dest_path.parent.mkdir(parents=True, exist_ok=True)
            dest_path.write_text(template_content, encoding="utf-8")
        return "CREATED"

    dest_content = dest_path.read_text(encoding="utf-8")
    dest_match = re.search(
        r"<!-- BACKEND-SPEC:START -->.*?<!-- BACKEND-SPEC:END -->",
        dest_content,
        re.DOTALL,
    )
    if dest_match:
        updated_content = (
            dest_content[: dest_match.start()]
            + full_managed_section
            + dest_content[dest_match.end() :]
        )
        if not dry_run:
            dest_path.write_text(updated_content, encoding="utf-8")
        return "UPDATED_BLOCK"

    # Archivo pre-existente sin marcadores
    legacy_indicators = [
        "# Instrucciones del Proyecto: backend-spec",
        "# Regla de Trabajo: backend-spec",
        "# backend-spec Rules for Windsurf",
    ]
    is_pure_legacy = any(ind in dest_content for ind in legacy_indicators)
    fm_match = re.match(r"\A---\s*\r?\n(.*?)\r?\n---\s*(?:\r?\n|$)", dest_content, re.DOTALL)

    if is_pure_legacy:
        if not dry_run:
            dest_path.write_text(template_content, encoding="utf-8")
        return "MIGRATED_TO_MANAGED"
    else:
        # El usuario tenía reglas o contenido propio en este archivo
        if fm_match:
            fm = dest_content[: fm_match.end()]
            rest = dest_content[fm_match.end() :].strip()
            updated_content = f"{fm}\n{full_managed_section}\n\n<!-- Custom Project Rules -->\n{rest}\n"
        else:
            updated_content = f"{full_managed_section}\n\n<!-- Custom Project Rules -->\n{dest_content.strip()}\n"
        if not dry_run:
            dest_path.write_text(updated_content, encoding="utf-8")
        return "MERGED_PRESERVING_USER_CONTENT"


def _merge_graphifyignore(dest_path: Path, template_path: Path, dry_run: bool = False) -> int:
    if not dest_path.exists():
        if not dry_run:
            dest_path.write_text(template_path.read_text(encoding="utf-8"), encoding="utf-8")
        return -1

    existing_lines = dest_path.read_text(encoding="utf-8").splitlines()
    existing_stripped = {
        l.strip() for l in existing_lines if l.strip() and not l.strip().startswith("#")
    }

    tmpl_lines = template_path.read_text(encoding="utf-8").splitlines()
    added_lines = []
    for l in tmpl_lines:
        s = l.strip()
        if s and not s.startswith("#") and s not in existing_stripped:
            added_lines.append(l)
            existing_stripped.add(s)

    if added_lines and not dry_run:
        new_content = (
            dest_path.read_text(encoding="utf-8").rstrip()
            + "\n\n# backend-spec additions\n"
            + "\n".join(added_lines)
            + "\n"
        )
        dest_path.write_text(new_content, encoding="utf-8")
    return len(added_lines)


def _update_pre_commit_hook(target_dir: Path, hook_src: Path, dry_run: bool = False) -> str:
    git_dir = target_dir / ".git"
    if not git_dir.exists() or not git_dir.is_dir():
        return "NO_GIT"

    hooks_dir = git_dir / "hooks"
    hook_dest = hooks_dir / "pre-commit"

    hook_src_content = hook_src.read_text(encoding="utf-8")
    tmpl_match = re.search(
        r"# BACKEND-SPEC:START(.*?)# BACKEND-SPEC:END", hook_src_content, re.DOTALL
    )
    managed_block = (
        tmpl_match.group(1).strip() if tmpl_match else hook_src_content.strip()
    )
    full_managed_section = f"# BACKEND-SPEC:START\n{managed_block}\n# BACKEND-SPEC:END"

    if not hook_dest.exists():
        if not dry_run:
            hooks_dir.mkdir(parents=True, exist_ok=True)
            hook_dest.write_text(hook_src_content, encoding="utf-8")
            try:
                hook_dest.chmod(hook_dest.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
            except Exception:
                pass
        return "CREATED"

    current_dest = hook_dest.read_text(encoding="utf-8", errors="ignore")
    if "# BACKEND-SPEC:START" in current_dest and "# BACKEND-SPEC:END" in current_dest:
        dest_match = re.search(
            r"# BACKEND-SPEC:START.*?# BACKEND-SPEC:END", current_dest, re.DOTALL
        )
        updated = (
            current_dest[: dest_match.start()]
            + full_managed_section
            + current_dest[dest_match.end() :]
        )
        if not dry_run:
            hook_dest.write_text(updated, encoding="utf-8")
        return "UPDATED_BLOCK"

    if "backend-spec" in current_dest:
        # Era un hook v0.x de backend-spec completo
        if not dry_run:
            hook_dest.write_text(hook_src_content, encoding="utf-8")
        return "REPLACED_LEGACY"

    # Es un hook ajeno (husky, linters del usuario, etc.) -> inyectar managed block sin borrarlo
    exit_match = re.search(r"(?m)^\s*exit\s+0\s*$", current_dest)
    if exit_match:
        updated = (
            current_dest[: exit_match.start()]
            + f"\n{full_managed_section}\n\n"
            + current_dest[exit_match.start() :]
        )
    else:
        updated = current_dest.rstrip() + f"\n\n{full_managed_section}\n"

    if not dry_run:
        hook_dest.write_text(updated, encoding="utf-8")
        try:
            hook_dest.chmod(hook_dest.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
        except Exception:
            pass
    return "INJECTED_INTO_EXISTING"


def _install_harness_skills(
    target_dir: Path,
    templates_root: Path,
    harnesses_root: Path,
    harness: str,
    dry_run: bool = False,
) -> List[str]:
    installed_items: List[str] = []
    skills_src = templates_root / ".spec" / "skills"
    if not skills_src.exists():
        return installed_items

    # 1. Resolver triggers y estrategias
    triggers = {
        "antigravity": "/grill-me",
        "claude": "/spec-grill",
        "cursor": "/spec-grill",
        "windsurf": "/spec-grill",
    }
    interview_trigger = triggers.get(harness, "/spec-grill")

    question_strategies = {
        "claude": "   - **Herramienta Interactiva (`AskUserQuestion`):** Presenta de 2 a 4 decisiones independientes por ronda con sus opciones ordenadas, colocando primero `(Recommended)` y resumiendo brevemente los trade-offs.",
        "cursor": "   - **Herramienta Interactiva (`AskQuestion`):** Presenta de 2 a 4 decisiones por tarjeta interactiva, anteponiendo la opción `(Recommended)` con una línea de justificación.",
        "windsurf": "   - **Pausa Estructurada en Chat (`A/B/C`):** Presenta de 2 a 4 preguntas con opciones `A) (Recomendado) ... / B) ... / C) ...` y **detén la ejecución** hasta que el usuario responda explícitamente antes de editar archivos.",
    }

    def _render_skill_text(raw_text: str) -> str:
        res = raw_text.replace("{{HARNESS_INTERVIEW_TRIGGER}}", interview_trigger)
        strat = question_strategies.get(harness, "   - Realiza preguntas concisas de opción múltiple con opción recomendada.")
        res = res.replace("{{HARNESS_QUESTION_STRATEGY}}", strat)
        return res

    if harness == "antigravity":
        # Antigravity instala backend-spec y backend-spec-bootstrap (conserva /grill-me nativo)
        skills_dest = target_dir / ".gemini" / "skills"
        for sk in ("backend-spec", "backend-spec-bootstrap"):
            src_file = skills_src / sk / "SKILL.md"
            if src_file.exists():
                dest_file = skills_dest / sk / "SKILL.md"
                if not dry_run:
                    dest_file.parent.mkdir(parents=True, exist_ok=True)
                    dest_file.write_text(_render_skill_text(src_file.read_text(encoding="utf-8")), encoding="utf-8")
                installed_items.append(f".gemini/skills/{sk}/SKILL.md")

    elif harness == "cursor":
        skills_dest = target_dir / ".cursor" / "skills"
        for sk in ("backend-spec", "backend-spec-bootstrap", "spec-grill"):
            src_file = skills_src / sk / "SKILL.md"
            if src_file.exists():
                dest_file = skills_dest / sk / "SKILL.md"
                if not dry_run:
                    dest_file.parent.mkdir(parents=True, exist_ok=True)
                    dest_file.write_text(_render_skill_text(src_file.read_text(encoding="utf-8")), encoding="utf-8")
                installed_items.append(f".cursor/skills/{sk}/SKILL.md")

    elif harness == "claude":
        skills_dest = target_dir / ".claude" / "skills"
        for sk in ("backend-spec", "backend-spec-bootstrap", "spec-grill"):
            src_file = skills_src / sk / "SKILL.md"
            if src_file.exists():
                dest_file = skills_dest / sk / "SKILL.md"
                if not dry_run:
                    dest_file.parent.mkdir(parents=True, exist_ok=True)
                    dest_file.write_text(_render_skill_text(src_file.read_text(encoding="utf-8")), encoding="utf-8")
                installed_items.append(f".claude/skills/{sk}/SKILL.md")

    elif harness == "windsurf":
        skills_dest = target_dir / ".windsurf" / "skills"
        for sk in ("backend-spec", "backend-spec-bootstrap", "spec-grill"):
            src_file = skills_src / sk / "SKILL.md"
            if src_file.exists():
                dest_file = skills_dest / sk / "SKILL.md"
                if not dry_run:
                    dest_file.parent.mkdir(parents=True, exist_ok=True)
                    dest_file.write_text(_render_skill_text(src_file.read_text(encoding="utf-8")), encoding="utf-8")
                installed_items.append(f".windsurf/skills/{sk}/SKILL.md")

    return installed_items


def _migrate_legacy_docs_and_config(
    target_dir: Path, templates_root: Path, dry_run: bool = False
) -> Dict[str, List[str]]:
    summary = {
        "cleaned_templates": [],
        "created_docs": [],
        "updated_index": [],
    }

    docs_dir = target_dir / "docs"
    tech_dir = docs_dir / "technical"
    func_dir = docs_dir / "functional"
    backlog_dir = docs_dir / "backlog"

    # 1. Limpieza de _template_*.md legados que estaban en docs/
    legacy_files = [
        tech_dir / "_template_database.md",
        tech_dir / "_template_components.md",
        tech_dir / "_template_tech_stack.md",
        tech_dir / "_template_deployment.md",
        tech_dir / "_template_test_spec.md",
        func_dir / "ocl-guidelines.md",
        func_dir / "use-cases" / "_template.md",
    ]
    for lf in legacy_files:
        if lf.exists():
            summary["cleaned_templates"].append(lf.name)
            if not dry_run:
                try:
                    lf.unlink()
                except Exception:
                    pass

    # 2. Creación no-destructiva de nuevos pilares en docs/
    clean_docs_src = templates_root / ".spec" / "docs"
    config_file = target_dir / ".spec" / "config.yaml"
    cfg_text = config_file.read_text(encoding="utf-8") if config_file.exists() else ""

    proj_name = target_dir.name
    ver_match = re.search(r'current_version:\s*["\']?([^"\'\r\n]+)["\']?', cfg_text)
    cur_ver = ver_match.group(1).strip() if ver_match else "0.1.0"
    rt_match = re.search(r'runtime_name:\s*["\']?([^"\'\r\n]+)["\']?', cfg_text)
    rt_name = rt_match.group(1).strip() if rt_match else "Backend"

    placeholders = {
        "PROJECT_NAME": proj_name,
        "CURRENT_VERSION": cur_ver,
        "MILESTONE_VERSION": f"v{cur_ver}",
        "RUNTIME_NAME": rt_name,
        "MANIFEST_FILE": "package.json",
        "SRC_EXT": ".ts",
        "VERSIONING_SCHEME": "semver",
        "VERSIONING_SCHEME_LABEL": "SemVer 2.0.0",
        "TODAY": datetime.date.today().isoformat(),
    }

    # Verificar docs/technical/api-contracts.md
    target_api_contracts = tech_dir / "api-contracts.md"
    src_api_contracts = clean_docs_src / "technical" / "api-contracts.md"
    if src_api_contracts.exists() and not target_api_contracts.exists():
        raw_text = src_api_contracts.read_text(encoding="utf-8")
        rendered = raw_text
        for k, v in placeholders.items():
            rendered = rendered.replace(f"{{{{{k}}}}}", v)
        summary["created_docs"].append("docs/technical/api-contracts.md")
        if not dry_run:
            tech_dir.mkdir(parents=True, exist_ok=True)
            target_api_contracts.write_text(rendered, encoding="utf-8")

    # Inyectar api-contracts.md en docs/technical/index.md si no está
    tech_index = tech_dir / "index.md"
    if tech_index.exists():
        idx_content = tech_index.read_text(encoding="utf-8")
        if "api-contracts.md" not in idx_content:
            row_insert = (
                "| **Contratos API, Eventos y RNFs** | [api-contracts.md](./api-contracts.md) | "
                "Endpoints HTTP/gRPC, catálogo de eventos asíncronos, idempotencia, concurrencia, seguridad RBAC y SLAs. |\n"
            )
            table_header_match = re.search(r"\|\s*Artefacto\s*\|\s*Archivo\s*\|[^\n]*\n\|[ :|-]+\|\n", idx_content)
            if table_header_match:
                end_pos = table_header_match.end()
                idx_content = idx_content[:end_pos] + row_insert + idx_content[end_pos:]
                summary["updated_index"].append("docs/technical/index.md")
                if not dry_run:
                    tech_index.write_text(idx_content, encoding="utf-8")

    # Verificar docs/backlog/audit-proposals.md
    target_audit_file = backlog_dir / "audit-proposals.md"
    src_audit_file = clean_docs_src / "backlog" / "audit-proposals.md"
    if src_audit_file.exists() and not target_audit_file.exists():
        raw_text = src_audit_file.read_text(encoding="utf-8")
        rendered = raw_text
        for k, v in placeholders.items():
            rendered = rendered.replace(f"{{{{{k}}}}}", v)
        summary["created_docs"].append("docs/backlog/audit-proposals.md")
        if not dry_run:
            backlog_dir.mkdir(parents=True, exist_ok=True)
            target_audit_file.write_text(rendered, encoding="utf-8")

    # Inyectar audit-proposals.md en docs/backlog/index.md si no está
    backlog_index = backlog_dir / "index.md"
    if backlog_index.exists():
        b_idx_content = backlog_index.read_text(encoding="utf-8")
        if "audit-proposals.md" not in b_idx_content:
            audit_row = "| [audit-proposals.md](./audit-proposals.md) | **Auditoría y Mejoras:** Buzón de deuda técnica, discrepancias (*doc drift*) y hallazgos Brownfield en espera de promoción. |\n"
            m_pend = re.search(r"\|\s*\[pending\.md\][^\n]+\n", b_idx_content)
            if m_pend:
                ins_pos = m_pend.end()
                b_idx_content = b_idx_content[:ins_pos] + audit_row + b_idx_content[ins_pos:]
                summary["updated_index"].append("docs/backlog/index.md")
                if not dry_run:
                    backlog_index.write_text(b_idx_content, encoding="utf-8")

    # Inyectar sección PENDING_DOMAINS en docs/functional/index.md si no está
    func_index = func_dir / "index.md"
    if func_index.exists():
        f_idx_content = func_index.read_text(encoding="utf-8")
        if "SYNC:PENDING_DOMAINS:START" not in f_idx_content:
            pending_sec = (
                "\n\n---\n\n## Módulos Legados Detectados (Modo Progresivo — Pendientes de Levantamiento As-Is)\n\n"
                "<!-- SYNC:PENDING_DOMAINS:START -->\n_Sin dominios legados pendientes de levantamiento._\n<!-- SYNC:PENDING_DOMAINS:END -->\n"
            )
            m_conv = re.search(r"\n---\s*\n##\s+Convenciones", f_idx_content)
            if m_conv:
                pos = m_conv.start()
                f_idx_content = f_idx_content[:pos] + pending_sec + f_idx_content[pos:]
            else:
                f_idx_content = f_idx_content.rstrip() + pending_sec
            summary["updated_index"].append("docs/functional/index.md")
            if not dry_run:
                func_index.write_text(f_idx_content, encoding="utf-8")

    return summary


def _migrate_config_yaml(
    target_dir: Path, installed_harnesses: List[str], dry_run: bool = False
):
    config_file = target_dir / ".spec" / "config.yaml"
    if not config_file.exists():
        return

    content = config_file.read_text(encoding="utf-8")

    # 1. Asegurar version: "1.1.0"
    content = re.sub(
        r'^version:\s*["\']?[^"\'\r\n]+["\']?',
        'version: "1.1.0"',
        content,
        flags=re.MULTILINE,
    )

    # 2. Asegurar paths.templates
    if "templates:" not in content:
        content = re.sub(
            r"(paths:\s*(?:\r?\n\s+[A-Za-z0-9_-]+:\s*[^\r\n]+)+)",
            r'\1\n  templates: ".spec/templates"',
            content,
            count=1,
        )

    # 3. Guardar lista de harnesses
    harnesses_yaml = "harnesses:\n" + "\n".join(f"  - {h}" for h in installed_harnesses)
    if "harnesses:" in content:
        content = re.sub(
            r"harnesses:\s*(?:\r?\n\s*-\s*[^\r\n]+)+",
            harnesses_yaml,
            content,
            count=1,
        )
    else:
        content = content.rstrip() + f"\n\n{harnesses_yaml}\n"

    # 4. Asegurar campos de ecosistema si faltaban (de v0.x)
    if "ecosystem:" not in content:
        detection = detect_ecosystem(target_dir)
        sig = detection.get("detected")
        if sig:
            extra = (
                f'ecosystem: "{sig["ecosystem"]}"\n'
                f'runtime_name: "{sig["name"]}"\n'
                f'src_ext: "{sig["src_ext"]}"\n'
                f'src_dir: "{sig["src_dir"]}"\n'
                f'test_pattern: "{sig["test_pattern"]}"'
            )
            content = re.sub(
                r'(project_name:\s*["\']?[^"\'\r\n]+["\']?)',
                r"\1\n" + extra,
                content,
                count=1,
            )

    if not dry_run:
        config_file.write_text(content, encoding="utf-8")


def run_update(
    target_dir: Path,
    harness: Optional[str] = None,
    dry_run: bool = False,
) -> bool:
    target_dir = Path(target_dir).resolve()
    spec_dir = target_dir / ".spec"
    docs_dir = target_dir / "docs"

    if not spec_dir.exists() and not docs_dir.exists():
        print(
            f"❌ Error: {target_dir} no parece ser un proyecto backend-spec (no tiene .spec/ ni docs/)."
        )
        print("👉 Ejecuta 'backend-spec init' para inicializarlo por primera vez.")
        return False

    prefix = "[DRY-RUN] " if dry_run else ""
    print(f"\n🔄 {prefix}Actualizando framework backend-spec a v1.1 en: {target_dir}")

    templates_root = locate_framework_asset("templates")
    harnesses_root = locate_framework_asset("harnesses")

    if not templates_root or not harnesses_root:
        raise RuntimeError("No se encontraron los recursos base de backend-spec.")

    # 1. Determinar harnesses a actualizar
    installed_harnesses = _detect_installed_harnesses(target_dir)
    if harness:
        if harness == "all":
            for h in ("antigravity", "cursor", "claude", "windsurf"):
                if h not in installed_harnesses:
                    installed_harnesses.append(h)
        elif harness in ("antigravity", "cursor", "claude", "windsurf"):
            if harness not in installed_harnesses:
                installed_harnesses.append(harness)

    if not installed_harnesses:
        installed_harnesses = ["antigravity"]

    # 2. Refrescar Blueprints en .spec/templates/
    blueprints_src = templates_root / ".spec" / "templates"
    blueprints_dest = spec_dir / "templates"
    updated_bp_count = 0
    if blueprints_src.exists():
        if not dry_run:
            blueprints_dest.mkdir(parents=True, exist_ok=True)
        for bp in blueprints_src.glob("*.md"):
            dest_bp = blueprints_dest / bp.name
            if not dry_run:
                shutil.copy2(bp, dest_bp)
            updated_bp_count += 1
        print(f"✔ {prefix}Blueprints actualizados en .spec/templates/ ({updated_bp_count} archivos)")

    # 3. Migración estructural limpia en docs/
    doc_mig = _migrate_legacy_docs_and_config(target_dir, templates_root, dry_run=dry_run)
    if doc_mig["cleaned_templates"]:
        print(
            f"✔ {prefix}Limpiadas {len(doc_mig['cleaned_templates'])} plantillas legadas que residían en docs/: "
            f"{', '.join(doc_mig['cleaned_templates'])}"
        )
    if doc_mig["created_docs"]:
        print(f"✔ {prefix}Creado pilar técnico/backlog faltante: {', '.join(doc_mig['created_docs'])}")
    if doc_mig["updated_index"]:
        print(f"✔ {prefix}Actualizados índices de navegación: {', '.join(doc_mig['updated_index'])}")

    # 4. Migrar .spec/config.yaml
    _migrate_config_yaml(target_dir, installed_harnesses, dry_run=dry_run)
    print(f"✔ {prefix}Configuración .spec/config.yaml actualizada con versión 1.1.0 y harnesses")

    # 5. Actualizar Harnesses preservando reglas del usuario e instalando skills
    for h in installed_harnesses:
        if h == "antigravity":
            dest_rule = target_dir / ".gemini" / "rules" / "backend-spec.md"
            src_rule = harnesses_root / "antigravity" / "rules" / "backend-spec.md"
            res = _update_managed_markdown(dest_rule, src_rule, dry_run=dry_run)
            print(f"✔ {prefix}Adaptador Antigravity (.gemini/rules/backend-spec.md): {res}")

            skills_inst = _install_harness_skills(target_dir, templates_root, harnesses_root, h, dry_run=dry_run)
            if skills_inst:
                print(f"✔ {prefix}Skills Antigravity instaladas: {', '.join(skills_inst)}")

        elif h == "cursor":
            dest_rule = target_dir / ".cursor" / "rules" / "backend-spec.mdc"
            src_rule = harnesses_root / "cursor" / "rules" / "backend-spec.mdc"
            res = _update_managed_markdown(dest_rule, src_rule, dry_run=dry_run)
            print(f"✔ {prefix}Adaptador Cursor (.cursor/rules/backend-spec.mdc): {res}")

            cmd_src = templates_root / ".cursor" / "commands"
            cmd_dest = target_dir / ".cursor" / "commands"
            if cmd_src.exists():
                if not dry_run:
                    cmd_dest.mkdir(parents=True, exist_ok=True)
                for f in cmd_src.glob("*.md"):
                    if not dry_run:
                        shutil.copy2(f, cmd_dest / f.name)
                print(f"✔ {prefix}Comandos de Cursor actualizados en .cursor/commands/")

            skills_inst = _install_harness_skills(target_dir, templates_root, harnesses_root, h, dry_run=dry_run)
            if skills_inst:
                print(f"✔ {prefix}Skills Cursor instaladas: {', '.join(skills_inst)}")

        elif h == "claude":
            dest_rule = target_dir / "CLAUDE.md"
            src_rule = harnesses_root / "claude" / "CLAUDE.md"
            res = _update_managed_markdown(dest_rule, src_rule, dry_run=dry_run)
            print(f"✔ {prefix}Adaptador Claude Code (CLAUDE.md): {res}")

            cmd_src = templates_root / ".claude" / "commands"
            cmd_dest = target_dir / ".claude" / "commands"
            if cmd_src.exists():
                if not dry_run:
                    cmd_dest.mkdir(parents=True, exist_ok=True)
                for f in cmd_src.glob("*.md"):
                    if not dry_run:
                        shutil.copy2(f, cmd_dest / f.name)
                print(f"✔ {prefix}Comandos de Claude Code actualizados en .claude/commands/")

            skills_inst = _install_harness_skills(target_dir, templates_root, harnesses_root, h, dry_run=dry_run)
            if skills_inst:
                print(f"✔ {prefix}Skills Claude Code instaladas: {', '.join(skills_inst)}")

        elif h == "windsurf":
            dest_rule = target_dir / ".windsurfrules"
            src_rule = harnesses_root / "windsurf" / ".windsurfrules"
            res = _update_managed_markdown(dest_rule, src_rule, dry_run=dry_run)
            print(f"✔ {prefix}Adaptador Windsurf (.windsurfrules): {res}")

            wf_src = templates_root / ".windsurf" / "workflows"
            wf_dest = target_dir / ".windsurf" / "workflows"
            if wf_src.exists():
                if not dry_run:
                    wf_dest.mkdir(parents=True, exist_ok=True)
                for f in wf_src.glob("*.md"):
                    if not dry_run:
                        shutil.copy2(f, wf_dest / f.name)
                print(f"✔ {prefix}Workflows de Windsurf actualizados en .windsurf/workflows/")

            skills_inst = _install_harness_skills(target_dir, templates_root, harnesses_root, h, dry_run=dry_run)
            if skills_inst:
                print(f"✔ {prefix}Skills Windsurf instaladas: {', '.join(skills_inst)}")

    # 6. Fusión aditiva en .graphifyignore
    graphify_src = templates_root / ".graphifyignore"
    graphify_dest = target_dir / ".graphifyignore"
    if graphify_src.exists():
        added = _merge_graphifyignore(graphify_dest, graphify_src, dry_run=dry_run)
        if added > 0:
            print(f"✔ {prefix}.graphifyignore actualizado (+{added} patrones nuevos fusionados)")
        else:
            print(f"✔ {prefix}.graphifyignore al día (cero duplicados)")

    # 7. Actualización del hook pre-commit
    hook_src = templates_root / ".githooks" / "pre-commit"
    if hook_src.exists():
        hook_res = _update_pre_commit_hook(target_dir, hook_src, dry_run=dry_run)
        if hook_res != "NO_GIT":
            print(f"✔ {prefix}Git hook .git/hooks/pre-commit: {hook_res}")

    # 8. Sincronizar y validar si no es dry-run
    if not dry_run:
        print("\n🔍 Verificando integridad tras la actualización...")
        run_sync_index(target_dir)
        check_ok = run_check(target_dir)
        if check_ok:
            print("✨ ¡Proyecto actualizado exitosamente y verificado al 100%!\n")
        else:
            print("⚠️  Actualización completada con advertencias en la verificación.\n")
        return check_ok
    else:
        print(f"\n✨ {prefix}Previsualización completada (cero archivos modificados en disco).\n")
        return True
