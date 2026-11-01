# Comando Cursor: /spec-bootstrap

Ejecuta el descubrimiento inicial (*Brownfield Bootstrap*) del proyecto actual:
1. Ejecuta `backend-spec bootstrap` para actualizar `docs/technical/tech-stack.md` y generar `.spec/bootstrap-report.md`.
2. Sigue la checklist de progreso en `.spec/bootstrap-report.md` como GPS en disco para no perder el foco entre sesiones.
3. Revisa `.spec/bootstrap-report.md` (y `graphify-out/graph.json` si existe) para documentar en `docs/technical/` las tablas reales, capas activas (filtrando código muerto) y contratos en `api-contracts.md`.
4. Elige modalidad (`full` vs `progressive`) con el usuario, documenta los casos de uso seleccionados en `docs/functional/use-cases/` con `status: "As-Is (Brownfield)"` y envía la deuda/desfases a `docs/backlog/audit-proposals.md`.
5. Ejecuta `backend-spec sync` + `backend-spec check` y marca la checklist completada.
