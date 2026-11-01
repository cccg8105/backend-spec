# Comando: 02b_plan_components

> **Propósito:** Especificar la arquitectura de software, responsabilidades y contratos entre capas para soportar el caso de uso (Etapa 2B).

## Instrucciones para el Agente:
1. Abre `docs/technical/component-design.md`.
2. Define los componentes necesarios siguiendo el patrón arquitectónico del proyecto (Clean Architecture / Hexagonal / Puertos y Adaptadores):
   - **Handlers / Controllers:** Puntos de entrada de transporte (HTTP, gRPC, CLI).
   - **Use Cases / Application Services:** Orquestadores de la lógica de negocio.
   - **Domain Entities & Value Objects:** Representación pura del estado y reglas.
   - **Repository Ports & Infrastructure Adapters:** Interfaces abstractas e implementaciones concretas.
3. Actualiza el diagrama de clases UML en Mermaid (`classDiagram`).
4. Genera el diagrama de secuencia técnica en Mermaid (`sequenceDiagram`) mostrando el flujo de llamadas paso a paso.
5. Documenta los DTOs de entrada y salida entre cada capa.
