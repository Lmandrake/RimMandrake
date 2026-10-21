"""Selftest: parity_fix_plans.py (U2 diff, U4 lay order) and the engine frame in
feature_drawcenter_audit.py. Offline, < 2 s, no save needed."""
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import feature_drawcenter_audit as A  # noqa: E402
import parity_fix_plans as P  # noqa: E402
import worldgeom  # noqa: E402

FAILS = []


def check(cond, msg):
    if not cond:
        FAILS.append(msg)


# --- engine frame ---------------------------------------------------------
# Labels the ENGINE placed on the 2026-10-20 dev world: world_features_import
# sets drawCenter = GetTileCenter(<middle CSV row of the region>). Raw values
# copied from that save; the tile is the region's middle row.
ENGINE_PLACED = [
    ("Pan", 8915, (-60.1358376, 79.4492645, -8.34384823)),
    ("Cratercrown", 11945, (-74.0401917, -15.3778486, -65.4172897)),
    ("Scald", 11942, (-71.5115356, -13.4465094, -68.5791092)),
    ("Fall Line", 11436, (74.0401917, 15.3778486, -65.4172745)),
]
geo = worldgeom.Geometry(21872)
for name, tile, raw in ENGINE_PLACED:
    dot = float(np.dot(A.raw_to_vec(raw), geo.vec[tile]))
    check(dot > 0.99999, "%s: engine-placed drawCenter is not on tile %d (dot %.5f)" % (name, tile, dot))
    # the old reflected frame must NOT pass this (it is what called these labels wrong)
    x, y, z = raw
    old = np.array([x, y, -z]) / np.linalg.norm(raw)
    if name != "Fall Line":
        check(float(np.dot(old, geo.vec[tile])) < 0.99, "%s: old frame unexpectedly agrees" % name)
for t in (0, 777, 21871):
    lon, lat = A.engine_longlat(A.vec_to_raw(geo.vec[t]))
    check(abs(lat - geo.lat[t]) < 0.01 and abs(((lon - geo.lon[t] + 180) % 360) - 180) < 0.01,
          "LongLatOf identity fails on tile %d" % t)
A._selfcheck_transform([], {}, geo)  # raises SystemExit on failure

# --- U4: lay order ---------------------------------------------------------
# a plain chain with a side branch
edges = [(0, 1), (1, 2), (2, 3), (2, 4), (4, 5), (3, 4)]
target = {0: 0, 1: 1, 2: 2, 3: 3, 4: 3, 5: 4}
order, mism = P.river_lay_order(edges, target)
check(not mism, "lay order mismatches %r" % mism)
check(len(order) == len(edges), "every edge must be laid exactly once (%d vs %d)" % (len(order), len(edges)))
check(len(set(tuple(sorted(e)) for e in order)) == len(edges), "an edge was laid twice")
# the canonical-world anomaly shape (tiles 14323/6225): 4 and 5 are BOTH 3 and
# linked, 5 is reached only through 4, so 4->5 must be laid while 4 is still 2
eq_edges = [(0, 1), (1, 2), (2, 4), (1, 4), (4, 5)]
eq_target = {0: 0, 1: 1, 2: 2, 4: 3, 5: 3}
o2, m2 = P.river_lay_order(eq_edges, eq_target)
check(not m2, "lay order mismatches on second graph %r" % m2)
# file order a->b as exported (not mouth-first) flattens the network: the cause
flat = P.simulate_overlay([(1, 0), (2, 1), (3, 2)])
check(max(flat.values()) == 1, "simulate_overlay should show the flattening (got %r)" % dict(flat))
check(P.simulate_overlay([(0, 1), (0, 1), (1, 2)])[2] == 2, "repeat lay must be a no-op")

# --- U2: mutator diff --------------------------------------------------------
dev = [(1, "Coast"), (1, "VEE_LargerRegion"), (2, "RM_SeaCoast"), (3, "River"), (5, "Mountain")]
stamp = [(1, "Coast"), (2, "Coast"), (3, "River"), (4, "Oasis")]
remove, restore, kept, sup = P.mutator_diff(dev, stamp)
check(remove == [(1, "VEE_LargerRegion"), (5, "Mountain")], "remove %r" % remove)
check(kept == [(2, "RM_SeaCoast")], "kept %r" % kept)
check(sup == [(2, "Coast")], "superseded %r" % sup)
check(restore == [(4, "Oasis")], "restore %r" % restore)

if FAILS:
    print("FAIL selftest_parity_fix_plans: %d" % len(FAILS))
    for f in FAILS:
        print("  -", f)
    sys.exit(1)
print("OK selftest_parity_fix_plans")
