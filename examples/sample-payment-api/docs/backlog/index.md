# Índice del Backlog y Ciclo de Versiones — sample-payment-api

> **Instrucción para el Agente de IA:**
> Este catálogo describe el estado operativo del proyecto y sus versiones.
> - Busca en [`pending.md`](./pending.md) la tarea de mayor prioridad (`P1`) del milestone en curso.
> - Para cambios `MAJOR` o `MINOR`, verifica siempre las referencias funcionales y técnicas antes de codificar.
> - Para fixes `PATCH` (*Fast-Track*), verifica el criterio de regresión en [`pending.md`](./pending.md).

---

## Estado Operativo del Proyecto

- **Versión Actual en Producción:** `v1.0.0`
- **Milestone Activo en Desarrollo:** `v1.1.0`
- **Esquema de Versionamiento Activo:** `SemVer 2.0.0` (ver [`versioning-strategy.md`](./versioning-strategy.md))

---

## Accesos Rápidos

| Documento | Descripción |
| :--- | :--- |
| [pending.md](./pending.md) | **Requerimientos Pendientes:** Lista priorizada de tareas delimitadas por archivos con criterios de aceptación. |
| [audit-proposals.md](./audit-proposals.md) | **Auditoría y Mejoras:** Buzón de deuda técnica, discrepancias (*doc drift*) y hallazgos Brownfield en espera de promoción. |
| [changelog.md](./changelog.md) | **Historial de Releases:** Auditoría cronológica e inmutable de requerimientos resueltos por versión. |
| [versioning-strategy.md](./versioning-strategy.md) | **Gobernanza:** Reglas de impacto (`MAJOR`, `MINOR`, `PATCH`), carril *Fast-Track* y sincronización de manifiesto. |

---

## Resumen del Milestone Activo (`v1.1.0`)

<!-- SYNC:BACKLOG_TABLE:START -->
| ID Requerimiento | Título | Impacto | Prioridad | Estado | Ref. Funcional | Ref. Técnica |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `REQ-BILL-001` | Procesar cobro con idempotencia | `MINOR` | `P1` | Pendiente | `docs/functional/use-cases/UC-BILL-001-process-charge.md` | `docs/technical/component-design.md`, `docs/technical/api-contracts.md` |
| `REQ-BILL-002` | Corregir redondeo de comision en centavos | `PATCH` | `P2` | Pendiente | `N/A (PATCH / Fast-Track)` | `docs/technical/component-design.md` |
<!-- SYNC:BACKLOG_TABLE:END -->
