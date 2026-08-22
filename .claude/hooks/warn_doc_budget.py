#!/usr/bin/env python3
"""PreToolUse/Bash hook — say out loud when a commit carries an over-budget doc.

WHY
===
`src/RimMandrake/Utils/doc_budget.py` has measured documentation bloat since
2026-08-13 and nothing ran it. On 2026-08-20 the repo stood at 342 markdown
files and 86,766 lines — roughly 954k tokens if read whole, more than a context
window — with six docs over their class budget. Every one of those overruns was
added by a seat that would have stopped had anything told it. Nothing did,
because the measurement lived in a command no one had a reason to type.

So this puts the number in front of the only person who can act on it, at the
only moment they can: the commit that grows the file.

WHAT IT DOES
============
For a `git commit` naming .md paths, it charges each path against
`doc_budget.BUDGETS` — the same table the report uses, imported, never copied —
and prints ONE line per overrun: the file, its length, its budget, the overrun.
Not the 40-line report; a report nobody reads is what we already had.

WARN, NOT GATE
==============
Exit 1, never 2. In Claude Code a PreToolUse hook blocks on 2 and only on 2;
1 is a non-blocking error whose stderr is shown to the user in red and then the
command runs anyway. Length is a judgement call and sometimes the long file is
right — this is a red flag on the way past, not a veto. Same contract as
`warn_unclosed_queue_item.py`.

⚠️ Queue files are reported but never counted as actionable, matching
doc_budget.py: they are append-only and their length tracks open work, not rot.

Stdlib only, and fail-open in code rather than in the shell wrapper — a hook
that crashes must never cost a commit.

    python3 .claude/hooks/selftest_warn_doc_budget.py
"""
import json
import os
import re
import sys

ROOT = os.environ.get("CLAUDE_PROJECT_DIR") or os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
UTILS = os.path.join(ROOT, "src", "RimMandrake", "Utils")


_MSG_FLAG_RE = re.compile(r"""(?x)
    (?:^|\s) -(?:m|F|c|C|-message|-file|-reedit-message|-reuse-message)
    (?:=|\s+)
    (?: "(?:[^"\\]|\\.)*"? | '[^']*'? | \S+ )
""")
_HEREDOC_RE = re.compile(r"<<-?\s*['\"]?(\w+)['\"]?.*?^\1", re.S | re.M)
_PATH_RE = re.compile(r"[\w./-]+\.(?:md|jsonl)")


def budget_for(rel, budgets, queue_classes):
    """Budget and queue-flag for one path. First match wins, as in doc_budget."""
    import fnmatch
    for pattern, budget in budgets:
        if fnmatch.fnmatch(rel, pattern):
            return budget, rel.startswith(queue_classes)
    return None, False


def overruns(paths):
    """-> [(rel, lines, budget, is_queue)] for paths over budget. [] if unmeasurable."""
    sys.path.insert(0, UTILS)
    try:
        import doc_budget
    except Exception:
        return []                                # nothing to measure against
    budgets = getattr(doc_budget, "BUDGETS", [])
    queues = tuple(getattr(doc_budget, "QUEUE_CLASSES", ()))
    out = []
    for rel in paths:
        budget, is_q = budget_for(rel, budgets, queues)
        if budget is None:
            continue                             # unbudgeted by design: length is content
        try:
            with open(os.path.join(ROOT, rel), encoding="utf-8",
                      errors="replace") as fh:
                n = sum(1 for _ in fh)
        except OSError:
            continue
        if n > budget:
            out.append((rel, n, budget, is_q))
    return out


def main():
    try:
        ev = json.load(sys.stdin)
    except Exception:
        return 0
    cmd = (ev.get("tool_input") or {}).get("command") or ""
    if "git" not in cmd or "commit" not in cmd:
        return 0

    # ⚠️ NOT a findall over the whole command — that reads a path quoted in a COMMIT
    # MESSAGE as a file being committed, and warns about a doc this commit never
    # touched. Same bug `queue_lint` fixed in `commit_pathspec`; these are ITS regexes,
    # lifted verbatim rather than re-derived, because re-deriving them is how this
    # file got the broken version in the first place.
    stripped = _HEREDOC_RE.sub(" ", cmd)
    stripped = _MSG_FLAG_RE.sub(" ", stripped)
    stripped = re.sub(r"\"(?:[^\"\\]|\\.)*\"|'[^']*'", " ", stripped)
    paths = sorted(set(_PATH_RE.findall(stripped)))
    if not paths:
        return 0
    hits = overruns(paths)
    real = [h for h in hits if not h[3]]
    if not hits:
        return 0

    print("⚠ over documentation budget, in this commit:", file=sys.stderr)
    for rel, n, budget, is_q in hits:
        tag = "  (queue — append-only, not actionable)" if is_q else ""
        print("    %-52s %5d lines  budget %4d  OVER +%d%s"
              % (rel, n, budget, n - budget, tag), file=sys.stderr)
    if real:
        # 🔴 THIS IS A WORK ORDER, NOT A NOTICE — owner's ruling, 2026-08-22:
        # *"we shouldn't just ignore a new (wiser) file just because it got long, it
        # should be fixed in place, AT THAT TIME, not just marked stale. No more
        # deferred work."* The old text ended with "full report: <command>", which is a
        # thing to run later — and later never came: every file in this repo's agent
        # class was over budget on the day this was rewritten.
        over = sum(n - b for _, n, b, q in hits if not q)
        print("", file=sys.stderr)
        print("  🔴 FIX IT IN THIS COMMIT. %d line%s over, and you are the seat that "
              "grew it." % (over, "" if over == 1 else "s"), file=sys.stderr)
        print("     Cut, in this order — the RULE stays, the story of how it was "
              "learned goes:", file=sys.stderr)
        print("       1. provenance — \"this used to say\", \"measured 2026-..\", "
              "\"that cost N hours\"", file=sys.stderr)
        print("       2. anything the file itself later contradicts", file=sys.stderr)
        print("       3. text that only restates another doc — leave a one-line "
              "pointer", file=sys.stderr)
        print("     ⛔ Never cut a rule, a full path, or a paste-able command.",
              file=sys.stderr)
        print("     Git history keeps everything you delete. The doc is for what is "
              "TRUE now.", file=sys.stderr)
        print("     python3 src/RimMandrake/Utils/doc_budget.py   # per-file "
              "provenance density", file=sys.stderr)
        print("  ⚠️  Deferring this is a decision to leave the file unreadable. If you "
              "truly", file=sys.stderr)
        print("     cannot cut it, the BUDGET is wrong — change it in "
              "src/RimMandrake/Utils/doc_budget.py", file=sys.stderr)
        print("     and say why in the same commit. A budget that cannot be met gets "
              "ignored.", file=sys.stderr)
        return 1
    return 0                                     # queues only: reported, not charged


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:
        sys.exit(0)
