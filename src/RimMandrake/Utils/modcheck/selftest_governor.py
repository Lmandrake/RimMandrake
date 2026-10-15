#!/usr/bin/env python3
"""Selftest: the row governor (modcheck/governor.py), TELEMETRY_COLONY_VITALS_BUILD_SPEC_SAID_SO.

Every owner ruling of 2026-10-13 (debug_process.md "Test disturbances") and every offline row of GPT §5's acceptance
table is a check: damage restarts (never FAIL), a corrected anomaly may PASS, every threat yields a valid
test-environment item line, protection is refused on health rows, coverage loss prevents CLEAN, an expected
transition is accepted while an extra one is still flagged, declared vs undeclared clock jumps. No game, no bridge.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.abspath(os.path.join(HERE, "..", "..", "rimflow")))

import governor as G  # noqa: E402

N = [0, 0]


def check(ok, name, why=""):
    N[0] += 1
    if not ok:
        N[1] += 1
    print(("ok   " if ok else "FAIL ") + name + ("" if ok else "  " + str(why)))


def T(seq, kind, sev, subject_id=-1, subject=None, declared=False, tick=100, detail=None):
    return {"seq": seq, "kind": kind, "severity": sev, "subjectId": subject_id, "subject": subject,
            "declared": declared, "tick": tick, "detail": detail or kind}


class FakeSession(object):
    """Answers jawa/vitals + jawa/safe_advance from a scripted list of triggers per attempt."""

    def __init__(self, attempts):
        self.attempts, self.n, self.calls = attempts, -1, []

    def call(self, tool, **p):
        self.calls.append((tool, p))
        if tool == "jawa/vitals" and p.get("action") == "arm":
            self.n += 1
            return {"success": True, "armed": True, "latched": {"seq": 0}}
        if tool == "jawa/vitals" and p.get("action") == "events":
            return {"success": True, "triggers": self.attempts[self.n], "truncated": 0}
        if tool == "jawa/vitals" and p.get("action") == "disarm":
            return {"success": True}
        if tool == "jawa/vitals":
            return {"success": True, "armed": True}
        if tool == "jawa/safe_advance":
            if p["ticks"] > 30000 and not p.get("timeException"):
                return {"success": False, "state": "refused", "refused": "over budget", "requested": p["ticks"], "executed": 0}
            return {"success": True, "state": "done", "requested": p["ticks"], "executed": p["ticks"]}
        return {"success": False}


def main():
    c = G.RowContract("pyre_ash_survives", about=("terrain",), actors=("Human12",), specimens=("Ash40",))

    # --- clean: nothing happened -> the criterion decides
    v = G.judge(c, [], "PASS")
    check(v["outcome"] == G.PASS and v["validity"] == "CLEAN" and not v["env_items"], "clean_row_passes", v)
    check(G.judge(c, [], "FAIL")["outcome"] == G.FAIL, "clean_row_fail_is_a_real_fail")

    # --- worker downed during the wait: DISRUPTED, RESTART, never FAIL (GPT §5 row 6)
    v = G.judge(c, [T(1, "downed", "damage", 12, "Ann")], "FAIL")
    check(v["outcome"] == G.RESTART and v["validity"] == "DISRUPTED", "downed_worker_restarts_not_fail", v["outcome"])
    check(any("NOT scored" in n for n in v["notes"]), "restart_says_criterion_not_scored", v["notes"])
    check(v["first_disturbance"]["seq"] == 1, "first_disturbance_recorded")

    # --- corrected anomaly with no damage: may PASS (owner)
    trig = [T(3, "hostile_arrival", "threat", 77, "Thrumbo")]
    v = G.judge(c, trig, "PASS", corrected={3})
    check(v["outcome"] == G.PASS and v["validity"] == "CLEAN" and "corrected" in " ".join(v["notes"]), "corrected_anomaly_may_pass", v)
    check(len(v["env_items"]) == 1 and "TESTENV_HOSTILES_HARDEN_KNOCK_FIRST" in v["env_items"][0], "every_threat_gets_an_item_even_when_passed", v["env_items"])

    # --- uncorrected anomaly, no damage: cannot certify, not a restart
    v = G.judge(c, trig, "PASS")
    check(v["outcome"] == G.UNMEASURED and v["validity"] == "INDETERMINATE", "uncorrected_anomaly_is_unmeasured", v["outcome"])

    # --- colony loss / specimen lost / death of an actor -> restart
    for kind in ("colony_loss", "specimen_lost"):
        check(G.judge(c, [T(1, kind, "damage")], "PASS")["outcome"] == G.RESTART, "%s_restarts" % kind)
    check(G.judge(c, [T(1, "death", "damage", 12)], "PASS")["outcome"] == G.RESTART, "actor_death_restarts")
    check(G.judge(c, [T(1, "death", "info", 99, "raider")], "PASS")["outcome"] == G.PASS, "hostile_death_is_info")

    # --- clock: undeclared jump -> restart; declared under a time exception -> allowed, noted; declared without -> restart
    check(G.judge(c, [T(1, "clock_discontinuity", "clock")], "PASS")["outcome"] == G.RESTART, "undeclared_clock_jump_not_clean")
    ct = G.RowContract("solar_timer", about=("growth",), time_exception=True)
    v = G.judge(ct, [T(1, "clock_discontinuity", "clock", declared=True)], "PASS")
    check(v["outcome"] == G.PASS and any("declared" in n for n in v["notes"]), "declared_clock_with_exception_allowed", v)
    check(G.judge(c, [T(1, "clock_discontinuity", "clock", declared=True)], "PASS")["outcome"] == G.RESTART,
          "declared_clock_without_row_exception_restarts")

    # --- coverage: monitor expiry / read failure prevents CLEAN (GPT §5 row 11)
    check(G.judge(c, [T(1, "coverage", "coverage")], "PASS")["validity"] == "INDETERMINATE", "coverage_trigger_prevents_clean")
    check(G.judge(c, [], "PASS", coverage_ok=False, coverage_why="ttl")["outcome"] == G.UNMEASURED, "coverage_flag_prevents_clean")

    # --- expected transition accepted, the extra one still flagged (GPT §5 row 9)
    ce = G.RowContract("manhunter_row", about=("combat",), expected=[("hostile_arrival", "Thrumbo77")])
    v = G.judge(ce, [T(1, "hostile_arrival", "threat", 77), T(2, "hostile_arrival", "threat", 78)], "PASS")
    check(len(v["anomalies"]) == 1 and v["anomalies"][0]["subjectId"] == 78 and v["outcome"] == G.UNMEASURED,
          "expected_accepted_extra_flagged", v["anomalies"])
    v = G.judge(ce, [T(1, "hostile_arrival", "threat", 77)], "PASS")
    check(v["outcome"] == G.PASS and not v["threats"], "expected_alone_is_clean")

    # --- protection is a label only for rows NOT about health/needs/damage/death
    try:
        G.RowContract("hunger_row", about=("needs",), protected=True)
        check(False, "protection_refused_on_needs_row")
    except G.ContractError:
        check(True, "protection_refused_on_needs_row")
    check(G.RowContract("paint_row", about=("art",), protected=True).protected, "protection_allowed_on_art_row")

    # --- env item names pass rimflow's namecheck (SUBJECT_INTENT_TWIST, <= 7 words, <= 44 chars)
    try:
        import model
        bad = []
        for k in list(G.ENV_NAMES) + ["weird_new_kind"]:
            n = G.env_item_name(k)
            subj, intent, twist = model.parse_name(n)
            if intent != "HARDEN" or len(n) > model.NAME_MAX_LEN or len(n.split("_")) > model.NAME_MAX_WORDS:
                bad.append(n)
        check(not bad, "env_item_names_pass_namecheck", bad)
    except ImportError as e:
        print("UNMEASURED env_item_names_pass_namecheck: rimflow model not importable (%s)" % e)
        N[1] += 1
    line = G.env_item_lines("r1", [T(5, "modal_stuck", "block", detail='dialog "x" open 31 s')])[0]
    check(line.startswith("rimflow file TESTENV_POPUPS_HARDEN_CLOSE_THE_DOOR --for BENCH") and "'x'" in line, "env_item_line_shape", line)
    check(len(G.env_item_lines("r1", [T(1, "hostile_arrival", "threat"), T(2, "hostile_arrival", "threat")])) == 1, "env_item_one_per_kind")

    # --- run_row: damage restarts, the second attempt is clean -> PASS; the restart is never a FAIL
    logs = []
    s = FakeSession([[T(1, "downed", "damage", 12)], []])
    out = G.run_row(s, c, lambda gov: "PASS", log=logs.append)
    check(len(out["attempts"]) == 2 and out["attempts"][0]["outcome"] == G.RESTART and out["final"]["outcome"] == G.PASS,
          "run_row_restarts_then_passes", [a["outcome"] for a in out["attempts"]])
    s = FakeSession([[T(1, "death", "damage", 12)]] * 3)
    out = G.run_row(s, c, lambda gov: "FAIL", log=logs.append)
    check(out["restarts_exhausted"] and out["final"]["outcome"] == G.RESTART and len(out["attempts"]) == 3,
          "run_row_restarts_exhausted_never_fail")
    check(any("governor: file -> rimflow file TESTENV_DEATHS" in l for l in logs), "run_row_prints_env_item")

    # --- governed advance: the 600k request is refused by the companion; the governor records it
    s = FakeSession([[]])
    gov = G.RowGovernor(s, c, log=logs.append)
    gov.arm()
    r = gov.advance(600000)
    check(r["state"] == "refused" and gov.advances[0]["refused"], "governed_600k_refused")
    check(s.calls[-1][1]["timeException"] is False and s.calls[-1][1]["budgetTicks"] == 0, "advance_passes_contract_flags")
    check(G.judge(c, [T(1, "cancel", "block")], "PASS")["env_items"] == [], "cancel_is_not_a_threat")

    # --- TESTENV_WILD_DOWNED_REPAIR_STOPS_CLOCK: a downed WILD animal (severity threat) neither stops the clock nor spoils the row
    check(G.judge(c, [T(1, "downed", "threat", 7, "dalgo mare")], "PASS")["outcome"] == G.PASS, "wild_downed_does_not_spoil_row")
    check(any("wild pawn" in n for n in G.judge(c, [T(1, "downed", "threat", 7, "dalgo mare")], "PASS")["notes"]),
          "wild_downed_is_noted")
    check(G.judge(c, [T(1, "downed", "threat", 7, "mare"), T(2, "hostile_arrival", "threat")], "PASS")["outcome"] == G.UNMEASURED,
          "wild_downed_does_not_hide_a_real_anomaly")

    class StopOnce(FakeSession):
        def __init__(self, stop):
            FakeSession.__init__(self, [[]])
            self.stop, self.sa = stop, 0

        def call(self, tool, **p):
            if tool == "jawa/safe_advance":
                self.calls.append((tool, p))
                self.sa += 1
                if self.sa == 1:
                    return {"success": False, "state": "stopped", "requested": p["ticks"], "executed": 700,
                            "stopBy": self.stop[0], "triggers": self.stop[1]}
                return {"success": True, "state": "done", "requested": p["ticks"], "executed": p["ticks"]}
            return FakeSession.call(self, tool, **p)

    wild = ({"kind": "downed", "severity": "threat", "detail": "dalgo mare downed"}, [T(1, "downed", "threat", 7)])
    s = StopOnce(wild)
    gov = G.RowGovernor(s, c, log=logs.append)
    gov.arm()
    r = gov.advance(2000)
    adv_ticks = [x[1]["ticks"] for x in s.calls if x[0] == "jawa/safe_advance"]
    check(r["state"] == "done" and r["executed"] == 2000 and adv_ticks == [2000, 1300] and gov.state == "EXECUTING",
          "governor_advance_resumes_past_wild_downed", (r, adv_ticks))
    real = ({"kind": "downed", "severity": "damage", "detail": "Cait downed"}, [T(1, "downed", "damage", 12)])
    s = StopOnce(real)
    gov = G.RowGovernor(s, c, log=logs.append)
    gov.arm()
    r = gov.advance(2000)
    check(r["state"] == "stopped" and gov.state == "LATCHED", "governor_advance_still_stops_on_downed_colonist", r)
    mixed = ({"kind": "downed", "severity": "threat", "detail": "x"}, [T(1, "downed", "threat", 7), T(2, "death", "damage", 12)])
    check(not G.clockgate.is_benign_stop(dict(state="stopped", stopBy=mixed[0], triggers=mixed[1])),
          "a death alongside the wild downed is a real stop")

    print("governor selftest: %d/%d passed" % (N[0] - N[1], N[0]))
    return 1 if N[1] else 0


if __name__ == "__main__":
    sys.exit(main())
