#!/usr/bin/env python3
"""Offline lint of SWBestiary (mandrake.rsw.swbestiary): XML defs against its three C# assemblies (Livestock, BeastMechanics, JawaIkee) and
data checks the kernels depend on. The shared generic lint (lint_mod_defs.py) expects one csproj and resolves only src/RimMandrake classes,
so this tool carries its own class resolution for the RimMandrake.StarWars.* names.

  sb-class        every Class= / workerClass / needClass / hediffClass naming RimMandrake.StarWars.{SWBestiary,Livestock,JawaIkee}.X resolves to a
                  class in an assembly's compiled sources; every compiled class is in its csproj (EnableDefaultCompileItems false hides a miss)
  sb-guard        a def OUTSIDE SWBestiary that names one of those classes must be guarded by MayRequire mandrake.rsw.swbestiary / FindMod / an About dependency
  sb-kiln         kiln-belly: doses needed >= 2 (one dose can never be spaced), rushed span < window, product and feed defs exist, the feed carries the feed comp
  sb-grief        moornak: unsettled hediff exists, decays (severityPerDay < 0), its max reaches the release spike, spike above the target, initial <= max;
                  prints how long a release spike outlasts the target
  sb-eat          metal eater: fractions in (0,1], nutrition > 0, dig names a thing when on, the think-tree insert and job defs exist
  sb-hoard        scrap hoarder: nest def exists, positive radii and cap, a spacing that fits the nest search radius
  sb-toxin        toxin need: positive fall, no custom max level (the kernel's thresholds are fractions of 1), hediff has the two stages the kernel picks from,
                  its chemicalNeed is that need; prints the days from full to withdrawal
  sb-spew         fuel-spew ability: positive range and width, comp range within the verb range, half angle printed
  sb-ikee         thought: two stages, comforted positive and unsettled negative, positive radius, tolerant xenotypes exist
  sb-settings     each Scribe default equals its field initializer
  sb-kernel       the three kernels import no Verse / RimWorld / UnityEngine and are compiled by their assemblies

    python3 src/RimMandrake/Utils/lint_swbestiary_defs.py [--quiet] [--mod-dir D] [--plant-check]
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
PACKAGE = "mandrake.rsw.swbestiary"
ASSEMBLIES = [("Livestock", "RimMandrakeLivestockRSW.csproj", "Kernel/RSW_LivestockKernel.cs"),
              ("BeastMechanics", "RimMandrakeBeastMechanicsRSW.csproj", "Kernel/RSW_BeastKernel.cs"),
              ("JawaIkee", "JawaIkee.csproj", "Kernel/RSW_IkeeKernel.cs")]
NS_PREFIXES = ("RimMandrake.StarWars.SWBestiary.", "RimMandrake.StarWars.Livestock.", "RimMandrake.StarWars.JawaIkee.")


def read(p):
    return open(p, encoding="utf-8-sig").read()


def defs_of(mod_or_src):
    out = {}
    for p in glob.glob(os.path.join(mod_or_src, "**", "*.xml"), recursive=True):
        try:
            r = ET.parse(p).getroot()
        except ET.ParseError:
            continue
        for d in r:
            n = d.findtext("defName") if hasattr(d, "findtext") else None
            if n:
                out.setdefault(n.strip(), []).append((d.tag, d, p))
    return out


def get(table, name, tag=None):
    for t, d, p in table.get(name, []):
        if tag is None or t == tag:
            return (t, d, p)
    return None


def main(argv):
    quiet = "--quiet" in argv
    src_root = argv[argv.index("--src-root") + 1] if "--src-root" in argv else SRC
    mod = argv[argv.index("--mod-dir") + 1] if "--mod-dir" in argv else os.path.join(src_root, "RimStarWars", "SWBestiary")
    errs, warns, info = [], [], []
    E = lambda c, m: errs.append(f"ERROR {c}: {m}")
    W = lambda c, m: warns.append(f"WARN  {c}: {m}")
    I = lambda c, m: info.append(f"INFO  {c}: {m}")
    base = os.path.join(mod, "Source")
    compiled = set()
    per_asm = {}
    for asm, csproj, kernel in ASSEMBLIES:
        d = os.path.join(base, asm)
        cp = read(os.path.join(d, csproj))
        types = set()
        for p in glob.glob(os.path.join(d, "**", "*.cs"), recursive=True):
            if os.sep + "obj" + os.sep in p:
                continue
            t = LA.strip_cs(read(p))
            ns = re.search(r"namespace\s+([\w.]+)", t)
            names = re.findall(r"\b(?:public|internal)\s+(?:static\s+|abstract\s+|sealed\s+)*(?:class|enum|struct)\s+(\w+)", t)
            for n in names:
                types.add((ns.group(1) + "." + n) if ns else n)
            rel = os.path.relpath(p, d).replace(os.sep, "\\")
            if "EnableDefaultCompileItems>false" in cp and rel not in cp and names:
                E("sb-class", f"{asm}/{rel} has classes {names} but is not in {csproj} (EnableDefaultCompileItems false: it compiles into nothing)")
        per_asm[asm] = types
        compiled |= types
    if len(compiled) < 40:
        print(f"LINT UNMEASURED: only {len(compiled)} compiled types found under {base}")
        return 2
    known = defs_of(mod)
    all_known = defs_of(os.path.join(src_root, "RimStarWars"))

    # sb-class
    xml_files = sorted(glob.glob(os.path.join(mod, "Defs", "**", "*.xml"), recursive=True) + glob.glob(os.path.join(mod, "Patches", "**", "*.xml"), recursive=True))
    nclass = 0
    for p in xml_files:
        txt = read(p)
        if "RimMandrake.StarWars." not in txt:
            continue
        for m in re.finditer(r'(?:Class="|<(?:workerClass|needClass|hediffClass|thingClass|compClass|driverClass|genStep)>)(RimMandrake\.StarWars\.[\w.]+)', re.sub(r"<!--.*?-->", "", txt, flags=re.S)):
            nclass += 1
            if m.group(1).startswith(NS_PREFIXES) and m.group(1) not in compiled:
                E("sb-class", f"{os.path.relpath(p, mod)}: {m.group(1)} is compiled by no SWBestiary assembly")
    # sb-guard
    seen = unguarded = 0
    for p in LA.all_xml(src_root):
        if os.path.commonpath([p, mod]) == mod:
            continue
        txt = read(p)
        if "RimMandrake.StarWars." not in txt or not any(t in txt for t in compiled):
            continue
        try:
            root = ET.fromstring(txt.encode("utf-8"))
        except ET.ParseError:
            continue
        pm = LA.parent_map(root)
        dep = LA.about_depends_on_armoury(LA.mod_root_of(p) if os.path.commonpath([p, src_root]) == src_root else os.path.dirname(p), PACKAGE)
        for el in root.iter():
            for v in (el.get("Class") or "", (el.text or "").strip()):
                if v in compiled:
                    seen += 1
                    if not LA.guarded(el, pm, dep, PACKAGE, "bestiary"):
                        unguarded += 1
                        E("sb-guard", f"{os.path.relpath(p, src_root)}: <{el.tag}> names {v} (compiled in SWBestiary) with no MayRequire {PACKAGE}, no FindMod and no About dependency")

    # def helpers
    def li_with(cls_suffix):
        for name, rows in known.items():
            for tag, d, p in rows:
                for li in d.iter("li"):
                    if (li.get("Class") or "").endswith(cls_suffix):
                        yield name, d, li, p

    # sb-kiln
    cp_src = LA.strip_cs(read(os.path.join(base, "Livestock", "CompKilnBelly.cs")))
    def cs_int(expr):
        e = expr.replace("GenDate.TicksPerDay", "60000")
        return int(eval(e, {"__builtins__": {}}, {})) if re.fullmatch(r"[0-9+*/() ]+", e) else 0
    dflt = {k: cs_int(v) for k, v in re.findall(r"public int (\w+) = ([^;]+);", cp_src)}
    needed = dflt.get("dosesNeeded", 0)
    if needed < 2:
        E("sb-kiln", f"default dosesNeeded is {needed}: with one dose the span is 0, which is never 'spaced', so every batch would be cracked")
    nk = 0
    for name, d, li, p in li_with("CompProperties_KilnBelly"):
        nk += 1
        n_ = int(float(li.findtext("dosesNeeded") or needed))
        if n_ < 2:
            E("sb-kiln", f"{name}: dosesNeeded {n_} < 2")
        win = int(float(li.findtext("doseWindowTicks") or dflt.get("doseWindowTicks", 0))); rush = int(float(li.findtext("rushedSpanTicks") or dflt.get("rushedSpanTicks", 0)))
        if not 0 < rush < win:
            E("sb-kiln", f"{name}: rushed span {rush} must be positive and under the window {win}")
        for f in ("doseFeedDef", "goodProductDef", "badProductDef"):
            v = (li.findtext(f) or "").strip()
            if v and v not in all_known:
                E("sb-kiln", f"{name}: {f} {v} is defined by no Defs folder here")
        feed = (li.findtext("doseFeedDef") or "").strip()
        if get(known, feed, "ThingDef") is not None and not any((c.get("Class") or "").endswith("CompProperties_KilnFeed") for c in get(known, feed, "ThingDef")[1].iter("li")):
            E("sb-kiln", f"{name}: feed {feed} carries no CompProperties_KilnFeed, so eating it never registers a dose")
        if int(float(li.findtext("goodProductCount") or 6)) < 1 or int(float(li.findtext("badProductCount") or 2)) < 1:
            E("sb-kiln", f"{name}: a product count under 1")
    # sb-grief
    ng = 0
    for name, d, li, p in li_with("CompProperties_MoornakGrief"):
        ng += 1
        h = (li.findtext("unsettledHediffDef") or "").strip()
        hd = get(known, h, "HediffDef")
        spike = float(li.findtext("releaseSpikeSeverity") or 1); target = float(li.findtext("unsettledTargetSeverity") or 0.6)
        if hd is None:
            E("sb-grief", f"{name}: unsettledHediffDef {h or '(none)'} is defined by no Defs folder")
        else:
            h_el = hd[1]
            mx = float(h_el.findtext("maxSeverity") or 1)
            decay = [float(c.findtext("severityPerDay") or 0) for c in h_el.iter("li") if (c.get("Class") or "").endswith("HediffCompProperties_SeverityPerDay")]
            if not decay or decay[0] >= 0:
                E("sb-grief", f"{h}: no negative severityPerDay: the unsettled feeling would never fade after the moornak leaves")
            if mx < spike:
                E("sb-grief", f"{h}: maxSeverity {mx} is under the release spike {spike} (the spike is clamped)")
            if decay and decay[0] < 0 and spike > target:
                I("sb-grief", f"a release spike of {spike} outlasts the {target} target by {(spike - target) / -decay[0]:.2f} days at {decay[0]}/day")
        if not target < spike:
            W("sb-grief", f"{name}: unsettledTargetSeverity {target} is not below the release spike {spike}: a release feels like the ordinary state")
        if float(li.findtext("initialGriefCharge") or 0.4) > float(li.findtext("maxGriefCharge") or 1):
            E("sb-grief", f"{name}: initialGriefCharge above maxGriefCharge")
    # sb-eat
    ne = 0
    for name, d, li, p in li_with("CompProperties_MetalEater"):
        ne += 1
        pct = float(li.findtext("percentageOfDestruction") or 0.2)
        if not 0 < pct <= 1:
            E("sb-eat", f"{name}: percentageOfDestruction {pct} outside (0,1]")
        if float(li.findtext("nutrition") or 1) <= 0:
            E("sb-eat", f"{name}: nutrition not positive: eating metal feeds nothing")
        if (li.findtext("digThingIfMapEmpty") or "false").strip().lower() == "true" and not (li.findtext("thingToDigIfMapEmpty") or "").strip():
            E("sb-eat", f"{name}: digThingIfMapEmpty on with no thingToDigIfMapEmpty")
        if not li.findall("customThingToEat/li"):
            E("sb-eat", f"{name}: customThingToEat is empty: it eats nothing")
    for jd, cls in (("RSW_EatMetal", "JobDriver_EatMetal"), ("RSW_HoardScrap", "JobDriver_HoardScrap")):
        job = get(known, jd, "JobDef")
        if job is None:
            E("sb-eat", f"JobDef {jd} is defined by no Defs folder (RSW_BeastMechanicsDefOf would be null)")
        elif cls not in (job[1].findtext("driverClass") or ""):
            E("sb-eat", f"JobDef {jd} driverClass is {job[1].findtext('driverClass')}, expected {cls}")
    # sb-hoard
    nh = 0
    for name, d, li, p in li_with("CompProperties_ScrapHoarder"):
        nh += 1
        nest = (li.findtext("nestDef") or "RSW_ScrapNest").strip()
        if nest not in known:
            E("sb-hoard", f"{name}: nestDef {nest} is defined by no Defs folder (the whole behaviour silently switches off)")
        sr, nr = float(li.findtext("scrapSearchRadius") or 40), float(li.findtext("nestSearchRadius") or 40)
        mn, sp = int(float(li.findtext("maxNestsPerMap") or 4)), float(li.findtext("minNestSpacing") or 18)
        if sr <= 0 or nr <= 0 or mn < 1 or sp <= 0:
            E("sb-hoard", f"{name}: non-positive radius / cap / spacing")
        if not li.findall("hoardableDefs/li"):
            E("sb-hoard", f"{name}: hoardableDefs is empty")
    # sb-toxin
    need = get(known, "RSW_ToxinDependence", "NeedDef")
    hed = None
    for name, rows in known.items():
        for tag, d, p in rows:
            if tag == "HediffDef" and (d.findtext("hediffClass") or "").endswith("RSW_Hediff_ToxinDependence"):
                hed = (name, d)
    nt = 0
    if need is not None:
        nt = 1
        nd = need[1]
        fall = float(nd.findtext("fallPerDay") or 0)
        if fall <= 0:
            E("sb-toxin", "fallPerDay not positive: the need never falls, so withdrawal is unreachable")
        else:
            I("sb-toxin", f"full to withdrawal in {(1.0 - 0.01) / fall:.2f} days at fallPerDay {fall}")
        if nd.findtext("maxLevel") not in (None, "1", "1.0", "1.00"):
            E("sb-toxin", f"NeedDef maxLevel {nd.findtext('maxLevel')}: the kernel's thresholds (0.1 / 0.01) are fractions of 1")
        if hed is None:
            E("sb-toxin", "no HediffDef with hediffClass RSW_Hediff_ToxinDependence")
        else:
            if len(hed[1].findall("stages/li")) != 2:
                E("sb-toxin", f"{hed[0]} has {len(hed[1].findall('stages/li'))} stages; the hediff picks stage 0 or 1")
            if (hed[1].findtext("chemicalNeed") or "").strip() != "RSW_ToxinDependence":
                E("sb-toxin", f"{hed[0]}.chemicalNeed is {hed[1].findtext('chemicalNeed')}, not RSW_ToxinDependence")
    else:
        E("sb-toxin", "NeedDef RSW_ToxinDependence not found")
    # sb-spew
    nsp = 0
    for name, d, li, p in li_with("CompProperties_AbilityFuelSpew"):
        nsp += 1
        rng, wid = float(li.findtext("range") or 10), float(li.findtext("lineWidthEnd") or 6)
        if rng <= 0 or wid <= 0:
            E("sb-spew", f"{name}: non-positive range or width")
        vr = d.findtext("verbProperties/range")
        if vr is not None and float(vr) < rng - 1e-6:
            W("sb-spew", f"{name}: the spray range {rng} is longer than the verb's {vr}: cells beyond the verb's reach can be hit")
        I("sb-spew", f"{name}: half angle {math.degrees(math.atan2(wid / 2, rng)):.1f} degrees at range {rng}, width {wid}")
    # sb-ikee
    ni = 0
    for name, tag, d, p in [(n, t, d_, p_) for n, rows in known.items() for (t, d_, p_) in rows]:
        if tag == "ThoughtDef" and (d.findtext("workerClass") or "").endswith("ThoughtWorker_IkeeNearby"):
            ni += 1
            st = d.findall("stages/li")
            if len(st) != 2:
                E("sb-ikee", f"{name}: {len(st)} stages; the worker returns stage 0 (comforted) or 1 (unsettled)")
            else:
                if float(st[0].findtext("baseMoodEffect") or 0) <= 0:
                    E("sb-ikee", f"{name}: stage 0 (comforted) is not a positive mood")
                if float(st[1].findtext("baseMoodEffect") or 0) >= 0:
                    E("sb-ikee", f"{name}: stage 1 (unsettled) is not a negative mood")
            for ext in d.iter("li"):
                if (ext.get("Class") or "").endswith("IkeeToleranceExtension"):
                    if float(ext.findtext("radius") or 12) <= 0:
                        E("sb-ikee", f"{name}: radius not positive")
                    for x in ext.findall("tolerantXenotypes/li"):
                        v = (x.text or "").strip()
                        if v not in all_known and os.path.isdir(os.path.join(src_root, "RimStarWars", "StarWarsRaces")):
                            E("sb-ikee", f"{name}: tolerant xenotype {v} is defined by no Defs folder")
    # sb-settings
    for f in glob.glob(os.path.join(base, "**", "*Settings.cs"), recursive=True):
        t = LA.strip_cs(read(f))
        init = {m.group(2): m.group(3) for m in re.finditer(r"public static (float|bool|int) (\w+) = ([\w.]+?)f?;", t)}
        for m in re.finditer(r'Scribe_Values\.Look\(ref (\w+), "(\w+)", ([\w.]+?)f?(?:, true)?\)', t):
            fld, key, dv = m.groups()
            if key != fld:
                E("sb-settings", f"{os.path.basename(f)}: key '{key}' != field '{fld}'")
            if fld in init and init[fld].rstrip("f") != dv.rstrip("f"):
                E("sb-settings", f"{os.path.basename(f)}: {fld} initialises to {init[fld]} but Scribes default {dv}")
    # sb-kernel
    for asm, csproj, kernel in ASSEMBLIES:
        kt = read(os.path.join(base, asm, *kernel.split("/")))
        if re.search(r"^\s*using\s+(Verse|RimWorld|UnityEngine|HarmonyLib)", kt, flags=re.M):
            E("sb-kernel", f"{kernel} imports Verse/RimWorld/UnityEngine/HarmonyLib (the fuzz build would break)")
        cp = read(os.path.join(base, asm, csproj))
        if "EnableDefaultCompileItems>false" in cp and kernel.replace("/", "\\") not in cp:
            E("sb-kernel", f"{csproj} does not list {kernel.replace('/', chr(92))}")
    for rel, need_s in (("Livestock/CompKilnBelly.cs", "RSW_KilnKernel.Register("), ("Livestock/CompMoornakGrief.cs", "RSW_GriefKernel.NextUnsettled("),
                        ("BeastMechanics/JobDriver_EatMetal.cs", "RSW_EatKernel.Chew("), ("BeastMechanics/JobGiver_HoardScrap.cs", "RSW_HoardKernel.NestCellOk("),
                        ("BeastMechanics/ToxinDependence.cs", "RSW_ToxinKernel.Next("), ("BeastMechanics/CompAbilityEffect_FuelSpew.cs", "RSW_SpewKernel.ConeFor("),
                        ("JawaIkee/ThoughtWorker_IkeeNearby.cs", "RSW_IkeeKernel.Stage(")):
        if need_s not in read(os.path.join(base, *rel.split("/"))):
            E("sb-kernel", f"{rel} no longer calls {need_s}")

    out = errs if quiet else warns + info + errs
    for l in out:
        print(l)
    print(f"swbestiary lint: {len(compiled)} compiled types in 3 assemblies, {nclass} class refs, {seen} cross-mod type uses ({unguarded} unguarded), "
          f"{nk} kiln, {ng} grief, {ne} eaters, {nh} hoarders, {nt} toxin needs, {nsp} sprays, {ni} ikee thoughts, {len(errs)} ERROR, {len(warns)} WARN")
    return 1 if errs else 0


PLANTS = [
    ("kiln needs one dose", "Source/Livestock/CompKilnBelly.cs", "public int dosesNeeded = 3;", "public int dosesNeeded = 1;"),
    ("kiln rushed span over the window", "Source/Livestock/CompKilnBelly.cs", "public int rushedSpanTicks = GenDate.TicksPerDay / 4;", "public int rushedSpanTicks = GenDate.TicksPerDay * 2;"),
    ("kiln feed ghost", "Defs/Livestock/ThingDefs_Animals/ThingDefs_Onnik.xml", "<doseFeedDef>RSW_KilnClay</doseFeedDef>", "<doseFeedDef>RSW_KilnClayy</doseFeedDef>"),
    ("moornak hediff never fades", "Defs/Livestock/HediffDefs/HediffDefs_Moornak.xml", "<severityPerDay>-0.4</severityPerDay>", "<severityPerDay>0.4</severityPerDay>"),
    ("moornak hediff max under the spike", "Defs/Livestock/HediffDefs/HediffDefs_Moornak.xml", "<maxSeverity>1</maxSeverity>", "<maxSeverity>0.5</maxSeverity>"),
    ("eater eats nothing", "Defs/DesertPort/RSW_DesertPortMisc_Races.xml", "<li>Steel</li>\n\t\t\t\t\t<li>ChunkSlagSteel</li>", ""),
    ("eater destroys more than all", "Defs/DesertPort/RSW_DesertPortMisc_Races.xml", "<percentageOfDestruction>0.2</percentageOfDestruction>", "<percentageOfDestruction>1.5</percentageOfDestruction>"),
    ("nest def ghost", "Defs/ThingDefs_Races/RSW_ScrapNestBird.xml", "<nestDef>RSW_ScrapNest</nestDef>", "<nestDef>RSW_ScrapNestt</nestDef>"),
    ("toxin never falls", "Defs/BiomesTeamPort/Support/RSW_BiomesTeamPort_Support.xml", "<fallPerDay>1</fallPerDay>", "<fallPerDay>0</fallPerDay>"),
    ("ikee comforted is negative", "Defs/JawaIkee/ThoughtDefs/Thought_IkeeWatching.xml", "<baseMoodEffect>4</baseMoodEffect>", "<baseMoodEffect>-4</baseMoodEffect>"),
    ("settings default drift", "Source/Livestock/RSW_LivestockSettings.cs", 'Scribe_Values.Look(ref kilnCooldownMultiplier, "kilnCooldownMultiplier", 1f);', 'Scribe_Values.Look(ref kilnCooldownMultiplier, "kilnCooldownMultiplier", 2f);'),
    ("kernel imports Verse", "Source/BeastMechanics/Kernel/RSW_BeastKernel.cs", "using System;", "using System;\nusing Verse;"),
    ("kernel missing from csproj", "Source/Livestock/RimMandrakeLivestockRSW.csproj", '<Compile Include="Kernel\\RSW_LivestockKernel.cs" />', ""),
    ("call site lost its kernel", "Source/BeastMechanics/JobDriver_EatMetal.cs", "RSW_EatKernel.Chew(", "ChewX("),
]


def plant_check():
    import shutil
    import subprocess
    import tempfile
    mod = os.path.join(SRC, "RimStarWars", "SWBestiary")
    caught = 0
    for name, rel, old, new in PLANTS:
        with tempfile.TemporaryDirectory() as td:
            dst = os.path.join(td, "RimStarWars", "SWBestiary")
            shutil.copytree(mod, dst, ignore=shutil.ignore_patterns("__pycache__", "Assemblies", "bin", "obj", "SelfTest", "Textures", "Sounds", "art", "Languages"))
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
