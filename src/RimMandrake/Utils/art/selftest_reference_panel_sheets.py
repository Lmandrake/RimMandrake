#!/usr/bin/env python3
"""selftest_reference_panel_sheets.py — the four sheets built before reference panels existed (drawbridge_art and the
three br1e bore shadow sheets) were rebuilt so every row whose census carries `reference_textures` shows them as
true-scale panels (`scale.refs`, one per texture, each naming its rendered image; the images are derived and stay unpinned). The rebuilt HTML, census and prereview
are pinned in Transient/ so this holds in every clone; it reads the ITEMS JSON directly (no mtime test, which a checkout scrambles).
Item ART_SHEETS_REBUILD_FOR_REFERENCE_PANELS."""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[4]
OUT = REPO / "Transient" / "biome_ffar"
SHEETS = {  # census slug -> sheet date
    "drawbridge_art": "2026-10-20",
    "art_eval_shadow_br1e_ports_bore_20261023": "2026-10-23",
    "art_eval_shadow_br1e_ports_bore_20261023_r2": "2026-10-23",
    "art_eval_shadow_br1e_ports_bore_20261023_r3": "2026-10-23",
}
FAILS: list[str] = []


def check(cond, msg):
    print(("PASS " if cond else "FAIL ") + msg)
    if not cond:
        FAILS.append(msg)


def items_of(html: Path) -> list[dict]:
    m = re.search(r'<script id="ITEMS" type="application/json">(.*?)</script>', html.read_text(), re.S)
    return json.loads(m.group(1)) if m else []


def main() -> int:
    rows_checked = 0
    for slug, date in SHEETS.items():
        cj, html = OUT / f"{slug}.subjects.json", OUT / f"{slug}_sheet_{date}.html"
        check(cj.is_file() and html.is_file(), f"{slug}: census and sheet are present")
        if not (cj.is_file() and html.is_file()):
            continue
        items = {i.get("key") or i.get("id"): i for i in items_of(html)}
        check(bool(items), f"{slug}: the sheet's ITEMS parse ({len(items)})")
        for b in json.loads(cj.read_text()).get("biomes", {}).values():
            for r in b.get("rows", []):
                refs = r.get("reference_textures") or []
                if not refs:
                    continue
                it = items.get(r["key"])
                if it is None:   # a row the sheet omits (ruled elsewhere) shows nothing, reference included
                    continue
                rows_checked += 1
                scale = it.get("scale") or {}
                got = scale.get("refs")
                check(got is not None, f"{slug} {r['key']}: scale carries a refs key")
                got = got or []
                check(len(got) == len(refs) and all(str(p.get("img") or "").endswith(".png") and not p.get("missing") for p in got),
                      f"{slug} {r['key']}: {len(refs)} reference panel(s) shown, each with an image ({len(got)})")
    print(f"rows with reference_textures checked: {rows_checked}")
    check(rows_checked >= 35, f"the 35 formerly-stale rows are all checked ({rows_checked})")
    print(f"{len(FAILS)} failed" if FAILS else "all passed")
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
