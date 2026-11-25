"""A compare plan (scene_compare.py): the fixture colony plays 1200 ticks with no act; the square and the job of each colonist and of
the donkey are recorded on every tick. Wandering, job choice and pathing draw random numbers, so any drift between arms shows here.
The fixture: make_fixture.py beside this file (thing ids survive a save and load). Item
RIMMANDRAKE_MEASURE_PLAY_AGAINST_PAUSED_STEP_NEVER_COMPARED."""
SAVE = "rm_fixture_play_vs_step"
LIMIT = 1200
# calm: a storyteller event opened a window that stopped the PLAY clock in the 2026-11-24 smoke run (cancelled at ticks 471 and 891)
CALM = "standard"
CAST = ("Human193", "Human196", "Human199", "Donkey12045")


def plan(c):
    return dict(until=LIMIT, record=[c.track(t, p) for t in CAST for p in ("Position", "CurJobDef")])
