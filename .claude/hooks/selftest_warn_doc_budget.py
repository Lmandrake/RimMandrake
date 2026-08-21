#!/usr/bin/env python3
"""Selftest for warn_doc_budget.py — run after ANY change to it or to BUDGETS.

Two things can go wrong quietly. It can charge a file that has no budget (design
docs and reports are unbudgeted BY DESIGN — their length is content), which
trains everyone to ignore the red. Or it can charge a queue file as actionable,
which does the same thing six times per run and is the exact failure doc_budget.py
itself was rewritten to fix on 2026-08-13.

⚠️ It matches with fnmatch, where `*` crosses `/` — unlike the glob doc_budget.py
uses. So `infrastructure/state/*.md` DOES match `.../state/queue/BUILD.md` here.
That is safe only because first-match-wins and the queue patterns sit earlier in
BUDGETS. Case 3 pins that ordering; if someone reorders the table it fails here
rather than silently re-budgeting every queue.

    python3 .claude/hooks/selftest_warn_doc_budget.py
"""
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
HOOK = os.path.join(HERE, "warn_doc_budget.py")
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "src", "RimMandrake", "Utils"))
import doc_budget                                            # noqa: E402


def run(cmd):
    ev = json.dumps({"tool_input": {"command": cmd}})
    env = dict(os.environ, CLAUDE_PROJECT_DIR=ROOT)
    p = subprocess.run([sys.executable, HOOK], input=ev, capture_output=True,
                       text=True, env=env, cwd=ROOT, timeout=30)
    return p.returncode, p.stderr


def pick(over, queue):
    """A real path from the live repo that is (over/under) budget, (queue/not)."""
    rows, _ = doc_budget.scan()
    qs = tuple(doc_budget.QUEUE_CLASSES)
    for path, n, budget, _prov in rows:
        if (n > budget) == over and path.startswith(qs) == queue:
            return path, n, budget
    return None, None, None


def main():
    fails = 0
    cases = []

    p, n, b = pick(over=True, queue=False)
    cases.append(("an over-budget doc is RED and names the overrun", 1,
                  "git commit %s -m x" % p, ["OVER +%d" % (n - b), p]) if p
                 else ("no over-budget non-queue doc exists — skipped", 0,
                       "git status", []))

    p, n, b = pick(over=False, queue=False)
    cases.append(("an under-budget doc is quiet", 0,
                  "git commit %s -m x" % p, []) if p
                 else ("no under-budget doc exists — skipped", 0,
                       "git status", []))

    p, n, b = pick(over=True, queue=True)
    cases.append(("an over-budget QUEUE is reported but NOT charged", 0,
                  "git commit %s -m x" % p, ["append-only"]) if p
                 else ("no over-budget queue exists — skipped", 0,
                       "git status", []))

    cases += [
        ("an UNBUDGETED design doc is silent", 0,
         "git commit design/INDEX.md -m x", []),
        ("a non-md commit is silent", 0,
         "git commit src/RimMandrake/Utils/doc_budget.py -m x", []),
        ("not a commit at all", 0, "git status --porcelain", []),
    ]

    for name, want, cmd, needles in cases:
        code, err = run(cmd)
        ok = code == want and all(x in err for x in needles)
        if code == 2:
            ok = False
            err += "\n  !! exit 2 GATES the commit — forbidden, this warns only"
        print("%-4s %s" % ("ok" if ok else "FAIL", name))
        if not ok:
            fails += 1
            print("       exit=%s want=%s stderr=%r" % (code, want, err[:400]))
    print("\n%d/%d passed" % (len(cases) - fails, len(cases)))
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
