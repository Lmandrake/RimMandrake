"""Software render of marks on real wall tiles at play zoom. Uses wallgeom's polygons, so what looks right here is what the C# prints."""
import numpy as np
from PIL import Image
import wallgeom as G

STUFF = {  # measured off game screenshots: (atlas, tint, floor)
    "slate_bricks": ("Bricks", (0.42, 0.40, 0.42)),
    "granite_bricks": ("Bricks", (0.62, 0.58, 0.55)),
    "marble_bricks": ("Bricks", (0.86, 0.85, 0.82)),
    "wood_planks": ("Planks", (0.62, 0.42, 0.24)),
    "steel_smooth": ("Smooth", (0.58, 0.58, 0.60)),
    "plasteel_smooth": ("Smooth", (0.62, 0.74, 0.72)),
}
FLOORS = {"wood": (58, 38, 22), "concrete": (96, 96, 92), "dirt": (94, 76, 56)}
_atlas = {}


def atlas(name):
    if name not in _atlas:
        _atlas[name] = Image.open(f"{G.CACHE}/ludeon.rimworld.core/Wall_Atlas_{name}.png").convert("RGBA")
    return _atlas[name]


def geom(name):
    return G.measure(atlas(name))


class Scene:
    def __init__(self, cells, w, h, stuff="slate_bricks", floor="wood", ppc=64, wallcolor=None):
        self.ppc, self.w, self.h = ppc, w, h
        self.wall = G.Wall(cells)
        self.at, tint = STUFF[stuff]
        self.tint = np.array(wallcolor or tint)
        self.g = geom(self.at)
        rng = np.random.default_rng(3)
        H, W = h * ppc, w * ppc
        base = np.array(FLOORS[floor], float)
        self.img = np.ones((H, W, 3)) * base
        self.img *= (1 + rng.normal(0, 0.02, (H, W, 1)))
        # plank seams, then the walls' shadow onto floors
        for x in range(0, W, ppc // 2):
            self.img[:, x:x + 1] *= 0.86
        self._draw_walls()

    def _draw_walls(self):
        p = self.ppc
        a = atlas(self.at)
        for c in self.wall.cells:
            t = G.tile(a, self.wall.links(c)).resize((p, p), Image.BILINEAR)
            arr = np.asarray(t).astype(float)
            col = arr[..., :3] * self.tint
            al = arr[..., 3:] / 255
            x0, y0 = c[0] * p, (self.h - c[1] - 1) * p
            self.img[y0:y0 + p, x0:x0 + p] = col * al + self.img[y0:y0 + p, x0:x0 + p] * (1 - al)
        self.base = self.img.copy()

    def poly_mask(self, poly):
        """Pixels inside a convex poly and their u, v by the poly's affine map."""
        p = self.ppc
        xs = np.array([q[0] for q in poly]) * p
        ys = (self.h - np.array([q[1] for q in poly])) * p
        x0, x1 = int(np.floor(xs.min())), int(np.ceil(xs.max()))
        y0, y1 = int(np.floor(ys.min())), int(np.ceil(ys.max()))
        x0, y0 = max(x0, 0), max(y0, 0)
        x1, y1 = min(x1, self.img.shape[1]), min(y1, self.img.shape[0])
        if x1 <= x0 or y1 <= y0:
            return None
        X, Y = np.meshgrid(np.arange(x0, x1) + 0.5, np.arange(y0, y1) + 0.5)
        n = len(poly)
        area = sum(xs[i] * ys[(i + 1) % n] - xs[(i + 1) % n] * ys[i] for i in range(n))
        inside = np.ones(X.shape, bool)
        for i in range(n):
            ax, ay, bx, by = xs[i], ys[i], xs[(i + 1) % n], ys[(i + 1) % n]
            cr = (bx - ax) * (Y - ay) - (by - ay) * (X - ax)
            inside &= cr * np.sign(area) >= -1e-6
        # affine from first three non-collinear
        A = np.array([[xs[i], ys[i], 1] for i in range(n)])
        U = np.array([poly[i][2] for i in range(n)])
        V = np.array([poly[i][3] for i in range(n)])
        cu = np.linalg.lstsq(A, U, rcond=None)[0]
        cv = np.linalg.lstsq(A, V, rcond=None)[0]
        return (x0, y0, x1, y1, inside, cu[0] * X + cu[1] * Y + cu[2], cv[0] * X + cv[1] * Y + cv[2])

    def draw(self, tex, polys, through=0.0, opacity=1.0):
        """tex: PIL RGBA prefiltered to about twice screen size. Paint, then the wall's own surface over it at `through`
        (unpainted wall is unchanged by construction: wall over wall is wall)."""
        t = np.asarray(tex).astype(float)
        th, tw = t.shape[:2]
        for poly in polys:
            m = self.poly_mask(poly)
            if m is None:
                continue
            x0, y0, x1, y1, inside, u, v = m
            fx = np.clip(u * tw - 0.5, 0, tw - 1.001)
            fy = np.clip((1 - v) * th - 0.5, 0, th - 1.001)
            ix, iy = fx.astype(int), fy.astype(int)
            ax, ay = (fx - ix)[..., None], (fy - iy)[..., None]
            s = (t[iy, ix] * (1 - ax) + t[iy, ix + 1] * ax) * (1 - ay) + (t[iy + 1, ix] * (1 - ax) + t[iy + 1, ix + 1] * ax) * ay
            al = s[..., 3:] / 255 * opacity
            reg = self.img[y0:y1, x0:x1]
            new = s[..., :3] * al + reg * (1 - al)
            if through:
                new = new * (1 - through) + self.base[y0:y1, x0:x1] * through
            reg[inside] = new[inside]

    def mark(self, tex, anchor, face, H, width, height, slide=0.0, slope=0.0, lift=0.5, through=0.3, opacity=1.0):
        polys = G.mark_polys(self.wall, anchor, face, self.g, H, width, height, slide, slope, lift)
        p = self.ppc
        # GPU would pick a mip by the larger shrink; give it a texture at about 2x the final footprint in its own plane.
        if face == G.FRONT:
            sz = (max(4, int(width * p * 2)), max(4, int(height * (self.g["crease"] / H) * p * 2)))
        else:
            sz = (max(4, int(width * p * 2)), max(4, int(height * (self.g["side"] / H) * p * 2)))
        tex2 = premul_resize(tex, sz)
        self.draw(tex2, polys, through, opacity)
        return polys

    def image(self):
        return Image.fromarray(np.clip(self.img, 0, 255).astype(np.uint8))


def premul_resize(tex, sz):
    a = np.asarray(tex.convert("RGBA")).astype(float)
    al = a[..., 3:] / 255
    pm = np.dstack((a[..., :3] * al, a[..., 3]))
    r = Image.fromarray(np.clip(pm, 0, 255).astype(np.uint8), "RGBA").resize(sz, Image.BOX if tex.width > sz[0] else Image.BILINEAR)
    b = np.asarray(r).astype(float)
    al = np.maximum(b[..., 3:] / 255, 1e-3)
    return Image.fromarray(np.clip(np.dstack((b[..., :3] / al, b[..., 3])), 0, 255).astype(np.uint8), "RGBA")


def room_cells(x0, z0, x1, z1):
    c = set()
    for x in range(x0, x1 + 1):
        c |= {(x, z0), (x, z1)}
    for z in range(z0, z1 + 1):
        c |= {(x0, z), (x1, z)}
    return c
