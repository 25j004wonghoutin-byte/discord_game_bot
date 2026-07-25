# Game Event Discord Bot

Python-based MVP for sending Discord reminders before game events end.

The first version uses manually maintained JSON data, local notification state, and Discord webhooks. It does not include crawlers, game login, databases, dashboards, or Discord bot tokens.

## Setup

1. Create or refresh the local virtual environment.
2. Copy `.env.example` to `.env`.
3. Set `DISCORD_WEBHOOK_URL` in `.env`.
4. Replace the disabled sample in `data/events.json` with official event data.

Do not commit `.env` or real webhook URLs.

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests
```

## Run

Preview due reminders without sending Discord messages:

```powershell
.\.venv\Scripts\python.exe -m src.main --dry-run
```

Send due reminders:

```powershell
.\.venv\Scripts\python.exe -m src.main
```

Run tests:

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests
```

## Event Format

```json
{
  "id": "blue-archive-jp-sample-2026-07",
  "game": "ブルーアーカイブ",
  "server": "JP",
  "event_name": "Sample event",
  "start_time": "2026-07-01T11:00:00+09:00",
  "end_time": "2026-07-29T03:59:00+09:00",
  "source_url": "https://example.com/official-announcement",
  "enabled": true,
  "notes": "Time verified against the official announcement."
}
```

All event times must include a UTC offset. The event `id` should stay stable even if the event name or time is corrected.

## Reminder Rules

- Send one `24h` reminder when an active event has less than or equal to 24 hours remaining.
- Send one `6h` reminder when an active event has less than or equal to 6 hours remaining.
- If a delayed run first sees an event inside the 6h window, send only the `6h` reminder.
- Record a reminder only after Discord returns success.

## Current Limitation

`data/notification_state.json` works for local runs, but GitHub-hosted runners do not preserve local files across scheduled executions. Before enabling hourly GitHub Actions, choose a persistent state strategy such as a dedicated state branch or an external KV store.

The included `CI` workflow only runs tests and dry-run checks. It does not send Discord messages.

## GitHub Actions Reminder Workflow

The `Event Check` workflow runs every hour at minute 17 UTC and can also be triggered manually from GitHub Actions.

Required repository setup:

1. Add a repository secret named `DISCORD_WEBHOOK_URL`.
2. Set Actions workflow permissions to `Read and write permissions`.
3. Keep the default branch as `main`.

The workflow uses a dedicated `notification-state` branch to persist sent reminders. On the first run, it creates that branch automatically with an initialization commit containing:

```text
notification_state.json
```

After each successful Discord send, the app updates that state file. Once the state branch exists, runs with no new reminders do not create state commits.

The workflow uses:

```yaml
permissions:
  contents: write

concurrency:
  group: game-event-reminder
  cancel-in-progress: false
```

`contents: write` is only needed so the workflow can commit `notification_state.json` to the `notification-state` branch. `concurrency` prevents overlapping scheduled runs from sending duplicate reminders.
