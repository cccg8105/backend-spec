# Comando Claude Code: /spec-bootstrap

Realiza la ingeniería inversa inicial (*Brownfield Bootstrap*) sobre un proyecto backend existente:
1. Ejecuta `backend-spec bootstrap` para escanear manifiestos, controladores, modelos/migraciones y generar `.spec/bootstrap-report.md`.
2. Lee la checklist de progreso en `.spec/bootstrap-report.md` y úsala como GPS en disco para no perder el contexto.
3. Si existe o deseas crear el grafo de conocimiento, invoca `/graphify .` para identificar *God Nodes* y comunidades reales.
4. Con base en `.spec/bootstrap-report.md` (y aplicando la regla de que el código ejecutable manda sobre la documentación antigua), completa sin alucinar:
   - `docs/technical/database-model.md` (tablas e índices existentes).
   - `docs/technical/component-design.md` (capas y adaptadores reales, filtrando código muerto).
   - `docs/technical/api-contracts.md` (endpoints públicos, autenticación y garantías operativas actuales).
   - Los casos de uso iniciales en `docs/functional/use-cases/` (con `status: "As-Is (Brownfield)"`).
5. Registra discrepancias, código muerto o brechas de tests en `docs/backlog/audit-proposals.md` y marca tu avance en `.spec/bootstrap-report.md`.
6. Sincroniza y valida con `backend-spec sync` y `backend-spec check`.
