import unittest

from src.question_catalog import default_catalog


class QuestionCatalogTests(unittest.TestCase):
    def test_keeps_unknown_dated_questions_separate(self):
        catalog = default_catalog()
        self.assertNotEqual(
            catalog.short_name("Belge A geçerlilik tarihi"),
            catalog.short_name("Belge B geçerlilik tarihi"),
        )
