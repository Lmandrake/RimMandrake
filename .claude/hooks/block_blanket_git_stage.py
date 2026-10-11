#!/usr/bin/env python3
"""PreToolUse/Bash hook — refuse blanket git staging in this repo.

WHY
===
Each seat clone has one owning window, but that window's subagents and
background jobs all work in the same tree and the same index. At any moment
much of what `git status` shows belongs to one of them, mid-edit. A blanket add
sweeps their unfinished work — and their *staged* work — into your commit,
under your message.

Both failure modes have already happened here, in the same commit (76d7f64,
2026-08-11):
  - it swept three staged `git mv` renames out of another thread's in-flight
    docs audit and committed them under a message about load order;
  - it committed documentation for a script while leaving the script behind,
    because `git commit -a` stages tracked modifications and ignores new
    untracked files.

So the rule in CLAUDE.md is: name every path. This enforces it.

WHAT IS BLOCKED
===============
  git add -A / --all / . / -u / --update       (and short bundles like -An)
  git commit -a / -am / --all
  git commit WITHOUT A PATHSPEC                (see "the index race" below)
  the same via `git -C <dir> ...`, inside compound commands, inside
  `bash -c '...'` / `sh -c`, and inside a heredoc fed to a shell (`bash <<EOF`)

NOT matched (false positives, 2026-10-11): the text `git add .` inside a quoted
string or inside a heredoc fed to anything but a shell (`python3 - <<'EOF'`,
`cat > f <<'EOF'`). Splitting is quote-aware, so `"a; git add ."` is one word.

WHAT IS NOT BLOCKED
===================
  git add <explicit paths>          git commit <paths> -m "..."
  git commit --amend                git commit --pathspec-from-file=<f>
  git diff --cached --stat          git restore --staged <p>
  everything non-git

`-u`/`--update` is included deliberately: it is `commit -a` in `add` form —
every tracked modification in the tree, including other threads'.

THE INDEX RACE — why a naked `git commit` is blocked too
========================================================
Naming paths on `git add` is NOT sufficient, because the index is shared. A
bare `git commit` commits the WHOLE index, including files another thread
staged in the window between your add and your commit. It fired twice on
2026-08-12 (`7c15278`, `5f67910`) and the prescribed `git diff --cached --stat`
guard *printed the foreign file and was still missed*. Discipline does not fix
a race; only removing the index from the path does.

    git commit path/one.md path/two.xml -F -    <- cannot pick up anyone else

⚠️ **`git commit <path>` requires git to already know the path**, so a BRAND-NEW
file is a two-step, and the second step still carries the pathspec:

    git add  path/new.md          # makes the path known
    git commit path/new.md -F -   # still bypasses the index

Measured 2026-08-12, because the belief in circulation was that the pathspec
form "cannot commit a new file" and the workaround was a bare commit — which
reopens the exact race. It is true only of an *untracked* path; after `git add`
the pathspec form commits a new file correctly. Verified in a throwaway repo:
with a peer's `theirs.txt` also staged, `git commit mine.txt` committed only
`mine.txt` and left `theirs.txt` staged and untouched.

Reads the hook JSON on stdin, writes a PreToolUse deny decision on stdout.
Fails OPEN: any parse problem allows the command through, because a broken
hook must never wedge the session.
"""
import json
import os
import re
import shlex
import sys

# global options that consume the following token, e.g. `git -C /path add -A`
TAKES_ARG = {"-C", "-c", "--git-dir", "--work-tree", "--namespace", "--exec-path"}

ADD_BLANKET = {"-A", "--all", "--no-ignore-removal", "-u", "--update", "."}

# `git commit` options that swallow the FOLLOWING token as their value. Without
# this table a message body would be mistaken for a pathspec and the commit
# would be waved through — the one failure direction that matters here.
COMMIT_TAKES_ARG = {
    "-m", "--message", "-F", "--file", "-c", "--reedit-message",
    "-C", "--reuse-message", "-t", "--template", "--author", "--date",
    "--cleanup", "--fixup", "--squash", "--trailer", "--pathspec-from-file",
}

# Options that make a naked `git commit` legitimate: it is no longer "whatever
# happens to be in the shared index".
COMMIT_PATHSPEC_EXEMPT = {"--amend", "--pathspec-from-file"}

# Shell tokens that survive shlex.split but are redirections, not pathspecs.
# `git commit -F - <<'EOF'` must not look like it names a file.
REDIR = re.compile(r"^(<<-?|<|>>|>|\d*>&?\d*)")


def offence(segment):
    """Return a reason string if this one command is a blanket stage, else None."""
    try:
        tok = shlex.split(segment)
    except ValueError:
        return None                      # unbalanced quotes: not our problem
    if not tok or tok[0] != "git":
        return None

    i = 1
    while i < len(tok) and tok[i].startswith("-"):
        i += 1 if tok[i] not in TAKES_ARG else 2
    if i >= len(tok):
        return None
    sub, args = tok[i], tok[i + 1:]

    if sub in ("add", "stage"):
        for a in args:
            if a in ADD_BLANKET:
                return "`git %s %s` stages everything in the tree" % (sub, a)
            # short bundles: -An, -Av ...
            if re.fullmatch(r"-[A-Za-z]*[Au][A-Za-z]*", a):
                return "`git %s %s` bundles a blanket flag" % (sub, a)
    elif sub in ("commit", "ci"):
        for a in args:
            if a == "--all":
                return "`git commit --all` stages every tracked modification"
            # -a, -am, -ma ... but never --amend / --author (they start with --)
            if re.fullmatch(r"-[A-Za-z]*a[A-Za-z]*", a):
                return "`git commit %s` stages every tracked modification" % a
        if not commit_has_pathspec(args):
            return ("`git commit` without a pathspec commits the WHOLE shared "
                    "index")
    return None


def commit_has_pathspec(args):
    """True if this `git commit` names paths, or is otherwise index-safe."""
    i = 0
    while i < len(args):
        a = args[i]

        if a == "--":                       # everything after is a pathspec
            rest = [x for x in args[i + 1:] if not REDIR.match(x)]
            return bool(rest)

        if a.startswith("-"):
            base = a.split("=", 1)[0]
            if base in COMMIT_PATHSPEC_EXEMPT:
                return True
            # `--opt=value` carries its own argument; `--opt value` eats the next
            if base in COMMIT_TAKES_ARG and "=" not in a:
                i += 2
                continue
            i += 1
            continue

        if REDIR.match(a):                  # `<<EOF`, `>log` — not a path
            i += 1
            continue

        return True                         # a bare positional: a pathspec
    return False


SHELLS = {"bash", "sh", "zsh", "dash"}
HEREDOC = re.compile(r"<<-?\s*(['\"]?)([A-Za-z_][A-Za-z0-9_]*)\1")


def split_heredocs(cmd):
    """(command text with heredoc bodies removed, [bodies fed to a shell]). A body fed to anything else
    (python, cat, tee ...) is data, not commands, so it is dropped from the scan."""
    lines = cmd.split("\n")
    keep, shell_bodies, i = [], [], 0
    while i < len(lines):
        line = lines[i]
        keep.append(line)
        i += 1
        for m in HEREDOC.finditer(line):
            delim, body = m.group(2), []
            while i < len(lines) and lines[i].strip() != delim:
                body.append(lines[i])
                i += 1
            i += 1                                   # the delimiter line
            head = line[:m.start()].split()
            words = [w for w in head if not re.match(r"^[A-Za-z_][A-Za-z0-9_]*=", w)]
            if words and os.path.basename(words[0]) in SHELLS and "-c" not in words:
                shell_bodies.append("\n".join(body))
    return "\n".join(keep), shell_bodies


def segments(cmd):
    """Quote-aware split on ; && || | and newlines. Yields each simple command's text, recursing into
    `bash -c '<script>'` and into heredoc bodies fed to a shell."""
    text, bodies = split_heredocs(cmd)
    segs, cur, q, i = [], [], None, 0
    while i < len(text):
        ch = text[i]
        if q:
            cur.append(ch)
            if ch == "\\" and q == '"' and i + 1 < len(text):
                cur.append(text[i + 1])
                i += 1
            elif ch == q:
                q = None
        elif ch in "'\"":
            q = ch
            cur.append(ch)
        elif ch == "\\" and i + 1 < len(text):
            cur.append(ch + text[i + 1])
            i += 1
        elif ch in ";|\n" or text.startswith("&&", i):
            segs.append("".join(cur))
            cur = []
            if text.startswith(("&&", "||"), i):
                i += 1
        else:
            cur.append(ch)
        i += 1
    segs.append("".join(cur))
    for seg in segs:
        seg = seg.strip()
        if not seg:
            continue
        yield seg
        try:
            tok = shlex.split(seg)
        except ValueError:
            continue
        words = [t for t in tok if not re.match(r"^[A-Za-z_][A-Za-z0-9_]*=", t)]
        if words and os.path.basename(words[0]) in SHELLS and "-c" in words:
            j = words.index("-c")
            if j + 1 < len(words):
                yield from segments(words[j + 1])
    for b in bodies:
        yield from segments(b)


def main():
    try:
        payload = json.load(sys.stdin)
        cmd = payload.get("tool_input", {}).get("command", "")
    except Exception:
        return 0                          # fail open

    if not cmd or "git" not in cmd:
        return 0

    for seg in segments(cmd):
        why = offence(seg)
        if not why:
            continue
        print(json.dumps({
            "hookSpecificOutput": {
                "hookEventName": "PreToolUse",
                "permissionDecision": "deny",
                "permissionDecisionReason": (
                    "Blocked by project house rule: %s.\n\n"
                    "Every helper in this seat clone shares its working tree AND "
                    "its index, so anything that is not path-scoped sweeps another "
                    "helper's unfinished work into your commit, under your "
                    "message.\n\n"
                    "Put the pathspec on the COMMIT, not just the add:\n"
                    "    git commit path/one.md path/two.xml -F - <<'EOF'\n\n"
                    "That bypasses the index entirely, so it cannot pick up a "
                    "peer's staged file no matter what lands mid-turn.\n\n"
                    "A brand-new file is a two-step, because `git commit "
                    "<path>` needs git to know the path first — but step two "
                    "still carries the pathspec:\n"
                    "    git add  path/new.md\n"
                    "    git commit path/new.md -F - <<'EOF'\n\n"
                    "Amending is unaffected: `git commit --amend` is allowed.\n"
                    "See CLAUDE.md > 'Commit explicit paths only'."
                    "\n\n\u26a0\ufe0f  NOTHING IN THAT COMMAND RAN \u2014 including anything BEFORE the "
                    "part that was\nrefused. A PreToolUse hook fires before the shell, so a compound "
                    "command is refused\nwhole. If you chained a file write to a commit, the write did "
                    "not happen either." % why
                ),
            }
        }))
        return 0
    return 0


if __name__ == "__main__":
    sys.exit(main())
