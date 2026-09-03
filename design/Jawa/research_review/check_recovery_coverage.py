#!/usr/bin/env python3
"""Coverage-or-refuse for recovery_drafts.md.

Asserts that every one of the 84 earlier-cut rows in restructured_model_v2.json
(fate2 == 'cut' with no v2 recover line) is assigned to exactly one cluster in
the ```roster``` block of recovery_drafts.md, and that the roster's per-cluster
counts match the Index table. Prose mentions are NOT the roster: several cut
research defNames collide with ThingDef names cited in the text.
"""
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
MODEL = HERE / "restructured_model_v2.json"
DOC = HERE / "recovery_drafts.md"


def main() -> int:
    model = json.loads(MODEL.read_text(encoding="utf-8"))
    inventory = [r["defName"] for r in model
                 if r.get("fate2") == "cut" and not r.get("recover")]
    doc = DOC.read_text(encoding="utf-8")

    block = re.search(r"```roster\n(.*?)```", doc, re.S)
    if not block:
        print("COVERAGE: FAIL — no ```roster``` block in recovery_drafts.md")
        return 1

    roster: dict[int, tuple[str, list[str]]] = {}
    seen: dict[str, list[int]] = {}
    for line in block.group(1).strip().splitlines():
        num, verdict, *names = line.split()
        cid = int(num)
        roster[cid] = (verdict, names)
        for n in names:
            seen.setdefault(n, []).append(cid)

    index = [(int(m[0]), m[1], int(m[2])) for m in re.findall(
        r"^\|\s*(\d+)\s*\|[^|]*\|\s*\*\*(RECOVER|LOOT-ONLY|DEAD)\*\*\s*\|\s*(\d+)\s*\|",
        doc, re.M)]

    missing = sorted(set(inventory) - set(seen))
    extra = sorted(set(seen) - set(inventory))
    dupes = sorted(n for n, ids in seen.items() if len(ids) > 1)
    mismatch = [(cid, v, n) for cid, v, n in index
                if cid not in roster
                or roster[cid][0] != v
                or len(roster[cid][1]) != n]

    print(f"inventory (fate2=cut, no v2 recover) : {len(inventory)}")
    print(f"roster clusters / rows assigned      : {len(roster)} / {sum(len(v[1]) for v in roster.values())}")
    print(f"index clusters / rows claimed        : {len(index)} / {sum(n for _, _, n in index)}")
    print(f"MISSING from roster                  : {missing or 'none'}")
    print(f"NOT IN INVENTORY                     : {extra or 'none'}")
    print(f"ASSIGNED TWICE                       : {dupes or 'none'}")
    print(f"INDEX/ROSTER MISMATCH                : {mismatch or 'none'}")

    ok = (len(inventory) == 84 and not missing and not extra
          and not dupes and not mismatch and len(index) == len(roster))
    print("COVERAGE:", "PASS — all 84 defNames assigned exactly once; index matches roster"
          if ok else "FAIL")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
