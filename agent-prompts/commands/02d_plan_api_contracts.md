# Comando: 02d_plan_api_contracts

> **Propósito:** Especificar los contratos síncronos/asíncronos de interfaz y garantías operativas backend (Etapa 2D).

## Instrucciones para el Agente:
1. Abre `docs/technical/api-contracts.md` (consulta `.spec/templates/_template_api_contracts.md` como referencia).
2. Documenta con precisión:
   - **Contratos HTTP/REST o gRPC:** Método, ruta/RPC, caso de uso vinculado, scope de autorización, idempotencia y códigos de estado RFC 7807.
   - **Eventos Asíncronos:** Evento, canal/tópico, dirección (`PUBLISH`/`CONSUME`) y política de reintentos/DLQ.
   - **Garantías Operativas (RNFs):** Estrategia de `Idempotency-Key`, nivel de aislamiento/concurrencia (`FOR UPDATE` u *optimistic locking*), control RBAC/anti-IDOR y presupuesto de latencia/timeouts.
3. Actualiza la tabla `## 📜 Historial de Revisiones` manteniendo máximo 3 filas.
