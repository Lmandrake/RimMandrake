#!/usr/bin/env python3
"""Selftest of the Designer's stage chain (DESIGNER_STAGES_WIRE_NOBODY_PRESSED_GO). A run-now runs ONE stage; before
this, a run that closed 'stage N done' left the concept ready and nothing launched stage N+1 until the
queues.designer.stalled_min alarm (OPS_DESIGNER_UNSTICK_READY_AND_WAITING_GZKV). Now the harvest
(role_launch._supervise_one -> chain_next) asks the next run-now itself, and the next decide launches it through the
run-now gates. Pure: fake obs, a temp dir, no systemd, no git."""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import selftest_dispatcher as SD  # noqa: E402  (fixtures; its own tests do not run on import)

RL = SD.RL
FAILS = []
T = SD.at_local("13:00")             # no fixture slot (11:00, 17:00) is due: only a run-now can launch
C1, C2 = "/tmp/concepts/ModOne", "/tmp/concepts/ModTwo"


def check(ok, msg):
    print("%s %s" % ("ok  " if ok else "FAIL", msg))
    if not ok:
        FAILS.append(msg)


def designer_row():
    sch = json.load(open(os.path.join(HERE, "dispatcher_schedule.json"), encoding="utf-8"))
    return next(r for r in sch["roles"] if isinstance(r, dict) and r.get("stage_machine") == "designer_stage")


def harvest(rs, status, ok=True, concept=C1, unit="rm-role-designer-1", cfg=None):
    """One finished Designer run on `concept` through the real supervisor; status = the stage.json after its close."""
    rs.setdefault("runs", []).append({"state": "running", "unit": unit, "at": T - 600, "day": RL.day_of(T),
                                      "budget": 90000, "mode": "run", "item": "X_ITEM", "concept": concept,
                                      "scope": "S.scope", "marker": "M"})
    res = {"subtype": "success", "usage": {k: 10 for k in RL.USAGE_KEYS}}
    acts = []
    obs = {"unit_state": lambda u: "inactive", "result": lambda r: res, "procs": lambda *a, **k: [],
           "stage_close": lambda c, u, t: (ok, [] if ok else ["bad result"]), "stage_land": lambda c, u: None,
           "stage_turn": lambda c: None, "stage_status": lambda c: status if not callable(status) else status(c)}
    RL._supervise_one("Designer", rs, cfg or dict(RL.ROLE_DEFAULTS, **designer_row()), obs, T,
                      lambda **kw: acts.append(kw), set())
    return acts


def test_row():
    row = designer_row()
    check(row.get("chain_stages") is True and "chain" in row.get("trigger", ""),
          "the Designer row sets chain_stages true and its trigger names the chain")
    check(not row.get("enabled") and not row.get("runs_local"), "the row still has no schedule (enabled false, no slots)")


def test_done_chains():
    rs = {}
    acts = harvest(rs, {"stage": 4, "status": "ready"})
    r = rs.get("run_now")
    check(isinstance(r, dict) and r.get("concept") == C1 and r.get("by") == "Dispatcher" and r.get("mode") == "run"
          and r.get("chained_from") == "rm-role-designer-1" and r.get("at") == T,
          "an accepted stage-3-done harvest on a ready concept asks a run-now for it: %r" % r)
    check(any(a["do"] == "role_hold" and "chained" in a["why"] for a in acts), "the chain is said on the ledger")
    # the next decide launches it (a disabled role, like the Designer), through the stage machine's open
    st = SD.fresh()
    st["roles"] = {"Arbiter": dict({"done": {}, "runs": []}, run_now=r)}
    opened = []
    ro = SD.lrobs(SD.ops_status(T), lambda: None)
    ro["stage_open"] = lambda c, u, b: (opened.append(c), ("PACKET", b))[1]
    ro["coverage_pre"] = lambda c: None
    la = [a for a in SD.role_acts(SD.rdecide([SD.arbiter(enabled=False)], st, ro, T + 60)) if a["do"] == "role_launch"]
    check(len(la) == 1 and opened == [C1] and "chain:" in la[0]["why"],
          "the next decide launches the chained run on that concept: %r %r" % (opened, [a["do"] for a in la]))


def test_no_chain_states():
    for status in ({"stage": 2, "status": "waiting_owner"}, {"stage": 2, "status": "blocked"},
                   {"stage": 5, "status": "locked"}):
        rs = {}
        harvest(rs, status)
        check("run_now" not in rs and not rs.get("run_now_queue"), "status %s chains nothing" % status["status"])
    rs = {}
    harvest(rs, {"stage": 3, "status": "ready"}, ok=False)
    check("run_now" not in rs, "a REJECTED result chains nothing (its alarm stands)")
    rs = {}
    harvest(rs, {"stage": 3, "status": "ready"}, cfg=dict(RL.ROLE_DEFAULTS, **dict(designer_row(), chain_stages=False)))
    check("run_now" not in rs, "a row without chain_stages chains nothing")

    def boom(c):
        raise RuntimeError("unreadable")
    rs = {}
    acts = harvest(rs, boom)
    check("run_now" not in rs and any(a.get("kind") == "role:Designer:chain" for a in acts),
          "an unreadable stage.json chains nothing and alarms")


def test_queue_behind_pending():
    hand = {"at": T - 30, "by": "BENCH", "why": "start ModTwo", "mode": "run", "concept": C2}
    rs = {"run_now": dict(hand)}
    harvest(rs, {"stage": 1, "status": "ready"})
    check(rs["run_now"] == hand and [q["concept"] for q in rs.get("run_now_queue") or []] == [C1],
          "a pending run-now keeps its slot; the chain waits behind it: %r" % rs.get("run_now_queue"))
    harvest(rs, {"stage": 2, "status": "ready"}, unit="rm-role-designer-2")
    check(len(rs["run_now_queue"]) == 1, "one queued entry per concept")
    rs2 = {"run_now": dict(hand, concept=C1)}
    harvest(rs2, {"stage": 1, "status": "ready"})
    check(rs2["run_now"]["by"] == "BENCH" and not rs2.get("run_now_queue"),
          "a pending run-now on the same concept already covers it")
    # the queued entry takes the slot once it frees, stamped at that moment
    rs.pop("run_now")
    RL.chain_pop(rs, T + 900)
    check(rs.get("run_now", {}).get("concept") == C1 and rs["run_now"]["at"] == T + 900 and "run_now_queue" not in rs,
          "a free slot takes the queued chain, its TTL starting now: %r" % rs.get("run_now"))
    st = SD.fresh()
    st["roles"] = {"Arbiter": {"done": {}, "runs": [], "run_now_queue": [dict(hand, concept=C1, at=T)]}}
    ro = SD.lrobs(SD.ops_status(T), lambda: None)
    ro["stage_open"] = lambda c, u, b: ("PACKET", b)
    ro["coverage_pre"] = lambda c: None
    la = [a for a in SD.role_acts(SD.rdecide([SD.arbiter(enabled=False)], st, ro, T + 60)) if a["do"] == "role_launch"]
    check(len(la) == 1 and "run_now_queue" not in st["roles"]["Arbiter"], "decide pops the queue and launches it")


def test_daily_cap():
    rs = {}
    cfg = dict(RL.ROLE_DEFAULTS, **dict(designer_row(), chain_max_per_day=2))
    for i in range(2):
        harvest(rs, {"stage": i + 1, "status": "ready"}, unit="u%d" % i, cfg=cfg)
        check(rs.pop("run_now", None) is not None, "chain %d of 2 asked" % (i + 1))
    acts = harvest(rs, {"stage": 1, "status": "ready"}, unit="u9", cfg=cfg)
    check("run_now" not in rs and [a.get("kind") for a in acts if a["do"] == "alarm"] == ["role:Designer:chain_cap"],
          "past chain_max_per_day the loop stops with one chain_cap alarm: %r" % [a.get("kind") for a in acts])
    other = harvest(rs, {"stage": 1, "status": "ready"}, unit="u10", concept=C2, cfg=cfg)
    check(rs.get("run_now", {}).get("concept") == C2 and not [a for a in other if a["do"] == "alarm"],
          "the cap is per concept")


def main():
    for t in (test_row, test_done_chains, test_no_chain_states, test_queue_behind_pending, test_daily_cap):
        t()
    print("selftest_designer_chain: %s" % ("FAIL %d" % len(FAILS) if FAILS else "PASS"))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
