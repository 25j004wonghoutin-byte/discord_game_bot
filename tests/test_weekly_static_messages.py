from __future__ import annotations

import os
import unittest
from unittest import mock

from src import weekly_static_messages


class WeeklyStaticMessagesTests(unittest.TestCase):
    def test_dry_run_prints_configured_messages(self):
        with mock.patch.dict(os.environ, {}, clear=True), mock.patch("builtins.print") as print_mock:
            result = weekly_static_messages.main(["--dry-run"])

        self.assertEqual(result, 0)
        print_mock.assert_has_calls(
            [
                mock.call("[NTE] 今日星期日, 清左都市體力未, 搶左劫未, 快"),
                mock.call("[HSR] 星期日記得打模擬宇宙, 快"),
            ]
        )

    def test_sends_messages_to_configured_webhook_keys(self):
        env = {
            "DISCORD_WEBHOOK_URL_NTE": "https://example.com/nte",
            "DISCORD_WEBHOOK_URL_HSR": "https://example.com/hsr",
        }

        with mock.patch.dict(os.environ, env, clear=True), mock.patch(
            "src.weekly_static_messages.send_discord_message"
        ) as send_mock:
            send_mock.return_value.status_code = 204

            result = weekly_static_messages.main([])

        self.assertEqual(result, 0)
        send_mock.assert_has_calls(
            [
                mock.call("https://example.com/nte", "今日星期日, 清左都市體力未, 搶左劫未, 快"),
                mock.call("https://example.com/hsr", "星期日記得打模擬宇宙, 快"),
            ]
        )


if __name__ == "__main__":
    unittest.main()
