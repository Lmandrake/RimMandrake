#!/usr/bin/env python3
"""selftest_scratch_reap_live_resolve_once.py — one /proc snapshot resolves each named path once
(RIMMANDRAKE_UNCLOG_SCRATCH_ARCHIVE_BACKLOG_29_KB_CLONES_EACH). Measured 2026-11-18 16:40 PST: Live() took 5-8 s, 5.2 s
of it in 25,542 os.path.realpath calls from _name_token, which resolved every argv word and environment value afresh in
each of ~107 processes; act() takes two snapshots per row, so a 29 KB archive cost about a minute.

Proves: the same token named by many processes is resolved once; a symlink in a token still adds the place it points
at; a `..` after a link still names the real parent. Pure: a temp root, a Live built without reading /proc."""
import os
import shutil
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import scratch_reap as s                                    # noqa: E402

FAILS = []


def ok(cond, what):
    print(("PASS " if cond else "FAIL ") + what)
    if not cond:
        FAILS.append(what)


def bare_live():
    L = object.__new__(s.Live)
    L.paths, L.named, L.resolved = [], set(), {}
    return L


root = Path(tempfile.mkdtemp(prefix="selftest_live_resolve_")).resolve()
try:
    (root / "real" / "sub").mkdir(parents=True)
    (root / "link").symlink_to(root / "real" / "sub")
    calls = []
    real_rp = s.os.path.realpath

    def counting(p, *a, **k):
        calls.append(p)
        return real_rp(p, *a, **k)
    s.os.path.realpath = counting
    try:
        L = bare_live()
        token = str(root / "link" / "f.txt")
        for pid in range(50):                       # one environment value, fifty processes
            L._name_token(token, "/", str(pid), True)
    finally:
        s.os.path.realpath = real_rp
    n = sum(1 for c in calls if str(c) == token)
    ok(n == 1, "a token fifty processes carry is resolved once (%d times)" % n)
    keys = {p for p, _ in L.paths}
    ok(str(root / "real" / "sub" / "f.txt") in keys, "the link's target is still named")
    ok(str(root / "link" / "f.txt") in keys, "the path as written is still named")
    ok(len([1 for p, pid in L.paths if p == str(root / "real" / "sub" / "f.txt")]) >= 50,
       "every process is still recorded against the target")

    L = bare_live()
    L._name_token(str(root / "link" / ".." / "x"), "/", "1", True)
    keys = {p for p, _ in L.paths}
    ok(str(root / "real" / "x") in keys, "a `..` after a link names the real parent (%s)" % sorted(keys))

    L = bare_live()
    named = str(root / "real" / "sub")
    L._name_token("--prompt=" + "x" * 8192 + f' "{named}"', str(root), "1", False)
    ok(named in L.resolved and len(L.resolved) < 32,
       f"a long prompt keeps its embedded path with a small cache ({len(L.resolved)} entries)")
finally:
    shutil.rmtree(root, ignore_errors=True)

print("%d failed" % len(FAILS))
sys.exit(1 if FAILS else 0)
