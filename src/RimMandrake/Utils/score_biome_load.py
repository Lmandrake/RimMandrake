#!/usr/bin/env python3
"""Score the BIOME RESTORATION block of EXPECTED_FAILURES_next_load.md. Run after the load.

⚠️ FIND THAT BLOCK BY ITS TITLE, NOT ITS NUMBER. This docstring said "§6" until
2026-08-23; the block was renumbered to §9 because §6 was already the closed 2026-08-21
load with a filled Results table. ✅ Nothing functional depended on it — the signature
strings live in this file and it reads the engine log directly, never the markdown — but a
reader following "§6" landed on another load's answers. Block numbers in that file have
now collided twice; see BIOME_BLOCK_MISNUMBERED_SIX_1.

    python3 src/RimMandrake/Utils/score_biome_load.py

Scores every row that can be read from the LOG and the DEF DUMP. P2 is deliberately
NOT here: it needs the live bridge and Windows python, and it is
`src/RimMandrake/bridgetools/check_map_biomes_live.py`.

🔑 P1 IS SCORED FIRST AND ON PURPOSE. All 26 operations in BiomeCast_Ashkarr.xml are
`PatchOperationConditional`, which returns true when it matches nothing - so if the
biomes are still absent for some other reason the patch goes SILENT and every
"expected absent" string below reads clean against a broken game. The ABSENT table
cannot detect that failure on its own.
"""
import glob, io, json, os, sys

BASE = ("/mnt/c/Users/Mandrake/AppData/LocalLow/Ludeon Studios/"
        "RimWorld by Ludeon Studios")
LOG = os.path.join(BASE, "Player.log")
REPO = os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.dirname(os.path.abspath(__file__)))))  # Utils -> RimMandrake -> src -> repo

# string -> (row, expected count, what a miss means)
ABSENT = {
    "Exception loading def from file Biomes_":
        ("F1", 0, "was 22 - the exception that discarded the biomes"),
    "BiomeAnimalRecord.LoadDataFromXmlCustom":
        ("F2", 0, "was 1 stack behind 22 throws"),
    "There are 54 defs of this type loaded":
        ("F3", 0, "was 26. A DIFFERENT number is still a fail - read it, it says how many survived"),
    "SWPotF_RaceDef_ysalamir":
        ("F5a", 0, "a ThingDef, now skipped rather than emitted"),
    "GiantAnt_Race":
        ("F5b", 0, "a ThingDef, now skipped rather than emitted"),
}
PRESENT = {
    "[Inhabited] ready:": ("P3", "294 characters"),
    "[JawaBench] ready:": ("P4", "121 tools"),
}

def newest_capture():
    caps = sorted(glob.glob(os.path.join(BASE, "DefDump", "captures", "*")))
    for c in reversed(caps):
        if os.path.isfile(os.path.join(c, "defs", "BiomeDef.json")):
            return c
    return None

def main():
    fails = []

    # ---- P1 first, and it is the only row that can catch a silent no-match ----
    cap = newest_capture()
    if not cap:
        print("P1  UNMEASURED  no capture holds a BiomeDef.json - was the dump armed?")
        fails.append("P1")
        biomes = set()
    else:
        d = json.load(io.open(os.path.join(cap, "defs", "BiomeDef.json"), encoding="utf-8"))
        defs = d if isinstance(d, list) else d["defs"]
        biomes = {x["defName"] for x in defs}
        ok = len(biomes) >= 80
        print("%s  P1  BiomeDef count = %d  (pass = 80; 54 means the fix never reached the game)"
              % ("PASS " if ok else "FAIL ", len(biomes)))
        print("      capture: %s" % os.path.basename(cap))
        if not ok:
            fails.append("P1")

    # ---- the map's own roster, offline half of P2 ----
    import csv
    tiles = os.path.join(REPO, "world", "ASHKARR_WORLDMAP_tiles.csv")
    if os.path.isfile(tiles) and biomes:
        import collections
        c = collections.Counter()
        with io.open(tiles, encoding="utf-8", newline="") as fh:
            for row in csv.DictReader(fh):
                c[row["biome"]] += 1
        missing = [(b, n) for b, n in c.most_common() if b not in biomes]
        lost = sum(n for _, n in missing)
        tot = sum(c.values())
        print("%s  P2* %d of %d map biomes resolve in the DUMP; %d tiles (%.1f%%) would not stamp"
              % ("PASS " if not missing else "FAIL ", len(c) - len(missing), len(c), lost, 100.0 * lost / tot))
        for b, n in missing[:10]:
            print("        MISSING %-30s %6d tiles" % (b, n))
        if missing:
            fails.append("P2*")
        print("      * dump-based. The LIVE reading is bridgetools/check_map_biomes_live.py")

    # ---- one streaming pass over the log ----
    if not os.path.isfile(LOG):
        sys.exit("no Player.log at %s" % LOG)
    counts = {k: 0 for k in list(ABSENT) + list(PRESENT)}
    first = {}
    xref = 0
    n = 0
    with io.open(LOG, encoding="utf-8", errors="replace") as fh:
        for i, line in enumerate(fh, 1):
            n = i
            if "Could not resolve cross-reference" in line:
                xref += 1
            for k in counts:
                if k in line:
                    counts[k] += 1
                    first.setdefault(k, (i, line.strip()[:150]))
    print("\nlog: %s lines" % format(n, ","))

    for k, (row, want) in PRESENT.items():
        got = first.get(k)
        if not got:
            print("FAIL   %s  %-26s ABSENT  (expected %s)" % (row, k, want))
            fails.append(row)
        else:
            print("PASS   %s  L%-9d %s" % (row, got[0], got[1]))

    for k, (row, want, why) in ABSENT.items():
        c = counts[k]
        ok = c == want
        print("%s  %s  %-46s %d   %s" % ("PASS " if ok else "FAIL ", row, k, c, "" if ok else why))
        if not ok:
            fails.append(row)
            if k in first:
                print("        first at L%d: %s" % first[k])

    ok = xref <= 40
    print("%s  F4  Could not resolve cross-reference          %d   (was 3037; baseline 25)"
          % ("PASS " if ok else "FAIL ", xref))
    if not ok:
        fails.append("F4")

    print("\n%s" % ("ALL ROWS PASS" if not fails else "FAILED ROWS: " + ", ".join(fails)))
    return 1 if fails else 0

if __name__ == "__main__":
    sys.exit(main())
