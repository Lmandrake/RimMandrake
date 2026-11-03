#!/usr/bin/env python3
"""FAUNA_TOLERANCE_NORMALIZATION_1: Laws 3, 5 and 6 hold over the whole roster, and the record regenerates.

1. fauna_normalization.check is CLEAN: the manifest and the three FaunaNorm_* patches are
   byte-identical to a regeneration from the committed snapshot, and on simulated post-patch
   values every measured rostered animal's comfy band covers its envelope +/-15 C (Law 5), every
   best hit sits in 12-15 x bodySize or at its ruled divergence (Law 3), and every product base
   follows bodySize (Law 6).
2. The instrument can see: the biome join resolves an RM_ twin through a renamed painted def
   (RM_Wastes -> record RUT_Wasteland, by tile count), reads the Lantern Deeps' fixed pocket
   temperature, refuses an unknown biome, and the
   snapshot is full-size; planted faults on each law are caught.
3. Widening only: no Law 5 manifest row narrows a band; every Law 5 Replace sits behind a
   numeric xpath guard.
4. Every divergence-manifest animal on the roster lands on its ruled best.
"""
import copy
import os
import re
import sys
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import fauna_normalization as fn  # noqa: E402


def main():
    fails = []
    animals = fn.build_all()
    bad, notes = fn.lint(animals)
    fails += ["lint: " + b for b in bad]
    for path, text in fn.outputs(animals).items():
        cur = open(path, encoding="utf-8").read() if os.path.exists(path) else None
        if cur != text:
            fails.append("stale: %s differs from a regeneration" % os.path.relpath(path, fn.ROOT))

    env = fn.envelopes()
    w = env("RM_Wastes")
    if not w or w[2] != "RUT_Wasteland":
        fails.append("biome join: RM_Wastes resolved to %r, expected the record's RUT_Wasteland" % (w,))
    ld = env("RM_LanternDeeps")
    if not ld or ld[2] != "constantOutdoorTemperature":
        fails.append("biome join: RM_LanternDeeps (a 17 C pocket) resolved to %r" % (ld,))
    if env("RM_NoSuchBiome") is not None:
        fails.append("biome join: an unknown biome got an envelope")
    if len(fn.arch_twins()) < 20:
        fails.append("architecture table yielded only %d RM_ twins" % len(fn.arch_twins()))

    by = {a["defName"]: a for a in animals}
    measured = [a for a in animals if "need" in a]
    if measured:
        a = copy.deepcopy(measured[0])
        a["comfy_post"]["ComfyTemperatureMin"] = a["need"][0] + 5
        if not any(b.startswith("Law5") for b in fn.lint([a] * 400)[0]):
            fails.append("planted fault not caught: narrow Law 5 band")
    armed = [a for a in animals if a["best_post"] > 0 and a["defName"] not in fn.divergences()]
    if armed:
        a = copy.deepcopy(armed[0])
        a["best_post"] = fn.K_HI * a["bs"] * 2 + 5
        if not any(b.startswith("Law3") for b in fn.lint([a] * 400)[0]):
            fails.append("planted fault not caught: out-of-band Law 3 hit")
        a = copy.deepcopy(armed[0])
        a["leather_post"] = 55.0
        if not any(b.startswith("Law6") for b in fn.lint([a] * 400)[0]):
            fails.append("planted fault not caught: Law 6 leather off base")

    for r in fn.load_csv(fn.MANIFEST):
        if r["law"] != "5":
            continue
        old, new = float(r["old"]), float(r["new"])
        if (r["field"].endswith("Min") and new > old) or (r["field"].endswith("Max") and new < old):
            fails.append("Law 5 row narrows: %s %s %s -> %s" % (r["defName"], r["field"], r["old"], r["new"]))
    tree = ET.parse(fn.PATCH_LAW5)
    reps = [op for op in tree.iter() if op.get("Class") == "PatchOperationReplace"]
    unguarded = [op.findtext("xpath") for op in reps if not re.search(r"\[number\(\.\) [<>] -?[\d.]+\]$", op.findtext("xpath") or "")]
    if not reps:
        fails.append("Law 5 patch has no Replace operations")
    if unguarded:
        fails.append("Law 5 Replace without a widen-only guard: %s" % unguarded[:3])
    for p in (fn.PATCH_LAW3, fn.PATCH_LAW6):
        if len(ET.parse(p).getroot()) < 10:
            fails.append("%s holds fewer than 10 operations" % os.path.basename(p))

    hit = 0
    for dn, d in fn.divergences().items():
        a = by.get(dn)
        if not a or a.get("law3_owner"):
            continue
        hit += 1
        want = float(d["ruled_best"]) if abs(float(d["bodySize"]) - a["bs"]) < 1e-6 else max(1.0, round(float(d["K_ruled"]) * a["bs"], 1))
        if abs(a["best_post"] - want) > 0.05:
            fails.append("divergence %s: best %s, ruled %s" % (dn, a["best_post"], want))
    if hit < 25:
        fails.append("only %d divergence animals found on the roster (expected 28)" % hit)

    for n in notes:
        print("note:", n)
    for f in fails:
        print("FAIL", f)
    if fails:
        return 1
    print("PASS: %d rostered animals (+%d off-roster divergences); Laws 3/5/6 hold post-patch; outputs "
          "regenerate byte-identical; %d divergences at ruled values; 3 planted faults caught"
          % (sum(a["rostered"] for a in animals), sum(not a["rostered"] for a in animals), hit))
    return 0


if __name__ == "__main__":
    sys.exit(main())
