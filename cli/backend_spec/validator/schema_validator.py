import json
import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


def locate_framework_asset(subdir: str) -> Optional[Path]:
    """
    Localiza un subdirectorio de recursos ('templates', 'harnesses', 'schemas')
    tanto en ejecución desde el árbol fuente como instalado vía wheel/uv/pipx.
    """
    # 1. Desde el repositorio raíz: cli/backend_spec/validator/schema_validator.py -> parents[3] / subdir
    repo_candidate = Path(__file__).resolve().parents[3] / subdir
    if repo_candidate.exists():
        return repo_candidate

    # 2. Desde paquete instalado (Hatchling force-include): backend_spec/<subdir>
    pkg_candidate = Path(__file__).resolve().parents[1] / subdir
    if pkg_candidate.exists():
        return pkg_candidate

    return None


def _parse_scalar(val: str) -> Any:
    val = val.strip()
    if not val:
        return ""
    if (val.startswith('"') and val.endswith('"')) or (val.startswith("'") and val.endswith("'")):
        return val[1:-1]
    if val.lower() == "true":
        return True
    if val.lower() == "false":
        return False
    if val.lower() in ("null", "none", "~"):
        return None
    if val.startswith("[") and val.endswith("]"):
        inner = val[1:-1].strip()
        if not inner:
            return []
        return [_parse_scalar(item) for item in inner.split(",")]
    if re.fullmatch(r"-?\d+", val):
        return int(val)
    return val


def parse_yaml_frontmatter(md_text: str) -> Tuple[Dict[str, Any], str, bool]:
    """
    Extrae un bloque YAML Frontmatter delimitado por '---' al inicio de un archivo Markdown.
    Retorna (diccionario_datos, cuerpo_sin_frontmatter, tiene_frontmatter).
    """
    match = re.match(r"\A---\s*\r?\n(.*?)\r?\n---\s*(?:\r?\n|$)", md_text, re.DOTALL)
    if not match:
        return {}, md_text, False

    raw_yaml = match.group(1)
    body = md_text[match.end():]
    data: Dict[str, Any] = {}
    current_list_key: Optional[str] = None

    for line in raw_yaml.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if stripped.startswith("- ") and current_list_key is not None:
            data.setdefault(current_list_key, []).append(_parse_scalar(stripped[2:]))
            continue

        kv_match = re.match(r"^([A-Za-z0-9_-]+)\s*:\s*(.*)$", stripped)
        if kv_match:
            key = kv_match.group(1)
            raw_val = kv_match.group(2).strip()
            if raw_val == "":
                data[key] = []
                current_list_key = key
            else:
                data[key] = _parse_scalar(raw_val)
                current_list_key = None

    return data, body, True


def validate_against_schema(data: Any, schema: Dict[str, Any], path: str = "$") -> List[str]:
    """
    Valida un objeto Python contra un subconjunto práctico de JSON Schema Draft-07
    (type, required, enum, pattern, minLength, properties, items) sin dependencias externas.
    """
    errors: List[str] = []

    expected_type = schema.get("type")
    if expected_type:
        allowed_types = expected_type if isinstance(expected_type, list) else [expected_type]
        type_ok = False
        for t in allowed_types:
            if t == "string" and isinstance(data, str):
                type_ok = True
            elif t == "boolean" and isinstance(data, bool):
                type_ok = True
            elif t == "integer" and isinstance(data, int) and not isinstance(data, bool):
                type_ok = True
            elif t == "number" and isinstance(data, (int, float)) and not isinstance(data, bool):
                type_ok = True
            elif t == "array" and isinstance(data, list):
                type_ok = True
            elif t == "object" and isinstance(data, dict):
                type_ok = True
            elif t == "null" and data is None:
                type_ok = True
        if not type_ok:
            errors.append(f"{path}: tipo inválido (se esperaba {expected_type}, se recibió {type(data).__name__})")
            return errors

    if "enum" in schema and data not in schema["enum"]:
        errors.append(f"{path}: valor '{data}' fuera de los permitidos {schema['enum']}")

    if isinstance(data, str):
        if "minLength" in schema and len(data.strip()) < schema["minLength"]:
            errors.append(f"{path}: longitud menor a minLength={schema['minLength']} ('{data}')")
        if "pattern" in schema and not re.match(schema["pattern"], data):
            errors.append(f"{path}: '{data}' no cumple el patrón '{schema['pattern']}'")

    if isinstance(data, dict):
        for req_key in schema.get("required", []):
            if req_key not in data or data[req_key] is None or data[req_key] == "":
                errors.append(f"{path}: falta campo obligatorio '{req_key}'")
        props = schema.get("properties", {})
        for k, v in data.items():
            if k in props and v is not None:
                errors.extend(validate_against_schema(v, props[k], f"{path}.{k}"))

    if isinstance(data, list) and "items" in schema:
        item_schema = schema["items"]
        for idx, item in enumerate(data):
            errors.extend(validate_against_schema(item, item_schema, f"{path}[{idx}]"))

    return errors


def load_json_schema(relative_schema_path: str) -> Optional[Dict[str, Any]]:
    schemas_root = locate_framework_asset("schemas")
    if not schemas_root:
        return None
    target = schemas_root / relative_schema_path
    if not target.exists():
        return None
    return json.loads(target.read_text(encoding="utf-8"))


def _extract_markdown_table_rows(section_text: str) -> List[List[str]]:
    rows: List[List[str]] = []
    for line in section_text.splitlines():
        stripped = line.strip()
        if not (stripped.startswith("|") and stripped.endswith("|")):
            continue
        cells = [c.strip() for c in stripped.strip("|").split("|")]
        if all(re.fullmatch(r":?-+:?", c) for c in cells if c):
            continue
        rows.append(cells)
    # Descartar fila cabecera si existe
    return rows[1:] if len(rows) > 1 else []


def extract_use_case_data(md_text: str) -> Tuple[Dict[str, Any], bool]:
    """
    Combina el YAML Frontmatter y las secciones Markdown de un caso de uso
    en una estructura lista para validarse contra schemas/use-case.schema.json.
    """
    fm, body, has_fm = parse_yaml_frontmatter(md_text)

    # Fallback para título/ID desde encabezado # UC-XXX: Título si faltan en frontmatter
    h1_match = re.search(r"^#\s+(UC-[A-Z0-9]+-[0-9]+)\s*:\s*(.+)$", body, re.MULTILINE)
    uc_id = fm.get("id") or (h1_match.group(1).strip() if h1_match else "")
    title = fm.get("title") or (h1_match.group(2).strip() if h1_match else "")

    dom_match = re.search(r"-\s*\*\*Dominio:\*\*\s*`?([^\n`]+)`?", body)
    actor_match = re.search(r"-\s*\*\*Actor Principal:\*\*\s*`?([^\n`]+)`?", body)
    trig_match = re.search(r"-\s*\*\*Disparador(?:\s*\(Trigger\))?:\*\*\s*`?([^\n`]+)`?", body)
    mermaid_match = re.search(r"```mermaid\s+(.*?)\s+```", body, re.DOTALL)

    inputs_sec = re.search(r"###\s*Inputs Requeridos:(.*?)(?=###|\n---|\Z)", body, re.DOTALL)
    inputs_list = []
    if inputs_sec:
        for r in _extract_markdown_table_rows(inputs_sec.group(1)):
            if len(r) >= 3:
                req_flag = r[2].strip().lower() in ("sí", "si", "yes", "true")
                inputs_list.append({
                    "name": r[0].strip("` "),
                    "type": r[1].strip("` "),
                    "required": req_flag,
                    "validation": r[3].strip() if len(r) >= 4 else "",
                })

    outputs_sec = re.search(r"###\s*Output Esperado:(.*?)(?=###|\n---|\Z)", body, re.DOTALL)
    outputs_list = []
    if outputs_sec:
        for r in _extract_markdown_table_rows(outputs_sec.group(1)):
            if len(r) >= 2:
                outputs_list.append({
                    "name": r[0].strip("` "),
                    "type": r[1].strip("` "),
                    "description": r[2].strip() if len(r) >= 3 else "",
                })

    br_matches = re.findall(
        r"-\s*\*\*\[(BR-[0-9]{2,})\]\s*([^:*]+):\*\*(.*?)(?=-\s*\*\*\[BR-|\n---|\Z)",
        body,
        re.DOTALL,
    )
    rules_list = []
    for br_id, br_name, br_body in br_matches:
        desc_match = re.search(r"-\s*\*\*Descripción:\*\*\s*(.+)", br_body)
        desc = desc_match.group(1).strip() if desc_match else br_name.strip()
        ocl_match = re.search(r"```ocl\s+(.*?)\s+```", br_body, re.DOTALL)
        rule_obj: Dict[str, Any] = {
            "id": br_id.strip(),
            "name": br_name.strip(),
            "description": desc,
        }
        if ocl_match:
            rule_obj["ocl_contract"] = ocl_match.group(1).strip()
        rules_list.append(rule_obj)

    data = {
        "id": str(uc_id),
        "title": str(title),
        "domain": str(fm.get("domain") or (dom_match.group(1).strip() if dom_match else "")),
        "actor": str(fm.get("actor") or (actor_match.group(1).strip() if actor_match else "")),
        "status": str(fm.get("status", "Activo")),
        "trigger": str(fm.get("trigger") or (trig_match.group(1).strip() if trig_match else "")),
        "process_diagram_mermaid": mermaid_match.group(1).strip() if mermaid_match else "",
        "inputs": inputs_list,
        "outputs": outputs_list,
        "business_rules": rules_list,
    }
    if "ocl_applied" in fm:
        data["ocl_applied"] = fm["ocl_applied"]

    return data, has_fm


def extract_requirement_data(full_req_block: str) -> Dict[str, Any]:
    """
    Convierte un bloque Markdown '### [REQ-...] Título' de pending.md en un diccionario
    listo para validarse contra schemas/requirement.schema.json.
    """
    header_match = re.search(r"###\s*\[(REQ-[^\]]+)\]\s*(.+)", full_req_block)
    req_id = header_match.group(1).strip() if header_match else ""
    title = header_match.group(2).strip() if header_match else ""

    prio_match = re.search(r"-\s*\*\*Prioridad:\*\*\s*(P[123])\b", full_req_block)
    priority = prio_match.group(1).strip() if prio_match else ""

    impact_match = re.search(r"-\s*\*\*Tipo:\*\*\s*[^\n]*?\b(MAJOR|MINOR|PATCH)\b", full_req_block)
    impact_type = impact_match.group(1).strip() if impact_match else ""

    ver_match = re.search(r"-\s*\*\*Versión Objetivo:\*\*\s*`?([^\n`]+)`?", full_req_block)
    target_version = ver_match.group(1).strip() if ver_match else ""

    func_ref_match = re.search(r"-\s*\*\*Referencia Funcional:\*\*\s*(.+)", full_req_block)
    raw_func_ref = func_ref_match.group(1).strip() if func_ref_match else ""
    func_ref = raw_func_ref.strip("` ")

    tech_ref_match = re.search(r"-\s*\*\*Referencia Técnica:\*\*\s*(.+)", full_req_block)
    tech_refs: List[str] = []
    if tech_ref_match:
        raw_tech = tech_ref_match.group(1)
        code_spans = re.findall(r"`([^`]+)`", raw_tech)
        if code_spans:
            tech_refs = [c.strip() for c in code_spans if c.strip()]
        else:
            tech_refs = [p.strip() for p in raw_tech.split(",") if p.strip()]

    artifacts: List[Dict[str, str]] = []
    for path_str, action_str in re.findall(
        r"-\s*`([^`]+)`\s*\[(NEW|MODIFY|DELETE)\]", full_req_block
    ):
        artifacts.append({"path": path_str.strip(), "action": action_str.strip()})

    restrictions: List[str] = []
    rest_sec = re.search(
        r"-\s*\*\*Restricciones:\*\*(.*?)(?=####|\Z)", full_req_block, re.DOTALL
    )
    if rest_sec:
        inline_and_sub = rest_sec.group(1)
        for line in inline_and_sub.splitlines():
            cleaned = line.strip()
            if cleaned.startswith("- "):
                restrictions.append(cleaned[2:].strip())
            elif cleaned:
                restrictions.append(cleaned)

    criteria: List[Dict[str, Any]] = []
    crit_sec = re.search(r"####\s*Criterios de Aceptación:(.*)", full_req_block, re.DOTALL)
    if crit_sec:
        for state_char, desc in re.findall(r"-\s*\[([ xX])\]\s*(.+)", crit_sec.group(1)):
            criteria.append({
                "description": desc.strip(),
                "completed": state_char.lower() == "x",
            })

    return {
        "id": req_id,
        "title": title,
        "priority": priority,
        "impact_type": impact_type,
        "target_version": target_version,
        "references": {
            "functional": func_ref,
            "technical": tech_refs,
        },
        "boundaries": {
            "artifacts": artifacts,
            "restrictions": restrictions,
        },
        "acceptance_criteria": criteria,
    }


def count_rolling_history_rows(md_text: str) -> int:
    """
    Cuenta las filas de datos en la tabla '## 📜 Historial de Revisiones'.
    """
    sec = re.search(r"##\s*📜\s*Historial de Revisiones.*?(?=\n##\s|\Z)", md_text, re.DOTALL)
    if not sec:
        return 0
    return len(_extract_markdown_table_rows(sec.group(0)))
