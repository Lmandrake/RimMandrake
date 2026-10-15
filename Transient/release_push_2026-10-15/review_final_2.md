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

## 3. Pyrelands, _Shared, Utils

| # | file | reachable | findings | fix sha | verdict |
|---|---|---|---|---|---|
| 31 | `src/RimMandrake/Pyrelands/Source/RM_PyrelandsMod.cs` | settings | none (the cross-biome builder's new label read too) | - | CLEAN |
| 32 | `.../Pyrelands/Source/FireEcologyHook.csproj`, `SelfTest/Fuzz/PyrelandsFuzz.cs`, `SelfTest/Fuzz/RimMandrakePyrelands.Fuzz.csproj` | build / offline fuzz | none; `selftest_pyrelands_fuzz.py` OK (15602 cases) | - | CLEAN |
| 33 | `.../Pyrelands/validation.py` | the Pyrelands live suite | none | - | CLEAN |
| 34 | `.../Pyrelands/diag/burrow_trials.sh`, `.hashignore`, `Languages/English/Keyed/RM_Pyrelands_CrossBiome.xml` | diag / packaging / text | none | - | CLEAN |
| 35 | `src/RimMandrake/Utils/selftest_settings_screens.py` | offline settings-screen check (GSS, FlowWorks hoses, Pyrelands among 101 mods) | DEFECT: MODS held 28 duplicate keys (Droidworks x6, GizkaStowaway x5, Sarlacc x5, UtinniPatches x4, UnfinishedLine x3, FallLineArrivals, PyrelandsMechanics, ScarlandsLadder x2), merge artifacts; Python keeps only the last, so an edit to an earlier copy silently did nothing (ScarlandsLadder's two copies named different .cs files). Deduplicated keeping the last of each: the effective table is byte-for-byte the same dict; 822/822 | 0f6ecb6f62 | CLEAN |

## 4. Test harness Python

| # | file | reachable | findings | fix sha | verdict |
|---|---|---|---|---|---|
| 36 | `src/RimMandrake/GimmeSomeSlack/validation.py`, `validation_aerial.py`, `validation_style.py` | GSS live/offline suites | none; validation.py offline 9/9, validation_style.py --offline green | - | CLEAN |
| 37 | `src/RimMandrake/GimmeSomeSlack/northstar/proof_all.py` | GSS north-star gate | none (note, scope frozen: DECLARED_ROWS omits M15d, M19m, M17) ; --offline-gate green | - | CLEAN |
| 38 | `src/RimMandrake/FlowWorks/validation.py`, `northstar/site_spec.py`, `northstar/extensions.py`, `northstar/selftest_flowworks_northstar.py` | FlowWorks suites | none; selftests green | - | CLEAN |
| 39 | `src/RimMandrake/FlowWorks/northstar/validation_v2.py` | FlowWorks v2 suite | FALSE comments/one row message still described pre-unify ponds (W2R 2-cell cap 10, W2 cap 5); now 4-cell cap 8 and "W2 (its capacity)". Note: J phase ignores set_pawn_skill `success`, caught downstream by set_work_priority, not live | f47381e9ec | CLEAN |
| 40 | `src/RimMandrake/FlowWorks/review_map_coverage.py` | review_map.py --plan | DEFECT: pit ramp art (04657a349b) had no coverage rule, so --plan failed 4 uncovered; rule added, COVERAGE.md/KEYSHEET regenerated | 7674f8ab35 | CLEAN |
| 41 | `GimmeSomeSlack/.hashignore`, `FlowWorks/.hashignore`, `Pyrelands/.hashignore`, `GimmeSomeSlack/review/gss_art_manifest.json`, `FlowWorks/review_map_stations_visuals.json`, `FlowWorks/northstar/player_missions_spec.json` | packaging / review map / player_missions.py verify | none | - | CLEAN |

## 5. Bridge companion files the three mods' tests call

| # | file | tools used | findings | fix sha | verdict |
|---|---|---|---|---|---|
| 42 | `JawaBenchMapInfoTools.cs` | map_info | FALSE comment: said Map.Biome can diverge from the tile after world_tile_set; it reads PrimaryBiome live (only a pocket map differs) | e1e2c21dee | CLEAN |
| 43 | `JawaBenchAwarenessCore.cs` | awareness chain | comment named a nonexistent JawaBenchAwarenessHooks.cs (it is JawaBenchAwareness.cs) | e1e2c21dee | CLEAN |
| 44 | `JawaBenchSocietyTools.cs` | pawn_severity_adjust (GSS/FlowWorks playtests) | DEFECT: a negative offset that takes a hediff to 0 removes it, and the tool reported that working push as a failure; now success, removed=true. Compiled (--gm), not deployed | 1315730754 | CLEAN |
| 45 | `JawaBenchTerrainTools.cs` (7,050 lines) | set/get_terrain_batch, spawn/destroy_batch, list_pawns/things, damage, order_pawn, roof, get_def(s), inspect_string … | none | - | CLEAN |
| 46 | `JawaBench{ColonyNameTool,ModSettingsFieldTools,QuietSiteTools,TargetFuelTools,ReviewLabels,BedTools,NorthstarTools,NeedsTools,ResearchTimeTools,StorytellerTools2,SimTools,VitalsTools,Vitals,VitalsCore,Awareness,AwarenessTools,GroupTools,SituationalTools,EventTools,PawnTools,WorldTools}.cs` (21) | the mods' validation/playtest calls | none | - | CLEAN |

Already CLEAN when checked (another reviewer today): JawaBenchFlowWorks{,Northstar,Pulse,JobProbe,Playtest,PlaytestHose,PlaytestScenes}Tools/.cs, JawaBenchGssPlaytest.cs, JawaBenchCompanionProbeTools.cs, prove_flowworks_pulse.py.

## Skipped: uncommitted edits by another agent

`src/RimMandrake/bridgetools/JawaBench.BridgeTools/JawaBenchPawnKitTools.cs`: uncommitted edits in the tree by another agent; not reviewed.

## Skipped: run records and data no test or game reads

Run-record JSONs; `art_source` sh/jobs/html/json; `review/*.md` and the keysheet docs (human-read); `FlowWorks_review.decisions.json`, `visual_principles_decisions.json`; `player_missions_BRIEF.md`.

## Still DIRTY, and why

- `JawaBenchPawnKitTools.cs`: another agent's uncommitted edits.
- Bridge files no GSS/FlowWorks/Pyrelands test calls, not reached tonight: JawaBenchTps* (13), JawaBenchHealth{,Core,Profiler,Tools}, ArgGuard, CompanionSafety, HookGuard, Init, MapCompTiming, CacheTools, DeepfireTools, ArtboardTools, ShadeGrid/ShadeProbeTools, HostileTools, ProjectileTools, ProofHookTools, CathedralAttitudeTools, StorytellerCompsTools.
- Other GSS/FlowWorks/Pyrelands/_Shared non-JSON files: CLEAN except docs and art_source (human-read, see Skipped).
