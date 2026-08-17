# New Windows computer setup

This project can move by GitHub. No physical zip is required.

## What continues without the old computer

These are GitHub Actions schedules and keep running from GitHub after changing computers:

- `Event Check` in `.github/workflows/event-check.yml`
  - hourly event deadline reminders
  - uses the `notification-state` branch
- `Weekly Static Messages` in `.github/workflows/weekly-static-messages.yml`
  - Sunday 15:00 Asia/Shanghai fixed NTE/HSR reminders

They depend on GitHub repository secrets, not the local `.env` file:

```text
DISCORD_WEBHOOK_URL_NTE
DISCORD_WEBHOOK_URL_BA
DISCORD_WEBHOOK_URL_HSR
DISCORD_WEBHOOK_URL_GBF
```

If these secrets are already set in GitHub, they do not need to be copied to the new computer.

## What must be restored on the new computer

Codex local assets are computer-local:

- the personal skill `$game-event-updater`
- the Codex local automation `Weekly game event updater`

The skill is now backed up in this repository under:

```text
codex/skills/game-event-updater
```

The automation prompt is backed up under:

```text
codex/automations/weekly-game-event-updater.prompt.md
```

## Setup steps

1. Install Git, Python 3.12, and Codex on the new Windows computer.
2. Clone the repository:

```powershell
git clone https://github.com/25j004wonghoutin-byte/discord_game_bot.git
cd discord_game_bot
```

3. Create the virtual environment:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

4. Validate the project:

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests
.\.venv\Scripts\python.exe -m src.main --validate-only
.\.venv\Scripts\python.exe -m src.weekly_static_messages --dry-run
```

5. Restore the Codex skill:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\restore_codex_assets.ps1
```

6. Recreate the Codex local automation.

In Codex, ask:

```text
Create a local weekly automation every Monday 12:00 Asia/Shanghai using the prompt in codex/automations/weekly-game-event-updater.prompt.md.
```

Replace `<PATH_TO_CLONED_REPO>` in the prompt with the actual clone path.

## Important limitation

GitHub Actions schedules run even if your computer is off.

Codex local automations are tied to the local Codex environment. After changing computers, recreate the local automation on the new machine if you want weekly automatic event searching/updating to continue.

## Local `.env`

For local manual sending, create `.env` from `.env.example` and fill in webhook URLs. Do not commit `.env`.

GitHub Actions do not read your local `.env`; they read GitHub repository secrets.
