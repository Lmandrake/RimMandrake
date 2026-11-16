#!/usr/bin/env python3
"""T_DEFS_OFFLINE (Pyrelands 0.1.0, RIMMANDRAKE_PIN_PYRE_DEF_FACTS_OFFLINE): the static def facts its bars rest on.

Reads the repo's XML and C# only (plus the def dump for the rainRate of weathers that are not ours):
  no_ordinary_rain       every weather on RM_Pyrelands's list, native AND patch-added, has rainRate 0 except black rain
  engineered             the biome description says the savanna was "genetically engineered", not negated in its clause
  venom tendable (g7)    RM_FlamefangVenom is tendable, immunizable, and tended severity falls (rise + tended < 0)
  furnace (g6 static)    RM_FurnaceBeast body size at least twice every other RM_Pyrelands animal's (native AND
                         patch-added rows) and its adult draw size strictly the largest; Patch_FurnaceBeastHeatImmunity
                         names it and absorbs Heat damage
  sand shovel            RM_FE_Ground_Sand digs to 5 RM_GlassSand and leaves RM_FE_Ground_Gravel

Then every planted fault (a mutant copy of the files) must turn at least one fact red, and the clean copy must stay green.
Run: python3 <this file>      exit 0 = PASS, 1 = a fact or a mutant failed, 2 = UNMEASURED (no def dump)
"""
import glob
import json
import os
import re
import shutil
import sqlite3
import sys
import tempfile
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(REPO, "src", "RimMandrake", "Utils"))
MOD = "src/RimMandrake/Pyrelands"
BIOME = "RM_Pyrelands"
BLACK_RAIN = "RM_FE_BlackRain"


def _xml_files(root, sub):
    return glob.glob(os.path.join(root, "src", "Rim*", "**", sub, "**", "*.xml"), recursive=True)


def _parse(f):
    try:
        return ET.parse(f).getroot()
    except ET.ParseError:
        return None


def _defs(root, tag):
    """Every <tag> def in the repo's Defs folders, by defName and by Name (for ParentName)."""
    by_name, by_abstract = {}, {}
    for f in _xml_files(root, "Defs"):
        r = _parse(f)
        if r is None:
            continue
        for d in r.iter(tag):
            if d.findtext("defName"):
                by_name[d.findtext("defName")] = d
            if d.get("Name"):
                by_abstract[d.get("Name")] = d
    return by_name, by_abstract


def _field(d, field, abstract):
    seen = 0
    while d is not None and seen < 10:
        v = d.findtext(field)
        if v is not None:
            return v
        d = abstract.get(d.get("ParentName"))
        seen += 1
    return None


def _dump_rain(names):
    from game_paths import DUMP_ROOT
    p = os.path.join(str(DUMP_ROOT), "defs.sqlite")
    if not os.path.exists(p):
        return None
    con = sqlite3.connect("file:" + p + "?mode=ro&immutable=1", uri=True)
    out = {}
    for n in names:
        row = con.execute("select json from defs where def_name=? and def_type='WeatherDef'", (n,)).fetchone()
        if row:
            out[n] = float(json.loads(row[0])["fields"].get("rainRate") or 0)
    return out


def weather_list(root):
    """RM_Pyrelands's weather names: its own baseWeatherCommonalities plus every patch Add aimed at that list."""
    biomes, _ = _defs(root, "BiomeDef")
    b = biomes.get(BIOME)
    names = []
    if b is not None and b.find("baseWeatherCommonalities") is not None:
        for c in b.find("baseWeatherCommonalities"):
            names.append(c.findtext("weather") if c.tag == "li" else c.tag)
    for f in _xml_files(root, "Patches"):
        r = _parse(f)
        if r is None:
            continue
        for op in r.iter():
            xp = op.findtext("xpath") or ""
            if 'defName="%s"' % BIOME in xp and "WeatherCommonalities" in xp and op.find("value") is not None:
                for c in op.find("value"):
                    names.append(c.findtext("weather") if c.tag == "li" else c.tag)
    return names


def _race_field(d, field, abstract):
    """A ThingDef's race/<field>, walking ParentName (race is a child element, so _field cannot)."""
    seen = 0
    while d is not None and seen < 10:
        r = d.find("race")
        if r is not None and r.findtext(field) is not None:
            return r.findtext(field)
        d = abstract.get(d.get("ParentName"))
        seen += 1
    return None


def _adult_draw(k, abstract):
    """A PawnKindDef's last life stage bodyGraphicData/drawSize (a bare number or "(x,y)": the larger side)."""
    seen = 0
    while k is not None and seen < 10:
        ls = k.find("lifeStages")
        if ls is not None and len(ls):
            v = ls[-1].findtext("bodyGraphicData/drawSize")
            if v is None:
                return None
            return max(float(x) for x in v.strip().strip("()").split(","))
        k = abstract.get(k.get("ParentName"))
        seen += 1
    return None


def animal_roster(root):
    """RM_Pyrelands's wild animals: its own <wildAnimals> plus every patch Add aimed at that list (XML elements)."""
    biomes, _ = _defs(root, "BiomeDef")
    b = biomes.get(BIOME)
    names = []

    def take(node):
        for c in node:
            names.append(c.findtext("animal") if c.tag == "li" else c.tag)
    if b is not None and b.find("wildAnimals") is not None:
        take(b.find("wildAnimals"))
    for f in _xml_files(root, "Patches"):
        r = _parse(f)
        if r is None:
            continue
        for op in r.iter():
            xp = op.findtext("xpath") or ""
            if 'defName="%s"' % BIOME in xp and xp.rstrip("/").endswith("wildAnimals") and op.find("value") is not None:
                take(op.find("value"))
    return names


def facts(root, dump_rain):
    out = []

    def fact(name, ok, detail):
        out.append((name, bool(ok), detail))

    # no ordinary rain
    names = weather_list(root)
    ours, ab = _defs(root, "WeatherDef")
    rain = {}
    for n in names:
        if n in ours:
            rain[n] = float(_field(ours[n], "rainRate", ab) or 0)
        elif n in dump_rain:
            rain[n] = dump_rain[n]
        else:
            rain[n] = None
    unknown = [n for n, v in rain.items() if v is None]
    wet = sorted(n for n, v in rain.items() if v and n != BLACK_RAIN)
    fact("no_ordinary_rain", names and not unknown and not wet and rain.get(BLACK_RAIN, 0) > 0,
         "%d weathers; raining other than black rain: %s; unknown: %s; black rain rainRate %s"
         % (len(names), wet or "none", unknown or "none", rain.get(BLACK_RAIN)))
    # engineered
    biomes, _ = _defs(root, "BiomeDef")
    desc = (biomes.get(BIOME).findtext("description") if BIOME in biomes else "") or ""
    # The leaf: the savanna WAS genetically engineered (blind challenge cycle 2: "\bengineered\b" alone passed "never
    # genetically engineered"); no negation in the clause before the phrase.
    eng = re.search(r"\bgenetically engineered\b", desc, re.I)
    clause = re.split(r"[.;:!?]", desc[:eng.start()])[-1] if eng else ""
    negated = re.search(r"\b(not|never|no longer|nor|un)\b|n't\b", clause, re.I)
    fact("biome_text_says_engineered", eng and not negated,
         "description %d chars%s" % (len(desc), "; negated: %r" % negated.group(0) if negated else ""))
    # venom
    hd, hab = _defs(root, "HediffDef")
    v = hd.get("RM_FlamefangVenom")
    ok, det = False, "RM_FlamefangVenom missing"
    if v is not None:
        comps = {c.get("Class"): c for c in v.find("comps")} if v.find("comps") is not None else {}
        imm, tend = comps.get("HediffCompProperties_Immunizable"), comps.get("HediffCompProperties_TendDuration")
        rise = float(imm.findtext("severityPerDayNotImmune") or 0) if imm is not None else None
        tended = float(tend.findtext("severityPerDayTended") or 0) if tend is not None else None
        ok = (v.findtext("tendable") or "").lower() == "true" and rise is not None and tended is not None and rise > 0 and rise + tended < 0
        det = "tendable %s, untreated +%s/day, tended %s/day, net tended %s" % (
            v.findtext("tendable"), rise, tended, None if rise is None or tended is None else round(rise + tended, 3))
    fact("flamefang_venom_tending_helps", ok, det)
    # furnace-beast
    td, tab = _defs(root, "ThingDef")
    fb = td.get("RM_FurnaceBeast")
    # The owner's bar (scenes.json sc_furnace_giant; by card 2026-11-15 "Keep 'twice', raise body to 9+"): twice every
    # other Pyrelands animal, the patch-added cast included. A roster that reads fewer than 16 kinds, or a kind whose
    # size will not resolve, is a blind instrument and fails.
    pk, pab = _defs(root, "PawnKindDef")
    sizes, draws, blind = {}, {}, []
    for n in animal_roster(root):
        k = pk.get(n)
        race = td.get(k.findtext("race")) if k is not None else None
        bs = _race_field(race, "baseBodySize", tab)
        dr = _adult_draw(k, pab)
        if bs is None or dr is None:
            blind.append(n)
            continue
        sizes[n], draws[n] = float(bs), dr
    fbs, fdr = sizes.pop("RM_FurnaceBeast", None), draws.pop("RM_FurnaceBeast", None)
    big = max(sizes, key=sizes.get) if sizes else None
    fact("furnace_twice_every_pyrelands_animal",
         fbs is not None and big and not blind and len(sizes) >= 15 and fbs >= 2 * sizes[big],
         "furnace %s vs largest other %s %s (needs >= %s); %d other kinds; unresolved %s"
         % (fbs, big, sizes.get(big), 2 * sizes[big] if big else None, len(sizes), blind or "none"))
    tall = max(draws, key=draws.get) if draws else None
    fact("furnace_drawn_largest", fdr is not None and tall and fdr > draws[tall],
         "furnace adult drawSize %s vs largest other %s %s" % (fdr, tall, draws.get(tall)))
    cs = open(os.path.join(root, MOD, "Source", "Patch_FurnaceBeastHeatImmunity.cs"), errors="replace").read()
    fact("furnace_heat_patch_targets_it", '"RM_FurnaceBeast"' in cs and re.search(r"absorbed\s*=\s*true", cs)
         and '"Heat"' in cs, "names RM_FurnaceBeast, the Heat category, and sets absorbed = true")
    # sand shovel
    terr, terrab = _defs(root, "TerrainDef")
    sand = terr.get("RM_FE_Ground_Sand")
    ext = None
    if sand is not None and sand.find("modExtensions") is not None:
        ext = next((li for li in sand.find("modExtensions") if (li.get("Class") or "").endswith("RM_TerrainDigYieldExtension")), None)
    y = (ext.findtext("yield"), ext.findtext("count"), ext.findtext("leaves")) if ext is not None else None
    fact("sand_shovel_yields_glass_sand", y == ("RM_GlassSand", "5", "RM_FE_Ground_Gravel") and "RM_GlassSand" in td,
         "yield/count/leaves %s; RM_GlassSand defined %s" % (y, "RM_GlassSand" in td))
    return out


def _mutate(root, rel, old, new):
    p = os.path.join(root, rel)
    t = open(p, errors="replace").read()
    assert old in t, "mutant anchor not found in %s: %r" % (rel, old)
    open(p, "w").write(t.replace(old, new, 1))


D = MOD + "/Defs/"
MUTANTS = [
    ("ordinary rain on the biome list", D + "BiomeDefs/Pyrelands.xml", "<Fog>2</Fog>", "<Fog>2</Fog><Rain>3</Rain>"),
    ("ordinary rain patch-added", "src/RimUtinni/UtinniPatches/Patches/AshStorms_Pyrelands.xml",
     "<RM_VolcanicAsh>3</RM_VolcanicAsh>", "<RM_VolcanicAsh>3</RM_VolcanicAsh><RainyThunderstorm>2</RainyThunderstorm>"),
    ("black rain dry", D + "WeatherDefs/BlackRain.xml", "<rainRate>1.1</rainRate>", "<rainRate>0</rainRate>"),
    ("ash fall rains", D + "WeatherDefs/AshFall.xml", "<rainRate>0</rainRate>", "<rainRate>0.5</rainRate>"),
    ("not engineered", D + "BiomeDefs/Pyrelands.xml", "genetically engineered", "planted"),
    ("engineered negated", D + "BiomeDefs/Pyrelands.xml", "savanna, genetically engineered", "savanna, never genetically engineered"),
    ("engineered without genetically", D + "BiomeDefs/Pyrelands.xml", "genetically engineered", "engineered"),
    ("venom not tendable", D + "HediffDefs/RM_FlamefangVenom.xml", "<tendable>true</tendable>", "<tendable>false</tendable>"),
    ("tending too weak", D + "HediffDefs/RM_FlamefangVenom.xml", "<severityPerDayTended>-0.4<", "<severityPerDayTended>-0.2<"),
    ("furnace size 8.9", D + "ThingDefs_Races/RM_PyrelandsFauna.xml", "<baseBodySize>9</baseBodySize>", "<baseBodySize>8.9</baseBodySize>"),
    ("zeer outgrows half", "src/RimStarWars/SWBestiary/Defs/ThingDefs_Races/RSW_Zeer.xml", "<baseBodySize>4.5</baseBodySize>",
     "<baseBodySize>4.6</baseBodySize>"),
    ("patch-added giant", "src/RimUtinni/UtinniPatches/Patches/WildAnimals_Pyrelands.xml", "<RSW_Gizka>1.0</RSW_Gizka>",
     "<RSW_Gizka>1.0</RSW_Gizka><RSW_Fambaa>0.1</RSW_Fambaa>"),
    ("roster kind unresolvable", "src/RimUtinni/UtinniPatches/Patches/WildAnimals_Pyrelands.xml", "<RSW_Gizka>1.0</RSW_Gizka>",
     "<RSW_Gizka>1.0</RSW_Gizka><RSW_NoSuchBeast>0.1</RSW_NoSuchBeast>"),
    ("furnace drawn as the zeer", D + "ThingDefs_Races/RM_PyrelandsFauna.xml", "<drawSize>7.5</drawSize>", "<drawSize>6</drawSize>"),
    ("heat patch on wrong def", MOD + "/Source/Patch_FurnaceBeastHeatImmunity.cs", '"RM_FurnaceBeast"', '"RM_Ullai"'),
    ("heat patch absorbs nothing", MOD + "/Source/Patch_FurnaceBeastHeatImmunity.cs", "absorbed = true", "absorbed = false"),
    ("shovel yields 4", D + "TerrainDefs/ScorchableGround.xml", "<count>5</count>", "<count>4</count>"),
    ("shovel leaves sand", D + "TerrainDefs/ScorchableGround.xml", "<leaves>RM_FE_Ground_Gravel</leaves>", "<leaves>RM_FE_Ground_Sand</leaves>"),
]


def _copy(dst):
    """Copy only what facts() reads: every src/Rim*/**/Defs, Patches and the mod's Source."""
    for f in _xml_files(REPO, "Defs") + _xml_files(REPO, "Patches") + glob.glob(os.path.join(REPO, MOD, "Source", "*.cs")):
        rel = os.path.relpath(f, REPO)
        os.makedirs(os.path.dirname(os.path.join(dst, rel)), exist_ok=True)
        shutil.copy2(f, os.path.join(dst, rel))


def main():
    try:
        names = weather_list(REPO)
    except Exception as e:  # pragma: no cover
        print("FAIL: weather list unreadable: %s" % e)
        return 1
    ours, _ = _defs(REPO, "WeatherDef")
    dump = _dump_rain([n for n in names if n not in ours] + ["Rain", "RainyThunderstorm"])
    if dump is None:
        print("UNMEASURED: no def dump (defs.sqlite) for the rainRate of weathers that are not ours")
        return 2
    bad = 0
    got = facts(REPO, dump)
    for name, ok, det in got:
        print("%-34s %s  %s" % (name, "ok  " if ok else "FAIL", det))
        bad += not ok
    tmp = tempfile.mkdtemp(prefix="pyre_defs_mut_")
    try:
        base = os.path.join(tmp, "base")
        _copy(base)
        if not all(ok for _, ok, _ in facts(base, dump)):
            print("FAIL: the unchanged copy is not green (the copy misses a file facts() reads)")
            return 1
        red = 0
        for label, relp, old, new in MUTANTS:
            m = os.path.join(tmp, "m%d" % red)
            shutil.copytree(base, m)
            _mutate(m, relp, old, new)
            fails = [n for n, ok, _ in facts(m, dump) if not ok]
            print("mutant %-30s %s %s" % (label, "red " if fails else "NOT CAUGHT", ",".join(fails)))
            bad += not fails
            red += bool(fails)
            shutil.rmtree(m)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    if bad:
        print("FAIL: %d fact(s) or mutant(s) wrong" % bad)
        return 1
    print("PASS: %d def facts hold, %d of %d mutants red, the clean copy green" % (len(got), red, len(MUTANTS)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
