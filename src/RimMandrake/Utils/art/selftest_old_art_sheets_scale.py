#!/usr/bin/env python3
"""selftest_old_art_sheets_scale.py — OLD_ART_SHEETS_REBUILD_WITH_SCALE_PANELS, proven from COMMITTED files only.

The two sheets the scale gate refused in October:
  sluice_panning_warden   rebuilt with `art_sheet.py --subjects` as sluice_panning_warden_sheet_2026-10-11; the gated
                          HTML and every image it shows are pinned in Transient/biome_ffar (transient_pin.py), so
                          this reads them without the art store or the artpipe (both live under the data root).
  sheet_conflicts_review_2026-10-09   finished, not rebuilt: its HTML is gone and every one of its rows was folded
                          into the biome sheets' decisions files with a `conflictSheet` record (commit 4822a83637).

Reads nothing outside the repo, needs no git history. The art modules resolve the data root at IMPORT time, so an
unset RM_DATA_ROOT is pointed at an empty temp dir first: nothing here reads it, and a check that silently needed
it would then fail loudly instead of passing on a populated store.
"""
from __future__ import annotations

import json
import os
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
if not os.environ.get("RM_DATA_ROOT"):
    os.environ["RM_DATA_ROOT"] = tempfile.mkdtemp(prefix="oldsheets_noroot_")
sys.path.insert(0, str(HERE))
import scaled_review_gate as G  # noqa: E402

SHEET_DIR = REPO / "Transient" / "biome_ffar"
SLUICE = "sluice_panning_warden_sheet_2026-10-11"
CONFLICT = "sheet_conflicts_review_2026-10-09"
FAILS: list[str] = []


def check(cond, msg):
    print(("PASS " if cond else "FAIL ") + msg)
    if not cond:
        FAILS.append(msg)


def sluice():
    html_p = SHEET_DIR / f"{SLUICE}.html"
    check(html_p.is_file(), f"{html_p.relative_to(REPO)} is in the tree")
    if not html_p.is_file():
        return
    html = html_p.read_text()
    ok, why = G.verify_stamp(html)
    check(ok, f"gate stamp: {why} (written only after every gate requirement passed, and only on that exact HTML)")
    items = G._items({"html": html})
    items = items if isinstance(items, list) else (items or {}).get("items") or []
    check(len(items) > 0, f"sheet carries {len(items)} rows")
    snap_p = REPO / "infrastructure/state/art/sheets" / f"{SLUICE}.snapshot.json"
    snap = json.loads(snap_p.read_text()) if snap_p.is_file() else {}
    missing = sorted({i["id"] for i in items} - set(snap.get("rows") or {}))
    check(bool(snap) and not missing, f"snapshot committed and names every sheet row (missing: {missing})")
    # requirement 2 exactly as the gate runs it, on the committed HTML and the image files committed beside it
    ground = G._ground_for(snap.get("biome") or "")
    ctx = {"html": html, "sheet_dir": SHEET_DIR, "ground": ground, "biome": snap.get("biome")}
    c = G.check_scale(ctx, items)
    ground_lines = [p for p in c.problems if "ground" in p]
    row_lines = [p for p in c.problems if p not in ground_lines]
    check(not row_lines, f"req 2 scale panels: {c.note}; row problems: {row_lines[:6]}")
    if ground is None:
        # the ground record (scale_ground_measured.json) is rewritten by every sheet build and stays untracked; its
        # check ran at build time and is sealed in the stamp above
        print(f"NOTE ground colour not re-measured offline (untracked record); stamp covers it: {ground_lines}")
    else:
        check(not ground_lines, f"ground colour record: {ground_lines}")
    panels = 0
    for it in items:
        prim = next((g for g in it.get("graphics", []) if g.get("primary")), None) or {}
        for col in prim.get("cols") or []:
            s = col.get("scale") or {}
            for key in ("img", "full"):
                if s.get(key):
                    panels += 1
                    check((SHEET_DIR / s[key]).is_file(), f"{it['id']} set {col.get('letter')} scale {key} on disk")
    check(panels > 0, f"{panels} per-set scale images found (zero would mean the instrument is blind)")


def conflicts():
    gone = REPO / "Transient" / f"{CONFLICT}.html"
    check(not gone.exists(), f"{gone.relative_to(REPO)} is gone (retired, nothing to rebuild)")
    dec_p = REPO / "Transient" / f"{CONFLICT}.decisions.json"
    clicked = json.loads(dec_p.read_text())["decisions"]
    recs: dict[str, list] = {}
    files = set()
    for f in sorted(SHEET_DIR.glob("*.decisions.json")):
        for v in (json.loads(f.read_text()).get("decisions") or {}).values():
            for r in (v.get("conflictSheet") or []) if isinstance(v, dict) else []:
                if r.get("sheet") == CONFLICT:
                    recs.setdefault(r["item"], []).append(r)
                    files.add(f.name)
    check(len(recs) == 66 and len(files) == 17, f"{len(recs)} conflict rows enacted into {len(files)} biome sheets (66 into 17)")
    not_done = [k for k in clicked if k not in recs]
    wrong = [k for k in clicked if k in recs and not any(r.get("by") == "click" and r.get("choice") ==
                                                         clicked[k].get("decision") for r in recs[k])]
    check(len(clicked) == 38 and not not_done and not wrong,
          f"{len(clicked)} clicked owner choices all enacted with his letter (missing {not_done[:5]}, wrong {wrong[:5]})")


def main() -> int:
    sluice()
    conflicts()
    print(f"\n{'FAIL' if FAILS else 'OK'}: {len(FAILS)} failure(s)")
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
