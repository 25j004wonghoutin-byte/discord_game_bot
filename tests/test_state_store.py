from __future__ import annotations

import tempfile
import unittest
from datetime import datetime
from pathlib import Path

from src.state_store import NotificationState


class StateStoreTests(unittest.TestCase):
    def test_state_round_trip(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "notification_state.json"
            state = NotificationState()
            state.mark_notified("event-1", "24h", datetime.fromisoformat("2026-07-21T00:00:00+00:00"))
            state.save(path)

            loaded = NotificationState.load(path)

        self.assertTrue(loaded.has_notified("event-1", "24h"))


if __name__ == "__main__":
    unittest.main()
