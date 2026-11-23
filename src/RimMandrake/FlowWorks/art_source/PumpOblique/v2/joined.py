"""joined.py <out.png> [--no-socket]: the four installed pumps as the game draws them with a pipe on every side, offline.
Draw order as RM_LiquidJoins: pipe tiles and under-runs, the pipes' end flanges, the pump, then the south socket piece
(PumpSouthSocket.cs, whose numbers this reads). 512 px per cell. Not a live capture: the game decides."""
import os, re, sys
import numpy as np
from PIL import Image, ImageDraw
HERE = os.path.dirname(os.path.abspath(__file__))
FW = os.path.normpath(os.path.join(HERE, "../../.."))
TEX = os.path.join(FW, "Textures/RimMandrake/FlowWorks")
C = 512
LOOKS = ("Scrapper", "Industrial", "Modern", "Futuristic")


def atlas(look, i):
    a = Image.open(os.path.join(TEX, "Pipe", look, "UniversalPipe_Atlas.png")).convert("RGBA"); c = a.width / 4
    ax, ay = (i % 4) * c + c * .125, a.height - (i // 4 + 1) * c + c * .125
    return a.crop((int(ax), int(ay), int(ax + c * .75), int(ay + c * .75))).resize((C, C), Image.LANCZOS)


def pump(look):
    p = os.path.join(FW, "Textures/Things/Building/FlowWorks/Machinery/RM_LiquidPump.png") if look == "Scrapper" else \
        os.path.join(TEX, "Pump", look, "RM_LiquidPump.png")
    return Image.open(p).convert("RGBA")


def sockets():
    """{look: (centre x, centre z above the cell's south edge, half width, half height, pipe centre)}, from the C# table."""
    src = open(os.path.join(FW, "Source/Machinery/PumpSouthSocket.cs")).read()
    return {m[0]: tuple(float(v) for v in m[1:]) for m in
            re.findall(r'\{ "(\w+)", new Cap\(([\d.]+), ([\d.]+), ([\d.]+), ([\d.]+)\) \}', src)}


def joined(look, socket=True, flange=True):
    """A 3x3-cell picture of the pump with a pipe on each side."""
    im = Image.new("RGBA", (3 * C, 3 * C), (176, 150, 112, 255))
    # straight tiles: the outer pipe runs on (its far end links outward), under-run to the centre
    for dx, dy, i in ((1, 0, 5), (1, 2, 5), (0, 1, 10), (2, 1, 10)):
        im.alpha_composite(atlas(look, i), (dx * C, dy * C))
    ns, ew, h = atlas(look, 5), atlas(look, 10), C // 2
    im.alpha_composite(ns.crop((0, h, C, C)), (C, C)); im.alpha_composite(ns.crop((0, 0, C, h)), (C, C + h))
    im.alpha_composite(ew.crop((h, 0, C, C)), (C, C)); im.alpha_composite(ew.crop((0, 0, h, C)), (C + h, C))
    if flange:
        f = Image.open(os.path.join(TEX, "Joins", look, "Flange.png")).convert("RGBA").resize((h, h), Image.LANCZOS)
        q = h // 2
        # angle counter-clockwise from east, the face on the shared edge
        for (x, y), a in (((C - h, C + q), 0), ((2 * C, C + q), 180), ((C + q, 2 * C), 90), ((C + q, C - h), 270)):
            im.alpha_composite(f.rotate(a), (x, y))
    im.alpha_composite(pump(look).resize((C, C), Image.LANCZOS), (C, C))
    if socket and look in sockets():
        im.alpha_composite(socket_piece(look), (C, C))
    return im


def socket_piece(look):
    """The south pipe drawn over the pump: the pipe tile's drawn width stretched from its own width at the cell edge to the
    cap's width, its top end the top half of the cap's ellipse."""
    cx, cz, rx, rz = sockets()[look]
    t = np.array(atlas(look, 5)).astype(float)
    al = t[C // 2, :, 3] > 128; w = np.where(al)[0]; lo, hi = w[0] / C, (w[-1] + 1) / C
    S = 4
    yy, xx = np.mgrid[0:C * S, 0:C * S]
    x, z = (xx + .5) / (C * S), 1 - (yy + .5) / (C * S)
    k = np.clip(z / cz, 0, 1)
    left, right = lo + (cx - rx - lo) * k, hi + (cx + rx - hi) * k
    inside = (z <= cz) & (x >= left) & (x <= right)
    inside |= (z > cz) & (((x - cx) / rx) ** 2 + ((z - cz) / rz) ** 2 <= 1)
    f = np.clip((x - left) / (right - left), 0, 1); u = lo + f * (hi - lo)
    px = np.clip((u * C).astype(int), 0, C - 1); py = np.clip(((1 - z) * C).astype(int), 0, C - 1)
    o = t[py, px] * inside[..., None]
    o[..., 3] = np.where(inside, t[C // 2, px, 3], 0)
    o = o.reshape(C, S, C, S, 4); a = o[..., 3:]
    A = a.mean((1, 3)); rgb = (o[..., :3] * a).mean((1, 3)) / np.maximum(A, 1e-6)
    return Image.fromarray(np.clip(np.rint(np.concatenate([rgb, A], -1)), 0, 255).astype(np.uint8), "RGBA")


if __name__ == "__main__":
    sock = "--no-socket" not in sys.argv; fl = "--no-flange" not in sys.argv
    out = Image.new("RGB", (4 * 2 * C, 2 * C))
    for k, l in enumerate(LOOKS):
        out.paste(joined(l, sock, fl).crop((C // 2, C // 2, 5 * C // 2, 5 * C // 2)), (k * 2 * C, 0))
    out.save(sys.argv[1])
