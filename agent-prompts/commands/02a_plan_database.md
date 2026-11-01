# Comando: 02a_plan_database

> **Propósito:** Especificar o actualizar el modelo de base de datos y persistencia a partir de los casos de uso funcionales (Etapa 2A).

## Instrucciones para el Agente:
1. Abre `docs/technical/database-model.md` e identifica las tablas o entidades involucradas en los nuevos casos de uso.
2. Si se requieren nuevas tablas o campos:
   - Actualiza el diagrama ER en Mermaid (`erDiagram`).
   - Añade o actualiza la sección del diccionario de datos tabular (nombre de campo, tipo, nulo, por defecto, claves primarias/foráneas, índices).
   - Documenta la estrategia de migración y el script de rollback correspondiente.
3. Asegúrate de respetar los principios de normalización e integridad referencial (claves foráneas, restricciones de unicidad y checks).
4. No mezcles lógica de controladores ni código fuente aquí; este documento es puramente el contrato de persistencia.
