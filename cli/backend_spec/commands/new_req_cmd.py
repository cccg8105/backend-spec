import re
from pathlib import Path
from typing import Dict, Optional, Tuple

from backend_spec.commands.sync_index_cmd import run_sync_index


def _slugify(text: str) -> str:
    slug = re.sub(r"[^a-zA-Z0-9]+", "-", text.strip().lower()).strip("-")
    return slug[:40] if slug else "feature"


def _read_config_settings(project_root: Path) -> Dict[str, str]:
    defaults = {
        "src_ext": ".ts",
        "src_dir": "src",
        "test_pattern": "tests/unit/{slug}.spec.ts",
        "current_milestone": "v0.2.0",
    }
    cfg = project_root / ".spec" / "config.yaml"
    if not cfg.exists():
        return defaults
    raw = cfg.read_text(encoding="utf-8")
    for k in tuple(defaults.keys()):
        m = re.search(rf'^{k}:\s*["\']?([^"\'\r\n]+)["\']?', raw, re.MULTILINE)
        if m:
            defaults[k] = m.group(1).strip()
    return defaults


def _find_audit_proposal(project_root: Path, audit_id: str) -> Optional[Dict[str, str]]:
    audit_file = project_root / "docs" / "backlog" / "audit-proposals.md"
    if not audit_file.exists():
        return None
    content = audit_file.read_text(encoding="utf-8")
    clean_id = audit_id.strip("[]")
    pattern = rf"###\s*\[{re.escape(clean_id)}\]\s*([^\n\r]+)(.*?)(?=###\s*\[|\Z)"
    match = re.search(pattern, content, re.DOTALL)
    if not match:
        return None

    title = match.group(1).strip()
    body = match.group(2)

    m_dom = re.search(r"-\s*\*\*Dominio:\*\*\s*`?([a-zA-Z0-9_-]+)`?", body)
    domain = m_dom.group(1).strip() if m_dom else "core"

    m_impact = re.search(r"-\s*\*\*Impacto Estimado:\*\*\s*`?(MAJOR|MINOR|PATCH)`?", body, re.IGNORECASE)
    impact = m_impact.group(1).strip().upper() if m_impact else "PATCH"

    m_sev = re.search(r"-\s*\*\*Severidad Sugerida:\*\*\s*`?(P1|P2|P3)`?", body, re.IGNORECASE)
    priority = m_sev.group(1).strip().upper() if m_sev else "P2"

    m_evid = re.search(r"-\s*\*\*Evidencia en Código:\*\*\s*`?([^`\n\r]+)`?", body)
    evidence = m_evid.group(1).strip() if m_evid else ""

    return {
        "id": clean_id,
        "title": title,
        "domain": domain,
        "impact": impact,
        "priority": priority,
        "evidence": evidence,
    }


def _mark_audit_proposal_promoted(project_root: Path, audit_id: str, req_id: str) -> bool:
    audit_file = project_root / "docs" / "backlog" / "audit-proposals.md"
    if not audit_file.exists():
        return False
    content = audit_file.read_text(encoding="utf-8")
    clean_id = audit_id.strip("[]")
    pattern = rf"(###\s*\[{re.escape(clean_id)}\][^\n\r]*\n.*?-\s*\*\*Estado:\*\*\s*)([^\n\r]+)"
    updated, count = re.subn(pattern, rf"\1Promovido a {req_id}", content, count=1, flags=re.DOTALL)
    if count > 0:
        audit_file.write_text(updated, encoding="utf-8")
        return True
    return False


def run_new_req(
    project_root: Path,
    title: Optional[str] = None,
    domain: str = "core",
    priority: str = "P2",
    impact: str = "MINOR",
    target_version: Optional[str] = None,
    uc_ref: Optional[str] = None,
    fast_track: bool = False,
    from_audit: Optional[str] = None,
) -> Optional[str]:
    project_root = Path(project_root).resolve()
    pending_file = project_root / "docs" / "backlog" / "pending.md"
    changelog_file = project_root / "docs" / "backlog" / "changelog.md"

    if not pending_file.exists():
        print("❌ Error: docs/backlog/pending.md no encontrado. Ejecuta 'backend-spec init' primero.")
        return None

    if from_audit:
        audit_info = _find_audit_proposal(project_root, from_audit)
        if not audit_info:
            print(f"❌ Error: No se encontró la propuesta de auditoría '{from_audit}' en docs/backlog/audit-proposals.md.")
            return None
        title = title or audit_info["title"]
        domain = audit_info["domain"]
        impact = audit_info["impact"]
        priority = priority if priority != "P2" else audit_info["priority"]
        print(f"ℹ️  Promoviendo propuesta de auditoría [{audit_info['id']}]: '{title}' (Impacto: {impact}, Prioridad: {priority})")
    elif not title:
        print("❌ Error: Debes proporcionar un título para el requerimiento o usar --from-audit <ID>.")
        return None

    pending_content = pending_file.read_text(encoding="utf-8")
    changelog_content = (
        changelog_file.read_text(encoding="utf-8") if changelog_file.exists() else ""
    )

    domain_upper = re.sub(r"[^A-Z0-9]", "", domain.upper()) or "CORE"
    combined_history = pending_content + "\n" + changelog_content
    existing_ids = re.findall(rf"REQ-{domain_upper}-(\d+)", combined_history)
    next_num = max(int(i) for i in existing_ids) + 1 if existing_ids else 1
    req_id = f"REQ-{domain_upper}-{next_num:03d}"

    cfg = _read_config_settings(project_root)
    if not target_version:
        v_match = re.search(r"##\s+Milestone\s+([^\s\n]+)", pending_content)
        target_version = v_match.group(1).strip() if v_match else cfg["current_milestone"]

    is_fast_track = fast_track or (impact.upper() == "PATCH")
    slug = _slugify(title)
    slug_snake = slug.replace("-", "_")
    slug_pascal = "".join(part.capitalize() for part in slug.split("-"))

    src_ext = cfg["src_ext"]
    src_dir = cfg["src_dir"]
    if src_ext == ".py":
        src_artifact = f"{src_dir}/application/{domain.lower()}_{slug_snake}{src_ext}"
    elif src_ext in (".java", ".kt", ".cs"):
        src_artifact = f"{src_dir}/{domain.lower()}/{slug_pascal}Service{src_ext}"
    elif src_ext in (".go", ".rs"):
        src_artifact = f"{src_dir}/{domain.lower()}/{slug_snake}{src_ext}"
    else:
        src_artifact = f"{src_dir}/application/use-cases/{slug}.use-case{src_ext}"

    test_artifact = (
        cfg["test_pattern"]
        .replace("{slug}", slug)
        .replace("{slug_snake}", slug_snake)
        .replace("{slug_pascal}", slug_pascal)
    )

    if from_audit and audit_info.get("evidence"):
        # Si la propuesta indicaba un archivo de evidencia real, preferirlo como artefacto a modificar
        clean_evid = audit_info["evidence"].split(":")[0].strip()
        if (project_root / clean_evid).exists():
            src_artifact = clean_evid

    if is_fast_track:
        resolved_uc_ref = uc_ref if uc_ref else "N/A (PATCH / Fast-Track)"
        req_type_label = "Hotfix / Fix (PATCH - Fast-Track)"
        action_src = "MODIFY" if (project_root / src_artifact).exists() else "NEW"
        req_block = f"""
### [{req_id}] {title}
- **Prioridad:** {priority}
- **Tipo:** {req_type_label}
- **Versión Objetivo:** `{target_version}`
- **Referencia Funcional:** `{resolved_uc_ref}`
- **Referencia Técnica:** `docs/technical/component-design.md`

#### Fronteras y Artefactos:
- **Artefactos a Modificar / Crear:**
  - `{src_artifact}` [{action_src}]
  - `{test_artifact}` [NEW]
- **Restricciones:**
  - Carril Fast-Track (`PATCH`): prohibido alterar contratos públicos de API o esquemas de base de datos.

#### Criterios de Aceptación:
- [ ] Reproducir el defecto mediante test automatizado de regresión antes del fix.
- [ ] Aplicar corrección verificando que la suite de pruebas pase al 100%.
"""
    else:
        resolved_uc_ref = (
            uc_ref
            if uc_ref
            else f"docs/functional/use-cases/UC-{domain_upper}-{next_num:03d}-{slug}.md"
        )
        action_src = "MODIFY" if (project_root / src_artifact).exists() else "NEW"
        req_block = f"""
### [{req_id}] {title}
- **Prioridad:** {priority}
- **Tipo:** Feature ({impact.upper()})
- **Versión Objetivo:** `{target_version}`
- **Referencia Funcional:** `{resolved_uc_ref}`
- **Referencia Técnica:** `docs/technical/component-design.md`, `docs/technical/api-contracts.md`

#### Fronteras y Artefactos:
- **Artefactos a Modificar / Crear:**
  - `{src_artifact}` [{action_src}]
  - `{test_artifact}` [NEW]
- **Restricciones:**
  - Respetar los contratos de arquitectura e idempotencia definidos en `docs/technical/`.

#### Criterios de Aceptación:
- [ ] Implementar la lógica del caso de uso conforme a sus reglas de negocio.
- [ ] Pruebas unitarias (*Spec-First*) pasando al 100%.
"""

    updated_content = pending_content.rstrip() + "\n" + req_block
    pending_file.write_text(updated_content, encoding="utf-8")

    if from_audit:
        _mark_audit_proposal_promoted(project_root, from_audit, req_id)
        print(f"✔ Estado de propuesta en docs/backlog/audit-proposals.md actualizado a 'Promovido a {req_id}'")

    run_sync_index(project_root)

    print(f"✔ Requerimiento creado exitosamente: {req_id}")
    print(f"📄 Archivo actualizado: docs/backlog/pending.md")
    if is_fast_track:
        print("⚡ Modo Fast-Track (PATCH) activado: ceremonia ligera sin exigir nuevo caso de uso.\n")
    else:
        print(f"👉 Asegúrate de crear/actualizar '{resolved_uc_ref}' antes de ejecutar 'backend-spec check'.\n")
    return req_id
