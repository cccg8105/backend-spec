---
artifact_type: deployment-strategy
rollout_type: rolling
---

# Estrategia de Despliegue, Infraestructura y CI/CD (Blueprint de Referencia)

## 1. Diagrama de Flujo del Pipeline CI/CD (Mermaid)

```mermaid
flowchart LR
    A["Git Push / PR"] --> B["Spec Check & Lint"]
    B --> C["Unit & Integration Tests"]
    C --> D["Security Scan & SAST"]
    D --> E["Build Docker Image Multi-Stage"]
    E --> F{"Branch?"}
    F -->|develop| G["Deploy to Staging"]
    G --> H["Smoke Tests E2E"]
    F -->|main / tag| I["Deploy Production Rolling / Canary"]
    I --> J{"Métricas Saludables?"}
    J -- Sí --> K["Promover a 100%"]
    J -- No --> L["Rollback Automático"]
```

---

## 2. Contenedorización (Dockerfile Multi-Stage)
- Separación entre etapa de compilación (*builder*) y ejecución (*runtime*), corriendo con usuario sin privilegios (`nonroot`) sobre imagen ligera (`alpine` / `slim` / `distroless`).

---

## 3. Variables de Entorno y Configuración

| Variable | Descripción | Ejemplo / Formato | Secreto? |
| :--- | :--- | :--- | :--- |
| `APP_ENV` | Entorno de ejecución | `production` / `staging` | No |
| `PORT` | Puerto de escucha HTTP | `8080` | No |
| `DATABASE_URL` | Cadena de conexión a BD | `postgresql://user:pass@host:5432/db` | Sí (Vault) |

---

## 4. Health Checks y Estrategia de Rollout
- **Liveness Probe:** `GET /health/live` (`200 OK` si el proceso responde).
- **Readiness Probe:** `GET /health/ready` (`200 OK` solo si dependencias críticas están operativas).
- **Rollout y Aborto:** Rolling Update con rollback automático si HTTP 5xx > 1% o latencia p95 supera el umbral durante los primeros 5 minutos.

---

## 📜 Historial de Revisiones (Últimos Cambios)

| Versión | Fecha | Requerimiento | Resumen del Cambio |
| :--- | :--- | :--- | :--- |
| `v0.1.0` | YYYY-MM-DD | `REQ-CORE-001` | Configuración inicial de CI/CD, contenedorización y probes. |

> *Nota: Esta tabla mantiene una ventana deslizante de los últimos 3 cambios. Para el historial completo, consultar [`docs/backlog/changelog.md`](../backlog/changelog.md).*
