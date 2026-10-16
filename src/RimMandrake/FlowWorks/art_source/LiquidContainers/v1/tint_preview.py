"""Apply CutoutComplex-style tint (lerp(base, base*colour, mask.r)) for review: out/<Size>/<Style>/tint_<liquid>.png,
plus a contact strip /tmp-free at out/_tints_contact.png. Colours = generate_liquid_suite.LIQUID_CONTAINER_COLORS."""
from pathlib import Path
import numpy as np
from PIL import Image
HERE = Path(__file__).resolve().parent
TINTS = {"freshwater": (0.62, 0.80, 0.98), "toxic": (0.58, 0.72, 0.28), "tar": (0.16, 0.15, 0.14)}
rows = []
for size in ["Bottle", "Bucket", "Barrel"]:
    for style in ["Scrapper", "Industrial", "Modern", "Futuristic"]:
        d = HERE / "out" / size / style
        base = np.array(Image.open(d / f"RM_{size}.png")).astype(float)
        m = np.array(Image.open(d / f"RM_{size}_m.png"))[..., 0:1].astype(float) / 255
        cells = [Image.open(d / f"RM_{size}.png")]
        for k, c in TINTS.items():
            t = base.copy()
            t[..., :3] = base[..., :3] * (1 - m) + base[..., :3] * np.array(c) * m
            im = Image.fromarray(t.clip(0, 255).astype(np.uint8), "RGBA")
            im.save(d / f"tint_{k}.png"); cells.append(im)
        rows.append(cells)
W = Image.new("RGBA", (4 * 128, 12 * 128), (120, 110, 95, 255))
for r, cells in enumerate(rows):
    for c, im in enumerate(cells):
        W.alpha_composite(im.resize((128, 128), Image.LANCZOS), (c * 128, r * 128))
W.save(HERE / "out" / "_tints_contact.png")
