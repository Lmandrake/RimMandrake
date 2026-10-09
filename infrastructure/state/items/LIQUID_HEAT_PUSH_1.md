# LIQUID_HEAT_PUSH_1 — hot and icy liquid move the air through vanilla heat

Source: `design/RimMandrake/gpt_reviews/DESIGN_PASS_2026-10-08.md` rows FL-1 / X-8. Closes the heat push that
closed `BOILING_WATER_BURNS_1` §3 specified and never landed.

## what
Built at `f90610cd5` (FlowWorks + one TerminalBiomes patch). Every 250 ticks, on its own timer (the depth engine
being off does not stop it), each wet hot or icy cell pushes vanilla heat into its ROOM — the same
`Room.Temperature` a heater writes, so vanilla Heatstroke / Hypothermia do any harm (one kind of heat).

- **Sources.** An excavated cell's fill: `FluidDef.hot/cold` (new), else the LiquidDef naming it as `canalFluid`.
  A natural terrain: its LiquidDef (`terrainSuite`) `hot` / `cold` (new, icy row via the generator), else the new
  terrain extension `RM_LiquidHeatExtension` (the Scald's six `RUT_ScaldWater*`, patched from TerminalBiomes,
  FindMod-guarded).
- **Bounds (all PROVISIONAL, `RM_LiquidHeatMath`).** 3 energy/s per fill level hot, 2 cold (a brim-full superdeep
  boiling cell ≈ half a heater); natural cell = 2 levels. A room levels off at 50 °C (hot) / 0 °C (icy) and takes at
  most 8 heaters' worth per interval. At most 3000 cells visited per interval, round robin, energy scaled so average
  power is exact. Natural cells rescanned every 15000 ticks.
- **Settings.** "Boiling and icy liquid warm or chill the room they are in" + strength slider (x0.25..3).
- **MEASURED limit (decompiled 1.6 `Room.PushHeat`):** a room using the outdoor temperature takes no heat. So an
  OPEN Scald shore stays at the outdoor temperature; a roofed hut on the shore warms. That is the ruling working,
  not a gap.
- **Not reachable yet:** a pit FLOODED with boiling water. No hot or cold canal FluidDef ships (boiling/icy LiquidDefs
  have `canalFluid` null, so a boiling pond's channel fills as plain water). The heat path for one is already wired
  (`FluidDef.hot`); the fluid itself is `BOILING_ICY_CANAL_FLUIDS_1`.

## criteria
- O1 L0: C# selftest LiquidHeat_* cases pass (kind, energy scaling, target clamp, room cap, budget); v2 --offline green; selftest_extensions counts the liquidHeatPushEnabled toggle
- A1 L1: FlowWorks and TerminalBiomes load on the live list with no config error; the six RUT_ScaldWater terrains carry RM_LiquidHeatExtension
- A2 L2: extension chain liquid_heat (northstar/extensions.py, DRAFT): a roofed hut over boiling water reads warmer than a plain-water twin, an icy one colder, the boiling hut never passes 50 C, and with the setting off its lead stops growing
- A3 L2: an open boiling patch identifies hot but reads outdoor, and the outdoor temperature beside it is unchanged

## verify

Run each criterion at its stated level and record it with `rimflow verify LIQUID_HEAT_PUSH_1 --criterion <ID> --result pass|fail|partial --config <list> --evidence <path>`:
- L0: offline build, selftest/fuzz/lint (already run at implementation).
- L1: one minimal-list load, read Player.log for config/cross-reference errors and the specific line, or one spawn-and-read bridge probe.
- L2: one quicktest map via the bridge or modcheck: set up the scenario in the criterion, step ticks, read the state named.
Evidence is the Player.log line or bridge read the criterion names; a screenshot is not evidence of state.
