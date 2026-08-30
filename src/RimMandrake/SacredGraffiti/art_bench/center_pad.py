#!/usr/bin/env python3
"""Crop a cutout to its subject bbox (alpha>=8), scale to fit within a target
box centered on a square canvas with margin, and write the result."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "SacredGraffiti"))
sys.path.insert(0, "/mnt/d/Luke/dev/Rimworld/skills/generating-images/scripts")
import pnglib  # noqa: E402

def main(inp, out, canvas=640, margin=64):
    w, h, px = pnglib.read_png(inp)
    floor = 8
    min_x, min_y, max_x, max_y = w, h, -1, -1
    for y in range(h):
        row = y * w
        for x in range(w):
            a = px[(row + x) * 4 + 3]
            if a >= floor:
                if x < min_x: min_x = x
                if x > max_x: max_x = x
                if y < min_y: min_y = y
                if y > max_y: max_y = y
    if max_x < 0:
        print("nothing found"); sys.exit(1)
    bw, bh = max_x - min_x + 1, max_y - min_y + 1
    cw, ch = bw, bh
    cropped = bytearray(cw * ch * 4)
    for y in range(ch):
        src = ((y + min_y) * w + min_x) * 4
        dst = y * cw * 4
        cropped[dst:dst + cw * 4] = px[src:src + cw * 4]

    target = canvas - 2 * margin
    scale = min(target / bw, target / bh)
    new_w, new_h = max(1, round(bw * scale)), max(1, round(bh * scale))
    scaled = pnglib.resize_rgba(cw, ch, cropped, new_w, new_h)

    out_px = bytearray(canvas * canvas * 4)
    off_x = (canvas - new_w) // 2
    off_y = (canvas - new_h) // 2
    for y in range(new_h):
        src = y * new_w * 4
        dst = ((y + off_y) * canvas + off_x) * 4
        out_px[dst:dst + new_w * 4] = scaled[src:src + new_w * 4]

    pnglib.write_rgba(out, canvas, canvas, out_px)
    print(f"wrote {out}  {canvas}x{canvas}, subject {new_w}x{new_h} at ({off_x},{off_y})")

if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
