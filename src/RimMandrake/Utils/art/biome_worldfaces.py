#!/usr/bin/env python3
"""Our own world-map biome faces (owner 2026-10-20: "simply generate the art for our own biome mods
rather than rely on world map enhanced"). Procedural, seamless, planet-scale-subtle faces built to the
spec in Transient/wme_analysis_2026-10-20.md section 6. No donor bytes: everything is periodic noise.

Spec, checked per file by `check`: 512x512 opaque RGB; seamless (wrap edge diff <= 2x interior neighbour
diff); mean per-channel sd 3-9; blockiness (std of the 8x8 grid of 64-px block means) <= 2.5; mean value
60-170 (ice/salt/bone up to 205); mean HSV saturation <= 60 %; water faces mean value <= 140 and cool.
Neighbour contrast: CIELAB distance between the mean colours of biomes that touch on the dev world record
(world/ASHKARR_WORLDMAP_tiles.csv) >= NEIGHBOUR_MIN_DE.

usage:
  python3 biome_worldfaces.py gen   [--out DIR]   write faces + sheet + 3x3 tiles + stats.json to DIR
  python3 biome_worldfaces.py check [--src]       stats on DIR (default) or on the installed files in src/
  python3 biome_worldfaces.py install [--dry-run] art-ledger install of every face (art.py install)
DIR defaults to <agent storage>/rimmandrake/scratch/biomeart.
Water faces only for RUT twins and mineral water: RM_GreySea/RM_TwilightSea/RM_TheScald point at vanilla
World/Biomes/Ocean and RM_TheChill at Jawa_SickWater (2026-10-20 audit) - those are left alone.
"""
import argparse, colorsys, json, os, subprocess, sys
import numpy as np
from PIL import Image, ImageDraw

N = 512
REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../../.."))
NEIGHBOUR_MIN_DE = 10.0
OWNER = "I would like us to simply generate the art for our own biome mods rather than rely on world map enhanced."

# key: (base, secondary, style, target_sd, seed, provisional, [ (mod, texname), ... ])
# Colours: the_*.md palette lines + Transient/biome_worldtex_2026-10-18/palette.json, muted to the spec.
U = "RimUtinni/UtinniPatches"
F = {
 "Stillsand":     ("#a88c5c", "#bba27a", "dunes",  4.0, 1, False, [("RimMandrake/Stillsand", "RM_Stillsand"), (U, "RUT_Stillsand")]),
 "LongShade":     ("#9a7a50", "#86705a", "dunes",  4.5, 2, False, [("RimMandrake/LongShade", "RM_LongShade"), (U, "RUT_LongShade")]),
 "LeaningScrub":  ("#8c8c66", "#9a8e5e", "crust",  6.0, 3, False, [("RimMandrake/LeaningScrub", "RM_LeaningScrub"), (U, "RUT_LeaningScrub")]),
 "Wasteland":     ("#9a9282", "#b2ad9e", "salt",   5.0, 4, False, [("RimMandrake/Wasteland", "RM_Wasteland"), (U, "RUT_Wasteland")]),
 "SleepingIce":   ("#b4b9c0", "#9097a3", "ice",    4.5, 5, False, [("RimMandrake/NightsideIce", "RM_SleepingIce"), (U, "RUT_SleepingIce")]),
 "Umbra":         ("#4c5464", "#4e5e60", "ice",    4.0, 6, True,  [(U, "RUT_Umbra")]),
 "Abyss":         ("#43455a", "#4c5468", "crust",  5.0, 7, False, [("RimMandrake/Abyss", "RM_Abyss"), (U, "RUT_Abyss")]),
 "BlueDesert":    ("#6e86a2", "#8296ae", "dunes",  4.0, 8, False, [("RimMandrake/BlueDesert", "RM_BlueDesert"), (U, "RUT_BlueDesert")]),
 "CrackedLands":  ("#8a5240", "#96644e", "cracks", 7.0, 9, False, [("RimMandrake/CrackedLands", "RM_CrackedLands"), (U, "RUT_CrackedLands")]),
 "Cauldron":      ("#55574a", "#5e5a4e", "crust",  6.0, 10, False, [("RimMandrake/Cauldron", "RM_Cauldron"), (U, "RUT_Cauldron")]),
 "RustCathedral": ("#7c4e3a", "#6a4a3e", "crust",  7.0, 11, False, [("RimMandrake/RustCathedral", "RM_RustCathedral"), (U, "RUT_RustCathedral")]),
 "Greentide":     ("#5a7450", "#667c54", "canopy", 7.5, 12, False, [("RimMandrake/Greentide", "RM_Greentide"), (U, "RUT_Greentide")]),
 "WeepingStones": ("#a6a192", "#7e8478", "weep",   6.5, 13, False, [("RimMandrake/WeepingStones", "RM_WeepingStones"), (U, "RUT_WeepingStones")]),
 "Pyrelands":     ("#8e7a50", "#6e6454", "bands",  6.5, 14, False, [("RimMandrake/Pyrelands", "RM_Pyrelands")]),
 "Contagion":     ("#784048", "#865058", "crust",  6.5, 15, False, [("RimMandrake/Contagion", "RM_Contagion"), (U, "RUT_Contagion")]),
 "Webwork":       ("#42583f", "#5c6a58", "silk",   6.5, 16, False, [("RimMandrake/Webwork", "RM_Webwork"), (U, "RUT_Webwork")]),
 "Slime":         ("#78844a", "#8a8450", "crust",  6.5, 17, False, [("RimMandrake/GelatinousSlime", "RM_Slime"), (U, "RUT_Slime")]),
 "Miasma":        ("#746a3a", "#686238", "crust",  6.5, 18, False, [("RimMandrake/Miasma", "RM_Miasma"), (U, "RUT_Miasma")]),
 "Warscar":       ("#62524c", "#5a4a4c", "cracks", 7.5, 19, False, [("RimMandrake/Scarlands", "RM_Warscar"), (U, "RUT_Warscar")]),
 "Forge":         ("#524a4a", "#5e4a42", "veins",  7.5, 20, False, [("RimMandrake/TheForge", "RM_Forge"), (U, "RUT_Forge")]),
 "FeverWood":     ("#4e5a32", "#5a5c34", "canopy", 7.5, 21, False, [("RimMandrake/FeverWood", "RM_FeverWood"), (U, "RUT_FeverWood")]),
 "Sump":          ("#484640", "#55503e", "crust",  5.0, 22, False, [("RimMandrake/TheSump", "RM_Sump"), (U, "RUT_Sump")]),
 "TheRot":        ("#968aa0", "#a8a0a4", "crust",  5.5, 23, False, [("RimMandrake/TheRot", "RM_TheRot"), (U, "RUT_TheRot")]),
 "LanternDeeps":  ("#3c4660", "#46505a", "crust",  5.0, 24, True,  [("RimMandrake/LanternDeeps", "RM_LanternDeeps")]),
 "ChillCrater":   ("#42465a", "#3a4050", "ice",    4.5, 25, True,  [("RimMandrake/TerminalBiomes", "RM_ChillCrater")]),
 # sea-floor layer: land-style rock/sediment, no ripple (spec 6.4)
 "SeabedFloor":   ("#77745e", "#686656", "crust",  5.0, 31, True,  [("RimMandrake/DivingInteraction", "RM_SeabedFloor")]),
 "SeabedGrey":    ("#78706c", "#6a6668", "crust",  5.0, 32, True,  [("RimMandrake/DivingInteraction", "RM_SeabedGrey")]),
 "SeabedChill":   ("#46585a", "#3e4c54", "crust",  5.0, 33, True,  [("RimMandrake/DivingInteraction", "RM_SeabedChill")]),
 "SeabedScald":   ("#70503e", "#5e4a42", "crust",  5.0, 34, True,  [("RimMandrake/DivingInteraction", "RM_SeabedScald")]),
 "SeabedTwilight":("#584c56", "#4c4a50", "crust",  5.0, 35, True,  [("RimMandrake/DivingInteraction", "RM_SeabedTwilight")]),
 "SeabedBedrock": ("#535458", "#4a4a50", "cracks", 5.0, 36, True,  [("RimMandrake/DivingInteraction", "RM_SeabedBedrock")]),
 # water: colour + one-direction ripple only (spec 6.4)
 "GreySea":       ("#4b5f6e", "#5a6e7c", "water",  3.6, 41, False, [(U, "RUT_GreySea")]),
 "TwilightSea":   ("#284669", "#344f74", "water",  3.6, 42, False, [(U, "RUT_TwilightSea")]),
 "Scald":         ("#3c727a", "#4a8088", "water",  3.8, 43, False, [(U, "RUT_Scald")]),
 "Chill":         ("#2d415f", "#3a4e6a", "water",  3.4, 44, False, [(U, "RUT_Chill")]),
 "MineralWater":  ("#3e5e5a", "#4c6c64", "water",  3.6, 45, True,  [(U, "RUT_MineralWater")]),
}
WATER = {k for k, v in F.items() if v[2] == "water"}
BRIGHT_OK = {"SleepingIce", "Wasteland", "WeepingStones", "Stillsand"}   # ice / salt / bone: value cap 205
# dev-world record biome -> art key (live planet uses the RM_ twins; same art)
RECORD = {"RUT_ExtremeDesert": "Stillsand", "RUT_Umbra": "Umbra", "RUT_Desert": "LongShade", "RUT_TheRot": "TheRot",
          "RUT_Wasteland": "Wasteland", "RUT_NightsideIce": "SleepingIce", "RUT_BlueDesert": "BlueDesert",
          "RUT_CrackedLands": "CrackedLands", "RUT_AridShrubland": "LeaningScrub", "RUT_TwilightSea": "TwilightSea",
          "RUT_GreySea": "GreySea", "RUT_TheScald": "Scald", "RUT_RustCathedral": "RustCathedral",
          "RUT_Greentide": "Greentide", "RUT_WeepingStones": "WeepingStones", "RUT_Contagion": "Contagion",
          "RUT_Webwork": "Webwork", "RUT_Slime": "Slime", "RUT_Miasma": "Miasma", "RUT_Scarlands": "Warscar",
          "RUT_PropaneLake": "Chill", "RUT_TheForge": "Forge", "RUT_FeverWood": "FeverWood", "RUT_Sump": "Sump"}


def storage_root():
    r = subprocess.run([sys.executable, os.path.expanduser("~/dev/Lodestar/bin/lib/agent_storage.py")],
                       capture_output=True, text=True)
    if r.returncode != 0 or not r.stdout.strip():
        sys.exit("agent storage root unset (agent_storage.py failed): " + r.stderr.strip())
    return os.path.join(r.stdout.strip(), "rimmandrake", "scratch", "biomeart")


def H(c):
    c = c.lstrip("#"); return np.array([int(c[i:i + 2], 16) for i in (0, 2, 4)], float)


# ---------- periodic noise (everything wraps exactly at N) ----------
_FX = np.fft.fftfreq(N)[None, :] * N
_FY = np.fft.fftfreq(N)[:, None] * N


def band(lo, hi, seed, ax=1.0, ay=1.0):
    """Zero-mean unit-std periodic noise with energy between lo and hi cycles per texture.
    ax/ay < 1 stretch features along that axis (x = rows run horizontally)."""
    r = np.random.default_rng(seed).standard_normal((N, N))
    k = np.sqrt((_FX / ax) ** 2 + (_FY / ay) ** 2)
    filt = np.exp(-(k / hi) ** 2) * (1 - np.exp(-(k / max(lo, 1e-6)) ** 2))
    filt[0, 0] = 0
    o = np.real(np.fft.ifft2(np.fft.fft2(r) * filt))
    return (o - o.mean()) / (o.std() + 1e-9)


def warp(field, dx, dy):
    """Bilinear sample field at (x+dx, y+dy) with wrap: periodic if dx, dy are periodic."""
    yy, xx = np.mgrid[0:N, 0:N].astype(float)
    x = (xx + dx) % N; y = (yy + dy) % N
    x0 = np.floor(x).astype(int); y0 = np.floor(y).astype(int); fx = x - x0; fy = y - y0
    x1 = (x0 + 1) % N; y1 = (y0 + 1) % N
    return (field[y0, x0] * (1 - fx) * (1 - fy) + field[y0, x1] * fx * (1 - fy)
            + field[y1, x0] * (1 - fx) * fy + field[y1, x1] * fx * fy)


def warped(lo, hi, seed, amp=10.0, ax=1.0, ay=1.0):
    return warp(band(lo, hi, seed, ax, ay), band(2, 6, seed + 1) * amp, band(2, 6, seed + 2) * amp)


def emboss(h, light=(0.7, 0.7)):
    gx = (np.roll(h, -1, 1) - np.roll(h, 1, 1)) * 0.5
    gy = (np.roll(h, -1, 0) - np.roll(h, 1, 0)) * 0.5
    e = gx * light[0] + gy * light[1]
    return (e - e.mean()) / (e.std() + 1e-9)


def ridge(n, width=1.2):
    """Soft lines of ~width px along the zero contours of n: a continuous network, never isolated shapes.
    Distance to the contour is |n|/|grad n|, so the line keeps one width wherever it runs."""
    gx = (np.roll(n, -1, 1) - np.roll(n, 1, 1)) * 0.5; gy = (np.roll(n, -1, 0) - np.roll(n, 1, 0)) * 0.5
    d = np.abs(n) / (np.sqrt(gx * gx + gy * gy) + 1e-3)
    return np.exp(-(d / width) ** 2)


def z(a): return (a - a.mean()) / (a.std() + 1e-9)


# ---------- styles: return (mix weight 0..1 toward secondary, luminance detail zero-mean, extra)
def style_fields(style, s):
    mott = z(0.3 * band(2, 5, s) + 0.7 * warped(8, 22, s + 10, 3))          # colour patches 23-64 px
    w = np.clip(0.5 + 0.22 * mott, 0, 1)
    crust = z(warped(25, 80, s + 20, 3))                                      # 6-20 px crust/lichen
    fine = band(60, 170, s + 30)                                              # 3-8 px grain
    det = 0.45 * crust + 0.30 * emboss(crust) + 0.15 * fine + 0.20 * mott
    if style == "dunes":    # ripple striations ~11 px apart, gently warped, broken up in patches
        yy = np.mgrid[0:N, 0:N][0]
        ph = 2 * np.pi * (46 * yy / N) + band(3, 8, s + 40) * 1.6 + band(10, 24, s + 41) * 0.5
        rip = np.sin(ph) * np.clip(0.55 + 0.45 * band(4, 10, s + 42), 0, 1)
        det = 0.40 * rip + 0.30 * crust + 0.15 * fine + 0.20 * mott
    elif style == "cracks":  # fine dark crack network (cells ~40-70 px), 1-2 px soft lines
        cr = ridge(warped(5, 11, s + 50, 6), 1.1) + 0.5 * ridge(warped(11, 22, s + 51, 4), 0.8)
        det = 0.40 * crust + 0.25 * emboss(crust) + 0.15 * fine + 0.15 * mott - 0.55 * z(cr)
    elif style == "veins":   # basalt with faint warm seams drawn as a tint
        v = ridge(warped(5, 11, s + 50, 6), 1.3)
        det = 0.45 * crust + 0.30 * emboss(crust) + 0.15 * fine + 0.15 * mott - 0.25 * z(v)
        return w, z(det), ("veins", v)
    elif style == "salt":    # pale connected crust patches, not dots
        sp = np.clip(warped(10, 30, s + 60, 6) - 0.5, 0, None)
        det = 0.40 * crust + 0.25 * emboss(crust) + 0.15 * fine + 0.15 * mott + 0.45 * z(sp)
    elif style == "ice":     # faint grey crease lines over a smooth sheet
        cr = ridge(warped(4, 9, s + 70, 8), 0.9)
        det = 0.35 * crust + 0.30 * emboss(crust) + 0.10 * fine + 0.20 * mott - 0.40 * z(cr)
    elif style == "bands":   # Pyrelands: migrating ash bands, soft, stretched across x
        b = warped(2, 7, s + 80, 6, ax=0.35, ay=1.0)
        w = np.clip(0.5 + 0.12 * mott + 0.16 * b, 0, 1)
    elif style == "canopy":  # forest: clumped crown speckle 5-15 px
        cn = z(warped(35, 100, s + 90, 3))
        det = 0.45 * cn + 0.30 * emboss(cn) + 0.15 * crust + 0.20 * mott
    elif style == "weep":    # bone stone with short dark weep streaks running down
        st = z(np.clip(warped(14, 40, s + 100, 4, ax=1.0, ay=0.25), 0.8, None))
        det = 0.40 * crust + 0.25 * emboss(crust) + 0.15 * fine + 0.15 * mott - 0.40 * st
    elif style == "silk":    # dark green with pale elongated wisps, low amplitude
        wi = z(np.clip(warped(10, 30, s + 110, 8, ax=0.4, ay=1.0), 0.9, None))
        det = 0.40 * crust + 0.25 * emboss(crust) + 0.15 * fine + 0.15 * mott + 0.35 * wi
    elif style == "water":   # calm field, one-direction (x) wavelet streaks 15-40 px long, 2-4 px thick
        st = warped(12, 32, s + 120, 3, ax=0.25, ay=1.0)
        hi_ = np.clip(st - 1.2, 0, None)
        w = np.clip(0.5 + 0.15 * band(3, 8, s + 121) + 0.1 * z(st), 0, 1)
        det = 0.65 * z(st) + 0.25 * z(hi_) + 0.10 * band(60, 160, s + 122)
    return w, z(det), None


def make(key):
    base, sec, style, tsd, s, _p, _f = F[key]
    b = H(base); m = H(sec)
    w, det, extra = style_fields(style, s * 1000)
    img = b[None, None, :] * (1 - w[..., None]) + m[None, None, :] * w[..., None]
    lum = det[..., None] * (0.35 + 0.65 * img / max(img.mean(), 1))         # detail scales with brightness
    if extra and extra[0] == "veins":
        img = img + (H("#7a3a26") - b)[None, None, :] * (0.22 * extra[1])[..., None]
    # scale the detail so the per-channel sd hits the target
    lo, hi = 0.0, 40.0
    for _ in range(30):
        a = (lo + hi) / 2
        sd = (img + lum * a).reshape(-1, 3).std(0).mean()
        lo, hi = (a, hi) if sd < tsd else (lo, a)
    out = img + lum * ((lo + hi) / 2)
    out += (b - out.reshape(-1, 3).mean(0))[None, None, :] * 0.5
    return np.clip(np.rint(out), 0, 255).astype(np.uint8)


# ---------- statistics ----------
def stats(a):
    a = a.astype(float); n = a.shape[0]; b = n // 8
    bm = a.reshape(8, b, 8, b, 3).mean((1, 3))
    nbr = (np.abs(np.diff(a, axis=1)).mean() + np.abs(np.diff(a, axis=0)).mean()) / 2
    seam = (np.abs(a[:, 0] - a[:, -1]).mean() + np.abs(a[0] - a[-1]).mean()) / 2
    mean = a.reshape(-1, 3).mean(0)
    h, sat, val = colorsys.rgb_to_hsv(*(mean / 255))
    return {"mean": [int(round(x)) for x in mean], "sd": round(float(a.reshape(-1, 3).std(0).mean()), 2),
            "blk": round(float(bm.reshape(-1, 3).std(0).mean()), 2), "seam": round(float(seam), 2),
            "nbr": round(float(nbr), 2), "sat": round(sat * 100), "val": round(val * 255), "hue": round(h * 360)}


def verdict(key, st, shape):
    bad = []
    if shape != (N, N, 3): bad.append(f"shape {shape}")
    if not 3 <= st["sd"] <= 9: bad.append(f"sd {st['sd']}")
    if st["blk"] > 2.5: bad.append(f"blk {st['blk']}")
    if st["seam"] > 2 * st["nbr"] + 0.5: bad.append(f"seam {st['seam']} > 2x nbr {st['nbr']}")
    if st["sat"] > 60: bad.append(f"sat {st['sat']}%")
    vmax = 140 if key in WATER else (205 if key in BRIGHT_OK else 170)
    if not 60 <= st["val"] <= vmax: bad.append(f"val {st['val']} not in 60-{vmax}")
    if key in WATER and not (st["mean"][2] > st["mean"][0]): bad.append("water not cool")
    return bad


def lab(rgb):
    c = np.array(rgb, float) / 255
    c = np.where(c > 0.04045, ((c + 0.055) / 1.055) ** 2.4, c / 12.92)
    M = np.array([[0.4124, 0.3576, 0.1805], [0.2126, 0.7152, 0.0722], [0.0193, 0.1192, 0.9505]])
    x, y, zz = M @ c / np.array([0.95047, 1.0, 1.08883])
    f = lambda t: np.cbrt(t) if t > 0.008856 else 7.787 * t + 16 / 116
    return np.array([116 * f(y) - 16, 500 * (f(x) - f(y)), 200 * (f(y) - f(zz))])


def neighbour_pairs():
    import csv
    p = os.path.join(REPO, "world/ASHKARR_WORLDMAP_tiles.csv")
    rows = list(csv.DictReader(open(p)))
    lat = np.radians([float(r["lat"]) for r in rows]); lon = np.radians([float(r["lon"]) for r in rows])
    xyz = np.stack([np.cos(lat) * np.cos(lon), np.cos(lat) * np.sin(lon), np.sin(lat)], 1)
    bio = [RECORD.get(r["biome"]) for r in rows]
    sp = np.sqrt(4 * np.pi / len(rows) * 2 / np.sqrt(3)); cut = 1.35 * sp
    cell = {}
    keyc = np.floor(xyz / cut).astype(int)
    for i, k in enumerate(map(tuple, keyc)): cell.setdefault(k, []).append(i)
    pairs = {}
    for i, k in enumerate(map(tuple, keyc)):
        if bio[i] is None: continue
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                for dz in (-1, 0, 1):
                    for j in cell.get((k[0] + dx, k[1] + dy, k[2] + dz), ()):
                        if j <= i or bio[j] is None or bio[j] == bio[i]: continue
                        if np.sum((xyz[i] - xyz[j]) ** 2) < cut * cut:
                            pr = tuple(sorted((bio[i], bio[j]))); pairs[pr] = pairs.get(pr, 0) + 1
    return pairs


def check_dir(d, from_src=False):
    res = {}; fails = 0
    for k, v in F.items():
        if from_src:
            mod, name = v[6][0]; p = os.path.join(REPO, "src", mod, "Textures/World/Biomes", name + ".png")
        else:
            p = os.path.join(d, "tex", k + ".png")
        im = Image.open(p); a = np.asarray(im.convert("RGB")) if im.mode == "RGB" else None
        if a is None: res[k] = {"bad": [f"mode {im.mode}"]}; fails += 1; continue
        st = stats(a); st["bad"] = verdict(k, st, a.shape); fails += bool(st["bad"]); res[k] = st
        if from_src:   # every twin file must be byte-identical to the first
            ref = open(p, "rb").read()
            for mod, name in v[6][1:]:
                q = os.path.join(REPO, "src", mod, "Textures/World/Biomes", name + ".png")
                if open(q, "rb").read() != ref: st["bad"].append(f"twin {name} differs"); fails += 1
    pairs = neighbour_pairs(); nb = []
    for (a, b), n in sorted(pairs.items(), key=lambda t: -t[1]):
        if n < 5: continue
        if "mean" not in res[a] or "mean" not in res[b]:   # a face that failed to load as RGB: already counted, cannot be measured
            nb.append({"a": a, "b": b, "edges": n, "dE": None, "ok": False}); continue
        de = float(np.linalg.norm(lab(res[a]["mean"]) - lab(res[b]["mean"])))
        nb.append({"a": a, "b": b, "edges": n, "dE": round(de, 1), "ok": de >= NEIGHBOUR_MIN_DE})
    return res, nb, fails + sum(not x["ok"] for x in nb)


def gen(out):
    os.makedirs(os.path.join(out, "tex"), exist_ok=True); os.makedirs(os.path.join(out, "tile3x3"), exist_ok=True)
    for k in F:
        a = make(k); Image.fromarray(a, "RGB").save(os.path.join(out, "tex", k + ".png"), optimize=True)
        t = Image.new("RGB", (3 * N, 3 * N)); im = Image.fromarray(a, "RGB")
        for i in range(3):
            for j in range(3): t.paste(im, (i * N, j * N))
        t.resize((768, 768), Image.LANCZOS).save(os.path.join(out, "tile3x3", k + ".png"))
    # contact sheet: each face 3x3-tiled at 1/4 scale (planet-ish zoom) + full-res crop
    keys = list(F); cols = 6; cw, ch = 260, 290
    sh = Image.new("RGB", (cols * cw, ((len(keys) + cols - 1) // cols) * ch), (30, 28, 26)); d = ImageDraw.Draw(sh)
    for i, k in enumerate(keys):
        im = Image.open(os.path.join(out, "tex", k + ".png")); x, y = (i % cols) * cw + 6, (i // cols) * ch + 4
        small = im.resize((80, 80), Image.LANCZOS)
        for a_ in range(3):
            for b_ in range(3): sh.paste(small, (x + a_ * 80, y + 18 + b_ * 80))
        d.text((x, y), k + (" *" if F[k][5] else ""), fill=(235, 230, 220))
    sh.save(os.path.join(out, "sheet.png"))
    res, nb, fails = check_dir(out)
    json.dump({"faces": res, "neighbours": nb}, open(os.path.join(out, "stats.json"), "w"), indent=1)
    return res, nb, fails


def report(res, nb, fails):
    for k, st in res.items():
        if st.get("bad"): print("FAIL", k, st["bad"])
    sds = [v["sd"] for v in res.values() if "sd" in v]; blks = [v["blk"] for v in res.values() if "blk" in v]
    print(f"faces {len(res)}  sd {min(sds)}-{max(sds)}  blk max {max(blks)}  "
          f"neighbour pairs {len(nb)} (min dE {min((x['dE'] for x in nb if x['dE'] is not None), default='UNMEASURED')})  fails {fails}")
    for x in nb:
        if not x["ok"]: print("NEIGHBOUR", x)


def install(dry):
    out = storage_root(); bad = 0
    for k, v in F.items():
        src = os.path.join(out, "tex", k + ".png")
        stage = os.path.join(REPO, "Transient", "biome_worldfaces_stage", k + ".png")   # art.py wants a file inside the clone
        os.makedirs(os.path.dirname(stage), exist_ok=True); open(stage, "wb").write(open(src, "rb").read())
        for mod, name in v[6]:
            rel = f"World/Biomes/{name}.png"
            cmd = [sys.executable, os.path.join(REPO, "src/RimMandrake/Utils/art/art.py"), "install", mod, rel,
                   "--file", os.path.relpath(stage, REPO), "--owner-said", OWNER] + (["--dry-run"] if dry else [])
            x = subprocess.run(cmd, capture_output=True, text=True, cwd=REPO)
            o = (x.stdout + x.stderr).strip().splitlines(); bad += x.returncode != 0
            print(x.returncode, mod, rel, (o[-1] if o else "")[:110])
    print("install failures", bad); return bad


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("cmd", choices=["gen", "check", "install"])
    ap.add_argument("--out"); ap.add_argument("--src", action="store_true"); ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()
    if a.cmd == "gen":
        r = gen(a.out or storage_root()); report(*r); sys.exit(1 if r[2] else 0)
    if a.cmd == "check":
        r = check_dir(a.out or storage_root(), from_src=a.src); report(*r); sys.exit(1 if r[2] else 0)
    sys.exit(1 if install(a.dry_run) else 0)
