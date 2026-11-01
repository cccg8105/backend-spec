---
artifact_type: tech-stack
---

# Stack Tecnológico y Convenciones Técnicas (Blueprint de Referencia)

## 1. Núcleo Tecnológico

| Componente | Tecnología Seleccionada | Versión | Justificación |
| :--- | :--- | :--- | :--- |
| **Lenguaje / Runtime** | TypeScript / Node.js | v20 LTS | Tipado estático robusto y alto rendimiento asíncrono. |
| **Framework HTTP** | Fastify / NestJS / Express | - | Modularidad y ecosistema estándar. |
| **Persistencia / ORM** | Prisma / TypeORM / SQLAlchemy | - | Migraciones tipadas y prevención de inyección SQL. |
| **Base de Datos** | PostgreSQL | v16 | Integridad referencial ACID y soporte JSONB. |
| **Caché & Colas** | Redis | v7 | Sesiones, idempotencia, rate limiting y colas. |
| **Testing** | Vitest / Pytest / JUnit | - | Ejecución rápida de pruebas unitarias e integración. |

---

## 2. Convenciones de Código y Nomenclatura

- **Archivos:** Convención idiomática del ecosistema (`kebab-case.ts`, `snake_case.py`, `PascalCase.java`).
- **Clases e Interfaces:** `PascalCase`.
- **Variables de Entorno:** `UPPER_SNAKE_CASE`.

---

## 3. Políticas Transversales

### A. Manejo Tipado de Errores
- Toda excepción de negocio hereda de `DomainError` y se serializa en la frontera HTTP bajo el estándar RFC 7807 (*Problem Details*).

### B. Logging Estructurado
- Emisión en JSON hacia `stdout` incluyendo `timestamp`, `level`, `message`, `correlationId` y `serviceName`. Prohibido registrar secretos o PII sensible.

### C. Validación de Entradas
- Validación estricta de esquemas en la capa de transporte antes de invocar casos de uso.

---

## 📜 Historial de Revisiones (Últimos Cambios)

| Versión | Fecha | Requerimiento | Resumen del Cambio |
| :--- | :--- | :--- | :--- |
| `v0.1.0` | YYYY-MM-DD | `REQ-CORE-001` | Definición inicial de runtime, librerías y políticas transversales. |

> *Nota: Esta tabla mantiene una ventana deslizante de los últimos 3 cambios. Para el historial completo, consultar [`docs/backlog/changelog.md`](../backlog/changelog.md).*
