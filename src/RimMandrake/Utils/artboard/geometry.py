"""Cell -> pixel mapping for a top-down orthographic RimWorld frame.

World X runs right, world Z runs UP; image v runs DOWN. So, per axis, an affine map:
    u = ax * X + bx          v = az * Z + bz   (az < 0)
where X, Z are continuous world coordinates (cell (x, z) spans [x, x+1] x [z, z+1]).

A board gives the map one of two ways:
  "camera": {"ppc": 25.0, "origin_px": [u0, v0]}  -- pixel of world corner (0, 0); square pixels
  "markers": [{"cell": [x, z], "px": [u, v]}, ...] -- pixel of a cell's CENTRE; fitted by least
             squares per axis (>= 2 distinct x and >= 2 distinct z). Residuals are reported, because a
             marker that is off by a cell is the commonest staging fault and must not be absorbed silently.
"""


class Mapping:
    def __init__(self, ax, bx, az, bz, residual_px=0.0):
        self.ax, self.bx, self.az, self.bz = ax, bx, az, bz
        self.residual_px = residual_px

    @property
    def ppc(self):
        return (abs(self.ax) + abs(self.az)) / 2.0

    def world_to_px(self, X, Z):
        return self.ax * X + self.bx, self.az * Z + self.bz

    def cell_box(self, x, z, w=1, h=1, pad=0.0):
        """Pixel box (left, top, right, bottom) of cells [x-pad, x+w+pad] x [z-pad, z+h+pad]."""
        u0, v0 = self.world_to_px(x - pad, z + h + pad)
        u1, v1 = self.world_to_px(x + w + pad, z - pad)
        l, r = sorted((u0, u1))
        t, b = sorted((v0, v1))
        return int(round(l)), int(round(t)), int(round(r)), int(round(b))

    def to_json(self):
        return {"ax": self.ax, "bx": self.bx, "az": self.az, "bz": self.bz,
                "ppc": self.ppc, "residual_px": self.residual_px}


def _fit_axis(pairs):
    """Least squares p = a*w + b over (world, pixel) pairs."""
    n = len(pairs)
    sw = sum(w for w, _ in pairs)
    sp = sum(p for _, p in pairs)
    sww = sum(w * w for w, _ in pairs)
    swp = sum(w * p for w, p in pairs)
    den = n * sww - sw * sw
    if den == 0:
        raise ValueError("markers need at least two distinct coordinates on each axis")
    a = (n * swp - sw * sp) / den
    b = (sp - a * sw) / n
    return a, b


def fit_markers(markers):
    xs = [(m["cell"][0] + 0.5, float(m["px"][0])) for m in markers]
    zs = [(m["cell"][1] + 0.5, float(m["px"][1])) for m in markers]
    ax, bx = _fit_axis(xs)
    az, bz = _fit_axis(zs)
    m = Mapping(ax, bx, az, bz)
    worst = 0.0
    for mk in markers:
        u, v = m.world_to_px(mk["cell"][0] + 0.5, mk["cell"][1] + 0.5)
        worst = max(worst, abs(u - mk["px"][0]), abs(v - mk["px"][1]))
    m.residual_px = worst
    return m


def mapping_from_board(board):
    if "camera" in board:
        c = board["camera"]
        ppc = float(c["ppc"])
        u0, v0 = c["origin_px"]
        return Mapping(ppc, float(u0), -ppc, float(v0))
    if "markers" in board:
        return fit_markers(board["markers"])
    raise ValueError("board needs 'camera' or 'markers'")
