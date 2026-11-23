#!/usr/bin/env python3
"""selftest_maturation_trend.py: the promises of design/specs/2026-11-23-ticket-trend-graph/boundary.md.

    python3 src/RimMandrake/Utils/selftest_maturation_trend.py

Fixture ledger events folded by the real model.replay; no real ledger, no network, no game.
"""
import datetime as dt
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "rimflow"))
try:
    import maturation_trend as T  # noqa: E402
except ImportError:
    T = None
import maturation_nonmod as N  # noqa: E402

NOW = float(dt.datetime(2026, 11, 23, 21, 30, tzinfo=dt.timezone.utc).timestamp())
H = 3600.0
MODS = ["FlowWorks", "Pyrelands", "Cauldron", "AlphaDeltaGamma", "AmberDuskGrove"]
SEQ = [0]


def iso(t):
    return dt.datetime.fromtimestamp(t, dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def ev(event, iid, ago_h, seat="BENCH", **kw):
    SEQ[0] += 1
    e = {"event": event, "seat": seat, "ts": iso(NOW - ago_h * H), "tsn": SEQ[0]}
    if iid:
        e["id"] = iid
    e.update(kw)
    return e


def filed(iid, ago_h, title="A plain thing", **kw):
    return ev("file", iid, ago_h, title=title, kind="task", **dict({"for": "BENCH"}, **kw))


def closed(iid, ago_h):
    return ev("close", iid, ago_h, sha="0000000", noCode="done")


def drop(iid, ago_h):
    return ev("drop", iid, ago_h, reason="not worth it")


def run(evs, runs=(), held=("Cauldron",), old=("OldMod",), now=NOW):
    assert T is not None, "no maturation_trend.py: the page has no graph of tickets by hour"
    import model
    evs = sorted(evs, key=lambda e: (e["ts"], e["tsn"]))
    d = T.hours(evs, now, MODS, N.classify, (), runs, held, old, replay=model.replay)
    d["state"] = "ok"
    return d


BASE = [filed("RIMMANDRAKE_FIX_PAGE_TYPO_ONE", 150), filed("RIMMANDRAKE_FIX_PAGE_TYPO_TWO", 10.2),
        filed("RIMMANDRAKE_TUNE_PYRELANDS_FIRE", 20.2), filed("RIMMANDRAKE_FIX_CAULDRON_POT", 9),
        filed("RIMMANDRAKE_FIX_OLDMOD_LAMP", 9), filed("RIMMANDRAKE_FIX_ADG_THING", 9),
        filed("RIMMANDRAKE_STALE_ONE_NOBODY_TOUCHED", 24 * 12), closed("RIMMANDRAKE_FIX_PAGE_TYPO_TWO", 5.2)]


def bin_of(d, ago_h):
    t = NOW - ago_h * H
    return next(k for k, e in enumerate(d["ends"]) if t < e or k == len(d["ends"]) - 1)


def t_hours_of_five_days():
    d = run(BASE)
    assert len(d["ends"]) == 121 and d["ends"][-1] == NOW and d["ends"][0] == d["t0"] + H
    assert all((e % 3600) == 0 for e in d["ends"][:-1]) and d["ends"][-2] <= NOW
    for c in T.CLASSES:
        for k in ("waiting", "opened", "closed"):
            assert len(d[k][c]) == 121


def t_stocks_and_flows_by_replay():
    d = run(BASE)
    nm, m = d["waiting"]["nonmod"], d["waiting"]["mod"]
    assert nm[bin_of(d, 100)] == 1 and nm[bin_of(d, 8)] == 2 and nm[-1] == 1, (nm[bin_of(d, 8)], nm[-1])
    assert m[bin_of(d, 30)] == 0 and m[-1] == 1
    assert d["opened"]["nonmod"][bin_of(d, 10.2)] == 1 and sum(d["opened"]["nonmod"]) == 1
    assert d["closed"]["nonmod"][bin_of(d, 5.2)] == 1 and sum(d["closed"]["nonmod"]) == 1
    assert sum(d["opened"]["mod"]) == 1 and sum(d["closed"]["mod"]) == 0
    # with nothing stale or parked, waiting moves by exactly opened minus closed
    for c in T.CLASSES:
        for k in range(1, 121):
            assert d["waiting"][c][k] - d["waiting"][c][k - 1] == d["opened"][c][k] - d["closed"][c][k], (c, k)
    # an event after now is not counted
    assert run(BASE + [filed("RIMMANDRAKE_LATER_THAN_NOW_ONE", -2)])["waiting"]["nonmod"][-1] == 1
    # a spawned ticket is opened, and a drop closes
    s = run(BASE + [ev("spawn", None, 4, name="RIMMANDRAKE_SPAWNED_FROM_ONE", title="Spawned", kind="task",
                       **{"for": "BENCH", "from": "RIMMANDRAKE_FIX_PAGE_TYPO_ONE"}),
                    drop("RIMMANDRAKE_FIX_PAGE_TYPO_ONE", 3)])
    assert s["opened"]["nonmod"][bin_of(s, 4)] == 1 and s["closed"]["nonmod"][bin_of(s, 3)] == 1, s["opened"]["nonmod"][-8:]


def t_left_out_tickets_are_named_and_counted():
    d = run(BASE + [filed("RIMMANDRAKE_PARKED_ON_A_DATE", 8),
                    ev("start", "RIMMANDRAKE_PARKED_ON_A_DATE", 7.5),
                    ev("wait", "RIMMANDRAKE_PARKED_ON_A_DATE", 7, until="2026-12-01", reason="next week"),
                    filed("RIMMANDRAKE_BLOCKED_ON_ONE", 8),
                    ev("block", "RIMMANDRAKE_BLOCKED_ON_ONE", 7, reason="after", on="RIMMANDRAKE_FIX_PAGE_TYPO_ONE", kind="item"),
                    filed("RIMMANDRAKE_FREED_WHEN_TWO_CLOSED", 8),
                    ev("block", "RIMMANDRAKE_FREED_WHEN_TWO_CLOSED", 7, reason="after", on="RIMMANDRAKE_FIX_PAGE_TYPO_TWO",
                       kind="item")])
    o = d["out"]
    assert o["mod"] == {"held": 1, "oldmod": 0, "later": 0, "parked": 0, "stale": 0}, o
    assert o["nonmod"] == {"held": 0, "oldmod": 1, "later": 0, "parked": 2, "stale": 1}, o
    nm = d["waiting"]["nonmod"]
    assert nm[-1] == 2 and nm[bin_of(d, 6.4)] == 2, (nm[-1], nm[bin_of(d, 6.4)])   # freed when its blocker closed
    assert sum(d["opened"]["nonmod"]) == 4, "a ticket filed and then parked was still opened"
    assert d["flow_out"]["opened"] == 2, d["flow_out"]
    x = run(BASE + [drop("RIMMANDRAKE_STALE_ONE_NOBODY_TOUCHED", 2)])
    assert x["flow_out"]["closed"] == 1 and sum(x["closed"]["nonmod"]) == 1, "a stale ticket's drop is drawn as work"
    # a note or a program's re-check does not make a stale ticket fresh; taking it up does
    n = run(BASE + [ev("note", "RIMMANDRAKE_STALE_ONE_NOBODY_TOUCHED", 2, text="sweep")])
    assert n["out"]["nonmod"]["stale"] == 1
    c = run(BASE + [ev("start", "RIMMANDRAKE_STALE_ONE_NOBODY_TOUCHED", 2)])
    assert c["out"]["nonmod"]["stale"] == 0 and c["waiting"]["nonmod"][-1] == 2, c["out"]
    L = " ".join(T.rule_lines(d))
    for k in T.GROUPS:
        assert T.GROUP_WORDS[k] in L, k
    assert "Left out now: 5 of" in L, L


def t_mod_by_the_page_rule_and_unclassed_counted():
    d = run(BASE)
    assert d["unclassed"] == 1 and "Could not class: 1" in " ".join(T.rule_lines(d))
    assert T.names_old_mod("RIMMANDRAKE_FIX_OLDMOD_LAMP", "", {"OLDMOD"}) and \
        T.names_old_mod("X_Y", "the OldMod lamp", {"OLDMOD"}) and not T.names_old_mod("X_OLD", "a lamp", {"OLDMOD"})


def t_worked_is_run_or_lease():
    iid = "RIMMANDRAKE_FIX_PAGE_TYPO_ONE"
    d = run(BASE, runs=[(iid, NOW - 3.2 * H, NOW - 1.2 * H), ("RIMMANDRAKE_TUNE_PYRELANDS_FIRE", NOW - H, None)])
    assert d["worked"][-1] == 1 and d["worked"][bin_of(d, 2.2)] == 1 and d["worked"][bin_of(d, 8)] == 0, d["worked"][-6:]
    assert d["waiting"]["nonmod"][bin_of(d, 2.2)] == 0 and d["waiting"]["mod"][-1] == 0, "a worked ticket still waits"
    le = ev("lease", iid, 0.4, action="take", token="BENCH.pid1.abcdef", expires=iso(NOW + 900))
    assert run(BASE + [le])["worked"][-1] == 1, "a live lease is being worked"
    assert run(BASE, runs=None)["worked"] == "UNMEASURED"
    assert T.run_spans([{"item": "A", "at": 1, "ended": 2}, {"item": "B", "at": 1, "ended": None, "status": "running"},
                        {"item": "C", "at": 1, "ended": None, "status": "dead"}], N.is_live) == [("A", 1, 2), ("B", 1, None)]
    assert T.run_spans(None, N.is_live) is None


def t_replay_matches_the_ledger():
    d = run(BASE)
    assert d["mismatch"] == 0 and d["open"] == 6, (d["mismatch"], d["open"])
    out = sum(sum(v.values()) for v in d["out"].values())
    assert sum(d["waiting"][c][-1] for c in T.CLASSES) + d["worked"][-1] + out + d["unclassed"] == d["open"]
    assert "disagree" in " ".join(T.rule_lines(dict(d, mismatch=3)))


def t_graph_is_one_line_with_six_series():
    d = run(BASE + [closed("RIMMANDRAKE_TUNE_PYRELANDS_FIRE", 3)], runs=[("RIMMANDRAKE_FIX_PAGE_TYPO_ONE", NOW - H, None)])
    b = T.block(d)
    assert "\n" not in b and b.startswith("<div") and b.count("<svg") == 1
    for c in T.CLASSES:
        assert re.search(r'stroke="%s" stroke-width="2' % T.COL[c], b), "no waiting line for " + c
        assert 'fill="%s"/>' % T.MUTED[c] in b, "no closed bars for " + c
        assert re.search(r'<rect [^>]*fill="%s"/>' % T.COL[c], b), "no opened bars for " + c
    for w in ("WAITING at the end of each hour", "NON-MOD: OPENED", "MOD: OPENED", "BEING WORKED", "Mon Nov 23", "1 opened",
              "tickets waiting"):
        assert w in b, w
    h, P = T.ops(d)
    assert all(-1 <= p[2] <= h for p in P if p[0] in "rt"), "something is drawn off the graph"
    assert all(p[3] >= 0 and p[4] >= 0 for p in P if p[0] == "r")
    assert T.block(run(BASE)) == T.block(run(BASE)), "same inputs, same graph"


def t_four_answers_differ():
    d = run(BASE)
    blind = T.block(T.safe(None, NOW, MODS, N.classify, (), None, N.is_live, cause="ledger: OSError: gone"))
    failed = T.block(T.safe([{"ts": 5}, 7], NOW, MODS, N.classify, (), [], N.is_live))
    zero = T.block(run([]))
    norec = T.block(run(BASE, runs=None))
    assert "COULD NOT LOOK" in blind and "OSError: gone" in blind and "<svg" not in blind
    assert "FAILED" in failed and "<svg" not in failed, failed
    assert "0 tickets waiting, level in five days" in zero and "<svg" in zero
    assert "UNMEASURED: the run records could not be read" in norec and "0 now" not in norec
    assert len({blind, failed, zero, norec, T.block(d)}) == 5


def main():
    tests = [t_hours_of_five_days, t_stocks_and_flows_by_replay, t_left_out_tickets_are_named_and_counted,
             t_mod_by_the_page_rule_and_unclassed_counted, t_worked_is_run_or_lease, t_replay_matches_the_ledger,
             t_graph_is_one_line_with_six_series, t_four_answers_differ]
    failed = 0
    for t in tests:
        try:
            t()
            print("PASS", t.__name__)
        except Exception as e:  # noqa: BLE001
            failed += 1
            print("FAIL", t.__name__, "%s: %s" % (type(e).__name__, str(e)[:400]))
    print("FAILED %d of %d" % (failed, len(tests)) if failed else "ALL PASS (%d)" % len(tests))
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
