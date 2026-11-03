#!/usr/bin/env python3
"""selftest_flowworks_salt_break_potable.py — the salt-water break sees every potable source (SALT_BREAK_FIX_MISSES_POTABLE_SOURCES).

WHY: GPT review FA_core_sim_3.4 (2026-10-23): RM_SaltBreakUtility.PotableReachable asked only bottles, tanks and
terrain, while JobGiver_RM_Drink also drinks from buckets/barrels, water items and pipe faucets — so a parched pawn
with a bucket of fresh water in reach could still take the brine-drinking break. PotableReachable is Verse-bound (the
C# SelfTest cannot run it), so this reads the PRODUCTION .cs (comments masked) and asserts that every source finder
JobGiver_RM_Drink calls is also asked by PotableReachable, with the Potable filter.

CAN IT FAIL: the source list is read from JobGiver_RM_Drink itself (not hard-coded), and each run applies an undo
splice that removes one source from PotableReachable in memory; the check must go RED on that copy.

    python3 src/RimMandrake/FlowWorks/selftest_flowworks_salt_break_potable.py
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

THIRST = Path(__file__).resolve().parent / "Source" / "Thirst"
FINDER = re.compile(r"\b((?:RM_\w+|Building_RM_\w+)\.(?:Best\w+|TryFindDrinkCell))\(")


def mask_comments(text: str) -> str:
    """Blank // and /* */ comments (keeping strings) so a source named only in a comment does not count."""
    out, i, n = [], 0, len(text)
    while i < n:
        c = text[i]
        if c == '"':
            j = i + 1
            while j < n and text[j] != '"':
                j += 2 if text[j] == "\\" else 1
            out.append(text[i:j + 1]); i = j + 1
        elif text.startswith("//", i):
            j = text.find("\n", i)
            j = n if j < 0 else j
            out.append(" " * (j - i)); i = j
        elif text.startswith("/*", i):
            j = text.find("*/", i + 2)
            j = n if j < 0 else j + 2
            out.append(re.sub(r"[^\n]", " ", text[i:j])); i = j
        else:
            out.append(c); i += 1
    return "".join(out)


def block_after(text: str, anchor: str) -> str | None:
    m = re.search(anchor, text)
    if not m:
        return None
    i = text.find("{", m.end())
    depth = 0
    for j in range(i, len(text)):
        depth += {"{": 1, "}": -1}.get(text[j], 0)
        if depth == 0:
            return text[i:j + 1]
    return None


def finders(block: str) -> set[str]:
    return set(FINDER.findall(block))


def check(salt_src: str, drink_src: str) -> list[str]:
    """Return failures (empty = pass)."""
    fails: list[str] = []
    giver = block_after(drink_src, r"Job\s+TryGiveJob\(Pawn pawn\)")
    reach = block_after(salt_src, r"static\s+bool\s+PotableReachable\(Pawn pawn, float level\)")
    if giver is None or reach is None:
        return ["could not find JobGiver_RM_Drink.TryGiveJob or PotableReachable"]
    want = finders(giver)
    if len(want) < 6:
        fails.append(f"instrument: JobGiver_RM_Drink shows only {len(want)} source finders {sorted(want)} (expected 6)")
    have = finders(reach)
    for f in sorted(want - have):
        fails.append(f"PotableReachable does not ask {f}")
    for call in re.finditer(FINDER, reach):
        tail = reach[call.end():reach.find(")", call.end()) + 1]
        if not re.search(r"\bpotable\)", tail):
            fails.append(f"{call.group(1)} in PotableReachable is not filtered to Potable")
    return fails


def main() -> int:
    salt = mask_comments((THIRST / "RM_SaltBreak.cs").read_text(encoding="utf-8"))
    drink = mask_comments((THIRST / "RM_ThirstJobs.cs").read_text(encoding="utf-8"))
    bad = check(salt, drink)
    for b in bad:
        print("FAIL", b)
    # can-fail: drop each of the three sources the review found missing; each copy must go red.
    undos = ["RM_ThirstContainerUtility.BestContainer(", "RM_WaterItemUtility.BestItem(", "Building_RM_PipeFaucet.BestFaucet("]
    for u in undos:
        if u not in salt:
            print("FAIL undo anchor missing:", u); bad.append(u); continue
        broken = salt.replace(u, "RM_Gone.Missing(")
        if not check(broken, drink):
            print("FAIL undo stayed green:", u); bad.append(u)
    if bad:
        return 1
    n = len(finders(block_after(drink, r"Job\s+TryGiveJob\(Pawn pawn\)")))
    print(f"PASS salt-break PotableReachable asks all {n} drink sources with the Potable filter; {len(undos)} undo splices go red")
    return 0


if __name__ == "__main__":
    sys.exit(main())
