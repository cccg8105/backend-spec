# Comando: 02c_plan_deployment

> **Propósito:** Especificar el impacto del cambio en infraestructura, CI/CD, variables de entorno y estrategia de despliegue (Etapa 2C).

## Instrucciones para el Agente:
1. Abre `docs/technical/deployment-strategy.md`.
2. Revisa si el requerimiento implica:
   - Nuevas variables de entorno requeridas (documentar si son sensibles / secretos de Vault).
   - Ajustes en el pipeline de CI/CD (lint, typecheck, tests, escaneo SAST).
   - Modificación en endpoints de observabilidad o health checks (`/health/live`, `/health/ready`).
   - Requisitos especiales de rollout (canary, rolling update).
3. Si el pipeline se modifica, actualiza el diagrama de flujo en Mermaid (`flowchart LR`).
