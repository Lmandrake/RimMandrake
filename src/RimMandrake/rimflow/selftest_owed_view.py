#!/usr/bin/env python3
"""selftest_owed_view.py - the owed view's block of waits that name the Conductor (owed.named_waits, owed.view).

Item RIMMANDRAKE_SHOW_CONDUCTOR_THE_WAITS_THAT_NAME_IT_TWENTY_TWO_UNSEEN; page
design/specs/2026-11-24-owed-view-named-waits/boundary.md (each t_ function is one promise of it, by name). Offline: plain
objects, no ledger. Seen red on the base (no named_waits).
"""
import os
import sys
from types import SimpleNamespace as NS

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
sys.dont_write_bytecode = True
from rimflow import owed as O  # noqa: E402

NOW = O.model.iso_epoch("2026-11-24T08:00:00Z")


def item(iid, **kw):
    d = dict(id=iid, title="title of " + iid, owner=O.model.canonical("BENCH"), open=True, kind="task", caused_by=None,
             blocked=False, blocked_reason=None, wait_until="2026-11-30T08:00:00Z",
             wait_reason="the Conductor reads the page and decides", state="doing", created_at="2026-11-20T08:00:00Z")
    d.update(kw)
    return NS(**d)


def world(*items):
    return NS(items={i.id: i for i in items})


def ids(*items):
    return [i.id for i in O.named_waits(world(*items), "BENCH", NOW)]


def t_a_wait_that_names_the_conductor_is_in_the_view():
    a, b = item("A_LATER"), item("B_SOONER", wait_until="2026-11-25T08:00:00Z")
    assert ids(a, b) == ["B_SOONER", "A_LATER"], "the soonest date first"
    out = O.view(world(a, b), "BENCH", NOW, show_all=True)
    assert out[0].startswith("OWED 0") and out[0].endswith("2 waits name you"), out[0]
    k = next(n for n, x in enumerate(out) if x.startswith("YOURS BY A WAIT (2)"))
    assert "B_SOONER" in out[k + 1] and "the Conductor reads the page" in out[k + 1] and "2026-11-25" in out[k + 1]


def t_only_an_open_wait_of_this_seat_that_names_the_conductor():
    assert ids(item("NO_NAME", wait_reason="the 7-day reading ends")) == []
    assert ids(item("CLOSED", open=False)) == []
    assert ids(item("OTHER_SEAT", owner="OWNER")) == []
    assert ids(item("OWED", kind="owed")) == [], "an owed item is in the view already"
    assert ids(item("STANDING", kind="standing")) == [], "a standing notice asks nothing"
    assert ids(item("NO_WAIT", wait_until=None)) == []
    assert ids(item("NO_REASON", wait_reason=None)) == []


def t_a_passed_date_is_said():
    p = item("PASSED", wait_until="2026-11-21T08:00:00Z")
    assert ids(p) == ["PASSED"]
    assert "PASSED 2026-11-21" in "\n".join(x for x in O.view(world(p), "BENCH", NOW, show_all=True) if "title of" in x)


def t_the_first_line_says_the_count_even_when_the_lines_are_cut():
    many = [item("OWED_%03d" % n, kind="owed", wait_until=None, wait_reason=None) for n in range(60)]
    out = O.view(world(*(many + [item("W_ONE")])), "BENCH", NOW)
    assert len(out) <= O.MAX_LINES and out[0].endswith("1 wait names you") and "--all" in out[-1], (len(out), out[0])
    assert O.banner(world(item("X", wait_until=None)), "BENCH", NOW) == "OWED 0 (actionable 0, waiting 0)"


def main():
    failed = 0
    for t in (t_a_wait_that_names_the_conductor_is_in_the_view, t_only_an_open_wait_of_this_seat_that_names_the_conductor,
              t_a_passed_date_is_said, t_the_first_line_says_the_count_even_when_the_lines_are_cut):
        try:
            t()
            print("PASS", t.__name__)
        except Exception as e:  # noqa: BLE001
            failed += 1
            print("FAIL", t.__name__, "%s: %s" % (type(e).__name__, str(e)[:300]))
    print("selftest_owed_view: %s" % ("PASS" if not failed else "FAIL (%d)" % failed))
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
