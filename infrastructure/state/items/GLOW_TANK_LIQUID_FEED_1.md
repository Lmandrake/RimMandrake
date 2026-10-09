# GLOW_TANK_LIQUID_FEED_1 — the GlowTank drinks from the pipe network

Source: `design/RimMandrake/gpt_reviews/DESIGN_PASS_2026-10-08.md` row LP-2 (owner card 2026-10-08: queue all batches).
Spec: `design/RimMandrake/deepfire_luminous_pigment_spec.md` §2.5 (Q5 2026-09-25: salt or boiling water only).

## what
Built at `041c0142b`. Checked first: the tank header and `Building_GlowTank.cs` said the water gate was not built,
and the reason ("no way to carry a liquid") no longer holds — FlowWorks ships `RM_LiquidNet.TanksFor` and
`Building_LiquidTank`.
- With FlowWorks loaded and "Tank needs ocean water" on, the tank draws one unit of `RM_Liquid_SaltWater` or
  `RM_Liquid_BoilingWater` from a liquid tank adjacent to it or on a hose run touching it, by reflection
  (`FlowWorksWaterBridge`, soft-hook convention: no assembly reference, no modDependency).
- `RM_GlowTankWater` kernel: a reserve of up to two units, drained while running, refilled at half a unit. Fuzzed
  (`LuminousPigmentFuzz` family `water`).
- Dry: the crop's growth pauses (Harmony postfix on `Plant.GrowthRate`, cultured crowncarpet in a GlowTank only).
  Nothing dies of thirst. The inspect string says dry / hours in reserve / "not needed (FlowWorks not loaded)".
- Mod Settings: toggle + units per day (0.5–20). Without FlowWorks, or off: power + seed as before.
- North-star: `validation.py` component `glowtank/water_gate_dry_tank_pauses`, mutant-checked in the selftest.

**PROVISIONAL number** (invented, owes a sitting): 4 units of ocean water per day of running.

Not built: the spec's other route, an orthogonally adjacent salt/boiling liquid terrain cell feeding the tank.

## criteria
- O1 L0: LuminousPigment builds; water fuzz family and selftest_luminouspigment pass
- A1 L1: with FlowWorks and LuminousPigment loaded, a seeded GlowTank on no net reads "Dry: growth paused"
- A2 L2: a salt-water tank beside it is drawn down one unit at a time and the crop grows; switching the setting off removes the line
- A3 L2: a fresh-water or brine tank beside it does not feed it
- H1 L4: the owner judges the drink rate (PROVISIONAL until then)

## verify

Run each criterion at its stated level and record it with `rimflow verify GLOW_TANK_LIQUID_FEED_1 --criterion <ID> --result pass|fail|partial --config <list> --evidence <path>`:
- L0: offline build, selftest/fuzz/lint (already run at implementation).
- L1: one minimal-list load, read Player.log for config/cross-reference errors and the specific line, or one spawn-and-read bridge probe.
- L2: one quicktest map via the bridge or modcheck: set up the scenario in the criterion, step ticks, read the state named.
- L4: owner judgement in a sitting; not a FOUNDRY acceptance task.
Evidence is the Player.log line or bridge read the criterion names; a screenshot is not evidence of state.

### Exact checks 2026-10-09 (acceptance sitting)
- A1 CHECK: Existing component `glowtank/water_gate_dry_tank_pauses` in `LuminousPigment/validation.py` (chain `glowtank`). Raw: `jawa/spawn_batch ops="RM_GlowTank:<x>,<z>"` on a roofed cleared pad, power it on, `jawa/mod_settings_field` set `tankNeedsWater`=True, advance 500 ticks, then `jawa/inspect_string thingIds=<tank id>`. Needs FlowWorks + LuminousPigment active. PASS: the inspect text contains `Dry: growth paused`; with tankNeedsWater=False after another 500 ticks it does not. FAIL: text lacks the line with the setting True; text says `not needed (FlowWorks not loaded)` (UNMEASURED: FlowWorks absent); or the line persists with the setting False.
