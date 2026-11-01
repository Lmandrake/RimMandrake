#!/usr/bin/env python3
"""selftest_scratch_reap_paths.py — path_forms is the one place scratch_reap reads path shapes out of an argv word or an
environment value. Every shape Codex rounds r10-r18 found is a row here, so the next one is a row and not a branch.
Pure: no /proc, no files beyond one temp dir."""
import os
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import scratch_reap as R  # noqa: E402

CWD = "/home/mandrake/rm/bench"
# (word, a path that must be named once normalised)
SHAPES = [
    ("/home/mandrake/rm/scratch/c", "/home/mandrake/rm/scratch/c"),               # plain
    ("../scratch/c", "/home/mandrake/rm/scratch/c"),                                # relative to cwd
    ("scratch/c/task.py", "/home/mandrake/rm/bench/scratch/c/task.py"),            # bare relative
    ("--repo=/home/mandrake/rm/scratch/c", "/home/mandrake/rm/scratch/c"),         # flag=abs
    ("--repo=../scratch/c", "/home/mandrake/rm/scratch/c"),                         # flag=rel
    ("-I../scratch/c/include", "/home/mandrake/rm/scratch/c/include"),             # attached short flag, rel (r18)
    ("-I/home/mandrake/rm/scratch/c/include", "/home/mandrake/rm/scratch/c/include"),
    ("-isystem/home/mandrake/rm/scratch/c/x", "/home/mandrake/rm/scratch/c/x"),    # long attached flag
    ("-isystem../scratch/c/x", "/home/mandrake/rm/scratch/c/x"),
    ("/a/b:/home/mandrake/rm/scratch/c", "/home/mandrake/rm/scratch/c"),           # PATH-like
    ("a:../scratch/c", "/home/mandrake/rm/scratch/c"),
    ("-O2 -I../scratch/c/i", "/home/mandrake/rm/scratch/c/i"),                      # blank-separated flags
    ("K=../scratch/c", "/home/mandrake/rm/scratch/c"),                              # make-style K=v
    ("/home/mandrake/rm/bench/../scratch/c", "/home/mandrake/rm/scratch/c"),        # `..` inside an absolute one
    ("-isystemscratch/c/x", "/home/mandrake/rm/bench/scratch/c/x"),               # undotted, glued to a long flag
    ('CC="-I../scratch/c/i"', "/home/mandrake/rm/scratch/c/i"),                   # quoted, shell punctuation
    ("(../scratch/c);", "/home/mandrake/rm/scratch/c"),
    ('git -C "$HOME/rm/scratch/c" status', "/home/mandrake/rm/scratch/c"),
    ("cd ../scratch/c&&exec ./run", "/home/mandrake/rm/scratch/c"),
    ("~/rm/scratch/c", "/home/mandrake/rm/scratch/c"),
    ("@scratch/c/build.rsp", "/home/mandrake/rm/bench/scratch/c/build.rsp"),      # response file
    ("-I=../scratch/c", "/home/mandrake/rm/scratch/c"),
]


def main() -> int:
    bad = []
    for word, want in SHAPES:
        got = {os.path.normpath(p) for p in R.path_forms(word, CWD)}
        if want not in got:
            bad.append(f"{word!r}: wanted {want}, got {sorted(got)}")
    with tempfile.TemporaryDirectory() as td:
        os.mkdir(os.path.join(td, "worker"))
        if os.path.join(td, "worker") not in R.path_forms("worker", td, True):
            bad.append("an environment bare word that exists is not named")
        if R.path_forms("nothere", td, True):
            bad.append("an environment bare word that is not there is named")
        if os.path.join(td, "nothere") not in R.path_forms("nothere", td, False):
            bad.append("an argv bare word is not named")
    if "/home/a b/c" not in {os.path.normpath(x) for x in R.path_forms("/home/a b/c", CWD)}:
        bad.append("a path holding a blank is not named whole")
    # users(): sibling names that sort between a dir and its children must not hide a user (r1 of the full-file review)
    live = object.__new__(R.Live)
    live.paths = sorted([("/x/clone-old", "1"), ("/x/clone.bak", "2"), ("/x/clone/inner/f", "3")])
    live.keys = [k for k, _ in live.paths]
    live.cmdblob, live.sessions, live.fresh = "", set(), {}
    if not any("pid 3" in u for u in live.users(Path("/x/clone"))):
        bad.append("a process inside the dir is hidden by siblings that sort before its children")
    bo = object.__new__(R.Borrows)
    bo.pairs = sorted([("/x/clone-old", "/h1"), ("/x/clone/objects", "/h2")])
    bo.keys = [k for k, _ in bo.pairs]
    if not R.Borrows.of(bo, Path("/x/clone")):
        bad.append("a borrower of the dir is hidden by a sibling name that sorts before its children")
    for empty in ("", ":", " "):
        if R.path_forms(empty, CWD):
            bad.append(f"{empty!r} names something")
    for bare in ("~", "$HOME", "${HOME}", "HOME=~"):          # naming HOME itself would walk every home dir as a lender
        if str(R.HOME) in R.path_forms(bare, CWD):
            bad.append(f"{bare!r} names the home dir itself")
    for b in bad:
        print("FAIL:", b)
    print("FAIL" if bad else "ok: scratch_reap path_forms", len(SHAPES), "shapes")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
