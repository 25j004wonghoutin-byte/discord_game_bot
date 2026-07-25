from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]


@dataclass(frozen=True)
class Config:
    discord_webhook_url: str | None
    events_file: Path
    state_file: Path
    dry_run: bool
    log_level: str


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


def load_config(*, dry_run: bool | None = None) -> Config:
    load_dotenv()
    resolved_dry_run = parse_bool(os.getenv("DRY_RUN")) if dry_run is None else dry_run
    webhook_url = os.getenv("DISCORD_WEBHOOK_URL")

    if not resolved_dry_run and not webhook_url:
        raise ValueError("DISCORD_WEBHOOK_URL is required unless dry-run mode is enabled.")

    return Config(
        discord_webhook_url=webhook_url,
        events_file=resolve_project_path(os.getenv("EVENTS_FILE", "data/events.json")),
        state_file=resolve_project_path(os.getenv("STATE_FILE", "data/notification_state.json")),
        dry_run=resolved_dry_run,
        log_level=os.getenv("LOG_LEVEL", "INFO").upper(),
    )
