#!/usr/bin/env python3
"""Offline selftest of validation_core.saveload_triplet (PROOF_HARNESS_BUILD_SAVELOAD_TRIPLET).

A fake game stands in for the bridge: a clock, a counter that grows with ticks, a tile temperature, and a save file that is
a snapshot of that state. Its knobs reproduce the two vanilla traps of 2026-11-01 -- PauseOnLoad's extra tick after a load
and the save's temperature quantisation -- plus a save that drops a field and a load that rolls a fresh random value. Every
verdict (IDENTICAL, SAVE_DROPS_STATE, LOAD_NONDETERMINISTIC, UNMEASURED) is driven at least once, and the sanity probes show
the instrument can see: the same quantisation WITHOUT a tolerance must not read IDENTICAL, and a reader blind to the field
the save drops must. Run: python3 selftest_saveload_triplet.py  (prints N/N; exit 0 all pass)."""
import copy
import os
import random
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "modcheck"))

import validation_core as V  # noqa: E402

RES = []


def ok(cond, label, extra=None):
    print("%-4s %s%s" % ("ok" if cond else "FAIL", label, "" if cond or extra is None else "  -- %r" % (extra,)))
    RES.append(bool(cond))


class FakeGame(V._BridgeBase):
    """state: tick, counter (+1 per tick, deterministic), temp (a finer float than the save keeps), widget (a field a buggy
    save may drop), seed (a value a buggy load may re-roll)."""

    def __init__(self, pause_on_load=1, quantise=True, drop_widget=False, nondet_load=False, refuse_save=False,
                 refuse_load_at=None, never_playing_at=None, overshoot=0, clock_dead_after_load=False, noop_load_at=None,
                 load_reply=None, arm_values=None):
        self.s = {"tick": 1000, "counter": 7, "temp": 21.437219, "widget": "on", "seed": 42}
        self.saves = {}
        self.pause_on_load, self.quantise, self.drop_widget = pause_on_load, quantise, drop_widget
        self.nondet_load, self.refuse_save, self.refuse_load_at = nondet_load, refuse_save, refuse_load_at
        self.never_playing_at, self.overshoot = never_playing_at, overshoot
        self.clock_dead_after_load, self.loads, self.clock_dead = clock_dead_after_load, 0, False
        self.rng = random.Random(1)
        self.noop_load_at, self.load_reply, self.arm_values = noop_load_at, load_reply, arm_values
        self.calls = []

    def _raw(self, tool, kw):
        self.calls.append(tool)
        if tool == "jawa/time_clock":
            return {"success": False} if self.clock_dead else {"success": True, "ticksGame": self.s["tick"]}
        if tool == "rimworld/save_game":
            if self.refuse_save:
                return {"success": False, "error": "no game"}
            snap = copy.deepcopy(self.s)
            if self.quantise:            # SurfaceLayer: ushort RoundToInt((t+300)*10)
                snap["temp"] = round((snap["temp"] + 300) * 10) / 10.0 - 300
            if self.drop_widget:
                snap.pop("widget")
            self.saves[kw["saveName"]] = snap
            return {"success": True}
        if tool == "rimworld/load_game":
            self.loads += 1
            if self.refuse_load_at == self.loads:
                return {"success": False, "error": "load refused"}
            if self.noop_load_at == self.loads:          # queued, never ran: the old map stays Playing
                return {"success": True, "message": "queued"}
            if self.load_reply is not None:
                return self.load_reply
            snap = copy.deepcopy(self.saves[kw["saveName"]])
            snap.setdefault("widget", "off")         # a dropped field comes back as its default
            if self.arm_values:                         # per-load value (arm B = load 1, arm C = load 2)
                snap["temp"] = self.arm_values[self.loads]
            if self.nondet_load:
                snap["seed"] = self.rng.randint(0, 10 ** 6)
            self.s = snap
            self._advance(self.pause_on_load)        # Game.LoadGame + Prefs.PauseOnLoad: one DoSingleTick
            if self.clock_dead_after_load:
                self.clock_dead = True
            return {"success": True, "message": "queued"}
        return {"success": True}

    def _advance(self, n):
        self.s["tick"] += n
        self.s["counter"] += n

    def ticks(self, n):
        self._advance(int(n) + self.overshoot)
        return {"success": True, "advanced": n}


def reader(fields=("counter", "temp", "widget", "seed")):
    def read(B):
        return {"map": {k: B.s.get(k) for k in fields}}
    return read


def run(g, read=None, **kw):
    files = {}

    def saves_stat():
        return dict(files)

    def wait_saved(name):
        if name in g.saves:
            files[name + ".rws"] = (len(repr(g.saves[name])), 1)
            return True
        return False

    def wait_playing(B):
        if g.never_playing_at == g.loads:
            return False, "Entry"
        return True, 1

    return V.saveload_triplet(g, read or reader(), save_name="RM_triplet_selftest", saves_stat=saves_stat,
                              wait_saved=wait_saved, wait_playing=wait_playing, **kw)


TOL = {"map.temp": 0.06}

# 1. IDENTICAL: quantised temperature within tolerance, PauseOnLoad tick absorbed by measuring the clock
r = run(FakeGame(), tolerance=TOL)
ok(r["verdict"] == V.TRIPLET_IDENTICAL, "IDENTICAL with quantised temp under tolerance and the +1 load tick", r["why"])
ok(r["arms"]["A"]["tick"] == r["arms"]["B"]["tick"] == r["arms"]["C"]["tick"] == r["target"] == 1060,
   "all three arms read at the same measured tick (target 1060)", {k: v["tick"] for k, v in r["arms"].items()})
ok(r["arms"]["B"]["loadedAt"] == 1001 and r["arms"]["C"]["loadedAt"] == 1001,
   "loaded arms measured one tick past the save (PauseOnLoad), not assumed", r["arms"]["B"]["loadedAt"])
ok(r["AB"] == {} and r["BC"] == {}, "no differing fields reported on IDENTICAL", (r["AB"], r["BC"]))

# 1b. glob tolerance key works the same
r = run(FakeGame(), tolerance={"*.temp": 0.06})
ok(r["verdict"] == V.TRIPLET_IDENTICAL, "an fnmatch tolerance pattern ('*.temp') applies", r["why"])

# 2. sanity: the same quantisation WITHOUT tolerance is seen as a save difference (the instrument can see 0.03 C)
r = run(FakeGame())
ok(r["verdict"] == V.TRIPLET_SAVE_DROPS and list(r["AB"]) == ["map.temp"],
   "untolerated quantisation reads SAVE_DROPS_STATE on map.temp alone", (r["verdict"], r["AB"]))

# 2b. sanity: no PauseOnLoad tick also aligns (measured, not assumed +1)
r = run(FakeGame(pause_on_load=0), tolerance=TOL)
ok(r["verdict"] == V.TRIPLET_IDENTICAL and r["arms"]["B"]["loadedAt"] == 1000, "a load with no extra tick aligns too",
   (r["verdict"], r["arms"]["B"]["loadedAt"]))

# 3. SAVE_DROPS_STATE: the save loses a field; both loads agree on the default
r = run(FakeGame(drop_widget=True), tolerance=TOL)
ok(r["verdict"] == V.TRIPLET_SAVE_DROPS, "a dropped field reads SAVE_DROPS_STATE", r["why"])
ok(r["AB"] == {"map.widget": ["on", "off"]} and r["BC"] == {}, "AB names the dropped field; BC is empty", (r["AB"], r["BC"]))
# 3b. sanity: a reader blind to that field cannot see it (so a reader must cover what it claims)
r = run(FakeGame(drop_widget=True), read=reader(("counter", "temp", "seed")), tolerance=TOL)
ok(r["verdict"] == V.TRIPLET_IDENTICAL, "a reader that omits the dropped field reads IDENTICAL (reader coverage matters)",
   r["verdict"])

# 4. LOAD_NONDETERMINISTIC: each load re-rolls a value
r = run(FakeGame(nondet_load=True), tolerance=TOL)
ok(r["verdict"] == V.TRIPLET_LOAD_NONDET, "a re-rolled value per load reads LOAD_NONDETERMINISTIC", r["why"])
ok("map.seed" in r["BC"], "BC names the re-rolled field", r["BC"])
# 4b. nondeterminism wins over a simultaneous drop: B != C decides first
r = run(FakeGame(nondet_load=True, drop_widget=True), tolerance=TOL)
ok(r["verdict"] == V.TRIPLET_LOAD_NONDET and "map.widget" in r["AB"], "drop + nondeterminism -> LOAD_NONDETERMINISTIC, "
   "AB still lists the drop", (r["verdict"], r["AB"]))

# 5. UNMEASURED: every way an arm goes unread
cases = [
    ("save refused", dict(g=FakeGame(refuse_save=True))),
    ("first load refused", dict(g=FakeGame(refuse_load_at=1))),
    ("second load refused", dict(g=FakeGame(refuse_load_at=2))),
    ("load never Playing", dict(g=FakeGame(never_playing_at=2))),
    ("arm overshoots the target", dict(g=FakeGame(overshoot=1))),
    ("clock unreadable after load", dict(g=FakeGame(clock_dead_after_load=True))),
    ("reader returns None", dict(g=FakeGame(), read=lambda B: None)),
    ("reader returns empty", dict(g=FakeGame(), read=lambda B: {})),
    ("reader raises", dict(g=FakeGame(), read=lambda B: 1 / 0)),
]
for label, c in cases:
    r = run(c["g"], read=c.get("read"), tolerance=TOL)
    ok(r["verdict"] == V.TRIPLET_UNMEASURED and r["why"], "UNMEASURED: %s (%s)" % (label, r["why"]), r["verdict"])

# 5b. a load landing further than TRIPLET_LOAD_SLACK past the save is not evidence the load ran
r = run(FakeGame(pause_on_load=V.TRIPLET_LOAD_SLACK + 2), tolerance=TOL)
ok(r["verdict"] == V.TRIPLET_UNMEASURED and "did not take" in (r["why"] or ""), "a load far past the saved tick is UNMEASURED",
   r["why"])

# 5d. GPT review 2026-11-04: a load answered success that never ran must NOT read IDENTICAL (B would reread A)
for at in (1, 2):
    r = run(FakeGame(noop_load_at=at), tolerance=TOL)
    ok(r["verdict"] == V.TRIPLET_UNMEASURED and "did not take" in (r["why"] or ""),
       "a queued load that never ran (load %d) is UNMEASURED, not IDENTICAL" % at, (r["verdict"], r["why"]))
for reply in ({}, {"success": None}, {"message": "queued"}):
    r = run(FakeGame(load_reply=reply), tolerance=TOL)
    ok(r["verdict"] == V.TRIPLET_UNMEASURED, "a load reply without success:true (%r) is UNMEASURED" % (reply,), r["verdict"])


# 5e. a reader that ticks a different amount per arm is UNMEASURED (arms read at different ticks)
def uneven(B, n=[0]):
    n[0] += 1
    B.ticks(n[0])
    return {"c": B.s["counter"]}


r = run(FakeGame(), read=uneven, tolerance=TOL)
ok(r["verdict"] == V.TRIPLET_UNMEASURED and "must not advance" in (r["why"] or ""), "uneven reader ticks -> UNMEASURED",
   r["why"])


def even(B):
    B.ticks(2)                                       # a framed census ticks 2 in every arm: still aligned
    return {"c": B.s["counter"]}


r = run(FakeGame(), read=even, tolerance=TOL)
ok(r["verdict"] == V.TRIPLET_UNMEASURED and "must not advance" in (r["why"] or ""), "GPT r2: even a reader ticking the same "
   "amount per arm is UNMEASURED (equal end ticks do not prove equal capture ticks)", (r["verdict"], r["why"]))
ok(all(a["readTick"] == r["target"] for a in run(FakeGame(), tolerance=TOL)["arms"].values()),
   "a non-ticking reader reads every arm at the target tick")

# 5h. GPT r2: tolerances are validated before anything is saved
for bad in ({"t": float("nan")}, {"t": -1}, {"t": "0.1"}, {"t": True}):
    g = FakeGame()
    try:
        run(g, tolerance=bad)
        ok(False, "tolerance %r raises ValueError" % (bad,))
    except ValueError:
        ok("rimworld/save_game" not in g.calls, "tolerance %r raises ValueError before saving" % (bad,))

# 5f. readings the comparison cannot trust
for label, rd in (("NaN", lambda B: {"t": float("nan")}), ("inf", lambda B: {"t": float("inf")}),
                  ("empty list", lambda B: [])):
    r = run(FakeGame(), read=rd, tolerance={"t": 1.0})
    ok(r["verdict"] == V.TRIPLET_UNMEASURED, "UNMEASURED: %s reading (%s)" % (label, r["why"]), r["verdict"])

# 5g. tolerance is not transitive: A=0, B=0.75, C=1.5 with tol 1 -> AB and BC equal, AC not -> no verdict
g = FakeGame(quantise=False, arm_values={1: 0.75, 2: 1.5})
g.s["temp"] = 0.0
r = run(g, read=reader(("temp",)), tolerance={"map.temp": 1.0})
ok(r["verdict"] == V.TRIPLET_UNMEASURED and "ambiguous" in (r["why"] or ""), "non-transitive tolerance -> UNMEASURED "
   "(not IDENTICAL)", (r["verdict"], r["AB"], r["BC"], r["AC"]))

# 5c. a same-name save already present refuses before saving
g = FakeGame()
r = V.saveload_triplet(g, reader(), save_name="X", saves_stat=lambda: {"X.rws": (1, 1)}, wait_saved=lambda n: True,
                       wait_playing=lambda B: (True, 1))
ok(r["verdict"] == V.TRIPLET_UNMEASURED and "rimworld/save_game" not in g.calls, "an existing same-name save refuses, "
   "nothing saved", g.calls)

# 6. ticks below the minimum is a caller error
for t in (1, V.TRIPLET_MIN_TICKS - 1):
    try:
        run(FakeGame(), ticks=t)
        ok(False, "ticks=%d raises ValueError" % t)
    except ValueError:
        ok(True, "ticks=%d raises ValueError" % t)
ok(V.TRIPLET_MIN_TICKS > V.TRIPLET_LOAD_SLACK, "TRIPLET_MIN_TICKS > TRIPLET_LOAD_SLACK (a no-op load cannot pass as fresh)")

# 7. triplet_diff units
ok(V.triplet_diff({"a": True}, {"a": False}, {"a": 5}) == {"a": [True, False]}, "triplet_diff: no tolerance on a bool")
ok(V.triplet_diff({"a": 1.0}, {"b": 1.0}) == {"a": [1.0, None], "b": [None, 1.0]}, "triplet_diff: one-sided keys differ")
ok(V.triplet_diff({"a": [1, 2]}, {"a": [1, 2]}) == {}, "triplet_diff: equal leaves")
ok(V.triplet_diff({"a": 1}, {"a": True}) == {"a": [1, True]} and V.triplet_diff({"a": 1}, {"a": "1"}) == {"a": [1, "1"]},
   "triplet_diff: 1 vs True and 1 vs '1' differ")
ok(V.triplet_diff({"a": 1}, {"a": 1.0}) == {}, "triplet_diff: 1 vs 1.0 equal (both numbers)")
ok(V.triplet_diff({"a": 2 ** 53 + 1}, {"a": float(2 ** 53)}, {"a": 0.5}) != {}, "GPT r3: int/float compared exactly under a "
   "tolerance (2**53+1 vs 2**53.0)")
ok(V._flatten({"x": 1, "y": {}}) != V._flatten({"x": 1}), "_flatten: an empty dict is kept as a leaf")
ok(len(V._flatten({"a.b": 1, "a": {"b": 1}})) == 2, "_flatten: a dotted key and a nested path stay two keys (escaped)",
   V._flatten({"a.b": 1, "a": {"b": 1}}))
for a, b in (({"a.b": 1}, {"a": {"b": 1}}), ({"x[0]": 1}, {"x": [1]}), ({1: 2}, {"1": 2}), ({1: 2}, {"<int:1>": 2})):
    ok(V.triplet_diff(V._flatten(a), V._flatten(b)) != {}, "GPT r2: %r and %r do not alias across arms" % (a, b),
       (V._flatten(a), V._flatten(b)))
ok(V._flatten({"m": {"x": [1, {"y": 2}], "e": []}}) == {"m.e": [], "m.x[0]": 1, "m.x[1].y": 2}, "_flatten: nested keys",
   V._flatten({"m": {"x": [1, {"y": 2}], "e": []}}))


# 8. the GSS wiring (GimmeSomeSlack/validation.py --triplet): run_triplet over a fake game whose census is the cord set
def gss_wiring():
    gdir = os.path.join(HERE, "..", "GimmeSomeSlack")
    sys.path.insert(0, os.path.abspath(gdir))
    import validation as GV   # noqa: E402
    import types

    class GssFake(FakeGame):
        probe_type = "fake"

        # 8b (live 2026-11-06): GSS lays cords over render frames after a load. lay=(n1, n2) leaves load k with only nk of
        # the 20 edges laid (a different partial set per load) until the probe's complete "rebuild"; stuck=True is a
        # rebuild that still leaves edges pending. The live arm (before any load) is fully laid.
        def __init__(self, lay=None, stuck=False, **kw):
            FakeGame.__init__(self, **kw)
            self.lay, self.stuck, self.laid = lay, stuck, 20
            self.rebuilds = 0

        def _raw(self, tool, kw):
            r = FakeGame._raw(self, tool, kw)
            if tool == "rimworld/load_game" and self.lay:
                self.laid = self.lay[self.loads - 1]
            return r

        def probe(self, cmd, wait_s=20.0):
            if cmd == "rebuild":
                self.rebuilds += 1
                if not self.stuck:
                    self.laid = 20
                return {"success": True, "cmd": "rebuild"}
            if cmd != "census":
                return {"success": True}
            if self.lay:
                edges = ["e%02d" % i for i in range(self.laid)]
            else:
                edges = ["e%d" % self.s["counter"] if self.drop_widget and self.s["widget"] == "off" else "e"]
            return {"success": True, "edgeHashes": edges, "geometryHash": "g", "pending": 20 - self.laid,
                    "ticksGame": self.s["tick"], "ends": [], "nodeTypes": {"seed": self.s["seed"]}}

    out = {}
    for label, g in (("identical", GssFake()), ("drops", GssFake(drop_widget=True)), ("nondet", GssFake(nondet_load=True)),
                     ("sliced", GssFake(lay=(8, 11))), ("stuck", GssFake(lay=(8, 11), stuck=True))):
        files = {}
        saved = (V._saves_stat, V._wait_saved, V._wait_playing, GV.Bridge, GV.time.sleep)
        try:
            V._saves_stat = lambda: dict(files)
            V._wait_saved = lambda name, g=g: bool(files.__setitem__(name + ".rws", (1, 1)) or name in g.saves)
            V._wait_playing = lambda B: (True, 1)
            GV.Bridge = lambda g=g: g
            GV.time.sleep = lambda s: None
            res = GV.run_triplet(types.SimpleNamespace(triplet_name="T_" + label, triplet_ticks=30))
        finally:
            V._saves_stat, V._wait_saved, V._wait_playing, GV.Bridge, GV.time.sleep = saved
        out[label] = (res["triplet"]["verdict"], [r["status"] for r in res["rows"]])
        out[label + "_rebuilds"] = g.rebuilds
    return out


try:
    w = gss_wiring()
    ok(w["identical"] == (V.TRIPLET_IDENTICAL, ["PASS"]), "GSS --triplet: unchanged cords -> PASS row", w["identical"])
    ok(w["drops"] == (V.TRIPLET_SAVE_DROPS, ["FAIL"]), "GSS --triplet: a save-dropped field -> FAIL row", w["drops"])
    ok(w["nondet"] == (V.TRIPLET_LOAD_NONDET, ["FAIL"]), "GSS --triplet: a per-load re-roll -> FAIL row", w["nondet"])
    ok(w["sliced"] == (V.TRIPLET_IDENTICAL, ["PASS"]) and w["sliced_rebuilds"] >= 3,
       "GSS --triplet: a different partial post-load lay per load is completed by a rebuild before census -> PASS row "
       "(live 2026-11-06 read it as LOAD_NONDETERMINISTIC)", (w["sliced"], w["sliced_rebuilds"]))
    ok(w["stuck"][0] not in (V.TRIPLET_IDENTICAL, V.TRIPLET_SAVE_DROPS, V.TRIPLET_LOAD_NONDET)
       and w["stuck"][1] == ["UNMEASURED"],
       "GSS --triplet: edges still pending after the rebuild -> UNMEASURED, never a verdict", w["stuck"])
except Exception as ex:  # noqa: BLE001 - an import/wiring crash is a FAIL, never a skip
    ok(False, "GSS --triplet wiring ran", repr(ex))


# 9. the live clause is readable whole and bound to the --triplet run. The ledger cuts a criterion at
# model.CRITERION_TEXT_MAX; the supervisor refuses a live round on a cut criterion no prose extends ("cut at 160 chars on
# the ledger and no prose holds the rest", 2026-11-04). Read A1 exactly as the live round does (relentless_live.Fx.prose +
# whole_criterion over the ledger's own copy) and check the proof line it would run is the GSS --triplet run.
ITEM = "PROOF_HARNESS_BUILD_SAVELOAD_TRIPLET"
try:
    ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
    sys.path.insert(0, os.path.join(ROOT, "src", "RimMandrake", "rimflow"))
    import relentless_live as RL   # noqa: E402
    fx = RL.Fx(books=ROOT)
    item = fx.item(ITEM) or {}
    a1 = [c for c in item.get("criteria") or [] if c.get("id") == "A1"]
    ok(len(a1) == 1 and a1[0].get("level") == "L2", "ledger holds live criterion A1 at L2", a1)
    whole = RL.whole_criterion(a1[0], fx.prose(ITEM)) if a1 else {"cut": True}
    ok(not whole.get("cut") and not whole.get("retiered"), "A1 reads whole (ledger copy extended by prose/.criteria)",
       whole)
    text = whole.get("text") or ""
    ok(all(w in text for w in ("saves once", "loads twice", "all three arms", "one measured tick", "IDENTICAL",
                               "validation.py --triplet exit 0")),
       "A1 whole text names the save-once/load-twice/three-arm IDENTICAL clause and its --triplet exit", text)
    with open(os.path.join(ROOT, "infrastructure", "state", "live_proofs", ITEM + ".txt"), encoding="utf-8") as f:
        a1_lines = [ln for ln in f.read().splitlines() if ln.startswith("live-proof A1:")]
    ok(len(a1_lines) == 1 and a1_lines[0].rstrip().endswith("GimmeSomeSlack/validation.py --triplet < /dev/null"),
       "live-proof A1 ends on the GSS --triplet run, whose exit is the verdict", a1_lines)
except Exception as ex:  # noqa: BLE001 - an unreadable ledger or proof file is a FAIL, never a skip
    ok(False, "live criterion A1 binding read", repr(ex))

n = sum(RES)
print("%d/%d" % (n, len(RES)))
sys.exit(0 if n == len(RES) else 1)
