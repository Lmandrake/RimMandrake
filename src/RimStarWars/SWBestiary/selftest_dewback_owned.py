#!/usr/bin/env python3
"""selftest_dewback_owned.py -- offline guard for MOOKEE_TRADE_ANIMAL_IDENTIFY_1.

"Mookee" (a pet name from RSW_Jawa_NamerPetSW) was worn by a donor `Dewback` from mlie.starwarsanimalcollection,
which has the donor's cartoonish art. The item closed because our port owns that animal. This test keeps it owned:
  1. RSW_Dewback is a ThingDef whose bodyGraphicData texPath is RimStarWars/SWBestiary/Dewback/Dewback, and the
     Dewback_{east,north,south}.png it reads exist as RGBA PNGs (owner's set C, 34bb644a86; footprint refit eafa695642);
  2. no def under src/ has the bare defName `Dewback` (that name is the donor's race);
  3. the donor packageId is absent from the shipping candidate list and from ModsConfig.FULL.LATEST (parsed
     activeMods; each list must hold all five DLC packageIds, or the parse is blind).
The defName scanner is probed on planted text first, so a blind scanner cannot pass.
Run bare: python3 src/RimStarWars/SWBestiary/selftest_dewback_owned.py   (exit 0 = clean)
"""
import os
import re
import struct
import sys
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
SRC = os.path.join(ROOT, "src")
RACE = os.path.join(HERE, "Defs", "ThingDefs_Races", "RSW_Dewback.xml")
TEX = os.path.join(HERE, "Textures", "RimStarWars", "SWBestiary", "Dewback")
TEXPATH = "RimStarWars/SWBestiary/Dewback/Dewback"
LISTS = [os.path.join(ROOT, "infrastructure", "state", "modlists", n) for n in
         ("ModsConfig.FULL.CANDIDATE_DONORS_RETIRED_2026-10-18.xml", "ModsConfig.FULL.LATEST.xml")]
DONOR = "mlie.starwarsanimalcollection"
DLC = ("ludeon.rimworld.royalty", "ludeon.rimworld.ideology", "ludeon.rimworld.biotech",
       "ludeon.rimworld.anomaly", "ludeon.rimworld.odyssey")
SKIP = {"obj", "bin", "Textures", ".git", "node_modules"}
COMMENT = re.compile(r"<!--.*?-->", re.S)
BARE = re.compile(r"<defName>\s*Dewback\s*</defName>")

FAILS = []


def check(ok, what):
    print("%s  %s" % ("ok  " if ok else "FAIL", what))
    if not ok:
        FAILS.append(what)


def bare_hits(text):
    return len(BARE.findall(COMMENT.sub("", text)))


def png_rgba(path):
    with open(path, "rb") as f:
        head = f.read(26)
    return head[:8] == b"\x89PNG\r\n\x1a\n" and head[12:16] == b"IHDR" and head[25] == 6 and struct.unpack(">I", head[16:20])[0] > 0


def main():
    # probe: the scanner sees a bare Dewback, ignores a commented one and the port's name
    check(bare_hits("<ThingDef><defName>Dewback</defName></ThingDef>") == 1, "probe: scanner sees a bare Dewback def")
    check(bare_hits("<!-- <defName>Dewback</defName> --><defName>RSW_Dewback</defName>") == 0,
          "probe: scanner skips comments and RSW_Dewback")

    root = ET.parse(RACE).getroot()
    race = [d for d in root.iter("ThingDef") if (d.findtext("defName") or "").strip() == "RSW_Dewback"]
    check(len(race) == 1, "RSW_Dewback ThingDef defined once in RSW_Dewback.xml")
    paths = {(t.text or "").strip() for t in root.iter("texPath")}
    check(TEXPATH in paths, "RSW_Dewback.xml binds texPath %s" % TEXPATH)
    for facing in ("east", "north", "south"):
        p = os.path.join(TEX, "Dewback_%s.png" % facing)
        check(os.path.isfile(p) and png_rgba(p), "Dewback_%s.png is an RGBA PNG" % facing)

    hits, seen = [], 0
    for dp, dns, fns in os.walk(SRC):
        dns[:] = [d for d in dns if d not in SKIP]
        for fn in fns:
            if not fn.endswith(".xml"):
                continue
            seen += 1
            with open(os.path.join(dp, fn), encoding="utf-8", errors="replace") as f:
                if bare_hits(f.read()):
                    hits.append(os.path.relpath(os.path.join(dp, fn), ROOT))
    check(seen > 100, "scanned %d XML files under src/ (instrument sees the tree)" % seen)
    check(not hits, "no bare <defName>Dewback</defName> under src/%s" % ("" if not hits else ": " + ", ".join(hits[:5])))

    for lst in LISTS:
        active = [(li.text or "").strip().lower() for li in ET.parse(lst).getroot().find("activeMods")]
        name = os.path.basename(lst)
        check(all(d in active for d in DLC), "%s parses: all five DLC present (%d active)" % (name, len(active)))
        check(DONOR not in active, "%s does not load %s" % (name, DONOR))

    print("RESULT: %s" % ("PASS" if not FAILS else "FAIL (%d)" % len(FAILS)))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
