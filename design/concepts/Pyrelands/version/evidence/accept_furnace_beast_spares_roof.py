#!/usr/bin/env python3
"""Acceptance test of RIMMANDRAKE_SPARE_PYRE_FURNACE_BARN_ROOF_FROM_TITAN_WAKE (Pyrelands in-game visit 7, 2026-11-23).

Reads the shipped defs and Huge Things source: with the shipped ladder, does the furnace-beast's own wake hole the thin roof
of the barn it heats? It does when its adult body size reaches tier T2 and nothing spares the roof. Two routes spare it:
  roof exemption (the route the item names): the race's RM_TitanicExtension says <sparesRoofs>true</sparesRoofs>, the
    extension class declares the field, and TitanicWakeProcessor.ProcessFootprint's roof call reads it;
  whole opt-out: <forceEnabled>false</forceEnabled> (also takes the beast out of the titan pool; see the item).
The live proof is P_furnace_room (Stage 6). PASS exit 0, FAIL exit 1, UNMEASURED exit 2 (a file or def cannot be read).
ACCEPT_ROOT names another tree to read (the plants)."""
import os, re, sys
import xml.etree.ElementTree as ET
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.environ.get("ACCEPT_ROOT") or os.path.normpath(os.path.join(HERE, *[".."] * 5))
HT = os.path.join(ROOT, "src", "RimMandrake", "HugeThings")


def text(*p):
    with open(os.path.join(HT, *p), encoding="utf-8-sig") as fh:
        return re.sub(r"//[^\n]*|/\*.*?\*/", "", fh.read(), flags=re.S)


def main():
    fauna = os.path.join(ROOT, "src", "RimMandrake", "Pyrelands", "Defs", "ThingDefs_Races", "RM_PyrelandsFauna.xml")
    race = [d for d in ET.parse(fauna).getroot() if d.findtext("defName") == "RM_FurnaceBeast"
            and d.find("race/baseBodySize") is not None][0]
    body = float(race.findtext("race/baseBodySize"))
    ladder = ET.parse(os.path.join(HT, "Defs", "TitanicTierDefs", "RM_TitanicTierDef.xml")).getroot()
    t2 = float(ladder.find(".//t2MinBodySize").text)
    ext = next((li for li in race.findall("modExtensions/li") if li.get("Class", "").endswith("RM_TitanicExtension")), None)

    def flag(name, want):
        return ext is not None and (ext.findtext(name) or "").strip().lower() == want
    if body < t2:
        return 0, "body size %g is under T2 (%g): its wake holes no roof" % (body, t2)
    if flag("forceEnabled", "false"):
        return 0, "whole opt-out (forceEnabled false): no wake"
    if not flag("sparesRoofs", "true"):
        return 1, "body size %g reaches T2 (%g) and the race names no roof exemption: its wake holes its own barn's roof" % (
            body, t2)
    decl = re.search(r"\bpublic\s+bool\s+sparesRoofs\b", text("Source", "Titanic", "Tiering", "RM_TitanicExtension.cs"))
    used = "sparesRoofs" in text("Source", "Titanic", "Wake", "TitanicWakeProcessor.cs")
    if not decl or not used:
        return 1, "the race says sparesRoofs, but %s" % ("RM_TitanicExtension declares no such field" if not decl else
                                                         "TitanicWakeProcessor never reads it")
    return 0, "T2 with a roof exemption that the wake reads"


try:
    rc, why = main()
except Exception as e:   # noqa: BLE001 - a file that cannot be read is not a verdict
    print("UNMEASURED: %r" % (e,)); sys.exit(2)
print("%s: %s" % ("PASS" if rc == 0 else "FAIL", why)); sys.exit(rc)
