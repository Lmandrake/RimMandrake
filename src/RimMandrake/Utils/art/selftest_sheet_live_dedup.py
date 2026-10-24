#!/usr/bin/env python3
"""selftest_sheet_live_dedup.py — an installed picture is shown AS installed even when an earlier lane shows its bytes
as a render (ART_EVAL_SHADOW_FIX_GIZKA_REQ15, 2026-10-24).

Gizka: render canonregen_rsw_gizka_v1 joins the base Gizka lane by creature word; its bytes are what GizkaW (the 80%
alternate graphic) has installed. The row's cross-lane dedup dropped the GizkaW lane's live column as a duplicate, so
the installed picture showed only as a render and gate req 15 refused every sheet with the row (shadow sheet
gptredo_01, a plain `art_sheet --subjects RSW_Gizka` alike). art_sheet._take_unseen keeps a live column unless an
earlier lane already showed those bytes as live; every other duplicate is still dropped.
"""
from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import art_sheet as AS  # noqa: E402

FAILS: list[str] = []


def check(ok: bool, what: str) -> None:
    print(("ok   " if ok else "FAIL ") + what)
    if not ok:
        FAILS.append(what)


def col(kind: str, faces: dict, label: str = "") -> dict:
    return {"kind": kind, "faces": dict(faces), "label": label}


def main() -> int:
    w = {"south": "a" * 64, "east": "b" * 64, "north": "c" * 64}
    base = {"south": "d" * 64, "east": "e" * 64, "north": "f" * 64}
    seen: set = set()
    lane1 = AS._take_unseen([col("live", base, "IN GAME — Gizka"), col("artpipe", w, "render canonregen_rsw_gizka_v1")], seen)
    check(len(lane1) == 2, "first lane keeps its live column and the render")
    lane2 = AS._take_unseen([col("live", w, "IN GAME — GizkaW"), col("artpipe", base, "render other")], seen)
    check([c["kind"] for c in lane2] == ["live"],
          "the GizkaW lane keeps its live column though the render with those bytes was shown first (was dropped: req 15)")
    lane3 = AS._take_unseen([col("live", w, "IN GAME — GizkaW again"), col("git", w, "older"), col("artpipe", w, "dup render")], seen)
    check(lane3 == [], "bytes already shown AS live are dropped, live or not")
    s2: set = set()
    AS._take_unseen([col("live", w)], s2)
    check(AS._take_unseen([col("artpipe", w)], s2) == [], "a render duplicating an earlier live column is still dropped")
    s3: set = set()
    same = AS._take_unseen([col("artpipe", w, "x"), col("artpipe", w, "y")], s3)
    check(len(same) == 2, "within one lane nothing is dropped (as before the fix)")
    print(f"\n{'FAIL' if FAILS else 'PASS'}: {len(FAILS)} failing")
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
