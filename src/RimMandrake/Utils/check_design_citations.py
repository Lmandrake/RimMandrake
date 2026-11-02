#!/usr/bin/env python3
"""Check that every machinery name a design doc cites as EXISTING really exists.

A design pass names defs, classes and fields it means to build on. A name that was
guessed reads exactly like one that was read, so the doc carries a table:

    ## Cited machinery
    | name | root | ... |
    |---|---|---|
    | `TileMutatorWorker_AncientStructure` | vanilla | ... |

and this tool searches the named root for each name as a literal string:

    src      this repo's src/ (*.xml, *.cs, *.py)
    vanilla  the game's Data/ folder (Core + every DLC; *.xml)
    vef      Vanilla Expanded Framework, workshop 2023507013 (*.xml, *.dll)

Exit 0: every row resolves. Exit 1: a row does not, or the table is missing or
empty (an empty table proves nothing, so it fails). Exit 2: a root is unreadable.
Before trusting any row it runs a sanity probe per root: one name that must be
found and one canary that must not, so a blind search cannot pass vacuously.

Usage: python3 src/RimMandrake/Utils/check_design_citations.py <doc.md>
"""
import os
import re
import sys

SELF = os.path.abspath(__file__)
HERE = os.path.dirname(SELF)
REPO = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, HERE)
import game_paths as _GP  # noqa: E402  per-platform game path resolution

VEF_ID = "2023507013"
ROOTS = {
    "src": (os.path.join(REPO, "src"), (".xml", ".cs", ".py")),
    "vanilla": (_GP.GAME_DATA, (".xml",)),
    "vef": (os.path.join(_GP.WORKSHOP, VEF_ID), (".xml", ".dll")),
}
# (must be found, must NOT be found) per root. The canary is assembled at run time:
# written as one literal it would sit in this file, under src/, and be found.
CANARY = "RM_NoSuchDef" + "_canary_" + "qzx"
PROBES = {
    "src": ("RM_InhabitedPlace", CANARY),
    "vanilla": ("TileMutatorDef", CANARY),
    "vef": ("GenStep_CustomStructureGen", CANARY),
}
ROW = re.compile(r"^\|\s*`([^`]+)`\s*\|\s*([a-z]+)\s*\|")


def read_rows(doc):
    """Return [(name, root)] from the doc's '## Cited machinery' table."""
    rows, inside = [], False
    with open(doc, encoding="utf-8") as fh:
        for line in fh:
            if line.startswith("## "):
                inside = line.strip().lower() == "## cited machinery"
                continue
            if inside:
                m = ROW.match(line.strip())
                if m:
                    rows.append((m.group(1), m.group(2)))
    return rows


def load_root(root):
    """Return a list of file contents (bytes) under one root, or None if unreadable."""
    path, exts = ROOTS[root]
    if not os.path.isdir(path):
        return None
    blobs = []
    for dirpath, dirnames, filenames in os.walk(path):
        dirnames[:] = [d for d in dirnames if d not in (".git", "bin", "obj")]
        for fn in filenames:
            full = os.path.join(dirpath, fn)
            # This file names its probes; it must never satisfy its own search.
            if fn.lower().endswith(exts) and os.path.abspath(full) != SELF:
                try:
                    with open(full, "rb") as fh:
                        blobs.append(fh.read())
                except OSError:
                    continue
    return blobs or None


def found(blobs, name):
    needle = name.encode("utf-8")
    return any(needle in b for b in blobs)


def main(argv):
    if len(argv) != 2:
        print(__doc__.strip().splitlines()[-1])
        return 2
    doc = argv[1]
    rows = read_rows(doc)
    if not rows:
        print(f"FAIL: no rows in a '## Cited machinery' table in {doc}")
        return 1
    cache, bad = {}, 0
    for root in sorted({r for _, r in rows}):
        if root not in ROOTS:
            print(f"FAIL: unknown root '{root}' (known: {', '.join(ROOTS)})")
            return 1
        blobs = load_root(root)
        if blobs is None:
            print(f"UNREADABLE: root '{root}' at {ROOTS[root][0]}")
            return 2
        must, canary = PROBES[root]
        if not found(blobs, must) or found(blobs, canary):
            print(f"UNREADABLE: sanity probe failed on root '{root}' ({len(blobs)} files)")
            return 2
        cache[root] = blobs
    for name, root in rows:
        ok = found(cache[root], name)
        bad += not ok
        print(f"{'ok  ' if ok else 'MISS'} {root:8} {name}")
    print(f"{len(rows) - bad}/{len(rows)} cited names resolve")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
