"""selftest_stun_bodysize_gate.py -- ThirdPartyStunBodySize_Squared.xml writes only when its StatDef exists. L0 (static).

Each op Adds victimSeverityScaling=RSW_Jawa_InverseBodySize to an absorbed KotOR stun DamageDef. That StatDef lives in
mandrake.rsw.ionweapons, which mandrake.rsw.patches neither depends on nor loads after; gated on the DamageDef alone,
a list without ionweapons got a dangling StatDef reference (cross-reference error at load). Every gating conditional
must select nothing when the StatDef is absent and its target when present, checked by evaluating the shipped xpaths
(lxml, XPath 1.0 as RimWorld's XmlDocument) on two synthetic combined-def documents. Red on the pre-wave-76 file."""
import os
import sys

from lxml import etree

HERE = os.path.dirname(os.path.abspath(__file__))
PATCH = os.path.join(HERE, "Patches", "ThirdPartyStunBodySize_Squared.xml")
STAT = "RSW_Jawa_InverseBodySize"
TARGETS = ("guy762_RangedDamage_KOstun", "guy762_RangedDamage_sonic")
FAILS = []


def check(name, cond, detail=""):
    print("%s  %s %s" % ("ok  " if cond else "FAIL", name, "" if cond else detail))
    if not cond:
        FAILS.append(name)


def _defs(with_stat):
    body = "".join("<DamageDef><defName>%s</defName><additionalHediffs><li><hediff>X</hediff></li></additionalHediffs>"
                   "</DamageDef>" % d for d in TARGETS)
    if with_stat:
        body += "<StatDef><defName>%s</defName></StatDef>" % STAT
    return etree.fromstring("<Defs>%s</Defs>" % body)


def problems(patch_root):
    out = []
    ops = [op for op in patch_root.iter("Operation") if op.get("Class") == "PatchOperationConditional"]
    if len(ops) != len(TARGETS):
        return ["expected %d conditionals, found %d" % (len(TARGETS), len(ops))]
    absent, present = _defs(False), _defs(True)
    for op in ops:
        xp = op.findtext("xpath")
        value = etree.tostring(op.find("match"), encoding="unicode")
        if STAT not in value:
            out.append("conditional %s: match no longer writes %s (update this test)" % (xp, STAT))
            continue
        if absent.xpath(xp):
            out.append("gate %s matches with %s absent: writes a dangling StatDef reference" % (xp, STAT))
        if not present.xpath(xp):
            out.append("gate %s selects nothing even with %s present: the op never runs" % (xp, STAT))
    return out


def main():
    root = etree.parse(PATCH).getroot()
    shipped = problems(root)
    check("shipped gates require the DamageDef AND the StatDef", not shipped, "; ".join(shipped))
    # planted break: the pre-wave-76 gate (DamageDef only)
    text = etree.tostring(root, encoding="unicode").replace('/Defs[StatDef[defName="%s"]]/' % STAT, "/Defs/")
    check("break caught: DamageDef-only gate", bool(problems(etree.fromstring(text))), "check stayed clean")
    print("RESULT", "FAIL %d" % len(FAILS) if FAILS else "PASS")
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
