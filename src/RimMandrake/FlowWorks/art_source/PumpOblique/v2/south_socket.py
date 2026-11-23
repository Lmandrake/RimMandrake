"""The round cap drawn on the south arm of each installed pump: south_socket.py prints it; --write regenerates PumpSouthSocket.cs.

The cap's dark seam is the darkest pixel on each of 120 rays round a seed ellipse; an axis-aligned ellipse is fitted to it.
Numbers are cells from the pump cell's south-west corner. selftest_pump_south_socket.py checks the table against the art."""
import os, sys
import numpy as np
from PIL import Image
HERE = os.path.dirname(os.path.abspath(__file__))
FW = os.path.normpath(os.path.join(HERE, "../../.."))
OUT = os.path.join(FW, "Source/Machinery/PumpSouthSocket.cs")
TEX = os.path.join(FW, "Textures")
ART = {l: "RimMandrake/FlowWorks/Pump/%s/RM_LiquidPump.png" % l for l in ("Industrial", "Modern", "Futuristic")}
ART["Scrapper"] = "Things/Building/FlowWorks/Machinery/RM_LiquidPump.png"
SEED = {"Scrapper": (256, 448, 33, 28), "Industrial": (256, 445, 33, 28), "Modern": (256, 446, 35, 30), "Futuristic": (256, 451, 33, 27)}
LOOKS = tuple(SEED)


def bilinear(a, y, x):
    y0, x0 = np.floor(y).astype(int), np.floor(x).astype(int)
    fy, fx = y - y0, x - x0
    return a[y0, x0] * (1 - fy) * (1 - fx) + a[y0 + 1, x0] * fy * (1 - fx) + a[y0, x0 + 1] * (1 - fy) * fx + a[y0 + 1, x0 + 1] * fy * fx


def image(look):
    return np.array(Image.open(os.path.join(TEX, ART[look])).convert("RGBA")).astype(float)


def fit(look):
    """(centre x, centre y, half width, half height) in px of the 512 px art, pixel edges counted from 0; and rays kept."""
    lum = image(look)[..., :3].mean(-1)
    cx, cy, rx, ry = SEED[look]
    p = []
    for th in np.linspace(0, 2 * np.pi, 120, endpoint=False):
        f = np.linspace(.85, 1.15, 61)
        xs, ys = cx + f * rx * np.cos(th), cy + f * ry * np.sin(th)
        i = bilinear(lum, ys, xs).argmin(); p.append((xs[i], ys[i]))
    p = np.array(p)
    for _ in range(4):
        A = np.c_[p[:, 0] ** 2, p[:, 1] ** 2, p[:, 0], p[:, 1]]
        s = np.linalg.lstsq(A, np.ones(len(p)), rcond=None)[0]
        x0, y0 = -s[2] / 2 / s[0], -s[3] / 2 / s[1]
        k = 1 + s[0] * x0 ** 2 + s[1] * y0 ** 2
        RX, RY = (k / s[0]) ** .5, (k / s[1]) ** .5
        p = p[abs(np.hypot((p[:, 0] - x0) / RX, (p[:, 1] - y0) / RY) - 1) < .05]
    return x0 + .5, y0 + .5, RX, RY, len(p)


def pipe_span(look):
    """(left, right) of the look's north-south pipe, in the atlas sub-tile's 0..1 frame."""
    a = np.array(Image.open(os.path.join(TEX, "RimMandrake/FlowWorks/Pipe", look, "UniversalPipe_Atlas.png")).convert("RGBA"))
    n = a.shape[0]; c = n / 4
    row = a[int(n - 1.5 * c), int(c):int(2 * c), 3] > 128
    w = np.where(row)[0]
    return (w[0] / c - .125) / .75, ((w[-1] + 1) / c - .125) / .75


def table():
    return {l: (round(x / 512, 4), round(1 - y / 512, 4), round(rx / 512, 4), round(ry / 512, 4)) for l in LOOKS for x, y, rx, ry, _ in [fit(l)]}


if __name__ == "__main__":
    for l in LOOKS:
        print(l, [round(v, 2) for v in fit(l)], "pipe", ["%.4f" % v for v in pipe_span(l)])
    if "--write" in sys.argv:
        src = open(OUT).read()
        a, b = src.index("// table:"), src.index("// :table")
        body = "// table:\n" + "".join('            { "%s", new Cap(%.4f, %.4f, %.4f, %.4f) },\n' % ((l,) + v) for l, v in table().items())
        open(OUT, "w").write(src[:a] + body + "            " + src[b:])
