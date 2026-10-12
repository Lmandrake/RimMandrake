# PYRE_RUINS_DIAGNOSE_JUNKYARD_STAYS_PRISTINE (presumed MOD, Pyrelands / GenStep_ScorchPyrelandsRuins)

`pyre_ruins_scorched` FAIL 2026-10-12: 3x3 footprints at 10 sampled unowned artificial buildings are 16% ash (map 8%), want
>= 50%. The footprints still carry ruin floors: TileLimestone 9, FlagstoneLimestone 2, TileSlate 1, TileSandstone 2,
AncientConcrete 15 (`Transient/bench_live_20261012/pyre_ns.log`). The sampled defs are mostly 1.6 ancient junk (AncientAPC,
AncientRustedJeep, AncientPodCar, AncientPipelineSection, AncientWarspiderRemains, ...).

`GenStep_ScorchPyrelandsRuins` (FireEcologyHook.cs, order 760) scorches only `MapGenerator.UsedRects` -- ScatterRuinsSimple
(750) and mutator structures. Ancient-junk gensteps that run later or never register a used rect are left pristine, and
surviving tile floors suggest some ruin rects were not scorched either. The walk bar says "ruins ... stand blackened and
fire-scarred, not pristine" -- the player reads junk as ruins.

NEXT step is a diagnosis, not a fix: on a fresh site, list which genstep placed each sampled thing (order vs 760) and whether
its cell is inside any UsedRect; the 2026-10-12 harness now notes `(def, x, z)` per sample. Then FOUNDRY decides: scorch by
a post-pass over unowned artificial buildings (after all scatter steps), or narrow the bar to ScatterRuinsSimple ruins.

Triage: `Transient/pyre_site_2026-10-12.md`.

## criteria

- A1 L0: offline fuzz (`selftest_pyrelands_fuzz.py`, eco) — `IsScorchableRuin` table and `RuinScorchRung` never-lighten rule (0b14ffc5fa).
- A2 L2: Pyrelands northstar `pyre_ruins_scorched` PASS on a FRESHLY generated site — 3x3 footprints at sampled unowned artificial buildings >= 50% ash.

Diagnosis (RimSage, offline): AncientJunkClusters, ScatterRoadDebris, ScatterCaveDebris, MechanoidRemains and the other Ideology
scatters run at order 960, after RM_FE_ScorchRuins (760), and `GenStep_ScatterGroup` never adds a UsedRect;
`GenStep_ScatterAncientUtilityBuilding` (750) never adds its own rect (its AncientConcrete/tile floors stayed pristine). MOD.
Fix (0b14ffc5fa): `RM_FE_ScorchRuinsLate` (order 965) sweeps every unowned, destroyable, non-rock artificial building. Report:
`Transient/pyre_mod_fixes_2026-10-12.md`.
