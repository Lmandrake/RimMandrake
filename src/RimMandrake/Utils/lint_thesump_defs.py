#!/usr/bin/env python3
"""Offline lint of The Sump (mandrake.rm.thesump): the generic mod lint (lint_mod_defs.py) plus data checks the generic lint cannot see:

  ts-kethrel-stages   the shell's stage ladder is whole: the default stageLoadKg is strictly increasing; the RM_KethrelShell hediff has exactly
                      one stage per threshold plus "bare", their minSeverity is 0,1,2,... and labels equal RM_KethrelKernel.StageLabel; its
                      maxSeverity reaches (top stage + 0.01); a sprite set RM_Kethrel_Stage<n>_{north,east,south}.png exists for every stage
  ts-kethrel-settings the molt-load slider and the shipped default: the default molt load is above the top stage threshold (else the carapace
                      stage can never be worn); WARN when the slider's low end is at or below it (a setting extreme that disables stages)
  ts-kethrel-defs     pickupDefs that carry our prefix exist in a Defs folder; the tar-name test ("Tar" in the defName) is satisfied by every
                      tar terrain the biome and moat use
  ts-vault            every CompProperties_TarVaultSeal sits on a ThingDef with tickerType Normal and a storage thingClass (the engine ConfigErrors
                      says so at load; this reads it offline) and the solvent / ruined-goods defs the vault looks up by name (GetNamedSilentFail
                      degrades silently) exist
  ts-mere             the Deep Black mere gen step names biome defNames that exist, RM_TarDeep / RM_TarShallow exist, and its constants alias the kernel
  ts-kernel-pure      the kernel imports no Verse / RimWorld / UnityEngine and is listed in the csproj

    python3 src/RimMandrake/Utils/lint_thesump_defs.py [--quiet] [--mod-dir D] [--plant-check]
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
DEFAULT_MOD = os.path.join(SRC, "RimMandrake", "TheSump")


def read(p):
    return open(p, encoding="utf-8-sig").read()


def all_defnames():
    names = {}
    for p in glob.glob(os.path.join(SRC, "*", "*", "Defs", "**", "*.xml"), recursive=True) + glob.glob(os.path.join(SRC, "*", "*", "**", "Defs", "**", "*.xml"), recursive=True):
        try:
            txt = read(p)
        except OSError:
            continue
        for m in re.finditer(r"<(\w[\w.]*)(?:\s[^>]*)?>\s*<defName>([^<]+)</defName>", txt):
            names.setdefault(m.group(2).strip(), set()).add(m.group(1).split(".")[-1])
    return names


def main(argv):
    quiet = "--quiet" in argv
    mod = argv[argv.index("--mod-dir") + 1] if "--mod-dir" in argv else DEFAULT_MOD
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        rc = lint_mod_defs.run("TheSump", ["--mod-dir", mod])
    gl = buf.getvalue().splitlines()
    if rc == 2:
        print("\n".join(gl))
        return 2
    errs = [l for l in gl if l.startswith("ERROR")]
    warns = [l for l in gl if l.startswith("WARN")]
    E = lambda c, m: errs.append(f"ERROR {c}: {m}")
    W = lambda c, m: warns.append(f"WARN  {c}: {m}")
    src = os.path.join(mod, "Source")
    known = all_defnames()
    kern = read(os.path.join(src, "Kernel", "RM_SumpKernel.cs"))
    keth = read(os.path.join(src, "RM_Kethrel.cs"))
    mod_cs = read(os.path.join(src, "RM_TheSumpMod.cs"))

    # kethrel stages
    m = re.search(r"stageLoadKg = new List<float> \{([^}]*)\}", keth)
    if not m:
        print("LINT UNMEASURED: default stageLoadKg not parsed from RM_Kethrel.cs")
        return 2
    th = [float(x.strip().rstrip("f")) for x in m.group(1).split(",") if x.strip()]
    if any(b <= a for a, b in zip(th, th[1:])) or not th:
        E("ts-kethrel-stages", f"default stageLoadKg {th} is not strictly increasing")
    kx = os.path.join(mod, "Defs", "ThingDefs_Races", "RM_Kethrel.xml")
    root = ET.parse(kx).getroot()
    hed = next((d for d in root.findall("HediffDef") if d.findtext("defName") == "RM_KethrelShell"), None)
    labels = dict((int(a), b) for a, b in re.findall(r'case (\d): return "([^"]+)";', kern))
    labels[0] = re.search(r'default: return "([^"]+)";', kern).group(1)
    if hed is None:
        E("ts-kethrel-stages", "HediffDef RM_KethrelShell not found")
    else:
        stages = hed.findall("stages/li")
        if len(stages) != len(th) + 1:
            E("ts-kethrel-stages", f"the hediff has {len(stages)} stages but the comp has {len(th)} thresholds (+ bare)")
        for i, st in enumerate(stages):
            if float(st.findtext("minSeverity") or 0) != float(i):
                E("ts-kethrel-stages", f"hediff stage {i} minSeverity {st.findtext('minSeverity')} != {i} (the kernel sets severity stage + 0.01)")
            if (st.findtext("label") or "") != labels.get(i):
                E("ts-kethrel-stages", f"hediff stage {i} label '{st.findtext('label')}' != StageLabel({i}) '{labels.get(i)}'")
        mx = float(hed.findtext("maxSeverity") or 0)
        if mx < len(th) + 0.01:
            E("ts-kethrel-stages", f"maxSeverity {mx} caps the top stage's severity {len(th) + 0.01}")
    texdir = os.path.join(mod, "Textures", "Things", "Pawn", "Animal", "RM_Kethrel")
    for n in range(0, len(th) + 1):
        for side in ("north", "east", "south"):
            if not os.path.exists(os.path.join(texdir, f"RM_Kethrel_Stage{n}_{side}.png")):
                E("ts-kethrel-stages", f"missing sprite RM_Kethrel_Stage{n}_{side}.png")
    # settings
    dflt = re.search(r"public static float kethrelMoltLoadKg = ([0-9.]+)f;", mod_cs)
    slider = re.search(r"kethrelMoltLoadKg = list\.Slider\(kethrelMoltLoadKg, ([0-9.]+)f, ([0-9.]+)f\)", mod_cs)
    if not dflt or not slider:
        print("LINT UNMEASURED: kethrelMoltLoadKg default / slider not parsed")
        return 2
    d, lo, hi = float(dflt.group(1)), float(slider.group(1)), float(slider.group(2))
    if d <= th[-1]:
        E("ts-kethrel-settings", f"molt load default {d} kg <= the top stage threshold {th[-1]} kg: the full carapace is unreachable")
    if not lo <= d <= hi:
        E("ts-kethrel-settings", f"molt load default {d} outside its slider {lo}..{hi}")
    if lo <= th[-1]:
        W("ts-kethrel-settings", f"the molt-load slider goes down to {lo} kg, at or below the top stage threshold {th[-1]} kg: at that end the heavier stages can never be worn")
    for li in root.iter("li"):
        if (li.get("Class") or "").endswith("RM_CompProperties_KethrelShell"):
            for d_ in li.findall("pickupDefs/li"):
                v = (d_.text or "").strip()
                if v.startswith(("RM_", "RUT_", "RSW_")) and v not in known:
                    E("ts-kethrel-defs", f"pickupDefs names {v}, defined by no Defs folder")
    tar_terrains = [n for n, t in known.items() if "TerrainDef" in t and ("Tar" in n)]
    for need in ("RM_TarDeep", "RM_TarShallow"):
        if need not in known:
            E("ts-mere", f"{need} is defined by no Defs folder (the mere gen step silently does nothing)")
        elif not re.search("Tar", need):
            E("ts-kethrel-defs", f"{need} has no 'Tar' in its name: kethrels would not recognise it as tar")
    if not tar_terrains:
        W("ts-kethrel-defs", "no TerrainDef with 'Tar' in its name found: kethrels would find no tar")

    # vault
    for p in glob.glob(os.path.join(mod, "Defs", "**", "*.xml"), recursive=True):
        r = ET.parse(p).getroot()
        for td in r.iter("ThingDef"):
            if any((li.get("Class") or "").endswith("CompProperties_TarVaultSeal") for li in td.iter("li")):
                if (td.findtext("tickerType") or "Never") == "Never":
                    E("ts-vault", f"{td.findtext('defName')}: tickerType is not set (Never): the vault comp never ticks")
                tc = td.findtext("thingClass") or ""
                parent = td.get("ParentName")
                if "Storage" not in tc and "Shelf" not in (parent or "") and "Storage" not in (parent or "") and not tc:
                    W("ts-vault", f"{td.findtext('defName')}: thingClass not set here (inherited from {parent}); cannot confirm it is a Building_Storage")
    vault_cs = read(os.path.join(src, "RM_Comp_TarVaultSeal.cs"))
    for n in re.findall(r'GetNamedSilentFail\("([^"]+)"\)', vault_cs):
        if n not in known:
            E("ts-vault", f"the vault looks up {n} by name and no Defs folder defines it (every extraction would be ruined / nothing would ruin)")

    # mere
    gs = read(os.path.join(src, "RUT_GenStep_DeepBlackMere.cs"))
    names = re.search(r"SumpBiomeDefNames = \{([^}]*)\}", gs)
    for n in re.findall(r'"([^"]+)"', names.group(1) if names else ""):
        if n not in known:
            E("ts-mere", f"gen step gates on biome {n}, which no Defs folder defines")
    for nm in ("MinMereCells", "MaxMereCells", "MinEdgeDistance", "MaxGrowAttempts"):
        mm = re.search(r"private const int " + nm + r" = ([^;]+);", gs)
        if not mm or "RM_MereKernel." not in mm.group(1):
            E("ts-mere", f"gen step {nm} = {mm.group(1) if mm else '(missing)'} is not an alias of the kernel constant")
    # kernel
    if re.search(r"^\s*using\s+(Verse|RimWorld|UnityEngine|HarmonyLib)", kern, flags=re.M):
        E("ts-kernel-pure", "the kernel imports Verse/RimWorld/UnityEngine/HarmonyLib (the fuzz build would break)")
    if "Kernel\\RM_SumpKernel.cs" not in read(os.path.join(src, "RM_TheSump.csproj")):
        E("ts-kernel-pure", "RM_TheSump.csproj does not list Kernel\\RM_SumpKernel.cs")

    if not quiet:
        for l in warns:
            print(l)
    for l in errs:
        print(l)
    print(f"thesump lint (data): {len(th)} kethrel stages, {len(tar_terrains)} tar terrains, molt default {d} kg (slider {lo}..{hi}), {len(errs)} ERROR, {len(warns)} WARN")
    return 1 if errs else 0


PLANTS = [
    ("hediff stage dropped", "Defs/ThingDefs_Races/RM_Kethrel.xml", "<label>heavy shell</label>", "<label>heavier shell</label>"),
    ("hediff max severity", "Defs/ThingDefs_Races/RM_Kethrel.xml", "<maxSeverity>3.99</maxSeverity>", "<maxSeverity>2.5</maxSeverity>"),
    ("thresholds out of order", "Source/RM_Kethrel.cs", "{ 3f, 10f, 22f }", "{ 3f, 22f, 10f }"),
    ("molt default under the top stage", "Source/RM_TheSumpMod.cs", "public static float kethrelMoltLoadKg = 30f;", "public static float kethrelMoltLoadKg = 20f;"),
    ("vault never ticks", "Defs/ThingDefs_Buildings/RM_TarVault.xml", "<tickerType>Normal</tickerType>", ""),
    ("biome gate names a ghost", "Source/RUT_GenStep_DeepBlackMere.cs", '"RM_TheSump", "RUT_Sump"', '"RM_TheSump", "RUT_Sumpp"'),
    ("stale mere constant", "Source/RUT_GenStep_DeepBlackMere.cs", "private const int MinMereCells = RM_MereKernel.MinMereCells;", "private const int MinMereCells = 180;"),
    ("kernel imports Verse", "Source/Kernel/RM_SumpKernel.cs", "using System;", "using System;\nusing Verse;"),
    ("kernel missing from csproj", "Source/RM_TheSump.csproj", '<Compile Include="Kernel\\RM_SumpKernel.cs" />', ""),
]


def plant_check():
    import shutil
    import subprocess
    import tempfile
    caught = 0
    for name, rel, old, new in PLANTS:
        with tempfile.TemporaryDirectory() as td:
            dst = os.path.join(td, "TheSump")
            shutil.copytree(DEFAULT_MOD, dst, ignore=shutil.ignore_patterns("__pycache__", "Assemblies", "bin", "obj", "SelfTest"))
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
