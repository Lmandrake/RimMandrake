#!/usr/bin/env python3
"""selftest_arena_judge_calib.py - arena_judge_calib.py, each criterion by FORCED outcome. Offline: no model is called
(fake OpusCLI / GptConsult classes stand in INSIDE the real arena_judge.judge(); the candidate is a real one of the
frozen set, so the real neutraliser, leak scan and prompt run).

  controls     all-accept fakes -> accept; all-reject fakes -> reject whose reasons are the rejecting votes' reasons;
               a split goes to the Opus tie-break; a garbage answer is invalid, never accept
  budget       too little wall budget -> skipped (no call made); a call shortened by the budget that dies -> budget_cut
  runner       through the real C.run: a budget-cut record is retried without using a try, and is never decisive
  blind        every prompt is byte-identical whichever arm is assigned and carries no calibration vocabulary; the
               task is not a replay (no source_item / RP_ id)
  fail closed  rate() with n=0 or a run defect is UNMEASURED; judge_rates on a block with no rows / too many invalid /
               no fingerprint / a labelled candidate without a verdict / coverage not computed / an unproved mutant
               makes every rate UNMEASURED; a decoy rate above the limit or an unmatched reject makes
               only the reason rates UNMEASURED; a measured rate carries the exact CP interval
  leak scan    a GPT reason using set vocabulary is flagged
"""
from __future__ import annotations

import json
import os
import shutil
import sys
import tempfile
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

FAILS: list = []


def check(cond, msg):
    if not cond:
        FAILS.append(msg)
        print("FAIL:", msg)


SEEN: list = []


def fake(kind_answers):
    class Fake:
        def __init__(self, prefix=None, priv=None, timeout=1500):
            self.timeout = timeout

        def preflight(self):
            pass

        def __call__(self, prompt, work):
            SEEN.append(prompt)
            a = kind_answers.pop(0) if kind_answers else "no json"
            if a == "DIE":
                raise J.JudgeError("timed out after %ss" % self.timeout)
            if isinstance(a, tuple) and a[0] == "TRIP":            # the hardened GPT judge's tripwire fired
                raise J.JudgeTripwire("gpt judge tripwire: command executed with tools off", a[1])
            if isinstance(a, tuple) and a[0] == "META":            # an answer carrying the GPT tool record
                out = J.JudgeAnswer(a[1])
                out.meta = a[2]
                return out
            if a == "SLOW_DIE":
                time.sleep(self.timeout)          # the shortened timeout elapses, then the call dies
                raise J.JudgeError("timed out after %ss" % self.timeout)
            return a
    return Fake


def ans(v, reasons):
    return "Here is my verdict.\n" + json.dumps({"verdict": v, "reasons": reasons, "arm_guess": "unknown"})


def review(JC, opus, gpt, deadline=None):
    import arena_critic_calib as C
    J.OpusCLI, J.GptConsult = fake(opus), fake(gpt)
    jc = JC.JudgeCritic()
    jc.deadline = deadline
    cand = JC._by_cid()[CID]
    return jc.review(C.CriticInput(cid=CID, prompt="", criteria=cand["criteria"], diff="", tree=None, work=None))


def t_review(JC):
    v = review(JC, [ans("accept", ["fine"])], [ans("accept", ["ok"])])
    check(v.verdict == "accept", "all-accept fakes give accept, got %s %s" % (v.verdict, v.reasons))
    v = review(JC, [ans("reject", ["A is wrong"])], [ans("reject", ["B is wrong"])])
    check(v.verdict == "reject" and v.reasons == ["A is wrong", "B is wrong"],
          "all-reject: reasons of the rejecting votes, got %s %s" % (v.verdict, v.reasons))
    check(v.meta.get("gpt_reasons") == ["B is wrong"], "gpt reasons kept for the leak scan")
    v = review(JC, [ans("accept", ["fine"]), ans("reject", ["tie says no"])], [ans("reject", ["B"])])
    check(v.verdict == "reject" and [x["judge"] for x in v.meta["votes"]] == ["opus", "gpt", "opus_tiebreak"]
          and v.reasons == ["B", "tie says no"], "split goes to the tie-break: %s %s" % (v.verdict, v.reasons))
    # ARENA_JUDGE_OWNPATH_TEST_PREFIX_SIBLING: the GPT vote's tool record survives into the calibration record, for a
    # clean vote AND for a tripwire (invalid) vote, so tool attempts stay countable from results.jsonl
    rec = {"n_tools": 0, "web": 0, "refused_tool_calls": 2, "tripwire": [], "wiped": ["tmp"]}
    v = review(JC, [ans("accept", ["fine"])], [("META", ans("accept", ["ok"]), rec)])
    g = [x for x in v.meta["votes"] if x["judge"] == "gpt"]
    check(len(g) == 1 and g[0].get("tools") == rec, "a clean GPT vote keeps its tools record in meta.votes: %s" % g)
    trip = {"n_tools": 1, "web": 0, "commands": ["dir"], "tripwire": ["command executed with tools off: 'dir'"]}
    v = review(JC, [ans("accept", ["fine"]), ans("accept", ["tie ok"])], [("TRIP", trip)])
    g = [x for x in v.meta["votes"] if x["judge"] == "gpt"]
    check(len(g) == 1 and g[0]["verdict"] == "invalid" and g[0].get("tools") == trip,
          "a tripwire (invalid) GPT vote keeps its tools record in meta.votes: %s" % g)
    v = review(JC, ["garbage"], [ans("accept", ["ok"])])
    check(v.verdict == "invalid", "garbage answer is invalid, got %s" % v.verdict)
    check(not v.meta.get("budget_cut"), "a garbage answer is not a budget cut")
    # blind: no calibration vocabulary in ANY prompt; the prompt is byte-identical whichever arm is assigned; the
    # task the judge gets is not a replay (no source_item, no RP_ id)
    real_judge, real_random = J.judge, JC.random
    tasks, prompts = [], {}

    class FixedRandom:
        def __init__(self, arm):
            self.arm = arm

        def __call__(self, _seed):
            return self

        def choice(self, _seq):
            return self.arm

    def spy(**kw):
        tasks.append((kw["task"], kw["arm"]))
        return real_judge(**kw)
    J.judge = spy
    try:
        for arm in J.arms()[:2]:
            JC.random = type("R", (), {"Random": FixedRandom(arm)})
            SEEN.clear()
            review(JC, [ans("accept", ["x"])], [ans("accept", ["y"])])
            prompts[arm] = list(SEEN)
    finally:
        J.judge, JC.random = real_judge, real_random
    a, b = list(prompts.values())
    check(len(a) == 2 and a == b, "prompts identical across assigned arms (%d calls)" % len(a))
    check(all(w not in p.lower() for p in a for w in JC.LEAK_WORDS), "no prompt carries calibration vocabulary")
    check([t[1] for t in tasks] == list(J.arms()[:2]), "the forced arms reached the judge")
    check(all("source_item" not in t and not t["id"].startswith("RP_") and not J.is_replay(t) for t, _ in tasks),
          "the calibration task is not a replay")


def t_runner(JC, tmp):
    """The runner contract: a budget-cut record is retried and does NOT use up a try (attempts=1), and the cut
    record's verdict is never the decisive one."""
    import arena_critic_calib as C
    import arena_critic_mutants as M
    doc = M.load_mutant_set()
    JC.MIN_START_S, JC.MIN_CALL_S, JC.GPT_SLACK_S = 0, 1, 0
    try:
        J.OpusCLI, J.GptConsult = fake([ans("reject", ["x"])]), fake(["SLOW_DIE"])
        C.run(doc, JC.JudgeCritic(), "rt", concurrency=1, max_n=1, attempts=1, root=tmp / "runs", budget_s=3)
        recs = C.read_results(tmp / "runs" / "rt" / "results.jsonl")
        check(len(recs) == 1 and recs[0]["verdict"] == "invalid" and recs[0]["meta"].get("budget_cut"),
              "first pass leaves one budget_cut record: %s" % [(r["verdict"], r["meta"].get("budget_cut"))
                                                                  for r in recs])
        J.OpusCLI, J.GptConsult = fake([ans("accept", ["a"])] * 5), fake([ans("accept", ["b"])] * 5)
        C.run(doc, JC.JudgeCritic(), "rt", concurrency=1, max_n=1, attempts=1, root=tmp / "runs", budget_s=None)
        recs = C.read_results(tmp / "runs" / "rt" / "results.jsonl")
        cid = recs[0]["cid"]
        got = M.run_records("rt", doc, tmp / "runs").get(cid, {})
        check(len([r for r in recs if r["cid"] == cid]) == 2 and got.get("verdict") == "accept",
              "the cut candidate is retried with attempts=1 and its valid verdict decides: %s"
              % [(r["cid"], r["verdict"]) for r in recs])
    finally:
        JC.MIN_START_S, JC.MIN_CALL_S, JC.GPT_SLACK_S = 420, 60, 70


def t_budget(JC):
    SEEN.clear()
    v = review(JC, [ans("accept", ["x"])], [ans("accept", ["y"])], deadline=time.time() + 30)
    check(v.verdict == "invalid" and v.meta.get("skipped") and not SEEN, "no budget -> skipped, no call made")
    JC.MIN_START_S, JC.MIN_CALL_S, JC.GPT_SLACK_S = 0, 1, 0
    v = review(JC, [ans("accept", ["x"])], ["SLOW_DIE"], deadline=time.time() + 3)
    check(v.verdict == "invalid" and v.meta.get("budget_cut"), "a budget-shortened call that dies is budget_cut: %s"
          % v.meta)
    v = review(JC, [ans("accept", ["x"])], ["DIE"], deadline=None)
    check(v.verdict == "invalid" and not v.meta.get("budget_cut"), "a failure under the full timeout is not a cut")
    JC.MIN_START_S, JC.MIN_CALL_S, JC.GPT_SLACK_S = 420, 60, 70


def blk(**kw):
    b = {"run": "r", "candidates": 56, "invalid": 0, "critic_fingerprint": "fp", "matcher_decoy_hits": [0, 10],
         "rejects_without_valid_match": 0,
         "verdict": {"catch": [20, 31], "false_reject": [1, 8], "unlabelled_reject": [3, 16]},
         "reason": {"catch": [15, 31], "false_reject": [1, 8], "unlabelled_reject": [3, 16]},
         "by_detect": {"test": {"verdict_catch": [10, 12], "reason_catch": [8, 12]},
                       "read": {"verdict_catch": [10, 19], "reason_catch": [7, 19]}}}
    b.update(kw)
    return {"reviewers": {"critic": b}}


def t_rates(JC):
    import arena_critic_mutants as M
    check(JC.rate(0, 0)["status"] == "UNMEASURED", "n=0 is UNMEASURED")
    r = JC.rate(1, 8)
    lo, hi = M.cp(1, 8)
    check(r["status"] == "MEASURED" and r["cp95"] == [round(lo, 3), round(hi, 3)], "measured rate carries CP")
    check(JC.rate(0, 8)["cp95"][1] > 0.3, "0/8 has a wide upper bound")
    out = JC.judge_rates(blk(), missing=[])
    check(out["false_reject_tierA"]["k"] == 1 and out["miss_verdict"]["k"] == 11 and out["miss_reason"]["k"] == 16,
          "miss = n - catch")
    check(out["miss_reason_detect_read"]["k"] == 12, "by-detect miss")
    for kw, why in (({"candidates": 0}, "no rows"), ({"invalid": 12}, "invalid"), ({"critic_fingerprint": None}, "fp")):
        o = JC.judge_rates(blk(**kw), missing=[])
        check(all(v["status"] == "UNMEASURED" for k, v in o.items() if isinstance(v, dict) and "status" in v),
              "run defect %s -> every rate UNMEASURED" % why)
    for missing, why in ((None, "coverage not computed"), (["cX"], "a labelled candidate without a verdict")):
        o = JC.judge_rates(blk(), missing=missing)
        check(all(v["status"] == "UNMEASURED" for v in o.values() if isinstance(v, dict) and "status" in v),
              "%s -> every rate UNMEASURED" % why)
    b = blk()
    b["detect"] = {"unproved": 1}
    o = JC.judge_rates(b, missing=[])
    check(o["false_reject_tierA"]["status"] == "UNMEASURED", "an unproved mutant -> UNMEASURED")
    for kw in ({"matcher_decoy_hits": [2, 10]}, {"rejects_without_valid_match": 1}):
        o = JC.judge_rates(blk(**kw), missing=[])
        check(o["miss_reason"]["status"] == "UNMEASURED" and o["miss_verdict"]["status"] == "MEASURED"
              and o["false_reject_tierA"]["status"] == "MEASURED", "reason-only defect %s" % kw)


def t_leak(JC):
    hits = JC.leak_scan({"c1": {"meta": {"gpt_reasons": ["the planted defect in fixtures/critic_mutants.json"]}},
                         "c2": {"meta": {"gpt_reasons": ["off by one in loop"]}}})
    check({h["cid"] for h in hits} == {"c1"}, "leak scan flags set vocabulary only")


def t_spend(JC, tmp):
    """A call refused for budget never started: it is no call, no GPT call, and no missing token report."""
    calls = [{"kind": "opus", "prompt_chars": 400, "timeout": 900, "wall_s": 5, "answer_chars": 40},
             {"kind": "opus", "prompt_chars": 400, "timeout": 900, "wall_s": 900},
             {"kind": "gpt", "prompt_chars": 400, "timeout": 900, "wall_s": 9},
             {"kind": "gpt", "prompt_chars": 400, "timeout": 5, "cut": True}]
    log = tmp / "gpt_calls.jsonl"
    log.write_text(json.dumps({"tokens_used": 1000}) + "\n")
    sp = JC.spend([{"meta": {"calls": calls}}], [], log)
    check((sp["model_calls"], sp["gpt_calls"], sp["calls_refused_for_budget"], sp["gpt_calls_without_token_report"],
           sp["opus_calls_answered"], sp["opus_cut_or_failed"], sp["opus_tokens_est"]) ==
          (3, 1, 1, 0, 1, 1, {"in": 200, "out": 10}), "spend counts started calls only: %s" % sp)


def main() -> int:
    global J, CID
    tmp = Path(tempfile.mkdtemp(prefix="selftest_judge_calib_"))
    os.environ["ARENA_JUDGE_WORK"] = str(tmp / "work")
    os.environ["ARENA_JUDGE_CALIB_PRIVATE"] = str(Path.home() / ".local" / "state" / ("rm_jc_selftest_%d" % os.getpid()))
    os.environ.setdefault("ARENA_JUDGE_OPUS_MODEL", "selftest-model")
    import arena_judge as J  # noqa: F811
    import arena_judge_calib as JC
    real = (J.OpusCLI, J.GptConsult)
    try:
        doc = JC.M.load_mutant_set()
        CID = next(c["cid"] for c in doc["candidates"] if c.get("role") == "mutant")
        t_review(JC)
        t_budget(JC)
        t_runner(JC, tmp)
        t_rates(JC)
        t_leak(JC)
        t_spend(JC, tmp)
    finally:
        J.OpusCLI, J.GptConsult = real
        shutil.rmtree(tmp, ignore_errors=True)
        shutil.rmtree(os.environ["ARENA_JUDGE_CALIB_PRIVATE"], ignore_errors=True)
    print("%s: %d failed" % ("FAIL" if FAILS else "PASS", len(FAILS)))
    return 1 if FAILS else 0


J = None
CID = None

if __name__ == "__main__":
    sys.exit(main())
