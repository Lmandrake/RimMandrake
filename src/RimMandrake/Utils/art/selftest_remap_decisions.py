#!/usr/bin/env python3
"""Selftest for remap_decisions.py: every letter classify() counts as remapped is rewritten by apply_map(),
in every field decisions_v2.letters() reads (schema 2 included). Pure: no files touched."""
import copy
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import decisions_v2 as DV  # noqa: E402
import remap_decisions as R  # noqa: E402

FAIL = []


def check(cond, name):
    print(("PASS " if cond else "FAIL ") + name)
    if not cond:
        FAIL.append(name)


def main():
    # A and B swapped pictures in the rebuild; C unchanged; D's pictures are gone.
    ruled = {"rows": {"r1": {"columns": {"A": ["sha_a"], "B": ["sha_b"], "C": ["sha_c"], "D": ["sha_d"]}}}}
    now = {"rows": {"r1": {"columns": {"A": ["sha_b"], "B": ["sha_a"], "C": ["sha_c"]}}}}
    row = {"decision": "A", "picks": {"g1": "B"}, "variants": ["A", "C"], "legacyVariants": ["B"],
           "slots": {"s1": {"pick": "A"}, "s2": {"pick": "C"}}, "pool": {"p": {"add": ["B"], "remove": ["A"]}},
           "reject": {"x": ["A", "D"]}, "retire": {"y": ["B"]}, "assign": {"A": "s1", "C": "s2"},
           "asks": {"more": [{"base": "B"}]}}
    dec = {"decisions": {"r1": copy.deepcopy(row)}}
    st, orphans, newmap = R.classify(dec, ruled, now)
    check(st["remapped"] == 2 and newmap == {"r1": {"A": "B", "B": "A"}}, "classify: A<->B remapped")
    check(orphans == ["r1:D"], "classify: D orphaned")
    R.apply_map(dec, newmap)
    v = dec["decisions"]["r1"]
    swap = {"A": "B", "B": "A"}
    check(DV.letters(v) == {swap.get(x, x) for x in DV.letters(row)}, "apply_map: every letter field rewritten")
    check(v["slots"]["s1"]["pick"] == "B" and v["pool"]["p"] == {"add": ["A"], "remove": ["B"]},
          "apply_map: slots and pool rewritten")
    check(v["reject"] == {"x": ["B", "D"]} and v["retire"] == {"y": ["A"]}, "apply_map: reject/retire rewritten")
    check(v["assign"] == {"B": "s1", "C": "s2"} and v["asks"]["more"][0]["base"] == "A",
          "apply_map: assign keys and asks base rewritten")
    check(v["decision"] == "B" and v["picks"] == {"g1": "A"} and v["variants"] == ["B", "C"]
          and v["legacyVariants"] == ["A"], "apply_map: schema-1 fields rewritten")
    # rebase(): the letters move to the current snapshot AND snapshotId follows them, so a second run (which reads
    # the decisions against the snapshot snapshotId names) finds nothing to do instead of swapping A<->B back.
    ruled2 = {"snapshotId": "old", "rows": {"r1": {"columns": {"A": ["sha_a"], "B": ["sha_b"]}}}}
    now2 = {"snapshotId": "new", "rows": {"r1": {"columns": {"A": ["sha_b"], "B": ["sha_a"]}}}}
    dec2 = {"snapshotId": "old", "decisions": {"r1": {"decision": "A", "picks": {"g1": "B"}}}}
    check(R.stale(dec2, ruled2, now2) and not R.stale(dec2, None, now2), "stale: only with a findable ruled snapshot")
    st2, orph2, map2 = R.classify(dec2, ruled2, now2)
    R.rebase(dec2, map2, now2)
    check(dec2["snapshotId"] == "new" and dec2["decisions"]["r1"] == {"decision": "B", "picks": {"g1": "A"}},
          "rebase: letters rewritten and snapshotId moved to the current snapshot")
    st3, _, map3 = R.classify(dec2, now2, now2)
    check(not R.stale(dec2, now2, now2) and map3 == {} and st3["remapped"] == 0,
          "rebase: a second run is a no-op (no swap back)")
    print("%s (%d failed)" % ("GREEN" if not FAIL else "RED", len(FAIL)))
    return 1 if FAIL else 0


if __name__ == "__main__":
    sys.exit(main())
