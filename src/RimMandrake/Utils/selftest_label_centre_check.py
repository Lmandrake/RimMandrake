"""Selftest: label_centre_check -- angular label-centre gate for the u1/labels70 parity applies.
Offline, < 2 s. Engine values are the real Slough/Knuckles centres from the
ASHKARR_DEV_START_2026-10-20_PARITY_QUIET_R2 save (GetTileCenter, radius ~99.989)."""
import json, math, os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import label_centre_check as LC, worldgeom, feature_drawcenter_audit as A
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
fails = []
def ok(c, m):
    if not c: fails.append(m)

U1 = {f["name"]: f for f in json.load(open(os.path.join(REPO, "world/ASHKARR_PARITY_U1_labels_2026-10-20_plan.json"),
                                          encoding="utf-8"))["features"]}
ENGINE = {"Slough": (2.16574883, 99.8169174, -5.44208193), "Knuckles": (-15.070076, 98.699646, 5.38822174)}
plan = [U1["Slough"], U1["Knuckles"]]
live = {n: {"drawCenter": {"x": v[0], "y": v[1], "z": v[2]}, "maxDrawSizeInTiles": U1[n]["after"]["size"]}
        for n, v in ENGINE.items()}

# 1. the measured spelling difference passes (the old per-axis 0.01 gate refused it)
ok(LC.check_labels(plan, live, "after") == [], "engine GetTileCenter vs plan lat/long spelling must pass")
ok(max(abs(a - b) for a, b in zip(ENGINE["Slough"], U1["Slough"]["after"]["drawCenter"])) > 0.1,
   "fixture no longer shows the per-axis drift it exists to cover")
# 2. the mechanism: LongLatOf's asin(y/100) on a radius-99.989 centre
x, y, z = ENGINE["Slough"]; r = math.sqrt(x * x + y * y + z * z)
ok(abs(math.degrees(math.asin(y / r) - math.asin(y / 100)) - LC.centre_arc_deg(ENGINE["Slough"], U1["Slough"]["after"]["drawCenter"])) < 0.002,
   "Slough's drift is no longer the LongLatOf radius bias")
# 3. a label one tile over fails -- the nearest neighbour of the planned tile
geo = worldgeom.Geometry(21872); t = U1["Slough"]["after"]["centerOnTile"]
nb = min(geo.neighbours(t), key=lambda n: -float(geo.vec[t] @ geo.vec[n]))
moved = dict(live); moved["Slough"] = dict(live["Slough"], drawCenter=[c * 0.99989 for c in A.vec_to_raw(geo.vec[nb])])
ok([b[:2] for b in LC.check_labels(plan, moved, "after")] == [("Slough", "centre")], "neighbour-tile centre must fail")
# 4. a label on another region fails; a wrong size fails; a missing label fails
other = dict(live); other["Knuckles"] = dict(live["Knuckles"], drawCenter=ENGINE["Slough"])
ok([b[:2] for b in LC.check_labels(plan, other, "after")] == [("Knuckles", "centre")], "wrong-region centre must fail")
sized = dict(live); sized["Slough"] = dict(live["Slough"], maxDrawSizeInTiles=99.0)
ok([b[:2] for b in LC.check_labels(plan, sized, "after")] == [("Slough", "size")], "wrong size must fail")
ok([b[:2] for b in LC.check_labels(plan, {"Slough": live["Slough"]}, "after")] == [("Knuckles", "missing live")], "missing must fail")
# 5. the tolerance is still a same-tile test on this planet
ok(LC.CENTRE_TOL_DEG < 0.934 / 2, "CENTRE_TOL_DEG must stay below half the smallest neighbour arc (0.934 deg)")

print("FAIL selftest_label_centre_check %s" % fails if fails else "OK selftest_label_centre_check"); sys.exit(1 if fails else 0)
