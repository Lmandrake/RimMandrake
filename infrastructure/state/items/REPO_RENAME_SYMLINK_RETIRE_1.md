# REPO_RENAME_SYMLINK_RETIRE_1 — retire the Rimworld -> RimMandrake symlink

## Context
The repo was renamed `Rimworld` -> `RimMandrake` on 2026-09-30 (origin is `git@github.com:Lmandrake/RimMandrake.git`; Lodestar plans `rename-rimmaster-archmagi-20260930` and `rename-rimmaster-macs-20260930`). The symlink `D:\Luke\dev\Rimworld -> D:\Luke\dev\RimMandrake` (made 2026-09-30 22:39) keeps old paths working. The owner asked for this item and wants the link eventually retired (his words, relayed by BENCH, not quoted via `--owner-said` because the guard needs a same-session typed quote): the repo got renamed, a symlink keeps us working, we want to retire that, ticket it out. He also reports "a whole bunch of RimWorld vs. RimMandrake vs. RimMaster confusion".

## Scan
Full report: `D:\Luke\dev\RimMandrake\Transient\repo_rename_scan_2026-09-30.md` (copy it out of `Transient/` if this item outlives ~14 days).

Tracked files (excluding `infrastructure/artpipe/`, `Transient/`): 1,178 hits in 573 files = **764 BREAKS** (443 files) / 265 MISLEADS / 149 BENIGN (ledger, handoffs, closed items: never edit).
BREAKS by group: `.claude/` 3 (docstring/selftest strings), live tooling 237 / 186 files, `world/_*` one-off scripts 416, `design/**` manifests 108.
Top live BREAKS: ~70 csproj `dotnet.exe build D:\Luke\dev\Rimworld\src\...` lines (e.g. `src/RimMandrake/FlowWorks/Source/RimMandrake_FlowWorks.csproj:25`); `src/RimMandrake/Utils/install_wt_seat_profiles.py:83,84,123,133` and `install_fleet_shortcut.py:53,54` (would regenerate the old Windows Terminal paths); `src/RimMandrake/Utils/claude_bounded.sh:91`; `skills/validate_skills.py:16`; about 20 `src/RimMandrake/bridgetools/*.py` with `sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")`; `infrastructure/dashboards/hub/data/publish_ready.json` (16 source paths).
Outside the repo: `~/.claude` 0 hits and no stale `-mnt-d-Luke-dev-Rimworld` project dir; systemd `lodestar-sync.service`, cron, and all 285 Windows scheduled tasks 0 hits; git worktrees 0 (59 repaired). Lodestar BREAKS: `D:\Luke\dev\.lodestar\managed.json:33`, `.lodestar\sync-status.json:354` (derived), `Lodestar/loops/rimworld-twilight-floor.md:7`, two journal handoff `repo:` lines. Windows-side `C:\Users\Mandrake\.claude\CLAUDE.md:14` MISLEADS. Orphan dir `D:\Luke\dev\Rimworld-wt-sightblock` (only `infrastructure/`, no `.git`) is a delete candidate.

## RimMaster finding
Not a typo: it is the repo's intermediate name. GitHub was `Lmandrake/RimMaster`, the Mac checkouts `~/dev/RimMaster`, this machine `~/dev/Rimworld`; Lodestar's repo id stays `rimmaster` on purpose. Live residue: `.bridge.eld:13` `:station RIMMASTER`, `.gitignore:1` comment, one selftest string. Mac convergence is unverified from here.

## Work
1. Repoint every live BREAKS hit (use `/mnt/d/Luke/dev/RimMandrake` / `D:\Luke\dev\RimMandrake`; prefer repo-relative or `git rev-parse --show-toplevel` where a script can). Skip BENIGN history. One-off `world/_*` scripts may be left or deleted by judgement, state which.
2. Fix Lodestar-owned path state (`managed.json`, the twilight-floor loop, handoff `repo:` lines) via Lodestar's own tooling, not by hand where it regenerates.
3. Delete the orphan `Rimworld-wt-sightblock` dir after looking at it.
4. Remove the symlink from Windows (`Remove-Item`, never recurse into it: `rmdir` on the link only).

## Acceptance
- Re-measure with the scan patterns: zero BREAKS hits (state the instrument and a sanity probe).
- Symlink removed.
- A fresh Claude session in the repo works, the hourly Lodestar sweep (`lodestar-sync.timer`) completes, and the artpipe daemon still runs.
