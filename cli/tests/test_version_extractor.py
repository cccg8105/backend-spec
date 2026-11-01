import shutil
import sys
import tempfile
import unittest
from pathlib import Path

cli_dir = Path(__file__).resolve().parent.parent
if str(cli_dir) not in sys.path:
    sys.path.insert(0, str(cli_dir))

from backend_spec.detector.version_extractor import (
    compare_versions,
    compute_next_milestone,
    extract_version,
    update_version,
)


class TestVersionExtractor(unittest.TestCase):
    def setUp(self):
        self.test_dir = Path(tempfile.mkdtemp())

    def tearDown(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_json_version(self):
        pkg = self.test_dir / "package.json"
        pkg.write_text('{\n  "name": "app",\n  "version": "1.2.3"\n}\n', encoding="utf-8")
        self.assertEqual(extract_version(pkg, "json"), "1.2.3")
        self.assertTrue(update_version(pkg, "json", "1.3.0"))
        self.assertEqual(extract_version(pkg, "json"), "1.3.0")

    def test_toml_version(self):
        toml = self.test_dir / "pyproject.toml"
        toml.write_text('[project]\nname = "app"\nversion = "0.5.1"\n', encoding="utf-8")
        self.assertEqual(extract_version(toml, "toml"), "0.5.1")
        self.assertTrue(update_version(toml, "toml", "0.6.0"))
        self.assertEqual(extract_version(toml, "toml"), "0.6.0")

    def test_xml_version_ignores_parent_block(self):
        pom = self.test_dir / "pom.xml"
        pom.write_text(
            "<project><parent><version>3.2.0</version></parent><version>1.4.2</version></project>",
            encoding="utf-8",
        )
        self.assertEqual(extract_version(pom, "xml"), "1.4.2")
        self.assertTrue(update_version(pom, "xml", "1.5.0"))

    def test_plain_version_and_comparisons(self):
        ver_file = self.test_dir / "VERSION"
        self.assertTrue(update_version(ver_file, "plain", "v2.1.0"))
        self.assertEqual(extract_version(ver_file, "plain"), "2.1.0")

        self.assertEqual(compare_versions("1.1.0", "1.0.0"), 1)
        self.assertEqual(compare_versions("v1.0.0", "1.0.0"), 0)
        self.assertEqual(compare_versions("0.2.0", "1.0.0"), -1)
        self.assertEqual(compute_next_milestone("1.0.0", "semver"), "v1.1.0")
        self.assertEqual(compute_next_milestone("4", "sequential"), "v5")


if __name__ == "__main__":
    unittest.main()
