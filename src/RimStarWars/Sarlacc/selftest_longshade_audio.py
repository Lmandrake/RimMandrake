#!/usr/bin/env python3
"""Offline first script for LONGSHADE_BEDAZZLE_MECHANICS_1's vanilla audio (owner ruling 2026-10-03).

Two sounds, each with a failure mode that logs nothing in game:
  * the swimmer's grinding (RSW_SwimmerRoad.cs): a sustainer that must be maintained every tick, gated on its
    setting and on the swimmer moving, naming a vanilla SoundDef that IS a sustainer;
  * the Crawler Road wrecks' ticking metal: vanilla CompAmbientSound maintains from CompTick, so a wreck left at
    tickerType Never spawns a sustainer that dies at once, silently.
audio_findings() is green on the shipped tree; each deliberate break turns it red.
Run: python3 src/RimStarWars/Sarlacc/selftest_longshade_audio.py
"""
import os
import re
import sys
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
VANILLA = "/mnt/c/Program Files (x86)/Steam/steamapps/common/RimWorld/Data"
INJ = os.path.join(ROOT, "src", "RimStarWars", "StructureInjectionsSW", "Defs")
FAILS = []


def rd(p):
    return open(p, encoding="utf-8").read()


def vanilla_sounddef(name):
    """(found, sustain, folder) for a vanilla SoundDef, or None when no install is visible (UNMEASURED)."""
    if not os.path.isdir(VANILLA):
        return None
    for dp, _, files in os.walk(VANILLA):
        if "SoundDefs" not in dp:
            continue
        for f in files:
            if not f.endswith(".xml"):
                continue
            t = rd(os.path.join(dp, f))
            if "<defName>%s</defName>" % name not in t:
                continue
            for sd in ET.fromstring(t).iter("SoundDef"):
                if sd.findtext("defName") == name:
                    return (True, (sd.findtext("sustain") or "").strip().lower() == "true",
                            (sd.findtext(".//clipFolderPath") or "").strip())
    return (False, False, "")


def audio_findings(road_cs=None, settings_cs=None, things_xml=None, sounds_xml=None):
    road_cs = road_cs if road_cs is not None else rd(os.path.join(HERE, "Source", "RSW_SwimmerRoad.cs"))
    settings_cs = settings_cs if settings_cs is not None else rd(os.path.join(HERE, "Source", "RSW_SarlaccSettings.cs"))
    things_xml = things_xml if things_xml is not None else rd(os.path.join(INJ, "ThingDefs_CrawlerRoad.xml"))
    sounds_xml = sounds_xml if sounds_xml is not None else rd(os.path.join(INJ, "SoundDefs_CrawlerRoad.xml"))
    bad = []
    tick = road_cs.split("public override void MapComponentTick()", 1)[-1].split("}", 1)[0]
    if "TickGrindSound();" not in tick:
        bad.append("grind: MapComponentTick never calls TickGrindSound (sustainer never maintained)")
    want = road_cs.split("public bool GrindWanted()", 1)[-1].split("}", 1)[0]
    if "swimmerGrindSoundEnabled" not in want or "pather.Moving" not in want:
        bad.append("grind: GrindWanted is not gated on swimmerGrindSoundEnabled AND the swimmer moving")
    m = re.search(r'GrindSoundDefName = "(\w+)"', road_cs)
    if not m:
        bad.append("grind: GrindSoundDefName not found")
    else:
        v = vanilla_sounddef(m.group(1))
        if v is not None and not v[0]:
            bad.append("grind: %s is not a vanilla SoundDef" % m.group(1))
        elif v is not None and not v[1]:
            bad.append("grind: %s is not a sustainer (TrySpawnSustainer would refuse it)" % m.group(1))
    if '"swimmerGrindSoundEnabled"' not in settings_cs or "ref swimmerGrindSoundEnabled" not in settings_cs.split("DoWindowContents", 1)[-1]:
        bad.append("grind: setting swimmerGrindSoundEnabled not Scribed or has no control")
    sounds = {sd.findtext("defName"): sd for sd in ET.fromstring(sounds_xml).iter("SoundDef")}
    tick_sd = sounds.get("RSW_WreckMetalTick")
    if tick_sd is None:
        bad.append("wreck: SoundDef RSW_WreckMetalTick missing")
    else:
        if (tick_sd.findtext("sustain") or "").strip().lower() != "true":
            bad.append("wreck: RSW_WreckMetalTick is not a sustainer (CompAmbientSound spawns a sustainer)")
        folder = (tick_sd.findtext(".//clipFolderPath") or "").strip()
        v = vanilla_sounddef("Tick_Tiny")
        if v is not None and folder != v[2]:
            bad.append("wreck: grain folder %r is not vanilla Tick_Tiny's own %r" % (folder, v[2]))
    things = {t.findtext("defName"): t for t in ET.fromstring(things_xml).iter("ThingDef")}
    for d in ("RSW_WreckedSkiff", "RSW_CrawlerTreadWreck"):
        t = things.get(d)
        if t is None:
            bad.append("wreck: %s missing" % d)
            continue
        comps = [li for li in t.iter("li") if li.get("Class") == "CompProperties_AmbientSound"]
        if not comps or (comps[0].findtext("sound") or "").strip() != "RSW_WreckMetalTick":
            bad.append("wreck: %s carries no CompAmbientSound naming RSW_WreckMetalTick" % d)
        if (t.findtext("tickerType") or "Never").strip() != "Normal":
            bad.append("wreck: %s tickerType is not Normal (CompAmbientSound maintains from CompTick: silent)" % d)
    return bad


def check(name, cond, detail=""):
    print("%s  %s %s" % ("ok  " if cond else "FAIL", name, "" if cond else detail))
    if not cond:
        FAILS.append(name)


if __name__ == "__main__":
    base = audio_findings()
    check("shipped tree green", base == [], "; ".join(base))
    R = rd(os.path.join(HERE, "Source", "RSW_SwimmerRoad.cs"))
    S = rd(os.path.join(HERE, "Source", "RSW_SarlaccSettings.cs"))
    T = rd(os.path.join(INJ, "ThingDefs_CrawlerRoad.xml"))
    D = rd(os.path.join(INJ, "SoundDefs_CrawlerRoad.xml"))
    check("sanity: wreck comp present twice", T.count("CompProperties_AmbientSound") == 2)

    def red(name, needle, **kw):
        f = audio_findings(**kw)
        check("break: " + name, any(needle in x for x in f), "findings=%r" % f)

    red("tick drops the call", "never calls", road_cs=R.replace("            TickGrindSound();\n", "", 1))
    red("gate ignores movement", "not gated", road_cs=R.replace("swimmer.pather.Moving", "true"))
    red("setting unscribed", "not Scribed", settings_cs=S.replace('"swimmerGrindSoundEnabled"', '"x"'))
    red("wreck ticker Never", "tickerType is not Normal", things_xml=T.replace("<tickerType>Normal</tickerType>", "<tickerType>Never</tickerType>", 1))
    red("wreck sound not a sustainer", "not a sustainer", sounds_xml=D.replace("<sustain>True</sustain>", "<sustain>False</sustain>"))
    if os.path.isdir(VANILLA):
        red("grind names a non-sustainer", "is not a sustainer", road_cs=R.replace('"FleshbeastDigging"', '"Tick_Tiny"'))
        red("grind names nothing vanilla", "not a vanilla SoundDef", road_cs=R.replace('"FleshbeastDigging"', '"RSW_Grind"'))
        red("wrong grain folder", "not vanilla Tick_Tiny", sounds_xml=D.replace("UI/TickTiny", "UI/TickLow"))
    else:
        print("UNMEASURED  vanilla SoundDef checks (no RimWorld install visible)")
    print("%d failure(s)" % len(FAILS))
    sys.exit(1 if FAILS else 0)
