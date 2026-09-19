## spec
Two background agents (standing owner instruction, 2026-09-11: "always have
at least one background sub agent working on art regeneration") queued and
the `artpiped.py` daemon finished 11 creatures' worth of art:

- **Proven-missing textures** (from `design/Jawa/worldbuilding/review/
  creature_art_register.decisions.json`, `texture: not_found`): `AA_ShadowCharger`,
  `AA_Thunderox`.
- **Star Wars canon "redo" creatures** (from `design/Jawa/worldbuilding/
  review/round2/decisions_propagated.json`, `art: "redo"`, reference gathered
  online per the redo-semantics ruling): `Kreetle`, `Horax`, `Fambaa`,
  `Dragonsnake`, `Zakkeg`.

Each has 3 facings (south/east/north) done in `infrastructure/artpipe/done/`
(`<id>_v1_<facing>.json` + `.manifest.json`, PNGs in `_artsrc/`). Per
`infrastructure/artpipe/README.md`, wiring a finished, validated file into a
mod's `Textures/` tree is explicitly a SEPARATE step this daemon does not do
— that's this item.

## verify
For each of the 7 creatures: the new art replaces the old (or fills the
missing) texture at the correct `texPath` in its owning mod's `Textures/`
tree, the game's ThingDef/PawnKindDef `texPath` fields still resolve, and
`validate_patch.py` stays clean. Spot-check in a quicktest or via a fresh
def-dump texture read, per `reading-rimworld-graphics`/`generating-
rimworld-sprites` doctrine — do not just trust the manifest's validator
verdict.

## criteria
All 7 creatures render the new art in-game (not a magenta placeholder, not
the old donor-reused texture), confirmed by looking, not inferred from a
clean manifest.

## Watch out
Still deliberately unqueued: ~24 more "redo" rows from the 2026-09-10
fauna/flora sitting (`decisions_propagated.json`) that need a real design
call (biome reassignment, a full rename+redefine) neither art agent would
guess at — AA_ShockGoat, Gundark, Aiwha, several GR_Chicken* rows, and
JRWBeelzebufo (rename+redefine). Route those to BENCH/the owner, not another
art-gen pass.
