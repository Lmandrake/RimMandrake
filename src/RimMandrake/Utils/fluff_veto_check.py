#!/usr/bin/env python3
"""fluff_veto_check.py -- proof for FLUFF_ASKS_DECIDE_EIGHT_UNDER_VETO.

Exits 0 when:
  1. design/RimMandrake/fluff_cuts_2026-10-23.md decides every one of the eight rows that
     used to ask the owner (Abyss #6, Fever Wood #11, Lantern Deeps #12, Miasma #M6/#M12,
     The Rot #R3, Wasteland #7/#11) inside its "Decided 2026-11-02" section, and no
     "Rows that ask him" section is left;
  2. design/validation_walks/RimMandrake/BlueDesert.md names the cut rime road nowhere, and
     the digest offers that north star for validation;
  3. the two cuts are gone from src (no live def, class, setting or proof names them) while
     what was kept (the blinker race, the two mangals) still exists.
Prints one line per failure; exits 1 on any.

    python3 src/RimMandrake/Utils/fluff_veto_check.py
"""
import os
import re
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", ".."))
DIGEST = os.path.join(ROOT, "design", "RimMandrake", "fluff_cuts_2026-10-23.md")
WALK = os.path.join(ROOT, "design", "validation_walks", "RimMandrake", "BlueDesert.md")
ROWS = ["Abyss #6", "Fever Wood #10 and #11", "Lantern Deeps #12, the blinker", "Lantern Deeps #12, the slick",
        "Miasma #M6", "Miasma #M12", "The Rot #R3", "Wasteland #7", "Wasteland #11"]
# Names that only the cut code carried. A line that also says "cut" or "retired" is the
# tombstone comment that records the cut, not a use.
GONE = re.compile(r"RM_CompFlashOnHurt|RM_CompProperties_FlashOnHurt|RM_BlinkerFlare|RM_BlinkerDazzled|"
                  r"blinkerFlashEnabled|ProofBlinker|blinker_flashes|PollinationGate|pollinationGateEnabled|"
                  r"pollinatorRace")
TOMBSTONE = re.compile(r"\bcut\b|retired", re.I)
EXTS = (".cs", ".xml", ".py", ".json", ".csproj")


def read(p):
    with open(p, encoding="utf-8") as f:
        return f.read()


def main():
    bad = []
    d = read(DIGEST)
    if "Rows that ask him" in d:
        bad.append("digest still has a 'Rows that ask him' section")
    m = re.search(r"^## Decided 2026-11-02.*?(?=^## )", d, re.S | re.M)
    if not m:
        bad.append("digest has no '## Decided 2026-11-02' section")
    else:
        sec = m.group(0)
        for r in ROWS:
            if r not in sec:
                bad.append("decided section does not name %r" % r)
        for h in ("### Cut", "### Kept", "### Moved out of scope"):
            if h not in sec:
                bad.append("decided section lacks %s" % h)
    if "offered to him for validation" not in d:
        bad.append("digest does not offer the BlueDesert north star for validation")
    w = read(WALK)
    if re.search(r"rime[ -]road|RM_RimeRoad", w, re.I):
        bad.append("BlueDesert walk still names the cut rime road")
    if not re.search(r"^## north star", w, re.M):
        bad.append("BlueDesert walk lost its north star section")

    scanned = 0
    for base in ("src",):
        for dp, dn, fn in os.walk(os.path.join(ROOT, base)):
            dn[:] = [x for x in dn if x not in ("bin", "obj", ".git", "node_modules")]
            for f in fn:
                if not f.endswith(EXTS) or f == "fluff_veto_check.py":
                    continue
                p = os.path.join(dp, f)
                scanned += 1
                try:
                    txt = read(p)
                except (UnicodeDecodeError, OSError):
                    continue
                if not GONE.search(txt):
                    continue
                for i, line in enumerate(txt.split("\n"), 1):
                    if GONE.search(line) and not TOMBSTONE.search(line):
                        bad.append("%s:%d still names cut code: %s" % (os.path.relpath(p, ROOT), i, line.strip()))
    if scanned < 1000:  # sanity probe: the instrument must see the tree
        bad.append("scanned only %d source files; the walk is blind" % scanned)

    ld = read(os.path.join(ROOT, "src", "RimMandrake", "LanternDeeps", "Defs", "Fauna", "RM_LanternDeeps_Hydrocarbon_Wave2.xml"))
    if ld.count("<defName>RM_Blinker</defName>") != 2:
        bad.append("the blinker (kept as a plain animal) lost its ThingDef or PawnKindDef")
    mg = read(os.path.join(ROOT, "src", "RimMandrake", "Miasma", "Defs", "ThingDefs_Plants", "RM_Miasma_Mangals.xml"))
    for k in ("RM_Thessamor", "RM_Quennath"):
        if "<defName>%s</defName>" % k not in mg:
            bad.append("kept mangal %s is missing" % k)

    for b in bad:
        print("FAIL " + b)
    print("fluff_veto_check: %s (%d source files scanned)" % ("FAIL" if bad else "PASS", scanned))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
