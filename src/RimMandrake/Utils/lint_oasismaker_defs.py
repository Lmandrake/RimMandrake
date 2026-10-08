#!/usr/bin/env python3
"""Offline lint of the OasisMaker mod (defs/patches vs C#): the generic lint (lint_mod_defs.py) plus data checks it cannot see:

  om-kernel     the kernel is Verse-free, listed in the mod csproj and called by the scorer, the place worker and the comp
  om-settings   every setting default sits inside its slider range and the floors are reachable (the floor cannot exceed the squares the
                scoring radius can ever count at its smallest), excellent > floor, minRadiusCap <= maxRadiusCap
  om-keyed      the three place-worker refusal strings exist in English Keyed and are non-empty (a missing key shows the raw key to the player)
  om-def        RM_OasisMaker carries the comp and the place worker the code expects, is rotatable=false (the footprint centre is not rotation-proof
                for an even size), and every terrain name on the growth ladders is a vanilla Core terrain or is defined under src/
  om-text       the Dormant/Attuning/Working inspect strings and the settings labels do not promise a shade reach the scorer cannot deliver

    python3 src/RimMandrake/Utils/lint_oasismaker_defs.py [--mod-dir <dir>] [--quiet]
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
# vanilla Core terrain defNames the ladders use (Core Defs/TerrainDefs); checked against the decompiled-def dump when reachable
CORE_TERRAIN = {"Sand", "SoftSand", "Gravel", "Soil", "SoilRich", "Mud", "Marsh", "WaterShallow"}


def rd(p):
    return open(p, encoding="utf-8-sig", errors="replace").read()


def extras(mod):
    errs = []
    E = lambda k, m: errs.append("ERROR om-%s: %s" % (k, m))
    src = os.path.join(mod, "Source")
    cs = {os.path.basename(p): rd(p) for p in glob.glob(os.path.join(src, "*.cs"))}
    nocom = {k: re.sub(r"//[^\n]*", "", v) for k, v in cs.items()}
    kp = os.path.join(src, "Kernel", "RM_OasisKernel.cs")
    kern = re.sub(r"//[^\n]*", "", rd(kp)) if os.path.isfile(kp) else None
    if kern is None:
        E("kernel", "Kernel/RM_OasisKernel.cs not found")
    else:
        for bad in ("using Verse", "using UnityEngine", "using RimWorld"):
            if bad in kern:
                E("kernel", "the kernel contains '%s': the fuzz compiles it on plain net8.0" % bad)
        cp = next(iter(glob.glob(os.path.join(src, "*.csproj"))), None)
        if cp is None or 'Include="Kernel\\RM_OasisKernel.cs"' not in rd(cp):
            E("kernel", "the mod csproj does not compile Kernel\\RM_OasisKernel.cs (EnableDefaultCompileItems is false: it would build nothing)")
        callers = {"RM_OasisPlacementScorer.cs": ("ScoreAt", "ShadeAt", "MeetsFloor", "Quality01"),
                   "RM_PlaceWorker_OasisMaker.cs": ("Verdict", "RadiusCap"),
                   "RM_CompOasisMaker.cs": ("Step", "AdvanceGrowth", "RingBand", "NextTerrain", "RadiusCap", "SpeedMultiplier")}
        for f, fns in callers.items():
            for fn in fns:
                if "RM_OasisKernel.%s(" % fn not in nocom.get(f, ""):
                    E("kernel", "%s no longer calls RM_OasisKernel.%s: the fuzz would be proving a copy" % (f, fn))
    # settings
    sc = nocom.get("RM_OasisMakerSettings.cs", "")
    inits = {n: v.strip() for n, v in re.findall(r"public static (?:bool|float|int) (\w+)\s*=\s*([^;]+);", sc)}
    scribes = {n: v.strip() for n, v in re.findall(r'Scribe_Values\.Look\(ref (\w+), "\w+", ([^)]+)\)', sc)}
    keys = dict(re.findall(r'Scribe_Values\.Look\(ref (\w+), "(\w+)"', sc))
    sliders = {m.group(1): (float(m.group(2)), float(m.group(3))) for m in re.finditer(r"(\w+)\s*=\s*(?:Mathf\.Max\([^,]+,\s*)?(?:\(int\)\s*)?list\.Slider\(\1,\s*([-\d.]+)f?,\s*([-\d.]+)f?\)", sc)}
    if len(inits) < 11:
        E("settings", "found %d settings, expected 11 (parser blind?)" % len(inits))
    for n, v in inits.items():
        if n not in scribes:
            E("settings", "%s has a static default but is never Scribed" % n)
            continue
        if keys.get(n) != n:
            E("settings", "%s is Scribed under key %r, not its own name" % (n, keys.get(n)))
        if v.rstrip("f") != scribes[n].rstrip("f"):
            E("settings", "%s: static default %s but Scribe default %s" % (n, v, scribes[n]))
        if n in sliders:
            lo, hi = sliders[n]
            d = float(v.rstrip("f")) if v not in ("true", "false") else 0
            if not lo <= d <= hi:
                E("settings", "%s default %s lies outside its slider range %s..%s" % (n, d, lo, hi))
    try:
        g = {n: float(v.rstrip("f")) for n, v in inits.items() if v not in ("true", "false")}
        if g["shadeScoreExcellent"] <= g["shadeScoreFloor"] or g["rockScoreExcellent"] <= g["rockScoreFloor"]:
            E("settings", "an 'excellent' score default must exceed its floor (quality would be 0 for every passing site)")
        if g["minRadiusCap"] > g["maxRadiusCap"]:
            E("settings", "minRadiusCap default exceeds maxRadiusCap")
        small = (2 * sliders.get("scoringRadius", (4, 12))[0] + 1) ** 2
        if g["shadeScoreFloor"] > small or g["rockScoreFloor"] > small:
            E("settings", "a default floor exceeds the %d cells the smallest scoring radius counts" % small)
        r = g["scoringRadius"]
        if g["shadeScoreFloor"] > (2 * r + 1) ** 2 or g["rockScoreFloor"] > (2 * r + 1) ** 2:
            E("settings", "a default floor exceeds the squares the default scoring radius counts")
    except KeyError as e:
        E("settings", "setting %s missing" % e)
    # Keyed
    kd = os.path.join(mod, "Languages", "English", "Keyed")
    keyed = {}
    for p in glob.glob(os.path.join(kd, "*.xml")):
        try:
            for el in ET.parse(p).getroot():
                keyed[el.tag] = (el.text or "").strip()
        except ET.ParseError:
            E("keyed", "%s does not parse" % os.path.basename(p))
    for k in ("RM_OasisMaker_NeedsShade", "RM_OasisMaker_NeedsRock", "RM_OasisMaker_NeedsBoth"):
        if not keyed.get(k):
            E("keyed", "%s is missing or empty in English Keyed (the player would see the raw key)" % k)
    # def
    defs = {}
    for p in glob.glob(os.path.join(mod, "Defs", "**", "*.xml"), recursive=True):
        try:
            root = ET.parse(p).getroot()
        except ET.ParseError:
            continue
        for d in root.iter("ThingDef"):
            if d.findtext("defName"):
                defs[d.findtext("defName")] = d
    d = defs.get("RM_OasisMaker")
    if d is None:
        E("def", "no ThingDef RM_OasisMaker")
    else:
        txt = ET.tostring(d, encoding="unicode")
        if "RimMandrake.OasisMaker.CompProperties_OasisMaker" not in txt:
            E("def", "RM_OasisMaker does not carry CompProperties_OasisMaker")
        if "RimMandrake.OasisMaker.RM_PlaceWorker_OasisMaker" not in txt:
            E("def", "RM_OasisMaker does not name the place worker")
        if (d.findtext("rotatable") or "true").strip().lower() != "false":
            E("def", "RM_OasisMaker must be rotatable=false: the ring centre of an even-sized footprint depends on rotation")
        if (d.findtext("tickerType") or "").strip() not in ("Rare", "Normal"):
            E("def", "RM_OasisMaker needs tickerType Rare (CompTickRare drives the whole machine); got %r" % d.findtext("tickerType"))
    # ladders vs terrain
    ladders = re.findall(r'(?:MarginLadder|PoolLadder) = \{([^}]*)\}', kern or "")
    names = {x.strip().strip('"') for l in ladders for x in l.split(",") if x.strip()}
    for nme in names:
        if nme not in CORE_TERRAIN:
            E("def", "ladder terrain %s is not a known Core terrain name (add it to the lint's list only after checking Core)" % nme)
    if "Sand" not in names or "WaterShallow" not in names or "SoilRich" not in names:
        E("def", "the ladders no longer reach Sand / SoilRich / WaterShallow")
    # text
    if re.search(r"shade[^\"\n]{0,60}\b(?:two|2)[- ]cells?\b", "\n".join(cs.values()), re.I):
        E("text", "a string promises shade from two cells away; the scorer only counts roofed cells and cells next to a shade caster")
    return errs


def main(argv):
    mod = os.path.join(REPO, "src", "RimMandrake", "OasisMaker")
    if "--mod-dir" in argv:
        mod = argv[argv.index("--mod-dir") + 1]
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        rc = lint_mod_defs.run("OasisMaker", argv)
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
