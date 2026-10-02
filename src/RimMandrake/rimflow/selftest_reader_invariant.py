#!/usr/bin/env python3
"""Selftest: the ledger reader invariant (git plan §2.5) and concurrent-claim resolution.

Union-merged shards carry duplicate lines and arbitrary interleave, so `model.read()`
must collapse identical events and order by content, never by file position. Runs
against throwaway ledgers only; the last case folds the REAL ledger read-only and
checks the new order projects identically to the pre-2026-10-02 file-position order.
"""
import os
import random
import shutil
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
from rimflow import model                                        # noqa: E402

PASS, FAIL = [], []


def case(name, fn):
    try:
        fn()
        PASS.append(name)
        print("ok    %s" % name)
    except Exception as e:                                       # noqa: BLE001
        FAIL.append(name)
        print("FAIL  %s\n        %s: %s" % (name, type(e).__name__, e))


def E(ts, verb, iid, seat="FOUNDRY", **kw):
    d = dict(seat=seat, event=verb, id=iid, ts=ts)
    d.update(kw)
    return d


FILE = E("2026-10-02T01:00:00Z", "file", "ALPHA_BETA_GAMMA_1", seat="BENCH",
         title="t", kind="task", **{"for": "FOUNDRY"})
CLAIM = E("2026-10-02T01:00:00Z", "claim", "ALPHA_BETA_GAMMA_1")
START = E("2026-10-02T01:00:00Z", "start", "ALPHA_BETA_GAMMA_1")
NOTE = E("2026-10-02T01:00:05Z", "note", "ALPHA_BETA_GAMMA_1", text="x")


def with_ledger(shards, fn):
    d = tempfile.mkdtemp()
    old = model.EVENTS
    try:
        model.EVENTS = os.path.join(d, "events.jsonl")
        os.makedirs(os.path.join(d, "events"))
        for seat, lines in shards.items():
            with open(os.path.join(d, "events", seat + ".jsonl"), "w") as fh:
                for ev in lines:
                    fh.write(model.event_key(ev) + "\n")
        return fn()
    finally:
        model.EVENTS = old
        shutil.rmtree(d)


def t_identical_duplicates_collapse():
    evs = with_ledger({"BENCH": [FILE], "FOUNDRY": [CLAIM, START, CLAIM, START, NOTE, NOTE]},
                      model.read)
    assert len(evs) == 4, "expected 4 distinct events, got %d" % len(evs)


def t_order_independent_of_position():
    base = [CLAIM, START, NOTE]
    want = [model.event_key(e) for e in model.canonical_order([FILE] + base)]
    rnd = random.Random(7)
    for _ in range(25):
        shuffled = base[:]
        rnd.shuffle(shuffled)
        got = with_ledger({"BENCH": [FILE], "FOUNDRY": shuffled}, model.read)
        assert [model.event_key(e) for e in got] == want, "order followed file position"
    # moving an event to another shard file must not change the order either
    got = with_ledger({"BENCH": [NOTE, FILE], "FOUNDRY": [START, CLAIM]}, model.read)
    assert [model.event_key(e) for e in got] == want


def t_same_second_causal_order():
    got = model.canonical_order([START, CLAIM, FILE])
    assert [e["event"] for e in got] == ["file", "claim", "start"], [e["event"] for e in got]
    w = model.replay(got)
    assert not w.errors, w.errors
    assert w.items["ALPHA_BETA_GAMMA_1"].state == "doing"


def t_tsn_orders_a_same_second_burst_across_files():
    """`game UP` then `game DOWN` in one second, by one writer: only `tsn` (stamped by
    append, i.e. content) can say which came first once position is meaningless."""
    up = dict(seat="OWNER", event="game", state="UP", ts="2026-10-02T02:00:00Z", tsn=1)
    down = dict(seat="OWNER", event="game", state="DOWN", ts="2026-10-02T02:00:00Z", tsn=2)
    got = with_ledger({"OWNER": [down, up]}, model.read)
    assert [e["state"] for e in got] == ["UP", "DOWN"], [e["state"] for e in got]
    d = tempfile.mkdtemp()
    try:
        p = os.path.join(d, "x.jsonl")
        model.append(dict(seat="OWNER", event="game", state="UP", ranBy="BENCH",
                          ownerSaid="game is up"), p)
        e = model._read_one(p)[0]
        assert isinstance(e.get("tsn"), int) and e["tsn"] > 0, e
    finally:
        shutil.rmtree(d)


def t_concurrent_claim_earliest_wins():
    c1 = E("2026-10-02T01:00:10Z", "claim", "ALPHA_BETA_GAMMA_1")
    c2 = E("2026-10-02T01:00:40Z", "claim", "ALPHA_BETA_GAMMA_1")
    # the later claim is written FIRST in the file — order must still follow ts
    evs = with_ledger({"BENCH": [FILE], "FOUNDRY": [c2, c1]}, model.read)
    w = model.replay(evs)
    cc = w.contested_claims
    assert len(cc) == 1, cc
    assert cc[0]["winner_ts"] == c1["ts"] and cc[0]["loser_ts"] == c2["ts"], cc
    assert w.items["ALPHA_BETA_GAMMA_1"].claim_ts == c1["ts"]


def t_reclaim_much_later_is_not_contested():
    c1 = E("2026-10-02T01:00:10Z", "claim", "ALPHA_BETA_GAMMA_1")
    c2 = E("2026-10-03T09:00:00Z", "claim", "ALPHA_BETA_GAMMA_1")
    w = model.replay(model.canonical_order([FILE, c1, c2]))
    assert w.contested_claims == [], w.contested_claims


def t_next_tells_the_loser():
    import io
    import contextlib
    from rimflow import cli
    import datetime as dt
    now = dt.datetime.now(dt.timezone.utc)
    f = lambda s: (now - dt.timedelta(seconds=s)).strftime("%Y-%m-%dT%H:%M:%SZ")  # noqa
    fl = dict(FILE, ts=f(120))
    c1 = E(f(100), "claim", "ALPHA_BETA_GAMMA_1")
    c2 = E(f(60), "claim", "ALPHA_BETA_GAMMA_1")
    w = model.replay(model.canonical_order([fl, c2, c1]))
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        cli._warn_contested_claims(w, "FOUNDRY")
    out = buf.getvalue()
    assert "CONTESTED CLAIM" in out and c2["ts"] in out and c1["ts"] in out, out
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        cli._warn_contested_claims(w, "BENCH")
    assert buf.getvalue() == "", "another seat was told about FOUNDRY's race"


def t_real_ledger_projects_as_before():
    """Read-only. The content order must fold the live ledger into the same World the
    old (ts, file rank, file position) order did — checked 2026-10-02 at 13,825 events."""
    files = model.ledger_files()
    if not files:
        print("        (no ledger here — UNMEASURED, not a pass)")
        return
    old = []
    for rank, f in enumerate(files):
        old.extend((str(ev.get("ts") or ""), rank, ev) for ev in model._read_one(f))
    old.sort(key=lambda t: (t[0], t[1]))
    old = [t[2] for t in old]
    new = model.read()

    def proj(evs):
        w = model.replay(evs)
        return ({k: (i.state, i.owner, i.blocked, i.closed_sha) for k, i in w.items.items()},
                w.bridge_holder, w.game, sorted(e[2][:80] for e in w.errors))
    a, b = proj(old), proj(new)
    diff = [k for k in set(a[0]) | set(b[0]) if a[0].get(k) != b[0].get(k)]
    assert not diff, "items project differently: %s" % diff[:5]
    assert a[1:] == b[1:], "bridge/game/errors differ"


for n, f in sorted((k, v) for k, v in globals().items() if k.startswith("t_")):
    case(n, f)
print("\n%d passed, %d failed" % (len(PASS), len(FAIL)))
sys.exit(1 if FAIL else 0)
