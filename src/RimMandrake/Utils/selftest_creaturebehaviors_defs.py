#!/usr/bin/env python3
"""Planted-break selftest for check_creaturebehaviors_defs.py. Proves the checker is clean on the real tree (and that
it actually looked: nodes and fields were checked), then plants one break at a time into an in-memory XML and proves
each kind is caught, plus a valid control that must stay clean. A checker that cannot fail proves nothing.

    python3 src/RimMandrake/Utils/selftest_creaturebehaviors_defs.py
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import check_creaturebehaviors_defs as chk  # noqa: E402

FAILED = []


def expect(label, ok, detail=""):
    print("%s %s %s" % ("ok  " if ok else "FAIL", label, detail))
    if not ok:
        FAILED.append(label)


def kinds(cs, xml_text, compiled):
    classes = chk.parse_cs(cs)
    findings = []
    chk.check_xml("<fixture>.xml", xml_text, classes, compiled, findings)
    return {k for k, _p, _l, _m in findings}, findings


def node(body, cls="RM_SandSwimExtension"):
    return ('<Defs><ThingDef><defName>T</defName><modExtensions><li Class="RimMandrake.CreatureBehaviors.%s">%s</li>'
            '</modExtensions></ThingDef></Defs>' % (cls, body))


def main():
    cs, xml, compiled = chk.read_tree()
    classes, findings, unparsed = chk.run(cs, xml, compiled)
    expect("real tree clean", not findings, "%d findings" % len(findings))
    expect("probe: nodes and fields were checked", chk.STATS["nodes"] >= 50 and chk.STATS["fields"] >= 200,
           "%d nodes, %d fields" % (chk.STATS["nodes"], chk.STATS["fields"]))
    expect("probe: sand swim ext requires its two hediffs",
           {"submergedHediff", "swimmerMarkerHediff"} <= set(chk.all_required(classes, "RM_SandSwimExtension")))
    good = "<submergedHediff>A</submergedHediff><swimmerMarkerHediff>B</swimmerMarkerHediff><surfacedTicks>300</surfacedTicks>"
    k, f = kinds(cs, node(good), compiled)
    expect("control: valid node is clean", not k, str(f))
    k, _ = kinds(cs, node(good, "RM_NoSuchExtension"), compiled)
    expect("UNRESOLVED_CLASS caught", "UNRESOLVED_CLASS" in k, str(k))
    k, _ = kinds(cs, node(good.replace("submergedHediff>A</submergedHediff", "submergedHedif>A</submergedHedif")), compiled)
    expect("UNKNOWN_FIELD caught (typo)", "UNKNOWN_FIELD" in k, str(k))
    k, _ = kinds(cs, node("<submergedHediff>A</submergedHediff>"), compiled)
    expect("MISSING_REQUIRED caught", "MISSING_REQUIRED" in k, str(k))
    k, _ = kinds(cs, node(good + "<surfacedTicks>soon</surfacedTicks>"), compiled)
    expect("BAD_VALUE caught (int)", "BAD_VALUE" in k, str(k))
    k, _ = kinds(cs, node(good + "<breachForAnyTarget>maybe</breachForAnyTarget>"), compiled)
    expect("BAD_VALUE caught (bool)", "BAD_VALUE" in k, str(k))
    k, _ = kinds(cs, node(good), {c for c in compiled if c != "RM_SandSwimExtension.cs"})
    expect("NOT_COMPILED caught", "NOT_COMPILED" in k, str(k))
    k, _ = kinds(cs, "<Defs><JobDef><driverClass>RimMandrake.CreatureBehaviors.RM_JobDriver_Nope</driverClass></JobDef></Defs>", compiled)
    expect("UNRESOLVED_CLASS caught in a class-valued element", "UNRESOLVED_CLASS" in k, str(k))
    print("selftest_creaturebehaviors_defs: %s" % ("FAILED " + ", ".join(FAILED) if FAILED else "OK"))
    return 1 if FAILED else 0


if __name__ == "__main__":
    sys.exit(main())
