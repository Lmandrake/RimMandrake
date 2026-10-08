# Greentide validation (Approach B), 2026-10-07 - DONE, nothing committed

## Kernels (Verse-free, `src/RimMandrake/Greentide/Source/Kernel/`, all in RM_Greentide.csproj; mod code calls them)
- `RM_SwallowKernel.cs` - churnmud swallow: dwell clock + prune (Dwell.Scan), burial merge (Bury), dig-out in stack-limit chunks with remainder kept (DigOut), dig effort. RM_MapComponent_MudSwallow / RM_JobDriver_DigOutBuried use it; `RM_BuriedCache` is now a typed view over the kernel's `Cache` (same Scribe keys, saves load).
- `RM_MireKernel.cs` - one pawn's RM_Mired severity per 60-tick check (gain, struggle, stuck struggle, decay, removal). RM_MapComponent_TerrainMire.
- `RM_LadderKernel.cs` - greatbole harvest-ladder thresholds with hysteresis, once-only catastrophe. RM_CompGreatboleHarvestLadder.
- `RM_VurrakKernel.cs` - false-bank contact verdict, per-check gate, reveal hold, first-reveal pause. RM_CompBankAmbusher.
- `RM_RulesKernel.cs` - biome score, cross-biome opt-in + list parse + mud coverage, greatbole seedling growth + water recheck, Roil toggle, thurrock tuning, fever mark / frenzy candidate / frenzy dose, stellock felled/branch/duration. BiomeWorker, Mod.AppliesToBiome, CrossBiomeChurnmud, Plant_Greatbole, DensityApplier, ThurrockAuraApplier, fever + stellock comps.
- Rejected (engine calls): RM_GreatboleServants (ritual target workers), RM_Proj_GrenadeStenchSmoke, WorkGivers / JobDriver_FreeMired (toils), RM_Weather overlay (rendering), RM_PatchOperationGreentideSettingGate, the greatbole catastrophe body (damage, spawn, faction goodwill), Fruitfall incident (spawning), Mod.cs UI.
- Breaklight / wet-bulb / Roil weather: XML defs only (WeatherDef, GameConditionDef, HediffDef, IncidentDef; checked by the existing `validation.py` spine chain), no C# beyond the render overlay and the Roil toggle (extracted). Nothing else to extract.

## Fuzz
`python3 src/RimMandrake/Utils/selftest_greentide_fuzz.py [--fuzz-scale F] [--fuzz-seed N] [--fuzz-only swallow|mire|ladder|vurrak|rules]` (project `Source/SelfTest/RimMandrakeGreentide.SelfTest.csproj`).
- swallow (sequences): scan verdict == independent first-seen ledger; ITEM MASS CONSERVATION (items + buried + dug out == created, per def, after every step); no two caches per (cell, def, stuff); a stack is filed under its own key; every placed chunk <= the def's stack limit; remainder of a failed placement stays buried; dig designation present iff something is buried at the cell.
- mire: severity in [0,1] on mire, struggle only half step (never when stuck), stuck pawn struggles at a tenth of the chance (measured over uniform rolls), at most one roll per check, off-mire decays exactly and removes at 0, fill time == ceil(1/rate).
- ladder: shaking/healing fire on the way up and re-arm only below threshold minus dead-zone, catastrophe at most once and only when enabled, a finished ladder is inert, == spec each poll.
- vurrak: verdict == spec (first heavy beats earlier light), exhaustive 512-row gate table, lying down waits out the hold, first reveal pauses once and only with a colonist there.
- rules: biome score == formula, boundaries, monotone, water -100; list parse with separators/blank entries; native biome never cross; coverage conversion is a fair fraction; seedling table and recheck clock; Roil toggle (lock == row == enabled, idempotent, never invents a row); thurrock interval/pace floor; truth tables for mark / candidate / dose (healing severity never scaled) / branch / duration.
- Seeds: default 3000 per family, 2.5 s. `--fuzz-scale 25`: 375,000 cases, 12.2M steps, 38 s, 0 failures. Blind check on every key transition (buried, merged, partial digs, struggles, drops, rearms, strikes, reveals, marks...).

## Mutation (24 planted, 24 caught, restored byte-identical)
`python3 src/RimMandrake/Utils/mutate_kernel_fuzz.py selftest_greentide_fuzz.py src/RimMandrake/Utils/mutations_greentide_fuzz.json`. Includes planting BOTH original defects (dig-out ignores stack limit; dig-out clears the designation over remaining caches). Two were first NOT caught (different-stuff merge; thurrock pace floor) and drove two extra checks.

## Lint
`python3 src/RimMandrake/Utils/lint_greentide_defs.py`: 44 defs + 4 patch files, 50 classes, 73 refs, 43 field checks, 2 drivers, 33 settings: 0 ERROR, 3 WARN, identical to the committed baseline. `crossBiomeEverywhere` / `crossBiomeBiomeList` are false positives (their only reads are inside the settings class's own AppliesToBiome, which the lint excludes); `canopySwarmEnabled` is a documented deliberate no-op (placement not built, GREENTIDE_CANOPY_SWARM_1).

## Defects
- FIXED RM_MapComponent_MudSwallow.DigOut put each merged cache back as ONE Thing whose stackCount can exceed the def's stack limit (Bury merges same def+stuff at a cell, so three buried stacks of 75 came back as a stack of 225). It now returns stacks of at most the limit.
- FIXED DigOut removed the dig designation even when a cache failed to land (blocked cell): the cache stayed in the buried list with no designation, so nothing could ever dig it out again until another item was swallowed on that cell. The designation now stays while anything is still buried there, and a partly landed cache keeps only its remainder.
- NOTE (design, not changed) a buried item comes back as a fresh Thing: quality, hit points, colour, ingredients, tainted/ownership are lost (the cache stores def, stuff, count only). "Nothing is ever destroyed" is true of count only.
- NOTE biome score bounds: temperature max and elevation max are inclusive, rainfall max exclusive. Probably unintended but harmless.
- NOTE FrenzyDose: base.DoIngestionOutcomeSpecial throwing would leave `severity` scaled (no try/finally). Unlikely.

## Build
`winbuild.py src/RimMandrake/Greentide/Source/RM_Greentide.csproj` -> 0 warnings 0 errors; DLL + .srchash rebuilt, UNCOMMITTED. `selftest_greentide_spine.py` re-run and PASSES after one repair: its ladder chain text-scans the C# for the old inline state machine, so `validation.py` (`_LADDER_KERNEL`, `ladder_findings`) and the six `cs_break` strings in `selftest_greentide_spine.py` now read comp + `Kernel/RM_LadderKernel.cs` together. Not wired into run_selftests.py.
