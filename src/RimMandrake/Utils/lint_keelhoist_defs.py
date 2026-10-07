#!/usr/bin/env python3
"""Offline lint of KeelHoist (mandrake.rm.keelhoist): the generic mod lint (lint_mod_defs.py) plus data checks the generic lint cannot
see, because the hoist is driven from OTHER mods' XML and from settings text:

  kh-foreign-classes  every <... Class="RimMandrake.KeelHoist.X"> anywhere under src/ (the Hutt slave pit in UtinniPatches, the
                      Foundry tower patch) names a class that exists, and each child element is a public field of X or its bases
                      (an unknown child is a load error that discards the def)
  kh-odds-text        the chance-chute settings text promises "about N%" return; N equals the closed-form return of the shipped
                      defaults, the shipped defaults return < 100% and jackpot+bust sliders can never exceed 100%
  kh-restraint        RM_HoistRestraint's disappearsAfterTicks equals restraintHours default x 2500 (TryCapture overwrites it, but a
                      beast bound by another route must agree), and it still caps Moving at 0
  kh-save-keys        RM_KeelHoist.ExposeData still saves under the keys older saves used (a rename drops cargo on cable)
  kh-constants        the component's re-declared constants alias the kernel's (BaseCycleTicks, CradleRadius, Open Line rates, fighter tests)
                      and the kernel's tick constants match GenDate (2500 / 60000); the kernel is Verse-free and listed in the csproj

    python3 src/RimMandrake/Utils/lint_keelhoist_defs.py [--quiet] [--mod-dir D] [--plant-check]
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
from lint_scarlands_defs import scan_csharp, chain, Cls  # noqa: E402

REPO = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
SRC = os.path.join(REPO, "src")
DEFAULT_MOD = os.path.join(SRC, "RimMandrake", "KeelHoist")


def read(p):
    return open(p, encoding="utf-8-sig").read()


def main(argv):
    quiet = "--quiet" in argv
    mod = argv[argv.index("--mod-dir") + 1] if "--mod-dir" in argv else DEFAULT_MOD
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        rc = lint_mod_defs.run("KeelHoist", ["--mod-dir", mod])
    gl = buf.getvalue().splitlines()
    if rc == 2:
        print("\n".join(gl))
        return 2
    errs = [l for l in gl if l.startswith("ERROR")]
    warns = [l for l in gl if l.startswith("WARN")]
    E = lambda c, m: errs.append(f"ERROR {c}: {m}")
    W = lambda c, m: warns.append(f"WARN  {c}: {m}")
    src = os.path.join(mod, "Source")
    classes = scan_csharp(src)
    mod_cs = read(os.path.join(src, "KeelHoistMod.cs"))
    kernel = read(os.path.join(src, "Kernel", "RM_HoistKernel.cs"))
    hoist = read(os.path.join(src, "RM_KeelHoist.cs"))

    # foreign XML referencing our classes
    nref = nfield = 0
    foreign = argv[argv.index("--foreign-dir") + 1] if "--foreign-dir" in argv else None
    xmls = glob.glob(os.path.join(foreign, "**", "*.xml"), recursive=True) if foreign else glob.glob(os.path.join(SRC, "*", "*", "**", "*.xml"), recursive=True)
    for p in xmls:
        if os.sep + "Textures" + os.sep in p:
            continue
        try:
            txt = read(p)
        except OSError:
            continue
        if "RimMandrake.KeelHoist." not in txt:
            continue
        try:
            root = ET.fromstring(txt.encode("utf-8"))
        except ET.ParseError as e:
            E("kh-foreign-classes", f"{os.path.relpath(p, SRC)} references KeelHoist but does not parse: {e}")
            continue
        for el in root.iter():
            cls = el.get("Class")
            if not cls or not cls.startswith("RimMandrake.KeelHoist."):
                continue
            nref += 1
            short = cls.split(".")[-1]
            c = classes.get(short)
            rel = os.path.relpath(p, SRC)
            if c is None:
                E("kh-foreign-classes", f"{rel}: Class {cls} is not a class in KeelHoist/Source")
                continue
            fields = set()
            for x in chain(classes, c):
                if isinstance(x, Cls):
                    fields |= x.fields
            for ch in el:
                if ch.tag in ("li",):
                    continue
                nfield += 1
                if ch.tag not in fields:
                    E("kh-foreign-classes", f"{rel}: <{el.tag} Class=\"{cls}\"> has <{ch.tag}> but {short} (+bases) has no such public field")
    if nref == 0:
        print("LINT UNMEASURED: no foreign Class=\"RimMandrake.KeelHoist.*\" reference found (the Hutt slave pit XML moved?)")
        return 2

    # odds text vs closed form
    fields = dict((m.group(1), float(m.group(2))) for m in re.finditer(r"public static float (\w+) = ([0-9.]+)f;", mod_cs))
    jp, bust, cut = fields.get("chuteJackpotChance"), fields.get("chuteBustChance"), fields.get("chuteHouseCut")
    if None in (jp, bust, cut):
        print("LINT UNMEASURED: chute defaults not parsed from KeelHoistMod.cs")
        return 2
    ev = (jp * 3 + bust * 0.3 + (1 - jp - bust) * 0.9) * (1 - cut)
    m = re.search(r"return about (\d+)% of a stake", mod_cs)
    if not m:
        W("kh-odds-text", "the chute settings text no longer states the shipped return (about N%)")
    elif abs(int(m.group(1)) - ev * 100) > 1.0:
        E("kh-odds-text", f"settings text says about {m.group(1)}% but the shipped defaults return {ev * 100:.1f}%")
    if ev >= 1.0:
        E("kh-odds-text", f"the shipped chute odds return {ev * 100:.0f}% of the stake: the house loses")
    sl = dict((mm.group(1), (float(mm.group(2)), float(mm.group(3)))) for mm in re.finditer(r"(\w+) = (?:Mathf\.Round\()?list\.Slider\(\1, ([0-9.]+)f, ([0-9.]+)f\)", mod_cs))
    if "chuteJackpotChance" in sl and "chuteBustChance" in sl and sl["chuteJackpotChance"][1] + sl["chuteBustChance"][1] > 1.0:
        E("kh-odds-text", "jackpot + bust slider maxima exceed 100%: the middle band can vanish")
    if "chuteHouseCut" in sl and "chuteJackpotChance" in sl and "chuteBustChance" in sl:
        worst = (sl["chuteJackpotChance"][1] * 3 + sl["chuteBustChance"][0] * 0.3 + (1 - sl["chuteJackpotChance"][1] - sl["chuteBustChance"][0]) * 0.9) * (1 - sl["chuteHouseCut"][0])
        if worst > 1.0 and "past 100%" not in mod_cs:
            E("kh-odds-text", f"slider extremes can pay {worst * 100:.0f}% but the settings text no longer warns about it")

    # restraint hediff
    rh = fields.get("restraintHours")
    hx = os.path.join(mod, "Defs", "HediffDefs", "RM_HoistRestraint.xml")
    if os.path.exists(hx):
        h = ET.parse(hx).getroot().find("HediffDef")
        dis = next((e.text for e in h.iter("disappearsAfterTicks")), None)
        if rh is None or dis is None or int(rh * 2500) != int(dis):
            E("kh-restraint", f"disappearsAfterTicks {dis} != restraintHours default {rh} x 2500")
        if h.findtext(".//capMods/li/capacity") != "Moving" or h.findtext(".//capMods/li/setMax") != "0":
            E("kh-restraint", "RM_HoistRestraint no longer caps Moving at 0")

    # save keys
    expose = hoist.split("public override void ExposeData()")[1].split("public override void SpawnSetup")[0]
    keys = set(re.findall(r'"(\w+)"', expose))
    for k in ("targetPortal", "targetHolder", "targetCell", "transit", "arriveAt", "goingUp", "fromLabel", "manifest"):
        if k not in keys:
            E("kh-save-keys", f'RM_KeelHoist.ExposeData no longer saves "{k}" (cargo on an older save would be lost)')

    # constants
    for nm, want in (("BaseCycleTicks", "RM_HoistKernel.BaseCycleTicks"), ("CradleRadius", "RM_HoistKernel.CradleRadius")):
        mm = re.search(r"public const (?:int|float) " + nm + r" = ([^;]+);", hoist)
        if not mm or want not in mm.group(1):
            E("kh-constants", f"RM_KeelHoist.{nm} = {mm.group(1) if mm else '(missing)'} is not an alias of {want}")
    pat = read(os.path.join(src, "KeelHoistPatches.cs"))
    for nm, want in (("RisePerHour", "RM_HoistKernel.OpenLineRisePerHour"), ("FallPerHour", "RM_HoistKernel.OpenLineFallPerHour")):
        mm = re.search(r"public const float " + nm + r" = ([^;]+);", pat)
        if not mm or want not in mm.group(1):
            E("kh-constants", f"RM_MapComponent_OpenLine.{nm} = {mm.group(1) if mm else '(missing)'} is not an alias of {want}")
    buy = read(os.path.join(src, "RM_PitBuyer.cs"))
    for nm, want in (("MeleeFighterSkill", "RM_HoistKernel.MeleeFighterSkill"), ("BeastFighterCombatPower", "RM_HoistKernel.BeastFighterCombatPower")):
        mm = re.search(r"public const (?:int|float) " + nm + r" = ([^;]+);", buy)
        if not mm or want not in mm.group(1):
            E("kh-constants", f"RM_PitBuyerUtility.{nm} = {mm.group(1) if mm else '(missing)'} is not an alias of {want}")
    t = dict((a, int(b)) for a, b in re.findall(r"public const int (TicksPerHour|TicksPerDay)\s*=\s*(\d+);", kernel))
    if t != {"TicksPerHour": 2500, "TicksPerDay": 60000}:
        E("kh-constants", f"kernel tick constants {t} differ from GenDate (2500 / 60000)")
    if re.search(r"^\s*using\s+(Verse|RimWorld|UnityEngine|HarmonyLib)", kernel, flags=re.M):
        E("kh-constants", "the kernel imports Verse/RimWorld/UnityEngine/HarmonyLib (the fuzz build would break)")

    if not quiet:
        for l in warns:
            print(l)
    for l in errs:
        print(l)
    print(f"keelhoist lint (data): {nref} foreign Class refs, {nfield} foreign field checks, chute shipped return {ev * 100:.1f}%, "
          f"{len(errs)} ERROR, {len(warns)} WARN")
    return 1 if errs else 0


PLANTS = [
    ("hutt extension field typo", "SRC:RimUtinni/UtinniPatches/Defs/HuttSlavePit/RUT_HuttSlavePit.xml", "<holderDef>RUT_HuttSlavePitShaft</holderDef>", "<holderDeff>RUT_HuttSlavePitShaft</holderDeff>"),
    ("odds text drifts", "Source/KeelHoistMod.cs", "return about 86% of a stake", "return about 96% of a stake"),
    ("house loses", "Source/KeelHoistMod.cs", "public static float chuteJackpotChance = 0.08f;", "public static float chuteJackpotChance = 0.3f;"),
    ("restraint hours drift", "Defs/HediffDefs/RM_HoistRestraint.xml", "<disappearsAfterTicks>60000</disappearsAfterTicks>", "<disappearsAfterTicks>30000</disappearsAfterTicks>"),
    ("save key renamed", "Source/RM_KeelHoist.cs", 'Scribe_Collections.Look(ref sched.arriveAt, "arriveAt"', 'Scribe_Collections.Look(ref sched.arriveAt, "arrive"'),
    ("stale constant", "Source/RM_KeelHoist.cs", "public const int BaseCycleTicks = RM_HoistKernel.BaseCycleTicks;", "public const int BaseCycleTicks = 625;"),
    ("kernel imports Verse", "Source/Kernel/RM_HoistKernel.cs", "using System;", "using System;\nusing Verse;"),
    ("kernel missing from csproj", "Source/RM_KeelHoist.csproj", '<Compile Include="Kernel\\RM_HoistKernel.cs" />', ""),
]


def plant_check():
    import shutil
    import subprocess
    import tempfile
    caught = 0
    for name, rel, old, new in PLANTS:
        with tempfile.TemporaryDirectory() as td:
            dst = os.path.join(td, "KeelHoist")
            shutil.copytree(DEFAULT_MOD, dst, ignore=shutil.ignore_patterns("__pycache__", "Assemblies", "bin", "obj", "SelfTest"))
            if rel.startswith("SRC:"):
                # a foreign file lives outside the mod dir: plant it in a COPY and point the lint at that copy only
                f = os.path.join(SRC, rel[4:])
                orig = open(f, encoding="utf-8").read()
                if old not in orig:
                    print("PLANT TARGET NOT FOUND:", name)
                    continue
                os.makedirs(os.path.join(td, "foreign"))
                open(os.path.join(td, "foreign", "x.xml"), "w", encoding="utf-8").write(orig.replace(old, new, 1))
                r = subprocess.run([sys.executable, os.path.abspath(__file__), "--quiet", "--mod-dir", dst, "--foreign-dir", os.path.join(td, "foreign")], capture_output=True, text=True)
            else:
                f = os.path.join(dst, rel)
                t = open(f, encoding="utf-8").read()
                if old not in t:
                    print("PLANT TARGET NOT FOUND:", name)
                    continue
                open(f, "w", encoding="utf-8").write(t.replace(old, new, 1))
                r = subprocess.run([sys.executable, os.path.abspath(__file__), "--quiet", "--mod-dir", dst], capture_output=True, text=True)
            hit = [l for l in (r.stdout + r.stderr).splitlines() if l.startswith("ERROR") or "Traceback" in l]
            print(("CAUGHT  " if hit else "MISSED  ") + name + ("  " + hit[0][:100] if hit else ""))
            caught += bool(hit)
    print(f"{caught}/{len(PLANTS)} planted defects caught")
    return 0 if caught == len(PLANTS) else 1


if __name__ == "__main__":
    if "--plant-check" in sys.argv:
        sys.exit(plant_check())
    sys.exit(main(sys.argv[1:]))
