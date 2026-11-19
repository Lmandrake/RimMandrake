#!/usr/bin/env python3
"""Offline selftest of card_capture.py's reads: one test per promise on
design/specs/2026-11-19-card-capture-reads/boundary.md, each named after it (boundary_check.py reads that).

    python3 src/RimMandrake/rimflow/selftest_card_capture_reads.py                 every test; exit 0 PASS, 1 FAILED
    python3 src/RimMandrake/rimflow/selftest_card_capture_reads.py --only t_x ...  those alone
"""
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import card_capture as C  # noqa: E402

FAILS = []


def check(ok, what, got=None):
    print("%s %s%s" % ("ok  " if ok else "FAIL", what, "" if ok or got is None else "  got: %r" % (got,)))
    if not ok:
        FAILS.append(what)


def t_answer_time_parses_or_is_none():
    """_epoch: the epoch second for an ISO time, None for one that does not parse; never 0."""
    check(C._epoch("2026-11-19T10:00:00Z") == 1795082400, "an ISO time is its epoch", C._epoch("2026-11-19T10:00:00Z"))
    for bad in ("UNMEASURED", "", None):
        check(C._epoch(bad) is None, "%r is no time" % (bad,), C._epoch(bad))


def t_a_card_without_a_readable_time_is_never_matched():
    """match("", [card]): a card answered a minute ago is taken; the same card with an unparseable time is not."""
    now = time.time()
    card = {"answered": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(now - 60)), "session": "s", "key": "k",
            "questions": []}
    check(C.match("", [card], now=now) is not None, "a card answered a minute ago is matched")
    got = C.match("", [dict(card, answered="UNMEASURED")], now=now)
    check(got is None, "a card whose time does not parse is not matched", got)


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    only = set(argv[argv.index("--only") + 1:]) if "--only" in argv else None
    for t in (t_answer_time_parses_or_is_none, t_a_card_without_a_readable_time_is_never_matched):
        if only is not None and t.__name__ not in only:
            continue
        print("== %s" % t.__name__)
        try:
            t()
        except Exception as e:      # noqa: BLE001
            check(False, "%s raised %s: %s" % (t.__name__, type(e).__name__, e))
    if FAILS:
        print("FAILED %d: %s" % (len(FAILS), "; ".join(FAILS[:8])))
        return 1
    print("PASS selftest_card_capture_reads")
    return 0


if __name__ == "__main__":
    sys.exit(main())
