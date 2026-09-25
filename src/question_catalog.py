from __future__ import annotations

import re
from dataclasses import dataclass


def _key(value: str) -> str:
    return re.sub(r"\s+", " ", value.strip().lower())


@dataclass(frozen=True)
class QuestionCatalog:
    labels: dict[str, str]

    def short_name(self, question: str) -> str:
        key = _key(question)
        for needle, label in self.labels.items():
            if needle in key:
                return label
        return question.strip() or "Diğer Tarihli Soru"


def default_catalog() -> QuestionCatalog:
    return QuestionCatalog({
        "trafik sigortası": "Trafik Sigortası",
        "araç muayenesi": "Muayene",
        "taşıt kartı": "Taşıt Kartı",
        "taşıt uygunluk": "Taşıt Uygunluk",
        "t9": "T9",
        "sızdırmazlık": "Sızdırmazlık",
        "tank basınç": "Tank Basınç",
        "hidrostatik": "Tank Basınç",
        "src-5": "SRC-5",
        "tehlikeli madde sigortası": "Tehlikeli Madde Sigortası",
    })
