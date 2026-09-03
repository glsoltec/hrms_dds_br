import json
import os
import tomllib
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MOD = os.path.join(ROOT, "hrms_dds_br", "hrms_dds_br")


def read_json(rel):
    with open(os.path.join(MOD, rel), encoding="utf-8") as fh:
        return json.load(fh)


class TestDDSWorkflow(unittest.TestCase):
    def setUp(self):
        self.workflow = read_json(
            os.path.join("workflow", "dds", "dds.json")
        )

    def test_submit_allows_responsavel_dds(self):
        actions = [
            (t["state"], t["action"], t["allowed"])
            for t in self.workflow["transitions"]
        ]
        self.assertIn(
            ("Rascunho", "Enviar", "Responsavel DDS"),
            actions,
        )


class TestSignatureFieldLevels(unittest.TestCase):
    def test_dds_signature_fields_have_permlevel(self):
        dds = read_json(os.path.join("doctype", "dds", "dds.json"))
        fields = {f["fieldname"]: f for f in dds["fields"]}
        for name in (
            "responsible_signature",
            "responsible_signature_hash",
            "responsible_signature_collected_by",
            "responsible_signature_collected_at",
            "photo",
        ):
            self.assertEqual(fields[name].get("permlevel"), 1, name)

    def test_participant_signature_fields_have_permlevel(self):
        child = read_json(
            os.path.join("doctype", "dds_participante", "dds_participante.json")
        )
        fields = {f["fieldname"]: f for f in child["fields"]}
        for name in ("signature", "signature_hash", "signature_collected_by", "signature_collected_at"):
            self.assertEqual(fields[name].get("permlevel"), 1, name)

    def test_level1_perm_for_privileged_roles(self):
        dds = read_json(os.path.join("doctype", "dds", "dds.json"))
        level1 = {
            p["role"] for p in dds["permissions"] if p.get("permlevel") == 1
        }
        self.assertTrue(
            {"System Manager", "Safety Manager", "Responsavel DDS"}.issubset(level1)
        )


class TestPackaging(unittest.TestCase):
    def test_pyproject_metadata(self):
        with open(os.path.join(ROOT, "pyproject.toml"), "rb") as fh:
            data = tomllib.load(fh)
        project = data["project"]
        self.assertEqual(project["name"], "hrms_dds_br")
        self.assertEqual(project["license"]["file"], "license.txt")
        self.assertEqual(project["requires-python"], ">=3.10,<3.15")

    def test_required_apps(self):
        hooks_path = os.path.join(ROOT, "hrms_dds_br", "hooks.py")
        with open(hooks_path, encoding="utf-8") as fh:
            hooks = fh.read()
        self.assertIn('required_apps = ["erpnext", "hrms"]', hooks)


if __name__ == "__main__":
    unittest.main()
