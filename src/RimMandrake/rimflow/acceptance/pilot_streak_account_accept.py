#!/usr/bin/env python3
"""Acceptance for RIMMANDRAKE_TYPE_PILOT_STREAK_AS_ITEM_ACCOUNT_ALREADY_ORDERED.

The Test Pilot streak (testpilot_route.judge: STREAK non-pass runs in a row, voided runs taken out) is derived from the
item's ordered runs today, but no `pipe` line moves it. When this passes, the streak is an item account in the control
store: `pipe limit <ITEM> pilot_streak N` and `pipe add <ITEM> pilot_streak -N` change judge()'s verdict, with an undo.
On a temp control store only (RM_UNDER_SELFTEST), never the live one.

  exit 0  PASS (every check)      exit 1  FAIL (each named)
"""
import contextlib
import io
import os
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
RIMFLOW = os.path.dirname(HERE)
sys.path.insert(0, RIMFLOW)
os.environ["RM_UNDER_SELFTEST"] = "1"
os.environ.pop("RM_CONTROL_DB", None)
os.environ.setdefault("RM_PIPE_CONTROL_DIR", tempfile.mkdtemp(prefix="pilot_streak_ctl_"))
import model  # noqa: E402
import testpilot_route as TP  # noqa: E402
import pipeline_control as PC  # noqa: E402

FAILS = []


def check(ok, msg, got=None):
    print("%s %s%s" % ("ok  " if ok else "FAIL", msg, "" if ok or got is None else "  (got %r)" % (got,)))
    if not ok:
        FAILS.append(msg)


class It(object):
    id, state, blocked, needs, history = "FAKE_STREAK_ITEM", "ready", False, "bridge", []
    runs = [model.Run("FAKE_STREAK_ITEM", n, "full-578", "fail", None, "abc", "2026-11-18T0%d:00:00Z" % n, n)
            for n in (1, 2, 3)]


def pipe(*argv):
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        try:
            rc = PC.main(list(argv) + ["--why", "acceptance"])
        except SystemExit as e:
            rc = e.code
    return rc, buf.getvalue().strip().splitlines()


def streak():
    v = TP.judge(It, [], void={})
    return bool(v) and v.get("kind") == "streak"


def main():
    check(streak(), "base: three fails in a row route the item")
    mid = "FAKE_STREAK_ITEM/run-2@full-578"
    check(TP.judge(It, [], void={mid: {"id": "v", "why": "harness"}}) is None,
          "a voided middle run breaks the streak (derived from ordered valid runs)")
    rc, out = pipe("limit", "FAKE_STREAK_ITEM", "pilot_streak", "4")
    check(rc == 0 and len(out) <= 3 and any("undo" in l for l in out), "pipe limit <ITEM> pilot_streak 4: one line, "
          "its undo", out)
    check(not streak(), "judge() honours the raised limit: three fails no longer route the item")
    pipe("limit", "FAKE_STREAK_ITEM", "pilot_streak", "default")
    check(streak(), "limit default routes it again")
    rc, out = pipe("add", "FAKE_STREAK_ITEM", "pilot_streak", "-1")
    check(rc == 0 and not streak(), "pipe add <ITEM> pilot_streak -1: one fail forgiven, no streak", out)
    print("%s: %d failure(s)" % ("FAIL" if FAILS else "PASS", len(FAILS)))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
