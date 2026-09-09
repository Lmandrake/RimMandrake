#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""rosters_residency.py — THE residency join. One shared loader; every consumer
imports it, nobody re-derives residency from the register.

Why this module exists
----------------------
`creature_register_rows.json` is the STATS source (bodySize, meat, tools, wildness,
art …) and stays that. But its `biomes`, `group` and `topCommonality` fields are the
MODS' OWN default residency — where Alpha Animals, Biomes! Caverns, Jurassic etc.
ship their creatures on a vanilla planet. Ash'karr's assignment (owner rulings
2026-09-09, BIOME_FAUNA_ASSIGNMENT_SITTING_1) is held in
`design/Jawa/worldbuilding/biomes/rosters/*.json` + `_global.json`. Those two
disagree about almost every row, so reading the register's residency after the
assignment pass is reading a stale planet.

  register  -> STATS only          (bodySize, meatAmount, tools, wildness, art…)
  rosters   -> RESIDENCY, always   (which biome, which sheet, what commonality)

Anything that needs both joins them here.

Shape
-----
    from rosters_residency import load
    R = load()
    R.residency["Bantha"]        -> [Residency(biome='Desert', sheet='desert',
                                                commonality=0.8, injection=False, …)]
    R.residents("Desert")        -> [Residency(...)]  (fauna landed in that BiomeDef)
    R.reserve                    -> set of homeless-reserve defNames (486)
    R.cuts                       -> {defName: reason}  (Cherry Picker cut list, 88)
    R.flora_residency["AB_..."]  -> [Residency(...)]
    R.primary_sheet("Bantha")    -> "desert"   (highest-commonality home; ties by name)

Injection layers (`fall_line`, `wreck_fields`, `the_lantern_deeps`) declare the
UNDERLYING BiomeDefs they inject over; their rows are ADDITIONS, flagged
`injection=True` so a figure can mark them distinctly instead of pretending they
are a biome of their own (ban 1: they are not BiomeDefs).

Run directly for a one-screen census:
    python3 design/Jawa/worldbuilding/review/rosters_residency.py
"""
from __future__ import annotations

import json
import os
from collections import defaultdict
from dataclasses import dataclass
from typing import Dict, List, Optional, Set

HERE = os.path.dirname(os.path.abspath(__file__))
ROSTER_DIR = os.path.abspath(os.path.join(HERE, "..", "biomes", "rosters"))
REGISTER = os.path.join(HERE, "creature_register_rows.json")


@dataclass(frozen=True)
class Residency:
    """One landed row: this def lives in this BiomeDef at this commonality."""
    defName: str
    biome: str          # BiomeDef defName
    sheet: str          # roster sheet stem (= biomes/<sheet>.md)
    commonality: float  # DESIGN CHOICE, not a measured stat
    injection: bool     # True = injection layer addition, not a biome of its own
    action: Optional[str] = None   # keep / import / adjust-keep (fauna only)
    band: Optional[str] = None
    law: Optional[str] = None

    @property
    def kind(self) -> str:
        return "flora" if self.band == "__flora__" else "fauna"


class Rosters:
    def __init__(self, sheets: Dict[str, dict], glob: dict):
        self.sheets = sheets
        self.glob = glob

        self.residency: Dict[str, List[Residency]] = defaultdict(list)
        self.flora_residency: Dict[str, List[Residency]] = defaultdict(list)
        self._by_biome: Dict[str, List[Residency]] = defaultdict(list)
        self._flora_by_biome: Dict[str, List[Residency]] = defaultdict(list)
        self.flora_purged: Dict[str, List[dict]] = {}
        self.evictions: Dict[str, List[dict]] = {}
        self.stat_adjustments: List[dict] = []
        self.new_defs: Dict[str, List[dict]] = {}

        for sheet, d in sheets.items():
            inj = bool(d.get("injection_layer") or d.get("injection"))
            biomes = list(d.get("defNames") or [])
            for row in d.get("fauna") or []:
                for b in biomes:
                    r = Residency(row["def"], b, sheet, float(row.get("commonality") or 0.0),
                                  inj, row.get("action"), row.get("band"), row.get("law"))
                    self.residency[row["def"]].append(r)
                    self._by_biome[b].append(r)
            for row in d.get("flora") or []:
                for b in biomes:
                    r = Residency(row["def"], b, sheet, float(row.get("commonality") or 0.0),
                                  inj, None, "__flora__", row.get("law"))
                    self.flora_residency[row["def"]].append(r)
                    self._flora_by_biome[b].append(r)
            self.flora_purged[sheet] = list(d.get("flora_purged") or [])
            self.evictions[sheet] = list(d.get("evictions") or [])
            self.new_defs[sheet] = list(d.get("new_defs") or [])
            for a in d.get("stat_adjustments") or []:
                self.stat_adjustments.append(dict(a, sheet=sheet))

        self.residency = dict(self.residency)
        self.flora_residency = dict(self.flora_residency)

        # biome defNames, in sheet order (stable across runs)
        seen, order = set(), []
        for sheet in sheets:
            for b in sheets[sheet].get("defNames") or []:
                if b not in seen:
                    seen.add(b)
                    order.append(b)
        self.biome_defs: List[str] = order
        self.sheets_of_biome: Dict[str, List[str]] = defaultdict(list)
        for sheet, d in sheets.items():
            for b in d.get("defNames") or []:
                self.sheets_of_biome[b].append(sheet)
        self.sheets_of_biome = dict(self.sheets_of_biome)

        self.reserve: Set[str] = set(glob.get("reserve_for_events") or [])
        self.reserve_evicted_from: Dict[str, List[str]] = dict(glob.get("reserve_evicted_from") or {})
        self.cuts: Dict[str, str] = {c["def"]: c.get("reason", "") for c in (glob.get("cuts") or [])}
        self.cut_rows: List[dict] = list(glob.get("cuts") or [])
        self.grindterra_defs: Set[str] = set(glob.get("grindterra_defs") or [])
        self.ruled: dict = dict(glob.get("ruled") or {})
        self.measured: dict = dict(glob.get("measured") or {})

    # ---------------------------------------------------------------- accessors
    def residents(self, biome: str) -> List[Residency]:
        """Fauna landed in this BiomeDef (injection-layer additions included)."""
        return list(self._by_biome.get(biome, []))

    def flora_residents(self, biome: str) -> List[Residency]:
        return list(self._flora_by_biome.get(biome, []))

    def rostered_defs(self) -> Set[str]:
        return set(self.residency)

    def rostered_flora(self) -> Set[str]:
        return set(self.flora_residency)

    def spread(self, defName: str) -> int:
        """How many distinct BiomeDefs this def is landed in."""
        return len({r.biome for r in self.residency.get(defName, [])})

    def top_commonality(self, defName: str) -> float:
        rs = self.residency.get(defName, [])
        return max((r.commonality for r in rs), default=0.0)

    def primary_sheet(self, defName: str) -> Optional[str]:
        """Highest-commonality home sheet; ties broken by sheet name for stability."""
        rs = self.residency.get(defName, [])
        if not rs:
            return None
        best = sorted({(r.sheet, max(x.commonality for x in rs if x.sheet == r.sheet)) for r in rs},
                      key=lambda t: (-t[1], t[0]))
        return best[0][0]

    def sheet_doc(self, sheet: str) -> dict:
        return self.sheets.get(sheet, {})

    def tiles(self, sheet: str) -> int:
        return int(self.sheets.get(sheet, {}).get("tiles") or 0)

    def is_injection(self, sheet: str) -> bool:
        d = self.sheets.get(sheet, {})
        return bool(d.get("injection_layer") or d.get("injection"))


_CACHE: Optional[Rosters] = None


def load(roster_dir: str = ROSTER_DIR, refresh: bool = False) -> Rosters:
    global _CACHE
    if _CACHE is not None and not refresh and roster_dir == ROSTER_DIR:
        return _CACHE
    sheets = {}
    glob = {}
    for fn in sorted(os.listdir(roster_dir)):
        if not fn.endswith(".json"):
            continue
        with open(os.path.join(roster_dir, fn), encoding="utf-8") as f:
            d = json.load(f)
        if fn == "_global.json":
            glob = d
        else:
            sheets[d.get("sheet") or fn[:-5]] = d
    if not glob:
        raise RuntimeError("rosters/_global.json missing — the residency join is incomplete")
    R = Rosters(sheets, glob)
    if roster_dir == ROSTER_DIR:
        _CACHE = R
    return R


def load_register_stats(path: str = REGISTER) -> Dict[str, dict]:
    """defName -> register row. STATS ONLY — never read `biomes`/`group`/
    `topCommonality` from these rows; residency comes from load() above."""
    with open(path, encoding="utf-8") as f:
        return {r["defName"]: r for r in json.load(f)["rows"]}


def register_meta(path: str = REGISTER) -> dict:
    with open(path, encoding="utf-8") as f:
        return json.load(f)["meta"]


if __name__ == "__main__":
    R = load()
    print("sheets           %d (%d injection layers)"
          % (len(R.sheets), sum(1 for s in R.sheets if R.is_injection(s))))
    print("BiomeDefs bound  %d" % len(R.biome_defs))
    print("rostered fauna   %d defs, %d (def, biome) rows"
          % (len(R.residency), sum(len(v) for v in R.residency.values())))
    print("rostered flora   %d defs, %d rows"
          % (len(R.flora_residency), sum(len(v) for v in R.flora_residency.values())))
    print("reserve          %d   cuts %d   grindterra %d"
          % (len(R.reserve), len(R.cuts), len(R.grindterra_defs)))
    print("_global measured %s" % json.dumps(R.measured))
    print("\nper-biome fauna rows / Σcommonality:")
    for b in sorted(R.biome_defs, key=lambda x: -len(R.residents(x))):
        rs = R.residents(b)
        print("  %-32s %3d rows  Σcomm %6.2f  sheets %s"
              % (b, len(rs), sum(r.commonality for r in rs), ",".join(R.sheets_of_biome[b])))
