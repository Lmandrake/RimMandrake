#!/usr/bin/env python3
"""preview_alpha.py — composite an RGBA image over a checkerboard.

Transparent and black are indistinguishable when you read a PNG back. This
flattens alpha onto a checkerboard so a surviving key fringe, a dark halo or a
chewed edge becomes visible. Optionally downscales first, because sprite
defects show up at display size rather than at generation size.

    python preview_alpha.py --input cut.png --out check.png
    python preview_alpha.py --input cut.png --out check.png --max-dim 256
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import pnglib  # noqa: E402


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--input", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--max-dim", type=int, default=512,
                    help="longest edge of the preview; 0 keeps native size")
    args = ap.parse_args()

    src = Path(args.input)
    if not src.is_file():
        print(f"ERROR no such file: {src}", file=sys.stderr)
        return 1

    w, h, px = pnglib.read_png(str(src))

    if args.max_dim and max(w, h) > args.max_dim:
        scale = args.max_dim / max(w, h)
        nw, nh = max(1, round(w * scale)), max(1, round(h * scale))
        px = pnglib.resize_rgba(w, h, px, nw, nh)
        w, h = nw, nh

    board = pnglib.checkerboard(w, h)
    flat = bytearray(w * h * 3)
    opaque = 0
    for i in range(w * h):
        a = px[i * 4 + 3] / 255.0
        if a > 0:
            opaque += 1
        for c in range(3):
            flat[i * 3 + c] = int(px[i * 4 + c] * a + board[i * 3 + c] * (1.0 - a))

    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    pnglib.write_png(args.out, w, h, flat)
    print(f"{w}x{h} preview, subject covers {opaque / (w * h):.1%}")
    print(f"wrote {args.out}  - read it back and look for a coloured rim")
    return 0


if __name__ == "__main__":
    sys.exit(main())
