## spec
Verify every open FOUNDRY-queue item's `state`/`needs`/`blocked`/`for` is
actually correct — not falsely `doing`, not falsely `blocked`, not
mis-owned. Filed thin by another seat; FOUNDRY scoped the check below.

## what was checked
- Full state census of `infrastructure/state/queue/FOUNDRY.md`: 20 items in
  `doing`, 0 in `blocked` (a `blocked` state exists in the schema but nothing
  is currently in it — no false-blocked to find).
- `row: unassigned` on all 20 `doing` items is **not a defect** — confirmed
  by reading `rimflow/cli.py:447` (`it.row if it.row is not None else "-"`):
  `row` is an optional source-spreadsheet-row citation, unrelated to who is
  actively working an item. Its absence is the normal default, not a sign of
  abandonment.
- Staleness (days since last ledger event) computed for all 20 `doing`
  items. Three read as multi-day-stale by the clock alone:
  - `DROID_SYSTEM_BUILD_1` (2026-09-02, 3 days) — confirmed **deliberately
    parked**, named explicitly in the `RIMFLOW_RECLAIM_COMMAND_1` free-stale
    sweep (commit `346d2cd7`: "Skipped DROID_SYSTEM (parked)"). Correctly
    excluded, correctly still `doing`.
  - `JAWA_PATCHES_SPLIT_1` (2026-09-04 22:06, <1 day at check time) —
    likewise named as deliberately **held** in the same sweep. Correctly
    `doing`.
  - `LIVESTOCK_STARTER_TRIO_1` (2026-09-01, 4 days) — read the item file in
    full: genuine open scope remains (Onnik's feed-mechanic increment is
    scoped and unstarted; Moornak is genuinely blocked on an unresolved
    spec-vs-design-doc scope question). Correctly `doing`, not abandoned.
- Sampled two more `doing` items whose last touch was 2+ days old
  (`INHABITED_STOCK_ONTO_MAP_AND_FATE_1`) — read in full, found a real,
  itemized "not done, deliberately" list still open. Correctly `doing`.
- The remaining 15 `doing` items were all touched within the last ~24h by
  this session or a concurrent one tonight (Ninefold, Vault, Inhabited,
  Sandworm, PlotMechanism, Armoury, DevLog, MassValidation, FluidCanal x2,
  Shield, LoadConfig, District, TileStructure, the standing review loop
  itself) — verified fresh by ledger timestamp, not re-read individually;
  this is the bounded scope of this pass, not exhaustive per-item re-audit.

## Not checked (owed if a fuller pass is wanted)
- The full `proposed`/`ready` list for the inverse error (an item marked
  open that is actually already done in the code). Not sampled this pass.
- `needs`/`for` field correctness for anything outside the `doing` set.
- BENCH's own queue (`queue/BENCH.md`) — this item's title says "every open
  item" but the census above only covers FOUNDRY's.

## verify
- Read `rimflow/cli.py`'s own `row` handling before concluding it was benign
  (done, cited above — not assumed).
- Read the actual item file (not just the queue summary line) for every
  item flagged stale-by-clock before calling it correctly `doing`.

## criteria
- [x] No item found falsely `doing` (all sampled multi-day-stale items have
      real, current, unclosed scope).
- [x] No item found falsely `blocked` (nothing is currently in that state).
- [x] `row: unassigned` confirmed benign, not a health signal — worth
      dropping from any future staleness heuristic that treats it as one.
- [~] Full `proposed`/`ready`-list inverse check and BENCH's queue: not
      done this pass, scoped out above rather than left silently undone.

Closing this pass as a bounded, honest spot-check — the queue reads healthy
where sampled. A fuller pass (inverse-direction check, BENCH's queue) is
real remaining scope if the daily staleness review (`QUEUE_DAILY_STALENESS_REVIEW_1`)
picks it up as a recurring job rather than a one-off.
