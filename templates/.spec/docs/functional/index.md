# Índice de Documentación Funcional — {{PROJECT_NAME}}

> **Instrucción para el Agente de IA:**
> Este catálogo contiene la lista de procesos de negocio y casos de uso activos del proyecto.
> - Antes de planificar cambios funcionales o técnicos, consulta este índice para identificar el caso de uso exacto.
> - **No leas todos los casos de uso simultáneamente**; carga únicamente el archivo vinculado a la tarea en curso.
> - Para crear un nuevo caso de uso, utiliza como referencia la plantilla en [`.spec/templates/_template_use_case.md`](../../.spec/templates/_template_use_case.md) y la guía OCL en [`.spec/templates/ocl-guidelines.md`](../../.spec/templates/ocl-guidelines.md).

---

## Catálogo de Casos de Uso

<!-- SYNC:FUNCTIONAL_CATALOG:START -->
_Aún no hay casos de uso registrados. Se agregarán automáticamente al formalizar requerimientos `MAJOR` o `MINOR`._
<!-- SYNC:FUNCTIONAL_CATALOG:END -->

---

## Módulos Legados Detectados (Modo Progresivo — Pendientes de Levantamiento As-Is)

<!-- SYNC:PENDING_DOMAINS:START -->
_Sin dominios legados pendientes de levantamiento._
<!-- SYNC:PENDING_DOMAINS:END -->

---

## Convenciones de Casos de Uso
1. Cada nuevo caso de uso debe colocarse dentro de `docs/functional/use-cases/` con formato `UC-[DOMINIO]-[NUMERO]-[slug].md` e incluir *YAML Frontmatter* válido (`id`, `title`, `domain`, `actor`, `status`).
2. Todo caso de uso debe contener un diagrama de proceso en Mermaid (`flowchart TD` o `sequenceDiagram`), tablas de Entrada/Salida y reglas `[BR-XX]`.
3. Ejecuta `backend-spec sync` (o deja que el agente actualice este bloque) para mantener este catálogo sincronizado.
