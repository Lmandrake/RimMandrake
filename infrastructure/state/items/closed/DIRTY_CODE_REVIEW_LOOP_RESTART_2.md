# DIRTY_CODE_REVIEW_LOOP_RESTART_2

Continuity note for resuming the standing dirty-code-review loop (FOUNDRY),
written ahead of an imminent agent shutdown, 2026-09-03.

## State at shutdown

Ledger: 285 clean entries in `infrastructure/state/CODE_REVIEW_STATUS.json`.
Everything through commit `51a39209` (WorldTools.cs round 4) is committed and
pushed to `origin/main` — nothing of this loop's work is uncommitted.

Artifact republished at 285 clean / 225+ real bugs found:
https://claude.ai/code/artifact/0433df46-cb58-4c81-81ba-3d6f1c0c880b

Permanent rules that must persist across the restart:
- Fix ≠ clean. Only a separate follow-up review with zero (or trivial)
  findings earns `mark-clean`.
- Subagents never `git commit` `CODE_REVIEW_STATUS.json` — only
  `mark-clean` (a flock'd disk write). The coordinator is the sole
  committer of that one file, once per wave, after a fresh `git pull`.
- Central/critical files get `model: opus`; fall back to `sonnet` after
  repeated HTTP 529s, and never `mark-clean` on a fallback pass.

## Lesson from this session's restart handling

After a coordinator-side pause, a background agent showing "no commit yet"
is **not** proof it's lost — it may just be slow. This session redispatched
a duplicate MapTools.cs review before the original (`a3b616b9683570438`)
actually landed; caught it via a stand-down `SendMessage` before the
duplicate committed anything, so no harm done. Check the agent's own
task-notification status (`failed` vs. still running) before redispatching
— don't infer "orphaned" from commit absence alone.

## Bridgetools DLL status (50 .cs files, `src/RimMandrake/bridgetools/JawaBench.BridgeTools/`)

41 clean, 9 dirty. Three files are genuine outliers — each found a real bug
on **every** follow-up round, and are tracked as owed a final high-tier
(opus) pass rather than declared done on a shaky sonnet "nothing found":

- **MapTools.cs** — 4 sonnet rounds, 17 bugs total. Opus hit HTTP 529 four
  times tonight specifically on this file. Known outstanding, not yet
  fixed: bare `Enum.Parse` (no `IsDefined` check) on `quality` (~line 780)
  and `gasType` (~line 1413) — `gasType` confirmed via `GasGrid.AddGas`
  source to silently no-op on an undefined value while the tool's loop
  still counts it as `changed++`.
- **WorldTools.cs** — 4 sonnet rounds, 17 bugs total. Latest round:
  `WorldTileValidate` silently deflated `matchPct` on bad CSV rows;
  `WorldLinksClear` and `WorldFeaturesSet` both had zero-trace
  id-vanishing bugs (no `errors[]`/`notFound[]` at all). Ruled **not** a
  bug: several other `Set` tools' hardcoded `success = true` convention —
  that's a deliberate, documented design (partial-failure detail lives in
  the array, not in `success`); don't "fix" it broadly, that's scope creep.
- **VehicleAerialTools.cs** — 5 sonnet rounds, 5-for-5 real bugs, all the
  same shape: a Pawn or vehicle silently orphaned from the save when a
  mid-tool spawn or container-add fails. Judgment call for whoever
  resumes: push one more exhaustive round, or accept as tracked-owed —
  real diminishing-returns risk here.
- **EventTools.cs, JobTools.cs, IncidentTools.cs** — also owed opus
  re-checks; sonnet-covered only so far, real fixes landed and correctly
  left dirty.

## Filed decision items still open for the owner (untouched this session)

`DESIGNATE_BATCH_OVER_DESIGNATES_1`, `BRIDGETOOLS_TILE_LAYER_DROPPED_1`,
`REOPEN_DESTROYS_CLEANCOUNT_STREAK_1`, `INHABITED_CHARACTERAPPLIER_GENE_LOSS_1`,
`RIVER_LINK_ORDER_SELFTEST_DRIFT_1` (blocked, not decision-pending).

## Next-session priority order

1. Try opus again on MapTools.cs / EventTools.cs / JobTools.cs /
   IncidentTools.cs — it 529'd repeatedly all of tonight; may have
   recovered.
2. Decide VehicleAerialTools.cs's 6th round (push vs. accept-and-move-on).
3. Broaden beyond bridgetools: `src/RimMandrake/rimflow/cli.py`,
   `rimflow/model.py`, `rimflow/priority.py` are all `NO ENTRY` in the
   ledger and known from earlier this session to have had real wave 4-5
   fixes — each is owed a genuine follow-up that was never dispatched.
   `src/RimMandrake/Utils/worldview.py` and `Utils/animal_contact_sheet.py`
   are also `NO ENTRY` still, each with multiple rounds of real fixes
   tonight (worldview.py: 2 fixes; animal_contact_sheet.py: 3 fixes across
   2 rounds) — owed yet another follow-up before either can go clean.
4. Then a fresh Python 2nd-pass sweep of the rest of `src/` via the fast
   raw-JSON ledger technique:
   `python3 -c "import json; print(len(json.load(open('infrastructure/state/CODE_REVIEW_STATUS.json'))))"`
   rather than the slow `list` subcommand. **Be careful to distinguish
   this review-sweep's fixes from other windows' concurrent unrelated
   edits** — many `.py` files under `Utils/` show commits made today from
   BENCH's own live-game work (e.g. `ashkarr_settle.py`, `worldmap.py`,
   `world_hydro.py`, `gravship_layout.py`). Do NOT treat those as owed a
   code-review follow-up unless the commit is confirmed to actually be a
   review fix from this loop.

Scale: ~600 files under `src/`. This is explicitly a multi-session effort
per the owner — never claim it's finished.
