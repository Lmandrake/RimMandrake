#!/usr/bin/env python3
"""selftest_seat_sync_unindexed_shard.py — a ledger shard on disk but out of the index refuses ./sync, never crashes it.

RIMMANDRAKE_REFUSE_UNINDEXED_SHARD_NOT_CRASH_SEAT_SYNC (review of 657a2a262a, 2026-11-16): dirty_merges read the
index blob of a merge=union path with `_blob(g, staged)` even when the path had no index entry (staged None, e.g. after
`git rm --cached` of a shard that stays on disk), and ./sync and ./publish died with a TypeError traceback instead of
naming the path. Fixture: origin appends to a union shard; the clone drops the shard from its index and appends its own.
"""
import contextlib
import io
import os
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import seat_sync  # noqa: E402

SHARD = "infrastructure/state/ledger/events/BENCH.jsonl"


def git(cwd, *a):
    subprocess.run(["git", "-C", cwd] + list(a), check=True, capture_output=True, text=True)


def write(root, rel, text):
    p = os.path.join(root, rel)
    os.makedirs(os.path.dirname(p) or root, exist_ok=True)
    with open(p, "w") as f:
        f.write(text)


def main():
    with tempfile.TemporaryDirectory() as td:
        o, a, b = (os.path.join(td, n) for n in ("o.git", "a", "b"))
        git(td, "init", "-q", "--bare", "-b", "main", o)
        for c in (a, b):
            git(td, "clone", "-q", o, c)
            for k, v in (("user.name", "t"), ("user.email", "t@t")):
                git(c, "config", k, v)
        write(a, ".gitattributes", "infrastructure/state/ledger/events/*.jsonl merge=union\n")
        write(a, SHARD, '{"e":1}\n')
        git(a, "add", "-A")
        git(a, "commit", "-q", "-m", "base")
        git(a, "push", "-q", "origin", "main")
        git(b, "pull", "-q", "origin", "main")
        write(a, SHARD, '{"e":1}\n{"e":"upstream"}\n')
        git(a, "commit", "-q", "-am", "upstream append")
        git(a, "push", "-q", "origin", "main")
        git(b, "fetch", "-q", "origin")
        git(b, "rm", "-q", "--cached", SHARD)
        write(b, SHARD, '{"e":1}\n{"e":"local"}\n')
        buf = io.StringIO()
        try:
            with contextlib.redirect_stdout(buf):
                rc = seat_sync.main(["--repo", b, "--no-fetch"])
        except Exception as e:  # noqa: BLE001 - the defect: a crash instead of a refusal
            print("FAIL: ./sync crashed: %s: %s" % (type(e).__name__, e))
            return 1
    out = buf.getvalue()
    ok = rc == 1 and "REFUSED" in out and SHARD in out
    print(("PASS" if ok else "FAIL") + ": rc %s, %s" % (rc, out.strip().splitlines()[-1][:200] if out.strip() else ""))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
