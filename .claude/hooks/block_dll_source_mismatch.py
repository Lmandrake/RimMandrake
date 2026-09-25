#!/usr/bin/env python3
"""PreToolUse/Bash hook — refuse a `git push` that INTRODUCES a committed
mod DLL/source-stamp mismatch (DLL_SOURCE_STAMP_GUARD_1).

WHY
===
80 built DLLs are committed under src/**/Assemblies/. A DLL can't merge, so a
conflict on one is usually resolved by keeping one branch's DLL, which
silently drops the other branch's C# from the build (measured 2026-09-25:
five branch merges that day each carried a rebuilt/stale
src/RimMandrake/CreatureBehaviors/Assemblies/RimMandrake.CreatureBehaviors.dll).
src/Directory.Build.targets now stamps every DLL it builds with a
`.srchash` sidecar (a SHA256 per source file); this hook is the enforcement
point — it runs src/RimMandrake/Utils/dll_source_stamp.py over exactly the
commits a `git push` is about to publish, and refuses if any of them makes a
committed DLL disagree with its committed source.

Only mismatches INTRODUCED by the pushed range are refused — dll_source_stamp.py's
own `check --range A..B` already does that comparison (mismatch at B but not
at A), so this hook is a thin, non-judging wrapper: parse the push command,
resolve A..B, run the checker, relay a refusal if it found anything.

Fails OPEN on any parse/git/subprocess problem: a broken hook must never wedge
a push, and this guard is a safety net, not the source of truth (the source of
truth is the checker, runnable by hand any time:
`python3 src/RimMandrake/Utils/dll_source_stamp.py check --range A..B`).
"""
import json
import os
import re
import shlex
import subprocess
import sys

TAKES_ARG = {"-C", "-c", "--git-dir", "--work-tree", "--namespace", "--exec-path"}
DOTNET_CANDIDATES = [
    "/mnt/c/Users/Mandrake/.dotnet/dotnet.exe",
    "/mnt/c/Program Files/dotnet/dotnet.exe",
]


def git_dir_arg(tok):
    """The -C directory on a git command, if any (copied from
    block_shared_tree_merge.py's helper of the same name — keep them in sync
    if that parsing pattern changes)."""
    for j in range(1, len(tok) - 1):
        if tok[j] == "-C":
            return tok[j + 1]
        if not tok[j].startswith("-"):
            break
    return None


def push_argv(tok):
    """Args after `git push`, or None if `tok` is not a push."""
    i = 1
    while i < len(tok) and tok[i].startswith("-"):
        i += 1 if tok[i] not in TAKES_ARG else 2
    if i >= len(tok) or tok[i] != "push":
        return None
    return tok[i + 1:]


def resolve_range(cwd, args):
    """(base, head) rev-range this push is about to publish, or None if it
    cannot be determined (caller then fails open on this command)."""
    positional = [a for a in args if not a.startswith("-")]
    remote, refspec = (positional + [None, None])[:2]
    candidates = []
    if remote and refspec:
        dest = refspec.split(":", 1)[1] if ":" in refspec else refspec
        dest = dest.lstrip("+")
        short = dest.rsplit("/", 1)[-1]
        if short:
            candidates.append("%s/%s" % (remote, short))
    candidates.append("@{upstream}")
    for c in candidates:
        r = subprocess.run(["git", "-C", cwd, "rev-parse", "--verify", "-q", c],
                            capture_output=True, text=True, timeout=8)
        if r.returncode == 0:
            return (c, "HEAD")
    return None


def repo_root(cwd):
    r = subprocess.run(["git", "-C", cwd, "rev-parse", "--show-toplevel"],
                        capture_output=True, text=True, timeout=8)
    if r.returncode != 0:
        return None
    return r.stdout.strip()


def to_windows_path(root, rel_posix_path):
    """/mnt/d/Luke/... -> D:\\Luke\\... ; anything else -> best-effort backslash form."""
    full = os.path.join(root, rel_posix_path)
    if full.startswith("/mnt/") and len(full) > 6 and full[6] == "/":
        drive = full[5].upper()
        rest = full[7:].replace("/", "\\")
        return "%s:\\%s" % (drive, rest)
    return full.replace("/", "\\")


def project_for_dll(cwd, dll_repo_path, head_ref):
    """Reads the ".srchash" sidecar's own "# project: <path>" header at
    head_ref to name the csproj to rebuild — the authoritative source,
    rather than guessing a filename from convention."""
    stamp_path = dll_repo_path + ".srchash"
    r = subprocess.run(["git", "-C", cwd, "show", "%s:%s" % (head_ref, stamp_path)],
                        capture_output=True, text=True, timeout=8)
    if r.returncode != 0:
        return None
    first = r.stdout.splitlines()[:1]
    if not first or not first[0].startswith("# project:"):
        return None
    project_rel = first[0][len("# project:"):].strip()
    return "src/" + project_rel


def dotnet_exe():
    for c in DOTNET_CANDIDATES:
        if os.path.isfile(c):
            return c
    return DOTNET_CANDIDATES[0]


def find_mismatches(cwd, base, head):
    root = repo_root(cwd)
    if not root:
        return None
    script = os.path.join(root, "src", "RimMandrake", "Utils", "dll_source_stamp.py")
    if not os.path.isfile(script):
        return None  # guard not present on this branch yet — nothing to enforce
    r = subprocess.run(
        [sys.executable if sys.executable else "python3", script,
         "check", "--range", "%s..%s" % (base, head)],
        cwd=cwd, capture_output=True, text=True, timeout=25)
    if r.returncode == 0:
        return []
    if r.returncode != 1:
        return None  # the checker itself errored — fail open, don't refuse on noise
    flagged = []
    for line in r.stdout.splitlines():
        m = re.match(r"^(MISMATCH|STAMP_MISSING) (\S+)$", line)
        if m:
            flagged.append((m.group(1), m.group(2), root))
    return flagged


def main():
    try:
        payload = json.load(sys.stdin)
        cmd = payload.get("tool_input", {}).get("command", "")
        cwd = payload.get("cwd") or os.getcwd()
    except Exception:
        return 0
    if not cmd or "git" not in cmd or "push" not in cmd:
        return 0

    for seg in re.split(r"&&|\|\||[;|\n]", cmd):
        try:
            tok = shlex.split(seg.strip())
        except ValueError:
            continue
        if not tok:
            continue
        if tok[0] == "cd" and len(tok) > 1:
            cwd = os.path.join(cwd, os.path.expanduser(tok[1]))
            continue
        if tok[0] != "git":
            continue
        args = push_argv(tok)
        if args is None:
            continue
        where = git_dir_arg(tok)
        where = os.path.join(cwd, where) if where else cwd

        try:
            rng = resolve_range(where, args)
            if rng is None:
                continue
            base, head = rng
            flagged = find_mismatches(where, base, head)
        except Exception:
            return 0  # fail open

        if not flagged:
            continue

        root = flagged[0][2]
        lines = []
        for kind, dll, _root in flagged:
            csproj = project_for_dll(where, dll, head)
            if csproj:
                win = to_windows_path(root, csproj)
                fix = ('rebuild it: "%s" build "%s" -c Release, then '
                       "commit the .dll and its .dll.srchash together"
                       % (dotnet_exe(), win))
            else:
                fix = "rebuild the project that produces it and commit the .dll and its .dll.srchash together"
            reason = ("its committed source changed without a rebuild"
                      if kind == "MISMATCH" else
                      "the DLL changed but its .srchash sidecar did not")
            lines.append("  %s — %s (%s)" % (dll, fix, reason))

        print(json.dumps({"hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "deny",
            "permissionDecisionReason": (
                "Blocked by project house rule: DLL_SOURCE_STAMP_GUARD_1 — this push "
                "would introduce a committed mod DLL that disagrees with its committed "
                "C# source (%s..%s):\n\n%s\n\n"
                "This is exactly the failure that silently drops a branch's code on a "
                "DLL merge conflict (see CLAUDE.md's Git section) — the DLL you are "
                "about to publish would not be what its own source says it should be.\n\n"
                "Check by hand any time:\n"
                "    python3 src/RimMandrake/Utils/dll_source_stamp.py check --range %s..%s\n\n"
                "NOTHING IN THAT COMMAND RAN — a compound command is refused whole."
                % (base, head, "\n".join(lines), base, head)),
        }}))
        return 0
    return 0


if __name__ == "__main__":
    sys.exit(main())
