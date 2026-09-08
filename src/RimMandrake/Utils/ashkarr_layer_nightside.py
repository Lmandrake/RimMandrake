"""ashkarr_layer_nightside.py - the nightside is LAYERS, not pockets, and one biome spanned 82 C.

    python3 src/RimMandrake/Utils/ashkarr_layer_nightside.py            # report only
    python3 src/RimMandrake/Utils/ashkarr_layer_nightside.py --apply    # rewrite the biome column

⛔ NOT A GENERATOR. One column, two thresholds the owner chose, no seed and no knobs.
`world/ASHKARR_WORLDMAP_tiles.csv` is FROZEN; this is the sanctioned surgical route its own
refusal message names, alongside ashkarr_clamp_rain.py and ashkarr_fix_impassable.py.

🔴 THE OWNER'S RULING, 2026-08-23, verbatim:

    "as we go from hot to cold over the terminator, we pass through the mycoid layer, then
     pass into the horror wastes (eliminating any RockyCrags that are still above freezing in
     the process), and only when it becomes truly cold do the horror wastes peter out and go
     into the truly alien methane, ethane, ice as a mineral type regimes. I hadn't intended
     horror wastes to be in the deepest cold."

⚠️ THIS REVERSES A READING, NOT A DECISION. Commit `0ccf44fe` ("HorrorWastes was two places
20C apart; the warm half was never his ruling") DELETED the warm half of HorrorWastes, reading
his 2026-08-22 words - *"HorrorWastes should be on the night-side where the ancient bioweapons
have adapted to the extreme cold"* - as meaning the deepest cold. **The warm half was the real
intent.** HorrorWastes is a BAND in the transition, with the alien chemistry BELOW it.

THE STACK, hot to cold, which is the whole point:

    AB_MycoticJungle / BMT_FungalForest   the mycoid layer, fades out around -31..-39 C
    HorrorWastes                          -55 .. -30 C   <-- this band
    AB_PropaneLakes / BMT_CrystalCaverns  below -55 C, methane/ethane and ice-as-mineral

⭐ IT FIXES A SECOND DEFECT FOR FREE. `AB_RockyCrags` was 3,816 tiles spanning -82.0 to -0.0 C
- the biggest biome on the planet and not a habitat at all, but a band running from deep
nightside to the terminator. Casting it as one creature list put a lizard and a snow-thing on
the same ground. Carving the band out leaves it at **-30 .. -0.0 C**, a coherent place.

THE THRESHOLDS ARE THE OWNER'S, picked from measured tile counts on 2026-08-23:
  * band -55 .. -30 C, chosen because the mycoid layer's own p25 is -31.4 C so the two abut;
  * below -55 C the alien regimes take over ENTIRELY - AB_RockyCrags stops existing there;
  * inside the band the conversion is TOTAL - no crag pockets survive, so it reads as a layer.

THE DEEP-COLD SPLIT is by elevation, and it is a physical story rather than a ratio: liquid
hydrocarbon pools in the BASINS, ice-as-a-mineral sits in the HIGHLANDS. The cut is the 70th
percentile elevation of the affected tiles, which keeps the lakes dominant as they already are.

⚠️ "eliminating any RockyCrags that are still above freezing" needs NO action and never did -
measured 2026-08-23, `AB_RockyCrags` holds **zero** tiles above 0 C; its warm end is -0.0 C.
The clause is already true, so this script does not touch anything above the band.
"""
import argparse
import collections
import csv
import os
import sys

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__)))))
CSV = os.path.join(REPO, "world", "ASHKARR_WORLDMAP_tiles.csv")
SETTLE = os.path.join(REPO, "world", "ASHKARR_WORLDMAP_settlements.csv")

SRC = ("AB_RockyCrags", "HorrorWastes")     # the two the band is carved from
BAND_LO, BAND_HI = -55.0, -30.0             # the owner's thresholds
LAKES, CAVERNS = "AB_PropaneLakes", "BMT_CrystalCaverns"
DEEP_SPLIT_PCT = 0.70                       # basins -> lakes, highlands -> caverns


def plan(rows):
    deep = [r for r in rows if r["biome"] in SRC and float(r["temp_c"]) < BAND_LO]
    ev = sorted(float(r["elev_m"]) for r in deep)
    cut = ev[int(DEEP_SPLIT_PCT * (len(ev) - 1))] if ev else 0.0
    moves = []
    for r in rows:
        if r["biome"] not in SRC:
            continue
        t = float(r["temp_c"])
        if BAND_LO <= t < BAND_HI:
            new = "HorrorWastes"
        elif t < BAND_LO:
            new = LAKES if float(r["elev_m"]) < cut else CAVERNS
        else:
            continue                        # above the band: AB_RockyCrags keeps its warm end
        if new != r["biome"]:
            moves.append((r, new))
    return moves, cut


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    a = ap.parse_args()

    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from verify_frozen import warn_if_stale
    warn_if_stale(CSV)

    rows = list(csv.DictReader(open(CSV, encoding="utf-8")))
    fields = list(rows[0].keys())
    before = collections.Counter(r["biome"] for r in rows)

    # 🔴 SUPERSEDED SINCE THIS SCRIPT WAS WRITTEN (2026-08-23) — refuse rather than
    # write a now-banned biome. Both this script's carve targets have since been
    # dissolved by LATER, more authoritative rulings it cannot see:
    #   - HorrorWastes: fully dissolved into the Blue Desert/ice sheet mosaic
    #     (HORRORWASTES_BIOME_DISSOLVE_1) — 0 rows remain, so it is no longer a
    #     real destination band, just a name this script would recreate from scratch.
    #   - BMT_CrystalCaverns: `the_lantern_deeps.md` hard ban #1, "No worldmap
    #     biome — BMT_CrystalCaverns never holds a surface tile again." Writing it
    #     here as a worldmap biome (line ~77, `CAVERNS`) would directly violate
    #     that ruling.
    # The owner's underlying ruling ("eliminate any RockyCrags still above
    # freezing") may still be genuinely unfulfilled — this script's own docstring
    # premise for that clause (measured 2026-08-23: zero RockyCrags tiles above
    # 0 C) no longer holds after the 2026-09-07 savegame rebase — but fixing THAT
    # needs a mechanism that doesn't resurrect either dead target, not a blind
    # re-run of this one. See RAIN_BAN_SCOPE_DRIFTED_1 for the sibling shape of
    # this exact problem in ashkarr_dry_jungle.py.
    if before.get("HorrorWastes", 0) == 0 and before.get(CAVERNS, 0) == 0:
        if a.apply:
            print("🔴 REFUSED: HorrorWastes and %s both hold 0 tiles today - both carve "
                  "targets are superseded by later rulings (HORRORWASTES_BIOME_DISSOLVE_1; "
                  "the_lantern_deeps.md hard ban #1 forbids %s as a worldmap biome at all). "
                  "This script cannot --apply without writing a banned biome. See "
                  "ASHKARR_NIGHTSIDE_LAYER_SUPERSEDED_1." % (CAVERNS, CAVERNS),
                  file=sys.stderr)
            return 1
        print("⚠️  HorrorWastes and %s both hold 0 tiles - this script's carve targets are "
              "superseded (see ASHKARR_NIGHTSIDE_LAYER_SUPERSEDED_1). Report below is "
              "informational only; --apply is refused.\n" % CAVERNS)

    moves, cut = plan(rows)

    if not moves:
        print("nothing to do - the nightside is already layered.")
        return 0

    tally = collections.Counter((r["biome"], new) for r, new in moves)
    print("elevation cut for the deep-cold split: %.0f m" % cut)
    for (old, new), n in sorted(tally.items(), key=lambda kv: -kv[1]):
        print("  %5d  %s -> %s" % (n, old, new))

    # ⚠️ a settlement sited on ground that just changed biome is worth SEEING, not guessing at
    moved_tiles = {r["tile"] for r, _ in moves}
    if os.path.exists(SETTLE):
        hit = [s for s in csv.DictReader(open(SETTLE, encoding="utf-8"))
               if s.get("tile") in moved_tiles]
        print("\nsettlements on reassigned ground: %d%s"
              % (len(hit), "" if not hit else "   <-- LOOK AT THESE"))
        for s in hit[:12]:
            print("   %-28s tile %s" % (s.get("name", "?"), s.get("tile")))

    if not a.apply:
        print("\n(report only - pass --apply to write)")
        return 0

    for r, new in moves:
        r["biome"] = new
    w = csv.DictWriter(open(CSV, "w", newline="", encoding="utf-8"), fieldnames=fields)
    w.writeheader()
    w.writerows(rows)
    after = collections.Counter(r["biome"] for r in rows)

    print("\nthe cold stack now, hot to cold:")
    for b in ("AB_MycoticJungle", "BMT_FungalForest", "AB_RockyCrags", "HorrorWastes",
              "IceSheet", LAKES, CAVERNS):
        v = sorted(float(r["temp_c"]) for r in rows if r["biome"] == b)
        if not v:
            continue
        print("  %-22s %5d -> %5d   %7.1f .. %7.1f C   med %6.1f"
              % (b, before[b], after[b], v[0], v[-1], v[len(v) // 2]))
    print("\nwrote %s" % CSV)
    print("⚠️ Now restamp the freeze:  python3 src/RimMandrake/Utils/verify_frozen.py "
          "--restamp world/ASHKARR_WORLDMAP_tiles.csv")
    print("now LOOK at it:  python3 src/RimMandrake/Utils/worldview.py "
          "world/ASHKARR_WORLDMAP --png")
    return 0


if __name__ == "__main__":
    sys.exit(main())
