import re
from pathlib import Path
from typing import List, Set, Tuple

from backend_spec.validator.schema_validator import (
    extract_requirement_data,
    extract_use_case_data,
)


def _replace_sync_section(
    doc_text: str, marker: str, fallback_heading_regex: str, new_block: str
) -> str:
    start_tag = f"<!-- SYNC:{marker}:START -->"
    end_tag = f"<!-- SYNC:{marker}:END -->"

    if start_tag in doc_text and end_tag in doc_text:
        pattern = re.compile(
            rf"{re.escape(start_tag)}.*?{re.escape(end_tag)}", re.DOTALL
        )
        replacement = f"{start_tag}\n{new_block.strip()}\n{end_tag}"
        return pattern.sub(lambda _: replacement, doc_text, count=1)

    heading_match = re.search(fallback_heading_regex, doc_text)
    if heading_match:
        insert_start = heading_match.end()
        next_sec = re.search(r"\n---\s*\n|\n##\s+", doc_text[insert_start:])
        if next_sec:
            end_pos = insert_start + next_sec.start()
            return (
                doc_text[:insert_start]
                + f"\n\n{start_tag}\n{new_block.strip()}\n{end_tag}\n"
                + doc_text[end_pos:]
            )
        return (
            doc_text[:insert_start].rstrip()
            + f"\n\n{start_tag}\n{new_block.strip()}\n{end_tag}\n"
        )

    return doc_text.rstrip() + f"\n\n{start_tag}\n{new_block.strip()}\n{end_tag}\n"


def _discover_use_case_files(func_dir: Path) -> List[Path]:
    files: List[Path] = []
    flat_dir = func_dir / "use-cases"
    if flat_dir.exists():
        for md in sorted(flat_dir.glob("*.md")):
            if not md.name.startswith("_") and md.name != "index.md":
                files.append(md)

    for sub in sorted(func_dir.iterdir()):
        if sub.is_dir() and sub.name != "use-cases":
            for md in sorted(sub.rglob("*.md")):
                if not md.name.startswith("_") and md.name != "index.md":
                    files.append(md)
    return files


def _read_detected_domains(project_root: Path) -> List[str]:
    report_file = project_root / ".spec" / "bootstrap-report.md"
    config_file = project_root / ".spec" / "config.yaml"
    domains: Set[str] = set()

    if report_file.exists():
        try:
            text = report_file.read_text(encoding="utf-8")
            m = re.search(r"-\s*\*\*Dominios Sugeridos:\*\*\s*(.+)", text)
            if m:
                raw_domains = re.findall(r"`([a-zA-Z0-9_-]+)`", m.group(1))
                domains.update(raw_domains)
        except Exception:
            pass

    if not domains and config_file.exists():
        try:
            cfg_text = config_file.read_text(encoding="utf-8")
            m_doms = re.findall(r"-\s*([a-zA-Z0-9_-]+)", cfg_text)
            domains.update(m_doms)
        except Exception:
            pass

    return sorted(domains)


def run_sync_index(project_root: Path) -> Tuple[int, int]:
    """
    Sincroniza en disco docs/backlog/index.md y docs/functional/index.md.
    Retorna (cantidad_reqs_sincronizados, cantidad_casos_uso_sincronizados).
    """
    project_root = Path(project_root).resolve()
    docs_dir = project_root / "docs"

    if not docs_dir.exists():
        print("❌ Error: docs/ no encontrado.")
        return 0, 0

    print("\n🔄 Sincronizando catálogos index.md en disco...")
    synced_reqs = 0
    synced_ucs = 0

    # 1. Sincronizar docs/backlog/index.md desde docs/backlog/pending.md
    pending_file = docs_dir / "backlog" / "pending.md"
    backlog_index = docs_dir / "backlog" / "index.md"

    if pending_file.exists() and backlog_index.exists():
        pending_content = pending_file.read_text(encoding="utf-8")
        req_blocks = re.findall(
            r"(###\s*\[REQ-[A-Z0-9]+-[0-9]+\].*?)(?=###\s*\[REQ-|\Z)",
            pending_content,
            re.DOTALL,
        )

        rows: List[str] = []
        for raw_block in req_blocks:
            req_data = extract_requirement_data(raw_block)
            req_id = req_data["id"]
            if not req_id:
                continue
            criteria = req_data["acceptance_criteria"]
            if criteria and all(c["completed"] for c in criteria):
                status = "Completado"
            elif any(c["completed"] for c in criteria):
                status = "En Progreso"
            else:
                status = "Pendiente"

            func_ref = req_data["references"]["functional"] or "N/A"
            tech_refs = ", ".join(f"`{t}`" for t in req_data["references"]["technical"]) or "N/A"
            func_disp = f"`{func_ref}`" if not func_ref.startswith("`") else func_ref
            rows.append(
                f"| `{req_id}` | {req_data['title']} | `{req_data['impact_type'] or 'MINOR'}` | "
                f"`{req_data['priority'] or 'P2'}` | {status} | {func_disp} | {tech_refs} |"
            )

        synced_reqs = len(rows)
        if rows:
            table_md = (
                "| ID Requerimiento | Título | Impacto | Prioridad | Estado | Ref. Funcional | Ref. Técnica |\n"
                "| :--- | :--- | :--- | :--- | :--- | :--- | :--- |\n"
                + "\n".join(rows)
            )
        else:
            table_md = "_Sin requerimientos pendientes en el milestone actual._"

        idx_text = backlog_index.read_text(encoding="utf-8")
        updated_idx = _replace_sync_section(
            idx_text,
            "BACKLOG_TABLE",
            r"##\s+Resumen del Milestone Activo[^\n]*",
            table_md,
        )
        backlog_index.write_text(updated_idx, encoding="utf-8")
        print(f"✔ Sincronizados {synced_reqs} requerimientos en docs/backlog/index.md")

    # 2. Sincronizar docs/functional/index.md desde docs/functional/**/use-cases/*.md
    func_dir = docs_dir / "functional"
    func_index = func_dir / "index.md"
    if func_dir.exists() and func_index.exists():
        uc_files = _discover_use_case_files(func_dir)
        uc_rows: List[str] = []
        covered_domains: Set[str] = set()

        for uc_path in uc_files:
            uc_text = uc_path.read_text(encoding="utf-8")
            uc_data, _ = extract_use_case_data(uc_text)
            rel_link = uc_path.relative_to(func_dir).as_posix()
            uc_id = uc_data["id"] or uc_path.stem
            title = uc_data["title"] or uc_path.stem
            domain = uc_data["domain"] or "core"
            covered_domains.add(domain.lower())
            status = uc_data["status"] or "Activo"
            has_ocl = "Sí" if any("ocl_contract" in r for r in uc_data["business_rules"]) else "No"
            uc_rows.append(
                f"| `{uc_id}` | `{domain}` | {title} | [{uc_path.name}](./{rel_link}) | {status} | {has_ocl} |"
            )

        synced_ucs = len(uc_rows)
        if uc_rows:
            uc_table = (
                "| ID | Dominio | Caso de Uso | Archivo | Estado | OCL |\n"
                "| :--- | :--- | :--- | :--- | :--- | :--- |\n"
                + "\n".join(uc_rows)
            )
        else:
            uc_table = (
                "_Aún no hay casos de uso registrados. Se agregarán automáticamente al formalizar "
                "requerimientos `MAJOR` o `MINOR`._"
            )

        f_idx_text = func_index.read_text(encoding="utf-8")
        updated_f_idx = _replace_sync_section(
            f_idx_text,
            "FUNCTIONAL_CATALOG",
            r"##\s+(?:Catálogo de Casos de Uso|Dominios de Negocio y Casos de Uso)[^\n]*",
            uc_table,
        )

        # 3. Sincronizar Módulos Legados Detectados (Modo Progresivo / Strangler)
        all_detected_domains = _read_detected_domains(project_root)
        pending_domains = [d for d in all_detected_domains if d.lower() not in covered_domains]

        if pending_domains:
            pending_rows = [
                f"| `{dom}` | Detectado en código | Pendiente de formalización As-Is | Documentar `UC-{dom.upper()}-*` y test de caracterización al planificar cambios en este módulo. |"
                for dom in pending_domains
            ]
            pending_table = (
                "| Dominio Detectado | Origen | Estado | Directiva de Expansión (Just-In-Time) |\n"
                "| :--- | :--- | :--- | :--- |\n"
                + "\n".join(pending_rows)
            )
        else:
            pending_table = "_Sin dominios legados pendientes de levantamiento (cobertura funcional al día)._"

        if "SYNC:PENDING_DOMAINS:START" in updated_f_idx:
            updated_f_idx = _replace_sync_section(
                updated_f_idx,
                "PENDING_DOMAINS",
                r"##\s+Módulos Legados Detectados[^\n]*",
                pending_table,
            )

        func_index.write_text(updated_f_idx, encoding="utf-8")
        print(f"✔ Sincronizados {synced_ucs} casos de uso en docs/functional/index.md")
        if pending_domains:
            print(f"ℹ️  {len(pending_domains)} dominios legados pendientes de levantamiento registrados en docs/functional/index.md")

    print("✨ Sincronización finalizada.\n")
    return synced_reqs, synced_ucs
