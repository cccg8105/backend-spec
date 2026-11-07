# Instrucciones Canónicas para Agentes de IA (`backend-spec` v1.0)

Este proyecto implementa la metodología **`backend-spec` v1.0**. El usuario **no necesita recordar ni ejecutar comandos de terminal manualmente**; el agente actúa como Arquitecto e Ingeniero Backend gobernando el ciclo de desarrollo mediante el **Protocolo Conversacional Gatekeeper de Dos Velocidades**.

---

## 🚦 PROTOCOLO GATEKEEPER DE DOS VELOCIDADES (Ceremonia Adaptativa)

### 🛑 REGLA DE ORO: PROHIBIDO CODIFICAR SIN TRAZABILIDAD EN EL BACKLOG
**Nunca modifiques código fuente (`src/`, `app/`, `internal/`) sin que exista un requerimiento registrado en `docs/backlog/pending.md` y aprobado por el usuario.** El hook Git `pre-commit` (`backend-spec check --staged`) bloqueará cualquier *commit fantasma*.

Ante cualquier solicitud del usuario, clasifica primero su impacto consultando `docs/backlog/versioning-strategy.md`:

| Tipo de Cambio | Impacto | Carril Activado | Ceremonia Requerida |
| :--- | :--- | :--- | :--- |
| Nuevos endpoints, reglas de negocio, tablas o *breaking changes* | `MAJOR` / `MINOR` | **Carril Completo** | Entrevista (`/grill-me`) → Caso de Uso con YAML Frontmatter + Mermaid + Heurística OCL → `docs/technical/` (`api-contracts.md`, `database-model.md`, `component-design.md`) → Test *Spec-First* → `pending.md` → Gatekeeper `/plan`. |
| Corrección de bug, condición de carrera, optimización o refactor interno sin alterar contratos ni BD | `PATCH` | **Carril Fast-Track (Micro-Spec)** | **Omite** crear casos de uso o diagramas Mermaid nuevos (`Referencia Funcional: N/A (PATCH / Fast-Track)`). Registra bloque compacto en `pending.md`, escribe test de regresión que reproduce el fallo, pide confirmación rápida y aplica el fix. |

---

## 🏗️ FLUJO DEL CARRIL COMPLETO (`MAJOR` / `MINOR`)

### Paso 1: Diagnóstico de Impacto y Entrevista (`/grill-me`)
1. Consulta `docs/functional/index.md` y `docs/technical/index.md` (carga únicamente los documentos afectados).
2. Si existen ambigüedades, formula preguntas concretas sobre validaciones de entrada, reglas invariantes (`[BR-*]`), garantías operativas (idempotencia, concurrencia, RBAC) e impacto en persistencia.

### Paso 2: Especificación Viva, YAML Frontmatter & OCL
1. **Funcional:** Crea o actualiza el caso de uso en `docs/functional/use-cases/UC-[DOMINIO]-[NUM]-[slug].md` basándote en `.spec/templates/_template_use_case.md` (incluyendo *YAML Frontmatter*, diagrama Mermaid, tablas Inputs/Outputs y reglas `[BR-XX]`).
2. **Evaluación Autónoma OCL:** Aplica la Matriz Heurística OCL (ver abajo) apoyándote en `.spec/templates/ocl-guidelines.md`.
3. **Técnica y Contratos Operativos:** Actualiza según corresponda:
   - `docs/technical/database-model.md` (tablas, índices, migraciones y `erDiagram`).
   - `docs/technical/component-design.md` (capas, puertos e invariantes `inv`).
   - `docs/technical/api-contracts.md` (endpoints HTTP/gRPC, eventos asíncronos, idempotencia, concurrencia/aislamiento, RBAC y SLAs).
4. **Historial Rolling Window:** Actualiza `## 📜 Historial de Revisiones` manteniendo **máximo 3 filas** por documento.

### Paso 3: Registro en Backlog y Sincronización
1. Registra `[REQ-DOMINIO-XXX]` en `docs/backlog/pending.md` (o ejecuta `backend-spec req:new`) declarando `Prioridad`, `Tipo`, `Versión Objetivo`, referencias reales y `Fronteras y Artefactos` (`[NEW]`, `[MODIFY]`, `[DELETE]`).
2. Ejecuta `backend-spec sync` y `backend-spec check` para asegurar que catálogos y esquemas JSON estén en verde.

### Paso 4: Puerta de Enlace (`/plan`)
Presenta el plan de implementación acotado a las fronteras del `REQ-*` y **detén la ejecución hasta recibir aprobación explícita del usuario**.

---

## ⚡ FLUJO DEL CARRIL FAST-TRACK (`PATCH` / Hotfix)
1. Confirma que el cambio **no modifica contratos públicos de E/S ni esquemas de base de datos**.
2. Registra el bloque `REQ-[DOMINIO]-[XXX]` con `Tipo: Hotfix / Fix (PATCH - Fast-Track)` y `Referencia Funcional: N/A (PATCH / Fast-Track)` en `docs/backlog/pending.md` (puedes apoyarte en `backend-spec req:new "Título" --domain X --impact PATCH`).
3. Solicita confirmación breve del usuario indicando los archivos exactos a tocar.
4. Aplica el protocolo `/diagnose`: reproduce, aísla, formula hipótesis y escribe primero el test de regresión que falla capturando el bug (Red). Aplica la corrección mínima y verifica que la suite completa y `backend-spec check` pasen.

---

## 🧠 MATRIZ HEURÍSTICA DE DECISIÓN OCL (Detección Autónoma)

| Escenario Detectado | Condición en la Solicitud | Acción del Agente con OCL |
| :--- | :--- | :--- |
| **Lógica Cuantitativa / Financiera** | Dinero, saldos, límites, cupos, comisiones o inventario. | **OBLIGATORIO:** Cláusulas `pre` y `post` (usando `@pre`). |
| **Máquinas de Estado de Negocio** | Transiciones restringidas (`PENDING -> APPROVED`, estados `FROZEN`). | **OBLIGATORIO:** Cláusulas `inv` y `pre` con `implies`. |
| **Relaciones Multi-campo / Temporales** | Restricciones cruzadas (`start_date < end_date`, `max >= current`). | **OBLIGATORIO:** Invariantes de entidad `inv`. |
| **CRUDs Simples o Ajustes Técnicos** | Lecturas/listados simples, cambios de perfil sin invariantes, CI/CD, logs. | **OMITIR OCL:** Solo prosa concisa (`ocl_applied: false`). |

---

## 🧭 ONBOARDING DE PROYECTOS EXISTENTES (`Brownfield Bootstrap`)
Si el repositorio ya contiene código fuente previo pero `docs/` acaba de inicializarse (o existen fases incompletas):
1. **Memoria en Disco:** Revisa `.spec/bootstrap-report.md`. Usa su checklist de progreso (`- [ ]` / `- [x]`) como GPS en disco para avanzar por bloques sin perder el hilo del contexto.
2. **Prioridad del Código:** El código ejecutable manda sobre documentación desfasada. Consulta `/graphify .` para mapear dependencias reales y omitir código muerto.
3. **Poblar Técnico As-Is:** Completa `docs/technical/` (`database-model.md`, `component-design.md`, `api-contracts.md`).
4. **Modo Full vs. Progresivo:** Levanta los casos de uso seleccionados en `docs/functional/use-cases/` con `status: "As-Is (Brownfield)"`. Los dominios no levantados quedarán catalogados en `docs/functional/index.md` como `Detectado (Pendiente As-Is)`.
5. **Aislamiento de Auditoría:** Registra discrepancias documentales, código muerto o brechas de pruebas exclusivamente en `docs/backlog/audit-proposals.md` (no en `pending.md`).

---

## ⚡ REGLA DE EXPANSIÓN PROGRESIVA (Just-In-Time)
Si una solicitud de cambio toca un dominio que figura en `docs/functional/index.md` como `Detectado (Pendiente As-Is)`:
- Documenta primero su caso de uso *As-Is* en `docs/functional/use-cases/` (y un test de caracterización si la cobertura base es nula).
- Sincroniza con `backend-spec sync` para graduar el dominio al catálogo activo.
- Procede entonces a planificar el requerimiento To-Be con su ceremonia habitual.

---

## 🕸️ CICLO OBLIGATORIO DE GRAPHIFY
1. **Antes de Modificar:** Si existe `graphify-out/graph.json`, consulta dependencias con `graphify query "..."` o `graphify path "Origen" "Destino"`.
2. **Después de Implementar y Pasar Tests:** Actualiza incrementalmente el grafo ejecutando en terminal:
   ```bash
   graphify update
   ```
   *(O invocando la skill del agente `/graphify . --update`)*. Respeta siempre `.graphifyignore`.
