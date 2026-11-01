# Comando Cursor: /spec-plan

Inicia el ciclo de especificación formal de `backend-spec`:
1. Clasifica el impacto en `MAJOR`, `MINOR` o `PATCH` según `docs/backlog/versioning-strategy.md`.
2. **Carril Fast-Track (`PATCH` sin cambios de contrato ni BD):**
   - Registra un bloque compacto en `docs/backlog/pending.md` con `Referencia Funcional: N/A (PATCH / Fast-Track)`.
   - Ejecuta `backend-spec sync` y `backend-spec check`, prepara el test de regresión y pide confirmación breve.
3. **Carril Completo (`MAJOR` / `MINOR`):**
   - Si hay ambigüedades, formula preguntas mediante `/spec-grill` (usando `AskQuestion`).
   - Si la tarea toca un módulo que figura como `Detectado (Pendiente As-Is)` en `docs/functional/index.md`, levanta primero su caso de uso *As-Is* (y test de caracterización si no hay tests) antes de planificar los cambios nuevos.
   - Crea/actualiza el caso de uso en `docs/functional/use-cases/` usando `.spec/templates/_template_use_case.md` (YAML Frontmatter + Mermaid + OCL heurístico).
   - Actualiza `docs/technical/` (`database-model.md`, `component-design.md`, `api-contracts.md`), registra el `REQ-*` en `pending.md`, ejecuta `backend-spec sync` y `backend-spec check`, y presenta el plan en Plan Mode.
