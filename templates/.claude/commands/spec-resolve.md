# Comando Claude Code: /spec-resolve

Resuelve y audita el requerimiento completado en `backend-spec` v1.0:
1. Verifica que todos los criterios de aceptación en `docs/backlog/pending.md` cuenten con pruebas automatizadas pasando al 100%.
2. Ejecuta `backend-spec check` para validar enlaces físicos, esquemas JSON y fronteras.
3. Ejecuta `backend-spec resolve <REQ-ID>` (añade `--bump` únicamente si deseas actualizar ya la versión en el manifiesto del proyecto).
4. Si existe `graphify-out/`, confirma que `graphify update` haya sincronizado el grafo de conocimiento.
