# The Rot naming sheet - enacted 2026-10-10

Labels are lowercase by RimWorld convention; only the proper-noun possessive keeps its capital ("Tumrata's shelf" - the owner wrote "Tumrata's Shelf"). Names are label-only; defNames/texPaths untouched. Not deployed (game running).

Files: TM = `src/RimMandrake/TheRot/Patches/RotSpecies_NamesAndSizes.xml`, HF = `.../TheRot/Patches/RotGiants_HugeFootprint.xml` (comments), FL = `.../TheRot/Defs/ThingDefs_Plants/RM_RotSporeKit_Flora.xml`, BI = `.../TheRot/Defs/BiomeDefs/RM_TheRot_Biome.xml` (comment), RUT = `src/RimUtinni/UtinniPatches/Defs/BiomeDefs/RUT_TheRot.xml` (comment), PT = `.../UtinniPatches/Patches/PlantTolerances_Ashkarr.xml` (comments).

| row id | shipping defName(s) | old label | new label | decision | description | files |
|---|---|---|---|---|---|---|
| AB_AgaricusDomeCap | AB_AgaricusDomeCap | skarrow dome | skarrowdome | own | reworded (name woven in, mechanics same) | TM, HF, PT |
| AB_Agarilux | RM_TollukCap, RM_TollukCapHarvest | tolluk cap | aumbri (harvest item: aumbri cap) | a | reworded | FL, BI, RUT, PT |
| AB_ArbuscularMycorrhiza | AB_ArbuscularMycorrhiza | bollusk trunk | madruka | own | reworded | TM, HF, PT |
| AB_DribblingCap | AB_DribblingCap | ruvvak weeper | amber weeper | own | unchanged | TM, HF, PT |
| AB_GiantAgarilux | AB_GiantAgarilux | vokkun pillar | vokkun pillar | own (same as current) | unchanged | none |
| AB_GlowingAgarilux | AB_GlowingAgarilux | ithra glowcap | ithrani glowcap | own | unchanged | TM, PT |
| AB_Glowstool | AB_Glowstool | nubbik stool | nubbik | own | unchanged | TM, PT |
| AB_LilacBeacon | AB_LilacBeacon | quessa spire | quessa spire | own (same as current) | unchanged | none |
| AB_SlimyPholiota | AB_SlimyPholiota | glissik slimecap | sweetsnare | b | unchanged | TM, PT |
| AB_WitchesOyster | AB_WitchesOyster | turrok shelf | Tumrata's shelf | own | unchanged | TM, HF, PT |
| RM_CrimsonCap | RM_CrimsonCap | rhessa cap | redsong | own | unchanged | FL, PT |
| RM_MortalMorelPlant | RM_MortalMorelPlant (+Growable) | vennik salve | yullcomb | own | unchanged (growable text now says yullcomb) | FL, PT |
| RM_Pusmelon | RM_Pusmelon | gubbra gourd | gubbra gourd | keep | unchanged | none |
| AA_AngelMoth | AA_AngelMoth (donor) | angel moth | dustveil | b | reworded; label patch added (none existed) | TM |

Items/eggs of donor defs keep donor labels, as for the other renames in TM. Old-label mentions in comments updated.
