#!/usr/bin/env python3
"""owed_blackstar_jetpacks.py - acceptance test owed by RIMMANDRAKE_GIVE_BLACKSTAR_RAIDERS_THE_ARMOURY_JETPACK_ALREADY_HERE.

Owner, 2026-11-24 about 11:15 PM PST: "The Blackstar faction definitely has jump packs (it is canon lore that Mandalorians
have jump packs)." The Star Wars jump packs already exist: guy762_Jetpack_light / _heavy / _missile in
mandrake.rsw.armoury (src/RimStarWars/Armoury), each with the vanilla Verb_Jump. No Blackstar pawn kind can wear one today.

RED by design until that ticket is built, so it is named outside run_selftests' `selftest*.py` discovery; the build that
makes it green renames it selftest_blackstar_jetpacks.py.

PASS when all hold, over the RUT_Jawa_Blackstar_* PawnKindDefs in Defs/PawnKindDefs/JawaFactionRoster.xml:
  1  at least one Blackstar kind requires (apparelRequired) or tags (apparelTags) a Verb_Jump apparel of the Armoury
  2  a required Armoury def carries MayRequire="mandrake.rsw.armoury" (load safety when the Armoury is absent)
  3  no Blackstar kind requires a def that the ship cut list cuts (infrastructure/state/cherrypicker/CherryPicker.SHIP.xml)
Exit 0 PASS, 1 FAIL, 2 COULD NOT LOOK (a file will not read or parse, or the Armoury holds no Verb_Jump apparel).
  --roster PATH   check this roster file instead (used to show the test can go green)
Seen RED on the base 2026-11-24 (line 1); GREEN on a planted roster with MNC_jetpack_light in the Breacher's tags; RED on
a planted roster that requires Apparel_PackJump (line 3) and on one that requires guy762_Jetpack_light unguarded (line 2).
"""
import argparse
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
ROSTER = REPO / "src/RimUtinni/UtinniPatches/Defs/PawnKindDefs/JawaFactionRoster.xml"
ARMOURY = REPO / "src/RimStarWars/Armoury/Defs"
CUT = REPO / "infrastructure/state/cherrypicker/CherryPicker.SHIP.xml"


def armoury_jump_gear():
    defs, tags = set(), set()
    for f in ARMOURY.rglob("*.xml"):
        root = ET.parse(f).getroot()
        for td in root.iter("ThingDef"):
            name = td.findtext("defName")
            verbs = [v.text for v in td.iter("verbClass")]
            if name and any(v and v.strip().endswith("Verb_Jump") for v in verbs):
                defs.add(name.strip())
                tags.update(li.text.strip() for li in td.findall("apparel/tags/li") if li.text)
    return defs, tags


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--roster")
    a = ap.parse_args()
    try:
        jdefs, jtags = armoury_jump_gear()
        root = ET.parse(a.roster or ROSTER).getroot()
        cut = set(re.findall(r"<li>ThingDef/([^<]+)</li>", CUT.read_text(encoding="utf-8")))
    except (OSError, ET.ParseError) as e:
        print(f"COULD NOT LOOK  {e}")
        return 2
    if not jdefs:
        print("COULD NOT LOOK  the Armoury holds no Verb_Jump apparel: the instrument sees nothing to give")
        return 2
    kinds = [k for k in root.iter("PawnKindDef") if (k.findtext("defName") or "").startswith("RUT_Jawa_Blackstar_")]
    if not kinds:
        print("COULD NOT LOOK  no RUT_Jawa_Blackstar_* PawnKindDef in the roster")
        return 2
    bad, carriers = [], []
    for k in kinds:
        n = k.findtext("defName")
        req = k.findall("apparelRequired/li")
        tags = {li.text.strip() for li in k.findall("apparelTags/li") if li.text}
        for li in req:
            d = (li.text or "").strip()
            if d in cut:
                bad.append(f"3 {n} requires {d}, which the ship cut list cuts")
            if d in jdefs:
                carriers.append(n)
                if li.get("MayRequire", "").lower() != "mandrake.rsw.armoury":
                    bad.append(f"2 {n} requires {d} without MayRequire=\"mandrake.rsw.armoury\"")
        if tags & jtags:
            carriers.append(n)
    if not carriers:
        bad.append(f"1 no Blackstar kind ({len(kinds)} read) requires or tags an Armoury jump pack "
                   f"({', '.join(sorted(jdefs))}; tags {', '.join(sorted(jtags))})")
    for b in bad:
        print("FAIL  " + b)
    if bad:
        return 1
    print(f"PASS  Blackstar kinds with a jump pack: {', '.join(sorted(set(carriers)))}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
