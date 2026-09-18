#!/usr/bin/env python3
"""Synthetic per-body-type target-extent masks for conform_sprite.py.

Not art -- solid filled boxes at the exact bbox each body type measured in
design/Jawa/desert_wraps_design_capture.md SS1.2 (south-facing values, reused
for all three directions as the scale/position target; the AI-drawn
silhouette shape itself is untouched by this -- conform_sprite only scales
and translates, it never warps). This is what lets the full body-type matrix
land at realistic relative proportions (Thin narrow, Hulk tall, Fat wide)
without needing an extracted vanilla body reference.
"""
from pathlib import Path
from PIL import Image, ImageDraw

OUT = Path("/mnt/d/Luke/dev/Rimworld/Transient/art_review_desert_wraps/bodytype_refs")
OUT.mkdir(parents=True, exist_ok=True)

# (x0, y0, x1, y1) inclusive, from the design capture's SS1.2 table (south).
BBOX = {
    "Male":   (155, 176, 356, 431),
    "Female": (164, 157, 347, 445),
    "Fat":    (102, 156, 409, 450),
    "Hulk":   (112, 131, 399, 502),
    "Thin":   (202, 174, 309, 430),
}
# The devolved head family (SS2.2): vanilla-comparable bbox, used identically
# for both head styles/genders/directions as a scale target.
HEAD_BBOX = (165, 157, 347, 355)  # ~182x198 centred, matches SS2.2's measured size

for name, (x0, y0, x1, y1) in BBOX.items():
    im = Image.new("RGBA", (512, 512), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([x0, y0, x1, y1], radius=min(x1 - x0, y1 - y0) // 6,
                         fill=(128, 128, 128, 255))
    im.save(OUT / f"{name}.png")
    print("wrote", OUT / f"{name}.png", (x1 - x0 + 1, y1 - y0 + 1))

x0, y0, x1, y1 = HEAD_BBOX
im = Image.new("RGBA", (512, 512), (0, 0, 0, 0))
d = ImageDraw.Draw(im)
d.rounded_rectangle([x0, y0, x1, y1], radius=min(x1 - x0, y1 - y0) // 5,
                     fill=(128, 128, 128, 255))
im.save(OUT / "Head.png")
print("wrote", OUT / "Head.png", (x1 - x0 + 1, y1 - y0 + 1))
