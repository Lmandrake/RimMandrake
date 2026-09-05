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
    paint: str | None = None         # vanilla PaintColorDef (owner, 2026-08-28)
    extra: dict | None = None        # identity-grade payload from a live EXPORT only:
                                     # quality/hitPoints/stackCount/faction/contents/
                                     # bills/storage. Authoring code never sets this;
                                     # the placer replays what it can and reports the rest.
    overlay: bool = False            # a NON-EDIFICE thing that shares its cell with an
                                     # edifice: a wall lamp (building.isAttachment, sits on
                                     # the floor cell in front of its wall), a floor decal or
                                     # sign (altitudeLayer Floor, fillPercent 0). Verified
                                     # against GenSpawn.SpawningWipes (1.6): a non-edifice
                                     # never wipes and is never wiped by an edifice, so the
                                     # engine exempts these from cell/footprint collision.
                                     # Only Ctx.place_overlay/wall_attach set this.


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


@dataclass
class Clear:
    """RIMPLACE_ENGINE_DELTAS_1 E1. A rect the GenStep must destroy BEFORE any
    FOUNDATION/terrain/things: mode="all" also mines out natural rock in the
    rect (replacing it with the matching rough-rock TerrainDef, looked up per
    rock type at GenStep-time - see GenStep_RimplacePlan.ExecuteClear, never
    hardcoded here); mode="soft" leaves rock standing (plants/filth/chunks/
    items only) for a template that wants to keep a rock lip (a cave mouth).

    A non-rectangular ("blob") clear is authored as a template loop of many
    1x1 Clear ops rather than a dedicated shape - `ctx:clear` takes any w/h,
    including 1x1, and a Lua for-loop over a blob's cells is all a template
    needs; no separate IR shape was worth the complexity for this pass.
    """
    x: int
    z: int
    w: int
    h: int
    mode: str = "all"          # "all" | "soft"


@dataclass
class Run:
    """E2. Extend `defName` from (x,z) toward the map edge in cardinal
    direction `dir` ("N"/"E"/"S"/"W"). This is engine-side (GenStep-time) by
    necessity: a plan is authored at small offline coordinates and cannot
    know the real map's edge, so the walk itself happens in C#
    (GenStep_RimplacePlan.ExecuteRun), not here."""
    x: int
    z: int
    dir: str
    defName: str
    stuff: str | None = None


@dataclass
class Pawn:
    """E3. Spawn a pawn (state="alive") or its remains (state="dead" ==
    freshly-killed corpse, "dessicated", "skeleton" - RimWorld's CompRottable
    has no stage past Dessicated, so "skeleton" reads as the same terminal
    RotStage; see GenStep_RimplacePlan.ExecutePawn). faction is "wild" (no
    Faction, a feral creature/beast), a real FactionDef defName, or - per the
    spec, checked at record time in Ctx.pawn - NEVER "player"."""
    kindDef: str
    x: int
    z: int
    faction: str = "wild"
    state: str = "alive"


class BuildPlan:
    """What every generator emits and the planner consumes."""

    def __init__(self, meta: dict[str, Any]):
        self.meta = meta
        self.things: list[Thing] = []
        self.terrain: dict[tuple[int, int], str] = {}
        self.foundation: dict[tuple[int, int], str] = {}    # 1.6 third grid (Substructure)
        self.roof: dict[tuple[int, int], str] = {}
        self.floor_color: dict[tuple[int, int], str] = {}   # cell -> ColorDef
        self.rooms: list[Room] = []
        self.notes: list[str] = []
        self.refusals: list[Refusal] = []
        self.clears: list[Clear] = []        # E1
        self.runs: list[Run] = []            # E2
        self.pawns: list[Pawn] = []          # E3

    # -- emit ---------------------------------------------------------------
    def add_thing(self, defName, x, z, rot=0, stuff=None, role=None,
                  paint=None, extra=None, overlay=False):
        self.things.append(Thing(defName, int(x), int(z), int(rot), stuff, role,
                                 paint, extra, bool(overlay)))

    def set_terrain(self, x, z, defName):
        self.terrain[(int(x), int(z))] = defName

    def set_roof(self, x, z, defName):
        self.roof[(int(x), int(z))] = defName

    def set_floor_color(self, x, z, defName):
        self.floor_color[(int(x), int(z))] = defName

    def set_foundation(self, x, z, defName):
        self.foundation[(int(x), int(z))] = defName

    def add_room(self, rid, role, rect: Rect):
        r = Room(rid, role, rect)
        self.rooms.append(r)
        return r

    def add_clear(self, x, z, w, h, mode="all"):
        c = Clear(int(x), int(z), int(w), int(h), str(mode))
        self.clears.append(c)
        return c

    def add_run(self, x, z, dir, defName, stuff=None):
        r = Run(int(x), int(z), str(dir), str(defName), str(stuff) if stuff else None)
        self.runs.append(r)
        return r

    def add_pawn(self, kindDef, x, z, faction="wild", state="alive"):
        p = Pawn(str(kindDef), int(x), int(z), str(faction), str(state))
        self.pawns.append(p)
        return p

    def refuse(self, what, reason, x=None, z=None,
               level="WARN", code="generator-refusal"):
        self.refusals.append(Refusal(what, reason, x, z, level, code))

    # -- query --------------------------------------------------------------
    def thing_at(self, x, z):
        return [t for t in self.things if t.x == x and t.z == z]

    def occupied(self, x, z) -> bool:
        """An EDIFICE stands here. Overlays (wall lamps, floor decals) do not
        count: a chair may share a cell with the decal under it."""
        return any(not t.overlay for t in self.thing_at(x, z))

    # -- serialise ----------------------------------------------------------
    def to_dict(self) -> dict:
        return {
            "meta": self.meta,
            "things": [asdict(t) for t in self.things],
            "terrain": [{"x": x, "z": z, "def": d} for (x, z), d in sorted(self.terrain.items())],
            "foundation": [{"x": x, "z": z, "def": d} for (x, z), d in sorted(self.foundation.items())],
            "roof": [{"x": x, "z": z, "def": d} for (x, z), d in sorted(self.roof.items())],
            "floorColor": [{"x": x, "z": z, "def": d} for (x, z), d in sorted(self.floor_color.items())],
            "rooms": [{"id": r.id, "role": r.role, "rect": r.rect.as_list(),
                       "doors": [list(d) for d in r.doors]} for r in self.rooms],
            "notes": self.notes,
            "refusals": [asdict(r) for r in self.refusals],
            "clears": [asdict(c) for c in self.clears],
            "runs": [asdict(r) for r in self.runs],
            "pawns": [asdict(p) for p in self.pawns],
        }

    def to_json(self, indent=2) -> str:
        return json.dumps(self.to_dict(), indent=indent)

    def defnames(self) -> set[str]:
        """Every defName this plan will ask the game for. The verifier's input."""
        out = {t.defName for t in self.things}
        out |= {t.stuff for t in self.things if t.stuff}
        out |= {t.paint for t in self.things if t.paint}     # ColorDefs are defs too
        out |= set(self.terrain.values())
        out |= set(self.foundation.values())
        out |= set(self.roof.values())
        out |= set(self.floor_color.values())
        out |= {r.defName for r in self.runs} | {r.stuff for r in self.runs if r.stuff}
        out |= {p.kindDef for p in self.pawns}    # a PawnKindDef, not a ThingDef -
        # the verifier's `defs` table is keyed by name across every def TYPE, so
        # this checks it exists at all, which is the useful half of "never guess".
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
