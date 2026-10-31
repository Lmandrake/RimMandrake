#!/usr/bin/env python3
"""selftest_arena_trial.py — arena_trial.py: the trial's explicit task list (ARENA_TRIAL_TASKS_FIX_DEFAULT_ALL_FROZEN).

Pure checks on select()/read_list() with synthetic banks, plus a shape check of the committed default
trial_tasks.json (N distinct ids, all three eras, oldest first). The size is a parameter (T.DEFAULT_N, `build --n`);
no check here hard-wires it (ARENA_TRIAL_SCHEDULE_FIX_STOPS_SHORT). No git, no frozen bank needed.
"""
from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import arena_analysis as AA  # noqa: E402
import arena_trial as T  # noqa: E402

FAILS = []


def check(name, ok, detail=""):
    print("%s  %s%s" % ("PASS" if ok else "FAIL", name, "" if ok else "  -- %s" % (detail,)))
    if not ok:
        FAILS.append(name)


def bank(n=241, cs_every=6):
    """n tasks, chrono = i (oldest first), every cs_every-th one C#."""
    return {"B%03d" % i: {"kind": "csharp" if i % cs_every == 0 else ("python-util", "tooling")[i % 2], "chrono": i}
            for i in range(n)}


def t_select():
    b = bank()
    N = T.DEFAULT_N
    ids = T.select(b)
    eras, _ = AA.era_map(b)
    check("default: exactly DEFAULT_N (%d) ids, distinct" % N, len(ids) == N and len(set(ids)) == N, len(ids))
    check("default is NOT every frozen task", len(ids) < len(b), len(ids))
    span = sorted({eras[t] for t in ids})
    check("the list spans all three eras of the bank", span == [0, 1, 2], span)
    per = [sum(1 for t in ids if eras[t] == e) for e in range(3)]
    even = [N // 3 + (1 if e >= 3 - N % 3 else 0) for e in range(3)]
    check("eras split evenly, remainder to the newest %s" % (even,), per == even, per)
    check("oldest first (chrono ascending)", [b[t]["chrono"] for t in ids] == sorted(b[t]["chrono"] for t in ids))
    cs = sum(1 for t in ids if b[t]["kind"] == "csharp")
    share = sum(1 for s in b.values() if s["kind"] == "csharp") / len(b)
    check("C# in proportion by default (bank share %.2f -> %d of %d)" % (share, cs, N), abs(cs - N * share) <= 3, cs)
    no = T.select(b, csharp=False)
    check("--no-csharp: no C# task, still N over three eras", len(no) == N and not any(
        b[t]["kind"] == "csharp" for t in no), len(no))
    check("deterministic", T.select(b) == ids)
    for bad in (0, -1, str(N), True, 1.5):
        try:
            T.select(b, bad)
            check("n=%r refused" % (bad,), False)
        except T.TrialError:
            check("n=%r refused (not a positive int)" % (bad,), True)
    # FORCED (ARENA_TRIAL_SCHEDULE_FIX_STOPS_SHORT): the size is a parameter, not a cap. The old MAX_N refused these.
    for big in (N + 1, 2 * N + 7):
        try:
            got = T.select(b, big)
            per = [sum(1 for t in got if eras[t] == e) for e in range(3)]
            check("n=%d (above the default) accepted: %d distinct ids over three eras, oldest first" % (big, big),
                  len(set(got)) == big == len(got) and all(per) and got == sorted(got, key=lambda t: b[t]["chrono"]),
                  (len(got), per))
        except T.TrialError as e:
            check("n=%d (above the default) accepted" % big, False, e)
    check("n=len(bank) -> every task", T.select(b, len(b)) == sorted(b))
    check("module default is a named parameter, not a cap", not hasattr(T, "MAX_N") and isinstance(T.DEFAULT_N, int))
    small = bank(20)
    check("a bank smaller than n -> every task, still oldest first", T.select(small) == sorted(small))
    try:
        T.select({"A": {"kind": "x", "chrono": 1}, "B": {"kind": "x"}})
        check("a bank task with no chronology key refuses", False)
    except T.TrialError:
        check("a bank task with no chronology key refuses", True)


def t_read_list():
    with tempfile.TemporaryDirectory() as d:
        p = Path(d, "l")
        for body, want in (('{"schema": "%s", "tasks": ["A", "B"]}' % T.SCHEMA, ["A", "B"]), ('["A", "B"]', ["A", "B"]),
                           ("A\n\nB\n", ["A", "B"])):
            p.write_text(body)
            check("read_list accepts %r" % body[:14], T.read_list(p) == want)
        for body in ('{"schema": "other", "tasks": ["A"]}', '["A", "A"]', "A\nA\n", "[1, 2]", '{"tasks": "A"}'):
            p.write_text(body)
            try:
                T.read_list(p)
                check("read_list refuses %r" % body, False)
            except ValueError:
                check("read_list refuses %r" % body, True)


def t_default_file():
    ids = T.read_list(T.DEFAULT_PATH)
    doc = json.loads(T.DEFAULT_PATH.read_text(encoding="utf-8"))
    check("committed default trial_tasks.json: n distinct ids, n as recorded", 0 < len(ids) == doc.get("n"), len(ids))
    check("committed default spans three eras", len(doc.get("eras_in_trial", [])) == 3 and all(
        doc["eras_in_trial"]), doc.get("eras_in_trial"))
    check("committed default: C# included (owner: C# tasks stay in the pool), sibling order checked",
          doc.get("csharp") is True and doc.get("kinds", {}).get("csharp", 0) > 0 and "check_rounds" in doc.get("order", ""),
          (doc.get("csharp"), doc.get("kinds")))
    check("analysis CLI default is this file", AA.TRIAL_DEFAULT == T.DEFAULT_PATH)


def t_exclude():
    """Pool exclusions, reader drops/unscores and one-per-bundled-commit (ARENA_POOL_FIX_BUNDLED_WRONG_REASON)."""
    b = bank(60)
    fixes = {t: "f%03d" % (int(t[1:]) // 3) for t in b}          # every 3 consecutive tasks share one commit
    el, why = T.exclude(b, {}, fixes)
    check("one per bundled commit: 60 tasks in 20 commits -> 20 eligible", len(el) == 20, len(el))
    check("the eligible sibling is the first by id", all(int(t[1:]) % 3 == 0 for t in el), sorted(el)[:4])
    check("every left-out sibling names its eligible one", all("sibling" in why[t] for t in b if t not in el))
    el2, why2 = T.exclude(b, {"B000": "dropped"}, fixes)
    check("a dropped sibling hands the slot to the next", "B001" in el2 and "B000" not in el2 and why2["B000"] == "dropped")
    check("--allow-bundled keeps every sibling", len(T.exclude(b, {}, fixes, bundled=True)[0]) == 60)
    check("a task with no fix sha is its own group", len(T.exclude(b, {}, {"B000": "x", "B001": "x"})[0]) == 59)
    ids = T.select(T.exclude(bank(241), {}, {t: "f%03d" % (int(t[1:]) // 2) for t in bank(241)})[0], 30)
    fx = {t: int(t[1:]) // 2 for t in ids}
    check("select over the deduped bank: N kept, no two of one commit", len(ids) == 30 and len(set(fx.values())) == 30)

    saved = (T.AA.load_tasks, T.AA.chrono_keys, T.hidden_fix_shas, T.A.load_pool_exclusions, T._source_items,
             T.reader_exclusions_path)
    with tempfile.TemporaryDirectory() as d:
        try:
            bb = bank(90)
            T.AA.load_tasks = lambda p=None: {t: dict(v) for t, v in bb.items()}
            T.AA.chrono_keys = lambda tasks, repo=None: {}
            T.hidden_fix_shas = lambda p=None: {t: "f%03d" % (int(t[1:]) // 2) for t in bb}
            T.A.load_pool_exclusions = lambda path=None: {"ITEM_B004": "provisional Clean"}
            T._source_items = lambda p=None: {t: "ITEM_" + t for t in bb}
            T.reader_exclusions_path = lambda p=None: Path(d, "absent.json")
            doc = T.build(n=20, check=False)
            check("build: pool exclusion by source item leaves the task out",
                  "B004" not in doc["tasks"] and "pool exclusion" in doc["left_out"]["B004"], doc["left_out"].get("B004"))
            check("build: one per bundled commit by default", doc["one_per_bundled_commit"] and
                  len({int(t[1:]) // 2 for t in doc["tasks"]}) == len(doc["tasks"]) == 20)
            check("build: absent default reader file -> reader null (not applied)", doc["reader"] is None)
            rx = Path(d, "rx.json")
            rx.write_text(json.dumps({"schema": T.READER_SCHEMA, "drop": {"B010": "no scored check left"},
                                      "unscore": {"B012": ["src/x/selftest_y.py"]}}))
            doc = T.build(n=20, check=False, reader=rx)
            check("build: reader DROP leaves the task out", "B010" not in doc["tasks"] and "reader pass" in doc["left_out"]["B010"])
            check("build: reader UNSCORE leaves the task out by default (judge cannot unscore yet)",
                  "B012" not in doc["tasks"] and "unscored" in doc["left_out"]["B012"])
            check("build: B011 (sibling of dropped B010) takes the slot", "B011" not in doc["left_out"], doc["left_out"].get("B011"))
            doc2 = T.build(n=20, check=False, reader=rx, allow_unscored=True)
            check("build: --allow-unscored keeps an unscored task eligible", "B012" not in doc2["left_out"])
            check("build: N stays a parameter after exclusions", len(T.build(n=33, check=False, reader=rx)["tasks"]) == 33)
            T.reader_exclusions_path = lambda p=None: rx
            check("build: the default reader path is applied when present", T.build(n=20, check=False)["reader"]["drop"] == 1)
            try:
                T.build(n=20, check=False, reader=Path(d, "missing.json"))
                check("build: an explicit missing reader file refuses", False)
            except T.TrialError:
                check("build: an explicit missing reader file refuses", True)
            Path(d, "bad.json").write_text('{"schema": "other"}')
            try:
                T.build(n=20, check=False, reader=Path(d, "bad.json"))
                check("build: a malformed reader file refuses", False)
            except T.TrialError:
                check("build: a malformed reader file refuses", True)
            check("build: --no-reader ignores it", T.build(n=20, check=False, reader=rx, use_reader=False)["reader"] is None)
        finally:
            (T.AA.load_tasks, T.AA.chrono_keys, T.hidden_fix_shas, T.A.load_pool_exclusions, T._source_items,
             T.reader_exclusions_path) = saved


def t_pool_exclusions_file():
    ex = T.A.load_pool_exclusions()
    want = {"CARBON_PRESS_FIX_NO_WORKGIVER_RUNS_BILLS", "COLD_INSPECT_FIX_PARTIAL_SAYS_ALL_HELD",
            "MISSION_FIXTURE_FIX_RESEARCH_WINDOW_BLINDS", "ROAST_STICK_FIX_DISABLED_COOK_STAT_ERRORS"}
    check("committed pool_exclusions.json names the four provisional Clean items", want <= set(ex), sorted(ex))
    with tempfile.TemporaryDirectory() as d:
        for body in ('{"schema": "x", "exclude": []}', '{"schema": "%s", "exclude": [{"item": "A"}]}' % T.A.POOL_EXCLUSIONS_SCHEMA,
                     '{"schema": "%s", "exclude": [{"item": "A", "reason": "r"}, {"item": "A", "reason": "r"}]}'
                     % T.A.POOL_EXCLUSIONS_SCHEMA):
            Path(d, "e.json").write_text(body)
            try:
                T.A.load_pool_exclusions(Path(d, "e.json"))
                check("malformed exclusion file refused: %s" % body[:40], False)
            except T.A.ArenaError:
                check("malformed exclusion file refused: %s" % body[:40], True)
        check("absent exclusion file -> {}", T.A.load_pool_exclusions(Path(d, "none.json")) == {})


def main():
    for t in (t_select, t_read_list, t_default_file, t_exclude, t_pool_exclusions_file):
        t()
    print("\n%d failure(s)%s" % (len(FAILS), (": " + ", ".join(FAILS)) if FAILS else ""))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
