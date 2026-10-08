#!/usr/bin/env python3
"""Offline lint of Jawa Ion Weapons (mandrake.rsw.ionweapons): the ion damage def, its buildup hediff, the inverse-body-size stat, the load
folders that gate the vehicle tier, and the C# settings, against the pure kernel the damage worker / stat part / vehicle postfix call.

  ion-def      RSW_JawaIon_Damage is an IonDamageDef with the buildup worker, harmsHealth false (capture-not-kill), machine EMP >= droid EMP > 0,
               a buildup entry whose hediff exists and adds a positive amount; prints the stun ticks per tier and the hits that down a human
  ion-hediff   the buildup hediff starts at 0, decays, has ascending stages, a top stage reachable below maxSeverity, and the stage that
               carries the downing Consciousness cap is reachable; prints the hits to down a human at the shipped numbers
  ion-stat     the inverse-size stat is hidden, defaults to 1.0 and its part class resolves
  ion-vehicle  the vehicle patch's IonDamageDefName is the def's defName; LoadFolders gates VehicleTier on Vehicle Framework and lists "/"
  ion-settings Scribe default = initializer = key; every slider range contains its default; the exponent slider reaches 0 (off) and 3
  ion-guard    a def outside this mod naming one of its classes is guarded
  ion-kernel   the kernel imports no Verse / RimWorld / UnityEngine, is compiled by the main and vehicle-tier assemblies and the old SelfTest,
               and the worker / stat part / vehicle postfix call it

    python3 src/RimMandrake/Utils/lint_jawaionweapons_defs.py [--quiet] [--src-root D] [--plant-check]
"""
import glob
import math
import os
import re
import sys
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import lint_armoury_defs as LA  # noqa: E402

REPO = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
SRC = os.path.join(REPO, "src")
PACKAGE = "mandrake.rsw.ionweapons"
NS = "RimMandrake.StarWars.JawaIonWeapons."


def read(p):
    return open(p, encoding="utf-8-sig").read()


def main(argv):
    quiet = "--quiet" in argv
    src_root = argv[argv.index("--src-root") + 1] if "--src-root" in argv else SRC
    mod = os.path.join(src_root, "RimStarWars", "JawaIonWeapons")
    base = os.path.join(mod, "Source")
    errs, warns, info = [], [], []
    E = lambda c, m: errs.append(f"ERROR {c}: {m}")
    W = lambda c, m: warns.append(f"WARN  {c}: {m}")
    I = lambda c, m: info.append(f"INFO  {c}: {m}")
    cs = {os.path.relpath(p, base): LA.strip_cs(read(p)) for p in glob.glob(os.path.join(base, "**", "*.cs"), recursive=True) if os.sep + "obj" + os.sep not in p}
    compiled = set()
    for rel, t in cs.items():
        if rel.startswith(("SelfTest", "FuzzTest")):
            continue
        for n in re.findall(r"\b(?:public|internal)\s+(?:static\s+|abstract\s+|sealed\s+)*(?:class|enum|struct)\s+(\w+)", t):
            compiled.add(NS + n)
    if len(compiled) < 6:
        print(f"LINT UNMEASURED: only {len(compiled)} compiled types under {base}")
        return 2
    defs = {}
    for p in glob.glob(os.path.join(mod, "Defs", "*.xml")):
        for d in ET.parse(p).getroot():
            n = d.findtext("defName")
            if n:
                defs.setdefault(n.strip(), []).append(d)
    all_names = set()
    for p in glob.glob(os.path.join(src_root, "RimStarWars", "*", "Defs", "**", "*.xml"), recursive=True):
        try:
            for d in ET.parse(p).getroot():
                n = d.findtext("defName")
                if n:
                    all_names.add(n.strip())
        except ET.ParseError:
            pass

    # ion-def
    dmg = (defs.get("RSW_JawaIon_Damage") or [None])[0]
    if dmg is None:
        E("ion-def", "DamageDef RSW_JawaIon_Damage not found")
        return 1
    if not (dmg.get("Class") or "").endswith("IonDamageDef") or (dmg.get("Class") or "") not in compiled:
        E("ion-def", f"RSW_JawaIon_Damage Class {dmg.get('Class')} is not a compiled IonDamageDef")
    if (dmg.findtext("workerClass") or "") not in compiled:
        E("ion-def", f"workerClass {dmg.findtext('workerClass')} is not compiled by this mod")
    if (dmg.findtext("harmsHealth") or "").strip().lower() != "false":
        E("ion-def", "harmsHealth is not false: an ion hit could wound or kill (capture-not-kill)")
    emp_m, emp_d = float(dmg.findtext("empAmountMachine") or 0), float(dmg.findtext("empAmountDroid") or 0)
    dd = re.search(r"public float empAmountMachine = ([0-9.]+)f;\s*public float empAmountDroid = ([0-9.]+)f;", cs["IonDamageDef.cs"].replace("\n", " "))
    if not (emp_d > 0 and emp_m >= emp_d):
        E("ion-def", f"EMP amounts machine {emp_m} / droid {emp_d}: the machine tier must be at least the droid tier and both positive")
    if dd and (float(dd.group(1)) != 60 or float(dd.group(2)) != 24):
        W("ion-def", f"IonDamageDef code defaults {dd.groups()} differ from the 60 / 24 the spec locks")
    I("ion-def", f"stun ticks (x30, before EMP resistance): machine {emp_m * 30:.0f}, droid {emp_d * 30:.0f}; 3x3 vehicle {emp_d / 9 * 30:.0f}")
    add = dmg.findall("additionalHediffs/li")
    sev_per = 0.0
    if not add:
        E("ion-def", "no additionalHediffs entry: flesh would take no buildup at all")
    for li in add:
        h = (li.findtext("hediff") or "").strip()
        if h not in defs:
            E("ion-def", f"buildup hediff {h} is defined by no Defs file")
        fixed, per = float(li.findtext("severityFixed") or 0), float(li.findtext("severityPerDamageDealt") or 0)
        if fixed <= 0 and per <= 0:
            E("ion-def", f"buildup entry for {h} adds nothing (fixed {fixed}, per damage {per})")
        sev_per = per
    # ion-hediff
    hed = (defs.get("RSW_JawaIon_Stun") or [None])[0]
    if hed is None:
        E("ion-hediff", "HediffDef RSW_JawaIon_Stun not found")
    else:
        if float(hed.findtext("initialSeverity") or 0.5) != 0:
            E("ion-hediff", "initialSeverity is not 0: the first bolt would start at the 'overloaded' stage")
        mx = float(hed.findtext("maxSeverity") or 1)
        decay = [float(c.findtext("severityPerDay") or 0) for c in hed.iter("li") if (c.get("Class") or "").endswith("HediffCompProperties_SeverityPerDay")]
        if not decay or decay[0] >= 0:
            E("ion-hediff", "no negative severityPerDay: buildup would never bleed off")
        mins = [float(s.findtext("minSeverity") or 0) for s in hed.findall("stages/li")]
        if mins != sorted(mins) or len(set(mins)) != len(mins):
            E("ion-hediff", f"stage minSeverity {mins} not strictly ascending")
        if mins and mins[-1] >= mx:
            E("ion-hediff", f"top stage at {mins[-1]} is not below maxSeverity {mx}: unreachable")
        caps = [float(s.findtext("minSeverity") or 0) for s in hed.findall("stages/li") if any(c.findtext("capacity") == "Consciousness" and c.findtext("setMax") for c in s.iter("li"))]
        if not caps:
            E("ion-hediff", "no stage sets a Consciousness cap: a flesh target can never be downed")
        elif sev_per > 0:
            dmg_h = 8.0
            hits = math.ceil(min(caps) / (sev_per * dmg_h))
            I("ion-hediff", f"a human (size 1) at damage {dmg_h:g} is downed (cap stage {min(caps)}) after {hits} solid hits; a rat (0.2) after {math.ceil(min(caps) * 0.04 / (sev_per * dmg_h))}")
            claim = re.search(r"about (\w+) solid hits", read(os.path.join(base, "RSW_JawaIonWeaponsSettings.cs")))
            words = {"two": 2, "three": 3, "four": 4, "five": 5, "six": 6, "seven": 7, "eight": 8}
            if claim and words.get(claim.group(1)) != hits:
                W("ion-hediff", f"the Mod Settings text says 'about {claim.group(1)} solid hits on a person' but the shipped numbers (damage {dmg_h:g}, {sev_per} per damage, cap stage at {min(caps)}) down a human in {hits}: "
                                "the 0.5 'still overloaded' stage (DROIDWORKS_ION_GUARD_1) landed after the 'x6 @8' live measurement; unverified live, text left as is")
    # ion-stat
    st = (defs.get("RSW_Jawa_InverseBodySize") or [None])[0]
    if st is None:
        E("ion-stat", "StatDef RSW_Jawa_InverseBodySize not found")
    else:
        if (st.findtext("alwaysHide") or "").lower() != "true" or float(st.findtext("defaultBaseValue") or 0) != 1.0:
            E("ion-stat", "the inverse-size stat must be hidden with defaultBaseValue 1.0 (a neutral multiplier when off)")
        for li in st.iter("li"):
            if (li.get("Class") or "") and (li.get("Class") or "") not in compiled:
                E("ion-stat", f"stat part {li.get('Class')} is compiled by no assembly here")
    # ion-vehicle
    veh = cs[os.path.join("VehicleTier", "VehicleIonPatches.cs")]
    nm = re.search(r'IonDamageDefName = "(\w+)"', veh).group(1)
    if nm != "RSW_JawaIon_Damage":
        E("ion-vehicle", f"the vehicle patch looks for damage def '{nm}', the def is RSW_JawaIon_Damage")
    lf = read(os.path.join(mod, "LoadFolders.xml"))
    if "<li>/</li>" not in lf or 'IfModActive="SmashPhil.VehicleFramework">VehicleTier' not in lf:
        E("ion-vehicle", "LoadFolders must list '/' unconditionally and gate VehicleTier on SmashPhil.VehicleFramework")
    if "SmashPhil.VehicleFramework" not in read(os.path.join(mod, "About", "About.xml")):
        W("ion-vehicle", "About.xml does not mention SmashPhil.VehicleFramework (loadAfter)")
    # ion-settings
    stt = cs["RSW_JawaIonWeaponsSettings.cs"]
    init = {m.group(2): m.group(3) for m in re.finditer(r"public static (float|bool) (\w+) = ([\w.]+?)f?;", stt)}
    for m in re.finditer(r'Scribe_Values\.Look\(ref (\w+), "(\w+)", ([\w.]+?)f?\)', stt):
        fld, key, dv = m.groups()
        if key != fld:
            E("ion-settings", f"key '{key}' != field '{fld}'")
        if fld in init and init[fld] != dv:
            E("ion-settings", f"{fld} initialises to {init[fld]} but Scribes default {dv}")
    sliders = re.findall(r"(\w+) = list\.Slider\(\1, ([0-9.]+)f, ([0-9.]+)f\)", stt)
    if not sliders:
        print("LINT UNMEASURED: no sliders parsed")
        return 2
    for f, lo, hi in sliders:
        d = float(init.get(f, "nan"))
        if not float(lo) <= d <= float(hi):
            E("ion-settings", f"{f} default {d} outside its slider {lo}..{hi}")
        if f == "bodySizeResistExponent" and (float(lo) != 0 or float(hi) < 2):
            E("ion-settings", f"the exponent slider {lo}..{hi} must reach 0 (size ignored) and past the default 2")
    # ion-guard
    seen = unguarded = 0
    for p in LA.all_xml(src_root):
        if os.path.commonpath([p, mod]) == mod:
            continue
        txt = read(p)
        if NS not in txt:
            continue
        try:
            r = ET.fromstring(txt.encode("utf-8"))
        except ET.ParseError:
            continue
        pm = LA.parent_map(r)
        dep = LA.about_depends_on_armoury(LA.mod_root_of(p), PACKAGE)
        for el in r.iter():
            for v in (el.get("Class") or "", (el.text or "").strip()):
                if v in compiled:
                    seen += 1
                    if not LA.guarded(el, pm, dep, PACKAGE, "ion"):
                        unguarded += 1
                        E("ion-guard", f"{os.path.relpath(p, src_root)}: <{el.tag}> names {v} with no MayRequire {PACKAGE}")
    # ion-kernel
    kern = cs[os.path.join("Kernel", "RSW_IonBuildupKernel.cs")]
    if re.search(r"^\s*using\s+(Verse|RimWorld|UnityEngine|HarmonyLib)", kern, flags=re.M):
        E("ion-kernel", "the kernel imports Verse/RimWorld/UnityEngine/HarmonyLib (the fuzz build would break)")
    for csproj, inc in (("JawaIonWeapons.csproj", "Kernel\\RSW_IonBuildupKernel.cs"), (os.path.join("VehicleTier", "JawaIonVehicleTier.csproj"), "..\\Kernel\\RSW_IonBuildupKernel.cs"),
                        (os.path.join("SelfTest", "JawaIonWeapons.SelfTest.csproj"), "..\\Kernel\\RSW_IonBuildupKernel.cs"), (os.path.join("FuzzTest", "RimStarWarsJawaIonWeapons.Fuzz.csproj"), "..\\Kernel\\RSW_IonBuildupKernel.cs")):
        if inc not in read(os.path.join(base, csproj)):
            E("ion-kernel", f"{csproj} does not compile {inc}")
    for rel, need in (("DamageWorker_IonBuildup.cs", "RSW_IonBuildupKernel.FleshSeverity("), ("DamageWorker_IonBuildup.cs", "RSW_IonBuildupKernel.MachineAmount("),
                      ("StatPart_InverseBodySize.cs", "RSW_IonBuildupKernel.InverseSizeValue("), ("RSW_JawaIonWeaponsSettings.cs", "RSW_IonBuildupKernel.BodySizeDivisor("),
                      (os.path.join("VehicleTier", "VehicleIonPatches.cs"), "RSW_IonBuildupKernel.VehicleStunTicks(")):
        if need not in cs[rel]:
            E("ion-kernel", f"{rel} no longer calls {need}")

    for l in (errs if quiet else warns + info + errs):
        print(l)
    print(f"jawaionweapons lint: {len(compiled)} compiled types, {len(add)} buildup entries, {len(sliders)} sliders, {seen} cross-mod type uses ({unguarded} unguarded), {len(errs)} ERROR, {len(warns)} WARN")
    return 1 if errs else 0


PLANTS = [
    ("ion hits can wound", "Defs/DamageDefs_JawaIon.xml", "<harmsHealth>false</harmsHealth>", "<harmsHealth>true</harmsHealth>"),
    ("droid EMP above machine EMP", "Defs/DamageDefs_JawaIon.xml", "<empAmountDroid>24</empAmountDroid>", "<empAmountDroid>90</empAmountDroid>"),
    ("buildup hediff ghost", "Defs/DamageDefs_JawaIon.xml", "<hediff>RSW_JawaIon_Stun</hediff>", "<hediff>RSW_JawaIon_Stunn</hediff>"),
    ("buildup adds nothing", "Defs/DamageDefs_JawaIon.xml", "<severityPerDamageDealt>0.03</severityPerDamageDealt>", "<severityPerDamageDealt>0</severityPerDamageDealt>"),
    ("buildup starts overloaded", "Defs/HediffDefs_JawaIonStun.xml", "<initialSeverity>0</initialSeverity>", "<initialSeverity>0.5</initialSeverity>"),
    ("buildup never decays", "Defs/HediffDefs_JawaIonStun.xml", "<severityPerDay>-0.3</severityPerDay>", "<severityPerDay>0.3</severityPerDay>"),
    ("stat visible", "Defs/StatDefs_JawaIon.xml", "<alwaysHide>true</alwaysHide>", "<alwaysHide>false</alwaysHide>"),
    ("vehicle def name drift", "Source/VehicleTier/VehicleIonPatches.cs", 'IonDamageDefName = "RSW_JawaIon_Damage"', 'IonDamageDefName = "RSW_JawaIon_Damagee"'),
    ("vehicle folder ungated", "LoadFolders.xml", 'IfModActive="SmashPhil.VehicleFramework">VehicleTier', ">VehicleTier"),
    ("settings default drift", "Source/RSW_JawaIonWeaponsSettings.cs", 'Scribe_Values.Look(ref bodySizeResistExponent, "bodySizeResistExponent", 2f);', 'Scribe_Values.Look(ref bodySizeResistExponent, "bodySizeResistExponent", 1f);'),
    ("exponent slider cannot reach 0", "Source/RSW_JawaIonWeaponsSettings.cs", "list.Slider(bodySizeResistExponent, 0f, 3f)", "list.Slider(bodySizeResistExponent, 0.5f, 3f)"),
    ("kernel imports Verse", "Source/Kernel/RSW_IonBuildupKernel.cs", "using System;", "using System;\nusing Verse;"),
    ("vehicle assembly lost the kernel", "Source/VehicleTier/JawaIonVehicleTier.csproj", '<Compile Include="..\\Kernel\\RSW_IonBuildupKernel.cs" />', ""),
    ("worker lost its kernel", "Source/DamageWorker_IonBuildup.cs", "RSW_IonBuildupKernel.MachineAmount(", "MachineAmountX("),
]


def plant_check():
    import shutil
    import subprocess
    import tempfile
    caught = 0
    for name, rel, old, new in PLANTS:
        with tempfile.TemporaryDirectory() as td:
            dst = os.path.join(td, "RimStarWars", "JawaIonWeapons")
            shutil.copytree(os.path.join(SRC, "RimStarWars", "JawaIonWeapons"), dst, ignore=shutil.ignore_patterns("__pycache__", "Assemblies", "bin", "obj", "Textures"))
            f = os.path.join(dst, rel)
            t = open(f, encoding="utf-8").read()
            if old not in t:
                print("PLANT TARGET NOT FOUND:", name)
                continue
            open(f, "w", encoding="utf-8").write(t.replace(old, new, 1))
            r = subprocess.run([sys.executable, os.path.abspath(__file__), "--quiet", "--src-root", td], capture_output=True, text=True)
            hit = [l for l in (r.stdout + r.stderr).splitlines() if l.startswith("ERROR") or "Traceback" in l]
            print(("CAUGHT  " if hit else "MISSED  ") + name + ("  " + hit[0][:110] if hit else ""))
            caught += bool(hit)
    print(f"{caught}/{len(PLANTS)} planted defects caught")
    return 0 if caught == len(PLANTS) else 1


if __name__ == "__main__":
    if "--plant-check" in sys.argv:
        sys.exit(plant_check())
    sys.exit(main(sys.argv[1:]))
