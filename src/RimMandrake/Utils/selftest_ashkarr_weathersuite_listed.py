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
Lists are parsed as XML (never grepped; instrument_traps.md).
"""
import glob
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


def main():
    lb, seen = check_lists()
    bad = lb + check_about() + check_one_geometry()
    for b in bad:
        print("FAIL", b)
    print("%s: %d list(s) with the engine checked, %d failure(s)" % (os.path.basename(__file__), seen, len(bad)))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
