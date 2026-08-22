#!/usr/bin/env python3
"""Selftest for warn_skill_unwired.py.

⚠️ The ALLOW cases matter most. This hook fires on every SKILL.md write, so a false
warning on a correctly-wired skill is noise on the one path seats use constantly — and
a warning people learn to scroll past is worse than no warning at all.
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile

HOOK = os.path.join(os.path.dirname(os.path.abspath(__file__)), "warn_skill_unwired.py")
PASS, FAIL = [], []


def run(name, wired, target, tool="Write"):
    root = tempfile.mkdtemp(prefix="selftest_wire_")
    try:
        os.makedirs(os.path.join(root, "skills", name), exist_ok=True)
        open(os.path.join(root, "skills", name, "SKILL.md"), "w").write("# s\n")
        os.makedirs(os.path.join(root, ".claude", "skills"), exist_ok=True)
        if wired == "ok":
            os.symlink(os.path.join("..", "..", "skills", name),
                       os.path.join(root, ".claude", "skills", name))
        elif wired == "dangling":
            os.symlink(os.path.join("..", "..", "skills", "gone"),
                       os.path.join(root, ".claude", "skills", name))
        ev = ({"tool_name": tool, "tool_input": {"file_path": target}} if tool != "Bash"
              else {"tool_name": "Bash", "tool_input": {"command": target}})
        p = subprocess.run([sys.executable, HOOK], input=json.dumps(ev),
                           capture_output=True, text=True,
                           env=dict(os.environ, CLAUDE_PROJECT_DIR=root), timeout=20)
        return p.returncode, p.stderr
    finally:
        shutil.rmtree(root, ignore_errors=True)


CASES = [
    ("WARN  writing a SKILL.md with no symlink", 1, "none",
     "skills/brand-new-skill/SKILL.md", "Write"),
    # ⚠️ A DANGLING link is exactly as invisible as no link — the whole point.
    ("WARN  a symlink that points at nothing", 1, "dangling",
     "skills/brand-new-skill/SKILL.md", "Write"),
    ("ALLOW a correctly wired skill", 0, "ok",
     "skills/brand-new-skill/SKILL.md", "Write"),
    ("ALLOW editing a wired skill", 0, "ok",
     "skills/brand-new-skill/SKILL.md", "Edit"),
    # A reference file under a wired skill is not the SKILL.md and must not warn.
    ("ALLOW a reference file inside a skill", 0, "ok",
     "skills/brand-new-skill/references/traps.md", "Write"),
    ("WARN  committing an unwired SKILL.md", 1, "none",
     "git commit skills/brand-new-skill/SKILL.md -m x", "Bash"),
    ("ALLOW committing a wired one", 0, "ok",
     "git commit skills/brand-new-skill/SKILL.md -m x", "Bash"),
    ("ALLOW a commit touching no skill", 0, "ok", "git commit src/x.py -m x", "Bash"),
]

for label, want, wired, target, tool in CASES:
    rc, err = run("brand-new-skill", wired, target, tool)
    if rc == want:
        PASS.append(label)
        print("ok   %s" % label)
    else:
        FAIL.append(label)
        print("FAIL %s\n       want rc=%d got rc=%d\n%s" % (label, want, rc, err))

print("\n%d/%d passed" % (len(PASS), len(PASS) + len(FAIL)))
sys.exit(1 if FAIL else 0)
