#!/usr/bin/env python3
"""selftest_designer_done_memo.py — designer_stage.done_items folds the ledger once per ledger state.

A Designer launch builds its packet twice in one Dispatcher beat (decide's preview, execute's commit) and each packet
called done_items twice: four whole-ledger replays, ~1.7 s each, inside the 20 s beat
(RIMMANDRAKE_FIT_DISPATCH_TICK_IN_ITS_BEAT, 2026-11-16: an observe step cut at 14 s on a DesignerCodex preview).
  memo      a second call on the same ledger files (path, size, mtime) replays nothing
  change    a ledger file that grew is replayed again
  copy      the caller gets its own dict: mutating it does not change the next answer
  unread    an unreadable ledger answers None and is not remembered
Nothing outside a temp dir is touched (model's readers are stubbed).
"""
import os
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import designer_stage as DS  # noqa: E402
import model  # noqa: E402

FAILS = []


def check(ok, msg):
    print(("ok    " if ok else "FAIL  ") + msg)
    if not ok:
        FAILS.append(msg)


class Item:
    def __init__(self, title, state):
        self.title, self.state = title, state


class World:
    def __init__(self, items):
        self.items = items


def main():
    tmp = tempfile.mkdtemp(prefix="selftest_designer_done_memo_")
    f = os.path.join(tmp, "BENCH.jsonl")
    with open(f, "w") as fh:
        fh.write("{}\n")
    calls = {"replay": 0, "fail": False}

    def replay(evs):
        calls["replay"] += 1
        if calls["fail"]:
            raise ValueError("torn line")
        return World({"A_DONE": Item("a", "done"), "B_OPEN": Item("b", "doing")})
    saved = model.ledger_files, model.read, model.replay
    model.ledger_files, model.read, model.replay = (lambda path=None: [f]), (lambda path=None: []), replay
    try:
        DS.__dict__.get("_DONE_MEMO", {}).clear()
        a = DS.done_items(DS.REPO)
        b = DS.done_items(DS.REPO)
        check(a == {"A_DONE": "a"} and b == a, "done items are the done ones: %s" % a)
        check(calls["replay"] == 1, "memo: the second call on the same ledger replays nothing (replays %d)" % calls["replay"])
        b["X"] = "mutated"
        check("X" not in DS.done_items(DS.REPO), "copy: a caller's edit does not reach the next answer")
        with open(f, "a") as fh:
            fh.write("{\"more\": 1}\n")
        DS.done_items(DS.REPO)
        check(calls["replay"] == 2, "change: a grown ledger file is replayed again (replays %d)" % calls["replay"])
        with open(f, "a") as fh:
            fh.write("{\"more\": 2}\n")
        calls["fail"] = True
        check(DS.done_items(DS.REPO) is None, "unread: an unreadable ledger answers None")
        calls["fail"] = False
        n = calls["replay"]
        check(DS.done_items(DS.REPO) == {"A_DONE": "a"} and calls["replay"] == n + 1,
              "unread: the None was not remembered; the next call replays")
        check(DS.done_items(tmp) is None, "a repo that is not the real one still answers None (a test repo patches it)")
    finally:
        model.ledger_files, model.read, model.replay = saved
    for msg in FAILS:
        print("FAILED: " + msg)
    print("%d failure(s)" % len(FAILS))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
