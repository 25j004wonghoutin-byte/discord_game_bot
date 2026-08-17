param(
    [string]$CodexHome = "$env:USERPROFILE\.codex"
)

$ErrorActionPreference = "Stop"

$repoRoot = Split-Path -Parent $PSScriptRoot
$sourceSkill = Join-Path $repoRoot "codex\skills\game-event-updater"
$targetSkills = Join-Path $CodexHome "skills"
$targetSkill = Join-Path $targetSkills "game-event-updater"

if (-not (Test-Path -LiteralPath $sourceSkill)) {
    throw "Skill source not found: $sourceSkill"
}

New-Item -ItemType Directory -Force -Path $targetSkills | Out-Null

if (Test-Path -LiteralPath $targetSkill) {
    $backup = "$targetSkill.backup-$(Get-Date -Format yyyyMMdd-HHmmss)"
    Move-Item -LiteralPath $targetSkill -Destination $backup
    Write-Host "Existing skill backed up to: $backup"
}

Copy-Item -LiteralPath $sourceSkill -Destination $targetSkill -Recurse

Write-Host "Installed skill to: $targetSkill"
Write-Host ""
Write-Host "Next step:"
Write-Host "Open Codex on the new computer and recreate the local automation using:"
Write-Host "  codex\automations\weekly-game-event-updater.prompt.md"
Write-Host ""
Write-Host "GitHub Actions schedules do not need this script; they run from GitHub once the repository secrets exist."
