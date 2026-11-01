# Windsurf Cascade Workflow: /spec-grill

1. Inspect existing code, schemas, and endpoints first to avoid asking questions already answered by the implementation.
2. Present 2 to 4 structured multiple-choice questions in chat formatted as:
   - Question description
   - Option A) (Recommended) ...
   - Option B) ...
   - Option C) ...
3. **Pause execution** and wait for the user's explicit response before proceeding to create or edit specification files.
4. Focus strictly on backend invariants:
   - Business rules `[BR-*]` and OCL contracts (`pre`/`post`/`inv`).
   - Idempotency, concurrency isolation, and RBAC rules.
   - For brownfield code: clarify whether undocumented behavior is an intentional As-Is rule or technical debt destined for `docs/backlog/audit-proposals.md`.
5. Summarize approved decisions and proceed with `/spec-plan`.
