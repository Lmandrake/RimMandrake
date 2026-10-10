#!/usr/bin/env python3
"""MINERALS_WHERE_THEY_BELONG_1 wave R1 (offline half): validate the mineral abundance registry CSV.

Checks: every biome column is a real BiomeDef (or the OTHER_vanilla_biomes pseudo-column), every
biome cell is a number or a legal token, units are legal, status present, duplicate materials,
and every row with status RULED/BUILT is reported as emit-eligible. Numbers in the CSV are agent
GUESSES (PROVISIONAL) until the owner approves the numbers sheet; this tool never ships them.
Usage: mineral_registry_check.py [csv]      mineral_registry_check.py --selftest
Exit 1 on a hard defect."""
import csv, glob, os, re, sys
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
CSV = os.path.join(ROOT, "design/RimMandrake/mineral_abundance_registry_2026-10-03.csv")
UNITS = {"EPM", "EPM/yr", "UPY", "deep share", "—"}
TOKENS = {"deep-only", "herd", "unbounded"}
PSEUDO = {"OTHER_vanilla_biomes"}

def biome_defnames(root=ROOT):
    names = set()
    for f in glob.glob(os.path.join(root, "src", "**", "*.xml"), recursive=True):
        try:
            t = open(f, encoding="utf-8", errors="ignore").read()
        except OSError:
            continue
        if "<BiomeDef" not in t:
            continue
        for m in re.finditer(r"<BiomeDef\b[^>]*>\s*<defName>(\w+)</defName>", t):
            names.add(m.group(1))
    return names

def check(path, biomes):
    rows = list(csv.DictReader(open(path, encoding="utf-8")))
    cols = [k for k in rows[0] if k.startswith(("RM_", "RUT_")) or k in PSEUDO]
    hard, soft, eligible, seen = [], [], [], set()
    for c in cols:
        if c not in PSEUDO and c not in biomes:
            soft.append(f"column {c}: no BiomeDef with that defName found in src (rename pending or biome unbuilt)")
    for r in rows:
        m = r["material"]
        if m in seen: hard.append(f"{m}: duplicate row")
        seen.add(m)
        if r["unit"] not in UNITS: hard.append(f"{m}: illegal unit {r['unit']!r}")
        if not r["status"].strip(): hard.append(f"{m}: empty status")
        for c in cols:
            v = r[c].strip()
            if v in TOKENS or re.fullmatch(r"\d+(\.\d+)?", v): continue
            hard.append(f"{m}/{c}: bad cell {v!r}")
        if re.match(r"(RULED|BUILT)", r["status"].strip()): eligible.append(m)
    return rows, hard, soft, eligible

def selftest():
    import tempfile
    d = tempfile.mkdtemp(); p = os.path.join(d, "r.csv")
    open(p, "w", encoding="utf-8").write("material,defs,unit,RM_A,RM_B,status\nx,d,EPM,5,bogus,RULED\nx,d,zz,0,deep-only,\n")
    _, hard, soft, el = check(p, {"RM_A"})
    assert any("bad cell" in h for h in hard) and any("duplicate" in h for h in hard)
    assert any("illegal unit" in h for h in hard) and any("empty status" in h for h in hard)
    assert any("RM_B" in s for s in soft) and el == ["x"]
    rows, hard, _, _ = check(CSV, biome_defnames())
    assert len(rows) > 40 and not hard, hard
    print("selftest ok")

if __name__ == "__main__":
    if "--selftest" in sys.argv: selftest(); sys.exit(0)
    p = next((a for a in sys.argv[1:] if not a.startswith("-")), CSV)
    rows, hard, soft, el = check(p, biome_defnames())
    print(f"{len(rows)} rows, {len(el)} emit-eligible (RULED/BUILT), {len(hard)} hard, {len(soft)} soft; values PROVISIONAL")
    for s in soft: print("SOFT", s)
    for h in hard: print("HARD", h)
    sys.exit(1 if hard else 0)
