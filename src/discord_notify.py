from __future__ import annotations

import time
import json
from dataclasses import dataclass
from http.client import HTTPResponse
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from .event_checker import Reminder, format_remaining


@dataclass(frozen=True)
class DiscordResult:
    status_code: int


class DiscordNotifyError(RuntimeError):
    pass


def build_message(reminder: Reminder) -> str:
    event = reminder.event
    end_time = event.end_time.isoformat()
    source = f"\nSource: {event.source_url}" if event.source_url else ""
    return (
        f"[{reminder.threshold} reminder] {event.game} ({event.server})\n"
        f"Event: {event.event_name}\n"
        f"Ends: {end_time}\n"
        f"Remaining: about {format_remaining(reminder.remaining)}"
        f"{source}"
    )


def send_discord_message(
    webhook_url: str,
    content: str,
    *,
    timeout_seconds: float = 10,
    max_retries: int = 2,
) -> DiscordResult:
    payload = json.dumps({"content": content}).encode("utf-8")
    request = Request(
        webhook_url,
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    for attempt in range(max_retries + 1):
        try:
            with urlopen(request, timeout=timeout_seconds) as response:
                status_code = response.getcode()
        except HTTPError as exc:
            if exc.code == 429 and attempt < max_retries:
                retry_after = _retry_after_seconds(exc)
                time.sleep(retry_after)
                continue
            raise DiscordNotifyError(f"Discord returned HTTP {exc.code}.") from exc
        except URLError as exc:
            if attempt >= max_retries:
                raise DiscordNotifyError(f"Discord request failed after retries: {exc}") from exc
            time.sleep(1)
            continue

        if 200 <= status_code < 300:
            return DiscordResult(status_code=status_code)

        raise DiscordNotifyError(f"Discord returned HTTP {status_code}.")

    raise DiscordNotifyError("Discord request failed.")


def _retry_after_seconds(response: HTTPError | HTTPResponse) -> float:
    header_value = response.headers.get("Retry-After", "1")
    try:
        body = response.read().decode("utf-8")
        data = json.loads(body) if body else {}
    except (ValueError, OSError):
        data = {}
    value = data.get("retry_after", header_value)
    try:
        return min(max(float(value), 0.5), 10)
    except (TypeError, ValueError):
        return 1
