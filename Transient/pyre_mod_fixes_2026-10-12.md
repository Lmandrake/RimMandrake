# Pyrelands mod fixes — 2026-10-12 (BENCH subagent, offline)

## SCORCH_FRUIT_FIX_ROLLS_BEFORE_THE_ASHES
- cause (MOD, confirmed by reading): `Patch_FireTick_AshAndScorchFruit` spent each Fire's one roll on its FIRST interval;
  the spot must be standable and plant-free, and the grass the fire is burning still stood in its cell and all 8 neighbours,
  so a fully grassed cohort got 0 fruit. Vanilla `Fire.DoComplexCalcs` (RimSage): the plant dies to fire damage in one
  150-tick calc and the fire is destroyed (no fuel) on the next, so a window of intervals exists with the cell bare.
- fix: `RM_FireEcoKernel.TakeFruitRoll` — the roll is taken (and the fire marked) only once a legal spot exists; the fire's
  OWN cell is scanned first (scorch fruit is Flammability 0, the dying fire cannot hurt it). Still one roll per fire, chance
  and map cap unchanged.
- selftest: `selftest_pyrelands_fuzz.py` eco family simulates a grassed cohort ignited at once on vanilla's 150-tick
  burnout/die rhythm: every fire rolls or its cell already bears fruit; the old first-interval order finds 0 spots there
  (regression model); planted defect (mark before scan) caught: 5 failures.
- live proof: `pyre_scorchfruit_fire_born` / `scorch_fruit_seed` (Pyrelands validation.py).

## PYRE_RUINS_DIAGNOSE_JUNKYARD_STAYS_PRISTINE
- diagnosis (RimSage, Defs/Core + Defs/Ideology MapGeneration/CommonMapGenerator.xml): AncientJunkClusters,
  ScatterRoadDebris, ScatterCaveDebris, MechanoidRemains, AncientTurret/Mechs/LandingPad/Fences run at order 960 — after
  RM_FE_ScorchRuins (760) — and `GenStep_ScatterGroup` never adds a UsedRect. `GenStep_ScatterAncientUtilityBuilding`
  (750) checks UsedRects but never adds its own, so its floors (AncientConcrete, tile) stay pristine. MOD defect: the
  760 pass can only see UsedRects.
- fix: second GenStepDef `RM_FE_ScorchRuinsLate` (order 965, after every 960 scatter), same class with
  `sweepUnownedBuildings=true`, wired via RM_Pyrelands extraGenSteps: every unowned, destroyable, non-rock artificial
  building (the bar's own census group, BuildingArtificial) gets heavy ash under its footprint, light ash on a 1-cell rim;
  never lightens a heavier rung, skips water and natural rock.
- selftest: fuzz tables for `IsScorchableRuin` and `RuinScorchRung`.
- live proof: `pyre_ruins_scorched` on a fresh site (needs a newly generated map).

## Build / shas
see the report in the BENCH conversation; DLL md5 recorded in the commit.
