import datetime
import json
import re
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

from backend_spec.commands.sync_index_cmd import _replace_sync_section, run_sync_index
from backend_spec.detector.ecosystem_detector import detect_ecosystem
from backend_spec.detector.version_extractor import extract_version
from backend_spec.validator.schema_validator import locate_framework_asset

FRAMEWORK_HINTS = {
    "fastapi": ("Framework Backend", "FastAPI"),
    "django": ("Framework Backend", "Django"),
    "flask": ("Framework Backend", "Flask"),
    "express": ("Framework Backend", "Express.js"),
    "fastify": ("Framework Backend", "Fastify"),
    "@nestjs/core": ("Framework Backend", "NestJS"),
    "spring-boot": ("Framework Backend", "Spring Boot"),
    "gin-gonic/gin": ("Framework Backend", "Gin (Go)"),
    "labstack/echo": ("Framework Backend", "Echo (Go)"),
    "gofiber/fiber": ("Framework Backend", "Fiber (Go)"),
    "actix-web": ("Framework Backend", "Actix Web"),
    "axum": ("Framework Backend", "Axum"),
}

ORM_HINTS = {
    "prisma": "Prisma ORM",
    "@prisma/client": "Prisma Client",
    "typeorm": "TypeORM",
    "drizzle-orm": "Drizzle ORM",
    "sqlalchemy": "SQLAlchemy",
    "sqlmodel": "SQLModel",
    "tortoise-orm": "Tortoise ORM",
    "alembic": "Alembic Migrations",
    "hibernate": "Hibernate / JPA",
    "flyway": "Flyway Migrations",
    "gorm.io/gorm": "GORM",
    "sqlx": "SQLx",
    "diesel": "Diesel ORM",
    "sea-orm": "SeaORM",
}

TEST_HINTS = {
    "vitest": "Vitest",
    "jest": "Jest",
    "pytest": "Pytest",
    "junit": "JUnit",
    "testify": "Testify",
}

SKIP_DIRS = {
    ".git",
    ".spec",
    "docs",
    "node_modules",
    ".venv",
    "venv",
    "__pycache__",
    "dist",
    "build",
    "target",
    "graphify-out",
    ".gemini",
    ".cursor",
    ".claude",
    ".windsurf",
}


def _scan_manifest_tech(project_root: Path, manifest_name: str) -> Dict[str, str]:
    found = {
        "framework": "No detectado automáticamente",
        "orm": "No detectado automáticamente",
        "testing": "Suite estándar del ecosistema",
    }
    manifest_path = project_root / manifest_name
    if not manifest_path.exists():
        return found

    raw = manifest_path.read_text(encoding="utf-8", errors="ignore").lower()
    for token, (_, label) in FRAMEWORK_HINTS.items():
        if token in raw:
            found["framework"] = label
            break

    orms = [label for token, label in ORM_HINTS.items() if token in raw]
    if orms:
        found["orm"] = ", ".join(dict.fromkeys(orms))

    tests = [label for token, label in TEST_HINTS.items() if token in raw]
    if tests:
        found["testing"] = ", ".join(dict.fromkeys(tests))

    return found


def _scan_repository_inventory(project_root: Path) -> Dict[str, List[str]]:
    controllers: List[str] = []
    models_and_migrations: List[str] = []
    api_specs: List[str] = []
    test_files: List[str] = []
    candidate_domains: Set[str] = set()

    for path in project_root.rglob("*"):
        if any(part in SKIP_DIRS for part in path.parts):
            continue
        if not path.is_file():
            continue

        rel = path.relative_to(project_root).as_posix()
        low_name = path.name.lower()
        low_rel = rel.lower()

        if low_name in ("openapi.yaml", "openapi.yml", "openapi.json", "swagger.yaml", "swagger.json", "asyncapi.yaml") or path.suffix == ".proto":
            api_specs.append(rel)

        if any(k in low_rel for k in ("controller", "router", "routes", "handler", "endpoint", "views")):
            controllers.append(rel)

        if any(k in low_rel for k in ("model", "entity", "entities", "schema.prisma", "migration", ".sql")):
            models_and_migrations.append(rel)

        if any(k in low_rel for k in ("test", "spec")) and path.suffix in (".py", ".ts", ".js", ".go", ".java", ".rs", ".cs"):
            test_files.append(rel)

        # Inferir dominios candidatos desde carpetas bajo src/, app/ o internal/
        parts = Path(rel).parts
        if len(parts) >= 3 and parts[0] in ("src", "app", "internal", "modules", "services"):
            generic = {
                "domain", "application", "infrastructure", "presentation", "controllers",
                "entities", "models", "repositories", "use-cases", "use_cases", "common",
                "shared", "utils", "config", "middlewares", "core", "api", "routes",
            }
            for seg in parts[1:-1]:
                clean_seg = re.sub(r"[^a-z0-9_-]", "", seg.lower())
                if clean_seg and clean_seg not in generic and len(clean_seg) >= 3:
                    candidate_domains.add(clean_seg)

    return {
        "controllers": sorted(controllers)[:30],
        "models": sorted(models_and_migrations)[:30],
        "api_specs": sorted(api_specs),
        "test_files": sorted(test_files),
        "domains": sorted(candidate_domains)[:12] or ["core"],
    }


def _scan_legacy_docs_and_tests(project_root: Path) -> Dict[str, object]:
    legacy_docs: List[Dict[str, str]] = []
    latest_src_mtime = 0.0

    for path in project_root.rglob("*"):
        if any(part in SKIP_DIRS for part in path.parts):
            continue
        if not path.is_file():
            continue
        rel = path.relative_to(project_root).as_posix()
        low_name = path.name.lower()

        if path.suffix in (".py", ".ts", ".js", ".go", ".rs", ".java", ".cs", ".kt"):
            try:
                mtime = path.stat().st_mtime
                if mtime > latest_src_mtime:
                    latest_src_mtime = mtime
            except Exception:
                pass

        # Detectar documentación previa fuera de backend-spec docs/
        if (
            low_name in ("readme.md", "architecture.md", "design.md", "adr.md")
            or "docs/" in rel.lower()
            or "postman" in low_name
            or "insomnia" in low_name
        ):
            if not rel.startswith("docs/"):
                try:
                    doc_mtime = path.stat().st_mtime
                    drift = "Posible desfase (anterior a cambios de código)" if latest_src_mtime > 0 and (latest_src_mtime - doc_mtime) > 86400 * 7 else "Reciente / Coincidente"
                except Exception:
                    drift = "No determinado"
                legacy_docs.append({"path": rel, "drift": drift})

    return {
        "docs": legacy_docs[:15],
        "has_docs": len(legacy_docs) > 0,
    }


def _read_graphify_summary(project_root: Path) -> List[str]:
    graph_json = project_root / "graphify-out" / "graph.json"
    if not graph_json.exists():
        return []
    try:
        payload = json.loads(graph_json.read_text(encoding="utf-8"))
        nodes = payload.get("nodes", [])
        links = payload.get("links") or payload.get("edges") or []
        degree: Dict[str, int] = {}
        labels: Dict[str, str] = {}
        for n in nodes:
            nid = str(n.get("id", ""))
            labels[nid] = str(n.get("label") or n.get("name") or nid)
            degree[nid] = 0
        for edge in links:
            src = str(edge.get("source", ""))
            tgt = str(edge.get("target", ""))
            degree[src] = degree.get(src, 0) + 1
            degree[tgt] = degree.get(tgt, 0) + 1
        top = sorted(degree.items(), key=lambda kv: kv[1], reverse=True)[:8]
        return [f"`{labels.get(nid, nid)}` ({deg} conexiones)" for nid, deg in top if deg > 0]
    except Exception:
        return []


def _extract_previous_checkbox_state(report_path: Path) -> Tuple[Dict[str, bool], str]:
    state: Dict[str, bool] = {}
    mode = "progressive"
    if not report_path.exists():
        return state, mode

    try:
        text = report_path.read_text(encoding="utf-8")
        m_mode = re.search(r"onboarding_mode:\s*([a-zA-Z0-9_-]+)", text)
        if m_mode:
            mode = m_mode.group(1).strip()

        for line in text.splitlines():
            m_cb = re.search(r"-\s*\[([ xX])\]\s*(.+)", line)
            if m_cb:
                is_checked = m_cb.group(1).lower() == "x"
                label = m_cb.group(2).strip()
                state[label] = is_checked
    except Exception:
        pass
    return state, mode


def run_bootstrap(
    project_root: Path,
    mode: str = "auto",
    reset: bool = False,
) -> Path:
    """
    Escanea un repositorio existente (Brownfield), actualiza docs/technical/tech-stack.md
    y .spec/config.yaml, inicializa docs/backlog/audit-proposals.md y genera .spec/bootstrap-report.md
    con checklist de progreso (GPS) para guiar la ingeniería inversa sin pérdida de contexto.
    """
    project_root = Path(project_root).resolve()
    spec_dir = project_root / ".spec"
    docs_dir = project_root / "docs"

    if not docs_dir.exists() or not spec_dir.exists():
        raise RuntimeError(
            "El proyecto aún no tiene estructura backend-spec. Ejecuta 'backend-spec init' primero."
        )

    print(f"\n🧭 Ejecutando Brownfield Bootstrap en: {project_root}")

    detection = detect_ecosystem(project_root)
    sig = detection.get("detected") or {
        "name": "Personalizado",
        "manifest": "N/A",
        "version_file": "N/A",
        "format": "plain",
    }
    version_path = detection.get("version_path")
    detected_ver = (
        extract_version(version_path, sig["format"]) if version_path else None
    ) or "0.1.0"

    tech_info = _scan_manifest_tech(project_root, sig["manifest"])
    inventory = _scan_repository_inventory(project_root)
    legacy_doc_info = _scan_legacy_docs_and_tests(project_root)
    god_nodes = _read_graphify_summary(project_root)
    today = datetime.date.today().isoformat()

    # Evaluar línea base de pruebas
    test_count = len(inventory["test_files"])
    ctrl_count = len(inventory["controllers"])
    if test_count == 0:
        test_baseline = "none"
        test_desc = "Crítica: 0 pruebas automatizadas detectadas (requiere tests de caracterización prioritarios)"
    elif test_count < ctrl_count:
        test_baseline = "partial"
        test_desc = f"Parcial: {test_count} archivos de test para {ctrl_count} controladores"
    else:
        test_baseline = "solid"
        test_desc = f"Sólida: {test_count} archivos de pruebas detectados"

    scenario = "CODE_AND_DOCS" if legacy_doc_info["has_docs"] else "CODE_ONLY"
    selected_mode = "progressive" if mode in ("auto", "progressive") else "full"

    report_path = spec_dir / "bootstrap-report.md"
    prev_state, prev_mode = _extract_previous_checkbox_state(report_path) if not reset else ({}, selected_mode)
    if not reset and prev_mode:
        selected_mode = prev_mode

    # 1. Asegurar docs/backlog/audit-proposals.md
    audit_file = docs_dir / "backlog" / "audit-proposals.md"
    if not audit_file.exists():
        templates_root = locate_framework_asset("templates")
        src_audit = templates_root / ".spec" / "docs" / "backlog" / "audit-proposals.md" if templates_root else None
        if src_audit and src_audit.exists():
            content = src_audit.read_text(encoding="utf-8")
            content = content.replace("{{PROJECT_NAME}}", project_root.name)
            content = content.replace("{{TODAY}}", today)
            content = content.replace("{{CURRENT_VERSION}}", detected_ver.lstrip("vV"))
            audit_file.write_text(content, encoding="utf-8")
        else:
            audit_file.write_text(
                f"# Registro de Auditoría y Propuestas de Mejora — {project_root.name}\n\n"
                "<!-- SYNC:AUDIT_PROPOSALS:START -->\n_Sin propuestas registradas aún._\n<!-- SYNC:AUDIT_PROPOSALS:END -->\n",
                encoding="utf-8",
            )
        print("✔ Inicializado buzón de deuda y hallazgos: docs/backlog/audit-proposals.md")

    # 2. Actualizar tabla en docs/technical/tech-stack.md
    tech_stack_file = docs_dir / "technical" / "tech-stack.md"
    if tech_stack_file.exists():
        stack_table = (
            "| Componente | Tecnología Seleccionada | Versión / Manifiesto | Justificación |\n"
            "| :--- | :--- | :--- | :--- |\n"
            f"| **Lenguaje / Runtime** | {sig['name']} | `{sig['manifest']}` (`v{detected_ver}`) | Detectado por `spec bootstrap`. |\n"
            f"| **Framework Backend** | {tech_info['framework']} | Manifiesto | Detectado en dependencias del proyecto. |\n"
            f"| **Persistencia / ORM** | {tech_info['orm']} | Manifiesto | Detectado en dependencias y esquemas. |\n"
            f"| **Testing** | {tech_info['testing']} | Manifiesto | {test_desc}. |"
        )
        ts_content = tech_stack_file.read_text(encoding="utf-8")
        updated_ts = _replace_sync_section(
            ts_content, "TECH_STACK", r"##\s+1\.\s+Núcleo Tecnológico[^\n]*", stack_table
        )
        tech_stack_file.write_text(updated_ts, encoding="utf-8")
        print("✔ Actualizado automáticamente: docs/technical/tech-stack.md")

    # 3. Actualizar dominios sugeridos en .spec/config.yaml
    config_file = spec_dir / "config.yaml"
    if config_file.exists() and inventory["domains"]:
        cfg_text = config_file.read_text(encoding="utf-8")
        domains_yaml = "domains:\n" + "\n".join(f"  - {d}" for d in inventory["domains"])
        updated_cfg = re.sub(
            r"domains:\s*(?:\r?\n\s*-\s*[^\r\n]+)+",
            domains_yaml,
            cfg_text,
            count=1,
        )
        config_file.write_text(updated_cfg, encoding="utf-8")
        print(f"✔ Dominios detectados registrados en .spec/config.yaml: {', '.join(inventory['domains'])}")

    # 4. Enlazar openapi/proto en docs/technical/api-contracts.md si se encontró
    api_contracts_file = docs_dir / "technical" / "api-contracts.md"
    if api_contracts_file.exists() and inventory["api_specs"]:
        primary_spec = inventory["api_specs"][0]
        ac_text = api_contracts_file.read_text(encoding="utf-8")
        ac_text = ac_text.replace("openapi_or_proto_ref: N/A", f"openapi_or_proto_ref: {primary_spec}")
        ac_text = ac_text.replace("**Especificación Formal Vinculada:** `N/A`", f"**Especificación Formal Vinculada:** `{primary_spec}`")
        api_contracts_file.write_text(ac_text, encoding="utf-8")
        print(f"✔ Vinculado contrato formal '{primary_spec}' en docs/technical/api-contracts.md")

    # 5. Generar reporte guía .spec/bootstrap-report.md con checklist GPS
    def _cb(label: str) -> str:
        checked = prev_state.get(label, False)
        box = "[x]" if checked else "[ ]"
        return f"- {box} {label}"

    ctrl_lines = "\n".join(f"- `{c}`" for c in inventory["controllers"]) or "- _Ninguno detectado_"
    model_lines = "\n".join(f"- `{m}`" for m in inventory["models"]) or "- _Ninguno detectado_"
    spec_lines = "\n".join(f"- `{s}`" for s in inventory["api_specs"]) or "- _Ninguno detectado_"
    graph_lines = (
        "\n".join(f"- {g}" for g in god_nodes)
        or "- _Grafo no generado aún (ejecuta `/graphify .` para enriquecer el análisis estructural)_"
    )

    doc_lines_list = [f"- `{d['path']}` — {d['drift']}" for d in legacy_doc_info["docs"]]
    legacy_doc_lines = "\n".join(doc_lines_list) if doc_lines_list else "- _No se detectó documentación previa ajena al framework (Escenario: Solo Código)_"

    domain_checks = "\n".join(_cb(f"Dominio `{d}`: Caso de uso As-Is documentado o evaluado") for d in inventory["domains"])

    report_md = f"""---
scenario: "{scenario}"
onboarding_mode: "{selected_mode}"
test_baseline: "{test_baseline}"
last_bootstrap: "{today}"
---

# Reporte de Descubrimiento Brownfield — {project_root.name}
*Generado el {today} por `backend-spec bootstrap` (Escenario: `{scenario}` | Modo: `{selected_mode}`)*

> **Instrucción para el Agente (`/spec-bootstrap`):**
> Este archivo es tu **memoria externa en disco**. Trabaja un bloque a la vez y marca con `[x]` cada casilla al completarla. Si la sesión se compacta, continúa desde la primera casilla pendiente `[ ]`.

## 0. Checklist de Progreso (GPS para el Agente)

### Fase 1: Diagnóstico y Grafo Estructural
{_cb("Inspeccionar dependencias del manifiesto y tech-stack.md")}
{_cb("Consultar o generar grafo de conocimiento con `/graphify .`")}

### Fase 2: Extracción Técnica As-Is (El código ejecutable manda)
{_cb("Poblar `docs/technical/database-model.md` desde modelos y migraciones")}
{_cb("Poblar `docs/technical/component-design.md` y filtrar código muerto")}
{_cb("Poblar `docs/technical/api-contracts.md` con endpoints y garantías operativas")}

### Fase 3: Casos de Uso Funcionales As-Is (`docs/functional/use-cases/`)
{domain_checks}

### Fase 4: Auditoría y Cierre
{_cb("Registrar discrepancias documentales y deuda en `docs/backlog/audit-proposals.md`")}
{_cb("Ejecutar `backend-spec sync` y verificar con `backend-spec check`")}

---

## 1. Resumen Tecnológico Detectado
- **Ecosistema:** {sig['name']}
- **Versión Actual:** `v{detected_ver}` (`{sig['manifest']}`)
- **Framework HTTP/RPC:** {tech_info['framework']}
- **ORM / Migraciones:** {tech_info['orm']}
- **Línea Base de Pruebas:** {test_desc}
- **Dominios Sugeridos:** {", ".join(f"`{d}`" for d in inventory["domains"])}

## 2. Documentación Previa y Análisis de Desfase (*Doc Drift*)
{legacy_doc_lines}

## 3. Controladores, Rutas y Handlers Encontrados ({len(inventory['controllers'])})
{ctrl_lines}

## 4. Modelos de Datos, Entidades y Migraciones ({len(inventory['models'])})
{model_lines}

## 5. Contratos OpenAPI / AsyncAPI / Protobuf ({len(inventory['api_specs'])})
{spec_lines}

## 6. Nodos Centrales en Graphify (`graphify-out/graph.json`)
{graph_lines}
"""
    report_path.write_text(report_md, encoding="utf-8")
    print(f"✔ Reporte de inventario y checklist GPS en: .spec/bootstrap-report.md")

    # 6. Sincronizar índices para reflejar dominios pendientes en docs/functional/index.md
    run_sync_index(project_root)

    print("✨ Bootstrap completado. Ejecuta '/spec-bootstrap' en tu agente para sintetizar la arquitectura real.\n")
    return report_path
