from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime
from enum import Enum
from pathlib import Path


class AssetType(str, Enum):
    TRACTOR = "Çekici"
    TRAILER = "Dorse"
    ISO_TANK = "ISO Tank"
    DRIVER = "Sürücü"


@dataclass(frozen=True)
class ArchiveFile:
    path: Path
    year: int
    month: str
    day: int
    carrier: str

    @property
    def archive_date(self) -> date:
        return date(self.year, MONTHS[self.month.upper()], self.day)


MONTHS = {
    "OCAK": 1, "ŞUBAT": 2, "MART": 3, "NİSAN": 4, "MAYIS": 5,
    "HAZİRAN": 6, "TEMMUZ": 7, "AĞUSTOS": 8, "EYLÜL": 9,
    "EKİM": 10, "KASIM": 11, "ARALIK": 12,
}


@dataclass(frozen=True)
class ValidityRecord:
    carrier: str
    asset_type: AssetType
    asset_id: str
    question: str
    short_name: str
    validity_date: date
    control_date: date
    source_path: str
    control_at: datetime | None = None


@dataclass
class AssetSummary:
    carrier: str
    asset_type: AssetType
    asset_id: str
    arrival_count: int
    latest_control_date: date
    document_dates: dict[str, date] = field(default_factory=dict)


@dataclass
class UnreadableFile:
    source_path: str
    reason: str


@dataclass
class AnalysisResult:
    by_type: dict[AssetType, list[AssetSummary]]
    critical: list[ValidityRecord]
