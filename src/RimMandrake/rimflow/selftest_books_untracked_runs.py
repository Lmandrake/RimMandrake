#!/usr/bin/env python3
"""Class guard for books_dirty (OPS_JAM_CLASS_FIX_AGAIN_HJWN): a run started from the books clone writes a NEW untracked
report beside its script (GimmeSomeSlack validation_triplet_*, then FlowWorks rail_walk_result_*). Each one froze the
belt until someone added its prefix to BOOKS_LEFT_IN_PLACE. The class: an untracked file origin does not track cannot
stop a fast-forward, so level_books leaves any such file where it is; an untracked file at a path origin now tracks
still refuses, and a hand edit to a tracked file still refuses."""
import os
import shutil
import subprocess
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import relentless as R  # noqa: E402

FAILS = []


def ok(cond, what):
    print(("ok   " if cond else "FAIL ") + what)
    if not cond:
        FAILS.append(what)


def g(cwd, *a):
    return subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@t", *a], cwd=cwd, capture_output=True,
                          text=True, check=True).stdout


def put(root, p, text):
    os.makedirs(os.path.dirname(os.path.join(root, p)) or root, exist_ok=True)
    with open(os.path.join(root, p), "w") as f:
        f.write(text)


def read(root, p):
    with open(os.path.join(root, p)) as f:
        return f.read()


def main():
    d = tempfile.mkdtemp(prefix="rlbu-")
    origin, up, books = (os.path.join(d, n) for n in ("o.git", "up", "books"))
    g(d, "init", "-q", "--bare", "-b", "main", origin)
    g(d, "clone", "-q", origin, up)
    g(up, "checkout", "-q", "-B", "main")
    put(up, "code.py", "one\n")
    g(up, "add", "--", "code.py")
    g(up, "commit", "-qm", "one")
    g(up, "push", "-q", "origin", "main")
    g(d, "clone", "-q", origin, books)
    fx = R.Effects.__new__(R.Effects)
    fx.books, fx.store = books, R.Store(os.path.join(d, "store"))

    def advance(p, text):
        put(up, p, text)
        g(up, "add", "--", p)
        g(up, "commit", "-qm", "move " + p)
        g(up, "push", "-q", "origin", "main")
        g(books, "fetch", "-q", "origin")

    def level():
        try:
            return fx.level_books()
        except RuntimeError as e:
            return str(e)

    # the instance, verbatim path: rm-deadman reopened the item on it 2026-11-05
    inst = "src/RimMandrake/FlowWorks/northstar/rail_walk_result_20261105T021421.json"
    other = "src/RimMandrake/SomeFutureMod/northstar/whatever_run_20261201T000000.json"
    put(books, inst, "rail walk report\n")
    put(books, other, "a run no prefix list names\n")
    advance("code.py", "two\n")
    why = level()
    ok(why is None, "an untracked run report origin does not track does not stop a level: %s" % why)
    ok(read(books, "code.py") == "two\n" and g(books, "rev-list", "--count", "HEAD..origin/main").strip() == "0",
       "the clone is level")
    ok(read(books, inst) == "rail walk report\n" and read(books, other) == "a run no prefix list names\n",
       "and both reports are still there, byte for byte")

    clash = "src/RimMandrake/FlowWorks/northstar/now_tracked.json"
    put(books, clash, "local untracked\n")
    advance(clash, "origin tracks it now\n")
    why = level()
    ok(why is not None and read(books, clash) == "local untracked\n",
       "an untracked file at a path origin now tracks refuses, nothing overwritten: %s" % why)
    os.remove(os.path.join(books, clash))
    ok(level() is None, "level again once it is gone")

    put(books, "code.py", "a hand edit\n")
    advance("other.py", "x\n")
    why = level()
    ok(why and "code.py" in why and read(books, "code.py") == "a hand edit\n", "a tracked hand edit refuses as before: %s" % why)
    shutil.rmtree(d, ignore_errors=True)
    print("%d failed" % len(FAILS))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
