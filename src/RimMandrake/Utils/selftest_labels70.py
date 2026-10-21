"""Selftest: label display scale (world_label_curve), labels70 plan, paint_inputs_build size column.
Offline, < 2 s."""
import json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import world_label_curve as C, labels70_plan as L, paint_inputs_build as B
fails = []
def ok(c, m):
    if not c: fails.append(m)
ok(abs(C.effective_draw_size(25) - 40) < 1e-9 and abs(C.effective_draw_size(60) - 100 * 0 - 102) < 1e-6, "curve knots/interp")
ok(C.scaled_max_draw(25, 1.0) == 25 and C.scaled_max_draw(10) == 10 and C.scaled_max_draw(11) == 10, "floor and identity")
ok(abs(C.effective_draw_size(C.scaled_max_draw(40)) - 0.7 * C.effective_draw_size(40)) < 0.05, "40 -> 70% width")
prev = -1
for x in range(10, 200):
    v = C.scaled_max_draw(x); ok(v >= prev, "monotone at %d" % x); prev = v
p = L.build(); fs = p["features"]
ok(len(fs) == 71 and p["counts"]["atFloor"] == len(p["atFloor"]), "plan counts")
ok(all(f["after"]["size"] <= f["before"]["size"] for f in fs), "never grows")
ok(all(f["after"]["effectiveWidthTiles"] >= 15 for f in fs), "never under the floor")
ok(all(abs(f["after"]["effectiveWidthTiles"] - max(15, .7 * f["before"]["effectiveWidthTiles"])) < .1 for f in fs), "70% of width or floor")
rows = [{"name": f["name"], "size": "1"} for f in fs]
B.apply_label_scale(rows, L.U1)
ok(all(float(r["size"]) == f["after"]["size"] for r, f in zip(rows, fs)), "bundle size column == plan")
B.apply_label_scale(rows, L.U1, 1.0)
ok(all(float(r["size"]) == f["before"]["size"] for r, f in zip(rows, fs)), "scale 1.0 = canonical")
print("FAIL selftest_labels70 %s" % fails if fails else "OK selftest_labels70"); sys.exit(1 if fails else 0)
