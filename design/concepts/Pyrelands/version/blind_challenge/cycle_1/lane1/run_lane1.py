#!/usr/bin/env python3
"""Run blind lane 1 (Pyrelands 0.1.0, cycle 1) against the shipped kernels, or with one kernel file swapped.
    python3 run_lane1.py [--kernel <path> ...] [--src <Pyrelands mod dir>] [--out <rows.jsonl>]
Stages BlindLane1.cs + the six kernel files under <agent storage>/scratch/pyre_blind_lane1 (dotnet.exe cannot build from a
WSL path), builds and runs it with the per-user Windows dotnet, adds the def/text rows read from the mod's XML here, writes
one JSON row per line and prints the verdict counts. Exit 0 = every decided row PASS (INFO/UNSETTLED do not fail)."""
import argparse, glob, json, os, re, shutil, subprocess, sys
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, *[".."] * 7))
MOD = os.path.join(REPO, "src/RimMandrake/Pyrelands")
KERNELS = ["Kernel/RM_FireEcoKernel.cs", "Kernel/RM_BurnKernel.cs", "Kernel/RM_FireHawkKernel.cs",
           "Kernel/RM_FireHawkRewardsKernel.cs", "Kernel/RM_FurnaceKernel.cs", "FurnaceWarmthMath.cs"]
CSPROJ = """<Project Sdk="Microsoft.NET.Sdk"><PropertyGroup><OutputType>Exe</OutputType><TargetFramework>net8.0</TargetFramework>
<LangVersion>latest</LangVersion><Nullable>disable</Nullable><ImplicitUsings>disable</ImplicitUsings></PropertyGroup></Project>"""
# vanilla textures our defs reuse on purpose (Core paths; a directory of the same name also exists under our Textures)
VANILLA_TEX = {"Terrain/Surfaces/Sand", "Terrain/Surfaces/Gravel", "Terrain/Surfaces/Soil", "Terrain/Surfaces/SoilRich", "Things/Item/Special/ThrumboHorn"}
RAIN_WEATHERS = {"Rain", "FoggyRain", "RainyThunderstorm", "SnowGentle", "SnowHard"}  # vanilla wet weathers (snow: wet too)


def row(id_, bars, kind, ok, cases, detail, verdict=None):
    return {"id": id_, "bars": bars, "kind": kind, "verdict": verdict or ("PASS" if ok else "FAIL"), "cases": cases, "detail": detail}


def defs(src):
    out = {}
    for p in glob.glob(os.path.join(src, "Defs", "**", "*.xml"), recursive=True):
        try:
            root = ET.parse(p).getroot()
        except ET.ParseError as e:
            out.setdefault("__parse_errors__", []).append("%s: %s" % (p, e))
            continue
        for d in root:
            key = d.findtext("defName") or d.get("Name")
            if key:
                out[(d.tag, key)] = (d, p)
    return out


def resolve(dd, tag, name, path):
    """A field through ParentName inheritance (abstract parents by Name)."""
    seen = 0
    node = dd.get((tag, name), (None, None))[0]
    while node is not None and seen < 10:
        v = node.find(path)
        if v is not None:
            return v
        parent = node.get("ParentName")
        node = next((n for (t, k), (n, _) in dd.items() if t == tag and k == parent and (n.get("Name") == parent or n.findtext("defName") == parent)), None)
        seen += 1
    return None


def def_rows(src):
    rows = []
    dd = defs(src)
    if dd.get("__parse_errors__"):
        rows.append(row("def_xml_parses", ["inv_biome_self_contained"], "fixed", False, 1, "; ".join(dd["__parse_errors__"])[:400]))
    biomes = [(k, v) for k, v in dd.items() if k[0] == "BiomeDef" and v[0].findtext("defName")]
    pyre = next((v[0] for k, v in biomes if k[1] in ("RM_Pyrelands", "RM_FE_Pyrelands")), None)
    name = pyre.findtext("defName") if pyre is not None else None
    desc = (pyre.findtext("description") or "") if pyre is not None else ""
    lang = glob.glob(os.path.join(src, "Languages", "*", "DefInjected", "BiomeDef", "*.xml"))
    rows.append(row("def_biome_text_says_engineered", ["biome_text_says_engineered"], "fixed",
                    "genetically engineered" in desc.lower() and not lang, 1,
                    "BiomeDef %s description %s 'genetically engineered'; DefInjected BiomeDef overrides: %d" % (name, "holds" if "genetically engineered" in desc.lower() else "LACKS", len(lang))))
    rows.append(row("def_biome_text_no_migration_promise", ["biome_text_says_engineered", "inv_ullai_herd_giant"], "fixed",
                    "migrat" not in desc.lower(), 1, "the description never promises the cut world migration"))
    wl = [c.tag for c in pyre.find("baseWeatherCommonalities")] if pyre is not None and pyre.find("baseWeatherCommonalities") is not None else []
    wet = [w for w in wl if w in RAIN_WEATHERS]
    rows.append(row("def_no_ordinary_rain_on_weather_list", ["no_ordinary_rain", "inv_weather"], "fixed", bool(wl) and not wet, len(wl),
                    "weather list %s; vanilla wet weathers on it: %s" % (",".join(wl), wet or "none")))
    ours = {k[1]: v[0] for k, v in dd.items() if k[0] == "WeatherDef"}
    rr = {n: float(d.findtext("rainRate") or 0) for n, d in ours.items()}
    wet_ours = [n for n, r in rr.items() if r > 0 and n != "RM_FE_BlackRain"]
    rows.append(row("def_only_black_rain_is_wet", ["no_ordinary_rain", "three_skies"], "fixed", rr.get("RM_FE_BlackRain", 0) > 0 and not wet_ours, len(rr),
                    "rainRate of our weathers: %s" % rr))
    cin = ours.get("RM_FE_Weather_Cinderfall")
    ev = [e.text for e in cin.iter("li")] if cin is not None else []
    rows.append(row("def_cinderfall_brings_lightning", ["three_skies"], "fixed", any("Lightning" in (e or "") for e in ev) or (cin is not None and "Lightning" in ET.tostring(cin, encoding="unicode")), 1,
                    "Cinderfall event makers / text name a lightning strike"))
    dens = float(pyre.findtext("animalDensity") or 0) if pyre is not None else 0
    wp = [c.tag for c in pyre.find("wildPlants")] if pyre is not None and pyre.find("wildPlants") is not None else []
    rows.append(row("def_roster_natives_and_density", ["populations_are_the_biomes_own", "inv_plant_roster"], "fixed",
                    dens > 0 and bool(wp) and all(p.startswith("RM_FE_Plant_") for p in wp) and "RM_FE_Plant_ScorchFruit" not in wp, len(wp) + 1,
                    "animalDensity %s; wildPlants %s" % (dens, wp)))
    # firebreak and lightning breaker stay excised (shipped files, not the mod's own selftests)
    hits_fb, hits_br = [], []
    for p in glob.glob(os.path.join(src, "**", "*"), recursive=True):
        if os.path.isdir(p) or "/SelfTest/" in p or p.endswith((".py", ".pyc", ".dll", ".png", ".pdb", ".srchash")) or "/__pycache__/" in p or "/obj/" in p or "/bin/" in p:
            continue
        try:
            t = open(p, encoding="utf-8", errors="replace").read()
        except OSError:
            continue
        for m in re.finditer(r"firebreak", t, re.I):
            line = t[t.rfind("\n", 0, m.start()) + 1: t.find("\n", m.end())]
            if "SCORCH_FRUIT_FIX_LANDS_ON_FIREBREAK" not in line:
                hits_fb.append(os.path.relpath(p, src))
        if re.search(r"breaker|fulgurite", t, re.I):
            hits_br.append(os.path.relpath(p, src))
    fbfile = os.path.exists(os.path.join(src, "Defs/TerrainDefs/Firebreak.xml"))
    rows.append(row("def_firebreak_stays_excised", ["inv_firebreak_firefoam"], "fixed", not fbfile and not hits_fb, 1,
                    "Firebreak.xml %s; other 'firebreak' mentions (item-name comments excepted): %s" % ("present" if fbfile else "absent", sorted(set(hits_fb)) or "none")))
    rows.append(row("def_lightning_breaker_stays_excised", ["inv_lightning_breaker"], "fixed", not hits_br, 1,
                    "breaker/fulgurite in shipped files: %s" % (sorted(set(hits_br)) or "none")))
    # no ordinary rain: the chooser postfix is compiled and aimed at WeatherDecider.ChooseNextWeather (RAIN_FIX_FORCED_WEATHER_SKIPS_THE_LIST)
    csproj = open(os.path.join(src, "Source/FireEcologyHook.csproj")).read()
    pf = os.path.join(src, "Source/PyrelandsNoOrdinaryRain.cs")
    pt = open(pf).read() if os.path.exists(pf) else ""
    wired = 'Include="PyrelandsNoOrdinaryRain.cs"' in csproj and '"ChooseNextWeather"' in pt and "RainBecomesBlackRain(" in pt and "__result = blackRain" in pt
    rows.append(row("rain_chooser_postfix_wired", ["no_ordinary_rain", "inv_weather"], "fixed", wired, 1,
                    "PyrelandsNoOrdinaryRain.cs %s, compiled: %s" % ("present" if pt else "absent", 'Include="PyrelandsNoOrdinaryRain.cs"' in csproj)))
    # sand shovel
    sand = dd.get(("TerrainDef", "RM_FE_Ground_Sand"), (None,))[0]
    ext = sand.find("modExtensions/li") if sand is not None else None
    ok = ext is not None and ext.findtext("count") == "5" and ext.findtext("leaves") == "RM_FE_Ground_Gravel" and ext.findtext("yield") == "RM_GlassSand"
    ash = dd.get(("TerrainDef", "RM_FE_Ash_Deep"), (None,))[0]
    ash_dig = ash is not None and ash.find("modExtensions") is not None and "TerrainDig" in ET.tostring(ash, encoding="unicode")
    rows.append(row("def_sand_yields_five_leaves_gravel", ["sand_shovel_yields_glass_sand", "inv_sand_shovel"], "fixed", ok and not ash_dig, 2,
                    "RM_FE_Ground_Sand -> %s x%s, leaves %s; deep ash diggable: %s" % (ext.findtext("yield") if ext is not None else None, ext.findtext("count") if ext is not None else None, ext.findtext("leaves") if ext is not None else None, ash_dig)))
    # giant
    fb = dd.get(("ThingDef", "RM_FurnaceBeast"), (None,))[0]
    bs = fb.findtext("race/baseBodySize") if fb is not None else None
    rows.append(row("def_furnacebeast_body_size_6", ["furnacebeast_warms", "inv_furnacebeast"], "fixed", bs is not None and abs(float(bs) - 6) < 1e-6, 1, "RM_FurnaceBeast baseBodySize %s" % bs))
    # scorch-fruit
    sp = dd.get(("ThingDef", "RM_FE_Plant_ScorchFruit"), (None,))[0]
    sy = dd.get(("ThingDef", "RM_FE_ScorchFruitYield"), (None,))[0]
    prot = float(sp.findtext(".//daysToRotStart") or 99) if sp is not None else 99
    yrot = float(sy.findtext(".//daysToRotStart") or 99) if sy is not None else 99
    nut = sy is not None and (sy.find(".//ingestible") is not None or "Nutrition" in ET.tostring(sy, encoding="unicode"))
    rows.append(row("def_scorchfruit_rots_fast_and_feeds", ["scorchfruit_born_of_fire", "inv_scorchfruit"], "fixed",
                    prot <= 1.5 and yrot <= 4.5 and nut and sp is not None and sp.findtext(".//harvestedThingDef") == "RM_FE_ScorchFruitYield", 3,
                    "plant rots from %.2f d, picked fruit from %.2f d; fruit ingestible: %s" % (prot, yrot, nut)))
    # deep ash fertility and the grasses' floor
    af = resolve(dd, "TerrainDef", "RM_FE_Ash_Deep", "fertility")
    ef = float(dd.get(("ThingDef", "RM_FE_Plant_EmberGrass"), (None,))[0].findtext(".//fertilityMin") or 9)
    rows.append(row("def_deep_ash_fertility_70_grass_sowable", ["ash_fertile_when_watered", "grass_carpets_and_regreens"], "fixed",
                    af is not None and abs(float(af.text) - 0.70) < 1e-6 and ef <= 0.70, 2, "RM_FE_Ash_Deep fertility %s; ember grass fertilityMin %s" % (af.text if af is not None else None, ef)))
    # venom wiring
    tool = dd.get(("ToolCapacityDef", "RM_FlamefangBite"), (None,))[0]
    dmg = dd.get(("DamageDef", "RM_FlamefangVenomBite"), (None,))[0]
    hed = dd.get(("HediffDef", "RM_FlamefangVenom"), (None,))[0]
    txt = "".join(open(p).read() for p in glob.glob(os.path.join(src, "Defs/ThingDefs_Races/*.xml")))
    uses = len(re.findall(r"RM_FlamefangBite\b", txt))
    rows.append(row("def_flamefang_venom_wired", ["flamefang_bite_carries_venom"], "fixed",
                    dmg is not None and hed is not None and (dmg.find(".//hediff") is not None and dmg.find(".//hediff").text == "RM_FlamefangVenom") and uses >= 1, 3,
                    "damage RM_FlamefangVenomBite -> hediff %s; race files naming the bite damage: %d; tool def %s" % (dmg.find('.//hediff').text if dmg is not None and dmg.find('.//hediff') is not None else None, uses, "present" if tool is not None else "absent")))
    # art: every texPath under one of our own texture roots resolves
    tex = os.path.join(src, "Textures")
    roots = {d for d in os.listdir(tex)} if os.path.isdir(tex) else set()
    miss, n = [], 0
    for (t, k), (d, p) in dd.items():
        for e in d.iter():
            if e.tag in ("texPath", "texturePath", "iconPath") and e.text and e.text not in VANILLA_TEX and os.path.isdir(os.path.join(tex, os.path.dirname(e.text))):
                n += 1
                b = os.path.join(tex, e.text)
                if not (os.path.exists(b + ".png") or os.path.isdir(b) or any(os.path.exists(b + s + ".png") for s in ("_south", "_north", "_east", "_a", "A"))):
                    miss.append("%s %s" % (k, e.text))
    rows.append(row("def_own_texture_paths_resolve", ["inv_art_and_text"], "fixed", not miss, n, "texPaths under our Textures roots: %d, unresolved: %s" % (n, miss[:8] or "none")))
    # gate: the shipped defaults (worldgen off, cross-biome off, master on)
    ms = open(os.path.join(src, "Source/RM_PyrelandsMod.cs")).read()
    def default(name):
        m = re.search(r"public static \w+ %s = ([^;]+);" % name, ms)
        return m.group(1).strip() if m else None
    want = {"pyrelandsEnabled": "true", "biomeGenerationEnabled": "false", "crossBiomeEnabled": "false", "crossBiomeEverywhere": "false"}
    got = {k: default(k) for k in want}
    scribe = {k: re.search(r'Scribe_Values\.Look\(ref %s, "%s", ([^)]+)\)' % (k, k), ms) for k in want}
    sok = all(scribe[k] and scribe[k].group(1).strip() == want[k] for k in want)
    rows.append(row("def_shipped_gate_defaults", ["inv_settings_gate", "inv_biome_self_contained"], "fixed", got == want and sok, len(want),
                    "field defaults %s; Scribe defaults agree: %s" % (got, sok)))
    # every saved switch's Scribe default equals its field default (a mismatch = a reset save reads a different shipped behaviour)
    mism = []
    for m in re.finditer(r'Scribe_Values\.Look\(ref (\w+), "(\w+)", ([^)]+)\)', ms):
        f, _, dv = m.groups()
        fd = default(f)
        if fd is not None and fd.replace("f", "") != dv.strip().replace("f", "") and fd != dv.strip():
            mism.append("%s field=%s scribe=%s" % (f, fd, dv.strip()))
    rows.append(row("settings_scribe_defaults_match_fields", ["inv_settings_gate"], "sweep", not mism, len(re.findall(r"Scribe_Values\.Look", ms)),
                    "mismatches: %s" % (mism or "none")))
    return rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--kernel", action="append", default=[], help="a replacement for one kernel file (matched by basename)")
    ap.add_argument("--src", default=MOD)
    ap.add_argument("--out", default=os.path.join(HERE, "lane1_rows.jsonl"))
    a = ap.parse_args()
    root = os.environ.get("PYRE_LANE1_STAGE") or "/mnt/d/ClaudeWork/rimmandrake/scratch/pyre_blind_lane1"
    os.makedirs(root, exist_ok=True)
    for f in glob.glob(os.path.join(root, "*.cs")):
        os.remove(f)
    shutil.copy(os.path.join(HERE, "BlindLane1.cs"), root)
    swap = {os.path.basename(k): k for k in a.kernel}
    for k in KERNELS:
        b = os.path.basename(k)
        shutil.copy(swap.get(b, os.path.join(a.src, "Source", k)), os.path.join(root, b))
    open(os.path.join(root, "BlindLane1.csproj"), "w").write(CSPROJ)
    dn = sorted(glob.glob("/mnt/c/Users/*/.dotnet/dotnet.exe"))[0]
    win = subprocess.run(["wslpath", "-w", root], capture_output=True, text=True, check=True).stdout.strip()
    b = subprocess.run([dn, "build", win + "\\BlindLane1.csproj", "-c", "Release", "--nologo", "-v", "q"], capture_output=True, text=True, timeout=400)
    rows = []
    if b.returncode:
        rows.append(row("kernel_build", ["*"], "fixed", False, 1, "BUILD FAILED " + (b.stdout[-600:] + b.stderr[-300:]).replace("\n", " ")))
    else:
        r = subprocess.run([dn, win + "\\bin\\Release\\net8.0\\BlindLane1.dll"], capture_output=True, text=True, timeout=400)
        rows = [json.loads(l) for l in r.stdout.splitlines() if l.startswith("{")]
        if not rows:
            rows.append(row("kernel_run", ["*"], "fixed", False, 1, "RUN FAILED rc %s %s" % (r.returncode, r.stderr[-500:])))
    rows += def_rows(a.src)
    with open(a.out, "w") as f:
        for x in rows:
            f.write(json.dumps(x) + "\n")
    c = {}
    for x in rows:
        c[x["verdict"]] = c.get(x["verdict"], 0) + 1
    print("LANE1", json.dumps(c), "rows", len(rows), "->", a.out)
    for x in rows:
        if x["verdict"] == "FAIL":
            print("FAIL", x["id"], x["detail"][:300])
    sys.exit(1 if c.get("FAIL") else 0)


main()
