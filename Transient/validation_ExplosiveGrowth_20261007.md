# ExplosiveGrowth validation (Approach B), 2026-10-07 - DONE, nothing committed

## Kernel (Verse-free, called by the mod with the same expressions)
`src/RimMandrake/ExplosiveGrowth/Source/Kernel/RM_ExplosiveGrowthKernel.cs`
- `RM_EgLedger<K>`: the per-map soak grid, suppression grid and charge records, and the whole 250-tick pass over them (arm what is soaked + mature + growing, step the charge, tell-stage ladder, creak, tremble puffs, fire, stale-plant removal). The component now holds one `RM_EgLedger<IntVec3>` and answers the pass through a private `Sink` (plant lookup, filth/sprout ring, sound, puffs, `RM_TopResolver.Fire`).
- `RM_ExplosiveGrowthKernel` statics: `StepCharge`, `StageFor`, `Hue`, `VisualScale`, `PassDelta`, `ChargeTicks`, `SoakFactor`, `EffectiveTop` (per-top fallback to Churn / None), irrigation/surge `SliceRange` + `NextCursor`, `InSurgeBand`.
- `RM_ChargeRecord` is now `partial` (fields in the kernel, Scribe half in the component); `RM_TellStage` moved to the kernel.
- Call-site edits: `RM_MapComponent_ExplosiveGrowth.cs`, `RM_SoakSources.cs`, `RM_TopResolver.cs`, `RM_ExplosiveGrowth.csproj` (1 Compile line). Files were clean in `git status` before the edit.
- Not extracted (engine calls): `RM_TopResolver` tops (spawn/filth/pawn damage/gas), `RM_SproutRing.CanSprout` (terrain/room/edifice), registry (DefDatabase), Harmony patches.

## Defect fixed while extracting
- A top switched off in settings (a disabled Churn resolves to None) still ARMED: the plant charged, swelled and "fired" nothing, then re-armed immediately, forever (class comment says it should relax). `Sink.TryGetPlant` now reports `soaks` only when `RM_TopResolver.Effective(prof.top) != None`, so such a plant never arms and an existing record is removed. Soak growth boost (`GrowthFactorFor`) unchanged.

## Fuzz
`python3 src/RimMandrake/Utils/selftest_explosivegrowth_fuzz.py [--fuzz-scale F] [--fuzz-seed N] [--fuzz-only ledger|clock|slice|top]`
Project `Source/SelfTest/RimMandrakeExplosiveGrowth.SelfTest.csproj` (net8.0, pulls the one kernel).
- ledger (seeds 1..5000; 30-120 actions over 12 cells): Plant / Remove / SetRate / SetGrowth / Soak / Suppress / Take / DebugSet / Force / Pass / Wait vs an independent array spec. Soak, suppression and every record (id, charge, stage, clock) equal after every action; kernel and spec event multisets (dirty / armed / creak / puff / fire) equal per pass; TrySoak and Take return values equal; invariants: no stale or non-soaking record survives a pass, charge in (0,1) after a pass, a cell is never live-soaked and live-suppressed, IsSoaked/IsSuppressed/GrowthFactor agree with the spec.
- clock (3000): wet+dormant HOLDS exactly, wet+growing advances, dry decays at exactly twice the wet rate, closed-form pass count to 1.0, dormant charge never lost over 500 passes, ladder monotone and exact at all five thresholds both sides, Hue quarter-quantised and zero iff charge <= 0.45, VisualScale = 1 up to 0.15 / bounded / parity only wobbles in the tremble band, PassDelta clamp [1, 2000].
- slice (2000): the 8 slices cover every cell exactly once from any start cursor, n from 0 to 200k; cursor wraps; surge band edges inclusive.
- top (exhaustive 7 tops x 64 flag sets): result is the top or the fallback, a disabled variant never survives.
- Seeds: default 5000 ledger / 3000 clock / 2000 slice (2.8 s, 10.5k cases, 536k steps). `--fuzz-scale 20`: 100,000 ledger + 60,000 clock + 40,000 slice seeds, 10.6M steps, 45 s, 0 failures; armed 32,963 / creak 14,725 / fires 15,934 / soaks refused 341,923 (blind-guard fails the run if arm/creak/fire/refusal never occur).
- Harness lesson: the first large-scale run flagged a "failure" that was the fake game's fire effect (sprout on the neighbour cell) depending on visit order; effect now touches only the fired cell.

## Mutation (17 planted, 17 caught, kernel restored byte-identical)
`python3 src/RimMandrake/Utils/mutate_explosivegrowth_fuzz.py [substring]` (5 s sleep between mutation and run; also the engine the other mods' mutators import).
dormant charge decays (the 2026-09-26 live bug) / dry at wet rate / Suppress keeps the soak / TrySoak ignores suppression / TrySoak shortens a soak / arm without GrowthRate>0 / arm an immature plant / stale plant id kept / fire leaves the record / Hue threshold `>` / Hue floor / slice off by one / surge band edge / Tinder falls to None / prune keeps due entries / GrowthFactor ignores the plant / PassDelta unclamped.

## Lint
`python3 src/RimMandrake/Utils/lint_explosivegrowth_defs.py [--quiet] [--mod-dir D] [--plant-check]` = generic `lint_mod_defs.py` + roster/numbering data checks over the RM roster and the campaign roster (`src/RimUtinni/PlantGrowth`): 2 rosters, 136 plant rows, 7 tops, 5 debug labels, 5 validation paths, 28 classes, 25 settings: 0 ERROR, 12 WARN.
- WARN wired: `RM_IncidentWorker_BloomBurst` has no def in THIS mod - its IncidentDef is `RUT_BloomBurst` in PlantGrowth. Not a defect.
- WARN x9: roster plants with our prefix defined by no Defs folder (RUT_RustPuff x2, RSW_Scrubgrass, RSW_Plant_{HydenockTree,MujaFruit,JoganTree}_Wild, RUT_PaleTree, RUT_PaleMoss, RUT_Placeholder_GreentideGiantTree): skipped silently at load by design (list-every-plausible-name policy), listed so a real typo is visible.
- WARN x2: noSoakBiomes RM_PoisonForest / RUT_PoisonForest are pre-rename names kept on purpose.
- `--plant-check`: 8 planted defects (top typo, unknown child, enum renumbered vs kernel byte literals, stale threshold literal in the component, renamed debug action vs validation.py path, Verse import in the kernel, kernel missing from csproj, CountByTop size) all caught.

## Build
`python3 src/RimMandrake/Utils/winbuild.py src/RimMandrake/ExplosiveGrowth/Source/RM_ExplosiveGrowth.csproj` -> 0 warnings 0 errors; `Assemblies/RimMandrake.ExplosiveGrowth.dll` + `.srchash` rebuilt, UNCOMMITTED. Not wired into run_selftests.py.
