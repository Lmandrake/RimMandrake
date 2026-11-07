#!/usr/bin/env python3
"""PreToolUse/Bash hook: refuse a robocopy that can hang (CALL_DEADLINES_ENFORCE_130_OPEN_ENDED).

WHY: robocopy's defaults are /R:1000000 /W:30. On 2026-11-02 one unreadable file on a damaged USB stick
turned an agent's background robocopy into a 3.6 h hang that held BENCH past its hard restart
(infrastructure/state/facts/tool_traps.md). A retry bound
alone does not bound a copy, so a total deadline is required too.

Refuses (exit 2) a Bash command in which robocopy is INVOKED (first word of a segment, or inside a
cmd.exe / powershell.exe / pwsh segment) unless that segment carries /R:n with n<=5, /W:n with n<=30, and
a `timeout N` deadline in front of it (a WSL-side timeout kills the Windows child: measured 2026-11-03,
`timeout 3 PING.EXE -n 40` left no PING.EXE in tasklist). Mentions (grep, echo, git log, a file path)
are never touched. Code that runs robocopy is held to the same rule by
src/RimMandrake/Utils/call_deadline_lint.py.

    python3 .claude/hooks/selftest_block_unbounded_robocopy.py
"""
import json
import os
import re
import sys

R_MAX, W_MAX = 5, 30
ROBO = re.compile(r"\brobocopy(?:\.exe)?\b", re.I)
SHELLS = {"cmd", "cmd.exe", "powershell", "powershell.exe", "pwsh", "pwsh.exe"}
PREFIX = {"sudo", "env", "nohup", "exec", "command", "nice", "stdbuf"}
ASSIGN = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*=\S*$")
SPLIT = re.compile(r"\|\||&&|[;|&\n]|\$\(|`")

REASON = (
    "Blocked: this robocopy can hang for hours ({why}).\n\n"
    "robocopy's defaults are /R:1000000 /W:30: one unreadable file held BENCH for 3.6 h on 2026-11-02.\n"
    "Bound the retries AND the whole copy:\n"
    "    timeout -k 10 1800 robocopy.exe <src> <dst> /E /R:2 /W:5\n"
    "(/R:<=%d, /W:<=%d, and a `timeout N` in front; a WSL timeout kills the Windows process.)\n"
    "Lesson: infrastructure/state/facts/tool_traps.md"
    % (R_MAX, W_MAX))


def _words(seg):
    return seg.strip().split()


def _strip_prefix(words):
    """Drop env assignments and wrapper commands; report whether a `timeout N` deadline was seen."""
    deadline, i = False, 0
    while i < len(words):
        w = os.path.basename(words[i].strip("'\""))
        if ASSIGN.match(words[i]) or w in PREFIX:
            i += 1
        elif w == "timeout":
            i += 1
            while i < len(words) and words[i].startswith("-"):
                i += 2 if words[i] in ("-k", "-s", "--kill-after", "--signal") else 1
            if i < len(words) and re.match(r"^\d+(\.\d+)?[smhd]?$", words[i]):
                deadline = True
                i += 1
        else:
            break
    return deadline, words[i:]


def problems(command):
    """-> list of reasons, empty when every robocopy invocation is bounded (or there is none)."""
    out = []
    for seg in SPLIT.split(command or ""):
        if not ROBO.search(seg):
            continue
        deadline, rest = _strip_prefix(_words(seg))
        if not rest:
            continue
        head = os.path.basename(rest[0].strip("'\"").replace("\\", "/")).lower()
        if head not in ("robocopy", "robocopy.exe") and head not in SHELLS:
            continue                                   # a mention: grep, echo, git log, a path
        need = []
        r = re.search(r"/R:(\d+)", seg, re.I)
        w = re.search(r"/W:(\d+)", seg, re.I)
        if not r or int(r.group(1)) > R_MAX:
            need.append("/R:<=%d" % R_MAX)
        if not w or int(w.group(1)) > W_MAX:
            need.append("/W:<=%d" % W_MAX)
        if not deadline:
            need.append("a `timeout N` deadline")
        if need:
            out.append("needs " + ", ".join(need))
    return out


def main():
    try:
        data = json.load(sys.stdin)
    except (ValueError, OSError):
        return 0
    if (data.get("tool_name") or "") != "Bash":
        return 0
    cmd = (data.get("tool_input") or {}).get("command") or ""
    bad = problems(cmd)
    if bad:
        print(REASON.format(why="; ".join(bad)), file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
