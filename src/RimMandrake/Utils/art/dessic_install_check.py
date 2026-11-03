#!/usr/bin/env python3
"""dessic_install_check.py — is every finished dessic_* corpse render the live picture? (DESSICATED_CORPSES_INSTALL_AFTER_PICKS)

Reads only committed state: the art ledger (infrastructure/state/art/events/*.jsonl) and the tree.
For each `binding` event of a dessic_* job (a finished render bound to its slot), the job's
`install_to` (from its `variant kind=artpipe` event) must hold that render's sha256 — unless no
XML of ours draws that texPath any more (the def was cut or redrawn onto other art since), which
is reported as RETIRED, not as a failure.

Exit 0 when every bound render is LIVE or RETIRED; 1 when any is STALE (other bytes at a path a
def still draws) or MISSING (a path a def still draws has no file); 2 when the instrument is blind
(no dessic bindings found — a zero here is a query bug, never a pass).
"""
from __future__ import annotations

import glob
import hashlib
import json
import os
import re
import sys
from collections import Counter

FACING = re.compile(r"_(east|west|north|south)$")


def repo_root() -> str:
    return os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))


def main() -> int:
    root = repo_root()
    os.chdir(root)
    events = []
    for f in sorted(glob.glob("infrastructure/state/art/events/*.jsonl")):
        with open(f, encoding="utf-8") as fh:
            events += [json.loads(line) for line in fh if line.strip()]
    binding = {e["job"]: e for e in events
               if e.get("type") == "binding" and str(e.get("job", "")).startswith("dessic_")}
    install_to = {e["job"]: e["install_to"] for e in events
                  if e.get("kind") == "artpipe" and str(e.get("job", "")).startswith("dessic_") and e.get("install_to")}
    if not binding:
        print("BLIND: no dessic_* binding events in the art ledger")
        return 2

    drawn: set[str] = set()
    tp = re.compile(r"<texPath>\s*([^<\s]+)\s*</texPath>")
    for x in glob.glob("src/**/*.xml", recursive=True):
        with open(x, encoding="utf-8", errors="replace") as fh:
            drawn.update(tp.findall(fh.read()))

    counts: Counter[str] = Counter()
    bad = []
    for job, b in sorted(binding.items()):
        path = install_to.get(job)
        if not path:
            counts["NO_INSTALL_TO"] += 1
            bad.append((job, "NO_INSTALL_TO", "-"))
            continue
        tex = b["texpath"]
        still_drawn = tex in drawn or FACING.sub("", tex) in drawn
        if os.path.isfile(path):
            with open(path, "rb") as fh:
                cur = hashlib.sha256(fh.read()).hexdigest()
        else:
            cur = None
        if cur == b["sha"]:
            cls = "LIVE"
        elif not still_drawn:
            cls = "RETIRED"
        elif cur is None:
            cls = "MISSING"
        else:
            cls = "STALE"
        counts[cls] += 1
        if cls in ("STALE", "MISSING", "NO_INSTALL_TO"):
            bad.append((job, cls, path))
        if "-v" in sys.argv:
            print(cls, job, path)
    for job, cls, path in bad:
        print(f"{cls}: {job} -> {path}")
    print(f"dessic bindings={len(binding)} " + " ".join(f"{k}={v}" for k, v in sorted(counts.items())))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
