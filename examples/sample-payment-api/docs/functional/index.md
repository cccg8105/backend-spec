# Índice de Documentación Funcional — sample-payment-api

> **Instrucción para el Agente de IA:**
> Este catálogo contiene la lista de procesos de negocio y casos de uso activos del proyecto.
> - Antes de planificar cambios funcionales o técnicos, consulta este índice para identificar el caso de uso exacto.
> - **No leas todos los casos de uso simultáneamente**; carga únicamente el archivo vinculado a la tarea en curso.
> - Para crear un nuevo caso de uso, utiliza como referencia la plantilla en [`.spec/templates/_template_use_case.md`](../../.spec/templates/_template_use_case.md) y la guía OCL en [`.spec/templates/ocl-guidelines.md`](../../.spec/templates/ocl-guidelines.md).

---

## Catálogo de Casos de Uso

<!-- SYNC:FUNCTIONAL_CATALOG:START -->
| ID | Dominio | Caso de Uso | Archivo | Estado | OCL |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `UC-BILL-001` | `billing` | Cobro Transaccional con Idempotencia | [UC-BILL-001-process-charge.md](./use-cases/UC-BILL-001-process-charge.md) | Activo | Sí |
<!-- SYNC:FUNCTIONAL_CATALOG:END -->


---

## Módulos Legados Detectados (Modo Progresivo — Pendientes de Levantamiento As-Is)

<!-- SYNC:PENDING_DOMAINS:START -->
| Dominio Detectado | Origen | Estado | Directiva de Expansión (Just-In-Time) |
| :--- | :--- | :--- | :--- |
| `core` | Detectado en código | Pendiente de formalización As-Is | Documentar `UC-CORE-*` y test de caracterización al planificar cambios en este módulo. |
<!-- SYNC:PENDING_DOMAINS:END -->

---

## Convenciones de Casos de Uso
1. Cada nuevo caso de uso debe colocarse dentro de `docs/functional/use-cases/` con formato `UC-[DOMINIO]-[NUMERO]-[slug].md` e incluir *YAML Frontmatter* válido (`id`, `title`, `domain`, `actor`, `status`).
2. Todo caso de uso debe contener un diagrama de proceso en Mermaid (`flowchart TD` o `sequenceDiagram`), tablas de Entrada/Salida y reglas `[BR-XX]`.
3. Ejecuta `backend-spec sync` (o deja que el agente actualice este bloque) para mantener este catálogo sincronizado.
