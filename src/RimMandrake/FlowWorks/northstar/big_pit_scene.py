"""RIMMANDRAKE_PROVE_UNDER_LIQUID_LAW_LIVE: the big-pit series, a live scene a human LOOKS at (owner 2026-11-12).

    python.exe big_pit_scene.py <OUT dir> <step> [origin_x origin_z]
    steps: plan  stage  fill  verify  labels  key  captures  shots  save:<name>
    exit 0 PASS, 1 FAIL, 2 UNMEASURED.  Test map only: stage clears roof, rock and everything in the site.

ONE 16x16 pit dug 4 m (8 notches) is copied 7 times at different liquid levels, identical contents at identical offsets.
Everything lives in the pure half (no bridge, selftested by selftest_big_pit_scene.py):
  * pack_layout: every footprint cell of every thing lies INSIDE the dug rect, MARGIN cells clear of each wall, for every
    rotation and every size (the owner's 2026-11-12 look: the outer ring straddled the pit walls);
  * pick_stuff: a stuffable def is never made with stuff=null (MakeThing error);
  * choose_origin: the scene is moved off any SteamGeyser (no bridge tool can destroy one: destroyable=false);
  * hp judge against the spawn-time baseline, the label text a cell must read, the capture list.
The live half drives the bridge. The fill route is the engine driver write RM_SubmergeDraw.ProofFillRect (the god-mode
pour/drain tools of RIMMANDRAKE_GIVE_GODMODE_LIQUID_POUR_DRAIN had not landed when this was written).
"""
import collections
import json
import os
import re
import sys
import time
from water_reads import levels  # noqa: E402  (whole levels from the one water number)

SUB = "RimMandrake.FlowWorks.RM_SubmergeDraw"
SCRATCH_FROM_EDGE = 12           # footprint probe spot, cells in from the NE corner (far from the scene at 40,89)
PW, DEPTH = 16, 8                # pit width in cells; dug notches (1 notch = 0.5 m)
MARGIN = 1                       # clear cells between any footprint and the pit walls (the dug rect's own edge ring)
DEFAULT_ORIGIN = (40, 89)        # SW corner of the site rect
SITE_W, SITE_H = 77, 40
GEYSER_CLEAR = 3                 # cells kept between a geyser and the site (a geyser is 2x2 and vents steam)
# (key, dx, dz, fill notches, fluid or None), offsets from the origin; the BP0..BP6 coordinates of the first series
COPY_ROWS = [("BP0_dry", 2, 22, 0, None), ("BP1_0.5m", 21, 22, 1, None), ("BP2_1m", 40, 22, 2, None),
             ("BP3_2m", 59, 22, 4, None), ("BP4_3m", 2, 2, 6, None), ("BP5_brim", 21, 2, 8, None),
             ("BP6_tar1.5m", 40, 2, 3, "RM_Fluid_Tar")]
HEADER_AT = (2, 41)              # offset of the series label
# installed furniture: (def, source mod); positions come from pack_layout
FURN = [("SculptureGrand", "Core"), ("DoubleBed", "Core"), ("RM_GlowTank", "RimMandrake LuminousPigment"),
        ("RM_HoseReel", "RimMandrake FlowWorks"), ("Table2x2c", "Core"), ("TableButcher", "Core"),
        ("HandTailoringBench", "Core"), ("SculptureLarge", "Core"), ("Bed", "Core"), ("Shelf", "Core"),
        ("Dresser", "Core"), ("RM_ResinSealingJarShelf", "RimMandrake ColdStorage"), ("Bedroll", "Core"),
        ("Battery", "Core"), ("PlantPot", "Core"), ("SculptureSmall", "Core"), ("DiningChair", "Core"),
        ("Stool", "Core"), ("Armchair", "Core"), ("EndTable", "Core"), ("StandingLamp", "Core"),
        ("TorchLamp", "Core"), ("Cooler", "Core"), ("RM_BrineCrock", "RimMandrake ColdStorage"),
        ("RM_EvaporativeCrock", "RimMandrake ColdStorage"),
        ("RM_AncientStasisLocker_Refurbished", "RimMandrake ColdStorage")]
# floor items: (def, stack, source)
ITEMS = [("WoodLog", 75, "Core"), ("Plasteel", 10, "Core"), ("Gold", 50, "Core"), ("ComponentIndustrial", 3, "Core"),
         ("Cloth", 60, "Core"), ("Hay", 40, "Core"), ("Silver", 500, "Core"), ("Steel", 1, "Core"),
         ("Leather_Plain", 30, "Core"), ("MealSimple", 1, "Core"), ("MealFine", 5, "Core"), ("RawPotatoes", 40, "Core"),
         ("Meat_Cow", 60, "Core"), ("Pemmican", 75, "Core"), ("Beer", 10, "Core"), ("Chocolate", 20, "Core"),
         ("MedicineIndustrial", 5, "Core"), ("MedicineHerbal", 1, "Core"), ("Neutroamine", 25, "Core"),
         ("MeleeWeapon_Knife", 1, "Core"), ("Gun_BoltActionRifle", 1, "Core"), ("Gun_Revolver", 1, "Core"),
         ("MeleeWeapon_LongSword", 1, "Core"), ("Apparel_Parka", 1, "Core"), ("Apparel_CowboyHat", 1, "Core"),
         ("Apparel_FlakVest", 1, "Core"), ("ChunkGranite", 1, "Core"), ("ChunkSlagSteel", 1, "Core"),
         ("Shell_HighExplosive", 5, "Core"), ("Shell_EMP", 1, "Core"), ("Jade", 10, "Core"), ("Novel", 1, "Core"),
         ("RM_ResinSealedMeat", 10, "RimMandrake ColdStorage"), ("RM_ResinSealedFruit", 10, "RimMandrake ColdStorage"),
         ("RM_AmberAgedMeat", 4, "RimMandrake ColdStorage")]
MINI = [("Armchair", "Core"), ("EndTable", "Core"), ("RM_BrineCrock", "RimMandrake ColdStorage")]
CORPSES = [("Muffalo", "Core (animal corpse)"), ("Villager", "Core (human corpse)")]
# stuff to use per category the def allows; first match wins (a stuff is chosen FROM the def's own stuffCategories, so it is legal)
STUFF_BY_CATEGORY = [("Metallic", "Steel"), ("Woody", "WoodLog"), ("Stony", "BlocksGranite"), ("Fabric", "Cloth"),
                     ("Leathery", "Leather_Plain")]


class LayoutError(Exception):
    pass


# ------------------------------------------------------------------------------------------------ pure: footprint, layout
def footprint(cx, cz, w, h, rot):
    """Every cell a w x h thing centred on (cx, cz) may occupy, rot 0-3 (E/W swap w and h). Engine convention for an even
    side is not read offline, so an even side is taken as 2k+1 cells centred on the cell (a one-cell superset): the layout
    is then inside the pit whichever way the engine rounds."""
    if rot % 2 == 1:
        w, h = h, w
    hw = w // 2 if w % 2 == 0 else (w - 1) // 2
    hh = h // 2 if h % 2 == 0 else (h - 1) // 2
    return {(x, z) for x in range(cx - hw, cx + hw + 1) for z in range(cz - hh, cz + hh + 1)}


def inside(cells, size=PW, margin=MARGIN):
    return all(margin <= x < size - margin and margin <= z < size - margin for x, z in cells)


def pack_layout(sizes, size=PW, margin=MARGIN):
    """sizes: ordered {key: (w, h)}. First-fit, biggest first (stable by input order), rot 0, scanning the interior
    [margin, size-margin)^2 bottom-left to top-right; each thing's whole footprint must be free and inside. Returns
    {key: (cx, cz)}. Raises LayoutError naming what did not fit: a layout that cannot fit is a refusal, never a spill."""
    used, out = set(), {}
    order = sorted(sizes, key=lambda k: -len(footprint(0, 0, *sizes[k], 0)))
    for key in order:
        w, h = sizes[key]
        placed = False
        for z in range(margin, size - margin):
            for x in range(margin, size - margin):
                cells = footprint(x, z, w, h, 0)
                if inside(cells, size, margin) and not cells & used:
                    used |= cells
                    out[key] = (x, z)
                    placed = True
                    break
            if placed:
                break
        if not placed:
            raise LayoutError("%s (%dx%d) does not fit inside the %dx%d interior (margin %d) with %d cells used"
                              % (key, w, h, size - 2 * margin, size - 2 * margin, margin, len(used)))
    return out


def scene_things(sizes):
    """The whole scene as ordered rows (kind, key, def, source, (cx, cz), stack) with local pit coordinates.
    kind: furn | item | mini | corpse. sizes covers FURN defs (w, h); item, mini and corpse are one cell each."""
    boxes = collections.OrderedDict()
    for dn, _s in FURN:
        if dn not in sizes:
            raise LayoutError("no measured size for %s" % dn)
        boxes["furn:" + dn] = tuple(sizes[dn])
    for i, (dn, _n, _s) in enumerate(ITEMS):
        boxes["item:%d:%s" % (i, dn)] = (1, 1)
    for i, (dn, _s) in enumerate(MINI):
        boxes["mini:%d:%s" % (i, dn)] = (1, 1)
    for i, (kind, _s) in enumerate(CORPSES):
        boxes["corpse:%d:%s" % (i, kind)] = (1, 1)
    at = pack_layout(boxes)
    rows = []
    for dn, src in FURN:
        rows.append(("furn", "furn:" + dn, dn, src, at["furn:" + dn], 1))
    for i, (dn, n, src) in enumerate(ITEMS):
        rows.append(("item", "item:%d:%s" % (i, dn), dn, src, at["item:%d:%s" % (i, dn)], n))
    for i, (dn, src) in enumerate(MINI):
        rows.append(("mini", "mini:%d:%s" % (i, dn), dn, src, at["mini:%d:%s" % (i, dn)], 1))
    for i, (kind, src) in enumerate(CORPSES):
        rows.append(("corpse", "corpse:%d:%s" % (i, kind), kind, src, at["corpse:%d:%s" % (i, kind)], 1))
    return rows


def copies_for(origin):
    ox, oz = origin
    return [(k, ox + dx, oz + dz, f, fl) for k, dx, dz, f, fl in COPY_ROWS]


def site_rect(origin):
    return (origin[0], origin[1], SITE_W, SITE_H + 3)


def choose_origin(map_size, geysers, preferred=DEFAULT_ORIGIN, step=8):
    """The site's SW corner: the preferred one when no geyser lies within GEYSER_CLEAR of the site rect, else the first
    clear one scanning the map (step-cell grid, 8 cells in from the edge). geysers: [(x, z)]. None when none is clear."""
    def clear(o):
        x0, z0, w, h = site_rect(o)
        return not any(x0 - GEYSER_CLEAR <= gx < x0 + w + GEYSER_CLEAR and z0 - GEYSER_CLEAR <= gz < z0 + h + GEYSER_CLEAR
                       for gx, gz in geysers)
    cands = [preferred] + [(x, z) for z in range(8, map_size - SITE_H - 12, step) for x in range(8, map_size - SITE_W - 8, step)]
    for o in cands:
        x0, z0, w, h = site_rect(o)
        if x0 >= 0 and z0 >= 0 and x0 + w <= map_size and z0 + h <= map_size and clear(o):
            return o
    return None


def pick_stuff(categories):
    """Stuff for a def: None when it takes none (empty/None categories); else a stuff from one of ITS categories."""
    txt = str(categories)
    if not categories or txt.strip() in ("[]", "None", "null", "()"):
        return None
    for cat, stuff in STUFF_BY_CATEGORY:     # substring: the bridge may send names, 'StuffCategoryDef/Name' or a joined string
        if cat in txt:
            return stuff
    cats = txt
    raise LayoutError("no stuff known for categories %s" % cats)


def parse_size(v):
    """'(2,2)' | [2, 2] | {'x': 2, 'z': 2} -> (2, 2); anything else None (the caller refuses: sizes are never guessed)."""
    if isinstance(v, dict):
        v = [v.get("x"), v.get("z", v.get("y"))]
    if isinstance(v, str):
        v = re.findall(r"-?\d+", v)
    try:
        a, b = int(v[0]), int(v[1])
    except (TypeError, ValueError, IndexError, KeyError):
        return None
    return (a, b) if a > 0 and b > 0 else None


def parse_def_rows(resp, fields):
    """{defName: {field: value}} from a jawa/get_defs reply (rows under 'defs' or 'results', fields nested or flat)."""
    out = {}
    for d in (resp.get("defs") or resp.get("results") or []) if isinstance(resp, dict) else []:
        f = d.get("fields") or d
        out[d.get("defName")] = {k: f.get(k) for k in fields}
    return out


# ------------------------------------------------------------------------------------------------ pure: judges
def metres(notches):
    return notches * 0.5


def format_metres(m):
    m = max(0.0, m)
    return ("%.2f" if 0.0 < m < 0.05 else "%.1f") % m + " m"


def expected_label(depth_notches, fill_notches, liquid_label):
    """The cell label RM_Volume.PitLabel gives for a dug cell (RIMMANDRAKE_LABEL_PIT_DEPTH_EXACT_ONE_WORD): 'Pit, 2.5 m deep'
    dry, 'Pit, 1.5 m water in 4.0 m' wet; None for an undug cell."""
    if depth_notches <= 0:
        return None
    hole = format_metres(metres(depth_notches))
    if fill_notches <= 0:
        return "Pit, %s deep" % hole
    return "Pit, %s %s in %s" % (format_metres(metres(fill_notches)), liquid_label or "liquid", hole)


def judge_hp(now, baseline):
    """PASS when a spawned thing's HP is unchanged since the read taken at spawn; None baseline is UNMEASURED."""
    if baseline is None or now is None:
        return "UNMEASURED"
    return "PASS" if now == baseline else "FAIL"


def judge_thing(t, px, pz, cell_fill_notches, planned, sizes):
    """One state-read row for a thing found in a copy: where it is, in the pit or not, liquid over it. t: a list_things
    row. px, pz: the pit's SW corner. planned: (def, i, j) it was meant to be at. -> (verdict, detail dict)."""
    i, j = t["x"] - px, t["z"] - pz
    w, h = sizes.get(t["def"], (1, 1))
    rot = t.get("rotation") or 0
    rot = rot if isinstance(rot, int) else {"North": 0, "East": 1, "South": 2, "West": 3}.get(str(rot), 0)
    cells = footprint(i, j, w, h, rot)
    det = {"def": t["def"], "at": [i, j], "planned": list(planned), "inPit": inside(cells), "liquidOverM": metres(cell_fill_notches)}
    ok = det["inPit"] and (i, j) == tuple(planned[1:])
    return ("PASS" if ok else "FAIL"), det


def capture_list(origin):
    """Camera rects for the later bridge run: the deepest copy first, then every copy, then the overview."""
    cps = copies_for(origin)
    deepest = max((c for c in cps if not c[4]), key=lambda c: c[3])
    out = [{"name": "deepest_" + deepest[0], "cx": deepest[1] + PW / 2, "cz": deepest[2] + PW / 2, "rootSize": 13.0,
            "rect": [deepest[1], deepest[2], PW, PW], "why": "the deepest water copy (brim): owner asked for this one"}]
    for key, x0, z0, f, fl in cps:
        out.append({"name": key, "cx": x0 + PW / 2, "cz": z0 + PW / 2, "rootSize": 13.0, "rect": [x0, z0, PW, PW],
                    "why": "%s fill %d notches" % ("tar" if fl else "water", f)})
    sx, sz, sw, sh = site_rect(origin)
    out.append({"name": "overview", "cx": sx + sw / 2, "cz": sz + sh / 2 - 3, "rootSize": 30.0, "rect": [sx, sz, sw, sh],
                "why": "the whole series"})
    return out


def key_markdown(plan, provisional=False):
    """BIG_PIT_KEY.md: the copies with world coordinates and fill, then every thing's local cell (the same in every copy;
    world cell = the copy's SW corner + local)."""
    ox, oz = plan["origin"]
    L = ["# Big-pit key", ""]
    if provisional:
        L += ["**PROVISIONAL: the def sizes were not read from a live game; `plan` rewrites this file from the real sizes.**", ""]
    L += ["Origin (SW corner of the site) %d,%d; site rect %s. One pit is %dx%d cells dug %d notches (%.1f m); one notch = 0.5 m."
          % (ox, oz, tuple(plan["site"]), PW, PW, DEPTH, metres(DEPTH)),
          "Local coordinates (i east, j north) run 0..%d from a pit's SW corner; things keep %d clear cell(s) from each wall, "
          "so they use i, j in %d..%d." % (PW - 1, MARGIN, MARGIN, PW - 1 - MARGIN), "",
          "## Copies", "", "| copy | SW corner (x,z) | fill | liquid | camera centre |", "|---|---|---|---|---|"]
    for key, x0, z0, f, fl in plan["copies"]:
        L.append("| %s | %d,%d | %d notch(es) = %s | %s | %.1f,%.1f |" % (key, x0, z0, f, format_metres(metres(f)), fl or ("water" if f else "dry"),
                                                                          x0 + PW / 2, z0 + PW / 2))
    L += ["", "Series label header at %d,%d (tag `bigpit`). The deepest copy is the brim one (%s)." % (ox + HEADER_AT[0], oz + HEADER_AT[1],
                                                                                              [c[0] for c in plan["copies"] if c[3] == DEPTH][0]),
          "", "## Contents (identical in every copy)", "", "| kind | def | source | local cell | stack | stuff |", "|---|---|---|---|---|---|"]
    for kind, _k, dn, src, (i, j), n in plan["things"]:
        L.append("| %s | %s | %s | %d,%d | %s | %s |" % (kind, dn, src, i, j, n if kind == "item" else "", plan["stuff"].get(dn, "")))
    L += ["", "World cell of a local cell: copy SW corner + local. Corpses are a Muffalo (factionless) and a Villager, stripped of "
          "inventory and apparel before the kill. Minified: the three `mini` rows (spawned, then minified).",
          "", "## Changing a level by hand (dev mode)", "",
          "Route today: the engine driver write `RM_SubmergeDraw.ProofFillRect` (`jawa/static_call`, args `x,z,w,h,waterM[,fluid]`), "
          "the route `fill` uses. The god-mode pour/drain tools of RIMMANDRAKE_GIVE_GODMODE_LIQUID_POUR_DRAIN had not landed when this "
          "was written; use them once they exist. The dev menu's `Fill excavated cell with fluid...` / `Place level holder (50%)` "
          "(RM_MapControls.cs near line 709) are the in-game equivalents; neither was exercised here."]
    return "\n".join(L) + "\n"


# ------------------------------------------------------------------------------------------------ live half
LOG, ROWS = [], []
B = None
OUT = STEP = None


def log(k, v):
    LOG.append({k: v})
    print(k, json.dumps(v, default=str)[:300])
    sys.stdout.flush()


def bridge():
    global B
    if B is None:
        sys.path.insert(0, os.path.join(os.environ.get("RM_REPO", r"D:\Luke\dev\RimMandrake"), "src", "RimMandrake", "Utils"))
        import validation_core as V
        B = V.Bridge()
    return B


def call(tool, **kw):
    try:
        return bridge().call(tool, **kw) or {}
    except Exception as ex:  # noqa: BLE001
        return {"success": False, "error": str(ex)}


def static(method, arg):
    r = call("jawa/static_call", type=SUB, method=method, args=arg)
    return str(r.get("result") or r.get("error") or r)


def row(name, verdict, got):
    ROWS.append({"row": name, "verdict": verdict, "got": got})
    if verdict != "PASS":
        log(verdict, ROWS[-1])


def dump():
    with open(os.path.join(OUT, "bigpit_%s_%s.json" % (STEP.replace(":", "_"), time.strftime("%Y%m%dT%H%M%S"))), "w") as fh:
        json.dump({"log": LOG, "rows": ROWS}, fh, indent=1, default=str)


def plan_path():
    return os.path.join(OUT, "scene_plan.json")


def load_plan():
    with open(plan_path()) as fh:
        return json.load(fh)


def read_defs(names, fields):
    r = call("jawa/get_defs", defs=";".join("ThingDef/" + n for n in sorted(names)), fields=",".join(fields))
    return parse_def_rows(r, fields)


def parse_cells(txt):
    """'[(200, 0, 200), (201, 0, 200)]' (GenAdj.OccupiedRect rendered by jawa/static_call) -> (width, height) or None."""
    cells = [(int(a), int(c)) for a, _b, c in re.findall(r"\((-?\d+),\s*(-?\d+),\s*(-?\d+)\)", str(txt))]
    if not cells:
        return None
    return (len({x for x, _ in cells}), len({z for _, z in cells}))


def measure_footprints(names, stuff, map_size):
    """{defName: (w, h)} read LIVE: jawa/get_defs cannot read ThingDef.size (an IntVec2: '(no such field)', 2026-11-12), so
    each def is spawned once at rot 0 in a scratch corner and its footprint read through Verse.GenAdj.OccupiedRect(Thing).
    A def that does not spawn or read back is absent (the caller refuses: sizes are never guessed)."""
    sx = sz = map_size - SCRATCH_FROM_EDGE
    rect = "%d,%d,10,10" % (sx - 4, sz - 4)
    out = {}
    call("rimworld/set_god_mode", enabled=True)
    call("jawa/destroy_batch", rects=rect, categories="All")
    call("jawa/set_roof_batch", ops="None:" + rect)
    call("jawa/set_terrain_batch", ops="Soil:" + rect)
    for dn in names:
        call("jawa/destroy_batch", rects=rect, categories="All")
        spawn_stuffed(dn, sx, sz, 1, {"stuff": stuff})
        t = [x for x in call("jawa/list_things", defName=dn, rect=rect, limit=5).get("things") or [] if x.get("def") == dn]
        if t:
            got = parse_cells(static_on("Verse.GenAdj", "OccupiedRect", t[0]["id"]))
            if got:
                out[dn] = got
    call("jawa/destroy_batch", rects=rect, categories="All")
    call("rimworld/set_god_mode", enabled=False)
    return out


def static_on(type_, method, arg):
    r = call("jawa/static_call", type=type_, method=method, args=arg)
    return str(r.get("result") or r.get("error") or r)


def geysers_on_map():
    r = call("jawa/list_things", defName="SteamGeyser", limit=500)
    if r.get("success") is False or r.get("things") is None:
        return None
    return [(t["x"], t["z"]) for t in r["things"]]


def do_plan(origin_arg):
    """Offline-derivable plan + the live reads it needs: map size, geyser cells, def sizes and stuffs. Writes scene_plan.json."""
    mi = call("jawa/map_info")
    size = int(mi.get("sizeX") or mi.get("width") or mi.get("size") or 0)
    gz = geysers_on_map()
    if not size or gz is None:
        row("plan_reads", "UNMEASURED", {"map_size": size, "geysers": gz})
        return False
    origin = choose_origin(size, gz, tuple(origin_arg) if origin_arg else DEFAULT_ORIGIN)
    if origin is None:
        row("plan_origin", "FAIL", "no geyser-free site of %dx%d on a %d map" % (SITE_W, SITE_H, size))
        return False
    names = {d for d, _s in FURN} | {d for d, _n, _s in ITEMS} | {d for d, _s in MINI}
    defs = read_defs(names, ("stuffCategories",))
    sizes, stuff, bad = {}, {}, []
    for dn in names:
        try:
            st = pick_stuff((defs.get(dn) or {}).get("stuffCategories"))
        except LayoutError:
            bad.append(dn)
            continue
        if st:
            stuff[dn] = st
    furn = {x for x, _ in FURN}
    measured = measure_footprints(sorted(furn - set(bad)), stuff, size)
    for dn in names - set(bad):
        sz = measured.get(dn) if dn in furn else (1, 1)
        if sz is None:
            bad.append(dn)
            continue
        sizes[dn] = sz
    if bad:
        row("plan_defs", "UNMEASURED", "size/stuff unreadable for %s" % sorted(bad))
        return False
    try:
        things = scene_things(sizes)
    except LayoutError as ex:
        row("plan_layout", "FAIL", str(ex))
        return False
    plan = {"origin": list(origin), "map_size": size, "geysers": gz, "sizes": sizes, "stuff": stuff, "things": things,
            "copies": copies_for(origin), "site": list(site_rect(origin)), "captures": capture_list(origin)}
    with open(plan_path(), "w") as fh:
        json.dump(plan, fh, indent=1)
    with open(os.path.join(OUT, "BIG_PIT_KEY.md"), "w") as fh:
        fh.write(key_markdown(plan))
    with open(os.path.join(OUT, "capture_list.json"), "w") as fh:
        json.dump(plan["captures"], fh, indent=1)
    log("plan", {"origin": origin, "things": len(things), "stuffed_defs": len(stuff), "geysers_on_map": len(gz)})
    row("plan", "PASS", "origin %s, %d things, all inside the %dx%d interior (margin %d)" % (origin, len(things), PW - 2 * MARGIN, PW - 2 * MARGIN, MARGIN))
    return True


def sky_gate(plan, when, clear=False):
    bridge()                      # puts Utils on sys.path: verify's first act is this gate (ModuleNotFoundError live, 2026-11-12)
    import validation_core as V
    rect = tuple(plan["site"])
    v = V.open_sky_site(bridge(), rect) if clear else V.assert_open_sky(bridge(), rect)
    log("open_sky_" + when, {k: v.get(k) for k in ("ok", "rect", "roofCells", "rockCells", "why", "cleared")})
    if not v.get("ok"):
        row("site_open_sky_" + when, "UNMEASURED", v.get("why"))
        dump()
        sys.exit(2)


def wild_pawns():
    """Every spawned non-player pawn on the map (wild animals, visitors, hostiles); None when unreadable."""
    r = call("jawa/list_pawns", faction="nonplayer", limit=500)
    if r.get("success") is False or r.get("pawns") is None:
        return None
    return r["pawns"]


def clear_wildlife():
    """Kill every non-player pawn on the map, remove its corpse, hold wild spawners off; assert none left."""
    call("jawa/wild_spawner_block", action="block", minutes=240)
    pawns = wild_pawns()
    if pawns is None:
        row("wildlife_clear", "UNMEASURED", "list_pawns unreadable")
        return
    for p in pawns:
        call("jawa/damage", damageDef="Blunt", amount=1000.0, thingId=p.get("id"))
    cells = set()
    r = call("jawa/list_things", group="Corpse", limit=500)
    for t in r.get("things") or []:
        cells.add((t["x"], t["z"]))
    for k in range(0, len(cells), 300):
        call("jawa/destroy_batch", rects=";".join("%d,%d,1,1" % c for c in sorted(cells)[k:k + 300]), categories="Item")
    left = wild_pawns()
    row("wildlife_none_left", "PASS" if left == [] else ("UNMEASURED" if left is None else "FAIL"),
        {"killed": len(pawns), "left": [(p.get("kind"), p.get("x"), p.get("z")) for p in (left or [])][:10]})


def assert_no_geyser(plan):
    gz = geysers_on_map()
    x0, z0, w, h = plan["site"]
    near = [g for g in (gz or []) if x0 - GEYSER_CLEAR <= g[0] < x0 + w + GEYSER_CLEAR and z0 - GEYSER_CLEAR <= g[1] < z0 + h + GEYSER_CLEAR]
    row("site_no_geyser", "UNMEASURED" if gz is None else "PASS" if not near else "FAIL", near or "no SteamGeyser within %d of the site" % GEYSER_CLEAR)


def stack_limits(names):
    lim = {}
    for dn, d in read_defs(names, ("stackLimit",)).items():
        try:
            lim[dn] = int(d.get("stackLimit"))
        except (TypeError, ValueError):
            pass
    return lim


def pawn_ids(r):
    out = []
    for v in r.values() if isinstance(r, dict) else []:
        if isinstance(v, list):
            out += [p.get("id") for p in v if isinstance(p, dict) and p.get("id")]
    return out


def spawn_stuffed(dn, x, z, n, plan):
    """One thing through jawa/spawn_batch, always with the stuff a stuffable def needs."""
    st = plan["stuff"].get(dn)
    kw = {"ops": "%s:%d,%d,%d" % (dn, x, z, n)}
    if st:
        kw["stuff"] = st
    return call("jawa/spawn_batch", **kw)


def stage(plan):
    x, z, w, h = plan["site"]
    rect = "%d,%d,%d,%d" % (x, z, w, h)
    log("reset", static("ProofResetRect", rect))
    clear_wildlife()
    sky_gate(plan, "before_stage", clear=True)
    log("cleared", {k: v for k, v in call("jawa/destroy_batch", rects=rect, categories="All").items() if k in ("success", "destroyed", "counts", "skippedUndestroyable")})
    call("jawa/set_fog", action="unfog", rect=rect)
    call("jawa/set_terrain_batch", ops="Soil:" + rect)
    sky_gate(plan, "after_clear")
    assert_no_geyser(plan)
    call("jawa/weather_set", weather="Clear", lockWeather=True)
    bad = 0
    for key, x0, z0, f, fl in plan["copies"]:
        for i in range(PW):
            for j in range(PW):
                r = call("jawa/flowworks_excavation_drive", x=x0 + i, z=z0 + j, deepenLevels=DEPTH, setBodyWaterM=-1, fillInLevels=0)
                bad += r.get("success") is False
    log("dig_failed_calls", bad)
    bridge().ticks(70)            # one swim refresh on the fresh dry pits (see pit_fittings_matrix stage)
    lim = stack_limits({r[2] for r in plan["things"]})
    call("rimworld/set_god_mode", enabled=True)
    route, baseline = {}, {}
    for key, x0, z0, f, fl in plan["copies"]:
        for kind, k2, dn, _src, (i, j), n in plan["things"]:
            cx, cz = x0 + i, z0 + j
            if kind == "furn":
                r = spawn_stuffed(dn, cx, cz, 1, plan)
                ok = r.get("success") is True and (r.get("thingsPlaced") or 0) >= 1
                route.setdefault(dn, set()).add("spawn_batch " + ("ok" if ok else "FAILED " + str(r)[:120]))
            elif kind == "item":
                spawn_stuffed(dn, cx, cz, min(n, lim.get(dn, n)), plan)
            elif kind == "mini":
                spawn_stuffed(dn, cx, cz, 1, plan)
                t = call("jawa/list_things", defName=dn, rect="%d,%d,1,1" % (cx, cz), limit=5).get("things") or []
                m = call("jawa/thing_minify", thing=str(t[0]["id"]).replace("Thing_", "")) if t else {"success": False}
                route.setdefault("minify " + dn, set()).add(str(m.get("success")))
            else:
                p = call("jawa/spawn_pawn", kindDef=dn, x=cx, z=cz, faction="none")
                ids = pawn_ids(p)
                for pid in ids:        # nothing may drop from a corpse: strip BEFORE the kill (lesson villager-corpse-drops-inventory)
                    call("jawa/pawn_gear", pawn=pid, action="clear", clearWhat="all")
                dres = [call("jawa/damage", damageDef="Blunt", amount=500.0, thingId=pid) for pid in ids]
                route.setdefault("corpse " + dn, set()).add("ids %s damage %s" % (ids, [d.get("success") for d in dres]))
        th = call("jawa/list_things", rect="%d,%d,%d,%d" % (x0, z0, PW, PW), limit=2000).get("things") or []
        baseline[key] = {"%s@%d,%d" % (t["def"], t["x"] - x0, t["z"] - z0): t.get("hitPoints") for t in th}
    call("rimworld/set_god_mode", enabled=False)
    with open(os.path.join(OUT, "spawn_baseline.json"), "w") as fh:
        json.dump(baseline, fh)
    log("routes", {k: sorted(v) for k, v in route.items()})
    labels(plan)


def fill(plan):
    for key, x0, z0, f, fl in plan["copies"]:
        if f:
            log("fill_" + key, static("ProofFillRect", "%d,%d,%d,%d,%g%s" % (x0, z0, PW, PW, f * 0.5, ("," + fl) if fl else "")))
    time.sleep(3)


def label_ops(plan):
    sys.path.insert(0, os.path.join(os.environ.get("RM_REPO", r"D:\Luke\dev\RimMandrake"), "src", "RimMandrake", "Utils"))
    from modcheck.reviewmap import label_line
    ox, oz = plan["origin"]
    ops = [label_line(ox + HEADER_AT[0], oz + HEADER_AT[1], "BIG PIT SERIES", "one 16x16 pit 4.0 m deep, copied 7x; same items, same cells",
                      "#ffd27f", "large", "bigpit")]
    for key, x0, z0, f, fl in plan["copies"]:
        what = "dry" if not f else "%.1f m %s" % (f * 0.5, "tar" if fl else "water") + (" (brim)" if f == DEPTH else "")
        ops.append(label_line(x0 + 2, z0 + PW + 1, key.split("_")[0] + " " + what, "pit 4.0 m deep, SW corner %d,%d" % (x0, z0),
                              "#bfe4ff", "medium", "bigpit"))
    return ops


def labels(plan):
    call("jawa/review_label", action="clear", tag="bigpit")
    r = call("jawa/review_label", action="add", ops="\n".join(label_ops(plan)))
    log("labels", {k: r.get(k) for k in ("success", "added", "message") if k in r})


def verify(plan):
    sky_gate(plan, "before_verify")
    assert_no_geyser(plan)
    left = wild_pawns()
    row("wildlife_none_on_map", "UNMEASURED" if left is None else "PASS" if not left else "FAIL",
        [(p.get("kind"), p.get("x"), p.get("z")) for p in (left or [])][:10] or "no non-player pawn on the map")
    try:
        with open(os.path.join(OUT, "spawn_baseline.json")) as fh:
            baseline = json.load(fh)
    except OSError:
        baseline = {}
    sizes = {k: tuple(v) for k, v in plan["sizes"].items()}
    things_tbl, sig = [], {}
    for key, x0, z0, f, fl in plan["copies"]:
        raw = call("jawa/list_things", rect="%d,%d,%d,%d" % (x0, z0, PW, PW), limit=2000)
        th = [t for t in raw.get("things") or [] if not str(t.get("def", "")).startswith(("Filth_", "Plant_"))]
        if raw.get("success") is False or not th:
            row(key + "_things_read", "UNMEASURED", str(raw)[:200])
            continue
        ex = call("jawa/flowworks_excavation_rect", x=x0, z=z0, w=PW, h=PW, includeTerrain=True)
        cells = {(c["x"] - x0, c["z"] - z0): c for c in ex.get("rows") or []}
        if len(cells) != PW * PW:
            row(key + "_depth_fill", "UNMEASURED", "excavation_rect returned %d cells" % len(cells))
        else:
            off = [(i, j, c.get("d"), levels(c, None)) for (i, j), c in cells.items() if c.get("d") != DEPTH or levels(c, None) != f]
            row(key + "_depth_fill", "PASS" if not off else "FAIL", off[:10] or "256 cells d=%d f=%d" % (DEPTH, f))
        sig[key] = collections.Counter((t["def"], t["x"] - x0, t["z"] - z0, t.get("stackCount")) for t in th)
        at = collections.defaultdict(list)
        for t in th:
            at[(t["x"] - x0, t["z"] - z0)].append(t)
        base = baseline.get(key, {})
        # one row per building kind, per item kind, per corpse: position, in-pit, liquid over it, stuff, HP against spawn baseline
        for kind, k2, dn, _src, (i, j), n in plan["things"]:
            want_def = "MinifiedThing" if kind == "mini" else ("Corpse_" + dn) if kind == "corpse" else dn
            found = [t for t in at[(i, j)] if (t["def"] == want_def or (kind == "corpse" and str(t["def"]).startswith("Corpse_")))]
            name = "%s_%s_%s" % (key, kind, dn)
            if not found:
                row(name, "FAIL", {"missing at": [i, j], "have": [t["def"] for t in at[(i, j)]]})
                continue
            t = found[0]
            fl_n = levels(cells.get((i, j)), 0) or 0
            v, det = judge_thing(t, x0, z0, fl_n, (want_def, i, j), sizes)
            if dn in plan["stuff"] and kind in ("furn", "item"):
                det["stuff"] = t.get("stuff")
                if not t.get("stuff"):
                    v = "FAIL"
            if kind in ("furn", "item") and t.get("maxHitPoints"):
                hv = judge_hp(t.get("hitPoints"), base.get("%s@%d,%d" % (t["def"], i, j)))
                det["hp"], det["hpBaseline"], det["hpVerdict"] = t.get("hitPoints"), base.get("%s@%d,%d" % (t["def"], i, j)), hv
                if hv == "FAIL" or (hv == "UNMEASURED" and v == "PASS"):
                    v = "FAIL" if hv == "FAIL" else "UNMEASURED"
            if kind in ("furn", "corpse", "mini"):
                row(name, v, det)
            things_tbl.append([key, kind, dn, v, det])
            if kind == "item" and v != "PASS":
                row(name, v, det)
        planned_footprint_cells = set()
        for kind, k2, dn, _s, (i, j), n in plan["things"]:
            planned_footprint_cells |= footprint(i, j, *(sizes.get(dn, (1, 1)) if kind == "furn" else (1, 1)), 0)
        stray = [(t["def"], t["x"] - x0, t["z"] - z0) for t in th if (t["x"] - x0, t["z"] - z0) not in planned_footprint_cells]
        row(key + "_nothing_unplanned", "PASS" if not stray else "FAIL", stray[:12] or "every thing is on a planned cell")
        row(key + "_inside_margin", "PASS" if all(inside({(t["x"] - x0, t["z"] - z0)}) for t in th) else "FAIL",
            "every thing's cell is at least %d cells from each pit wall" % MARGIN)
        # label record: the text a cell must read (PitLabel) from the TRUE depth and fill; the ON-SCREEN text has no reader
        fluid_label = "tar" if fl else "water"
        lab = {}
        for (i, j), c in cells.items():
            lab["%d,%d" % (i, j)] = expected_label(int(c.get("d") or 0), levels(c, 0), fluid_label)
        row(key + "_label_expected", "PASS", {"distinct": sorted(set(lab.values())), "cells": len(lab)})
    if "BP0_dry" in sig:
        ref = sig["BP0_dry"]
        for key, s in sig.items():
            if key != "BP0_dry":
                d1, d2 = ref - s, s - ref
                row(key + "_same_as_dry_copy", "PASS" if not d1 and not d2 else "FAIL",
                    {"onlyInDry": [list(k) for k in d1][:8], "onlyHere": [list(k) for k in d2][:8]} if d1 or d2 else
                    "%d things identical in def, offset and stack" % sum(s.values()))
    row("label_onscreen_text", "UNMEASURED",
        "no bridge reader for RM_MapComponent_Excavation.PitLabelAt (instance method; mouseover only): expected text recorded, "
        "actual text owed (item RIMMANDRAKE_ADD_PIT_LABEL_STATE_READER_MOUSEOVER_HAS_NONE)")
    with open(os.path.join(OUT, "bigpit_things_table.json"), "w") as fh:
        json.dump(things_tbl, fh, indent=0, default=str)


def shot(name, cx, cz, root):
    import shutil
    call("jawa/clear_ui", all=True)
    call("rimworld/jump_camera_to_cell", x=int(cx), z=int(cz))
    call("rimworld/set_camera_zoom", rootSize=root)
    time.sleep(1.5)
    r = call("jawa/take_screenshot", fileName="bp_%s_%d" % (name, int(time.time())))
    src = r.get("filePath")
    for _ in range(12):
        if src and os.path.exists(src):
            break
        time.sleep(0.5)
    if not src or not os.path.exists(src):
        log("shot_failed", {"name": name, "r": str(r)[:200]})
        return None
    dst = os.path.join(OUT, "bp_" + name + ".png")
    shutil.copyfile(src, dst)
    return dst


def shots(plan):
    files = {c["name"]: shot(c["name"], c["cx"], c["cz"], c["rootSize"]) for c in plan["captures"]}
    log("shots", files)


def save(plan, name):
    """Pause, then write the keeper save and its sign sidecar (review labels of this scene)."""
    from modcheck.reviewmap import save_keeper
    call("rimworld/pause_game")
    log("save_keeper", save_keeper(bridge(), name, signs=label_ops(plan)))
    paused = call("rimworld/get_game_info").get("isPaused")
    row("paused_after_save", "PASS" if paused is True else "UNMEASURED" if paused is None else "FAIL", paused)


def main(argv):
    global OUT, STEP
    OUT, STEP = argv[1], argv[2]
    os.makedirs(OUT, exist_ok=True)
    t0 = time.time()
    if STEP == "plan":
        ok = do_plan([int(argv[3]), int(argv[4])] if len(argv) > 4 else None)
    else:
        ok = True
        plan = load_plan()
        if STEP == "stage":
            stage(plan)
        elif STEP == "fill":
            fill(plan)
        elif STEP == "verify":
            verify(plan)
        elif STEP == "labels":
            labels(plan)
        elif STEP == "shots":
            shots(plan)
        elif STEP.startswith("save:"):
            save(plan, STEP.split(":", 1)[1])
        elif STEP == "key":
            with open(os.path.join(OUT, "BIG_PIT_KEY.md"), "w") as fh:
                fh.write(key_markdown(plan))
        elif STEP == "captures":
            print(json.dumps(plan["captures"], indent=1))
    log("elapsed_s", round(time.time() - t0, 1))
    dump()
    print("TOTALS", collections.Counter(r["verdict"] for r in ROWS))
    if not ok or any(r["verdict"] == "UNMEASURED" for r in ROWS):
        return 2
    return 1 if any(r["verdict"] != "PASS" for r in ROWS) else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
