#!/usr/bin/env python3
"""Offline lint of the NightsideIce mod (defs/patches vs C#): the generic lint (lint_mod_defs.py) plus data checks it cannot see:

  ni-kernel     the kernel is Verse-free, listed in the mod csproj and called by the heat dial, the breach loop / crack and the shivven comp
  ni-settings   every setting's slider range holds its default and the labels that promise a rate do not contradict the measured one
  ni-shivven    the shivven comp's XML knobs (legCells >= 1, searchCellBudget >= 1, intervalTicks >= 1) are sane when set, and the race def names
                the comp and the sand-swim extension the comp reads (without the extension the comp does nothing at all)
  ni-crack      RM_BreachCrack carries the crack building class, is attackable (has health) and is not blocking pathing (a crack is open ice)
  ni-names      the pawn kind / sound / thing the code looks up by name exist (RM_Shivven, RM_BreachCrack, RM_ShivvenBreach)
  ni-text       settings text must not promise "one a day" (measured: ~71 h per breach at a full dial because of the two-day cooldown)

    python3 src/RimMandrake/Utils/lint_nightsideice_defs.py [--mod-dir <dir>] [--quiet]
"""
import contextlib
import glob
import io
import os
import re
import sys
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import lint_mod_defs  # noqa: E402

REPO = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))


def rd(p):
    return open(p, encoding="utf-8-sig", errors="replace").read()


def extras(mod):
    errs = []
    E = lambda k, m: errs.append("ERROR ni-%s: %s" % (k, m))
    src = os.path.join(mod, "Source")
    cs = {os.path.basename(p): rd(p) for p in glob.glob(os.path.join(src, "*.cs"))}
    nocom = {k: re.sub(r"//[^\n]*", "", v) for k, v in cs.items()}
    kern_path = os.path.join(src, "Kernel", "RM_NightsideIceKernel.cs")
    kern = re.sub(r"//[^\n]*", "", rd(kern_path)) if os.path.isfile(kern_path) else None
    if kern is None:
        E("kernel", "Kernel/RM_NightsideIceKernel.cs not found")
    else:
        for bad in ("using Verse", "using UnityEngine", "using RimWorld"):
            if bad in kern:
                E("kernel", "the kernel contains '%s': the fuzz compiles it on plain net8.0" % bad)
        csproj = next(iter(glob.glob(os.path.join(src, "*.csproj"))), None)
        if csproj is None or 'Include="Kernel\\RM_NightsideIceKernel.cs"' not in rd(csproj):
            E("kernel", "the mod csproj does not compile Kernel\\RM_NightsideIceKernel.cs (EnableDefaultCompileItems is false: it would build nothing)")
        callers = {"RM_HeatDial.cs": ("DialDue", "Ease", "Target", "RoomHeat", "FireHeat", "PowerHeat", "HottestIndex", "SourceCacheValid"),
                   "RM_BreachCracks.cs": ("BreachDue", "BreachRollMade", "BreachChance", "ShivvenCount", "BreakHours", "InEdgeBand", "CrackLook"),
                   "RM_Shivven.cs": ("IcePath", "Touches", "LegIndex")}
        for f, fns in callers.items():
            for fn in fns:
                if "RM_NightsideIceKernel.%s(" % fn not in nocom.get(f, ""):
                    E("kernel", "%s no longer calls RM_NightsideIceKernel.%s: the fuzz would be proving a copy" % (f, fn))
    # settings
    mod_cs = nocom.get("RM_NightsideIceMod.cs", "")
    inits = dict(re.findall(r"public static (?:bool|float|int) (\w+)\s*=\s*([^;]+);", mod_cs))
    scribes = dict(re.findall(r'Scribe_Values\.Look\(ref (\w+), "\w+", ([^)]+)\)', mod_cs))
    keys = dict(re.findall(r'Scribe_Values\.Look\(ref (\w+), "(\w+)"', mod_cs))
    sliders = {}
    for m in re.finditer(r"(\w+)\s*=\s*(?:Mathf\.RoundToInt\()?list\.Slider\(\1,\s*([-\d.]+)f,\s*([-\d.]+)f\)", mod_cs):
        sliders[m.group(1)] = (float(m.group(2)), float(m.group(3)))
    if len(inits) < 12:
        E("settings", "found %d settings, expected 13 (parser blind?)" % len(inits))
    for n, v in inits.items():
        if n not in scribes:
            E("settings", "%s has a static default but is never Scribed (it would not persist)" % n)
            continue
        if keys.get(n) != n:
            E("settings", "%s is Scribed under key %r, not its own name" % (n, keys.get(n)))
        if v.strip().rstrip("f") != scribes[n].strip().rstrip("f"):
            E("settings", "%s: static default %s but Scribe default %s" % (n, v.strip(), scribes[n].strip()))
        if n in sliders:
            lo, hi = sliders[n]
            d = float(v.strip().rstrip("f"))
            if not lo <= d <= hi:
                E("settings", "%s default %s lies outside its slider range %s..%s" % (n, d, lo, hi))
    full = "\n".join(cs.values())
    if re.search(r"averages one (?:breach )?a day", full):
        E("text", "a setting or comment still promises 'one a day' (measured ~71 h per breach at a full dial: the two-day cooldown)")
    # defs
    defs = {}
    for p in glob.glob(os.path.join(mod, "Defs", "**", "*.xml"), recursive=True):
        try:
            root = ET.parse(p).getroot()
        except ET.ParseError:
            continue
        for d in root.iter():
            n = d.findtext("defName")
            if n:
                defs[n] = (d, p)
                defs[(d.tag, n)] = (d, p)
    for needed in ("RM_Shivven", "RM_BreachCrack", "RM_ShivvenBreach"):
        if needed not in defs:
            E("names", "%s is looked up by name in the code but no def under Defs/ defines it" % needed)
    if ("ThingDef", "RM_BreachCrack") in defs:
        d, _ = defs[("ThingDef", "RM_BreachCrack")]
        if "RM_Building_BreachCrack" not in (d.findtext("thingClass") or ""):
            E("crack", "RM_BreachCrack's thingClass must be RimMandrake.NightsideIce.RM_Building_BreachCrack")
        hp = d.find("statBases/MaxHitPoints")
        if hp is None or float(hp.text or "0") <= 0:
            E("crack", "RM_BreachCrack has no MaxHitPoints: 'destroy it in time and the breach is stopped' needs an attackable building")
        if (d.findtext("passability") or "").strip() in ("Impassable",):
            E("crack", "RM_BreachCrack is Impassable: a crack in open ice must not wall off the base")
    thing = defs.get(("ThingDef", "RM_Shivven"), (None, None))[0]
    if thing is None:
        E("shivven", "no ThingDef RM_Shivven")
    else:
        comps = ET.tostring(thing, encoding="unicode")
        if "RM_CompProperties_ShivvenHeatSeek" not in comps:
            E("shivven", "RM_Shivven does not carry RM_CompProperties_ShivvenHeatSeek")
        if "RM_SandSwimExtension" not in comps:
            E("shivven", "RM_Shivven has no RM_SandSwimExtension: the heat-seek comp reads it and does nothing without it")
        for li in thing.iter("li"):
            if (li.get("Class") or "").endswith("RM_CompProperties_ShivvenHeatSeek"):
                for tag, lo in (("legCells", 1), ("searchCellBudget", 1), ("intervalTicks", 1)):
                    v = li.findtext(tag)
                    if v is not None:
                        try:
                            if int(v) < lo:
                                E("shivven", "%s %s must be >= %d" % (tag, v, lo))
                        except ValueError:
                            E("shivven", "%s %r does not parse" % (tag, v))
    return errs


def main(argv):
    mod = os.path.join(REPO, "src", "RimMandrake", "NightsideIce")
    if "--mod-dir" in argv:
        mod = argv[argv.index("--mod-dir") + 1]
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        rc = lint_mod_defs.run("NightsideIce", argv)
    out = buf.getvalue()
    errs = extras(mod)
    if "--quiet" not in argv:
        sys.stdout.write(out)
    else:
        for l in out.splitlines():
            if l.startswith("ERROR"):
                print(l)
    for e in errs:
        print(e)
    return rc if rc else (1 if errs else 0)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
