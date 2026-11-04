#!/usr/bin/env python3
"""Selftest: one shared fault is one record across Relentless's two incident stores
(INCIDENT_STORES_UNIFY_TWO_BOOKS_ONE_FAULT).

    python3 src/RimMandrake/rimflow/selftest_relentless_incident_book.py

relentless_breakers keeps capability incidents (incidents.json: one signature on three items, undiagnosed);
relentless_incident keeps instrument incidents (instrument_incidents.json: a diagnosed fault keyed by its repair item).
Pins:
  * whichever opens second links both ways (the capability names its repair, the instrument lists the signature);
  * `book()` shows a linked pair, or an unlinked pair sharing an item (records from before the link), as ONE row;
    disjoint faults stay two rows;
  * the repair's release after fixtures that RAN and held releases the linked capability incident; a release on the
    close alone (a worker snag, no fixtures) does not;
  * the Conductor's capability alarm names the repair item and the one book;
  * a shared item joining an open capability incident later still links it; a signature released and reopened for
    other items is not freed by the old repair (GPT review 2026-11-04, P2 and P1).
"""
import os
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import relentless as R                       # noqa: E402
import relentless_breakers as B              # noqa: E402
import relentless_incident as RI             # noqa: E402

FAILS = []
WHY = "bridge refused: connection reset by peer after 30 s"
KLASS = "bridge_unreachable"
GOOD, BAD = "python3 fixture_good.py", "python3 fixture_bad.py"


def ok(cond, what):
    print(("ok   " if cond else "FAIL ") + what)
    if not cond:
        FAILS.append(what)


def store():
    return R.Store(tempfile.mkdtemp(prefix="incbook_"))


def three(s, items=("I0", "I1", "I2"), now=1000.0):
    for n, i in enumerate(items):
        s.save({"item": i, "status": "queued"})     # in line: tell() hands the probe on only past a gone item
        with s.lock():
            B.note(s, i, KLASS, WHY, {}, now + n)
    return [k for k, v in B.load(s).items() if v.get("open")]


def run_ok(cmd):
    return (0, "FIXTURE_VERDICT: PASS") if cmd == GOOD else (1, "FIXTURE_VERDICT: FAIL")


def t_instrument_then_capability():
    s = store()
    with s.lock():
        RI.link(s, "REP_A", "I0", "a" * 40, 900.0, "the bridge", "reset by peer", {"good": GOOD, "bad": BAD}, ["HARNESS"])
    opened = three(s)
    ok(len(opened) == 1, "three items on one signature open one capability incident")
    cap = B.load(s)[opened[0]]
    ok(cap.get("repair") == "REP_A", "the capability incident names the repair that explains it: %s" % cap.get("repair"))
    ok(RI.get(s, "REP_A").get("capability") == opened, "the instrument incident lists the signature")
    rows = RI.book(s)
    ok(len(rows) == 1 and rows[0]["book"] == "instrument+capability", "one fault, ONE row: %s" % [r["book"] for r in rows])
    ok(rows and rows[0]["items"] == ["I0", "I1", "I2"], "the row carries every affected item from both books")
    # the repair closes, its fixtures hold, the last parent leaves: the capability incident goes with it
    okk, why = RI.check(s, "REP_A", run_ok, 2000.0, "REP_A:done:abc:1", need_fixtures=True)
    ok(okk, "fixtures hold: %s" % why)
    with s.lock():
        RI.released(s, "REP_A", "I0", 2001.0)
    ok(opened[0] not in B.load(s), "the repair's release with held fixtures releases the linked capability incident")
    ok(B.waits(s, "I1") is None, "and its waiting items are back in line")
    ok(RI.book(s) == [], "the book is empty: nothing left open in either store")


def t_capability_then_instrument():
    s = store()
    opened = three(s)
    with s.lock():
        RI.link(s, "REP_B", "I1", None, 1500.0, None, "worker snag", None, ["worker_snag"])
    ok(B.load(s)[opened[0]].get("repair") == "REP_B", "a later diagnosis links onto the open capability incident")
    ok(RI.get(s, "REP_B").get("capability") == opened, "and the instrument incident lists it")
    tell = []
    fx = type("Fx", (), {"conductor_alarm": lambda self, t: tell.append(t)})()
    acts = []
    B.tell(s, fx, 1600.0, acts)
    ok(len(tell) == 1 and "REP_B" in tell[0] and "relentless.py incidents" in tell[0],
       "the Conductor's alarm names the repair and the one book")
    # a worker snag releases on the repair's close alone (no fixtures): that proves nothing about the instrument
    okk, _ = RI.check(s, "REP_B", run_ok, 2000.0, "REP_B:done:abc:1", need_fixtures=False)
    with s.lock():
        RI.released(s, "REP_B", "I1", 2001.0)
    ok(okk and RI.get(s, "REP_B")["status"] == RI.RELEASED, "the snag's parent is released on the close")
    ok((B.load(s).get(opened[0]) or {}).get("open"), "no fixtures ran: the capability incident stays for its probe")
    rows = RI.book(s)
    ok(len(rows) == 1 and rows[0]["book"] == "capability" and rows[0]["repair"] == "REP_B",
       "what is left is one capability row that still names its repair: %s" % rows)


def t_unlinked_overlap_and_disjoint():
    s = store()
    opened = three(s)
    # an instrument record written before the link existed: shares I2, links to nothing
    RI.save(s, {"REP_OLD": {"repair": "REP_OLD", "component": "site", "repro": [], "fixtures": {}, "checks": [],
                            "targets": ["SITE"], "status": RI.OPEN, "opened_at": 10.0, "released_at": None,
                            "items": {"I2": {"sha": None, "since": 10.0, "released_at": None, "waits": True}}}})
    rows = RI.book(s)
    ok(len(rows) == 1 and rows[0]["book"] == "instrument+capability" and rows[0]["capability"] == opened,
       "an unlinked pair sharing an item still reads as one row")
    # a disjoint fault is its own row
    with s.lock():
        RI.link(s, "REP_X", "J9", "b" * 40, 50.0, "the checker box", "ssh refused", None, ["CHECKER"])
    rows = RI.book(s)
    ok(sorted(r["repair"] for r in rows) == ["REP_OLD", "REP_X"], "a disjoint fault is a second row: %s" % rows)
    ok("one row per fault" in RI.book_text(rows) and "REP_X" in RI.book_text(rows), "the text view lists both")


def t_late_join_links():
    """GPT review P2: the shared item reports the signature AFTER the capability incident opened on other items."""
    s = store()
    with s.lock():
        RI.link(s, "REP_D", "X", "c" * 40, 900.0, "the bridge", "reset", {"good": GOOD, "bad": BAD}, ["HARNESS"])
    opened = three(s)
    ok(not B.load(s)[opened[0]].get("repair"), "no shared item yet: no link")
    three(s, items=("X",), now=1100.0)
    ok(B.load(s)[opened[0]].get("repair") == "REP_D", "the shared item joining later makes the link")
    RI.check(s, "REP_D", run_ok, 2000.0, "REP_D:done:abc:1", need_fixtures=True)
    with s.lock():
        RI.released(s, "REP_D", "X", 2001.0)
    ok(opened[0] not in B.load(s), "and the repair's release releases it")


def t_stale_link_reopened_signature():
    """GPT review P1: a signature released and reopened for unrelated items is a new incident the old repair never
    explained; the old repair's release must not free it."""
    s = store()
    with s.lock():
        RI.link(s, "REP_C", "I0", "d" * 40, 900.0, "the bridge", "reset", {"good": GOOD, "bad": BAD}, ["HARNESS"])
    opened = three(s)
    with s.lock():
        B.probe_passed(s, B.load(s)[opened[0]]["probe"], 1200.0)
    ok(opened[0] not in B.load(s), "the probe's candidate released the first capability incident")
    again = three(s, items=("K0", "K1", "K2"), now=1300.0)
    ok(again == opened and not B.load(s)[again[0]].get("repair"), "the same signature reopens for other items, unlinked")
    RI.check(s, "REP_C", run_ok, 2000.0, "REP_C:done:abc:1", need_fixtures=True)
    with s.lock():
        RI.released(s, "REP_C", "I0", 2001.0)
    ok((B.load(s).get(again[0]) or {}).get("open"), "the old repair's release leaves the new incident open")
    rows = RI.book(s)
    ok(len(rows) == 1 and rows[0]["book"] == "capability" and rows[0]["items"] == ["K0", "K1", "K2"],
       "and the book shows it alone: %s" % rows)


def t_two_repairs_one_capability():
    """GPT review 2 P3: two instrument incidents sharing one capability incident: it sits in ONE row."""
    s = store()
    with s.lock():
        RI.link(s, "REP_E", "I0", "e" * 40, 900.0, "bridge", "reset", None, ["HARNESS"])
        RI.link(s, "REP_F", "I2", "f" * 40, 950.0, "bridge", "reset", None, ["HARNESS"])
    opened = three(s)
    rows = RI.book(s)
    holding = [r["repair"] for r in rows if opened[0] in r["capability"]]
    ok(holding == ["REP_E"], "the capability incident is in one row, its repair's: %s" % holding)
    other = [r for r in rows if r["repair"] == "REP_F"]
    ok(other and other[0]["shares"] == opened and other[0]["items"] == ["I2"], "the other repair lists it as shared")


def main():
    for t in (t_instrument_then_capability, t_capability_then_instrument, t_unlinked_overlap_and_disjoint,
              t_late_join_links, t_stale_link_reopened_signature, t_two_repairs_one_capability):
        t()
    print("%s %s: %d failure(s)" % ("FAIL" if FAILS else "PASS", os.path.basename(__file__), len(FAILS)))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
