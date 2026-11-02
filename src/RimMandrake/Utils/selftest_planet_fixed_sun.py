#!/usr/bin/env python3
"""PLANET_GEOMETRY_WIDEN_SUN_STANDS_STILL: the planet's sun geometry has ONE provider and Sun & Shade reads it.

Offline, source-level (the reader is reflection against RimWorld's def database, which no offline test can load):
  1. WeatherSuite's PlanetGeometryDef declares `public bool fixedSun;` (default false: no def or false = day/night world).
  2. The one shipped PlanetGeometryDef (Ash'karr, RimUtinni) sets <fixedSun>true</fixedSun>.
  3. CreatureBehaviors' RM_PlanetSunGeometry names the def's real full type name, and every field it reflects on
     (AccessTools.Field(geo, "x")) is a field the def declares: a rename on either side would read silently as "no def".
  4. RM_PlanetSunGeometry.cs is compiled (listed in RM_CreatureBehaviors.csproj).
  5. Every sun resolver takes E and the bearing through RM_PlanetSunGeometry: ShadeGrid.ResolveSun and
     PinnedSun.ResolveGeometry call TrySunAt and no longer hand a biome extension's substellar point to SunGeometry;
     the world-view sun reads RM_PlanetSunGeometry and does no reflection of its own.
  6. The def's point is actually USED: Resolve binds substellarLat/Lon/fixedSun to the def's same-named fields and
     stores their values in the statics (no shadowing local); FixedSun returns the stored flag; SubstellarPoint returns them exactly when `loaded` (the fallback only otherwise); TrySunAt hands
     SubstellarPoint's output, not the fallback, to SunGeometry and derives E = 90 - arc.
Then each check is shown to fire on a planted defect in a temp copy.

    python3 src/RimMandrake/Utils/selftest_planet_fixed_sun.py
"""
import glob
import os
import re
import sys
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.normpath(os.path.join(HERE, "..", ".."))
WS = os.path.join(SRC, "RimMandrake", "WeatherSuite", "Source", "WeatherSuiteHook.cs")
GEO_DIR = os.path.join(SRC, "RimUtinni", "AshkarrWeatherSuite", "Defs")
CB = os.path.join(SRC, "RimMandrake", "CreatureBehaviors", "Source")
READER = os.path.join(CB, "RM_PlanetSunGeometry.cs")
CSPROJ = os.path.join(CB, "RM_CreatureBehaviors.csproj")
SHADE = os.path.join(CB, "RM_MapComponent_ShadeGrid.cs")
PINNED = os.path.join(CB, "RM_MapComponent_PinnedSun.cs")
WORLD = os.path.join(CB, "RM_WorldSunPatch.cs")


def read(p):
    with open(p, encoding="utf-8") as f:
        return f.read()


def method_body(src, name):
    """Text of the first method `name(` from its opening brace to the matching close."""
    m = re.search(r"\b" + re.escape(name) + r"\s*\([^)]*\)\s*\{", src)
    if not m:
        return None
    i, depth = m.end() - 1, 0
    for j in range(i, len(src)):
        depth += {"{": 1, "}": -1}.get(src[j], 0)
        if depth == 0:
            return src[i:j + 1]
    return None


def strip_cs_comments(text):
    """C# source without // and /* */ comments (string literals kept), so commented-out code never counts."""
    return re.sub(r'"(?:\\.|[^"\\\n])*"|/\*.*?\*/|//[^\n]*',
                  lambda m: m.group(0) if m.group(0).startswith('"') else ("" if m.group(0).startswith("//") else " "),
                  text, flags=re.S)


def check(files):
    """files: dict key -> text (geometry xml is a list of texts). Returns list of failure strings."""
    files = dict(files)
    for key in ("ws", "reader", "shade", "pinned", "world"):
        files[key] = strip_cs_comments(files[key])
    fails = []
    ws = files["ws"]
    ns = re.search(r"namespace\s+([\w.]+)", ws)
    cls = re.search(r"public\s+class\s+PlanetGeometryDef\s*:\s*Def\s*\{(.*?)\n    \}", ws, re.S)
    if not ns or not cls:
        return ["ws: PlanetGeometryDef class not found"]
    fields = dict((n, t) for t, n in re.findall(r"public\s+(\w+)\s+(\w+)\s*(?:=[^;]*)?;", cls.group(1)))
    full = ns.group(1) + ".PlanetGeometryDef"
    if fields.get("fixedSun") != "bool":
        fails.append("1 ws: PlanetGeometryDef has no `public bool fixedSun;`")
    elif re.search(r"public\s+bool\s+fixedSun\s*=\s*(?!\s*false\s*;)", cls.group(1)):
        fails.append("1 ws: fixedSun defaults to true; a def that omits it must mean a day/night world")
    elif re.search(r"(?<!public bool )\bfixedSun\s*(?:[|&^]?=(?!=))", cls.group(1)):
        fails.append("1 ws: PlanetGeometryDef assigns fixedSun in its body (a constructor or method); only the XML may set it")

    geos = []
    for text in files["geo"]:
        for d in ET.fromstring(text):
            if d.tag == full or d.tag.endswith("PlanetGeometryDef"):
                geos.append(d)
    if len(geos) != 1:
        fails.append(f"2 geo: {len(geos)} PlanetGeometryDef defs shipped, expected exactly one")
    for d in geos:
        if d.tag != full:
            fails.append(f"2 geo: def tag {d.tag} is not the class's full name {full}")
        if (d.get("Abstract") or "").strip().lower() == "true":
            fails.append(f"2 geo: {d.findtext('defName')} is Abstract, so the def database holds no instance to read")
        if (d.findtext("fixedSun") or "").strip() != "true":
            fails.append(f"2 geo: {d.findtext('defName')} does not set <fixedSun>true</fixedSun> (Ash'karr's sun stands still)")

    rd = files["reader"]
    m = re.search(r'PlanetGeometryDefType\s*=\s*"([^"]+)"', rd)
    if not m or m.group(1) != full:
        fails.append(f"3 reader: PlanetGeometryDefType is {m.group(1) if m else None!r}, not {full!r}")
    reflected = re.findall(r'AccessTools\.Field\(\s*geo\s*,\s*"(\w+)"\s*\)', rd)
    if "fixedSun" not in reflected:
        fails.append("3 reader: RM_PlanetSunGeometry never reads fixedSun")
    for f in ("substellarLat", "substellarLon"):
        if fields.get(f) != "float":
            fails.append(f"3 ws: PlanetGeometryDef.{f} is {fields.get(f)!r}, not float (the reader casts it with (float))")
    for f in reflected:
        if f not in fields:
            fails.append(f"3 reader: reflects on field {f!r}, which PlanetGeometryDef does not declare")

    if '<Compile Include="RM_PlanetSunGeometry.cs" />' not in re.sub(r"<!--.*?-->", "", files["csproj"], flags=re.S):
        fails.append("4 csproj: RM_PlanetSunGeometry.cs is not compiled into CreatureBehaviors")

    for key, meth in (("shade", "ResolveSun"), ("pinned", "ResolveGeometry")):
        body = method_body(files[key], meth)
        if body is None:
            fails.append(f"5 {key}: method {meth} not found")
            continue
        if "RM_PlanetSunGeometry.TrySunAt(" not in body:
            fails.append(f"5 {key}: {meth} does not take E and the bearing from RM_PlanetSunGeometry.TrySunAt")
        call = re.search(r"RM_PlanetSunGeometry\.TrySunAt\(\s*map\.Tile\s*,\s*ext\.substellarLatitude\s*,\s*ext\.substellarLongitude\s*,"
                         r"\s*out\s+float\s+(\w+)\s*,\s*out\s+float\s+(\w+)\s*\)", body)
        if not call or not re.search("elev", call.group(1), re.I) or not re.search("bearing", call.group(2), re.I):
            fails.append(f"5 {key}: {meth}'s TrySunAt call is not (map.Tile, lat, lon, out <elevation>, out <bearing>) in that order")
        elif re.search(r"\b(?:" + call.group(1) + "|" + call.group(2) + r")\s*(?:[-+*/|&^]?=(?!=)|\+\+|--)", body[call.end():]):
            fails.append(f"5 {key}: {meth} overwrites TrySunAt's E or bearing after receiving them")
        if re.search(r"SunGeometry\([^;]*ext\.substellar", body):
            fails.append(f"5 {key}: {meth} still hands the biome extension's substellar point to SunGeometry")
    if not re.search(r"private\s+static\s+Vector3\?\s+pinned\s*;", files["world"]):
        fails.append("5 world: the cache is not declared `private static Vector3? pinned;` (must start empty)")
    if len(re.findall(r"\bpinned\s*(?:[-+*/|&^]?=(?!=)|\+\+|--)", files["world"])) != 1:
        fails.append("5 world: `pinned` is assigned somewhere other than PinnedDirection's one store")
    post = method_body(files["world"], "Postfix_CurSunPositionInWorldSpace")
    if post is None or not re.match(r"\{\s*if\s*\(\s*!\s*RM_WorldStarsMath\.PinsWorldSun\(\s*RM_CreatureBehaviorsSettings\.worldSunPinned\s*,\s*Current\.ProgramState\s*==\s*ProgramState\.Playing\s*\)\s*\)"
                                     r"\s*\{\s*return\s*;\s*\}\s*__result\s*=\s*PinnedDirection\(\)\s*;\s*\}$", post):
        fails.append("5 world: the world-sun postfix is not `if (!PinsWorldSun(setting, Playing)) return; __result = PinnedDirection();`")
    world = method_body(files["world"], "PinnedDirection")
    if world is None or "RM_PlanetSunGeometry." not in world:
        fails.append("5 world: PinnedDirection does not read RM_PlanetSunGeometry")
    elif not re.search(r"if\s*\(\s*RM_PlanetSunGeometry\.Loaded\s*\)\s*\{\s*RM_PlanetSunGeometry\.SubstellarPoint\(\s*0f\s*,\s*0f\s*,\s*out\s+lat\s*,\s*out\s+lon\s*\)\s*;"
                       r"\s*source\s*=[^;]*;\s*\}\s*else\s*\{\s*foreach\s*\(\s*BiomeDef\b", world):
        fails.append("5 world: PinnedDirection does not take (lat, lon) from RM_PlanetSunGeometry.SubstellarPoint when a def is loaded, with the biome fallback only in the else")
    elif not re.match(r"\{\s*if\s*\(\s*pinned\.HasValue\s*\)\s*return\s+pinned\.Value\s*;\s*float\s+lat\s*=\s*0f\s*,\s*lon\s*=\s*0f\s*;", world):
        fails.append("5 world: PinnedDirection does not open with `if (pinned.HasValue) return pinned.Value; float lat = 0f, lon = 0f;`")
    elif not re.search(r"\}\s*catch\s*\(\s*Exception\s+e\s*\)\s*\{[^{}]*\}\s*RM_WorldStarsMath\.SubstellarDirection\(", world):
        fails.append("5 world: something runs between the try/catch and SubstellarDirection (it could overwrite the def's lat/lon)")
    elif not re.search(r"SubstellarDirection\(\s*lat\s*,\s*lon\s*,\s*out\s+float\s+x\s*,\s*out\s+float\s+y\s*,\s*out\s+float\s+z\s*\)\s*;"
                       r"\s*pinned\s*=\s*new\s+Vector3\(\s*x\s*,\s*y\s*,\s*z\s*\)\s*;\s*Log\.Message\([^;]*\)\s*;\s*return\s+pinned\.Value\s*;\s*\}$", world):
        fails.append("5 world: PinnedDirection does not hand (lat, lon) to SubstellarDirection and return new Vector3(x, y, z)")
    elif "GetTypeInAnyAssembly" in world or "AccessTools.Field" in world:
        fails.append("5 world: PinnedDirection reflects on the geometry def itself (a second reader)")

    for f in reader_use_fails(rd):
        fails.append(f)
    return fails


def reader_use_fails(rd):
    """Clause 6: the def's substellar point flows from the def's fields to SunGeometry."""
    fails = []
    res = method_body(rd, "Resolve") or ""
    for typ, name in (("bool", "resolved"), ("bool", "loaded"), ("float", "substellarLat"), ("float", "substellarLon"),
                      ("bool", "fixedSun"), ("string", "defName")):
        if not re.search(r"private\s+static\s+" + typ + r"\s+" + name + r"\s*;", rd):
            fails.append(f"6 reader: static `{name}` is not declared `private static {typ} {name};` (no initializer)")
    if not re.match(r"\{\s*if\s*\(\s*resolved\s*\)\s*\{\s*return\s*;\s*\}\s*resolved\s*=\s*true\s*;", res):
        fails.append("6 reader: Resolve does not open with the read-once guard (if (resolved) return; resolved = true;)")
    flow = (r"Type\s+geo\s*=\s*GenTypes\.GetTypeInAnyAssembly\(\s*PlanetGeometryDefType\s*\)\s*;\s*if\s*\(\s*geo\s*==\s*null\s*\)\s*\{\s*return\s*;\s*\}",
            r"if\s*\(\s*fLat\s*==\s*null\s*\|\|\s*fLon\s*==\s*null\s*\)\s*\{[^{}]*return\s*;\s*\}",
            r"foreach\s*\(\s*Def\s+d\s+in\s+GenDefDatabase\.GetAllDefsInDatabaseForDef\(\s*geo\s*\)\s*\)\s*\{"
            r"\s*substellarLat\s*=\s*\(float\)\s*fLat\.GetValue\(\s*d\s*\)\s*;\s*substellarLon\s*=\s*\(float\)\s*fLon\.GetValue\(\s*d\s*\)\s*;"
            r"\s*fixedSun\s*=\s*fFixed\s*!=\s*null\s*&&\s*\(bool\)\s*fFixed\.GetValue\(\s*d\s*\)\s*;\s*defName\s*=\s*d\.defName\s*;"
            r"\s*loaded\s*=\s*true\s*;\s*break\s*;\s*\}")
    for i, pat in enumerate(flow):
        if not re.search(pat, res):
            fails.append(("6 reader: Resolve's type lookup guard is not `if (geo == null) return;`",
                          "6 reader: Resolve's missing-field guard is not `if (fLat == null || fLon == null) ... return;`",
                          "6 reader: Resolve's def loop is not exactly: read lat, lon, fixedSun, defName from d; loaded = true; break")[i])
    for var, field in (("fLat", "substellarLat"), ("fLon", "substellarLon")):
        if not re.search(r"FieldInfo\s+" + var + r'\s*=\s*AccessTools\.Field\(\s*geo\s*,\s*"' + field + r'"\s*\)', res):
            fails.append(f"6 reader: Resolve does not bind {var} to the def's {field} field")
        if not re.search(r"(?m)^\s*" + field + r"\s*=\s*\(float\)\s*" + var + r"\.GetValue\(\s*d\s*\)\s*;", res):
            fails.append(f"6 reader: Resolve does not store the def's {field} ({var}.GetValue(d))")
    shadow = re.findall(r"\b(?!return\b|else\b|out\b|ref\b)(?:[A-Za-z_][\w.<>\[\]?]*\s+|,\s*)(substellarLat|substellarLon|loaded|fixedSun)\s*[;=,]", res)
    if shadow:
        fails.append(f"6 reader: Resolve declares a local {shadow[0]!r} that shadows the static field it must set")
    for name, n in (("substellarLat", 1), ("substellarLon", 1), ("fixedSun", 1), ("loaded", 2), ("resolved", 1)):
        writes = len(re.findall(r"(?m)^\s*" + name + r"\s*(?:[|&^]?=(?!=))", rd))
        if writes != n:
            fails.append(f"6 reader: static `{name}` is written {writes} times, expected {n} (a later write could undo the def's value)")
    if not re.search(r"catch\s*\(\s*Exception\s+e\s*\)\s*\{\s*loaded\s*=\s*false\s*;", rd):
        fails.append("6 reader: `loaded = false;` is not the catch block's first statement (it must only undo a failed read)")
    if not re.search(r'FieldInfo\s+fFixed\s*=\s*AccessTools\.Field\(\s*geo\s*,\s*"fixedSun"\s*\)', res):
        fails.append("6 reader: Resolve does not bind fFixed to the def's fixedSun field")
    if not re.search(r"(?m)^\s*fixedSun\s*=\s*fFixed\s*!=\s*null\s*&&\s*\(bool\)\s*fFixed\.GetValue\(\s*d\s*\)\s*;", res):
        fails.append("6 reader: Resolve does not store the def's fixedSun (fFixed.GetValue(d))")
    if not re.search(r"public\s+static\s+bool\s+Loaded\s*\{\s*get\s*\{\s*Resolve\(\)\s*;\s*return\s+loaded\s*;\s*\}\s*\}", rd):
        fails.append("6 reader: Loaded does not return `loaded` after Resolve()")
    if not re.search(r"public\s+static\s+string\s+DefName\s*\{\s*get\s*\{\s*Resolve\(\)\s*;\s*return\s+defName\s*;\s*\}\s*\}", rd):
        fails.append("6 reader: DefName does not return `defName` after Resolve()")
    if not re.search(r"public\s+static\s+bool\s+FixedSun\s*\{\s*get\s*\{\s*Resolve\(\)\s*;\s*return\s+loaded\s*&&\s*fixedSun\s*;\s*\}\s*\}", rd):
        fails.append("6 reader: FixedSun does not return the def's stored fixedSun (loaded && fixedSun)")
    if not re.search(r"(?m)^\s*loaded\s*=\s*true\s*;", res):
        fails.append("6 reader: Resolve never sets loaded = true, so the def's point is never used")
    for sig, label in ((r"public\s+static\s+void\s+SubstellarPoint\(\s*float\s+fallbackLat\s*,\s*float\s+fallbackLon\s*,\s*out\s+float\s+lat\s*,\s*out\s+float\s+lon\s*\)", "SubstellarPoint(float fallbackLat, float fallbackLon, out float lat, out float lon)"),
                       (r"public\s+static\s+bool\s+TrySunAt\(\s*PlanetTile\s+tile\s*,\s*float\s+fallbackLat\s*,\s*float\s+fallbackLon\s*,\s*out\s+float\s+elevationDeg\s*,\s*out\s+float\s+bearingDeg\s*\)", "TrySunAt(PlanetTile tile, float fallbackLat, float fallbackLon, out float elevationDeg, out float bearingDeg)")):
        if not re.search(sig, rd):
            fails.append(f"6 reader: signature is not `{label}` (callers bind by position)")
    sp = method_body(rd, "SubstellarPoint")
    want = (r"^\{\s*Resolve\(\)\s*;\s*if\s*\(\s*loaded\s*\)\s*\{\s*lat\s*=\s*substellarLat\s*;\s*lon\s*=\s*substellarLon\s*;\s*\}"
            r"\s*else\s*\{\s*lat\s*=\s*fallbackLat\s*;\s*lon\s*=\s*fallbackLon\s*;\s*\}\s*\}$")
    if sp is None or not re.search(want, sp):
        fails.append("6 reader: SubstellarPoint does not return the def's substellarLat/Lon when loaded (fallback only otherwise)")
    ts = method_body(rd, "TrySunAt")
    if ts is None:
        fails.append("6 reader: TrySunAt not found")
    else:
        head = re.match(r"\{\s*elevationDeg\s*=\s*float\.NaN\s*;\s*bearingDeg\s*=\s*float\.NaN\s*;\s*"
                        r"if\s*\(\s*Find\.WorldGrid\s*==\s*null\s*\|\|\s*!\s*tile\.Valid\s*\)\s*\{\s*return\s+false\s*;\s*\}\s*"
                        r"Vector2\s+longLat\s*=\s*Find\.WorldGrid\.LongLatOf\(\s*tile\s*\)\s*;\s*SubstellarPoint\(", ts)
        if not head:
            fails.append("6 reader: TrySunAt's opening is not NaN outputs, `if (Find.WorldGrid == null || !tile.Valid) return false;`, LongLatOf(tile), then SubstellarPoint")
        m = re.search(r"SubstellarPoint\(\s*fallbackLat\s*,\s*fallbackLon\s*,\s*out\s+float\s+(\w+)\s*,\s*out\s+float\s+(\w+)\s*\)\s*;", ts)
        if not m:
            fails.append("6 reader: TrySunAt does not take the point from SubstellarPoint(fallbackLat, fallbackLon, out lat, out lon)")
        else:
            a, b = m.group(1), m.group(2)
            g = re.search(r"SunGeometry\(\s*longLat\.y\s*,\s*longLat\.x\s*,\s*" + a + r"\s*,\s*" + b
                          + r"\s*,\s*out\s+bearingDeg\s*,\s*out\s+float\s+(\w+)\s*\)", ts[m.end():])
            if not g:
                fails.append("6 reader: TrySunAt does not hand SubstellarPoint's lat/lon to SunGeometry for the bearing")
            elif re.search(r"\b(?:" + a + "|" + b + r")\s*(?:[-+*/]?=(?!=)|\+\+|--)", ts[m.end():m.end() + g.start()]):
                fails.append("6 reader: TrySunAt overwrites SubstellarPoint's lat/lon before SunGeometry uses them")
            else:
                after = ts[m.end() + g.end():]
                e = re.search(r"elevationDeg\s*=\s*90f\s*-\s*" + g.group(1) + r"\s*;", after)
                if not e:
                    fails.append("6 reader: TrySunAt does not derive E = 90 - arc from that SunGeometry call")
                elif re.search(r"\b" + g.group(1) + r"\s*(?:[-+*/]?=(?!=)|\+\+|--)", after[:e.start()]):
                    fails.append("6 reader: TrySunAt alters the arc between SunGeometry and E")
                if not re.match(r"\s*;\s*elevationDeg\s*=\s*90f\s*-\s*" + g.group(1) + r"\s*;\s*return\s+true\s*;\s*\}$", after):
                    fails.append("6 reader: TrySunAt does more than E = 90 - arc between SunGeometry and return true (outputs may be altered)")
                if not (e and re.match(r"\s*return\s+true\s*;\s*\}$", after[e.end():])):
                    fails.append("6 reader: TrySunAt does not return true right after deriving E")
                if re.search(r"\b(?:bearingDeg|elevationDeg)\s*(?:[-+*/]?=(?!=)|\+\+|--)", after[e.end():] if e else ""):
                    fails.append("6 reader: TrySunAt alters the bearing or E after deriving them")
    return fails


def load():
    geo = [read(p) for p in sorted(glob.glob(os.path.join(GEO_DIR, "**", "*.xml"), recursive=True))
           if "PlanetGeometryDef" in read(p)]
    return {"ws": read(WS), "geo": geo, "reader": read(READER), "csproj": read(CSPROJ),
            "shade": read(SHADE), "pinned": read(PINNED), "world": read(WORLD)}


PLANTS = [
    ("field removed", "ws", "public bool fixedSun;", "public float fixedSunX;", "1 ws"),
    ("field commented out", "ws", "public bool fixedSun;", "// public bool fixedSun;", "1 ws"),
    ("reader store commented out", "reader", "substellarLat = (float)fLat.GetValue(d);", "/* substellarLat = (float)fLat.GetValue(d); */", "6 reader"),
    ("field defaults true", "ws", "public bool fixedSun;", "public bool fixedSun = true;", "defaults to true"),
    ("field defaults true in parentheses", "ws", "public bool fixedSun;", "public bool fixedSun = (true);", "defaults to true"),
    ("constructor sets fixedSun", "ws", "public bool fixedSun;", "public bool fixedSun;\n        public PlanetGeometryDef() { fixedSun = true; }", "1 ws: PlanetGeometryDef assigns fixedSun"),
    ("Ash'karr def made abstract", "geo", "<RimMandrake.StarWars.WeatherSuite.PlanetGeometryDef>", '<RimMandrake.StarWars.WeatherSuite.PlanetGeometryDef Abstract="True">', "2 geo: RUT_WS_AshkarrGeometry is Abstract"),
    ("Ash'karr sun moves", "geo", "<fixedSun>true</fixedSun>", "<fixedSun>false</fixedSun>", "2 geo"),
    ("Ash'karr omits fixedSun", "geo", "<fixedSun>true</fixedSun>", "", "2 geo"),
    ("latitude becomes double", "ws", "public float substellarLat", "public double substellarLat", "3 ws: PlanetGeometryDef.substellarLat"),
    ("type name drifts", "reader", '"RimMandrake.StarWars.WeatherSuite.PlanetGeometryDef"', '"RimMandrake.WeatherSuite.PlanetGeometryDef"', "3 reader"),
    ("reflected field renamed", "reader", 'AccessTools.Field(geo, "fixedSun")', 'AccessTools.Field(geo, "sunFixed")', "3 reader"),
    ("not compiled", "csproj", '<Compile Include="RM_PlanetSunGeometry.cs" />', "", "4 csproj"),
    ("compile entry commented out", "csproj", '<Compile Include="RM_PlanetSunGeometry.cs" />', '<!-- <Compile Include="RM_PlanetSunGeometry.cs" /> -->', "4 csproj"),
    ("shade grid bypasses the provider", "shade", "RM_PlanetSunGeometry.TrySunAt(", "RM_PlanetSunGeometry.TrySunAtX(", "5 shade"),
    ("pinned sky reads its own point", "pinned", "RM_PlanetSunGeometry.TrySunAt(map.Tile,",
     "SunGeometry(0f, 0f, ext.substellarLatitude, ext.substellarLongitude, out _, out _); RM_PlanetSunGeometry.TrySunAt(map.Tile,", "5 pinned"),
    ("SubstellarPoint ignores the def", "reader", "if (loaded)", "if (false)", "6 reader: SubstellarPoint"),
    ("SubstellarPoint inverted", "reader", "if (loaded)", "if (!loaded)", "6 reader: SubstellarPoint"),
    ("SubstellarPoint swaps lat/lon", "reader", "lat = substellarLat;", "lat = substellarLon;", "6 reader: SubstellarPoint"),
    ("Resolve never marks loaded", "reader", "loaded = true;", "loaded = false;", "6 reader: Resolve never"),
    ("Resolve stores the wrong value", "reader", "substellarLat = (float)fLat.GetValue(d);", "substellarLat = 0f;", "6 reader: Resolve does not store"),
    ("Resolve shadows the latitude", "reader", "substellarLat = (float)fLat.GetValue(d);", "float substellarLat = (float)fLat.GetValue(d);", "6 reader: Resolve does not store"),
    ("Resolve shadows loaded", "reader", "loaded = true;", "bool loaded = true;", "6 reader: Resolve never"),
    ("Resolve shadows the latitude, split", "reader", "substellarLat = (float)fLat.GetValue(d);", "float substellarLat; substellarLat = (float)fLat.GetValue(d);", "6 reader: Resolve declares a local"),
    ("Resolve shadows loaded, split", "reader", "                    loaded = true;", "                    bool loaded;\n                    loaded = true;", "6 reader: Resolve declares a local"),
    ("Resolve shadows the latitude, second declarator", "reader", "substellarLat = (float)fLat.GetValue(d);", "float unused, substellarLat; substellarLat = (float)fLat.GetValue(d);", "6 reader: Resolve declares a local"),
    ("TrySunAt overwrites the point", "reader", "SubstellarPoint(fallbackLat, fallbackLon, out float lat, out float lon);",
     "SubstellarPoint(fallbackLat, fallbackLon, out float lat, out float lon); lat = fallbackLat; lon = fallbackLon;", "6 reader: TrySunAt overwrites"),
    ("Resolve shadows fixedSun", "reader", "fixedSun = fFixed != null", "bool fixedSun = fFixed != null", "6 reader: Resolve declares a local"),
    ("Resolve drops fixedSun", "reader", "fixedSun = fFixed != null && (bool)fFixed.GetValue(d);", "fixedSun = false;", "6 reader: Resolve does not store the def's fixedSun"),
    ("FixedSun getter ignores the def", "reader", "return loaded && fixedSun;", "return false;", "6 reader: FixedSun does not"),
    ("Resolve binds the wrong field", "reader", 'AccessTools.Field(geo, "substellarLat")', 'AccessTools.Field(geo, "substellarLon")', "6 reader: Resolve does not bind"),
    ("TrySunAt skips SubstellarPoint", "reader", "SubstellarPoint(fallbackLat, fallbackLon, out float lat, out float lon);",
     "float lat = fallbackLat, lon = fallbackLon;", "6 reader: TrySunAt does not take"),
    ("TrySunAt feeds the fallback to SunGeometry", "reader", "SunGeometry(longLat.y, longLat.x, lat, lon,",
     "SunGeometry(longLat.y, longLat.x, fallbackLat, fallbackLon,", "6 reader: TrySunAt does not hand"),
    ("TrySunAt E ignores the arc", "reader", "elevationDeg = 90f - arcDeg;", "elevationDeg = 90f;", "6 reader: TrySunAt does not derive"),
    ("TrySunAt clamps the arc", "reader", "elevationDeg = 90f - arcDeg;", "arcDeg = Mathf.Min(90f, arcDeg); elevationDeg = 90f - arcDeg;", "6 reader: TrySunAt alters the arc"),
    ("TrySunAt rewrites the bearing", "reader", "elevationDeg = 90f - arcDeg;", "elevationDeg = 90f - arcDeg; bearingDeg = 0f;", "6 reader: TrySunAt alters the bearing"),
    ("Resolve guard inverted", "reader", "if (resolved)", "if (!resolved)", "6 reader: Resolve does not open"),
    ("TrySunAt reports failure", "reader", "elevationDeg = 90f - arcDeg;\n            return true;", "elevationDeg = 90f - arcDeg;\n            return false;", "6 reader: TrySunAt does not return true"),
    ("TrySunAt folds the bearing", "reader", "elevationDeg = 90f - arcDeg;", "bearingDeg = Mathf.Repeat(bearingDeg, 180f); elevationDeg = 90f - arcDeg;", "6 reader: TrySunAt does more than"),
    ("type guard inverted", "reader", "if (geo == null)", "if (geo != null)", "6 reader: Resolve's type lookup guard"),
    ("field guard inverted", "reader", "if (fLat == null || fLon == null)", "if (fLat != null || fLon != null)", "6 reader: Resolve's missing-field guard"),
    ("def loop dropped", "reader", "GenDefDatabase.GetAllDefsInDatabaseForDef(geo)", "new Def[0]", "6 reader: Resolve's def loop"),
    ("TrySunAt validity guard inverted", "reader", "|| !tile.Valid)", "|| tile.Valid)", "6 reader: TrySunAt's opening"),
    ("TrySunAt reads the wrong tile", "reader", "LongLatOf(tile)", "LongLatOf(PlanetTile.Invalid)", "6 reader: TrySunAt's opening"),
    ("shade grid swaps E and bearing", "shade", "out float rawElev, out float bearingDeg)", "out float bearingDeg, out float rawElev)", "5 shade: ResolveSun's TrySunAt call"),
    ("pinned sky swaps E and bearing", "pinned", "out float rawElev, out float bearingDeg)", "out float bearingDeg, out float rawElev)", "5 pinned: ResolveGeometry's TrySunAt call"),
    ("world sun swaps lat and lon", "world", "SubstellarPoint(0f, 0f, out lat, out lon)", "SubstellarPoint(0f, 0f, out lon, out lat)", "5 world: PinnedDirection does not take"),
    ("Loaded reports resolved", "reader", "Resolve(); return loaded; }", "Resolve(); return resolved; }", "6 reader: Loaded does not"),
    ("reader born resolved", "reader", "private static bool resolved;", "private static bool resolved = true;", "6 reader: static `resolved`"),
    ("world direction swaps lat and lon", "world", "SubstellarDirection(lat, lon,", "SubstellarDirection(lon, lat,", "5 world: PinnedDirection does not hand"),
    ("TrySunAt signature swaps outputs", "reader", "out float elevationDeg, out float bearingDeg)", "out float bearingDeg, out float elevationDeg)", "6 reader: signature is not `TrySunAt"),
    ("SubstellarPoint signature swaps fallbacks", "reader", "float fallbackLat, float fallbackLon, out float lat", "float fallbackLon, float fallbackLat, out float lat", "6 reader: signature is not `SubstellarPoint"),
    ("world direction swaps axes", "world", "pinned = new Vector3(x, y, z);", "pinned = new Vector3(z, y, x);", "5 world: PinnedDirection does not hand"),
    ("world cache guard inverted", "world", "if (pinned.HasValue)", "if (!pinned.HasValue)", "5 world: PinnedDirection does not open"),
    ("world fallback not exclusive", "world", "                else\n                {\n                    foreach (BiomeDef", "                {\n                    foreach (BiomeDef", "5 world: PinnedDirection does not take"),
    ("world cache born full", "world", "private static Vector3? pinned;", "private static Vector3? pinned = Vector3.zero;", "5 world: the cache is not declared"),
    ("world cache overwritten", "world", "pinned = new Vector3(x, y, z);", "pinned = new Vector3(x, y, z); pinned = Vector3.zero;", "5 world: `pinned` is assigned"),
    ("loaded reset after the read", "reader", "                if (loaded && fFixed == null)", "                loaded = false;\n                if (loaded && fFixed == null)", "6 reader: static `loaded` is written"),
    ("catch no longer resets loaded", "reader", "                loaded = false;\n                Log.Warning", "                Log.Warning", "6 reader: `loaded = false;` is not"),
    ("world point zeroed before conversion", "world", "            RM_WorldStarsMath.SubstellarDirection(", "            lat = lon = 0f;\n            RM_WorldStarsMath.SubstellarDirection(", "5 world: something runs between"),
    ("loaded set outside the loop", "reader", "                    loaded = true;\n                    break;\n                }", "                    break;\n                }\n                loaded = true;", "6 reader: Resolve's def loop"),
    ("world postfix flips the sun", "world", "__result = PinnedDirection();", "__result = -PinnedDirection();", "5 world: the world-sun postfix"),
    ("world direction negated", "world", "pinned = new Vector3(x, y, z);", "pinned = new Vector3(x, y, z); pinned *= -1f;", "5 world: `pinned` is assigned"),
    ("shade grid resets the bearing", "shade", "out float rawElev, out float bearingDeg))", "out float rawElev, out float bearingDeg)) { bearingDeg = 0f; } if (false)", "5 shade: ResolveSun overwrites"),
    ("pinned sky resets E", "pinned", "out float rawElev, out float bearingDeg))", "out float rawElev, out float bearingDeg)) { rawElev = 90f; } if (false)", "5 pinned: ResolveGeometry overwrites"),
    ("world postfix guard inverted", "world", "if (!RM_WorldStarsMath.PinsWorldSun(", "if (RM_WorldStarsMath.PinsWorldSun(", "5 world: the world-sun postfix"),
    ("world sun reflects again", "world", "if (RM_PlanetSunGeometry.Loaded)", "var t = GenTypes.GetTypeInAnyAssembly(\"x\"); if (RM_PlanetSunGeometry.Loaded)", "5 world"),
]


def main():
    files = load()
    bad = 0
    fails = check(files)
    for f in fails:
        print("FAIL real tree: " + f)
    bad += len(fails)
    if not fails:
        print("ok   real tree: fixedSun declared (bool, default false), Ash'karr sets it true, reader and 3 resolvers wired")
    for label, key, old, new, want in PLANTS:
        mutated = dict(files)
        if key == "geo":
            if not any(old in t for t in files["geo"]):
                print(f"FAIL plant {label}: pattern not found")
                bad += 1
                continue
            mutated["geo"] = [t.replace(old, new, 1) for t in files["geo"]]
        else:
            if old not in files[key]:
                print(f"FAIL plant {label}: pattern not found")
                bad += 1
                continue
            mutated[key] = files[key].replace(old, new, 1)
        hit = [f for f in check(mutated) if want in f]
        print(("ok   " if hit else "FAIL ") + f"plant {label}" + (f": {hit[0]}" if hit else ": not caught"))
        bad += not hit
    total = 1 + len(PLANTS)
    print(f"{'PASS' if not bad else 'FAIL'} selftest_planet_fixed_sun: {total - bad}/{total}")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
