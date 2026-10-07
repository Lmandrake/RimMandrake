#!/usr/bin/env python3
"""Offline lint of ExplosiveGrowth (mandrake.rm.explosivegrowth) and its campaign half (src/RimUtinni/PlantGrowth).

First the generic mod lint (lint_mod_defs.py: class/field/driver/GetNamed/DefOf/settings/compile-listed/wired), then the
data checks the generic lint cannot see because the roster is one Def holding string lists:

  eg-roster-fields   every <li> of a roster's <plants> carries only plant/top/produceFactor/ringPlant/slimeTerrain, has a
                     plant, a top that is an RM_GrowthTop name and a produceFactor >= 0 (a bad enum value discards the def)
  eg-roster-rows     Slime rows name a slimeTerrain, Tinder rows a ringPlant; a RM_/RUT_/RSW_ ringPlant / slimeTerrain /
                     bloomPlant / pawn kind / hediff / fluid must exist in some Defs folder; a plant listed twice in one
                     roster, or listed with a top while also exempt, is a dead row (WARN)
  eg-roster-names    noSoakBiomes / soakWeathers / irrigationFluids entries with our prefix that no Defs folder defines (WARN:
                     the list-every-plausible-name policy makes some of these deliberate; the count is printed)
  eg-top-numbering   RM_GrowthTop's numeric values equal the byte literals in the kernel's EffectiveTop, CountByTop is sized
                     to the enum, and the kernel is Verse-free and listed in the csproj
  eg-no-stale-copy   the map component re-declares no tell threshold / pass interval as a literal (it must alias the kernel)
  eg-debug-paths     every `Actions\\...` path validation.py drives names a [DebugAction] label that exists

    python3 src/RimMandrake/Utils/lint_explosivegrowth_defs.py [--quiet] [--mod-dir D]
"""
import glob
import os
import re
import sys
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import lint_mod_defs  # noqa: E402

REPO = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
SRC = os.path.join(REPO, "src")
PREFIX = ("RM_", "RUT_", "RSW_")
ENTRY_FIELDS = {"plant", "top", "produceFactor", "ringPlant", "slimeTerrain"}


def all_defnames():
    names = {}
    for p in glob.glob(os.path.join(SRC, "*", "*", "**", "Defs", "**", "*.xml"), recursive=True) + \
            glob.glob(os.path.join(SRC, "*", "*", "Defs", "**", "*.xml"), recursive=True):
        try:
            txt = open(p, encoding="utf-8-sig", errors="replace").read()
        except OSError:
            continue
        for m in re.finditer(r"<(\w[\w.]*)(?:\s[^>]*)?>\s*<defName>([^<]+)</defName>", txt):
            names.setdefault(m.group(2).strip(), set()).add(m.group(1).split(".")[-1])
    return names


def main(argv):
    quiet = "--quiet" in argv
    rc = lint_mod_defs.run("ExplosiveGrowth", [a for a in argv if a != "--quiet"] + (["--quiet"] if quiet else []))
    if rc == 2:
        return 2
    mod = os.path.join(SRC, "RimMandrake", "ExplosiveGrowth")
    if "--mod-dir" in argv:
        mod = argv[argv.index("--mod-dir") + 1]
    camp = os.path.join(SRC, "RimUtinni", "PlantGrowth")
    errs, warns = [], []
    E = lambda c, m: errs.append(f"ERROR {c}: {m}")
    W = lambda c, m: warns.append(f"WARN  {c}: {m}")
    known = all_defnames()
    top_names = set()
    gt = open(os.path.join(mod, "Source", "RM_GrowthTop.cs"), encoding="utf-8-sig").read()
    enum = {n: int(v) for n, v in re.findall(r"^\s*(\w+)\s*=\s*(\d+)\s*,", gt.split("enum RM_GrowthTop")[1].split("}")[0], flags=re.M)}
    top_names = set(enum)
    rosters = glob.glob(os.path.join(mod, "Defs", "**", "*.xml"), recursive=True) + glob.glob(os.path.join(camp, "**", "Defs", "**", "*.xml"), recursive=True)
    nrows = nroster = nplausible = 0
    exempt_all, rows_by_roster = set(), {}
    for p in sorted(rosters):
        try:
            root = ET.parse(p).getroot()
        except ET.ParseError as e:
            E("xml-parses", f"{p}: {e}")
            continue
        rel = os.path.relpath(p, SRC)
        for d in root:
            if d.tag.endswith("RM_ExplosiveGrowthRosterDef"):
                nroster += 1
                dn = d.findtext("defName")
                seen = {}
                for li in d.findall("plants/li"):
                    nrows += 1
                    kids = {c.tag for c in li}
                    for k in sorted(kids - ENTRY_FIELDS):
                        E("eg-roster-fields", f"{rel} {dn}: <li> has unknown child <{k}> (RM_ExplosiveGrowthRosterEntry has no such field)")
                    plant = (li.findtext("plant") or "").strip()
                    if not plant:
                        E("eg-roster-fields", f"{rel} {dn}: a plants <li> has no <plant>")
                        continue
                    if plant.startswith(PREFIX) and plant not in known:
                        W("eg-roster-rows", f"{rel} {dn}: roster plant {plant} is defined by no Defs folder (the row is skipped silently at load)")
                    top = (li.findtext("top") or "Churn").strip()
                    if top not in top_names:
                        E("eg-roster-fields", f"{rel} {dn}: {plant} top '{top}' is not an RM_GrowthTop ({','.join(sorted(top_names))})")
                    try:
                        if float(li.findtext("produceFactor") or 1) < 0:
                            E("eg-roster-fields", f"{rel} {dn}: {plant} produceFactor is negative")
                    except ValueError:
                        E("eg-roster-fields", f"{rel} {dn}: {plant} produceFactor is not a number")
                    if top == "Slime" and not (li.findtext("slimeTerrain") or "").strip():
                        W("eg-roster-rows", f"{rel} {dn}: Slime row {plant} names no slimeTerrain (the ring falls back to slime filth)")
                    if top == "Tinder" and not (li.findtext("ringPlant") or "").strip():
                        W("eg-roster-rows", f"{rel} {dn}: Tinder row {plant} names no ringPlant (it sows itself)")
                    for f in ("ringPlant", "slimeTerrain"):
                        v = (li.findtext(f) or "").strip()
                        if v.startswith(PREFIX) and v not in known:
                            E("eg-roster-rows", f"{rel} {dn}: {plant} {f} {v} is defined by no Defs folder")
                    if plant in seen:
                        W("eg-roster-rows", f"{rel} {dn}: plant {plant} listed twice (the later row wins)")
                    seen[plant] = top
                rows_by_roster[dn] = seen
                ex = {(x.text or "").strip() for x in d.findall("exemptPlants/li")}
                exempt_all |= ex
                for pl in sorted(ex & set(seen)):
                    if seen[pl] != "None":
                        W("eg-roster-rows", f"{rel} {dn}: {pl} is both exempt and given top {seen[pl]} (exempt wins; the row is dead)")
                for lst in ("noSoakBiomes", "soakWeathers", "irrigationFluids", "rupturePawnKinds", "ruptureMutationHediffs"):
                    for x in d.findall(lst + "/li"):
                        v = (x.text or "").strip()
                        if v.startswith(PREFIX) and v not in known:
                            nplausible += 1
                            (E if lst in ("rupturePawnKinds", "ruptureMutationHediffs") else W)("eg-roster-names", f"{rel} {dn}: {lst} entry {v} is defined by no Defs folder")
            for inc in root.iter("li"):
                if (inc.get("Class") or "").endswith("RM_BloomBurstExtension"):
                    bp = (inc.findtext("bloomPlant") or "").strip()
                    if bp.startswith(PREFIX) and bp not in known:
                        E("eg-roster-rows", f"{rel}: bloomPlant {bp} is defined by no Defs folder")
    if nroster == 0:
        print("LINT UNMEASURED: no RM_ExplosiveGrowthRosterDef found")
        return 2

    # the campaign roster must not contradict the RM roster silently: count overriding rows
    names = sorted(rows_by_roster)
    if len(names) >= 2:
        a, b = rows_by_roster[names[0]], rows_by_roster[names[1]]
        diff = [p for p in set(a) & set(b) if a[p] != b[p]]
        for p in sorted(diff):
            W("eg-roster-rows", f"{p} is {a[p]} in {names[0]} and {b[p]} in {names[1]} (the later-loaded def wins)")

    # numbering
    kt = open(os.path.join(mod, "Source", "Kernel", "RM_ExplosiveGrowthKernel.cs"), encoding="utf-8-sig").read()
    if re.search(r"^\s*using\s+(Verse|RimWorld|UnityEngine)", kt, flags=re.M):
        E("eg-top-numbering", "the kernel imports Verse/RimWorld/UnityEngine (the self-test build would break)")
    cases = {int(n): v for n, v in re.findall(r"case\s+(\d+):\s*return\s+(\w+)\s*\?", kt)}
    want = {enum["Burst"]: "burst", enum["Tinder"]: "tinder", enum["Slime"]: "slime", enum["Rupture"]: "rupture", enum["Flush"]: "flush"}
    for n, flag in want.items():
        if cases.get(n) != flag:
            E("eg-top-numbering", f"kernel EffectiveTop case {n} tests '{cases.get(n)}' but RM_GrowthTop value {n} is {[k for k, v in enum.items() if v == n]} (flag {flag})")
    if f"case {enum['Churn']}: return fallback" not in kt:
        E("eg-top-numbering", "kernel EffectiveTop has no 'case Churn: return fallback'")
    if "(byte)6" not in kt and "(byte)" in kt and enum["None"] != 6:
        E("eg-top-numbering", f"kernel hard-codes None as 6 but the enum says {enum['None']}")
    if enum["None"] != 6:
        E("eg-top-numbering", f"RM_GrowthTop.None is {enum['None']}; the kernel's fallback and 'top >= 6' are written for 6")
    reg = open(os.path.join(mod, "Source", "RM_ExplosiveGrowthRegistry.cs"), encoding="utf-8-sig").read()
    m = re.search(r"CountByTop\s*=\s*new int\[(\d+)\]", reg)
    if not m or int(m.group(1)) != len(enum):
        E("eg-top-numbering", f"Registry.CountByTop size {m.group(1) if m else '?'} != RM_GrowthTop member count {len(enum)}")
    mc = open(os.path.join(mod, "Source", "RM_MapComponent_ExplosiveGrowth.cs"), encoding="utf-8-sig").read()
    for nm in ("PassInterval", "SwellAt", "HueAt", "TrembleAt", "CreakAt", "SilenceAt", "MatureGrowth"):
        mm = re.search(r"public const (?:int|float) " + nm + r" = ([^;]+);", mc)
        if not mm or "RM_ExplosiveGrowthKernel." not in mm.group(1):
            E("eg-no-stale-copy", f"component {nm} = {mm.group(1) if mm else '(missing)'} is not an alias of the kernel constant")

    # debug action paths
    dbg = open(os.path.join(mod, "Source", "Debug", "RM_ExplosiveGrowthDebugActions.cs"), encoding="utf-8-sig").read()
    labels = set(re.findall(r'\[DebugAction\(CAT,\s*"([^"]+)"', dbg))
    val = open(os.path.join(mod, "validation.py"), encoding="utf-8-sig").read()
    paths = re.findall(r'P_\w+\s*=\s*"Actions\\\\(?:T: )?([^"]+)"', val)
    if not labels or not paths:
        print(f"LINT UNMEASURED: debug labels {len(labels)} / validation paths {len(paths)}")
        return 2
    for pth in paths:
        if pth not in labels:
            E("eg-debug-paths", f"validation.py drives 'Actions\\{pth}' but no [DebugAction] has that label")

    if not quiet:
        for l in warns:
            print(l)
    for l in errs:
        print(l)
    print(f"explosivegrowth lint (data): {nroster} rosters, {nrows} plant rows, {len(enum)} tops, {len(labels)} debug labels, "
          f"{len(paths)} validation paths, {nplausible} unresolved-name entries, {len(errs)} ERROR, {len(warns)} WARN")
    return 1 if errs or rc == 1 else 0


PLANTS = [
    ("roster top typo", "Defs/ExplosiveGrowth/RM_ExplosiveGrowthRoster.xml", "<top>Burst</top>", "<top>Brust</top>"),
    ("roster unknown child", "Defs/ExplosiveGrowth/RM_ExplosiveGrowthRoster.xml", "<produceFactor>2.5</produceFactor>", "<produceFactr>2.5</produceFactr>"),
    ("enum renumbered", "Source/RM_GrowthTop.cs", "Rupture = 4,", "Rupture = 2,"),
    ("component stale literal", "Source/RM_MapComponent_ExplosiveGrowth.cs", "public const float HueAt = RM_ExplosiveGrowthKernel.HueAt;", "public const float HueAt = 0.5f;"),
    ("debug label renamed", "Source/Debug/RM_ExplosiveGrowthDebugActions.cs", '"Soak 5x5 here"', '"Soak 3x3 here"'),
    ("kernel import Verse", "Source/Kernel/RM_ExplosiveGrowthKernel.cs", "using System;", "using System;\nusing Verse;"),
    ("csproj omits kernel", "Source/RM_ExplosiveGrowth.csproj", '<Compile Include="Kernel\\RM_ExplosiveGrowthKernel.cs" />', ""),
    ("registry table size", "Source/RM_ExplosiveGrowthRegistry.cs", "new int[7]", "new int[6]"),
]


def plant_check():
    """Copy the mod to a temp dir, plant each defect, demand the lint reports an ERROR for it. Exit 0 iff all caught."""
    import shutil
    import subprocess
    import tempfile
    mod = os.path.join(SRC, "RimMandrake", "ExplosiveGrowth")
    caught = 0
    for name, rel, old, new in PLANTS:
        with tempfile.TemporaryDirectory() as td:
            dst = os.path.join(td, "ExplosiveGrowth")
            shutil.copytree(mod, dst, ignore=shutil.ignore_patterns("__pycache__", "Assemblies", "bin", "obj", "SelfTest"))
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
