# Standard black-background creature-art template

`ART_BACKGROUND_TEMPLATE_1`. For a NEW-creature generation job (no `reference`,
so `artpiped.py`'s validator is skipped entirely — see
`src/RimMandrake/Utils/artpipe/artpiped.py` around the `"no reference on this
job"` note) that needs a solid, non-transparent black backdrop instead of the
usual `background: "transparent"` sprite pipeline. Proven out empirically
against the live daemon; see `BACKGROUND_TEMPLATE_LOG.md` for the raw results.

## The template

Job row fields (per `fill_queue.py`'s `REQUIRED_ROW_FIELDS` + optional columns):

```
background:   "#000000"
```

Append this sentence verbatim to the job's `prompt` (or put it in
`style_notes` — both tested clean; either works):

```
Backdrop: studio photograph on solid black seamless paper, evenly lit from
the front so the black stays pure black to every edge of the frame.
```

Keep the rest of the prompt's own subject description phrased as a positive
state, not a prohibition (`AGENTS.md` rule 2): say what the frame IS, not
what it lacks.

## Why this wording and not another

The obvious instinct — spell out what to avoid ("no gradient, no vignette,
no floor, no shadow") — was NOT what was tested here, on purpose: image
models condition on the tokens present, and negated tokens still describe
the picture. The winning wording never says "no" at all; it gives the model
a concrete real-world referent (photographing a subject against seamless
black paper, evenly lit) that has pure black to the edges as a natural
physical consequence, not a rule being enforced.

A first candidate that DID spell out the prohibitions explicitly
(`bgtest_a_v1`) also came back visually clean, but with a handful of
very-faint non-zero pixels (max channel value 24/255) in its outer border
ring — likely antialiasing bleed from the subject's fur, not a true
gradient, but strictly worse than the seamless-paper wording's two clean
0-stray-pixel results. Prefer the seamless-paper phrasing.

## What "clean" means here (no automated check exists for this case)

`validate_sprite.py` (the pipeline's only validator) checks alpha-channel
transparency against a reference image; it is skipped entirely for a
reference-less/new-creature job, hex-background or not. There is currently
NO automated purity check for a solid-hex background. Judge it the way this
proof-out did:

1. **Look at the image.** A visible gradient, vignette or floor plane is
   usually obvious to the eye.
2. **Sample the border ring numerically** — every pixel in the outer 20px
   ring, checking the max RGB channel value and how many pixels exceed a
   small tolerance (2/255 used here). A true gradient shows up as a rising
   max value toward one edge; scattered 1-pixel antialiasing bleed does not.

```python
from PIL import Image
im = Image.open(path).convert("RGB")
w, h = im.size
px = im.load()
maxv = nonblack = total = 0
for x in range(w):
    for y in list(range(0, 20)) + list(range(h - 20, h)):
        r, g, b = px[x, y]; total += 1; m = max(r, g, b)
        maxv = max(maxv, m)
        nonblack += m > 2
for y in range(h):
    for x in list(range(0, 20)) + list(range(w - 20, w)):
        r, g, b = px[x, y]; total += 1; m = max(r, g, b)
        maxv = max(maxv, m)
        nonblack += m > 2
print(total, maxv, nonblack)
```

## Scope

Tested at 256x256, `channel: "codex"`, two subjects (a quadruped mammal, a
bird), one canvas size. Not yet tested: larger canvases, the `gemini`
channel, or a subject with fine wispy edges (fur/feather tips reaching past
the silhouette are exactly where the one imperfect candidate's stray pixels
showed up) — retest before leaning on this for those cases.
