# Índice de Documentación Técnica — sample-payment-api

> **Instrucción para el Agente de IA:**
> Utiliza este índice para cargar **únicamente** el documento técnico relevante para tu tarea actual:
> - ¿Tablas, columnas, índices o migraciones? → [`database-model.md`](./database-model.md)
> - ¿Capas, clases, puertos/adaptadores o invariantes `inv` de dominio? → [`component-design.md`](./component-design.md)
> - ¿Endpoints HTTP/gRPC, eventos asíncronos, idempotencia, concurrencia, RBAC o SLAs? → [`api-contracts.md`](./api-contracts.md)
> - ¿Runtimes, librerías autorizadas, formato RFC 7807 o logging? → [`tech-stack.md`](./tech-stack.md)
> - ¿Dockerfiles, CI/CD, variables de entorno o health checks? → [`deployment-strategy.md`](./deployment-strategy.md)
> - Plantillas de referencia y scaffolding BDD (*Spec-First*): [`.spec/templates/`](../../.spec/templates/)

---

## Artefactos Técnicos del Sistema

| Artefacto | Archivo | Responsabilidad y Contenido Clave |
| :--- | :--- | :--- |
| **Modelo de Persistencia** | [database-model.md](./database-model.md) | Diagrama ER en Mermaid, diccionario de tablas/columnas, índices y política de migraciones/rollback. |
| **Diseño de Componentes** | [component-design.md](./component-design.md) | Arquitectura en capas, diagramas UML/Secuencia en Mermaid e invariantes formales OCL (`inv`). |
| **Contratos API, Eventos y RNFs** | [api-contracts.md](./api-contracts.md) | Endpoints HTTP/gRPC, catálogo de eventos asíncronos, idempotencia, concurrencia, seguridad RBAC y SLAs. |
| **Stack & Convenciones** | [tech-stack.md](./tech-stack.md) | Runtime (`Node.js / TypeScript (NestJS, Express, Fastify)`), dependencias detectadas, nomenclatura (`*.ts`), errores RFC 7807 y logging. |
| **Estrategia de Despliegue** | [deployment-strategy.md](./deployment-strategy.md) | Flujo CI/CD en Mermaid, contenedorización segura, variables de entorno, probes y rollout. |

---

## Principios Técnicos Invariables
1. **Separación de Responsabilidades:** La lógica de negocio vive en Casos de Uso y Entidades de dominio; los Controladores adaptan transporte y los Repositorios adaptan persistencia.
2. **Sincronía Visual y Contractual:** Todo cambio en tablas actualiza `database-model.md`; todo cambio en endpoints, eventos o concurrencia actualiza `api-contracts.md`.
