"""ashkarr_dry_jungle.py - finish the rain ban the owner ruled, on the 363 tiles it skipped.

    python3 src/RimMandrake/Utils/ashkarr_dry_jungle.py            # report only
    python3 src/RimMandrake/Utils/ashkarr_dry_jungle.py --apply    # rewrite rain_mm

⛔ NOT A GENERATOR. One selector, one column, no seed and no knobs. It reads the current
CSV and changes named rows, which is the ONLY sanctioned way to change the planet -
`world/ASHKARR_WORLDMAP_tiles.csv.frozen.json` refuses `ashkarr_paint.py` and explicitly
leaves this family free.

THE DEFECT. `RAIN_BAN_SCOPE_1` offered two readings of the owner's rain ban: (a) zero
`rain_mm` on every tile below `hilliness` 4 with no biome exempted, or (b) the same but
sparing `AB_FeraliskInfestedJungle`. **The edit that ran was (b), and nobody recorded
that a choice had been made** - it reads as if the ban simply applied.

OWNER'S CALL, 2026-08-21: option (a). Measured the same day, 363 tiles still carried
`rain_mm > 0` at `hilliness < 4` and every one of them was `AB_FeraliskInfestedJungle`,
121 of them at the 1668 mm ceiling.

✅ IT REPAINTS NOTHING HE CAN SEE. `rain_mm` is not rendered on the world map, and the
design already holds that the Feralisk jungles are fed by RIVERS, not sky - so drying
them costs the fiction nothing.

⛔ TOUCHES NOTHING AT `hilliness >= 4`. Those 1,396 tiles keep their rain; that is the
ruling, not an oversight, and the report prints the count so a wrong join is visible.
"""
from __future__ import annotations
import argparse
import csv
import collections
import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
TILES = os.path.join(ROOT, "world", "ASHKARR_WORLDMAP_tiles.csv")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--apply", action="store_true",
                    help="write the change (default: report only)")
    a = ap.parse_args()

    with open(TILES, encoding="utf-8", newline="") as fh:
        rd = csv.DictReader(fh)
        cols = rd.fieldnames
        rows = list(rd)

    sel = [r for r in rows if float(r["rain_mm"]) > 0 and int(r["hilliness"]) < 4]
    keep = [r for r in rows if float(r["rain_mm"]) > 0 and int(r["hilliness"]) >= 4]

    print("tiles                      %d" % len(rows))
    print("rain_mm > 0, hilliness < 4 %d   <- to be dried" % len(sel))
    print("  biome                    %s"
          % dict(collections.Counter(r["biome"] for r in sel)))
    print("  hilliness                %s"
          % dict(sorted(collections.Counter(int(r["hilliness"]) for r in sel).items())))
    print("  region                   %s"
          % dict(collections.Counter(r["region"] or "unnamed" for r in sel).most_common()))
    print("rain_mm > 0, hilliness >= 4 %d   <- UNTOUCHED, the ruling keeps these" % len(keep))

    if not a.apply:
        print("\nreport only. Re-run with --apply to write.")
        return 0
    if not sel:
        print("\nnothing to do - the selector already returns 0 rows.")
        return 0

    for r in sel:
        r["rain_mm"] = "0"
    with open(TILES, "w", encoding="utf-8", newline="") as fh:
        wr = csv.DictWriter(fh, fieldnames=cols)
        wr.writeheader()
        wr.writerows(rows)

    after = [r for r in rows if float(r["rain_mm"]) > 0 and int(r["hilliness"]) < 4]
    mx = max(float(r["rain_mm"]) for r in rows)
    print("\nwrote %s" % TILES)
    print("  selector now returns     %d   (must be 0)" % len(after))
    print("  rain_mm > 0, hilliness >= 4 %d   (must be unchanged)" % len(keep))
    print("  max rain_mm now          %g" % mx)
    return 0 if not after else 1


if __name__ == "__main__":
    sys.exit(main())
