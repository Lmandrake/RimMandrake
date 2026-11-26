#!/usr/bin/env python3
"""Pyrelands 0.1.0, blind cycle 3, lane 1: the file-side checks written from the bars alone (offline bars
biome_text_says_engineered, inv_firebreak_firefoam, inv_lightning_breaker, inv_settings_gate, inv_art_and_text).
    python3 blind_lane1_files.py [--mod <Pyrelands mod root>] [--src <repo src root>]
Prints one JSON row per line. Exit 0 = no FAIL row."""
import argparse, glob, json, os, re, sys
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, *[".."] * 7))
ap = argparse.ArgumentParser()
ap.add_argument("--mod", default=os.path.join(REPO, "src/RimMandrake/Pyrelands"))
ap.add_argument("--src", default=os.path.join(REPO, "src"))
a = ap.parse_args()
MOD = a.mod
fails = 0


def row(id_, bars, kind, verdict, cases, detail):
    global fails
    if verdict == "FAIL":
        fails += 1
    print(json.dumps({"id": id_, "bars": bars, "kind": kind, "verdict": verdict, "cases": cases, "detail": detail}))


def xml_files(*sub):
    out = []
    for s in sub:
        out += sorted(glob.glob(os.path.join(MOD, s, "**", "*.xml"), recursive=True))
    return out


def defs():
    for f in xml_files("Defs"):
        try:
            root = ET.parse(f).getroot()
        except ET.ParseError as e:
            yield f, None, e
            continue
        for d in root:
            yield f, d, None


# ---------------------------------------------------------------- biome_text_says_engineered
desc, n = None, 0
for f, d, err in defs():
    if d is not None and d.tag == "BiomeDef" and (d.findtext("defName") or "") == "RM_Pyrelands":
        desc, n = d.findtext("description") or "", n + 1
bad = []
if n != 1:
    bad.append("RM_Pyrelands BiomeDefs found: %d" % n)
low = (desc or "").lower()
if "genetically engineered" not in low:
    bad.append("description lacks 'genetically engineered'")
if "millennia" not in low:
    bad.append("description lacks 'millennia' (the experience: engineered AND burned for millennia)")
# a patch anywhere in the repo's mods that rewrites that description would change it "as loaded"
patchers = []
for f in glob.glob(os.path.join(a.src, "**", "*.xml"), recursive=True):
    try:
        t = open(f, encoding="utf-8", errors="replace").read()
    except OSError:
        continue
    if re.search(r'BiomeDef\[defName\s*=\s*"RM_Pyrelands"\]\s*/\s*description', t) or (
            "RM_Pyrelands.description" in t and "DefInjected" in f):
        patchers.append(os.path.relpath(f, a.src))
if patchers:
    bad.append("description patched/injected by " + ", ".join(patchers))
row("text_fixed_biome_description_engineered", ["biome_text_says_engineered"], "fixed",
    "FAIL" if bad else "PASS", 3,
    "; ".join(bad) + ("; would pass: RM_Pyrelands' own description says genetically engineered, unpatched" if bad else "")
    or "RM_Pyrelands description (the only BiomeDef of that name) says 'genetically engineered' and 'millennia'; no patch or DefInjected in src/ rewrites it: " + desc[:160])

# ---------------------------------------------------------------- inv_firebreak_firefoam / inv_lightning_breaker: absence
def absent(id_, bar, words, files_gone):
    hits = []
    for f in xml_files("Defs", "Patches", "Languages"):
        try:
            root = ET.parse(f).getroot()
        except ET.ParseError:
            continue
        for el in root.iter():
            if el.tag in ("defName", "label", "texPath") and el.text and re.search(words, el.text, re.I):
                hits.append("%s %s=%s" % (os.path.relpath(f, MOD), el.tag, el.text.strip()))
            if el.tag.lower().startswith("li") is False and re.search(words, el.tag, re.I):
                hits.append("%s key %s" % (os.path.relpath(f, MOD), el.tag))
    for f in glob.glob(os.path.join(MOD, "Source", "**", "*.cs"), recursive=True):
        if "/SelfTest/" in f:
            continue
        code = re.sub(r"//.*|/\*.*?\*/", "", open(f, encoding="utf-8", errors="replace").read(), flags=re.S)
        code = re.sub(r'"(?:[^"\\]|\\.)*"', '""', code)
        for m in re.finditer(r"\b\w*(" + words + r")\w*\b", code, re.I):
            hits.append("%s identifier %s" % (os.path.relpath(f, MOD), m.group(0)))
    for g in glob.glob(os.path.join(MOD, "Textures", "**", "*"), recursive=True):
        if re.search(words, os.path.basename(g), re.I):
            hits.append("texture " + os.path.relpath(g, MOD))
    for p in files_gone:
        if os.path.exists(os.path.join(MOD, p)):
            hits.append("file still present: " + p)
    row(id_, [bar], "fixed", "FAIL" if hits else "PASS", 1,
        ("still shipped: " + "; ".join(hits[:6]) + "; would pass: nothing of it ships") if hits else
        "nothing named /%s/ ships as a def, label, texture, keyed string or code identifier; %s absent" % (words, ", ".join(files_gone) or "-"))

absent("excised_fixed_firebreak_gone", "inv_firebreak_firefoam", r"firebreak", ["Defs/TerrainDefs/Firebreak.xml"])
absent("excised_fixed_lightning_breaker_gone", "inv_lightning_breaker", r"breaker|fulgurite", [])

# ---------------------------------------------------------------- inv_settings_gate: shipped settings, file half
src = open(os.path.join(MOD, "Source", "RM_PyrelandsMod.cs"), encoding="utf-8").read()
cls = src[src.index("class RM_PyrelandsSettings"):]
fields = {}
for m in re.finditer(r"public static (bool|float|int|string) (\w+) = ([^;]+);", cls):
    fields[m.group(2)] = (m.group(1), m.group(3).strip())
consts = dict(re.findall(r"public const float (\w+) = ([\d.]+)f;", cls))


def val(t, s):
    s = s.strip()
    if s in consts:
        s = consts[s]
    if t == "bool":
        return s == "true"
    if t == "string":
        return s.strip('"')
    return float(s.rstrip("f"))


scribe = {m.group(1): (m.group(2), m.group(3)) for m in re.finditer(r'Scribe_Values\.Look\(ref (\w+), "(\w+)", ([^)]+)\);', cls)}
bad, cases = [], 0
for name, (t, init) in fields.items():
    cases += 1
    if name not in scribe:
        bad.append(name + " is never saved (no Scribe_Values)")
        continue
    if val(t, scribe[name][1]) != val(t, init):
        bad.append("%s: initializer %s but Scribe default %s (a missing key loads a different value than shipped)" % (name, init, scribe[name][1]))
for name in scribe:
    if name not in fields:
        bad.append("Scribed but not a public static setting: " + name)
row("settings_fixed_every_setting_saved_with_its_shipped_default", ["inv_settings_gate"], "fixed",
    "FAIL" if bad else "PASS", cases,
    ("; ".join(bad[:5]) + "; would pass: each setting Scribed under its own default") if bad else
    "%d settings: each is Scribed, and its Scribe default equals its shipped initializer" % cases)

# sliders: the shipped default sits inside the slider's range (else the first touch of the slider moves it)
bad, cases = [], 0
for m in re.finditer(r"(\w+) = (?:Mathf\.RoundToInt\()?(?:\(int\))?list\.Slider\((\w+), ([^,]+), ([^)]+?)\)\)?;", cls):
    name = m.group(2)
    if name not in fields:
        continue
    cases += 1
    t, init = fields[name]

    def ev(x):
        x = x.strip()
        for k, v in consts.items():
            x = x.replace(k, v)
        x = re.sub(r"(\d)f\b", r"\1", x)
        if re.fullmatch(r"[\w.]+", x) and not re.fullmatch(r"[\d.]+", x):
            return None
        return eval(x, {"__builtins__": {}})
    lo, hi = ev(m.group(3)), ev(m.group(4))
    d = val(t, init)
    if lo is None or hi is None:
        continue
    if not (lo <= d <= hi):
        bad.append("%s default %s outside slider [%s, %s]" % (name, d, lo, hi))
row("settings_sweep_defaults_inside_slider_ranges", ["inv_settings_gate"], "sweep", "FAIL" if bad else "PASS", cases,
    ("; ".join(bad) + "; would pass: each default inside its slider") if bad else
    "%d sliders: every shipped default lies inside its slider range" % cases)

# every setting has a control on the screen, and sits in a section whose reset names it
win = cls[cls.index("public void DoWindowContents"):]
groups = re.findall(r'Group\(list, "[^"]+", [\w.]+, new\[\] \{([^}]*)\}', win)
in_group = set()
for g in groups:
    in_group |= set(re.findall(r'"(\w+)"', g))
bad, cases = [], 0
for name in fields:
    cases += 1
    uses = len(re.findall(r"\b" + name + r"\b", win))
    if uses == 0:
        bad.append(name + " has no control")
    if name not in in_group:
        bad.append(name + " in no section's reset list")
bogus = sorted(n for n in in_group if n not in fields)
if bogus:
    bad.append("section resets name unknown settings: " + ", ".join(bogus))
row("settings_fixed_every_setting_on_screen_and_in_a_section_reset", ["inv_settings_gate"], "fixed", "FAIL" if bad else "PASS", cases,
    ("; ".join(bad[:8]) + "; would pass: each setting drawn and named by its section's reset") if bad else
    "%d settings: each drawn in the window and named in its section's reset list (%d sections)" % (cases, len(groups)))

# ---------------------------------------------------------------- inv_art_and_text: art resolves, descriptions present, text true
tex_root = os.path.join(MOD, "Textures")
pngs = set(os.path.relpath(p, tex_root)[:-4].replace("\\", "/") for p in glob.glob(os.path.join(tex_root, "**", "*.png"), recursive=True))
dirs = set(os.path.relpath(p, tex_root).replace("\\", "/") for p in glob.glob(os.path.join(tex_root, "**"), recursive=True) if os.path.isdir(p))
bad, cases, notours = [], 0, 0
for f in xml_files("Defs", "Patches"):
    try:
        root = ET.parse(f).getroot()
    except ET.ParseError as e:
        bad.append("XML parse error " + os.path.relpath(f, MOD) + ": " + str(e))
        continue
    for el in root.iter():
        if el.tag in ("texPath", "flyingAnimationFramePathPrefix") and el.text:
            p = el.text.strip()
            cases += 1
            ok = p in pngs or any(p + s in pngs for s in ("_south", "_north", "_east", "_side", "_front")) or p in dirs \
                or any(x.startswith(p) for x in pngs) if el.tag == "flyingAnimationFramePathPrefix" else (
                    p in pngs or any(p + s in pngs for s in ("_south", "_north", "_east")) or p in dirs)
            if not ok:
                # a vanilla or other-mod path is not ours to resolve
                if not re.search(r"Pyrelands|RM_|/FE_|Ash|Ember|Scorch|Ullai|Furnace|Firehawk|FireHawk|Ashwallow", p):
                    notours += 1
                    continue
                bad.append("%s %s=%s resolves to no texture" % (os.path.relpath(f, MOD), el.tag, p))
row("art_fixed_every_own_texpath_resolves", ["inv_art_and_text"], "fixed", "FAIL" if bad else "PASS", cases,
    ("; ".join(bad[:6]) + "; would pass: every own texPath has its PNG") if bad else
    "%d texture paths: every one naming our art resolves to a PNG, facing set or folder under Textures (%d point at vanilla/other art)" % (cases, notours))

bad, cases = [], 0
for f, d, err in defs():
    if d is None or d.get("Abstract", "").lower() == "true":
        continue
    if d.tag in ("ThingDef", "BiomeDef", "TerrainDef", "HediffDef", "WeatherDef", "PawnKindDef"):
        cases += 1
        lab = d.findtext("label")
        dsc = d.findtext("description")
        cat = d.findtext("category") or ""
        if d.tag == "ThingDef" and cat in ("Projectile", "Mote", "Ethereal", "Filth", "Gas", "Attachment"):
            continue
        if d.tag == "PawnKindDef":
            continue
        if not lab and not d.get("ParentName"):
            bad.append("%s %s has no label" % (d.tag, d.findtext("defName")))
        if dsc is not None and not dsc.strip():
            bad.append("%s %s has an empty description" % (d.tag, d.findtext("defName")))
row("text_fixed_defs_carry_labels_and_no_empty_descriptions", ["inv_art_and_text"], "fixed", "FAIL" if bad else "PASS", cases,
    ("; ".join(bad[:6]) + "; would pass: a label and a non-empty description on each") if bad else
    "%d player-facing defs: labelled, and no description is empty" % cases)

# the shipped text must not promise what ships off: the worldgen switch ships OFF, labelled unsupported (his card 2026-11-13)
about = open(os.path.join(MOD, "About", "About.xml"), encoding="utf-8").read()
adesc = re.search(r"<description>(.*?)</description>", about, re.S).group(1)
gen_default = fields.get("biomeGenerationEnabled", ("bool", "?"))[1]
claims = [s.strip() for s in re.split(r"(?<=\.)\s+", adesc) if re.search(r"places itself on newly generated worlds|generates on new worlds|appears? on new worlds by default", s, re.I)]
if claims and gen_default == "false":
    row("text_fixed_about_does_not_promise_worldgen_that_ships_off", ["inv_art_and_text"], "fixed", "FAIL", 1,
        "About.xml says: \"%s\" but biomeGenerationEnabled ships %s (sheet floor:worldgen: 'ships off and is labelled unsupported', his card 2026-11-13); a player reading the Steam text expects the biome on a new world and gets none. Reproduce: python3 blind_lane1_files.py. Would pass: the About description says the Pyrelands is placed on the shipped world and that new-world placement is an unsupported switch, off by default"
        % (claims[0], gen_default))
else:
    row("text_fixed_about_does_not_promise_worldgen_that_ships_off", ["inv_art_and_text"], "fixed", "PASS", 1,
        "About.xml makes no new-world placement promise that the shipped default (%s) breaks" % gen_default)

sys.exit(1 if fails else 0)
