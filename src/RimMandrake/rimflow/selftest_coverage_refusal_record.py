#!/usr/bin/env python3
"""selftest_coverage_refusal_record.py - the coverage judge emits refusal records and its launcher checks them
(RIMMANDRAKE_EMIT_REFUSAL_RECORDS_FROM_JUDGE_BRIEFS, T4 of the refusal contract,
design/specs/2026-11-12-refusal-contract-for-judges-and-gates.md section 1).

A not_covered verdict whose gaps carry no attainable path to pass is refused itself: it is re-asked once in the same
session with the check's errors, and a second malformed answer is recorded as `malformed`, never as not_covered, so it
does not send the Designer back and does not count toward the third-refusal stop; two malformed rounds stop judging (the
brief FAILED). A well-formed verdict is stored whole in the contract's store. The claude call and the signer are stubbed:
no network, no model, no real concept is touched."""
import json
import os
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import concept_tree as CT  # noqa: E402
import coverage_judge as CJ  # noqa: E402
import designer_stage as DS  # noqa: E402
import refusal_contract as RC  # noqa: E402

FAILS = []


def check(name, ok, got=""):
    print("%s %s%s" % ("ok  " if ok else "FAIL", name, "" if ok else "  got: %r" % (got,)))
    if not ok:
        FAILS.append(name)


def concept(root, item="FOO_ITEM"):
    d = os.path.join(root, "design", "concepts", "Foo")
    os.makedirs(d, exist_ok=True)
    os.makedirs(os.path.join(root, os.path.dirname(CT.OWNER_SHARD)), exist_ok=True)
    files = {
        "stage.json": {"stage": 5, "status": "open", "item": item,
                       "budget": {"cap": 4000000, "reserve": 60000, "spent": 0, "charges": []}},
        "record.json": {"inventory": [{"id": "inv_throw", "what": "an explosion throws loose items outward"}]},
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
        {"id": "leaf_wall", "evidence": ["tree.json", "sheet.md"],
         "parts": [{"what": "a wall stops a throw", "scene": "", "ok": False}]}]


def good_gap(**kw):
    g = {"what": "no scene tests the wall stop", "where": "tree.json leaf_wall", "return_to": 3, "ids": ["leaf_wall"],
         "new_since": "first", "evidence": ["tree.json", "scenes.json"],
         "observed": "leaf_wall says a wall stops a thrown item; scenes.json has only sc_throw, which has no wall",
         "would_pass": "a scene sc_wall places a wall one cell east of a blast and asserts the steel stack stays west of it",
         "smallest_fix": {"what": "add scene sc_wall to scenes.json with a wall east of the blast and a stack assertion",
                          "attainable": "yes", "cost": "edit"},
         "criterion_verdict": "sound",
         "criterion_why": "The leaf names a behaviour a single staged blast can show, so a scene can pass it."}
    g.update(kw)
    return g


def first_look(d):
    """Make the next run a first look on this concept (no prior verdict, so no repair slots): the records these cases
    test are a first look's. On a later look an earlier gap is a numbered slot and blocks as first written, so a
    re-reported gap is not re-validated (design/specs/2026-11-17-judge-flaws-not-polish/7_same_problem_rule.md)."""
    try:
        os.remove(os.path.join(d, CJ.VERDICT_FILE))
    except FileNotFoundError:
        pass


def bad_gap():
    return good_gap(would_pass="does not pass", smallest_fix={"what": "needs more work", "attainable": "maybe",
                                                              "cost": "edit"})


def answer(verdict, gaps=(), rows=ROWS, session="sess"):
    res = {"structured_output": {"verdict": verdict, "gaps": list(gaps), "reasons": "r", "checklist": list(rows)},
           "usage": {"input_tokens": 10, "output_tokens": 2, "cache_read_input_tokens": 0,
                     "cache_creation_input_tokens": 0}}
    if session:
        res["session_id"] = session
    return json.dumps(res)


def script(answers, argvs):
    def r(argv, cwd, env, timeout):
        argvs.append(argv)
        return 0, answers.pop(0)
    return r


def main():
    CJ.delta_plan = lambda d, prior, read=None: None   # the full judge; the delta judge shares the record text
    DS.owner_away = lambda: (False, "selftest: attended")
    saved = (CT.coverage_problem, CT.sign, DS.exam_errors, RC.status)
    RC.status = lambda family: "CALIBRATED"  # calibration transitions have their own selftest
    CT.coverage_problem = lambda d, repo, tree: "no coverage signature"
    DS.exam_errors = lambda ex, d, st, repo=None: []
    CT.sign = lambda d, by, repo=None, **kw: []
    # one concept is judged several times here: the not_covered and run limits are selftest_coverage_judge_loop's,
    # lifted so only the malformed limit can stop these cases
    CJ.NOT_COVERED_LIMIT = CJ.JUDGE_RUNS_MAX = 10 ** 6
    CJ.JUDGE_SPEND_MAX = 10 ** 15
    env = {k: os.environ.get(k) for k in ("RM_REFUSAL_DIR", "RM_OPS_WATCH_DIR", "RM_DISPATCHER_STATE")}
    try:
        with tempfile.TemporaryDirectory() as root:
            ops = os.path.join(root, "ops")
            os.makedirs(ops)
            os.environ.update(RM_REFUSAL_DIR=os.path.join(root, "refusals"), RM_OPS_WATCH_DIR=ops,
                              RM_DISPATCHER_STATE=os.path.join(root, "dispatcher"))
            gp = CJ.SCHEMA["properties"]["gaps"]["items"]
            check("the schema makes every gap a refusal record",
                  all(f in gp["required"] for f in ("evidence", "observed", "would_pass", "smallest_fix",
                                                    "criterion_verdict", "criterion_why")), gp["required"])
            check("the schema asks each checklist row for its evidence",
                  "evidence" in CJ.SCHEMA["properties"]["checklist"]["items"]["required"])
            d = concept(root)
            argvs = []
            rec, _ = CJ.run(d, root, script([answer("not_covered", [good_gap()])], argvs))
            first = argvs[0][argvs[0].index("-p") + 1]
            check("the prompt asks for would_pass, smallest_fix and a verdict on the criterion itself",
                  all(w in first for w in ("would_pass", "smallest_fix", "criterion_verdict")), first[-600:])
            check("a well-formed not_covered stands, one call, the contract accepted it",
                  rec["verdict"] == "not_covered" and len(argvs) == 1 and rec["contract"]["ok"]
                  and not rec.get("malformed"), rec.get("contract"))
            check("a well-formed not_covered reflects its brief calibration (selftest_judge_calibration tests both)",
                  bool(rec.get("advisory")) == RC.advisory(CJ.CONTRACT_FAMILY) and CJ.stop_exit(rec) is bool(
                      rec.get("advisory")), (rec.get("advisory"), RC.status(CJ.CONTRACT_FAMILY)))
            rows = [json.loads(x) for x in open(os.path.join(root, "refusals", "refusals.jsonl"))]
            check("the refusal is stored whole in the contract store, clause leaf_wall",
                  any(r.get("kind") == "refusal" and r["record"]["clause"] == "leaf_wall"
                      and r["record"]["would_pass"] == good_gap()["would_pass"] for r in rows), rows[-1:])

            # An observed text far past any old cut is stored whole (new evidence content, so no repeat-cache hit).
            long_obs = "leaf_wall: a wall stops a thrown item, no scene " + "x" * 5000   # 2+ words of its evidence
            with open(os.path.join(d, "scenes.json"), "w") as f:
                json.dump({"scenes": [{"id": "sc_throw", "asserts": "steel lands three cells out"}]}, f)
            os.remove(os.path.join(d, CJ.VERDICT_FILE))
            rec, _ = CJ.run(d, root, script([answer("not_covered", [good_gap(observed=long_obs, new_since="unfixed")])],
                                            []))
            rows = [json.loads(x) for x in open(os.path.join(root, "refusals", "refusals.jsonl"))]
            check("a 5000-character observation is stored whole",
                  any(r.get("record", {}).get("observed") == long_obs for r in rows), [len(str(r)) for r in rows])

            # Malformed, then fixed on the re-ask in the same session.
            argvs = []
            first_look(d)   # a later look checks repair slots, not records (7_same_problem_rule.md rule 3)
            rec, _ = CJ.run(d, root, script([answer("not_covered", [bad_gap()]),
                                             answer("not_covered", [good_gap(new_since="unfixed")])], argvs))
            check("a malformed refusal is re-asked once, same session, with the check's errors",
                  len(argvs) == 2 and argvs[1][argvs[1].index("--resume") + 1] == "sess"
                  and "would_pass says nothing checkable" in argvs[1][argvs[1].index("-p") + 1], argvs[1][argvs[1].index("-p") + 1][:400] if len(argvs) > 1 else argvs)
            check("fixed on the re-ask -> the not_covered stands", rec["verdict"] == "not_covered"
                  and rec["contract"]["ok"], rec.get("contract"))

            # A fresh concept: on the one above, a gap on new ids at a later look over unchanged material is `late` and
            # advisory (bar_rule.blocks, RIMMANDRAKE_TEACH_JUDGES_BARS_HOLD_NO_TUNING_NUMBERS), so it never reaches
            # the record check these cases test. It has its own item too: the contract counts refusals per item, and
            # this first look's `first` gaps were refused after FOO_ITEM's two counted ones.
            d = concept(os.path.join(root, "rows"), item="FOO_ROWS_ITEM")
            # RIMMANDRAKE_SPEND_PYRELANDS_LOOK_ON_MALFORMED_REFUSAL: one broken record must not void a whole look.
            # The re-ask names only the broken records (the gaps schema), with the checker's complaint and the text
            # the record cites; the well-formed rows stand.
            throw_bad = good_gap(ids=["inv_throw"], evidence=["sheet.md:1"], what="the throw scene reads no distance",
                                 observed="the range reading is missing; nobody measures distance",
                                 new_since="unfixed")
            throw_ok = dict(throw_bad, evidence=["record.json", "scenes.json"],
                            observed="record.json inv_throw says items are thrown outward; sc_throw asserts steel lands")
            argvs = []
            rec, _ = CJ.run(d, root, script([answer("not_covered", [good_gap(new_since="unfixed"), throw_bad]),
                                             json.dumps({"structured_output": {"gaps": [throw_ok]},
                                                         "session_id": "sess"})], argvs))
            ask2 = argvs[1][argvs[1].index("-p") + 1] if len(argvs) > 1 else ""
            check("bad row fixed on re-ask: one row re-ask, only the broken record, its complaint and its cited text",
                  len(argvs) == 2 and "observed quotes no token of its evidence" in ask2 and "# Foo" in ask2
                  and "leaf_wall" not in ask2 and '"gaps"' in argvs[1][argvs[1].index("--json-schema") + 1]
                  and '"checklist"' not in argvs[1][argvs[1].index("--json-schema") + 1], ask2[:500])
            check("bad row fixed on re-ask: both refusals stand, the contract accepts the whole look",
                  rec["verdict"] == "not_covered" and rec["contract"]["ok"] and not rec.get("malformed_rows")
                  and sorted(i for g in rec["gaps"] for i in g["ids"]) == ["inv_throw", "leaf_wall"],
                  (rec.get("verdict"), rec.get("malformed"), [g["ids"] for g in rec.get("gaps") or []], rec.get("contract"), rec.get("malformed_rows")))

            # One bad row that stays bad: bounded re-asks, then the well-formed row is the stored verdict and the
            # broken one is kept on file marked malformed (the evidence rule is not loosened: it is not submitted).
            argvs = []
            first_look(d)   # a later look checks repair slots, not records (7_same_problem_rule.md rule 3)
            rec, msg = CJ.run(d, root, script([answer("not_covered", [good_gap(new_since="unfixed"), throw_bad])]
                                              + [json.dumps({"structured_output": {"gaps": [throw_bad]},
                                                             "session_id": "sess"})] * CJ.ROW_REASK_MAX, argvs))
            bad_rows = [g for g in rec.get("gaps") or [] if g.get("malformed")]
            check("one bad row: re-asked at most ROW_REASK_MAX times, then the look is kept",
                  len(argvs) == 1 + CJ.ROW_REASK_MAX and rec["verdict"] == "not_covered", (len(argvs), rec["verdict"]))
            check("one bad row: it is marked malformed with the checker's words; the good row is the stored refusal",
                  [g["ids"] for g in bad_rows] == [["inv_throw"]]
                  and "observed quotes no token" in " ".join(bad_rows[0]["malformed"])
                  and [r["clause"] for r in rec.get("malformed_rows") or []] == ["inv_throw"]
                  and rec["contract"]["ok"] and not rec.get("malformed") and CJ.stop_exit(rec) is bool(
                      rec.get("advisory")), (rec.get("malformed_rows"), rec.get("contract"), msg))
            rows = [json.loads(x) for x in open(os.path.join(root, "refusals", "refusals.jsonl"))]
            check("one bad row: the broken record never reaches the contract store as a refusal",
                  not any(r.get("kind") == "refusal" and r["record"]["clause"] == "inv_throw"
                          and r["record"]["observed"] == throw_bad["observed"] for r in rows), rows[-1:])

            # Every row bad, every re-ask too: refused itself; never a not_covered; stops the Designer's run start.
            st0 = DS.load_state(d)
            nc0 = sum(1 for r in st0.get("coverage_rounds") or [] if r.get("verdict") == "not_covered")
            argvs = []
            first_look(d)   # a later look checks repair slots, not records (7_same_problem_rule.md rule 3)
            rec, msg = CJ.run(d, root, script([answer("not_covered", [bad_gap()])]
                                              + [answer("not_covered", [bad_gap()])] * CJ.ROW_REASK_MAX, argvs))
            check("all rows bad: bounded re-asks, then the whole look is malformed",
                  len(argvs) == 1 + CJ.ROW_REASK_MAX and not rec.get("malformed_rows"), len(argvs))
            st1 = DS.load_state(d)
            nc1 = sum(1 for r in st1.get("coverage_rounds") or [] if r.get("verdict") == "not_covered")
            check("malformed twice -> verdict `malformed`, the errors on file, not signed",
                  rec["verdict"] == "malformed" and rec.get("malformed") and not rec["signed"], rec.get("malformed"))
            check("a malformed verdict does not count as a not_covered round", nc1 == nc0, (nc0, nc1))
            check("a malformed verdict stops the Designer's run from starting (exit 3)", CJ.stop_exit(rec) is True, msg)
            check("the malformed verdict is stored with its errors", any(
                json.loads(x).get("kind") == "malformed"
                for x in open(os.path.join(root, "refusals", "refusals.jsonl"))))

            # No session to resume: malformed at once.
            first_look(d)   # a later look checks repair slots, not records (7_same_problem_rule.md rule 3)
            rec, _ = CJ.run(d, root, script([answer("not_covered", [bad_gap()], session=None)], []))
            check("a second malformed round stops judging: the brief FAILED",
                  rec["verdict"] == "malformed" and "malformed" in (rec.get("stopped") or ""), rec.get("stopped"))
            check("stop_reason names the malformed limit",
                  "malformed" in (CJ.stop_reason(DS.load_state(d), d) or ""), CJ.stop_reason(DS.load_state(d), d))

            # A flawed criterion is surfaced for the neutral fixer, not counted as the item's failure alone.
            d2 = concept(os.path.join(root, "two"))
            rec, _ = CJ.run(d2, os.path.join(root, "two"), script([answer("not_covered", [good_gap(
                criterion_verdict="unattainable",
                criterion_why="No scene can show a wall stop because walls are not spawnable on the test map.")])], []))
            check("a flawed or unattainable criterion is listed for the criteria fixer",
                  rec.get("criteria_suspect") == ["leaf_wall"], rec.get("criteria_suspect"))

            # A gap on no single row is clause `rest`; a gap naming an id that is no row or leaf is malformed.
            d3 = concept(os.path.join(root, "three"))
            g_rest = good_gap(ids=[], evidence=["sheet.md", "tree.json", "scenes.json"],
                              observed="the sheet says walls stop them but no scene has a wall")
            rows3 = [dict(ROWS[0]), dict(ROWS[1], parts=[{"what": "a wall stops a throw", "scene": "sc_throw", "ok": True}])]
            v, given = CJ.contract_verdict(d3, {"verdict": "not_covered", "gaps": [g_rest], "checklist": rows3}, "FOO")
            check("a gap on no single row refuses clause `rest`",
                  [r["clause"] for r in v["refusals"]] == [CJ.REST_CLAUSE] and not RC.check(v, given), RC.check(v, given))
            v, given = CJ.contract_verdict(d3, {"verdict": "not_covered", "gaps": [good_gap(ids=["no_such_id"])],
                                                "checklist": rows3}, "FOO")
            check("a gap naming an id that is no inventory row or leaf is malformed",
                  any("not in the criterion set" in e for e in RC.check(v, given)), RC.check(v, given))
            v, given = CJ.contract_verdict(d3, {"verdict": "covered", "gaps": [], "checklist": rows3}, "FOO")
            check("a covered verdict is a well-formed contract verdict with no refusals",
                  v["refusals"] == [] and not RC.check(v, given), RC.check(v, given))
    finally:
        CT.coverage_problem, CT.sign, DS.exam_errors, RC.status = saved
        for k, v in env.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v
    print("selftest_coverage_refusal_record: %s" % ("PASS" if not FAILS else "FAIL (%d)" % len(FAILS)))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
