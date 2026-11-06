#!/usr/bin/env python3
"""Clone-independent `required_checks.py --check` (VALIDATION_ROWRETURN_AUDIT_CHAINS_CUT_SHORT).

build() records a script's load_error verbatim, and for a validation.py with no module-level `suite` that
text embeds the ABSOLUTE path of the clone that ran it; build() then hashes it. So `--check` is red in any
clone but the one that wrote the manifest, though the manifest content is right. This proof rebuilds the
manifest, rewrites this clone's root inside load_error to the root the committed manifest recorded, and
requires (1) the per-mod content to equal the committed content exactly, (2) the hash build() would
compute over that content to equal the committed manifest_hash. Any added, lost or changed row (a
`return` restored inside a non-final row hides rows again) turns it red. Exit 0 current, 1 stale."""
import hashlib
import json
import os
import re
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _HERE)
import required_checks as rc  # noqa: E402

_ROOTED = re.compile(r"(/\S+?)/src/RimMandrake/")


def committed_root(mods):
    roots = {m.group(1) for row in mods.values() if row.get("load_error")
             for m in _ROOTED.finditer(row["load_error"])}
    if len(roots) > 1:
        raise SystemExit("committed manifest mixes roots %s" % sorted(roots))
    return roots.pop() if roots else None


def main():
    old = rc.load()
    man = rc.build()
    root = committed_root(old["mods"])
    here = rc.ROOT.rstrip("/")
    mods = man["mods"]
    if root and root != here:
        for row in mods.values():
            if row.get("load_error"):
                row["load_error"] = row["load_error"].replace(here + "/", root + "/")
    h = hashlib.sha256(json.dumps(mods, sort_keys=True).encode()).hexdigest()[:16]
    bad = []
    for mod in sorted(set(mods) | set(old["mods"])):
        if mods.get(mod) != old["mods"].get(mod):
            a = {c["id"] for c in (old["mods"].get(mod) or {}).get("checks", [])}
            b = {c["id"] for c in (mods.get(mod) or {}).get("checks", [])}
            bad.append("%s: +%s -%s" % (mod, sorted(b - a)[:5], sorted(a - b)[:5]))
    if bad or h != old.get("manifest_hash"):
        print("STALE: committed %s, current (root-normalised) %s; %d mod(s) differ" % (
            old.get("manifest_hash"), h, len(bad)))
        for b in bad[:20]:
            print("  " + b)
        return 1
    n = sum(len(r["checks"]) for r in mods.values())
    print("current %s (root %s -> %s), %d mods, %d checks" % (h, here, root, len(mods), n))
    return 0


if __name__ == "__main__":
    sys.exit(main())
