#!/usr/bin/env python3
"""size_verdict_check.py -- is a creature-size verdict enacted in the defs?

Item: CREATURE_SIZES_JUDGE_THIRTY_NINE_OFF_CURVE. A judge writes a verdict JSON (for example
design/RimMandrake/creature_size_verdicts_2026-11-27.json) whose `changes` list holds, per PawnKindDef,
the def file and the `new` drawSize of each lifeStage in order. This tool reads each def file and compares
every drawSize under that kind's lifeStages (bodyGraphicData, swimmingGraphicData and any other graphic
of the stage) with `new`, to 0.005.

Only changes with "route": "fixer" are checked; a change routed elsewhere (a held mod's polish list) is
listed, never counted.

USAGE
    python3 src/RimMandrake/Utils/size_verdict_check.py <verdict.json>

EXIT  0 every fixer change is in the defs · 1 at least one is not (each named) · 2 could not look (a file
      or kind missing, a stage count that differs from the verdict, unreadable JSON or XML)
"""
from __future__ import annotations

import json
import os
import sys

from lxml import etree as LX

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", ".."))
TOL = 0.005


def stage_sizes(path: str, kind: str):
    """[[drawSize, ...] per lifeStage] of PawnKindDef `kind` in `path`; None when the kind is absent."""
    tree = LX.parse(path)
    pk = tree.xpath(f'//PawnKindDef[defName="{kind}"]')
    if len(pk) != 1:
        return None
    return [[float(e.text) for e in li.xpath(".//drawSize")] for li in pk[0].xpath("lifeStages/li")]


def check(verdict_path: str) -> int:
    try:
        v = json.load(open(verdict_path, encoding="utf-8"))
    except (OSError, ValueError) as e:
        print(f"COULD NOT LOOK: {verdict_path}: {e}")
        return 2
    blind, off, ok = [], [], []
    for c in v.get("changes", []):
        kind, route = c["kind"], c.get("route")
        if route != "fixer":
            print(f"SKIP     {kind}: routed to {route}")
            continue
        path = os.path.join(ROOT, c["file"])
        try:
            got = stage_sizes(path, kind)
        except (OSError, LX.XMLSyntaxError) as e:
            blind.append(f"{kind}: {c['file']}: {e}")
            continue
        if got is None:
            blind.append(f"{kind}: no single PawnKindDef of that name in {c['file']}")
            continue
        if len(got) != len(c["new"]):
            blind.append(f"{kind}: {len(got)} lifeStages in the def, {len(c['new'])} in the verdict")
            continue
        bad = [(i, sizes, want) for i, (sizes, want) in enumerate(zip(got, c["new"]))
               if not sizes or any(abs(s - want) > TOL for s in sizes)]
        if bad:
            off.append(f"{kind}: " + "; ".join(f"stage {i} draws {sizes}, verdict {want}" for i, sizes, want in bad))
        else:
            ok.append(kind)
    for k in ok:
        print(f"ENACTED  {k}")
    for line in off:
        print(f"NOT YET  {line}")
    for line in blind:
        print(f"COULD NOT LOOK  {line}")
    if blind:
        return 2
    if not ok and not off:
        print("COULD NOT LOOK: the verdict lists no fixer change")
        return 2
    return 1 if off else 0


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(__doc__)
        sys.exit(2)
    sys.exit(check(sys.argv[1]))
