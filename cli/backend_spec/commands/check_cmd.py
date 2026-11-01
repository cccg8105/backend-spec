import re
import subprocess
from pathlib import Path
from typing import List, Set

from backend_spec.validator.schema_validator import (
    count_rolling_history_rows,
    extract_requirement_data,
    extract_use_case_data,
    load_json_schema,
    parse_yaml_frontmatter,
    validate_against_schema,
)

SOURCE_EXTENSIONS = {
    ".py", ".ts", ".tsx", ".js", ".jsx", ".go", ".rs", ".java", ".kt", ".cs", ".rb", ".php"
}
NON_SOURCE_PREFIXES = (
    "docs/",
    ".spec/",
    "tests/",
    "test/",
    ".gemini/",
    ".cursor/",
    ".claude/",
    ".windsurf/",
    ".github/",
    "migrations/",
)
EXPECTED_TECHNICAL_DOCS = (
    "database-model.md",
    "component-design.md",
    "api-contracts.md",
    "tech-stack.md",
    "deployment-strategy.md",
)


def _check_markdown_links(md_file: Path, errors: List[str]):
    content = md_file.read_text(encoding="utf-8")
    # Ignorar bloques de código cercados para no evaluar ejemplos
    stripped = re.sub(r"```.*?```", "", content, flags=re.DOTALL)
    for label, raw_target in re.findall(r"\[([^\]]+)\]\(([^)]+)\)", stripped):
        target = raw_target.strip().split()[0]
        if (
            not target
            or target.startswith(("http://", "https://", "mailto:", "#", "file:", "conversation:", "sidecar:"))
        ):
            continue
        clean_rel = target.split("#")[0]
        if not clean_rel:
            continue
        resolved = (md_file.parent / clean_rel).resolve()
        if not resolved.exists():
            errors.append(
                f"Enlace roto en '{md_file.name}': [{label}]({raw_target}) -> no existe '{clean_rel}'"
            )


def _is_source_code_path(rel_posix: str) -> bool:
    if rel_posix.startswith(NON_SOURCE_PREFIXES):
        return False
    p = Path(rel_posix)
    if len(p.parts) == 1:
        # Archivos sueltos de configuración en la raíz (ej. setup.py, vite.config.ts)
        return False
    return p.suffix.lower() in SOURCE_EXTENSIONS


def _verify_staged_commits(
    project_root: Path, declared_artifacts: Set[str], has_active_reqs: bool, errors: List[str]
):
    try:
        res = subprocess.run(
            ["git", "diff", "--cached", "--name-only"],
            cwd=str(project_root),
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=10,
        )
    except Exception:
        return

    if res.returncode != 0:
        return

    staged_files = [
        line.strip().replace("\\", "/")
        for line in res.stdout.splitlines()
        if line.strip()
    ]
    if not staged_files:
        return

    staged_source = [f for f in staged_files if _is_source_code_path(f)]
    if not staged_source:
        return

    changelog_staged = "docs/backlog/changelog.md" in staged_files
    docs_staged = any(f.startswith("docs/") for f in staged_files)

    # Si se está cerrando un requerimiento en este mismo commit (changelog.md en stage), es válido
    if changelog_staged:
        return

    if not has_active_reqs:
        errors.append(
            "Commit fantasma bloqueado: se intentan confirmar cambios en código fuente "
            f"({', '.join(staged_source[:5])}) sin ningún requerimiento activo en "
            "docs/backlog/pending.md ni cierre en changelog.md."
        )
        return

    # Verificar que los archivos de código modificados estén declarados dentro de las fronteras activas
    undeclared = [f for f in staged_source if f not in declared_artifacts]
    if undeclared and not docs_staged:
        errors.append(
            "Violación de fronteras (Commit fantasma parcial): los archivos en stage "
            f"({', '.join(undeclared[:5])}) no figuran en las 'Fronteras y Artefactos' de ningún "
            "REQ-* activo en docs/backlog/pending.md."
        )


def run_check(project_root: Path, check_staged: bool = False) -> bool:
    project_root = Path(project_root).resolve()
    docs_dir = project_root / "docs"

    print(f"\n🔍 Ejecutando verificación de integridad backend-spec v1.0 en: {docs_dir}")
    errors: List[str] = []
    warnings: List[str] = []

    if not docs_dir.exists():
        print("❌ Error: Directorio docs/ no encontrado. Ejecuta 'backend-spec init'.")
        return False

    uc_schema = load_json_schema("use-case.schema.json")
    req_schema = load_json_schema("requirement.schema.json")

    # 1. Verificar índices funcionales y casos de uso contra JSON Schema
    func_dir = docs_dir / "functional"
    func_index = func_dir / "index.md"
    use_cases_dir = func_dir / "use-cases"

    if not func_index.exists():
        errors.append("Falta el archivo obligatorio docs/functional/index.md")
    else:
        _check_markdown_links(func_index, errors)
        index_content = func_index.read_text(encoding="utf-8")

        uc_candidates: List[Path] = []
        if use_cases_dir.exists():
            for uc_file in sorted(use_cases_dir.glob("*.md")):
                if not uc_file.name.startswith("_"):
                    uc_candidates.append(uc_file)
                    if uc_file.name not in index_content:
                        warnings.append(
                            f"El caso de uso '{uc_file.name}' no está catalogado en docs/functional/index.md (ejecuta 'spec sync')"
                        )

        for domain_dir in sorted(func_dir.iterdir()):
            if domain_dir.is_dir() and domain_dir.name != "use-cases":
                domain_index = domain_dir / "index.md"
                if not domain_index.exists():
                    warnings.append(
                        f"Sub-dominio '{domain_dir.name}' no tiene sub-índice docs/functional/{domain_dir.name}/index.md"
                    )
                else:
                    _check_markdown_links(domain_index, errors)
                    dom_content = domain_index.read_text(encoding="utf-8")
                    for uc in sorted(domain_dir.rglob("*.md")):
                        if uc.name != "index.md" and not uc.name.startswith("_"):
                            uc_candidates.append(uc)
                            if uc.name not in dom_content:
                                warnings.append(
                                    f"El caso de uso '{uc.name}' no está catalogado en el sub-índice de {domain_dir.name}"
                                )

        for uc_path in uc_candidates:
            _check_markdown_links(uc_path, errors)
            uc_text = uc_path.read_text(encoding="utf-8")
            uc_data, has_fm = extract_use_case_data(uc_text)
            if not has_fm:
                warnings.append(
                    f"Caso de uso '{uc_path.name}': se recomienda añadir cabecera YAML Frontmatter"
                )
            if uc_schema:
                schema_errs = validate_against_schema(uc_data, uc_schema, path=uc_path.name)
                errors.extend(schema_errs)

    # 2. Verificar índices y existencia física de los 5 documentos técnicos
    tech_dir = docs_dir / "technical"
    tech_index = tech_dir / "index.md"
    if not tech_index.exists():
        errors.append("Falta el archivo obligatorio docs/technical/index.md")
    else:
        _check_markdown_links(tech_index, errors)
        tech_index_content = tech_index.read_text(encoding="utf-8")
        for tf in EXPECTED_TECHNICAL_DOCS:
            tf_path = tech_dir / tf
            if not tf_path.exists():
                errors.append(f"Falta el documento técnico obligatorio en disco: docs/technical/{tf}")
            else:
                _check_markdown_links(tf_path, errors)
                fm, _, has_fm = parse_yaml_frontmatter(tf_path.read_text(encoding="utf-8"))
                if not has_fm or not fm.get("artifact_type"):
                    warnings.append(
                        f"Documento técnico '{tf}' no incluye 'artifact_type' en su YAML Frontmatter"
                    )
            if tf not in tech_index_content:
                warnings.append(
                    f"El documento técnico '{tf}' no está referenciado en docs/technical/index.md"
                )

    # 3. Verificar backlog, pending.md, referencias físicas y fronteras
    backlog_index = docs_dir / "backlog" / "index.md"
    if backlog_index.exists():
        _check_markdown_links(backlog_index, errors)

    pending_file = docs_dir / "backlog" / "pending.md"
    declared_artifacts: Set[str] = set()
    has_active_reqs = False

    if not pending_file.exists():
        errors.append("Falta el archivo obligatorio docs/backlog/pending.md")
    else:
        content = pending_file.read_text(encoding="utf-8")
        raw_blocks = re.findall(
            r"(###\s*\[REQ-[^\]]+\].*?)(?=###\s*\[REQ-|\Z)", content, re.DOTALL
        )
        print(f"✔ Requerimientos activos analizados en backlog: {len(raw_blocks)}")
        has_active_reqs = len(raw_blocks) > 0

        for block in raw_blocks:
            req_data = extract_requirement_data(block)
            req_id = req_data["id"] or "REQ-UNKNOWN"

            if req_schema:
                req_errs = validate_against_schema(req_data, req_schema, path=req_id)
                errors.extend(req_errs)

            if not req_data["boundaries"]["artifacts"]:
                errors.append(
                    f"{req_id}: Debe declarar al menos un archivo en 'Artefactos a Modificar / Crear'"
                )
            if not req_data["acceptance_criteria"]:
                errors.append(
                    f"{req_id}: Debe incluir al menos una casilla '- [ ]' en 'Criterios de Aceptación'"
                )

            # Validar existencia física de Referencia Funcional (salvo PATCH Fast-Track con N/A)
            func_ref = req_data["references"]["functional"]
            is_patch = req_data["impact_type"] == "PATCH"
            if func_ref:
                if func_ref.upper().startswith("N/A"):
                    if not is_patch:
                        errors.append(
                            f"{req_id}: Solo los requerimientos de impacto PATCH (Fast-Track) pueden omitir Referencia Funcional ('N/A')"
                        )
                else:
                    if not (project_root / func_ref).exists():
                        errors.append(
                            f"{req_id}: La Referencia Funcional '{func_ref}' no existe en el repositorio"
                        )

            # Validar existencia física de Referencias Técnicas
            for t_ref in req_data["references"]["technical"]:
                if not t_ref.upper().startswith("N/A") and not (project_root / t_ref).exists():
                    errors.append(
                        f"{req_id}: La Referencia Técnica '{t_ref}' no existe en el repositorio"
                    )

            # Validar existencia física de archivos marcados [MODIFY] o [DELETE]
            for art in req_data["boundaries"]["artifacts"]:
                norm_path = art["path"].replace("\\", "/").lstrip("./")
                declared_artifacts.add(norm_path)
                if art["action"] in ("MODIFY", "DELETE") and not (project_root / norm_path).exists():
                    errors.append(
                        f"{req_id}: El archivo '{norm_path}' está marcado como [{art['action']}], pero no existe en disco"
                    )

    # 4. Verificar sintaxis básica de diagramas Mermaid y límite Rolling Window (máx 3 filas)
    valid_mermaid_types = (
        "flowchart",
        "sequenceDiagram",
        "classDiagram",
        "erDiagram",
        "stateDiagram",
        "graph",
    )
    for md_file in sorted(docs_dir.rglob("*.md")):
        md_text = md_file.read_text(encoding="utf-8")
        mermaid_blocks = re.findall(r"```mermaid\s+(.*?)\s+```", md_text, re.DOTALL)
        for b in mermaid_blocks:
            first_line = b.strip().splitlines()[0].strip() if b.strip() else ""
            if not any(first_line.startswith(vt) for vt in valid_mermaid_types):
                warnings.append(
                    f"Diagrama Mermaid sin encabezado estándar en {md_file.name}: '{first_line}'"
                )

        rev_rows = count_rolling_history_rows(md_text)
        if rev_rows > 3:
            warnings.append(
                f"Historial de Revisiones en '{md_file.relative_to(docs_dir).as_posix()}' tiene {rev_rows} filas (máximo Rolling Window: 3)"
            )

    # 5. Verificación Git Pre-commit contra commits fantasma (--staged)
    if check_staged:
        _verify_staged_commits(project_root, declared_artifacts, has_active_reqs, errors)

    # 6. Reporte final
    print("-" * 60)
    if warnings:
        print(f"⚠️  Advertencias encontradas ({len(warnings)}):")
        for w in warnings:
            print(f"   - {w}")
    else:
        print("✔ Cero advertencias de catálogo o Rolling Window.")

    if errors:
        print(f"\n❌ Errores de integridad detectados ({len(errors)}):")
        for e in errors:
            print(f"   - {e}")
        return False

    print("\n✅ ¡Todos los artefactos, enlaces y esquemas superaron la verificación con éxito!\n")
    return True
