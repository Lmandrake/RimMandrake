"""selftest_raise_ladder.py — raise_ladder.py and its wiring into the Dispatcher's dead-window path
(OPS_RAISE_REWIRE_WITH_DEATH_LADDER; design/RimMandrake/operations_metronome_strategy_2026-11-02.md §4).

Planted deaths, no real window: the ladder (2/8 min backoff, life 4 in 24 h stops, 7 in 7 days stops however spread
out, time alone clears no stop), the resets (6 h healthy clears only the day count, a named fix both), the login/quota
gate per model with backoff, single flight (old process alive, memory short), a death charged to the raise before it,
the life note, the endings read from a transcript and memwatch, and a full Dispatcher cycle through decide(). Nothing
outside a temp dir is touched.
"""
import json
import os
import sys
import tempfile
import time

HERE = os.path.dirname(os.path.abspath(__file__))
TMP = tempfile.mkdtemp(prefix="selftest_raise_ladder_")
os.environ["RM_DISPATCHER_STATE"] = os.path.join(TMP, "state")
os.environ["TESTQ_QUEUE"] = os.path.join(TMP, "testq")
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.dirname(HERE))
import raise_ladder as L  # noqa: E402
import dispatcher as D  # noqa: E402

FAILS = []
T0 = 2_000_000_000.0
M = 60


def check(ok, msg):
    print(("ok    " if ok else "FAIL  ") + msg)
    if not ok:
        FAILS.append(msg)


def reg(*deaths):
    rec = {"deaths": [], "raises": []}
    for at, ending in deaths:
        L.record_death(rec, at, ending)
    return rec


def test_ladder():
    rec = reg((T0, "window_gone"))
    v = L.decide(rec, T0 + 119)
    check(v["verdict"] == "wait" and v["life"] == 2 and v["until"] == T0 + 120, "life 2 waits 2 min after the death (%r)" % v)
    v = L.decide(rec, T0 + 120)
    check(v["verdict"] == "raise" and v["life"] == 2, "life 2 raised at 2 min")
    L.record_raise(rec, "S", T0 + 120, 2)
    L.record_death(rec, T0 + 3600, "window_gone")
    check(L.decide(rec, T0 + 3600 + 479)["verdict"] == "wait", "life 3 waits 8 min")
    check(L.decide(rec, T0 + 3600 + 480)["verdict"] == "raise", "life 3 raised at 8 min")
    L.record_death(rec, T0 + 7200, "out_of_memory")
    v = L.decide(rec, T0 + 7200 + 9999)
    check(v["verdict"] == "stop" and v["new"] and "life 4 in 24 h" in v["why"] and "out_of_memory" in v["why"]
          and "window_gone" in v["why"], "life 4 in 24 h, causes mixed: stop quoting every death (%r)" % v["why"])
    v = L.decide(rec, T0 + 9 * 86400)
    check(v["verdict"] == "stop" and not v["new"], "time alone clears no stop: still stopped 9 days on")
    # 7 in 7 days, one death every 25 h: never two in a 24 h window, yet the 7th in 6.25 days stops
    rec = {"deaths": [], "raises": []}
    verdicts = []
    t = T0
    for k in range(7):
        L.record_death(rec, t, "window_gone")
        verdicts.append(L.decide(rec, t + 600)["verdict"])
        t += 25 * 3600
    check(verdicts[:6] == ["raise"] * 6 and verdicts[6] == "stop", "7 deaths in 7 days, spread past every 24 h window: "
          "the 7th stops (%r)" % verdicts)
    check("7 deaths in 7 days" in rec["stopped"]["why"], "the breaker names itself")


def test_resets():
    rec = reg((T0, "window_gone"), (T0 + 600, "window_gone"), (T0 + 1200, "window_gone"))
    check(L.decide(rec, T0 + 2000)["verdict"] == "stop", "three deaths: stopped")
    check(not L.healthy(rec, T0 + 3000, T0 + 3000 + 6 * 3600 - 1), "5 h 59 min healthy: no reset")
    check(L.healthy(rec, T0 + 3000, T0 + 3000 + 6 * 3600) and "stopped" not in rec, "6 h healthy: the day count and stop clear")
    day, week = L.counts(rec, T0 + 3000 + 6 * 3600 + 1)
    check(day == [] and len(week) == 3, "a healthy reset clears the day, never the 7-day count")
    check(not L.healthy(rec, T0 + 3000, T0 + 3000 + 7 * 3600), "a second healthy reading with nothing new: no reset")
    rec2 = reg(*[(T0 + i * 25 * 3600, "window_gone") for i in range(7)])
    check(L.decide(rec2, T0 + 150 * 3600 + 600)["verdict"] == "stop", "seven in seven days: stopped")
    check(not L.apply_fix(rec2, {"fix": "", "at": T0}), "a fix with no name is refused")
    check(L.apply_fix(rec2, {"fix": "WATCHDOG_FIX", "at": T0 + 7 * 25 * 3600 + 1}) and "stopped" not in rec2,
          "a named fix clears the stop")
    check(L.counts(rec2, T0 + 7 * 25 * 3600 + 2) == ([], []), "a named fix clears both counts")
    check(not L.apply_fix(rec2, {"fix": "WATCHDOG_FIX", "at": T0 + 7 * 25 * 3600 + 1}), "the same fix twice applies once")


def test_gate():
    rec = {"deaths": [], "raises": []}
    L.record_death(rec, T0, "login_or_quota", "rate_limit", model="opus")
    calls = []

    def bad(model):
        calls.append(model)
        return False, "usage limit reached"
    v = L.decide(rec, T0 + 120, model_ok=bad)
    check(v["verdict"] == "gated" and v["new"] and calls == ["opus"] and v["until"] == T0 + 120 + 300,
          "login/quota: the check runs for THAT model and fails -> gated, next try in 5 min (%r)" % v)
    v = L.decide(rec, T0 + 200, model_ok=bad)
    check(v["verdict"] == "gated" and calls == ["opus"], "before the backoff ends the check is not run again")
    v = L.decide(rec, T0 + 420, model_ok=bad)
    check(v["verdict"] == "gated" and not v["new"] and v["until"] == T0 + 420 + 900, "second failure backs off 15 min")
    v = L.decide(rec, T0 + 1320, model_ok=lambda m: (None, "timeout"))
    check(v["verdict"] == "gated" and v["until"] == T0 + 1320 + 1800, "no reading is not a pass: 30 min")
    v = L.decide(rec, T0 + 3120, model_ok=lambda m: (True, ""))
    check(v["verdict"] == "raise" and rec["gate"].get("passed_at") == T0 + 3120, "the check passes -> raise")
    check(L.decide(rec, T0 + 3121, model_ok=bad)["verdict"] == "raise" and calls == ["opus"] * 2,
          "a passed gate is not rechecked for the same death")
    rec = reg((T0, "login_or_quota"))
    check(L.decide(rec, T0 + 9999)["verdict"] == "gated", "no account check available: gated, never raised blind")


def test_single_flight_and_blame():
    rec = reg((T0, "window_gone"))
    v = L.decide(rec, T0 + 200, old_alive=True)
    check(v["verdict"] == "wait" and "still running" in v["why"], "the dead window's process still alive: wait")
    v = L.decide(rec, T0 + 200, mem=(False, "0.5 GB available"))
    check(v["verdict"] == "wait" and "memory short" in v["why"], "memory short: wait")
    check(L.decide(rec, T0 + 200, mem=(None, "unreadable"))["verdict"] == "raise", "no memory reading does not block")
    rid = L.record_raise(rec, "FOUNDRY", T0 + 200, 2)
    d = L.record_death(rec, T0 + 200 + 900, "window_gone")
    check(d["raise_id"] == rid == "FOUNDRY-life2-%d" % int(T0 + 200), "a death within 15 min of a raise is charged to it")
    d = L.record_death(rec, T0 + 200 + 901 + 3600, "bogus")
    check(d["raise_id"] is None and d["ending"] == "window_gone", "later: not charged; an unknown ending is window_gone")
    L.unraise(rec, T0 + 200)
    check(rec["raises"] == [], "unraise gives back a raise never started")


def test_note_and_endings():
    last = {"at": T0, "ending": "out_of_memory", "cause": "unknown", "raise_id": "S-life2-1"}
    n = L.life_note("S", 3, last, "/c/h.md")
    check(n.startswith("Life 3 today. Life 2 ended out_of_memory at ") and "within minutes of raise S-life2-1" in n
          and "Its progress file: /c/h.md." in n and L.ADVICE["out_of_memory"] in n, "life note: number, ending, raise, file, advice (%r)" % n)
    n = L.life_note("S", 2, dict(last, ending="window_gone", raise_id=None), None)
    check(n.endswith("Its progress file: none written."), "no advice line for window_gone; no file says so")
    # memwatch events.jsonl
    p = os.path.join(TMP, "events.jsonl")
    ts = lambda t: time.strftime("%Y-%m-%dT%H:%M:%S%z", time.localtime(t))  # noqa: E731
    with open(p, "w") as f:
        f.write(json.dumps({"ts": ts(T0 - 7200), "kind": "oom_kill", "seat": "bench"}) + "\n")
        f.write(json.dumps({"ts": ts(T0 - 60), "kind": "oom_kill", "seat": "foundry"}) + "\n")
    check(L.oom_killed("FOUNDRY", T0, p) and not L.oom_killed("BENCH", T0, p), "memwatch: an oom kill in the last hour, per seat")
    # transcript endings
    clone = os.path.join(TMP, "clone")
    os.makedirs(os.path.join(clone, "infrastructure", "state", "handoffs"), exist_ok=True)
    tp = os.path.join(TMP, "t.jsonl")
    import seat_restart as SR
    orig = SR.transcript_for
    try:
        SR.transcript_for = lambda sess, cfg: tp
        for err, want in (("rate_limit", ("login_or_quota", "rate_limit")),
                          ("authentication_failed", ("login_or_quota", "authentication_failed")),
                          ("server_error", ("server_error", "unknown"))):
            with open(tp, "w") as f:
                f.write(json.dumps({"type": "user", "message": {"content": "x"}}) + "\n")
                f.write(json.dumps({"type": "assistant", "isApiErrorMessage": True, "error": err,
                                    "message": {"content": [{"type": "text", "text": "e"}], "stop_reason": "stop_sequence"}}) + "\n")
            check(L.ending_of("NOSUCHSEAT", {"pid": 1}, {"clone": clone}) == want, "ending from transcript: %s -> %r" % (err, want))
        SR.transcript_for = lambda sess, cfg: None
        check(L.ending_of("NOSUCHSEAT", {}, {"clone": clone}) == ("window_gone", "unknown"), "no transcript: window_gone")
    finally:
        SR.transcript_for = orig
    hp = os.path.join(clone, "infrastructure", "state", "handoffs", "FOUNDRY_REBOOT_HANDOFF_1.md")
    open(hp, "w").close()
    check(L.progress_of("FOUNDRY", {"clone": clone}) == hp and L.progress_of("BENCH", {"clone": clone}) is None,
          "progress file: the seat's newest handoff in its clone")
    ok, why = L.mem_ok()
    check(ok in (True, False) and "GB available" in why, "memory reads /proc/meminfo (%s)" % why)


def sched():
    s = {"seats": {"FOUNDRY": {"enabled": True, "wake": True, "recover_dead": True, "session_name": "AGENT FOUNDRY",
                               "clone": os.path.join(TMP, "clone"), "model": "opus"}},
         "roles": [], "alarm_item": "ALARMS_X", "no_handoff": {"conductor_log": os.path.join(TMP, "cl.md")}}
    path = os.path.join(TMP, "sched.json")
    with open(path, "w") as f:
        json.dump(s, f)
    return D.load_schedule(path)


def obs(sessions, ending=("window_gone", "unknown"), model_ok=None, resets=None, old_alive=False):
    return {"paused": None, "agents": {"state": "MEASURED", "sessions": sessions},
            "peek": lambda seat: {}, "events": lambda seat, since: [], "consumed": lambda seat, rid: None,
            "armed": lambda seat: {"pid": 4242}, "alive": lambda pid: True,
            "raise": {"ending": lambda seat, sess, cfg: ending, "progress": lambda seat, cfg: "/c/FOUNDRY_H.md",
                      "mem": lambda: (True, ""), "model_ok": model_ok, "resets": lambda: resets or {},
                      "old_alive": lambda pid: old_alive}}


def test_dispatcher_cycle():
    sch = sched()
    st = {"seats": {}, "wakes": [], "recovers": [], "alarms": {}}
    up = [{"name": "AGENT FOUNDRY", "status": "busy", "sessionId": "sid-1", "pid": 777}]
    D.decide(sch, st, obs(up), T0, True)
    check(st["seats"]["FOUNDRY"]["last_sess"] == {"pid": 777, "sessionId": "sid-1"}, "the live window's pid is remembered")
    t = T0 + 100
    D.decide(sch, st, obs([]), t, True)
    a = D.decide(sch, st, obs([], old_alive=True), t + 600, True)
    rec = st["lives"]["FOUNDRY"]
    check(len(rec["deaths"]) == 1 and rec["deaths"][0]["at"] == t and not [x for x in a if x["do"] == "recover"]
          and any("still running" in x.get("why", "") for x in a if x["do"] == "hold"),
          "death on the register; no raise while the old process lives")
    a = D.decide(sch, st, obs([]), t + 660, True)
    r = [x for x in a if x["do"] == "recover"]
    check(len(r) == 1 and r[0]["life"] == 2 and "Life 2 today. Life 1 ended window_gone" in r[0]["message"]
          and "/c/FOUNDRY_H.md" in r[0]["message"] and len(rec["deaths"]) == 1, "life 2 raised with its note (%r)" % r[:1])
    rid = r[0]["raise_id"]
    # the raise never comes back: raise_failed charged to it; life 3 at 8 min
    a = D.decide(sch, st, obs([]), t + 660 + 300, True)
    check(rec["deaths"][-1]["ending"] == "raise_failed" and rec["deaths"][-1]["raise_id"] == rid, "failed raise on the register")
    a = D.decide(sch, st, obs([]), t + 960 + 479, True)
    check(not [x for x in a if x["do"] == "recover"], "life 3 waits 8 min after the failed raise")
    a = D.decide(sch, st, obs([]), t + 960 + 480, True)
    check([x["life"] for x in a if x["do"] == "recover"] == [3], "life 3 raised")
    # it comes back, then dies on quota: life 4 -> stop, whatever the cause
    back = [{"name": "AGENT FOUNDRY", "status": "busy", "sessionId": "sid-1", "pid": 778}]
    D.decide(sch, st, obs(back), t + 1500, True)
    D.decide(sch, st, obs([]), t + 2000, True)
    a = D.decide(sch, st, obs([], ending=("login_or_quota", "rate_limit")), t + 2600, True)
    al = [x for x in a if x["do"] == "alarm"]
    check(len(al) == 1 and al[0]["kind"] == "ladder:FOUNDRY" and al[0]["ticket"] == "ALARMS_X" and al[0]["conductor_log"]
          and "raise_failed" in al[0]["why"] and "login_or_quota" in al[0]["why"], "life 4: stop alarm quoting every death (%r)" % al[:1])
    a = D.decide(sch, st, obs([]), t + 99 * 86400, True)
    check(not [x for x in a if x["do"] == "recover"] and [x["kind"] for x in a if x["do"] == "alarm"] == ["ladder:FOUNDRY"],
          "still stopped long after: the incident stays open")
    fix = {"FOUNDRY": {"fix": "SOME_FIX", "at": t + 99 * 86400 + 1}}
    a = D.decide(sch, st, obs([], resets=fix), t + 99 * 86400 + 10, True)
    check(any(x["do"] == "ladder_reset" for x in a) and "stopped" not in rec, "a named fix resets the ladder in the tick")
    # a quota death on a fresh ladder: gated per model until the check passes
    st2 = {"seats": {}, "wakes": [], "recovers": [], "alarms": {}}
    D.decide(sch, st2, obs(up), T0, True)
    D.decide(sch, st2, obs([]), T0 + 1, True)
    seen = []
    a = D.decide(sch, st2, obs([], ending=("login_or_quota", "rate_limit"),
                               model_ok=lambda m: seen.append(m) or (False, "limit")), T0 + 700, True)
    check(seen == ["opus"] and [x["kind"] for x in a if x["do"] == "alarm"] == ["raise_gate:FOUNDRY"]
          and not [x for x in a if x["do"] == "recover"], "quota death: the seat's model is checked, gated, one alarm")
    a = D.decide(sch, st2, obs([], model_ok=lambda m: (True, "")), T0 + 1001, True)
    check([x["life"] for x in a if x["do"] == "recover"] == [2], "check passes after the backoff: raised")
    check("recovers_per_seat_day" not in sch["caps"], "the flat recovers_per_seat_day cap is gone")
    with open(os.path.join(HERE, "dispatcher_schedule.json")) as f:
        check("recovers_per_seat_day" not in json.load(f)["caps"], "the live schedule carries no recovers_per_seat_day")


def test_reset_cli():
    root = os.path.join(TMP, "droot")
    rc = L.main(["reset", "--seat", "foundry", "--fix", "X_FIX", "--root", root])
    got = L.read_resets(root)
    check(rc == 0 and got["FOUNDRY"]["fix"] == "X_FIX" and got["FOUNDRY"]["at"] > 0, "reset CLI writes the request a tick reads")


def main():
    for t in (test_ladder, test_resets, test_gate, test_single_flight_and_blame, test_note_and_endings,
              test_dispatcher_cycle, test_reset_cli):
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
