import unittest
from datetime import date, datetime

from src.aggregator import summarize
from src.models import AssetType, ValidityRecord


def record(validity: date, control: date) -> ValidityRecord:
    return ValidityRecord("AGENA LOJ.", AssetType.TRACTOR, "34ABC123", "Sigorta sorusu", "Trafik Sigortası", validity, control, "form.xlsx")


class AggregatorTests(unittest.TestCase):
    def test_summary_uses_latest_form_per_asset_question(self):
        result = summarize([
            record(date(2027, 1, 1), date(2026, 9, 1)),
            record(date(2027, 4, 18), date(2026, 9, 25)),
        ], date(2026, 9, 25))
        summary = result.by_type[AssetType.TRACTOR][0]
        self.assertEqual(summary.document_dates["Trafik Sigortası"], date(2027, 4, 18))
        self.assertEqual(summary.arrival_count, 2)

    def test_renewed_document_does_not_remain_critical(self):
        result = summarize([
            record(date(2026, 9, 1), date(2026, 9, 1)),
            record(date(2027, 9, 1), date(2026, 9, 25)),
        ], date(2026, 9, 25))
        self.assertEqual(result.critical, [])

    def test_uses_later_timestamp_for_same_day_form(self):
        old = record(date(2026, 9, 30), date(2026, 9, 25))
        new = record(date(2027, 9, 30), date(2026, 9, 25))
        old = ValidityRecord(**{**old.__dict__, "control_at": datetime(2026, 9, 25, 9, 0)})
        new = ValidityRecord(**{**new.__dict__, "control_at": datetime(2026, 9, 25, 16, 12)})
        result = summarize([old, new], date(2026, 9, 25))
        summary = result.by_type[AssetType.TRACTOR][0]
        self.assertEqual(summary.document_dates["Trafik Sigortası"], date(2027, 9, 30))
