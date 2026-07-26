from __future__ import annotations

import os
import re
from dataclasses import dataclass
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]


@dataclass(frozen=True)
class Config:
    discord_webhook_urls: dict[str, str]
    events_file: Path
    state_file: Path
    dry_run: bool
    log_level: str

    def get_webhook_url(self, webhook_key: str | None) -> str:
        key = normalize_webhook_key(webhook_key) if webhook_key else "DEFAULT"
        try:
            return self.discord_webhook_urls[key]
        except KeyError as exc:
            expected_env = "DISCORD_WEBHOOK_URL_DEFAULT" if key == "DEFAULT" else f"DISCORD_WEBHOOK_URL_{key}"
            raise ValueError(f"Missing webhook URL for key '{key}'. Expected environment variable: {expected_env}.") from exc


def load_dotenv(path: Path = PROJECT_ROOT / ".env") -> None:
    if not path.exists():
        return

    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        os.environ.setdefault(key, value)


def parse_bool(value: str | None, default: bool = False) -> bool:
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "y", "on"}


def resolve_project_path(value: str) -> Path:
    path = Path(value)
    if path.is_absolute():
        return path
    return PROJECT_ROOT / path


def normalize_webhook_key(value: str) -> str:
    normalized = value.strip().upper().replace("-", "_").replace(" ", "_")
    if not normalized or not re.fullmatch(r"[A-Z0-9_]+", normalized):
        raise ValueError("webhook_key may only contain letters, numbers, spaces, hyphens, or underscores.")
    return normalized


def collect_webhook_urls() -> dict[str, str]:
    urls: dict[str, str] = {}
    legacy_default = os.getenv("DISCORD_WEBHOOK_URL")
    if legacy_default:
        urls["DEFAULT"] = legacy_default

    for name, value in os.environ.items():
        if not name.startswith("DISCORD_WEBHOOK_URL_") or not value:
            continue
        key = name.removeprefix("DISCORD_WEBHOOK_URL_")
        if key == "DEFAULT":
            urls["DEFAULT"] = value
        else:
            urls[normalize_webhook_key(key)] = value

    return urls


def load_config(*, dry_run: bool | None = None) -> Config:
    load_dotenv()
    resolved_dry_run = parse_bool(os.getenv("DRY_RUN")) if dry_run is None else dry_run
    webhook_urls = collect_webhook_urls()

    if not resolved_dry_run and not webhook_urls:
        raise ValueError("At least one DISCORD_WEBHOOK_URL_* environment variable is required unless dry-run mode is enabled.")

    return Config(
        discord_webhook_urls=webhook_urls,
        events_file=resolve_project_path(os.getenv("EVENTS_FILE", "data/events.json")),
        state_file=resolve_project_path(os.getenv("STATE_FILE", "data/notification_state.json")),
        dry_run=resolved_dry_run,
        log_level=os.getenv("LOG_LEVEL", "INFO").upper(),
    )
