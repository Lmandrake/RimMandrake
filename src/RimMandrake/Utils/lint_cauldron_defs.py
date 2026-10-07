#!/usr/bin/env python3
"""Offline lint of the Cauldron mod: XML defs/patches against its C# source (see lint_modpack_defs.py for the generic
checks) plus Cauldron-specific data checks:

  cauldron-vent     the vent's RM_VentExtension: every weather row and the bloom weather name a WeatherDef of this mod, no
                    weather listed twice, the bloom row louder than the default and the falter quieter than every row, positive
                    recover / recent / suppression numbers
  cauldron-garden   RM_CondensateHabitatExtension: chances in [0,1], growth range ordered inside [0,1], vent ring ordered,
                    a known vent habitat, and either a shore or a habitat (ConfigErrors says it at load)
  cauldron-yield    RM_CompProperties_MetalYield: a metalDef, countAtMinGrowth <= countAtFullGrowth, the plant's
                    harvestMinGrowth below 1
  cauldron-flecks   RM_AssayFlecksExtension: lightFrom <= heavyFrom inside [0,1]; overlay art counted (art owed = dormant, INFO)
  cauldron-vexxiss  RM_CompProperties_VexxissBehaviour: positive intervals, vent scan radius <= groan radius, positive print
                    step and lifetime, every water swap names two terrains

    python3 src/RimMandrake/Utils/lint_cauldron_defs.py [--mod-dir <dir>] [--quiet]
"""
import os
import re
import sys
import xml.etree.ElementTree as ET

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import lint_modpack_defs as L  # noqa: E402

HABITATS = {"None", "StableRing", "ChronicLeak", "RecentBlowout"}


def _f(el, tag):
    t = el.findtext(tag)
    try:
        return float(t.strip()) if t is not None else None
    except ValueError:
        return None


def extra(mod, E, W, defs_xml, patch_xml, defnames, ctx):
    n = {"vent": 0, "garden": 0, "yield": 0, "flecks": 0, "vexxiss": 0}
    docs = []
    for p in defs_xml:
        try:
            docs.append((p, ET.parse(p).getroot()))
        except ET.ParseError:
            pass
    weathers = {dn for (t, dn) in defnames if t == "WeatherDef"}
    terrains = {dn for (t, dn) in defnames if t == "TerrainDef"}
    plants = {}
    for p, root in docs:
        for d in root:
            if d.tag == "ThingDef" and d.findtext("defName") and d.find("plant") is not None:
                plants[d.findtext("defName")] = d
    missing_art = 0
    for p, root in docs:
        rel = os.path.relpath(p, mod)
        for d in root:
            owner = d.findtext("defName") or d.get("ParentName") or d.tag
            for el in d.iter():
                cls = el.get("Class", "")
                if cls.endswith("RM_VentExtension"):
                    n["vent"] += 1
                    rows = []
                    for li in el.findall("weatherOutput/li"):
                        w, o = (li.findtext("weather") or "").strip(), _f(li, "output")
                        if w.startswith(L.OUR_PREFIX) and w not in weathers:
                            E("cauldron-vent", f"{rel}: weather row {w} is not a WeatherDef of this mod")
                        if o is None or o < 0:
                            E("cauldron-vent", f"{rel}: weather row {w} has output {li.findtext('output')}")
                        rows.append((w, o if o is not None else 0.0))
                    ws = [w for w, _ in rows]
                    for w in set(ws):
                        if ws.count(w) > 1:
                            E("cauldron-vent", f"{rel}: weather {w} listed twice (only the first row ever applies)")
                    bloom = (el.findtext("bloomWeather") or "").strip()
                    if bloom.startswith(L.OUR_PREFIX) and bloom not in weathers:
                        E("cauldron-vent", f"{rel}: bloomWeather {bloom} is not a WeatherDef of this mod")
                    default = _f(el, "defaultOutput")
                    default = 1.0 if default is None else default
                    for w, o in rows:
                        if w == bloom and o <= default:
                            E("cauldron-vent", f"{rel}: the bloom row ({o}) is not louder than the default output ({default})")
                    fo = _f(el, "falterOutput")
                    fo = 0.1 if fo is None else fo
                    if any(o <= fo for _, o in rows) or default <= fo:
                        E("cauldron-vent", f"{rel}: falterOutput {fo} is not quieter than every weather row and the default")
                    for f in ("recoverTicks", "recentBlowoutTicks", "suppressionNeeded"):
                        v = _f(el, f)
                        if v is not None and v <= 0:
                            E("cauldron-vent", f"{rel}: {f} = {v} must be > 0")
                    v = _f(el, "suppressionDecayPerDay")
                    if v is not None and v < 0:
                        E("cauldron-vent", f"{rel}: suppressionDecayPerDay {v} < 0 would grow the meter")
                if cls.endswith("RM_CondensateHabitatExtension"):
                    n["garden"] += 1
                    for f in ("mapgenChance", "colonizeChance", "spawnGrowthMin", "spawnGrowthMax"):
                        v = _f(el, f)
                        if v is not None and not (0.0 <= v <= 1.0):
                            E("cauldron-garden", f"{rel}: {owner}.{f} = {v} outside [0,1]")
                    lo, hi = _f(el, "spawnGrowthMin"), _f(el, "spawnGrowthMax")
                    if lo is not None and hi is not None and lo > hi:
                        E("cauldron-garden", f"{rel}: {owner} spawn growth {lo}..{hi} is reversed")
                    lo, hi = _f(el, "ventMinRadius"), _f(el, "ventRadius")
                    if lo is not None and hi is not None and hi <= lo:
                        E("cauldron-garden", f"{rel}: {owner} ventRadius {hi} must exceed ventMinRadius {lo}")
                    hab = (el.findtext("ventHabitat") or "None").strip()
                    if hab not in HABITATS:
                        E("cauldron-garden", f"{rel}: {owner} ventHabitat {hab} is not one of {sorted(HABITATS)}")
                    if hab == "None" and not el.findall("shoreOf/li"):
                        E("cauldron-garden", f"{rel}: {owner} has neither shoreOf terrains nor a ventHabitat")
                    for li in el.findall("shoreOf/li"):
                        t = (li.text or "").strip()
                        if t.startswith(L.OUR_PREFIX) and t not in terrains:
                            E("cauldron-garden", f"{rel}: {owner} shoreOf {t} is not a TerrainDef of this mod")
                if cls.endswith("RM_CompProperties_MetalYield"):
                    n["yield"] += 1
                    if not (el.findtext("metalDef") or "").strip():
                        E("cauldron-yield", f"{rel}: {owner} metal yield names no metalDef")
                    lo, hi = _f(el, "countAtMinGrowth"), _f(el, "countAtFullGrowth")
                    if lo is not None and hi is not None and lo > hi:
                        E("cauldron-yield", f"{rel}: {owner} yields more at minimum growth ({lo}) than at full growth ({hi})")
                    pl = d.find("plant")
                    hmg = _f(pl, "harvestMinGrowth") if pl is not None else None
                    if hmg is not None and hmg >= 1.0:
                        E("cauldron-yield", f"{rel}: {owner} harvestMinGrowth {hmg} >= 1: the yield lerp has no range")
                if cls.endswith("RM_AssayFlecksExtension"):
                    n["flecks"] += 1
                    lf, hf = _f(el, "lightFrom"), _f(el, "heavyFrom")
                    lf = 1.0 / 3.0 if lf is None else lf
                    hf = 2.0 / 3.0 if hf is None else hf
                    if not (0.0 <= lf <= hf <= 1.0):
                        E("cauldron-flecks", f"{rel}: {owner} fleck bands light {lf:.2f} / heavy {hf:.2f} must satisfy 0 <= light <= heavy <= 1")
                    for tag in ("lightTexPath", "heavyTexPath"):
                        tp = (el.findtext(tag) or "").strip()
                        if tp and not os.path.exists(os.path.join(mod, "Textures", *tp.split("/")) + ".png"):
                            missing_art += 1
                if cls.endswith("RM_CompProperties_VexxissBehaviour"):
                    n["vexxiss"] += 1
                    for f in ("fireScanIntervalTicks", "waterCheckIntervalTicks", "ventScanIntervalTicks", "printCheckIntervalTicks",
                              "printLifetimeTicks", "ventDrinkCooldownTicks", "attackJobExpiryTicks"):
                        v = _f(el, f)
                        if v is not None and v <= 0:
                            E("cauldron-vexxiss", f"{rel}: {f} = {v} must be > 0 (IsHashIntervalTick divides by it)")
                    scan, groan = _f(el, "ventScanRadius"), _f(el, "ventGroanRadius")
                    if scan is not None and groan is not None and groan < scan:
                        E("cauldron-vexxiss", f"{rel}: ventGroanRadius {groan} is smaller than ventScanRadius {scan}")
                    ps = _f(el, "printStepCells")
                    if ps is not None and ps <= 0:
                        E("cauldron-vexxiss", f"{rel}: printStepCells {ps} <= 0 prints on every check")
                    for li in el.findall("waterSwaps/li"):
                        fr, to = (li.findtext("from") or "").strip(), (li.findtext("to") or "").strip()
                        if not fr or not to or fr == to:
                            E("cauldron-vexxiss", f"{rel}: water swap {fr!r} -> {to!r} is empty or a no-op")
                        for t in (fr, to):
                            if t.startswith(L.OUR_PREFIX) and t not in terrains:
                                E("cauldron-vexxiss", f"{rel}: water swap terrain {t} is not a TerrainDef of this mod")
    if n["vent"] == 0:
        E("cauldron-vent", "no RM_VentExtension found in this mod's defs (wrong --mod-dir?)")
    print(f"cauldron data: {n['vent']} vent ext, {n['garden']} garden ext, {n['yield']} yield comps, {n['flecks']} fleck ext "
          f"({missing_art} overlay textures not on disk: dormant by design), {n['vexxiss']} vexxiss comps checked")


if __name__ == "__main__":
    sys.exit(L.run(sys.argv[1:], "Cauldron", "RM_CauldronSettings", "RM_CauldronMod.cs", "RM_Cauldron.csproj", "cauldron", extra=extra))
