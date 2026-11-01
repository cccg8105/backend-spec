---
artifact_type: tech-stack
---

# Stack Tecnológico y Convenciones — sample-payment-api

## 1. Núcleo Tecnológico

<!-- SYNC:TECH_STACK:START -->
| Componente | Tecnología Seleccionada | Versión / Manifiesto | Justificación |
| :--- | :--- | :--- | :--- |
| **Lenguaje / Runtime** | Node.js / TypeScript (NestJS, Express, Fastify) | `package.json` (`v1.0.0`) | Detectado por `spec bootstrap`. |
| **Framework Backend** | Express.js | Manifiesto | Detectado en dependencias del proyecto. |
| **Persistencia / ORM** | Prisma ORM, Prisma Client | Manifiesto | Detectado en dependencias y esquemas. |
| **Testing** | Vitest | Manifiesto | Suite de verificación detectada. |
<!-- SYNC:TECH_STACK:END -->

---

## 2. Convenciones de Código y Nomenclatura

- **Extensión de Código Fuente:** `*.ts`
- **Clases, Tipos y Entidades:** `PascalCase`
- **Constantes y Variables de Entorno:** `UPPER_SNAKE_CASE`

---

## 3. Políticas Transversales

### A. Manejo Tipado de Errores
- Toda excepción de dominio se traduce en la capa de transporte al estándar RFC 7807 (*Problem Details*) sin filtrar trazas internas en producción.

### B. Logging Estructurado
- Logs estructurados en JSON hacia `stdout` con `timestamp`, `level`, `message` y `correlationId`. Prohibido registrar credenciales, secretos o datos sensibles.

### C. Validación de Entradas
- Todo input externo se valida estrictamente antes de invocar la capa de aplicación.

---

## 📜 Historial de Revisiones (Últimos Cambios)

| Versión | Fecha | Requerimiento | Resumen del Cambio |
| :--- | :--- | :--- | :--- |
| `v1.0.0` | 2026-10-31 | `INIT` | Configuración base para Node.js / TypeScript (NestJS, Express, Fastify). |

> *Nota: Esta tabla mantiene una ventana deslizante de los últimos 3 cambios. Para el historial completo, consultar [`docs/backlog/changelog.md`](../backlog/changelog.md).*
