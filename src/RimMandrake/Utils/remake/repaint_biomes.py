#!/usr/bin/env python3
"""The big repaint, offline half: measure what a save's planet carries, and build the
biome-only stamp CSV that `jawa/world_tile_import` paints onto the live dev world.

Plan: design/Jawa/worldbuilding/big_repaint_plan_2026-10-21.md (owner 2026-10-21: "The world
we're building now is the big repaint! Right now!").

    python3 src/RimMandrake/Utils/remake/repaint_biomes.py census <save.rws> [...]
    python3 src/RimMandrake/Utils/remake/repaint_biomes.py build --save <save.rws> \
        --rename RM_NightsideIce=RM_SleepingIce --rename RM_Wasteland=RM_Wastes \
        [--edits tile_biome_edits.csv] --out <tiles_biome_only.csv>
    python3 src/RimMandrake/Utils/remake/repaint_biomes.py selftest

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
import argparse, collections, csv, hashlib, json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
UTILS = os.path.dirname(HERE)
REPO = os.path.abspath(os.path.join(UTILS, "..", "..", ".."))
sys.path.insert(0, UTILS)

EXPECT_TILES = 21872
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


def cmd_build(a):
    import worldmap
    dump = a.dump or _dump_dir()
    n_s, sha_s = save_fingerprint(a.save)
    n_d, sha_d, cap = dump_fingerprint(dump)
    if sha_s != sha_d and not a.allow_fingerprint_mismatch:
        print("REFUSED: save mod set %d/%s != dump %d/%s (captured %s). A hash table from another mod set "
              "can decode a tile to the WRONG biome. Re-capture the dump on the save's list, or pass "
              "--allow-fingerprint-mismatch and say why." % (n_s, sha_s, n_d, sha_d, cap))
        return 2
    g = worldmap.WorldGrid(a.save, os.path.join(dump, "defs"))
    if g.unresolved():
        print("REFUSED: %d tileBiome hash(es) unresolved in this dump: %s" % (len(g.unresolved()), g.unresolved()[:10]))
        return 2
    arr = g.arrays["tileBiome"]
    if len(arr) != EXPECT_TILES:
        print("REFUSED: %d tiles, expected %d" % (len(arr), EXPECT_TILES))
        return 2
    base = {i: g.biome_by_hash[h] for i, h in enumerate(arr)}
    renames = {}
    for r in a.rename or []:
        old, _, new = r.partition("=")
        if not old or not new:
            print("REFUSED: --rename wants OLD=NEW, got %r" % r)
            return 2
        renames[old] = new
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
    os.makedirs(os.path.dirname(os.path.abspath(a.out)), exist_ok=True)
    with open(a.out, "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["tile", "biome"])
        for t in range(EXPECT_TILES):
            w.writerow([t, out[t]])
    prov = {"save": a.save, "save_mods": n_s, "save_sha16": sha_s, "dump_captured": cap, "dump_sha16": sha_d,
            "renames": renames, "edits_file": a.edits, "edits": len(edits), "moved": dict(moved),
            "renames_with_no_tiles": absent_old, "histogram": dict(hist.most_common()),
            "import": "jawa/world_tile_import {path:<this csv, Windows path>, apply:false, expectTiles:%d} "
                      "then apply:true, then jawa/world_tile_validate on the same path, then jawa/world_commit"
                      % EXPECT_TILES}
    json.dump(prov, open(a.out + ".provenance.json", "w"), indent=1)
    print("wrote %s (%d tiles, %d biomes); moved %s; renames with no tiles %s" % (
        a.out, EXPECT_TILES, len(hist), dict(moved), absent_old))
    return 0


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
    sub.add_parser("selftest")
    a = ap.parse_args(argv)
    return {"census": cmd_census, "build": cmd_build, "selftest": cmd_selftest}[a.cmd](a)


if __name__ == "__main__":
    sys.exit(main())
