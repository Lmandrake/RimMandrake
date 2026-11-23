"""Draw the GENERATED options in the same scenes as the procedural ones: the deck from its ROOT / MID / TIP / SOLO tiles,
each post from its generated sprite (rising north from its foot, as the game draws tall things), and each cable, hanger,
A-frame leg and portal beam as a generated texture laid along its run. The geometry (where posts stand, where cables run,
the shadows) is render.py's, unchanged, so a generated option sits on exactly the geometry it was built on.
RIMMANDRAKE_REDESIGN_JETTY_AND_BRIDGE_ART_STEEL_ONE_READS_AS_WOOD."""
import math
import os

import numpy as np
from PIL import Image

import gen_tiles as GT
import render

# generated key -> (post sprite, cable texture); cable textures: gen_prompts.CABLES
PARTS = {
    "steel_jetty_B": ("steel_jetty_B", "galv"),
    "steel_jetty_C": ("steel_jetty_C", "galv"),
    "heavy_jetty_A": ("heavy_jetty_A", "black"),
    "heavy_jetty_B": ("heavy_jetty_B", "black"),
    "bridge_Scrapper_A": ("Scrapper_A", "black"),     # judge: rusty rope-lashed cable read as wood at default zoom
    "bridge_Scrapper_C": ("Scrapper_C", "chain"),
    "bridge_Industrial_A": ("Industrial_A", "black"),
    "bridge_Industrial_C": ("Industrial_C", "black"),
    "bridge_Modern_A": ("Modern_A", "galv"),
    "bridge_Modern_B": ("Modern_B", "galv"),
    "bridge_Futuristic_A": ("Futuristic_A", "cyan"),
    "bridge_Futuristic_B": ("Futuristic_B", "magenta"),
    "heavy_bridge_A": ("heavy_jetty_A", "black"),
    "heavy_bridge_B": ("heavy_jetty_A", "black"),    # judge: steel towers hid the cement -> the concrete pylons
}
# judge repairs (GPT judge, 2026-11-22): steel C's A-frame cables crossed the walkway north/south -> twin lattice masts;
# heavy B's portal crossbeam read as a gate over the walkway -> twin box columns, no beam
GEOM_FIX = {"steel_jetty_C": dict(posts="twin", post_out=0.1), "heavy_jetty_B": dict(posts="twin"),
            "bridge_Futuristic_B": dict(posts="twin", post_inset=0.16), "heavy_bridge_B": dict(posts="twin")}
# the four looks of the steel bridge share one silhouette in the geometry options, so at default zoom they differed only by
# deck surface (GPT four-look judge, 2026-11-22: FAIL; Industrial C ~ Modern A, Industrial A ~ Modern B). Each look gets its
# own structure: Scrapper low and slack, Industrial massive and heavy-cabled, Modern slim and sparse, Futuristic tall and taut.
LOOK_GEOM = {
    "Scrapper": dict(post_h=1.0, sag_low=0.08, hanger_pitch=0.5),
    "Industrial": dict(post_h=1.3, post_w=0.17, cable_w=0.075, sag_low=0.18, hanger_pitch=0.33, hanger_w=0.55),
    "Modern": dict(post_h=1.35, post_w=0.075, cable_w=0.03, sag_low=0.55, hanger_pitch=1.0, hanger_w=0.6),
    "Futuristic": dict(post_h=1.55, post_w=0.1, cable_w=0.035, sag_low=1.0, hanger_pitch=0.25, hanger_w=0.45),
}
GEOM_TEXT = {
    "bridge_Futuristic_B": "Matte graphite deck, magenta edge light, twin slim graphite pylons at each end (the judge's repair: one "
                           "centre pylon ran its cables over the walkway north/south), amber clamp lights.",
    "heavy_bridge_B": "Concrete deck panels between two big riveted steel box girders, twin concrete pylons with steel caps at "
                      "each end (the judge's repair: the portal crossbeam read as a bar over the walkway, and steel towers hid "
                      "the cement), doubled main cables.",
    "bridge_Scrapper_A": "Mismatched salvaged plates, many bare steel-grey, riveted over each other; towers of welded pipe; "
                         "greased steel wire-rope main cables (the judge's repair: brown rope cables read as wood at default "
                         "zoom).",
    "steel_jetty_C": "A narrow ribbed steel gangway between two side trusses; twin lattice masts at the root (the judge's repair of the "
                     "A-frame, whose cables crossed the walkway north/south), a cable from each mast head to its own tip corner.",
    "heavy_jetty_B": "Concrete deck panels between two big riveted steel box girders, twin riveted steel box columns at the root "
                     "(the judge's repair: the portal crossbeam read as a gate over the walkway), doubled cables, a striped "
                     "crash beam at the tip.",
}
CABLE_THICK = {"chain": 1.9, "black": 1.35, "rusty": 1.35}       # texture height over the geometry's cable width

_cache = {}


def _img(path):
    if path not in _cache:
        _cache[path] = Image.open(path).convert("RGBA")
    return _cache[path]


def spec_for(key):
    """The geometry spec of the option this generated key is built on, marked so the hooks draw the generated pieces."""
    name, text, spec = GT.geometry(key)
    post, cable = PARTS[key]
    spec.update(gen=key, gen_post=post, gen_cable=cable, cable_end_h=0.02)     # cables land ON the deck (judge: no midair ends)
    if key.startswith("bridge_"):
        spec.update(LOOK_GEOM[GT.GP.DECKS[key][2]])
    spec.update(GEOM_FIX.get(key, {}))
    text = GEOM_TEXT.get(key, text)
    if key.startswith(("bridge", "heavy_bridge")):
        spec["bridge"] = True
    return name, text, spec


def safe_paste(dst, im, x, y):
    x, y = int(round(x)), int(round(y))
    x0, y0 = max(0, x), max(0, y)
    x1, y1 = min(dst.width, x + im.width), min(dst.height, y + im.height)
    if x1 <= x0 or y1 <= y0:
        return
    dst.alpha_composite(im.crop((x0 - x, y0 - y, x1 - x, y1 - y)), (x0, y0))


def lay_along(dst, tex, a, b, width, upright=False):
    """Lay texture tex along the run a -> b, width px across. A horizontal texture (cables) repeats along the run; an
    upright sprite (posts) is stretched to the run, its top toward b."""
    L = math.dist(a, b)
    if L < 1:
        return
    wpx = max(2, int(round(width)))
    if upright:
        strip = tex.resize((wpx, max(2, int(round(L)))), Image.LANCZOS)
        ang = math.degrees(math.atan2(-(b[0] - a[0]), -(b[1] - a[1])))
    else:
        tw = max(2, int(round(tex.width * wpx / tex.height)))
        t = tex.resize((tw, wpx), Image.LANCZOS)
        n = int(math.ceil(L / tw)) + 1
        row = Image.new("RGBA", (n * tw, wpx), (0, 0, 0, 0))
        for i in range(n):
            row.paste(t, (i * tw, 0))
        strip = row.crop((0, 0, max(2, int(round(L))), wpx))
        ang = math.degrees(math.atan2(-(b[1] - a[1]), b[0] - a[0]))
    rot = strip.rotate(ang, resample=Image.BICUBIC, expand=True)
    mx, my = (a[0] + b[0]) / 2, (a[1] + b[1]) / 2
    safe_paste(dst, rot, mx - rot.width / 2, my - rot.height / 2)


def _tile(key, piece, P):
    im = _img(os.path.join(GT.TILES, "%s_%s.png" % (key, piece)))
    return im if im.width == P else im.resize((P, P), Image.LANCZOS)


def deck(n, look, spec, seed, ends, P):
    key = spec.get("gen")
    if not key:
        return render.deck_image(n, look, spec, seed, ends, P)
    seq = ["solo"] if n == 1 else ["root"] + ["mid"] * (n - 2) + ["tip"]
    out = Image.new("RGBA", (n * P, P), (0, 0, 0, 0))
    for i, p in enumerate(seq):
        out.paste(_tile(key, p, P), (i * P, 0))
    return out


def post(sc, d, base, h, w, look, kind, spec):
    if not spec.get("gen"):
        return render.draw_post(sc, d, base, h, w, look, kind, spec)
    spr = _img(os.path.join(GT.POSTS, spec["gen_post"] + ".png"))
    H = h * sc.P * 1.06                          # the head's saddle sits just above the cable point
    width = min(max(H * spr.width / spr.height, w * 1.1), w * 1.9)
    im = spr.resize((max(2, int(width)), max(2, int(H))), Image.LANCZOS)
    safe_paste(sc.img, im, base[0] - im.width / 2, base[1] - im.height + 0.02 * sc.P)


def leg(sc, d, f, at, pw, look, spec):
    if not spec.get("gen"):
        return render.draw_leg(sc, d, f, at, pw, look, spec)
    lay_along(sc.img, _img(os.path.join(GT.POSTS, spec["gen_post"] + ".png")), f, at, pw * 1.3, upright=True)


def beam(sc, d, t0, t1, pw, look, spec):
    if not spec.get("gen"):
        return render.draw_beam(sc, d, t0, t1, pw, look, spec)
    spr = _img(os.path.join(GT.POSTS, spec["gen_post"] + ".png")).rotate(90, expand=True)
    lay_along(sc.img, spr.crop((int(spr.width * 0.12), 0, int(spr.width * 0.88), spr.height)), t0, t1, pw * 0.9)


def cable(sc, d, p0, h0, p1, h1, w, look, spec, style=None):
    if not spec.get("gen"):
        return render.draw_cable(sc, d, p0, h0, p1, h1, w, look, spec, style)
    key = spec["gen_cable"]
    a, b = sc.scr(p0, h0), sc.scr(p1, h1)
    lay_along(sc.img, _img(os.path.join(GT.CABLES, key + ".png")), a, b, w * CABLE_THICK.get(key, 1.2))
    if h1 <= 0.05:          # a bolted clamp where the cable lands on the deck edge
        r = max(3, w * 0.9)
        d.rounded_rectangle([b[0] - r, b[1] - r, b[0] + r, b[1] + r], radius=r * 0.35, fill=(78, 82, 88), outline=(24, 24, 26),
                            width=max(1, int(r * 0.25)))
        d.ellipse([b[0] - r * 0.35, b[1] - r * 0.35, b[0] + r * 0.35, b[1] + r * 0.35], fill=(150, 154, 160))


render.HOOKS.update(deck=deck, post=post, cable=cable, leg=leg, beam=beam)


def jetty(key, d, n, ppc, human=False, generated=True, seed=5):
    name, text, spec = spec_for(key)
    if not generated:
        spec = GT.geometry(key)[2]          # the procedural option exactly as first drawn
    look = GT.GP.DECKS[key][2]
    return render.jetty(look, spec, seed, d, n, ppc, human=human)


def bridge(key, ns, ppc, human=False, generated=True, seed=5):
    name, text, spec = spec_for(key)
    if not generated:
        spec = GT.geometry(key)[2]          # the procedural option exactly as first drawn
    look = GT.GP.DECKS[key][2]
    return render.bridge(look, spec, seed, ns, ppc, human=human)


if __name__ == "__main__":
    import sys
    out = sys.argv[1] if len(sys.argv) > 1 else "/tmp/jb"
    jetty("steel_jetty_B", "E", 2, 128, human=True).save(os.path.join(out, "t_sjB_E2.png"))
    jetty("heavy_jetty_A", "N", 2, 128, human=True).save(os.path.join(out, "t_hjA_N2.png"))
    bridge("bridge_Scrapper_C", False, 128, human=True).save(os.path.join(out, "t_brSC_EW.png"))
    print("ok")
