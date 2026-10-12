#!/usr/bin/env python3
"""Offline composite of the INSTALLED tap clamp, per look, on the cords the production builder actually lays.

Input is the SelfTest's dump (TapClampPoseChecks writes tapclamp_poses.json under --dump): every strand CordBuilder laid
around a tap, for each bitten-cord direction x side our cord comes from, plus the pose AerialMath.TapClampPose chose
(bite, AngleAxis angle). Nothing about the pose is recomputed here, so the picture shows what the game will draw.

    python3 src/RimMandrake/Utils/selftest_gimmesomeslack.py --no-export --dump /mnt/d/Luke/dev/_rmbuild/tapdump
    python3 .../render_tapclamp_poses.py /mnt/d/Luke/dev/_rmbuild/tapdump/tapclamp_poses.json <out.png>

Rows = looks (Scrapper / Industrial / Modern / Futuristic, each on its own strand texture); columns = poses
(their cord W/E/S/N x ours). Their cord is drawn in the look's strand, ours in the same look (as in game, a tap bites a
run of the same look only by chance; here the look under test is the point). Conduit cells tinted, machines dark.
"""
import json
import math
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

REPO = Path(__file__).resolve().parents[5]
TEX = REPO / "src/RimMandrake/GimmeSomeSlack/Textures/RimMandrake/GimmeSomeSlack"
CLAMP = {"Scrapper": "Aerial/TapClamp.png", "Industrial": "Aerial/Styles/Industrial/TapClamp.png",
         "Modern": "Aerial/Styles/Modern/TapClamp.png", "Futuristic": "Aerial/Styles/Futuristic/TapClamp.png"}
STRAND = {"Scrapper": "Strand_Jawa.png", "Industrial": "Styles/StarWars/Strand_BlackRubber.png",
          "Modern": "Styles/ExtCord/Strand_Orange.png", "Futuristic": "Styles/Cybertek/Strand.png"}
TAP_SIZE, STRAND_W, SHADOW_W, SHADOW_OFF = 1.5, 0.08, 0.13, (0.03, -0.045)
PPC, HALF = 96, 2.0        # px per cell; each tile shows the tap +-2 cells


def sand(w, h, seed=7):
    rng = np.random.default_rng(seed)
    n = rng.normal(0, 6, (h, w, 1))
    return Image.fromarray(np.clip(np.array([196, 170, 124], np.float32) + n, 0, 255).astype(np.uint8), "RGB").convert("RGBA")


def draw_strand(img, pts, look, to_px):
    """Lay the strand texture along the polyline: one rotated strip per segment (SectionLayer_RM_MessyCords ribbon)."""
    tex = Image.open(TEX / STRAND[look]).convert("RGBA")
    shadow = Image.open(TEX / "StrandShadow.png").convert("RGBA")
    for layer, w, off in ((shadow, SHADOW_W, SHADOW_OFF), (tex, STRAND_W, (0, 0))):
        wpx = max(2, round(w * PPC))
        for (ax, az), (bx, bz) in zip(pts, pts[1:]):
            ax, az, bx, bz = ax + off[0], az + off[1], bx + off[0], bz + off[1]
            L = math.hypot(bx - ax, bz - az)
            if L < 1e-6:
                continue
            lpx = max(1, round(L * PPC) + 2)
            strip = layer.resize((lpx, wpx), Image.BOX)
            ang = math.degrees(math.atan2(bz - az, bx - ax))         # world CCW from east = image CCW
            rs = strip.rotate(ang, expand=True, resample=Image.BICUBIC)
            cx, cy = to_px((ax + bx) / 2, (az + bz) / 2)
            img.alpha_composite(rs, (round(cx - rs.width / 2), round(cy - rs.height / 2)))


def tile(scene, look):
    S = round(2 * HALF * PPC)
    img = sand(S, S, seed="WESN".index(scene["their"]) * 4 + "WESN".index(scene["ours"]))
    tx, tz = scene["tap"]
    ox, oz = tx + 0.5 - HALF, tz + 0.5 - HALF

    def to_px(x, z):
        return (x - ox) * PPC, S - (z - oz) * PPC

    d = ImageDraw.Draw(img)
    for cx, cz in scene["conduits"]:
        x0, y1 = to_px(cx, cz)
        d.rectangle([x0, y1 - PPC, x0 + PPC, y1], fill=(150, 135, 105, 255))
    for mx, mz in scene["machines"]:
        x0, y1 = to_px(mx, mz)
        d.rectangle([x0 + 8, y1 - PPC + 8, x0 + PPC - 8, y1 - 8], fill=(70, 66, 60, 255))
    x0, y1 = to_px(tx, tz)
    d.rectangle([x0, y1 - PPC, x0 + PPC, y1], outline=(90, 80, 60, 255), width=1)
    for st in scene["strands"]:
        draw_strand(img, [tuple(p) for p in st["pts"]], look, to_px)
    spr = Image.open(TEX / CLAMP[look]).convert("RGBA")
    dpx = round(TAP_SIZE * PPC)
    spr = spr.resize((dpx, dpx), Image.LANCZOS).rotate(-scene["angle"], expand=False, resample=Image.BICUBIC)
    bx, by = to_px(*scene["bite"])
    img.alpha_composite(spr, (round(bx - dpx / 2), round(by - dpx / 2)))
    d = ImageDraw.Draw(img)
    d.text((4, 3), f"theirs {scene['their']}  ours {scene['ours']}  {scene['angle']:+.0f}deg", fill=(40, 30, 20, 255))
    return img


def main(dump, out):
    scenes = json.load(open(dump))
    # one column per their-direction, two our-sides each (straight through + one perpendicular)
    pick = []
    opp = {"W": "E", "E": "W", "S": "N", "N": "S"}
    perp = {"W": "N", "E": "S", "S": "E", "N": "W"}
    for t in ("W", "E", "S", "N"):
        for o in (opp[t], perp[t]):
            pick += [s for s in scenes if s["their"] == t and s["ours"] == o]
    looks = list(CLAMP)
    S = round(2 * HALF * PPC)
    sheet = Image.new("RGBA", (S * len(pick) + 4 * (len(pick) - 1), S * len(looks) + 4 * (len(looks) - 1)), (30, 26, 22, 255))
    for r, look in enumerate(looks):
        for c, sc in enumerate(pick):
            sheet.alpha_composite(tile(sc, look), (c * (S + 4), r * (S + 4)))
    sheet.convert("RGB").save(out)
    print(f"{out}: {len(looks)} looks x {len(pick)} poses at {PPC} px/cell")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
