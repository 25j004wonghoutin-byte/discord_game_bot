from __future__ import annotations

import os

from src.discord_notify import send_discord_message


def main() -> int:
    webhook_url = os.getenv("DISCORD_WEBHOOK_URL")
    if not webhook_url:
        print("DISCORD_WEBHOOK_URL is not set.")
        return 1

    result = send_discord_message(webhook_url, "Game event webhook test succeeded.")
    print(result.status_code)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
