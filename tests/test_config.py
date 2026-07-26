from __future__ import annotations

import os
import unittest
from unittest import mock

from src.config import collect_webhook_urls, load_config, normalize_webhook_key


class ConfigTests(unittest.TestCase):
    def test_collects_named_webhook_urls(self):
        env = {
            "DISCORD_WEBHOOK_URL_NTE": "https://example.com/nte",
            "DISCORD_WEBHOOK_URL_BA": "https://example.com/ba",
        }
        with mock.patch.dict(os.environ, env, clear=True):
            urls = collect_webhook_urls()

        self.assertEqual(urls["NTE"], "https://example.com/nte")
        self.assertEqual(urls["BA"], "https://example.com/ba")

    def test_get_webhook_url_uses_event_key(self):
        env = {
            "DISCORD_WEBHOOK_URL_NTE": "https://example.com/nte",
        }
        with mock.patch.dict(os.environ, env, clear=True), mock.patch("src.config.load_dotenv"):
            config = load_config(dry_run=False)

        self.assertEqual(config.get_webhook_url("NTE"), "https://example.com/nte")

    def test_normalizes_webhook_key(self):
        self.assertEqual(normalize_webhook_key("blue archive"), "BLUE_ARCHIVE")


if __name__ == "__main__":
    unittest.main()
