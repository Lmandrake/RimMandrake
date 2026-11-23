#!/usr/bin/env python3
"""selftest_flowworks_no_minified_thingsofdef.py: no FlowWorks C# asks ListerThings.ThingsOfDef for MinifiedThing.

WHY (RIMMANDRAKE_TRACE_SLACK_FLOWWORKS_TIER_MINIFIED_LOOKUP_ERROR): vanilla Verse.ListerThings.ThingsOfDef refuses
MinifiedThing with Log.ErrorOnce "Tried to get ThingsOfDef of MinifiedThing, use
ThingsMatching(ThingRequest.ForGroup(ThingRequestGroup.MinifiedThing)) instead". FlowWorks' pit rescue
(RM_PitAccess.SparePortable, looking for a spare portable ladder) made that call, so every map where a pawn needed a
ladder out of a pit logged a red error, and Z_log_budget read FAIL on tier gimmesomeslack_flowworks.

WHAT IT CHECKS, over every production .cs under FlowWorks/Source (SelfTest and obj excluded, comments masked):
  * no call ThingsOfDef( ... MinifiedThing ) - by ThingDefOf.MinifiedThing or by a bare MinifiedThing name;
  * RM_PitAccess.SparePortable still looks for crates through ThingsInGroup(ThingRequestGroup.MinifiedThing)
    (so deleting the search outright, which would also silence the error, reads red).

CAN IT FAIL: each run plants the old call into a throwaway copy of RM_PitAccess.cs and re-runs the scan; it must read
red. A plant that stays green is itself a FAIL.

    python3 src/RimMandrake/FlowWorks/selftest_flowworks_no_minified_thingsofdef.py
"""
from __future__ import annotations

import re
import sys
import tempfile
from pathlib import Path

FW = Path(__file__).resolve().parent
SRC = FW / "Source"
PIT = SRC / "Superdeep" / "RM_PitAccess.cs"

BAD = re.compile(r"ThingsOfDef\s*\(\s*(?:[A-Za-z_][\w.]*\.)?MinifiedThing\s*\)")
GOOD = re.compile(r"ThingsInGroup\s*\(\s*ThingRequestGroup\s*\.\s*MinifiedThing\s*\)")
SPARE = re.compile(r"MinifiedThing\s+SparePortable\s*\(")


def mask_comments(text: str) -> str:
    """Blank // and /* */ comments (keeps strings intact enough for this scan)."""
    text = re.sub(r"/\*.*?\*/", lambda m: " " * len(m.group(0)), text, flags=re.S)
    return re.sub(r"//[^\n]*", "", text)


def method_body(text: str, anchor: re.Pattern) -> str | None:
    m = anchor.search(text)
    if not m:
        return None
    i = text.find("{", m.end())
    depth = 0
    for j in range(i, len(text)):
        if text[j] == "{":
            depth += 1
        elif text[j] == "}":
            depth -= 1
            if depth == 0:
                return text[i:j + 1]
    return None


def scan(files: list[Path], pit: Path) -> tuple[list[str], int]:
    bad = []
    for f in files:
        t = mask_comments(f.read_text(encoding="utf-8", errors="replace"))
        for m in BAD.finditer(t):
            line = t.count("\n", 0, m.start()) + 1
            bad.append(f"{f.name}:{line}: {m.group(0)}")
    body = method_body(mask_comments(pit.read_text(encoding="utf-8")), SPARE)
    if body is None:
        bad.append("RM_PitAccess.SparePortable not found")
    elif not GOOD.search(body):
        bad.append("RM_PitAccess.SparePortable no longer searches ThingsInGroup(ThingRequestGroup.MinifiedThing)")
    return bad, len(files)


def main() -> int:
    files = [p for p in SRC.rglob("*.cs") if "SelfTest" not in p.parts and "obj" not in p.parts and "bin" not in p.parts]
    bad, n = scan(files, PIT)
    ok = True
    print(f"scan: {len(bad)} ThingsOfDef(MinifiedThing) call(s) or missing group search (limit 0), {n} .cs files read")
    for b in bad:
        print(f"  FAIL {b}")
    if bad:
        ok = False
    if n < 50:
        print(f"FAIL instrument: only {n} .cs files read (expected the whole FlowWorks Source, >= 50)")
        ok = False
    # mutation: plant the old call; the scan must go red
    with tempfile.TemporaryDirectory() as td:
        planted = Path(td) / "RM_PitAccess.cs"
        src = PIT.read_text(encoding="utf-8")
        mutated = GOOD.sub("ThingsOfDef(ThingDefOf.MinifiedThing)", src, count=1)
        planted.write_text(mutated, encoding="utf-8")
        mbad, _ = scan([planted], planted)
        caught = mutated != src and len(mbad) >= 1
        print(f"plant: old call spliced into a copy of RM_PitAccess.cs -> {len(mbad)} finding(s) (must be >= 1): "
              f"{'caught' if caught else 'NOT CAUGHT'}")
        if not caught:
            ok = False
    print("PASS" if ok else "FAIL")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
