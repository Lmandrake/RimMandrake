# Full-file re-review of the L1 builder's files — BENCH reviewer, 2026-10-15

Why: `l1_fixes.md` marked these CLEAN after reviewing only its own change in context (lesson d75b357e0c2d).
All reopened, then reviewed every line. Commits: 15b8330990 4f470f7c57 ca7a2f3e31 7a57b3c491 333117ca8e c8fb15078a d5c81f46e4.

Excluded: `src/RimMandrake/FlowWorks/Tools/generate_liquid_suite.py` (also carries fuel-moat b0ec1721ff).
Fuel-moat builder's files (not touched by L1, not reviewed here): FlowWorks `RM_LiquidFire.cs`, `RM_FuelFireMath.cs`,
`FluidDef.cs`, `RimMandrakeFlowWorksMod.cs`, `RimMandrakeFlowWorks_DefOf.cs`, csprojs, `FuelFireChecks.cs`,
`GptFixesAChecks.cs`, SelfTest `Program.cs`, `FlowWorks_LiquidFire.xml`, `FlowWorks_PitFluids.xml`,
`selftest_flowworks_call_sites.py`, `selftest_flowworks_fuel_moat.py`, Astrofuel adoption + registry XML.

| file | lines | verdict | findings | fix sha |
|---|---|---|---|---|
| GimmeSomeSlack/Source/Aerial/AerialMath.cs | 726 | pending | | |
| GimmeSomeSlack/Source/Aerial/RM_FallenWireShock.cs | 261 | pending | | |
| GimmeSomeSlack/Source/SelfTest/GptPreReleaseChecks.cs | 362 | pending | | |
| GimmeSomeSlack/Source/GssSessionReset.cs | 47 | pending | | |
| GimmeSomeSlack/validation.py | 1798 | pending | | |
| FlowWorks/northstar/extensions.py | 2712 | pending | | |
| FlowWorks/northstar/selftest_extensions.py | 1063 | pending | | |
| FlowWorks/Tools/selftest_water_not_food.py | 78 | pending | | |
| FlowWorks/Defs/LiquidTypes/ThingDefs/RM_LiquidBottles.xml | 434 | pending | | |
| Pyrelands/selftest_pyrelands_fruit_clear.py | 91 | pending | | |
| Pyrelands/validation.py | 2774 | pending | | |
| Utils/modcheck/clockgate.py | 585 | pending | | |
| Utils/modcheck/selftest_clockgate.py | 515 | pending | | |
| Greentide/Source/RM_GreentideMod.cs | 563 | pending | | |
| Scarlands/Source/RM_WarscarMod.cs | 826 | pending | | |
| TerminalBiomes/Source/RM_TerminalBiomes.csproj | 152 | pending | | |
| TerminalBiomes/Source/RM_TerminalBiomesMod.cs | 921 | pending | | |
| Utils/selftest_settings_screens.py | 1060 | pending | | |
