# BOUNDARY: a mod's road back holds only the mod's own work, Design Version 0.1.0

Code: `src/RimMandrake/rimflow/maturation.py` (`ledger_homes`, the `home` field of `ledger_items_caused_by`),
`src/RimMandrake/rimflow/maturation_autonomy.py` (`off_mod`, `road_back_open`, `_road_back`) and
`src/RimMandrake/rimflow/maturation_dispatch.py` (`live_units_on`, and the pilot launch and holder reads of the road
back). Item `RIMMANDRAKE_FIX_REPAIR_RUN_HOLDS_MOD_VISIT_WAITS_GAME_IDLE`. Each promise has a test of its name in
`src/RimMandrake/rimflow/selftest_road_back_holds_own_work.py`.

The case (6:15 PM PST 2026-11-27): the Conductor filed the pipeline repair
`RIMMANDRAKE_SEAL_STEWARD_SECTION_BLIND_JUDGE_READ_IT_FIRST` (the blind judge's brief), caused by FlowWorks' blind-cycle-5
judge item. The road back reads every open item caused by its steward and judge items, so it read the repair as
FlowWorks' work. The tick launched FlowWorks' holder run on it at stage `in_game` (it holds FlowWorks' ledger lease and
carries `RM_CONTROL_MOD=FlowWorks`). That live holder held in-game visit 14 while ArchBig was free. The status page placed
the run on FlowWorks correctly: the tick itself had launched the run as the mod's holder.

## The rule

A run holds a mod's next run only when the run works that mod. The pipeline launches a holder or fixer run of the mod
only on the mod's own road-back work. An open road-back item whose last ledger home (`rimflow home`) places it off the
mod is not the mod's work: `pipeline:`, `game:`, `machine:`, `fix:` or another mod's `mod:`. It gets no holder or fixer run
of the mod, and it holds no cycle or visit of the mod. The Workshop Pipeline, or the other mod's pipeline, works it
(`mod_work.of`: the home is the decision).

An item with no home, or the home `unplaced`, stays the mod's road-back work, as before. Measured 2026-11-27: 75 of 93 past
road-back items had no home and no repo path, and a path alone misplaces a FlowWorks fix whose prose cites only its
`design/specs` page. So a path is never read as a home here.

A live run that the mod's pipeline launched on the mod stays live on the mod (`live_units_on`), and nothing launches on
the mod while it runs: two runs never write one mod's files at the same time.

## ACCEPTS

- **home-events.** A ledger `home` event names its item in `id` and its home in `home`, a string. The last one in time
  order (`ts`, then `tsn`) is the item's home. An event of another shape is ignored.

## DOES NOT SURVIVE

- A pipeline ticket filed with no home. It stays in the road back of the mod that caused it, as before; the filer or the
  Conductor gives it its home with `rimflow home <ID> --home pipeline:<part> ...`.
- The stage record's road-back hold of the offline build (`road_back_decide`, `road_back_hold`), which reads its items
  from the stage record, not from this reader.

## PROMISES

- **a-ticket-homed-off-the-mod-holds-no-stage-of-it.** An open road-back item whose last home is not `mod:<this mod>`
  (and not `unplaced`) is left out of the road back: the dry tick's road-back step decides nothing on it, the owed cycle
  or visit stays the launch, and the holder step runs no holder of the mod on it.
- **the-mods-own-work-still-holds-its-next-run.** An item homed `mod:<this mod>`, unhomed or `unplaced` still takes its
  fixer before the next cycle or visit; the mod's own item beside an off-mod one still holds; a live run on the mod is
  live on it.
- **could-not-look-launches-nothing.** Run records that cannot be read make `live_units_on` read `UNMEASURED`, never an
  empty list; a ledger that cannot be read makes the road back `blind`, and no visit launches.

## Offline simulation: yes

The selftest runs the real road-back step and holder step against a throwaway ledger shard and a fake run-record reader.
