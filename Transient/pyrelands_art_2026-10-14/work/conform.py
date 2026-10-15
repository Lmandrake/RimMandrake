#!/usr/bin/env python3
"""Conform the raw renders of PYRELANDS_SHIP_READINESS_1's art pass to game canvases.
raw/<name>.png -> final/<texture file>.png. Edits of a living sprite were drawn at the same position and scale,
so the whole canvas is resized (premultiplied) to the reference canvas; free renders are trimmed, centred and fitted."""
import sys
from pathlib import Path
from PIL import Image
W = Path(__file__).resolve().parent
R = W.parents[2]
LIVE = R / "src/RimMandrake/Pyrelands/Textures/Things/Pawn/Animal/Pyrelands"
BRK = R / "src/RimMandrake/Pyrelands/Textures/Things/Building/Power/RM_LightningBreaker.png"
(W / "final").mkdir(exist_ok=True)

def clean(im):
    a = im.getchannel("A").point(lambda v: 0 if v < 32 else v)
    im.putalpha(a)
    return im

def resize(im, size):
    return im.convert("RGBa").resize(size, Image.LANCZOS).convert("RGBA")

def whole(raw, ref, out):
    im = Image.open(raw).convert("RGBA")
    clean(resize(im, Image.open(ref).size)).save(out)

def fit(raw, canvas, frac_w, frac_h, out):
    im = clean(Image.open(raw).convert("RGBA"))
    im = im.crop(im.getchannel("A").getbbox())
    s = min(canvas[0] * frac_w / im.width, canvas[1] * frac_h / im.height)
    im = resize(im, (max(1, round(im.width * s)), max(1, round(im.height * s))))
    c = Image.new("RGBA", canvas, (0, 0, 0, 0))
    c.alpha_composite(im, ((canvas[0] - im.width) // 2, (canvas[1] - im.height) // 2))
    clean(c).save(out)

for c in ("Emberscythe", "FireWasp", "Flamefang", "Sytheclaw", "Barbslinger"):
    for f in ("south", "east", "north"):
        raw = W / "raw" / f"Dessicated_{c}_{f}.png"
        if raw.exists():
            whole(raw, LIVE / c / f"{c}_{f}.png", W / "final" / f"Dessicated_{c}_{f}.png")
jobs = {"BarbslingerSpike": ((128, 128), 0.5, 0.86), "BreakerCore": ((128, 128), 0.84, 0.84),
        "FirefoamSprayer": ((256, 256), 0.9, 0.9)}
for n, (cv, fw, fh) in jobs.items():
    if (W / "raw" / f"{n}.png").exists():
        fit(W / "raw" / f"{n}.png", cv, fw, fh, W / "final" / f"{n}.png")
if (W / "raw" / "Breaker_Off.png").exists():
    # a frame swap on the SAME building: register the tripped frame's base onto the normal sprite's (width and
    # bottom edge), so the frame does not jump when the breaker trips; only the thrown lever may rise above it
    im = resize(Image.open(W / "raw" / "Breaker_Off.png").convert("RGBA"), Image.open(BRK).size)
    ref = Image.open(BRK).getchannel("A").point(lambda v: 255 if v >= 32 else 0).getbbox()
    bb = im.getchannel("A").point(lambda v: 255 if v >= 32 else 0).getbbox()
    sub = im.crop(bb)
    s = (ref[2] - ref[0]) / sub.width
    sub = resize(sub, (round(sub.width * s), round(sub.height * s)))
    c = Image.new("RGBA", im.size, (0, 0, 0, 0))
    c.alpha_composite(sub, (ref[0], ref[3] - sub.height))
    clean(c).save(W / "final" / "RM_LightningBreaker_Off.png")
print("\n".join(sorted(p.name for p in (W / "final").glob("*.png"))))
