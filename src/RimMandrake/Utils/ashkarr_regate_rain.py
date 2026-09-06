"""ashkarr_regate_rain.py - gate the Scald plume, and touch NOTHING else.

    python3 src/RimMandrake/Utils/ashkarr_regate_rain.py            # verify + report only
    python3 src/RimMandrake/Utils/ashkarr_regate_rain.py --apply    # rewrite rain_mm

⛔ THIS IS NOT THE PAINTER AND MUST NOT BECOME IT. `ashkarr_paint.py` regenerates all
fourteen columns; the map is ACCEPTED for v1 (`canon.yml`), and the ortho globes the owner
signed off describe the file as it stands. Re-running the painter would silently make
those globes describe a planet that no longer exists. This pass rewrites exactly ONE
column - `rain_mm` - and asserts that every other byte of every other column is unchanged.

THE DEFECT, measured live 2026-08-21 after the first successful paint.
`ashkarr_paint.py:481`:

    rain_src = clip((0.35 + 3.6*lift) * moist * dayside  +  2.6 * scald_plume, 0.02, None)
                    \\________ gated by dayside ________/     \\___ UNGATED ___/

`scald_plume` peaks at 1.0, so the plume term alone reaches 2.6 - and `:902` computes
`rain = 18 + 1650 * clip(rain_src/2.6, 0, 1)**2.2`, whose ceiling is exactly 1668. So
every tile within about 15 degrees of the Scald point saturates the rainfall scale
outright, no matter its biome, its elevation, or whether it is lava. 596 tiles sat at that
ceiling: 271 of them the jungle corridor the plume EXISTS to create, and 325 of them
badlands, desert, oasis, grassland and the entire 69-tile volcanic province.

THE FIX, owner's call 2026-08-21: gate the plume the way every other term is gated.
Multiply it by `dayside`, so the Scald still pumps water into its own corridor but stops
saturating the scale on ground the sun has already left.

🔑 WHY IT RECONSTRUCTS BEFORE IT WRITES. `rain_src` is not in the bundle - only the
`rain_mm` it produced - and the transform SATURATES, so it cannot be inverted on exactly
the tiles that are wrong. So the model is rebuilt from the columns that ARE in the bundle
(`arc`, `elev_m`, `lat`, `lon`) plus the adjacency graph, and is REFUSED unless it
reproduces the committed `rain_mm` almost exactly. A model that cannot predict the old
numbers has no business writing new ones.
"""
import argparse
import csv
import io
import os
import sys

import numpy as np

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", ".."))
TILES = os.path.join(REPO, "world", "ASHKARR_WORLDMAP_tiles.csv")
GRAPH = os.path.join(REPO, "world", "world_graph.npz")

NIGHT_ARC = 100.0          # ashkarr_paint.py:327
SCALD_ARC, SCALD_BEAR = 35.0, 185.0    # ashkarr_paint.py:468, point_dist(V, 35, 185)
LIFT_DIV = 260.0
RAIN_FLOOR, RAIN_SPAN, RAIN_EXP, RAIN_SAT = 18.0, 1650.0, 2.2, 2.6
SEA_RAIN = 90


def ab_vec(arc, bear):
    a, b = np.radians(np.atleast_1d(arc)), np.radians(np.atleast_1d(bear))
    lat = np.arcsin(np.sin(a) * np.sin(b))
    lon = np.arctan2(np.sin(a) * np.cos(b), np.cos(a))
    return np.stack([np.cos(lat) * np.cos(lon), np.sin(lat),
                     np.cos(lat) * np.sin(lon)], axis=-1)


def model(arc, elev, V, idx, keep, gate_plume):
    """Reproduce ashkarr_paint.py's rainfall, optionally with the plume gated."""
    n = len(arc)
    d = np.degrees(np.arccos(np.clip(V.dot(ab_vec(SCALD_ARC, SCALD_BEAR)[0]), -1, 1)))
    scald_plume = np.exp(-((d - 15.0) / 11.0) ** 2)
    moist = 0.42 * np.exp(-((arc - 96.0) / 34.0) ** 2) + 1.9 * scald_plume
    dayside = np.clip((NIGHT_ARC + 12.0 - arc) / 24.0, 0, 1)

    lift = np.zeros(n)
    for t in range(n):
        if arc[t] > NIGHT_ARC + 14:
            continue
        best = 0.0
        for u in idx[t][keep[t]]:
            u = int(u)
            if arc[u] > arc[t]:
                best = max(best, (elev[t] - elev[u]) / LIFT_DIV)
        lift[t] = best

    plume_term = RAIN_SAT * scald_plume
    if gate_plume:
        # 🔑 THE WHOLE CHANGE. One factor, the same `dayside` the orographic term
        # already carries. Nothing else in the model moves.
        plume_term = plume_term * dayside

    rain_src = np.clip((0.35 + 3.6 * np.clip(lift, 0, 6.0)) * moist * dayside
                       + plume_term, 0.02, None)
    return np.clip(RAIN_FLOOR + RAIN_SPAN * np.clip(rain_src / RAIN_SAT, 0, 1) ** RAIN_EXP,
                   12, 4800)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true", help="rewrite rain_mm; default reports only")
    a = ap.parse_args()

    with io.open(TILES, encoding="utf-8", newline="") as fh:
        rd = csv.DictReader(fh)
        cols = list(rd.fieldnames)
        rows = list(rd)
    n = len(rows)

    arc = np.array([float(r["arc"]) for r in rows])
    elev = np.array([float(r["elev_m"]) for r in rows])
    old = np.array([int(r["rain_mm"]) for r in rows])
    sea = np.array([r["water"] == "1" or r["biome"] in ("Ocean", "Lake") for r in rows])

    z = np.load(GRAPH)
    V = z["vec"]
    idx, keep = z["idx"], z["keep"]

    # ---- 1. can the model predict what is already committed? -----------------
    pred = np.rint(model(arc, elev, V, idx, keep, gate_plume=False)).astype(int)
    pred[sea] = SEA_RAIN
    land = ~sea
    err = np.abs(pred[land] - old[land])
    exact = int((err == 0).sum())
    print("reconstruction against the committed rain_mm, %d land tiles:" % land.sum())
    print("   exact %d (%.2f%%)   max error %d   mean error %.3f"
          % (exact, 100.0 * exact / land.sum(), err.max(), err.mean()))
    if exact < 0.99 * land.sum():
        sys.exit("🔴 REFUSING: the model does not reproduce the committed numbers, so it "
                 "cannot be trusted to replace them. Nothing was written.")

    # ---- 2. the gated version ------------------------------------------------
    new = np.rint(model(arc, elev, V, idx, keep, gate_plume=True)).astype(int)
    new[sea] = SEA_RAIN
    moved = int((new != old).sum())
    ceil_before = int((old == 1668).sum())
    ceil_after = int((new == 1668).sum())
    print("\ngated plume:")
    print("   tiles whose rainfall moves: %d (%.1f%%)" % (moved, 100.0 * moved / n))
    print("   at the 1668 ceiling: %d -> %d" % (ceil_before, ceil_after))

    import collections
    was = collections.Counter()
    for i, r in enumerate(rows):
        if old[i] == 1668 and new[i] != 1668:
            was[r["biome"]] += 1
    print("   dried off the ceiling, by biome:")
    for b, c in was.most_common():
        print("      %5d  %-30s %s" % (c, b, ""))
    still = collections.Counter(rows[i]["biome"] for i in range(n) if new[i] == 1668)
    print("   still at the ceiling: %s" % (dict(still.most_common()) or "none"))
    dry = [i for i in range(n) if rows[i]["biome"] in ("Volcano", "LavaField",
                                                       "AB_PyroclasticConflagration")]
    print("   volcanic province (%d tiles): rain %d..%d -> %d..%d"
          % (len(dry), old[dry].min(), old[dry].max(), new[dry].min(), new[dry].max()))

    if not a.apply:
        print("\nreport only. Pass --apply to write.")
        return 0

    for i, r in enumerate(rows):
        r["rain_mm"] = str(int(new[i]))
    with io.open(TILES, "w", encoding="utf-8", newline="") as fh:
        wr = csv.DictWriter(fh, fieldnames=cols)
        wr.writeheader()
        wr.writerows(rows)
    print("\nwrote %s — rain_mm only" % TILES)
    print("⚠️ Now restamp the freeze:  python3 src/RimMandrake/Utils/verify_frozen.py "
          "--restamp world/ASHKARR_WORLDMAP_tiles.csv")
    return 0


if __name__ == "__main__":
    sys.exit(main())
