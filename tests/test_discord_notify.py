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

    def test_message_uses_localized_reminder_format_without_source_url(self):
        event = Event(
            id="event-1",
            game="System Test",
            server="Test",
            event_name="Discord notification workflow test",
            end_time=datetime.fromisoformat("2026-07-25T21:20:00+09:00"),
            enabled=True,
            source_url="https://example.com/source",
        )
        reminder = Reminder(event=event, threshold="6h", remaining=timedelta(hours=5, minutes=4))

        message = build_message(reminder)

        self.assertEqual(
            message,
            "[活動結束提醒] System Test (Test)\n"
            "活動: Discord notification workflow test\n"
            "終了時間: 07/25 21:20 [JST]\n"
            "提醒: 距離結束還有 05時間04分",
        )
        self.assertNotIn("Source:", message)
        self.assertNotIn("https://example.com/source", message)


if __name__ == "__main__":
    unittest.main()
