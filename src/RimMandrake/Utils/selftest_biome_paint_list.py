#!/usr/bin/env python3
"""Selftest: the biome paint list matches the 2026-10-21 R3 census (PAINT_LIST_CORRECT_STALE_SINCE_SEPTEMBER).

Offline, < 2 s. Reads infrastructure/state/facts/biome_paint_list.md against the R3 histogram in
design/Jawa/worldbuilding/big_repaint_plan_2026-10-21.md §1a. Checks:
 1 the histogram parses to 27 biomes and 21,872 tiles (sanity probe: the parser can see)
 2 every census biome has exactly one table row whose tile cell equals its count; a renamed def is
   matched through the cell's "(as `OldName`)" note
 3 those rows, and only those, are PAINT (27); every other row is NO PAINT with 0 tiles
 4 every row names its package: RM_ -> mandrake.rm.biomes, RUT_ -> mandrake.rut.patches
 5 no "2026-09-12 export" anywhere in the file; no "not active" in any RM_ row
 6 every table defName is a <defName> in src/ XML; paint_inputs_build.paint_verdicts() agrees with the table
 7 mutant probes: the checker goes red on a changed count, a stale note, a dropped row, a wrong package,
   a flipped verdict and a September-style row

    python3 src/RimMandrake/Utils/selftest_biome_paint_list.py
"""
import os, re, sys, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
PAINTLIST = os.path.join(REPO, "infrastructure", "state", "facts", "biome_paint_list.md")
PLAN = os.path.join(REPO, "design", "Jawa", "worldbuilding", "big_repaint_plan_2026-10-21.md")
CENSUS_BIOMES, CENSUS_TILES = 27, 21872
PACKAGE = {"RM_": "mandrake.rm.biomes", "RUT_": "mandrake.rut.patches"}

fails = []


def ok(cond, name):
    print(("ok  " if cond else "FAIL"), name)
    if not cond:
        fails.append(name)


def census(plan_text):
    """{defName: tiles} from the plan's 'R3's histogram' paragraph."""
    m = re.search(r"R3's histogram.*?\n\n", plan_text, re.S)
    if not m:
        return {}
    para = m.group(0).split("The names in bold")[0]
    return {d: int(n.replace(",", "")) for d, n in re.findall(r"`((?:RM|RUT)_\w+)`\**\s+([\d,]+)", para)}


def table_rows(text):
    """[(defName, cells, raw line)] for every table row starting | `defName` |."""
    rows = []
    for line in text.splitlines():
        if re.match(r"\|\s*`[A-Za-z0-9_]+`\s*\|", line):
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            rows.append((cells[0].strip("`"), cells, line))
    return rows


def check(text, hist):
    """Return a list of problems; empty means the paint list holds the census."""
    bad = []
    if "2026-09-12 export" in text:
        bad.append("'2026-09-12 export' cited")
    rows = table_rows(text)
    if not rows:
        return bad + ["no table rows"]
    seen, by_key = set(), {}
    for d, cells, line in rows:
        if d in seen:
            bad.append("duplicate row %s" % d)
        seen.add(d)
        if len(cells) != 6:
            bad.append("%s has %d cells, not 6" % (d, len(cells)))
            continue
        if d.startswith("RM_") and "not active" in line.lower():
            bad.append("%s says 'not active'" % d)
        pre = "RUT_" if d.startswith("RUT_") else "RM_" if d.startswith("RM_") else None
        if pre is None:
            bad.append("%s is not an RM_/RUT_ def" % d)
        elif not cells[2].endswith("`%s`" % PACKAGE[pre]):
            bad.append("%s package cell %r does not end in `%s`" % (d, cells[2], PACKAGE[pre]))
        tm = re.fullmatch(r"([\d,]+)(?: \(as `(\w+)`\))?", cells[3])
        if not tm:
            bad.append("%s tile cell %r unparsable" % (d, cells[3]))
            continue
        tiles, key = int(tm.group(1).replace(",", "")), tm.group(2) or d
        verdict = cells[5]
        if key in hist:
            by_key[key] = d
            if tiles != hist[key]:
                bad.append("%s tiles %d != census %d" % (d, tiles, hist[key]))
            if verdict != "PAINT":
                bad.append("%s is painted in the census but verdict %r" % (d, verdict))
        else:
            if tiles != 0:
                bad.append("%s claims %d tiles but is not in the census" % (d, tiles))
            if verdict != "NO PAINT":
                bad.append("%s is on 0 census tiles but verdict %r" % (d, verdict))
    for k in hist:
        if k not in by_key:
            bad.append("census biome %s has no row" % k)
    npaint = sum(1 for _, c, _ in rows if len(c) == 6 and c[5] == "PAINT")
    if npaint != len(hist):
        bad.append("%d PAINT rows, census has %d" % (npaint, len(hist)))
    return bad


def src_defnames():
    out = set()
    for root in ("src",):
        for dp, dn, fn in os.walk(os.path.join(REPO, root)):
            dn[:] = [x for x in dn if not x.startswith(".") and x not in ("bin", "obj")]
            for f in fn:
                if f.endswith(".xml"):
                    try:
                        t = open(os.path.join(dp, f), encoding="utf-8", errors="replace").read()
                    except OSError:
                        continue
                    if "<BiomeDef" in t:
                        out.update(re.findall(r"<defName>\s*((?:RM|RUT)_\w+)\s*</defName>", t))
    return out


text = open(PAINTLIST, encoding="utf-8").read()
hist = census(open(PLAN, encoding="utf-8").read())

# 1 the instrument can see
ok(len(hist) == CENSUS_BIOMES, "census parses to %d biomes (got %d)" % (CENSUS_BIOMES, len(hist)))
ok(sum(hist.values()) == CENSUS_TILES, "census sums to %d tiles (got %d)" % (CENSUS_TILES, sum(hist.values())))
rows = table_rows(text)
ok(len(rows) > CENSUS_BIOMES, "paint list table parses (%d rows)" % len(rows))

# 2-5 the paint list holds the census
probs = check(text, hist)
for p in probs:
    print("   ", p)
ok(not probs, "paint list matches the R3 census (counts, verdicts, packages, no stale text)")
ok(text.count("2026-09-12 export") == 0, "no '2026-09-12 export' in the file")

# 6 defs exist; the machine reader agrees
defs = src_defnames()
ok(len(defs) > 40, "src BiomeDef scan sees defs (%d)" % len(defs))
missing = [d for d, _, _ in rows if d not in defs]
ok(not missing, "every table defName is a BiomeDef <defName> in src/ (missing %s)" % missing)
import paint_inputs_build as B  # noqa: E402
pv = B.paint_verdicts()
ok(pv == {d: c[5] for d, c, _ in rows}, "paint_inputs_build.paint_verdicts() equals the table's verdicts")
ok(sum(1 for v in pv.values() if v == "PAINT") == CENSUS_BIOMES, "paint_verdicts() has 27 PAINT")


# 7 mutant probes: each must make check() red
def first_row(d):
    return next(line for x, _, line in rows if x == d)


still, wastes, rut = first_row("RM_Stillsand"), first_row("RM_Wastes"), first_row("RUT_Umbra")
mutants = {
    "count changed": text.replace(still, still.replace("| 3,969 |", "| 3,000 |")),
    "stale note on an RM_ row": text.replace(wastes, wastes.replace(
        "`generatesNaturally=false`", "not active `generatesNaturally=false`")),
    "September tile source cited": text.replace(still, still.replace(
        "carries the home tile", "2026-09-12 export; carries the home tile")),
    "row dropped": text.replace(still + "\n", ""),
    "wrong package": text.replace(still, still.replace("`mandrake.rm.biomes`", "`mlie.advancedbiomes`")),
    "verdict flipped": text.replace(rut, rut.replace("| PAINT |", "| NO PAINT |")),
    "September row": text.replace(still, "| `RM_Stillsand` | the Stillsand | `src/RimMandrake/Stillsand` / "
                                  "`mandrake.rm.biomes` | 0 | not active | PAINT |"),
    "old-name note lost": text.replace(wastes, wastes.replace(" (as `RM_Wasteland`)", "")),
}
for name, mt in mutants.items():
    ok(mt != text, "mutant '%s' differs from the file" % name)
    ok(bool(check(mt, hist)), "mutant '%s' goes red" % name)

# the machine reader sees a flipped verdict too
with tempfile.NamedTemporaryFile("w", suffix=".md", delete=False, encoding="utf-8") as tf:
    tf.write(mutants["verdict flipped"])
saved = B.PAINTLIST
try:
    B.PAINTLIST = tf.name
    ok(B.paint_verdicts().get("RUT_Umbra") == "NO PAINT", "probe: paint_verdicts() reads a flipped verdict")
finally:
    B.PAINTLIST = saved
    os.unlink(tf.name)

print("FAIL selftest_biome_paint_list %s" % fails if fails else "OK selftest_biome_paint_list")
sys.exit(1 if fails else 0)
