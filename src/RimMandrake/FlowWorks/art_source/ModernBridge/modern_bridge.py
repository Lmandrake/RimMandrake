#!/usr/bin/env python3
"""Modern bridges as plain modern bridges: the firetruck red becomes painted structural steel (MODERN_BRIDGE_REDRAW_BRIDGE_NOT_PLUMBING).

Owner 2026-10-24: "Bridges make no sense to color like any of this water stuff. They should look like modern bridges, period."
So the Modern suspension bridge and drawbridge carry neither the old pipe red nor the new waterworks blue: concrete decks
(already grey), galvanised grating and cables (already silver), and the red trim, anchors, gate frames and winch frames
repainted the flat blue-grey of highway bridge steel, with light weathering.

A recolour, as art_source/ModernStyle/waterworks_blue.py: only colour moves, alpha is copied byte for byte, so every piece
keeps the geometry the deck atlases, drawbridge leaf math and anchor seats were fitted to. Per pixel a red weight (waterworks_blue's, with a
narrower hue band that spares wood) blends the original with
  hue  STEEL_H, sat STEEL_S (almost neutral: paint, not a colour statement),
  val  VAL_0 + VAL_K * v (a mid grey below the concrete, so the frame still reads against the deck),
then a low-frequency grime field. Non-red pixels are untouched, so a second pass moves under 1% of pixels (half-weighted edges)
and the installed art can always be re-derived from either the red or the repainted pictures.

The no-plumbing check, `plumbing_colour(im)`, is what selftest_modern_bridge_art.py pins: it fails on the red set (and on
a pipe-blue fixture) and passes on every repainted piece.

Usage: modern_bridge.py OUT_DIR [--src TEXTURES_DIR] [--atlases]
  writes OUT_DIR/<rel path> for every piece in pieces(); --atlases also rebuilds the deck link atlases from the repainted
  decks (SuspensionLooks/build_deck_atlas.build). Installing is a separate, ledgered step (art.py install)."""
import argparse
import sys
import zlib
from pathlib import Path

import numpy as np
from PIL import Image

HERE = Path(__file__).resolve().parent
TEX = HERE.parents[1] / "Textures"
sys.path.insert(0, str(HERE.parent / "ModernStyle"))
import waterworks_blue as WB  # noqa: E402

SUSP = "RimMandrake/FlowWorks/SuspensionBridge/Modern"
DRAW = "Things/Building/FlowWorks/Drawbridge"

STEEL_H = 208 / 360   # cool grey
STEEL_S = 0.07
VAL_0, VAL_K = 0.16, 0.50
GRIME = 0.10
# the bridge red sits within 10 deg of 0 (census 2026-10-24); the timber pieces' wood starts at 15 deg, so the band is
# narrower than the pipe recolour's (16..34 deg would grey the wood a little more on every pass)
RED_CORE, RED_EDGE = 10 / 360, 14 / 360

# pipe-colour bands for the check: the retired firetruck red and the current waterworks blue
RED_DEG, BLUE_LO, BLUE_HI = 20, 185, 225
RED_SAT, BLUE_SAT, VAL_MIN = 0.45, 0.20, 0.25   # red: firetruck s > 0.6, brown wood/rust below; blue: the faded
                                                # waterworks blue on the installed pipes reads s 0.25..0.40
MAX_SHARE = 0.01      # at most 1% of opaque pixels in a pipe colour


def pieces(tex=TEX):
    """Every Modern bridge picture (atlases excluded: they are rebuilt from their deck)."""
    rels = sorted(p.relative_to(tex).as_posix() for p in (tex / SUSP).glob("*.png") if not p.stem.endswith("_Atlas"))
    rels += sorted(p.relative_to(tex).as_posix() for p in (tex / DRAW).glob("*_Modern*.png"))
    return rels


def atlas_jobs(tex=TEX):
    """(deck rel, atlas rel) for each Modern deck that has a link atlas."""
    out = []
    for rel in pieces(tex):
        a = rel[:-4] + "_Atlas.png"
        if (tex / a).is_file():
            out.append((rel, a))
    return out


def red_weight(rgb):
    """Per-pixel weight in [0, 1]: how much a pixel is the bridge red (waterworks_blue.red_weight with the narrower band)."""
    mx, mn = rgb.max(-1), rgb.min(-1)
    s = np.where(mx > 0, (mx - mn) / np.maximum(mx, 1e-6), 0.0)
    h = WB._hue(rgb, mx, mn)
    dist = np.minimum(h, 1.0 - h)
    return (1.0 - WB._ramp(dist, RED_CORE, RED_EDGE)) * WB._ramp(s, WB.SAT_LO, WB.SAT_HI)


def repaint(im, name):
    """Return (RGBA image, info). `name` seeds the grime (use the relative path) so output is reproducible."""
    src = np.asarray(im.convert("RGBA"))
    rgb = src[..., :3].astype(float) / 255.0
    w = red_weight(rgb)
    mx = rgb.max(-1)
    rng = np.random.default_rng(zlib.crc32(name.encode()))
    scale = max(src.shape[:2]) / 256.0
    steel = WB._hsv_to_rgb(np.full(w.shape, STEEL_H), np.full(w.shape, STEEL_S), np.clip(VAL_0 + VAL_K * mx, 0, 1))
    steel *= (1.0 - GRIME * WB._field(w.shape, rng, 6 * scale) ** 1.5)[..., None]
    out = rgb * (1 - w[..., None]) + steel * w[..., None]
    res = np.dstack([np.clip(np.round(out * 255), 0, 255).astype(np.uint8), src[..., 3]])
    op = src[..., 3] > 128
    return Image.fromarray(res, "RGBA"), {"repainted_px": int(((w > 0.5) & op).sum()), "opaque_px": int(op.sum())}


def plumbing_colour(im, alpha_min=128):
    """(red share, blue share) of opaque pixels in a saturated pipe colour; a bridge passes when both are <= MAX_SHARE."""
    a = np.asarray(im.convert("RGBA")).astype(float) / 255.0
    rgb, op = a[..., :3], a[..., 3] > alpha_min / 255.0
    if not op.any():
        return 0.0, 0.0
    mx, mn = rgb.max(-1), rgb.min(-1)
    s = np.where(mx > 0, (mx - mn) / np.maximum(mx, 1e-6), 0.0)
    deg = WB._hue(rgb, mx, mn) * 360
    lit = (mx > VAL_MIN) & op
    red = lit & (s > RED_SAT) & (np.minimum(deg, 360 - deg) < RED_DEG)
    blue = lit & (s > BLUE_SAT) & (deg >= BLUE_LO) & (deg <= BLUE_HI)
    n = float(op.sum())
    return float(red.sum()) / n, float(blue.sum()) / n


def is_bridge_coloured(im):
    r, b = plumbing_colour(im)
    return r <= MAX_SHARE and b <= MAX_SHARE


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("out")
    ap.add_argument("--src", default=str(TEX))
    ap.add_argument("--atlases", action="store_true")
    a = ap.parse_args(argv)
    src, out = Path(a.src), Path(a.out)
    bad = 0
    for rel in pieces(src):
        im = Image.open(src / rel)
        res, info = repaint(im, rel)
        dst = out / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        res.save(dst)
        r0, b0 = plumbing_colour(im)
        r1, b1 = plumbing_colour(res)
        bad += not is_bridge_coloured(res)
        print(f"{rel} {info} red {r0:.3f}->{r1:.3f} blue {b0:.3f}->{b1:.3f}")
    if a.atlases:
        sys.path.insert(0, str(HERE.parent / "SuspensionLooks"))
        import build_deck_atlas as DA
        for deck, atlas in atlas_jobs(src):
            DA.build(out / deck, 28).save(out / atlas)
            print("atlas", atlas)
    print("pieces not bridge-coloured after repaint:", bad)
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
