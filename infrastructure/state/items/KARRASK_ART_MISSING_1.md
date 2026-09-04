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
