"""DRAWBRIDGE_CABLES_FIX_STOP_SHORT: offline before/after renders of a one-lane drawbridge's anchor ropes, lowered and raised,
per material (Timber, Steel) and look, in all four rotations. A mirror of the print path (Graphic.Print for the anchor,
Building_SuspensionAnchor.Print + RM_DrawbridgeArt.PrintBollards/PrintRopes, RM_DrawbridgeArt.DrawLeafUp + LeafMesh) and of
RM_DrawbridgeCableMath (Taut, Slack, ToUV, UVToWorld) over the measured fixture anchor_cable_art.json. "before" draws the
anchors and the raised leaf whole, as the game did; "after" draws them as the fix does. Deck squares use the plain deck tile
(context only, not the linked atlas).

    python3 src/RimMandrake/FlowWorks/art_source/Drawbridge/render_cables.py <out dir> [--look Scrapper]
"""
import json
import math
import os
import sys

import numpy as np
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
TEX = os.path.join(HERE, "..", "..", "Textures")
SB = os.environ.get("RM_ANCHOR_SB") or os.path.join(TEX, "RimMandrake", "FlowWorks", "SuspensionBridge")   # override: render candidate anchors
DB = os.path.join(TEX, "Things", "Building", "FlowWorks", "Drawbridge")
FIX = json.load(open(os.path.join(HERE, "anchor_cable_art.json")))
S = 96  # px per cell
DECK_OVERLAP, SLACK_REACH = 0.04, 0.9
_tex = {}


def tex(path):
    if path not in _tex:
        _tex[path] = np.asarray(Image.open(path).convert("RGBA")).astype(np.float32) / 255.0
    return _tex[path]


# ---- RM_DrawbridgeCableMath mirror ----
def ropes_of(look, mat, facing="east"):
    k = "%s/%s/%s" % (look, mat, facing)   # per facing: an upright bollard's attachment differs by facing (ANCHOR_BOLLARD)
    return FIX["anchors"][k]


def taut(r):
    out = [(r["attach"], r["end"], True)]
    if r["end"] < 1.0 + DECK_OVERLAP:
        out.append((max(r["attach"], r["end"] - r["thick"]), 1.0 + DECK_OVERLAP, False))
    return out


COIL_ASPECT, COIL_MARGIN, COIL_WIDE, COIL_WOBBLE = 0.55, 0.05, 0.15, 0.10
UPRIGHT_FOOT_NORTH = 0.27   # RM_DrawbridgeCableMath.UprightFootNorth: the post foot in every styled Timber/Steel _north picture


def slack(r, vertical, foot=-1.0, n=44):
    """RM_DrawbridgeCableMath.Slack: a loose coil flat on the ground (squashed in the screen's vertical), in front of an upright
    post's foot when the deck is up the screen, else ahead of the attachment; ends in a loose end pointing away from the deck."""
    s = 1.0 if r["lateral"] >= 0 else -1.0
    lat = abs(r["lateral"])
    along_room = max(0.06, (SLACK_REACH - r["attach"]) / 2)
    lat_room = (0.5 - 2 * COIL_MARGIN) / 2
    if vertical:
        rl = min(COIL_WIDE, lat_room)
        ra = min(COIL_ASPECT * rl, along_room)
    else:
        ra = max(min(COIL_WIDE, along_room), 0.15)
        rl = min(COIL_ASPECT * ra, lat_room)
    ca = max(foot - ra, ra + COIL_MARGIN) if foot >= 0 else min(r["attach"] + ra, SLACK_REACH - ra)
    want = lat - 0.04 if vertical else lat
    cl = s * min(max(want, COIL_MARGIN + rl), 0.5 - COIL_MARGIN - rl)
    t0 = math.atan2((r["lateral"] - cl) / rl, (r["attach"] - ca) / ra)
    tail = s * (math.pi / 2 + (0.6 if vertical else 0.0))
    sweep = 2 * math.pi + (s * (t0 - tail)) % (2 * math.pi)
    pts = [(r["attach"], r["lateral"])]
    for i in range(n + 1):
        t = i / n
        th = t0 - s * t * sweep
        k = (1.0 - 0.45 * t) * (1.0 + COIL_WOBBLE * math.sin(5 * math.pi * t))
        pts.append((ca + k * ra * math.cos(th), cl + k * rl * math.sin(th)))
    for k in (0.95, 1.3):
        a = min(max(ca + k * ra * math.cos(tail), 0.02), min(SLACK_REACH, ca + ra))
        l = cl + k * rl * math.sin(tail)
        l = s * min(max(s * l, COIL_MARGIN), 0.5 - COIL_MARGIN)
        pts.append((a, l))
    return pts


def tex_dir(facing):
    return {"east": (1, 0), "south": (0, -1)}.get(facing, (0, 1))


def to_uv(facing, a, l):
    du, dv = tex_dir(facing)
    lu, lv = -dv, du
    return 0.5 + du * (a - 0.5) + lu * l, 0.5 + dv * (a - 0.5) + lv * l


def uv_to_world(u, v, flip, ang):
    qx = 0.5 - u if flip else u - 0.5
    qz = v - 0.5
    r = math.radians(ang)
    return qx * math.cos(r) + qz * math.sin(r), -qx * math.sin(r) + qz * math.cos(r)


# ---- a tiny quad rasteriser (world units, z up) ----
class Canvas:
    def __init__(self, x0, z0, x1, z1):
        self.x0, self.z1 = x0, z1
        self.w, self.h = int(round((x1 - x0) * S)), int(round((z1 - z0) * S))
        self.img = np.zeros((self.h, self.w, 4), np.float32)
        self.img[:, :] = (0.55, 0.45, 0.33, 1.0)

    def rect(self, x0, z0, x1, z1, rgba):
        a, b = int((x0 - self.x0) * S), int((self.z1 - z1) * S)
        c, d = int((x1 - self.x0) * S), int((self.z1 - z0) * S)
        self.img[max(0, b):d, max(0, a):c] = rgba

    def quad(self, center, size, rot, texarr, uvs):
        """PrintPlane: local corners (-x,-z),(-x,+z),(+x,+z),(+x,-z) take uvs[0..3]; turned clockwise by rot degrees."""
        cx, cz = center
        sx, sz = size
        r = math.radians(rot)
        X = np.array([math.cos(r), -math.sin(r)])   # local +x in world
        Z = np.array([math.sin(r), math.cos(r)])    # local +z in world
        corners = [np.array([cx, cz]) + X * (ex * sx) + Z * (ez * sz) for ex, ez in ((-.5, -.5), (-.5, .5), (.5, .5), (.5, -.5))]
        xs = [c[0] for c in corners]
        zs = [c[1] for c in corners]
        px0, px1 = int(math.floor((min(xs) - self.x0) * S)), int(math.ceil((max(xs) - self.x0) * S))
        py0, py1 = int(math.floor((self.z1 - max(zs)) * S)), int(math.ceil((self.z1 - min(zs)) * S))
        px0, py0 = max(px0, 0), max(py0, 0)
        px1, py1 = min(px1, self.w), min(py1, self.h)
        if px1 <= px0 or py1 <= py0:
            return
        gx, gy = np.meshgrid(np.arange(px0, px1) + 0.5, np.arange(py0, py1) + 0.5)
        wx = self.x0 + gx / S - cx
        wz = self.z1 - gy / S - cz
        lx = (wx * X[0] + wz * X[1]) / sx + 0.5   # 0..1 across
        lz = (wx * Z[0] + wz * Z[1]) / sz + 0.5   # 0..1 along
        inside = (lx >= 0) & (lx <= 1) & (lz >= 0) & (lz <= 1)
        # bilinear in the corner uvs: uv0 at (0,0), uv1 at (0,1), uv2 at (1,1), uv3 at (1,0)
        u = (1 - lx) * (1 - lz) * uvs[0][0] + (1 - lx) * lz * uvs[1][0] + lx * lz * uvs[2][0] + lx * (1 - lz) * uvs[3][0]
        v = (1 - lx) * (1 - lz) * uvs[0][1] + (1 - lx) * lz * uvs[1][1] + lx * lz * uvs[2][1] + lx * (1 - lz) * uvs[3][1]
        th, tw = texarr.shape[:2]
        ti = np.clip(((1 - v) * th).astype(int), 0, th - 1)
        tj = np.clip((u * tw).astype(int), 0, tw - 1)
        src = texarr[ti, tj]
        al = src[..., 3:4] * inside[..., None]
        dst = self.img[py0:py1, px0:px1]
        dst[..., :3] = src[..., :3] * al + dst[..., :3] * (1 - al)

    def save(self, path, label):
        im = Image.fromarray((np.clip(self.img, 0, 1) * 255).astype(np.uint8), "RGBA").convert("RGB")
        d = ImageDraw.Draw(im)
        d.rectangle((0, 0, len(label) * 7 + 8, 16), fill=(30, 30, 30))
        d.text((4, 2), label, fill=(255, 255, 255))
        im.save(path)


FULL_UV = [(0, 0), (0, 1), (1, 1), (1, 0)]
FLIP_UV = [(1, 0), (1, 1), (0, 1), (0, 0)]
CORNERS = [(-0.5, -0.5), (-0.5, 0.5), (0.5, 0.5), (0.5, -0.5)]
DIRS = {"N": (0, 1, 0), "E": (1, 0, 90), "S": (0, -1, 180), "W": (-1, 0, 270)}


def anchor_setup(look, mat, rot):
    """Graphic.Print of a styled anchor: the facing file, unturned; west = the east file mirrored."""
    facing = {"N": "north", "E": "east", "S": "south", "W": "east"}[rot]
    return facing, rot == "W", 0.0, tex(os.path.join(SB, look, "RM_SuspensionAnchor_%s_%s.png" % (mat, facing)))


def world(center, facing, flip, ang, a, l):
    x, z = uv_to_world(*to_uv(facing, a, l), flip, ang)
    return center[0] + x, center[1] + z


def hand(center, facing, flip, ang, fx, fz):
    p0 = world(center, facing, flip, ang, 0, 0)
    p1 = world(center, facing, flip, ang, 0, 1)
    lat = (p1[0] - p0[0], p1[1] - p0[1])
    return 1.0 if lat[0] * fz + lat[1] * (-fx) > 0 else -1.0


def rope_run(cv, t, r, facing, h, s, e, src, slack_on):
    lo, hi = r["attach"] + 0.01, r["end"] - 0.005
    dx, dz = e[0] - s[0], e[1] - s[1]
    ln = math.hypot(dx, dz)
    if ln < 1e-4:
        return src
    rot = math.degrees(math.atan2(dx, dz))
    pad = r["thick"] * 0.5
    done = 0.0
    while done < ln - 1e-4:
        if src < lo or src > hi - 0.02:
            src = lo
        piece = min(ln - done, hi - src)
        f = (done + piece / 2) / ln
        mid = (s[0] + dx * f, s[1] + dz * f)
        geo = piece + (pad if slack_on else 0.0)
        uvs = []
        for sx, sz in CORNERS:
            a = src + (sz + 0.5) * min(geo, hi - src)
            l = r["lateral"] + h * sx * r["thick"]
            uvs.append(to_uv(facing, a, l))
        cv.quad(mid, (r["thick"], geo), rot, t, uvs)
        done += piece
        src += piece
    return src


def draw_anchor(cv, center, look, mat, rot, raised, after):
    facing, flip, ang, t = anchor_setup(look, mat, rot)
    fx, fz, _ = DIRS[rot]
    ropes = ropes_of(look, mat, facing)
    if not after:
        cv.quad(center, (1, 1), ang, t, FLIP_UV if flip else FULL_UV)
        return
    h = hand(center, facing, flip, ang, fx, fz)
    if raised:   # PrintBollards: the picture up to the attachment point
        cut = min(r["attach"] for r in ropes)
        a0, a1 = 0.0, cut
        c = world(center, facing, flip, ang, (a0 + a1) / 2, 0)
        p0, p1 = world(center, facing, flip, ang, a0, 0), world(center, facing, flip, ang, a1, 0)
        rr = math.degrees(math.atan2(p1[0] - p0[0], p1[1] - p0[1]))
        uvs = [to_uv(facing, (a0 + a1) / 2 + sz * (a1 - a0), 0 + h * sx * 1.0) for sx, sz in CORNERS]
        cv.quad(c, (1.0, a1 - a0), rr, t, uvs)
    else:
        cv.quad(center, (1, 1), ang, t, FLIP_UV if flip else FULL_UV)
    for r in ropes:
        if raised:
            foot = UPRIGHT_FOOT_NORTH if facing == "north" and mat in ("Timber", "Steel") else -1.0   # SlackFoot
            pts = slack(r, fz != 0, foot)   # the coil lies flat in every rotation
            src = r["attach"] + 0.01
            for i in range(len(pts) - 1):
                src = rope_run(cv, t, r, facing, h, world(center, facing, flip, ang, *pts[i]), world(center, facing, flip, ang, *pts[i + 1]), src, True)
        else:
            for a0, a1, painted in taut(r):
                if not painted:
                    rope_run(cv, t, r, facing, h, world(center, facing, flip, ang, a0, r["lateral"]),
                             world(center, facing, flip, ang, a1, r["lateral"]), r["end"] - (a1 - a0) - 0.01, False)


def leaf_path(mat, look, view):
    # DrawbridgeArtPaths.LeafUp: the material's picture first, else the look's ("Material picks win")
    for p in ("RM_DrawbridgeLeafUp_%s_%s" % (mat, view), "RM_DrawbridgeLeafUp_%s_%s" % (view, look)):
        if os.path.exists(os.path.join(DB, p + ".png")):
            return p
    return None


def scene(look, mat, rot, raised, after, out):
    L = 5  # anchor, 3 deck, anchor
    fx, fz, ang = DIRS[rot]
    cells = [(i * fx, i * fz) for i in range(L)]
    xs = [c[0] for c in cells]
    zs = [c[1] for c in cells]
    cv = Canvas(min(xs) - 1.5, min(zs) - 1.5, max(xs) + 2.5, max(zs) + (4.5 if raised else 1.5))
    # the pit under the deck squares (two squares wider across)
    sxv, szv = abs(fz), abs(fx)   # across
    for i in range(1, L - 1):
        cx, cz = cells[i]
        for k in (-1, 0, 1):
            x, z = cx + sxv * k, cz + szv * k
            cv.rect(x - 0.5, z - 0.5, x + 0.5, z + 0.5, (0.17, 0.13, 0.10, 1.0))
    deck = tex(os.path.join(SB, look, "RM_SuspensionDeck_%s.png" % mat)) if os.path.exists(os.path.join(SB, look, "RM_SuspensionDeck_%s.png" % mat)) else tex(os.path.join(SB, look, "RM_SuspensionDeck.png"))
    if not raised:
        for i in range(1, L - 1):
            cv.quad(cells[i], (1, 1), ang, deck, FULL_UV)
    rots = {"N": "S", "S": "N", "E": "W", "W": "E"}
    draw_anchor(cv, cells[0], look, mat, rot, raised, after)
    draw_anchor(cv, cells[-1], look, mat, rots[rot], raised, after)
    if raised:   # DrawLeafUp: standing on the hinge edge of the anchor square, height = leaf length, drawn north-up
        view = {"N": "Face", "S": "Underside"}.get(rot, "Edge")
        p = leaf_path(mat, look, view)
        if p:
            t = tex(os.path.join(DB, p + ".png"))
            hgt = 3.0
            at = (cells[0][0] + fx * 0.5, cells[0][1] + fz * 0.5 + hgt / 2)
            flip = rot == "W"
            u0, u1, vt = 0.0, 1.0, 1.0
            key = p[len("RM_DrawbridgeLeafUp_"):]
            if after and key in FIX["leafEdges"]:
                b = FIX["leafEdges"][key]["body"]
                u0, u1 = max(0.0, b[0] - 0.008), min(1.0, b[1] + 0.008)
                vt = 1.0 - min(1.0, max(0.0, FIX["leafEdges"][key]["eyeTop"] - 0.002))
            x0, x1 = (0.5 - u1, 0.5 - u0) if flip else (u0 - 0.5, u1 - 0.5)
            ua, ub = (u1, u0) if flip else (u0, u1)
            cz = at[1] - hgt / 2 + hgt * vt / 2
            cv.quad((at[0] + (x0 + x1) / 2, cz), (x1 - x0, hgt * vt), 0, t, [(ua, 0), (ua, vt), (ub, vt), (ub, 0)])
    cv.save(out, "%s %s %s %s rot %s" % ("after" if after else "before", look, mat, "raised" if raised else "lowered", rot))


def main():
    out = sys.argv[1]
    looks = ["Scrapper"]
    if "--look" in sys.argv:
        looks = [sys.argv[sys.argv.index("--look") + 1]]
    if "--all-looks" in sys.argv:
        looks = ["Scrapper", "Industrial", "Modern", "Futuristic"]
    os.makedirs(out, exist_ok=True)
    n = 0
    for look in looks:
        for mat in ("Timber", "Steel"):
            for raised in (False, True):
                for after in (False, True):
                    for rot in "NESW":
                        scene(look, mat, rot, raised, after, os.path.join(out, "%s_%s_%s_%s_%s.png" % (
                            "after" if after else "before", look, mat, "raised" if raised else "lowered", rot)))
                        n += 1
    print("rendered %d scenes into %s" % (n, out))


if __name__ == "__main__":
    main()
