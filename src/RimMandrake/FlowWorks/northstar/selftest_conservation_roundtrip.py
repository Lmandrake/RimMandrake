#!/usr/bin/env python3
"""POND_BED_DESIGN_LAKES_ARE_TALL_CANALS: the owner's conservation round trips, as an offline model.

Owner, 2026-10-11: "Start with A filled, then move it into tanks, then move it into empty reservoir B of a bigger
size. Then drain B back into the tanks and back into A... and A looks the same."

This is a MODEL of the shipped arithmetic, not the C#. Its constants are read from the production sources so a
change there fails here instead of drifting (RM_Volume's yardstick, RM_ExcavationDepth.Superdeep, the water FluidDef's
volumePerTile). The rules it mirrors, with their homes:

  dug basin       integer D (1..4) and F (0..D) per cell              RM_MapComponent_Excavation depthGrid/fillGrid
  pump draw       one level out of a cell (TryTakeLevel) -> +5 tank units        Building_LiquidPump.TryDraw
  pump draw body  TryDebit(volumePerTile) of float stock -> +5 tank units        Building_LiquidPump.TryDraw
  pump pour       -5 tank units -> +1 level into the EXCAVATED cell with most room Building_LiquidPump.TryPour, PickPour
  flow pulse      GRAVITY (recipient deeper than donor) or OVERFLOW (donor at brim) RM_FlowKernel.PickDonor
  body            capacity = sum(bed levels: shallow 2, deep 4) * volumePerTile; supported = floor(stock / mean perCell)
  tank            capacity = footprint squares * RM_Volume.UnitsPerSquare (x2 tall)  Building_LiquidTank.Capacity
  (POND_VOLUME_UNIFY_DEEP_NOTCH_YARDSTICK: one tank square = one deep canal square = one deep pond square)
  pour into body  whole levels into the pond's stock, up to capacity (POND_RETURN_LEG_BUILD_WATER_GOES_HOME:
                  Building_LiquidPump.PourToPond, RM_LiquidSpill.Outlet -> Body, Excavation.TryReturnLevels -> CreditLevels)

LIMITS (GPT review 2026-10-11 #3/#24/#25): the model draws from the fullest cell anywhere (production draws only in the
pump's reach), its flow order is a stand-in for the kernel's hop order, and outflows, hoses, rollback, displacement, rain
and spills are not modelled. It proves the ARITHMETIC of the legs conserves; it cannot prove production does.

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


VOLUME = _read("Source/RM_Volume.cs")
DEPTH = _read("Source/RM_ExcavationDepth.cs")
UNITS_PER_LEVEL = int(_const(VOLUME, "UnitsPerLevel"))
LEVELS_PER_SQUARE = int(_const(VOLUME, "LevelsPerSquare"))
SHALLOW_BED = int(_const(VOLUME, "ShallowBedLevels"))
UNITS_PER_SQUARE = LEVELS_PER_SQUARE * UNITS_PER_LEVEL
SUPERDEEP = int(_const(DEPTH, "Superdeep"))
_water = re.search(r"<defName>RM_Fluid_Water</defName>(.*?)</RimMandrake\.FlowWorks\.FluidDef>",
                   _read("Defs/Canals/FluidDefs/FlowWorks_Fluids.xml"), re.S).group(1)
VPT = float(re.search(r"<volumePerTile>([0-9.]+)</volumePerTile>", _water).group(1))
assert "<canalCellsPerSourceCell>" not in _water, "the 5:1 field is back in the water FluidDef"
# The trips' tank: a tall 3x3 (RM_Volume.TankCapacity(9, tall) at multiplier 1) = 360 units.
TANK_CAP = 9 * UNITS_PER_SQUARE * 2


def tank_capacity(area, tall=False, mult=1.0):
    """RM_Volume.TankCapacity: footprint squares x UnitsPerSquare x (2 if tall) x slider, never below one level."""
    return max(UNITS_PER_LEVEL, int(math.floor(area * UNITS_PER_SQUARE * (2 if tall else 1) * mult + 0.5)))


def migrated_stock(old_stock, old_cap, new_cap):
    """RM_Volume.MigratedStock: keep the fill fraction."""
    if old_cap <= 0 or new_cap <= 0:
        return max(new_cap, 0.0)
    return min(1.0, max(0.0, old_stock / old_cap)) * new_cap


def _production_pours_into_bodies():
    """True once a pump/outflow can put liquid INTO a natural body (the return leg of the owner's trip)."""
    pump = _read("Source/LiquidTypes/Building_LiquidPump.cs")
    spill = _read("Source/Machinery/RM_LiquidSpill.cs")
    strip = lambda t: re.sub(r"//[^\n]*", "", t)
    pour_body = re.search(r"private string TryPour\(\)(.*?)\n\t\t}\n", strip(pump), re.S)
    if not pour_body:
        raise SystemExit("cannot find the TryPour declaration -- the gap detector is blind, fix it")
    # POND_RETURN_LEG_BUILD_WATER_GOES_HOME: TryPour hands a pond in reach to PourToPond, whose leg is the Body outlet;
    # the outlet's Body leg calls TryReturnLevels, and that credits through CreditLevels. Every link must be present.
    ex = strip(_read("Source/RM_MapComponent_Excavation.cs"))
    ret = re.search(r"public bool TryReturnLevels\(.*?\n\t\t}\n", ex, re.S)
    credits = bool(ret and "stock.CreditLevels(" in ret.group(0))
    pond = re.search(r"private string PourToPond\(.*?\n\t\t}\n", strip(pump), re.S)
    via_pour = "PourToPond(" in pour_body.group(1) and bool(pond and "RM_OutletKind.Body" in pond.group(0))
    via_outlet = "ex.TryReturnLevels(" in strip(spill) and "return RM_OutletKind.Body;" in strip(spill)
    return credits and (via_pour or via_outlet)


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
    """A natural RM_LiquidBody: float stock, per-square beds (deep 4, shallow 2), floor recession, LIFO restore."""

    def __init__(self, n_cells, limitless=False, keep_last=True, beds=None):
        self.n = n_cells
        self.limitless = limitless
        self.keep_last = keep_last
        self.beds = list(beds) if beds is not None else [LEVELS_PER_SQUARE] * n_cells
        self.capacity = sum(self.beds) * VPT
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
    def __init__(self, count, cap=None):
        self.cap = TANK_CAP if cap is None else cap
        self.units = [0] * count

    def total(self):
        return sum(self.units)

    def add(self, k):
        for i, u in enumerate(self.units):
            if self.cap - u >= k:
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
            if not any(u >= UNITS_PER_LEVEL for u in src.units):
                break   # production's Store leg needs one tank that can provide a whole level
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
            if not dst.add(0) or all(dst.cap - u < UNITS_PER_LEVEL for u in dst.units):
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
    check(UNITS_PER_LEVEL == 5, "RM_Volume.UnitsPerLevel moved: %s" % UNITS_PER_LEVEL)
    check(SUPERDEEP == 4, "Superdeep moved: %s" % SUPERDEEP)
    check(LEVELS_PER_SQUARE == SUPERDEEP == 4 and UNITS_PER_SQUARE == 20,
          "one deep notch is no longer 4 levels = the deepest dug square = 20 units")

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
    poured = 0
    while poured < 40:
        if not A.pour_level():
            A.pulse()
            if not A.pour_level():
                break
        poured += 1
    A.pulse()
    check(poured == 40 and A.levels() == 40, "trip 4: set-up poured %d of 40" % poured)
    a0, total0 = A.snapshot(), ledger(A, B, T)
    move(A, T); move(T, B); move(B, T)
    move(T, A)
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
    drawn = move(nA, T)
    check(drawn == 80 and abs(nA.stock) < 1e-9 and nA.wet_cells() == set(), "trip 6: 20-cell pond did not drain "
          "dry at stock 0 (drawn %d, stock %.3f, wet %d)" % (drawn, nA.stock, len(nA.wet_cells())))
    move(T, B); move(B, T); back = move(T, nA)
    if POURS_INTO_BODIES:
        check(back == 80 and nA.stock == nA.capacity and nA.wet_cells() == set(range(20)),
              "trip 6: return leg exists but the pond did not come back whole")
    else:
        check(back == 0 and T.total() == 80 * UNITS_PER_LEVEL and ledger(nA, B, T) == total0,
              "trip 6: with no return leg the water must wait in the tanks, not vanish")
        notes.append("trip 6 KNOWN GAP: nothing can pour INTO a natural pond; 400 units wait in the tanks and the pond "
                     "refills only by ooze/rain")

    # 7. natural pond vs an equal dug basin: one deep pond square = one deep canal square (POND_VOLUME_UNIFY)
    nA = Body(25)
    B, T = Basin(5, 5), Tanks(3)
    move(nA, T); move(T, B)
    left = T.total() // UNITS_PER_LEVEL
    check(B.levels() == 100 and left == 0 and nA.stock == 0, "trip 7: 25 deep pond squares should fill a 25-square D4 pit "
          "exactly, got %d in B and %d left in the tanks" % (B.levels(), left))
    notes.append("trip 7: a 25-cell deep pond holds %d levels; a 25-cell SUPERDEEP basin holds %d -- exact" %
                 (int(nA.capacity / VPT), 25 * SUPERDEEP))

    # 8. quantisation: refill adds float stock; a sub-level remainder is held by a kept cell and cannot be drawn
    nA = Body(4)
    nA.stock = 0.0
    nA.stock += 0.13 * 4 * 0.5 * 0.9   # a dry-season day of ooze, a bit less
    nA.settle()
    check(not nA.can_supply() and nA.wet_cells() == {0}, "trip 8: a %.3f-unit remainder should show one wet cell "
          "that a pump cannot draw" % nA.stock)

    # 9. save/load mid-trip: the body stock is a float32; Scribe writes floats with G9 (GPT review #20, public decompile),
    #    which round-trips float32 exactly -- the 9-digit row is the shipped case, the real risk is float32 accrual
    nA = Body(37)
    for _ in range(3):
        nA.debit_level()
    nA.stock += 0.1234567   # a refill fraction
    for fmt in ("%.9g", "%r"):
        txt = fmt % nA.stock
        drift = abs(float(txt) - nA.stock)
        notes.append("trip 9: stock %s written as %-12s drifts %.2e units per save" % (repr(nA.stock), txt, drift))
    snap = json.loads(json.dumps({"a": A.snapshot().__len__(), "stock": nA.stock}))
    check(snap["stock"] == nA.stock, "trip 9: round-trip through text changed the stock")

    # 10. limitless endpoints: drawing never runs out; with no return leg nothing is ever credited back
    ocean = Body(4000, limitless=True)
    T = Tanks(10)
    check(move(ocean, T) == 10 * TANK_CAP // UNITS_PER_LEVEL, "trip 10: limitless draw stalled before the tanks filled")

    # 11. square equals square: N deep canal squares into tanks of N squares fill them exactly, and back
    for (w, h) in ((1, 1), (1, 2), (2, 2), (3, 3)):
        A, T = Basin(w, h, fill=SUPERDEEP), Tanks(1, cap=tank_capacity(w * h))
        a0 = A.snapshot()
        out = move(A, T)
        check(out == w * h * SUPERDEEP and T.total() == T.cap and A.levels() == 0,
              "trip 11: a %dx%d deep canal did not fill a %dx%d tank exactly (%d levels, tank %d/%d)"
              % (w, h, w, h, out, T.total(), T.cap))
        move(T, A)
        check(A.snapshot() == a0 and T.total() == 0, "trip 11: the %dx%d tank did not fill the canal back exactly" % (w, h))
        Tt = Tanks(1, cap=tank_capacity(w * h, tall=True))
        A2 = Basin(w, h * 2, fill=SUPERDEEP)
        check(move(A2, Tt) == 2 * w * h * SUPERDEEP and Tt.total() == Tt.cap and A2.levels() == 0,
              "trip 11: a tall %dx%d tank is not exactly twice its footprint of canal" % (w, h))

    # 12. mixed pond: 10 shallow + 10 deep squares hold 60 levels; drained and (with a return leg) refilled LIFO
    nA = Body(20, beds=[SHALLOW_BED] * 10 + [LEVELS_PER_SQUARE] * 10)
    check(nA.capacity == 60 * VPT, "trip 12: a 10 shallow + 10 deep pond holds %g, want 60" % nA.capacity)
    T = Tanks(1)
    w0, total0 = nA.wet_cells(), ledger(nA, T)
    trail = []
    while nA.debit_level():
        T.add(UNITS_PER_LEVEL)
        nA.settle()
        trail.append(frozenset(nA.wet_cells()))
    check(T.total() == 60 * UNITS_PER_LEVEL and ledger(nA, T) == total0, "trip 12: draining the mixed pond lost volume")
    if POURS_INTO_BODIES:
        back = move(T, nA)
        check(back == 60 and nA.wet_cells() == w0 and ledger(nA, T) == total0,
              "trip 12: the mixed pond did not come back to the same wet set")
    else:
        # the LIFO restore alone (stock credited by hand as the return leg will): same wet set at every level
        for k in range(60):
            nA.stock += VPT
            nA.settle()
            if k < 59:
                check(frozenset(nA.wet_cells()) == trail[58 - k], "trip 12: refill at level %d is not the drain reversed" % (k + 1))
        check(nA.wet_cells() == w0, "trip 12: refilled mixed pond is not its first shape")

    # 13. migration from volume model 1: pond keeps its fraction, an overfull old tank keeps every unit
    old_cap = 25 * 5.0            # model 1: 5 levels a square
    new_cap = Body(25).capacity   # model 2: 4
    s13 = migrated_stock(50.0, old_cap, new_cap)
    check(abs(s13 / new_cap - 50.0 / old_cap) < 1e-9, "trip 13: the pond's fill fraction changed in migration")
    T = Tanks(1, cap=tank_capacity(4))
    T.units[0] = 250              # an old 300-unit 2x2 tank holding 250, now 80
    check(not T.add(UNITS_PER_LEVEL) and T.total() == 250, "trip 13: an overfull tank took input or lost units")
    drained = 0
    while T.remove(UNITS_PER_LEVEL):
        drained += UNITS_PER_LEVEL
    check(drained == 250 and T.total() == 0, "trip 13: an overfull tank did not drain every stored unit")

    print("conservation round-trip model: %d unit(s) per level, D max %d, one square = %d levels = %d units, "
          "pour-into-body %s" % (UNITS_PER_LEVEL, SUPERDEEP, LEVELS_PER_SQUARE, UNITS_PER_SQUARE,
                                 "PRESENT" if POURS_INTO_BODIES else "ABSENT"))
    for n in notes:
        print("  note:", n)
    if bad:
        for b in bad:
            print("FAIL:", b)
        return 1
    print("PASS: 13/13 trips conserve volume")
    return 0


if __name__ == "__main__":
    sys.exit(main())
