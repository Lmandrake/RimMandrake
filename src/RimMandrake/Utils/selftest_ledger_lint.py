#!/usr/bin/env python3
"""Selftest for ledger_lint.py — every refusal refuses, the clean cases pass, and the
REAL ledger (worktree vs origin/main) is clean. This file is how run_selftests.py runs
the lint on every sweep (git plan §2.5 invariant 2)."""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ledger_lint as L                                          # noqa: E402

FAIL = []


def j(**kw):
    return json.dumps(kw, separators=(",", ":"))


A = j(seat="BENCH", event="note", id="X_Y_Z_1", text="a", ts="2026-10-02T00:00:00Z")
B = j(seat="BENCH", event="note", id="X_Y_Z_1", text="b", ts="2026-10-02T00:00:01Z")
A_EDIT = j(seat="BENCH", event="note", id="X_Y_Z_1", text="EDITED", ts="2026-10-02T00:00:00Z")
A2 = j(seat="BENCH", event="note", id="X_Y_Z_1", text="other", ts="2026-10-02T00:00:09Z")
A3 = j(seat="BENCH", event="note", id="X_Y_Z_1", text="other2", ts="2026-10-02T00:00:09Z")


def codes(data, base=None):
    return sorted({c for c, *_ in L.lint_blob("s.jsonl", data.encode(), base and base.encode())})


def check(name, got, want):
    ok = got == want
    print(("ok    " if ok else "FAIL  ") + name + ("" if ok else "  got %s want %s" % (got, want)))
    if not ok:
        FAIL.append(name)


check("clean append", codes(A + "\n" + B + "\n", A + "\n"), [])
check("identical duplicate is fine (union artifact)", codes(A + "\n" + A + "\n", A + "\n"), [])
check("malformed line", codes(A + "\n{\"seat\":\n", A + "\n"), ["MALFORMED"])
check("non-object line", codes(A + "\n[1]\n"), ["MALFORMED"])
check("missing trailing newline", codes(A + "\n" + B, A + "\n"), ["NO_NEWLINE"])
check("removed line", codes(B + "\n", A + "\n" + B + "\n"), ["NOT_APPEND"])
check("edit in place", codes(A_EDIT + "\n" + B + "\n", A + "\n" + B + "\n"),
      ["DUP_DIFFERENT", "NOT_APPEND"])
check("union of an edit: original kept + altered twin", codes(A + "\n" + A_EDIT + "\n", A + "\n"),
      ["DUP_DIFFERENT"])
check("two new same-second distinct events are legitimate", codes(A + "\n" + A2 + "\n" + A3 + "\n", A + "\n"), [])
check("empty shard", codes(""), [])
check("a shard truncated to empty loses its base lines", codes("", A + "\n" + B + "\n"), ["NOT_APPEND"])
check("a shard gone at rev (None) loses its base lines",
      sorted({c for c, *_ in L.lint_blob("s.jsonl", None, (A + "\n").encode())}), ["NOT_APPEND"])


def _scratch_repo():
    """A throwaway git repo: base commit with a shard, a second commit that DELETES it."""
    import subprocess
    import tempfile
    root = tempfile.mkdtemp(prefix="ledger_lint_self_")
    g = lambda *a: subprocess.run(["git", "-C", root, *a], capture_output=True, check=True)  # noqa: E731
    g("init", "-q")
    g("config", "user.email", "selftest@example.invalid")
    g("config", "user.name", "selftest")
    os.makedirs(os.path.join(root, L.SHARD_DIR))
    shard = L.SHARD_DIR + "/X.jsonl"
    with open(os.path.join(root, shard), "w") as fh:
        fh.write(A + "\n")
    g("add", shard)
    g("commit", "-q", "-m", "base")
    g("tag", "base")
    g("rm", "-q", shard)
    g("commit", "-q", "-m", "delete the shard")
    return root


_root = _scratch_repo()
try:
    got = sorted({f[0] for f in L.lint(_root, "HEAD", "base")[0]})
    check("a shard DELETED at rev is NOT_APPEND (it was never listed, so it passed)", got, ["NOT_APPEND"])
    check("the worktree with the shard deleted is NOT_APPEND too",
          sorted({f[0] for f in L.lint(_root, None, "base")[0]}), ["NOT_APPEND"])
    try:
        L.lint(_root, "no_such_rev", "base")
        check("an unknown --rev cannot run (it listed no shards and read clean)", "ran", "raised")
    except RuntimeError:
        check("an unknown --rev cannot run (it listed no shards and read clean)", "raised", "raised")
    check("CLI: an unknown --rev exits 2, not 0", L.main(["--root", _root, "--rev", "no_such_rev", "--base", "base"]), 2)
finally:
    import shutil
    shutil.rmtree(_root, ignore_errors=True)

findings, notes = L.lint()
for n in notes:
    print("note: " + n)
real = ["%s %s:%s %s" % f for f in findings]
check("real ledger is clean (worktree vs origin/main)", real, [])
print("\n%s" % ("FAILED: " + ", ".join(FAIL) if FAIL else "all passed"))
sys.exit(1 if FAIL else 0)
