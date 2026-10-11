# RimPulse <-> RimFlow tie (2026-10-10)

## Owner question

**Should "to rule" show every open item rimflow says needs you, or only ones an agent explicitly
re-pointed to you with `needs --to owner`?**
- **A — every item rimflow marks needs=owner (recommended, live now).** One source of truth: the widget
  says exactly what `rimflow` says. "To rule" went from 6 to 35 rows tonight (still a 14-day window from
  when the item became yours; 25 older ones stay in rimflow only), including the four WarLab/Cradle/
  Sekkulaath design choices filed today.
- **B — only explicit `needs --to owner` asks.** Shorter list (about 6), but items filed or built as
  needing you never show. Removals stay correct either way.
Reverting to B is one filter in `owner_rulings()` (`pulse_core.py`).

## Findings

Measured 2026-10-10 ~19:30 PDT against the live daemon (`rm-pulse.service`, this clone's code).

1. **Timing is not the problem.** The collector ticks every 5 s and re-reads the ledger whenever any
   shard's (mtime, size) changes, across BOTH clones' shard dirs on local ext4
   (`/home/mandrake/rm/bench/...` and `/home/mandrake/rm/foundry/...`), union-deduped. A FOUNDRY write
   in the foundry clone is visible on the next tick without any push/pull: origin/main is not in the
   path at all. Ledger source cost: 0 ms when unchanged; a full read is ~80 ms. Every tick pushes SSE.
   So any row the classifier derives correctly appears within <=5 s of the rimflow write, either seat.
2. **The staleness is WHAT pulse derives, not WHEN.** pulse_core re-interpreted raw events for "to rule"
   (only `needs --to owner`, dropped only by a later `needs` or close/drop/supersede/reassign), while
   rimflow's own model sets `item.needs` from five verbs (`file --needs`, `spawn`, `needs`,
   `implemented` with its derived needs, `verify` advancing the cheapest owed level; L4 -> owner).
   Live divergence right now:
   - **Removal gap (the bug he saw):** `SCRAPNEST_BIRD_BASE_THEFT_1` is listed "to rule" but rimflow says
     state=built, needs=bridge since `implemented` at 14:54Z; it would have stayed listed 14 days. Same
     shape as FIREHAWK: anything that moves needs off the owner other than a `needs` verb.
   - **Addition gap:** rimflow holds 60 open items with needs=owner; pulse showed 6. Within the 14-day
     window, 29 items reached needs=owner via `file --needs owner` (22) or `implemented` (7) and never
     appeared (e.g. the four WARLAB/CRADLE/SEKKULAATH design choices filed today 20:05Z).
3. Other row sources and freshness: sessions/subagents/memwatch/hands/bridge every 5 s; kernel OOM every
   20 s; artpipe counts every 5 s (`done/` every 300 s); review sheets every 45 s and only those whose
   server answers HTTP 200 (dead servers already drop within 45 s). Hand-offs (`pulse.py hand`) never
   expire by design (owner 2026-10-10: opening dims, never removes) - not a rimflow concern.
4. Robustness gap: pulse read only the last 4 MB of each shard. FOUNDRY.jsonl is 1.9 MB today; past
   4 MB a replay would lose the `file` events and every item would vanish. Fixed by reading whole shards
   (only on change, ~80 ms).

## Options

| | option | verdict |
|---|---|---|
| 1 | Derive "to rule" from rimflow's own replay (`model.replay`, open AND needs=="owner") | **chosen** - fixes both gaps at the root, no second interpretation of verbs to drift again |
| 2 | Keep pulse's own event reading, add `implemented`/`verify`/`file` cases | rejected - the third patch to a parallel interpretation (b7e3ce88e was the second); rimflow has 5+ verbs that move `needs` and will grow more |
| 3 | rimflow post-write hook pokes the daemon (instant push) | rejected - saves <=5 s on a 5 s tick; adds a cross-process coupling in the ledger's write path |
| 4 | Fetch origin for the other seat's shard | rejected - unnecessary: the daemon already reads both clones' local shards; origin adds latency, not freshness |
| 5 | inotify on ledger files | rejected - the (mtime,size) check per tick costs 0 ms already |

## Decision

Option 1. The collector keeps its 5 s tick and re-reads only when a ledger file in either clone changes
(now including the frozen history `events.jsonl`, which the replay needs), then folds the union through
`rimflow.model.replay` once per change (~0.3 s) and caches the result. Target latency: a rimflow write in
either clone shows on the widget within one tick (<=5 s). No network fetch at all.

## Implementation

- `src/RimMandrake/rimflow/model.py`: `replay(..., observe=None)` - an optional per-event callback
  `observe(ev, world, ok)` so a reader can see WHICH event moved a projected field without re-implementing
  the fold. Default behaviour unchanged.
- `src/RimMandrake/Utils/pulse/pulse_core.py`: `read_ledger` reads whole files from rimflow's own file
  list per clone (`ledger_files`) and orders with `model.canonical_order` (content identity, the reader
  invariant); new `owner_rulings(events)` = open items with needs=="owner" + the event that made them so
  (a repeated `needs --to owner` re-asks and moves the time); `classify_ledger` uses it - the parallel
  `owner_needs` interpretation is deleted. `RULE_WINDOW_SECS` (14 d) unchanged.
- `src/RimMandrake/Utils/pulse/pulse.py`: collector signature covers `events.jsonl` + shards (mtime_ns,
  size) of both clones, caches rulings per change, reports `events` / `changed_at` in `sources.ledger`
  (that is the latency instrument).

## Tests

New in `selftest_pulse.py` (fixtures are now valid rimflow events - filed items, lowercase `owner` - because
the rows come from rimflow's replay):
- `implemented` moving needs off the owner leaves "to rule" - **FAILS on the old code** (`needs:BUILT_1` listed)
- an item FILED needing the owner is "to rule" - **FAILS on the old code**
- a clone holding the same event twice still folds to one item - **ERRORS on the old code** (no `owner_rulings`)
- a dropped item is not "to rule"; a re-ask moves the time and reason, a note does not (regression guards; pass on both)
Old-code run: `pulse_core.py` from HEAD + the new selftest in a scratch dir -> 2 FAIL + AttributeError.
New code: `selftest_pulse.py` OK 0 failing; all 26 `src/RimMandrake/rimflow/selftest_*.py` exit 0.
Full `run_selftests.py --workers 12`: 384/388 pass; the 4 non-greens are not this change -
`selftest_ledger_lint` (this clone's FOUNDRY shard is behind origin/main), `selftest_one_path_seam`
(`src/RimStarWars/Armoury/prove_canon_materials.py`), and two 240 s timeouts under parallel load
(`selftest_empire_ladder`, `selftest_skeleton_burial`).

Live, after `systemctl --user restart rm-pulse` (2026-10-10 ~19:40 PDT):
- "to rule" 6 -> 35 rows; `SCRAPNEST_BIRD_BASE_THEFT_1` (built, needs bridge) gone; the WarLab design
  choices filed today present. Matches `rimflow`'s replay exactly (60 open needs=owner, 35 inside 14 d).
- Latency, BENCH clone: `rimflow note` -> daemon re-fold (`sources.ledger.changed_at`) **3.6 s**, including
  the CLI's own run time. FOUNDRY clone: same stat path (its shards are in the signature); FOUNDRY made no
  write during a 7-minute passive watch, so not separately timed - bound is the same one tick (<=5 s).
- Before: removal of a ruling by anything but a `needs`/close verb: **never** (until the 14-day window
  expired; SCRAPNEST had been stale ~9.5 h). Additions via `file`/`implemented`: never.
- Ledger source cost: 0 ms per unchanged tick; ~0.4 s per change (read 18,353 events + replay).
