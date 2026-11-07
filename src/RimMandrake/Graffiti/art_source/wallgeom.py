"""How RimWorld draws a wall, measured from the atlas, and how a mark lies on it.

Offline twin of RM_GraffitiKernel's wall-plane code: same numbers, same polygons. Reads the extracted Core atlases.
A wall tile is a fake box: dark cap, a front face at the south edge (only with no wall south), side faces east and
west (only with no wall on that side), mitred where they meet. No north face exists anywhere in the art."""
import glob, os, sys
import numpy as np
from PIL import Image

CACHE = "/mnt/d/Luke/dev/RimMandrake/observed/inventory/bundle_textures"
N, E, S, W = 1, 2, 4, 8   # MaterialAtlasPool link bits


def tile(atlas, links):
    """The 0.1875 window the engine samples for a link set, as an RGBA array, row 0 = north edge of the cell."""
    w = atlas.width
    u0 = (links % 4) * 0.25 + 1 / 32
    v0 = (links // 4) * 0.25 + 1 / 32
    box = (round(u0 * w), round(w - (v0 + 0.1875) * w), round((u0 + 0.1875) * w), round(w - v0 * w))
    return atlas.crop(box)


def lum(a):
    return a[..., :3].astype(float).mean(2)


def crossing(profile, cap_at, face_lo, face_hi):
    """Walking from the cap's middle (cap_at) toward the face (indices face_lo..face_hi of the profile), the first index
    two thirds of the way from the cap's value to the face's own: that is the crease, not the cap's soft border."""
    p = np.asarray(profile, float)
    cap = p[cap_at]
    face = np.median(p[face_lo:face_hi])
    step = 1 if face_lo > cap_at else -1
    i = cap_at
    while 0 <= i < len(p):
        if abs(p[i] - cap) >= abs(face - cap) * 2 / 3:
            return i
        i += step
    return None


def measure(atlas):
    """crease = height of the front face above the cell's south edge; side = width of a side face; both in cells."""
    t = np.asarray(tile(atlas, E | W).convert("RGBA"))
    h = t.shape[0]
    prof = np.median(lum(t)[:, t.shape[1] // 3:2 * t.shape[1] // 3], axis=1)
    row = crossing(prof, h // 4, int(h * 0.80), int(h * 0.93))
    t = np.asarray(tile(atlas, N | S).convert("RGBA"))
    w = t.shape[1]
    prof = np.median(lum(t)[h // 3:2 * h // 3, :], axis=0)
    col = crossing(prof, w // 2, int(w * 0.86), int(w * 0.94))
    return {"crease": None if row is None else round(1 - row / h, 3), "side": None if col is None else round(1 - col / w, 3)}


def front_poly(links, g):
    """Front face of a wall cell, cell coords (x east, z north, 0..1), convex, counter-clockwise. None if hidden."""
    if links & S:
        return None
    c, m = g["crease"], g["side"]
    x0b, x0t = (0.0, 0.0) if links & W else (0.03, m)
    x1b, x1t = (1.0, 1.0) if links & E else (0.97, 1 - m)
    return [(x0b, 0.02), (x1b, 0.02), (x1t, c), (x0t, c)]


def side_poly(links, g, east):
    """East or west side face of a wall cell, None if a wall stands there. It stops at the front face's mitre."""
    if links & (E if east else W):
        return None
    c, m = g["crease"], g["side"]
    outer, inner = (0.97, 1 - m) if east else (0.03, m)
    z1 = 1.0 if links & N else 0.97 - 0.02
    if links & S:
        b_out, b_in = 0.0, 0.0
    else:
        b_out, b_in = 0.02, c
    pts = [(outer, b_out), (outer, z1), (inner, z1), (inner, b_in)]
    return pts if east else pts[::-1]


def clip(poly, conv):
    """Sutherland-Hodgman: poly (any orientation) against a convex counter-clockwise polygon. Keeps extra payload after (x, z)."""
    out = list(poly)
    n = len(conv)
    for i in range(n):
        ax, az = conv[i]
        bx, bz = conv[(i + 1) % n]
        inp, out = out, []
        if not inp:
            return []
        def side(p):
            return (bx - ax) * (p[1] - az) - (bz - az) * (p[0] - ax)
        for j, p in enumerate(inp):
            q = inp[j - 1]
            sp, sq = side(p), side(q)
            if (sp >= 0) != (sq >= 0):
                f = sq / (sq - sp)
                out.append(tuple(q[k] + (p[k] - q[k]) * f for k in range(len(p))))
            if sp >= 0:
                out.append(p)
    return out


def ccw(poly):
    a = sum(poly[i][0] * poly[(i + 1) % len(poly)][1] - poly[(i + 1) % len(poly)][0] * poly[i][1] for i in range(len(poly)))
    return poly if a > 0 else poly[::-1]


class Wall:
    """Wall cells on a grid; set of (x, z). Link set per cell as Graphic_Linked computes it."""

    def __init__(self, cells):
        self.cells = set(cells)

    def links(self, c):
        x, z = c
        l = 0
        if (x, z + 1) in self.cells: l |= N
        if (x + 1, z) in self.cells: l |= E
        if (x, z - 1) in self.cells: l |= S
        if (x - 1, z) in self.cells: l |= W
        return l


FRONT, EAST_FACE, WEST_FACE, HIDDEN = "front", "eastface", "westface", "hidden"


def face_of_side(wall_side):
    """Rot4 side the wall stands on, seen from the mark's floor cell -> which face of the wall the mark lies on."""
    return {0: FRONT, 1: WEST_FACE, 3: EAST_FACE, 2: HIDDEN}[wall_side]


def plane_to_cell(face, s, t, g, H):
    """Plane (s along the wall to the painter's right, cells from the anchor cell's centre; t up from the wall foot, world
    cells) -> screen cell coords relative to the anchor wall cell. Face height H world cells fills the visible band."""
    if face == FRONT:
        return (0.5 + s, 0.02 + t * (g["crease"] - 0.02) / H)
    if face == EAST_FACE:
        return (0.97 - t * (g["side"] - 0.03) / H, 0.5 + s)      # painter faces west, right hand is north
    if face == WEST_FACE:
        return (0.03 + t * (g["side"] - 0.03) / H, 0.5 - s)      # painter faces east, right hand is south
    raise ValueError(face)


def mark_polys(wall, anchor, face, g, H, width, height, slide=0.0, slope=0.0, lift=0.5):
    """One mark as cell-clipped polygons: list of [(screen_x, screen_z, u, v)...] in absolute cell coords.
    `slope` shears the baseline (rise per cell along the wall) so a hand's tilt never bends a run off the vertical.
    The mark runs along the wall cell by cell and stops at the first cell with no such face (corner, door, wall end)."""
    along = (1, 0) if face == FRONT else ((0, 1) if face == EAST_FACE else (0, -1))
    halfw = width / 2
    # t of the mark's centre: `lift` of the free height of the face, baseline shear kept inside by `room`
    room = abs(slope) * halfw
    hh = min(height, H - 2 * room)
    tc = hh / 2 + room + (H - hh - 2 * room) * lift
    out = []
    for k in range(-5, 6):
        s0 = k - 0.5
        if s0 + 1 < slide - halfw or s0 > slide + halfw:
            continue
        # walk outward from the anchor: every cell between must carry the face
        ok = True
        for j in (range(0, k + 1) if k >= 0 else range(0, k - 1, -1)):
            c = (anchor[0] + along[0] * j, anchor[1] + along[1] * j)
            if c not in wall.cells or face_poly(wall.links(c), g, face) is None:
                ok = False
        if not ok:
            continue
        cell = (anchor[0] + along[0] * k, anchor[1] + along[1] * k)
        conv = ccw(face_poly(wall.links(cell), g, face))
        conv_abs = [(cell[0] + x, cell[1] + z) for x, z in conv]
        quad = []
        for u, v in ((0, 0), (1, 0), (1, 1), (0, 1)):
            s = slide + (u - 0.5) * width
            t = tc + (v - 0.5) * hh + slope * (s - slide)
            x, z = plane_to_cell(face, s, t, g, H)
            quad.append((anchor[0] + x, anchor[1] + z, u, v))
        p = clip(quad, conv_abs)
        if len(p) >= 3:
            out.append(p)
    return out


def face_poly(links, g, face):
    if face == FRONT:
        return front_poly(links, g)
    if face == EAST_FACE:
        return side_poly(links, g, True)
    if face == WEST_FACE:
        return side_poly(links, g, False)
    return None


if __name__ == "__main__":
    rows = []
    for p in sorted(glob.glob(CACHE + "/*/*tlas*.png") + glob.glob(CACHE + "/*/textures/things/building/linked/*tlas*.png")):
        n = os.path.basename(p).lower()
        if not any(w in n for w in ("wall", "rock")) or n.endswith("_m.png") or "blueprint" in n:
            continue
        a = Image.open(p).convert("RGBA")
        print(os.path.relpath(p, CACHE), a.size, measure(a))
