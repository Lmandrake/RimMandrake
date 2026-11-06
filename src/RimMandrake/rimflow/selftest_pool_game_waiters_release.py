#!/usr/bin/env python3
"""Class guard for CLONEPOOL_FIX_GAME_WAITERS_HOG_THE_POOL: on 2026-11-03 staffing read "pool full" for 4.9 h (21% of the
day) while items waiting on the game phase kept their work clones (16/16): the holds were "commits" (a trailing commit
pinned the clone) and "live" (a dead worker unit still counted as running). An item waiting on the game holds no worker
place and no clone: whatever it holds (WIP, state-only commits, real commits, a dead uncharged run) goes back in a bundle
recorded on the item, and only the one item in an ACTIVE game phase (staging, proving) keeps its clone. Pins make_room
(the full-pool road) and release_parked (the every-tick road) on the same fixture."""
import os
import shutil
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import relentless as R  # noqa: E402
import relentless_game as G  # noqa: E402

FAILS = []
WAITING = ("implement", "prove", "stage", "final")      # game phases that wait: nothing of the item runs in its clone
WIPS = {"wip": {"kept": False, "real": ["a.cs"]},
        "state_commit": {"kept": False, "carry": True, "real": []},
        "real_commit": {"kept": True, "carry_real": True, "real": []},
        "dead_run": {"kept": False, "real": []}}


def ok(cond, what):
    print(("ok   " if cond else "FAIL ") + what)
    if not cond:
        FAILS.append(what)


class Fx:
    """What pool_rows, make_room and release_parked read. `cap`: the clone cap; `up`: units still running."""
    def __init__(self, pool, cap, up=()):
        self.pool, self.cap, self.up, self.gone = dict(pool), cap, set(up), []
    def pool_clones(self): return [c for c in self.pool if c not in self.gone]
    def clone_present(self, c): return c in self.pool_clones()
    def pool_load(self): return len(self.pool_clones()), 0, self.cap, 70 * 10**9
    def warm_count(self): return 0
    def clone_idle_s(self, c): return 5          # just put down: well inside pool_parked_release_s
    def clone_busy(self, c): return False
    def alive(self, run): return bool(run) and run.get("unit") in self.up
    def clone_wip(self, c): return dict(self.pool[c])
    def measure(self, run): return 0, "estimated"
    def remove_clone(self, st, before=None):
        out = "/bundle/" + st["clone"]
        if before:
            before(out)
        self.gone.append(st["clone"])
        return out


def put(s, item, status, clone, phase=None, unit=None):
    st = R.new_state(item, 0, "test")
    st.update(status=status, clone=clone)
    if phase:
        st["game"] = {"phase": phase, "sha": "s", "clauses": ["A1"], "stages": 0, "entered_at": 0}
    if unit:
        st["run"] = {"unit": unit, "at": 0, "charged": None}
    s.save(st)


def fixture(s):
    """Every waiting phase x every kind of holding, plus one active game item and one running builder. -> (pool, up)"""
    pool, up = {}, set()
    for ph in WAITING:
        for kind, wip in WIPS.items():
            item = "GW_%s_%s" % (ph.upper(), kind.upper())
            c = "/c/" + item
            put(s, item, G.GAME, c, ph, "u-dead-" + item if kind == "dead_run" else None)
            pool[c] = wip
    put(s, "GA_PROVING", G.GAME, "/c/GA_PROVING", "proving")
    pool["/c/GA_PROVING"] = {"kept": True, "carry_real": True, "real": ["b.cs"]}
    put(s, "RUN", "running", "/c/RUN", unit="u-run")
    pool["/c/RUN"] = {"kept": False, "real": ["c.cs"]}
    up.add("u-run")
    return pool, up


def main():
    ok(set(G.ACTIVE) == {"staging", "proving"} and not set(WAITING) & set(G.ACTIVE),
       "the active game phases are staging and proving, none of the waiting ones: %s" % (G.ACTIVE,))
    ok(G.GAME in R.PUT_DOWN, "an item waiting on the game is put down")
    r = R.rules()
    for road in ("make_room", "release_parked"):
        d = tempfile.mkdtemp(prefix="poolgame-")
        try:
            s = R.Store(d)
            pool, up = fixture(s)
            waiters = sorted(c for c in pool if "/GW_" in c)
            fx = Fx(pool, cap=len(pool), up=up)
            ranks = {os.path.basename(x["clone"]): x["rank"] for x in R.pool_rows(s, fx, r)}
            ok(all(ranks[os.path.basename(c)] == 1 for c in waiters),
               "%s: every game-waiting clone ranks parked, a dead uncharged run included: %s" % (road, ranks))
            ok(ranks["GA_PROVING"] == 2 and ranks["RUN"] == 2, "%s: the proving item and the running builder rank live" % road)
            acts = []
            if road == "make_room":
                hold = R.make_room(s, fx, r, 100.0, acts)
                ok(hold is None and len(fx.gone) == 1 and fx.gone[0] in waiters,
                   "make_room: a pool full of game waiters makes room by giving one back: hold=%s gone=%s" % (hold, fx.gone))
                while R.make_room(s, fx, r, 100.0, acts) is None and len(fx.gone) < len(waiters):
                    fx.cap -= 1     # ask again with less room until every waiter has had to go
                fx.cap = len(fx.pool_clones())      # full again with only the live two: nothing is left to give
                hold = R.make_room(s, fx, r, 100.0, acts)
                ok(hold is not None and "GA_PROVING (live)" in hold and "RUN (live)" in hold and "GW_" not in hold,
                   "make_room: only the proving item and the builder are left to name: %s" % hold)
            else:
                R.release_parked(s, fx, r, 100.0, acts)
            ok(sorted(fx.gone) == waiters, "%s: every game waiter's clone went back: %d of %d" % (road, len(fx.gone), len(waiters)))
            ok("/c/GA_PROVING" not in fx.gone and "/c/RUN" not in fx.gone,
               "%s: the proving item's clone and the builder's stay" % road)
            carried = [c for c in waiters if not c.endswith("_DEAD_RUN")]
            ok(all(s.load(os.path.basename(c)).get("bundle") == "/bundle/" + c for c in carried),
               "%s: each waiter's WIP or commits are recorded on its item, so its next clone restores them" % road)
            ok(all(s.load(os.path.basename(c)).get("bundle") is None for c in waiters if c.endswith("_DEAD_RUN")),
               "%s: a waiter with nothing to carry records no bundle" % road)
        finally:
            shutil.rmtree(d)
    print("%d failed" % len(FAILS))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
