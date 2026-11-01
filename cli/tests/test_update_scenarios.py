import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

cli_dir = Path(__file__).resolve().parent.parent
if str(cli_dir) not in sys.path:
    sys.path.insert(0, str(cli_dir))

from backend_spec.commands.check_cmd import run_check
from backend_spec.commands.init_cmd import run_init
from backend_spec.commands.update_cmd import run_update


class TestUpdateScenarios(unittest.TestCase):
    def setUp(self):
        self.test_dir = Path(tempfile.mkdtemp())
        # Mock package.json y .git
        (self.test_dir / "package.json").write_text(
            '{\n  "name": "update-test-api",\n  "version": "1.0.0"\n}\n', encoding="utf-8"
        )
        (self.test_dir / ".git").mkdir()

    def tearDown(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_scenario_1_standard_update_protects_docs(self):
        """Escenario 1: Actualizar framework no modifica ni sobrescribe jamás docs/ viva."""
        run_init(self.test_dir, harness="antigravity")

        db_model = self.test_dir / "docs" / "technical" / "database-model.md"
        custom_user_doc = (
            "---\nartifact_type: database-model\n---\n"
            "# Mi Modelo de Base de Datos Real\n\n"
            "```mermaid\nerDiagram\n  CUSTOM_USER_TABLE {\n    uuid id PK\n  }\n```\n"
        )
        db_model.write_text(custom_user_doc, encoding="utf-8")

        pending_file = self.test_dir / "docs" / "backlog" / "pending.md"
        custom_pending = (
            "# Backlog Vivo con Tareas Reales\n\n"
            "### [REQ-CUSTOM-001] Tarea de usuario\n"
            "- **Prioridad:** P2\n"
            "- **Tipo:** Hotfix / Fix (PATCH - Fast-Track)\n"
            "- **Versión Objetivo:** `v1.0.0`\n"
            "- **Referencia Funcional:** `N/A (PATCH / Fast-Track)`\n"
            "- **Referencia Técnica:** `docs/technical/component-design.md`\n\n"
            "#### Fronteras y Artefactos:\n"
            "- **Artefactos a Modificar / Crear:**\n"
            "  - `src/custom.ts` [NEW]\n"
            "- **Restricciones:**\n"
            "  - Ninguna\n\n"
            "#### Criterios de Aceptación:\n"
            "- [ ] Completar tarea\n"
        )
        pending_file.write_text(custom_pending, encoding="utf-8")

        # Corromper o desactualizar una plantilla en .spec/templates/
        uc_tmpl = self.test_dir / ".spec" / "templates" / "_template_use_case.md"
        uc_tmpl.write_text("# Plantilla vieja desactualizada\n", encoding="utf-8")

        # Ejecutar update
        ok = run_update(self.test_dir)
        self.assertTrue(ok)

        # La plantilla en .spec/templates/ se refrescó con la última versión del framework
        self.assertIn("UC-[DOMINIO]-[ID]", uc_tmpl.read_text(encoding="utf-8"))

        # Pero los documentos vivos en docs/ se mantuvieron 100% idénticos
        self.assertEqual(db_model.read_text(encoding="utf-8"), custom_user_doc)
        self.assertEqual(pending_file.read_text(encoding="utf-8"), custom_pending)

    def test_scenario_2_legacy_v0_migration(self):
        """Escenario 2: Migrar proyecto legado v0.x eliminando _template_* de docs/ y añadiendo api-contracts.md."""
        docs_dir = self.test_dir / "docs"
        tech_dir = docs_dir / "technical"
        func_dir = docs_dir / "functional"
        backlog_dir = docs_dir / "backlog"

        tech_dir.mkdir(parents=True, exist_ok=True)
        func_dir.mkdir(parents=True, exist_ok=True)
        backlog_dir.mkdir(parents=True, exist_ok=True)

        # Archivos legados v0.x dentro de docs/
        (tech_dir / "_template_database.md").write_text("# legacy template\n", encoding="utf-8")
        (func_dir / "ocl-guidelines.md").write_text("# legacy ocl\n", encoding="utf-8")
        (tech_dir / "database-model.md").write_text(
            "---\nartifact_type: database-model\n---\n# DB\n", encoding="utf-8"
        )
        (tech_dir / "component-design.md").write_text(
            "---\nartifact_type: component-design\n---\n# Components\n", encoding="utf-8"
        )
        (tech_dir / "tech-stack.md").write_text(
            "---\nartifact_type: tech-stack\n---\n# Tech Stack\n", encoding="utf-8"
        )
        (tech_dir / "deployment-strategy.md").write_text(
            "---\nartifact_type: deployment-strategy\n---\n# Deployment\n", encoding="utf-8"
        )
        (tech_dir / "index.md").write_text(
            "# Indice Tecnico\n\n| Artefacto | Archivo |\n| :--- | :--- |\n| Modelo | [database-model.md](./database-model.md) |\n",
            encoding="utf-8",
        )
        (func_dir / "index.md").write_text("# Indice Funcional\n", encoding="utf-8")
        (backlog_dir / "pending.md").write_text("# Pending\n", encoding="utf-8")
        (backlog_dir / "index.md").write_text("# Backlog Index\n", encoding="utf-8")
        (backlog_dir / "changelog.md").write_text("# Changelog\n", encoding="utf-8")

        spec_dir = self.test_dir / ".spec"
        spec_dir.mkdir(parents=True, exist_ok=True)
        (spec_dir / "config.yaml").write_text(
            'version: "0.1.0"\nproject_name: "legacy-app"\ncurrent_version: "1.0.0"\npaths:\n  backlog: "docs/backlog"\n',
            encoding="utf-8",
        )

        ok = run_update(self.test_dir)
        self.assertTrue(ok)

        # Plantillas legadas eliminadas de docs/
        self.assertFalse((tech_dir / "_template_database.md").exists())
        self.assertFalse((func_dir / "ocl-guidelines.md").exists())

        # Nuevo pilar api-contracts.md creado
        self.assertTrue((tech_dir / "api-contracts.md").exists())
        self.assertIn("api-contracts.md", (tech_dir / "index.md").read_text(encoding="utf-8"))

        # Blueprints creados en .spec/templates/
        self.assertTrue((spec_dir / "templates" / "_template_use_case.md").exists())
        self.assertTrue((spec_dir / "templates" / "ocl-guidelines.md").exists())

        # Config actualizado a version: "1.1.0"
        cfg = (spec_dir / "config.yaml").read_text(encoding="utf-8")
        self.assertIn('version: "1.1.0"', cfg)
        self.assertIn('templates: ".spec/templates"', cfg)

        # Buzón audit-proposals.md creado en docs/backlog/
        self.assertTrue((self.test_dir / "docs" / "backlog" / "audit-proposals.md").exists())

        self.assertTrue(run_check(self.test_dir))

    def test_scenario_3_custom_user_rules_and_graphifyignore_preserved(self):
        """Escenario 3: Preservar reglas propias en CLAUDE.md y patrones en .graphifyignore."""
        run_init(self.test_dir, harness="claude")

        claude_file = self.test_dir / "CLAUDE.md"
        claude_initial = claude_file.read_text(encoding="utf-8")
        user_custom_rule = (
            "\n\n# Directivas Propias del Proyecto\n"
            "- Prohibido hacer commits directos a main sin PR previo.\n"
            "- Todos los logs deben usar prefijo [PAYMENT-CORE].\n"
        )
        claude_file.write_text(claude_initial + user_custom_rule, encoding="utf-8")

        graphify_file = self.test_dir / ".graphifyignore"
        user_ignore_pattern = "\n# Ignorar carpeta secreta de tokens\nsecret-tokens-vault/\n"
        graphify_file.write_text(graphify_file.read_text(encoding="utf-8") + user_ignore_pattern, encoding="utf-8")

        ok = run_update(self.test_dir)
        self.assertTrue(ok)

        # Verificar que el bloque gestionado de backend-spec existe
        claude_updated = claude_file.read_text(encoding="utf-8")
        self.assertIn("<!-- BACKEND-SPEC:START -->", claude_updated)
        self.assertIn("<!-- BACKEND-SPEC:END -->", claude_updated)

        # Y que las reglas propias del usuario se conservaron intactas
        self.assertIn("Directivas Propias del Proyecto", claude_updated)
        self.assertIn("secret-tokens-vault/", graphify_file.read_text(encoding="utf-8"))

    def test_scenario_4_selective_harness_autodetection_and_expansion(self):
        """Escenario 4: Auto-detectar solo los harnesses existentes y permitir expandir con --harness."""
        run_init(self.test_dir, harness="claude")
        self.assertTrue((self.test_dir / "CLAUDE.md").exists())
        self.assertFalse((self.test_dir / ".cursor").exists())

        # Update sin banderas -> solo actualiza claude, no crea cursor
        ok = run_update(self.test_dir)
        self.assertTrue(ok)
        self.assertFalse((self.test_dir / ".cursor").exists())

        # Update con --harness cursor -> añade Cursor al proyecto
        ok2 = run_update(self.test_dir, harness="cursor")
        self.assertTrue(ok2)
        self.assertTrue((self.test_dir / ".cursor" / "rules" / "backend-spec.mdc").exists())
        self.assertTrue((self.test_dir / ".cursor" / "commands" / "spec-plan.md").exists())

    def test_scenario_5_dry_run_makes_zero_disk_changes(self):
        """Escenario 5: Modo --dry-run previsualiza sin modificar ningún archivo en disco."""
        run_init(self.test_dir, harness="windsurf")
        bp_file = self.test_dir / ".spec" / "templates" / "_template_use_case.md"
        bp_file.unlink()
        self.assertFalse(bp_file.exists())

        ok = run_update(self.test_dir, dry_run=True)
        self.assertTrue(ok)

        # En dry-run el archivo borrado no debe ser recreado físicamente
        self.assertFalse(bp_file.exists())

    def test_scenario_6_foreign_pre_commit_hook_preserved(self):
        """Escenario 6: Si existe un hook pre-commit de otra herramienta, inyectar el bloque sin destruirlo."""
        hook_path = self.test_dir / ".git" / "hooks" / "pre-commit"
        hook_path.parent.mkdir(parents=True, exist_ok=True)
        foreign_hook = "#!/bin/sh\n\necho 'Ejecutando ESLint pre-commit'\nnpm run lint\nexit 0\n"
        hook_path.write_text(foreign_hook, encoding="utf-8")

        run_init(self.test_dir, harness="antigravity")
        ok = run_update(self.test_dir)
        self.assertTrue(ok)

        updated_hook = hook_path.read_text(encoding="utf-8")
        # Ambos deben coexistir
        self.assertIn("npm run lint", updated_hook)
        self.assertIn("# BACKEND-SPEC:START", updated_hook)
        self.assertIn("backend-spec check --staged", updated_hook)


if __name__ == "__main__":
    unittest.main()
