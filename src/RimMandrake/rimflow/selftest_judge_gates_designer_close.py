#!/usr/bin/env python3
"""selftest_judge_gates_designer_close.py - one test per promise of
design/specs/2026-11-19-judge-gates-and-designer-close/boundary.md (lane
RIMMANDRAKE_FIX_JUDGE_GATES_AND_DESIGNER_CLOSE_CRASHES): the Designer's close rejects a malformed id instead of
crashing, a block whose ledger item closed is read again, the open preview writes nothing, a coverage refusal judged on
inputs that moved counts as no strike, the bar detector spares a player-visible gap that names a def word, and the gate
blocks a filer writes. Each test is named after its promise. Runs in a temp dir; the claude call, the ledger fold and
the alarm rows are stubbed; no real concept, ledger or state is touched."""
import contextlib
import hashlib
import io
import json
import os
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
os.environ.setdefault("RM_JUDGE_SYNC", "0")
import bar_rule as BR  # noqa: E402
import concept_tree as CT  # noqa: E402
import coverage_judge as CJ  # noqa: E402
import designer_stage as DS  # noqa: E402
import launch_checks as LC  # noqa: E402
import refusal_contract as RC  # noqa: E402

FAILS = []
ITEM = "CONCEPT_FOO_ITEM"


def check(name, ok, got=""):
    print("%s %s%s" % ("ok  " if ok else "FAIL", name, "" if ok else "  got: %s" % (got,)))
    if not ok:
        FAILS.append(name)


def sha(p):
    with open(p, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def repo_at(tmp):
    owner = os.path.join(tmp, CT.OWNER_SHARD)
    os.makedirs(os.path.dirname(owner), exist_ok=True)
    open(owner, "a").close()
    return tmp


def concept(tmp, name="Foo"):
    d = os.path.join(tmp, "design", "concepts", name)
    DS.init(d, name, ITEM, cap=200000, reserve=20000)
    return d


def put(d, name, obj):
    with open(os.path.join(d, name), "w", encoding="utf-8") as f:
        json.dump(obj, f)


@contextlib.contextmanager
def patched(mod, name, fn):
    old = getattr(mod, name, None)     # None on a base commit without it: the case then fails, never the run
    setattr(mod, name, fn)
    try:
        yield
    finally:
        setattr(mod, name, old)


def crash_or(fn, *a, **k):
    try:
        return fn(*a, **k)
    except Exception as e:
        return "CRASH %s: %s" % (type(e).__name__, e)


# ---------------------------------------------------------------- designer_stage close_run

def t_close_run_rejects_non_string_ids(tmp):
    repo = repo_at(tmp)
    tree = {"leaves": [{"id": "L1"}, {"id": "L2"}]}
    base = {"kind": "acceptance", "staged_by": "script", "entry_point": "x::y", "entry_point_item": "IT",
            "action": "a", "expect": "e", "restore": "r", "start": ["s"], "hold": DS.HOLDS[0],
            "control": {"case": "c", "expect": "e", "rules_out": "r"}}
    sc = {"scenes": [dict(base, id="s1", requirement=[{"id": "L1"}]),
                     dict(base, id="s2", kind="interaction", features=["L1", ["L2"]])]}
    errs = crash_or(DS.scene_errors, sc, tree, repo)
    check("close-run-rejects-non-string-ids: a dict requirement is a scene error naming it, never a crash",
          isinstance(errs, list) and any("s1" in e and "requirement entry" in e and '"id": "L1"' in e for e in errs)
          and any("s2" in e and "features entry" in e for e in errs), errs)
    rec = {"inventory": [{"id": "ladder", "impl": "present", "scope": "approved"}]}
    a = {"id": "a1", "text": "t", "decision": "d", "about": [{}], "author": "x",
         "review": {"by": "y", "verdict": "pass"}}
    errs = crash_or(DS.ask_errors, a, rec)
    check("close-run-rejects-non-string-ids: an ask about [{}] is an ask error naming it, never a crash",
          isinstance(errs, list) and any("about entry {}" in e for e in errs), errs)
    # the whole close: a waiting_owner result whose sent ask is about [{}] -> rejected, the run cleared
    d = concept(tmp, "Ids")
    st = DS.load_state(d)
    st["stage"] = 1     # only stages 1-2 send him asks: the stage where ask_errors reads `about`
    DS.write_json(DS.state_path(d), st)
    DS.open_run(d, "r1", repo=repo)
    put(d, "record.json", {"inventory": [], "asks": [dict(a, status="sent")]})
    put(d, "result.json", {"run": "r1", "stage": 1, "outcome": "waiting_owner"})
    got = crash_or(DS.close_run, d, "r1", 100, repo=repo)
    st = DS.load_state(d)
    check("close-run-rejects-non-string-ids: close_run returns (False, reasons) and clears running",
          isinstance(got, tuple) and got[0] is False and any("about entry {}" in e for e in got[1])
          and st.get("running") is None, (got, st.get("running")))


def t_close_run_never_raises_on_a_result_shape(tmp):
    repo = repo_at(tmp)
    d = concept(tmp, "Shape")
    DS.open_run(d, "r1", repo=repo)
    put(d, "result.json", {"run": "r1", "stage": 0, "outcome": "done"})

    def boom(res, d, st, repo=None):
        raise TypeError("unhashable type: 'dict'")
    with patched(DS, "result_errors", boom):
        got = crash_or(DS.close_run, d, "r1", 100, repo=repo)
    st = DS.load_state(d)
    check("close-run-never-raises-on-a-result-shape: a validator crash is a rejection naming it, running cleared",
          isinstance(got, tuple) and got[0] is False and "TypeError" in got[1][0] and st.get("running") is None
          and st["results"][-1]["outcome"] == "rejected", (got, st.get("running")))


# ---------------------------------------------------------------- designer_stage blocks whose item closed

def blocked(d, on, **extra):
    st = DS.load_state(d)
    st.update(status="blocked", blocked_on=on, **extra)
    DS.write_json(DS.state_path(d), st)


def t_closed_block_lifts_at_open(tmp):
    repo = repo_at(tmp)
    d = concept(tmp, "Lift")
    blocked(d, "SOME_FIX_ITEM: the gate needs it")
    with patched(DS, "closed_items", lambda r: {"SOME_FIX_ITEM": "done"}):
        before = sha(DS.state_path(d))
        got = crash_or(DS.open_run, d, "p1", repo=repo, commit=False)
        check("closed-block-lifts-at-open: the preview opens past it and writes nothing",
              isinstance(got, tuple) and sha(DS.state_path(d)) == before, got)
        got = crash_or(DS.open_run, d, "r1", repo=repo)
    st = DS.load_state(d)
    check("closed-block-lifts-at-open: the open writes the lift, its history naming the item and its state",
          isinstance(got, tuple) and st["status"] != "blocked" and "blocked_on" not in st and any(
              h.get("what") == "unblock" and "SOME_FIX_ITEM is done" in h.get("why", "") for h in st["history"]),
          (got, st.get("status"), st["history"][-3:]))


def t_closed_block_keeps_holds_stops_and_unread(tmp):
    repo = repo_at(tmp)
    closed = {"SOME_FIX_ITEM": "done", RC.ALARM_ID: "done", "OPEN_ONE_ITEM": None}
    cases = (("an open item", "OPEN_ONE_ITEM: still owed", {}, {"OPEN_ONE_ITEM_X": "done"}),
             ("the coverage alarm id", "%s: 3 not_covered verdicts" % RC.ALARM_ID, {}, closed),
             ("an owner hold", "SOME_FIX_ITEM: OWNER HOLD, not a refusal", {}, closed),
             ("a standing coverage stop", "SOME_FIX_ITEM: x", {"coverage_stop": {"at": "t", "why": "w"}}, closed),
             ("a cleanse block", "SOME_FIX_ITEM: x", {"cleanse": {"digest": "d"}}, closed),
             ("an unread ledger", "SOME_FIX_ITEM: x", {}, None),
             ("a reason that names no item first", "waiting on the ladder: SOME_FIX_ITEM", {}, closed))
    for i, (what, on, extra, cl) in enumerate(cases):
        d = concept(tmp, "Keep%d" % i)
        blocked(d, on, **extra)
        with patched(DS, "closed_items", lambda r, cl=cl: None if cl is None else dict(cl)):
            got = crash_or(DS.open_run, d, "r1", repo=repo)
        st = DS.load_state(d)
        check("closed-block-keeps-holds-stops-and-unread: %s keeps the block (open refuses BLOCKED)" % what,
              isinstance(got, str) and "BLOCKED" in got and st["status"] == "blocked" and st["blocked_on"] == on,
              (got, st.get("status")))


def t_unblock_closed_sweep_reads_or_refuses(tmp):
    repo = repo_at(tmp)
    root = os.path.join(tmp, "sweep", "design", "concepts")
    a, b = concept(os.path.join(tmp, "sweep"), "A"), concept(os.path.join(tmp, "sweep"), "B")
    blocked(a, "SOME_FIX_ITEM: x")
    blocked(b, "STILL_OPEN_ITEM: y")
    with patched(DS, "closed_items", lambda r: None):
        got = crash_or(DS.unblock_closed, root, repo, True)
    check("unblock-closed-sweep-reads-or-refuses: an unread ledger refuses UNMEASURED and lifts nothing",
          isinstance(got, str) and "UNMEASURED" in got and DS.load_state(a)["status"] == "blocked", got)
    with patched(DS, "closed_items", lambda r: {"SOME_FIX_ITEM": "superseded"}):
        dry = DS.unblock_closed(root, repo, False)
        check("unblock-closed-sweep-reads-or-refuses: dry names the one closed block and writes nothing",
              [os.path.basename(x) for x, _ in dry] == ["A"] and DS.load_state(a)["status"] == "blocked", dry)
        DS.unblock_closed(root, repo, True)
    check("unblock-closed-sweep-reads-or-refuses: apply lifts A only",
          DS.load_state(a)["status"] == "ready" and DS.load_state(b)["status"] == "blocked")
    with patched(DS, "closed_items", lambda r: {}):
        none = DS.unblock_closed(os.path.join(tmp, "sweep", "design", "concepts"), repo, False)
    check("unblock-closed-sweep-reads-or-refuses: a read ledger with nothing closed is [] (looked, none)",
          none == [], none)


def t_open_preview_writes_nothing(tmp):
    repo = repo_at(tmp)
    d = concept(tmp, "Prev")
    before = sha(DS.state_path(d))
    out = io.StringIO()
    with patched(DS, "REPO", repo), contextlib.redirect_stdout(out):
        rc = DS.open_preview(d, "launch-check")
    check("open-preview-writes-nothing: a fresh concept would open (exit 0), no packet, stage.json unchanged",
          rc == 0 and "would open" in out.getvalue() and "===" not in out.getvalue()
          and sha(DS.state_path(d)) == before, (rc, out.getvalue()[-200:]))
    blocked(d, "OPEN_THING_ITEM: owed")
    before = sha(DS.state_path(d))
    with patched(DS, "closed_items", lambda r: {}), patched(DS, "REPO", repo), contextlib.redirect_stdout(out):
        rc = DS.open_preview(d, "launch-check")
    check("open-preview-writes-nothing: a blocked concept refuses (exit 1) and stays byte-identical",
          rc == 1 and sha(DS.state_path(d)) == before, rc)


# ---------------------------------------------------------------- coverage_judge stale refusals

def answer(verdict, gaps=()):
    return json.dumps({"structured_output": {"verdict": verdict, "gaps": list(gaps), "reasons": "r", "checklist": []},
                       "session_id": "sess", "usage": {"input_tokens": 10, "output_tokens": 2}})


def judge_concept(root):
    d = os.path.join(root, "design", "concepts", "Foo")
    os.makedirs(d, exist_ok=True)
    os.makedirs(os.path.join(root, os.path.dirname(CT.OWNER_SHARD)), exist_ok=True)
    put(d, "stage.json", {"stage": 5, "status": "open", "item": "FOO_ITEM",
                          "budget": {"cap": 4000000, "reserve": 60000, "spent": 0, "charges": []}})
    put(d, "tree.json", {"kind": "mod", "leaves": []})
    with open(os.path.join(d, "sheet.md"), "w") as f:
        f.write("sheet\n")
    put(d, "scenes.json", {"scenes": []})
    return d


def t_stale_refusal_counts_no_strike(tmp):
    gap = {"what": "w", "where": "x", "return_to": 3}
    saved = {k: getattr(CJ, k) for k in ("CONTRACT", "delta_plan", "NOT_COVERED_LIMIT")}
    saved_ct = (CT.coverage_problem, DS.exam_errors, DS.owner_away, RC.status)
    env = {k: os.environ.get(k) for k in ("RM_REFUSAL_DIR", "RM_OPS_WATCH_DIR", "RM_DISPATCHER_STATE")}
    try:
        CJ.CONTRACT = False
        CJ.delta_plan = lambda d, prior, read=None: None
        CJ.NOT_COVERED_LIMIT = 1
        CT.coverage_problem = lambda d, repo, tree: "no coverage signature"
        DS.exam_errors = lambda ex, d, st, repo=None: []
        DS.owner_away = lambda: (False, "selftest: attended")
        RC.status = lambda family: "CALIBRATED"
        root = os.path.join(tmp, "cj")
        os.makedirs(os.path.join(root, "ops"))
        os.environ.update(RM_REFUSAL_DIR=os.path.join(root, "refusals"), RM_OPS_WATCH_DIR=os.path.join(root, "ops"),
                          RM_DISPATCHER_STATE=os.path.join(root, "dispatcher"))
        d = judge_concept(root)

        def moving(argv, cwd, env, timeout):     # the Designer edits scenes.json while the judge reads
            put(d, "scenes.json", {"scenes": [{"id": "new"}]})
            return 0, answer("not_covered", [gap])
        rec, msg = CJ.run(d, root, moving, now=1793900000)
        st = DS.load_state(d)
        rnd = (st.get("coverage_rounds") or [{}])[-1]
        check("stale-refusal-counts-no-strike: the refusal names the moved input and is advisory",
              rec.get("stale_inputs") == ["scenes.json"] and "scenes.json" in str(rec.get("advisory")), rec)
        check("stale-refusal-counts-no-strike: its round carries stale_inputs and is no refusal",
              rnd.get("stale_inputs") == ["scenes.json"] and not CJ.is_refusal(rnd)
              and DS.refusals_since_loop(st) == 0, rnd)
        check("stale-refusal-counts-no-strike: at a limit of 1 it stops nothing and writes no block",
              CJ.stop_reason(st, d) is None and st.get("status") != "blocked" and "stopped" not in msg, (msg, st.get("status")))
        check("stale-refusal-counts-no-strike: the next plan judges again (a stale advisory waits on nothing)",
              CJ.plan(d, root)[0] == "judge", CJ.plan(d, root))

        def still(argv, cwd, env, timeout):
            return 0, answer("not_covered", [gap])
        rec, msg = CJ.run(d, root, still, now=1793900100)
        st = DS.load_state(d)
        check("stale-refusal-counts-no-strike: a refusal on unchanged inputs is a strike and stops at the limit",
              not rec.get("stale_inputs") and CJ.is_refusal(st["coverage_rounds"][-1])
              and DS.refusals_since_loop(st) == 1 and "stopped" in msg and st.get("status") == "blocked", (msg, rec))
    finally:
        for k, v in saved.items():
            setattr(CJ, k, v)
        CT.coverage_problem, DS.exam_errors, DS.owner_away, RC.status = saved_ct
        for k, v in env.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v


# ---------------------------------------------------------------- bar_rule

def t_experience_gap_naming_a_def_word_blocks():
    eat = {"what": "The player cannot eat the fruit.", "would_pass": "A pawn eats the fruit and the meal completes.",
           "smallest_fix": {"what": "Repair its ingestible definition so the eating action completes."}}
    b, why = BR.blocks(eat)
    check("experience-gap-naming-a-def-word-blocks: the eat-the-fruit gap blocks", b is True, why)
    contagion = {"what": "The selftest does not cover the plants' fields",
                 "would_pass": "The selftest covers every rostered plant's ingestible and yield fields",
                 "smallest_fix": {"what": "add the rows"}}
    b, why = BR.blocks(contagion)
    check("experience-gap-naming-a-def-word-blocks: the Contagion ingestible and yield fields stay advisory",
          b is False and "tuning_number" in str(why), why)


# ---------------------------------------------------------------- launch_checks

def t_gate_preview_blocks_are_one_must_pass():
    ok = True
    for kind, kw in (("designer_open", {"mod": "Foo"}), ("coverage_judge", {"mod": "Foo"}),
                     ("certify", {"mod": "Foo", "owner_event": "OWNER:12"})):
        b = crash_or(LC.block_for, kind, **kw)
        ok = ok and isinstance(b, str) and not b.startswith("CRASH") and \
            [c["kind"] for c in LC.parse(b)] == ["must-pass"] and "design/concepts/Foo" in b
    bad = [crash_or(LC.block_for, k, **kw) for k, kw in (
        ("designer_open", {"mod": None}), ("coverage_judge", {"mod": "a b"}), ("certify", {"mod": "Foo"}),
        ("certify", {"mod": "Foo", "owner_event": "OWNER:"}), ("designer_open", {"mod": "../x"}))]
    check("gate-preview-blocks-are-one-must-pass: each gate's block parses as one must-pass; a bad mod or event "
          "raises ValueError", ok and all(isinstance(x, str) and x.startswith("CRASH ValueError") for x in bad), bad)
    check("gate-preview-blocks-are-one-must-pass: an unclassed plan value is could-not-look (126), never 0 or 1",
          CJ.WOULD_JUDGE_EXIT.get("something_new", 126) == 126 and CJ.WOULD_JUDGE_EXIT["judge"] == 0)


def t_exam_retake_steward_carries_the_open_gate():
    import maturation_autonomy as MA
    got = crash_or(MA.advance_checks, {"steward_kind": "exam_retake", "mod": "Foo", "stage": "designer"})
    check("exam-retake-steward-carries-the-open-gate: the exam_retake row's block is the Designer open preview",
          got == LC.block_for("designer_open", mod="Foo") and [c["kind"] for c in LC.parse(got)] == ["must-pass"], got)
    ready = crash_or(MA.advance_checks, {"steward_kind": "ready", "mod": "Foo", "stage": "offline_build"})
    route = crash_or(MA.advance_checks, {"steward_kind": "exit_not_met", "mod": "Foo", "stage": "in_game"})
    check("exam-retake-steward-carries-the-open-gate: a ready row keeps its advance block, a routing row gets none",
          isinstance(ready, str) and "maturation.py gate Foo --to blind_challenge" in ready and route is None,
          (ready, route))


def guarded(fn, tmp):
    """Run one temp-dir test; a crash is that test's failure, never the end of the run."""
    sub = tempfile.mkdtemp(dir=tmp)
    try:
        fn(sub)
    except Exception as e:
        check("%s ran to the end" % fn.__name__, False, "CRASH %s: %s" % (type(e).__name__, e))


def stub_ledger():
    """The temp repos have no ledger to fold: no item is done or closed (a test patches closed_items itself)."""
    saved = DS.done_items, getattr(DS, "closed_items", None)
    DS.done_items = lambda repo: {}
    DS.closed_items = lambda repo: {}
    return saved


def main():
    tmp = tempfile.mkdtemp(prefix="judge_gates_")
    saved = stub_ledger()
    try:
        guarded(t_close_run_rejects_non_string_ids, tmp)
        guarded(t_close_run_never_raises_on_a_result_shape, tmp)
        guarded(t_closed_block_lifts_at_open, tmp)
        guarded(t_closed_block_keeps_holds_stops_and_unread, tmp)
        guarded(t_unblock_closed_sweep_reads_or_refuses, tmp)
        guarded(t_open_preview_writes_nothing, tmp)
        guarded(t_stale_refusal_counts_no_strike, tmp)
        t_experience_gap_naming_a_def_word_blocks()
        t_gate_preview_blocks_are_one_must_pass()
        t_exam_retake_steward_carries_the_open_gate()
    finally:
        DS.done_items, DS.closed_items = saved
    print("%s: %d failure(s)" % ("FAIL" if FAILS else "PASS", len(FAILS)))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
