#!/usr/bin/env python3
"""Selftest for block_ledger_lint.py: a real malformed shard is REFUSED in git-native
pre-push mode; a clean shard passes; a lint that exits 2 or crashes (traceback, exit 1,
no summary line) fails OPEN *with* a "NOT linted" warning instead of passing silently
or refusing with an empty reason."""
import importlib.util
import io
import os
import shutil
import subprocess
import sys
import tempfile
from contextlib import redirect_stderr

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
ENV = dict(os.environ, GIT_AUTHOR_NAME="t", GIT_AUTHOR_EMAIL="t@t", GIT_COMMITTER_NAME="t",
           GIT_COMMITTER_EMAIL="t@t", GIT_CONFIG_GLOBAL="/dev/null", GIT_CONFIG_SYSTEM="/dev/null")
SHARD = "infrastructure/state/ledger/events/T.jsonl"
LINT = "src/RimMandrake/Utils/ledger_lint.py"

spec = importlib.util.spec_from_file_location("bll", os.path.join(HERE, "block_ledger_lint.py"))
bll = importlib.util.module_from_spec(spec)
spec.loader.exec_module(bll)


def git(cwd, *a):
    return subprocess.run(["git", "-C", cwd] + list(a), capture_output=True, text=True,
                          env=ENV, check=True).stdout.strip()


def write(root, rel, data):
    p = os.path.join(root, rel)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "w") as f:
        f.write(data)


def commit(work, msg):
    git(work, "add", "-A")
    git(work, "commit", "-q", "-m", msg)
    return git(work, "rev-parse", "HEAD")


def pre_push(work, sha, base):
    err = io.StringIO()
    with redirect_stderr(err):
        rc = bll.git_pre_push(["refs/heads/main %s refs/heads/main %s" % (sha, base)], work)
    return rc, err.getvalue()


def main():
    tmp = tempfile.mkdtemp(prefix="bll_selftest_")
    results = []
    try:
        work = os.path.join(tmp, "w")
        os.makedirs(work)
        git(work, "init", "-q", "-b", "main")
        write(work, LINT, open(os.path.join(REPO, LINT)).read())
        write(work, SHARD, '{"seat":"T","event":"note","id":"A","ts":"1"}\n')
        base = commit(work, "base")
        write(work, SHARD, '{"seat":"T","event":"note","id":"A","ts":"1"}\n'
                           '{"seat":"T","event":"note","id":"B","ts":"2"}\n')
        good = commit(work, "append")
        rc, err = pre_push(work, good, base)
        results.append(("clean append passes silently", rc == 0 and err == ""))
        write(work, SHARD, '{"seat":"T","event":"note","id":"A","ts":"1"}\n{torn\n')
        bad = commit(work, "torn")
        rc, err = pre_push(work, bad, good)
        results.append(("torn line REFUSED with the finding",
                        rc == 1 and "REFUSED" in err and "MALFORMED" in err))
        # lint exits 2 (could not run): fail open, but loudly
        write(work, LINT, 'import sys\nprint("ledger_lint: could not run: boom")\nsys.exit(2)\n')
        rc, err = pre_push(work, bad, good)
        results.append(("exit 2 fails open WITH a warning",
                        rc == 0 and "NOT linted" in err and "boom" in err))
        # lint crashes with a traceback (exit 1, no summary line): not a refusal
        write(work, LINT, 'raise ImportError("no module named kaboom")\n')
        rc, err = pre_push(work, bad, good)
        results.append(("traceback (exit 1) fails open WITH a warning, not an empty refusal",
                        rc == 0 and "NOT linted" in err and "kaboom" in err
                        and "REFUSED" not in err))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    fails = 0
    for name, ok in results:
        fails += not ok
        print(("PASS " if ok else "FAIL ") + name)
    print("selftest_block_ledger_lint: %d/%d passed" % (len(results) - fails, len(results)))
    return 1 if fails or len(results) != 4 else 0


if __name__ == "__main__":
    sys.exit(main())
