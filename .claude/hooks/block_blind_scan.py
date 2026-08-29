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

def _measure_scripts():
    """Find the measuring-large-artifacts skill, which lives OUTSIDE this repo.

    It is a generic skill that this project happens to use, so it is versioned
    on its own. Three places are tried, most explicit first; returns None if it
    is not installed, and every caller here degrades rather than failing.
    """
    import os
    cands = []
    env = os.environ.get("MEASURE_SKILL_HOME")
    if env:
        cands.append(os.path.join(env, "scripts"))
    cands.append(os.path.expanduser(
        "~/.claude/skills/measuring-large-artifacts/scripts"))
    d = os.path.abspath(__file__)
    while d != os.path.dirname(d):
        d = os.path.dirname(d)
        if os.path.isdir(os.path.join(d, ".git")):
            cands.append(os.path.join(os.path.dirname(d),
                                      "measuring-large-artifacts", "scripts"))
            break
    for c in cands:
        if os.path.isdir(os.path.join(c, "measure")):
            return c
    return None


_S = _measure_scripts()
if _S:
    sys.path.insert(0, _S)

try:
    from measure import artifacts
except Exception:                                   # fail open, always
    artifacts = None

#: Real instruments. If one of these appears anywhere on the command line the
#: whole segment is allowed — they are ALLOWED to name the artifact, that is
#: their job, and several of them shell out to a scanner internally.
INSTRUMENTS = (
    "measure", "cli.py", "savemap.py", "harvest_log.py",
    "validate_save_artifact.py", "refresh.py", "worldview.py",
    "def_inventory.py", "animal_live_diff.py", "rimbridge_client.py",
)

#: Flags that consume the next token, so a pattern is never mistaken for a path.
TAKES_ARG = {"-e", "--regexp", "-f", "--file", "-m", "--max-count",
             "--include", "--exclude", "--exclude-dir", "-A", "-B", "-C",
             "--after-context", "--before-context", "--context", "-d",
             "--devices", "--binary-files", "-t", "--type", "-g", "--glob"}

REDIR = re.compile(r"^(<<-?|<|>>|>|\d*>&?\d*)")


def segments(cmd):
    """Split a compound command into the individual commands it runs.

    Also unwraps `bash -c "..."` / `sh -c "..."`, because a scan hidden one
    quote deep is still a scan. Found by red team 2026-08-21.
    """
    parts = [s for s in re.split(r"\|\||&&|\||;|\n", cmd) if s.strip()]
    out = []
    for seg in parts:
        out.append(seg)
        try:
            tok = shlex.split(seg)
        except ValueError:
            continue
        for i, t in enumerate(tok[:-1]):
            if os.path.basename(t) in ("bash", "sh", "zsh") and tok[i + 1] == "-c":
                if i + 2 < len(tok):
                    out.extend(segments(tok[i + 2]))
    return out


def _tool_and_args(tok):
    """Strip env assignments and wrappers; return (tool, remaining args)."""
    i = 0
    while i < len(tok) and "=" in tok[i] and not tok[i].startswith("-"):
        i += 1
    while i < len(tok) and tok[i] in ("sudo", "time", "nice", "command", "xargs",
                                      "env"):
        i += 1
    if i >= len(tok):
        return None, []
    return os.path.basename(tok[i]), tok[i + 1:]


def _paths_in(args, tool, cwd):
    """Every token in `args` that names a classified artifact.

    Two rules keep this from firing on search patterns, which is what made an
    earlier cut refuse `grep -c "world/tiles.csv" notes.txt`:
      * for grep-family tools the FIRST non-flag token is the pattern, skipped
      * a token must actually look like a path
    """
    hits = []
    skip_pattern = tool in artifacts.PATTERN_FIRST
    j = 0
    while j < len(args):
        t = args[j]
        if t in TAKES_ARG:
            j += 2
            continue
        if t.startswith("-") or REDIR.match(t):
            j += 1
            continue
        if skip_pattern:
            skip_pattern = False        # that was the pattern
            j += 1
            continue
        cand = t
        if cwd and not os.path.isabs(cand):
            # ⚠️ NOT gated on os.path.exists(joined): classify() is pure
            # pattern matching (fnmatch), so existence buys nothing and
            # actively defeats resolution whenever the artifact's layout has
            # moved since a fixture/pattern was written, or the mount is
            # slow/absent - the exact case that let a relative-path scan
            # through (BLIND_SCAN_RELATIVE_PATHS_1).
            cand = os.path.join(cwd, cand)
        if artifacts.looks_like_path(cand) or artifacts.looks_like_path(t):
            art = artifacts.classify(cand) or artifacts.classify(t)
            if art is not None:
                hits.append((art, cand))
        j += 1
    return hits


def offence(cmd, cwd=None):
    """(artifact, tool, path) if this command blind-scans a structured file."""
    if artifacts is None:
        return None

    reader_hits = []          # artifacts opened by cat/head/... earlier in a pipe
    for segment in segments(cmd):
        try:
            tok = shlex.split(segment)
        except ValueError:
            continue
        if not tok:
            continue

        # An instrument is recognised by its own token, not by appearing
        # anywhere in the line — a trailing `# per rimbench` comment used to
        # wave a scan straight through.
        if any(os.path.basename(t).split("=")[0] in INSTRUMENTS
               or t in INSTRUMENTS for t in tok):
            continue

        tool, args = _tool_and_args(tok)
        if tool is None:
            continue

        if tool in artifacts.READERS:
            reader_hits.extend(_paths_in(args, tool, cwd))
            continue

        if tool not in artifacts.BLIND_SCANNERS:
            continue

        hits = _paths_in(args, tool, cwd)
        if hits:
            return hits[0][0], tool, hits[0][1]
        if reader_hits:
            # `cat save.rws | grep -c biome` — the path and the scanner are on
            # different segments, and neither alone looks wrong.
            art, path = reader_hits[0]
            return art, tool, path
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

    hit = offence(cmd, payload.get("cwd"))
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
