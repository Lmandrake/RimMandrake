#!/usr/bin/env python3
"""PreToolUse/Bash hook + git pre-push guard — refuse texture PNG changes the art ledger
did not make (ART_VERSION_WRANGLING_1; owner green-lit by question card 2026-10-04).

WHY
===
Writers overwrote src/**/Textures in place with no ruling check and no copy of what they
replaced: 774 PNGs overwritten in 71 commits, ~327 with no cited ruling, and art the owner
had kept was lost under later renders (design/RimMandrake/art_ledger_design_2026-10-04.md §0).
`art.py install` / `artledger.install_bytes` is now the only sanctioned writer: it archives
the displaced bytes, refuses to move an owner-kept picture without his ruling, and appends a
`live` event. This guard refuses any PNG add/change/delete under src/**/Textures/ that is
not the end of an authorized `live` chain in the art ledger (rule: art_guard.check_change).

WHERE IT BITES
==============
  * `git commit` (pathspec or index) and `./publish -m ... <paths>`: the PNGs that commit
    would take, checked against the working-tree ledger; also refused if the ledger shard
    has uncommitted lines and is not part of the same commit (the event must travel with
    the bytes, or the push guard refuses later).
  * `git push` / bare `./publish`, and git-native `infrastructure/githooks/pre-push`
    (`--git-pre-push`): every non-merge commit in the pushed range, ledger read at the head.

Commits that touch no texture PNG are never examined. On a crash the guard fails OPEN,
except an unparseable ledger while PNGs are in play: then it fails CLOSED and says so —
a guard that cannot read the ledger cannot vouch for art.
"""
import json
import os
import re
import shlex
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ZERO = "0" * 40
COMMIT_VALUE_FLAGS = {"-m", "-F", "-C", "-c", "-t", "--author", "--date", "--fixup", "--squash",
                      "--trailer", "--message", "--file", "--template", "--reuse-message",
                      "--reedit-message", "--cleanup"}
FIX = ("Install art through the ledger instead of writing Textures/ directly:\n"
       "    python3 src/RimMandrake/Utils/art/art.py install <mod> <rel> <sha> --reason script:<writer>\n"
       "  (or --ruling <owner keep id>), or from a script: artledger.install_bytes(dest, data, reason=...).\n"
       "  Check by hand: python3 src/RimMandrake/Utils/art/art_guard.py worktree | range A..B")


def _root(cwd):
    r = subprocess.run(["git", "-C", cwd, "rev-parse", "--show-toplevel"], capture_output=True,
                       text=True, timeout=8)
    return r.stdout.strip() if r.returncode == 0 else None


def _guard(root):
    """Import art_guard bound to `root`'s ledger and src (a fixture repo in the selftest)."""
    os.environ["ART_LEDGER_DIR"] = os.path.join(root, "infrastructure", "state", "art")
    os.environ["ART_SRC_ROOT"] = os.path.join(root, "src")
    mod_dir = os.path.join(root, "src", "RimMandrake", "Utils", "art")
    if not os.path.isfile(os.path.join(mod_dir, "art_guard.py")):
        mod_dir = os.path.join(os.path.dirname(os.path.dirname(HERE)), "src", "RimMandrake", "Utils", "art")
    sys.path.insert(0, mod_dir)
    import art_guard  # noqa: E402
    return art_guard


def _fmt(bad):
    return "\n".join("  %s%s — %s" % ((c[:10] + " ") if c else "", p, why) for c, p, why in bad[:25]) + \
        ("\n  … %d more" % (len(bad) - 25) if len(bad) > 25 else "")


def check_push(root, base, head):
    g = _guard(root)
    return g.check_range(root, base, head)


def check_commit(root, paths):
    """paths None = index commit. Returns (bad, shard_problem)."""
    g = _guard(root)
    if paths is None:
        raw = subprocess.run(["git", "-C", root, "diff", "--cached", "--raw", "--no-renames", "-z"],
                             capture_output=True, text=True, timeout=30).stdout.split("\0")
        rows, i = [], 0
        while i < len(raw) - 1:
            if raw[i].startswith(":"):
                f = raw[i][1:].split()
                if g.is_texture_png(raw[i + 1]):
                    rows.append((raw[i + 1], f[2], f[3]))
                i += 2
            else:
                i += 1
        shas = g._sha256_blobs(root, [r[1] for r in rows] + [r[2] for r in rows])
        changes = [(p, shas.get(a), shas.get(b)) for p, a, b in rows]
    else:
        changes = g.worktree_changes(root, paths)
    if not changes:
        return [], None
    bad = [(None, p, why) for p, why in g.check(changes, g.L.read_events())]
    shard_problem = None
    if not bad:
        dirty = subprocess.run(["git", "-C", root, "status", "--porcelain", "--untracked-files=all", "--", g.LEDGER_EVENTS],
                               capture_output=True, text=True, timeout=30).stdout.split("\n")
        dirty = [d[3:] for d in dirty if len(d) > 3]
        if paths is None:
            staged = set(subprocess.run(["git", "-C", root, "diff", "--cached", "--name-only"],
                                        capture_output=True, text=True, timeout=30).stdout.split())
            missing = [d for d in dirty if d not in staged]
        else:
            norm = [os.path.normpath(p) for p in paths]
            missing = [d for d in dirty
                       if not any(os.path.normpath(d) == n or os.path.normpath(d).startswith(n + os.sep)
                                  for n in norm)]
        if missing:
            shard_problem = missing
    return bad, shard_problem


def pushed_head(cwd, refspec):
    """The commit a `git push <remote> <src>:<dst>` publishes: <src>, not HEAD
    (ART_LEDGER_SEAT_DEFAULT_1 — `git push origin <sha>:main` used to be checked
    against whatever HEAD happened to be). Falls back to HEAD."""
    src = (refspec or "").lstrip("+").split(":", 1)[0] if refspec else ""
    if src:
        r = subprocess.run(["git", "-C", cwd, "rev-parse", "--verify", "-q", src + "^{commit}"],
                           capture_output=True, text=True, timeout=8)
        if r.returncode == 0 and r.stdout.strip():
            return r.stdout.strip()
    return "HEAD"


def _push_range(cwd, args):
    positional = [a for a in args if not a.startswith("-")]
    remote, refspec = (positional + [None, None])[:2]
    cands = []
    if remote and refspec:
        dest = refspec.split(":", 1)[1] if ":" in refspec else refspec
        short = dest.lstrip("+").rsplit("/", 1)[-1]
        if short:
            cands.append("%s/%s" % (remote, short))
    cands += ["@{upstream}", "origin/main"]
    for c in cands:
        r = subprocess.run(["git", "-C", cwd, "rev-parse", "--verify", "-q", c],
                           capture_output=True, text=True, timeout=8)
        if r.returncode == 0:
            return c, pushed_head(cwd, refspec)
    return None


def _commit_paths(args):
    """pathspec of a `git commit`, or None for an index commit."""
    paths, i = [], 0
    while i < len(args):
        a = args[i]
        if a == "--":
            paths += args[i + 1:]
            break
        if a in COMMIT_VALUE_FLAGS:
            i += 2
            continue
        if a.startswith("-"):
            i += 1
            continue
        paths.append(a)
        i += 1
    return paths or None


def _deny(msg):
    print(json.dumps({"hookSpecificOutput": {
        "hookEventName": "PreToolUse", "permissionDecision": "deny",
        "permissionDecisionReason": "Blocked by project house rule: ART_VERSION_WRANGLING_1 — " + msg +
        "\n\nNOTHING IN THAT COMMAND RAN — a compound command is refused whole."}}))


def evaluate(cmd, cwd):
    """Returns a deny message or None."""
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
        where = cwd
        kind, args = None, []
        if tok[0] == "git":
            i = 1
            while i < len(tok) and tok[i].startswith("-"):
                if tok[i] == "-C" and i + 1 < len(tok):
                    where = os.path.join(cwd, tok[i + 1])
                    i += 2
                    continue
                i += 2 if tok[i] in ("-c", "--git-dir", "--work-tree") else 1
            if i < len(tok) and tok[i] in ("commit", "push"):
                kind, args = tok[i], tok[i + 1:]
        elif os.path.basename(tok[0]) == "publish":
            kind, args = "publish", tok[1:]
        elif len(tok) > 1 and tok[0].startswith("python") and tok[1].endswith("publish.py"):
            kind, args = "publish", tok[2:]
        if not kind:
            continue
        root = _root(where)
        if not root:
            continue
        try:
            if kind == "push" or (kind == "publish" and not _publish_paths(args)):
                rng = _push_range(root, args if kind == "push" else [])
                if not rng:
                    continue
                bad = check_push(root, *rng)
                shard = None
                if bad:
                    return ("this push carries texture PNG changes the art ledger did not make "
                            "(%s..%s):\n%s\n\n%s" % (rng[0], rng[1], _fmt(bad), FIX))
            else:
                paths = _commit_paths(args) if kind == "commit" else _publish_paths(args)
                bad, shard = check_commit(root, paths)
                if bad:
                    return ("this commit takes texture PNG changes the art ledger did not make:\n%s\n\n%s"
                            % (_fmt(bad), FIX))
                if shard:
                    return ("this commit takes ledger-installed PNGs but leaves their art-ledger "
                            "lines behind; add %s to the same commit." % " ".join(shard))
        except ValueError as e:      # unparseable ledger while PNGs are in play: fail closed
            return "the art ledger could not be read (%s); PNG commits wait until it parses." % e
        except Exception:
            continue                  # fail open
    return None


def _publish_paths(args):
    paths, i = [], 0
    while i < len(args):
        if args[i] in ("-m", "--message", "-F", "--file"):
            i += 2
            continue
        if not args[i].startswith("-"):
            paths.append(args[i])
        i += 1
    return paths


def git_pre_push(lines, cwd):
    root = _root(cwd)
    if not root:
        return 0
    for line in lines:
        parts = line.split()
        if len(parts) < 4 or parts[1] == ZERO:
            continue
        head, remote_sha = parts[1], parts[3]
        base = None
        for c in ([remote_sha] if remote_sha != ZERO else []) + ["origin/main"]:
            r = subprocess.run(["git", "-C", root, "rev-parse", "--verify", "-q", c + "^{commit}"],
                               capture_output=True, text=True, timeout=8)
            if r.returncode == 0:
                base = c
                break
        if base is None:
            continue
        try:
            bad = check_push(root, base, head)
        except ValueError as e:
            sys.stderr.write("pre-push REFUSED (ART_VERSION_WRANGLING_1): art ledger unreadable (%s)\n" % e)
            return 1
        if bad:
            sys.stderr.write("pre-push REFUSED (ART_VERSION_WRANGLING_1): texture PNG changes the art "
                             "ledger did not make (%s..%s):\n%s\n%s\n" % (base[:10], head[:10], _fmt(bad), FIX))
            return 1
    return 0


def main():
    if "--git-pre-push" in sys.argv:
        try:
            return git_pre_push(sys.stdin.read().splitlines(), os.getcwd())
        except Exception as e:
            sys.stderr.write("pre-push: art guard crashed, failing open: %r\n" % (e,))
            return 0
    try:
        payload = json.load(sys.stdin)
        cmd = payload.get("tool_input", {}).get("command", "")
        cwd = payload.get("cwd") or os.getcwd()
    except Exception:
        return 0
    if not cmd or not re.search(r"\bcommit\b|\bpush\b|publish", cmd):
        return 0
    msg = evaluate(cmd, cwd)
    if msg:
        _deny(msg)
    return 0


if __name__ == "__main__":
    sys.exit(main())
