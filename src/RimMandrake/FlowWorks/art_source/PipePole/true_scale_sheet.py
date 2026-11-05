"""True-scale judging sheet for the pipe-pole looks (PIPE_POLE_REDRAW_NOT_A_POWER_POLE).

  python3 src/RimMandrake/FlowWorks/art_source/PipePole/true_scale_sheet.py OUT.png

One row per look at 64 px a cell: the OLD stand-in (the tinted GSS power mast) at left for contrast, then two new pipe poles
4 cells apart joined by the look's PipeSpan strand, and a vanilla colonist (scale_panel.human_sprite) between them. Placement
follows the game: the pole texture is drawSize (2,4) at drawOffset z 1.5 (it covers z -0.5..3.5 about its cell centre); the
span runs seat to seat at the def's attachZ, spanWidth cells wide, its strip tiled 4:1 as GSS maps it, and is drawn OVER the
poles because GSS draws spans at PawnState +5, above buildings and above any top overlay (+4). The span is drawn straight
(GSS's pipe sag, a Mod Setting, is not modelled here). The colonist stands on the cell row between the poles.
"""
import os
import sys

from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", "..", "..", ".."))
sys.path.insert(0, os.path.join(REPO, "src", "RimMandrake", "Utils", "art"))
FW = os.path.join(REPO, "src", "RimMandrake", "FlowWorks", "Textures", "RimMandrake", "FlowWorks", "PipePole")
GSS = os.path.join(REPO, "src", "RimMandrake", "GimmeSomeSlack", "Textures", "RimMandrake", "GimmeSomeSlack", "Aerial", "Styles")
LOOKS = ("Scrapper", "Industrial", "Modern", "Futuristic")
PPC = 64
ATTACH_Z, SPAN_W = 2.66, 0.14
OLD_TINT = (170, 182, 196)
COLS, ROW_CELLS = 9, 5            # cells per row: old mast at x=0, poles at x=3 and x=7, colonist at x=5


def tex(path, cells_w, cells_h, tint=None):
    im = Image.open(path).convert("RGBA").resize((round(cells_w * PPC), round(cells_h * PPC)), Image.LANCZOS)
    if tint:
        r, g, b, a = im.split()
        r = r.point(lambda v: v * tint[0] // 255)
        g = g.point(lambda v: v * tint[1] // 255)
        b = b.point(lambda v: v * tint[2] // 255)
        im = Image.merge("RGBA", (r, g, b, a))
    return im


def row(look, human):
    W, H = COLS * PPC, ROW_CELLS * PPC
    img = Image.new("RGBA", (W, H), (122, 104, 80, 255))
    d = ImageDraw.Draw(img)
    for x in range(COLS):
        for y in range(ROW_CELLS):
            d.rectangle([x * PPC, y * PPC, (x + 1) * PPC - 1, (y + 1) * PPC - 1], outline=(110, 94, 72, 255))
    base_cz = 0.5                                              # cell-centre z of the ground row, in cells from the bottom

    def Y(z):                                                  # z in cells above the bottom edge -> image row
        return round(H - z * PPC)

    def put(im, cx, z_top):
        img.alpha_composite(im, (round(cx * PPC - im.size[0] / 2), Y(z_top)))

    put(tex(os.path.join(GSS, look, "AerialMast.png"), 2, 4, OLD_TINT), 0.5 + 0.5, base_cz + 1.5 + 2)
    pole = tex(os.path.join(FW, look, "PipePole.png"), 2, 4)
    xa, xb = 3.5, 7.5
    for cx in (xa, xb):
        put(pole, cx, base_cz + 1.5 + 2)
    hum, m, hoff = human
    img.alpha_composite(hum, (round(5.5 * PPC - m / 2), Y(base_cz + 0.75) - hoff))
    # span: the look's strip, spanWidth tall, tiled every 4 x spanWidth along its length, drawn over the poles
    sh = round(SPAN_W * PPC)
    tile = Image.open(os.path.join(FW, look, "PipeSpan.png")).convert("RGBA").resize((4 * sh, sh), Image.LANCZOS)
    L = round((xb - xa) * PPC)
    strip = Image.new("RGBA", (L, sh))
    for x0 in range(0, L, tile.size[0]):
        strip.alpha_composite(tile, (x0, 0))
    seat = Y(base_cz + ATTACH_Z)
    img.alpha_composite(strip, (round(xa * PPC), seat - sh // 2))
    d.text((4, 4), look + "  (left: old stand-in, the tinted GSS power mast)", fill=(255, 255, 255, 255))
    return img


def main(out):
    from scale_panel import human_sprite
    human = human_sprite(PPC)
    rows = [row(l, human) for l in LOOKS]
    sheet = Image.new("RGBA", (rows[0].size[0], sum(r.size[1] for r in rows) + 8 * len(rows)), (40, 40, 40, 255))
    y = 0
    for r in rows:
        sheet.alpha_composite(r, (0, y))
        y += r.size[1] + 8
    sheet.save(out)
    print("wrote", out, sheet.size)


if __name__ == "__main__":
    main(sys.argv[1])
