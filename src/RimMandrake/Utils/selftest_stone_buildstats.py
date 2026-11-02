#!/usr/bin/env python3
"""Selftest for stone_buildstats.py (STONE_BUILDSTATS_TUNE_GRANITE_GETS_RIVALS)."""
from __future__ import annotations

import copy
import io
import json
import sys
from contextlib import redirect_stdout
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import stone_buildstats as sb  # noqa: E402

FAILS = []


def expect(cond: bool, what: str) -> None:
    print(("ok   " if cond else "FAIL ") + what)
    if not cond:
        FAILS.append(what)


def run(table, base, vanilla, src_defs):
    with redirect_stdout(io.StringIO()) as out:
        fails = sb.check(table, base, vanilla, src_defs)
    return fails, out.getvalue()


def main() -> int:
    table = json.loads(sb.TABLE.read_text())
    base, vanilla = sb.load_vanilla()
    # The instrument can see: vanilla granite is the known 1.7 HP factor, 1.25 mass, inherited WorkToBuild 6.
    g = vanilla["BlocksGranite"]
    expect(g["statFactors"]["MaxHitPoints"] == 1.7 and g["statBases"]["Mass"] == 1.25
           and g["statFactors"]["WorkToBuild"] == 6.0, "vanilla granite read and inherited from StoneBlocksBase")
    expect(sb.get(g, "statFactors.Beauty") == 1.0, "absent factor reads as 1")

    fails, out = run(table, base, vanilla, {})
    expect(fails == [], f"shipped table passes ({fails})")
    expect(out.count("PENDING") == len(table["stones"]), "unbuilt stones print PENDING")

    t = copy.deepcopy(table)
    t["stones"]["basalt"]["statBases"]["Mass"] = 1.2
    fails, _ = run(t, base, vanilla, {})
    expect(any("basalt: claim statBases.Mass max" in f for f in fails), "basalt lighter than granite fails its claim")

    t = copy.deepcopy(table)
    t["stones"]["pumice"]["statFactors"]["MaxHitPoints"] = 0.3
    fails, _ = run(t, base, vanilla, {})
    expect(any("outside envelope" in f for f in fails), "out-of-envelope number fails")

    t = copy.deepcopy(table)
    t["stones"]["obsidian"] = copy.deepcopy(t["stones"]["basalt"])
    t["stones"]["obsidian"]["claims"] = []
    fails, _ = run(t, base, vanilla, {})
    expect(any("identical effective numbers" in f for f in fails), "two identical stones fail")

    t = copy.deepcopy(table)
    t["stones"]["basalt"]["defName"] = "RM_BlocksBasalt"
    want = sb.table_stats(t["stones"]["basalt"])
    fails, out = run(t, base, vanilla, {"RM_BlocksBasalt": (Path("x.xml"), want)})
    expect(fails == [] and "OK basalt" in out, "built def carrying the table's numbers passes")
    drift = copy.deepcopy(want)
    drift["statFactors"]["MaxHitPoints"] = 1.7
    fails, _ = run(t, base, vanilla, {"RM_BlocksBasalt": (Path("x.xml"), drift)})
    expect(any("table says" in f for f in fails), "built def drifting from the table fails")
    fails, _ = run(t, base, vanilla, {})
    expect(any("no src ThingDef" in f for f in fails), "registered defName with no def fails")

    fails, _ = run(table, base, vanilla, {"RUT_SaltRockBlocks": (Path("y.xml"), want)})
    expect(any("not registered" in f for f in fails), "unregistered salt-rock block fails")

    fails, _ = run(table, base, vanilla, {"RM_BlocksTuff": (Path("z.xml"), want)})
    expect(any("pumice block" in f for f in fails), "unregistered tuff block (an alias) fails")

    fails, _ = run(table, base, vanilla, sb.src_block_defs(sb.REPO / "src"))
    expect(fails == [], f"live src passes ({fails})")

    print(f"selftest_stone_buildstats: {'FAIL ' + str(len(FAILS)) if FAILS else 'PASS'}")
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
