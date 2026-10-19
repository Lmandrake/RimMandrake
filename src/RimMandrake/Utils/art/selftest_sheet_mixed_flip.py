#!/usr/bin/env python3
"""selftest_sheet_mixed_flip.py — a def with a flip-book AND ordinary ground art (Strill, Whisperbird) builds a sheet row.

Was: flip_layout did int('single') and crashed `art_sheet.py --subjects RSW_Strill`. Now a ground-facing set that
landed in the flip lane moves to the unassigned lane (keeping its ground facings) and flip_layout counts frames only.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import art_sheet as S  # noqa: E402

FAILS = []


def check(cond, msg):
    print(("PASS " if cond else "FAIL ") + msg)
    if not cond:
        FAILS.append(msg)


def main():
    live = {"kind": "live", "faces": {"1_east": "a", "1_south": "b", "2_east": "c", "2_south": "d"}}
    ground = {"kind": "artpipe", "faces": {"single": "g"}}
    cols = [live, ground]
    try:
        keys, n, fac = S.flip_layout(cols)
        ok = n == 2 and fac == ["east", "south"] and "single" not in keys
    except ValueError:
        ok = False
    check(ok, "flip_layout over a mixed column list counts frames only (no ValueError on 'single')")
    gr = [{"res": "_flip:S/Strill_Flying_", "role": S.FLIP_ROLE, "cols": [live, ground], "flip": True, "prior_raw": None}]
    S._ground_out_of_flip(gr)
    check(len(gr) == 2 and gr[0]["cols"] == [live] and gr[1]["res"] is None and gr[1]["cols"] == [ground],
          "the ground set leaves the flip lane for the unassigned lane, faces intact")
    S._ground_out_of_flip(gr)
    check(len(gr) == 2 and gr[1]["cols"] == [ground], "idempotent")
    print("FAIL" if FAILS else "ALL PASS")
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
