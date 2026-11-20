#!/usr/bin/env python3
"""selftest_maturation_game_only_exit: the promises of design/specs/2026-11-19-maturation-game-only-blind-exit/boundary.md,
one test per promise, each named as the promise is. On a game-only move whose `game_only` clause passes, the blind
exit does not count the new blind judge owed for the cycle's own FIXED Problems, nor lane-1 not_kernel rows whose bars
named game-only items carry (RIMMANDRAKE_UNBLOCK_GAME_ONLY_ADVANCE_AT_BLIND_EXIT); every other gap still refuses. No
game, no network; every file is in a temp root."""
import json
import os
import shutil
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
TMP = tempfile.mkdtemp(prefix="mat_goexit_")
os.environ["RM_DISPATCHER_STATE"] = os.path.join(TMP, "_dispatcher")
import maturation as M  # noqa: E402

FAILS = []
MOD = "GMod"
TT = {"version": "0.1.0", "tests": {"t1": {"command": "python3 t1.py"}, "t2": {"command": "python3 t2.py"}},
      "bars": [{"id": "b_off1", "proves_at": "4-5", "decides": ["t1"]},
               {"id": "b_off2", "proves_at": "4-5", "decides": ["t2"]},
               {"id": "b_live", "proves_at": "6", "decides": []}]}
BOTH = {"b_off1": ["G1"], "b_off2": ["G2"]}     # the bars the move's two game-only items carry


def check(ok, name, got=""):
    print("%s  %s%s" % ("PASS" if ok else "FAIL", name, "" if ok else "  got: %r" % (got,)))
    if not ok:
        FAILS.append(name)


def put(root, rel, data):
    p = os.path.join(root, rel)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "w", encoding="utf-8") as f:
        f.write(data if isinstance(data, str) else json.dumps(data))


def lines(rows):
    return "".join(json.dumps(r) + "\n" for r in rows)


def make(name, judge_true=False, fixed=True, unfixed=False, fix_red_rc=1, red_bar=None, rows=None):
    """A fresh root with mod GMod at the blind challenge, cycle 1 in the FORMAT_NOTES layout. Default: the judge says
    exit_met false, one Problem FIXED (shown red then green), lane 1 leaves one not_kernel UNSETTLED row on each offline
    bar, before and after the fixes."""
    root = os.path.join(TMP, name)
    shutil.rmtree(root, ignore_errors=True)
    c = "design/concepts/%s/" % MOD
    cy = c + "version/blind_challenge/cycle_1/"
    put(root, c + "version/test_table.json", TT)
    put(root, c + "version/VERSION.json", {"version": "0.1.0"})
    put(root, c + "version/stage_record.json", {
        "mod": MOD, "version": "0.1.0", "stage": "blind_challenge", "since": "2026-11-19T10:00:00Z",
        "cycles": {"total": 1, "visit": 1},
        "moves": [{"from": "offline_build", "to": "blind_challenge", "at": "2026-11-19T09:00:00Z"},
                  {"from": "in_game", "to": "blind_challenge", "at": "2026-11-19T10:00:00Z"}]})
    put(root, c + "journal.md", "# journal\n")
    put(root, cy + "SUMMARY.md", "# cycle 1\n\n## Exit\noffline_bars: {b_off1: %s, b_off2: green}\nproblems_open: %d\n"
        "exit_met: %s\n" % ("red" if red_bar else "green", 1 if unfixed else 0, "true" if judge_true else "false"))
    put(root, cy + "lane2/reruns.jsonl", lines([{"test": t, "command": "python3 %s.py" % t, "rc": 0, "result": "PASS"}
                                                for t in ("t1", "t2")]))
    faults = [{"id": "FIX_A", "class": "Problem", "status": "FIXED abc1234"} if fixed else
              {"id": "POL_A", "class": "Polish", "status": "NOTED_FOR_CONDUCTOR"}]
    if unfixed:
        faults.append({"id": "OPEN_B", "class": "Problem", "status": "NOTED_FOR_CONDUCTOR"})
    put(root, cy + "lane2/faults.json", {"faults": faults})
    put(root, cy + "lane2/fixes.jsonl", lines([{"fault": "FIX_A", "red": {"cmd": "python3 t1.py", "rc": [fix_red_rc]},
                                                "green": {"cmd": "python3 t1.py", "rc": [0]}}] if fixed else []))
    rows = rows if rows is not None else [{"id": "R1", "kind": "not_kernel", "verdict": "UNSETTLED", "bars": ["b_off1"]},
                                          {"id": "R2", "kind": "not_kernel", "verdict": "UNSETTLED", "bars": ["b_off2"]}]
    put(root, cy + "lane1/lane1_rows.jsonl", lines([{"id": "L_ok", "verdict": "PASS"}] + rows))
    put(root, cy + "lane2/lane1_rows_after_fix.jsonl", lines(rows))
    put(root, cy + "tests_edited.json", {"edited": []})
    put(root, cy + "lane2/planted_results.jsonl", lines([{"baseline": True}, {"id": "PF", "caught": True,
                                                                              "tree_clean_after": True},
                                                         {"tree_clean_after": True}]))
    ev = [{"seat": "CONDUCTOR", "event": "file", "id": i, "title": "GMod 0.1.0 %s in game: shown live" % b,
           "kind": "task", "needs": "game-up", "caused_by": "PARENT_ITEM", "ts": "2026-11-19T11:00:0%dZ" % k,
           "tsn": 1795000000000000000 + k} for k, (i, b) in enumerate((("G1", "b_off1"), ("G2", "b_off2")))]
    put(root, "infrastructure/state/ledger/events/CONDUCTOR.jsonl", lines(ev))
    return root


def read(root, bars=BOTH):
    return M.read_exit(root, MOD, 1, game_only_bars=bars)


def t_game_only_exit_skips_owed_judge_and_named_rows():
    root = make("happy")
    ex = read(root)
    check(ex["state"] == "met", "the owed judge and two carried rows: met", ex.get("why"))
    check(ex["checks"].get("judge_owed_not_counted_game_only") == ["FIX_A"], "the reading names the fix not re-judged",
          ex["checks"])
    check(ex["checks"].get("lane1_deferred_to_game_only_items") == {"R1": ["G1"], "R2": ["G2"]},
          "the reading names each row's item", ex["checks"])
    check(any("game-only move" in w for w in ex["why"]), "its why says it is the game-only reading", ex["why"])
    check(not any("exit_met true" in w for w in ex["why"]), "its why never says the judge's false was true", ex["why"])
    ex = read(make("judge_true", judge_true=True))
    check(ex["state"] == "met" and "judge_owed" not in ex["checks"], "a judge's true with a FIXED Problem: met, no "
          "owed judge", ex)
    got = []

    def clause(cid, text, good, evidence, **kw):
        got.append((cid, good, kw.get("observed")))
    M.exit_met_clause(root, MOD, M.load(root, MOD), "blind_challenge", None, clause, "r", "q", game_only_bars=BOTH)
    check(got and got[0][0] == "exit_met" and got[0][1] is True, "exit_met_clause with the bars passes", got)
    check(M.bars_named_by(root, MOD, ["G1", "G2"]) == BOTH, "bars_named_by reads each title's bar",
          M.bars_named_by(root, MOD, ["G1", "G2"]))
    check(M.bars_named_by(root, MOD, ["G1"]) == {"b_off1": ["G1"]}, "an unnamed item carries no bar",
          M.bars_named_by(root, MOD, ["G1"]))


def t_unfixed_problem_still_refuses():
    ex = read(make("unfixed", unfixed=True))
    check(ex["state"] == "not_met", "an unfixed Problem: not met", ex.get("why"))
    check(any("not FIXED" in w for w in ex["why"]), "the reading names the open Problem", ex.get("why"))


def t_offline_row_without_named_item_still_refuses():
    ex = read(make("one_named"), bars={"b_off1": ["G1"]})
    check(ex["state"] == "not_met" and any("R2" in w for w in ex["why"]), "a row on a bar no item carries: not met",
          ex.get("why"))
    rows = [{"id": "R12", "kind": "not_kernel", "verdict": "UNSETTLED", "bars": ["b_off1", "b_off2"]}]
    ex = read(make("half_named", rows=rows), bars={"b_off1": ["G1"]})
    check(ex["state"] == "not_met", "a row whose second bar no item carries: not met", ex.get("why"))
    rows = [{"id": "RK", "kind": "kernel", "verdict": "UNSETTLED", "bars": ["b_off1"]}]
    ex = read(make("kernel_row", rows=rows))
    check(ex["state"] == "not_met", "a kernel row is never deferred, carried or not", ex.get("why"))
    ex = read(make("no_bars"), bars={})
    check(ex["state"] == "not_met", "a game-only move whose items carry no bar defers no row", ex.get("why"))


def t_not_game_only_move_unchanged():
    root = make("plain")
    ex = M.read_exit(root, MOD, 1)
    check(ex["state"] == "not_met", "no game_only_bars: not met", ex.get("why"))
    check(ex["why"][0] == M.JUDGE_SAYS_FALSE and any("R1" in w and "R2" in w for w in ex["why"]),
          "the judge's false and both rows block, as before", ex.get("why"))
    ex = M.read_exit(make("plain_true", judge_true=True, rows=[]), MOD, 1)
    check(ex["checks"].get("judge_owed") is True and ex["state"] == "not_met",
          "a cycle's own fixes still owe a new blind judge", ex)
    got = []

    def clause(cid, text, good, evidence, **kw):
        got.append((cid, good, kw.get("observed")))
    rec = M.load(root, MOD)
    M.exit_met_clause(root, MOD, rec, "blind_challenge", None, clause, "r", "q")
    check(got and got[0][0] == "exit_met" and got[0][1] is False, "exit_met_clause without bars refuses", got)


def t_owed_judge_from_other_cause_still_refuses():
    ex = read(make("nothing_fixed", fixed=False))
    check(ex["state"] == "not_met" and ex["why"] == [M.JUDGE_SAYS_FALSE],
          "a judge's false in a cycle that fixed nothing: not met", ex.get("why"))
    ex = read(make("fix_not_red", fix_red_rc=0))
    check(ex["state"] == "not_met" and any("shown red" in w for w in ex["why"]),
          "a FIXED Problem not shown red then green: not met", ex.get("why"))
    ex = read(make("red_bar", red_bar=True))
    check(ex["state"] == "not_met" and any("b_off1 reads red" in w for w in ex["why"]), "a red offline bar: not met",
          ex.get("why"))


def t_evaluate_gives_bars_only_when_game_only_passes():
    seen = []
    real = M.exit_met_clause

    def spy(*a, **kw):
        seen.append(kw.get("game_only_bars"))
        return real(*a, **kw)
    M.exit_met_clause = spy
    try:
        def ev(root, ids):
            seen.clear()
            v = M.evaluate(root, MOD, "in_game", steward="s", conductor="c", by="CONDUCTOR", why="w", check_by=True,
                           game_only=ids)["verdict"]
            return seen[-1] if seen else "exit_met_clause not called", v
        root = make("eval")
        bars, v = ev(root, ["G1", "G2"])
        check(bars == BOTH, "a passing game_only clause hands over the bars", bars)
        check("exit_met" not in [r["clause"] for r in v["refusals"]], "and exit_met then passes",
              [(r["clause"], r["observed"]) for r in v["refusals"]])
        bars, v = ev(root, ["G1"])     # G2 is an open sibling left unnamed: the clause fails
        check(bars is None and "game_only" in [r["clause"] for r in v["refusals"]],
              "a failing game_only clause hands over None", bars)
        check("exit_met" in [r["clause"] for r in v["refusals"]], "and exit_met then refuses", v["refusals"])
        bars, v = ev(root, None)
        check(bars is None and "exit_met" in [r["clause"] for r in v["refusals"]],
              "a move with no --game-only hands over None and exit_met refuses", bars)
    finally:
        M.exit_met_clause = real


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    only = set(argv[argv.index("--only") + 1:]) if "--only" in argv else None
    for t in (t_game_only_exit_skips_owed_judge_and_named_rows, t_unfixed_problem_still_refuses,
              t_offline_row_without_named_item_still_refuses, t_not_game_only_move_unchanged,
              t_owed_judge_from_other_cause_still_refuses, t_evaluate_gives_bars_only_when_game_only_passes):
        if only is not None and t.__name__ not in only:
            continue
        print("== %s" % t.__name__)
        try:
            t()
        except Exception as e:      # noqa: BLE001
            check(False, "%s raised %s: %s" % (t.__name__, type(e).__name__, e))
    shutil.rmtree(TMP, ignore_errors=True)
    if FAILS:
        print("FAILED %d: %s" % (len(FAILS), "; ".join(FAILS[:8])))
        return 1
    print("PASS selftest_maturation_game_only_exit")
    return 0


if __name__ == "__main__":
    sys.exit(main())
