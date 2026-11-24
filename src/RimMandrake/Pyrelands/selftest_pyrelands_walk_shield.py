#!/usr/bin/env python3
"""Offline selftest for the walk's shield (RIMMANDRAKE_SHIELD_PYRE_WALK_FROM_FULL_LIST_EVENTS), bar walk_season_on_the_pyre.

On his 315-mod list (Pyrelands visit 2, 2026-11-21) the two-week walk_season was stopped by a hostile that ARRIVED from
another mod ("arrived: Human VRESaurids_TownGuard_Saurid (humanlike)", quiet storyteller): 8 of 8 parts UNMEASURED. Inside
walk_season a foreign arrival is vanished (jawa/pawn_force_incapacitate action=vanish, read back) and the advance resumes;
the removal is noted. Everything else still stops: the biome's own cast arriving hostile, a hostile present at arm, an
animal that turned hostile, a critical or declared pawn, any harm to a colonist riding along, and a removal that could not
be read back. A fake bridge replays the measured stop.

Range declared: the trigger kinds and detail forms the companion writes for a hostile (JawaBenchVitalsCore.Diff: "present
at arm: ", "arrived: ", "turned hostile: "), the cast (ANIMAL_MANIFEST) against a foreign def, critical and declared flags,
a damage trigger riding along, a repair that cannot see or cannot remove. Left out: the arrival's source mod (no offline
read can name it; the live walk notes every removal), and several maps (the shield vanishes by id on whatever map lists it).
Run: python3 <this file>   (PYRE_WALK_VALIDATION=<path to another validation.py> runs it against that copy)
"""
import importlib.util
import inspect
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
UTILS = os.path.abspath(os.path.join(HERE, "..", "Utils"))
for p in (HERE, UTILS, os.path.join(UTILS, "modcheck")):
    if p not in sys.path:
        sys.path.insert(0, p)

import clockgate as CG  # noqa: E402

_path = os.environ.get("PYRE_WALK_VALIDATION") or os.path.join(HERE, "validation.py")
_spec = importlib.util.spec_from_file_location("validation", _path)
V = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(V)

RESULTS = []


def check(name, cond, detail=""):
    RESULTS.append(bool(cond))
    print("%s %s%s" % ("ok  " if cond else "FAIL", name, ("  -- %s" % detail) if detail and not cond else ""))


def trig(kind="hostile_arrival", detail="arrived: Human VRESaurids_TownGuard_Saurid (humanlike)", sid=77001, sev="threat",
         critical=False, declared=False):
    return {"kind": kind, "severity": sev, "subjectId": sid, "subject": "x", "critical": critical, "declared": declared,
            "detail": detail}


SAURID = trig()
HURT = trig("hurt", "health 1 -> 0.8; newest hediff Cut/Torso age 3", 76045, "damage")


class FakeSession(object):
    """safe_advance stops once on `stop` (with `triggers`), then finishes; list_pawns lists `alive` ids until vanished."""

    def __init__(self, stop, triggers, alive=("Human77001",), vanish_works=True, list_ok=True):
        self.stop, self.triggers, self.alive = stop, triggers, set(alive)
        self.vanish_works, self.list_ok, self.calls, self.n = vanish_works, list_ok, [], 0

    def call(self, tool, **p):
        self.calls.append((tool, p))
        if tool == "jawa/safe_advance" and not p.get("action"):
            self.n += 1
            if self.n == 1:
                return {"success": False, "state": "stopped", "requested": p["ticks"], "executed": 1140,
                        "stopBy": self.stop, "triggers": self.triggers}
            return {"success": True, "state": "done", "requested": p["ticks"], "executed": p["ticks"]}
        if tool == "jawa/safe_advance":
            return {"success": True, "ticksGame": 1}
        if tool == "jawa/list_pawns":
            if not self.list_ok:
                return {"success": False, "message": "bridge busy"}
            return {"success": True, "pawns": [{"id": i, "dead": False, "hostile": True} for i in sorted(self.alive)]
                    + [{"id": "Human76045", "dead": False, "hostile": False}]}
        if tool == "jawa/pawn_force_incapacitate":
            if self.vanish_works:
                self.alive.discard(p.get("pawn"))
            return {"success": True}
        return {"success": True}


class FakeT(object):
    def __init__(self, session):
        self.session, self.upstream_failed, self.notes = session, False, []

    def _record(self, label, data):
        self.notes.append((label, data))


# ---- 1. which triggers the shield takes (pure)
P = getattr(V, "walk_foreign_arrival", None)
check("validation.walk_foreign_arrival exists", callable(P))
if callable(P):
    cases = [
        ("a foreign humanlike that arrived (the measured Saurid)", SAURID, True),
        ("a foreign manhunter that arrived", trig(detail="arrived: Warg Warg (animal)"), True),
        ("a hostile present at arm (the scene's own state)", trig(detail="present at arm: Human Pirate (humanlike)"), False),
        ("an animal that turned hostile on the map", trig(detail="turned hostile: RM_Flamefang (ManhunterPermanent)"), False),
        ("the biome's own cast arriving hostile (race def)", trig(detail="arrived: RM_Flamefang RM_Flamefang (animal)"), False),
        ("the biome's own cast arriving hostile (kind def)", trig(detail="arrived: Ullai RM_Ullai (animal)"), False),
        ("a critical actor", trig(critical=True), False),
        ("a declared pawn", trig(declared=True), False),
        ("a hurt colonist", HURT, False),
        ("a colonist turned hostile", trig("colonist_hostile", "colonist turned hostile (Berserk)", 76045, "damage"), False),
        ("not a dict", None, False),
    ]
    for label, t, want in cases:
        got = P(t)
        check("shield %s %s" % ("takes" if want else "leaves", label), got is want, "got %r" % got)

# ---- 2. inside the shield: the arrival is vanished, read back, noted, and the chunk finishes
shield = getattr(V, "_walk_shield", None)
check("validation._walk_shield exists", callable(shield))
if callable(shield):
    s = FakeSession(SAURID, [SAURID, trig("departed", "left the spawned set", 5, "info")])
    t = FakeT(s)
    with shield(t):
        got = CG.advance_chunk(s, 2000)
    vanished = [p.get("pawn") for tool, p in s.calls if tool == "jawa/pawn_force_incapacitate"]
    check("a foreign arrival is vanished and the chunk finishes", got == 2000 and vanished == ["Human77001"] and not s.alive,
          "executed %r, vanished %r, alive %r" % (got, vanished, s.alive))
    check("the vanish asks for no death (action=vanish)",
          all(p.get("action") == "vanish" for tool, p in s.calls if tool == "jawa/pawn_force_incapacitate"))
    noted = [d for lab, d in t.notes if "walk shield" in str(lab)]
    check("the removal is noted on the run's evidence", noted and "Human77001" in str(noted), "notes %r" % t.notes)
    check("the shield is withdrawn when the walk ends", not CG.EXPECTED, "EXPECTED %r" % CG.EXPECTED)

    for label, kw in (("a colonist hurt riding along with the arrival", dict(stop=SAURID, triggers=[SAURID, HURT])),
                      ("a vanish that does not take", dict(stop=SAURID, triggers=[SAURID], vanish_works=False)),
                      ("a pawn listing that fails (could not look)", dict(stop=SAURID, triggers=[SAURID], list_ok=False)),
                      ("the biome's own cast arriving",
                       dict(stop=trig(detail="arrived: RM_Flamefang RM_Flamefang (animal)"),
                            triggers=[trig(detail="arrived: RM_Flamefang RM_Flamefang (animal)")])),
                      ("a hurt colonist alone", dict(stop=HURT, triggers=[HURT]))):
        s = FakeSession(**kw)
        try:
            with shield(FakeT(s)):
                CG.advance_chunk(s, 2000)
            check("can-fail: %s still stops the walk" % label, False, "the advance finished")
        except CG.GovernorStop:
            check("can-fail: %s still stops the walk" % label, s.n == 1, "safe_advance calls %d" % s.n)

    s = FakeSession(SAURID, [SAURID])
    try:
        CG.advance_chunk(s, 2000)
        check("can-fail: outside the shield the same arrival still stops", False)
    except CG.GovernorStop:
        check("can-fail: outside the shield the same arrival still stops", True)

# ---- 3. walk_season runs every one of its parts inside the shield
src = inspect.getsource(V.walk_season)
lines = src.splitlines()
w = [i for i, ln in enumerate(lines) if ln.strip() == "with _walk_shield(t):"]
check("walk_season opens the shield", bool(w), "no `with _walk_shield(t):` line")
if w:
    ind = len(lines[w[0]]) - len(lines[w[0]].lstrip())
    body = lines[w[0] + 1:]
    inside = all((len(ln) - len(ln.lstrip())) > ind for ln in body if ln.strip())
    check("every walk part (reload, second pass, the ten and r6 parts) is inside the shield",
          inside and any("_ten_walk_season(t)" in ln for ln in body) and any("_r6_walk_season(t)" in ln for ln in body)
          and any('"walk_reload_keeps_the_state"' in ln for ln in body))

# ---- 4. ordinary life on his full list (visit 5, 2026-11-22): harm to a pawn not the player's (wildlife, the cast,
# visitors), or a colonist's panic flight, resumes after list_pawns reads the subject; a colonist's harm, another mental
# state, an unlisted subject (a death) or a failed listing still stops the walk
NUNA = trig("downed", "downed (health 0.18)", 100601, "threat")
PANIC = trig("mental", "mental state PanicFleeFire", 100626, "info")
BERSERK = trig("mental", "mental state Berserk", 100626, "info")


class PawnsSession(object):
    def __init__(self, pawns, ok=True):
        self.pawns, self.ok = pawns, ok

    def call(self, tool, **p):
        if tool == "jawa/list_pawns":
            return {"success": True, "pawns": self.pawns} if self.ok else {"success": False}
        return {}


WILD = {"id": "RSW_Nuna100601", "faction": None, "isPlayer": False, "hasGenes": False}
VISITOR = {"id": "Human100601", "faction": "OutlanderCivil", "isPlayer": False, "hasGenes": True}
COLONIST = {"id": "Human100601", "faction": "PlayerColony", "isPlayer": True, "hasGenes": True}
JILL = {"id": "Human100626", "faction": "PlayerColony", "isPlayer": True, "hasGenes": True}


def ok_of(pawns, stop_trig, others=(), list_ok=True):
    return V._walk_wildlife_check(PawnsSession(pawns, list_ok), {"state": "stopped", "stopBy": stop_trig,
                                                                 "triggers": [stop_trig] + list(others)}).get("ok")


check("predicate takes a downed, non-critical subject", V.walk_wildlife_harm(NUNA))
check("predicate refuses a critical subject", not V.walk_wildlife_harm(trig("downed", "x", 1, critical=True)))
check("predicate refuses an arrival", not V.walk_wildlife_harm(SAURID))
check("a wild animal's downing reads ok", ok_of([WILD], NUNA) is True)
check("a visitor's downing reads ok", ok_of([VISITOR], NUNA) is True)
check("a wild downing beside a colonist's PanicFleeFire reads ok", ok_of([WILD, JILL], NUNA, [PANIC]) is True)
check("can-fail: a colonist's downing is not ok", ok_of([COLONIST], NUNA) is False)
WASP = {"id": "RM_FireWasp100617", "faction": None, "isPlayer": False, "hasGenes": False}
STARVE = trig("starving", "food category Starving", 100617, "info")
check("a visitor's downing with starving wild fire-wasps riding along reads ok", ok_of([VISITOR, WASP], NUNA, [STARVE]) is True)
check("can-fail: a starving colonist is not ok", ok_of([JILL], trig("starving", "food category Starving", 100626, "info")) is False)
check("can-fail: a colonist's Berserk beside a wild downing is not ok", ok_of([WILD, JILL], NUNA, [BERSERK]) is False)
check("can-fail: a subject list_pawns does not list (a dead pawn) is not ok", ok_of([], NUNA) is False)
check("can-fail: a failed listing is not ok", ok_of([WILD], NUNA, list_ok=False) is False)

# ---- 5. the burn line's shield (visit 8, 2026-11-23): a wild animal's harm resumes, any mental state or colonist harm stands
BH = getattr(V, "burn_wildlife_harm", None)
check("burn line: a wild animal's downing is taken", BH is not None and bool(BH(NUNA)))
check("burn line: can-fail: a mental state is never taken (a manhunter, a colonist's panic)",
      BH is not None and not BH(BERSERK) and not BH(PANIC))
check("burn line: can-fail: an arrival or a critical subject is not taken",
      BH is not None and not BH(SAURID) and not BH(trig("downed", "x", 1, critical=True)))
check("burn line: the days run inside the shield",
      "with _wildlife_shield(t):\n        _r6_burn_line(t)" in open(V.__file__, encoding="utf-8").read())

check("a wild animal's 'info' death riding with a wild downing reads ok",
      ok_of([WILD], NUNA, [trig("death", "died: Burn", 75687, "info")]) is True)
check("can-fail: a death above 'info' (a colonist's) is not ok", ok_of([WILD], NUNA, [trig("death", "died: Burn", 75687, "threat")]) is False)

for chain in ("fresh_burn_bonus", "embergrass_regrow"):
    check("burn line's shield: chain %s runs inside it" % chain,
          "@_wildlife_shielded\ndef %s(t):" % chain in open(V.__file__, encoding="utf-8").read())

# ---- 6. the hunger row runs unfed (visit 8, 2026-11-24): the harness's feeder turned an urgently hungry colonist full
class Fed(object):
    feed = True


class TF(Fed):
    watch = Fed()


tf = TF()
UNFED = getattr(V, "_unfed", None)
if UNFED:
    with UNFED(tf):
        inside = (tf.feed, tf.watch.feed)
check("unfed: the suite's and the watch's feeder are off inside and back on after",
      UNFED is not None and inside == (False, False) and (tf.feed, tf.watch.feed) == (True, True))
check("unfed: the hunger row runs inside it", 'with _unfed(t), _comp(t, "fire_sense_hungry_eats_first")' in open(V.__file__, encoding="utf-8").read())

n = sum(RESULTS)
print("\n%d/%d passed" % (n, len(RESULTS)))
sys.exit(0 if n == len(RESULTS) else 1)
