#!/usr/bin/env python3
"""Offline lint of Webwork (mandrake.rm.webwork): the generic mod lint (lint_mod_defs.py) plus data checks the generic lint cannot see:

  ww-urraveth-layout  the seven-piece skeleton: every Layout def exists, each footprint (XML <size>) sits inside the 15 x 9 site, no two
                      overlap, the chapters are exactly the kernel's ChapterOrder, one skull holds the highest rank, every piece of rank > 0
                      has a strictly lower-rank NEIGHBOUR (the kernel's adjacency) or losing the pieces below it can never load it, the
                      graph is connected, tickerType is Rare (StepLoad runs from TickRare), and the fuzz's copy of the layout equals the mod's
  ww-settings         every slider's shipped default lies inside the slider range; the ranges cannot drive the kernel out of domain
                      (warning window above one rare tick, relay multiplier above the kernel floor, chance 0..1)
  ww-lance            the traction lance's tether ladder cloth < devilstrand < thrixweave on range / strength / reel and the reverse on snap,
                      the rigging fuel filter equals the fabrics the ladder names, stuff categories, the research that unlocks it, the gutter
                      junction that grants that research, and the extension fields exist on the CreatureBehaviors class
  ww-nest             nest GenStep constants name defs that exist, the relay comp sits on the wall with the ruled 20~30 day range and a mother
                      race that exists, the GenStepDefs order the nest (324) before the skeleton (325) and both are added to the map generator
  ww-economy          the thrixweave neighbours: this mod relabels Hyperweave, the campaign economy loads after it, the startup gate reaches the
                      front extension by a field name that exists, and no def outside the known owners adds Hyperweave to a trader's stock
  ww-kernel-pure      the kernel imports no Verse / RimWorld / UnityEngine and is listed in the csproj; an unattached emergent comp is WARNed

    python3 src/RimMandrake/Utils/lint_webwork_defs.py [--quiet] [--mod-dir D] [--plant-check]
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
DEFAULT_MOD = os.path.join(SRC, "RimMandrake", "Webwork")


def read(p):
    return open(p, encoding="utf-8-sig").read()


def adjacent(a, b):
    """The kernel's rule: b has a cell inside a expanded by one. Rects are (minX, minZ, maxX, maxZ)."""
    return b[0] <= a[2] + 1 and b[2] >= a[0] - 1 and b[1] <= a[3] + 1 and b[3] >= a[1] - 1


def xml_root(p):
    return ET.fromstring(read(p).encode("utf-8"))


def main(argv):
    quiet = "--quiet" in argv
    mod = argv[argv.index("--mod-dir") + 1] if "--mod-dir" in argv else DEFAULT_MOD
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        rc = lint_mod_defs.run("Webwork", ["--mod-dir", mod])
    gl = buf.getvalue().splitlines()
    if rc == 2:
        print("\n".join(gl))
        return 2
    errs = [l for l in gl if l.startswith("ERROR")]
    warns = [l for l in gl if l.startswith("WARN")]
    E = lambda c, m: errs.append(f"ERROR {c}: {m}")
    W = lambda c, m: warns.append(f"WARN  {c}: {m}")
    src = os.path.join(mod, "Source")
    kernel = read(os.path.join(src, "Kernel", "RM_WebworkKernel.cs"))
    remains = read(os.path.join(src, "RM_UrravethRemains.cs"))
    settings = read(os.path.join(src, "RM_WebworkMod.cs"))
    defs = os.path.join(mod, "Defs")
    n = {"pieces": 0, "sliders": 0, "factors": 0, "neighbours": 0}

    # ---- the skeleton ----
    layout = [(m.group(1), int(m.group(2)), int(m.group(3))) for m in re.finditer(r'\("(RM_Urraveth_\w+)", (\d+), (\d+)\)', remains)]
    sw = re.search(r"SiteWidth = (\d+), SiteHeight = (\d+)", remains)
    root = xml_root(os.path.join(defs, "ThingDefs_Buildings", "RM_Urraveth_Remains.xml"))
    xml = {}
    for td in root.iter("ThingDef"):
        dn = td.findtext("defName")
        if not dn:
            continue
        ext = td.find("modExtensions/li")
        sz = re.match(r"\((\d+),\s*(\d+)\)", td.findtext("size") or "")
        xml[dn] = dict(size=(int(sz.group(1)), int(sz.group(2))) if sz else None,
                       rank=int(ext.findtext("supportRank")) if ext is not None and ext.findtext("supportRank") else None,
                       cap=float(ext.findtext("loadCapacity")) if ext is not None and ext.findtext("loadCapacity") else None,
                       chapter=ext.findtext("chapter") if ext is not None else None,
                       skull=(ext.findtext("isSkull") == "true") if ext is not None else False,
                       examine=int(ext.findtext("examineTicks")) if ext is not None and ext.findtext("examineTicks") else 3000)
    base = next((td for td in root.iter("ThingDef") if td.get("Name") == "RM_UrravethPieceBase"), None)
    if base is None or base.findtext("tickerType") != "Rare":
        E("ww-urraveth-layout", "RM_UrravethPieceBase is not tickerType Rare: StepLoad runs from TickRare, so the bones would never creak")
    if "public override void TickRare()" not in remains:
        E("ww-urraveth-layout", "RM_Building_UrravethPiece no longer overrides TickRare")
    if not layout or not sw:
        print("LINT UNMEASURED: urraveth Layout / site size not parsed from RM_UrravethRemains.cs")
        return 2
    SW, SH = int(sw.group(1)), int(sw.group(2))
    rects, rows = [], []
    for name, x, z in layout:
        d = xml.get(name)
        if d is None or d["size"] is None or d["rank"] is None or d["cap"] is None:
            E("ww-urraveth-layout", f"Layout names {name} but RM_Urraveth_Remains.xml has no complete def (size / supportRank / loadCapacity) for it")
            continue
        n["pieces"] += 1
        w, h = d["size"]
        if x < 0 or z < 0 or x + w > SW or z + h > SH:
            E("ww-urraveth-layout", f"{name} at ({x},{z}) size {w}x{h} leaves the {SW}x{SH} site")
        rects.append((x, z, x + w - 1, z + h - 1))
        rows.append((name, d))
        if d["cap"] <= 0:
            E("ww-urraveth-layout", f"{name} loadCapacity {d['cap']} <= 0: it is overloaded the moment it is placed")
        if d["examine"] < 60:
            W("ww-urraveth-layout", f"{name} examineTicks {d['examine']} below the kernel floor of 60")
    for i in range(len(rects)):
        for j in range(i + 1, len(rects)):
            a, b = rects[i], rects[j]
            if not (b[0] > a[2] or b[2] < a[0] or b[1] > a[3] or b[3] < a[1]):
                E("ww-urraveth-layout", f"{rows[i][0]}#{i} and {rows[j][0]}#{j} overlap")
    skulls = [i for i, (_nm, d) in enumerate(rows) if d["skull"]]
    if len(skulls) != 1:
        E("ww-urraveth-layout", f"{len(skulls)} skulls in the layout (exactly one holds the last wrapping)")
    elif rows[skulls[0]][1]["rank"] != max(d["rank"] for _n, d in rows):
        E("ww-urraveth-layout", "the skull is not the highest-ranked piece")
    order = re.search(r"ChapterOrder = \{([^}]*)\}", kernel)
    chapters = re.findall(r'"(\w+)"', order.group(1)) if order else []
    have = sorted(set(d["chapter"] for _n, d in rows))
    if sorted(chapters) != have or len(chapters) != 4:
        E("ww-urraveth-layout", f"the kernel's ChapterOrder {chapters} is not the set of chapters the pieces carry {have}")
    for i, (name, d) in enumerate(rows):
        if d["rank"] == 0:
            continue
        lower = [rows[j][0] for j in range(len(rows)) if j != i and rows[j][1]["rank"] < d["rank"] and adjacent(rects[i], rects[j])]
        n["neighbours"] += len(lower)
        if not lower:
            E("ww-urraveth-layout", f"{name}#{i} (rank {d['rank']}) touches no piece of lower rank: nothing below it can ever load it")
    seen, stack = {0}, [0]
    while stack and rects:
        i = stack.pop()
        for j in range(len(rects)):
            if j not in seen and adjacent(rects[i], rects[j]):
                seen.add(j)
                stack.append(j)
    if rects and len(seen) != len(rects):
        E("ww-urraveth-layout", f"the skeleton is not connected: {len(seen)} of {len(rects)} pieces reachable by adjacency")
    fz = os.path.join(src, "SelfTest", "WebworkFuzz.cs")
    if os.path.exists(fz):
        frows = [(m.group(1), m.group(2), m.group(3) == "true", int(m.group(4)), float(m.group(5)), int(m.group(6)), int(m.group(7)), int(m.group(8)), int(m.group(9)))
                 for m in re.finditer(r'\("(\w+)", "(\w+)", (true|false), (\d+), ([0-9.]+)f, (\d+), (\d+), (\d+), (\d+)\)', read(fz))]
        want = []
        for (name, x, z), (_n, d) in zip(layout, rows):
            want.append((name.replace("RM_Urraveth_", ""), d["chapter"], d["skull"], d["rank"], d["cap"], x, z, d["size"][0], d["size"][1]))
        if frows != want:
            E("ww-urraveth-layout", "the fuzz's copy of the layout differs from the mod's (Layout + XML): " + str([r for r in frows if r not in want][:2]))
    if "HeavyDamageFraction = RM_UrravethKernel.HeavyDamageFraction" not in remains:
        E("ww-urraveth-layout", "RM_Urraveth.HeavyDamageFraction is no longer an alias of the kernel's")

    # ---- settings ranges ----
    fields = dict((m.group(1), float(m.group(2))) for m in re.finditer(r"public static (?:float|int) (\w+) = ([0-9.]+)f?;", settings))
    sl = {}
    for m in re.finditer(r"(\w+) = (?:Mathf\.RoundToInt\()?list\.Slider\((?:\1, )([0-9.]+)f, ([0-9.]+)f\)", settings):
        sl[m.group(1)] = (float(m.group(2)), float(m.group(3)))
    for nm, (lo, hi) in sl.items():
        n["sliders"] += 1
        if nm in fields and not (lo <= fields[nm] <= hi):
            E("ww-settings", f"{nm} default {fields[nm]} lies outside its slider {lo}..{hi}")
    if not sl:
        print("LINT UNMEASURED: no Mod Settings sliders parsed from RM_WebworkMod.cs")
        return 2
    if "urravethWarningHours" in sl and sl["urravethWarningHours"][0] * 2500 < 250:
        E("ww-settings", "the shortest creak warning is below one rare tick")
    if "eggRelayIntervalMultiplier" in sl and sl["eggRelayIntervalMultiplier"][0] < 0.01:
        E("ww-settings", "the relay multiplier slider can go below the kernel's 0.01 floor")
    if "urravethSiteChance" in sl and not (sl["urravethSiteChance"][0] >= 0 and sl["urravethSiteChance"][1] <= 1):
        E("ww-settings", "urravethSiteChance slider leaves 0..1")
    if "frontCreepIntervalMultiplier" in sl and sl["frontCreepIntervalMultiplier"][0] <= 0:
        E("ww-settings", "front creep interval slider reaches 0 (an advance every tick)")
    ttext = re.search(r"half as likely", settings)
    gate = read(os.path.join(src, "RM_WebworkStartupGate.cs"))
    if not ttext or "commonality = 0.05f" not in gate:
        W("ww-settings", "the thrixweave setting text no longer says 'half as likely' beside the gate's 0.05 commonality")

    # ---- the traction lance ----
    lance = xml_root(os.path.join(defs, "ThingDefs_Buildings", "RM_TractionLance.xml")).find("ThingDef")
    fac = {}
    for li in lance.findall("modExtensions/li/factors/li"):
        fac[li.findtext("stuff")] = tuple(float(li.findtext(k)) for k in ("range", "strength", "reel", "snap"))
    n["factors"] = len(fac)
    ladder = ["Cloth", "DevilstrandCloth", "Hyperweave"]
    if sorted(fac) != sorted(ladder):
        E("ww-lance", f"tether factors name {sorted(fac)}, expected {sorted(ladder)}")
    else:
        for k, nm in ((0, "range"), (1, "strength"), (2, "reel")):
            if not (fac[ladder[0]][k] < fac[ladder[1]][k] < fac[ladder[2]][k]):
                E("ww-lance", f"{nm} is not strictly cloth < devilstrand < thrixweave: {[fac[s][k] for s in ladder]}")
        if not (fac[ladder[0]][3] > fac[ladder[1]][3] > fac[ladder[2]][3]):
            E("ww-lance", f"snap is not strictly cloth > devilstrand > thrixweave: {[fac[s][3] for s in ladder]}")
    fuel = sorted(e.text for e in lance.findall(".//comps/li[@Class='CompProperties_Refuelable']/fuelFilter/thingDefs/li"))
    if fuel != sorted(ladder):
        E("ww-lance", f"the rigging fuel filter {fuel} is not the fabrics the tether ladder names {sorted(ladder)}")
    if [e.text for e in lance.findall("stuffCategories/li")] != ["Fabric"]:
        E("ww-lance", "the lance is no longer stuffed by Fabric alone (the stuff IS the tether)")
    res = [e.text for e in lance.findall("researchPrerequisites/li")]
    rproj = xml_root(os.path.join(defs, "ResearchProjectDefs", "RM_Research_TractionLance.xml")).find("ResearchProjectDef")
    if res != [rproj.findtext("defName")]:
        E("ww-lance", f"researchPrerequisites {res} is not the shipped project {rproj.findtext('defName')}")
    req = [e.text for e in rproj.findall("requiredAnalyzed/li")]
    gj = xml_root(os.path.join(defs, "ThingDefs_Items", "RM_GutterJunction.xml")).find("ThingDef")
    if req != [gj.findtext("defName")]:
        E("ww-lance", f"the research needs {req} analysed but the junction def is {gj.findtext('defName')}")
    grants = [e.text for e in gj.findall(".//grantsResearch/li")]
    if rproj.findtext("defName") not in grants:
        E("ww-lance", "studying the gutter junction does not grant the traction lance research (it would stay locked)")
    if gj.findtext("stackLimit") != "1":
        E("ww-lance", "the gutter junction stacks: an analyzable item must be single")
    cb = os.path.join(SRC, "RimMandrake", "CreatureBehaviors", "Source")
    ext_src = ""
    for p in glob.glob(os.path.join(cb, "**", "*.cs"), recursive=True):
        t = read(p)
        if "class RM_TetherStuffExtension" in t:
            ext_src = t
    if not ext_src:
        print("LINT UNMEASURED: RM_TetherStuffExtension not found in CreatureBehaviors")
        return 2
    for ch in lance.find("modExtensions/li"):
        if ch.tag not in ("factors",) and not re.search(r"public \w+ " + ch.tag + r"\b", ext_src):
            E("ww-lance", f"the lance sets <{ch.tag}> but RM_TetherStuffExtension has no such field")
    ids = set(re.findall(r"<analysisID>(\d+)</analysisID>", read(os.path.join(defs, "ThingDefs_Items", "RM_GutterJunction.xml"))))
    for p in glob.glob(os.path.join(SRC, "*", "*", "Defs", "**", "*.xml"), recursive=True):
        if os.path.abspath(p).startswith(os.path.abspath(os.path.join(defs, "ThingDefs_Items", "RM_GutterJunction.xml"))):
            continue
        try:
            t = read(p)
        except OSError:
            continue
        for i in ids:
            if f"<analysisID>{i}</analysisID>" in t and os.path.basename(p) != "RM_GutterJunction.xml":
                E("ww-lance", f"analysisID {i} is reused by {os.path.relpath(p, SRC)}")

    # ---- the nest ----
    nestsrc = read(os.path.join(src, "RM_GenStep_WebworkNest.cs"))
    cdef = lambda c: re.search(c + r' = "(\w+)"', nestsrc).group(1)
    nest_xml = xml_root(os.path.join(defs, "ThingDefs_Buildings", "RM_Webwork_Nest.xml"))
    nest_names = {td.findtext("defName") for td in nest_xml.iter("ThingDef")}
    for c in ("NestWallDefName", "EggClutchDefName"):
        if cdef(c) not in nest_names:
            E("ww-nest", f"{c} = {cdef(c)} is not a ThingDef in RM_Webwork_Nest.xml")
    biome_name = cdef("WebworkBiomeDefName")
    if not any(biome_name == b.findtext("defName") for p in glob.glob(os.path.join(defs, "BiomeDefs", "*.xml")) for b in xml_root(p).iter("BiomeDef")):
        E("ww-nest", f"WebworkBiomeDefName {biome_name} is not a BiomeDef of this mod")
    relay = None
    for td in nest_xml.iter("ThingDef"):
        if td.findtext("defName") == cdef("NestWallDefName"):
            relay = td.find(".//comps/li[@Class='RimMandrake.Webwork.RM_CompProperties_EggClutchRelay']")
    if relay is None:
        E("ww-nest", "the nest wall no longer carries RM_CompProperties_EggClutchRelay (no egg economy)")
    else:
        if relay.findtext("relayIntervalDays") != "20~30":
            E("ww-nest", f"relayIntervalDays {relay.findtext('relayIntervalDays')} is not the ruled 20~30")
        mr = relay.findtext("motherRaceDefName")
        races = {td.findtext("defName") for p in glob.glob(os.path.join(defs, "ThingDefs_Races", "*.xml")) for td in xml_root(p).iter("ThingDef")}
        if mr not in races:
            E("ww-nest", f"motherRaceDefName {mr} is not a race this mod defines")
        ec = relay.findtext("eggClutchDefName")
        if ec is not None and ec != cdef("EggClutchDefName"):
            E("ww-nest", f"the relay lays {ec} but the nest gen step places {cdef('EggClutchDefName')}")
    if "20f, 30f" not in read(os.path.join(src, "RM_CompEggClutchRelay.cs")) or "20-30 days" not in settings:
        E("ww-nest", "the relay comp default range or the settings text no longer says 20-30 days")
    steps = {}
    for p in glob.glob(os.path.join(defs, "MapGeneration", "*.xml")):
        for g in xml_root(p).iter("GenStepDef"):
            steps[g.findtext("defName")] = (int(g.findtext("order")), g.find("genStep").get("Class"))
    if steps.get("RM_WebworkNestScatter", (0,))[0] >= steps.get("RM_UrravethRemainsScatter", (0,))[0] > 0:
        E("ww-nest", "the nest does not generate before the skeleton: the skeleton's footprint search could wipe the nest")
    patched = " ".join(read(p) for p in glob.glob(os.path.join(mod, "Patches", "*MapGenPatch.xml")))
    for sname in steps:
        if f"<li>{sname}</li>" not in patched:
            E("ww-nest", f"GenStepDef {sname} is not added to MapCommonBase by any patch (it would never run)")
    nbiome = xml_root(os.path.join(defs, "BiomeDefs", "RM_Webwork_Biome.xml"))
    if not any(b.findtext("workerClass") == "RimMandrake.Webwork.RM_BiomeWorker_Webwork" for b in nbiome.iter("BiomeDef")):
        E("ww-nest", "the Webwork BiomeDef no longer names RM_BiomeWorker_Webwork (it would never generate on a new world)")

    # ---- the thrixweave economy neighbours ----
    rename = read(os.path.join(mod, "Patches", "RM_Thrixweave_Rename.xml"))
    for xp in ("Defs/ThingDef[defName=\"Hyperweave\"]/label", "Defs/ThingDef[defName=\"Hyperweave\"]/description"):
        if xp not in rename:
            E("ww-economy", f"RM_Thrixweave_Rename.xml no longer replaces {xp}")
    eco = os.path.join(SRC, "RimUtinni", "ShokkweaveEconomy")
    if os.path.isdir(eco):
        about = read(os.path.join(eco, "About", "About.xml"))
        la = re.search(r"<loadAfter>(.*?)</loadAfter>", about, flags=re.S)
        if not la or "mandrake.rm.webwork" not in la.group(1):
            E("ww-economy", "ShokkweaveEconomy does not load after mandrake.rm.webwork: its Shokkweave relabel would be overwritten by the thrixweave one")
        for p in glob.glob(os.path.join(eco, "Patches", "*.xml")):
            t = read(p)
            if "Hyperweave" in t and "ThingDef[defName=\"Hyperweave\"]" in t and "PatchOperationReplace" not in t and "PatchOperationAdd" not in t:
                W("ww-economy", f"{os.path.basename(p)} names Hyperweave without a replace / add operation")
        owners = {"Webwork", "ShokkweaveEconomy", "CreatureBehaviors"}
        for p in glob.glob(os.path.join(SRC, "*", "*", "**", "*.xml"), recursive=True):
            if os.sep + "Textures" + os.sep in p:
                continue
            parts = os.path.relpath(p, SRC).split(os.sep)
            if parts[1] in owners:
                continue
            try:
                t = read(p)
            except OSError:
                continue
            if "Hyperweave" in t and re.search(r"stockGenerators|thingDefs|ThingDef\b.*Hyperweave", t) and "TraderKindDef" in t and re.search(r"<thingDefs>.*?Hyperweave", t, flags=re.S):
                E("ww-economy", f"{os.path.relpath(p, SRC)} stocks Hyperweave on a trader outside the sole-source owners")
    ccs = re.search(r'GetField\("(\w+)"\)', gate)
    fc = ""
    for p in glob.glob(os.path.join(cb, "**", "RM_FrontCreepExtension.cs"), recursive=True):
        fc = read(p)
    if not ccs or not fc or not re.search(r"public int " + ccs.group(1) + r"\b", fc):
        E("ww-economy", "the startup gate reflects a front-extension field that does not exist on RM_FrontCreepExtension (the creep interval would never scale)")
    if '"RM_FrontCreepExtension"' not in gate:
        E("ww-economy", "the startup gate no longer matches the extension by its type name")
    biome_has = any("RM_FrontCreepExtension" in (read(p)) for p in glob.glob(os.path.join(defs, "BiomeDefs", "*.xml")))
    if not biome_has:
        W("ww-economy", "the Webwork BiomeDef carries no RM_FrontCreepExtension: the front-creep toggle gates nothing")

    # ---- kernel / csproj / emergent comp ----
    if re.search(r"^\s*using\s+(Verse|RimWorld|UnityEngine|HarmonyLib)", kernel, flags=re.M):
        E("ww-kernel-pure", "the kernel imports Verse/RimWorld/UnityEngine/HarmonyLib (the fuzz build would break)")
    proj = read(os.path.join(src, "RM_Webwork.csproj"))
    if 'Compile Include="Kernel\\RM_WebworkKernel.cs"' not in proj:
        E("ww-kernel-pure", "the kernel is not listed in RM_Webwork.csproj (it compiles into nothing, silently)")
    if "SelfTest" in proj:
        E("ww-kernel-pure", "the SelfTest folder is compiled into the mod assembly")
    attached = [p for p in glob.glob(os.path.join(SRC, "*", "*", "Defs", "**", "*.xml"), recursive=True)
                if "RM_CompProperties_EmergentSpawnOnDestroy\">" in read(p)]
    if not attached:
        W("ww-kernel-pure", "no def attaches RM_CompProperties_EmergentSpawnOnDestroy: the emergent-spawn settings gate nothing yet (SHOKKWEAVE_SOLE_SOURCE_1)")
    for p in attached:
        for ch in xml_root(p).iter("li"):
            if (ch.get("Class") or "").endswith("RM_CompProperties_EmergentSpawnOnDestroy"):
                sc = float(ch.findtext("spawnChance") or 0.03)
                if not (0 < sc <= 1):
                    E("ww-kernel-pure", f"{os.path.basename(p)} spawnChance {sc} outside (0, 1]")

    if not quiet:
        for l in warns:
            print(l)
    for l in errs:
        print(l)
    print(f"webwork lint (data): {n['pieces']} skeleton pieces ({n['neighbours']} support links), {n['sliders']} slider ranges, "
          f"{n['factors']} tether factors, {len(errs)} ERROR, {len(warns)} WARN")
    return 1 if errs else 0


PLANTS = [
    ("hind legs back at z 1", "Source/RM_UrravethRemains.cs", '("RM_Urraveth_LimbPile", 1, 2)', '("RM_Urraveth_LimbPile", 1, 1)'),
    ("piece off the site", "Source/RM_UrravethRemains.cs", '("RM_Urraveth_Skull", 12, 4)', '("RM_Urraveth_Skull", 14, 4)'),
    ("two pieces overlap", "Source/RM_UrravethRemains.cs", '("RM_Urraveth_RibSection", 6, 3)', '("RM_Urraveth_RibSection", 5, 3)'),
    ("pieces stop ticking", "Defs/ThingDefs_Buildings/RM_Urraveth_Remains.xml", "<tickerType>Rare</tickerType>", "<tickerType>Never</tickerType>"),
    ("chapter order drifts", "Source/Kernel/RM_WebworkKernel.cs", '"pinned", "bound", "cut", "eaten"', '"pinned", "bound", "cut", "devoured"'),
    ("slider default outside its range", "Source/RM_WebworkMod.cs", "urravethWarningHours = list.Slider(urravethWarningHours, 1f, 24f)", "urravethWarningHours = list.Slider(urravethWarningHours, 8f, 24f)"),
    ("tether ladder inverted", "Defs/ThingDefs_Buildings/RM_TractionLance.xml", "<strength>1.6</strength>", "<strength>0.5</strength>"),
    ("rigging accepts a fabric the ladder lacks", "Defs/ThingDefs_Buildings/RM_TractionLance.xml", "<li>DevilstrandCloth</li>\n            <li>Hyperweave</li>", "<li>DevilstrandCloth</li>\n            <li>Hyperweave</li>\n            <li>Synthread</li>"),
    ("junction grants nothing", "Defs/ThingDefs_Items/RM_GutterJunction.xml", "<li>RM_Research_TractionLance</li>", "<li>RM_Research_Nothing</li>"),
    ("relay range drifts", "Defs/ThingDefs_Buildings/RM_Webwork_Nest.xml", "<relayIntervalDays>20~30</relayIntervalDays>", "<relayIntervalDays>2~3</relayIntervalDays>"),
    ("skeleton generates before the nest", "Defs/MapGeneration/RM_UrravethRemains.xml", "<order>325</order>", "<order>300</order>"),
    ("skeleton step unpatched", "Patches/RM_UrravethRemains_MapGenPatch.xml", "<li>RM_UrravethRemainsScatter</li>", "<li>RM_UrravethRemainsScatterX</li>"),
    ("front field renamed in the gate", "Source/RM_WebworkStartupGate.cs", 'GetField("advanceIntervalTicks")', 'GetField("advanceTicks")'),
    ("kernel imports Verse", "Source/Kernel/RM_WebworkKernel.cs", "using System;", "using System;\nusing Verse;"),
    ("kernel missing from csproj", "Source/RM_Webwork.csproj", '<Compile Include="Kernel\\RM_WebworkKernel.cs" />', ""),
]


def plant_check():
    import shutil
    import subprocess
    import tempfile
    caught = 0
    for name, rel, old, new in PLANTS:
        with tempfile.TemporaryDirectory() as td:
            dst = os.path.join(td, "Webwork")
            shutil.copytree(DEFAULT_MOD, dst, ignore=shutil.ignore_patterns("__pycache__", "Assemblies", "bin", "obj", "Textures", "art", "Languages", "SelfTest"))
            f = os.path.join(dst, rel)
            t = open(f, encoding="utf-8").read()
            if old not in t:
                print("PLANT TARGET NOT FOUND:", name)
                continue
            open(f, "w", encoding="utf-8").write(t.replace(old, new, 1))
            r = subprocess.run([sys.executable, os.path.abspath(__file__), "--quiet", "--mod-dir", dst], capture_output=True, text=True)
            hit = [l for l in (r.stdout + r.stderr).splitlines() if l.startswith("ERROR") or "Traceback" in l]
            print(("CAUGHT  " if hit else "MISSED  ") + name + ("  " + hit[0][:110] if hit else ""))
            caught += bool(hit)
    print(f"{caught}/{len(PLANTS)} planted defects caught")
    return 0 if caught == len(PLANTS) else 1


if __name__ == "__main__":
    if "--plant-check" in sys.argv:
        sys.exit(plant_check())
    sys.exit(main(sys.argv[1:]))
