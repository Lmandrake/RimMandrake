"""compose.py -- hose reel straight side coupling candidates (owner, 2026-10-15).

Each raw Codex edit (raw/<Look>_<A|B>.png) redraws a 128x128 crop (x 0-128, y 72-200 of the 256 Reel_Deployed art,
upscaled to 1024). This script downsamples it (BOX), registers it to the original by the body pixels right of the
coupling, and pastes ONLY the columns left of the coupling/body junction (xcut, found where the edit stops agreeing
with the original) into a copy of the original art, so the body, drum, wheel and valve are the original pixels.
The same coupling is pasted into the stored art (Reel_PumpHookup), shifted to that art's own junction.

    python3 Transient/hose_reel_coupling_2026-10-15/compose.py     -> cand/<Look>_<cand>_<state>.png + report.json
"""
import json
import os
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
TEX = os.path.join(HERE, "../../src/RimMandrake/FlowWorks/Textures/RimMandrake/FlowWorks/Hose/")
LOOKS = {"Scrapper": "", "Industrial": "Styles/Industrial/", "Modern": "Styles/Modern/", "Futuristic": "Styles/Futuristic/"}
CX0, CY0, CW = 0, 72, 128
RAW = "raw2"                 # the blockout-guided edits (blockout.py); a first unguided pass (deleted) drifted to ~31 px tall
NORMALISE = False           # raw2 is drawn at the target geometry; normalise() was for the unguided pass
YB0, YB1 = 92, 182          # rows the coupling may occupy


def load(p):
    return np.asarray(Image.open(p).convert("RGBA")).astype(float)


def premul_down(im, size):
    a = im[..., 3:4] / 255.0
    pm = np.concatenate([im[..., :3] * a, im[..., 3:4]], 2)
    r = np.stack([np.asarray(Image.fromarray(pm[..., c].astype(np.float32), "F").resize((size, size), Image.BOX))
                  for c in range(4)], 2)
    al = r[..., 3:4]
    rgb = np.where(al > 0, r[..., :3] / np.maximum(al, 1e-6) * 255.0, 0)
    return np.concatenate([np.clip(rgb, 0, 255), al], 2)


def diffcols(a, b):
    return np.abs(a - b).sum(2)[YB0:YB1].mean(0)


def register(edit, orig, x0, x1):
    """Best integer (dx, dy) placing the edit crop on the original, judged on the body columns x0..x1."""
    best = None
    for dy in range(-4, 5):
        for dx in range(-4, 5):
            e = np.roll(np.roll(edit, dy, 0), dx, 1)
            d = np.abs(e[YB0 - CY0:YB1 - CY0, x0:x1] - orig[YB0:YB1, x0:x1]).mean()
            if best is None or d < best[0]:
                best = (d, dx, dy)
    return best


def junction(orig, placed, lo=30, hi=54, thr=60):
    """Right-most column in lo..hi where the placed edit still differs from the original (the coupling's end)."""
    d = diffcols(placed, orig)
    cols = [x for x in range(lo, hi) if d[x] > thr]
    return (max(cols) + 1) if cols else lo


def paste(orig, placed, xcut, feather=3):
    out = orig.copy()
    for x in range(0, xcut + feather):
        w = 1.0 if x < xcut else 1.0 - (x - xcut + 1) / (feather + 1)
        out[YB0:YB1, x] = placed[YB0:YB1, x] * w + orig[YB0:YB1, x] * (1 - w)
    # the edit may leave stray pixels above/below the band left of the cut: keep the original there (it is empty)
    return out


def coupling_geom(img, xcut):
    al = img[..., 3]
    cols = [x for x in range(0, xcut) if (al[YB0:YB1, x] > 128).any()]
    if not cols:
        return None
    tip = cols[0]
    mids, hs = [], []
    for x in range(tip + 2, min(tip + 14, xcut)):
        ys = np.nonzero(al[YB0:YB1, x] > 128)[0]
        if len(ys):
            mids.append(YB0 + (ys[0] + ys[-1]) / 2.0)
            hs.append(ys[-1] - ys[0] + 1)
    return {"tip_u": tip, "centre_v": round(float(np.median(mids)), 1), "height_px": int(np.median(hs))}


PX = 256 / 2.8                       # art pixels per cell (drawSize 2.8 on a 256 canvas)
TIP_U, MOUTH_V = 9, 135              # HoseReelRect.NozzleTip u 9/256, MouthDZ -> v 135/256
HOSE_PX = round(0.465 * PX)          # HoseMath.VisibleWidth(1, plump 1) = 0.38 + 0.085 cells -> 42 px


def premul_resize(a, w, h):
    al = a[..., 3:4] / 255.0
    pm = np.concatenate([a[..., :3] * al, a[..., 3:4]], 2)
    r = np.stack([np.asarray(Image.fromarray(pm[..., c].astype(np.float32), "F").resize((w, h), Image.LANCZOS))
                  for c in range(4)], 2)
    r[..., 3] = np.clip(r[..., 3], 0, 255)
    alr = r[..., 3:4]
    rgb = np.where(alr > 0.5, r[..., :3] / np.maximum(alr / 255.0, 1e-6), 0)
    return np.concatenate([np.clip(rgb, 0, 255), alr], 2)


def normalise(img, xcut):
    """Stretch the new coupling (tip .. where the pump body starts) so it is HOSE_PX tall, centred on MOUTH_V, its
    flat end at TIP_U: the hose (and its end coupling, drawn at NozzleTip) then meets it on the code's own anchor."""
    al = img[..., 3]
    g = coupling_geom(img, xcut)
    tip, h0, yc = g["tip_u"], g["height_px"], g["centre_v"]
    xe = xcut
    for x in range(tip + 6, xcut):
        ys = np.nonzero(al[YB0:YB1, x] > 128)[0]
        if len(ys) and ys[-1] - ys[0] + 1 > 1.35 * h0:
            xe = x
            break
    y0, y1 = int(round(yc - h0 / 2 - 3)), int(round(yc + h0 / 2 + 3))
    strip = img[y0:y1, tip:xe].copy()
    s = HOSE_PX / h0
    nh = int(round((y1 - y0) * s))
    big = premul_resize(strip, xe - TIP_U, nh)
    out = img.copy()
    out[y0:y1, 0:xe, 3] = 0
    ny0 = int(round(MOUTH_V - nh / 2))
    reg = out[ny0:ny0 + nh, TIP_U:xe]
    a = big[..., 3:4] / 255.0
    b = reg[..., 3:4] / 255.0
    oa = a + b * (1 - a)
    rgb = np.where(oa > 0, (big[..., :3] * a + reg[..., :3] * b * (1 - a)) / np.maximum(oa, 1e-6), 0)
    out[ny0:ny0 + nh, TIP_U:xe] = np.concatenate([rgb, oa * 255], 2)
    return out, xe


def fit_tip(img, xcut):
    """Resample columns tip..xcut onto TIP_U..xcut so the flat end sits exactly where the code draws the hose's end
    coupling (HoseReelRect.NozzleTip, u 9/256); the body right of xcut is untouched."""
    g = coupling_geom(img, xcut)
    if g is None or g["tip_u"] == TIP_U:
        return img
    tip = g["tip_u"]
    band = img[YB0:YB1, tip:xcut]
    big = premul_resize(band, xcut - TIP_U, YB1 - YB0)
    out = img.copy()
    out[YB0:YB1, 0:xcut] = 0
    out[YB0:YB1, TIP_U:xcut] = big
    return out


def main():
    os.makedirs(os.path.join(HERE, "cand"), exist_ok=True)
    rep = {}
    for look, sub in LOOKS.items():
        dep = load(TEX + sub + "Reel_Deployed.png")
        sto = load(TEX + sub + "Reel_PumpHookup.png")
        rep[look] = {"orig_Deployed": coupling_geom(dep, 50), "orig_PumpHookup": coupling_geom(sto, 50)}
        for cand in "AB":
            rp = os.path.join(HERE, RAW, f"{look}_{cand}.png")
            if not os.path.exists(rp):
                continue
            edit = premul_down(load(rp), CW)
            d, dx, dy = register(edit, dep, 70, 128)
            edit = np.roll(np.roll(edit, dy, 0), dx, 1)
            placed = dep.copy()
            placed[CY0:CY0 + CW, CX0:CX0 + CW] = edit
            xcut = junction(dep, placed)
            new_dep = paste(dep, placed, xcut)
            # stored art: same coupling columns, shifted so its body junction lines up (search dx on columns xcut..xcut+20)
            best = None
            for sx in range(-6, 7):
                for sy in range(-4, 5):
                    sh = np.roll(np.roll(placed, sy, 0), sx, 1)
                    v = np.abs(sh[YB0:YB1, xcut + sx:xcut + sx + 16] - sto[YB0:YB1, xcut + sx:xcut + sx + 16]).mean()
                    if best is None or v < best[0]:
                        best = (v, sx, sy)
            _, sx, sy = best
            sh = np.roll(np.roll(placed, sy, 0), sx, 1)
            new_sto = paste(sto, sh, xcut + sx)
            xe = xes = None
            new_dep, new_sto = fit_tip(new_dep, xcut), fit_tip(new_sto, xcut + sx)
            for arr in (new_dep, new_sto):          # the end is flush at TIP_U: no glow or shadow spills left of it
                arr[YB0:YB1, :TIP_U] = 0
            if NORMALISE:
                new_dep, xe = normalise(new_dep, xcut)
                new_sto, xes = normalise(new_sto, xcut + sx)
            for state, arr in (("Deployed", new_dep), ("PumpHookup", new_sto)):
                Image.fromarray(np.clip(arr + 0.5, 0, 255).astype(np.uint8), "RGBA").save(
                    os.path.join(HERE, "cand", f"{look}_{cand}_{state}.png"))
            rep[look][cand] = {"register_dxdy": [dx, dy], "register_err": round(float(d), 1), "xcut": xcut,
                               "stored_shift": [sx, sy], "coupling_end_u": [xe, xes], "Deployed": coupling_geom(new_dep, xcut),
                               "PumpHookup": coupling_geom(new_sto, xcut + sx)}
    json.dump(rep, open(os.path.join(HERE, "report.json"), "w"), indent=1)
    print(json.dumps(rep, indent=1))


if __name__ == "__main__":
    sys.exit(main())
