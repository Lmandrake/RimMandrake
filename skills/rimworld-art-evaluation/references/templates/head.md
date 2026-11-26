# Template: head (humanlike species heads, and head attachments such as montrals, lekku, horns and crests)

Everything above the JSON block is sent to the reviewer as the class module. The JSON block is read by code: the
panels a card must carry, the checklist every reviewer answers item by item, and the limits of the code gate.

**Two modules.** `head`: a head-type texture (the whole head the game draws on the head mesh). `attachment`: a part
that a gene draws over the head on its own render node (Togruta montrals, a Zabrak horn set, a Chagrian headbone).

## What code measured before you (do not re-estimate these)

Code judged two things on this card before any model was asked (`src/RimMandrake/Utils/art_eval/head_truth.py`).
A card reaches you only when both passed or could not be measured; the card prints the numbers.

- **Envelope** (module `head`): the skull mass is sized and seated to the vanilla head box, and horns, ears and
  lekku stay inside their allowance and the canvas (`src/RimMandrake/Utils/art/head_envelope.json`). The owner's rule
  (`design/RimStarWars/head_envelope_2026-10-20.md`): *"when looking at head art you must center the head regardless
  of additional appendages such as horns, ears, or anything else. The bulk of the head must be searched for detectable
  chins (or bottom of skull mass) vs top of head ignoring these extensions."* Facing-to-facing size is part of it.
- **Greyscale** (when the card says `skin_tint: yes`): the picture carries no hue. The game's skin shader multiplies
  the texture by the pawn's skin colour, so painted colour shifts every skin tone and the head stops matching the body.

## Panels you are given

- **facings.png** — south, east and north side by side on a checkerboard at ONE scale. Each facing is also attached
  alone (`south.png`, `east.png`, `north.png`). The game mirrors east to draw west.
- **scale.png** (module `head`) — the head beside a vanilla human head at the size the engine draws it.
- **head_reference.png** (module `attachment`) — the attachment drawn on the head it belongs to, every facing. The
  head in it is a reference, not a candidate.
- **siblings.png** (when given) — the owner-kept other heads of the species (the other sex, the variants): the style
  and size target.

## How to look

1. **Facings.** South = the face toward the camera. North = the back of the head: **no face, no eyes, no mouth**.
   East = a true side profile looking to the screen's right (the game mirrors it for west); a three-quarter view
   or a profile looking left is `F_EAST_NOT_PROFILE`. None is an overhead view. The owner's rule for every pawn
   picture (creature template, 2026-09-15): *"North facing is 'looking away from the player camera' (their butt).
   South facing is 'looking at the player camera'."*
2. **The same head on every facing.** Every montral, lek, horn, ear and crest is present and turns with the head:
   the count stays the same (a Togruta has two montrals and three lekku), a lek that falls over the chest on south
   falls behind the shoulder line on east, and the back lek shows on north.
3. **A head only.** No human hairstyle, beard, hat, helmet or clothing painted on: the game draws hair and headgear
   on top of the head, so a painted one doubles or shows through. A species' own fur, quills or tendrils are part of
   the head. No body, shoulders or backdrop.
4. **Skin-tinted heads are painted in values, not colours.** Light skin reads as near-white, shading as grey. A
   marking that canon says keeps its own colour (a Togruta's white facial pigments, lekku stripes) cannot keep it
   under the skin tint. If the canon entry lists it under Engine limits, it is not a failure. If it lists it under
   Must show, then check that the marking reads as a lighter or darker value pattern.
5. **Canon.** Answer each Must show line of the card's canon entry (from `design/RimStarWars/canon_references/`).
   An Engine limits line is never a failure.
6. **Attachments meet their head** (module `attachment`). On `head_reference.png`, the part grows from the skull
   where canon puts it (montrals atop the skull, lekku from its base), on every facing: no gap, no float, no part
   cutting through the face, and in front of or behind the head as it would be from that side.
7. **Painterly vanilla style, realistic, not cute.** Soft painted shading and the thin dark outline that vanilla
   heads carry. Glossy round eyes or a cartoon smile is `STYLE_CARTOON`; a photo or 3D render is `STYLE_OFF`.
8. **Provenance.** A head taken from another mod is donor art (`DONOR`), never a final keep.
9. **Scale and legibility** are polish: the head beside the vanilla head against the canon's size words, and the
   species read at 32 px per cell.

```json template
{
  "template": "head",
  "version": "head@v1",
  "modules": ["head", "attachment"],
  "required_panels": {
    "head":       ["south", "east", "north", "facings", "scale"],
    "attachment": ["south", "east", "north", "facings", "head_reference"],
    "*":          ["south", "east", "north", "facings"]
  },
  "gate": {
    "greyscale": {"mean_chroma_max": 0.08, "p95_chroma_max": 0.16,
                  "_danger": "the skin shader multiplies a painted hue into every skin tone, so head and body colours disagree",
                  "_basis": "MEASURED 2026-11-26, chroma = max-min of RGB over opaque pixels: vanilla Core heads 0.004 mean / 0.016 p95; shipped skin-tinted Lasat and Nelvaanian heads at most 0.068 / 0.122; full-colour paintings drawn untinted (Mimbanese, Ortolan) at least 0.253 / 0.333"}
  },
  "checklist": [
    {"id": "SOUTH_FRONT",  "q": "Which surface does south show? It must be the face toward the camera.", "code": "F_SOUTH_NOT_FRONT"},
    {"id": "NORTH_REAR",   "q": "Which surface does north show? It must be the back of the head, with no face, eyes or mouth.", "code": "F_NORTH_FACE"},
    {"id": "EAST_PROFILE", "q": "Is east a true side profile looking to the screen's right (not three-quarter, not looking left)?", "code": "F_EAST_NOT_PROFILE"},
    {"id": "NO_OVERHEAD",  "q": "Is any facing an overhead/top-down view?", "code": "F_TOPDOWN"},
    {"id": "SAME_HEAD",    "q": "Same head on every facing, every montral, lek, horn, ear and crest present in the same count and turned with the head?", "code": "F_INCONSISTENT"},
    {"id": "HEAD_ONLY",    "q": "Is it the head alone: no human hairstyle, beard, hat, helmet, clothing, body or shoulders painted on?", "code": "HEAD_BAKED_EXTRAS", "modules": ["head"]},
    {"id": "ATTACH_FIT",   "q": "On head_reference, does the part grow from the skull where canon puts it on every facing, with no gap, float or cut through the face, and in front of or behind the head as seen from that side?", "code": "ATTACH_MISFIT", "modules": ["attachment"]},
    {"id": "CANON",        "q": "Is every canon Must show line present (Engine limits excluded)?", "code": "CANON_MISS", "when": "canon"},
    {"id": "STYLE",        "q": "Painterly and realistic in the vanilla head style, not cute, cel-shaded, photo or 3D?", "code": "STYLE_CARTOON"},
    {"id": "OURS",         "q": "Is it our own art, not a donor/vanilla stand-in or placeholder?", "code": "DONOR"},
    {"id": "ALPHA",        "q": "Clean cut-out: no backdrop, halo or shadow baked in?", "code": "ALPHA_HALO"},
    {"id": "SIBLINGS",     "q": "Same artist, palette and size class as the owner-kept siblings?", "code": "SIBLING_MISMATCH", "when": "siblings"},
    {"id": "OWNER_NOTES",  "q": "Is every owner note on the card honoured?", "code": "OWNER_NOTE_IGNORED", "when": "owner_notes"},
    {"id": "SCALE",        "q": "Does its size beside the vanilla head fit the canon's size words?", "code": "SCALE_WRONG", "modules": ["head"]},
    {"id": "LEGIBLE",      "q": "At 32 px per cell does the species read (its montrals, lekku, horns or face shape)?", "code": "LEGIB_32"}
  ]
}
```
