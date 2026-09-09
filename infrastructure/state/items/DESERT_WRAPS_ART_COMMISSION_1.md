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

## Candidates (2026-09-09, FOUNDRY)
Contact sheet: `Transient/DESERT_WRAPS_ART_COMMISSION_1_candidates_2026-09-09.png`
(4 wrap styles + 2 head shapes, south-facing, labeled). Source PNGs (real
alpha, generated via `codex_image.py generate` per the `generating-rimworld-sprites`
skill — Codex now returns native alpha on this install, no chroma-key needed)
sit beside it at `Transient/desert_wraps_candidates/*.png`.

Style inputs used: this item's own `design/Jawa/desert_wraps_design_capture.md`
(prose-only capture, no donor pixels) plus our own absorbed
`src/RimStarWars/Armoury/Textures/SWApparel/Sovereign_Tuskens/{Wraps,SandHead_south}.png`
as style anchor — described in prompts, never passed as image input to avoid
any derivative-of-our-own-derivative ambiguity, and the donor mod's own PNGs
were never opened. All 6 candidates are original generated art.

- Wrap A "Spiral Wrap" — grayscale/neutral, Stuff-dyeable, thick outline +
  converging spiral seam bands (closest to the Rimwars mod's own grammar per
  the capture doc, redrawn from scratch).
- Wrap B "Banded Wrap" — overlapping horizontal cloth bands, warm tan, uneven
  hem.
- Wrap C "Segmented Raider" — armored/segmented plates over a wrap base, more
  rugged register.
- Wrap D "Draped Shawl" — loose flowing drape, cream, softer trader read.
- Head 1 "Blunt Bucket Head" — flat squared crown, cylindrical taper, heavy
  jaw-shadow mass, blank dot eyes (closest to the capture doc's measured
  geometry delta from vanilla).
- Head 2 "Elongated Ridged Skull" — domed elongated crown with brow ridges;
  a genuinely different "devolved" direction, not a minor tweak of Head 1.

**Awaits the owner's pick.** Do not build the full body-type × direction
matrix or wire any ThingDef/HeadTypeDef until he picks — see CLAUDE.md's
mockups-first doctrine.

## Verify
Candidates sheet reviewed by owner; picked styles produce the full
matrix passing validate_sprite; defs load on minimal list; DeepDesert
pawnkinds spawn wearing wraps in a quicktest.

## Criteria
Owner-picked art shipped at the three placements above; no asset
traceable to the unsubscribed mod's files.
