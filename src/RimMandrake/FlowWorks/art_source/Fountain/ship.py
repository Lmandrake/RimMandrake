"""Downscale a 1024x1536 fountain master to the ship canvas 256x384 (drawSize (1,1.5) at 256 px/cell, D2 generous),
premultiplied (pnglib.resize_rgba, no dark halo); master alpha < 32 cleared first.  usage: ship.py <in.png> <out.png>"""
import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../../../../skills/generating-images/scripts"))
import pnglib  # noqa: E402

src, out = sys.argv[1], sys.argv[2]
w, h, rgba = pnglib.read_png(src)[:3]
nw, nh = 256, 384
# the generator leaves an invisible spray haze (alpha 1-31: 5% of A_v2's canvas); it is no picture and corrupts every
# alpha measurement (validate_sprite.py "faint fringe"), so it is cleared on the MASTER before the downscale
rgba = bytearray(rgba)
for i in range(3, len(rgba), 4):
    if rgba[i] < 32:
        rgba[i] = 0
assert w * nh == h * nw, "master aspect %dx%d is not 2:3" % (w, h)
pnglib.write_rgba(out, nw, nh, pnglib.resize_rgba(w, h, rgba, nw, nh))
print(out)
