# Comando Claude Code: /spec-grill

Inicia una entrevista técnica estructurada para destrabar ambigüedades funcionales, contratos API o garantías operativas:
1. Inspecciona primero el código fuente y artefactos existentes ("código primero, humano después").
2. Utiliza la herramienta `AskUserQuestion` para presentar entre 2 y 4 decisiones independientes por ronda con sus opciones ordenadas, colocando primero `(Recommended)` y resumiendo brevemente los trade-offs.
3. Resuelve los puntos críticos de arquitectura backend:
   - Reglas invariantes `[BR-*]` y contratos OCL (`pre`/`post`/`inv`).
   - Idempotencia (`Idempotency-Key`), concurrencia/aislamiento transaccional y RBAC.
   - En proyectos existentes: aclarar si comportamientos anómalos son reglas de negocio intencionales (*As-Is*) o deuda técnica para `audit-proposals.md`.
4. Al concluir, resume los acuerdos alcanzados y continúa hacia la especificación viva.
