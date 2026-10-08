# LeaningScrub validation (Approach B), 2026-10-07 - DONE, nothing committed

## Kernels (Verse-free, `src/RimMandrake/LeaningScrub/Source/Kernel/`, all in RM_LeaningScrub.csproj; mod code now calls them)
- `RM_LeanKernel.cs` - heading lock, direction, alignment, scent threat pick, downwind fire neighbours + spread pick, banker's-rounded Step, Shed V cells. RM_TheLean.cs, Walk/Shed use it.
- `RM_SmotherKernel.cs` - claim ticks (saturating), start/remaining, pass gate, due, yield, stack split. RM_SmotherCraft.cs uses it.
- `RM_BlazeKernel.cs` - blaze cluster, converge action, new-blaze rule, stamp reach. RM_FireStamp.cs uses it.
- `RM_GuardianKernel.cs` - disturbance meter, stages, forgiveness, reroost, refill, double-roost yield. RM_SweetlineGuardians.cs uses it.
- `RM_FormsKernel.cs` - scratch clocks, thorn gate, lash, rearing, quench, hoard grow-in sweep, walking-stand march (components, leading edge, runners, cap, tail). RM_VenomvineForms.cs / RM_TwitcherLash.cs use it (Walk and Hoard Sweep were rewritten around it).
- `RM_CoatKernel.cs` - coat rub split, felt store, payout, runway-bloom cooldown + delayed-answer queue. RM_SweetlineScratching/Station/RunwayBloom use it.
- Rejected: RM_SweetlineStation visitor/history, RM_GenStep_SweetlineTrees, RM_SweetlineFelt, RM_VisslerArm, RM_VenomvineRooms, RM_WindCalendar, RM_LeaningScrubMod (UI/settings): all engine calls (pawn lists, jobs, hediffs, map generation); the only pure bits are one-line wrappers.

## Fuzz
`python3 src/RimMandrake/Utils/selftest_leaningscrub_fuzz.py [--fuzz-scale F] [--fuzz-seed N] [--fuzz-only lean|smother|blaze|guardian|forms|walk|coat]` (project `Source/SelfTest/RimMandrakeLeaningScrub.SelfTest.csproj`).
- lean: heading locks once (0 deg is valid); direction is (cos,sin) unit; alignment == double oracle, antisymmetric, distance-free; 3-4 downwind neighbours matching oracle; pick bias 0/off is vanilla, bias 1 always downwind and every neighbour reachable; Step(1) never the origin and mirrors Step(-1); scent = first alive, in-range, cos>=0.7, fleeable person; Shed V cell count formula, all downwind, never the root, one roll per cell.
- smother (sequences): first Start wins, remaining == start+claim-now (no overflow), matures only on a pass with feature on and never early/twice, no due claim survives its pass, yield monotone in growth with the 0.3 floor, stacks sum/limit.
- blaze: cluster index == brute oracle, translation/permutation invariants, dispatch table, one message per blaze (not on drift).
- guardian (sequences): meter in [0,1] and tracks a double ledger, stage == StageOf(meter) always, announce iff stage rose, drop iff full, refused adds change nothing, no forgiveness while raging, full drain takes max(0.5,days)*30 long ticks, double-roost rule antisymmetric and the lowest id is never blocked.
- forms (sequences): scratch spacing >= interval, no scratch of an unarmed/spared pawn, stale-clock prune only after 2500 overdue; lash spacing and 60 floor; rear never shortened; quench spacing; hoard never takes early/corpse-when-off/over capacity, stunted stand leaves its books alone, liveness with room to spare.
- walk: 8-connected stands vs union-find, smothered stand inert, runners at Step(src,k) from grown leading-edge cells only, no duplicates, cap respected, omissions justified, kills only grown cells of stands >1 with free tail, exact kill oracle (cap 0, chance 1), deterministic.
- coat: rub balance (ground+felt within 1 of shed), RoundRandom unbiased, felt store [0,cap] and whole-unit payout; bloom cooldown == independent ledger, answers once, never early, newest first.
- Seeds: default 3000 per family (walk 4000), 2 s. `--fuzz-scale 25`: 550,000 cases, 19.7M steps, 25 s, 0 failures. Blind check: every key transition is counted (scent threats, matured claims, drops, scratches, runners, kills, blooms...) and the run fails itself if one is never reached.

## Mutation (26 planted, 26 caught, all restored byte-identical)
`python3 src/RimMandrake/Utils/mutate_kernel_fuzz.py selftest_leaningscrub_fuzz.py src/RimMandrake/Utils/mutations_leaningscrub_fuzz.json`. Planted e.g. zero displacement aligned, heading 0 as unset, fire window 90 deg, a second smother restarts the clock, huge claim wraps, undersized blaze, stage never falls, two roosts yield to each other, forgiveness while raging, rearing cut short, lash floor lost, smothered stand marches, cap off by one, lone cell dies, felt uncapped, bloom cooldown doubled.

## Lint
`python3 src/RimMandrake/Utils/lint_leaningscrub_defs.py [--quiet] [--mod-dir D]`: 20 defs + 5 patch files, 70 classes, 77 refs, 60 field checks, 2 drivers, 52 settings: 0 ERROR, 1 WARN (RM_SweetlineToken has no art; its def says placeholder). 6 planted defects caught (class typo, field typo, csproj omission, missing Scribe, default mismatch, DefOf typo).
- Shared lint change (`lint_mod_defs.py`): `texpath-resolves` now accepts art that ANY RimMandrake mod ships (venomvine forms borrow EnvironmentalHazards' RM_Venomvine render on purpose) and takes `known_missing_art=` to demote filed placeholders to WARN. Wasteland lint output unchanged.

## Defects
- None that change shipped behaviour found. Latent hardenings now in the kernels: a stack limit < 1 (stack split looped forever / Mathf.Clamp(left,1,0)), and a NaN/huge `smotherDays` (float->int cast wraps negative) both guarded.
- NOTE (harmless) `SweepThorns` prunes scratch clocks at `now % 2500 == 0` but only runs on `now % 15 == 0`, so the prune happens every 7500 ticks, not 2500. Only memory.
- NOTE `FindBlaze` is O(n^2) in open fires every 600 ticks; fine unless thousands burn.
- NOTE smotherYieldFactor 0 still yields 1 wood (Max(1,..)); presumably intended.

## Build
`winbuild.py src/RimMandrake/LeaningScrub/Source/RM_LeaningScrub.csproj` -> 0 warnings 0 errors; DLL + .srchash rebuilt, UNCOMMITTED. Existing `selftest_leaningscrub.py` still run (see below). Not wired into run_selftests.py.
