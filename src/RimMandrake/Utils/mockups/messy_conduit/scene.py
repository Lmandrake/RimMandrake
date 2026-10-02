"""Fixed synthetic base scene for the Messy Conduit phase-0 mock-ups.

Cell coordinates are (x, y) with x to the east and y to the SOUTH (image rows), so
row 0 is the north edge. The grid key in the mock-up README uses the same numbers:
column letters A.. for x, row numbers 0.. for y.

Every scene is plain data so the renderer can draw small test beds (swatches, the
break strip) with the same code path as the main scene.
"""


def _rect_perimeter(x0, y0, x1, y1):
    cells = []
    for x in range(x0, x1 + 1):
        cells += [(x, y0), (x, y1)]
    for y in range(y0 + 1, y1):
        cells += [(x0, y), (x1, y)]
    return cells


def base_scene():
    door = (15, 10)
    walls = [c for c in _rect_perimeter(11, 2, 21, 10) if c != door]
    main = [(6, 4), (7, 4), (8, 4), (9, 4), (10, 4), (11, 4), (11, 5), (11, 6), (11, 7)] + \
           [(x, 7) for x in range(12, 21)]
    ring = [(7, 6), (8, 6), (9, 6), (9, 7), (9, 8), (8, 8), (7, 8), (7, 7)]
    ring_link = [(9, 5)]
    tree_branch = [(7, 9), (6, 9), (5, 9), (4, 9)]        # live side ends at (4,9)
    dead_side = [(2, 9), (1, 9), (1, 10), (1, 11)]         # gap at (3,9); dead side
    wb_branch = [(15, 6), (15, 5), (15, 4)]
    bat_branch = [(18, 6), (18, 5), (18, 4)]
    south = [(15, 8), (15, 9), (15, 10), (15, 11), (15, 12)]  # through the door, capped stub
    conduit = main + ring + ring_link + tree_branch + dead_side + wb_branch + bat_branch + south
    return {
        "name": "base",
        "w": 23, "h": 14,
        "indoor": [(11, 2, 21, 10)],            # floor rects (x0,y0,x1,y1) drawn as wood
        "walls": walls,
        "doors": [door],
        "rock": [],
        "machines": [
            {"id": "generator", "kind": "generator", "x": 4, "y": 3, "w": 2, "h": 2,
             "hookup": (6, 4), "source": True},
            {"id": "workbench", "kind": "workbench", "x": 13, "y": 3, "w": 3, "h": 1, "hookup": (15, 4)},
            {"id": "battery", "kind": "battery", "x": 18, "y": 3, "w": 2, "h": 1, "hookup": (18, 4)},
            {"id": "heater", "kind": "heater", "x": 20, "y": 8, "w": 1, "h": 1, "hookup": (20, 7)},
            {"id": "console", "kind": "console", "x": 2, "y": 11, "w": 1, "h": 1, "hookup": (1, 11)},
        ],
        "lamps": [{"x": 8, "y": 7, "hookup": (8, 8)}],
        "trees": [{"x": 6, "y": 9}],
        "items": [(4, 12, "steel"), (17, 8, "crate"), (13, 8, "components"), (10, 11, "wood"),
                  (12, 9, "chunk")],
        "conduit": conduit,
    }


# Grid key, used by the README and the on-image ruler (column letter + row number).
GRID_KEY = [
    ("E3:F4", "generator (2x2), the only power source"),
    ("G4..L4, L4:L7", "main line; L4..L7 runs ON TOP of the west wall, then drops into the room along row 7"),
    ("H6..J8", "a closed conduit LOOP (ring of 8 cells) around the lamp post at I7; J5 links it to the main line"),
    ("I7", "lamp post; its hookup climbs the post from I8"),
    ("H9..E9", "branch west; it wraps the tree trunk at G9"),
    ("D9", "THE BREAK: a one-cell gap. E9 is the live end (sparks), C9 the dead end (limp)"),
    ("C9, B9..B11", "dead side of the break, feeding the console at C11 (unpowered)"),
    ("P7", "X junction: N to the workbench (N3:P3), S through the door at P10"),
    ("S7", "T junction: N to the battery bank (S3:T3)"),
    ("U7", "end of the main line, plugged into the heater at U8"),
    ("P10", "door: the cable runs under the threshold"),
    ("P12", "lone dead end: a deliberate capped stub (never sparks)"),
    ("E12, R8, N8, K11, M9", "floor items (steel, crate, components, wood, chunk) drawn over the wires"),
]


def mini(cells, w, h, **kw):
    d = {"name": kw.pop("name", "mini"), "w": w, "h": h, "indoor": [], "walls": [], "doors": [],
         "rock": [], "machines": [], "lamps": [], "trees": [], "items": [], "conduit": list(cells)}
    d.update(kw)
    return d


def break_scene():
    """Battery on the left powers a run that breaks at x=4; x=5.. is dead."""
    return mini([(1, 1), (2, 1), (3, 1), (5, 1), (6, 1), (7, 1)], 9, 3, name="break",
                machines=[{"id": "battery", "kind": "battery", "x": 0, "y": 0, "w": 1, "h": 2,
                           "hookup": (1, 1), "source": True}])


def sprawl_scene():
    """Owner-excursion test bed (§8.11): real open floor, a rock outcrop and a pillar block to
    avoid, runs laid one cell off a wall base (excess piles against it) and through a doorway."""
    W, Hh = 26, 16
    door = (9, 10)
    walls = [c for c in _rect_perimeter(9, 2, 24, 14) if c != door]
    rock = [(x, y) for x in range(0, 4) for y in range(0, 4)] + [(1, 4), (2, 4), (0, 4)]
    rock += [(15, 6), (16, 6), (15, 7), (16, 7)]          # a rock pillar inside the hall
    outdoor = [(x, 10) for x in range(3, 9)]                # generator -> door
    lamp_run = [(5, y) for y in range(5, 10)]               # north past the outcrop to a lamp
    west_base = [(10, y) for y in range(3, 10)]             # along the base of the west wall
    north_base = [(x, 3) for x in range(11, 23)]            # along the base of the north wall
    hall = [(x, 10) for x in range(10, 22)]                 # across the open hall floor
    south = [(10, 11), (10, 12), (10, 13)] + [(x, 13) for x in range(11, 17)]
    conduit = outdoor + [door] + lamp_run + west_base + north_base + hall + south
    return {
        "name": "sprawl", "w": W, "h": Hh,
        "indoor": [(9, 2, 24, 14)], "walls": walls, "doors": [door], "rock": rock,
        "machines": [
            {"id": "generator", "kind": "generator", "x": 1, "y": 9, "w": 2, "h": 2, "hookup": (3, 10),
             "source": True},
            {"id": "heater", "kind": "heater", "x": 22, "y": 4, "w": 1, "h": 1, "hookup": (22, 3)},
            {"id": "workbench", "kind": "workbench", "x": 22, "y": 9, "w": 2, "h": 3, "hookup": (21, 10)},
            {"id": "battery", "kind": "battery", "x": 17, "y": 12, "w": 2, "h": 2, "hookup": (16, 13)},
        ],
        "lamps": [{"x": 5, "y": 4, "hookup": (5, 5)}],
        "trees": [], "items": [(13, 12, "crate"), (19, 5, "components"), (7, 13, "steel")],
        "conduit": conduit,
    }


SPRAWL_KEY = [
    ("A0:D4, P6:Q7", "rock outcrop and a rock pillar: unwalkable, loops must go round or pile against them"),
    ("D10..I10", "generator -> door; excess heaps around the doorway J10"),
    ("F5..F9", "branch north past the outcrop to a lamp at F5"),
    ("K3..K9, L3..W3", "runs one cell off the west and north wall bases: slack bunches against the walls"),
    ("K10..V10", "across open hall floor to the workbench: room for big loops and figure-eights"),
    ("K11..Q13", "south to the battery bank"),
]
