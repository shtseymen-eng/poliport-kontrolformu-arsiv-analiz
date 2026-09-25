import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from src.archive_indexer import discover_archive, select_forms


class ArchiveIndexerTests(unittest.TestCase):
    def test_select_forms_accepts_multiple_months_and_one_carrier(self):
        with TemporaryDirectory() as temp:
            root = Path(temp)
            for month, day, carrier, name in [
                ("EYLÜL", "2", "AGENA LOJ.", "a.xlsx"),
                ("EKİM", "3", "AGENA LOJ.", "b.xlsx"),
                ("EKİM", "3", "ALİŞAN LOJ.", "c.xlsx"),
            ]:
                path = root / "2026" / month / day / carrier / "Kontrol Formları" / name
                path.parent.mkdir(parents=True, exist_ok=True)
                path.touch()
            catalog = discover_archive(root)
            selected = select_forms(catalog, {2026}, {"EYLÜL", "EKİM"}, set(), "AGENA LOJ.")
            self.assertEqual([item.path.name for item in selected], ["a.xlsx", "b.xlsx"])
