#!/usr/bin/env python3
"""selftest_rot_donor_names.py -- the Alpha Animals ports never show the player a donor creature name.

Offline proof that validation.donor_name_checks can see: the shipped RM_Chittik.xml / RM_AgariPorts.xml are clean,
and each planted donor name (in a label, a description, a labelShort) turns it red, while the same name inside a
provenance comment does not. Found in the ROT_FAUNA_KIN_WIRING_1 review: the chittik's hediff said "Swarmling".
    python3 src/RimMandrake/TheRot/Tools/selftest_rot_donor_names.py
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import validation  # noqa: E402

FAUNA = os.path.join(validation.HERE, "Defs", "Fauna")


def main():
    chit = open(os.path.join(FAUNA, "RM_Chittik.xml"), encoding="utf-8").read()
    agari = open(os.path.join(FAUNA, "RM_AgariPorts.xml"), encoding="utf-8").read()
    cases = [("clean", not validation.donor_name_checks())]

    def planted(name, fn, old, new, want_red=True):
        txt = chit if fn == "RM_Chittik.xml" else agari
        mutated = txt.replace(old, new, 1)
        if mutated == txt:   # an anchor that matches nothing would read as caught
            cases.append((name + " (anchor missing)", False))
            return
        red = bool(validation.donor_name_checks({fn: mutated}))
        cases.append((name, red == want_red))

    planted("hediff label", "RM_Chittik.xml", "<label>chittik implantation</label>",
            "<label>swarmling implantation</label>")
    planted("description", "RM_AgariPorts.xml", "<label>gromma</label>\n    <description>A great",
            "<label>gromma</label>\n    <description>An Agaripod, a great")
    planted("labelShort", "RM_Chittik.xml", "<labelShort>claw</labelShort>", "<labelShort>Swarmling claw</labelShort>")
    planted("comment ignored", "RM_AgariPorts.xml", "<!-- ROT_FAUNA_KIN_WIRING_1:",
            "<!-- (was AA_MycoidColossus, Alpha Animals) ROT_FAUNA_KIN_WIRING_1:", want_red=False)
    fails = [n for n, ok in cases if not ok]
    for n, ok in cases:
        print("%s %s" % ("ok  " if ok else "FAIL", n))
    if len(cases) < 5:
        fails.append("only %d cases ran" % len(cases))
    if fails:
        print("selftest_rot_donor_names: FAIL (%s)" % ", ".join(fails))
        return 1
    print("selftest_rot_donor_names: PASS (%d/%d)" % (len(cases), len(cases)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
