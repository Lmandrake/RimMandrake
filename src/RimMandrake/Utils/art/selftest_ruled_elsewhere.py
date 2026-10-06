#!/usr/bin/env python3
"""selftest_ruled_elsewhere.py — a subject the owner already ruled on another sheet is found, through subject.py
name variants; prefill-only, purge-only and the sheet's own rows are not rulings (owner, 2026-10-05)."""
from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import art_sheet as A  # noqa: E402

FAILS = []


def check(cond, msg):
    print(("PASS " if cond else "FAIL ") + msg)
    if not cond:
        FAILS.append(msg)


def main():
    with tempfile.TemporaryDirectory() as td:
        d = Path(td)
        other = {"biome": "RM_Other", "savedBy": "review-sheet-sidecar", "writeCount": 5,
                 "decisions": {
                     "RSW_Wraid": {"decision": "B", "at": "2026-10-05T01:00:00Z", "decidedAt": "x", "note": "good"},
                     "RM_Gorg": {"decision": "A", "prefill": "A"},
                     "RSW_Plant_Nysyllin_Wild": {"decision": "redo", "at": "2026-10-05T02:00:00Z", "decidedAt": "x"},
                     "RSW_Purgy": {"decision": "A", "at": "2026-10-05T02:00:00Z", "purgeTouched": True}}}
        (d / "other_sheet_2026-10-05.decisions.json").write_text(json.dumps(other))
        gen = {"biome": "RM_Gen", "reviewStatus": {"state": "prefill"},
               "decisions": {"RM_Skorra": {"decision": "A", "at": "2026-10-05T03:00:00Z", "decidedAt": "x"}}}
        (d / "gen_sheet_2026-10-05.decisions.json").write_text(json.dumps(gen))
        mine = {"biome": "RM_Mine", "savedBy": "review-sheet-sidecar", "writeCount": 2,
                "decisions": {"RM_Fuzz": {"decision": "B", "at": "2026-10-05T03:00:00Z", "decidedAt": "x"}}}
        (d / "mine_sheet_2026-10-05.decisions.json").write_text(json.dumps(mine))
        ents = A.ruled_elsewhere(d, "mine_sheet_2026-10-05", {"RM_Other": "Other Biome"})
        f = lambda n: A.ruled_elsewhere_for(A._subject_names(n), ents)
        check(f("RSW_Wraid") and f("RSW_Wraid")["decision"] == "B" and f("RSW_Wraid")["sheet"] == "Other Biome",
              "exact subject found, sheet named by biome label")
        check(f("RSW_WraidAlpha") is not None, "variant word (WraidAlpha) matches the base species")
        check(f("RM_Wraid") is not None, "tier prefix does not make it a new subject")
        check(f("Plant_Nysyllin_Wild") is not None, "Plant_ prefix and tier prefix both stripped")
        check(f("RM_Gorg") is None, "an untouched prefill is not a ruling")
        check(f("RSW_Purgy") is None, "a purge-only touch is not a ruling")
        check(f("RM_Skorra") is None, "a sheet nobody ruled (generator prefill) is not a source")
        check(f("RM_Fuzz") is None, "the sheet's own rows are never 'elsewhere'")
        check(f("RM_Unknown") is None, "an unruled subject stays open")
    print(f"{len(FAILS)} failed" if FAILS else "all passed")
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
