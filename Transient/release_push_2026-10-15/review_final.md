# Independent full-file code review — release push 2026-10-15 (BENCH reviewer)

Owner, 2026-10-15: "please ensure that full clean/dirty code reviews are provided for these files before then".
Every row below is a FULL-FILE read by a reviewer who did not write the change under review (lesson d75b357e0c2d: a
diff-only review is not clean). Set-1 files were `reopen`ed first. Verdict = `code_review_status.py check` after the
mark. Selftests run after each fix are named in the row.

## 1. fw_builds.md build files (author CLEAN marks covered own diffs only; reopened, re-read whole)

| # | file | reachable | findings | fix sha | verdict |
|---|---|---|---|---|---|
| 1 | `src/RimMandrake/FlowWorks/Source/RM_NorthstarProofs.cs` | static_call dev surface (extensions.py, climb_proof.py) | ProofRamp and ProofLip accepted off-map cells (OOB throw instead of REFUSED) | f01b9b2a89 (DLL rebuilt, C# SelfTest 325/325) | CLEAN |
| 2 | `src/RimMandrake/FlowWorks/northstar/extensions.py` | extension_proof.py, validation.py | owed rows `liquid_ignition_off_default` / `liquid_corrosion_default_off` named for an OFF default that b5c8547e8b flipped ON; renamed (runsheet updated) | 9b4bc9cb14 | CLEAN |
| 3 | `src/RimMandrake/FlowWorks/validation.py` | modcheck suite | stale comment (riverSteam named as still owed); 5 new registry bools named in TOGGLES_NOT_ON_FLOOR | 357d29cd31 | CLEAN |
| 4 | `src/RimMandrake/FlowWorks/Source/ManyWaters/RiverSteamHook.cs` | MapComponent on every map | header kept a dated tile-count note calling the worldmap CSV authoritative (a RECORD, not the planet; zero-tile biome is expected) — removed | f01b9b2a89 | CLEAN |
| 5 | `src/RimMandrake/FlowWorks/northstar/selftest_extensions.py` | offline selftest | stale "staged at 100" comment | 357d29cd31 | CLEAN |
| 6 | `src/RimMandrake/FlowWorks/Source/RM_LiquidFire.cs` | Phase 6 fire engine | none (pending map, ExposeData round trip, blast-hop memory, roundtrip proof all read correct) | - | CLEAN |
| 7 | `src/RimMandrake/FlowWorks/Source/RM_PitTrapMath.cs` | pure math, SelfTest-compiled | none | - | CLEAN |
| 8 | `src/RimMandrake/FlowWorks/northstar/climb_proof.py` | live climb proof | none (live risk only: snow/things add to CalculatedCostAt; a flat step would then read >0 as MOD) | - | CLEAN |
| 9 | `src/RimMandrake/FlowWorks/northstar/selftest_climb_proof.py` | offline | none | - | CLEAN |
| 10 | `src/RimMandrake/FlowWorks/Source/RM_DigDiscovery.cs` | dig finds | none | - | CLEAN |

## 2. Left DIRTY with only changes reviewed

| # | file | reachable | findings | fix sha | verdict |
|---|---|---|---|---|---|
| 11 | `src/RimMandrake/GimmeSomeSlack/northstar/proof_all.py` | the GSS live proof | ORDER docstring still said "one fresh quicktest map" (default is the saved site) | 8ffc08e6f1 | CLEAN |
| 12 | `src/RimMandrake/FlowWorks/northstar/validation_v2.py` | FlowWorks core proof | docstring said live = fresh map; offline O1-O11, O-NEG, O-LIVE-NEG (43 faults) all PASS | 357d29cd31 | CLEAN |
| 13 | `src/RimMandrake/Utils/modcheck/test_site_saves.py` | proof_all, v2, extension_proof | none (destroy_batch confirmed DestroyMode.Vanish, so casket sleepers are destroyed not dropped) | - | CLEAN at 8ffc08e6f1; DIRTY again at 08:40: another agent has an uncommitted edit (+23/-4) in progress |

## 3. Walkthrough-map builders

| # | file | reachable | findings | fix sha | verdict |
|---|---|---|---|---|---|
| 14 | `src/RimMandrake/GimmeSomeSlack/human_review.py` | GSS review map | in-world title label said default look covers 12-33 and per-build 1-11 (round 8 added 34-41); html nav said north gallery 18-33 | 5909240827 | CLEAN |
| 15 | `src/RimMandrake/GimmeSomeSlack/save_review_map.py` | keeper save | none | - | CLEAN |
| 16 | `src/RimMandrake/FlowWorks/review_map.py` | FlowWorks review map | cards told the owner Liquid ignition / Liquid corrosion "ship OFF" (both ON since b5c8547e8b); small-pond card said ~20 cells at 5:1 (yardstick is 4 levels a deep square: ~8 cells) | 58956edb07 | CLEAN |
| 17 | `src/RimMandrake/FlowWorks/review_map_rivers.py` | map R | none | - | CLEAN |
| 18 | `src/RimMandrake/FlowWorks/review_map_coverage.py` | --plan | none | - | CLEAN |
| 19 | `src/RimMandrake/FlowWorks/selftest_review_map.py` | offline | none (PASS, 75 stations) | - | CLEAN |
| 20 | `src/RimMandrake/Pyrelands/human_review.py` | Pyrelands review map | DEFECT: 3 stations (burn bonus, firebreak and foam, empty twin pen) expected nothing, so verify read them "as built" with nothing read. station_verdict now returns None (unread) when nothing is expected, each station names its expectation, layout_check refuses an expectation-less station | 516a42e0b6 | CLEAN |
| 21 | `src/RimMandrake/Pyrelands/review/selftest_pyre_review_map.py` | offline | probes added for both new rules (ALL PASS) | 516a42e0b6 | CLEAN |
| 22 | `src/RimMandrake/FlowWorks/northstar/river_site.py` | river site builder | none (selftest_river_site 0 fail) | - | CLEAN |
| 23 | `src/RimMandrake/FlowWorks/northstar/settings_registry.py` | extensions, validation | REAL: RM_KitSettings (6 fields) and RM_SluiceGateSettings (3) are scribed into the FlowWorks settings file but were missing from site_spec SETTINGS/SETTINGS_SOURCES, so L2 drift, P-B4 and the O2 census never read them. Registered (fix in site_spec.py); 122 registry toggles, O2 sees 123 in 8 classes | 357d29cd31 | CLEAN |

## 4. Other DIRTY files under GSS / FlowWorks / Pyrelands / _Shared

| # | file | findings | fix sha | verdict |
|---|---|---|---|---|
| 24 | `src/RimMandrake/FlowWorks/northstar/site_spec.py` | carries the registry fix above; rest clean | 357d29cd31 | CLEAN |
| 25 | `src/RimMandrake/FlowWorks/northstar/selftest_flowworks_northstar.py` | count 117 -> 122 | 357d29cd31 | CLEAN |
| 26 | `src/RimMandrake/_Shared/LightLedger/LightLedger.cs` | none | - | CLEAN |
| 27 | `src/RimMandrake/_Shared/LightLedger/LightLedgerKernel.cs` | none | - | CLEAN |
| 28 | `src/RimMandrake/_Shared/LightLedger/SelfTest/Program.cs` | none | - | CLEAN |
| 29 | `src/RimMandrake/GimmeSomeSlack/Source/Aerial/AerialMath.cs` | none | - | CLEAN |
| 30 | `src/RimMandrake/GimmeSomeSlack/Source/Aerial/AerialSettings.cs` | none | - | CLEAN |
| 31 | `src/RimMandrake/GimmeSomeSlack/Source/GimmeSomeSlackMod.cs` | none | - | CLEAN |
| 32 | `src/RimMandrake/GimmeSomeSlack/validation.py` | B7c docstring called floor ripple default OFF | 4070b653a4 | CLEAN |
| 33 | `src/RimMandrake/FlowWorks/Source/LiquidTypes/LiquidCorrosion.cs` | DEFECT, ships ON since b5c8547e8b: apparel worn to 0 HP is `pawn.apparel.Remove(piece)`d, never destroyed: the Thing is orphaned (no holder, not destroyed). Vanilla wear-out calls `piece.Destroy()`. Header comments still say it never shipped. NOT fixed: FlowWorks C# is mid-edit by another builder (uncommitted .cs), a rebuild would bake their work into the DLL | - | DIRTY |
| 34 | `src/RimMandrake/FlowWorks/Source/LiquidTypes/LiquidIgnition.cs` | no behaviour defect (inert unless a liquid terrain is flammable); header comments now false ("never shipped, owner's call after a live proof") | - | DIRTY |
| 35 | `src/RimMandrake/_Shared/FlowWorksIrrigation/FlowWorksIrrigationRead.cs` | DEFECT: the irrigation gate reads the map's ActiveFluid, not the cell's own fluid (per-cell identity since LIQUID_BODY_FLUID_IDENTITY_1), so a tar canal off a tar pond waters Pyrelands ash / ExplosiveGrowth soil. Fix needs a fluid-grid read and rebuilds of Pyrelands + ExplosiveGrowth; Pyrelands is mid-edit | - | DIRTY |

## Skipped (another agent mid-edit, or touched in the last 15 min)

FlowWorks Source with uncommitted edits at 08:34: `RM_ExcavationDepth.cs`, `RM_LiquidBody.cs`, `RM_LiquidStock.cs`,
`RM_MapComponent_Excavation.cs`, `RM_PocketGridMath.cs`, `RM_Volume.cs`, `RimMandrakeFlowWorks_DefOf.cs` (and earlier
`CompLiquidConverter.cs`, `RM_LiquidReaction.cs`, `RM_ConversionMath.cs`, `RM_LiquidNetKernel.cs`, SelfTest `PlanChecks.cs`,
`Program.cs`). Committed in the last 15 min: `RimMandrakeFlowWorksMod.cs`, `Rivers/RM_Weir.cs`,
`selftest_flowworks_gpt_c.py` (ec3e21b942); every Pyrelands DIRTY file (`Defs/JobDefs/RM_PyrelandsJobs.xml`,
`Defs/TerrainDefs/AshField.xml`, `ScorchableGround.xml`, `Source/CompFurnaceWarmthAura.cs`, `FireEcologyHook.cs`,
`FurnaceWarmthMath.cs`, `JobDriver_RUT_FireHawkCarryEmber.cs`, `Kernel/RM_BurnKernel.cs`, `Kernel/RM_FireEcoKernel.cs`,
`PyrelandsAshField.cs`, `SelfTest/Fuzz/PyrelandsFuzz.cs`, `SelfTest/Program.cs`, `validation.py`).

## Owed

- The golden FlowWorks trial site's prep snapshot predates the two registered settings classes: its next re-prep (already
  owed after every DLL build) records them; until then P-B4 contract reads them as drift.
- LiquidCorrosion apparel orphaning (row 33) and the irrigation fluid gate (row 35) need a builder with the FlowWorks /
  Pyrelands trees quiet.
