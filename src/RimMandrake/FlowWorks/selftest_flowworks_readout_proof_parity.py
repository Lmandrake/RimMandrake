#!/usr/bin/env python3
"""selftest_flowworks_readout_proof_parity.py — READOUT_PROOF_FIX_BYPASSES_MOUSEOVER.

WHY: RM_NorthstarProofs.ProofReadout is the bridge-readable form of the player's cell readout. It used to return
eng.DepthReadoutAt only, skipping the sheet-water (RM_MapComponent_Sheet.ReadoutAt) and natural-liquid fallbacks of
RM_Patch_MouseoverDepth.DepthSuffix, so a proof measured a different line than the player sees. The fix routes the
proof through DepthSuffix itself. Verse-bound code cannot run offline, so this reads the PRODUCTION .cs (comments
masked) and asserts the shape.

CAN IT FAIL: each check is also run against an in-memory copy with the old line spliced back; it must go RED there.

    python3 src/RimMandrake/FlowWorks/selftest_flowworks_readout_proof_parity.py
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

SRC = Path(__file__).resolve().parent / "Source"
PROOFS = SRC / "RM_NorthstarProofs.cs"
MOUSE = SRC / "RM_MouseoverDepth.cs"
NEW = 'return "OK " + (RM_Patch_MouseoverDepth.DepthSuffix(map, c) ?? "-");'
OLD = 'return "OK " + (eng.DepthReadoutAt(c) ?? "-");'


def mask_comments(text: str) -> str:
    """Blank // and /* */ comments, keeping strings and line structure."""
    out, i, n = [], 0, len(text)
    while i < n:
        ch = text[i]
        if ch == '"':
            j = i + 1
            while j < n and text[j] != '"':
                j += 2 if text[j] == "\\" else 1
            out.append(text[i:j + 1]); i = j + 1
        elif text.startswith("//", i):
            j = text.find("\n", i); j = n if j < 0 else j
            out.append(" " * (j - i)); i = j
        elif text.startswith("/*", i):
            j = text.find("*/", i + 2); j = n if j < 0 else j + 2
            out.append(re.sub(r"[^\n]", " ", text[i:j])); i = j
        else:
            out.append(ch); i += 1
    return "".join(out)


def method_body(text: str, sig: str) -> str:
    """The brace-balanced body of the first method whose header matches `sig` (regex), or ''."""
    m = re.search(sig, text)
    if not m:
        return ""
    i = text.find("{", m.end())
    depth, j = 0, i
    while j < len(text):
        if text[j] == "{":
            depth += 1
        elif text[j] == "}":
            depth -= 1
            if depth == 0:
                return text[i:j + 1]
        j += 1
    return ""


def checks(proofs: str, mouse: str) -> list[tuple[str, bool]]:
    pr = method_body(mask_comments(proofs), r"public\s+static\s+string\s+ProofReadout\s*\(")
    ds = method_body(mask_comments(mouse), r"public\s+static\s+string\s+DepthSuffix\s*\(\s*Map\s+map\s*,\s*IntVec3\s+c\s*\)")
    return [
        ("ProofReadout found", bool(pr)),
        ("DepthSuffix(Map, IntVec3) is public static and found", bool(ds)),
        ("ProofReadout returns DepthSuffix(map, c)", "RM_Patch_MouseoverDepth.DepthSuffix(map, c)" in pr),
        ("ProofReadout no longer reads DepthReadoutAt directly", "DepthReadoutAt" not in pr),
        ("DepthSuffix still carries the sheet-water fallback", "RM_MapComponent_Sheet.ReadoutAt(map, c)" in ds),
        ("DepthSuffix still carries the natural-liquid fallback", "RM_LiquidBottleUtility.LiquidAt(" in ds),
        ("the mouseover Prefix prints DepthSuffix", "DepthSuffix(map, c)" in method_body(mask_comments(mouse), r"public\s+static\s+void\s+Prefix\s*\(")),
    ]


def main() -> int:
    proofs, mouse = PROOFS.read_text(encoding="utf-8"), MOUSE.read_text(encoding="utf-8")
    bad = 0
    for name, ok in checks(proofs, mouse):
        print(("PASS " if ok else "FAIL ") + name)
        bad += not ok
    if NEW not in proofs:
        print("FAIL undo splice: fixed line not found verbatim"); bad += 1
    else:
        undone = checks(proofs.replace(NEW, OLD), mouse)
        red = [n for n, ok in undone if not ok]
        ok = "ProofReadout returns DepthSuffix(map, c)" in red and "ProofReadout no longer reads DepthReadoutAt directly" in red
        print(("PASS " if ok else "FAIL ") + "undo (old line spliced back) goes red: " + ", ".join(red))
        bad += not ok
    print("RESULT " + ("GREEN" if not bad else "RED %d" % bad))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
