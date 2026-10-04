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


SCALARS_FOR_TEST = ("techLevel", "baseCost", "tab", "researchViewX", "researchViewY")


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
    # ---- retag_rows_vs_dump (RESEARCHRETAG_COVERAGE_GAPS_1 offline half) ----
    exp, targets = v.patch_expectations()
    try:
        rows = v._load_rows()
    except Exception as e:
        rows = None
        print("UNMEASURED  retag rows vs dump: %s" % e)
    if rows:
        import copy
        # VFET_RETAG_ROWS_NOT_HELD_1: 13 VFE Tribals rows were overridden by RR Stepping Stones' compat patch until it joined
        # forceLoadAfter. A dump from before that fix shows ONLY these unheld; the rest of this selftest runs on that dump
        # with the 13 set to their patched values (the post-fix state), so it stays green on either side of the next load.
        vfet13 = frozenset("VFET_" + n for n in ("Fire", "Agriculture", "Cultivation", "Medicine", "AnimalHandling", "Mining",
                                                 "Construction", "Furniture", "Tribalwear", "Hunting", "Weapons", "Bow", "Culture"))
        raw_bad = v.retag_findings(exp, rows)[2]
        check("raw dump: nothing but the 13 VFET rows is unheld (%d findings)" % len(raw_bad),
              all(b.split(".")[0] in vfet13 for b in raw_bad), [b for b in raw_bad if b.split(".")[0] not in vfet13][:3])
        rows = copy.deepcopy(rows)
        for (d, f), w in exp.items():
            if d in vfet13 and d in rows and w != v.REMOVED:
                rows[d]["fields"][f] = w
        held, checked, bad = v.retag_findings(exp, rows)
        check("sanity probe: >= 600 expectations, >= 380 targets, no pinned unheld rows", len(exp) >= 600 and len(targets) >= 380 and len(v.KNOWN_UNHELD) == 0, (len(exp), len(targets)))
        check("shipped patches vs the dump (13 VFET rows at post-fix values): every checked value holds (%d/%d)" % (held, checked), checked >= 300 and not bad, bad[:3])
        check("the 31 prerequisite removals are in the expectations", sum(1 for w in exp.values() if w == v.REMOVED) >= 25, sum(1 for w in exp.values() if w == v.REMOVED))
        check("pinned rows are still unheld", v.unheld_findings(exp, rows) == [], v.unheld_findings(exp, rows))
        check("forceLoadAfter names every owner", v.load_order_findings(targets, rows, v._force_load_after()) == [])
        k, fld = sorted((d, f) for (d, f), w in exp.items() if f == "tab" and d in rows and d not in v.KNOWN_UNHELD)[0]
        r2 = copy.deepcopy(rows)
        r2[k]["fields"]["tab"] = "SomeOtherTab"
        got = v.retag_findings(exp, r2)[2]
        check("break: a tab that did not take is named (%s)" % k, len(got) == 1 and k in got[0], got)
        rm = [d for (d, f), w in exp.items() if w == v.REMOVED and d in rows and d not in v.KNOWN_UNHELD][0]
        r3 = copy.deepcopy(rows)
        r3[rm]["fields"]["prerequisites"] = ["Electricity"]
        got = v.retag_findings(exp, r3)[2]
        check("break: a prerequisite removal that did not take is named (%s)" % rm, any(rm in g for g in got), got)
        numeric = [(d, f) for (d, f), w in exp.items() if f == "baseCost" and d in rows and d not in v.KNOWN_UNHELD][0]
        r4 = copy.deepcopy(rows)
        r4[numeric[0]]["fields"]["baseCost"] = float(r4[numeric[0]]["fields"]["baseCost"]) + 1
        check("break: a baseCost off by one is named (numeric compare, %s)" % numeric[0], len(v.retag_findings(exp, r4)[2]) == 1)
        r5 = copy.deepcopy(rows)
        pin = sorted(vfet13)[0]
        for (d, f), w in exp.items():
            if d == pin and w != v.REMOVED:
                r5[pin]["fields"][f] = w
        check("break: a pinned row that now holds is flagged for un-pinning", any("now HOLDS" in g for g in v.unheld_findings(exp, r5, frozenset([pin]))), v.unheld_findings(exp, r5, frozenset([pin])))
        r6 = copy.deepcopy(rows)
        del r6[pin]
        check("break: a pinned row missing from the dump is flagged", any("not in the dump" in g for g in v.unheld_findings(exp, r6, frozenset([pin]))))
        some_owner = rows[sorted(targets & set(rows))[40]]["packageId"].lower()
        fla = [x for x in v._force_load_after() if x.lower() != some_owner]
        check("break: an owner dropped from forceLoadAfter is named (%s)" % some_owner,
              (some_owner in v.load_order_findings(targets, rows, fla)) or some_owner.startswith("ludeon") or some_owner == "mandrake.rut.researchretag")
        check("break: a planted foreign owner is named", v.load_order_findings({"Electricity", "X_Planted"}, dict(rows, X_Planted={"packageId": "foo.bar"}), []) == ["foo.bar"])
        # the chain, through its own Suite: green, green-with-pre-patch-dump is UNMEASURED, a broken value is red
        import runner
        from northstar_driver.session import FastSession
        from northstar_driver.transport import MockGame, MockTransport

        def chain(mut_rows):
            saved = v._load_rows
            v._load_rows = lambda: mut_rows
            try:
                own = v.Suite("ResearchRetag")
                own.toggles = []
                own.chains = [(n, f) for n, f in v.suite.chains if n == "retag_rows_vs_dump"]
                with FastSession(transport=MockTransport(MockGame()), strict=False) as sess:
                    res = runner.run_suite(own, sess, anchor=None, mod=None)
            finally:
                v._load_rows = saved
            return dict((c["name"], c["verdict"]) for ch in res["chains"] for c in ch["components"])
        got = chain(rows)
        check("clean chain: all five retag bars PASS", sorted(got.values()) == ["PASS"] * 5, got)
        got = chain(r2)
        check("a tab that did not take reddens only the value bar", [n for n, vd in got.items() if vd == "FAIL"] == ["every_retag_value_and_prereq_removal_holds_in_the_dump"], got)
        pre = copy.deepcopy(rows)
        for (d, f), w in exp.items():
            if d in pre and f in SCALARS_FOR_TEST and w != v.REMOVED:
                pre[d]["fields"][f] = "unpatched"
        got = chain(pre)
        check("a dump that predates the patch is UNMEASURED, never PASS", got["dump_was_captured_with_this_patch_applied"] != "PASS", got)
    if FAILS:
        print("\n%d ResearchRetag selftest(s) FAILED" % len(FAILS))
        return 1
    print("\nall ResearchRetag selftests passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
