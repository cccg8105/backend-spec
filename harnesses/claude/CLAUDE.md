<!-- BACKEND-SPEC:START -->
# Instrucciones del Proyecto: backend-spec v1.0 (Claude Code)

Este repositorio opera bajo **`backend-spec` v1.0** con validación estricta en `pre-commit` (`backend-spec check --staged`).

## Slash Commands Integrados
- **`/plan`**: Gatekeeper obligatorio antes de implementar cambios `MAJOR` o `MINOR`.
- **`/diff`**: Audita que los archivos modificados coincidan exactamente con las fronteras del `REQ-*`.
- **`/compact`**: Compacta contexto preservando el `REQ-*` activo y enlaces a `docs/`.
- **Comandos en `.claude/commands/`**:
  - `/spec-plan`: Flujo guiado de dos velocidades (`MAJOR`/`MINOR` completo vs `PATCH` Fast-Track).
  - `/spec-grill`: Entrevista técnica interactiva (con `AskUserQuestion`) para destrabar reglas de negocio y contratos.
  - `/spec-bootstrap`: Onboarding de repositorios existentes (*Brownfield*) con checklist persistente en `.spec/bootstrap-report.md`.
  - `/spec-resolve`: Cierre y archivado seguro con `backend-spec resolve <REQ-ID> [--bump]`.

## Protocolo Gatekeeper de Dos Velocidades
1. **Prohibido codificar sin backlog:** Ningún archivo de código fuente puede modificarse sin estar listado en las fronteras de un `REQ-*` activo en `docs/backlog/pending.md`.
2. **Carril Completo (`MAJOR` / `MINOR`):**
   - Aclara ambigüedades (apoyándote en `/spec-grill`).
   - Si la tarea toca un módulo que figura como `Detectado (Pendiente As-Is)` en `docs/functional/index.md`, levanta primero su caso de uso *As-Is* antes de planificar los cambios nuevos.
   - Crea/actualiza el caso de uso en `docs/functional/use-cases/` (usando `.spec/templates/_template_use_case.md` con YAML Frontmatter, Mermaid y OCL heurístico).
   - Actualiza `docs/technical/` (`database-model.md`, `component-design.md`, `api-contracts.md`) respetando el límite de 3 filas en Historial de Revisiones.
   - Registra el `REQ-*` en `pending.md`, ejecuta `backend-spec sync` y `backend-spec check`, y espera aprobación en `/plan`.
3. **Carril Fast-Track (`PATCH` / Hotfix sin cambio de contratos ni BD):**
   - Omite casos de uso y diagramas nuevos (`Referencia Funcional: N/A (PATCH / Fast-Track)`).
   - Registra el `REQ-* (PATCH)` en `pending.md`, prepara el test de regresión, confirma brevemente e implementa el fix.
4. **Gobernanza Brownfield y Auditoría:**
   - Trata `docs/backlog/audit-proposals.md` como solo lectura; nunca implementes código directamente desde allí salvo promoción explícita a `pending.md`.
5. **Sincronización Graphify:** Tras pasar las pruebas, si existe `graphify-out/`, ejecuta `graphify update` (o `/graphify . --update`).
<!-- BACKEND-SPEC:END -->
