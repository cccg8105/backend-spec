# Comando Claude Code: /spec-plan

Inicia la formulación de un requerimiento en `backend-spec` evaluando primero el carril:
1. Clasifica el cambio según `docs/backlog/versioning-strategy.md` (`MAJOR`, `MINOR` o `PATCH`).
2. **Si es `PATCH` (Fast-Track, sin cambios de contrato ni BD):**
   - Registra un bloque compacto `REQ-[DOMINIO]-[XXX]` con impacto `PATCH` y `Referencia Funcional: N/A (PATCH / Fast-Track)` en `docs/backlog/pending.md`.
   - Ejecuta `backend-spec sync` y `backend-spec check`, propón el test de regresión y pide confirmación rápida.
3. **Si es `MAJOR` o `MINOR` (Carril Completo):**
   - Si existen ambigüedades, formula preguntas mediante `/spec-grill` (usando `AskUserQuestion`).
   - Si la tarea toca un módulo que figura como `Detectado (Pendiente As-Is)` en `docs/functional/index.md`, levanta primero su caso de uso *As-Is* (y test de caracterización si no hay tests) antes de planificar los cambios nuevos.
   - Crea/actualiza el caso de uso en `docs/functional/use-cases/` desde `.spec/templates/_template_use_case.md` (con YAML Frontmatter, Mermaid y OCL si aplica).
   - Actualiza `docs/technical/` (`database-model.md`, `component-design.md`, `api-contracts.md`) y registra el `REQ-*` en `pending.md`.
   - Ejecuta `backend-spec sync` y `backend-spec check`, y entra en modo `/plan` antes de codificar.
