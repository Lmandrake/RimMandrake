#!/usr/bin/env python3
"""selftest_ashkarr_weathersuite_listed -- mandrake.rut.weathersuite rides right behind its engine.

ASHKARR_WEATHER_INSTALL_THE_SLEEPING_STORMS (owner by card 2026-10-19, "Weather Suite mod inactive,
storms/aurora off - deliberate? -> Not deliberate, turn it on"). The engine (mandrake.rm.weathersuite)
gates its terminator storm, nightside aurora and geothermal nightside cutoff on
WeatherGeometryUtility.ActiveGeometry = the FIRST loaded PlanetGeometryDef. Only the Ash'karr wiring
mod (mandrake.rut.weathersuite) ships one, so without it every band check returns false.

Asserts, offline:
  1. ModsConfig.FULL.LATEST.xml (the owner's real list) and every *.RULED_* tier list that enables
     the engine also enable the wiring mod, at the index directly after the engine.
  2. The wiring mod's About.xml hard-depends on and loads after the engine.
  3. Exactly one PlanetGeometryDef ships in src/ (ActiveGeometry takes FirstOrDefault).
  4. The live A1 readback (AshkarrWeatherSuite/validation.py) asks jawa/get_defs for the def by the
     class's FULL type name (a bare name resolves only in Verse/RimWorld: the 2026-11-03 live A1
     FAIL "No def TYPE named 'PlanetGeometryDef'"), and expects exactly the shipped XML's values.
Lists are parsed as XML (never grepped; instrument_traps.md).
"""
import ast
import glob
import re
import os
import sys
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
LISTS = os.path.join(REPO, "infrastructure", "state", "modlists")
ENGINE, WIRING = "mandrake.rm.weathersuite", "mandrake.rut.weathersuite"
ABOUT = os.path.join(REPO, "src", "RimUtinni", "AshkarrWeatherSuite", "About", "About.xml")


def active(path):
    return [(li.text or "").strip().lower() for li in ET.parse(path).getroot().find("activeMods").findall("li")]


def check_lists():
    bad, seen = [], 0
    paths = [os.path.join(LISTS, "ModsConfig.FULL.LATEST.xml")] + sorted(
        glob.glob(os.path.join(LISTS, "ModsConfig.*.RULED_*.xml")))
    for p in paths:
        mods = active(p)
        name = os.path.basename(p)
        if name == "ModsConfig.FULL.LATEST.xml" and ENGINE not in mods:
            bad.append("%s: the owner's list lacks the engine %s" % (name, ENGINE))
            continue
        if ENGINE not in mods:
            continue
        seen += 1
        i = mods.index(ENGINE)
        if WIRING not in mods:
            bad.append("%s: %s enabled at %d but %s absent" % (name, ENGINE, i, WIRING))
        elif mods.index(WIRING) != i + 1:
            bad.append("%s: %s at %d, %s at %d (want %d)" % (name, ENGINE, i, WIRING, mods.index(WIRING), i + 1))
    if seen < 2:  # sanity probe: the glob must see FULL.LATEST plus at least one tier list
        bad.append("only %d list(s) carrying the engine were read -- instrument blind?" % seen)
    return bad, seen


def check_about():
    root = ET.parse(ABOUT).getroot()
    bad = []
    if (root.findtext("packageId") or "").strip().lower() != WIRING:
        bad.append("About.xml packageId is not %s" % WIRING)
    deps = [(li.findtext("packageId") or "").strip().lower() for li in root.findall("modDependencies/li")]
    after = [(li.text or "").strip().lower() for li in root.findall("loadAfter/li")]
    if ENGINE not in deps:
        bad.append("About.xml modDependencies lacks %s" % ENGINE)
    if ENGINE not in after:
        bad.append("About.xml loadAfter lacks %s" % ENGINE)
    return bad


def check_one_geometry():
    found = []
    for p in glob.glob(os.path.join(REPO, "src", "**", "Defs", "**", "*.xml"), recursive=True):
        try:
            root = ET.parse(p).getroot()
        except ET.ParseError:
            continue
        for el in root:
            if isinstance(el.tag, str) and el.tag.endswith("PlanetGeometryDef") and el.get("Abstract") != "True":
                found.append("%s:%s" % (os.path.relpath(p, REPO), el.findtext("defName")))
    if len(found) != 1 or not found[0].endswith(":RUT_WS_AshkarrGeometry"):
        return ["want exactly one PlanetGeometryDef RUT_WS_AshkarrGeometry, found %r" % found]
    return []


VALIDATION = os.path.join(REPO, "src", "RimUtinni", "AshkarrWeatherSuite", "validation.py")
HOOK_CS = os.path.join(REPO, "src", "RimMandrake", "WeatherSuite", "Source", "WeatherSuiteHook.cs")
GEOMETRY_XML = os.path.join(REPO, "src", "RimUtinni", "AshkarrWeatherSuite", "Defs",
                            "WeatherGeometryDefs", "WeatherGeometryDefs_Ashkarr.xml")


def _module_literals(path, names):
    out = {}
    for node in ast.parse(open(path, encoding="utf-8").read()).body:
        if isinstance(node, ast.Assign) and len(node.targets) == 1 and isinstance(node.targets[0], ast.Name):
            if node.targets[0].id in names:
                out[node.targets[0].id] = ast.literal_eval(node.value)
    return out


def check_readback_matches():
    bad = []
    lit = _module_literals(VALIDATION, {"GEOMETRY_TYPE", "GEOMETRY_EXPECT", "GEOMETRY_DEF"})
    src = open(HOOK_CS, encoding="utf-8").read()
    ns = re.search(r"^\s*namespace\s+([\w.]+)", src, re.M)
    if not ns or not re.search(r"\bclass\s+PlanetGeometryDef\s*:\s*Def\b", src):
        return ["cannot read namespace/class PlanetGeometryDef from %s" % os.path.relpath(HOOK_CS, REPO)]
    full = ns.group(1) + ".PlanetGeometryDef"
    if lit.get("GEOMETRY_TYPE") != full:
        bad.append("validation.py GEOMETRY_TYPE %r is not the class's full name %r"
                   % (lit.get("GEOMETRY_TYPE"), full))
    if re.search(r"defs\s*=\s*[\"']PlanetGeometryDef/", open(VALIDATION, encoding="utf-8").read()):
        bad.append("validation.py still asks jawa/get_defs for the bare 'PlanetGeometryDef/' type")
    el = next((e for e in ET.parse(GEOMETRY_XML).getroot() if isinstance(e.tag, str)
               and e.tag.endswith("PlanetGeometryDef")), None)
    if el is None:
        return bad + ["no PlanetGeometryDef in %s" % os.path.relpath(GEOMETRY_XML, REPO)]
    if el.tag != full:
        bad.append("XML element %r is not the class's full name %r" % (el.tag, full))
    if lit.get("GEOMETRY_DEF") != el.findtext("defName"):
        bad.append("GEOMETRY_DEF %r != XML defName %r" % (lit.get("GEOMETRY_DEF"), el.findtext("defName")))
    shipped = {c.tag: (c.text or "").strip() for c in el if c.tag != "defName"}
    expect = lit.get("GEOMETRY_EXPECT") or {}
    if set(shipped) != set(expect):
        bad.append("GEOMETRY_EXPECT fields %r != shipped XML fields %r" % (sorted(expect), sorted(shipped)))
    for k, v in expect.items():
        x = shipped.get(k)
        ok = (x is not None and (x.lower() == str(v).lower() if isinstance(v, bool)
                                 else float(x) == float(v)))
        if not ok:
            bad.append("GEOMETRY_EXPECT[%s]=%r but the XML ships %r" % (k, v, x))
    return bad


def main():
    lb, seen = check_lists()
    bad = lb + check_about() + check_one_geometry() + check_readback_matches()
    for b in bad:
        print("FAIL", b)
    print("%s: %d list(s) with the engine checked, %d failure(s)" % (os.path.basename(__file__), seen, len(bad)))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
