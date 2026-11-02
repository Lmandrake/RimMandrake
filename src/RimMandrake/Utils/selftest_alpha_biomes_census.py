#!/usr/bin/env python3
"""selftest_alpha_biomes_census.py -- the census refuses what it should, and today's tree passes.

    python3 src/RimMandrake/Utils/selftest_alpha_biomes_census.py

Each mutant damages a copy of the real decisions or a small fake repo; none touches the tree.
Item ALPHA_BIOMES_CENSUS_THE_REST_OF_IT.
"""
import copy
import json
import os
import subprocess
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import alpha_biomes_census as C  # noqa: E402

FAILS = []


def check(cond, what, detail=""):
    print(("PASS " if cond else "FAIL ") + what + ("" if cond else "  -- %s" % (detail,)))
    if not cond:
        FAILS.append(what)


def write(root, rel, text):
    p = os.path.join(root, rel)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "w", encoding="utf-8") as fh:
        fh.write(text)


def fake():
    """A small repo: one ported terrain, one category row each, one comment token."""
    t = tempfile.mkdtemp()
    subprocess.run(["git", "init", "-q", t], check=True)
    fill = "".join("<!-- AB_Fill%03d -->\n" % i for i in range(120))
    write(t, "src/M/Defs/T.xml", "<Defs>\n" + fill +
          "<TerrainDef><defName>RM_Soil</defName><texturePath>X/AB_Soil_Polluted</texturePath></TerrainDef></Defs>")
    write(t, "src/M/Source/A.cs", '// AB_Soil in a comment\nclass A { string s = "http://x"; }\n')
    subprocess.run(["git", "-C", t, "add", "src"], check=True)
    cats = {c: {} for c in C.CATEGORIES}
    cats["TerrainDef"]["AB_Soil"] = {"decision": "PORTED", "to": ["RM_Soil"], "why": "x"}
    dec = {"categories": cats, "donor_counts": {c: len(cats[c]) for c in C.CATEGORIES},
           "tokens": dict({"AB_Fill%03d" % i: "fragment" for i in range(120)}, AB_Soil_Polluted="texture_or_record"),
           "live_allowed": []}
    inv = {"defs": ["AB_Soil"] + ["AB_Filler%02d" % i for i in range(60)], "abstracts": []}
    return t, dec, inv


def run(t, dec, inv):
    return C.verify(dec, inv, C.tracked(t), t, donor_root=os.path.join(t, "no_donor"))


def synthetic():
    t, dec, inv = fake()
    status, finds, notes = run(t, dec, inv)
    check(status == "CLEAN", "fixture is clean", finds)
    check(any("UNMEASURED" in n for n in notes), "an absent donor says UNMEASURED, it does not pass silently", notes)

    d = copy.deepcopy(dec)
    d["categories"]["TerrainDef"]["AB_Soil"]["decision"] = "maybe"
    check(any(f.startswith("UNDECIDED") for f in run(t, d, inv)[1]), "mutant: a row with no decision word is refused")

    d = copy.deepcopy(dec)
    d["categories"]["TerrainDef"]["AB_Soil"]["to"] = ["RM_Gone"]
    check(any(f.startswith("STALE_PORT") for f in run(t, d, inv)[1]), "mutant: a port to a missing def is refused")

    d = copy.deepcopy(dec)
    d["categories"]["WeatherDef"]["AB_Soil"] = {"decision": "PORTED", "to": ["RM_Soil"], "why": "x"}
    d["donor_counts"]["WeatherDef"] = 1
    check(any("STALE_PORT WeatherDef" in f for f in run(t, d, inv)[1]), "mutant: a port to a def of the wrong TYPE is refused")

    d = copy.deepcopy(dec)
    d["donor_counts"]["BiomeDef"] = 12
    check(any(f.startswith("COUNT BiomeDef") for f in run(t, d, inv)[1]), "mutant: a category missing rows is refused")

    d = copy.deepcopy(dec)
    d["categories"]["TerrainDef"]["AB_Soil"]["why"] = ""
    check(any(f.startswith("NO_WHY") for f in run(t, d, inv)[1]), "mutant: a decision with no reason is refused")

    d = copy.deepcopy(dec)
    d["tokens"]["AB_Vanished"] = "fragment"
    check(any(f.startswith("STALE_TOKEN") for f in run(t, d, inv)[1]), "mutant: a token gone from src is refused")

    d = copy.deepcopy(dec)
    del d["tokens"]["AB_Soil_Polluted"]
    check(any(f.startswith("UNDECIDED_TOKEN") for f in run(t, d, inv)[1]), "mutant: a new name with no decision is refused")

    i2 = {"defs": ["AB_Soil"], "abstracts": []}
    check(run(t, dec, i2)[0] == "UNMEASURED", "a blind inventory is UNMEASURED, never clean")

    t2, d2, i3 = fake()
    write(t2, "src/M/Source/B.cs", 'class B { string s = "AB_Soil"; }\n')
    write(t2, "src/M/Defs/L.xml", "<Defs><BiomeDef><defName>RM_B</defName><w><AB_Soil>1</AB_Soil></w></BiomeDef></Defs>")
    write(t2, "src/M/Patches/P.xml", "<Patch><Operation><xpath>Defs/BiomeDef/w/AB_Soil</xpath></Operation></Patch>")
    subprocess.run(["git", "-C", t2, "add", "src"], check=True)
    finds = run(t2, d2, i3)[1]
    check(any(f.startswith("LIVE AB_Soil in src/M/Source/B.cs") for f in finds), "a live C# string is refused", finds)
    check(any(f.startswith("LIVE AB_Soil in src/M/Defs/L.xml") for f in finds), "a live XML tag is refused", finds)
    check(any(f.startswith("LIVE AB_Soil in src/M/Patches/P.xml") for f in finds), "an xpath step is refused", finds)

    t3, d3, i4 = fake()
    t4 = dict(d3, tokens=dict(d3["tokens"]))
    t4["live_allowed"] = [{"token": "AB_Soil", "file": "src/M/Source/A.cs"}]
    check(any(f.startswith("STALE_ALLOW") for f in run(t3, t4, i4)[1]), "an allow row with no hit is refused")

    t5 = tempfile.mkdtemp()
    subprocess.run(["git", "init", "-q", t5], check=True)
    write(t5, "src/M/Untracked.xml", "<Defs/>")
    status = C.verify(dec, inv, C.tracked(t5), t5, donor_root=os.path.join(t5, "x"))[0]
    check(status == "UNMEASURED", "an empty tree is UNMEASURED, never clean", status)


def real():
    dec, inv = C.load(C.DECISIONS), C.load(C.INVENTORY)
    status, finds, notes = C.verify(dec, inv, C.tracked(C.REPO), C.REPO)
    check(status == "CLEAN", "the real tree is CLEAN", finds[:5])
    total = sum(len(r) for r in dec["categories"].values())
    check(total >= 200, "the six categories hold every donor row, not a slice", total)


def main():
    synthetic()
    real()
    print("RESULT:", "FAIL %d" % len(FAILS) if FAILS else "PASS")
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
