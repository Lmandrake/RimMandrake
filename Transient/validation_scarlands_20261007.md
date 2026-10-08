# Scarlands validation (Approach B), 2026-10-07 - DONE, nothing committed

## Kernels (all Verse-free, called by the mod with the same expressions)
- `src/RimMandrake/Scarlands/Source/Kernel/RM_AerosolKernel.cs` - screen radius (empty gel halves), liveness, coverage union `Screened<T>`; RM_CompAerosolScreen now implements `IAerosolScreenView` and `IsPositionScreened` is one kernel call.
- `.../Kernel/RM_RingKernel.cs` - condition roll (0.7 working / 0.3 failing), liveness, 40-cell wake, evaluate/salvage/repair eligibility and transitions; the `RingCondition` enum moved here.
- `.../Kernel/RM_SettlingKernel.cs` - calm / strong-wind hysteresis counters and the buried-ordnance reveal rule (60% strict, 1 relaxed).
- Why these: aerosol union and ring state machine were asked for and are the new, branchy code; the Settling detector was cheaper than Geiger/lift front (pure counters) and gave the reveal rule's float `open*0.6f` an exhaustive check. Geiger choir and lift front not done (mostly Verse state, little pure logic).
- Call-site edits (files were clean in `git status` before each edit): RM_AerosolScreen.cs, RM_WarscarRings.cs, RM_WarscarSalvage.cs, RM_Settling.cs, RM_Warscar.csproj (3 Compile lines). RM_GlowerShield.cs untouched.

## Fuzz
`python3 src/RimMandrake/Utils/selftest_scarlands_fuzz.py [--fuzz-scale F] [--fuzz-seed N] [--fuzz-only aero|ring|settle|reveal]`
- Project: `Source/SelfTest/RimMandrakeScarlands.SelfTest.csproj` (net8.0, pulls the three kernels only).
- aero: kernel vs brute-force lattice oracle (double math, quarter-valued radii so float r*r is exact); setting off / null map screens nothing; order independence; adding a screen only widens, removing only narrows; radius x1.5 widens, x0.5 narrows; screens on another map never count; Radius/IsLive truth tables; 3-4-5 boundary.
- ring: action sequences (Spawn, Evaluate, Salvage, Repair, Engine, Lift, wake/salvage setting toggles) vs a literal spec ledger; dead-def always Dead and live-def never Dead; Failing ring never holds a dome; dead ring hums iff setting && woken && spawned; wild rings never repairable; salvage needs evaluated+wild; Dead strips, others uninstall with condition unchanged and evaluated; repair only Failing->Working on a player ring; wake lattice exact at 40 cells; 100k-roll Working fraction ~0.7; replay determinism; shrinking.
- settle: random wind streams with exact-threshold and 1-ulp samples vs a consecutive-sample oracle; start only after ceil(10*hours) calm samples, end only after the strong-wind run; liveness.
- reveal: exhaustive open 0..8 x film x relaxed vs exact 60% rational; monotone in film; relaxed superset of strict.
- Seeds: default 4000 aero / 4000 ring / 3000 settle (1.5 s, 11k cases). `--fuzz-scale 25`: 100,001 aero + 100,001 ring + 75,000 settle seeds, 136M steps, 17.5 s, 0 failures. Ring tallies at that scale: stripped 74,492 / uninstalled 148,916 / repaired 34,120; aero boundary cells exercised 144,376.
- No real defect found in the four kernels.

## Mutation (14 planted, 14 caught, all restored byte-identical)
Covers `<=`->`<`; dry-gel 0.5->0.75; IsLive drops hasPowerTrader; Screened drops `!enabled`; RollLive 0.7->0.75; CanRepair drops `!wild`; Salvage strips Failing not Dead; SalvagedCondition laundered to Working; EngineWakes `<=`->`<`; CanSalvage drops `evaluated`; dead-ring liveness drops shipWakesLine; reveal 0.6->0.5; calm `<`->`<=`; ShouldEnd `>=`->`>`. Needs sleep 4 + touch between runs (winbuild stale-DLL trap, same as the Bazaar note).

## Lint
`python3 src/RimMandrake/Utils/lint_scarlands_defs.py [--quiet] [--mod-dir D]` - 60 defs + 4 patch files, 133 classes, 119 class/def refs, 28 field checks, 13 drivers, 81 settings: 0 ERROR, 8 WARN. 6 planted defects (type typo x2, field typo, missing Scribe, key/default mismatch, csproj omission) all caught.
- WARN `biomeRarityFactor`: slider and label only; nothing in Scarlands code applies it to the biome (dead setting unless another mod reads it).
- WARN `crossBiomeEnabled/Everywhere/BiomeList/Coverage`: Scribed, one checkbox for Enabled, but no code reads any of them; three have no UI at all.
- Not defects: GetNamedSilentFail("RM_ReactionLiquor*") lives in FlowWorks; the lint skips those.

## Build
`python3 src/RimMandrake/Utils/winbuild.py src/RimMandrake/Scarlands/Source/RM_Warscar.csproj` -> 0 warnings 0 errors; `Assemblies/RimMandrake.Warscar.dll` + `.srchash` rebuilt and left UNCOMMITTED (srchash reads +dirty until committed with the source).
Not wired into run_selftests.py (neither is the Bazaar fuzz).
