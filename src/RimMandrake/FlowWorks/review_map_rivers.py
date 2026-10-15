"""review_map_rivers.py -- the FlowWorks review map's RIVER block (map R): the river works on a REAL river.

Why a second map: every river mechanic reads the river current, and the current is RM_MapComponent_RiverCurrent's copy
of map.waterInfo.riverFlowMap, which only map generation writes. River terrain painted onto the quicktest map has NO
current, so a weir there never pools or catches, a ferry rope never matters, nothing is carried or swept and a flood
never breaches anything. The main map keeps the bank works as LOOKS (painted river, labelled "no current here"); the
mechanics are staged here, on the river site map that northstar/river_site.py founds (the shared test-site builder,
not edited from here).

Stations are anchored at build time on the river the site happens to have: river_anchors() reads the map's terrain
(jawa/get_terrain_batch), finds straight crossings of moving water from a standable bank to a standable far bank, and
hands one crossing to each station, spaced apart. Pure and selftested (selftest_review_map.py); the live half only
places what the plan says and reports what did not build.
"""
import json
import os

TAG = "fw_review_r"
SPAN_MAX = 40                 # RM_RiversSettings.ferryMaxSpan default: a rope longer than this is refused
SPACING = 26                  # cells between two stations' bank anchors (labels and effects never meet)
MARGIN = 12                   # keep anchors off the map edge (the swept row and the label both need room)
AVOID_R = 14                  # and away from river_site's colonists at (centre x, 30)
ROT = {(0, 1): 0, (1, 0): 1, (0, -1): 2, (-1, 0): 3}   # Rot4 int facing the water: the 1x2 weir/sluice box wet end

# Each station: what kind of anchor it takes (every one is a crossing: bank cell b, direction d into the water,
# n moving cells, far bank e), its short label, the clause under it, how to poke it, what to look for, and the
# capabilities its status is derived from (human_review CAPS).
STATIONS = [
    dict(id="r_current", short="The current carries things", caps=["L09"],
         notice="a log stack and a muffalo in the fast water, frozen before the current moves them",
         try_=["unpause: the logs drift downstream and the muffalo is pushed along; at the map edge the water takes it"],
         look="weak spot: does the push follow the river's bend, or run straight into the bank? A carried muffalo "
              "should bruise sometimes and drop what it carries"),
    dict(id="r_ford", short="Ford stones across", caps=["L09"],
         notice="a line of ford stones right across, and a drafted colonist on the near bank",
         try_=["order him to the far bank: on the stones he is not carried", "order him across beside the stones: he is"],
         look="weak spot: stones that read as dry ground in the middle of a river; a colonist pushed off the line"),
    dict(id="r_weir", short="A weir pools and catches", caps=["L10", "L13"],
         notice="a new weir on the bank; its slack pool forms upstream once the game runs",
         try_=["unpause a few hours: the pool spreads upstream and fish and drift gather by the weir",
               "select it: the inspect line says what it holds"],
         look="weak spot: a pool on the downstream side; a catch that never stops growing (the cap is 30)"),
    dict(id="r_breach", short="A worn weir breaches", caps=["L12"],
         notice="the same weir, worn below half health: the next flood breaches it",
         try_=["dev: Incidents > seasonal flood, then unpause: the weir breaks and its catch is washed downstream"],
         look="weak spot: a breach that deletes the catch instead of washing it a few cells; a breach with no letter"),
    dict(id="r_stakes", short="A stake-line levee", caps=["L11"],
         notice="a line of bank stakes along the shore with one gap in the middle",
         try_=["dev: Incidents > seasonal flood: the water stays behind the stakes and leaks only through the gap"],
         look="weak spot: water crossing a stake; a stake that blocks walking (it should not)"),
    dict(id="r_silt", short="A silt trap", caps=["L11"],
         notice="a silt trap on the bank",
         try_=["unpause a day: the soil beside it turns rich; remove the trap and it slowly goes back"],
         look="weak spot: richening that spreads beyond the trap's neighbours"),
    dict(id="r_ferry", short="A ferry rope", caps=["L13"],
         notice="two ferry posts on opposite banks with the rope strung between them",
         try_=["undraft a colonist and send him across: he takes the rope and is not swept",
               "deconstruct one post: the rope goes too"],
         look="weak spot: a rope drawn under the water or not at all; a rope across land"),
    dict(id="r_placer", short="Sluice box and panning", caps=["M05", "M06"],
         notice="a sluice box set into the bank and a panning spot beside it, on real moving water",
         try_=["unpause a day: the sluice washes a little ore onto its bank end",
               "a colonist pans at the spot: mostly nothing, sometimes a few units"],
         look="weak spot: ore that appears on the water end; panning that never yields"),
]


# ------------------------------------------------------------------------------------------------ pure planning
def is_moving(d):
    return "Moving" in str(d or "")


def is_land(d):
    d = str(d or "")
    return bool(d) and not any(k in d for k in ("Water", "Marsh", "Mud", "Ice", "Lava", "Deep", "Shallow", "Ocean"))


def crossings(terrain, size, span=SPAN_MAX):
    """[(b, d, n, e)]: from bank cell b, walking d crosses n moving-water cells to land cell e (n <= span)."""
    w, h = size
    out = []
    for (x, z), t in terrain.items():
        if not is_land(t):
            continue
        for d in ROT:
            c = (x + d[0], z + d[1])
            if not is_moving(terrain.get(c)):
                continue
            n = 0
            while is_moving(terrain.get(c)) and n <= span:
                n += 1
                c = (c[0] + d[0], c[1] + d[1])
            if n <= span and is_land(terrain.get(c)) and 0 <= c[0] < w and 0 <= c[1] < h:
                out.append(((x, z), d, n, c))
    return out


def river_anchors(terrain, size, k=len(STATIONS), spacing=SPACING, margin=MARGIN, avoid=None):
    """-> [crossing] for up to k stations, greedy: narrow-to-middling crossings near the map centre first, every bank
    anchor at least `spacing` from the others (Chebyshev), `margin` off the edge, `AVOID_R` from `avoid`."""
    w, h = size
    avoid = avoid if avoid is not None else (w // 2, 30)
    cx, cz = w // 2, h // 2

    def ok(c):
        return margin <= c[0] < w - margin and margin <= c[1] < h - margin
    cand = [c for c in crossings(terrain, size) if ok(c[0]) and ok(c[3])
            and max(abs(c[0][0] - avoid[0]), abs(c[0][1] - avoid[1])) >= AVOID_R]
    cand.sort(key=lambda c: (c[2] > 12, abs(c[0][0] - cx) + abs(c[0][1] - cz), c[0]))
    pick = []
    for c in cand:
        if all(max(abs(c[0][0] - p[0][0]), abs(c[0][1] - p[0][1])) >= spacing for p in pick):
            pick.append(c)
        if len(pick) == k:
            break
    return pick


def station_ops(st, cr):
    """One station's ops on its crossing: dict(build, terrain, items, pawns, hp, label). Positions absolute."""
    (bx, bz), d, n, (ex, ez) = cr
    p = (-d[1], d[0])                           # along the bank
    mid = (bx + d[0] * max(1, n // 2), bz + d[1] * max(1, n // 2))
    rot = ROT[d]
    o = dict(build=[], terrain=[], items=[], pawns=[], hp=[], label=(bx - 3 * d[0], bz - 3 * d[1]))
    i = st["id"]
    if i == "r_current":
        o["items"] = [("WoodLog", 25, mid)]
        o["pawns"] = [("Muffalo", (bx + d[0] + p[0] * 2, bz + d[1] + p[1] * 2), "none", None)]
    elif i == "r_ford":
        o["terrain"] = [("RM_FordStones", (bx + d[0] * k, bz + d[1] * k)) for k in range(1, n + 1)]
        o["pawns"] = [("Colonist", (bx - d[0], bz - d[1]), "player", "drafted")]
    elif i in ("r_weir", "r_breach"):
        o["build"] = [("RM_BankWeir", (bx, bz), rot, None)]
        if i == "r_breach":
            o["hp"] = [("RM_BankWeir", (bx, bz), 0.4)]
    elif i == "r_stakes":
        o["build"] = [("RM_BankStake", (bx + p[0] * k, bz + p[1] * k), None, None) for k in range(-5, 6) if k != 0]
    elif i == "r_silt":
        o["build"] = [("RM_SiltTrap", (bx, bz), None, None)]
    elif i == "r_ferry":
        o["build"] = [("RM_FerryPost", (bx, bz), None, None), ("RM_FerryPost", (ex, ez), None, None)]
    elif i == "r_placer":
        o["build"] = [("RM_SluiceBox", (bx, bz), rot, None), ("RM_PanningSpot", (bx + p[0] * 3, bz + p[1] * 3), None, None)]
    return o


def plan(terrain, size, avoid=None):
    """-> ([(station, crossing, ops)], unplaced station ids)."""
    anchors = river_anchors(terrain, size, avoid=avoid)
    out = [(s, c, station_ops(s, c)) for s, c in zip(STATIONS, anchors)]
    return out, [s["id"] for s in STATIONS[len(anchors):]]


# ------------------------------------------------------------------------------------------------ live half
def read_terrain(B, size, chunk=50):
    """{(x,z): TerrainDef} for the whole current map, in chunks (one call per chunk)."""
    import site_spec as SS
    w, h = size
    out = {}
    for x in range(0, w, chunk):
        for z in range(0, h, chunk):
            r = B.call("jawa/get_terrain_batch", rects="%d,%d,%d,%d" % (x, z, min(chunk, w - x), min(chunk, h - z))) or {}
            if not r.get("success"):
                raise SystemExit("get_terrain_batch refused at %d,%d: %s" % (x, z, str(r)[:200]))
            out.update(SS.parse_ops(r.get("ops")))
    return out


def build(R, label_line):
    """Stage map R on the CURRENT map (river_site.py made it current). R is review_map.Review (calls, notes, say).
    -> (placed [(station, crossing, ops)] in R-number order, verify {"R<n>": dict})."""
    B = R.B
    mi = B.call("jawa/map_info")
    size = (int(mi.get("sizeX") or 0), int(mi.get("sizeZ") or mi.get("sizeY") or 0))
    if size[0] <= 2:
        raise SystemExit("map_info gave no size: %s" % str(mi)[:200])
    prof = B.call("jawa/static_call", type="RimMandrake.FlowWorks.Rivers.RM_RiverWorksProof", method="ProofGrid", args="-")
    if "current=" not in str(prof.get("result", "")) or "current=0" in str(prof.get("result", "")):
        raise SystemExit("map R needs a river with a current (run northstar/river_site.py first): %s" % str(prof)[:200])
    terr = read_terrain(B, size)
    placed, unplaced = plan(terr, size)
    for sid in unplaced:
        R.notes.append("river station %s: no free crossing left on this river" % sid)
    B.call("jawa/review_label", action="clear", tag=TAG)
    for k, (st, cr, o) in enumerate(placed):
        (bx, bz), d = cr[0], cr[1]
        x0, z0 = min(bx, cr[3][0]) - 6, min(bz, cr[3][1]) - 6
        rr = "%d,%d,%d,%d" % (x0, z0, abs(cr[3][0] - bx) + 13, abs(cr[3][1] - bz) + 13)
        B.call("jawa/destroy_batch", rects=rr, categories="Plant")
        B.call("jawa/set_fog", action="unfog", rect=rr)
        for t, (x, z) in o["terrain"]:
            R.call("jawa/set_terrain_batch", ops="%s:%d,%d,1,1" % (t, x, z))
        for dname, (x, z), rot, stuff in o["build"]:
            kw = dict(ops="%s:%d,%d" % (dname, x, z) + ("" if rot is None else ",%d" % rot), faction="player",
                      wipeExisting=False)
            if stuff:
                kw["stuff"] = stuff
            r = R.call("jawa/build_batch", **kw)
            if r.get("survived") == 0:
                R.notes.append("R%d %s: %s not built %s" % (k + 1, st["id"], dname, (r.get("failed") or [])[:1]))
        for dname, (x, z), frac in o["hp"]:
            th = B.call("jawa/list_things", defName=dname, rect="%d,%d,1,1" % (x, z), limit=3).get("things") or []
            if th:
                tid = str(th[0].get("id") or th[0].get("thingId"))
                mx = B.call("jawa/set_thing_props", thing=tid).get("maxHitPoints")
                if isinstance(mx, (int, float)) and mx > 0:
                    R.call("jawa/set_thing_props", thing=tid, hitPoints=max(1, int(mx * frac)))
        for dname, n_, (x, z) in o["items"]:
            R.call("rimworld/spawn_thing", defName=dname, stackCount=n_, x=x, z=z)
        for kind, (x, z), fac, role in o["pawns"]:
            r = R.call("jawa/spawn_pawn", kindDef=kind, x=x, z=z, faction=fac, count=1)
            pid = (r.get("pawns") or [{}])[0].get("id") if r.get("pawns") else r.get("id")
            if pid is not None and role == "drafted":
                R.call("jawa/set_draft", pawnId=str(pid), drafted=True)
    R.call("rimworld/pause_game", pause=True)
    verify = {}
    for k, (st, cr, o) in enumerate(placed):
        need = sorted({b[0] for b in o["build"]})
        xs = [c[1][0] for c in o["build"]] + [cr[0][0]]
        zs = [c[1][1] for c in o["build"]] + [cr[0][1]]
        rr = "%d,%d,%d,%d" % (min(xs), min(zs), max(xs) - min(xs) + 2, max(zs) - min(zs) + 2)
        defs = {t.get("def") or t.get("defName") for t in B.call("jawa/list_things", rect=rr, limit=100).get("things") or []}
        miss = [d for d in need if d not in defs]
        # nothing built to read (the current, the ford): None, never "as built"
        verify["R%d" % (k + 1)] = dict(id=st["id"], ok=(not miss) if need else None, missing=miss, at=cr[0], width=cr[2])
    labels(B, placed, label_line)
    R.say("map R: %d of %d river stations placed, %d read as built, %d with nothing built to read" % (
        len(placed), len(STATIONS), sum(1 for v in verify.values() if v["ok"]),
        sum(1 for v in verify.values() if v["ok"] is None)))
    return placed, verify


def labels(B, placed, label_line):
    L = []
    for k, (st, cr, o) in enumerate(placed):
        x, z = o["label"]
        L.append(label_line(x, z + 1, "R%d  %s" % (k + 1, st["short"]), "", "#ffd27f", "small", TAG))
        L.append(label_line(x, z - 1, st["notice"][:60], "", "#f2e6cf", "tiny", TAG))
    return B.call("jawa/review_label", action="add", ops="\n".join(L), tag=TAG)


def goto(B, placed, which):
    k = int(str(which).upper().lstrip("R")) - 1
    st, cr, o = placed[k]
    xs = [cr[0][0], cr[3][0], o["label"][0]]
    zs = [cr[0][1], cr[3][1], o["label"][1]]
    return B.call("rimworld/frame_cell_rect", x=min(xs) - 2, z=min(zs) - 2, width=max(xs) - min(xs) + 5,
                  height=max(zs) - min(zs) + 5, paddingCells=2)


def save_placed(path, placed):
    """Where each R station landed, kept beside the key sheet: the plan cannot be re-derived after the build (the ford
    stones change the river), and --rivers --goto/--labels need it."""
    rows = [dict(n=k + 1, id=st["id"], crossing=[list(cr[0]), list(cr[1]), cr[2], list(cr[3])], label=list(o["label"]))
            for k, (st, cr, o) in enumerate(placed)]
    with open(path, "w", encoding="utf-8") as f:
        json.dump(rows, f, indent=1)


def load_placed(path):
    if not os.path.exists(path):
        raise SystemExit("map R was never built here (%s missing): run --rivers --build first" % path)
    by = {s["id"]: s for s in STATIONS}
    out = []
    for r in json.load(open(path, encoding="utf-8")):
        b, d, n, e = r["crossing"]
        out.append((by[r["id"]], (tuple(b), tuple(d), n, tuple(e)), dict(label=tuple(r["label"]))))
    return out
