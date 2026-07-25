from __future__ import annotations

import argparse
import logging
import sys
from datetime import UTC, datetime

from .config import load_config
from .data_loader import EventDataError, load_events
from .discord_notify import DiscordNotifyError, build_message, send_discord_message
from .event_checker import find_due_reminders
from .state_store import NotificationState


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Send Discord reminders for game events.")
    parser.add_argument("--dry-run", action="store_true", help="Print due reminders without sending Discord messages.")
    args = parser.parse_args(argv)

    try:
        config = load_config(dry_run=args.dry_run)
        logging.basicConfig(level=config.log_level, format="%(levelname)s %(message)s")

        events = load_events(config.events_file)
        state = NotificationState.load(config.state_file)
        now = datetime.now(UTC)
        reminders = find_due_reminders(events, state, now)

        if not reminders:
            logging.info("No reminders are due.")
            return 0

        for reminder in reminders:
            message = build_message(reminder)
            if config.dry_run:
                print(message)
                print()
                continue

            assert config.discord_webhook_url is not None
            result = send_discord_message(config.discord_webhook_url, message)
            logging.info("Sent %s reminder for %s. Discord HTTP %s.", reminder.threshold, reminder.event.id, result.status_code)
            state.mark_notified(reminder.event.id, reminder.threshold, now)

        if not config.dry_run:
            state.save(config.state_file)
        return 0
    except (EventDataError, ValueError, DiscordNotifyError) as exc:
        logging.error("%s", exc)
        return 1


if __name__ == "__main__":
    sys.exit(main())
