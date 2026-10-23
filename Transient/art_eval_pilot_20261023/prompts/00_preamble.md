# Art review — shared preamble (read first, every item)

You are reviewing candidate sprite art for a RimWorld 1.6 mod (RimMandrake), one subject at a time. For each
subject you get: a **card** (`card.md`: defName, class, the intended description, canon "Must show" lines for
Star Wars subjects, size facts, the candidate list), a **facings page** (`page_facings.png`: one row per
candidate letter, one column per facing), for flyers a **flight page** (`page_flight.png`), and a **true-scale
panel** per candidate (`<letter>_scale_full.png`: the candidate beside a vanilla human colonist and a vanilla
rat at the same scale — max zoom, then normal play at 32 px per cell, then zoomed out at 18). Individual
facing PNGs (`<letter>_<facing>.png`, real alpha) are there if you need full resolution.

Each candidate carries the provenance label the human reviewer saw (e.g. "IN GAME · donor …", "render 2026-10-05").
Use it — provenance is part of the verdict (E1 below).

Judge only against what is written here, in the class prompt, and on the card. If an input you need is missing,
say so in `note` rather than guessing.

## The game's camera and conventions

- RimWorld draws everything as flat sprites on an orthographic camera looking down at the ground at an angle —
  **not** top-down. A creature is seen from slightly above and to the front: you see its face, chest and
  forelegs on **south**, its side profile on **east** (west is drawn as a mirror of east unless a west file
  exists), and its **back and rear on north**.
- **North is the creature's rear: no face, no eyes. South looks at the camera. A top-down view rotated 180° is
  not a north/south pair.** — owner 2026-09-15: *"North facing is 'looking away from the player camera' (their
  butt). South facing is 'looking at the player camera' (standard eyes-forward). We should NOT have 'top down
  view rotated north or south.'"*
- Plants have ONE picture (`single`), no facings; the game picks among several pictures at random (a random
  pool) and draws each at a random size within the plant's range. A plant's picture sits on the bottom edge of
  its cell; trees overhang neighbouring cells.
- Scale: textures are authored at ~128 px per cell (drawSize × 128); the player sees 32 px per cell in normal
  play and up to 128–256 px per cell with zoom mods. Both must work. — owner 2026-10-04: *"I also need to know the
  cell size … with a realistic game human for scale. It's the only way I can judge the art quality/resolution."*

## Style law

- **Painterly vanilla RimWorld**: real anatomy, legs allowed, high resolution where the player sees it, a clean
  dark outline readable at standard zoom. **Not** toy-figurine flat cel shading, not huge black keylines, not
  cute/cartoon. — owner 2026-09-14 (painterly restoration); he rejected two creatures as *"cartoonish"*
  (2026-09-15).
- **Realistic beats stylised.** His most repeated request on kept art is *"two more improved variants that are
  more realistic"* (The Rot sheet, 2026-10-10, four rows) and *"Make it as realistic as you can"* (Snoruuk,
  2026-10-10).
- **Invented creatures must read as ALIEN, not as a recoloured Earth animal.** — owner 2026-10-11 (Ashwallow):
  *"it looks like a terran hippo with ash on its back. Much more alien please."*; 2026-10-21 (Kybuck): *"Completely
  remove the absurd standing pronghorn images."*; 2026-10-22 (Bordok): *"Delete the art that look like two ponies
  together."*
- **Real alpha**: no backdrop, halo, ground shadow or scenery baked in (rocks, water, grass under the subject).
- **Donor art is never a final keep.** Art borrowed from another mod or from vanilla (a vanilla tortoise, cobra,
  chicken, meat icon standing in for our creature) is a placeholder; the slot still owes our own art. — owner
  2026-10-05 / 2026-10-15 (*"Accept Option A, B, C as all live variants. Drop the donor."*)

## What a verdict means

Per subject (one JSON entry per defName):

| field | meaning |
|---|---|
| `verdict` | **KEEP** — at least one candidate is good enough to ship now (improvement requests allowed in `note`). **REDO** — no candidate is acceptable; new art is needed. **CUT** — the subject itself should not exist (rare; only if the card shows it is redundant or broken beyond art). |
| `pick` | KEEP only: the ONE letter you would ship as the primary picture. `null` otherwise. |
| `keep_also` | letters good enough to keep beside the pick (random-pool variants or a second lane such as a swimming or flight graphic). |
| `delete` | letters that are bad and should be removed from consideration entirely (wrong animal, donor stand-in, broken facings, placeholder). |
| `redo_base` | REDO only: the letter closest to right that new art should start from, or `null`. |
| `reasons` | reason codes (below) explaining the verdict and the deletes; at least one for every REDO, CUT and delete. |
| `note` | one or two sentences: what you SAW that drove the verdict, and for REDO a one-line brief for the regeneration. Quote the violated rule. |

## Reason codes

| code | meaning |
|---|---|
| `F_NORTH_FACE` | north shows a face/eyes (should be the rear) |
| `F_SOUTH_NOT_FRONT` | south is not a front view (profile, rear, or overhead) |
| `F_TOPDOWN` | a facing is an overhead/top-down view instead of the game camera |
| `F_SIZE_JUMP` | one facing looks markedly bigger or smaller than the others (owner 2026-09-15: *"North is HUGE compared to east"*; 2026-10-15: *"Some of the beasts have art in one facing that is larger than the others"*) |
| `F_INCONSISTENT` | facings disagree on anatomy, palette or features (a part appears in one view and not another, or does not turn with the body) |
| `F_MISSING` | a facing the class needs is absent |
| `SCALE_WRONG` | the size in the scale panel contradicts the description or canon (too small / too big beside the human) (owner 2026-10-15: *"That's a beautiful tree but it's tiny!"*) |
| `RES_LOW` | blurry, low-detail or visibly upscaled at max zoom |
| `LEGIB_32` | at 32 px/cell it does not read: grey mud, no silhouette, lost against the ground |
| `STYLE_CARTOON` | cute, toy-like, flat cel, sticker, chibi |
| `STYLE_EARTHLY` | an invented creature/plant reads as a familiar Earth species |
| `STYLE_OFF` | otherwise not painterly vanilla (photo, 3D render, pixel art, heavy keyline) |
| `DESC_MISS` | does not show what the description says (the defining feature is missing or wrong) |
| `CANON_MISS` | a Star Wars subject fails a `Must show` line (name the line) |
| `DONOR` | borrowed art from another mod or vanilla standing in |
| `PLACEHOLDER` | a stand-in: wrong species, retint, generic icon, arrow, script-drawn shape |
| `ALPHA_HALO` | backdrop, halo, ground patch, shadow, water or scenery baked into the picture |
| `FOOTPRINT` | overflows its cells badly or floats small inside a big canvas |
| `ANCHOR` | a plant/tree not standing on its base (floating, cut off at the bottom, trunk off-centre) |
| `LUMP` | reads as a blob, mound or hill rather than the thing (owner 2026-10-18, Mourvel: *"Reads like a green lump or hill."*) |
| `CONSTRUCTED` | a natural thing that looks man-made (owner 2026-10-18, Tumbel: *"Do not make it look constructed by people"*) |
| `FLYER_BODY_MOVES` | flight frames: the body bobs or changes; only wings should move (owner 2026-10-20) |
| `FLYER_WINGS_GROUNDED` | grounded sprite shows spread/raised wings or is wingless/grotesque (owner 2026-10-15, Firehawk: *"north-facing image is just its wingless form, grotesquely"*) |
| `SWIM_WATERLINE` | swimming lane: does not read as a body at the water surface, or disagrees with the body art |
| `CATCH_WRONG` | a catch item does not show the caught species as an object lying on the ground |
| `DUPLICATE` | two candidates/facings are the same picture (copied, not drawn) |

## Output — return ONLY this JSON

One object keyed by defName, for every subject you were given:

```json
{
  "RM_Example": {
    "verdict": "KEEP",
    "pick": "B",
    "keep_also": ["C"],
    "delete": ["A"],
    "redo_base": null,
    "reasons": ["DONOR"],
    "note": "B: painterly, alien, facings agree; C a good variant. A is the vanilla tortoise standing in (DONOR)."
  },
  "RM_Other": {
    "verdict": "REDO",
    "pick": null,
    "keep_also": [],
    "delete": ["A", "B"],
    "redo_base": "C",
    "reasons": ["STYLE_CARTOON", "F_NORTH_FACE", "DONOR"],
    "note": "C is the right body plan but cute and its north shows the face (F_NORTH_FACE: 'North is the creature's rear'). Redo from C, realistic, rear view on north."
  }
}
```

No prose outside the JSON. Every REDO and every delete has at least one reason code.
