"""Every TILE MUTATOR the stack can draw an icon for, on one sheet.

A `TileMutatorDef` carries NO icon field of its own -- which makes it look, correctly
and misleadingly, like landforms have no art. The icons live in a THIRD def type in a
third mod: Smart Odyssey's `MutatorIconDef` maps mutator defName -> texture path, and
the textures themselves ship with Alpha Biomes. So the answer to "does this landform
have a picture" is never in the landform's own def.

That indirection is the whole reason this file exists.
"""
import glob, os, re, sys

from PIL import Image, ImageDraw, ImageFont

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
WORKSHOP = "/mnt/c/Program Files (x86)/Steam/steamapps/workshop/content/294100"
ICON_DEFS = f"{WORKSHOP}/3522762411/1.6/Defs/MutatorIconDef/MutatorIconDef.xml"


def mapping():
    s = open(ICON_DEFS, encoding="utf-8").read()
    out = {}
    for m in re.finditer(r"<mutator>(.*?)</mutator>\s*<icon>(.*?)</icon>", s, re.S):
        out[m.group(1).strip()] = m.group(2).strip()
    return out


def index():
    idx = {}
    for root in (WORKSHOP, "/mnt/c/Program Files (x86)/Steam/steamapps/common/RimWorld/Mods"):
        for sub in ("UI/Icons/AB_MutatorIcons", "UI/Icons/AB_Landmarks", "World/Landmarks"):
            for p in glob.glob(f"{root}/*/Textures/{sub}/*.png"):
                idx.setdefault(p.split("/Textures/", 1)[1][:-4].lower(), p)
    return idx


def build(out_png, prefix=None, cols=10, cell=104):
    mp, idx = mapping(), index()
    names = sorted(n for n in mp if not prefix or n.startswith(prefix))
    pad, lbl = 6, 26
    rows = (len(names) + cols - 1) // cols
    W = cols * (cell + pad) + pad
    H = rows * (cell + lbl + pad) + pad + 30
    sheet = Image.new("RGB", (W, H), (58, 60, 56))
    d = ImageDraw.Draw(sheet)
    try:
        f = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 10)
        fb = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 14)
    except OSError:
        f = fb = ImageFont.load_default()
    d.text((pad, 8), f"Tile mutators with icons — {len(names)} of {len(mp)} mapped"
                     f"{' · prefix ' + prefix if prefix else ''}", font=fb, fill=(238, 238, 230))
    missing = []
    for i, n in enumerate(names):
        r, c = divmod(i, cols)
        x, y = pad + c * (cell + pad), 30 + pad + r * (cell + lbl + pad)
        p = idx.get(mp[n].lower())
        if p:
            im = Image.open(p).convert("RGBA").resize((cell, cell), Image.LANCZOS)
            bg = Image.new("RGBA", (cell, cell), (150, 150, 150, 255))
            bg.alpha_composite(im)
            sheet.paste(bg.convert("RGB"), (x, y))
        else:
            missing.append(n)
            d.rectangle([x, y, x + cell, y + cell], fill=(90, 40, 40))
        d.text((x, y + cell + 2), n[:20], font=f, fill=(236, 236, 228))
        d.text((x, y + cell + 13), n[20:40], font=f, fill=(236, 236, 228))
    sheet.save(out_png)
    return out_png, names, missing


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    pre = next((a.split("=", 1)[1] for a in sys.argv if a.startswith("--prefix=")), None)
    p, names, missing = build(args[0] if args else "TRANSIENT_mutator_icons.png", pre)
    print(p, len(names), "icons")
    if missing:
        print(f"  {len(missing)} with no texture found:", ", ".join(missing[:12]))
