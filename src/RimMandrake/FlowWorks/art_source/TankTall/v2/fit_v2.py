"""TANK_TALL_BUILD_TWICE_THE_DRINK v2: scale a raw edit (same aspect as its guide) onto the game canvas.
The raw keeps the guide's layout, so a uniform resize lands the base on the short sibling's ground line.
Premultiplied BOX downscale (no LANCZOS ringing on alpha dust); alpha < 32 cleared (faint fringe).
usage: fit_v2.py <raw.png> <out.png> <W> <H>"""
import sys
from PIL import Image
src, dst, W, H = sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4])
im = Image.open(src).convert("RGBA")
im = im.convert("RGBa").resize((W, H), Image.BOX).convert("RGBA")
a = im.getchannel("A").point(lambda v: 0 if v < 32 else v); im.putalpha(a)
im.save(dst); print(dst, im.size, "bbox", a.getbbox())
