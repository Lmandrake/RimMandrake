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
