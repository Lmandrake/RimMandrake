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
SB = os.path.join(TEX, "RimMandrake", "FlowWorks", "SuspensionBridge")
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
def ropes_of(look, mat):
    k = "%s/%s/east" % (look, mat)
    return FIX["anchors"][k]


def taut(r):
    out = [(r["attach"], r["end"], True)]
    if r["end"] < 1.0 + DECK_OVERLAP:
        out.append((max(r["attach"], r["end"] - r["thick"]), 1.0 + DECK_OVERLAP, False))
    return out


def slack(r, n=14):
    s = 1.0 if r["lateral"] >= 0 else -1.0
    reach = SLACK_REACH
    f = min(1.0, 0.8 * abs(r["lateral"]) / 0.17)
    P = [(r["attach"], r["lateral"]), (reach, r["lateral"] + 0.05 * s * f), (reach, r["lateral"] - 0.13 * s * f),
         (r["attach"] + 0.3 * (reach - r["attach"]), r["lateral"] - 0.17 * s * f)]
    pts = []
    for i in range(n + 1):
        t = i / n
        u = 1 - t
        b = (u ** 3, 3 * u * u * t, 3 * u * t * t, t ** 3)
        pts.append((sum(b[j] * P[j][0] for j in range(4)), sum(b[j] * P[j][1] for j in range(4))))
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
    ropes = ropes_of(look, mat)
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
            pts = slack(r)
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
