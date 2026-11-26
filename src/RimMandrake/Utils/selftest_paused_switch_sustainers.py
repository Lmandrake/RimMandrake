#!/usr/bin/env python3
"""SOUNDSCAPE_PAUSED_SWITCH_FIX_HUM_LEAKS offline check: no on-camera soundscape plays over another map after a map switch
made while the game is paused.

Why (decompiled 1.6, read through RimSage 2026-11-26): an OnCamera sustainer has no map (Sample.Map is null, so
SoundDefHelper.CorrectContextNow never mutes it for being on the wrong map), and a PerTick sustainer ends only when
TicksGame passes its last Maintain() (Sustainer.SustainerUpdate), which never happens while paused. MapComponentTick does
not run while paused, but Map.MapUpdate calls MapComponentUpdate on every map every frame, paused or not. So each such
soundscape either ends its sustainers in MapComponentUpdate when its map is not the current map (the RustCathedral hum's
fix, RM_MapComponent_BiomeAttitude.cs), or its every subSound is muteWhenPaused (Sample.Volume is 0 while paused, and the
first tick after unpause ends it through the tick gate).

Each check is shown red on a planted fault (the fix removed, the mute flag cleared) in the same run.

    python3 src/RimMandrake/Utils/selftest_paused_switch_sustainers.py
"""
import os
import re
import sys
import xml.etree.ElementTree as ET

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
SRC = os.path.join(ROOT, "src", "RimMandrake")

# (file, the method that ends every sustainer of the component)
UPDATE_ENDS = [
    (os.path.join(SRC, "CreatureBehaviors", "Source", "RM_HeatSoundscape.cs"), "End"),
    (os.path.join(SRC, "CreatureBehaviors", "Source", "RM_MapComponent_ProximitySoundscape.cs"), "EndAll"),
]
# (SoundDefs file, sustainer defName): sustainers whose owner gates the map only in tick code and that rely on the mute.
MUTED = [
    (os.path.join(SRC, "TheForge", "Defs", "SoundDefs", "RM_ForgeVoices.xml"), "RM_ForgeVoice_StillThrob"),
    (os.path.join(SRC, "TheForge", "Defs", "SoundDefs", "RM_ForgeVoices.xml"), "RM_ForgeVoice_RainHiss"),
    (os.path.join(SRC, "Wastes", "Defs", "SoundDefs", "RM_WastesSounds.xml"), "RM_Storm_CinderwireWhine"),
]


def method_body(src, signature_re):
    """The brace-matched body of the first method matching signature_re, or None."""
    m = re.search(signature_re, src)
    if not m:
        return None
    i = src.find("{", m.end())
    if i < 0:
        return None
    depth = 0
    for j in range(i, len(src)):
        if src[j] == "{":
            depth += 1
        elif src[j] == "}":
            depth -= 1
            if depth == 0:
                return src[i + 1:j]
    return None


def update_finding(src, end_method):
    """None when MapComponentUpdate ends every sustainer once the map is not the current map; else what is wrong."""
    body = method_body(src, r"public\s+override\s+void\s+MapComponentUpdate\s*\(\s*\)")
    if body is None:
        return "no MapComponentUpdate override (the tick-only map gate never runs while paused)"
    if not re.search(r"Find\.CurrentMap\s*!=\s*map|map\s*!=\s*Find\.CurrentMap", body):
        return "MapComponentUpdate does not test Find.CurrentMap != map"
    if not re.search(r"\b%s\s*\(\s*\)\s*;" % re.escape(end_method), body):
        return "MapComponentUpdate does not call %s()" % end_method
    return None


def muted_finding(xml_text, def_name):
    """None when every subSound of the SoundDef is muteWhenPaused; else what is wrong."""
    root = ET.fromstring(xml_text)
    defs = [d for d in root.iter("SoundDef") if (d.findtext("defName") or "").strip() == def_name]
    if len(defs) != 1:
        return "SoundDef %s found %d times" % (def_name, len(defs))
    subs = defs[0].findall("subSounds/li")
    if not subs:
        return "SoundDef %s has no subSounds" % def_name
    for k, li in enumerate(subs):
        if (li.findtext("muteWhenPaused") or "").strip().lower() != "true":
            return "SoundDef %s subSound %d is not muteWhenPaused" % (def_name, k)
    return None


def main():
    bad = 0

    def report(name, finding):
        nonlocal bad
        if finding:
            bad += 1
            print("FAIL %s: %s" % (name, finding))
        else:
            print("ok   %s" % name)

    for path, end in UPDATE_ENDS:
        name = os.path.basename(path)
        src = open(path, encoding="utf-8").read()
        report("%s ends its sustainers per frame off the current map" % name, update_finding(src, end))
        planted = re.sub(r"public\s+override\s+void\s+MapComponentUpdate", "public void NotMapComponentUpdate", src)
        report("%s planted fault (update removed) is caught" % name,
               None if update_finding(planted, end) else "the check stayed green with the update removed")

    for path, def_name in MUTED:
        text = open(path, encoding="utf-8").read()
        report("%s is muteWhenPaused" % def_name, muted_finding(text, def_name))
        planted = re.sub(r"<muteWhenPaused>\s*True\s*</muteWhenPaused>", "<muteWhenPaused>False</muteWhenPaused>", text,
                         flags=re.I)
        report("%s planted fault (mute cleared) is caught" % def_name,
               None if muted_finding(planted, def_name) else "the check stayed green with the mute cleared")

    total = 2 * (len(UPDATE_ENDS) + len(MUTED))
    print("paused switch sustainers selftest: %d/%d ok" % (total - bad, total))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
