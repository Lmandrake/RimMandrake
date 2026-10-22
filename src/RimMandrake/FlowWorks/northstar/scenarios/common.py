"""scenarios/common.py -- the shared vocabulary of the FlowWorks COMPOSITE review scenarios (C1-C12).

Design (authoritative): design/RimMandrake/flowworks_composite_review_scenarios_2026-10-21.md. Owner by card
2026-10-21 ~21:23 PDT: build all twelve in one go, for one walk (REVIEW_SCENARIOS_BUILD_ALL_TWELVE_AT_ONCE).

A scenario module (cNN_*.py) holds DATA only: one SCENARIO dict made by scenario(). Its `setup` uses the station
vocabulary of src/RimMandrake/FlowWorks/review_map.py (SETUPS keys: terrain, dig, fluid, roof, designate, build, spawn,
stuffed, style, hostile, build_after, items, beds, tank, pump, ladder, hose, hose_flow, hose_reelin, hose_order,
hose_trail, flood_trigger, scorch) in PLOT-LOCAL cells (0,0 = the plot's south-west corner), so review_map.Review stages
it unchanged. Composite-only keys, staged by scenarios_map.py:

    pawns      (kind, x, z, faction, role)        role: drafted | prisoner | penned | None
    pawn_ops   (x, z, op, arg)                    op: wear (apparel def) | need ("RM_Thirst=0.2") | name ("Hobb")
    batteries  (x, z)                             charged to 100 % by jawa/battery_set (a built battery holds 0 Wd)
    markers    (method, x, z, tail)               RM_MapControls.Place*: args "x,z|tail" (static_call splits on '|')
    calls      dict(typ, method, fmt, cells)      any other proof surface; fmt's {0},{1}.. become absolute "x,z"
    gizmos     (x, z, prefix, want)               the thing's own button, pressed until it reads `want`
    pens       (kind, x, z, faction)              hostiles behind a shut grate: spawned ONLY in the raid branch save
    pen_ops    (x, z, op, arg)                    pawn_ops for a pen pawn (raid branch)
    spawn_plants (def, x, z)                      plants (rimworld/spawn_thing)
    optional_build (def, x, z, rot, stuff, needs) built only when live get_defs finds `needs` (another mod's def)

Every scenario also lists `pieces`: each named element of the design is staged (with a ref the selftest resolves
against the setup) or DEFERRED (with why and the item that will build it). In-world, every DEFERRED piece gets a
label AND a sign book at its cell, so a plain load still says what is missing.

No defName is typed from memory: selftest_scenarios_map.py resolves every one against src/**/Defs and the game's
Data/*/Defs (def_index below). A def another mod brings sets `needs_def` on the scenario and is checked live.
"""
import glob
import os
import re

LEVEL_M = 0.5                       # RM_Volume.MetresPerNotch (CentimetresPerNotch = 50)
COLONIST_DIG_MAX = 4                # levels = 2 m: owner card 2026-10-21 "COLONISTS go back to a 2 m dig limit"
PORTABLE_LADDER_LEVELS = 6          # RimMandrakeFlowWorksMod.portableLadderMaxLevels default (3 m)
HOSE_CELLS = 40                     # one reel's hose (review_map hose_maze notes; GSS walk)
SOAK_TICKS = 5000                   # two in-game hours unattended (GPT #1)
CLOCK_HOUR = 10                     # the map's one clock (GPT #1)
LOOKS = ("Scrapper", "Industrial", "Modern", "Futuristic")
TAGS = ("demonstrated", "poked", "look", "DEFERRED", "blocked")

NSP = "RimMandrake.FlowWorks.RM_NorthstarProofs"
PROMO = "RimMandrake.FlowWorks.RM_PromotionProofs"
MAPCTL = "RimMandrake.FlowWorks.MapControls.RM_MapControls"
SUSP = "RimMandrake.FlowWorks.Pits.RM_SuspensionProofs"
DPROOF = "RimMandrake.FlowWorks.Pits.RM_DrawbridgeProofs"
LPROOF = "RimMandrake.FlowWorks.Machinery.RM_LineProofs"
SWIM = "RimMandrake.FlowWorks.Swimming.RM_Swim"
DROWN = "RimMandrake.FlowWorks.RM_PitFillEffects"
FLUID = "RimMandrake.FlowWorks.RM_FluidIdentityProof"
W, TAR = "RM_Fluid_Water", "RM_Fluid_Tar"

# Tonight's owner rulings every scenario respects (owner, 2026-10-21; quoted in the design and the brief)
RULINGS = {
    "dig2m": "colonists dig to 2 m; deeper holes are machine-dug (machine dig not built: DEFERRED)",
    "girth": "pipes half as thick / hoses much thinner: art being redrawn; the CURRENT art is shown",
    "overflow": "canal overflow ships in 1.0 but only Stage 0 (offline kernel) exists: DEFERRED",
    "reach": "reachability option 3 is being built separately (REACH_MAP_BUILD_WALLS_AND_DEPTH_AGREE)",
    "cord": "a fallen cord lands walkable (fix built)",
}
DEEP_DIG_ITEM = "DEEP_DIG_BUILD_DROIDS_TAKE_THE_SHOVEL"
OVERFLOW_ITEM = "CANAL_OVERFLOW_BUILD_EVERY_PUDDLE_AUDITED"
GIRTH_NOTE = "pipes and hoses show TODAY's art; the half-girth pipe and much thinner hose are being redrawn " \
             "(PIPE_GIRTH_TUNE_HALF_AS_THICK, HOSE_GIRTH_TUNE_MUCH_THINNER)"


# ------------------------------------------------------------------------------------------------ geometry helpers
def perimeter(x0, z0, x1, z1, gaps=()):
    gaps = set(gaps)
    return [(x, z) for x in range(x0, x1 + 1) for z in range(z0, z1 + 1)
            if (x in (x0, x1) or z in (z0, z1)) and (x, z) not in gaps]


def walls(cells, stuff="Steel", d="Wall"):
    return [(d, x, z, None, stuff) for x, z in cells]


def hline(x0, x1, z, gaps=()):
    return [(x, z) for x in range(x0, x1 + 1) if (x, z) not in set(gaps)]


def vline(x, z0, z1, gaps=()):
    return [(x, z) for z in range(z0, z1 + 1) if (x, z) not in set(gaps)]


def cells_of(r):
    """cells of an (x, z, w, h, ...) rect tuple."""
    return [(r[0] + i, r[1] + j) for i in range(r[2]) for j in range(r[3])]


def metres(levels):
    return levels * LEVEL_M


# ------------------------------------------------------------------------------------------------ pieces
def staged(name, key, d=None, at=None, tag="demonstrated", note=""):
    """A named design element that IS staged: `key` names the setup key that stages it, `d` the def/kind/method it
    must name (None = any), `at` a plot-local cell the entry must cover. tag: demonstrated|poked|look."""
    return dict(name=name, status="staged", key=key, d=d, at=at, tag=tag, note=note)


def deferred(name, why, item, at, tag="DEFERRED"):
    """A named design element that is NOT built. `at` is the free plot-local cell where its DEFERRED label and sign
    book stand; `item` the ledger item (or ruling) that will build it."""
    return dict(name=name, status="DEFERRED", why=why, item=item, at=at, tag=tag)


def scenario(**kw):
    d = dict(id=None, n=None, slug=None, name=None, map="C", size=None, look_style=None, purpose="", start="",
             try_=[], look_for="", broken="", idle="", reset="reload the save to reset", setup={}, parts=[],
             pieces=[], exercises={}, branch={}, needs_def=None, goal="", owed_cs=[], prove_first=None,
             edge_drain=None, anchor=None, fluid_moves=False)
    unknown = set(kw) - set(d)
    if unknown:
        raise ValueError("scenario(): unknown keys %s" % sorted(unknown))
    d.update(kw)
    return d


# ------------------------------------------------------------------------------------------------ setup cell walk
def _rect_keys():
    return ("terrain", "dig", "fluid", "roof", "designate")


def setup_cells(u):
    """{(x,z): [what]} for every plot-local cell the setup touches (rect keys expanded)."""
    out = {}

    def put(c, w):
        out.setdefault(tuple(c), []).append(w)
    for k in _rect_keys():
        for r in u.get(k, []):
            rr = r[1:5] if isinstance(r[0], str) else r[:4]
            for c in cells_of(rr):
                put(c, k)
    for k in ("build", "spawn", "hostile", "build_after", "stuffed", "spawn_plants", "optional_build"):
        for r in u.get(k, []):
            put((r[1], r[2]), "%s:%s" % (k, r[0]))
    for r in u.get("items", []):
        put((r[2], r[3]), "items:%s" % r[0])
    for k in ("pawns", "pens"):
        for r in u.get(k, []):
            put((r[1], r[2]), "%s:%s" % (k, r[0]))
    for k in ("tank", "pump", "ladder", "batteries", "flood_trigger", "hose_flow", "hose_reelin", "gizmos"):
        for r in u.get(k, []):
            put((r[0], r[1]), k)
    for r in u.get("markers", []):
        put((r[1], r[2]), "markers:%s" % r[0])
    for r in u.get("hose", []):
        put((r[0], r[1]), "hose")
        put((r[2], r[3]), "hose_end")
    for r in u.get("hose_order", []):
        put((r[0], r[1]), "hose_order")
        put((r[2], r[3]), "hose_order_to")
    for r in u.get("hose_trail", []):
        for c in r[2]:
            put(c, "hose_trail")
    for c in u.get("calls", []):
        for cc in c["cells"]:
            put(cc, "calls:%s" % c["method"])
    for r in u.get("beds", []):
        put((r[0], r[1]), "beds")
    for k in ("pawn_ops", "pen_ops"):
        for r in u.get(k, []):
            put((r[0], r[1]), "%s:%s" % (k, r[2]))
    return out


def solid_cells(u):
    """Cells a sign book or label marker must not sit on: anything built, spawned, dug, painted or occupied."""
    return {c for c, ws in setup_cells(u).items()
            if any(not w.startswith(("hose_end", "hose_order_to", "pawn_ops", "pen_ops", "calls", "terrain", "roof"))
                   for w in ws)}


def find_ref(u, piece):
    """True when the piece's ref resolves in the setup: setup[key] has an entry naming `d` (if given) that covers `at`
    (if given)."""
    key, d, at = piece["key"], piece.get("d"), piece.get("at")
    rows = u.get(key, [])
    for r in rows:
        if key in ("build", "spawn", "hostile", "build_after", "stuffed", "spawn_plants", "optional_build"):
            name, cells = r[0], [(r[1], r[2])]
        elif key == "items":
            name, cells = r[0], [(r[2], r[3])]
        elif key in ("pawns", "pens"):
            name, cells = r[0], [(r[1], r[2])]
        elif key in ("terrain",):
            name, cells = r[0], cells_of(r[1:5])
        elif key in ("dig", "roof", "designate"):
            name, cells = (r[0] if isinstance(r[0], str) else None), cells_of(r[1:5] if isinstance(r[0], str) else r[:4])
        elif key == "fluid":
            name, cells = r[5], cells_of(r[:4])
        elif key == "markers":
            name, cells = r[0], [(r[1], r[2])]
        elif key == "style":
            name, cells = r[3], [(r[1], r[2])]
        elif key == "calls":
            name, cells = r["method"], [tuple(c) for c in r["cells"]]
        elif key in ("hose", "hose_order"):
            name, cells = None, [(r[0], r[1]), (r[2], r[3])]
        elif key == "hose_trail":
            name, cells = None, [(r[0], r[1])] + list(r[2])
        elif key in ("pawn_ops", "pen_ops"):
            name, cells = r[3], [(r[0], r[1])]
        elif key in ("tank", "pump", "ladder", "batteries", "flood_trigger", "hose_flow", "hose_reelin", "gizmos", "beds"):
            name, cells = (r[2] if key in ("pump", "ladder", "tank") and len(r) > 2 else None), [(r[0], r[1])]
        else:
            return False
        if d is not None and name != d:
            continue
        if at is not None and tuple(at) not in cells:
            continue
        return True
    return False


# ------------------------------------------------------------------------------------------------ def references
def referenced_defs(u):
    """-> {defName: [where]} for every def a setup names (things, terrain, pawn kinds, styles, fluids, designations,
    apparel, liquids, stuff)."""
    out = {}

    def add(d, w):
        if d:
            out.setdefault(d, []).append(w)
    for d, *_ in u.get("terrain", []):
        add(d, "terrain")
    for k in ("build", "spawn", "hostile", "build_after"):
        for r in u.get(k, []):
            add(r[0], k)
            if len(r) > 4:
                add(r[4], k + " stuff")
    for r in u.get("spawn_plants", []):
        add(r[0], "plant")
    for r in u.get("optional_build", []):
        add(r[0], "optional (needs %s)" % r[5])
    for r in u.get("stuffed", []):
        add(r[0], "stuffed")
        add(r[4], "stuffed stuff")
    for r in u.get("items", []):
        add(r[0], "items")
    for r in u.get("style", []):
        add(r[0], "style thing")
        add(r[3], "style")
    for r in u.get("fluid", []):
        add(r[5], "fluid")
    for r in u.get("designate", []):
        add(r[0], "designate")
    for r in u.get("roof", []):
        add(r[0], "roof")
    for k in ("pawns", "pens"):
        for r in u.get(k, []):
            add(r[0], k)
    for r in u.get("tank", []):
        add(r[3], "tank liquid")
    for x, z, op, arg in u.get("pawn_ops", []) + u.get("pen_ops", []):
        if op == "wear":
            add(arg, "apparel")
        if op == "need":
            add(arg.split("=")[0], "need")
    for r in u.get("markers", []):
        tail = str(r[3])
        m = re.match(r"(RM_Fluid_\w+)", tail)
        if m:
            add(m.group(1), "marker fluid")
    return out


def _data_roots():
    here = os.path.dirname(os.path.abspath(__file__))
    repo = os.path.abspath(os.path.join(here, "..", "..", "..", "..", ".."))
    game = [r"C:\Program Files (x86)\Steam\steamapps\common\RimWorld\Data",
            "/mnt/c/Program Files (x86)/Steam/steamapps/common/RimWorld/Data"]
    return os.path.join(repo, "src"), [g for g in game if os.path.isdir(g)]


_DEFNAME = re.compile(r"<defName>\s*([^<\s]+)\s*</defName>")


def def_index():
    """-> (set of defNames, dict(src=n_files, game=n_files, game_root=path|None)). Reads every Defs XML under src/ and
    the installed game's Data/<Core|DLC>/Defs. A missing game folder leaves vanilla names unresolvable: the caller
    reports them UNMEASURED, never as absent."""
    src, games = _data_roots()
    names, n_src, n_game = set(), 0, 0
    for path in glob.glob(os.path.join(src, "**", "*.xml"), recursive=True):
        if os.sep + "Defs" + os.sep not in path and "/Defs/" not in path:
            continue
        n_src += 1
        try:
            with open(path, encoding="utf-8", errors="replace") as f:
                names.update(_DEFNAME.findall(f.read()))
        except OSError:
            pass
    for g in games[:1]:
        for path in glob.glob(os.path.join(g, "*", "Defs", "**", "*.xml"), recursive=True):
            n_game += 1
            try:
                with open(path, encoding="utf-8", errors="replace") as f:
                    names.update(_DEFNAME.findall(f.read()))
            except OSError:
                pass
    return names, dict(src=n_src, game=n_game, game_root=games[0] if games else None)


# ------------------------------------------------------------------------------------------------ maze routing (offline goal read)
def route_len(blocked, start, goal, size):
    """4-neighbour BFS steps from start to goal over plot cells not in `blocked`; None when unreachable. A hose is
    laid on walkable ground: walls, pits and the chasm are blocked."""
    from collections import deque
    w, h = size
    if start == goal:
        return 0
    seen = {start}
    q = deque([(start, 0)])
    while q:
        (x, z), n = q.popleft()
        for dx, dz in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            c = (x + dx, z + dz)
            if c == goal:
                return n + 1
            if c in seen or c in blocked or not (0 <= c[0] < w and 0 <= c[1] < h):
                continue
            seen.add(c)
            q.append((c, n + 1))
    return None


# ------------------------------------------------------------------------------------------------ def facts (size, stuff)
def def_facts():
    """-> {defName: dict(size=(w, h)|None, stuffable=bool|None, kind=tag)} for every ThingDef/TerrainDef/... in src/ and
    the game's Data, with ParentName inheritance resolved (Name= abstract parents). size None = no <size> anywhere up
    the chain (RimWorld's default is 1x1)."""
    import xml.etree.ElementTree as ET
    src, games = _data_roots()
    files = [p for p in glob.glob(os.path.join(src, "**", "*.xml"), recursive=True)
             if os.sep + "Defs" + os.sep in p or "/Defs/" in p]
    for g in games[:1]:
        files += glob.glob(os.path.join(g, "*", "Defs", "**", "*.xml"), recursive=True)
    named, defs = {}, {}
    for path in files:
        try:
            root = ET.parse(path).getroot()
        except Exception:  # noqa: BLE001
            continue
        for el in root:
            nm, par = el.get("Name"), el.get("ParentName")
            size = el.findtext("size")
            stuff = el.find("stuffCategories")
            rec = dict(kind=el.tag, parent=par, size=size.strip() if size else None,
                       stuffable=(stuff is not None and len(stuff) > 0) if stuff is not None else None)
            if nm:
                named[nm] = rec
            dn = el.findtext("defName")
            if dn:
                defs[(el.tag, dn.strip())] = rec

    def resolve(rec, field, depth=0):
        while rec is not None and depth < 20:
            if rec.get(field) is not None:
                return rec[field]
            rec = named.get(rec.get("parent")) if rec.get("parent") else None
            depth += 1
        return None
    out = {}
    for (kind, dn), rec in defs.items():
        sz = resolve(rec, "size")
        wh = None
        if sz:
            m = re.match(r"\(\s*(\d+)\s*,\s*(\d+)\s*\)", sz)
            if m:
                wh = (int(m.group(1)), int(m.group(2)))
        out[(kind, dn)] = dict(size=wh, stuffable=resolve(rec, "stuffable"), kind=kind)
    return out


def fact(facts, dn, kinds=("ThingDef", "TerrainDef", "PawnKindDef")):
    """The first def of that name among `kinds` (a defName may name a ThingDef AND a PrefabDef)."""
    for k in kinds:
        if (k, dn) in facts:
            return facts[(k, dn)]
    return None


# Defs the game GENERATES at load, so no XML names them (verified by their use on the live review map 2026-10-15/16:
# review_map look_walls paints Granite_Rough): stone floors from rock types (TerrainDefGenerator_Stone).
RUNTIME_GENERATED = {"Granite_Rough", "Sandstone_Rough", "Limestone_Rough", "Slate_Rough", "Marble_Rough"}


def footprint(x, z, size, rot=None):
    """Cells a size (w, h) thing anchored at (x, z) occupies (GenAdj.OccupiedRect for rot north/south; east/west swap
    w and h). Even sizes run anchor..anchor+1 (owner_review_stage._edge_anchor's rule)."""
    w, h = size or (1, 1)
    if rot in (1, 3):
        w, h = h, w
    x0, z0 = x - (w - 1) // 2, z - (h - 1) // 2
    return [(x0 + i, z0 + j) for i in range(w) for j in range(h)]
