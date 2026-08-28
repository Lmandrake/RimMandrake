#!/usr/bin/env python3
"""PreToolUse/SendMessage hook — agents may message their OWN subagents, never a peer window.

WHY THIS EXISTS RATHER THAN A DENY RULE
=======================================
The owner's ruling (2026-08-19) has two halves, and a blanket permission deny
can only satisfy one of them:

    "All that was meant is that Agents should not talk to each other. The User
     may send out messages and be heard by Agents, but that is all (/broadcast
     skill). Sub-agents should function normally."

`SendMessage` serves BOTH jobs. Claude Code's own documentation is explicit:
"Denying SendMessage also removes messaging to subagents and agent-team
teammates, since the same tool serves both." And there is no scoped specifier
syntax — `SendMessage` takes the bare tool name only, so a deny rule blocks
both or neither.

So `permissions.deny: ["SendMessage"]` enforced "no peer messaging" by ALSO
breaking every subagent resume — a seat could spawn a worker and then never
collect from it. This hook draws the line where the ruling actually draws it.

WHAT IS BLOCKED
===============
  a target naming an agent WINDOW / seat: BUILD, CHECK, DECIDE, REP, HUMAN,
  ALL  (any case, any surrounding punctuation)

WHAT IS ALLOWED
===============
  a target that is a spawned subagent id (the long hex handle the Agent tool
  hands back, e.g. a10c9b4b731f16d0a) — your own worker, your own context,
  costing no other seat anything.

THE OTHER HALF OF THE RULING, WHICH IS A SETTING AND NOT THIS HOOK
==================================================================
`crossSessionInbound` in .claude/settings.json MUST STAY "accept".

That is not an oversight and it is not the ruling being half-applied. The
owner's `broadcast.py` reaches every window by writing the peer socket, and
that socket "is run through the same inbound controls as any other peer
message" — so "refuse" would drop the OWNER'S OWN game-state announcements
(*game is up* / *game is loading* / *WRAP is initiated*), which are the one
thing that is supposed to get through. Inbound stays open for the human;
outbound is what this hook shuts.

⚠️ CLAUDE.md, POLICY.md and the four seat files all claim the setting reads
"refuse". They are wrong about the config and right about the intent.

⚠️ AND THE REPO-SCOPED "accept" DOES NOT GRANT ANYTHING — read off the CLI binary
2.1.238 on 2026-08-21 (BROADCAST_WITHOUT_A_DIALOG_1). Local/project settings only
RATCHET STRICTER: `if (N1i[n] > N1i[e ?? "accept"]) e = n`, N1i={accept:0,hold:1,
refuse:2}. So a project-scoped `accept` never exceeds the default and is
discarded — but a project-scoped `hold` or `refuse` WOULD take effect and would
drop the owner's announcements. "MUST STAY accept" above is therefore exactly
right; the value here only ever matters in the direction that shuts him out.
What actually gets his messages delivered without a dialog is the `from-mode`
attribute broadcast.py now asserts. Full write-up in its docstring.

Reads the hook JSON on stdin, writes a PreToolUse deny decision on stdout.
Fails OPEN on a malformed payload — a broken hook must not strand a seat that
is only trying to collect from its own worker.
"""

import json
import re
import sys

# The agent windows in this repo. A message aimed at one of these is the thing
# the ruling forbids.
SEATS = {
    "bench", "foundry",                       # the live windows, 2026-08-27
    "build", "check", "decide", "rep",        # retired seats — still refused
    "human", "all",
}

# The handle the Agent tool returns for a subagent this session spawned.
SUBAGENT_ID = re.compile(r"^[0-9a-f]{12,}$")

# Field names the target could arrive under, across harness versions.
TARGET_KEYS = ("to", "agentId", "agent_id", "target", "name", "sessionId")


def target_of(tool_input):
    for key in TARGET_KEYS:
        val = tool_input.get(key)
        if isinstance(val, str) and val.strip():
            return val.strip()
    return ""


def verdict(raw):
    """Return a refusal reason, or None to allow."""
    if not raw:
        # No target found at all. Allow: this is far more likely to be a
        # harness field rename than a peer message, and stranding a seat from
        # its own subagents is the worse failure.
        return None

    if SUBAGENT_ID.match(raw.lower()):
        return None                                   # own subagent: fine

    bare = raw.strip().strip("@<>[](){}'\"`,.:;!?").lower()
    if bare in SEATS:
        return "'%s' is an agent window, not your subagent" % raw

    # Anything else: a name we cannot positively identify as a spawned worker.
    # The subagent path always has the id available, so asking for it costs
    # nothing and closes the hole where a seat is addressed by a nickname.
    return ("'%s' is not a subagent id this hook can recognise" % raw)


def main():
    try:
        payload = json.load(sys.stdin)
        tool_input = payload.get("tool_input", {}) or {}
    except Exception:
        return 0                                      # fail open

    if not isinstance(tool_input, dict):
        return 0

    why = verdict(target_of(tool_input))
    if why is None:
        return 0

    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "deny",
            "permissionDecisionReason": (
                "Blocked by the owner's ruling of 2026-08-19: agents do not "
                "message each other. %s.\n\n"
                "Waking another seat is a USER function — the owner sends the "
                "rare cross-window message himself, with "
                "`python3 src/RimMandrake/Utils/broadcast.py`, and only to "
                "announce a change of GAME STATE.\n\n"
                "There is no exception for urgency, a reversed ruling, a spec, "
                "a handoff, a finding, or a peer about to destroy work. Put it "
                "where they already read:\n"
                "    work for another seat   infrastructure/state/queue/<SEAT>.md\n"
                "    the owner must decide   infrastructure/state/queue/HUMAN.md\n"
                "    a doctrine correction   the file that says otherwise, plus a commit\n"
                "    genuinely urgent        tell the OWNER in your own reply\n\n"
                "✅ Your OWN subagents are not peers and are not blocked. "
                "Resume one by the hex id the Agent tool returned, not by a "
                "nickname.\n"
                "See CLAUDE.md > 'AGENTS DO NOT MESSAGE EACH OTHER'."
                "\n\n\u26a0\ufe0f  NOTHING IN THAT COMMAND RAN \u2014 including anything BEFORE the "
                "part that was\nrefused. A PreToolUse hook fires before the shell, so a compound "
                "command is refused\nwhole. If you chained a file write to a commit, the write did "
                "not happen either." % why
            ),
        }
    }))
    return 0


if __name__ == "__main__":
    sys.exit(main())
