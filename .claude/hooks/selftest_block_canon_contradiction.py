#!/usr/bin/env python3
"""Selftest for block_canon_contradiction.py — run after ANY change to it or canon.yml.

⚠️ The ALLOW cases carry the weight here. This hook BLOCKS, and a block that fires on
correct work is worse than no block at all: it gets disabled, and then it protects
nothing rather than protecting most things. So most of what follows pins the cases
where it must stay quiet — an unrelated commit, a doc quoting a dead value on purpose,
an advisory-only hit, and a missing dependency.

    python3 .claude/hooks/selftest_block_canon_contradiction.py
"""
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
HOOK = os.path.join(HERE, "block_canon_contradiction.py")
ROOT = os.path.dirname(os.path.dirname(HERE))
PROBE_DIR = os.path.join(ROOT, "design", ".selftest_probe")
DENY, ALLOW = "deny", "allow"


def run(body, cmd_path="design/.selftest_probe/probe.md", write=True):
    os.makedirs(PROBE_DIR, exist_ok=True)
    path = os.path.join(PROBE_DIR, "probe.md")
    if write:
        open(path, "w", encoding="utf-8").write(body)
    env = dict(os.environ, CLAUDE_PROJECT_DIR=ROOT)
    p = subprocess.run([sys.executable, HOOK],
                       input=json.dumps({"tool_input":
                                         {"command": "git commit %s -m x" % cmd_path}}),
                       capture_output=True, text=True, env=env, cwd=ROOT, timeout=90)
    out = p.stdout.strip()
    if out:
        try:
            d = json.loads(out)["hookSpecificOutput"]
            return d["permissionDecision"], d["permissionDecisionReason"]
        except Exception:
            pass
    return ALLOW, p.stderr


CASES = [
    ("DENY  a live contradiction", DENY, "canon says 8.14%",
     "Water is ~25% of tiles, accept 22-28%.\n", None),
    ("DENY  a wrong faction count", DENY, "13 factions",
     "Fourteen factions stand on the map.\n", None),

    # The escape hatch. ⚠️ If this ever fails, the hook has no way out and will be
    # disabled by the first person who legitimately needs to quote a dead number.
    ("ALLOW <!-- canon-ok: --> on the line above", ALLOW, None,
     "<!-- canon-ok: quoting the dead worldgen_sea_spec on purpose -->\n"
     "Water is ~25% of tiles.\n", None),
    ("ALLOW <!-- canon-ok: --> on the same line", ALLOW, None,
     "Water is ~25% of tiles. <!-- canon-ok: the dead spec -->\n", None),

    # Prose that DOCUMENTS an old number is how a correction is written. Blocking it
    # would punish exactly the docs that did the work.
    ("ALLOW a struck-through historical value", ALLOW, None,
     "~~25% of tiles water~~ was the old spec; it is 8.14%.\n", None),
    ("ALLOW a denial — 'not 25%' asserts nothing", ALLOW, None,
     "Water is 8.14% of tiles — not 25%.\n", None),

    # Advisory hits must never gate: every undated mod count was true on its day.
    ("ALLOW an undated mod count (advisory only)", ALLOW, None,
     "The stack is 562 mods.\n", None),

    ("ALLOW a clean doc", ALLOW, None,
     "The planet is 21,872 tiles and 8.14% water.\n", None),
    ("ALLOW a commit touching no design/ file", ALLOW, None,
     "Water is ~25% of tiles.\n", "src/foo.py"),
]


def main():
    fails = 0
    try:
        for name, want, needle, body, path in CASES:
            got, reason = run(body, path or "design/.selftest_probe/probe.md")
            ok = got == want and (not needle or needle.lower() in (reason or "").lower())
            print("%-5s %s" % ("ok" if ok else "FAIL", name))
            if not ok:
                fails += 1
                print("        got=%s want=%s\n        %s"
                      % (got, want, (reason or "")[:300].replace("\n", "\n        ")))
    finally:
        import shutil
        shutil.rmtree(PROBE_DIR, ignore_errors=True)
    print("\n%d/%d passed" % (len(CASES) - fails, len(CASES)))
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
