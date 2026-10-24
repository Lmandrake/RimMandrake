#!/usr/bin/env python3
"""PIPE_JOINS_REDRAW_RISER_ELBOW_AND_COLLAR: every pipe look x every join, drawn offline by fw_compositor as the game
layers it -- BEFORE (the shipped code, emulated) and AFTER (the proposal), on numbered stations.

Joins per look: straight E-W / N-S, the four corners, the four tees, the cross, the four ends, a lone cell, the universal
tank entered from the west on its lower row and its upper row (the riser), from the east, from the south (no riser), and a
pump entered from the west and the north (machine flange).

BEFORE emulates RM_LiquidJoins.cs as shipped: the pipe's own atlas tile (its arm toward a riser tank cut: a dead-end cap),
the riser as square straights (LiquidJoinRule.RiserStub -> StubPieces) and the Flange sprite on it.
AFTER: the riser cell draws no cap -- the pipe bends in an S (two arcs, the straight tile's cross-section carried round,
LiquidJoinRule.RiserBend) from the cell's far edge (or from the hub when the cell joins other pipes too) onto the tank's
own drawn port, runs on under the nozzle, and no extra Flange is drawn over the nozzle the tank art already has.

Usage: python3 fw_scenes_pipejoins.py [--out DIR] [--px 80]
"""
import argparse
import math
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import fw_compositor as fc  # noqa: E402
from PIL import Image, ImageDraw  # noqa: E402

FLANGE = 0.5          # LiquidJoinRule.FlangeSize
BORE_HALF = 0.12      # strip half-width: the bore is 0.136 cell wide in every look (measured), plus its rim shadow
UNDER_NOZZLE = 0.15   # AFTER: how far the bent pipe runs on past the edge, under the tank's drawn nozzle


def art_insets():
    """TankArtEdges.Table for RM_LiquidTank: look -> [S0,S1,N0,N1,W0,W1,E0,E1] (cells inward from the footprint edge)."""
    src = (fc.FW / "Source/Machinery/TankArtEdges.cs").read_text()
    out = {}
    for m in re.finditer(r"new\[\] \{([^}]*)\},\s*// (\w+) (\w+)", src):
        if m.group(2) == "RM_LiquidTank":
            out[m.group(3)] = [float(v) for v in m.group(1).split(",")]
    return out


INSETS = art_insets()


def drawn_inset(c, d, b):
    if b["def"] != "RM_LiquidTank":
        return 0.0
    lane = c[0] - b["x"] if d[1] != 0 else c[1] - b["z"]
    side = {(0, 1): 0, (0, -1): 2, (1, 0): 4, (-1, 0): 6}[d]
    return INSETS[b["look"]][side + max(0, min(1, lane))]


def flange_on_art(d, inset):
    face = 0.5 + inset
    if face <= -0.5 + 1e-9:
        return None
    c = face - FLANGE / 2
    ang = {(1, 0): 0, (0, 1): 90, (-1, 0): 180, (0, -1): 270}[d]
    return d[0] * c, d[1] * c, ang


def s_bend(x0, z0, x1, z1):
    """Two equal arcs from (x0, z0) heading along x to (x1, z1) heading along x (LiquidJoinRule.RiserBend): path segments."""
    w, h = x1 - x0, z1 - z0
    sx = 1 if w > 0 else -1
    if abs(h) < 1e-6:
        return [("L", x0, z0, x1, z1)]
    th = 2 * math.atan2(abs(h), abs(w))
    r = abs(w) / (2 * math.sin(th))
    sz = 1 if h > 0 else -1
    # first arc: centre beside the start, on the side the bend turns toward
    c1 = (x0, z0 + sz * r)
    heading0 = 0 if sx > 0 else 180
    a0 = heading0 - 90 * sz if sx > 0 else heading0 + 90 * sz
    sweep1 = sz * sx * math.degrees(th)
    mid = (x0 + sx * r * math.sin(th), z0 + sz * r * (1 - math.cos(th)))
    c2 = (x1, z1 - sz * r)
    a2 = math.degrees(math.atan2(mid[1] - c2[1], mid[0] - c2[0]))
    return [("A", c1[0], c1[1], r, a0, sweep1), ("A", c2[0], c2[1], r, a2, -sweep1)]


def draw_net(s, net, mode, under=True, flip_bug=False):
    """Print every pipe cell, stub, flange and partner as the game would (mode 'before' or 'after'; under =
    RM_MachinerySettings.pipesUnderToCentre: the riser's run goes on to the tank's centre, else UNDER_NOZZLE past the edge;
    flip_bug re-creates the review's west-going rim flip, so fw_offline_checks can prove its rim check sees it)."""
    stubs_alt = ("FloorEmplacement", -0.002)
    for b in net.partners:
        s.thing(b["tex"], b["x"], b["z"], size=(b["w"], b["h"]), draw_size=b.get("draw_size"), alt="Building",
                offset=b.get("offset", (0, 0)), meta={"kind": "partner"})
    for c, look in net.pipes.items():
        if net.partner_at(*c) is not None:
            continue   # a pipe under a tank or machine: hidden (the building covers it)
        atlas = fc.pipe_atlas(look)
        straight = fc.atlas_tile(atlas, fc.LEFT | fc.RIGHT)
        mask = fc.link_mask(net, c)
        risers = []
        for (dx, dz) in fc.DIRS.values():
            b = net.partner_at(c[0] + dx, c[1] + dz)
            if b is None:
                continue
            pz = fc.riser_into(net, c, (dx, dz), b)
            if pz is not None:
                risers.append(((dx, dz), b, pz))
        cx, cz = c[0] + 0.5, c[1] + 0.5
        if mode == "after" and risers:
            # RM_LiquidJoins.RiserPlanFor: a cell rising into two tanks keeps its own tile and bends into each from its
            # centre (RiserCount > 1); otherwise the one riser's RiserBend plan
            two = len(risers) > 1
            if two:
                s.plane(fc.atlas_tile(atlas, mask), cx, cz, 1, 1, alt="FloorEmplacement",
                        meta={"kind": "tile", "cell": c, "mask": mask, "riser": True})
            for (dx, dz), b, pz in risers:
                edge = cx + dx * 0.5
                mx = b["x"] + b["w"] / 2.0 if under else edge + dx * UNDER_NOZZLE
                pieces = ([("strip", s_bend(cx, cz, edge, pz) + [("L", edge, pz, mx, pz)])] if two
                          else riser_after(cx, cz, dx, pz, mx, mask, atlas))
                for piece in pieces:
                    if piece[0] == "tile":
                        s.plane(piece[1], cx, cz, 1, 1, alt="FloorEmplacement",
                                meta={"kind": "tile", "cell": c, "mask": piece[2], "riser": True})
                    elif piece[0] == "tile_at":
                        s.plane(piece[1], cx, piece[2], 1, 1, alt="FloorEmplacement", dy=0.0005,
                                meta={"kind": "tile", "cell": c, "mask": piece[3], "riser": True, "fitting": True})
                    else:
                        s.strip(straight, piece[1], half_w=BORE_HALF, alt="FloorEmplacement", dy=0.001,
                                meta={"kind": "strip", "cell": c, "id": len(s.risers), "west": False if flip_bug else None},
                                west=False if flip_bug else None)
                        s.risers.append((c, piece[1]))
        else:
            s.plane(fc.atlas_tile(atlas, mask), cx, cz, 1, 1, alt="FloorEmplacement",
                    meta={"kind": "tile", "cell": c, "mask": mask, "riser": bool(risers)})
        # stubs and flanges toward each cardinal partner (shipped behaviour; AFTER changes only the riser)
        for (dx, dz) in fc.DIRS.values():
            b = net.partner_at(c[0] + dx, c[1] + dz)
            if b is None:
                continue
            pz = fc.riser_into(net, c, (dx, dz), b)
            mx, mz = b["x"] + b["w"] / 2.0, b["z"] + b["h"] / 2.0
            if pz is not None:
                if mode == "before":   # RiserStub with the under-run
                    pts = [(cx, cz), (cx, pz), (cx + dx * 0.5, pz), (mx, pz), (mx, mz)]
                    for (ax, az), (bx_, bz_) in zip(pts, pts[1:]):
                        _stub(s, straight, atlas, ax, az, bx_, bz_, stubs_alt, meta={"kind": "stub", "cell": c})
                    s.risers.append((c, [("L", ax, az, bx_, bz_) for (ax, az), (bx_, bz_) in zip(pts, pts[1:])
                                         if abs(bx_ - ax) + abs(bz_ - az) > 1e-9]))
                    ox, oz, ang = flange_on_art((dx, dz), 0)
                    s.plane(fc.tex("RimMandrake/FlowWorks/Joins/%s/Flange" % look), cx + ox, pz, FLANGE, FLANGE,
                            alt="FloorEmplacement", dy=0.02, rot=-ang, meta={"kind": "flange", "cell": c, "riser": True})
                continue
            # CentreStub (pipesUnderToCentre on): edge -> (bend) -> footprint centre, under the partner
            ex, ez = cx + dx * 0.5, cz + dz * 0.5
            kx, kz = (mx if dx else ex), (mz if dz else ez)
            pts = [(ex, ez)] + ([(kx, kz)] if (abs(kx - mx) > 1e-9 or abs(kz - mz) > 1e-9) else []) + [(mx, mz)]
            for (ax, az), (bx_, bz_) in zip(pts, pts[1:]):
                _stub(s, straight, atlas, ax, az, bx_, bz_, stubs_alt, meta={"kind": "stub", "cell": c})
            f = flange_on_art((dx, dz), drawn_inset(c, (dx, dz), b))
            if f is not None:
                ox, oz, ang = f
                s.plane(fc.tex("RimMandrake/FlowWorks/Joins/%s/Flange" % look), cx + ox, cz + oz, FLANGE, FLANGE,
                        alt="FloorEmplacement", dy=0.02, rot=-ang, meta={"kind": "flange", "cell": c, "riser": False})


ELBOW_R = 0.22


def riser_after(cx, cz, dx, pz, mx, mask, atlas):
    """AFTER: what a riser cell prints -- ('tile', img) and ('strip', path) pieces (LiquidJoinRule.RiserBend's three cases).
    gentle: the cell carries only this run -> one S across the whole cell from its far edge onto the port, no cap.
    fitting: the cell has an arm toward the port's row (the port is on that edge) -> the atlas tee (or elbow, when that
            arm is all the cell has) drawn at the port's height, its arm into the tank running on under the nozzle.
    elbow:  otherwise -> the tile for its links plus a half arm toward the port's row cut where a quarter bend turns it in."""
    away = fc.LEFT if dx > 0 else fc.RIGHT
    mask &= ~(fc.RIGHT if dx > 0 else fc.LEFT)   # a link toward the tank is the riser itself
    sg = 1 if pz > cz else -1
    vert = fc.UP if sg > 0 else fc.DOWN
    edge = cx + dx * 0.5
    run = ("L", edge, pz, mx, pz)
    if mask in (away, 0):
        return [("strip", s_bend(cx - dx * 0.5, cz, edge, pz) + [run])]
    if mask & vert:
        # the port sits on this arm's edge: the junction is a fitting there (the atlas tee/elbow, hub and all) moved to
        # the port's height; the cell keeps its own tile unless the arm toward the port is all it has
        into = fc.RIGHT if dx > 0 else fc.LEFT
        opp = fc.DOWN if vert == fc.UP else fc.UP
        rest = mask & ~vert
        shifted = vert | into | (opp if rest else 0)
        out = [("tile", fc.atlas_tile(atlas, mask), mask)] if rest else []
        return out + [("tile_at", fc.atlas_tile(atlas, shifted), pz, shifted), ("strip", [("L", edge, pz, mx, pz)])]
    tile = fc.atlas_tile(atlas, mask | vert).copy()
    z0 = pz - sg * ELBOW_R                                  # where the bend starts
    H = tile.height
    row = round((cz + 0.5 - z0) * H)                         # image row of z0 (row 0 = the cell's north edge)
    a = tile.getchannel("A")
    from PIL import ImageDraw as _D
    d = _D.Draw(a)
    if sg > 0:
        d.rectangle((0, 0, tile.width, max(0, row) - 1), fill=0)
    else:
        d.rectangle((0, min(H, row), tile.width, H), fill=0)
    tile.putalpha(a)
    ccx, ccz = cx + dx * ELBOW_R, z0
    a0 = 180 if dx > 0 else 0
    arc = ("A", ccx, ccz, ELBOW_R, a0, -dx * sg * 90)
    return [("tile", tile, mask | vert), ("strip", [arc, ("L", ccx, pz, mx, pz)])]


def _stub(s, straight, atlas, ax, az, bx, bz, alt, meta=None):
    """StubPieces: straight tile slices (<= 1 cell) along an axis-aligned leg."""
    ln = abs(bx - ax) + abs(bz - az)
    if ln < 1e-9:
        return
    ew = abs(bz - az) < 1e-9
    tile = straight if ew else fc.atlas_tile(atlas, fc.UP | fc.DOWN)
    W = tile.width
    ux, uz = (bx - ax) / ln, (bz - az) / ln
    done = 0.0
    while done < ln - 1e-9:
        l = min(1.0, ln - done)
        mid = done + l / 2
        u0, u1 = 0.5 - l / 2, 0.5 + l / 2
        piece = tile.crop((round(u0 * W), 0, round(u1 * W), W)) if ew else tile.crop((0, round((1 - u1) * W), W, round((1 - u0) * W)))
        s.plane(piece, ax + ux * mid, az + uz * mid, l if ew else 1, 1 if ew else l, alt=alt[0], dy=alt[1], meta=meta)
        done += l


def pump_tex(look):
    p = "RimMandrake/FlowWorks/Pump/%s/RM_LiquidPump" % look
    return p if (fc.TEX / (p + ".png")).exists() else "Things/Building/FlowWorks/Machinery/RM_LiquidPump"


def look_scene(look, mode, px, flip_bug=False):
    """One look's board, 24 x 10 cells, stations numbered."""
    s = fc.Scene(24, 10, px=px)
    net = fc.PipeNet()
    tank = "RimMandrake/FlowWorks/Tank/%s/RM_LiquidTank" % look
    lt = {"def": "RM_LiquidTank"}
    # 1 the window: a 5x5 ring with a cross through it -> 4 corners, 4 tees, 1 cross
    net.add_pipe([(x, z) for x in range(1, 6) for z in range(2, 7) if x in (1, 3, 5) or z in (2, 4, 6)], look)
    # 2 ends: a free stub out of each side of the ring
    net.add_pipe([(3, 7), (3, 1), (0, 4), (6, 4)], look)
    # 3 straights and a lone cell
    net.add_pipe([(8, 8), (9, 8), (10, 8)], look)
    net.add_pipe([(12, 7), (12, 8), (12, 9)], look)
    net.add_pipe([(14, 9)], look)
    # 4 tank A: a run straight in from the west on the lower row (the owner's shot), east on the upper row, from the south
    net.add_partner(**lt, look=look, x=9, z=2, w=2, h=2, tex=tank)
    net.add_pipe([(7, 2), (8, 2)], look)
    net.add_pipe([(11, 3), (12, 3)], look)
    net.add_pipe([(10, 0), (10, 1)], look)
    # 5 elbows: tank B entered round a corner on its upper row (N+W), tank C on its lower row from the south
    net.add_partner(**lt, look=look, x=17, z=4, w=2, h=2, tex=tank)
    net.add_pipe([(16, 7), (16, 6), (16, 5), (15, 5), (14, 5)], look)
    net.add_partner(**lt, look=look, x=21, z=4, w=2, h=2, tex=tank)
    net.add_pipe([(20, 4), (20, 3), (20, 2)], look)
    # 6 a run passing tank C's east side: both row cells branch into the port on their shared edge
    net.add_pipe([(23, 2), (23, 3), (23, 4), (23, 5), (23, 6), (23, 7)], look)
    # 7 pump: from the west and the north
    net.add_partner(**{"def": "RM_LiquidPump"}, look=look, x=15, z=1, w=1, h=1, tex=pump_tex(look))
    net.add_pipe([(13, 1), (14, 1)], look)
    net.add_pipe([(15, 2), (15, 3)], look)
    draw_net(s, net, mode, flip_bug=flip_bug)
    for x, z, t in [(1, 7.1, "1 window"), (0, 1.4, "2 ends"), (8, 9.7, "3 straights / lone"), (7, 1.5, "4 tank W / E / S"),
                    (14, 8.1, "5 elbows into tank"), (20, 8.1, "6 run past tank"), (13, 0.5, "7 pump")]:
        s.label(x + 0.05, z, t)
    return s


def _grid(cells, head, out, title):
    """Rows x 2 (BEFORE | AFTER) with a numbered header per row."""
    f, ft = fc.font(22), fc.font(28)
    cw = max(c.width for r in cells for c in r)
    ch = max(c.height for r in cells for c in r)
    pad, top, lh = 10, 50, 30
    W = pad + 2 * (cw + pad)
    H = top + len(cells) * (lh + ch + pad)
    sheet = Image.new("RGB", (W, H), (28, 28, 28))
    d = ImageDraw.Draw(sheet)
    d.text((pad, 10), title, fill=(255, 255, 255), font=ft)
    y = top
    for i, (row, h) in enumerate(zip(cells, head), 1):
        for j, (im, tag) in enumerate(zip(row, ("BEFORE (shipped)", "AFTER (proposal)"))):
            x = pad + j * (cw + pad)
            d.text((x, y), "%s.%s  %s - %s" % (i, "ab"[j], h, tag), fill=(255, 230, 120), font=f)
            sheet.paste(im.convert("RGB"), (x, y + lh))
        y += lh + ch + pad
    sheet.save(out)
    return out


def build(out, px):
    out.mkdir(parents=True, exist_ok=True)
    full, detail = [], []
    for look in fc.LOOKS:
        row_f, row_d = [], []
        for mode in ("before", "after"):
            im = look_scene(look, mode, px).render()
            im.save(out / ("pipejoins_%s_%s.png" % (look, mode)))
            row_f.append(im)
            big = look_scene(look, mode, 128).render()
            P = 128
            # stations 4-7 close up: x 6.5..24, z 0.2..7.8 (image rows from the top: z = 10 - row / P)
            row_d.append(big.crop((round(6.5 * P), round((10 - 7.8) * P), 24 * P, round((10 - 0.2) * P))).resize(
                (round(17.5 * P * 0.6), round(7.6 * P * 0.6)), Image.LANCZOS))
        full.append(row_f)
        detail.append(row_d)
    paths = [_grid(full, fc.LOOKS, out / "SHEET_pipejoins_all_looks.png",
                   "PIPE_JOINS_REDRAW_RISER_ELBOW_AND_COLLAR - every join, every look (stations 1-7 on each board)"),
             _grid(detail, fc.LOOKS, out / "SHEET_pipejoins_tank_closeup.png",
                   "Tank entries close up: 4 straight in (W low / E high / S), 5 elbows in, 6 run past, 7 pump")]
    return paths


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="/mnt/d/ClaudeWork/rimmandrake/fw_art_geometry_20261024/pipejoins")
    ap.add_argument("--px", type=int, default=80)
    a = ap.parse_args()
    for p in build(Path(a.out), a.px):
        print(p)
