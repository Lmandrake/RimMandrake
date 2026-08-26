"""Ship the regenerated Behemoth facings, and correct drawSize for the new framing.

🔴 THE TRAP THIS FILE EXISTS FOR. RimWorld stretches the WHOLE texture across
`drawSize` cells, so a creature's on-screen size is `drawSize * subject/canvas`, not
`drawSize`. The shipping art wasted 47% of its canvas on empty margin; the regenerated
art fills 94%. Dropping the new art in at the old drawSize would render the Behemoth
nearly twice as large again -- a size change nobody asked for, arriving as a side
effect of better framing.

So drawSize is recomputed to hold the on-screen size EXACTLY where it is, and the win
is taken as resolution instead: the same creature, roughly twice the pixels per cell.
"""
import os, re, sys
import numpy as np
from PIL import Image

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
DEST = os.path.join(REPO, "src/Jawa/Jawa_Patches/Textures/Things/Pawn/Animal/FO_ForsakenDragon")
PATCH = os.path.join(REPO, "src/Jawa/Jawa_Patches/Patches/CreatureResize_Ashkarr.xml")
FACINGS = ("south", "north", "east")


def extent(path):
    """Subject height as a fraction of canvas — the number drawSize is really scaled by."""
    a = np.array(Image.open(path).convert("RGBA").getchannel("A"))
    ys, xs = np.nonzero(a > 16)
    return (ys.max() - ys.min() + 1) / a.shape[0], (xs.max() - xs.min() + 1) / a.shape[1]


def main(src_dir, apply=False):
    old = {f: extent(f"{DEST}/FO_ForsakenDragon_{f}.png") for f in FACINGS}
    new = {f: extent(f"{src_dir}/cut_{f}.png") for f in FACINGS}
    # south is the facing the eye judges size by, and the one drawSize was tuned against
    ratio = old["south"][0] / new["south"][0]
    print(f"old south fills {old['south'][0]*100:.0f}% of canvas, new fills {new['south'][0]*100:.0f}%"
          f"  ->  drawSize must scale by {ratio:.3f}")
    cur = [float(m) for m in re.findall(
        r'AA_Behemoth"\]/lifeStages/li\[\d\]/bodyGraphicData/drawSize</xpath>\s*'
        r'<value><drawSize>([\d.]+)</drawSize>', open(PATCH, encoding="utf-8").read())]
    newsizes = [round(c * ratio, 2) for c in cur]
    for c, n in zip(cur, newsizes):
        print(f"  drawSize {c} -> {n}   (on-screen cells unchanged: "
              f"{c*old['south'][0]:.1f} -> {n*new['south'][0]:.1f})")
    for f in FACINGS:
        px = Image.open(f"{src_dir}/cut_{f}.png").convert("RGBA")
        print(f"  {f}: {px.size[0]}px canvas, subject {new[f][1]*100:.0f}x{new[f][0]*100:.0f}% "
              f"-> {px.size[0]*new[f][0]/ (newsizes[-1]*new['south'][0]):.0f} px per cell")
        if apply:
            px.save(f"{DEST}/FO_ForsakenDragon_{f}.png")
    if apply:
        s = open(PATCH, encoding="utf-8").read()
        # match on the literal text, not on a reformatted float: the file writes 26.40
        # and f"{26.4:g}" is "26.4", so a formatted needle silently replaces nothing and
        # only the first of three values moves
        for m, n in zip(re.finditer(r"<value><drawSize>([\d.]+)</drawSize>", s), newsizes):
            s = s.replace(m.group(0), f"<value><drawSize>{n:.2f}</drawSize>", 1)
        open(PATCH, "w", encoding="utf-8").write(s)
        print("WROTE art + drawSize")
    else:
        print("(dry run — pass --apply)")


if __name__ == "__main__":
    a = [x for x in sys.argv[1:] if not x.startswith("--")]
    main(a[0], "--apply" in sys.argv)
