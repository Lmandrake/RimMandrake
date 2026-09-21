#!/usr/bin/env python3
"""Stack three per-creature contact sheets into one vertical review sheet."""
import sys
from pathlib import Path

sys.path.insert(0, "/mnt/d/Luke/dev/Rimworld/.claude/skills/generating-images/scripts")
import pnglib  # noqa: E402

GAP = 24
PAD = 16

def main():
    paths = sys.argv[1:-1]
    out = sys.argv[-1]
    imgs = [pnglib.read_png(p) for p in paths]
    width = max(w for w, h, _ in imgs) + PAD * 2
    height = PAD + sum(h for _, h, _ in imgs) + GAP * (len(imgs) - 1) + PAD
    canvas = bytearray(b"\xff" * (width * height * 3))
    y = PAD
    for w, h, px in imgs:
        x = (width - w) // 2
        for yy in range(h):
            src = yy * w * 4
            drow = (y + yy) * width * 3
            for xx in range(w):
                s = src + xx * 4
                r, g, b, a = px[s:s+4]
                d = drow + (x + xx) * 3
                if a == 255:
                    canvas[d:d+3] = bytes((r, g, b))
                elif a:
                    for k, v in enumerate((r, g, b)):
                        canvas[d+k] = (v * a + canvas[d+k] * (255 - a)) // 255
        y += h + GAP
    pnglib.write_png(out, width, height, canvas)
    print(f"wrote {out} ({width}x{height})")

if __name__ == "__main__":
    main()
