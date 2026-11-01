---
artifact_type: api-contracts
openapi_or_proto_ref: openapi.yaml
---

# Contratos de Interfaz (API / Eventos) y Garantías Operativas Backend

## 1. Contratos Síncronos (HTTP/REST / gRPC)

- **Especificación Formal Vinculada:** `openapi.yaml` / `proto/service.proto` (si existe en el repositorio).
- **Estándar de Errores:** RFC 7807 (`application/problem+json`) con `correlationId` obligatorio.
- **Paginación Estándar:** Cursor-based (`cursor`, `limit`, `nextCursor`) para colecciones de alto volumen.

| Método | Ruta / RPC | Caso de Uso | Auth / Scope | Idempotente | Códigos de Respuesta |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `POST` | `/api/v1/transactions` | `UC-BILL-001` | `Bearer (payments:write)` | Sí (`Idempotency-Key`) | `201`, `400`, `409`, `422`, `429` |
| `GET` | `/api/v1/transactions/{id}` | `UC-BILL-002` | `Bearer (payments:read)` | Sí (Nativo) | `200`, `401`, `403`, `404` |

---

## 2. Contratos Asíncronos (Eventos de Dominio y Mensajería)

| Evento | Canal / Tópico | Dirección | Productor / Consumidor | Política de DLQ y Reintentos |
| :--- | :--- | :--- | :--- | :--- |
| `billing.transaction.completed.v1` | ` billing-events` | `PUBLISH` | `BillingService` | Outbox transaccional + 5 reintentos exponenciales → `billing-events.dlq` |
| `fraud.charge.flagged.v1` | `fraud-alerts` | `CONSUME` | `RiskWorker` | Deduplicación por `eventId` + DLQ tras 3 fallos |

---

## 3. Garantías Operativas y Atributos de Calidad (RNFs Backend)

- **Idempotencia:** Toda mutación crítica (`POST`/`PATCH` no naturalmente idempotente) exige cabecera `Idempotency-Key` (UUID v4) persistida en Redis/PostgreSQL con TTL de 24 horas; peticiones duplicadas con distinto payload devuelven `409 Conflict`.
- **Concurrencia y Aislamiento:** Nivel de aislamiento `READ COMMITTED` por defecto; mutaciones de saldo o inventario emplean bloqueo pesimista (`SELECT ... FOR UPDATE`) o bloqueo optimista mediante columna `version` entera.
- **Seguridad, Autorización (RBAC) y Rate Limiting:** Tokens JWT de corta duración (15 min), validación de pertenencia de recursos (*object-level authorization* contra IDOR) y *Rate Limiting* de `60 req/min` por usuario en endpoints transaccionales.
- **Resiliencia y SLAs:** Presupuesto de latencia `p95 < 250ms` en lecturas y `p95 < 800ms` en escrituras con pasarela; *timeout* estricto de `3000ms` hacia proveedores externos con *Circuit Breaker* tras 5 fallos consecutivos.

---

## 📜 Historial de Revisiones (Últimos Cambios)

| Versión | Fecha | Requerimiento | Resumen del Cambio |
| :--- | :--- | :--- | :--- |
| `v0.1.0` | YYYY-MM-DD | `REQ-CORE-001` | Definición inicial de contratos HTTP/Eventos, idempotencia, concurrencia y SLAs. |

> *Nota: Esta tabla mantiene una ventana deslizante de los últimos 3 cambios. Para el historial completo, consultar [`docs/backlog/changelog.md`](../backlog/changelog.md).*
