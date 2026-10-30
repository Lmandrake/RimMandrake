#!/usr/bin/env python3
"""Selftest for testpilot.py (harness step 13): the forced-failure proofs of its done-when, offline, on a fake game.

  1. no reload is logged without a rule (a rule-less or unknown-rule reload is refused before anything is written,
     and every `reload` event in every run names a rule and a decision logged before it);
  2. a C# fix forces a logged reload naming its rule and the reload cost used: cheap = a few more tests then R3,
     expensive = drain every valuable test first, either = the maximum acceptance delay; unmeasured = expensive;
  3. (removed 2026-10-30, owner: his return to the machine is no event, so no yield path exists to test);
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
import time
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
        self.during = {}                # scenario id -> callable run inside the proof (before the poll)
        self.out = {}                   # scenario id -> proof output text (default "scenario <id> rc=<rc>")
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
        return self.rc.get(sid, 0), self.out.get(sid, "scenario %s rc=%d" % (sid, self.rc.get(sid, 0)))

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


# ---------------------------------------------------------------- launch failure (indep3 C)
def _ml_setup(name, lane, drv):
    root, p = fresh(name)
    T.enqueue(p, "ITEM_P", SHA[0], "B1", plan("s1"))
    pl = pilot(root, drv, "P1", lane=lane)
    pl.wake()
    return root, p, pl


def _ml_state(root, p, d):
    rel = [c for c in d.calls if c[0] == "release"]
    return (len(rel), sum(1 for c in d.calls if c[0] == "restore"), T.read_session(p, d.lane).get("status"),
            L.swap_marker(L.lane_paths(root), d.lane).is_file())


def t_launch_failures():
    L.Lane.WATCH_POLL_S = 0.05

    class DC(FakeDriver):               # C: the launch fails (no bridge token)
        lane = "steve"

        def launch_and_wait(self):
            self.t += 30
            return False, "[4 launch] no bridge token within 600 s"
    d = DC()
    root, p, pl = _ml_setup("lfC", "steve", d)
    r = None
    try:
        r = pl.step()
    except BaseException as e:  # noqa: BLE001
        check(False, "C: a launch failure escaped Pilot.step: %s" % e)
    rel, rest, status, marker = _ml_state(root, p, d)
    check(rel == 1 and rest >= 1 and not marker and status == "aborted",
          "C: launch failure restores his list, releases the bridge, ends the session (rel=%s restore=%s status=%s "
          "marker=%s)" % (rel, rest, status, marker))
    check(decisions(p, "abort") and any(e["status"] == "invalid" for e in T.evidence(p)),
          "C: the failed step is logged (abort decision, invalid evidence)")
    check(T.states(p)["ITEM_P@1"]["state"] == "queued", "C: the candidate is requeued once")
    n_rel = len([c for c in d.calls if c[0] == "release"])
    pl.abort(RuntimeError("again"), {"cand": "ITEM_P@1"})
    check(len([c for c in d.calls if c[0] == "release"]) == n_rel and len(decisions(p, "abort")) == 1,
          "C: a second abort by the retired pilot acts on nothing")
    pl2 = pilot(root, d, "P2", lane="steve")
    pl2.wake()
    pl2.step()
    check(T.states(p)["ITEM_P@1"]["state"] == "parked", "C: a second launch failure parks the candidate, not a loop")

    # C1b: run_pass stops after an abort (no StalePilot from a further step) and reports the abort
    d = DC()
    root, p, pl = _ml_setup("lfC1b", "steve", d)
    try:
        steps = pl.run_pass()
        ab = steps[-1]["result"]
        check(len(steps) == 1 and T._aborted(ab) and ab.get("id") and "no bridge token" in ab.get("why", ""),
              "C1b: run_pass stops after the abort and returns it with the launch error and decision id")
    except BaseException as e:  # noqa: BLE001
        check(False, "C1b: run_pass kept stepping after an abort: %s: %s" % (type(e).__name__, e))

    # C2: the pass CLI path: an exception out of run_pass still restores and releases
    d = DC()
    root, p, pl = _ml_setup("lfC2", "steve", d)
    pl.step = lambda canary_ok=None: (_ for _ in ()).throw(RuntimeError("boom"))
    try:
        T.run_pass_guarded(pl)
    except RuntimeError:
        pass
    rel, rest, status, marker = _ml_state(root, p, d)
    check(rel == 1 and not marker and status == "aborted", "C2: an exception out of the pass restores and releases "
          "(rel=%s status=%s marker=%s)" % (rel, status, marker))

def t_default_never_consults_owner():
    """Owner 2026-10-30: his return to the machine is no event for testpilot (no probe, no yield, no hold)."""
    src = Path(T.__file__).read_text(encoding="utf-8")
    hits = [w for w in ("owner_returned", "OwnerReturned", "check_owner", "_yield", "owner_t", 'get("hold")', '"action": "hold"')
            if w in src]
    check(not hits, "testpilot.py has no owner-return probe, yield or hold path: %s" % hits)
    knobs = [k for k in json.loads(T.RULE_FILE.read_text(encoding="utf-8")) if "yield" in k.lower()]
    check(not knobs, "the reload rule file has no yield knob (TESTPILOT_FIX_STALE_YIELD_KNOBS): %s" % knobs)
    L.Lane.WATCH_POLL_S = 0.05
    root, p = fresh("noown")

    class D(FakeDriver):
        lane = "archmagi"
        probed = 0

        def owner_returned(self):
            D.probed += 1
            return True

        def launch_and_wait(self):
            time.sleep(0.2)
            return super().launch_and_wait()
    d = D()
    T.enqueue(p, "ITEM_N", SHA[0], "B1", plan("s1"))
    pl = pilot(root, d, "P1", lane="archmagi")
    pl.wake()
    take = [c for c in d.calls if c[0] == "take"]
    check(take and take[-1][2] is False, "the take is a plain take, not --idle-ok")
    r = pl.step()
    check(r["decision"]["action"] == "reload" and pl.step()["decision"]["action"] != "yield",
          "launch and quicktest run, no yield")
    check(D.probed == 0, "owner_returned() was never consulted (%d calls)" % D.probed)


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

    # R2.c: a poll failure kills the proof's whole process group (a child holding the pipe cannot stall it)
    import time as _t
    drv = T.PilotDriver.__new__(T.PilotDriver)

    def poll():
        raise T.StalePilot("taken over")
    t0 = _t.time()
    why = raises(T.StalePilot, drv.run_scenario, ["bash", "-c", "sleep 60 & sleep 60"], str(TMP), poll, 0.2)
    check(why is not None and _t.time() - t0 < 15, "a poll failure stops a proof with a child in %.1fs"
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


# ---------------------------------------------------------------- independent-test defects (2026-10-30)
def t_taint_keeps_fail():
    """TESTPILOT_FIX_TAINT_ERASING_FAIL: a taint note (the `taint` CLI) annotates a FAIL, it never replaces it."""
    root, p = fresh("arena")            # the CLI's own paths: ARENA_ROOT
    d = FakeDriver()
    c = T.enqueue(p, "ITEM_TN", SHA[0], "B1", plan("s1", "s2", "s3", s1={"taints": []}))
    d.rc["s1"] = 1
    pl = pilot(root, d, "P1")
    pl.wake()
    pl.step()
    pl.step()                           # R0, s1 FAILS
    check(T.scenario_status(p, c)["s1"]["status"] == "fail", "taint: s1 fails first")
    rc = T.main(["taint", "--cand", c["cand"], "--scenario", "s1", "--names", "s2"])
    e = T.scenario_status(p, c)["s1"]
    check(rc == 0 and e["status"] == "fail" and e.get("taint") == ["s2"],
          "the taint CLI keeps s1's FAIL and attaches the note: %s %s" % (e["status"], e.get("taint")))
    note = [x for x in T.evidence(p) if x["status"] == "note"]
    check(len(note) == 1 and note[0].get("note_on") == e["ts"],
          "the note names the result it was checked against: %s" % [x.get("note_on") for x in note])
    d.rc["s1"] = 0                      # flaky: it would pass on a re-run
    steps = pl.run_pass()
    check(ran(d).count("s1") == 1 and T.states(p)[c["cand"]].get("verdict") == "fail",
          "the FAIL stands: s1 is not re-run and the candidate resolves FAIL: %s %s"
          % (actions(steps), T.states(p)[c["cand"]]))
    why = raises(SystemExit, T.main, ["taint", "--cand", c["cand"], "--scenario", "s3", "--names", "s2"])
    check(why is not None and T.scenario_status(p, c)["s3"]["status"] == "pass",
          "a taint note on a scenario with no FAIL/invalid result is refused: %s" % why)


def t_canary_blip():
    """TESTPILOT_FIX_CANARY_BLIP_RELOAD: one red pre-canary cured by a reconnect is re-checked, never reloaded (M1)."""
    root, p = fresh("blip")
    d = FakeDriver()
    c = T.enqueue(p, "ITEM_BL", SHA[0], "B1", plan("s1", "s2"))
    pl = pilot(root, d, "P1")
    pl.wake()
    pl.step()                           # R0
    d.t += 1.0
    d.colonists = 0
    st = pl.step()
    check(st["result"]["status"] == "invalid", "blip: the red pre-canary invalidates s1 (not run)")
    d.colonists = 3                     # the blip is over
    steps = pl_run(pl, False)
    acts = actions(steps)
    check(not [a for a in acts if a[0] == "reload"] and d.calls.count(("launch",)) == 1,
          "a canary blip cured by the ladder spends no reload: %s" % acts)
    check(ran(d).count("s1") == 1 and T.states(p)[c["cand"]].get("verdict") == "pass",
          "s1 is re-checked on the same game and the item resolves PASS: %s %s" % (ran(d), T.states(p)[c["cand"]]))
    check(not T.read_session(p, "steve")["game"].get("canary_red"),
          "a re-checked scenario that ran green leaves no red history behind: %s"
          % T.read_session(p, "steve")["game"].get("canary_red"))
    # the red history is the candidate's own: another candidate's stuck s1 does not block this one's s1
    other = T.enqueue(p, "ITEM_BX", SHA[1], "B1", plan("s1"))
    T.add_evidence(p, other, "s1", "invalid", "steve", "P1", t=d.t, why="canary red", taint=None)
    sess = {"game": {"reset_t": 0, "canary_red": {c["cand"] + "|s1": "stuck"}}}
    check(T._pending(p, other, sess) == (["s1"], []),
          "another candidate's stuck canary history does not block this one: %s" % (T._pending(p, other, sess),))
    sess["game"]["canary_red"] = {other["cand"] + "|s1": "stuck"}
    check(T._pending(p, other, sess) == ([], ["s1"]), "its own stuck history does: %s" % (T._pending(p, other, sess),))
    # a canary that stays flapping still ends (no endless re-check loop)
    root, p = fresh("flap")
    d = FakeDriver()
    c = T.enqueue(p, "ITEM_FL", SHA[0], "B1", plan("s1"))
    pl = pilot(root, d, "P1")
    pl.wake()
    pl.step()
    real = d.game_facts
    n = {"k": 0}

    def flap():                         # red at every pre-canary of a test, green at every ladder canary
        f = real()
        n["k"] += 1
        f["ingame_canary"]["ok"] = n["k"] % 2 == 0
        f["live_colonists"] = 3 if n["k"] % 2 == 0 else 0
        return f
    d.game_facts = flap
    steps = []
    can = None
    for _ in range(12):
        r = pl.step(can)
        steps.append(r)
        if r["decision"]["action"] in ("reload", "idle", "yield"):
            break
        res = r.get("result") or {}
        can = res.get("canary_ok") if isinstance(res, dict) else None
    reds = [e for e in T.evidence(p) if e["scenario"] == "s1" and e.get("why") == "canary red"]
    check(len(reds) == 2 and ran(d) == [],
          "a canary red again on the re-check is not re-checked a third time on this game: %d reds, %s"
          % (len(reds), actions(steps)))


def t_ladder_remembers_reloads():
    """TESTPILOT_FIX_LADDER_FORGETS_RELOAD: a canary that stays red (or flaps) reaches a bounded end: a logged park,
    never an endless ladder -> reload -> ladder cycle (M1)."""
    _ladder_bound("ladder_forgets", False)
    _ladder_bound("ladder_flaps", True)


def _ladder_bound(name, flap):
    root, p = fresh(name)
    d = FakeDriver()
    c = T.enqueue(p, "ITEM_LF", SHA[0], "B1", plan("s1", "s2"))
    pl = pilot(root, d, "P1")
    pl.wake()
    pl.step()
    real = d.game_facts
    # each guard is proved alone: the red canary by the reload memory, the flapping one by the rung count
    pl.rule = dict(pl.rule, **({"max_red_reloads": 99} if flap else {"max_red_rungs": 99}))

    n = {"k": 0}

    def red():
        f = real()
        n["k"] += 1
        ok = flap and n["k"] % 2 == 0     # a flapping canary is green on every other probe
        f["ingame_canary"]["ok"] = ok
        f["live_colonists"] = 3 if ok else 0
        return f
    d.game_facts = red
    acts = []
    can = None
    for _ in range(60):
        r = pl.step(can)
        a = r["decision"]["action"]
        acts.append(a)
        if a in ("idle", "yield", "park"):
            break
        res = r.get("result") or {}
        can = False if a in ("ladder", "test", "hot_apply") else None
    check(acts and acts[-1] in ("idle", "park") and acts.count("reload") <= 1,
          "%s: a red canary ends in a bounded way: %s" % (name, acts))
    check(any(x.get("kind") == "park" for x in T._read(p["decisions"])), "the park is a logged decision")
    check(T.states(p)[c["cand"]]["state"] == "parked", "the candidate is parked: %s" % T.states(p)[c["cand"]])


def pl_run(pl, canary_ok, n=20):
    out = []
    for _ in range(n):
        r = pl.step(canary_ok)
        out.append(r)
        if r["decision"]["action"] in ("idle", "yield"):
            break
        res = r.get("result") or {}
        canary_ok = res.get("canary_ok") if isinstance(res, dict) else None
    return out


def t_carried_rebuild():
    """TESTPILOT_CARRIED_REBUILD_WASTES_RELOAD: a rebuild whose every scenario is carried spends no reload."""
    root, p = fresh("carry_noreload")
    d = FakeDriver()
    fp = {"s1": {"footprint": {"files": ["src/RimMandrake/A/Defs/*.xml"]}},
          "s2": {"footprint": {"files": ["src/RimMandrake/B/Defs/*.xml"]}}}
    a = T.enqueue(p, "ITEM_CR", SHA[0], "B1", plan("s1", "s2", **fp), mods=["Slime"],
                  changed_files=["src/RimMandrake/A/Defs/x.xml"])
    pl = pilot(root, d, "P1")
    pl.wake()
    pl.run_pass()
    check(T.states(p)[a["cand"]].get("verdict") == "pass", "carry: attempt 1 passes")
    b = T.enqueue(p, "ITEM_CR", SHA[1], "B1", plan("s1", "s2", **fp), mods=["Slime"],
                  changed_files=["src/RimMandrake/C/Defs/y.xml"])
    n0, r0 = d.calls.count(("launch",)), len(ev(root, "reload"))
    steps = pl_run(pl, None)
    check(d.calls.count(("launch",)) == n0 and len(ev(root, "reload")) == r0 and
          not [x for x in actions(steps) if x[0] == "reload"],
          "an all-carried rebuild launches nothing and logs no reload: %s" % actions(steps))
    check(T.states(p)[b["cand"]].get("verdict") == "pass" and
          {e["status"] for e in T.scenario_status(p, b).values()} == {"carried"},
          "it resolves PASS on carried records alone: %s" % T.states(p)[b["cand"]])
    check(any(x["decision"]["action"] == "carry" for x in steps) and decisions(p, "carry"),
          "the carry is a logged decision")
    # a target superseded after the decision is not carried: nothing is published for it
    e = T.enqueue(p, "ITEM_CR", SHA[2], "B1", plan("s1", "s2", **fp), mods=["Slime"],
                  changed_files=["src/RimMandrake/C/Defs/z.xml"])
    dec = pl.decide()
    T.set_state(p, e["cand"], "superseded", why="test: superseded after the decision")
    why = raises(T.PilotRefused, pl.carry, dec)
    check(dec["action"] == "carry" and why and "superseded" in why and not T.scenario_status(p, e),
          "a carry whose target was superseded after the decision writes nothing: %s %s" % (dec["action"], why))
    # a pilot taken over after the decision publishes nothing either
    f = T.enqueue(p, "ITEM_CR", SHA[3], "B1", plan("s1", "s2", **fp), mods=["Slime"],
                  parent=b["cand"], changed_files=["src/RimMandrake/C/Defs/w.xml"])
    dec = pl.decide()
    pilot(root, d, "P2").wake(takeover_dead=True)
    why = raises(T.StalePilot, pl.carry, dec)
    check(dec["action"] == "carry" and why and not T.scenario_status(p, f),
          "a carry by a taken-over pilot writes nothing: %s %s" % (dec["action"], why))


def t_mutant_guards():
    """TESTPILOT_HARDEN_SELFTEST_MUTANTS: the guards the mutation run showed no check could see."""
    # c2: the reload decision record itself carries the cost it used
    root, p = fresh("m_cost")
    d = FakeDriver()
    T.enqueue(p, "ITEM_MC", SHA[0], "B1", plan("s1"))
    pl = pilot(root, d, "P1")
    pl.wake()
    st = pl.step()
    rec = decisions(p, "reload")
    check(rec and rec[0]["cost"] == st["decision"]["cost"] and
          {"cost_s", "basis", "class", "threshold_s"} <= set(rec[0]["cost"]),
          "the logged reload decision names the cost it used: %s" % (rec[0].get("cost") if rec else None))
    # c5: a same-id pilot superseded by a newer wake (generation) is refused, all else matching
    p2 = pilot(root, d, "P1")
    p2.wake(takeover_dead=True)
    s = T.read_session(p, "steve")
    check(s["pilot"] == pl.id and s["epoch"] == pl.epoch and s["generation"] == pl.gen + 1,
          "probe: only the generation tells the old P1 from the new one")
    why = raises(T.StalePilot, pl.step)
    check(why is not None and "generation" in why, "a stale same-id pilot is refused by its generation: %s" % why)
    # c5: a retired pilot is refused even if the session file still reads it live
    p2.retired = True
    why = raises(T.StalePilot, p2.step)
    check(why is not None and "handed off" in why, "a retired pilot makes no act on a still-live session: %s" % why)
    # c6: a footprint glob alone forces a re-run (the parent PASSED both scenarios)
    root, p = fresh("m_fp")
    d = FakeDriver()
    fp = {"s1": {"footprint": {"files": ["src/RimMandrake/A/Defs/*.xml"]}},
          "s2": {"footprint": {"files": ["src/RimMandrake/B/Defs/*.xml"]}}}
    a = T.enqueue(p, "ITEM_FP", SHA[0], "B1", plan("s1", "s2", **fp), mods=["Slime"])
    pl = pilot(root, d, "P1")
    pl.wake()
    pl.run_pass()
    b = T.enqueue(p, "ITEM_FP", SHA[1], "B1", plan("s1", "s2", **fp), mods=["Slime"],
                  changed_files=["src/RimMandrake/A/Defs/x.xml"])
    pre = T.plan_retest(p, b, write=False)
    check(T.states(p)[a["cand"]].get("verdict") == "pass" and set(pre["run"]) == {"s1"} and
          "footprint" in pre["run"]["s1"] and set(pre["carried"]) == {"s2"},
          "a changed file matching only s1's footprint glob re-runs s1, carries s2: %s" % pre)


def t_abort_scenario():
    """TESTPILOT_FIX_ABORT_WRONG_SCENARIO (independent probe_abort.py case A)."""
    # A: s1 is invalid (rc 7); its re-test fails inside the driver -> the invalid lands on s1, never on unrun s2
    root, p = fresh("ab_scn")
    d = FakeDriver()
    T.enqueue(p, "ITEM_Q", SHA[0], "B1", plan("s1", "s2"))
    pl = pilot(root, d, "P1")
    pl.wake()
    d.rc["s1"] = 7
    pl.step()
    r1 = pl.step()
    check(r1["decision"]["action"] == "test" and r1["result"]["status"] == "invalid", "A: probe: s1 is invalid")
    d.rc["s1"] = 0

    def boom():
        raise RuntimeError("driver lost the proof pipe")
    d.during["s1"] = boom
    r2 = pl.step()
    evs = [(e["scenario"], e["status"], e.get("why") or "") for e in T.evidence(p)]
    check(r2["decision"].get("scenario") == "s1" and T._aborted(r2["result"]), "A: probe: the s1 re-test aborts")
    check([x for x in evs if "proof pipe" in x[2]] == [("s1", "invalid", "RuntimeError: driver lost the proof pipe")]
          and not any(x[0] == "s2" for x in evs),
          "A: the abort's invalid is on the scenario that was running (s1), s2 never ran and has none: %s" % evs)
    # A2: an exception out of the pass with no decision in hand (run_pass_guarded) still records the in-flight test
    root, p = fresh("ab_inflight")
    d = FakeDriver()
    T.enqueue(p, "ITEM_Q2", SHA[0], "B1", plan("s1", "s2"))
    pl = pilot(root, d, "P1")
    pl.wake()
    pl.step()
    pl.step()                           # s1 PASSes; s2 is next

    def kb():
        raise KeyboardInterrupt()
    d.during["s2"] = kb
    try:
        T.run_pass_guarded(pl)
    except KeyboardInterrupt:
        pass
    evs = [(e["scenario"], e["status"]) for e in T.evidence(p)]
    s = T.read_session(p, "steve")
    check(evs == [("s1", "pass"), ("s2", "invalid")] and not s.get("in_flight") and s["status"] == "aborted",
          "A2: a BaseException mid-s2 records s2 invalid from the session's in_flight (no decision passed): %s" % evs)
    # A3: a launch failure (reload decision, no scenario) marks the scenario the next test would run, not a resulted one
    root, p = fresh("ab_launch")

    class DL(FakeDriver):
        fail = False

        def launch_and_wait(self):
            if self.fail:
                self.t += 30
                return False, "[4 launch] no bridge token"
            return super().launch_and_wait()
    d = DL()
    T.enqueue(p, "ITEM_Q3", SHA[0], "B1", plan("s1", "s2"))
    pl = pilot(root, d, "P1")
    pl.wake()
    pl.step()
    d.rc["s1"] = 7
    pl.step()                           # s1 invalid: still valuable, the next test runs s1 again
    d.running, d.fail = False, True
    r = pl.step()
    last = T.evidence(p)[-1]
    check(r["decision"].get("rule") == "R1" and last["scenario"] == "s1" and "LaneRefused" in (last.get("why") or ""),
          "A3: a relaunch failure marks the scenario the next test would run (s1): %s %s"
          % (r["decision"].get("rule"), last["scenario"]))



def t_mutant_guards2():
    """TESTPILOT_HARDEN_SELFTEST_MUTANTS_ROUND2: the guards the independent mutants (indep5 e2..e31) showed unseen."""
    rule = T.load_rule()
    # e2: the cost is the median of the NEWEST load_time_samples rows, not of every row
    root, p = fresh("m2_cost")
    p["load_times"].parent.mkdir(parents=True, exist_ok=True)
    rows = [{"lane": "steve", "ok": True, "profile": "minimal", "tier": None, "launch_to_ready_s": v}
            for v in [900.0] * 6 + [20.0] * 5]
    p["load_times"].write_text("".join(json.dumps(r) + "\n" for r in rows), encoding="utf-8")
    c = T.reload_cost(p, dict(rule, load_time_samples=5), "steve", "minimal", None)
    check(c["cost_s"] == 20.0 and c["class"] == "cheap" and "of 5" in c["basis"],
          "e2: reload cost = median of the newest 5 rows (20 s cheap), old slow rows aged out: %s" % c)
    # e12 / e4 / e28 on one live lane
    root, p = fresh("m2_live")
    d = FakeDriver()
    T.enqueue(p, "ITEM_E", SHA[0], "B1", plan("s1", "s2"))
    pl = pilot(root, d, "P1")
    pl.wake()
    e0 = T.read_session(p, "steve").get("epoch")
    pl.step()
    e1 = T.read_session(p, "steve")["epoch"]
    check(e0 == 0 and e1 == 1 and pl.epoch == 1, "e12: a reload starts a new epoch (0 -> 1): %s -> %s" % (e0, e1))
    d.running = False
    dd = pl.decide()
    check(dd["action"] == "reload" and dd["rule"] == "R1" and "dead" in dd["why"],
          "e4: a dead game process with a queued candidate decides R1: %s %s" % (dd["action"], dd.get("rule")))
    pl.step()
    check(T.read_session(p, "steve")["epoch"] == 2, "e12: the R1 reload starts epoch 2")
    dt = pl.decide()
    T.set_state(p, "ITEM_E@1", "parked", why="test: parked between decision and act")
    n = len(ran(d))
    why = raises(T.PilotRefused, pl.test, dt)
    check(dt["action"] == "test" and why is not None and "changed since the decision" in why and len(ran(d)) == n,
          "e28: a candidate made terminal after the decision is not tested: %s" % why)
    # e27: no reload without the pilot's own clone
    root, p = fresh("m2_clone")
    d = FakeDriver()
    T.enqueue(p, "ITEM_C", SHA[0], "B1", plan("s1"))
    pl = T.Pilot("steve", d, "P1", clone=None, root=root)
    pl.wake()
    why = raises(T.PilotRefused, pl.step)
    check(why is not None and "own clone" in why and not [c for c in d.calls if c[0] == "launch"],
          "e27: a pilot with no clone refuses the reload before launching: %s" % why)
    # e13 + e7: a game that dies mid-scenario is a crash; max_item_crashes crashes quarantine the item
    root, p = fresh("m2_crash")
    d = FakeDriver()
    T.enqueue(p, "ITEM_K", SHA[0], "B1", plan("s1"))
    pl = pilot(root, d, "P1")
    pl.rule = dict(pl.rule, max_item_crashes=1)
    pl.wake()
    pl.step()

    def die():
        d.running = False
    d.during["s1"] = die
    pl.step()
    e = T.evidence(p)[-1]
    check(e["status"] == "invalid" and e.get("crash") is True, "e13: a game death mid-scenario is a crash: %s" % e.get("crash"))
    check(T.states(p)["ITEM_K@1"]["state"] == "quarantined", "e7: max_item_crashes crashes quarantine the candidate: %s"
          % T.states(p)["ITEM_K@1"]["state"])
    # e14: rc == fail_rc with a non-assertion traceback is an invalid crash-of-the-proof, not a FAIL
    root, p = fresh("m2_tb")
    d = FakeDriver()
    T.enqueue(p, "ITEM_TB", SHA[0], "B1", plan("s1"))
    pl = pilot(root, d, "P1")
    pl.wake()
    pl.step()
    d.rc["s1"] = 1
    d.out["s1"] = "Traceback (most recent call last):\n  File \"proof.py\", line 3\nKeyError: 'x'\n"
    r = pl.step()
    check(r["result"]["status"] == "invalid" and "traceback" in (T.evidence(p)[-1].get("why") or ""),
          "e14: a proof that died on a traceback is invalid, not judged FAIL: %s" % r["result"]["status"])
    # e6: max_live_fails failed candidates of one item park it (L10)
    root, p = fresh("m2_lf")
    d = FakeDriver()
    d.rc["s1"] = 1
    T.enqueue(p, "ITEM_LF", SHA[0], "B1", plan("s1"))
    pl = pilot(root, d, "P1")
    pl.rule = dict(pl.rule, max_live_fails=2)
    pl.wake()
    pl.run_pass()
    s1 = T.states(p)["ITEM_LF@1"]
    T.enqueue(p, "ITEM_LF", SHA[1], "B1", plan("s1"))
    pl.run_pass()
    s2 = T.states(p)["ITEM_LF@2"]
    check(s1.get("verdict") == "fail" and s2["state"] == "parked" and "L10" in (s2.get("why") or ""),
          "e6: the first FAIL resolves, the max_live_fails-th parks the item: %s / %s" % (s1, s2.get("state")))
    # e16: a newer attempt supersedes an older queued one
    root, p = fresh("m2_sup")
    a = T.enqueue(p, "ITEM_S", SHA[0], "B1", plan("s1"))
    b = T.enqueue(p, "ITEM_S", SHA[1], "B1", plan("s1"))
    st = T.states(p)
    check(st[a["cand"]]["state"] == "superseded" and st[a["cand"]].get("by") == b["cand"]
          and st[b["cand"]]["state"] == "queued", "e16: enqueue supersedes the older queued attempt")
    # e20 e22 e23 e31: touched() carry guards, each in isolation (a footprint that matches nothing otherwise)
    scn = {"id": "s1", "argv": ["python3", "proof.py", "s1"], "footprint": {"files": ["nomatch/*.xml"],
                                                                         "defs": ["RM_Foot"]}}
    par = {"mods": ["A"], "profile": "minimal", "tier": None, "has_dll": False, "changed_files": [],
           "changed_defs": []}
    base = dict(par, changed_files=["src/RimMandrake/Other/x.xml"])
    check(T.touched(scn, scn, base, par, set()) is None, "touched probe: an unrelated change carries")
    for k, v in (("mods", ["B"]), ("profile", "minimal_deps"), ("tier", "slime"), ("has_dll", True)):
        w = T.touched(scn, scn, dict(base, **{k: v}), par, set())
        check(w == "%s changed" % k, "e20: a %s change re-runs: %s" % (k, w))
    w = T.touched(scn, scn, dict(base, changed_defs=["RM_Foot"]), par, set())
    check(w is not None and "changed def RM_Foot" in w, "e22: a changed def in the footprint re-runs: %s" % w)
    bare = {"id": "s1", "argv": ["python3", "proof.py", "s1"]}
    w = T.touched(bare, bare, base, par, set())
    check(w == "no declared footprint", "e23: no declared footprint re-runs: %s" % w)
    w = T.touched(scn, scn, base, par, "uncertain")
    check(w is not None and "uncertain" in w, "e31: an uncertain parent taint re-runs: %s" % w)
    # e26: hot-apply only onto the same mod set
    game = {"cand": "X@1", "profile": "minimal", "tier": None, "mods": ["A"]}
    byid = {"X@1": {"cand": "X@1", "mods": ["A"]}}
    live = {"class": "live", "profile": "minimal", "tier": None, "mods": ["A"], "parent": "X@1"}
    check(T.hot_appliable(live, game, byid) and not T.hot_appliable(dict(live, mods=["A", "B"]), game, byid)
          and not T.hot_appliable(dict(live, parent="Y@1"), game, byid),
          "e26: a live candidate hot-applies only onto its parent's loaded mod set")
    # e29: a hot-fixed parent PASS is never carried
    root, p = fresh("m2_hfc")
    fp = {"s1": {"footprint": {"files": ["nomatch/*.xml"]}}}
    a = T.enqueue(p, "ITEM_HC", SHA[0], "B1", plan("s1", **fp))
    T.add_evidence(p, a, "s1", "pass", "steve", "P1", hotfix=True)
    b = T.enqueue(p, "ITEM_HC", SHA[1], "B1", plan("s1", **fp), parent=a["cand"], changed_files=[])
    pre = T.plan_retest(p, b, write=False)
    check("s1" in pre["run"] and "clean PASS" in pre["run"]["s1"] and not pre["carried"],
          "e29: a hot-fixed parent PASS re-runs, it is not carried: %s" % pre)
    # e30: a rule file missing a required key is refused
    bad = {k: v for k, v in json.loads(T.RULE_FILE.read_text(encoding="utf-8")).items() if k != "ladder"}
    rp = TMP / "bad_rule.json"
    rp.write_text(json.dumps(bad), encoding="utf-8")
    why = raises(T.PilotRefused, T.load_rule, rp)
    check(why is not None and "'ladder'" in why, "e30: a reload rule file with no 'ladder' is refused: %s" % why)


def t_proof_timeout():
    """A proof past its limit is a logged, non-crash result; the pass survives (was: TimeoutError aborted it)."""
    root, p = fresh("proof_timeout")
    d = FakeDriver()
    c = T.enqueue(p, "ITEM_TO", SHA[0], "B1", plan("s1", "s2"))
    pl = pilot(root, d, "P1")
    pl.wake()
    pl.step()

    def hang():
        raise TimeoutError("scenario over 1800 s")
    d.during["s1"] = hang
    r = pl.step()
    s = T.read_session(p, "steve")
    ev = [e for e in T.evidence(p) if e["scenario"] == "s1"]
    check(r["decision"]["action"] == "test" and (r["result"] or {}).get("status") == "invalid",
          "the timeout step returns a recorded invalid result, not a raise: %r" % (r,))
    check(len(ev) == 1 and ev[0]["status"] == "invalid" and "timed out" in (ev[0].get("why") or ""),
          "one evidence record says the proof timed out: %r" % ev)
    check(not ev[0].get("crash"), "a timeout is not a pilot crash (no M5 quarantine count)")
    check(s["status"] == "live" and s["pilot"] == "P1" and not s.get("in_flight"),
          "session still P1's and in_flight is cleared: %r" % s.get("in_flight"))
    d.during.clear()
    r = pl.step()
    check((r["result"] or {}).get("status") in ("pass", "invalid") and r["decision"]["action"] != "idle",
          "the pass goes on after the timeout: %r" % r["decision"])
    # the real driver: past its limit it raises TimeoutError and kills the group
    import time as _t
    drv = T.PilotDriver.__new__(T.PilotDriver)
    drv.LIMIT_S = 0.5
    t0 = _t.time()
    why = raises(TimeoutError, drv.run_scenario, ["bash", "-c", "sleep 60 & wait"], str(TMP), lambda: None, 0.1)
    check(why is not None and _t.time() - t0 < 8, "the real driver times out and returns promptly")


def t_killpg():
    """c4: a poll failure (S6 takeover) kills the proof's whole process group, grandchildren included (real PilotDriver)."""
    import time as _t
    drv = T.PilotDriver.__new__(T.PilotDriver)
    pidf = TMP / "grandchild.pid"

    def poll():
        if pidf.is_file() and pidf.read_text().strip():
            raise T.StalePilot("taken over")
    t0 = _t.time()
    why = raises(T.StalePilot, drv.run_scenario, ["bash", "-c", "sleep 60 & echo $! > %s; wait" % pidf],
                 str(TMP), poll, 0.2)
    dt = _t.time() - t0
    gpid = int(pidf.read_text().strip())
    for _ in range(50):                 # SIGKILL is async: give the kernel a moment to reap
        try:
            stat = Path("/proc/%d/stat" % gpid).read_text()
        except OSError:
            stat = ""
        if not stat or stat.split(") ", 1)[1][:1] in ("Z", "X"):
            break
        _t.sleep(0.1)
    check(why is not None and dt < 5 and (not stat or stat.split(") ", 1)[1][:1] in ("Z", "X")),
          "a poll failure kills the proof's grandchild too, in %.1fs (state %r)"
          % (dt, stat.split(") ", 1)[1][:1] if stat else "gone"))
    if stat and stat.split(") ", 1)[1][:1] not in ("Z", "X"):
        os.kill(gpid, 9)


def _die(d):
    def f():
        d.running = False
    return f


def t_checkout_refusal():
    """TESTPILOT_FIX_CHECKOUT_REFUSAL_LOOPS: a checkout that fails after the reload decision is an act failure: the
    candidate is requeued once then parked, never re-decided forever (indep6 probe_defects case 1)."""
    root, p = fresh("co_loop")
    d = FakeDriver()
    d.checkout = lambda clone, sha: (False, "fatal: reference is not a tree")
    T.enqueue(p, "ITEM_CO", SHA[0], "B1", plan("s1"))
    seen = []
    for i in range(4):
        pl = pilot(root, d, "P%d" % i)
        pl.wake()
        try:
            T.run_pass_guarded(pl, 5)
            err = None
            if not pl.retired:
                pl.handoff("test: pass end")
        except Exception as e:  # noqa: BLE001
            err = "%s: %s" % (type(e).__name__, e)
        seen.append((T.states(p)["ITEM_CO@1"]["state"], len(decisions(p, "reload")), err))
    check(seen[0][0] == "queued" and T._requeues(p, "ITEM_CO@1") >= 1 and seen[0][2] is None,
          "checkout: the first failure requeues the candidate inside the pass (no escape): %s" % seen[0:1])
    check(seen[1][0] == "parked", "checkout: the second failure parks it: %s" % seen)
    check(seen[2][1] == seen[1][1] == seen[3][1] == 2,
          "checkout: no reload is decided for it once parked (2 reload decisions, not one per pass): %s" % seen)
    check(len(decisions(p, "abort")) == 2 and any("checkout" in (e.get("why") or "") for e in T.evidence(p)),
          "checkout: each failure is a logged abort with invalid evidence naming the checkout")
    s = T.read_session(p, "steve")
    check(s["status"] == "aborted" or s["status"] in ("handoff", "closed"), "checkout: the session ended: %s"
          % s["status"])


def t_quarantine_item():
    """TESTPILOT_FIX_QUARANTINE_SPARES_SIBLING: a quarantine (2 crashes) and the 3-live-fail park cover the whole
    item (M5, L10): its other open candidates close with it and are never tested."""
    root, p = fresh("qq_item")
    d = FakeDriver()
    a = T.enqueue(p, "ITEM_QQ", SHA[0], "B1", plan("s1", "s2"))
    pl = pilot(root, d, "Q1")
    pl.wake()
    pl.step()
    d.during["s1"] = _die(d)
    pl.step()                                       # crash 1 on @1 (testing)
    b = T.enqueue(p, "ITEM_QQ", SHA[1], "FIX", plan("s1", "s2"), kind="repair", fault="SITE", parent=a["cand"])
    for _ in range(6):
        if pl.retired:
            break
        r = pl.step()
        if r["decision"]["action"] == "idle":
            break
    st = {k: v["state"] for k, v in T.states(p).items()}
    runs = [c for c in d.calls if c[0] == "scenario"]
    check(st == {a["cand"]: "quarantined", b["cand"]: "quarantined"} and T.item_parked(p, "ITEM_QQ"),
          "quarantine: the second crash quarantines the item, its open sibling %s too: %s" % (b["cand"], st))
    check(runs == [("scenario", "s1"), ("scenario", "s1")], "quarantine: the sibling is never tested: %s" % runs)
    # the 3-live-fail park (L10): the third failing candidate parks the item and its open sibling
    root, p = fresh("lf_item")
    d = FakeDriver()
    d.rc["s1"] = 1
    pl = pilot(root, d, "L1")
    pl.wake()
    for i in range(2):
        T.enqueue(p, "ITEM_LF3", SHA[i], "B1", plan("s1", s1={"taints": []}))
        pl.run_pass()
    c3 = T.enqueue(p, "ITEM_LF3", SHA[2], "B1", plan("s0", "s1", s1={"taints": []}))
    pl.step()                                       # @3 hot-applies (live, same mods): s0 passes, @3 testing
    c4 = T.enqueue(p, "ITEM_LF3", SHA[3], "B1", plan("s0", "s1", s1={"taints": []}), changed_files=None)
    r = pl.step()                                   # @3's s1 fails: the third failing candidate
    st = T.states(p)
    check(r["decision"].get("cand") == c3["cand"] and st[c3["cand"]]["state"] == "parked" and
          st[c4["cand"]]["state"] == "parked" and T.item_parked(p, "ITEM_LF3"),
          "live-fail park: the third failure parks the item and its open sibling %s: %s"
          % (c4["cand"], {k: v["state"] for k, v in st.items()}))
    n = len([c for c in d.calls if c[0] == "scenario"])
    pl.run_pass()
    check(len([c for c in d.calls if c[0] == "scenario"]) == n, "live-fail park: the parked sibling is never tested")


def t_mutant_guards3():
    """TESTPILOT_HARDEN_SELFTEST_MUTANTS_ROUND3: the guards the indep6 mutants (n1-n5, n7-n10, n12, n17, n18) showed
    unseen."""
    ex = {"s1": {"taints": []}}
    # n1: the abort's invalid goes on the in-flight scenario (s2), not the first pending one (s1)
    root, p = fresh("m3_inflight")
    d = FakeDriver()
    c = T.enqueue(p, "ITEM_N1", SHA[0], "B1", plan("s1", "s2", **ex))
    pl = pilot(root, d, "P1")
    pl.wake()
    pl.step()

    def kb():
        raise KeyboardInterrupt()
    d.during["s2"] = kb
    try:
        pl.test({"action": "test", "cand": c["cand"], "scenario": "s2", "why": "test: s2 first"})
    except KeyboardInterrupt as e:
        pl.abort(e)
    evs = [(e["scenario"], e["status"]) for e in T.evidence(p)]
    check(evs == [("s2", "invalid")], "n1: an abort with no decision marks the in-flight s2, not pending s1: %s" % evs)
    # n5: a stale pilot's abort never reads the live pilot's in_flight
    root, p = fresh("m3_stale")
    d = FakeDriver()
    c = T.enqueue(p, "ITEM_N5", SHA[0], "B1", plan("s1", "s2"))
    p1 = pilot(root, d, "P1")
    p1.wake()
    p1.step()
    p2 = pilot(root, d, "P2")
    p2.wake(takeover_dead=True)
    d.during["s1"] = lambda: p1.abort(RuntimeError("stale pilot failed"))
    p2.step()
    evs = [(e["scenario"], e["status"], e["pilot"]) for e in T.evidence(p)]
    check(evs == [("s1", "pass", "P2")] and T._requeues(p, c["cand"]) == 0,
          "n5: the stale P1's abort records nothing on P2's in-flight test: %s" % evs)
    # n2: a failure after the act recorded its result does not re-mark that result invalid
    root, p = fresh("m3_after")
    d = FakeDriver()
    c = T.enqueue(p, "ITEM_N2", SHA[0], "B1", plan("s1", "s2"))
    pl = pilot(root, d, "P1")
    pl.wake()
    pl.step()

    def bad_resolve(*a, **k):
        raise RuntimeError("resolve failed after the evidence")
    pl._resolve = bad_resolve
    r = pl.step()
    evs = [(e["scenario"], e["status"]) for e in T.evidence(p)]
    check(T._aborted(r["result"]) and evs == [("s1", "pass")],
          "n2: an act failing after its PASS was recorded leaves that PASS alone: %s" % evs)
    # n3: a relaunch failure marks the FIRST pending scenario (s1), not the last (s2)
    root, p = fresh("m3_first")

    class DL(FakeDriver):
        fail = False

        def launch_and_wait(self):
            if self.fail:
                self.t += 30
                return False, "[4 launch] no bridge token"
            return super().launch_and_wait()
    d = DL()
    c = T.enqueue(p, "ITEM_N3", SHA[0], "B1", plan("s1", "s2", **ex))
    pl = pilot(root, d, "P1")
    pl.wake()
    pl.step()
    d.rc["s1"] = 7
    pl.step()
    v, _b = T._pending(p, c, T.read_session(p, "steve"))
    d.running, d.fail = False, True
    pl.step()
    check(v == ["s1", "s2"] and T.evidence(p)[-1]["scenario"] == "s1",
          "n3: with s1 and s2 both pending a relaunch failure marks s1: %s -> %s" % (v, T.evidence(p)[-1]["scenario"]))
    # n4: an act failure is not a crash: one abort plus one game death does not quarantine
    root, p = fresh("m3_abortcrash")
    d = FakeDriver()
    c = T.enqueue(p, "ITEM_N4", SHA[0], "B1", plan("s1", "s2", **ex))
    pl = pilot(root, d, "P1")
    pl.wake()
    pl.step()

    def boom():
        raise RuntimeError("driver lost the proof pipe")
    d.during["s1"] = boom
    pl.step()
    pl = pilot(root, d, "P2")
    pl.wake()
    d.during["s1"] = _die(d)
    for _ in range(3):
        r = pl.step()
        if r["decision"]["action"] == "test":
            break
    crashes = [e for e in T.evidence(p) if e.get("crash")]
    check(len(crashes) == 1 and T.states(p)[c["cand"]]["state"] != "quarantined" and not T.item_parked(p, "ITEM_N4"),
          "n4: an abort is no crash: one game death after it does not quarantine (%d crash records, %s)"
          % (len(crashes), T.states(p)[c["cand"]]["state"]))
    # n7 + n9: a dead pilot's interrupted test is a crash; with one game death that is 2: the item is quarantined
    # and parked (a new attempt is refused)
    root, p = fresh("m3_deadcrash")
    d = FakeDriver()
    c = T.enqueue(p, "ITEM_N7", SHA[0], "B1", plan("s1", "s2", **ex))
    p1 = pilot(root, d, "P1")
    p1.wake()
    p1.step()
    s = T.read_session(p, "steve")
    s["in_flight"] = {"cand": c["cand"], "scenario": "s1", "t": d.t}
    T.write_session(p, "steve", s)
    p2 = pilot(root, d, "P2")
    p2.wake(takeover_dead=True)
    d.during["s1"] = _die(d)
    r = p2.step()
    check(r["decision"]["action"] == "test" and T.states(p)[c["cand"]]["state"] == "quarantined",
          "n7: a dead pilot's interrupted test counts as a crash: one game death after it quarantines: %s"
          % T.states(p)[c["cand"]]["state"])
    check(T.item_parked(p, "ITEM_N7") and raises(T.PilotRefused, T.enqueue, p, "ITEM_N7", SHA[1], "B1", plan("s1")),
          "n9: the quarantine parks the item: a new attempt is refused")
    # f5: two dead-pilot interruptions are two crashes: the second quarantines the item at the takeover, before any
    # run (not merely parks the attempt on its requeue budget)
    root, p = fresh("m3_twodead")
    d = FakeDriver()
    c = T.enqueue(p, "ITEM_F5", SHA[0], "B1", plan("s1", **ex))
    p1 = pilot(root, d, "P1")
    p1.wake()
    p1.step()
    for nxt in ("P2", "P3"):
        s = T.read_session(p, "steve")
        s["in_flight"] = {"cand": c["cand"], "scenario": "s1", "t": d.t}
        T.write_session(p, "steve", s)
        pilot(root, d, nxt).wake(takeover_dead=True)
    crashes = [e for e in T.evidence(p) if e.get("crash")]
    check(len(crashes) == 2 and T.states(p)[c["cand"]]["state"] == "quarantined" and T.item_parked(p, "ITEM_F5"),
          "f5: two dead-pilot interruptions quarantine the item at the takeover (%d crashes, %s)"
          % (len(crashes), T.states(p)[c["cand"]]["state"]))
    # n8: crashes count per item, across its attempts
    root, p = fresh("m3_peritem")
    d = FakeDriver()
    a = T.enqueue(p, "ITEM_N8", SHA[0], "B1", plan("s1", "s2", **ex))
    pl = pilot(root, d, "P1")
    pl.wake()
    pl.step()
    d.during["s1"] = _die(d)
    pl.step()                                       # crash 1, on @1
    b = T.enqueue(p, "ITEM_N8", SHA[1], "B1", plan("s1", "s2", **ex))
    T.set_state(p, a["cand"], "superseded", by=b["cand"], why="test: a newer attempt")
    for _ in range(3):
        r = pl.step()
        if r["decision"]["action"] == "test":
            break
    check(r["decision"].get("cand") == b["cand"] and T.states(p)[b["cand"]]["state"] == "quarantined",
          "n8: one crash on @1 and one on @2 quarantine the item (crashes count per item): %s"
          % T.states(p)[b["cand"]]["state"])
    # n10: a park resets the canary rung counters
    root, p = fresh("m3_park")
    d = FakeDriver()
    T.enqueue(p, "ITEM_N10", SHA[0], "B1", plan("s1"))
    pl = pilot(root, d, "P1")
    pl.wake()
    pl.step()
    s = T.read_session(p, "steve")
    s["red_rungs"], s["red_reloads"], s["ladder_tried"] = 6, 1, ["reconnect"]
    T.write_session(p, "steve", s)
    pl.park({"cand": None, "why": "test: canary flapping"})
    s = T.read_session(p, "steve")
    check((s["red_rungs"], s["red_reloads"], s["ladder_tried"]) == (0, 0, []),
          "n10: a park resets red_rungs, red_reloads and the tried ladder: %s"
          % ((s["red_rungs"], s["red_reloads"], s["ladder_tried"]),))
    # n12: a carry supersedes the item's older open attempts
    root, p = fresh("m3_carry")
    d = FakeDriver()
    fp = {"s1": {"footprint": {"files": ["src/RimMandrake/A/Defs/*.xml"]}, "taints": []},
          "s2": {"footprint": {"files": ["src/RimMandrake/B/Defs/*.xml"]}}}
    a = T.enqueue(p, "ITEM_N12", SHA[0], "B1", plan("s1", "s2", **fp), mods=["Slime"], changed_files=[])
    pl = pilot(root, d, "P1")
    pl.wake()
    pl.run_pass()
    b = T.enqueue(p, "ITEM_N12", SHA[1], "B1", plan("s1", "s2", **fp), mods=["Slime"], parent=a["cand"],
                  changed_files=["src/RimMandrake/A/Defs/x.xml"])
    d.rc["s1"] = 7
    pl.step()                                       # reload @2
    pl.step()                                       # @2's s1 invalid: @2 testing
    c = T.enqueue(p, "ITEM_N12", SHA[2], "B1", plan("s1", "s2", **fp), mods=["Slime"], parent=a["cand"],
                  changed_files=["src/RimMandrake/C/Defs/y.xml"])
    pre = T.states(p)[b["cand"]]["state"]
    r = pl.step()
    st = T.states(p)
    check(pre == "testing" and r["decision"]["action"] == "carry" and st[c["cand"]].get("verdict") == "pass" and
          st[b["cand"]]["state"] == "superseded",
          "n12: the carried @3 resolves and supersedes the older open @2: %s %s %s"
          % (pre, r["decision"]["action"], st[b["cand"]]["state"]))
    # n17: a live-class repair for another profile is not hot-applied: it waits for a reload
    root, p = fresh("m3_profile")
    d = FakeDriver()
    a = T.enqueue(p, "ITEM_N17", SHA[0], "B1", plan("s1", s1={"taints": []}))
    d.rc["s1"] = 1
    pl = pilot(root, d, "P1")
    pl.wake()
    pl.step()
    pl.step()
    rep = T.enqueue(p, "ITEM_N17", SHA[1], "FIX", plan("s1", s1={"taints": []}), parent=a["cand"], kind="repair",
                    fault="HARNESS", changed_files=["src/RimMandrake/Utils/proofs/proof_f.py"],
                    profile="minimal+deps")
    dec = pl.decide()
    check(rep["class"] == "live" and dec["action"] == "reload" and dec["cand"] == rep["cand"],
          "n17: a live repair on another profile reloads, it is not hot-applied: %s" % dec["action"])
    # n18: a MOD repair hot-applied is no hot-fix: its PASS counts at once (no state-reset repass)
    root, p = fresh("m3_modhot")
    d = FakeDriver()
    a = T.enqueue(p, "ITEM_N18", SHA[0], "B1", plan("s1", fixture="fixture_m", s1={"taints": []}))
    d.rc["s1"] = 1
    pl = pilot(root, d, "P1")
    pl.wake()
    pl.step()
    pl.step()
    rep = T.enqueue(p, "ITEM_N18", SHA[1], "FIX", plan("s1", fixture="fixture_m", s1={"taints": []}),
                    parent=a["cand"], kind="repair", fault="MOD", review="reviews/n18.md",
                    changed_files=["src/RimMandrake/Utils/proofs/proof_m.py"])
    d.rc["s1"] = 0
    r = pl.step()
    recs = [e for e in T.evidence(p) if e["cand"] == rep["cand"]]
    check(r["decision"]["action"] == "hot_apply" and len(recs) == 1 and not recs[0].get("hotfix") and
          T.states(p)[rep["cand"]].get("verdict") == "pass",
          "n18: a hot-applied MOD repair's PASS is no hot-fix and resolves it: %s %s"
          % ([e.get("hotfix") for e in recs], T.states(p)[rep["cand"]].get("state")))


def main():
    for t in (t_rule_refused, t_cs_cheap, t_cs_expensive, t_cs_max_delay, t_unmeasured, t_handoff,
              t_takeover_dead, t_l9a, t_classes, t_hotfix, t_ladder, t_review1, t_review2, t_review2b,
              t_taint_keeps_fail, t_canary_blip, t_ladder_remembers_reloads, t_carried_rebuild, t_mutant_guards, t_killpg, t_proof_timeout, t_launch_failures, t_default_never_consults_owner,
              t_abort_scenario, t_mutant_guards2, t_checkout_refusal, t_quarantine_item, t_mutant_guards3):
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
