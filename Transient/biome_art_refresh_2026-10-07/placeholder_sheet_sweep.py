#!/usr/bin/env python3
"""Every candidate set on every served biome sheet (from the sheet snapshots), through the geometric placeholder
detector (owner rule 2026-10-07 22:33 PDT). Prints JSON {sheet: [{row, column, label, faces, reason}]} to stdout."""
import json
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "src/RimMandrake/Utils/art"))
import artledger as L  # noqa: E402
import placeholder_detect as PD  # noqa: E402

served = sorted(set(subprocess.run(["bash", "-c", "pgrep -af 'serve_sheet.py|serve_gated.py' | grep -o -- '--sheet [^ ]*' | cut -d' ' -f2"],
                                   capture_output=True, text=True).stdout.split()))
cache, out, unread = {}, {}, 0
for sh in served:
    sid = Path(sh).stem
    sp = L.ledger_dir() / "sheets" / f"{sid}.snapshot.json"
    if not sp.is_file():
        out[sid] = "UNMEASURED: no snapshot"
        continue
    snap = json.loads(sp.read_text())
    hits = []
    for row, r in (snap.get("rows") or {}).items():
        for letter, faces in (r.get("columns") or {}).items():
            shas = [s for s in (faces or {}).values() if s]
            if not shas:
                continue
            why = []
            for s in shas:
                if s not in cache:
                    try:
                        cache[s] = (PD.placeholder_reason(L.store_get(s)) or "") if L.store_has(s) else None
                    except Exception:  # noqa: BLE001
                        cache[s] = None
                if cache[s] is None:
                    unread += 1
                why.append(cache[s])
            if all(why):
                hits.append({"row": row, "column": letter, "label": (r.get("labels") or {}).get(letter, ""),
                             "faces": sorted(faces), "reason": why[0]})
    out[sid] = hits
print(json.dumps({"served": len(served), "pictures_checked": len(cache), "unreadable": unread, "sheets": out}, indent=1))
