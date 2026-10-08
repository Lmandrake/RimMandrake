#!/usr/bin/env python3
"""Offline lint of Warcasket (mandrake.rm.warcasket): the generic mod lint (lint_mod_defs.py) plus data checks the generic lint cannot see:

  wc-suit        the suit ticks (tickerType Rare, inherited by the Junker variant), its failure numbers stay probabilities even for a wrecked
                 suit at three hazards, the per-failure damage leaves the suit many failures to live, three hazards at once cannot kill the
                 wearer with one breach, the kernel's thresholds are the ones the XML ships
  wc-hediffs     both hediffs: lethalSeverity 1, stage minSeverity strictly ascending from 0, tendable; the breach decays; sustained
                 compound exposure outruns the decay (the mechanic can actually kill) and one failure alone cannot
  wc-terrain     the terrain clock: the suit's protection fits the stat's range, the drive-factor floor leaves the gear-held branch of the
                 kernel unreachable (WARN: a warcasket wearer still drowns, in the hours printed), time to lethal per protection
  wc-sarcophagus every salvage row names a def that exists (this mod's or Core's) with a stack limit of at least 1, the extension fields
                 are sane, the Junker variant never generates on its own; WARN when the variant inherited the recipe (craftable core source)
  wc-core        the core ticks (Rare), is single-stack, belongs to the hazard-cask category, the bay's filters admit it and the cask
                 category; the bay ticks (Rare) and carries the shielding comp; dose numbers positive
  wc-kernel-pure the kernel imports no Verse / RimWorld / UnityEngine and is listed in the csproj; the mod's remaining inline constants
                 alias the kernel's

    python3 src/RimMandrake/Utils/lint_warcasket_defs.py [--quiet] [--mod-dir D] [--plant-check]
"""
import contextlib
import glob
import io
import math
import os
import re
import sys
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import lint_mod_defs  # noqa: E402

REPO = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
SRC = os.path.join(REPO, "src")
DEFAULT_MOD = os.path.join(SRC, "RimMandrake", "Warcasket")
CORE_STACK_LIMIT = {"ComponentIndustrial": 10, "Steel": 75, "Plasteel": 75, "ComponentSpacer": 10}   # vanilla stack limits, for the rows we ship


def read(p):
    return open(p, encoding="utf-8-sig").read()


def xroot(p):
    return ET.fromstring(read(p).encode("utf-8"))


def main(argv):
    quiet = "--quiet" in argv
    mod = argv[argv.index("--mod-dir") + 1] if "--mod-dir" in argv else DEFAULT_MOD
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        rc = lint_mod_defs.run("Warcasket", ["--mod-dir", mod])
    gl = buf.getvalue().splitlines()
    if rc == 2:
        print("\n".join(gl))
        return 2
    errs = [l for l in gl if l.startswith("ERROR")]
    warns = [l for l in gl if l.startswith("WARN")]
    E = lambda c, m: errs.append(f"ERROR {c}: {m}")
    W = lambda c, m: warns.append(f"WARN  {c}: {m}")
    src = os.path.join(mod, "Source")
    defs = os.path.join(mod, "Defs")
    kernel = read(os.path.join(src, "Kernel", "RM_WarcasketKernel.cs"))
    n = {"defs": 0, "salvage": 0}

    # ---- the suit ----
    apparel = xroot(os.path.join(defs, "ThingDefs_Apparel", "RM_Warcasket.xml"))
    suit = next((d for d in apparel.iter("ThingDef") if d.findtext("defName") == "RM_Warcasket"), None)
    junker = next((d for d in apparel.iter("ThingDef") if d.findtext("defName") == "RM_WarcasketJunker"), None)
    if suit is None or junker is None:
        print("LINT UNMEASURED: RM_Warcasket / RM_WarcasketJunker not parsed")
        return 2
    n["defs"] += 2
    if suit.findtext("tickerType") != "Rare":
        E("wc-suit", "RM_Warcasket is not tickerType Rare: apparel defaults to Never, so the compound-failure roll would never run")
    if suit.get("Name") != "RM_Warcasket" or junker.get("ParentName") != "RM_Warcasket":
        E("wc-suit", "the Junker variant no longer inherits from RM_Warcasket by its Name= attribute (ParentName resolves by Name, never defName)")
    elif junker.findtext("tickerType") not in (None, "Rare"):
        E("wc-suit", "the Junker variant overrides tickerType away from Rare")
    comp = suit.find(".//comps/li[@Class='RimMandrake.Warcasket.RM_CompProperties_WarcasketIntegrity']")
    if comp is None:
        E("wc-suit", "RM_Warcasket carries no RM_CompProperties_WarcasketIntegrity")
        return finish(errs, warns, quiet, n)
    f = lambda k: float(comp.findtext(k))
    base, extra, dmg, sev = f("baseFailureChancePerCheck"), f("failureChancePerExtraHazard"), f("integrityDamagePerFailure"), f("wearerHediffSeverityPerFailure")
    cold, heat, vac = f("extremeColdThresholdC"), f("extremeHeatThresholdC"), f("vacuumThreshold")
    maxhp = float(suit.findtext("statBases/MaxHitPoints"))
    if base < 0 or extra < 0:
        E("wc-suit", "negative failure chance")
    if (base + extra) * 1.6 > 1.0:
        E("wc-suit", f"a wrecked suit at three hazards would fail with probability {(base + extra) * 1.6:.2f} > 1: every check")
    if not (cold < heat):
        E("wc-suit", f"cold threshold {cold} is not below heat threshold {heat}: every temperature is a hazard")
    if not (0 < vac < 1):
        E("wc-suit", f"vacuum threshold {vac} outside (0, 1)")
    if dmg + 12 >= maxhp / 4:
        W("wc-suit", f"a failure costs up to {dmg + 12:.0f} of {maxhp:.0f} hp: the suit survives fewer than four failures")
    if dmg < 0 or sev <= 0:
        E("wc-suit", "per-failure damage / severity not positive")
    if 3 * sev >= 1.0:
        E("wc-suit", f"one failure at three hazards adds {3 * sev:.2f} breach severity: the wearer dies from a single roll")
    if int(f("checkIntervalTicks")) != 250:
        W("wc-suit", "checkIntervalTicks is not the rare-tick cadence (250): the comp ticks on CompTickRare and ignores the field")
    for nm, kv in (("extremeColdThresholdC", "-60"), ("extremeHeatThresholdC", "70"), ("vacuumThreshold", "0.5")):
        if comp.findtext(nm) != kv.lstrip("+"):
            W("wc-suit", f"{nm} {comp.findtext(nm)} differs from the thresholds the fuzz exercises ({kv}); the kernel takes it as input, so only the fuzz's edge table is stale")

    # ---- hediffs ----
    hed = {h.findtext("defName"): h for h in xroot(os.path.join(defs, "HediffDefs", "RM_WarcasketHediffs.xml")).iter("HediffDef")}
    n["defs"] += len(hed)
    decay = 0.0
    for nm in ("RM_TerrainImmersionHazard", "RM_WarcasketBreach"):
        h = hed.get(nm)
        if h is None:
            E("wc-hediffs", f"{nm} missing")
            continue
        if h.findtext("lethalSeverity") != "1":
            E("wc-hediffs", f"{nm} lethalSeverity is {h.findtext('lethalSeverity')}, not 1 (the fuzz's death model)")
        mins = [float(s.findtext("minSeverity") or 0) for s in h.findall("stages/li")]
        if not mins or mins[0] != 0 or any(b <= a for a, b in zip(mins, mins[1:])):
            E("wc-hediffs", f"{nm} stage minSeverity not strictly ascending from 0: {mins}")
        if h.findtext("tendable") != "true":
            E("wc-hediffs", f"{nm} is not tendable")
        if nm == "RM_WarcasketBreach":
            sp = h.find(".//comps/li[@Class='HediffCompProperties_SeverityPerDay']/severityPerDay")
            decay = -float(sp.text) if sp is not None else 0.0
    if decay <= 0:
        E("wc-hediffs", "the breach hediff no longer decays: one failure would linger forever")
    else:
        per_day = 60000 / 250
        net = per_day * base * (sev * 2) - decay
        pristine_2 = per_day * base * sev * 2
        if sev * 2 >= 1.0:
            E("wc-hediffs", "a single failure at two hazards is lethal")
        if pristine_2 <= decay:
            W("wc-hediffs", f"sustained 2-hazard exposure of a pristine suit adds {pristine_2:.2f}/day against a decay of {decay}/day: it can never kill")
        n["compound_net_per_day"] = round(net, 3)

    # ---- the terrain clock ----
    stat = xroot(os.path.join(defs, "StatDefs", "RM_WarcasketStats.xml")).find("StatDef")
    prot = float(suit.findtext("statBases/RM_HazardousTerrainProtection"))
    if not (0 < prot <= float(stat.findtext("maxValue"))):
        E("wc-terrain", f"suit protection {prot} outside (0, stat maxValue {stat.findtext('maxValue')}]")
    imm = read(os.path.join(src, "RM_MapComponent_HazardousTerrainImmersion.cs"))
    mind = re.search(r"MinDriveFactor = ([^;]+);", imm)
    ph = re.search(r"ProtectionDriveFactor\([^;]*?, MinDriveFactor, ([0-9.]+)f\)", imm)
    kmin = re.search(r"MinDriveFactor = ([0-9.]+)f;", kernel)
    if not mind or not kmin or not ph:
        print("LINT UNMEASURED: immersion drive-factor call / kernel floor not parsed")
        return 2
    if "RM_WarcasketKernel.MinDriveFactor" not in mind.group(1):
        E("wc-kernel-pure", "the map component's MinDriveFactor is no longer an alias of the kernel's")
    gain = float(re.search(r"GainPerCheckUnprotected = ([0-9.]+)f", kernel).group(1))
    floor = float(kmin.group(1))
    hold = float(ph.group(1))
    if floor > 0 and hold == 0:
        drive = max(floor, 1 - prot)
        hours = math.ceil(1 / (gain * drive)) * 250 / 2500
        full = math.ceil(1 / (gain * floor)) * 250 / 2500
        W("wc-terrain", f"drive factor floors at {floor} with no hold threshold, so the kernel's gear-held branch (drive <= 0) can never run: "
                        f"a warcasket wearer (protection {prot}) in deep water still reaches lethal severity in {hours:.1f} h, perfect gear in {full:.1f} h")
    elif hold > 0:
        W("wc-terrain", "a hold threshold is set: re-measure which protection holds the clock before trusting the time-to-lethal figures")

    # ---- sarcophagus and salvage ----
    ext = junker.find(".//modExtensions/li[@Class='RimMandrake.Warcasket.RM_JunkerSarcophagusExtension']")
    if ext is None:
        E("wc-sarcophagus", "the Junker variant lost RM_JunkerSarcophagusExtension")
        return finish(errs, warns, quiet, n)
    own = {d.findtext("defName"): d for p in glob.glob(os.path.join(defs, "**", "*.xml"), recursive=True) for d in xroot(p).iter("ThingDef") if d.findtext("defName")}
    for row in ext.findall("salvage/*"):
        n["salvage"] += 1
        cnt = int(row.text)
        if cnt <= 0:
            E("wc-sarcophagus", f"salvage row {row.tag} has count {cnt}")
        if row.tag in own:
            lim = int(own[row.tag].findtext("stackLimit") or 1)
        elif row.tag in CORE_STACK_LIMIT:
            lim = CORE_STACK_LIMIT[row.tag]
        else:
            E("wc-sarcophagus", f"salvage row {row.tag} names no def this mod defines and no Core def the lint knows")
            continue
        if lim < 1:
            E("wc-sarcophagus", f"salvage row {row.tag} has stackLimit {lim} < 1: the crack job loop would never place it")
    if int(ext.findtext("crackOpenTicks") or 0) <= 0:
        E("wc-sarcophagus", "crackOpenTicks not positive")
    if ext.findtext("isSealedSarcophagus") != "true":
        E("wc-sarcophagus", "the Junker variant's extension is not sealed")
    if junker.findtext("generateAllowChance") != "0":
        E("wc-sarcophagus", "the Junker variant may generate on random pawns (generateAllowChance != 0)")
    if junker.find("recipeMaker") is None and suit.find("recipeMaker") is not None:
        W("wc-sarcophagus", "RM_WarcasketJunker inherits RM_Warcasket's recipeMaker: the adjusted warcasket is craftable at the machining table, and "
                            "every one worn to a death and cracked open yields a half-extracted core (the core's comment says no recipe makes one)")
    if junker.find(".//comps/li[@Class='RimMandrake.Warcasket.RM_CompProperties_SarcophagusSeal']") is None:
        E("wc-sarcophagus", "the Junker variant carries no RM_CompProperties_SarcophagusSeal: it never seals")

    # ---- the core and the bay ----
    items = xroot(os.path.join(defs, "ThingDefs_Items", "RM_HalfExtractedCore.xml"))
    core = next(d for d in items.iter("ThingDef") if d.findtext("defName") == "RM_HalfExtractedCore")
    cats = {c.findtext("defName") for c in items.iter("ThingCategoryDef")}
    n["defs"] += 2
    if core.findtext("tickerType") != "Rare":
        E("wc-core", "RM_HalfExtractedCore is not tickerType Rare: it would never dose")
    if core.findtext("stackLimit") != "1":
        E("wc-core", "the core stacks: claims and doses assume single items")
    cat = core.findtext("thingCategories/li")
    if cat not in cats:
        E("wc-core", f"the core's category {cat} is not defined in this mod")
    cd = core.find(".//comps/li[@Class='RimMandrake.Warcasket.RM_CompProperties_CoreDose']")
    if cd is None or float(cd.findtext("radius")) <= 0 or float(cd.findtext("toxicFactor")) <= 0:
        E("wc-core", "the core's dose comp is missing or has a non-positive radius / factor")
    bay = next(d for p in glob.glob(os.path.join(defs, "ThingDefs_Buildings", "*.xml")) for d in xroot(p).iter("ThingDef") if d.findtext("defName") == "RM_CaskBay")
    if bay.findtext("tickerType") != "Rare":
        E("wc-core", "RM_CaskBay is not tickerType Rare: its shielding comp would never hold the dissolve clock")
    if bay.find(".//comps/li[@Class='RimMandrake.Warcasket.RM_CompProperties_CaskShielding']") is None:
        E("wc-core", "the bay carries no shielding comp")
    for sect in ("fixedStorageSettings", "defaultStorageSettings"):
        flt = bay.find(f"building/{sect}/filter")
        if flt is None or "RM_HalfExtractedCore" not in [e.text for e in flt.findall("thingDefs/li")] or cat not in [e.text for e in flt.findall("categories/li")]:
            E("wc-core", f"the bay's {sect} no longer admits the core and its category")
    if bay.findtext("thingClass") != "Building_Storage":
        E("wc-core", "the bay is no longer a Building_Storage (stored items are read from its cells)")

    # ---- kernel / csproj ----
    if re.search(r"^\s*using\s+(Verse|RimWorld|UnityEngine|HarmonyLib)", kernel, flags=re.M):
        E("wc-kernel-pure", "the kernel imports Verse/RimWorld/UnityEngine/HarmonyLib (the fuzz build would break)")
    proj = read(os.path.join(src, "RM_Warcasket.csproj"))
    if 'Compile Include="Kernel\\RM_WarcasketKernel.cs"' not in proj:
        E("wc-kernel-pure", "the kernel is not listed in RM_Warcasket.csproj (it compiles into nothing, silently)")
    if "SelfTest" in proj:
        E("wc-kernel-pure", "the SelfTest folder is compiled into the mod assembly")
    for fn in ("RM_CompWarcasketIntegrity.cs", "RM_MapComponent_HazardousTerrainImmersion.cs", "RM_CaskBay.cs", "RM_Sarcophagus.cs"):
        if "RM_WarcasketKernel." not in read(os.path.join(src, fn)):
            E("wc-kernel-pure", f"{fn} no longer calls the kernel")
    return finish(errs, warns, quiet, n)


def finish(errs, warns, quiet, n):
    if not quiet:
        for l in warns:
            print(l)
    for l in errs:
        print(l)
    print(f"warcasket lint (data): {n['defs']} defs checked, {n['salvage']} salvage rows, "
          f"{len(errs)} ERROR, {len(warns)} WARN")
    return 1 if errs else 0


PLANTS = [
    ("suit stops ticking", "Defs/ThingDefs_Apparel/RM_Warcasket.xml", "<tickerType>Rare</tickerType>", "<tickerType>Never</tickerType>"),
    ("failure odds exceed one", "Defs/ThingDefs_Apparel/RM_Warcasket.xml", "<baseFailureChancePerCheck>0.015</baseFailureChancePerCheck>", "<baseFailureChancePerCheck>0.9</baseFailureChancePerCheck>"),
    ("one failure kills", "Defs/ThingDefs_Apparel/RM_Warcasket.xml", "<wearerHediffSeverityPerFailure>0.08</wearerHediffSeverityPerFailure>", "<wearerHediffSeverityPerFailure>0.4</wearerHediffSeverityPerFailure>"),
    ("thresholds swapped", "Defs/ThingDefs_Apparel/RM_Warcasket.xml", "<extremeColdThresholdC>-60</extremeColdThresholdC>", "<extremeColdThresholdC>90</extremeColdThresholdC>"),
    ("breach stops decaying", "Defs/HediffDefs/RM_WarcasketHediffs.xml", "<severityPerDay>-0.4</severityPerDay>", "<severityPerDay>0.4</severityPerDay>"),
    ("hediff stages out of order", "Defs/HediffDefs/RM_WarcasketHediffs.xml", "<minSeverity>0.35</minSeverity>", "<minSeverity>0.05</minSeverity>"),
    ("salvage names a missing def", "Defs/ThingDefs_Apparel/RM_Warcasket.xml", "<RM_HalfExtractedCore>1</RM_HalfExtractedCore>", "<RM_HalfExtractedCoreX>1</RM_HalfExtractedCoreX>"),
    ("core stops ticking", "Defs/ThingDefs_Items/RM_HalfExtractedCore.xml", "<tickerType>Rare</tickerType>", "<tickerType>Never</tickerType>"),
    ("core stacks", "Defs/ThingDefs_Items/RM_HalfExtractedCore.xml", "<stackLimit>1</stackLimit>", "<stackLimit>20</stackLimit>"),
    ("bay stops ticking", "Defs/ThingDefs_Buildings/RM_CaskBay.xml", "<tickerType>Rare</tickerType>", "<tickerType>Never</tickerType>"),
    ("bay refuses the core", "Defs/ThingDefs_Buildings/RM_CaskBay.xml", "<li>RM_HalfExtractedCore</li>", "<li>RM_HalfExtractedCoreX</li>"),
    ("junker generates on its own", "Defs/ThingDefs_Apparel/RM_Warcasket.xml", "<generateAllowChance>0</generateAllowChance>", "<generateAllowChance>0.3</generateAllowChance>"),
    ("kernel imports Verse", "Source/Kernel/RM_WarcasketKernel.cs", "using System;", "using System;\nusing Verse;"),
    ("kernel missing from csproj", "Source/RM_Warcasket.csproj", '<Compile Include="Kernel\\RM_WarcasketKernel.cs" />', ""),
    ("drive floor alias drifts", "Source/RM_MapComponent_HazardousTerrainImmersion.cs", "MinDriveFactor = RM_WarcasketKernel.MinDriveFactor;", "MinDriveFactor = 0.05f;"),
]


def plant_check():
    import shutil
    import subprocess
    import tempfile
    caught = 0
    for name, rel, old, new in PLANTS:
        with tempfile.TemporaryDirectory() as td:
            dst = os.path.join(td, "Warcasket")
            shutil.copytree(DEFAULT_MOD, dst, ignore=shutil.ignore_patterns("__pycache__", "Assemblies", "bin", "obj", "Textures", "SelfTest"))
            f = os.path.join(dst, rel)
            t = open(f, encoding="utf-8").read()
            if old not in t:
                print("PLANT TARGET NOT FOUND:", name)
                continue
            open(f, "w", encoding="utf-8").write(t.replace(old, new, 1))
            r = subprocess.run([sys.executable, os.path.abspath(__file__), "--quiet", "--mod-dir", dst], capture_output=True, text=True)
            hit = [l for l in (r.stdout + r.stderr).splitlines() if l.startswith("ERROR") or "Traceback" in l or "UNMEASURED" in l]
            print(("CAUGHT  " if hit else "MISSED  ") + name + ("  " + hit[0][:110] if hit else ""))
            caught += bool(hit)
    print(f"{caught}/{len(PLANTS)} planted defects caught")
    return 0 if caught == len(PLANTS) else 1


if __name__ == "__main__":
    if "--plant-check" in sys.argv:
        sys.exit(plant_check())
    sys.exit(main(sys.argv[1:]))
