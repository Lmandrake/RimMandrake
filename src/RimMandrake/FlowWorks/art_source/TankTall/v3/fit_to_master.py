"""Fit a look render whose subject drifted in size onto its master's footprint: scale so the subject's WIDTH equals the
master's, centre it on the master's x, and stand it on the master's ground line (bbox bottom). Premultiplied BOX resize,
alpha < 32 cleared. usage: fit_to_master.py <raw.png> <master.png> <out.png>"""
import sys
from PIL import Image
raw, master, out = sys.argv[1:4]
m = Image.open(master).convert("RGBA"); mb = m.getchannel("A").point(lambda v: 255 if v >= 32 else 0).getbbox()
im = Image.open(raw).convert("RGBA"); a = im.getchannel("A").point(lambda v: v if v >= 32 else 0); im.putalpha(a); im = im.crop(a.getbbox())
w = mb[2] - mb[0]; h = round(im.height * w / im.width)
im = im.convert("RGBa").resize((w, h), Image.BOX).convert("RGBA")
im.putalpha(im.getchannel("A").point(lambda v: v if v >= 32 else 0))
c = Image.new("RGBA", m.size, (0, 0, 0, 0)); c.alpha_composite(im, (mb[0], max(0, mb[3] - h)))
c.save(out); print(out, "bbox", c.getchannel("A").getbbox(), "master", mb)
