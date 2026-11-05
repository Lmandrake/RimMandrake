#!/usr/bin/env python3
"""selftest_walk_metrics.py - the `walk` verb and W1-W4 read from it (OWNER_WALK_MEASURE_STAGED_AND_DONE).

Pure cases replay hand-built events through model.replay; the CLI cases run the real cli.py as a subprocess against a
throwaway ledger (RIMFLOW_LEDGER) and never touch the real one.
"""
from __future__ import annotations

import datetime as dt
import json
import os
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
from rimflow import model, walk_metrics        # noqa: E402

CLI = os.path.join(HERE, "cli.py")
REPO = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
NOW = dt.datetime(2026, 11, 5, 0, 0, 0, tzinfo=dt.timezone.utc)
PASS, FAIL = [], []


def case(name, fn):
    try:
        fn()
        PASS.append(name)
        print("PASS", name)
    except Exception as e:                             # noqa: BLE001
        FAIL.append(name)
        print("FAIL", name, "-", type(e).__name__, e)


def ev(n, **kw):
    kw.setdefault("ts", "2026-11-0%dT00:00:00Z" % n)
    kw.setdefault("tsn", 1793000000000000000 + n)
    return kw


def filed(iid, title, needs="owner", n=1):
    return ev(n, seat="BENCH", event="file", id=iid, title=title, kind="task", needs=needs, **{"for": "BENCH"})


def walk(iid, phase, n, seat="BENCH", **kw):
    return ev(n, seat=seat, event="walk", id=iid, phase=phase, **kw)


def t_no_walk_event_is_unmeasured_not_zero():
    w = model.replay([filed("A_WALK_X", "owner walk the canyon"), filed("B_OFF_X", "refactor", needs="offline")])
    m = walk_metrics.measure(w, NOW)
    assert m["W1"]["value"] == 1 and m["W1"]["items"] == ["A_WALK_X"], m["W1"]
    assert m["W2"]["value"] == "0/1", m["W2"]
    assert m["W3"]["value"] == walk_metrics.UNMEASURED and m["W4"]["value"] == walk_metrics.UNMEASURED, m


def t_staged_then_done_moves_every_metric():
    evs = [filed("A_WALK_X", "owner walk the canyon"),
           filed("C_LOOK_X", "art check", n=1),                       # no walk title: owed only once a walk names it
           walk("A_WALK_X", "staged", 2, save="canyon.rws"),
           walk("C_LOOK_X", "staged", 2)]
    w = model.replay(evs)
    m = walk_metrics.measure(w, NOW)
    assert m["W1"]["items"] == ["A_WALK_X", "C_LOOK_X"], m["W1"]
    assert m["W2"]["value"] == "2/2", m["W2"]
    assert w.items["A_WALK_X"].walks[0]["save"] == "canyon.rws"
    evs.append(walk("A_WALK_X", "done", 3, seat="OWNER", found=2, findings=["F_ONE_X", "F_TWO_X"], detail="dust"))
    m = walk_metrics.measure(model.replay(evs), NOW)
    assert m["W2"]["value"] == "1/2" and m["W2"]["unstaged"] == ["A_WALK_X"], m["W2"]   # a done consumes the staging
    assert m["W3"]["value"] == 2.0 and m["W3"]["item"] == "A_WALK_X" and m["W3"]["found"] == 2, m["W3"]
    assert m["W4"]["value"] == 2.0 and m["W4"]["walks"] == 1, m["W4"]
    evs.append(walk("C_LOOK_X", "done", 4, seat="OWNER", found=0))
    m = walk_metrics.measure(model.replay(evs), NOW)
    assert m["W3"]["item"] == "C_LOOK_X" and m["W3"]["value"] == 1.0, m["W3"]
    assert m["W4"]["value"] == 1.0 and m["W4"]["findings"] == 2, m["W4"]


def t_done_without_found_leaves_w4_unmeasured():
    w = model.replay([filed("A_WALK_X", "walk"), walk("A_WALK_X", "done", 2, seat="OWNER")])
    m = walk_metrics.measure(w, NOW)
    assert m["W3"]["value"] == 3.0, m["W3"]
    assert m["W4"]["value"] == walk_metrics.UNMEASURED, m["W4"]


def t_a_walk_on_a_closed_item_counts_for_w3_not_w1():
    w = model.replay([filed("A_WALK_X", "walk"), ev(2, seat="BENCH", event="drop", id="A_WALK_X", reason="walked already"),
                      walk("A_WALK_X", "done", 3, seat="OWNER", found=1)])
    m = walk_metrics.measure(w, NOW)
    assert m["W1"]["value"] == 0 and m["W3"]["item"] == "A_WALK_X", m


def t_bad_walks_are_refused():
    host = filed("A_WALK_X", "walk")
    for bad, why in ((walk("A_WALK_X", "done", 2), "an agent's own `done`"),
                     (walk("A_WALK_X", "half", 2), "an unknown phase"),
                     (walk("A_WALK_X", "staged", 2, found=1), "`found` on a staging"),
                     (walk("A_WALK_X", "done", 2, seat="OWNER", found=-1), "a negative count"),
                     (walk("A_WALK_X", "done", 2, seat="OWNER", found=True), "a bool count"),
                     (walk("A_WALK_X", "done", 2, seat="OWNER", findings="F_ONE_X"), "findings not a list")):
        try:
            model.replay([dict(host), dict(bad)], strict=True)
        except model.LedgerError:
            continue
        raise AssertionError("%s was accepted" % why)
    w = model.replay([dict(host), walk("A_WALK_X", "done", 2)])                   # non-strict: refused, not fatal
    assert w.items["A_WALK_X"].walks == [] and w.errors, "a refused walk must apply nothing and be counted"


def _cli(tmp, seat, *args):
    e = {k: v for k, v in os.environ.items() if k not in ("RIMFLOW_SEAT", "AGENT_SEAT", "CLAUDE_SESSION_ID")}
    e.update(RIMFLOW_LEDGER=os.path.join(tmp, "events.jsonl"), RIMFLOW_ITEMS=os.path.join(tmp, "items"),
             RIMFLOW_PROBE="no-reading", RIMFLOW_SEAT=seat, RIMFLOW_GITINDEX="off")
    p = subprocess.run([sys.executable, CLI] + list(args), cwd=REPO, env=e, capture_output=True, text=True,
                       timeout=120)
    return p.returncode, p.stdout, p.stderr


def t_cli_writes_and_reads_walk_events():
    tmp = tempfile.mkdtemp(prefix="walkmetrics_")
    real = [os.path.join(REPO, "infrastructure", "state", "ledger", "events")]
    before = {f: os.path.getsize(os.path.join(real[0], f)) for f in os.listdir(real[0])} if os.path.isdir(real[0]) else {}
    try:
        os.makedirs(os.path.join(tmp, "items"))
        rc, out, err = _cli(tmp, "BENCH", "file", "CANYON_WALK_MEASURE_DUSTY_BOOTS", "--for", "BENCH",
                            "--title", "owner walk the canyon in game", "--needs", "owner")
        assert rc == 0, (out, err)
        rc, out, err = _cli(tmp, "BENCH", "walk", "staged", "CANYON_WALK_MEASURE_DUSTY_BOOTS", "--save", "canyon.rws")
        assert rc == 0 and "walk staged" in out, (out, err)
        rc, out, err = _cli(tmp, "BENCH", "walk", "done", "CANYON_WALK_MEASURE_DUSTY_BOOTS", "--found", "1")
        assert rc != 0, "an agent's own walk-done was accepted: %s" % out
        rc, out, err = _cli(tmp, "BENCH", "walk", "staged", "CANYON_WALK_MEASURE_DUSTY_BOOTS", "--found", "1")
        assert rc != 0, "--found on a staging was accepted"
        rc, out, err = _cli(tmp, "BENCH", "walks", "--json")
        assert rc == 0 and json.loads(out)["W2"]["value"] == "1/1", (out, err)
        rc, out, err = _cli(tmp, "BENCH", "walk", "done", "CANYON_WALK_MEASURE_DUSTY_BOOTS", "--found", "2",
                            "--findings", "F_ONE_X,F_TWO_X", "--owner-said", "walked the canyon, two things off")
        assert rc == 0, (out, err)
        rc, out, err = _cli(tmp, "BENCH", "walks", "--json")
        m = json.loads(out)
        assert m["W4"]["value"] == 2.0 and m["W3"]["findings"] == ["F_ONE_X", "F_TWO_X"], m
        rc, out, err = _cli(tmp, "BENCH", "walks")
        assert rc == 0 and "W3 last walk age" in out and "W4 walk yield" in out, out
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    after = {f: os.path.getsize(os.path.join(real[0], f)) for f in os.listdir(real[0])} if os.path.isdir(real[0]) else {}
    assert before == after, "the real ledger was written"


CASES = [t_no_walk_event_is_unmeasured_not_zero, t_staged_then_done_moves_every_metric,
         t_done_without_found_leaves_w4_unmeasured, t_a_walk_on_a_closed_item_counts_for_w3_not_w1,
         t_bad_walks_are_refused, t_cli_writes_and_reads_walk_events]

if __name__ == "__main__":
    for fn in CASES:
        case(fn.__name__, fn)
    print("\n%d/%d passed" % (len(PASS), len(PASS) + len(FAIL)))
    sys.exit(1 if FAIL else 0)
