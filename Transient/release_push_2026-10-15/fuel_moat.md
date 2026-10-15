# Fuel moat — CHEMFUEL_MOAT_WIRE_MISSING_CHANNEL (BENCH, 2026-10-15)

Owner, by card 2026-10-15: "Connect it today and make it tremendous. ... a moat of gasoline ... Then there's
astrofuel. That should simply be a massive explosion ... In Utinni such a thing should instantly summon raids ..."

| step | state | sha | notes |
|---|---|---|---|
| 1 chemfuel/astrofuel fill channels (canalFluid) | done | b0ec1721ff | registry row via generator; astrofuel adoption patch. Tank->pump/hose->channel was already generic. |
| 2 chemfuel inferno | done | 1a5a2ceee7, DLL c5101f6c22 | fireKind Inferno: 2-tick front, RM_LiquidFlame_Inferno (vanilla fire art at 2.4 cells), 8x heat, ~3-cell ignite halo (capped 360 tries/check), a level per 5 s. Settings: on/intensity/spread/burn-rate. |
| 3 astrofuel detonation | done | 1a5a2ceee7 | BFS plan (RM_FuelFireMath.PlanDetonation): 1 tick a ring, <=4 Bomb blasts and <=400 emptied cells a tick, <=240 blasts a body, stagger + PawnFlyer_Stun throw, heat, ash; schedule saved. Settings: on/blast scale. |
| 4 Utinni hook | done | 6238e06206, DLL 0e6e3f5554 | A heat system EXISTS: Colony Visibility, raised via EmpirePursuit's EmpireSearch.AdjustVisibility. FuelBlastInvestigation binds RM_FuelFireEvents by reflection: +40..80 Visibility (chemfuel fire 1/3), one forced RaidEnemy/map/day by the pursuer, CenterDrop on the blast after 2 h. |
| review-map stations + extension chains | done | b7392d3d39, DLL 4b14b4dc69 | stations 21/22 (frozen unlit); chains fuel_moat_chemfuel, fuel_moat_astrofuel |
| review fixes + CLEAN marks | done | 538e17abf9, 6e4fc00401 | 5 files CLEAN; big shared files left DIRTY (below) |

## Perf numbers (offline, C# SelfTest FuelFireChecks)

- 60x1 channel: 20 blasts, 59 ticks, max 1 cell / 1 blast a tick, plan 0.5 ms
- 30x30: 900 cells, 100 blasts, 60 ticks, max 58 cells / 4 blasts a tick
- 2000x1 lit mid: 223 blasts (spacing 9), 1000 ticks
- 141x141 (19,881 cells): 225 blasts (spacing 10), 280 ticks, max 141 cells / 4 blasts a tick, plan 15 ms
- chemfuel 100-cell moat lit end to end in 198 ticks (oil: 8910); 60 brim cells burnt dry in 1250 ticks, all 144 levels accounted
- LIVE cost of 4 vanilla Bomb explosions a tick: UNMEASURED (FUEL_MOAT_VERIFY_LIGHT_THE_GASOLINE)

## Live proof commands

- deploy FlowWorks + EmpirePursuit, then `northstar/extension_proof.py` chains `fuel_moat_chemfuel`, `fuel_moat_astrofuel`
- bridge: `RimMandrake.FlowWorks.RM_LiquidFireProof.ProofIgnite "x,z"`, `ProofReport ""`;
  `RuthlessPursuingMechanoids.FuelBlastInvestigation.ProofState ""`, `ProofFireNow ""`, `ProofCancel ""`

## Filed

- FUEL_MOAT_VERIFY_LIGHT_THE_GASOLINE (BENCH, bridge) — the live proof and a hitch measurement
- PROPANE_CANAL_WIRE_STILL_NO_FLUID (FOUNDRY, offline) — propane has no canal FluidDef

## Left DIRTY (changed, not full-file reviewed)

RimMandrakeFlowWorksMod.cs, FluidDef.cs, RimMandrakeFlowWorks_DefOf.cs, SelfTest/Program.cs, GptFixesAChecks.cs,
selftest_flowworks_call_sites.py, review_map.py, review_map_coverage.py, northstar/extensions.py, site_spec.py,
selftest_flowworks_northstar.py, EmpireLadder.cs, EmpireLadderMath.cs, Settings.cs, EmpirePursuit SelfTest/Program.cs,
selftest_settings_screens.py
