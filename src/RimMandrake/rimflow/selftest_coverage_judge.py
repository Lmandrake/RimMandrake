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


def answer(verdict, gaps=(), tokens=True):
    res = {"structured_output": {"verdict": verdict, "gaps": list(gaps), "reasons": "r"}}
    if tokens:
        res["usage"] = {"input_tokens": 10, "output_tokens": 2, "cache_read_input_tokens": 0,
                        "cache_creation_input_tokens": 0}
    return json.dumps(res)


def main():
    saved = (CT.coverage_problem, CT.sign, DS.exam_errors)
    signed, seen = [], {}
    CT.coverage_problem = lambda d, repo, tree: seen.get("cov", "no coverage signature")
    DS.exam_errors = lambda ex, d, st, repo=None: seen.get("exam", [])

    def fake_sign(d, by, repo=None, **kw):
        signed.append((by, os.environ.get("RM_ROLE_UNIT")))
        return []
    CT.sign = fake_sign
    try:
        with tempfile.TemporaryDirectory() as root:
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
    sched = json.load(open(os.path.join(HERE, "dispatcher_schedule.json")))
    des = [r for r in sched["roles"] if r.get("name") == "Designer"]
    check("the Designer's schedule bounds the pre-launch step above the judge's own timeout",
          des and des[0].get("pre_launch_max_s", 0) > CJ.TIMEOUT_S, des and des[0].get("pre_launch_max_s"))
    print("selftest_coverage_judge: %s" % ("PASS" if not FAILS else "FAIL (%d)" % len(FAILS)))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
