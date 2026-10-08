#!/usr/bin/env python3
"""Contact sheet + body-lock metric for the flyer sample (FLYER_STABLE_BODY_GATE_1). Read-only on src."""
import sys, pathlib
import numpy as np
from PIL import Image, ImageDraw
REPO = pathlib.Path(__file__).resolve().parents[2]
SRC = REPO / "src"
idx = {}
for p in SRC.rglob("*.png"):
    s = str(p); i = s.find("/Textures/")
    if i >= 0: idx.setdefault(s[i+10:-4], p)
SAMPLE = [  # (defName, body plan, static texPath, frame prefix, n frames)
 ("RM_FireHawk", "bird", "Things/Pawn/Animal/Pyrelands/FireHawk/FireHawk", "Things/Pawn/Animal/Pyrelands/FireHawk/FireHawk_Flying_", 5),
 ("RM_FireWasp", "insect", "Things/Pawn/Animal/Pyrelands/FireWasp/FireWasp", "Things/Pawn/Animal/Pyrelands/FireWasp/FireWasp_Fly_", 8),
 ("RSW_Hawkbat", "bat-wing", "swanimals/Hawkbat/Hawkbat", "swanimals/Hawkbat/Hawkbat_Flying_", 4),
 ("RSW_Neebray", "membrane/ray", "swanimals/Neebray/Neebray", "swanimals/Neebray/Neebray_Flying_", 4),
 ("RM_Krizzak", "moth (4-wing)", "RM_Abyss/Things/Pawn/Animal/RM_Krizzak/RM_Krizzak", "RM_Abyss/Things/Pawn/Animal/RM_Krizzak/RM_Krizzak_Flying_", 5),
 ("RUT_EmperorVulture", "large bird", "Things/Pawn/Animal/RUT_EmperorVulture/RUT_EmperorVulture", "", 0),
 ("RM_Thozzik", "insect (no frames)", "RM_TheRot/Fauna/Redrawn/Thozzik/Thozzik", "", 0),
 ("RM_Blisterfloat", "gas-bag floater", "Things/Pawn/Animal/RM_Blisterfloat/RM_Blisterfloat", "", 0),
]
C = 128
def load(k):
    p = idx.get(k)
    if not p: return None
    return Image.open(p).convert("RGBA")
def bodylock(prefix, n, facing):
    fr = [load(f"{prefix}{i}_{facing}") for i in range(1, n+1)]
    fr = [f for f in fr if f is not None]
    if len(fr) < 2: return None
    size = fr[0].size
    fr = [np.asarray(f.resize(size)).astype(float) for f in fr]
    a = [f[..., 3] > 128 for f in fr]
    inter = np.logical_and.reduce(a); mean_area = np.mean([x.sum() for x in a])
    core = inter.sum() / max(mean_area, 1)
    if inter.sum() == 0: return core, float("nan"), 0
    rgb = np.stack([f[..., :3][inter] for f in fr])
    drift = float(np.mean(np.abs(rgb - rgb.mean(0))))
    cents = [np.argwhere(x).mean(0) for x in a]
    cd = float(np.max([np.linalg.norm(c - cents[0]) for c in cents]) / size[0] * 100)
    return core, drift, cd
rows = []
for dn, plan, st, pre, n in SAMPLE:
    cells = [load(f"{st}_{f}") for f in ("east", "south", "north")]
    cells += [load(f"{pre}{i}_east") for i in range(1, min(n, 5)+1)] if pre else []
    rows.append((dn, plan, cells))
    for fc in ("east", "south", "north"):
        m = bodylock(pre, n, fc) if pre else None
        if m: print(f"{dn:20s} {fc:5s} core-overlap {m[0]:.2f}  core RGB drift {m[1]:5.1f}/255  centroid drift {m[2]:4.1f}% of canvas")
W = 8
sheet = Image.new("RGBA", (180 + W*C, len(rows)*(C+18)), (60, 44, 32, 255))
d = ImageDraw.Draw(sheet)
for r, (dn, plan, cells) in enumerate(rows):
    y = r*(C+18)
    d.text((4, y+4), dn, fill="white"); d.text((4, y+18), plan, fill=(230, 200, 150))
    for c, im in enumerate(cells[:W]):
        x = 180 + c*C
        d.rectangle([x, y, x+C-2, y+C-2], fill=(120, 110, 100, 255))
        if im is not None:
            im = im.copy(); im.thumbnail((C-2, C-2)); sheet.alpha_composite(im, (x, y))
        lab = ["static E", "static S", "static N"][c] if c < 3 else f"fly {c-2} E"
        d.text((x+2, y+C+2), lab, fill="white")
out = pathlib.Path(__file__).with_name("sample_contact.png")
sheet.convert("RGB").save(out); print("wrote", out)
