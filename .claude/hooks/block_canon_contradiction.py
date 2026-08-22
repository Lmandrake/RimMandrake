#!/usr/bin/env python3
"""PreToolUse/Bash hook — BLOCKS a commit whose design doc contradicts canon.yml.

WHY THIS ONE BLOCKS WHEN ITS SIBLINGS ONLY WARN
===============================================
A 2026-08-20 audit of the 119-document design tier found 21 numbers asserted at two or
more different values, in files that all read as current. Water was 25%, 22–28%, 8.6%,
8.1% and 6.9%. Factions were 14, 13, 12 and 11. None of it was carelessness — every
document was written by someone who had measured something — and it took ten agents a
full pass to reconcile.

⚠️ The cost is asymmetric, which is what earns the block. A contradiction costs seconds
to fix at commit time and a day to find later, because by then it has been quoted
forward into three more documents by people with no reason to doubt it. `Lake` was cut
in one file and load-bearing in five; the terminator was +14 in one and −37 in another,
and both were right about different things that nobody had said out loud.

⛔ IT BLOCKS ONLY ON A HARD CONTRADICTION. `check_canon.py` classifies undated mod
counts as ADVISORY and never fails on them: every one of the twenty was true the day it
was written, and the defect is the missing date, not the number.

THE ESCAPE HATCH IS PART OF THE DESIGN
======================================
A doc that genuinely must state a value canon disagrees with says so:

    <!-- canon-ok: quoting the dead worldgen_sea_spec on purpose -->

on the line or the line above. ⚠️ A block with no escape is a block that gets disabled,
and a disabled hook protects nothing. Requiring a REASON is the point — it converts a
silent contradiction into a sentence someone wrote deliberately.

Fail-open, stdlib only in the hook itself. ⚠️ `check_canon.py` imports PyYAML; if it is
missing the checker exits 2 and this hook ALLOWS, because UNMEASURED is not the same as
FAILED and refusing to commit over a missing dependency helps nobody.

    python3 .claude/hooks/selftest_block_canon_contradiction.py
"""
import json
import os
import re
import subprocess
import sys



# ---- pathspec extraction, borrowed wholesale from queue_lint --------------
# 🔑 Over-stripping is the SAFE direction: a missed pathspec means a rule does not fire;
# a phantom one from prose means CORRECT work is refused, and a hook that refuses correct
# work gets disabled — after which nothing is guarded at all.
_MSG_FLAG_RE = re.compile(r"""(?x)
    (?:^|\s) -(?:m|F|c|C|-message|-file|-reedit-message|-reuse-message)
    (?:=|\s+)
    (?: "(?:[^"\\]|\\.)*"? | '[^']*'? | \S+ )
""")
_HEREDOC_RE = re.compile(r"<<-?\s*['\"]?(\w+)['\"]?.*?^\1", re.S | re.M)
_PATH_RE = re.compile(r"[\w./-]+\.(?:md|jsonl)")


def commit_pathspec(cmd):
    stripped = _HEREDOC_RE.sub(" ", cmd)
    stripped = _MSG_FLAG_RE.sub(" ", stripped)
    stripped = re.sub(r"\"(?:[^\"\\]|\\.)*\"|'[^']*'", " ", stripped)
    return _PATH_RE.findall(stripped)


def proposed_body(ti, tool, full):
    """The content the file WOULD have after this tool call, or None if unknowable."""
    if tool == "Write":
        return ti.get("content")
    try:
        with open(full, encoding="utf-8") as fh:
            body = fh.read()
    except OSError:
        return None
    edits = ti.get("edits") or [ti]
    for e in edits:
        old, new = e.get("old_string"), e.get("new_string")
        if old is None or new is None or old not in body:
            return None                   # cannot simulate faithfully; stay silent
        body = body.replace(old, new, -1 if e.get("replace_all") else 1)
    return body


def check_body(root, rel, body, at_write):
    """Run check_canon over a TEMP copy of `body`. Nothing on disk is touched."""
    import tempfile
    tool = os.path.join(root, "src", "RimMandrake", "Utils", "check_canon.py")
    if not os.path.exists(tool):
        return 0
    d = tempfile.mkdtemp(prefix="canon_")
    try:
        stage = os.path.join(d, os.path.basename(rel))
        with open(stage, "w", encoding="utf-8") as fh:
            fh.write(body)
        try:
            r = subprocess.run([sys.executable, tool, stage], capture_output=True,
                               text=True, timeout=30, cwd=root)
        except Exception:
            return 0                      # never cost a write for a broken checker
        if r.returncode != 1:
            return 0
        detail = "\n".join(l for l in r.stdout.splitlines()
                            if l.strip() and not l.startswith("advisory"))
        # The checker reports the TEMP path it was handed; the seat needs its own.
        detail = re.sub(r"\S*" + re.escape(os.path.basename(rel)) + r"(?=:\d)",
                        rel, detail)
        print(json.dumps({"hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "deny",
            "permissionDecisionReason": (
                "\u26d4 Blocked at the WRITE — this would make %s contradict "
                "infrastructure/state/canon.yml.\n\n%s\n\n"
                "\u2705 Three ways forward, and all three are yours to take now:\n"
                "  1. The doc is wrong -> change what you were writing.\n"
                "  2. CANON is wrong -> change `infrastructure/state/canon.yml` in the "
                "same turn.\n     A ruling that has been overtaken is a defect, not a "
                "wall; fix it where it lives.\n"
                "  3. Both are right and the rule cannot see it -> put "
                "`<!-- canon-ok: why -->`\n     on the contradicting line.\n\n"
                "     python3 src/RimMandrake/Utils/check_canon.py --list\n\n"
                "\u26a0\ufe0f  Refused HERE rather than at the commit so you learn it "
                "before writing the\nrest of the doc, not after."
                % (rel, detail))}}))
        return 0
    finally:
        import shutil
        shutil.rmtree(d, ignore_errors=True)


def main():
    try:
        ev = json.load(sys.stdin)
    except Exception:
        return 0
    root = os.environ.get("CLAUDE_PROJECT_DIR") or os.getcwd()
    ti = ev.get("tool_input") or {}
    tool = ev.get("tool_name") or ""

    # ---- REFUSE AT THE WRITE ------------------------------------------------
    # 🔴 Owner's ruling, 2026-08-22: *"a guard refuses at the WRITE, never only at the
    # commit."* This hook used to permit every write into `design/**` and refuse the
    # commit, so a seat wrote a whole doc before learning it contradicted canon. The
    # proposed content is checked against a TEMP COPY — nothing on disk is touched.
    if tool in ("Write", "Edit", "MultiEdit"):
        fp = (ti.get("file_path") or "").replace("\\", "/")
        rel = fp[len(root) + 1:] if fp.startswith(root) else fp.lstrip("./")
        if not rel.startswith("design/") or not rel.endswith(".md"):
            return 0
        proposed = proposed_body(ti, tool, os.path.join(root, rel))
        if proposed is None:
            return 0                      # cannot simulate it; say nothing
        return check_body(root, rel, proposed, at_write=True)

    cmd = ti.get("command") or ""
    if "git" not in cmd or "commit" not in cmd:
        return 0
    # ⚠️ NOT `re.findall` over the whole command — that read a `design/…md` quoted in a
    # COMMIT MESSAGE as a path being committed and refused the commit for it.
    # `queue_lint.commit_pathspec` fixed exactly this bug and this hook never got it.
    paths = [q for q in commit_pathspec(cmd) if q.startswith("design/")]
    if not paths:
        return 0
    exists = [p for p in paths if os.path.exists(os.path.join(root, p))]
    if not exists:
        return 0

    tool = os.path.join(root, "src", "RimMandrake", "Utils", "check_canon.py")
    if not os.path.exists(tool):
        return 0
    try:
        r = subprocess.run([sys.executable, tool, *exists], capture_output=True,
                           text=True, cwd=root, timeout=60)
    except Exception:
        return 0                                   # fail open
    if r.returncode != 1:
        # 0 = clean. 2 = could not measure (no PyYAML). Neither is a contradiction.
        return 0

    body = "\n".join(l for l in r.stdout.splitlines()
                     if l.strip() and not l.startswith("advisory"))
    print(json.dumps({"hookSpecificOutput": {
        "hookEventName": "PreToolUse",
        "permissionDecision": "deny",
        "permissionDecisionReason": (
            "Blocked: a design doc in this commit contradicts "
            "infrastructure/state/canon.yml.\n\n%s\n\n"
            "Canon holds ONE traceable value per contested number, each with the "
            "measurement or ruling behind it. A contradiction costs seconds to fix now "
            "and a day to find later, because by then it has been quoted forward into "
            "other documents by people with no reason to doubt it.\n\n"
            "Three ways out, in order of how often each is right:\n"
            "  1. The doc is wrong  -> fix the number. Strike the old one through with "
            "a date rather than deleting it; never lose the history of a number.\n"
            "  2. The doc is QUOTING a dead value on purpose -> mark the line:\n"
            "         <!-- canon-ok: why this line states it -->\n"
            "  3. CANON is wrong -> fix canon.yml, with a `src:` for the new value, "
            "and record the loser under `superseded:`.\n\n"
            "    python3 src/RimMandrake/Utils/check_canon.py --list"
            "\n\n\u26a0\ufe0f  NOTHING IN THAT COMMAND RAN \u2014 including anything BEFORE the "
            "part that was\nrefused. A PreToolUse hook fires before the shell, so a compound "
            "command is refused\nwhole. If you chained a file write to a commit, the write did "
            "not happen either." % body[:2500])}}))
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:
        sys.exit(0)
