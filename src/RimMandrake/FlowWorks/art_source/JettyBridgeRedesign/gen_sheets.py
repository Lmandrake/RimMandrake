"""Sheets for the GENERATED options: each beside the procedural geometry it was built on, east/west and north/south, close
zoom (128 px per cell, a vanilla colonist at the same scale) and default zoom (40 px per cell), on the warm dark-brown page
the owner prefers. One uncompressed PNG per kind, an overview sheet of every option at default zoom (the four looks side
by side), and one judge picture per option. RIMMANDRAKE_REDESIGN_JETTY_AND_BRIDGE_ART_STEEL_ONE_READS_AS_WOOD.

    python3 gen_sheets.py OUTDIR [kind ...]      kinds: steel_jetty heavy_jetty bridge_<look> heavy_bridge overview judge"""
import os
import sys

from PIL import Image, ImageDraw, ImageFont

import gen_prompts as GP
import gen_render as G

CLOSE, DEFAULT = 128, 40
BG = (44, 33, 25)
PANEL = (60, 46, 35)
INK = (240, 228, 210)
MUTED = (196, 176, 150)
ACCENT = (230, 176, 96)
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

KINDS = {
    "steel_jetty": ("Steel jetty (station 59): generated options", ["steel_jetty_B", "steel_jetty_C"]),
    "heavy_jetty": ("Heavy jetty (station 60): generated options", ["heavy_jetty_A", "heavy_jetty_B"]),
    "bridge_scrapper": ("Steel bridge, Scrapper look (station 61): generated options", ["bridge_Scrapper_A", "bridge_Scrapper_C"]),
    "bridge_industrial": ("Steel bridge, Industrial look (station 62): generated options",
                          ["bridge_Industrial_A", "bridge_Industrial_C"]),
    "bridge_modern": ("Steel bridge, Modern look (station 63): generated options", ["bridge_Modern_A", "bridge_Modern_B"]),
    "bridge_futuristic": ("Steel bridge, Futuristic look (station 64): generated options",
                          ["bridge_Futuristic_A", "bridge_Futuristic_B"]),
    "heavy_bridge": ("Heavy truss bridge (stations 54-55): generated options", ["heavy_bridge_A", "heavy_bridge_B"]),
}


def font(n, bold=False):
    return ImageFont.truetype(BOLD if bold else FONT, n)


def caption(img, text, size=22, col=INK):
    out = Image.new("RGBA", (img.width, img.height + size + 14), BG + (255,))
    out.paste(img, (0, 0))
    ImageDraw.Draw(out).text((4, img.height + 5), text, font=font(size), fill=col)
    return out


def hstack(ims, gap=20):
    out = Image.new("RGBA", (sum(i.width for i in ims) + gap * (len(ims) - 1), max(i.height for i in ims)), BG + (255,))
    x = 0
    for i in ims:
        out.paste(i, (x, 0))
        x += i.width + gap
    return out


def vstack(ims, gap=20):
    out = Image.new("RGBA", (max(i.width for i in ims), sum(i.height for i in ims) + gap * (len(ims) - 1)), BG + (255,))
    y = 0
    for i in ims:
        out.paste(i, (0, y))
        y += i.height + gap
    return out


def wrap(text, f, width):
    lines, cur = [], ""
    for w in text.split():
        t = (cur + " " + w).strip()
        if cur and f.getlength(t) > width:
            lines.append(cur)
            cur = w
        else:
            cur = t
    return lines + ([cur] if cur else [])


def head(width, title, sub, big=40):
    width = max(width, 900)
    lines = wrap(sub, font(20), width - 10) if sub else []
    im = Image.new("RGBA", (width, big + 20 + 26 * len(lines)), BG + (255,))
    d = ImageDraw.Draw(im)
    d.text((0, 0), title, font=font(big, True), fill=ACCENT if big < 40 else INK)
    for i, ln in enumerate(lines):
        d.text((2, big + 12 + 26 * i), ln, font=font(20), fill=MUTED)
    return im


def page(body, title, sub):
    top = head(body.width, title, sub, 44)
    inner = vstack([top, body], 26)
    out = Image.new("RGBA", (inner.width + 60, inner.height + 60), BG + (255,))
    out.paste(inner, (30, 30))
    return out.convert("RGB")


def is_jetty(key):
    return "jetty" in key


def views(key, ppc, generated=True, human=False):
    """[(label, image)] for one option at one zoom."""
    if is_jetty(key):
        return [("east, 2 squares" + (", colonist on the tip" if human else ""), G.jetty(key, "E", 2, ppc, human, generated)),
                ("west, 1 square", G.jetty(key, "W", 1, ppc, False, generated)),
                ("north, 2 squares" + (", colonist on the tip" if human else ""), G.jetty(key, "N", 2, ppc, human, generated)),
                ("south, 1 square", G.jetty(key, "S", 1, ppc, False, generated))]
    return [("east/west" + (", colonist mid-span" if human else ""), G.bridge(key, False, ppc, human, generated)),
            ("north/south" + (", colonist mid-span" if human else ""), G.bridge(key, True, ppc, human, generated))]


def option_block(key):
    kind, opt, look, _, _ = GP.DECKS[key]
    name, text, spec = G.spec_for(key)
    gen_close = views(key, CLOSE, True, True)
    geo_close = views(key, CLOSE, False, True)
    if is_jetty(key):
        close = [caption(gen_close[0][1], "GENERATED " + gen_close[0][0]),
                 caption(geo_close[0][1], "geometry it was built on (procedural)", col=MUTED),
                 caption(gen_close[2][1], "GENERATED " + gen_close[2][0]),
                 caption(gen_close[3][1], "GENERATED " + gen_close[3][0])]
        row1 = hstack([vstack(close[:2]), close[2], vstack([close[3], caption(gen_close[1][1], "GENERATED " + gen_close[1][0])])])
    else:
        row1 = hstack([vstack([caption(gen_close[0][1], "GENERATED " + gen_close[0][0]),
                               caption(geo_close[0][1], "geometry it was built on (procedural)", col=MUTED)]),
                       caption(gen_close[1][1], "GENERATED " + gen_close[1][0]),
                       caption(geo_close[1][1], "geometry, north/south", col=MUTED)])
    small = [caption(im, lab.split(",")[0] + ", default zoom", 16) for lab, im in views(key, DEFAULT, True, False)]
    small_geo = [caption(im, "geometry", 16, MUTED) for lab, im in views(key, DEFAULT, False, False)[:1]]
    row2 = hstack(small + small_geo, 14)
    title = "Option %s: %s  (%s finish, generated)" % (opt, name, look)
    return vstack([head(row1.width, title, text, 30), row1, row2], 16)


def kind_sheet(kind):
    title, keys = KINDS[kind]
    body = vstack([option_block(k) for k in keys], 60)
    sub = ("Close zoom 128 px per cell with a vanilla colonist at the same scale; default zoom 40 px per cell. Over the real "
           "pit from the 2026-11-22 walk. Generated deck, posts and cables; the geometry beside it is the procedural option "
           "it was built on. Nothing is installed in the mod.")
    return page(body, title, sub)


def overview():
    """Every generated option at default zoom, east/west and north/south: the four looks of the steel bridge side by side."""
    rows = []
    for kind, (title, keys) in KINDS.items():
        cells = []
        for k in keys:
            v = views(k, DEFAULT, True, False)
            pics = [v[0][1], v[2][1]] if is_jetty(k) else [v[0][1], v[1][1]]
            opt = GP.DECKS[k][1]
            cells.append(caption(hstack(pics, 10), "%s: %s" % (opt, G.spec_for(k)[0]), 18))
        rows.append(vstack([head(10, title.split(":")[0], "", 26), hstack(cells, 40)], 8))
    looks = vstack(rows[2:6], 30)
    jet = vstack(rows[:2] + rows[6:], 30)
    body = hstack([jet, looks], 80)
    return page(body, "Jetties and bridges: every generated option at default zoom",
                "40 px per cell, east/west and north/south. Right column: the steel bridge in the four looks, top to bottom "
                "Scrapper, Industrial, Modern, Futuristic. Each kind has its own sheet with close zoom and the geometry.")


def judge_pic(key):
    v = views(key, CLOSE, True, True)
    d = views(key, DEFAULT, True, False)
    if is_jetty(key):
        top = hstack([v[0][1], v[2][1]])
        bot = hstack([x[1] for x in d], 10)
    else:
        top = hstack([v[0][1], v[1][1]])
        bot = hstack([x[1] for x in d], 10)
    return vstack([top, bot]).convert("RGB")


def main(argv):
    out = argv[1]
    os.makedirs(out, exist_ok=True)
    kinds = argv[2:] or list(KINDS) + ["overview"]
    for k in kinds:
        if k == "overview":
            overview().save(os.path.join(out, "overview_generated.png"), compress_level=0)
        elif k == "judge":
            os.makedirs(os.path.join(out, "judge"), exist_ok=True)
            for key in GP.DECKS:
                judge_pic(key).save(os.path.join(out, "judge", key + ".png"))
        else:
            kind_sheet(k).save(os.path.join(out, k + "_generated.png"), compress_level=0)
        print("wrote", k)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
