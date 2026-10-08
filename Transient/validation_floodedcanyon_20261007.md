# FloodedCanyon validation (Approach B), 2026-10-07 - DONE, nothing committed

## Kernels (Verse-free, `src/RimMandrake/FloodedCanyon/Source/Kernel/`, all four in RM_FloodedCanyon.csproj; mod code calls them)
- `RM_FloodKernel.cs` - the Dry / Herald / Warned / Flooding phase machine (`Tick`: five beats, staged chimes, schedule + jitter, peakstorm pull, refuge sweep requests), flood begin bookkeeping, the thinned spread of flood cells, chime geometry (far corner, points toward the seed), and `Ledger` (what the flood raised and its exact restore). RM_MapComponent_CanyonFlood.cs is now orchestration (its clocks live in `FloodState`; Scribe keys unchanged, enum names unchanged so saves load).
- `RM_RefugeKernel.cs` - who shelters, what each seeker is told (hold / go / skip / unreachable), the nearest reachable ledge cell (12-probe bound, empty preferred), nearest chime anchor. RM_LedgeRefuge.cs.
- `RM_PanKernel.cs` - the sleeper pan's seal / wake / dig-in state machine. RM_CompPanSleeper.cs.
- `RM_CanyonRulesKernel.cs` - recede-aftermath counts and timers, the biome score (lazy seeded gate), fossil face / depth / deep BFS, recut candidates, seam pick. RM_MapComponent_RecedeAftermath, RM_BiomeWorker_FloodedCanyon, RM_FossilStrata.
- Rejected (engine calls): RM_CrackedLandsFlora, RM_TarruqHushPatch (Harmony), RM_WeatherEvent_DistantFlicker, RM_ExplosiveGrowthBridge (reflection), RM_FloodedCanyonMod (UI), the aftermath spawns and the fossil seam placement (thing spawning), debug actions, sustainers.

## Fuzz
`python3 src/RimMandrake/Utils/selftest_floodedcanyon_fuzz.py [--fuzz-scale F] [--fuzz-seed N] [--fuzz-only flood|cells|refuge|pan|rules]` (project `Source/SelfTest/RimMandrakeFloodedCanyon.SelfTest.csproj`).
- flood (sequences with time steps, storms, setting toggles): only legal phase changes; a flood never begins without the first chime having rung, nor before its time; recede not before the flood's end and the next flood lies in the jitter band with the 2500 floor; chimes in order, each once, never early; herald beats 1,2,3 in order, never early and (settings untouched) never late; Warned entry chooses a seed only when none is pending; the peakstorm pull only moves the flood earlier, once per cycle, not within half a period of a recede, not for a flood already under 60000 ticks away, never inside the warning lead; an inactive cycle does nothing, but a flood under way recedes at once; liveness (floods recur) and tick/target clamps.
- cells: spread <= target, unique, eligible, one 4-connected body starting at the seed (the roar sits on cells[0]), a free field fills to the target; ledger partition (every cell flooded as terrain, raised with its prior, or left), recede restores soil only where flood terrain remains and every fill to its prior exactly; far corner is the farthest, chimes walk toward the seed and clamp.
- refuge: exhaustive 8192-row seeker table, 16-row decision table, nearest-reachable against an independent walk, the 12-probe bound, nearest anchor.
- pan: dig-in after exactly ceil(hours * 2500 / interval) dry checks, water or a flood resets the clock, wake only with water and the setting, re-sleep of a sealed awake pan, nothing for a missing comp or a dead pawn.
- rules: cohort = min(max, cells / 8), timers, salvage rule, biome score formula + the seeded roll spent only when reached and only when the gate is under 1, fossil depth / deep / face sets against an independent multi-source BFS, recut candidates against an 8-neighbourhood oracle, seam bands.
- Seeds: 3000 per family, 2.3 s. `--fuzz-scale 25`: 375,000 cases, 6.3M steps, 47 s, 0 failures (110k floods, 102k recedes, 4.8k peakstorm pulls, 9.6k forced recedes, 278k chimes, 1.9M flood cells, 5.9M fossil faces). Blind check on every transition.

## Mutation (30 planted, 30 caught, restored byte-identical)
`python3 src/RimMandrake/Utils/mutate_kernel_fuzz.py selftest_floodedcanyon_fuzz.py src/RimMandrake/Utils/mutations_floodedcanyon_fuzz.json`. Includes the original defect re-planted (a flood under way never recedes when the cycle is switched off) and: schedule floor lost, peakstorm pull inside the lead / later / every time / on a near flood, herald beats late (first NOT caught: only "not early" was asserted; added a not-late bound), third chime early, flood start/recede early, herald entry or Warned entry mishandling the seed, chime stage restart, spread overshoot, ineligible cells flooded, prior fill lost, refused excavated cell flooded anyway, soil on non-flood terrain, first chime at the near corner, target clamp, seeker/decision/probe-bound errors, pan dig-in late / water not resetting / wake without the setting, cohort size, biome roll spent early, fossil depth cap, seam bands.

## Lint
`python3 src/RimMandrake/Utils/lint_floodedcanyon_defs.py`: 18 defs + 2 patch files, 31 classes, 11 refs, 6 field checks, 29 settings: 0 ERROR, 0 WARN. 4 planted defects caught (csproj omission, missing Scribe, DefOf typo, class typo).

## Defects
- FIXED RM_MapComponent_CanyonFlood.MapComponentTick returned at once when `Active` went false (floodCycleEnabled switched off, or featureInOtherBiomes off on a non-canyon map) EVEN WHILE FLOODING: `RecedeFlood` never ran, so the `WaterMovingShallow` cells, raised excavation fills, the roar sustainer and the cached cell lists stayed until the cycle was switched back on (the flood game condition expires by itself, the terrain does not). The kernel now recedes a flood under way when the cycle goes inactive and reschedules.
- NOTE `RM_MapComponent_RecedeAftermath.OnRecede` called twice before the first cohort / salvage has expired overwrites `cohortDieTick` / `salvageExpireTick`, so the earlier cohort lives (and its salvage persists) until the later deadline. Harmless; lists keep both batches.
- NOTE the chime anchors and herald beats assume `TickManager` steps of 1; a long skip (a caravan day-jump) can fire all three beats and two staged chimes on one tick.

## Repairs to existing tooling
`validation.py` (static checks) scanned the flood clock for three `Refuge?.Sweep()` calls and walked `Source/` for csproj-unlisted files. It now reads the kernel's `step.SweepRefuge = true` requests plus the single `if (step.SweepRefuge) Refuge?.Sweep()` carrier, and skips `Source/SelfTest/`. `selftest_floodedcanyon_static.py` PASSES (0 failures).

## Build
`winbuild.py src/RimMandrake/FloodedCanyon/Source/RM_FloodedCanyon.csproj` -> 0 warnings 0 errors; DLL + .srchash rebuilt, UNCOMMITTED. Not wired into run_selftests.py.
