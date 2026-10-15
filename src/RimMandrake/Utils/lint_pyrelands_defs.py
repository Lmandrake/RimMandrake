#!/usr/bin/env python3
"""Offline lint of the Pyrelands mod AND its campaign companion mandrake.rut.pyrelandsmechanics (src/RimUtinni/PyrelandsMechanics):
XML defs/patches against C# source (see lint_modpack_defs.py for the generic checks, run against RM_PyrelandsSettings) plus
Pyrelands-specific data checks:

  pyrelands-tuning   PyrelandsTuning.cs relationships: raid threshold <= arson-debt cap, fire-front days ordered, charge/seek/avoid
                     ordered, bleed ambient below charge ambient, retry <= quiet, desert dwell <= max dwell, no biome on two herd legs
  pyrelands-slider   every Mod Settings slider of the companion whose value is compared with a capped quantity must not offer values past the
                     cap (the arson-debt threshold slider once went to 2000 against a 1500 cap, so the top quarter of it never raided)
  pyrelands-ground   deep ash stays the ground: gravelTerrain and the gravel/pocket noise bands cannot starve bar pyre_ground_deep_ash
  pyrelands-biome    the RM_Pyrelands BiomeDef: worker class resolves, the PyrelandsBiomeRanges numbers are ordered, the biome can WIN a tile
                     against vanilla's arid shrubland somewhere in its own band (else it never generates), plantDensity / wildPlantRegrowDays
                     equal the density enforcer's constants, every wildPlants row is on the wild-plant allowlist (else it is stripped at spawn)
  pyrelands-incident the companion's IncidentDefs: the worker classes exist in its source; its csproj lists every source file
  pyrelands-kernel   every Source/Kernel/*.cs is in the mod csproj AND the fuzz project (and FurnaceWarmthMath), and is engine-free;
                     the burn-history constants the fuzz hard-codes still equal MapComponent_BurnLine's
  pyrelands-turret   every CompProperties_TurretGun (the Barbslinger's tail guns) names a ThingDef of this mod
  pyrelands-flight   the fire-hawk's ember JobDef sets tryStartFlying + ifFlyingKeepFlying (else the sortie is walked)
  pyrelands-affordance every TerrainDef of ours carries Light, Medium, Heavy and Diggable like vanilla Soil (Heavy does not imply Medium)

    python3 src/RimMandrake/Utils/lint_pyrelands_defs.py [--mod-dir <dir>] [--quiet]
"""
import glob
import os
import re
import sys
import xml.etree.ElementTree as ET

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import lint_modpack_defs as L  # noqa: E402

UTINNI = os.path.join(L.REPO, "src", "RimUtinni", "PyrelandsMechanics")


def tuning(mod):
    txt = L.strip_comments(open(os.path.join(mod, "Source", "PyrelandsTuning.cs"), encoding="utf-8-sig").read())
    v, pend = {}, []
    for m in re.finditer(r"public\s+const\s+(?:float|int)\s+(\w+)\s*=\s*([^;]+);", txt):
        e = m.group(2).strip()
        try:
            v[m.group(1)] = float(e.rstrip("fF"))
        except ValueError:
            pend.append((m.group(1), e))
    for k, e in pend:
        if e in v:
            v[k] = v[e]
    arrays = {m.group(1): re.findall(r'"([^"]+)"', m.group(2)) for m in re.finditer(r"public\s+static\s+readonly\s+string\[\]\s+(\w+)\s*=\s*\{([^}]*)\}\s*;", txt)}
    return v, arrays


def _rng(text):
    m = re.match(r"^\s*(-?[\d.]+)\s*~\s*(-?[\d.]+)\s*$", text or "")
    return (float(m.group(1)), float(m.group(2))) if m else None


def extra(mod, E, W, defs_xml, patch_xml, defnames, ctx):
    n = {"consts": 0, "sliders": 0, "incidents": 0, "kernels": 0}
    v, arrays = tuning(mod)
    n["consts"] = len(v)
    if len(v) < 40:
        E("pyrelands-tuning", f"only {len(v)} constants parsed from PyrelandsTuning.cs: the reader is blind")
    g = lambda k: v.get(k)
    cap = g("ArsonDebtCap")

    def chk(cond, msg):
        # cond is a lambda: a constant missing from the parse (None) is reported, never a TypeError traceback.
        try:
            ok = cond()
        except TypeError:
            E("pyrelands-tuning", f"a constant this check needs was not parsed from PyrelandsTuning.cs: {msg}")
            return
        if not ok:
            E("pyrelands-tuning", msg)

    chk(lambda: g("ArsonDebtRaidThreshold") <= cap, f"ArsonDebtRaidThreshold {g('ArsonDebtRaidThreshold')} is above ArsonDebtCap {cap}: the shipped default can never raid")
    chk(lambda: g("FireFrontMinDays") <= g("FireFrontMaxDays"), "FireFrontMinDays > FireFrontMaxDays")
    chk(lambda: g("FireRiteGroupMin") <= g("FireRiteGroupMax"), "FireRiteGroupMin > FireRiteGroupMax")
    chk(lambda: 0.0 < g("FurnaceChargeSeekBelow") < g("FurnaceChargeAvoidAbove") <= 1.0, "furnace charge hysteresis not ordered inside (0,1]")
    chk(lambda: g("FurnaceBleedAmbientC") < g("FurnaceChargeAmbientC"), "furnace bleed ambient is not below the charge ambient (no dead band)")
    chk(lambda: g("StandingBurnRetryTicks") <= g("StandingBurnQuietTicks"), "StandingBurnRetryTicks > StandingBurnQuietTicks")
    chk(lambda: g("WorldHerdDeepDesertDwellTicks") <= g("WorldHerdMaxLegDwellTicks"), "desert dwell longer than the max leg dwell")
    chk(lambda: g("WorldHerdMinSize") <= g("WorldHerdMaxSize"), "herd size range reversed")
    chk(lambda: g("FlameHarvestMinFires") >= 1 and g("FireFrontWidthCells") >= 1, "harvest minimum fires / front width < 1")
    allnames = arrays.get("PyrelandsBiomeDefNames", []) + arrays.get("NearTerminatorBiomeDefNames", []) + arrays.get("DeepDesertBiomeDefNames", [])
    dup = sorted({x for x in allnames if allnames.count(x) > 1})
    chk(lambda: not dup, f"biome(s) listed on two herd legs: {', '.join(dup)}")
    biomes = set()
    for xp in glob.glob(os.path.join(L.REPO, "src", "**", "Defs", "**", "*.xml"), recursive=True):
        if os.sep + "obj" + os.sep in xp:
            continue
        try:
            for d in ET.parse(xp).getroot():
                if d.tag == "BiomeDef" and d.findtext("defName"):
                    biomes.add(d.findtext("defName"))
        except ET.ParseError:
            pass
    for nm in allnames:
        if nm.startswith(L.OUR_PREFIX) and nm not in biomes:
            W("pyrelands-tuning", f"herd-leg biome {nm} is not a BiomeDef anywhere in src (a leg that can never be found)")

    # ---- the companion's sliders vs the caps they are compared with
    mp = os.path.join(UTINNI, "Source", "PyrelandsMechanicsMod.cs")
    if os.path.exists(mp):
        mt = L.strip_comments(open(mp, encoding="utf-8-sig").read())
        m = re.search(r"arsonDebtRaidThreshold\s*=\s*list\.Slider\(\s*arsonDebtRaidThreshold\s*,\s*([^,]+),\s*([^)]+)\)", mt)
        if not m:
            E("pyrelands-slider", "the arson-debt threshold slider was not found (the lint is blind, or it was renamed)")
        else:
            n["sliders"] += 1
            hi = m.group(2).strip()
            hv = float(hi.rstrip("f")) if re.match(r"^-?[\d.]+f?$", hi) else (v.get(hi.split(".")[-1]) if hi.split(".")[-1] in v else None)
            if hv is None:
                E("pyrelands-slider", f"cannot evaluate the arson-debt slider maximum {hi!r}")
            elif cap is not None and hv > cap:
                E("pyrelands-slider", f"the arson-debt threshold slider offers up to {hv:g} but the debt is capped at {cap:g}: values above the cap can never raid")
        m = re.search(r"flameHarvestMinFires\s*=\s*Mathf\.RoundToInt\(list\.Slider\(\s*flameHarvestMinFires\s*,\s*([^,]+),\s*([^)]+)\)\)", mt)
        if m:
            n["sliders"] += 1
            if float(m.group(1).rstrip("f")) < 1:
                E("pyrelands-slider", "the flame-harvest minimum-fires slider can reach 0 (a visit with no burn)")
    else:
        E("pyrelands-slider", f"{mp} not found")

    # ---- the biome
    bp = os.path.join(mod, "Defs", "BiomeDefs", "Pyrelands.xml")
    arid = lambda t, r: 22.5 + (t - 20) * 2.2 + (r - 600) / 100.0
    if os.path.exists(bp):
        root = ET.parse(bp).getroot()
        for d in root:
            if d.tag != "BiomeDef" or d.findtext("defName") != "RM_Pyrelands":
                continue
            wc = (d.findtext("workerClass") or "").strip()
            if wc and wc.split(".")[-1] not in ctx["classes"]:
                E("pyrelands-biome", f"workerClass {wc} is not a C# class")
            ext = None
            for el in d.iter():
                if (el.get("Class") or "").endswith("PyrelandsBiomeRanges"):
                    ext = el
            tmin, tmax = (_rng(ext.findtext("temperature")) if ext is not None and ext.findtext("temperature") else (25.0, 60.0))
            rmin, rmax = (_rng(ext.findtext("rainfall")) if ext is not None and ext.findtext("rainfall") else (550.0, 1000.0))
            emin, emax = (_rng(ext.findtext("elevation")) if ext is not None and ext.findtext("elevation") else (0.0, 2200.0))
            base = float(ext.findtext("baseScore")) if ext is not None and ext.findtext("baseScore") else 30.0
            dw = float(ext.findtext("degreeWeight")) if ext is not None and ext.findtext("degreeWeight") else 2.6
            div = float(ext.findtext("rainfallDivisor")) if ext is not None and ext.findtext("rainfallDivisor") else 120.0
            if not (tmin < tmax and rmin < rmax and emin < emax):
                E("pyrelands-biome", f"a PyrelandsBiomeRanges band is empty or reversed: T {tmin}~{tmax}, R {rmin}~{rmax}, E {emin}~{emax}")
            else:
                wins, lo_t, hi_t = 0, None, None
                r = rmin
                while r < rmax:
                    t = tmin
                    while t <= tmax:
                        if base + (t - tmin) * dw + (r - rmin) / (div if div > 0.0001 else 1.0) > arid(t, r):
                            wins += 1
                            lo_t = t if lo_t is None else min(lo_t, t)
                            hi_t = t if hi_t is None else max(hi_t, t)
                            break
                        t += 0.1
                    r += 10.0
                if wins == 0:
                    E("pyrelands-biome", "the Pyrelands score never beats vanilla arid shrubland anywhere in its own band: the biome can never be placed")
                else:
                    print(f"pyrelands biome: out-bids arid shrubland from {lo_t:.1f} C (at the lowest rainfall row) in a band {tmin:g}~{tmax:g} C / {rmin:g}~{rmax:g} mm")
            pd, rg = d.findtext("plantDensity"), d.findtext("wildPlantRegrowDays")
            enf = open(os.path.join(mod, "Source", "RM_PyrelandsDensityEnforcer.cs"), encoding="utf-8-sig").read()
            ed = re.search(r"PlantDensity\s*=\s*([\d.]+)f", enf)
            er = re.search(r"WildPlantRegrowDays\s*=\s*([\d.]+)f", enf)
            if pd and ed and float(pd) != float(ed.group(1)):
                E("pyrelands-biome", f"plantDensity {pd} in the XML but the density enforcer re-asserts {ed.group(1)}")
            if rg and er and float(rg) != float(er.group(1)):
                E("pyrelands-biome", f"wildPlantRegrowDays {rg} in the XML but the density enforcer re-asserts {er.group(1)}")
            # PYRE_DEEP_ASH_TUNE_ONE_POINT_SHORT: bar pyre_ground_deep_ash wants >=0.85 of open land (aim 0.90) and the
            # real share is only readable live, so guard the INPUTS: gravel (>10-16% on 2026-10-12 maps) came from a wide
            # fertility rung and the rock-margin band (gravelTerrain), and pockets must stay rare.
            gt = d.findtext("gravelTerrain")
            if gt != "RM_FE_Ash_Deep":
                E("pyrelands-ground", f"gravelTerrain is {gt}, not RM_FE_Ash_Deep: the rock-margin band lays gravel over >5% of open land and the deep-ash bar (0.85) is missed")
            for li in d.findall("terrainsByFertility/li"):
                if li.findtext("terrain") != "RM_FE_Ash_Deep" and float(li.findtext("max") or 0) > 0.05:
                    E("pyrelands-ground", f"terrainsByFertility lays {li.findtext('terrain')} below noise {li.findtext('max')} (> 0.05): that alone starves the deep-ash bar")
            for pm in d.findall("terrainPatchMakers/li"):
                w = sum(min(float(t.findtext("max") or 0), 1.0) - max(float(t.findtext("min") or 0), 0.0)
                        for t in pm.findall("thresholds/li") if t.findtext("terrain") in ("RM_FE_Ground_Soil", "RM_FE_Ground_Gravel"))
                if w > 0.10:
                    E("pyrelands-ground", f"an unburned-pocket patchmaker spans {w:.2f} of its noise (> 0.10): pockets are meant to be rare")
            wl = open(os.path.join(mod, "Source", "WildPlantAllowlist.cs"), encoding="utf-8-sig").read()
            allow = set(re.findall(r'"(RM_FE_Plant_\w+)"', wl))
            wp = d.find("wildPlants")
            rows = [c.tag for c in wp] if wp is not None else []
            things = set()
            for xp in glob.glob(os.path.join(mod, "Defs", "**", "*.xml"), recursive=True):
                try:
                    for td in ET.parse(xp).getroot():
                        if td.tag == "ThingDef" and td.findtext("defName"):
                            things.add(td.findtext("defName"))
                except ET.ParseError:
                    pass
            if not allow:
                E("pyrelands-biome", "no allowlist entries parsed from WildPlantAllowlist.cs: the lint is blind")
            for a in sorted(allow):
                if a not in things:
                    E("pyrelands-biome", f"allowlisted plant {a} is not a ThingDef of this mod")
            for rtag in rows:
                if rtag not in allow:
                    E("pyrelands-biome", f"wildPlants row {rtag} is not on the wild-plant allowlist: the allowlist strips it at spawn, so it never grows")
            if not rows:
                E("pyrelands-biome", "RM_Pyrelands has no wildPlants rows")
            n["biome"] = 1
        if "biome" not in n:
            E("pyrelands-biome", "no BiomeDef RM_Pyrelands found in Defs/BiomeDefs/Pyrelands.xml")
    else:
        E("pyrelands-biome", f"{bp} not found")

    # ---- the companion mod
    usrc = {}
    for p in glob.glob(os.path.join(UTINNI, "Source", "*.cs")):
        usrc[os.path.basename(p)] = L.strip_comments(open(p, encoding="utf-8-sig", errors="replace").read())
    ucs = open(os.path.join(UTINNI, "Source", "RimMandrake.Utinni.PyrelandsMechanics.csproj"), encoding="utf-8-sig").read()
    listed = set(re.findall(r'Compile Include="([^"]+)"', ucs))
    for f in usrc:
        if f not in listed:
            E("pyrelands-incident", f"{f} is not in the companion csproj (compiles into nothing, silently)")
    ucode = "\n".join(usrc.values())
    for xp in glob.glob(os.path.join(UTINNI, "Defs", "**", "*.xml"), recursive=True):
        try:
            root = ET.parse(xp).getroot()
        except ET.ParseError as e:
            E("pyrelands-incident", f"{os.path.relpath(xp, UTINNI)}: {e}")
            continue
        for el in root.iter():
            cls = (el.text or "").strip() if el.tag in ("workerClass", "driverClass", "giverClass", "jobClass") else el.get("Class", "")
            if cls.startswith("RimMandrake.Utinni.PyrelandsMechanics."):
                n["incidents"] += 1
                short = cls.split(".")[-1]
                if not re.search(r"\bclass\s+" + short + r"\b", ucode):
                    E("pyrelands-incident", f"{os.path.relpath(xp, UTINNI)}: {cls} is not a class of the companion source")
    if n["incidents"] < 2:
        E("pyrelands-incident", f"only {n['incidents']} companion classes referenced from XML: the lint is blind")

    # ---- kernels
    kdir = os.path.join(mod, "Source", "Kernel")
    fuzz = os.path.join(mod, "Source", "SelfTest", "Fuzz", "RimMandrakePyrelands.Fuzz.csproj")
    fz = open(fuzz, encoding="utf-8-sig").read() if os.path.exists(fuzz) else ""
    fzc = "\n".join(re.findall(r'<Compile Include="[^"]+"', fz))
    if "FurnaceWarmthMath.cs" not in fzc:
        E("pyrelands-kernel", "FurnaceWarmthMath.cs is not in the fuzz project")
    for k in sorted(glob.glob(os.path.join(kdir, "*.cs"))):
        n["kernels"] += 1
        base = os.path.basename(k)
        if base not in fzc:
            E("pyrelands-kernel", f"Kernel/{base} is not in the fuzz project (unfuzzed)")
        if re.search(r"^\s*using (Verse|RimWorld|UnityEngine)", open(k, encoding="utf-8-sig").read(), flags=re.M):
            E("pyrelands-kernel", f"Kernel/{base} references Verse/RimWorld/UnityEngine (a kernel must be engine-free)")
    if n["kernels"] < 4:
        E("pyrelands-kernel", f"only {n['kernels']} kernel files found")
    # ---- a pawn's natural ranged attack (CompProperties_TurretGun, the Barbslinger's tail guns) names a ThingDef of this mod
    things, guns = set(), []
    for xp in glob.glob(os.path.join(mod, "Defs", "**", "*.xml"), recursive=True):
        try:
            root = ET.parse(xp).getroot()
        except ET.ParseError:
            continue
        for d in root:
            if d.tag == "ThingDef" and d.findtext("defName"):
                things.add(d.findtext("defName"))
            for li in d.iter("li"):
                if li.get("Class") == "CompProperties_TurretGun":
                    guns.append((d.findtext("defName"), (li.findtext("turretDef") or "").strip()))
    n["turrets"] = len(guns)
    if not guns:
        E("pyrelands-turret", "no CompProperties_TurretGun found in the mod's Defs (the Barbslinger's tail guns): the reader is blind")
    for owner, td in guns:
        if td not in things:
            E("pyrelands-turret", f"{owner}: CompProperties_TurretGun turretDef {td!r} is not a ThingDef in this mod (the ranged attack never exists)")
    # ---- natural ground carries vanilla Soil's build affordances (ASH_TERRAIN_FIX_NO_MEDIUM_GROUND): Heavy does not imply Medium.
    tbase, tconc = {}, []
    for xp in glob.glob(os.path.join(mod, "Defs", "**", "*.xml"), recursive=True):
        try:
            root = ET.parse(xp).getroot()
        except ET.ParseError:
            continue
        for d in root:
            if d.tag != "TerrainDef":
                continue
            a = d.find("affordances")
            own = (a.get("Inherit", "").lower() == "false", [li.text for li in a.findall("li")]) if a is not None else None
            if d.get("Name"):
                tbase[d.get("Name")] = (d.get("ParentName"), own)
            if d.get("Abstract", "").lower() != "true" and d.findtext("defName"):
                tconc.append((d.findtext("defName"), d.get("ParentName"), own))
    n["terrains"] = 0
    for dn, parent, own in tconc:
        if parent is not None and parent not in tbase:
            continue  # a vanilla base (FlagstoneBase): not ours to judge
        acc, chain, p = [], [own], parent
        while p in tbase:
            chain.append(tbase[p][1])
            p = tbase[p][0]
        for c in chain:
            if c is None:
                continue
            acc = c[1] + acc
            if c[0]:
                break
        n["terrains"] += 1
        miss = [x for x in ("Light", "Medium", "Heavy", "Diggable") if x not in acc]
        if miss:
            E("pyrelands-affordance", f"TerrainDef {dn} lacks {', '.join(miss)}: vanilla Soil carries them, and a building needing a missing one cannot be placed on it")
    if n["terrains"] == 0:
        E("pyrelands-affordance", "no Pyrelands TerrainDef parsed: the affordance check is blind")
    # ---- every Tribes incident obeys the Fire clock switch (FIRE_CLOCK_FIX_RAIDS_IGNORE_THE_SWITCH): its tooltip promises it.
    for fn in ("IncidentWorker_FireRaid.cs", "IncidentWorker_FlameHarvest.cs"):
        fp = os.path.join(UTINNI, "Source", fn)
        ft = L.strip_comments(open(fp, encoding="utf-8-sig").read()) if os.path.exists(fp) else ""
        if not re.search(r"TribesIncidentSwitchesOn\([^;]*fireClockEnabled", ft):
            E("pyrelands-incident", f"{fn}: CanFireNowSub does not gate on RM_BurnKernel.TribesIncidentSwitchesOn(..., fireClockEnabled), so the Fire clock switch does not stop it")
    # ---- the fire rite's exits source from EVERY travel toil (FIRE_RITE_FIX_DEFENDERS_MISS_THE_WAR): LordJob_Travel's DefendPoint
    # toil is a second source, and a signal-driven Trigger_BecamePlayerEnemy missed there is never replayed.
    fp = os.path.join(UTINNI, "Source", "LordJob_RUT_FireRite.cs")
    ft = L.strip_comments(open(fp, encoding="utf-8-sig").read()) if os.path.exists(fp) else ""
    for tr in ("arrived", "turnedOn"):
        if not re.search(tr + r"\.AddSources\(TravelToilsBut\(", ft):
            E("pyrelands-incident", f"LordJob_RUT_FireRite: transition {tr} does not source from every travel-subgraph toil (TravelToilsBut), so the DefendPoint toil misses it")
    # ---- a flyer's own sortie job flies (FIREHAWK_EMBER_FIX_WALKS_ITS_TWIG): without these flags Notify_JobStarted lands it.
    jobs = {}
    for xp in glob.glob(os.path.join(mod, "Defs", "**", "*.xml"), recursive=True):
        try:
            for d in ET.parse(xp).getroot():
                if d.tag == "JobDef" and d.findtext("defName"):
                    jobs[d.findtext("defName")] = d
        except ET.ParseError:
            pass
    for jn in ("RM_FireHawkCarryEmber",):
        d = jobs.get(jn)
        if d is None:
            E("pyrelands-flight", f"JobDef {jn} not found: the flight check is blind")
            continue
        for fld in ("tryStartFlying", "ifFlyingKeepFlying"):
            if (d.findtext(fld) or "").strip().lower() != "true":
                E("pyrelands-flight", f"JobDef {jn} lacks <{fld}>true: Pawn_FlightTracker.Notify_JobStarted force-lands the flyer, which walks its sortie")
    mc = open(os.path.join(mod, "Source", "MapComponent_BurnLine.cs"), encoding="utf-8-sig").read()
    hi_, hk = re.search(r"BurnHistoryIntervalTicks\s*=\s*(\d+)", mc), re.search(r"BurnHistoryKeepTicks\s*=\s*(\d+)", mc)
    if not hi_ or not hk or (int(hi_.group(1)), int(hk.group(1))) != (2500, 600000):
        E("pyrelands-kernel", "BurnHistoryIntervalTicks / BurnHistoryKeepTicks are no longer 2500 / 600000, which the fuzz hard-codes")
    print(f"pyrelands data: {n['consts']} tuning constants, {n['sliders']} companion sliders, biome checked, {n['incidents']} companion classes in XML, {n['kernels']} kernels checked, {n['turrets']} turret guns resolved")


# Settings keys that differ from their field ON PURPOSE (reported as WARN, never ERROR).
INTENTIONAL_KEYS = (
    # scorchFruitChance: per-tick -> per-cell semantics change 2026-09-16; the key was renamed so old saved per-tick values are ignored.
    'field scorchFruitChance is saved under key "scorchFruitChancePerCell"',
)


def main(argv):
    import contextlib
    import io
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        rc = L.run(argv, "Pyrelands", "RM_PyrelandsSettings", "RM_PyrelandsMod.cs", "FireEcologyHook.csproj", "pyrelands", extra=extra)
    out, errs = [], 0
    for line in buf.getvalue().splitlines():
        if line.startswith("ERROR") and any(k in line for k in INTENTIONAL_KEYS):
            line = "WARN  intentional-key:" + line[len("ERROR"):] + "  [renamed on purpose with a semantics change]"
        elif line.startswith("ERROR"):
            errs += 1
        out.append(line)
    warns = sum(1 for l in out if l.startswith("WARN"))
    for l in out:
        if " lint: " in l:
            continue
        if "--quiet" in argv and l.startswith("WARN"):
            continue
        print(l)
    summary = [l for l in out if " lint: " in l]
    if summary:
        print(f"{summary[0].rsplit(',', 2)[0]}, {errs} ERROR, {warns} WARN")
    return 1 if errs else (2 if rc == 2 else 0)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
