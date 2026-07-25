from __future__ import annotations

import json
import os
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


StateData = dict[str, dict[str, str]]


class NotificationState:
    def __init__(self, data: StateData | None = None) -> None:
        self._data: StateData = data or {}

    @classmethod
    def load(cls, path: Path) -> "NotificationState":
        if not path.exists():
            return cls()
        raw = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(raw, dict):
            raise ValueError("Notification state root must be an object.")
        return cls(_normalize_state(raw))

    def has_notified(self, event_id: str, threshold: str) -> bool:
        return threshold in self._data.get(event_id, {})

    def mark_notified(self, event_id: str, threshold: str, notified_at: datetime | None = None) -> None:
        timestamp = (notified_at or datetime.now(UTC)).astimezone(UTC).isoformat().replace("+00:00", "Z")
        self._data.setdefault(event_id, {})[threshold] = timestamp

    def save(self, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        temp_path = path.with_suffix(path.suffix + ".tmp")
        temp_path.write_text(json.dumps(self._data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        os.replace(temp_path, path)


def _normalize_state(raw: dict[str, Any]) -> StateData:
    normalized: StateData = {}
    for event_id, thresholds in raw.items():
        if not isinstance(event_id, str) or not isinstance(thresholds, dict):
            raise ValueError("Notification state must map event ids to threshold objects.")
        normalized[event_id] = {}
        for threshold, timestamp in thresholds.items():
            if not isinstance(threshold, str) or not isinstance(timestamp, str):
                raise ValueError("Notification state threshold entries must be strings.")
            normalized[event_id][threshold] = timestamp
    return normalized
