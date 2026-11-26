#!/usr/bin/env python3
"""owner_objections.py — count the owner's typed blocks in conversation records that match a named objection.

    python3 src/RimMandrake/Utils/owner_objections.py <conversations dir> <start YYYY-MM-DD> <end YYYY-MM-DD> [--rev REV]

A record is in the window when its file-name date (the session start, UTC) lies in [start, end]. A block counts when
it is a `## Lukas` block he typed: card answers, machine prompts and helper briefs are dropped by prefix, as are blocks
over 3,000 characters (pasted material). --rev reads the records as they were at that commit (git), so a measurement
taken once stays reproducible while records keep arriving.

Made by Crystallize 2026-W47 (sweeps lane); it measures the success criterion of
`design/RimMandrake/standing_rulings.md` §No limit without the danger it guards: `arbitrary_limit` read 8 blocks in 7
records for 2026-11-05..2026-11-19 (selftest_owner_objections.py pins that). Exit 0 with the counts; exit 2 when the
records could not be read (a missing directory or revision is not a count of zero).
"""
import re
import subprocess
import sys
from pathlib import Path

MACHINE = re.compile(r"^(\[Rim|You are|<task-notification>|<cross-session-message|# |Brief:|<system-reminder>|<command-|Caveat:|This session is being continued|\[Request interrupted|<local-command|Base directory|Ledger item:|\[SYSTEM|\[Seat|\[Dispatcher|\[Operations|\[Conductor|DESKTOP|<<<|_\(card answer\)_|_\(ran |<agent-message|This instruction carries|Your verdict|These refusal records|The spend watchdog|wake\. Fresh|Build item|Fix ledger item|Night order|Item[: ]|Make src/|Two items marked|The Conductor restarted you|This is a test of)", re.I)
PATTERNS = {
    "arbitrary_limit": r"arbitrary (pause|pacing|rule|cut|limit)s?|time limits?\b|no caps|pacing control|why must we wait|cut off text|why is there even such a|reason to limit|why is \S+ a limit",
    "account_list": r"(codex|account).{0,80}(again|forgot|didn't quote|did not quote)|always quote codex|how much is left|not how much (we've|you've) used",
    "fix_it_now": r"fix it,? right then|do it now|you do it now|just fix|fix (it|this) (yourself|now)|don't just (watch|diagnose)|just get it done",
}


def count(records, start, end):
    """records: iterable of (file name, text) -> (typed blocks, {pattern: [file name per matching block]})."""
    n = 0
    hits = {k: [] for k in PATTERNS}
    for name, text in sorted(records):
        if not (start <= name[:10] <= end):
            continue
        parts = re.split(r"^## (Lukas|Claude)\s*$", text, flags=re.M)
        for i in range(1, len(parts), 2):
            b = parts[i + 1].strip()
            if parts[i] != "Lukas" or not b or MACHINE.match(b) or len(b) > 3000 or "You are a DETACHED helper" in b:
                continue
            n += 1
            for k, p in PATTERNS.items():
                if re.search(p, b, re.I):
                    hits[k].append(name)
    return n, hits


def records_in_dir(root):
    root = Path(root)
    if not root.is_dir():
        raise OSError("no conversations directory at %s" % root)
    return [(f.name, f.read_text(errors="replace")) for f in root.glob("*.md")]


# A git call can hang (a held index.lock, a slow drvfs mount: lesson
# 20261119T084833Z-BENCH-git-index-lock-file-exists-refusal); a hung read becomes "could not look", never a stuck
# selftest. 600 s is far past a measured read of the whole window (about 1 s, 2026-11-19).
GIT_TIMEOUT_S = 600


def records_at_rev(root, rev, start, end):
    """The window's records as they were at commit rev, read with one git cat-file --batch."""
    try:
        return _records_at_rev(root, rev, start, end)
    except subprocess.TimeoutExpired as e:
        raise OSError("git did not answer within %d s: %s" % (GIT_TIMEOUT_S, " ".join(e.cmd)))


def _records_at_rev(root, rev, start, end):
    root = Path(root)
    repo = subprocess.run(["git", "-C", str(root), "rev-parse", "--show-toplevel"], capture_output=True, text=True,
                          timeout=GIT_TIMEOUT_S)
    if repo.returncode:
        raise OSError("not in a git repo: %s" % root)
    top = repo.stdout.strip()
    rel = str(root.resolve().relative_to(Path(top).resolve()))
    ls = subprocess.run(["git", "-C", top, "ls-tree", "--name-only", rev, rel + "/"], capture_output=True, text=True,
                        timeout=GIT_TIMEOUT_S)
    if ls.returncode:
        raise OSError("revision %s not readable: %s" % (rev, ls.stderr.strip()))
    paths = [p for p in ls.stdout.split() if p.endswith(".md") and start <= Path(p).name[:10] <= end]
    if not paths:
        return []
    cat = subprocess.run(["git", "-C", top, "cat-file", "--batch"], input="".join("%s:%s\n" % (rev, p) for p in paths).encode(),
                         capture_output=True, timeout=GIT_TIMEOUT_S)
    if cat.returncode:
        raise OSError("git cat-file failed: %s" % cat.stderr.decode(errors="replace").strip())
    out, pos, recs = cat.stdout, 0, []
    for p in paths:
        nl = out.index(b"\n", pos)
        head = out[pos:nl].split()
        if len(head) < 3 or head[1] != b"blob":
            raise OSError("git cat-file could not read %s:%s" % (rev, p))
        size = int(head[2])
        recs.append((Path(p).name, out[nl + 1:nl + 1 + size].decode(errors="replace")))
        pos = nl + 1 + size + 1
    return recs


def main(argv=None):
    a = list(sys.argv[1:] if argv is None else argv)
    rev = None
    if "--rev" in a:
        i = a.index("--rev")
        rev = a[i + 1]
        del a[i:i + 2]
    if len(a) != 3:
        print(__doc__.strip().splitlines()[2].strip(), file=sys.stderr)
        return 2
    root, start, end = a
    try:
        recs = records_at_rev(root, rev, start, end) if rev else records_in_dir(root)
    except (OSError, ValueError) as e:
        print("COULD NOT LOOK: %s" % e, file=sys.stderr)
        return 2
    n, hits = count(recs, start, end)
    print(f"{start}..{end}: {n} typed blocks")
    for k, v in hits.items():
        print(f"  {k}: {len(v)} blocks in {len(set(v))} records")
    return 0


if __name__ == "__main__":
    sys.exit(main())
