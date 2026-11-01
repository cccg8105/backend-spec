---
name: backend-spec
description: "Gobierna el desarrollo backend asistido por IA (v1.0) con especificaciones vivas, contratos API/RNFs, heurística OCL, carril rápido PATCH y onboarding brownfield."
---

# backend-spec v1.0 Skill

Esta skill guía al agente como Arquitecto e Ingeniero Backend mediante el **Protocolo Gatekeeper de Dos Velocidades**, acoplado a los slash commands nativos (`/plan`, `/grill-me`, `/goal`, `/boost`) y validado por `backend-spec check`.

## Cuándo Activar esta Skill
- Ante cualquier nueva funcionalidad, cambio de API/base de datos, refactorización, corrección de bugs (`PATCH`) u onboarding de un repositorio existente (*Brownfield*).

---

## 1. Selección de Carril por Impacto

| Impacto | Cuándo Aplica | Flujo Operativo |
| :--- | :--- | :--- |
| **`MAJOR` / `MINOR`** | Nuevos endpoints/eventos, cambios de reglas de negocio o persistencia. | **Carril Completo:** /grill-me → Caso de Uso (YAML Frontmatter + Mermaid + OCL heurístico) → `docs/technical/` (`api-contracts.md`, `database-model.md`, `component-design.md`) → Test *Spec-First* → `pending.md` → `backend-spec sync` & `check` → Gatekeeper `/plan`. |
| **`PATCH` (Fast-Track)** | Bugfixes, condiciones de carrera o refactors internos sin alterar contratos ni BD. | **Micro-Spec:** Sin caso de uso ni Mermaid nuevos (`Referencia Funcional: N/A (PATCH / Fast-Track)`). Registra `REQ-* (PATCH)` en `pending.md` → `backend-spec sync` → Test de regresión → Confirmación breve → Fix. |

---

## 2. Reglas Clave de Calidad
1. **Plantillas del Agente:** Toma los moldes desde `.spec/templates/` (`_template_use_case.md`, `_template_api_contracts.md`, `_template_audit_proposals.md`, `_template_test_spec.md`, `ocl-guidelines.md`).
2. **Garantías Operativas Backend:** En `docs/technical/api-contracts.md`, explicita siempre idempotencia, nivel de aislamiento/concurrencia, autorización RBAC y presupuestos de latencia/timeouts.
3. **Rolling Window:** Mantén un máximo de **3 filas** en la tabla `## 📜 Historial de Revisiones` de cada documento modificado.
4. **Fronteras Estrictas:** Solo modifica archivos declarados en `Fronteras y Artefactos` del `REQ-*` activo (`backend-spec check --staged` bloquea commits fantasma).
5. **Auditoría Aislada:** Trata `docs/backlog/audit-proposals.md` como buzón de solo lectura; jamás implementes código fuente directamente desde allí salvo promoción explícita a `pending.md`.
6. **Onboarding Brownfield y Módulos Progresivos:**
   - En repositorios preexistentes, apóyate en la skill `backend-spec-bootstrap` (o `/spec-bootstrap`) y `.spec/bootstrap-report.md`.
   - Si una tarea toca un dominio que figura en `docs/functional/index.md` como `Detectado (Pendiente As-Is)`, documenta primero su caso de uso *As-Is* (y test de caracterización si la cobertura es nula) antes de planificar nuevas modificaciones.
7. **Cierre y Graphify:** Al pasar los tests al 100%, ejecuta `graphify update` en consola (o `/graphify . --update` si existe `graphify-out/`) y ofrece archivar con `backend-spec resolve <REQ-ID> [--bump]`.
