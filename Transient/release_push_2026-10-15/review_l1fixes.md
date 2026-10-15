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
| GimmeSomeSlack/Source/Aerial/AerialMath.cs | 726 | CLEAN | + LayTouches (pure, for the scoped exemption) | 57de30cb37 |
| GimmeSomeSlack/Source/Aerial/RM_FallenWireShock.cs | 261 | CLEAN | DEFECT: exemption was `p.CurJobDef == Restringing.Job` -- ANY re-string worker on ANY live wire anywhere (his path there, another cut) was unshockable. Now OnOwnCut: only cells on either fallen half of a cut span of the anchor his job targets | 57de30cb37 |
| GimmeSomeSlack/Source/SelfTest/GptPreReleaseChecks.cs | 362 | CLEAN | +3 rows: his cut's wire vs another cut's wire vs the hanging part (688/688) | 57de30cb37 |
| GimmeSomeSlack/Source/GssSessionReset.cs | 47 | CLEAN | none. Verified in RimWorld source: Game.ExposeData -> ExposeSmallComponents is the only save path for Game.components; FillComponents runs only in LoadingVars (and Game()), so a component dropped while Saving is not re-added before the write; patch class is in the PatchApplier namespace. Old saves: class still exists, deep-loads via ctor(Game) (= the reset), next save drops it. The ctor runs twice on load (Game() + FillComponents): harmless, idempotent clears | - |
| GimmeSomeSlack/validation.py | 1798 | CLEAN | O7 shape row updated to the scoped exemption + LayTouches row; offline 9/9 | 57de30cb37 |
| FlowWorks/northstar/extensions.py | 2712 | DIRTY | excluded: fuel-moat builder has UNCOMMITTED edits in it right now (chemfuelInferno/astrofuelDetonation toggles, 'chain fuel_moat' not yet present). Whole file read; no defect in the L1 bottle_dirty_off change or elsewhere. Re-mark after their commit | - |
| FlowWorks/northstar/selftest_extensions.py | 1063 | CLEAN | none (PASS, 52 chains / 141 components) | - |
| FlowWorks/Tools/selftest_water_not_food.py | 78 | CLEAN | none (PASS) | - |
| FlowWorks/Defs/LiquidTypes/ThingDefs/RM_LiquidBottles.xml | 434 | CLEAN | none (byte-identical to generator; no inherited Nutrition in the bases) | - |
| Pyrelands/selftest_pyrelands_fruit_clear.py | 91 | CLEAN | none (PASS) | - |
| Pyrelands/validation.py | 2774 | CLEAN | none | - |
| Utils/modcheck/clockgate.py | 585 | CLEAN | none (last-tick resumable stop completes the chunk; resume cap still raises) | - |
| Utils/modcheck/selftest_clockgate.py | 515 | CLEAN | none (64/64) | - |
| Greentide/Source/RM_GreentideMod.cs | 563 | CLEAN | none (krannock only in RM_Greentide wildAnimals; field names checked against 1.6 BiomeDef) | 2529681445 mark |
| Scarlands/Source/RM_WarscarMod.cs | 826 | CLEAN | none (its registry-reset GameComponent is saved, but Warscar has stateful GameComponents in saves anyway: not the GSS defect) | 2529681445 mark |
| TerminalBiomes/Source/RM_TerminalBiomes.csproj | 152 | CLEAN | false comments the L1 pass left: build instructions pointed at the read-only mirror; 'loadAfter ... ModsConfig.IsActive in a NoInlining method' (registration is unconditional) | 2529681445 |
| TerminalBiomes/Source/RM_TerminalBiomesMod.cs | 921 | CLEAN | DEFECT: cages-passable flip Off->On did not reach loaded maps: RecalculatePerceivedPathCostUnderThing returns early for a passable zero-pathCost def, so the path grid kept the cage cells blocked (and the walkability notify read the stale grid). Now per-cell RecalculatePerceivedPathCostAt then notify. Also a stale NoInlining comment | 2529681445 |
| Utils/selftest_settings_screens.py | 1060 | CLEAN | none (822/822) | - |

Shas: skeleton 3adb239283, GSS fix 57de30cb37, TerminalBiomes fix 2529681445. DLLs rebuilt by winbuild.py (GSS, TerminalBiomes) with .srchash. Not deployed (no live proof run); live proof for the GSS change: proof_all GSS re-string row with a second cut's live wire on the worker's path.
