# Comando: 03_create_requirement

> **Propósito:** Sintetizar las especificaciones en un requerimiento atómico del backlog (`docs/backlog/pending.md`) con fronteras estrictas de archivos, validado contra `schemas/requirement.schema.json`.

## Instrucciones para el Agente:
1. Consulta `docs/backlog/versioning-strategy.md` para clasificar el impacto y el carril:
   - `MAJOR` / `MINOR` → **Carril Completo** (exige caso de uso funcional y referencias técnicas existentes).
   - `PATCH` → **Carril Fast-Track** (permite `Referencia Funcional: N/A (PATCH / Fast-Track)` si no cambia comportamiento contratado).
2. Asigna un ID único `REQ-[DOMINIO]-[NUMERO]` verificando tanto `pending.md` como `changelog.md` (o ejecuta `backend-spec req:new`).
3. Declara obligatoriamente:
   - **Prioridad:** `P1`, `P2` o `P3`.
   - **Tipo:** `Feature (MAJOR|MINOR)` o `Hotfix / Fix (PATCH - Fast-Track)`.
   - **Versión Objetivo:** Milestone activo (ej. `v1.1.0`).
   - **Referencias:** Rutas reales en `docs/` (incluyendo `docs/technical/api-contracts.md` si toca transporte o RNFs).
   - **Fronteras y Artefactos:** Archivos exactos (`[NEW]`, `[MODIFY]`, `[DELETE]`) coherentes con la extensión del proyecto configurada en `.spec/config.yaml`.
   - **Criterios de Aceptación:** Casillas `- [ ]` verificables mediante tests automatizados.
4. **Scaffolding BDD / Regresión:**
   - En `MAJOR`/`MINOR`: genera el esqueleto *Spec-First* basándote en `.spec/templates/_template_test_spec.md` con anotaciones `@spec`, `@req` y `@businessRule`.
   - En `PATCH`: prepara el test de regresión que reproduce el defecto.
5. Ejecuta `backend-spec sync` y `backend-spec check` para validar integridad de enlaces y esquemas.
6. **Gatekeeper:** Presenta el plan (`/plan` en modo completo o resumen rápido en `PATCH`) y espera aprobación del usuario antes de tocar código fuente.
