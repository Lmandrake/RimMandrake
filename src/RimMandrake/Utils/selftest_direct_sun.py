#!/usr/bin/env python3
"""Direct Sun is a pure function of geometry, never of the biome (offline, seconds).

Items: DIRECT_SUN_UNIFY_GEOMETRY_ALONE_DECIDES, DIRECT_SUN_SELFTEST_BUILD_EVERY_BIOME_EQUAL,
DIRECT_SUN_SETTINGS_WIRE_FEWER_KNOBS. Design: design/RimMandrake/unified_direct_sun_heat_2026-10-19.md §3-6. Owner card
2026-10-19: "a pure function of geometry, NOT biome ... no biome-specific heat, no biome-specific sun".

The math (55 x sin E, shadow length h / tan E, covered cells at every E, equality of the shipped functions at every E)
is the C# half: src/RimMandrake/Utils/selftest_sun_heat.py. This file is the half that reads defs and source:

  every_biome   every BiomeDef under src/ carries no field that Direct Sun reads (XML parsed as elements), so the C#
                model, which takes no biome input, gives every biome the same offset and shade at the same E. A BiomeDef
                of a mod the owner holds (mod_owner_hold.json) may still name them only if the load-time strip patch
                (CreatureBehaviors/Patches/RM_DirectSun_LegacyFields.xml) removes each one: such rows print HELD.
  code          no C# under src/ names a heat kind (RM_HeatKind, KindFromElevation, GearKindFactor, ...).
  extension     RM_SunHeatExtension declares no field that decides Direct Sun (only the two documented legacy
                substellar fields, kept for Stillsand's compiled DLL while Stillsand is held).
  strip         every removed field that some def under src/ still names has its PatchOperationRemove in the strip patch.
  gear          RM_SunShield is not shade gear; no shade-gear comp outside a held mod carries a per-kind factor.
  air_heat      the four hot-air biomes (the Forge, the Scald, the Fever Wood, the Greentide) carry RM_AirHeatExtension
                naming a GameConditionDef of class GameCondition_TemperatureOffset with a non-zero temperatureOffset, in
                their own mod, and carry no Direct Sun number. A held mod prints HELD.
  weather       the vanilla overcast weathers get a sun factor below 1 (DS6).
  settings      Creature Behaviors' settings: no kindFromElevationEnabled, a zenith setting defaulting to 55 and a
                weather switch defaulting on, each saved with the same default; the master reads "Direct Sun". Each
                air-heat biome mod (not held) has an on/off and a degrees slider that write its condition's offset.

Then each check is shown to fire on a planted fault in a temp copy (--no-mutate skips that).

    python3 src/RimMandrake/Utils/selftest_direct_sun.py [--only every_biome,code,...] [--no-mutate]
Exit 0: all chosen checks pass. 1: a check failed (named). 2: could not look (a file it needs is missing).
"""
import argparse
import glob
import json
import os
import re
import shutil
import sys
import tempfile
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", "..", ".."))

# Every field the one geometry model removed from RM_SunHeatExtension (design §4): none may decide Direct Sun.
REMOVED_EXT = ["heatKind", "heatOffsetC", "maxHeatOffsetC", "heatScalesWithElevation", "minScaledHeatOffsetC",
               "overheadAboveElevationDegrees", "minElevationDegrees", "maxElevationDegrees", "bodySizeExponent",
               "minBodySizeFactor", "maxBodySizeFactor", "sunPathCostPerCell", "sandGlareExposureFloor"]
# Kept on the class only for Stillsand's compiled DLL (RM_PreciousCaves reads them); Direct Sun never does.
LEGACY_EXT = ["substellarLatitude", "substellarLongitude"]
REMOVED_GEAR = ["overheadFactor", "lowSunFactor"]
KIND_TOKENS = ["RM_HeatKind", "KindFromElevation", "GearKindFactor", "EffectiveHeatKind", "GearKind",
               "kindFromElevationEnabled", "overheadAboveElevationDegrees", "heatScalesWithElevation",
               "minScaledHeatOffsetC", "ElevationHeatOffset"]
AIR = {  # biome defName -> (mod folder, condition defName)
    "RM_TheForge": ("TheForge", "RM_ForgeAirHeat"),
    "RM_TheScald": ("TerminalBiomes", "RM_ScaldAirHeat"),
    "RM_FeverWood": ("FeverWood", "RM_FeverWoodAirHeat"),
    "RM_Greentide": ("Greentide", "RM_GreentideAirHeat"),
}
OVERCAST = ["Overcast", "Rain", "Fog", "FoggyRain", "RainyThunderstorm", "SnowHard", "Blizzard"]
EXT_CLASS = "RM_SunHeatExtension"
GEAR_CLASS = "RM_CompProperties_ShadeGear"


class CouldNotLook(Exception):
    pass


def _p(root, *a):
    return os.path.join(root, *a)


def held_mods(root):
    p = _p(root, "src", "RimMandrake", "rimflow", "mod_owner_hold.json")
    try:
        with open(p, encoding="utf-8") as f:
            return {h["mod"] for h in json.load(f).get("holds", [])}
    except (OSError, ValueError, KeyError) as e:
        raise CouldNotLook("the hold list %s cannot be read: %s" % (p, e))


def mod_of(root, path):
    rel = os.path.relpath(path, _p(root, "src")).split(os.sep)
    return rel[1] if len(rel) > 2 else rel[0]


def xml_files(root):
    out = sorted(glob.glob(_p(root, "src", "**", "*.xml"), recursive=True))
    if not out:
        raise CouldNotLook("no XML under %s" % _p(root, "src"))
    return out


def parse(path):
    try:
        return ET.parse(path).getroot()
    except ET.ParseError:
        return None  # not a def file we can read; a broken def file is the XML validators' finding, not this one's


def cls_is(el, name):
    c = el.get("Class") or ""
    return c == name or c.endswith("." + name)


def strip_ops(root):
    """-> {field} stripped by the load-time patch, per target ('ext' / 'gear')."""
    p = _p(root, "src", "RimMandrake", "CreatureBehaviors", "Patches", "RM_DirectSun_LegacyFields.xml")
    got = {"ext": set(), "gear": set()}
    r = parse(p) if os.path.isfile(p) else None
    if r is None:
        return got
    for op in r.iter("Operation"):
        if op.get("Class") != "PatchOperationRemove" or (op.findtext("success") or "").strip() != "Always":
            continue
        xp = (op.findtext("xpath") or "").strip()
        m = re.match(r"^Defs/(BiomeDef|ThingDef)/(modExtensions|comps)/li\[@Class='RimMandrake\.CreatureBehaviors\."
                     r"(\w+)'\]/(\w+)$", xp)
        if not m:
            continue
        if m.group(1) == "BiomeDef" and m.group(3) == EXT_CLASS:
            got["ext"].add(m.group(4))
        if m.group(1) == "ThingDef" and m.group(3) == GEAR_CLASS:
            got["gear"].add(m.group(4))
    return got


def biome_defs(root):
    """-> [(path, BiomeDef element or patch li, defName)] for every BiomeDef and every patch value li of our extension."""
    out = []
    for f in xml_files(root):
        r = parse(f)
        if r is None:
            continue
        for b in r.iter("BiomeDef"):
            out.append((f, b, b.findtext("defName") or "?"))
        if r.tag == "Patch":
            for li in r.iter("li"):
                if cls_is(li, EXT_CLASS):
                    out.append((f, li, "(patch)"))
    return out


def check_every_biome(root, rows, fails):
    held = held_mods(root)
    stripped = strip_ops(root)["ext"]
    found = biome_defs(root)
    nb = sum(1 for _, _, d in found if d != "(patch)")
    if nb == 0:
        raise CouldNotLook("no BiomeDef found under src/: the instrument is blind")
    bad, heldrows = [], []
    for f, el, name in found:
        lis = [el] if el.tag == "li" else [li for li in el.iter("li") if cls_is(li, EXT_CLASS)]
        for li in lis:
            named = [c.tag for c in li if c.tag in REMOVED_EXT or c.tag in LEGACY_EXT]
            if not named:
                continue
            mod = mod_of(root, f)
            if mod in held and all(n in stripped for n in named):
                heldrows.append("%s (%s): %s" % (name, mod, ",".join(named)))
            else:
                bad.append("%s %s: %s" % (os.path.relpath(f, root), name, ",".join(named)))
    for h in heldrows:
        rows.append("HELD every_biome: %s, stripped at load until the mod's own next build" % h)
    if bad:
        fails.append("every_biome: %d def(s) carry a Direct Sun field: %s" % (len(bad), "; ".join(bad[:8])))
    else:
        rows.append("PASS every_biome: %d BiomeDefs read, none carries a field Direct Sun reads (%d held, stripped)"
                    % (nb, len(heldrows)))


def check_code(root, rows, fails):
    files = glob.glob(_p(root, "src", "**", "*.cs"), recursive=True)
    if not files:
        raise CouldNotLook("no C# under src/")
    pat = re.compile(r"\b(%s)\b" % "|".join(KIND_TOKENS))
    hits = []
    for f in files:
        with open(f, encoding="utf-8", errors="replace") as h:
            for i, line in enumerate(h, 1):
                code = line.split("//", 1)[0]
                m = pat.search(code)
                if m:
                    hits.append("%s:%d %s" % (os.path.relpath(f, root), i, m.group(1)))
    if hits:
        fails.append("code: %d line(s) name a heat kind: %s" % (len(hits), "; ".join(hits[:8])))
    else:
        rows.append("PASS code: %d C# files, none names a heat kind" % len(files))


def _class_fields(src, cls):
    m = re.search(r"\bclass\s+%s\b[^{]*\{" % cls, src)
    if not m:
        return None
    depth, i = 1, m.end()
    while i < len(src) and depth:
        depth += {"{": 1, "}": -1}.get(src[i], 0)
        i += 1
    body = src[m.end():i]
    return re.findall(r"^\s*public\s+(?!static|const|override|class)[\w<>\[\],\s]+?\s+(\w+)\s*(?:=|;)", body, re.M)


def check_extension(root, rows, fails):
    p = _p(root, "src", "RimMandrake", "CreatureBehaviors", "Source", "RM_SunHeatExtension.cs")
    if not os.path.isfile(p):
        raise CouldNotLook("%s is missing" % p)
    with open(p, encoding="utf-8") as h:
        fields = _class_fields(h.read(), EXT_CLASS)
    if not fields:
        raise CouldNotLook("no public field found in %s: the parser is blind" % EXT_CLASS)
    deciding = [f for f in fields if f in REMOVED_EXT]
    if deciding:
        fails.append("extension: RM_SunHeatExtension still declares %s" % ",".join(deciding))
    else:
        rows.append("PASS extension: RM_SunHeatExtension declares none of the %d removed fields (%d fields read)"
                    % (len(REMOVED_EXT), len(fields)))


def named_fields(root):
    """-> ({removed extension fields some BiomeDef or patch names}, {removed gear fields some ThingDef names})."""
    ext, gear = set(), set()
    for f, el, _ in biome_defs(root):
        for li in ([el] if el.tag == "li" else [li for li in el.iter("li") if cls_is(li, EXT_CLASS)]):
            ext.update(c.tag for c in li if c.tag in REMOVED_EXT)
    for f in xml_files(root):
        r = parse(f)
        if r is None:
            continue
        for li in r.iter("li"):
            if cls_is(li, GEAR_CLASS):
                gear.update(c.tag for c in li if c.tag in REMOVED_GEAR)
    return ext, gear


def check_strip(root, rows, fails):
    got = strip_ops(root)
    ext, gear = named_fields(root)
    miss = sorted(ext - got["ext"]) + sorted(gear - got["gear"])
    if miss:
        fails.append("strip: a def still names %s, and no load-time PatchOperationRemove (success Always) strips it"
                     % ",".join(miss))
    else:
        rows.append("PASS strip: the %d removed fields some def still names are stripped at load" % (len(ext) + len(gear)))


def check_gear(root, rows, fails):
    held = held_mods(root)
    stripped = strip_ops(root)["gear"]
    shield, factors = [], []
    for f in xml_files(root):
        r = parse(f)
        if r is None:
            continue
        for td in r.iter("ThingDef"):
            for li in td.iter("li"):
                if not cls_is(li, GEAR_CLASS):
                    continue
                if (td.findtext("defName") or "") == "RM_SunShield":
                    shield.append(os.path.relpath(f, root))
                named = [c.tag for c in li if c.tag in REMOVED_GEAR]
                if named and not (mod_of(root, f) in held and all(n in stripped for n in named)):
                    factors.append("%s %s: %s" % (os.path.relpath(f, root), td.findtext("defName"), ",".join(named)))
    if shield:
        fails.append("gear: RM_SunShield is still shade gear (%s)" % shield[0])
    if factors:
        fails.append("gear: %d shade-gear comp(s) carry a per-kind factor: %s" % (len(factors), "; ".join(factors[:6])))
    if not shield and not factors:
        rows.append("PASS gear: no RM_SunShield shade gear, no per-kind gear factor outside a held mod")


def _defs_in_mod(root, mod, tag):
    out = {}
    for f in glob.glob(_p(root, "src", "RimMandrake", mod, "**", "*.xml"), recursive=True):
        r = parse(f)
        if r is None:
            continue
        for d in r.iter(tag):
            out[d.findtext("defName") or "?"] = d
    return out


def check_air_heat(root, rows, fails):
    held = held_mods(root)
    for biome, (mod, cond) in sorted(AIR.items()):
        biomes = _defs_in_mod(root, mod, "BiomeDef")
        b = biomes.get(biome)
        if b is None:
            raise CouldNotLook("BiomeDef %s not found in %s" % (biome, mod))
        if mod in held:
            rows.append("HELD air_heat: %s (%s is held; its air heat is owed at its next build)" % (biome, mod))
            continue
        exts = [li for li in b.iter("li") if cls_is(li, "RM_AirHeatExtension")]
        named = [li.findtext("condition") for li in exts]
        why = []
        if cond not in named:
            why.append("its BiomeDef names no RM_AirHeatExtension condition %s (names %s)" % (cond, named))
        c = _defs_in_mod(root, mod, "GameConditionDef").get(cond)
        if c is None:
            why.append("no GameConditionDef %s in %s" % (cond, mod))
        else:
            if (c.findtext("conditionClass") or "").strip() != "GameCondition_TemperatureOffset":
                why.append("%s is not a GameCondition_TemperatureOffset" % cond)
            try:
                if float(c.findtext("temperatureOffset") or "0") == 0:
                    why.append("%s has no temperatureOffset" % cond)
            except ValueError:
                why.append("%s temperatureOffset unreadable" % cond)
        sun = [x.tag for li in b.iter("li") if cls_is(li, EXT_CLASS) for x in li if x.tag in REMOVED_EXT]
        if sun:
            why.append("its BiomeDef still carries a sun number %s" % sun)
        if why:
            fails.append("air_heat %s: %s" % (biome, "; ".join(why)))
        else:
            rows.append("PASS air_heat: %s is hotter air (%s), no sun number" % (biome, cond))


def check_weather(root, rows, fails):
    p = _p(root, "src", "RimMandrake", "CreatureBehaviors", "Patches", "RM_DirectSun_WeatherSun.xml")
    r = parse(p) if os.path.isfile(p) else None
    got = {}
    if r is not None:
        for op in r.iter("Operation"):
            xp = op.findtext("xpath") or ""
            v = op.find("value/li/sunExposureFactor")
            if v is None:
                continue
            for n in re.findall(r'defName="(\w+)"', xp):
                got[n] = float(v.text)
    miss = [w for w in OVERCAST if not (w in got and got[w] < 1)]
    if miss:
        fails.append("weather: no sun factor below 1 for %s" % ",".join(miss))
    else:
        rows.append("PASS weather: %d vanilla weathers dim Direct Sun" % len(got))


SET = {"TheForge": ("RM_TheForgeMod.cs", "RM_ForgeAirHeat"), "TerminalBiomes": ("RM_TerminalBiomesMod.cs", "RM_ScaldAirHeat"),
       "Greentide": ("RM_GreentideMod.cs", "RM_GreentideAirHeat"), "FeverWood": ("RM_FeverWoodMod.cs", "RM_FeverWoodAirHeat")}


def check_settings(root, rows, fails):
    p = _p(root, "src", "RimMandrake", "CreatureBehaviors", "Source", "RM_CreatureBehaviorsMod.cs")
    if not os.path.isfile(p):
        raise CouldNotLook("%s is missing" % p)
    with open(p, encoding="utf-8") as h:
        s = h.read()
    why = []
    if re.search(r"\bkindFromElevationEnabled\b", s):
        why.append("kindFromElevationEnabled is still a setting")
    if not re.search(r"public static float directSunZenithC\s*=\s*RM_DirectSun\.ZenithDefaultC\s*;", s):
        why.append("no directSunZenithC defaulting to RM_DirectSun.ZenithDefaultC")
    if not re.search(r'Scribe_Values\.Look\(ref directSunZenithC, "directSunZenithC", RM_DirectSun\.ZenithDefaultC\)', s):
        why.append("directSunZenithC is not saved with its default")
    if not re.search(r"public static bool directSunWeatherDims\s*=\s*true\s*;", s) or not re.search(
            r'Scribe_Values\.Look\(ref directSunWeatherDims, "directSunWeatherDims", true\)', s):
        why.append("no directSunWeatherDims defaulting on and saved")
    if 'CheckboxLabeled("Direct Sun", ref sunHeatEnabled' not in s:
        why.append('the master switch is not labelled "Direct Sun"')
    m = _p(root, "src", "RimMandrake", "CreatureBehaviors", "Source", "RM_SunHeatMath.cs")
    if not os.path.isfile(m) or not re.search(r"ZenithDefaultC\s*=\s*55f", open(m, encoding="utf-8").read()):
        why.append("RM_DirectSun.ZenithDefaultC is not 55")
    held = held_mods(root)
    for mod, (fname, cond) in sorted(SET.items()):
        if mod in held:
            rows.append("HELD settings: %s (its air-heat settings are owed at its next build)" % mod)
            continue
        f = _p(root, "src", "RimMandrake", mod, "Source", fname)
        t = open(f, encoding="utf-8").read() if os.path.isfile(f) else ""
        projs = glob.glob(_p(root, "src", "RimMandrake", mod, "Source", "*.csproj"))
        linked = any("AirHeat\\AirHeatSetting.cs" in open(c, encoding="utf-8").read() for c in projs)
        helper = _p(root, "src", "RimMandrake", "_Shared", "AirHeat", "AirHeatSetting.cs")
        writes = os.path.isfile(helper) and "def.temperatureOffset = on ? degreesC : 0f;" in open(helper, encoding="utf-8").read()
        if not (re.search(r"public static bool airHeatEnabled\s*=\s*true", t) and re.search(r"public static float airHeatC\s*=", t)
                and "Scribe_Values.Look(ref airHeatEnabled" in t and "Scribe_Values.Look(ref airHeatC" in t
                and re.search(r'AirHeatSetting\.Apply\("%s"' % cond, t) and linked and writes
                and "plants feel it too" in t and "[StaticConstructorOnStartup]" in t and "WriteSettings" in t):
            why.append("%s: no airHeatEnabled/airHeatC row that writes %s's temperatureOffset (at startup and on close) with "
                       "its label" % (mod, cond))
    if why:
        fails.append("settings: " + "; ".join(why))
    else:
        rows.append("PASS settings: Direct Sun rows (zenith 55, weather on, no kind toggle) and each air-heat mod's switch")


# The promises of design/specs/2026-11-26-direct-sun/boundary.md, one test each (boundary_check.py).
t_every_biome_carries_no_sun_field = check_every_biome
t_no_code_names_a_heat_kind = check_code
t_the_extension_holds_no_sun_number = check_extension
t_removed_fields_are_stripped_at_load = check_strip
t_shade_gear_is_parasol_and_tent = check_gear
t_hot_air_is_a_vanilla_condition = check_air_heat
t_weather_dims_direct_sun = check_weather
t_settings_rows_match_the_ruling = check_settings

CHECKS = [("every_biome", check_every_biome), ("code", check_code), ("extension", check_extension),
          ("strip", check_strip), ("gear", check_gear), ("air_heat", check_air_heat), ("weather", check_weather),
          ("settings", check_settings)]


def run(root, only):
    rows, fails = [], []
    for name, fn in CHECKS:
        if only and name not in only:
            continue
        fn(root, rows, fails)
    return rows, fails


# ---- planted faults: each check must go red on its own fault -------------------------------------------------------

def _copy(root, tmp):
    for rel in ["src"]:
        shutil.copytree(_p(root, rel), _p(tmp, rel), ignore=shutil.ignore_patterns(
            "*.dll", "*.png", "*.jpg", "*.ogg", "*.wav", "Textures", "Sounds", "bin", "obj", "Assemblies", "*.pdb"))


def _edit(path, old, new):
    with open(path, encoding="utf-8") as f:
        s = f.read()
    if old not in s:
        raise CouldNotLook("planted fault: %r not in %s" % (old[:60], path))
    with open(path, "w", encoding="utf-8") as f:
        f.write(s.replace(old, new, 1))


def mutate(root, only):
    plants = [
        ("every_biome", "src/RimMandrake/Pyrelands/Defs/BiomeDefs/Pyrelands.xml", "<modExtensions>",
         '<modExtensions>\n      <li Class="RimMandrake.CreatureBehaviors.RM_SunHeatExtension"><heatOffsetC>10</heatOffsetC></li>'),
        ("code", "src/RimMandrake/CreatureBehaviors/Source/RM_SunHeatMath.cs", "public static class RM_DirectSun",
         "public enum RM_HeatKind { overhead }\n    public static class RM_DirectSun"),
        ("extension", "src/RimMandrake/CreatureBehaviors/Source/RM_SunHeatExtension.cs",
         "public float substellarLatitude = 0f;", "public float substellarLatitude = 0f;\n        public float heatOffsetC = 30f;"),
        ("strip", "src/RimMandrake/CreatureBehaviors/Patches/RM_DirectSun_LegacyFields.xml", "/heatKind</xpath>", "/heatKindX</xpath>"),
        ("gear", "src/RimMandrake/EnvironmentalHazards/Defs/ThingDefs_Buildings/RM_ShadeGear.xml", "<mode>footprint</mode>",
         "<mode>footprint</mode><lowSunFactor>0.3</lowSunFactor>"),
        ("air_heat", "src/RimMandrake/TheForge/Defs/GameConditionDefs/RM_ForgeAirHeat.xml",
         "<temperatureOffset>15</temperatureOffset>", "<temperatureOffset>0</temperatureOffset>"),
        ("weather", "src/RimMandrake/CreatureBehaviors/Patches/RM_DirectSun_WeatherSun.xml", 'defName="Overcast"', 'defName="OvercastX"'),
        ("settings", "src/RimMandrake/CreatureBehaviors/Source/RM_CreatureBehaviorsMod.cs",
         "public static bool directSunWeatherDims = true;", "public static bool directSunWeatherDims = false;"),
    ]
    out = []
    for name, rel, old, new in plants:
        if only and name not in only:
            continue
        tmp = tempfile.mkdtemp(prefix="ds_mut_")
        try:
            _copy(root, tmp)
            _edit(_p(tmp, rel), old, new)
            _, fails = run(tmp, {name})
            caught = any(f.startswith(name) for f in fails)
            out.append(("CAUGHT" if caught else "NOT CAUGHT", name, rel))
        finally:
            shutil.rmtree(tmp, ignore_errors=True)
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--only", default="", help="comma list of checks: " + ",".join(n for n, _ in CHECKS))
    ap.add_argument("--no-mutate", action="store_true", help="skip the planted-fault pass")
    ap.add_argument("--held-is-fail", action="store_true",
                    help="a HELD row fails (the outcome check of RIMMANDRAKE_STRIP_HELD_BIOMES_LEGACY_SUN_FIELDS_AT_LIFT)")
    ap.add_argument("--root", default=REPO, help=argparse.SUPPRESS)
    a = ap.parse_args(argv)
    # Every promise's test runs by default; --only narrows a run by hand.
    promised = (t_every_biome_carries_no_sun_field, t_no_code_names_a_heat_kind, t_the_extension_holds_no_sun_number,
                t_removed_fields_are_stripped_at_load, t_shade_gear_is_parasol_and_tent, t_hot_air_is_a_vanilla_condition,
                t_weather_dims_direct_sun, t_settings_rows_match_the_ruling)
    assert all(fn in dict(CHECKS).values() for fn in promised)
    only = {x.strip() for x in a.only.split(",") if x.strip()}
    unknown = only - {n for n, _ in CHECKS}
    if unknown:
        print("COULD NOT LOOK: unknown check(s) %s" % ",".join(sorted(unknown)))
        return 2
    try:
        rows, fails = run(a.root, only)
    except CouldNotLook as e:
        print("COULD NOT LOOK: %s" % e)
        return 2
    for r in rows:
        print(r)
    if a.held_is_fail:
        fails += ["held: " + r[len("HELD "):] for r in rows if r.startswith("HELD ")]
    for f in fails:
        print("FAIL " + f)
    if fails:
        print("%d check(s) failed" % len(fails))
        return 1
    if not a.no_mutate:
        try:
            muts = mutate(a.root, only)
        except CouldNotLook as e:
            print("COULD NOT LOOK: %s" % e)
            return 2
        for verdict, name, rel in muts:
            print("%s planted fault: %s (%s)" % (verdict, name, rel))
        if any(v != "CAUGHT" for v, _, _ in muts):
            print("FAIL a planted fault was not caught")
            return 1
    print("ALL PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
