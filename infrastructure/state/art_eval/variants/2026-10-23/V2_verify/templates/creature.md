# Template: creature (walkers, pack animals, swimmers, amphibians, flyers, and their catch items)

Everything above the JSON block is sent to the reviewer as the class module. The JSON block is read by code: the
panels a card must carry, and the checklist every reviewer answers item by item.

## Panels you are given

- **facings.png** — the candidate's south, east, north (and west if it has its own file) side by side on a
  checkerboard, all at ONE scale (a facing that looks bigger IS bigger). Each facing is also attached alone at
  full resolution (`south.png`, `east.png`, `north.png`).
- **scale.png** — the candidate beside a vanilla human and a rat at true in-game size: max zoom, normal play
  (32 px per cell), zoomed out.
- **flight.png** (flyers with a flip-book) — every flight frame per direction.
- **living_reference.png** (catch items) — the LIVING animal's facings. It is a reference, not a candidate.
- **siblings.png** (when given) — the owner-kept other sex, lifestages or variants: the style and size target.

## How to look (owner's past notes, the reason each check exists)

1. **Facings.** South = the face toward the camera. North = the rear: back and tail, **no face, no eyes**.
   East = a true side profile. None of them is an overhead view. — owner 2026-09-15: *"North facing is 'looking
   away from the player camera' (their butt). South facing is 'looking at the player camera'… We should NOT have
   'top down view rotated north or south.'"* Every structure (horns, fans, sails, tails) is present and turns
   with the body in every view — a crest or fan that is a front-facing wheel on south AND north but a lengthwise
   sail on east has not turned with the body: `F_INCONSISTENT`.
2. **Same size on every facing** — owner 2026-10-22: *"it needs the treatment that makes the different facings the
   same size."* The card prints the measured height spread; trust that number for what it measures.
3. **Alien, not a recoloured Earth animal** (invented creatures). First name the Earth animal it most resembles,
   in one word, in `nearest_earth_animal`. Then check each line of the card's `departures` (the per-subject
   features that make it NOT that animal): each one present or absent. — owner 2026-10-11: *"it looks like a
   terran hippo with ash on its back. Much more alien please."* A canon (RSW_) or vanilla subject is not
   invented; a def whose own text names its Earth body (a frog, an octopus) may look like it.
4. **The defining feature** the description names (the fan, the comb, the sail) is visible and legible.
5. **Realistic and painterly, not cute** — he rejected creatures as *"cartoonish"* (2026-09-15) and asked
   *"Make it as realistic as you can"* (2026-10-10). Glossy round eyes and a smiling face are cute.
6. **Provenance**: a vanilla or other-mod animal is donor art, never a final keep.
7. **Real alpha**: no water, rock, grass or shadow baked under the body.
8. **Scale** beside the human against the description's size words; **legibility** at 32 px. Both are polish.

### Module: swimmer / amphibious
Still a body sprite with south/east/north; a fish's south is its face head-on, its north its tail end. A swimming
lane (`swim_*`) reads as the body at the surface. A land reptile standing in for a fish is a placeholder.

### Module: flyer
Grounded: wings folded and symmetric (raised wings are polish — the owner kept one). Flight frames: head, neck and
body hold still across frames; only wings move — owner 2026-10-20: *"Their bodies should be kept static while the
wings flap."* Judge from stills only; never ask for a live capture.

### Module: catch (an item: one picture)
A catch is the caught creature as an **object**: a dead specimen of THE SAME body as `living_reference.png`,
lying on the ground — limp, eyes shut or dull. First name four identity features of the living reference
(colour pattern, head shape, fins or limbs, tail) and check each on the catch in `CATCH_SPECIES`'s `seen`. Mid-swim, mid-leap, propped up or hanging in water is
`CATCH_POSE`. A different animal, or a body that no longer matches the living art, is `CATCH_WRONG`. Facing
checks do not apply. Code makes the catch follow its living animal: if the living animal is being regenerated,
the catch waits for it whatever you say here.

```json template
{
  "template": "creature",
  "version": "creature@v2-V2ver",
  "modules": ["walker", "pack", "swimmer", "amphibious", "flyer", "catch"],
  "required_panels": {
    "*":     ["south", "east", "north", "facings", "scale"],
    "flyer": ["south", "east", "north", "facings", "scale"],
    "catch": ["single", "scale", "living_reference"]
  },
  "checklist": [
    {"id": "SOUTH_FRONT",   "q": "Which surface does south show? It must be the front, face toward camera.", "code": "F_SOUTH_NOT_FRONT", "not_modules": ["catch"]},
    {"id": "NORTH_REAR",    "q": "Which surface does north show? It must be the rear with no face or eyes.", "code": "F_NORTH_FACE", "not_modules": ["catch"]},
    {"id": "NO_OVERHEAD",   "q": "Is any facing an overhead/top-down view?", "code": "F_TOPDOWN", "not_modules": ["catch"]},
    {"id": "SAME_SIZE",     "q": "Do all facings show the animal at the same size?", "code": "F_SIZE_JUMP", "not_modules": ["catch"]},
    {"id": "SAME_ANIMAL",   "q": "Same animal on every facing, every structure present and turned with the body?", "code": "F_INCONSISTENT", "not_modules": ["catch"]},
    {"id": "SIGNATURE",     "q": "Is the description's defining feature visible and legible?", "code": "DESC_MISS"},
    {"id": "ALIEN",         "q": "Does it read as alien rather than the Earth animal you named?", "code": "STYLE_EARTHLY", "when": "invented"},
    {"id": "DEPARTURES",    "q": "Is every line of the card's departures present? Answer per line in seen.", "code": "DEPARTURE_MISSING", "when": "departures"},
    {"id": "CANON",         "q": "Is every canon Must show line present (Engine limits excluded)?", "code": "CANON_MISS", "when": "canon"},
    {"id": "STYLE",         "q": "Painterly and realistic, not cute, cel-shaded, photo or 3D?", "code": "STYLE_CARTOON"},
    {"id": "OURS",          "q": "Is it our own art, not a donor/vanilla stand-in or placeholder?", "code": "DONOR"},
    {"id": "ALPHA",         "q": "Clean cut-out: no backdrop, water, rock, ground or shadow baked in?", "code": "ALPHA_HALO"},
    {"id": "SIBLINGS",      "q": "Same artist, palette and size class as the owner-kept siblings?", "code": "SIBLING_MISMATCH", "when": "siblings"},
    {"id": "OWNER_NOTES",   "q": "Is every owner note on the card honoured?", "code": "OWNER_NOTE_IGNORED", "when": "owner_notes"},
    {"id": "SCALE",         "q": "Does its size beside the human fit the description?", "code": "SCALE_WRONG"},
    {"id": "LEGIBLE",       "q": "At 32 px per cell does it read as a few bold shapes apart from the ground?", "code": "LEGIB_32"},
    {"id": "WINGS_FOLDED",  "q": "Grounded: wings folded and symmetric?", "code": "FLYER_WINGS_GROUNDED", "modules": ["flyer"]},
    {"id": "BODY_STATIC",   "q": "Flight frames: body still, only wings move?", "code": "FLYER_BODY_MOVES", "modules": ["flyer"], "when": "flight"},
    {"id": "WATERLINE",     "q": "Swimming lane reads as the body at the surface?", "code": "SWIM_WATERLINE", "modules": ["swimmer", "amphibious"], "when": "swim_lane"},
    {"id": "CATCH_SPECIES", "q": "Is the catch the same body as the living reference?", "code": "CATCH_WRONG", "modules": ["catch"]},
    {"id": "CATCH_DEAD",    "q": "Is it a dead specimen lying on the ground (limp, eyes shut/dull), not posed alive?", "code": "CATCH_POSE", "modules": ["catch"]}
  ]
}
```
