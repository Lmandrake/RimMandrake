#!/usr/bin/env python3
"""selftest_brake_release.py - the filler brake's known causes (STEVE_BRAKE_FIX_KNOWN_CAUSES_RELEASE): a cancel never
counts, Operations' deterministic canary on a brake with recorded non-fault causes, and everything else escalating."""
import json
import os
import shutil
import sys
import tempfile
import time

HERE = os.path.dirname(os.path.abspath(__file__))
FAILS = []


def check(ok, msg):
    print(("ok    " if ok else "FAIL  ") + msg)
    if not ok:
        FAILS.append(msg)


def main():
    tmp = tempfile.mkdtemp(prefix="rf_brake_")
    os.environ.update(TESTQ_QUEUE=tmp, TESTQ_INGEST_PUSH="0")
    os.environ.pop("TESTQ_FILL_MODS", None)
    sys.path.insert(0, HERE)
    import schema as S
    import testq as T
    import brake_release as BR
    import steward as W
    W.tick_timer_state = lambda: "active"
    T.preview = lambda mod, sel: {"refusal": None, "rows": None, "drivers": [], "chains": None}
    T.fill_rank = lambda mod, n, now, today=None, exclude=(): {"verdict": "exhausted", "pick": [], "text": "x"}
    now = time.time()
    check(T.QHOME == tmp, "the queue is the temp one")
    T.ensure_dirs()

    def iso(t):
        return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(t))

    def wipe():
        for d in T.STATES:
            for f in os.listdir(T.q(d)):
                os.remove(T.q(d, f))
        for f in ("lane_windows.jsonl", "brake_release.json", "ssh_state.json", "quarantine.json", "paused.json",
                  "steward.json"):
            if os.path.exists(T.q(f)):
                os.remove(T.q(f))

    def job(at, by=T.FILLER, canary=True):
        j = S.make_job("Mock", {"chains": ["c1"]}, "guard", by, "abc1234", canary=canary)
        j["id"] = j["id"][:-6] + "%06x" % (abs(hash((at, by))) % 0xffffff)
        j["submitted"] = iso(at)
        return j

    def done(at, outcome, cause, cancelled=False, by=T.FILLER, canary=True, sent=None):
        j = job(at, by, canary)
        res = {"schema": S.RESULT_SCHEMA, "job": j["id"], "attempt": j["id"] + ".a1", "outcome": outcome, "cause": cause,
               "rows": [], "counts": {}, "runner_sha": "d", "artifacts": [], "note": "x", "started": iso(at),
               "finished": iso(at + 60)}
        rec = {"job": j, "result": res, "attempts": [res["attempt"]], "cancelled": cancelled, "finished": iso(at + 60)}
        if sent:
            rec["sent"] = iso(sent)
        S.dump(rec, T.q("done", j["id"] + ".json"))
        return j

    def cancelled_pending(at):
        j = job(at)
        S.dump({"job": j, "reason": "by hand", "at": iso(at)}, T.q("cancelled", j["id"] + ".json"))
        return j

    def window(t0, t1, kind="maintenance"):
        T.record_lane_window(kind, iso(t0), iso(t1), "test")

    def plan():
        return T.fill_plan("Mock", 1, 1000, 10 ** 9, now)

    def pending_canaries():
        return [j for j in T.records("pending") if j.get("requested_by") == BR.BY]

    day = now - 3 * 86400       # outside today's cap, and every window below is ours

    # ------------------------------------------------ clause 1: a deliberate cancel never counts
    done(day, "INVALID", "HARNESS")
    done(day + 100, "REFUSED", "SYNC", cancelled=True)
    check(plan()["verdict"] != "brake", "one failure and a cancelled running job: no brake")
    wipe()
    done(day, "INVALID", "HARNESS")
    cancelled_pending(day + 100)
    check(plan()["verdict"] != "brake", "one failure and a cancelled pending job: no brake")
    wipe()
    done(day, "INVALID", "HARNESS", cancelled=True)
    done(day + 100, "INVALID", "HARNESS", cancelled=True)
    check(plan()["verdict"] != "brake", "two cancels: no brake")
    wipe()
    a, b = done(day, "INVALID", "HARNESS"), done(day + 200, "INVALID", "LOAD")
    done(day + 100, "REFUSED", "SYNC", cancelled=True)
    cancelled_pending(day + 300)
    p = plan()
    check(p["verdict"] == "brake" and sorted(T.job_of(t)["id"] for t in p["tail"]) == sorted([a["id"], b["id"]]),
          "a cancel neither brakes nor hides two real failures around it: %s" % p.get("text"))

    # ------------------------------------------------ the cause reader
    wipe()
    wins = [("maintenance", day, day + 1000)]
    def rec(outcome, cause, at, **kw):
        res = {"outcome": outcome, "cause": cause, "started": iso(at), "finished": iso(at)}
        return dict({"result": res, "finished": iso(at)}, **kw)
    check(T.nonfault_cause(rec("REFUSED", "SYNC", 0, cancelled=True), []) == "cancel", "cancelled -> cancel, any outcome")
    check(T.nonfault_cause(rec("INTERRUPTED", "CRASH", day + 500), wins) == "maintenance", "killed inside a window")
    check(T.nonfault_cause(rec("INVALID", "GAME_DIED", day + 500), wins) == "maintenance", "the game died inside a window")
    check(T.nonfault_cause(rec("INTERRUPTED", "CRASH", day + 5000), wins) is None, "killed outside any window: a fault")
    check(T.nonfault_cause(rec("INTERRUPTED", "CRASH", day + 5000, sent=iso(day + 500)), wins) == "maintenance",
          "admitted in the window, the record finished after it: its span overlaps")
    for oc in (("INVALID", "DEPLOY"), ("REFUSED", "SYNC"), ("INVALID", "CANARY"), ("INVALID", "HARNESS")):
        check(T.nonfault_cause(rec(oc[0], oc[1], day + 500), wins) is None, "%s/%s inside a window is still the lane's fault" % oc)
    check(T.nonfault_cause(rec("INTERRUPTED", "CRASH", day + 500, finished="garbage"), wins) is None,
          "an unreadable stamp excuses nothing")
    with open(T.q("lane_windows.jsonl"), "w") as f:
        f.write('{"kind": "maintenance", "since": "torn\n')
    check(T.lane_windows(now) == [], "a torn window line says nothing")

    # ------------------------------------------------ recording a window: the three doors
    wipe()
    S.dump({"since": iso(day), "until": iso(day + 7200), "outcome": None, "reason": "NVMe"}, T.q("paused.json"))
    check(("maintenance", S.parse_ts(iso(day)), now) in T.lane_windows(now), "a live pause --hours is an open window")
    import argparse
    T.cmd_resume(argparse.Namespace(reason="back", lane=None))
    check(any(k == "maintenance" and s == S.parse_ts(iso(day)) for k, s, u in T.lane_windows(now)),
          "resuming it keeps the window")
    wipe()
    S.dump({"since": iso(day), "until": None, "outcome": None, "reason": "held"}, T.q("paused.json"))
    T.cmd_resume(argparse.Namespace(reason="back", lane=None))
    check(T.lane_windows(now) == [], "a pause with no expiry is not a window")
    S.dump({"since": iso(day), "until": None, "outcome": "INVALID", "cause": "CANARY", "reason": "red"}, T.q("paused.json"))
    T.cmd_resume(argparse.Namespace(reason="back", lane=None))
    check(T.lane_windows(now) == [], "an auto pause is not a window")
    wipe()
    S.dump({"down_since": iso(day), "last_probe": 0, "last_error": "timed out"}, T.q("ssh_state.json"))
    check(any(k == "machine_down" for k, s, u in T.lane_windows(now)), "ssh down now is an open window")
    real_remote = T.remote
    T.remote = lambda args, stdin=None, timeout=180: (0, {"state": "idle"})
    T.ssh_reachable()
    T.remote = real_remote
    w = T.lane_windows(now)
    check(len(w) == 1 and w[0][0] == "machine_down" and w[0][1] == S.parse_ts(iso(day)), "ssh back keeps the outage: %s" % w)
    wipe()
    check(T.main(["maintenance", "--reason", "BIOS", "--since", iso(day), "--until", iso(day + 60)]) == 0
          and [x[0] for x in T.lane_windows(now)] == ["maintenance"], "testq.py maintenance records one by hand")
    check(T.main(["maintenance", "--reason", "x", "--since", iso(day + 60), "--until", iso(day)]) == 2,
          "maintenance refuses since after until")
    check(T.main(["maintenance", "--reason", "x", "--since", "yesterday"]) == 2, "maintenance refuses a bad stamp")

    # ------------------------------------------------ clause 2: one canary, no LLM
    wipe()
    a, b = done(day, "INTERRUPTED", "CRASH"), done(day + 200, "INVALID", "GAME_DIED")
    window(day - 10, day + 400)
    r = BR.release_pass(now, ["Mock"])
    c = pending_canaries()
    check(r["state"] == "released" and len(c) == 1, "both tail jobs known: released, one canary: %s" % r)
    check(c and c[0]["canary"] is True and c[0]["selector"].get("chains") == ["c1"] and c[0]["lane"] == T.STEVE,
          "the canary job has its canary on, on the Steve lane, one chain")
    check(c and c[0]["requested_by"] == BR.BY and c[0]["requested_by"] != T.FILLER, "and never enters the filler's window")
    check(sorted(r["causes"].values()) == ["maintenance", "maintenance"] and r["canary"]["job"] == c[0]["id"],
          "the reading names the causes and the job")
    r2 = BR.release_pass(now + 60, ["Mock"])
    check(len(pending_canaries()) == 1 and r2["state"] == "none", "next pass: the lane is busy, no second canary: %s" % r2)
    check(r2["canary"]["job"] == c[0]["id"], "the spent canary stays on the record")
    # it failed: same tail, no loop, escalate
    os.remove(T.q("pending", c[0]["id"] + ".json"))
    fail = dict(c[0])
    res = {"schema": S.RESULT_SCHEMA, "job": fail["id"], "attempt": fail["id"] + ".a1", "outcome": "INVALID", "cause": "CANARY",
           "rows": [], "counts": {}, "runner_sha": "d", "artifacts": [], "note": "x", "finished": iso(now)}
    S.dump({"job": fail, "result": res, "attempts": [res["attempt"]], "finished": iso(now)}, T.q("done", fail["id"] + ".json"))
    r3 = BR.release_pass(now + 120, ["Mock"])
    check(r3["state"] == "escalate" and "spent" in r3["reason"] and not pending_canaries(),
          "the canary came back red: escalate, no second one: %s" % r3)
    ls = W.lane_state(now + 120, ["Mock"])
    check(ls["state"] == "BRAKED" and ls["fault_at"] == 0, "and the steward calls it a fault now: %s" % ls["reason"][:80])
    # it went green: the brake ends
    res.update(outcome="DONE", cause=None, finished=iso(now + 200))
    S.dump({"job": fail, "result": res, "attempts": [res["attempt"]], "finished": iso(now + 200)}, T.q("done", fail["id"] + ".json"))
    check(plan()["verdict"] != "brake", "the canary DONE: the brake is released")
    r4 = BR.release_pass(now + 240, ["Mock"])
    check(r4["state"] == "none", "and Operations has nothing left to do: %s" % r4)

    # the filler's pick is preferred, and carries its row items
    wipe()
    done(day, "INTERRUPTED", "CRASH"), done(day + 200, "INTERRUPTED", "CRASH")
    window(day - 10, day + 400)
    saved = T.fill_rank
    T.fill_rank = lambda mod, n, now, today=None, exclude=(): {"verdict": "pick", "pick": ["cA", "cB"], "purpose": "guard",
                                                                "row_items": {"cA": "ITEM_A", "cB": "ITEM_B"}, "text": "x"}
    BR.release_pass(now, ["Mock"])
    T.fill_rank = saved
    c = pending_canaries()
    check(c and c[0]["selector"]["chains"] == ["cA"] and c[0]["row_items"] == {"cA": "ITEM_A"},
          "the canary is one chain of the filler's own pick: %s" % (c and c[0]["selector"]))

    # a refused submit is said, and retried
    wipe()
    done(day, "INTERRUPTED", "CRASH"), done(day + 200, "INTERRUPTED", "CRASH")
    window(day - 10, day + 400)
    real_preview = T.preview
    T.preview = lambda mod, sel: {"refusal": "bad row", "rows": None, "drivers": [], "chains": None}
    r = BR.release_pass(now, ["Mock"])
    T.preview = real_preview
    check(r["state"] == "refused" and "bad row" in r["reason"] and not r.get("canary"), "a refused submit: said, not spent: %s" % r)
    r = BR.release_pass(now + 60, ["Mock"])
    check(r["state"] == "released", "and tried again next pass")

    # the machine down or quarantined: wait
    wipe()
    done(day, "INTERRUPTED", "CRASH"), done(day + 200, "INTERRUPTED", "CRASH")
    window(day - 10, day + 400)
    S.dump({"down_since": iso(now - 60), "last_probe": now, "last_error": "x"}, T.q("ssh_state.json"))
    r = BR.release_pass(now, ["Mock"])
    check(r["state"] == "wait" and not pending_canaries(), "machine down: no canary: %s" % r)
    os.remove(T.q("ssh_state.json"))
    S.dump({"reason": "by hand"}, T.q("quarantine.json"))
    r = BR.release_pass(now, ["Mock"])
    check(r["state"] == "wait" and not pending_canaries(), "quarantined: no canary")
    os.remove(T.q("quarantine.json"))

    # a stop file, an auto pause: not ours to lift
    open(T.q("fill.stop"), "w").close()
    r = BR.release_pass(now, ["Mock"])
    check(r["state"] == "none" and not pending_canaries(), "a stop file comes first: %s" % r["reason"][:60])
    os.remove(T.q("fill.stop"))

    # ------------------------------------------------ clause 3's first half: otherwise escalate
    wipe()
    done(day, "INTERRUPTED", "CRASH"), done(day + 200, "INVALID", "DEPLOY")
    window(day - 10, day + 400)
    r = BR.release_pass(now, ["Mock"])
    check(r["state"] == "escalate" and not pending_canaries() and "no recorded non-fault cause" in r["reason"],
          "one job with no cause: no canary, escalate: %s" % r["reason"][:80])
    ls = W.lane_state(now, ["Mock"])
    check(ls["state"] == "BRAKED" and ls["fault_at"] == 0 and ls["at_once"], "the steward's HARNESS brake still fires at once")
    wipe()
    done(day, "INTERRUPTED", "CRASH"), done(day + 200, "INTERRUPTED", "CRASH")
    r = BR.release_pass(now, ["Mock"])
    check(r["state"] == "escalate" and not pending_canaries(), "killed with no record of why: escalate, a person looks")

    # the steward holds a known brake while Operations owes its canary, for a grace only
    wipe()
    fresh = now - 300
    done(fresh - 200, "INTERRUPTED", "CRASH"), done(fresh, "INTERRUPTED", "CRASH")
    window(fresh - 300, fresh + 100)
    ls = W.lane_state(now, ["Mock"])
    check(ls["state"] == "BRAKED" and abs(ls["fault_at"] - (fresh + 60 + BR.RELEASE_GRACE_S)) < 2
          and not ls["at_once"] and "Operations" in ls["reason"], "a known brake: a fault only after the grace: %s" % ls)
    rec = W.steward_pass(now=now, mods=["Mock"])
    check(rec["fault"] is False and rec["incident"] is None, "no incident opens inside the grace")
    rec = W.steward_pass(now=fresh + 60 + BR.RELEASE_GRACE_S + 5, mods=["Mock"])
    check(rec["fault"] is True, "past the grace (Operations never came) it is a plain fault")

    # ------------------------------------------------ today's brake, replayed
    wipe()
    d0 = S.parse_ts("2026-11-01T23:47:11Z")
    done(d0, "DONE", None)
    done(d0 + 900, "INTERRUPTED", "CRASH")
    done(d0 + 900 + 150000, "REFUSED", "SYNC", cancelled=True)
    T.record_lane_window("maintenance", "2026-11-02T00:13:21Z", "2026-11-03T19:11:33Z", "NVMe swap")
    check(plan()["verdict"] != "brake", "2026-11-03: the cancelled SYNC job is out, so the filler was never braked")

    src = open(os.path.join(HERE, "brake_release.py"), encoding="utf-8").read()
    check("claude" not in src.lower().replace("no llm", "") and "gpt" not in src.lower(), "no LLM in the release pass")
    print(json.dumps({"fails": len(FAILS)}))
    shutil.rmtree(tmp, ignore_errors=True)
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
