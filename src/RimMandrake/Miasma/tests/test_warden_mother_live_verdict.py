#!/usr/bin/env python3
"""MIASMA_WARDEN_MOTHER_ART_1: offline proof that live L2 (warden_mother_live_proof.py) can go red.

1. The probe's constants match RM_WardenMother.xml: the adult stage draws ADULT_TEX, the PawnKindDef lifeStage that
   pairs with the RM_WardenMotherElder race stage draws AGED_TEX, and ADULT_AGE < elder minAge <= AGED_AGE < lifeExpectancy.
2. verdict() on readings shaped like the real thing_explain / set_pawn_age replies:
   PASS on a good reading; FAIL on the gen-1 checker's mutant (elder texPath set back to adult art), on a stage that
   never turns elder, on an aged path no mod holds, and on a resolved render tree drawing another texture;
   UNMEASURED (never PASS) when the render tree never resolved.
Exit 0 all hold, 1 otherwise.
"""
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import warden_mother_live_proof as P  # noqa: E402

XML = HERE.parent / "Defs/ThingDefs_Races/RM_WardenMother.xml"
PACK = "mandrake.rm.biomes"
FAILS = []


def check(name, ok, detail=""):
    print(("PASS " if ok else "FAIL ") + name + (": " + detail if detail else ""))
    if not ok:
        FAILS.append(name)


def explain(tex, label="OBSERVED", holders=(PACK,), limits="animal life-stage graphics only"):
    return {"success": True, "what": {"x": 10, "z": 10},
            "appearance": {"limits": limits, "paths": [
                {"role": "body", "texPath": tex, "packsHoldingPath": list(holders),
                 "provider": holders[0] if holders else None, "label": label, "note": ""}]}}


def defs_side():
    root = ET.parse(XML).getroot()
    race = next(t for t in root.iter("ThingDef") if t.findtext("defName") == P.KIND)
    ages = race.find("race/lifeStageAges").findall("li")
    stages = [li.findtext("def") for li in ages]
    elder_i = stages.index(P.ELDER_STAGE)
    elder_min = float(ages[elder_i].findtext("minAge"))
    life = float(race.findtext("race/lifeExpectancy"))
    kind = next(t for t in root.iter("PawnKindDef") if t.findtext("defName") == P.KIND)
    kls = [li.findtext("bodyGraphicData/texPath") for li in kind.find("lifeStages").findall("li")]
    check("kind lifeStages pair 1:1 with race lifeStageAges", len(kls) == len(stages), "%d vs %d" % (len(kls), len(stages)))
    check("elder stage draws AGED_TEX", kls[elder_i] == P.AGED_TEX, repr(kls[elder_i]))
    check("adult stage draws ADULT_TEX", kls[elder_i - 1] == P.ADULT_TEX, repr(kls[elder_i - 1]))
    check("ELDER_MIN_AGE pinned to the XML", P.ELDER_MIN_AGE == elder_min, "%s vs %s" % (P.ELDER_MIN_AGE, elder_min))
    check("ADULT_AGE < elder minAge <= AGED_AGE < lifeExpectancy",
          float(ages[elder_i - 1].findtext("minAge")) <= P.ADULT_AGE < elder_min <= P.AGED_AGE < life,
          "%s < %s <= %s < %s" % (P.ADULT_AGE, elder_min, P.AGED_AGE, life))


def verdict_side():
    adult = explain(P.ADULT_TEX)
    cases = [
        ("good reading", ("AnimalAdult", adult, P.ELDER_STAGE, explain(P.AGED_TEX)), 0),
        ("MUTANT elder texPath -> adult art", ("AnimalAdult", adult, P.ELDER_STAGE, explain(P.ADULT_TEX)), 1),
        ("stage never turns elder", ("AnimalAdult", adult, "AnimalAdult", explain(P.ADULT_TEX)), 1),
        ("aged path held by no mod", ("AnimalAdult", adult, P.ELDER_STAGE,
                                      explain(P.AGED_TEX, label="UNKNOWN", holders=())), 1),
        ("render tree draws another texture", ("AnimalAdult", adult, P.ELDER_STAGE,
                                               explain(P.AGED_TEX, label="CANDIDATE")), 1),
        ("adult stage draws wrong art", ("AnimalAdult", explain(P.AGED_TEX), P.ELDER_STAGE, explain(P.AGED_TEX)), 1),
        ("render tree never resolved", ("AnimalAdult", adult, P.ELDER_STAGE, explain(
            P.AGED_TEX, label="CANDIDATE", limits="x; render tree not resolved yet (never forced), so no OBSERVED")), 2),
        ("boundary never crossed", (P.ELDER_STAGE, explain(P.AGED_TEX), P.ELDER_STAGE, explain(P.AGED_TEX)), 2),
        ("no body row", ("AnimalAdult", {"appearance": {"paths": []}}, P.ELDER_STAGE, explain(P.AGED_TEX)), 2),
    ]
    for name, args, want in cases:
        code, line = P.verdict(*args)
        check("verdict: " + name, code == want, "exit %d (want %d) %s" % (code, want, line))


def main():
    defs_side()
    verdict_side()
    print("RESULT: %s" % ("FAIL " + ", ".join(FAILS) if FAILS else "PASS"))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
