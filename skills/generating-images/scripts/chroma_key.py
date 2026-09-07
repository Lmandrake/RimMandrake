#!/usr/bin/env python3
"""chroma_key.py — turn a flat key-colour background into real alpha.

🔴 RETIRED FROM THE GENERATION PATH, 2026-09-06 (CODEX_WRAPPER_HARVEST_FIX_1).
Nothing generates onto a key any more: the built-in `image_gen` tool emits a
real alpha channel when the prompt asks for one (MEASURED: 1448x1086 RGBA,
55.7% alpha-0, corners (0,0,0,0), 0.28% mid-alpha, no rim — and again across 7
of the 14 recovered tree orphans). `codex_image.py` no longer has a
`--chroma-key` flag, and `make_sprite.py` no longer cuts anything. **Do not
reach for this when making new art** — ask for transparency in the prompt.

It survives ONLY to process green-keyed raws that already exist on disk, and it
has exactly two callers, both of which read such legacy raws:
`src/RimStarWars/SeaBeasts/art/tools/build_sea_facings.py` and
`src/RimMandrake/DesertVehicleReskin/Source/recrop_east_v2.py`. The 7
green-background files under
`src/RimUtinni/AshkarrFlora/_artsrc/sweetline_orphans_2026-09-06/` are the same
case. When those inputs are gone, so is this file.

Why it exists rather than the helper Codex ships: that one imports Pillow,
which is not installed in the system Python here. This uses only `pnglib.py`
and the standard library.

    python chroma_key.py --input raw.png --out cut.png
    python chroma_key.py --input raw.png --out cut.png --key '#ff00ff'

Exit codes: 0 ok, 1 the result failed its own validation.
"""

from __future__ import annotations

import argparse
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import pnglib  # noqa: E402

# --- thresholds ----------------------------------------------------------
# Distances are Euclidean in 8-bit RGB, so the theoretical maximum is
# sqrt(3*255^2) = 441.
#
# BELOW_IS_BACKGROUND: generated keys are flat but not bit-identical - JPEG-ish
# ringing and mild dithering move pixels a few units. 12 is comfortably above
# that noise floor and far below any real subject colour.
#
# ABOVE_IS_SUBJECT: anything this far from the key is certainly the object.
# Between the two the pixel is a blend - an antialiased edge - and gets partial
# alpha, which is what keeps edges from stair-stepping.
#
# ⚠️ BOTH ends were wrong on the first real run, in opposite directions.
#
# The lower bound was too LOW. A generated key is flat to the eye but varies by
# 18-37 units, so background pixels landed at alpha 8-31 instead of 0 - an
# invisible fringe that still counts as subject. It inflated a measured
# bounding box by 20% and silently scaled a conformed sprite 20% undersized,
# while passing every other check. 40 clears that spread.
#
# The upper bound was too HIGH. A saturated key sits in a corner of the RGB
# cube, so most real subject colours are only 150-250 away from it; with 220,
# 36% of the image came out between alpha 128 and 254 and the art rendered
# washed out. Dark greys measure ~205 from a green key, so 120 puts genuine
# subject firmly opaque and leaves 40-120 as the antialiasing blend band.
BELOW_IS_BACKGROUND = 40.0
ABOVE_IS_SUBJECT = 120.0

# A pixel is "spilled" when the key hue bleeds onto the subject's edge. Pulling
# the key channel back to the level of its neighbours removes the green rim
# without touching genuinely green parts of the subject, because those have all
# three channels arranged differently.
DESPILL_STRENGTH = 1.0

# Border ring sampled to auto-detect the key colour. 2px is enough to be
# representative and thin enough that a subject touching the frame does not
# dominate the sample.
BORDER_SAMPLE_PX = 2

# Validation floors. A cutout that is almost entirely transparent means the key
# ate the subject; one that is almost entirely opaque means it removed nothing.
MIN_SUBJECT_COVERAGE = 0.01
MAX_SUBJECT_COVERAGE = 0.98


def parse_hex(s: str) -> tuple[int, int, int]:
    s = s.strip().lstrip("#")
    if len(s) != 6:
        raise ValueError(f"expected a 6-digit hex colour, got {s!r}")
    return tuple(int(s[i:i + 2], 16) for i in (0, 2, 4))  # type: ignore[return-value]


def detect_key(w: int, h: int, px: bytearray) -> tuple[int, int, int]:
    """Median colour of the border ring."""
    rs: list[int] = []
    gs: list[int] = []
    bs: list[int] = []
    for y in range(h):
        edge_row = y < BORDER_SAMPLE_PX or y >= h - BORDER_SAMPLE_PX
        step = 1 if edge_row else max(1, w - 1)
        for x in range(0, w, step):
            if not edge_row and BORDER_SAMPLE_PX <= x < w - BORDER_SAMPLE_PX:
                continue
            i = (y * w + x) * 4
            rs.append(px[i]); gs.append(px[i + 1]); bs.append(px[i + 2])
    if not rs:
        raise ValueError("image too small to sample a border")
    mid = len(rs) // 2
    return (sorted(rs)[mid], sorted(gs)[mid], sorted(bs)[mid])


def key_out(w: int, h: int, px: bytearray, key: tuple[int, int, int],
            t_lo: float, t_hi: float, despill: bool) -> tuple[bytearray, float]:
    kr, kg, kb = key
    # Which channel the key leads on; used only for despill.
    lead = max(range(3), key=lambda c: key[c])
    out = bytearray(px)
    visible = 0

    for i in range(0, len(px), 4):
        r, g, b = px[i], px[i + 1], px[i + 2]
        d = math.sqrt((r - kr) ** 2 + (g - kg) ** 2 + (b - kb) ** 2)

        if d <= t_lo:
            out[i + 3] = 0
            continue
        if d >= t_hi:
            a = 255
        else:
            a = int(round(255 * (d - t_lo) / (t_hi - t_lo)))

        if despill and a > 0:
            chans = [r, g, b]
            others = [chans[c] for c in range(3) if c != lead]
            ceiling = max(others)
            if chans[lead] > ceiling:
                chans[lead] = int(round(
                    ceiling + (chans[lead] - ceiling) * (1.0 - DESPILL_STRENGTH)
                ))
                out[i], out[i + 1], out[i + 2] = chans

        out[i + 3] = a
        if a > 0:
            visible += 1

    return out, visible / (w * h)


def contract_edge(w: int, h: int, px: bytearray) -> bytearray:
    """One-pixel alpha erosion, to bite off a surviving key fringe."""
    out = bytearray(px)
    for y in range(h):
        for x in range(w):
            i = (y * w + x) * 4
            if px[i + 3] == 0:
                continue
            lowest = 255
            for dy in (-1, 0, 1):
                for dx in (-1, 0, 1):
                    ny, nx = y + dy, x + dx
                    if 0 <= ny < h and 0 <= nx < w:
                        lowest = min(lowest, px[(ny * w + nx) * 4 + 3])
                    else:
                        lowest = 0
            out[i + 3] = min(px[i + 3], lowest)
    return out


def validate(w: int, h: int, px: bytearray, coverage: float) -> list[str]:
    problems = []
    if coverage < MIN_SUBJECT_COVERAGE:
        problems.append(
            f"only {coverage:.1%} of pixels survived - the key colour probably "
            f"matches the subject. Re-generate on a different key."
        )
    if coverage > MAX_SUBJECT_COVERAGE:
        problems.append(
            f"{coverage:.1%} of pixels are opaque - nothing was removed. The "
            f"background may not be flat, or the key was mis-detected."
        )
    corners = [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)]
    opaque_corners = [c for c in corners if px[((c[1] * w) + c[0]) * 4 + 3] > 8]
    if opaque_corners:
        problems.append(
            f"{len(opaque_corners)} of 4 corners are still opaque - the "
            f"background is not uniform to the frame edge."
        )
    return problems


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--input", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--key", default=None,
                    help="key colour as hex; default auto-detects from the border")
    ap.add_argument("--transparent-threshold", type=float, default=BELOW_IS_BACKGROUND)
    ap.add_argument("--opaque-threshold", type=float, default=ABOVE_IS_SUBJECT)
    ap.add_argument("--no-despill", action="store_true")
    ap.add_argument("--edge-contract", action="store_true",
                    help="erode alpha by 1px; use only if a fringe survives")
    args = ap.parse_args()

    src = Path(args.input)
    if not src.is_file():
        print(f"ERROR no such file: {src}", file=sys.stderr)
        return 1

    w, h, px = pnglib.read_png(str(src))
    key = parse_hex(args.key) if args.key else detect_key(w, h, px)

    out, coverage = key_out(w, h, px, key, args.transparent_threshold,
                            args.opaque_threshold, not args.no_despill)
    if args.edge_contract:
        out = contract_edge(w, h, out)
        coverage = sum(1 for i in range(3, len(out), 4) if out[i] > 0) / (w * h)

    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    pnglib.write_rgba(args.out, w, h, out)

    print(f"key #{key[0]:02x}{key[1]:02x}{key[2]:02x}"
          f"{'' if args.key else ' (auto)'}  "
          f"{w}x{h}  subject covers {coverage:.1%}")
    print(f"wrote {args.out}")

    problems = validate(w, h, out, coverage)
    for p in problems:
        print(f"WARN {p}", file=sys.stderr)
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
