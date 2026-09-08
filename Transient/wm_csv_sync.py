"""Surgical edit of world/ASHKARR_WORLDMAP_tiles.csv to match the live planet
after the two vanilla-water rulings (owner, 2026-09-07).

  262 SeaIce -> RUT_TwilightSea (171) / RUT_GreySea (91)   [biome only]
   10 Lake   -> AB_TarPits (5) / ZBiome_Badlands (5)       [biome, elev_m, water]

Only these columns on these rows move. Everything else is written back byte-for-byte
from the original. Run with --apply to write; default is a dry diff.
"""
import sys, csv, io, os, shutil

SRC = "/mnt/d/Luke/dev/Rimworld/world/ASHKARR_WORLDMAP_tiles.csv"
LIVE = "/mnt/d/Luke/dev/Rimworld/Transient/live_after.csv"
apply = "--apply" in sys.argv

live = {r["tile"]: r for r in csv.DictReader(open(LIVE))}

raw = open(SRC, newline="").read()
rdr = csv.DictReader(io.StringIO(raw))
fields = rdr.fieldnames
rows = list(rdr)

changed = {"biome": 0, "elev_m": 0, "water": 0}
touched = set()
for r in rows:
    l = live[r["tile"]]
    if r["biome"] != l["biome"]:
        r["biome"] = l["biome"]
        changed["biome"] += 1
        touched.add(r["tile"])
    le = float(l["elevation"])
    if abs(float(r["elev_m"]) - le) > 0.5:
        r["elev_m"] = str(int(round(le)))
        changed["elev_m"] += 1
        touched.add(r["tile"])
    # keep the bookkeeping water flag consistent with the engine's own test
    want = "1" if le <= 0 else "0"
    if r["tile"] in touched and r["water"] != want:
        r["water"] = want
        changed["water"] += 1

print("rows touched: %d" % len(touched))
print("cells changed: %s" % changed)

if not apply:
    print("\nDRY RUN. Re-run with --apply to write.")
    sys.exit(0)

bak = SRC + ".bak-seaice-lake-20260907"
shutil.copy2(SRC, bak)
buf = io.StringIO()
w = csv.DictWriter(buf, fieldnames=fields, lineterminator="\n")
w.writeheader()
w.writerows(rows)
open(SRC, "w", newline="").write(buf.getvalue())
print("\nwrote %s  (backup: %s)" % (SRC, bak))
print("NOW RUN: python3 src/RimMandrake/Utils/verify_frozen.py --restamp")
