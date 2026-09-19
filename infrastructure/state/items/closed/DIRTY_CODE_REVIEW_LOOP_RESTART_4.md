# DIRTY_CODE_REVIEW_LOOP_RESTART_4

Continuity note for resuming the standing dirty-code-review loop (FOUNDRY).
Successor to `DIRTY_CODE_REVIEW_LOOP_RESTART_3` (resumed this session,
closed below).

## State at handoff

`infrastructure/state/CODE_REVIEW_STATUS.json`: **296 clean entries** (was
293 at the last restart). 655 `.cs`/`.py` files total under `src/` — still
well under half clean; this is explicitly multi-session, never claim it's
finished.

This session's wave (4 files, fanned out as parallel subagents — 2 opus for
central/live-companion files, 2 sonnet for workaday single-mod files, per
the model ladder in `Agent_Policy.md`):

- **`broadcast.py`** — 3 real bugs fixed (ledger stamp lost when nobody was
  listening; `--to`/`--from` missing a value became message text and
  silently changed who was reached; a cwd-less session record misread as
  in-repo). **Left DIRTY on purpose** — the file also implements
  `GAME_STATE_BROADCAST_NARROWING_1`'s narrowing, which the owner ruled
  "leave it as is" on while the item record says it was never adopted. That
  mismatch needs an owner call before this file can be marked clean; don't
  resolve it unilaterally.
- **`DefDumper.cs`** — 6 real bugs fixed, all in the "dump claims more than
  it captured" class (phantom manifest entries, vanished pass-1 failures,
  an overcounted `defTypeCount`, two live routes back to the original
  filename-collision bug, three new `animals.json` gap-naming fields, an
  unrecognised dump mode falling through silently). Built clean (0/0),
  deployed, marked CLEAN.
- **`PitDebugActions.cs`** — `ReportPit`'s standing-mass sum was missing the
  same own-faction exclusion the real `CompPitCoverTrigger.RunScan` applies,
  so the debug report could claim `WOULD_SPRING=true` for a load the real
  trigger would never spring on. Built clean, deployed, marked CLEAN. Also
  noted, not fixed (design ambiguity, not a crash): base-pit debug actions
  match `is Building_OpenPit`, which also matches the `Building_PitCell`
  subclass — flagged for a judgment call, not acted on.
- **`JawaRules.cs`** — full re-review, no real bugs found (reviewer
  cross-checked every claim against live decompiled 1.6 source via RimSage).
  Marked CLEAN, no edit needed.

Everything through commit `1c0aeca4` (rebuilt DLLs) / `de83ee4d` (ledger) is
committed and pushed to `origin/main`.

## Doctrine carried forward, still true

**Check reachability before reviewing** (owner, 2026-09-03, in CLAUDE.md
under "Code isn't clean until a review says so"). Every review-agent prompt
must state, or have the coordinator confirm before dispatch, that the target
file is still live (an active mod's packageId in the real `ModsConfig.xml`,
a `.csproj` Compile include, a doc/hook/script reference, or a CLI entry
point) — a naive grep can call a live file dead, and a file only a human
runs by hand, or a tool reached only via reflection/string lookup, can look
unused and not be. This session's 4 files were all pre-confirmed live by the
coordinator before dispatch, not re-checked by each subagent (saved a round
trip each — fine to keep doing that once the coordinator has actually
checked, not skipped).

Fix ≠ clean. Only a full-file review with zero (or trivial) findings, or a
found-and-fixed pass where the fix is itself committed and (for C#) rebuilt,
earns `mark-clean`.

Subagents never `git commit` `CODE_REVIEW_STATUS.json` — only `mark-clean`
(a flock'd disk write), and only after their OWN fix is committed (mark-clean
refuses on uncommitted changes). The coordinator is the sole committer of
that one file, once per wave, after a fresh `git pull`/rebase.

Central/critical files (live game companions, anything in the game-state or
cross-window broadcast path) get `model: opus`; workaday single-mod files run
fine at `sonnet`.

**Every `Agent` call needs an explicit `model`** — `block_agent_without_model.py`
refuses otherwise.

In a shared worktree, `git stash push -- <exact paths>` (list every path
explicitly, including `infrastructure/state/codebase_health_last.json` if it
has flapped — it is never FOUNDRY's to commit, but it still blocks a rebase)
before `pull --rebase`, then pop and commit only the paths that are actually
yours. `.git/index.lock` collisions from a concurrent window's own git
command are normal here — wait a few seconds and retry, don't force-remove
the lock.

**A C# fix is not real until it's rebuilt.** `"%USERPROFILE%\.dotnet\dotnet.exe"
build <csproj> -c Release` (Windows-native, cannot take a `/mnt/d` path — use
the `D:\...` form), then `deploy_custom_mods.py --mod <name> --apply`, and
commit the resulting `.dll` alongside the source fix in the same wave. The
DLL can only be written while the game is not running.

## Filed decision items still open for the owner (untouched this session)

`DESIGNATE_BATCH_OVER_DESIGNATES_1`, `BRIDGETOOLS_TILE_LAYER_DROPPED_1`,
`REOPEN_DESTROYS_CLEANCOUNT_STREAK_1`, `INHABITED_CHARACTERAPPLIER_GENE_LOSS_1`,
`RIVER_LINK_ORDER_SELFTEST_DRIFT_1` (blocked, not decision-pending),
`GAME_STATE_BROADCAST_NARROWING_1` (the mismatch noted above needs a fresh
look — the item record and the shipped code disagree about what was ruled).

## Bridgetools DLL status (unchanged this session — not touched)

`MapTools.cs` round 5 already found ~4 more minor items, judged a 6th pass
warranted whenever bridgetools comes back up in rotation.
`VehicleAerialTools.cs` — ruled accept-as-tracked-owed, not worth a 6th
round; don't reopen without a reason.

## Next-session priority order

1. **Keep broadening beyond bridgetools/rimflow.** Sample the next batch of
   NO-ENTRY files the same way this session did:
   `python3 -c "import json; print(len(json.load(open('infrastructure/state/CODE_REVIEW_STATUS.json'))))"`
   for a fast count, `code_review_status.py check <path>...` to confirm
   DIRTY/NO-ENTRY on candidates, size/centrality to pick the wave, reachability
   check before dispatch, model tier by centrality.
2. MapTools.cs 6th round, whenever bridgetools comes back up in rotation.
3. Scale: 655 `.cs`/`.py` files under `src/`, 296 clean (~45%). Still
   explicitly multi-session per the owner — never claim it's finished.
