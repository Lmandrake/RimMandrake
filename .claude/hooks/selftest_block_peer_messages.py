#!/usr/bin/env python3
"""Selftest for block_peer_messages.py — run after ANY change to it.

This hook carries BOTH halves of the owner's 2026-08-19 ruling, and the two
failure directions are not symmetric:

  * a false ALLOW re-opens agent-to-agent messaging, which is the thing the
    ruling exists to stop, and nobody notices because the message just works;
  * a false DENY strands a seat from its own subagents — loud, but it is how a
    blanket `permissions.deny: ["SendMessage"]` broke every subagent resume
    before this hook replaced it.

    python3 .claude/hooks/selftest_block_peer_messages.py

⚠️ Written 2026-08-21 alongside BROADCAST_WITHOUT_A_DIALOG_1, whose whole point
is that the OWNER's broadcasts now arrive with no dialog. That change is on the
INBOUND side and must not have loosened this, the outbound side. These cases are
what says it did not.
"""
import json
import os
import subprocess
import sys

HOOK = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                    "block_peer_messages.py")

DENY, ALLOW = "deny", "allow"

CASES = [
    # ---- must DENY: an agent window / seat, in every shape it is typed -----
    (DENY,  {"to": "BUILD"}),
    (DENY,  {"to": "build"}),
    (DENY,  {"to": "CHECK"}),
    (DENY,  {"to": "DECIDE"}),
    (DENY,  {"to": "REP"}),
    (DENY,  {"to": "HUMAN"}),
    (DENY,  {"to": "ALL"}),                    # there is no broadcast
    (DENY,  {"to": "@BUILD"}),                 # the typeahead form
    (DENY,  {"to": " Check, "}),
    (DENY,  {"to": "[DECIDE]"}),
    (DENY,  {"agentId": "REP"}),               # other field names
    (DENY,  {"agent_id": "BUILD"}),
    (DENY,  {"target": "CHECK"}),
    (DENY,  {"name": "DECIDE"}),
    (DENY,  {"sessionId": "HUMAN"}),

    # ---- must DENY: anything not positively identifiable as a subagent -----
    (DENY,  {"to": "AGENT OPS"}),              # a window's display name
    (DENY,  {"to": "worker"}),                 # a nickname, not an id
    (DENY,  {"to": "BUILD-2"}),

    # ---- must ALLOW: this session's own spawned subagent -------------------
    (ALLOW, {"to": "a10c9b4b731f16d0a"}),
    (ALLOW, {"to": "aa870a9fc9c75cfb9"}),      # a real id from this session
    (ALLOW, {"agentId": "0123456789ab"}),      # 12 hex, the shortest accepted
    (ALLOW, {"to": "A10C9B4B731F16D0A"}),      # case-insensitive

    # ---- must ALLOW: fail-open on a payload this hook cannot read ----------
    (ALLOW, {}),                               # harness renamed every field
    (ALLOW, {"message": "hello"}),             # target absent
]


def decision(tool_input):
    payload = json.dumps({"tool_name": "SendMessage", "tool_input": tool_input})
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
    for want, ti in CASES:
        got = decision(ti)
        ok = got == want
        bad += not ok
        print("%s  want=%-5s got=%-5s  %s" %
              ("ok  " if ok else "FAIL", want, got, json.dumps(ti)))
    print("\n%d/%d passed" % (len(CASES) - bad, len(CASES)))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
