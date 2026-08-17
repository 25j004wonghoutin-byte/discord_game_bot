# Configured games

Use this reference with `game-event-updater`.

## Repository

- Local repo: `C:\Users\Jerry\Desktop\WORKSPACE\game_discord_bot`
- Event file: `data/events.json`
- Branch: `main`
- Remote: `origin`

## Common schema

```json
{
  "id": "game-server-slug-yyyy-mm",
  "game": "Display name",
  "server": "Server label",
  "event_name": "Event name",
  "start_time": "YYYY-MM-DDTHH:MM:SS+09:00",
  "end_time": "YYYY-MM-DDTHH:MM:SS+09:00",
  "source_url": "https://example.com/source",
  "webhook_key": "KEY",
  "enabled": true,
  "notes": "Times are treated as JST (+09:00)."
}
```

`start_time` and `source_url` are optional. `end_time` must be exact.

## Games

### NTE

- Game display: `NTE 異環`
- Server: `Asia-Japan`
- Timezone: JST `+09:00`
- webhook_key: `NTE`
- Source preference:
  1. GameWith NTE event page
  2. Official NTE notices if available
- Existing source URL: `https://gamewith.jp/nte/559568`
- Candidate exclusions:
  - Skip the event named `オープン記念`.
  - Skip any event whose name ends with `ギフト` (for example, `強がりギフト`).
  - Apply these exclusions before duplicate checks. Do not add excluded events or report them as ambiguous candidates.

### Blue Archive

- Game display: `Blue Archive`
- Server: `日服`
- Timezone: JST `+09:00`
- webhook_key: `BA`
- Source preference:
  1. Blue Archive JP official news
  2. Game8 Blue Archive event schedule
  3. GameWith Blue Archive notices
- Add event campaigns and major event periods.
- Do not add gacha banners unless Jerry explicitly requests gacha reminders.

### Honkai Star Rail

- Game display: `崩壊：スターレイル`
- Server: `Asia-Japan`
- Timezone: JST `+09:00`
- webhook_key: `HSR`
- Source preference:
  1. Official HoYoLAB / Star Rail notices where accessible
  2. GameWith 崩壊：スターレイル攻略ガイド

### GBF

- Game display: `GBF`
- Server: `Japan`
- Timezone: JST `+09:00`
- webhook_key: `GBF`
- Source preference:
  1. Official Granblue Fantasy news
  2. GameWith / Kamigame event schedule pages
- Add collaboration and event periods.
- Do not add draw banners unless Jerry explicitly requests gacha reminders.

## Formatting notes

- Notification grouping is controlled by `webhook_key`.
- The bot formats messages as:

```text
[活動結束提醒] {game} ({server})
活動: {event_name}
終了時間: mm/dd HH:MM [JST]
提醒: 距離結束還有 HH時間MM分
```
