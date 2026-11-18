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

## proof (corrected 2026-11-17, drain of the retired judge)
Acceptance clause 1 was re-measured here. It FAILS. Instrument:

    git grep -I -l -i -e 'dev\\Rimworld' -e 'dev/Rimworld' -e 'dev-Rimworld'

The doubled backslash is load-bearing: git grep's default BRE reads `dev\Rimworld` as `devRimworld`
and under-reads by 7 files. Sanity probes run with the same instrument in the same call: the new name
`dev\\RimMandrake`/`dev/RimMandrake` returns 1199 files (the instrument can see), and
`dev\\RimNoSuchThing` returns 0 (it is not matching everything).

Measured 2026-11-17 on the drain clone at the branch point:
  86 tracked files still carry an old-name path
  44 of them are BENIGN by this item's own rule (`infrastructure/state/ledger`,
     `infrastructure/state/items/closed`, `conversations`, `infrastructure/state/code_review`: never edit)
  42 non-benign remain, of which these are LIVE TOOLING — Work step 1's target, a script or
  instruction file that would act on the old path:
    .claude/hooks/block_shared_tree_merge.py
    .claude/hooks/selftest_block_blanket_git_stage.py
    .claude/hooks/selftest_block_shared_tree_merge.py
    infrastructure/output/pawn_flavor_phase2_census_gen.py
    src/RimMandrake/Utils/artpipe/orphan_masters.py
    skills/generating-rimworld-sprites/references/traps.md
    skills/rimworld-modding/SKILL.md
  (two further non-benign hits are frozen evidence, not tooling: a pulse time-ledger replay jsonl and
  `whittle/amend_hook_harden_swept_a_neighbour/evidence/.../hook_selftest.txt`)
  The top live BREAKS the Scan named — ~70 csproj build lines, ~20 `bridgetools/*.py` sys.path
  inserts, `install_wt_seat_profiles.py`, `install_fleet_shortcut.py`, `claude_bounded.sh`,
  `skills/validate_skills.py`, `infrastructure/dashboards` — now read ZERO. That part of step 1 landed.
  The remainder is hooks, one generator, one artpipe tool and two skills.
Evidence: /Users/mandrake/ClaudeWork/scratch/rm-drain-logs/proofs/REPO_RENAME_SYMLINK_RETIRE_1.txt

## why this is ready, not done
Three reasons, and the first is the only one a desk worker can clear:
1. Acceptance clause 1 is red: 7 live-tooling files still carry the old path. Repoint them (prefer
   `git rev-parse --show-toplevel` or a repo-relative path over a second absolute literal), then
   re-run the instrument above WITH both sanity probes and state the three counts.
2. Clause 2 (symlink removed) is a Windows filesystem action on `D:\Luke\dev\Rimworld`. UNMEASURED
   from here: this clone is on a Mac with no `/mnt/d` and no `C:\`.
3. Clause 3 (fresh session, `lodestar-sync.timer`, artpipe daemon) is a live reading on the Archmagi
   host. UNMEASURED from here for the same reason.

Next worker: do (1) offline in the real repo; (2) and (3) need the Windows host and must be read
there, after (1), in that order — removing the link before the last live BREAKS is repointed is what
breaks the daemon.
