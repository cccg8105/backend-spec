# Windsurf Cascade Workflow: /spec-execute

1. Read the highest-priority active requirement in `docs/backlog/pending.md`.
2. Load ONLY its referenced functional and technical specs (`docs/functional/`, `docs/technical/`).
3. Create or update unit/regression tests in Red state first (`@spec`, `@req`, `@businessRule`).
4. Modify ONLY the files declared under `Fronteras y Artefactos` (`pre-commit` enforces boundaries via `backend-spec check --staged`).
5. Run automated tests until 100% green, mark acceptance criteria `[x]`, and run `backend-spec sync` + `backend-spec check`.
6. If `graphify-out/` exists, run `graphify update` (or `/graphify . --update`).
