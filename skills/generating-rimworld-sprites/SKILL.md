---
name: generating-rimworld-sprites
description: Produces RimWorld-ready sprite art that matches an existing reference asset — correct canvas, real alpha, silhouette inside the original footprint, and a style that reads as shipping in the same game. Use when creating or altering RimWorld textures, pawn or building art, damaged or variant states of an existing thing, or any PNG destined for a mod's Textures folder. Wraps generating-images and editing-images with the game's hard constraints and an offline validator that rejects art before it costs a game load.
---

# RimWorld sprite art

A RimWorld texture is not a picture, it is an asset with a contract: exact
canvas, real alpha, and a silhouette that occupies the tiles the def says it
occupies. Art that violates any of those looks broken in game and costs a
**~23–30 minute** cold load to discover.

So the rule that governs everything here: **no sprite reaches the Mods folder
until the validator passes offline.** The load is for learning things that
cannot be computed. Canvas size and alpha can be computed.

Builds on `generating-images` (engine, chroma key) and `editing-images`
(invariants, drift detection). Read
`../generating-images/references/codex-contract.md` for the verified CLI facts.

## ⚠️ The size trap — read this before generating anything

`gpt-image-2` requires **both edges to be multiples of 16** and **total pixels
between 655,360 and 8,294,400**.

Typical RimWorld sprites fail both ends:

| asset | pixels | legal to generate? |
|---|---|---|
| a `512x640` facing | 327,680 | ❌ **below the minimum** |
| a `1416x1416` sheet | 2,005,056 | ❌ 1416 is not a multiple of 16 |
| `1024x1024` | 1,048,576 | ✅ |
| `2048x2048` | 4,194,304 | ✅ |

**Never generate at the target size.** Generate at a legal size with the right
*aspect*, then downscale with `pnglib.resize_rgba`, which premultiplies alpha
and so avoids the dark halo that plain averaging produces on a cutout.

## Workflow

Copy this checklist and work down it:

```
- [ ] 1. Measure the reference (canvas, alpha, coverage, palette)
- [ ] 2. Generate or edit on a chroma key at a LEGAL size
- [ ] 3. Cut the key to alpha
- [ ] 4. Conform to the reference canvas
- [ ] 5. Validate against the reference
- [ ] 6. Look at it composited, at true display size
```

### 1. Measure the reference

```bash
python skills/generating-rimworld-sprites/scripts/validate_sprite.py \
  --reference path/to/original_south.png --describe
```

Never assume the canvas. RimWorld sprites routinely **transpose between
facings** — the smelter is `512x640` north/south and `640x512` east/west. A
validator that checks one canvas for all four facings will pass broken art.

### 2. Generate or edit

Match the reference's *aspect*, not its size. For a `512x640` reference
(4:5), generate `1024x1280` — both multiples of 16, 1,310,720 px, in range.

Always pass `--chroma-key`; RimWorld textures need alpha and there is no other
route to it on this install.

### 3–4. Cut and conform

```bash
python skills/generating-images/scripts/chroma_key.py \
  --input raw.png --out cut.png

python skills/generating-rimworld-sprites/scripts/conform_sprite.py \
  --reference original_south.png --input cut.png --out final_south.png
```

`conform_sprite.py` trims, scales and **registers the subject against the
reference by mask overlap** rather than by bounding-box centre — damaged art is
missing chunks, so its bounding box centre is not where the machine sits.

### 5. Validate

```bash
python skills/generating-rimworld-sprites/scripts/validate_sprite.py \
  --reference original_south.png --candidate final_south.png
```

Findings are graded: **REJECT** blocks, **WARN** asks a human to look, and
`--strict` promotes warnings to blocks.

| Family | Catches |
|---|---|
| Canvas | size differs from the reference |
| **Linear span** | subject width or height off by >6%, either direction |
| **Subject aspect** | art squashed rather than redrawn |
| **Origin** | subject sits somewhere else on the canvas |
| Footprint | silhouette overruns the reference's box |
| Coverage | area collapsed, or ballooned (warn) |
| Alpha channel | missing entirely |
| Corners | key not fully removed |
| **Faint fringe** | pixels at alpha 1–31: invisible, but they corrupt every measurement |
| **Mid-alpha mass** | a fat alpha histogram middle — art renders washed out |
| **Key spill** (warn) | the rim is measurably more key-coloured than the body |
| **Canvas contact** (warn) | subject touches an edge the reference does not — clipping |
| **Fragments** (warn) | solid pixels detached from the main mass |
| Identity | pixel-identical to the reference — nothing changed |

⚠️ **Span is checked separately from coverage, and that separation is the
point.** A wreck legitimately *loses area* — material is removed — so the area
tolerance has to stay loose. But it must still *span* its footprint. Checking
only area is what let a sprite ship 20% undersized while every check passed.

### The validator is itself tested

```bash
python skills/generating-rimworld-sprites/scripts/selftest.py \
  --reference path/to/any_real_sprite.png
```

Nine cases: a control that must pass, and eight synthesised defects that must
each be rejected *for the stated reason*. Run it after changing any threshold.

It has already earned its place twice. It found the fringe threshold set at
0.5% when the real defect measured 0.12% — above the bug it was written to
catch, so it would never have fired. And it found the identity check hashing
*file bytes*, so re-encoding the same pixels defeated it; it now hashes pixels.

**Thresholds are calibrated against measurements, not taste.** Each constant in
`validate_sprite.py` carries the observation that set it. If you change one,
re-run the self-test and update the note.

### 6. Look at it

```bash
python skills/generating-images/scripts/preview_alpha.py \
  --input final_south.png --out _check.png --max-dim 128
```

**At true display size**, not at generation size. The project's own pilot
learned this the hard way: art that read beautifully at 1024px read as brown
mud at sprite size, because the damage was mid-tone surface detail rather than
silhouette.

To judge several candidates at once, or to judge one against the reference:

```bash
python skills/generating-rimworld-sprites/scripts/contact_sheet.py \
  --reference original_south.png --out sheet.png a.png b.png c.png
```

Two rows — large for craft, true sprite size for whether it reads at all — all
over a checkerboard so transparency is visible rather than read as black.
**The validator says shippable; only this says good.**

## Art direction that survives downscaling

Earned on this project's pilot; both rules are now non-negotiable.

1. **Silhouette, not surface.** Damage must be **subtractive** — chunks torn
   out of the outline. Surface corrosion disappears into noise at sprite size.
   Lit indicators and hard cable shapes survive; mid-tone rust does not.
2. **Nothing projects past the outline.** A hose reaching outside the footprint
   overlaps whatever the player built next door, *and* costs the machine its
   own size, because conforming scales the whole drawing back into the original
   canvas. Measured cost on the first attempt: **14% of body size**.

Phrase both positively in the prompt — "every fitting terminates flush against
the hull", never "no cables sticking out". See
`../generating-images/references/prompting.md`.

## Matching the reference's style

Attach the reference with `--image` and edit from it rather than generating
fresh. A generated-from-scratch sprite will not match a shipped mod's palette
and line quality, and mismatch is more obvious in game than missing detail.

State the invariants every iteration: *"the silhouette, canvas, camera angle
and palette stay exactly as they are; change only the surface"*.

## Multi-facing assets

RimWorld `Graphic_Multi` things ship four facings that must agree — a hole in
one flank appears in every view that can see that flank.

**Prove one facing before attempting four.** Four-view consistency fails for
reasons unrelated to whether the pipeline works, and one facing is enough to
learn whether the art direction survives downscaling.

### ⚠️ Generate facings individually, not as a 2×2 sheet

The sheet is the obvious way to get consistency — one machine drawn four ways,
in one pass. **Measured 2026-08-12, it is the wrong trade**, and the reason is
resolution rather than art.

A generation returns roughly a fixed pixel budget regardless of what is in it.
Put four facings in one image and each gets a quarter of it:

| approach | pixels per facing | oversampling vs a 512×640 sprite |
|---|---|---|
| 2×2 sheet (1254×1254) | ~393,000 | **1.2×** |
| individual (1120×1405) | ~1,574,000 | **4.8×** |

**4× fewer pixels per facing, leaving almost no downsampling headroom.** The
crispness of a finished sprite comes from generating well above target and
area-averaging down; at 1.2× there is nothing to average.

What the sheet *did* do well, so this is a trade rather than a failure: it held
the 2×2 layout, kept each cell's own viewing direction, and produced four
panels more stylistically alike than four independent runs. It still did not
deliver verifiable damage correspondence between views.

**Recommendation: generate each facing individually, anchored to a chosen
sibling** — pass the reference as image 1 and the approved facing as image 2,
and ask for a match on palette, material and damage language. That buys most of
the consistency at full resolution.

## Before it ships

Deploying is a separate claim from writing. The game reads the Steam Mods
folder, never this repo — run `python src/RimMandrake/Utils/deploy_custom_mods.py` for a plan,
read it, then `--apply`. Per `agents_def.md`, only deploy your own files.

## Reference

- `scripts/validate_sprite.py` — the graded reference-vs-candidate gate; `--describe` to
  measure a single file.
- `scripts/selftest.py` — nine cases proving the validator catches what it claims.
- `scripts/contact_sheet.py` — candidates beside the reference, two sizes.
- `scripts/conform_sprite.py` — trim, scale, register onto the reference canvas.
- `../generating-images/` — engine, chroma key, alpha preview, prompting.
- `../editing-images/` — invariants and drift detection.

## Dependencies

None beyond the standard library.
