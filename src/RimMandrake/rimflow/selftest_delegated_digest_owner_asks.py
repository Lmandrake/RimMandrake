#!/usr/bin/env python3
"""selftest_delegated_digest_owner_asks.py — the digest's open OWNER asks (OWNER_ASKS_MEASURE_AGE_IN_DIGEST, D4(a)).

A fixture ledger (one jsonl file, model.read(path)) is run through the REAL path: delegated_digest.main --dry-run
--ledger <fixture> --cut <fixed>, which reads it, replays it, computes owner_asks, projects it through
contracts.blind and renders the page. Asserted on the written page:

  listed     every open item on the OWNER seat, and nothing else (a dropped OWNER item, a BENCH item: absent)
  age        whole hours and days from the `file` event to the cut; oldest first
  waiting    direct = open items whose live block names it (--on or --also-on); chain = every open item whose chain of
             live blocks reaches it, a wait cycle counted once; a closed waiter, and a block released at read time (its
             --on reached its --until level), wait on nothing
  withheld   an OWNER ask about accounts is counted, never named
  default    the page says no default is applied or recommended, and carries no other default word
  unmeasured an unreadable ledger reads the section UNMEASURED, never "0 asks"
  edge       an id whose end and the next word on its line spell an account (a planted fixture key) is withheld and
             counted; before the fix the per-line gate refused the WHOLE digest (2026-11-04, the real ledger)
  planted    the assertions are shown to SEE a fault: with priority.block_holds broken (every block released) the
             waiting counts check fails, and with the OWNER filter broken the listed check fails
Writes only under a temp dir.
"""
import datetime as dt
import json
import os
import re
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.dirname(HERE))
import delegated_digest as D  # noqa: E402

FAILS = []
CUT = dt.datetime(2026, 11, 4, 12, 0, 0, tzinfo=dt.timezone.utc)
DATE = "2026-11-04"


def check(ok, msg):
    print(("PASS " if ok else "FAIL ") + msg)
    if not ok:
        FAILS.append(msg)


def ts(hours_before_cut):
    return (CUT - dt.timedelta(hours=hours_before_cut)).strftime("%Y-%m-%dT%H:%M:%SZ")


def fixture():
    ev = []

    def file(iid, seat, h, kind="task"):
        ev.append({"ts": ts(h), "seat": seat, "event": "file", "id": iid, "for": seat, "title": "t", "kind": kind})

    def block(iid, h, on, also=None, until=None):
        e = {"ts": ts(h), "seat": "BENCH", "event": "block", "id": iid, "reason": "r", "on": on}
        if also:
            e["also_on"] = also
        if until:
            e["until"] = until
        ev.append(e)

    file("ASK_OLD_ONE", "OWNER", 245)            # 10 days 5 hours
    file("ASK_NEW_TWO", "OWNER", 5)
    file("ASK_MID_THREE", "OWNER", 50)           # 2 days 2 hours; waited on only by a released block
    file("ASK_DROPPED_FOUR", "OWNER", 300)
    ev.append({"ts": ts(299), "seat": "OWNER", "event": "drop", "id": "ASK_DROPPED_FOUR", "reason": "r"})
    file("OPS_ACCOUNT_DRAIN_ASK", "OWNER", 100)  # about accounts: withheld, counted
    file("BENCH_NOT_AN_ASK", "BENCH", 400)
    for w in ("W_ONE", "W_TWO", "W_THREE", "W_FOUR", "W_FIVE", "W_CLOSED", "W_LIFTED", "W_SIDE"):
        file(w, "BENCH", 40)
    block("W_ONE", 30, "ASK_OLD_ONE")                          # direct
    block("W_TWO", 30, "W_ONE")                                # chain through W_ONE
    block("W_THREE", 30, "W_SIDE", also=["ASK_OLD_ONE"])       # direct through also_on
    block("W_FIVE", 30, "W_FOUR", also=["ASK_OLD_ONE"])        # direct, and a cycle with W_FOUR
    block("W_FOUR", 29, "W_FIVE")                              # chain through W_FIVE (cycle: counted once)
    block("W_CLOSED", 30, "ASK_NEW_TWO")
    ev.append({"ts": ts(20), "seat": "BENCH", "event": "drop", "id": "W_CLOSED", "reason": "r"})   # waits on nothing
    block("W_LIFTED", 30, "ASK_MID_THREE", until="built")       # released at read time once ASK_MID_THREE is built
    ev.append({"ts": ts(10), "seat": "OWNER", "event": "implemented", "id": "ASK_MID_THREE", "sha": "a" * 40})
    return ev


EXPECT = {   # id: (age days, age hours, waiting direct, waiting chain)
    "ASK_OLD_ONE": (10, 245, 3, 5),
    "ASK_MID_THREE": (2, 50, 0, 0),   # built: still open, still an ask
    "ASK_NEW_TWO": (0, 5, 0, 0),
}
ORDER = ["ASK_OLD_ONE", "ASK_MID_THREE", "ASK_NEW_TWO"]


def write_ledger(tmp, events):
    p = os.path.join(tmp, "fixture.jsonl")
    with open(p, "w") as fh:
        for e in events:
            fh.write(json.dumps(e) + "\n")
    return p


def page(tmp, ledger, sub):
    out = os.path.join(tmp, sub)
    rc = D.main(["--dry-run", "--date", DATE, "--cut", CUT.strftime("%Y-%m-%dT%H:%M:%SZ"), "--ledger", ledger,
                 "--state", os.path.join(tmp, "state.json"), "--out-dir", out,
                 "--errors", os.path.join(tmp, "errors.log")])
    with open(os.path.join(out, "delegated_digest_%s.md" % DATE)) as fh:
        return rc, fh.read()


def ask_rows(text):
    """-> [(id, filed, days, hours, state, needs, blocked, direct, chain)] from the asks table."""
    rows = []
    for line in text.splitlines():
        m = re.match(r"\| ([A-Z][A-Z0-9_]+) \| (\S+) \| (\d+) \| (\d+) \| (\S+) \| (\S+) \| (yes|no) \| (\d+) \| (\d+) \|$",
                     line)
        if m:
            g = m.groups()
            rows.append((g[0], g[1], int(g[2]), int(g[3]), g[4], g[5], g[6], int(g[7]), int(g[8])))
    return rows


def verdicts(text):
    """-> {name: ok} for the page's owner-asks claims (a function, so the planted faults can be shown to trip it)."""
    rows = ask_rows(text)
    ids = [r[0] for r in rows]
    by = {r[0]: r for r in rows}
    head = re.search(r"^## Open OWNER asks (\d+)$", text, re.M)
    v = {
        "listed": sorted(ids) == sorted(EXPECT) and head is not None and int(head.group(1)) == len(EXPECT),
        "order": ids == ORDER,
        "age": all(i in by and by[i][2:4] == EXPECT[i][:2] for i in EXPECT),
        "waiting": all(i in by and by[i][7:9] == EXPECT[i][2:] for i in EXPECT),
        "withheld": "OPS_ACCOUNT_DRAIN_ASK" not in text and re.search(r"Withheld: 1; malformed: 0\.", text) is not None,
        "default": ("no default is applied or recommended" in text
                    and len(re.findall(r"\bdefault\b", text, re.I)) == 1),
        "filed": by.get("ASK_OLD_ONE", (None, None))[1] == ts(245),
    }
    return v


def test_fixture_real_path():
    with tempfile.TemporaryDirectory() as tmp:
        led = write_ledger(tmp, fixture())
        from rimflow import model
        w = model.replay(model.read(led))
        check(not w.errors, "instrument: the fixture ledger replays with no refused event (%s)" % (w.errors[:2],))
        check(w.items["W_LIFTED"].blocked and w.items["W_FOUR"].blocked and w.items["W_FIVE"].blocked,
              "instrument: the planted blocks are on the books (a released one too)")
        rc, text = page(tmp, led, "out")
        check(rc == 0, "real path: main --dry-run --ledger exits 0")
        for k, ok in verdicts(text).items():
            check(ok, "owner asks %s: %s" % (k, ask_rows(text)))
        check(not os.path.exists(os.path.join(tmp, "state.json")), "a dry run writes no state")


def test_planted_faults_are_seen():
    """The assertions see a fault: break the code under test, the matching verdict goes false."""
    from rimflow import priority as PR
    with tempfile.TemporaryDirectory() as tmp:
        led = write_ledger(tmp, fixture())
        real = PR.block_holds
        PR.block_holds = lambda world, it, now: False          # every block reads released
        try:
            _rc, text = page(tmp, led, "fault_holds")
        finally:
            PR.block_holds = real
        check(not verdicts(text)["waiting"], "planted: with block_holds broken the waiting check FAILS")
        real_oa = D.owner_asks
        D.owner_asks = lambda world, cut: [dict(a, id=a["id"]) for a in real_oa(world, cut)] + [
            {"id": "BENCH_NOT_AN_ASK", "filed": CUT, "age_hours": 0, "state": "proposed", "needs": "offline",
             "blocked": False, "waiting": 0, "chain": 0}]      # the OWNER filter broken: a BENCH item listed
        try:
            _rc, text = page(tmp, led, "fault_filter")
        finally:
            D.owner_asks = real_oa
        check(not verdicts(text)["listed"], "planted: with the OWNER filter broken the listed check FAILS")


def test_unmeasured():
    with tempfile.TemporaryDirectory() as tmp:
        rc, text = page(tmp, os.path.join(tmp, "missing.jsonl"), "out")
        check(rc == 0 and "## Open OWNER asks UNMEASURED" in text and not ask_rows(text),
              "an unreadable ledger reads the asks UNMEASURED, never zero")


def test_real_ledger_sees_asks():
    """Instrument sanity on the real ledger: the section is measured and lists >0 asks (35 open OWNER items on
    2026-11-04)."""
    from rimflow import model
    w = model.replay(model.read())
    n = sum(1 for i in w.items.values() if i.open and i.owner == "OWNER")
    asks = D.owner_asks(w, dt.datetime.now(dt.timezone.utc))
    check(n > 0 and len(asks) == n, "real: owner_asks sees every open OWNER item (%d of %d)" % (len(asks), n))


def test_account_edge_withheld():
    from contracts import blind as BL
    from contracts import blind_core as C
    real = C.account_keys
    C.account_keys = lambda: frozenset(real()) | {"zorbanote"}       # a fixture account: "..._ZORBA" + " note"
    try:
        ev = [{"seat": "BENCH", "event": "note", "id": "ASK_TO_ZORBA", "text": "x", "why": "delegated: scope",
               "ts": ts(2)},
              {"seat": "BENCH", "event": "note", "id": "ASK_OLD_ONE", "text": "x", "why": "delegated: scope",
               "ts": ts(3)}]
        reads = {s: D._read() for s in D.SOURCES}
        reads["ledger"] = D.ledger_read(ev)
        ids = BL.Identity(frozenset({"ASK_TO_ZORBA", "ASK_OLD_ONE"}), frozenset())
        asks = [{"id": "ASK_TO_ZORBA", "filed": CUT, "age_hours": 0, "state": "proposed", "needs": "offline",
                 "blocked": False, "waiting": 0, "chain": 0}]
        text, _seen = D.build(DATE, None, CUT, reads, ids=ids, asks=asks)
        check("ZORBA" not in text and "ASK_OLD_ONE" in text and "Withheld: 1;" in text,
              "edge: an id that joins its neighbour into an account is withheld (record and ask), the rest shown")
    finally:
        C.account_keys = real


def main():
    for t in (test_account_edge_withheld, test_fixture_real_path, test_planted_faults_are_seen, test_unmeasured, test_real_ledger_sees_asks):
        try:
            t()
        except Exception as e:  # noqa: BLE001
            import traceback
            traceback.print_exc()
            check(False, "%s crashed: %s" % (t.__name__, e))
    print("%d failure(s)" % len(FAILS))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
