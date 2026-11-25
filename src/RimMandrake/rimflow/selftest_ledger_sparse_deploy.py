#!/usr/bin/env python3
"""Selftest for RIMMANDRAKE_TRACE_DEPLOY_SHARD_CUT_TO_ONE_LINE: a ledger append never writes a tracked shard that the
checkout left off disk, and the deploy update clears a stale index.lock that no process holds.

The failure (2026-11-12): the deploy checkout is sparse and its cone leaves out infrastructure/state/ledger. A rimflow
append whose ROOT resolved there opened events/BENCH.jsonl O_APPEND|O_CREAT, so the tracked 18,763-line shard became a
1-line file. git read it as 18,763 deletions, and `pull --ff-only` refused for about 36 h. In the same outage a git
killed at update_code's budget left .git/index.lock, and every later pass failed on it.

Cases (each a real git repo in a temp dir, nothing on the real ledger):
  A1 sparse cone without the ledger: append raises, names the checkout, creates no file; git status stays clean.
  A2 a tracked shard deleted by hand in a full checkout: append raises the same way (the same 1-line damage).
  A3 a tracked shard on disk: append writes one line (the normal path).
  A4 a new seat shard that git does not track: append creates it (a first event of a seat must still land).
  A5 a ledger outside any git repo (a test's throwaway ledger): append creates the shard.
  B1 a .git/index.lock older than the update budget, held by no process: update_code removes it, reports its age,
     and the pull lands.
  B2 a fresh index.lock (younger than the budget): update_code leaves it and fails loud (a live git may own it).
  B3 an old index.lock that a process holds open: update_code leaves it and fails loud.

    python3 src/RimMandrake/rimflow/selftest_ledger_sparse_deploy.py      exit 0 = all PASS
"""
import os
import subprocess
import sys
import tempfile
import time
from pathlib import Path

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(REPO, "src", "RimMandrake", "Utils", "ops_core"))

import model  # noqa: E402

FAILS = []


def check(name, ok, detail=""):
    print("%s  %s%s" % ("PASS" if ok else "FAIL", name, "" if ok else "  -- %s" % (detail,)))
    if not ok:
        FAILS.append(name)


def g(cwd, *a):
    return subprocess.run(["git", "-C", str(cwd), *a], check=True, capture_output=True, text=True).stdout.strip()


def make_repo(d, shard_lines=3):
    """-> a git repo with src/x.py and a tracked infrastructure/state/ledger/events/BENCH.jsonl of shard_lines lines."""
    r = Path(d)
    g(r, "init", "-q", "-b", "main")
    g(r, "config", "user.email", "t@t")
    g(r, "config", "user.name", "t")
    (r / "src").mkdir()
    (r / "src" / "x.py").write_text("x = 1\n")
    ev = r / "infrastructure" / "state" / "ledger" / "events"
    ev.mkdir(parents=True)
    (ev / "BENCH.jsonl").write_text("".join('{"n":%d}\n' % i for i in range(shard_lines)))
    g(r, "add", "-A")
    g(r, "commit", "-qm", "one")
    return r


def bind(r):
    """Point model at the ledger of repo r; -> the old EVENTS."""
    old = model.EVENTS
    model.EVENTS = str(Path(r) / "infrastructure" / "state" / "ledger" / "events.jsonl")
    return old


def ev(seat="BENCH"):
    return {"event": "note", "id": "SELFTEST_SPARSE_SHARD_ITEM", "seat": seat, "text": "t", "why": "selftest"}


def attempt(seat="BENCH"):
    """-> (raised exception or None)."""
    try:
        model.append(ev(seat))
        return None
    except Exception as e:  # noqa: BLE001 - the case reads what was raised
        return e


def t_implicit_append_preserves_tracked_history():
    with tempfile.TemporaryDirectory() as d:
        r = make_repo(d)
        g(r, "sparse-checkout", "set", "src")
        shard = r / "infrastructure" / "state" / "ledger" / "events" / "BENCH.jsonl"
        old = bind(r)
        try:
            e = attempt()
        finally:
            model.EVENTS = old
        check("A1 sparse cone without the ledger: append raises", e is not None, "no exception")
        check("A1 the refusal names the checkout", e is not None and str(r) in str(e), e)
        check("A1 no shard file was created", not shard.exists(), shard.exists() and shard.read_text())
        st = g(r, "status", "--short")
        check("A1 git status stays clean", st == "", st)

    with tempfile.TemporaryDirectory() as d:
        r = make_repo(d)
        shard = r / "infrastructure" / "state" / "ledger" / "events" / "BENCH.jsonl"
        shard.unlink()
        old = bind(r)
        try:
            e = attempt()
        finally:
            model.EVENTS = old
        check("A2 a tracked shard deleted from disk: append raises", e is not None, "no exception")
        check("A2 no 1-line shard was created", not shard.exists(), shard.exists() and shard.read_text())

    with tempfile.TemporaryDirectory() as d:
        r = make_repo(d)
        shard = r / "infrastructure" / "state" / "ledger" / "events" / "BENCH.jsonl"
        old = bind(r)
        try:
            e = attempt()
        finally:
            model.EVENTS = old
        n = len(shard.read_text().splitlines())
        check("A3 a tracked shard on disk: append writes one more line", e is None and n == 4, (e, n))

    with tempfile.TemporaryDirectory() as d:
        r = make_repo(d)
        new = r / "infrastructure" / "state" / "ledger" / "events" / "OWNER.jsonl"
        old = bind(r)
        try:
            e = attempt("OWNER")
        finally:
            model.EVENTS = old
        check("A4 an untracked new seat shard is created", e is None and new.exists(), (e, new.exists()))

    with tempfile.TemporaryDirectory() as d:
        led = Path(d) / "ledger"
        led.mkdir()
        old = model.EVENTS
        model.EVENTS = str(led / "events.jsonl")
        try:
            e = attempt()
        finally:
            model.EVENTS = old
        check("A5 a ledger outside any git repo: the shard is created", e is None and (led / "events" / "BENCH.jsonl").exists(), e)


def t_deploy_recovers_abandoned_index_lock():
    import deploy_update as du
    with tempfile.TemporaryDirectory() as d:
        origin, deploy = Path(d) / "origin", Path(d) / "deploy"
        origin.mkdir()
        g(origin, "init", "-q", "-b", "main")
        g(origin, "config", "user.email", "t@t")
        g(origin, "config", "user.name", "t")
        (origin / "f").write_text("1")
        g(origin, "add", "f")
        g(origin, "commit", "-qm", "one")
        subprocess.run(["git", "clone", "-q", str(origin), str(deploy)], check=True)
        du.update_code(deploy)                                   # a good pass first, so the stamp exists
        lock = deploy / ".git" / "index.lock"
        old_t = time.time() - 10 * du.UPDATE_BUDGET_S

        def advance(n):
            (origin / "f").write_text(str(n))
            g(origin, "commit", "-qam", str(n))

        advance(2)
        lock.write_text("")
        os.utime(lock, (old_t, old_t))
        try:
            u = du.update_code(deploy)
            err = None
        except Exception as e:  # noqa: BLE001
            u, err = None, e
        check("B1 a stale unheld index.lock is cleared and the pull lands",
              err is None and u and u.get("changed") is True and not lock.exists(), (err, u, lock.exists()))
        cleared = u.get("cleared_lock") if u else None
        check("B1 the result reports the cleared lock's age", isinstance(cleared, (int, float))
              and cleared > du.UPDATE_BUDGET_S, cleared)

        lock.unlink(missing_ok=True)
        advance(3)
        lock.write_text("")                                      # fresh: a live git may own it
        try:
            du.update_code(deploy)
            raised = False
        except Exception:  # noqa: BLE001
            raised = True
        check("B2 a fresh index.lock is left and the pass fails loud", raised and lock.exists(), (raised, lock.exists()))

        os.utime(lock, (old_t, old_t))
        fh = open(lock, "rb")                                   # this process holds it open
        try:
            try:
                du.update_code(deploy)
                raised = False
            except Exception:  # noqa: BLE001
                raised = True
            check("B3 an old index.lock that a process holds is left and the pass fails loud",
                  raised and lock.exists(), (raised, lock.exists()))
        finally:
            fh.close()


def main():
    os.environ.setdefault("RIMFLOW_TEST_PROCESS", "1")
    t_implicit_append_preserves_tracked_history()
    t_deploy_recovers_abandoned_index_lock()
    print("RESULT %s (%d fail)" % ("FAIL" if FAILS else "PASS", len(FAILS)))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
