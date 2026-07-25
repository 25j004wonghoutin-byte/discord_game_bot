from __future__ import annotations

import unittest
from unittest import mock

from datetime import datetime, timedelta

from src.data_loader import Event
from src.discord_notify import build_message, send_discord_message
from src.event_checker import Reminder


class DiscordNotifyTests(unittest.TestCase):
    def test_send_uses_user_agent_header(self):
        response = mock.Mock()
        response.__enter__ = mock.Mock(return_value=response)
        response.__exit__ = mock.Mock(return_value=None)
        response.getcode.return_value = 204

        with mock.patch("src.discord_notify.urlopen", return_value=response) as urlopen:
            result = send_discord_message("https://discord.com/api/webhooks/test", "hello")

        request = urlopen.call_args.args[0]
        self.assertEqual(result.status_code, 204)
        self.assertEqual(request.get_header("User-agent"), "game-event-discord-bot/1.0")

    def test_message_does_not_include_source_url(self):
        event = Event(
            id="event-1",
            game="Game",
            server="JP",
            event_name="Event",
            end_time=datetime.fromisoformat("2026-07-25T21:20:00+09:00"),
            enabled=True,
            source_url="https://example.com/source",
        )
        reminder = Reminder(event=event, threshold="6h", remaining=timedelta(hours=5))

        message = build_message(reminder)

        self.assertNotIn("Source:", message)
        self.assertNotIn("https://example.com/source", message)


if __name__ == "__main__":
    unittest.main()
