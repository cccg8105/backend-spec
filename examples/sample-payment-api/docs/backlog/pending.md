# Backlog de Requerimientos Pendientes — sample-payment-api

> **Instrucción para el Agente de IA:**
> Los requerimientos están organizados por milestones de versión y ordenados por prioridad (`P1` Alta, `P2` Media, `P3` Baja).
> 1. Modifica **únicamente** los archivos declarados en **Fronteras y Artefactos** (`[NEW]`, `[MODIFY]`, `[DELETE]`).
> 2. Respeta las restricciones indicadas y verifica todos los criterios de aceptación (`[x]`) con pruebas automatizadas.
> 3. Para bugs o ajustes internos sin cambio de contrato (`PATCH`), utiliza el formato compacto *Fast-Track* con `Referencia Funcional: N/A (PATCH / Fast-Track)`.

---

## Milestone v1.1.0

### [REQ-BILL-001] Procesar cobro con idempotencia
- **Prioridad:** P1
- **Tipo:** Feature (MINOR)
- **Versión Objetivo:** `v1.1.0`
- **Referencia Funcional:** `docs/functional/use-cases/UC-BILL-001-process-charge.md`
- **Referencia Técnica:** `docs/technical/component-design.md`, `docs/technical/api-contracts.md`

#### Fronteras y Artefactos:
- **Artefactos a Modificar / Crear:**
  - `src/application/use-cases/procesar-cobro-con-idempotencia.use-case.ts` [NEW]
  - `tests/unit/procesar-cobro-con-idempotencia.spec.ts` [NEW]
- **Restricciones:**
  - Respetar los contratos de arquitectura e idempotencia definidos en `docs/technical/`.

#### Criterios de Aceptación:
- [ ] Implementar la lógica del caso de uso conforme a sus reglas de negocio.
- [ ] Pruebas unitarias (*Spec-First*) pasando al 100%.

### [REQ-BILL-002] Corregir redondeo de comision en centavos
- **Prioridad:** P2
- **Tipo:** Hotfix / Fix (PATCH - Fast-Track)
- **Versión Objetivo:** `v1.1.0`
- **Referencia Funcional:** `N/A (PATCH / Fast-Track)`
- **Referencia Técnica:** `docs/technical/component-design.md`

#### Fronteras y Artefactos:
- **Artefactos a Modificar / Crear:**
  - `src/application/use-cases/corregir-redondeo-de-comision-en-centavo.use-case.ts` [NEW]
  - `tests/unit/corregir-redondeo-de-comision-en-centavo.spec.ts` [NEW]
- **Restricciones:**
  - Carril Fast-Track (`PATCH`): prohibido alterar contratos públicos de API o esquemas de base de datos.

#### Criterios de Aceptación:
- [ ] Reproducir el defecto mediante test automatizado de regresión antes del fix.
- [ ] Aplicar corrección verificando que la suite de pruebas pase al 100%.
