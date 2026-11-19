#!/usr/bin/env python3
"""Selftest: what a coverage sign-off resets, and what closes a repaired slot.

One test per promise on design/specs/2026-11-19-coverage-signoff-and-slots/boundary.md (same names, t_ prefix).
Items RIMMANDRAKE_RESET_COVERAGE_STRIKES_AFTER_SIGNOFF_OLD_TWO_COUNTED and
RIMMANDRAKE_REQUIRE_PASSING_ROW_TO_CLOSE_REPAIRED_SLOT. The control store is a throwaway one (RM_CONTROL_DB).

  python3 src/RimMandrake/rimflow/selftest_coverage_signoff.py
"""
import json
import os
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import coverage_judge as CJ  # noqa: E402

FAILS = []
NC, OK, BAD = "not_covered", "covered", "malformed"


def check(name, ok, detail=""):
    print(("PASS " if ok else "FAIL ") + name + ("" if ok else "  -- %r" % (detail,)))
    if not ok:
        FAILS.append(name)


def st(vs, releases=None, tokens=1000):
    rs = [{"judge": "j%d" % i, "at": "2026-11-19T%02d:00:00Z" % i, "verdict": v, "tokens": tokens}
          for i, v in enumerate(vs)]
    out = {"coverage_rounds": rs}
    if releases is not None:
        out["coverage_releases"] = releases
    return out


def t_strikes_count_from_the_last_sign_off(tmp):
    check("strikes-count-from-the-last-sign-off: nc, nc, covered, nc does not stop (Graffiti 2026-11-17)",
          CJ.stop_reason(st([NC, NC, OK, NC])) is None, CJ.stop_reason(st([NC, NC, OK, NC])))
    check("strikes-count-from-the-last-sign-off: nc, nc, covered does not stop",
          CJ.stop_reason(st([NC, NC, OK])) is None, CJ.stop_reason(st([NC, NC, OK])))


def t_runs_and_spend_count_from_the_last_sign_off(tmp):
    runs = [NC, OK] * CJ.JUDGE_RUNS_MAX            # 2x the run cap, every episode ending in a sign-off
    check("runs-and-spend-count-from-the-last-sign-off: runs before the last sign-off are not counted",
          CJ.stop_reason(st(runs + [NC])) is None, CJ.stop_reason(st(runs + [NC])))
    big = CJ.JUDGE_SPEND_MAX                       # one round alone reaches the spend cap
    check("runs-and-spend-count-from-the-last-sign-off: spend before the last sign-off is not counted",
          CJ.stop_reason(st([OK, NC], tokens=big // 2 + 1)) is None, CJ.stop_reason(st([OK, NC], tokens=big // 2 + 1)))
    s = st([OK, NC], tokens=big)
    s["coverage_rounds"][0]["tokens"] = big
    s["coverage_rounds"][1]["tokens"] = 1
    check("runs-and-spend-count-from-the-last-sign-off: a big spend that ended in a sign-off is not counted",
          CJ.stop_reason(s) is None, CJ.stop_reason(s))


def t_the_strike_limit_still_binds_without_a_sign_off(tmp):
    for vs in ([NC] * CJ.NOT_COVERED_LIMIT, [OK] + [NC] * CJ.NOT_COVERED_LIMIT, [NC, OK] + [NC] * CJ.NOT_COVERED_LIMIT):
        why = CJ.stop_reason(st(vs))
        check("the-strike-limit-still-binds-without-a-sign-off: %s stops" % ",".join(vs), bool(why), why)
    why = CJ.stop_reason(st([NC], tokens=CJ.JUDGE_SPEND_MAX))
    check("the-strike-limit-still-binds-without-a-sign-off: the spend cap binds with no sign-off",
          bool(why) and "spend" in why, why)
    errs = st([OK] + [None] * CJ.JUDGE_RUNS_MAX)
    for r in errs["coverage_rounds"][1:]:
        r.update(error="exited 1", error_kind="judge")
    why = CJ.stop_reason(errs)
    check("the-strike-limit-still-binds-without-a-sign-off: the run cap binds on runs after a sign-off",
          bool(why) and "judge runs since the sign-off" in why, why)
    why = CJ.stop_reason(st([NC, NC], releases=[{"rounds_at": 1}]))
    check("the-strike-limit-still-binds-without-a-sign-off: a release's one look still stops on its refusal",
          bool(why) and "one more look" in why, why)


def t_a_sign_off_after_a_release_ends_the_release(tmp):
    s = st([NC, NC, OK, NC], releases=[{"rounds_at": 2}])
    why = CJ.stop_reason(s)
    check("a-sign-off-after-a-release-ends-the-release: release, covered, nc does not stop", why is None, why)
    s = st([NC, NC, OK, NC, NC], releases=[{"rounds_at": 2}])
    why = CJ.stop_reason(s)
    check("a-sign-off-after-a-release-ends-the-release: two strikes after that sign-off stop as strikes",
          bool(why) and "not_covered verdicts" in why, why)


def t_malformed_verdicts_are_not_reset_by_a_sign_off(tmp):
    s = st([BAD] * CJ.MALFORMED_LIMIT + [OK])
    why = CJ.stop_reason(s)
    check("malformed-verdicts-are-not-reset-by-a-sign-off: no release", bool(why) and "malformed" in why, why)
    s = st([BAD] * CJ.MALFORMED_LIMIT + [OK], releases=[{"rounds_at": 0}])
    why = CJ.stop_reason(s)
    check("malformed-verdicts-are-not-reset-by-a-sign-off: after a release", bool(why) and "malformed" in why, why)


def t_pipe_show_counts_the_window_the_stop_reads(tmp):
    import pipeline_control as PC
    root = os.path.join(tmp, "root")
    cases = {"Signed": st([NC, NC, OK, NC]), "Plain": st([NC, NC]),
             "RelSigned": st([NC, NC, OK, NC], releases=[{"rounds_at": 2}]), "Rel": st([NC, NC], releases=[{"rounds_at": 1}])}
    for mod, s in cases.items():
        d = os.path.join(root, "design", "concepts", mod)
        os.makedirs(d)
        with open(os.path.join(d, "stage.json"), "w") as f:
            json.dump(s, f)
    ctx = PC.Ctx(root=root)
    want = {"Signed": (1, 1, None), "Plain": (2, 2, None), "RelSigned": (1, 1, None), "Rel": (None, 1, 1)}
    for mod, (nc, runs, look) in want.items():
        got = (PC.RESOURCES["coverage_not_covered"][2](ctx, mod)[0], PC.RESOURCES["coverage_runs"][2](ctx, mod)[0],
               PC.RESOURCES["granted_look"][2](ctx, mod)[0])
        check("pipe-show-counts-the-window-the-stop-reads: %s cov-nc, cov-runs, look" % mod, got == (nc, runs, look), got)


def _slot_case():
    """The Codex scenario (2026-11-18, round 2 finding 1): prior gap g1 on leaf_wall, whose checklist part failed; only
    the sheet changed; no fix claim; the judge answers repaired with an empty checklist and no gaps."""
    prior_row = {"id": "leaf_wall", "parts": [{"part": "scene", "ok": False}]}
    g1 = {"gid": "g1", "ids": ["leaf_wall"], "what": "the leaf wall scene runs with the wall off"}
    dp = {"claims": [], "refused": [], "changed": ["sheet:sheet"], "against": "jprior", "prior_checklist": [prior_row],
          "entries": {}, "ids": [], "claimed_gaps": [], "carried": [g1], "loose": True}
    return g1, prior_row, dp


def t_a_repaired_slot_closes_only_with_a_passing_row_per_id(tmp):
    g1 = {"gid": "g1", "ids": ["a", "b"]}
    rep = [{"gap": "g1", "repaired": True}]
    good = [{"id": "a", "parts": [{"ok": True}]}, {"id": "b", "parts": [{"ok": True}]}]
    closed, still, _ = CJ._slots([g1], [], rep, [])
    check("a-repaired-slot-closes-only-with-a-passing-row-per-id: no rows, stays open", not closed and still, closed)
    closed, still, _ = CJ._slots([g1], good[:1], rep, [])
    check("a-repaired-slot-closes-only-with-a-passing-row-per-id: one id of two, stays open", not closed, closed)
    closed, still, _ = CJ._slots([g1], [good[0], {"id": "b", "parts": [{"ok": False}]}], rep, [])
    check("a-repaired-slot-closes-only-with-a-passing-row-per-id: a failing row, stays open", not closed, closed)
    closed, still, _ = CJ._slots([g1], good, rep, [])
    check("a-repaired-slot-closes-only-with-a-passing-row-per-id: every id passing, closes", closed == [g1], still)
    closed, still, _ = CJ._slots([g1], good, [{"gap": "g1", "repaired": False}], [])
    check("a-repaired-slot-closes-only-with-a-passing-row-per-id: passing rows but not repaired, stays open",
          not closed, closed)


def t_a_claimed_slot_is_owed_its_rows(tmp):
    d = os.path.join(tmp, "concept_owed")
    os.makedirs(d)
    prior = {"verdict": NC, "hashes": {}, "judge": "jprior",
             "gaps": [{"gid": "g1", "ids": ["leaf_wall"], "what": "x"}, {"gid": "g2", "ids": ["sky_lock"], "what": "y"}],
             "checklist": [{"id": "leaf_wall", "parts": [{"ok": False}]}]}
    saved = (CJ.entries, CJ.entry_hashes, CJ.fix_claims)
    CJ.entries = lambda d, read=None: {}
    CJ.entry_hashes = lambda d, read=None: {}
    CJ.fix_claims = lambda d, prior: ([{"gap": "g1", "evidence": "the wall now stands in sc_a"}], [])
    try:
        dp = CJ.delta_plan(d, prior)
    finally:
        CJ.entries, CJ.entry_hashes, CJ.fix_claims = saved
    check("a-claimed-slot-is-owed-its-rows: the claimed slot's ids are asked for, the unclaimed one's are not",
          dp is not None and dp["ids"] == ["leaf_wall"], dp and dp["ids"])
    text = CJ.delta_prompt(d, tmp, dp, 2) if dp else ""
    check("a-claimed-slot-is-owed-its-rows: the prompt names it in the rows it asks for",
          "none skipped: leaf_wall." in text, text[-400:])
    check("a-claimed-slot-is-owed-its-rows: the prompt says a carried slot needs a row on every id to close",
          "write a row for every one of its ids" in text, text)


def t_an_unchecked_repair_never_signs(tmp):
    g1, prior_row, dp = _slot_case()
    rec = {"verdict": OK, "checklist": [], "gaps": []}
    out = CJ.delta_merge(rec, dp, repairs=[{"gap": "g1", "repaired": True, "evidence": "sheet reworded"}])
    check("an-unchecked-repair-never-signs: the verdict is not_covered", out["verdict"] == NC, out["verdict"])
    check("an-unchecked-repair-never-signs: g1 is still open, carried",
          any(g.get("gid") == "g1" and g.get("carried") for g in out["gaps"]) and not out.get("answered"), out)


def main():
    import control as C
    tmp = tempfile.mkdtemp(prefix="selftest_coverage_signoff_")
    keep = {k: os.environ.get(k) for k in ("RM_CONTROL_DB", "RM_UNDER_SELFTEST")}
    try:
        os.environ["RM_CONTROL_DB"] = os.path.join(tmp, "control.db")
        os.environ["RM_UNDER_SELFTEST"] = "1"
        C.init(os.environ["RM_CONTROL_DB"])
        t_strikes_count_from_the_last_sign_off(tmp)
        t_runs_and_spend_count_from_the_last_sign_off(tmp)
        t_the_strike_limit_still_binds_without_a_sign_off(tmp)
        t_a_sign_off_after_a_release_ends_the_release(tmp)
        t_malformed_verdicts_are_not_reset_by_a_sign_off(tmp)
        t_pipe_show_counts_the_window_the_stop_reads(tmp)
        t_a_repaired_slot_closes_only_with_a_passing_row_per_id(tmp)
        t_a_claimed_slot_is_owed_its_rows(tmp)
        t_an_unchecked_repair_never_signs(tmp)
    finally:
        for k, v in keep.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v
    print("selftest_coverage_signoff: %s (%d failure(s))" % ("FAIL" if FAILS else "PASS", len(FAILS)))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
