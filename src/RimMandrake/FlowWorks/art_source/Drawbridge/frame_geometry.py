"""RIMMANDRAKE_PRUNE_FLOWWORKS_DRAWBRIDGE_TO_HIS_NOV_THIRD_RULINGS: the drawbridge's gate frame, hauling lines and mooring,
solved offline (the accepted v3 sheet's rigid model: mockups/v3/_work/scene.py). DrawbridgeFrameMath (Source/RM_DrawbridgeMath.cs)
is the C# copy; DrawbridgeChecks and selftest_flowworks_drawbridge_frame.py keep the two equal.

Frame: origin = the middle of the hinge lip; f = toward the leaf's tip; u along f, v along the bridge's side vector, h up.
A point draws at (f*u + side*v) + (0, K*h): the map camera keeps the ground square and lifts a height K cells up the screen.

    python3 frame_geometry.py sheet OUT.png [material]     every direction x width x length, raised and lowered, in the real art
"""
import math, os, sys

K = 0.5
PLANE = -0.10       # the frame's plane: just behind the hinge lip
POST_V = 0.10       # a post's centre outside the lanes' edge
POST_W = 0.22       # drawn width
POST_H = 1.26       # drawn height up the screen (cells), caps included
OPEN_H = 0.86       # the doorway's clear height up the screen
LINTEL_T = 0.30     # the lintel's drawn depth below the post caps
SHEAVE_Z = 1.10     # a sheave's height up the screen
EYE_BACK = 0.0      # a hauling line ties to the drawn tip edge itself
MOOR_U = 0.26       # the mooring posts' distance past the tip
DRUM_Z = 0.10       # the rope leaves the winch this far above its square's centre
HITCH_DEG = 3.0
HOLD = {"N": 85.0, "S": 55.0, "E": 75.0, "W": 75.0}
F = {"N": (0, 1), "S": (0, -1), "E": (1, 0), "W": (-1, 0)}


def side(d):           # a record running d: its side vector is d turned clockwise
    x, z = F[d]
    return (z, -x)


def xy(d, u, v, zup=0.0):
    fx, fz = F[d]
    sx, sz = side(d)
    return (fx * u + sx * v, fz * u + sz * v + zup)


def leaf_pt(d, along, v, deg, below=0.0):
    a = math.radians(deg)
    return xy(d, along * math.cos(a) + below * math.sin(a), v, K * (along * math.sin(a) - below * math.cos(a)))


def eye(d, w, L, sgn, deg):
    return leaf_pt(d, L - EYE_BACK, sgn * w / 2, deg)


def sheave(d, w, sgn):
    return xy(d, PLANE, sgn * (w / 2 + POST_V), SHEAVE_Z)


def near_line(d, w, L, sgn, deg, winch_sgn, drum):
    """one taut hauling line: eye -> its own sheave -> (along the lintel to the winch-side sheave) -> the winch drum"""
    p = [eye(d, w, L, sgn, deg), sheave(d, w, sgn)]
    if sgn != winch_sgn:
        p.append(sheave(d, w, winch_sgn))
    return p + [drum]


def moor(d, w, L, sgn):
    return xy(d, L + MOOR_U, sgn * (w / 2 - 0.1))


def hitch(d, w, L, sgn, deg):
    """the short mooring hitch on the far bank: whole lowered, cast off in the first HITCH_DEG, nothing at the hold"""
    k = 1 - deg / HITCH_DEG
    if k <= 0:
        return None
    a = moor(d, w, L, sgn)
    a = (a[0], a[1] + 0.12)
    b = eye(d, w, L, sgn, deg)
    return [a, (a[0] + (b[0] - a[0]) * k, a[1] + (b[1] - a[1]) * k)]


def posts(d, w):
    """(centre x, foot z) of the two posts"""
    return [xy(d, PLANE, s * (w / 2 + POST_V)) for s in (-1, 1)]


def interior(d, w):
    """the doorway's clear rectangle on screen (x0, z0, x1, z1); None edge-on (east/west)"""
    if d in "EW":
        return None
    z = xy(d, PLANE, 0)[1]
    h = w / 2 + POST_V - POST_W / 2
    return (-h, z, h, z + OPEN_H)


# ── the composite (real art) ───────────────────────────────────────────────────────────────────────────────────────────
def sheet(out, mats=("Timber", "Steel")):
    from PIL import Image, ImageDraw
    import numpy as np
    here = os.path.dirname(os.path.abspath(__file__))
    T = os.path.join(here, "..", "..", "Textures")
    D, S = "Things/Building/FlowWorks/Drawbridge/", "Things/Building/FlowWorks/SuspensionBridge/"
    cache = {}

    def tex(p):
        if p not in cache:
            cache[p] = Image.open(os.path.join(T, p + ".png")).convert("RGBA")
        return cache[p]
    PX = 72

    class Cv:
        def __init__(s, W, H):
            s.W, s.H = W, H
            s.im = Image.new("RGBA", (int(W * PX), int(H * PX)), (134, 122, 98, 255))

        def p(s, x, z):
            return (x * PX, (s.H - z) * PX)

        def rect(s, x0, z0, x1, z1, col):
            ImageDraw.Draw(s.im).rectangle([*s.p(x0, z1), *s.p(x1, z0)], fill=col)

        def quad(s, t, box, pts, shade=1.0):
            """box in texture px; pts = screen corners TL,TR,BR,BL"""
            src = t.crop(box)
            if shade != 1.0:
                a = np.asarray(src).astype(float).copy(); a[..., :3] *= shade; src = Image.fromarray(a.astype("uint8"), "RGBA")
            q = [s.p(*a) for a in pts]
            x0 = int(min(a[0] for a in q)) - 1; y0 = int(min(a[1] for a in q)) - 1
            x1 = int(max(a[0] for a in q)) + 2; y1 = int(max(a[1] for a in q)) + 2
            if x1 - x0 < 3 or y1 - y0 < 3:
                return
            m, b = [], []
            for (x, y), (a, c) in zip([(a - x0, e - y0) for a, e in q], [(0, 0), (src.width, 0), (src.width, src.height), (0, src.height)]):
                m += [[x, y, 1, 0, 0, 0, -a * x, -a * y], [0, 0, 0, x, y, 1, -c * x, -c * y]]
                b += [a, c]
            try:
                co = np.linalg.solve(np.array(m, float), np.array(b, float)).tolist()
            except np.linalg.LinAlgError:
                return
            if x1 <= 0 or y1 <= 0 or x0 >= s.im.width or y0 >= s.im.height:
                return
            lay = src.transform((x1 - x0, y1 - y0), Image.PERSPECTIVE, co, Image.BICUBIC)
            s.im.alpha_composite(lay, (max(x0, 0), max(y0, 0)), (max(-x0, 0), max(-y0, 0)))

        def plane(s, t, box, cx, cz, w, h, ang=0):
            r = math.radians(ang); c, sn = math.cos(r), math.sin(r)
            f = lambda x, z: (cx + x * c + z * sn, cz - x * sn + z * c)
            s.quad(t, box, [f(-w / 2, h / 2), f(w / 2, h / 2), f(w / 2, -h / 2), f(-w / 2, -h / 2)])

        def line(s, a, b, t, w):
            d = math.hypot(b[0] - a[0], b[1] - a[1])
            if d < 1e-4:
                return
            tile = w * t.width / t.height
            n = max(1, round(d / tile))
            r = math.atan2(b[0] - a[0], b[1] - a[1])
            rt = t.transpose(Image.ROTATE_90)
            for i in range(n):
                k = (i + .5) / n
                s.plane(rt, (0, 0, rt.width, rt.height), a[0] + (b[0] - a[0]) * k, a[1] + (b[1] - a[1]) * k, w, d / n + .01, math.degrees(r))

    def draw(cv, ox, oz, d, w, L, m, deg):
        O = lambda q: (q[0] + ox, q[1] + oz)
        horiz = d in "EW"
        ang = {"N": 0, "E": 90, "S": 180, "W": 270}[d]
        # pads: one per near anchor square, footing at the far bank
        pad, pbox = (tex(S + "RM_SuspensionDeck_Timber"), (26, 0, 230, 256)) if m == "Timber" else (tex(S + "RM_SuspensionDeck_SteelGrated"), (56, 0, 200, 256))
        for lane in range(w):
            c = O(xy(d, -.5, lane - (w - 1) / 2))
            cv.plane(pad, pbox, *c, 1, 1, ang)
        foot = tex(S + "RM_SuspensionAnchor_Steel_north")
        a, b = O(xy(d, L + .08, -w / 2)), O(xy(d, L + .44, w / 2))
        x0, x1 = sorted((a[0], b[0])); z0, z1 = sorted((a[1], b[1]))
        cv.rect(x0 - .03, z0 - .03, x1 + .03, z1 + .03, (20, 18, 16, 255))
        cv.quad(foot, (60, 120, 190, 190), [(x0, z1), (x1, z1), (x1, z0), (x0, z0)], .55)
        mt, mb, mw, mh = (tex(S + "RM_SuspensionAnchor_Timber_north"), (54, 104, 108, 190), .21, .335) if m == "Timber" else (tex(S + "RM_SuspensionAnchor_Steel"), (42, 134, 100, 242), .225, .42)
        for s in sorted((-1, 1), key=lambda s: -moor(d, w, L, s)[1]):
            c = O(moor(d, w, L, s))
            cv.plane(mt, mb, c[0], c[1] + mh / 2 - .1, mw, mh)
        # winch beside the hinge anchor, lane = w
        wc = O(xy(d, -.5, w / 2 + .5))
        wf = {"N": "south", "S": "north", "E": "east", "W": "east"}[d]
        # in game PartRot = the leaf's direction: rot north draws _north
        wf = {"N": "north", "S": "south", "E": "east", "W": "east"}[d]
        wt = tex(D + f"RM_DrawbridgeWinch_{m}_{wf}")
        if d == "W":
            wt = wt.transpose(Image.FLIP_LEFT_RIGHT)
        cv.plane(wt, (0, 0, 384, 384), *wc, 1.5, 1.5)
        # gate panels on the door squares
        gt = tex(D + f"RM_DrawbridgeGate_{m}_Closed_south")
        ge = tex(D + f"RM_DrawbridgeGate_{m}_Open_east")
        shut = deg > 0
        for lane in sorted(range(w), key=lambda q: -xy(d, -1.5, q)[1]):
            c = O(xy(d, -1.5, lane - (w - 1) / 2))
            k = 1.0 if shut else .14
            if horiz:
                cv.plane(ge, (100, 90, 156, 330), c[0], c[1], .24 * (1.0 if shut else .4), 1.0)
            else:
                for hs in (-1, 1):
                    cv.plane(gt, (62, 122, 193, 122 + 226 * k), c[0] + hs * .25, c[1] - .39 + .45 * k, .5, .9 * k)
        # leaf
        ft = tex(D + f"RM_DrawbridgeLeafUp_{m}_Face")
        for lane in range(w):
            v0 = lane - w / 2
            for i in range(L):
                sl = 0 if i == 0 else 3 if i == L - 1 else 1 + (i - 1) % 2
                box = (31, 1024 - 256 * (sl + 1), 241, 1024 - 256 * sl)
                p = lambda al, v: O(leaf_pt(d, al, v, deg))
                amt = min(1, deg / HOLD[d]) * .42
                cv.quad(ft, box, [p(i + 1, v0), p(i + 1, v0 + 1), p(i, v0 + 1), p(i, v0)], 1 - amt * (1 - (i + .5) / L))
        if deg > 1:
            th = .16 if m == "Timber" else .10
            q = [O(leaf_pt(d, L, v, deg, b)) for v, b in ((-w / 2, 0), (w / 2, 0), (w / 2, th), (-w / 2, th))]
            ImageDraw.Draw(cv.im).polygon([cv.p(*a) for a in q], fill=(168, 120, 74, 255) if m == "Timber" else (150, 154, 158, 255), outline=(20, 16, 12, 255))
            if horiz:
                vv = -w / 2 if xy(d, 0, -1)[1] < 0 else w / 2
                q = [O(leaf_pt(d, al, vv, deg, b)) for al, b in ((0, 0), (L, 0), (L, th), (0, th))]
                ImageDraw.Draw(cv.im).polygon([cv.p(*a) for a in q], fill=(92, 60, 34, 255) if m == "Timber" else (70, 74, 78, 255), outline=(20, 16, 12, 255))
        # frame
        fs = tex(D + f"RM_DrawbridgeGate_{m}_Open_south")
        ps = sorted([O(q) for q in posts(d, w)], key=lambda q: -q[1])
        if not horiz:
            z = ps[0][1]
            xl, xr = sorted(q[0] for q in ps)
            s0, s1 = xl + POST_W / 2 - .02, xr - POST_W / 2 + .02
            lt, lb = (84, 150) if m == "Timber" else (84, 122)
            unit = (190 - 64) / 256 * POST_H / (300 / 256)
            lh = (lb - lt) / 256 * POST_H / (300 / 256)
            top = z + POST_H - (lt - 72) / 256 * POST_H / (300 / 256)
            n = max(1, round((s1 - s0) / unit))
            for i in range(n):
                cv.plane(fs, (64, lt, 190, lb), s0 + (s1 - s0) * (i + .5) / n, top - lh / 2, (s1 - s0) / n + .004, lh)
            cv.plane(fs, (11, 72, 66, 372), xl, z + POST_H / 2, POST_W, POST_H)
            cv.plane(fs, (189, 72, 244, 372), xr, z + POST_H / 2, POST_W, POST_H)
        else:
            pw = .34
            for k, q in enumerate(ps):
                if k == 1:   # the lintel seen end to end, under the nearer post's cap
                    z0, z1 = ps[1][1] + POST_H - .12, ps[0][1] + POST_H - .10
                    cv.rect(q[0] - .16, z0, q[0] + .16, z1, (20, 16, 12, 255))
                    lt, lb = (88, 112) if m == "Timber" else (86, 120)
                    n = max(1, round((z1 - z0) / .5))
                    for i in range(n):
                        cv.plane(fs, (64, lt, 190, lb), q[0], z0 + (z1 - z0) * (i + .5) / n, (z1 - z0) / n, .27, 90)
                cv.plane(ge, (94, 10, 162, 374), q[0], q[1] + POST_H / 2, pw, POST_H)
        # lines
        rope = tex("Things/Building/FlowWorks/Rivers/RM_FerryRope").crop((0, 26, 256, 38)) if m == "Timber" else tex("RimMandrake/FlowWorks/SuspensionBridge/Cables/RM_Cable_Galv")
        lw = .075 if m == "Timber" else .075
        drum = (wc[0], wc[1] + DRUM_Z)
        for s in (-1, 1):
            h = hitch(d, w, L, s, deg)
            if h:
                cv.line(O(h[0]), O(h[1]), rope, lw)
            pth = [O(q) for q in near_line(d, w, L, s, deg, 1, (0, 0))[:-1]] + [drum]
            for a, b in zip(pth, pth[1:]):
                cv.line(a, b, rope, lw)

    rows = []
    for m in mats:
        for d in "SNEW":
            rows.append((m, d))
    cases = [(1, 4), (2, 4), (4, 4), (1, 1), (2, 2)] + [(2, 8)]
    cw, ch = 12.0, 12.0
    W = len(cases) * 2
    big = Image.new("RGB", (int(W * 5.2 * PX) + 0, int(len(rows) * 7 * PX)))
    cells = []
    for (m, d) in rows:
        strip = []
        for (w, L) in cases:
            if m == "Timber" and L > 4:
                continue
            for deg in (0, HOLD[d]):
                horiz = d in "EW"
                ww, hh = (L + 5.2, w + 4.6 + L * .25) if horiz else (w + 4.0, L + 5.0)
                cv = Cv(ww, hh)
                lip = {"N": (ww / 2 - .4, 2.4), "S": (ww / 2 + .4, hh - 2.8), "E": (2.4, w / 2 + 1.6), "W": (ww - 2.4, w / 2 + 1.6)}[d]
                p0, p1 = (xy(d, 0, 0)), (xy(d, L, 0))
                if horiz:
                    xs = sorted((lip[0], lip[0] + p1[0])); cv.rect(xs[0], 0, xs[1], hh, (38, 26, 18, 255))
                else:
                    zs = sorted((lip[1], lip[1] + p1[1])); cv.rect(0, zs[0], ww, zs[1], (38, 26, 18, 255))
                draw(cv, lip[0], lip[1], d, w, L, m, deg)
                strip.append(cv.im.convert("RGB"))
        H = max(i.height for i in strip)
        r = Image.new("RGB", (sum(i.width + 6 for i in strip), H + 6), (20, 20, 20))
        x = 0
        for i in strip:
            r.paste(i, (x, 0)); x += i.width + 6
        cells.append(r)
    W = max(r.width for r in cells)
    big = Image.new("RGB", (W, sum(r.height for r in cells)), (20, 20, 20))
    y = 0
    for r in cells:
        big.paste(r, (0, y)); y += r.height
    big.save(out)
    print(big.size)


if __name__ == "__main__" and len(sys.argv) > 2 and sys.argv[1] == "sheet":
    sheet(sys.argv[2], tuple(sys.argv[3:]) or ("Timber", "Steel"))
