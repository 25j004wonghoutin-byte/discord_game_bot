from __future__ import annotations

import argparse
import logging
import sys
from dataclasses import dataclass

from .config import load_config
from .discord_notify import DiscordNotifyError, send_discord_message


@dataclass(frozen=True)
class StaticMessage:
    webhook_key: str
    content: str


WEEKLY_SUNDAY_MESSAGES: tuple[StaticMessage, ...] = (
    StaticMessage(
        webhook_key="NTE",
        content="今日星期日, 清左都市體力未, 搶左劫未, 快",
    ),
    StaticMessage(
        webhook_key="HSR",
        content="星期日記得打模擬宇宙, 快",
    ),
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Send weekly static Sunday Discord messages.")
    parser.add_argument("--dry-run", action="store_true", help="Print messages without sending Discord webhooks.")
    args = parser.parse_args(argv)

    try:
        config = load_config(dry_run=args.dry_run)
        logging.basicConfig(level=config.log_level, format="%(levelname)s %(message)s")

        for message in WEEKLY_SUNDAY_MESSAGES:
            if config.dry_run:
                print(f"[{message.webhook_key}] {message.content}")
                continue

            webhook_url = config.get_webhook_url(message.webhook_key)
            result = send_discord_message(webhook_url, message.content)
            logging.info(
                "Sent weekly static message via webhook key %s. Discord HTTP %s.",
                message.webhook_key,
                result.status_code,
            )

        return 0
    except (ValueError, DiscordNotifyError) as exc:
        logging.error("%s", exc)
        return 1


if __name__ == "__main__":
    sys.exit(main())
