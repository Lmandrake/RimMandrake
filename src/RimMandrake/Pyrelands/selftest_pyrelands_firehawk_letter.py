#!/usr/bin/env python3
"""Offline selftest for the first of the fire-hawk's two hunt rewards, the letter (owner, 2026-11-13: "That gives a great reason for players to hunt the
Firehawk."; "It is ok that they are common. That is the threat.").

  RIMMANDRAKE_ANNOUNCE_FIREHAWK_EMBER_LETTER_ON_FIRST_SIGHTING   the once-per-game letter (FireHawkRewards.cs)
  RIMMANDRAKE_ADD_PRISTINE_EMBERHAWK_CRESTFEATHER_HUNT_TROPHY    the crestfeather trophy (RM_PristineFirehawkCrestfeather.xml)
  (the second id keeps its filed spelling; the owner corrected the name to Firehawk, so that word appears nowhere in the mod)

Static half (this file): the letter's keyed strings exist for every key the code translates, the Mod Settings toggle exists,
ships ON, is saved, is drawn and is greyed under the hawk's master, and the component feeds it (and the once-only flag it saves)
to the kernel gate; the trophy def exists with its label, Beauty, MarketValue above the hawk's, a small stack and a marked
placeholder texture; the hawk's race carries the butcher-trophy extension at 35 %; the postfix that rolls it is on
Pawn.ButcherProducts and asks the kernel; the art is queued. The gate's logic itself (once only, toggle off = no letter, the
flat chance) is the fuzz family `rewards` (Source/SelfTest/Fuzz/FireHawkRewardsFuzz.cs, selftest_pyrelands_fuzz.py).
Live half: Pyrelands/firehawk_rewards_live_proof.py. Run: python3 <this file>
"""
import os
import re
import sys
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "Source")
KEYED = os.path.join(HERE, "Languages", "English", "Keyed", "Pyrelands.xml")
FAUNA = os.path.join(HERE, "Defs", "ThingDefs_Races", "RM_PyrelandsFauna.xml")
TROPHY_XML = os.path.join(HERE, "Defs", "ThingDefs_Items", "RM_PristineFirehawkCrestfeather.xml")
CODE = os.path.join(SRC, "FireHawkRewards.cs")
KERNEL = os.path.join(SRC, "Kernel", "RM_FireHawkRewardsKernel.cs")
SETTINGS = os.path.join(SRC, "RM_PyrelandsMod.cs")
COMP = os.path.join(SRC, "CompFireHawkSpread.cs")
ART_LIST = os.path.join(HERE, "..", "..", "..", "infrastructure", "artpipe", "art_lists",
                        "pyrelands_firehawk_crestfeather_2026-11-13.csv")
TROPHY = "RM_PristineFirehawkCrestfeather"
LABEL = "pristine firehawk crestfeather"
CHANCE = 0.35
SETTING = "fireHawkSightingLetterEnabled"
LETTER_KEYS = ("RM_FireHawkSightedLabel", "RM_FireHawkSightedText", "RM_FireHawkEmberFromPlant", "RM_FireHawkEmberFromBurn",
               "RM_FireHawkTargetPlant", "RM_FireHawkTargetGround")
COMPASS_KEYS = tuple("RM_Compass_" + d for d in ("N", "NE", "E", "SE", "S", "SW", "W", "NW"))


def _read(p):
    with open(p, encoding="utf-8") as fh:
        return fh.read()


def _def(root, name):
    for d in root.iter("ThingDef"):
        if d.findtext("defName") == name:
            return d
    return None


def check_letter(probs):
    if not os.path.exists(CODE):
        probs.append("letter: %s does not exist" % os.path.relpath(CODE, HERE))
        return
    code = _read(CODE)
    keyed = {e.tag: (e.text or "") for e in ET.parse(KEYED).getroot()}
    used = set(re.findall(r'"(RM_[A-Za-z_]+)"\s*\.Translate', code))
    for k in sorted(used | set(LETTER_KEYS) | set(COMPASS_KEYS)):
        if not keyed.get(k, "").strip():
            probs.append("letter: keyed string %s is missing or empty in Languages/English/Keyed/Pyrelands.xml" % k)
    missing_use = [k for k in LETTER_KEYS if k not in used]
    if missing_use:
        probs.append("letter: the code never translates %s" % ", ".join(missing_use))
    text = keyed.get("RM_FireHawkSightedText", "")
    for arg in ("{HAWK}", "{EMBER}", "{SOURCE_DIST}", "{SOURCE_DIR}", "{TARGET}", "{TARGET_DIST}", "{TARGET_DIR}"):
        if arg not in text:
            probs.append("letter: RM_FireHawkSightedText lacks %s (it describes the ember the hawk carries now)" % arg)
    for word in ("biggest stand of unburnt fuel", "bring"):
        if word not in text:
            probs.append("letter: RM_FireHawkSightedText does not say %r" % word)
    if "Emberhawk" in text or "emberhawk" in text.lower():
        probs.append("letter: the text says Emberhawk")
    # the gate: the component hands the kernel its saved flag, the setting, the mechanics master, carrying, home, fogged
    if not re.search(r"RM_FireHawkRewardsKernel\.TryClaimSighting\(\s*ref\s+announced\s*,\s*RM_PyrelandsSettings\." + SETTING, code):
        probs.append("letter: the component does not pass `ref announced` and RM_PyrelandsSettings.%s to TryClaimSighting" % SETTING)
    if "PyrelandsMechanicsGate.On" not in code:
        probs.append("letter: the component ignores the Pyrelands master (PyrelandsMechanicsGate.On)")
    if not re.search(r'Scribe_Values\.Look\(\s*ref\s+announced\s*,\s*"announced"\s*,\s*false\s*\)', code):
        probs.append("letter: the once-only flag is not saved (Scribe_Values.Look(ref announced, \"announced\", false))")
    if not re.search(r"class\s+\w+\s*:\s*GameComponent\b", code):
        probs.append("letter: the once-only flag does not live in a GameComponent (once per game)")
    if "LetterDefOf.ThreatSmall" not in code:
        probs.append("letter: not sent as LetterDefOf.ThreatSmall")
    if "IsPlayerHome" not in code or "Fogged(" not in code:
        probs.append("letter: no player-home or fog check in the component")
    if not os.path.exists(KERNEL) or "TryClaimSighting" not in _read(KERNEL):
        probs.append("letter: kernel %s has no TryClaimSighting" % os.path.relpath(KERNEL, HERE))
    if not re.search(r"internal\s+bool\s+CarryingEmber", _read(COMP)):
        probs.append("letter: CompFireHawkSpread.CarryingEmber is not internal (the one hook the letter reads)")
    st = _read(SETTINGS)
    if not re.search(r"public static bool %s\s*=\s*true;" % SETTING, st):
        probs.append("settings: %s is not a public static bool that ships true" % SETTING)
    if not re.search(r'Scribe_Values\.Look\(ref %s, "%s", true\)' % (SETTING, SETTING), st):
        probs.append("settings: %s is not saved with default true" % SETTING)
    if not re.search(r'\.Declare\("fireHawkSpreadEnabled",\s*"%s"\)' % SETTING, st):
        probs.append("settings: %s is not greyed under fireHawkSpreadEnabled (Masters.Declare)" % SETTING)
    if not re.search(r"CheckboxLabeled\([^;]*ref %s" % SETTING, st, re.S):
        probs.append("settings: %s is never drawn" % SETTING)


def main():
    probs = []
    check_letter(probs)
    print("selftest_pyrelands_firehawk_letter: %s" % ("FAIL" if probs else "PASS"))
    for p in probs:
        print("  - " + p)
    return 1 if probs else 0


if __name__ == "__main__":
    sys.exit(main())
