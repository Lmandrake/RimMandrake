#!/usr/bin/env python3
"""Selftest for block_blanket_git_stage.py — run after ANY change to it.

This hook denies Bash commands for four agents at once. A false ALLOW loses
someone's work to the index race; a false DENY wedges a thread mid-task and is
noticed within seconds. Both are cheap to catch here and expensive to catch
live, so every case below is one that has either happened or is one keystroke
away from happening.

    python3 .claude/hooks/selftest_block_blanket_git_stage.py
"""
import json
import subprocess
import sys
import os

HOOK = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                    "block_blanket_git_stage.py")

DENY, ALLOW = "deny", "allow"

CASES = [
    # ---- must DENY: blanket staging (the original 2026-08-11 failure) -------
    (DENY,  "git add -A"),
    (DENY,  "git add --all"),
    (DENY,  "git add ."),
    (DENY,  "git add -u"),
    (DENY,  "git add -An"),
    (DENY,  "git commit -a -m 'x'"),
    (DENY,  "git commit -am 'x'"),
    (DENY,  "git commit --all -m 'x'"),
    (DENY,  "git -C /mnt/d/Luke/dev/Rimworld add -A"),
    (DENY,  "echo hi && git add -A && echo done"),

    # ---- must DENY: naked commit, the shared-INDEX race (2026-08-12) --------
    (DENY,  "git commit -m 'x'"),
    (DENY,  "git commit -F - <<'EOF'"),
    (DENY,  "git commit"),
    (DENY,  "git commit --no-verify -m 'x'"),
    (DENY,  "git add file.md && git commit -m 'x'"),   # add-then-naked: the race
    (DENY,  "git commit -m 'touch file.md now'"),      # path only INSIDE the msg

    # ---- must DENY: hidden in a shell the command runs (2026-10-11) ---------
    (DENY,  "bash -c 'cd /x && git add -A'"),
    (DENY,  "sh -c \"git commit -am x\""),
    (DENY,  "bash <<'EOF'\ncd /x\ngit add .\nEOF"),
    (DENY,  "cat > f.py <<'EOF'\nprint(1)\nEOF\ngit add -A"),   # after the heredoc ends

    # ---- must DENY: an env prefix does not hide git ---------------------------
    (DENY,  "GIT_AUTHOR_NAME=x git add -A"),
    (DENY,  "env FOO=1 git commit -m 'x'"),
    (DENY,  "command git add ."),
    (ALLOW, "FOO=1 git commit path/one.md -m 'x'"),

    # ---- must ALLOW: the prescribed safe forms -----------------------------
    (ALLOW, "git commit path/one.md -m 'x'"),
    (ALLOW, "git commit path/one.md path/two.xml -F - <<'EOF'"),
    (ALLOW, "git commit -m 'x' path/one.md"),          # pathspec after the msg
    (ALLOW, "git commit -F - path/one.md <<'EOF'"),
    (ALLOW, "git commit -- path/one.md"),
    (ALLOW, "git commit --amend"),                     # explicitly still allowed
    (ALLOW, "git commit --amend --no-edit"),
    (ALLOW, "git commit --pathspec-from-file=paths.txt"),
    (ALLOW, "git add path/new.md"),                    # step 1 of the new-file pair
    (ALLOW, "git add path/one.md path/two.xml"),

    # ---- must ALLOW: everything that is not a staging command --------------
    (ALLOW, "git diff --cached --stat"),
    (ALLOW, "git restore --staged path/one.md"),
    (ALLOW, "git status --porcelain"),
    (ALLOW, "git log --oneline -5"),
    (ALLOW, "python3 src/RimMandrake/Utils/refresh.py"),
    (ALLOW, "echo 'git add -A is a bad idea'"),        # mentioned, not run
    # ---- must ALLOW: text, not commands (false positives hit 2026-10-11) ----
    (ALLOW, "python3 - <<'EOF'\nBLANKET = ['git add .', 'git add -A']\ngit add .\nEOF"),
    (ALLOW, "cat > notes.md <<EOF\ngit add -A\ngit commit -m x\nEOF"),
    (ALLOW, "python3 -c \"import re; re.compile('x; git add .')\""),
    (ALLOW, "grep -n 'git add .; git commit -a' f.md"),
]


def decision(cmd):
    payload = json.dumps({"tool_input": {"command": cmd}})
    out = subprocess.run([sys.executable, HOOK], input=payload,
                         capture_output=True, text=True).stdout.strip()
    if not out:
        return ALLOW
    try:
        d = json.loads(out)["hookSpecificOutput"]["permissionDecision"]
    except Exception:
        return ALLOW
    return DENY if d == "deny" else ALLOW


def main():
    bad = 0
    for want, cmd in CASES:
        got = decision(cmd)
        ok = got == want
        bad += not ok
        print("%s  want=%-5s got=%-5s  %s" %
              ("ok  " if ok else "FAIL", want, got, cmd))
    print("\n%d/%d passed" % (len(CASES) - bad, len(CASES)))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
