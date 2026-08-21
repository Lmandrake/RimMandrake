#!/usr/bin/env python3
"""PreToolUse/Bash hook — refuse a byte scan of an artifact whose encoding it
cannot read. Option E of SCANNED_ARTIFACTS_CANNOT_LIE_1.

WHY
===
Seven instruments were caught returning confident wrong NUMBERS in one session
(2026-08-21). The register is `infrastructure/state/BUILDABLE.md`, "INSTRUMENTS
THAT RETURN A CONFIDENT WRONG ANSWER". Three of them were a byte scanner pointed
at a structured file:

  * `grep` on a `.rws` for biome defNames returned **2**, where the answer was
    3 / 233 / 31. World biomes are indices into a compressed grid; they are not
    present as text at all.
  * `strings -a -el` on the companion DLL found **16** of 115 tool names.
    Attribute strings live in .NET metadata blobs, not as UTF-16 literals.
  * a count off the def dump read **0** for a type holding 612 defs.

None of those printed an error. That is the whole problem: **a scanner that does
not understand the encoding returns a plausibly-shaped number and no warning**,
and the number then decides something expensive.

This hook is the only part of the fix that acts BEFORE the wrong number exists.

WHAT IS BLOCKED
===============
A blind scanner (`grep`, `rg`, `strings`, `wc`, `awk`, `sed`, ...) whose command
line names a path that `measure/artifacts.py` classifies as a structured
artifact — the def dump, a `.rws`, a `.dll`, a world CSV, `Player.log`.

WHAT IS NOT BLOCKED
===================
  * anything not naming one of those artifacts — the overwhelming majority
  * `measure/cli.py`, `savemap.py`, `harvest_log.py` and the other real
    instruments, including when their own arguments name the artifact
  * a scan run with MEASURE_ALLOW_SCAN=1 in the environment
  * `ls`, `stat`, `cp`, `du`, `head` and anything else that is not a scanner
  * a scanner reading from a pipe with no artifact path on the line

⚠️ **It fails OPEN.** Any parse problem, missing import or unreadable stdin
allows the command through. A hook that wedges the session is worse than the
failure it prevents — and this one gates a very common tool.

🔑 **Why a refusal here is safe, when the analysis warned that enforcement
without a cheap alternative is just an obstacle:** the alternative shipped
first. `measure/cli.py count <Type>` answers in one line, which is *less* effort
than composing a grep. E was deliberately built after C. If the instrument ever
stops being cheaper than the scan, remove this hook rather than keeping both.
"""
import json
import os
import re
import shlex
import sys

REPO = os.environ.get("CLAUDE_PROJECT_DIR") or os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(REPO, "src", "RimMandrake"))

try:
    from measure import artifacts
except Exception:                                   # fail open, always
    artifacts = None

#: Real instruments. If one of these appears anywhere on the command line the
#: whole segment is allowed — they are ALLOWED to name the artifact, that is
#: their job, and several of them shell out to a scanner internally.
INSTRUMENTS = (
    "measure/cli.py", "measure.cli", "savemap.py", "harvest_log.py",
    "rimbench", "validate_save_artifact.py", "refresh.py", "worldview.py",
    "def_inventory.py", "animal_live_diff.py", "rimbridge_client.py",
)

#: Flags that consume the next token, so a pattern is never mistaken for a path.
TAKES_ARG = {"-e", "--regexp", "-f", "--file", "-m", "--max-count",
             "--include", "--exclude", "--exclude-dir", "-A", "-B", "-C",
             "--after-context", "--before-context", "--context", "-d",
             "--devices", "--binary-files", "-t", "--type", "-g", "--glob"}

REDIR = re.compile(r"^(<<-?|<|>>|>|\d*>&?\d*)")


def segments(cmd):
    """Split a compound command into the individual commands it runs."""
    return [s for s in re.split(r"\|\||&&|\||;|\n", cmd) if s.strip()]


def offence(segment):
    """(artifact, tool, path) if this segment blind-scans a structured file."""
    if artifacts is None:
        return None
    try:
        tok = shlex.split(segment)
    except ValueError:
        return None
    if not tok:
        return None

    joined = " ".join(tok)
    if any(ins in joined for ins in INSTRUMENTS):
        return None

    # the tool is the first token that is not an env assignment or a wrapper
    i = 0
    while i < len(tok) and ("=" in tok[i] and not tok[i].startswith("-")):
        i += 1
    while i < len(tok) and tok[i] in ("sudo", "time", "nice", "command", "xargs"):
        i += 1
    if i >= len(tok):
        return None
    tool = os.path.basename(tok[i])
    if tool not in artifacts.BLIND_SCANNERS:
        return None

    j = i + 1
    while j < len(tok):
        t = tok[j]
        if t in TAKES_ARG:
            j += 2
            continue
        if t.startswith("-") or REDIR.match(t):
            j += 1
            continue
        art = artifacts.classify(t)
        if art is not None:
            return art, tool, t
        j += 1
    return None


def main():
    try:
        payload = json.load(sys.stdin)
    except Exception:
        return 0
    if payload.get("tool_name") != "Bash":
        return 0
    cmd = (payload.get("tool_input") or {}).get("command") or ""
    if not cmd:
        return 0
    if os.environ.get("MEASURE_ALLOW_SCAN") or "MEASURE_ALLOW_SCAN=1" in cmd:
        return 0

    for seg in segments(cmd):
        hit = offence(seg)
        if hit:
            art, tool, path = hit
            print(json.dumps({
                "hookSpecificOutput": {
                    "hookEventName": "PreToolUse",
                    "permissionDecision": "deny",
                    "permissionDecisionReason": (
                        artifacts.refusal_text(art, tool, path)
                        + "\n\n⚠️  NOTHING IN THAT COMMAND RAN — a PreToolUse "
                          "hook fires before the shell, so a compound command "
                          "is refused whole."
                    ),
                }
            }))
            return 0
    return 0


if __name__ == "__main__":
    sys.exit(main())
