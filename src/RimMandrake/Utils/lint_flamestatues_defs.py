#!/usr/bin/env python3
"""Offline lint of FlameStatues (mandrake.rm.flamestatues): defs vs C# via lint_mod_defs.py, plus the data checks the generic lint
cannot see because the flames are a list of offsets inside one comp:

  fs-points       every statue def carries RM_CompProperties_FlamePoints with the spec's number of vents (ember 1, dancer 3,
                  colossus 5), each size > 0 and each offset inside the drawn sprite (|x|,|z| <= drawSize/2 + 0.25, PROVISIONAL)
  fs-ticker       the statue (or its abstract parent) ticks Normal and draws MapMeshAndRealTime, or the flames never draw / burn
  fs-fuel         Refuelable: chemfuel only, rate > 0, capacity > 0, initial target <= capacity, 0 < autoRefuel <= 1;
                  Glower: radius > 0, colour channels within 0..255
  fs-ladder       statues escalate: points, fuel rate, fuel capacity and glow radius strictly increase ember < dancer < colossus
  fs-phase        for every shipped fleck interval x every quality scale, the vents' fleck phases (i * 37 mod interval) are distinct
                  (otherwise a statue puffs in unison, which the phase offset exists to prevent)
  fs-slider       the settings slider range equals the kernel's multiplier clamp, and the default multiplier is 1
  fs-kernel-pure  Kernel/*.cs names no Verse / RimWorld / UnityEngine / HarmonyLib

    python3 src/RimMandrake/Utils/lint_flamestatues_defs.py [--quiet] [--mod-dir D]
"""
import glob
import os
import re
import sys
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import lint_mod_defs  # noqa: E402

REPO = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
SPEC_POINTS = {"RM_FlameStatue_Ember": 1, "RM_FlameStatue_Dancer": 3, "RM_FlameStatue_Colossus": 5}
LADDER = ["RM_FlameStatue_Ember", "RM_FlameStatue_Dancer", "RM_FlameStatue_Colossus"]
FLAME_CLASS = "RimMandrake.FlameStatues.RM_CompProperties_FlamePoints"
QUALITY_SCALES = [0.5, 0.7, 1.0, 1.2, 1.4, 1.7, 2.0]


def vec(text, n):
    nums = [float(x) for x in re.findall(r"-?\d+(?:\.\d+)?", text or "")]
    return nums if len(nums) == n else None


def main(argv):
    rc = lint_mod_defs.run("FlameStatues", argv)
    if rc == 2:
        return 2
    mod = os.path.join(REPO, "src", "RimMandrake", "FlameStatues")
    if "--mod-dir" in argv:
        mod = argv[argv.index("--mod-dir") + 1]
    errs = []
    E = lambda c, m: errs.append("ERROR %s: %s" % (c, m))
    named, defs = {}, {}
    for p in glob.glob(os.path.join(mod, "Defs", "**", "*.xml"), recursive=True):
        for d in ET.parse(p).getroot().iter("ThingDef"):
            if d.get("Name"):
                named[d.get("Name")] = d
            if d.findtext("defName"):
                defs[d.findtext("defName")] = d

    def inherited(d, tag):
        for _ in range(4):
            v = d.findtext(tag)
            if v is not None:
                return v.strip()
            d = named.get(d.get("ParentName"))
            if d is None:
                return None
        return None

    for need in SPEC_POINTS:
        if need not in defs:
            E("fs-points", "statue def %s is missing" % need)
    ladder = {}
    intervals = set()
    for name, d in sorted(defs.items()):
        sz = vec(d.findtext("graphicData/drawSize"), 2) or [1, 1]
        flame = next((li for li in d.findall("comps/li") if li.get("Class") == FLAME_CLASS), None)
        if flame is None:
            E("fs-points", "%s has no %s" % (name, FLAME_CLASS))
            continue
        pts = flame.findall("points/li")
        if name in SPEC_POINTS and len(pts) != SPEC_POINTS[name]:
            E("fs-points", "%s has %d flame points, the spec says %d" % (name, len(pts), SPEC_POINTS[name]))
        for i, pt in enumerate(pts):
            off = vec(pt.findtext("offset"), 3)
            size = float(pt.findtext("size") or "0.4")
            if size <= 0:
                E("fs-points", "%s point %d has size %s" % (name, i, size))
            if off is None:
                E("fs-points", "%s point %d has no (x,y,z) offset" % (name, i))
            elif abs(off[0]) > sz[0] / 2 + 0.25 or abs(off[2]) > sz[1] / 2 + 0.25:
                E("fs-points", "%s point %d offset %s lies outside the %sx%s sprite" % (name, i, off, sz[0], sz[1]))
        iv = flame.findtext("fireGlowFleckIntervalTicks")
        intervals.add(int(iv) if iv else 90)
        if inherited(d, "tickerType") != "Normal":
            E("fs-ticker", "%s does not tick Normal (flecks and the free-burn refill live in CompTick)" % name)
        if inherited(d, "drawerType") != "MapMeshAndRealTime":
            E("fs-ticker", "%s drawerType is %s, not MapMeshAndRealTime (comp PostDraw, the flames, would never run)" % (name, inherited(d, "drawerType")))
        ref = next((li for li in d.findall("comps/li") if li.get("Class") == "CompProperties_Refuelable"), None)
        glow = next((li for li in d.findall("comps/li") if li.get("Class") == "CompProperties_Glower"), None)
        rate = cap = radius = None
        if ref is None:
            E("fs-fuel", "%s has no CompProperties_Refuelable" % name)
        else:
            rate = float(ref.findtext("fuelConsumptionRate") or 0)
            cap = float(ref.findtext("fuelCapacity") or 0)
            tgt = float(ref.findtext("initialConfigurableTargetFuelLevel") or cap)
            auto = float(ref.findtext("autoRefuelPercent") or 0.3)
            filt = [li.text.strip() for li in ref.findall("fuelFilter/thingDefs/li") if li.text]
            if filt != ["Chemfuel"]:
                E("fs-fuel", "%s fuel filter is %s, the ruling is chemfuel only (R4)" % (name, filt))
            if rate <= 0 or cap <= 0:
                E("fs-fuel", "%s fuel rate %s / capacity %s must be positive" % (name, rate, cap))
            if tgt > cap:
                E("fs-fuel", "%s initial fuel target %s exceeds capacity %s" % (name, tgt, cap))
            if not (0 < auto <= 1):
                E("fs-fuel", "%s autoRefuelPercent %s outside (0,1]" % (name, auto))
        if glow is None:
            E("fs-fuel", "%s has no CompProperties_Glower (the lit room)" % name)
        else:
            radius = float(glow.findtext("glowRadius") or 0)
            col = vec(glow.findtext("glowColor"), 4) or vec(glow.findtext("glowColor"), 3)
            if radius <= 0:
                E("fs-fuel", "%s glowRadius %s" % (name, radius))
            if col is None or any(c < 0 or c > 255 for c in col):
                E("fs-fuel", "%s glowColor %s is not 3-4 channels within 0..255" % (name, glow.findtext("glowColor")))
        ladder[name] = (len(pts), rate, cap, radius)
    present = [n for n in LADDER if n in ladder and None not in ladder[n]]
    for a, b in zip(present, present[1:]):
        for label, ia in (("points", 0), ("fuel rate", 1), ("fuel capacity", 2), ("glow radius", 3)):
            if not ladder[a][ia] < ladder[b][ia]:
                E("fs-ladder", "%s %s (%s) is not below %s (%s)" % (a, label, ladder[a][ia], b, ladder[b][ia]))
    # fs-phase: distinct fleck phases per statue for every shipped interval and quality
    for name, d in defs.items():
        flame = next((li for li in d.findall("comps/li") if li.get("Class") == FLAME_CLASS), None)
        if flame is None:
            continue
        n = len(flame.findall("points/li"))
        base = int(flame.findtext("fireGlowFleckIntervalTicks") or 90)
        if base <= 0:
            continue
        for q in QUALITY_SCALES:
            iv = max(10, int(round(base / q)))
            ph = [(i * 37) % iv for i in range(n)]
            if len(set(ph)) != n:
                E("fs-phase", "%s at quality scale %s (fleck interval %d) has vents puffing in unison: phases %s" % (name, q, iv, ph))
    # fs-slider / fs-kernel-pure
    try:
        mod_cs = open(os.path.join(mod, "Source", "FlameStatuesMod.cs"), encoding="utf-8-sig").read()
        kern = open(os.path.join(mod, "Source", "Kernel", "RM_FlameKernel.cs"), encoding="utf-8-sig").read()
    except OSError as e:
        E("fs-slider", "cannot read the mod or kernel source: %s" % e)
        mod_cs = kern = ""
    sl = re.search(r"list\.Slider\(consumptionMultiplier, ([\d.]+)f, ([\d.]+)f\)", mod_cs)
    kmin = re.search(r"MinFuelMultiplier = ([\d.]+)f", kern)
    kmax = re.search(r"MaxFuelMultiplier = ([\d.]+)f", kern)
    if not (sl and kmin and kmax):
        E("fs-slider", "could not find the settings slider or the kernel clamp constants")
    else:
        if (float(sl.group(1)), float(sl.group(2))) != (float(kmin.group(1)), float(kmax.group(1))):
            E("fs-slider", "slider range %s..%s differs from the kernel clamp %s..%s (a slider value would be silently clamped at startup)" %
              (sl.group(1), sl.group(2), kmin.group(1), kmax.group(1)))
    if not re.search(r"public static float consumptionMultiplier = 1f;", mod_cs):
        E("fs-slider", "the fuel-use multiplier default is not 1")
    for lineno, line in enumerate(kern.splitlines(), 1):
        if re.match(r"\s*using\s+(Verse|RimWorld|UnityEngine|HarmonyLib)\b", line):
            E("fs-kernel-pure", "Kernel/RM_FlameKernel.cs:%d `%s`" % (lineno, line.strip()))
    print("flamestatues data: %d statue defs, %d fleck interval(s) %s x %d quality scales" % (len(defs), len(intervals), sorted(intervals), len(QUALITY_SCALES)))
    for e in errs:
        print(e)
    return 1 if (errs or rc) else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
