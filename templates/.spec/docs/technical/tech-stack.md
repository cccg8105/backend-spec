---
artifact_type: tech-stack
---

# Stack Tecnológico y Convenciones — {{PROJECT_NAME}}

## 1. Núcleo Tecnológico

<!-- SYNC:TECH_STACK:START -->
| Componente | Tecnología Seleccionada | Versión / Manifiesto | Justificación |
| :--- | :--- | :--- | :--- |
| **Lenguaje / Runtime** | {{RUNTIME_NAME}} | `{{MANIFEST_FILE}}` (`v{{CURRENT_VERSION}}`) | Ecosistema principal detectado en el proyecto. |
| **Framework Backend** | Por detallar (`spec bootstrap`) | - | Capa de transporte y enrutamiento. |
| **Persistencia / ORM** | Por detallar (`spec bootstrap`) | - | Acceso a datos y migraciones. |
| **Testing** | Suite nativa del ecosistema | - | Verificación automatizada *Spec-First*. |
<!-- SYNC:TECH_STACK:END -->

---

## 2. Convenciones de Código y Nomenclatura

- **Extensión de Código Fuente:** `*{{SRC_EXT}}`
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
| `v{{CURRENT_VERSION}}` | {{TODAY}} | `INIT` | Configuración base para {{RUNTIME_NAME}}. |

> *Nota: Esta tabla mantiene una ventana deslizante de los últimos 3 cambios. Para el historial completo, consultar [`docs/backlog/changelog.md`](../backlog/changelog.md).*
