#!/usr/bin/env python3
"""The big repaint, offline half: measure what a save's planet carries, and build the
biome-only stamp CSV that `jawa/world_tile_import` paints onto the live dev world.

Plan: design/Jawa/worldbuilding/big_repaint_plan_2026-10-21.md (owner 2026-10-21: "The world
we're building now is the big repaint! Right now!").

    python3 src/RimMandrake/Utils/remake/repaint_biomes.py census <save.rws> [...]
    python3 src/RimMandrake/Utils/remake/repaint_biomes.py build --save <save.rws> \
        --rename RM_NightsideIce=RM_SleepingIce --rename RM_Wasteland=RM_Wastes \
        [--edits tile_biome_edits.csv] [--decode-by-name] --out <tiles_biome_only.csv>
    python3 src/RimMandrake/Utils/remake/repaint_biomes.py check <tiles_biome_only.csv>     the stamp's bar, exit 0/1
    python3 src/RimMandrake/Utils/remake/repaint_biomes.py verify-save <stamped.rws> --against <csv>   exit 0/1
    python3 src/RimMandrake/Utils/remake/repaint_biomes.py selftest

--decode-by-name (2026-11-02): the dump that matched R3's 325-mod set is gone, so the build decodes each tile hash as
the BASE shortHash of exactly one known BiomeDef name (dump + src/ + each --rename OLD), refuses a bumped, unknown or
unsettled hash, and must reproduce R3's matching-dump histogram of 2026-10-21 exactly before it writes. `check`'s
moved-count bar is pinned to that same R3 histogram. The live half is repaint_stamp.py.

Why a BIOME-ONLY csv and not the w9_run bundle: `jawa/world_tile_import` writes EVERY column it
finds (biome, elev_m, temp_c, rain_mm, hilliness, swampiness, pollution). The 2026-10-20 bundle
(`world/paint_inputs_2026-10-20/`) predates mountains passes 1 and 2 (2,744 hilliness/elevation
edits applied live into `_PARITY`), so re-stamping that bundle onto the dev world would silently
revert them. The source of truth for "what the dev world is" is the dev save itself, decoded
here; only the biome column changes.

Why the decode is trustworthy only on a matching dump: tileBiome is stored as 2-byte BiomeDef
shortHashes; a table from a different mod set can resolve a hash to the WRONG biome rather than
failing. `census` prints the save's own mod-set fingerprint beside the dump's; `build` refuses a
mismatch unless --allow-fingerprint-mismatch, and always refuses a save with unresolved hashes.

A rename target need not exist in the dump yet (the renamed def is not loaded until the next
deploy + cold load); `build` checks it against `<defName>` lines of BiomeDef XML under src/
instead, and the live import reports any name it cannot resolve as `unknownBiomes` (stop).
Read-only against every save: nothing here writes a .rws (owner 2026-08-18/19: no save writes).
"""
import argparse, collections, csv, hashlib, json, math, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
UTILS = os.path.dirname(HERE)
REPO = os.path.abspath(os.path.join(UTILS, "..", "..", ".."))
sys.path.insert(0, UTILS)

EXPECT_TILES = 21872
# R3's biome histogram, read 2026-10-21 against a dump whose mod set MATCHED the save (325, f1c87543b447bab6):
# design/Jawa/worldbuilding/big_repaint_plan_2026-10-21.md section 1a. That dump is gone (2026-11-02), so a
# --decode-by-name build must reproduce this exactly before it may write a stamp.
R3_HISTOGRAM_2026_10_21 = {
    "RM_Stillsand": 3969, "RUT_Umbra": 2531, "RM_LongShade": 2390, "RM_TheRot": 2204, "RM_Wasteland": 1853,
    "RM_NightsideIce": 1506, "RM_Abyss": 1135, "RM_BlueDesert": 1029, "RM_FloodedCanyon": 970, "RM_LeaningScrub": 628,
    "RM_TwilightSea": 607, "RM_Cauldron": 546, "RM_GreySea": 472, "RM_TheScald": 312, "RM_RustCathedral": 236,
    "RM_Greentide": 235, "RM_WeepingStones": 223, "RM_Pyrelands": 222, "RM_Contagion": 179, "RM_Webwork": 161,
    "RM_GelatinousSlime": 96, "RM_Miasma": 93, "RM_Warscar": 90, "RM_TheChill": 57, "RM_TheForge": 44,
    "RM_FeverWood": 43, "RM_TheSump": 41}
OURS = re.compile(r"^mandrake\.")
VANILLA = re.compile(r"^ludeon\.")


def klass(pkg):
    if pkg and OURS.match(pkg):
        return "ours"
    if pkg and VANILLA.match(pkg):
        return "vanilla/DLC"
    return "DONOR" if pkg else "UNKNOWN"


def _dump_dir():
    import game_paths
    return game_paths.DEF_DUMP


def _defs(dump, def_type):
    p = os.path.join(dump, "defs", def_type + ".json")
    if not os.path.exists(p):
        return {}, {}
    rows = json.load(open(p, encoding="utf-8"))["defs"]
    return {d["defName"]: d for d in rows}, {d["shortHash"]: d["defName"] for d in rows}


def _sha16(ids):
    return hashlib.sha256("\n".join(sorted(i.lower() for i in ids)).encode()).hexdigest()[:16]


def dump_fingerprint(dump):
    man = json.load(open(os.path.join(dump, "manifest.json"), encoding="utf-8"))
    ids = [m["packageId"] for m in man["mods"]]
    return len(ids), _sha16(ids), man.get("capturedUtc")


def save_fingerprint(save):
    with open(save, "rb") as fh:
        head = fh.read(400000).decode("utf-8", "replace")
    m = re.search(r"<modIds>(.*?)</modIds>", head, re.S)
    ids = re.findall(r"<li>(.*?)</li>", m.group(1)) if m else []
    return len(ids), _sha16(ids)


def census(save, dump):
    import worldmap
    biomes, _ = _defs(dump, "BiomeDef")
    muts, mut_h = _defs(dump, "TileMutatorDef")
    lms, _ = _defs(dump, "LandmarkDef")
    g = worldmap.WorldGrid(save, os.path.join(dump, "defs"))
    n_s, sha_s = save_fingerprint(save)
    n_d, sha_d, cap = dump_fingerprint(dump)
    rows = []
    for name, n in sorted(g.census().items(), key=lambda kv: -kv[1]):
        pkg = biomes.get(name, {}).get("packageId")
        rows.append({"biome": str(name), "tiles": n, "package": pkg, "class": klass(pkg)})
    mc = collections.Counter()
    for _t, h in g.mutator_entries():
        name = mut_h.get(h, "?%d" % h)
        mc[klass(muts.get(name, {}).get("packageId"))] += 1
    wo = worldmap.WorldObjects(save)
    lc = collections.Counter(klass(lms.get(l["def"], {}).get("packageId")) for l in wo.landmarks())
    return {
        "save": save, "tiles": len(g.arrays["tileBiome"]),
        "save_mods": n_s, "save_sha16": sha_s, "dump": dump, "dump_captured": cap,
        "dump_mods": n_d, "dump_sha16": sha_d, "fingerprint_match": sha_s == sha_d,
        "unresolved_hashes": g.unresolved(), "biomes": rows,
        "mutators_by_class": dict(mc), "landmarks_by_class": dict(lc),
        "settlements": len(wo.settlements()),
    }


def short_hash(name):
    """RimWorld ShortHashGiver's base hash, (ushort)(StableStringHash(defName) % 65535) with C#'s truncating %.
    A def whose base hash was taken gets a bumped one that depends on load order: by_name_table never matches it."""
    h = 23
    for ch in name:
        h = (h * 31 + ord(ch)) & 0xFFFFFFFF
    if h >= 0x80000000:
        h -= 0x100000000
    return int(math.fmod(h, 65535)) & 0xFFFF


def by_name_table(names):
    """{base shortHash: defName} over every candidate BiomeDef name, and {hash: names} for hashes names share."""
    table, clash = {}, {}
    for n in sorted(set(names)):
        h = short_hash(n)
        if h in table and table[h] != n:
            clash.setdefault(h, {table[h]}).add(n)
        table.setdefault(h, n)
    return table, clash


def decode_by_name(arr, names, assigned=None):
    """Decode a tileBiome hash array from defNames alone, with no mod-set hash table: each tile hash must be the BASE
    hash of exactly one candidate name. -> (base {tile: name}, problems [str]). A bumped (order-dependent) hash, an
    unknown hash and an ambiguous hash are each a problem, never a guess. One exception: two names sharing a base hash
    (RM_RustCathedral and the frozen twin RUT_Cauldron do) is settled by `assigned`, a dump's {hash: name}, only when the
    dump gives that hash to one of the clashing names; the caller must cross-check the result."""
    table, clash = by_name_table(names)
    problems = []
    for h in sorted(set(arr)):
        if h in clash:
            pick = (assigned or {}).get(h)
            if pick in clash[h]:
                table[h] = pick
            else:
                problems.append("hash %d is the base hash of %s and no dump settles it" % (h, sorted(clash[h])))
        elif h not in table:
            problems.append("hash %d is no candidate name's base hash (unknown or collision-bumped)" % h)
    return ({i: table.get(h, "?%d" % h) for i, h in enumerate(arr)}, problems)


def src_biome_defnames(root=os.path.join(REPO, "src")):
    """defNames declared in any BiomeDef XML under src/ (the renamed name may not be loaded yet)."""
    names = set()
    for dp, _dn, fns in os.walk(root):
        if "BiomeDef" not in dp and "Biome" not in dp:
            continue
        for fn in fns:
            if fn.endswith(".xml"):
                txt = open(os.path.join(dp, fn), encoding="utf-8", errors="replace").read()
                for blk in re.findall(r"<BiomeDef\b[^>]*>(.*?)</BiomeDef>", txt, re.S):
                    m = re.search(r"<defName>\s*([A-Za-z0-9_]+)\s*</defName>", blk)
                    if m:
                        names.add(m.group(1))
    return names


def apply_paint(base, renames, edits):
    """base: {tile: biome}. renames: {old: new}. edits: {tile: biome} (applied last).
    Returns (out, counts) - counts[old->new] = tiles moved by each rename."""
    out, moved = {}, collections.Counter()
    for t, b in base.items():
        nb = renames.get(b, b)
        if nb != b:
            moved["%s->%s" % (b, nb)] += 1
        out[t] = nb
    for t, b in edits.items():
        if t not in out:
            raise ValueError("edit names tile %d, not on the grid" % t)
        if out[t] != b:
            moved["edit->%s" % b] += 1
        out[t] = b
    return out, moved


def cmd_census(a):
    dump = a.dump or _dump_dir()
    res = [census(s, dump) for s in a.saves]
    for r in res:
        own = sum(x["tiles"] for x in r["biomes"] if x["class"] == "ours")
        print("%s tiles=%d ours=%d not-ours=%d unresolved=%d fingerprint %s (save %d/%s, dump %d/%s) "
              "mutators %s landmarks %s" % (
                  os.path.basename(r["save"]), r["tiles"], own, r["tiles"] - own, len(r["unresolved_hashes"]),
                  "MATCH" if r["fingerprint_match"] else "MISMATCH", r["save_mods"], r["save_sha16"],
                  r["dump_mods"], r["dump_sha16"], r["mutators_by_class"], r["landmarks_by_class"]))
    if a.json:
        json.dump(res, open(a.json, "w"), indent=1)
        print("wrote", a.json)
    return 0


def _parse_renames(items):
    renames = {}
    for r in items or []:
        old, _, new = r.partition("=")
        if not old or not new:
            raise ValueError("--rename wants OLD=NEW, got %r" % r)
        renames[old] = new
    return renames


def cmd_build(a):
    import worldmap
    dump = a.dump or _dump_dir()
    n_s, sha_s = save_fingerprint(a.save)
    n_d, sha_d, cap = dump_fingerprint(dump)
    try:
        renames = _parse_renames(a.rename)
    except ValueError as e:
        print("REFUSED: %s" % e)
        return 2
    if sha_s != sha_d and not (a.allow_fingerprint_mismatch or a.decode_by_name):
        print("REFUSED: save mod set %d/%s != dump %d/%s (captured %s). A hash table from another mod set "
              "can decode a tile to the WRONG biome. Re-capture the dump on the save's list, pass --decode-by-name "
              "(no hash table), or pass --allow-fingerprint-mismatch and say why." % (n_s, sha_s, n_d, sha_d, cap))
        return 2
    g = worldmap.WorldGrid(a.save, os.path.join(dump, "defs"))
    arr = g.arrays["tileBiome"]
    if len(arr) != EXPECT_TILES:
        print("REFUSED: %d tiles, expected %d" % (len(arr), EXPECT_TILES))
        return 2
    decode = "dump hash table (fingerprint %s)" % ("MATCH" if sha_s == sha_d else "MISMATCH, allowed")
    if a.decode_by_name:
        drows, dhash = _defs(dump, "BiomeDef")
        base, problems = decode_by_name(arr, list(drows) + sorted(src_biome_defnames()) + list(renames), dhash)
        if problems:
            print("REFUSED: by-name decode: %s" % "; ".join(problems[:10]))
            return 2
        hist0 = dict(collections.Counter(base.values()))
        if a.reference == "r3-2026-10-21" and hist0 != R3_HISTOGRAM_2026_10_21:
            diff = {k: (hist0.get(k, 0), R3_HISTOGRAM_2026_10_21.get(k, 0))
                    for k in set(hist0) | set(R3_HISTOGRAM_2026_10_21) if hist0.get(k, 0) != R3_HISTOGRAM_2026_10_21.get(k, 0)}
            print("REFUSED: by-name decode differs from R3's matching-dump histogram of 2026-10-21 (got, recorded): %s"
                  % diff)
            return 2
        decode = "by name (base shortHash of each defName), equal to %s" % a.reference
    else:
        if g.unresolved():
            print("REFUSED: %d tileBiome hash(es) unresolved in this dump: %s" % (len(g.unresolved()), g.unresolved()[:10]))
            return 2
        base = {i: g.biome_by_hash[h] for i, h in enumerate(arr)}
    edits = {}
    if a.edits:
        with open(a.edits, encoding="utf-8") as fh:
            for row in csv.DictReader(fh):
                edits[int(row["tile"])] = row["biome"].strip()
    biomes, _ = _defs(dump, "BiomeDef")
    declared = src_biome_defnames()
    wanted = set(renames.values()) | set(edits.values())
    missing = sorted(n for n in wanted if n not in biomes and n not in declared)
    if missing:
        print("REFUSED: target biome(s) neither in the dump nor declared under src/: %s" % missing)
        return 2
    absent_old = sorted(o for o in renames if o not in set(base.values()))
    out, moved = apply_paint(base, renames, edits)
    hist = collections.Counter(out.values())
    not_ours = sorted(b for b in hist if b in biomes and klass(biomes[b]["packageId"]) != "ours")
    if not_ours and not a.allow_not_ours:
        print("REFUSED: output paints biomes that are not ours: %s" % not_ours)
        return 2
    unloadable = sorted(b for b in hist if b in renames or (b not in biomes and b not in declared))
    if unloadable:
        print("REFUSED: output paints names no deployed or src/ BiomeDef carries (an old name left unrenamed?): %s"
              % unloadable)
        return 2
    os.makedirs(os.path.dirname(os.path.abspath(a.out)), exist_ok=True)
    with open(a.out, "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["tile", "biome"])
        for t in range(EXPECT_TILES):
            w.writerow([t, out[t]])
    prov = {"decode": decode, "save": a.save, "save_mods": n_s, "save_sha16": sha_s, "dump_captured": cap, "dump_sha16": sha_d,
            "renames": renames, "edits_file": a.edits, "edits": len(edits), "moved": dict(moved),
            "renames_with_no_tiles": absent_old, "histogram": dict(hist.most_common()),
            "import": "jawa/world_tile_import {path:<this csv, Windows path>, apply:false, expectTiles:%d} "
                      "then apply:true, then jawa/world_tile_validate on the same path, then jawa/world_commit"
                      % EXPECT_TILES}
    json.dump(prov, open(a.out + ".provenance.json", "w"), indent=1)
    print("wrote %s (%d tiles, %d biomes); moved %s; renames with no tiles %s" % (
        a.out, EXPECT_TILES, len(hist), dict(moved), absent_old))
    return 0


def check_stamp(rows, prov, declared):
    """rows: [(tile, biome)] read from the stamp CSV. -> [problem]. The bar plan section 3 step 3 sets."""
    bad = []
    if [t for t, _b in rows] != list(range(EXPECT_TILES)):
        bad.append("tiles are not exactly 0..%d in order (%d rows)" % (EXPECT_TILES - 1, len(rows)))
    hist = dict(collections.Counter(b for _t, b in rows))
    if hist != prov.get("histogram"):
        bad.append("histogram differs from the provenance file")
    old = sorted(set(hist) & set(prov.get("renames") or {}))
    if old:
        bad.append("old names still painted: %s" % old)
    undeclared = sorted(b for b in hist if b not in declared)
    if undeclared:
        bad.append("biomes no src/ BiomeDef declares: %s" % undeclared)
    for o, n in (prov.get("renames") or {}).items():
        want = R3_HISTOGRAM_2026_10_21.get(o, 0)
        got = (prov.get("moved") or {}).get("%s->%s" % (o, n), 0)
        if got != want:
            bad.append("rename %s->%s moved %d tiles, R3 held %d" % (o, n, got, want))
    return bad


def _read_stamp(path):
    with open(path, encoding="utf-8") as fh:
        return [(int(r["tile"]), r["biome"].strip()) for r in csv.DictReader(fh)]


def cmd_check(a):
    if not (os.path.exists(a.csv) and os.path.exists(a.csv + ".provenance.json")):
        print("FAIL: %s or its .provenance.json is missing" % a.csv)
        return 1
    prov = json.load(open(a.csv + ".provenance.json", encoding="utf-8"))
    bad = check_stamp(_read_stamp(a.csv), prov, src_biome_defnames())
    for b in bad:
        print("FAIL:", b)
    if not bad:
        print("PASS %s: %d tiles, %d biomes, moved %s" % (a.csv, EXPECT_TILES, len(prov["histogram"]), prov["moved"]))
    return 1 if bad else 0


def cmd_verify_save(a):
    """Read-only: the stamped save's biome layer equals the stamp CSV, tile by tile (plan section 3 step 9)."""
    import worldmap
    stamp = _read_stamp(a.against)
    if not os.path.exists(a.save):
        print("FAIL: no save at %s" % a.save)
        return 1
    g = worldmap.WorldGrid(a.save, os.path.join(a.dump or _dump_dir(), "defs"))
    arr = g.arrays["tileBiome"]
    drows, dhash = _defs(a.dump or _dump_dir(), "BiomeDef")
    base, problems = decode_by_name(arr, list(drows) + sorted(src_biome_defnames()), dhash)
    if len(arr) != EXPECT_TILES:
        problems.append("%d tiles, expected %d" % (len(arr), EXPECT_TILES))
    want = dict(stamp)
    off = [t for t in range(min(len(arr), EXPECT_TILES)) if base.get(t) != want.get(t)]
    if off:
        problems.append("%d tile(s) differ from the stamp, first %s" % (len(off), [(t, base[t], want.get(t)) for t in off[:5]]))
    for p in problems:
        print("FAIL:", p)
    if not problems:
        print("PASS %s: %d tiles equal %s, %d biomes" % (os.path.basename(a.save), EXPECT_TILES, a.against,
                                                         len(set(base.values()))))
    return 1 if problems else 0


def cmd_selftest(_a):
    base = {0: "RM_NightsideIce", 1: "RM_Wasteland", 2: "RM_Stillsand", 3: "RM_Wasteland"}
    out, moved = apply_paint(base, {"RM_Wasteland": "RM_Wastes"}, {2: "RM_TheScald"})
    assert out == {0: "RM_NightsideIce", 1: "RM_Wastes", 2: "RM_TheScald", 3: "RM_Wastes"}, out
    assert moved == {"RM_Wasteland->RM_Wastes": 2, "edit->RM_TheScald": 1}, moved
    try:
        apply_paint(base, {}, {99: "RM_TheScald"})
        raise AssertionError("an off-grid edit was accepted")
    except ValueError:
        pass
    assert klass("mandrake.rm.biomes") == "ours" and klass("ludeon.rimworld.odyssey") == "vanilla/DLC"
    assert klass("mlie.advancedbiomes") == "DONOR" and klass(None) == "UNKNOWN"
    assert _sha16(["B", "a"]) == _sha16(["A", "b"]), "fingerprint must be order- and case-free"
    names = src_biome_defnames()
    assert "RM_Stillsand" in names, "sanity probe: the src/ BiomeDef reader cannot see RM_Stillsand"
    # by-name decode: the recorded base hashes (geo_landmarks.py pins the same two), a bumped hash, a clash
    assert short_hash("RM_Wasteland") == 18404 and short_hash("RM_NightsideIce") == 21915
    base2, pr = decode_by_name([18404, 21915, 18404], ["RM_Wasteland", "RM_NightsideIce", "RM_Stillsand"])
    assert pr == [] and base2 == {0: "RM_Wasteland", 1: "RM_NightsideIce", 2: "RM_Wasteland"}, (base2, pr)
    _b, pr = decode_by_name([18405], ["RM_Wasteland"])
    assert len(pr) == 1 and "bumped" in pr[0], pr
    tbl, clash = by_name_table(["RM_Wasteland"])
    assert clash == {} and tbl == {18404: "RM_Wasteland"}
    assert short_hash("RM_RustCathedral") == short_hash("RUT_Cauldron") == 3765, "the clash the R3 decode meets"
    _b, pr = decode_by_name([3765], ["RM_RustCathedral", "RUT_Cauldron"])
    assert len(pr) == 1 and "no dump settles" in pr[0], pr
    b3, pr = decode_by_name([3765], ["RM_RustCathedral", "RUT_Cauldron"], {3765: "RM_RustCathedral", 3766: "RUT_Cauldron"})
    assert pr == [] and b3 == {0: "RM_RustCathedral"}, (b3, pr)
    _b, pr = decode_by_name([3765], ["RM_RustCathedral", "RUT_Cauldron"], {3765: "RM_Other"})
    assert pr, "a dump naming a third def settled a clash"
    assert sum(R3_HISTOGRAM_2026_10_21.values()) == EXPECT_TILES, "the recorded R3 histogram must cover the grid"
    # check_stamp: a good stamp passes; an old name, a wrong count, a gap each fail
    hist = dict(R3_HISTOGRAM_2026_10_21)
    hist["RM_Wastes"] = hist.pop("RM_Wasteland")
    rows, t = [], 0
    for b, n in sorted(hist.items()):
        rows += [(t + k, b) for k in range(n)]
        t += n
    prov = {"histogram": hist, "renames": {"RM_Wasteland": "RM_Wastes"}, "moved": {"RM_Wasteland->RM_Wastes": 1853}}
    decl = set(hist)
    assert check_stamp(rows, prov, decl) == [], check_stamp(rows, prov, decl)
    assert check_stamp(rows[:-1], prov, decl), "a missing tile passed"
    assert check_stamp(rows, dict(prov, moved={"RM_Wasteland->RM_Wastes": 3}), decl), "a short move passed"
    bad_rows = rows[:-1] + [(EXPECT_TILES - 1, "RM_Wasteland")]
    assert check_stamp(bad_rows, prov, decl | {"RM_Wasteland"}), "an old name left on a tile passed"
    print("selftest PASS (%d BiomeDefs declared under src/)" % len(names))
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    c = sub.add_parser("census"); c.add_argument("saves", nargs="+"); c.add_argument("--dump"); c.add_argument("--json")
    b = sub.add_parser("build")
    b.add_argument("--save", required=True); b.add_argument("--rename", action="append")
    b.add_argument("--edits", help="CSV tile,biome applied after the renames (paint-list placements)")
    b.add_argument("--out", required=True); b.add_argument("--dump")
    b.add_argument("--allow-fingerprint-mismatch", action="store_true")
    b.add_argument("--allow-not-ours", action="store_true")
    b.add_argument("--decode-by-name", action="store_true",
                   help="decode tiles from defNames' base shortHashes, no mod-set hash table (the save's dump is gone)")
    b.add_argument("--reference", default="r3-2026-10-21", choices=["r3-2026-10-21", "none"],
                   help="the histogram a --decode-by-name decode must equal before anything is written")
    k = sub.add_parser("check"); k.add_argument("csv")
    v = sub.add_parser("verify-save"); v.add_argument("save"); v.add_argument("--against", required=True)
    v.add_argument("--dump")
    sub.add_parser("selftest")
    a = ap.parse_args(argv)
    return {"census": cmd_census, "build": cmd_build, "check": cmd_check, "verify-save": cmd_verify_save,
            "selftest": cmd_selftest}[a.cmd](a)


if __name__ == "__main__":
    sys.exit(main())
