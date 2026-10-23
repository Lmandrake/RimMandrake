# Severity policy — what blocks, decided by policy, never by model mood

The pilot (`Transient/art_eval_pilot_20261023/SCORE.md`, 47 Weeping Stones subjects) showed the failure this file
exists for: **Opus named the owner's defect on 15 of 16 REDO rows but filed 7 of them as minor follow-ups and
kept the picture.** Perception was fine; severity was not. So a reviewer reports *what it saw* as reason codes,
and this table decides whether each code blocks. The model's own severity guess is recorded beside it (so a
disagreement is visible) but never used.

Rules of the table:

- **blocking** = identity and contract: wrong surface on a facing, the subject's defining feature missing, reads
  as a familiar Earth animal when it is invented, donor/placeholder art, baked backdrop, a catch that is not a dead
  specimen of its living animal, a pipe bore in the wrong plane. Any blocking finding stops an auto-accept.
- **polish** = improvements the owner has kept pictures with: scale tweaks (often a `drawSize` def fix, not new
  art), legibility at 32 px (advisory, brief B2), a stray harness on one facing (Tirbak), raised grounded wings
  (Dactillion), an overhead view on a wall-clinger (Sillik), "wants more variants". Recorded, never a regen on
  its own.
- `polish_when` lists card facts that demote a blocking code for that subject only. Each demotion is the
  owner's observed tolerance from the pilot, cited.
- **gross** codes (`X_*`) are blocking and also make the Opus band `really_bad` at any confidence.
- `X_INPUT` is not a severity: an incomplete card never reaches a model (decision `HOLD_INPUT`).

A new code, or a code moved between columns, is a **criteria change**: add a row to the criteria ledger
(`criteria_ledger.md`), bump `version`, and re-run the regression set before the new version decides anything.

```json policy
{
  "version": "severity@v2",
  "high_confidence": 0.8,
  "codes": {
    "F_NORTH_FACE":        {"brief": "C1", "default": "blocking", "means": "north shows a face or eyes; north is the rear"},
    "F_SOUTH_NOT_FRONT":   {"brief": "C1", "default": "blocking", "means": "south is not a front view (profile, rear, overhead)"},
    "F_TOPDOWN":           {"brief": "C1", "default": "blocking", "means": "a facing is an overhead view, not the game camera",
                            "polish_when": ["body_plan:wall_clinger", "body_plan:serpentine"],
                            "why_polish": "owner kept Sillik (overhead wall-clinger), Weeping Stones 2026-10-10"},
    "F_SIZE_JUMP":         {"brief": "C2", "default": "blocking", "means": "one facing markedly bigger or smaller"},
    "F_INCONSISTENT":      {"brief": "C2", "default": "blocking", "means": "facings disagree on anatomy/palette, or a structure does not turn with the body"},
    "F_MISSING":           {"brief": "C2", "default": "blocking", "means": "a facing the template needs is absent"},
    "SCALE_WRONG":         {"brief": "D1", "default": "polish",   "means": "size beside the human contradicts the description",
                            "why_polish": "owner kept Rockfinger with 'make it 50% larger'; size is usually a drawSize fix"},
    "RES_LOW":             {"brief": "D2", "default": "polish",   "means": "soft or upscaled at max zoom"},
    "LEGIB_32":            {"brief": "B2", "default": "polish",   "means": "does not read at 32 px/cell (advisory by the brief)"},
    "STYLE_CARTOON":       {"brief": "B1", "default": "blocking", "means": "cute, toy-like, flat cel, sticker"},
    "STYLE_OFF":           {"brief": "B1", "default": "blocking", "means": "not painterly vanilla: photo, 3D render, pixel art, heavy keyline"},
    "STYLE_EARTHLY":       {"brief": "B1", "default": "blocking", "means": "an invented creature/plant reads as a familiar Earth species",
                            "polish_when": ["earth_body_named", "not_invented"],
                            "why_polish": "owner kept Burrak/Vobbal whose def text names the Earth body; canon and vanilla subjects are not invented"},
    "DEPARTURE_MISSING":   {"brief": "E4", "default": "blocking", "means": "a required departure from the nearest Earth animal (card `departures`) is absent"},
    "DESC_MISS":           {"brief": "A2", "default": "blocking", "means": "the description's defining feature is missing or wrong (a fruiting plant without its fruit)"},
    "CANON_MISS":          {"brief": "A2", "default": "blocking", "means": "a canon Must show line fails (never for an Engine limit, A4)"},
    "SIBLING_MISMATCH":    {"brief": "B3", "default": "blocking", "means": "reads as a different artist or size class than the owner-kept siblings"},
    "OWNER_NOTE_IGNORED":  {"brief": "E4", "default": "blocking", "means": "an owner note on the subject is not honoured"},
    "DONOR":               {"brief": "E1", "default": "blocking", "means": "borrowed art from another mod or vanilla"},
    "PLACEHOLDER":         {"brief": "E2", "default": "blocking", "means": "a stand-in: wrong species, retint, script-drawn shape"},
    "ALPHA_HALO":          {"brief": "D4", "default": "blocking", "means": "backdrop, halo, ground patch, painted shadow or scenery baked in"},
    "FOOTPRINT":           {"brief": "D3", "default": "blocking", "means": "overflows its cells badly or floats tiny inside the canvas"},
    "ANCHOR":              {"brief": "D3", "default": "blocking", "means": "a plant not standing on its base (floating, cut off, trunk off-centre)"},
    "LUMP":                {"brief": "A2", "default": "blocking", "means": "reads as a blob or hill rather than the thing"},
    "CONSTRUCTED":         {"brief": "A2", "default": "blocking", "means": "a natural thing that looks man-made"},
    "FLYER_BODY_MOVES":    {"brief": "C4", "default": "blocking", "means": "flight frames: body bobs or changes; only wings may move"},
    "FLYER_WINGS_GROUNDED":{"brief": "C5", "default": "polish",   "means": "grounded sprite shows raised/spread wings",
                            "why_polish": "owner kept Dactillion with raised grounded wings, 2026-10-10"},
    "SWIM_WATERLINE":      {"brief": "C2", "default": "polish",   "means": "swimming lane does not read as the body at the surface"},
    "GEAR_EAST_ONLY":      {"brief": "C2", "default": "polish",   "means": "gear or harness on one facing only",
                            "why_polish": "owner kept Tirbak's east-only harness, 2026-10-10"},
    "CATCH_WRONG":         {"brief": "A2", "default": "blocking", "means": "the catch is not the caught species (differs from the living art)"},
    "CATCH_POSE":          {"brief": "A2", "default": "blocking", "means": "the catch is posed alive (mid-swim, mid-leap, propped up) instead of a dead specimen lying on the ground"},
    "DUPLICATE":           {"brief": "C2", "default": "blocking", "means": "two facings or variants are the same picture"},
    "WANTS_VARIANTS":      {"brief": "B3", "default": "polish",   "means": "a single own-art picture where a random pool is wanted (ground cover, bush)"},
    "CAM_WRONG":           {"brief": "C3", "default": "blocking", "means": "not the building camera (35 degrees; round top an ellipse ~0.56): a side elevation or a circle facing the camera"},
    "BORE_PLANE":          {"brief": "C6", "default": "blocking", "means": "a pipe/hose shows its open bore where it does not turn toward the camera"},
    "PORT_MISFIT":         {"brief": "C6", "default": "blocking", "means": "a coupler, hose or cord does not meet its port at the same cell, height and plane"},
    "LAYER_ORDER":         {"brief": "C3", "default": "blocking", "means": "what is in front does not draw in front in the assembled view"},
    "MATERIAL_PAINT":      {"brief": "B4", "default": "polish",   "means": "colour reads as a coat of paint, not the material"},
    "X_BLANK":             {"brief": "D4", "default": "gross",    "means": "nothing rendered"},
    "X_WRONG":             {"brief": "A2", "default": "gross",    "means": "not the named subject at all"},
    "X_CROP":              {"brief": "D3", "default": "gross",    "means": "cut off by the canvas"},
    "X_INPUT":             {"brief": "-",  "default": "input",    "means": "the card is incomplete; never judged"}
  }
}
```
