#!/usr/bin/env python3
"""selftest_dispatcher_beat.py — the Dispatcher inside a metronome beat (OPS_METRONOME_MIGRATE_CLOCKS_FENCED, clock 3).

The metronome's dispatch phase kills a tick at METRONOME_DEADLINE (limit_s 20; live ticks measured p95 21 s, max 97 s).
  beat deadline   execute starts no deferrable act (ring, recover, withdraw, login, role launch) once BEAT_ACT_RESERVE_S
                  remain: those are given back exactly and journalled `deferred`, never an alarm; alarms and every
                  other kind still run (decide() already moved their state); BEAT_STARVED_AFTER deferring beats in a
                  row alarm tick:beat_starved and stop the dead-man's last_ok_tick
  fence           --metronome-gen: an act is started only while metronome.may_act says the generation is live;
                  Fenced stops the tick (exit 3), gives back what was not started and journals `fenced`, no alarm
  step limits     observing+deciding end at the act reserve, execute and the helper budget BEAT_HARD_RESERVE_S before
                  the kill: a step past its end is cut (SIGALRM), journalled `step_cut` naming it, its undone acts
                  given back, and the tick still ends by itself inside the beat with its state saved; never
                  tick:raised. Each beat's step seconds go to tick_steps.jsonl
  ownership       an --apply tick without a generation acts nothing while the phase table owns rm-dispatcher.timer
                  and that timer is not measured inactive; with it off, it is an on-demand wake and runs
Nothing outside a temp dir is touched.
"""
import json
import os
import sys
import tempfile
import time

HERE = os.path.dirname(os.path.abspath(__file__))
TMP = tempfile.mkdtemp(prefix="selftest_dispatcher_beat_")
os.environ["RM_DISPATCHER_STATE"] = os.path.join(TMP, "state")
os.environ["TESTQ_QUEUE"] = os.path.join(TMP, "testq")      # git_lock's ingest.lock: never the real queue
os.environ.pop("METRONOME_DEADLINE", None)
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.dirname(HERE))
import dispatcher as D  # noqa: E402

FAILS = []


def check(ok, msg):
    print(("ok    " if ok else "FAIL  ") + msg)
    if not ok:
        FAILS.append(msg)


class Lock:
    def close(self):
        pass


def sched():
    path = os.path.join(TMP, "sched.json")
    with open(path, "w") as f:
        json.dump({"seats": {}, "roles": [], "alarm_item": "DISPATCHER_ALARMS_X", "ledger_notes": True,
                   "publish": True, "no_handoff": {"conductor_log": os.path.join(TMP, "conductor_log.md")}}, f)
    return D.load_schedule(path)


def alarms(n):
    return [{"do": "alarm", "kind": "k%d" % i, "why": "w", "note": True} for i in range(n)]


def journal(root):
    p = os.path.join(root, "journal.jsonl")
    return [json.loads(x) for x in open(p)] if os.path.exists(p) else []


def slow_note(item, text):
    time.sleep(0.25)
    return True, "ok"


def ring_act(seat, rid):
    return {"do": "ring", "seat": seat, "ring_id": rid, "message": "m"}


def test_beat_deadline_defers():
    sch, root = sched(), os.path.join(TMP, "defer")
    os.makedirs(root, exist_ok=True)
    st = {"seats": {"A": {"ring": {"ring_id": "ra"}}, "B": {"ring": {"ring_id": "rb"}}}, "alarms": {}, "wakes": [],
          "recovers": []}
    pub, rung = [], []
    fx = {"lock": Lock, "note": slow_note, "publish": lambda n: pub.append(n) or "pushed",
          "ring": lambda root, seat, *a, **k: rung.append(seat) or "rung"}
    acts = [ring_act("A", "ra"), dict(alarms(1)[0], kind="k0"), dict(alarms(1)[0], kind="k1"), ring_act("B", "rb")]
    D.execute(acts, sch, st, root, True, 100.0, fx, act_deadline=time.time() + 0.4, deadline=time.time() + 5)
    check(rung == ["A"], "a ring is started before the beat deadline only: %s" % rung)
    check([a.get("kind") for a in acts if a["do"] == "alarm" and "result" in a] == ["k0", "k1"],
          "alarms still run past the act deadline (their carry is already popped)")
    check(sorted(st["alarms"]) == ["k0", "k1"], "both alarms stamped: %s" % sorted(st["alarms"]))
    check("ring" not in st["seats"]["B"] and "ring" in st["seats"]["A"], "the deferred ring is given back, the rung one kept")
    j = journal(root)
    dfr = [x for x in j if x["do"] == "deferred"]
    check(len(dfr) == 1 and "1 act(s) not started (ring)" in dfr[0]["why"], "one `deferred` line names the ring: %s" % dfr)
    check(not any(x.get("kind", "").startswith("tick:") for x in j), "deferral is not an alarm")
    check(pub == [2], "the notes already made are still published: %s" % pub)


def test_deferred_launch_is_given_back():
    sch, root = sched(), os.path.join(TMP, "launch")
    os.makedirs(root, exist_ok=True)
    st = {"seats": {}, "alarms": {}, "roles": {
        "Arbiter": {"pending_launch": {"unit": "u2", "mode": "slot", "had_done": False, "key": "d1",
                                       "event_cursor": None, "events_seen": None}, "runs": [], "done": {"d1": 5}},
        "Other": {"pending_launch": {"unit": "u9", "mode": "fresh"}, "runs": []}}}
    launch = {"do": "role_launch", "role": "Arbiter", "unit": "u2"}
    D.execute([launch], sch, st, root, True, 100.0, {"lock": Lock, "publish": lambda n: None},
              act_deadline=time.time() - 1)
    check("pending_launch" not in st["roles"]["Arbiter"] and "d1" not in st["roles"]["Arbiter"]["done"],
          "the deferred launch's reservation is given back (its slot is due again)")
    check("pending_launch" in st["roles"]["Other"], "a reservation of no deferred act is not touched (unreserve's alarm "
          "keeps it)")


def test_deferred_ring_is_given_back():
    sch, root = sched(), os.path.join(TMP, "ring")
    os.makedirs(root, exist_ok=True)
    # decide() made the ring: a pending ring to verify and a wake on the caps, both at this tick's now
    st = {"seats": {"FOUNDRY": {"ring": {"ring_id": "r1", "at": 100.0}}}, "alarms": {}, "recovers": [],
          "wakes": [{"seat": "FOUNDRY", "at": 100.0}, {"seat": "BENCH", "at": 100.0}]}
    ring = {"do": "ring", "seat": "FOUNDRY", "ring_id": "r1", "message": "m"}
    calls = []
    fx = {"lock": Lock, "note": slow_note, "publish": lambda n: "pushed",
          "ring": lambda *a, **k: calls.append(a) or "rung"}
    D.execute([ring], sch, st, root, True, 100.0, fx, act_deadline=time.time() - 1)
    check(not calls, "no ring is started past the beat deadline")
    check("result" not in ring, "the deferred ring has no result")
    check("ring" not in st["seats"]["FOUNDRY"], "the never-released ring is given back: nothing to verify")
    check(st["wakes"] == [{"seat": "BENCH", "at": 100.0}], "its wake is off the caps: %s" % st["wakes"])
    check(any(x["do"] == "deferred" and "ring" in x["why"] for x in journal(root)), "the deferral names the ring")


def test_fence_stops_the_tick():
    sch, root = sched(), os.path.join(TMP, "fence")
    os.makedirs(root, exist_ok=True)
    st = {"seats": {}, "alarms": {}}
    asked = []

    def fence(what):
        asked.append(what)
        return len(asked) < 2
    acts = alarms(3)
    try:
        D.execute(acts, sch, st, root, True, 100.0, {"lock": Lock, "note": lambda i, t: (True, ""),
                                                      "publish": lambda n: "pushed"}, fence=fence)
        check(False, "a fenced act must raise Fenced")
    except D.Fenced:
        pass
    check([a["kind"] for a in acts if "result" in a] == ["k0"], "only the act before the fence ran")
    check(sorted(st["alarms"]) == ["k0"], "the fenced acts keep no stamp")
    dry = alarms(2)
    D.execute(dry, sch, {"seats": {}, "alarms": {}}, root, False, 100.0, {}, fence=lambda w: False)
    check(all("result" in a for a in dry), "a dry tick is never fenced (it acts nothing)")


def test_tick_fenced_and_beat_end():
    sch = sched()
    o = {"paused": None, "agents": {"state": "MEASURED", "sessions": []}}
    real_decide = D.decide
    seq = iter(range(10 ** 6))

    def decide(sch, st, o, now, apply, out=None):
        rid = "r%d" % next(seq)
        st["seats"].setdefault("A", {})["ring"] = {"ring_id": rid}
        out.extend([dict(alarms(1)[0], kind="k_" + rid), ring_act("A", rid)])    # a new kind: never rate-limited
        return out
    D.decide = decide
    # the alarm's note outlasts the act reserve, so the ring after it is deferred (decide itself ends in time)
    fx = {"lock": Lock, "note": lambda i, t: time.sleep(0.5) or (True, ""), "publish": lambda n: "pushed",
          "conductor_log": lambda *a: "conductor log appended: t", "ring": lambda *a, **k: "rung"}

    def at_end():
        return time.time() + D.BEAT_ACT_RESERVE_S + 0.2
    try:
        try:
            D.tick(sch, True, obs=o, now=time.time(), fx=fx, still_owner=lambda w: False)
            check(False, "tick with a dead generation must raise Fenced")
        except D.Fenced:
            pass
        root = D.state_root(True)
        j = journal(root)
        check(any(x["do"] == "fenced" for x in j), "a fenced tick journals `fenced`")
        check(not any(x.get("kind") == "tick:raised" for x in j), "a fenced tick is not a raised tick")
        st = D.load_state(root)
        check(not st.get("alarm_carry"), "a fenced tick carries no alarm to the next")
        acts = D.tick(sch, True, obs=o, now=time.time(), fx=fx, beat_end=at_end())
        ran = [a["do"] for a in acts if "result" in a]
        check(ran == ["alarm"] and [a["do"] for a in acts][-1] == "deferred",
              "a tick at its beat's end defers its ring and still runs its alarm: ran %s" % ran)
        st = D.load_state(root)
        check(st.get("last_tick") and not st.get("alarm_carry"), "the deferred tick saved its state, no alarm carried")
        check(st.get("last_ok_tick") and st.get("beat_deferred_streak") == 1,
              "one deferring beat: still a working tick, streak 1")
        t1 = time.time() + 10
        for k in range(D.BEAT_STARVED_AFTER - 1):
            acts = D.tick(sch, True, obs=o, now=t1 + k, fx=fx, beat_end=at_end())
        st = D.load_state(root)
        check(any(a.get("kind") == "tick:beat_starved" for a in acts), "beat %d deferring in a row alarms beat_starved"
              % D.BEAT_STARVED_AFTER)
        check(st.get("last_ok_tick") == D.iso(t1 + D.BEAT_STARVED_AFTER - 3),
              "a starved tick stops the dead-man's last_ok_tick: %s" % st.get("last_ok_tick"))
        D.tick(sch, True, obs=o, now=t1 + 50, fx=fx, beat_end=time.time() + 60)
        st = D.load_state(root)
        check("beat_deferred_streak" not in st and st.get("last_ok_tick") == D.iso(t1 + 50),
              "a beat that fits ends the streak and stamps last_ok_tick again")
        os.environ["METRONOME_DEADLINE"] = "%.3f" % (time.time() + 60)
        try:
            check(abs(D.beat_deadline() - time.time() - 60) < 2, "beat_deadline reads METRONOME_DEADLINE")
            acts = D.tick(sch, True, obs=o, now=time.time() + 1, fx=fx)
            check(not any(a["do"] == "deferred" for a in acts), "a beat with time left defers nothing")
        finally:
            os.environ.pop("METRONOME_DEADLINE", None)
        check(D.beat_deadline() is None, "outside a beat there is no deadline")
        os.environ["METRONOME_DEADLINE"] = "garbage"
        check(D.beat_deadline() is None, "an unreadable METRONOME_DEADLINE is no deadline")
        os.environ.pop("METRONOME_DEADLINE", None)
    finally:
        D.decide = real_decide


def test_apply_without_generation_refuses_when_owned():
    real, real_state = D.metronome_owner, D.old_timer_state
    called = []
    real_tick = D.tick
    D.tick = lambda *a, **k: called.append(1) or []
    sched = os.path.join(TMP, "sched.json")
    try:
        D.metronome_owner = lambda timer=D.OLD_TIMER: "dispatch"
        for st in ("active", "unmeasured (rc 1)", ""):
            D.old_timer_state = lambda timer=D.OLD_TIMER, st=st: st
            rc = D.main(["tick", "--apply", "--schedule", sched])
            check(rc == 0 and not called, "an owned clock, old timer %r: --apply without --metronome-gen acts nothing" % st)
        D.main(["tick", "--schedule", sched])
        check(called == [1], "a dry tick still runs while owned")
        D.old_timer_state = lambda timer=D.OLD_TIMER: "inactive"
        D.main(["tick", "--apply", "--schedule", sched])
        check(called == [1, 1], "owned with the old timer measured inactive: an on-demand wake (seat_restart) runs")
        D.metronome_owner = lambda timer=D.OLD_TIMER: None
        D.old_timer_state = lambda timer=D.OLD_TIMER: (_ for _ in ()).throw(AssertionError("read only when owned"))
        D.main(["tick", "--apply", "--schedule", sched])
        check(called == [1, 1, 1], "before cutover the old timer's --apply tick runs")
    finally:
        D.metronome_owner, D.old_timer_state, D.tick = real, real_state, real_tick
    check(D.metronome_owner() in (None, "dispatch"), "metronome_owner reads the real phase table")


def test_step_limit():
    import signal
    sl = getattr(D, "step_limit", None)
    check(sl is not None, "dispatcher has step_limit")
    if sl is None:
        return
    prev = signal.getsignal(signal.SIGALRM)
    t0, cut = time.time(), None
    try:
        with sl("slow", time.time() + 0.3):
            time.sleep(3)
    except BaseException as e:  # noqa: BLE001
        cut = e
    check(getattr(cut, "step", None) == "slow" and not isinstance(cut, Exception) and time.time() - t0 < 1.5,
          "a step past its end is cut (a BaseException, so `except Exception` cannot swallow it): %r" % cut)
    check(signal.getsignal(signal.SIGALRM) == prev and signal.getitimer(signal.ITIMER_REAL)[0] == 0,
          "the cut restores SIGALRM and stops its timer")
    with sl("fast", time.time() + 5):
        pass
    check(signal.getitimer(signal.ITIMER_REAL)[0] == 0, "a step inside its end leaves no timer running")
    with sl("free", None):
        time.sleep(0.05)
    try:
        with sl("late", time.time() - 1):
            check(False, "a step whose end has passed must not start")
    except BaseException as e:  # noqa: BLE001
        check(getattr(e, "step", None) == "late", "an end already passed cuts the step before it starts")


def test_cut_publish_child_dies():
    sl = getattr(D, "step_limit", None)
    pidf = os.path.join(TMP, "child.pid")
    argv = [sys.executable, "-c", "import os,time; open(%r,'w').write(str(os.getpid())); time.sleep(30)" % pidf]
    t0 = time.time()
    try:
        if sl is None:
            raise RuntimeError("no step_limit")
        with sl("execute", time.time() + 0.8):
            D.publish_bounded(0, 20, argv=argv)
    except BaseException:  # noqa: BLE001
        pass
    time.sleep(0.2)
    pid = int(open(pidf).read()) if os.path.exists(pidf) else None
    alive = False
    if pid:
        try:
            os.kill(pid, 0)
            alive = open("/proc/%d/stat" % pid).read().split()[2] != "Z"
        except OSError:
            alive = False
    check(pid and not alive and time.time() - t0 < 3,
          "a publish child is killed when its wait is cut (its own session: nothing else stops it): pid %s alive %s"
          % (pid, alive))
    if alive:
        os.kill(pid, 9)


def _cut_tick(name, decide, fx_extra=None, hb=None, beat_s=2.0):
    """One --apply tick with small reserves (act 1.0 s, hard 0.5 s) and beat_end beat_s ahead.
    -> (acts or the exception, seconds it took, beat_end, root)"""
    saved = D.BEAT_ACT_RESERVE_S, getattr(D, "BEAT_HARD_RESERVE_S", None), D.decide, D.HB.tick_step
    os.environ["RM_DISPATCHER_STATE"] = os.path.join(TMP, "cut_" + name)
    D.BEAT_ACT_RESERVE_S, D.BEAT_HARD_RESERVE_S, D.decide = 1.0, 0.5, decide
    if hb:
        D.HB.tick_step = hb
    fx = {"lock": Lock, "note": lambda i, t: (True, ""), "publish": lambda n: "pushed",
          "conductor_log": lambda *a: "conductor log appended: t", "ring": lambda *a, **k: "rung"}
    fx.update(fx_extra or {})
    o = {"paused": None, "agents": {"state": "MEASURED", "sessions": []}}
    t0 = time.time()
    beat_end = t0 + beat_s
    try:
        out = D.tick(sched(), True, obs=o, now=t0, fx=fx, beat_end=beat_end)
    except BaseException as e:  # noqa: BLE001
        out = e
    finally:
        D.BEAT_ACT_RESERVE_S, D.BEAT_HARD_RESERVE_S, D.decide, D.HB.tick_step = saved
        os.environ["RM_DISPATCHER_STATE"] = os.path.join(TMP, "state")
    return out, time.time() - t0, beat_end, os.path.join(TMP, "cut_" + name)


def _cut_checks(name, out, took, beat_end, root, step):
    j = journal(root)
    check(isinstance(out, list), "%s: the tick returns, it does not raise: %r" % (name, out if not isinstance(out, list) else ""))
    check(time.time() < beat_end, "%s: the tick ends inside its beat (took %.2f s, %.2f s left)"
          % (name, took, beat_end - time.time()))
    check(any(x.get("do") == "step_cut" and x.get("step") == step for x in j),
          "%s: the journal names the cut step %r: %s" % (name, step, [x.get("do") for x in j]))
    check(not any(x.get("kind") == "tick:raised" for x in j), "%s: no tick:raised" % name)
    st = D.load_state(root)
    check(st.get("last_tick") and not st.get("alarm_carry") and st.get("beat_deferred_streak") == 1,
          "%s: state saved, no alarm carried, the cut counts toward beat_starved" % name)
    p = os.path.join(root, "tick_steps.jsonl")
    rows = [json.loads(x) for x in open(p)] if os.path.exists(p) else []
    check(rows and rows[-1].get(step) == "cut" and isinstance(rows[-1].get("total"), (int, float)),
          "%s: tick_steps.jsonl records the cut and the tick's seconds: %s" % (name, rows[-1:]))
    return st


def ring_then(seconds, alarm_first=False):
    def decide(sch, st, o, now, apply, out=None):
        st["seats"].setdefault("A", {})["ring"] = {"ring_id": "rx"}
        out.extend(([dict(alarms(1)[0], kind="slow", conductor_log=True)] if alarm_first else []) + [ring_act("A", "rx")])
        if seconds:
            time.sleep(seconds)
        return out
    return decide


def test_slow_observe_is_cut():
    out, took, end, root = _cut_tick("observe", ring_then(6))
    st = _cut_checks("slow decide", out, took, end, root, "observe")
    check("ring" not in (st.get("seats", {}).get("A") or {}), "slow decide: the ring it decided is given back")


def test_slow_execute_is_cut():
    hb = []
    out, took, end, root = _cut_tick("execute", ring_then(0, alarm_first=True),
                                     {"conductor_log": lambda *a: time.sleep(6) or "appended"},
                                     hb=lambda *a, **k: hb.append(1))
    st = _cut_checks("slow act", out, took, end, root, "execute")
    check("ring" not in (st.get("seats", {}).get("A") or {}), "slow act: the ring not yet started is given back")
    check(not hb, "slow act: no time left, so the helper budget is not started")


def test_slow_helper_budget_is_cut():
    out, took, end, root = _cut_tick("budget", ring_then(0), hb=lambda *a, **k: time.sleep(6))
    _cut_checks("slow helper budget", out, took, end, root, "helper_budget")
    j = journal(root)
    check(any(x.get("do") == "ring" and x.get("result") for x in j), "slow helper budget: the acts before it ran")


def test_killed_publish_leaves_the_helper_budget_its_slot():
    # live 2026-11-14 15:14Z: a publish killed at its deadline every beat, and the helper budget cut after it 4 times
    sch = sched()
    saved = D.BEAT_ACT_RESERVE_S, D.decide, D.HB.tick_step, D.publish_bounded
    os.environ["RM_DISPATCHER_STATE"] = os.path.join(TMP, "slow_publish")
    hb = []
    D.BEAT_ACT_RESERVE_S, D.decide = 1.0, ring_then(0)
    D.HB.tick_step = lambda *a, **k: hb.append(1)
    D.publish_bounded = lambda n, timeout, **k: time.sleep(max(0.0, timeout)) or "publish KILLED (stub)"
    fx = {"lock": Lock, "note": lambda i, t: (True, ""), "ring": lambda *a, **k: "rung"}
    o = {"paused": None, "agents": {"state": "MEASURED", "sessions": []}}
    try:
        t0 = time.time()
        out = D.tick(sch, True, obs=o, now=t0, fx=fx, beat_end=t0 + 5.0)
    finally:
        D.BEAT_ACT_RESERVE_S, D.decide, D.HB.tick_step, D.publish_bounded = saved
        os.environ["RM_DISPATCHER_STATE"] = os.path.join(TMP, "state")
    root = os.path.join(TMP, "slow_publish")
    j = journal(root)
    check(hb == [1] and not any(x.get("do") == "step_cut" for x in j),
          "a publish killed at its deadline still leaves the helper budget its slot: ran %s, cuts %s"
          % (hb, [x.get("step") for x in j if x.get("do") == "step_cut"]))
    check(isinstance(out, list) and time.time() < t0 + 5.0, "the slow-publish tick ends inside its beat")


def main():
    for t in (test_beat_deadline_defers, test_deferred_launch_is_given_back, test_deferred_ring_is_given_back, test_fence_stops_the_tick,
              test_tick_fenced_and_beat_end, test_apply_without_generation_refuses_when_owned, test_step_limit, test_cut_publish_child_dies,
              test_slow_observe_is_cut, test_slow_execute_is_cut, test_slow_helper_budget_is_cut,
              test_killed_publish_leaves_the_helper_budget_its_slot):
        try:
            t()
        except Exception as e:  # noqa: BLE001
            import traceback
            traceback.print_exc()
            check(False, "%s crashed: %s" % (t.__name__, e))
    for msg in FAILS:
        print("FAILED: " + msg)
    print("%d failure(s)" % len(FAILS))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
