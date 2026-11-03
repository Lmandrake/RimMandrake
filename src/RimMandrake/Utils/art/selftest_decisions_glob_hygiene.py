#!/usr/bin/env python3
"""selftest_decisions_glob_hygiene.py — every file the `*.decisions.json` glob finds is a decisions doc enact can read.

enact, ingest and remap_decisions all glob Transient/biome_ffar/*.decisions.json. A file there that names no
snapshot, names a snapshot that is gone, or is not a decisions doc at all makes every one of those paths refuse
(DECISIONS_ORPHANS_PRUNE_NO_SNAPSHOT, 2026-10-24: three such files). This test holds the folder to the same head
checks build_plan makes (enact.py `build_plan`: schema, snapshot named, snapshot on disk) without paying for an
artledger Index, and checks the guard that stops remap_decisions.py --json writing its report over a ruling (how
phase0_remaining_art_sheet_2026-10-16.decisions.json was lost on 2026-10-22).
"""
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import decisions_v2 as DV  # noqa: E402

REPO = HERE.parents[3]
FOLDER = REPO / "Transient" / "biome_ffar"


def problems(f: Path) -> str | None:
    try:
        doc = json.loads(f.read_text())
    except ValueError as e:
        return f"not JSON: {e}"
    if not isinstance(doc, dict) or not isinstance(doc.get("decisions"), dict):
        return "not a decisions doc (no `decisions` map)"
    bad = DV.refuse_unknown(doc)
    if bad:
        return bad
    snap = doc.get("snapshot")
    if not isinstance(snap, str) or not snap.strip():
        return "names no snapshot"
    sp = Path(snap) if Path(snap).is_absolute() else REPO / snap
    if not sp.is_file():
        return f"snapshot missing: {snap}"
    return None


def main() -> int:
    fails = []
    files = sorted(FOLDER.glob("*.decisions.json"))
    if not files:  # an empty glob is a blind instrument, not a clean folder
        fails.append(f"no *.decisions.json under {FOLDER} — the instrument cannot see")
    for f in files:
        p = problems(f)
        if p:
            fails.append(f"{f.name}: {p}")
    # the three files the item named
    if (FOLDER / "tree_art_new_renders_sheet_2026-10-18.decisions.json").exists():
        fails.append("tree_art_new_renders_sheet_2026-10-18.decisions.json is back (its snapshot was deleted in 76e72b9156)")
    p0 = FOLDER / "phase0_remaining_art_sheet_2026-10-16.decisions.json"
    if p0.exists():
        d = json.loads(p0.read_text())
        if d.get("sheetId") != "phase0_remaining_art_sheet_2026-10-16" or len(d.get("decisions") or {}) != 20:
            fails.append("phase0 decisions doc is not his 20-row ruling restored from 6a0fa2c99a")
    # remap_decisions.py refuses a report path that the decisions glob would read (and that may be a ruling)
    with tempfile.TemporaryDirectory() as td:
        target = Path(td) / "x_sheet.decisions.json"
        target.write_text('{"keep": true}')
        r = subprocess.run([sys.executable, str(HERE / "remap_decisions.py"), "--json", str(target)],
                           capture_output=True, text=True, timeout=120)
        if r.returncode == 0 or target.read_text() != '{"keep": true}':
            fails.append(f"remap_decisions.py --json *.decisions.json was not refused (rc {r.returncode})")
        elif "must not be named" not in r.stderr:
            fails.append(f"remap_decisions.py refused for another reason: {r.stderr.strip()[-200:]}")
    for line in fails:
        print("FAIL", line)
    print(f"{'FAIL' if fails else 'PASS'}: {len(files)} decisions files checked, {len(fails)} problem(s)")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
