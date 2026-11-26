#!/usr/bin/env python3
"""selftest_one_live_run_per_mod: the promises of design/specs/2026-11-23-one-live-run-per-mod/boundary.md, one test per
promise, each named as the promise is. Dispatch launched a second run on ExplosiveKnockback while its holder was live,
and the second lease fenced the first (2026-11-23 12:07 PM PST; item
RIMMANDRAKE_REFUSE_SECOND_HOLDER_WHILE_FIRST_LIVES_FENCED_AGAIN). The ticks here are real (MD.tick), the runs are placed
by the real maturation_now.runs_for_mods from the env each launch recorded, and the leases are real ledger grants in a
temp root. No game, no network, no real unit."""
import json
import os
import shutil
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "Utils"))
TMP = tempfile.mkdtemp(prefix="one_live_run_")
os.environ["RM_DISPATCHER_STATE"] = os.path.join(TMP, "_dispatcher")
os.environ["RM_MATURATION_DISPATCH_DIR"] = os.path.join(TMP, "state")
os.environ["RM_RUN_VOIDS_FILE"] = os.path.join(TMP, "state", "voids.jsonl")
os.environ["MATURATION_BRIEF_DIR"] = os.path.join(TMP, "briefs")
os.environ["RM_OWNER_HOLD_FILE"] = os.path.join(TMP, "mod_owner_hold.json")
os.environ["RM_CONTROL_DB"] = os.path.join(TMP, "control", "control.db")
os.environ.pop("RM_MODLEDGER_WRITER", None)
for _d in ("_dispatcher", "state", "briefs", "control"):
    os.makedirs(os.path.join(TMP, _d))
import control                      # noqa: E402
import maturation as M              # noqa: E402
import maturation_autonomy as AUT   # noqa: E402
import maturation_dispatch as MD    # noqa: E402
import maturation_now as MN         # noqa: E402
import modledger as ML              # noqa: E402

control.init()                      # an empty control store: no hold, no switch, no count adjusted

MOD = "ExplosiveKnockback"
NOW = 1795464297.0
CFG = {"enabled": True, "advancing": [MOD], "cap_tokens": 3_750_000, "max_live": 4, "settle_s": 180, "blind_enabled": True,
       "blind_cap_tokens": 5_000_000, "blind_auto_cycles_per_visit": 3, "ingame_enabled": True, "ingame_cap_tokens": 7_500_000,
       "ingame_auto_runs_per_visit": 1, "steward_cap_tokens": 1_250_000, "fix_cap_tokens": 2_500_000, "steward_model": "opus", "launch_tries": 3,
       "stalled_min": 10, "seat": "BENCH", "model": "opus"}
STEWARD = "RIMMANDRAKE_ROUTE_EXPLOSIVEKNOCKBACK_VISIT_FOUR_FAILURES_BACK"
# the two real items: neither id names the mod, and the holder's title says EK
CARRIER = "RIMMANDRAKE_HOLD_SPARED_CARRIER_IN_BLAST_IT_WALKED_AWAY"
FRAMES = "RIMMANDRAKE_RUN_KNOCKBACK_WALK_FRAME_ARMS_SMALL_COLONY_ABSENT"
TITLES = {CARRIER: "EK visit 4, sc_spared read FAIL once", FRAMES: "EK 0.1.0 visit 4, sc_walk_raid: FRAME_BUDGET"}


class Patch:
    def __init__(self, *trips):
        self.trips, self.old = trips, []

    def __enter__(self):
        for obj, name, val in self.trips:
            self.old.append((obj, name, getattr(obj, name)))
            setattr(obj, name, val)

    def __exit__(self, *a):
        for obj, name, val in reversed(self.old):
            setattr(obj, name, val)


class World:
    """One mod at in_game with an open road back; every launch writes a run record, as detached_helper does."""

    stage = "in_game"

    def __init__(self, strip=False):
        self.root = tempfile.mkdtemp(prefix="root_", dir=TMP)
        os.makedirs(os.path.join(self.root, "design", "concepts", MOD, "ledger"))
        ML.append(self.root, MOD, "DISPATCH", "version.open", "version", body={"version": "0.1.0"}, version="0.1.0")
        self.recs, self.launched, self.strip = {}, [], strip
        self.unreadable, self.no_status, self.gone = set(), set(), set()
        self.open = [{"id": CARRIER, "needs": "offline"}, {"id": FRAMES, "needs": "offline"}]
        self.blind_records = False
        d = os.environ["RM_MATURATION_DISPATCH_DIR"]
        for f in os.listdir(d):
            os.remove(os.path.join(d, f))
        with open(os.path.join(d, "state.json"), "w") as fh:
            json.dump({"mods": {MOD: {"road_back": {"caused_by": STEWARD, "at": NOW - 600, "from": "in_game",
                                                    "had_items": True}}}}, fh)

    def record(self, unit):
        if unit in self.unreadable:
            return None
        r = self.recs.get(unit)
        return {k: v for k, v in r.items() if k != "status"} if r and unit in self.no_status else r

    def live_status(self, rec, *a, **k):        # systemd's word: a unit in `gone` is measured gone
        st = rec.get("status")
        return "dead" if st in ("launching", "running") and rec.get("unit") in self.gone else st

    def facts(self):
        recs = [dict(r, live_state=self.live_status(r)) for u, r in self.recs.items() if self.record_seen(u)]
        runs = MN.runs_for_mods([MOD], recs, [], {}, NOW, spend=lambda r: (1.0, None, False), titles=TITLES)[MOD]
        ends = [r["end"] for r in runs if isinstance(r["end"], (int, float))]
        offline = self.stage == "offline_build"
        return {MOD: {"mod": MOD, "stage": self.stage, "version": "0.1.0", "visit": 4,
                      "owed": "build" if offline else "exit not met", "refused_bars": ["unbuilt"] if offline else [],
                      "live_units": "UNMEASURED" if self.blind_records else [r["unit"] for r in runs if r["live"]],
                      "last_end": max(ends) if ends else None, "ingame_live": [], "ingame_runs": [],
                      "ended_runs": [r for r in runs if not r["live"] and isinstance(r["end"], (int, float))],
                      "opened": "2026-11-23T01:00:00-08:00", "blocked": [],
                      "exit": {"state": "not_met", "why": ["sc_spared reads FAIL"], "record": "x"}}}

    def record_seen(self, u):
        return u not in self.unreadable and u not in self.no_status

    def launch_brief(self, item, text, model, cap, seat="BENCH", env=None, **kw):
        unit = "rm-detached-bench-%s-%d" % (item.lower()[-24:], len(self.recs))
        env = dict(env or {})
        if self.strip:
            env = {k: v for k, v in env.items() if not k.startswith("RM_CONTROL_")}
        self.recs[unit] = {"unit": unit, "item": item, "status": "running", "at": NOW, "env": env}
        self.launched.append((item, unit, env))
        return 0, "DETACHED %s" % unit, unit

    def grants(self):
        return [e["body"]["token"] for e in ML.read(self.root, MOD) if e.get("kind") == "lease.grant"]

    def tick(self, now):
        fx = {"facts": self.facts, "account": lambda: (True, "ok"), "bridge": lambda p: (True, "free"),
              "record": self.record, "launch_brief": self.launch_brief, "known": lambda: set(),
              "file": lambda item, title, why, **k: (True, "filed"), "publish": lambda item: (True, "pushed"),
              "launch": lambda mod, cap, item, **k: self.launch_brief(item, "", "opus", cap),
              "open_items": lambda ids, **kw: list(self.open), "item_live": lambda i: next(
                  (u for u, r in self.recs.items() if r["item"] == i and r["status"] == "running"), None),
              "designer_state": lambda m: None, "designer_unit": lambda m: None, "designer_chain": lambda m: None,
              "version_locked": lambda m: True, "version_evidence": lambda m: [], "discovered": lambda: [],
              "seed": lambda root, mod: "x", "card": lambda *a: None, "pilot": lambda root, mod: True,
              "repair_launch": lambda *a, **k: (True, "fixture", None), "land_ledger": lambda paths: "landed",
              "adopt_walk": lambda *a: None, "endings": lambda *a, **k: [], "clone": lambda: (0, 0),
              "convergence": lambda root, rd: None, "hands": {}, "rescue": {}, "pause": lambda n: {},
              "pins": lambda: {}}
        with Patch((MD, "pilot_ledger", lambda root, mod: True), (MD, "land_ledger", lambda *a, **k: "landed"),
                   (MD.DH, "live_status", self.live_status), (MD, "record_spend", lambda *a, **k: None),
                   (MD, "slow_chores", lambda *a, **k: None), (MD, "record_holder_session", lambda *a, **k: "-"),
                   (M, "ledger_needs", lambda root, ids: {}), (MD.PP, "expire", lambda n: []),
                   (MD.PP, "state", lambda n=None: {}), (MD.PP, "reason", lambda pz, mod=None: None),
                   (MD.PP, "summary", lambda pz: {"said": []}), (MD.PC, "state", lambda: {}),
                   (MD.PC, "off", lambda **k: None), (MD.OH, "load", lambda: {}),
                   (control, "queue_apply", lambda a: a), (control, "heartbeat", lambda *a: None),
                   (control, "game_held", lambda g: None)):
            rd = MD.tick(self.root, dict(CFG), True, fx=fx, now=now)
        self.needs_conductor = rd["needs_conductor"]
        return (rd["mods"].get(MOD) or {})

    def state(self):
        with open(os.path.join(os.environ["RM_MATURATION_DISPATCH_DIR"], "state.json")) as fh:
            return json.load(fh)["mods"][MOD]


def say(w, rows):
    return "launched %s grants %s reads %s" % ([x[0][12:40] for x in w.launched], w.grants(),
                                               [(r.get("decision"), str(r.get("why"))[:160]) for r in rows])


def started(w):
    """Tick N: the holder starts on both items, one lease. -> its row."""
    r = w.tick(NOW)
    if len(w.launched) != 1 or len(w.grants()) != 1 or len(w.state().get("holder_road_back") or []) != 1:
        raise AssertionError("the fixture launched no holder at tick N: %s" % say(w, [r]))
    return r


def t_a_live_holder_gets_no_second_run():
    w = World()
    rows = [started(w), w.tick(NOW + 68), w.tick(NOW + 128)]
    return (len(w.launched) == 1 and len(w.grants()) == 1 and [r.get("decision") for r in rows[1:]] == ["live", "live"]
            ), say(w, rows)


def t_a_holder_launch_records_its_mod():
    w = World()
    started(w)
    item, unit, env = w.launched[0]
    ok = [env.get("RM_CONTROL_MOD") == MOD, env.get("RM_CONTROL_STAGE") == "in_game", "RM_MODLEDGER_WRITER" in env,
          MN.runs_for_mods([MOD], list(w.recs.values()), [], {}, NOW, titles=TITLES)[MOD] != [],
          MN.runs_for_mods([MOD], [dict(w.recs[unit], env={})], [], {}, NOW, titles=TITLES)[MOD] == []]
    for pilot in (True, False):
        w2 = World()
        row = {"mod": MOD, "stage": "in_game", "cert_reds": ["T_A"], "known_red": {"T_A": CARRIER}, "cap": 10,
               "certificate": {"rows": []}, "cert_gate": {"stage": "in_game"}}
        st = {"mods": {MOD: {}}}
        with Patch((MD, "pilot_ledger", lambda root, mod: pilot), (MD, "land_ledger", lambda *a, **k: "landed")):
            MD.cert_launch(w2.root, dict(CFG, **{MD.MM.PINS_KEY: {}}), st, row, NOW,
                           {"launch_brief": w2.launch_brief, "ended": lambda ids: set(),
                            "publish": lambda i: (True, "ok"), "pilot": lambda root, mod: pilot}, set(),
                           lambda *a, **k: (True, "filed"))
        e = w2.launched[0][2] if w2.launched else {}
        ok += [e.get("RM_CONTROL_MOD") == MOD, "RM_CONTROL_STAGE" not in e,
               ("RM_MODLEDGER_WRITER" in e) is pilot]
    return all(ok), "%s env %s" % (ok, env)


def t_a_live_run_that_placement_missed_is_live():
    w = World(strip=True)           # the record names no mod, as the launch wrote it on 2026-11-23
    rows = [started(w), w.tick(NOW + 68), w.tick(NOW + 128)]
    live = [r.get("decision") for r in rows[1:]] == ["live", "live"] and len(w.launched) == 1 and len(w.grants()) == 1
    run = {"unit": "rm-j", "run": "j1", "writer": "JUDGE.j1"}
    for status in ("launching", "running"):
        f = MD.own_live({"mods": {MOD: {"ledger_runs": [run]}}}, {MOD: {"live_units": []}},
                        lambda u: {"unit": u, "status": status}, lambda r: r["status"])
        live = live and f[MOD]["live_units"] == ["rm-j"]
    return live, say(w, rows)


def t_a_live_run_holds_the_mod_at_every_stage():
    """A live run moves its own mod's stage (`maturation.py advance`): the next stage's steward waits for its end. Each
    stage has its control: the same tick with that run finished launches."""
    out = []
    for stage in ("preflight", "pre_human", "in_game"):
        for rec, go in (({"status": "running"}, False), (None, False), ({"status": "finished"}, True)):
            w = World(strip=True)
            w.stage = stage
            st = {"mods": {MOD: {"ledger_runs": [{"unit": "rm-old", "run": "run-1", "writer": "HOLDER.run-1"}]}}}
            with open(os.path.join(os.environ["RM_MATURATION_DISPATCH_DIR"], "state.json"), "w") as fh:
                json.dump(st, fh)
            if rec:
                w.recs["rm-old"] = {"unit": "rm-old", "item": CARRIER, "at": NOW - 900, "env": {}, "result": "success",
                                    **rec}
            ML.launch(w.root, MOD, "run-1", "holder", stage=stage)
            r = w.tick(NOW)
            out.append((stage, rec, (len(w.launched) == 1 and len(w.grants()) == 2) if go else (
                not w.launched and len(w.grants()) == 1 and r.get("decision") == "live" and "rm-old" in str(r.get("why"))
                and ("cannot be read" in str(r.get("why"))) is (rec is None)), say(w, [r])))
    # a launch refused only for a slot is never granted again past the fence (prioritise), and an act or a zero-token
    # rerun, which grants no lease, is left alone; a mod whose live run is not a ledger run keeps its launch
    own, other = {MOD: {"live_units": ["u"], "own_live": ["u"]}}, {MOD: {"live_units": ["u"]}}
    for facts, row, go in ((own, {"decision": "slots_full"}, False), (own, {"decision": "steward", "aut": "steward"}, False),
                           (own, {"decision": "launch", "cert_rerun_key": "k"}, True),
                           (own, {"decision": "autolock", "aut": "autolock"}, True),
                           (other, {"decision": "steward", "aut": "steward"}, True)):
        row = dict(row, mod=MOD, why="x")
        la = MD.one_run_fence(facts, [row], [MOD])
        out.append((row, None, (la == [MOD] and row["decision"] != "live") if go else (
            la == [] and row["decision"] == "live" and not row.get("aut")), la))
    w = World()
    w.open.clear()
    first = w.tick(NOW)
    if len(w.launched) != 1 or len(w.grants()) != 1 or not any(
            e.get("unit") == w.launched[0][1] for e in (w.state().get("steward") or {}).values()):
        raise AssertionError("the in-game steward did not start: %s" % say(w, [first]))
    unit = w.launched[0][1]
    w.stage = "pre_human"
    # The cooperative stop has told the books, but the unit is still working toward its stopping point.
    control.void_books(unit, MOD, "stopped (at-easy-spot): fixture", None, "fixture-stop")
    pending = w.tick(NOW + 60)
    grants = len(w.grants())
    moved = w.state().get("voided") or []
    assert any(e["book"] == "ledger_runs" and e["unit"] == unit for e in moved), moved
    out.append(("cooperative stop pending", None, pending.get("decision") == "live" and unit in pending.get("live", [])
                and len(w.launched) == grants == 1, "pre_human read %s with %d launches and %d leases" % (
                    pending.get("decision"), len(w.launched), grants)))
    w.recs[unit].update(status="finished", ended=NOW + 100, result="success (exited 0)")
    ended = w.tick(NOW + 120)
    out.append(("cooperative stop ended", None, ended.get("decision") == "launched" and len(w.grants()) == grants + 1,
                "pre_human read %s with %d leases" % (ended.get("decision"), len(w.grants()))))
    return all(x[2] for x in out), [x for x in out if not x[2]]


def t_an_ended_holder_frees_the_mod():
    out = []
    for how in ("finished", "gone"):
        for strip in (False, True):
            w = World(strip=strip)
            rows = [started(w), w.tick(NOW + 68)]
            unit = w.launched[0][1]
            if how == "finished":
                w.recs[unit].update(status="finished", ended=NOW + 100, result="success (exited 0)")
            else:
                w.gone.add(unit)
            rows += [w.tick(NOW + 900), w.tick(NOW + 960)]
            out.append((how, strip, len(w.launched) == 2, len(w.grants()) == 2, rows[1].get("decision") == "live",
                        rows[3].get("decision") == "live", say(w, rows)))
    f = MD.own_live({"mods": {MOD: {"ledger_runs": [{"unit": "rm-x", "ended": NOW}]}}}, {MOD: {"live_units": []}},
                    lambda u: None, lambda r: r["status"])
    w = World()
    w.stage = "offline_build"
    w.open = [{"id": CARRIER, "needs": "offline"}]
    started(w)
    live = w.tick(NOW + 60)
    unit = w.launched[0][1]
    w.open.clear()
    w.recs[unit].update(status="finished", ended=NOW + 100, result="success (exited 0)")
    settling = w.tick(NOW + 120)
    build = w.tick(NOW + 100 + CFG["settle_s"])
    ok = (live.get("decision") == "live" and settling.get("decision") == "settling"
          and build.get("decision") == "launched" and build.get("refused") == 1 and not w.needs_conductor
          and not w.state().get("stopped") and len(w.launched) == 2 and w.state()["launches"][-1]["ids"] == ["unbuilt"])
    if not ok:
        return False, "offline road-back holder after settlement read %s with %d launches: %s" % (
            build.get("decision"), len(w.launched), "; ".join(w.needs_conductor) or build.get("why"))
    return all(x[2] and x[3] and x[4] and x[5] for x in out) and f[MOD]["live_units"] == [], out


def t_an_unreadable_record_is_not_an_end():
    out = []
    for how in ("unreadable", "no_status"):
        for strip in (False, True):
            w = World(strip=strip)
            rows = [started(w)]
            getattr(w, how).add(w.launched[0][1])
            rows += [w.tick(NOW + 900), w.tick(NOW + 960)]
            out.append((how, strip, len(w.launched) == 1 and len(w.grants()) == 1 and all(
                r.get("decision") == "live" and "cannot be read" in str(r.get("why")) for r in rows[1:]), say(w, rows)))
    def boom(u):
        raise OSError("[Errno 12] Cannot allocate memory")
    f = MD.own_live({"mods": {MOD: {"ledger_runs": [{"unit": "rm-x"}]}}}, {MOD: {"live_units": []}}, boom)[MOD]
    out.append(("raises", None, f["live_units"] == ["rm-x"] and f["live_unread"] == ["rm-x"], f))
    return all(x[2] for x in out), [x for x in out if not x[2]]


def t_an_unreadable_reading_stays_unreadable():
    run = {"unit": "rm-x", "run": "r1", "writer": "HOLDER.r1"}
    st = {"mods": {MOD: {"ledger_runs": [run, dict(run)]}}}
    rec = lambda u: {"unit": u, "status": "running"}     # noqa: E731
    status = lambda r: r["status"]                      # noqa: E731
    facts = {MOD: {"live_units": "UNMEASURED"}}
    a = MD.own_live(st, facts, rec, status)[MOD]["live_units"]
    placed = MD.own_live(st, {MOD: {"live_units": ["rm-x"]}}, rec, status)[MOD]
    b = placed["live_units"]
    c = MD.own_live(st, {MOD: {"live_units": []}}, rec, status)[MOD]["live_units"]
    src = {MOD: {"live_units": []}}
    MD.own_live(st, src, rec, status)
    w = World()
    started(w)
    w.blind_records = True
    r = w.tick(NOW + 68)
    return (a == "UNMEASURED" and b == ["rm-x"] and placed.get("own_live") == ["rm-x"] and c == ["rm-x"] and src == {MOD: {"live_units": []}}
            and len(w.launched) == 1), (a, b, c, say(w, [r]))


def main():
    tests = [t_a_live_holder_gets_no_second_run, t_a_holder_launch_records_its_mod,
             t_a_live_run_that_placement_missed_is_live, t_a_live_run_holds_the_mod_at_every_stage, t_an_ended_holder_frees_the_mod,
             t_an_unreadable_record_is_not_an_end, t_an_unreadable_reading_stays_unreadable]
    bad = 0
    for t in tests:
        try:
            ok, why = t()
        except Exception as e:  # noqa: BLE001  a crash is a FAIL with its cause
            import traceback
            ok, why = False, "%s: %s %s" % (type(e).__name__, e, traceback.format_exc()[-600:])
        bad += not ok
        print("%s %s%s" % ("PASS" if ok else "FAIL", t.__name__[2:].replace("_", "-"), "" if ok else ": %s" % (why,)))
    shutil.rmtree(TMP, ignore_errors=True)
    print("ALL PASS" if not bad else "%d of %d FAIL" % (bad, len(tests)))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
