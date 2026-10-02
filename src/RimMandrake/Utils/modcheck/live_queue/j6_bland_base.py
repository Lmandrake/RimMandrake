"""J6 NORTHSTAR_BLAND_BASE_SAVE_1: one-time creation of the saved bland world BLAND_NORTHSTAR_BASE.

Runs the J3 bland-tile recipe (colony_found -> map -> wildlife/ruins gone -> 3 colonists), then
induce_and_finish_naming (no naming dialog can ever re-raise), assert_bland, and save_base (backs up Saves, proves
a NEW file appeared and no existing save changed). After this, saved_base.world_reset() loads the save between suites.
Write-once: refuses (UNMEASURED) if the save already exists. NOT YET RUN LIVE.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import Unmeasurable, main   # noqa: E402
import j3_bland_tile                   # noqa: E402
import saved_base as BW               # noqa: E402
import helpers as H                    # noqa: E402

def fake_world():
    w = j3_bland_tile.fake_world()
    w.saves_dir = os.environ.get("LQ_SAVES_DIR")      # the selftest points both at one temp dir
    return w


def body(s, job):
    saves_dir = os.environ.get("LQ_SAVES_DIR") or BW.default_saves_dir()
    if (BW.SAVE_NAME + ".rws") in BW.snapshot_saves(saves_dir):
        raise Unmeasurable("%s.rws already exists; delete it deliberately to rebuild" % BW.SAVE_NAME)
    j3_bland_tile.body(s, job)
    np_ = BW.induce_and_finish_naming(s)
    job.check("colony named, no naming dialog open", not np_, np_)
    problems = H.assert_bland(s)
    job.check("assert_bland passes before saving", not problems, problems)
    if np_ or problems:
        return
    r = BW.save_base(s, saves_dir, wait=float(os.environ.get("LQ_SAVE_WAIT", "2.0")))
    job.note("save", r)
    job.check("a NEW %s.rws appeared and no existing save changed" % BW.SAVE_NAME, r["verified"], r["problems"])


if __name__ == "__main__":
    sys.exit(main("J6_bland_base", body, fake_builder=fake_world))
