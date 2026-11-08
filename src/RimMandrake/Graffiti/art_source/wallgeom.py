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


CAP_RATE = 1.0     # the top of a wall faces the camera: a world cell of it is a screen cell. The face is foreshortened, the top is not.
CAP_LIP = 0.08     # bare wall top the paint leaves at the far edge.
FOOT = 0.04        # world cells of bare face under the lowest mark.


def cap_poly(links, g):
    """The top of a wall cell, convex and counter-clockwise, in cell coords: above the crease, or the cell's whole depth where no
    front shows; inside the side faces; to the far edge where the wall runs on north."""
    c, m = g["crease"], g["side"]
    x0 = 0.0 if links & W else m
    x1 = 1.0 if links & E else 1 - m
    z0 = 0.0 if links & S else c
    z1 = 1.0 if links & N else 0.95
    return [(x0, z0), (x1, z0), (x1, z1), (x0, z1)]


def climb_max(face, g, H):
    """World height a mark can reach on this face: its whole face, then the top as far as the lip (front), or for a side face (seen
    almost edge-on) most of the way across the top, its paint starting high on the bevel (foot_of)."""
    return H + (0.95 - CAP_LIP - g["crease"] if face == FRONT else 1 - 2 * g["side"] - SIDE_TOP_LIP) / CAP_RATE


SIDE_FACE_SHARE, SIDE_TOP_LIP = 0.22, 0.05   # RM_GraffitiKernel.SideFaceShare, SideTopLip: a side mark is painted high, over the bevel and across the top


def foot_of(face, H):
    return FOOT if face == FRONT else H - SIDE_FACE_SHARE


def plane_to_screen(face, s, t, g, H):
    """Plane -> screen, relative to the anchor cell. Below t = H on the foreshortened face, above it on the top: one surface, bent."""
    if t <= H:
        return plane_to_cell(face, s, t, g, H)
    over = (t - H) * CAP_RATE
    if face == FRONT:
        return (0.5 + s, g["crease"] + over)
    if face == EAST_FACE:
        return (1 - g["side"] - over, 0.5 + s)
    return (g["side"] + over, 0.5 - s)


def split_t(poly, H):
    """A polygon in plane coords (s, t, u, v) cut at the crease: the part on the face, the part on the top."""
    low, high = [], []
    for j, p in enumerate(poly):
        q = poly[j - 1]
        if (p[1] <= H) != (q[1] <= H):
            f = (H - q[1]) / (p[1] - q[1])
            x = tuple(q[k] + (p[k] - q[k]) * f for k in range(4))
            low.append(x); high.append(x)
        (low if p[1] <= H else high).append(p)
    return low, high


def mark_polys(wall, anchor, face, g, H, width, height, slide=0.0, slope=0.0, lift=0.5, climb=True):
    """One mark as cell-clipped polygons, [(screen_x, screen_z, u, v)...] in absolute cell coords, on its face and bent onto the top."""
    along = (1, 0) if face == FRONT else ((0, 1) if face == EAST_FACE else (0, -1))
    halfw = width / 2
    room = abs(slope) * halfw
    top = climb_max(face, g, H) if climb else H
    foot = foot_of(face, H) if climb else FOOT
    hh = min(height, top - foot - 2 * room)
    t0 = foot + room + (top - foot - hh - 2 * room) * lift
    plane = []
    for u, v in ((0, 0), (1, 0), (1, 1), (0, 1)):
        s = slide + (u - 0.5) * width
        plane.append((s, t0 + v * hh + slope * (s - slide), u, v))
    low, high = split_t(plane, H)

    def screen(poly):
        out = []
        for s, t, u, v in poly:
            x, z = plane_to_screen(face, s, t, g, H)
            out.append((anchor[0] + x, anchor[1] + z, u, v))
        return out

    low, high = screen(low), screen(high)
    out = []
    for k in range(-5, 6):
        s0 = k - 0.5
        if s0 + 1 < slide - halfw or s0 > slide + halfw:
            continue
        ok = True
        for j in (range(0, k + 1) if k >= 0 else range(0, k - 1, -1)):
            c = (anchor[0] + along[0] * j, anchor[1] + along[1] * j)
            if c not in wall.cells or face_poly(wall.links(c), g, face) is None:
                ok = False
        if not ok:
            continue
        cell = (anchor[0] + along[0] * k, anchor[1] + along[1] * k)
        l = wall.links(cell)
        fp = [(cell[0] + x, cell[1] + z) for x, z in ccw(face_poly(l, g, face))]
        cp = [(cell[0] + x, cell[1] + z) for x, z in cap_poly(l, g)]
        if low:
            p = clip(low, fp)
            if len(p) >= 3:
                out.append(p)
        if high:
            p = clip(high, cp)
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
