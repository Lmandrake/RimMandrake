#!/usr/bin/env python3
"""selftest_orphan_bundles.py — the orphan-bundle judge deletes only what origin holds, and says UNLANDED otherwise.

RIMMANDRAKE_PRUNE_ORPHAN_BUNDLES_FULLY_LANDED. Fixture: an origin with a.txt (edited once since), an ignored *.log
rule and a ledger shard; bundles holding (1) an edit origin later took and edited again, (2) an edit origin never
held, (3) an untracked file origin holds, (4) an untracked file origin lacks, (5) only ignored files, (6) a commit whose
shard lines origin holds under other context.
"""
import io
import os
import subprocess
import sys
import tarfile
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import orphan_bundles as OB  # noqa: E402

FAILS = []


def check(cond, msg):
    print(("ok   " if cond else "FAIL ") + msg)
    if not cond:
        FAILS.append(msg)


def git(cwd, *a):
    return subprocess.run(["git", "-C", cwd] + list(a), check=True, capture_output=True, text=True).stdout


def write(root, rel, text):
    p = os.path.join(root, rel)
    os.makedirs(os.path.dirname(p) or root, exist_ok=True)
    with open(p, "w") as f:
        f.write(text)


def tar(path, files):
    with tarfile.open(path, "w") as t:
        for name, text in files.items():
            data = text.encode()
            ti = tarfile.TarInfo(name)
            ti.size = len(data)
            t.addfile(ti, io.BytesIO(data))


def main():
    with tempfile.TemporaryDirectory() as td:
        o, c, store = os.path.join(td, "o.git"), os.path.join(td, "c"), os.path.join(td, "store")
        git(td, "init", "-q", "--bare", "-b", "main", o)
        git(td, "clone", "-q", o, c)
        for k, v in (("user.name", "t"), ("user.email", "t@t")):
            git(c, "config", k, v)
        write(c, ".gitignore", "*.log\n")
        write(c, "a.txt", "one\n")
        write(c, "kept.txt", "kept\n")
        write(c, "shard.jsonl", '{"e":1}\n')
        git(c, "add", "-A")
        git(c, "commit", "-q", "-m", "base")
        base = git(c, "rev-parse", "HEAD").strip()
        # a worker's edits: a.txt -> two (lands), a.txt -> never (does not)
        write(c, "a.txt", "two\n")
        landed_patch = git(c, "diff", "--binary")
        write(c, "a.txt", "never\n")
        unlanded_patch = git(c, "diff", "--binary")
        write(c, "a.txt", "two\n")
        git(c, "commit", "-q", "-am", "origin takes two")
        write(c, "a.txt", "three\n")
        git(c, "commit", "-q", "-am", "origin edits again")
        # a worker commit on the base adding a shard line; origin gets the same line after another clone's line
        git(c, "checkout", "-q", "-b", "worker", base)
        write(c, "shard.jsonl", '{"e":1}\n{"e":"mine"}\n')
        git(c, "commit", "-q", "-am", "worker line")
        git(c, "bundle", "create", "-q", os.path.join(td, "w.bundle"), "worker", "--not", base)
        git(c, "checkout", "-q", "main")
        write(c, "shard.jsonl", '{"e":1}\n{"e":"peer"}\n{"e":"mine"}\n')
        git(c, "commit", "-q", "-am", "union of shards")
        git(c, "push", "-q", "origin", "main")

        def bundle(name, **members):
            d = os.path.join(store, name)
            os.makedirs(d)
            for k, v in members.items():
                if k == "real_untracked":
                    tar(os.path.join(d, "real_untracked.tar"), v)
                elif k == "commits":
                    os.link(v, os.path.join(d, "commits.bundle"))
                else:
                    write(d, k.replace("_", ".", 1), v)
            write(d, "HEAD", base + "\n")
            return d

        bundle("1_landed_then_edited", real_patch=landed_patch)
        bundle("2_never_landed", real_patch=unlanded_patch)
        bundle("3_untracked_on_origin", real_patch="", real_untracked={"kept.txt": "kept\n"})
        bundle("4_untracked_missing", real_patch="", real_untracked={"new.txt": "mine\n"})
        bundle("5_only_ignored", real_patch="", real_untracked={"run.log": "x\n"})
        bundle("6_shard_commit", real_patch="", commits=os.path.join(td, "w.bundle"))

        OB.REPO = c
        orig = OB.Origin()
        try:
            got = {n: OB.judge(os.path.join(store, n), orig)[0] for n in sorted(os.listdir(store))}
        finally:
            orig.close()
        want = {"1_landed_then_edited": "LANDED", "2_never_landed": "UNLANDED", "3_untracked_on_origin": "LANDED",
                "4_untracked_missing": "UNLANDED", "5_only_ignored": "LANDED", "6_shard_commit": "LANDED"}
        for n, v in want.items():
            check(got.get(n) == v, "%s -> %s (want %s)" % (n, got.get(n), v))
        OB.main(["prune", "--store", store, "--apply"])
        left = sorted(os.listdir(store))
        check(left == ["2_never_landed", "4_untracked_missing"], "prune deletes only the landed bundles: %s" % left)
    if FAILS:
        print("FAIL %d" % len(FAILS))
        return 1
    print("PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
