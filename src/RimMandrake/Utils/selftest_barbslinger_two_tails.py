#!/usr/bin/env python3
"""BARBSLINGER_REDRAW_TWO_TAILS_OWNER_NOTE: the barbslinger has two tails, in its art and in every text a judge reads.

Owner, 2026-11-01, on the kept-art sheet where he picked C: "It is supposed to have two tails, that was the whole
original definition. How in the world that was dropped I don't know. I wrote this creature originally."
The 2026-10-23 art judge had installed a one-tailed render because the def description said "The barbed tail";
the two-tailed art (pick C) is back in, so what this guards is the text that drove the drop:
  1. RM_Barbslinger's <description> names two tails and never "the barbed tail" (singular);
  2. the art-eval departures brief carries a two-tail departure;
  3. the criteria ledger records his note against RM_Barbslinger;
  4. the six installed Barbslinger PNGs are the pick-C bytes (two tails in every facing, looked at 2026-11-05).
Exit 0 when all hold, 1 otherwise.
"""
import hashlib
import json
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
DEF = ROOT / "src/RimMandrake/Pyrelands/Defs/ThingDefs_Races/RM_PyrelandsPortedFauna.xml"
BRIEF = ROOT / "infrastructure/state/art_eval/briefs/RM_Barbslinger.json"
LEDGER = ROOT / "infrastructure/state/art_eval/criteria_ledger.jsonl"
TEX = ROOT / "src/RimMandrake/Pyrelands/Textures/Things/Pawn/Animal/Pyrelands/Barbslinger"
PICK_C = {  # art ledger installs of the 2026-10-31 sheet pick C (and the 2026-11-01 dessicated set)
    "Barbslinger_south.png": "d2217327b73ce22b3e05a66ef32d66aaa375998b1f8ad09b14422868b0b8def3",
    "Barbslinger_east.png": "bbaf33113a1097ac646f2a635c148f9b2c28923afd8d7fcab23b4917e01d2995",
    "Barbslinger_north.png": "b690d85f1fee3de081bb9a73525c2b10bf95aba1b9f291b8c02b74708618a995",
    "Dessicated_Barbslinger_south.png": "872b4a0b39bb3bf99fdde11ee57235588a174b1eca0d110fe9683770104db022",
    "Dessicated_Barbslinger_east.png": "d5d53269ec852ab61abd673b0e9b8032b90f4b889ea9d0a0376101054ed1134b",
    "Dessicated_Barbslinger_north.png": "1564b2938a6a9ee1f92251ca199321cce4508ab5d95368c7dd2999fb59e97014",
}
TWO = re.compile(r"\b(two|twin|both)\b[^.]{0,40}\btails\b", re.I)


def checks():
    fails = []
    desc = None
    for td in ET.parse(DEF).getroot().iter("ThingDef"):
        if td.findtext("defName") == "RM_Barbslinger":
            desc = td.findtext("description") or ""
    if desc is None:
        fails.append("RM_Barbslinger ThingDef not found (sanity: the instrument cannot see the def)")
    else:
        if not TWO.search(desc):
            fails.append("description does not name two tails")
        if re.search(r"\bthe barbed tail\b", desc, re.I):
            fails.append("description still says 'the barbed tail' (one tail)")
    b = json.loads(BRIEF.read_text())
    if not any(TWO.search(d.get("feature", "") + " " + d.get("quote", "")) for d in b.get("departures", [])):
        fails.append("brief has no two-tail departure")
    rows = [json.loads(l) for l in LEDGER.read_text().splitlines() if l.strip()]
    if not any(r.get("subject") == "RM_Barbslinger" and "two tails" in json.dumps(r) for r in rows):
        fails.append("criteria ledger has no RM_Barbslinger two-tails entry")
    for name, sha in PICK_C.items():
        p = TEX / name
        got = hashlib.sha256(p.read_bytes()).hexdigest() if p.is_file() else "MISSING"
        if got != sha:
            fails.append(f"{name} is not the pick-C install ({got[:12]})")
    return fails


def main():
    fails = checks()
    for f in fails:
        print("FAIL", f)
    print("PASS barbslinger two tails" if not fails else f"{len(fails)} failure(s)")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
