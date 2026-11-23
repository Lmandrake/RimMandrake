#!/usr/bin/env python3
"""Acceptance test of RIMMANDRAKE_TEACH_EXIT_READER_KINDS_KNOWS_THREE_WORDS_ONLY: the Stage 6 exit reader knows the three
test kinds and the seven outcomes (design/RimMandrake/standing_rulings.md §Live tests have three kinds).

The fields that the ticket fixes:
  test_table.json  tests.<id>.test_kind "A" | "B" | "C" (absent = "A"); tag_evidence (text); budget (runs, kind B);
                   x_of_y [X, Y] (a result random by design)
  rows.jsonl       outcome, one of the seven; spoiled_by (what spoiled the run and the record that shows it);
                   forbidden [effects seen]
`must_stay` rows are green on the base commit too. Offline: temp roots, the build match stubbed.
Run: python3 design/specs/2026-11-23-three-test-kinds/accept_exit_reader_kinds.py   (exit 0 only when every row is ok)"""
import copy
import os
import subprocess
import sys
import tempfile

REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", ".."))
RF = os.path.join(REPO, "src", "RimMandrake", "rimflow")
sys.path.insert(0, RF)
import selftest_wrong_check_fixed_in_sitting as S  # noqa: E402

OTHERS = [S.row("c2"), S.row("c3")]
SPOILED = "the carrier left for food: evidence/trace_c1.json, job Ingest at tick 1200"
N = [0]


def table(**c1):
    tt = copy.deepcopy(S.TT6)
    tt["tests"]["c1"].update(c1)
    return tt


def read(rows, **c1):
    N[0] += 1
    return S.ingame(rows + OTHERS, name="kinds%d" % N[0], tt=table(**c1))


def said(ex, *words):
    t = " ".join(ex["why"]).lower()
    return all(w.lower() in t for w in words)


B = dict(test_kind="B", tag_evidence="colonists leave for food; needs frozen and the door locked; jobs still interrupt", budget=3)


def env(verdict="UNMEASURED", **kw):
    return S.row("c1", verdict, outcome="ENVIRONMENT FAULT", **dict({"spoiled_by": SPOILED}, **kw))


def good(**kw):
    return S.row("c1", "PASS", outcome="SUCCESS", **kw)


def t_must_stay_plain_pass_is_met():
    return read([S.row("c1")])["state"] == "met"


def t_must_stay_mod_failure_still_blocks():
    return read([S.row("c1", "FAIL", outcome="MOD FAILURE", **{"class": "MOD"}), good()])["state"] == "not_met"


def t_environment_fault_needs_no_later_pass_to_cancel_it():
    """A FAIL word beside an ENVIRONMENT FAULT that its record shows is no FAIL against the mod."""
    return read([env(verdict="FAIL"), good()])["state"] == "met"


def t_environment_fault_with_no_record_reads_unresolved():
    ex = read([env(spoiled_by=""), good()])
    return ex["state"] == "not_met" and said(ex, "c1", "UNRESOLVED")


def t_unresolved_holds_the_pass():
    ex = read([S.row("c1", "UNMEASURED", outcome="UNRESOLVED"), good()])
    return ex["state"] == "not_met" and said(ex, "c1", "UNRESOLVED")


def t_forbidden_effect_in_a_spoiled_run_is_mod_failure():
    ex = read([env(forbidden=["a pawn lost"]), good()])
    return ex["state"] == "not_met" and ex["lines"]["c1"]["count"] == "mod"


def t_last_run_spoiled_says_run_that_scene_again():
    ex = read([env()])
    return ex["state"] == "not_met" and ex["lines"]["c1"]["count"] == "spoiled" and said(ex, "c1", "again")


def t_kind_b_budget_done_with_no_success_is_inconclusive():
    ex = read([env(), env(), env()], **B)
    return ex["state"] == "not_met" and ex["rows"]["c1"] == "INCONCLUSIVE"


def t_kind_b_one_success_passes():
    return read([env(verdict="FAIL"), good(), env(verdict="FAIL")], **B)["state"] == "met"


def t_random_by_design_passes_on_x_of_y():
    miss = S.row("c1", "FAIL", outcome="RANDOM MISS")
    tag = dict(B, x_of_y=[2, 4], budget=4)
    two = read([good(), miss, good(), miss], **tag)
    one = read([good(), miss, miss, miss], **tag)
    return two["state"] == "met" and one["state"] == "not_met"


def t_random_miss_on_kind_a_is_refused():
    ex = read([S.row("c1", "UNMEASURED", outcome="RANDOM MISS"), good()])
    return ex["state"] == "not_met" and said(ex, "c1", "RANDOM MISS")


def t_tag_with_no_evidence_is_refused():
    ex = read([good()], test_kind="B", tag_evidence="", budget=3)
    return ex["state"] == "not_met" and said(ex, "c1", "tag")


def t_hunt_is_never_part_of_the_exit():
    """A kind C row does not hold the exit and does not decide it."""
    tt = copy.deepcopy(S.TT6)
    tt["tests"]["hunt"] = {"kind": "live", "stage": "6", "command": "python3 h.py", "test_kind": "C",
                           "tag_evidence": "raider lifted out of a pit: 1 of 18; trace evidence/rim.json"}
    N[0] += 1
    return S.ingame([S.row("c1")] + OTHERS, name="kinds%d" % N[0], tt=tt)["state"] == "met"


def t_unknown_outcome_word_is_refused():
    ex = read([S.row("c1", outcome="FLAKY")])
    return ex["state"] == "not_met" and said(ex, "FLAKY")


def t_driver_brief_carries_the_kinds():
    root = S.visit("kinds_brief", [S.row("c1")] + OTHERS)
    text = S.M.ingame_brief_text(root, S.MOD)[0]
    return all(w in text for w in ("ENVIRONMENT FAULT", "UNRESOLVED", "INCONCLUSIVE", "HUNT OPENED"))


def t_hunt_open_tells_the_conductor_and_refuses_a_blank():
    tool = os.path.join(RF, "hunt_open.py")
    log = os.path.join(tempfile.mkdtemp(prefix="hunt_"), "log.md")
    e = dict(os.environ, RM_CONDUCTOR_LOG=log, RM_HUNT_OPEN_NO_NOTE="1")
    full = ["RIMMANDRAKE_HUNT_WMOD_RAIDER_LIFTED_OUT_ONCE", "--what", "lifted once in 18", "--why-it-matters",
            "a prisoner escapes", "--next-step", "order the rescue", "--cost", "one scene load"]
    a = subprocess.run([sys.executable, tool] + full, env=e, capture_output=True, text=True, cwd=REPO)
    b = subprocess.run([sys.executable, tool] + full[:-1] + [""], env=e, capture_output=True, text=True, cwd=REPO)
    lines = open(log, encoding="utf-8").read() if os.path.exists(log) else ""
    return (a.returncode == 0 and b.returncode != 0 and lines.count("HUNT OPENED") == 1 and "RAISE FIRST" in lines
            and all(w in lines for w in ("lifted once in 18", "order the rescue", "one scene load")))


def main():
    bad = 0
    for k, f in sorted((k, f) for k, f in globals().items() if k.startswith("t_")):
        try:
            ok = bool(f())
            note = ""
        except Exception as e:      # noqa: BLE001  a crash is not a pass
            ok, note = False, " (%s: %s)" % (type(e).__name__, e)
        bad += not ok
        print("%s %s%s" % ("ok  " if ok else "FAIL", k[2:], note))
    print("%s: %d failed" % ("PASS" if not bad else "FAIL", bad))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
