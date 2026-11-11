from pathlib import Path
root=Path(__file__).resolve().parents[3]
e=Path(__file__).parent
p=root/'src/RimMandrake/Utils/selftest_hugethings_test_races.py'
s=p.read_text(); start=s.index('    r2 = "RM_TestTitanT2Adult tier=T2 roofAfter='); end=s.index('    t2 = "RM_TestTitanT2Adult tier=T2 costOpen=',start)
s=s[:start]+'''    r2 = "RM_TestTitanT2Adult tier=T2 roofAfter=none wallHpBefore=195 wallHpAfter=%d wallDestroyed=%s"
    rc = "RM_TestTitanT2Control tier=None roofAfter=RoofConstructed wallHpBefore=195 wallHpAfter=195 wallDestroyed=False"
    mode = dict(giantAnimalsEnabled="True", wakeEnabled="True", wakeRoofHolingEnabled="True",
                titanClearingEnabled="True", wallsSlotsEnabled="True")
    legacy = dict(mode, wallsSlotsEnabled="False")
    intact, damaged, broken = r2 % (195, "False"), r2 % (180, "False"), r2 % (0, "True")

    def roof(t, c, m):
        try:
            return L.judge_roof(t, c, m)[0]
        except TypeError:  # pre-fix checker cannot accept measured mode
            return "OLD_CHECKER_NO_MODE"

    for m, good, bad in ((mode, intact, damaged), (legacy, damaged, intact)):
        label = "default" if m is mode else "legacy"
        check("judge_roof %s: correct opposite wall expectation passes" % label, roof(good, rc, m) == "PASS")
        check("judge_roof %s: wrong wall expectation fails" % label, roof(bad, rc, m) == "FAIL")
        check("judge_roof %s: missing control cannot pass" % label, roof(good, None, m) != "PASS")
        for old,new in (("RoofConstructed", "none"), ("wallHpAfter=195", "wallHpAfter=190"),
                        ("tier=None", "tier=T2"), ("RM_TestTitanT2Control", "Elephant")):
            check("judge_roof %s: bad control %s fails" % (label, old), roof(good, rc.replace(old,new), m) == "FAIL")
    check("judge_roof legacy: destroyed wall passes", roof(broken, rc, legacy) == "PASS")
    check("judge_roof default: destroyed wall fails", roof(broken, rc, mode) == "FAIL")
    check("judge_roof: absent measured mode cannot pass", roof(intact, rc, None) is None)
    for f in mode:
        for invalid in (None, "", "yes", "1", "False trailing"):
            check("judge_roof: malformed mode %s=%r is unmeasured" % (f,invalid), roof(intact, rc, dict(mode, **{f:invalid})) is None)
        missing = dict(mode); missing.pop(f)
        check("judge_roof: missing mode field %s is unmeasured" % f, roof(intact, rc, missing) is None)
    for f in ("giantAnimalsEnabled", "wakeEnabled", "wakeRoofHolingEnabled", "titanClearingEnabled"):
        check("judge_roof: disabled prerequisite %s cannot pass" % f, roof(intact, rc, dict(mode, **{f:"False"})) != "PASS")
    for old,new in (("tier=T2", "tier=None"), ("RM_TestTitanT2Adult", "Elephant"),
                    ("roofAfter=none", "roofAfter=RoofConstructed"), ("roofAfter=none", "roofAfter=RoofRockThin")):
        check("judge_roof: wrong subject/roof %s fails" % new, roof(intact.replace(old,new), rc, mode) == "FAIL")
    for t,c in ((intact.replace("wallHpBefore=195", "wallHpBefore=0"),rc),
                (intact,rc.replace("wallHpBefore=195 wallHpAfter=195", "wallHpBefore=0 wallHpAfter=0")),
                (intact.replace("wallHpAfter=195", "wallHpAfter=-1"),rc),
                (intact.replace("wallHpAfter=195", "wallHpAfter=196"),rc),
                (broken.replace("wallDestroyed=True", "wallDestroyed=False"),rc),
                (intact.replace("wallDestroyed=False", "wallDestroyed=garbage"),rc),
                (intact.replace("roofAfter=none", ""),rc),
                (intact+" tier=T2",rc), ("FAIL no map or kind",rc)):
        check("judge_roof: malformed or vacuous data cannot pass: %s" % t, roof(t,c,mode) != "PASS")
''' +s[end:]
p.write_text(s)
