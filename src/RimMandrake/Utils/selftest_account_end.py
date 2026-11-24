#!/usr/bin/env python3
"""selftest: the end of an account (RIMMANDRAKE_BUILD_ACCOUNT_END_WARN_SAVE_PAUSE_SWITCH_SIZED_BY_BURN; page
design/specs/2026-11-24-account-end/boundary.md). One check per promise, by its name. Planted readings, a fake switcher,
a fake clock and scratch dirs only: it never reads the live meter, the live runs or the real switcher. The planted
faults: account_end_mutants.py.

    python3 src/RimMandrake/Utils/selftest_account_end.py
"""
import json
import os
import stat
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
TMP = Path(tempfile.mkdtemp(prefix="selftest_account_end_"))
os.environ["RM_SWITCH_PLAN_DIR"] = str(TMP / "out")
os.environ["RM_ACCOUNTS_DIR"] = str(TMP / "accounts")
os.environ["RM_CONTROL_DB"] = str(TMP / "control.db")
os.environ["RM_DISPATCHER_STATE"] = str(TMP / "state")
os.environ.setdefault("RM_UNDER_SELFTEST", "1")
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "rimflow"))
import account_end as AE  # noqa: E402
import switching_plan as SP  # noqa: E402

FAILS = []
NOW = 1_800_000_000.0
PLAN = json.loads((HERE / "switching_plan.json").read_text())
PLAN["exceptions"] = []
CFG = PLAN["account_end"]
(TMP / "plan.json").write_text(json.dumps(PLAN))
SP.PLAN_PATH = TMP / "plan.json"
RUN = ["rm-detached-bench-rimmandrake-some-builder-1795180000"]
ORD = {"rate": 0.067, "stale": False, "age_s": 0, "span_min": 45, "why": ""}
FAST = {"rate": 0.25, "stale": False, "age_s": 0, "span_min": 45, "why": ""}
STALE = AE.stale_burn("the newest reading is 33 min old")


def check(name, ok, detail=""):
    print(("ok    " if ok else "FAIL  ") + name + ("" if ok or not detail else ": " + str(detail)[:400]))
    if not ok:
        FAILS.append(name)


def R(left, h, src="MEASURED", age=1.0, stale=False):
    return {"source": src, "week_pct_left": left, "week_pct_used": None if left is None else 100 - left,
            "hours_to_week_reset": h, "week_resets_at": SP.iso(NOW + h * 3600), "stale": stale, "age_min": age}


OFF = {"steven": R(90, 100)}     # outside his 48 h window


def m(left, lukas=98):
    return {**OFF, "system": R(left, 100), "lukas": R(lukas, 120)}


def D(meter, live, runs=(), burn=ORD, state=None):
    return SP.decide(meter, live, NOW, PLAN, dict(state or {}), markers={}, polled=True, live_runs=runs, burn=burn)


class Fake:
    """The machine: a switcher that records its calls, live runs, the order channel, and a clock that only sleep moves."""

    def __init__(self, live="system", runs=RUN, burn=ORD, send_err=None):
        self.live, self.runs, self.burn, self.sent, self.slept, self.err = live, list(runs), burn, [], [], send_err
        self.t, self.withdrawn, self.on_sleep = NOW, [], None
        for k in list(SP.read_markers()):
            (SP.OUT / "markers" / f"{k}.json").unlink()
        for f in ("notice.json", "state.json", "log.jsonl", "HOLD"):
            (SP.OUT / f).unlink(missing_ok=True)
        self.calls = TMP / "calls.txt"
        self.calls.write_text("")
        sw = TMP / "claude-account"
        sw.write_text("#!/bin/sh\necho \"$@\" >> %s\n[ \"$1\" = use ] && echo \"$2\" > %s\nif [ \"$1\" = \"--json\" ]; then "
                      "echo '{\"live\": \"'$(cat %s)'\", \"machine\": \"testbox\", \"armed\": true}'; fi\nexit 0\n"
                      % (self.calls, TMP / "live.txt", TMP / "live.txt"))
        sw.chmod(sw.stat().st_mode | stat.S_IEXEC)
        (TMP / "live.txt").write_text(live)
        SP.CA = str(sw)
        SP.clock = lambda: self.t
        SP.sleep = self.sleep

    # the order channel
    def store_runs(self):
        return list(self.runs)

    def send(self, units, mode, text, deadline=None):
        if self.err:
            return None, self.err
        self.sent.append({"units": units, "mode": mode, "text": text, "deadline": deadline, "at": self.t,
                          "used": "use" in self.acts() or "fleet-stop" in self.acts()})
        return "ct_%d" % len(self.sent), None

    def withdraw(self, acts, why):
        self.withdrawn += acts
        return len(acts), None

    def saved(self, unit, since):
        return "still live; no note seen since its order" if unit in self.runs else "ended by itself before the switch"

    def sleep(self, s):
        self.slept.append(s)
        self.t += s
        if self.on_sleep:
            self.on_sleep()

    def go(self, meter, runs="own", passes=1):
        SP.check(dry=False, now=self.t if passes == 1 else None, meter_fn=meter if callable(meter) else lambda: meter,
                 poll_fn=lambda: None, runs_fn=(lambda: list(self.runs)) if runs == "own" else runs,
                 burn_fn=lambda *a: self.burn, orders=self, passes=passes)

    def acts(self):
        return [ln.split()[0] for ln in self.calls.read_text().splitlines() if ln.split() and ln.split()[0] != "--json"]

    def notice(self):
        return json.loads((SP.OUT / "notice.json").read_text())

    def state(self):
        return SP.load_state()

    def steps(self):
        return [r for r in (json.loads(x) for x in (SP.OUT / "log.jsonl").read_text().splitlines())
                if r.get("do") == "account_end"]


# ------------------------------------------------------------------ the numbers
def t_the_warning_fires_at_two_at_an_ordinary_burn():
    n = "the-warning-fires-at-two-at-an-ordinary-burn"
    for ln in (1, 2):
        check("%s: line %s" % (n, ln), AE.warning_line(ln, ORD, CFG) == 2, AE.warning_line(ln, ORD, CFG))
    for left, want in ((4, False), (3, False), (2, True)):
        d = D(m(left), "system", RUN)
        check("%s: at %s%%" % (n, left), bool(d.get("account_end")) is want and d["do"] in ("soft", "normal"), d)
    f = Fake()
    for left, orders in ((4, 0), (3, 0), (2, 1)):
        f.go(m(left))
        check("%s: %d order(s) at %s%%" % (n, orders, left), len(f.sent) == orders, f.sent)
    check("%s: no switch while the run lives" % n, "use" not in f.acts(), f.acts())
    check("%s: an easy-spot order to the run" % n, f.sent and f.sent[0]["mode"] == "at_easy_spot" and
          f.sent[0]["units"] == RUN, f.sent)


def t_the_warning_fires_at_three_at_a_fast_burn():
    n = "the-warning-fires-at-three-at-a-fast-burn"
    check("%s: line 1" % n, AE.warning_line(1, FAST, CFG) == 3)
    check("%s: the edge is save_need_min" % n, AE.warning_line(1, dict(FAST, rate=0.1), CFG) == 2
          and AE.warning_line(1, dict(FAST, rate=0.101), CFG) == 3)
    check("%s: steven's 52 stays 52 at a fast burn (51 points above 1%%)" % n, AE.warning_line(52, FAST, CFG) == 52)
    check("%s: a 3%% line is 3, and 4 at 0.25%% a minute" % n, AE.warning_line(3, ORD, CFG) == 3
          and AE.warning_line(3, FAST, CFG) == 4)
    f = Fake(burn=FAST)
    f.go(m(6))
    check("%s: nothing at 6%%" % n, not f.sent, f.sent)
    f.go(m(3))
    check("%s: the order at 3%%" % n, len(f.sent) == 1, f.sent)


def t_the_burn_is_the_slope_of_this_week():
    n = "the-warning-fires-at-three-at-a-fast-burn"
    rs = SP.iso(NOW + 3 * 86400)

    def rows(pts, acct="lukas", reset=rs, src="MEASURED"):
        return [{"account": acct, "source": src, "measured_at": SP.iso(NOW - a * 60), "week_pct_used": u,
                 "week_resets_at": reset} for a, u in pts]
    today = rows([(142, 55), (127, 57), (112, 59), (97, 60), (82, 61), (67, 62), (52, 63), (37, 66), (22, 67), (7, 69)])
    b = AE.burn_of(today, "lukas", NOW, CFG)
    check("%s: the burn of 45 min" % n, not b["stale"] and abs(b["rate"] - 6 / 45) < 1e-6 and abs(b["age_s"] - 420) < 2, b)
    b = AE.burn_of(rows([(60, 95)], reset=SP.iso(NOW - 1800)) + rows([(25, 0), (10, 2)]), "lukas", NOW, CFG)
    check("%s: a reset inside the window is no burn" % n, not b["stale"] and abs(b["rate"] - 2 / 15) < 1e-6, b)
    b = AE.burn_of(rows([(40, 95), (25, 0), (10, 1)]), "lukas", NOW, CFG)
    check("%s: a refill with the reset time unchanged is no burn (steven, 2026-11-22)" % n,
          not b["stale"] and abs(b["rate"] - 1 / 15) < 1e-6, b)
    b = AE.burn_of(rows([(40, 10), (25, 11), (10, 12)], acct="system"), "lukas", NOW, CFG)
    check("%s: another account's readings are not lukas's" % n, b["stale"] and b["rate"] is None, b)
    b = AE.burn_of(rows([(40, 10), (25, 11), (5, 30)])[:2] + rows([(5, 30)], src="ESTIMATE"), "lukas", NOW, CFG)
    check("a-stale-reading-uses-the-safe-values: an estimate is no reading", b["stale"], b)
    check("a-stale-reading-uses-the-safe-values: no readings", AE.burn_of([], "lukas", NOW, CFG)["stale"])
    b = AE.burn_of(rows([(60, 10), (45, 11), (21, 12)]), "lukas", NOW, CFG)
    check("a-stale-reading-uses-the-safe-values: newest 21 min old", b["stale"] and "21 min" in b["why"], b)
    b = AE.read_burn("lukas", NOW, CFG, path=TMP / "absent.jsonl")
    check("a-stale-reading-uses-the-safe-values: an unreadable series", b["stale"] and "unreadable" in b["why"], b)
    (TMP / "series.jsonl").write_text("{torn\n" + "\n".join(json.dumps(r) for r in today) + "\n")
    b = AE.read_burn("lukas", NOW, CFG, path=TMP / "series.jsonl")
    check("%s: read from the series file, a torn line skipped" % n, not b["stale"] and b["rate"] > 0.13, b)


def t_the_order_tells_the_numbers():
    n = "the-order-tells-the-numbers"
    w = AE.warn_text("lukas", 2, ORD, 1, CFG, False)
    check("%s: percent, burn and minutes" % n, "2% of its week" in w and "0.067% a minute" in w and "14 minutes" in w
          and "switches accounts" in w, w)
    check("%s: his words and the note that carries the work on" % n,
          "wrap it up cleanly and safely save your work" in w and "LEFT OPEN:" in w and "ACCOUNT END" in w, w)
    check("%s: no spend of the run" % n, "token" not in w and "$" not in w and "budget" not in w, w)
    e = AE.emergency_text("lukas", 1, ORD, 89, False)
    check("%s: the emergency's" % n, "1% of its week" in e and "0.067%" in e and "89 seconds" in e and
          "emergency: record your state immediately and prepare for termination" in e, e)
    k = AE.warn_text("steven", 52, ORD, 52, CFG, False)
    check("%s: a kept account's order promises no emergency" % n, "no emergency step" in k and "minutes to" not in k, k)
    z = AE.warn_text("lukas", 2, ORD, 2, CFG, True)
    check("%s: the last account's order says that the machine stops" % n, "stops until an account resets" in z, z)
    age = AE.minutes_left(2, dict(ORD, age_s=300), CFG)
    check("%s: the age of the reading comes off the minutes" % n, abs(age - (1 / 0.067 - 5)) < 0.01, age)


def t_no_new_work_after_the_warning():
    import detached_helper as DH
    n = "no-new-work-after-the-warning"
    f = Fake()
    f.go(m(2))
    nt = f.notice()
    check("%s: the notice" % n, nt["state"] == "soft" and nt["drain"] is True and nt["account_end"] is True, nt)
    p = str(SP.OUT / "notice.json")
    for what, a in (("a new run", ({}, None)), ("a continuation", ({"continued_from": "rm-x"}, None)),
                    ("a resume", ({}, "sess-1"))):
        check("%s: %s is refused" % (n, what), bool(DH.drain_refusal(f.t + 30, *a, path=p)))
    check("%s: a stale notice refuses nothing" % n, DH.drain_refusal(f.t + 1800, {}, None, path=p) is None)
    Path(p).write_text(json.dumps(dict(nt, account_end=False)))
    check("%s: a drain that is no account end lets a continuation and a resume go" % n,
          DH.drain_refusal(f.t + 30, {"continued_from": "rm-x"}, None, path=p) is None
          and DH.drain_refusal(f.t + 30, {}, "s", path=p) is None and bool(DH.drain_refusal(f.t + 30, {}, None, path=p)))


def t_the_switch_goes_when_the_last_run_ends():
    n = "the-switch-goes-when-the-last-run-ends"
    f = Fake()
    f.go(m(2))
    check("%s: not while the run lives" % n, "use" not in f.acts(), f.acts())
    f.runs = []
    f.t += 300
    f.go(m(2))
    check("%s: at 2%%, at once, with no pause" % n, f.acts() == ["use"] and not f.slept, (f.acts(), f.slept))
    check("%s: no emergency order" % n, [s["mode"] for s in f.sent] == ["at_easy_spot"], f.sent)
    f = Fake(burn=FAST)
    f.go(m(3))
    f.runs = []
    f.go(m(3))
    check("%s: at 3%% too, after a fast burn" % n, "use" in f.acts(), f.acts())


def t_the_warning_is_latched():
    n = "the-warning-is-latched"
    f = Fake(burn=FAST)
    f.go(m(3))
    f.burn = ORD
    f.t += 300
    f.go(m(3))
    check("%s: a slower burn keeps it" % n, f.notice()["account_end"] is True, f.notice())
    f.runs = []
    f.go(m(3))
    check("%s: and the switch goes at 3%%" % n, "use" in f.acts(), f.acts())
    f = Fake()
    f.go(m(2))
    f.go(m(100))
    check("%s: a reset takes it back and withdraws its orders" % n,
          f.withdrawn == ["ct_1"] and "account_end" not in f.state() and not f.notice().get("account_end"),
          (f.withdrawn, f.state()))


def t_the_emergency_orders_pauses_then_switches():
    n = "the-emergency-orders-pauses-then-switches"
    f = Fake()
    f.go(m(2))
    f.t += 300
    t0 = f.t
    f.go(m(1))
    em = [s for s in f.sent if s["mode"] == "write_now"]
    want = AE.pause_s(ORD, CFG)
    check("%s: the order" % n, len(em) == 1 and em[0]["units"] == RUN and not em[0]["used"], f.sent)
    check("%s: the pause is %d s" % (n, want), sum(f.slept) == want, f.slept)
    check("%s: the order's deadline is the end of the pause" % n, em and abs(em[0]["deadline"] - (t0 + want)) < 1, em)
    check("%s: then the switch, and no run killed by hand" % n, f.acts() == ["use"], f.acts())
    # the last run ends in the pause
    f = Fake()
    f.on_sleep = lambda: f.runs.clear()
    f.go(m(1))
    check("%s: the switch comes sooner when the last run ends" % n, f.acts() == ["use"] and sum(f.slept) <= 5, f.slept)
    # a pass that died in the pause
    f = Fake()
    SP.save_state({"account_end": {"account": "system", "warn_line": 2, "ordered": {RUN[0]: {"emergency": NOW - 60}},
                                   "emergency": {"at": NOW - 60, "pause_s": 89}}})
    f.go(m(1))
    check("%s: a dead pass's pause is not started again" % n, sum(f.slept) == 29 and f.acts() == ["use"], f.slept)
    check("%s: nor its order sent twice" % n, not f.sent, f.sent)
    # the order could not be written: the machine's own step still goes
    f = Fake(send_err="Unreadable: locked")
    f.go(m(1))
    check("%s: an order that cannot be written stops nothing, and is said" % n, f.acts() == ["use"] and
          any("could NOT be written" in r["text"] for r in f.steps()), f.steps())


def t_the_pause_keeps_the_chance_of_zero_under_ten_percent():
    n = "the-pause-keeps-the-chance-of-zero-under-ten-percent"
    check("%s: 89 s at 2026-11-24's burn" % n, AE.pause_s(ORD, CFG) == 89, AE.pause_s(ORD, CFG))
    check("%s: 24 s at 0.25%% a minute" % n, AE.pause_s(FAST, CFG) == 24, AE.pause_s(FAST, CFG))
    check("%s: 180 s at most" % n, AE.pause_s(dict(ORD, rate=0.005), CFG) == 180
          and AE.pause_s(dict(ORD, rate=0.0), CFG) == 180)
    check("%s: 20 s at least" % n, AE.pause_s(dict(ORD, rate=5.0), CFG) == 20)
    check("%s: the age of the reading comes off" % n, AE.pause_s(dict(ORD, age_s=60), CFG) == 29)
    for rate in (0.02, 0.067, 0.1, 0.25):      # a true level uniform in (0, 1), the worst reading of "1%"
        spent = AE.pause_s(dict(ORD, rate=rate), CFG) / 60 * rate
        check("%s: at %s%% a minute it spends %.3f points" % (n, rate, spent), spent <= 0.1 + 1e-9, spent)


def t_a_stale_reading_uses_the_safe_values():
    n = "a-stale-reading-uses-the-safe-values"
    for b in (STALE, None):
        check("%s: the warning line is 3" % n, AE.warning_line(1, b, CFG) == 3)
        check("%s: the pause is the shortest" % n, AE.pause_s(b, CFG) == 20)
    f = Fake(burn=STALE)
    f.go(m(3))
    check("%s: the order at 3%% says stale" % n, len(f.sent) == 1 and "STALE" in f.sent[0]["text"]
          and "33 min old" in f.sent[0]["text"] and "assume 10 minutes" in f.sent[0]["text"], f.sent)
    f.go(m(1))
    check("%s: the emergency says stale, the pause is 20 s" % n, "STALE" in f.sent[-1]["text"]
          and "20 seconds" in f.sent[-1]["text"] and sum(f.slept) == 20, (f.sent, f.slept))
    f = Fake()
    SP.check(dry=False, now=f.t, meter_fn=lambda: m(3), poll_fn=lambda: None, runs_fn=lambda: RUN,
             burn_fn=lambda *a: 1 / 0, orders=f)
    check("%s: a burn reader that raises is stale, not slow" % n, len(f.sent) == 1 and "STALE" in f.sent[0]["text"], f.sent)
    d = D({**OFF, "system": R(3, 100, src="ESTIMATE", age=40, stale=True), "lukas": R(98, 120)}, "system", RUN, STALE)
    check("%s: a level that cannot be read again is warned at 3%%" % n, d.get("account_end") is True, d)
    f = Fake()
    f.go({**OFF, "system": R(0.8, 100, src="ESTIMATE", age=40, stale=True), "lukas": R(98, 120)})
    check("%s: a blind meter at its last 0.8%%: the emergency, 20 s, the switch" % n,
          [s["mode"] for s in f.sent] == ["write_now"] and sum(f.slept) == 20 and f.acts() == ["use"], (f.sent, f.slept))


def t_a_kept_account_has_no_emergency():
    n = "a-kept-account-has-no-emergency"
    for left in (52, 51, 50, 40, 10, 2):
        d = D({"steven": R(left, 150), "system": R(40, 100), "lukas": R(98, 120)}, "steven", RUN)
        check("%s: at %s%% with a run live it waits" % (n, left), d["do"] == "soft" and d.get("account_end")
              and not d.get("emergency"), d)
    for left in (1, 0):
        d = D({"steven": R(left, 150), "system": R(40, 100), "lukas": R(98, 120)}, "steven", RUN)
        check("%s: no emergency at %s%%" % (n, left), not d.get("emergency"), d)
    f = Fake(live="steven")
    f.go({"steven": R(52, 150), "system": R(40, 100), "lukas": R(98, 120)})
    f.go({"steven": R(49, 150), "system": R(40, 100), "lukas": R(98, 120)})
    check("%s: the warning only, no switch" % n, [s["mode"] for s in f.sent] == ["at_easy_spot"] and not f.acts(), f.sent)
    f.runs = []
    f.go({"steven": R(49, 150), "system": R(40, 100), "lukas": R(98, 120)})
    check("%s: the switch when the last run ends" % n, f.acts() == ["use"] and not f.slept, f.acts())
    d = D({"steven": R(80, 110), "system": R(40, 100), "lukas": R(98, 120)}, "steven", RUN)
    check("%s: past his window at 80%% the runs finish, nobody is told to end" % n, d["do"] == "soft" and d.get("drain")
          and not d.get("account_end"), d)


def t_the_last_account_goes_dark_and_comes_back():
    n = "the-last-account-goes-dark-and-comes-back"
    last = lambda left: {**OFF, "system": R(0.5, 100), "lukas": R(left, 120)}      # noqa: E731
    f = Fake(live="lukas")
    f.go(last(2))
    check("%s: the warning, no switch, no stop" % n, [s["mode"] for s in f.sent] == ["at_easy_spot"] and not f.acts()
          and "stops until an account resets" in f.sent[0]["text"], (f.sent, f.acts()))
    f.go(last(1))
    check("%s: the emergency, the pause, then the stop" % n, f.sent[-1]["mode"] == "write_now" and f.acts() == ["fleet-stop"]
          and sum(f.slept) == AE.pause_s(ORD, CFG) and f.state().get("stopped"), (f.acts(), f.slept))
    n_sent = len(f.sent)
    f.go(last(1))
    check("%s: DARK orders nothing more" % n, len(f.sent) == n_sent and f.acts() == ["fleet-stop"], f.acts())
    f.runs = []
    f.go({**OFF, "system": R(0.5, 100), "lukas": R(100, 167)})
    check("%s: its own reset starts the fleet" % n, f.acts() == ["fleet-stop", "fleet-start"] and "stopped" not in f.state()
          and f.notice()["state"] == "none", (f.acts(), f.state()))
    f = Fake(live="lukas", runs=[])
    f.go(last(2))
    check("%s: at its own 2%% line with no run live: the stop" % n, f.acts() == ["fleet-stop"], f.acts())
    f.go({**OFF, "system": R(100, 167), "lukas": R(2, 110)})
    check("%s: another account's reset switches to it" % n, f.acts()[-1] == "use" and "stopped" not in f.state()
          and f.notice()["state"] == "none", (f.acts(), f.notice()))
    f = Fake(live="lukas", runs=[], burn=FAST)
    f.go(last(3))
    check("%s: at 3%% (a fast burn), above its 2%% line: no new start, no stop" % n, not f.acts()
          and f.notice()["account_end"] is True, (f.acts(), f.notice()))


def t_a_one_percent_line_is_not_killed_unwarned():
    n = "a-one-percent-line-is-not-killed-unwarned"
    d = D(m(2), "system", RUN)
    check("%s: 2%% drains" % n, d["do"] == "soft" and d.get("drain") is True, d)
    f = Fake()
    f.go(m(1))      # even with no pass at 2%
    check("%s: 1%% orders and pauses before the switch" % n, f.sent and not f.sent[0]["used"] and sum(f.slept) >= 20
          and f.acts() == ["use"], (f.sent, f.slept, f.acts()))


def t_unreadable_runs_count_as_live():
    n = "unreadable-runs-count-as-live"
    d = D(m(2), "system", None)
    check("%s: 2%% drains, UNMEASURED" % n, d.get("account_end") is True and "UNMEASURED" in d["why"], d)
    f = Fake()
    f.go(m(1), runs=lambda: None)
    check("%s: 1%% orders the store's runs, pauses whole and switches" % n, f.sent and f.sent[0]["units"] == RUN
          and sum(f.slept) == AE.pause_s(ORD, CFG) and f.acts() == ["use"], (f.sent, f.slept))


def t_each_step_is_recorded_once():
    n = "each-step-is-recorded-once"
    f = Fake(runs=RUN + ["rm-detached-bench-other-1795180001"])
    f.go(m(2))
    f.go(m(2))
    f.runs = RUN[:]
    f.go(m(1))
    st = f.steps()
    check("%s: three steps, one line each" % n, [r["step"] for r in st] == ["save warning", "emergency", "switch"],
          [r["step"] for r in st])
    check("%s: each has percent, burn and runs" % n, all("% a minute" in r["text"] and "live run(s)" in r["text"] for r in st), st)
    check("%s: the switch says what each run had saved" % n, st and "other-1795180001: ended by itself before the switch"
          in st[-1]["text"] and "%s: still live; no note seen" % RUN[0] in st[-1]["text"], st)
    ev = f.state().get("account_end_events") or []
    check("%s: one ledger event owed for each" % n, len(ev) == 3 and "account_end" not in f.state(), f.state())
    # a run that shows up after the warning gets its order; the one that has it does not get it again
    f = Fake()
    f.go(m(2))
    f.runs = RUN + ["rm-role-designer-1795180009"]
    f.go(m(2))
    check("%s: a later run is ordered alone" % n, [s["units"] for s in f.sent] == [RUN, ["rm-role-designer-1795180009"]]
          and len(f.steps()) == 1, f.sent)
    (SP.OUT / "state.json").write_text(json.dumps({"account_end_events": ["a", "b"]}))
    old = AE.ledger_events
    try:
        AE.ledger_events = lambda t: ["b"]
        SP.flush_events()
        check("%s: an event that was not written stays owed" % n, f.state() == {"account_end_events": ["b"]}, f.state())
        AE.ledger_events = lambda t: 1 / 0
        SP.flush_events()
        check("%s: a writer that raises keeps it owed" % n, f.state() == {"account_end_events": ["b"]}, f.state())
        AE.ledger_events = lambda t: []
        SP.flush_events()
        check("%s: written, it is owed no more" % n, f.state() == {}, f.state())
    finally:
        AE.ledger_events = old


def t_an_order_spends_no_trial_and_blocks_nothing():
    import control as C
    n = "an-order-spends-no-trial-and-blocks-nothing"
    C.init(str(TMP / "control.db"))
    u = "rm-detached-bench-probe-1795180002"
    with C.txn() as c:
        c.execute("INSERT INTO runs (id, unit, family, item, state, started_at) VALUES (?,?,?,?,'started',?)",
                  (u, u, "detached", "RIMMANDRAKE_PROBE_ITEM", NOW))
        c.execute("INSERT INTO runs (id, unit, family, state, started_at) VALUES ('g','rm-game-deploy-1','game_deploy','started',?)",
                  (NOW,))
    o = AE.Orders()
    check("%s: the store's detached and role runs are the ones ordered" % n, o.store_runs() == [u], o.store_runs())
    text = AE.warn_text("lukas", 2, ORD, 1, CFG, False)
    act, err = o.send([u], "at_easy_spot", text)
    check("%s: the order is written" % n, bool(act) and err is None, err)
    with C.txn() as c:
        left = {t: c.execute("SELECT COUNT(*) FROM %s" % t).fetchone()[0] for t in ("switches", "voids", "reservations")}
    check("%s: no OFF switch, no void, no reservation touched" % n, not any(left.values()), left)
    code, said = C.hook(unit=u)
    check("the-order-tells-the-numbers: the run's own stop hook says it, numbers whole", code == 2 and text in said
          and "STOP ORDER" in said and "RIMMANDRAKE_PROBE_ITEM" in said, said)
    act2, _ = o.send([u], "write_now", AE.emergency_text("lukas", 1, ORD, 89, False), NOW + 89)
    code, said = C.hook(unit=u)
    check("the-order-tells-the-numbers: the emergency order replaces it", code == 2 and "89 seconds" in said
          and "write now" in said, said)
    check("the-warning-is-latched: withdrawn orders say so to their run", o.withdraw([act, act2], "reset")[0] == 2
          and "WITHDRAWN" in C.hook(unit=u)[1])
    check("the-warning-is-latched: and then say nothing", o.withdraw([act, act2], "reset")[0] == 0)
    check("each-step-is-recorded-once: a live run with no record could not be looked for",
          "no run record" in o.saved(u, NOW), o.saved(u, NOW))
    C.ended(u)
    check("each-step-is-recorded-once: an ended run had saved", o.saved(u, NOW) == "ended by itself before the switch",
          o.saved(u, NOW))
    os.rename(TMP / "control.db", TMP / "control.gone")
    try:
        blind = o.store_runs()
    except C.Unreadable as e:
        blind = e
    check("%s: an unreadable store is said: no list, no order, could not look" % n, isinstance(blind, C.Unreadable)
          and o.send([u], "write_now", "x")[0] is None and "could not look" in o.saved(u, NOW), blind)
    f = Fake()
    f.store_runs = o.store_runs
    f.go(m(2))
    check("unreadable-runs-count-as-live: an unreadable store: the runs of systemd are ordered, and the record says so",
          f.sent and f.sent[0]["units"] == RUN and "control store could not be read" in f.steps()[0]["text"], f.steps())


def t_a_wrapped_run_is_carried_on_after_the_switch():
    import left_open_continue as LOC
    n = "a-wrapped-run-is-carried-on-after-the-switch"
    unit = "rm-detached-bench-wrapped-%d" % int(NOW - 600)
    DH = LOC.DH
    rec = {"unit": unit, "item": "RIMMANDRAKE_WRAPPED_ITEM", "seat": "BENCH", "status": "finished", "at": NOW - 600,
           "ended": NOW - 60, "result": "success (exited 0)", "model": "opus", "state": str(TMP / "state"),
           "clone": str(TMP / "c"), "continue_plan": {"act": "continue", "target": "RIMMANDRAKE_WRAPPED_ITEM", "n": 1,
                                                      "why": "LEFT OPEN note"}}
    DH.write_record(rec)
    launched = []

    def launch(*a, **k):
        launched.append(a)
        return 0, "DETACHED rm-detached-bench-wrapped-2"
    ok = {k: (lambda _a: None) for k in LOC.GATES}
    kw = {"launch_fn": launch, "gates": ok, "reader": lambda t: {"state": "doing", "notes": []}, "log_path": str(TMP / "log.md")}
    SP.OUT.mkdir(parents=True, exist_ok=True)
    (SP.OUT / "notice.json").write_text(json.dumps({"state": "soft", "drain": True, "account_end": True, "at": SP.iso(NOW)}))
    x = LOC.run(unit, now=NOW, **kw)
    got = DH.read_record(unit)
    check("%s: not while the account ends" % n, not launched and "account switch" in x["why"] and got.get("continue_waits"), x)

    class Ran:
        returncode, stdout, stderr, refused, why = 0, "", "", False, ""
    kicks = []
    import control as C
    real, C.launch_unit = C.launch_unit, lambda argv, spec, **k: kicks.append(spec) or Ran()
    try:
        said = LOC.kick_waiting(NOW + 60, plan_dir=str(SP.OUT))
        check("%s: nor kicked then" % n, not kicks and DH.read_record(unit).get("continue_waits"), said)
        (SP.OUT / "notice.json").write_text(json.dumps({"state": "none", "at": SP.iso(NOW + 300)}))
        (SP.OUT / "log.jsonl").write_text(json.dumps({"do": "normal", "at": SP.iso(NOW + 300)}) + "\n")
        Ran.returncode = 1
        LOC.kick_waiting(NOW + 330, plan_dir=str(SP.OUT))
        check("%s: a kick that fails is owed still" % n, bool(DH.read_record(unit).get("continue_waits")))
        Ran.returncode = 0
        kicks.clear()
        LOC.kick_waiting(NOW + 360, plan_dir=str(SP.OUT))
        check("%s: the first pass with headroom starts it" % n, len(kicks) == 1 and kicks[0]["unit"] == unit + "-continue"
              and kicks[0].get("reuse_name") is True and not DH.read_record(unit).get("continue_waits"), kicks)
        LOC.kick_waiting(NOW + 400, plan_dir=str(SP.OUT))
        check("%s: once" % n, len(kicks) == 1, kicks)
    finally:
        C.launch_unit = real
    x = LOC.run(unit, now=NOW + 400, **kw)
    check("%s: and its step then launches" % n, x["act"] == "continued" and len(launched) == 1, x)


def t_a_switch_never_lands_on_an_ending_account():
    n = "a-switch-never-lands-on-an-ending-account"
    for left in (2, 3):
        d = D({**OFF, "system": R(left, 100), "lukas": R(40, 120)}, "lukas")
        check("%s: system at %s%% is no target" % (n, left), d["do"] == "normal", d)
    d = D({**OFF, "system": R(4, 100), "lukas": R(40, 120)}, "lukas")
    check("%s: system at 4%% is" % n, d["do"] == "switch" and d["to"] == "system", d)


def t_the_hold_file_stops_it():
    n = "the-hold-file-stops-it"
    f = Fake()
    f.on_sleep = lambda: (SP.OUT / "HOLD").write_text("x")
    f.go(m(1))
    check("%s: no switch" % n, f.acts() == [] and f.sent, f.acts())
    last = json.loads((SP.OUT / "log.jsonl").read_text().splitlines()[-1])
    check("%s: the pass ends in the pause, it does not try the switch" % n, last["do"] == "passive" and "pause" in last["why"], last)
    (SP.OUT / "HOLD").unlink()


def t_the_pass_repeats_while_an_account_ends():
    n = "the-switch-goes-when-the-last-run-ends"
    f = Fake()
    SP_t = {"n": 0}

    def meter():
        return m(2)

    def slept():
        SP_t["n"] += 1
        if SP_t["n"] == 2:
            f.runs = []
    f.on_sleep = slept
    f.go(meter, passes=5)
    check("%s: seen inside the same 5-min beat" % n, f.acts() == ["use"] and f.slept == [60, 60], (f.acts(), f.slept))
    f = Fake()
    f.go(lambda: m(40), passes=5)
    check("%s: a pass with no account ending does not repeat" % n, not f.slept, f.slept)
    f = Fake()
    f.go(lambda: m(2), passes=5)
    check("%s: at most 4 repeats" % n, f.slept == [60] * 4, f.slept)


def t_the_reading_is_fresh_at_the_end():
    n = "the-pause-keeps-the-chance-of-zero-under-ten-percent"
    polled = []
    f = Fake()
    for left, age, want in ((2, 1.0, 1), (2, 0.2, 0), (20, 4.0, 0)):
        polled.clear()
        (SP.OUT / "state.json").unlink(missing_ok=True)
        meter = {**OFF, "system": R(left, 100, age=age), "lukas": R(98, 120, age=0.1)}
        SP.check(dry=False, now=f.t, meter_fn=lambda: meter, poll_fn=lambda: polled.append(1), runs_fn=lambda: RUN,
                 burn_fn=lambda *a: ORD, orders=f)
        check("%s: at %s%%, a reading %s min old: %d poll(s)" % (n, left, age, want), len(polled) == want, polled)
    polled.clear()
    meter = {**OFF, "system": R(2, 100, age=1.0), "lukas": R(98, 120, age=0.1)}
    SP.save_state({"last_poll": SP.iso(f.t)})
    SP.check(dry=False, now=f.t + 60, meter_fn=lambda: meter, poll_fn=lambda: polled.append(1), runs_fn=lambda: RUN,
             burn_fn=lambda *a: ORD, orders=f)
    check("%s: each 60 s repeat reads the meter again" % n, polled == [1], polled)


def t_the_dark_notice_starts_nothing():
    import detached_helper as DH
    n = "no-new-work-after-the-warning"
    f = Fake(live="lukas", runs=[])
    f.go({**OFF, "system": R(0.5, 100), "lukas": R(1, 120)})
    p = str(SP.OUT / "notice.json")
    for what, a in (("a new run", ({}, None)), ("a continuation", ({"continued_from": "rm-x"}, None)), ("a resume", ({}, "s"))):
        check("%s: %s is refused while the fleet is stopped" % (n, what), f.notice()["state"] == "stop"
              and bool(DH.drain_refusal(f.t + 30, *a, path=p)), f.notice())
    import maturation_autonomy as MA
    check("%s: the tick reads that refusal as a wait, not a fault" % n,
          bool(MA.WAIT_REFUSAL.search(DH.drain_refusal(f.t + 30, {}, None, path=p) or "")))
    check("%s: a stop notice 30 min old refuses nothing" % n, DH.drain_refusal(f.t + 1800, {}, None, path=p) is None)
    f.go({**OFF, "system": R(0.5, 100), "lukas": R(100, 167)})
    check("%s: after the reset all start again" % n, DH.drain_refusal(f.t + 30, {}, None, path=p) is None)
    # while the switcher runs (about 13 s) the notice refuses a continuation too
    f = Fake(runs=[])
    seen, real = [], SP.armed_call

    def call(*a, **k):
        seen.append(DH.drain_refusal(f.t + 1, {"continued_from": "rm-x"}, None, path=p))
        return real(*a, **k)
    SP.armed_call = call
    try:
        f.go(m(2))
    finally:
        SP.armed_call = real
    check("%s: nor does a continuation start inside the switch" % n, f.acts() == ["use"] and seen and bool(seen[0]), seen)


def t_the_latch_ends_with_a_lowered_line():
    n = "the-warning-is-latched"
    f = Fake(live="steven")
    meter = {"steven": R(51, 150), "system": R(40, 100), "lukas": R(98, 120)}
    f.go(meter)
    check("%s: warned at 52" % n, len(f.sent) == 1, f.sent)
    low = dict(PLAN, accounts=dict(PLAN["accounts"], steven={"leave_pct_left": 5, "window_h_after_reset": None}))
    (TMP / "low.json").write_text(json.dumps(low))
    SP.PLAN_PATH = TMP / "low.json"
    try:
        f.runs = []
        f.go(meter)
    finally:
        SP.PLAN_PATH = TMP / "plan.json"
    st = {"account_end": {"account": "steven", "warn_line": 52, "line": 52}}
    d = SP.decide(meter, "steven", NOW, low, st, markers={}, polled=True, live_runs=[], burn=ORD)
    check("%s: the decision itself does not read the old latch" % n, d["do"] == "normal" and d["warn_line"] == 5, d)
    check("%s: his line lowered to 5: no switch at 51%%, the orders are withdrawn" % n, not f.acts()
          and f.withdrawn == ["ct_1"] and "account_end" not in f.state(), (f.acts(), f.withdrawn, f.state()))


def t_a_level_that_cannot_be_read_is_stale():
    n = "a-stale-reading-uses-the-safe-values"
    blind = lambda left: {**OFF, "system": R(left, 100, src="ESTIMATE", age=12), "lukas": R(98, 120)}     # noqa: E731
    f = Fake()      # the burn reads fresh, the level does not
    f.go(blind(3))
    check("%s: an unread level at 3%% is warned though the burn reads fresh" % n, len(f.sent) == 1
          and "STALE" in f.sent[0]["text"], f.sent)
    f = Fake()
    f.go(blind(0.8))
    check("%s: an unread 0.8%%: the emergency order and the record say stale" % n, f.sent and "STALE" in f.sent[0]["text"]
          and "STALE" in f.steps()[0]["text"] and sum(f.slept) == 20, (f.sent, f.steps()))
    f = Fake()
    f.go({**OFF, "system": R(3, 100, age=25), "lukas": R(98, 120)})
    check("%s: a level 25 min old is stale too" % n, len(f.sent) == 1 and "STALE" in f.sent[0]["text"], f.sent)


def t_the_burn_is_only_of_the_time_it_was_live():
    n = "the-pause-keeps-the-chance-of-zero-under-ten-percent"
    rs = SP.iso(NOW + 3 * 86400)
    rows = [{"account": "lukas", "source": "MEASURED", "measured_at": SP.iso(NOW - a * 60), "week_pct_used": u,
             "week_resets_at": rs} for a, u in ((45, 95), (30, 95), (15, 95), (8, 96), (0, 97))]
    b = AE.burn_of(rows, "lukas", NOW, CFG, since=NOW - 15 * 60)
    check("%s: idle readings from before the switch to it are no burn" % n, not b["stale"] and abs(b["rate"] - 2 / 15) < 1e-6, b)
    b = AE.burn_of(rows, "lukas", NOW, CFG, since=NOW - 5 * 60)
    check("%s: 5 min after a switch the burn is stale" % n, b["stale"], b)
    log = SP.SWITCH_LOG
    log.parent.mkdir(parents=True, exist_ok=True)
    log.write_text("".join(json.dumps({"op": "use", "from": f, "to": t, "changed": True, "ts": SP.iso(NOW - a)}) + "\n"
                           for f, t, a in (("system", "lukas", 9000), ("lukas", "system", 5000), ("system", "lukas", 900))))
    check("%s: since is the last switch to it" % n, SP.live_since("lukas") == NOW - 900 and SP.live_since("system") is None,
          (SP.live_since("lukas"), SP.live_since("system")))
    log.unlink()


def main():
    real_clock, real_sleep = SP.clock, SP.sleep
    for t in (t_the_warning_fires_at_two_at_an_ordinary_burn, t_the_warning_fires_at_three_at_a_fast_burn,
              t_the_burn_is_the_slope_of_this_week, t_the_order_tells_the_numbers, t_no_new_work_after_the_warning,
              t_the_switch_goes_when_the_last_run_ends, t_the_warning_is_latched,
              t_the_emergency_orders_pauses_then_switches, t_the_pause_keeps_the_chance_of_zero_under_ten_percent,
              t_a_stale_reading_uses_the_safe_values, t_a_kept_account_has_no_emergency,
              t_the_last_account_goes_dark_and_comes_back, t_a_one_percent_line_is_not_killed_unwarned,
              t_unreadable_runs_count_as_live, t_each_step_is_recorded_once,
              t_an_order_spends_no_trial_and_blocks_nothing, t_a_wrapped_run_is_carried_on_after_the_switch,
              t_a_switch_never_lands_on_an_ending_account, t_the_hold_file_stops_it,
              t_the_pass_repeats_while_an_account_ends, t_the_reading_is_fresh_at_the_end,
              t_the_dark_notice_starts_nothing, t_the_latch_ends_with_a_lowered_line, t_a_level_that_cannot_be_read_is_stale,
              t_the_burn_is_only_of_the_time_it_was_live):
        try:
            t()
        except Exception as e:  # noqa: BLE001
            import traceback
            traceback.print_exc()
            check(t.__name__ + " raised", False, "%s: %s" % (type(e).__name__, e))
    SP.clock, SP.sleep = real_clock, real_sleep
    print("selftest_account_end: %s (%d failed)" % ("FAIL" if FAILS else "PASS", len(FAILS)))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
