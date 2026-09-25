import unittest
from datetime import datetime
from pathlib import Path
from tempfile import TemporaryDirectory

from openpyxl import Workbook

from src.form_reader import read_form
from src.models import ArchiveFile, AssetType
from src.question_catalog import default_catalog


class FormReaderTests(unittest.TestCase):
    def test_reader_finds_headers_and_only_dated_questions(self):
        with TemporaryDirectory() as temp:
            path = Path(temp) / "form.xlsx"
            book = Workbook()
            sheet = book.active
            sheet.append(["Başlık"])
            sheet.append([])
            sheet.append(["Sorumlu", "Soru", "Cevap", "Geçerlilik Tarihi", "Tarih"])
            sheet.append(["34ABC123", "Zorunlu trafik sigortası mevcut mu?", "Evet", "18.04.2027", "25.09.2026 13:05"])
            sheet.append(["34ABC123", "Lastikler sağlam mı?", "Evet", "", "25.09.2026 13:05"])
            book.save(path)
            archive = ArchiveFile(path, 2026, "EYLÜL", 25, "AGENA LOJ.")
            records, unreadable = read_form(archive, default_catalog())
            self.assertEqual(unreadable, [])
            self.assertEqual(len(records), 1)
            self.assertEqual(records[0].asset_type, AssetType.TRACTOR)
            self.assertEqual(records[0].short_name, "Trafik Sigortası")
            self.assertEqual(records[0].control_at, datetime(2026, 9, 25, 13, 5))

    def test_reader_keeps_seconds_in_control_timestamp(self):
        with TemporaryDirectory() as temp:
            path = Path(temp) / "form.xlsx"
            book = Workbook()
            sheet = book.active
            sheet.append(["Sorumlu", "Soru", "Cevap", "Geçerlilik Tarihi", "Tarih"])
            sheet.append(["34ABC123", "Zorunlu trafik sigortası mevcut mu?", "Evet", "18.04.2027", "25.09.2026 13:05:44"])
            book.save(path)
            archive = ArchiveFile(path, 2026, "EYLÜL", 25, "AGENA LOJ.")
            records, _ = read_form(archive, default_catalog())
            self.assertEqual(records[0].control_at, datetime(2026, 9, 25, 13, 5, 44))
