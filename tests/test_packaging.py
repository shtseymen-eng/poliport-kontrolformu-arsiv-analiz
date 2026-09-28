import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class PackagingTests(unittest.TestCase):
    def test_mac_builder_creates_a_windowed_app_bundle(self):
        script = ROOT / "MAC_APP_OLUSTUR.command"
        self.assertTrue(script.exists())
        content = script.read_text(encoding="utf-8")
        self.assertIn("PyInstaller", content)
        self.assertIn("--windowed", content)
        self.assertIn("SEYMEN_Kontrol_Formu_Arsiv_Analizi", content)

    def test_github_workflow_builds_macos_app(self):
        workflow = ROOT / ".github" / "workflows" / "build-macos-app.yml"
        self.assertTrue(workflow.exists())
        content = workflow.read_text(encoding="utf-8")
        self.assertIn("macos-latest", content)
        self.assertIn("PyInstaller", content)
        self.assertIn("upload-artifact", content)
