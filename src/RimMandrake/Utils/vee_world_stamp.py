#!/usr/bin/env python3
"""vee_world_stamp.py - the VEE world layers' rename: map, offline proof, the one live stamp, the live verify.

Plan: design/RimMandrake/vee_port_plan_2026-10-22.md section 3 (item VEE_WORLD_RENAME_ONE_STAMP_AT_END).
Map:  design/RimMandrake/vee_port_map.json (same shape as retired_mutators_port_map.json, read by
      save_donor_rewrite.py --mutators-only --map).

    python3    vee_world_stamp.py build-map [--capture ID]     (re)write the map from R3 + src/ + a capture
    python3    vee_world_stamp.py prove-rename [--save P]      L1: rename an in-memory COPY of R3, prove it; writes nothing
    python3    vee_world_stamp.py plan [--save P]              offline: what the stamp would add/remove, per row
    python.exe vee_world_stamp.py stamp [--apply]              LIVE, bridge held, inside the big repaint (dry by default)
    python.exe vee_world_stamp.py verify-live [--save P]       LIVE read-only: exit 0 iff the stamp holds

R3 (the dev start, canon.yml planet.start_savegame) is the reference for every tile set. It is read, never written.

Old shortHashes: R3's own capture (2026-10-21T11-18-41Z) no longer exists. A TileMutatorDef's shortHash is
(ushort)(StableStringHash(defName) % 65535) unless a name sorting earlier took it (Verse.ShortHashGiver); so the
old hash of a VEE def is its raw hash provided no other known TileMutatorDef name (the union of every capture on
disk) shares or neighbours it. prove-rename checks that and refuses otherwise, and the decoded counts must equal the
plan's measured 14,413 / 805 (the sanity probe that the instrument can see).

Stamp order (plan s3): per row, add the RM_ port on its tiles while VEE is still loaded, read back, then remove the
VEE_ def; the tile is never bare. A port keeps its donor's categories (selftest_vee_port_map.py), so AddMutator's
same-category displacement is like-for-like. Solar rows are painted from geometry (plan s4,
Utils/remake/solar_insolation.py), not from the donor's tiles. A landmark is re-pointed by AddLandmark on its tile
(it overwrites the old one), the mutators that call rolls are removed again, and its stored name is restored.
Exactly one jawa/world_commit at the end.
"""
import argparse
import base64
import collections
import glob
import html
import json
import os
import re
import struct
import sys
import xml.etree.ElementTree as ET
import zlib

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "remake"))
import game_paths  # noqa: E402
import save_donor_rewrite as sdr  # noqa: E402

MAP = os.path.join(ROOT, "design", "RimMandrake", "vee_port_map.json")
R3 = "ASHKARR_DEV_START_2026-10-20_PARITY_QUIET_R3.rws"
PREFIX = "VEE_"
PKG = "vanillaexpanded.vexploratione"
SOLAR = {"VEE_MoreSolarPower": "RM_StrongInsolation", "VEE_LessSolarPower": "RM_Sunless"}
# Owner card 2026-10-22 on VEE_DEADLIFE_VENTS_ASK_ZOMBIES_AGAIN: "Drop them" (plan s4b option a).
DROPS = {"VEE_DeadlifeVents": "DROPPED by owner card 2026-10-22 (VEE_DEADLIFE_VENTS_ASK_ZOMBIES_AGAIN): no zombies; "
                              "its 10 tiles are stripped, not renamed"}
# Measured on R3 2026-10-22 (plan s1) and re-measured 2026-11-05: the sanity bar the decode must reproduce.
EXPECT = {"entries": 27913, "vee_entries": 14413, "vee_defs": 58, "landmarks": 3008, "vee_landmarks": 805,
          "vee_landmark_defs": 24, "VEE_Cenotes_literal": 339}


def save_path(p=None):
    return p or os.path.join(game_paths.SAVES, R3)


# ---- reading a save ----------------------------------------------------------------------------------------------
def _arr(raw, tag, fmt):
    m = re.findall(rb"<%s>(.*?)</%s>" % (tag, tag), raw, re.S)
    if len(m) != 1:
        raise SystemExit("expected exactly one <%s>, found %d" % (tag.decode(), len(m)))
    g = zlib.decompress(base64.b64decode(m[0].strip()), -15)
    w = struct.calcsize(fmt)
    return list(struct.unpack("<%d%s" % (len(g) // w, fmt), g))


def mutator_entries(raw):
    """[(tile, shortHash)] in save order (engine SurfaceLayer.SerializeMutators: parallel arrays)."""
    hs = _arr(raw, b"tileMutatorDefsDeflate", "H")
    ts = _arr(raw, b"tileMutatorTilesDeflate", "I")
    if len(hs) != len(ts):
        raise SystemExit("mutator arrays disagree: %d defs vs %d tiles" % (len(hs), len(ts)))
    return list(zip(ts, hs))


def landmarks(raw):
    """[(tile, def, name)] from the world's <landmarks> dictionary (keys 'tile,layer' parallel to values)."""
    outer = re.findall(rb"<landmarks>\s*<landmarks>(.*?)</landmarks>\s*</landmarks>", raw, re.S)
    if len(outer) != 1:
        raise SystemExit("expected one world <landmarks> dictionary, found %d" % len(outer))
    body = outer[0]
    keys = re.search(rb"<keys>(.*?)</keys>", body, re.S).group(1)
    vals = re.search(rb"<values>(.*)</values>", body, re.S).group(1)
    ks = [int(k.split(b",")[0]) for k in re.findall(rb"<li>([^<]*)</li>", keys)]
    vs = re.findall(rb"<li>\s*<def>([^<]+)</def>\s*<name>([^<]*)</name>\s*(?:<isComboLandmark>[^<]*</isComboLandmark>\s*)?</li>",
                    vals)
    if len(ks) != len(vs):
        raise SystemExit("landmark keys (%d) and values (%d) differ" % (len(ks), len(vs)))
    return [(t, d.decode(), html.unescape(n.decode("utf-8"))) for t, (d, n) in zip(ks, vs)]


# ---- hashes ------------------------------------------------------------------------------------------------------
def capture_names(def_type="TileMutatorDef"):
    names = set()
    for p in glob.glob(os.path.join(game_paths.CAPTURES, "*", "defs", def_type + ".json")):
        with open(p) as fh:
            names |= {r["defName"] for r in json.load(fh)["defs"]}
    return names


def raw_old_hashes(wanted, universe):
    """{name: hash} for `wanted`, by raw ShortHash; refuses a name some subset of the known names could bump.

    ShortHashGiver over a SUPERSET bumps a name at least as far as over any subset (every earlier name of the subset
    is in the superset too), so: if the assignment over universe+wanted leaves a name on its raw hash, every mod set
    drawn from those names does too. A name the superset bumps is refused (conservative)."""
    names = set(universe) | set(wanted)
    full = sdr.assign_short_hashes(names)
    out = {}
    for n in wanted:
        h = sdr.short_hash_raw(n)
        if h == 0 or full[n] != h:
            rivals = sorted(m for m in names if m != n and (h - 3) & 0xFFFF <= sdr.short_hash_raw(m) <= h)
            raise SystemExit("raw shortHash of %s (%d) is contested (bumped to %d; near: %s) - cannot infer its old "
                             "hash" % (n, h, full[n], rivals[:5]))
        out[n] = h
    return out


# ---- the map -----------------------------------------------------------------------------------------------------
def src_ports():
    out = {}
    for p in glob.glob(os.path.join(ROOT, "src", "**", "Defs", "**", "*.xml"), recursive=True):
        try:
            root = ET.parse(p).getroot()
        except ET.ParseError:
            continue
        for d in root:
            n = d.findtext("defName")
            if n and d.tag in ("TileMutatorDef", "LandmarkDef"):
                out[(d.tag, n)] = os.path.relpath(p, ROOT).replace(os.sep, "/")
    return out


def mod_of(path):
    parts = path.split("/")
    return parts[2] if len(parts) > 2 else path


def build_map(capture, save=None):
    raw = open(save_path(save), "rb").read()
    universe = capture_names()
    with open(os.path.join(game_paths.CAPTURES, capture, "defs", "TileMutatorDef.json")) as fh:
        cap = {r["defName"]: r for r in json.load(fh)["defs"]}
    vee = sorted(n for n in universe if n.startswith(PREFIX))
    hs = raw_old_hashes(vee, universe)
    inv = {h: n for n, h in hs.items()}
    cnt = collections.Counter(inv[h] for _, h in mutator_entries(raw) if h in inv)
    lcnt = collections.Counter(d for _, d, _ in landmarks(raw) if d.startswith(PREFIX))
    ports = src_ports()
    tm, lm = collections.OrderedDict(), collections.OrderedDict()
    for o, k in sorted(cnt.items(), key=lambda kv: (-kv[1], kv[0])):
        fl = cap.get(o, {}).get("fields") or {}
        cats = sorted(fl.get("categories") or [])
        prio = int(fl.get("priority") or 0)
        if o in DROPS:
            tm[o] = {"new": None, "drop": True, "status": "dropped", "mod": "-", "how": DROPS[o],
                     "categories": cats, "priority": prio, "r3_entries": k}
            continue
        n = SOLAR.get(o, "RM_" + o[len(PREFIX):])
        p = ports.get(("TileMutatorDef", n))
        if not p:
            raise SystemExit("no TileMutatorDef %s in src/ for %s" % (n, o))
        row = {"new": n, "status": "ported", "mod": mod_of(p), "categories": cats, "priority": prio,
               "r3_entries": k}
        if o in SOLAR:
            row["stamp"] = "geometry"
            row["how"] = "derived label painted from sun elevation at the stamp (plan s4, remake/solar_insolation.py)"
        tm[o] = row
    for o, k in sorted(lcnt.items(), key=lambda kv: (-kv[1], kv[0])):
        n = "RM_" + o[len(PREFIX):]
        p = ports.get(("LandmarkDef", n))
        if not p:
            raise SystemExit("no LandmarkDef %s in src/ for %s" % (n, o))
        lm[o] = {"new": n, "status": "ported", "mod": mod_of(p), "r3_entries": k}
    return collections.OrderedDict([
        ("_what", "VEE (vanillaexpanded.vexploratione) world-tile mutators and landmarks on the frozen planet -> our "
                  "own defs. Read by save_donor_rewrite.py --mutators-only --map (offline rename proof) and by "
                  "vee_world_stamp.py stamp (the one live stamp inside the big repaint). Rows: every VEE def R3 "
                  "carries; the 83 mutators and 35 landmarks on no tile are not ported (no worldgen)."),
        ("_authority", "Owner card 2026-10-22 on VEE_WORLD_MUTATORS_DECIDE_FOURTEEN_THOUSAND: \"Port all to our own "
                       "mod\". Plan: design/RimMandrake/vee_port_plan_2026-10-22.md s3."),
        ("_made_by", "python3 src/RimMandrake/Utils/vee_world_stamp.py build-map --capture %s (R3 counts; "
                     "categories from that capture)" % capture),
        ("_stamp", "stamp=geometry: the tile set is f(sun elevation), not the donor's tiles (plan s4); "
                   "drop=true: the entries are removed, not renamed."),
        ("TileMutatorDef", tm), ("LandmarkDef", lm)])


def load_map(path=MAP):
    with open(path) as fh:
        return json.load(fh)


# ---- L1: the rename proof on an in-memory copy -------------------------------------------------------------------
def splice(raw, edits):
    out, last = bytearray(), 0
    for s, e, b in sorted(edits):
        if s < last:
            raise SystemExit("overlapping splices")
        out += raw[last:s] + b
        last = e
    return bytes(out + raw[last:])


def prove_rename(save=None, map_path=MAP, new_capture=None):
    fails = []

    def check(ok, msg):
        print(("PASS " if ok else "FAIL ") + msg)
        if not ok:
            fails.append(msg)

    mapping = load_map(map_path)
    raw = open(save_path(save), "rb").read()
    universe = capture_names()
    vee = sorted(n for n in universe if n.startswith(PREFIX))
    check(len(vee) >= EXPECT["vee_defs"], "the captures on disk name %d VEE TileMutatorDefs (>= %d)"
          % (len(vee), EXPECT["vee_defs"]))
    old = raw_old_hashes(vee, universe)
    # sanity probe: the raw hash equals what a live capture recorded for the same def (instrument can see)
    newest = new_capture or sorted(os.listdir(game_paths.CAPTURES))[-1]
    live = {k: int(v) for k, v in sdr.capture_hashes(newest, "TileMutatorDef").items()}
    agree = [n for n in vee if n in live and live[n] == old[n]]
    check(len(agree) == len([n for n in vee if n in live]) and agree,
          "raw ShortHash reproduces capture %s for %d of %d VEE defs it holds" % (newest, len(agree),
                                                                                 len([n for n in vee if n in live])))
    inv = {h: n for n, h in old.items()}
    before = mutator_entries(raw)
    vcnt = collections.Counter(inv[h] for _, h in before if h in inv)
    check(len(before) == EXPECT["entries"], "R3 holds %d mutator entries (plan s1: %d)" % (len(before), EXPECT["entries"]))
    check(sum(vcnt.values()) == EXPECT["vee_entries"] and len(vcnt) == EXPECT["vee_defs"],
          "R3 holds %d VEE entries over %d defs (plan s1: %d over %d)"
          % (sum(vcnt.values()), len(vcnt), EXPECT["vee_entries"], EXPECT["vee_defs"]))
    lit = raw.count(b"<def>VEE_Cenotes</def>")
    lb = landmarks(raw)
    lcnt = collections.Counter(d for _, d, _ in lb if d.startswith(PREFIX))
    check(lit == lcnt["VEE_Cenotes"] == EXPECT["VEE_Cenotes_literal"],
          "second instrument: literal <def>VEE_Cenotes</def> %d = decoded %d = %d"
          % (lit, lcnt["VEE_Cenotes"], EXPECT["VEE_Cenotes_literal"]))
    check(len(lb) == EXPECT["landmarks"] and sum(lcnt.values()) == EXPECT["vee_landmarks"]
          and len(lcnt) == EXPECT["vee_landmark_defs"],
          "R3 holds %d landmarks, %d VEE over %d defs" % (len(lb), sum(lcnt.values()), len(lcnt)))
    check(set(vcnt) == set(mapping["TileMutatorDef"]), "the map has a row for exactly the VEE mutators R3 carries")
    check(set(lcnt) == set(mapping["LandmarkDef"]), "the map has a row for exactly the VEE landmarks R3 carries")

    # the rewrite, through save_donor_rewrite's --map path (old hashes: raw; new: simulated over `newest` + ports)
    hmap = sdr.mutator_hash_map(mapping, old_capture=sdr.RAW_OLD, new_capture=newest, universe=universe)
    edits, report = sdr.rewrite_world_mutators(raw, mapping, hmap)
    out = splice(raw, edits)
    after = mutator_entries(out)
    nh = {o: hmap[old[o]][2] for o in mapping["TileMutatorDef"]}
    drops = {o for o, r in mapping["TileMutatorDef"].items() if r.get("drop")}
    ndrop = sum(vcnt[o] for o in drops)
    check(len(after) == len(before) - ndrop, "entries kept: %d = %d - %d dropped" % (len(after), len(before), ndrop))
    port_h = {h for o, h in nh.items() if h is not None}
    check(not ({old[o] for o in vcnt} & {h for _, h in after}), "0 VEE hashes remain in the copy")
    # a port that already sat on the planet before (RM_QuicksandPits, from the 10-19 port) keeps its own entries.
    # Those are found by R3's OWN names (r3_named_entries), never by the predicted new hash: an R3 entry holding a
    # port's new hash that is not that port by name would be silently absorbed into it, so it is a failure.
    r3n = {}
    for t, n in r3_named_entries(raw):
        r3n.setdefault(n, set()).add(t)
    port_of_h = {h: mapping["TileMutatorDef"][o]["new"] for o, h in nh.items() if h is not None}
    impostor = [(t, h) for t, h in before if h in port_of_h and h not in inv and t not in r3n.get(port_of_h[h], set())]
    check(not impostor, "no R3 entry holds a port's new hash without being that port by name%s"
          % ((": %s" % impostor[:3]) if impostor else ""))
    prior = {mapping["TileMutatorDef"][o]["new"]: r3n.get(mapping["TileMutatorDef"][o]["new"], set())
             for o in mapping["TileMutatorDef"] if mapping["TileMutatorDef"][o].get("new")}
    print("NOTE ports already on R3 before the rename: %s" % ({n: len(v) for n, v in prior.items() if v} or "none"))
    keep_b = [(t, h) for t, h in before if h not in inv and h not in port_h]
    keep_a = [(t, h) for t, h in after if h not in port_h]
    check(keep_b == keep_a, "every other entry is identical and in the same order (%d)" % len(keep_b))
    check(len(set(after)) == len(after), "no tile carries the same mutator twice in the copy")
    bad = []
    for o, r in mapping["TileMutatorDef"].items():
        if r.get("drop"):
            continue
        tb = sorted([t for t, h in before if h == old[o]] + sorted(prior[r["new"]]))
        ta = sorted(t for t, h in after if h == nh[o])
        if tb != ta:
            bad.append(o)
    check(not bad, "each port carries exactly its donor's tile set (+ its own prior entries) (%d rows)%s"
          % (len(mapping["TileMutatorDef"]) - len(drops), (": " + ", ".join(bad)) if bad else ""))
    check(len(port_h) == len(mapping["TileMutatorDef"]) - len(drops),
          "every port has its own new shortHash (%d distinct)" % len(port_h))
    # landmarks
    la = landmarks(out)
    lmap = {o: r["new"] for o, r in mapping["LandmarkDef"].items()}
    want = [(t, lmap.get(d, d), n) for t, d, n in lb]
    check(la == want, "landmarks: %d re-pointed, tile and stored name kept, 0 VEE left (%d)"
          % (sum(lcnt.values()), sum(1 for _, d, _ in la if d.startswith(PREFIX))))
    # every byte outside the allowed regions identical. Independent of splice(): the regions are re-found by regex in
    # BOTH files and blanked, then the remainders compared; and every splice must lie inside an allowed region.
    def regions(buf, lm_names):
        rs = [(m.start(1), m.end(1)) for t in (b"tileMutatorDefsDeflate", b"tileMutatorTilesDeflate")
              for m in re.finditer(rb"<%s>(.*?)</%s>" % (t, t), buf, re.S)]
        w = re.search(rb"<landmarks>\s*<landmarks>.*?</landmarks>\s*</landmarks>", buf, re.S)
        for d in re.finditer(rb"<def>([^<]+)</def>", w.group(0)):
            if d.group(1).decode() in lm_names:
                rs.append((w.start() + d.start(1), w.start() + d.end(1)))
        return sorted(rs)

    def blank(buf, rs):
        o, last = bytearray(), 0
        for s0, e0 in rs:
            o += buf[last:s0] + b"\0"
            last = e0
        return bytes(o + buf[last:])
    both = set(lmap) | set(lmap.values())  # a port landmark may already sit on the planet (blank it in both files)
    r_in, r_out = regions(raw, both), regions(out, both)
    check(len(r_in) == len(r_out) >= 2 + sum(lcnt.values()) and blank(raw, r_in) == blank(out, r_out),
          "every byte outside the 2 mutator arrays and the %d landmark <def>s of mapped names is identical "
          "(re-found in both files)" % (len(r_in) - 2))
    stray = [(s0, e0) for s0, e0, _ in edits if not any(a0 <= s0 and e0 <= b0 for a0, b0 in r_in)]
    check(not stray, "all %d splices lie inside those regions%s" % (len(edits), (": %s" % stray[:3]) if stray else ""))
    print("RESULT %s: %d checks failed" % ("FAIL" if fails else "PASS", len(fails)))
    return 1 if fails else 0


# ---- the stamp: rows -> (add def, tiles, remove def, tiles) ------------------------------------------------------
def stamp_rows(mapping, vee_tiles, geometry=None):
    """[(old, new or None, add_tiles, remove_tiles)] from live (or saved) VEE tiles per def."""
    rows = []
    for o, r in mapping["TileMutatorDef"].items():
        rem = sorted(vee_tiles.get(o, []))
        if r.get("drop") or not r.get("new"):
            rows.append((o, None, [], rem))
        elif r.get("stamp") == "geometry":
            if geometry is None:
                import solar_insolation
                geometry = solar_insolation.tiles_by_label()
            rows.append((o, r["new"], geometry[r["new"]], rem))
        else:
            rows.append((o, r["new"], rem, rem))
    return rows


def saved_vee_tiles(raw, mapping):
    universe = capture_names()
    old = raw_old_hashes(sorted(mapping["TileMutatorDef"]), universe)
    inv = {h: n for n, h in old.items()}
    out = collections.defaultdict(list)
    for t, h in mutator_entries(raw):
        if h in inv:
            out[inv[h]].append(t)
    return out


def cmd_plan(a):
    mapping = load_map()
    raw = open(save_path(a.save), "rb").read()
    rows = stamp_rows(mapping, saved_vee_tiles(raw, mapping))
    for o, n, add, rem in rows:
        print("%-28s -> %-26s add %5d  remove %5d" % (o, n or "(drop)", len(add), len(rem)))
    lm = [(t, d) for t, d, _ in landmarks(raw) if d in mapping["LandmarkDef"]]
    print("landmarks re-pointed: %d over %d defs" % (len(lm), len({d for _, d in lm})))
    return 0


def _bridge():
    from rimbridge_client import RimBridge, resolve_endpoint
    host, port, token = resolve_endpoint()
    if not token:
        raise SystemExit("No bridge token in Player.log - is the game running?")
    return RimBridge(host, port, token)


def live_state(rb):
    from w9_run import read_live_mutators, EXPECT_TILES
    wi = rb.call("jawa/world_info_get", {}) or {}
    mut = read_live_mutators(rb, wi.get("tilesCount") or EXPECT_TILES)
    lg = rb.call("jawa/world_landmarks_get", {"limit": 5000})
    if not lg.get("success") or (lg.get("count") or 0) > len(lg.get("landmarks") or []):
        raise SystemExit("world_landmarks_get truncated or failed: %s" % str(lg)[:160])
    lms = [(int(x["tile"]), x.get("def"), x.get("name")) for x in lg.get("landmarks") or []]
    return mut, lms


def _chunks(seq, k=1000):
    for i in range(0, len(seq), k):
        yield seq[i:i + k]


def _by_tile(mut):
    out = collections.defaultdict(set)
    for t, d in mut:
        out[t].add(d)
    return out


def cmd_stamp(a):
    """Dry by default. Any surprise refuses BEFORE a VEE def is removed; nothing is committed on a refusal, and the
    sitting reloads the save to undo an in-memory add (a world edit lives in memory until the save)."""
    mapping = load_map()
    vee_names = set(mapping["TileMutatorDef"])
    with _bridge() as rb:
        mut, lms = live_state(rb)
        by = collections.defaultdict(list)
        for t, d in mut:
            by[d].append(t)
        rows = stamp_rows(mapping, {o: by.get(o, []) for o in mapping["TileMutatorDef"]})
        for o, n, add, rem in rows:
            print("%-28s -> %-26s add %5d  remove %5d" % (o, n or "(drop)", len(add), len(rem)))
        lmv = [(t, d, nm) for t, d, nm in lms if d in mapping["LandmarkDef"]]
        print("landmarks to re-point: %d" % len(lmv))
        if not a.apply:
            print("DRY RUN - pass --apply to write")
            return 0

        def call(action, name, tiles, may_displace=frozenset()):
            for ch in _chunks(tiles):
                rr = rb.call("jawa/world_mutators_set", {"action": action, "mutators": name,
                                                          "tiles": ",".join(map(str, ch)), "readBack": 2})
                if not rr.get("success"):
                    raise SystemExit("world_mutators_set %s %s failed: %s" % (action, name, str(rr.get("message"))[:160]))
                lost = {k: v for k, v in (rr.get("displacedByDef") or {}).items() if k not in may_displace}
                if lost:
                    raise SystemExit("REFUSED: adding %s displaced %s (not a VEE def due for removal). Nothing "
                                     "committed: reload the save to undo." % (name, lost))

        before = _by_tile(mut)
        # 1. add every port first (VEE still loaded); a port may displace only VEE defs, which go anyway
        for o, n, add, _ in rows:
            if n and add:
                call("add", n, add, may_displace=vee_names)
        mut2, _ = live_state(rb)
        now = _by_tile(mut2)
        missing = {n: len([t for t in add if n not in now[t]]) for o, n, add, _ in rows if n}
        missing = {k: v for k, v in missing.items() if v}
        lost = [(t, d) for t, ds in before.items() for d in ds - now[t] if d not in vee_names]
        if missing or lost:
            raise SystemExit("REFUSED before any removal: ports missing %s; non-VEE entries lost %d (e.g. %s). "
                             "Reload the save to undo." % (missing, len(lost), lost[:3]))
        # 2. remove the VEE defs
        for o, _, _, rem in rows:
            if rem:
                call("remove", o, rem)
        # 3. landmarks: AddLandmark overwrites the tile's landmark and rolls mutatorChances (which can displace a
        #    same-category mutator): strip what the roll added, put back what it pushed off, restore the name
        mut3, _ = live_state(rb)
        settled = _by_tile(mut3)
        for t, d, nm in lmv:
            new = mapping["LandmarkDef"][d]["new"]
            rr = rb.call("jawa/world_landmarks_set", {"action": "add", "def": new, "tiles": str(t),
                                                       "forced": True, "checkValid": False})
            if not rr.get("success"):
                raise SystemExit("world_landmarks_set add %s on %d failed: %s" % (new, t, str(rr)[:160]))
            g = rb.call("jawa/world_mutators_get", {"tiles": str(t), "limit": 2})
            cur = {(m or {}).get("def") for x in g.get("tiles") or [] for m in x.get("mutators") or []} - {None}
            for extra in sorted(cur - settled[t]):
                call("remove", extra, [t])
            for back in sorted(settled[t] - cur):
                call("add", back, [t])
            g = rb.call("jawa/world_mutators_get", {"tiles": str(t), "limit": 2})
            cur = {(m or {}).get("def") for x in g.get("tiles") or [] for m in x.get("mutators") or []} - {None}
            if cur != settled[t]:
                raise SystemExit("REFUSED: landmark tile %d mutators %s, expected %s" % (t, sorted(cur), sorted(settled[t])))
            rn = rb.call("jawa/world_landmark_rename", {"tile": t, "name": nm})
            if not rn.get("success"):
                raise SystemExit("world_landmark_rename %d failed: %s" % (t, str(rn)[:160]))
        cm = rb.call("jawa/world_commit", {})
        if not (cm or {}).get("success"):
            raise SystemExit("world_commit failed: %s - run verify-live before saving" % str(cm)[:160])
    print("stamped; now run: vee_world_stamp.py verify-live")
    return 0


def verify(mapping, raw, mut, lms, geometry=None):
    """-> list of failure strings: the live world against R3 renamed. Checks 0 VEE left, every port exactly on its
    expected tiles (plus its own prior R3 entries), every non-VEE R3 entry on a tile the stamp touched still live,
    and every re-pointed landmark with its port and stored name."""
    fails = []
    have = collections.defaultdict(set)
    for t, d in mut:
        have[d].add(t)
    live_t = _by_tile(mut)
    left = {d: len(ts) for d, ts in have.items() if d.startswith(PREFIX)}
    if left:
        fails.append("VEE_ mutators still live: %s" % left)
    saved = r3_named_entries(raw)
    prior = collections.defaultdict(set)
    for t, d in saved:
        prior[d].add(t)
    touched = set()
    for o, n, add, rem in stamp_rows(mapping, saved_vee_tiles(raw, mapping), geometry):
        touched |= set(add) | set(rem)
        if not n:
            continue
        want = set(add) | prior.get(n, set())
        if want - have[n]:
            fails.append("%s missing on %d of its %d tiles" % (n, len(want - have[n]), len(want)))
        if have[n] - want:
            fails.append("%s on %d tile(s) outside its expected set" % (n, len(have[n] - want)))
    lm_r3 = [(t, d, nm) for t, d, nm in landmarks(raw) if d in mapping["LandmarkDef"]]
    touched |= {t for t, _, _ in lm_r3}
    lost = [(t, d) for t, d in saved if t in touched and not d.startswith(PREFIX) and d not in live_t[t]]
    if lost:
        fails.append("%d non-VEE R3 entries on stamped tiles are gone, e.g. %s" % (len(lost), lost[:3]))
    lv = [x for x in lms if (x[1] or "").startswith(PREFIX)]
    if lv:
        fails.append("VEE_ landmarks still live: %d" % len(lv))
    live_l = {t: (d, nm) for t, d, nm in lms}
    wrong = [t for t, d, nm in lm_r3 if live_l.get(t) != (mapping["LandmarkDef"][d]["new"], nm)]
    if wrong:
        fails.append("%d re-pointed landmarks lack their port or stored name, e.g. tile %d" % (len(wrong), wrong[0]))
    return fails


def r3_named_entries(raw):
    """[(tile, defName)] for every R3 entry whose hash resolves uncontested over the captures' names (a contested
    vanilla hash, e.g. Lakeshore/Crevasse, is left out rather than guessed)."""
    universe = capture_names()
    full = sdr.assign_short_hashes(universe)
    rh = {n: sdr.short_hash_raw(n) for n in universe}
    contested = {rh[n] for n in universe if not rh[n] or full[n] != rh[n]}
    inv = {rh[n]: n for n in universe if full[n] == rh[n] and rh[n] not in contested}
    return [(t, inv[h]) for t, h in mutator_entries(raw) if h in inv]


def cmd_verify_live(a):
    mapping = load_map()
    raw = open(save_path(a.save), "rb").read()
    with _bridge() as rb:
        mut, lms = live_state(rb)
    fails = verify(mapping, raw, mut, lms)
    for f in fails:
        print("FAIL " + f)
    print("RESULT %s (%d live mutator entries, %d landmarks read)" % ("FAIL" if fails else "PASS", len(mut), len(lms)))
    return 1 if fails else 0


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    b = sub.add_parser("build-map")
    b.add_argument("--capture", default=None)
    b.add_argument("--save")
    b.add_argument("--out", default=MAP)
    for name in ("prove-rename", "plan", "verify-live"):
        s = sub.add_parser(name)
        s.add_argument("--save")
    s = sub.add_parser("stamp")
    s.add_argument("--apply", action="store_true")
    a = ap.parse_args(argv)
    if a.cmd == "build-map":
        cap = a.capture or sorted(os.listdir(game_paths.CAPTURES))[-1]
        m = build_map(cap, a.save)
        with open(a.out, "w") as fh:
            json.dump(m, fh, indent=1)
            fh.write("\n")
        print("wrote %s: %d mutator rows, %d landmark rows" % (a.out, len(m["TileMutatorDef"]), len(m["LandmarkDef"])))
        return 0
    if a.cmd == "prove-rename":
        return prove_rename(a.save)
    if a.cmd == "plan":
        return cmd_plan(a)
    if a.cmd == "stamp":
        return cmd_stamp(a)
    return cmd_verify_live(a)


if __name__ == "__main__":
    sys.exit(main())
