"""Offline checks for jawa_shallows_proof.py's pure verdicts (JAWA_DROWNING_PROVE_RAT_SIZED_IN_SHALLOWS; since
RIMMANDRAKE_CLASS_DROID_AND_JAWA_GONE_IN_SHALLOW_TAR the proof holds the fixed behaviour). No bridge.

Also pins the arithmetic the live proof stands on, read from the shipped C# (a humanlike is HeightByBand[2] x sqrt(body
size), DefaultHeadFraction 0.9): a Jawa (body size 0.5) is 1.24 m, its head under at 1.11 m, so 0.5 m shallows are wading
water."""
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
jawa_h = bands[2] * 0.5 ** 0.5 if len(bands) > 2 else 0.0
check("C#: a humanlike's height is HeightByBand[2] x sqrt(body size)",
      re.search(r"return\s+HeightByBand\[2\]\s*\*\s*\(float\)Math\.Sqrt\(\s*b\s*\)", rr) is not None)
check("C#: the proof's Jawa floor is under a Jawa's height (%.2f m)" % jawa_h, J.JAWA_MIN_H <= jawa_h)
hf = re.search(r"DefaultHeadFraction\s*=\s*([0-9.]+)f", rr)
check("C#: DefaultHeadFraction is the proof's head fraction", hf is not None and float(hf.group(1)) == J.HEAD_FRACTION)
check("arithmetic: 0.5 m of water is under a Jawa's head standing", 0.5 <= jawa_h * J.HEAD_FRACTION)
fe = open(os.path.join(SRC, "RM_PitFillEffects.cs"), encoding="utf-8").read()
check("C#: ProofDrown prints H, lying, water, under, headUp", all(k in fe for k in ('" H="', '" lying="', '" water="',
                                                                                   '" under="', '" headUp="')))
sw = open(os.path.join(SRC, "Swimming", "RM_Swim.cs"), encoding="utf-8").read()
check("C#: RM_Swim lives in the namespace the proof calls",
      "namespace " + J.SWIM_TYPE.rsplit(".", 1)[0] in sw and "public static string ProofSwim" in sw)
check("C#: RM_PitFillEffects lives in the namespace the proof calls",
      "namespace " + J.FILL_TYPE.rsplit(".", 1)[0] in fe and "public static string ProofDrown" in fe)

DROWN = "DROWN Human123 H=1.24 lying=False water=0.50 under=False headUp=True exit=False perCheck=0.0000"
d = J.parse(DROWN)
check("parse: id and keys", d.get("id") == "Human123" and d.get("H") == "1.24" and d.get("headUp") == "True")
check("parse: REFUSED is empty", J.parse("REFUSED: no pawn at (1, 0, 1)") == {})

check("terrain: brine PASS", J.terrain_verdict(J.BRINE)[0] == "PASS")
check("can-fail terrain: soil FAIL", J.terrain_verdict("Soil")[0] == "FAIL")
check("terrain: none UNMEASURED", J.terrain_verdict(None)[0] == "UNMEASURED")

check("height: 1.24 PASS", J.height_verdict(d)[0] == "PASS")
check("can-fail height: the rat's 0.50 FAIL", J.height_verdict(J.parse(DROWN.replace("H=1.24", "H=0.50")))[0] == "FAIL")
check("height: no line UNMEASURED", J.height_verdict({})[0] == "UNMEASURED")

check("under head: 0.50 m standing, under=False PASS", J.under_head_verdict(d)[0] == "PASS")
check("can-fail under head: the rat's H, under=True FAIL",
      J.under_head_verdict(J.parse(DROWN.replace("H=1.24", "H=0.50").replace("under=False", "under=True")))[0] == "FAIL")
check("can-fail under head: mod says under=True FAIL", J.under_head_verdict(J.parse(DROWN.replace("under=False", "under=True")))[0] == "FAIL")
check("under head: lying is UNMEASURED", J.under_head_verdict(J.parse(DROWN.replace("lying=False", "lying=True")))[0] == "UNMEASURED")
check("under head: no water UNMEASURED", J.under_head_verdict(J.parse(DROWN.replace("water=0.50", "water=0.00")))[0] == "UNMEASURED")

NONE = {"class": "None", "exhaustion": "0.000"}
calm = [{"tick": 0, "severity": 0, "drown": d, "swim": NONE}, {"tick": 6000, "severity": 0, "drown": d, "swim": NONE}]
check("no drowning: wades the whole run PASS", J.no_drowning_verdict(calm, 6000)[0] == "PASS")
check("can-fail no drowning: drowning fires FAIL",
      J.no_drowning_verdict([calm[0], dict(calm[1], severity=0.04)], 6000)[0] == "FAIL")
check("can-fail no drowning: it swims FAIL",
      J.no_drowning_verdict([calm[0], dict(calm[1], swim={"class": "Swimmer", "exhaustion": "0.1"})], 6000)[0] == "FAIL")
check("no drowning: stopped early UNMEASURED", J.no_drowning_verdict([calm[0], dict(calm[1], tick=2000)], 6000)[0] == "UNMEASURED")
check("no drowning: no reads UNMEASURED", J.no_drowning_verdict([], 6000)[0] == "UNMEASURED")

# exit semantics the live round reads (0 PASS, 1 FAIL, else UNMEASURED): a harness fault is never a mod FAIL
def rws(*st):
    return [{"id": "JS%d_x" % (i + 1), "status": v} for i, v in enumerate(st)]


check("exit: four PASS rows -> 0", J.exit_code(rws("PASS", "PASS", "PASS", "PASS")) == 0)
check("exit: a measured FAIL -> 1", J.exit_code(rws("PASS", "FAIL", "PASS", "PASS")) == 1)
check("exit: an UNMEASURED row, no FAIL -> 2", J.exit_code(rws("PASS", "PASS", "UNMEASURED", "PASS")) == 2)
check("exit: no rows (died before JS1) -> 2", J.exit_code([{"id": "JS0_site_ready", "status": "UNMEASURED"}]) == 2)


def boom():
    raise RuntimeError("refusing rimworld/go_to_main_menu: 1 earlier mutating call(s) have an UNKNOWN outcome")


check("guarded: a bridge refusal traceback -> 2, not 1", J.guarded(boom) == 2)
check("guarded: a clean return passes through", J.guarded(lambda: 1) == 1)

print("%d FAIL" % len(fails) if fails else "ALL OK")
sys.exit(1 if fails else 0)
