#!/usr/bin/env python3
"""Hold our new stone blocks to their balance table (STONE_BUILDSTATS_TUNE_GRANITE_GETS_RIVALS).

    python3 src/RimMandrake/Utils/stone_buildstats.py check      exit 0 = every check passes
    python3 src/RimMandrake/Utils/stone_buildstats.py table      effective numbers, vanilla beside ours

The table (design/RimMandrake/world_remake_2026-10-19/stone_buildstats_table.json) gives each new stone
(basalt, pumice, salt rock, obsidian; 12_rocks_design.md idea 4) its stuffProps as overrides on vanilla
StoneBlocksBase. The vanilla blocks are read from the installed Core Various_Stone.xml, never retyped.
Checks:
  1. every number sits inside the table's envelope;
  2. each stone's identity claims hold as a measured extreme (strict) over vanilla + table stones;
  3. no two stones (vanilla or ours) have identical effective numbers;
  4. a stone whose defName is set must exist in src as a ThingDef with ParentName StoneBlocksBase and
     carry exactly the table's numbers; defName null prints PENDING (the block is not built yet);
  5. a src block def with ParentName StoneBlocksBase whose defName names a table stone but is not
     registered in the table fails (a built stone must not drift from its numbers unseen).
Override the game Data folder with RM_RIMWORLD_DATA.
"""
from __future__ import annotations

import json
import os
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
TABLE = REPO / "design/RimMandrake/world_remake_2026-10-19/stone_buildstats_table.json"
GAME_DATA = os.environ.get("RM_RIMWORLD_DATA",
                           "/mnt/c/Program Files (x86)/Steam/steamapps/common/RimWorld/Data")
VANILLA_XML = "Core/Defs/ThingDefs_Misc/Various_Stone.xml"
SECTIONS = ("statBases", "stuffProps/statFactors", "stuffProps/statOffsets")
VANILLA_STONES = ("BlocksGranite", "BlocksMarble", "BlocksLimestone", "BlocksSlate", "BlocksSandstone")


def _key(section: str) -> str:
    return section.split("/")[-1]


def read_def(node: ET.Element) -> dict:
    """{'statBases': {...}, 'statFactors': {...}, 'statOffsets': {...}} of one def node, floats."""
    out = {}
    for sec in SECTIONS:
        e = node.find(sec)
        out[_key(sec)] = {c.tag: float(c.text) for c in e} if e is not None else {}
    return out


def merge(base: dict, child: dict) -> dict:
    """RimWorld XML inheritance for these maps: a child's named stat replaces the parent's, others stay."""
    return {k: {**base.get(k, {}), **child.get(k, {})} for k in ("statBases", "statFactors", "statOffsets")}


def load_vanilla(data_dir: str = GAME_DATA) -> tuple[dict, dict]:
    path = Path(data_dir) / VANILLA_XML
    if not path.is_file():
        raise SystemExit(f"stone_buildstats: vanilla stone defs not found at {path} (set RM_RIMWORLD_DATA)")
    root = ET.parse(path).getroot()
    base = next((d for d in root if d.get("Name") == "StoneBlocksBase"), None)
    if base is None:
        raise SystemExit(f"stone_buildstats: no StoneBlocksBase in {path}")
    base_stats = read_def(base)
    stones = {}
    for d in root:
        if d.findtext("defName") in VANILLA_STONES:
            stones[d.findtext("defName")] = merge(base_stats, read_def(d))
    missing = set(VANILLA_STONES) - set(stones)
    if missing:
        raise SystemExit(f"stone_buildstats: vanilla blocks missing from {path}: {sorted(missing)}")
    return base_stats, stones


def table_stats(entry: dict) -> dict:
    return {k: {s: float(v) for s, v in entry.get(k, {}).items()} for k in ("statBases", "statFactors", "statOffsets")}


def get(stats: dict, dotted: str) -> float | None:
    """An absent factor is 1 and an absent offset 0, as in game; an absent base stat is None."""
    sec, stat = dotted.split(".", 1)
    return stats.get(sec, {}).get(stat, {"statFactors": 1.0, "statOffsets": 0.0}.get(sec))


def src_block_defs(src: Path) -> dict:
    """defName -> (path, stats) for every src ThingDef whose ParentName is StoneBlocksBase."""
    found = {}
    for p in src.rglob("*.xml"):
        try:
            root = ET.parse(p).getroot()
        except ET.ParseError:
            continue
        for d in root.iter("ThingDef"):
            if d.get("ParentName") == "StoneBlocksBase" and d.findtext("defName"):
                found[d.findtext("defName")] = (p, read_def(d))
    return found


def check(table: dict, base: dict, vanilla: dict, src_defs: dict) -> list[str]:
    """Returns failure lines; PENDING/OK lines are printed, not returned."""
    fails = []
    env = table["envelope"]
    ours = {name: merge(base, table_stats(e)) for name, e in table["stones"].items()}
    pool = {**vanilla, **ours}
    for name, entry in table["stones"].items():
        raw = table_stats(entry)
        for sec, stats in raw.items():
            for stat, v in stats.items():
                bounds = env.get(f"{sec}.{stat}")
                if bounds and not bounds[0] <= v <= bounds[1]:
                    fails.append(f"{name}: {sec}.{stat}={v} outside envelope {bounds}")
        for claim in entry["claims"]:
            mine = get(ours[name], claim["stat"])
            others = [get(s, claim["stat"]) for n, s in pool.items() if n != name]
            if mine is None or None in others:
                fails.append(f"{name}: claim {claim['stat']} is unmeasured on some stone (base stat absent)")
                continue
            ok = mine > max(others) if claim["extreme"] == "max" else mine < min(others)
            if not ok:
                fails.append(f"{name}: claim {claim['stat']} {claim['extreme']} fails ({mine} vs {sorted(others)})")
    names = sorted(pool)
    for i, a in enumerate(names):
        for b in names[i + 1:]:
            if pool[a] == pool[b]:
                fails.append(f"{a} and {b} have identical effective numbers")
    registered = {}
    for name, entry in table["stones"].items():
        dn = entry.get("defName")
        if not dn:
            print(f"PENDING {name}: no block ThingDef yet (BIOME_STONES_DESIGN_BASALT_JOINS_THE_BAND builds it)")
            continue
        registered[dn] = name
        if dn not in src_defs:
            fails.append(f"{name}: defName {dn} set in table but no src ThingDef with ParentName StoneBlocksBase")
            continue
        path, got = src_defs[dn]
        want = table_stats(entry)
        if got != want:
            fails.append(f"{name}: {dn} in {path} carries {got}, table says {want}")
        else:
            print(f"OK {name}: {dn} matches the table")
    words = {name: [name.replace("_", "").lower()] + [a.lower() for a in e.get("aliases", [])]
             for name, e in table["stones"].items()}
    for dn, (path, _) in src_defs.items():
        low = dn.lower()
        for name, ws in words.items():
            if any(w in low for w in ws) and dn not in registered:
                fails.append(f"{dn} ({path}) looks like the {name} block but is not registered in the table")
    return fails


def main(argv: list[str]) -> int:
    cmd = argv[1] if len(argv) > 1 else "check"
    table = json.loads(TABLE.read_text())
    base, vanilla = load_vanilla()
    if cmd == "table":
        ours = {n: merge(base, table_stats(e)) for n, e in table["stones"].items()}
        cols = sorted({f"{s}.{k}" for st in {**vanilla, **ours}.values() for s in st for k in st[s]})
        print("stone," + ",".join(cols))
        for n, st in {**vanilla, **ours}.items():
            print(n + "," + ",".join("" if get(st, c) is None else f"{get(st, c):g}" for c in cols))
        return 0
    if cmd != "check":
        print(__doc__)
        return 2
    fails = check(table, base, vanilla, src_block_defs(REPO / "src"))
    for f in fails:
        print("FAIL", f)
    print(f"stone_buildstats: {len(table['stones'])} stones vs {len(vanilla)} vanilla blocks; "
          f"{'FAIL ' + str(len(fails)) if fails else 'PASS'}")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
