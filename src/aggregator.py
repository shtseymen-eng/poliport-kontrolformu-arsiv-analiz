from __future__ import annotations

from collections import defaultdict
from datetime import date, datetime

from .models import AnalysisResult, AssetSummary, AssetType, ValidityRecord


def remaining_days(record: ValidityRecord, as_of: date) -> int:
    return (record.validity_date - as_of).days


def _control_time(record: ValidityRecord) -> datetime:
    return record.control_at or datetime.combine(record.control_date, datetime.min.time())


def _latest_documents(values: list[ValidityRecord]) -> dict[str, ValidityRecord]:
    latest: dict[str, ValidityRecord] = {}
    for value in values:
        previous = latest.get(value.short_name)
        if previous is None or _control_time(value) > _control_time(previous):
            latest[value.short_name] = value
    return latest


def critical_records(records: list[ValidityRecord], as_of: date, warning_days: int = 20) -> list[ValidityRecord]:
    return sorted(
        [item for item in records if remaining_days(item, as_of) <= warning_days],
        key=lambda item: (item.validity_date, item.carrier, item.asset_id),
    )


def summarize(records: list[ValidityRecord], as_of: date) -> AnalysisResult:
    grouped: dict[tuple[str, AssetType, str], list[ValidityRecord]] = defaultdict(list)
    for record in records:
        grouped[(record.carrier, record.asset_type, record.asset_id)].append(record)
    by_type: dict[AssetType, list[AssetSummary]] = {asset_type: [] for asset_type in AssetType}
    for (carrier, asset_type, asset_id), values in grouped.items():
        latest_documents = _latest_documents(values)
        by_type[asset_type].append(AssetSummary(
            carrier=carrier,
            asset_type=asset_type,
            asset_id=asset_id,
            arrival_count=len({_control_time(value) for value in values}),
            latest_control_date=max(value.control_date for value in values),
            document_dates={name: value.validity_date for name, value in latest_documents.items()},
        ))
    for rows in by_type.values():
        rows.sort(key=lambda item: (item.carrier.lower(), item.asset_id))
    current_records = [record for values in grouped.values() for record in _latest_documents(values).values()]
    return AnalysisResult(by_type=by_type, critical=critical_records(current_records, as_of))
