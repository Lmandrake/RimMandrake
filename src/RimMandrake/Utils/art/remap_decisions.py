#!/usr/bin/env python3
"""remap_decisions.py — after a sheet rebuild, check every owner decision still names the SAME ART.

A decisions file names sets by column letter (decision, picks, variants). Letters are meant to be stable, but
the identity is the pictures (image shas in the snapshot). For each decisions file this takes the snapshot it
was ruled against (artledger.snapshot_by_id) and the current snapshot and classifies every used (row, letter):
  unchanged  the letter names the same pictures now
  remapped   the letter now names other pictures but the ruled pictures sit under another letter -> rewritten
  orphaned   the ruled pictures are gone from the row -> reported, never silently dropped (left as is)
Default is a dry run; --apply backs the file up (<name>.bak-<stamp>) then rewrites only remapped letters.
Purges are shas already, so they need no remap.
"""
from __future__ import annotations

import argparse
import json
import shutil
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import artledger as L  # noqa: E402

REPO = Path(__file__).resolve().parents[4]
SHEETS = REPO / "infrastructure/state/art/sheets"
OUT = REPO / "Transient/biome_ffar"


def classify(dec: dict, ruled: dict | None, now: dict):
    """Returns (stats, orphans, newmap{row:{oldletter:newletter}})."""
    st = {"unchanged": 0, "remapped": 0, "orphaned": 0, "no_ruled_snapshot": 0}
    orphans, newmap = [], {}
    for row, v in sorted((dec.get("decisions") or {}).items()):
        nc = ((now.get("rows") or {}).get(row) or {}).get("columns") or {}
        rc = (((ruled or {}).get("rows") or {}).get(row) or {}).get("columns") or {}
        for l in sorted(L.decision_letters(v)):
            if ruled is None:
                st["no_ruled_snapshot"] += 1
                continue
            if l not in rc:
                st["unchanged"] += 1      # nothing was ruled through a letter the ruled snapshot never had
            elif rc[l] == nc.get(l):
                st["unchanged"] += 1
            else:
                hit = next((k for k, f in nc.items() if f == rc[l]), None)
                if hit:
                    st["remapped"] += 1
                    newmap.setdefault(row, {})[l] = hit
                else:
                    st["orphaned"] += 1
                    orphans.append(f"{row}:{l}")
    return st, orphans, newmap


def apply_map(dec: dict, newmap: dict) -> None:
    for row, m in newmap.items():
        v = dec["decisions"][row]
        if (v.get("decision") or "") in m:
            v["decision"] = m[v["decision"]]
        if v.get("picks"):
            v["picks"] = {g: m.get(x, x) for g, x in v["picks"].items()}
        if v.get("variants"):
            v["variants"] = sorted({m.get(x, x) for x in v["variants"]})


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--json", help="write the per-sheet report here")
    a = ap.parse_args()
    rep = {}
    for dp in sorted(OUT.glob("*.decisions.json")):
        base = dp.name[:-len(".decisions.json")]
        sp = SHEETS / f"{base}.snapshot.json"
        if not sp.is_file():
            continue
        dec, now = json.loads(dp.read_text()), json.loads(sp.read_text())
        ruled = L.snapshot_by_id(sp, dec.get("snapshotId")) if dec.get("snapshotId") else None
        st, orphans, newmap = classify(dec, ruled, now)
        rep[base] = {**st, "orphans": orphans, "remap": newmap}
        if a.apply and newmap:
            shutil.copy2(dp, dp.with_name(dp.name + f".bak-{time.strftime('%Y%m%d-%H%M%S')}"))
            apply_map(dec, newmap)
            dp.write_text(json.dumps(dec, indent=1, sort_keys=True))
    for b, r in rep.items():
        print(f"{b:45s} unchanged {r['unchanged']:3d} remapped {r['remapped']:3d} orphaned {r['orphaned']:3d}"
              + (f" no-ruled-snapshot {r['no_ruled_snapshot']}" if r["no_ruled_snapshot"] else "")
              + (f"  ORPHANS {', '.join(r['orphans'][:8])}" if r["orphans"] else ""))
    if a.json:
        Path(a.json).write_text(json.dumps(rep, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
