"""Exercise the actual add-a-unit workflow without touching the real catalog."""
import importlib.util
import json
from pathlib import Path
import shutil
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("lab", ROOT / "scripts/lab.py")
lab = importlib.util.module_from_spec(spec)
spec.loader.exec_module(lab)


class LabWorkflow(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        (self.root / "visualizations").mkdir()
        shutil.copytree(ROOT / "templates", self.root / "templates")

    def test_each_kind_uses_only_its_selected_outputs(self):
        expected = {"static": {"figure.svg"}, "interactive": {"interactive.html"}, "both": set(lab.OUTPUTS)}
        for kind, outputs in expected.items():
            unit = lab.create_unit(self.root, "sample-" + kind, "一个问题", kind, 2)
            self.assertEqual({name for name in lab.OUTPUTS if (unit / name).exists()}, outputs)
            readme = (unit / "README.md").read_text(encoding="utf-8")
            self.assertNotIn("{{", readme)
            for name in lab.OUTPUTS:
                self.assertEqual(f"]({name})" in readme, name in outputs)
        self.assertEqual(len(lab.units(self.root)), 3)

    def test_new_unit_is_discovered_and_index_is_deterministic(self):
        unit = lab.create_unit(self.root, "a-question", "测试几何关系", "static", 3)
        metadata = json.loads((unit / "unit.json").read_text(encoding="utf-8"))
        self.assertEqual(metadata["status"], "draft")
        index = (self.root / "index.html").read_text(encoding="utf-8")
        self.assertIn("测试几何关系", index)
        self.assertIn("visualizations/a-question/figure.svg", index)
        self.assertIn("3D", index)
        self.assertIn("草稿", index)
        lab.build_index(self.root)
        self.assertEqual(index, (self.root / "index.html").read_text(encoding="utf-8"))

    def test_rejects_path_traversal_and_existing_unit_without_changes(self):
        for name in ("../escape", "Bad_Name", "double--dash", "a/b"):
            with self.assertRaises(ValueError):
                lab.create_unit(self.root, name, "title", "both", 2)
        unit = lab.create_unit(self.root, "keep", "original", "static", 2)
        before = (unit / "unit.json").read_bytes()
        with self.assertRaises(ValueError):
            lab.create_unit(self.root, "keep", "replacement", "both", 2)
        self.assertEqual(before, (unit / "unit.json").read_bytes())

    def test_index_and_scaffold_escape_authored_text(self):
        title = '<script>alert("x")</script> & geometry'
        unit = lab.create_unit(self.root, "safe-text", title, "interactive", 2)
        for target in (unit / "interactive.html", self.root / "index.html"):
            text = target.read_text(encoding="utf-8")
            self.assertNotIn(title, text)
            self.assertIn("&lt;script&gt;", text)
        self.assertEqual(lab.units(self.root)[0][1]["title"], title)

    def test_missing_output_and_missing_readme_section_fail(self):
        unit = lab.create_unit(self.root, "incomplete", "title", "static", 2)
        (unit / "figure.svg").unlink()
        with self.assertRaisesRegex(ValueError, "至少需要"):
            lab.units(self.root)
        shutil.copyfile(self.root / "templates/unit/figure.svg", unit / "figure.svg")
        (unit / "README.md").write_text("## Topic\nOnly a topic", encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "Mathematical Insight"):
            lab.units(self.root)

    def test_invalid_metadata_fails_with_unit_name(self):
        unit = lab.create_unit(self.root, "bad-data", "title", "static", 2)
        for key, value in (("dimension", True), ("status", "published"), ("reference", {})):
            data = {"title": "title", "dimension": 2, "status": "draft"}
            data[key] = value
            (unit / "unit.json").write_text(json.dumps(data), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "bad-data"):
                lab.units(self.root)


if __name__ == "__main__":
    unittest.main()
