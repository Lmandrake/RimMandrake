"""Topology library: small, well-defined power-grid scenes as plain JSON-able dicts (format mc_scene/1).

Coordinates are scene cells (x east, y SOUTH = image rows), the same convention as the Python mock-up
(src/RimMandrake/Utils/mockups/messy_conduit/scene.py). placer.py maps them to game (x, z) with north up.

A scene:
  {"format": "mc_scene/1", "name", "topology", "w", "h",
   "conduit": [[x,y]...], "walls", "doors", "rock", "water", "trees": [[x,y]...],
   "devices": [{"id", "role", "x", "y", "w", "h", "hookup": [x,y] | None, "charged", "active", "on"}],
   "aerial": None | {"poles": [[x,y]...], "spans": [[i,j]...], "cut": [span index...]},
   "hose":   None | {"cells": [[x,y]...], "inflation": "flat" | "plump"},
   "break_cell": [x,y] | None,       # a conduit cell deliberately NOT built (the break axis)
   "notes": [...]}

Device roles and their live-game realization (DEVICE_DEFS; sizes/comps read from the 1.6 defs via RimSage,
2026-10-02): transmitter roles (battery, generator, switch) are wired by the game to EVERY cardinally adjacent
conduit cell, exactly as CordWorldAdapter does; connector roles (consumer, bench, lamp) connect to the single
nearest wire-able transmitter (PowerConnectionMaker.BestTransmitterForConnector), so `hookup` must be that
cell -- lint() emulates the game's rule and refuses an ambiguous or wrong hookup.

Adding a topology: write `def t_<name>()` returning a Canvas whose west entry cell is (0, entry_y) and add it
to TOPOLOGIES. compose() supplies the feeder (density), the source battery, the break cell, aerial and hose.
"""
import math

DIRS4 = [(1, 0), (-1, 0), (0, 1), (0, -1)]

# role -> realization. walkable: the pathgrid stays walkable on the footprint (PassThroughOnly/Standable), so the
# C# adapter does NOT bury conduit under it (the Python mock-up blocks every machine cell; oracle.py corrects that).
DEVICE_DEFS = {
    "battery": {"def": "Battery", "size": (1, 2), "transmitter": True, "wire_parent": True, "walkable": True,
                "type": "battery", "src": "RimSage Battery: size (1,2), CompProperties_Battery transmitsPower, PassThroughOnly"},
    "generator": {"def": "WoodFiredGenerator", "size": (2, 2), "transmitter": True, "wire_parent": True,
                  "walkable": True, "type": "source",
                  "src": "RimSage WoodFiredGenerator: size (2,2), CompPowerPlant transmitsPower, Refuelable, PassThroughOnly"},
    "switch": {"def": "PowerSwitch", "size": (1, 1), "transmitter": True, "wire_parent": False, "walkable": True,
               "type": "transmitter", "src": "RimSage PowerSwitch: CompPowerTransmitter, allowWireConnection false, Standable"},
    "consumer": {"def": "Heater", "size": (1, 1), "transmitter": False, "walkable": True, "type": "consumer",
                 "src": "RimSage Heater: CompPowerTrader, default size, PassThroughOnly"},
    "bench": {"def": "ElectricSmelter", "size": (3, 1), "transmitter": False, "walkable": True, "type": "consumer",
              "src": "RimSage ElectricSmelter: size (3,1), CompPowerTrader, PassThroughOnly"},
    "lamp": {"def": "StandingLamp", "size": (1, 1), "transmitter": False, "walkable": True, "type": "lamp",
             "live_type": "consumer", "src": "StandingLamp, proven 1x1 by validation.py LAMP; adapter emits Consumer"},
}
TOPOLOGY_ORDER = ["line", "l_chain", "tee", "cross4", "ring", "lattice2", "lattice3", "lattice5", "mesh", "star",
                  "spur", "spur_blob", "gap", "multinet", "device_attached", "doorway", "wall_entry", "rock_entry",
                  "under_building", "canal", "long_run"]


class Canvas(object):
    def __init__(self, name):
        self.name = name
        self.cells = []
        self.devices = []
        self.walls, self.doors, self.rock, self.water, self.trees = [], [], [], [], []
        self.entry_y = 0
        self.notes = []
        self.intended_dense = False      # a lattice: dense fields here are on purpose
        self.extra_break = []            # cells inside the topology deliberately left out (the gap topology)

    def run(self, pts):
        for p in pts:
            p = tuple(p)
            if p not in self.cells:
                self.cells.append(p)
        return pts[-1]

    def line(self, a, b):
        (x0, y0), (x1, y1) = a, b
        if x0 == x1:
            s = 1 if y1 >= y0 else -1
            return self.run([(x0, y) for y in range(y0, y1 + s, s)])
        s = 1 if x1 >= x0 else -1
        return self.run([(x, y0) for x in range(x0, x1 + s, s)])

    def dev(self, did, role, x, y, hookup=None, **kw):
        w, h = DEVICE_DEFS[role]["size"]
        d = {"id": did, "role": role, "x": x, "y": y, "w": w, "h": h,
             "hookup": list(hookup) if hookup is not None else None}
        d.update(kw)
        self.devices.append(d)
        return d

    def heater_beyond(self, did, end, d):
        """A heater one cell past `end` in direction d, hooked to `end`."""
        return self.dev(did, "consumer", end[0] + d[0], end[1] + d[1], hookup=end)

    def bbox(self):
        pts = list(self.cells) + self.walls + self.doors + self.rock + self.water + self.trees
        for d in self.devices:
            pts += [(d["x"], d["y"]), (d["x"] + d["w"] - 1, d["y"] + d["h"] - 1)]
        xs, ys = [p[0] for p in pts], [p[1] for p in pts]
        return min(xs), min(ys), max(xs), max(ys)


# ----------------------------------------------------------------------------- topologies (entry at (0, entry_y))
def t_line():
    c = Canvas("line")
    c.entry_y = 0
    e = c.line((0, 0), (7, 0))
    c.heater_beyond("h1", e, (1, 0))
    return c


def t_l_chain():
    c = Canvas("l_chain")
    p = c.line((0, 0), (3, 0))
    p = c.line(p, (3, 2))
    p = c.line(p, (6, 2))
    p = c.line(p, (6, 4))
    p = c.line(p, (9, 4))
    c.heater_beyond("h1", p, (1, 0))
    return c


def t_tee():
    c = Canvas("tee")
    c.entry_y = 4
    c.line((0, 4), (4, 4))
    n = c.line((4, 3), (4, 0))
    s = c.line((4, 5), (4, 8))
    c.heater_beyond("hn", n, (0, -1))
    c.heater_beyond("hs", s, (0, 1))
    return c


def t_cross4():
    c = Canvas("cross4")
    c.entry_y = 4
    e = c.line((0, 4), (8, 4))
    n = c.line((4, 3), (4, 0))
    s = c.line((4, 5), (4, 8))
    c.heater_beyond("he", e, (1, 0))
    c.heater_beyond("hn", n, (0, -1))
    c.heater_beyond("hs", s, (0, 1))
    return c


def t_ring():
    c = Canvas("ring")
    c.entry_y = 3
    c.line((0, 3), (2, 3))
    for p in [(x, 1) for x in range(2, 8)] + [(7, y) for y in range(2, 6)] + [(x, 5) for x in range(7, 1, -1)] + \
            [(2, y) for y in range(4, 1, -1)]:
        c.run([p])
    c.heater_beyond("he", (7, 3), (1, 0))
    c.dev("lamp", "lamp", 4, 0, hookup=(4, 1))
    return c


def _lattice(k, name):
    c = Canvas(name)
    c.intended_dense = True
    c.entry_y = k // 2 + 1
    c.line((0, c.entry_y), (2, c.entry_y))
    for x in range(3, 3 + k):
        for y in range(1, 1 + k):
            c.run([(x, y)])
    e = c.line((3 + k, c.entry_y), (5 + k, c.entry_y))
    c.heater_beyond("he", e, (1, 0))
    return c


def t_lattice2():
    return _lattice(2, "lattice2")


def t_lattice3():
    return _lattice(3, "lattice3")


def t_lattice5():
    return _lattice(5, "lattice5")


def t_star():
    """A hub (X) whose four arms each split again (T): eight leaves, eight heaters."""
    c = Canvas("star")
    c.entry_y = 8
    c.line((0, 8), (2, 8))
    c.line((2, 7), (2, 4))            # west arm goes north to a T
    hub = (8, 8)
    c.line((3, 4), (8, 4))
    c.line((8, 5), (8, 12))           # hub column
    c.line((9, 8), (14, 8))           # east arm
    c.line((2, 9), (2, 12))           # south-west arm
    c.line((3, 12), (7, 12))
    leaves = []
    leaves.append(c.line((14, 7), (14, 5)))
    leaves.append(c.line((14, 9), (14, 11)))
    leaves.append(c.line((8, 3), (8, 1)))
    leaves.append(c.line((9, 4), (11, 4)))
    leaves.append(c.line((8, 13), (8, 15)))
    leaves.append(c.line((9, 12), (11, 12)))
    dirs = [(0, -1), (0, 1), (0, -1), (1, 0), (0, 1), (1, 0)]
    for k, (lf, d) in enumerate(zip(leaves, dirs)):
        c.heater_beyond("h%d" % k, lf, d)
    c.notes.append("hub X at %s; arms split again into T junctions" % (hub,))
    return c


def t_spur():
    """A main run with a 1-cell and a 2-cell needless spur (pruned into coils, design 8.7.5) and a 3-cell
    unfinished spur that stays a LIVE terminal."""
    c = Canvas("spur")
    c.entry_y = 3
    e = c.line((0, 3), (14, 3))
    c.run([(3, 2)])                     # 1-cell spur
    c.line((6, 2), (6, 1))              # 2-cell spur
    c.line((10, 4), (10, 6))            # 3-cell spur: a real terminal
    c.heater_beyond("he", e, (1, 0))
    return c


def t_gap():
    """Live side and dead side: run -- gap -- run -- T; the T's north arm has a SECOND gap (dead-dead pair) and
    the far heater is dead."""
    c = Canvas("gap")
    c.entry_y = 4
    c.line((0, 4), (4, 4))            # live side ends at (4,4)
    c.extra_break.append((5, 4))
    c.line((6, 4), (12, 4))           # dead side
    c.line((9, 3), (9, 2))            # north arm (dead)
    c.extra_break.append((9, 1))
    c.line((9, 0), (12, 0))           # beyond the second gap (dead)
    c.heater_beyond("hdead", (12, 4), (1, 0))
    c.line((2, 5), (2, 7))            # an unfinished 3-cell spur on the LIVE side: a live terminal
    return c


def t_multinet():
    """Three nets in close company: the fed net, a second net with an EMPTY battery (dead), and a third
    conduit run with no source that touches the first only diagonally (separate net, design lesson run 1)."""
    c = Canvas("multinet")
    c.entry_y = 2
    e = c.line((0, 2), (12, 2))
    c.heater_beyond("h1", e, (1, 0))
    e2 = c.line((2, 4), (12, 4))      # two rows away: never 4-adjacent
    c.dev("bat2", "battery", 1, 4, charged=False)   # footprint (1,4),(1,5): hooks (2,4) only
    c.heater_beyond("h2", e2, (1, 0))
    c.line((5, 0), (9, 0))            # third net, row 0: two rows from row 2, never 4-adjacent
    c.notes.append("net A row 2 (fed), net B row 4 (empty battery), net C row 0 (no source)")
    return c


def t_device_attached():
    """Every device role on one run: an in-line switch (ON), an empty side battery, an unfuelled generator,
    a lamp and a heater."""
    c = Canvas("device_attached")
    c.entry_y = 4
    c.line((0, 4), (5, 4))
    c.dev("sw", "switch", 6, 4, on=True)            # in-line: hooks (5,4) and (7,4)
    e = c.line((7, 4), (16, 4))
    c.dev("bat", "battery", 9, 2, charged=False)     # footprint (9,2),(9,3): hooks (9,4)
    c.dev("gen", "generator", 12, 5, active=False)   # footprint (12..13,5..6): hooks (12,4),(13,4)
    c.dev("lamp", "lamp", 3, 2, hookup=(3, 3))
    c.run([(3, 3)])                                  # lamp feed (1 cell off the run, kept by its hookup)
    c.heater_beyond("he", e, (1, 0))
    c.dev("h3", "consumer", 14, 5, hookup=(14, 4))
    c.dev("hfar", "consumer", 4, 9, hookup=(4, 4))   # hooked FIVE cells away (design 4.2 T10): a long plug cord
    return c


def t_mesh():
    """A conduit MESH: 3x3 grid lines, 3 cells apart (7x7 cells): 9 junctions, never a dense field. A spacing-2
    5x5 mesh is NOT a mesh to the reducer: every hole has 8 conduit neighbours, so it is one tangle (lattice5)."""
    c = Canvas("mesh")
    c.entry_y = 4
    c.line((0, 4), (2, 4))
    for x in range(3, 10):
        for y in range(1, 8):
            if (x - 3) % 3 == 0 or (y - 1) % 3 == 0:
                c.run([(x, y)])
    e = c.line((10, 4), (11, 4))
    c.heater_beyond("he", e, (1, 0))
    return c


def t_spur_blob():
    """Design 4.2 T6: a needless 1-cell spur and a needless 2x2 blob sitting on a run."""
    c = Canvas("spur_blob")
    c.entry_y = 2
    e = c.line((0, 2), (14, 2))
    c.run([(4, 1)])
    c.run([(8, 3), (9, 3)])            # with (8,2),(9,2): a full 2x2 block
    c.intended_dense = True
    c.heater_beyond("he", e, (1, 0))
    return c


def t_rock_entry():
    """Design 4.2 T13: a run tunnelling through a granite block, and a branch that ENDS inside the rock."""
    c = Canvas("rock_entry")
    c.entry_y = 3
    c.rock = [(x, y) for x in range(5, 9) for y in range(0, 7)]
    e = c.line((0, 3), (12, 3))
    c.line((2, 2), (2, 0))
    c.line((3, 0), (5, 0))             # (5,0) is inside the rock: a buried dead end
    c.heater_beyond("he", e, (1, 0))
    return c


def t_doorway():
    c = Canvas("doorway")
    c.entry_y = 3
    room = (3, 0, 11, 6)
    door = (3, 3)
    c.walls = [p for p in _perimeter(*room) if p != door]
    c.doors = [door]
    e = c.line((0, 3), (8, 3))
    c.heater_beyond("he", e, (1, 0))
    return c


def t_wall_entry():
    """A run that dives under a wall and comes out the far side, plus a branch that ENDS inside the wall
    (a live wall terminal)."""
    c = Canvas("wall_entry")
    c.entry_y = 3
    c.walls = [(6, y) for y in range(0, 8)]
    e = c.line((0, 3), (10, 3))       # (6,3) is under the wall
    c.line((3, 4), (3, 6))
    c.line((4, 6), (6, 6))            # ends at (6,6) inside the wall
    c.heater_beyond("he", e, (1, 0))
    return c


def t_under_building():
    """A run under a walkable bench (ElectricSmelter 3x1: the cord stays on the floor, no stubs) and a run
    tunnelling under a 3x3 granite block (buried: two rock stubs)."""
    c = Canvas("under_building")
    c.entry_y = 2
    e = c.line((0, 2), (14, 2))
    c.dev("bench", "bench", 3, 2, hookup=(4, 2))    # Position = centre (4,2) sits on conduit: distance 0
    c.rock = [(x, y) for x in range(8, 11) for y in range(1, 4)]
    c.heater_beyond("he", e, (1, 0))
    return c


def t_canal():
    """Deep water two cells wide; the run crosses it on waterproof conduit (buried: two water stubs)."""
    c = Canvas("canal")
    c.entry_y = 3
    c.water = [(x, y) for x in (5, 6) for y in range(0, 7)]
    e = c.line((0, 3), (10, 3))
    c.heater_beyond("he", e, (1, 0))
    return c


def t_long_run():
    c = Canvas("long_run")
    c.entry_y = 0
    e = c.line((0, 0), (39, 0))
    c.heater_beyond("he", e, (1, 0))
    return c


def field_scene(n, seed=1, name=None):
    """Density ladder (design 4.2 B): exactly n conduit cells, a seeded mix of 3x3 lattice blocks (60%) and straight
    runs (40%) inside a square plot, fed by one battery through a 1-cell lead. Several nets are allowed."""
    import random
    rng = random.Random(seed * 7919 + n)
    side = max(1, int(math.ceil(math.sqrt(n / 0.5))))
    X0, Y0 = 3, 3
    ey = Y0 + side // 2
    cells = [(2, ey)]
    while len(cells) < n:
        if rng.random() < 0.6:
            bx, by = X0 + rng.randrange(side), Y0 + rng.randrange(side)
            add = [(bx + a, by + b) for a in range(3) for b in range(3)]
        else:
            bx, by = X0 + rng.randrange(side), Y0 + rng.randrange(side)
            L = rng.randint(3, 8)
            add = [(bx + k, by) for k in range(L)] if rng.random() < 0.5 else [(bx, by + k) for k in range(L)]
        for p in add:
            if X0 <= p[0] < X0 + side and Y0 <= p[1] < Y0 + side and p not in cells and len(cells) < n:
                cells.append(p)
        if len(cells) < n and (X0, ey) not in cells and len(cells) > n - 2:
            cells.append((X0, ey))
    W, H = X0 + side + 4, Y0 + side + 4
    sc = {"format": "mc_scene/1", "name": name or "field%d" % n, "topology": "field", "w": W, "h": H,
          "conduit": cells, "walls": [], "doors": [], "rock": [], "water": [], "trees": [],
          "devices": [{"id": "src", "role": "battery", "x": 1, "y": ey - 1, "w": 1, "h": 2, "hookup": None,
                       "charged": True}],
          "aerial": None, "hose": None, "break_cell": None, "intended_dense": True, "designed_gaps": [],
          "notes": ["density ladder: %d cells, seed %d" % (n, seed)], "params": {"density_target": n}}
    _canon(sc)
    return sc


def _perimeter(x0, y0, x1, y1):
    out = []
    for x in range(x0, x1 + 1):
        out += [(x, y0), (x, y1)]
    for y in range(y0 + 1, y1):
        out += [(x0, y), (x1, y)]
    return out


TOPOLOGIES = {n: globals()["t_" + n] for n in TOPOLOGY_ORDER}


# ----------------------------------------------------------------------------- composition
def _feeder_path(cx0, Y, R0, R1, n):
    """n fine cells of a boustrophedon over a coarse grid (step 2) starting at (cx0, Y): north to R0, then
    columns cx0-2, cx0-4 ... alternately south/north. Non-consecutive cells are never 4-adjacent and no 3x3
    window holds 6 cells, so the feeder never reads as a dense field."""
    out = [(cx0, Y)]
    x, y, dy = cx0, Y, -1
    while len(out) < n:
        ny = y + dy
        if (dy < 0 and ny < R0) or (dy > 0 and ny > R1):
            out.append((x - 1, y))
            x -= 2
            out.append((x, y))
            dy = -dy
            continue
        out.append((x, ny))
        y = ny
    return out[:n]


def compose(topology, density=20, brk="none", aerial="none", hose="none", name=None):
    """Full scene: [battery]-feeder snake-fill(4)-topology [+ aerial strip][+ hose strip].
    density = target conduit cell count (the feeder pads up to it; the topology is never shrunk)."""
    tc = TOPOLOGIES[topology]()
    M = 3
    tx0, ty0, tx1, ty1 = tc.bbox()
    # normalise so the topology bbox starts at (0,0) with the entry at local x=0
    assert tx0 == 0, (topology, tx0)
    th = ty1 - ty0 + 1
    topo_n = len(tc.cells)
    feed = max(5, density - topo_n)              # fill (4) + snake prefix (>=1)
    Lp = feed - 4
    region_h = max(th, min(40, int(math.sqrt(2 * Lp)) + 4))
    H = region_h + 2 * M + 3
    oy_local = (H - th) // 2                     # topology top row in scene coords
    Y = oy_local + (tc.entry_y - ty0)
    par = Y % 2
    R0 = M + 2 + ((M + 2 - par) % 2)
    R1 = H - M - 3
    if (R1 - par) % 2:
        R1 -= 1
    col_len = R1 - R0 + 2
    ncols = 1 + max(0, (Lp - (Y - R0 + 1) + col_len - 1) // col_len)
    feeder_w = 2 * ncols + 3
    cx0 = M + feeder_w                           # first (east) feeder column
    ox = cx0 + 5
    W = ox + (tx1 - tx0 + 1) + M + 2
    dx, dy = ox - tx0, oy_local - ty0

    def T(p):
        return (p[0] + dx, p[1] + dy)
    cells = []
    snake = _feeder_path(cx0, Y, R0, R1, Lp)
    fill = [(cx0 + k, Y) for k in range(1, 5)]
    for p in list(reversed(snake)) + fill + [T(p) for p in tc.cells]:
        if p not in cells:
            cells.append(p)
    devices = []
    # source battery past the far end of the snake (vertical 1x2, the only orientation we place)
    E = snake[-1]
    P = snake[-2] if len(snake) > 1 else (E[0] + 1, E[1])
    d = (E[0] - P[0], E[1] - P[1])
    cs = set(cells)
    cand = []
    if d[1] == -1:
        cand = [(E[0], E[1] - 2)]
    elif d[1] == 1:
        cand = [(E[0], E[1] + 1)]
    else:
        cand = [(E[0] + d[0], E[1] - 1), (E[0] + d[0], E[1])]
    bx, by = cand[0]
    for (x, y) in cand:
        fp = [(x, y), (x, y + 1)]
        hooks = {q for f in fp for q in _nb4(f) if q in cs}
        if hooks == {E} and not any(f in cs for f in fp):
            bx, by = x, y
            break
    devices.append({"id": "src", "role": "battery", "x": bx, "y": by, "w": 1, "h": 2, "hookup": None,
                    "charged": brk != "dead_gap"})
    for dv in tc.devices:
        dd = dict(dv)
        dd["x"], dd["y"] = T((dv["x"], dv["y"]))
        if dv.get("hookup") is not None:
            dd["hookup"] = list(T(dv["hookup"]))
        devices.append(dd)
    sc = {"format": "mc_scene/1", "name": name or topology, "topology": topology, "w": W, "h": H,
          "conduit": cells, "walls": [T(p) for p in tc.walls], "doors": [T(p) for p in tc.doors],
          "rock": [T(p) for p in tc.rock], "water": [T(p) for p in tc.water], "trees": [T(p) for p in tc.trees],
          "devices": devices, "aerial": None, "hose": None, "break_cell": None,
          "intended_dense": tc.intended_dense, "notes": list(tc.notes),
          "params": {"density_target": density, "break": brk, "aerial": aerial, "hose": hose}}
    for p in tc.extra_break:
        q = T(p)
        if q in sc["conduit"]:
            sc["conduit"].remove(q)
    sc["designed_gaps"] = [list(T(p)) for p in tc.extra_break]
    if brk in ("live_gap", "dead_gap"):
        b = (ox - 2, Y)
        sc["conduit"].remove(b)
        sc["break_cell"] = list(b)
    if aerial != "none" or hose != "none":
        _add_strips(sc, aerial, hose)
    # a tree beside the feeder fill (trees are walkable extra-cost cells; they change routing, never the graph)
    tree = (cx0 + 2, Y + 2)
    if tree not in set(map(tuple, sc["conduit"])) and not any(_in_fp(tree, d) for d in sc["devices"]):
        sc["trees"].append(tree)
    _canon(sc)
    return sc


def _add_strips(sc, aerial, hose):
    a = sc["h"] + 1
    W = max(sc["w"], 30)
    extra = 0
    if aerial != "none":
        poles = [5, 11] if aerial == "one_span" else [5, 11, 17, 23]
        sc["conduit"] += [(3, a), (4, a)]
        sc["devices"].append({"id": "src_air", "role": "battery", "x": 2, "y": a - 1, "w": 1, "h": 2,
                              "hookup": None, "charged": True})
        xp = poles[-1]
        sc["conduit"] += [(xp + 1, a), (xp + 2, a)]
        sc["devices"].append({"id": "h_air", "role": "consumer", "x": xp + 3, "y": a, "w": 1, "h": 1,
                              "hookup": [xp + 2, a]})
        spans = [[i, i + 1] for i in range(len(poles) - 1)]
        sc["aerial"] = {"poles": [[x, a] for x in poles], "spans": spans,
                        "cut": [1] if aerial == "chain_cut" else []}
        extra = 3
    if hose != "none":
        y = a + extra
        # RM_HoseReel is 2x2 (Position = SW cell = design (3, y); design y grows south, so the footprint is
        # (3,y) (4,y) (3,y-1) (4,y-1)); the hose leaves its centre. `cells` stays the 12-cell strip (cells[0] = the reel's
        # Position, cells[-1] = the free end); (4,y) is under the reel, so the strip's planned cells are only 5..14.
        sc["hose"] = {"cells": [[x, y] for x in range(3, 15)], "inflation": hose,
                      "footprint": [[3, y], [4, y], [3, y - 1], [4, y - 1]]}
        extra += 2
    sc["w"] = W
    sc["h"] = a + extra + 2


def _nb4(c):
    return [(c[0] + a, c[1] + b) for a, b in DIRS4]


def _in_fp(c, d):
    return d["x"] <= c[0] < d["x"] + d["w"] and d["y"] <= c[1] < d["y"] + d["h"]


def _canon(sc):
    for k in ("conduit", "walls", "doors", "rock", "water", "trees"):
        sc[k] = sorted({tuple(p) for p in sc[k]})
        sc[k] = [list(p) for p in sc[k]]


# ----------------------------------------------------------------------------- lint: is the scene well defined?
def footprint(d):
    return [(x, y) for x in range(d["x"], d["x"] + d["w"]) for y in range(d["y"], d["y"] + d["h"])]


def transmitter_hookups(sc, d):
    cs = {tuple(p) for p in sc["conduit"]}
    fp = set(footprint(d))
    out = []
    for f in sorted(fp):
        for q in _nb4(f):
            if q in cs and q not in fp and q not in out:
                out.append(q)
    return sorted(out)


def game_position(d):
    """The device's Position cell in SCENE coords as the game would hold it for rot North:
    min + (size-1)//2 along x, and along game z (north) -- scene y is south, so the game's minZ row is the
    scene's MAX y row."""
    gx = d["x"] + (d["w"] - 1) // 2
    gy = (d["y"] + d["h"] - 1) - (d["h"] - 1) // 2
    return gx, gy


def best_transmitter(sc, pos):
    """Emulates PowerConnectionMaker.BestTransmitterForConnector on the scene: every conduit cell and every
    wire-able transmitter device's Position within the 13x13 square, squared distance, scan game-z ascending
    (scene y DESCENDING) then x ascending, strict <. Returns (cell, kind, tie) where tie = another candidate
    at the same distance exists."""
    cands = []
    for p in sc["conduit"]:
        cands.append((tuple(p), "conduit"))
    on = {tuple(p): True for p in sc["conduit"]}
    for d in sc["devices"]:
        r = DEVICE_DEFS[d["role"]]
        if r["transmitter"] and r.get("wire_parent") and not (d["role"] == "switch" and not d.get("on", True)):
            gp = game_position(d)
            if gp not in on:
                cands.append((gp, "device:" + d["id"]))
    best, bd, tie = None, 1e9, False
    order = sorted(cands, key=lambda c: (-c[0][1], c[0][0]))
    for c, kind in order:
        if abs(c[0] - pos[0]) > 6 or abs(c[1] - pos[1]) > 6:
            continue
        dd = (c[0] - pos[0]) ** 2 + (c[1] - pos[1]) ** 2
        if dd < bd:
            best, bd, tie = (c, kind), dd, False
        elif dd == bd:
            tie = True
    return (best[0], best[1], tie) if best else (None, None, False)


def dense_cells(cells):
    """Same density rule as nodal.dense_clusters' seed (full 2x2 block or >=6 in a 3x3 window)."""
    s = set(cells)
    out = set()
    for (x, y) in s:
        if all((x + a, y + b) in s for a in (0, 1) for b in (0, 1)):
            out |= {(x + a, y + b) for a in (0, 1) for b in (0, 1)}
        if sum((x + a, y + b) in s for a in (-1, 0, 1) for b in (-1, 0, 1)) >= 6:
            out.add((x, y))
    return out


def lint(sc):
    """Problems that would make the scene ill-defined in game. [] = clean."""
    probs = []
    cs = {tuple(p) for p in sc["conduit"]}
    W, H = sc["w"], sc["h"]
    for p in cs:
        if not (0 <= p[0] < W and 0 <= p[1] < H):
            probs.append("conduit off canvas %s" % (p,))
    occ = {}
    for d in sc["devices"]:
        for f in footprint(d):
            if not (0 <= f[0] < W and 0 <= f[1] < H):
                probs.append("%s off canvas" % d["id"])
            if f in occ:
                probs.append("%s overlaps %s at %s" % (d["id"], occ[f], f))
            occ[f] = d["id"]
            if f in cs and DEVICE_DEFS[d["role"]]["transmitter"]:
                probs.append("transmitter %s sits on conduit %s" % (d["id"], f))
        r = DEVICE_DEFS[d["role"]]
        if r["transmitter"]:
            hk = transmitter_hookups(sc, d)
            if d["id"].startswith("src") and len(hk) != 1:
                probs.append("source %s has %d hookups %s (want exactly 1)" % (d["id"], len(hk), hk))
        else:
            want = tuple(d["hookup"]) if d.get("hookup") is not None else None
            got, kind, tie = best_transmitter(sc, game_position(d))
            if want is None or want not in cs:
                probs.append("connector %s hookup %s is not conduit" % (d["id"], want))
            elif got != want or kind != "conduit":
                probs.append("connector %s would wire to %s (%s), not its hookup %s" % (d["id"], got, kind, want))
            elif tie:
                probs.append("connector %s hookup %s is a distance TIE (game picks by scan order)" % (d["id"], want))
    blocked = set(map(tuple, sc["walls"])) | set(map(tuple, sc["rock"])) | set(map(tuple, sc["water"]))
    for d in sc["devices"]:
        for f in footprint(d):
            if f in blocked:
                probs.append("%s on blocked cell %s" % (d["id"], f))
    if not sc.get("intended_dense"):
        dn = dense_cells(cs - blocked)
        if dn:
            probs.append("unintended dense field (would become a tangle/blob): %s" % sorted(dn)[:6])
    if sc.get("aerial"):
        for p in sc["aerial"]["poles"]:
            if tuple(p) in cs or tuple(p) in occ:
                probs.append("pole on occupied cell %s" % (p,))
    if sc.get("hose"):
        fp = sc["hose"].get("footprint") or [sc["hose"]["cells"][0]]
        for p in list(sc["hose"]["cells"]) + list(fp):
            if tuple(p) in cs or tuple(p) in occ:
                probs.append("hose on occupied cell %s" % (p,))
    return probs
