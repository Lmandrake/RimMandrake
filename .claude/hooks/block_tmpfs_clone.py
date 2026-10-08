#!/usr/bin/env python3
"""PreToolUse/Bash hook: refuse writing a repo copy or large tree onto a RAM disk.

WHY: /tmp, /dev/shm and /run are tmpfs on this machine. Their pages are RAM, charged to the
seat's cgroup. Six seat deaths 2026-10-01..10-07 trace to full clones / copies parked there
(design/RimMandrake/memory_clones_drives_2026-10-08.md, SEAT_MEMORY_CLONES_DRIVES_1).

Refuses (exit 2) when the TARGET is under /tmp, /dev/shm or /run:
  git clone ..., worktree add, cp -r/-a/-R and rsync of a git repo or repo-sized tree,
  git init <tmpfs> / git init in a tmpfs cwd when the same command fetches or adds a remote.
Relative targets resolve against the cwd and any `cd` in the command; $TMPDIR, $(mktemp -d) and
simple VAR=... assignments are expanded. Anything unresolvable is allowed (fail open).
Small /tmp use (echo > /tmp/f, --out /tmp/x.json, mktemp) is never touched.

    python3 .claude/hooks/selftest_block_tmpfs_clone.py
"""
import json
import os
import re
import shlex
import sys

TMPFS = ("/tmp", "/dev/shm", "/run")
REASON = (
    "Blocked: this writes a repo copy / large tree onto a RAM disk ({target}).\n\n"
    "/tmp, /dev/shm and /run are tmpfs: the pages are RAM charged to this seat's cgroup, and\n"
    "six seat deaths (2026-10-01..10-07) came from exactly this.\n"
    "To push work: `./publish -m \"subject\" <paths>` (Utils/publish.py builds the commit in a\n"
    "private index, no checkout needed). If a full copy is genuinely needed, clone onto ext4:\n"
    "  /home/mandrake/rm/scratch/<SEAT>/<name>\n"
    "Small scratch files in /tmp are fine. Doc: design/RimMandrake/memory_clones_drives_2026-10-08.md"
)
GIT_OPT_VAL = {"-C", "-c", "--git-dir", "--work-tree", "--namespace"}
CLONE_OPT_VAL = {"--reference", "--reference-if-able", "--depth", "-b", "--branch", "-o", "--origin",
                 "-c", "--config", "--separate-git-dir", "--template", "-j", "--jobs", "--filter",
                 "--shallow-since", "--shallow-exclude", "--server-option", "-u", "--upload-pack",
                 "--bundle-uri", "--ref-format"}
SKIP_FIRST = {"echo", "printf", "grep", "rg", "cat", "sed", "awk", "man", "which", "type"}
ASSIGN = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*=")


def is_tmpfs(p):
    return any(p == t or p.startswith(t + "/") for t in TMPFS)


def mktemp_sub(m):
    inner = m.group(1) or m.group(2) or ""
    mm = re.search(r"(?:-p\s+|--tmpdir=)(\S+)", inner)
    base = mm.group(1) if mm else os.environ.get("TMPDIR") or "/tmp"
    return base.rstrip("/") + "/mktemp.XXXXXX"


def expand(tok, env, cwd):
    """Expand a token to an absolute path, or None if it cannot be resolved."""
    def var(m):
        v = env.get(m.group(1) or m.group(2))
        return v if v is not None else "\x00"
    tok = re.sub(r"\$\{(\w+)\}|\$(\w+)", var, tok)
    if tok.startswith("~"):
        tok = os.path.expanduser(tok)
    if "\x00" in tok or "$" in tok or "`" in tok:
        return None
    if not os.path.isabs(tok):
        if cwd is None:
            return None
        tok = os.path.join(cwd, tok)
    return os.path.normpath(tok)


def segments(cmd):
    cmd = re.sub(r"\$\(\s*mktemp([^)]*)\)|`\s*mktemp([^`]*)`", mktemp_sub, cmd)
    cmd = cmd.replace("\n", " ; ")
    lex = shlex.shlex(cmd, posix=True, punctuation_chars=";&|()<>")
    lex.whitespace_split = True
    lex.commenters = ""
    seg, out = [], []
    for t in lex:
        if t and set(t) <= set(";&|()"):
            if seg:
                out.append(seg)
            seg = []
        elif t and set(t) <= set("<>"):
            seg.append("\x01")  # redirect marker; the next token is a file, not an argument
        else:
            seg.append(t)
    if seg:
        out.append(seg)
    return out


def repo_sized(path):
    try:
        if os.path.exists(os.path.join(path, ".git")):
            return True
        if os.path.isdir(path) and (path.startswith("/home/mandrake/rm/") or path.startswith("/mnt/d/Luke/dev")):
            return True
    except OSError:
        pass
    return False


def check(cmd, cwd0):
    """Return the offending target path, or None."""
    env = dict(os.environ)
    env.setdefault("TMPDIR", "/tmp")
    cwd = cwd0
    inits = []          # tmpfs dirs touched by `git init` / fetch
    fetches = False
    for seg in segments(cmd):
        seg = [t for i, t in enumerate(seg) if t != "\x01" and (i == 0 or seg[i - 1] != "\x01")]
        while seg and ASSIGN.match(seg[0]):
            k, _, v = seg.pop(0).partition("=")
            env[k] = expand(v, env, cwd) or v
        if not seg:
            continue
        if seg[0] == "cd":
            cwd = expand(seg[1], env, cwd) if len(seg) > 1 else os.path.expanduser("~")
            continue
        if seg[0] in SKIP_FIRST:
            continue
        idx = next((i for i, t in enumerate(seg[:8]) if os.path.basename(t) in ("git", "cp", "rsync")), None)
        if idx is None:
            continue
        prog, args, here = os.path.basename(seg[idx]), seg[idx + 1:], cwd
        if prog == "git":
            i = 0
            while i < len(args) and args[i].startswith("-"):
                if args[i] == "-C" and i + 1 < len(args):
                    here = expand(args[i + 1], env, here)
                i += 2 if args[i] in GIT_OPT_VAL else 1
            if i >= len(args):
                continue
            sub, rest = args[i], args[i + 1:]
            if sub in ("fetch", "pull") or (sub == "remote" and rest[:1] == ["add"]):
                fetches = True
                if here and is_tmpfs(here):
                    inits.append(here)
            elif sub == "clone":
                pos, j = [], 0
                while j < len(rest):
                    a = rest[j]
                    if a == "--":
                        pos += rest[j + 1:]
                        break
                    if a.startswith("-"):
                        j += 2 if a in CLONE_OPT_VAL else 1
                        continue
                    pos.append(a)
                    j += 1
                if not pos:
                    continue
                if len(pos) >= 2:
                    tgt = expand(pos[-1], env, here)
                else:
                    name = re.sub(r"\.git$", "", pos[0].rstrip("/").split("/")[-1].split(":")[-1])
                    tgt = os.path.join(here, name) if here else None
                if tgt and is_tmpfs(tgt):
                    return tgt
            elif sub == "worktree" and rest[:1] == ["add"]:
                pos = [a for a in rest[1:] if not a.startswith("-")]
                tgt = expand(pos[0], env, here) if pos else None
                if tgt and is_tmpfs(tgt):
                    return tgt
            elif sub == "init":
                pos = [a for a in rest if not a.startswith("-")]
                tgt = expand(pos[-1], env, here) if pos else here
                if tgt and is_tmpfs(tgt):
                    inits.append(tgt)
        else:
            flags = [a for a in args if a.startswith("-") and not a.startswith("--")]
            longs = [a for a in args if a.startswith("--")]
            letters = "rRa" if prog == "cp" else "ra"
            rec = any(re.search("[" + letters + "]", f) for f in flags) or "--recursive" in longs or "--archive" in longs
            if not rec:
                continue
            pos = [a for a in args if not a.startswith("-")]
            if len(pos) < 2:
                continue
            tgt = expand(pos[-1], env, cwd)
            if not (tgt and is_tmpfs(tgt)):
                continue
            for s in pos[:-1]:
                sp = expand(s.rstrip("/") or "/", env, cwd)
                if sp and repo_sized(sp):
                    return tgt
    if fetches and inits:
        return inits[0]
    return None


def main():
    try:
        ev = json.load(sys.stdin)
    except Exception:
        return 0
    if ev.get("tool_name") != "Bash":
        return 0
    cmd = str((ev.get("tool_input") or {}).get("command") or "")
    cwd = ev.get("cwd") or os.getcwd()
    try:
        tgt = check(cmd, cwd)
    except Exception:
        return 0  # fail open
    if tgt:
        print(REASON.format(target=tgt), file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
