#!/usr/bin/env python3
"""Git pre-push guard: refuse a push that adds item prose its own ledger cannot account for.

    infrastructure/githooks/pre-push runs this as: block_orphan_item_prose.py --git-pre-push
    .claude/settings.json runs it bare as a PreToolUse/Bash hook on `git push` and `./publish`

`infrastructure/state/items/*.md` is the live glob, and selftest_items_glob_live.py reddens the nightly when a file there
has no ledger row. 6489a12285 pushed two items' prose with no row and no `rimflow file`, and the sweep went red 12 hours
later (NIGHTLY_COP_FIX_RED_ATJKEB_FBYD). The guard applies the same verdict at the door, to each file the push adds,
against the ledger IN THE PUSHED COMMIT: a row sitting uncommitted in this clone's shard does not reach origin, so it does
not count. Fix a refusal by filing the item (`rimflow file`) and committing the seat's shard in the same push.

The pre-push mode is the door: `./publish`, plain shells and timers all reach `git push`; exit 1 refuses. The PreToolUse mode
only refuses sooner, for commits already waiting in the clone, before an agent spends a rebase and a push on them. Either mode
fails open on a crash and says so on stderr.
"""
import json
import os
import posixpath
import re
import shlex
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ZERO = "0" * 40
ITEMS = "infrastructure/state/items"
LEDGER_HISTORY = "infrastructure/state/ledger/events.jsonl"
LEDGER_SHARDS = "infrastructure/state/ledger/events"
REFUSAL = ("REFUSED (orphan item prose): the pushed ledger has no live row for:\n%s\n"
           "File each with `rimflow file` and commit infrastructure/state/ledger/events/<SEAT>.jsonl in this push.\n")


def git(root, *args):
    r = subprocess.run(["git", "-C", root] + list(args), capture_output=True, text=True, timeout=120)
    if r.returncode:
        raise RuntimeError("git %s: %s" % (" ".join(args), r.stderr.strip()))
    return r.stdout


def added_prose(root, base, head):
    """-> item stems whose top-level items/<stem>.md is new on head's side of base. items/closed/ never counts."""
    names = git(root, "diff", "--name-only", "--no-renames", "--diff-filter=A", "-z", "%s...%s" % (base, head), "--", ITEMS)
    return sorted(posixpath.basename(n)[:-3] for n in names.split("\0")
                  if posixpath.dirname(n) == ITEMS and n.endswith(".md"))


def ledger_at(root, head):
    """-> every event of the ledger as committed at `head`. An unreadable ledger raises: it cannot vouch for anything."""
    listed = git(root, "ls-tree", "-r", "--name-only", "-z", head, "--", LEDGER_HISTORY, LEDGER_SHARDS).split("\0")
    events = []
    for path in sorted(n for n in listed if n.endswith(".jsonl")):
        for line in git(root, "show", "%s:%s" % (head, path)).splitlines():
            if line.strip():
                try:
                    events.append(json.loads(line))
                except ValueError:
                    pass                 # ledger_lint owns a malformed line; the rest of the ledger still reads
    if not events:
        raise RuntimeError("no ledger events readable at %s" % head)
    return events


def rimflow_modules(root):
    """-> (model, the selftest holding the verdict), from `root`, else from the clone holding this hook."""
    for base in (root, os.path.dirname(os.path.dirname(HERE))):
        pkg = os.path.join(base, "src", "RimMandrake")
        if os.path.isfile(os.path.join(pkg, "rimflow", "model.py")):
            sys.path.insert(0, os.path.join(pkg, "rimflow"))
            sys.path.insert(0, pkg)
            from rimflow import model
            import selftest_items_glob_live as glob_live
            return model, glob_live
    raise RuntimeError("rimflow not found from %s" % root)


def orphans(root, base, head):
    """-> [(stem, why)] for each item file the push adds that the pushed ledger cannot account for."""
    stems = added_prose(root, base, head)
    if not stems:
        return []                        # the common push: never pays for a ledger replay
    model, glob_live = rimflow_modules(root)
    state = model.replay(model.canonical_order(ledger_at(root, head)))
    return [(stem, why) for stem, why in ((s, glob_live.verdict(s, state)) for s in stems) if why]


def base_of(root, remote_sha):
    """-> the commit to diff against: the remote's tip when this clone has it, else origin/main, else None."""
    for c in ([remote_sha] if remote_sha != ZERO else []) + ["origin/main"]:
        r = subprocess.run(["git", "-C", root, "rev-parse", "--verify", "-q", c + "^{commit}"],
                           capture_output=True, text=True, timeout=8)
        if r.returncode == 0:
            return c
    return None


def git_pre_push(lines, cwd):
    root = git(cwd, "rev-parse", "--show-toplevel").strip()
    for line in lines:
        parts = line.split()
        if len(parts) < 4 or parts[1] == ZERO:
            continue
        base = base_of(root, parts[3])
        if base is None:
            continue
        bad = orphans(root, base, parts[1])
        if bad:
            sys.stderr.write("pre-push " + REFUSAL % "\n".join("  %s.md: %s" % row for row in bad))
            return 1
    return 0


def landing_dir(cmd, cwd):
    """-> the directory a `git push` or `publish` in this command acts on, or None when it has neither."""
    for seg in re.split(r"&&|\|\||[;|\n]", cmd):
        try:
            tok = shlex.split(seg.strip())
        except ValueError:
            continue
        if not tok:
            continue
        if tok[0] == "cd" and len(tok) > 1:
            cwd = os.path.join(cwd, os.path.expanduser(tok[1]))
        elif os.path.basename(tok[0]) == "publish" or (tok[0].startswith("python") and tok[1:2] and tok[1].endswith("publish.py")):
            return cwd
        elif tok[0] == "git" and "push" in tok[1:]:
            return os.path.join(cwd, tok[tok.index("-C") + 1]) if "-C" in tok[:-1] else cwd
    return None


def pre_tool_use(payload):
    """Deny the landing when commits already waiting in the clone would be refused at pre-push anyway."""
    where = landing_dir(payload.get("tool_input", {}).get("command", ""), payload.get("cwd") or os.getcwd())
    if not where:
        return
    root = git(where, "rev-parse", "--show-toplevel").strip()
    bad = orphans(root, "origin/main", "HEAD")
    if bad:
        print(json.dumps({"hookSpecificOutput": {
            "hookEventName": "PreToolUse", "permissionDecision": "deny",
            "permissionDecisionReason": REFUSAL % "\n".join("  %s.md: %s" % row for row in bad)
            + "NOTHING IN THAT COMMAND RAN: a compound command is refused whole."}}))


def main():
    pre_push = "--git-pre-push" in sys.argv
    try:
        if pre_push:
            return git_pre_push(sys.stdin.read().splitlines(), os.getcwd())
        pre_tool_use(json.load(sys.stdin))
    except Exception as e:
        sys.stderr.write("pre-push: orphan item prose guard crashed, failing open: %r\n" % (e,))
    return 0


if __name__ == "__main__":
    sys.exit(main())
