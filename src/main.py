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
    parser.add_argument("--validate-only", action="store_true", help="Validate event and state files without sending reminders.")
    parser.add_argument("--now", help="Override current time for testing, as ISO 8601 with UTC offset.")
    args = parser.parse_args(argv)

    try:
        config = load_config(dry_run=args.dry_run or args.validate_only)
        logging.basicConfig(level=config.log_level, format="%(levelname)s %(message)s")

        events = load_events(config.events_file)
        state = NotificationState.load(config.state_file)
        if args.validate_only:
            logging.info("Validation OK. Loaded %s event(s).", len(events))
            return 0

        now = parse_now(args.now) if args.now else datetime.now(UTC)
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

            webhook_url = config.get_webhook_url(reminder.event.webhook_key)
            result = send_discord_message(webhook_url, message)
            logging.info(
                "Sent %s reminder for %s via webhook key %s. Discord HTTP %s.",
                reminder.threshold,
                reminder.event.id,
                reminder.event.webhook_key or "DEFAULT",
                result.status_code,
            )
            state.mark_notified(reminder.event.id, reminder.threshold, now)

        if not config.dry_run:
            state.save(config.state_file)
        return 0
    except (EventDataError, ValueError, DiscordNotifyError) as exc:
        logging.error("%s", exc)
        return 1


def parse_now(value: str) -> datetime:
    normalized = value.strip()
    if normalized.endswith("Z"):
        normalized = normalized[:-1] + "+00:00"
    parsed = datetime.fromisoformat(normalized)
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise ValueError("--now must include a UTC offset.")
    return parsed


if __name__ == "__main__":
    sys.exit(main())
