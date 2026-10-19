#!/usr/bin/env python3
"""True-scale offline preview for PIPE_ENDS_BUILD_MEET_IN_THE_MIDDLE + PUMP_ART_RESKIN_LESS_GARDEN_HOSE.

Emulates the game's draw order at 64 px/cell: terrain, then the under-building centre stubs (pipe: the atlas's
straight tile cropped per LiquidJoinRule.StubPieces; hose: the plump strand), then pipe cells (linked atlas, linking
into tanks/machines), hoses and their brass couplings at the shared edge, then the buildings on top, beside a vanilla
colonist (Utils/art/scale_panel.human_sprite). Scenes: pump + pipe (W); pump + hose (S); pump + pipe (W) and hose (E);
2x2 tank fed by a pipe entering off its centre line (L-shaped stub). Output: Transient/pump_pipes/.
Usage: python3 preview_pipes.py
"""
import sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[4]
sys.path.insert(0, str(REPO / "src" / "RimMandrake" / "Utils" / "art"))
import scale_panel  # noqa: E402

TEX = REPO / "src/RimMandrake/FlowWorks/Textures"
OUT = REPO / "Transient/pump_pipes"
P = 64
W, H = 20, 5

ATLAS = Image.open(TEX / "RimMandrake/FlowWorks/Pipe/Scrapper/UniversalPipe_Atlas.png").convert("RGBA")
PUMP = Image.open(TEX / "Things/Building/FlowWorks/Machinery/RM_LiquidPump.png").convert("RGBA")
TANK = Image.open(TEX / "RimMandrake/FlowWorks/Tank/Scrapper/RM_LiquidTank.png").convert("RGBA")
STRAND = Image.open(TEX / "RimMandrake/FlowWorks/Hose/Strand_Plump.png").convert("RGBA")
COUPLING = Image.open(TEX / "RimMandrake/FlowWorks/Hose/Coupling_Bare.png").convert("RGBA")

UP, RIGHT, DOWN, LEFT = 1, 2, 4, 8   # LinkDirections; image y grows DOWN, so "up" = smaller y


def tile(links):
    """MaterialAtlasPool.SubMaterialFromAtlas: tile (i%4, i//4) from the bottom-left, inner 0.1875 of each 0.25 block."""
    t = ATLAS.width / 4
    x, y = links % 4, links // 4
    left, top = x * t + t / 8, (3 - y) * t + t / 8
    return ATLAS.crop((round(left), round(top), round(left + t * 0.75), round(top + t * 0.75))).resize((P, P), Image.LANCZOS)


def centre_stub(cx, cz, dx, dz, bx, bz, bw, bh):
    """LiquidJoinRule.CentreStub, in image cell units (z = image row)."""
    nx, nz = cx + dx, cz + dz
    if not (bx <= nx < bx + bw and bz <= nz < bz + bh):
        return None
    ex, ez = cx + 0.5 + dx * 0.5, cz + 0.5 + dz * 0.5
    mx, mz = bx + bw / 2, bz + bh / 2
    kx, kz = (mx if dx else ex), (mz if dz else ez)
    return [(ex, ez), (kx, kz), (mx, mz)] if (kx, kz) != (mx, mz) else [(ex, ez), (mx, mz)]


def stub_pieces(poly):
    out = []
    for (ax, az), (bx, bz) in zip(poly, poly[1:]):
        ln = abs(bx - ax) + abs(bz - az)
        if ln < 1e-9:
            continue
        ew = abs(bz - az) < 1e-9
        ux, uz = (bx - ax) / ln, (bz - az) / ln
        done = 0.0
        while done < ln - 1e-9:
            l = min(1.0, ln - done)
            mid = done + l / 2
            out.append((ax + ux * mid, az + uz * mid, l, 0.5 - l / 2, 0.5 + l / 2, ew))
            done += l
    return out


def paste_centered(canvas, img, x, y):
    canvas.alpha_composite(img, (round(x - img.width / 2), round(y - img.height / 2)))


def draw_pipe_stub(canvas, poly):
    for x, z, l, u0, u1, ew in stub_pieces(poly):
        t = tile(LEFT | RIGHT if ew else UP | DOWN)
        if ew:
            piece = t.crop((round(u0 * P), 0, round(u1 * P), P))
        else:
            piece = t.crop((0, round(u0 * P), P, round(u1 * P)))
        paste_centered(canvas, piece, x * P, z * P)


def hose_seg(canvas, a, b, width=0.48):
    """A straight hose ribbon from a to b (cell units), the plump strand tiled along it."""
    (ax, az), (bx, bz) = a, b
    ln = abs(bx - ax) + abs(bz - az)
    if ln <= 0:
        return
    wpx = round(width * P)
    strip_len = round(ln * P)
    tile_w = round(STRAND.width * wpx / STRAND.height)
    s = STRAND.resize((tile_w, wpx), Image.LANCZOS)
    strip = Image.new("RGBA", (strip_len, wpx))
    for x in range(0, strip_len, tile_w):
        strip.alpha_composite(s, (x, 0))
    if abs(bz - az) > 1e-9:
        strip = strip.rotate(90, expand=True)
    paste_centered(canvas, strip, (ax + bx) / 2 * P, (az + bz) / 2 * P)


def coupling(canvas, edge, d, size=1.2):
    """Coupling_Bare at a port: face (+X of the art, 0.46 canvas) on the shared edge, pointing along d."""
    c = COUPLING.resize((round(size * P), round(size * P)), Image.LANCZOS)
    ang = {(1, 0): 0, (0, -1): 90, (-1, 0): 180, (0, 1): 270}[d]
    c = c.rotate(ang, expand=False, resample=Image.BICUBIC)
    paste_centered(canvas, c, (edge[0] - d[0] * 0.46 * size) * P, (edge[1] - d[1] * 0.46 * size) * P)


def render(under=True):
    img = Image.new("RGBA", (W * P, H * P), (152, 128, 96, 255))
    g = ImageDraw.Draw(img)
    for i in range(W + 1):
        g.line([(i * P, 0), (i * P, H * P)], fill=(140, 117, 87, 255))
    for j in range(H + 1):
        g.line([(0, j * P), (W * P, j * P)], fill=(140, 117, 87, 255))

    pumps = [(2, 2), (6, 2), (10, 2)]
    tanks = [(15, 2, 2, 2)]
    blds = [(x, z, 1, 1) for x, z in pumps] + tanks
    pipes = {(0, 2), (1, 2), (8, 2), (9, 2), (13, 3), (14, 3)}
    # hoses: (cells of the run, end cell, side toward the building)
    hoses = [([(6, 4.5), (6, 3)], (6, 3), (0, -1)), ([(13, 2), (11, 2)], (11, 2), (-1, 0))]

    def partner(c):
        for b in blds:
            if b[0] <= c[0] < b[0] + b[2] and b[1] <= c[1] < b[1] + b[3]:
                return b
        return None

    # 1. under-building stubs (pipe altitude / hose band: both below Building)
    if under:
        for (cx, cz) in pipes:
            for dx, dz in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                b = partner((cx + dx, cz + dz))
                if b:
                    draw_pipe_stub(img, centre_stub(cx, cz, dx, dz, *b))
        for _, (ex, ez), (dx, dz) in hoses:
            b = partner((ex + dx, ez + dz))
            poly = centre_stub(ex, ez, dx, dz, *b)
            for a, c in zip(poly, poly[1:]):
                hose_seg(img, a, c)
    # 2. pipe cells, linking to pipes and into partners (pipeLinksIntoMachines)
    for (cx, cz) in pipes:
        links = 0
        for bit, (dx, dz) in ((UP, (0, -1)), (RIGHT, (1, 0)), (DOWN, (0, 1)), (LEFT, (-1, 0))):
            n = (cx + dx, cz + dz)
            if n in pipes or partner(n):
                links |= bit
        img.alpha_composite(tile(links), (cx * P, cz * P))
    # 3. hoses and their couplings at the shared edge
    for run, (ex, ez), (dx, dz) in hoses:
        (ax, az), (bx, bz) = run
        # the run reaches the shared edge (in game the coupling + binding wrap cover end-cell centre -> edge)
        hose_seg(img, (ax + 0.5, az + 0.5), (bx + 0.5 + dx * 0.5, bz + 0.5 + dz * 0.5))
        coupling(img, (ex + 0.5 + dx * 0.5, ez + 0.5 + dz * 0.5), (dx, dz))
    # 4. buildings on top
    pu = PUMP.resize((P, P), Image.LANCZOS)
    for x, z in pumps:
        img.alpha_composite(pu, (x * P, z * P))
    for x, z, w, h in tanks:
        img.alpha_composite(TANK.resize((w * P, h * P), Image.LANCZOS), (x * P, z * P))
    # 5. a vanilla colonist, standing in cell (18, 2)
    hum, m, hoff = scale_panel.human_sprite(P)
    img.alpha_composite(hum, (round(18.5 * P - hum.width / 2), round(2.5 * P + m / 2 - hum.height)))
    return img


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    on, off = render(True), render(False)
    try:
        font = ImageFont.truetype("DejaVuSans.ttf", 13)
    except OSError:
        font = ImageFont.load_default()
    labels = [(2.5, "pump + pipe (W)"), (6.5, "pump + hose (S)"), (10.5, "pump + pipe W, hose E"), (16, "2x2 tank + pipe"), (18.5, "colonist")]
    sheet = Image.new("RGBA", (W * P, 2 * H * P + 60), (36, 36, 36, 255))
    sheet.alpha_composite(on, (0, 22))
    sheet.alpha_composite(off, (0, H * P + 52))
    d = ImageDraw.Draw(sheet)
    d.text((6, 4), "TRUE SCALE 64 px/cell - pipes/hoses run on beneath to the centre (setting ON, shipped default)", fill="white", font=font)
    d.text((6, H * P + 34), "same scene, setting OFF (runs stop at the building edge)", fill="white", font=font)
    for x, t in labels:
        d.text((x * P - 40, 22 + 4), t, fill=(255, 255, 255, 255), font=font)
    sheet.save(OUT / "pump_pipes_truescale.png")
    z = on.crop((0, P, 18 * P, 5 * P))
    z = z.resize((z.width * 2, z.height * 2), Image.NEAREST)
    z.save(OUT / "pump_pipes_zoom2x.png")
    print(OUT / "pump_pipes_truescale.png")
    print(OUT / "pump_pipes_zoom2x.png")


if __name__ == "__main__":
    main()
