#!/usr/bin/env python3
"""walk_pens.py: stage one pen for each creature kind of a mod on a walk save, six animals in each, for the owner's look.

Page: design/specs/2026-11-24-walk-pens/boundary.md. Rule: src/RimMandrake/rimflow/roles/walk_brief.md (a walk save for a mod
that adds or changes creatures holds pens with six of each creature of the mod). Owner, 2026-11-24, on the Pyrelands walk:
"This walkthrough really should have already done that for me in pens, no reason not to."

    python3    src/RimMandrake/Utils/modcheck/walk_pens.py --roster <Mod>              offline: the kinds that get a pen
    python.exe src/RimMandrake/Utils/modcheck/walk_pens.py --mod <Mod> --stage [--save NAME]
                    LIVE, on the loaded walk save, paused: build the pens, spawn, check by state reads; with --save, save it
    python.exe src/RimMandrake/Utils/modcheck/walk_pens.py --mod <Mod> --check      LIVE: read the pens of the loaded save

A mod's walk staging calls stage(B, mod) before its save (Pyrelands: in_game/visit_9/scripts/walk_restage.py).

THE ROSTER is read at run time from the XML, parsed as elements: the mod's BiomeDefs' <wildAnimals>, then every patch under src/
that adds, removes or replaces children of that <wildAnimals>. A mod with no biome roster uses its own PawnKindDefs whose race is
not Humanlike. THE PEN: stone walls (BlocksGranite), no roof, one door on its south wall, sized by body size, a sign
"SIGN pen: <label> (<kind>)" one cell south-east of the door, and a review label. Six animals, wild: three male, three female;
one juvenile and one baby where the race has those stages; all face south. The block of pens goes where no station, water,
roof, pawn or fire is; if no such block exists it stages nothing and says COULD NOT STAGE. The game stays paused.

Exit codes of --stage and --check: 0 every pen holds six; 1 a pen is short or wrong (each named); 2 could not look or stage.
"""
import argparse
import glob
import json
import os
import re
import sys
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
TIERS = ("RimMandrake", "RimStarWars", "RimUtinni")
PEN_SIGN = "SIGN pen: "
LABEL_TAG = "pens"
LANE = 2              # cells between pens
STUFF = "BlocksGranite"


# ---------------------------------------------------------------------------------------------------- the roster (pure, offline)
def mod_dir(mod, root=REPO):
    for t in TIERS:
        d = os.path.join(root, "src", t, mod)
        if os.path.isdir(d):
            return d
    return None


def _xml_files(d):
    return sorted(glob.glob(os.path.join(d, "**", "*.xml"), recursive=True))


def _parse(path):
    try:
        return ET.parse(path).getroot()
    except (ET.ParseError, OSError):
        return None


def _cast_of(wild):
    """<wildAnimals> element -> kinds, in order. Shorthand <Kind>w</Kind> or <li><animal>Kind</animal>."""
    out = []
    for ch in wild:
        if not isinstance(ch.tag, str):
            continue
        if ch.tag == "li":
            a = ch.find("animal")
            if a is not None and (a.text or "").strip():
                out.append(a.text.strip())
        else:
            out.append(ch.tag)
    return out


def _biomes_in(d):
    """-> {biome defName: [kinds]} for the BiomeDefs in folder d that declare <wildAnimals>."""
    out = {}
    for f in _xml_files(d):
        r = _parse(f)
        if r is None:
            continue
        for b in r.iter("BiomeDef"):
            name = (b.findtext("defName") or "").strip()
            wild = b.find("wildAnimals")
            if name and wild is not None:
                out[name] = _cast_of(wild)
    return out


def _ops(root_el):
    """Every Operation-like element of a patch file, FindMod / Sequence / Conditional children included."""
    for el in root_el.iter():
        if isinstance(el.tag, str) and el.get("Class", "").startswith("PatchOperation") and el.find("xpath") is not None:
            yield el


def _apply_patches(root, biome, cast):
    pat = re.compile(r"BiomeDef\[defName\s*=\s*[\"']%s[\"']\]/wildAnimals(?:/([A-Za-z0-9_]+))?\s*$" % re.escape(biome))
    cast = list(cast)
    for f in _xml_files(os.path.join(root, "src")):
        try:
            if biome not in open(f, encoding="utf-8", errors="replace").read():
                continue
        except OSError:
            continue
        r = _parse(f)
        if r is None or r.tag != "Patch":
            continue
        for op in _ops(r):
            m = pat.search((op.findtext("xpath") or "").strip())
            if not m:
                continue
            kind, cls = m.group(1), op.get("Class", "")
            val = op.find("value")
            if cls.endswith("Remove") and kind:
                cast = [k for k in cast if k != kind]
            elif cls.endswith("Add") and not kind and val is not None:
                cast += [k for k in _cast_of(val) if k not in cast]
            elif cls.endswith("Replace") and val is not None:
                inner = val.find("wildAnimals")
                new = _cast_of(inner if inner is not None else val)
                if kind:
                    i = cast.index(kind) if kind in cast else len(cast)
                    cast = cast[:i] + [k for k in new if k not in cast] + cast[i + 1:]
                else:
                    cast = new
    return cast


def biome_cast(root, biome):
    """The cast of one biome after the patches under src/ (the biome may live in any mod folder)."""
    base = []
    for t in TIERS:
        for d in sorted(glob.glob(os.path.join(root, "src", t, "*"))):
            b = _biomes_in(d)
            if biome in b:
                base = b[biome]
                break
        if base:
            break
    return _apply_patches(root, biome, base)


def _animal_kinds(d):
    races, kinds = {}, []
    roots = [r for r in (_parse(f) for f in _xml_files(os.path.join(d, "Defs"))) if r is not None]
    for r in roots:
        for td in r.iter("ThingDef"):
            race = td.find("race")
            if race is not None and (td.findtext("defName") or "").strip():
                races[td.findtext("defName").strip()] = (race.findtext("intelligence") or "Animal").strip()
    for r in roots:
        for pk in r.iter("PawnKindDef"):
            name, race = (pk.findtext("defName") or "").strip(), (pk.findtext("race") or "").strip()
            if name and pk.get("Abstract", "").lower() != "true" and races.get(race, "Humanlike") != "Humanlike":
                kinds.append(name)
    return kinds


def roster(mod, root=REPO):
    """-> {"kinds": [...], "biomes": [...], "from": "biome" | "pawnkinds" | "no mod folder"}."""
    d = mod_dir(mod, root)
    if not d:
        return {"kinds": [], "biomes": [], "from": "no mod folder"}
    biomes = sorted(_biomes_in(d))
    if biomes:
        kinds = []
        for b in biomes:
            kinds += [k for k in biome_cast(root, b) if k not in kinds]
        return {"kinds": kinds, "biomes": biomes, "from": "biome"}
    return {"kinds": _animal_kinds(d), "biomes": [], "from": "pawnkinds"}


# ---------------------------------------------------------------------------------------------------- the layout (pure)
def interior(body_size):
    """Inside side of a pen, in cells: six animals with room to see each."""
    for lim, side in ((1.0, 8), (2.0, 10), (3.0, 12), (6.0, 14)):
        if body_size < lim:
            return side
    return 20


def layout(sizes, max_w=96):
    """{kind: bodySize} -> (pens, W, H): rows of square pens, small to large, LANE cells apart, relative to (0, 0)."""
    kinds = sorted(sizes, key=lambda k: (sizes[k], k))
    rows, cur, curw = [], [], 0
    for k in kinds:
        w = interior(sizes[k]) + 2
        if cur and curw + LANE + w > max_w:
            rows.append(cur)
            cur, curw = [], 0
        cur.append((k, w))
        curw += (LANE if len(cur) > 1 else 0) + w
    if cur:
        rows.append(cur)
    pens, z = [], 0
    for row in rows:
        x = 0
        for k, w in row:
            pens.append({"kind": k, "x": x, "z": z, "w": w, "h": w})
            x += w + LANE
        z += max(w for _, w in row) + LANE
    if not pens:
        return [], 0, 0
    return pens, max(p["x"] + p["w"] for p in pens), max(p["z"] + p["h"] for p in pens)


def door_cell(p):
    return p["x"] + p["w"] // 2, p["z"]


def wall_cells(p):
    x0, z0, w, h = p["x"], p["z"], p["w"], p["h"]
    cells = {(x, z0) for x in range(x0, x0 + w)} | {(x, z0 + h - 1) for x in range(x0, x0 + w)}
    cells |= {(x0, z) for z in range(z0, z0 + h)} | {(x0 + w - 1, z) for z in range(z0, z0 + h)}
    cells.discard(door_cell(p))
    return cells


def sign_cell(p):
    dx, dz = door_cell(p)
    return dx + 1, dz - 1


def pen_from_sign(kind_w, sx, sz):
    """The inverse of sign_cell for a square pen of side kind_w."""
    return {"x": sx - 1 - kind_w // 2, "z": sz + 1, "w": kind_w, "h": kind_w}


def spawn_cells(p):
    x0, z0, w, h = p["x"], p["z"], p["w"], p["h"]
    xs = [x0 + 1 + (w - 2) // 4, x0 + w // 2, x0 + w - 2 - (w - 2) // 4]
    zs = [z0 + 1 + (h - 2) // 3, z0 + h - 2 - (h - 2) // 3]
    return [(x, z) for z in zs for x in xs]


def station_cells(points, radius, size):
    """Every cell within `radius` (Chebyshev) of a station sign or label, inside a map of `size` (W, H)."""
    W, H = size
    out = set()
    for sx, sz in points:
        for x in range(max(0, sx - radius), min(W, sx + radius + 1)):
            for z in range(max(0, sz - radius), min(H, sz + radius + 1)):
                out.add((x, z))
    return out


def pick_site(size, blocked, cost, W, H, margin=3, prefer=None):
    """-> (ox, oz) of a W x H block whose rect plus `margin` holds no blocked cell and the least cost, nearest `prefer`
    (default: the map centre); None when no such block exists. Never returns a block over a blocked cell."""
    MW, MH = size
    if W + 2 * margin > MW or H + 2 * margin > MH:
        return None
    px, pz = prefer or (MW / 2.0, MH / 2.0)
    Pb = [[0] * (MH + 1) for _ in range(MW + 1)]
    Pc = [[0] * (MH + 1) for _ in range(MW + 1)]
    for x in range(MW):
        for z in range(MH):
            Pb[x + 1][z + 1] = (1 if (x, z) in blocked else 0) + Pb[x][z + 1] + Pb[x + 1][z] - Pb[x][z]
            Pc[x + 1][z + 1] = cost.get((x, z), 0) + Pc[x][z + 1] + Pc[x + 1][z] - Pc[x][z]
    rs = lambda P, x0, z0, x1, z1: P[x1][z1] - P[x0][z1] - P[x1][z0] + P[x0][z0]  # noqa: E731
    best = None
    for oz in range(margin, MH - H - margin + 1):
        for ox in range(margin, MW - W - margin + 1):
            a = (ox - margin, oz - margin, ox + W + margin, oz + H + margin)
            if rs(Pb, *a):
                continue
            key = (rs(Pc, *a), abs(ox + W / 2.0 - px) + abs(oz + H / 2.0 - pz), ox, oz)
            if best is None or key < best:
                best = key
    return None if best is None else (best[2], best[3])


def stage_at(stages, age):
    """stages [(minAge, def)], age -> the def that age falls in."""
    cur = stages[0][1]
    for m, d in sorted(stages):
        if age >= m:
            cur = d
    return cur


def age_plan(stages):
    """-> six (gender, life stage, biological age): 3 male then 3 female; index 2 the stage before adult (juvenile), index 5
    the first stage (baby); with two stages both young ones are the first stage; with one stage all are adult."""
    st = sorted(stages)
    adult_min, adult = st[-1]
    adult_age = round(adult_min * 1.25 + 0.1, 3)
    plan = []
    for i in range(6):
        g = "Male" if i < 3 else "Female"
        if len(st) >= 3 and i == 2:
            m0, m1 = st[-2][0], st[-1][0]
            plan.append((g, st[-2][1], round((m0 + m1) / 2.0, 3)))
        elif len(st) >= 2 and i in (2, 5):
            m1 = st[1][0]
            plan.append((g, st[0][1], round(st[0][0] + (m1 - st[0][0]) / 2.0, 3)))
        else:
            plan.append((g, adult, adult_age))
    return plan


def judge_pen(kind, pawns):
    """pawns: the list_pawns rows inside the pen (None = could not read) -> {kind, verdict, ...}."""
    if pawns is None:
        return {"kind": kind, "verdict": "COULD NOT LOOK", "why": "no pawn list for the pen"}
    living = [p for p in pawns if not p.get("dead")]
    of_kind = [p for p in living if p.get("kindDef") == kind]
    hostile = sum(1 for p in living if p.get("hostile"))
    mental = sum(1 for p in living if p.get("inMentalState") or p.get("mentalState"))
    ok = len(of_kind) == 6 and len(living) == 6 and not hostile and not mental
    return {"kind": kind, "verdict": "PASS" if ok else "FAIL", "of_kind": len(of_kind), "living": len(living),
            "hostile": hostile, "mental": mental}


def exit_code(rows):
    if not rows or any(r["verdict"] == "COULD NOT LOOK" for r in rows):
        return 2
    return 0 if all(r["verdict"] == "PASS" for r in rows) else 1


# ---------------------------------------------------------------------------------------------------- live (python.exe, bridge)
def _ops_cells(ops):
    out = {}
    for part in str(ops or "").split(";"):
        if ":" not in part:
            continue
        d, rest = part.rsplit(":", 1)
        try:
            v = [int(a) for a in rest.split(",")]
        except ValueError:
            continue
        w, h = (v[2] if len(v) > 2 else 1), (v[3] if len(v) > 3 else 1)
        for i in range(w):
            for j in range(h):
                out[(v[0] + i, v[1] + j)] = d
    return out


def paused(B):
    import time
    B.call("rimworld/set_time_speed", speed=0)
    a = B.call("rimworld/get_game_info").get("ticksGame")
    time.sleep(1.5)
    b = B.call("rimworld/get_game_info").get("ticksGame")
    return a is not None and a == b, a


def live_cast(B, kinds):
    """-> (race {kind: race}, size {kind: bodySize}, stages {kind: [(minAge, def)]}, label {kind: label}, not_loaded [kinds])."""
    pk = B.call("jawa/get_defs", defs=";".join("PawnKindDef/" + k for k in kinds), fields="label,race")
    race, label = {}, {}
    for d in pk.get("defs") or []:
        if d.get("found"):
            v = (d.get("fields") or {}).get("race")
            race[d["defName"]] = v if isinstance(v, str) else (v or {}).get("defName", str(v))
            label[d["defName"]] = (d.get("fields") or {}).get("label") or d.get("label") or d["defName"]
    not_loaded = [k for k in kinds if k not in race]
    s = B.call("jawa/animal_stats", defs=",".join(sorted(set(race.values()))))
    bs = {r.get("defName"): r.get("bodySize") for r in (s.get("animals") or s.get("rows") or [])}
    rd = B.call("jawa/get_defs", defs=";".join("ThingDef/" + r for r in sorted(set(race.values()))), fields="race", deep=True)
    lsa = {}
    for d in rd.get("defs") or []:
        rr = (d.get("fields") or {}).get("race") or {}
        lsa[d.get("defName")] = [(float(x.get("minAge", 0)), x.get("def")) for x in rr.get("lifeStageAges") or []] or [(0.0, "Adult")]
    size = {k: bs.get(race[k]) for k in race}
    stages = {k: lsa.get(race[k], [(0.0, "Adult")]) for k in race}
    missing = [k for k in race if size[k] is None]
    for k in missing:
        not_loaded.append(k)
        race.pop(k)
    return race, {k: v for k, v in size.items() if v is not None}, stages, label, not_loaded


def _pen_pawns(B, p):
    r = B.call("jawa/list_pawns", rect="%d,%d,%d,%d" % (p["x"] + 1, p["z"] + 1, p["w"] - 2, p["h"] - 2))
    if not r.get("success", True) and "pawns" not in r:
        return None
    rows = r.get("pawns") or []
    ids = [q.get("id") for q in rows if q.get("id")]
    if ids:
        cen = {c.get("id"): c for c in B.call("jawa/pawn_census", ids=",".join(ids)).get("pawns") or []}
        for q in rows:
            c = cen.get(q.get("id")) or {}
            q["inMentalState"] = bool(c.get("inMentalState") or c.get("mentalState"))
    return rows


def site_grid(B, W, H, station_radius=16, fire_berth=12):
    """-> (size, blocked, cost, points): what pick_site needs, read from the live map."""
    mi = B.call("jawa/map_info")
    size = (int(mi.get("sizeX") or 0), int(mi.get("sizeZ") or 0))
    if not size[0] or not size[1]:
        raise RuntimeError("COULD NOT LOOK: jawa/map_info gave no sizeX/sizeZ: %s" % str(mi)[:200])
    rect = "0,0,%d,%d" % size
    terr = _ops_cells(B.call("jawa/get_terrain_batch", rects=rect).get("ops"))
    roof = _ops_cells(B.call("jawa/get_roof_batch", rects=rect).get("ops"))
    every = B.call("jawa/list_things", rect=rect, group="Everything", limit=400000)
    if every.get("isCompleteList") is False:
        raise RuntimeError("COULD NOT LOOK: list_things Everything is not complete")
    soft = set()
    for g in ("Plant", "Filth", "HaulableEver"):
        soft |= {t["id"] for t in B.call("jawa/list_things", rect=rect, group=g, limit=400000).get("things") or []}
    hard = {(t["x"], t["z"]) for t in every.get("things") or [] if t["id"] not in soft}
    fires = B.call("jawa/list_things", rect=rect, group="Fire", limit=20000).get("things") or []
    pawns = {(p["x"], p["z"]) for p in B.call("jawa/list_pawns", limit=2000).get("pawns") or []}
    points = [(s["x"], s["z"]) for s in B.call("jawa/review_sign", action="list").get("signs") or []]
    labs = B.call("jawa/review_label", action="list")
    points += [(int(lb["x"]), int(lb["z"])) for lb in labs.get("labels") or [] if "x" in lb and "z" in lb]
    blocked = station_cells(points, station_radius, size) | station_cells([(f["x"], f["z"]) for f in fires], fire_berth, size)
    blocked |= pawns | {c for c, v in roof.items() if v not in ("None", "")}
    bad = ("Water", "Lava", "Marsh", "Mud", "Bridge", "Ice")
    blocked |= {c for c, d in terr.items() if any(s in d for s in bad)}
    hist = {}
    for d in terr.values():
        hist[d] = hist.get(d, 0) + 1
    common = set(sorted(hist, key=lambda d: -hist[d])[:3])
    cost = {c: 1 for c, d in terr.items() if d not in common}
    for c in hard:
        cost[c] = cost.get(c, 0) + 10
    return size, blocked, cost, points


def stage(B, mod, root=REPO, log=print):
    """Stage the pens of `mod` on the loaded, paused map. -> dict(ok, pens, signs, labels, rows, not_loaded, why)."""
    ok, tick = paused(B)
    if not ok:
        return {"ok": False, "why": "COULD NOT STAGE: the game did not hold paused", "rows": []}
    ro = roster(mod, root)
    if not ro["kinds"]:
        return {"ok": False, "why": "COULD NOT STAGE: no roster (%s)" % ro["from"], "rows": []}
    race, size, stages, label, not_loaded = live_cast(B, ro["kinds"])
    pens, W, H = layout(size)
    gsize, blocked, cost, points = site_grid(B, W, H)
    site = pick_site(gsize, blocked, cost, W, H, margin=3)
    if site is None:
        return {"ok": False, "why": "COULD NOT STAGE: no free %dx%d block away from the stations" % (W, H), "rows": [],
                "not_loaded": not_loaded}
    ox, oz = site
    pens = [dict(p, x=p["x"] + ox, z=p["z"] + oz) for p in pens]
    log("site %d,%d block %dx%d, %d pens" % (ox, oz, W, H, len(pens)))
    B.call("jawa/destroy_batch", rects="%d,%d,%d,%d" % (ox - 3, oz - 3, W + 6, H + 6), categories="Plant,Filth,Item,Building")
    B.call("jawa/set_roof_batch", ops="None:%d,%d,%d,%d" % (ox, oz, W, H))
    sign_ops, label_ops = [], []
    for p in pens:
        dx, dz = door_cell(p)
        ops = ";".join("Wall:%d,%d" % c for c in sorted(wall_cells(p))) + ";Door:%d,%d,0" % (dx, dz)
        B.call("jawa/build_batch", ops=ops, stuff=STUFF, faction="player", readBack=0)
        sx, sz = sign_cell(p)
        name = label.get(p["kind"], p["kind"])
        sign_ops.append("%d|%d|%s%s (%s)|Creature pen: six %s (%s), wild, three male and three female." %
                        (sx, sz, PEN_SIGN, name, p["kind"], name, p["kind"]))
        label_ops.append("%d|%d|%s|%s|#ffd27f|small|%s" % (dx, dz - 1, name, p["kind"], LABEL_TAG))
    B.call("jawa/review_sign", action="place", ops="\n".join(sign_ops))
    B.call("jawa/review_label", action="clear", tag=LABEL_TAG)
    B.call("jawa/review_label", action="add", tag=LABEL_TAG, ops="\n".join(label_ops))
    ids_all = []
    for p in pens:
        plan = age_plan(stages[p["kind"]])
        for (x, z), (g, st, age) in zip(spawn_cells(p), plan):
            before = {q.get("id") for q in (_pen_pawns(B, p) or [])}
            B.call("jawa/spawn_pawn", kindDef=p["kind"], x=x, z=z, faction="none", count=1)
            new = [q for q in (_pen_pawns(B, p) or []) if q.get("id") not in before]
            if not new:
                continue
            pid = new[0]["id"]
            ids_all.append(pid)
            g0 = (B.call("jawa/pawn_get", pawn=pid).get("pawns") or [{}])[0]
            if g0.get("gender") not in (None, "None", g):
                B.call("jawa/set_pawn_gender", pawn=pid, gender=g)
            if stage_at(stages[p["kind"]], float(g0.get("ageBiologicalYears") or 0)) != st:
                B.call("jawa/set_pawn_age", pawn=pid, biologicalYears=age, chronologicalYears=age, allowBackwards=True)
                g1 = (B.call("jawa/pawn_get", pawn=pid).get("pawns") or [{}])[0]
                if g1.get("gender") not in (None, "None"):       # dirty the renderer so the young graphic draws
                    B.call("jawa/set_pawn_gender", pawn=pid, gender=g1["gender"])
    if ids_all:
        B.call("jawa/set_pawn_rotation", pawnId=",".join(ids_all), dir="south", lockRotation=False)
    paused(B)
    rows = [judge_pen(p["kind"], _pen_pawns(B, p)) for p in pens]
    return {"ok": exit_code(rows) == 0, "site": site, "block": [W, H], "pens": pens, "signs": sign_ops, "labels": label_ops,
            "rows": rows, "not_loaded": not_loaded, "tick": tick}


def check(B, mod, root=REPO):
    """Read the pens of the loaded save from their signs. -> rows (judge_pen), one per roster kind."""
    ro = roster(mod, root)
    race, size, stages, label, not_loaded = live_cast(B, ro["kinds"])
    signs = B.call("jawa/review_sign", action="list").get("signs") or []
    at = {}
    for s in signs:
        m = re.match(r"^%s.*\(([A-Za-z0-9_]+)\)\s*$" % re.escape(PEN_SIGN), s.get("title") or "")
        if m:
            at[m.group(1)] = (s["x"], s["z"])
    rows = []
    for k in ro["kinds"]:
        if k in not_loaded:
            rows.append({"kind": k, "verdict": "COULD NOT LOOK", "why": "the game did not load this kind"})
        elif k not in at:
            rows.append({"kind": k, "verdict": "FAIL", "why": "no pen sign for this kind"})
        else:
            p = pen_from_sign(interior(size[k]) + 2, *at[k])
            rows.append(dict(judge_pen(k, _pen_pawns(B, p)), rect=[p["x"], p["z"], p["w"], p["h"]]))
    return rows


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--roster", metavar="MOD")
    ap.add_argument("--mod")
    ap.add_argument("--stage", action="store_true")
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--save", metavar="NAME")
    a = ap.parse_args(argv)
    if a.roster:
        r = roster(a.roster)
        print(json.dumps(r, indent=1))
        return 0 if r["kinds"] else 2
    if not a.mod or not (a.stage or a.check):
        ap.error("--roster MOD, or --mod MOD with --stage or --check")
    from modcheck import reviewmap as RM
    B = RM.LiveBridge()
    if a.stage:
        out = stage(B, a.mod)
        if out.get("ok") and a.save:
            stations = ["%d|%d|%s|" % (s["x"], s["z"], s["title"]) for s in
                        B.call("jawa/review_sign", action="list").get("signs") or [] if not s["title"].startswith(PEN_SIGN)]
            out["save"] = RM.save_keeper(B, a.save, saves=RM.SAVES, signs=stations + out["signs"])
            if not out["save"].get("ok"):
                out["ok"] = False
        print(json.dumps({k: v for k, v in out.items() if k not in ("signs", "labels")}, indent=1))
        rows = out.get("rows") or []
        rc = exit_code(rows) if rows else 2
        return rc if rc or not a.save or out.get("save", {}).get("ok") else 1
    rows = check(B, a.mod)
    for r in rows:
        print("%-14s %-16s %s" % (r["verdict"], r["kind"], {k: v for k, v in r.items() if k not in ("verdict", "kind")}))
    rc = exit_code(rows)
    print("WALK PENS %s: %d of %d pens hold six" % (("PASS", "FAIL", "COULD NOT LOOK")[rc], sum(r["verdict"] == "PASS" for r in rows),
                                                    len(rows)))
    return rc


if __name__ == "__main__":
    sys.path.insert(0, os.path.dirname(HERE))
    sys.exit(main())
