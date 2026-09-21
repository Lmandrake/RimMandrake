#!/usr/bin/env python3
"""Kill the invisible alpha fringe (1-31) and stretch alpha so the most opaque
pixel reaches 255. Model-native alpha from $imagegen tops out at 254, which
leaves the validator's 'solid' bucket empty and its fringe check hot."""
import sys
sys.path.insert(0, "/mnt/d/Luke/dev/Rimworld/skills/generating-images/scripts")
import pnglib  # noqa: E402

FLOOR = 32     # alpha 1-31 is invisible but corrupts every measurement
KNEE = 200     # at or above this the pixel is opaque under a Cutout shader anyway

def main(inp, out):
    w, h, px = pnglib.read_png(inp)
    px = bytearray(px)
    top = max(px[3::4]) or 255
    killed = lifted = 0
    for i in range(3, len(px), 4):
        a = px[i]
        if a == 0:
            continue
        if a < FLOOR:
            px[i] = 0
            killed += 1
        elif a >= KNEE and a != 255:
            px[i] = 255
            lifted += 1
    pnglib.write_rgba(out, w, h, bytes(px))
    print(f"wrote {out}  peak alpha was {top}, fringe killed {killed}, lifted to 255 {lifted}")

if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
