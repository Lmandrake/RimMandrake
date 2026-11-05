#!/usr/bin/env python3
"""dessic_install_check.py — is every finished dessic_* corpse render the live picture? (DESSICATED_CORPSES_INSTALL_AFTER_PICKS)

Reads only committed state: the art ledger (infrastructure/state/art/events/*.jsonl) and the tree.
For each `binding` event of a dessic_* job (a finished render bound to its slot), the job's
`install_to` (from its `variant kind=artpipe` event) must hold that render's sha256 — unless no
XML of ours draws that texPath any more (the def was cut or redrawn onto other art since), which
is reported as RETIRED, not as a failure.

Bytes alone do not prove the install went THROUGH art.py: a LIVE slot must also be the art ledger's current
live picture (artledger.Index().live, folded by causal prev) at that sha, and the ledger must hold a
type=live event for that slot and sha written by an art.py install path — `art.py install` (reason
"install" on a ruling, or "artpipe-collect" for a collected artpipe render) or the 2026-10-18 bulk accept (bulk_accept_renders.py, which calls artledger.install). A file
whose bytes match but whose slot has no such event is UNLEDGERED (a plain copy that bypassed art.py).

A render whose slot holds OTHER bytes that the owner kept (an active owner keep on the ledger's live picture
there, e.g. his 2026-11-03 "Simply accept all art as currently rendered" over a v2 drawn the next day) is
KEPT_OTHER: displacing kept art is his call, so it is reported, not failed.

Exit 0 when every bound render is LIVE, RETIRED or KEPT_OTHER; 1 when any is UNLEDGERED (right bytes, no art.py install event), STALE (other bytes at a path a
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

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import artledger as A  # noqa: E402

FACING = re.compile(r"_(east|west|north|south)$")
ART_PY_REASONS = ("install", "artpipe-collect")   # artledger.install on a ruling, or --reason artpipe-collect (art guard verifies it)
ART_PY_REASON_PREFIXES = ("script:src/RimMandrake/Utils/art/bulk_accept_renders.py bulk accept",)


def installed_through_art_py(ev: dict) -> bool:
    r = ev.get("reason") or ""
    return r in ART_PY_REASONS or r.startswith(ART_PY_REASON_PREFIXES)


def kept_other(index: "A.Index", path: str, cur: str) -> bool:
    """The slot holds another picture the owner KEPT (an unreleased owner keep on those bytes, and it is the
    ledger's live picture there): displacing kept art is his call (delegation_policy §2), so this render was
    passed over by his decision, not left uninstalled."""
    split = A.split_texture_path(path)
    led = index.live.get((A.mod_key(split[0]), A.rel_key(split[1]))) if split else None
    return bool(led and led.get("sha") == cur and index.protected(cur))


def repo_root() -> str:
    return os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))


def main() -> int:
    root = repo_root()
    os.chdir(root)
    events = A.read_events()          # every shard, archives included, deduped by id
    index = A.Index(events)
    slot_installs: dict[tuple, list] = {}
    for e in events:
        if e.get("type") == "live" and e.get("mod") and e.get("rel") and e.get("sha"):
            slot_installs.setdefault((A.mod_key(e["mod"]), A.rel_key(e["rel"])), []).append(e)
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
            split = A.split_texture_path(path)
            key = (A.mod_key(split[0]), A.rel_key(split[1])) if split else None
            led = index.live.get(key) if key else None
            via = [e for e in slot_installs.get(key, []) if e["sha"] == b["sha"] and installed_through_art_py(e)]
            if led is None or led.get("sha") != b["sha"] or not via:
                cls = "UNLEDGERED"
        elif not still_drawn:
            cls = "RETIRED"
        elif cur is not None and kept_other(index, path, cur):
            cls = "KEPT_OTHER"
        elif cur is None:
            cls = "MISSING"
        else:
            cls = "STALE"
        counts[cls] += 1
        if cls in ("STALE", "MISSING", "NO_INSTALL_TO", "UNLEDGERED"):
            bad.append((job, cls, path))
        if "-v" in sys.argv:
            print(cls, job, path)
    for job, cls, path in bad:
        print(f"{cls}: {job} -> {path}")
    print(f"dessic bindings={len(binding)} " + " ".join(f"{k}={v}" for k, v in sorted(counts.items())))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
