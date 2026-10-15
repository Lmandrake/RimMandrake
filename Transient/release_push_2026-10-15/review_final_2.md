# Independent full-file code review, pass 2 — release push 2026-10-15 (BENCH reviewer)

Owner, 2026-10-15: "please ensure that full clean/dirty code reviews are provided for these files before then".
Every row is a FULL-FILE read by a reviewer who did not write the code (lesson d75b357e0c2d). Verdict =
`code_review_status.py check` after the mark. Sweep at start: 337 DIRTY of 852 tracked text files under
GimmeSomeSlack/FlowWorks/Pyrelands/_Shared, plus 21 bridge companion files those mods' tests call.

## 1. GimmeSomeSlack C# (gss_gpt_fixes.md list + sweep)

| # | file | reachable | findings | fix sha | verdict |
|---|---|---|---|---|---|
| 1 | `src/RimMandrake/GimmeSomeSlack/Source/Aerial/AerialMath.cs` | SelfTest-compiled; every aerial span | doc: AssignTerminals' summary was attached to TerminalSig (two summaries on one member) | 4588414c2f | CLEAN |
| 2 | `.../Source/Aerial/RM_MapComponent_Aerial.cs` | MapComponent, every map | none | - | CLEAN |
| 3 | `.../Source/RM_MapComponent_CordGraph.cs` | MapComponent, every map | FALSE comment: RipplesNow said floor ripple "default OFF" (ON since 2026-10-15, GimmeSomeSlackSettings.floorRipple = true) | 4588414c2f | CLEAN |
| 4 | `.../Source/Core/CordBuilder.cs` | cord lay | doc: PileConnectors' summary was attached to MaxPileCables | 4588414c2f | CLEAN |
| 5 | `.../Source/Core/CordGraph.cs` | cord graph | none | - | CLEAN |
| 6 | `.../Source/Core/CordAudit.cs` | SelfTest + live artfit | none | - | CLEAN |
| 7 | `src/RimMandrake/_Shared/SlackGeometry/CordLayer.cs` | GSS + FlowWorks hoses | none | - | CLEAN |
| 8 | `.../Source/GimmeSomeSlackMod.cs` | settings | doc: Apply's summary was attached to appliedPrint | 4588414c2f | CLEAN |
| 9 | `.../Source/GimmeSomeSlackProbe.cs` | validation.py live channel | `set:` with an unknown field returned hand-built JSON (field name unescaped, no cmd); now J.S like every other error | 4588414c2f | CLEAN |
| 10 | `.../Source/Aerial/AerialProbe.cs` | validation_aerial.py channel | none | - | CLEAN |
| 11 | `.../Source/Aerial/CompAerialAnchor.cs` | every mast/bracket | none | - | CLEAN |
| 12 | `.../Source/Aerial/ConduitStyles.cs` | SelfTest-compiled run rules | none | - | CLEAN |
| 13 | `.../Source/Aerial/ConduitStylePicker.cs` | build menu, patches | none | - | CLEAN |
| 14 | `.../Source/Aerial/RM_MapComponent_ConduitRuns.cs` | run rule | doc: two summaries on one field | 4588414c2f | CLEAN |
| 15 | `.../Source/Aerial/ConduitStyleProbe.cs` | validation_style.py | none | - | CLEAN |
| 16 | `.../Source/Aerial/StyleProbeAerial.cs` | validation_style.py | none | - | CLEAN |
| 17 | `.../Source/SectionLayer_RM_MessyCords.cs` | every section | none | - | CLEAN |
| 18 | `.../Source/SelfTest/GptPreReleaseChecks.cs` | offline suite | none (note: a few "can-fail" rows are arithmetic tautologies, e.g. `30 - 35 <= 0`; B15 timing row is wall-clock and could flake on a loaded host) | - | CLEAN |
| 19 | `.../Source/SelfTest/Program.cs`, `AerialSelfTest.cs`, both GSS csproj, `GimmeSomeSlack/.hashignore` | offline suite / build | none | - | CLEAN |
| 20 | `_Shared/LightLedger/SelfTest/*.csproj`, `_Shared/SettingsKit/SelfTest/*.csproj` | offline suites | none | - | CLEAN |

GSS DLL rebuilt from committed source + the fixes above (no other uncommitted GSS source in the tree); `selftest_gimmesomeslack.py` 682/682.

## 2. FlowWorks C#, defs, generator

| # | file | reachable | findings | fix sha | verdict |
|---|---|---|---|---|---|
| 21 | `src/RimMandrake/FlowWorks/Source/Hose/HoseMath.cs` | SelfTest-compiled; every hose lay | none | - | CLEAN |
| 22 | `.../FlowWorks/Source/RM_MapComponent_Excavation.cs` | MapComponent, every map | FALSE header: "superdeepTrap.Tick (only while a D=4 cell exists)"; it also runs under the relative climb rule while anything is dug or a dry bed is a hollow, and RM_PocketGrid.Tick runs every tick | c0b0cba109 | CLEAN |
| 23 | `.../FlowWorks/Source/RM_StockMath.cs`, `RimMandrakeFlowWorks_DefOf.cs` | stock model / DefOf | none | - | CLEAN |
| 24 | `.../FlowWorks/Source/RimMandrake_FlowWorks.csproj` | build | build line told a builder to run dotnet against `D:\Luke\dev\RimMandrake`, the read-only mirror; now winbuild.py | c0b0cba109 | CLEAN |
| 25 | `.../FlowWorks/Source/Superdeep/RM_PitRamp.cs` | ramp building | FALSE: "ART: PLACEHOLDER (vanilla UI/Overlays/Arrow)"; real Graphic_Multi art installed at 04657a349b | c0b0cba109 | CLEAN |
| 26 | `.../FlowWorks/Source/SelfTest/{GptFixesAChecks,HoseHoldChecks,PlanChecks,PondReturnChecks,Program,ReviewFixChecks,SettleChecks,TransferChecks}.cs` | offline suite | none | - | CLEAN |
| 27 | `.../FlowWorks/Source/SelfTest/RimMandrakeFlowWorks.SelfTest.csproj` | offline suite | "Direct invocation" pointed dotnet at the read-only mirror (would test origin/main, not the clone) | 94c8f530e1 | CLEAN |
| 28 | `.../FlowWorks/Tools/generate_liquid_suite.py` | generator of the liquid terrain/registry/bottles/looks | stale note "FlowWorks_Fluids.xml ships only water and tar" (13 FluidDefs now); regenerated in a scratch copy: all 23 outputs byte-identical | 94c8f530e1 | CLEAN |
| 29 | `.../FlowWorks/Defs/LiquidTypes/TerrainDefs/*.xml` (16 generated + RM_Churnmud, RM_TarGlass read too) | game | generated outputs byte-identical to the generator | - | CLEAN |
| 30 | `.../FlowWorks/Defs/Canals/TerrainDefs/FlowWorks_Terrain.xml` | game | FALSE player text: very deep pit "without a ladder standing in the hole, it is not climbing out" (pit ramps ship ON, pitRampsEnabled = true) | 94c8f530e1 | CLEAN |

FlowWorks DLL rebuilt from committed source + the fixes (no other uncommitted FlowWorks source in the tree); `selftest_flowworks_stock.py` 356/356 + hose 130/130 + 342/342.
Already CLEAN when checked (another reviewer, after the builds): RM_MapComponent_Hoses.cs, RimMandrakeFlowWorksMod.cs, RM_NorthstarProofs.cs, CliffMaskChecks.cs.

## 3. Pyrelands, _Shared

| # | file | reachable | findings | fix sha | verdict |
|---|---|---|---|---|---|

## 4. Test harness Python

| # | file | reachable | findings | fix sha | verdict |
|---|---|---|---|---|---|

## 5. Bridge companion files the three mods' tests call

| # | file | tools used | findings | fix sha | verdict |
|---|---|---|---|---|---|

## Skipped: uncommitted edits by another agent

## Skipped: run records and data no test or game reads

## Still DIRTY, and why
