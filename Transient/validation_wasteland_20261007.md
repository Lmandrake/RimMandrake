# Wasteland validation (Approach B), 2026-10-07 - DONE, nothing committed

## Kernels (Verse-free, `src/RimMandrake/Wasteland/Source/Kernel/`, all in RM_Wasteland.csproj)
- `RM_WasteCaskKernel.cs` - cask breach / leak gate / pacing / dose loss / burst; bay seal charge, heat step, containment, leak gate, processing progress, launch verdict ladder, ship check, capacity. RM_WasteCaskBay.cs now calls it (comp bodies keep only engine effects).
- `RM_StormKernel.cs` - fresh-fall memory (cap 4000, overwrite when full), per-batch fall count, fall/dose gates, germination draw count, and the named-storm PHASE MACHINE (Begin/Tick/End events, hold during warning, click interval, hand-off delay). RM_NamedStorms.cs MapComponentTick/BeginPhase now run on `PhaseState` + `PhaseEvent`; RM_MapComponent_WastelandStorms.cs uses the gates.
- `RM_TippingKernel.cs` - Rite of Tipping delivery state machine (pad / miss / fail / complete), one-shot evidence ask, finance hint/grant, schedule, void test, reburial discovery. QuestPart_RM_TippingContract.TryDeliver / DoFinance / Notify_IllegalReburial call it.
- `RM_DoseKernel.cs` - ambient dose falloff + indoor/outdoor, gripper UnitsToTake, processor fullness rate, un-pollute chance. RM_CompAmbientDose / RM_GripperTheft / RM_CompProcessorGatherable call it.
- Rejected: Middenshell (1045 lines, step/crush/tentacle are footprint, passability and thing-spawn calls; the only pure bits are trivial), RM_MiddenshellProcession, BiomeWorker (all Verse state).

## Fuzz
`python3 src/RimMandrake/Utils/selftest_wasteland_fuzz.py [--fuzz-scale F] [--fuzz-seed N] [--fuzz-only cask|storm|tipping|dose]` (net8.0 project `Source/SelfTest/RimMandrakeWasteland.SelfTest.csproj`, built via winbuild staging).
- cask (action sequences vs spec): seal charge in [0,1] and equals the literal drain/regen rule; heat tracks the one-step double recurrence and never overshoots; heat target spec; cask leak gate == spec (never leaks inside a contained bay); bay never pulses while contained; pulse spacing >= interval and LeakDue == `<0 || now>=next`; dose never negative, loses exactly min(per, dose); launch verdict == independent ladder, Safe with casks aboard implies powered+integrity+heat and (when launchIntegrity >= leakThreshold) contained; ship verdict == spec and names the first bad bay; burst gates/floors; processing completes and consumes one cask; units: banker's rounding, capacity, per-cell clamp, breach boundary, drain-to-leak and recontain tick bounds.
- storm: phase state == literal spec after every step (weather change, ticks of 1..50, enable toggles, OnWeatherStart); IsHolding == spec; the storm layer NEVER runs during a named storm's warning; events (Warn/Storm/Disabled) consistent; unleash exactly at start+warn; units: fresh fall cap/overwrite/roll argument (10k adds), FallPerBatch vs double oracle, truth tables, germination draws, click interval monotone, hand-off delay.
- tipping: state vs ledger (done/missed/active/goodwill/silver), asks <= 1, grant <= 1, hint <= 1 and never after a grant, fail only when missed > allowed, finished contract inert, licensed contract completes in exactly N loads, padless in allowed+1 misses, discovery roll lazy and Rand.Value==1.0 safe.
- dose: factor within [toxic*min(1,edge), toxic*max(1,edge)], monotone with distance, zero beyond radius, rim == toxic*edge; UnitsToTake vs long oracle (incl. 3e9 cap); fullness reaches 1 in days*60000/growth ticks (+-3%, float accumulation), off-feed slower.
- Seeds: default 3000 cask / 3000 storm / 3000 tipping / 2000 dose (3.5 s). `--fuzz-scale 25`: 75,001 + 75,001 + 75,001 + 50,000 cases, 51M steps, 62 s, 0 failures. Reached at scale 25: bay pulses 563,226, cask pulses 313,355, processed casks 8,518, storm unleashes 38,757, holdings 173,035, tipping completed 33,877 / failed 39,188 / grants 10,994 / discoveries 57,169.
- A fuzz that never reaches a key transition fails itself (blind check).

## Mutation (20 planted, 20 caught, all restored byte-identical)
`python3 src/RimMandrake/Utils/mutate_kernel_fuzz.py selftest_wasteland_fuzz.py <mutations.json>` (new, generic; sleeps 4 s + touches between runs). Planted: Contained `>=`->`>`; drain halved; LeakDue `>=`->`>`; bay leaks while contained; dose unclamped; launch drops power check; ship check ignores loose casks; cask leaks inside contained bay; powered cooling ignored; IsHolding drops `!unleashed`; unleash off by one; disabled phases still warn; fall cap off by one; fall ignores map area; missed `>=`; finance re-grant; Chance(1) not certain (needs Rand.Value == 1.0); evidence asked every load; rim dosed; UnitsToTake float cast restored. Three were first NOT caught (LeakDue, cooling, Chance) and drove three extra harness checks.

## Lint
`python3 src/RimMandrake/Utils/lint_wasteland_defs.py [--quiet] [--mod-dir D]` (wrapper over new generic `lint_mod_defs.py`, which imports helpers from lint_scarlands_defs.py): 32 defs + 3 patch files, 52 classes, 47 class/def refs, 20 field checks, 2 drivers, 33 settings: 0 ERROR, 1 WARN.
- WARN `brineDepositsEnabled`: setting, label and Scribe exist, no code reads it (its own tooltip says NOT YET WIRED; validation.py references it as a toggle). Dead toggle until a GenStep reads it.
- 6 planted defects caught (class typo x2, field typo, missing Scribe, key default mismatch, csproj omission).

## Defects
- FIXED (latent) RM_GripperTheft.UnitsToTake: `Mathf.FloorToInt(maxCarryMass / unitMass)` cast a float quotient to int; above 2^31 (a feather-light item with a large carry cap) it wraps negative and the gripper silently refuses the theft. The kernel floors in double and clamps. Fuzz plants the old cast and catches it.
- FIXED (latent) QuestPart_RM_TippingContract.TryDeliver is public (debug/state reads) and had no state guard: calling it on a finished or failed contract delivered a fresh load, paid goodwill and could re-fire Complete. It now returns false unless the part is Enabled.
- NOTE (design, not changed) a breached cask inside an UNcontained bay makes both the cask and the bay pulse (double pollution/gas). Probably intended ("a leaking bay is worse"); say so if not.
- NOTE float accumulation: processor fullness (float += ~1e-6/tick) drifts up to ~1.3% from days*60000 ticks; harmless, only a stall below ~6e-8 per tick.

## Build
`python3 src/RimMandrake/Utils/winbuild.py src/RimMandrake/Wasteland/Source/RM_Wasteland.csproj` -> 0 warnings 0 errors; `Wasteland/Assemblies/RimMandrake.Wasteland.dll` + `.srchash` rebuilt and left UNCOMMITTED. `selftest_wasteland.py` (suite) still passes. Not wired into run_selftests.py.
