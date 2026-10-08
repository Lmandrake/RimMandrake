# BlueDesert validation (Approach B), 2026-10-07 - DONE, nothing committed

## Kernels (Verse-free, `src/RimMandrake/BlueDesert/Source/Kernel/`, both in RM_BlueDesert.csproj; mod code calls them)
- `RM_BlueKernel.cs` - cold-sink heat/ice step (Absorb), melt drips, clarity stage, thaw counter + stack clamp, the weighted pick shared by thaw debris and ablation corpses, vhaulk detonation gate / EMP trap / part kill, plant-charge warm counter, ruled-weather toggle, vhaulk road cell + departure/stay timing + crop-to-growth, ablation timeline, ossivel choir (singers, intruders, silence hold, centroid), virr nearest + pitch. RM_ColdSink, RM_BlueIceThaw, RM_VhaulkDetonation, BlueDesertLife, RM_BlueDesertWeatherTable, RM_VhaulkRoad, RM_AblationSalvage, RM_BlueDesertSoundscape use it.
- `RM_MurrekKernel.cs` - the post-drift reseed plan (nearest reachable burrow per idle murrek with spacing, new-murrek allowance against the cap) and the buried murrek's 30-tick decision. RM_MurrekDrift.cs.
- Rejected (engine calls): RM_BlueDesertMod (settings UI), the fauna/flora comps that only forward to explosions, effecters and sound sustainers, HediffComp wrappers, DeathActionWorker/IngestionOutcomeDoer overrides, RM_Building_ColdSinkRack graphics, Murrek job toils.

## Fuzz
`python3 src/RimMandrake/Utils/selftest_bluedesert_fuzz.py [--fuzz-scale F] [--fuzz-seed N] [--fuzz-only cold|thaw|rules|murrek]` (project `Source/SelfTest/RimMandrakeBlueDesert.SelfTest.csproj`).
- cold (sequences, against a model of the vanilla cooler step): HEAT CONSERVATION (what the room loses == what the ice absorbs, every tick and in total), never absorbs more than the ice holds, never cools past the target, no ice used when the room is not above target (and a warming step can never consume or add ice), melt store in [0, blocksPerCan) and drips account for every melted block, clarity stage follows the 50 / 10 percent boundaries.
- thaw: a roll every blocksPerRoll blocks exactly, counter in range; weighted pick picks in proportion to weight, never a zero or negative weight, never from nothing; stack clamp.
- rules (sequences + exhaustive tables): detonation gate (heat or lightning or EMP or gate off), EMP trap, part kill, plant charge needs two warm long-ticks in a row and resets cool/disabled, departure fires once and re-fires only after a replaced job, road cell filter, ablation timeline (never backwards, call and exposure once, exposure never before the silhouette), choir (silence hold after an intruder, singer minimum, centroid inside the singers' bounds, gated choir inert), nearest virr and pitch.
- murrek: plan == independent oracle (nearest-first, 12 candidates, reachability, spacing) on random drifts, one burrow per murrek, only eligible murrek, every new burrow/spawn keeps the spacing from everything taken before it, spawns <= min(roll, cap - present), none when the ecosystem is full, exhaustive 512-row buried-check table.
- Seeds: 3000 per family, 0.4 s. `--fuzz-scale 25`: 300,000 cases, 7.9M steps, 8 s, 0 failures (1.1M absorbs, 148k drips, 10.4M thaw counts, 525k detonation rows, 158k burrows, 34k spawns). Blind check on every transition.

## Mutation (26 planted, 26 caught, restored byte-identical)
`python3 src/RimMandrake/Utils/mutate_kernel_fuzz.py selftest_bluedesert_fuzz.py src/RimMandrake/Utils/mutations_bluedesert_fuzz.json`. Planted: rack absorbs beyond its ice, cold per block 0, drips doubled, warming step consumes ice, ice use halved, clarity boundary, roll one block late, negative weights, no stack limit, EMP no longer detonates, heat gate inverted, EMP trap hits the dead, charge needs 3 warm ticks, disabled charge keeps warmth, departure not restarted, road over temp terrain, exposure on the silhouette time, silence hold halved, intruder radius, farthest virr, pitch unclamped, spacing boundary (first NOT caught: the oracle reused the kernel's own Clear; now an independent spec), spawn allowance ignores present murrek, spawns into a full ecosystem, only one candidate tried, tired buried murrek stays down.

## Lint
`python3 src/RimMandrake/Utils/lint_bluedesert_defs.py`: 21 defs + 2 patch files, 42 classes, 65 refs, 31 field checks, 1 driver, 25 settings: 0 ERROR, 0 WARN. 3 planted defects caught (csproj omission, missing Scribe, class typo).

## Defects
- None that change shipped behaviour in the extracted logic.
- Hardened: `RM_CompColdSink` consumed `-tempChange * cells / ColdPerBlock` ice without a sign guard; a warming (positive) step, impossible from the vanilla cooler call today, would have called ConsumeFuel with a NEGATIVE count and added ice. The kernel refuses it.
- Hardened: the cold sink dripped one thing PER drip; kept, but the count of cans per drip is now `max(1, cansPerMelt)` in one place.
- NOTE `RM_JobDriver_MurrekBurrow`/Reseed spawn allowance counts murrek present on the map (`maxMurrekOnMap - murrek.Count`); murrek buried under sand are spawned pawns so they count, as intended.
- NOTE `RM_CompPlantCharge` kills on the second warm long-tick, so a plant is condemned at ~2 * 2000 ticks above the threshold; a one-tick warm spike never kills.

## Build
`winbuild.py src/RimMandrake/BlueDesert/Source/RM_BlueDesert.csproj` -> 0 warnings 0 errors; DLL + .srchash rebuilt, UNCOMMITTED. `selftest_bluedesert.py` ALL OK. Not wired into run_selftests.py.
