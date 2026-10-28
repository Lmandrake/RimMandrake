#!/usr/bin/env python3
"""selftest_testq_steward.py - the SteveDesktop lane steward and its heartbeat watcher (steward.py,
STEVE_STEWARD_BUILD_NO_LLM_OWNER; design/RimMandrake/work_allocation_framework_2026-10-26.md section 6).

A temp queue, a temp ledger (RIMFLOW_LEDGER / RIMFLOW_ITEMS, the steward's own item filed in it), a temp pulse state
(RM_PULSE_STATE), push off (TESTQ_INGEST_PUSH=0); the clock is passed in, rimflow is the real CLI. Proves the three
acceptance injections of section 8 and the states around them:
  a brake          BRAKED is a fault: T+10 spawns one BENCH item (needs offline) and a failed steve:lane record, T+30
                   raises it, T+120 with no claim spawns an OWNER item (needs owner); each rung once
  recovery         RUNNING ends the incident: steve:lane ok, a note on the item
  no duplicate     a second incident while the item is open notes it instead of spawning another
  an abandoned claim  a claim's live lease freezes the clock; the lease lapsing (45 min) resumes it
  pauses           a pause with an expiry never escalates before it expires; one without becomes a fault at 60 min;
                   an auto pause (a red canary) is a fault at once; a quarantine and a HARNESS-class brake escalate at once
  quiet states     EXHAUSTED and the day budget are not faults; a ready job is not one for 5 min
  a stopped tick   the watcher sees steward.json go stale, restarts the tick timer ONCE, then escalates; a fresh
                   steward pass recovers it
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
CLI = os.path.join(REPO, "src", "RimMandrake", "rimflow", "cli.py")
STEWARD_ITEM = "STEVE_STEWARD_BUILD_NO_LLM_OWNER"
FAILS = []


def check(ok, msg):
    print(("ok    " if ok else "FAIL  ") + msg)
    if not ok:
        FAILS.append(msg)


def main():
    tmp = tempfile.mkdtemp(prefix="rf_steward_")
    try:
        queue, items = os.path.join(tmp, "queue"), os.path.join(tmp, "items")
        led = os.path.join(tmp, "ledger", "events.jsonl")
        pulse = os.path.join(tmp, "pulse")
        for d in (queue, items, os.path.dirname(led), pulse):
            os.makedirs(d)
        open(led, "w").close()
        for k in ("RIMFLOW_SEAT", "CLAUDE_PROJECT_DIR", "TESTQ_FILL_MODS"):
            os.environ.pop(k, None)
        os.environ.update(TESTQ_QUEUE=queue, RIMFLOW_LEDGER=led, RIMFLOW_ITEMS=items, TESTQ_INGEST_PUSH="0",
                          RM_PULSE_STATE=pulse)
        sys.path.insert(0, HERE)
        import schema as S
        import testq as T
        import steward as W
        W.tick_timer_state = lambda: "active"      # the real one asks this machine's systemd
        check(T.QHOME == queue, "the queue is the temp one")

        def cli(*a, seat="BENCH"):
            r = subprocess.run([sys.executable, CLI] + list(a) + ["--seat", seat], capture_output=True, text=True,
                               timeout=120)
            return r.returncode, r.stdout + r.stderr

        rc, out = cli("file", STEWARD_ITEM, "--for", "BENCH", "--title", "the steward")
        check(rc == 0, "the steward's item is filed in the temp ledger: %s" % out[-200:])
        shard = os.path.join(tmp, "ledger", "events", "RUNNER.jsonl")

        def events(verb=None):
            try:
                evs = [json.loads(x) for x in open(shard)]
            except OSError:
                return []
            return [e for e in evs if verb is None or e.get("event") == verb]

        def pulses():
            try:
                return [json.loads(x) for x in open(os.path.join(pulse, "failures.jsonl"))]
            except OSError:
                return []

        def reset():
            for d in T.STATES:
                shutil.rmtree(T.q(d), ignore_errors=True)
            for f in ("paused.json", "fill.stop", "quarantine.json", "ssh_state.json"):
                if os.path.exists(T.q(f)):
                    os.remove(T.q(f))
            T.ensure_dirs()

        def filler(outcome, cause, at):
            job = S.make_job("Mock", {"chains": ["c1"]}, "guard", T.FILLER, "abc1234")
            job["submitted"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(at))
            res = {"schema": S.RESULT_SCHEMA, "job": job["id"], "attempt": job["id"] + ".a1", "outcome": outcome,
                   "cause": cause, "rows": [], "counts": {}, "runner_sha": "def5678", "artifacts": [], "note": "x"}
            S.dump({"job": job, "result": res, "attempts": [res["attempt"]], "finished": S.utcnow()},
                   T.q("done", job["id"] + ".json"))
            return job

        def running(at):
            job = S.make_job("Mock", {"chains": ["c1"]}, "guard", "BENCH", "abc1234")
            S.dump({"job": job, "attempt": job["id"] + ".a1", "sent": S.utcnow(), "attempts": [job["id"] + ".a1"],
                    "auto_retries": 0, "cancel": False}, T.q("running", job["id"] + ".json"))
            return job

        def step(t):
            return W.steward_pass(now=t, mods=["Mock"])

        base = time.time() - 60
        wakes = []
        W.launch_wake = lambda clone, brief, logp, budget, max_s: wakes.append((clone, open(brief).read(), budget,
                                                                                max_s)) or (True, "ok")
        W.wake_active = lambda: False
        os.environ["TESTQ_WAKE_CLONE"] = REPO
        # ------------------------------------------------ a brake (MOD-class: the normal clock)
        reset()
        j1, j2 = filler("INVALID", "GAME_DIED", base - 3600), filler("INVALID", "HANG", base - 1800)
        ls = W.lane_state(base, ["Mock"])
        check(ls["state"] == "BRAKED" and ls["fault_at"] == 0 and not ls["at_once"] and j1["id"] in ls["jobs"],
              "two non-DONE filler jobs: BRAKED, a fault, with the job ids: %s" % ls)
        rec = step(base)
        check(rec["incident"] and rec["incident"]["level"] == 0 and not events("spawn"),
              "first braked pass opens an incident, escalates nothing: %s" % rec["incident"])
        rec = step(base + 300)
        check(rec["incident"]["unowned_s"] == 300 and not events("spawn"), "T+5 min: clock 300 s, no item yet")
        rec = step(base + 600)
        sp = events("spawn")
        item = rec["incident"]["item"]
        check(rec["incident"]["level"] == 1 and len(sp) == 1 and sp[0]["for"] == "BENCH" and
              sp[0].get("needs") == "offline" and sp[0]["name"] == item and item.startswith(
                  "STEVE_LANE_UNSTICK_BRAKED_UNOWNED_") and j1["id"] in sp[0].get("title", ""),
              "T+10: one BENCH item, needs offline, naming the state and a job: %s" % sp)
        pl = pulses()
        check(pl and pl[-1]["task"] == "steve:lane" and pl[-1]["status"] == "failed" and
              pl[-1]["cause"].startswith("BRAKED"), "T+10: steve:lane failed --cause BRAKED: %s" % pl[-1:])
        step(base + 900)
        check(len(events("spawn")) == 1, "T+15: still one item (no duplicate)")
        rec = step(base + 1800)
        rz = events("raise")
        check(rec["incident"]["level"] == 2 and len(rz) == 1 and rz[0]["id"] == item, "T+30: the item is raised")
        check(len(wakes) == 1 and "RUNBOOK.md" in wakes[0][1] and T.q("steward.json") in wakes[0][1] and
              item in wakes[0][1] and wakes[0][2] == "5" and wakes[0][3] == 2700 and
              (T.read_json(T.q("wake.json")) or {}).get("item") == item,
              "T+30 unanswered: ONE capped wake session, its brief names the state, item and RUNBOOK")
        model, wd = W.world()
        check(wd.items[item].raised is not None, "T+30: the ledger shows it raised")
        step(base + 3600)
        rec = step(base + 7200)
        sp = events("spawn")
        check(rec["incident"]["level"] == 3 and len(sp) == 2 and sp[1]["for"] == "OWNER" and
              sp[1].get("needs") == "owner" and rec["incident"]["owner_item"] == sp[1]["name"] and
              not sp[1]["title"].startswith("IN PERSON"),
              "T+120 with no claim: one OWNER item, needs owner, remote: %s" % sp[1:])
        step(base + 9000)
        check(len(wakes) == 1, "one wake per incident")
        check(len(events("spawn")) == 2 and len(events("raise")) == 1, "past T+120: nothing more is written")
        # ------------------------------------------------ recovery
        notes0 = len(events("note"))
        running(base + 9100)
        rec = step(base + 9100)
        check(rec["state"] == "RUNNING" and rec["incident"] is None and rec["last_item"] == item,
              "RUNNING ends the incident and keeps the item for the next one")
        check(pulses()[-1]["status"] == "ok", "recovery records steve:lane ok")
        check(len(events("note")) == notes0 + 1 and events("note")[-1]["id"] == item, "recovery notes the item")
        # ------------------------------------------------ no duplicate while the item is open
        reset()
        filler("INVALID", "HANG", base), filler("INVALID", "HANG", base)
        step(base + 10000)
        rec = step(base + 10600)
        check(rec["incident"]["item"] == item and len(events("spawn")) == 2 and events("note")[-1]["id"] == item,
              "a second incident while the item is open notes it, never a second item")
        # ------------------------------------------------ an abandoned claim: a live lease freezes the clock
        rc, out = cli("claim", item)
        check(rc == 0, "BENCH claims the item: %s" % out[-160:])
        model, wd = W.world()
        lease = wd.items[item].lease or {}
        exp = model.epoch(lease.get("expires"))
        check(exp and W.claim_holds(item, exp - 60), "a live lease holds the clock")
        check(not W.claim_holds(item, exp + 60), "a lapsed lease does not")
        t0 = exp - 1200
        a = step(t0)["incident"]["unowned_s"]
        b = step(t0 + 600)["incident"]["unowned_s"]
        check(a == b, "while the lease is live the clock does not move (%d -> %d)" % (a, b))
        c1 = step(exp + 10)["incident"]["unowned_s"]
        c = step(exp + 610)["incident"]["unowned_s"]
        check(c1 == b + 10 and c == c1 + 600, "the lease lapsed: only the time after expiry is charged (%d -> %d -> %d)"
              % (b, c1, c))
        check(W.claim_cover(item, exp - 100, exp + 100) == 100 and W.claim_cover(item, exp + 5, exp + 50) == 0
              and W.claim_cover(item, exp - 50, exp - 10) == 40, "claim_cover counts only the seconds under the lease")

        inc = {"state": "BRAKED", "level": 2, "item": item, "unowned_s": 1800}
        check(W.maybe_wake(dict(inc), {"reason": "r"}, exp + 700).startswith("skipped: cooldown") and len(wakes) == 1,
              "a second incident inside the cooldown: no wake")
        check(W.maybe_wake(dict(inc), {"reason": "r"}, exp - 60) is None, "a live claim: no wake")
        open(T.q("wake.stop"), "w").close()
        check(W.maybe_wake(dict(inc), {"reason": "r"}, exp + 20000) is None, "wake.stop: no wake")
        os.remove(T.q("wake.stop"))
        W.wake_active = lambda: True
        check(W.maybe_wake(dict(inc), {"reason": "r"}, exp + 20000).startswith("skipped: a wake session"),
              "one already running: no second")
        W.wake_active = lambda: False
        check(W.maybe_wake(dict(inc), {"reason": "r"}, exp + 20000).startswith("started") and len(wakes) == 2,
              "after the cooldown a new incident may wake again")

        class It:
            open, owner, lease = True, "BENCH", None

        it = It()
        it.claim_ts = model.stamp(base)
        fake = (model, type("Wd", (), {"items": {"X": it}})())
        check(W.claim_holds("X", base + 3600, fake) and not W.claim_holds("X", base + 7300, fake),
              "a claim with no lease holds the clock 2 h, then not")
        # ------------------------------------------------ pauses
        reset()
        S.dump({"since": S.utcnow(), "job": None, "outcome": None, "cause": None, "reason": "owner moving the box",
                "until": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(base + 4 * 3600))}, T.q("paused.json"))
        ls = W.lane_state(base, ["Mock"])
        check(ls["state"] == "PAUSED" and ls["fault_at"] == S.parse_ts(time.strftime(
            "%Y-%m-%dT%H:%M:%SZ", time.gmtime(base + 4 * 3600))), "a pause with an expiry is a fault only after it")
        r = T.main(["pause", "--reason", "x"])
        check(r == 1, "pause refuses when already paused")
        os.remove(T.q("paused.json"))
        T.main(["pause", "--reason", "looking at it"])
        pz = T.paused()
        ls = W.lane_state(time.time(), ["Mock"])
        check(pz and pz["until"] is None and ls["fault_at"] == S.parse_ts(pz["since"]) + 3600,
              "testq pause with no --hours: a fault at 60 min: %s" % ls)
        os.remove(T.q("paused.json"))
        T.main(["pause", "--reason", "rebooting", "--hours", "2"])
        pz = T.paused()
        check(pz["until"] and abs(S.parse_ts(pz["until"]) - time.time() - 7200) < 120, "pause --hours 2 sets until")
        S.dump({"since": S.utcnow(), "job": "J1", "attempt": "J1.a1", "outcome": "INVALID", "cause": "CANARY",
                "reason": "red canary", "note": "n"}, T.q("paused.json"))
        ls = W.lane_state(base, ["Mock"])
        check(ls["state"] == "PAUSED" and ls["fault_at"] == 0, "an auto pause (red canary) is a fault at once")
        open(T.q("quarantine.json"), "w").write('{"reason": "flapping"}')
        ls = W.lane_state(base, ["Mock"])
        check(ls["state"] == "QUARANTINE" and ls["at_once"], "a quarantine escalates at once")
        reset()
        filler("REFUSED", "DEPLOY", base), filler("INVALID", "HANG", base)
        check(W.lane_state(base, ["Mock"])["at_once"], "a brake with a HARNESS-class (DEPLOY) failure: at once")
        S.dump({"down_since": S.utcnow(), "last_probe": base, "last_error": "timeout"}, T.q("ssh_state.json"))
        check(W.lane_state(base, ["Mock"])["state"] == "UNREACHABLE", "ssh down: UNREACHABLE")
        # ------------------------------------------------ quiet states
        reset()
        ls = W.lane_state(base, ["Mock"])
        check(ls["state"] == "IDLE_EMPTY" and ls["fault_at"] == 0, "an empty queue with nothing selectable: "
              "IDLE_EMPTY, a fault (an evidence gap): %s" % ls["reason"])
        real = T.fill_plan
        try:
            T.fill_plan = lambda *a, **k: {"verdict": "exhausted", "text": "nothing to fill"}
            ls = W.lane_state(base, ["Mock"])
            check(ls["state"] == "EXHAUSTED" and ls["fault_at"] is None, "EXHAUSTED is not a fault")
            T.fill_plan = lambda *a, **k: {"verdict": "budget", "text": "cap: day budget"}
            ls = W.lane_state(base, ["Mock"])
            check(ls["state"] == "BRAKED" and ls["fault_at"] is None, "the day budget is a brake, not a fault")
        finally:
            T.fill_plan = real
        job = S.make_job("Mock", {"chains": ["c1"]}, "guard", "BENCH", "abc1234")
        S.dump(job, T.q("pending", job["id"] + ".json"))
        ls = W.lane_state(S.parse_ts(job["submitted"]) + 60, ["Mock"])
        check(ls["state"] == "READY" and ls["fault_at"] == S.parse_ts(job["submitted"]) + 300,
              "a ready job is a fault only after 5 min not admitted")
        # ------------------------------------------------ the tick TIMER stopped (2026-10-28 05:04: an agent stopped
        # every rm-*/testq-* timer for a cutover and never restarted them; the steward, run by hand, blamed the fill)
        W.tick_timer_state = lambda: "inactive"
        ls = W.lane_state(S.parse_ts(job["submitted"]) + 60, ["Mock"])
        check(ls["state"] == "TICK_STOPPED" and ls["fault_at"] == 0 and ls["at_once"]
              and "testq-tick.timer" in ls["reason"] and "systemctl --user start" in ls["reason"],
              "a stopped tick timer outranks READY: TICK_STOPPED, a fault at once, naming the fix: %s" % ls["reason"])
        os.remove(T.q("pending", job["id"] + ".json"))
        ls = W.lane_state(base, ["Mock"])
        check(ls["state"] == "TICK_STOPPED", "an empty queue with a stopped tick is TICK_STOPPED, not IDLE_EMPTY "
              "'the fill failed?': %s" % ls["state"])
        check(W.TAG.get("TICK_STOPPED") == "STALLED", "TICK_STOPPED has a pulse tag")
        W.tick_timer_state = lambda: None          # no systemd here (the dispatch clone, a test box): no verdict
        check(W.lane_state(base, ["Mock"])["state"] == "IDLE_EMPTY", "an unknown timer state changes nothing")
        W.tick_timer_state = lambda: "active"
        # review r1: RUNNING and an intentional pause both outrank a stopped tick (header: only RUNNING ends an incident)
        reset()
        W.tick_timer_state = lambda: "inactive"
        S.dump({"since": S.utcnow(), "job": None, "outcome": None, "cause": None, "reason": "cutover",
                "until": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(base + 4 * 3600))}, T.q("paused.json"))
        ls = W.lane_state(base, ["Mock"])
        check(ls["state"] == "PAUSED" and ls["fault_at"] != 0, "a future-expiry pause outranks a stopped tick: %s"
              % ls["state"])
        os.remove(T.q("paused.json"))
        running(base)
        check(W.lane_state(base, ["Mock"])["state"] == "RUNNING", "a running job outranks a stopped tick")
        reset()
        W.tick_timer_state = lambda: "active"
        # ------------------------------------------------ a stopped tick: the watcher
        reset()
        restarts = []
        W.restart_tick = lambda: restarts.append(1) or "exit 0"
        running(base)
        rec = step(base)
        n_spawn = len(events("spawn"))
        w0 = W.watch_pass(now=base + 120)
        check(w0["incident"] is None, "a fresh steward.json: no incident")
        w1 = W.watch_pass(now=base + 400)
        check(w1["incident"] and w1["incident"]["state"] == "STALE_HEARTBEAT" and len(restarts) == 1,
              "steward.json 400 s old: STALE_HEARTBEAT, the tick timer restarted once")
        W.watch_pass(now=base + 460)
        check(len(restarts) == 1 and len(events("spawn")) == n_spawn, "still stale: no second restart, not yet T+10")
        w3 = W.watch_pass(now=base + 700)
        sp = events("spawn")
        check(w3["incident"]["level"] == 1 and len(restarts) == 1 and pulses()[-1]["status"] == "failed",
              "stale past T+10 after the restart failed: escalated (item %s)" % w3["incident"].get("item"))
        check(len(sp) == n_spawn or sp[-1]["name"].startswith("STEVE_LANE_UNSTICK_STALLED_"),
              "the watcher's item names the stall (or refreshes the open one)")
        step(base + 760)
        w4 = W.watch_pass(now=base + 780)
        check(w4["incident"] is None and pulses()[-1]["status"] == "ok", "a fresh steward pass: the watcher recovers")
        j = [json.loads(x) for x in open(T.q("steward.jsonl"))]
        check(any(e["event"] == "restart" for e in j) and any(e["event"] == "state" for e in j),
              "steward.jsonl holds state changes and the restart")
        # ------------------------------------------------ review r2: watcher recovery, refused raise, lock, dup
        reset()
        S.dump({"epoch": base + 1000, "incident": {"state": "BRAKED", "level": 1, "unowned_s": 700, "item": item},
                "state": "BRAKED", "fault": True}, T.q("steward.json"))
        S.dump({"first_seen": base, "incident": {"state": "STALE_HEARTBEAT", "level": 0, "unowned_s": 400,
                                                 "item": None}}, T.q("steward_watch.json"))
        W.failreport(False, "BRAKED: x")
        n = len(pulses())
        W.watch_pass(now=base + 1010)
        check(pulses()[-1]["status"] == "failed" and len(pulses()) == n,
              "the heartbeat is fresh but the steward still holds a fault incident: the watcher does not clear the row")
        real_rf = W.rimflow
        W.rimflow = lambda *a: (1, "rimflow: only an open item can be raised")
        inc = {"state": "BRAKED", "since": "x", "unowned_s": 2000, "level": 1, "item": item, "owner_item": None}
        W.escalate(inc, {"reason": "r", "jobs": []}, base + 5, item)
        check(inc["level"] == 1 and inc.get("error"), "a refused raise is not recorded as level 2")
        W.rimflow = real_rf
        reset()
        fd = W.lock_open()
        try:
            W.LOCK_WAIT_S = 0.3
            check(W.steward_pass(now=base + 20000, mods=["Mock"]) is None, "a concurrent pass is refused by the lock")
        finally:
            fd.close()
        W.LOCK_WAIT_S = 30
        # a spawn that landed but whose incident never reached disk: the next pass finds the open item, no duplicate
        filler("INVALID", "HANG", base), filler("INVALID", "HANG", base)
        step(base + 30000)
        step(base + 30700)
        n1 = len(events("spawn"))
        os.remove(T.q("steward.json"))
        step(base + 31000)
        step(base + 31700)
        check(len(events("spawn")) == n1, "a lost steward.json does not mint a second item while one is open")
        # ------------------------------------------------ units
        units = T.UNITS["testq-tick.service"]
        order = [units.find(x) for x in ("testq.py tick", "testq.py fill", "testq.py steward", "ingest.py")]
        check(all(o > 0 for o in order) and order == sorted(order), "tick service: tick, fill, steward, ingest")
        check("testq-steward-watch.timer" in T.UNITS and "steward-watch" in T.UNITS["testq-steward-watch.service"]
              and "pull" not in T.UNITS["testq-steward-watch.service"], "the watcher has its own timer and never pulls")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    print("ALL PASS" if not FAILS else "%d FAILED" % len(FAILS))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
