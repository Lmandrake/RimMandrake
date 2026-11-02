#!/usr/bin/env python3
"""geo_landmarks.py - the hand-placed geological landmarks, frozen for the one world paint.

Item GEO_LANDMARKS_SKETCH_BEFORE_THE_PAINT_DRIES (before-paint gate of BIOME_PAINT_ONCE_AT_THE_END_1).
Design: design/RimMandrake/world_remake_2026-10-19/16_geo_landmarks.md.

Two files, both committed:
  <spec>.csv         one row per landmark: id, name, kind, centre tile, rings, stones (now / planned), notes
  <spec>_tiles.csv   one row per (landmark, tile): the FROZEN tile list. This, not the centre and rings, is the
                     authority; `author` wrote it once from the dev planet and nothing re-derives it.

Hand-authored only (CLAUDE.md, owner 2026-08-15/18): the centres are chosen by hand, the tile list is written
once and frozen. Nothing here places landmarks by rule at runtime, and nothing can produce a second planet.

  author --save S [--dump D] [--spec P] [--rewrite]   write <spec>_tiles.csv from the spec (refuses to overwrite)
  check  [P|--spec P] [--save S] [--dump D]             PASS/FAIL; with --save also checks against the planet
  selftest                                            the rules on a toy graph, plus resolver sanity probes

Planet geometry is engine truth exported to world/world_tiles_sub7b.csv and world/world_neighbors_sub7b.csv
(see worldgeom.py). Arc = angle from the substellar point (0, 0) (the_one_map.md, THE GEOMETRY).
"""
import argparse, collections, csv, json, math, os, re, sys
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
UTILS = os.path.dirname(HERE)
REPO = os.path.dirname(os.path.dirname(os.path.dirname(UTILS)))
sys.path.insert(0, UTILS)

SPEC = os.path.join(REPO, "design", "RimMandrake", "world_remake_2026-10-19", "geo_landmarks.csv")
TILES_GEO = os.path.join(REPO, "world", "world_tiles_sub7b.csv")
NEIGHBOURS = os.path.join(REPO, "world", "world_neighbors_sub7b.csv")
LEDGER = os.path.join(REPO, "infrastructure", "state", "ledger")
SELF_ITEM = "GEO_LANDMARKS_SKETCH_BEFORE_THE_PAINT_DRIES"
PLANET_TILES = 21872
MIN_TILES, MAX_TILES = 7, 120
ID_RE = re.compile(r"^RM_Geo_[A-Z][A-Za-z]+$")
# Biomes a landmark never covers: the seas (their floor is the ship layer's business and their tiles are water)
# and the one biome that forces its own stone (a landmark there would REPLACE the cathedral's deck plate).
EXCLUDED_BIOMES = {"RM_TheScald", "RM_TwilightSea", "RM_GreySea", "RM_RustCathedral"}
# Biomes renamed in src/ after the dev save was written (commit 33596c33a9, BIOME_DEFNAME_MIGRATION_WAVE_1). The
# save still stores the OLD name's shortHash, which no current dump holds. An alias is used only when the old name's
# recomputed shortHash equals the save's hash EXACTLY and the new name is in the dump; any other undecoded hash FAILS.
RENAMED_BIOMES = {"RM_Wasteland": "RM_Wastes", "RM_NightsideIce": "RM_SleepingIce"}
SPEC_FIELDS = ["id", "name", "kind", "centre_tile", "rings", "label_tile", "stones_now", "stones_planned",
               "owed_item", "note"]


def short_hash(name):
    """RimWorld ShortHashGiver base hash: (ushort)(StableStringHash(name) % 65535), C# truncating %.
    skills/rimworld-savegame/SKILL.md section 5. A collision-bumped def is NOT matched (by design: exact only)."""
    h = 23
    for ch in name:
        h = (h * 31 + ord(ch)) & 0xFFFFFFFF
    if h >= 0x80000000:
        h -= 0x100000000
    return int(math.fmod(h, 65535)) & 0xFFFF


def alias_unresolved(unresolved, hash_by_biome, renamed=RENAMED_BIOMES):
    """-> ({hash: (old, new)}, [hashes still undecoded]). An alias needs an exact recomputed hash and a live new name."""
    by_old = {short_hash(o): (o, n) for o, n in renamed.items()}
    aliases, left = {}, []
    for h in unresolved:
        hit = by_old.get(h)
        if hit and hit[1] in hash_by_biome:
            aliases[h] = hit
        else:
            left.append(h)
    return aliases, left


def save_mod_ids(save):
    with open(save, encoding="utf-8", errors="replace") as fh:
        head = fh.read(2000000)
    a, b = head.find("<modIds>"), head.find("</modIds>")
    return [] if a < 0 or b < 0 else re.findall(r"<li>([^<]+)</li>", head[a:b])


def dump_mod_ids(dump):
    p = os.path.join(os.path.dirname(dump.rstrip("/\\")), "manifest.json")
    try:
        with open(p, encoding="utf-8") as fh:
            return [m.get("packageId", "") for m in json.load(fh).get("mods", [])]
    except (OSError, ValueError):
        return None


def split(v):
    return [s for s in (v or "").split(";") if s]


def read_spec(path):
    with open(path, encoding="utf-8", newline="") as fh:
        rows = list(csv.DictReader(fh))
    return rows


def tiles_path(spec):
    return spec[:-4] + "_tiles.csv"


def read_tiles(path):
    out = collections.OrderedDict()
    with open(path, encoding="utf-8", newline="") as fh:
        for r in csv.DictReader(fh):
            out.setdefault(r["id"], []).append(int(r["tile"]))
    return out


def read_neighbours(path=NEIGHBOURS):
    nb = {}
    with open(path, encoding="utf-8", newline="") as fh:
        for r in csv.DictReader(fh):
            nb[int(r["tile"])] = [int(r[k]) for k in ("n0", "n1", "n2", "n3", "n4", "n5") if int(r[k]) >= 0]
    return nb


def read_geo(path=TILES_GEO):
    geo = {}
    with open(path, encoding="utf-8", newline="") as fh:
        for r in csv.DictReader(fh):
            geo[int(r["tile"])] = (float(r["lat"]), float(r["long"]))
    return geo


def arc(lat, lon):
    la, lo = math.radians(lat), math.radians(lon)
    return math.degrees(math.acos(max(-1.0, min(1.0, math.cos(la) * math.cos(lo)))))


def rings(centre, k, nb):
    seen, front = {centre}, {centre}
    for _ in range(k):
        front = {n for t in front for n in nb[t]} - seen
        seen |= front
    return seen


def connected(tiles, nb):
    tiles = set(tiles)
    if not tiles:
        return False
    start = next(iter(tiles))
    seen, stack = {start}, [start]
    while stack:
        t = stack.pop()
        for n in nb.get(t, []):
            if n in tiles and n not in seen:
                seen.add(n)
                stack.append(n)
    return seen == tiles


# ---- stone resolution -------------------------------------------------------------------------------------
def src_rocks(root=os.path.join(REPO, "src")):
    """defName -> {'resource': bool, 'file': path} for every ThingDef under src/ whose parent is RockBase
    or which sets building/isNaturalRock."""
    out = {}
    for dp, _dn, fns in os.walk(root):
        for fn in fns:
            if not fn.endswith(".xml"):
                continue
            p = os.path.join(dp, fn)
            try:
                with open(p, encoding="utf-8") as fh:
                    txt = fh.read()
                if "RockBase" not in txt and "isNaturalRock" not in txt:
                    continue
                root_el = ET.fromstring(txt)
            except (ET.ParseError, UnicodeDecodeError, OSError):
                continue
            for e in root_el.iter("ThingDef"):
                dn = e.findtext("defName")
                b = e.find("building")
                natural = e.get("ParentName") == "RockBase" or (b is not None and b.findtext("isNaturalRock") == "true")
                if dn and natural:
                    res = b is not None and b.findtext("isResourceRock") == "true"
                    out[dn] = {"resource": res, "file": os.path.relpath(p, REPO)}
    return out


def dump_rocks(names):
    """defName -> {'resource': bool} for the names the def db knows as natural rock ThingDefs.
    Returns None when the db cannot be opened (UNMEASURED, never 'absent')."""
    try:
        import game_paths, dump_manifest
    except Exception:
        return None
    out = {}
    with dump_manifest.dump_db(game_paths.DUMP_ROOT, check_currency=False) as db:
        if db is None:
            return None
        q = "SELECT def_name, json FROM defs WHERE def_type='ThingDef' AND def_name IN (%s)" % ",".join("?" * len(names))
        for n, j in db.sql(q, tuple(names)):
            f = json.loads(j)
            f = f.get("fields", f)
            b = f.get("building") or {}
            if b.get("isNaturalRock"):
                out[n] = {"resource": bool(b.get("isResourceRock"))}
    return out


def resolve_stones(names, src=None, dump=None):
    src = src_rocks() if src is None else src
    dump = dump_rocks(sorted(set(names) | {"Granite"})) if dump is None else dump
    if dump is not None and "Granite" not in dump:
        raise SystemExit("UNMEASURED: the def db cannot see Granite, so it cannot be trusted to say a stone is absent")
    res = {}
    for n in names:
        if n in src:
            res[n] = dict(src[n], where="src")
        elif dump is not None and n in dump:
            res[n] = dict(dump[n], where="dump")
        else:
            res[n] = None
    return res, dump is not None


# ---- owed items: liveness from the LEDGER, not items/*.md ---------------------------------------------------
# The ledger is what ships with a commit into every checker's box; infrastructure/state/items/ is left out of a
# blind checker's tree on purpose (relentless_rules.json tree_exclude), so reading it there sees nothing.
TERMINAL = {"close", "drop", "supersede"}
OPENING = {"file", "claim", "start", "reclaim", "implemented"}


def ledger_states(root=LEDGER):
    """id -> last state-changing event ('file', 'close', ...), over events.jsonl and events/*.jsonl, by ts."""
    paths = [os.path.join(root, "events.jsonl")]
    ev_dir = os.path.join(root, "events")
    if os.path.isdir(ev_dir):
        paths += [os.path.join(ev_dir, n) for n in sorted(os.listdir(ev_dir)) if n.endswith(".jsonl")]
    last = {}
    for p in paths:
        if not os.path.exists(p):
            continue
        with open(p, encoding="utf-8") as f:
            for line in f:
                try:
                    e = json.loads(line)
                except ValueError:
                    continue
                ev, i = e.get("event"), e.get("id")
                if i and ev in TERMINAL | OPENING:
                    k = (e.get("ts") or "", ev)
                    if i not in last or k[0] >= last[i][0]:
                        last[i] = k
    return {i: ev for i, (_ts, ev) in last.items()}


def ledger_item_exists(root=LEDGER):
    """-> predicate 'is this a filed, not closed/dropped/superseded item'. Refuses (UNMEASURED) when the ledger
    cannot see this item's own file event: a ledger that is absent or unreadable says nothing about any item."""
    states = ledger_states(root)
    if SELF_ITEM not in states:
        raise SystemExit("UNMEASURED: the ledger at %s does not hold %s itself, so it cannot say an owed item is "
                         "live or dead" % (root, SELF_ITEM))
    return lambda i: states.get(i) in OPENING


# ---- the checks -------------------------------------------------------------------------------------------
def check(spec_rows, tiles, nb, stones, n_tiles=PLANET_TILES, item_exists=None, planet=None):
    """Return a list of failure strings (empty = PASS). `stones` maps defName -> info or None.
    `planet` (optional): {'biome': [..], 'landmark_tiles': set()} read from the save."""
    item_exists = item_exists or ledger_item_exists()
    fails = []
    ids, names, owner_of = set(), set(), {}
    for r in spec_rows:
        i = r["id"]
        tag = "%s:" % i
        if not ID_RE.match(i):
            fails.append("%s id is not RM_Geo_<Name>" % tag)
        if i in ids:
            fails.append("%s duplicate id" % tag)
        ids.add(i)
        if r["name"] in names:
            fails.append("%s duplicate name %r" % (tag, r["name"]))
        names.add(r["name"])
        ts = tiles.get(i)
        if not ts:
            fails.append("%s no frozen tiles" % tag)
            continue
        if len(set(ts)) != len(ts):
            fails.append("%s a tile is listed twice" % tag)
        if not (MIN_TILES <= len(set(ts)) <= MAX_TILES):
            fails.append("%s %d tiles, outside %d..%d" % (tag, len(set(ts)), MIN_TILES, MAX_TILES))
        bad = [t for t in ts if not 0 <= t < n_tiles]
        if bad:
            fails.append("%s tiles off the planet: %s" % (tag, bad[:5]))
            continue
        for t in ts:
            if t in owner_of and owner_of[t] != i:
                fails.append("%s tile %d also belongs to %s" % (tag, t, owner_of[t]))
            owner_of[t] = i
        c, lab = int(r["centre_tile"]), int(r["label_tile"])
        if c not in ts:
            fails.append("%s centre %d not in its own tiles" % (tag, c))
        if lab not in ts:
            fails.append("%s label tile %d not in its own tiles" % (tag, lab))
        if not connected(ts, nb):
            fails.append("%s tiles are not one connected patch" % tag)
        now, planned = split(r["stones_now"]), split(r["stones_planned"])
        if not now:
            fails.append("%s no stones_now" % tag)
        for s in now:
            if stones.get(s) is None:
                fails.append("%s stone %s does not resolve (stones_now takes only existing defs)" % (tag, s))
        # RM_PreciousCaves.cs:846 picks a NON-resource natural rock from the list; give it one.
        if now and all(stones.get(s) is not None for s in now) and all(stones[s]["resource"] for s in now):
            fails.append("%s every stone_now is a resource rock; RM_PreciousCaves needs a plain one" % tag)
        owed = r["owed_item"].strip()
        for s in planned:
            if stones.get(s) is None:
                if not owed:
                    fails.append("%s planned stone %s does not exist and no owed_item names who builds it" % (tag, s))
        if owed and not item_exists(owed):
            fails.append("%s owed_item %s is not a live item (ledger: never filed, or closed/dropped/superseded)" % (tag, owed))
        if planet is not None:
            biomes = {planet["biome"][t] for t in ts}
            hit = sorted(biomes & EXCLUDED_BIOMES)
            if hit:
                fails.append("%s covers excluded biome(s) %s" % (tag, hit))
            if lab in planet["landmark_tiles"]:
                fails.append("%s label tile %d already carries a landmark" % (tag, lab))
            # LandmarkDef.IsValidTile rejects a settlement tile (jawa/world_landmarks_set description)
            if lab in planet.get("settlement_tiles", set()):
                fails.append("%s label tile %d holds a settlement" % (tag, lab))
    for i in tiles:
        if i not in ids:
            fails.append("%s: frozen tiles for an id not in the spec" % i)
    return fails


def load_planet(save, dump):
    import worldmap
    g = worldmap.WorldGrid(save, dump)
    wo = worldmap.WorldObjects(save)
    aliases, left = alias_unresolved(g.unresolved(), g.hash_by_biome)
    biome = [aliases[h][1] if h in aliases else g.biome_by_hash.get(h, "?%d" % h) for h in g.arrays["tileBiome"]]
    sm, dm = save_mod_ids(save), dump_mod_ids(dump)
    return {"tiles": g.tiles, "biome": biome, "unresolved": left, "aliases": aliases,
            "known_biomes": set(g.hash_by_biome), "save_mods": sm, "dump_mods": dm,
            "landmark_tiles": {l["tile"] for l in wo.landmarks() if l["layer"] == 0},
            "settlement_tiles": {x["tile"] for x in wo.settlements() if x["layer"] == 0}}


def default_dump():
    import game_paths
    return os.path.join(game_paths.DEF_DUMP, "defs")


def cmd_author(a):
    spec = read_spec(a.spec)
    out = tiles_path(a.spec)
    if os.path.exists(out) and not a.rewrite:
        raise SystemExit("REFUSED: %s exists; the tile list is frozen (pass --rewrite to re-author by hand)" % out)
    nb, geo = read_neighbours(), read_geo()
    planet = load_planet(a.save, a.dump or default_dump())
    if not spec:
        raise SystemExit("REFUSED: %s has no landmark rows" % a.spec)
    rows = []
    for r in spec:
        ts = sorted(t for t in rings(int(r["centre_tile"]), int(r["rings"]), nb)
                    if planet["biome"][t] not in EXCLUDED_BIOMES)
        for t in ts:
            la, lo = geo[t]
            rows.append({"id": r["id"], "tile": t, "biome_at_authoring": planet["biome"][t],
                         "lat": "%.2f" % la, "long": "%.2f" % lo, "arc": "%.1f" % arc(la, lo)})
    with open(out, "w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()), lineterminator="\n")
        w.writeheader()
        w.writerows(rows)
    print("WROTE %s: %d rows for %d landmarks" % (os.path.relpath(out, REPO), len(rows), len(spec)))


def cmd_check(a):
    spec = read_spec(a.spec)
    tiles = read_tiles(tiles_path(a.spec))
    nb = read_neighbours()
    names = sorted({s for r in spec for s in split(r["stones_now"]) + split(r["stones_planned"])})
    stones, measured = resolve_stones(names)
    if not measured:
        print("UNMEASURED: def db unavailable; only src/ stones resolve")
    planet = None
    if a.save:
        planet = load_planet(a.save, a.dump or default_dump())
        if planet["tiles"] != PLANET_TILES:
            print("FAIL: save has %d tiles, not %d" % (planet["tiles"], PLANET_TILES))
            return 1
        rc = fingerprint(planet)
        if rc:
            return rc
    fails = check(spec, tiles, nb, stones, planet=planet)
    geo = read_geo()
    for r in spec:
        ts = tiles.get(r["id"], [])
        la, lo = geo.get(int(r["centre_tile"]), (float("nan"), float("nan")))
        line = "%-20s %-22s %3d tiles  centre %5s (lat %.1f, long %.1f, arc %.0f)  now %s" % (
            r["id"], r["name"], len(ts), r["centre_tile"], la, lo, arc(la, lo), r["stones_now"])
        if planet is not None:
            bc = collections.Counter(planet["biome"][t] for t in ts).most_common()
            line += "  biomes %s" % ",".join("%s:%d" % kv for kv in bc)
        print(line)
    if fails:
        for f in fails:
            print("FAIL " + f)
        return 1
    print("PASS: %d landmarks, %d tiles, %d stones resolved%s" % (
        len(spec), sum(len(v) for v in tiles.values()), sum(1 for v in stones.values() if v),
        "" if planet else " (no --save: planet checks skipped)"))
    return 0


def fingerprint(planet):
    """The dump must decode this save's planet: every biome hash resolves (renames only by exact alias), and the
    instrument can see the biomes a landmark must avoid. Mod-set drift is printed; it matters only through biomes."""
    for h, (o, n) in sorted(planet["aliases"].items()):
        print("alias  biome hash %d = old %s (recomputed exactly), read as %s" % (h, o, n))
    sm, dm = planet["save_mods"], planet["dump_mods"]
    if dm is None:
        print("FAIL fingerprint: no manifest.json beside the dump; cannot compare its mod set with the save")
        return 1
    s, d = {x.lower() for x in sm}, {x.lower() for x in dm}
    print("mods   save %d, dump %d; only in save: %s; only in dump: %s" % (
        len(s), len(d), ",".join(sorted(s - d)) or "-", ",".join(sorted(d - s)) or "-"))
    blind = sorted(EXCLUDED_BIOMES - planet["known_biomes"])
    if blind:
        print("FAIL fingerprint: the dump has no hash for %s, so the excluded-biome check cannot see it" % blind)
        return 1
    if planet["unresolved"]:
        n = sum(1 for b in planet["biome"] if b.startswith("?"))
        print("FAIL fingerprint: %d tiles carry biome hashes the dump cannot decode: %s" % (n, planet["unresolved"]))
        return 1
    print("ok     every biome hash in the save decodes (%d aliased)" % len(planet["aliases"]))
    return 0


def cmd_selftest(_a):
    # toy planet: a path 0-1-2-...-19 plus a detached pair 30-31
    nb = {i: [j for j in (i - 1, i + 1) if 0 <= j < 20] for i in range(20)}
    nb[30], nb[31] = [31], [30]
    stones = {"Granite": {"resource": False}, "RM_Plate": {"resource": True}, "Bogus": None, "RM_Basalt": None}
    good = [{"id": "RM_Geo_Alpha", "name": "Alpha", "kind": "k", "centre_tile": "3", "rings": "3", "label_tile": "4",
             "stones_now": "Granite", "stones_planned": "RM_Basalt", "owed_item": "LIVE", "note": ""}]
    t_good = {"RM_Geo_Alpha": list(range(0, 8))}
    live = lambda i: i == "LIVE"
    n_fail = 0

    def expect(label, fails, want):
        nonlocal n_fail
        ok = (not fails) if want is None else any(want in f for f in fails)
        print("%s %s %s" % ("ok  " if ok else "FAIL", label, fails if not ok else ""))
        n_fail += 0 if ok else 1

    expect("good spec passes", check(good, t_good, nb, stones, item_exists=live), None)
    bad = [dict(good[0], stones_now="Bogus")]
    expect("unknown stone fails", check(bad, t_good, nb, stones, item_exists=live), "does not resolve")
    bad = [dict(good[0], stones_now="RM_Plate")]
    expect("resource-only stones fail", check(bad, t_good, nb, stones, item_exists=live), "resource rock")
    bad = [dict(good[0], owed_item="")]
    expect("planned stone with no owner fails", check(bad, t_good, nb, stones, item_exists=live), "no owed_item")
    bad = [dict(good[0], owed_item="DEAD")]
    expect("dead owed item fails", check(bad, t_good, nb, stones, item_exists=live), "not a live item")
    expect("disconnected patch fails", check(good, {"RM_Geo_Alpha": list(range(0, 6)) + [30, 31]}, nb, stones,
                                             item_exists=live), "connected")
    expect("centre outside fails", check([dict(good[0], centre_tile="12")], t_good, nb, stones, item_exists=live),
           "centre 12")
    two = good + [dict(good[0], id="RM_Geo_Beta", name="Beta", centre_tile="7", label_tile="7")]
    expect("overlap fails", check(two, {"RM_Geo_Alpha": t_good["RM_Geo_Alpha"],
                                        "RM_Geo_Beta": list(range(7, 15))}, nb, stones, item_exists=live), "also belongs")
    expect("tiny patch fails", check(good, {"RM_Geo_Alpha": [3, 4]}, nb, stones, item_exists=live), "outside")
    expect("bad id fails", check([dict(good[0], id="Geo1")], {"Geo1": t_good["RM_Geo_Alpha"]}, nb, stones,
                                 item_exists=live), "RM_Geo_")
    planet = {"biome": ["RM_Stillsand"] * 20, "landmark_tiles": {4}}
    expect("label on an existing landmark fails", check(good, t_good, nb, stones, item_exists=live, planet=planet),
           "already carries")
    planet = {"biome": ["RM_Stillsand"] * 20, "landmark_tiles": set(), "settlement_tiles": {4}}
    expect("label on a settlement fails", check(good, t_good, nb, stones, item_exists=live, planet=planet),
           "settlement")
    planet = {"biome": ["RM_GreySea"] * 20, "landmark_tiles": set()}
    expect("sea tile fails", check(good, t_good, nb, stones, item_exists=live, planet=planet), "excluded biome")
    ok = short_hash("RM_Wasteland") == 18404 and short_hash("RM_NightsideIce") == 21915 and short_hash("RM_GreySea") == 65412
    print("%s short_hash reproduces three hashes measured in the dev save and dump" % ("ok  " if ok else "FAIL"))
    n_fail += 0 if ok else 1
    al, left = alias_unresolved([18404, 21915, 777], {"RM_Wastes": 1})
    ok = al == {18404: ("RM_Wasteland", "RM_Wastes")} and left == [21915, 777]
    print("%s alias needs exact hash AND a live new name; the rest stay undecoded" % ("ok  " if ok else "FAIL"))
    n_fail += 0 if ok else 1
    base = {"tiles": 2, "biome": ["RM_Wastes", "?777"], "aliases": {}, "save_mods": ["a"], "dump_mods": ["a"],
            "known_biomes": set(EXCLUDED_BIOMES)}
    for label, extra, want in (("undecoded hash fails the fingerprint", {"unresolved": [777]}, 1),
                               ("decoded planet passes the fingerprint", {"unresolved": []}, 0),
                               ("dump blind to a sea fails", {"unresolved": [], "known_biomes": {"RM_TheScald"}}, 1),
                               ("dump with no manifest fails", {"unresolved": [], "dump_mods": None}, 1)):
        ok = fingerprint(dict(base, **extra)) == want
        print("%s %s" % ("ok  " if ok else "FAIL", label))
        n_fail += 0 if ok else 1
    # owed-item liveness from a toy ledger: legacy file + shards, ts order, reopen after close, absent ledger refuses
    import tempfile
    with tempfile.TemporaryDirectory() as d:
        os.makedirs(os.path.join(d, "events"))
        rows = [("events.jsonl", SELF_ITEM, "file", "1"), ("events.jsonl", "OPEN", "file", "1"),
                ("events/A.jsonl", "SHUT", "file", "1"), ("events/B.jsonl", "SHUT", "close", "2"),
                ("events/A.jsonl", "BACK", "close", "2"), ("events/B.jsonl", "BACK", "claim", "3"),
                ("events/A.jsonl", "SHUT", "note", "4")]
        for f, i, ev, ts in rows:
            with open(os.path.join(d, f), "a", encoding="utf-8") as fh:
                fh.write(json.dumps({"event": ev, "id": i, "ts": ts}) + "\n")
        alive = ledger_item_exists(d)
        ok = alive("OPEN") and not alive("SHUT") and alive("BACK") and not alive("NEVER")
        print("%s ledger liveness: filed live, closed dead (a later note does not revive), reclaimed live, unfiled dead"
              % ("ok  " if ok else "FAIL"))
        n_fail += 0 if ok else 1
        try:
            ledger_item_exists(os.path.join(d, "nowhere"))
            ok = False
        except SystemExit as e:
            ok = "UNMEASURED" in str(e)
        print("%s an absent ledger refuses as UNMEASURED instead of calling every owed item dead" % ("ok  " if ok else "FAIL"))
        n_fail += 0 if ok else 1
    # sanity probes: the real resolvers can see what exists
    src = src_rocks()
    for n in ("RM_LanternstoneWall", "RM_CathedralDeckPlate"):
        ok = n in src
        print("%s src resolver sees %s" % ("ok  " if ok else "FAIL", n))
        n_fail += 0 if ok else 1
    ok = src.get("RM_CathedralDeckPlate", {}).get("resource") is True and src.get("RM_LanternstoneWall", {}).get("resource") is False
    print("%s src resolver reads isResourceRock" % ("ok  " if ok else "FAIL"))
    n_fail += 0 if ok else 1
    d = dump_rocks(["Granite", "Slate", "NoSuchStone_X"])
    if d is None:
        print("note dump db unavailable here: dump probe UNMEASURED")
    else:
        ok = "Granite" in d and "Slate" in d and "NoSuchStone_X" not in d
        print("%s dump resolver sees Granite/Slate and not a bogus name" % ("ok  " if ok else "FAIL"))
        n_fail += 0 if ok else 1
    nbr = read_neighbours()
    ok = len(nbr) == PLANET_TILES and sum(1 for v in nbr.values() if len(v) == 5) == 12
    print("%s neighbour table: %d tiles, 12 pentagons" % ("ok  " if ok else "FAIL", len(nbr)))
    n_fail += 0 if ok else 1
    print("SELFTEST %s" % ("PASS" if n_fail == 0 else "FAIL (%d)" % n_fail))
    return 1 if n_fail else 0


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    for name in ("author", "check"):
        p = sub.add_parser(name)
        p.add_argument("spec_pos", nargs="?", metavar="SPEC", help="spec csv (same as --spec)")
        p.add_argument("--spec", default=None)
        p.add_argument("--save", required=(name == "author"))
        p.add_argument("--dump", help="capture defs/ folder for the biome hash table (default: newest capture)")
        if name == "author":
            p.add_argument("--rewrite", action="store_true")
    sub.add_parser("selftest")
    a = ap.parse_args(argv)
    if a.cmd in ("author", "check"):
        if a.spec_pos and a.spec and os.path.abspath(a.spec_pos) != os.path.abspath(a.spec):
            ap.error("two different specs given")
        a.spec = a.spec_pos or a.spec or SPEC
    return {"author": cmd_author, "check": cmd_check, "selftest": cmd_selftest}[a.cmd](a) or 0


if __name__ == "__main__":
    sys.exit(main())
