#!/usr/bin/env python3
"""Offline lint of EmpirePursuit (mandrake.rut.empirepursuit, src/RimUtinni/EmpirePursuit): the generic mod lint
(lint_mod_defs.py: compile-listed, settings Scribe key/default, dead toggles, no control) plus the ladder data checks:

  ep-rung-fields   every RUT_EmpireRungDef child is a public field of the class (an unknown child discards the def); kind is an
                   EmpireRungKind; rungIndex is an int in 1..TopRung
  ep-rung-set      rungIndex 1..N unique and gap-free, N == EmpireLadderMath.TopRung (a gap strands the ladder: NextRungIndex skips it)
  ep-rung-kind     Strike/Cordon/Breach name no arrival/strategy mismatch: raid-shaped rungs carry arrivalMode and raidStrategy; Breach
                   with secondArrivalMode needs secondRaidStrategy or defaults; Probe lists >= 1 pawnKind
  ep-rung-times    Probe/Spotter/Cordon successHours > 0 (0 means the contact is won on its first check) and timeoutHours > successHours
                   for Probe/Spotter; Bombardment telegraphHours >= 1; every rung has an arrivalLetterLabel
  ep-keys          every "RUT_*".Translate() key in C# is defined under Languages/*/Keyed
  ep-constants     the kernel's tick constants match the engine ones the component aliases (GenDate.TicksPerHour 2500 / TicksPerDay 60000)
  ep-kernel-pure   the kernel imports no Verse / RimWorld / UnityEngine / HarmonyLib; csproj lists it; EmpireRungKind is declared once
  ep-scenpart      the ScenPartDef names classes that exist in Source

    python3 src/RimMandrake/Utils/lint_empirepursuit_defs.py [--quiet] [--mod-dir D] [--plant-check]
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
DEFAULT_MOD = os.path.join(REPO, "src", "RimUtinni", "EmpirePursuit")
RAID_SHAPED = {"Strike", "Cordon", "Breach"}


def read(p):
    return open(p, encoding="utf-8-sig").read()


def generic(mod):
    """Run the generic lint, capturing its output. The generic settings scan runs to the end of Settings.cs, so it also reads the
    Mod class's `public static RFPSettings settings` instance field as a settings field; those two lines are a known false
    positive and are dropped (counted, so the drop is visible)."""
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        rc = lint_mod_defs.run("EmpirePursuit", ["--mod-dir", mod])
    lines = buf.getvalue().splitlines()
    keep, dropped = [], 0
    for l in lines:
        if re.search(r"settings field settings (is declared but never Scribed|is never read)", l):
            dropped += 1
        else:
            keep.append(l)
    errs = [l for l in keep if l.startswith("ERROR")]
    return rc, keep, dropped, errs


def main(argv):
    quiet = "--quiet" in argv
    mod = argv[argv.index("--mod-dir") + 1] if "--mod-dir" in argv else DEFAULT_MOD
    src = os.path.join(mod, "Source")
    rc, gl, dropped, gerrs = generic(mod)
    if rc == 2:
        print("\n".join(gl))
        return 2
    errs, warns = list(gerrs), [l for l in gl if l.startswith("WARN")]
    E = lambda c, m: errs.append(f"ERROR {c}: {m}")
    W = lambda c, m: warns.append(f"WARN  {c}: {m}")

    defsrc = read(os.path.join(src, "RUT_EmpireRungDef.cs"))
    fields = set(re.findall(r"public\s+(?!static|override|const)[\w<>\[\]]+\s+(\w+)\s*(?:=[^;]*)?;", defsrc.split("class RUT_EmpireRungDef")[1].split("public static RUT_EmpireRungDef ForIndex")[0])) | {"defName", "label", "description"}
    kernel = read(os.path.join(src, "Kernel", "EmpireLadderKernel.cs"))
    kinds = re.findall(r"(\w+),", kernel.split("enum EmpireRungKind")[1].split("}")[0])
    top = int(re.search(r"TopRung\s*=\s*(\d+)", read(os.path.join(src, "EmpireLadderMath.cs"))).group(1))

    rungs = []
    for p in sorted(glob.glob(os.path.join(mod, "Defs", "EmpireRungDefs", "*.xml"))):
        root = ET.parse(p).getroot()
        for d in root:
            if not d.tag.endswith("RUT_EmpireRungDef"):
                continue
            dn = d.findtext("defName")
            for c in d:
                if c.tag not in fields:
                    E("ep-rung-fields", f"{dn}: <{c.tag}> is not a field of RUT_EmpireRungDef (the def would be discarded)")
            kind = (d.findtext("kind") or "Strike").strip()
            if kind not in kinds:
                E("ep-rung-fields", f"{dn}: kind '{kind}' is not an EmpireRungKind ({','.join(kinds)})")
            try:
                idx = int(d.findtext("rungIndex") or 1)
            except ValueError:
                E("ep-rung-fields", f"{dn}: rungIndex is not an int")
                continue
            if not 1 <= idx <= top:
                E("ep-rung-fields", f"{dn}: rungIndex {idx} outside 1..{top}")
            num = lambda t, dflt=0.0: float(d.findtext(t) or dflt)
            succ, tout, tele = num("successHours"), num("timeoutHours", 72), num("telegraphHours", 24)
            if kind in RAID_SHAPED and not ((d.findtext("arrivalMode") or "").strip() and (d.findtext("raidStrategy") or "").strip()):
                E("ep-rung-kind", f"{dn}: {kind} rung needs arrivalMode and raidStrategy (ConfigErrors rejects it at load)")
            if d.findtext("secondArrivalMode") and kind != "Breach":
                W("ep-rung-kind", f"{dn}: secondArrivalMode is only read for Breach")
            if kind == "Probe" and not d.findall("pawnKinds/li"):
                W("ep-rung-kind", f"{dn}: Probe lists no pawnKinds (falls back to the faction's smallest combat pawn)")
            if kind in ("Probe", "Spotter", "Cordon") and succ <= 0:
                E("ep-rung-times", f"{dn}: {kind} successHours is {succ}; the contact would be won on its first check")
            if kind in ("Probe", "Spotter") and tout <= succ:
                E("ep-rung-times", f"{dn}: timeoutHours {tout} <= successHours {succ}; the contact can never succeed")
            if kind == "Bombardment" and tele < 1:
                E("ep-rung-times", f"{dn}: telegraphHours {tele} < 1")
            if not (d.findtext("arrivalLetterLabel") or "").strip():
                E("ep-rung-times", f"{dn}: no arrivalLetterLabel")
            rungs.append((idx, dn, kind))
    if not rungs:
        print("LINT UNMEASURED: no RUT_EmpireRungDef found")
        return 2
    idxs = sorted(i for i, _, _ in rungs)
    if idxs != list(range(1, top + 1)):
        E("ep-rung-set", f"rungIndex set {idxs} is not 1..{top} exactly once each")
    canon = ["Probe", "Spotter", "Strike", "Cordon", "Breach", "Bombardment"]
    for i, dn, k in rungs:
        if i <= len(canon) and k != canon[i - 1]:
            W("ep-rung-set", f"{dn}: rung {i} is {k}; the design ladder has {canon[i - 1]} there")

    # keyed strings
    keyed = set()
    for p in glob.glob(os.path.join(mod, "Languages", "*", "Keyed", "*.xml")):
        keyed |= set(re.findall(r"<(RUT_\w+)>", read(p)))
    used = set()
    for p in glob.glob(os.path.join(src, "**", "*.cs"), recursive=True):
        if os.sep + "SelfTest" + os.sep in p or os.sep + "obj" + os.sep in p:
            continue
        used |= set(re.findall(r'"(RUT_\w+)"\s*\.Translate', read(p)))
    for k in sorted(used - keyed):
        E("ep-keys", f'"{k}".Translate() has no <{k}> under Languages/*/Keyed (the player sees the raw key)')

    # constants
    m = {n: int(v) for n, v in re.findall(r"public const int (TickInterval|TicksPerHour|TicksPerDay)\s*=\s*(\d+);", kernel)}
    if m.get("TicksPerHour") != 2500 or m.get("TickInterval") != 2500 or m.get("TicksPerDay") != 60000:
        E("ep-constants", f"kernel tick constants {m} differ from GenDate (TicksPerHour 2500, TicksPerDay 60000)")
    comp = read(os.path.join(src, "EmpireLadder.cs"))
    for nm, want in (("StorytellerSpacingTicks", "EmpireLadderState.StorytellerSpacingTicks"), ("CheckInterval", "EmpireLadderState.CheckInterval")):
        mm = re.search(r"const int " + nm + r"\s*=\s*([^;]+);", comp)
        if not mm or want not in mm.group(1):
            E("ep-constants", f"EmpireLadder.cs {nm} = {mm.group(1) if mm else '(missing)'} is not an alias of {want}")
    pursuit = read(os.path.join(src, "RuthlessPursuingMechanoids.cs"))
    if not re.search(r"const int TickInterval = GenDate\.TicksPerHour;", pursuit):
        E("ep-constants", "the scenario part's TickInterval is no longer GenDate.TicksPerHour (the kernel's hourly scheduler assumes 2500)")

    # kernel purity
    if re.search(r"^\s*using\s+(Verse|RimWorld|UnityEngine|HarmonyLib)", kernel, flags=re.M):
        E("ep-kernel-pure", "the kernel imports Verse/RimWorld/UnityEngine/HarmonyLib (the fuzz build would break)")
    if "Kernel\\EmpireLadderKernel.cs" not in read(os.path.join(src, "EmpirePursuit.csproj")):
        E("ep-kernel-pure", "EmpirePursuit.csproj does not list Kernel\\EmpireLadderKernel.cs")
    decls = [p for p in glob.glob(os.path.join(src, "**", "*.cs"), recursive=True) if os.sep + "SelfTest" + os.sep not in p and re.search(r"enum\s+EmpireRungKind", read(p))]
    if len(decls) != 1:
        E("ep-kernel-pure", f"EmpireRungKind is declared in {len(decls)} files")

    # scenpart classes
    allsrc = "\n".join(read(p) for p in glob.glob(os.path.join(src, "*.cs")))
    for p in glob.glob(os.path.join(mod, "Defs", "Scenarios", "*.xml")):
        for el in ET.parse(p).getroot().iter():
            cls = el.get("Class") or (el.text or "").strip() if el.tag == "scenPartClass" or el.get("Class") else ""
            short = cls.split(".")[-1]
            if cls.startswith("RuthlessPursuingMechanoids.") and not re.search(r"class\s+" + short + r"\b", allsrc):
                E("ep-scenpart", f"{os.path.basename(p)}: {cls} is not a class in Source")

    if not quiet:
        for l in warns:
            print(l)
    for l in errs:
        print(l)
    print(f"empirepursuit lint: {len(rungs)} rungs, top {top}, {len(used)} translate keys ({len(keyed)} keyed), {dropped} known-false settings lines dropped, "
          f"{len(errs)} ERROR, {len(warns)} WARN")
    return 1 if errs else 0


PLANTS = [
    ("rung kind typo", "Defs/EmpireRungDefs/RUT_EmpireRungs.xml", "<kind>Cordon</kind>", "<kind>Cordn</kind>"),
    ("unknown child", "Defs/EmpireRungDefs/RUT_EmpireRungs.xml", "<successHours>2</successHours>", "<succesHours>2</succesHours>"),
    ("rung gap", "Defs/EmpireRungDefs/RUT_EmpireRungs.xml", "<rungIndex>4</rungIndex>", "<rungIndex>7</rungIndex>"),
    ("instant probe", "Defs/EmpireRungDefs/RUT_EmpireRungs.xml", "<successHours>2</successHours>", "<successHours>0</successHours>"),
    ("probe can never succeed", "Defs/EmpireRungDefs/RUT_EmpireRungs.xml", "<timeoutHours>24</timeoutHours>", "<timeoutHours>1</timeoutHours>"),
    ("missing keyed string", "Languages/English/Keyed/EmpireLadder.xml", "<RUT_Ladder_Cordon>", "<RUT_Ladder_Cordonn>"),
    ("kernel imports Verse", "Source/Kernel/EmpireLadderKernel.cs", "using System;", "using System;\nusing Verse;"),
    ("tick constant drift", "Source/Kernel/EmpireLadderKernel.cs", "public const int TicksPerDay = 60000;", "public const int TicksPerDay = 24000;"),
    ("stale alias", "Source/EmpireLadder.cs", "public const int StorytellerSpacingTicks = EmpireLadderState.StorytellerSpacingTicks;", "public const int StorytellerSpacingTicks = 120000;"),
    ("kernel missing from csproj", "Source/EmpirePursuit.csproj", '<Compile Include="Kernel\\EmpireLadderKernel.cs" />', ""),
]


def plant_check():
    import shutil
    import subprocess
    import tempfile
    caught = 0
    for name, rel, old, new in PLANTS:
        with tempfile.TemporaryDirectory() as td:
            dst = os.path.join(td, "EmpirePursuit")
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
