---
name: game-event-updater
description: Search current game event schedules and update Jerry's Discord game notification bot. Use when asked to find game events, add events to C:\Users\Jerry\Desktop\WORKSPACE\game_discord_bot\data\events.json, validate reminder output, commit, push, or run the weekly multi-game event update workflow for NTE, Blue Archive, Honkai Star Rail, GBF, or similar games.
---

# Game Event Updater

## Scope

Update Jerry's Discord game notification bot at:

`C:\Users\Jerry\Desktop\WORKSPACE\game_discord_bot`

Use this skill to:

1. Search current event schedules for configured games.
2. Keep only events with clear end date and end time.
3. Add or update events in `data/events.json`.
4. Validate the bot.
5. Commit and push to `origin/main`.

Do not expose Discord webhook URLs. Do not read `.env` aloud or include secret values in summaries.

## Required reference

Read `references/games.md` before searching or editing. It contains configured games, source preferences, server labels, time zones, and webhook keys.

## Event acceptance rules

Only add an event when its end time is explicit enough to convert to ISO 8601 with UTC offset.

Accept:

- `2026年8月3日(月)20:59`
- `8月26日(水) 6:00`, when the year is clear from page context or current event season
- `2026/08/05 03:59`

Do not add without user confirmation:

- date-only ranges with no HH:MM
- "メンテナンスまで", "長期間開催", "予定", or unclear end
- inferred reset times unless the user explicitly approves that rule

If start time is `メンテナンス後` or otherwise not exact, omit `start_time` and mention that in `notes`.

Use the game server's configured timezone. For Japanese servers, use JST `+09:00`.

## Workflow

1. Inspect repo status.
   - Run `git status --short`.
   - If unrelated user changes exist, preserve them and avoid staging them.

2. Search sources.
   - Prefer official sites when searchable.
   - Use configured攻略 sites when official pages are front-end-only or incomplete.
   - Browse/search because event schedules are time-sensitive.
   - Apply the game-specific candidate exclusions in `references/games.md` before recording candidates or checking duplicates.
   - For each candidate, record event name, start time if exact, end time, source URL, and confidence.

3. Present a compact candidate list before editing when the user asks to review first, or when any time is uncertain.
   - Separate "ready to add" from "needs confirmation".

4. Check for duplicates before editing.
   - Read the current `data/events.json`.
   - Treat an event as already present and skip it when any of these match an existing enabled or disabled event:
     - same `id`
     - same `game`, `server`, `event_name`, and `end_time`
     - same `game`, `server`, normalized `event_name`, and overlapping active period
   - Normalize event names for comparison by lowercasing ASCII, trimming whitespace, converting full-width/half-width punctuation where obvious, and ignoring common separators such as spaces, `・`, `/`, `-`, `:`, `：`, parentheses, and brackets.
   - Treat an event as a possible duplicate when it has the same `game` and `server`, a highly similar name, and either:
     - the same `end_time`
     - overlapping start/end times
     - one exact time and one omitted `start_time` but the end times are close
   - Do not automatically write possible duplicates. Report the existing event ID, candidate event, and reason, then ask Jerry whether to skip, replace, or keep both.
   - During weekly automation, skip possible duplicates instead of asking, and report them as needing confirmation.

5. Edit `data/events.json`.
   - Keep UTF-8 without BOM.
   - Preserve existing user events and unrelated formatting as much as practical.
   - Use unique IDs:
     - `{game-key}-{server-key}-{slug}-{yyyy-mm}`
     - example: `ba-jp-normal-drop-2x-2026-07`
   - Use configured `webhook_key`.
   - Include `source_url` when obtained from a page.
   - Include `notes` for user-provided times, omitted start times, or source caveats.

6. Validate.
   - Run:
     - `.\.venv\Scripts\python.exe -m src.main --validate-only`
     - `.\.venv\Scripts\python.exe -m unittest discover -s tests`
   - Run at least one dry-run around a new event's 24h or 6h threshold:
     - `.\.venv\Scripts\python.exe -m src.main --dry-run --now <ISO_JST_TIME>`

7. Secret safety check.
   - Use `git grep`, not broad `rg -uu`, to avoid printing local `.env` secrets:
     - `git grep -n -E "discord\.com/api/webhooks|DISCORD_WEBHOOK_URL[[:space:]]*=[[:space:]]*https" -- .`
   - A fake test webhook URL in tests is acceptable.

8. Commit and push.
   - Stage only intended files:
     - `git add -- data/events.json`
   - Use a clear commit message:
     - `Add <game> event reminders`
     - `Update weekly game event reminders`
   - Push:
     - `git push origin main`

9. Final response.
   - Summarize added/updated events.
   - Include validation results and commit hash.
   - Mention any events skipped due to unclear times.

## Weekly automation behavior

For scheduled weekly runs:

- Search all configured games in `references/games.md`.
- Add only ready events with clear end times.
- Run the duplicate check before writing. Skip exact duplicates; report possible duplicates for Jerry confirmation.
- If nothing changes, do not commit; report that no update was needed.
- If sources are blocked or times are ambiguous, leave files unchanged and report what needs user confirmation.
- Push only after validation passes.
