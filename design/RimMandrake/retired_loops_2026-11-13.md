# Retired 2026-11-13: Relentless per-ticket work, the Artisan loops, the Whittle loops

## His words

The owner, 2026-11-13 about 3:40 PM PST:

> "I want to ensure right now that the old Relentless per-ticket work will NOT come back on, nor will the Artisan or Whittle loops. Please don't just "pause" things there, stop those processes such that there's nothing to resume, fully documented of course. Then release all the clones etc. so that they aren't being held by those old processes, if they were that is. Clean up anything you need to clean up, get us back healthy and ready for a new way to work."

The new way to work is the Maturation Pipeline (`design/specs/2026-11-13-maturation-pipeline.md`), which is still in design.
Until it ships, the Conductor launches builds itself as detached helpers (`src/RimMandrake/rimflow/detached_helper.py`, clones from the pool).

## What each thing was

- **Relentless per-ticket work.**
  - `rm-relentless.timer` ticked `src/RimMandrake/rimflow/relentless.py`. Each tick took ledger items, leased them to BENCH, gave each one a clone (`/home/mandrake/rm/relentless/clones/*`) and ran Builder and Judge workers in `rm-relentless-job@<item>` units.
  - Helpers around it:
    - `rm-relentless-release.timer` (lease release);
    - `rm-relentless-wake.path` and `.service` (woke the tick when the queue changed);
    - `rm-store-ledger-diff.timer` (a nightly comparison of the store against the ledger).
- **Artisan loops.**
  - These were the `ralph_*` loops: Claude sessions re-run on one art or biome goal in `rm-ralph-*` transient units, restarted from saved `.service.saved` recipes.
  - `rm-artisan-now.timer` drew their status page.
- **Whittle loops.**
  - `whittle-claude@<SEAT>` services on Archmagi and Steve. Each re-ran Claude in a clone under `/home/mandrake/rm/scratch/BENCH/claude-*`, held open by the Stop hook `.claude/hooks/whittle_stop.py` against `whittle/STATEMENT.md`.
  - `rm-whittle-now.timer` drew their status page.

## What was stopped (nothing to resume)

Nothing here was paused. No `timers_guard.py pause` was used, so no resume timer is armed.

- **Archmagi.** Each of these units was stopped, disabled, had its unit file moved out of `~/.config/systemd/user`, and was masked:
  - `rm-relentless.timer`/`.service`
  - `rm-relentless-release.timer`/`.service`
  - `rm-relentless-wake.path`/`.service`
  - `rm-relentless-job@.service`
  - `rm-store-ledger-diff.timer`/`.service`
  - `rm-artisan-now.timer`/`.service`
  - `rm-whittle-now.timer`/`.service`
  - `whittle-claude@.service`

  The 19 moved unit files and drop-ins are under `D:\ClaudeWork\backups\rimmandrake\retire_loops_20261113\systemd\archmagi\`.
- **Steve.** `whittle-claude@.service` and its drop-ins were tarred to `...\retire_loops_20261113\systemd\stevedesktop\whittle-claude.tar`, removed, and masked.
- **Artisan restart recipes.** The two saved recipes, `rm-ralph-gss-steve.service.saved` and `rm-ralph-pyrelands.service.saved`, were moved to `...\retire_loops_20261113\saved_recipes\`. No `rm-ralph-*` unit was loaded.
- **Whittle Stop hook.** `whittle/STOP` now exists. While it exists the hook holds no session open, even one started with `WHITTLE=1`.
- **Monitoring.**
  - The units are listed in `src/RimMandrake/rimflow/live_retired.txt`, so deadman no longer reopens promises on them.
  - `ops_clocks` lists them as outside its watch.
  - `ops_watch` reads `rm-relentless.timer` there and judges the `relentless.*` points as retired, not failing (commit 5941703eea).
- **Ledger.**
  - The 162 BENCH items Relentless had leased were reclaimed to ready. Four of them needed `--owner-said`, because the store still carried them.
  - Three items held by dead Whittle seats were reassigned to BENCH (739db6d73b).
  - The two builds the Conductor launched as detached helpers were left alone.
- **Clones.**
  - The finished detached clones were returned to the pool with `detached_helper.py return`.
  - The five Whittle clones in `/home/mandrake/rm/scratch/BENCH/claude-*` were removed. First, their unpushed backup branches were bundled to `...\retire_loops_20261113\clones\*.unpushed.bundle` and verified.
  - The four `ralph_*` clones there are kept for the owner to decide on.

## Where state and code live (code is NOT deleted in this pass)

- **Code.** It stays as it was:
  - `src/RimMandrake/rimflow/relentless.py` and `relentless_rules.json`;
  - the repo's unit copies in `src/RimMandrake/Utils/systemd/`;
  - the skills `relentless`, `relentless-pipeline`, `artisan*` and `whittle`;
  - `.claude/hooks/whittle_stop.py`.

  An agent could still run `relentless.py` by hand. Nothing does so on a schedule.
- **State.** It stays as history:
  - the Relentless store at `/home/mandrake/rm/relentless/store`, with item states frozen as they were;
  - `whittle/`;
  - the ralph work dirs under `D:\ClaudeWork\rimmandrake\ralph_*`.
- **Design.**
  - `design/RimMandrake/relentless_*.md`
  - the ralph loop design
  - this file

## What was left running

Designer, Operations and the Conductor seats are still running, along with:

- `ops_watch`, the metronome, the canon sweep, the nightly selftests, deadman and the login watch;
- the publish and ledger belt, the mirror and the art daemons;
- `rm-findings-judge.timer`;
- `detached_helper.py` with the clone pool.

`rm-relentless-job@` is masked, but `detached_helper.py` does not use it: it starts its own `rm-detached-*` transients.

## Check that it is still off

This is a check, not a resume recipe. Every line should print `masked`, `inactive`, or nothing:

```
for u in rm-relentless.timer rm-relentless.service rm-relentless-release.timer rm-relentless-wake.path \
         rm-relentless-job@.service rm-store-ledger-diff.timer rm-artisan-now.timer rm-whittle-now.timer \
         whittle-claude@.service; do echo "$u $(systemctl --user is-enabled $u 2>&1) $(systemctl --user is-active $u 2>&1)"; done
ssh stevedesktop systemctl --user is-enabled whittle-claude@.service       # masked
systemctl --user list-units --all --no-legend 'rm-ralph-*' 'whittle-claude@*' 'rm-relentless-job@*'   # empty
grep -c 'owner 2026-11-13' src/RimMandrake/rimflow/live_retired.txt         # 9
test -f whittle/STOP && echo STOP-present
python3 src/RimMandrake/rimflow/detached_helper.py status --all             # only Conductor-launched helpers
```

The ledger item `RIMMANDRAKE_RETIRE_RELENTLESS_ARTISAN_WHITTLE_NOTHING_TO_RESUME` carries his words and stays open until a recurring checker makes this check by itself.
