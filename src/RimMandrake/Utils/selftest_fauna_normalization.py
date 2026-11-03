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
5. The RULED numbers are pinned as literals here, never read back from the generator
   (owner 2026-09-11: Law 5 +15 C both sides; Law 3 K 12-15 x bodySize; Law 6 meat 140 /
   leather 40 bases): the constants equal the ruling, and the committed Law 5 / Law 6 patches,
   parsed independently and applied over each animal's pre-patch value, meet the literal bands.
   A mutant that regenerates with a different MARGIN, K or base goes red here, because lint and
   the byte-identity check share the generator's constants and cannot see it.
"""
import copy
import os
import re
import sys
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import fauna_normalization as fn  # noqa: E402

# The ruling, owner 2026-09-11 (item FAUNA_TOLERANCE_NORMALIZATION_1 ## RULED). Literals on purpose.
RULED_MARGIN_C = 15.0
RULED_K_LO, RULED_K_HI = 12.0, 15.0
RULED_MEAT_BASE, RULED_LEATHER_BASE = 140.0, 40.0
TOL = 0.05


def committed_stat_writes(path):
    """{(defName, tag): value} read straight from a committed FaunaNorm patch, no generator code."""
    out = {}
    for op in ET.parse(path).getroot():
        xp = op.findtext("xpath") or ""
        m = re.match(r'^/Defs/ThingDef\[defName="([^"]+)"\]/statBases/(\w+)$', xp)
        if not m:
            continue
        dn, tag = m.groups()
        vals = {float(e.text) for v in op.iter("value") for e in v.iter(tag)}
        if len(vals) != 1:
            raise ValueError("%s: %s %s carries values %r" % (os.path.basename(path), dn, tag, vals))
        out[(dn, tag)] = vals.pop()
    return out


def ruled_checks(animals):
    """Law 5/3/6 against the literal ruling; returns failure strings."""
    fails = []
    for name, got, want in (("MARGIN", fn.MARGIN, RULED_MARGIN_C), ("K_LO", fn.K_LO, RULED_K_LO),
                            ("K_HI", fn.K_HI, RULED_K_HI), ("MEAT_BASE", fn.MEAT_BASE, RULED_MEAT_BASE),
                            ("LEATHER_BASE", fn.LEATHER_BASE, RULED_LEATHER_BASE)):
        if got != want:
            fails.append("ruling: fauna_normalization.%s = %r, the owner ruled %r" % (name, got, want))
    divs = fn.divergences()
    w5 = committed_stat_writes(fn.PATCH_LAW5)
    w6 = committed_stat_writes(fn.PATCH_LAW6)
    n5 = n3 = n6 = 0
    for a in animals:
        if not a["rostered"]:
            continue
        dn, bs = a["defName"], a["bs"]
        lo, hi = a["env"][0], a["env"][1]
        if lo is not None:
            n5 += 1
            pre_mn, pre_mx = a["comfy_pre"]["ComfyTemperatureMin"], a["comfy_pre"]["ComfyTemperatureMax"]
            v = w5.get((dn, "ComfyTemperatureMin"))
            mn = pre_mn if v is None else min(pre_mn, v)      # the patch's guard: replace only when narrower
            v = w5.get((dn, "ComfyTemperatureMax"))
            mx = pre_mx if v is None else max(pre_mx, v)
            if mn > lo - RULED_MARGIN_C or mx < hi + RULED_MARGIN_C:
                fails.append("ruled Law5 %s: committed band %s..%s, envelope %s..%s needs %s..%s"
                             % (dn, mn, mx, lo, hi, lo - RULED_MARGIN_C, hi + RULED_MARGIN_C))
        b = a["best_post"]
        if b > 0 and dn not in divs:
            n3 += 1
            band = (max(1.0, RULED_K_LO * bs), max(1.0, RULED_K_HI * bs))
            if not band[0] - TOL <= b <= band[1] + TOL:
                fails.append("ruled Law3 %s: best %s outside %s..%s x bodySize %s" % (dn, b, RULED_K_LO, RULED_K_HI, bs))
        meat = w6.get((dn, "MeatAmount"), a["meat_post"])
        if meat not in (0, None):
            n6 += 1
            want = round(RULED_MEAT_BASE * bs, 1) if bs > 1 else RULED_MEAT_BASE
            if abs(meat - want) > TOL:
                fails.append("ruled Law6 %s: meat base %s, ruled %s (bodySize %s)" % (dn, meat, want, bs))
        leather = w6.get((dn, "LeatherAmount"), a["leather_post"])
        if leather and abs(leather - RULED_LEATHER_BASE) > TOL:
            fails.append("ruled Law6 %s: leather base %s, ruled %s" % (dn, leather, RULED_LEATHER_BASE))
    for k, v in (("Law 5 patch writes", len(w5)), ("Law 6 patch writes", len(w6)),
                 ("Law 5 animals", n5), ("Law 3 animals", n3), ("Law 6 animals", n6)):
        if v < 100:
            fails.append("ruled checks saw only %d %s: the instrument is blind" % (v, k))
    return fails


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

    fails += ruled_checks(animals)

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
