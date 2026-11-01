# Comando Cursor: /spec-grill

Inicia una entrevista técnica interactiva para resolver dudas de arquitectura backend antes de codificar:
1. Inspecciona el código existente antes de preguntar ("código primero, humano después").
2. Utiliza la herramienta `AskQuestion` para presentar entre 2 y 4 decisiones por tarjeta interactiva, anteponiendo la opción `(Recommended)` con una línea de justificación.
3. Aclara los requerimientos clave de `backend-spec`:
   - Reglas de negocio invariantes `[BR-*]` y contratos OCL para lógica financiera o máquinas de estado.
   - Idempotencia, aislamiento de concurrencia y roles RBAC para `api-contracts.md`.
   - Si es un proyecto brownfield: clasificar ambigüedades entre reglas As-Is válidas o deuda para `docs/backlog/audit-proposals.md`.
4. Al cerrar la entrevista, sintetiza los acuerdos y pasa a la fase de especificación en Plan Mode.
