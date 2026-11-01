<!-- BACKEND-SPEC:START -->
# Regla de Trabajo: backend-spec v1.0 (Google Antigravity)

Este proyecto opera bajo **`backend-spec` v1.0**. El agente gobierna el desarrollo integrando los Slash Commands nativos de Antigravity con un **Protocolo Gatekeeper de Dos Velocidades**.

---

## Integración con Slash Commands Nativos de Antigravity

| Slash Command | Momento de Activación | Acción Obligatoria |
| :--- | :--- | :--- |
| **`/grill-me`** | **Entrevista (`MAJOR`/`MINOR`)** | Formula preguntas estructuradas ante ambigüedades en reglas de negocio, contratos API o RNFs (idempotencia, concurrencia, RBAC). |
| **`/boost`** | **Impacto `MAJOR`** | Activa razonamiento profundo ante *breaking changes*, migraciones delicadas o concurrencia financiera. |
| **`/plan`** | **Gatekeeper (`MAJOR`/`MINOR`)** | Genera el artefacto de plan (`RequestFeedback: true`) heredando las fronteras del `REQ-*`. Espera aprobación antes de tocar código fuente. |
| **`/goal`** | **Ejecución de Milestones** | Ejecuta secuencialmente múltiples `REQ-*` verificando pruebas, `backend-spec check` y `spec resolve`. |
| **`/compact`** | **Gestión de Contexto** | Compacta sesiones largas preservando el `REQ-*` activo y los enlaces a `docs/`. |

---

## Protocolo de Dos Velocidades

### 1. Carril Completo (`MAJOR` / `MINOR` — Nuevas funcionalidades o cambios de contrato)
1. **No codificar directamente:** Revisa `docs/functional/index.md` y `docs/technical/index.md`.
2. **Aterrizaje (`/grill-me`):** Aclara reglas `[BR-*]`, excepciones y garantías operativas.
3. **Especificación Viva + YAML Frontmatter + OCL:**
   - Crea/actualiza el caso de uso en `docs/functional/use-cases/` usando `.spec/templates/_template_use_case.md` (con YAML Frontmatter y Mermaid).
   - Aplica bloques OCL (`pre`/`post`/`inv`) automáticamente en lógica financiera, cupos o máquinas de estado; omítelos en CRUDs simples.
   - Actualiza `docs/technical/` (`database-model.md`, `component-design.md`, `api-contracts.md`) y su tabla Rolling Window (máx. 3 filas).
   - Genera esqueleto BDD *Spec-First* (`@spec`, `@req`, `@businessRule`).
4. **Backlog + Validación:** Registra el `REQ-*` en `docs/backlog/pending.md`, ejecuta `backend-spec sync` y `backend-spec check`.
5. **Gatekeeper `/plan`:** Presenta el plan interactivo y espera confirmación antes de modificar código.

### 2. Carril Fast-Track (`PATCH` / Hotfix — Corrección de bugs sin alterar contratos ni BD)
1. Omite crear casos de uso o diagramas Mermaid nuevos (`Referencia Funcional: N/A (PATCH / Fast-Track)`).
2. Registra el bloque `REQ-* (PATCH)` compacto en `docs/backlog/pending.md` delimitando archivos afectados y ejecuta `backend-spec sync`.
3. Pide confirmación breve, crea el test de regresión en rojo, aplica la corrección y valida con tests + `backend-spec check`.

### 3. Sincronización Post-Implementación con Graphify
- Si existe `graphify-out/`, ejecuta `graphify update` en consola (o invoca `/graphify . --update`) tras pasar las pruebas.

### 4. Gobernanza Brownfield y Expansión Progresiva
- En repositorios existentes, consulta `.spec/bootstrap-report.md` para continuar la checklist de progreso de la skill `backend-spec-bootstrap`.
- Si un requerimiento toca un módulo listado como `Detectado (Pendiente As-Is)` en `docs/functional/index.md`, documenta primero su caso de uso *As-Is* antes de planificar los cambios nuevos.
- Trata `docs/backlog/audit-proposals.md` como solo lectura (no ejecutes sus propuestas salvo promoción explícita a `pending.md`).
<!-- BACKEND-SPEC:END -->
