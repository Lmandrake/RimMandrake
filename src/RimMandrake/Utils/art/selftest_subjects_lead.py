#!/usr/bin/env python3
"""selftest_subjects_lead.py — a --subjects sheet's purpose paragraph (--lead) is stored in its census, so the
page shows it above the rows and a refresh_sheets rebuild (which reads that census back) keeps it."""
from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import art_sheet as A  # noqa: E402

FAILS: list[str] = []


def check(c, m):
    print(("PASS " if c else "FAIL ") + m)
    if not c:
        FAILS.append(m)


def main():
    lead = "<p class=purpose>You are judging X. Skipping keeps the donor art.</p>"
    with tempfile.TemporaryDirectory() as td:
        old = A.BIOME_OUT
        A.BIOME_OUT = Path(td)
        try:
            p, key = A.subjects_census("lead_probe", [], (), "Lead probe", lead)
            c = json.loads(p.read_text())
            check(c["biomes"][key].get("lead_html") == lead, "lead paragraph stored in the census")
            p2, _ = A.subjects_census("lead_probe2", [], (), "No lead")
            c2 = json.loads(p2.read_text())
            check(c2["biomes"]["SUBJECTS_lead_probe2"].get("lead_html") == "", "no --lead: empty lead, no crash")
        finally:
            A.BIOME_OUT = old
    check('ap.add_argument("--lead"' in (HERE / "art_sheet.py").read_text(), "--lead is a CLI flag")
    print(f"{3 - len(FAILS)}/3")
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
