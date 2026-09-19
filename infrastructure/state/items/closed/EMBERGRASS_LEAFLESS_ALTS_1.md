# EMBERGRASS_LEAFLESS_ALTS_1 — EmberGrass leafless: additional variant sprites

Owner, 2026-09-16, on the shipped leafless sprite: *"Add more! This is great,
but add more alternates"*.

## what shipped

Three new leafless variants beside the approved anchor, in
`src/RimMandrake/Pyrelands/Textures/Things/Plant/RM_FE_EmberGrass_Leafless/`:

| file | what it is |
|---|---|
| `RM_FE_EmberGrass_LeaflessA.png` | the anchor the owner approved — upright charred clump, three ember tips (unchanged) |
| `RM_FE_EmberGrass_LeaflessB.png` | low and splayed, several stems bent over or lying flat, one ember tip on the left |
| `RM_FE_EmberGrass_LeaflessC.png` | taller remnant, stems standing but snapped off halfway with ragged ends, two ember tips |
| `RM_FE_EmberGrass_LeaflessD.png` | burned nearly away — a wide low fan of short ash-bleached stubs, no embers at all |

All four are 256x256 RGBA with clear corners and four DISTINCT pixel sha256s
(checked explicitly — a copied file masquerading as a fourth variant is the
failure mode this class of work has).

## no def change was needed, and that is a measured fact

`PlantProperties.ResolveReferences` builds the leafless graphic as
`GraphicDatabase.Get(parentDef.graphicData.graphicClass, leaflessGraphicPath,
…)` — RimSage, `RimWorld/PlantProperties.cs:263`. EmberGrass declares
`graphicClass Graphic_Random`, so `leaflessGraphicPath` is a FOLDER and every
PNG under it is already a random variant; the `<color>` ochre tint carries over
the same way. Dropping the PNGs in is the whole wiring. The def edit in this
item is a comment recording that, so the next agent does not go looking for a
list to append to.

## what was assumed (the item carried no criteria)

- **"Alternates" means more random-selection variants of the same leafless
  state**, not new growth stages — Quickgrass owns the stage-art mechanism
  (`PlantGrowthStages` modExtension) and ember grass has no stage art.
- **Three more, not one and not ten.** The living art ships three variants
  (A/B/C); four leafless now exceeds it, and a burned tile is seen less often
  than a living one.
- **Spread, not repetition**: each variant differs in silhouette AND in ember
  count (3 / 1 / 2 / 0), so a burned patch reads as varied at sprite size
  rather than as one sprite rotated.

## validator note — read before "fixing" a REJECT

`validate_sprite.py --reference A --candidate B` REJECTs all three on subject
span, aspect and origin. **That is the instrument being used outside its
scope, not a defect.** Those checks exist to catch a facing or damage variant
of the SAME asset being squashed or misregistered; a Graphic_Random sibling is
*meant* to have a different silhouette. The shipped living set proves the
convention — `RM_FE_EmberGrassA/B/C` span 219x237, 220x200 and 131x199, aspects
0.924 / 1.100 / 0.658, at three different origins.

What was checked and does bind, all passing: 256x256 canvas, real alpha, all
four corners at zero, faint-fringe 0.33–0.55% and mid-alpha 0.77–0.89% (both
*below* the shipped living art's 0.54–0.75% / 1.28–1.53%), no canvas-edge
contact, no detached-fragment blobs, ground line within 9px across all four,
distinct pixel hashes.

## generated on the Gemini channel, not Codex

Codex's `$imagegen` was out of quota for the sitting (`You've hit your usage
limit … try again at 10:52 PM`), so all three were made with
`gemini_image.py generate --ref <anchor> --cutout` and conformed with
`conform_sprite.py`. `--ref` gives the same reference-conditioning the Codex
`edit` path gives, and the style holds against the anchor.

## validation plan

```
PROVE    spawn RM_FE_Plant_EmberGrass on a pyrelands map and drive it leafless
         (burn the tile, or set growth past lifespan), default zoom, several
         plants at once so the random roll is visible
EXPECT   the burned tuft is NOT the same sprite on every plant — across ~9
         leafless plants at least three of the four silhouettes appear, and at
         least one carries no ember tip at all (that is D, and it is the only
         one that does)
LIES     Graphic_Random rolls per plant, so a small sample can legitimately
         land on one variant twice and look broken. Judge on ~9 plants, never
         on one. And a mis-deployed folder falls back to nothing rather than to
         A — an all-magenta tuft is a texPath failure, not a variant failure.
```

Deployed to the Steam Mods folder 2026-09-18 (`deploy_custom_mods.py --mod
Pyrelands --apply`, VERIFIED in sync). Defs parse at startup only, so the live
game needs a restart before the look is worth anything.
