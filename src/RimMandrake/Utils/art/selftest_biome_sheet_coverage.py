#!/usr/bin/env python3
"""biome_sheet_coverage: a census row is covered by a snapshot row or a snapshot's droppedAllRuled, nothing else."""
import json
import os
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import biome_sheet_coverage as C  # noqa: E402


def main() -> int:
    census = {"biome_order": ["RM_A", "RM_B", "RM_Empty"], "biomes": {
        "RM_A": {"rows": [{"key": "x"}, {"key": "y"}, {"key": "z"}], "summary": {"no_art": 0, "canon_missing_entry": 0}},
        "RM_B": {"rows": [{"key": "q"}], "summary": {"no_art": 1, "canon_missing_entry": 0}},
        "RM_Empty": {"rows": [], "summary": {}}}}
    slug = lambda b: b[3:].lower()  # noqa: E731
    with tempfile.TemporaryDirectory() as d:
        json.dump({"biome": "RM_A", "rows": {"x": {}}}, open(os.path.join(d, "a_sheet_1.snapshot.json"), "w"))
        json.dump({"biome": "RM_A", "rows": {}, "droppedAllRuled": ["y"]}, open(os.path.join(d, "a_sheet_2.snapshot.json"), "w"))
        json.dump({"biome": "RM_Other", "rows": {"z": {}}}, open(os.path.join(d, "a_sheet_3.snapshot.json"), "w"))
        json.dump({"biome": "RM_B", "rows": {"q": {}}}, open(os.path.join(d, "b_sheet_1.snapshot.json"), "w"))
        cov = C.coverage(census, d, slug)
    fails = []
    if set(cov) != {"RM_A", "RM_B"}:
        fails.append(f"biomes {sorted(cov)}")
    if cov["RM_A"]["uncovered"] != ["z"]:          # z only on another biome's snapshot (slug collision): not covered
        fails.append(f"RM_A uncovered {cov['RM_A']['uncovered']}")
    if cov["RM_A"]["dropped_all_ruled"] != ["y"]:
        fails.append(f"RM_A dropped {cov['RM_A']['dropped_all_ruled']}")
    if set(C.failing(cov)) != {"RM_A", "RM_B"}:    # RM_B: covered but no_art=1
        fails.append(f"failing {sorted(C.failing(cov))}")
    print("FAIL " + "; ".join(fails) if fails else "PASS selftest_biome_sheet_coverage")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
