# Comando: 04_execute_requirement

> **Propósito:** Ejecutar la implementación de un requerimiento aprobado dentro de sus fronteras autorizadas y sincronizar catálogos y grafo de conocimiento.

## Instrucciones para el Agente:
1. Lee el bloque `REQ-*` activo en `docs/backlog/pending.md` y carga únicamente sus documentos referenciados.
2. **Descomposición e Implementación Acotada:**
   - Si el requerimiento involucra múltiples archivos o componentes, traza un mini-grafo de ejecución interna (estrategia de tickets atómicos): implementa primero contratos, tipos e interfaces desacopladas (*test seams*) antes de los componentes dependientes.
   - Modifica **únicamente** los archivos listados en `Fronteras y Artefactos` (de lo contrario `backend-spec check --staged` bloqueará el commit).
   - Respeta invariantes OCL (`pre` → guardias de dominio, `inv` → invariantes de entidad, `post` → aserciones de prueba) y garantías operativas de `docs/technical/api-contracts.md`.
3. **Verificación Integral y Auditoría de Código:**
   - Ejecuta la suite de pruebas del proyecto hasta que pase al 100% (incluyendo la prueba de regresión o spec-first).
   - Realiza una revisión del diff (`/code-review`) verificando que no se introduzcan code smells (*Primitive Obsession*, *Shotgun Surgery*, *Feature Envy*) ni fugas de abstracción.
   - Marca con `[x]` los criterios cumplidos en `docs/backlog/pending.md` y ejecuta `backend-spec sync` y `backend-spec check`.
4. **Sincronización Obligatoria del Grafo (Graphify):**
   - Si existe `graphify-out/`, ejecuta en terminal `graphify update` (o invoca la skill `/graphify . --update`) para actualizar `graphify-out/graph.json`.
5. **Cierre y Resolución:**
   - Notifica o ejecuta `backend-spec resolve <REQ-ID>` (añadiendo `--bump` solo al cerrar la versión del manifiesto).
