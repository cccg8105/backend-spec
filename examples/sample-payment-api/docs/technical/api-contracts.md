---
artifact_type: api-contracts
openapi_or_proto_ref: N/A
---

# Contratos de Interfaz (API / Eventos) y Garantías Operativas — sample-payment-api

## 1. Contratos Síncronos (HTTP/REST / gRPC)

- **Especificación Formal Vinculada:** `N/A` (enlazar `openapi.yaml` o `.proto` si aplica).
- **Estándar de Errores:** RFC 7807 (`application/problem+json`) con `correlationId`.

| Método | Ruta / RPC | Caso de Uso | Auth / Scope | Idempotente | Códigos de Respuesta |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `GET` | `/health/live` | Diagnóstico | Público | Sí | `200` |
| `GET` | `/health/ready` | Diagnóstico | Público | Sí | `200`, `503` |

---

## 2. Contratos Asíncronos (Eventos y Mensajería)

| Evento | Canal / Tópico | Dirección | Productor / Consumidor | Política de DLQ y Reintentos |
| :--- | :--- | :--- | :--- | :--- |
| `_Sin eventos aún_` | `-` | `PUBLISH` | `-` | Por definir al incorporar mensajería |

---

## 3. Garantías Operativas y Atributos de Calidad (RNFs Backend)

- **Idempotencia:** Mutaciones críticas no idempotentes por naturaleza deben exigir `Idempotency-Key` con almacenamiento temporal y respuesta determinista ante reintentos.
- **Concurrencia y Aislamiento:** Nivel de aislamiento transaccional `READ COMMITTED` por defecto; operaciones sobre saldos/cupos deben declarar bloqueo optimista (`version`) o pesimista (`FOR UPDATE`).
- **Seguridad, Autorización (RBAC) y Rate Limiting:** Autenticación validada en frontera de transporte, control de acceso basado en roles/scopes y validación de pertenencia de recursos.
- **Resiliencia y SLAs:** Timeouts explícitos en toda llamada de red saliente, reintentos con *exponential backoff* únicamente sobre operaciones idempotentes y presupuesto de latencia documentado por endpoint crítico.

---

## 📜 Historial de Revisiones (Últimos Cambios)

| Versión | Fecha | Requerimiento | Resumen del Cambio |
| :--- | :--- | :--- | :--- |
| `v1.0.0` | 2026-10-31 | `INIT` | Inicialización de contratos de borde y garantías operativas backend. |

> *Nota: Esta tabla mantiene una ventana deslizante de los últimos 3 cambios. Para el historial completo, consultar [`docs/backlog/changelog.md`](../backlog/changelog.md).*
