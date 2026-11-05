#!/usr/bin/env python3
"""Selftest for the mineable-scatterer census (MINERAL_SCATTERERS_AUDIT_OUTSIDE_ROCKS).

1. scatterer_census.py's detectors see what they must (fixture DLL bytes, fixture XML, a fixture mod tree) and not more.
2. The committed census TSV is whole: every row names a known cover, an adapter cover names a source file that exists and
   mentions the row's engine symbol, and every row is named in the R5 item prose
   (infrastructure/state/items/MINERAL_ADAPTERS_BUILD_DONOR_SOURCES.md), so R5 covers each one.
"""
import csv
import os
import re
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, HERE)
import scatterer_census as sc  # noqa: E402

CENSUS = os.path.join(REPO, "design", "RimMandrake", "mineral_scatterers_census_2026-11-05.tsv")
R5 = os.path.join(REPO, "infrastructure", "state", "items", "MINERAL_ADAPTERS_BUILD_DONOR_SOURCES.md")
COVERS = {"surface_placer", "explicit_lists", "meteorite", "r5_owed", "item", "none_owed"}
ADAPTER_COVERS = {"surface_placer", "explicit_lists", "meteorite"}
COLS = ["id", "source", "engine_symbol", "picks_by", "policy_effect", "cover", "cover_where"]

fails = []
passes = 0


def check(ok, what):
    global passes
    if ok:
        passes += 1
    else:
        fails.append(what)


# ---- 1. detectors -------------------------------------------------------------------------------------------------
check(sc.dll_hits(b"\x00junk mineableScatterCommonality\x00GenStep_ScatterLumpsMineable\x00")
      == ["mineableScatterCommonality", "GenStep_ScatterLumpsMineable"], "dll_hits finds both metadata names")
check(sc.dll_hits(b"mineableScatterLumpSizeRange isResourceRock") == [], "dll_hits ignores near-miss names")
check(sc.dll_hits(b"TileMutatorWorker_MineralRich") == ["TileMutatorWorker_MineralRich"], "dll_hits sees MineralRich")
fx = b"""<Defs><GenStepDef><defName>A</defName><genStep Class="GenStep_ScatterLumpsMineable"><count>3</count></genStep>
</GenStepDef><GenStepDef><defName>B</defName><genStep Class="Foo.GenStep_ScatterLumpsMineableX">
<forcedDefToScatter>MineableSteel</forcedDefToScatter></genStep></GenStepDef>
<GenStepDef><defName>C</defName><genStep Class="GenStep_ScatterThings"/></GenStepDef></Defs>"""
check(sc.xml_hits(fx) == [("GenStep_ScatterLumpsMineable", ""), ("Foo.GenStep_ScatterLumpsMineableX", "MineableSteel")],
      "xml_hits: unforced and forced lump steps, not ScatterThings")
check(sc.xml_hits(b"<Defs><broken") is None, "xml_hits: a parse error is None (unknown), not an empty list")

with tempfile.TemporaryDirectory() as tmp:
    for name, pid in (("ModA", "x.a"), ("ModB", "x.b")):
        os.makedirs(os.path.join(tmp, name, "About"))
        with open(os.path.join(tmp, name, "About", "About.xml"), "w") as f:
            f.write("<ModMetaData><packageId>%s</packageId></ModMetaData>" % pid.upper())
    os.makedirs(os.path.join(tmp, "ModA", "1.6", "Assemblies"))
    with open(os.path.join(tmp, "ModA", "1.6", "Assemblies", "a.dll"), "wb") as f:
        f.write(b"MZ..mineableScatterCommonality..")
    os.makedirs(os.path.join(tmp, "ModB", "Defs"))
    with open(os.path.join(tmp, "ModB", "Defs", "g.xml"), "wb") as f:
        f.write(fx)
    with open(os.path.join(tmp, "ModB", "Defs", "plain.xml"), "wb") as f:
        f.write(b"<Defs><ThingDef><defName>Rock</defName></ThingDef></Defs>")
    with open(os.path.join(tmp, "ModB", "Defs", "bad.xml"), "wb") as f:
        f.write(b'<Defs><GenStepDef><genStep Class="GenStep_ScatterLumpsMineable">')
    rows = sc.scan([tmp], active={"x.a"})
    check([r[3] for r in rows if r[0] == "parse_error"] == [os.path.join("Defs", "bad.xml")],
          "scan: an XML that names a lump step but does not parse is a parse_error row, not silence")
    rows = [r for r in rows if r[0] != "parse_error"]
    kinds = sorted((r[0], r[1], r[2]) for r in rows)
    check(kinds == [("dll", "x.a", "yes"), ("xml", "x.b", "no"), ("xml", "x.b", "no")],
          "scan: one dll hit in an active mod, two xml hits in an inactive one, packageId lower-cased: %r" % kinds)
    check(len(sc.scan([os.path.join(tmp, "ModA")])) == 1, "scan: a root that is itself a mod is scanned as one mod")
    halves = [sorted(r[1] for r in sc.scan([tmp], None, (i, 2)) if r[0] != "parse_error") for i in (0, 1)]
    check(halves == [["x.a"], ["x.b", "x.b"]], "scan: shard 0/2 and 1/2 split the mods between them: %r" % halves)
    check(sc.scan([os.path.join(tmp, "nope")])[0][0] == "error", "scan: a missing root is an error row")
    mc = os.path.join(tmp, "mc.xml")
    with open(mc, "w") as f:
        f.write("<ModsConfigData><activeMods><li>X.A_steam</li><li>x.b</li></activeMods></ModsConfigData>")
    check(sc.active_ids(mc) == {"x.a", "x.b"}, "active_ids: lower-cased, _steam suffix dropped")
    with open(mc, "w") as f:
        f.write("<ModsConfigData><version>1.6</version></ModsConfigData>")
    check(sc.active_ids(mc) is None, "active_ids: no activeMods is unknown (None), never an empty set")

# ---- 2. the census is whole and R5 names every row ------------------------------------------------------------------
check(os.path.isfile(CENSUS), "census TSV exists: " + CENSUS)
check(os.path.isfile(R5), "R5 item prose exists: " + R5)
if os.path.isfile(CENSUS) and os.path.isfile(R5):
    with open(CENSUS, encoding="utf-8") as f:
        rd = csv.DictReader(f, delimiter="\t")
        check(rd.fieldnames == COLS, "census columns are %s, got %s" % (COLS, rd.fieldnames))
        census = list(rd)
    with open(R5, encoding="utf-8") as f:
        r5 = f.read()
    check(len(census) >= 8, "census has its rows (%d)" % len(census))
    ids = [r["id"] for r in census]
    check(len(ids) == len(set(ids)), "census ids are unique")
    for r in census:
        rid, cover, where = r["id"], r.get("cover") or "", r.get("cover_where") or ""
        check(None not in r and all((r.get(c) or "").strip() for c in COLS), rid + ": every column filled, none extra")
        check(cover in COVERS, rid + ": cover %r is one of %s" % (cover, sorted(COVERS)))
        check(("`%s`" % rid) in r5, rid + ": named in R5 item prose")
        if cover in ADAPTER_COVERS:
            p = os.path.join(REPO, where)
            ok = os.path.isfile(p)
            check(ok, rid + ": adapter file exists " + where)
            if ok:
                with open(p, encoding="utf-8") as f:
                    src = f.read()
                sym = (r.get("engine_symbol") or "").split(".")[-1] or "\x00none"
                check(re.search(r"\b%s\b" % re.escape(sym), src) is not None, rid + ": %s names %s" % (where, sym))
        elif cover == "item":
            check(re.fullmatch(r"[A-Z][A-Z0-9_]+", where) is not None and where in r5,
                  rid + ": owning item %r is an item id and R5 cites it" % where)
        elif cover == "r5_owed":
            check(where == "MINERAL_ADAPTERS_BUILD_DONOR_SOURCES", rid + ": r5_owed points at R5")

print("selftest_mineral_scatterer_census: %d passed, %d failed" % (passes, len(fails)))
for x in fails:
    print("FAIL " + x)
sys.exit(1 if fails else 0)
