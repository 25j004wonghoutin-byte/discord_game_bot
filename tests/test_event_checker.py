from __future__ import annotations

import unittest
from datetime import datetime

from src.data_loader import Event
from src.event_checker import THRESHOLD_24H, THRESHOLD_6H, find_due_reminders
from src.state_store import NotificationState


def make_event(end_time: str, *, start_time: str | None = None, enabled: bool = True) -> Event:
    return Event(
        id="event-1",
        game="Game",
        server="JP",
        event_name="Event",
        start_time=datetime.fromisoformat(start_time) if start_time else None,
        end_time=datetime.fromisoformat(end_time),
        enabled=enabled,
    )


class EventCheckerTests(unittest.TestCase):
    def test_finds_24h_reminder(self):
        now = datetime.fromisoformat("2026-07-21T00:00:00+00:00")
        event = make_event("2026-07-21T23:30:00+00:00")

        reminders = find_due_reminders([event], NotificationState(), now)

        self.assertEqual([reminder.threshold for reminder in reminders], [THRESHOLD_24H])

    def test_prioritizes_6h_over_late_24h(self):
        now = datetime.fromisoformat("2026-07-21T00:00:00+00:00")
        event = make_event("2026-07-21T05:30:00+00:00")

        reminders = find_due_reminders([event], NotificationState(), now)

        self.assertEqual([reminder.threshold for reminder in reminders], [THRESHOLD_6H])

    def test_does_not_repeat_sent_threshold(self):
        now = datetime.fromisoformat("2026-07-21T00:00:00+00:00")
        event = make_event("2026-07-21T23:30:00+00:00")
        state = NotificationState()
        state.mark_notified("event-1", THRESHOLD_24H, now)

        reminders = find_due_reminders([event], state, now)

        self.assertEqual(reminders, [])


if __name__ == "__main__":
    unittest.main()
