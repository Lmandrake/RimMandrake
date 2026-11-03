"""selftest_tree_crowns_measured.py -- TREE_CROWN_MEASURE_FROM_THE_ART: crowns measured from the art, never invented.

    python3 src/RimMandrake/Utils/selftest_tree_crowns_measured.py      -> "N/N PASS", exit 0

measure_huge_plant_masks.py --crowns measures crownRadiusFactor / crownHeightFactor for the six day-side giants
(tree shade model sec 4.2 invents 0.8 / 0.5). This pins:
  * measure_crown on synthetic sprites with a known answer: a disc on a pole, a crown over stilt roots WIDER than it
    (the roots must never be read as the crown), a bush with no neck (the whole silhouette is crown), a bare column
    with a small cap (a small radius, not the base flare);
  * the committed tree_crowns_measured.json is CURRENT against a fresh measurement of the art (the tool's --check);
  * it holds exactly the six giants the design names, every variant file exists, every factor is in (0, 1.01], and
    the cells fields are the factors times the full-growth size (r = f x s/2, hc = f x s).
"""
import io
import json
import os
import sys
from contextlib import redirect_stdout

import numpy as np

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "src", "RimMandrake", "HugeThings"))
import measure_huge_plant_masks as M  # noqa: E402

N = M.WORK_PX
results = []


def check(name, ok, detail=""):
    results.append(ok)
    print("%s  %s%s" % ("PASS" if ok else "FAIL", name, ("  -- " + detail) if detail and not ok else ""))


def canvas():
    return np.zeros((N, N), dtype=np.float32)


def rect(a, u0, u1, v0, v1):
    """Fill quad box u in [u0,u1), v in [v0,v1) (v from the bottom)."""
    a[N - int(round(v1 * N)):N - int(round(v0 * N)), int(round(u0 * N)):int(round(u1 * N))] = 1.0


def disc(a, cu, cv, ru, rv):
    yy, xx = np.mgrid[0:N, 0:N]
    u, v = (xx + 0.5) / N, (N - yy - 0.5) / N
    a[((u - cu) / ru) ** 2 + ((v - cv) / rv) ** 2 <= 1.0] = 1.0


def near(x, want, tol=0.02):
    return abs(x - want) <= tol


# 1. a disc on a pole: crown 0.6 wide centred at v 0.75 above ground at v 0.0
a = canvas()
rect(a, 0.47, 0.53, 0.0, 0.62)
disc(a, 0.5, 0.75, 0.3, 0.15)
c = M.measure_crown(a)
check("pole: radius factor = crown width 0.6", near(c["crownRadiusFactor"], 0.6), str(c["crownRadiusFactor"]))
check("pole: height factor = crown centroid 0.75", near(c["crownHeightFactor"], 0.75), str(c["crownHeightFactor"]))
check("pole: crown bottom near the disc's 0.6", near(c["crownBottom"], 0.6, 0.04), str(c["crownBottom"]))
check("pole: neck is distinct", c["neckDistinct"])

# 2. stilt roots wider (0.9) than the crown (0.5), the ground raised to v 0.1
a = canvas()
rect(a, 0.05, 0.95, 0.1, 0.35)   # root arch mass
rect(a, 0.45, 0.55, 0.1, 0.8)    # trunk
disc(a, 0.5, 0.85, 0.25, 0.1)
c = M.measure_crown(a)
check("stilts: wider roots below are never the crown (radius 0.5)", near(c["crownRadiusFactor"], 0.5), str(c["crownRadiusFactor"]))
check("stilts: height measured from the raised ground (0.75)", near(c["crownHeightFactor"], 0.75), str(c["crownHeightFactor"]))

# 3. a bush with no neck: the whole silhouette is crown
a = canvas()
disc(a, 0.5, 0.4, 0.4, 0.4)
c = M.measure_crown(a)
check("bush: no distinct neck", not c["neckDistinct"])
check("bush: radius factor = whole width 0.8", near(c["crownRadiusFactor"], 0.8), str(c["crownRadiusFactor"]))
check("bush: height factor = centroid 0.4", near(c["crownHeightFactor"], 0.4), str(c["crownHeightFactor"]))

# 4. a bare column with a small cap and a wide base flare
a = canvas()
rect(a, 0.45, 0.55, 0.0, 0.95)
rect(a, 0.2, 0.8, 0.0, 0.08)     # flare
rect(a, 0.42, 0.58, 0.95, 0.98)  # cap
c = M.measure_crown(a)
check("column: radius is the cap (0.16), not the flare", near(c["crownRadiusFactor"], 0.16), str(c["crownRadiusFactor"]))

# 4b. the neck threshold: a neck at exactly NECK_DISTINCT x the widest row is no neck
a = canvas()
a[N // 10:N // 2, 100:900] = 1.0                 # 800 px wide upper body
a[N // 2:, 200:800] = 1.0                         # 600 px = exactly 0.75 x 800, the lower body
c = M.measure_crown(a)
check("neck at exactly 0.75 x the widest row: whole silhouette is crown", not c["neckDistinct"] and near(c["crownBottom"], 0.0, 0.01),
      "%s %s" % (c["neckDistinct"], c["crownBottom"]))

# 4c. the patch guard can see: a single-quoted texPath patch is caught, a /plant temperature patch is not
import tempfile  # noqa: E402
with tempfile.TemporaryDirectory() as td:
    bad_p, ok_p = os.path.join(td, "bad.xml"), os.path.join(td, "ok.xml")
    open(bad_p, "w").write("<Patch><Operation Class='PatchOperationReplace'><xpath>/Defs/ThingDef[defName='RM_Veluthar']"
                           "/graphicData</xpath><value><graphicData><texPath>X</texPath></graphicData></value></Operation></Patch>")
    open(ok_p, "w").write('<Patch><Operation Class="PatchOperationAdd"><xpath>/Defs/ThingDef[defName="RM_Nogtyl"]/plant</xpath>'
                          "<value><minGrowthTemperature>5</minGrowthTemperature></value></Operation></Patch>")
    rm_p = os.path.join(td, "rm.xml")
    open(rm_p, "w").write('<Patch><Operation Class="PatchOperationRemove"><xpath>/Defs/ThingDef[defName="RM_Kaddrath"]/plant'
                          "</xpath></Operation></Patch>")
    hits = M.crown_patch_hits([[bad_p, ok_p, rm_p]])
check("patch guard: catches a single-quoted graphic patch and a /plant removal, passes a temperature patch",
      [h[1] for h in hits] == ["RM_Veluthar", "RM_Kaddrath"], str(hits))

# 5. the committed file is current
buf = io.StringIO()
with redirect_stdout(buf):
    rc = M.main(["--crowns", "--check"])
check("tree_crowns_measured.json is CURRENT against the art", rc == 0, buf.getvalue().strip().splitlines()[-1] if buf.getvalue() else "")

# 6. its contents
doc = json.load(open(M.CROWNS_JSON, encoding="utf-8"))
plants = doc.get("plants", {})
check("exactly the six day-side giants", sorted(plants) == sorted(M.CROWN_GIANTS), str(sorted(plants)))
bad = []
for dn, p in plants.items():
    s = p["fullGrowthSize"]
    if not (s == p["drawSizeX"] * p["visualSizeRange"][1]):
        bad.append("%s size" % dn)
    if not p["variants"]:
        bad.append("%s no variants" % dn)
    for v in p["variants"]:
        if not os.path.isfile(os.path.join(ROOT, v["file"])):
            bad.append("%s missing %s" % (dn, v["file"]))
        for k in ("crownRadiusFactor", "crownHeightFactor"):
            if not (0 < v[k] <= 1.01):
                bad.append("%s %s %s" % (dn, v["texture"], k))
    if abs(p["crownRadiusCells"] - p["crownRadiusFactor"] * s / 2) > 1e-3 or abs(p["crownHeightCells"] - p["crownHeightFactor"] * s) > 1e-3:
        bad.append("%s cells" % dn)
check("every giant: variants on disk, factors in (0,1.01], cells = factor x size", not bad, "; ".join(bad))
check("the invented defaults are recorded beside the measurement",
      doc.get("inventedDefaults") == {"crownRadiusFactor": 0.8, "crownHeightFactor": 0.5})

print("%d/%d PASS" % (sum(results), len(results)))
sys.exit(0 if all(results) else 1)
