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
Since 2026-10-24 the Grey Sea and Twilight Sea faces (both twins) come from world_water_variants.py (owner picks,
WORLD_SEA_FACES_INSTALL_PICKED_LOOKS); `install` skips them (PICKED_ELSEWHERE) so a rerun cannot revert his pick.
"""
import argparse, colorsys, json, os, subprocess, sys
import numpy as np
from PIL import Image, ImageDraw

N = 512
REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../../.."))
NEIGHBOUR_MIN_DE = 10.0
SWIRL_OWNER = ("Abyss I had envisioned as far darker still with eerie swirling within it. The Rot should have a lot more "
               "texture and swirls of wild colors.")
OWNER = "I would like us to simply generate the art for our own biome mods rather than rely on world map enhanced."

# key: (base, secondary, style, target_sd, seed, provisional, [ (mod, texname), ... ])
# Colours: the_*.md palette lines + Transient/biome_worldtex_2026-10-18/palette.json, muted to the spec.
U = "RimUtinni/UtinniPatches"
F = {
 "Stillsand":     ("#a88c5c", "#bba27a", "dunes",  4.0, 1, False, [("RimMandrake/Stillsand", "RM_Stillsand"), (U, "RUT_Stillsand")]),
 "LongShade":     ("#9a7a50", "#86705a", "dunes",  4.5, 2, False, [("RimMandrake/LongShade", "RM_LongShade"), (U, "RUT_LongShade")]),
 "LeaningScrub":  ("#8c8c66", "#9a8e5e", "crust",  6.0, 3, False, [("RimMandrake/LeaningScrub", "RM_LeaningScrub"), (U, "RUT_LeaningScrub")]),
 "Wasteland":     ("#9a9282", "#b2ad9e", "salt",   5.0, 4, False, [("RimMandrake/Wastes", "RM_Wastes"), (U, "RUT_Wastes")]),
 "SleepingIce":   ("#b4b9c0", "#9097a3", "ice",    4.5, 5, False, [("RimMandrake/SleepingIce", "RM_SleepingIce"), (U, "RUT_SleepingIce")]),
 "Umbra":         ("#4c5464", "#4e5e60", "ice",    4.0, 6, True,  [(U, "RUT_Umbra")]),
 "Abyss":         ("#15151d", "#1c2130", "abyss", 5.0, 7, False, [("RimMandrake/Abyss", "RM_Abyss"), (U, "RUT_Abyss")]),
 "BlueDesert":    ("#6e86a2", "#8296ae", "dunes",  4.0, 8, False, [("RimMandrake/BlueDesert", "RM_BlueDesert"), (U, "RUT_BlueDesert")]),
 "CrackedLands":  ("#8a5240", "#96644e", "cracks", 7.0, 9, False, [("RimMandrake/CrackedLands", "RM_CrackedLands"), (U, "RUT_CrackedLands")]),
 "Cauldron":      ("#55574a", "#5e5a4e", "crust",  6.0, 10, False, [("RimMandrake/Cauldron", "RM_Cauldron"), (U, "RUT_Cauldron")]),
 "RustCathedral": ("#6e3c28", "#3e2a22", "machinery", 15.0, 11, False, [("RimMandrake/RustCathedral", "RM_RustCathedral"), (U, "RUT_RustCathedral")]),
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
 "TheRot":        ("#5e4a6a", "#6a4058", "rot",    13.0, 23, False, [("RimMandrake/TheRot", "RM_TheRot"), (U, "RUT_TheRot")]),
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
          "RUT_Wastes": "Wasteland", "RUT_SleepingIce": "SleepingIce", "RUT_BlueDesert": "BlueDesert",
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


# Calm pass (2026-10-20, STIPPLE research): the "crust" family carried 1-4 px grain (emboss + fine bands) that a minified
# texture turns into sparkle at mid zoom. These faces get their detail low-passed (Gaussian sigma in px, periodic) and
# then re-scaled to the same sd, so colour, mean and neighbour contrast are untouched; only the <=5 px grain is gone.
CALM = {"Forge": 3.0, "Greentide": 3.0, "Warscar": 3.0, "Miasma": 3.0, "FeverWood": 3.0,
        "Cauldron": 2.6, "CrackedLands": 2.6, "Slime": 2.6, "LeaningScrub": 2.6, "Pyrelands": 2.6, "Contagion": 2.6,
        "Sump": 2.2}
CALM_SD = 0.65      # and their total sd is cut to this fraction (floor CALM_SD_MIN, the spec's lower bound + margin)
CALM_SD_MIN = 3.6


def gblur(a, sigma):
    k = np.sqrt(_FX ** 2 + _FY ** 2) / N          # cycles per pixel
    return np.real(np.fft.ifft2(np.fft.fft2(a) * np.exp(-2 * (np.pi * sigma) ** 2 * k ** 2)))


# Owner say-so overrides of the calm spec (2026-10-20, WORLD_FACES_REDRAW_ABYSS_ROT_RUST): "Abyss I had envisioned as far
# darker still with eerie swirling within it. The Rot should have a lot more texture and swirls of wild colors. ... I
# really liked the harsh rusty machinery". These three are judged by these bounds instead of the spec's.
OVERRIDE = {"Abyss": {"val": (14, 45), "sd": (2, 9)},
            "TheRot": {"sd": (8, 18), "sat": 75, "blk": 6.0},
            "RustCathedral": {"sd": (10, 20), "sat": 72, "blk": 6.0}}


def curl_lic(seed, lo, hi, steps=14, h=1.6, vlo=1.2, vhi=3.5, vamp=60.0):
    """Swirls: periodic noise smeared along the streamlines of a periodic curl field (a line-integral convolution).
    psi's extrema become eddies; streaks run around them. Wraps exactly at N."""
    psi = band(vlo, vhi, seed) * vamp
    vx = (np.roll(psi, -1, 0) - np.roll(psi, 1, 0)) * 0.5
    vy = -(np.roll(psi, -1, 1) - np.roll(psi, 1, 1)) * 0.5
    sp = np.sqrt(vx * vx + vy * vy) + 1e-6
    vx, vy = vx / sp * h, vy / sp * h
    f0 = band(lo, hi, seed + 1)
    acc = f0.copy(); fa = f0; fb = f0
    for i in range(1, steps + 1):
        fa = warp(fa, vx, vy); fb = warp(fb, -vx, -vy)
        wgt = 1.0 - i / (steps + 1)
        acc += wgt * (fa + fb)
    return z(acc), psi


def style_abyss(base, sec, s):
    """Near-black basin floor; a faint cold swirl in the face itself (the overlay carries the bold one)."""
    b = H(base); m = H(sec)
    lic, _ = curl_lic(s + 1, 18, 60, steps=12)
    mott = z(warped(3, 9, s + 2, 6))
    w = np.clip(0.5 + 0.25 * mott + 0.15 * lic, 0, 1)
    img = b * (1 - w[..., None]) + m * w[..., None]
    fil = ridge(lic, 1.6)
    img = img + H("#3a4a5e")[None, None, :] * (0.35 * fil)[..., None] * (0.5 + 0.5 * np.clip(mott, 0, None))[..., None]
    img = img + (gblur(z(warped(20, 60, s + 3, 3)), 1.2) * 1.6)[..., None]
    return img


WILD = ["#9a2ab0", "#d02a7a", "#7ac020", "#20a8a0", "#e09020", "#6a3ad0", "#c03030", "#30a050"]


def wild_colour(t):
    """t in [0,1) -> a cyclic walk through the wild palette, smooth."""
    pal = np.array([H(c) for c in WILD]); n = len(pal)
    x = (t % 1.0) * n; i0 = np.floor(x).astype(int) % n; i1 = (i0 + 1) % n; f = (x - np.floor(x))[..., None]
    f = f * f * (3 - 2 * f)
    return pal[i0] * (1 - f) + pal[i1] * f


def style_rot(base, sec, s):
    """Rich, lumpy rot: crust and pustule relief, and swirled pools of wild colour bleeding through a bruised base."""
    b = H(base); m = H(sec)
    lic, _ = curl_lic(s + 1, 10, 30, steps=10, vlo=2, vhi=6)
    hue = 0.5 + 0.18 * z(warped(2, 5, s + 2, 8)) + 0.10 * lic
    col = wild_colour(hue)
    mott = z(warped(4, 12, s + 3, 5))
    w = np.clip(0.5 + 0.3 * mott, 0, 1)
    img = b * (1 - w[..., None]) + m * w[..., None]
    pool = np.clip(0.45 + 0.35 * z(warped(3, 10, s + 4, 10)) + 0.2 * lic, 0, 1)[..., None]
    img = img * (1 - 0.7 * pool) + col * 0.7 * pool
    crust = gblur(z(warped(20, 55, s + 5, 4)), 1.0)
    pus = gblur(np.clip(z(warped(14, 34, s + 6, 3)) - 1.3, 0, None), 1.0)
    relief = 0.55 * emboss(crust) + 0.35 * crust + 0.5 * z(pus) + 0.25 * emboss(pus)
    return img + (z(relief) * 1.0)[..., None]


def _disc(hmap, cx, cy, r, val, teeth=0):
    yy, xx = np.mgrid[0:N, 0:N]
    dx = (xx - cx + N / 2) % N - N / 2; dy = (yy - cy + N / 2) % N - N / 2
    d = np.sqrt(dx * dx + dy * dy); ang = np.arctan2(dy, dx)
    rr = r + (np.clip(np.sin(ang * teeth) * 3, -1, 1) * 2.5 if teeth else 0)
    gear = d < rr
    hmap[gear] = np.maximum(hmap[gear], val)
    hmap[(d < r * 0.62) & (d > r * 0.45)] -= 0.5      # sunken ring
    hmap[d < r * 0.22] = val + 0.6                     # hub
    return hmap


def style_machinery(base, sec, s):
    """Bold harsh rusty machinery at planet scale: riveted plate fields with dark seams, heavy pipe runs with collars,
    geared drums, and rust weeping down from them. Feature scale 6-80 px, no grain under ~3 px (calmer than 0f01bd5f7)."""
    r = np.random.default_rng(s)
    hm = np.zeros((N, N))
    # plate field: bands of plates, each its own height, seams between
    ys = np.sort(r.choice(np.arange(0, N, 8), 7, replace=False))
    for bi in range(len(ys)):
        y0, y1 = ys[bi], ys[(bi + 1) % len(ys)] + (N if bi == len(ys) - 1 else 0)
        xs = np.sort(r.choice(np.arange(0, N, 8), r.integers(3, 7), replace=False))
        for xi in range(len(xs)):
            x0, x1 = xs[xi], xs[(xi + 1) % len(xs)] + (N if xi == len(xs) - 1 else 0)
            lv = r.uniform(-0.6, 0.8)
            yr = np.arange(y0, y1) % N; xr = np.arange(x0, x1) % N
            hm[np.ix_(yr, xr)] = lv
            hm[np.ix_(yr, xr[:3])] = -1.4; hm[np.ix_(yr[:3], xr)] = -1.4     # seams
    # pipes: full-length runs (seamless by construction), cylinder profile, collars
    pipe_tint = np.zeros((N, N))
    for k in range(4):
        horiz = k % 2 == 0; c = r.integers(0, N); wdt = r.integers(5, 11)
        prof = np.zeros(N); idx = (np.arange(-wdt, wdt + 1) + c) % N
        prof[idx] = 1.6 + 1.2 * np.sqrt(np.clip(1 - (np.arange(-wdt, wdt + 1) / (wdt + 0.5)) ** 2, 0, 1))
        coll = np.zeros(N); step = r.integers(48, 96); off = r.integers(0, step)
        for q in range(off, N, step): coll[np.arange(q, q + 6) % N] = 0.7
        P = (prof[:, None] * (1 + 0)) if horiz else prof[None, :]
        C = coll[None, :] if horiz else coll[:, None]
        P = np.broadcast_to(P, (N, N)); C = np.broadcast_to(C, (N, N))
        mask = P > 0
        hm = np.where(mask, np.maximum(hm, P + C * mask), hm)
        pipe_tint = np.where(mask, 1.0 if k in (1, 4) else 0.5, pipe_tint)
    # geared drums
    for k in range(5):
        hm = _disc(hm, r.integers(0, N), r.integers(0, N), r.integers(18, 40), 2.4, teeth=r.integers(10, 18))
    hm = gblur(hm, 1.3)
    shade = emboss(hm, (0.6, 0.8))
    occl = z(gblur(hm, 6.0) - hm)                                   # crevices dark
    rust = z(warped(3, 10, s + 5, 8)); ox = z(warped(10, 30, s + 6, 4))
    weep = gblur(np.clip(warped(16, 40, s + 7, 3, ax=1.0, ay=0.12), 0.9, None), 1.0)
    dark, mid, light, iron = H("#2a170f"), H(base), H("#c06a34"), H("#4e3c36")
    t = np.clip(0.52 + 0.32 * shade - 0.28 * occl + 0.08 * rust - 0.10 * z(weep), 0, 1)[..., None]
    img = np.where(t < 0.55, dark * (1 - t / 0.55) + mid * (t / 0.55), mid * (1 - (t - 0.55) / 0.45) + light * ((t - 0.55) / 0.45))
    img = img * (1 - 0.45 * pipe_tint[..., None] * (pipe_tint[..., None] > 0.9)) + iron * 0.45 * pipe_tint[..., None] * (pipe_tint[..., None] > 0.9)
    img = img + (H(sec) - H(base))[None, None, :] * np.clip(0.35 * ox, 0, 1)[..., None]
    return img


# Biome-wide swirl overlays (RM_WorldLook.BuildSwirls draws World/RM_Swirls/<key> over every tile of the biome, UVs
# continuous across it). RGBA: the alpha IS the swirl. Shipped in TerminalBiomes beside RM_Hills.
SWIRL_MOD = "RimMandrake/TerminalBiomes"
SWIRL_REL = "World/RM_Swirls/{}.png"


def swirl_abyss(seed):
    """Eerie pale currents over the near-black Abyss: thin rim-lit filaments wound round slow eddies, a faint cold glow."""
    lic, psi = curl_lic(seed, 3, 9, steps=28, h=2.2, vlo=0.8, vhi=2.0)
    # streamlines: contours of the stream function wind round its extrema as nested whirlpool rings; the LIC term
    # wobbles them so they read as currents, not a contour plot
    sl = np.sin(z(psi) * 7.0 + 0.8 * lic)
    fil = ridge(sl, 1.7) * np.clip(0.4 + 0.6 * (0.5 + 0.5 * lic), 0, 1)
    gate = np.clip(0.35 + 0.65 * z(warped(1.2, 3, seed + 7, 20)), 0, 1) ** 1.5   # currents come and go, in patches
    glow = gblur(fil, 5.0)
    a = np.clip(0.50 * fil * gate + 0.30 * (glow / (glow.max() + 1e-9)) * gate, 0, 0.6)
    tint = np.clip(0.5 + 0.5 * z(warped(2, 5, seed + 8, 10)), 0, 1)[..., None]
    rgb = H("#9fc4d8") * (1 - tint) + H("#c8d2ff") * tint
    return rgb, a


def swirl_rot(seed):
    """Wild-coloured swirls over The Rot: broad marbled bands whose hue walks the wild palette, with brighter edges."""
    lic, psi = curl_lic(seed, 4, 14, steps=18, h=2.0, vlo=1.2, vhi=3.2)
    bands = 0.5 + 0.5 * np.sin(lic * 2.2)
    hue = 0.5 + 0.30 * z(warped(1.5, 4, seed + 3, 16)) + 0.12 * lic
    rgb = np.clip(wild_colour(hue) * 1.15, 0, 255)
    edge = ridge(z(np.sin(lic * 2.2)), 2.0)
    rgb = rgb * (1 - 0.35 * edge[..., None]) + H("#f0d8ff") * 0.35 * edge[..., None]
    gate = np.clip(0.6 + 0.4 * z(warped(1.5, 4, seed + 9, 20)), 0, 1)
    a = np.clip((0.22 + 0.55 * bands ** 2 + 0.3 * edge) * gate, 0, 0.9)
    return rgb, a


SWIRLS = {"Abyss": (swirl_abyss, 7001), "TheRot": (swirl_rot, 23001)}


def make_swirl(key):
    fn, seed = SWIRLS[key]
    rgb, a = fn(seed)
    out = np.dstack([np.clip(np.rint(rgb), 0, 255), np.clip(np.rint(a * 255), 0, 255)]).astype(np.uint8)
    return out


CUSTOM = {"abyss": style_abyss, "rot": style_rot, "machinery": style_machinery}


def make(key):
    base, sec, style, tsd, s, _p, _f = F[key]
    if style in CUSTOM:
        img = CUSTOM[style](base, sec, s * 1000)
        mean = img.reshape(-1, 3).mean(0); dev = img - mean
        a = tsd / max(dev.reshape(-1, 3).std(0).mean(), 1e-6)
        out = mean * 0.5 + H(base) * 0.5 + dev * a
        return np.clip(np.rint(out), 0, 255).astype(np.uint8)
    b = H(base); m = H(sec)
    w, det, extra = style_fields(style, s * 1000)
    if key in CALM:
        det = z(gblur(det, CALM[key]))
        if extra: extra = (extra[0], gblur(extra[1], CALM[key]))
        tsd = max(CALM_SD_MIN, tsd * CALM_SD)
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
    bad = []; o = OVERRIDE.get(key, {})
    if shape != (N, N, 3): bad.append(f"shape {shape}")
    sdlo, sdhi = o.get("sd", (3, 9))
    if not sdlo <= st["sd"] <= sdhi: bad.append(f"sd {st['sd']}")
    if st["blk"] > o.get("blk", 2.5): bad.append(f"blk {st['blk']}")
    if st["seam"] > 2 * st["nbr"] + 0.5: bad.append(f"seam {st['seam']} > 2x nbr {st['nbr']}")
    if st["sat"] > o.get("sat", 60): bad.append(f"sat {st['sat']}%")
    vmin, vmax = o.get("val", (60, 140 if key in WATER else (205 if key in BRIGHT_OK else 170)))
    if not vmin <= st["val"] <= vmax: bad.append(f"val {st['val']} not in {vmin}-{vmax}")
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
        a = make(k); Image.fromarray(a).save(os.path.join(out, "tex", k + ".png"), optimize=True)
        t = Image.new("RGB", (3 * N, 3 * N)); im = Image.fromarray(a)
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
    os.makedirs(os.path.join(out, "swirls"), exist_ok=True)
    for k in SWIRLS:
        sw = make_swirl(k); Image.fromarray(sw, "RGBA").save(os.path.join(out, "swirls", k + ".png"), optimize=True)
        face = Image.open(os.path.join(out, "tex", k + ".png")).convert("RGBA")
        comp = Image.alpha_composite(face, Image.fromarray(sw, "RGBA"))
        t = Image.new("RGB", (3 * N, 3 * N))
        for i in range(3):
            for j in range(3): t.paste(comp.convert("RGB"), (i * N, j * N))
        t.resize((768, 768), Image.LANCZOS).save(os.path.join(out, "tile3x3", k + "_swirl.png"))
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


PICKED_ELSEWHERE = {"GreySea", "TwilightSea"}   # faces owned by world_water_variants.py (owner picks 2026-10-24)


def install(dry, only=None):
    out = storage_root(); bad = 0
    for k, v in F.items():
        if only and k not in only: continue
        if k in PICKED_ELSEWHERE:
            print("skip", k, "- face owned by world_water_variants.py (owner pick)"); continue
        os.makedirs(os.path.join(REPO, "Transient", "biome_worldfaces_stage"), exist_ok=True)
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
    for k in SWIRLS:
        src = os.path.join(out, "swirls", k + ".png")
        stage = os.path.join(REPO, "Transient", "biome_worldfaces_stage", "swirl_" + k + ".png")
        open(stage, "wb").write(open(src, "rb").read())
        cmd = [sys.executable, os.path.join(REPO, "src/RimMandrake/Utils/art/art.py"), "install", SWIRL_MOD, SWIRL_REL.format(k),
               "--file", os.path.relpath(stage, REPO), "--owner-said", SWIRL_OWNER] + (["--dry-run"] if dry else [])
        x = subprocess.run(cmd, capture_output=True, text=True, cwd=REPO)
        o = (x.stdout + x.stderr).strip().splitlines(); bad += x.returncode != 0
        print(x.returncode, SWIRL_MOD, SWIRL_REL.format(k), (o[-1] if o else "")[:110])
    print("install failures", bad); return bad


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("cmd", choices=["gen", "check", "install"])
    ap.add_argument("--out"); ap.add_argument("--src", action="store_true"); ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--only", help="install: comma-separated face keys (swirls always go)")
    a = ap.parse_args()
    if a.cmd == "gen":
        r = gen(a.out or storage_root()); report(*r); sys.exit(1 if r[2] else 0)
    if a.cmd == "check":
        r = check_dir(a.out or storage_root(), from_src=a.src); report(*r); sys.exit(1 if r[2] else 0)
    sys.exit(1 if install(a.dry_run, set(a.only.split(",")) if a.only else None) else 0)
