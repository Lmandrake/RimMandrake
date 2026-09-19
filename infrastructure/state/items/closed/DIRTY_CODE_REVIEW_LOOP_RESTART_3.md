# DIRTY_CODE_REVIEW_LOOP_RESTART_3

Continuity note for resuming the standing dirty-code-review loop (FOUNDRY),
written ahead of an agent reboot, 2026-09-03. Successor to
`DIRTY_CODE_REVIEW_LOOP_RESTART_2` (resumed this session, closed below).

## State at shutdown

Ledger: 293 clean entries in `infrastructure/state/CODE_REVIEW_STATUS.json`
(was 285 at the last restart). 654 `.cs`/`.py` files total under `src/` — still
well under half clean; this is explicitly multi-session, never claim it's
finished.

Everything through commit `11be1f36` (the doctrine note below) is committed
and pushed to `origin/main` — nothing of this session's review work is
uncommitted. `git status` at handoff shows only two files dirty that are NOT
mine: `infrastructure/state/codebase_health_last.json` and
`infrastructure/state/items/FLUID_CANAL_FLOOD_LIVE_CHECK_1.md`, both BENCH's
live concurrent work in the shared worktree — leave them alone.

## New doctrine this session — must persist across the restart

**Check reachability before reviewing.** Owner, 2026-09-03: "we have some old
scripts lying around that aren't even important anymore." Recorded in
`CLAUDE.md` under "Code isn't clean until a review says so" (commit
`11be1f36`). Every review-agent prompt from here on must include, as step 1
before the full-file read: is this file still imported/invoked/referenced
anywhere live (importers, `python3 <it>` in a doc/hook/script, a CLI entry
point, `.csproj` inclusion, or — for reflection-registered bridge tools — the
tool-name string, not just C# call sites)? If no live reference turns up,
don't spend the review budget on a full read — report it as a DEAD-FILE
candidate instead, naming exactly what was checked. **Never delete on a grep
alone** — verify, then file it or drop it. A file only a human runs by hand,
or a tool reached only via reflection/string lookup, can look unused to a
naive grep and not be. Bake this into the prompt text itself; a fresh
subagent won't re-read CLAUDE.md unprompted.

## Permanent rules carried forward from RESTART_2 (still true)

- Fix ≠ clean. Only a separate follow-up review with zero (or trivial)
  findings earns `mark-clean`.
- Subagents never `git commit` `CODE_REVIEW_STATUS.json` — only `mark-clean`
  (a flock'd disk write). The coordinator is the sole committer of that one
  file, once per wave, after a fresh `git pull`.
- Central/critical files (anything live infrastructure everyone depends on —
  `rimflow/*.py` counted as this tier this session) get `model: opus`; fall
  back to `sonnet` after repeated HTTP 529s, and never `mark-clean` on a
  fallback pass. Workaday single-purpose tools (`worldview.py`,
  `animal_contact_sheet.py`) ran fine at `sonnet`.
- **Every `Agent` call needs an explicit `model`** — `block_agent_without_model.py`
  refuses otherwise. Learned the hard way this session (two calls blocked,
  redispatched with `model: sonnet`).
- In a shared worktree, `git stash push -- <exact paths>` before
  `pull --rebase`, then pop and commit only the paths that are actually
  yours. `codebase_health_last.json` flaps on nearly every git operation in
  this repo (looks hook-driven) — it is never FOUNDRY's to commit; always
  leave it for whoever owns it. `.git/index.lock` collisions from a
  concurrent window's own git command are normal in this shared worktree —
  wait a few seconds and retry, don't force-remove the lock.

## New finding this session: the ledger's double-terminal-transition bug was live and had already fired

`rimflow/model.py`'s `_transition` short-circuited on `state == item.state`
*above* the terminal-state check, so a second `close`/`drop`/`supersede` on an
already-terminal item was a silent no-op that still let `_apply_item_verb`
overwrite fields (`closed_sha`, `superseded_by`, the `blocked` flag) from the
discarded event. Fixed at `3089b753`. It had already fired 4 times in the
live ledger before the fix (`CUT_LIST_ONE_READER_1`, VEHICLE_FRAMEWORK_AERIAL_DEBUG_1`,
`REFMATCH_THRESHOLDS_CALIBRATE_1`, `IMPERIAL_CAST_BINDING_1`) — three were
already correctly resolved by an unrelated seat-ownership guard and needed no
action; one (`CUT_LIST_ONE_READER_1`) was genuinely corrupted, displaying a
stale `PENDING` closed_sha instead of the real `bdd7e682`. Corrected with a
`note` event at `5eced8aa`, following the exact precedent
`VEHICLE_FRAMEWORK_AERIAL_DEBUG_1` had already set on 2026-08-30 for the same
symptom (ledger is append-only — a correction is a new `note`, never an edit).
**If any other item ever displays a `PENDING`/`pending` closed_sha, that's the
same bug's fingerprint — check the raw ledger for a same-item repeat close
within seconds of the first, and note-correct it the same way.**

## Bridgetools DLL status (54 `.cs` files, `src/RimMandrake/bridgetools/JawaBench.BridgeTools/`)

This session cleaned 3 more (EventTools, IncidentTools, JobTools) via opus
full re-reviews — 13, 9, and 11 real bugs respectively, all fixed. Detail is
in the commit messages (`8cbe627d`+`275928c6`, `1a5f8ecf`+`1acd1615`,
`482d36ef`+`86ac78d7`).

Still open:

- **MapTools.cs** — round 5 done this session (`44fc3ddc`, 20 more bugs
  fixed, both known-outstanding `Enum.Parse` issues confirmed and closed).
  Deliberately left DIRTY — reviewer found ~4 more minor items (non-edifice
  displaced-things reporting in `connect_cells`, `get_terrain_layers`
  truncation with no flag, `set_fog` error-precedence, `map_zones` duplicate-
  label handling) and judged a 6th pass warranted. Do it next time this file
  comes up.
- **VehicleAerialTools.cs** — 5 sonnet rounds, 5-for-5 real bugs, all the same
  orphaned-Pawn/vehicle shape. **Ruled this session: accept as tracked-owed,
  not worth a 6th round** — diminishing returns, the pattern is well
  understood and documented. Don't reopen this ruling without a reason.

## rimflow itself — now clean (was the top of last session's priority list)

`rimflow/cli.py`, `rimflow/model.py`, `rimflow/priority.py` all reviewed
full-file this session and marked CLEAN (`26ae3a31`+`3d60b716`, `3089b753`).
Between them: 11 real bugs, the double-terminal-transition bug above being
the most consequential, plus a stale-world write race in `cli.py` (a command
reads the ledger, does slow work, then writes — another window's write in
that gap was invisible to the terminal/duplicate-id guards; fixed by a fresh
replay immediately before write). `_transition`'s remaining known gap:
`check()`+`append()` are still not atomic together — would need a `flock`
held across both in `model.py`'s primitives. Noted, not fixed, out of scope
for a review pass (it's a design change, not a bug fix).

Also worth knowing for next time anyone runs `selftest_cli.py`: it uses a
**fixed** scratch dir, `<repo>/.rimflow_selftest_cli`, and `fresh()` rmtree's
it — two windows/agents running it at once destroy each other's scratch
ledger mid-test and produce spurious failures. Not fixed (lives in the
selftest itself, out of scope for the files reviewed). If you see a wall of
"has never been filed" failures, suspect a concurrent run before suspecting
your change.

## `worldview.py` / `animal_contact_sheet.py` — also now clean

Both reviewed and marked CLEAN this session (`d4993d9e`, `d17af88d`).
`worldview.py`'s finding is worth a second look by whoever owns Ash'karr
render review: the mutator layer has been counted in the legend header since
commit `873d08f9` but never actually drawn on the map until this session's
fix — any earlier rendered review artifact that cites "N mutated tiles" was
showing a legend claim with nothing on the map to back it. Not re-litigating
past owner decisions made from those renders — just flagging that the visual
evidence behind them was incomplete.

## Filed decision items still open for the owner (untouched this session)

`DESIGNATE_BATCH_OVER_DESIGNATES_1`, `BRIDGETOOLS_TILE_LAYER_DROPPED_1`,
`REOPEN_DESTROYS_CLEANCOUNT_STREAK_1`, `INHABITED_CHARACTERAPPLIER_GENE_LOSS_1`,
`RIVER_LINK_ORDER_SELFTEST_DRIFT_1` (blocked, not decision-pending).

## Next-session priority order

1. **Broaden beyond bridgetools/rimflow** — this session's priority-3 list is
   now clear. Pick the next batch of `NO ENTRY` files from `src/` by the same
   method: `python3 -c "import json; print(len(json.load(open('infrastructure/state/CODE_REVIEW_STATUS.json'))))"`
   for a fast count (the `list` subcommand is slow — timed out at 120s this
   session; don't wait on it), then `code_review_status.py check <path>...`
   on candidate files to confirm DIRTY/NO-ENTRY before spending an agent on
   one. **Apply the new reachability-check doctrine above to every one of
   these** — some are very likely dead scripts nobody has touched in months.
2. MapTools.cs 6th round (the ~4 minor items named above), whenever bridgetools
   comes back up in rotation.
3. Scale: 654 `.cs`/`.py` files under `src/`, 293 clean (~45%). Still
   explicitly multi-session per the owner — never claim it's finished.
