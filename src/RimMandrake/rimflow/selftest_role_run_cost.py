#!/usr/bin/env python3
"""OPS_ROLE_SHRINK_RUN_COST: Operations runs cost less per run, and no run is starved.

Measured basis (2026-11-04, D:\\ClaudeWork\\rimmandrake\\scratch\\ops_shrink): a run starts at 56,333 tokens of context
that every turn re-reads; 48,098 with --strict-mcp-config; no MCP tool in 60 Operations transcripts. Run 1793686300
(486k weighted) paid for queues.artpipe.stalled_min while its reading was already back under the line (clear_seen >= 1).
Owner e7069d65ba: "smaller prompt, fewer re-reads, cheaper triage model, never refuse a run".

  C1 launch_argv carries the role's launch_args (the real Operations entry: --strict-mcp-config) before the schema args.
  C2 launch_args outside LAUNCH_ARGS_OK (a permission or settings flag) and a model_by_mode naming haiku are refused
     by validate_role; the real schedule validates.
  C3 an alarm run launches on model_by_mode["alarm"] (sonnet for Operations); a scheduled run keeps `model` (opus);
     launch_role hands execute that model, and a run-now keeps its enabled copy.
  C4 an OPEN alarm whose reading is back under the line (clear_seen >= 1) buys no alarm run and is journaled once;
     it stays unseen, so when it re-breaches (clear_seen 0) the next tick launches its run (never starved).
  C5 a recovering alarm beside a breaching one: the run launches and covers only the breaching one.
  C6 the alarm-run message carries each covered alarm's row and the schedule's scope_by_mode["alarm"] line; a
     scheduled run's message carries neither.
Pure: fake observers (selftest_dispatcher helpers)."""
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.dirname(HERE))
os.environ["TZ"] = "UTC"
time.tzset()
import role_launch as RL  # noqa: E402
import selftest_dispatcher as SD  # noqa: E402

FAILS = []


def check(ok, what):
    print(("PASS " if ok else "FAIL ") + what)
    if not ok:
        FAILS.append(what)


def real_ops():
    with open(os.path.join(HERE, "dispatcher_schedule.json"), encoding="utf-8") as f:
        sch = json.load(f)
    return next(r for r in sch["roles"] if r.get("name") == "Operations")


def drive(role, now, rs, status):
    st = {"roles": {"Operations": rs}}
    acts = []
    RL.decide_roles({"roles": [role]}, st, SD.robs(status), now, lambda **kw: acts.append(kw), set(), None)
    return acts, st


def launched(acts, mode=None):
    return [a for a in acts if a.get("do") == "role_launch" and (mode is None or a.get("mode") == mode)]


def op(**kw):
    base = dict(runs_local=["07:30"], economy_pass_local=None, model="opus", model_by_mode={"alarm": "sonnet"},
                launch_args=["--strict-mcp-config"], scope_by_mode={"alarm": "SCOPE-LINE alarm sections only"})
    base.update(kw)
    return SD.operations(**base)


def main():
    real = real_ops()
    # C1
    argv = RL.launch_argv(dict(real, clone="/tmp/c"), "rm-role-operations-1", "msg", "/tmp/o", "/tmp/e", "/usr/bin/claude")
    check("--strict-mcp-config" in argv and argv.index("--strict-mcp-config") > argv.index("--model"),
          "C1 the real Operations launch drops MCP servers (--strict-mcp-config in its argv)")
    argv0 = RL.launch_argv(dict(real, clone="/tmp/c", launch_args=[]), "u", "m", "/tmp/o", "/tmp/e", "/usr/bin/claude")
    check("--strict-mcp-config" not in argv0, "C1 a role without launch_args gets no extra flag")
    # C2
    for bad, what in ((dict(real, launch_args=["--dangerously-skip-permissions"]), "a permission flag"),
                      (dict(real, launch_args=["--settings", "x.json"]), "a settings flag"),
                      (dict(real, launch_args="--strict-mcp-config"), "a bare string"),
                      (dict(real, model_by_mode={"alarm": "haiku"}), "haiku (banned)"),
                      (dict(real, scope_by_mode={"alarm": 3}), "a non-text scope")):
        try:
            RL.validate_role(dict(RL.ROLE_DEFAULTS, **bad))
            check(False, "C2 validate_role refuses %s" % what)
        except ValueError:
            check(True, "C2 validate_role refuses %s" % what)
    try:
        RL.validate_role(dict(RL.ROLE_DEFAULTS, **real))
        check(real.get("model_by_mode", {}).get("alarm") == "sonnet" and real.get("model") == "opus",
              "C2 the real Operations entry validates, alarm runs on sonnet, the rest on opus")
    except ValueError as e:
        check(False, "C2 the real Operations entry validates (%s)" % e)
    # C3 + C6
    t = SD.at_local("12:00")
    al = {"QUEUE_STALLED:queues.x": {"state": "OPEN", "item": "OPS_X_ITEM", "clear_seen": 0,
                                     "title": "Ops alarm QUEUE_STALLED x", "since": "2026-11-03T05:37:00Z",
                                     "told": {"v": 26.2}}}
    acts, st = drive(op(), t, {"done": {}, "runs": []}, SD.ops_status(t, alarms=al))
    la = launched(acts, "alarm")
    check(len(la) == 1 and "model sonnet" in la[0]["why"], "C3 the alarm run launches on sonnet (%r)" % [
        a.get("why") for a in la])
    if la:
        role = RL.launch_role(op(), la[0])
        check(role["model"] == "sonnet" and op()["model"] == "opus", "C3 launch_role hands execute the sonnet copy")
        msg = la[0]["message"]
        check("OPS_X_ITEM = QUEUE_STALLED:queues.x" in msg and "26.2" in msg and "SCOPE-LINE" in msg,
              "C6 the alarm message carries the alarm row and the scope line")
    t2 = SD.at_local("07:30")
    acts, _ = drive(op(), t2, {"done": {}, "runs": []}, SD.ops_status(t2))
    ls = launched(acts)
    check(len(ls) == 1 and ls[0]["mode"] != "alarm" and "model opus" in ls[0]["why"]
          and "SCOPE-LINE" not in ls[0]["message"] and "alarms this run covers" not in ls[0]["message"],
          "C3/C6 the scheduled run keeps opus and carries no alarm rows or alarm scope (%r)" % [a.get("why") for a in ls])
    if ls:
        check(RL.launch_role(op(), ls[0])["model"] == "opus", "C3 launch_role keeps opus for a scheduled run")
    rn = RL.launch_role(op(), {"mode": "alarm", "run_now": {"by": "x"}})
    check(rn["model"] == "sonnet" and rn["enabled"] is True, "C3 a run-now copy is enabled and keeps the mode model")
    # C4
    rec = json.loads(json.dumps(al))
    rec["QUEUE_STALLED:queues.x"]["clear_seen"] = 1
    rs = {"done": {}, "runs": []}
    acts, st = drive(op(), t, rs, SD.ops_status(t, alarms=rec))
    holds = [a for a in acts if a.get("do") == "role_hold" and "back under the line" in a.get("why", "")]
    check(not launched(acts, "alarm") and len(holds) == 1, "C4 a recovering alarm buys no run, one hold journaled (%r)" % [
        (a.get("do"), a.get("why")) for a in acts])
    rs = st["roles"]["Operations"]
    check("OPS_X_ITEM" not in (rs.get("alarms_seen") or []), "C4 the recovering alarm is not marked seen")
    acts, st = drive(op(), t + 60, rs, SD.ops_status(t + 60, alarms=rec))
    check(not [a for a in acts if a.get("do") == "role_hold" and "back under" in a.get("why", "")],
          "C4 the same recovering set is journaled once")
    acts, st = drive(op(), t + 120, st["roles"]["Operations"], SD.ops_status(t + 120, alarms=al))
    check(len(launched(acts, "alarm")) == 1, "C4 a re-breach (clear_seen 0) launches the alarm run at once")
    # C5
    two = json.loads(json.dumps(rec))
    two["QUEUE_STALLED:queues.y"] = {"state": "OPEN", "item": "OPS_Y_ITEM", "clear_seen": 0, "title": "y",
                                     "since": "2026-11-03T06:00:00Z", "told": {"v": 99}}
    acts, st = drive(op(), t, {"done": {}, "runs": []}, SD.ops_status(t, alarms=two))
    la = launched(acts, "alarm")
    check(len(la) == 1 and "OPS_Y_ITEM" in la[0]["message"] and "OPS_X_ITEM =" not in la[0]["message"],
          "C5 a recovering alarm beside a breaching one: the run covers the breaching one only")
    check(st["roles"]["Operations"].get("alarm_day", {}).get("keys") == {"OPS_Y_ITEM": 1},
          "C5 only the breaching key is counted as run")
    print("\n%d FAIL" % len(FAILS) if FAILS else "\nALL PASS")
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
