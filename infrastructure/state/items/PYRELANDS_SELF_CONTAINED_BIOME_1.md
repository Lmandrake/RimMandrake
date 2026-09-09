# PYRELANDS_SELF_CONTAINED_BIOME_1

## Spec
Owner, verbatim (2026-09-09): "The pyre land has no biome of its own. It
should be self contained as you said. So let's make it self contained.
Scorch fruit. Strange weather the lot. Ash that blows like snow.
Cinderfall storms. Rapidly growing grass." Resolves PYRELANDS_GENERIC_
TEXT_1's R9 fork: OWN the biome, no donor dep.

## verify
No ## verify was written when this was filed; FOUNDRY (2026-09-09, this
close) decided: (1) every new/edited XML under `src/RimMandrake/Pyrelands/`
is well-formed and passes `validate_patch.py` with 0 errors in static mode
(no live game/def dump is available from WSL to check ParentName/Class
resolution or texPath against the real load set — that is exactly the
deploy+quicktest leg below, deliberately deferred); (2) the five named
elements from the owner's ruling are each a real, inspectable def:
ScorchFruit (`RM_FE_Plant_ScorchFruit`/`RM_FE_ScorchFruitYield`), strange
weather (`RM_FE_Weather_AshFall`, `RM_FE_Weather_Cinderfall`,
`RM_FE_BlackRain`), ash-as-snow (AshFall's snow-pace accumulation →
`RM_FE_Filth_LooseAsh`), Cinderfall storms (ember storm + vanilla lightning
ignition), fast grass (`RM_FE_Plant_EmberGrass`, growDays 0.8,
`wildPlantRegrowDays` 9 on the BiomeDef vs. vanilla savanna's 26-27); (3)
the biome is placeable with no donor dependency (own `workerClass` +
`PyrelandsBiomeRanges` modExtension, own terrains/weather table, no patch
onto another mod's BiomeDef). This is a paper/static verify only — no
bridge, no live game, no ConfigError log, per this task's offline scope.

## re-verified 2026-09-09 (FOUNDRY, this close)
Confirmed all of the above still holds: `validate_patch.py` on
`src/RimMandrake/Pyrelands/Defs` → 12 files, 0 errors, 8 advisory warnings
(all vanilla texPath reuse — Things/Plant/Grass, Things/Item/Resource/Jade,
etc. — expected and flagged by the tool itself as indistinguishable from a
typo without a live dump; not a defect). All 12 XML files parse cleanly.
Cross-checked `design/Jawa/worldbuilding/biomes/the_pyrelands.md` (the
ratified biome sheet) — scorch-fruit spoilage, quickgrass/EmberGrass
regrowth, the ash ladder and the flame-harvest loop all match what's
implemented; the doc's `RSW_FE_*` defNames are stale relative to the
implementation's `RM_FE_*` (tier was promoted RSW→RM in commit 485380d4,
"WeatherSuite+Pyrelands promoted to RM whole") — that's a pre-existing doc
drift outside this item's scope, not something this build introduced.
RimSage's static index has no RM_FE_Pyrelands entries because this mod is
authored-only, never deployed to the game's Mods folder — expected, and
exactly what "Owed before close" item 1 below still covers. No code
changes were needed; authoring was already complete and pushed
(2b29b3cb, 339aba05, a3e5ba3d, all on origin/main). Closing on authoring
completion per this item's dispatch instructions — deploy and the 3-part
quicktest belong to PYRELANDS_WORLD_SWITCH_1's own live work, not a
precondition of this item's close.

## State — BUILT 2026-09-09 (BENCH-orchestrated opus agent)
RM_FE_Pyrelands BiomeDef (+XML-tunable placement modExtension +
BiomeWorker), RM_FE_Plant_EmberGrass (growDays 0.8, flammability 1.6),
RM_FE_Weather_AshFall (grey snow-pace ash → RM_FE_Filth_LooseAsh via new
MapComponent), RM_FE_Weather_Cinderfall (ember storm, vanilla lightning
ignition, feeds the fulgurite postfix), 512px world tile, About rewritten
to the now-true self-contained claim. Build 0W/0E; lint adds zero;
deliberately NO vanilla rain (BlackRain 3→45 under the large-fire
multiplier is the biome's fire answer).

## Owed — moved to PYRELANDS_WORLD_SWITCH_1, not this item's close
1. 🔴 DEPLOY XML + DLL TOGETHER in the next shutdown window — never
   apart (NAMESPACE_PAIR_DEPLOY precedent; a missing modExtension type
   eats the whole BiomeDef silently).
2. The 3-part quicktest validation plan (in the build report, PROVE/
   EXPECT/LIES): worldgen tile count, forced AshFall accumulation count,
   forced Cinderfall strikes. Owner look for the aesthetic.
3. PYRELANDS_WORLD_SWITCH_1 (Ashkarr tiles → this def, pre-freeze) is
   gated on this proving out — that item owns the deploy+quicktest work,
   not a reopen of this one.
