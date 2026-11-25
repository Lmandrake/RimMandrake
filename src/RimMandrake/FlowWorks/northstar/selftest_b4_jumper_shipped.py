"""Offline selftest of live_session.py g_pit_access A3 (row B4_access_jump_pack_in_no_fall, scene sc_ways_out): the jumper
it stages is one the SHIPPED game has, so the case can ask on every game, ArchBig included.

The fault (FlowWorks visit 11, RIMMANDRAKE_RUN_FLOWWORKS_WAYS_OUT_WHERE_CHERRY_PICKER_KEEPS_JUMP_PACK): the case put an
Apparel_PackJump on its colonist. The ship cut list (infrastructure/state/cherrypicker/CherryPicker.SHIP.xml; ArchBig's live
Cherry Picker config is byte-identical to it, measured 2026-11-24) cuts Apparel_PackJump, Apparel_ArmorLocust and the
JumpPack research, and Cherry Picker's Pawn_ApparelTracker.Wear prefix refused the pack on 12 of 12 pawns. The row read
UNMEASURED twice on ArchBig, and a shipped game never has a jump pack at all.

It drives the SHIPPED g_pit_access (a real Session, not a copy) against a fake world. The fake world models ArchBig: a call
that stages a ship-cut def (a worn ThingDef, an added GeneDef, a cast AbilityDef, a HediffDef) is refused, as Cherry Picker
refuses it there. What must hold:
  1. the A3 jumper stages at least one thing, and nothing it stages is on the ship cut list;
  2. on the ArchBig-like world, with a mod that lands the jumper in the pit unhurt, the row reads PASS (the old staging read
     UNMEASURED here: the visit 11 symptom);
  3. planted mod faults read FAIL: a fall hediff after the landing, or a jumper that never reaches the pit floor;
  4. an unread step never reads PASS: the cast refused, the pawn read refused, a gene add refused -> UNMEASURED.
Range read: the six worlds above (refusal of each staging step, landing depth 0 or 6 notches, hediff present or absent). Left
out: the real jump timing and pathing, which only the live game shows (Stage 6, sc_ways_out).

  python3 src/RimMandrake/FlowWorks/northstar/selftest_b4_jumper_shipped.py
"""
import os
import re
import sys
import tempfile
import types

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
sys.path.insert(0, HERE)
import live_session as L  # noqa: E402

SHIP = os.path.join(ROOT, "infrastructure", "state", "cherrypicker", "CherryPicker.SHIP.xml")
ROW = "B4_access_jump_pack_in_no_fall"
FAILS = []


def check(cond, what):
    print(("ok   " if cond else "FAIL ") + what)
    if not cond:
        FAILS.append(what)


with open(SHIP, encoding="utf-8") as fh:
    CUT = set(re.findall(r"<li>([A-Za-z]+Def/[^<]+)</li>", fh.read()))
check(len(CUT) > 1000 and "ThingDef/Apparel_PackJump" in CUT,
      "instrument: the ship cut list reads (%d keys) and cuts Apparel_PackJump" % len(CUT))

# what a staging call names, by tool: (DefType, parameter)
STAGED = {"jawa/pawn_gear": ("ThingDef", "def"), "jawa/pawn_genes": ("GeneDef", "gene"),
          "jawa/pawn_use_ability": ("AbilityDef", "ability"), "jawa/grant_ability": ("AbilityDef", "ability"),
          "jawa/pawn_hediff": ("HediffDef", "hediff"), "jawa/add_hediff": ("HediffDef", "hediff")}


def staged_key(tool, kw):
    t = STAGED.get(tool)
    if not t or not kw.get(t[1]) or kw.get("action") in ("list", "remove"):
        return None
    return "%s/%s" % (t[0], kw[t[1]])


class FakeWorld(object):
    """ArchBig, as far as A3 reads it. depth is in notches (2 per metre); the A3 pit is 6 notches deep."""

    def __init__(self, land_depth=6, hediffs=(), refuse=()):
        self.land_depth, self.hediffs, self.refuse = land_depth, list(hediffs), set(refuse)
        self.n, self.depth, self.calls, self.tick, self.jumped = 0, {}, [], 0, set()

    def call(self, tool, **kw):
        self.calls.append((tool, kw))
        key = staged_key(tool, kw)
        if key in CUT:
            return {"success": False, "error": "Cherry Picker removed %s (ship cut list)" % key}
        if tool in self.refuse or (tool, kw.get("action")) in self.refuse:
            return {"success": False, "error": "refused (planted)"}
        if tool == "jawa/flowworks_excavation_drive":
            return {"success": True, "depth": kw.get("deepenLevels")}
        if tool == "jawa/spawn_pawn":
            self.n += 1
            pid = "Human%d" % self.n
            self.depth[pid] = 0
            return {"success": True, "pawns": [{"id": pid}]}
        if tool == "jawa/order_pawn":
            return {"success": True, "pawns": [{"id": kw.get("pawnId"), "orderAccepted": True, "drafted": True}]}
        if tool == "jawa/pawn_force_incapacitate":
            return {"success": True, "downedAfter": True}
        if tool == "jawa/static_call" and kw.get("method") == "ProofClimb":
            pid = str(kw.get("args")).split(":", 1)[1]
            d = self.land_depth if pid in self.jumped else self.depth.get(pid, 0)
            return {"success": True, "result": "cell=1,1 depth=%s held=False trapped=False" % d}
        if tool == "jawa/pawn_use_verb":
            if kw.get("action") == "list":
                return {"success": True, "result": {"verbs": [{"id": "Verb_Jump_0", "label": "jump"}]}}
            self.jumped.add(kw.get("pawn"))
            return {"success": True}
        if tool == "jawa/pawn_use_ability":
            if kw.get("action") == "list":
                return {"success": True, "result": [{"ability": kw.get("ability") or "Longjump", "canCast": True}]}
            self.jumped.add(kw.get("pawn"))
            return {"success": True, "accepted": True}
        if tool == "jawa/pawn_get":
            return {"success": True, "pawns": [{"id": kw.get("pawn"),
                                                "hediffs": [{"def": h} for h in self.hediffs] if kw.get("pawn") in self.jumped else []}]}
        if tool == "jawa/list_things":
            return {"success": True, "things": []}
        if tool == "jawa/flowworks_engine_state":
            self.tick += 1
            return {"success": True, "ticksGame": self.tick}
        return {"success": True}


sys.modules["fw_walk_common"] = types.SimpleNamespace(place=lambda *_a, **_k: {"survived": True})


def run(world):
    s = L.Session(types.SimpleNamespace(mock=False, dry_run=False), tempfile.mkdtemp(prefix="st_b4_jumper_"))
    s.say = lambda *_a: None
    s.w = world
    for _ in L.g_pit_access(s):
        pass
    got = [r for r in s.rows if r["id"] == ROW]
    return (got[0]["status"] if got else None), s


def jumper_id(world):
    """The A3 jumper: the pawn that the scene made jump (or tried to)."""
    for tool, kw in world.calls:
        if tool in ("jawa/pawn_use_verb", "jawa/pawn_use_ability", "jawa/pawn_gear", "jawa/pawn_genes") \
                and kw.get("action") not in ("list",) and kw.get("pawn") and \
                (tool != "jawa/pawn_gear" or kw.get("def") != "RM_ClimbingGear"):
            return kw.get("pawn")
    return None


# 1. what the jumper stages
w = FakeWorld()
st, _s = run(w)
j = jumper_id(w)
keys = [staged_key(t, kw) for t, kw in w.calls if kw.get("pawn") == j and staged_key(t, kw)]
check(j is not None and keys, "the A3 jumper stages something (%s: %s)" % (j, keys))
cut = [k for k in keys if k in CUT]
check(not cut, "nothing the A3 jumper stages is on the ship cut list (cut: %s)" % cut)

# 2. ArchBig-like world, a mod that lands the jumper unhurt: PASS
check(st == "PASS", "ArchBig world, landed 3 m deep with no fall hediff: %s reads PASS (got %s)" % (ROW, st))

# 3. planted mod faults read FAIL
st, _s = run(FakeWorld(hediffs=("Bruise",)))
check(st == "FAIL", "planted: a Bruise after the landing reads FAIL (got %s)" % st)
st, _s = run(FakeWorld(land_depth=0))
check(st == "FAIL", "planted: a jumper that never reaches the pit floor reads FAIL (got %s)" % st)

# 4. an unread step never reads PASS
for refuse, what in ((("jawa/pawn_use_ability", "cast"), "the jump cast refused"),
                     (("jawa/pawn_get", None), "the pawn read refused"),
                     (("jawa/pawn_genes", "add"), "a gene add refused")):
    st, _s = run(FakeWorld(refuse={refuse}))
    check(st != "PASS", "unread: %s never reads PASS (got %s)" % (what, st))
st, _s = run(FakeWorld(refuse={("jawa/pawn_genes", "add")}))
check(st == "UNMEASURED", "unread: a gene add refused reads UNMEASURED (got %s)" % st)

print("cases read: 7 runs over 6 worlds; failing: %d" % len(FAILS))
if FAILS:
    print("FAIL selftest_b4_jumper_shipped: %d failed" % len(FAILS))
    sys.exit(1)
print("PASS selftest_b4_jumper_shipped")
