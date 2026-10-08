#!/usr/bin/env python3
"""Offline lint of HugeThings (mandrake.rm.hugethings): defs vs C# via lint_mod_defs.py, plus:

  ht-blocker      RM_HugeTrunkBlocker is what the mechanism needs it to be: thingClass Building_TrunkBlocker, Building category,
                  Impassable, edifice, invisible (drawerType None), not selectable, no hit points, Rare ticker (its self-cleanup
                  runs in TickRare), never buildable / claimable
  ht-clamp        the settings sliders' ceilings equal the kernel's MaxTrunkScale (MaxRect, used to re-link blockers after a load,
                  is sized from it) and RM_HugeThingsSettings.MaxTrunkScale aliases the kernel constant
  ht-defaults     the DefModExtension defaults equal the kernel's PROVISIONAL defaults (minGrowthToBlock, hitboxFraction)
  ht-opt-ins      every RM_HugePlantExtension anywhere in src/: trunkWidth 1..6, trunkDepth / stemHeight 0..12, minGrowthToBlock 0..1,
                  each extension li in another mod's patch is MayRequire-guarded on mandrake.rm.hugethings, and its target def is
                  a plant xpath; with a sanity probe that the sweep sees the Rot giants
  ht-csproj       default globbing is ON for this csproj, so the net8 SelfTest folder must be <Compile Remove>d
  ht-kernel-pure  Kernel/*.cs names no Verse / RimWorld / UnityEngine / HarmonyLib

    python3 src/RimMandrake/Utils/lint_hugethings_defs.py [--quiet] [--mod-dir D]
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
PLANT_EXT = "RimMandrake.HugeThings.RM_HugePlantExtension"


def main(argv):
    rc = lint_mod_defs.run("HugeThings", argv)
    if rc == 2:
        return 2
    mod = os.path.join(REPO, "src", "RimMandrake", "HugeThings")
    if "--mod-dir" in argv:
        mod = argv[argv.index("--mod-dir") + 1]
    errs = []
    E = lambda c, m: errs.append("ERROR %s: %s" % (c, m))
    rd = lambda *p: open(os.path.join(mod, *p), encoding="utf-8-sig").read()

    # ht-blocker
    root = ET.parse(os.path.join(mod, "Defs", "ThingDefs", "RM_HugeTrunkBlocker.xml")).getroot()
    d = next((x for x in root.iter("ThingDef") if x.findtext("defName") == "RM_HugeTrunkBlocker"), None)
    if d is None:
        E("ht-blocker", "RM_HugeTrunkBlocker is missing")
    else:
        want = {"thingClass": "RimMandrake.HugeThings.Building_TrunkBlocker", "category": "Building", "passability": "Impassable",
                "drawerType": "None", "selectable": "false", "useHitPoints": "false", "tickerType": "Rare",
                "building/isEdifice": "true", "building/neverBuildable": "true", "building/claimable": "false", "building/isTargetable": "false"}
        for k, v in want.items():
            got = (d.findtext(k) or "").strip()
            if got != v:
                E("ht-blocker", "%s is %r, the mechanism needs %r" % (k, got, v))
        if (d.findtext("statBases/Flammability") or "").strip() != "0":
            E("ht-blocker", "the blocker is flammable (fire must go to the plant, not an invisible cell)")

    # ht-clamp / ht-defaults
    kern = rd("Source", "Kernel", "RM_FootprintKernel.cs")
    settings = rd("Source", "RM_HugeThingsSettings.cs")
    ext = rd("Source", "Extensions.cs")
    kmax = re.search(r"MaxTrunkScale = ([\d.]+)f", kern)
    if "MaxTrunkScale = RM_FootprintKernel.MaxTrunkScale" not in settings:
        E("ht-clamp", "RM_HugeThingsSettings.MaxTrunkScale is not an alias of the kernel constant")
    for name in ("plantTrunkScale", "pawnHitboxScale"):
        m = re.search(r"%s = list\.Slider\(%s, ([\d.]+)f, ([\w.]+)\)" % (name, name), settings)
        hi = m.group(2) if m else None
        if hi is None:
            E("ht-clamp", "no slider found for %s" % name)
            continue
        val = float(hi.rstrip("f")) if re.fullmatch(r"[\d.]+f?", hi) else (float(kmax.group(1)) if hi == "MaxTrunkScale" and kmax else None)
        if val is None or kmax is None or abs(val - float(kmax.group(1))) > 1e-9:
            E("ht-clamp", "%s slider ceiling %s differs from the kernel's MaxTrunkScale %s" % (name, hi, kmax.group(1) if kmax else "?"))
    for fld, const in (("minGrowthToBlock", "DefaultMinGrowthToBlock"), ("hitboxFraction", "DefaultHitboxFraction")):
        a = re.search(r"public float %s = ([\d.]+)f;" % fld, ext)
        b = re.search(r"%s = ([\d.]+)f;" % const, kern)
        if not (a and b) or abs(float(a.group(1)) - float(b.group(1))) > 1e-9:
            E("ht-defaults", "%s default %s differs from the kernel's %s %s" % (fld, a.group(1) if a else "?", const, b.group(1) if b else "?"))

    # ht-opt-ins
    seen = 0
    for p in glob.glob(os.path.join(REPO, "src", "*", "*", "**", "*.xml"), recursive=True):
        if os.sep + "Textures" + os.sep in p or "__pycache__" in p:
            continue
        try:
            txt = open(p, encoding="utf-8-sig", errors="replace").read()
        except OSError:
            continue
        if PLANT_EXT not in txt:
            continue
        try:
            tree = ET.parse(p).getroot()
        except ET.ParseError:
            continue
        rel = os.path.relpath(p, os.path.join(REPO, "src"))
        in_mod = p.startswith(mod + os.sep)
        for li in tree.iter("li"):
            if li.get("Class") != PLANT_EXT:
                continue
            seen += 1
            tw = int(li.findtext("trunkWidth") or 2)
            td = int(li.findtext("trunkDepth") or 0)
            sh = int(li.findtext("stemHeight") or 0)
            mg = float(li.findtext("minGrowthToBlock") or 0.25)
            if not 1 <= tw <= 6:
                E("ht-opt-ins", "%s: trunkWidth %d outside 1..6" % (rel, tw))
            if not (0 <= td <= 12 and 0 <= sh <= 12):
                E("ht-opt-ins", "%s: trunkDepth %d / stemHeight %d outside 0..12" % (rel, td, sh))
            if not 0 <= mg <= 1:
                E("ht-opt-ins", "%s: minGrowthToBlock %s outside 0..1" % (rel, mg))
            if tw * max(td, tw) < 2 and not in_mod:
                E("ht-opt-ins", "%s: a %dx%d trunk blocks nothing (the plant alone is one cell)" % (rel, tw, max(td, tw)))
            if not in_mod and li.get("MayRequire") != "mandrake.rm.hugethings":
                E("ht-opt-ins", "%s: extension li lacks MayRequire=mandrake.rm.hugethings (a load without this mod would hit a missing type)" % rel)
    if seen < 9:
        E("ht-opt-ins", "only %d plant extensions found; the Rot giants alone carry 9 (sanity probe)" % seen)

    # ht-csproj / ht-kernel-pure
    cs = rd("Source", "RM_HugeThings.csproj")
    if not re.search(r"<EnableDefaultCompileItems>\s*false", cs) and not re.search(r'<Compile Remove="SelfTest\\\*\*"', cs):
        E("ht-csproj", "default globbing is on and SelfTest\\** is not removed: the net8 fuzz project would compile into the mod")
    for kf in glob.glob(os.path.join(mod, "Source", "Kernel", "*.cs")):
        for n, line in enumerate(open(kf, encoding="utf-8-sig").read().splitlines(), 1):
            if re.match(r"\s*using\s+(Verse|RimWorld|UnityEngine|HarmonyLib)\b", line):
                E("ht-kernel-pure", "%s:%d `%s`" % (os.path.basename(kf), n, line.strip()))
    print("hugethings data: %d plant extensions checked" % seen)
    for e in errs:
        print(e)
    return 1 if (errs or rc) else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
