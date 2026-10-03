# STILLSAND_SUN_GOGGLES_ART_1 — wire the sun goggles' own art

`RM_SunGoggles` (`src/RimMandrake/Stillsand/Defs/ThingDefs_Apparel/RM_SunGoggles.xml`, built by `STILLSAND_GLARE_BLIND_GOGGLES_1`) ships with the biosilica texture as its icon and no `wornGraphicPath`, because its art is still queued: `infrastructure/artpipe/pending/RM_SunGoggles.json` and `RM_SunGogglesWorn_{south,east,north}.json` (smoked honey and leather).

## spec

When the art lands, copy it into `src/RimMandrake/Stillsand/Textures/` (icon at a `Things/Item/Apparel/...` path; the worn set as `<path>_south/_east/_north`), point `graphicData/texPath` at the icon and add `apparel/wornGraphicPath` for the worn set (EyeCover layer, head-aligned). Check the art is not already sitting in `infrastructure/artpipe/done/` or `_artsrc/` before re-queuing anything.

## criteria

- The goggles show their own icon on the ground and are drawn on a wearer's face in all facings.
