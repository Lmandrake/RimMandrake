# FlowWorks playtest runner — Approach A (in-game scenario runner)

Status: **built, compiles clean; NOT yet deployed or run live** (2026-10-06, BENCH helper). Plan:
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

## Next step

Not yet run live. Build verified 2026-10-06 (`winbuild.py` on the companion csproj: clean, the three tool
names present in the DLL). The live pilot:

1. Game down (the DLL is memory-mapped), then `python3 src/RimMandrake/bridgetools/build.py --gm --apply`.
2. Game up on a scratch map with colonists (a quicktest map is fine), bridge held.
3. `python.exe D:\Luke\dev\RimMandrake\src\RimMandrake\FlowWorks\northstar\playtest_runner.py --recipe pilot --tick-mode batch`
   then the same with `--tick-mode speed` (the tick-rate comparison), then `--recipe fluids,inject`
   (must read INCOMPLETE with the fluids record kept). Each new run needs fresh fixture ground; the
   search skips cells earlier runs changed.

Expected first result: `fluids` FAILs (the source finding); `dig` and `pit` are unknown.
Record first live timings here.

## Known limits of the pilot

- The pit's escape attempts use ordinary `Goto` jobs on non-player pawns (re-issued every 120 ticks if
  their own AI drops it); a colonist turret can kill the hostile, which voids the scenario (INVALID), never PASS.
- Fixtures are left on the map (water/tar strips, the pit, the ladder); scratch maps only.
- No save/reload, no review save yet (days 3+ of the plan).
