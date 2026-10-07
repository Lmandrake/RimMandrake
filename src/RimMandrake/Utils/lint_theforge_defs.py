#!/usr/bin/env python3
"""Offline lint of the TheForge mod: XML defs/patches against its C# source (see lint_modpack_defs.py for the generic
checks) plus TheForge-specific data checks:

  theforge-cycle    the RM_ForgeCycleExtension on the pulse condition: every phase range ordered and positive, hiss lead
                    shorter than the still heat, wave/flood/garden counts ordered, chances in [0,1], maxFrozenCells > 0,
                    and the basalt / pumice / crack terrains defined and <temporary>true (ConfigErrors says it at load)
  theforge-garden   the floatstone garden ripens (start growth -> harvestMinGrowth over growDays) inside the SHORTEST
                    growth phase, or gardens drift off unharvested
  theforge-comps    CompProperties_ForgeCycleDormancy / DhokkurWays / JossurStoop numbers: positive intervals, ordered
                    bands, a slow hediff defined when the run clock is on
  Scaffolding settings the mod header documents as declared-but-unwired are allowed and not WARNed.

    python3 src/RimMandrake/Utils/lint_theforge_defs.py [--mod-dir <dir>] [--quiet]
"""
import glob
import os
import re
import sys
import xml.etree.ElementTree as ET

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import lint_modpack_defs as L  # noqa: E402

SCAFFOLDING = ("tibannaTapRate", "vaporColumnImmunity", "towerScatterCount", "dieOffRingDensity", "ventWorkSpeedBonus")


def _rng(text):
    m = re.match(r"^\s*(-?[\d.]+)\s*~\s*(-?[\d.]+)\s*$", text or "")
    return (float(m.group(1)), float(m.group(2))) if m else None


def _f(el, tag):
    t = el.findtext(tag)
    try:
        return float(t.strip()) if t is not None else None
    except ValueError:
        return None


def extra(mod, E, W, defs_xml, patch_xml, defnames, ctx):
    n = {"cycle": 0, "garden": 0, "comps": 0}
    docs = []
    for p in defs_xml:
        try:
            docs.append((p, ET.parse(p).getroot()))
        except ET.ParseError:
            pass
    temporary = {}
    plants = {}
    for p, root in docs:
        for d in root:
            if d.tag == "TerrainDef" and d.findtext("defName"):
                temporary[d.findtext("defName")] = (d.findtext("temporary") or "").strip().lower() == "true"
            if d.tag == "ThingDef" and d.findtext("defName") and d.find("plant") is not None:
                plants[d.findtext("defName")] = d.find("plant")
    for p, root in docs:
        rel = os.path.relpath(p, mod)
        for el in root.iter():
            cls = el.get("Class", "")
            if cls.endswith("RM_ForgeCycleExtension"):
                n["cycle"] += 1
                hours = {}
                for f in ("stillHours", "gasWashHours", "rainHours", "freezeHours", "growthHours", "cracksHours", "meltHours"):
                    r = _rng(el.findtext(f))
                    if el.findtext(f) is not None and (r is None or r[0] <= 0 or r[0] > r[1]):
                        E("theforge-cycle", f"{rel}: {f} = {el.findtext(f)} is not a positive ordered range")
                    hours[f] = r
                lead = _f(el, "hissLeadHours")
                if lead is not None and hours.get("stillHours") and lead >= hours["stillHours"][0]:
                    E("theforge-cycle", f"{rel}: hissLeadHours {lead} is not shorter than the shortest still heat {hours['stillHours'][0]}")
                for f in ("gasWashWaves", "floodReleases", "gardenCount"):
                    r = _rng(el.findtext(f))
                    if el.findtext(f) is not None and (r is None or r[0] < 0 or r[0] > r[1]):
                        E("theforge-cycle", f"{rel}: {f} = {el.findtext(f)} is not an ordered non-negative range")
                for f in ("gasWashCellChance", "pumiceChance", "gardenStartGrowth"):
                    v = _f(el, f)
                    if v is not None and not (0.0 <= v <= 1.0):
                        E("theforge-cycle", f"{rel}: {f} = {v} outside [0,1]")
                mf = _f(el, "maxFrozenCells")
                if mf is not None and mf <= 0:
                    E("theforge-cycle", f"{rel}: maxFrozenCells {mf} <= 0 freezes nothing")
                for f in ("basaltTerrain", "pumiceTerrain", "crackTerrain"):
                    t = (el.findtext(f) or "").strip()
                    if t and t.startswith(L.OUR_PREFIX):
                        if t not in temporary:
                            E("theforge-cycle", f"{rel}: {f} {t} is not a TerrainDef of this mod")
                        elif not temporary[t]:
                            E("theforge-cycle", f"{rel}: {f} {t} must be <temporary>true</temporary> (laid on the temp-terrain layer)")
                # the garden must ripen inside the shortest growth phase
                gd = (el.findtext("gardenDef") or "").strip()
                if gd:
                    n["garden"] += 1
                    pl = plants.get(gd)
                    if pl is None:
                        E("theforge-garden", f"{rel}: gardenDef {gd} is not a plant ThingDef of this mod")
                    else:
                        days, ripe = _f(pl, "growDays"), _f(pl, "harvestMinGrowth")
                        start = _f(el, "gardenStartGrowth") or 0.0
                        shortest = hours.get("growthHours")
                        if days is not None and ripe is not None and shortest:
                            need = max(0.0, ripe - start) * days * 24.0
                            if need > shortest[0]:
                                E("theforge-garden", f"{rel}: {gd} needs {need:.1f} h to ripen ({start}->{ripe} over {days} days) but the shortest growth phase is {shortest[0]} h")
            if cls.endswith("CompProperties_ForgeCycleDormancy"):
                n["comps"] += 1
                if (_f(el, "checkIntervalTicks") or 250) <= 0:
                    E("theforge-comps", f"{rel}: dormancy checkIntervalTicks <= 0")
                for f in ("minAwakeHours", "slowFinalHours"):
                    v = _f(el, f)
                    if v is not None and v < 0:
                        E("theforge-comps", f"{rel}: dormancy {f} = {v} < 0")
                if (el.findtext("runClock") or "").strip().lower() == "true":
                    sh = (el.findtext("slowHediff") or "").strip()
                    if not sh:
                        E("theforge-comps", f"{rel}: runClock is on but no slowHediff names the final-quarter slowing")
                    elif sh.startswith(L.OUR_PREFIX) and ("HediffDef", sh) not in defnames:
                        E("theforge-comps", f"{rel}: slowHediff {sh} is not a HediffDef of this mod")
                    rs = _f(el, "runSoundSlowFactor")
                    if rs is not None and rs < 1:
                        E("theforge-comps", f"{rel}: runSoundSlowFactor {rs} < 1 would speed the scuttle up toward the end of the run")
                    if (_f(el, "runSoundIntervalTicks") or 70) <= 0:
                        E("theforge-comps", f"{rel}: runSoundIntervalTicks <= 0")
            if cls.endswith("CompProperties_DhokkurWays"):
                n["comps"] += 1
                for f in ("checkIntervalTicks", "shoveIntervalTicks"):
                    v = _f(el, f)
                    if v is not None and v <= 0:
                        E("theforge-comps", f"{rel}: dhokkur {f} = {v} <= 0 (IsHashIntervalTick would divide by it)")
                for f in ("wakeWaterTicks", "sealDepressionRadius"):
                    v = _f(el, f)
                    if v is not None and v < 0:
                        E("theforge-comps", f"{rel}: dhokkur {f} = {v} < 0")
            if cls.endswith("CompProperties_JossurStoop"):
                n["comps"] += 1
                lo, hi = _f(el, "stoopMinDistance"), _f(el, "stoopMaxDistance")
                if lo is not None and hi is not None and lo >= hi:
                    E("theforge-comps", f"{rel}: stoop band {lo}..{hi} is empty")
                if (_f(el, "checkIntervalTicks") or 20) <= 0:
                    E("theforge-comps", f"{rel}: jossur checkIntervalTicks <= 0")
    if n["cycle"] == 0:
        E("theforge-cycle", "no RM_ForgeCycleExtension found in this mod's defs (wrong --mod-dir?)")
    print(f"theforge data: {n['cycle']} cycle extension, {n['garden']} garden check, {n['comps']} comp property blocks checked")


if __name__ == "__main__":
    sys.exit(L.run(sys.argv[1:], "TheForge", "RM_TheForgeSettings", "RM_TheForgeMod.cs", "RM_TheForge.csproj", "theforge", extra=extra, allow_dead=SCAFFOLDING))
