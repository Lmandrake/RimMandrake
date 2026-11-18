#!/usr/bin/env python3
"""selftest_role_headers_state_free.py: no role file says whether its role is switched on.

ROLE_HEADERS_RETIRE_ENABLED_PROSE: rimflow/roles/*.md headers said "(v3.x, enabled)" and "`enabled: true` since ..."
while dispatcher_schedule.json had the Producer, Auditor and Innovator rows disabled (read 2026-11-18). Whether a role
runs is its schedule row's `enabled` field and nothing else; a role file may say how the switch works ("Off switch:
`enabled: false` on the X role"), never which way it is set.

Run: python3 src/RimMandrake/rimflow/selftest_role_headers_state_free.py
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROLES = os.path.join(HERE, "roles")

# a state claim: the title's "(v3.1, enabled)" or a sentence giving the switch's current setting
TITLE_STATE = re.compile(r"^#.*\((?:[^)]*,\s*)?(?:enabled|disabled)\)", re.I)
SET_STATE = re.compile(r"`enabled:\s*(?:true|false)`\s*(?:since|,\s*for|and no slots)", re.I)


def claims(text):
    """-> [(line number, line)] of every state claim in a role file's text."""
    out = []
    for n, line in enumerate(text.splitlines(), 1):
        if (n == 1 and TITLE_STATE.search(line)) or SET_STATE.search(line):
            out.append((n, line.strip()))
    return out


def main():
    fails = 0

    def check(name, cond, detail=""):
        nonlocal fails
        print("%s  %s%s" % ("ok  " if cond else "FAIL", name, ("\n        " + detail) if detail and not cond else ""))
        fails += 0 if cond else 1

    # the instrument sees: planted claims are caught, the mechanism sentence is not
    check("a title naming the state is caught", claims("# Producer role: instructions (v3.3, enabled)\n"))
    check("a 'disabled' title is caught", claims("# X role (disabled)\n"))
    check("'`enabled: true` since' is caught", claims("x\nRegistered ... `enabled: true` since the v3 night\n"))
    check("'with `enabled: false`, for the Conductor to flip' is caught",
          claims("x\nRegistered in s → roles[name=A] with `enabled: false`, for the Conductor to flip.\n"))
    check("the off-switch mechanism line is allowed",
          not claims("x\n**Off switch:** `enabled: false` on the Auditor role in the schedule (the owner's)\n"))
    check("a plain title is allowed", not claims("# Auditor role: instructions (v3.4)\n"))

    names = sorted(n for n in os.listdir(ROLES) if n.endswith(".md"))
    check("the roles folder is read (%d files)" % len(names), len(names) >= 5)
    bad = []
    for n in names:
        with open(os.path.join(ROLES, n), encoding="utf-8") as fh:
            bad += ["%s:%d: %s" % (n, ln, text[:120]) for ln, text in claims(fh.read())]
    check("no role file states its switch setting", not bad, "\n        ".join(bad))
    print("\n%s" % ("ALL OK" if not fails else "%d FAILED" % fails))
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
