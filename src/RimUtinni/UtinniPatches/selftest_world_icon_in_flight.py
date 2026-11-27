"""selftest_world_icon_in_flight.py -- the verdict of chain world_icon_in_flight (UTINNI_WORLDMAP_FLIGHT_ICON_1),
driven offline on hand-made jawa/world_objects_get replies: our textures PASS; vanilla's dome (the 2026-09-24
sighting) FAILS by name; every reply that cannot answer is UNMEASURED, never PASS and never FAIL. Also the walk of
the colonists onto the pad: each order_pawn call fits the bridge client's 30 s read limit (the 2026-11-27 ArchSmall
run timed out on one 5000-tick wait), and the walk counts who stands on the pad."""
import importlib.util
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
UTILS = os.path.abspath(os.path.join(HERE, "..", "..", "RimMandrake", "Utils"))
if UTILS not in sys.path:
    sys.path.insert(0, UTILS)
FAILS = []


def check(name, cond, detail=""):
    print("%s  %s %s" % ("ok  " if cond else "FAIL", name, "" if cond else detail))
    if not cond:
        FAILS.append(name)


def reply(*tex):
    return {"success": True, "count": len(tex),
            "objects": [{"row": {"def": "Gravship", "tile": 7}, "textures": x} for x in tex]}


class FakeWalk:
    """order_pawn as the live bridge answers it: a call that may wait 30 s or more is cut by the client (RimBridgeError
    timeout, outcome UNKNOWN); a call that fits walks the pawns `step` cells per call toward the cell."""
    def __init__(self, start, step=6):
        self.pos, self.step, self.calls = dict(start), step, []

    def __call__(self, tool, **kw):
        self.calls.append((tool, kw))
        if tool != "jawa/order_pawn":
            return {}
        if int(kw.get("timeoutSeconds", 30)) >= 30:
            raise RuntimeError("RimBridgeError: timed out: deadline exceeded: bridge request after 30.0 s")
        rows = []
        for pid, (x, z) in self.pos.items():
            dx, dz = kw["x"] - x, kw["z"] - z
            x += max(-self.step, min(self.step, dx))
            z += max(-self.step, min(self.step, dz))
            self.pos[pid] = (x, z)
            rows.append({"pawnId": pid, "end": {"x": x, "z": z}, "arrived": (x, z) == (kw["x"], kw["z"])})
        return {"success": all(r["arrived"] for r in rows), "pawns": rows,
                "waitEnded": "arrived" if all(r["arrived"] for r in rows) else "timeout"}


def walk_checks(v):
    X, Z = 100, 100
    near = FakeWalk({"a": (95, 95), "b": (90, 112)})
    try:
        got = v.walk_onto_pad(near, X, Z)
    except Exception as e:  # the old one-call 180 s wait lands here
        got = ("raised", str(e)[:120])
    check("walk: every order_pawn call fits the 30 s client limit",
          all(int(kw.get("timeoutSeconds", 30)) < 30 for tool, kw in near.calls if tool == "jawa/order_pawn"),
          near.calls)
    check("walk: both colonists counted on the pad", got == 2, got)
    for name, start, want in (("a colonist who never gets there is not counted", {"a": (95, 95), "b": (400, 400)}, 1),
                              ("no colonist is 0 aboard", {}, 0)):
        fake = FakeWalk(start, step=2)
        try:
            got = v.walk_onto_pad(fake, X, Z)
        except Exception as e:
            got = ("raised", str(e)[:120])
        check("walk: " + name, got == want, got)
        check("walk: %s ends after a bounded number of orders" % name,
              len(fake.calls) <= v.WALK_ROUNDS, len(fake.calls))


def ring_checks(v):
    #   1 - 2 - 3 - 4      a chain of tiles with a branch: 2 also touches 5
    #       |
    #       5
    nbr = {1: [2], 2: [1, 3, 5], 3: [2, 4], 4: [3], 5: [2]}
    got = v.tile_rings(nbr, 1, 3)
    check("rings: by distance, no repeats", got == [[2], [3, 5], [4]], got)
    got = v.tile_rings(nbr, 9, 2)
    check("rings: an unknown origin gives empty rings", got == [[], []], got)


def main():
    spec = importlib.util.spec_from_file_location("up_v", os.path.join(HERE, "validation.py"))
    v = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(v)
    f = v.world_icon_findings
    ours = {"expandingIcon": "RUT_Utinni", "materialTexture": "RUT_UtinniCaravan"}
    vanilla = {"expandingIcon": "Gravship", "materialTexture": "Caravan"}
    for field in ("expandingIcon", "materialTexture"):
        check("ours passes: " + field, f(reply(ours), field)[0] == "PASS", f(reply(ours), field))
        got = f(reply(vanilla), field)
        check("vanilla fails by name: " + field, got[0] == "FAIL" and "vanilla" in got[1], got)
        mixed = f(reply(ours, vanilla), field)
        check("one vanilla ship of two fails: " + field, mixed[0] == "FAIL", mixed)
        for name, r in (("no reply", None), ("refusal", {"success": False, "message": "No world"}),
                        ("no ship", {"success": True, "count": 0, "objects": []}),
                        ("old companion, no textures", {"success": True, "count": 1,
                                                        "objects": [{"def": "Gravship", "tile": 7}]}),
                        ("read threw", reply(dict(ours, **{field: "ERROR: NullReferenceException: x"}))),
                        ("no texture", reply(dict(ours, **{field: "(none)"}))),
                        ("missing key", reply({}))):
            got = f(r, field)
            check("%s is UNMEASURED: %s" % (name, field), got[0] == "UNMEASURED", got)
    walk_checks(v)
    ring_checks(v)
    print("RESULT: %s" % ("PASS" if not FAILS else "FAIL %d" % len(FAILS)))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
