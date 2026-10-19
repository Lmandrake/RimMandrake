#!/usr/bin/env python3
"""No two tracked paths may differ only by letter case.

Windows and macOS are case-insensitive: a clone there cannot hold both `PaleTree_B.png` and `PaleTree_b.png`, so
one silently shadows the other (the Mac laptop needed an ignore rule). Retired 2026-10-18 (4c8371290), re-added
2026-10-19 04:07 by bulk_accept_renders.py (681aca61b), retired again with a guard in artledger.install.
This test is the git-level backstop for every writer that is not the art ledger.

    python3 src/RimMandrake/Utils/selftest_no_case_twins.py          # exit 1 and list twins when any exist
Importable: `case_twins(paths)` -> [[path, path, ...], ...]  (used by donor_regen_install_hourly.py before commit).
"""
import subprocess
import sys
from collections import defaultdict
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]


def case_twins(paths):
    """Groups of paths (files AND their parent folders) that collide ignoring case."""
    seen = defaultdict(set)
    for p in paths:
        parts = p.split("/")
        for i in range(1, len(parts) + 1):
            sub = "/".join(parts[:i])
            seen[sub.casefold()].add(sub)
    groups = [sorted(v) for v in seen.values() if len(v) > 1]
    # a colliding folder makes every path under it collide too; report only the shallowest collision
    groups.sort(key=lambda g: (g[0].count("/"), g))
    out, roots = [], []
    for g in groups:
        if any(x.casefold().startswith(r + "/") for r in roots for x in g):
            continue
        roots.append(g[0].casefold())
        out.append(g)
    return out


def tracked(repo=REPO):
    r = subprocess.run(["git", "-C", str(repo), "ls-files", "-z"], capture_output=True, check=True)
    return [p for p in r.stdout.decode("utf-8", "surrogateescape").split("\0") if p]


def _self_check():
    assert case_twins(["a/B.png", "a/b.png", "a/c.png"]) == [["a/B.png", "a/b.png"]]
    assert case_twins(["X/a.png", "x/b.png"]) == [["X", "x"]]
    assert case_twins(["a/b.png", "a/c.png"]) == []
    # the lowest writer refuses too: artledger.install's case_twin_refusal
    import tempfile
    sys.path.insert(0, str(REPO / "src/RimMandrake/Utils/art"))
    import artledger
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        (root / "M/Textures/P").mkdir(parents=True)
        (root / "M/Textures/P/Tree_b.png").write_bytes(b"x")
        assert "CASE-TWIN" in (artledger.case_twin_refusal(root / "M/Textures/P/Tree_B.png", root) or "")
        assert "CASE-TWIN" in (artledger.case_twin_refusal(root / "M/Textures/p/Tree_c.png", root) or "")
        assert artledger.case_twin_refusal(root / "M/Textures/P/Tree_b.png", root) is None
        assert artledger.case_twin_refusal(root / "M/Textures/P/Tree_c.png", root) is None


def main():
    _self_check()
    files = tracked()
    assert len(files) > 1000, f"git ls-files returned {len(files)} paths — the instrument is blind"
    twins = case_twins(files)
    if twins:
        print(f"FAIL: {len(twins)} case-insensitive duplicate path group(s) in git — Windows/macOS clones cannot hold them:")
        for g in twins:
            print("  " + "  |  ".join(g))
        print("Retire one spelling through the art ledger (artledger.retire) or `git rm` it; keep the KEPT picture.")
        return 1
    print(f"PASS: no case-twin paths among {len(files)} tracked files")
    return 0


if __name__ == "__main__":
    sys.exit(main())
