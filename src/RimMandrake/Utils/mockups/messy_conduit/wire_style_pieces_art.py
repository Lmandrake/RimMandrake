"""wire_style_pieces_art.py -- per-build-style art for MessyConduit's non-cable pieces (Stage 4 art fill, 2026-10-04).

    python3 src/RimMandrake/Utils/mockups/messy_conduit/wire_style_pieces_art.py [--dry] [--only Look/Slot ...]

Design: design/RimMandrake/messyconduit_style_per_build_design.md sec. 4. Report: Transient/mc_style_art_report.md.

Sources: Codex $imagegen EDITS of the shipped Scrapper piece (same pose/framing, new materials), conformed onto the Scrapper
piece's canvas with skills/generating-rimworld-sprites/scripts/conform_sprite.py (strips: band crop + wrap crossfade),
validated with validate_sprite.py. Conformed candidates live outside git at
D:\\Luke\\dev\\_rmscratch\\mc_style_art\\conformed\\<Look>\\<Slot>.png; every installed byte is archived in the art store.

Naming scheme (the rule the code reads; Look = Industrial | Modern | Futuristic, Scrapper = the existing root files):
  a piece shipped at  <folder>/<Name>.png  has its style version at  <folder>/Styles/<Look>/<Name>.png
  (the Aerial rule, AerialMaterials.AerialStyleDir, generalised), so:
    Styles/<Look>/PowerSwitch.png, Styles/<Look>/PowerSwitch_Off.png      128x128
    Aerial/Styles/<Look>/TapClamp.png                                     128x128
    Hose/Styles/<Look>/Reel_PumpHookup.png (stored), Reel_Deployed.png (laid, empty drum)   256x256, the 2x2 reel
    Hose/Styles/<Look>/Strand_Flat.png, Strand_Plump.png                  256x64, tile along u
    Hose/Styles/<Look>/Binding.png 82x40, Coupling_Bare.png, Nozzle_Bare.png, EndCap_Bare.png 128x128, Mouth.png 64x64
  Cable decal slots keep CordMaterials' family folders (StarWars = Industrial, ExtCord = Modern, Cybertek = Futuristic):
    Styles/<Family>/EndFrayed_Live.png 64x64;  Styles/ExtCord/PowerStrip_Off.png 64x32 (Modern only)
Derived deterministically here, never generated: PowerSwitch_Off (centre lamp darkened) and PowerStrip_Off (LED off).
"""
import colorsys
import os
import sys

import numpy as np
from PIL import Image

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "art"))
import artledger  # noqa: E402  the only sanctioned writer into Textures

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", "..", "..", ".."))
TEX = os.path.join(REPO, "src", "RimMandrake", "MessyConduit", "Textures", "RimMandrake", "MessyConduit")
CONF = "/mnt/d/Luke/dev/_rmscratch/mc_style_art/conformed"
REASON = "script:src/RimMandrake/Utils/mockups/messy_conduit/wire_style_pieces_art.py"
LOOKS = ("Industrial", "Modern", "Futuristic")
FAMILY = {"Industrial": "StarWars", "Modern": "ExtCord", "Futuristic": "Cybertek"}
DEST = {"PowerSwitch": "Styles/{L}/PowerSwitch.png", "TapClamp": "Aerial/Styles/{L}/TapClamp.png",
        "EndFrayed_Live": "Styles/{F}/EndFrayed_Live.png"}
for _s in ("Reel_PumpHookup", "Reel_Deployed", "Strand_Flat", "Strand_Plump", "Binding", "Coupling_Bare",
           "Nozzle_Bare", "EndCap_Bare", "Mouth"):
    DEST[_s] = "Hose/Styles/{L}/" + _s + ".png"


def switch_off(im):
    """Darken the centre lamp: lit (bright or saturated) pixels within 26 px of the lamp centre (64,60 on the 128 canvas,
    measured as the On/Off difference of the shipped Scrapper pair) go to a dark desaturated grey."""
    a = np.asarray(im.convert("RGBA")).astype(np.float32)
    h, w = a.shape[:2]
    cy, cx, r = 60 * h / 128, 64 * w / 128, 26 * w / 128
    yy, xx = np.mgrid[0:h, 0:w]
    inside = (yy - cy) ** 2 + (xx - cx) ** 2 <= r * r
    rgb = a[..., :3] / 255.0
    mx, mn = rgb.max(2), rgb.min(2)
    sat = np.where(mx > 0, (mx - mn) / np.maximum(mx, 1e-6), 0)
    lum = rgb @ np.array([0.299, 0.587, 0.114])
    lit = inside & (a[..., 3] > 0) & ((lum > 0.55) | (sat > 0.45))
    grey = (lum * 0.28 + 0.06)[..., None] * np.array([1.0, 1.0, 1.05])
    a[..., :3] = np.where(lit[..., None], grey * 255, a[..., :3])
    return Image.fromarray(a.clip(0, 255).astype(np.uint8)), int(lit.sum())


def strip_off(im):
    """Power strip with its LED off: warm (orange) pixels in the LED corner become the housing's dark grey."""
    a = np.asarray(im.convert("RGBA")).astype(np.float32)
    n = 0
    for y in range(a.shape[0]):
        for x in range(44, a.shape[1]):
            r_, g_, b_, al = a[y, x]
            if al > 0 and r_ - b_ > 40 and r_ > 90:
                v = 0.30 * r_ + 0.59 * g_ + 0.11 * b_
                a[y, x, :3] = (v * 0.25 + 30, v * 0.25 + 30, v * 0.25 + 33)
                n += 1
    return Image.fromarray(a.clip(0, 255).astype(np.uint8)), n


def plan():
    """[(dest rel under TEX, PIL image or None, note)] for every candidate present on disk."""
    out = []
    for L in LOOKS:
        for slot, pat in DEST.items():
            src = os.path.join(CONF, L, slot + ".png")
            if not os.path.isfile(src):
                continue
            im = Image.open(src).convert("RGBA")
            rel = pat.format(L=L, F=FAMILY[L])
            out.append((rel, im, src))
            if slot == "PowerSwitch":
                off, n = switch_off(im)
                out.append((rel.replace("PowerSwitch.png", "PowerSwitch_Off.png"), off, "derived lamp-off %d px" % n))
    strip, n = strip_off(Image.open(os.path.join(TEX, "PowerStrip.png")))
    out.append(("Styles/ExtCord/PowerStrip_Off.png", strip, "derived LED-off %d px from PowerStrip.png" % n))
    return out


def main(argv):
    only = argv[argv.index("--only") + 1:] if "--only" in argv else None
    for rel, im, note in plan():
        if only and not any(o in rel for o in only):
            continue
        dest = os.path.join(TEX, rel)
        if "--dry" in argv:
            print("would install", rel, im.size, note)
            continue
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        r = artledger.install_image(dest, im, reason=REASON)
        print(r.get("status"), rel, im.size)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
