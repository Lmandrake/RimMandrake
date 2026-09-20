#!/usr/bin/env python3
"""Selftest for warn_close_live_proof_owed.py (CLOSE_OWED_LIVE_PROOF_1).

End-to-end against a real throwaway git repo, same contract as
selftest_warn_unclosed_queue_item.py: the hook shells out to `git show` and
reads a real ledger file, so a test that stubbed either out would miss
exactly the kind of regression this hook exists to catch.

    python3 .claude/hooks/selftest_warn_close_live_proof_owed.py
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile

HOOK = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                    "warn_close_live_proof_owed.py")
LEDGER_REL = os.path.join("infrastructure", "state", "ledger", "events.jsonl")


def git(root, *a):
    subprocess.run(["git", "-C", root, *a], capture_output=True, text=True,
                   check=True)


def run(root, cmd):
    ev = json.dumps({"tool_input": {"command": cmd}})
    env = dict(os.environ, CLAUDE_PROJECT_DIR=root)
    p = subprocess.run([sys.executable, HOOK], input=ev, capture_output=True,
                       text=True, env=env, cwd=root, timeout=20)
    return p.returncode, p.stderr


def append_ledger(root, ev):
    with open(os.path.join(root, LEDGER_REL), "a", encoding="utf-8") as fh:
        fh.write(json.dumps(ev) + "\n")


def make_repo():
    root = tempfile.mkdtemp(prefix="selftest_wclpo_")
    os.makedirs(os.path.join(root, os.path.dirname(LEDGER_REL)), exist_ok=True)
    git(root, "init", "-q")
    git(root, "config", "user.email", "t@t")
    git(root, "config", "user.name", "t")
    open(os.path.join(root, LEDGER_REL), "w").close()
    open(os.path.join(root, "README.md"), "w").write("base\n")
    git(root, "add", "README.md", LEDGER_REL)
    git(root, "commit", "-q", "README.md", LEDGER_REL, "-m", "base")
    return root


def commit(root, name, msg):
    p = os.path.join(root, name)
    open(p, "w").write("x\n")
    git(root, "add", name)
    git(root, "commit", "-q", name, "-m", msg)
    return subprocess.run(["git", "-C", root, "rev-parse", "--short", "HEAD"],
                          capture_output=True, text=True).stdout.strip()


def main():
    fails = 0
    cases = []

    # Case 1: offline-only close, phrase present, no spawn — must WARN.
    root = make_repo()
    sha = commit(root, "a.txt",
                "Close FAKE_ITEM_1: builds clean\n\n"
                "dotnet build 0/0. Deploy + live proof owed (next game-down).\n")
    cmd = ("python3 src/RimMandrake/rimflow/cli.py close FAKE_ITEM_1 --sha %s"
          % sha)
    cases.append(("offline-only close, no successor — must warn",
                  root, cmd, 1, "FAKE_ITEM_1"))

    # Case 2: same shape, but a spawn already names it as `from` — must be quiet.
    root = make_repo()
    sha = commit(root, "a.txt",
                "Close FAKE_ITEM_1: builds clean\n\n"
                "dotnet build 0/0. Deploy + live proof owed (next game-down).\n")
    append_ledger(root, {"seat": "FOUNDRY", "event": "spawn",
                         "name": "FAKE_SUCCESSOR_1", "kind": "task",
                         "for": "FOUNDRY", "from": "FAKE_ITEM_1"})
    cmd = ("python3 src/RimMandrake/rimflow/cli.py close FAKE_ITEM_1 --sha %s"
          % sha)
    cases.append(("offline-only close WITH successor — must be quiet",
                  root, cmd, 0, None))

    # Case 2b: successor spawned from a RUN under the item (ID/run-N@env) —
    # still counts.
    root = make_repo()
    sha = commit(root, "a.txt",
                "Close FAKE_ITEM_1: builds clean\n\n"
                "dotnet build 0/0. Live proof still owed.\n")
    append_ledger(root, {"seat": "FOUNDRY", "event": "spawn",
                         "name": "FAKE_SUCCESSOR_1", "kind": "task",
                         "for": "FOUNDRY", "from": "FAKE_ITEM_1/run-2@offline"})
    cmd = ("python3 src/RimMandrake/rimflow/cli.py close FAKE_ITEM_1 --sha %s"
          % sha)
    cases.append(("successor spawned from a run under the item — must be quiet",
                  root, cmd, 0, None))

    # Case 3: close commit names no debt at all — must be quiet.
    root = make_repo()
    sha = commit(root, "a.txt", "Close CLEAN_ITEM_1: fully done, nothing owed\n")
    cmd = ("python3 src/RimMandrake/rimflow/cli.py close CLEAN_ITEM_1 --sha %s"
          % sha)
    cases.append(("clean close, no debt phrase — must be quiet",
                  root, cmd, 0, None))

    # Case 4: --sha omitted — falls back to HEAD, same as cmd_close's own default.
    root = make_repo()
    commit(root, "a.txt",
          "Close FAKE_ITEM_1: builds clean\n\nfollow-on work: deploy + live proof.\n")
    cmd = "python3 src/RimMandrake/rimflow/cli.py close FAKE_ITEM_1"
    cases.append(("no --sha, defaults to HEAD — still warns",
                  root, cmd, 1, "FAKE_ITEM_1"))

    # Case 5: not a `close` command at all — must be quiet.
    root = make_repo()
    cases.append(("unrelated command — not our business",
                  root, "git status --porcelain", 0, None))

    # Case 6: a `rimflow spawn` command itself, not a close — must be quiet
    # even though the word "close" never appears.
    root = make_repo()
    cases.append(("a spawn command, not a close — not our business",
                  root, "python3 src/RimMandrake/rimflow/cli.py spawn --from X "
                        "--for FOUNDRY --name Y", 0, None))

    try:
        for name, root, cmd, want, needle in cases:
            try:
                code, err = run(root, cmd)
            finally:
                shutil.rmtree(root, ignore_errors=True)
            ok = (code == want) and (not needle or needle in err)
            if code == 2:
                ok = False
                err += "\n  !! exit 2 GATES the close — forbidden (WARN, not refuse)"
            print("%-4s %s" % ("ok" if ok else "FAIL", name))
            if not ok:
                fails += 1
                print("       exit=%s want=%s stderr=%r" % (code, want, err[:400]))
    finally:
        pass
    print("\n%d/%d passed" % (len(cases) - fails, len(cases)))
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
