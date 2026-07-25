from __future__ import annotations

import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from src.main import main, parse_now


class MainTests(unittest.TestCase):
    def test_validate_only_does_not_require_webhook(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            events_file = temp_path / "events.json"
            state_file = temp_path / "notification_state.json"
            events_file.write_text(
                json.dumps(
                    [
                        {
                            "id": "event-1",
                            "game": "Game",
                            "server": "JP",
                            "event_name": "Event",
                            "end_time": "2026-07-22T10:00:00+09:00",
                            "enabled": True,
                        }
                    ]
                ),
                encoding="utf-8",
            )
            state_file.write_text("{}\n", encoding="utf-8")

            env = {
                "EVENTS_FILE": str(events_file),
                "STATE_FILE": str(state_file),
            }
            with mock.patch.dict(os.environ, env, clear=True):
                result = main(["--validate-only"])

        self.assertEqual(result, 0)

    def test_parse_now_requires_offset(self):
        with self.assertRaisesRegex(ValueError, "UTC offset"):
            parse_now("2026-07-21T00:00:00")


if __name__ == "__main__":
    unittest.main()
