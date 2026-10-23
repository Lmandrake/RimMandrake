#!/usr/bin/env python3
"""Cut the four parts of a generated Modern joins sheet (coupling, flange, tee, collar; left to right) and conform them
to the live canvases with the live anchors kept (Coupler 128 centred at the old centre, Flange 128 flush to the right
edge, Saddle 256 sleeve centred on the old sleeve, UnderCollar/UnderPipe via UnderCouplers/conform_generated.py).
Usage: fit_joins.py SHEET.png STRIP.png OUTDIR"""
import subprocess, sys
from pathlib import Path
import numpy as np
from PIL import Image
HERE = Path(__file__).resolve().parent

def parts(sheet):
    a = np.asarray(sheet)[..., 3] > 32
    cols = np.where(a.any(0))[0]
    breaks = np.where(np.diff(cols) > 15)[0]
    starts = [cols[0]] + [cols[b + 1] for b in breaks]; ends = [cols[b] for b in breaks] + [cols[-1]]
    out = []
    for s, e in zip(starts, ends):
        sub = sheet.crop((s, 0, e + 1, sheet.height)); sa = np.asarray(sub)[..., 3] > 32
        ys = np.where(sa.any(1))[0]; xs = np.where(sa.any(0))[0]
        out.append(sub.crop((xs[0], ys[0], xs[-1] + 1, ys[-1] + 1)))
    return out

def down(im, size):
    a = np.asarray(im).astype(np.float32) / 255; pm = a.copy(); pm[..., :3] *= pm[..., 3:4]
    r = np.asarray(Image.fromarray((pm * 255).astype(np.uint8)).resize(size, Image.LANCZOS)).astype(np.float32) / 255
    al = r[..., 3:4]; r[..., :3] = np.where(al > 1e-3, r[..., :3] / np.maximum(al, 1e-3), 0)
    r[..., 3] = np.where(r[..., 3] < 0.12, 0, r[..., 3])
    return Image.fromarray((np.clip(r, 0, 1) * 255 + .5).astype(np.uint8))

def place(canvas, part, h=None, w=None, cx=None, cy=None, right=None):
    W, H = canvas
    if h and not w: w = max(1, round(part.width * h / part.height))
    if w and not h: h = max(1, round(part.height * w / part.width))
    p = down(part, (w, h)); c = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    x = (right - w) if right is not None else round(cx - w / 2)
    c.alpha_composite(p, (x, round(cy - h / 2))); return c

def main(sheet, strip, out):
    out = Path(out); out.mkdir(parents=True, exist_ok=True)
    cpl, fl, tee, col = parts(Image.open(sheet).convert("RGBA"))
    # Coupler: old collar 19x31 at centre (63.5, 64.5); a PVC coupling is ~1.25 pipe tall (pipe 0.136 cell = 17 px)
    place((128, 128), cpl, h=23, cx=63.5, cy=64.5).save(out / "Coupler.png")
    # Flange: old bar x 115..128, y 47..80 (flush to the port edge)
    place((128, 128), fl, h=33, w=10, cy=63.5, right=128).save(out / "Flange.png")
    # Saddle: old sleeve rows 107..147 (centre y 127, x 108..149 centre 128.5); sleeve height ~40 px
    sleeve_frac = 0.59                              # sleeve height / tee total height in the generated part
    th = round(40 / sleeve_frac); tw = round(tee.width * th / tee.height)
    sad = Image.new("RGBA", (256, 256), (0, 0, 0, 0))
    sad.alpha_composite(down(tee, (tw, th)), (round(128.5 - tw / 2), 107))
    sad.save(out / "Saddle.png")
    col.save(out / "_collar_master.png")
    subprocess.run([sys.executable, str(HERE.parent / "UnderCouplers/conform_generated.py"), "Modern",
                    str(out / "_collar_master.png"), strip, str(out / "_under")], check=True)
    for n in ("UnderCollar", "UnderPipe"):
        Image.open(out / "_under/Modern" / f"{n}.png").save(out / f"{n}.png")
    print("wrote", sorted(p.name for p in out.glob("*.png")))

if __name__ == "__main__":
    main(*sys.argv[1:4])
