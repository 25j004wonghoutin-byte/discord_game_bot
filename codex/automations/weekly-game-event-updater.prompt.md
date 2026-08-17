# Weekly game event updater automation prompt

Use this prompt when recreating the Codex local automation on a new computer.

Schedule: every Monday 12:00 Asia/Shanghai.

Prompt:

```text
Use $game-event-updater to update Jerry's Discord game event notification bot for all configured games.

Actual bot repository path: <PATH_TO_CLONED_REPO>
Skill path: <USERPROFILE>\.codex\skills\game-event-updater

Run the weekly multi-game update workflow for NTE, Blue Archive, Honkai Star Rail, and GBF:
1. Read the skill and its references.
2. Search current event schedules for each configured game/server.
3. Add or update only events with explicit end date and end time in data/events.json.
4. Use the configured webhook_key for each game.
5. Do not include or print Discord webhook secret values. Do not read local .env aloud.
6. Validate with validate-only, unit tests, and at least one relevant dry-run.
7. Use git grep only on tracked files for webhook leak checks.
8. If files changed and validation passes, commit and push to origin/main.
9. If no valid event changes are found, do not commit.
10. If any source is blocked or a time is ambiguous, leave that event unchanged and report what needs user confirmation.
```
