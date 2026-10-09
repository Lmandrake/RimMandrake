#!/usr/bin/env python3
"""orphan_masters.py — find derive_from masters whose done manifest exists but whose
PNG is missing from _artsrc/<id>/<id>.png. claim_next HOLDS every derived job on such
a master forever (see artpiped._derive_master_resolved). Read-only: reports counts and
CANDIDATE source paths, never restores anything.

    python3 orphan_masters.py [--md PATH]
"""
from __future__ import annotations
import argparse, json, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import state_dir  # noqa: E402


def _job_files(d: Path):
    return [p for p in d.glob("*.json") if not p.name.endswith(".manifest.json")] if d.is_dir() else []


def scan(root: Path, repo: Path = state_dir.REPO_ROOT) -> dict:
    masters: dict[str, set[str]] = {}
    for sub in ("pending", "active", "done"):
        for p in _job_files(root / sub):
            try:
                df = json.loads(p.read_text()).get("derive_from")
            except (OSError, ValueError):
                continue
            if isinstance(df, str) and df:
                masters.setdefault(df, set()).add(f"{sub}/{p.name}")
    rows, present = [], []
    for m, users in sorted(masters.items()):
        has_manifest = (root / "done" / f"{m}.manifest.json").is_file()
        png = root / "_artsrc" / m / f"{m}.png"
        if has_manifest and png.is_file():
            present.append(m)
        elif has_manifest:
            cands = []
            old = repo / "infrastructure" / "artpipe" / "_artsrc" / m / f"{m}.png"
            if old.is_file():
                cands.append(str(old))
            # The worker's own reported `out` — a pre-2026-10-02 job names the
            # retired D:\Luke\dev\Rimworld\infrastructure\artpipe tree, which the
            # `old` path above (relative to THIS clone) never reaches.
            try:
                wout = (json.loads((root / "done" / f"{m}.manifest.json").read_text())
                        .get("worker_self_report") or {}).get("out")
            except (OSError, ValueError, AttributeError):
                wout = None
            if isinstance(wout, str) and len(wout) > 2 and wout[1] == ":":
                wp = Path("/mnt") / wout[0].lower() / wout[3:].replace("\\", "/")
                if wp.is_file() and str(wp) not in cands:
                    cands.append(str(wp))
            cands += [str(c) for c in list((repo / "src").glob(f"**/Textures/**/{m}*.png"))[:5]]
            rows.append((m, sorted(users), cands))
    return {"masters": len(masters), "present": present, "orphans": rows}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--md", default=str(state_dir.REPO_ROOT / "Transient" / "artpipe_orphan_masters.md"))
    a = ap.parse_args(argv)
    root = state_dir.require() if hasattr(state_dir, "require") else state_dir.resolve()
    r = scan(root)
    if not r["present"]:
        print("SANITY PROBE FAILED: no master found present — instrument cannot see _artsrc", file=sys.stderr)
        return 2
    probe = r["present"][0]
    lines = ["# artpipe orphan masters", "",
             f"- derive_from masters seen: {r['masters']}",
             f"- present (done manifest + PNG): {len(r['present'])}  (sanity probe: {probe} found present)",
             f"- ORPHAN (done manifest, PNG missing): {len(r['orphans'])}", ""]
    for m, users, cands in r["orphans"]:
        lines.append(f"- {m}: used by {len(users)} job(s); candidates: {cands or 'none found'}")
    Path(a.md).write_text("\n".join(lines) + "\n")
    print(f"masters={r['masters']} present={len(r['present'])} orphans={len(r['orphans'])} -> {a.md}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
