#!/usr/bin/env python3
"""Selftest for block_ledger_lint.py: a real malformed shard is REFUSED in git-native
pre-push mode; a clean shard passes; a lint that exits 2 or crashes (traceback, exit 1,
no summary line) fails OPEN *with* a "NOT linted" warning instead of passing silently
or refusing with an empty reason."""
import importlib.util
import io
import json
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
ZERO = bll.ZERO


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


def pre_tool(work, command):
    """Run the hook in PreToolUse mode; -> True when it denies the command."""
    payload = json.dumps({"tool_input": {"command": command}, "cwd": work})
    r = subprocess.run([sys.executable, os.path.join(HERE, "block_ledger_lint.py")],
                       input=payload, capture_output=True, text=True, env=ENV, timeout=60)
    return '"deny"' in r.stdout


def ancestor_cases(tmp, results):
    """A ref whose commit is already inside origin/main publishes no ledger line that
    origin/main lacks, so a tag on an older pass commit must pass; a push that drops a
    line from main, or a new commit that drops one, must still be refused."""
    bare = os.path.join(tmp, "origin.git")
    git(tmp, "init", "-q", "--bare", "-b", "main", bare)
    work = os.path.join(tmp, "a")
    os.makedirs(work)
    git(work, "init", "-q", "-b", "main")
    git(work, "remote", "add", "origin", bare)
    write(work, LINT, open(os.path.join(REPO, LINT)).read())
    a = '{"seat":"T","event":"note","id":"A","ts":"1"}\n'
    b = '{"seat":"T","event":"note","id":"B","ts":"2"}\n'
    write(work, SHARD, a)
    old = commit(work, "old pass commit")
    write(work, SHARD, a + b)
    commit(work, "later append")
    git(work, "push", "-q", "origin", "main")
    git(work, "tag", "-a", "-m", "pass", "mod/X/v0.1.0", old)
    tag_obj = git(work, "rev-parse", "mod/X/v0.1.0")
    results.append(("PreToolUse: annotated tag on an ancestor of origin/main is ALLOWED",
                    not pre_tool(work, "git push origin mod/X/v0.1.0")))
    results.append(("PreToolUse: refs/tags/ spelling of the same tag is ALLOWED",
                    not pre_tool(work, "git push origin refs/tags/mod/X/v0.1.0")))
    rc, err = pre_push_line(work, "refs/tags/mod/X/v0.1.0 %s refs/tags/mod/X/v0.1.0 %s"
                            % (tag_obj, ZERO))
    results.append(("git-native: new tag on an ancestor of origin/main is ALLOWED",
                    rc == 0 and "REFUSED" not in err))
    # planted faults: each must stay refused
    results.append(("PreToolUse: forced rewind of main to the ancestor is REFUSED",
                    pre_tool(work, "git push --force origin %s:main" % old)))
    results.append(("PreToolUse: same rewind spelled refs/heads/main is REFUSED",
                    pre_tool(work, "git push -f origin %s:refs/heads/main" % old)))
    rc, err = pre_push_line(work, "refs/heads/main %s refs/heads/main %s"
                            % (old, git(work, "rev-parse", "origin/main")))
    results.append(("git-native: rewind of main to the ancestor is REFUSED",
                    rc == 1 and "NOT_APPEND" in err))
    write(work, SHARD, b)                       # a NEW commit that drops line A
    drop = commit(work, "drops a line")
    git(work, "branch", "feat", drop)
    results.append(("PreToolUse: branch push of a commit that drops a line is REFUSED",
                    pre_tool(work, "git push origin feat")))
    git(work, "tag", "-a", "-m", "bad", "mod/X/v0.2.0", drop)
    results.append(("PreToolUse: tag on a non-ancestor commit that drops a line is REFUSED",
                    pre_tool(work, "git push origin mod/X/v0.2.0")))
    rc, err = pre_push_line(work, "refs/heads/feat %s refs/heads/feat %s" % (drop, ZERO))
    results.append(("git-native: new branch that drops a line is REFUSED",
                    rc == 1 and "NOT_APPEND" in err))


def pre_push_line(work, line):
    err = io.StringIO()
    with redirect_stderr(err):
        rc = bll.git_pre_push([line], work)
    return rc, err.getvalue()


def main():
    tmp = tempfile.mkdtemp(prefix="bll_selftest_")
    results = []
    try:
        ancestor_cases(tmp, results)
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
    return 1 if fails or len(results) != 13 else 0


if __name__ == "__main__":
    sys.exit(main())
