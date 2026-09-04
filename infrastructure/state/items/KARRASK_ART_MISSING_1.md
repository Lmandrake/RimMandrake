# KARRASK_ART_MISSING_1 — RSW_Karrask has no sprite anywhere in the repo

Found running `validate_patch.py` against the live def dump (`XML_PATCH_VALIDATION_SWEEP_1`).

## spec

Three `texPath`s on our own original creature resolve to no file anywhere under any
`Textures/` root:
- `src/RimStarWars/Livestock/Defs/PawnKindDefs/PawnKindDefs_Karrask.xml` —
  PawnKindDef `RSW_Karrask`: `Things/Pawn/Animal/Karrask/Karrask`
- `src/RimStarWars/Livestock/Defs/ThingDefs_Animals/ThingDefs_Karrask.xml` — ThingDef
  `RSW_Karrask` (same path), `RSW_KarraskShedRaw`/`RSW_KarraskPlate`:
  `Things/Item/Resource/Leather`-style paths

Confirmed: `find . -iname "*Karrask*.png"` finds only unrelated mockup concept art
(`src/RimStarWars/Livestock/art/mockups/karrask_opt2.png`, `karrask_opt3.png`), not
under any Textures tree. Every one of these things currently renders as a pink
placeholder in game.

## verify

`skills/generating-rimworld-sprites/scripts/validate_sprite.py` passes clean for the
generated sprite(s), and the `find` above turns up a real file under
`src/RimStarWars/Livestock/Textures/...` matching each texPath.

## criteria

Generate via the `generating-rimworld-sprites` skill (wraps `generating-images` /
`editing-images` with RimWorld's hard constraints). Not attempted in this item — art
generation is iterative and out of scope for a code-review pass.

## done (2026-09-04)

Wrote `src/RimStarWars/Livestock/Textures/Things/Pawn/Animal/Karrask/Karrask.png`
(256x256, matches the Skarnix convention for this mod's similar-drawSize animals —
1.5 max drawSize -> 128px/cell target 192, rounded to the next power of two, same
band as Skarnix's 1.6 drawSize -> 256). Source: the owner's already-picked mockup
(`art/mockups/karrask_opt2.png`, PICKS.md) — it was already rendered on a clean
chroma-key green with no fringe, so it was chroma-keyed directly
(`chroma_key.py`, 27.1% coverage, 0% fringe/mid-alpha, all 4 corners clean) rather
than re-generated, then tight-cropped to its subject bbox and conformed onto a
transparent 256x256 canvas at ~88% width / low vertical placement, matching this
mod's other Graphic_Single quadrupeds (Cindermare, Skarnix).

`RSW_KarraskShedRaw`/`RSW_KarraskPlate`'s `Things/Item/Resource/Leather` texPaths
were the vanilla-packed-asset false positive named in `VALIDATE_PATCH_BLIND_SPOTS_1`
finding #2 — real, already-loaded vanilla art, not missing; only the one creature
texPath needed generating.

Also fixed the two now-stale "PLACEHOLDER / no file exists yet" header comments in
`ThingDefs_Karrask.xml` and `PawnKindDefs_Karrask.xml`.

```
PROVE    python3 skills/generating-rimworld-sprites/scripts/validate_sprite.py \
           --reference .../Karrask/Karrask.png --describe
EXPECT   canvas 256x256, alpha yes, corners [0,0,0,0], coverage ~15%, no
         "touches canvas edge" line
LIES     the describe-only check can't catch bare-path fallback (a mis-deployed
         file at the base path without a game load) or key spill invisible at
         thumbnail size - not exercised: def is not yet deployed/load-tested
```

Not done: deploy to the live Mods folder or a game-load check — out of this
item's scope (offline art generation only); a future load round should confirm
it in-game per `rimworld-load-round`.
