"""Build the comparison sheets (one per kind) and the join sheet. Usage: python3 sheets.py OUTDIR [kind ...]
Kinds: join steel_jetty heavy_jetty bridge_scrapper bridge_industrial bridge_modern bridge_futuristic heavy_bridge.
Every scene is the real pit from the owner's 2026-11-22 capture; close zoom 128 px per cell, default zoom 40 px per cell; the
vanilla human (scale_panel.human_sprite) stands on a deck in every close east/west view at the same scale.
RIMMANDRAKE_REDESIGN_JETTY_AND_BRIDGE_ART_STEEL_ONE_READS_AS_WOOD."""
import os
import sys

from PIL import Image, ImageDraw, ImageFont

import render as R
import specs as S

CLOSE, DEFAULT, STRIP = 128, 40, 48
BG = (248, 246, 240)
INK = (30, 30, 30)
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"


def font(n, bold=False):
    return ImageFont.truetype(BOLD if bold else FONT, n)


def caption(img, text, size=22):
    """The picture with a caption bar under it."""
    out = Image.new("RGBA", (img.width, img.height + size + 14), BG + (255,))
    out.paste(img, (0, 0))
    ImageDraw.Draw(out).text((6, img.height + 5), text, font=font(size), fill=INK)
    return out


def hstack(ims, gap=18):
    w = sum(i.width for i in ims) + gap * (len(ims) - 1)
    h = max(i.height for i in ims)
    out = Image.new("RGBA", (w, h), BG + (255,))
    x = 0
    for i in ims:
        out.paste(i, (x, 0))
        x += i.width + gap
    return out


def vstack(ims, gap=18, left=0):
    w = max(i.width for i in ims) + left
    h = sum(i.height for i in ims) + gap * (len(ims) - 1)
    out = Image.new("RGBA", (w, h), BG + (255,))
    y = 0
    for i in ims:
        out.paste(i, (left, y))
        y += i.height + gap
    return out


def titled(body, title, sub):
    head = Image.new("RGBA", (body.width + 40, 120), BG + (255,))
    d = ImageDraw.Draw(head)
    d.text((20, 14), title, font=font(46, True), fill=INK)
    d.text((22, 74), sub, font=font(22), fill=(70, 70, 70))
    out = Image.new("RGBA", (body.width + 40, body.height + 140), BG + (255,))
    out.paste(head, (0, 0))
    out.paste(body, (20, 130))
    return out


def option_head(key, name, text, width):
    im = Image.new("RGBA", (width, 74), BG + (255,))
    d = ImageDraw.Draw(im)
    d.text((0, 4), "Option %s: %s" % (key, name), font=font(32, True), fill=INK)
    d.text((2, 44), text, font=font(20), fill=(60, 60, 60))
    return im


def jetty_sheet(title, opts, look, seed0):
    rows = []
    for i, (key, name, text, spec) in enumerate(opts):
        seed = seed0 + i * 17
        close = [
            caption(R.jetty(look, spec, seed, "E", 2, CLOSE, human=True), "east, 2 squares (a colonist on the tip)"),
            caption(R.jetty(look, spec, seed, "W", 1, CLOSE), "west, 1 square"),
            caption(R.jetty(look, spec, seed, "N", 2, CLOSE), "north, 2 squares"),
            caption(R.jetty(look, spec, seed, "S", 1, CLOSE), "south, 1 square"),
        ]
        dflt = [caption(R.jetty(look, spec, seed, d, n, DEFAULT), "%s %d" % (d, n), 16)
                for d, n in (("E", 2), ("W", 1), ("N", 2), ("S", 1))]
        looks = [caption(R.jetty(lk, spec, seed, "E", 2, STRIP), lk, 16) for lk in ("Scrapper", "Industrial", "Modern", "Futuristic")]
        right = vstack([caption(hstack(dflt[:2], 10), "default zoom", 18), hstack(dflt[2:], 10),
                        caption(hstack(looks[:2], 10), "the same structure in the four looks (east, 2 squares)", 18),
                        hstack(looks[2:], 10)], 12)
        body = hstack([vstack(close[:2], 12)] + close[2:] + [right], 24)
        rows.append(vstack([option_head(key, name, text, body.width), body], 6))
    return titled(vstack(rows, 50), title, "Close zoom 128 px per cell (true scale beside the colonist); shown in the %s look. "
                  "Offline mockups drawn in Python, not generated art. Pick one option per kind." % look)


def bridge_sheet(title, opts, look, seed0):
    rows = []
    for i, (key, name, text, spec) in enumerate(opts):
        seed = seed0 + i * 17
        ew = caption(R.bridge(look, spec, seed, False, CLOSE, human=True), "east/west (a colonist mid-span)")
        ns = caption(R.bridge(look, spec, seed, True, CLOSE), "north/south")
        dflt = vstack([caption(R.bridge(look, spec, seed, False, DEFAULT), "default zoom, east/west", 16),
                       caption(R.bridge(look, spec, seed, True, DEFAULT), "default zoom, north/south", 16)], 10)
        body = hstack([ew, ns, dflt], 24)
        rows.append(vstack([option_head(key, name, text, body.width), body], 6))
    return titled(vstack(rows, 50), title, "Close zoom 128 px per cell (true scale beside the colonist). Offline mockups drawn "
                  "in Python, not generated art. Pick one option.")


def today_jetty(d, n, tier="Steel"):
    """Today's draw: the Scrapper jetty picture once per square (Graphic_Multi), the anchor, the real pit."""
    tex = "../../Textures/RimMandrake/FlowWorks/SuspensionBridge/Scrapper/"
    base = "../../Textures/Things/Building/FlowWorks/SuspensionBridge/"
    rot = {"E": "east", "W": "east", "N": "north", "S": "south"}[d]
    P = CLOSE
    if d in ("E", "W"):
        sc = R.backdrop.scene(6, 5, (1, 1), False, P)
        anc = (0, 2) if d == "E" else (5, 2)
        cells = [(anc[0] + R.DIRS[d][0] * (k + 1), 2) for k in range(n)]
    else:
        sc = R.backdrop.scene(5, 8, (1, 2), True, P)
        anc = (2, 6) if d == "N" else (2, 1)
        cells = [(2, anc[1] + R.DIRS[d][1] * (k + 1)) for k in range(n)]
    name = "RM_SuspensionJetty_Steel_%s.png" % rot if tier == "Steel" else "RM_SuspensionJetty_%s.png" % rot
    j = Image.open(os.path.join(tex, name)).convert("RGBA").resize((P, P), Image.LANCZOS)
    if d == "W":
        j = j.transpose(Image.FLIP_LEFT_RIGHT)
    a = Image.open(os.path.join(base, "RM_SuspensionAnchor_Steel_%s.png" % rot)).convert("RGBA").resize((P, P), Image.LANCZOS)
    if d == "W":
        a = a.transpose(Image.FLIP_LEFT_RIGHT)
    sc.alpha_composite(a, (anc[0] * P, anc[1] * P))
    for c in cells:
        sc.alpha_composite(j, (c[0] * P, c[1] * P))
    return sc


def mark_cells(img, cells, P, labels):
    """Dashed cell boundaries and piece names over a picture (the join diagram)."""
    im = img.copy()
    d = ImageDraw.Draw(im)
    for (c, r), lab in zip(cells, labels):
        x0, y0 = c * P, r * P
        for k in range(0, P, 12):
            for (a, b) in (((x0 + k, y0), (x0 + k + 6, y0)), ((x0 + k, y0 + P), (x0 + k + 6, y0 + P)),
                           ((x0, y0 + k), (x0, y0 + k + 6)), ((x0 + P, y0 + k), (x0 + P, y0 + k + 6))):
                d.line([a, b], fill=(255, 230, 80), width=2)
        d.rectangle([x0 + 4, y0 + P - 30, x0 + 8 + 13 * len(lab), y0 + P - 6], fill=(20, 20, 20))
        d.text((x0 + 7, y0 + P - 29), lab, font=font(18, True), fill=(255, 230, 80))
    return im


def join_sheet():
    P = CLOSE
    spec = S.STEEL_JETTY[0][3]
    today = [caption(today_jetty("E", 2), "TODAY east: one framed picture per square"),
             caption(today_jetty("N", 2), "TODAY north")]
    new_e = R.jetty("Industrial", spec, 5, "E", 2, P)
    new_n = R.jetty("Industrial", spec, 5, "N", 2, P)
    new_e1 = R.jetty("Industrial", spec, 5, "E", 1, P)
    new = [caption(mark_cells(new_e, [(1, 2), (2, 2)], P, ["ROOT", "TIP"]), "NEW east: one strip cut into root + tip"),
           caption(mark_cells(new_n, [(2, 5), (2, 4)], P, ["ROOT", "TIP"]), "NEW north"),
           caption(mark_cells(new_e1, [(1, 2)], P, ["SOLO"]), "NEW east, 1 square: the solo piece")]
    body = vstack([hstack(today, 24), hstack(new, 24)], 40)
    return titled(body, "Why a jetty reads as two squares, and the join",
                  "Top: today's Scrapper steel jetty, drawn from the mod's own textures. Bottom: the redesign (steel jetty option "
                  "A, Industrial look); dashed yellow lines are the cell edges, which the picture no longer shows.")


SHEETS = {
    "join": join_sheet,
    "steel_jetty": lambda: jetty_sheet("Steel jetty (station 59): three options", S.STEEL_JETTY, "Industrial", 101),
    "heavy_jetty": lambda: jetty_sheet("Heavy jetty (station 60): three options", S.HEAVY_JETTY, "Industrial", 201),
    "bridge_scrapper": lambda: bridge_sheet("Steel bridge, Scrapper look (station 61): three options", S.BRIDGE["Scrapper"], "Scrapper", 301),
    "bridge_industrial": lambda: bridge_sheet("Steel bridge, Industrial look (station 62): three options", S.BRIDGE["Industrial"], "Industrial", 401),
    "bridge_modern": lambda: bridge_sheet("Steel bridge, Modern look (station 63): three options", S.BRIDGE["Modern"], "Modern", 501),
    "bridge_futuristic": lambda: bridge_sheet("Steel bridge, Futuristic look (station 64): three options", S.BRIDGE["Futuristic"], "Futuristic", 601),
    "heavy_bridge": lambda: bridge_sheet("Heavy truss bridge (stations 54-55): three options", S.HEAVY_BRIDGE, "Industrial", 701),
}


if __name__ == "__main__":
    out = sys.argv[1]
    os.makedirs(out, exist_ok=True)
    for k in (sys.argv[2:] or list(SHEETS)):
        im = SHEETS[k]()
        p = os.path.join(out, "%s.png" % k)
        im.convert("RGB").save(p, optimize=True)
        print(p, im.size)
