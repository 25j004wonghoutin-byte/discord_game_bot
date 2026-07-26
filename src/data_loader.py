from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class Event:
    id: str
    game: str
    server: str
    event_name: str
    end_time: datetime
    enabled: bool
    start_time: datetime | None = None
    source_url: str | None = None
    webhook_key: str | None = None
    notes: str | None = None


class EventDataError(ValueError):
    pass


def load_events(path: Path) -> list[Event]:
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise EventDataError(f"Events file not found: {path}") from exc
    except json.JSONDecodeError as exc:
        raise EventDataError(f"Invalid JSON in {path}: {exc}") from exc

    if not isinstance(raw, list):
        raise EventDataError("Events file root must be a JSON array.")

    seen_ids: set[str] = set()
    events: list[Event] = []
    for index, item in enumerate(raw):
        if not isinstance(item, dict):
            raise EventDataError(f"Event at index {index} must be an object.")

        event_id = _required_str(item, "id", index)
        if event_id in seen_ids:
            raise EventDataError(f"Duplicate event id: {event_id}")
        seen_ids.add(event_id)

        enabled = item.get("enabled")
        if not isinstance(enabled, bool):
            raise EventDataError(f"Event {event_id}: enabled must be a boolean.")

        end_time = _parse_datetime(_required_str(item, "end_time", index, event_id), "end_time", event_id)
        start_time_value = item.get("start_time")
        start_time = None
        if start_time_value is not None:
            if not isinstance(start_time_value, str) or not start_time_value.strip():
                raise EventDataError(f"Event {event_id}: start_time must be a non-empty string when present.")
            start_time = _parse_datetime(start_time_value, "start_time", event_id)
            if start_time >= end_time:
                raise EventDataError(f"Event {event_id}: start_time must be earlier than end_time.")

        events.append(
            Event(
                id=event_id,
                game=_required_str(item, "game", index, event_id),
                server=_required_str(item, "server", index, event_id),
                event_name=_required_str(item, "event_name", index, event_id),
                start_time=start_time,
                end_time=end_time,
                source_url=_optional_str(item, "source_url", event_id),
                webhook_key=_optional_str(item, "webhook_key", event_id),
                enabled=enabled,
                notes=_optional_str(item, "notes", event_id),
            )
        )

    return events


def _required_str(item: dict[str, Any], key: str, index: int, event_id: str | None = None) -> str:
    value = item.get(key)
    if not isinstance(value, str) or not value.strip():
        target = event_id or f"at index {index}"
        raise EventDataError(f"Event {target}: {key} must be a non-empty string.")
    return value.strip()


def _optional_str(item: dict[str, Any], key: str, event_id: str) -> str | None:
    value = item.get(key)
    if value is None:
        return None
    if not isinstance(value, str):
        raise EventDataError(f"Event {event_id}: {key} must be a string when present.")
    return value.strip() or None


def _parse_datetime(value: str, field: str, event_id: str) -> datetime:
    normalized = value.strip()
    if normalized.endswith("Z"):
        normalized = normalized[:-1] + "+00:00"
    try:
        parsed = datetime.fromisoformat(normalized)
    except ValueError as exc:
        raise EventDataError(f"Event {event_id}: {field} must be valid ISO 8601.") from exc
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise EventDataError(f"Event {event_id}: {field} must include a UTC offset.")
    return parsed
