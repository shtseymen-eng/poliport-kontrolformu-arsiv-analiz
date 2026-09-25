from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path

from .models import ArchiveFile, MONTHS


@dataclass(frozen=True)
class ArchiveCatalog:
    root: Path
    files: tuple[ArchiveFile, ...]

    @property
    def years(self) -> list[int]:
        return sorted({item.year for item in self.files})

    @property
    def months(self) -> list[str]:
        return sorted({item.month for item in self.files}, key=lambda value: MONTHS.get(value.upper(), 99))


def discover_archive(root: Path) -> ArchiveCatalog:
    files: list[ArchiveFile] = []
    if not root.exists():
        return ArchiveCatalog(root, ())
    for path in root.glob("*/*/*/*/Kontrol Formları/*.xlsx"):
        try:
            year, month, day, carrier = path.relative_to(root).parts[:4]
            if int(year) and int(day) and month.upper() in MONTHS:
                files.append(ArchiveFile(path, int(year), month.upper(), int(day), carrier))
        except (ValueError, IndexError):
            continue
    return ArchiveCatalog(root, tuple(sorted(files, key=lambda item: str(item.path).lower())))


def select_forms(catalog: ArchiveCatalog, years: set[int], months: set[str], days: set[int], carrier: str | None) -> list[ArchiveFile]:
    selected = []
    wanted_months = {item.upper() for item in months}
    for item in catalog.files:
        if years and item.year not in years:
            continue
        if wanted_months and item.month.upper() not in wanted_months:
            continue
        if days and item.day not in days:
            continue
        if carrier and carrier != "Tümü" and item.carrier != carrier:
            continue
        selected.append(item)
    return sorted(selected, key=lambda item: (item.year, MONTHS[item.month], item.day, item.carrier.lower(), item.path.name.lower()))


def carrier_file_counts(files: list[ArchiveFile]) -> dict[str, int]:
    grouped: dict[str, set[Path]] = defaultdict(set)
    for item in files:
        grouped[item.carrier].add(item.path)
    return dict(sorted((carrier, len(paths)) for carrier, paths in grouped.items()))
