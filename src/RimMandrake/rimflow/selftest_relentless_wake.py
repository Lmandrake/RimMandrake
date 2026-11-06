#!/usr/bin/env python3
"""RELENTLESS_WIRE_WAKE_ON_STATE_CHANGE. A poke (publish, land, a detached job's end) wakes Relentless in seconds: an idle
tick unit is started at once, a running tick absorbs the trigger and serves it at its next boundary, bursts coalesce
into one start and one serve, and rate caps keep a trigger loop from hammering the live unit. Fire and serve never
write into the watched directory (no self-wake). The units keep rm-relentless.timer as the heartbeat.

    PYTHONDONTWRITEBYTECODE=1 python3 src/RimMandrake/rimflow/selftest_relentless_wake.py
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import relentless_wake as W  # noqa: E402

FAILS = []
UNITS = os.path.join(os.path.dirname(HERE), "Utils", "systemd")
CFG = dict(W.DEFAULTS, mode="live", fire_min_gap_s=10, fire_max_per_hour=5, serve_min_gap_s=20, serve_max_per_tick=3)


def ok(cond, what):
    print(("ok   " if cond else "FAIL ") + what)
    if not cond:
        FAILS.append(what)


class Clock:
    def __init__(self, t=1000.0):
        self.t = t

    def __call__(self):
        return self.t


def rig():
    root = tempfile.mkdtemp(prefix="rlwake-")
    os.makedirs(os.path.join(root, "store"))
    return root, os.path.join(root, "store")


def listing(sdir):
    d = os.path.join(sdir, W.WAKE_DIR)
    return sorted(os.listdir(d)) if os.path.isdir(d) else []


def t_poke():
    root, sdir = rig()
    p = W.poke("publish", "abc123", root=root, now=50.0)
    ok(p == os.path.join(sdir, "wake", "publish.json"), "poke: one file per source in the watched dir")
    W.poke("publish", "def456", root=root, now=60.0)
    ok(listing(sdir) == ["publish.json"], "poke: a second poke of the same source overwrites (the dir never grows)")
    ok(W.pokes(sdir)[0]["at"] == 60.0, "poke: the newest poke is what is read")
    ok(not os.listdir(os.path.join(sdir, W.TMP_DIR)), "poke: written beside and renamed in, no temp file left")
    ok(W.poke("x", root=os.path.join(root, "nowhere")) is None, "poke: no store on this host -> None, no raise")
    W.poke("../../evil name", root=root, now=61.0)
    ok("______evil_name.json" in listing(sdir), "poke: a source cannot leave the wake dir")
    shutil.rmtree(root)


def t_fire_coalesce():
    root, sdir = rig()
    starts = []
    clk = Clock()
    ok(W.fire(sdir, now=clk(), active=lambda: False, start=lambda: starts.append(1), cfg=CFG)["do"] == "idle",
       "fire: nothing unserved -> idle, no start")
    for i in range(5):                                  # a burst of landings
        W.poke("publish%d" % i, root=root, now=900.0 + i)
    got = [W.fire(sdir, now=clk() + k, active=lambda: False, start=lambda: starts.append(1) or None, cfg=CFG)
           for k in range(0, 9)]                        # the path unit fires repeatedly within 9 s
    ok(len(starts) == 1, "coalescing: a burst of 5 pokes and 9 fires inside fire_min_gap_s starts exactly one tick")
    ok(got[0]["do"] == "started" and got[0]["pokes"] == 5 and got[0]["lag_s"] == 100.0,
       "coalescing: the one start covers all 5 pokes and says the oldest's lag")
    ok(all(g["do"] == "capped" for g in got[1:]), "coalescing: the rest are capped by the start floor")
    before = listing(sdir)
    W.fire(sdir, now=clk() + 30, active=lambda: True, start=lambda: starts.append(1), cfg=CFG)
    ok(listing(sdir) == before, "fire never writes into the watched dir (no self-wake)")
    shutil.rmtree(root)


def t_fire_absorbed():
    root, sdir = rig()
    starts = []
    W.poke("publish", root=root, now=990.0)
    got = W.fire(sdir, now=1000.0, active=lambda: True, start=lambda: starts.append(1), cfg=CFG)
    ok(got["do"] == "absorbed" and not starts, "a tick already running absorbs the trigger: no second start")
    with W._state(sdir) as st:
        ok(not st["fires"], "an absorbed trigger spends no start from the rate cap")
    ok(W.fire(sdir, now=1001.0, active=lambda: True, start=lambda: starts.append(1), cfg=dict(CFG, mode="off"))["do"]
       == "off", "mode off: fire does nothing")
    shutil.rmtree(root)


def t_fire_rate_cap():
    """A tick that exits at once under a poke storm: starts are bounded by the floor and the hourly ceiling."""
    root, sdir = rig()
    starts = []
    t = 10000.0
    for k in range(400):                                # one poke and one fire a second for 400 s
        W.poke("storm", root=root, now=t + k)
        W.fire(sdir, now=t + k, active=lambda: False, start=lambda: starts.append(1) or None, cfg=CFG)
    ok(len(starts) == CFG["fire_max_per_hour"],
       "rate cap: 400 fires in 400 s start at most fire_max_per_hour (%d) ticks, got %d"
       % (CFG["fire_max_per_hour"], len(starts)))
    starts2 = []
    for k in range(0, 50, 1):
        W.fire(sdir, now=t + 3700 + k, active=lambda: False, start=lambda: starts2.append(1) or None, cfg=CFG)
    ok(len(starts2) == 5, "rate cap: after an hour the floor alone holds (one start per 10 s): got %d" % len(starts2))
    got = W.fire(sdir, now=t + 9000, active=lambda: False, start=lambda: "unit refused", cfg=CFG)
    ok(got == {"do": "error", "why": "unit refused"}, "fire: a refused start says why")
    shutil.rmtree(root)


def t_serve():
    root, sdir = rig()
    clk, calls, acts, ts = Clock(), [], [], {}

    def do():
        calls.append(clk())
        return ["DEP"]
    ok(not W.serve(sdir, 0, do, acts, ts, cfg=CFG, wall=clk), "serve: no poke -> nothing, no call")
    ok(not os.path.exists(os.path.join(sdir, W.STATE)) and not os.path.exists(os.path.join(sdir, "wake.lock")),
       "serve: the common no-poke case writes nothing to the store")
    W.poke("publish", root=root, now=950.0)
    W.poke("land", root=root, now=960.0)
    before = listing(sdir)
    ok(W.serve(sdir, 1000.0, do, acts, ts, cfg=CFG, wall=clk) and len(calls) == 1,
       "serve: two unserved pokes -> one do() (coalesced)")
    ok(acts[-1] == {"do": "wake_serve", "lag_s": 50.0, "sources": ["land", "publish"], "enrolled": ["DEP"]},
       "serve: the act names the lag from the oldest poke, the sources and what enrolled")
    ok(listing(sdir) == before, "serve never writes into the watched dir (no self-wake)")
    ok(not W.serve(sdir, 1001.0, do, acts, ts, cfg=CFG, wall=clk) and len(calls) == 1,
       "serve: nothing new -> no second do()")
    W.poke("publish", root=root, now=1005.0)
    clk.t += 5
    ok(not W.serve(sdir, 1005.0, do, acts, ts, cfg=CFG, wall=clk), "serve: inside serve_min_gap_s the poke waits")
    clk.t += 20
    ok(W.serve(sdir, 1025.0, do, acts, ts, cfg=CFG, wall=clk) and len(calls) == 2, "serve: after the gap it is served")
    for k in range(5):
        W.poke("publish", root=root, now=1030.0 + k * 30)
        clk.t += 30
        W.serve(sdir, 1030.0 + k * 30, do, acts, ts, cfg=CFG, wall=clk)
    ok(len(calls) == CFG["serve_max_per_tick"], "rate cap: at most serve_max_per_tick serves in one tick, got %d"
       % len(calls))
    ts2 = {}                                            # the next tick has its own count

    def late():                                         # a landing while the serve runs stays unserved
        W.poke("publish", root=root, now=9999.0)
        return []
    ok(W.serve(sdir, 2000.0, late, acts, ts2, cfg=CFG, wall=clk), "serve: next tick serves the waiting poke")
    with W._state(sdir) as st:
        ok(W.unserved(sdir, st["served_at"]), "serve: a poke landing during do() stays unserved for the next boundary")

    def boom():
        raise RuntimeError("books cannot fetch")
    clk.t += 100
    ok(W.serve(sdir, 2100.0, boom, acts, ts2, cfg=CFG, wall=clk) and "books cannot fetch" in acts[-1]["why"],
       "serve: a failed do() is said in the act, never raised into the tick")
    shutil.rmtree(root)


def t_mark():
    root, sdir = rig()
    W.mark_served_through(sdir, 500.0)
    ok(not os.path.exists(os.path.join(sdir, W.STATE)), "mark: no poke -> no write")
    W.poke("publish", root=root, now=400.0)
    W.poke("land", root=root, now=600.0)
    W.mark_served_through(sdir, 500.0)
    with W._state(sdir) as st:
        ok([p["source"] for p in W.unserved(sdir, st["served_at"])] == ["land"],
           "mark: the tick's own enrol serves pokes before its sync, not after")
    shutil.rmtree(root)


def t_tick_serves():
    """The tick absorbs a poke and enrols the dependent at its first boundary (the prelude), from a fresh sync."""
    import relentless as R
    import selftest_relentless as T
    x = T.Rig(n=0, share=1.0, max_workers=10)
    syncs = []

    def sync():
        syncs.append(1)
        if len(syncs) == 2:         # the wake's sync fetches the close: the dependent becomes offerable
            x.w.items["DEP"] = "proposed"
    x.w.sync = sync
    W.poke("publish", "close of BLOCKER", root=x.d, now=x.now)
    acts = x.tick()
    serve = [a for a in acts if a.get("do") == "wake_serve"]
    ok(len(serve) == 1 and serve[0].get("enrolled") == ["DEP"],
       "tick: a running tick serves the poke and enrols the dependent before its own enrol: %s" % serve)
    ok({"do": "enrol", "item": "DEP", "wake": True} in acts, "tick: the enrol is journalled as the wake's")
    ok(R.Store(x.d).load("DEP") is not None, "tick: the dependent is in the store")
    acts2 = x.tick()
    ok(not [a for a in acts2 if a.get("do") == "wake_serve"], "tick: a served poke is not served again")
    x.done()


def t_units():
    def read(n):
        with open(os.path.join(UNITS, n), encoding="utf-8") as f:
            return f.read()
    p, s, timer = read("rm-relentless-wake.path"), read("rm-relentless-wake.service"), read("rm-relentless.timer")
    ok("PathChanged=/home/mandrake/rm/relentless/store/wake\n" in p and "Unit=rm-relentless-wake.service" in p,
       "units: the path unit watches the store's wake dir and starts the wake service")
    ok("relentless_wake.py fire" in s and "Type=oneshot" in s, "units: the wake service runs fire")
    ok("OnUnitInactiveSec=" in timer, "units: the heartbeat timer is still there")
    ok(W.WAKE_DIR == "wake" and W.STATE not in ("wake",) and not W.STATE.startswith("wake/"),
       "units: fire/serve state lives outside the watched dir")


def t_config():
    with open(W.CONFIG, encoding="utf-8") as f:
        raw = json.load(f)
    for k in ("fire_min_gap_s", "fire_max_per_hour", "serve_min_gap_s", "serve_max_per_tick"):
        ok(k in raw and "_" + k in raw and "easured" in raw["_" + k], "config: %s carries a measured reason" % k)
    with open(os.path.join(HERE, "relentless_rules.json"), encoding="utf-8") as f:
        rules = json.load(f)
    kinds = {"ceiling", "throttle", "window", "backoff_owed", "wp11"}
    for name, row in sorted(raw.get("clock_keys", {}).items()):
        node = rules
        for part in name.split("."):
            node = node.get(part) if isinstance(node, dict) else None
        ok(isinstance(node, (int, float)) and row.get("kind") in kinds and len(row.get("why", "")) > 40,
           "clock key %s is a live rules number with a kind and a reason: %r" % (name, node))
    ok(len(raw.get("clock_keys", {})) >= 16, "every remaining clock key is listed (%d)" % len(raw.get("clock_keys", {})))


def t_cli_poke():
    root, sdir = rig()
    got = subprocess.run([sys.executable, os.path.join(HERE, "relentless_wake.py"), "poke", "land", "abc"],
                         capture_output=True, text=True, env=dict(os.environ, RELENTLESS_ROOT=root), timeout=60)
    ok(got.returncode == 0 and listing(sdir) == ["land.json"], "cli: poke writes the poke")
    shutil.rmtree(root)


def main():
    for t in (t_poke, t_fire_coalesce, t_fire_absorbed, t_fire_rate_cap, t_serve, t_mark, t_tick_serves, t_units,
              t_config, t_cli_poke):
        t()
    print("FAILED %d" % len(FAILS) if FAILS else "ALL PASS")
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
