#!/usr/bin/env python3
"""Selftest for testpilot.py (harness step 13): the forced-failure proofs of its done-when, offline, on a fake game.

  1. no reload is logged without a rule (a rule-less or unknown-rule reload is refused before anything is written,
     and every `reload` event in every run names a rule and a decision logged before it);
  2. a C# fix forces a logged reload naming its rule and the reload cost used: cheap = a few more tests then R3,
     expensive = drain every valuable test first, either = the maximum acceptance delay; unmeasured = expensive;
  3. an owner return mid-test yields within the bound, keeps completed evidence and requeues the in-flight test;
  4. a pilot handoff loses no queued candidate (one queued before, one during the handoff), the game stays up, the
     stale pilot is refused every act;
  5. a rebuild touching one scenario's footprint re-runs only that scenario plus the ones the taint note names;
  6. hot-load classes: a live-class harness repair lands on the running game, its PASS counts only after a clean
     re-pass after a state reset; a reload/cs-class repair waits sealed.
Writes only under a temp dir (ARENA_ROOT points there).
"""
import json
import os
import shutil
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
TMP = Path(tempfile.mkdtemp(prefix="selftest_arena_testpilot_"))
os.environ["ARENA_ROOT"] = str(TMP / "arena")
import arena_lane as L  # noqa: E402
import testpilot as T  # noqa: E402

L.canonical_saves = lambda: {"CANON_START_SAVE"}
L.canonical_worlds = lambda: [{"name": "Canon'World", "seed": "canonseed"}]

FAILS = []
SHA = ["%x" % i * 40 for i in range(1, 10)]
CLONE = str(TMP / "pilotclone")


def check(ok, msg):
    print(("ok    " if ok else "FAIL  ") + msg)
    if not ok:
        FAILS.append(msg)


def raises(exc, fn, *a, **k):
    try:
        fn(*a, **k)
    except exc as e:
        return str(e)
    return None


class FakeDriver:
    def __init__(self, launch_s=22.0):
        self.t = 1000.0
        self.running, self.launch_s = False, launch_s
        self.owner_back = False
        self.log_mtime = 0.0
        self.active = ["ludeon.rimworld"]
        self.head = {}
        self.calls = []
        self.rc = {}                    # scenario id -> proof rc (default 0)
        self.during = {}                # scenario id -> callable run inside the proof (before the owner poll)
        self.colonists = 3

    def clock(self):
        return self.t

    def bridge_take(self, host, purpose, idle_ok):
        self.calls.append(("take", host, idle_ok))
        return True, "taken"

    def bridge_release(self, host):
        self.calls.append(("release", host))
        return True, "released"

    def game_running(self):
        return self.running

    def stop_game(self):
        self.calls.append(("stop",))
        self.running = False

    def known_tiers(self):
        return {"slime"}

    def expected_active(self, profile, tier):
        return ["ludeon.rimworld"]

    def clone_dirty(self, clone):
        return []

    def apply_minimal(self):
        self.calls.append(("minimal",))
        return True, "swapped"

    def apply_tier(self, tier):
        return True, "wrote"

    def restore_modlist(self):
        self.calls.append(("restore",))
        self.t += 30.0
        return True, "restored"

    def clone_head(self, clone):
        return self.head.get(clone)

    def restore_mods(self, mods, clone):
        self.calls.append(("restore_mods", tuple(mods)))
        return True, "main redeployed", "c" * 40

    def deploy(self, mod, clone):
        self.calls.append(("deploy", mod, self.running))
        self.active.append("mandrake.rm.%s" % mod.lower())
        return True, "deployed"

    def package_ids(self, mods, clone):
        return ["mandrake.rm.%s" % m.lower() for m in mods]

    def launch_and_wait(self):
        self.calls.append(("launch",))
        self.t += self.launch_s
        self.running = True
        self.log_mtime = self.t
        return True, "bridge token seen"

    def start_quicktest(self):
        self.t += 5.0
        return True, "Playing"

    def load_save(self, name):
        self.calls.append(("load_save", name))
        return True, "loaded"

    def owner_returned(self):
        return self.owner_back

    def game_facts(self):
        return {"ingame_canary": {"ok": self.colonists > 0, "problems": []}, "live_colonists": self.colonists,
                "player_log_mtime": self.log_mtime, "game_version": "1.6.4633 rev1", "active_mods": list(self.active),
                "world": {"name": "Quick-IX", "seed": "wulan"}}

    def checkout(self, clone, sha):
        self.head[clone] = sha
        return True, ""

    def run_scenario(self, argv, clone, poll, poll_s):
        sid = argv[-1]
        self.calls.append(("scenario", sid))
        self.t += 10.0
        if sid in self.during:
            self.during[sid]()
        poll()
        return self.rc.get(sid, 0), "scenario %s rc=%d" % (sid, self.rc.get(sid, 0))

    def reconnect(self):
        return True, "reconnected"

    def restage(self):
        return False, "no restage"


def fresh(name, owner_playing=None):
    root = TMP / name
    p = T.ppaths(root)
    cfg = {"steve": {"game_version": "1.6.4633 rev1"}, "archmagi": {"game_version": "1.6.4633 rev1"}}
    if owner_playing is not None:
        cfg["archmagi"]["owner_playing"] = owner_playing
    L.write_config(p, cfg)
    return root, p


def plan(*ids, fixture=None, **extra):
    scns = []
    for i in ids:
        s = {"id": i, "argv": ["python3", "proof.py", i]}
        s.update(extra.get(i, {}))
        scns.append(s)
    out = {"scenarios": scns}
    if fixture:
        out["fixture_save"] = fixture
    return out


def ev(root, event=None):
    return [e for e in L.read_events(L.lane_paths(root), T.ARM) if event is None or e["event"] == event]


def decisions(p, kind=None):
    return [d for d in T._read(p["decisions"]) if kind is None or d.get("kind") == kind]


def pilot(root, d, pid, lane="steve"):
    return T.Pilot(lane, d, pid, clone=CLONE, root=root)


def actions(steps):
    return [(s["decision"]["action"], s["decision"].get("rule"), s["decision"].get("scenario")) for s in steps]


def every_reload_has_a_rule(root, p, label):
    """The invariant behind 'no reload logged without a rule', checked on every run's own log."""
    rel = ev(root, "reload")
    ids = {d["id"]: d for d in decisions(p, "reload")}
    bad = []
    for e in rel:
        why = (e.get("detail") or {}).get("why") or ""
        did = why.split()[0].split("=", 1)[1] if why.startswith("decision=") else None
        if e.get("rule") not in L.RELOAD_RULES or did not in ids or ids[did]["rule"] != e["rule"]:
            bad.append(e)
    check(rel and not bad, "%s: all %d reload events name a rule and the decision logged before them" %
          (label, len(rel)))
    return bad


# ---------------------------------------------------------------- 1. no reload without a rule
def t_rule_refused():
    root, p = fresh("norule")
    d = FakeDriver()
    T.enqueue(p, "ITEM_A", SHA[0], "B1", plan("s1"))
    pl = pilot(root, d, "P1")
    pl.wake()
    for bad in ({"rule": None, "cand": "ITEM_A@1", "why": "x"}, {"rule": "R9", "cand": "ITEM_A@1", "why": "x"},
                {"cand": "ITEM_A@1", "why": "x"}):
        why = raises(T.PilotRefused, pl.reload, bad)
        check(why and "rule" in why, "reload with rule %r refused: %s" % (bad.get("rule"), why))
    check(not ev(root, "reload") and not decisions(p) and ("launch",) not in d.calls,
          "a refused rule-less reload wrote no reload event, no decision and launched nothing")
    st = pl.step()
    check(st["decision"]["action"] == "reload" and st["decision"]["rule"] == "R0", "a cold start is R0")
    every_reload_has_a_rule(root, p, "norule")
    pl.lane.reload("minimal", None, rule="R2", why="a bypass of the pilot")      # sanity probe: the check can see
    bad = [e for e in ev(root, "reload") if "bypass" in ((e.get("detail") or {}).get("why") or "")]
    rel = ev(root, "reload")
    ids = {x["id"] for x in decisions(p, "reload")}
    seen = [e for e in rel if not ((e.get("detail") or {}).get("why") or "").startswith("decision=")
            or e["detail"]["why"].split()[0].split("=", 1)[1] not in ids]
    check(bad and seen == bad, "probe: a reload that bypassed the pilot's decision log IS caught by the checker")


# ---------------------------------------------------------------- 2. a C# fix forces a costed R3
def _cs_setup(name, launch_s, extra_scn=6):
    root, p = fresh(name)
    d = FakeDriver(launch_s=launch_s)
    ids = ["s%d" % i for i in range(1, extra_scn + 1)]
    a = T.enqueue(p, "ITEM_CS", SHA[0], "B1", plan(*ids, **{"s1": {"taints": []}}), mods=["Slime"],
                  has_dll=True, changed_files=["src/RimMandrake/Slime/Source/Slime.cs"], now=d.t)
    check(a["class"] == "cs", "%s: a .cs change is class cs" % name)
    d.rc["s1"] = 1
    pl = pilot(root, d, "P1")
    pl.wake()
    s0 = pl.step()                      # R0
    s1 = pl.step()                      # s1 fails
    check(s0["decision"]["rule"] == "R0" and s1["result"]["status"] == "fail", "%s: R0 then s1 FAILS" % name)
    rep = T.enqueue(p, "ITEM_CS", SHA[1], "FIX1", plan(*ids), mods=["Slime"], has_dll=True, parent=a["cand"],
                    changed_files=["src/RimMandrake/Slime/Source/Slime.cs"], kind="repair", fault="MOD",
                    review="review-1", now=d.t)
    d.rc["s1"] = 0
    return root, p, d, pl, a, rep


def t_cs_cheap():
    root, p, d, pl, a, rep = _cs_setup("cs_cheap", 22.0)
    check(rep["class"] == "cs", "the fix subagent's C# repair is class cs: it cannot be hot-loaded")
    check(not T.hot_appliable(rep, T.read_session(p, "steve")["game"], T.cand_by_id(p)),
          "a cs repair is not hot-appliable onto the running game (S3)")
    steps = [pl.step() for _ in range(4)]
    acts = actions(steps)
    check(acts[:3] == [("test", None, "s2"), ("test", None, "s3"), ("test", None, "s4")],
          "cheap reload (27 s measured): exactly 3 more unrelated tests run first: %s" % acts[:3])
    r3 = steps[3]["decision"]
    check(r3["action"] == "reload" and r3["rule"] == "R3" and r3["cand"] == rep["cand"],
          "then R3 loads the sealed repair: %s %s" % (r3.get("rule"), r3.get("cand")))
    check(r3["cost"]["cost_s"] == 27.0 and r3["cost"]["class"] == "cheap" and "measured" in r3["cost"]["basis"],
          "R3 names the measured cost used: %s" % r3["cost"])
    rl = [e for e in ev(root, "reload") if e["rule"] == "R3"]
    why = (rl[-1].get("detail") or {}).get("why", "") if rl else ""
    check(len(rl) == 1 and "rule=R3" in why and "cost_used=27.0" in why and "class=cheap" in why,
          "the lane's reload event names its rule and cost: %s" % why[:160])
    dep = [c for c in d.calls if c[0] == "deploy"]
    check(dep and all(c[2] is False for c in dep), "every C# deploy happened with the game down (S3)")
    check(T.states(p)[a["cand"]]["state"] == "superseded", "the failed attempt is superseded once the repair loads")
    every_reload_has_a_rule(root, p, "cs_cheap")


def t_cs_expensive():
    root, p, d, pl, a, rep = _cs_setup("cs_exp", 300.0)
    steps = [pl.step() for _ in range(6)]
    acts = actions(steps)
    check([x[2] for x in acts[:5]] == ["s2", "s3", "s4", "s5", "s6"],
          "expensive reload (305 s): every valuable test drains first: %s" % acts[:5])
    r3 = steps[5]["decision"]
    check(r3["rule"] == "R3" and r3["cost"]["class"] == "expensive" and r3["cost"]["cost_s"] == 305.0,
          "then R3, logged with the expensive cost used: %s %s" % (r3.get("rule"), r3.get("cost")))
    every_reload_has_a_rule(root, p, "cs_exp")


def t_cs_max_delay():
    root, p, d, pl, a, rep = _cs_setup("cs_delay", 300.0)
    pl.step()                           # s2
    d.t += 3600.0
    st = pl.step()
    dec = st["decision"]
    check(dec["rule"] == "R3" and "maximum acceptance delay" in dec["why"] and dec["drain"]["valuable_left"] > 0,
          "expensive, valuable tests left, but the max acceptance delay passed: R3 now (%s)" % dec.get("why"))
    every_reload_has_a_rule(root, p, "cs_delay")


def t_unmeasured():
    root, p = fresh("unmeasured")
    rule = T.load_rule()
    c = T.reload_cost(p, rule, "steve", "minimal", None)
    check(c["cost_s"] is None and c["class"] == "expensive" and "UNMEASURED" in c["basis"],
          "no measured load time: treated as expensive and logged UNMEASURED, never 22 s: %s" % c)


# ---------------------------------------------------------------- 3. the owner's return
def t_owner_yield():
    root, p = fresh("owner", owner_playing=True)
    d = FakeDriver()
    T.enqueue(p, "ITEM_O", SHA[0], "B1", plan("s1", "s2", "s3"))
    pl = pilot(root, d, "P1", lane="archmagi")
    pl.wake()
    take = [c for c in d.calls if c[0] == "take"]
    check(take and take[-1][2] is True, "Archmagi while he plays: the take is --idle-ok")
    pl.step()                           # R0
    r1 = pl.step()                      # s1 passes
    d.during["s2"] = lambda: setattr(d, "owner_back", True)
    r2 = pl.step()                      # he comes back mid-s2
    check(r1["result"]["status"] == "pass" and r2["decision"]["action"] == "yield", "owner return mid-test: yield")
    y = r2["result"]
    check(y["within"] and y["steps"] <= 2 and y["seconds"] <= 300,
          "yield within the bound: %s steps, %s s (bound 2 steps, 300 s)" % (y["steps"], y["seconds"]))
    st = T.scenario_status(p, T.cand_by_id(p)["ITEM_O@1"])
    check(st["s1"]["status"] == "pass" and st["s2"]["status"] == "invalid" and "owner" in st["s2"]["why"],
          "completed evidence kept (s1 pass), the in-flight test is invalid (s2)")
    check(T.states(p)["ITEM_O@1"]["state"] == "queued", "the candidate is requeued (M4)")
    check(("restore",) in d.calls and d.calls[-1][0] == "release" and not d.running,
          "the game is stopped, his list restored and the bridge released")
    check(raises(T.StalePilot, pl.step) is not None or pl.step()["decision"]["action"] == "yield",
          "the yielded pilot makes no further act")
    why = raises(T.PilotRefused, pilot(root, d, "P2", lane="archmagi").wake)
    check(why and "owner" in why, "no new take while he is home: %s" % why)
    d.owner_back = False
    d.during.clear()
    p3 = pilot(root, d, "P3", lane="archmagi")
    p3.wake()
    steps = p3.run_pass()
    ran = [c[1] for c in d.calls if c[0] == "scenario"]
    check(ran.count("s1") == 1 and ran.count("s2") == 2 and T.states(p)["ITEM_O@1"].get("verdict") == "pass",
          "after he leaves, s2 re-runs, s1 is not re-run, and the item resolves PASS: %s" % actions(steps))
    every_reload_has_a_rule(root, p, "owner")


# ---------------------------------------------------------------- 4. the handoff
def t_handoff():
    root, p = fresh("handoff")
    d = FakeDriver()
    T.enqueue(p, "ITEM_H", SHA[0], "B1", plan("s1", "s2"))
    p1 = pilot(root, d, "P1")
    p1.wake()
    p1.step()                           # R0
    p1.step()                           # s1
    T.enqueue(p, "ITEM_Q", SHA[1], "B2", plan("q1"))
    why = raises(T.PilotRefused, pilot(root, d, "P2").wake)
    check(why and "hands off" in why, "a second pilot cannot wake while P1 is live: %s" % why)
    with T.locked(p1.p):                # handoff only at a test boundary
        s = T.read_session(p, "steve")
        s["in_flight"] = {"cand": "ITEM_H@1", "scenario": "s2", "t": d.t}
        T.write_session(p, "steve", s)
    check(raises(T.PilotRefused, p1.handoff) is not None, "handoff refused while a test is in flight")
    s["in_flight"] = None
    T.write_session(p, "steve", s)
    launches = d.calls.count(("launch",))
    p1.handoff()
    check(d.running and ("restore",) not in d.calls and L.swap_marker(L.lane_paths(root), "steve").is_file(),
          "handoff leaves the game up and the restore owed (swap marker kept)")
    T.enqueue(p, "ITEM_R", SHA[2], "B3", plan("r1"))          # queued while no pilot drives
    check(raises(T.StalePilot, p1.step) is not None, "the handed-off pilot is refused a step (S6)")
    check(raises(T.PilotRefused, p1.reload, {"rule": "R2", "cand": "ITEM_Q@1", "why": "stale"}) is not None,
          "the handed-off pilot is refused a reload (S6)")
    p2 = pilot(root, d, "P2")
    w = p2.wake()
    check(set(w["queued"]) == {"ITEM_H@1", "ITEM_Q@1", "ITEM_R@1"},
          "the fresh pilot reads every queued candidate from disk (before and during the handoff): %s" % w["queued"])
    st = p2.step()
    check(st["decision"]["action"] == "test" and st["decision"]["scenario"] == "s2" and st["result"]["canary_ok"],
          "the fresh pilot tests on the SAME game (canary green, no reload): %s" % (actions([st]),))
    check(d.calls.count(("launch",)) == launches, "no launch at the handoff")
    p2.run_pass(max_steps=20)
    check(raises(T.PilotRefused, pilot(root, d, "P4").wake) is not None, "no wake while P2 is live")
    n = 2
    while T.queued(p) and n < 8:        # one item per pass: each pass ends with a handoff to a fresh pilot
        cur = pilot(root, d, "P%d" % n) if n > 2 else p2
        if n > 2:
            cur.wake()
            cur.run_pass(max_steps=20)
        cur.handoff()
        n += 1
    last = pilot(root, d, "PLAST")
    last.wake()
    last.close()
    sts = T.states(p)
    check(all(sts[c]["state"] in T.TERMINAL for c in ("ITEM_H@1", "ITEM_Q@1", "ITEM_R@1")),
          "every candidate was tested to a verdict: none lost: %s" % {c: sts[c]["state"] for c in sts})
    check(("restore",) in d.calls and not L.swap_marker(L.lane_paths(root), "steve").is_file(),
          "close restores his list")
    every_reload_has_a_rule(root, p, "handoff")


def t_takeover_dead():
    root, p = fresh("takeover")
    d = FakeDriver()
    T.enqueue(p, "ITEM_D", SHA[0], "B1", plan("s1", "s2"))
    p1 = pilot(root, d, "P1")
    p1.wake()
    p1.step()
    s = T.read_session(p, "steve")
    s["in_flight"] = {"cand": "ITEM_D@1", "scenario": "s1", "t": d.t}      # P1 dies mid-test
    T.write_session(p, "steve", s)
    p2 = pilot(root, d, "P2")
    p2.wake(takeover_dead=True)
    e = T.scenario_status(p, T.cand_by_id(p)["ITEM_D@1"])["s1"]
    check(e["status"] == "invalid" and T.states(p)["ITEM_D@1"]["state"] == "queued",
          "a dead pilot's in-flight test is invalid and requeued")
    check(raises(T.StalePilot, p1.step) is not None, "the dead pilot, if it wakes, is refused (S6)")


# ---------------------------------------------------------------- 5. L9a
def t_l9a():
    root, p = fresh("l9a")
    d = FakeDriver()
    fp = {"s2": {"footprint": {"files": ["src/RimMandrake/Bar/Defs/*.xml"]}},
          "s3": {"footprint": {"defs": ["RM_Baz"]}},
          "s1": {"footprint": {"files": ["src/RimMandrake/Slime/Defs/*.xml"]}, "taints": ["s3"]}}
    a = T.enqueue(p, "ITEM_L", SHA[0], "B1", plan("s2", "s3", "s1", **fp), mods=["Slime"],
                  changed_files=["src/RimMandrake/Slime/Defs/a.xml"])
    d.rc["s1"] = 1
    pl = pilot(root, d, "P1")
    pl.wake()
    pl.run_pass()
    check(T.states(p)[a["cand"]].get("verdict") == "fail", "the first attempt fails on s1 (taints s3)")
    b = T.enqueue(p, "ITEM_L", SHA[1], "B1", plan("s2", "s3", "s1", **fp), mods=["Slime"],
                  changed_files=["src/RimMandrake/Slime/Defs/a.xml"])
    pre = T.plan_retest(p, b, write=False)
    check(set(pre["run"]) == {"s1", "s3"} and set(pre["carried"]) == {"s2"},
          "rebuild touching s1's footprint: re-run s1 + taint-named s3, carry s2: %s" % pre)
    d.rc["s1"] = 0
    before = len([c for c in d.calls if c[0] == "scenario"])
    pl.run_pass()
    ran = [c[1] for c in d.calls if c[0] == "scenario"][before:]
    check(sorted(ran) == ["s1", "s3"], "live re-test ran only s1 and s3: %s" % ran)
    car = T.scenario_status(p, b)["s2"]
    check(car["status"] == "carried" and car["source_fingerprint"] == a["fingerprint"],
          "s2 is recorded `carried` with its source fingerprint")
    check(T.states(p)[b["cand"]].get("verdict") == "pass", "the rebuild resolves PASS")
    c2 = dict(b, changed_files=None)
    check(set(T.plan_retest(p, dict(c2, cand="x", fingerprint="zz", parent=a["cand"]), write=False)["run"]) ==
          {"s1", "s2", "s3"}, "unknown changed files: everything re-runs")
    c3 = dict(b, cand="y", fingerprint="yy", parent=a["cand"], changed_files=[T.HARNESS_FILES[0]])
    check(set(T.plan_retest(p, c3, write=False)["run"]) >= {"s2"}, "a harness change re-runs a carried scenario")
    c4 = dict(b, cand="z", fingerprint="ww", parent=a["cand"], changed_files=["src/RimMandrake/Other/x.xml"],
              changed_defs=["RM_Baz"])
    r4 = T.plan_retest(p, c4, write=False)["run"]
    check("s3" in r4 and "s2" not in r4, "a changed def re-runs the scenario naming it: %s" % r4)
    every_reload_has_a_rule(root, p, "l9a")


# ---------------------------------------------------------------- 6. hot-load classes
def t_classes():
    check(T.classify(["src/RimMandrake/X/Source/A.cs"], False, ["X"]) == "cs", "classify .cs -> cs")
    check(T.classify(["src/RimMandrake/X/Defs/A.xml"], False, ["X"]) == "reload", "classify Defs xml -> reload")
    check(T.classify(["design/fixtures/site.json"], False, []) == "live", "classify a fixture -> live")
    check(T.classify(None, False, ["X"]) == "reload", "unknown changes to a mod -> reload, never live")
    check(T.classify([], True, []) == "cs", "has_dll -> cs")
    root, p = fresh("classes")
    why = raises(T.PilotRefused, T.enqueue, p, "ITEM_K", SHA[0], "B", plan("s1"), mods=["X"],
                 changed_files=["src/RimMandrake/X/Defs/A.xml"], fix_class="live")
    check(why and "never lowered" in why, "a declared class may not lower the computed one")
    why = raises(T.PilotRefused, T.enqueue, p, "ITEM_K", SHA[0], "B", plan("s1"), kind="repair", fault="MOD",
                 parent=None)
    check(why is not None, "a repair without a parent is refused")
    T.enqueue(p, "ITEM_K", SHA[0], "B", plan("s1"))
    why = raises(T.PilotRefused, T.enqueue, p, "ITEM_K", SHA[1], "FIX", plan("s1"), kind="repair", fault="MOD",
                 parent="ITEM_K@1")
    check(why and "review" in why, "a MOD repair without its blind diff review is refused (L10)")
    why = raises(T.PilotRefused, T.enqueue, p, "ITEM_K", SHA[1], "B", plan("s1"), profile="full")
    check(why and "minimal" in why, "the full profile is refused")


def t_hotfix():
    root, p = fresh("hotfix")
    d = FakeDriver()
    a = T.enqueue(p, "ITEM_F", SHA[0], "B1", plan("s1", fixture="fixture_f", s1={"taints": []}))
    d.rc["s1"] = 1
    pl = pilot(root, d, "P1")
    pl.wake()
    pl.step()
    pl.step()
    check(T.states(p)[a["cand"]].get("verdict") == "fail", "s1 fails (HARNESS fault)")
    rep = T.enqueue(p, "ITEM_F", SHA[1], "FIX", plan("s1", fixture="fixture_f", s1={"taints": []}), parent=a["cand"],
                    kind="repair", fault="HARNESS", changed_files=["src/RimMandrake/Utils/proofs/proof_f.py"])
    check(rep["class"] == "live", "a proof-script repair is class live")
    d.rc["s1"] = 0
    reloads = len(ev(root, "reload"))
    steps = pl.run_pass()
    acts = actions(steps)
    check(acts[0][0] == "hot_apply" and len(ev(root, "reload")) == reloads,
          "the live-class repair lands on the running game, no reload: %s" % acts)
    recs = [e for e in T.evidence(p) if e["cand"] == rep["cand"] and e["scenario"] == "s1"]
    check(len(recs) == 2 and recs[0]["hotfix"] and not recs[1]["hotfix"],
          "the hot-fixed PASS (rep 1) is repassed clean after a state reset (rep 2)")
    check(("ladder", "reload_save", None) in [(a_, s.get("rung"), None) for a_, s in
                                              [(x["decision"]["action"], x["decision"]) for x in steps]],
          "the state reset is the ladder's fixture reload, not a game reload")
    check(("load_save", "fixture_f") in d.calls and T.states(p)[rep["cand"]].get("verdict") == "pass",
          "the repair resolves PASS only after the clean repass")
    every_reload_has_a_rule(root, p, "hotfix")


def t_ladder():
    root, p = fresh("ladder")
    d = FakeDriver()
    T.enqueue(p, "ITEM_G", SHA[0], "B1", plan("s1", "s2", fixture="fx"))
    pl = pilot(root, d, "P1")
    pl.wake()
    pl.step()
    d.colonists = 0                     # the canary goes red on a live process
    st = pl.step()
    check(st["result"]["status"] == "invalid" and not st["result"]["canary_ok"], "a red canary invalidates the test")
    seq = []
    for _ in range(4):
        r = pl.step(canary_ok=False)
        seq.append((r["decision"]["action"], r["decision"].get("rung") or r["decision"].get("rule")))
        if r["decision"]["action"] == "reload":
            break
    check(seq == [("ladder", "reconnect"), ("ladder", "reload_save"), ("ladder", "restage"), ("reload", "R1")],
          "red canary: reconnect, reload save, restage, and only then R1: %s" % seq)
    d.running = False
    d.colonists = 3
    st = pl.step()
    check(st["decision"]["action"] in ("test", "reload"), "after R1 the pilot goes on: %s" % (actions([st]),))
    every_reload_has_a_rule(root, p, "ladder")


# ---------------------------------------------------------------- blind review round 1 (each a forced failure)
def ran(d):
    return [c[1] for c in d.calls if c[0] == "scenario"]


def t_review1():
    # R1.1: a pilot taken over mid-proof records nothing and does not clear the taker's state
    root, p = fresh("rv_stale")
    d = FakeDriver()
    T.enqueue(p, "ITEM_S", SHA[0], "B1", plan("s1", "s2"))
    p1 = pilot(root, d, "P1")
    p1.wake()
    p1.step()
    p2 = pilot(root, d, "P2")
    d.during["s1"] = lambda: p2.wake(takeover_dead=True)
    why = raises(T.StalePilot, p1.step)
    d.during.pop("s1")
    recs = [e for e in T.evidence(p) if e["scenario"] == "s1"]
    check(why is not None and [e["pilot"] for e in recs] == ["P2"] and recs[0]["status"] == "invalid",
          "a pilot taken over mid-proof is stopped at the poll; only the taker's `invalid` is recorded: %s" % why)
    check(T.read_session(p, "steve")["pilot"] == "P2", "the taker keeps the session")
    # R1.2: a second pilot under the same id cannot wake into a live session
    dup = pilot(root, d, "P2")
    check(raises(T.PilotRefused, dup.wake) is not None, "a same-id wake into a live session is refused")
    # R1.3: a failed bridge release keeps the session live and this pilot's
    d.bridge_release = lambda host: (False, "release boom")
    why = raises(T.PilotRefused, p2.handoff)
    s = T.read_session(p, "steve")
    check(why and "release" in why and s["status"] == "live" and s["pilot"] == "P2",
          "a handoff whose bridge release fails publishes nothing: %s" % why)
    del d.bridge_release

    # R1.4: a candidate with no mods still runs its proofs from its own revision
    root, p = fresh("rv_rev")
    d = FakeDriver()
    d.head[CLONE] = SHA[0]
    T.enqueue(p, "ITEM_R", SHA[2], "B1", plan("s1"))
    pl = pilot(root, d, "P1")
    pl.wake()
    pl.step()
    check(d.head.get(CLONE) == SHA[2], "a no-mods candidate's clone is checked out at its sha before its proofs")
    nc = T.Pilot("steve", FakeDriver(), "PX", clone=None, root=fresh("rv_noclone")[0])
    T.enqueue(nc.p, "ITEM_R", SHA[2], "B1", plan("s1"))
    nc.wake()
    st = raises(T.PilotRefused, nc.step)
    check(st and "clone" in st, "a pilot without a clone is refused its reload: %s" % st)

    # R1.5: the same sha with a changed plan entry is a new test
    root, p = fresh("rv_plan")
    d = FakeDriver()
    a = T.enqueue(p, "ITEM_P", SHA[0], "B1", plan("s1"))
    pl = pilot(root, d, "P1")
    pl.wake()
    pl.run_pass()
    b = T.enqueue(p, "ITEM_P", SHA[0], "B1", plan("s1", s1={"argv": ["python3", "proof2.py", "s1"]}))
    check(a["fingerprint"] == b["fingerprint"] and "s1" in T.scenario_status(p, a)
          and "s1" not in T.scenario_status(p, b), "a changed argv at the same sha does not reuse the old PASS")

    # R1.7: a failed candidate stays open while a fixture reload can restore its blocked scenarios
    root, p = fresh("rv_blocked")
    d = FakeDriver()
    c = T.enqueue(p, "ITEM_B", SHA[0], "B1", plan("s1", "s2", fixture="fx", s1={"taints": ["s2"]}))
    d.rc["s1"] = 1
    pl = pilot(root, d, "P1")
    pl.wake()
    steps = pl.run_pass()
    check(ran(d) == ["s1", "s2"] and ("load_save", "fx") in d.calls and
          T.states(p)[c["cand"]].get("verdict") == "fail",
          "s1 fails and taints s2: fixture reload, s2 still runs, then FAIL: %s" % actions(steps))

    # R1.8: a hot-applied repair never re-runs a scenario it carries
    root, p = fresh("rv_hotcarry")
    d = FakeDriver()
    fp = {"s1": {"footprint": {"files": ["src/RimMandrake/Other/*"]}, "taints": []},
          "s2": {"footprint": {"files": ["src/RimMandrake/Utils/proofs/proof_s2.py"]}, "taints": []}}
    a = T.enqueue(p, "ITEM_H", SHA[0], "B1", plan("s1", "s2", fixture="fx", **fp))
    d.rc["s2"] = 1
    pl = pilot(root, d, "P1")
    pl.wake()
    pl.run_pass()
    rep = T.enqueue(p, "ITEM_H", SHA[1], "FIX", plan("s1", "s2", fixture="fx", **fp), parent=a["cand"],
                    kind="repair", fault="HARNESS", changed_files=["src/RimMandrake/Utils/proofs/proof_s2.py"])
    d.rc["s2"] = 0
    before = len(ran(d))
    pl.run_pass()
    check("s1" not in ran(d)[before:] and T.scenario_status(p, rep)["s1"]["status"] == "carried",
          "the hot-applied repair carries s1 and never runs it: %s" % ran(d)[before:])

    # R1.9: a bare proof file name in argv is part of the footprint
    sc = {"id": "s1", "argv": ["python3", "proof.py", "s1"], "footprint": {"files": ["x/*"]}}
    par = {"mods": [], "profile": "minimal", "tier": None, "has_dll": False}
    why = T.touched(sc, dict(sc), dict(par, changed_files=["src/RimMandrake/Utils/proofs/proof.py"]), par, set())
    check(why and "proof file" in why, "a changed bare-named proof file re-runs its scenario: %s" % why)
    why = T.touched(sc, dict(sc), dict(par, changed_files=["src/RimMandrake/Utils/proofs/other.py"]), par, set())
    check(why is None, "probe: an unrelated file does not")

    # R1.10: a rebuild that carries every scenario resolves without running one
    root, p = fresh("rv_allcarried")
    d = FakeDriver()
    fp = {"s1": {"footprint": {"files": ["src/RimMandrake/Slime/Defs/a*.xml"]}},
          "s2": {"footprint": {"files": ["src/RimMandrake/Slime/Defs/b*.xml"]}}}
    a = T.enqueue(p, "ITEM_C", SHA[0], "B1", plan("s1", "s2", **fp), mods=["Slime"])
    pl = pilot(root, d, "P1")
    pl.wake()
    pl.run_pass()
    b = T.enqueue(p, "ITEM_C", SHA[1], "B1", plan("s1", "s2", **fp), mods=["Slime"],
                  changed_files=["src/RimMandrake/Slime/Defs/zz.xml"])
    before = len(ran(d))
    steps = pl.run_pass()
    check(T.states(p)[b["cand"]].get("verdict") == "pass" and ran(d)[before:] == [],
          "an all-carried rebuild resolves PASS with no test run: %s" % actions(steps))
    every_reload_has_a_rule(root, p, "allcarried")


def t_review2():
    # R2.a: a takeover during a reload wins: the reloading pilot writes no session afterwards
    root, p = fresh("rv2_reload")
    d = FakeDriver()
    T.enqueue(p, "ITEM_T", SHA[0], "B1", plan("s1"))
    p1 = pilot(root, d, "P1")
    p1.wake()
    p2 = pilot(root, d, "P2")
    real = d.launch_and_wait

    def launch_taken():
        p2.wake(takeover_dead=True)
        return real()
    d.launch_and_wait = launch_taken
    why = raises(T.StalePilot, p1.step)
    del d.launch_and_wait
    s = T.read_session(p, "steve")
    check(why is not None and s["pilot"] == "P2" and not s.get("game"),
          "a pilot taken over during its reload records no game in the taker's session: %s" % why)

    # R2.b: a hot-fixed PASS with no fixture to reset to is repassed after an R2 reload, never left stuck
    root, p = fresh("rv2_nofixture")
    d = FakeDriver()
    a = T.enqueue(p, "ITEM_N", SHA[0], "B1", plan("s1", s1={"taints": []}))
    d.rc["s1"] = 1
    pl = pilot(root, d, "P1")
    pl.wake()
    pl.run_pass()
    rep = T.enqueue(p, "ITEM_N", SHA[1], "FIX", plan("s1", s1={"taints": []}), parent=a["cand"], kind="repair",
                    fault="HARNESS", changed_files=["src/RimMandrake/Utils/proofs/proof_n.py"])
    d.rc["s1"] = 0
    steps = pl.run_pass()
    acts = actions(steps)
    check(("reload", "R2", None) in acts and T.states(p)[rep["cand"]].get("verdict") == "pass",
          "no fixture: the failed save reset is followed by an R2 reload and a clean repass: %s" % acts)
    every_reload_has_a_rule(root, p, "nofixture")

    # R2.c: a yield kills the proof's whole process group (a child holding the pipe cannot stall it)
    import time as _t
    drv = T.PilotDriver.__new__(T.PilotDriver)

    def poll():
        raise L.OwnerReturned("owner back")
    t0 = _t.time()
    why = raises(L.OwnerReturned, drv.run_scenario, ["bash", "-c", "sleep 60 & sleep 60"], str(TMP), poll, 0.2)
    check(why is not None and _t.time() - t0 < 15, "the owner yield stops a proof with a child in %.1fs"
          % (_t.time() - t0))


def t_review2b():
    # R2.3: a hot-applied repair supersedes the item's older open attempt (it can never be reloaded back)
    root, p = fresh("rv2_supersede")
    d = FakeDriver()
    a = T.enqueue(p, "ITEM_V", SHA[0], "B1", plan("s1", "s2", fixture="fx", s1={"taints": ["s2"]}))
    d.rc["s1"] = 1
    pl = pilot(root, d, "P1")
    pl.wake()
    pl.step()
    pl.step()
    check(T.states(p)[a["cand"]]["state"] == "testing", "A failed s1 and stays open (s2 restorable)")
    rep = T.enqueue(p, "ITEM_V", SHA[1], "FIX", plan("s1", "s2", fixture="fx", s1={"taints": ["s2"]}),
                    parent=a["cand"], kind="repair", fault="HARNESS",
                    changed_files=["src/RimMandrake/Utils/proofs/proof_v.py"])
    d.rc["s1"] = 0
    st = pl.step()
    check(st["decision"]["action"] == "hot_apply" and T.states(p)[a["cand"]]["state"] == "superseded",
          "the hot-applied repair supersedes A: %s" % (actions([st]),))
    # R2.4: a terminal state is never left (a late requeue cannot resurrect a superseded attempt)
    check(T.set_state(p, a["cand"], "queued", requeued=True) is None and
          T.states(p)[a["cand"]]["state"] == "superseded", "set_state refuses to leave a terminal state")
    # R2.2: a close whose restore fails publishes nothing: the lane stays this pilot's
    real = pl.lane.release

    def boom(**k):
        raise L.RestoreFailed("restore boom")
    pl.lane.release = boom
    why = raises(L.RestoreFailed, pl.close)
    s = T.read_session(p, "steve")
    check(why is not None and s["status"] == "live" and s["pilot"] == "P1",
          "a close whose release fails keeps the session live and this pilot's")
    pl.lane.release = real
    pl.close()
    check(T.read_session(p, "steve")["status"] == "closed", "the retried close publishes `closed`")


def main():
    for t in (t_rule_refused, t_cs_cheap, t_cs_expensive, t_cs_max_delay, t_unmeasured, t_owner_yield, t_handoff,
              t_takeover_dead, t_l9a, t_classes, t_hotfix, t_ladder, t_review1, t_review2, t_review2b):
        try:
            t()
        except Exception as e:  # noqa: BLE001 - a crash in one test is a failure, the others still run
            import traceback
            traceback.print_exc()
            check(False, "%s crashed: %s: %s" % (t.__name__, type(e).__name__, e))
    shutil.rmtree(TMP, ignore_errors=True)
    print("\n%d failure(s)" % len(FAILS))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
