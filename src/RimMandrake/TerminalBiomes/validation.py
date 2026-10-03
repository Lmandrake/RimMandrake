"""validation.py -- modcheck suite for RimMandrake: TerminalBiomes (first script, item CHILL_NATIVE_COLD_TOLERANCE_1).

PROVES (def level, offline): every RM_ Chill native ThingDef is comfortable below the -110 C floor
(ComfyTemperatureMin <= -150, ComfyTemperatureMax still set and above the min).
NOT PROVEN: live hypothermia absence on a dive (UNMEASURED; needs a live dive with the owner's walk).
`python3 validation.py` runs static_checks() without a game.
"""
import os
import sys
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
FLOOR_C = -110.0
NATIVE_MIN_C = -150.0
FILES = ["RM_TheChillFauna.xml", "RM_TheChillFloorLife.xml"]
NATIVES = ["RM_Heemin", "RM_Oovanam", "RM_Hoolen", "RM_Vaunoom", "RM_Fessu", "RM_Krellik", "RM_Oddu",
           "RM_Oovu", "RM_Iliss", "RM_Tarnn"]


def static_checks():
    bad, seen = [], set()
    for f in FILES:
        root = ET.parse(os.path.join(HERE, "Defs", "ThingDefs_Races", f)).getroot()
        for td in root.findall("ThingDef"):
            n = td.findtext("defName")
            if n not in NATIVES:
                continue
            seen.add(n)
            mn = td.findtext("statBases/ComfyTemperatureMin")
            mx = td.findtext("statBases/ComfyTemperatureMax")
            if mn is None or float(mn) > NATIVE_MIN_C:
                bad.append("%s ComfyTemperatureMin=%s, needs <= %g" % (n, mn, NATIVE_MIN_C))
            if mx is None or (mn is not None and float(mx) <= float(mn)):
                bad.append("%s ComfyTemperatureMax %s not above min" % (n, mx))
    for n in NATIVES:
        if n not in seen:
            bad.append("native ThingDef %s not found" % n)
    return bad


try:
    from modcheck import Suite
    suite = Suite("TerminalBiomes")

    @suite.chain("natives_tolerate_floor")
    def natives_tolerate_floor(t):
        bad = static_checks()
        if bad:
            from modcheck import ExpectationFailed
            raise ExpectationFailed("; ".join(bad))
except ImportError:
    suite = None

if __name__ == "__main__":
    problems = static_checks()
    print("STATIC: %s" % ("PASS (0 findings)" if not problems else "FAIL"))
    for p in problems:
        print("  - " + p)
    sys.exit(1 if problems else 0)
