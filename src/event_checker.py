from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime, timedelta

from .data_loader import Event
from .state_store import NotificationState


THRESHOLD_24H = "24h"
THRESHOLD_6H = "6h"


@dataclass(frozen=True)
class Reminder:
    event: Event
    threshold: str
    remaining: timedelta


def find_due_reminders(events: list[Event], state: NotificationState, now: datetime) -> list[Reminder]:
    now_utc = now.astimezone(UTC)
    due: list[Reminder] = []

    for event in events:
        if not event.enabled:
            continue

        if event.start_time is not None and now_utc < event.start_time.astimezone(UTC):
            continue

        end_utc = event.end_time.astimezone(UTC)
        remaining = end_utc - now_utc
        if remaining <= timedelta(0):
            continue

        if remaining <= timedelta(hours=6):
            if not state.has_notified(event.id, THRESHOLD_6H):
                due.append(Reminder(event=event, threshold=THRESHOLD_6H, remaining=remaining))
            continue

        if remaining <= timedelta(hours=24) and not state.has_notified(event.id, THRESHOLD_24H):
            due.append(Reminder(event=event, threshold=THRESHOLD_24H, remaining=remaining))

    return due


def format_remaining(remaining: timedelta) -> str:
    total_minutes = max(0, int(remaining.total_seconds() // 60))
    hours, minutes = divmod(total_minutes, 60)
    if hours:
        return f"{hours}h {minutes}m"
    return f"{minutes}m"
