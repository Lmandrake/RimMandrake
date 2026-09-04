"""Structure printing: rooms, floors, walls and furniture, validated first.

WHAT WORKS AND WHY THIS EXISTS

`apply_architect_designator` is a real generation API, not a click wrapper:

  * it takes **width/height rectangles**, not single cells
  * **`dryRun: true`** validates placement WITHOUT mutating
  * `flood_fill_cells` with a `designatorId` is a **site finder** — every cell
    where a building legally fits, honouring footprint, anchor, walkability and
    pawn reachability

A 13x11 furnished room took 21 calls and about 40 seconds. Two workbenches in
that run failed because they were handed corners with no clearance — which is
exactly what `plan()` here is for. **Validate the whole layout before building
any of it**, so a bad plan costs nothing.

🔑 LAYING A FLOOR DESTROYS WHAT IS UNDER IT. Grass, bushes and plants inside a
floor rectangle are wiped. This is the only working destruction primitive; the
direct ones (`Clear area (rect)`) do nothing through the bridge. Floor first,
then build on clean ground.

DESIGNATOR IDS are stable strings of the form

    architect-designator:<category>:build-<name>

so `D("structure", "wall")` and `D("furniture", "diningchair")`. Category and
name come from `list_architect_categories` / `list_architect_designators`.
Nothing here hardcodes a modded def, so the same code prints a vanilla shack or
a Jawa workshop.
"""
import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)


def D(category, name):
    """Designator id for a buildable. Categories: structure, floors, furniture,
    production, power, security, temperature, recreation, ship, misc."""
    return "architect-designator:%s:build-%s" % (category, name)


WALL = D("structure", "wall")
DOOR = D("structure", "door")
AUTODOOR = D("structure", "autodoor")


class Blueprint(object):
    """A layout you can validate, review and then commit.

    The point is that `plan()` is free and `build()` is not. Collect every piece
    first, dry-run the lot, print what would fail, and only then place — instead
    of discovering a bad footprint halfway through a half-built room.
    """

    def __init__(self, session, label="structure"):
        self.s = session
        self.label = label
        self.pieces = []          # (designatorId, x, z, w, h, note)

    def add(self, designator, x, z, w=1, h=1, note=""):
        self.pieces.append((designator, x, z, w, h, note))
        return self

    # ------------------------------------------------------------- shapes
    def rect_walls(self, x, z, w, h, designator=WALL):
        """Four wall runs forming a closed shell."""
        self.add(designator, x,         z,         w, 1, "south wall")
        self.add(designator, x,         z + h - 1, w, 1, "north wall")
        self.add(designator, x,         z,         1, h, "west wall")
        self.add(designator, x + w - 1, z,         1, h, "east wall")
        return self

    def floor(self, x, z, w, h, kind="woodplankfloor"):
        """Interior floor. ALSO CLEARS VEGETATION — see module docstring."""
        return self.add(D("floors", kind), x, z, w, h, "floor")

    def room(self, x, z, w, h, floor="woodplankfloor", door_offset=None,
             wall=WALL, door=DOOR):
        """A closed room with a floor and one door on the south wall."""
        self.rect_walls(x, z, w, h, wall)
        self.floor(x + 1, z + 1, w - 2, h - 2, floor)
        off = (w // 2) if door_offset is None else door_offset
        self.add(door, x + off, z, 1, 1, "door")
        return self

    # ------------------------------------------------------------ execute
    def plan(self, verbose=True):
        """Dry-run every piece. Returns (ok, failures) and mutates nothing."""
        failures = []
        for did, x, z, w, h, note in self.pieces:
            try:
                r = self.s.call("rimworld/apply_architect_designator",
                                designatorId=did, x=x, z=z, width=w, height=h,
                                dryRun=True)
                if not r.get("success"):
                    failures.append((did, x, z, note, "rejected"))
            except Exception as e:
                failures.append((did, x, z, note, str(e)[:80]))
        if verbose:
            print("  plan %-18s %d pieces, %d would fail"
                  % (self.label, len(self.pieces), len(failures)))
            for did, x, z, note, why in failures[:8]:
                print("     FAIL %-34s (%d,%d) %s  %s"
                      % (did.split(":")[-1], x, z, note, why))
        return (not failures), failures

    def build(self, skip_invalid=True, verbose=True):
        """Place everything. Dry-runs first and skips pieces that would fail."""
        ok, failures = self.plan(verbose=verbose)
        bad = {(d, x, z) for d, x, z, _n, _w in failures}
        placed = skipped = 0
        for did, x, z, w, h, note in self.pieces:
            if skip_invalid and (did, x, z) in bad:
                skipped += 1
                continue
            try:
                r = self.s.call("rimworld/apply_architect_designator",
                                designatorId=did, x=x, z=z, width=w, height=h,
                                keepSelected=True)
                # A piece that PASSED the dry-run above can still come back
                # success:false for real (a race with another placement, a
                # cell that changed between plan() and here) -- that must
                # count as skipped, not silently vanish from both totals.
                # placed + skipped must equal len(self.pieces) or the report
                # is exactly the kind of number that lies about the work done.
                if r.get("success"):
                    placed += 1
                else:
                    skipped += 1
            except Exception:
                skipped += 1
        if verbose:
            print("  built %-18s placed=%d skipped=%d" % (self.label, placed, skipped))
        return placed, skipped

    # --------------------------------------------------------------- site
    def find_site(self, near_x, near_z, w, h, designator=WALL,
                  require_reachable_pawn=None, max_cells=4000):
        """Ask the game where this footprint legally fits near a point.

        This is `flood_fill_cells` doing the work: it walks outward from a root
        cell and validates the whole footprint at each candidate, so siting
        respects walls, water, rock and reachability instead of guessing.
        """
        p = {"x": near_x, "z": near_z, "width": w, "height": h,
             "footprintAnchor": "top_left", "requireNotFogged": True,
             "requireNoImpassableThings": True,
             "maxCellsToProcess": max_cells, "maxReturnedCells": 24,
             "designatorId": designator}
        if require_reachable_pawn:
            p["reachablePawnId"] = require_reachable_pawn
        try:
            r = self.s.call("rimworld/flood_fill_cells", **p)
        except Exception as e:
            print("  find_site failed: %s" % str(e)[:120])
            return []
        return [(c.get("x"), c.get("z"))
                for c in (r.get("cells") or r.get("matches") or [])]


# ------------------------------------------------------------- furnishing
def furnish_bunkroom(bp, x, z, w, h):
    """A plausible player bunkroom: beds along the north wall, a table, lamps.

    Deliberately parameterised off the room rect rather than absolute cells, so
    it composes into larger buildings. Furniture is placed with clearance from
    the walls because benches and tables reject cramped footprints.
    """
    F = lambda n: D("furniture", n)
    beds = min(4, max(1, (w - 4) // 2))
    for i in range(beds):
        bp.add(F("bed"), x + 1 + i * 2, z + h - 2, 1, 1, "bed %d" % (i + 1))
    bp.add(F("endtable"), x + 1 + beds * 2, z + h - 2, 1, 1, "end table")
    cx, cz = x + w // 2, z + h // 2 - 1
    bp.add(F("table2x2c"), cx, cz, 1, 1, "dining table")
    for dx, dz in ((-1, 0), (2, 0), (0, -1), (1, 2)):
        bp.add(F("diningchair"), cx + dx, cz + dz, 1, 1, "chair")
    bp.add(F("standinglamp"), x + 2, cz, 1, 1, "lamp")
    bp.add(F("standinglamp"), x + w - 3, cz, 1, 1, "lamp")
    return bp


def furnish_workshop(bp, x, z, w, h, benches=("tablestonecutter", "fueledstove")):
    """Workbenches along the interior with clearance, plus light.

    Benches are multi-cell and reject cramped placements, which is precisely why
    Blueprint.plan() exists — run it and read the failures rather than trusting
    these offsets on an arbitrary room size.
    """
    for i, b in enumerate(benches):
        bp.add(D("production", b), x + 2 + i * 4, z + 2, 1, 1, b)
    bp.add(D("furniture", "standinglamp"), x + w // 2, z + h // 2, 1, 1, "lamp")
    return bp
