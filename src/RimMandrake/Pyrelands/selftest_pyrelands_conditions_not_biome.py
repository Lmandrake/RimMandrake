#!/usr/bin/env python3
"""T_CONDITIONS_NOT_BIOME_OFFLINE (Pyrelands 0.2.0, bar mechanics_switch_plain_no_biome).

The bar (vision.md 0.2.0): "Each mechanic works by its conditions, never by the biome (his cards of 2026-11-21). Mod Settings
holds a plain on/off for each mechanic, default on, with no biome in it."

A static read of the shipped source (C# comments are provenance and are stripped before any read):
  gates     every file of the conversion list's Pyrelands rows code 2 to code 12 (read from conversion_list.md, not typed
            here): no mechanic gate reads a biome defName list or a biome defName compare (Biome.defName == / != "...",
            Array.IndexOf over a biome-name list) or a cross-biome setting; and nowhere in Source do the biome-list symbols
            survive (MapComponent_BurnLine.IsPyrelandsMap, PyrelandsTuning.PyrelandsBiomeDefNames, FireEcologyBiomeGate,
            AppliesToBiome, any crossBiome* name), nor the shell's per-biome Enabled(key) (RM_BiomesSettings, ShellOn)
  settings  RM_PyrelandsSettings has no crossBiome field and no "Enable outside" text is in Source or Languages
  switches  each mechanic of the rows has its own switch: declared `public static bool <s> = true;`, Scribe'd with default
            true, drawn on the screen (CheckboxLabeled ... ref <s>), and read by the mechanic's own file
  data      the biome data rows read the biome's def or its extension: the no-ordinary-rain postfix, the foreign-arrival
            postfixes and the standing burn read RM_PyrelandsBiomeTraits; the patch that gives RM_Pyrelands its traits
            sets every trait true; the ash field's weather table reads the BiomeDef's own weather list
Every planted fault (in memory, on a copy of the read texts) must go red and the clean copy stay green.

Range: the static text of the shipped source only. Left out: what the game does on a live map (the live scenes own that).
Run: python3 <this file>      exit 0 = PASS, 1 = FAIL
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
SOURCE = os.path.join(HERE, "Source")
LANG = os.path.join(HERE, "Languages")
CONVERSION = os.path.join(REPO, "design", "specs", "2026-11-21-guiding-principles", "conversion_list.md")
TRAITS_PATCH = os.path.join(HERE, "Patches", "RM_Pyrelands_BiomeTraits.xml")
SETTINGS = "RM_PyrelandsMod.cs"
TRAITS = "RM_PyrelandsBiomeTraits"

# Each mechanic of rows code 2-12 -> (its file, its own switch). The switch names come from RM_PyrelandsSettings (read, not
# guessed); the three new ones are the names VERSION.json mod_settings asks for (herd thirst, the step away from fire, the
# meal before fire duty).
SWITCHES = [
    ("ashwallow dive from fire (code 2)", "RM_JobGiver_BurrowOnFire.cs", "burrowOnFireEnabled"),
    ("the burn line (code 3)", "MapComponent_BurnLine.cs", "burnLineEnabled"),
    ("wind carries fire (code 3)", "MapComponent_BurnLine.cs", "windCarriesFireEnabled"),
    ("fire ecology: ash dusting (code 4)", "FireEcologyHook.cs", "ashDustingEnabled"),
    ("fire ecology: scorch-fruit (code 4)", "FireEcologyHook.cs", "scorchFruitEnabled"),
    ("ash fall buries the ground (code 5)", "PyrelandsAshSand.cs", "ashfallAccumulationEnabled"),
    ("herd thirst (code 7)", "PyrelandsHerdThirst.cs", "herdThirstEnabled"),
    ("the step away from fire (code 8)", "PyrelandsFireSense.cs", "fireSenseEnabled"),
    ("the meal before fire duty (code 9)", "ThinkNode_ConditionalPyrelandsColonist.cs", "mealBeforeFireDutyEnabled"),
    ("the mod (code 10)", "PyrelandsMechanicsGate.cs", "pyrelandsEnabled"),
]
# Biome data rows: the file and the trait it must read off RM_PyrelandsBiomeTraits.
DATA = [
    ("ordinary rain falls black (code 6, weather data)", "PyrelandsNoOrdinaryRain.cs", "ordinaryRainFallsBlack"),
    ("no foreign arrivals (code 13, roster data)", "PyrelandsForeignArrivals.cs", "onlyOwnAnimalsArrive"),
    ("the standing burn (code 3, standing burn odds)", "MapComponent_BurnLine.cs", "standingBurn"),
]
SYMBOLS = re.compile(r"\b(IsPyrelandsMap|PyrelandsBiomeDefNames|FireEcologyBiomeGate|AppliesToBiome|RM_BiomesSettings|ShellOn)\b"
                     r"|crossBiome", re.I)
COMPARES = [
    re.compile(r"Biome\??\.defName\s*[!=]="),
    re.compile(r"[!=]=\s*[\w.?]*Biome\??\.defName"),
    re.compile(r"\.defName\s*[!=]=\s*\"RM_Pyrelands\""),
    re.compile(r"\"RM_Pyrelands\"\s*[!=]="),
    re.compile(r"Array\.IndexOf\([^;]*BiomeDefNames"),
    re.compile(r"NativeBiomeDefName\s*[!=]=|[!=]=\s*NativeBiomeDefName"),
]


def strip_comments(cs):
    cs = re.sub(r"/\*.*?\*/", "", cs, flags=re.S)
    return re.sub(r"//[^\n]*", "", cs)


def row_files(conv_text):
    """The Source files of the Pyrelands section's rows code 2 to code 12."""
    sec = conv_text.split("## Pyrelands\n", 1)[1].split("\n## ", 1)[0]
    files = []
    for line in sec.splitlines():
        m = re.match(r"\|\s*code (\d+)\s*\|(.*?)\|", line)
        if m and 2 <= int(m.group(1)) <= 12:
            for f in re.findall(r"Pyrelands/Source/([\w/]+\.cs)", m.group(2)):
                if f not in files:
                    files.append(f)
    return files


def read_all():
    texts = {}
    for root, _, names in os.walk(SOURCE):
        if os.sep + "obj" in root or os.sep + "bin" in root:
            continue
        for n in names:
            if n.endswith(".cs"):
                p = os.path.join(root, n)
                with open(p, encoding="utf-8-sig") as f:
                    texts[os.path.relpath(p, SOURCE).replace(os.sep, "/")] = f.read()
    lang = {}
    for root, _, names in os.walk(LANG):
        for n in names:
            if n.endswith(".xml"):
                p = os.path.join(root, n)
                with open(p, encoding="utf-8-sig") as f:
                    lang[os.path.relpath(p, LANG)] = f.read()
    patch = open(TRAITS_PATCH, encoding="utf-8-sig").read() if os.path.exists(TRAITS_PATCH) else None
    with open(CONVERSION, encoding="utf-8") as f:
        conv = f.read()
    return {"cs": texts, "lang": lang, "patch": patch, "conv": conv}


def check(d):
    """-> (errors, cases read)."""
    errs, cases = [], 0
    cs = {k: strip_comments(v) for k, v in d["cs"].items()}
    rows = row_files(d["conv"])
    if len(rows) < 9:
        errs.append("conversion list rows code 2-12 name %d Source files, expected the 11 of 2026-11-21" % len(rows))
    for f in rows:
        cases += 1
        if f not in cs:
            errs.append("gates: row file %s is not in Source" % f)
            continue
        for rx in COMPARES:
            m = rx.search(cs[f])
            if m:
                errs.append("gates: %s compares a biome defName: %r" % (f, m.group(0)))
    for f, text in sorted(cs.items()):
        if f.startswith("SelfTest/"):
            continue
        cases += 1
        m = SYMBOLS.search(text)
        if m:
            errs.append("gates: %s still reads the biome-list / cross-biome / shell symbol %r" % (f, m.group(0)))
    settings = cs.get(SETTINGS, "")
    raw_settings = d["cs"].get(SETTINGS, "")
    cases += 1
    if re.search(r"crossBiome", raw_settings, re.I):
        errs.append("settings: RM_PyrelandsSettings still names a crossBiome field")
    for f, text in list(d["cs"].items()) + list(d["lang"].items()):
        if "Enable outside" in text:
            errs.append("settings: %s carries 'Enable outside' text" % f)
    for what, f, s in SWITCHES:
        cases += 1
        if not re.search(r"public\s+static\s+bool\s+%s\s*=\s*true\s*;" % s, settings):
            errs.append("switches: %s: %s is not declared default true" % (what, s))
        if not re.search(r"Scribe_Values\.Look\(\s*ref\s+%s\s*,\s*\"%s\"\s*,\s*true\s*\)" % (s, s), settings):
            errs.append("switches: %s: %s is not Scribe'd with default true" % (what, s))
        if not re.search(r"CheckboxLabeled\([^;]*ref\s+%s\b" % s, settings):
            errs.append("switches: %s: %s is not drawn on the settings screen" % (what, s))
        if not re.search(r"RM_PyrelandsSettings\.%s\b" % s, cs.get(f, "")):
            errs.append("switches: %s: %s never reads RM_PyrelandsSettings.%s" % (what, f, s))
    for what, f, trait in DATA:
        cases += 1
        # The trait read off the biome: RM_PyrelandsBiomeTraits.StandingBurn(...) (the accessor is the trait's PascalCase name)
        # or RM_PyrelandsBiomeTraits.Of(...).standingBurn.
        if TRAITS not in cs.get(f, ""):
            errs.append("data: %s: %s does not read %s" % (what, f, TRAITS))
        elif not re.search(r"%s\.(?:Of\([^;]*?\)\??\.)?%s\b" % (TRAITS, trait), cs.get(f, ""), re.I):
            errs.append("data: %s: %s does not read trait %s" % (what, f, trait))
    cases += 1
    tdef = next((v for k, v in cs.items() if re.search(r"class\s+%s\s*:\s*DefModExtension" % TRAITS, v)), None)
    if tdef is None:
        errs.append("data: no %s : DefModExtension in Source" % TRAITS)
    if d["patch"] is None:
        errs.append("data: %s is missing" % os.path.relpath(TRAITS_PATCH, REPO))
    else:
        p = re.sub(r"<!--.*?-->", "", d["patch"], flags=re.S)
        if 'defName="RM_Pyrelands"' not in p or TRAITS not in p:
            errs.append("data: the traits patch does not give BiomeDef RM_Pyrelands its %s" % TRAITS)
        for _, _, trait in DATA:
            if not re.search(r"<%s>\s*true\s*</%s>" % (trait, trait), p):
                errs.append("data: the traits patch does not set %s true on RM_Pyrelands" % trait)
    cases += 1
    if not re.search(r"\.weatherCommonalities|baseWeatherCommonalities", cs.get("PyrelandsAshField.cs", "")):
        errs.append("data: PyrelandsAshField.cs no longer reads the BiomeDef's own weather table")
    return errs, cases


def mutate(d, f, old, new, kind="cs"):
    m = {"cs": dict(d["cs"]), "lang": dict(d["lang"]), "patch": d["patch"], "conv": d["conv"]}
    if kind == "patch":
        if m["patch"] is None or old not in m["patch"]:
            return None
        m["patch"] = m["patch"].replace(old, new, 1)
        return m
    src = m[kind].get(f)
    if src is None or old not in src:
        return None
    m[kind][f] = src.replace(old, new, 1)
    return m


MUTANTS = [
    ("an IsPyrelandsMap gate put back in RM_JobGiver_BurrowOnFire", "RM_JobGiver_BurrowOnFire.cs",
     "return FireIsNear(pawn, map, ext.detectionRadius);",
     "if (!burnLine.IsPyrelandsMap) return false;\n            return FireIsNear(pawn, map, ext.detectionRadius);", "cs"),
    ("a biome defName compare in the fire sense", "PyrelandsFireSense.cs", "RM_PyrelandsSettings.fireSenseEnabled",
     "RM_PyrelandsSettings.fireSenseEnabled && map.Biome.defName == \"RM_Pyrelands\"", "cs"),
    ("a mechanic switch defaulting false (herd thirst)", SETTINGS, "public static bool herdThirstEnabled = true;",
     "public static bool herdThirstEnabled = false;", "cs"),
    ("a mechanic switch Scribe'd default false (meal before fire duty)", SETTINGS,
     "Scribe_Values.Look(ref mealBeforeFireDutyEnabled, \"mealBeforeFireDutyEnabled\", true)",
     "Scribe_Values.Look(ref mealBeforeFireDutyEnabled, \"mealBeforeFireDutyEnabled\", false)", "cs"),
    ("the step-away switch never read", "PyrelandsFireSense.cs", "RM_PyrelandsSettings.fireSenseEnabled", "true", "cs"),
    ("a crossBiome field put back", SETTINGS, "public static bool herdThirstEnabled = true;",
     "public static bool herdThirstEnabled = true;\n        public static bool crossBiomeEnabled = false;", "cs"),
    ("the shell's per-biome Enabled(key) put back", "PyrelandsMechanicsGate.cs", "On => RM_PyrelandsSettings.pyrelandsEnabled;",
     "On => RM_PyrelandsSettings.pyrelandsEnabled && ShellOn();", "cs"),
    ("the no-ordinary-rain postfix back on a biome-name list", "PyrelandsNoOrdinaryRain.cs",
     "RM_PyrelandsBiomeTraits.OrdinaryRainFallsBlack(___map.Biome)",
     "Array.IndexOf(PyrelandsTuning.PyrelandsBiomeDefNames, ___map.Biome.defName) >= 0", "cs"),
    ("the traits patch drops the standing burn", None, "<standingBurn>true</standingBurn>",
     "<standingBurn>false</standingBurn>", "patch"),
]


def main():
    d = read_all()
    errs, cases = check(d)
    for e in errs:
        print("FAIL " + e)
    red = 0
    for what, f, old, new, kind in MUTANTS:
        m = mutate(d, f, old, new, kind)
        if m is None:
            print("FAIL mutant %r: its anchor %r is not in %s (the mutant cannot be planted)" % (what, old[:60], f or kind))
            errs.append("mutant not planted")
            continue
        merrs, _ = check(m)
        if merrs:
            red += 1
        else:
            print("FAIL mutant %r stayed green" % what)
            errs.append("mutant green")
    worst = len(errs)
    print("T_CONDITIONS_NOT_BIOME_OFFLINE: worst %d failure(s), limit 0; %d cases read; %d of %d mutants red"
          % (worst, cases, red, len(MUTANTS)))
    if errs:
        print("FAIL")
        return 1
    print("PASS: every mechanic gate reads its conditions, not the biome; each has its own default-on switch; "
          "biome data reads the biome's traits; %d of %d mutants red, the clean copy green" % (red, len(MUTANTS)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
