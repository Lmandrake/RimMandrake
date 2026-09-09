# DESERT_WRAPS_ART_COMMISSION_1

## Spec
Owner (2026-09-09, verbatim on the event): commission art INSPIRED BY the
Sand People mod's two genuinely-new asset families, then he unsubscribes:
1. Desert wrap apparel with FULL body-type coverage (Fat/Female/Hulk/
   Male/Thin × 3 directions) — the production value our absorbed Tusken
   set lacks.
2. A "devolved" head shape (custom HeadTypeDef geometry).

🔴 LEGAL LINE: original art only. Written design-capture (already taken
while subscribed) + OUR OWN absorbed Sovereign-Tusken art as style
anchor. Never their PNGs as image inputs — no derivatives.

Process (owner-design-loop): CANDIDATES first — 3-4 wrap style options +
2 head-shape options, south-facing, contact sheet to the owner; his pick
then fans out to the full body-type × direction matrix via
generating-rimworld-sprites.

## Placement plan (the "where in our races" the owner asked for)
- Wrap apparel ThingDef + textures → src/RimStarWars/Armoury (the
  weapons/apparel cell; sits beside the absorbed GS_SandP_Hood set,
  RSW_ prefix, own defNames — not tied to the donor-gated KotOR hold).
- Devolved HeadTypeDef (+ gene if gated) → src/RimStarWars/StarWarsRaces
  (headtypes live with races — the SovSith precedent), offered to the
  RSW_RimMandrakeTusken xenotype.
- Campaign wiring (RUT_Jawa_DeepDesert_* pawnkinds wear the wraps; head
  frequency on the tribe) → src/RimUtinni/UtinniPatches, per the
  engine/content doctrine.

## Verify
Candidates sheet reviewed by owner; picked styles produce the full
matrix passing validate_sprite; defs load on minimal list; DeepDesert
pawnkinds spawn wearing wraps in a quicktest.

## Criteria
Owner-picked art shipped at the three placements above; no asset
traceable to the unsubscribed mod's files.
