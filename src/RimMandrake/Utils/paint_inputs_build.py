#!/usr/bin/env python3
"""paint_inputs_build.py - G7 'stamp inputs valid': build the w9 paint bundle and resolve it.

    python3 src/RimMandrake/Utils/paint_inputs_build.py            build + resolve (writes --out)
    python3 src/RimMandrake/Utils/paint_inputs_build.py --check    resolve an existing --out only

Reads the canonical-save export (world/rescue_2026-10-19/ported/, names already through the
historical renames) and writes a NEW folder (default world/paint_inputs_2026-10-20/) that
`w9_run.py --inputs DIR` stamps. Remaps come from one table,
design/RimMandrake/world_remake_2026-10-19/paint_inputs_remap.json (biome twins -> RM_ survivors,
unported mutators, dropped factions, the region-label FeatureDef), plus
design/RimMandrake/retired_mutators_port_map.json for mutators/landmarks.

Then EVERY def name in every written CSV is resolved against the PAINT def closure: every def
in the newest def-dump capture whose packageId is on
infrastructure/state/modlists/ModsConfig.PAINT.RULED_2026-10-20.xml (the closure rule of
selftest_ship_paint_closure.py). RESOLVER.md + resolver.json record it. Exit 1 if any name is
unresolved, or the instrument is blind (sanity probe: the closure must hold Human and RUT_Umbra,
and the UN-remapped source must show unresolved mutators - an instrument that cannot see the
loss proves nothing).

🔴 Refuses to write into world/ itself: world/ASHKARR_WORLDMAP_*.csv is the frozen RECORD.
"""
import argparse, collections, csv, io, json, os, re, sys, xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, HERE)

PAINT = os.path.join(REPO, "infrastructure/state/modlists/ModsConfig.PAINT.RULED_2026-10-20.xml")
TABLE = os.path.join(REPO, "design/RimMandrake/world_remake_2026-10-19/paint_inputs_remap.json")
PORTMAP = os.path.join(REPO, "design/RimMandrake/retired_mutators_port_map.json")
PAINTLIST = os.path.join(REPO, "infrastructure/state/facts/biome_paint_list.md")
SRC = os.path.join(REPO, "world/rescue_2026-10-19/ported")
OUT = os.path.join(REPO, "world/paint_inputs_2026-10-20")
F = "ASHKARR_WORLDMAP_%s.csv"
COPIED = ("tiles", "links", "settlements", "mutators", "landmarks", "factions", "features")

# (layer, column, def type, splitter) - every def-bearing column a written CSV carries.
DEF_COLUMNS = [
    ("tiles", "biome", "BiomeDef", None),
    ("links", "def", "RiverDef", lambda r: r["kind"] == "river"),
    ("links", "def", "RoadDef", lambda r: r["kind"] == "road"),
    ("settlements", "faction_def", "FactionDef", None),
    ("settlements", "biome", "BiomeDef", None),
    ("mutators", "mutators", "TileMutatorDef", ";"),
    ("landmarks", "landmark", "LandmarkDef", None),
    ("factions", "def", "FactionDef", None),
    ("factions", "ideo_culture", "CultureDef", None),
    ("features", "def", "FeatureDef", None),
]


def read(path):
    with io.open(path, encoding="utf-8-sig", newline="") as fh:
        r = csv.DictReader(fh)
        return r.fieldnames, list(r)


def write(path, fields, rows):
    with io.open(path, "w", encoding="utf-8", newline="") as fh:
        wr = csv.DictWriter(fh, fieldnames=fields, lineterminator="\n")
        wr.writeheader()
        wr.writerows(rows)


def closure():
    """{defType: {defName: packageId}} for the PAINT profile, from the newest dump capture."""
    import game_paths
    ids = {li.text.strip().lower() for li in ET.parse(PAINT).getroot().find("activeMods")}
    cap = game_paths.DEF_DUMP
    man = json.load(io.open(os.path.join(cap, "manifest.json"), encoding="utf-8-sig"))
    capids = {m["packageId"].lower() for m in man.get("mods", [])}
    by = collections.defaultdict(dict)
    unreadable = []
    ddir = os.path.join(cap, "defs")
    for f in os.listdir(ddir):
        try:
            j = json.load(io.open(os.path.join(ddir, f), encoding="utf-8-sig"))
        except Exception:
            # Never silent: an unreadable def file under-counts the closure and every name in it
            # would then read as "unresolved" (or worse, a probe would pass on a thin closure).
            unreadable.append(f)
            continue
        # Bucket by the FILE's def type, not each def's own: HAR re-types Human as
        # ThingDef_AlienRace inside ThingDef.json, and a subclass must still count as its base.
        ftype = j.get("defType") or f[:-5]
        for d in j.get("defs", []):
            if (d.get("packageId") or "").lower() in ids:
                by[ftype][d["defName"]] = d.get("packageId")
    return by, {"capture": os.path.basename(cap), "capturedUtc": man.get("capturedUtc"),
                "paint_mods": len(ids), "paint_mods_absent_from_capture": sorted(ids - capids),
                "unreadable_def_files": unreadable}


def paint_verdicts():
    """{defName: 'PAINT'|'NO PAINT'} from the paint list's table (last column)."""
    v = {}
    for line in io.open(PAINTLIST, encoding="utf-8"):
        m = re.match(r"\|\s*`([A-Za-z0-9_]+)`\s*\|", line)
        if m:
            last = line.rstrip().rstrip("|").rsplit("|", 1)[-1].strip()
            v[m.group(1)] = "NO PAINT" if last.startswith("NO PAINT") else "PAINT"
    return v


def names(layer, rows, col, typ, sel):
    c = collections.Counter()
    for r in rows:
        if callable(sel) and not sel(r):
            continue
        val = r.get(col) or ""
        for n in (val.split(";") if sel == ";" else [val]):
            if n:
                c[n] += 1
    return c


def build(src, out, tab, pm, log):
    tb, keep = tab["biome"], tab["biome_keep"]
    assert not set(tb) & set(keep), "a biome is both remapped and kept"
    # tiles
    fields, tiles = read(os.path.join(src, F % "tiles"))
    moved = collections.Counter()
    for r in tiles:
        b = r["biome"]
        if b in tb:
            moved[(b, tb[b])] += 1
            r["biome"] = tb[b]
    write(os.path.join(out, F % "tiles"), fields, tiles)
    biome_of = {r["tile"]: r["biome"] for r in tiles}
    log["tiles"] = {"rows": len(tiles), "remapped": sum(moved.values()),
                    "moves": [[a, b, n] for (a, b), n in sorted(moved.items())]}
    # settlements
    fields, sett = read(os.path.join(src, F % "settlements"))
    pre = tab["settlement_faction_prefix"]
    nf = nb = 0
    for r in sett:
        if r["faction_def"].startswith(pre["from"]):
            r["faction_def"] = pre["to"] + r["faction_def"][len(pre["from"]):]
            nf += 1
        if biome_of.get(r["tile"]) and r["biome"] != biome_of[r["tile"]]:
            r["biome"] = biome_of[r["tile"]]
            nb += 1
    write(os.path.join(out, F % "settlements"), fields, sett)
    log["settlements"] = {"rows": len(sett), "faction_prefixed": nf, "biome_column_synced_to_tile": nb}
    # mutators: port map, then the table
    pmm = {k: v.get("new") for k, v in pm["TileMutatorDef"].items()}
    tm = tab["mutators"]
    fields, muts = read(os.path.join(src, F % "mutators"))
    acts, kept = collections.Counter(), []
    for r in muts:
        new = []
        for n in [x for x in r["mutators"].split(";") if x]:
            if n in tm:
                t = tm[n]["new"]
                acts[(n, t or "DROP")] += 1
                n = t
            elif n in pmm:
                acts[(n, pmm[n] or "DROP")] += 1
                n = pmm[n]
            if n and n not in new:
                new.append(n)
        if new:
            r["mutators"] = ";".join(new)
            kept.append(r)
    write(os.path.join(out, F % "mutators"), fields, kept)
    log["mutators"] = {"tiles_in": len(muts), "tiles_out": len(kept),
                       "actions": [[a, b, n] for (a, b), n in sorted(acts.items())]}
    # landmarks
    plm = {k: v.get("new") for k, v in pm["LandmarkDef"].items()}
    plm.update({k: v["new"] for k, v in tab["landmarks"].items()})
    fields, lmk = read(os.path.join(src, F % "landmarks"))
    acts, kept = collections.Counter(), []
    for r in lmk:
        n = r["landmark"]
        if n in plm:
            acts[(n, plm[n] or "DROP")] += 1
            if not plm[n]:
                continue
            r["landmark"] = plm[n]
        kept.append(r)
    write(os.path.join(out, F % "landmarks"), fields, kept)
    log["landmarks"] = {"rows_in": len(lmk), "rows_out": len(kept),
                        "actions": [[a, b, n] for (a, b), n in sorted(acts.items())]}
    # links: unchanged
    fields, links = read(os.path.join(src, F % "links"))
    write(os.path.join(out, F % "links"), fields, links)
    log["links"] = {"rows": len(links)}
    # factions: drop, and strip relations naming a dropped ref
    fields, fac = read(os.path.join(src, F % "factions"))
    drop = tab["factions_drop"]
    gone = {r["ref"] for r in fac if r["def"] in drop}
    kept = []
    for r in fac:
        if r["ref"] in gone:
            continue
        r["relations"] = ";".join(x for x in (r["relations"] or "").split(";")
                                  if x and x.split(":")[0] not in gone)
        kept.append(r)
    write(os.path.join(out, F % "factions"), fields, kept)
    log["factions"] = {"rows_in": len(fac), "rows_out": len(kept),
                       "dropped": sorted(r["def"] for r in fac if r["ref"] in gone)}
    # features: one def for all labels
    fields, feat = read(os.path.join(src, F % "features"))
    fd = tab["feature_def"]["new"]
    old = sorted({r["def"] for r in feat})
    for r in feat:
        r["def"] = fd
    write(os.path.join(out, F % "features"), fields, feat)
    log["features"] = {"rows": len(feat), "def": [old, fd]}


def resolve(d, by, tab):
    """-> (report dict, unresolved list). Unresolved = a name absent from the closure."""
    rep, unres = [], []
    for layer, col, typ, sel in DEF_COLUMNS:
        p = os.path.join(d, F % layer)
        if not os.path.isfile(p):
            unres.append([layer, col, typ, "<file missing>", 0])
            continue
        _, rows = read(p)
        c = names(layer, rows, col, typ, sel)
        bad = {k: v for k, v in c.items() if k not in by.get(typ, {})}
        rep.append({"layer": layer, "column": col, "type": typ, "distinct": len(c),
                    "entries": sum(c.values()), "unresolved": bad})
        unres += [[layer, col, typ, k, v] for k, v in sorted(bad.items())]
    return rep, unres


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", default=SRC)
    ap.add_argument("--out", default=OUT)
    ap.add_argument("--check", action="store_true", help="resolve --out only, write nothing but the report")
    a = ap.parse_args(argv)
    out = os.path.abspath(a.out)
    if os.path.realpath(out) in (os.path.realpath(os.path.join(REPO, "world")), os.path.realpath(a.src)):
        print("REFUSED: --out is world/ (the frozen record) or the --src folder it is built from")
        return 2
    tab = json.load(open(TABLE))
    pm = json.load(open(PORTMAP))
    by, prov = closure()
    # sanity probe 1: the instrument can see
    if "Human" not in by.get("ThingDef", {}) or "RUT_Umbra" not in by.get("BiomeDef", {}):
        print("FAIL instrument blind: closure lacks Human or RUT_Umbra")
        return 1
    if prov["unreadable_def_files"]:
        print("FAIL capture def files unreadable %s - closure would under-count" % prov["unreadable_def_files"])
        return 1
    if prov["paint_mods_absent_from_capture"]:
        print("FAIL capture lacks PAINT mods %s - closure would under-count" % prov["paint_mods_absent_from_capture"])
        return 1
    # sanity probe 2: the raw source shows the known loss
    _, rawm = read(os.path.join(a.src, F % "mutators"))
    raw_bad = {k for k in names("mutators", rawm, "mutators", "TileMutatorDef", ";")
               if k not in by["TileMutatorDef"]}
    if not raw_bad:
        print("FAIL probe: the un-remapped source resolves fully - the resolver cannot see a loss")
        return 1
    log = {}
    if not a.check:
        os.makedirs(out, exist_ok=True)
        build(a.src, out, tab, pm, log)
    rep, unres = resolve(out, by, tab)
    verdict = paint_verdicts()
    _, tiles = read(os.path.join(out, F % "tiles"))
    bc = collections.Counter(r["biome"] for r in tiles)
    nopaint = {b: n for b, n in bc.items() if verdict.get(b) != "PAINT"}
    res = {"closure": prov, "closure_sizes": {t: len(by.get(t, {})) for t in sorted({c[2] for c in DEF_COLUMNS})},
           "probe_raw_unresolved_mutators": sorted(raw_bad), "build": log, "resolve": rep,
           "unresolved": unres, "tile_biomes": dict(bc.most_common()),
           "tile_biomes_not_PAINT_verdict": nopaint}
    with io.open(os.path.join(out, "resolver.json"), "w", encoding="utf-8") as fh:
        json.dump(res, fh, indent=1, ensure_ascii=False)
        fh.write("\n")
    md = ["# Paint inputs resolver - %s" % ("PASS" if not unres and not nopaint else "FAIL"), "",
          "Written by `src/RimMandrake/Utils/paint_inputs_build.py`. Closure: every def in capture `%s` "
          "(%s) whose packageId is on `ModsConfig.PAINT.RULED_2026-10-20.xml` (%d mods, 0 absent from the capture)."
          % (prov["capture"], prov["capturedUtc"], prov["paint_mods"]), "",
          "Sanity probe: the un-remapped source carries %d mutator names outside the closure (%s), so the "
          "instrument can see a loss." % (len(raw_bad), ", ".join(sorted(raw_bad))), "",
          "| layer | column | def type | distinct | entries | unresolved |", "|---|---|---|---|---|---|"]
    for r in rep:
        md.append("| %s | %s | %s | %d | %d | %d |" % (r["layer"], r["column"], r["type"], r["distinct"],
                                                    r["entries"], len(r["unresolved"])))
    md += ["", "**Unresolved: %d.** Tile biomes whose paint-list verdict is not PAINT: %d %s"
           % (len(unres), len(nopaint), nopaint or ""), "",
           "## Tile biomes written", "", "| biome | tiles |", "|---|---|"]
    md += ["| `%s` | %d |" % (b, n) for b, n in bc.most_common()]
    for u in unres:
        md.append("- UNRESOLVED %s" % u)
    with io.open(os.path.join(out, "RESOLVER.md"), "w", encoding="utf-8") as fh:
        fh.write("\n".join(md) + "\n")
    print("resolver: %d unresolved, %d non-PAINT tile biomes -> %s"
          % (len(unres), len(nopaint), os.path.join(out, "RESOLVER.md")))
    return 1 if unres or nopaint else 0


if __name__ == "__main__":
    sys.exit(main())
