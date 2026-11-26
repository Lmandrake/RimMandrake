"""Pyrelands 0.1.0 blind challenge cycle 2, lane 1: run the blind judge's own tests.
    python3 run_lane1.py [--kernel <path>]... [--src <Pyrelands mod dir>] [--out <rows.jsonl>]
C# half: stages BlindLane1.cs with the six kernel files under /mnt/d/ClaudeWork/rimmandrake/scratch/pyrelands_blind_c2_lane1/
(dotnet.exe cannot build from a WSL path; override with PYRE_LANE1_STAGE), builds with the per-user Windows dotnet and runs it.
--kernel <file> replaces the shipped kernel of the same file name (planted faults reuse it).
Python half: the bars' offline facts read from the mod's Defs, Patches, About and settings source (--src, default the repo's).
Writes one JSON row per line; prints verdict counts. Exit 0 = no FAIL row."""
import argparse, glob, json, os, re, shutil, subprocess, sys
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, *[".."] * 7))
MOD = os.path.join(REPO, "src/RimMandrake/Pyrelands")
KERNELS = ["Source/FurnaceWarmthMath.cs", "Source/Kernel/RM_BurnKernel.cs", "Source/Kernel/RM_FireEcoKernel.cs",
           "Source/Kernel/RM_FireHawkKernel.cs", "Source/Kernel/RM_FireHawkRewardsKernel.cs", "Source/Kernel/RM_FurnaceKernel.cs"]
CSPROJ = """<Project Sdk="Microsoft.NET.Sdk"><PropertyGroup><OutputType>Exe</OutputType><TargetFramework>net8.0</TargetFramework>
<LangVersion>latest</LangVersion><Nullable>disable</Nullable><ImplicitUsings>disable</ImplicitUsings></PropertyGroup></Project>"""
ROWS = []
ORDINARY_RAIN = ["Rain", "FoggyRain", "RainyThunderstorm", "TorrentialRain"]


def row(id_, bars, kind, ok, cases, detail):
    verdict = {True: "PASS", False: "FAIL", None: "INFO" if kind == "info" else "UNSETTLED"}[ok]
    ROWS.append({"id": id_, "bars": bars, "kind": kind, "verdict": verdict, "cases": cases, "detail": detail})


def run_csharp(kernel_overrides, timeout=480):
    stage = os.environ.get("PYRE_LANE1_STAGE", "/mnt/d/ClaudeWork/rimmandrake/scratch/pyrelands_blind_c2_lane1")
    os.makedirs(stage, exist_ok=True)
    for f in glob.glob(os.path.join(stage, "*.cs")):
        os.remove(f)
    shutil.copy(os.path.join(HERE, "BlindLane1.cs"), stage)
    over = {os.path.basename(k): k for k in kernel_overrides}
    for k in KERNELS:
        b = os.path.basename(k)
        shutil.copy(over.get(b, os.path.join(MOD, k)), os.path.join(stage, b))
    open(os.path.join(stage, "BlindLane1.csproj"), "w").write(CSPROJ)
    dn = sorted(glob.glob("/mnt/c/Users/*/.dotnet/dotnet.exe"))[0]
    win = subprocess.run(["wslpath", "-w", stage], capture_output=True, text=True, check=True).stdout.strip()
    b = subprocess.run([dn, "build", win + "\\BlindLane1.csproj", "-c", "Release", "--nologo", "-v", "q"], capture_output=True, text=True, timeout=timeout)
    if b.returncode:
        row("csharp_kernels_build", KERNEL_BARS, "fixed", False, 1, "BUILD FAILED: " + (b.stdout[-600:] + b.stderr[-300:]).replace("\n", " "))
        return
    r = subprocess.run([dn, win + "\\bin\\Release\\net8.0\\BlindLane1.dll"], capture_output=True, text=True, timeout=timeout)
    got = [json.loads(l) for l in r.stdout.splitlines() if l.startswith("{")]
    if not got:
        row("csharp_kernels_run", KERNEL_BARS, "fixed", False, 1, "RUN FAILED rc %s: %s" % (r.returncode, r.stderr[-600:]))
    ROWS.extend(got)


KERNEL_BARS = ["ash_fertility_probe", "inv_settings_gate"]


def xml_files(*dirs):
    for d in dirs:
        for p in glob.glob(os.path.join(d, "**", "*.xml"), recursive=True):
            yield p


def defs_by_name(src, tag):
    out = {}
    for p in xml_files(os.path.join(src, "Defs")):
        try:
            root = ET.parse(p).getroot()
        except ET.ParseError:
            continue
        for d in root.iter(tag):
            n = d.findtext("defName")
            if n:
                out[n] = (d, p)
    return out


def strip_cs_comments(text):
    text = re.sub(r"/\*.*?\*/", "", text, flags=re.S)
    return re.sub(r"//[^\n]*", "", text)


def python_rows(src):
    biomes = defs_by_name(src, "BiomeDef")
    things = defs_by_name(src, "ThingDef")
    terrains = defs_by_name(src, "TerrainDef")
    pyre = biomes.get("RM_Pyrelands", (None, None))[0]

    # ---- biome_text_says_engineered (offline bar)
    desc = (pyre.findtext("description") if pyre is not None else "") or ""
    m = re.search(r"genetically engineered", desc, re.I)
    negated = bool(m and re.search(r"\b(not|never|no longer)\b[^.]{0,30}genetically engineered", desc, re.I))
    overrides = []
    for p in xml_files(os.path.join(src, "Patches")):
        t = open(p, encoding="utf-8").read()
        if re.search(r'RM_Pyrelands"?\]?/description', t):
            overrides.append(os.path.relpath(p, src))
    for p in glob.glob(os.path.join(src, "Languages", "**", "DefInjected", "BiomeDef", "*.xml"), recursive=True):
        t = open(p, encoding="utf-8").read()
        if "RM_Pyrelands.description" in t and "engineered" not in t:
            overrides.append(os.path.relpath(p, src) + " (injected text without the word)")
    row("biome_description_says_genetically_engineered", ["biome_text_says_engineered", "inv_art_and_text"], "fixed",
        bool(m) and not negated and not overrides and pyre is not None, 1,
        "RM_Pyrelands description: " + (repr(desc[max(0, (m.start() if m else 0) - 40):(m.end() if m else 60) + 30]) if desc else "MISSING")
        + ("; NEGATED" if negated else "") + ("; overridden by " + ", ".join(overrides) if overrides else "; no patch or DefInjected override"))
    plant_only = [n for n, (d, p) in things.items() if "engineered" in (d.findtext("description") or "").lower()]
    row("engineered_word_not_only_on_a_plant", ["biome_text_says_engineered"], "info", None, len(plant_only) + 1,
        "other defs saying engineered: " + (", ".join(sorted(plant_only)) or "none") + " (the bar's false pass is the word on a plant only)")

    # ---- inv_firebreak_firefoam (offline bar): the cut floor stays gone
    hits = []
    if glob.glob(os.path.join(src, "Defs", "**", "*irebreak*"), recursive=True):
        hits.append("a Firebreak def file")
    for n in terrains:
        if "firebreak" in n.lower():
            hits.append("TerrainDef " + n)
    for p in glob.glob(os.path.join(src, "Source", "**", "*.cs"), recursive=True):
        if "/SelfTest/" in p:
            continue
        code = strip_cs_comments(open(p, encoding="utf-8").read())
        if re.search(r"Firebreak", code):
            hits.append(os.path.relpath(p, src) + " code names Firebreak")
    for p in list(xml_files(os.path.join(src, "Patches"))) + list(xml_files(os.path.join(src, "Languages"))):
        if re.search(r"firebreak", re.sub(r"<!--.*?-->", "", open(p, encoding="utf-8").read(), flags=re.S), re.I):
            hits.append(os.path.relpath(p, src))
    about = open(os.path.join(src, "About", "About.xml"), encoding="utf-8").read()
    about_text = re.sub(r"<!--.*?-->", "", about, flags=re.S)
    if re.search(r"firebreak", about_text, re.I):
        hits.append("About.xml promises a firebreak")
    row("firebreak_floor_stays_excised", ["inv_firebreak_firefoam"], "fixed", not hits, 5,
        "no Firebreak terrain, def file, code reference, patch, language key or About promise" if not hits else "; ".join(hits))
    paving = re.search(r"pav(ed|ing)[^.]{0,80}(stop|hold|block)", about_text, re.I) or re.search(r"pav(ed|ing)[^.]{0,80}(stop|hold|block)", desc, re.I)
    row("no_text_promises_paving_stops_fire", ["inv_firebreak_firefoam"], "fixed", not paving, 2,
        "About.xml and the biome text: " + ("PROMISE FOUND: " + paving.group(0) if paving else "no promise that paving stops the ground fire (his card 2026-11-14 dropped it)"))
    spr = [n for n in things if "firefoam" in n.lower() or "sprayer" in n.lower()]
    row("firefoam_sprayer_still_ships", ["inv_firebreak_firefoam", "firefoam_sprayer_reaches_the_fruit"], "info", None, 1,
        "sprayer defs: " + (", ".join(spr) or "NONE") + " (the cut is the floor only; his root ending keeps the sprayer)")

    # ---- inv_lightning_breaker (offline bar): built once, then excised
    lb = []
    for p in glob.glob(os.path.join(src, "**", "*"), recursive=True):
        if os.path.isdir(p) or "/SelfTest/" in p or p.endswith((".dll", ".png", ".srchash", ".pdb")):
            if re.search(r"breaker|fulgurite", os.path.basename(p), re.I):
                lb.append(os.path.relpath(p, src) + " (file name)")
            continue
        if not p.endswith((".xml", ".cs")):
            continue
        t = open(p, encoding="utf-8", errors="replace").read()
        live = strip_cs_comments(t) if p.endswith(".cs") else re.sub(r"<!--.*?-->", "", t, flags=re.S)
        if re.search(r"breaker|fulgurite", live, re.I):
            lb.append(os.path.relpath(p, src))
    row("lightning_breaker_and_fulgurite_excised", ["inv_lightning_breaker"], "fixed", not lb, 1,
        "no def, code, patch, language key or texture names a lightning breaker or fulgurite" if not lb else "; ".join(lb[:8]))

    # ---- inv_settings_gate (offline bar): settings as shipped
    mod_cs = open(os.path.join(src, "Source", "RM_PyrelandsMod.cs"), encoding="utf-8").read()
    consts = {m.group(1): m.group(2) for m in re.finditer(r"public const float (\w+) = ([\d.]+)f;", mod_cs)}
    tun = open(os.path.join(src, "Source", "PyrelandsTuning.cs"), encoding="utf-8").read()

    def val(expr):
        expr = expr.strip()
        if expr in consts:
            expr = consts[expr]
        e = expr.rstrip("f")
        if e in ("true", "false"):
            return e == "true"
        if e.startswith('"'):
            return e.strip('"')
        try:
            return float(e)
        except ValueError:
            m = re.match(r"(\w+) \* ([\d.]+)f?$", expr)
            if m and m.group(1) in consts:
                return float(consts[m.group(1)]) * float(m.group(2))
            return None
    cls = mod_cs[mod_cs.index("class RM_PyrelandsSettings"):]
    fields = {m.group(2): val(m.group(3)) for m in re.finditer(r"public static (bool|float|int|string) (\w+) = ([^;]+);", cls)}
    scribed = {m.group(1): (m.group(2), val(m.group(3))) for m in re.finditer(r'Scribe_Values\.Look\(ref (\w+), "(\w+)", ([^)]+)\)', mod_cs)}
    miss = [f for f in fields if f not in scribed]
    wrong = [f"{f}: field {fields[f]} vs scribe {scribed[f][1]}" for f in fields if f in scribed and fields[f] != scribed[f][1]]
    row("settings_every_field_saved_with_its_shipped_default", ["inv_settings_gate"], "fixed", not miss and not wrong, len(fields),
        f"{len(fields)} settings; unsaved: {miss or 'none'}; default mismatches: {wrong or 'none'}")
    sliders = re.findall(r"(\w+) = (?:Mathf\.RoundToInt\()?\(?(?:int\))?list\.Slider\((\w+), ([^,]+), ([^)]+?)\)", mod_cs)
    bad = []
    for name, _, lo, hi in sliders:
        d, l, h = fields.get(name), val(lo), val(hi.rstrip(")"))
        if name == "wildPlantRegrowDaysOverride":
            continue  # its hi is a runtime constant; default 0 = off sits at lo
        if d is None or l is None or h is None or not (l <= d <= h):
            bad.append(f"{name} default {d} range [{lo}, {hi}]")
    row("settings_every_slider_holds_its_default", ["inv_settings_gate"], "sweep", not bad, len(sliders),
        f"{len(sliders)} sliders; defaults outside their range: {bad or 'none'}")
    decl = set()
    for m in re.finditer(r"\.(?:Declare|Independent)\(([^)]*)\)", mod_cs):
        decl.update(re.findall(r'"(\w+)"', m.group(1)))
    undeclared = [f for f in fields if f not in decl and f != "crossBiomeBiomeList"]
    ghosts = [d for d in decl if d not in fields]
    row("settings_every_switch_has_a_master_or_is_independent", ["inv_settings_gate"], "fixed", not undeclared and not ghosts, len(fields),
        f"undeclared settings: {undeclared or 'none'}; declared names with no field: {ghosts or 'none'}")
    masters = re.search(r'\.Declare\("pyrelandsEnabled", ([^)]*)\)', mod_cs)
    under_master = set(re.findall(r'"(\w+)"', masters.group(1))) if masters else set()
    enabled = [f for f in fields if f.endswith("Enabled") and f != "pyrelandsEnabled"]
    own = [f for f in enabled if f not in under_master]
    row("settings_mechanic_switches_outside_mod_enabled", ["inv_settings_gate"], "info", None, len(enabled),
        f"{len(enabled)} mechanic switches; not under 'Mod enabled': {own} (the code names these independent: restart-time giants/ullai, sand shovelling, the cross-biome opt-in, sub-switches under their own master)")
    gen = fields.get("biomeGenerationEnabled")
    lab = re.search(r'CheckboxLabeled\("([^"]*)", ref biomeGenerationEnabled', mod_cs)
    row("world_placement_switch_ships_off_labelled_unsupported", ["inv_settings_gate"], "fixed",
        gen is False and scribed.get("biomeGenerationEnabled", (0, None))[1] is False and bool(lab and "unsupported" in lab.group(1).lower()), 3,
        f"biomeGenerationEnabled = {gen}; saved default {scribed.get('biomeGenerationEnabled')}; label {lab.group(1) if lab else None!r}")
    reset = re.search(r"shippedDefaults", mod_cs)
    row("settings_reset_all_present", ["inv_settings_gate"], "info", None, 1, "Reset-all over shippedDefaults: " + ("present" if reset else "ABSENT"))
    md = re.search(r"public static bool MechanicsOn\(bool modMaster, bool shellPresent, bool shellOn\)\s*\{\s*return ([^;]+);", open(os.path.join(src, "Source", "Kernel", "RM_FireEcoKernel.cs")).read())
    gate_cs = open(os.path.join(src, "Source", "PyrelandsMechanicsGate.cs"), encoding="utf-8").read()
    gate_ok = "RM_FireEcoKernel.MechanicsOn(RM_PyrelandsSettings.pyrelandsEnabled, ShellPresent, ShellOn)" in gate_cs and 'RosterKey = "Pyrelands"' in gate_cs
    row("gate_wired_to_master_and_roster_toggle", ["inv_settings_gate"], "fixed", gate_ok, 1,
        "PyrelandsMechanicsGate.On = MechanicsOn(Mod enabled, shell present, shell 'Pyrelands' toggle): " + str(gate_ok))

    # ---- furnacebeast_warms (stage 6; its def half is offline)
    def race_size(name, pool):
        d = pool.get(name)
        if d is None:
            return None
        rc = d[0].find("race")
        s = rc.findtext("baseBodySize") if rc is not None else None
        return float(s) if s else None
    allthings = {}
    for p in glob.glob(os.path.join(REPO, "src", "**", "Defs", "**", "*.xml"), recursive=True):
        try:
            for d in ET.parse(p).getroot().iter("ThingDef"):
                n = d.findtext("defName")
                if n and n not in allthings:
                    allthings[n] = (d, p)
        except ET.ParseError:
            pass
    allthings.update(things)
    cast = [c.tag for c in (pyre.find("wildAnimals") if pyre is not None and pyre.find("wildAnimals") is not None else [])]
    patch = os.path.join(REPO, "src/RimUtinni/UtinniPatches/Patches/WildAnimals_Pyrelands.xml")
    patched = re.findall(r"<(RSW_\w+|RM_\w+|RUT_\w+)>[\d.]+</", open(patch).read()) if os.path.exists(patch) else []
    fb = race_size("RM_FurnaceBeast", things)
    others = {n: race_size(n, allthings) for n in cast + patched if n != "RM_FurnaceBeast"}
    known = {n: s for n, s in others.items() if s is not None}
    unknown = [n for n, s in others.items() if s is None]
    big = max(known.values()) if known else None
    row("furnace_beast_body_size_nine_twice_every_other", ["furnacebeast_warms"], "fixed", fb == 9.0 and big is not None and fb >= 2 * big, len(others) + 1,
        f"RM_FurnaceBeast baseBodySize {fb}; largest other roster kind {big} ({[n for n, s in known.items() if s == big]}); sizes not in this repo: {unknown or 'none'}")
    cls_size = re.search(r"FurnaceClassicBodySize = ([\d.]+)f", tun)
    row("furnace_classic_restore_size_3_2", ["furnacebeast_warms", "inv_settings_gate"], "fixed", bool(cls_size and float(cls_size.group(1)) == 3.2), 1,
        "PyrelandsTuning.FurnaceClassicBodySize = " + (cls_size.group(1) if cls_size else "MISSING"))
    bank = things.get("RM_FurnaceHideBank", (None, None))[0]
    comps = [li.get("Class") for li in bank.find("comps")] if bank is not None and bank.find("comps") is not None else []
    hp = bank.find("comps/li[@Class='CompProperties_HeatPusher']") if bank is not None else None
    cap = float(hp.findtext("heatPushMaxTemperature")) if hp is not None and hp.findtext("heatPushMaxTemperature") else None
    fuel = [c for c in comps if c and re.search(r"Power|Refuel|Flick", c)]
    cost = bank.findtext("costList/RM_FurnaceHide") if bank is not None else None
    leather = race_size and things.get("RM_FurnaceBeast", (None,))[0].findtext("race/leatherDef") if things.get("RM_FurnaceBeast") else None
    row("furnace_hide_bank_no_fuel_no_power_never_above_21", ["furnacebeast_warms"], "fixed",
        hp is not None and cap is not None and cap <= 21 and not fuel and cost is not None and leather == "RM_FurnaceHide", 4,
        f"heat pusher {hp is not None}, max {cap} C, fuel/power comps {fuel or 'none'}, costs {cost} RM_FurnaceHide, beast leather {leather}")

    # ---- no_ordinary_rain (stage 6; its list half is offline)
    wl = [c.tag for c in pyre.find("baseWeatherCommonalities")] if pyre is not None else []
    rain_on = [w for w in wl if w in ORDINARY_RAIN]
    rain_patch = [os.path.relpath(p, src) for p in xml_files(os.path.join(src, "Patches"))
                  if re.search(r"RM_Pyrelands", open(p).read()) and re.search(r"<(" + "|".join(ORDINARY_RAIN) + r")>", open(p).read())]
    row("biome_weather_list_has_no_ordinary_rain", ["no_ordinary_rain", "three_skies"], "fixed", not rain_on and not rain_patch and "RM_FE_BlackRain" in wl, len(wl),
        f"weathers {wl}; ordinary rain {rain_on or 'none'}; patches adding it {rain_patch or 'none'}")

    # ---- inv_firehawk_hunt_rewards def half
    hawk = things.get("RM_FireHawk", (None,))[0]
    ch = hawk.find("modExtensions/li[@Class='RimMandrake.Pyrelands.RM_ButcherTrophyExtension']") if hawk is not None else None
    feather = things.get("RM_PristineFirehawkCrestfeather", (None,))[0]
    mv = float(feather.findtext("statBases/MarketValue")) if feather is not None else None
    hmv = float(hawk.findtext("statBases/MarketValue") or 0) if hawk is not None else None
    beauty = float(feather.findtext("statBases/Beauty") or 0) if feather is not None else None
    others_trophy = [n for n, (d, p) in things.items() if n != "RM_FireHawk" and d.find("modExtensions/li[@Class='RimMandrake.Pyrelands.RM_ButcherTrophyExtension']") is not None]
    row("crestfeather_on_the_hawk_only_valuable_and_beautiful", ["inv_firehawk_hunt_rewards"], "fixed",
        ch is not None and ch.findtext("chance") == "0.35" and mv is not None and hmv is not None and mv > hmv and beauty and beauty > 0 and not others_trophy, 4,
        f"hawk trophy chance {ch.findtext('chance') if ch is not None else None}; feather value {mv} vs hawk {hmv}; beauty {beauty}; other trophy carriers {others_trophy or 'none'}")

    # ---- sand_shovel_yields_glass_sand
    sand = terrains.get("RM_FE_Ground_Sand", (None,))[0]
    ext = sand.find("modExtensions/li[@Class='RimMandrake.Pyrelands.RM_TerrainDigYieldExtension']") if sand is not None else None
    diggers = [n for n, (d, p) in terrains.items() if d.find("modExtensions/li[@Class='RimMandrake.Pyrelands.RM_TerrainDigYieldExtension']") is not None]
    row("sand_shovel_five_glass_sand_leaves_gravel_sand_only", ["sand_shovel_yields_glass_sand"], "fixed",
        ext is not None and ext.findtext("count") == "5" and ext.findtext("leaves") == "RM_FE_Ground_Gravel" and diggers == ["RM_FE_Ground_Sand"], 3,
        f"yield {ext.findtext('yield') if ext is not None else None} x{ext.findtext('count') if ext is not None else None}, leaves {ext.findtext('leaves') if ext is not None else None}; diggable terrains {diggers}")

    # ---- ullai_cross_the_map_as_vanilla_herds (tree tier offline)
    ull = things.get("RM_Ullai", (None,))[0]
    herd = ull.findtext("race/herdAnimal") if ull is not None else None
    hm = ull.findtext("race/herdMigrationAllowed") if ull is not None else None
    patch_off = [os.path.relpath(p, REPO) for p in glob.glob(os.path.join(REPO, "src", "**", "Patches", "**", "*.xml"), recursive=True)
                 if "herdMigrationAllowed" in open(p, errors="replace").read() and re.search(r"RM_Ullai|RM_Pyrelands", open(p, errors="replace").read())]
    row("ullai_is_a_vanilla_migrating_herd_animal", ["ullai_cross_the_map_as_vanilla_herds"], "fixed",
        herd == "true" and hm != "false" and not patch_off and "RM_Ullai" in cast, 4,
        f"herdAnimal {herd}, herdMigrationAllowed {hm}, patches touching it {patch_off or 'none'}, in the biome list {'RM_Ullai' in cast}; parent defs not resolved (stage 6 reads CanFireNow)")

    # ---- flamefang_bite_carries_venom: only the flamefang's tool carries the venom
    venom_users = []
    for n, (d, p) in things.items():
        for t in d.iter("capacities"):
            if any((li.text or "").strip() == "RM_FlamefangBite" for li in t):
                venom_users.append(n)
    row("venom_bite_on_the_flamefang_only", ["flamefang_bite_carries_venom"], "fixed", venom_users == ["RM_Flamefang"], 1,
        f"races whose tools use RM_FlamefangBite: {venom_users}")

    row("biome_sets_animal_density", ["populations_are_the_biomes_own"], "fixed", pyre is not None and float(pyre.findtext("animalDensity") or 0) > 0, 1,
        f"animalDensity {pyre.findtext('animalDensity') if pyre is not None else None}; cast {cast} + patch-added {patched}")

    # ---- inv_art_and_text: texture paths resolve inside this mod where their folder is ours
    tex_root = os.path.join(src, "Textures")
    unresolved, ours = [], 0
    for p in xml_files(os.path.join(src, "Defs")):
        for m in re.finditer(r"<texPath>([^<]+)</texPath>", re.sub(r"<!--.*?-->", "", open(p).read(), flags=re.S)):
            tp = m.group(1).strip()
            base = os.path.join(tex_root, tp)
            if not os.path.isdir(os.path.dirname(base)) and not os.path.isdir(base):
                continue  # a vanilla or donor slot
            ours += 1
            if not (glob.glob(base + ".png") or glob.glob(base + "_south.png") or (os.path.isdir(base) and glob.glob(os.path.join(base, "*.png")))):
                unresolved.append(tp)
    row("art_texpaths_in_our_folders_resolve", ["inv_art_and_text"], "fixed", not unresolved, ours,
        f"{ours} texPaths under this mod's Textures; unresolved: {unresolved or 'none'}")
    row("art_sheet_approval_is_a_record", ["inv_art_and_text"], "info", None, 1,
        "the approval itself (OWNER 2026-10-16) is a ledger record, not logic: its recorded check is rerun in lane 2")

    # ---- stage-6 bars whose logic is game-side: one not_kernel row each
    for bar, why in [
        ("ash_ground_and_blowing_ash", "terrain census, blowing-ash look and the light level are read on a live map"),
        ("grass_carpets_and_regreens", "cover share, regrowth days and the roof wither are plant ticks in the game"),
        ("scorchfruit_born_of_fire", "fruit rolls on a live fire tick; harvest, eating and rot are game jobs"),
        ("populations_are_the_biomes_own", "a census of a generated map; thirst and water visits are live"),
        ("ruins_stand_blackened", "ruin generation and the charred paint are map generation"),
        ("ashwallow_dives_unharmed", "the dive job, burrowed status and health are live"),
        ("three_skies", "telling three skies apart is a capture read; lightning counts are live"),
        ("firefoam_sprayer_reaches_the_fruit", "spraying and pathing through fire are live jobs"),
        ("fire_rite_hook_silent_alone", "the hook's raise and a clean log need a running burn"),
        ("walk_season_on_the_pyre", "two weeks of play on the full list"),
        ("firehawk_lights_ahead", "carry, drop and the fire at the drop cell are live jobs (the drop choice is tested above)"),
        ("furnacebeast_warms", "status, room temperature and the bed fire are live (the maths and defs are tested above)"),
    ]:
        row("not_kernel_" + bar, [bar], "not_kernel", None, 0, why + "; owed to stage 6")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--kernel", action="append", default=[])
    ap.add_argument("--src", default=MOD)
    ap.add_argument("--out", default=os.path.join(HERE, "lane1_rows.jsonl"))
    ap.add_argument("--no-csharp", action="store_true")
    a = ap.parse_args()
    if not a.no_csharp:
        run_csharp(a.kernel)
    python_rows(os.path.abspath(a.src))
    with open(a.out, "w") as f:
        for r in ROWS:
            f.write(json.dumps(r) + "\n")
    c = {}
    for r in ROWS:
        c[r["verdict"]] = c.get(r["verdict"], 0) + 1
    print("LANE1", json.dumps(c), "rows", len(ROWS), "->", a.out)
    for r in ROWS:
        if r["verdict"] == "FAIL":
            print("FAIL", r["id"], r["detail"][:400])
    sys.exit(1 if c.get("FAIL") else 0)


if __name__ == "__main__":
    main()
