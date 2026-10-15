"""TANK_TALL_BUILD_TWICE_THE_DRINK: fit a painted tall-tank master (codex edit of the short sibling) onto its game canvas.
usage: fit_tall.py <master.png> <out.png> <canvas_h> <subject_h> <bottom_y> [x_stretch]
Canvas is 512 wide (drawSize x = 2). bottom_y matches the short sibling's base line shifted by the drawOffset,
so tall and short stand on the same ground. Premultiplied-alpha downscale; alpha < 32 cleared (faint fringe)."""
import sys
from PIL import Image
src, dst, H, sh, bottom = sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4]), int(sys.argv[5])
im = Image.open(src).convert("RGBA")
a = im.getchannel("A").point(lambda v: v if v >= 32 else 0)
im.putalpha(a)
im = im.crop(a.getbbox())
xs = float(sys.argv[6]) if len(sys.argv) > 6 else 1.0  # mild widening so the upright hull spans the 2-cell footprint
sw = round(im.width * sh / im.height * xs)
im = im.convert("RGBa").resize((sw, sh), Image.LANCZOS).convert("RGBA")
a = im.getchannel("A").point(lambda v: v if v >= 32 else 0)
im.putalpha(a)
c = Image.new("RGBA", (512, H), (0, 0, 0, 0))
c.alpha_composite(im, ((512 - sw) // 2, bottom - sh))
c.save(dst)
print(dst, c.size, "subject", sw, "x", sh, "bbox", c.getchannel("A").getbbox())
