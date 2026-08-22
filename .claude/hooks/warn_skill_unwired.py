#!/usr/bin/env python3
"""PreToolUse hook — a skill this project cannot SEE is a skill nobody will use.

WHY
===
`skills/<name>/SKILL.md` is where a skill is authored, and it is NOT where Claude Code
looks. Discovery is `.claude/skills/<name>`, a symlink back into `skills/`. Nothing
creates that symlink, nothing checks it, and a skill without one is invisible to every
seat in every session — it loads for no one, triggers on nothing, and the only symptom
is that the work it encodes silently never happens.

Measured 2026-08-22: all 26 skills were wired, by hand, by whoever remembered. That is
one forgotten `ln -s` away from an invisible skill, and the failure is undetectable from
inside a session — the skill simply never appears.

WARN, NOT GATE
==============
Exit 1, never 2. Authoring the skill is the work; wiring is one command, and refusing
the write would cost more than the defect. Same contract as `warn_doc_budget.py` and
`warn_unclosed_queue_item.py`: red on stderr, then the command runs anyway.

Stdlib only, fail-open in code — a hook that crashes must never cost a write.

    python3 .claude/hooks/selftest_warn_skill_unwired.py
"""
import json
import os
import re
import sys

ROOT = os.environ.get("CLAUDE_PROJECT_DIR") or os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SKILL_RE = re.compile(r"skills/([\w.-]+)/SKILL\.md$")
# ⚠️ The same pattern WITHOUT the `$`. A commit names the path mid-string, so the
# anchored form matched nothing there and the commit case silently never fired —
# caught by the selftest, which is the only reason this comment exists.
SKILL_IN_CMD_RE = re.compile(r"skills/([\w.-]+)/SKILL\.md")


def unwired(name):
    """True if `skills/<name>` exists but nothing in .claude/skills reaches it."""
    link = os.path.join(ROOT, ".claude", "skills", name)
    # `os.path.exists` follows the link, so a DANGLING symlink reports missing too —
    # which is right: a broken link is exactly as invisible as no link.
    return not os.path.exists(os.path.join(link, "SKILL.md"))


def report(names):
    print("⚠ skill not wired into this project — it is INVISIBLE to every seat:",
          file=sys.stderr)
    for n in names:
        print("    skills/%s/SKILL.md  has no working .claude/skills/%s" % (n, n),
              file=sys.stderr)
    print("  Claude Code discovers skills through .claude/skills/, never through "
          "skills/.", file=sys.stderr)
    print("  \U0001f511 Fix it now — one command, and the skill is live next session:",
          file=sys.stderr)
    for n in names:
        print("      ln -s ../../skills/%s %s/.claude/skills/%s" % (n, ROOT, n),
              file=sys.stderr)
    print("  ⚠️  Nothing else will tell you. An unwired skill has no symptom "
          "— it simply", file=sys.stderr)
    print("     never loads, for anyone, and the work it encodes quietly does not "
          "happen.", file=sys.stderr)
    return 1


def main():
    try:
        ev = json.load(sys.stdin)
    except Exception:
        return 0
    ti = ev.get("tool_input") or {}
    tool = ev.get("tool_name") or ""
    names = []
    if tool in ("Write", "Edit", "MultiEdit"):
        m = SKILL_RE.search((ti.get("file_path") or "").replace("\\", "/"))
        if m:
            names = [m.group(1)]
    else:
        cmd = ti.get("command") or ""
        if "git" in cmd and "commit" in cmd:
            names = sorted(set(SKILL_IN_CMD_RE.findall(cmd)))
    names = [n for n in names if unwired(n)]
    return report(names) if names else 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:
        sys.exit(0)                                  # never cost a write
