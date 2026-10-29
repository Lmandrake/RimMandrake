#!/usr/bin/env python3
"""selftest_runner_guard.py - pre-commit refuses an AI-session commit in a clone named 'runner' and allows the rest."""
import os, subprocess, sys, tempfile

HOOK = os.path.join(os.path.dirname(os.path.abspath(__file__)), "pre-commit")
BASE = {k: v for k, v in os.environ.items() if k not in ("CLAUDECODE", "AI_AGENT", "CLAUDE_CODE_SESSION_ID", "RUNNER_AI_COMMIT_OK")}
FAILS = []


def run(name, env_extra):
    d = tempfile.mkdtemp()
    repo = os.path.join(d, name)
    os.makedirs(repo)
    subprocess.run(["git", "init", "-q", repo], check=True)
    return subprocess.run(["sh", HOOK], cwd=repo, env={**BASE, **env_extra}, capture_output=True, text=True).returncode


def check(label, got, want):
    print(("ok   " if got == want else "FAIL ") + label)
    if got != want:
        FAILS.append(label)


check("AI session in runner clone is refused", run("runner", {"CLAUDECODE": "1"}), 1)
check("AI_AGENT alone is refused", run("runner", {"AI_AGENT": "x"}), 1)
check("runner's own non-AI commit allowed", run("runner", {}), 0)
check("explicit override allowed", run("runner", {"CLAUDECODE": "1", "RUNNER_AI_COMMIT_OK": "1"}), 0)
check("AI session in a seat clone allowed", run("foundry", {"CLAUDECODE": "1"}), 0)
sys.exit(1 if FAILS else 0)
