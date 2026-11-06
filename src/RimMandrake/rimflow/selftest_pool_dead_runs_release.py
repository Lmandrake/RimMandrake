#!/usr/bin/env python3
"""Class guard for pool_full (OPS_JAM_CLASS_FIX_AGAIN_HJWN, 2026-11-06): the pool read "15 clones, cap 16, nothing to
release" while only five units ran. pool_rows took a run with `charged` None as live; a worker that finishes or snags
while its unit is still up moves its item to candidate or held, and those branches never settle the run, so its dead
unit stayed "live" for good (LEANINGSCRUB_CROWN_MOB_LIVE_1 held 20 h, BAROQUE_LIST_PAGE_REDRAW_UMBRA_AS_BIOME a candidate
stuck on publish_unknown 5 h). The class: an uncharged run pins its clone only while its unit is alive; a dead one's
clone ranks by its item's status, and the tick charges the dead run whatever status the item has moved on to."""
import os
import shutil
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import relentless as R  # noqa: E402

FAILS = []


def ok(cond, what):
    print(("ok   " if cond else "FAIL ") + what)
    if not cond:
        FAILS.append(what)


class Fx:
    """Just what pool_rows and make_room read. `up`: units still running."""
    def __init__(self, pool, up=()):
        self.pool, self.up, self.gone = list(pool), set(up), []
    def pool_clones(self): return [c for c in self.pool if c not in self.gone]
    def clone_present(self, c): return c in self.pool_clones()
    def pool_load(self): return len(self.pool_clones()), 0, 3, 40 * 10**9
    def warm_count(self): return 0
    def clone_idle_s(self, c): return 10**6
    def clone_busy(self, c): return False
    def alive(self, run): return bool(run) and run.get("unit") in self.up
    def clone_wip(self, c): return {"kept": False, "real": False}
    def measure(self, run): return 0, "estimated"
    def remove_clone(self, st, before=None):
        self.gone.append(st["clone"])
        return None


def put(s, item, status, unit, clone):
    st = R.new_state(item, 0, "test")
    st.update(status=status, clone=clone, run={"unit": unit, "at": 0, "charged": None})
    if status == "held":
        st["hold"] = {"why": "test", "kind": "seat"}
    s.save(st)


def main():
    d = tempfile.mkdtemp(prefix="pooldead-")
    try:
        s = R.Store(d)
        r = R.rules()
        pool = ["/c/CAND", "/c/HELD", "/c/RUN"]
        put(s, "CAND", "candidate", "u-cand", pool[0])
        put(s, "HELD", "held", "u-held", pool[1])
        put(s, "RUN", "running", "u-run", pool[2])
        fx = Fx(pool, up={"u-run"})
        rank = {os.path.basename(x["clone"]): x["rank"] for x in R.pool_rows(s, fx, r)}
        ok(rank.get("RUN") == 2, "an uncharged run whose unit is up stays live: %s" % rank)
        ok(rank.get("CAND") == 1, "a candidate whose finished unit is dead is parked, not live: %s" % rank)
        ok(rank.get("HELD") == 1, "a held item whose snagged unit is dead is parked, not live: %s" % rank)
        hold = R.make_room(s, fx, r, 100.0, [])
        ok(hold is None and fx.gone and "/c/RUN" not in fx.gone,
           "a full pool of dead uncharged runs makes room, and the running clone stays: hold=%s gone=%s" % (hold, fx.gone))
        fx2 = Fx(pool, up={"u-cand", "u-held", "u-run"})
        ok(R.make_room(s, fx2, r, 100.0, []) is not None and not fx2.gone, "live units are never evicted")
        if hasattr(R, "charge_dead_runs"):
            R.charge_dead_runs(s, fx, r, 100.0, [])
        ok(s.load("HELD")["run"]["charged"] is not None and s.load("CAND")["run"]["charged"] is not None,
           "the tick charges a dead run of a held or candidate item")
        ok(s.load("RUN")["run"]["charged"] is None, "and leaves a running unit's run alone")
    finally:
        shutil.rmtree(d)
    print("%d failed" % len(FAILS))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
