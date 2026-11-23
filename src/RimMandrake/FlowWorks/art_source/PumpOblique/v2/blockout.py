"""Grey 3D blockout of the liquid pump under the building camera, the camera anchor (image 1) of each pump render.

Orthographic, looking north, 34 deg up: screen_x = 256 + e, screen_y = 256 - K*n - H*(z - AXIS), K=0.56, H=0.828.
Real solids (signed distances, raymarched), so hidden faces are hidden. N/S necks are longer in the ground plane than
E/W necks, because the ground grid of the game is not foreshortened and every port must end at its edge centre.
Run: python3 blockout.py <out.png> [flange_radius] [neck_radius]      (1024 px, transparent)
"""
import sys
import numpy as np
from PIL import Image

K, H = 0.56, 0.8285
S = 2                                  # px per unit
FR = float(sys.argv[2]) if len(sys.argv) > 2 else 50.0
NR = float(sys.argv[3]) if len(sys.argv) > 3 else 35.0
AXIS = FR + 6
BR, BH = 134.0, AXIS + 62              # casing
NEND = (256 - 20 - H * FR) / K         # N terminal face: its ellipse top at y=20
SEND = (490 - 256 - H * FR) / K        # S terminal face: its ellipse bottom at y=490
EEND = 246.0
FT = 24.0                              # flange thickness along the axis (E/W)
FTN = FT / K * 0.75


def cyl(p, axis, c, r, h0, h1, rd=3.0):
    i = [k for k in range(3) if k != axis]
    d = np.sqrt((p[..., i[0]] - c[0]) ** 2 + (p[..., i[1]] - c[1]) ** 2) - r + rd
    a = np.abs(p[..., axis] - (h0 + h1) / 2) - (h1 - h0) / 2 + rd
    return np.minimum(np.maximum(d, a), 0) + np.sqrt(np.maximum(d, 0) ** 2 + np.maximum(a, 0) ** 2) - rd


def torus(p, z, R, r):
    q = np.sqrt(p[..., 0] ** 2 + p[..., 1] ** 2) - R
    return np.sqrt(q * q + (p[..., 2] - z) ** 2) - r


def capsule(p, a, b, r):
    a, b = np.array(a, float), np.array(b, float)
    t = np.clip(((p - a) @ (b - a)) / ((b - a) @ (b - a)), 0, 1)[..., None]
    return np.linalg.norm(p - a - t * (b - a), axis=-1) - r


def parts():
    """[(shade, fn)]"""
    L = []
    add = lambda s, f: L.append((s, f))
    add(150, lambda p: cyl(p, 2, (0, 0), BR, 8, BH))                      # casing
    add(120, lambda p: cyl(p, 2, (0, 0), BR + 9, 0, 14, 4))               # foot ring
    add(165, lambda p: cyl(p, 2, (0, 0), BR + 6, BH - 16, BH, 4))         # lid rim
    domeR = 105.0; rise = 24.0; R = (domeR ** 2 + rise ** 2) / (2 * rise)
    def dome(p):
        s = np.sqrt(p[..., 0] ** 2 + p[..., 1] ** 2 + (p[..., 2] - (BH + rise - R)) ** 2) - R
        return np.maximum(s, np.maximum(BH - 1 - p[..., 2], np.sqrt(p[..., 0] ** 2 + p[..., 1] ** 2) - domeR))
    add(185, dome)
    add(170, lambda p: cyl(p, 2, (0, 0), domeR + 4, BH - 2, BH + 6, 2))
    top = BH + rise
    add(60, lambda p: cyl(p, 2, (0, 0), 47, BH, top + 3, 1))              # dark grille well
    add(200, lambda p: torus(p, top + 5, 48, 7))                          # grille rim
    for a in (0, 90):
        c, s = np.cos(np.radians(a)), np.sin(np.radians(a))
        add(200, lambda p, c=c, s=s: capsule(p, (-46 * c, -46 * s, top + 7), (46 * c, 46 * s, top + 7), 5))
    add(130, lambda p: torus(p, top + 4, 28, 3))
    add(210, lambda p: cyl(p, 2, (0, 0), 15, top, top + 18, 5))           # hub
    for a in (45, 135, 225, 315):                                          # dome bolts
        x, y = 86 * np.cos(np.radians(a)), 86 * np.sin(np.radians(a))
        add(215, lambda p, x=x, y=y: cyl(p, 2, (x, y), 11, BH, BH + 19, 3))
    for a in range(15, 360, 30):                                           # lid rim bolts
        x, y = 124 * np.cos(np.radians(a)), 124 * np.sin(np.radians(a))
        add(205, lambda p, x=x, y=y: cyl(p, 2, (x, y), 6, BH, BH + 6, 2))
    for a in (205, 232, 308, 335):                                         # wall rivets
        ca, sa = np.cos(np.radians(a)), np.sin(np.radians(a))
        add(205, lambda p, ca=ca, sa=sa: np.linalg.norm(p - np.array([BR * ca, BR * sa, BH * .5]), axis=-1) - 7)
    # necks: axis 1 = n (north +), axis 0 = e
    for ax, end, ft in ((1, NEND, FTN), (1, -SEND, FTN), (0, EEND, FT), (0, -EEND, FT)):
        sgn = 1 if end > 0 else -1
        lo, hi = sorted((sgn * (BR - 40), end)); c = (0, AXIS)
        add(160, lambda p, ax=ax, lo=lo, hi=hi: cyl(p, ax, (0, AXIS), NR, lo, hi, 2))
        f0, f1 = sorted((end, end - sgn * ft))
        add(190, lambda p, ax=ax, f0=f0, f1=f1: cyl(p, ax, (0, AXIS), FR, f0, f1, 5))       # flange
        g0, g1 = sorted((end - sgn * ft, end - sgn * ft * 1.45))
        add(135, lambda p, ax=ax, g0=g0, g1=g1: cyl(p, ax, (0, AXIS), NR + 6, g0, g1, 3))   # weld collar
        r0, r1 = sorted((sgn * (BR - 12), sgn * (BR + 13)))
        add(175, lambda p, ax=ax, r0=r0, r1=r1: cyl(p, ax, (0, AXIS), NR + 8, r0, r1, 4))  # root collar on the casing
        if sgn < 0 and ax == 1:                                                              # S mating face: raised boss
            add(150, lambda p: cyl(p, 1, (0, AXIS), NR - 2, -SEND - 5, -SEND, 2))
        for a in range(30, 390, 60):                                                          # flange bolts
            u, v = (NR + FR) / 2 * np.cos(np.radians(a)), (NR + FR) / 2 * np.sin(np.radians(a))
            b0, b1 = sorted((end - sgn * (ft + 8), end + sgn * (4 if ax else 3)))
            add(225, lambda p, ax=ax, u=u, v=v, b0=b0, b1=b1: cyl(p, ax, (u, AXIS + v), 7.0, b0, b1, 2))
    return L


def main():
    P = parts()
    n = 512 * S
    yy, xx = np.mgrid[0:n, 0:n]
    e = (xx + .5) / S - 256; v = 256 - (yy + .5) / S          # v = K*n + H*(z-AXIS)
    # view dir into the scene (north and down): perpendicular to screen-up (0,K,H)
    d = np.array([0, H, -K])
    up = np.array([0, K, H])
    o = np.stack([e, v * up[1], v * up[2] + AXIS], -1) - 700 * d
    t = np.zeros((n, n)); hit = np.zeros((n, n), bool); idx = np.zeros((n, n), int)
    act = np.ones((n, n), bool)
    # screen-space reject of rays that can hit nothing is not needed: 1024^2 x 80 steps on shrinking sets
    for _ in range(140):
        w = np.where(act)
        if not len(w[0]):
            break
        p = o[w] + t[w][:, None] * d
        best = np.full(len(p), 1e9)
        for s, f in P:
            best = np.minimum(best, f(p))
        t[w] += best * 0.95
        hit[w] |= best < 0.15
        act[w] = (best >= 0.15) & (t[w] < 1500)
    w = np.where(hit)
    p = o[w] + t[w][:, None] * d
    ds = np.stack([f(p) for _, f in P], 0)
    idx[w] = ds.argmin(0) + 1
    sc = lambda q: np.min(np.stack([f(q) for _, f in P], 0), 0)
    g = np.stack([sc(p + dv) - sc(p - dv) for dv in np.eye(3) * 0.4], -1)
    g /= np.maximum(np.linalg.norm(g, axis=-1, keepdims=True), 1e-6)
    l = np.array([-.35, -.45, .82]); l /= np.linalg.norm(l)
    lam = np.clip(g @ l, 0, 1)
    sh = np.array([s for s, _ in P])[idx[w] - 1]
    img = np.zeros((n, n, 4))
    img[w] = np.concatenate([np.repeat((sh * (.35 + .75 * lam))[:, None], 3, 1), np.full((len(p), 1), 255)], 1)
    # part edges
    depth = np.where(hit, t, 3000)
    edge = np.zeros((n, n), bool)
    for ax in (0, 1):
        r = np.roll(idx, 1, ax); edge |= (idx != r) & (hit)
        edge |= hit & (np.abs(depth - np.roll(depth, 1, ax)) > 14)
    img[edge & hit, :3] = 25
    Image.fromarray(np.clip(img, 0, 255).astype(np.uint8), "RGBA").save(sys.argv[1])
    a = np.where(hit); print("bbox px/512:", a[1].min() / S, a[0].min() / S, a[1].max() / S, a[0].max() / S)


if __name__ == "__main__":
    main()
