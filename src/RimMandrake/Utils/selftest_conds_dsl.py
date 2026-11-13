#!/usr/bin/env python3
"""selftest_conds_dsl.py - CONDSDSL_WIRE_PYTHON_BUILDERS (bridge_conditions build_spec §2 T4) against a fake bridge.

The fake companion runs the REAL T1 core (conds.Compiler / conds.Run) over a scripted world, so the runner is tested
against the semantics the C# twin shares, not against hand-written replies. It covers the T4 acceptance:
  A. the JSON shapes the builders make (and that the T1 core compiles them), and the wire names vs tool_schemas.json
  B. state -> verdict mapping
  C. a 540 s re-attach by runKey (the run outlives one call's timeoutMs; every call carries the same runKey)
  D. the benign-stop resume recording its mutation (site_recover -> mutations[]); a real stop still raises
  E. an edge baseline reset after a recovery (coverage.gaps[] names the edge; a level condition records no gap)
  F. B.watch: arm/read/clear, and a recovery inside B.ticks re-arms the watcher and records mutation and gap
  G. scenelib.until / watch / cond_eval ride the same engine with the scene's stopOn
Exit 0 green, 1 red. Offline; no game.
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
os.environ["RIMBRIDGE_GOVERNOR_LOG"] = ""   # GovernorStops raised here are fixtures: no governor_stops.jsonl row
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "modcheck"))
sys.path.insert(0, os.path.join(HERE, "scenes"))

import conds  # noqa: E402
import conds_dsl as D  # noqa: E402
from conds import cell, fw, pawn, game, ring, thing, map_, all_, any_, not_, edge, stays, changed, alarm  # noqa: E402
import validation_core as V  # noqa: E402
import clockgate as CG  # noqa: E402

FAILS = []


def check(cond, what):
    if not cond:
        FAILS.append(what)
    return cond


# ---------------------------------------------------------------------------------------------- the fake companion
class World(object):
    """Scripted game state: read(key, tick) -> (v, status); stops {tick: stopBy dict} latch once."""

    def __init__(self, tick=1000, reads=None, stops=None, per_call=None):
        self.tick = tick
        self.reads = reads or (lambda key, t: (t, "ok") if key == "game.tick" else (None, "error", "no " + key))
        self.stops = dict(stops or {})
        self.per_call = per_call         # ticks one call may run before it returns `running` (the timeoutMs)
        self.override = {}               # key -> (v, status): a mutation's effect, from its tick on

    def read(self, key):
        if key in self.override:
            return self.override[key]
        r = self.reads(key, self.tick)
        return r if len(r) == 3 else (r[0], r[1], "")


class Source(object):
    def __init__(self, world):
        self.w = world

    def current_map(self):
        return 0

    def map_size(self, map_id):
        return (250, 250) if map_id == 0 else None

    def refuse(self, key):
        return None

    def read(self, key):
        return self.w.read(key)


class FakeBridge(V._BridgeBase):
    def __init__(self, world):
        self.w = world
        self.calls = []
        self.runs = {}                   # runKey -> [Run, requested]
        self.watchers = {}               # owner -> {"run": Run, "names": [...]}
        self.ring = []                   # (owner, event) with a global seq

    def _raw(self, tool, kw):
        self.calls.append((tool, json.loads(json.dumps(kw))))
        if tool == "jawa/safe_advance":
            return self.safe_advance(kw)
        if tool == "jawa/cond_eval":
            return conds.cond_eval({"tree": kw["tree"]}, Source(self.w))
        if tool == "jawa/cond_watch":
            return self.cond_watch(kw)
        return {"success": False, "error": "fake has no " + tool}

    # one tick of game time: watchers see it, then the stop latch
    def _tick(self):
        self.w.tick += 1
        for owner, ws in self.watchers.items():
            before = len(ws["run"].events)
            ws["run"].step({"tick": self.w.tick})
            for ev in ws["run"].events[before:]:
                self.ring.append((owner, dict(ev, seq=len(self.ring))))
        return self.w.stops.pop(self.w.tick, None)

    def safe_advance(self, kw):
        if kw.get("action") == "status":
            return {"success": True, "ticksGame": self.w.tick}
        if kw.get("action") == "cancel":
            return {"success": True}
        if "until" not in kw:                            # plain governed advance (B.ticks / clockgate.advance_chunk)
            n, done = int(kw["ticks"]), 0
            while done < n:
                sb = self._tick()
                done += 1
                if sb:
                    return {"success": True, "state": "stopped", "executed": done, "requested": n,
                            "stopBy": dict(sb, tick=self.w.tick), "triggers": [dict(sb, tick=self.w.tick)]}
            return {"success": True, "state": "done", "executed": n, "requested": n}
        key = kw["runKey"]
        if key not in self.runs:
            spec = dict((k, v) for k, v in kw.items() if k in conds.RUN_KEYS)
            spec["max_ticks"] = kw["ticks"]
            try:
                c = conds.Compiler(Source(self.w), "run").compile_spec(spec)
            except conds.Refused as e:
                return conds.refusal(e)
            run = conds.Run(c, Source(self.w))
            run.arm({"tick": self.w.tick})
            self.runs[key] = [run, None]
        run, sb = self.runs[key]
        budget = self.w.per_call
        while run.state == "running" and (budget is None or budget > 0):
            stop = self._tick()
            frame = {"tick": self.w.tick}
            if stop:
                frame["stop"] = stop["kind"]
                sb = self.runs[key][1] = dict(stop, tick=self.w.tick)
            run.step(frame)
            if budget is not None:
                budget -= 1
        r = run.result()
        r["success"] = True
        if run.state == "stopped" and sb:
            r["stopBy"] = sb
            r["triggers"] = [t if t != sb["kind"] else sb for t in r["triggers"]]
        return r

    def cond_watch(self, kw):
        a, owner = kw["action"], kw["owner"]
        if a == "arm":
            spec = {"until": {"cmp": [{"p": "game.tick"}, "<", 0]}, "max_ticks": conds.HARD_MAX_TICKS,
                    "watch": kw["watch"]}
            try:
                c = conds.Compiler(Source(self.w), "run").compile_spec(spec)
            except conds.Refused as e:
                return conds.refusal(e)
            run = conds.Run(c, Source(self.w))
            run.arm({"tick": self.w.tick})
            self.watchers[owner] = {"run": run, "names": [w["name"] for w in kw["watch"]]}
            return {"success": True, "nextSeq": len(self.ring), "canonical": c.canonical}
        if a == "read":
            evs = [e for o, e in self.ring if o == owner and e["seq"] >= kw["since_seq"]]
            return {"success": True, "events": evs, "nextSeq": len(self.ring), "gap": None}
        if a == "clear":
            self.watchers.pop(owner, None)
            return {"success": True}
        return {"success": True, "owners": sorted(self.watchers)}


def sa_calls(B):
    return [kw for t, kw in B.calls if t == "jawa/safe_advance" and "until" in kw]


QUIET = lambda s: None  # noqa: E731


# ---------------------------------------------------------------------------------------------- A. shapes
def test_shapes():
    t = (fw(106, 103).water_m >= 0.5).tree
    check(t == {"cmp": [{"p": "fw.water_m", "cell": [106, 103]}, ">=", 0.5]}, "A1 fw water_m >= 0.5: %s" % t)
    t = ((fw(106, 103).water_m >= 0.5) & ~(pawn("Human123").downed == True)).tree  # noqa: E712
    want = {"all": [{"cmp": [{"p": "fw.water_m", "cell": [106, 103]}, ">=", 0.5]},
                    {"not": {"cmp": [{"p": "pawn.state", "pawn": "Human123", "f": "downed"}, "==", True]}}]}
    check(t == want, "A2 the §1.2 example tree: %s" % t)
    t = edge(cell(110, 90).is_water == False).tree  # noqa: E712
    check(t == {"edge": {"cmp": [{"p": "cell.is_water", "cell": [110, 90]}, "==", False]}, "dir": "rise"},
          "A3 edge: %s" % t)
    t = stays(not_(changed(fw(1, 2).water_m)), 600).tree
    check(t == {"stays": {"not": {"changed": {"p": "fw.water_m", "cell": [1, 2]}}}, "ticks": 600}, "A4 settled: %s" % t)
    t = (fw(105, 102, 3, 3).water_m.max() >= 0.5).tree
    check(t == {"cmp": [{"p": "fw.water_m", "rect": [105, 102, 3, 3], "reduce": "max"}, ">=", 0.5]}, "A5 rect max: %s" % t)
    t = ((game.tick >= 5) & (game.tick >= 6) & (game.tick >= 7)).tree
    check(len(t.get("all", [])) == 3, "A6 & flattens: %s" % t)
    t = D.to_tree(cell(3, 4).roofed)
    check(t == {"cmp": [{"p": "cell.roofed", "cell": [3, 4]}, "==", True]}, "A7 bool probe is == True: %s" % t)
    try:
        bool(game.tick >= 1)
        check(False, "A8 bool(Cond) must raise")
    except TypeError:
        pass
    specs = [
        game.hour.hour_in(22, 4), map_.sky_glow < 0.3, ring("damage_log").count >= 1,
        thing("Thing_42").field("comp.charge") > 0.5, game.tick.eq(10, tol=2), cell(5, 5).glow.in_(0.1, 0.4),
        cell(1, 1, 4, 4).is_water.count_where("==", True) >= 2, map_.count("Steel") >= 3,
        any_(pawn("P1").x >= 10, pawn("P1").job_def == "Goto"), (cell(2, 2).temp > 40).named("hot").optional(),
        cell(9, 9, map_id=0).fire, edge(fw(4, 4).water_m >= 0.5, dir="fall"),
    ]
    for i, c in enumerate(specs):
        try:
            D.precheck(D.run_spec(c, 100))
        except D.CondRefused as e:
            check(False, "A9.%d the T1 core refused builder output %s: %s" % (i, D.to_tree(c), e))
    try:
        D.precheck(D.run_spec(thing("T").field("Get()") == 1, 10))
        check(False, "A10 a method path must be refused offline")
    except D.CondRefused as e:
        check(e.refusal["refused"] == "field_method", "A10 refusal name: %s" % e.refusal)
    sp = D.run_spec(game.tick >= 1, 10, watch={"w": alarm(cell(1, 1).fire)})
    check(D.precheck(sp)["watch"][0]["name"] == "w", "A11 alarm watcher compiles")
    ids = D.stateful_ids(D.precheck(D.run_spec(edge(game.tick >= 1) & (game.tick >= 2), 10,
                                               watch={"w": edge(game.tick >= 3)})))
    check(ids == ["n1", "w/n4"], "A12 stateful ids come from the core's one counter: %s" % ids)
    miss = D.check_wire_names()
    check(not miss, "A13 wire names vs tool_schemas.json: %s" % miss)
    # the wire: ticks=max_ticks, cond params, runKey, timeoutMs capped
    B = FakeBridge(World())
    B.until(game.tick >= 1010, 50, timeout_ms=900000, progress=QUIET, run_key="k-shape")
    kw = sa_calls(B)[0]
    check(kw["ticks"] == 50 and "max_ticks" not in kw and kw["runKey"] == "k-shape" and kw["timeoutMs"] == 480000
          and kw["stopOn"] == "default" and kw["until"] == (game.tick >= 1010).tree,
          "A14 safe_advance args: %s" % kw)
    ev = B.cond_eval(fw(3, 3).water_m >= 0.5)
    check(ev.get("status") == "error" and B.calls[-1] == ("jawa/cond_eval", {"tree": (fw(3, 3).water_m >= 0.5).tree}),
          "A15 cond_eval: %s" % ev)


# ---------------------------------------------------------------------------------------------- B. verdicts
def test_verdicts():
    B = FakeBridge(World())
    r = B.until(game.tick >= 1010, 50, progress=QUIET)
    check(r.state == "hit" and r.hit_tick == 1010 and r.executed == 10, "B1 hit: %r" % r)
    check(r.verdict() == ("PASS", "hit at tick 1010"), "B1 verdict %s" % (r.verdict(),))
    check(r.verdict(expect_hit=False)[0] == "FAIL", "B2 hit when it must not happen = FAIL")
    r = B.until(game.tick >= 99999, 20, progress=QUIET)
    check(r.state == "done" and r.verdict()[0] == "FAIL" and r.verdict(on_done="UNMEASURED")[0] == "UNMEASURED"
          and r.verdict(expect_hit=False)[0] == "PASS", "B3 done mapping %r" % r)
    r = B.until(fw(3, 3).water_m >= 0.5, 20, progress=QUIET)
    v = r.verdict()
    check(r.state == "unknown" and v[0] == "UNMEASURED" and "error" in v[1], "B4 unknown -> UNMEASURED: %s" % (v,))
    r = B.until(game.tick >= 1000, 20, progress=QUIET)
    check(r.state == "hit" and r.executed == 0 and r.true_at_arm, "B5 true at arm: %r" % r)
    for st in ("budget", "epoch", "error", "cancelled"):
        check(D.CondResult({"state": st}).verdict()[0] == "UNMEASURED", "B6 %s -> UNMEASURED" % st)
    try:
        D.CondResult({"state": "done"}).verdict(on_done="PASS")
        check(False, "B7 on_done=PASS must be refused")
    except ValueError:
        pass
    # a companion refusal raises CondRefused (precheck off, so the fake companion refuses)
    try:
        B.until({"cmp": [{"p": "nope"}, "==", 1]}, 5, progress=QUIET, precheck_offline=False)
        check(False, "B8 refusal must raise")
    except D.CondRefused as e:
        check(e.refusal["refused"] == "unknown_probe", "B8 refusal name %s" % e.refusal)


# ---------------------------------------------------------------------------------------------- C. re-attach
def test_reattach():
    lines = []
    B = FakeBridge(World(per_call=400))                 # each call returns `running` after 400 ticks
    r = B.until(game.tick >= 2000, 5000, progress=lines.append, run_key="v2-P3-a1b2")
    calls = sa_calls(B)
    check(len(calls) == 3, "C1 three calls for 1000 ticks at 400 per call: %d" % len(calls))
    check(all(c["runKey"] == "v2-P3-a1b2" and c["ticks"] == 5000 and c["timeoutMs"] <= 480000 for c in calls),
          "C2 every re-attach carries the same runKey and the whole budget: %s" % calls)
    check(len(B.runs) == 1, "C3 one run on the companion: %s" % list(B.runs))
    check(r.state == "hit" and r.hit_tick == 2000 and r.executed == 1000, "C4 result over re-attach: %r" % r)
    check(len(lines) == 3 and "re-attaching" in lines[0] and "re-attaching" not in lines[2], "C5 progress %s" % lines)


class Forgetful(FakeBridge):
    """Drops every run after the first call: a load between re-attaches."""
    def safe_advance(self, kw):
        r = FakeBridge.safe_advance(self, kw)
        if "until" in kw:
            self.runs.clear()
        return r


def test_lost_run():
    B = Forgetful(World(per_call=100))
    r = B.until(game.tick >= 5000, 5000, progress=QUIET, run_key="lost-1")
    check(r.state == "error" and "lost on re-attach" in (r.raw.get("abortWhy") or ""), "C6 a lost run is an error: %r %s"
          % (r, r.raw.get("abortWhy")))
    check(r.verdict()[0] == "UNMEASURED", "C7 a lost run is UNMEASURED")
    try:
        B.until(game.tick >= 1, 10, progress=QUIET, run_key="lost-1")
        check(False, "C8 a reused runKey must be refused")
    except ValueError:
        pass


# ---------------------------------------------------------------------------------------------- D. benign resume
INTRUDER = {"kind": "hostile_arrival", "severity": "threat", "detail": "Megascarab arrived", "subjectId": 77}


class Recover(object):
    def __init__(self, world=None, effect=None, ok=True):
        self.world, self.effect, self.ok, self.seen = world, effect, ok, []

    def __call__(self, B, r):
        self.seen.append(r)
        if not self.ok:
            return None
        V.SITE_NOTES.append({"id": "SITE_DISTURBANCE_INTRUDER", "detail": {"removed": [77]}})
        if self.effect:
            self.world.override.update(self.effect)
        return int(r.get("executed") or 0)


def with_recover(rec, fn):
    old = V.site_recover
    V.site_recover = rec
    try:
        return fn()
    finally:
        V.site_recover = old


def test_resume():
    w = World(stops={1300: INTRUDER})
    B = FakeBridge(w)
    rec = Recover()
    r = with_recover(rec, lambda: B.until(game.tick >= 1500, 1000, progress=QUIET, run_key="res"))
    calls = sa_calls(B)
    check(len(rec.seen) == 1 and len(calls) == 2, "D1 one recover, two segments: %d %d" % (len(rec.seen), len(calls)))
    check(calls[1]["runKey"] == "res~r1" and calls[1]["ticks"] == 700, "D2 resumed segment: %s" % calls[1])
    check(r.state == "hit" and r.hit_tick == 1500 and r.executed == 500, "D3 result after resume: %r" % r)
    m = r.mutations
    check(len(m) == 1 and m[0]["kind"] == "site_recover" and m[0]["atTick"] == 1300 and m[0]["runKey"] == "res"
          and m[0]["notes"] == [{"removed": [77]}], "D4 mutation recorded: %s" % m)
    check(r.coverage["gaps"] == [] and r.coverage["complete"], "D5 a level condition records no gap: %s" % r.coverage)
    check(r.resumes and r.resumes[0]["resumed"] and r.resumes[0]["why"] == "site_recover", "D6 resumes %s" % r.resumes)
    # a real stop (recover refuses) raises GovernorStop, as B.ticks does
    B = FakeBridge(World(stops={1100: INTRUDER}))
    try:
        with_recover(Recover(ok=False), lambda: B.until(game.tick >= 1500, 1000, progress=QUIET))
        check(False, "D7 an unrecoverable stop must raise GovernorStop")
    except CG.GovernorStop as g:
        check(g.result.get("state") == "stopped", "D7 GovernorStop carries the result")
    # a real stop on the hit's own tick: the stop wins, the hit is still readable on the exception
    B = FakeBridge(World(stops={1100: INTRUDER}))
    try:
        with_recover(Recover(ok=False), lambda: B.until(game.tick >= 1100, 1000, progress=QUIET))
        check(False, "D7b must raise")
    except CG.GovernorStop as g:
        cr = getattr(g, "cond_result", None)
        check(cr is not None and cr.hit and cr.hit_tick == 1100, "D7b the hit rides on the GovernorStop: %r" % cr)
    # a clockgate-benign stop (a wild animal downed) resumes with no mutation, noted in BENIGN_STOPS
    downed = {"kind": "downed", "severity": "threat", "detail": "Hare downed", "subjectId": 5}
    B = FakeBridge(World(stops={1200: downed}))
    n0 = len(CG.BENIGN_STOPS)
    r = with_recover(Recover(ok=False), lambda: B.until(game.tick >= 1400, 1000, progress=QUIET))
    check(r.state == "hit" and not r.mutations and len(CG.BENIGN_STOPS) == n0 + 1
          and r.resumes[0]["why"] == "benign", "D8 clockgate benign resume: %r %s" % (r, r.resumes))
    # a hit on the stop's own tick, stop absorbed: the hit stands, no second segment
    B = FakeBridge(World(stops={1250: INTRUDER}))
    r = with_recover(Recover(), lambda: B.until(game.tick >= 1250, 1000, progress=QUIET))
    check(r.state == "hit" and r.hit_tick == 1250 and len(sa_calls(B)) == 1 and len(r.mutations) == 1,
          "D9 hit and stop on one tick: %r" % r)


# ---------------------------------------------------------------------------------------------- E. edge baseline
def test_edge_reset():
    def wet_until(t_dry):
        return lambda key, t: ((t, "ok") if key == "game.tick" else
                               ((t < t_dry), "ok") if key == "cell.is_water cell=110,90" else (None, "error", key))
    dry = edge(cell(110, 90).is_water == False)  # noqa: E712
    # the flip comes after the recovery: segment 2 arms a fresh baseline and still sees it; the gap is recorded
    w = World(reads=wet_until(1400), stops={1300: INTRUDER})
    B = FakeBridge(w)
    r = with_recover(Recover(), lambda: B.until(dry, 1000, progress=QUIET))
    g = r.coverage["gaps"]
    check(r.state == "hit" and r.hit_tick == 1400, "E1 edge after resume still found: %r" % r)
    check(len(g) == 1 and g[0]["fromTick"] == 1300 and g[0]["toTick"] == r.segments[1]["tickFrom"]
          and g[0]["nodes"] == ["n0"] and not r.coverage["complete"],
          "E2 the resume's hole is in coverage.gaps: %s" % g)
    # the recovery itself dries the cell: the restarted baseline cannot see that flip; the gap names the edge
    w = World(reads=wet_until(99999), stops={1300: INTRUDER})
    B = FakeBridge(w)
    rec = Recover(world=w, effect={"cell.is_water cell=110,90": (False, "ok", "")})
    r = with_recover(rec, lambda: B.until(dry, 600, progress=QUIET))
    check(r.state == "done" and r.coverage["gaps"] and r.coverage["gaps"][0]["nodes"] == ["n0"]
          and r.mutations, "E3 a flip inside the recovery is a named hole, not a silent miss: %r" % r)
    # the offline twin agrees: the same edge over one unbroken series WOULD have hit at 1300
    vec = {"spec": D.run_spec(dry, 600), "frames": [{"tick": 1000, "reads": {"cell.is_water cell=110,90": [True, "ok"]}}]
           + [{"tick": t} for t in range(1001, 1300)] + [{"tick": 1300, "reads": {"cell.is_water cell=110,90":
                                                                               [False, "ok"]}}]}
    tw = conds.evaluate(vec["spec"], conds.SeriesSource(vec))
    check(tw.get("state") == "hit" and tw.get("hitTick") == 1300, "E4 twin over the unbroken series: %s"
          % {k: tw.get(k) for k in ("state", "hitTick")})


# ---------------------------------------------------------------------------------------------- F. watch
def test_watch():
    def wet(key, t):
        if key == "game.tick":
            return (t, "ok")
        if key == "cell.is_water cell=110,90":
            return (not (1100 <= t < 1150 or t >= 1400), "ok")
        return (None, "error", key)
    w = World(reads=wet)
    B = FakeBridge(w)
    with B.watch("dry", edge(cell(110, 90).is_water == False), owner="RUN") as h:  # noqa: E712
        B.ticks(300)
        evs = h.events()
    check([e.tick for e in evs] == [1100], "F1 one dry edge in 300 ticks: %s" % evs)
    check([c for t, c in B.calls if t == "jawa/cond_watch"][-1]["action"] == "clear" and not B.watchers,
          "F2 cleared on exit")
    # a recovery inside B.ticks: the watcher is drained, re-armed (baseline restarts), mutation and gap recorded
    w = World(reads=wet, stops={1200: INTRUDER})
    B = FakeBridge(w)
    with_recover(Recover(), lambda: _watch_through(B))
    h = B._last
    check([e.tick for e in h.all] == [1100, 1400], "F3 events across the re-arm: %s" % h.all)
    check(len(h.mutations) == 1 and h.mutations[0]["kind"] == "site_recover", "F4 watch mutation %s" % h.mutations)
    want = D.stateful_ids(h.arm_reply["canonical"])
    check(len(h.gaps) == 1 and h.gaps[0]["fromTick"] == 1200 and want and h.gaps[0]["nodes"] == want
          and all(i.startswith("dry/") for i in want), "F5 watch gap names the companion's ids %s vs %s"
          % (h.gaps, want))
    check(not h.complete, "F5b a re-armed watch is not complete")
    arms = [c for t, c in B.calls if t == "jawa/cond_watch" and c["action"] == "arm"]
    check(len(arms) == 2 and all(a["owner"] == "RUN" for a in arms), "F6 re-armed once under its owner")
    check(not B._watches(), "F7 the registry is empty after exit")


class LostWatch(FakeBridge):
    def cond_watch(self, kw):
        if kw["action"] == "read":
            return {"success": False, "error": "game changed"}
        return FakeBridge.cond_watch(self, kw)


class GapWatch(FakeBridge):
    def cond_watch(self, kw):
        r = FakeBridge.cond_watch(self, kw)
        if kw["action"] == "read":
            r["gap"] = [3, 9]
        return r


def test_watch_loss():
    B = LostWatch(World())
    with B.watch("t", edge(game.tick >= 1010), owner="L") as h:
        B.ticks(20)
        evs = h.events()
        evs2 = h.events()
    check(evs == [] and evs2 == [] and h.lost == "game changed" and not h.complete and len(h.gaps) == 1,
          "F8 a lost watcher is recorded, not an empty success: %s %s" % (h.lost, h.gaps))
    check(sum(1 for t, c in B.calls if t == "jawa/cond_watch" and c["action"] == "read") == 1,
          "F9 no reads after the loss")
    B = GapWatch(World())
    with B.watch("t", edge(game.tick >= 1010), owner="G") as h:
        h.events()
    check(h.gaps == [{"fromSeq": 3, "toSeq": 9, "why": "ring overflow"}], "F10 a [from, to] gap normalises %s" % h.gaps)


def _watch_through(B):
    with B.watch({"dry": edge(cell(110, 90).is_water == False)}, owner="RUN") as h:  # noqa: E712
        B.ticks(500)
        h.all = h.events()
    B._last = h


# ---------------------------------------------------------------------------------------------- G. scenelib
def test_scenelib():
    import scenelib as SL
    w = World()
    fb = FakeBridge(w)

    class SceneFake(FakeBridge):
        stop_on = SL.SCENE_STOP_ON
    B = SceneFake(w)
    old = SL._B
    SL._B = B
    try:
        r = SL.until(game.tick >= 1005, 100, progress=QUIET)
        ev = SL.cond_eval(game.tick >= 0)
        with SL.watch("t", edge(game.tick >= 1010)) as h:
            pass
    finally:
        SL._B = old
    check(r.state == "hit" and sa_calls(B)[0]["stopOn"] == SL.SCENE_STOP_ON, "G1 scenelib.until with the scene stopOn")
    check(ev.get("v") is True, "G2 scenelib.cond_eval %s" % ev)
    check(h.owner == "scene" and not fb.calls, "G3 scenelib.watch owner")


def main():
    for t in (test_shapes, test_verdicts, test_reattach, test_lost_run, test_resume, test_edge_reset, test_watch,
              test_watch_loss, test_scenelib):
        try:
            t()
        except Exception as e:  # noqa: BLE001
            import traceback
            FAILS.append("%s crashed: %s\n%s" % (t.__name__, e, traceback.format_exc()))
    if FAILS:
        print("RED selftest_conds_dsl: %d failure(s)" % len(FAILS))
        for f in FAILS:
            print("  " + f)
        return 1
    print("GREEN selftest_conds_dsl: A shapes, B verdicts, C re-attach, D resume+mutation, E edge reset, F watch, "
          "G scenelib")
    return 0


if __name__ == "__main__":
    sys.exit(main())
