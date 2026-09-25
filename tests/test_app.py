import unittest

from app import build_selection, choose_carrier


class AppTests(unittest.TestCase):
    def test_build_selection_uses_months_days_and_carrier(self):
        selection = build_selection({"2026"}, {"EYLÜL", "EKİM"}, {"2"}, "AGENA LOJ. (5 araç)")
        self.assertEqual(selection.years, {2026})
        self.assertEqual(selection.months, {"EYLÜL", "EKİM"})
        self.assertEqual(selection.days, {2})
        self.assertEqual(selection.carrier, "AGENA LOJ.")

    def test_choose_carrier_rejects_multiple_carriers(self):
        with self.assertRaises(ValueError):
            choose_carrier({"AGENA LOJ. (5 araç)", "ALIŞAN LOJ. (3 araç)"})
