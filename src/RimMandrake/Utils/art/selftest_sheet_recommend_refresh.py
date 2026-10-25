#!/usr/bin/env python3
"""selftest_sheet_recommend_refresh.py — ART_SHEET_HARDEN_RECOMMEND_ON_REFRESH: --recommend FAM=WHY is kept in the census
entry, so a refresh_sheets rebuild (no CLI flags) still prefills the agent's recommendation; sibling_keeps matches
texPaths case-insensitively."""
from __future__ import annotations
import json
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import art_sheet as A  # noqa: E402

FAILS = []


def check(cond, msg):
    print(("PASS " if cond else "FAIL ") + msg)
    if not cond:
        FAILS.append(msg)


with tempfile.TemporaryDirectory() as td:
    A.BIOME_OUT = Path(td)
    A.RECOMMEND_CLI.clear()
    A.RECOMMEND_CLI["famX"] = "cleanest silhouette"
    path, key = A.subjects_census("rec_test", [], [])
    ent = json.loads(path.read_text())["biomes"][key]
    check(ent.get("recommend") == {"famX": "cleanest silhouette"}, "census entry holds the recommendation")
    A.RECOMMEND_CLI.clear()               # a refresh rebuild: no CLI flags
    A.set_recommend(ent)
    check(A.RECOMMEND == {"famX": "cleanest silhouette"}, "refresh rebuild recovers it from the census")
    A.RECOMMEND_CLI["famX"] = "newer reason"
    A.set_recommend(ent)
    check(A.RECOMMEND["famX"] == "newer reason", "a CLI value overrides the saved one")
    A.RECOMMEND_CLI.clear()
    A.set_recommend({})
    check(A.RECOMMEND == {}, "no leak into the next sheet")
    g = {"cols": [{"letter": "B", "label": "render famX"}]}
    A.set_recommend(ent)
    check(A._recommended(g) == ("B", "agent recommends: cleanest silhouette"), "prefill picks the recommended column")


class Idx:
    live = {("m", "Textures/Things/Animal/Zorb/Zorb_A_east.png"): {"sha": "s1"},
            ("m", "Textures/Things/Animal/Zorb/zorb_b_east.png"): {"sha": "s2"}}

    def protected(self, sha):
        return []


out = A.sibling_keeps(Idx(), {"Things/Animal/Zorb/Zorb_A"}, ["Zorb"], {"Things/Animal/Zorb/Zorb_B": [{"subject": "Zorb"}]})
check(any(o["res"].lower().endswith("zorb_b") for o in out), "case-different texPath still joins as a sibling")
print("FAILED: " + ", ".join(FAILS) if FAILS else "all ok")
sys.exit(1 if FAILS else 0)
