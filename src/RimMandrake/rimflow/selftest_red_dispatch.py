#!/usr/bin/env python3
"""selftest_red_dispatch.py: red_dispatch.py's decisions over fake facts, in a temp state dir; fake start, launch and
Conductor line, so nothing is spawned, published or written outside the temp tree. Offline, no model.

Item RIMMANDRAKE_ROUTE_NIGHTLY_REDS_RAISED_INTO_A_RETIRED_POOL: one capped fixer per red item, at most max_live, one attempt
a night, a failed attempt stops with one Needs Conductor line and is never retried by the program, and the dead
Relentless pool route is gone from ops_watch, its rules and known_reds."""
import os
import re
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
TMP = tempfile.mkdtemp(prefix="selftest_red_dispatch_")
os.environ["RM_RED_DISPATCH_DIR"] = TMP
sys.path.insert(0, HERE)
import red_dispatch as RD  # noqa: E402

FAILS = []


def check(name, ok, got=None):
    print("%s %s" % ("PASS" if ok else "FAIL", name))
    if not ok:
        FAILS.append(name)
        if got is not None:
            print("    got: %r" % (got,))


SHIPPED = RD.load_cfg()
# The shipped file is the owner's to tune: one sanity check reads it (ranges), and every case below runs on pinned
# fixture numbers, so a changed knob never turns a case red (RIMMANDRAKE_PIN_TUNABLES_OUT_OF_SELFTESTS).
check("shipped red_dispatch.json is sane: caps and limits positive, opus cap >= sonnet cap, min_tests >= 2",
      SHIPPED["max_live"] >= 1 and SHIPPED["max_launches_per_night"] >= 1 and SHIPPED["sonnet_cap_usd"] > 0
      and SHIPPED["opus_cap_usd"] >= SHIPPED["sonnet_cap_usd"] and SHIPPED["opus_if"]["min_tests"] >= 2,
      {k: SHIPPED[k] for k in ("max_live", "max_launches_per_night", "sonnet_cap_usd", "opus_cap_usd")})
CFG = dict(SHIPPED, enabled=True, max_live=2, max_launches_per_night=3, sonnet_cap_usd=5, opus_cap_usd=12,
           detail_lines=60, opus_if=dict(SHIPPED["opus_if"], min_tests=2))
NOW = 1794740000.0      # 2026-11-15 ~01:33 PST: night 2026-11-14


def alarm(item, tests, title="Ops alarm NIGHTLY_RED: 1 red: FAIL x", state="OPEN", due="2026-11-17T11:00:00Z"):
    return {"state": state, "item": item, "name": item, "title": title, "filed": "2026-11-14T12:00:00Z",
            "noted": ["%s (due %s)" % (t, due) for t in tests]}


ALARMS = {
    "NIGHTLY_RED:testing.red_aaaaaa": alarm("SELFTEST_FIX_ALPHA_AAAA", ["src/RimMandrake/rimflow/selftest_alpha.py"]),
    "NIGHTLY_RED:testing.red_bbbbbb": alarm("SELFTEST_FIX_BETA_BBBB", ["src/RimMandrake/Utils/selftest_beta.py",
                                                                       "src/RimMandrake/Utils/selftest_gamma.py"]),
    "NIGHTLY_RED:testing.red_cccccc": alarm("SELFTEST_FIX_GAMMA_CCCC", ["src/RimMandrake/Utils/selftest_c.py"]),
    "NIGHTLY_RED:testing.red_dddddd": alarm("SELFTEST_FIX_DONE_DDDD", ["src/RimMandrake/Utils/selftest_d.py"], state="CLEAR"),
    "OPS_OTHER:x": alarm("OPS_OTHER_THING_XXXX", ["a.py"]),
}

# ---- parsing ---------------------------------------------------------------------------------------------------------
reds = RD.red_alarms(ALARMS)
check("red_alarms keeps only OPEN build-cop groups that name a red-fix item",
      [r["item"] for r in reds] == ["SELFTEST_FIX_ALPHA_AAAA", "SELFTEST_FIX_BETA_BBBB", "SELFTEST_FIX_GAMMA_CCCC"],
      [r["item"] for r in reds])
check("red_alarms strips the due suffix off each test and keeps the earliest due",
      reds[1]["tests"] == ["src/RimMandrake/Utils/selftest_beta.py", "src/RimMandrake/Utils/selftest_gamma.py"]
      and reds[0]["due"] == "2026-11-17T11:00:00Z", reds[1])
check("red_alarms of an empty or odd store is empty", RD.red_alarms({}) == [] and RD.red_alarms({"NIGHTLY_RED:testing.red_x": "?"}) == [])

# ---- model choice ----------------------------------------------------------------------------------------------------
check("one plain test: sonnet", RD.pick_model(CFG, ["src/RimMandrake/rimflow/selftest_a.py"], "FAIL x")[0] == "sonnet")
check("two tests sharing a cause: opus", RD.pick_model(CFG, ["a.py", "b.py"], "FAIL x")[0] == "opus")
check("a C# / build cause: opus", RD.pick_model(CFG, ["src/RimMandrake/Utils/selftest_a.py"], "error CS0103 in Foo.cs")[0] == "opus")
check("a timeout: opus", RD.pick_model(CFG, ["src/RimMandrake/Utils/selftest_a.py"], "timeout: exceeded #s")[0] == "opus")
check("a test in a mod's own tree: opus",
      RD.pick_model(CFG, ["src/RimMandrake/FlowWorks/northstar/selftest_x.py"], "FAIL x")[0] == "opus")

# ---- the night -------------------------------------------------------------------------------------------------------
check("night_of: 01:33 PST belongs to the night before; 03:30 PST to its own date",
      RD.night_of(NOW) == "2026-11-14" and RD.night_of(NOW + 2 * 3600) == "2026-11-15", (RD.night_of(NOW), RD.night_of(NOW + 7200)))


# ---- a tick through fakes --------------------------------------------------------------------------------------------
def open_items(**over):
    d = {r["item"]: {"state": "proposed", "blocked": False, "owner": "BENCH"} for r in reds}
    d.update(over)
    return d


WORLD = {"items": open_items(), "runs": {}, "night": {}}
CALLS = {"launch": [], "need": []}
LAUNCH_RC = {"rc": 0}


def fx():
    def launch(item, model, cap, brief, seat):
        CALLS["launch"].append((item, model, cap, seat, brief))
        if LAUNCH_RC["rc"]:
            return 1, "LAUNCH FAILED fake", None
        return 0, "DETACHED rm-detached-bench-%s-1" % item.lower(), "rm-detached-bench-%s-1" % item.lower()

    def need(text, now):
        CALLS["need"].append(text)
    return {"facts": lambda: {"reds": reds, **WORLD}, "account": lambda: (True, "ok"),
            "launch": launch, "need": need}


rd = RD.tick(CFG, apply=False, fx=fx(), now=NOW)
check("a dry pass launches nothing, writes no state, and says would_launch",
      not CALLS["launch"] and not os.path.exists(os.path.join(TMP, "state.json"))
      and [v["decision"] for v in rd["items"].values()] == ["would_launch", "would_launch", "slots_full"], rd["items"])

rd = RD.tick(CFG, apply=True, fx=fx(), now=NOW)
dec = {k: v["decision"] for k, v in rd["items"].items()}
check("max_live 2: two launch, the third waits", dec == {"SELFTEST_FIX_ALPHA_AAAA": "launched", "SELFTEST_FIX_BETA_BBBB":
                                                         "launched", "SELFTEST_FIX_GAMMA_CCCC": "slots_full"}, dec)
check("each brief's first step starts the item as BENCH and publishes the shard (acceptance B's start)",
      all(c[4].index("cli.py start %s --seat BENCH" % c[0]) < c[4].index("1. Run") and "events/BENCH.jsonl" in c[4]
          for c in CALLS["launch"]), [c[0] for c in CALLS["launch"]])
check("sonnet at its cap for one test, opus at its cap for a shared cause, seat BENCH",
      [(c[1], c[2], c[3]) for c in CALLS["launch"]] == [("sonnet", 5, "BENCH"), ("opus", 12, "BENCH")], CALLS["launch"])
b = CALLS["launch"][0][4]
check("the brief names the item, the test, the --only command, the publish/close steps and the no-weakening rule",
      "SELFTEST_FIX_ALPHA_AAAA" in b and "run_selftests.py --only selftest_alpha.py" in b and "./publish" in b
      and "cli.py close SELFTEST_FIX_ALPHA_AAAA" in b and "Never weaken an assertion" in b and "north-star bar" in b, b[:400])
check("the reading lists the two launches", len(rd["launched"]) == 2 and os.path.exists(os.path.join(TMP, "reading.json")))

# the two runs are live: nothing more on them, and still no slot for the third
U1, U2 = "rm-detached-bench-selftest_fix_alpha_aaaa-1", "rm-detached-bench-selftest_fix_beta_bbbb-1"
WORLD["items"] = open_items(SELFTEST_FIX_ALPHA_AAAA={"state": "doing", "blocked": False, "owner": "BENCH"},
                            SELFTEST_FIX_BETA_BBBB={"state": "doing", "blocked": False, "owner": "BENCH"})
WORLD["runs"] = {"SELFTEST_FIX_ALPHA_AAAA": {"live": [U1], "ended": []}, "SELFTEST_FIX_BETA_BBBB": {"live": [U2], "ended": []}}
n0 = len(CALLS["launch"])
rd = RD.tick(CFG, apply=True, fx=fx(), now=NOW + 600)
dec = {k: v["decision"] for k, v in rd["items"].items()}
check("live runs: nothing launches on them, the third still waits for a slot",
      dec["SELFTEST_FIX_ALPHA_AAAA"] == "live" and dec["SELFTEST_FIX_GAMMA_CCCC"] == "slots_full"
      and len(CALLS["launch"]) == n0, dec)

# alpha's run ends with the item closed; beta's ends with the item still open
WORLD["items"]["SELFTEST_FIX_ALPHA_AAAA"] = {"state": "done", "blocked": False, "owner": "BENCH"}
WORLD["runs"] = {"SELFTEST_FIX_ALPHA_AAAA": {"live": [], "ended": [U1]}, "SELFTEST_FIX_BETA_BBBB": {"live": [], "ended": [U2]}}
rd = RD.tick(CFG, apply=True, fx=fx(), now=NOW + 1200)
dec = {k: v["decision"] for k, v in rd["items"].items()}
check("a fixed item reads closed; a failed attempt reads stopped; the freed slot goes to the third",
      dec == {"SELFTEST_FIX_ALPHA_AAAA": "closed", "SELFTEST_FIX_BETA_BBBB": "stopped",
              "SELFTEST_FIX_GAMMA_CCCC": "launched"}, dec)
check("the stopped item gets exactly one Needs Conductor line naming it and the clear command",
      len(CALLS["need"]) == 1 and "SELFTEST_FIX_BETA_BBBB" in CALLS["need"][0] and "red_dispatch.py clear" in CALLS["need"][0],
      CALLS["need"])

WORLD["runs"]["SELFTEST_FIX_GAMMA_CCCC"] = {"live": [], "ended": ["rm-detached-bench-selftest_fix_gamma_cccc-1"]}
n0 = len(CALLS["launch"])
for k in range(3):     # many ticks, nights later: never a second automatic try, never a second line
    rd = RD.tick(CFG, apply=True, fx=fx(), now=NOW + 86400 * (k + 1))
dec = {k: v["decision"] for k, v in rd["items"].items()}
check("no automatic retry on later ticks or later nights (no reject-and-retry loop)",
      len(CALLS["launch"]) == n0 and dec["SELFTEST_FIX_BETA_BBBB"] == "stopped" and dec["SELFTEST_FIX_GAMMA_CCCC"] == "stopped",
      (len(CALLS["launch"]) - n0, dec))
check("each stopped item is told once, not once per tick", len(CALLS["need"]) == 2, CALLS["need"])

# the Conductor clears beta: one more attempt, once
check("clear lifts a stop", RD.main(["clear", "SELFTEST_FIX_BETA_BBBB", "--why", "selftest"]) == 0)
WORLD["items"]["SELFTEST_FIX_BETA_BBBB"] = {"state": "doing", "blocked": False, "owner": "BENCH"}
WORLD["runs"]["SELFTEST_FIX_BETA_BBBB"] = {"live": [], "ended": [U2]}
rd = RD.tick(CFG, apply=True, fx=fx(), now=NOW + 86400 * 4)
check("after clear, exactly one more launch on it", rd["items"]["SELFTEST_FIX_BETA_BBBB"]["decision"] == "launched"
      and len(CALLS["launch"]) == n0 + 1, rd["items"]["SELFTEST_FIX_BETA_BBBB"])

# ---- the other gates, on a fresh state -------------------------------------------------------------------------------
os.remove(os.path.join(TMP, "state.json"))
WORLD.update(items=open_items(SELFTEST_FIX_ALPHA_AAAA={"state": "ready", "blocked": True, "owner": "BENCH"},
                              SELFTEST_FIX_BETA_BBBB={"state": "doing", "blocked": False, "owner": "STEVE"}),
             runs={}, night={"src/RimMandrake/Utils/selftest_c.py": ("PASS", [])})
rd = RD.tick(CFG, apply=False, fx=fx(), now=NOW)
dec = {k: v["decision"] for k, v in rd["items"].items()}
check("blocked, claimed by someone else, and green on the last night: no launch on any",
      dec == {"SELFTEST_FIX_ALPHA_AAAA": "blocked", "SELFTEST_FIX_BETA_BBBB": "claimed", "SELFTEST_FIX_GAMMA_CCCC": "green"}, dec)

WORLD.update(items=open_items(), night={})
rd = RD.tick(dict(CFG, max_launches_per_night=1), apply=False, fx=fx(), now=NOW)
check("max_launches_per_night caps the night", [v["decision"] for v in rd["items"].values()] ==
      ["would_launch", "night_cap", "night_cap"], rd["items"])
rd = RD.tick(dict(CFG, enabled=False), apply=False, fx=fx(), now=NOW)
check("enabled: false launches nothing", all(v["decision"] == "disabled" for v in rd["items"].values()), rd["items"])
f2 = fx()
f2["account"] = lambda: (False, "account pick reads HOLD")
rd = RD.tick(CFG, apply=False, fx=f2, now=NOW)
check("the Dispatcher's account hold holds launches", all(v["decision"] == "account_hold" for v in rd["items"].values()))
rd = RD.tick(dict(CFG, sonnet_cap_usd=0), apply=False, fx=fx(), now=NOW)
check("no positive cap: that model never launches", rd["items"]["SELFTEST_FIX_ALPHA_AAAA"]["decision"] == "no_cap", rd["items"])
f3 = fx()
f3["facts"] = lambda: {"reds": None, "items": {}, "runs": {}, "night": None}
rd = RD.tick(CFG, apply=False, fx=f3, now=NOW)
check("an unreadable alarm store is blind: nothing launches", list(rd["items"].values())[0]["decision"] == "blind", rd["items"])
WORLD["items"] = {}
rd = RD.tick(CFG, apply=False, fx=fx(), now=NOW)
check("an item the ledger does not hold yet is blind, not launched", all(v["decision"] == "blind" for v in rd["items"].values()))

# a failed launch is the attempt: never retried
WORLD.update(items=open_items(), runs={})
LAUNCH_RC["rc"] = 1
n0 = len(CALLS["launch"])
RD.tick(dict(CFG, max_live=1), apply=True, fx=fx(), now=NOW)
LAUNCH_RC["rc"] = 0
rd = RD.tick(dict(CFG, max_live=1), apply=True, fx=fx(), now=NOW + 600)
check("a failed launch stops the item (one Needs Conductor line), the next item gets the slot",
      rd["items"]["SELFTEST_FIX_ALPHA_AAAA"]["decision"] == "stopped" and
      rd["items"]["SELFTEST_FIX_BETA_BBBB"]["decision"] == "launched" and len(CALLS["launch"]) == n0 + 2, rd["items"])

# ---- acceptance test (B): started_check over fake ledger events ------------------------------------------------------
st = {"items": {"SELFTEST_FIX_ALPHA_AAAA": {"attempts": [{"night": "x"}]}, "SELFTEST_FIX_BETA_BBBB": {"attempts": [{}]},
                "SELFTEST_FIX_GAMMA_CCCC": {}}}
evs = [{"event": "spawn", "name": "SELFTEST_FIX_ALPHA_AAAA", "seat": "RUNNER", "ts": "2026-11-14T12:00:00Z"},
       {"event": "start", "id": "SELFTEST_FIX_ALPHA_AAAA", "seat": "CONDUCTOR", "ts": "2026-11-14T13:00:00Z",
        "role_unit": "rm-detached-bench-selftest-fix-alpha-aaaa-1"},
       {"event": "spawn", "name": "SELFTEST_FIX_BETA_BBBB", "seat": "RUNNER", "ts": "2026-11-14T12:00:00Z"},
       {"event": "start", "id": "SELFTEST_FIX_BETA_BBBB", "seat": "CONDUCTOR", "ts": "2026-11-14T13:00:00Z"},
       {"event": "start", "id": "SELFTEST_FIX_BETA_BBBB", "seat": "BENCH", "ts": "2026-11-16T13:00:00Z"}]
rc, lines = RD.started_check(24, events=evs, st=st)
check("started_check: a detached fixer's start (written CONDUCTOR, role_unit rm-detached-*) within 24 h passes; "
      "the Conductor window's own start or a late one does not",
      rc == 1 and lines[0].startswith("PASS  SELFTEST_FIX_ALPHA") and lines[1].startswith("FAIL  SELFTEST_FIX_BETA")
      and "1 of 2" in lines[-1], lines)
rc, lines = RD.started_check(24, events=evs, st=dict(st, live_since=RD.dt.datetime(2026, 11, 14, 12, 30, tzinfo=RD.dt.timezone.utc).timestamp()))
check("started_check: items filed before the step went live are listed, not counted; none counted is UNMEASURED",
      rc == 2 and lines[0].startswith("BEFORE  SELFTEST_FIX_ALPHA") and "UNMEASURED" in lines[-1], lines)
check("builder_start: OWNER never, a bare CONDUCTOR window never, a detached unit and another seat yes",
      [RD.builder_start(e) for e in ({"seat": "OWNER", "role_unit": "rm-detached-x"}, {"seat": "CONDUCTOR"},
                                     {"seat": "CONDUCTOR", "role_unit": "rm-conductor-window"},
                                     {"seat": "CONDUCTOR", "role_unit": "rm-detached-x"}, {"seat": "STEVE"})]
      == [False, False, False, True, True])
rc, lines = RD.started_check(24, events=evs, st={"items": {}})
check("started_check with no launches is UNMEASURED (rc 2), never a pass", rc == 2, lines)

# ---- the dead Relentless pool route is gone (acceptance test A) ------------------------------------------------------
s = "".join(open(os.path.join(REPO, p), encoding="utf-8").read() for p in (
    "src/RimMandrake/Utils/ops_watch_rules.json", "src/RimMandrake/Utils/ops_watch.py", "src/RimMandrake/Utils/known_reds.py"))
n = len(re.findall(r"relentless pool_order|first in relentless|relentless. pool", s))
check("no relentless pool route left in ops_watch, its rules or known_reds (acceptance A)", n == 0, n)

# ---- the unit ------------------------------------------------------------------------------------------------------
sysd = os.path.join(REPO, "src", "RimMandrake", "Utils", "systemd")
svc = open(os.path.join(sysd, "rm-red-dispatch.service"), encoding="utf-8").read()
tmr = open(os.path.join(sysd, "rm-red-dispatch.timer"), encoding="utf-8").read()
check("rm-red-dispatch.service runs red_dispatch.py tick --apply from the dispatch clone",
      "red_dispatch.py tick --apply" in svc and "WorkingDirectory=/home/mandrake/rm/dispatch" in svc)
check("rm-red-dispatch.timer fires every 10 min", "OnUnitActiveSec=10min" in tmr)

print("RESULT: %s (%d fail)" % ("GREEN" if not FAILS else "RED", len(FAILS)))
sys.exit(1 if FAILS else 0)
