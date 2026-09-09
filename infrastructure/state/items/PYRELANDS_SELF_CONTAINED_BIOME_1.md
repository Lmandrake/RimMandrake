# PYRELANDS_SELF_CONTAINED_BIOME_1

## Spec
Owner, verbatim (2026-09-09): "The pyre land has no biome of its own. It
should be self contained as you said. So let's make it self contained.
Scorch fruit. Strange weather the lot. Ash that blows like snow.
Cinderfall storms. Rapidly growing grass." Resolves PYRELANDS_GENERIC_
TEXT_1's R9 fork: OWN the biome, no donor dep.

## State — BUILT 2026-09-09 (BENCH-orchestrated opus agent)
RM_FE_Pyrelands BiomeDef (+XML-tunable placement modExtension +
BiomeWorker), RM_FE_Plant_EmberGrass (growDays 0.8, flammability 1.6),
RM_FE_Weather_AshFall (grey snow-pace ash → RM_FE_Filth_LooseAsh via new
MapComponent), RM_FE_Weather_Cinderfall (ember storm, vanilla lightning
ignition, feeds the fulgurite postfix), 512px world tile, About rewritten
to the now-true self-contained claim. Build 0W/0E; lint adds zero;
deliberately NO vanilla rain (BlackRain 3→45 under the large-fire
multiplier is the biome's fire answer).

## Owed before close
1. 🔴 DEPLOY XML + DLL TOGETHER in the next shutdown window — never
   apart (NAMESPACE_PAIR_DEPLOY precedent; a missing modExtension type
   eats the whole BiomeDef silently).
2. The 3-part quicktest validation plan (in the build report, PROVE/
   EXPECT/LIES): worldgen tile count, forced AshFall accumulation count,
   forced Cinderfall strikes. Owner look for the aesthetic.
3. PYRELANDS_WORLD_SWITCH_1 (Ashkarr tiles → this def, pre-freeze) is
   gated on this proving out.
