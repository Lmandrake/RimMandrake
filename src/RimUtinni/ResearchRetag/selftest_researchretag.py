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
    # hearth_layout_static (LOAD13_CONFIGERRORS_TRIAGE_1)
    ov = v.patched_view_coords()
    check("patch coord parse sees the Hearth layout ops (AdvancedShowers 2,1; VCE_CondimentsResearch y 0.6)",
          ov.get("AdvancedShowers") == {"researchViewX": 2.0, "researchViewY": 1.0}
          and ov.get("VCE_CondimentsResearch", {}).get("researchViewY") == 0.6, ov.get("AdvancedShowers"))
    check("break overlap: two nodes 0.2 apart in a column are reported",
          len(v.tab_overlaps([("A", 0, 0), ("B", 0, 0.2), ("C", 0, 1)])) == 1)
    check("float edge: 4.9 vs 5.15 counts as overlap (float32 box edge)",
          len(v.tab_overlaps([("A", 0, 4.9), ("B", 0, 5.15)])) == 1)
    try:
        import json
        import game_paths as GP
        rows = json.load(open(os.path.join(GP.DEF_DUMP, "defs", "ResearchProjectDef.json")))["defs"]
    except Exception as e:
        rows = None
        print("UNMEASURED  shipped Hearth layout vs def dump: %s" % e)
    if rows:
        nodes = v.effective_tab_nodes(rows, "RUT_Tree_Hearth", ov)
        check("shipped Hearth layout: no overlapping nodes", len(nodes) >= 20 and not v.tab_overlaps(nodes), v.tab_overlaps(nodes)[:4])
        raw = v.effective_tab_nodes(rows, "RUT_Tree_Hearth", {})
        # The dump may be captured BEFORE or AFTER our coordinate ops applied (load 14's capture is after). Detect which from
        # the dump's own values: post-patch means the dump already carries our coordinates, so 'without our ops' is clean too
        # and cannot serve as the control; the control then becomes a planted collision on the real dump nodes.
        raw_by = {n[0]: (n[1], n[2]) for n in raw}
        post = all(raw_by.get(d) == (c["researchViewX"], c["researchViewY"]) for d, c in ov.items() if d in raw_by and d in ("AdvancedShowers",))
        print("dump is %s our Hearth coordinate ops" % ("AFTER" if post else "BEFORE"))
        if post:
            check("post-patch dump already carries our coordinates (live evidence the ops applied)", post and "AdvancedShowers" in raw_by)
            a, b = nodes[0], nodes[1]
            planted = [(a[0], a[1], a[2]), (b[0], a[1], a[2] + 0.1)]
            planted_all = [n for n in nodes if n[0] != b[0]] + [planted[1]]
            check("break (control): planting one node 0.1 off another in the real dump's Hearth layout is reported",
                  len(v.tab_overlaps(planted_all)) > 0)
        else:
            check("break: without our coordinate ops the dump's Hearth overlaps (control)", len(v.tab_overlaps(raw)) > 0)
    if FAILS:
        print("\n%d ResearchRetag selftest(s) FAILED" % len(FAILS))
        return 1
    print("\nall ResearchRetag selftests passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
