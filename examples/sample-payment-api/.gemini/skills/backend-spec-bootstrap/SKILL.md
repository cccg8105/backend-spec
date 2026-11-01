---
name: backend-spec-bootstrap
description: "Guía el onboarding asistido de proyectos backend existentes (Brownfield) en backend-spec mediante ingeniería inversa estructurada en 4 fases, preservando el estado en disco (.spec/bootstrap-report.md)."
---

# backend-spec-bootstrap Skill

Esta skill guía al agente de IA en la ingeniería inversa metódica de repositorios backend preexistentes, convirtiendo código no documentado o con documentación desfasada en especificaciones vivas confiables.

## Cuándo Activar esta Skill
- Al inicializar `backend-spec` en un repositorio existente con código previo (*Brownfield*).
- Cuando el usuario ejecuta `/spec-bootstrap` o solicita documentar la arquitectura actual del proyecto.
- Cuando existen fases o dominios pendientes de levantar (`[ ]`) en `.spec/bootstrap-report.md`.

---

## 🛑 REGLA DE ORO ANTI-PÉRDIDA DE CONTEXTO
1. **Memoria en disco (`.spec/bootstrap-report.md`):** Consulta siempre este archivo antes de comenzar. Contiene el inventario real y la lista de verificación (Checklist GPS).
2. **Un bloque por turno:** Procesa un único dominio o documento técnico a la vez.
3. **Marca tu avance:** Tras completar cada paso, edita `.spec/bootstrap-report.md` cambiando `- [ ]` por `- [x]`. Si la sesión se compacta (`/compact`) o se interrumpe, sabrás exactamente dónde continuar sin releer el código completo.

---

## 🧭 Flujo Operativo en 4 Fases

### Fase 1: Diagnóstico Determinista y Línea Base
1. Ejecuta el comando en consola si aún no se ha generado el reporte:
   ```bash
   backend-spec bootstrap
   ```
2. Si existe `graphify-out/graph.json`, analiza los *God Nodes* y comunidades. Si no existe, ofrece ejecutar `/graphify .` para mapear dependencias.
3. Lee la cabecera de `.spec/bootstrap-report.md` identificando:
   - **Escenario:** `CODE_ONLY` (solo código) vs. `CODE_AND_DOCS` (código + documentación previa).
   - **Línea base de pruebas (`test_baseline`):** `none` (0%), `partial` o `solid`.
   - **Posible desfase:** Revisa si se detectaron advertencias de desfase temporal (*doc drift*) entre documentos y código.

---

### Fase 2: Extracción Técnica As-Is y Conciliación
**Regla de Verdad:** *El código ejecutable manda sobre la documentación antigua.*
1. **Base de Datos y Persistencia:** A partir de esquemas ORM (Prisma, TypeORM, SQLAlchemy, Hibernate, etc.) o migraciones SQL listadas en el reporte, puebla `docs/technical/database-model.md` con su diagrama Mermaid `erDiagram`, diccionario de tablas y notas de índices reales.
2. **Diseño de Componentes y Flujo:** A partir de la estructura de carpetas y dependencias en Graphify, describe las capas en `docs/technical/component-design.md`. **Filtra código muerto:** si encuentras archivos/rutas sin referencias de entrada desde routers o workers, no los asumas como arquitectura activa; anótalos para auditoría.
3. **Contratos API y Operativos:** A partir de controladores y especificaciones (`openapi.yaml`, etc.), puebla `docs/technical/api-contracts.md` con los endpoints reales, mecanismos de autenticación vigentes y supuestos de concurrencia/idempotencia observados en código.
4. Mantén la tabla `## 📜 Historial de Revisiones` en cada documento con un máximo de 3 filas.
5. Marca `[x]` en la sección técnica de `.spec/bootstrap-report.md`.

---

### Fase 3: Selección de Modalidad y Funcional As-Is
Consulta al usuario (usando `/grill-me` o preguntas concisas):
- **Modo Completo (`full`):** Levantar casos de uso funcionales para todos los dominios detectados ahora.
- **Modo Progresivo / Strangler (`progressive`):** Levantar casos de uso únicamente para los 1 o 2 flujos más críticos y dejar los demás como `Detectado (Pendiente As-Is)`.

Para cada dominio a levantar:
1. Inspecciona los controladores y servicios del dominio.
2. Crea el caso de uso en `docs/functional/use-cases/UC-[DOMINIO]-[NUM]-[slug].md` con:
   - Cabecera YAML Frontmatter indicando `status: "As-Is (Brownfield)"`.
   - Diagrama Mermaid del flujo actual.
   - Tablas Inputs / Outputs reales.
   - Reglas de negocio identificadas `[BR-*]`. Aplica OCL (`pre`/`post`/`inv`) solo si hay lógica cuantitativa o de estados clara.
3. **Si surgen dudas de negocio:** Aplica la regla *"Código primero, humano después"*. Solo pregunta al usuario mediante `/grill-me` si un comportamiento anómalo en código (ej. falta de validación o cálculo especial) es una regla intencional de negocio o un defecto.
4. Ejecuta `backend-spec sync` para actualizar `docs/functional/index.md` (los dominios no levantados aparecerán en `Módulos Legados Detectados`).
5. Marca `[x]` en el dominio correspondiente dentro de `.spec/bootstrap-report.md`.

---

### Fase 4: Triage de Auditoría y Cierre
1. Vuelca en `docs/backlog/audit-proposals.md` los hallazgos identificados sin alterar el código fuente:
   - Documentación antigua obsoleta (*doc drift*).
   - Rutas huérfanas o código muerto.
   - Brechas de tests (si `test_baseline: none`, sugiere crear tests de caracterización prioritarios).
   - Vulnerabilidades o riesgos de concurrencia detectados en código.
   - Usa el formato `[AUDIT-[DOMINIO]-[NUMERO]]` con evidencia exacta `archivo:L10-L25`.
2. Ejecuta la validación de integridad:
   ```bash
   backend-spec check
   ```
3. Marca la Fase 4 como completada en `.spec/bootstrap-report.md`.
4. Informa al usuario del resumen del levantamiento y recuérdale que en el trabajo diario, si se toca un módulo pendiente en modo progresivo, se deberá documentar su caso de uso *Just-In-Time* antes de planificar nuevas funcionalidades.
