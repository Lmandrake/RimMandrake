"""selftest_researchretag.py -- the own_prereq_graph_static bar reddens on each break it exists to catch.

Breaks are planted in a copy of the parsed graph (never the shipped XML): a two-project cycle, a prerequisite
naming no loaded project, and a blind parse. The shipped graph must be clean against the def dump.
"""
import importlib.util
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
UTILS = os.path.join(HERE, "..", "..", "RimMandrake", "Utils")
for p in (UTILS,):
    if p not in sys.path:
        sys.path.insert(0, p)

FAILS = []


def check(name, cond, detail=""):
    print("%s  %s %s" % ("ok  " if cond else "FAIL", name, "" if cond else detail))
    if not cond:
        FAILS.append(name)


def main():
    spec = importlib.util.spec_from_file_location("rr_v", os.path.join(HERE, "validation.py"))
    v = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(v)
    g = v.own_prereq_graph()
    check("own graph parses (>= 15 projects, RR_LateralThinking, some prerequisites)",
          len(g) >= 15 and "RR_LateralThinking" in g and any(g.values()), len(g))
    known = set(p for ps in g.values() for p in ps) | {"Electricity"}     # mock load: every named prereq exists
    check("clean graph: no cycle, nothing dangling", v.prereq_findings(g, known) == ([], []), v.prereq_findings(g, known))
    cyc = dict((k, list(ps)) for k, ps in g.items())
    cyc["RR_LateralThinking"].append("RR_Organization")
    cyc["RR_Organization"].append("RR_LateralThinking")
    c, d = v.prereq_findings(cyc, known)
    check("break cycle: reported, nothing dangling", len(c) == 1 and not d, (c, d))
    dang = dict((k, list(ps)) for k, ps in g.items())
    dang["RR_Organization"].append("NoSuchProject_X")
    c, d = v.prereq_findings(dang, known)
    check("break dangling: named exactly", d == ["RR_Organization -> NoSuchProject_X"] and not c, (c, d))
    gone = sorted(set(p for ps in g.values() for p in ps if p not in g))
    c, d = v.prereq_findings(g, set())
    check("break empty load: every external prerequisite dangles", len(d) == sum(1 for ps in g.values() for p in ps if p not in g) and gone, d)
    if FAILS:
        print("\n%d ResearchRetag selftest(s) FAILED" % len(FAILS))
        return 1
    print("\nall ResearchRetag selftests passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
