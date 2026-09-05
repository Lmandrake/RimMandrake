#!/usr/bin/env python3
"""Alpha cutout via rembg — the better replacement for chroma_key.py.

The Codex channel (ChatGPT auth) cannot emit native transparency, so historically
every sprite was generated on a flat green key and cut with chroma_key.py. rembg
removes the background from ANY neutral/plain background with a trained matte, so:
  - no green key needed (generate on a plain neutral background instead),
  - antialiased edges survive (soft alpha matte),
  - no key-colour despill artifacts on rims that happen to be green-ish.

🔴 Run with the rwgfx venv python, which has rembg installed:
    ~/.venvs/rwgfx/bin/python skills/generating-images/scripts/rembg_cut.py --input raw.png --out cut.png

Options:
  --input   the raw image (any background)
  --out     destination PNG (RGBA)
  --tight   crop to the subject's alpha bounding box (default: keep canvas)
  --min-opaque N   fail if <N%% of pixels end up opaque (default 3) — guards a
                   silent all-transparent cutout, the way chroma_key validated.
"""
import argparse
import sys


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--tight", action="store_true")
    ap.add_argument("--min-opaque", type=float, default=3.0)
    a = ap.parse_args()

    try:
        from rembg import remove
        from PIL import Image
        import numpy as np
    except ImportError as e:
        sys.exit("missing dep (%s) — run with ~/.venvs/rwgfx/bin/python" % e)

    inp = Image.open(a.input).convert("RGBA")
    out = remove(inp)  # returns RGBA with a soft alpha matte

    alpha = np.array(out)[:, :, 3]
    opaque_pct = 100.0 * (alpha > 0).mean()
    if opaque_pct < a.min_opaque:
        sys.exit("cutout is %.1f%% opaque (< %.1f%%) — rembg found almost no "
                 "subject; check the input has a clear subject on a plain "
                 "background" % (opaque_pct, a.min_opaque))

    if a.tight:
        ys, xs = np.where(alpha > 0)
        if len(xs):
            out = out.crop((xs.min(), ys.min(), xs.max() + 1, ys.max() + 1))

    out.save(a.out)
    print("cut %s -> %s  (%dx%d, %.0f%% opaque%s)" % (
        a.input, a.out, out.width, out.height, opaque_pct,
        ", tight-cropped" if a.tight else ""))


if __name__ == "__main__":
    main()
