---
name: editing-images
description: Modifies an existing image with a text prompt by attaching it to Codex's built-in $imagegen tool, then verifies what actually changed against the original. Use when asked to edit, alter, restyle, damage, age, repair, recolour, retexture or add detail to an image that already exists, or to derive a variant from a reference image. Covers holding invariants steady across iterations and detecting silhouette drift. For creating an image from nothing, use generating-images instead.
---

# Editing an existing image

Editing is not generation with an extra file attached. The defining problem is
that **everything you did not mention is free to drift** — size, framing,
palette, and the outline of the subject. This skill is mostly about pinning
those down and proving they held.

Requires `generating-images`, whose `scripts/` holds the shared engine. The
verified CLI facts live in
`../generating-images/references/codex-contract.md`; read that before
debugging any failure that looks environmental.

## Edit

```bash
python skills/generating-images/scripts/codex_image.py edit \
  --image src/Jawa/art_bench/machine.png \
  --prompt "make all exposed metal ancient and heavily corroded" \
  --out src/Jawa/art_bench/machine_rusted.png
```

`--image` may repeat for multi-image edits. **Order is meaningful** — refer to
them by index in the prompt ("use image 1 as the subject and image 2 for
style"). Add `--chroma-key '#00ff00'` if the result needs alpha, then cut it
out with `chroma_key.py` exactly as in `generating-images`.

## State invariants, every single time

The model is not holding your earlier instructions. Repeat what must not change
in **every** iteration, phrased as things that stay true:

```text
Change only the surface material. The silhouette, canvas size, camera angle
and the position of the object on the canvas all stay exactly as they are.
```

Two failure modes this prevents, both observed in this project:

- **Silhouette drift.** The subject is redrawn slightly larger, smaller or
  shifted. Anything downstream that registers the result against the original
  then either rescales it or mis-registers it.
- **Style drift across a chain.** When each pass edits the previous output,
  small palette and detail shifts compound. By the third pass the result no
  longer matches the source it is supposed to belong with.

## Verify what changed — do not assume

An edit that returns a plausible image is not evidence the edit was obeyed.
Compare against the original:

```bash
python skills/editing-images/scripts/compare_images.py \
  --before src/Jawa/art_bench/machine.png \
  --after src/Jawa/art_bench/machine_rusted.png
```

It reports canvas change, subject bounding box and coverage change, centroid
shift, and mean colour drift — the four things that silently go wrong. It exits
non-zero when the canvas changed or the subject moved or resized beyond
tolerance, so it can gate a pipeline.

Then look at both images. Numbers catch geometry; only your eyes catch "this is
the wrong kind of rust".

## Chain edits deliberately

When a sequence of states is wanted — intact → damaged → repaired — edit each
from the **previous output**, not from the original. That is what makes damage
persist coherently: a hole torn in step 1 is still there, patched, in step 3.

The cost is compounding drift, so run `compare_images.py` against the
**original** at every step, not just against the immediately previous one.

## Editing is where the negation trap does the most damage

An edit prompt is mostly constraints, and constraints are where prohibitions
creep in. "Don't change the background" invites background changes. Write
"the background stays flat #00ff00" instead. Full guidance:
`../generating-images/references/prompting.md`.

## Reference

- `scripts/compare_images.py` — before/after geometry and colour diff.
- `../generating-images/scripts/codex_image.py` — the shared engine.
- `../generating-images/references/prompting.md` — prompt construction.
- `../generating-images/references/codex-contract.md` — verified CLI facts.

## Dependencies

None beyond the standard library.
