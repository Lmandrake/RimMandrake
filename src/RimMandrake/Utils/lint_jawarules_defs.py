#!/usr/bin/env python3
"""Offline lint of JawaRules (mandrake.rsw.jawarules): the XML it ships (the always-on hood node patch, the kept-hood marker) and the C# it
compiles, plus the cross-file facts the hood rule leans on. The shared generic lint resolves only src/RimMandrake classes and expects Defs/,
so this tool carries its own checks:

  jr-hood      the patch names classes that exist in this assembly, targets a GeneDef and a hood ThingDef that exist, the fallback node draws
               below ordinary headgear (baseLayer 65 under 71 / 90) and its texture exists on disk; the kept-hood marker is a DefModExtension
  jr-flags     the kernel's flag constants are the measured engine bits (Headgear 0x20, Clothes 0x40; the source comment cites them) and the C#
               ApparelFlags is exactly Clothes | Headgear
  jr-xenotype  the Jawa xenotype name the mod compares against is defined
  jr-labels    the world-label transpiler constants (0.3 / 0.6, 0.4 / 1.5, four lift hits) match the settings defaults the sliders start at
  jr-settings  each Scribe default equals its field initializer, key = field
  jr-guard     a def outside JawaRules naming a JawaRules class is guarded (MayRequire mandrake.rsw.jawarules / FindMod / About dependency)
  jr-patches   every Harmony target the static constructor resolves is listed (the names cannot be checked against the engine offline: UNMEASURED
               for the engine side, printed so a game update has a checklist)
  jr-kernel    the kernel imports no Verse / RimWorld / UnityEngine / HarmonyLib, is in the csproj, and the patches call it

    python3 src/RimMandrake/Utils/lint_jawarules_defs.py [--quiet] [--src-root D] [--plant-check]
"""
import glob
import os
import re
import sys
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import lint_armoury_defs as LA  # noqa: E402

REPO = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
SRC = os.path.join(REPO, "src")
PACKAGE = "mandrake.rsw.jawarules"
NS = "RimMandrake.StarWars.JawaRules."


def read(p):
    return open(p, encoding="utf-8-sig").read()


def main(argv):
    quiet = "--quiet" in argv
    src_root = argv[argv.index("--src-root") + 1] if "--src-root" in argv else SRC
    mod = os.path.join(src_root, "RimStarWars", "JawaRules")
    base = os.path.join(mod, "Source")
    errs, warns, info = [], [], []
    E = lambda c, m: errs.append(f"ERROR {c}: {m}")
    W = lambda c, m: warns.append(f"WARN  {c}: {m}")
    I = lambda c, m: info.append(f"INFO  {c}: {m}")
    cs = {os.path.relpath(p, base): LA.strip_cs(read(p)) for p in glob.glob(os.path.join(base, "*.cs")) + glob.glob(os.path.join(base, "Kernel", "*.cs"))}
    compiled = set()
    for rel, t in cs.items():
        for n in re.findall(r"\b(?:public|internal)\s+(?:static\s+|abstract\s+|sealed\s+)*(?:class|enum|struct)\s+(\w+)", t):
            compiled.add(NS + n)
    csproj = read(os.path.join(base, "JawaRules.csproj"))
    if len(compiled) < 12:
        print(f"LINT UNMEASURED: only {len(compiled)} compiled types under {base}")
        return 2
    for rel in cs:
        if rel.endswith(".cs") and "EnableDefaultCompileItems>false" in csproj and rel.replace("/", "\\") not in csproj:
            E("jr-kernel", f"{rel} is not in JawaRules.csproj (compiles into nothing)")
    kern = cs[os.path.join("Kernel", "RSW_JawaRulesKernel.cs")]

    # jr-hood
    patch = os.path.join(mod, "Patches", "RSW_JawaHood.xml")
    ptxt = read(patch)
    root = ET.fromstring(ptxt.encode("utf-8"))
    for m in re.finditer(r"(?:Class=\"|<workerClass>)(RimMandrake\.StarWars\.JawaRules\.\w+)", ptxt):
        if m.group(1) not in compiled:
            E("jr-hood", f"the patch names {m.group(1)}, which this assembly does not compile")
    all_defs = {}
    for p in glob.glob(os.path.join(src_root, "RimStarWars", "**", "*.xml"), recursive=True):
        try:
            r = ET.parse(p).getroot()
        except ET.ParseError:
            continue
        for d in r:
            n = d.findtext("defName")
            if n:
                all_defs.setdefault(n.strip(), set()).add(d.tag)
    gene = re.search(r'Defs/GeneDef\[defName="(\w+)"\]', ptxt).group(1)
    hood = re.search(r'Defs/ThingDef\[defName="(\w+)"\]', ptxt).group(1)
    if "GeneDef" not in all_defs.get(gene, ()):
        E("jr-hood", f"the patch targets GeneDef {gene}, defined by no Defs folder")
    if "ThingDef" not in all_defs.get(hood, ()):
        E("jr-hood", f"the patch targets ThingDef {hood}, defined by no Defs folder")
    layer = re.search(r"<baseLayer>(\d+)</baseLayer>", ptxt)
    if not layer or int(layer.group(1)) >= 71:
        E("jr-hood", f"the fallback hood's baseLayer {layer.group(1) if layer else '(none)'} must stay under ordinary headgear (71)")
    tex = re.search(r"<texPath>([^<]+)</texPath>", ptxt).group(1)
    found = glob.glob(os.path.join(src_root, "RimStarWars", "*", "Textures", *tex.split("/")) + "*.png")
    if not found:
        E("jr-hood", f"the fallback hood texture {tex} exists in no Textures folder (a bare Jawa head, magenta)")
    if "DefModExtension" not in cs["Patch_JawaHoodSwimming.cs"].split("class RSW_KeepHoodWhileSwimming")[1][:40]:
        E("jr-hood", "RSW_KeepHoodWhileSwimming is not a DefModExtension")
    # jr-flags
    km = dict(re.findall(r"public const int Headgear = (0x[0-9A-Fa-f]+), Clothes = (0x[0-9A-Fa-f]+)", kern) and [("Headgear", re.search(r"Headgear = (0x[0-9A-Fa-f]+)", kern).group(1)), ("Clothes", re.search(r"Clothes = (0x[0-9A-Fa-f]+)", kern).group(1))])
    swim_src = read(os.path.join(base, "Patch_JawaHoodSwimming.cs"))
    if int(km.get("Headgear", "0"), 16) != 0x20 or int(km.get("Clothes", "0"), 16) != 0x40:
        E("jr-flags", f"kernel flag bits {km} differ from the measured engine bits (Headgear 0x20, Clothes 0x40)")
    if "Headgear 0x20" not in swim_src or "Clothes 0x40" not in swim_src:
        W("jr-flags", "the source comment no longer cites the measured bits Headgear 0x20 / Clothes 0x40")
    if "ApparelFlags = PawnRenderFlags.Clothes | PawnRenderFlags.Headgear" not in re.sub(r"\s+", " ", swim_src):
        E("jr-flags", "JawaHoodRender.ApparelFlags is not Clothes | Headgear")
    # jr-xenotype
    xeno = re.search(r'JawaXenotype = "(\w+)"', cs["JawaRules.cs"]).group(1)
    if "XenotypeDef" not in all_defs.get(xeno, ()):
        E("jr-xenotype", f"the Jawa xenotype {xeno} is defined by no Defs folder: the no-sow rule can never match")
    # jr-labels
    jr = cs["JawaRules.cs"]; st = cs["RSW_JawaRulesSettings.cs"]
    consts = {k: float(v) for k, v in re.findall(r"public const float (\w+) = ([0-9.]+)f;", jr)}
    defaults = {k: float(v) for k, v in re.findall(r"public static float (\w+) = ([0-9.]+)f;", st)}
    if consts.get("WantedAlpha") != defaults.get("worldLabelAlpha") or consts.get("WantedLift") != defaults.get("worldLabelLift"):
        E("jr-labels", f"the wanted constants {consts} differ from the settings defaults {defaults}")
    if consts.get("VanillaAlpha") != 0.3 or consts.get("VanillaLift") != 0.4:
        E("jr-labels", f"vanilla constants {consts}: the transpiler matches ldc.r4 0.3 (alpha) and 0.4 (lift) in the engine")
    if "ExpectedHits = 4" not in jr:
        E("jr-labels", "the lift transpiler no longer expects four 0.4 constants")
    # jr-settings
    init = {m.group(2): m.group(3) for m in re.finditer(r"public static (float|bool) (\w+) = ([\w.]+?)f?;", st)}
    for m in re.finditer(r'Scribe_Values\.Look\(ref (\w+), "(\w+)", ([\w.]+?)f?\)', st):
        fld, key, dv = m.groups()
        if key != fld:
            E("jr-settings", f"key '{key}' != field '{fld}'")
        if fld in init and init[fld] != dv:
            E("jr-settings", f"{fld} initialises to {init[fld]} but Scribes default {dv}")
    # jr-guard
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
                    if not LA.guarded(el, pm, dep, PACKAGE, "jawa"):
                        unguarded += 1
                        E("jr-guard", f"{os.path.relpath(p, src_root)}: <{el.tag}> names {v} with no MayRequire {PACKAGE}")
    # jr-patches
    targets = re.findall(r"AccessTools\.(?:Method|PropertyGetter)\(typeof\((\w+(?:_\w+)?)\)\s*,\s*(?:nameof\(\w+\.(\w+)\)|\"(\w+)\")", cs["JawaRules.cs"])
    I("jr-patches", "Harmony targets (UNMEASURED against the engine offline): " + ", ".join(f"{a}.{b or c}" for a, b, c in targets))
    # jr-kernel
    if re.search(r"^\s*using\s+(Verse|RimWorld|UnityEngine|HarmonyLib)", kern, flags=re.M):
        E("jr-kernel", "the kernel imports Verse/RimWorld/UnityEngine/HarmonyLib (the fuzz build would break)")
    if "Kernel\\RSW_JawaRulesKernel.cs" not in csproj:
        E("jr-kernel", "JawaRules.csproj does not list Kernel\\RSW_JawaRulesKernel.cs")
    for rel, need in (("Patch_JawaHoodSwimming.cs", "RSW_HoodKernel.Postfix("), ("PawnRenderNodeWorker_JawaHoodFallback.cs", "RSW_HoodKernel.FallbackDraws("),
                      ("PawnRenderNodeWorker_JawaHoodFallback.cs", "RSW_HoodKernel.RealHoodIsDrawing("), ("JawaRules.cs", "RSW_RulesKernel.SowResult("),
                      ("JawaRules.cs", "RSW_RulesKernel.NeedsPetName("), ("JawaRules.cs", "RSW_RulesKernel.ForceKind("), ("RSW_JawaRulesSettings.cs", "RSW_RulesKernel.Current(")):
        if need not in cs[rel]:
            E("jr-kernel", f"{rel} no longer calls {need}")

    for l in (errs if quiet else warns + info + errs):
        print(l)
    print(f"jawarules lint: {len(compiled)} compiled types, {seen} cross-mod type uses ({unguarded} unguarded), {len(targets)} Harmony targets, {len(errs)} ERROR, {len(warns)} WARN")
    return 1 if errs else 0


PLANTS = [
    ("patch names a ghost class", "Patches/RSW_JawaHood.xml", "PawnRenderNodeWorker_JawaHoodFallback</workerClass>", "PawnRenderNodeWorker_JawaHoodFallbak</workerClass>"),
    ("patch targets a ghost gene", "Patches/RSW_JawaHood.xml", 'Defs/GeneDef[defName="RSW_Jawa_Head_Plain"]/renderNodeProperties', 'Defs/GeneDef[defName="RSW_Jawa_Head_Plainn"]/renderNodeProperties'),
    ("fallback hood over headgear", "Patches/RSW_JawaHood.xml", "<baseLayer>65</baseLayer>", "<baseLayer>80</baseLayer>"),
    ("fallback texture ghost", "Patches/RSW_JawaHood.xml", "SWApparel/Robes/jawa/hood</texPath>", "SWApparel/Robes/jawa/hoodd</texPath>"),
    ("kernel flag bits drift", "Source/Kernel/RSW_JawaRulesKernel.cs", "Headgear = 0x20, Clothes = 0x40", "Headgear = 0x40, Clothes = 0x20"),
    ("apparel flags drift", "Source/Patch_JawaHoodSwimming.cs", "PawnRenderFlags.Clothes | PawnRenderFlags.Headgear;", "PawnRenderFlags.Clothes;"),
    ("xenotype name drift", "Source/JawaRules.cs", 'JawaXenotype = "RSW_MandrakeJawa"', 'JawaXenotype = "RSW_MandrakeJawaa"'),
    ("label constant drift", "Source/JawaRules.cs", "public const float WantedAlpha = 0.6f;", "public const float WantedAlpha = 0.5f;"),
    ("lift hits drift", "Source/JawaRules.cs", "ExpectedHits = 4", "ExpectedHits = 3"),
    ("settings default drift", "Source/RSW_JawaRulesSettings.cs", 'Scribe_Values.Look(ref swimHoodEnabled, "swimHoodEnabled", true);', 'Scribe_Values.Look(ref swimHoodEnabled, "swimHoodEnabled", false);'),
    ("kernel imports Verse", "Source/Kernel/RSW_JawaRulesKernel.cs", "using System;", "using System;\nusing Verse;"),
    ("kernel missing from csproj", "Source/JawaRules.csproj", '<Compile Include="Kernel\\RSW_JawaRulesKernel.cs" />', ""),
    ("postfix lost its kernel", "Source/Patch_JawaHoodSwimming.cs", "RSW_HoodKernel.Postfix(", "HoodKernelPostfix("),
]


def plant_check():
    import shutil
    import subprocess
    import tempfile
    caught = 0
    for name, rel, old, new in PLANTS:
        with tempfile.TemporaryDirectory() as td:
            dst = os.path.join(td, "RimStarWars")
            os.makedirs(dst)
            shutil.copytree(os.path.join(SRC, "RimStarWars", "JawaRules"), os.path.join(dst, "JawaRules"), ignore=shutil.ignore_patterns("__pycache__", "Assemblies", "bin", "obj", "SelfTest"))
            # the defs and the one texture it leans on live in other mods: mirror just those
            for other, sub in (("StarWarsRaces", "Defs"), ("Armoury", "Defs"), ("Armoury", os.path.join("Textures", "SWApparel", "Robes", "jawa"))):
                shutil.copytree(os.path.join(SRC, "RimStarWars", other, sub), os.path.join(dst, other, sub), dirs_exist_ok=True)
            f = os.path.join(dst, "JawaRules", rel)
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
