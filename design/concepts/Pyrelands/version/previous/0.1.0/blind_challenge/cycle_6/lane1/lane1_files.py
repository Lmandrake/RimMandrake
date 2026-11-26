"""Lane 1, the file half: settings, text, absence, art files, the venom course. Written from the bars; reads shipped defs and settings only."""
import glob, os, re, sys
import xml.etree.ElementTree as ET
from PIL import Image

def rows(repo):
    out = []
    def row(i, bars, kind, bad, cases, info=""):
        out.append(dict(id=i, bars=bars, kind=kind, verdict="FAIL" if bad else "PASS", cases=cases, detail=("; ".join(bad)[:900] if bad else info)))
    mod = os.path.join(repo, "src/RimMandrake/Pyrelands")
    s = open(os.path.join(mod, "Source/RM_PyrelandsMod.cs"), encoding="utf-8-sig").read()
    cls = s[s.index("class RM_PyrelandsSettings"):s.index("public override void ExposeData")]
    consts = dict(re.findall(r"public const float (\w+) = ([\d.]+)f", cls))
    fields = {n: v.strip() for _, n, v in re.findall(r"public static (bool|float|int|string) (\w+) = ([^;]+);", cls)}
    def norm(v):
        v = v.strip(); v = consts.get(v, v)
        try: return float(v.rstrip("f"))
        except ValueError: return v
    sc = {a: (k, d) for a, k, d in re.findall(r'Scribe_Values\.Look\(ref (\w+), "(\w+)", ([^)]+)\)', s)}
    bad = ["%s never saved" % f for f in fields if f not in sc] + ["%s saved default %s, shipped %s" % (f, sc[f][1], fields[f]) for f in fields if f in sc and norm(sc[f][1]) != norm(fields[f])]
    if len({k for k, _ in sc.values()}) != len(sc): bad.append("two settings share one save key")
    row("settings_saved_at_shipped_defaults", ["inv_settings_gate"], "sweep", bad, len(fields), "%d settings" % len(fields))
    decl = s[s.index("SettingDependencies Masters"):s.index("private static object GetField")]
    known = set(re.findall(r'"(\w+)"', "".join(re.findall(r"\.(?:Declare|Independent)\(([^)]*)\)", decl))))
    bad = ["%s in no master and not independent" % f for f in fields if f not in known] + ["%s declared, no such setting" % k for k in known if k not in fields]
    row("settings_every_one_declared", ["inv_settings_gate"], "sweep", bad, len(fields))
    ui = s[s.index("void DoWindowContents"):]
    drawn = set(re.findall(r"ref (\w+)", ui)) | set(re.findall(r"(\w+) = \(?(?:int\))?(?:Mathf\.RoundToInt\()?\(?list\.(?:Slider|TextEntry)", ui)) | {"crossBiomeBiomeList"}
    drawn |= set(re.findall(r"(\w+) = (?:\(int\)|Mathf\.RoundToInt\()list\.Slider", ui))
    bad = ["%s has no control" % f for f in fields if f not in drawn]
    grp = set(re.findall(r'"(\w+)"', "".join(re.findall(r"Group\(list, [^;{]*?new\[\] \{([^}]*)\}", ui))))
    bad += ["%s resets with no group" % f for f in fields if f not in grp]
    row("settings_every_one_drawn_and_reset", ["inv_settings_gate"], "sweep", bad, len(fields))
    bad = []
    for f, lo, hi in re.findall(r"(\w+) = [^;]*?list\.Slider\(\w+, ([\w.* ]+?), ([\w.* ]+?)\)", ui):
        try: lo_, hi_ = (eval(re.sub(r"([\d.]+)f", r"\1", x).replace("AshDustingDefault", consts["AshDustingDefault"])) for x in (lo, hi))
        except Exception: continue
        v = float(norm(fields[f]))
        if not lo_ <= v <= hi_: bad.append("%s default %s outside slider %s..%s" % (f, v, lo_, hi_))
    row("settings_defaults_inside_sliders", ["inv_settings_gate"], "sweep", bad, 18)
    row("settings_worldgen_off_and_labelled", ["inv_settings_gate"], "fixed", [] if fields["biomeGenerationEnabled"] == "false" and "(unsupported)" in ui else ["worldgen switch not off/labelled"], 1)
    # the "Mod enabled" tooltip names what it does not gate: every switch it does not gate must be named there or be false
    tip = re.search(r'CheckboxLabeled\("Mod enabled".*?\);', ui, re.S).group(0).lower()
    top = re.search(r'\.Declare\("pyrelandsEnabled",(.*?)\)', decl, re.S).group(1)
    gated = set(re.findall(r'"(\w+)"', top)); ch = True
    while ch:
        ch = False
        for a, rest in re.findall(r'\.Declare\("(\w+)",?([^)]*)\)', decl):
            if a in gated:
                new = set(re.findall(r'"(\w+)"', rest)) - gated
                if new: gated |= new; ch = True
    words = dict(sandShovelEnabled="sand shovel", furnaceBeastGiant="giant furnace-beast", ullaiEnabled="ullai", sprayerFoamsPathEnabled="spray", biomeGenerationEnabled="tile placement", ashDryFertility="dry", wildPlantRegrowDaysOverride="regrow", crossBiomeEnabled="outside")
    bad = ["'Mod enabled' says every mechanic below stops, but does not gate %s and its tooltip does not name it" % f for f in fields if fields[f] in ("true",) and f not in gated and f not in ("pyrelandsEnabled",) and words.get(f, f) not in tip]
    row("settings_master_tooltip_names_what_it_leaves_on", ["inv_settings_gate"], "fixed", bad, len(fields) - len(gated))
    # the wind switch's tooltip against the kernel it switches
    wt = re.search(r'CheckboxLabeled\("The wind carries the fire".*?\);', ui, re.S).group(0)
    wt = " ".join(re.findall(r'"([^"]*)"', wt))
    k = open(os.path.join(mod, "Source/Kernel/RM_BurnKernel.cs"), encoding="utf-8-sig").read()
    bad = []
    if "FlankPlan(" in k and re.search(r"never spreads back or sideways|as wide as what was lit|lights one cell", wt):
        bad.append("tooltip says each fire lights one cell, never sideways, a line as wide as what was lit; CarryPlan heals a cell aside and FlankPlan opens and closes the flanks (a lone fire fans out)")
    row("settings_wind_tooltip_matches_kernel", ["inv_settings_gate"], "fixed", bad, 1)
    # text
    bio = ET.parse(os.path.join(mod, "Defs/BiomeDefs/Pyrelands.xml")).getroot()
    d = [b.findtext("description") or "" for b in bio.iter("BiomeDef") if b.findtext("defName") == "RM_Pyrelands"]
    bad = [] if len(d) == 1 and "engineered" in d[0].lower() and "millenni" in d[0].lower() else ["description: %s" % d]
    row("text_biome_engineered_millennia", ["biome_text_says_engineered"], "fixed", bad, 1, d[0][:200] if d else "")
    alltext = {}
    for p in glob.glob(mod + "/Defs/**/*.xml", recursive=True) + glob.glob(mod + "/Patches/**/*.xml", recursive=True) + glob.glob(mod + "/Languages/**/*.xml", recursive=True) + [mod + "/About/About.xml"]:
        alltext[p] = ET.tostring(ET.parse(p).getroot(), encoding="unicode")
    for i, bar, pat in (("text_absent_breaker", "inv_lightning_breaker", r"breaker|fulgurite"), ("text_absent_firebreak", "inv_firebreak_firefoam", r"fire\s?-?break|FirebreakLine")):
        bad = ["%s: %s" % (os.path.basename(p), m.group(0)) for p, t in alltext.items() for m in re.finditer(pat, t, re.I)]
        bad += ["settings: " + m for m in re.findall(pat, "\n".join(re.findall(r'"([^"]*)"', s)), re.I)]
        bad += [os.path.basename(p) for p in glob.glob(mod + "/**/*", recursive=True) if re.search(pat, os.path.basename(p), re.I) and "selftest" not in p and "/Source/SelfTest" not in p]
        row(i, [bar], "fixed", bad, len(alltext))
    bad = []
    n = 0
    for p, t in alltext.items():
        if "/Defs/" not in p: continue
        for e in ET.fromstring(t):
            if e.get("Abstract") == "True": continue
            if e.tag in ("ThingDef", "BiomeDef", "HediffDef", "WeatherDef", "DesignationDef", "JobDef", "TerrainDef") and e.findtext("defName"):
                n += 1
                if e.tag in ("BiomeDef", "WeatherDef", "HediffDef") and not (e.findtext("description") or "").strip() : bad.append(e.findtext("defName") + " no description")
                if e.tag == "ThingDef" and e.find("race") is not None and not (e.findtext("description") or "").strip(): bad.append(e.findtext("defName") + " no description")
                for tag in ("label", "description"):
                    v = e.findtext(tag) or ""
                    if re.search(r"\b(TODO|TBD|placeholder|lorem|jawa)\b", v, re.I): bad.append(e.findtext("defName") + " " + tag + ": " + v[:60])
    row("text_defs_described", ["inv_art_and_text"], "sweep", bad, n)
    # art: each graphic's files exist, are RGBA with a transparent corner, and all facings of one animal share a size
    bad, n = [], 0
    tex = os.path.join(mod, "Textures")
    for p, t in alltext.items():
        if "/Defs/" not in p: continue
        for e in ET.fromstring(t).iter():
            tp = e.findtext("texPath")
            if not tp: continue
            base = os.path.join(tex, tp)
            multi = (e.findtext("graphicClass") or "") == "Graphic_Multi"
            have = glob.glob(base + "*.png") or (glob.glob(base + "/*.png") if os.path.isdir(base) else [])
            if not have:
                if tp.split("/")[-1].startswith(("RM_", "Ullai", "FireHawk")) or "Pyrelands" in tp: bad.append("missing " + tp)
                continue
            n += 1
            if os.path.isdir(os.path.dirname(base)):
                f = [base + x + ".png" for x in ("_north", "_east", "_south")]
                if any(os.path.exists(x) for x in f):
                    if not all(os.path.exists(x) for x in f): bad.append(tp + " lacks a facing")
                    sz = {Image.open(x).size for x in f if os.path.exists(x)}
                    if len(sz) > 1: bad.append("%s facings differ in size %s" % (tp, sz))
    for x in glob.glob(tex + "/Things/Pawn/**/*.png", recursive=True):
        im = Image.open(x)
        if im.mode != "RGBA": bad.append(os.path.relpath(x, tex) + " mode " + im.mode); continue
        a = im.getchannel("A"); w, h = im.size
        if a.getbbox() is None: bad.append(os.path.relpath(x, tex) + " empty")
        if any(a.getpixel(c) > 8 for c in ((0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1))): bad.append(os.path.relpath(x, tex) + " opaque corner")
    row("art_files_whole", ["inv_art_and_text"], "sweep", bad, n)
    # venom: one bite of a healthy colonist, worst rolls, power after our own patch
    hd = ET.parse(os.path.join(mod, "Defs/HediffDefs/RM_FlamefangVenom.xml")).getroot()
    c = [x for x in hd.iter("li") if x.get("Class") == "HediffCompProperties_Immunizable"][0]
    g = lambda k: float(c.findtext(k))
    dose = float(ET.parse(os.path.join(mod, "Defs/DamageDefs/RM_FlamefangVenomBite.xml")).getroot().find(".//severityPerDamageDealt").text)
    bad, seen = [], []
    for power in (10, 22.5):
        for roll in (.8, 1, 1.2):
            for imm in (.8, 1, 1.2):
                sev, im, t, peak = dose * power * roll, 0.0, 0.0, 0
                s0 = sev
                while sev > 0 and t < 20:
                    sev += (g("severityPerDayImmune") if im >= 1 else g("severityPerDayNotImmune")) * .01
                    im += g("immunityPerDaySick") * imm * .01 if im < 1 else 0
                    peak = max(peak, sev); t += .01
                seen.append(peak)
                if peak >= 1: bad.append("power %s roll %s imm %s dies (%.2f)" % (power, roll, imm, peak))
                if t >= 20: bad.append("never thrown off")
                if peak <= s0: bad.append("never worsens")
    row("venom_one_bite_course", ["flamefang_bite_carries_venom"], "sweep", bad, 18, "peaks %.2f..%.2f" % (min(seen), max(seen)))
    for bar, why in (("inv_lightning_breaker", None),):
        pass
    return out
