# SHADECRAFT_LESSONS_DESIGN_1 — shade gear learned by study: the mapping and the cross-biome conflict

Split from `LONGSHADE_GPT_ENRICHMENT_1` §5 (owner-picked by card 2026-09-30). The picked spec:
*"Parasol, shade tent and standing shield unlock by studying a dewfringe rim, a herd crossing and a
mirrak hide (hidden research or a knowledge GameComponent), instead of being known from the start.
Coordinate with `SHADE_GEAR_FAMILY_1`."* Nothing was built, because three questions decide the
design and none of them is answered.

Built and shipping today: all three pieces are craftable from the start
(`EnvironmentalHazards/Defs/ThingDefs_Buildings/RM_ShadeGear.xml`, `SHADE_GEAR_FAMILY_1`, closed).
The Long Carry GenStep hands a dead traveller a parasol (`RM_GenStep_SunGraves`, `gearDef
RM_Parasol`). Mirrak hide exists (`RM_LongShade_Mirrak.xml`) and is the deepest shade cloth.

## open questions (the owner's)

1. **Which lesson unlocks which piece.** The spec lists the gear and the lessons in two parallel
   lists (parasol / tent / shield against dewfringe rim / herd crossing / mirrak hide). The consult
   instead ties the lessons to *ideas* (condensation geometry, portable shade, deeper shade cloth),
   not to pieces. Is it read in order, or some other way?
2. **Cross-biome availability. This is a conflict with a ruling.** `SHADE_GEAR_FAMILY_1` was ruled
   with *"this MUST be applied on other biomes where heat is extreme too"*, and the sun shield is
   the one piece that works under a low sun (the Stillsand). Every lesson named is Long Shade-only:
   the dewfringe and the mirrak live nowhere else. So a colony that never visits the Long Shade could
   never learn the gear its own biome needs. Options: the lock applies only to colonies that start
   there; each hot biome teaches its own lesson; or the lessons speed research up rather than gate it.
3. **What "studying a herd crossing" is mechanically.** It might be a colonist watching a shade
   dash happen nearby, a job at a patch rim, or something that counts crossings seen.
4. **Hidden research or a knowledge GameComponent.** A vanilla research project gives the familiar
   UI. A GameComponent gives letters and progress of its own.

## criteria

- The owner answers 1–3. Then a build item is filed with the answers as its spec.
