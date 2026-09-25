import unittest
from datetime import date

from src.models import AssetType, ValidityRecord


class ModelTests(unittest.TestCase):
    def test_validity_record_keeps_asset_identity_and_date(self):
        record = ValidityRecord(
            carrier="AGENA LOJ.", asset_type=AssetType.TRACTOR,
            asset_id="34ABC123", question="Zorunlu trafik sigortası mevcut mu?",
            short_name="Trafik Sigortası", validity_date=date(2027, 4, 18),
            control_date=date(2026, 9, 25), source_path="form.xlsx",
        )
        self.assertIs(record.asset_type, AssetType.TRACTOR)
        self.assertEqual(record.validity_date, date(2027, 4, 18))
