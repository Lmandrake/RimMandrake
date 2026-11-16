#!/usr/bin/env python3
"""selftest_bar_rule_tuning_numbers.py - a passing bar never pins a tuning number or an asset-variant count
(RIMMANDRAKE_TEACH_JUDGES_BARS_HOLD_NO_TUNING_NUMBERS; owner 2026-11-16, design/RimMandrake/standing_rulings.md
§A passing bar is an experience).

Contagion's coverage judge refused on "every rostered plant's ingestible and yield fields", "the Halfmade Tree resolves
more than one graphic variant" and "one row per inventory special, each with its field and expected value", and graded
each of those criteria `sound` itself. The gate (bar_rule.py, applied inside coverage_judge.run) must not block on those,
and must still block on true experience gaps (a guard is untested until it rejects a broken input and still accepts a
good one). Also: a later look's new gap on material that did not change blocks nothing, and the judge's own grade of its
criterion is not the binding one. The claude call and the signer are stubbed: no network, no model, no real concept."""
import json
import os
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

FAILS = []


def check(name, ok, got=""):
    print("%s %s%s" % ("ok  " if ok else "FAIL", name, "" if ok else "  got: %r" % (got,)))
    if not ok:
        FAILS.append(name)


# Verbatim from design/concepts/Contagion/coverage_verdict.json (judge rm-coverage-judge-1794821839, 2026-11-16).
CONTAGION_YIELD_VARIANT = {
    "what": "The zero-forage nutrition check omits three rostered plants, and Halfmade variant art is unread",
    "where": "tree.json flora_yields_declared",
    "ids": ["flora_yields_declared", "flora_lashgrass", "flora_rattlegrope", "flora_halfmade_blighted",
            "flora_halfmade_tree"],
    "would_pass": "The selftest covers every rostered plant's ingestible and yield fields, and the Halfmade Tree "
                  "resolves more than one graphic variant.",
    "smallest_fix": {"attainable": "yes", "cost": "edit", "what": "tree.json flora_yields_declared scenario"},
    "criterion_verdict": "sound", "criterion_why": "A zero-forage claim needs every rostered plant checked.",
    "observed": "The scenario lists 'Eyebark, Bleedleaf, Gorestalk, Sapblister, Bloody Fist, Halfmade Tree, Meatvine, "
                "Toothmoss and Wombpod'. Lashgrass, Rattlegrope and RM_HalfmadeTreeBlighted (rostered in "
                "RM_Contagion.xml) are missing, and the Halfmade Tree's 'variant art' is never read."}
CONTAGION_FIELD_TABLE = {
    "what": "fauna_specials_declared's table omits the specials of many inventory rows",
    "where": "tree.json fauna_specials_declared",
    "ids": ["fauna_specials_declared", "fauna_doublemaw", "fauna_peeper", "bulloo"],
    "would_pass": "The leaf's table has one row per inventory special, each with its field and expected value, and "
                  "the VEF arms run with VEF loaded or are marked out with a reason.",
    "smallest_fix": {"attainable": "yes", "cost": "edit", "what": "tree.json fauna_specials_declared experience and oracle"},
    "criterion_verdict": "sound", "criterion_why": "Each built special needs a named check.",
    "observed": "Not listed: Doublemaw fast, Peeper docile, Eyestinger heavy ambusher, Bulloo 'zero MeatAmount, light "
                "leather', Blisterfloat leave-map."}
CONTAGION_WORKERS = {
    "what": "waiting_costs_more reads recovery workers it never stages", "where": "scenes.json sc_waiting_costs_more",
    "ids": ["waiting_costs_more"],
    "would_pass": "The start asserts N colonists ordered to the site at each stage, and the action reads their touched "
                  "severity and the manhunters' reach toward them at stage 1 and at stage 2.",
    "smallest_fix": {"attainable": "yes", "cost": "edit",
                     "what": "scenes.json: add the recovery party to sc_waiting_costs_more's start and action"},
    "criterion_verdict": "sound", "criterion_why": "A scene must stage what its expect reads.",
    "observed": "The expect says 'the recovery workers sent to the stage-2 site take more touched exposure than at "
                "stage 1'. The start and action stage no workers."}
CONTAGION_CONTROL = {
    "what": "sc_bodyprints_phased's control expects a slime death from an unnamed native corpse",
    "where": "scenes.json sc_bodyprints_phased", "ids": ["bodyprints", "bodyprints_phased"],
    "would_pass": "The start names the species, and the control expects what today's build does to that corpse (for "
                  "example the corpse rots in place, no skin or print), read from the deployed build.",
    "smallest_fix": {"attainable": "yes", "cost": "edit", "what": "scenes.json sc_bodyprints_phased start and control"},
    "criterion_verdict": "sound", "criterion_why": "A control must be a reachable state that discriminates.",
    "observed": "The start has 'a native corpse in the open', and the control expects 'the old slime death and no "
                "print'. A corpse already exists, so a slime death cannot follow."}


def gate_cases():
    import bar_rule as BR
    for name, g, blocks in (("Contagion yield fields and Halfmade variant count", CONTAGION_YIELD_VARIANT, False),
                            ("Contagion 'each with its field and expected value' table", CONTAGION_FIELD_TABLE, False),
                            ("Contagion recovery workers never staged (a true experience gap)", CONTAGION_WORKERS, True),
                            ("Contagion bodyprints control unreachable (a true experience gap)", CONTAGION_CONTROL, True)):
        b, why = BR.blocks(dict(g))
        check("gate: %s %s" % (name, "blocks" if blocks else "does not block"), b is blocks, (b, why))
    b, _ = BR.blocks(dict(CONTAGION_YIELD_VARIANT, bar_kind="experience"))
    check("gate: a judge calling the yield gap `experience` does not make it block", b is False)
    b, _ = BR.blocks(dict(CONTAGION_WORKERS, bar_kind="declared_data"))
    check("gate: a gap the judge itself files as declared_data is advisory", b is False)
    b, _ = BR.blocks(dict(CONTAGION_WORKERS, new_since="late", miss_of="rm-coverage-judge-1"))
    check("gate: a late gap after a refusing look (new, nothing changed) blocks nothing", b is False)
    b, _ = BR.blocks(dict(CONTAGION_WORKERS, new_since="late"))
    check("gate: a late gap with no refusing look before it still blocks", b is True)
    check("rule text carries the one-sentence test and the named Contagion non-gaps",
          "re-passed after we renormalize" in BR.RULE_TEXT and "more than one graphic variant" in BR.RULE_TEXT
          and "each with its field and expected value" in BR.RULE_TEXT, BR.RULE_TEXT[:200])


def concept(root, name="Foo"):
    import concept_tree as CT
    d = os.path.join(root, "design", "concepts", name)
    os.makedirs(d, exist_ok=True)
    os.makedirs(os.path.join(root, os.path.dirname(CT.OWNER_SHARD)), exist_ok=True)
    files = {
        "stage.json": {"stage": 5, "status": "open", "item": "FOO_ITEM",
                       "budget": {"cap": 4000000, "reserve": 60000, "spent": 0, "charges": []}},
        "record.json": {"inventory": [{"id": "inv_throw", "what": "an explosion throws loose items outward"},
                                      {"id": "inv_plants", "what": "native plants give no forage; the Halfmade Tree "
                                       "has variant art"}]},
        "tree.json": {"kind": "mod", "leaves": [{"id": "leaf_wall", "what": "a wall stops a thrown item"}]},
        "scenes.json": {"scenes": [{"id": "sc_throw", "asserts": "steel lands two cells out"}]},
    }
    for name, obj in files.items():
        with open(os.path.join(d, name), "w") as f:
            json.dump(obj, f)
    with open(os.path.join(d, "sheet.md"), "w") as f:
        f.write("# Foo\n\n## What it does\nA blast throws items; walls stop them.\n")
    return d


ROWS = [{"id": "inv_throw", "evidence": ["record.json", "scenes.json"],
         "parts": [{"what": "items thrown outward", "scene": "sc_throw", "ok": True}]},
        {"id": "inv_plants", "evidence": ["record.json"],
         "parts": [{"what": "every plant's yield fields and the tree's variants", "scene": "", "ok": False}]},
        {"id": "leaf_wall", "evidence": ["tree.json", "sheet.md"],
         "parts": [{"what": "a wall stops a throw", "scene": "", "ok": False}]}]
ROWS_ALL_OK = [dict(r, parts=[dict(p, ok=True) for p in r["parts"]]) for r in ROWS]


def true_gap(**kw):
    g = {"what": "no scene tests the wall stop", "where": "tree.json leaf_wall", "return_to": 3, "ids": ["leaf_wall"],
         "new_since": "first", "bar_kind": "experience", "evidence": ["tree.json", "scenes.json"],
         "observed": "leaf_wall says a wall stops a thrown item; scenes.json has only sc_throw, which has no wall",
         "would_pass": "a scene sc_wall places a wall one cell east of a blast and asserts the steel stack stays west of it",
         "smallest_fix": {"what": "add scene sc_wall to scenes.json with a wall east of the blast and a stack assertion",
                          "attainable": "yes", "cost": "edit"},
         "criterion_verdict": "sound",
         "criterion_why": "The leaf names a behaviour a single staged blast can show, so a scene can pass it."}
    g.update(kw)
    return g


def pedantic_gap(base, **kw):
    g = dict(base, ids=["inv_plants"], return_to=3, new_since="first", bar_kind="experience",
             evidence=["record.json"])
    g.update(kw)
    return g


def answer(verdict, gaps=(), rows=ROWS, session="sess"):
    res = {"structured_output": {"verdict": verdict, "gaps": list(gaps), "reasons": "r", "checklist": list(rows)},
           "usage": {"input_tokens": 10, "output_tokens": 2, "cache_read_input_tokens": 0,
                     "cache_creation_input_tokens": 0}, "session_id": session}
    return json.dumps(res)


def script(answers):
    def r(argv, cwd, env, timeout):
        return 0, answers.pop(0)
    return r


def run_cases():
    import concept_tree as CT
    import coverage_judge as CJ
    import designer_stage as DS
    DS.owner_away = lambda: (False, "selftest: attended")
    CT.coverage_problem = lambda d, repo, tree: "no coverage signature"
    DS.exam_errors = lambda ex, d, st, repo=None: []
    CT.sign = lambda d, by, repo=None, **kw: []
    CJ.NOT_COVERED_LIMIT = CJ.JUDGE_RUNS_MAX = 10 ** 6
    CJ.JUDGE_SPEND_MAX = 10 ** 15
    real_delta = CJ.delta_plan
    with tempfile.TemporaryDirectory() as root:
        ops = os.path.join(root, "ops")
        os.makedirs(ops)
        os.environ.update(RM_REFUSAL_DIR=os.path.join(root, "refusals"), RM_OPS_WATCH_DIR=ops,
                          RM_DISPATCHER_STATE=os.path.join(root, "dispatcher"))
        gp = CJ.SCHEMA["properties"]["gaps"]["items"]
        check("the judge's schema asks every gap for its bar_kind", "bar_kind" in gp["required"], gp["required"])
        CJ.delta_plan = lambda d, prior, read=None: None   # full judges first
        d = concept(root)
        text = CJ.prompt(d, root, ["inv_throw"], False, 1)
        check("the judge's prompt carries the bar rule", "re-passed after we renormalize" in text, text[:300])

        # 1. a look whose only gaps are the Contagion yield/variant and field-table kinds does not block
        rec, _ = CJ.run(d, root, script([answer("not_covered", [
            pedantic_gap(CONTAGION_YIELD_VARIANT), pedantic_gap(CONTAGION_FIELD_TABLE, ids=["inv_plants"])],
            rows=[ROWS[0], ROWS[1], ROWS_ALL_OK[2]])]))
        st = DS.load_state(d)
        check("run: only tuning/variant/field-table gaps -> no blocking gap, verdict covered",
              rec["verdict"] == "covered" and not rec.get("gaps") and len(rec.get("advisory_gaps") or []) == 2,
              (rec.get("verdict"), len(rec.get("gaps") or []), len(rec.get("advisory_gaps") or [])))
        check("run: that look is not counted as a not_covered round",
              (st.get("coverage_rounds") or [{}])[-1].get("verdict") == "covered", st.get("coverage_rounds"))

        # 2. the same pedantry beside a true experience gap: the true gap still blocks, alone
        d = concept(root, "Foo2")
        rec, _ = CJ.run(d, root, script([answer("not_covered", [pedantic_gap(CONTAGION_YIELD_VARIANT), true_gap()])]),
                        reader=None)
        check("run: a true experience gap still blocks (not_covered, one gap, one advisory)",
              rec["verdict"] == "not_covered" and [g.get("ids") for g in rec.get("gaps") or []] == [["leaf_wall"]]
              and len(rec.get("advisory_gaps") or []) == 1, (rec.get("verdict"), rec.get("gaps"),
                                                             rec.get("advisory_gaps")))
        refs = (rec.get("contract") or {})
        check("run: the contract accepted the blocking refusal record", refs.get("ok") is True, refs)

        # 3. the judge does not grade its own criterion: a second reader does, and its verdict binds
        d = concept(root, "Foo3")
        seen = []

        def reader(items):
            seen.append(items)
            return [{"criterion_verdict": "flawed", "criterion_why": "the leaf asks for a wall the mod never builds",
                     "bar_kind": "experience"} for _ in items]
        rec, _ = CJ.run(d, root, script([answer("not_covered", [true_gap()])]), reader=reader)
        g = (rec.get("gaps") or [{}])[0]
        check("run: the second reader saw the blocking gap and not the judge's own grade",
              len(seen) == 1 and len(seen[0]) == 1 and "criterion_verdict" not in seen[0][0], seen)
        check("run: the binding criterion_verdict is the second reader's; the judge's is kept as its opinion",
              g.get("criterion_verdict") == "flawed" and g.get("judge_criterion_verdict") == "sound"
              and g.get("criterion_by") == "second_reader", g)
        check("run: a criterion the second reader faults goes to the neutral fixer (criteria_suspect)",
              rec.get("criteria_suspect") == ["leaf_wall"], rec.get("criteria_suspect"))

        # 4. a second reader that cannot answer leaves the refusal binding nothing
        d = concept(root, "Foo4")
        rec, _ = CJ.run(d, root, script([answer("not_covered", [true_gap()])]), reader=lambda items: None)
        check("run: no second read -> the refusal is advisory, the Designer is not sent back",
              rec["verdict"] == "not_covered" and "second reader" in str(rec.get("advisory")) and CJ.stop_exit(rec),
              rec.get("advisory"))

        # 5. a later look may not raise a new gap on material that did not change
        CJ.delta_plan = real_delta
        d = concept(root, "Foo5")
        rec, _ = CJ.run(d, root, script([answer("not_covered", [true_gap()])]), reader=None)
        late = true_gap(ids=["inv_throw"], what="the throw distance is unread", new_since="late",
                        late_why="the earlier pass did not read sc_throw's distance claim",
                        where="scenes.json sc_throw",
                        observed="sc_throw asserts steel lands two cells out; record says an explosion throws items",
                        would_pass="sc_throw also asserts the stack is thrown away from the blast centre on two sides")
        fixes = {"against": rec["judge"], "claims": [{"gap": "g1", "evidence": "scenes.json sc_wall added"}]}
        with open(os.path.join(d, CJ.FIXES_FILE), "w") as f:
            json.dump(fixes, f)
        rec2, _ = CJ.run(d, root, script([answer("not_covered", [late], rows=ROWS_ALL_OK)]), reader=None)
        check("run: a new gap on unchanged material at a later look is advisory (a miss), not a blocking gap",
              not rec2.get("gaps") and any(a.get("ids") == ["inv_throw"] for a in rec2.get("advisory_gaps") or []),
              (rec2.get("verdict"), rec2.get("gaps"), rec2.get("advisory_gaps"), rec2.get("dropped")))


def main():
    env = {k: os.environ.get(k) for k in ("RM_REFUSAL_DIR", "RM_OPS_WATCH_DIR", "RM_DISPATCHER_STATE")}
    try:
        try:
            gate_cases()
        except ImportError as e:
            check("bar_rule importable", False, str(e))
        try:
            run_cases()
        except TypeError as e:   # run() without a reader parameter: the pre-fix code
            check("coverage_judge.run takes a second reader", False, str(e))
    finally:
        for k, v in env.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v
    print("%s: %d failure(s)" % ("FAIL" if FAILS else "PASS", len(FAILS)))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
