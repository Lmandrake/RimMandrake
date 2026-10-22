#!/usr/bin/env python3
"""PIPE_FITTINGS_REDRAW_NO_MORE_LADDERS (owner card 2026-10-22 "Draft all of it").

1. CONFORM each artpipe master pipefitraw_<piece>_<look>_v1 (1024, top-down) to the live atlas scale:
   176 px per cell, pipe band 18 px (0.102 cell). Every piece is scaled so its stub girth equals the atlas pipe;
   the result is clamped to the study sizes (cross/tee body <= 0.26 cell, coupling 0.135, end cap 0.11-0.12).
   -> cand/<Look>_<Piece>.png (piece on its own, real alpha)
2. COMPOSE a DRAFT UniversalPipe_Atlas per look (704 x 704, same 4x4 tile layout as the live one):
   * body = the live straight tile with every coupling band painted out (each band column replaced by the nearest
     clean column), so the look's own pipe texture stays;
   * ONE coupling per joint: half a coupling at every linked tile edge, so two neighbouring cells make one;
   * 3 links -> the Tee hub, 4 links -> the Cross hub, 1 link -> the look's End cap, 0 links -> a capped stub;
   * corners -> an elbow bent from the clean body profile (radius half a cell, as the live atlas).
   -> draft/<Look>/UniversalPipe_Atlas.png, plus comp/<Look>_layout.png (a test layout drawn from the draft atlas
      the way Graphic_Linked tiles it) and comp/<Look>_live_layout.png (the same layout from the LIVE atlas).
3. PUMPS: pumplook_<look>_v1 (512) -> cand/<Look>_Pump.png (trimmed, re-centred, same fill as the live pump).
    python3 compose.py
"""
import json
import math
import os
import sys
from pathlib import Path

from PIL import Image

H = Path(__file__).resolve().parent
REPO = H.parents[2]
SRC = Path("/mnt/d/ClaudeWork/rimmandrake/artpipe/_artsrc")
LOOKS = ["Scrapper", "Industrial", "Modern", "Futuristic"]
ATLAS = REPO / "src/RimMandrake/FlowWorks/Textures/RimMandrake/FlowWorks/Pipe/{look}/UniversalPipe_Atlas.png"
LIVE_PUMP = REPO / "src/RimMandrake/FlowWorks/Textures/Things/Building/FlowWorks/Machinery/RM_LiquidPump.png"
T = 176          # px per atlas tile = per cell
C = T // 2
GIRTH = 18       # live pipe band, px (rows 79-96 of every look's straight tile)
TOP = 79
MAXC = {"Cross": 0.26, "Tee": 0.26, "Coupling": 0.135, "EndCap": 0.12}   # cells, joints study D9/D11
# owner card 2026-10-22 (pipe atlases A-D): "redraw the END CAPS ~1.5x bolder in each look first (draft caps vanish at play
# zoom)" -> every end cap is conformed 1.5x larger (scale, collar threshold and clamp), from the 1024 master, not upscaled
CAP_BOLD = 1.5


def trim(im):
    bb = im.split()[3].point(lambda v: 255 if v > 24 else 0).getbbox()
    return im.crop(bb)


def fit(im, w, h):
    return im.convert("RGBa").resize((max(1, round(w)), max(1, round(h))), Image.LANCZOS).convert("RGBA")


def stub_girth(t, side):
    """Opaque run (px) through the stub at 3% in from the given side ('left' / 'right' / 'bottom')."""
    a = t.split()[3]
    if side in ("left", "right"):
        x = max(2, round(t.width * 0.03)) if side == "left" else t.width - 1 - max(2, round(t.width * 0.03))
        rows = [y for y in range(t.height) if a.getpixel((x, y)) > 128]
        return (rows[-1] - rows[0] + 1, (rows[0] + rows[-1]) / 2) if rows else (0, 0)
    y = t.height - 1 - max(2, round(t.height * 0.03))
    cols = [x for x in range(t.width) if a.getpixel((x, y)) > 128]
    return (cols[-1] - cols[0] + 1, (cols[0] + cols[-1]) / 2) if cols else (0, 0)


def conform_piece(piece, look):
    src = SRC / f"pipefitraw_{piece.lower()}_{look.lower()}_v1" / f"pipefitraw_{piece.lower()}_{look.lower()}_v1.png"
    if not src.is_file():
        return None, {"missing": str(src)}
    t = trim(Image.open(src).convert("RGBA"))
    g, mid = stub_girth(t, "left")
    if piece == "Tee":   # its stem points down: the bottom stub is also a stub
        g = (g + stub_girth(t, "bottom")[0]) / 2
    k = GIRTH / g
    bold = CAP_BOLD if piece == "EndCap" else 1.0
    k *= bold
    if piece in ("Cross", "Tee"):
        k = min(k, MAXC[piece] * T / min(t.width, t.height) * 2.6)   # never let the hub body run past ~0.26 cell
    s = fit(t, t.width * k, t.height * k)
    if piece in ("Cross", "Tee"):
        # pad to a square whose centre is the junction (left stub's centre row x bottom stub's centre column),
        # so placing/rotating about the image centre puts every stub on the atlas pipe's centreline
        jy = stub_girth(s, "left")[1]
        jx = stub_girth(s, "bottom")[1]
        half = math.ceil(max(jx, s.width - jx, jy, s.height - jy)) + 1
        sq = Image.new("RGBA", (2 * half, 2 * half), (0, 0, 0, 0))
        sq.alpha_composite(s, (round(half - jx), round(half - jy)))
        s = sq
    info = {"master": str(src), "stub_px": g, "scale": round(k, 4), "w_cells": round(s.width / T, 3), "h_cells": round(s.height / T, 3)}
    if piece in ("Coupling", "EndCap"):
        # keep only the collar/cap columns (taller than 1.15x the pipe) + 2 px; the atlas body draws the pipe itself
        a = s.split()[3]
        tall = [x for x in range(s.width) if sum(1 for y in range(s.height) if a.getpixel((x, y)) > 128) > 1.15 * GIRTH * bold]
        if tall:
            s = s.crop((max(0, tall[0] - 2), 0, min(s.width, tall[-1] + 3), s.height))
        if s.height > MAXC[piece] * T * 1.15 * bold:               # clamp an over-tall collar to the study size
            k2 = MAXC[piece] * bold * T / s.height
            s = fit(s, s.width * k2, s.height * k2)
            info["clamped"] = round(k2, 3)
        info.update(w_cells=round(s.width / T, 3), h_cells=round(s.height / T, 3))
    s = clean(s)
    out = H / "cand" / f"{look}_{piece}.png"
    s.save(out)
    return s, info


def clean(im):
    px = im.load()
    for y in range(im.height):
        for x in range(im.width):
            if px[x, y][3] < 8:
                px[x, y] = (0, 0, 0, 0)
    return im


def body_strip(look):
    """The live straight east-west tile with every band painted out: a 176 x 176 tile, pipe rows TOP..TOP+GIRTH."""
    a = Image.open(str(ATLAS).format(look=look)).convert("RGBA")
    st = a.crop((2 * T, T, 3 * T, 2 * T))
    px = st.load()
    lo, hi = TOP - 3, TOP + GIRTH + 3
    prof = [[px[x, y] for y in range(lo, hi)] for x in range(T)]
    # a band column differs from the median column; median per row over all columns
    med = []
    for i in range(hi - lo):
        vals = sorted(prof[x][i] for x in range(T))
        med.append(vals[len(vals) // 2])

    def dist(col):
        return sum(sum(abs(col[i][c] - med[i][c]) for c in range(4)) for i in range(len(col))) / len(col)
    d = [dist(prof[x]) for x in range(T)]
    srt = sorted(d)
    thr = max(srt[len(srt) // 2] * 2.2, 18)
    bad = [v > thr for v in d]
    good = [x for x in range(T) if not bad[x]]
    out = st.copy()
    op = out.load()
    for x in range(T):
        if bad[x]:
            src = min(good, key=lambda g: abs(g - x))
            for y in range(T):
                op[x, y] = px[src, y]
    # median profile column (for elbows): rows lo..hi
    return out, med, lo, sum(bad)


def elbow(med, lo, corner):
    """A quarter-circle elbow of radius C around the given tile corner ('UR','RD','DL','LU' = the two linked sides)."""
    cx = T if "R" in corner else 0
    cy = 0 if "U" in corner else T
    im = Image.new("RGBA", (T, T), (0, 0, 0, 0))
    p = im.load()
    n = len(med)
    for y in range(T):
        for x in range(T):
            r = math.hypot(x + 0.5 - cx, y + 0.5 - cy)
            off = r - C + (TOP - lo) + GIRTH / 2 - 0.5     # distance across the pipe -> profile index
            i = int(round(off))
            if 0 <= i < n:
                p[x, y] = med[i]
    return im


def rot(im, k):
    """Rotate counter-clockwise by k quarter turns."""
    return im.rotate(90 * k, expand=False) if k % 4 else im


def tile_links(tx, ty):
    return {"U": bool(tx & 1), "R": bool(tx & 2), "L": ty in (0, 1), "D": ty in (0, 2)}


def paste_c(dst, im, cx, cy):
    dst.alpha_composite(im, (round(cx - im.width / 2), round(cy - im.height / 2)))


def compose(look, pieces):
    body, med, lo, nbad = body_strip(look)
    horiz = body                                  # full east-west body
    half_r = body.crop((C, 0, T, T))              # centre -> east edge
    atlas = Image.new("RGBA", (4 * T, 4 * T), (0, 0, 0, 0))
    ang = {"R": 0, "U": 1, "L": 2, "D": 3}        # CCW quarter turns that take an east-pointing piece to that side
    cpl = pieces.get("Coupling")
    for ty in range(4):
        for tx in range(4):
            ln = tile_links(tx, ty)
            S = [k for k in "URDL" if ln[k]]
            tile = Image.new("RGBA", (T, T), (0, 0, 0, 0))
            if set(S) == {"L", "R"}:
                tile.alpha_composite(horiz)
            elif set(S) == {"U", "D"}:
                tile.alpha_composite(rot(horiz, 1))
            elif len(S) == 2:
                corner = "".join(S) if "".join(S) in ("UR", "RD") else ("DL" if set(S) == {"D", "L"} else "LU")
                tile.alpha_composite(elbow(med, lo, corner))
            else:
                for k in S:
                    arm = Image.new("RGBA", (T, T), (0, 0, 0, 0))
                    arm.alpha_composite(half_r, (C, 0))
                    tile.alpha_composite(rot(arm, ang[k]))
                if len(S) == 4 and pieces.get("Cross"):
                    paste_c(tile, pieces["Cross"], C, TOP + GIRTH / 2)
                elif len(S) == 3 and pieces.get("Tee"):
                    missing = [k for k in "URDL" if k not in S][0]
                    # the Tee master has its closed side UP; turn it so the closed side faces the missing link
                    paste_c(tile, rot(pieces["Tee"], ang[missing] - ang["U"]), C, TOP + GIRTH / 2)
                elif len(S) == 1 and pieces.get("EndCap"):
                    away = {"U": "D", "D": "U", "L": "R", "R": "L"}[S[0]]
                    cap = rot(pieces["EndCap"], ang[away])
                    dx = {"R": 1, "L": -1}.get(away, 0)
                    dy = {"D": 1, "U": -1}.get(away, 0)
                    paste_c(tile, cap, C + dx * cap.width / 2, TOP + GIRTH / 2 + dy * cap.height / 2)
                elif len(S) == 0 and pieces.get("EndCap"):
                    stub = body.crop((C - 26, 0, C + 26, T))
                    tile.alpha_composite(stub, (C - 26, 0))
                    cap = pieces["EndCap"]
                    paste_c(tile, cap, C + 26 + cap.width / 2 - 2, TOP + GIRTH / 2)
                    paste_c(tile, rot(cap, 2), C - 26 - cap.width / 2 + 2, TOP + GIRTH / 2)
            if cpl is not None:                       # one coupling per joint: half at every linked edge
                for k in S:
                    c = cpl if k in "LR" else rot(cpl, 1)
                    ex = {"R": T, "L": 0}.get(k, C)
                    ey = {"U": 0, "D": T}.get(k, TOP + GIRTH / 2)
                    paste_c(tile, c, ex, ey)
            atlas.alpha_composite(tile, (tx * T, ty * T))
    od = H / "draft" / look
    od.mkdir(parents=True, exist_ok=True)
    clean(atlas).save(od / "UniversalPipe_Atlas.png")
    return atlas, nbad


# a test layout: (x, y) cells; drawn with the atlas the way Graphic_Linked picks a tile from the 4 neighbours
LAYOUT = {(x, 3) for x in range(0, 9)} | {(4, y) for y in range(0, 7)} | {(8, y) for y in range(3, 7)} | \
         {(x, 6) for x in range(5, 8)} | {(1, y) for y in range(3, 6)} | {(6, 0)} | {(x, 1) for x in range(6, 9)}


def layout(atlas, ppc=88):
    xs = [p[0] for p in LAYOUT]
    ys = [p[1] for p in LAYOUT]
    w, h = max(xs) + 1, max(ys) + 1
    im = Image.new("RGBA", (w * ppc, h * ppc), (122, 104, 84, 255))
    for (x, y) in LAYOUT:
        U, R, D, L = (x, y - 1) in LAYOUT, (x + 1, y) in LAYOUT, (x, y + 1) in LAYOUT, (x - 1, y) in LAYOUT
        tx = (1 if U else 0) | (2 if R else 0)
        ty = {(True, True): 0, (False, True): 1, (True, False): 2, (False, False): 3}[(D, L)]
        tile = atlas.crop((tx * T, ty * T, (tx + 1) * T, (ty + 1) * T)).resize((ppc, ppc), Image.LANCZOS)
        im.alpha_composite(tile, (x * ppc, y * ppc))
    return im


def pump(look):
    src = SRC / f"pumplook_{look.lower()}_v1" / f"pumplook_{look.lower()}_v1.png"
    if not src.is_file():
        return None
    live = Image.open(LIVE_PUMP).convert("RGBA")
    lb = live.split()[3].point(lambda v: 255 if v > 24 else 0).getbbox()
    t = trim(Image.open(src).convert("RGBA"))
    k = min((lb[2] - lb[0]) / t.width, (lb[3] - lb[1]) / t.height)
    s = fit(t, t.width * k, t.height * k)
    c = Image.new("RGBA", live.size, (0, 0, 0, 0))
    c.alpha_composite(s, (round((lb[0] + lb[2]) / 2 - s.width / 2), round((lb[1] + lb[3]) / 2 - s.height / 2)))
    clean(c).save(H / "cand" / f"{look}_Pump.png")
    return {"master": str(src), "fill_box_live": lb, "canvas": live.size}


if __name__ == "__main__":
    for d in ("cand", "comp", "draft"):
        (H / d).mkdir(exist_ok=True)
    sizes = {}
    for look in LOOKS:
        pieces = {}
        for piece in ("Cross", "Tee", "Coupling", "EndCap"):
            im, info = conform_piece(piece, look)
            sizes[f"{look}_{piece}"] = info
            if im is not None:
                pieces[piece] = im
        if len(pieces) == 4:
            atlas, nbad = compose(look, pieces)
            sizes[f"{look}_atlas"] = {"band_columns_painted_out": nbad}
            layout(atlas).save(H / "comp" / f"{look}_layout.png")
            live = Image.open(str(ATLAS).format(look=look)).convert("RGBA")
            layout(live).save(H / "comp" / f"{look}_live_layout.png")
        if look != "Scrapper":
            sizes[f"{look}_Pump"] = pump(look)
    (H / "sizes.json").write_text(json.dumps(sizes, indent=1, default=str))
    print(json.dumps({k: v for k, v in sizes.items()}, default=str)[:3000])
