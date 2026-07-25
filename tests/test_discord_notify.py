from __future__ import annotations

import unittest
from unittest import mock

from src.discord_notify import send_discord_message


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


if __name__ == "__main__":
    unittest.main()
