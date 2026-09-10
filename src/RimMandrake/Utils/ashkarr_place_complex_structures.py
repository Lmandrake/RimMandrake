#!/usr/bin/env python3
"""
ashkarr_place_complex_structures.py — put the RUT_ComplexStructures landmark on
every tile that has actually earned it.

Owner, 2026-09-07: he wanted a marker that "clearly identified 'complex structures'
... indicating a particularly complicated and dense network on the map (as there are
in many, many places here)", and chose the >=6 threshold.

THE RULE. A tile qualifies when it carries >= THRESHOLD tile mutators AND its biome
is not in BIOME_DENYLIST. Owner ruling 2026-09-08 ("bad idea here", the Fever Wood
screenshot vs "they look great in the Rust Cathedral"): the wet-green biomes' density
is BIOLOGICAL — megahives, locust country — and an icon that says "built structures"
is the wrong word for it there. 59 icons were removed from those biomes at V27;
the denylist keeps a re-run from putting them back.
The icon is therefore a READOUT of density that is genuinely present, not decoration
asserting it. Measured 2026-09-07 over all 21,872 tiles:

    0 muts 7730 | 1 7509 | 2 3715 | 3 1542 | 4 687 | 5 428
    6 146 | 7 86 | 8 22 | 9 3 | 10 2 | 11 1 | 12 1

  >=6 -> 261 tiles, the top 1.2% of the planet, 108 of them in the Rust Cathedral.

⚠️ WHY THIS NEEDS A RESTART BEFORE IT WILL RUN. `RUT_ComplexStructures` is a new
LandmarkDef, and RimWorld parses defs only at startup — deploying the XML is not
enough. The script checks the def is actually live and refuses rather than reporting
a success the game never honoured.

⚠️ IT SKIPS TILES THAT ALREADY HAVE A LANDMARK. A tile carries one, and an existing
hand-placed or generated landmark is someone's decision; overwriting it to show a
density readout would be a bad trade.

⚠️ AND IT DIFFS THE WHOLE PLANET'S MUTATORS AFTERWARDS. A landmark's mutatorChances
rolls go through AddMutator and can DISPLACE existing mutators. RUT_ComplexStructures
deliberately declares none, so the loss count must be zero — but "must be" is not
"is", and these are the busiest tiles on the map, so it is checked rather than
assumed.

    python3 ashkarr_place_complex_structures.py            # plan
    python.exe ashkarr_place_complex_structures.py --apply # place (needs the bridge)
"""
import argparse
import collections
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, HERE)

DEF = "RUT_ComplexStructures"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--threshold", type=int, default=6)
    ap.add_argument("--apply", action="store_true")
    a = ap.parse_args()

    from rimbridge_client import RimBridge, resolve_endpoint
    host, port, token = resolve_endpoint()

    with RimBridge(host, port, token) as rb:
        chk = rb.call("jawa/get_defs", {"defs": "LandmarkDef/%s" % DEF})
        live = bool(chk.get("defs") and chk["defs"][0].get("found"))
        if not live:
            print("REFUSED: LandmarkDef/%s is not loaded in the running game.\n"
                  "  The XML is deployed but RimWorld parses defs only at startup.\n"
                  "  Restart the game, then re-run." % DEF)
            return 1

        r = rb.call("jawa/world_mutators_get", {"range": "0-21871", "limit": 22000})
        rows = r.get("tiles") or r.get("rows") or []
        before = {x["tile"]: sorted(d["def"] for d in x["mutators"]) for x in rows}

        lm = rb.call("jawa/world_landmarks_get", {"limit": 5000})
        taken = {l["tile"] for l in (lm.get("landmarks") or lm.get("rows") or [])}

        # Owner ruling 2026-09-08: never in the wet-green family — their density is
        # biological, not structural. See module docstring.
        BIOME_DENYLIST = {
            "COMIGO_GreaterSwamp_Tropical",   # the Fever Wood
            "AB_MiasmicMangrove",             # the Miasma
            "BiomeCypreJungle",               # the Greentide
            "AB_OcularForest",                # the Contagion
            "AB_FeraliskInfestedJungle",      # the Webwork
            "ZBiome_Grasslands",              # the Pyrelands
        }
        te = rb.call("jawa/world_tile_export",
                     {"path": r"D:\Luke\dev\Rimworld\Transient\cs_place_tiles.csv"})
        import csv as _csv
        # 🔴 The bridge call above writes on the GAME's (Windows) filesystem, so its
        # path argument stays Windows-style. But this process may be python3 under
        # WSL, where `D:\...\cs_place_tiles.csv` is not openable (no drive letter,
        # backslashes aren't separators) - it must read back via the REPO-relative
        # path in ITS OWN native form.
        local_csv = os.path.join(REPO, "Transient", "cs_place_tiles.csv")
        biome_of = {int(x["tile"]): x["biome"] for x in _csv.DictReader(
            open(local_csv, encoding="utf-8"))}
        dense = sorted(t for t, m in before.items() if len(m) >= a.threshold)
        denied = [t for t in dense if biome_of.get(t) in BIOME_DENYLIST]
        dense = [t for t in dense if biome_of.get(t) not in BIOME_DENYLIST]
        print("  denied by biome (wet-green ruling 2026-09-08): %d" % len(denied))
        plan = [t for t in dense if t not in taken]

        print("COMPLEX STRUCTURES — landmark on tiles carrying >= %d mutators" % a.threshold)
        print("  qualifying tiles: %d" % len(dense))
        print("  already carry another landmark, skipped: %d" % (len(dense) - len(plan)))
        print("  to place: %d" % len(plan))
        hist = collections.Counter(len(before[t]) for t in plan)
        print("  by mutator count: %s" % dict(sorted(hist.items())))

        if not a.apply:
            print("\nPLAN ONLY. --apply to place.")
            return 0

        CH = 200
        for i in range(0, len(plan), CH):
            chunk = plan[i:i + CH]
            res = rb.call("jawa/world_landmarks_set",
                          {"action": "add", "tiles": ",".join(str(x) for x in chunk),
                           "def": DEF})
            print("ADD %3d tiles -> success=%s added=%s"
                  % (len(chunk), res.get("success"), res.get("added")))
        print("COMMIT failedSteps=%s" % rb.call("jawa/world_commit", {}).get("failedSteps"))

        r2 = rb.call("jawa/world_mutators_get", {"range": "0-21871", "limit": 22000})
        after = {x["tile"]: sorted(d["def"] for d in x["mutators"])
                 for x in (r2.get("tiles") or r2.get("rows") or [])}
        lost = collections.Counter()
        for t, b in before.items():
            for d in set(b) - set(after.get(t, [])):
                lost[d] += 1
        print("\nWHOLE-PLANET MUTATOR LOSSES: %s" % (dict(lost) or "NONE"))

        lm2 = rb.call("jawa/world_landmarks_get", {"limit": 5000})
        got = sum(1 for l in (lm2.get("landmarks") or lm2.get("rows") or [])
                  if l["def"] == DEF)
        print("READ BACK: %d tiles now carry %s (wanted %d)" % (got, DEF, len(plan)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
