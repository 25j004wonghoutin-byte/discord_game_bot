from __future__ import annotations

import time
import json
from dataclasses import dataclass
from datetime import timedelta
from http.client import HTTPResponse
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from .event_checker import Reminder


@dataclass(frozen=True)
class DiscordResult:
    status_code: int


class DiscordNotifyError(RuntimeError):
    pass


def build_message(reminder: Reminder) -> str:
    event = reminder.event
    end_time = event.end_time.strftime("%m/%d %H:%M")
    timezone = _timezone_label(event.end_time)
    return (
        f"[活動結束提醒] {event.game} ({event.server})\n"
        f"活動: {event.event_name}\n"
        f"終了時間: {end_time} [{timezone}]\n"
        f"提醒: 距離結束還有 {_format_remaining_zh(reminder.remaining)}\n"
        "--------------------"
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
        headers={
            "Content-Type": "application/json",
            "User-Agent": "game-event-discord-bot/1.0",
        },
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
            detail = _safe_response_detail(exc)
            raise DiscordNotifyError(f"Discord returned HTTP {exc.code}.{detail}") from exc
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


def _format_remaining_zh(remaining: timedelta) -> str:
    total_minutes = max(0, int(remaining.total_seconds() // 60))
    hours, minutes = divmod(total_minutes, 60)
    return f"{hours:02d}時間{minutes:02d}分"


def _timezone_label(end_time) -> str:
    offset = end_time.utcoffset()
    if offset is None:
        return "UTC unknown"

    total_minutes = int(offset.total_seconds() // 60)
    if total_minutes == 540:
        return "JST"
    if total_minutes == 0:
        return "UTC"

    sign = "+" if total_minutes >= 0 else "-"
    absolute_minutes = abs(total_minutes)
    hours, minutes = divmod(absolute_minutes, 60)
    return f"UTC{sign}{hours:02d}:{minutes:02d}"


def _safe_response_detail(response: HTTPError) -> str:
    try:
        body = response.read().decode("utf-8", errors="replace")
    except OSError:
        return ""

    compact = " ".join(body.split())
    if not compact:
        return ""

    return f" Response: {compact[:500]}"
