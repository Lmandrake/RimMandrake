#!/usr/bin/env python3
"""selftest_sheet_question.py — a --subjects sheet's --question (one per-row choice besides the pictures, e.g. a tree
size tier, TREE_TIERS_JUDGE_FORTY_FOUR_TRUNKS) is validated on load, kept in the census so a refresh_sheets rebuild
keeps it, and its prefill is the AGENT's guess: the decisions file stores it as qPrefill, never as his answer q, and the
row control writes only q."""
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
    q = {"key": "tier", "label": "Size tier", "options": [["small", "Small"], ["big", "Big"]],
         "rows": {"RM_Probe": {"prefill": "big", "why": "probe", "context": "biome: none"}}}
    with tempfile.TemporaryDirectory() as td:
        qp = Path(td) / "q.json"
        qp.write_text(json.dumps(q))
        check(A.load_question(qp)["key"] == "tier", "a valid question loads")
        bad = dict(q, rows={"RM_Probe": {"prefill": "huge"}})
        qp.write_text(json.dumps(bad))
        try:
            A.load_question(qp)
            check(False, "a prefill that is not an option is refused")
        except SystemExit:
            check(True, "a prefill that is not an option is refused")
        old = A.BIOME_OUT
        A.BIOME_OUT = Path(td)
        try:
            p, key = A.subjects_census("q_probe", [], (), "Q probe", "", (), q)
            c = json.loads(p.read_text())
            check(c["biomes"][key].get("question", {}).get("key") == "tier", "question stored in the census")
            p2, key2 = A.subjects_census("q_probe2", [], (), "No q")
            check("question" not in json.loads(p2.read_text())["biomes"][key2], "no --question: no question key")
        finally:
            A.BIOME_OUT = old
    src = (HERE / "art_sheet.py").read_text()
    check('ap.add_argument("--question"' in src, "--question is a CLI flag")
    check('"qPrefill": {Q["key"]' in src, "the decisions prefill stores the guess as qPrefill")
    check("rec.q = q" in src and "rec.qPrefill" not in src, "the row control writes his answer to q only")
    check("bs-qguess" in src and "agent guess" in src, "the guess is drawn as a guess, not an answer")
    print(f"{8 - len(FAILS)}/8")
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
