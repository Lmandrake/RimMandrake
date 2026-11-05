#!/usr/bin/env python3
"""selftest_scratch_reap_objformat.py — scratch_reap's git() lends the mirrors' objects (GIT_ALTERNATE_OBJECT_DIRECTORIES)
only to a repo of the same object format. Lending sha1 packs to a sha256 repo made every read of it log
"error: wrong index v2 file size" and refuse it as "cannot list commits" (MIRROR_PACK_REPAIR_STILL_GRUMBLING, 2026-11-04:
197 lines a day in the rm-scratch-reap journal, blamed on a mirror whose packs were sound). A sha1 repo still borrows."""
import os
import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import scratch_reap as R  # noqa: E402


def sh(cwd, *a, env=None):
    subprocess.run(["git", *a], cwd=cwd, check=True, capture_output=True, env=env)


def main() -> int:
    bad = []
    with tempfile.TemporaryDirectory() as td:
        t = Path(td)
        ident = dict(os.environ, GIT_AUTHOR_NAME="t", GIT_AUTHOR_EMAIL="t@t", GIT_COMMITTER_NAME="t",
                     GIT_COMMITTER_EMAIL="t@t")
        src = t / "src"
        src.mkdir()
        sh(src, "init", "-q", "-b", "main")
        (src / "f").write_text("x\n")
        sh(src, "add", "f")
        sh(src, "commit", "-qm", "one", env=ident)
        tip = subprocess.run(["git", "rev-parse", "HEAD"], cwd=src, capture_output=True, text=True).stdout.strip()
        mirror = t / "mirror.git"
        sh(t, "clone", "-q", "--mirror", str(src), str(mirror))
        sh(mirror, "repack", "-adq", "--write-bitmap-index")
        sh(mirror, "commit-graph", "write", "--reachable")
        os.environ["SCRATCH_REAP_MIRRORS"] = str(mirror)
        # a sha256 repo, like the wallsha256* selftest fixtures under ~/.seat-tmp
        s256 = t / "s256"
        s256.mkdir()
        sh(s256, "init", "-q", "--object-format=sha256", "-b", "main")
        (s256 / "a.py").write_text("1\n")
        sh(s256, "add", "a.py")
        sh(s256, "commit", "-qm", "root", env=ident)
        r = R.git(s256, "log", "--oneline", "--all")
        if r.returncode != 0 or "wrong index" in r.stderr or "hash version" in r.stderr:
            bad.append(f"sha256 repo read through sha1 mirror: rc={r.returncode} stderr={r.stderr.strip()[:200]!r}")
        # a sha1 repo with no objects of its own still reads the mirror's commit through the alternates
        empty = t / "s1"
        empty.mkdir()
        sh(empty, "init", "-q", "-b", "main")
        if R.git(empty, "cat-file", "-e", tip).returncode != 0:
            bad.append("a sha1 repo no longer borrows the mirror's objects")
    for b in bad:
        print("FAIL", b)
    print("selftest_scratch_reap_objformat:", "FAIL" if bad else "PASS")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
