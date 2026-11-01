# Estrategia y Gobernanza de Versionamiento — sample-payment-api

> **Instrucción para el Agente de IA:**
> Consulta este documento al crear cualquier requerimiento (`REQ-*`) para clasificar su impacto (`MAJOR`, `MINOR`, `PATCH`), elegir el carril de ceremonia adecuado y asignar `target_version`.

---

## 1. Esquema Activo del Proyecto: `SemVer 2.0.0` (`semver`)

- **Archivo Manifiesto Sincronizado:** `package.json`
- **Versión Base Detectada:** `v1.0.0`
- **Milestone Inicial en Desarrollo:** `v1.1.0`

---

## 2. Clasificación de Impacto y Niveles de Ceremonia

### A. `MAJOR` — Cambio Incompatible (*Breaking Change* → Carril Completo + `/boost`)
- Eliminación o cambio incompatible de endpoints HTTP/gRPC, payloads obligatorios o eventos públicos.
- Migraciones destructivas en base de datos.
- **Ceremonia exigida:** Entrevista `/grill-me` + Caso de Uso + Mermaid + OCL (si aplica) + `api-contracts.md` / `database-model.md` + BDD Scaffold + Gatekeeper `/plan`.

### B. `MINOR` — Nueva Funcionalidad Retrocompatible (Carril Completo)
- Nuevos casos de uso, endpoints, eventos o columnas opcionales/con valor por defecto sin romper consumidores actuales.
- **Ceremonia exigida:** Entrevista `/grill-me` + Caso de Uso + Mermaid + OCL (según matriz heurística) + actualización técnica si aplica + BDD Scaffold + Gatekeeper `/plan`.

### C. `PATCH` — Corrección de Bug o Ajuste Interno (**Carril Fast-Track / Micro-Spec**)
- Corrección de defectos, condiciones de carrera, optimización de queries o refactorización interna manteniendo intactos los contratos públicos y el esquema de datos.
- **Ceremonia reducida (*Fast-Track*):**
  1. **No** requiere crear nuevos casos de uso ni diagramas Mermaid (`Referencia Funcional: N/A (PATCH / Fast-Track)` o enlace al caso existente si corrige una regla documentada).
  2. Registro compacto del `REQ-*` con impacto `PATCH` en `docs/backlog/pending.md`.
  3. Test de regresión que reproduce el defecto antes de aplicar el fix.

---

## 3. Reglas por Esquema Configurado
- **`semver`:** `MAJOR.MINOR.PATCH` (ej. `1.2.0` → `1.2.1` en `PATCH`, `1.3.0` en `MINOR`, `2.0.0` en `MAJOR`).
- **`calver`:** `YYYY.MM.MICRO` (ej. `2026.10.1` → incremento de ciclo calendario o micro-release).
- **`sequential`:** Incremento secuencial de release (`v1`, `v2`, o `0.N.0` según convención del equipo).

---

## 4. Sincronización Segura con el Código Fuente
1. `backend-spec resolve <REQ-ID>` archiva el requerimiento en `changelog.md` sin alterar el manifiesto hasta que el desarrollador o release manager lo indique.
2. `backend-spec resolve <REQ-ID> --bump` actualiza la versión en `package.json` y `.spec/config.yaml`, **bloqueando automáticamente cualquier regresión (*downgrade*)** respecto a la versión actual del manifiesto.
