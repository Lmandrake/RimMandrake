#!/usr/bin/env python3
"""Class guard for RIMMASTER_RELEASE_POOL_FROZEN_ITEMS_HOLD_CLONES: on 2026-11-07 the owner asked why the clone pool was
full while little ran. The pipeline had been stopped (the owner's PAUSE, 2026-11-06 18:22): ten items that were running,
checking or in the game's active phases kept their clones, 16 of 16 places and 67 of 70 GB, because pool_rows ranks them
live by status and only release_parked/make_room give clones back, and neither touches a live row. A stop must park them.

Planted cases, both roads (park_stopped under PAUSE, and forced for a stop that left no tick):
  - not paused and not forced: nothing is parked (the gate);
  - paused: a dead running, stopping and checking item, a dead-checker clone and a game item in an active phase are parked;
  - never parked: a running item whose unit is up, a clone with a process in it, a closing item, an orphan, a quarantined run;
  - each parked work clone records its bundle on its item, a check clone records none;
  - through the real Effects and git: the commit and the dirty file leave in the bundle and come back whole."""
import inspect
import os
import shutil
import subprocess
import sys
import tarfile
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import relentless as R  # noqa: E402
import relentless_game as G  # noqa: E402

FAILS = []


def ok(cond, what):
    print(("ok   " if cond else "FAIL ") + what)
    if not cond:
        FAILS.append(what)


class Fx:
    """What pool_rows and park_stopped read. `up`: units running; `busy`: clones a process sits in; `pause`: the PAUSE."""
    def __init__(self, pool, up=(), busy=(), pause=True):
        self.pool, self.up, self.busy, self.pause, self.gone = dict(pool), set(up), set(busy), pause, []
    def paused(self): return self.pause
    def pool_clones(self): return [c for c in self.pool if c not in self.gone]
    def clone_present(self, c): return c in self.pool_clones()
    def clone_idle_s(self, c): return 10**6      # idle for days, as the frozen ones were: only the orphan row reads this
    def clone_busy(self, c): return c in self.busy
    def alive(self, run): return bool(run) and run.get("unit") in self.up
    def clone_wip(self, c): return dict(self.pool[c])
    def remove_clone(self, st, before=None):
        out = "/bundle/" + os.path.basename(st["clone"])
        if before:
            before(out)
        self.gone.append(st["clone"])
        return out


def put(s, item, status, clone, unit=None, phase=None, check_clone=None, check_unit=None, quarantine=False, charged=None):
    st = R.new_state(item, 0, "test")
    st.update(status=status, clone=clone)
    if unit:
        st["run"] = {"unit": unit, "at": 0, "charged": charged}
    if phase:
        st["game"] = {"phase": phase, "sha": "s", "clauses": ["A1"], "stages": 0, "entered_at": 0}
    if check_clone:
        st["check"] = {"clone": check_clone, "at": 0, "nonce": "n", "run": {"unit": check_unit, "at": 0, "charged": None} if check_unit else None}
    if quarantine:
        st["quarantined"].append({"run": {"unit": "u-q", "at": 0, "charged": None}, "at": 0, "clone": clone, "reaped": False})
    s.save(st)


WIP = {"kept": True, "carry_real": True, "real": ["a.cs"]}
CLEAN = {"kept": False, "real": []}


def fixture(s):
    """-> (pool, up, busy, parked, stays): every frozen shape that must go, and every shape that must stay."""
    pool, up, busy = {}, set(), set()
    def add(item, status, wip=WIP, **kw):
        c = "/c/" + item
        put(s, item, status, c, **kw)
        pool[c] = wip
        return c
    parked = [add("RUN_DEAD", "running", unit="u-dead"),
              add("STOP_DEAD", "stopping", unit="u-dead2"),
              add("CHK_WORK", "checking", wip=CLEAN, check_clone="/c/check-CHK_WORK-c1"),
              add("GAME_STAGING", G.GAME, phase="staging", unit="u-dead3"),
              add("GAME_PROVING", G.GAME, phase="proving")]
    pool["/c/check-CHK_WORK-c1"] = CLEAN
    parked.append("/c/check-CHK_WORK-c1")
    stays = [add("RUN_LIVE", "running", unit="u-live"),
             add("RUN_CHARGED_UP", "running", unit="u-live2", charged=5),   # charged, yet its unit is up: pool_rows reads it by status
             add("RUN_BUSY", "running"),
             add("CLOSING", "closing"),
             add("QUARANTINED", "held", unit=None, quarantine=True)]
    up.update(("u-live", "u-live2"))
    busy.add("/c/RUN_BUSY")
    pool["/c/ORPHAN_NOBODY"] = WIP                  # no item names it
    stays.append("/c/ORPHAN_NOBODY")
    put(s, "CHK_LIVE", "checking", "/c/CHK_LIVE", check_clone="/c/check-CHK_LIVE-c1", check_unit="u-check-live")
    pool["/c/CHK_LIVE"], pool["/c/check-CHK_LIVE-c1"] = CLEAN, CLEAN
    up.add("u-check-live")
    stays.append("/c/check-CHK_LIVE-c1")            # its checker is up: the clone stays (the work clone parks)
    parked.append("/c/CHK_LIVE")
    return pool, up, busy, parked, stays


def t_planted():
    r = R.rules()
    d = tempfile.mkdtemp(prefix="parkstop-")
    try:
        s = R.Store(d)
        pool, up, busy, parked, stays = fixture(s)
        fx = Fx(pool, up, busy, pause=False)
        acts = []
        ok(R.park_stopped(s, fx, r, 100.0, acts) == [] and not fx.gone, "no PAUSE and no force: nothing is parked, even the frozen")
        ok(R.pool_rows(s, fx, r) and all(x["rank"] != 1 for x in R.pool_rows(s, fx, R.rules()) if x["item"] in ("RUN_DEAD", "CHK_WORK")),
           "the frozen rows still read live without the stop (the cause this fixes)")
        fx.pause = True
        got = R.park_stopped(s, fx, r, 100.0, acts)
        names = sorted(os.path.basename(c) for c in fx.gone)
        ok(sorted(os.path.basename(c) for c in parked) == names,
           "under PAUSE every dead frozen clone goes back, the dead checker's too: %s" % names)
        ok(not set(fx.gone) & set(stays), "a live unit, a process in the clone, a closing item, a quarantine and an orphan stay: %s"
           % sorted(set(fx.gone) & set(stays)))
        ok(len(got) == len(parked) and all(len(x) == 3 for x in got), "the verb reports (item, clone, bundle) for each: %d" % len(got))
        ok(all(s.load(i).get("bundle") == "/bundle/" + i for i in ("RUN_DEAD", "STOP_DEAD", "GAME_PROVING")),
           "each frozen work clone's WIP is recorded on its item, so its next lease restores it")
        ok(s.load("CHK_WORK").get("bundle") is None and s.load("CHK_LIVE").get("bundle") is None,
           "a clean clone, and a checker's, record no bundle")
        ok(s.load("RUN_LIVE").get("bundle") is None and s.load("RUN_BUSY").get("bundle") is None, "a clone that stays records none")
        again = R.park_stopped(s, fx, r, 101.0, [])
        ok(again == [], "a second call finds nothing more to give back")
        # forced: a stop that left the timer off and PAUSE unset
        d2 = tempfile.mkdtemp(prefix="parkstop2-")
        try:
            s2 = R.Store(d2)
            pool2, up2, busy2, parked2, _ = fixture(s2)
            fx2 = Fx(pool2, up2, busy2, pause=False)
            R.park_stopped(s2, fx2, r, 100.0, [], force=True)
            ok(sorted(fx2.gone) == sorted(parked2), "force parks the same set with no PAUSE: %d" % len(fx2.gone))
        finally:
            shutil.rmtree(d2, ignore_errors=True)
        src = inspect.getsource(R._tick)
        ok("park_stopped(store, fx, r, now, acts)" in src, "the tick calls it, so a PAUSE parks them without anyone running a verb")
        ok("park-pool" in inspect.getsource(R.main), "and the verb park-pool is there for a stop with no tick")
    finally:
        shutil.rmtree(d, ignore_errors=True)


def t_real_git():
    """Through the real Effects, Store and git: a frozen item's commit and dirty file leave in its bundle and come back."""
    d = tempfile.mkdtemp(prefix="parkreal-")
    try:
        store = R.Store(d)
        r = dict(R.rules(), warm_clones=0)
        fx = R.Effects(r, store)
        def git(c, *a):
            return subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@t", *a], cwd=c, check=True,
                                  capture_output=True, text=True).stdout
        o = os.path.join(d, "o.git")
        os.makedirs(os.path.join(d, "clones"))
        git(d, "init", "-q", "--bare", o, "-b", "main")
        def clone(name):
            c = os.path.join(d, "clones", name)
            git(d, "clone", "-q", o, c)
            with open(os.path.join(c, name + ".txt"), "w", encoding="utf-8") as f:
                f.write("base\n")
            git(c, "add", name + ".txt")
            git(c, "commit", "-qm", "base")
            git(c, "push", "-q", "origin", "HEAD")
            return c
        c = clone("FROZEN_RUN")
        with open(os.path.join(c, "real.cs"), "w", encoding="utf-8") as f:
            f.write("real work\n")
        git(c, "add", "real.cs")
        git(c, "commit", "-qm", "real work")
        with open(os.path.join(c, "dirty.cs"), "w", encoding="utf-8") as f:
            f.write("not yet committed\n")
        st = R.new_state("FROZEN_RUN", 0, "t")
        st.update(clone=c, status="running")
        store.save(st)
        cc = clone("check-FROZEN_CHK-c1")
        wc = clone("FROZEN_CHK")
        st = R.new_state("FROZEN_CHK", 0, "t")
        st.update(clone=wc, status="checking", check={"clone": cc, "at": 0, "nonce": "n", "run": None})
        store.save(st)
        live = clone("LIVE_CLOSING")
        st = R.new_state("LIVE_CLOSING", 0, "t")
        st.update(clone=live, status="closing")
        store.save(st)
        acts = []
        got = R.park_stopped(store, fx, r, R.time.time(), acts, force=True)
        ok(sorted(x[1] for x in got) == ["FROZEN_CHK", "FROZEN_RUN", "check-FROZEN_CHK-c1"], "the frozen clones go: %s" % (got,))
        ok(fx.clone_present(live) and not fx.clone_present(c) and not fx.clone_present(wc) and not fx.clone_present(cc),
           "the closing item's clone stays; the frozen three are gone from the pool")
        b = store.load("FROZEN_RUN").get("bundle")
        ok(b and os.path.exists(os.path.join(b, "commits.bundle")) and os.path.exists(os.path.join(b, "carry")),
           "the commit is in the bundle the item points to: %s" % (b,))
        held = []
        for f in os.listdir(b):
            if f.endswith(".tar"):
                with tarfile.open(os.path.join(b, f)) as t:
                    held += t.getnames()
        ok(any(n.endswith("dirty.cs") for n in held), "and the dirty file: %s" % (held,))
        git(d, "clone", "-q", o, c)
        ok(fx.restore_bundle("FROZEN_RUN", b, c) == [], "the bundle restores into a fresh clone")
        ok(os.path.exists(os.path.join(c, "real.cs")) and os.path.exists(os.path.join(c, "dirty.cs")), "the commit's file and the dirty file are back")
        ok(git(c, "rev-list", "--count", "HEAD", "--not", "--remotes").strip() == "1", "the commit is back as one unlanded commit")
    finally:
        shutil.rmtree(d, ignore_errors=True)


def main():
    t_planted()
    t_real_git()
    print("%d failed" % len(FAILS))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
