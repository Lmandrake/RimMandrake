#!/usr/bin/env python3
"""selftest_scratch_reap_stale_handed_over.py — selftest_stale counts only the fixtures sweep_fixtures can remove
(RIMMANDRAKE_UNCLOG_SCRATCH_ARCHIVE_BACKLOG_29_KB_CLONES_EACH, spec point 2). Measured 2026-11-16: of 1222 fixtures past
the TTL, 1201 were mkdtemp dirs holding a git repo, which sweep_fixtures hands to the clone judgment (keeps_work); on
2026-11-18 18:03 PST the end reading was 274 over its line of 200. Those dirs are already clone rows (ARCHIVE, YOUNG,
REFUSE), so counting them here too held the scratch:sanity alarm open on work the fixture sweep may not touch.

Proves: an aged tmpXXXXXXXX dir holding a git repo is not a stale fixture; an aged selftest_ dir is, with or without a
repo inside (the runner's own prefix under ~/.seat-tmp is a fixture by name); an aged plain tmpXXXXXXXX dir is; and
sweep_fixtures holds exactly the dirs the count leaves out. Pure: a temp root named .seat-tmp, `git init`."""
import os
import subprocess
import sys
import tempfile
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path[:0] = [str(HERE), str(HERE.parent / "rimflow")]
import scratch_reap as R  # noqa: E402

FAILS = []


def check(ok, what):
    print(("PASS " if ok else "FAIL ") + what)
    if not ok:
        FAILS.append(what)


with tempfile.TemporaryDirectory(prefix="selftest_stale_handed_") as td:
    seat = Path(td) / ".seat-tmp" / "BENCH"
    seat.mkdir(parents=True)
    repo_tmp = seat / "tmpab12cd34"                  # a mkdtemp name holding a git repo: the clone judgment's
    plain_tmp = seat / "tmpzz99yy88"                 # a mkdtemp name holding no repo: a fixture
    named = seat / "selftest_named_x1"               # the runner's prefix, a repo inside: a fixture by name
    for d in (repo_tmp, plain_tmp, named):
        d.mkdir()
        (d / "f.txt").write_text("x")
    for d in (repo_tmp, named):
        subprocess.run(["git", "init", "-q", str(d)], check=True)
    saved = {k: os.environ.get(k) for k in ("SCRATCH_REAP_ROOTS", "SCRATCH_REAP_STATE")}
    os.environ.update(SCRATCH_REAP_ROOTS=str(Path(td) / ".seat-tmp"), SCRATCH_REAP_STATE=str(Path(td) / "state"))
    try:
        later = time.time() + 3 * 86400              # three days on: every dir is past FIXTURE_TTL_S
        m = R.measure(later, None, {})
        check(m["selftest_stale"] == 2, "only the two fixtures the sweep may remove count as stale (%r)" % m["selftest_stale"])
        check(m["selftest_dirs"] == 2, "a dir handed to the clone judgment is not a fixture dir either (%r)"
              % m["selftest_dirs"])
        ok_now = [R.handed_over(p) for p in (repo_tmp, plain_tmp, named)] if hasattr(R, "handed_over") else None
        check(ok_now == [True, False, False], "handed_over names exactly the repo-holding mkdtemp dir (%r)" % ok_now)
        ctx = R.Ctx.__new__(R.Ctx)
        ctx.now = later
        ctx.live = type("L", (), {"blind": [], "taken": later, "users": lambda self, p: []})()
        ctx.borrows = type("B", (), {"hold": [], "of": lambda self, p: []})()
        out = R.sweep_fixtures(ctx, False, 0)
        check(out["held"] == 1, "sweep_fixtures holds the one dir the count leaves out (%r)" % out)
    finally:
        for k, v in saved.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v

print("%d failed" % len(FAILS))
sys.exit(1 if FAILS else 0)
