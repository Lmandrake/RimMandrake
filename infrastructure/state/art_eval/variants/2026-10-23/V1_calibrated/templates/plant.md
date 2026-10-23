# Template: plant (ground cover, bush, tree, special growth)

Everything above the JSON block is sent to the reviewer as the class module; the JSON block is read by code.

## Panels you are given

- **single.png** — the candidate picture on a checkerboard at full resolution. Plants have no facings; the game
  draws one of a random pool of pictures, each at a random size within the plant's range, standing on the bottom
  edge of its cell (trees overhang their neighbours).
- **scale.png** — the plant beside a vanilla human at true size (mature visual size, mesh count as the engine
  scatters it): max zoom, normal play (32 px per cell), zoomed out.
- **variants.png** (when given) — the other members of its random pool.
- **siblings.png** (when given) — owner-kept pictures of the same plant: the style target.

## How to look (owner's past notes)

1. **The defining feature** the description names is visible: the fruit it yields, the quills, the glow, the
   frond shape. A plant harvested for an item shows that item on the mature plant (a fruiting plant drawn
   without its fruit is `DESC_MISS`).
2. **Reads as its kind**, not a lump — owner 2026-10-18 (Mourvel): *"Reads like a green lump or hill. It was
   supposed to be a willow-like dome the player could step beneath."* Ground cover sits low and reads as a
   texture of the land; a tree shows trunk and canopy.
3. **Natural, not constructed** — owner 2026-10-18 (Tumbel): *"Do not make it look constructed by people."*
4. **Stands on its base**: stem or trunk meets the ground at the bottom of the picture, nothing cut off, not
   floating. A lean, sweep or lopsided crown that the description itself asks for is correct, not an `ANCHOR`
   failure.
5. **No baked scenery**: no soil mound, rock, cliff, water or ground disc unless the description makes it part
   of the plant.
6. **Alien where invented** (not a plain Earth plant), **realistic** over illustration — owner 2026-10-18
   (Vurmeloth): *"Much more realistic please."*
7. **Fills its canvas**: a tiny subject floating in a big canvas is drawn tiny in game.
8. **Scale** beside the human against the description's words ("knee-high" is about a third of the human); a
   full-grown tree is several times human height — owner 2026-10-15: *"That's a beautiful tree but it's tiny!"*
   Scale and legibility are polish (a size is usually a def fix).
9. **Variants**: a ground cover or bush with ONE own picture wants a random pool — note `WANTS_VARIANTS`
   (polish). His most repeated note on kept flora: *"two more improved variants that are more realistic."*

```json template
{
  "template": "plant",
  "version": "plant@v2-V1cal",
  "modules": ["ground_cover", "bush", "tree", "special"],
  "required_panels": {"*": ["single", "scale"]},
  "checklist": [
    {"id": "SIGNATURE",   "q": "Is the description's defining feature (fruit, quills, glow, frond shape) visible?", "code": "DESC_MISS"},
    {"id": "READS_KIND",  "q": "Does it read as its kind (ground cover low, bush, tree with trunk and canopy), not a lump?", "code": "LUMP"},
    {"id": "NATURAL",     "q": "Natural growth, not man-made looking?", "code": "CONSTRUCTED"},
    {"id": "ANCHOR",      "q": "Standing on its base at the bottom centre, nothing cut off, not floating?", "code": "ANCHOR"},
    {"id": "NO_SCENERY",  "q": "No soil, rock, water or ground baked in (unless the description makes it part of the plant)?", "code": "ALPHA_HALO"},
    {"id": "ALIEN",       "q": "Reads as an invented plant, not a plain Earth species?", "code": "STYLE_EARTHLY", "when": "invented"},
    {"id": "STYLE",       "q": "Realistic and painterly, not cartoon or flat?", "code": "STYLE_CARTOON"},
    {"id": "OURS",        "q": "Our own art, not a donor/vanilla stand-in?", "code": "DONOR"},
    {"id": "FILLS",       "q": "Fills its canvas sensibly (not tiny inside a big empty canvas, not overflowing)?", "code": "FOOTPRINT"},
    {"id": "SIBLINGS",    "q": "Matches the owner-kept siblings in style and size class?", "code": "SIBLING_MISMATCH", "when": "siblings"},
    {"id": "OWNER_NOTES", "q": "Is every owner note on the card honoured?", "code": "OWNER_NOTE_IGNORED", "when": "owner_notes"},
    {"id": "SCALE",       "q": "Size beside the human fits the description?", "code": "SCALE_WRONG"},
    {"id": "LEGIBLE",     "q": "Reads at 32 px per cell?", "code": "LEGIB_32"},
    {"id": "VARIANTS",    "q": "Ground cover/bush: is there more than one own picture in its pool?", "code": "WANTS_VARIANTS", "modules": ["ground_cover", "bush"]}
  ]
}
```
