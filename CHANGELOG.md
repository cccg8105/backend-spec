# Registro de Cambios (Changelog)

Todos los cambios notables en este proyecto se documentan en este archivo.

El formato se basa en [Keep a Changelog](https://keepachangelog.com/es-ES/1.1.0/) y este proyecto se adhiere a [Semantic Versioning 2.0.0](https://semver.org/lang/es/).

---

## Guía de Versionamiento Semántico (SemVer)

Las versiones se estructuran bajo el esquema `MAJOR.MINOR.PATCH`:

- **MAJOR (x.0.0):** Cambios que rompen la compatibilidad hacia atrás (breaking changes). Ejemplos: reestructuración obligatoria de directorios (`.spec/`, `docs/`), cambios en la sintaxis de esquemas JSON que invalidan especificaciones anteriores, eliminación o cambio de argumentos obligatorios en comandos del CLI.
- **MINOR (0.x.0):** Nuevas funcionalidades que mantienen la compatibilidad hacia atrás. Ejemplos: soporte para nuevos harnesses de IA, nuevos comandos en el CLI, adición de detectores de nuevos frameworks o lenguajes, nuevos campos opcionales en esquemas o plantillas.
- **PATCH (0.0.x):** Correcciones de errores y mejoras internas que mantienen la compatibilidad hacia atrás. Ejemplos: corrección de expresiones regulares en el validador, ajustes en mensajes de ayuda, correcciones de enlaces en plantillas, actualización de documentación.

---

## [Unreleased]

### Planned
- Soporte para exportación automática de contratos a colecciones Postman y OpenAPI 3.1.
- Detección ampliada para arquitecturas Serverless (AWS Lambda, Cloudflare Workers).

---

## [1.1.0] - 2026-11-04

### Changed
- Actualización y consolidación de la documentación técnica en `README.md`.
- Normalización estilística de títulos y encabezados en toda la documentación para alineación con estándares profesionales.
- Refuerzo en las directivas de actualización no destructiva (`backend-spec update`) para proyectos existentes.

---

## [1.0.0] - 2026-11-01

### Added
- Lanzamiento inicial del framework y herramienta de línea de comandos `backend-spec`.
- CLI ejecutable en Python estándar (>= 3.9) con cero dependencias externas en tiempo de ejecución:
  - `backend-spec init`: Inicialización interactiva o desatendida de la estructura `.spec/` y `docs/`.
  - `backend-spec bootstrap`: Escaneo automático de repositorios existentes (*Brownfield*) con generación de `.spec/bootstrap-report.md`.
  - `backend-spec req:new`: Creación delimitada de requerimientos para carril completo o carril *Fast-Track*.
  - `backend-spec check`: Validación estricta de enlaces físicos, esquemas JSON Draft-07 y verificación de commits con `--staged`.
  - `backend-spec sync`: Sincronización automática de índices en `docs/functional/` y `docs/backlog/`.
  - `backend-spec resolve`: Cierre y archivado inmutable de requerimientos con actualización automática de versión (`--bump`).
  - `backend-spec update`: Actualización segura de reglas de agentes y plantillas sin modificar `docs/`.
- Motor de validación propio (`schema_validator.py`):
  - Parser independiente de bloques YAML Frontmatter.
  - Validador JSON Schema Draft-07 nativo sin librerías externas.
- Detector de ecosistemas backend (`ecosystem_detector.py`):
  - Soporte para Node.js/TypeScript (NestJS, Express, Fastify).
  - Soporte para Python (FastAPI, Django, Flask).
  - Soporte para Java / Spring Boot (Maven y Gradle).
  - Soporte para Kotlin (Gradle Kotlin DSL).
  - Soporte para Rust (Actix, Axum).
  - Soporte para Go (Gin, Echo, Fiber).
- Extractor y actualizador de versiones (`version_extractor.py`) con soporte para SemVer, CalVer y Sequential, incluyendo validación anti-downgrade.
- Esquemas JSON formales en `schemas/`:
  - `use-case.schema.json`: Esquema para especificaciones funcionales y reglas de negocio.
  - `requirement.schema.json`: Esquema para requerimientos en `pending.md` y `changelog.md`.
  - `technical/`: Esquemas para contratos de API, diseño de componentes, modelo de datos, estrategia de despliegue y stack tecnológico.
- Protocolo Gatekeeper de Dos Velocidades:
  - Carril Completo (`MAJOR` / `MINOR`): Entrevista, Caso de Uso formal con Mermaid y OCL, contratos técnicos y aprobación explícita.
  - Carril *Fast-Track* (`PATCH`): Micro-especificación ágil para hotfixes y refactorizaciones sin alteración de contratos.
- Adopción formal de Object Constraint Language (OCL):
  - Guía normativa `ocl-guidelines.md` para precondiciones (`pre`), postcondiciones (`post` con `@pre`) e invariantes (`inv`).
- Soporte Multi-Harness para agentes de Inteligencia Artificial:
  - Reglas y comandos para Google Antigravity (`rules/backend-spec.md`).
  - Adaptador para Claude Code (`CLAUDE.md` y skills/comandos).
  - Reglas para Cursor (`.cursor/rules/backend-spec.mdc` y comandos).
  - Configuración y workflows para Windsurf (`.windsurfrules`).
- Mecanismo de protección en Git:
  - Hook `pre-commit` para prevenir *commits fantasma* de código fuente sin trazabilidad en el backlog.
- Proyecto de referencia completo en `examples/sample-payment-api/`.
- Batería integral de pruebas unitarias en `cli/tests/`.

---

## [0.1.0] - 2026-10-31

### Added
- Inicialización del repositorio y estructura base del proyecto.

---

[Unreleased]: https://github.com/cesarcardenas/backend-spec/compare/v1.1.0...HEAD
[1.1.0]: https://github.com/cesarcardenas/backend-spec/compare/v1.0.0...v1.1.0
[1.0.0]: https://github.com/cesarcardenas/backend-spec/compare/v0.1.0...v1.0.0
[0.1.0]: https://github.com/cesarcardenas/backend-spec/releases/tag/v0.1.0
