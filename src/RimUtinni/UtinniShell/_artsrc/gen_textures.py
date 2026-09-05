#!/usr/bin/env python3
"""
RimUtinni Shell — procedural UI texture generator (PROVENANCE, committed).

Authors the RimThemes theme's 9-slice button atlases, the gizmo Command.BGTex,
the loader bar tint swatches and the theme picker icon — all deterministic PIL,
so the pixel-precise symmetric 9-slice geometry a RimWorld atlas needs is under
our control rather than an image model's. (The two big evocative pieces — the
Ishko menu background and the amber tactical loader — are image-gen; see
gen_bg.py.)

Palette from design/Jawa/worldbuilding/ui_shell_spec.md §1, tuned to the refs
(ref1 rust plate + chalk graffiti + LED, ref3 amber tactical).

Vanilla source dims (measured against RimThemes' own consumed Cyberpunk theme,
which mirrors vanilla): ButtonBGAtlas 64x64 RGB, Command.BGTex 75x75,
LoaderBar/TextBar 10x10 RGBA, Misc/Icon 96x96 RGBA. RimWorld's Widgets.DrawAtlas
uses a border of width/4 -> 16 px corners on a 64 px atlas; all bevel/frame work
stays inside that 16 px so the 9-slice quarters line up.

Run:  python3 gen_textures.py            # writes options + ships the default + contact sheet
"""
import os, math, random
from PIL import Image, ImageDraw, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
MOD  = os.path.dirname(HERE)
THEME_TEX = os.path.join(MOD, "RimThemes", "Utinni Shell", "Textures")
THEME_LOADER = os.path.join(MOD, "RimThemes", "Utinni Shell", "Loader")
THEME_MISC = os.path.join(MOD, "RimThemes", "Utinni Shell", "Misc")
OPTDIR = os.path.join(HERE, "options")
for d in (THEME_TEX, THEME_LOADER, THEME_MISC, OPTDIR):
    os.makedirs(d, exist_ok=True)

# ---- palette (RGB 0-255) --------------------------------------------------
GROUND       = (18, 21, 26)
DARK_RUST    = (38, 28, 24)
WARM_RUST    = (74, 44, 30)
BRASS        = (198, 138, 58)
BRASS_HI     = (232, 176, 96)
CHALK        = (150, 160, 175)
CHALK_HI     = (196, 204, 214)
LED_RED      = (196, 72, 54)
BONE         = (222, 214, 200)
GREY_PANEL   = (58, 60, 64)     # recessed grey sub-panel (ref1/ref2)
GREY_PANEL_D = (34, 36, 40)

BORDER = 16  # 9-slice corner size for a 64px atlas (Widgets.DrawAtlas: width/4)

def _n(base, amt, rng):
    return tuple(max(0, min(255, base[i] + rng.randint(-amt, amt))) for i in range(3))

def rusted_plate(size, base, amt, rng, streak=0.0, streak_col=None):
    """Opaque rust-metal fill with pitting + optional vertical streaks."""
    im = Image.new("RGB", (size, size), base)
    px = im.load()
    for y in range(size):
        for x in range(size):
            px[x, y] = _n(base, amt, rng)
    # soft blotches of oxidation
    d = ImageDraw.Draw(im, "RGBA")
    for _ in range(int(size * size * 0.012)):
        cx, cy = rng.randint(0, size - 1), rng.randint(0, size - 1)
        r = rng.randint(1, max(2, size // 12))
        tone = rng.choice([(120, 74, 46), (52, 30, 22), (150, 96, 58)])
        a = rng.randint(20, 70)
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=tone + (a,))
    if streak and streak_col:
        for _ in range(int(size * streak)):
            x = rng.randint(0, size - 1)
            a = rng.randint(15, 45)
            d.line([(x, 0), (x + rng.randint(-2, 2), size)], fill=streak_col + (a,), width=1)
    return im

def bevel(im, hi, sh, depth=BORDER, invert=False, strength=1.0):
    """Draw a symmetric raised (or, if invert, recessed) bevel frame inside `depth` px."""
    size = im.width
    d = ImageDraw.Draw(im, "RGBA")
    top_col, bot_col = (hi, sh) if not invert else (sh, hi)
    for i in range(depth):
        # fade the bevel as it goes inward
        a = int(200 * strength * (1 - i / depth))
        if a <= 0:
            continue
        # top + left = top_col ; bottom + right = bot_col
        d.line([(i, i), (size - 1 - i, i)], fill=top_col + (a,))           # top
        d.line([(i, i), (i, size - 1 - i)], fill=top_col + (a,))           # left
        d.line([(i, size - 1 - i), (size - 1 - i, size - 1 - i)], fill=bot_col + (a,))  # bottom
        d.line([(size - 1 - i, i), (size - 1 - i, size - 1 - i)], fill=bot_col + (a,))  # right
    return im

def chalk_inset(im, col=CHALK, inset=6, jitter=True):
    """A weathered chalk-outline rectangle inset from the edge (ref1 graffiti border)."""
    size = im.width
    d = ImageDraw.Draw(im, "RGBA")
    rng = random.Random(99)
    for pass_i in range(2):
        a = 150 if pass_i == 0 else 90
        w = 2 if pass_i == 0 else 1
        off = inset + (0 if pass_i == 0 else 1)
        pts = [off, off, size - 1 - off, size - 1 - off]
        d.rectangle(pts, outline=col + (a,), width=w)
    if jitter:  # scuff the chalk so it reads hand-drawn, not printed
        px = im.load()
        for _ in range(size * 3):
            x, y = rng.randint(0, size - 1), rng.randint(0, size - 1)
            if rng.random() < 0.3:
                pass
    return im

# ---- three button-atlas style options -------------------------------------
def style_heavy(seed):
    """A: heavy oxidised rust, deep pitted plate, strong dark bevel — grimy."""
    rng = random.Random(seed)
    base = (88, 52, 38)
    bg = rusted_plate(64, base, 26, rng, streak=0.5, streak_col=(30, 16, 12))
    bevel(bg, (140, 92, 62), (34, 20, 14), strength=1.15)
    mo = rusted_plate(64, (96, 58, 42), 24, random.Random(seed + 1), streak=0.4, streak_col=(30, 16, 12))
    bevel(mo, BRASS_HI, (46, 28, 16), strength=1.0)          # brass edge
    ImageDraw.Draw(mo, "RGBA").rectangle([1, 1, 62, 62], outline=BRASS + (230,), width=2)
    cl = rusted_plate(64, (52, 30, 22), 18, random.Random(seed + 2))
    bevel(cl, (24, 14, 10), (96, 60, 40), invert=True, strength=1.1)  # pressed/recessed
    return bg, mo, cl

def style_clean(seed):
    """B: cleaner brushed rust-bronze plate, subtle bevel — most readable."""
    rng = random.Random(seed)
    base = (98, 62, 46)
    bg = rusted_plate(64, base, 12, rng)
    # horizontal brushed sheen
    dd = ImageDraw.Draw(bg, "RGBA")
    for y in range(BORDER, 64 - BORDER, 2):
        dd.line([(BORDER, y), (63 - BORDER, y)], fill=(120, 82, 58, 40))
    bevel(bg, (150, 104, 72), (48, 28, 20), strength=0.85)
    mo = rusted_plate(64, (110, 70, 50), 12, random.Random(seed + 1))
    bevel(mo, BRASS_HI, (52, 32, 20), strength=0.85)
    ImageDraw.Draw(mo, "RGBA").rectangle([1, 1, 62, 62], outline=BRASS + (235,), width=2)
    cl = rusted_plate(64, (64, 40, 30), 10, random.Random(seed + 2))
    bevel(cl, (30, 18, 12), (110, 74, 52), invert=True, strength=0.9)
    return bg, mo, cl

def style_chalk(seed):
    """C: rust plate framed by a chalk-white graffiti outline (ref1 motif)."""
    rng = random.Random(seed)
    base = (84, 50, 38)
    bg = rusted_plate(64, base, 20, rng, streak=0.3, streak_col=(28, 15, 11))
    bevel(bg, (128, 84, 56), (38, 22, 15), strength=0.8)
    chalk_inset(bg, CHALK, inset=7)
    mo = rusted_plate(64, (92, 56, 42), 18, random.Random(seed + 1))
    bevel(mo, BRASS_HI, (44, 26, 16), strength=0.75)
    chalk_inset(mo, CHALK_HI, inset=7)
    ImageDraw.Draw(mo, "RGBA").rectangle([2, 2, 61, 61], outline=BRASS + (210,), width=2)
    cl = rusted_plate(64, (52, 31, 23), 14, random.Random(seed + 2))
    bevel(cl, (26, 15, 11), (92, 58, 40), invert=True, strength=0.85)
    chalk_inset(cl, (110, 118, 130), inset=7)
    return bg, mo, cl

STYLES = {"A_heavy": style_heavy, "B_clean": style_clean, "C_chalk": style_chalk}
DEFAULT_STYLE = "B_clean"  # ship B as default; owner picks from the contact sheet

# ---- 9-slice blit (for the contact sheet's real-size buttons) -------------
def nineslice(atlas, w, h, b=BORDER):
    """Render `atlas` onto a w×h button using 9-slice (corners fixed, edges/center stretched)."""
    s = atlas.width
    out = Image.new("RGB", (w, h))
    regions = [  # (src_box, dst_box)
        ((0, 0, b, b),           (0, 0, b, b)),
        ((s - b, 0, s, b),       (w - b, 0, w, b)),
        ((0, s - b, b, s),       (0, h - b, b, h)),
        ((s - b, s - b, s, s),   (w - b, h - b, w, h)),
        ((b, 0, s - b, b),       (b, 0, w - b, b)),
        ((b, s - b, s - b, s),   (b, h - b, w - b, h)),
        ((0, b, b, s - b),       (0, b, b, h - b)),
        ((s - b, b, s, s - b),   (w - b, b, w, h - b)),
        ((b, b, s - b, s - b),   (b, b, w - b, h - b)),
    ]
    for sb, db in regions:
        piece = atlas.crop(sb).resize((db[2] - db[0], db[3] - db[1]), Image.LANCZOS)
        out.paste(piece, (db[0], db[1]))
    return out

# ---- generate all options + ship the default ------------------------------
def main():
    from PIL import ImageFont
    made = {}
    for name, fn in STYLES.items():
        bg, mo, cl = fn(seed=1000 + hash(name) % 1000)
        od = os.path.join(OPTDIR, name)
        os.makedirs(od, exist_ok=True)
        bg.save(os.path.join(od, "Widgets.ButtonBGAtlas.png"))
        mo.save(os.path.join(od, "Widgets.ButtonBGAtlasMouseover.png"))
        cl.save(os.path.join(od, "Widgets.ButtonBGAtlasClick.png"))
        made[name] = (bg, mo, cl)

    # ship the default style's three atlases into the theme folder
    bg, mo, cl = made[DEFAULT_STYLE]
    bg.save(os.path.join(THEME_TEX, "Widgets.ButtonBGAtlas.png"))
    mo.save(os.path.join(THEME_TEX, "Widgets.ButtonBGAtlasMouseover.png"))
    cl.save(os.path.join(THEME_TEX, "Widgets.ButtonBGAtlasClick.png"))

    # Command.BGTex — recessed grey sub-panel with a chalk outline (75x75, opaque)
    rng = random.Random(7)
    cmd = rusted_plate(75, GREY_PANEL, 8, rng)
    bevel(cmd, (18, 19, 22), (86, 88, 94), depth=14, invert=True, strength=1.0)  # recessed
    chalk_inset(cmd, CHALK, inset=9)
    cmd.save(os.path.join(THEME_TEX, "Command.BGTex.png"))

    # LoaderBar / TextBar — 10x10 brass tint swatches (RGBA), what RimThemes stretches
    for fn_name, col in (("LoaderBar.png", BRASS), ("TextBar.png", BRASS_HI)):
        bar = Image.new("RGBA", (10, 10), col + (255,))
        d = ImageDraw.Draw(bar)
        d.line([(0, 0), (9, 0)], fill=BRASS_HI + (255,))     # top sheen
        d.line([(0, 9), (9, 9)], fill=(120, 80, 34, 255))    # bottom shade
        bar.save(os.path.join(THEME_LOADER, fn_name))

    # Misc/Icon — 96x96 theme picker icon: rust plate, brass ring, LED
    icon = rusted_plate(96, (90, 56, 42), 16, random.Random(3))
    bevel(icon, (150, 104, 72), (40, 24, 16), depth=10, strength=1.0)
    di = ImageDraw.Draw(icon, "RGBA")
    di.ellipse([20, 20, 76, 76], outline=BRASS + (255,), width=4)
    di.ellipse([30, 30, 66, 66], outline=CHALK + (200,), width=2)
    di.ellipse([43, 43, 53, 53], fill=LED_RED + (255,))       # LED
    icon.save(os.path.join(THEME_MISC, "Icon.png"))

    contact_sheet(made)
    print("ships default style:", DEFAULT_STYLE)
    print("wrote atlases, Command.BGTex, LoaderBar/TextBar, Icon, contact sheet")

def contact_sheet(made):
    from PIL import ImageFont
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 16)
        small = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 13)
    except Exception:
        font = small = ImageFont.load_default()
    BW, BH = 190, 42                 # real-ish text-button size
    pad, gap = 26, 18
    col_labels = ["Default", "Mouseover", "Pressed"]
    rows = list(made.items())
    sheet_w = pad * 2 + 3 * BW + 2 * gap + 150
    sheet_h = pad * 2 + 30 + len(rows) * (BH + gap) + 20
    sheet = Image.new("RGB", (sheet_w, sheet_h), GROUND)
    d = ImageDraw.Draw(sheet)
    d.text((pad, 8), "RimUtinni Shell — button atlas options (9-slice on a real-size button)",
           fill=BONE, font=font)
    x0 = pad + 150
    for c, cl in enumerate(col_labels):
        d.text((x0 + c * (BW + gap) + BW // 2 - 30, 30), cl, fill=CHALK, font=small)
    y = pad + 30
    for name, (bg, mo, cl) in rows:
        d.text((pad, y + BH // 2 - 8), name, fill=BRASS, font=font)
        for c, atlas in enumerate((bg, mo, cl)):
            btn = nineslice(atlas, BW, BH)
            bx = x0 + c * (BW + gap)
            sheet.paste(btn, (bx, y))
            # button label text in bone, like a real RimWorld button
            bd = ImageDraw.Draw(sheet)
            lbl = "New Colony"
            tb = bd.textbbox((0, 0), lbl, font=small)
            bd.text((bx + BW // 2 - (tb[2] - tb[0]) // 2, y + BH // 2 - (tb[3] - tb[1]) // 2),
                    lbl, fill=BONE, font=small)
        y += BH + gap
    out = os.path.join(HERE, "button_atlas_contact_sheet.png")
    sheet.save(out)
    print("contact sheet:", out)

if __name__ == "__main__":
    main()
