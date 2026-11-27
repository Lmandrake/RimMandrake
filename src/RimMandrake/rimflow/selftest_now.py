#!/usr/bin/env python3
"""selftest_now.py: the promises of design/specs/2026-11-27-now/boundary.md (each t_ function is one promise, by
name). Offline: fake readers, fake run records, a fake ledger world. Written before now.py; seen failing on the base
(the module and ./now absent).

    python3 src/RimMandrake/rimflow/selftest_now.py
"""
import contextlib
import io
import os
import re
import subprocess
import sys
import time
from types import SimpleNamespace as NS

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
for _p in (HERE, os.path.join(REPO, "src", "RimMandrake")):
    if _p not in sys.path:
        sys.path.insert(0, _p)
sys.dont_write_bytecode = True
os.environ["RM_UNDER_SELFTEST"] = "1"
NOW = 1_800_000_000.0


def _now():
    import now as N
    return N


def t_each_reader_has_a_line():
    N = _now()
    out = N.screen({"alpha": lambda: "one\ntwo", "beta": lambda: "", "gamma": lambda: None}, deadline_s=5)
    for name in ("alpha", "beta", "gamma"):
        assert any("] %s: " % name in ln for ln in out.splitlines()), "no line for reader %s:\n%s" % (name, out)
    assert "beta: none (looked)" in out, "an empty answer does not read none (looked):\n%s" % out
    assert "gamma: COULD NOT LOOK" in out, "a reader that returns None is not COULD NOT LOOK:\n%s" % out
    names = list(N.readers())
    for name in ("locks", "pipe", "accounts", "runs", "queue"):
        assert name in names, "./now has no %s reader (it has %s)" % (name, names)
    assert os.access(os.path.join(REPO, "now"), os.X_OK), "./now at the repo root is absent or not executable"


def t_a_reader_that_raises_reads_could_not_look():
    N = _now()

    def boom():
        raise RuntimeError("exit 2: the lock file is gone")
    out = N.screen({"locks": boom, "pipe": lambda: "ALL ON"}, deadline_s=5)
    line = [ln for ln in out.splitlines() if "] locks: " in ln]
    assert line and "COULD NOT LOOK" in line[0] and "the lock file is gone" in line[0], out
    assert any("] pipe: ALL ON" in ln for ln in out.splitlines()), "the other reader lost its line:\n%s" % out


def t_a_hung_reader_does_not_hold_the_screen():
    N = _now()
    t0 = time.monotonic()
    out = N.screen({"queue": lambda: time.sleep(60), "pipe": lambda: "ALL ON"}, deadline_s=1)
    took = time.monotonic() - t0
    assert took < 10, "a hung reader held the screen %.1f s" % took
    line = [ln for ln in out.splitlines() if "] queue: " in ln]
    assert line and "COULD NOT LOOK" in line[0] and "no answer in 1 s" in line[0], out
    # the process ends too: a hung reader thread does not keep ./now alive after it printed
    code = ("import sys,time; sys.path.insert(0,%r); import now; "
            "print(now.screen({'q': lambda: time.sleep(120)}, deadline_s=1))" % HERE)
    t0 = time.monotonic()
    r = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True, timeout=60)
    took = time.monotonic() - t0
    assert r.returncode == 0 and "COULD NOT LOOK" in r.stdout, (r.returncode, r.stdout, r.stderr)
    assert took < 30, "the process stayed %.1f s for a hung reader" % took


def t_live_runs_listed_with_age():
    N = _now()
    recs = [
        {"unit": "rm-detached-bench-a-1", "item": "ITEM_A", "model": "opus", "status": "running", "at": NOW - 600},
        {"unit": "rm-detached-bench-b-2", "item": "ITEM_B", "model": "sonnet", "status": "finished", "at": NOW - 60},
        {"unit": "rm-detached-bench-c-3", "item": "ITEM_C", "model": "opus", "status": "running", "at": NOW - 3 * 3600},
        {"unit": "rm-detached-bench-d-4", "item": "ITEM_D", "model": "opus", "status": "launching", "at": NOW - 30},
    ]
    st = {"rm-detached-bench-a-1": "running", "rm-detached-bench-c-3": "dead", "rm-detached-bench-d-4": "launching"}
    out = N.live_runs(records=lambda: iter(recs), status=lambda r: st[r["unit"]], now=NOW)
    text = "\n".join(out)
    assert "ITEM_B" not in text, "a finished run is listed:\n%s" % text
    a = [ln for ln in out if "ITEM_A" in ln]
    assert a and "10 min" in a[0] and "rm-detached-bench-a-1" in a[0] and "running" in a[0], text
    c = [ln for ln in out if "ITEM_C" in ln]
    assert c and "3.0 h" in c[0] and "DEAD" in c[0], "a dead unit is not marked DEAD with its age:\n%s" % text
    assert any("ITEM_D" in ln and "launching" in ln for ln in out), text
    assert N.live_runs(records=lambda: iter([recs[1]]), status=lambda r: "finished", now=NOW) == [], \
        "no live run is not an empty answer (the screen reads it none (looked))"


def t_queue_head_listed():
    N = _now()
    items = [NS(id="ITEM_%02d" % i, state="ready", title="title %d" % i) for i in range(9)]
    loaded = []

    def load():
        loaded.append(1)
        return [], NS(items={})
    out = N.queue_head(load=load, rank=lambda w, seat: items, n=5)
    text = "\n".join(out)
    assert loaded, "the queue reader did not read the ledger"
    ids = [ln.split()[0] for ln in out if ln.startswith("ITEM_")]
    assert ids == ["ITEM_00", "ITEM_01", "ITEM_02", "ITEM_03", "ITEM_04"], "not the head in rank order: %s" % ids
    assert "title 0" in text and "ready" in text, text
    assert "4 more" in text, "the rest is not counted:\n%s" % text
    assert "rimflow next" not in text, "the line sends the reader to `rimflow next`, which reserves a lease"
    assert N.queue_head(load=load, rank=lambda w, seat: [], n=5) == [], "an empty queue is not an empty answer"
    # the named command lists the rest: run it. (`cli.py queue BENCH` is a compact view: on 2026-11-27 it held 15
    # of the 37 ranked items, so a line that named it sent the reader to a list without them.)
    more = [ln for ln in out if ln.startswith("...")]
    assert more and "(./now --queue lists them)" in more[0], "the line names no command that this test can run: %s" % more
    real = (N._load, N._rank)
    N._load, N._rank = load, (lambda w, seat: items)
    buf = io.StringIO()
    try:
        with contextlib.redirect_stdout(buf):
            rc = N.main(["--queue"])
    finally:
        N._load, N._rank = real
    listed = re.findall(r"\] queue: (ITEM_\d+) ", buf.getvalue())
    assert rc == 0 and listed == [i.id for i in items], "./now --queue does not list the whole queue in rank order " \
        "(rc %s): %s\n%s" % (rc, listed, buf.getvalue())
    assert "more (" not in buf.getvalue() and "rimflow next" not in buf.getvalue(), buf.getvalue()
    err = io.StringIO()
    with contextlib.redirect_stderr(err), contextlib.redirect_stdout(io.StringIO()):
        rc = N.main(["--bogus"])
    assert rc == 2 and "--queue" in err.getvalue(), "an unknown argument does not exit 2 with its usage (%s)" % rc


def main():
    failed = 0
    tests = [t_each_reader_has_a_line, t_a_reader_that_raises_reads_could_not_look, t_a_hung_reader_does_not_hold_the_screen,
             t_live_runs_listed_with_age, t_queue_head_listed]
    for t in tests:
        try:
            t()
            print("PASS", t.__name__)
        except Exception as e:  # noqa: BLE001 - a promise whose test cannot run is a FAIL, never a crash
            failed += 1
            print("FAIL", t.__name__, "%s: %s" % (type(e).__name__, str(e)[:400]))
    print("FAILED %d of %d" % (failed, len(tests)) if failed else "ALL PASS (%d)" % len(tests))
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
