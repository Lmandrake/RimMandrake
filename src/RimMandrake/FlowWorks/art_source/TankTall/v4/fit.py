#!/usr/bin/env python3
"""Fit each v4 raw drawing onto its shape master's canvas (v3/_master/<Tank>.png): scale to fit INSIDE the master's subject
box (the smaller of the width and height ratios, so no new tank draws past the master over a neighbouring cell), centre it
on the master's x and stand it on the master's ground line. Premultiplied BOX resize, alpha < 32 cleared (as v3/fit_to_master.py).
    fit.py      -> v4/<Look>/<Tank>.png for every raw/<Tank>_<Look>.png"""
from pathlib import Path
from PIL import Image
HERE = Path(__file__).resolve().parent
MASTER = HERE.parent / "v3" / "_master"
for raw in sorted((HERE / "raw").glob("*.png")):
    tank, look = raw.stem.rsplit("_", 1)
    m = Image.open(MASTER / f"{tank}.png").convert("RGBA")
    mb = m.getchannel("A").point(lambda v: 255 if v >= 32 else 0).getbbox()
    im = Image.open(raw).convert("RGBA"); a = im.getchannel("A").point(lambda v: v if v >= 32 else 0); im.putalpha(a)
    im = im.crop(a.getbbox())
    s = min((mb[2] - mb[0]) / im.width, (mb[3] - mb[1]) / im.height)
    w, h = round(im.width * s), round(im.height * s)
    im = im.convert("RGBa").resize((w, h), Image.BOX).convert("RGBA")
    im.putalpha(im.getchannel("A").point(lambda v: v if v >= 32 else 0))
    c = Image.new("RGBA", m.size, (0, 0, 0, 0)); c.alpha_composite(im, ((mb[0] + mb[2] - w) // 2, mb[3] - h))
    (HERE / look).mkdir(exist_ok=True); out = HERE / look / f"{tank}.png"; c.save(out)
    print(out.relative_to(HERE), "bbox", c.getchannel("A").getbbox(), "master", mb)
