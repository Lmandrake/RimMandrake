"""Offline checks for jawa_shallows_proof.py's pure verdicts (JAWA_DROWNING_PROVE_RAT_SIZED_IN_SHALLOWS). No bridge.

Also pins the arithmetic the live proof stands on, read from the shipped C# (RM_RelativeRulesMath.HeightByBand[1] = 0.5,
DefaultHeadFraction 0.9): a Jawa's head is under at 0.45 m standing, so 0.5 m of shallow water is over it."""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import jawa_shallows_proof as J  # noqa: E402

SRC = os.path.join(os.path.dirname(HERE), "Source")
fails = []


def check(name, cond):
    print("%-4s  %s" % ("ok" if cond else "FAIL", name))
    if not cond:
        fails.append(name)


# the C# the constants mirror
rr = open(os.path.join(SRC, "RM_RelativeRulesMath.cs"), encoding="utf-8").read()
m = re.search(r"HeightByBand\s*=\s*\{([^}]*)\}", rr)
bands = [float(v.strip().rstrip("f")) for v in m.group(1).split(",")] if m else []
check("C#: HeightByBand[1] (small band) is the proof's Jawa H", len(bands) > 1 and bands[1] == J.JAWA_H)
hf = re.search(r"DefaultHeadFraction\s*=\s*([0-9.]+)f", rr)
check("C#: DefaultHeadFraction is the proof's head fraction", hf is not None and float(hf.group(1)) == J.HEAD_FRACTION)
check("arithmetic: 0.5 m of water is over a 0.5 m creature's head standing", 0.5 > J.JAWA_H * J.HEAD_FRACTION + 1e-4)
fe = open(os.path.join(SRC, "RM_PitFillEffects.cs"), encoding="utf-8").read()
check("C#: ProofDrown prints H, lying, water, under, headUp", all(k in fe for k in ('" H="', '" lying="', '" water="',
                                                                                   '" under="', '" headUp="')))
sw = open(os.path.join(SRC, "Swimming", "RM_Swim.cs"), encoding="utf-8").read()
check("C#: RM_Swim lives in the namespace the proof calls",
      "namespace " + J.SWIM_TYPE.rsplit(".", 1)[0] in sw and "public static string ProofSwim" in sw)
check("C#: RM_PitFillEffects lives in the namespace the proof calls",
      "namespace " + J.FILL_TYPE.rsplit(".", 1)[0] in fe and "public static string ProofDrown" in fe)

DROWN = "DROWN Human123 H=0.50 lying=False water=0.50 under=True headUp=True exit=False perCheck=0.0000"
d = J.parse(DROWN)
check("parse: id and keys", d.get("id") == "Human123" and d.get("H") == "0.50" and d.get("headUp") == "True")
check("parse: REFUSED is empty", J.parse("REFUSED: no pawn at (1, 0, 1)") == {})

check("terrain: brine PASS", J.terrain_verdict(J.BRINE)[0] == "PASS")
check("can-fail terrain: soil FAIL", J.terrain_verdict("Soil")[0] == "FAIL")
check("terrain: none UNMEASURED", J.terrain_verdict(None)[0] == "UNMEASURED")

check("height: 0.50 PASS", J.height_verdict(d)[0] == "PASS")
check("can-fail height: a person-band 1.75 FAIL", J.height_verdict(J.parse(DROWN.replace("H=0.50", "H=1.75")))[0] == "FAIL")
check("height: no line UNMEASURED", J.height_verdict({})[0] == "UNMEASURED")

check("over head: 0.50 m standing, under=True PASS", J.over_head_verdict(d)[0] == "PASS")
check("can-fail over head: 0.40 m FAIL",
      J.over_head_verdict(J.parse(DROWN.replace("water=0.50", "water=0.40").replace("under=True", "under=False")))[0] == "FAIL")
check("can-fail over head: mod says under=False FAIL", J.over_head_verdict(J.parse(DROWN.replace("under=True", "under=False")))[0] == "FAIL")
check("over head: lying is UNMEASURED", J.over_head_verdict(J.parse(DROWN.replace("lying=False", "lying=True")))[0] == "UNMEASURED")

SW = {"class": "Swimmer", "exhaustion": "0.100"}
DOWN = J.parse(DROWN.replace("headUp=True", "headUp=False"))
good = [{"tick": 0, "severity": 0, "drown": d, "swim": SW},
        {"tick": 2250, "severity": 0.04, "drown": DOWN, "swim": dict(SW, exhaustion="1.000")}]
check("drowning: swims, then drowns head-under PASS", J.drowning_verdict(good)[0] == "PASS")
check("can-fail drowning: never fires FAIL", J.drowning_verdict([dict(good[0]), dict(good[0], tick=6000)])[0] == "FAIL")
check("can-fail drowning: fires while headUp FAIL",
      J.drowning_verdict([good[0], dict(good[1], drown=d)])[0] == "FAIL")
check("can-fail drowning: drowns with no swim read FAIL",
      J.drowning_verdict([dict(r, swim={"class": "None"}) for r in good])[0] == "FAIL")
check("drowning: no reads UNMEASURED", J.drowning_verdict([])[0] == "UNMEASURED")

print("%d FAIL" % len(fails) if fails else "ALL OK")
sys.exit(1 if fails else 0)
