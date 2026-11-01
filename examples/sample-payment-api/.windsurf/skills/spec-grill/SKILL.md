---
name: spec-grill
description: "Entrevista estructurada de árbol de decisiones arquitectónicas y funcionales para ingeniería backend, eliminando ambigüedades antes de escribir especificaciones o código."
---

# spec-grill Skill

Esta skill activa el modo de entrevista técnica interactiva para destrabar reglas de negocio, decisiones de persistencia y garantías operativas de backend.

## Cuándo Activar esta Skill
- Al planificar requerimientos `MAJOR` o `MINOR` cuando existan ambigüedades en inputs, reglas `[BR-*]`, excepciones o garantías no funcionales.
- Al ejecutar el comando slash `/spec-grill`.
- Durante el onboarding *Brownfield* (`/spec-bootstrap`) para clarificar si un comportamiento del código legado es una regla de negocio intencional o un defecto.

---

## 🛑 REGLAS DE ORO DEL ENTREVISTADOR

1. **"Código primero, humano después":**
   Está **estrictamente prohibido** preguntar al usuario datos que puedan responderse inspeccionando los archivos del repositorio (manifiestos, controladores, esquemas de BD, migraciones, tests o `graphify-out/`). Investiga el código antes de formular una pregunta.
2. **Estrategia de Interacción por Entorno:**
   - **Pausa Estructurada en Chat (`A/B/C`):** Presenta de 2 a 4 preguntas con opciones `A) (Recomendado) ... / B) ... / C) ...` y **detén la ejecución** hasta que el usuario responda explícitamente antes de editar archivos.
3. **Árbol de Decisión Quirúrgico Backend:**
   Enfoca tus preguntas exclusivamente en los artefactos del framework:
   - **Reglas Invariantes (`[BR-*]`):** Validaciones cruzadas, precondiciones de negocio y casos borde.
   - **Contratos OCL (`pre`/`post`/`inv`):** En lógica cuantitativa (saldos, cupos, límites) o máquinas de estado.
   - **Garantías Operativas (`api-contracts.md`):** Estrategia de idempotencia (`Idempotency-Key`), nivel de concurrencia y aislamiento transaccional (`optimistic` vs. `pessimistic locking`), autorización RBAC/anti-IDOR y presupuesto de latencia/timeouts.
   - **Onboarding Brownfield:** Distinguir intenciones: *"En `PaymentService:128` no se valida saldo mínimo: ¿es un comportamiento intencional para clientes corporativos (regla As-Is) o un bug que registro en `audit-proposals.md`?"*

---

## 📋 Protocolo de Cierre
Al resolver todas las ramas del árbol de decisión:
1. Sintetiza los acuerdos en una lista concisa de decisiones tomadas.
2. Invoca el siguiente paso correspondiente:
   - En features nuevas: formalizar en `docs/functional/use-cases/`, `docs/technical/` y registrar el `REQ-*` en `pending.md`.
   - En brownfield: registrar el `UC-*.md` o la entrada en `audit-proposals.md`.
