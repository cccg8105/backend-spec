# backend-spec v1.1

> **Framework y CLI de Especificación Viva para Ingeniería Backend asistida por Agentes de IA (Spec-Driven Backend)**

`backend-spec` estructura la colaboración entre desarrolladores e Inteligencia Artificial en proyectos backend, sustituyendo el *"vibe coding"* por un flujo auditable de **Dos Velocidades**: máximo rigor arquitectónico en funcionalidades nuevas (`MAJOR`/`MINOR`) y fricción mínima en correcciones rápidas (`PATCH` *Fast-Track*), con onboarding asistido para proyectos existentes (*Brownfield*) y soporte multi-harness nativo.

---

## 🏛️ Arquitectura del Proyecto Inicializado (`v1.1`)

`backend-spec` separa limpiamente los **moldes del agente** (`.spec/templates/`) del **estado vivo del proyecto** (`docs/`):

```text
.spec/
├── config.yaml                 # Ecosistema detectado, extensiones, versión y milestone
├── bootstrap-report.md         # Checklist GPS e inventario automático para proyectos existentes (Brownfield)
└── templates/                  # Blueprints de consulta para el Agente y el CLI
    ├── _template_use_case.md
    ├── _template_api_contracts.md
    ├── _template_audit_proposals.md
    ├── _template_database.md
    ├── _template_components.md
    ├── _template_tech_stack.md
    ├── _template_deployment.md
    ├── _template_test_spec.md
    └── ocl-guidelines.md

docs/
├── functional/                 # [1] Dominio y Reglas de Negocio Puras
│   ├── index.md                # Catálogo activo + Módulos Legados Detectados (Modo Progresivo)
│   └── use-cases/              # Casos de uso con YAML Frontmatter + Mermaid + OCL
│
├── technical/                  # [2] Arquitectura Modular y Garantías Operativas
│   ├── index.md                # Catálogo de navegación O(1) en tokens
│   ├── database-model.md       # Modelo ER en Mermaid, diccionario e índices
│   ├── component-design.md     # Capas Clean/Hexagonal, secuencia e invariantes inv OCL
│   ├── api-contracts.md        # HTTP/gRPC, eventos AsyncAPI, idempotencia, concurrencia y RBAC
│   ├── tech-stack.md           # Runtime, dependencias reales, RFC 7807 y logging JSON
│   └── deployment-strategy.md  # Pipeline CI/CD, contenedorización, probes y rollout
│
└── backlog/                    # [3] Contratos de Ejecución y Versionamiento
    ├── index.md                # Resumen vivo del milestone en desarrollo y accesos rápidos
    ├── versioning-strategy.md  # Gobernanza SemVer / CalVer / Sequential + Fast-Track
    ├── pending.md              # Requerimientos activos con fronteras estrictas de archivos
    ├── audit-proposals.md      # Hallazgos Brownfield, código muerto y deuda técnica (aislado / solo lectura)
    └── changelog.md            # Historial inmutable de requerimientos resueltos por release
```

---

## ⚡ Capacidades Clave en v1.1

* **Protocolo Gatekeeper de Dos Velocidades:**
  * **Carril Completo (`MAJOR` / `MINOR`):** Entrevista (`/grill-me` en Antigravity o `/spec-grill` en Cursor/Claude/Windsurf) → Caso de Uso con YAML Frontmatter + Mermaid + OCL heurístico → `api-contracts.md` / `database-model.md` → Test *Spec-First* → Gatekeeper `/plan`.
  * **Carril Fast-Track (`PATCH` / Hotfix):** Para correcciones sin cambios de contrato ni base de datos, omite crear casos de uso y diagramas nuevos; registra un Micro-Spec compacto en `pending.md`, exige test de regresión y aplica el fix sin burocracia.
* **Onboarding Brownfield Asistido con Memoria GPS en Disco:**
  * `backend-spec bootstrap` escanea controladores, modelos ORM/SQL, documentación antigua (detectando posibles desfases *doc drift*) y línea base de tests (`0%`, parcial, sólida).
  * Genera `.spec/bootstrap-report.md` con checklist interactiva (`- [ ]` / `- [x]`) para que el agente avance por bloques sin perder contexto entre sesiones o compactaciones (`/compact`).
  * Soporta modalidad **Completa** (`--mode full`) o **Progresiva** (`--mode progressive`), registrando dominios pendientes en `docs/functional/index.md` con la directiva *Just-In-Time*.
  * Aísla deuda técnica y código muerto en `docs/backlog/audit-proposals.md`, permitiendo promoverlos cuando se desee vía `backend-spec req:new --from-audit AUDIT-...`.
* **Paridad Multi-Harness de Entrevista (`spec-grill`):**
  * Resuelve la falta de un comando `/grill-me` nativo en otros entornos instalando la skill y comando `/spec-grill` adaptado a la UI nativa de **Claude Code** (`AskUserQuestion`), **Cursor** (`AskQuestion`) y **Windsurf** (pausa estructurada `A/B/C`), conservando `/grill-me` nativo en **Google Antigravity**.
* **Contratos Operativos Backend (`api-contracts.md`):** Modela explícitamente `Idempotency-Key`, nivel de aislamiento/concurrencia (`FOR UPDATE` vs. *optimistic locking*), autorización RBAC/anti-IDOR y presupuestos de latencia/timeouts.
* **Validación Real con JSON Schemas y Pre-commit Anti-Fantasmas:** `backend-spec check --staged` valida enlaces físicos, esquemas de `schemas/`, fronteras `[MODIFY]`/`[DELETE]` y bloquea *commits fantasma* en código fuente sin trazabilidad en `docs/backlog/` (con escape `git commit --no-verify` para emergencias).

---

## 🚀 Inicio Rápido

El CLI está escrito íntegramente en **Python estándar (cero dependencias externas)** y empaquetado desde la raíz con Hatchling.

### 1. Ejecución directa con los wrappers locales o Python:
```powershell
# Inicializar un proyecto nuevo o existente:
.\spec.ps1 init --dir /ruta/proyecto --harness all --versioning semver

# Inventariar arquitectura de un proyecto existente (Brownfield):
.\spec.ps1 bootstrap --dir /ruta/proyecto

# Crear requerimientos (Carril Completo o Fast-Track PATCH):
.\spec.ps1 req:new "Procesar cobro con idempotencia" --domain bill --priority P1 --impact MINOR
.\spec.ps1 req:new "Corregir redondeo en comisión" --domain bill --priority P1 --impact PATCH

# Sincronizar índices, validar esquemas/fronteras y archivar releases:
.\spec.ps1 sync --dir /ruta/proyecto
.\spec.ps1 check --staged --dir /ruta/proyecto
.\spec.ps1 resolve REQ-BILL-001 --bump --dir /ruta/proyecto

# Actualizar el framework en un proyecto existente (sin tocar docs/):
.\spec.ps1 update --dir /ruta/proyecto
.\spec.ps1 update --dry-run --dir /ruta/proyecto
```

### 2. Instalación o ejecución portable con `uv` / `pipx`:
```bash
# Ejecutar al vuelo desde la raíz del repositorio:
uvx --from . backend-spec init --dir /ruta/proyecto

# Instalar globalmente en el sistema:
uv tool install .
backend-spec check --staged
```

---

## 🔄 Actualización del Framework en Proyectos Existentes (`spec update`)

Cuando este repositorio se actualiza con mejoras en reglas de agentes, nuevos esquemas, blueprints o hooks:

1. **Actualiza el CLI en tu sistema:**
   ```bash
   uv tool install . --reinstall
   # O si está instalado desde un repositorio Git:
   uv tool upgrade backend-spec
   ```

2. **Refresca de forma segura el proyecto consumidor:**
   ```bash
   backend-spec update
   # O previsualizar cambios sin escribir en disco:
   backend-spec update --dry-run
   ```

`backend-spec update` garantiza:
* **Protección de `docs/`:** Jamás toca ni sobrescribe tus casos de uso, arquitectura ni backlog.
* **Bloques gestionados:** En `CLAUDE.md`, `.windsurfrules`, etc., actualiza únicamente la sección entre `<!-- BACKEND-SPEC:START -->` y `<!-- BACKEND-SPEC:END -->`, preservando cualquier directiva propia fuera del bloque.
* **Fusión aditiva:** Añade nuevos patrones de exclusión a `.graphifyignore` sin duplicar ni borrar los tuyos.
* **Migración no destructiva:** Si el proyecto venía de una versión anterior (`v0.x`), limpia plantillas viejas que residían en `docs/` y añade los nuevos pilares técnicos (`api-contracts.md`) de forma automática.

---

## 📂 Estructura del Repositorio

* `pyproject.toml`: Configuración de empaquetado raíz (Hatchling con `force-include` de plantillas, harnesses y esquemas).
* `cli/`: Implementación en Python estándar del CLI (`init`, `bootstrap`, `req:new`, `sync`, `check`, `resolve`), detectores de ecosistema y validador de JSON Schema / YAML Frontmatter.
* `schemas/`: Esquemas formales Draft-07 para casos de uso, requerimientos y documentos técnicos.
* `templates/`: Blueprints de `.spec/templates/`, plantillas base limpias de `docs/`, hook `pre-commit` y comandos por harness.
* `harnesses/` y `agent-prompts/`: Instrucciones canónicas y adaptadores específicos para Antigravity, Cursor, Claude Code y Windsurf.
* `examples/sample-payment-api/`: Proyecto de referencia completo validado con `backend-spec check`.
