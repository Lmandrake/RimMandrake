#!/usr/bin/env python3
"""Tricky configurations gallery for the nodal cord model (design §8.7): 08_tricky_*.png.

    python3 nodal.py --tricky --out <dir> [--seed 1] [--ss 2]

Each scene is plain data (scene.mini) and goes through exactly the same reduce -> plan -> lay path
as the main 07 scene; nothing here is special-cased for the picture.
"""
import os
import sys

from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import nodal  # noqa: E402
import render  # noqa: E402
from scene import mini  # noqa: E402


def downed_scene():
    """A wall along row 1. Live: F5 junction -> F2 -> INTO the wall at F1, and the conduit ENDS inside
    the wall (F1, G1): a wall terminal on a live net. Dead: J2..J3 + J1, K1 inside the wall, on no net.
    G6..G8: an unfinished 3-cell spur (live terminal). H5 | gap I5 | J5: a paired gap, heater dead."""
    wall = [(x, 3) for x in range(1, 13)]
    conduit = [(x, 7) for x in range(3, 8)] + [(5, 6), (5, 5), (5, 4), (5, 3), (6, 3)] + \
        [(9, 5), (9, 4), (9, 3), (10, 3)] + [(6, 8), (6, 9), (6, 10)] + [(9, 7), (10, 7)]
    sh = lambda cs: [(x, y - 2) for x, y in cs]  # noqa: E731  (drawn two rows up: no empty sky)
    return mini(sh(conduit), 14, 10, name="downed", walls=sh(wall), indoor=[],
                machines=[{"id": "gen", "kind": "generator", "x": 1, "y": 4, "w": 2, "h": 2, "hookup": (3, 5),
                           "source": True},
                          {"id": "heat", "kind": "heater", "x": 11, "y": 5, "w": 1, "h": 1, "hookup": (10, 5)}],
                trees=[], items=[])


DOWNED_KEY = ["F1: conduit runs into the wall and ENDS inside it on a live net: the cord hangs out of a scorched hole, "
              "spark-dripping like a downed line",
              "J1: the same on a dead net: it hangs still.   G6..G8: unfinished spur (live terminal: whips + sparks)   "
              "H5|I5|J5: a gap (live end H5, dead end J5)"]


def under_scene():
    """A rock mass the conduit tunnels under (holes on both faces), a lake it runs under (the cord dives
    in and comes out), and a 3x3 powered machine sitting ON its conduit (the cord goes INTO the machine,
    through a power strip at its base)."""
    rock = [(x, y) for x in range(6, 12) for y in range(2, 10) if not (x in (6, 11) and y in (2, 9))]
    water = [(x, y) for x in range(15, 19) for y in range(7, 12) if not (x == 18 and y == 11)]
    conduit = [(x, 5) for x in range(3, 15)] + [(14, y) for y in range(6, 10)] + [(x, 9) for x in range(15, 20)] + \
        [(19, 10)] + [(14, 4), (14, 3), (14, 2)] + [(x, 2) for x in range(15, 20)]
    return mini(conduit, 22, 13, name="under", rock=rock, water=water,
                machines=[{"id": "gen", "kind": "generator", "x": 1, "y": 4, "w": 2, "h": 2, "hookup": (3, 5),
                           "source": True},
                          {"id": "drill", "kind": "bigmachine", "x": 15, "y": 1, "w": 3, "h": 3, "hookup": (16, 2)},
                          {"id": "heat", "kind": "heater", "x": 20, "y": 2, "w": 1, "h": 1, "hookup": (19, 2)},
                          {"id": "bench", "kind": "heater", "x": 20, "y": 10, "w": 1, "h": 1, "hookup": (19, 10)}],
                trees=[{"x": 4, "y": 8}], items=[])


UNDER_KEY = ["G2:L9 rock mass: conduit row 5 runs under it; cable holes at F5|G5 and L5|M5, nothing drawn on the rock",
             "P8:S12 deep water: the cord dives in at O9 and comes out at T9 (ripples)   P2:R4 a powered 3x3 machine "
             "standing on its conduit: cords plug into power strips at its base"]


def tangle_scene(power_off=False):
    """A room whose floor is a lattice of conduit (a dense field) with four exits: ONE tangle node."""
    walls = [c for c in _perimeter(1, 1, 16, 10) if c != (8, 10)]
    lattice = [(x, y) for x in range(5, 12) for y in range(3, 8) if x % 2 == 1 or y % 2 == 1]
    lattice += [(6, 4), (8, 6), (10, 4)]                         # a few solid blocks, it was laid badly
    conduit = lattice + [(4, 5), (12, 4), (13, 4), (8, 8), (8, 9), (8, 10), (8, 11), (12, 3)]
    sc = mini(conduit, 18, 13, name="tangle", walls=walls, doors=[(8, 10)], indoor=[(1, 1, 16, 10)],
              machines=[{"id": "gen", "kind": "generator", "x": 2, "y": 4, "w": 2, "h": 2, "hookup": (4, 5),
                         "source": True},
                        {"id": "bench", "kind": "workbench", "x": 14, "y": 4, "w": 2, "h": 3, "hookup": (13, 4)},
                        {"id": "heat", "kind": "heater", "x": 9, "y": 11, "w": 1, "h": 1, "hookup": (8, 11)}],
              lamps=[{"x": 12, "y": 2, "hookup": (12, 3)}], trees=[], items=[])
    if power_off:
        sc["power_off"] = True
    return sc


def _perimeter(x0, y0, x1, y1):
    cells = []
    for x in range(x0, x1 + 1):
        cells += [(x, y0), (x, y1)]
    for y in range(y0 + 1, y1):
        cells += [(x0, y), (x1, y)]
    return cells


def needless_scene():
    """Two lines with needless conduit: a 1-cell spur, a 2-cell spur, a 2x2 block; a zigzag kink, a ring
    (two parallel cords), and -- for contrast -- a 4-cell spur, which is a real terminal."""
    top = [(x, 2) for x in range(2, 18)] + [(5, 1), (9, 1), (9, 0), (12, 3), (13, 3)]
    bot = [(2, 7), (3, 7), (4, 7), (4, 6), (5, 6), (6, 6), (6, 7), (7, 7), (8, 7), (9, 7), (10, 7), (11, 7), (12, 7),
           (13, 7), (13, 6), (14, 6), (15, 6), (15, 7), (13, 8), (14, 8), (15, 8), (16, 7), (17, 7)]
    bot += [(10, 8), (10, 9), (10, 10), (10, 11)]
    return mini(top + bot, 20, 13, name="needless",
                machines=[{"id": "gen", "kind": "generator", "x": 0, "y": 1, "w": 2, "h": 2, "hookup": (2, 2),
                           "source": True},
                          {"id": "h1", "kind": "heater", "x": 18, "y": 2, "w": 1, "h": 1, "hookup": (17, 2)},
                          {"id": "gen2", "kind": "generator", "x": 0, "y": 6, "w": 2, "h": 2, "hookup": (2, 7),
                           "source": True},
                          {"id": "h2", "kind": "heater", "x": 18, "y": 7, "w": 1, "h": 1, "hookup": (17, 7)}],
                trees=[], items=[])


NEEDLESS_KEY = ["Row 2: F1 1-cell spur and J0..J1 2-cell spur -> pointless loops in the cord;  M2:N3 2x2 block -> a "
                "knot (a pointless loop + tape)",
                "Row 7: E6..G6 zigzag -> nothing (degree-2 cells collapse);  N6..P8 ring -> two cords round their own "
                "sides;  K8..K11 4-cell spur -> a real TERMINAL (sparks)"]


def sheet(sc, style, cell, ss, seed, title, sub, keys, frame=0):
    img, _ = nodal.render_nodal(sc, style, "default", cell, ss, seed, frame)
    fr = render.frame_scene(img, sc, title, sub, cell)
    return nodal.key_strip(fr, keys)


def main(a):
    out = a.out
    seed, ss = a.seed, a.ss
    written = []

    def save(img, name):
        p = os.path.join(out, name)
        img.save(p, optimize=True)
        written.append(p)
        print("wrote", p, flush=True)
    thumbs = []
    # 1+2: terminals and the downed wire
    sc = downed_scene()
    full = sheet(sc, "jawa", 110, ss, seed, "Terminals: every conduit end is a node; the cord to it lies broken",
                 "live ends whip and spark; a run that ends INSIDE a wall hangs out of it like a downed line", DOWNED_KEY)
    frames = []
    names = ["drip: sparks fall down the wall face", "FLASH: a burst, the wall lights up", "quiet: an ember",
             "crackle: small burst, a few drips"]
    for f in range(4):
        im, _ = nodal.render_nodal(sc, "jawa", "default", 100, ss, seed, f)
        frames.append(render.label_panel(im.crop((int(3.6 * 100), 0, int(6.6 * 100), int(3.6 * 100))),
                                         f"live wall terminal, frame {f + 1}/4", names[f]))
    im, _ = nodal.render_nodal(sc, "jawa", "default", 100, ss, seed, 1)
    frames.append(render.label_panel(im.crop((int(7.6 * 100), 0, int(10.6 * 100), int(3.6 * 100))),
                                     "dead wall terminal (no net)", "hangs still: soot, dull copper"))
    strip = render.grid(frames, 5)
    body = Image.new("RGB", (max(full.width, strip.width), full.height + strip.height), (22, 17, 13))
    body.paste(full, (0, 0))
    body.paste(strip, (0, full.height))
    img = render.titled(body, "08 tricky: terminals and the downed wire  -  Jawa variant",
                        "owner: 'hangs sparking out of the wall ... a pulsing, flashing, spark-dripping pattern like a "
                        "real downed power line' (in game: irregular, real-time, readable while paused)")
    save(img, "08_tricky_downed_wire.png")
    thumbs.append(full)
    # 3: under impassable areas
    sc = under_scene()
    full = sheet(sc, "jawa", 64, ss, seed, "Conduit under impassable ground: 'it's in there'",
                 "buried conduit is never drawn; stubs where it goes in and comes out, chosen by the conduit itself",
                 UNDER_KEY)
    dbg, _ = nodal.render_debug(sc, seed, 48, ss)
    img = render.titled(render.grid([full, dbg], 1), "08 tricky: under a mountain, a lake and a machine  -  Jawa",
                        "top: the render; bottom: the node graph (rock/water/device stubs, buried edges dashed)")
    save(img, "08_tricky_under_mountain.png")
    thumbs.append(full)
    # 4: dense field -> one tangle
    panels = []
    for off, lab in ((False, "live: power strips lit"), (True, "generator off: strips dark, no sparks")):
        sc = tangle_scene(off)
        im, _ = nodal.render_nodal(sc, "jawa", "default", 64, ss, seed)
        panels.append(render.frame_scene(im, sc, f"Dense conduit field -> ONE tangle  ({lab})",
                                         "a 7x5 lattice = 1 node with 4 exit cords, not ~60 edges", 64))
    dbg, g = nodal.render_debug(tangle_scene(), seed, 48, ss, "the lattice is ONE tangle node.")
    img = render.titled(render.grid(panels + [dbg], 1), "08 tricky: a grid of conduit under the floor  -  Jawa",
                        "owner: 'a huge tangle of nasty wires and power strips all swirled together terribly'")
    save(img, "08_tricky_grid_tangle.png")
    thumbs.append(panels[0])
    # 5: needless conduit
    sc = needless_scene()
    full = sheet(sc, "jawa", 64, ss, seed, "Needless conduit: a pointless loop, not a node",
                 "short spurs and 2x2 blocks on a line become loops/knots in the cord; a long spur is a real terminal",
                 NEEDLESS_KEY)
    dbg, _ = nodal.render_debug(sc, seed, 48, ss, "red X = needless spur cell.")
    img = render.titled(render.grid([full, dbg], 1), "08 tricky: needless conduit  -  Jawa",
                        "owner: 'a needless conduit square along a linear strip (a pointless loop in the wire on the "
                        "ground perhaps)'")
    save(img, "08_tricky_needless_loop.png")
    thumbs.append(full)
    # overview
    tw = 900
    ims = [t.resize((tw, int(t.height * tw / t.width)), Image.LANCZOS) for t in thumbs]
    labs = ["08_tricky_downed_wire", "08_tricky_under_mountain", "08_tricky_grid_tangle", "08_tricky_needless_loop"]
    ims = [render.label_panel(i, n) for i, n in zip(ims, labs)]
    save(render.titled(render.grid(ims, 2), "08 tricky configurations  -  overview (Jawa variant)",
                       "terminals + downed wire | under rock/water/machines | dense field -> one tangle | needless "
                       "conduit -> loops; rules in design §8.7"), "08_tricky_overview.png")
    return written
