#!/usr/bin/env python3
"""PreToolUse hook — an agent may not hand-write the owner's validation.

WHY
===
The north star system (design/RimMandrake/north_star_validation_spec.md, owner
2026-09-15) exists because a mod went GREEN while its experience was absent: the
pit mod's state assertions all passed while the player watched a pawn stand in a
64px vanilla trap icon. The fix binds a mod's verdict to a checklist of things a
screenshot must show — but only once the OWNER has validated that checklist. An
agent-written bar judged by an agent is two agents agreeing, which is not
evidence.

So there are exactly two things standing between a DRAFT checklist and a GREEN
mod, and both are one file edit away from being forged:

  1. `state: VALIDATED` + `validated-hash:` in the walk's `## north star`
     section. Written ONLY by `modcheck validate <mod> --owner-said "..."`,
     which prints the lines that are about to bind and refuses to bless
     silently. A hand-written pair turns an agent's draft into a bar.
  2. `infrastructure/state/modcheck_status.json`. Owned by `modcheck/status.py`,
     whose `verdict_for()` is where the five conditions of GREEN live. A
     hand-edited entry skips all five.

This is the same shape as CODE_REVIEW_STATUS.json ("never hand-edited") and the
ledger (written only by rimflow): the registry is not a document, it is the
output of a gate.

WHAT IS BLOCKED
===============
  Write/Edit/MultiEdit under design/validation_walks/ that introduces
      `state: VALIDATED`, or a `validated-hash:` with a value
  Write/Edit/MultiEdit to infrastructure/state/modcheck_status.json
  Bash that writes either of those (`>`, `>>`, `tee`, `sed -i`)

WHAT IS NOT BLOCKED
===================
  drafting a checklist — `state: DRAFT` and a blank `validated-hash:` are the
      normal agent-written form, and an agent SHOULD write those
  editing `## must be true`, walk steps, or any other part of a walk
  reading either file; `modcheck validate` / `review` / `run` themselves
  everything else

Fails OPEN: any parse problem allows the call through, because a broken hook
must never wedge the session.
"""
import json
import os
import re
import sys

WALK_DIR = os.path.join("design", "validation_walks")
REGISTRY = os.path.join("infrastructure", "state", "modcheck_status.json")

# `state: VALIDATED` on its own line, and `validated-hash:` with a value on the
# SAME line. Both are what `northstar.record_validation` writes and nothing else
# may. ⚠️ The horizontal-whitespace class is load-bearing: `\s*` crosses
# newlines, so a blank `validated-hash:` followed by any later text read as a
# forged hash and denied the normal DRAFT-drafting flow.
EDIT_TOOLS = ("Write", "Edit", "MultiEdit")
FORGED_STATE = re.compile(r"^[ \t]*state:[ \t]*VALIDATED[ \t]*$", re.M | re.I)
FORGED_HASH = re.compile(r"^[ \t]*validated-hash:[ \t]*\S+", re.M | re.I)

BASH_WRITE = re.compile(r">>?\s*\S*%s|tee\s+\S*%s|sed\s+(-\w+\s+)*-i"
                        % (re.escape("modcheck_status.json"),
                           re.escape("modcheck_status.json")))

VALIDATE_CMD = ('python3 src/RimMandrake/Utils/modcheck/cli.py validate <mod> '
                '--owner-said "<his verbatim words>"')


def _new_text(tool, tool_input):
    """Everything this call would ADD to the file. An Edit's `old_string` is
    what is being removed, so it is not read -- deleting a forged line is fine."""
    if tool == "Write":
        return tool_input.get("content") or ""
    if tool == "Edit":
        return tool_input.get("new_string") or ""
    if tool == "MultiEdit":
        return "\n".join(e.get("new_string") or ""
                         for e in tool_input.get("edits") or ())
    return ""


def offence(tool, tool_input):
    """A reason string, or None."""
    if tool == "Bash":
        cmd = tool_input.get("command") or ""
        if "modcheck_status.json" in cmd and BASH_WRITE.search(cmd):
            return ("this writes %s by hand. That registry is the output of "
                    "`modcheck/status.py`'s GREEN gate, not a document"
                    % REGISTRY)
        return None

    if tool not in EDIT_TOOLS:
        return None                         # reading either file is fine
    path = (tool_input.get("file_path") or "").replace("\\", "/")
    if not path:
        return None

    if path.endswith(REGISTRY.replace(os.sep, "/")):
        return ("%s is written only by `modcheck/status.py` -- its "
                "`verdict_for()` is where the five conditions of GREEN live, "
                "and a hand-written entry skips all five" % REGISTRY)

    if WALK_DIR.replace(os.sep, "/") in path:
        text = _new_text(tool, tool_input)
        if FORGED_STATE.search(text):
            return ("this writes `state: VALIDATED` into a validation walk by "
                    "hand. Only the owner validates a checklist")
        if FORGED_HASH.search(text):
            return ("this writes a `validated-hash:` value by hand. That hash "
                    "is what makes his validation un-rewritable; setting it "
                    "yourself defeats the one property the design turns on")
    return None


def main():
    try:
        payload = json.load(sys.stdin)
        tool = payload.get("tool_name") or ""
        tool_input = payload.get("tool_input") or {}
    except Exception:
        return 0                            # fail open

    why = offence(tool, tool_input)
    if not why:
        return 0

    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "deny",
            "permissionDecisionReason": (
                "Blocked: %s.\n\n"
                "A DRAFT checklist cannot green a mod, and the only route from "
                "DRAFT to VALIDATED is his word:\n\n"
                "    %s\n\n"
                "That verb prints every line about to bind and writes nothing "
                "without --owner-said. Run it with no --owner-said to read the "
                "bar to him first.\n\n"
                "Drafting is not blocked: `state: DRAFT` with a blank "
                "`validated-hash:` is the correct agent-written form, and "
                "distilling must-show lines from his recorded words is the "
                "job.\n\n"
                "See design/RimMandrake/north_star_validation_spec.md §5."
                % (why, VALIDATE_CMD)
            ),
        }
    }))
    return 0


if __name__ == "__main__":
    sys.exit(main())
