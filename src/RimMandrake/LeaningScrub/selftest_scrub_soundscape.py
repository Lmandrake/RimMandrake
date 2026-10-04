#!/usr/bin/env python3
"""Offline first script for LEANINGSCRUB_MECHANICS_BUILD_1 part 7 (the soundscape; vanilla beds, owner 2026-10-03).

The ruled shape: a rich bed of bugs on the wind, and the Stall goes quiet BECAUSE the wind does. So: every scrub
weather that blows carries an insect bed; the Stall carries no ambient sound; the biome itself carries no
soundsAmbient (a biome bed would keep playing through the Stall); every named SoundDef is a vanilla one.
Run: python3 src/RimMandrake/LeaningScrub/selftest_scrub_soundscape.py
"""
import os
import sys
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
WEATHER = os.path.join(HERE, "Defs", "WeatherDefs", "RM_LeaningScrub_Weather.xml")
BIOME = os.path.join(HERE, "Defs", "BiomeDefs", "RM_LeaningScrub_Biome.xml")
VANILLA = "/mnt/c/Program Files (x86)/Steam/steamapps/common/RimWorld/Data"
INSECTS = {"Ambient_DayInsects_Jungle", "Ambient_NightInsects_Jungle", "Ambient_NightInsects_Standard"}
FAILS = []


def findings(weather_xml, biome_xml, vanilla_names=None):
    bad = []
    ws = {w.findtext("defName"): [li.text.strip() for li in w.findall("ambientSounds/li")]
          for w in ET.fromstring(weather_xml).iter("WeatherDef")}
    if "RM_Stall" not in ws:
        bad.append("RM_Stall missing")
    elif ws["RM_Stall"]:
        bad.append("the Stall carries ambient sound %s: it must go quiet" % ws["RM_Stall"])
    for w in ("RM_ScrubWind", "RM_ScrubWindFog"):
        if not INSECTS & set(ws.get(w, [])):
            bad.append("%s carries no insect bed (the rich soundscape rides the wind)" % w)
    for b in ET.fromstring(biome_xml).iter("BiomeDef"):
        if b.find("soundsAmbient") is not None and len(b.find("soundsAmbient")):
            bad.append("biome %s has soundsAmbient: it would keep playing through the Stall" % b.findtext("defName"))
    if vanilla_names is not None:
        for w, names in ws.items():
            for n in names:
                if n not in vanilla_names:
                    bad.append("%s names %s, not a vanilla SoundDef" % (w, n))
    return bad


def vanilla_names():
    if not os.path.isdir(VANILLA):
        return None
    out = set()
    for dp, _, files in os.walk(VANILLA):
        if "SoundDefs" in dp:
            for f in files:
                if f.endswith(".xml"):
                    for sd in ET.parse(os.path.join(dp, f)).getroot().iter("SoundDef"):
                        out.add(sd.findtext("defName"))
    return out


def check(name, cond, detail=""):
    print("%s  %s %s" % ("ok  " if cond else "FAIL", name, "" if cond else detail))
    if not cond:
        FAILS.append(name)


W, B, V = open(WEATHER, encoding="utf-8").read(), open(BIOME, encoding="utf-8").read(), vanilla_names()
check("shipped green", findings(W, B, V) == [], findings(W, B, V))
if V is None:
    print("UNMEASURED  vanilla-name check (no install visible)")
else:
    check("sanity: vanilla set sees Ambient_Wind_Clear", "Ambient_Wind_Clear" in V)
    check("break: non-vanilla bed", any("not a vanilla" in f for f in findings(W.replace("Ambient_DayInsects_Jungle", "RM_Tikkit"), B, V)))


def red(name, needle, w=W, b=B):
    f = findings(w, b)
    check("break: " + name, any(needle in x for x in f), f)


red("Stall gets a bed", "must go quiet", w=W.replace("<windSpeedFactor>0</windSpeedFactor>",
    "<windSpeedFactor>0</windSpeedFactor><ambientSounds><li>Ambient_Wind_Clear</li></ambientSounds>", 1))
red("wind loses its insects", "RM_ScrubWind carries no insect bed",
    w=W.replace("<li>Ambient_Wind_Clear</li>\n      <!--", "<li>Ambient_Wind_Clear</li>\n      <!-- x", 1).replace(
        "      <li>Ambient_DayInsects_Jungle</li>\n      <li>Ambient_NightInsects_Jungle</li>\n", "", 1))
red("biome-wide bed", "would keep playing", b=B.replace("<BiomeDef>", "<BiomeDef><soundsAmbient><li>Ambient_DayInsects_Jungle</li></soundsAmbient>", 1))
print("%d failure(s)" % len(FAILS))
sys.exit(1 if FAILS else 0)
