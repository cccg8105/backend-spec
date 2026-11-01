# Comando: 01_plan_functional

> **Propósito:** Redactar o actualizar formalmente un caso de uso funcional (Etapa 1 — Carril Completo `MAJOR` / `MINOR`).

## Instrucciones para el Agente:
1. Analiza los requerimientos de negocio sin acoplarlos a librerías ni ORMs.
2. Identifica el dominio (ej. `auth`, `billing`, `orders`) y determina el siguiente ID secuencial (ej. `UC-BILL-001`).
3. Crea `docs/functional/use-cases/UC-[DOMINIO]-[NUM]-[slug].md` tomando como molde `.spec/templates/_template_use_case.md`.
4. Incluye obligatoriamente:
   - Cabecera *YAML Frontmatter* (`id`, `title`, `domain`, `actor`, `status`, `ocl_applied`).
   - Diagrama de proceso en Mermaid (`flowchart TD` o `sequenceDiagram`).
   - Tablas de Entrada (`Inputs Requeridos`) y Salida (`Output Esperado`).
   - Reglas de negocio `[BR-XX]` con bloques OCL (`pre`/`post`) cuando aplique la Matriz Heurística OCL (`.spec/templates/ocl-guidelines.md`).
   - Tabla `## 📜 Historial de Revisiones` (máx. 3 filas).
5. Ejecuta `backend-spec sync` y `backend-spec check` para actualizar `docs/functional/index.md` y validar contra `schemas/use-case.schema.json`.
