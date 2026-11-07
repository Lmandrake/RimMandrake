"""Every baked mark on real wall tiles at play zoom, every material: the art judged the way a player sees it, without the game.
usage: gallery_sim.py <baked_dir> <out_prefix>"""
import os, sys
import numpy as np
from PIL import Image, ImageDraw
import manifest as MF, wallsim as S, wallgeom as G

H = 0.8


def hand(i):
    return dict(slope=[-.03, .02, 0, .05, -.05][i % 5], lift=[.5, .2, .8, .4, .6][i % 5])


def run(baked, prefix):
    names = [n for n in MF.M if os.path.exists(f"{baked}/{n}.png")]
    stuffs = ["granite_bricks", "steel_smooth", "wood_planks", "slate_bricks", "marble_bricks"]
    rows, cur, x = [], [], 1
    for n in names:
        w = int(np.ceil(MF.M[n]["width"]))
        if x + w + 1 > 26:
            rows.append(cur); cur, x = [], 1
        cur.append((n, x)); x += w + 1
    rows.append(cur)
    out = []
    for r, row in enumerate(rows):
        stuff = stuffs[r % len(stuffs)]
        sc = S.Scene({(i, 2) for i in range(0, 27)}, 27, 3, stuff=stuff, floor=["concrete", "wood", "dirt"][r % 3])
        for j, (n, x) in enumerate(row):
            m = MF.M[n]
            t = Image.open(f"{baked}/{n}.png").convert("RGBA")
            if m["pigmented"]:
                pig = [(.74, .27, .2), (.82, .6, .27), (.92, .9, .83), (.2, .19, .19), (.42, .52, .33), (.36, .48, .58)][j % 6]
                a = np.asarray(t).astype(float)
                a[..., :3] *= pig
                t = Image.fromarray(a.astype(np.uint8), "RGBA")
            through = 0 if m["mode"] == "scratch" else .18
            sc.mark(t, (x + int(np.ceil(m["width"])) // 2, 2), G.FRONT, H, m["width"], 1.2 * min(1, m["height"]), through=through, **hand(j))
        im = sc.image().crop((0, 0, 27 * 64, 96))
        d = ImageDraw.Draw(im)
        for n, x in row:
            d.text((x * 64 + 2, 72), n, fill=(230, 230, 200))
        out.append(im)
    sheet = Image.new("RGB", (27 * 64, sum(i.height + 2 for i in out)))
    y = 0
    for i in out:
        sheet.paste(i, (0, y)); y += i.height + 2
    sheet.save(prefix + "_gallery.png")
    print(sheet.size)


if __name__ == "__main__":
    run(sys.argv[1], sys.argv[2])
