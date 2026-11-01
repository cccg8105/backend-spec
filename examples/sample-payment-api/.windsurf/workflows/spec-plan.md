# Windsurf Cascade Workflow: /spec-plan

1. Classify request impact (`MAJOR`, `MINOR`, or `PATCH`) per `docs/backlog/versioning-strategy.md`.
2. **If `PATCH` (Fast-Track bugfix/internal adjustment with NO contract or DB changes):**
   - Register compact `REQ-[DOMAIN]-[XXX]` in `docs/backlog/pending.md` with `Referencia Funcional: N/A (PATCH / Fast-Track)`.
   - Run `backend-spec sync` and `backend-spec check`, outline the regression test, and ask for quick confirmation.
3. **If `MAJOR` or `MINOR` (Full Track):**
   - If there are ambiguities, trigger `/spec-grill` (pausing for structured choice input).
   - If the task touches a module listed as `Detectado (Pendiente As-Is)` in `docs/functional/index.md`, document its As-Is use case first before planning new modifications.
   - Create/update `docs/functional/use-cases/UC-XXX.md` from `.spec/templates/_template_use_case.md` (YAML Frontmatter + Mermaid + OCL if applicable).
   - Update `docs/technical/` (`database-model.md`, `component-design.md`, `api-contracts.md`), register `REQ-*` in `pending.md`, run `backend-spec sync` and `backend-spec check`, and wait for user approval before coding.
