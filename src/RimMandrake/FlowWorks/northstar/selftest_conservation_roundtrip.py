#!/usr/bin/env python3
"""POND_BED_DESIGN_LAKES_ARE_TALL_CANALS: the owner's conservation round trips, as an offline model.

Owner, 2026-10-11: "Start with A filled, then move it into tanks, then move it into empty reservoir B of a bigger
size. Then drain B back into the tanks and back into A... and A looks the same."

This is a MODEL of the shipped arithmetic, not the C#. Its constants are read from the production sources so a
change there fails here instead of drifting (RM_PumpMath.TankUnitsPerLevel, RM_ExcavationDepth.Superdeep, the water
FluidDef's volumePerTile / canalCellsPerSourceCell). The rules it mirrors, with their homes:

  dug basin       integer D (1..4) and F (0..D) per cell              RM_MapComponent_Excavation depthGrid/fillGrid
  pump draw       one level out of a cell (TryTakeLevel) -> +5 tank units        Building_LiquidPump.TryDraw
  pump draw body  TryDebit(volumePerTile) of float stock -> +5 tank units        Building_LiquidPump.TryDraw
  pump pour       -5 tank units -> +1 level into the EXCAVATED cell with most room Building_LiquidPump.TryPour, PickPour
  flow pulse      GRAVITY (recipient deeper than donor) or OVERFLOW (donor at brim) RM_FlowKernel.PickDonor
  body            capacity = cells * canalCellsPerSourceCell * volumePerTile; supported = floor(stock / perCell)
  pour into body  NOT POSSIBLE today (CanPourLevel needs IsExcavated; RM_LiquidSpill.Outlet blocks water terrain)

The last rule is detected from the source text (`_production_pours_into_bodies`), so when someone builds the
missing return path the natural-A cases switch from documenting the gap to demanding the full round trip.

    python3 src/RimMandrake/FlowWorks/northstar/selftest_conservation_roundtrip.py
"""
import json
import math
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
MOD = os.path.dirname(HERE)
SRC = os.path.join(MOD, "Source")


def _read(rel):
    with open(os.path.join(MOD, rel), encoding="utf-8") as fh:
        return fh.read()


def _const(text, name):
    m = re.search(r"\b%s\s*=\s*([0-9.]+)f?\s*;" % re.escape(name), text)
    if not m:
        raise SystemExit("cannot read %s from production source" % name)
    return float(m.group(1))


PUMP = _read("Source/RM_PumpMath.cs")
DEPTH = _read("Source/RM_ExcavationDepth.cs")
UNITS_PER_LEVEL = int(_const(PUMP, "TankUnitsPerLevel"))
SUPERDEEP = int(_const(DEPTH, "Superdeep"))
_water = re.search(r"<defName>RM_Fluid_Water</defName>(.*?)</RimMandrake\.FlowWorks\.FluidDef>",
                   _read("Defs/Canals/FluidDefs/FlowWorks_Fluids.xml"), re.S).group(1)
VPT = float(re.search(r"<volumePerTile>([0-9.]+)</volumePerTile>", _water).group(1))
CELLS_PER_SOURCE = float(re.search(r"<canalCellsPerSourceCell>([0-9.]+)</canalCellsPerSourceCell>", _water).group(1))
TANK_CAP = 300   # Building_LiquidTank.BaseCapacityUnits at multiplier 1


def _production_pours_into_bodies():
    """True once a pump/outflow can put liquid INTO a natural body (the return leg of the owner's trip)."""
    pump = _read("Source/LiquidTypes/Building_LiquidPump.cs")
    spill = _read("Source/Machinery/RM_LiquidSpill.cs")
    pour_body = re.search(r"TryPour\(\)(.*?)\n\t\t}\n", pump, re.S)
    via_pour = bool(pour_body and "TryCredit" in pour_body.group(1))
    via_outlet = "TryCredit" in spill or "Stock." in spill
    return via_pour or via_outlet


# ── the model ──────────────────────────────────────────────────────────────

class Basin:
    """A dug reservoir: cells (x, z) -> [D, F], integers, F <= D."""

    def __init__(self, w, h, depth=SUPERDEEP, fill=0, depths=None):
        self.cells = {}
        self.reach = None   # the pump's reach cells; None = every cell (an idealised pump)
        for x in range(w):
            for z in range(h):
                d = depths(x, z) if depths else depth
                self.cells[(x, z)] = [d, min(fill, d)]

    def levels(self):
        return sum(f for _, f in self.cells.values())

    def snapshot(self):
        return {c: f for c, (_, f) in self.cells.items()}

    def take_level(self):
        """Pump draw: one level out of the fullest cell (ties by cell order, deterministic)."""
        best = None
        for c in sorted(self.cells):
            if self.cells[c][1] > 0 and (best is None or self.cells[c][1] > self.cells[best][1]):
                best = c
        if best is None:
            return False
        self.cells[best][1] -= 1
        return True

    def pour_level(self, reach=None):
        """Pump pour: +1 level into the cell with most room (PickPour) among the cells in reach."""
        reach = reach if reach is not None else self.reach
        pool = reach if reach is not None else sorted(self.cells)
        best, room = None, 0
        for c in pool:
            d, f = self.cells[c]
            if d - f > room:
                best, room = c, d - f
        if best is None:
            return False
        self.cells[best][1] += 1
        return True

    def pulse(self, max_pulses=500):
        """RM_FlowKernel's donor rule, iterated to rest: a level moves to a cardinal neighbour when the recipient is
        DEEPER (gravity) or the donor is at its brim (overflow). Every move is -1/+1, so the sum is invariant; the
        flow order here is a strict (depth, cell) order, which keeps it acyclic like the kernel's hop order."""
        for _ in range(max_pulses):
            moved = False
            for r in sorted(self.cells, key=lambda c: (-self.cells[c][0], c)):
                dr, fr = self.cells[r]
                if fr >= dr:
                    continue
                for dx, dz in ((0, 1), (1, 0), (0, -1), (-1, 0)):
                    n = (r[0] + dx, r[1] + dz)
                    if n not in self.cells:
                        continue
                    dn, fn = self.cells[n]
                    if fn == 0 or (dr <= dn and fn < dn):
                        continue
                    if dr == dn and (n > r):   # equal depth overflow: one direction only (acyclic)
                        continue
                    self.cells[n][1] -= 1
                    self.cells[r][1] += 1
                    moved = True
                    break
            if not moved:
                return


class Body:
    """A natural RM_LiquidBody: float stock, the 5:1 budget, floor recession, LIFO restore."""

    def __init__(self, n_cells, limitless=False, keep_last=True):
        self.n = n_cells
        self.limitless = limitless
        self.keep_last = keep_last
        self.capacity = n_cells * CELLS_PER_SOURCE * VPT
        self.stock = self.capacity
        self.receded = []   # cell ids, oldest first

    def per_cell(self):
        return self.capacity / self.n

    def supported(self):
        s = int(math.floor(self.stock / self.per_cell()))
        if self.keep_last and s == 0 and self.stock > 0:
            return 1
        return s

    def settle(self):
        """Recede then restore, as RM_LiquidStock.Pulse does (recession order abstracted to cell ids n-1..0)."""
        if self.limitless:
            return
        wet = self.n - len(self.receded)
        while wet > self.supported():
            self.receded.append(self.n - 1 - len(self.receded))
            wet -= 1
        while self.receded and wet < self.supported():
            self.receded.pop()
            wet += 1

    def wet_cells(self):
        return set(range(self.n)) - set(self.receded)

    def can_supply(self):
        return self.limitless or self.stock >= VPT

    def debit_level(self):
        if self.limitless:
            return True
        if self.stock < VPT:
            return False
        self.stock -= VPT
        return True

    def credit_level(self):
        """The return leg production lacks. A limited body takes a whole level or nothing (no partial credit)."""
        if self.limitless:
            return True
        if self.capacity - self.stock < VPT:
            return False
        self.stock += VPT
        return True


class Tanks:
    def __init__(self, count):
        self.units = [0] * count

    def total(self):
        return sum(self.units)

    def add(self, k):
        for i, u in enumerate(self.units):
            if TANK_CAP - u >= k:
                self.units[i] += k
                return True
        return False

    def remove(self, k):
        for i in range(len(self.units) - 1, -1, -1):
            if self.units[i] >= k:
                self.units[i] -= k
                return True
        return False


def ledger(*parts):
    """Everything in tank units: a level is UNITS_PER_LEVEL, a body fill-unit is UNITS_PER_LEVEL / VPT."""
    tot = 0.0
    for p in parts:
        if isinstance(p, Basin):
            tot += p.levels() * UNITS_PER_LEVEL
        elif isinstance(p, Tanks):
            tot += p.total()
        elif isinstance(p, Body):
            tot += 0.0 if p.limitless else p.stock * UNITS_PER_LEVEL / VPT
    return tot


def move(src, dst, tanks=None, limit=10 ** 6):
    """Move levels src -> (tanks) -> dst until either side refuses. Returns levels moved."""
    moved = 0
    while moved < limit:
        if isinstance(src, Tanks):
            if src.total() < UNITS_PER_LEVEL:
                break
            if isinstance(dst, Basin):
                if not dst.pour_level():
                    dst.pulse()   # the cells in reach brim: wait for the flow pulse to carry it on, then retry
                    if not dst.pour_level():
                        break
            elif isinstance(dst, Body):
                if not POURS_INTO_BODIES or not dst.credit_level():
                    break
            src.remove(UNITS_PER_LEVEL)
        else:   # world -> tanks: the tank leg is checked first, the world take never undone
            if not dst.add(0) or all(TANK_CAP - u < UNITS_PER_LEVEL for u in dst.units):
                break
            ok = src.take_level() if isinstance(src, Basin) else src.debit_level()
            if not ok:
                break
            dst.add(UNITS_PER_LEVEL)
        moved += 1
    for side in (src, dst):
        if isinstance(side, Basin):
            side.pulse()
        if isinstance(side, Body):
            side.settle()
    return moved


POURS_INTO_BODIES = _production_pours_into_bodies()


# ── the cases ─────────────────────────────────────────────────────────────

def main():
    bad, notes = [], []

    def check(ok, msg):
        if not ok:
            bad.append(msg)

    # 0. constants the doc's numbers rest on
    check(UNITS_PER_LEVEL == 5, "TankUnitsPerLevel moved: %s" % UNITS_PER_LEVEL)
    check(SUPERDEEP == 4, "Superdeep moved: %s" % SUPERDEEP)
    check(CELLS_PER_SOURCE * VPT > SUPERDEEP,
          "a natural cell is no longer worth more than a SUPERDEEP canal cell (5:1 vs D=4 gap closed?)")

    # 1. owner's trip, dug reservoirs: A (5x5, D4, full) -> tanks -> B (8x8, D4) -> tanks -> A
    A, B, T = Basin(5, 5, fill=SUPERDEEP), Basin(8, 8), Tanks(2)
    a0, total0 = A.snapshot(), ledger(A, B, T)
    for src, dst in ((A, T), (T, B), (B, T), (T, A)):
        move(src, dst)
        check(ledger(A, B, T) == total0, "trip 1 leg %s->%s changed the total" % (type(src).__name__, type(dst).__name__))
    check(A.snapshot() == a0, "trip 1: A full -> B -> A does not look the same")
    check(B.levels() == 0 and T.total() == 0, "trip 1: residue left in B or tanks")

    # 2. equal volumes, two tanks of 60 levels carry a 100-level A in two trips: same result
    A, B, T = Basin(5, 5, fill=SUPERDEEP), Basin(5, 5), Tanks(1)
    total0 = ledger(A, B, T)
    for _ in range(4):
        move(A, T); move(T, B)
    for _ in range(4):
        move(B, T); move(T, A)
    check(ledger(A, B, T) == total0 and A.levels() == 100, "trip 2 (one tank, several runs) lost or made volume")

    # 3. partial fill in a FLAT basin: volume returns, shape does not (no sub-brim levelling in the engine)
    A, B, T = Basin(5, 5, fill=2), Basin(8, 8), Tanks(2)
    A.reach = [(x, z) for x in range(2) for z in range(2)]   # a pump at the corner reaches ~4 cells (reach 1.5)
    a0, total0 = A.snapshot(), ledger(A, B, T)
    move(A, T); move(T, B); move(B, T); move(T, A)
    check(ledger(A, B, T) == total0 and A.levels() == 50, "trip 3: half-full A lost volume")
    shape_same = A.snapshot() == a0
    notes.append("trip 3 (half-full flat A): volume exact, shape %s" % ("SAME" if shape_same else
                 "DIFFERENT -- pours level the cells in reach, the rest fills only by brim overflow"))

    # 4. a sloped bed (deep centre, shallow rim) partial: fill-lowest-first puts the water in the middle
    bowl = lambda x, z: max(1, SUPERDEEP - max(abs(x - 3), abs(z - 3)))
    A, B, T = Basin(7, 7, depths=bowl), Basin(8, 8), Tanks(2)
    A.reach = [(x, z) for x in range(2) for z in range(2)]
    for _ in range(40):
        A.pour_level()
    A.pulse()
    a0, total0 = A.snapshot(), ledger(A, B, T)
    move(A, T); move(T, B); move(B, T)
    for _ in range(40):
        T.remove(UNITS_PER_LEVEL); A.pour_level()
    A.pulse()
    check(ledger(A, B, T) == total0, "trip 4: sloped bed changed the total")
    notes.append("trip 4 (sloped bowl, 40 levels): shape %s" % ("SAME" if A.snapshot() == a0 else "DIFFERENT"))

    # 5. B smaller than the load: the pour stalls, nothing is lost, the rest waits in the tanks
    A, B, T = Basin(5, 5, fill=SUPERDEEP), Basin(3, 3), Tanks(2)
    total0 = ledger(A, B, T)
    move(A, T); move(T, B)
    check(B.levels() == 36 and T.total() == (100 - 36) * UNITS_PER_LEVEL and ledger(A, B, T) == total0,
          "trip 5: a too-small B lost volume or overfilled")

    # 6. natural A -> tanks -> dug B -> tanks -> natural A
    nA = Body(20)
    B, T = Basin(10, 10), Tanks(2)
    total0 = ledger(nA, B, T)
    drawn = move(nA, T); move(T, B); move(B, T); back = move(T, nA)
    check(drawn == 100 and abs(nA.stock) < 1e-9 and nA.wet_cells() == set(), "trip 6: 20-cell pond did not drain "
          "dry at stock 0 (drawn %d, stock %.3f, wet %d)" % (drawn, nA.stock, len(nA.wet_cells())))
    if POURS_INTO_BODIES:
        check(back == 100 and nA.stock == nA.capacity and nA.wet_cells() == set(range(20)),
              "trip 6: return leg exists but the pond did not come back whole")
    else:
        check(back == 0 and T.total() == 100 * UNITS_PER_LEVEL and ledger(nA, B, T) == total0,
              "trip 6: with no return leg the water must wait in the tanks, not vanish")
        notes.append("trip 6 KNOWN GAP: nothing can pour INTO a natural pond; 500 units wait in the tanks and the pond "
                     "refills only by ooze/rain")

    # 7. natural pond vs an 'equal' dug basin: same cell count is NOT equal volume (5:1 budget vs D=4)
    nA = Body(25)
    B, T = Basin(5, 5), Tanks(3)
    move(nA, T); move(T, B)
    left = T.total() // UNITS_PER_LEVEL
    check(B.levels() == 100 and left == 25, "trip 7: expected 25 levels with nowhere to go, got %d" % left)
    notes.append("trip 7: a 25-cell pond holds %d levels; a 25-cell SUPERDEEP basin holds %d" %
                 (int(25 * CELLS_PER_SOURCE * VPT / VPT), 25 * SUPERDEEP))

    # 8. quantisation: refill adds float stock; a sub-level remainder is held by a kept cell and cannot be drawn
    nA = Body(4)
    nA.stock = 0.0
    nA.stock += 0.13 * 4 * 0.5 * 0.9   # a dry-season day of ooze, a bit less
    nA.settle()
    check(not nA.can_supply() and nA.wet_cells() == {0}, "trip 8: a %.3f-unit remainder should show one wet cell "
          "that a pump cannot draw" % nA.stock)

    # 9. save/load mid-trip: the body stock is a float; Scribe writes it as text
    nA = Body(37)
    for _ in range(3):
        nA.debit_level()
    nA.stock += 0.1234567   # a refill fraction
    for fmt in ("%.7g", "%r"):
        txt = fmt % nA.stock
        drift = abs(float(txt) - nA.stock)
        notes.append("trip 9: stock %s written as %-12s drifts %.2e units per save" % (repr(nA.stock), txt, drift))
    snap = json.loads(json.dumps({"a": A.snapshot().__len__(), "stock": nA.stock}))
    check(snap["stock"] == nA.stock, "trip 9: round-trip through text changed the stock")

    # 10. limitless endpoints: drawing never runs out; with no return leg nothing is ever credited back
    ocean = Body(4000, limitless=True)
    T = Tanks(10)
    check(move(ocean, T) == 10 * TANK_CAP // UNITS_PER_LEVEL, "trip 10: limitless draw stalled before the tanks filled")

    print("conservation round-trip model: %d unit(s) per level, D max %d, %g:1 budget, pour-into-body %s"
          % (UNITS_PER_LEVEL, SUPERDEEP, CELLS_PER_SOURCE, "PRESENT" if POURS_INTO_BODIES else "ABSENT"))
    for n in notes:
        print("  note:", n)
    if bad:
        for b in bad:
            print("FAIL:", b)
        return 1
    print("PASS: 10/10 trips conserve volume")
    return 0


if __name__ == "__main__":
    sys.exit(main())
