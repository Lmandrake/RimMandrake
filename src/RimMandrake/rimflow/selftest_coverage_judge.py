#!/usr/bin/env python3
"""selftest_coverage_judge.py - coverage_judge.py (CONCEPT_LOCK_UNBLOCK_SIGNER_NEVER_CALLED): it judges only a concept at
stage 5 whose exam passed and that carries no valid signature; it signs only on a well-formed `covered` verdict over an
unchanged tree and sheet, as a coverage judge unit; and the role launcher adds it as the pre-launch step of a Designer run
at stage 5 and at no other stage. The claude call, the ledger write and the gate's inputs are stubbed: no network,
no model, no real concept is touched."""
import json
import os
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import concept_tree as CT  # noqa: E402
import coverage_judge as CJ  # noqa: E402
import designer_stage as DS  # noqa: E402
import role_launch as RL  # noqa: E402

FAILS = []


def check(name, ok, got=""):
    print("%s %s%s" % ("ok  " if ok else "FAIL", name, "" if ok else "  got: %r" % (got,)))
    if not ok:
        FAILS.append(name)


def concept(root, stage=5, status="open"):
    d = os.path.join(root, "design", "concepts", "Foo")
    os.makedirs(d, exist_ok=True)
    os.makedirs(os.path.join(root, os.path.dirname(CT.OWNER_SHARD)), exist_ok=True)
    with open(os.path.join(d, "stage.json"), "w") as f:
        json.dump({"stage": stage, "status": status, "item": "FOO_ITEM", "budget": {"cap": 4000000, "reserve": 60000, "spent": 0, "charges": []}}, f)
    with open(os.path.join(d, "tree.json"), "w") as f:
        json.dump({"kind": "mod", "leaves": []}, f)
    with open(os.path.join(d, "sheet.md"), "w") as f:
        f.write("sheet\n")
    return d


def answer(verdict, gaps=(), tokens=True, checklist=None):
    res = {"structured_output": {"verdict": verdict, "gaps": list(gaps), "reasons": "r", "checklist": checklist or []},
           "session_id": "sess"}
    if tokens:
        res["usage"] = {"input_tokens": 10, "output_tokens": 2, "cache_read_input_tokens": 0,
                        "cache_creation_input_tokens": 0}
    return json.dumps(res)


def row(i, ok=True, scene="sc_a"):
    return {"id": i, "parts": [{"what": "part of %s" % i, "scene": scene, "ok": ok}]}


def one_pass(root, calls, runner_of, signed):
    """DESIGNER_GAPJUDGE_FIX_ONE_BATCH_PER_ROUND: every owed row in the first answer, or a re-ask, or never signed."""
    d = concept(os.path.join(root, "onepass"))
    with open(os.path.join(d, "record.json"), "w") as f:
        json.dump({"inventory": [{"id": "inv_a", "what": "a"}, {"id": "inv_b", "what": "b"}]}, f)
    with open(os.path.join(d, "tree.json"), "w") as f:
        json.dump({"kind": "mod", "leaves": [{"id": "leaf_c"}, {"id": "inv_a"}]}, f)
    del signed[:]
    check("the owed ids are the inventory then the leaves, once each",
          CJ.required_ids(d, CT.load(d)) == ["inv_a", "inv_b", "leaf_c"], CJ.required_ids(d, CT.load(d)))
    full = [row("inv_a"), row("inv_b"), row("leaf_c")]

    n = len(calls)
    rec, _ = CJ.run(d, os.path.join(root, "onepass"), runner_of(answer("covered", checklist=full)))
    first = calls[n][0][2]
    check("the prompt names every owed id and says one pass lists every gap",
          all(i in first for i in ("inv_a", "inv_b", "leaf_c")) and "EVERY gap" in first, first[-400:])
    check("a first judge is not told of a previous verdict", "previous judge" not in first, first[-300:])
    check("the schema refuses an answer with no checklist and a gap with no ids",
          "checklist" in CJ.SCHEMA["required"]
          and "ids" in CJ.SCHEMA["properties"]["gaps"]["items"]["required"])
    check("all rows, none failed -> signed, one call, checklist on file",
          rec["signed"] and len(calls) == n + 1 and rec["checklist"] == full and "unchecked" not in rec, rec)

    # A missing row is re-asked once, in the same session.
    os.remove(os.path.join(d, CJ.VERDICT_FILE))
    answers = [answer("covered", checklist=full[:2]), answer("covered", checklist=full)]
    argvs = []

    def script(argv, cwd, env, timeout):
        argvs.append(argv)
        return 0, answers.pop(0)
    del signed[:]
    rec, _ = CJ.run(d, os.path.join(root, "onepass"), script)
    check("a missing row -> one re-ask, same session, naming only that row",
          len(argvs) == 2 and argvs[1][argvs[1].index("--resume") + 1] == "sess" and "leaf_c" in argvs[1][2]
          and "inv_a" not in argvs[1][2] and rec["reasked"] == ["leaf_c"], argvs[1:])
    check("answered on the re-ask -> signed", rec["signed"] and signed and "unchecked" not in rec, rec)
    check("both calls are charged", rec["tokens"] == 2 * RL.run_tokens(json.loads(answer("covered"))), rec.get("tokens"))

    # Still missing: a covered verdict never signs; a not_covered one stays actionable.
    os.remove(os.path.join(d, CJ.VERDICT_FILE))
    answers[:] = [answer("covered", checklist=full[:2]), answer("covered", checklist=full[:2])]
    del argvs[:], signed[:]
    rec, _ = CJ.run(d, os.path.join(root, "onepass"), script)
    check("covered, still missing a row after one re-ask -> not signed, no third call",
          not rec["signed"] and not signed and len(argvs) == 2 and rec["unchecked"] == ["leaf_c"] and rec.get("error"), rec)
    gap = {"what": "w", "where": "x", "return_to": 3, "ids": ["inv_a"]}
    answers[:] = [answer("not_covered", [gap], checklist=[row("inv_a", False, "")]),
                  answer("not_covered", [gap], checklist=[row("inv_a", False, "")])]
    rec, _ = CJ.run(d, os.path.join(root, "onepass"), script)
    check("not_covered, rows still missing -> gaps stand, the rest on file as unchecked",
          rec["verdict"] == "not_covered" and bare(rec["gaps"]) == [gap] and rec["unchecked"] == ["inv_b", "leaf_c"] and not rec["signed"], rec)
    answers[:] = [answer("covered", checklist=full[:2]), "not json"]
    rec, _ = CJ.run(d, os.path.join(root, "onepass"), script)
    check("a broken re-ask leaves the first answer, not signed",
          not rec["signed"] and rec["unchecked"] == ["leaf_c"], rec)
    no_session = json.loads(answer("covered", checklist=full[:2]))
    del no_session["session_id"]
    rec, _ = CJ.run(d, os.path.join(root, "onepass"), runner_of(json.dumps(no_session)))
    check("no session to resume -> no re-ask, not signed", not rec["signed"] and "reasked" not in rec, rec)
    rec, _ = CJ.run(d, os.path.join(root, "onepass"), runner_of(answer("covered", checklist=[
        row("inv_a"), row("inv_b"), {"id": "leaf_c", "parts": []}]), None), timeout=CJ.REASK_MIN_S - 1)
    check("a row naming no part is a missing row; too little time left -> no re-ask",
          not rec["signed"] and rec["unchecked"] == ["leaf_c"] and "reasked" not in rec, rec)

    # A failed part cannot fall out of the list, and cannot sign.
    del signed[:]
    failing = [row("inv_a", False, ""), row("inv_b"), row("leaf_c")]
    rec, _ = CJ.run(d, os.path.join(root, "onepass"), runner_of(answer("covered", checklist=failing)))
    check("covered over a failed part -> not_covered, the part is a gap, not signed",
          rec["verdict"] == "not_covered" and not rec["signed"] and not signed
          and [g["ids"] for g in rec["gaps"]] == [["inv_a"]], rec)
    rec, _ = CJ.run(d, os.path.join(root, "onepass"), runner_of(answer("not_covered", [gap], checklist=failing)))
    check("a failed part its gap already names is not listed twice", bare(rec["gaps"]) == [gap], rec)
    failing[1] = row("inv_b", False, "sc_b")
    rec, _ = CJ.run(d, os.path.join(root, "onepass"), runner_of(answer("not_covered", [gap], checklist=failing)))
    check("a failed part no gap names joins the list",
          len(rec["gaps"]) == 2 and rec["gaps"][1]["ids"] == ["inv_b"] and "sc_b" in rec["gaps"][1]["where"], rec)

    with open(os.path.join(d, "record.json"), "w") as f:
        f.write("{broken")
    check("an unreadable record.json does not stop the pre-launch step", CJ.required_ids(d, CT.load(d)) == ["leaf_c", "inv_a"])
    with open(os.path.join(d, "record.json"), "w") as f:
        json.dump({"inventory": [{"id": "inv_a", "what": "a"}, {"id": "inv_b", "what": "b"}]}, f)

    # A re-judge carries the last verdict forward; a judge that reached none leaves nothing to carry.
    n = len(calls)
    CJ.run(d, os.path.join(root, "onepass"), runner_of(answer("not_covered", [gap], checklist=failing)))
    again = calls[n][0][2]
    check("a re-judge is pointed at the previous verdict, and a passed unchanged part needs a quoted defect",
          "previous judge" in again and CJ.VERDICT_FILE in again and "quote the defect" in again, again[-400:])
    CJ.run(d, os.path.join(root, "onepass"), runner_of("not json"))
    n = len(calls)
    CJ.run(d, os.path.join(root, "onepass"), runner_of(answer("not_covered", [gap], checklist=failing)))
    check("an errored earlier run is no previous verdict", "previous judge" not in calls[n][0][2], calls[n][0][2][-300:])


def bare(gaps):
    """The gaps without the program's round tags (new_since, judge_said) and numbering (gid): selftest_coverage_judge_loop
    and selftest_coverage_delta test those."""
    return [{k: v for k, v in g.items() if k not in ("new_since", "judge_said", "since", "gid")} for g in gaps]


def main():
    CJ.CONTRACT = False   # bare gaps test another rule; the refusal record is selftest_coverage_refusal_record
    CJ.delta_plan = lambda d, prior, read=None: None   # the full judge's loop; the delta re-judge is selftest_coverage_delta
    DS.owner_away = lambda: (False, "selftest: attended")   # the real presence must not move this test
    saved = (CT.coverage_problem, CT.sign, DS.exam_errors)
    signed, seen = [], {}
    CT.coverage_problem = lambda d, repo, tree: seen.get("cov", "no coverage signature")
    DS.exam_errors = lambda ex, d, st, repo=None: seen.get("exam", [])

    def fake_sign(d, by, repo=None, **kw):
        signed.append((by, os.environ.get("RM_ROLE_UNIT")))
        return []
    CT.sign = fake_sign
    # these cases judge one concept a dozen times: the loop limit is selftest_coverage_judge_loop's to test, so it is
    # lifted here, and any alarm a case raised would land in a temp dir, never the real rows
    CJ.NOT_COVERED_LIMIT = CJ.JUDGE_RUNS_MAX = 10 ** 6
    CJ.JUDGE_SPEND_MAX = 10 ** 15
    # an alarm a case raises tells through incident.signal: the ops dir and the dispatcher state must be temp too, or a
    # tripped case opens a real incident for the Conductor (it did once: refusals-20261112233646)
    env = {k: os.environ.get(k) for k in ("RM_REFUSAL_DIR", "RM_OPS_WATCH_DIR", "RM_DISPATCHER_STATE")}
    try:
        with tempfile.TemporaryDirectory() as root:
            ops = os.path.join(root, "ops")
            os.makedirs(ops)
            os.environ.update(RM_REFUSAL_DIR=os.path.join(root, "refusals"), RM_OPS_WATCH_DIR=ops,
                              RM_DISPATCHER_STATE=os.path.join(root, "dispatcher"))
            d = concept(root)
            calls = []

            def runner_of(out, mutate=None):
                def r(argv, cwd, env, timeout):
                    calls.append((argv, env.get("RM_ROLE_UNIT")))
                    if mutate:
                        mutate()
                    return 0, out
                return r

            check("plan: stage 5, exam passed, unsigned -> judge", CJ.plan(d, root)[0] == "judge", CJ.plan(d, root))
            rec, msg = CJ.run(d, root, runner_of(answer("covered")), now=1793900000)
            check("covered -> signed as CoverageJudge from the judge's unit",
                  rec["signed"] and signed == [("CoverageJudge", "rm-coverage-judge-1793900000")], (rec, signed))
            check("the judge ran opus with a json schema and its own unit",
                  calls and "--json-schema" in calls[-1][0] and "opus" in calls[-1][0]
                  and calls[-1][1] == "rm-coverage-judge-1793900000", calls[-1:])
            prompt = calls[-1][0][2]
            check("the prompt names the contract and the lock packet, and keeps the maker's account out",
                  "designer_scene_contract.md" in prompt and "designer_lock.md" in prompt and "result.*.json" in prompt)
            check("RM_ROLE_UNIT is restored after signing", os.environ.get("RM_ROLE_UNIT") != "rm-coverage-judge-1793900000")
            check("the verdict is on file", json.load(open(os.path.join(d, CJ.VERDICT_FILE)))["verdict"] == "covered")
            st = DS.load_state(d)
            check("the judge's tokens are charged to the concept as a review",
                  any(c.get("kind") == "review" and c.get("ref") == "rm-coverage-judge-1793900000"
                      for c in st["budget"]["charges"]), st["budget"]["charges"])
            del signed[:]
            rec, _ = CJ.run(d, root, runner_of(answer("not_covered", [{"what": "w", "where": "x", "return_to": 3}])))
            check("not_covered -> no signature, gaps on file", not rec["signed"] and not signed and rec["gaps"], rec)
            rec, _ = CJ.run(d, root, runner_of(answer("covered", [{"what": "w", "where": "x", "return_to": 3}])))
            check("covered with gaps -> not signed", not rec["signed"] and not signed, rec)
            rec, _ = CJ.run(d, root, runner_of('{"result": "I think it is covered"}'))
            check("no structured verdict -> not signed", not rec["signed"] and not signed and rec.get("error"), rec)
            rec, _ = CJ.run(d, root, runner_of("not json"))
            check("unparseable output -> not signed", not rec["signed"] and not signed and rec.get("error"), rec)

            def edit_sheet():
                with open(os.path.join(d, "sheet.md"), "a") as f:
                    f.write("more\n")
            rec, _ = CJ.run(d, root, runner_of(answer("covered"), edit_sheet))
            check("covered but the sheet changed meanwhile -> not signed", not rec["signed"] and not signed, rec)
            one_pass(root, calls, runner_of, signed)
            n = len(calls)
            seen["cov"] = None
            check("already signed -> skip, no judge launched",
                  CJ.run(d, root, runner_of(answer("covered")))[0] is None and len(calls) == n)
            seen["cov"], seen["exam"] = "no coverage signature", ["exam: 8/10 is under 90%"]
            check("exam not passed -> skip", CJ.plan(d, root)[0] == "skip" and "exam" in CJ.plan(d, root)[1])
            seen["exam"] = []
            d4 = concept(os.path.join(root, "r4"), stage=4)
            check("stage 4 -> skip", CJ.plan(d4, root)[0] == "skip")
            dl = concept(os.path.join(root, "rl"), status="locked")
            check("locked -> skip", CJ.plan(dl, root)[0] == "skip")
            check("no stage.json -> error", CJ.plan(os.path.join(root, "nothing"), root)[0] == "error")
            # the launcher's wiring
            pre = RL.coverage_pre(d)
            check("role_launch: a Designer run at stage 5 gets the judge as its pre-launch step",
                  pre == [["python3", "src/RimMandrake/rimflow/coverage_judge.py", "run", d]], pre)
            check("role_launch: at stage 4 no pre-launch step", RL.coverage_pre(d4) is None)
            check("role_launch: locked, no pre-launch step", RL.coverage_pre(dl) is None)
            check("role_launch: unreadable concept, no pre-launch step", RL.coverage_pre(os.path.join(root, "x")) is None)
    finally:
        CT.coverage_problem, CT.sign, DS.exam_errors = saved
        for k, v in env.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v
    sched =json.load(open(os.path.join(HERE, "dispatcher_schedule.json")))
    des = [r for r in sched["roles"] if r.get("name") == "Designer"]
    check("the Designer's schedule bounds the pre-launch step above the judge's own timeout",
          des and des[0].get("pre_launch_max_s", 0) > CJ.TIMEOUT_S, des and des[0].get("pre_launch_max_s"))
    print("selftest_coverage_judge: %s" % ("PASS" if not FAILS else "FAIL (%d)" % len(FAILS)))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
