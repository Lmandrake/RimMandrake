#!/usr/bin/env python3
"""Offline selftest for validation.walk_bed_resume_verdict (sc_walk's part walk_master_bed_fire_resumes, visit 8).

Until visit 8 the part read whatever furnace-beast happened to sleep on grass over the walk's on-day: none did in visit 5
(two walks on his full list), so the part was UNMEASURED by design and sc_walk could never be counted. The part now lays a
beast down on ember grass: master off (no light over the control span), then on (the sleep roll lights it). Scripted here:
every verdict, the two planted states (the master left off over the on-phase; left on over the off-phase), and that no
short or unslept span gives a verdict. Run: python3 <this file>   (PYRE_WALK_VALIDATION=<path> runs it on that copy)
"""
import importlib.util
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
UTILS = os.path.abspath(os.path.join(HERE, "..", "Utils"))
for p in (HERE, UTILS, os.path.join(UTILS, "modcheck")):
    if p not in sys.path:
        sys.path.insert(0, p)
_path = os.environ.get("PYRE_WALK_VALIDATION") or os.path.join(HERE, "validation.py")
_spec = importlib.util.spec_from_file_location("validation", _path)
V = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(V)

FN = getattr(V, "walk_bed_resume_verdict", None)
fails, n = 0, 0


def check(name, ok, got=None):
    global fails, n
    n += 1
    if not ok:
        fails += 1
        print("FAIL %s: %r" % (name, got))


def poll(awake="False", cell="10,10", grass="True", lit="-1", fire=0):
    return {"awake": awake, "cell": cell, "flammablePlant": grass, "litAfterTicks": lit, "fire": fire}


def run(off, on):
    if FN is None:
        return ("MISSING", "validation.walk_bed_resume_verdict is absent", {})
    return FN(off, on)


step, grace = V.SLEEP_POLL_TICKS, V.SLEEP_GRACE_TICKS
NEED_OFF = (grace + V.SLEEP_CONTROL_ROLL_TICKS) // step + 1    # polls of one unbroken sleep that fill the off span
NEED_ON = (grace + V.SLEEP_FAIL_ROLL_TICKS) // step + 1
OFF = [poll() for _ in range(NEED_OFF)]
LIT = [poll() for _ in range(10)] + [poll(lit="2500", fire=1)]

check("off unlit, on lit", run(OFF, LIT)[0] == "PASS", run(OFF, LIT))
check("on lit, fire read at the next poll", run(OFF, [poll() for _ in range(9)] + [poll(lit="2500"), poll(lit="2500", fire=2)])[0] == "PASS")
check("planted: master left off over the on-phase", run(OFF, [poll() for _ in range(NEED_ON)])[0] == "FAIL", run(OFF, [poll() for _ in range(NEED_ON)]))
check("planted: master left on over the off-phase (sleep roll)", run(LIT, LIT)[0] == "FAIL", run(LIT, LIT))
check("off: a fire on the sleeper's plot", run(OFF[:5] + [poll(fire=1)] + OFF, LIT)[0] == "FAIL")
check("on: lit and no fire two polls running", run(OFF, [poll(), poll(lit="2500"), poll(lit="2500")])[0] == "FAIL")
check("on: lit, fire not yet read", run(OFF, [poll(), poll(lit="2500")])[0] is None)
check("off span too short", run(OFF[:NEED_OFF - 2], LIT)[0] is None, run(OFF[:NEED_OFF - 2], LIT))
check("off: awake all along is no reading", run([poll(awake="True") for _ in range(NEED_OFF * 2)], LIT)[0] is None)
check("off: no grass under it is no reading", run([poll(grass="False") for _ in range(NEED_OFF * 2)], LIT)[0] is None)
check("off: never one cell for long", run([poll(cell="%d,10" % (i % 2)) for i in range(NEED_OFF * 2)], LIT)[0] is None)
check("on: span too short", run(OFF, [poll() for _ in range(NEED_ON - 2)])[0] is None)
check("on: awake all along is no reading", run(OFF, [poll(awake="True") for _ in range(NEED_ON * 2)])[0] is None)
check("no polls", run([], [])[0] is None)
check("a fire beside an awake beast in the off-phase still counts", run(OFF + [poll(awake="True", fire=1)], LIT)[0] == "FAIL")
gap = [poll(awake="True")]
check("two half sleeps: each pays its own grace", run(OFF[:NEED_OFF // 2] + gap + OFF[:NEED_OFF // 2], LIT)[0] is None)
# ---- walk_master_off_then_on: two spells (visit 8 tier rehearsal: one on-day read "no front" while the relight takes two days)
MV = getattr(V, "master_spells_verdict", None)


def spell(fires, ash, beds=None):
    return {"fires": fires, "ash": ash, "beds": beds or [0] * len(fires)}


def mv(off, on):
    return (MV or (lambda a, b: ("MISSING", "")))(off, on)[0]


DECAY = [272.0, 250.0, 230.0, 212.0]
QUIET = spell([0, 0, 0], DECAY)
LITON = spell([0, 3, 9], [50.0, 46.0, 43.0, 48.0])
check("off quiet, on lit and dusting", mv(QUIET, LITON) is True, mv(QUIET, LITON))
check("planted left_on: fires in the off spell", mv(LITON, LITON) is False)
check("planted left_off: no fire in the on spell", mv(QUIET, QUIET) is False)
check("off: ash rose in one hour under a net fall", mv(spell([0, 0, 0], [272.0, 250.0, 251.0, 212.0]), LITON) is False)
check("off: a bed fire", mv(spell([0, 0, 0], DECAY, [0, 1, 0]), LITON) is False)
check("on: fire and no ash in any hour", mv(QUIET, spell([0, 3, 9], DECAY)) is False)
check("a missing ash read is undecided", mv(QUIET, spell([0, 3, 9], [50.0, None, 43.0, 48.0])) is None)
check("no reads are undecided", mv(spell([], [1.0]), LITON) is None)
check("the off spells outlast the standing burn's quiet window",
      getattr(V, "WALK_OFF_SPELL_TICKS", 0) > V.BURN_QUIET_TICKS and getattr(V, "R8_MASTER_HOURS", 0) * 2500 > V.BURN_QUIET_TICKS)
src = open(_path, encoding="utf-8").read()
check("the part stages its own sleeper", "def _walk_bed_fire_resumes" in src)
check("the part carries its planted switch", "PYRE_PLANT_BED_MASTER" in src)
print("selftest_pyrelands_walk_bed_resume: %d/%d" % (n - fails, n))
sys.exit(1 if fails else 0)
