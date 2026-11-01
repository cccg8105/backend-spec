import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

cli_dir = Path(__file__).resolve().parent.parent
if str(cli_dir) not in sys.path:
    sys.path.insert(0, str(cli_dir))

from backend_spec.commands.check_cmd import run_check
from backend_spec.commands.init_cmd import run_init
from backend_spec.commands.new_req_cmd import run_new_req
from backend_spec.commands.resolve_cmd import run_resolve
from backend_spec.commands.sync_index_cmd import run_sync_index


class TestCLIWorkflow(unittest.TestCase):
    def setUp(self):
        self.test_dir = Path(tempfile.mkdtemp())
        (self.test_dir / "package.json").write_text(
            '{\n  "name": "test-api",\n  "version": "1.0.0"\n}\n', encoding="utf-8"
        )
        (self.test_dir / ".git").mkdir()

    def tearDown(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_complete_v1_workflow(self):
        # 1. Init limpio
        run_init(self.test_dir, harness="all", versioning="semver")
        self.assertTrue((self.test_dir / ".spec" / "config.yaml").exists())
        self.assertTrue((self.test_dir / ".spec" / "templates" / "_template_use_case.md").exists())
        self.assertTrue((self.test_dir / ".spec" / "templates" / "_template_api_contracts.md").exists())
        self.assertTrue((self.test_dir / ".spec" / "templates" / "ocl-guidelines.md").exists())

        for tech_doc in (
            "database-model.md",
            "component-design.md",
            "api-contracts.md",
            "tech-stack.md",
            "deployment-strategy.md",
        ):
            self.assertTrue((self.test_dir / "docs" / "technical" / tech_doc).exists())

        # Sin requerimientos ficticios al inicializar
        pending_initial = (self.test_dir / "docs" / "backlog" / "pending.md").read_text(encoding="utf-8")
        self.assertNotIn("REQ-AUTH-001", pending_initial)

        # Comandos multi-harness incluidos
        self.assertTrue((self.test_dir / ".cursor" / "commands" / "spec-bootstrap.md").exists())
        self.assertTrue((self.test_dir / ".claude" / "commands" / "spec-bootstrap.md").exists())
        self.assertTrue((self.test_dir / ".windsurf" / "workflows" / "spec-bootstrap.md").exists())
        self.assertTrue((self.test_dir / ".git" / "hooks" / "pre-commit").exists())

        # 2. Check inicial en verde
        self.assertTrue(run_check(self.test_dir))

        # 3. Crear requerimiento Fast-Track (PATCH) y verificar sincronización real en disco
        req1 = run_new_req(
            self.test_dir,
            domain="auth",
            title="Fix token clock skew",
            priority="P1",
            impact="PATCH",
        )
        self.assertEqual(req1, "REQ-AUTH-001")
        backlog_idx = (self.test_dir / "docs" / "backlog" / "index.md").read_text(encoding="utf-8")
        self.assertIn("`REQ-AUTH-001`", backlog_idx)
        self.assertTrue(run_check(self.test_dir))

        # 4. Resolver SIN auto_bump: package.json debe permanecer en 1.0.0 y sin duplicar cabecera
        self.assertTrue(run_resolve(self.test_dir, "REQ-AUTH-001", auto_bump=False))
        pkg_after_no_bump = json.loads((self.test_dir / "package.json").read_text(encoding="utf-8"))
        self.assertEqual(pkg_after_no_bump["version"], "1.0.0")

        changelog = (self.test_dir / "docs" / "backlog" / "changelog.md").read_text(encoding="utf-8")
        self.assertEqual(changelog.count("[REQ-AUTH-001]"), 1)

        # 5. Nuevo requerimiento en el mismo dominio no debe reutilizar REQ-AUTH-001
        req2 = run_new_req(
            self.test_dir,
            domain="auth",
            title="Fix refresh token rotation",
            priority="P2",
            impact="PATCH",
        )
        self.assertEqual(req2, "REQ-AUTH-002")

        # 6. Resolver CON auto_bump hacia milestone v1.1.0 actualiza package.json a 1.1.0
        self.assertTrue(run_resolve(self.test_dir, "REQ-AUTH-002", auto_bump=True))
        pkg_after_bump = json.loads((self.test_dir / "package.json").read_text(encoding="utf-8"))
        self.assertEqual(pkg_after_bump["version"], "1.1.0")

        reqs_count, _ = run_sync_index(self.test_dir)
        self.assertEqual(reqs_count, 0)


if __name__ == "__main__":
    unittest.main()
