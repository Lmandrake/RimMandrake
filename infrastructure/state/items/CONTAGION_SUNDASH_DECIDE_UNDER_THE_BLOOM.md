# CONTAGION_SUNDASH_DECIDE_UNDER_THE_BLOOM — should natives sun-dash under the standing Bloom?

Found 2026-10-23 (COALESCENCE_STAGE_DIAGNOSE_STUCK_AT_ONE): on an RM_Contagion map with the Burn OFF, wild
Unfinished ran RM_JobGiver_SunEscape (CreatureBehaviors, RM_ShadeHop.cs) and dashed for shade, because the biome
carries RM_SunHeatExtension. The fiction is a standing storm (the Bloom: red fog, endless rain) torn open only by
the Burn, when natives DIVE (RM_GameCondition_ContagionBurn.TryDive). So between Burns two "flee the light"
behaviours overlap, and the sun one fires under a sky the fiction calls covered.

Owner ruling to respect (standing_rulings.md §Direct Sun, 2026-09-29/10-19): one Direct Sun, a pure function of
geometry, no biome-specific sun. Open question for a judge (design, not art): does a weather's cloud cover reduce
Direct Sun everywhere (a geometry-consistent rule that would quiet the dash under the Bloom), or is the overlap
fine as is? If it needs a change to his ruling it goes to him (delegation_policy.md §2); otherwise decide and log.

## criteria
- O1 L0: a written decision (judge agent or owner), with the code change it implies filed as its own item
