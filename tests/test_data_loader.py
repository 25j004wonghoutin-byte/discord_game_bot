from __future__ import annotations

import json
import unittest
from unittest import mock


from src.data_loader import EventDataError, load_events


def write_events(tmp_path, events):
    path = tmp_path / "events.json"
    path.write_text(json.dumps(events), encoding="utf-8")
    return path


def valid_event(**overrides):
    event = {
        "id": "event-1",
        "game": "Game",
        "server": "JP",
        "event_name": "Event",
        "start_time": "2026-07-20T10:00:00+09:00",
        "end_time": "2026-07-22T10:00:00+09:00",
        "enabled": True,
    }
    event.update(overrides)
    return event


class DataLoaderTests(unittest.TestCase):
    def test_loads_valid_event(self):
        with mock.patch("pathlib.Path.read_text", return_value=json.dumps([valid_event()])):
            events = load_events(__import__("pathlib").Path("events.json"))

        self.assertEqual(events[0].id, "event-1")
        self.assertIsNotNone(events[0].end_time.utcoffset())

    def test_loads_webhook_key(self):
        with mock.patch("pathlib.Path.read_text", return_value=json.dumps([valid_event(webhook_key="NTE")])):
            events = load_events(__import__("pathlib").Path("events.json"))

        self.assertEqual(events[0].webhook_key, "NTE")

    def test_rejects_duplicate_ids(self):
        with mock.patch("pathlib.Path.read_text", return_value=json.dumps([valid_event(), valid_event()])):
            with self.assertRaisesRegex(EventDataError, "Duplicate event id"):
                load_events(__import__("pathlib").Path("events.json"))

    def test_rejects_datetime_without_offset(self):
        event_data = [valid_event(end_time="2026-07-22T10:00:00")]
        with mock.patch("pathlib.Path.read_text", return_value=json.dumps(event_data)):
            with self.assertRaisesRegex(EventDataError, "UTC offset"):
                load_events(__import__("pathlib").Path("events.json"))


if __name__ == "__main__":
    unittest.main()
