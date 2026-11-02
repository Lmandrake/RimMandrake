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


def check(files):
    """files: dict key -> text (geometry xml is a list of texts). Returns list of failure strings."""
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
    elif re.search(r"public\s+bool\s+fixedSun\s*=\s*true", cls.group(1)):
        fails.append("1 ws: fixedSun defaults to true; a def that omits it must mean a day/night world")

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
        if (d.findtext("fixedSun") or "").strip() != "true":
            fails.append(f"2 geo: {d.findtext('defName')} does not set <fixedSun>true</fixedSun> (Ash'karr's sun stands still)")

    rd = files["reader"]
    m = re.search(r'PlanetGeometryDefType\s*=\s*"([^"]+)"', rd)
    if not m or m.group(1) != full:
        fails.append(f"3 reader: PlanetGeometryDefType is {m.group(1) if m else None!r}, not {full!r}")
    reflected = re.findall(r'AccessTools\.Field\(\s*geo\s*,\s*"(\w+)"\s*\)', rd)
    if "fixedSun" not in reflected:
        fails.append("3 reader: RM_PlanetSunGeometry never reads fixedSun")
    for f in reflected:
        if f not in fields:
            fails.append(f"3 reader: reflects on field {f!r}, which PlanetGeometryDef does not declare")

    if '<Compile Include="RM_PlanetSunGeometry.cs" />' not in files["csproj"]:
        fails.append("4 csproj: RM_PlanetSunGeometry.cs is not compiled into CreatureBehaviors")

    for key, meth in (("shade", "ResolveSun"), ("pinned", "ResolveGeometry")):
        body = method_body(files[key], meth)
        if body is None:
            fails.append(f"5 {key}: method {meth} not found")
            continue
        if "RM_PlanetSunGeometry.TrySunAt(" not in body:
            fails.append(f"5 {key}: {meth} does not take E and the bearing from RM_PlanetSunGeometry.TrySunAt")
        if re.search(r"SunGeometry\([^;]*ext\.substellar", body):
            fails.append(f"5 {key}: {meth} still hands the biome extension's substellar point to SunGeometry")
    world = method_body(files["world"], "PinnedDirection")
    if world is None or "RM_PlanetSunGeometry." not in world:
        fails.append("5 world: PinnedDirection does not read RM_PlanetSunGeometry")
    elif "GetTypeInAnyAssembly" in world or "AccessTools.Field" in world:
        fails.append("5 world: PinnedDirection reflects on the geometry def itself (a second reader)")
    return fails


def load():
    geo = [read(p) for p in sorted(glob.glob(os.path.join(GEO_DIR, "**", "*.xml"), recursive=True))
           if "PlanetGeometryDef" in read(p)]
    return {"ws": read(WS), "geo": geo, "reader": read(READER), "csproj": read(CSPROJ),
            "shade": read(SHADE), "pinned": read(PINNED), "world": read(WORLD)}


PLANTS = [
    ("field removed", "ws", "public bool fixedSun;", "public float fixedSunX;", "1 ws"),
    ("field defaults true", "ws", "public bool fixedSun;", "public bool fixedSun = true;", "defaults to true"),
    ("Ash'karr sun moves", "geo", "<fixedSun>true</fixedSun>", "<fixedSun>false</fixedSun>", "2 geo"),
    ("Ash'karr omits fixedSun", "geo", "<fixedSun>true</fixedSun>", "", "2 geo"),
    ("type name drifts", "reader", '"RimMandrake.StarWars.WeatherSuite.PlanetGeometryDef"', '"RimMandrake.WeatherSuite.PlanetGeometryDef"', "3 reader"),
    ("reflected field renamed", "reader", 'AccessTools.Field(geo, "fixedSun")', 'AccessTools.Field(geo, "sunFixed")', "3 reader"),
    ("not compiled", "csproj", '<Compile Include="RM_PlanetSunGeometry.cs" />', "", "4 csproj"),
    ("shade grid bypasses the provider", "shade", "RM_PlanetSunGeometry.TrySunAt(", "RM_PlanetSunGeometry.TrySunAtX(", "5 shade"),
    ("pinned sky reads its own point", "pinned", "RM_PlanetSunGeometry.TrySunAt(map.Tile,",
     "SunGeometry(0f, 0f, ext.substellarLatitude, ext.substellarLongitude, out _, out _); RM_PlanetSunGeometry.TrySunAt(map.Tile,", "5 pinned"),
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
