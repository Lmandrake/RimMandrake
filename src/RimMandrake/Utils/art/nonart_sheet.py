#!/usr/bin/env python3
"""nonart_sheet.py — the checked route for review sheets that are NOT biome art sheets (owner card, 2026-10-09).

serve_gated.py serves a biome art sheet only with a scaled_review_gate stamp. A sheet that is not art (a code-triage sheet, a
keep/replace sheet) can never earn that stamp, so it had no way to be served. This gives it its own checks instead of loosening
the art ones:

  * the HTML declares  <meta name="sheet-kind" content="non-art">   (add it with `nonart_sheet.py declare <html>`)
  * it is NOT an art-gated sheet: no scaled-review-gate stamp, not under biome_ffar/, no biome_ffar image
  * check_sheet.py (review-sheets skill) reports 0 FAIL against the sheet AND its decisions file
  * the decisions file: JSON object, sheetId == the sheet's file stem, reviewStatus.state valid, `decisions` an object whose
    every value is an object with a string `decision`, every key a row id in the sheet's ITEMS
    python3 nonart_sheet.py check <html> <decisions.json>
"""
from __future__ import annotations

import importlib.util
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import scaled_review_gate as SG  # noqa: E402

KIND_RE = re.compile(r'<meta name="sheet-kind" content="([^"]*)">')
SKILL_ASSETS = Path.home() / ".claude" / "skills" / "review-sheets" / "assets"
VALID_STATES = {"prefill", "ruled"}


def declares_nonart(html: str) -> bool:
    m = KIND_RE.search(html)
    return bool(m and m.group(1) == "non-art")


def declare(html: str) -> str:
    if KIND_RE.search(html):
        return KIND_RE.sub('<meta name="sheet-kind" content="non-art">', html, count=1)
    return html.replace("<head>", '<head>\n<meta name="sheet-kind" content="non-art">', 1)


def _items(html: str):
    m = re.search(r'<script id="ITEMS"[^>]*>(.*?)</script>', html, re.S)
    if not m:
        return None
    try:
        return json.loads(m.group(1).replace("<\\/", "</"))
    except ValueError:
        return None


def _check_sheet(sheet: Path, decisions: Path):
    spec = importlib.util.spec_from_file_location("check_sheet", str(SKILL_ASSETS / "check_sheet.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.check(str(sheet), str(decisions))


def verify(sheet: Path, decisions: Path) -> tuple[bool, str]:
    """(ok, message). Every failure names what is wrong; ok means serve_gated may start the server."""
    html = sheet.read_text()
    if not declares_nonart(html):
        return False, "no <meta name=\"sheet-kind\" content=\"non-art\"> declaration"
    if SG.STAMP_RE.search(html):
        return False, "carries a scaled-review-gate stamp, so it is an art sheet; it is served by its stamp, not as non-art"
    if "biome_ffar" in str(sheet.resolve()).replace("\\", "/") or "biome_ffar" in html:
        return False, "is under or points into biome_ffar/, so it is a biome art sheet and needs the gate stamp"
    if not decisions.is_file():
        return False, f"decisions file {decisions} does not exist"
    try:
        doc = json.loads(decisions.read_text())
    except ValueError as e:
        return False, f"decisions file is not JSON: {e}"
    if not isinstance(doc, dict):
        return False, "decisions file is not a JSON object"
    if doc.get("sheetId") != sheet.stem:
        return False, f"decisions sheetId {doc.get('sheetId')!r} != sheet stem {sheet.stem!r}"
    rs = doc.get("reviewStatus")
    if not isinstance(rs, dict) or rs.get("state") not in VALID_STATES:
        return False, "decisions reviewStatus.state missing or not one of " + "/".join(sorted(VALID_STATES))
    dec = doc.get("decisions")
    if not isinstance(dec, dict):
        return False, "decisions['decisions'] is not an object"
    items = _items(html)
    if not isinstance(items, list):
        return False, "sheet has no readable ITEMS block"
    ids = {i.get("id") for i in items if isinstance(i, dict)}
    for k, v in dec.items():
        if not isinstance(v, dict) or not isinstance(v.get("decision"), str):
            return False, f"decision row {k!r} is not an object with a string 'decision'"
        if k not in ids:
            return False, f"decision row {k!r} is not a row in the sheet"
    try:
        results = _check_sheet(sheet, decisions)
    except Exception as e:  # noqa: BLE001
        return False, f"check_sheet.py could not run: {e}"
    fails = [f"{label}: {detail}" for sev, label, detail in results if sev == "FAIL"]
    if fails:
        return False, "check_sheet.py FAIL: " + "; ".join(fails[:3])
    return True, "non-art sheet checks ok"


def main(argv):
    if len(argv) >= 2 and argv[0] == "declare":
        p = Path(argv[1])
        p.write_text(declare(p.read_text()))
        print(f"declared non-art: {p}")
        return 0
    if len(argv) == 3 and argv[0] == "check":
        ok, msg = verify(Path(argv[1]), Path(argv[2]))
        print(("OK " if ok else "REFUSED ") + msg)
        return 0 if ok else 1
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
