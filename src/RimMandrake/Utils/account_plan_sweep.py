#!/usr/bin/env python3
"""The sweep of the account plan over burn regimes (page design/specs/2026-11-25-account-plan-sweep/boundary.md).

It runs the real pass (account_plan.tick, which drives account_actuator.check with account_plan.decide) every 5
minutes through a simulated week, over a grid of regimes. Stand-ins replace only what touches the world: the meter's
raw poll, the switcher, the live runs and their orders, the ssh door to SteveDesktop, the phone and the ledger. It
checks the wanted behaviour on every pass, computes the owner's measures and a foresight bound, and gives each region
of the grid one verdict. Deterministic: a regime and its seed give the same result every time. No model call; it
reads no live meter and writes only under its own scratch folder.

    account_plan_sweep.py tonight              the region of tonight's first real switch
    account_plan_sweep.py grid [--quick]       every region; --quick is the small fixed part that ./publish runs
    account_plan_sweep.py one '<regime json>'  one regime, every pass that broke a wanted behaviour
    account_plan_sweep.py grid --map <path>    write the regime map
"""
import argparse
import contextlib
import copy
import io
import json
import os
import random
import shutil
import sys
import tempfile
import time
from datetime import datetime, timedelta
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = Path(tempfile.mkdtemp(prefix="account_plan_sweep_"))
# the scratch world, set before the plan code is imported (account_actuator reads its folders at import)
os.environ.update({"RM_ACCOUNT_PLAN_DIR": str(ROOT / "plan"), "RM_SWITCH_PLAN_DIR": str(ROOT / "out"),
                   "RM_ACCOUNTS_DIR": str(ROOT / "accounts"), "RM_UNDER_SELFTEST": "1",
                   "RM_CONTROL_DB": str(ROOT / "control.db"), "RM_DISPATCHER_STATE": str(ROOT / "state")})
os.environ.pop("RM_ACCOUNT_PLAN_FRAME", None)
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "rimflow"))
import account_end as AE  # noqa: E402
import account_plan as AP  # noqa: E402
import account_usage as AU  # noqa: E402
import account_actuator as ACT  # noqa: E402
import fulltext  # noqa: E402

HOOK = HERE.parent.parent.parent / ".claude" / "hooks" / "switch_checkpoint_signal.py"
WEEK = 7 * 86400
PASS_S = 300
T0 = AP.stamp("2026-11-25T18:00:00-08:00")      # a Wednesday evening, the hour of tonight's switch
ACCTS = ("steven", "system", "lukas")
STEVE = "SteveDesktop"

# The wanted behaviour's numbers (the page, LIMITS, holds the danger and evidence of each).
K_STUCK = 36            # passes (3 h): the longest designed refusal with an account that can take over is a drain
#                         (rescue.drain_h 2 h, or a run that needs up to 120 min to save and end) plus 60 min of a meter
SAME_N = 288            # passes (24 h) of the same refusal with no input changed is stuck, whatever else holds
FLIP_H = 24             # hours: A -> B -> A with no reset between is churn
COSTLY_PTS = 10         # points of cost over the foresight bound (more than three switches' worth)


def _load_hook():
    import importlib.util
    spec = importlib.util.spec_from_file_location("switch_checkpoint_signal_sweep", str(HOOK))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


HK = _load_hook()


# ------------------------------------------------------------------ the plan of a regime
def today_plan():
    """Today's plan as this machine can build it: the first plan (steven 52% in his 48 h window, system 1%, lukas 1%,
    codex 25%), SteveDesktop listed. The live plan file is on Archmagi."""
    p = AP.first_plan()
    p.pop("ledger_item", None)
    p["machines"] = {STEVE: {"ssh": "stevedesktop-wsl"}}
    return p


def plan_of(reg, t0):
    p = today_plan()
    for path, v in (reg.get("numbers") or {}).items():     # a what-if on the sweep's copy of the plan, never the live one
        d = p["numbers"]
        keys = path.split(".")
        for k in keys[:-1]:
            d = d[k]
        d[keys[-1]] = v
    pv = reg.get("plan") or {}
    h = pv.get("at_h", 0)
    at = AP.iso(t0 + h * 3600)
    if pv.get("kind") == "hold":
        p["holds"].append({"id": "H1", "at": at, "ends": AP.iso(t0 + (h + pv.get("hours", 2)) * 3600), "why": "sweep"})
    elif pv.get("kind") == "pin":
        p["pins"].append({"account": pv["account"], "at": at, "ends": AP.iso(t0 + (h + pv.get("hours", 24)) * 3600)})
    elif pv.get("kind") == "line_until_reset":
        acc = pv["account"]
        s = copy.deepcopy(p["steps"][AP.find_step(p, acc)])
        s.update(name="tmp-" + acc, leave=pv["leave"], **{"from": at, "ends_at_reset_of": acc})
        s.pop("when", None) if pv.get("drop_when") else None
        p["steps"].insert(0, s)
    elif pv.get("kind") == "request":
        p["requests"].append({"to": pv["to"], "at": at, "ends": AP.iso(t0 + (h + 24) * 3600), "why": "sweep",
                              "now": bool(pv.get("now"))})
    for sc in reg.get("schedules") or []:
        if not sc.get("at_h"):
            put_sched(p, sc, reg, t0)
    return p


def assumed_reset(reg, t0, a, sc):
    """The reset that the owner typed the schedule against: the true first reset ahead, moved by drift_h."""
    r = t0 + reg["start"]["reset_h"][a] * 3600
    while r <= t0:
        r += WEEK
    return r + sc.get("drift_h", 0) * 3600


def sched_text(points, reset):
    """Points [hours before the reset, percent, how] as the text that the owner would type for that reset."""
    return "; ".join("%s=%s %s" % (AP.pacific_point(reset - hb * 3600), g(pct), how) for hb, pct, how in points)


def g(x):
    return AP.g(x)


def put_sched(p, sc, reg, t0):
    """The step of sc["account"] (its first step in force) takes the schedule, typed for the assumed reset."""
    a = sc["account"]
    text = sc.get("text") or sched_text(sc["points"], assumed_reset(reg, t0, a, sc))
    s = next(x for x in p["steps"] if x["use"] == a)
    try:
        AP.put_schedule(p, s, text)
    except AP.Refused:          # a text that a hand edit broke: kept as typed, its highest percent in leave
        s["schedule"] = text
        s["leave"] = max([float(x) for x in __import__("re").findall(r"=\s*(\d+(?:\.\d+)?)", text)] or [s["leave"]])
    return p


def oracle_line(sc, reset_assumed, t):
    """The line that the owner typed, at t, computed apart from the plan's code: from the regime's points as hours
    before the assumed reset (the week (reset - 7 days, reset]). None outside that week."""
    if not reset_assumed - WEEK < t <= reset_assumed:
        return None
    pts = sorted(sc["points"], key=lambda x: -x[0])
    h = (reset_assumed - t) / 3600
    for i, (hb, pct, how) in enumerate(pts):
        if h >= hb:
            if i == 0 or how != "ramp":
                return pct
            hb0, pct0 = pts[i - 1][0], pts[i - 1][1]
            return pct0 + (pct - pct0) * (hb0 - h) / (hb0 - hb)
    return pts[-1][1]


def typed_off(sc, reset_assumed, t, line, t_typed=None, jitter_h=0.0):
    """How far the plan's line is from the line as typed (oracle_line), or None where the check does not apply: within
    SNAP_S of either end of the week (the minutes in which the meter's reset and the true one disagree: the week's
    end and the next week's start are both right), and in a week that holds a daylight-saving change the typed points
    keep their Pacific clock while a reset fixed in UTC does not, so the line may be the typed one an hour away (t_typed:
    a moment of the week that the points were typed for). jitter_h: the meter's reset moves the point at the reset, and
    so the slope of a ramp to it, by up to that much: the line may be the typed one that many hours away."""
    if reset_assumed - t <= AP.SNAP_S or t - (reset_assumed - WEEK) <= AP.SNAP_S:
        return None
    off = lambda x: datetime.fromtimestamp(x, AP.TZ).utcoffset()     # noqa: E731
    dst = len({off(x) for x in (t, reset_assumed, reset_assumed - WEEK, t if t_typed is None else t_typed)}) > 1
    k = (1.0 if dst else 0.0) + abs(jitter_h)
    wants = [oracle_line(sc, reset_assumed, x) for x in ((t, t - k * 3600, t + k * 3600) if k else (t,))]
    wants = [x for x in wants if x is not None]
    if k and len(wants) > 1:        # any line between the typed ones an hour (or the jitter) either way
        return 0.0 if min(wants) - 0.6 <= line <= max(wants) + 0.6 else min(abs(x - line) for x in wants)
    return None if not wants else min(abs(x - line) for x in wants)


def change_mid_week(reg):
    """The writes of the plan in the middle of the week: [(hour, change)], in order."""
    out = []
    pv = reg.get("plan") or {}
    if pv.get("kind") == "order":
        order = pv["order"]

        def ch(p):
            p["steps"].sort(key=lambda s: order.index(s["use"]) if s["use"] in order else 99)
            return p
        out.append((pv.get("at_h", 24), ch))
    t0 = T0 + reg.get("t0_shift_s", 0)
    for sc in reg.get("schedules") or []:
        if sc.get("at_h"):
            out.append((sc["at_h"], lambda p, sc=sc: put_sched(p, sc, reg, t0)))
    return sorted(out, key=lambda x: x[0])


# ------------------------------------------------------------------ the world (the stand-ins)
def rate_at(b, h):
    """The burn of a consumer at hour h of the week, points of a week an hour."""
    if not b:
        return 0.0
    k = b.get("kind", "const")
    if k == "const":
        return b["rate"]
    if k == "step":
        return b["r0"] if h < b["at_h"] else b["r1"]
    if k == "burst":
        return b["peak"] if (h - b.get("phase_h", 0)) % b["period_h"] < b["on_h"] else b["base"]
    if k == "zero":
        return 0.0 if (h - b.get("phase_h", 0)) % 24 < b["zero_h"] else b["rate"]
    if k == "pulse":        # peak from from_h to to_h (each period_h when it has one), else base
        x = h - b["from_h"]
        if b.get("period_h"):
            x %= b["period_h"]
        return b["peak"] if 0 <= x < b["to_h"] - b["from_h"] else b["base"]
    raise ValueError("burn kind %s" % k)


class Machine:
    """The live runs of one machine. mode: none (no run: the windows burn), always (n runs, each started as soon as
    the gate lets it), never_ends (always, and one run never ends)."""

    def __init__(self, name, live, spec, rng):
        self.name, self.live, self.rng = name, live, rng
        self.mode = spec.get("mode", "always")
        self.n = spec.get("n", 3) if self.mode != "none" else 0
        self.save_min = spec.get("save_min", 20)
        self.dur = spec.get("dur_min", (24, 122))
        self.runs = []      # {name, start, end, save_by, forever}
        self.seq = 0
        self.ended_by_switch = 0
        self.burned = []    # (t, account, points): the last hour, for the burn reader

    def start(self, t, forever=False):
        self.seq += 1
        lo, hi = self.dur
        self.runs.append({"name": "rm-detached-sim-%s-%d" % (self.name.lower(), self.seq), "start": t,
                          "end": float("inf") if forever else t + self.rng.uniform(lo, hi) * 60, "save_by": None})

    def share(self):
        return 1.0 if self.mode == "none" else min(1.0, len(self.runs) / max(1, self.n))

    def tick(self, t):
        self.runs = [r for r in self.runs if r["end"] > t and (r["save_by"] is None or r["save_by"] > t)]

    def order(self, names, mode, t):
        """An order of the account end: save (at an easy spot) and the emergency (write now) end the run."""
        for r in self.runs:
            if r["name"] in names and mode in ("at_easy_spot", "write_now") and r["end"] != float("inf"):
                by = t + (self.save_min if mode == "at_easy_spot" else min(self.save_min, 2)) * 60
                r["save_by"] = by if r["save_by"] is None else min(r["save_by"], by)

    def told_save(self, t):
        for r in self.runs:
            if r["end"] != float("inf") and r["save_by"] is None:
                r["save_by"] = t + self.save_min * 60


class World:
    def __init__(self, reg):
        self.reg = reg
        self.rng = random.Random(reg.get("seed", 0))
        self.t0 = T0 + reg.get("t0_shift_s", 0)
        self.t = self.t0
        st = reg["start"]
        self.used = {a: 100.0 - st["left"][a] for a in ACCTS}
        self.start_left = {a: st["left"][a] for a in ACCTS}       # until its reset: what an overshoot is measured from
        self.reset = {a: self.t0 + st["reset_h"][a] * 3600 for a in ACCTS}
        for a in ACCTS:     # a reset that is already past at the start is the one of next week
            while self.reset[a] <= self.t0:
                self.reset[a] += WEEK
        self.arch = Machine("Archmagi", st["live"], reg.get("runs") or {}, self.rng)
        sd = reg.get("steve") or {}
        self.steve_on = sd.get("account", st["live"]) if sd.get("account") != "same" else st["live"]
        self.steve = Machine(STEVE, self.steve_on, sd.get("runs") or {"mode": "none"}, self.rng)
        self.steve_burn = sd.get("burn")
        self.steve_reach = sd.get("unreachable_h")      # [from, to] hours when ssh fails
        self.steve_runs_blind = sd.get("runs_unread_h")
        self.steve_notice = None
        self.laptop = reg.get("laptop")
        self.laptop_on = (self.laptop or {}).get("account") or st["live"]
        self.burn = reg.get("burn") or {"kind": "const", "rate": 6}
        mt = reg.get("meter") or {}
        self.meter_every = mt.get("every_min", 5)
        self.blackout = mt.get("blackout_h")            # [from, to]: no poll reads anything
        self.unread = mt.get("unread")                  # {account, from_h, to_h}: one account cannot be read
        self.post_reset_gap = mt.get("post_reset_gap_min", 0)
        self.reads = {}                                 # account -> raw record of its last poll
        self.series = []
        self.log = []
        self.stopped = False
        self.sw = reg.get("switcher") or {}
        self.sw_fails_left = 1 if self.sw.get("kind") == "fails_once" else 0
        self.events = []                               # switches, stops, resets: what the checks read
        self.erased = {a: 0.0 for a in ACCTS}
        self.idle_pts = 0.0
        self.refused_min = 0
        self.steve_refused_min = 0
        self.last_read_t = {a: None for a in ACCTS}
        self.plan_now = None
        # the measures of a line schedule (page design/specs/2026-11-27-account-line-schedule/boundary.md)
        self.under_min = {a: 0 for a in ACCTS}
        self.lowest_gap = {a: None for a in ACCTS}
        self.dark_min = 0.0
        self.fleet_under = 0.0
        self.line_cache = {}

    def h(self, t=None):
        return ((self.t if t is None else t) - self.t0) / 3600

    def left(self, a):
        return max(0.0, 100.0 - self.used[a])

    # ---- the meter
    def readable(self, a, t):
        h = self.h(t)
        if self.blackout and self.blackout[0] <= h < self.blackout[1]:
            return False
        u = self.unread
        if u and (u["account"] in (a, "all")) and u["from_h"] <= h < u["to_h"]:
            return False
        if self.post_reset_gap and any(self.reset[a] - WEEK <= t < self.reset[a] - WEEK + self.post_reset_gap * 60
                                       for _ in [0]):
            return False
        return True

    def poll(self, t):
        for a in ACCTS:
            if self.readable(a, t):
                rec = {"account": a, "ts": AP.iso(t), "measured_at": AP.iso(t), "source": "MEASURED",
                       "week_pct_used": float(round(self.used[a])), "week_resets_at": AP.iso(self.reset[a])}
                self.reads[a] = rec
                self.last_read_t[a] = t
                self.series.append(rec)
        cut = t - 26 * 3600
        if self.series and AP.stamp(self.series[0]["measured_at"]) < cut:
            self.series = [r for r in self.series if AP.stamp(r["measured_at"]) >= cut]

    def history(self):
        """24 h of readings before the start, on the burn of those hours: the burn is known at the first pass, as on a machine
        whose reader has run for days. Going back from the start, the burn comes off the live account while its level
        since its last reset can hold it, then off the account with the most used: the sum of the rises is the burn."""
        back = dict(self.used)
        rows = []
        for k in range(1, 289):
            t = self.t0 - k * PASS_S
            x = rate_at(self.burn, self.h(t)) * PASS_S / 3600     # the burn's own pattern, run backwards
            for a in [self.arch.live] + sorted(ACCTS, key=lambda b: -back[b]):
                if self.reset[a] - WEEK > t:
                    continue        # before this account's last reset: another week, not read here
                take = min(x, back[a])
                back[a] -= take
                x -= take
                if x <= 1e-9:
                    break
            for a in ACCTS:
                if self.reset[a] - WEEK <= t:
                    rows.append({"account": a, "ts": AP.iso(t), "measured_at": AP.iso(t), "source": "MEASURED",
                                 "week_pct_used": float(round(back[a])), "week_resets_at": AP.iso(self.reset[a])})
        self.series.extend(reversed(rows))

    def meter_rows(self):
        out = {}
        for a, rec in self.reads.items():
            d = AU.derive_record(rec, self.t)
            d["hours_to_week_reset"] = d.get("hours_to_week_reset")
            if self.unread and self.unread["account"] in (a, "all") and \
                    self.unread["from_h"] <= self.h() < self.unread["to_h"]:
                d.update(source="UNMEASURED", week_pct_left=None, why="sweep: this account cannot be read")
            out[a] = d
        return out

    def burn_reader(self, live, now, cfg):
        pts = sum(p for t, a, p in self.arch.burned if a == live and t > now - 45 * 60)
        if now - self.t0 < 10 * 60:
            return AE.stale_burn("sweep: under 10 min of burn")
        return {"rate": pts / 45.0, "stale": False, "age_s": 0, "span_min": 45}

    # ---- the switcher of Archmagi
    def switcher(self, argv, full=False, timeout=None):     # the signature of account_actuator.run
        verb = argv[1] if len(argv) > 1 else ""
        if verb == "use":
            to = argv[2]
            fail_h = self.sw.get("fail_h")
            if self.sw_fails_left > 0 or (fail_h and fail_h[0] <= self.h() < fail_h[1]):
                self.sw_fails_left = max(0, self.sw_fails_left - 1)
                self.events.append({"kind": "use_failed", "t": self.t, "machine": "Archmagi", "from": self.arch.live,
                                    "to": to, "left": {a: self.left(a) for a in ACCTS}})
                return 1, "sweep: the switcher failed"
            self.switch_arch(to)
            return 0, "switched to %s" % to
        if verb == "fleet-stop":
            self.stopped = True
            self.events.append({"kind": "stop", "t": self.t, "machine": "Archmagi", "live": self.arch.live})
            return 0, "stopped"
        if verb == "fleet-start":
            self.stopped = False
            self.events.append({"kind": "start", "t": self.t, "machine": "Archmagi"})
            return 0, "started"
        return 0, ""

    def switch_arch(self, to):
        frm = self.arch.live
        rec = {"op": "use", "changed": True, "from": frm, "to": to, "ts": AP.iso(self.t)}
        self.log.append(rec)
        with open(ACT.SWITCH_LOG, "a") as f:
            f.write(json.dumps(rec) + "\n")
        n = len(self.arch.runs)
        self.arch.ended_by_switch += n
        self.arch.runs = []
        self.events.append({"kind": "switch", "t": self.t, "machine": "Archmagi", "from": frm, "to": to, "runs": n,
                            "left": {a: self.left(a) for a in ACCTS}})
        self.arch.live = to
        self.stopped = False

    # ---- SteveDesktop over ssh
    def steve_up(self):
        r = self.steve_reach
        return not (r and r[0] <= self.h() < r[1])

    def ms_account(self, alias):
        return (self.steve.live, None) if self.steve_up() else (None, "sweep: ssh cannot reach it")

    def ms_send(self, alias, n):
        if not self.steve_up():
            return False, "sweep: ssh cannot reach it"
        self.steve_notice = n
        if n.get("account_end"):
            self.steve.told_save(self.t)        # its hooks tell each live run to save and publish
        return True, None

    def ms_runs(self, alias):
        b = self.steve_runs_blind
        if not self.steve_up() or (b and b[0] <= self.h() < b[1]):
            return None, "sweep: its runs cannot be read"
        return len(self.steve.runs), None

    def ms_switch(self, alias, name, account):
        fail_h = self.sw.get("fail_h")
        if fail_h and fail_h[0] <= self.h() < fail_h[1]:
            return False, "sweep: the switcher failed"
        frm = self.steve.live
        n = len(self.steve.runs)
        self.steve.ended_by_switch += n
        self.steve.runs = []
        self.events.append({"kind": "switch", "t": self.t, "machine": STEVE, "from": frm, "to": account, "runs": n,
                            "left": {a: self.left(a) for a in ACCTS}})
        self.steve.live = account
        return True, "switched"

    # ---- the orders channel of Archmagi's actuator
    def store_runs(self):
        return []

    def send(self, units, mode, text, deadline=None):
        self.arch.order(set(units), mode, self.t)
        return "ct_sim", None

    def withdraw(self, acts, why):
        return len(acts), None

    def saved(self, unit, since):
        return "saved (sweep)"

    # ---- time
    def line_of(self, a, t=None):
        """The leave line of `a` by the plan now, on the true levels (None: no step uses it now)."""
        t = self.t if t is None else t
        env = AP.Env(t, lambda x: self.left(x) if x in ACCTS else None, lambda x: self.reset.get(x))
        rl = AP.rule_of(self.plan_now, a, env)
        return rl

    def gate_arch(self, plan):
        """The real launcher's answer on the deciding machine (account_plan.new_run_gate), on the files the pass wrote."""
        f = {"now": self.t, "live": self.arch.live, "notice": AP.read_json(AP.notice_dir() / "notice.json"),
             "published": AP.read_json(AP.plan_dir() / "decision.json"), "rows": self.meter_rows(),
             "burn_h": None, "switches": list(self.log), "runs": [r["name"] for r in self.arch.runs],
             "state": ACT.load_state(), "markers": ACT.read_markers(), "hand": False}
        rc, why = AP.new_run_gate(plan, f, self.arch.live)
        return rc == AP.OK, why

    def gate_steve(self):
        n = self.steve_notice
        if not AP.fresh_record(n, self.t):
            return False, "COULD NOT LOOK: no fresh notice"
        r = AP.notice_refusal(n, self.t)
        return r is None, r or ""

    def advance(self, secs, plan):
        """Move the world on by secs, minute by minute: resets, burn, runs ending and starting, meter polls."""
        end = self.t + secs
        while self.t < end - 1e-6:
            dt = min(60.0, end - self.t)
            self.t += dt
            t = self.t
            for a in ACCTS:
                if self.reset[a] <= t:
                    rl = self.line_of(a, self.reset[a] - 1)
                    line = rl["line"] if rl else AP.standing_line(self.plan_now, a)
                    lost = max(0.0, self.left(a) - (line or 0))
                    self.erased[a] += lost
                    self.events.append({"kind": "reset", "t": self.reset[a], "account": a, "erased": lost,
                                        "line": line})
                    self.used[a] = 0.0
                    self.start_left[a] = 100.0
                    self.reset[a] += WEEK
            h = self.h()
            self.arch.tick(t)
            self.steve.tick(t)
            ok_a, _w = self.gate_arch(plan)
            demand = rate_at(self.burn, h) * dt / 3600
            if not ok_a:
                self.refused_min += dt / 60
                if demand > 0:
                    self.dark_min += dt / 60     # work waited and no account could take a new run
            if ok_a and not self.stopped:
                while len(self.arch.runs) < self.arch.n:
                    forever = self.arch.mode == "never_ends" and not any(
                        r["end"] == float("inf") for r in self.arch.runs)
                    self.arch.start(t, forever)
            ok_s, _ = self.gate_steve()
            if not ok_s and self.steve.mode != "none":
                self.steve_refused_min += dt / 60
            if ok_s:
                while len(self.steve.runs) < self.steve.n:
                    self.steve.start(t)
            land = 0.0 if self.stopped else demand * self.arch.share()
            lc = self.line_cache.get(self.arch.live)
            if lc is not None and self.left(self.arch.live) <= lc and land > 0:
                self.fleet_under += land
            self.idle_pts += demand - land
            self._burn(self.arch, self.arch.live, land, t)
            sd = rate_at(self.steve_burn, h) * dt / 3600 * self.steve.share()
            self._burn(self.steve, self.steve.live, sd, t)
            lp = self.laptop
            if lp and lp["from_h"] <= h < lp["to_h"]:
                self._burn(None, self.laptop_on, lp["rate"] * dt / 3600, t)
            if int((t - self.t0) // 60) % self.meter_every == 0:
                self.poll(t)

    def _burn(self, m, a, pts, t):
        if a not in self.used or pts <= 0:
            return
        self.used[a] = min(100.0, self.used[a] + pts)
        if m is not None:
            m.burned.append((t, a, pts))
            if len(m.burned) > 200:
                m.burned = [x for x in m.burned if x[0] > t - 3600]


# ------------------------------------------------------------------ one regime, pass by pass
class Seam:
    """Patches the plan code's doors to the world for the life of one regime, and takes them back."""

    def __init__(self, w):
        self.w, self.saved = w, []

    def __enter__(self):
        w = self.w
        pairs = [(ACT, "run", w.switcher), (ACT, "switcher_status",
                                           lambda: {"live": w.arch.live, "machine": "archmagi", "armed": True}),
                 (ACT, "clock", lambda: w.t), (ACT, "sleep", lambda s: w.advance(s, w.plan_now)),
                 (ACT, "notify_stop", lambda state: None), (AP, "flush_ledger", lambda plan: None),
                 (AP, "series_rows", lambda *a, **k: list(w.series)), (AP, "clock", lambda: w.t),
                 (os, "fsync", lambda fd: None)]      # a scratch folder: a write need not reach the disk
        for mod, name, fn in pairs:
            self.saved.append((mod, name, getattr(mod, name)))
            setattr(mod, name, fn)
        return self

    def __exit__(self, *exc):
        for mod, name, fn in reversed(self.saved):
            setattr(mod, name, fn)


def use_root(root):
    """This process's scratch world (each worker of a parallel sweep has its own)."""
    global ROOT
    ROOT = Path(root)
    os.environ.update({"RM_ACCOUNT_PLAN_DIR": str(ROOT / "plan"), "RM_SWITCH_PLAN_DIR": str(ROOT / "out"),
                       "RM_ACCOUNTS_DIR": str(ROOT / "accounts"), "RM_CONTROL_DB": str(ROOT / "control.db"),
                       "RM_DISPATCHER_STATE": str(ROOT / "state")})


def _worker():
    use_root(tempfile.mkdtemp(prefix="account_plan_sweep_w_"))


def _one(job):
    name, spec, seed, hours = job
    reg = realize(spec, seed, hours)
    try:
        return name, seed, reg, (codex_week(reg) if "codex" in reg else run_regime(reg))
    except Exception as e:  # noqa: BLE001  a regime that breaks the code is a finding, by name
        import traceback
        return name, seed, reg, {"violations": [{"check": "CRASH", "h": 0, "detail": {
            "error": "%s: %s" % (type(e).__name__, e), "where": traceback.format_exc().splitlines()[-4:]}}],
            "seconds": 0, "measures": {}, "bound": {}, "costly_by": 0, "passes": 0}


def run_regions(regions, seeds, hours=None, workers=None):
    """Every region, its regimes in parallel (each worker its own scratch world). -> [region verdicts], in order."""
    import multiprocessing as mp
    jobs = [(n, s, seed, hours) for n, s in regions for seed in seeds]
    workers = workers or max(1, min(len(jobs), (os.cpu_count() or 2) - 2))
    if workers == 1:
        _worker()
        got = [_one(j) for j in jobs]
    else:
        with mp.get_context("fork").Pool(workers, initializer=_worker) as pool:
            got = pool.map(_one, jobs, chunksize=1)
    by = {}
    for name, seed, reg, r in got:
        by.setdefault(name, []).append((seed, reg, r))
    return [verdict(n, by[n]) for n, _s in regions]


def verdict(name, runs):
    """-> the region's verdict: {name, verdict, n, violations: {check: smallest case}, costly: [...], seconds}."""
    viol, costly, secs, worst = {}, [], 0.0, None
    for s, reg, r in runs:
        secs += r["seconds"]
        for v in r["violations"]:
            c = v["check"]
            size = v["h"] or 0
            if c not in viol or size < viol[c]["h_first"]:
                viol[c] = {"h_first": size, "seed": s, "regime": reg, "detail": v["detail"],
                           "count": viol.get(c, {}).get("count", 0)}
            viol[c]["count"] += 1
        if r.get("costly_by", 0) > COSTLY_PTS:
            costly.append({"seed": s, "by": r["costly_by"], "plan": r["measures"], "bound": r["bound"], "regime": reg})
        if worst is None or r.get("costly_by", 0) > worst["by"]:
            worst = {"seed": s, "by": r.get("costly_by", 0), "plan": r.get("measures"), "bound": r.get("bound")}
    v = "VIOLATES" if viol else "COSTLY" if costly else "OK"
    return {"name": name, "verdict": v, "n": len(runs), "violations": viol, "costly": costly, "worst": worst,
            "seconds": round(secs, 1), "all_measures": [r.get("measures") or {} for _s, _reg, r in runs]}


def fresh_dirs():
    for d in ("plan", "out", "accounts"):
        p = ROOT / d
        if p.exists():
            shutil.rmtree(p)
        p.mkdir(parents=True)
    ACT.OUT = ROOT / "out"
    ACT.SWITCH_LOG = ROOT / "accounts" / "log.jsonl"
    assert ACT.OUT != ACT.LIVE_OUT and str(AP.plan_dir()).startswith(str(ROOT)), "the sweep reached a live folder"


def can_take_over(w, machine_acct):
    """The accounts of the plan, other than machine_acct, that are readable now and above their entry line (a switch
    may land on them), on the true levels."""
    out = []
    for a in ACCTS:
        if a == machine_acct:
            continue
        rl = w.line_of(a)
        if rl is None or not w.readable(a, w.t) or a not in w.reads:
            continue
        if w.left(a) > AP.entry_line(w.plan_now, rl):
            out.append(a)
    return out


def pending_truth(d):
    """The decision intends to leave the live account now (a switch, its drain, a stop, the end at the line)."""
    if not d:
        return False
    if d.get("do") in ("switch", "hold"):
        return True
    if d.get("do") in ("stop", "stopped"):      # a stop for a reset is no switch: the notice says hard stop
        return False
    return bool(d.get("drain_of") or d.get("account_end") or (d.get("do") == "soft" and d.get("drain")))


def run_regime(reg, hours=None, stop_at_first=False, trace=None):
    """-> {violations: [{check, h, detail}], measures, bound, passes, seconds}."""
    t_start = time.time()
    fresh_dirs()
    w = World(reg)
    plan = plan_of(reg, w.t0)
    AP.commit(lambda _o: copy.deepcopy(plan), {"why": "sweep", "create": True}, base=None)
    w.plan_now = AP.load_plan()[0]
    mids = change_mid_week(reg)
    hours = hours or reg.get("hours", 72)
    viol, seen = [], set()
    w.history()
    w.poll(w.t)
    st = {"arch_refused": 0, "steve_refused": 0, "same": 0, "last_key": None, "steve_same": 0, "last_steve": None,
          "min_under": {}, "max_over": 0.0}
    machine_ds = []

    real_mn = AP.machine_notice

    def spy_mn(plan_, f, account, now, name, prev=None, why_unread=None):
        n = real_mn(plan_, f, account, now, name, prev, why_unread)
        d = AP.decide(plan_, AP.machine_facts(f, account)) if account else None
        machine_ds.append((account, n, d))
        return n

    def flag(check, detail):
        key = (check, detail.get("key", ""))
        if key in seen:
            return
        seen.add(key)
        viol.append({"check": check, "h": round(w.h(), 2), "detail": {k: v for k, v in detail.items() if k != "key"}})

    passes = 0
    with Seam(w):
        AP.machine_notice = spy_mn
        try:
            while w.t < w.t0 + hours * 3600:
                while mids and w.h() >= mids[0][0]:
                    ch = mids.pop(0)[1]
                    AP.commit(lambda o: ch(o), {"why": "sweep: a change in the middle of the week"})
                    w.plan_now = AP.load_plan()[0]
                machine_ds.clear()
                ev0 = len(w.events)
                live0 = w.arch.live
                seams = {"now": w.t, "meter_fn": w.meter_rows, "poll_fn": lambda: w.poll(w.t),
                         "runs_fn": lambda: [r["name"] for r in w.arch.runs], "burn_fn": w.burn_reader,
                         "orders": w, "passes": 5,
                         "machines": {"account_of": w.ms_account, "send": w.ms_send, "runs_of": w.ms_runs,
                                      "switch": w.ms_switch}}
                with contextlib.redirect_stdout(io.StringIO()):
                    AP.tick(seams=seams)
                passes += 1
                if trace is not None:
                    dd = AP.read_json(AP.plan_dir() / "decision.json") or {}
                    trace.append("%6.2fh %-8s %-7s to=%-7s runs=%d stopped=%s levels=%s read=%s steve=%s | %s" % (
                        w.h(), w.arch.live, dd.get("do"), dd.get("to"), len(w.arch.runs), w.stopped,
                        {a: round(w.left(a), 1) for a in ACCTS},
                        {a: (r.get("week_pct_used"), round((w.t - AP.stamp(r["measured_at"])) / 60))
                         for a, r in w.reads.items()}, w.steve.live, fulltext.fit(str(dd.get("why")), 220)))
                check_pass(w, reg, st, flag, machine_ds, ev0, live0)
                if stop_at_first and viol:
                    break
                w.advance(PASS_S - ((w.t - w.t0) % PASS_S or 0) if (w.t - w.t0) % PASS_S else PASS_S, w.plan_now)
        finally:
            AP.machine_notice = real_mn
    out = {"violations": viol, "passes": passes, "seconds": round(time.time() - t_start, 2),
           "measures": dict(measures_of(w), overshoot_max=round(st["max_over"], 1))}
    out["bound"] = foresight_bound(reg, hours)
    out["costly_by"] = round(out["measures"]["cost"] - out["bound"]["cost"], 1)
    return out


def check_pass(w, reg, st, flag, machine_ds, ev0, live0):
    """The wanted behaviour, on the state after one pass."""
    plan = w.plan_now
    d = AP.read_json(AP.plan_dir() / "decision.json") or {}
    if not AP.fresh_record(d, w.t + 1):
        d = {}
    n = AP.read_json(AP.notice_dir() / "notice.json") or {}
    new = w.events[ev0:]
    acted = [e for e in new if e["kind"] in ("switch", "stop") and e["machine"] == "Archmagi"]
    live = w.arch.live
    can = can_take_over(w, live)
    ok_gate, why_gate = w.gate_arch(plan)
    hold = AP.active(plan["holds"], w.t)

    # STUCK: no new run for more than K passes while another account can take over
    if not ok_gate and can and not hold:
        st["arch_refused"] += 1
        if st["arch_refused"] > K_STUCK:
            flag("STUCK", {"machine": "Archmagi", "key": "Archmagi", "refused_passes": st["arch_refused"],
                           "live": live, "left": round(w.left(live), 1), "can_take_over": can,
                           "why": fulltext.fit(" ".join(str(why_gate).split()), 300)})
    else:
        st["arch_refused"] = 0
    key = (d.get("do"), d.get("to"), ok_gate, live, tuple(round(w.left(a)) for a in ACCTS))
    if not ok_gate and can and key == st["last_key"]:
        st["same"] += 1
        if st["same"] >= SAME_N:
            flag("STUCK_SAME", {"machine": "Archmagi", "key": "same", "passes": st["same"], "do": d.get("do")})
    else:
        st["same"] = 0
    st["last_key"] = key

    # the fleet never stops while an account can take over
    failed = [e for e in new if e["kind"] == "use_failed"]
    for e in acted:
        if e["kind"] == "stop":
            c = can_take_over(w, e["live"])
            rl = w.line_of(e["live"], e["t"])
            line = rl["line"] if rl else AP.standing_line(plan, e["live"])
            spent = line is None or w.left(e["live"]) <= line + 0.5
            if failed and spent:
                continue        # a failed switch off a spent account: the designed brake; the switch is retried
            if c:
                flag("STOP_WITH_TAKER", {"key": "stop", "live": e["live"], "can_take_over": c,
                                          "after_failed_switch": bool(failed), "left": round(w.left(e["live"]), 1),
                                          "line": line,
                                          "why": fulltext.fit(str(d.get("why")), 300)})
    # switch pending: told only when one is pending, always when one is
    if not acted and live == live0 and d:
        told = HK.switch_pending(n)
        truth = pending_truth(d)
        if told != truth and n.get("state") == "soft" or (truth and n.get("state") != "soft" and w.arch.runs):
            flag("FALSE_PENDING" if told and not truth else "MISSED_PENDING",
                 {"key": "Archmagi:%s:%s" % (d.get("do"), told), "do": d.get("do"), "notice_state": n.get("state"),
                  "switch_pending": n.get("switch_pending"), "why": fulltext.fit(str(d.get("why")), 300)})
    for account, mn, md in machine_ds:
        if account and md is not None:
            told, truth = HK.switch_pending(mn), md.get("do") in AP.REFUSES and not md.get("unread")
            if told != truth:
                flag("FALSE_PENDING" if told else "MISSED_PENDING",
                     {"key": "Steve:%s:%s" % (md.get("do"), told), "machine": STEVE, "do": md.get("do"),
                      "switch_pending": mn.get("switch_pending"), "why": fulltext.fit(str(md.get("why")), 300)})
    # an unread level never causes a switch or a stop by itself; no act at a line that the true level is far above
    for e in acted:
        frm = e.get("from") or e.get("live")
        rl = w.line_of(frm, e["t"])
        line = rl["line"] if rl else None
        true_left = e.get("left", {}).get(frm, w.left(frm))
        under = bool(d.get("under")) or e["kind"] == "stop"
        reading = w.reads.get(frm)
        unread = reading is None or not w.readable(frm, e["t"]) or w.last_read_t.get(frm) is None or \
            e["t"] - w.last_read_t[frm] > 20 * 60
        rate = rate_at(w.burn, w.h(e["t"]))
        slack = 1.5 + rate * (((e["t"] - (w.last_read_t.get(frm) or e["t"])) / 3600) + 0.25)
        if line is not None and under and true_left > line + slack:
            flag("UNREAD_ACT" if unread else "ACT_ABOVE_LINE",
                 {"key": "act:%s" % frm, "act": e["kind"], "from": frm, "true_left": round(true_left, 1),
                  "line": line, "why": fulltext.fit(str(d.get("why")), 300)})
    # no switch to an account at or under its line; no A -> B -> A with no reset between
    for e in new:
        if e["kind"] != "switch":
            continue
        rl = w.line_of(e["to"], e["t"])
        if rl is None or e["left"][e["to"]] <= rl["line"]:
            flag("SWITCH_TO_SPENT", {"key": "to:%s:%s" % (e["machine"], e["to"]), "machine": e["machine"],
                                      "to": e["to"], "left": round(e["left"][e["to"]], 1),
                                      "line": None if rl is None else rl["line"]})
        prev = [x for x in w.events[:-len(new) or None] + new[:new.index(e)]
                if x["kind"] == "switch" and x["machine"] == e["machine"]]
        if prev:
            p = prev[-1]
            rl_b = w.line_of(e["from"], e["t"])
            spent = rl_b is None or e["left"][e["from"]] <= AP.entry_line(w.plan_now, rl_b)
            if p["from"] == e["to"] and not spent and e["t"] - p["t"] < FLIP_H * 3600 and not any(
                    x["kind"] == "reset" and x["account"] in (e["to"], e["from"]) and p["t"] <= x["t"] <= e["t"]
                    for x in w.events):
                flag("FLIP_FLOP", {"key": "flip:%s" % e["machine"], "machine": e["machine"],
                                   "path": "%s->%s->%s" % (p["from"], p["to"], e["to"]),
                                   "hours": round((e["t"] - p["t"]) / 3600, 2)})
        # a machine above its line is switched only in the stated cases
        rl_from = w.line_of(e["from"], e["t"])
        if rl_from is not None and e["left"][e["from"]] > rl_from["line"] + 1:
            why = str(d.get("why")) if e["machine"] == "Archmagi" else ""
            stated = e["machine"] == STEVE and False
            if e["machine"] == "Archmagi":
                stated = any(s in why for s in ("rescue", "the step", "no step uses", "requested", "is at its",
                                                "the fleet is stopped on"))
            else:
                md = next((x[2] for x in machine_ds if x[0] == e["from"]), None) or {}
                stated = rl_from is None or "no step uses" in str(md.get("why")) or "the step" in str(md.get("why"))
            if not stated:
                flag("SWITCH_ABOVE_LINE", {"key": "above:%s" % e["machine"], "machine": e["machine"],
                                            "from": e["from"], "left": round(e["left"][e["from"]], 1),
                                            "line": rl_from["line"], "why": fulltext.fit(why, 300)})
    # the reserve kept, and the line as the owner typed it (page design/specs/2026-11-27-account-line-schedule/)
    for a in ACCTS:
        rla = w.line_of(a)
        w.line_cache[a] = None if rla is None else rla["line"]
        if rla is None:
            st.setdefault("cross", {}).pop(a, None)
            continue
        gap = w.left(a) - rla["line"]
        w.lowest_gap[a] = round(gap, 1) if w.lowest_gap[a] is None else min(w.lowest_gap[a], round(gap, 1))
        if gap < 0:
            w.under_min[a] += PASS_S // 60
        cr = st.setdefault("cross", {})
        if gap > 0:
            cr.pop(a, None)
        elif a not in cr:       # the level at which it went under: the line (a burn) or the level (a rising line)
            cr[a] = min(rla["line"], st.get("prev_left", {}).get(a, w.left(a)))
        for sc in reg.get("schedules") or []:
            if sc["account"] != a or sc.get("text") or abs(sc.get("drift_h", 0)) * 3600 >= AP.SNAP_S \
                    or w.h() < sc.get("at_h", 0) or "schedule" not in rla:
                continue
            ra = w.reset[a] + sc.get("drift_h", 0) * 3600
            d = typed_off(sc, ra, w.t, rla["line"], t_typed=w.t0)
            if d is not None and d > 0.6:
                flag("LINE_NOT_AS_TYPED", {"key": "typed:%s" % a, "account": a, "want": round(oracle_line(sc, ra, w.t), 2),
                                           "line": rla["line"], "h_to_reset": round((w.reset[a] - w.t) / 3600, 2)})
    st["prev_left"] = {a: w.left(a) for a in ACCTS}
    # the live account's overshoot under its line while the fleet is on it
    rl = w.line_of(live)
    if rl is not None and can:
        # one that started under its line overshot nothing; one that a rising line put under overshoots from there
        under_by = min(rl["line"], w.start_left[live], st.get("cross", {}).get(live, 100.0)) - w.left(live)
        if under_by > st["max_over"]:
            st["max_over"] = under_by
            rate = rate_at(w.burn, w.h())
            bound = 1.5 + rate * ((w.arch.save_min + 15) / 60.0)
            if under_by > bound and w.arch.mode != "never_ends":
                flag("OVERSHOOT", {"key": "over:%s" % live, "live": live, "under_by": round(under_by, 1),
                                   "bound": round(bound, 1), "left": round(w.left(live), 1), "line": rl["line"]})
    # SteveDesktop: refused while an account can take over and it could be switched
    sl = w.steve.live
    if w.steve.mode != "none" and w.steve_up():
        ok_s, why_s = w.gate_steve()
        can_s = can_take_over(w, sl)
        if not ok_s and can_s and not hold:
            st["steve_refused"] += 1
            if st["steve_refused"] > K_STUCK + 6:      # one pass of ssh lag and the retry wait of a failed switch
                flag("STUCK", {"machine": STEVE, "key": STEVE, "refused_passes": st["steve_refused"], "on": sl,
                               "left": round(w.left(sl), 1) if sl in ACCTS else None, "can_take_over": can_s,
                               "runs": len(w.steve.runs), "why": fulltext.fit(" ".join(str(why_s).split()), 300)})
        else:
            st["steve_refused"] = 0


def measures_of(w):
    sw = [e for e in w.events if e["kind"] == "switch"]
    erased = round(sum(w.erased.values()), 1)
    return {"erased": {a: round(v, 1) for a, v in w.erased.items()}, "erased_total": erased, "switches": len(sw),
            "switch_list": ["%.1fh %s %s->%s (%d runs)" % ((e["t"] - w.t0) / 3600, e["machine"], e["from"], e["to"],
                                                         e["runs"]) for e in sw][:12],
            "refused_min": round(w.refused_min), "steve_refused_min": round(w.steve_refused_min),
            "runs_ended_by_switch": w.arch.ended_by_switch + w.steve.ended_by_switch,
            "idle_pts": round(w.idle_pts, 1), "stops": sum(1 for e in w.events if e["kind"] == "stop"),
            "cost": round(erased + 3 * len(sw) + w.idle_pts, 1),
            "left_end": {a: round(w.left(a), 1) for a in ACCTS},
            "under_line_min": dict(w.under_min), "lowest_gap": dict(w.lowest_gap), "dark_h": round(w.dark_min / 60, 2),
            "fleet_under_pts": round(w.fleet_under, 1)}


# ------------------------------------------------------------------ the foresight bound
def foresight_bound(reg, hours):
    """The best of a family of rules that know the whole burn ahead, on the same burn, levels, resets and lines:
    the controlled burn (Archmagi and SteveDesktop together) goes to the account whose allowance a reset erases first
    (earliest deadline first), leaving the account it is on only when that account is spent or when, with foresight,
    more than theta points of another account would be erased if it waited. The laptop's burn stays on its account.
    Not the optimum: an upper bound on it, so a gap to it is a lower bound on what the plan loses. -> {cost, ...}."""
    w = World(reg)
    w.plan_now = AP.load_plan()[0] or plan_of(reg, w.t0)
    step = 300
    n = int(hours * 3600 / step)
    dem = [(rate_at(w.burn, i * step / 3600) + rate_at(w.steve_burn, i * step / 3600) *
            (0 if (reg.get("steve") or {}).get("runs", {}).get("mode", "none") == "none" else 1)) * step / 3600
           for i in range(n)]
    lap = [(w.laptop["rate"] * step / 3600 if w.laptop and w.laptop["from_h"] <= i * step / 3600 < w.laptop["to_h"]
            else 0.0) for i in range(n)]
    machines = 2        # SteveDesktop is a machine of the plan: it is switched off a finished account too
    best = None
    for theta in (0.0, 3.0, 6.0, 12.0, float("inf")):
        r = _edf(w, reg, dem, lap, theta, step, n, machines)
        if best is None or r["cost"] < best["cost"]:
            best = r
    return best


def _edf(w0, reg, dem, lap, theta, step, n, machines=1):
    used = {a: 100.0 - reg["start"]["left"][a] for a in ACCTS}
    reset = dict(w0.reset)
    plan = w0.plan_now
    t0 = w0.t0
    live, erased, sw, idle = reg["start"]["live"], 0.0, 0, 0.0
    lap_on = w0.laptop_on
    cum = [0.0]
    for x in dem:
        cum.append(cum[-1] + x)

    def rule(a, t):
        env = AP.Env(t, lambda x: 100.0 - used[x] if x in used else None, lambda x: reset.get(x))
        return AP.rule_of(plan, a, env)

    def usable(a, t):
        rl = rule(a, t)
        return 0.0 if rl is None else max(0.0, 100.0 - used[a] - rl["line"]), rl

    for i in range(n):
        t = t0 + i * step
        for a in ACCTS:
            if reset[a] <= t:
                rl = rule(a, reset[a] - 1)
                line = rl["line"] if rl else (AP.standing_line(plan, a) or 0)
                erased += max(0.0, 100.0 - used[a] - line)
                used[a], reset[a] = 0.0, reset[a] + WEEK
        u = {a: usable(a, t)[0] for a in ACCTS}
        cands = [a for a in ACCTS if u[a] > 0.05]
        if live not in cands or u[live] <= 0.05:
            nxt = min(cands, key=lambda a: reset[a]) if cands else None
            if nxt and nxt != live:
                live, sw = nxt, sw + machines
        elif theta != float("inf"):
            # with foresight: the burn that reaches `a` before its reset if we stay until live is spent
            j_spent = i
            while j_spent < n and cum[j_spent] - cum[i] < u[live]:
                j_spent += 1
            for a in sorted(cands, key=lambda x: reset[x]):
                if a == live or reset[a] >= reset[live]:
                    continue
                j_reset = min(n, int((reset[a] - t0) / step))
                reach = max(0.0, cum[j_reset] - cum[min(j_spent, j_reset)])
                if u[a] - reach > theta + 3 * machines:
                    live, sw = a, sw + machines
                    break
        x = dem[i]
        if live in u and u[live] > 0:
            used[live] = min(100.0, used[live] + x)
        else:
            idle += x
        if lap[i] and lap_on in used:
            used[lap_on] = min(100.0, used[lap_on] + lap[i])
    return {"cost": round(erased + 3 * sw + idle, 1), "erased": round(erased, 1), "switches": sw,
            "idle": round(idle, 1), "theta": theta}


# ------------------------------------------------------------------ the Codex week, on the real gate
OWNER_EX = [[None, 40, "hold"], [0, 0, "ramp"]]     # the owner's example; None: Saturday 11:59 PM, set per regime


def owner_example(reset):
    """The owner's example of 2026-11-27 as points before `reset`: 40% through Saturday 11:59 PM, a ramp to 0% at the
    reset (his Codex reset is on Tuesday afternoon)."""
    d = datetime.fromtimestamp(reset, AP.TZ)
    sat = d - timedelta(days=(d.weekday() - 5) % 7)
    sat = sat.replace(hour=23, minute=59, second=0, microsecond=0)
    if sat.timestamp() >= reset:
        sat -= timedelta(days=7)
    return [[round((reset - sat.timestamp()) / 3600, 4), 40, "hold"], [0, 0, "ramp"]]


def codex_week(reg):
    """Codex (a meter account: no switch) over `weeks` weeks at the timed pass's 5 min, on the real gate
    (account_plan.can_use, what codex_advice and the Codex lane ask). Stand-ins: the meter (a reading each pass,
    whole points, the reported reset = the true reset + jitter, windows when it cannot be read, a stale reading after
    the reset), the Codex lane's demand (jobs wait while its burn is over 0; a job is sent only on a yes), and the
    owner's own use (a second burner on some weekdays that the plan does not control).
    -> {violations, measures: per week and in total}."""
    t_start = time.time()
    cx = reg["codex"]
    t0 = T0 + reg.get("t0_shift_s", 0)
    plan = today_plan()
    for path, v in (reg.get("numbers") or {}).items():
        d = plan["numbers"]
        keys = path.split(".")
        for k in keys[:-1]:
            d = d[k]
        d[keys[-1]] = v
    R = t0 + cx.get("reset_h", 90) * 3600
    sc = cx.get("schedule")
    if sc is not None:
        sc = dict(sc, account="codex")
        if sc.get("example"):
            sc["points"] = owner_example(R + sc.get("drift_h", 0) * 3600)
    reg_like = {"start": {"reset_h": {"codex": (R - t0) / 3600}}}
    if sc is not None and not sc.get("at_h"):
        put_sched(plan, sc, reg_like, t0)
    left, viol, seen = float(cx.get("left", 70)), [], set()
    fleet, owner = cx.get("fleet") or {"kind": "const", "rate": 0.8}, cx.get("owner")
    unread, post_gap = cx.get("unread_h"), cx.get("post_reset_gap_min", 0)
    jitter = cx.get("jitter_min", 0)
    m = {"under_line_min": 0, "lowest_gap": None, "fleet_under_pts": 0.0, "erased": 0.0, "left_at_reset": [],
         "dark_h": 0.0, "owner_starved_min": 0, "fleet_pts": 0.0, "owner_pts": 0.0, "line_shift_max": 0.0,
         "resets": 0, "switches": 0}
    old_read, last_reset = None, R - WEEK
    t, weeks = t0, cx.get("weeks", 2)

    def flag(check, detail):
        if (check, detail.get("key")) in seen:
            return
        seen.add((check, detail.get("key")))
        viol.append({"check": check, "h": round((t - t0) / 3600, 2), "detail": detail})
    while t < t0 + weeks * WEEK:
        h = (t - t0) / 3600
        if sc is not None and sc.get("at_h") and h >= sc["at_h"] and "schedule" not in plan["steps"][AP.find_step(plan, "codex")]:
            put_sched(plan, sc, reg_like, t0)
        if R <= t:      # the true reset: what is left above the line one second before it is erased
            env = AP.Env(R - 1, lambda x: left, lambda x: R)
            rl = AP.rule_of(plan, "codex", env)
            line = rl["line"] if rl else 0
            m["erased"] += max(0.0, left - line)
            m["left_at_reset"].append(round(left, 1))
            m["resets"] += 1
            left, last_reset = 100.0, R
            R += WEEK
        rep_reset = R + (jitter if (m["resets"] % 2 == 0) else -jitter) * 60
        blind = unread and unread[0] <= h < unread[1]
        stale = post_gap and last_reset <= t < last_reset + post_gap * 60 and old_read is not None
        if blind:
            rd = {**AP.reading(None, t), "last_left": None if old_read is None else old_read["last_left"],
                  "why": "sweep: the meter cannot be read", "burn_h": None}
        elif stale:
            rd = dict(old_read)          # the reading of before the reset: its level and its reset, now passed
        else:
            rd = {**AP.reading(None, t), "left": float(round(left)), "ok": True, "state": "MEASURED", "reset": rep_reset,
                  "age_min": 1.0, "last_left": float(round(left)), "why": "", "burn_h": rate_at(fleet, h)}
            if R - t > 600:
                old_read = rd
        f = {"now": t, "rows": {}, "codex": rd}
        try:
            rc, why = AP.can_use(plan, f, "codex")
        except Exception as e:  # noqa: BLE001  a gate that raises is a finding, by name
            flag("CRASH", {"key": "crash", "error": "%s: %s" % (type(e).__name__, e)})
            break
        rl_true = AP.rule_of(plan, "codex", AP.Env(t, lambda x: left, lambda x: rep_reset))
        line = rl_true["line"] if rl_true else 0.0
        if sc is not None and h >= sc.get("at_h", 0):
            want = oracle_line(sc, R + sc.get("drift_h", 0) * 3600, t)
            if want is not None:
                m["line_shift_max"] = max(m["line_shift_max"], round(abs(want - line), 1))
                d = typed_off(sc, R + sc.get("drift_h", 0) * 3600, t, line, t_typed=t0, jitter_h=jitter / 60)
                if abs(sc.get("drift_h", 0)) * 3600 < AP.SNAP_S and abs(jitter) * 60 < AP.SNAP_S and not sc.get("text") \
                        and d is not None and d > 0.6:
                    flag("LINE_NOT_AS_TYPED", {"key": "typed", "want": round(want, 2), "line": line,
                                               "h_to_reset": round((R - t) / 3600, 2)})
        gap = left - line
        m["lowest_gap"] = round(gap, 1) if m["lowest_gap"] is None else min(m["lowest_gap"], round(gap, 1))
        if gap < 0:
            m["under_line_min"] += 5
        demand = rate_at(fleet, h)
        if rc != AP.OK:
            if demand > 0:
                m["dark_h"] += PASS_S / 3600
            if not rd["ok"] and rc == AP.OK:
                pass
        elif not rd["ok"]:
            flag("FREE_TO_BURN", {"key": "blind", "why": why})     # a yes on a level that is not read
        hi = plan["steps"][AP.find_step(plan, "codex")]["leave"]
        if rc == AP.OK and rl_true and "COULD NOT LOOK" in str(rl_true.get("note")) and left <= hi:
            flag("FREE_TO_BURN", {"key": "unreadable", "left": round(left, 1), "line": line, "why": why})
        burn_f = demand * PASS_S / 3600 if rc == AP.OK else 0.0
        if burn_f and left <= line - 1.5:     # whole points and one pass of burn: the gate's own grain
            flag("FLEET_UNDER", {"key": "under", "left": round(left, 1), "line": line, "why": why})
        if burn_f and left <= line:
            m["fleet_under_pts"] += burn_f
        burn_o = 0.0
        if owner:
            d = datetime.fromtimestamp(t, AP.TZ)
            if d.weekday() in owner["days"] and owner["from_h"] <= d.hour < owner["to_h"]:
                burn_o = owner["rate"] * PASS_S / 3600
                if left <= 0.05:
                    m["owner_starved_min"] += 5
        take = min(left, burn_f + burn_o)
        if burn_f + burn_o > 0:
            m["fleet_pts"] += take * burn_f / (burn_f + burn_o)
            m["owner_pts"] += take * burn_o / (burn_f + burn_o)
        left -= take
        t += PASS_S
    wk = max(1e-9, weeks)
    for k in ("erased", "dark_h", "fleet_pts", "owner_pts", "fleet_under_pts"):
        m[k + "_per_week"] = round(m[k] / wk, 1)
        m[k] = round(m[k], 1)
    m["under_line_h_per_week"] = round(m["under_line_min"] / 60 / wk, 1)
    m["owner_starved_h_per_week"] = round(m["owner_starved_min"] / 60 / wk, 1)
    m["cost"] = round(m["erased"] + m["dark_h"], 1)
    return {"violations": viol, "measures": m, "bound": {"cost": m["cost"]}, "costly_by": 0, "passes": int(weeks * 2016),
            "seconds": round(time.time() - t_start, 2)}


# ------------------------------------------------------------------ the grid
def base(**kw):
    r = {"seed": 1, "hours": 72, "burn": {"kind": "const", "rate": 6},
         "start": {"live": "steven", "left": {"steven": 60, "system": 70, "lukas": 40},
                   "reset_h": {"steven": 150, "system": 60, "lukas": 110}},
         "runs": {"mode": "always", "n": 3, "save_min": 20}, "steve": {"account": "same", "runs": {"mode": "none"}},
         "meter": {"every_min": 5}}
    for k, v in kw.items():
        r[k] = v
    return r


def tonight_regions():
    """Tonight: steven live near its 52% line, burn 4 to 12 points an hour, each run state, SteveDesktop on steven
    with and without live runs. Each region is a range; the seeds pick points inside it."""
    regs = []
    for rate_lo, rate_hi in ((4, 6), (6, 9), (9, 12)):
        for runs_name, runs in (("no run", {"mode": "none"}), ("runs, quick save", {"mode": "always", "n": 3,
                                                                                    "save_min": (1, 15)}),
                                ("runs, slow save", {"mode": "always", "n": 3, "save_min": (30, 120)}),
                                ("a run that never ends", {"mode": "never_ends", "n": 3, "save_min": (5, 30)})):
            for steve_name, steve in (("SteveDesktop idle on steven", {"account": "same", "runs": {"mode": "none"}}),
                                      ("SteveDesktop with runs on steven",
                                       {"account": "same", "runs": {"mode": "always", "n": 2, "save_min": (5, 60)},
                                        "burn": {"kind": "const", "rate": 2}})):
                name = "tonight | burn %d-%d | %s | %s" % (rate_lo, rate_hi, runs_name, steve_name)
                regs.append((name, {"burn": ("const", rate_lo, rate_hi), "runs": runs, "steve": steve,
                                    "left_steven": (53, 58), "left_system": (40, 95), "left_lukas": (2, 40),
                                    "hours": 30}))
    return regs


def axis_regions():
    """One axis at a time around a base week, each bin a range; plus the combinations that the two faults of
    2026-11-25 needed (an unread level after a reset; a machine on an account that no step uses)."""
    R = []
    for lo, hi in ((0, 0.5), (0.5, 3), (3, 8), (8, 15), (15, 22), (22, 30)):
        R.append(("burn constant %g-%g/h" % (lo, hi), {"burn": ("const", lo, hi)}))
    R.append(("burn steps up mid-week (2-4 -> 12-25/h)", {"burn": ("step", (2, 4), (12, 25))}))
    R.append(("burn steps down mid-week (12-25 -> 0-2/h)", {"burn": ("step", (12, 25), (0, 2))}))
    R.append(("burn in bursts (base 1-3, peaks 15-30 for 1-4 h)", {"burn": ("burst",)}))
    R.append(("burn with 6-14 hours of zero a day", {"burn": ("zero",)}))
    R.append(("laptop on the live account 1-4/h, all week", {"laptop": ("all",)}))
    R.append(("laptop starts and stops at any hour", {"laptop": ("window",)}))
    R.append(("start: live account 0-10% left", {"left_live": (0, 10)}))
    R.append(("start: live account 90-100% left", {"left_live": (90, 100)}))
    R.append(("start: every account 0-5% left", {"all_low": True}))
    R.append(("start: two resets in the same hour", {"same_reset": True}))
    R.append(("start: a reset 1 s before or after a pass", {"reset_at_pass": True}))
    R.append(("start: steven's 48 h window opens or closes within the week", {"window_edge": True}))
    R.append(("meter: readings 10-60 min old", {"meter": ("every", 10, 60)}))
    R.append(("meter: no reading for 2-24 passes", {"meter": ("blackout", 2, 24)}))
    R.append(("meter: RESET PASSED with no level for 5-60 min", {"meter": ("post_reset", 5, 60)}))
    R.append(("meter: one account unread for 2-12 h", {"meter": ("unread_one", 2, 12)}))
    R.append(("meter: no account readable for 1-6 h", {"meter": ("unread_all", 1, 6)}))
    R.append(("runs: none", {"runs": {"mode": "none"}}))
    R.append(("runs: always, save in 1-30 min", {"runs": {"mode": "always", "n": 4, "save_min": (1, 30)}}))
    R.append(("runs: always, save in 30-120 min", {"runs": {"mode": "always", "n": 4, "save_min": (30, 120)}}))
    R.append(("runs: one never ends", {"runs": {"mode": "never_ends", "n": 3, "save_min": (5, 30)}}))
    R.append(("SteveDesktop on the live account with runs", {"steve": ("same_runs",)}))
    R.append(("SteveDesktop on another account with runs", {"steve": ("other_runs",)}))
    R.append(("SteveDesktop on an account that no step uses (steven past its window, above its line)",
              {"steve": ("no_step",)}))
    R.append(("SteveDesktop not reachable for 1-12 h", {"steve": ("unreachable",)}))
    R.append(("SteveDesktop's run count unread for 1-12 h", {"steve": ("runs_blind",)}))
    R.append(("plan: a hold of 1-8 h", {"plan": ("hold",)}))
    R.append(("plan: a pin on the live account for 6-48 h", {"plan": ("pin",)}))
    R.append(("plan: a line changed until the reset", {"plan": ("line",)}))
    R.append(("plan: the order changed mid-week", {"plan": ("order",)}))
    R.append(("plan: a switch request", {"plan": ("request",)}))
    R.append(("switcher fails once", {"switcher": {"kind": "fails_once"}}))
    R.append(("switcher fails for an hour", {"switcher": ("hour",)}))
    return R


def realize(spec, seed, hours=None):
    """A region's spec and a seed -> one concrete regime (a point inside the region's ranges)."""
    rng = random.Random(seed * 7919 + 17)
    u = lambda a, b: round(rng.uniform(a, b), 1)    # noqa: E731
    live = rng.choice(ACCTS)
    left = {a: u(5, 100) for a in ACCTS}
    reset_h = {a: u(0.5, 168) for a in ACCTS}
    reg = base(seed=seed, hours=hours or spec.get("hours", 168))
    b = spec.get("burn") or ("const", 2, 12)
    if b[0] == "const":
        reg["burn"] = {"kind": "const", "rate": u(b[1], b[2])}
    elif b[0] == "step":
        reg["burn"] = {"kind": "step", "r0": u(*b[1]), "r1": u(*b[2]), "at_h": u(12, 60)}
    elif b[0] == "burst":
        reg["burn"] = {"kind": "burst", "base": u(1, 3), "peak": u(15, 30), "on_h": u(1, 4), "period_h": u(8, 24),
                       "phase_h": u(0, 8)}
    elif b[0] == "zero":
        reg["burn"] = {"kind": "zero", "rate": u(4, 14), "zero_h": u(6, 14), "phase_h": u(0, 24)}
    if "left_steven" in spec:       # tonight: steven live just above its line, inside its window
        live = "steven"
        left = {"steven": u(*spec["left_steven"]), "system": u(*spec["left_system"]), "lukas": u(*spec["left_lukas"])}
        reset_h = {"steven": u(168 - 47, 168 - 12), "system": u(2, 168), "lukas": u(2, 168)}
    if "left_live" in spec:
        left[live] = u(*spec["left_live"])
    if spec.get("all_low"):
        left = {a: u(0, 5) for a in ACCTS}
    if spec.get("same_reset"):
        a, b2 = rng.sample(ACCTS, 2)
        reset_h[b2] = round(reset_h[a] + rng.uniform(-0.5, 0.5), 3)
    if spec.get("reset_at_pass"):
        a = rng.choice(ACCTS)
        reset_h[a] = round(rng.randint(1, 60) * PASS_S / 3600 + rng.choice((-1, 1)) / 3600, 6)
    if spec.get("window_edge"):
        live = "steven"
        left["steven"] = u(55, 100)
        reset_h["steven"] = round(168 - 48 + rng.uniform(-1, 1) * rng.choice((1 / 60, 0.1, 6)), 4)
    reg["start"] = {"live": live, "left": left, "reset_h": reset_h}
    m = spec.get("meter")
    if m and m[0] == "every":
        reg["meter"] = {"every_min": rng.randint(m[1], m[2])}
    elif m and m[0] == "blackout":
        h = u(1, 60)
        reg["meter"] = {"every_min": 5, "blackout_h": [h, h + rng.randint(m[1], m[2]) * PASS_S / 3600]}
    elif m and m[0] == "post_reset":
        reg["meter"] = {"every_min": 5, "post_reset_gap_min": rng.randint(m[1], m[2])}
        a = live if spec.get("live_resets") else rng.choice(ACCTS)
        reset_h[a] = u(*spec.get("reset_in", (1, 40)))
    elif m and m[0] == "unread_one":
        h = u(0, 48)
        reg["meter"] = {"every_min": 5, "unread": {"account": rng.choice(ACCTS), "from_h": h, "to_h": h + u(m[1], m[2])}}
    elif m and m[0] == "unread_all":
        h = u(0, 48)
        reg["meter"] = {"every_min": 5, "unread": {"account": "all", "from_h": h, "to_h": h + u(m[1], m[2])}}
    if "runs" in spec:
        r = dict(spec["runs"])
        if isinstance(r.get("save_min"), tuple):
            r["save_min"] = rng.randint(*r["save_min"])
        reg["runs"] = r
    else:
        reg["runs"] = {"mode": rng.choice(("none", "always", "always")), "n": rng.randint(1, 5),
                       "save_min": rng.randint(1, 120)}
    s = spec.get("steve")
    if isinstance(s, dict):
        s = dict(s)
        if isinstance((s.get("runs") or {}).get("save_min"), tuple):
            s["runs"] = dict(s["runs"], save_min=rng.randint(*s["runs"]["save_min"]))
        reg["steve"] = s
    elif s:
        sr = {"mode": "always", "n": 2, "save_min": rng.randint(5, 90)}
        sb = {"kind": "const", "rate": u(1, 4)}
        if s[0] == "same_runs":
            reg["steve"] = {"account": "same", "runs": sr, "burn": sb}
        elif s[0] == "other_runs":
            reg["steve"] = {"account": rng.choice([a for a in ACCTS if a != live]), "runs": sr, "burn": sb}
        elif s[0] == "no_step":
            reg["steve"] = {"account": "steven", "runs": sr, "burn": sb}
            reset_h["steven"] = u(1, 119)       # steven past its 48 h window: no step uses it
            left["steven"] = u(55, 100)         # and above its line: the fault of d469f03d9d needs both
            if live == "steven":
                live = rng.choice(("system", "lukas"))
                reg["start"]["live"] = live
                left[live] = u(20, 100)
        elif s[0] == "unreachable":
            h = u(0, 48)
            reg["steve"] = {"account": "same", "runs": sr, "burn": sb, "unreachable_h": [h, h + u(1, 12)]}
        elif s[0] == "runs_blind":
            h = u(0, 48)
            reg["steve"] = {"account": "same", "runs": sr, "burn": sb, "runs_unread_h": [h, h + u(1, 12)]}
    else:
        reg["steve"] = rng.choice(({"account": "same", "runs": {"mode": "none"}},
                                   {"account": "same", "runs": {"mode": "always", "n": 2, "save_min": 30},
                                    "burn": {"kind": "const", "rate": 2}}))
    lp = spec.get("laptop")
    if lp and lp[0] == "all":
        reg["laptop"] = {"rate": u(1, 4), "from_h": 0, "to_h": 1e9, "account": live}
    elif lp:
        h = u(0, 60)
        reg["laptop"] = {"rate": u(1, 4), "from_h": h, "to_h": h + u(1, 30), "account": rng.choice(ACCTS)}
    p = spec.get("plan")
    if p and p[0] == "hold":
        reg["plan"] = {"kind": "hold", "at_h": u(0, 48), "hours": u(1, 8)}
    elif p and p[0] == "pin":
        reg["plan"] = {"kind": "pin", "account": live, "at_h": u(0, 24), "hours": u(6, 48)}
    elif p and p[0] == "line":
        a = rng.choice(ACCTS)
        reg["plan"] = {"kind": "line_until_reset", "account": a, "leave": rng.choice((1, 5, 10, 25, 40)),
                       "at_h": u(0, 48)}
    elif p and p[0] == "order":
        o = list(ACCTS)
        rng.shuffle(o)
        reg["plan"] = {"kind": "order", "order": o, "at_h": u(6, 60)}
    elif p and p[0] == "request":
        reg["plan"] = {"kind": "request", "to": rng.choice([a for a in ACCTS if a != live]), "at_h": u(0, 48),
                       "now": rng.random() < 0.5}
    sw = spec.get("switcher")
    if isinstance(sw, tuple):
        h = u(0, 48)
        reg["switcher"] = {"kind": "hour", "fail_h": [h, h + 1]}
    elif sw:
        reg["switcher"] = sw
    if spec.get("t0_shift_s"):
        reg["t0_shift_s"] = spec["t0_shift_s"]
    if spec.get("sched"):
        realize_schedules(spec, reg, rng, u)
    if spec.get("codex"):
        realize_codex(spec, reg, rng, u)
    return reg


def drift_of(spec, rng, u):
    d = spec.get("drift_h")
    return 0.0 if not d else round(rng.choice((-1, 1)) * u(*d), 3)


def realize_schedules(spec, reg, rng, u):
    """Line schedules on the Claude accounts of a regime, as points before each account's reset (sched_text renders
    them in the owner's words). Kinds: rising (the live account's line ramps up past its level), falling (another
    account's high line ramps down: it can take over in the middle of the week), cross (both), live_more (the live
    account's line ramps down, the next one flat), beside_window (a schedule on system beside steven's 48 h step)."""
    st = reg["start"]
    live, kind = st["live"], spec["sched"]
    others = [a for a in ACCTS if a != live]
    out = []

    def hb_now(a):
        r = st["reset_h"][a]
        return r if r > 0 else r + 168
    if kind in ("rising", "cross"):
        a, r = live, hb_now(live)
        st["left"][a] = u(20, 70)
        x = u(1, min(12, r - 4)) if r > 6 else 0.5
        hb1 = round(r - x, 2)
        hb2 = round(max(0.2, hb1 - u(2, 12)), 2)
        out.append({"account": a, "points": [[hb1, rng.choice((1, 3, 5)), "hold"],
                                             [hb2, min(95, round(st["left"][a] + u(5, 30))), "ramp"]]})
    if kind in ("falling", "cross"):
        b = rng.choice(others)
        r = hb_now(b)
        st["left"][b] = u(30, 80)
        hb1 = round(r - u(0.5, min(6, r - 2)), 2) if r > 3 else r
        hb2 = round(max(0.2, hb1 - u(6, 30)), 2)
        out.append({"account": b, "points": [[hb1, min(95, round(st["left"][b] + u(5, 15))), "hold"],
                                             [hb2, 5, "ramp"]]})
    if kind == "live_more":
        a, r = live, hb_now(live)
        st["left"][a] = u(25, 60)
        hb1 = round(r - u(1, min(24, r - 2)), 2) if r > 3 else r
        out.append({"account": a, "points": [[hb1, 30, "hold"], [round(max(0.2, hb1 - u(6, 48)), 2), 5, "ramp"]]})
    if kind == "beside_window":
        r = hb_now("system")
        hb1 = round(r - u(1, min(24, r - 2)), 2) if r > 3 else r
        out.append({"account": "system", "points": [[hb1, 40, "hold"], [round(max(0.2, hb1 - u(6, 48)), 2), 1, "ramp"]]})
    for sc in out:
        sc["drift_h"] = drift_of(spec, rng, u)
        if spec.get("at_h"):
            sc["at_h"] = u(*spec["at_h"])
    reg["schedules"] = out
    if spec.get("unread_near_point") and out:
        sc = out[0]
        h = st["reset_h"][sc["account"]] - sc["points"][-1][0]
        h = h if h > 0 else h + 168
        reg["meter"] = {"every_min": 5, "unread": {"account": rng.choice((sc["account"], "all")), "from_h": max(0, h - u(0.5, 3)),
                                                   "to_h": h + u(0.5, 3)}}
    if spec.get("laptop_on_sched") and out:
        reg["laptop"] = {"rate": u(1, 4), "from_h": u(0, 24), "to_h": 1e9, "account": out[0]["account"]}


def realize_codex(spec, reg, rng, u):
    """A Codex week: its start, its reset, the Codex lane's burn, the owner's own use, the meter, and the plan (today's
    flat 25%, the owner's example, or a schedule of the region)."""
    c = spec["codex"]
    x = {"weeks": c.get("weeks", 2), "reset_h": u(*c.get("reset_h", (1, 168))), "left": u(*c.get("left", (20, 100)))}
    fl = c.get("fleet", ("const", 0.2, 1.5))
    if fl[0] == "const":
        x["fleet"] = {"kind": "const", "rate": u(fl[1], fl[2])}
    elif fl[0] == "before_ramp":     # a burst in the 12 h before the ramp of the owner's example, each week
        start = x["reset_h"] - 61.5 - 12
        x["fleet"] = {"kind": "pulse", "base": u(0.1, 0.5), "peak": u(3, 8), "from_h": start % 168,
                      "to_h": start % 168 + 12, "period_h": 168}
    elif fl[0] == "burst":
        x["fleet"] = {"kind": "burst", "base": u(0.1, 0.5), "peak": u(2, 6), "on_h": u(1, 4), "period_h": u(8, 24),
                      "phase_h": u(0, 8)}
    if c.get("jitter_min"):
        x["jitter_min"] = round(u(*c["jitter_min"]), 2)
    if c.get("owner"):
        lo, hi = c["owner"]
        x["owner"] = {"days": [2, 3, 4, 5], "from_h": 9, "to_h": 23, "rate": u(lo, hi)}
    sk = c.get("schedule", "example")
    if sk == "example":
        x["schedule"] = {"example": True}
    elif sk == "unreadable":
        x["schedule"] = {"text": "Sat 23:59=40 hold; Tue 25:99=0 ramp", "points": [[61.5, 40, "hold"], [0, 0, "ramp"]]}
    elif sk == "at_reset":       # a point at the very minute of the reset, and one in the middle
        x["schedule"] = {"points": [[u(60, 120), rng.choice((30, 40, 50)), "hold"], [0, 0, "ramp"]]}
    elif sk == "steps":          # three held steps down to the reset
        a = u(100, 150)
        x["schedule"] = {"points": [[a, 50, "hold"], [round(a / 2, 2), 30, "hold"], [round(a / 4, 2), 10, "hold"],
                                    [0, 0, "hold"]]}
    if "schedule" in x:
        x["schedule"]["drift_h"] = drift_of(c, rng, u)
        if c.get("at_h"):
            x["schedule"]["at_h"] = u(*c["at_h"])
    if c.get("unread") == "near_point":
        h = (x["reset_h"] - 61.5) % 168
        x["unread_h"] = [max(0, h - u(0.5, 4)), h + u(0.5, 4)]
    elif c.get("unread") == "near_reset":
        h = x["reset_h"] % 168
        x["unread_h"] = [max(0, h - u(0.5, 4)), h + u(0.5, 4)]
    if c.get("post_reset"):
        x["post_reset_gap_min"] = rng.randint(*c["post_reset"])
    reg["codex"] = x


DST_MAR = AP.stamp("2027-03-11T18:00:00-08:00") - T0     # the week holds 2027-03-14 2:00 AM (clocks go forward)
DST_NOV = AP.stamp("2026-10-29T18:00:00-07:00") - T0     # the week holds 2026-11-01 2:00 AM (clocks go back)


def schedule_regions():
    """Line schedules on the Claude accounts, run through the real pass: each kind with each run state, the reset
    drifting from the schedule's, the meter unread near a point and after a reset, a schedule set mid-week, the two
    daylight-saving weeks, the owner's laptop on the scheduled account, a burst before a ramp."""
    R = []
    for kind, label in (("rising", "the live account's line ramps up past its level"),
                        ("falling", "another account's high line falls: it can take over mid-week"),
                        ("cross", "two schedules that cross"),
                        ("live_more", "the live account's line falls, the next account flat"),
                        ("beside_window", "a schedule on system beside steven's 48 h step")):
        for rl, runs in (("no run", {"mode": "none"}), ("4 runs, save in 1-30 min",
                                                         {"mode": "always", "n": 4, "save_min": (1, 30)}),
                         ("a run that never ends", {"mode": "never_ends", "n": 3, "save_min": (5, 30)})):
            R.append(("schedule: %s | %s" % (label, rl), {"sched": kind, "runs": runs, "hours": 96}))
    for d, label in (((0.02, 1), "1 min to 1 h"), ((1, 6), "1 to 6 h"), ((24, 72), "1 to 3 days")):
        R.append(("schedule: the reset is %s from the one the schedule was typed for" % label,
                  {"sched": "cross", "drift_h": d, "hours": 120}))
    R.append(("schedule: the meter cannot be read near a point", {"sched": "rising", "unread_near_point": True, "hours": 96}))
    R.append(("schedule: RESET PASSED with no level for 5-60 min, beside a falling line",
              {"sched": "falling", "meter": ("post_reset", 5, 60), "hours": 96}))
    R.append(("schedule: set in the middle of the week", {"sched": "cross", "at_h": (6, 48), "hours": 96}))
    R.append(("schedule: the week of the daylight-saving change in March", {"sched": "cross", "t0_shift_s": DST_MAR,
                                                                            "hours": 120}))
    R.append(("schedule: the week of the daylight-saving change in November", {"sched": "cross", "t0_shift_s": DST_NOV,
                                                                               "hours": 120}))
    R.append(("schedule: the owner's laptop burns the scheduled account (personal use)",
              {"sched": "rising", "laptop_on_sched": True, "hours": 96}))
    R.append(("schedule: a burst before a ramp", {"sched": "rising", "burn": ("burst",), "hours": 96}))
    R.append(("schedule: the step order changed mid-week, beside two schedules that cross",
              {"sched": "cross", "plan": ("order",), "hours": 96}))
    R.append(("schedule: readings 10-60 min old, beside a line that rises", {"sched": "rising", "meter": ("every", 10, 60),
                                                                           "hours": 96}))
    return R


FLEETS = (("slow (0.05-0.3/h: never reaches the line)", ("const", 0.05, 0.3)),
          ("medium (0.5-1.2/h, today's 0.8)", ("const", 0.5, 1.2)),
          ("fast (2.5-5/h: at the line on the first day)", ("const", 2.5, 5)),
          ("a burst of 3-8/h in the 12 h before the ramp", ("before_ramp",)))


CODEX_T0 = AP.stamp("2026-11-24T13:40:00-08:00")      # 4 min after a Codex reset (the meter's: Tuesday 1:36 PM)
CODEX_WEEK_H = (AP.stamp("2026-12-01T13:36:00-08:00") - CODEX_T0) / 3600


def codex_regions():
    """Codex on the real gate: the owner's example and today's flat 25% over the burn regimes, with and without his own
    use; then the corner cases of the example (the reset moving, the meter, the clock edges, a hand edit)."""
    R = []
    for fl, f in FLEETS:
        for ol, o in (("no personal use", None), ("his use Wed-Sat 9 AM-11 PM at 0.3-0.7/h", (0.3, 0.7))):
            for pl, sk in (("today's flat 25%", "flat"), ("the owner's example", "example")):
                # the real Codex week: from the reset of Tuesday 1:36 PM (2026-11-24), full, three weeks
                c = {"weeks": 3, "reset_h": (CODEX_WEEK_H, CODEX_WEEK_H), "left": (100, 100), "fleet": f, "schedule": sk}
                if o:
                    c["owner"] = o
                R.append(("codex: %s | %s | %s" % (pl, fl, ol), {"codex": c, "t0_shift_s": CODEX_T0 - T0}))
    ex = {"weeks": 2, "fleet": ("const", 0.5, 2), "schedule": "example", "reset_h": (CODEX_WEEK_H, CODEX_WEEK_H),
          "left": (100, 100)}
    for label, more in (("the meter's reset jitters by 1-60 min", {"jitter_min": (1, 60)}),
                        ("the reset is 1-6 h from the one the schedule was typed for", {"drift_h": (1, 6)}),
                        ("the reset is 1-3 days from the one the schedule was typed for", {"drift_h": (24, 72)}),
                        ("the meter cannot be read near the point of Saturday", {"unread": "near_point"}),
                        ("the meter cannot be read near the reset", {"unread": "near_reset"}),
                        ("a reading from before the reset for 5-60 min", {"post_reset": (5, 60)}),
                        ("the schedule set in the middle of the week", {"at_h": (6, 100)}),
                        ("a point at the reset's minute", {"schedule": "at_reset"}),
                        ("three held steps down to the reset", {"schedule": "steps"}),
                        ("a schedule that a hand edit broke", {"schedule": "unreadable"}),
                        ("his use Wed-Sat at 1-3/h (more than the reserve)", {"owner": (1, 3)})):
        R.append(("codex: the owner's example | %s" % label, {"codex": dict(ex, **more), "t0_shift_s": CODEX_T0 - T0}))
    for label, shift in (("March", DST_MAR), ("November", DST_NOV)):
        x = dict(ex)
        x.pop("reset_h")
        x.pop("left")
        R.append(("codex: the owner's example | the week of the daylight-saving change in %s" % label,
                  {"codex": x, "t0_shift_s": shift}))
    return R


def compare_table(results):
    """The owner's example against today's flat 25%, over the burn regimes: each measure, side by side (the mean over
    the regimes of each region, per week)."""
    by = {r["name"]: r for r in results}
    cols = (("reserve: h/week under the line", "under_line_h_per_week"), ("lowest gap", "lowest_gap"),
            ("erased at the reset, pts/week", "erased_per_week"), ("dark h/week", "dark_h_per_week"),
            ("owner starved h/week", "owner_starved_h_per_week"), ("fleet pts/week", "fleet_pts_per_week"),
            ("owner pts/week", "owner_pts_per_week"))
    out = ["| burn regime | his own use | plan | " + " | ".join(c for c, _k in cols) + " |",
           "|---|---|---|" + "---|" * len(cols)]
    for fl, _f in FLEETS:
        for ol in ("no personal use", "his use Wed-Sat 9 AM-11 PM at 0.3-0.7/h"):
            for pl in ("today's flat 25%", "the owner's example"):
                r = by.get("codex: %s | %s | %s" % (pl, fl, ol))
                if not r:
                    continue
                ms = r.get("all_measures") or []
                vals = []
                for _c, k in cols:
                    xs = [m[k] for m in ms if m.get(k) is not None]
                    vals.append("UNMEASURED" if not xs else g(min(xs)) if k == "lowest_gap" else g(sum(xs) / len(xs)))
                out.append("| %s | %s | %s | %s |" % (fl, ol, pl, " | ".join(vals)))
    return out


def regime_line(reg):
    if "codex" in reg:
        return "codex %s%s" % (json.dumps(reg["codex"], sort_keys=True), "; t0 shift %s s" % reg["t0_shift_s"]
                               if reg.get("t0_shift_s") else "")
    s = reg["start"]
    return ("live %s; left %s; resets in %s h; burn %s; runs %s; SteveDesktop %s%s%s%s%s" % (
        s["live"], {a: s["left"][a] for a in ACCTS}, {a: s["reset_h"][a] for a in ACCTS}, reg["burn"], reg["runs"],
        reg.get("steve"), "; laptop %s" % reg["laptop"] if reg.get("laptop") else "",
        "; meter %s" % reg["meter"] if reg.get("meter") != {"every_min": 5} else "",
        "; plan %s" % reg["plan"] if reg.get("plan") else "", "; switcher %s" % reg["switcher"] if reg.get("switcher")
        else "")) + ("; schedules %s" % json.dumps(reg["schedules"]) if reg.get("schedules") else "") + (
        "; t0 shift %s s" % reg["t0_shift_s"] if reg.get("t0_shift_s") else "")


def report(results, title):
    out = ["## %s" % title, ""]
    for r in results:
        out.append("- **%s**: %s (%d regimes, %.0f s)" % (r["name"], r["verdict"], r["n"], r["seconds"]))
        for c, v in sorted(r["violations"].items()):
            out.append("  - %s in %d regime(s); smallest: seed %d, at hour %s: %s" % (
                c, v["count"], v["seed"], v["h_first"], fulltext.fit(json.dumps(v["detail"], sort_keys=True), 400)))
            out.append("    - regime: `%s`" % regime_line(v["regime"]))
        ms = r.get("all_measures") or []
        if any("under_line_min" in m for m in ms):
            out.append("  - measures (each regime): " + "; ".join(measure_line(m) for m in ms))
        if r["verdict"] == "COSTLY":
            c = max(r["costly"], key=lambda x: x["by"])
            out.append("  - COSTLY in %d of %d: worst seed %d, %s points over the bound (plan: %s erased, %s switches, "
                       "%s idle; bound: %s erased, %s switches, %s idle, theta %s)" % (
                           len(r["costly"]), r["n"], c["seed"], c["by"], c["plan"]["erased_total"], c["plan"]["switches"],
                           c["plan"]["idle_pts"], c["bound"]["erased"], c["bound"]["switches"], c["bound"]["idle"],
                           c["bound"]["theta"]))
            out.append("    - regime: `%s`" % regime_line(c["regime"]))
    return out


def measure_line(m):
    """The measures of the line schedule page, in one line."""
    if "under_line_h_per_week" in m:        # a Codex week
        return ("under the line %s h/wk, lowest gap %s, erased %s/wk, dark %s h/wk, owner starved %s h/wk, line off "
                "the typed one by up to %s" % (m["under_line_h_per_week"], m["lowest_gap"], m["erased_per_week"],
                                              m["dark_h_per_week"], m["owner_starved_h_per_week"], m["line_shift_max"]))
    under = {a: v for a, v in (m.get("under_line_min") or {}).items() if v}
    return "under its line %s min, lowest gap %s, erased %s, dark %s h, %s switches (%s runs ended), fleet under %s" % (
        under or 0, {a: v for a, v in (m.get("lowest_gap") or {}).items() if v is not None and v < 5} or "none under 5",
        m.get("erased_total"), m.get("dark_h"), m.get("switches"), m.get("runs_ended_by_switch"), m.get("fleet_under_pts"))


QUICK = [("quick: tonight, burn 4-12, slow save, SteveDesktop with runs",
          {"burn": ("const", 4, 12), "runs": {"mode": "always", "n": 3, "save_min": (30, 120)},
           "steve": {"account": "same", "runs": {"mode": "always", "n": 2, "save_min": (5, 60)},
                     "burn": {"kind": "const", "rate": 2}},
           "left_steven": (53, 58), "left_system": (40, 95), "left_lukas": (2, 40), "hours": 12}),
         ("quick: the live account's reset passes with no level read for 20-60 min",
          {"meter": ("post_reset", 20, 60), "live_resets": True, "reset_in": (2, 8), "hours": 12}),
         ("quick: SteveDesktop on an account that no step uses", {"steve": ("no_step",), "hours": 12}),
         ("quick: a line schedule rises past the live account's level", {"sched": "rising", "hours": 12,
                                                                          "runs": {"mode": "always", "n": 3, "save_min": (1, 30)}}),
         ("quick: Codex on the owner's example, with his own use", {"codex": {"weeks": 1, "fleet": ("const", 0.5, 3),
                                                                              "schedule": "example", "owner": (1, 3)}}),
         ("quick: Codex with a line schedule that a hand edit broke", {"codex": {"weeks": 1, "fleet": ("const", 0.5, 3),
                                                                                  "schedule": "unreadable"}})]


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("what", choices=("tonight", "grid", "quick", "one", "schedules", "codex"))
    ap.add_argument("regime", nargs="?")
    ap.add_argument("--seeds", type=int, default=4, help="regimes drawn inside each region")
    ap.add_argument("--hours", type=float, default=None)
    ap.add_argument("--map", default=None, help="write the report here")
    ap.add_argument("--json", default=None, help="write every result here")
    ap.add_argument("--trace", default=None, help="one: write one line for each pass here")
    ap.add_argument("--only", default=None, help="quick, schedules, codex: only the regions whose name holds this text")
    a = ap.parse_args(argv)
    t = time.time()
    try:
        if a.what == "one":
            tr = [] if a.trace else None
            reg1 = json.loads(a.regime)
            r = codex_week(reg1) if "codex" in reg1 else run_regime(reg1, hours=a.hours, trace=tr)
            if tr is not None:
                Path(a.trace).write_text("\n".join(tr) + "\n")
            print(json.dumps(r, indent=1, sort_keys=True, default=str))
            return 1 if r["violations"] else 0
        pick = lambda regs: [q for q in regs if not a.only or a.only in q[0]]     # noqa: E731
        if a.what == "quick":
            res = run_regions(pick(QUICK), [1, 2])
        elif a.what == "tonight":
            res = run_regions(tonight_regions(), range(1, a.seeds + 1), a.hours)
        elif a.what == "schedules":
            res = run_regions(pick(schedule_regions()), range(1, a.seeds + 1), a.hours)
        elif a.what == "codex":
            res = run_regions(pick(codex_regions()), range(1, a.seeds + 1), a.hours)
        else:
            res = run_regions(tonight_regions() + axis_regions() + schedule_regions() + codex_regions(),
                              range(1, a.seeds + 1), a.hours)
        text = "\n".join(report(res, a.what)) + "\n"
        if a.what in ("codex", "grid"):
            text += "\n## The owner's example against today's flat 25%% (Codex, the mean per week over %d regimes each)\n\n" % (
                a.seeds) + "\n".join(compare_table(res)) + "\n"
        cnt = {k: sum(1 for r in res if r["verdict"] == k) for k in ("OK", "VIOLATES", "COSTLY")}
        text += "\n%s: %d regions, %d regimes, %.0f s: %d OK, %d VIOLATES, %d COSTLY\n" % (
            a.what, len(res), sum(r["n"] for r in res), time.time() - t, cnt["OK"], cnt["VIOLATES"], cnt["COSTLY"])
        if a.map:
            Path(a.map).write_text(text)
        if a.json:
            Path(a.json).write_text(json.dumps(res, default=str, indent=1))
        print(text)
        return 1 if cnt["VIOLATES"] else 0
    finally:
        shutil.rmtree(ROOT, ignore_errors=True)


if __name__ == "__main__":
    sys.exit(main())
