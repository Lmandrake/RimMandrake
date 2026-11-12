#!/usr/bin/env python3
"""PreToolUse gate for the Claude Whittle loops: each loop drives only its own game, an offline loop drives none.

Installed per worker clone in the gitignored .claude/settings.local.json by install.sh:
  {"hooks":{"PreToolUse":[{"matcher":"Bash","hooks":[{"type":"command",
     "command":"python3 \"${CLAUDE_PROJECT_DIR}/infrastructure/whittle_claude/gate.py\" <lane>"}]}]}}
Lanes: archmagi (Archmagi's game only), steve (SteveDesktop's game A only, through whittle_claude/steve.sh), offline (no
game). Reads the hook JSON on stdin; exit 2 with the reason on stderr refuses the Bash call, exit 0 lets it run.
It is a guard rail against a wrong-machine slip, not a sandbox: a command it cannot parse is let through.

  gate.py <lane> --test "<command>"   print ALLOW or REFUSE: <why>, for checking a pattern by hand
"""
import json
import re
import sys

GAME = re.compile(
    r"bridge\s+take|rimbridge|live_session|modset_builder[^|;&]*--apply|modlist_swap|deploy_custom_mods[^|;&]*--apply"
    r"|logwait|\./game\s+(?:\S+\s+)*(?:up|down|loading)\b|--live\b|northstar_driver|northstar_site|gate_live_proof"
    r"|firefoam_aim_live_proof|human_review\.py|RimWorldWin64|steam://|Start-Process|taskkill|system_click"
    r"|system_screenshot|rw_game\.sh|preflight_bridge")
STEVE = re.compile(r"steve\.sh|stevedesktop", re.I)
RIMFLOW = re.compile(r"(?:rimflow|rimflow/cli\.py)\s+(\S+)")
# commands whose arguments are only text or files: they cannot start a game, so a game word inside them (a grep pattern,
# a commit message) is no reason to refuse. `git` is here for commit messages and ledger work.
INERT = {"git", "grep", "egrep", "rg", "cat", "ls", "head", "tail", "wc", "diff", "echo", "printf", "sort", "uniq", "find",
         "stat", "file", "less", "cut", "tr", "sed", "awk", "jq", "test", "[", "cd", "mkdir", "cp", "mv", "rm", "touch"}


def split_segments(cmd):
    """Split on && || ; | and newlines, but not inside '...' or "..." (steve.sh's remote command is quoted)."""
    segs, cur, q, i = [], [], None, 0
    while i < len(cmd):
        c = cmd[i]
        if q:
            cur.append(c)
            if c == "\\" and q == '"' and i + 1 < len(cmd):
                cur.append(cmd[i + 1]); i += 1
            elif c == q:
                q = None
        elif c in "'\"":
            q = c; cur.append(c)
        elif c in ";\n|&":
            segs.append("".join(cur)); cur = []
            while i + 1 < len(cmd) and cmd[i + 1] in "|&" and c in "|&":
                i += 1
        else:
            cur.append(c)
        i += 1
    segs.append("".join(cur))
    return [s.strip() for s in segs if s.strip()]


def substitutions(seg):
    """Bodies of $(...) and `...` in a segment: bash runs them before the command they sit in."""
    out, i = [], 0
    while True:
        i = seg.find("$(", i)
        if i < 0:
            break
        depth, j = 1, i + 2
        while j < len(seg) and depth:
            depth += {"(": 1, ")": -1}.get(seg[j], 0)
            j += 1
        out.append(seg[i + 2:j - 1 if depth == 0 else j])
        i += 2
    out += re.findall(r"`([^`]*)`", seg)
    return [b for b in out if not re.match(r"\s*cat\s+<<", b)]   # a commit message heredoc is text


def first_word(seg):
    for w in seg.split():
        if "=" in w and not w.startswith(("-", "/", ".")) and w.split("=", 1)[0].replace("_", "").isalnum():
            continue   # FOO=bar prefix
        return w.rsplit("/", 1)[-1]
    return ""


def verdict(lane, cmd):
    segs = split_segments(cmd)
    for s in segs:
        for body in substitutions(s):
            v = verdict(lane, body)
            if v.startswith("REFUSE"):
                return v
        if first_word(s) in INERT:
            continue
        rf = RIMFLOW.search(s)
        verb = rf.group(1) if rf else None
        # the ledger: every verb is fine except taking a game you do not drive (close --live is a ledger record)
        if verb and verb != "bridge":
            continue
        if verb == "bridge" and not re.search(r"bridge\s+take", s):
            continue
        if lane == "offline":
            if GAME.search(s):
                return "REFUSE: an offline loop drives no game (%r); finish the offline part and park the live step" % s[:120]
        elif lane == "archmagi":
            if STEVE.search(s):
                return ("REFUSE: SteveDesktop's game belongs to CLAUDE_STEVEDESKTOP_FWLIVE (%r); this loop drives "
                        "Archmagi's game only" % s[:120])
        elif lane == "steve":
            if "whittle_claude/steve.sh" in s:
                continue
            if re.search(r"bridge\s+take", s):
                if not re.search(r"--host\s+stevedesktop\b(?!\.)", s):
                    return "REFUSE: this loop takes SteveDesktop's game only: rimflow bridge take --host stevedesktop ..."
                continue
            if GAME.search(s):
                return ("REFUSE: Archmagi's game belongs to CLAUDE_ARCHMAGI_FWLIVE (%r); drive SteveDesktop's game A "
                        "through infrastructure/whittle_claude/steve.sh" % s[:120])
    return "ALLOW"


def main(argv):
    lane = argv[1] if len(argv) > 1 else "offline"
    if len(argv) > 3 and argv[2] == "--test":
        print(verdict(lane, argv[3]))
        return 0
    try:
        d = json.load(sys.stdin)
        cmd = d.get("tool_input", {}).get("command") or ""
    except (ValueError, AttributeError):
        return 0
    v = verdict(lane, cmd)
    if v.startswith("REFUSE"):
        print("whittle_claude gate (%s lane): %s" % (lane, v), file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
