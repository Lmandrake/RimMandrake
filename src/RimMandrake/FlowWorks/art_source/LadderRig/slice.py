"""slice.py -- LADDER_RAILS_DRAWN_ON_THE_FACE: cut the generated front-view ladders (wood_ladder_v1.png, steel_ladder_v1.png,
rails_v1.png) into the tiles RM_LadderDraw prints: one rung period (seamless top to bottom, rung centred) and the top cap.
python3 slice.py <out dir>"""
import sys
import colorsys
import numpy as np
from PIL import Image

HERE = __file__.rsplit("/", 1)[0]
OUT = sys.argv[1]
W = 160   # px across the ladder in every tile


def rungs(a):
    h, w = a.shape
    col = a[:, w // 2 - 20:w // 2 + 20].mean(axis=1)
    rows = np.where(col > 128)[0]
    runs, s, p = [], None, None
    for r in rows:
        if s is None:
            s = r
        elif r != p + 1:
            runs.append((s + p) / 2)
            s = r
        p = r
    runs.append((s + p) / 2)
    return runs


def tone(im, sat, val):
    a = np.array(im).astype(float) / 255
    rgb = a[:, :, :3]
    mx, mn = rgb.max(axis=2), rgb.min(axis=2)
    grey = (mx + mn) / 2
    rgb = grey[:, :, None] + (rgb - grey[:, :, None]) * sat
    a[:, :, :3] = np.clip(rgb * val, 0, 1)
    return Image.fromarray((a * 255).astype(np.uint8), "RGBA")


def cut(src, name, sat=1.0, val=1.0):
    im = Image.open(src).convert("RGBA")
    a = np.array(im)[:, :, 3].astype(float)
    bb = im.split()[3].getbbox()
    c = rungs(a)
    per = float(np.mean(np.diff(c)))
    mid = c[len(c) // 2]
    x0, x1 = bb[0], bb[2]
    tile = im.crop((x0, int(round(mid - per / 2)), x1, int(round(mid + per / 2))))
    cap = im.crop((x0, 0, x1, int(round(c[0] + per / 2))))
    th = int(round(W * per / (x1 - x0)))
    tile = tone(tile.resize((W, th), Image.LANCZOS), sat, val)
    cap = tone(cap.resize((W, int(round(W * cap.height / (x1 - x0)))), Image.LANCZOS), sat, val)
    tile.save("%s/RM_LadderTile_%s.png" % (OUT, name))
    cap.save("%s/RM_LadderCap_%s.png" % (OUT, name))
    print(name, "period px", round(per, 1), "tile", tile.size, "cap", cap.size, "cap/tile", round(cap.height / tile.height, 3))


cut(HERE + "/wood_ladder_v1.png", "Wood", sat=0.55, val=0.86)
cut(HERE + "/steel_ladder_v1.png", "Steel")


def rails(src, hooks_src, tile_w=200, rail_w=24):
    """The fixed rail pair: one generated rail (rails_v1.png, left rail with its brackets) placed at each edge of a tile_w
    canvas, one bracket period tall; the cap carries the old rig's J hooks (RM_Ladder_north.png) over the rail tops."""
    im = Image.open(src).convert("RGBA")
    a = np.array(im)[:, :, 3]
    cols = np.where((a > 128).sum(axis=0) > 200)[0]
    gap = np.where(np.diff(cols) > 3)[0][0]
    x0, x1 = cols[0], cols[gap]
    w = (a[:, x0:x1 + 1] > 128).sum(axis=1)
    rows = np.where(w > w.min() + 10)[0]
    br, s, p = [], None, None
    for r in rows:
        if s is None:
            s = r
        elif r != p + 1:
            br.append((s + p) / 2)
            s = r
        p = r
    br.append((s + p) / 2)
    per = float(np.mean(np.diff(br)))
    mid = br[len(br) // 2]
    strip = im.crop((x0, int(round(mid - per / 2)), x1 + 1, int(round(mid + per / 2))))
    k = rail_w / strip.width
    th = int(round(strip.height * k))
    strip = strip.resize((rail_w, th), Image.LANCZOS)
    tile = Image.new("RGBA", (tile_w, th), (0, 0, 0, 0))
    tile.alpha_composite(strip, (0, 0))
    tile.alpha_composite(strip.transpose(Image.FLIP_LEFT_RIGHT), (tile_w - rail_w, 0))
    tile.save("%s/RM_LadderRailTile.png" % OUT)
    # the cap: a hook over each rail top, then the rail down to half a period
    old = Image.open(hooks_src).convert("RGBA")
    hook = old.crop((112, 99, 137, 126))          # the old rig's left J hook (384 px canvas, 256 px a cell)
    hook = hook.resize((int(round(hook.width * tile_w / (0.74 * 256))), int(round(hook.height * tile_w / (0.74 * 256)))), Image.LANCZOS)
    upper = strip.crop((0, 0, rail_w, th // 2))
    capH = hook.height - 4 + upper.height
    cap = Image.new("RGBA", (tile_w, capH), (0, 0, 0, 0))
    for x, flip in ((0, False), (tile_w - rail_w, True)):
        u = upper.transpose(Image.FLIP_LEFT_RIGHT) if flip else upper
        cap.alpha_composite(u, (x, capH - u.height))
        h = hook.transpose(Image.FLIP_LEFT_RIGHT) if flip else hook
        hx = x + (rail_w - h.width) // 2 + (3 if flip else -3)
        cap.alpha_composite(h, (max(0, min(tile_w - h.width, hx)), 0))
    cap.save("%s/RM_LadderRailCap.png" % OUT)
    print("rails period px", round(per, 1), "tile", tile.size, "cap", cap.size, "tile aspect", round(th / tile_w, 4),
          "cap aspect", round(capH / tile_w, 4))


rails(HERE + "/rails_v1.png", HERE + "/../../Textures/Things/Building/FlowWorks/Canals/RM_Ladder_north.png")
