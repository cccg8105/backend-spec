import shutil
import sys
import tempfile
import unittest
from pathlib import Path

cli_dir = Path(__file__).resolve().parent.parent
if str(cli_dir) not in sys.path:
    sys.path.insert(0, str(cli_dir))

from backend_spec.detector.ecosystem_detector import detect_ecosystem


class TestEcosystemDetector(unittest.TestCase):
    def setUp(self):
        self.test_dir = Path(tempfile.mkdtemp())

    def tearDown(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_greenfield_detection(self):
        result = detect_ecosystem(self.test_dir)
        self.assertEqual(result["mode"], "greenfield")
        self.assertIsNone(result["detected"])

    def test_brownfield_node_detection(self):
        (self.test_dir / "package.json").write_text(
            '{"name": "test", "version": "1.0.0"}', encoding="utf-8"
        )
        result = detect_ecosystem(self.test_dir)
        self.assertEqual(result["mode"], "brownfield")
        self.assertEqual(result["detected"]["ecosystem"], "node")
        self.assertEqual(result["detected"]["src_ext"], ".ts")

    def test_brownfield_python_detection(self):
        (self.test_dir / "pyproject.toml").write_text(
            '[project]\nversion = "2.1.0"', encoding="utf-8"
        )
        result = detect_ecosystem(self.test_dir)
        self.assertEqual(result["mode"], "brownfield")
        self.assertEqual(result["detected"]["ecosystem"], "python")
        self.assertEqual(result["detected"]["src_ext"], ".py")

    def test_brownfield_go_uses_version_file(self):
        (self.test_dir / "go.mod").write_text(
            "module github.com/acme/payments\n\ngo 1.22\n", encoding="utf-8"
        )
        result = detect_ecosystem(self.test_dir)
        self.assertEqual(result["mode"], "brownfield")
        self.assertEqual(result["detected"]["ecosystem"], "go")
        self.assertEqual(result["detected"]["version_file"], "VERSION")
        self.assertEqual(result["detected"]["format"], "plain")


if __name__ == "__main__":
    unittest.main()
