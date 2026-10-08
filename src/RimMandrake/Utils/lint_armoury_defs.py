#!/usr/bin/env python3
"""Offline lint of Jawa Armoury (mandrake.rsw.armoury): the generic mod lint (lint_mod_defs.py) plus data checks the generic lint cannot see.
The generic lint only resolves RM_/RUT_/RSW_ classes; Armoury's classes keep their donor names (guy762_Ionization, KoltoTank, ...), so it
reports them as unwired. Those warnings are re-verified here against the XML and dropped only with proof.

  ar-guard        a def OUTSIDE Armoury that names a type compiled into JawaArmoury.dll (Class=, workerClass, genStep ...) must be guarded: a
                  MayRequire naming mandrake.rsw.armoury on the element or an ancestor, a PatchOperationFindMod for Armoury above it, or the
                  mod's own About.xml depending on Armoury. An unguarded use is a config error ("can't find class") the moment Armoury is off
  ar-ion          every ModExtension_HediffGiver: only fields the class has, the hediff exists, positive fixed severity; WARN when the owning
                  DamageDef's worker is not one that reads the extension (the extension then does nothing)
  ar-blocker      every ModExtension_MentalBreakBlocker: cause is an enum member; WARN on `anyway` (0 = blocks nothing as a blacklist)
  ar-yield        every ModExtension_SecondaryMineableYield: drop chance in (0,1], entries have weight >= 0 and a positive total, yield >= 1
  ar-kolto        the tank comp: body-size band ordered, fill speed in (0,1], multiplier > 0, entry / exit hediffs exist; state enum order = kernel
  ar-settings     every slider holds its default; derived shipped numbers (emergency heal 20000 / 2500 ticks, kolto 2.5 h) match the kernel
  ar-kernel       the kernel imports no Verse / RimWorld / UnityEngine, is in the csproj, and the call sites alias its constants

    python3 src/RimMandrake/Utils/lint_armoury_defs.py [--quiet] [--mod-dir D] [--plant-check]
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
DEFAULT_MOD = os.path.join(SRC, "RimStarWars", "Armoury")
PACKAGE = "mandrake.rsw.armoury"
ION_WORKERS_THAT_READ = {"DamageWorker_Humanlikes", "DamageWorker_Animals", "DamageWorker_Insectoids", "DamageWorker_Mechanoids", "DamageWorker_Organics",
                         "DamageWorker_Ionization", "DamageWorker_Ionize", "DamageWorker_AllDroids"}
HG_FIELDS = {"hediffToAdd", "hediffResistanceStat", "severityFixed", "severityVariesBySize", "hediffAppliedToWholeBody"}


def read(p):
    return open(p, encoding="utf-8-sig").read()


def strip_cs(t):
    t = re.sub(r"/\*.*?\*/", "", t, flags=re.S)
    return re.sub(r"//[^\n]*", "", t)


def all_xml(root):
    return sorted(glob.glob(os.path.join(root, "**", "*.xml"), recursive=True))


def defnames_by_type(mod):
    names = {}
    for p in glob.glob(os.path.join(SRC, "*", "*", "Defs", "**", "*.xml"), recursive=True) + glob.glob(os.path.join(SRC, "*", "*", "*", "Defs", "**", "*.xml"), recursive=True):
        try:
            r = ET.parse(p).getroot()
        except ET.ParseError:
            continue
        for d in r:
            n = d.findtext("defName")
            if n:
                names.setdefault(n.strip(), set()).add(d.tag)
    return names


def compiled_types(mod):
    """namespace.Class for every class in the sources the csproj compiles."""
    out = set()
    for p in glob.glob(os.path.join(mod, "Source", "**", "*.cs"), recursive=True):
        if os.sep + "SelfTest" + os.sep in p or os.sep + "obj" + os.sep in p:
            continue
        t = strip_cs(read(p))
        ns = re.search(r"namespace\s+([\w.]+)", t)
        if not ns:
            continue
        for m in re.finditer(r"\b(?:public|internal)\s+(?:static\s+|abstract\s+|sealed\s+)*(?:class|enum|struct)\s+(\w+)", t):
            out.add(ns.group(1) + "." + m.group(1))
    return out


def parent_map(root):
    return {c: p for p in root.iter() for c in p}


def guarded(el, pm, about_depends, package=PACKAGE, namekey="armoury"):
    if about_depends:
        return True
    cur = el
    while cur is not None:
        if package in (cur.get("MayRequire") or "").lower():
            return True
        if (cur.get("Class") or "").endswith("PatchOperationFindMod"):
            if any(namekey in (li.text or "").lower() for li in cur.findall("mods/li")):
                return True
        cur = pm.get(cur)
    return False


def mod_root_of(path):
    parts = os.path.relpath(path, SRC).split(os.sep)
    return os.path.join(SRC, parts[0], parts[1])


def about_depends_on_armoury(modroot, package=PACKAGE, cache={}):
    if (modroot, package) in cache:
        return cache[(modroot, package)]
    ab = os.path.join(modroot, "About", "About.xml")
    ok = False
    if os.path.exists(ab):
        try:
            r = ET.parse(ab).getroot()
            ok = any(package in (li.findtext("packageId") or "").lower() for li in r.findall("modDependencies/li"))
        except ET.ParseError:
            pass
    cache[(modroot, package)] = ok
    return ok


def main(argv):
    global SRC
    quiet = "--quiet" in argv
    if "--src-root" in argv:
        SRC = argv[argv.index("--src-root") + 1]
    mod = argv[argv.index("--mod-dir") + 1] if "--mod-dir" in argv else os.path.join(SRC, "RimStarWars", "Armoury")
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        rc = lint_mod_defs.run("Armoury", ["--mod-dir", mod])
    gl = buf.getvalue().splitlines()
    if rc == 2:
        print("\n".join(gl))
        return 2
    errs = [l for l in gl if l.startswith("ERROR")]
    warns = []
    E = lambda c, m: errs.append(f"ERROR {c}: {m}")
    W = lambda c, m: warns.append(f"WARN  {c}: {m}")
    src = os.path.join(mod, "Source")
    known = defnames_by_type(mod)
    xml_text = {p: read(p) for p in all_xml(mod)}
    types = compiled_types(mod)
    if len(types) < 40:
        print(f"LINT UNMEASURED: only {len(types)} compiled types found in {src}")
        return 2

    # re-verify the generic lint's warnings that come from Armoury's un-prefixed names
    dropped = 0
    for l in gl:
        if not l.startswith("WARN"):
            continue
        m = re.match(r"WARN\s+wired: \w+ subclass (\w+) ", l)
        if m:
            name = m.group(1)
            hit = any(re.search(r"\b" + name + r"\b", re.sub(r"<!--.*?-->", "", t, flags=re.S)) for t in list(xml_text.values()) + [read(p) for p in all_xml(os.path.join(SRC, "RimUtinni"))[:0]])
            if hit:
                dropped += 1
                continue
        m = re.match(r"WARN\s+settings-scribed: settings field (\w+) is never read", l)
        if m:
            f = m.group(1)
            sp = os.path.join(src, "RSW_ArmourySettings.cs")
            lines = strip_cs(read(sp)).splitlines()
            member = None
            for i, ln in enumerate(lines):
                if re.search(r"\b" + f + r"\b", ln) and not re.search(r"Scribe_Values|list\.Slider|list\.Label|list\.Checkbox|public static (float|bool|int) " + f, ln):
                    for j in range(i, -1, -1):
                        mm = re.search(r"public static \w+ (\w+)\s*(?:=>|\()", lines[j])
                        if mm:
                            member = mm.group(1)
                            break
            if member and any(re.search(r"\b" + member + r"\b", strip_cs(read(p))) for p in glob.glob(os.path.join(src, "**", "*.cs"), recursive=True) if not p.endswith("RSW_ArmourySettings.cs")):
                dropped += 1
                continue
        warns.append(l)

    # ar-guard
    unguarded = 0
    seen = 0
    short = {t.split(".")[-1]: t for t in types}
    for p in all_xml(SRC):
        if os.path.commonpath([p, mod]) == mod:
            continue
        txt = read(p)
        if not any(t in txt for t in types):
            continue
        try:
            root = ET.fromstring(txt.encode("utf-8"))
        except ET.ParseError:
            continue
        pm = parent_map(root)
        dep = about_depends_on_armoury(mod_root_of(p))
        for el in root.iter():
            txt_v = (el.text or "").strip()
            vals = [el.get("Class") or "", txt_v]
            if el.tag.endswith("Class") or el.tag in ("genStep", "driverClass"):
                vals.append(short.get(txt_v, ""))
            for v in vals:
                if v in types:
                    seen += 1
                    if not guarded(el, pm, dep):
                        unguarded += 1
                        E("ar-guard", f"{os.path.relpath(p, SRC)}: <{el.tag}> names {v} (compiled in Armoury) with no MayRequire {PACKAGE}, no FindMod and no About dependency")
    # ar-ion
    pm_cache = {}
    n_ion = n_blk = n_yield = n_kolto = 0
    enum_names = set(re.findall(r"^\s*(\w+)\s*=\s*\d+", strip_cs(read(os.path.join(src, "MentalBreakBlocker", "BlockMentalBreakCause.cs"))), flags=re.M))
    for p in all_xml(SRC):
        txt = read(p)
        if "ModExtension_" not in txt and "KoltoTank." not in txt:
            continue
        try:
            root = ET.fromstring(txt.encode("utf-8"))
        except ET.ParseError:
            continue
        pm = parent_map(root)
        rel = os.path.relpath(p, SRC)
        for el in root.iter("li"):
            cls = el.get("Class") or ""
            owner = pm.get(pm.get(el))
            oname = (owner.findtext("defName") if owner is not None else None) or "?"
            if cls == "guy762_Ionization.ModExtension_HediffGiver":
                n_ion += 1
                for ch in el:
                    if ch.tag not in HG_FIELDS:
                        E("ar-ion", f"{rel}: {oname}: unknown field <{ch.tag}> on ModExtension_HediffGiver")
                h = (el.findtext("hediffToAdd") or "").strip()
                if not h:
                    E("ar-ion", f"{rel}: {oname}: no hediffToAdd (the worker then does nothing)")
                elif h not in known:
                    W("ar-ion", f"{rel}: {oname}: hediffToAdd {h} is defined by no Defs folder here (vanilla / donor?)")
                sev = el.findtext("severityFixed")
                if sev is not None and float(sev) <= 0:
                    E("ar-ion", f"{rel}: {oname}: severityFixed {sev} adds nothing")
                if owner is not None and owner.tag == "DamageDef":
                    wc = (owner.findtext("workerClass") or "").strip().split(".")[-1]
                    if wc not in ION_WORKERS_THAT_READ:
                        redundant = wc == "DamageWorker_AddGlobal" and (owner.findtext("hediff") or "").strip() == h
                        W("ar-ion", f"{rel}: DamageDef {oname} has workerClass {wc or '(default)'}, which never reads ModExtension_HediffGiver: the extension does nothing"
                          + (" (harmless: AddGlobal already adds the def's own <hediff>)" if redundant else ""))
            elif cls == "MentalBreakBlocker.ModExtension_MentalBreakBlocker":
                n_blk += 1
                c = (el.findtext("cause") or "all").strip()
                if c not in enum_names:
                    E("ar-blocker", f"{rel}: {oname}: cause {c} is not a BlockMentalBreakCause member")
                if c == "anyway":
                    W("ar-blocker", f"{rel}: {oname}: cause anyway (0) blocks NOTHING as a blacklist and everything as a whitelist")
            elif cls == "SecondaryMineableYield.ModExtension_SecondaryMineableYield":
                n_yield += 1
                dc = float(el.findtext("mineableDropChance") or 1)
                if not 0 < dc <= 1:
                    E("ar-yield", f"{rel}: {oname}: mineableDropChance {dc} outside (0,1]")
                total = 0.0
                entries = el.findall("entries/li")
                for e in entries:
                    w = float(e.findtext("randomWeight") or 1)
                    if w < 0:
                        E("ar-yield", f"{rel}: {oname}: negative randomWeight {w}")
                    total += max(w, 0)
                    if int(float(e.findtext("mineableYield") or 1)) < 1:
                        E("ar-yield", f"{rel}: {oname}: mineableYield under 1")
                    if not (e.findtext("mineableThing") or "").strip():
                        E("ar-yield", f"{rel}: {oname}: an entry names no mineableThing")
                if not entries or total <= 0:
                    E("ar-yield", f"{rel}: {oname}: no entries or zero total weight: the bonus can never drop")
            elif cls == "KoltoTank.CompProperties_KoltoTank":
                n_kolto += 1
                lo, hi = float(el.findtext("bodySizeMin") or 0), float(el.findtext("bodySizeMax") or 0)
                if lo > hi:
                    E("ar-kolto", f"{rel}: {oname}: bodySizeMin {lo} > bodySizeMax {hi}: no pawn fits")
                fs = float(el.findtext("waterfillspeed") or 0.01)
                if not 0 < fs <= 1:
                    E("ar-kolto", f"{rel}: {oname}: waterfillspeed {fs} outside (0,1]: the tank never fills or fills in one tick")
                if float(el.findtext("multiplier") or 0) <= 0:
                    W("ar-kolto", f"{rel}: {oname}: multiplier not positive: the tank heals on the plain 2500-tick hour")
                for f in ("hediffOnEntry", "hediffOnExit"):
                    v = (el.findtext(f) or "").strip()
                    if v and v not in known:
                        E("ar-kolto", f"{rel}: {oname}: {f} {v} is defined by no Defs folder (AddHediff(null) at runtime)")
    kc = strip_cs(read(os.path.join(src, "KoltoTank", "Building_KoltoTank.cs")))
    en = re.search(r"enum KoltoTankState\s*\{([^}]*)\}", kc)
    order = [x.strip() for x in en.group(1).split(",") if x.strip()] if en else []
    if order != ["Empty", "StartFilling", "Full"]:
        E("ar-kolto", f"KoltoTankState is {order}; the kernel numbers Empty=0 StartFilling=1 Full=2")
    bl = strip_cs(read(os.path.join(src, "MentalBreakBlocker", "BlockMentalBreakCause.cs")))
    vals = {a: int(b) for a, b in re.findall(r"(\w+)\s*=\s*(\d+)", bl)}
    if vals.get("mood") != 1 or vals.get("damage") != 2 or vals.get("psycast") != 4 or vals.get("all") != 7:
        E("ar-blocker", f"BlockMentalBreakCause bits {vals} differ from the kernel's mood=1 damage=2 psycast=4 all=7")

    # ar-settings
    sp = strip_cs(read(os.path.join(src, "RSW_ArmourySettings.cs")))
    defaults = {m.group(2): float(m.group(3)) if m.group(1) != "bool" else m.group(3) for m in re.finditer(r"public static (float|bool) (\w+) = ([\w.]+?)f?;", sp)}
    sliders = re.findall(r"(\w+) = list\.Slider\(\1, ([0-9.]+)f, ([0-9.]+)f\)", sp)
    if not defaults or not sliders:
        print("LINT UNMEASURED: settings defaults / sliders not parsed")
        return 2
    for f, lo, hi in sliders:
        d = defaults.get(f)
        if d is None:
            E("ar-settings", f"slider {f} has no static default")
        elif not float(lo) <= d <= float(hi):
            E("ar-settings", f"{f} default {d} outside its slider {lo}..{hi}")
    kern = read(os.path.join(src, "Kernel", "RSW_ArmouryKernel.cs"))
    th = float(re.search(r"TicksPerHour = ([0-9.]+)f", kern).group(1))
    if round(defaults["instantHealReuseHours"] * th) != 20000 or round(defaults["instantHealRecentHarmHours"] * th) != 2500:
        E("ar-settings", f"shipped emergency-heal defaults give {round(defaults['instantHealReuseHours'] * th)} / {round(defaults['instantHealRecentHarmHours'] * th)} ticks, not 20000 / 2500")
    lo_h = [float(lo) for f, lo, hi in sliders if f == "instantHealRecentHarmHours"]
    if lo_h and round(lo_h[0] * th) < 1:
        E("ar-settings", "the recent-harm slider can reach 0 ticks")
    if "TicksPerHour = 2500f" not in sp:
        E("ar-settings", "RSW_ArmourySettings.TicksPerHour is not 2500f (the kernel's hour)")

    # ar-kernel
    if re.search(r"^\s*using\s+(Verse|RimWorld|UnityEngine|HarmonyLib)", kern, flags=re.M):
        E("ar-kernel", "the kernel imports Verse/RimWorld/UnityEngine/HarmonyLib (the fuzz build would break)")
    if "Kernel\\RSW_ArmouryKernel.cs" not in read(os.path.join(src, "JawaArmoury.csproj")):
        E("ar-kernel", "JawaArmoury.csproj does not list Kernel\\RSW_ArmouryKernel.cs")
    jg = strip_cs(read(os.path.join(src, "JumppackForMeleeAI", "JobGiver_AIMeleeJumppack.cs")))
    if "minTargetDistance = RSW_CombatKernel.MeleeJumpMinDistSq" not in jg:
        E("ar-kernel", "JobGiver_AIMeleeJumppack.minTargetDistance is not the kernel constant")
    cd = strip_cs(read(os.path.join(src, "SelfHediffVerb", "CompVerbWithCooltime.cs")))
    if "RSW_GearKernel.Tick(" not in cd or "RSW_GearKernel.AfterUse(" not in cd:
        E("ar-kernel", "CompVerbWithCooltime does not call the cooldown kernel")
    for rel, need in (("guy762_Ionization/DamageWorker_RaceHediffBase.cs", "RSW_IonKernel.Decide("), ("guy762_IonizationABF/DamageWorker_Ionize.cs", "RSW_IonKernel.Decide("),
                      ("SecondaryMineableYield/SecondaryMineableYield.cs", "RSW_YieldKernel.Pick("), ("KoltoTank/Building_KoltoTank.cs", "RSW_KoltoKernel.Step(")):
        if need not in read(os.path.join(src, *rel.split("/"))):
            E("ar-kernel", f"{rel} no longer calls {need}")

    if not quiet:
        for l in warns:
            print(l)
    for l in errs:
        print(l)
    print(f"armoury lint (data): {len(types)} compiled types, {seen} cross-mod type uses ({unguarded} unguarded), {n_ion} ion extensions, {n_blk} blockers, {n_yield} yield tables, {n_kolto} tank comps, "
          f"{len(sliders)} sliders, {dropped} generic warnings re-verified and dropped, {len(errs)} ERROR, {len(warns)} WARN")
    return 1 if errs else 0


PLANTS = [
    ("unguarded cross-mod use", "RimStarWars/StarWarsRaces/Defs/Misc/SW_Support.xml", ' MayRequire="mandrake.rsw.armoury">', ">", True),
    ("kolto band inverted", "Defs/Absorbed_KotorCore/ThingDefs_Resources/Absorbed_KotorCore_KotORResource_Kolto.xml", "<bodySizeMax>2</bodySizeMax>", "<bodySizeMax>-1</bodySizeMax>", False),
    ("kolto never fills", "Defs/Absorbed_KotorCore/ThingDefs_Resources/Absorbed_KotorCore_KotORResource_Kolto.xml", "<waterfillspeed>0.005</waterfillspeed>", "<waterfillspeed>0</waterfillspeed>", False),
    ("kolto entry hediff ghost", "Defs/Absorbed_KotorCore/ThingDefs_Resources/Absorbed_KotorCore_KotORResource_Kolto.xml", "<hediffOnEntry>KoltoTank_Coma</hediffOnEntry>", "<hediffOnEntry>KoltoTank_Comaa</hediffOnEntry>", False),
    ("blocker cause typo", "Defs/Absorbed_KotorCore/ThingDefs_WeaponsArmorsGadgets/Absorbed_KotorCore_GadgetApparel_SWBelts.xml", "<cause>moodAndDamage</cause>", "<cause>moodAndDamge</cause>", False),
    ("state enum reordered", "Source/KoltoTank/Building_KoltoTank.cs", "Empty,\n        StartFilling,\n        Full", "StartFilling,\n        Empty,\n        Full", False),
    ("slider default outside range", "Source/RSW_ArmourySettings.cs", "public static float koltoHealSpeed = 1f;", "public static float koltoHealSpeed = 9f;", False),
    ("emergency heal default drifted", "Source/RSW_ArmourySettings.cs", "public static float instantHealReuseHours = 8f;", "public static float instantHealReuseHours = 4f;", False),
    ("kernel imports Verse", "Source/Kernel/RSW_ArmouryKernel.cs", "using System;", "using System;\nusing Verse;", False),
    ("kernel missing from csproj", "Source/JawaArmoury.csproj", '<Compile Include="Kernel\\RSW_ArmouryKernel.cs" />', "", False),
    ("jobgiver constant drifted", "Source/JumppackForMeleeAI/JobGiver_AIMeleeJumppack.cs", "minTargetDistance = RSW_CombatKernel.MeleeJumpMinDistSq;", "minTargetDistance = 25f;", False),
]


def plant_check():
    import shutil
    import subprocess
    import tempfile
    caught = 0
    done = 0
    for name, rel, old, new, outside in PLANTS:
        done += 1
        with tempfile.TemporaryDirectory() as td:
            dst = os.path.join(td, "RimStarWars", "Armoury")
            shutil.copytree(DEFAULT_MOD, dst, ignore=shutil.ignore_patterns("__pycache__", "Assemblies", "bin", "obj", "SelfTest", "Textures", "_artsrc", "Sounds", "Languages"))
            if outside:
                srcf = os.path.join(SRC, *rel.split("/"))
                f = os.path.join(td, *rel.split("/"))
                os.makedirs(os.path.dirname(f), exist_ok=True)
                shutil.copy2(srcf, f)
            else:
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
    print(f"{caught}/{done} planted defects caught")
    return 0 if caught == done else 1


if __name__ == "__main__":
    if "--plant-check" in sys.argv:
        sys.exit(plant_check())
    sys.exit(main(sys.argv[1:]))
