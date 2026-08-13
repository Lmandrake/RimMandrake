---
name: generating-images
description: Generates raster images from a text prompt by driving the Codex CLI's built-in $imagegen tool, then retrieves, inspects and validates the result locally. Use when asked to create, generate, draw, render or make an image, texture, sprite, icon, concept art or mockup, and when an image with a transparent background is needed. Covers the chroma-key workflow that is the only route to alpha on a ChatGPT-auth Codex install. For modifying an image that already exists, use editing-images instead.
---

# Generating images through Codex

Claude cannot synthesise raster images. Codex can. This skill makes Codex the
image worker and keeps Claude as the controller — which matters, because the
controller is the half that can *look at the result and iterate*.

**Everything here was verified on 2026-08-12** against codex-cli
0.147.0-alpha.6.6. Facts that came from reading the installed Codex skill or
running the binary are in `references/codex-contract.md`. Do not re-derive them.

## Check the toolchain first

```bash
python skills/generating-images/scripts/codex_image.py probe
```

Reports the CLI path, `CODEX_HOME`, auth mode and version without generating
anything. Run it before concluding that a failure is your prompt's fault.

## Generate

```bash
python skills/generating-images/scripts/codex_image.py generate \
  --prompt "a rusty industrial smelter seen from directly above" \
  --out src/Jawa/art_bench/smelter.png
```

For anything needing transparency, add `--chroma-key '#00ff00'` and then cut it
out — see below. Add `--dry-run` to see the resolved command and final prompt
without spending a generation.

## ⚠️ Transparency is a two-step process, and there is no shortcut

The built-in `image_gen` tool **cannot produce a transparent background.** True
model-native transparency needs `gpt-image-1.5 --background transparent`, which
runs through the CLI fallback and requires an `OPENAI_API_KEY`. This machine
authenticates as `auth_mode: chatgpt`, which does **not** provide one.

So the only route to alpha is: generate on a flat key, remove it locally.

```bash
# 1. generate on a flat key background
python skills/generating-images/scripts/codex_image.py generate \
  --prompt "a brass astrolabe, top-down, centred" \
  --chroma-key '#00ff00' \
  --out src/Jawa/art_bench/astrolabe_raw.png

# 2. convert the key to alpha
python skills/generating-images/scripts/chroma_key.py \
  --input src/Jawa/art_bench/astrolabe_raw.png \
  --out src/Jawa/art_bench/astrolabe.png
```

`chroma_key.py` auto-detects the key from the border, applies a soft matte so
edges stay antialiased, despills the key hue from the rim, and **validates its
own output** — it warns and exits non-zero if the subject vanished, if nothing
was removed, or if any corner is still opaque.

**Choosing a key colour.** Default `#00ff00`. Use `#ff00ff` if the subject is
green. Avoid `#0000ff` for blue subjects. The rule is simply that the key must
not appear in the subject; when it does, the subject gets holes punched in it
and coverage drops, which the validator will tell you about.

If a thin coloured fringe survives, re-run with `--edge-contract`.

## Always look at what you got

The reason this pipeline is worth building is that you can inspect the result.
Read the PNG back — Claude renders images — and check it against what you
asked for. To judge alpha specifically, composite over a checkerboard first;
transparent and black look identical otherwise.

```bash
python skills/generating-images/scripts/preview_alpha.py \
  --input src/Jawa/art_bench/astrolabe.png --out src/Jawa/art_bench/_check.png
```

Then read `_check.png`. A green rim, a soft halo or a chewed edge is visible
there and invisible in the raw file.

## Prompting

Full guidance in `references/prompting.md`. The three rules that matter most,
because they are the ones that get violated:

1. **Never phrase a constraint as a prohibition.** Image models condition on
   the tokens present, so "no glowing lights" reliably produces glowing lights.
   Write the state you want instead: "every lamp is dark grey, cracked, unlit".
2. **Constraints first, and keep the whole prompt short.** Early tokens carry
   more weight. A 900-word specification gets sampled, not followed.
3. **Nothing human-facing in the prompt.** Shell commands and rationale dilute
   what is left and cannot be acted on.

## Cost and timing

A generation takes roughly one to several minutes and consumes the owner's
Codex quota. Treat each call as costing something real: use `--dry-run` while
iterating on prompt wording, and generate at low ambition first — one small
image proves the plumbing before a large one proves the art.

## Reference

- `references/codex-contract.md` — verified CLI facts: how the binary is
  located, auth modes and what each unlocks, size limits, output locations.
- `references/prompting.md` — what works, what backfires, worked examples.
- `scripts/codex_image.py` — the engine: `generate`, `edit`, `probe`.
- `scripts/chroma_key.py` — key-to-alpha with self-validation.
- `scripts/preview_alpha.py` — composite over a checkerboard for inspection.
- `scripts/pnglib.py` — dependency-free PNG read/write/resize.

## Dependencies

**None beyond the standard library.** This is deliberate: Pillow is not
installed here, so the Codex-supplied `remove_chroma_key.py` cannot run, and
everything in `scripts/` works without it.
