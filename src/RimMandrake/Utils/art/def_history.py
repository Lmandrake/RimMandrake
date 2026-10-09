#!/usr/bin/env python3
"""def_history.py — the recorded defName renames and deletions in git, as data for render_subjects.py.

    python3 def_history.py [--write]      (default: print counts; --write refreshes infrastructure/state/art/def_history.json)

A render whose job family names a def that no longer exists is either RENAMED (the same git hunk removes
`<defName>Old</defName>` and adds `<defName>New</defName>`, equal counts, paired in order) or DELETED (removed with
no re-add). The resolver only trusts a rename when the new name exists in the live def world, so a noisy pair is
inert. Regenerable; the file is tracked so the resolver needs no git at run time.
"""
from __future__ import annotations

import collections
import json
import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import artledger as L  # noqa: E402

OUT = L.REPO_ROOT / "infrastructure" / "state" / "art" / "def_history.json"
RX = re.compile(r"^([+-])\s*<defName>([^<]*)</defName>")


def scan() -> dict:
    p = subprocess.run(["git", "-C", str(L.REPO_ROOT), "log", "--format=#C# %h %ad %s", "--date=short", "-p", "-U0",
                        "-G<defName>", "--", "*.xml"], capture_output=True, text=True, errors="replace")
    ren, info = collections.defaultdict(set), {}
    plus_c, minus_c = collections.defaultdict(list), collections.defaultdict(list)
    cur, minus, plus = "", [], []

    def flush():
        nonlocal minus, plus
        if minus and len(minus) == len(plus):
            for a, b in zip(minus, plus):
                if a != b:
                    ren[a].add(b)
                    info.setdefault(f"{a}>{b}", cur)
        minus, plus = [], []
    for line in p.stdout.splitlines():
        if line.startswith("#C# "):
            flush()
            cur = line[4:]
            continue
        if line.startswith("@@"):
            flush()
            continue
        m = RX.match(line)
        if m:
            (minus if m.group(1) == "-" else plus).append(m.group(2))
            (minus_c if m.group(1) == "-" else plus_c)[m.group(2)].append(cur)
    flush()
    deleted = {}
    for dn, cs in minus_c.items():
        gone = [c for c in dict.fromkeys(cs) if c not in set(plus_c.get(dn, ()))]
        if gone:
            deleted[dn] = gone[0]          # newest first: the latest commit that removed it without re-adding
    # a hunk that pairs a removed def with an added one inside a DELETION commit is adjacency, not a rename
    junk = re.compile(r"\b(delet|cut|retire|remov|strike|purge)", re.I)
    for k in [k for k, c in info.items() if junk.search(c.split(" ", 2)[2] if c.count(" ") >= 2 else "")]:
        a, b = k.split(">", 1)
        ren[a].discard(b)
        del info[k]
    return {"renames": {a: sorted(b) for a, b in sorted(ren.items()) if b}, "rename_commit": info,
            "deleted": dict(sorted(deleted.items()))}


def load() -> dict:
    try:
        return json.loads(OUT.read_text())
    except (OSError, ValueError):
        return {"renames": {}, "rename_commit": {}, "deleted": {}}


def main(argv=None) -> int:
    d = scan()
    print(f"renames from {len(d['renames'])} old names; deletions {len(d['deleted'])}")
    if "--write" in (argv if argv is not None else sys.argv[1:]):
        OUT.write_text(json.dumps(d, indent=0, sort_keys=True))
        print("wrote", OUT)
    return 0


if __name__ == "__main__":
    sys.exit(main())
