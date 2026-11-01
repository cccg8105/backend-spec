import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

cli_dir = Path(__file__).resolve().parent.parent
if str(cli_dir) not in sys.path:
    sys.path.insert(0, str(cli_dir))

from backend_spec.commands.bootstrap_cmd import run_bootstrap
from backend_spec.commands.check_cmd import run_check
from backend_spec.commands.init_cmd import run_init
from backend_spec.commands.new_req_cmd import run_new_req
from backend_spec.commands.resolve_cmd import run_resolve
from backend_spec.commands.sync_index_cmd import run_sync_index
from backend_spec.validator.schema_validator import count_rolling_history_rows


class TestValidatorAndNegativeCases(unittest.TestCase):
    def setUp(self):
        self.test_dir = Path(tempfile.mkdtemp())

    def tearDown(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_anti_downgrade_protection_on_resolve(self):
        (self.test_dir / "package.json").write_text(
            '{\n  "name": "legacy-api",\n  "version": "2.4.0"\n}\n', encoding="utf-8"
        )
        run_init(self.test_dir, harness="antigravity")
        req_id = run_new_req(
            self.test_dir,
            domain="core",
            title="Legacy hotfix",
            impact="PATCH",
            target_version="v0.2.0",
        )
        self.assertTrue(run_resolve(self.test_dir, req_id, auto_bump=True))
        pkg = json.loads((self.test_dir / "package.json").read_text(encoding="utf-8"))
        # Protección anti-downgrade debe conservar 2.4.0
        self.assertEqual(pkg["version"], "2.4.0")

    def test_go_mod_is_never_corrupted(self):
        go_mod = self.test_dir / "go.mod"
        go_mod_text = "module github.com/acme/ledger\n\ngo 1.22.5\n"
        go_mod.write_text(go_mod_text, encoding="utf-8")

        run_init(self.test_dir, harness="claude")
        self.assertEqual(go_mod.read_text(encoding="utf-8"), go_mod_text)
        self.assertTrue((self.test_dir / "VERSION").exists())

        req_id = run_new_req(self.test_dir, domain="ledger", title="Fix balance lock", impact="PATCH")
        self.assertTrue(run_resolve(self.test_dir, req_id, auto_bump=True))
        self.assertEqual(go_mod.read_text(encoding="utf-8"), go_mod_text)
        self.assertEqual((self.test_dir / "VERSION").read_text(encoding="utf-8").strip(), "0.2.0")

    def test_broken_links_and_missing_modify_boundaries_fail_check(self):
        run_init(self.test_dir, harness="antigravity")
        tech_index = self.test_dir / "docs" / "technical" / "index.md"
        tech_index.write_text(
            tech_index.read_text(encoding="utf-8") + "\n- [Enlace Muerto](./no-existe.md)\n",
            encoding="utf-8",
        )
        self.assertFalse(run_check(self.test_dir))

        # Restaurar índice técnico, pero agregar un archivo [MODIFY] que no existe en disco
        run_init(self.test_dir, harness="antigravity", force=True)
        pending = self.test_dir / "docs" / "backlog" / "pending.md"
        pending.write_text(
            pending.read_text(encoding="utf-8")
            + """
### [REQ-CORE-001] Modificar servicio inexistente
- **Prioridad:** P1
- **Tipo:** Hotfix / Fix (PATCH - Fast-Track)
- **Versión Objetivo:** `v0.2.0`
- **Referencia Funcional:** `N/A (PATCH / Fast-Track)`
- **Referencia Técnica:** `docs/technical/component-design.md`

#### Fronteras y Artefactos:
- **Artefactos a Modificar / Crear:**
  - `src/missing_service.py` [MODIFY]
- **Restricciones:**
  - Ninguna

#### Criterios de Aceptación:
- [ ] Corregir fallo
""",
            encoding="utf-8",
        )
        self.assertFalse(run_check(self.test_dir))

    def test_use_case_schema_validation_and_functional_sync(self):
        run_init(self.test_dir, harness="antigravity")
        bad_uc = self.test_dir / "docs" / "functional" / "use-cases" / "UC-BAD.md"
        bad_uc.write_text("# Documento incompleto sin frontmatter ni tablas ni mermaid\n", encoding="utf-8")
        self.assertFalse(run_check(self.test_dir))
        bad_uc.unlink()

        valid_uc = self.test_dir / "docs" / "functional" / "use-cases" / "UC-AUTH-001-login.md"
        valid_uc.write_text(
            """---
id: UC-AUTH-001
title: Inicio de Sesion Seguro
domain: auth
actor: Usuario Registrado
status: Activo
ocl_applied: false
---

# UC-AUTH-001: Inicio de Sesion Seguro

## 1. Contexto & Actores
- **Dominio:** `auth`
- **Actor Principal:** `Usuario Registrado`
- **Disparador (Trigger):** `POST /api/v1/auth/login`

## 2. Diagrama del Proceso de Negocio (Mermaid)
```mermaid
flowchart TD
    A["Recibir credenciales"] --> B["Emitir JWT"]
```

## 3. Contrato de Entrada y Salida
### Inputs Requeridos:
| Campo | Tipo | Obligatorio | Validaciones |
| :--- | :--- | :--- | :--- |
| `email` | String | Sí | Formato RFC 5322 |

### Output Esperado:
| Campo | Tipo | Descripción |
| :--- | :--- | :--- |
| `accessToken` | String | Token firmado |

## 4. Reglas de Negocio Asociadas
- **[BR-01] Credenciales Verificadas:**
  - **Descripción:** Solo usuarios activos con hash válido reciben token.

## 📜 Historial de Revisiones (Últimos Cambios)
| Versión | Fecha | Requerimiento | Resumen |
| :--- | :--- | :--- | :--- |
| `v0.2.0` | 2026-10-31 | `REQ-AUTH-001` | Alta inicial |
""",
            encoding="utf-8",
        )
        _, ucs_count = run_sync_index(self.test_dir)
        self.assertEqual(ucs_count, 1)
        func_idx = (self.test_dir / "docs" / "functional" / "index.md").read_text(encoding="utf-8")
        self.assertIn("`UC-AUTH-001`", func_idx)
        self.assertTrue(run_check(self.test_dir))

    def test_rolling_window_row_counter(self):
        sample_md = """# Doc
## 📜 Historial de Revisiones (Últimos Cambios)
| Versión | Fecha | Requerimiento | Resumen |
| :--- | :--- | :--- | :--- |
| v4 | 2026-10-31 | REQ-4 | Cambio 4 |
| v3 | 2026-10-30 | REQ-3 | Cambio 3 |
| v2 | 2026-10-29 | REQ-2 | Cambio 2 |
| v1 | 2026-10-28 | REQ-1 | Cambio 1 |
"""
        self.assertEqual(count_rolling_history_rows(sample_md), 4)

    def test_staged_phantom_commit_blocking_and_approval(self):
        # Inicializar repositorio Git real en directorio temporal
        subprocess.run(["git", "init"], cwd=str(self.test_dir), check=True, capture_output=True)
        (self.test_dir / "pyproject.toml").write_text('[project]\nname="api"\nversion="1.0.0"\n', encoding="utf-8")
        run_init(self.test_dir, harness="claude")

        # Crear y hacer git add de un archivo de código fuente SIN ningún REQ-* activo
        src_file = self.test_dir / "src" / "application" / "payments_charge.py"
        src_file.parent.mkdir(parents=True, exist_ok=True)
        src_file.write_text("def charge():\n    return True\n", encoding="utf-8")
        subprocess.run(["git", "add", "src/application/payments_charge.py"], cwd=str(self.test_dir), check=True, capture_output=True)

        # Debe bloquearse por commit fantasma
        self.assertFalse(run_check(self.test_dir, check_staged=True))

        # Registrar requerimiento PATCH que declara exactamente ese archivo
        run_new_req(self.test_dir, domain="payments", title="charge", impact="PATCH")
        self.assertTrue(run_check(self.test_dir, check_staged=True))

    def test_brownfield_bootstrap_inventory(self):
        (self.test_dir / "pyproject.toml").write_text(
            '[project]\nname = "orders-api"\nversion = "1.3.0"\ndependencies = ["fastapi", "sqlalchemy", "alembic", "pytest"]\n',
            encoding="utf-8",
        )
        (self.test_dir / "openapi.yaml").write_text("openapi: 3.1.0\n", encoding="utf-8")
        router = self.test_dir / "src" / "orders" / "order_router.py"
        model = self.test_dir / "src" / "orders" / "order_model.py"
        router.parent.mkdir(parents=True, exist_ok=True)
        router.write_text("# router\n", encoding="utf-8")
        model.write_text("# model\n", encoding="utf-8")

        graph_dir = self.test_dir / "graphify-out"
        graph_dir.mkdir()
        (graph_dir / "graph.json").write_text(
            json.dumps({
                "nodes": [{"id": "n1", "label": "OrderService"}, {"id": "n2", "label": "OrderRepository"}],
                "links": [{"source": "n1", "target": "n2"}],
            }),
            encoding="utf-8",
        )

        run_init(self.test_dir, harness="antigravity")
        report_path = run_bootstrap(self.test_dir)
        self.assertTrue(report_path.exists())

        tech_stack = (self.test_dir / "docs" / "technical" / "tech-stack.md").read_text(encoding="utf-8")
        self.assertIn("FastAPI", tech_stack)
        self.assertIn("SQLAlchemy", tech_stack)

        cfg = (self.test_dir / ".spec" / "config.yaml").read_text(encoding="utf-8")
        self.assertIn("- orders", cfg)

        api_contracts = (self.test_dir / "docs" / "technical" / "api-contracts.md").read_text(encoding="utf-8")
        self.assertIn("openapi.yaml", api_contracts)
        self.assertTrue(run_check(self.test_dir))

    def test_installed_wheel_layout_and_pyproject_toml(self):
        import os
        import tomllib

        repo_root = Path(__file__).resolve().parents[2]
        pyproject_data = tomllib.loads((repo_root / "pyproject.toml").read_text(encoding="utf-8"))
        force_inc = pyproject_data["tool"]["hatch"]["build"]["targets"]["wheel"]["force-include"]
        self.assertEqual(force_inc["templates"], "backend_spec/templates")
        self.assertEqual(force_inc["harnesses"], "backend_spec/harnesses")
        self.assertEqual(force_inc["schemas"], "backend_spec/schemas")

        # Simular site-packages aislado sin carpetas templates/ en niveles padres
        fake_site = self.test_dir / "isolated_env" / "Lib" / "site-packages"
        fake_pkg = fake_site / "backend_spec"
        shutil.copytree(repo_root / "cli" / "backend_spec", fake_pkg)
        for asset_dir, target_rel in force_inc.items():
            shutil.copytree(repo_root / asset_dir, fake_site / target_rel)

        target_proj = self.test_dir / "external_user_project"
        target_proj.mkdir()
        sub_env = {**os.environ, "PYTHONPATH": str(fake_site), "PYTHONIOENCODING": "utf-8"}

        res = subprocess.run(
            [sys.executable, "-m", "backend_spec", "init", "--dir", str(target_proj), "--harness", "antigravity"],
            cwd=str(target_proj),
            env=sub_env,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=20,
        )
        self.assertEqual(res.returncode, 0, msg=(res.stderr or "") + "\n" + (res.stdout or ""))
        self.assertTrue((target_proj / "docs" / "technical" / "api-contracts.md").exists())
        self.assertTrue((target_proj / ".spec" / "templates" / "_template_use_case.md").exists())

        res_check = subprocess.run(
            [sys.executable, "-m", "backend_spec", "check", "--dir", str(target_proj)],
            cwd=str(target_proj),
            env=sub_env,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=20,
        )
        self.assertEqual(res_check.returncode, 0, msg=(res_check.stderr or "") + "\n" + (res_check.stdout or ""))


if __name__ == "__main__":
    unittest.main()
