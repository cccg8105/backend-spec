# Comando: 04_execute_requirement

> **Propósito:** Ejecutar la implementación de un requerimiento aprobado dentro de sus fronteras autorizadas y sincronizar catálogos y grafo de conocimiento.

## Instrucciones para el Agente:
1. Lee el bloque `REQ-*` activo en `docs/backlog/pending.md` y carga únicamente sus documentos referenciados.
2. **Implementación Acotada:**
   - Modifica **únicamente** los archivos listados en `Fronteras y Artefactos` (de lo contrario `backend-spec check --staged` bloqueará el commit).
   - Respeta invariantes OCL (`pre` → guardias de dominio, `inv` → invariantes de entidad, `post` → aserciones de prueba) y garantías operativas de `docs/technical/api-contracts.md`.
3. **Verificación Integral:**
   - Ejecuta la suite de pruebas del proyecto hasta que pase al 100%.
   - Marca con `[x]` los criterios cumplidos en `docs/backlog/pending.md` y ejecuta `backend-spec sync` y `backend-spec check`.
4. **Sincronización Obligatoria del Grafo (Graphify):**
   - Si existe `graphify-out/`, ejecuta en terminal `graphify update` (o invoca la skill `/graphify . --update`) para actualizar `graphify-out/graph.json`.
5. **Cierre y Resolución:**
   - Notifica o ejecuta `backend-spec resolve <REQ-ID>` (añadiendo `--bump` solo al cerrar la versión del manifiesto).
