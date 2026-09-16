#!/usr/bin/env python3
"""Selftest for block_forged_validation.py — run after ANY change to it.

A false ALLOW here lets an agent forge the owner's validation, which is the one
property the whole north-star design turns on. A false DENY blocks the drafting
work the same design asks agents to do. Both are cheap to catch here.

    python3 .claude/hooks/selftest_block_forged_validation.py
"""
import json
import os
import subprocess
import sys

HOOK = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                    "block_forged_validation.py")

DENY, ALLOW = "deny", "allow"

WALK = "design/validation_walks/RimMandrake/Pits.md"
REGISTRY = "infrastructure/state/modcheck_status.json"

DRAFT_SECTION = """## north star
state: DRAFT
validated-hash:

### must show
- [ ] `pit_reads_as_hole` — a sprung pit reads as a dark hole
"""

CASES = [
    # ---- must DENY: forging his validation --------------------------------
    (DENY, "Write", {"file_path": WALK,
                     "content": "## north star\nstate: VALIDATED\n"}),
    (DENY, "Edit", {"file_path": WALK, "old_string": "state: DRAFT",
                    "new_string": "state: VALIDATED"}),
    (DENY, "Edit", {"file_path": WALK, "old_string": "validated-hash:",
                    "new_string": "validated-hash: %s" % ("ab" * 32)}),
    (DENY, "MultiEdit", {"file_path": WALK, "edits": [
        {"old_string": "x", "new_string": "y"},
        {"old_string": "state: DRAFT", "new_string": "state: VALIDATED"},
    ]}),
    # lower case, and with trailing whitespace: same forgery
    (DENY, "Edit", {"file_path": WALK, "old_string": "state: DRAFT",
                    "new_string": "state: validated  "}),
    # an absolute path is the form the tools actually receive
    (DENY, "Write", {"file_path": "/Users/x/dev/RimMaster/" + WALK,
                     "content": "state: VALIDATED\n"}),

    # ---- must DENY: hand-editing the registry ------------------------------
    (DENY, "Write", {"file_path": REGISTRY, "content": "{}"}),
    (DENY, "Edit", {"file_path": REGISTRY, "old_string": '"RED"',
                    "new_string": '"GREEN"'}),
    (DENY, "Bash", {"command": 'echo "{}" > %s' % REGISTRY}),
    (DENY, "Bash", {"command": "sed -i 's/RED/GREEN/' %s" % REGISTRY}),
    (DENY, "Bash", {"command": "cat x | tee %s" % REGISTRY}),

    # ---- must ALLOW: drafting, which is the agent's actual job -------------
    (ALLOW, "Write", {"file_path": WALK, "content": DRAFT_SECTION}),
    (ALLOW, "Edit", {"file_path": WALK, "old_string": "- [ ] `a` — x",
                     "new_string": "- [ ] `a` — a sprung pit reads as a hole"}),
    (ALLOW, "Edit", {"file_path": WALK, "old_string": "## must be true",
                     "new_string": "## must be true\n- a new assertion"}),
    # removing a forged line is not forging one
    (ALLOW, "Edit", {"file_path": WALK, "old_string": "state: VALIDATED",
                     "new_string": "state: DRAFT"}),

    # ---- must ALLOW: everything else ---------------------------------------
    (ALLOW, "Read", {"file_path": REGISTRY}),
    (ALLOW, "Bash", {"command": "cat %s" % REGISTRY}),
    (ALLOW, "Bash", {"command": "python3 src/RimMandrake/Utils/modcheck/cli.py "
                                "status"}),
    (ALLOW, "Bash", {"command": 'python3 src/RimMandrake/Utils/modcheck/cli.py '
                                'validate Pits --owner-said "yes, bind it"'}),
    (ALLOW, "Write", {"file_path": "design/RimMandrake/notes.md",
                      "content": "state: VALIDATED"}),
    (ALLOW, "Bash", {"command": "echo hi > /tmp/x"}),
]


def decision(tool, tool_input):
    payload = json.dumps({"tool_name": tool, "tool_input": tool_input})
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
    for want, tool, tool_input in CASES:
        got = decision(tool, tool_input)
        ok = got == want
        bad += not ok
        label = tool_input.get("command") or tool_input.get("file_path")
        print("%s  want=%-5s got=%-5s  %-9s %s"
              % ("ok  " if ok else "FAIL", want, got, tool, label))
    print("\n%d/%d passed" % (len(CASES) - bad, len(CASES)))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
