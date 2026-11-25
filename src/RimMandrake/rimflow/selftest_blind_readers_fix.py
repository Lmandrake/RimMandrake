#!/usr/bin/env python3
"""selftest_blind_readers_fix: the promises of design/specs/2026-11-25-blind-readers-fix/boundary.md, one test per
promise, each named as the promise is. Item RIMMANDRAKE_LET_BLIND_READERS_FIX_TWO_STILL_FORBIDDEN_IN_CODE; the owner's
ruling of 2026-11-25: "A blind judge absolutely CAN fix and SHOULD fix! But it would then require a new blind judge run
to validate its work thereafter."

Two blind readers: the steward's fresh reader of a mod fix (maturation.review_state and its three callers, the steward
brief, the tick's route) and the coverage judge (coverage_judge.judge_tail, its prompts, judge_fix, delta_plan, run).
No model, no network, no game; every file is in a temp root. `--mutants` plants a fault in each promise's code and
reports any mutant that no test catches (exit 1)."""
import json
import os
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import selftest_wrong_check_fixed_in_sitting as W  # noqa: E402  its visit and cycle fixtures (temp roots)
import maturation as M  # noqa: E402
import maturation_autonomy as MA  # noqa: E402
import concept_tree as CT  # noqa: E402
import coverage_judge as CJ  # noqa: E402
import designer_stage as DS  # noqa: E402

MAKER, R1, R2, R3 = "rm-blind-judge-wmod-1", "rm-steward-wmod-cycle-one-2", "rm-steward-wmod-cycle-one-3", "rm-steward-x-4"
S1, S2 = "1111111aaa", "2222222bbb"
RED = {"cmd": "python3 tests/flow.py", "rc": 1}
GREEN = {"cmd": "python3 tests/flow.py", "rc": 0}


def fixed(reader, key, at, **kw):
    r = {"reader": reader, "verdict": "fixed", "fixed_at": at, "red": RED, "green": GREEN,
         "why": "the fix sums the flow twice; the reader's test reads it red, its own fix green"}
    r.update(kw)
    r["fault" if not M.SHA_RE.match(key) else "fix"] = key
    return r


def said(reader, key, verdict="sound"):
    return {"fix": key, "reader": reader, "verdict": verdict, "why": "read the diff and ran the test at both sides"}


NOLINE = (lambda u: {u})        # no detached records: a run continues nothing


# ---- the steward's fresh reader --------------------------------------------------------------------------------------

def t_a_readers_fix_is_no_pass_and_owes_one_fresh_validator():
    st = M.review_state([fixed(R1, "CHK_A", S1)], "CHK_A", MAKER, NOLINE)
    ok = st["state"] == "owed" and S1 in st["why"] and R1 in st["why"] and st["chain"][0]["fixed_at"] == S1
    sound = M.review_state([fixed(R1, "CHK_A", S1), said(R2, S1)], "CHK_A", MAKER, NOLINE)
    unsound = M.review_state([fixed(R1, "CHK_A", S1), said(R2, S1, "unsound")], "CHK_A", MAKER, NOLINE)
    nocommit = M.review_state([fixed(R1, "CHK_A", "")], "CHK_A", MAKER, NOLINE)
    unshown = M.review_state([fixed(R1, "CHK_A", S1, red={"cmd": "x", "rc": 0})], "CHK_A", MAKER, NOLINE)
    return (ok and sound["state"] == "sound" and unsound["state"] == "unsound" and nocommit["state"] == "unsound"
            and unshown["state"] == "owed" and "not shown" in unshown["why"]
            and M.review_sound([fixed(R1, "CHK_A", S1)], "CHK_A", MAKER, NOLINE)[0] is False), (
        st, sound["state"], unsound["state"], nocommit, unshown["why"])


def t_the_validator_starts_fresh_and_made_no_fix():
    """A row on the reader's fix by that reader, by the maker of the first fix, or by a run that carries on the reader's
    run (a continuation: its record's continued_from or continue_root) is not counted."""
    lin = {R3: {R3, R1}}            # R3 is a continuation of R1
    line = lambda u: lin.get(u, {u})    # noqa: E731
    rows = [fixed(R1, "CHK_A", S1)]
    own = M.review_state(rows + [said(R1, S1)], "CHK_A", MAKER, line)
    maker = M.review_state(rows + [said(MAKER, S1)], "CHK_A", MAKER, line)
    cont = M.review_state(rows + [said(R3, S1)], "CHK_A", MAKER, line)
    fresh = M.review_state(rows + [said(R2, S1)], "CHK_A", MAKER, line)
    # the real lineage reads the detached record's continuation fields
    real = M.run_lineage("rm-no-such-unit-selftest")
    return (all(x["state"] == "owed" for x in (own, maker, cont)) and fresh["state"] == "sound"
            and real == {"rm-no-such-unit-selftest"}), (own["why"], maker["why"], cont["why"], fresh)


def t_the_chain_ends_at_the_second_fix():
    rows = [fixed(R1, "CHK_A", S1), fixed(R2, S1, S2)]
    ended = M.review_state(rows, "CHK_A", MAKER, NOLINE)
    third = M.review_state(rows + [said(R3, S2)], "CHK_A", MAKER, NOLINE)       # no third read counts
    con = M.review_state(rows + [said("CONDUCTOR", S2)], "CHK_A", MAKER, NOLINE)
    con_bad = M.review_state(rows + [said("CONDUCTOR", S2, "unsound")], "CHK_A", MAKER, NOLINE)
    return (ended["state"] == "ended" and ended["why"].startswith(M.FIX_CHAIN_ENDED) and third["state"] == "ended"
            and con["state"] == "sound" and con_bad["state"] == "unsound"), (ended, third["state"], con, con_bad)


def t_the_blind_exit_reads_the_chain():
    owed = W.blind("bf_owed", against="mod", reviews=[fixed(R1, "CHK_A", S1)])
    good = W.blind("bf_good", against="mod", reviews=[fixed(R1, "CHK_A", S1), said(R2, S1)])
    ended = W.blind("bf_ended", against="mod", reviews=[fixed(R1, "CHK_A", S1), fixed(R2, S1, S2)])
    return (owed["state"] == "not_met" and owed["checks"].get("fix_reader_owed") == ["CHK_A"]
            and owed["checks"].get("reader_fixes", {}).get("CHK_A")
            and good["state"] == "met"
            and ended["state"] == "not_met" and ended["checks"].get("fix_chain_ended") == ["CHK_A"]
            and not ended["checks"].get("fix_reader_owed")
            and any(M.FIX_CHAIN_ENDED in w for w in ended["why"])), (owed["why"], good["why"], ended["why"])


def t_the_visit_exit_reads_the_chain():
    fx = W.MOD_FIX["commit"]
    owed = W.ingame(W.mod_fixed(), reviews=[fixed(W.READER, fx, S1)], name="vf_owed")
    good = W.ingame(W.mod_fixed(), reviews=[fixed(W.READER, fx, S1), said(R2, S1)], name="vf_good")
    ended = W.ingame(W.mod_fixed(), reviews=[fixed(W.READER, fx, S1), fixed(R2, S1, S2)], name="vf_ended")
    return (owed["state"] == "not_met" and owed.get("fix_readers_owed") and good["state"] == "met"
            and ended["state"] == "not_met" and ended.get("fix_chain_ended") == [fx]
            and not ended.get("fix_readers_owed")
            and any(M.FIX_CHAIN_ENDED in w for w in ended["why"])), (owed["why"], good["why"], ended["why"])


def t_the_tick_sends_an_ended_chain_to_the_conductor():
    why = M.FIX_CHAIN_ENDED + "reader a fixed this fix at x, and its validator b fixed again at y"
    row = {"mod": W.MOD, "decision": "exit_not_met", "stage": "in_game", "visit": 1, "why": why}
    MA._route(W.TMP, {}, {}, {"exit": {"why": ["in-game check c1: " + why]}}, row, "0.1.0", lambda m: {}, False, {},
              fx_signed=lambda m: True)
    plain = {"mod": W.MOD, "decision": "exit_not_met", "stage": "in_game", "visit": 1, "why": "c1 reads FAIL"}
    MA._route(W.TMP, {}, {}, {"exit": {"why": ["in-game check c1: its last row reads FAIL"]}}, plain, "0.1.0",
              lambda m: {}, False, {}, fx_signed=lambda m: True)
    return (row.get("decision") == "fix_chain_ended" and row.get("aut") is None
            and "fix_chain_ended" in MA.PAUSE_WHY and plain.get("aut") == "steward"), (row, plain.get("decision"))


def t_the_steward_brief_lets_the_reader_fix():
    root = W.visit("bf_brief", W.ALL_PASS)
    text = " ".join(MA.steward_brief(root, W.MOD, {"steward_kind": "exit_not_met", "stage": "in_game", "mod": W.MOD,
                                                   "why": "x", "decision": "steward"}).split())
    need = ('"verdict": "sound"|"unsound"|"fixed"', '"fixed_at": <your commit>', "test first",
            "Your row is no pass of your own fix", "one new fresh reader", "starts fresh", "the chain ends there",
            "no third read", "never a bar")
    lacks = [n for n in need if n not in text]
    stale = [s for s in ("never fix the fix yourself", "never fix") if s in text.lower()]
    return not lacks and not stale, lacks + stale


# ---- the coverage judge ----------------------------------------------------------------------------------------------

def concept(root):
    d = os.path.join(root, "design", "concepts", "Foo")
    os.makedirs(d, exist_ok=True)
    os.makedirs(os.path.join(root, os.path.dirname(CT.OWNER_SHARD)), exist_ok=True)
    with open(os.path.join(d, "stage.json"), "w") as f:
        json.dump({"stage": 5, "status": "open", "item": "FOO_ITEM",
                   "budget": {"cap": 4000000, "reserve": 60000, "spent": 0, "charges": []}}, f)
    with open(os.path.join(d, "tree.json"), "w") as f:
        json.dump({"kind": "mod", "leaves": [{"id": "leaf_a", "text": "the lantern lights straw"}]}, f)
    with open(os.path.join(d, "sheet.md"), "w") as f:
        f.write("sheet\n")
    with open(os.path.join(d, "scenes.json"), "w") as f:
        json.dump({"scenes": [{"id": "sc_a", "text": "a lantern far from straw"}]}, f)
    return d


GAP = {"what": "sc_a never puts the lantern on straw", "where": "scenes.json sc_a", "return_to": 3, "ids": ["leaf_a"]}


def answer(verdict, gaps=()):
    return json.dumps({"structured_output": {"verdict": verdict, "gaps": list(gaps), "reasons": "r", "repairs": [],
                                             "checklist": [{"id": "leaf_a", "evidence": ["scenes.json"], "parts": [
                                                 {"what": "lights straw", "scene": "sc_a", "ok": not gaps}]}]},
                       "session_id": "sess", "usage": {"input_tokens": 10, "output_tokens": 2}})


class Cov:
    """A temp concept and a stub judge that may edit a file while it judges; the real program around it."""

    def __init__(self, root):
        self.root, self.calls = root, []
        self.d = concept(root)

    def runner(self, out, edit=None):
        def r(argv, cwd, env, timeout):
            self.calls.append(argv)
            if edit:
                with open(os.path.join(self.d, edit), "a") as f:
                    f.write("\n")
            return 0, out
        return r

    def look(self, out, edit=None, now=None):
        return CJ.run(self.d, self.root, self.runner(out, edit), now=now, charge=False, reader=None)


def with_cov(fn):
    """Run fn(Cov) with the coverage program's outside world stubbed: the exam passes, nothing signs for real, the
    caps are lifted (the chain rule, not a cap, must stop it), and every alarm lands in a temp dir."""
    saved = (CJ.CONTRACT, CT.coverage_problem, CT.sign, DS.exam_errors, DS.owner_away, CJ.NOT_COVERED_LIMIT,
             CJ.JUDGE_RUNS_MAX, CJ.JUDGE_SPEND_MAX, CJ.RC.status)
    env = {k: os.environ.get(k) for k in ("RM_REFUSAL_DIR", "RM_OPS_WATCH_DIR", "RM_DISPATCHER_STATE")}
    CJ.CONTRACT = False
    CT.coverage_problem = lambda d, repo, tree: "no coverage signature"
    CT.sign = lambda d, by, repo=None, **kw: []
    DS.exam_errors = lambda ex, d, st, repo=None: []
    DS.owner_away = lambda: (False, "selftest: attended")
    CJ.NOT_COVERED_LIMIT = CJ.JUDGE_RUNS_MAX = 10 ** 6
    CJ.JUDGE_SPEND_MAX = 10 ** 15
    CJ.RC.status = lambda family: "CALIBRATED"
    try:
        with tempfile.TemporaryDirectory() as root:
            ops = os.path.join(root, "ops")
            os.makedirs(ops)
            os.environ.update(RM_REFUSAL_DIR=os.path.join(root, "refusals"), RM_OPS_WATCH_DIR=ops,
                              RM_DISPATCHER_STATE=os.path.join(root, "dispatcher"))
            return fn(Cov(root))
    finally:
        (CJ.CONTRACT, CT.coverage_problem, CT.sign, DS.exam_errors, DS.owner_away, CJ.NOT_COVERED_LIMIT,
         CJ.JUDGE_RUNS_MAX, CJ.JUDGE_SPEND_MAX, CJ.RC.status) = saved
        for k, v in env.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v


def t_the_coverage_judge_may_fix_and_its_second_reader_reads_only():
    def body(c):
        c.look(answer("covered"), now=1793900001)
        judge = c.calls[-1]
        got = []
        CJ.default_runner, real = (lambda argv, cwd, env, timeout: (got.append(argv), (0, "null"))[1]), CJ.default_runner
        try:
            CJ.llm_reader(c.d, c.root, "u", charge=False, runner=lambda argv, cwd, env, timeout: (
                got.append(argv), (0, "null"))[1])([{"clause": ["leaf_a"]}])
        finally:
            CJ.default_runner = real
        reader = got[-1] if got else []
        deny = reader[reader.index("--disallowedTools") + 1].split(",") if "--disallowedTools" in reader else []
        return ("--disallowedTools" not in judge and sorted(deny) == ["Edit", "NotebookEdit", "Write"]
                and "--model" in judge), (judge[-8:], reader[-8:])
    return with_cov(body)


def t_the_coverage_prompts_carry_the_fix_rule():
    def body(c):
        full = " ".join(CJ.prompt(c.d, c.root, ["leaf_a"]).split())
        dp = {"claims": [], "refused": [], "changed": [], "against": "j0", "prior_checklist": [], "entries": {},
              "ids": ["leaf_a"], "claimed_gaps": [], "carried": [], "loose": False}
        delta = " ".join(CJ.delta_prompt(c.d, c.root, dp, 2).split())
        fix = " ".join(CJ.JUDGE_FIX_TEXT.split())
        stale = [s for s in ("Do not edit any file", "edit nothing", "edit \"nothing") for t in (full, delta) if s in t]
        need = ("You may fix a gap yourself", "scenes.json", "Your fix is no pass of your own", "the chain ends",
                "a fresh judge that did not make the fix")
        return (fix in full and fix in delta and not stale and all(n in fix for n in need)), stale
    return with_cov(body)


def t_a_judges_fix_is_no_pass_and_no_refusal():
    def body(c):
        rec, msg = c.look(answer("covered", [dict(GAP, judge_fixed="sc_a: the lantern now falls on straw")]),
                          edit="scenes.json", now=1793900002)
        jf = rec.get("judge_fixed") or {}
        dp = CJ.delta_plan(c.d, rec)
        return (rec.get("verdict") == "not_covered" and not rec.get("signed") and jf.get("files") == ["scenes.json"]
                and not CJ.is_refusal(rec) and "no pass" in str(rec.get("advisory"))
                and dp is not None and [x["gap"] for x in dp["claims"]] == ["g1"]
                and "fixed it itself" in dp["claims"][0]["evidence"]), (rec.get("verdict"), jf, rec.get("advisory"),
                                                                        dp and dp["claims"], msg)
    return with_cov(body)


def t_a_judges_fix_outside_scenes_is_no_fix():
    def body(c):
        rec, _ = c.look(answer("not_covered", [dict(GAP, judge_fixed="the sheet now says so")]), edit="sheet.md",
                        now=1793900003)
        return (not rec.get("judge_fixed") and rec.get("judge_fix_refused") and rec.get("stale_inputs")
                and "no pass" not in str(rec.get("advisory"))), rec
    return with_cov(body)


def t_the_coverage_chain_ends_at_the_second_fix():
    def body(c):
        first, _ = c.look(answer("not_covered", [dict(GAP, judge_fixed="sc_a: lantern on straw")]), edit="scenes.json",
                          now=1793900004)
        second, msg = c.look(answer("not_covered", [dict(GAP, judge_fixed="sc_a: the straw is dry now")]),
                             edit="scenes.json", now=1793900005)
        n = len(c.calls)
        what, why = CJ.plan(c.d, c.root)
        third = c.look(answer("covered"), now=1793900006)
        fresh = c.calls[0] != c.calls[1] and "--resume" not in c.calls[1]
        return (first.get("judge_fixed") and not first.get("fix_chain_ended")
                and str(second.get("fix_chain_ended") or "").startswith(CJ.FIX_CHAIN_ENDED)
                and "stopped" in msg and what == "stopped" and len(c.calls) == n and fresh
                and third[0] is not None and "stopped" in str(third[1])), (first.get("fix_chain_ended"), msg, what,
                                                                          why, third)
    return with_cov(body)


def run(tests, quiet=False):
    fails = []
    for t in tests:
        try:
            ok, got = t()
        except Exception as e:  # noqa: BLE001 - a raise is a red test, named
            ok, got = False, "raised %s: %s" % (type(e).__name__, e)
        name = t.__name__[2:].replace("_", "-")
        if not quiet:
            print("%s  %s%s" % ("PASS" if ok else "FAIL", name, "" if ok else "  got: %r" % (got,)))
        if not ok:
            fails.append(name)
    return fails


# ---- mutants: a planted fault in each promise's code must turn a test red ---------------------------------------------

def _mutants():
    """-> [(name, module, attribute, replacement)]: each a planted fault."""
    real_state = M.review_state

    def pass_own_fix(reviews, key, maker, lineage=None):       # a reader's `fixed` row read as sound
        r = real_state([dict(x, verdict="sound") if x.get("verdict") == "fixed" else x for x in reviews or []],
                       key, maker, lineage)
        return r

    def no_chain_end(reviews, key, maker, lineage=None):       # the second fix owes a third reader instead
        r = real_state(reviews, key, maker, lineage)
        return dict(r, state="owed") if r["state"] == "ended" else r

    def no_lineage(reviews, key, maker, lineage=None):         # a continuation of the fixer validates its fix
        return real_state(reviews, key, maker, lambda u: {u})
    real_fix = CJ.judge_fix

    def judge_passes(rec, prior, moved):                       # the judge's fix is read as no fix at all
        return None

    def no_cov_chain(rec, prior, moved):
        real_fix(rec, None, moved)
    real_tail = CJ.judge_tail
    return [("a reader's fix read as a pass", M, "review_state", pass_own_fix),
            ("the chain never ends", M, "review_state", no_chain_end),
            ("a continuation of the fixer may validate", M, "review_state", no_lineage),
            ("the tick never sees an ended chain", MA, "_fix_chain_ended", lambda f: None),
            ("the judge's fix not read", CJ, "judge_fix", judge_passes),
            ("the coverage chain never ends", CJ, "judge_fix", no_cov_chain),
            ("the judge is read-only again", CJ, "judge_tail", lambda name, schema, may_fix=False: real_tail(name, schema)),
            ("the second reader may edit", CJ, "judge_tail", lambda name, schema, may_fix=False: real_tail(name, schema,
                                                                                                        True)),
            ("the delta drops the judge's claims", CJ, "own_fix_only", lambda rec: False)]


def missed_mutants(tests):
    missed = []
    for name, mod, attr, fake in _mutants():
        real = getattr(mod, attr)
        setattr(mod, attr, fake)
        try:
            if not run(tests, quiet=True):
                missed.append(name)
        finally:
            setattr(mod, attr, real)
    return missed


def main():
    tests = [t_a_readers_fix_is_no_pass_and_owes_one_fresh_validator, t_the_validator_starts_fresh_and_made_no_fix,
             t_the_chain_ends_at_the_second_fix, t_the_blind_exit_reads_the_chain, t_the_visit_exit_reads_the_chain,
             t_the_tick_sends_an_ended_chain_to_the_conductor, t_the_steward_brief_lets_the_reader_fix,
             t_the_coverage_judge_may_fix_and_its_second_reader_reads_only, t_the_coverage_prompts_carry_the_fix_rule,
             t_a_judges_fix_is_no_pass_and_no_refusal, t_a_judges_fix_outside_scenes_is_no_fix,
             t_the_coverage_chain_ends_at_the_second_fix]
    fails = run(tests)
    missed = missed_mutants(tests) if "--mutants" in sys.argv[1:] else []
    for m in missed:
        print("MISSED mutant: %s (no test went red)" % m)
    print("%s selftest_blind_readers_fix (%d of %d)" % ("PASS" if not fails and not missed else "FAIL",
                                                         len(tests) - len(fails), len(tests)))
    return 0 if not fails and not missed else 1


if __name__ == "__main__":
    sys.exit(main())
