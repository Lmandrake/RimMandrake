#!/usr/bin/env python3
"""selftest_reference_textures.py — a census row's `reference_textures` (e.g. the installed canon twin beside the base it
will reskin) is shown read-only and can NEVER become a pickable column: not a graphic, column, letter, snapshot entry,
decision or enact target. Checked on a synthetic row through the real builder helpers, and on every built subject sheet
whose census carries the field."""
from __future__ import annotations

import hashlib
import json
import re
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import art_sheet as A  # noqa: E402
import artledger as L  # noqa: E402

FAILS = []


def check(cond, msg):
    print(("PASS " if cond else "FAIL ") + msg)
    if not cond:
        FAILS.append(msg)


def synthetic():
    from PIL import Image
    with tempfile.TemporaryDirectory(dir=L.REPO_ROOT / "Transient") as td:
        png = Path(td) / "ref.png"
        Image.new("RGBA", (64, 64), (200, 30, 30, 255)).save(png)
        sha = hashlib.sha256(png.read_bytes()).hexdigest()
        rel = str(png.relative_to(L.REPO_ROOT))
        size = {"status": "fallback", "kind": "plant", "drawSize": [1.0, 1.0], "visualMax": 2.0, "mesh": 1, "quad": 2.0,
                "cells": 2.0, "color": [1, 1, 1], "source": "FALLBACK test"}
        had = L.store_has(sha)
        refs = A._reference_panels({"key": "ST_Row", "reference_textures": [rel, "no/such.png"]}, size, Path(td))
        check(len(refs) == 2 and refs[0].get("img") and (Path(td).parent / refs[0]["img"]).exists(),
              "a reference texture renders a true-scale panel")
        check(refs[1].get("missing") is True, "a missing reference path is reported, not dropped")
        check(set(refs[0]) == {"path", "img", "full"}, f"a reference panel carries no letter/sha/faces: {sorted(refs[0])}")
        check(L.store_has(sha) == had, "a reference texture is never put in the art store (so no column can name it)")


def built_sheets():
    n = 0
    for cj in sorted(A.BIOME_OUT.glob("*.subjects.json")):
        c = json.loads(cj.read_text())
        for b in c.get("biomes", {}).values():
            for r in b.get("rows", []):
                refs = r.get("reference_textures") or []
                if not refs:
                    continue
                shas = {hashlib.sha256((L.REPO_ROOT / p).read_bytes()).hexdigest() for p in refs if (L.REPO_ROOT / p).is_file()}
                for snap in sorted((L.REPO_ROOT / "infrastructure/state/art/sheets").glob(f"{b['slug']}_sheet_*.snapshot.json")):
                    s = json.loads(snap.read_text())
                    cols = json.dumps((s.get("rows") or {}).get(r["key"], {}).get("columns", {}))
                    n += 1
                    check(not any(h in cols for h in shas), f"{snap.stem} {r['key']}: no reference texture is a column")
                for html in sorted(A.BIOME_OUT.glob(f"{b['slug']}_sheet_*.html")):
                    h = html.read_text()
                    m = re.search(r'<script id="ITEMS" type="application/json">(.*?)</script>', h, re.S)
                    items = json.loads(m.group(1)) if m else []
                    it = next((i for i in items if i.get("key") == r["key"] or i.get("id") == r["key"]), None)
                    if it is None:
                        continue
                    gcols = json.dumps(it.get("graphics") or [])
                    check(not any(h_ in gcols for h_ in shas) and not any(p in gcols for p in refs),
                          f"{html.stem} {r['key']}: no reference texture in the row's graphics")
                    check(len((it.get("scale") or {}).get("refs") or []) == len(refs),
                          f"{html.stem} {r['key']}: every reference texture is shown ({len(refs)})")
    print(f"built-sheet rows with reference_textures checked: {n}")


def main():
    synthetic()
    built_sheets()
    print(f"{len(FAILS)} failed" if FAILS else "all passed")
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
