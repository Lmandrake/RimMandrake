#!/usr/bin/env python3
"""Offline lint of WeatherSuite (mandrake.rm.weathersuite): the generic mod lint (lint_mod_defs.py) plus data checks it cannot see.

  ws-geometry   every PlanetGeometryDef under src/ (the geometry lives in the RimUtinni wiring mod): exactly one is loaded (the mod reads
                whichever loads first), lat/lon in range, 0 <= wall min <= wall max <= 180, and the dark side starts at or past the wall's outer
                edge so the two bands can never overlap
  ws-defs       the aurora incident's gameCondition resolves and runs the maximised-aurora class; the incident targets the World (the
                any-home-map nightside test is only sound for a world-level incident); the front is permanent-capable and off underground
  ws-kernel     the kernel is Verse-free and listed in the csproj; the slider floors in the settings window equal the kernel's vanilla constants
                (so the vanilla floor is reachable but the sliders never promise less); no hand copy of the arc, the tint or the forecast sort survives

    python3 src/RimMandrake/Utils/lint_weathersuite_defs.py [--quiet] [--mod-dir D] [--geometry-dir D]
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
SRC = os.path.join(REPO, "src")
DEFAULT_MOD = os.path.join(SRC, "RimMandrake", "WeatherSuite")


def read(p):
    return open(p, encoding="utf-8-sig").read()


def main(argv):
    quiet = "--quiet" in argv
    mod = argv[argv.index("--mod-dir") + 1] if "--mod-dir" in argv else DEFAULT_MOD
    geo_root = argv[argv.index("--geometry-dir") + 1] if "--geometry-dir" in argv else None
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        rc = lint_mod_defs.run("WeatherSuite", ["--mod-dir", mod])
    gl = buf.getvalue().splitlines()
    if rc == 2:
        print("\n".join(gl))
        return 2
    errs = [l for l in gl if l.startswith("ERROR")]
    warns = [l for l in gl if l.startswith("WARN")]
    E = lambda c, m: errs.append(f"ERROR {c}: {m}")
    src = os.path.join(mod, "Source")
    n = {"geometry": 0, "defs": 0, "sliders": 0}

    # ws-geometry: the geometry def is shipped by the wiring mod; with --geometry-dir (selftest copy) read the copy
    roots = [geo_root] if geo_root else [os.path.join(SRC, "*", "*", "Defs"), os.path.join(mod, "Defs")]
    files = []
    for r in roots:
        files += glob.glob(os.path.join(r, "**", "*.xml"), recursive=True)
    geos = []
    for p in sorted(set(files)):
        if "PlanetGeometryDef" not in read(p):
            continue
        for d in ET.parse(p).getroot():
            if d.tag.endswith("PlanetGeometryDef"):
                geos.append((os.path.relpath(p, SRC), d))
    n["geometry"] = len(geos)
    if len(geos) != 1:
        E("ws-geometry", f"{len(geos)} PlanetGeometryDef defs loaded {[g[0] for g in geos]}: the mod reads whichever loads first, ship exactly one")
    for rel, d in geos:
        try:
            v = {k: float(d.findtext(k, dflt)) for k, dflt in (("substellarLat", "0"), ("substellarLon", "0"), ("terminatorBandMinArc", "63"),
                                                              ("terminatorBandMaxArc", "117"), ("nightsideBandMinArc", "117"))}
        except ValueError as e:
            E("ws-geometry", f"{rel}: unparsable number: {e}")
            continue
        if not -90 <= v["substellarLat"] <= 90 or not -180 <= v["substellarLon"] <= 180:
            E("ws-geometry", f"{rel}: substellar point {v['substellarLat']},{v['substellarLon']} is off the globe")
        if not 0 <= v["terminatorBandMinArc"] <= v["terminatorBandMaxArc"] <= 180:
            E("ws-geometry", f"{rel}: wall arcs {v['terminatorBandMinArc']}..{v['terminatorBandMaxArc']} are not 0 <= min <= max <= 180")
        if v["nightsideBandMinArc"] < v["terminatorBandMaxArc"]:
            E("ws-geometry", f"{rel}: the dark side starts at {v['nightsideBandMinArc']}, inside the wall (ends {v['terminatorBandMaxArc']}): a tile could carry both")

    # ws-defs
    defs = {}
    for p in glob.glob(os.path.join(mod, "Defs", "**", "*.xml"), recursive=True):
        for d in ET.parse(p).getroot():
            if d.findtext("defName"):
                defs[(d.tag, d.findtext("defName"))] = d
    inc = defs.get(("IncidentDef", "RM_WS_DarkAurora"))
    cond = defs.get(("GameConditionDef", "RM_WS_DarkAurora"))
    front = defs.get(("GameConditionDef", "RM_WS_TerminatorFront"))
    n["defs"] = sum(x is not None for x in (inc, cond, front))
    if inc is not None:
        if inc.findtext("gameCondition") != "RM_WS_DarkAurora" or cond is None:
            E("ws-defs", "the aurora incident's gameCondition does not resolve to this mod's RM_WS_DarkAurora")
        if [t.text for t in inc.findall("targetTags/li")] != ["World"]:
            E("ws-defs", "the aurora incident no longer targets the World alone (the any-home-map nightside gate assumes a world-level incident)")
        if inc.findtext("workerClass") != "RimMandrake.StarWars.WeatherSuite.IncidentWorker_NightsideAurora":
            E("ws-defs", "the aurora incident's worker is not IncidentWorker_NightsideAurora")
    if cond is not None and cond.findtext("conditionClass") != "RimMandrake.StarWars.WeatherSuite.GameCondition_DarkAuroraMax":
        E("ws-defs", "RM_WS_DarkAurora does not run GameCondition_DarkAuroraMax (the maximised look would never apply)")
    if front is not None:
        if front.findtext("canBePermanent") != "true":
            E("ws-defs", "RM_WS_TerminatorFront is not canBePermanent (MakeConditionPermanent would throw)")
        if front.findtext("allowUnderground") != "false":
            E("ws-defs", "RM_WS_TerminatorFront allows underground (pocket maps would get the storm wall)")

    # ws-kernel
    kernel = read(os.path.join(src, "Kernel", "RM_WeatherKernel.cs"))
    if re.search(r"^\s*using\s+(Verse|RimWorld|UnityEngine|HarmonyLib)", kernel, flags=re.M):
        E("ws-kernel", "the kernel imports Verse/RimWorld/UnityEngine/HarmonyLib (the fuzz build would break)")
    if "Kernel\\RM_WeatherKernel.cs" not in read(os.path.join(src, "WeatherSuiteHook.csproj")):
        E("ws-kernel", "WeatherSuiteHook.csproj does not compile Kernel\\RM_WeatherKernel.cs (EnableDefaultCompileItems is false: it compiles into nothing)")
    hook = "\n".join(l for l in read(os.path.join(src, "WeatherSuiteHook.cs")).splitlines() if not l.strip().startswith("//"))
    for pat, what in ((r"Mathf\.Acos", "a hand copy of the arc"), (r"Color\.Lerp\(Color\.white", "a hand copy of the tint"), (r"weighted\.Sort", "a hand copy of the forecast sort")):
        if re.search(pat, hook):
            E("ws-kernel", f"{what} survives in WeatherSuiteHook.cs beside the kernel")
    set_txt = read(os.path.join(src, "WeatherSuiteSettings.cs"))
    for fld, const in (("auroraSkySaturation", "VanillaSkySaturation"), ("auroraOverlaySaturation", "VanillaOverlaySaturation"), ("auroraSkyBrightness", "VanillaBrightness")):
        n["sliders"] += 1
        sm = re.search(fld + r" = list\.Slider\(" + fld + r", ([0-9.]+)f", set_txt)
        km = re.search(const + r" = ([0-9.]+)f", kernel)
        if not sm or not km or float(sm.group(1)) != float(km.group(1)):
            E("ws-kernel", f"slider floor of {fld} ({sm.group(1) if sm else None}) is not the kernel's {const} ({km.group(1) if km else None})")

    if not quiet:
        for l in warns:
            print(l)
    for l in errs:
        print(l)
    print(f"weathersuite lint (data): {n['geometry']} geometry def, {n['defs']} defs checked, {n['sliders']} slider floors, {len(errs)} ERROR, {len(warns)} WARN")
    return 1 if errs else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
