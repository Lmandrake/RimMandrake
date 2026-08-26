"""rimplace.core - the BuildPlan IR, the seeded RNG, and the palette.

The IR is PURE DATA. Nothing in this file imports Lua, talks to the bridge, or
needs a running game. That is the whole point: everything upstream of the bridge
is testable in milliseconds, and a 25-minute cold load is never spent on a bug
that a dataclass could have caught.
"""
from __future__ import annotations

import json
import random
from dataclasses import dataclass, field, asdict
from typing import Any


# --------------------------------------------------------------------------- #
#  Geometry
# --------------------------------------------------------------------------- #
@dataclass(frozen=True)
class Rect:
    x: int
    z: int
    w: int
    h: int

    @property
    def x2(self) -> int: return self.x + self.w - 1

    @property
    def z2(self) -> int: return self.z + self.h - 1

    def cells(self):
        for zz in range(self.z, self.z + self.h):
            for xx in range(self.x, self.x + self.w):
                yield xx, zz

    def edge_cells(self):
        for xx, zz in self.cells():
            if xx in (self.x, self.x2) or zz in (self.z, self.z2):
                yield xx, zz

    def inner(self) -> "Rect":
        return Rect(self.x + 1, self.z + 1, max(0, self.w - 2), max(0, self.h - 2))

    def contains(self, x: int, z: int) -> bool:
        return self.x <= x <= self.x2 and self.z <= z <= self.z2

    def as_list(self): return [self.x, self.z, self.w, self.h]


# --------------------------------------------------------------------------- #
#  Plan entities
# --------------------------------------------------------------------------- #
@dataclass
class Thing:
    defName: str
    x: int
    z: int
    rot: int = 0
    stuff: str | None = None
    role: str | None = None          # provenance: which palette role produced this


@dataclass
class Room:
    id: str
    role: str
    rect: Rect
    doors: list[tuple[int, int]] = field(default_factory=list)


@dataclass
class Refusal:
    what: str
    reason: str
    x: int | None = None
    z: int | None = None
    # 🔑 A refusal is not always a WARN. "the palette has no entry for X" is a
    # note; "this thing would be destroyed by the next one" is an ERROR, and
    # lint must be able to tell them apart without matching on prose.
    level: str = "WARN"
    code: str = "generator-refusal"


class BuildPlan:
    """What every generator emits and the planner consumes."""

    def __init__(self, meta: dict[str, Any]):
        self.meta = meta
        self.things: list[Thing] = []
        self.terrain: dict[tuple[int, int], str] = {}
        self.roof: dict[tuple[int, int], str] = {}
        self.rooms: list[Room] = []
        self.notes: list[str] = []
        self.refusals: list[Refusal] = []

    # -- emit ---------------------------------------------------------------
    def add_thing(self, defName, x, z, rot=0, stuff=None, role=None):
        self.things.append(Thing(defName, int(x), int(z), int(rot), stuff, role))

    def set_terrain(self, x, z, defName):
        self.terrain[(int(x), int(z))] = defName

    def set_roof(self, x, z, defName):
        self.roof[(int(x), int(z))] = defName

    def add_room(self, rid, role, rect: Rect):
        r = Room(rid, role, rect)
        self.rooms.append(r)
        return r

    def refuse(self, what, reason, x=None, z=None,
               level="WARN", code="generator-refusal"):
        self.refusals.append(Refusal(what, reason, x, z, level, code))

    # -- query --------------------------------------------------------------
    def thing_at(self, x, z):
        return [t for t in self.things if t.x == x and t.z == z]

    def occupied(self, x, z) -> bool:
        return bool(self.thing_at(x, z))

    # -- serialise ----------------------------------------------------------
    def to_dict(self) -> dict:
        return {
            "meta": self.meta,
            "things": [asdict(t) for t in self.things],
            "terrain": [{"x": x, "z": z, "def": d} for (x, z), d in sorted(self.terrain.items())],
            "roof": [{"x": x, "z": z, "def": d} for (x, z), d in sorted(self.roof.items())],
            "rooms": [{"id": r.id, "role": r.role, "rect": r.rect.as_list(),
                       "doors": [list(d) for d in r.doors]} for r in self.rooms],
            "notes": self.notes,
            "refusals": [asdict(r) for r in self.refusals],
        }

    def to_json(self, indent=2) -> str:
        return json.dumps(self.to_dict(), indent=indent)

    def defnames(self) -> set[str]:
        """Every defName this plan will ask the game for. The verifier's input."""
        out = {t.defName for t in self.things}
        out |= {t.stuff for t in self.things if t.stuff}
        out |= set(self.terrain.values())
        out |= set(self.roof.values())
        return {d for d in out if d}


# --------------------------------------------------------------------------- #
#  Deterministic RNG
# --------------------------------------------------------------------------- #
class SeededRng:
    """Same seed + same template + same params => byte-identical plan.

    Without this nothing is reproducible and no generated-content bug is ever
    diagnosable, because you cannot get the same house back twice.
    """

    def __init__(self, seed: int):
        self.seed = int(seed)
        self._r = random.Random(self.seed)

    def int(self, a, b): return self._r.randint(int(a), int(b))
    def chance(self, p): return self._r.random() < float(p)
    def pick(self, seq):
        seq = list(seq)
        return seq[self._r.randrange(len(seq))] if seq else None
    def shuffle(self, seq):
        s = list(seq)
        self._r.shuffle(s)
        return s


# --------------------------------------------------------------------------- #
#  Palette
# --------------------------------------------------------------------------- #
TECH_ORDER = ["Animal", "Neolithic", "Medieval", "Industrial", "Spacer",
              "Ultra", "Archotech"]


def tech_at_most(tech: str, ceiling: str) -> bool:
    try:
        return TECH_ORDER.index(tech) <= TECH_ORDER.index(ceiling)
    except ValueError:
        return False


class Palette:
    """Maps an abstract ROLE (WALL, BED, LIGHT...) to a concrete defName.

    🔴 Every defName in the palette file is UNVERIFIED until checked against the
    live def dump. `rimplace verify` does that. The compiler REFUSES to emit
    bridge calls for unverified defs unless explicitly overridden - a wrong
    defName is the single most expensive mistake this tool could make, because
    it costs a game load to discover.
    """

    def __init__(self, data: dict, faction: str, tech: str, wealth: str):
        self.data = data
        self.faction = faction
        self.tech = tech
        self.wealth = wealth
        self._resolved: dict[str, str] = {}
        self.missing: list[str] = []

        base = dict(data.get("default", {}))
        for key in (f"tech:{tech}", f"wealth:{wealth}", f"faction:{faction}"):
            base.update(data.get(key, {}))
        self._table = base

    def get(self, role: str) -> str | None:
        role = role.upper()
        v = self._table.get(role)
        if v is None:
            if role not in self.missing:
                self.missing.append(role)
            return None
        return v

    def roles(self): return sorted(self._table)
