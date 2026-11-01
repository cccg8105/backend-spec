import json
import shutil
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
from backend_spec.commands.sync_index_cmd import run_sync_index
from backend_spec.commands.update_cmd import run_update


class TestBrownfieldAndGrill(unittest.TestCase):
    def setUp(self):
        self.test_dir = Path(tempfile.mkdtemp())

    def tearDown(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_scenario_code_only_zero_tests(self):
        """Escenario: Repositorio con controladores y modelos pero 0% pruebas y sin docs previas."""
        (self.test_dir / "package.json").write_text(
            '{\n  "name": "legacy-zero-tests",\n  "version": "0.5.0",\n  "dependencies": {\n    "fastify": "^4.0.0",\n    "prisma": "^5.0.0"\n  }\n}\n',
            encoding="utf-8",
        )
        (self.test_dir / ".git").mkdir()

        # Simular controladores y esquemas
        src_auth = self.test_dir / "src" / "auth"
        src_billing = self.test_dir / "src" / "billing"
        src_auth.mkdir(parents=True, exist_ok=True)
        src_billing.mkdir(parents=True, exist_ok=True)

        (src_auth / "auth.controller.ts").write_text("// login route", encoding="utf-8")
        (src_billing / "charge.routes.ts").write_text("// charge route", encoding="utf-8")
        (self.test_dir / "schema.prisma").write_text("model User { id Int @id }", encoding="utf-8")

        # 1. Init
        run_init(self.test_dir, harness="all")
        self.assertTrue((self.test_dir / "docs" / "technical" / "tech-stack.md").exists())

        # 2. Bootstrap
        report_path = run_bootstrap(self.test_dir)
        self.assertTrue(report_path.exists())

        report_text = report_path.read_text(encoding="utf-8")
        self.assertIn('scenario: "CODE_ONLY"', report_text)
        self.assertIn('test_baseline: "none"', report_text)
        self.assertIn("## 0. Checklist de Progreso (GPS para el Agente)", report_text)
        self.assertIn("- [ ] Dominio `auth`:", report_text)
        self.assertIn("- [ ] Dominio `billing`:", report_text)

        # Verificar que audit-proposals.md fue creado
        audit_file = self.test_dir / "docs" / "backlog" / "audit-proposals.md"
        self.assertTrue(audit_file.exists())

        # Verificar que docs/functional/index.md tiene la tabla de pendientes (Modo Progresivo)
        func_index = (self.test_dir / "docs" / "functional" / "index.md").read_text(encoding="utf-8")
        self.assertIn("Módulos Legados Detectados (Modo Progresivo — Pendientes de Levantamiento As-Is)", func_index)
        self.assertIn("`auth`", func_index)
        self.assertIn("`billing`", func_index)

        # Integrity check pasa
        self.assertTrue(run_check(self.test_dir))

    def test_scenario_code_and_docs_drift_and_gps_preservation(self):
        """Escenario: Código + docs previos con doc drift, y preservación de progreso GPS [x] en bootstrap."""
        (self.test_dir / "package.json").write_text(
            '{\n  "name": "legacy-with-docs",\n  "version": "1.0.0"\n}\n', encoding="utf-8"
        )
        (self.test_dir / ".git").mkdir()

        # Documentación previa
        (self.test_dir / "ARCHITECTURE.md").write_text("# Arquitectura vieja del 2023\n", encoding="utf-8")

        # Código más reciente
        src_orders = self.test_dir / "src" / "orders"
        src_orders.mkdir(parents=True, exist_ok=True)
        (src_orders / "orders.controller.ts").write_text("// post order", encoding="utf-8")

        run_init(self.test_dir, harness="all")
        report_path = run_bootstrap(self.test_dir)
        report_text = report_path.read_text(encoding="utf-8")

        self.assertIn('scenario: "CODE_AND_DOCS"', report_text)
        self.assertIn("ARCHITECTURE.md", report_text)

        # El agente avanza y marca casillas en .spec/bootstrap-report.md
        modified_report = report_text.replace(
            "- [ ] Poblar `docs/technical/database-model.md` desde modelos y migraciones",
            "- [x] Poblar `docs/technical/database-model.md` desde modelos y migraciones",
        )
        report_path.write_text(modified_report, encoding="utf-8")

        # Re-ejecutar bootstrap sin --reset debe preservar la casilla [x]
        run_bootstrap(self.test_dir, reset=False)
        refreshed_text = report_path.read_text(encoding="utf-8")
        self.assertIn("- [x] Poblar `docs/technical/database-model.md` desde modelos y migraciones", refreshed_text)

        # Con --reset debe volver a [ ]
        run_bootstrap(self.test_dir, reset=True)
        reset_text = report_path.read_text(encoding="utf-8")
        self.assertIn("- [ ] Poblar `docs/technical/database-model.md` desde modelos y migraciones", reset_text)

    def test_progressive_graduation_and_audit_promotion(self):
        """Verifica la graduación de dominios detectados al crear UC As-Is y la promoción de propuestas con req:new --from-audit."""
        (self.test_dir / "package.json").write_text(
            '{\n  "name": "progressive-api",\n  "version": "1.0.0"\n}\n', encoding="utf-8"
        )
        (self.test_dir / ".git").mkdir()

        src_orders = self.test_dir / "src" / "orders"
        src_users = self.test_dir / "src" / "users"
        src_orders.mkdir(parents=True, exist_ok=True)
        src_users.mkdir(parents=True, exist_ok=True)

        (src_orders / "orders.controller.ts").write_text("// orders", encoding="utf-8")
        (src_users / "users.controller.ts").write_text("// users", encoding="utf-8")

        run_init(self.test_dir, harness="all")
        run_bootstrap(self.test_dir)

        # Inicialmente orders y users están pendientes en docs/functional/index.md
        idx_initial = (self.test_dir / "docs" / "functional" / "index.md").read_text(encoding="utf-8")
        self.assertIn("`orders`", idx_initial)
        self.assertIn("`users`", idx_initial)

        # Simular levantamiento As-Is de orders: UC-ORDERS-001 con status: "As-Is (Brownfield)"
        uc_orders = (
            "---\n"
            "id: UC-ORDERS-001\n"
            "title: Crear orden de compra\n"
            "domain: orders\n"
            "actor: Cliente\n"
            "status: As-Is (Brownfield)\n"
            "trigger: HTTP POST /orders\n"
            "---\n\n"
            "# Caso de Uso As-Is: Crear orden de compra\n\n"
            "```mermaid\n"
            "flowchart TD\n"
            "  A[Cliente] --> B[Crear Orden]\n"
            "```\n\n"
            "## 1. Entradas y Salidas\n"
            "### Entradas\n"
            "| Campo | Tipo | Requerido | Validación |\n"
            "| :--- | :--- | :--- | :--- |\n"
            "| `items` | array | Sí | No vacío |\n\n"
            "### Salidas\n"
            "| Campo | Tipo | Descripción |\n"
            "| :--- | :--- | :--- |\n"
            "| `orderId` | string | ID de orden |\n\n"
            "## 2. Reglas de Negocio\n"
            "| ID | Regla | Descripción |\n"
            "| :--- | :--- | :--- |\n"
            "| `BR-01` | Validación de ítems | Debe contener al menos un producto |\n"
        )
        uc_file = self.test_dir / "docs" / "functional" / "use-cases" / "UC-ORDERS-001-create-order.md"
        uc_file.write_text(uc_orders, encoding="utf-8")

        run_sync_index(self.test_dir)
        idx_updated = (self.test_dir / "docs" / "functional" / "index.md").read_text(encoding="utf-8")

        # orders se graduó al catálogo principal de casos de uso y ya NO está en Módulos Legados
        self.assertIn("| `UC-ORDERS-001` | `orders` |", idx_updated)
        self.assertIn("As-Is (Brownfield)", idx_updated)
        # users sigue como legado detectado
        self.assertIn("| `users` | Detectado en código |", idx_updated)

        # Simular registro de una propuesta de deuda técnica en audit-proposals.md
        audit_file = self.test_dir / "docs" / "backlog" / "audit-proposals.md"
        proposal = (
            "\n### [AUDIT-ORDERS-001] Falta de idempotencia en creación de ordenes\n"
            "- **Dominio:** `orders`\n"
            "- **Categoría:** Concurrencia\n"
            "- **Severidad Sugerida:** P1\n"
            "- **Impacto Estimado:** PATCH\n"
            "- **Evidencia en Código:** `src/orders/orders.controller.ts:15`\n"
            "- **Estado:** Propuesto\n\n"
            "#### Descripción del Hallazgo:\n"
            "Doble cobro si el cliente reintenta la petición.\n"
        )
        audit_file.write_text(audit_file.read_text(encoding="utf-8") + proposal, encoding="utf-8")

        # Check pasa (audit-proposals no ensucia pending.md)
        self.assertTrue(run_check(self.test_dir))

        # Promover la propuesta a requerimiento formal
        req_id = run_new_req(self.test_dir, from_audit="AUDIT-ORDERS-001")
        self.assertEqual(req_id, "REQ-ORDERS-001")

        pending_text = (self.test_dir / "docs" / "backlog" / "pending.md").read_text(encoding="utf-8")
        self.assertIn("[REQ-ORDERS-001] Falta de idempotencia en creación de ordenes", pending_text)
        self.assertIn("`src/orders/orders.controller.ts` [MODIFY]", pending_text)

        audit_after = audit_file.read_text(encoding="utf-8")
        self.assertIn("- **Estado:** Promovido a REQ-ORDERS-001", audit_after)

    def test_multi_harness_skills_distribution(self):
        """Verifica que spec-grill se instale en Claude, Cursor y Windsurf pero NO en Antigravity (que conserva /grill-me nativo)."""
        run_init(self.test_dir, harness="all")

        # Antigravity: backend-spec y backend-spec-bootstrap, pero NO spec-grill
        gemini_skills = self.test_dir / ".gemini" / "skills"
        self.assertTrue((gemini_skills / "backend-spec" / "SKILL.md").exists())
        self.assertTrue((gemini_skills / "backend-spec-bootstrap" / "SKILL.md").exists())
        self.assertFalse((gemini_skills / "spec-grill").exists())

        # Claude: skills (backend-spec, backend-spec-bootstrap, spec-grill con AskUserQuestion) + commands
        claude_skills = self.test_dir / ".claude" / "skills"
        self.assertTrue((claude_skills / "spec-grill" / "SKILL.md").exists())
        self.assertTrue((claude_skills / "backend-spec-bootstrap" / "SKILL.md").exists())
        self.assertTrue((self.test_dir / ".claude" / "commands" / "spec-grill.md").exists())
        claude_grill_skill = (claude_skills / "spec-grill" / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("AskUserQuestion", claude_grill_skill)

        # Cursor: skills + commands (con AskQuestion)
        cursor_skills = self.test_dir / ".cursor" / "skills"
        self.assertTrue((cursor_skills / "spec-grill" / "SKILL.md").exists())
        self.assertTrue((cursor_skills / "backend-spec-bootstrap" / "SKILL.md").exists())
        self.assertTrue((self.test_dir / ".cursor" / "commands" / "spec-grill.md").exists())
        cursor_grill_skill = (cursor_skills / "spec-grill" / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("AskQuestion", cursor_grill_skill)

        # Windsurf: skills + workflows (con pausa A/B/C)
        windsurf_skills = self.test_dir / ".windsurf" / "skills"
        self.assertTrue((windsurf_skills / "spec-grill" / "SKILL.md").exists())
        self.assertTrue((windsurf_skills / "backend-spec-bootstrap" / "SKILL.md").exists())
        self.assertTrue((self.test_dir / ".windsurf" / "workflows" / "spec-grill.md").exists())
        windsurf_grill_skill = (windsurf_skills / "spec-grill" / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("Pausa Estructurada en Chat", windsurf_grill_skill)


if __name__ == "__main__":
    unittest.main()
