#!/usr/bin/env python3
"""FILL_IN_DESIGNATION_FIX_SCAN_INVALIDATED: the fill-in work scan must not walk the live designation list.

WorkGiver_FillInCanal.HasJobOnCell deletes stale RM_FillInCanal designations while JobGiver_Work is still
enumerating PotentialWorkCellsGlobal. A lazy `yield return` over DesignationManager.SpawnedDesignationsOfDef
then throws "Collection was modified" (seen live 2026-10-25 run4). The fix materialises the cells into a List,
as WorkGiver_DigCanal does. This test pins the source shape offline AND that the committed DLL was built from
exactly this source (its .srchash line for the file matches the file's sha256), so the shipped binary has the fix.
"""
import hashlib
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
FW = REPO / "src" / "RimMandrake" / "FlowWorks"
SRC = FW / "Source"
SRCHASH = FW / "Assemblies" / "RimMandrakeFlowWorks.dll.srchash"


def method_body(text: str, name: str) -> str:
    m = re.search(r"\b" + re.escape(name) + r"\s*\([^)]*\)\s*\{", text)
    if not m:
        raise AssertionError(f"method {name} not found")
    i, depth = m.end(), 1
    while depth:
        c = text[i]
        depth += c == "{"
        depth -= c == "}"
        i += 1
    return text[m.end():i - 1]


def check(cond: bool, msg: str, fails: list) -> None:
    print(("ok   " if cond else "FAIL ") + msg)
    if not cond:
        fails.append(msg)


def main() -> int:
    fails: list = []
    for fname, deletes in (("WorkGiver_FillInCanal.cs", True), ("WorkGiver_DigCanal.cs", None)):
        path = SRC / fname
        text = path.read_text(encoding="utf-8")
        scan = method_body(text, "PotentialWorkCellsGlobal")
        check("SpawnedDesignationsOfDef" in scan, f"{fname}: scan reads the designation list (probe sees the method)", fails)
        check("yield" not in scan, f"{fname}: PotentialWorkCellsGlobal has no lazy yield", fails)
        check(re.search(r"new\s+List<IntVec3>", scan) is not None and re.search(r"return\s+cells\s*;", scan) is not None,
              f"{fname}: PotentialWorkCellsGlobal returns a materialised List<IntVec3>", fails)
        if deletes:
            job = method_body(text, "HasJobOnCell")
            check("des.Delete()" in job, f"{fname}: HasJobOnCell still deletes stale designations (the hazard is real)", fails)
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        pinned = {ln.split()[1]: ln.split()[0] for ln in SRCHASH.read_text(encoding="utf-8").splitlines()
                  if ln and not ln.startswith("#") and len(ln.split()) == 2}
        check(pinned.get(fname) == digest, f"{fname}: committed DLL .srchash pins this exact source", fails)
    print("FAILED" if fails else "PASS", f"({len(fails)} failing)")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
