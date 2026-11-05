#!/usr/bin/env python3
"""ROLE_RUNS_BUILD_RESUME_AFTER_ACCOUNT_LOSS (owner 2026-11-04: "You could just poke the agents to continue where they
were."): a role run the ACCOUNT ended (usage_limit_reached / 429) is not a role failure, and after real usage the next
tick past the account's reset resumes it in its own session (`--resume <session>`, same unit template, slice and
budget, a continue prompt). A 0-usage death stays a fresh run on the normal schedule. Driven through the real
supervise_roles, decide_roles, launch_argv/launch and dispatcher.execute; pure, no systemd, no clock."""
import os
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
os.environ["TZ"] = "UTC"
import dispatcher as D  # noqa: E402
import role_launch as RL  # noqa: E402
import selftest_dispatcher as SD  # noqa: E402

FAILS = []
# the result claude -p wrote for rm-role-conductor-1793808830 (2026-11-04 outage), its fields as measured
OUTAGE = {"type": "result", "subtype": "success", "is_error": True, "terminal_reason": "api_error",
          "api_error_status": 429, "api_error": "usage_limit_reached", "num_turns": 1, "total_cost_usd": 0,
          "session_id": "af866c1c-c238-44b1-9175-dab20f2457bb",
          "result": "You've hit your weekly limit · resets 12pm (America/Los_Angeles)"}
SID = "11111111-2222-3333-4444-555555555555"


def check(name, ok):
    if not ok:
        FAILS.append(name)
    print(("ok   " if ok else "FAIL ") + name)


def death(**usage):
    return dict(OUTAGE, session_id=SID, usage=SD.usage(**usage))     # claude reports the run's own session


def test_classify():
    check("the measured outage result is an account death", RL.account_death(death()) == "usage_limit_reached")
    check("a bare 429 is one", RL.account_death({"is_error": True, "api_error_status": 429}) == "429")
    check("a short limit text on an api_error is one", RL.account_death(
        {"is_error": True, "terminal_reason": "api_error", "result": "You've hit your session limit"}) == "limit")
    check("an auth death is not (login_watch's)", RL.account_death(
        {"is_error": True, "terminal_reason": "api_error",
         "result": "Failed to authenticate: OAuth session expired and could not be refreshed"}) is None)
    check("a good result is not", RL.account_death({"is_error": False, "result": "hit your limit"}) is None)
    check("a long result quoting a limit is not", RL.account_death(
        {"is_error": True, "terminal_reason": "api_error", "result": "x" * 500 + " hit your limit"}) is None)
    check("no result is not", RL.account_death(None) is None)


def world(op=None):
    op = op or SD.operations(runs_local=["07:30"], economy_pass_local=None, alarm_runs=False)
    sch = {"roles": [op]}
    st = {"roles": {}}
    ob = SD.robs(SD.ops_status(SD.at_local("07:30")))
    result = [None]
    ob.update(unit_state=lambda u: "inactive", result=lambda run: result[0])
    return op, sch, st, ob, result


def decide(sch, st, ob, at, gate=None):
    acts = []
    ob["ops"] = lambda: SD.ops_status(at)
    RL.decide_roles(sch, st, ob, at, lambda **k: acts.append(k), set(), gate)
    launch = [a for a in acts if a.get("do") == "role_launch"]
    for a in launch:                          # what dispatcher.execute records on a good systemd-run
        rs = st["roles"]["Operations"]
        rs["runs"].append(dict({"unit": a["unit"], "at": at, "state": "running", "mode": a["mode"],
                                "budget": a["budget"], "slot": a["slot"], "item": a["ticket"], "seat": "BENCH",
                                "scope": "sc", "session": a.get("resume") or SID,
                                "consumed": rs.pop("pending_launch")},
                               **({"resume_of": a["resume_of"], "resume_n": a["resume_n"]} if a.get("resume") else {})))
    return launch, acts


def supervise(sch, st, ob, at):
    acts = []
    RL.supervise_roles(sch, st, ob, at, lambda **k: acts.append(k))
    return acts


def failed_alarms(acts):
    return [a for a in acts if a.get("do") == "alarm" and str(a.get("kind")).endswith(":failed")]


def test_resume_after_real_usage():
    op, sch, st, ob, result = world()
    t0 = SD.at_local("07:30")
    first, _ = decide(sch, st, ob, t0)
    check("the 07:30 slot launches", len(first) == 1)
    result[0] = death(input_tokens=40000, output_tokens=2000)
    acts = supervise(sch, st, ob, t0 + 600)
    rs = st["roles"]["Operations"]
    check("an account death raises no role:Operations:failed", not failed_alarms(acts))
    hold = [a for a in acts if a.get("do") == "role_hold" and "ended on the account" in a.get("why", "")]
    check("it is said once, as the account's, resumable", len(hold) == 1 and "resumable" in hold[0]["why"])
    rec = rs.get("resume") or {}
    reset = RL.limit_reset_at(OUTAGE["result"], t0 + 600)
    check("the resume holds the run's session, budget and slot", rec.get("session") == SID
          and rec.get("budget") == first[0]["budget"] and rec.get("slot") == first[0]["slot"]
          and rec.get("mode") == first[0]["mode"] and rec.get("n") == 1)
    check("it is due at the reset its message names", reset is not None and rec.get("due") == reset and reset > t0 + 600)
    op["runs_local"] = ["07:30", time.strftime("%H:%M", time.gmtime(reset - 1800))]    # a fresh slot before the reset
    early, acts = decide(sch, st, ob, reset - 1800 + 60)
    check("before the reset nothing resumes, and the due fresh slot is held, said", not early and rs.get("resume")
          and any("holds for the resume" in a.get("why", "") for a in acts))
    op["runs_local"] = ["07:30"]
    dead = lambda kind: (False, {"why": "account still held"})
    held, acts = decide(sch, st, ob, reset + 60, dead)
    check("a held account gate holds the resume, said", not held and rs.get("resume")
          and any(a.get("do") == "role_hold" and "resume of" in a.get("why", "") for a in acts))
    go, _ = decide(sch, st, ob, reset + 120)
    a = go[0] if len(go) == 1 else {}
    check("the account back: one resume launch", len(go) == 1 and "resume" not in rs)
    check("same session, budget, mode; chain counted", a.get("resume") == SID and a.get("budget") == rec["budget"]
          and a.get("mode") == rec["mode"] and a.get("resume_n") == 1 and a.get("resume_of") == first[0]["unit"])
    check("a continue prompt, not the original", "Continue exactly where you left off" in a.get("message", "")
          and "Do not start the task over" in a.get("message", ""))
    # launch_role + launch_argv: the same unit template, --resume instead of --session-id, no pre-steps re-run
    role = RL.launch_role(dict(op, pre_launch=["true"]), a)
    argv = RL.launch_argv(role, a["unit"], a["message"], "o", "e", "/x/claude", session="NEW")
    check("the argv resumes the session", "--resume" in argv and argv[argv.index("--resume") + 1] == SID
          and "--session-id" not in argv)
    check("same unit template", argv[:2] == ["systemd-run", "--user"] and argv[argv.index("--unit") + 1] == a["unit"]
          and "--model" in argv and "role-pre-launch" not in argv)
    fresh_argv = RL.launch_argv(RL.launch_role(op, {"mode": "run"}), "U", "m", "o", "e", "/x/claude", session="NEW")
    check("a fresh run is unchanged: --session-id, no --resume", "--resume" not in fresh_argv
          and fresh_argv[fresh_argv.index("--session-id") + 1] == "NEW")
    seen = []
    ok, _, recd = RL.launch(role, a["unit"], a["message"], SD.TMP, "/x/claude",
                            runner=lambda argv, **k: seen.append(argv) or subprocess.CompletedProcess([], 0, "", ""))
    check("launch keeps the resumed session id on the run", ok and recd.get("session") == SID and "--resume" in seen[0])
    # the resumed run finishes well: nothing more owed
    result[0] = {"subtype": "success", "result": "done", "usage": SD.usage(input_tokens=10)}
    acts = supervise(sch, st, ob, reset + 900)
    check("a good resumed run raises nothing and leaves no resume", not failed_alarms(acts) and "resume" not in rs)
    check("and is not resumed again", not decide(sch, st, ob, reset + 1800)[0])


def test_account_switch_and_ttl():
    op, sch, st, ob, result = world()
    t0 = SD.at_local("07:30")
    decide(sch, st, ob, t0)
    result[0] = death(input_tokens=5000)
    supervise(sch, st, ob, t0 + 60)
    rs = st["roles"]["Operations"]
    check("the account at death is kept", rs["resume"].get("account") == "acct")
    ob["account"] = lambda: "other"
    go, _ = decide(sch, st, ob, t0 + 120)
    check("on another account the resume goes before the reset", len(go) == 1 and go[0].get("resume") == SID
          and "another account" in go[0]["why"])
    # a weekly reset days out: kept past RESUME_TTL_S from death, dropped RESUME_TTL_S past its due time
    rs = {"resume": {"unit": "U", "session": "s", "at": 0.0, "due": 5 * 86400.0, "n": 1, "error": "429", "of": "U"}}
    acts = []
    RL.resume_due("Operations", rs, dict(op), 3 * 86400.0, lambda **k: acts.append(k), set(), None)
    check("a resume due in days is not dropped by the TTL before it", rs.get("resume"))
    RL.resume_due("Operations", rs, dict(op), 5 * 86400.0 + RL.RESUME_TTL_S + 10, lambda **k: acts.append(k), set(), None)
    check("it is dropped TTL past its due time, said", "resume" not in rs and "dropped" in acts[-1]["why"])
    # a disabled role's resume is dropped and said, never resumed later unannounced
    op2, sch2, st2, ob2, result2 = world()
    decide(sch2, st2, ob2, t0)
    result2[0] = death(input_tokens=5000)
    supervise(sch2, st2, ob2, t0 + 60)
    op2["enabled"] = False
    _, acts = decide(sch2, st2, ob2, t0 + 120)
    check("a disabled role's resume is dropped, said", "resume" not in st2["roles"]["Operations"]
          and any("role is disabled" in a.get("why", "") for a in acts))
    # two chains cut off: the one with more work is kept, the other named
    op3, sch3, st3, ob3, result3 = world()
    rs3 = st3["roles"].setdefault("Operations", {"done": {}, "runs": []})
    rs3["resume"] = {"unit": "OLD", "of": "OLD", "session": "old-s", "tokens": 10 ** 9, "at": 1.0, "due": 2.0, "n": 1}
    rs3["runs"] = [{"unit": "NEW", "at": t0, "state": "running", "mode": "run", "budget": 9, "item": "I", "seat": "BENCH",
                    "scope": "sc", "session": "new-s"}]
    result3[0] = dict(death(input_tokens=5), session_id="new-s")
    acts = supervise(sch3, st3, ob3, t0 + 60)
    check("the run with more work keeps its resume; the other session is named", rs3["resume"]["unit"] == "OLD"
          and any("new-s" in a.get("why", "") and "dropped" in a.get("why", "") for a in acts))


def test_zero_usage_stays_fresh():
    op, sch, st, ob, result = world()
    t0 = SD.at_local("07:30")
    decide(sch, st, ob, t0)
    result[0] = death()
    acts = supervise(sch, st, ob, t0 + 60)
    rs = st["roles"]["Operations"]
    check("0-usage death: no failed alarm", not failed_alarms(acts))
    check("0-usage death: not resumable, said", "resume" not in rs and any(
        "not resumed" in a.get("why", "") for a in acts if a.get("do") == "role_hold"))
    later, _ = decide(sch, st, ob, t0 + 6 * 3600)
    check("0-usage death: its slot is not given back (the normal schedule runs next)", not later)
    nxt, _ = decide(sch, st, ob, t0 + 86400)
    check("the next day's slot runs fresh", len(nxt) == 1 and not nxt[0].get("resume"))


def test_chain_and_limits():
    op, sch, st, ob, result = world()
    t0 = SD.at_local("07:30")
    decide(sch, st, ob, t0)
    result[0] = death(input_tokens=5000)
    supervise(sch, st, ob, t0 + 60)
    rs = st["roles"]["Operations"]
    t = t0 + 60
    for n in range(1, RL.RESUME_MAX + 1):
        t = rs["resume"]["due"] + 10
        go, _ = decide(sch, st, ob, t)
        check("resume %d launches" % n, len(go) == 1 and go[0]["resume_n"] == n)
        result[0] = death()                     # dies at once again: the chain's work is still in the session
        acts = supervise(sch, st, ob, t + 30)
        check("resume %d's death raises no failed alarm" % n, not failed_alarms(acts))
    check("past RESUME_MAX the chain is given up, said", "resume" not in rs)
    # no reset named: RESUME_WAIT_S
    rec, why = RL.resume_record({"unit": "U", "tokens": 9, "session": "s"}, {"result": "rate limited"}, "429", 100.0, {})
    check("no reset in the text: due after RESUME_WAIT_S", rec["due"] == 100.0 + RL.RESUME_WAIT_S)
    check("a stage-machine run is not resumed", RL.resume_record({"unit": "U", "tokens": 9, "session": "s",
                                                                  "concept": "c"}, {}, "429", 1.0, {})[0] is None)
    check("no session, not resumed", RL.resume_record({"unit": "U", "tokens": 9}, {}, "429", 1.0, {})[0] is None)
    # a stale resume, or a disabled role, is dropped and said
    rs["resume"] = {"unit": "U", "session": "s", "at": 0.0, "due": 0.0, "n": 1, "error": "429", "of": "U"}
    acts = []
    RL.resume_due("Operations", rs, dict(op), RL.RESUME_TTL_S + 10, lambda **k: acts.append(k), set(), None)
    check("a stale resume is dropped, said", "resume" not in rs and acts and "dropped" in acts[0]["why"])
    # unlaunch: a resume that did not launch is pending again
    rec = {"unit": "U", "session": "s", "at": 1.0, "due": 1.0, "n": 1, "error": "429", "of": "U", "mode": "run"}
    rs = {"resume": dict(rec), "runs": []}
    acts = []
    RL.resume_due("Operations", rs, dict(op), 10.0, lambda **k: acts.append(k), set(), None)
    unit = acts[0]["unit"]
    check("unlaunch gives the resume back", RL.unlaunch(rs, unit) and rs.get("resume") == rec)


def test_off_switch_holds_resume():
    op, sch, st, ob, result = world()
    t0 = SD.at_local("07:30")
    decide(sch, st, ob, t0)
    result[0] = death(input_tokens=5000)
    supervise(sch, st, ob, t0 + 60)
    rs = st["roles"]["Operations"]
    ob["off"] = lambda p: "off for a while"
    go, _ = decide(sch, st, ob, rs["resume"]["due"] + 10)
    check("an off switch launches no resume and keeps it", not go and rs.get("resume"))


def test_execute_records_the_chain():
    op = SD.operations()
    sch = SD.sched(roles=[op])
    st = SD.fresh()
    st["roles"] = {"Operations": {"pending_launch": {"unit": "U2", "mode": "resume", "resume": {"unit": "U1"}}}}
    act = {"do": "role_launch", "role": "Operations", "unit": "U2", "message": "m", "ticket": "ROLES_ITEM_X",
           "note": True, "mode": "run", "budget": 60000, "slot": "resume of U1", "band": "GREEN", "why": "w",
           "resume": SID, "resume_of": "U1", "resume_n": 1, "blind": RL.blind("Operations", "launched", "run", "U2")}
    got = []
    fx = {"note": lambda i, t: (True, ""), "publish": lambda n: "p", "lock": lambda: open(os.devnull),
          "role_launch": lambda role, *a: got.append(role) or (True, "unit U2 started",
                                                               {"out": "o", "err": "e", "session": SID})}
    D.execute([act], sch, st, os.path.join(SD.TMP, "resume_exec"), True, 100.0, fx)
    run = (st["roles"]["Operations"].get("runs") or [{}])[0]
    check("execute launches with the session to resume", got and got[0].get("resume_session") == SID)
    check("execute records the chain on the run", run.get("resume_of") == "U1" and run.get("resume_n") == 1
          and run.get("session") == SID and run.get("budget") == 60000)
    st = SD.fresh()
    rec = {"unit": "U1", "session": SID}
    st["roles"] = {"Operations": {"pending_launch": {"unit": "U2", "mode": "resume", "resume": rec}}}
    fx["role_launch"] = lambda *a: (False, "systemd-run exit 1", {})
    D.execute([dict(act)], sch, st, os.path.join(SD.TMP, "resume_exec"), True, 100.0, fx)
    check("a resume systemd-run refused is pending again", st["roles"]["Operations"].get("resume") == rec
          and not st["roles"]["Operations"].get("runs"))


def test_transcript_counts_only_the_resume():
    import json
    import tempfile
    with tempfile.TemporaryDirectory() as d:
        os.makedirs(os.path.join(d, "proj"))
        with open(os.path.join(d, "proj", SID + ".jsonl"), "w") as f:
            for i, ts in enumerate(("2026-11-04T14:00:00.123Z", "2026-11-04T21:00:00.456Z")):
                f.write(json.dumps({"type": "assistant", "timestamp": ts, "message": {
                    "id": "m%d" % i, "usage": {"input_tokens": 1000 * (i + 1)}}}) + "\n")
        at = RL.utc_epoch("2026-11-04T20:30:00Z")
        whole = RL.transcript_usage({"session": SID, "at": at}, d)
        resumed = RL.transcript_usage({"session": SID, "at": at, "resume_of": "U1"}, d)
    check("a fresh run's transcript counts every turn", whole and whole["input_tokens"] == 3000)
    check("a resumed run counts only its own turns, never the run it continues",
          resumed and resumed["input_tokens"] == 2000)


def main():
    test_classify()
    test_resume_after_real_usage()
    test_zero_usage_stays_fresh()
    test_account_switch_and_ttl()
    test_transcript_counts_only_the_resume()
    test_chain_and_limits()
    test_off_switch_holds_resume()
    test_execute_records_the_chain()
    print("%d FAIL" % len(FAILS) if FAILS else "ALL PASS")
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
