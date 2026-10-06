# FlowWorks playtest runner — Approach A (in-game scenario runner)

Status: pilot run live 2026-10-06; coverage scenes built offline, not yet run live (section "Coverage scenes"). Plan:
`design/RimMandrake/flowworks_playtest_automation_2026-10-06.md` (Approach A, days 1–2 pilot scope).
Timing is a first-class output: the owner is comparing approaches A/B/C by wall time.

## What

One bridge call starts a run; C# owns execution from there. A static controller (no MapComponent,
no GameComponent, nothing in saves) plus a hidden `MonoBehaviour` whose `Update()` advances the
current scenario once per Unity frame. Scenarios are C# iterators that `yield` waits ("N ticks",
"until predicate or timeout"), so nothing ever blocks inside one bridge call. Each scenario's
result is appended to a JSONL journal the moment it finishes; the run's last line is `run_end`.
A journal with no `run_end`, or one whose `run_end` says `completed=false`, reads **INCOMPLETE**,
never green.

Bridge tools (JawaBench companion):

| tool | returns |
|---|---|
| `jawa/playtest_start` (recipe, seed, tickMode, frameBudgetMs) | run id at once; the run proceeds across frames |
| `jawa/playtest_status` (runId) | state, current scenario/phase, ticks, wall, records so far |
| `jawa/playtest_collect` (runId) | journal path + verdict + summary re-derived FROM THE FILE |

## Files

- `src/RimMandrake/bridgetools/JawaBench.BridgeTools/JawaBenchFlowWorksPlaytest.cs` — runner, driver, 3 scenarios, tools.
- `src/RimMandrake/FlowWorks/northstar/playtest_runner.py` — python.exe launcher: start, poll, collect, timing table.
- `src/RimMandrake/FlowWorks/northstar/selftest_playtest_runner.py` — selftest of the launcher's pure logic (verdict + timing table).

Journal: `<RimWorld save-data folder>\JawaBench\playtest\<runId>.jsonl`; the launcher copies it to
`Transient/flowworks_playtest/`.

## Timing

Every scenario record carries `timing{wallSec, ticks, frames, phases{setup,exec,observe}{wallSec,ticks,frames}}`;
`run_end` carries the run totals, the same three-way phase split, achieved ticks/sec, and the tick mode.

Two tick modes, so the question "can ticks go faster than the speed setting" is measured, not argued:

- `speed` — game unpaused at `TimeSpeed.Ultrafast` (the fastest setting); ticks come from vanilla
  `TickManager.TickManagerUpdate`. Reports `timeSpeed` and `tickRateMultiplier` actually in force.
- `batch` (default) — game paused; the driver calls `Find.TickManager.DoSingleTick()` (the dev
  "step one tick" entry point) repeatedly inside a per-frame wall budget (`frameBudgetMs`, default 50),
  checking the scenario's predicate after every tick. Rendering and the bridge still get a frame
  every ~budget ms.

Both report achieved ticks/sec over the scenario's waits. Which is faster is the first live result to
record here.

## Scenarios (pilot)

Fixtures are found by a search for clean soil, away from water, edge and buildings; setup
shortcuts (terrain writes, `Deepen()` for the pit, direct pawn/ladder spawns) build FIXTURES only.
Each scenario's evidence route is a production path:

1. **fluids_touching** — water strip side-adjacent to a tar strip. Evidence route: the production
   classifier `RM_LiquidStock.BodyAt` on first contact (what the pulse calls). PASS = two bodies,
   each carrying its own fluid. Source finding expected to make this FAIL
   (`Source/RM_LiquidStock.cs:157,168`: the flood fill expands over any `IsSourceCell` neighbour, the body
   takes the seed's fluid).
2. **dig_fill** — `Designator_DigCanal.CanDesignateCell` + `DesignateSingleCell` on one soil cell; one
   undrafted colonist gets Mining enabled (setup); the colonist's own think tree must take
   `RM_DigCanalJob` (`playerForced` must be false) and depth must rise. Then
   `Designator_FillInCanal` likewise; PASS = depth back to 0 and top/foundation terrain equal to the
   pre-dig snapshot (our own snapshot, not the component's `originalTerrain`).
3. **pit_escape** — a D4 square (side ≥ max(3, RequiredWidth+1)) built with `Deepen()`. A weaponless
   hostile pawn ordered (Goto) to a cell outside: must stay in the pit and `CanReach` must be false.
   A lowered `RM_Ladder` is then spawned on the pit edge: the hostile must STILL stay
   (`MayClimb` = false for hostiles); a non-hostile-faction pawn in the same pit must get out.
   (Owner's ladder rule: lowered ladder lets own/friendly out; enemies never; prisoners only in a break.)

`recipe` is a comma list of `fluids,dig,pit` (`pilot` = all three); add `inject` to append a scenario
that throws, to prove the INCOMPLETE path.

## Pilot result (live, 2026-10-06)

Run on the 10-mod `flowworks` tier, quicktest map: `fluids` FAIL (water and tar merge into one body, the source
finding), `dig` PASS (colonist took the dig unforced; fill-in restored terrain), `pit` FAIL on `friendly_with_ladder`
only (reachability credits the ladder, the pather does not route through it - the `RM_PitPathing` work). Batch vs
speed: about 2,080 vs 2,090 ticks/s achieved over waits at a 50 ms frame budget - no measurable difference.
`fluids,inject` read INCOMPLETE with the fluids record kept, as designed. Each run needs fresh fixture ground; the
search skips cells earlier runs changed.

## Known limits of the pilot

- The pit's escape attempts use ordinary `Goto` jobs on non-player pawns (re-issued every 120 ticks if
  their own AI drops it); a colonist turret can kill the hostile, which voids the scenario (INVALID), never PASS.
- Fixtures are left on the map (water/tar strips, the pit, the ladder); scratch maps only.
- No save/reload, no review save yet (days 3+ of the plan).

## Coverage scenes (2026-10-06)

Built offline, compiles clean, **not yet run live**. Code: `src/RimMandrake/bridgetools/JawaBench.BridgeTools/JawaBenchFlowWorksPlaytestScenes.cs`
(a fixed catalogue of C# iterators, no scenario language). Recipes: `pilot` (fluids,dig,pit), `full` (every scene below,
`save_reload` last), or any comma list of scene names. Fixture shortcuts are the same kind as the pilot's; each scene names
its evidence route in `evidence.route`.

| scene | fixture (setup only) | evidence route | PASS asserts |
|---|---|---|---|
| `depth_fill` | 15 isolated 9x3 soil strips, one per (D,F): D0 baseline plus every legal F for D1-D4, by `Deepen` + `TrySetDriverFill(water)` | read back through `DepthAt/FillAt/FluidAt`; vanilla `PathGrid.Cost`; a friendly pawn Goto end to end along each strip's middle row | every state reads back; F=2 on a D1 cell clamps to 1; dry path cost D1 > surface and non-decreasing D1..D3; dry D1..D3 crossings no faster than surface. Wet and D4 rows recorded, not asserted (no ruled number) |
| `fire` | 7-cell D1 strips of tar, then water (and any `Detonation` FluidDef — none defined today, so not run) | a vanilla Fire beside the strip (`FireUtility.TryStartFireIn`, else the same spawn) -> `Fire.SpawnSetup` postfix -> `RM_LiquidFire` front | tar beside the fire lit within 300 ticks; every cell lit within 4000; ignition order follows distance; water never lights in 900 ticks |
| `pump` | D3 channel cell (water F3) - `RM_LiquidPump` - 2x2 `RM_LiquidTank`; power by the vanilla DEV "toggle power on" | the pump's own Tick (250-tick cycle) -> TryDraw/TryPour | unpowered moves nothing; powered draw = 1 level -> 5 units; tank 5 short of full takes one level and then clamps; tar tank refused into a water channel; tar poured into the emptied channel, tank pays 5/level |
| `river` | needs a river map (INVALID otherwise); `RM_FordStones` beside a current cell; two `RM_FerryPost` on the banks | `RM_MapComponent_RiverCurrent.MapComponentTick` (scan 250 / process 15) on a pawn holding a Wait job | pawn in the current shoved within 1500 ticks, first step = the cell's flow direction; pawn beside a ford and pawn on the ferry rope not carried. A case whose fixture cannot be placed is recorded `skipped`, not passed |
| `sluice` | 5-cell D2 channel, 2 cells water F2, flow door on the middle cell (`RM_SecurityGrateDoor` closed, `RM_Sluice` shut, `RM_Sluice` held open) | the flow pulse for 2000 ticks | RULED behaviour: grate passes, shut sluice holds, open sluice passes. **`expectedFailUntil: FLOWWORKS_SLUICE_TWO_DOORS_1`** - today the shut sluice passes, so the record is FAIL marked expected (XFAIL); an unexpected failure (grate/open) clears the mark |
| `pit_ladder_release` | D4 pit, side max(4, W+2), lowered `RM_Ladder` mid top row | Goto to a cell beyond the side AWAY from the ladder | friendly held at start, leaves via the ladder cell, reaches the far-side destination; hostile with the same ladder stays 900 ticks; no descent recorded |
| `pit_fall_forced` | 4x4 D4 pit | (1) Goto straight across the pit's middle row; (2) a pawn on the lip teleported into the pit (a skip's arrival) | walker never steps into an open pit cell and arrives; the forced arrival is counted by the trap's own descent detector within 120 ticks and the pawn is held |
| `save_reload` / `save_reload_b` | 3x3 natural pond (WaterShallow) feeding a dry 9-cell D2 channel | A: 500 ticks (mid-flow), `GameDataSaveLoader.SaveGame("JBPT_<runId>")`, then the uninterrupted branch for 1500 ticks; checkpoint `<runId>.checkpoint.txt` beside the journal; record **PENDING**. B (after the launcher loads that save): checks the tick, compares the loaded state with the saved snapshot, runs the same 1500 ticks | per channel cell D/F/fluid and the pond body's stock/capacity/receded count equal the uninterrupted branch line for line (and the loaded state equals the saved one) |

Verdict (C# collect and `playtest_runner.py` share it): INCOMPLETE without a completed run_end or with any status other than
PASS/FAIL/INVALID (PENDING included); FAIL on any FAIL not marked `expectedFailUntil`; INVALID; **XFAIL** when the only FAILs are
expected ones; PASS. An expected-fail scene that passes prints XPASS (its item may be built). The launcher, on a PENDING
`save_reload`, calls `rimworld/load_game_ready` on the named save and starts `save_reload_b resume=<first runId>`; the combined
verdict replaces PENDING with the resume half's status (`--no-resume` stops after the first half: INCOMPLETE).

Live trial, game up on a scratch map **with a river** (for `river`), bridge held, companion deployed (`build.py --gm --apply` with the game down):

    python.exe D:\Luke\dev\RimMandrake\src\RimMandrake\FlowWorks\northstar\playtest_runner.py --recipe full --tick-mode batch

`full` writes `JBPT_<runId>.rws` into the Saves folder (unique name, never overwrites) and then LOADS it.

Known limits: the swimmer, walkers and pit pawns are generated friendly/hostile faction pawns, never colonists (a
colonist case would add a colonist); `pit_fall_forced` exercises the pathing half that the parallel `RM_PitPathing`
work is building, so it may FAIL until that lands; fixtures are left on the map.
