# Windsurf Cascade Workflow: /spec-bootstrap

1. Run `backend-spec bootstrap` to inspect project manifests, controllers, database models, and produce `.spec/bootstrap-report.md`.
2. Follow the progress checklist inside `.spec/bootstrap-report.md` as an external disk-based GPS to stay focused without context loss.
3. Review `.spec/bootstrap-report.md` (and `graphify-out/graph.json` if available) to populate `docs/technical/` (`database-model.md`, `component-design.md`, `api-contracts.md`) using actual code over outdated documentation and filtering dead code.
4. Agree with the user on mode (`full` vs `progressive`), document the initial use cases in `docs/functional/use-cases/` with `status: "As-Is (Brownfield)"`, and record discrepancies or test gaps in `docs/backlog/audit-proposals.md`.
5. Run `backend-spec sync` and `backend-spec check` to ensure complete consistency.
