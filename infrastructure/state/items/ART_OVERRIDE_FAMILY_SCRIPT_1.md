# ART_OVERRIDE_FAMILY_SCRIPT_1

Child of NORTHSTAR_EVERYWHERE_PROGRAM_1.

## spec
The `*ArtOverride` mods (59 on 2026-10-09, two of them with no About.xml) (list: `src/*/*ArtOverride`) only retexture a creature. ONE parametrized script covers them: for each, the target def resolves, its texPath resolves to a real texture in all required facings (never judge by `*south*` glob alone; measure `_south.png`), and the creature spawns without a magenta/missing-texture error. Parametrize from each mod's About.xml/Defs, not hand lists. Prove the checks can fail (a deliberately missing texture).

## verify
One live run on a tier carrying all of them (or batched), results JSON in Transient/northstar/.

## criteria
All covered by the family script with per-mod rows; findings classified; committed.
