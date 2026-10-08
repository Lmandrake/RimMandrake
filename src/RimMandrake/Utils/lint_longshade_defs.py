#!/usr/bin/env python3
"""Offline lint of the LongShade mod (defs/patches vs C#): the generic lint (lint_mod_defs.py) plus data checks it cannot see:

  ls-armed     a static class whose static constructor installs a Harmony patch MUST carry [StaticConstructorOnStartup]: nothing else ever runs
               a static constructor of a class nobody references, so the patch silently never arms (the dewfringe rim gate was dead this way)
  ls-engine    WildPlantSpawner.CalculatePlantsWhichCanGrowAt still takes (IntVec3 c, List<ThingDef> outPlants, ...) and the spawner still has a
               `map` field (the postfix binds `c`, `outPlants` and `___map` by name); the gravship members the commons read still exist
  ls-ladder    the Shipfall Commons rungs are listed in ascending afterHours order (the ladder opens the leading run of rungs), at least one rung,
               chances in 0..1, a positive radius, minShade in (0,1], named races exist, maxBodySize >= 0
  ls-cache     every place the commons list is cleared also drops the cache key (an emptied list served as "fresh" after a re-landing)
  ls-midden    the midden heap's numbers are sane (layers, gain, cooldown, ticks, radii, spacing) and its yield table is non-empty with positive
               weights, ordered counts, items that stack (stackLimit >= 1 is read as >= 1) and builder races that exist
  ls-kernel    the kernel is Verse-free, listed in the mod csproj and called by the midden, map-generation, shipfall and dewfringe code
  ls-art       art a def names but the mod does not ship is an ERROR unless it is the one filed placeholder below

    python3 src/RimMandrake/Utils/lint_longshade_defs.py [--mod-dir <dir>] [--quiet]
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
ENGINE = os.environ.get("RIMWORLD_DECOMPILED", "/mnt/d/Luke/dev/reference/rimworld-decompiled")
# Finished art (artpipe done/ls_regen_RM_Dakkra_rest_v1_*) that has not been installed through the art ledger yet; the def keeps the owner-ruled
# stationaryGraphicData (LONGSHADE_SHEET_STRUCTURAL_RULINGS_1, 2026-10-04). Reported as a WARN until the texture lands.
KNOWN_MISSING_ART = ("Things/Pawn/Animal/RM_Dakkra/RM_Dakkra_rest",)


def rd(p):
    return open(p, encoding="utf-8-sig", errors="replace").read()


def extras(mod):
    errs = []
    E = lambda k, m: errs.append("ERROR ls-%s: %s" % (k, m))
    src = os.path.join(mod, "Source")
    cs = {os.path.relpath(p, src).replace(os.sep, "/"): rd(p) for p in glob.glob(os.path.join(src, "**", "*.cs"), recursive=True)
          if "SelfTest" not in p and "/obj/" not in p and "/bin/" not in p}
    nocom = {k: re.sub(r"//[^\n]*", "", v) for k, v in cs.items()}
    # armed
    n_static = 0
    for f, t in nocom.items():
        for m in re.finditer(r"((?:\[[^\]]+\]\s*)*)(?:public\s+|internal\s+)?static\s+class\s+(\w+)\s*\{", t):
            attrs, name = m.group(1), m.group(2)
            sc = re.search(r"\bstatic\s+%s\s*\(\s*\)\s*\{" % re.escape(name), t[m.end():])
            if not sc:
                continue
            seg = t[m.end() + sc.end(): m.end() + sc.end() + 2500]
            if re.search(r"\.Patch\(|PatchAll\(", seg):
                n_static += 1
                if "StaticConstructorOnStartup" not in attrs:
                    E("armed", "%s: %s installs a Harmony patch in its static constructor but lacks [StaticConstructorOnStartup]: nothing runs that constructor, so the patch never arms" % (f, name))
    if n_static < 1:
        E("armed", "found no static class with a patching static constructor (parser blind?)")
    # engine
    wp = os.path.join(ENGINE, "RimWorld", "WildPlantSpawner.cs")
    if os.path.isfile(wp):
        w = rd(wp)
        m = re.search(r"void CalculatePlantsWhichCanGrowAt\(([^)]*)\)", w)
        if not m:
            E("engine", "WildPlantSpawner.CalculatePlantsWhichCanGrowAt is gone: the dewfringe gate cannot arm")
        else:
            args = m.group(1)
            if not re.search(r"IntVec3\s+c\b", args) or not re.search(r"List<ThingDef>\s+outPlants\b", args):
                E("engine", "CalculatePlantsWhichCanGrowAt no longer takes (IntVec3 c, List<ThingDef> outPlants, ...): %s" % args.strip())
        if not re.search(r"\bMap\s+map\s*;", w):
            E("engine", "WildPlantSpawner has no `map` field: the postfix's ___map binding would throw")
    # gravship members used by the commons
    gs = nocom.get("RM_ShipfallCommons.cs", "")
    for member, where in (("ValidSubstructure", ("RimWorld", "Building_GravEngine.cs")), ("GetPlayerGravEngine_NewTemp", ("RimWorld", "GravshipUtility.cs")), ("PilotConsole", ("RimWorld", "JobDefOf.cs"))):
        p = os.path.join(ENGINE, *where)
        if member in gs and os.path.isfile(p) and member not in rd(p):
            E("engine", "%s no longer exists in %s (RM_ShipfallCommons.cs reads it)" % (member, where[1]))
    # ladder (the biome's extension)
    n_rungs = 0
    for p in glob.glob(os.path.join(mod, "Defs", "**", "*.xml"), recursive=True):
        try:
            root = ET.parse(p).getroot()
        except ET.ParseError:
            continue
        defnames = set()
        for el in root.iter("li"):
            if (el.get("Class") or "").endswith("RM_ShipfallCommonsExtension"):
                stages = el.find("stages")
                rungs = list(stages) if stages is not None else []
                if not rungs:
                    E("ladder", "RM_ShipfallCommonsExtension has no stages")
                hours = []
                for ri, r in enumerate(rungs):
                    n_rungs += 1
                    try:
                        hours.append(float(r.findtext("afterHours") or "0"))
                    except ValueError:
                        E("ladder", "rung %d afterHours does not parse" % ri)
                        continue
                    if hours[-1] < 0:
                        E("ladder", "rung %d has a negative afterHours" % ri)
                    mb = r.findtext("maxBodySize")
                    if mb is not None and float(mb) < 0:
                        E("ladder", "rung %d maxBodySize is negative" % ri)
                if any(b < a for a, b in zip(hours, hours[1:])):
                    E("ladder", "rungs are not in ascending afterHours order %s: the ladder opens the leading run of rungs, so a later-listed earlier rung waits for the rungs before it" % hours)
                for tag in ("pullChance", "stayChance"):
                    v = el.findtext(tag)
                    if v is not None and not 0 <= float(v) <= 1:
                        E("ladder", "%s %s must be in 0..1" % (tag, v))
                if int(el.findtext("radius") or "8") < 1:
                    E("ladder", "radius must be >= 1")
                ms = el.findtext("minShade")
                if ms is not None and not 0 < float(ms) <= 1:
                    E("ladder", "minShade %s must be in (0,1]" % ms)
                for r in el.iter("races"):
                    for race in r:
                        name = (race.text or "").strip()
                        if name and name not in _all_defnames(mod):
                            E("ladder", "rung race %s is not defined under Defs/ (a missing race silently admits nobody)" % name)
    if n_rungs < 4:
        E("ladder", "found %d ladder rungs, expected the 4 shipped ones (parser blind?)" % n_rungs)
    # cache keys
    sc = nocom.get("RM_ShipfallCommons.cs", "")
    lines = sc.split("\n")
    n_clear = 0
    for i, line in enumerate(lines):
        if re.search(r"\bcommons\.Clear\(\)", line):
            n_clear += 1
            window = "\n".join(lines[max(0, i - 4): i + 6])
            if "commonsKey.Invalidate()" not in window and "commonsKey.Set(" not in window:
                E("cache", "RM_ShipfallCommons.cs line %d clears the commons list without dropping the cache key: a re-landing ship would be served the emptied list" % (i + 1))
    if n_clear < 2:
        E("cache", "found %d commons.Clear() sites, expected the shipped ones (parser blind?)" % n_clear)
    # middens
    n_heap = 0
    for p in glob.glob(os.path.join(mod, "Defs", "**", "*.xml"), recursive=True):
        try:
            root = ET.parse(p).getroot()
        except ET.ParseError:
            continue
        for li in root.iter("li"):
            if not (li.get("Class") or "").endswith("CompProperties_RM_MiddenHeap"):
                continue
            n_heap += 1
            g = lambda t, d: float(li.findtext(t) if li.findtext(t) is not None else d)
            if g("maxLayers", 4) < 1:
                E("midden", "maxLayers < 1")
            if not 0 <= g("startLayers", 1) <= g("maxLayers", 4):
                E("midden", "startLayers must be within 0..maxLayers")
            if not g("tendGain", 0.1) > 0:
                E("midden", "tendGain must be > 0 or a heap never gains a layer")
            if g("tendCooldownTicks", 30000) < 0 or g("tendDurationTicks", 400) < 1 or g("searchTicks", 900) < 1 or g("rollsPerLayer", 2) < 1:
                E("midden", "a tick count or rollsPerLayer is out of range")
            if g("maxHeapsPerMap", 6) < 1 or g("minHeapSpacing", 16) <= 0 or g("buildRadius", 10) < 1 or g("heapSearchRadius", 30) <= 0:
                E("midden", "heap count / spacing / radius out of range")
            if not 0 <= g("minBuildShade", 0.5) <= 1:
                E("midden", "minBuildShade must be in 0..1")
            yields = li.find("yields")
            rows = list(yields) if yields is not None else []
            if not rows:
                E("midden", "empty yields table")
            for r in rows:
                if not (r.findtext("thing") or "").strip():
                    E("midden", "a yield row has no <thing>")
                if float(r.findtext("weight") or "1") <= 0:
                    E("midden", "yield %s has a non-positive weight (it can never be rolled)" % r.findtext("thing"))
                cnt = (r.findtext("count") or "1~1").split("~")
                try:
                    lo, hi = int(cnt[0]), int(cnt[-1])
                except ValueError:
                    E("midden", "yield %s count %r does not parse" % (r.findtext("thing"), r.findtext("count")))
                    continue
                if lo < 1 or hi < lo:
                    E("midden", "yield %s count %s must be an ordered range of at least 1" % (r.findtext("thing"), r.findtext("count")))
            for race in li.iter("builderRaces"):
                for b in race:
                    if (b.text or "").strip() not in _all_defnames(mod):
                        E("midden", "builder race %s is not defined under Defs/ (an unloaded name is skipped, so nobody builds or tends heaps)" % (b.text or "").strip())
    if n_heap < 1:
        E("midden", "found no CompProperties_RM_MiddenHeap (parser blind?)")
    # kernel
    kp = os.path.join(src, "Kernel", "RM_LongShadeKernel.cs")
    kern = re.sub(r"//[^\n]*", "", rd(kp)) if os.path.isfile(kp) else None
    if kern is None:
        E("kernel", "Kernel/RM_LongShadeKernel.cs not found")
    else:
        for bad in ("using Verse", "using UnityEngine", "using RimWorld"):
            if bad in kern:
                E("kernel", "the kernel contains '%s': the fuzz compiles it on plain net8.0" % bad)
        cp = next(iter(glob.glob(os.path.join(src, "*.csproj"))), None)
        if cp is None or 'Include="Kernel\\RM_LongShadeKernel.cs"' not in rd(cp):
            E("kernel", "the mod csproj does not compile Kernel\\RM_LongShadeKernel.cs (EnableDefaultCompileItems is false: it would build nothing)")
        callers = {"RM_LongShadeMiddens.cs": ("CanTendNow", "Tend", "SearchRolls", "StackSplit", "NearestTendable", "ShouldBuildHeap", "SpacingOk", "ClampStartLayers", "Untended"),
                   "RM_LongShadeMapgen.cs": ("DashCells", "RoadSpacing", "Islands", "TwoBiggest", "RimSample", "ClosestPair", "RoadSegments", "RoadLinkIndices", "GraveBand", "InGraveBand", "GravesFarEnough"),
                   "RM_ShipfallCommons.cs": ("OpenStages", "Admits", "FirstAdmitting", "CommonsCells"),
                   "RM_Patch_DewfringeWildSpawnGate.cs": ("OnRim",)}
        for f, fns in callers.items():
            for fn in fns:
                if "RM_LongShadeKernel.%s(" % fn not in nocom.get(f, ""):
                    E("kernel", "%s no longer calls RM_LongShadeKernel.%s: the fuzz would be proving a copy" % (f, fn))
    return errs


_NAMES = {}


def _all_defnames(mod):
    """every defName under src/*/*/Defs plus this mod's own Defs (the mod may be a temp copy during the planted-break selftest)"""
    if mod not in _NAMES:
        names = set()
        paths = glob.glob(os.path.join(REPO, "src", "*", "*", "Defs", "**", "*.xml"), recursive=True) + \
            glob.glob(os.path.join(mod, "Defs", "**", "*.xml"), recursive=True)
        for p in paths:
            try:
                names |= set(re.findall(r"<defName>([^<]+)</defName>", rd(p)))
            except OSError:
                pass
        _NAMES[mod] = names
    return _NAMES[mod]


def main(argv):
    mod = os.path.join(REPO, "src", "RimMandrake", "LongShade")
    if "--mod-dir" in argv:
        mod = argv[argv.index("--mod-dir") + 1]
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        rc = lint_mod_defs.run("LongShade", argv, known_missing_art=KNOWN_MISSING_ART)
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
