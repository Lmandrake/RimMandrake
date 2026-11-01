#!/usr/bin/env python3
"""fanout_sim.py - every architecture on the SAME fan-out terms (ARCH_SIM_MEASURE_FANOUT_EQUAL_TERMS).

WHY. The earlier process sims gave v2/v3 a helper pool with concurrency defects and no merge cost, gave Ralph one
context at a time (kappa forced to 0, "+sub" a bare wall divisor with no contention), and let TP/TP+ inherit that
divisor. Fan-out was therefore credited to some arms and denied to others. This module changes no existing sim: it
subclasses them so one worker pool and one set of contention costs apply to every arm.

THE COMMON TERMS (Fan mixin; arm-specific costs such as dispatch_min, restart, stack load, spirals, critics and
pilots stay where they were):
  - N worker slots for the whole arm. Helpers, Ralph iterations, quick work, critic rounds, pilot fixes and checks
    all compete for them. A ticket's nh units are the SAME keyed draws in every arm and any free slot may take one.
  - kappa: the defect rate of a ticket follows the workers beside it, theta * (1 + kappa c) / (1 + kappa c_ref), with
    c the mean others over the ticket's flight, capped at k_sat. Theta was calibrated at real concurrency, so c_ref
    carries it and N=1 sits BELOW theta. It is one rate on the base keyed Poisson, so base defects stay paired.
  - inherited b_collide / c_collide_area read serial_busy, which stays False here: the merge term replaces them.
  - merge: landing checks one conflict chance per ticket landed during this one's flight (same area c_merge, other
    area c_merge * x_area); a conflict costs m_ite and m_s and with m_redo reruns the ticket.
  - one landing server and two rig (bridge) servers: queue WAIT only, because the service itself is already inside
    the measured helper durations. Live-test chance is the base one in every arm: C's runner claims no bridge seat but
    still needs a rig. N=1 has no such queue, so it reduces to serial.
  - LLM judgement is a worker: Arbiter verdicts, critic rounds, pilot fixes and fair checks take a slot. Machine test
    runners (lane B, C's, TP's pilots) keep their own one or two servers, outside N, and pay their ITE.
  - w_ite per unit started while another worker runs (brief and return).
  - slow: wall inflation per worker above 4 (machine contention).
  - a fair check. Owner ruling 2026-10-31: fan-out counts only if work is fairly checked. An arm with no independent
    check of its own (v2, v3.0, the Ralph A/AB/C lanes) pays a blind check on every ticket that overlapped another:
    a slot, chk_min, chk_ite, sensitivity chk_s, false reject chk_fr. Arms whose Arbiter or critic really passed the
    ticket pay nothing twice. Phase "postchk" checks every ticket, N=1 included. Weekly quotas stay the base model's.

Identity: with kappa 0, Ralph A at N=1 reproduces RalphSim A (selftest), so this generalises the serial loop.
Known and accepted: v3 quick tickets pay no helper ITE because the base model books them in seat_ite_per_close, while
Ralph pays r_ctx + r_quick; the off-track draw stays keyed by lane iteration so the identity holds, which adds noise
across N but no bias.
Ranges in FO_PRIORS are ASSUMED; POSTERIOR holds ranges constrained by the census and names the evidence. Results:
design/RimMandrake/fanout_sim_refit_2026-11-01.md.

    fanout_sim.py sweep --phase prior|post --scenario pull_present [--members 40] [--procs 4] [--budget-s 500]
    fanout_sim.py report [--json OUT]
    fanout_sim.py one --arm A --n 4
Rows go to RM_FANOUT_OUT (default D:/ClaudeWork/rimmandrake/fanout_sim_2026-11-01). Offline, stdlib + numpy.
"""
import argparse
import collections
import copy
import hashlib
import json
import math
import multiprocessing
import os
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import rimflow_v3_sim as S  # noqa: E402
import ralph_loop_sim as R  # noqa: E402
import testpilot_sim as TP  # noqa: E402

OUT = os.environ.get("RM_FANOUT_OUT", "/mnt/d/ClaudeWork/rimmandrake/fanout_sim_2026-11-01")
HOUR, DAY = S.HOUR, S.DAY
F_STOCK, F_STOCKCLS, F_MERGE, F_REDO, F_CHK, F_CHKFR, F_FOTHETA = range(201, 208)   # clear of the other sims' fields
SWEEP_N = (1, 2, 4, 8)
ARMS = ("v2", "v3.0", "v3.4", "A", "AB_test", "AB_build", "C", "TP", "TP+")
TRIAL_NAMES = {"v3.4": "trial v3", "A": "trial ralph_a", "C": "ralph_c (not in replay)", "TP+": "trial trio (nearest)"}
PHASES = ("prior", "post", "postslow", "postchk", "hold")
SCENARIOS = ("pull_present", "pull_unattended", "park_present")

FO_PRIORS = {
    "kappa": (0.0, 0.15, "relative extra defects per other worker in flight (the old sim's range)"),
    "k_sat": (7.0, 7.0, "others beyond which kappa stops growing (prior: it never does, up to N=8)"),
    "c_merge": (0.0005, 0.03, "conflict chance per ticket landed in the same area during this one's flight"),
    "x_area": (0.05, 0.5, "that chance for a ticket landed in the other area, against c_merge"),
    "m_s": (120.0, 1200.0, "wall seconds of rebase and re-test after a conflict, holding the slot"),
    "m_ite": (50e3, 400e3, "ITE of that repair"),
    "m_redo": (0.05, 0.4, "chance a conflict reruns the ticket instead of being resolved in place"),
    "land_s": (20.0, 180.0, "landing server occupancy per ticket"),
    "rig_min": (10.0, 45.0, "live-verify occupancy of one of two rig servers"),
    "w_ite": (10e3, 150e3, "ITE per unit started beside another worker (brief and return)"),
    "chk_s": (0.3, 0.7, "fair check sensitivity to a visible defect"),
    "chk_fr": (0.02, 0.2, "fair check false reject"),
    "chk_ite": (100e3, 300e3, "ITE per fair check"),
    "chk_min": (2.0, 15.0, "wall minutes per fair check, holding a slot"),
    "slow": (0.0, 0.05, "wall inflation per worker above 4"),
    "c_ref": (1.0, 2.0, "others beside a ticket when theta was calibrated: census means 1.2 by seat, 1.9 overall"),
}
# name -> (lo, hi, evidence). Parameters absent here keep their prior: nothing measured them.
POSTERIOR = {
    "fo": {
        "kappa": (0.10, 0.50, "1,084 verifies, seat-day FE: 0.33 +- 0.19; first verifies only 0.35 +- 0.31"),
        "k_sat": (2.0, 4.0, "verify fail by workers: 0.05 under 1.5, 0.14 at 1.5-3, 0.11 at 3-5, 0.10 above 5"),
        "c_merge": (0.0003, 0.003, "21 unique conflicts in 6,482 publishes over 2.4-7 landings in flight"),
        "chk_ite": (150e3, 260e3, "relentless: 44 blind checks, mean 206k, median 172k"),
        "chk_min": (3.0, 9.0, "relentless: 44 blind checks, p50 3.2 min, p90 19 min"),
        "chk_fr": (0.03, 0.15, "relentless: 9-11 of 44 checks failed; false rejects can only be a part of that"),
        "slow": (0.0, 0.01, "4,812 helpers: duration and ITE do not rise with concurrency (corr -0.15, -0.07)"),
    },
    "rp": {
        "r_p_off": (0.10, 0.45, "ralph_a 6 of 14 passes failed; relentless about 14 of 66 leases genuinely off track"),
        "r_ite_mult": (0.65, 1.12, "paired ralph_a/v3 ITE on 6 tasks: geometric mean 0.85, se(log) 0.14"),
        "c_invalid": (0.05, 0.40, "gate invalid: v3 3/27, ralph_a 11/27, trio 10/23; arms disagree, so it widened"),
    },
    "tp": {
        "crit_ite": (130e3, 260e3, "relentless blind checks are the same job; trio's own capture is UNMEASURED"),
        "crit_min": (3.0, 10.0, "relentless blind checks"),
        "p_invalid": (0.05, 0.40, "trio tests invalid 5 of 13; v3 3 of 27 at the gate; widened"),
    },
}


HOLD_FO = ("chk_ite", "chk_min", "chk_fr")        # phase "hold" keeps these at prior
HOLD_P_OFF = (0.20, 0.66)                         # ralph_a alone: 6 of 14 passes, Wilson 80% interval


# sensitivities on phase post. The wall ratio is per task, so it already holds restarts, off-track passes and checks
# that the sim charges apart: it does not identify r_dur_mult, which keeps its prior in "post" and takes this box here.
SLOW_DUR = (1.0, 2.5)
STOCK_PER_H = 10              # tickets per hour into an unattended queue; must exceed every arm's clearing rate


def fingerprint():
    h = hashlib.sha1((R.FP + TP.FP).encode())
    h.update(open(os.path.join(HERE, "fanout_sim.py"), "rb").read().split(b"# " + b"-" * 40 + b" reporting")[0])
    return h.hexdigest()[:12]


def _draw(table, member, seed, field):
    return {k: lo + (hi - lo) * S.u01(seed, field, member, i)
            for i, (k, (lo, hi)) in enumerate(sorted((k, v[:2]) for k, v in table.items()))}


def draw_fo(member, phase="prior", seed=4242):
    tab = FO_PRIORS if phase == "prior" else dict(FO_PRIORS, **POSTERIOR["fo"])
    return _draw(tab, member, seed, F_FOTHETA)


def apply_posterior(rp, tp, member, seed=4243):
    """redraw only the constrained parameters, on the same keyed unit values as their prior draw was not: the keys
    are new, so a posterior member is a fresh draw inside the posterior box"""
    rp, tp = dict(rp), dict(tp)
    for i, (k, (lo, hi, _)) in enumerate(sorted(POSTERIOR["rp"].items())):
        rp[k] = lo + (hi - lo) * S.u01(seed, F_FOTHETA, member, 50 + i)
    for i, (k, (lo, hi, _)) in enumerate(sorted(POSTERIOR["tp"].items())):
        tp[k] = lo + (hi - lo) * S.u01(seed, F_FOTHETA, member, 80 + i)
    return rp, tp


class Fan:
    """the shared pool. Events travel as ("arb_done", "FO", (name, ...)) because Sim.run dispatches a closed set of
    kinds and this module must not edit it."""

    def fo_setup(self, n, fo, own_check, unattended):
        self.fo_spin = set()
        self.N, self.fo, self.own_check = n, fo, own_check
        self.busy = 0
        self.peak = 0                 # highest occupancy actually reached; the selftest compares it with N
        self.reserved = 0             # a dispatch in progress already owns its slot
        self.live = collections.Counter()
        self.fo_start = {}            # ticket -> (t, occupancy integral) at this attempt's start
        self.fo_over = set()          # tickets that ever overlapped another worker; sticky across attempts
        self.fo_redone = set()        # a merge rerun is full work, not a repair
        self.fo_land0 = {}
        self.area, self.area_t = 0.0, 0.0
        self.area_week = collections.Counter()
        self.landed = {"FOUNDRY": 0, "BENCH": 0}
        self.land_free = 0.0
        self.rig_free = [0.0, 0.0]
        self.jobs = collections.deque()
        self.checked = set()          # tickets whose CURRENT result passed the fair check; repair clears it
        self.now = 0.0
        self.th["kappa"] = 0.0        # the base model's term stays off; fo_finish scales the rate instead
        self.fo_stocked = unattended
        if unattended:
            self.present = [False] * len(self.present)
            if hasattr(self, "owner_busy"):
                self.owner_busy = [False] * len(self.owner_busy)

    # ---- slots
    def fo_used(self):
        return self.busy + self.reserved

    def fo_tick(self, t):
        """occupancy integral, split at week ends: the census's concurrency and each ticket's exposure"""
        while self.area_t < t:
            end = min(t, (self.area_t // S.WEEK + 1) * S.WEEK)
            d = self.busy * (end - self.area_t)
            self.area += d
            self.area_week[int(self.area_t // S.WEEK)] += d
            self.area_t = end

    def fo_take(self, t, tk=None):
        self.fo_tick(t)
        self.busy += 1
        self.peak = max(self.peak, self.fo_used())
        if tk is not None:
            self.live[tk] += 1
        if self.busy >= 2:            # overlap is an event: a mean over the flight hides it behind any dispatch gap
            self.fo_over.update(self.live)

    def fo_drop(self, t, tk=None):
        self.fo_tick(t)
        self.busy -= 1
        if tk is not None:
            self.live[tk] -= 1
            if self.live[tk] <= 0:
                del self.live[tk]

    def fo_release(self, t, tk=None):
        self.fo_drop(t, tk)
        self.fo_wake(t)

    def fo_wake(self, t):
        self.fo_pump(t)
        for s in self.seats.values():
            self.try_work(s, t)

    def fo_pump(self, t):
        while self.jobs and self.fo_used() < self.N and not self.all_blocked:
            dur, ev, ite, what = self.jobs.popleft()
            self.fo_take(t)
            if ite:
                self.charge(t, ite, what)
            S.Sim.push(self, t + self.fo_dur(dur), "arb_done", "FO", ev)

    def fo_job(self, t, dur, ev, ite=0.0, what=""):
        self.jobs.append((dur, ev, ite, what))
        self.fo_pump(t)

    def fo_dur(self, d):
        return d * (1.0 + self.fo["slow"] * max(0, self.busy - 4))

    def fo_unit(self, t, s, tk, dur, kind="unit"):
        beside = self.busy > 0
        self.fo_take(t, tk)
        if beside:
            self.charge(t, self.fo["w_ite"], "fo_brief")
        self.push(t + self.fo_dur(dur), "arb_done", "FO", (kind, s.name, tk))

    def fo_begin_ticket(self, t, tk):
        self.fo_tick(t)
        self.fo_land0[tk] = dict(self.landed)
        self.fo_start[tk] = (t, self.area)

    def fo_exposure(self, t, tk):
        """mean others beside this attempt; own sibling units count, as nh did in the base kappa term"""
        self.fo_tick(t)
        t0, a0 = self.fo_start.get(tk, (t, self.area))
        return max(0.0, (self.area - a0) / (t - t0) - 1.0) if t > t0 else 0.0

    # ---- dispatch
    def arb_done(self, t, a, b):
        self.now = t
        if a != "FO":
            return super().arb_done(t, a, b)
        kind = b[0]
        if kind == "unit":
            self.fo_unit_done(t, self.seats[b[1]], b[2])
        elif kind == "spin":
            self.fo_spin.discard(b[1])
            self.fo_release(t)
        elif kind == "redo":
            self.fo_redo_now(t, b[1])
        elif kind == "land":
            self.fo_land(t, self.seats[b[1]], b[2])
        elif kind == "final":
            self.fo_final(t, self.seats[b[1]], b[2])
        elif kind == "check":
            self.fo_check_done(t, b[1])
        elif kind == "own":                  # an arm's own judgement (Arbiter, critic, pilot fix) that took a slot
            self.fo_drop(t)
            super().arb_done(t, b[1], b[2])
            self.fo_wake(t)

    def fo_unit_done(self, t, s, tk):
        tk.pending -= 1
        if tk.pending > 0:
            self.fo_release(t, tk)
            return
        if getattr(self, "off", {}).get(tk):   # an off-track iteration commits nothing: nothing to land
            self.fo_finish(t, s, tk)
            return
        wait = 0.0
        if self.N > 1:                       # at N>1 the servers are shared whoever else is in flight just now
            # the BASE chance, not the arm's: C's runner claims no bridge seat but its live test still needs the rig
            if S.u01(self.seed, S.F_VER, tk.key, tk.attempt) < self.P["fixed"]["p_verify"]["value"]:
                i = 0 if self.rig_free[0] <= self.rig_free[1] else 1
                rs = self.fo["rig_min"] * 60
                start = max(t, self.rig_free[i])
                self.rig_free[i] = start + rs
                wait = start - t
                self.add(t, "fo_rig_wait_min", wait / 60)
            start = max(t + wait, self.land_free)
            self.land_free = start + self.fo["land_s"]
            self.add(t, "fo_land_wait_min", (start - t - wait) / 60)
            wait = start - t
        if wait > 0:
            self.push(t + wait, "arb_done", "FO", ("land", s.name, tk))
        else:
            self.fo_land(t, s, tk)

    def fo_land(self, t, s, tk):
        c, x = self.fo["c_merge"], self.fo["x_area"]
        base = self.fo_land0.get(tk, self.landed)
        same, other = 0, 0
        for a, n in self.landed.items():
            d = n - base.get(a, n)
            if a == tk.seat:
                same += d
            else:
                other += d
        p = 1.0 - (1.0 - c) ** same * (1.0 - c * x) ** other
        if p > 0 and S.u01(self.seed, F_MERGE, tk.key, tk.attempt) < p:
            self.add(t, "fo_conflicts")
            self.charge(t, self.fo["m_ite"], "fo_merge")
            if S.u01(self.seed, F_REDO, tk.key, tk.attempt) < self.fo["m_redo"]:
                self.add(t, "fo_redo")
                self.push(t + self.fo["m_s"], "arb_done", "FO", ("redo", tk))
                return
            self.push(t + self.fo["m_s"], "arb_done", "FO", ("final", s.name, tk))
            return
        self.fo_final(t, s, tk)

    def fo_redo_now(self, t, tk):
        self.fo_redone.add(tk)
        self.fo_release(t, tk)
        tk.attempt += 1
        self.enqueue(t, tk, front=True)

    def fo_landed(self, tk):
        self.landed[tk.seat] += 1

    def fo_final(self, t, s, tk):
        self.fo_landed(tk)
        self.fo_finish(t, s, tk)

    def fo_finish(self, t, s, tk):
        fo, th = self.fo, self.th
        c = self.fo_exposure(t, tk)
        rate = (1 + fo["kappa"] * min(c, fo["k_sat"])) / (1 + fo["kappa"] * min(fo["c_ref"], fo["k_sat"]))
        if tk in self.fo_redone:             # base complete would read this attempt as a repair
            self.fo_redone.discard(tk)
            rate /= 0.3
        self.fo_drop(t, tk)
        self.fo_pump(t)
        self.now = t
        held = th["mu_prod"], th["mu_proc"]
        th["mu_prod"], th["mu_proc"] = held[0] * rate, held[1] * rate
        self.complete(t, s, tk)
        th["mu_prod"], th["mu_proc"] = held
        self.after_completion(s, t)
        self.fo_wake(t)

    # ---- the fair check
    def fo_own_check(self, tk):
        return False

    def repair(self, t, tk, hit):
        self.checked.discard(tk)             # new work, so the old pass no longer covers it
        super().repair(t, tk, hit)

    def close(self, t, tk):
        self.now = t
        if (self.fo_own_check(tk) or tk in self.checked
                or not (tk in self.fo_over or self.fo.get("chk_all"))):
            return super().close(t, tk)
        self.add(t, "fo_checks")
        self.fo_job(t, self.fo["chk_min"] * 60, ("check", tk), self.fo["chk_ite"], "fo_check")

    def fo_check_done(self, t, tk):
        self.fo_drop(t)
        hit = [d for j, d in enumerate(tk.defects) if d[0] == 0 and not d[1]
               and S.u01(self.seed, F_CHK, tk.key, tk.attempt, j) < self.fo["chk_s"]]
        if hit or S.u01(self.seed, F_CHKFR, tk.key, tk.attempt) < self.fo["chk_fr"]:
            self.add(t, "fo_check_fail")
            self.repair(t, tk, hit)
        else:
            self.checked.add(tk)
            super().close(t, tk)
        self.fo_wake(t)


def _stamp(name):
    """Fan.push needs the current time to turn a pushed end time into a duration; Sim.run keeps it in a local"""
    def f(self, t, *a):
        self.now = t
        return getattr(super(Fan, self), name)(t, *a)
    return f


def _hour(self, t):
    """Unattended is not idle: the owner is away but the queue holds a stock, as the relentless store does. Without it
    the only tickets are those a role invents, and that ranks proposers, not workers. The stock arrives faster than any
    arm can clear it, costs no owner time, and carries the owner's class mix."""
    self.now = t
    if self.fo_stocked:
        h = int(t // S.HOUR)
        for i in range(STOCK_PER_H):
            k = S.mix(self.seed, F_STOCK, h, i)
            cls = "product" if S.u01(self.seed, F_STOCKCLS, k) < self.th["p_prod_ext"] else "process"
            self.file_ticket(t + i * 60, k, cls, "owner")
    return super(Fan, self).hour(t)


Fan.hour = _hour
for _n in ("day", "ring_tick", "week_reset", "activate", "resume", "disc", "arb_start"):
    setattr(Fan, _n, _stamp(_n))


class FanRalph(Fan, R.RalphSim):
    def __init__(self, P, theta, variant, rp, seed, n, fo, weeks=4, quotas=None, unattended=False):
        super().__init__(P, theta, variant, rp, seed, weeks=weeks, quotas=quotas)
        self.fo_setup(n, fo, own_check=False, unattended=unattended)
        self.unit_q = collections.deque()

    def fo_units(self, tk):
        """iter_cost at r_par 1, unit by unit: the first carries restart and context, so N=1 is the serial iteration"""
        rp, th = self.rp, self.th
        if tk.quick and tk.attempt == 0:
            return [(rp["r_restart_s"] + th["quick_min"] * 60 * rp["r_dur_mult"], rp["r_ctx_ite"] + rp["r_quick_ite"])]
        nh = 1 + S.poisson(max(0.0, th["helpers_per_job"] - 1), self.seed, S.F_NHELP, tk.key, tk.attempt)
        units = []
        for i in range(nh):
            u = S.u01(self.seed, S.F_HELP, tk.key, tk.attempt, i)
            units.append((S.qsample(self.fx["helper_dur_q"][tk.seat], u) * rp["r_dur_mult"],
                          S.qsample(self.fx["helper_ite_q"][tk.seat], u) * rp["r_ite_mult"]))
        units[0] = (units[0][0] + rp["r_restart_s"], units[0][1] + rp["r_ctx_ite"])
        return units

    def fo_start_units(self, t):
        while self.unit_q and self.fo_used() < self.N and not self.all_blocked:
            ls, tk, d, ite = self.unit_q.popleft()
            self.charge(t, ite, "ralph_iter")
            self.fo_unit(t, ls, tk, d)

    def try_work(self, s, t):
        self.now = t
        self.fo_pump(t)
        if self.all_blocked:
            return
        self.fo_start_units(t)
        if s.name not in self.lanes:
            return
        if s.stalled:
            if self.fo_used() < self.N and not self.unit_q and s.name not in self.fo_spin:     # a spiral eats one worker
                self.iter_n[s.name] += 1
                u = S.u01(self.seed, R.F_SPIN, S.SEATS.index(s.name), self.iter_n[s.name])
                dur = self.rp["r_restart_s"] + S.qsample(self.fx["helper_dur_q"][s.name], u) * self.rp["r_dur_mult"]
                ite = self.rp["r_ctx_ite"] + S.qsample(self.fx["helper_ite_q"][s.name], u) * self.rp["r_ite_mult"]
                self.charge(t, ite, "ralph_iter")
                self.add(t, "iters")
                self.add(t, "iters_wasted")
                self.fo_take(t)
                self.fo_spin.add(s.name)
                self.push(t + self.fo_dur(dur), "arb_done", "FO", ("spin", s.name))
            return
        while self.fo_used() < self.N and not self.unit_q and not self.all_blocked:
            tk = self.pop(s, t)
            if tk is None:
                tk = self.pull(s, t)
            if tk is None:
                return
            self.iter_n[s.name] += 1
            self.off[tk] = S.u01(self.seed, R.F_ROFF, S.SEATS.index(s.name), self.iter_n[s.name]) < self.rp["r_p_off"]
            units = self.fo_units(tk)
            self.add(t, "iters")
            tk.pending = len(units)
            self.inflight[s.name] += 1
            self.fo_begin_ticket(t, tk)
            self.unit_q.extend((s, tk, d, i) for d, i in units)
            self.fo_start_units(t)


class FanTP(Fan, TP.TPSim):
    """TP's critic rounds and pilot fixes are workers too: they queue for a slot like everyone's"""

    def __init__(self, P, theta, variant, rp, tp, seed, n, fo, weeks=4, quotas=None, const=None, unattended=False):
        super().__init__(P, theta, variant, rp, tp, seed, weeks=weeks, quotas=quotas, const=const)
        self.fo_setup(n, fo, own_check=True, unattended=unattended)
        self.unit_q = collections.deque()

    fo_units = FanRalph.fo_units
    fo_start_units = FanRalph.fo_start_units
    try_work = FanRalph.try_work

    def fo_own_check(self, tk):
        return True

    def push(self, t, kind, *pl):
        if kind == "arb_done" and pl[0] != "FO" and isinstance(pl[1], tuple) and pl[1][:2] in (("TP", "crit"),
                                                                                                ("TP", "fix")):
            return self.fo_job(self.now, t - self.now, ("own", pl[0], pl[1]))
        S.Sim.push(self, t, kind, *pl)


class FanV3(Fan, TP.V3Strict):
    def __init__(self, P, theta, policy, rp, seed, n, fo, weeks=4, quotas=None, unattended=False):
        super().__init__(P, dict(theta), policy, seed, weeks=weeks, quotas=quotas, warm_weeks=1, rp=rp)
        self.fo_setup(n, fo, own_check=False, unattended=unattended)

    def fo_own_check(self, tk):
        return bool(tk.accepted)      # the Arbiter really passed this ticket, not merely exists in the policy

    def push(self, t, kind, *pl):
        if kind == "arb_done" and pl[0] != "FO":     # an Arbiter verdict is a worker
            return self.fo_job(self.now, t - self.now, ("own", pl[0], pl[1]))
        S.Sim.push(self, t, kind, *pl)

    def seat_cap(self, s, t):
        c = self.N
        if self.pol.get("throttle") == "helpers_first" and self.throttle_k > 0:
            c = min(c, 1)
        return c

    def try_work(self, s, t):
        self.now = t
        self.fo_pump(t)
        if s.stalled or s.serial_busy or self.all_blocked:
            return
        free = self.fo_used() < self.N
        if s.launch_q:
            if free and s.running < self.seat_cap(s, t):
                tk, i = s.launch_q.popleft()
                s.serial_busy = True
                self.reserved += 1
                self.push(t + self.th["dispatch_min"] * 60, "launch", s.name, tk, i)
            return
        if not free:
            return                    # a released slot wakes every seat
        tk = self.pop(s, t)
        if tk is None and self.parked[s.name]:
            tk = self.parked[s.name].popleft()
            self.add(t, "pulled_from_backlog")
        if tk is None:
            if s.running == 0:
                self.stall(s, t, empty=True)
            return
        self.fo_begin_ticket(t, tk)
        if tk.quick and tk.attempt == 0:
            s.serial_busy = True
            tk.pending = 1
            self.fo_unit(t, s, tk, self.th["quick_min"] * 60, kind="quick")
            return
        tk.nh = 1 + S.poisson(max(0.0, self.th["helpers_per_job"] - 1), self.seed, S.F_NHELP, tk.key, tk.attempt)
        tk.pending = tk.nh
        for i in range(tk.nh):
            s.launch_q.append((tk, i))
        self.try_work(s, t)

    def launch(self, t, s, tk, i):
        self.now = t
        s.serial_busy = False
        self.fo_tick(t)
        self.reserved -= 1            # handed straight to fo_unit below, with no wake between
        u = S.u01(self.seed, S.F_HELP, tk.key, tk.attempt, i)
        ite = S.qsample(self.fx["helper_ite_q"][s.name], u)
        dur = S.qsample(self.fx["helper_dur_q"][s.name], u)
        if self.role("Operations", t):
            ite *= self.th["m_ops_waste"]
        self.charge(t, ite, "helpers")
        self.add(t, "helpers")
        s.running += 1
        self.fo_unit(t, s, tk, dur)
        self.try_work(s, t)

    def fo_unit_done(self, t, s, tk):
        s.running -= 1
        super().fo_unit_done(t, s, tk)

    def arb_done(self, t, a, b):
        if a == "FO" and b[0] == "quick":
            s = self.seats[b[1]]
            s.serial_busy = False
            s.running += 1            # balances the decrement in fo_unit_done
            return self.fo_unit_done(t, s, b[2])
        super().arb_done(t, a, b)


# ---------------------------------------------------------------- running
KEEP = ["sound_prod_d", "done_d", "escapes_wk", "ite_week", "blocked_h", "defect_frac", "nudges_d", "prod_q_end"]


def row_of(sim, rows):
    rows = [R.add_derived(r) for r in rows]
    out = {k: R.wmean(rows, k) for k in KEEP}
    ms = sim.m[1:]
    wk = max(1, len(ms))
    for k in ("fo_conflicts", "fo_redo", "fo_checks", "fo_check_fail", "fo_land_wait_min", "fo_rig_wait_min"):
        out[k] = sum(m.get(k, 0.0) for m in ms) / wk
    sim.fo_tick(sim.T_end)
    out["mean_busy"] = sum(sim.area_week[w] for w in range(1, sim.weeks)) / (wk * S.WEEK)   # the census's measure
    out["peak"] = sim.peak
    out["sound_per_gite"] = out["sound_prod_d"] * 7 / (max(1.0, out["ite_week"]) / 1e9)
    return out


def build(P, m, arm, n, rp, tp, fo, scenario):
    seed = 50000 + m["member"] * 97
    q = dict(m["quotas"])
    un = scenario.endswith("unattended")
    if arm in ("v2", "v3.0", "v3.4"):
        return FanV3(P, m["theta"], S.policy_cfg(P, arm), rp, seed, n, fo, quotas=q, unattended=un)
    if arm in ("TP", "TP+"):
        r = dict(rp, r_par=1.0, r_par_ite=1.0)
        return FanTP(P, m["theta"], arm, r, tp, seed, n, fo, quotas=q, unattended=un)
    return FanRalph(P, m["theta"], arm, dict(rp), seed, n, fo, quotas=q, unattended=un)


def job(a):
    phase, scenario, member_row, arm, n, rep = a
    S.STRUCTURE = "park" if scenario.startswith("park") else "pull"
    P = S.load_params()
    uid = member_row["member"] + 1000 * rep       # a rep redraws everything the ABC ensemble does not fix
    m = dict(member_row, member=uid)
    rp, tp, fo = draws(uid, phase)
    sim = build(P, m, arm, n, rp, tp, fo, scenario)
    res = sim.run()
    return {"fp": FP, "phase": phase, "scenario": scenario, "member": uid, "arm": arm, "n": n,
            "row": row_of(sim, res)}


def draws(uid, phase):
    rp, tp = R.draw_rp(uid), TP.draw_tp(uid)
    fo = draw_fo(uid, phase)
    if phase in ("post", "hold"):
        rp, tp = apply_posterior(rp, tp, uid)
    if phase == "postslow":
        rp, tp = apply_posterior(rp, tp, uid)
        rp["r_dur_mult"] = SLOW_DUR[0] + (SLOW_DUR[1] - SLOW_DUR[0]) * S.u01(4245, F_FOTHETA, uid)
    if phase == "postchk":
        rp, tp = apply_posterior(rp, tp, uid)
        fo = dict(fo, chk_all=1.0)
    if phase == "hold":                           # the relentless run is held out: its evidence must not leak in
        fo = dict(draw_fo(uid, "post"), **{k: draw_fo(uid, "prior")[k] for k in HOLD_FO})
        rp["r_p_off"] = HOLD_P_OFF[0] + (HOLD_P_OFF[1] - HOLD_P_OFF[0]) * S.u01(4244, F_FOTHETA, uid)
    return rp, tp, fo


def rows_path(phase, scenario):
    return os.path.join(OUT, f"rows_{phase}_{scenario}.jsonl")


def load_rows(phase, scenario):
    p = rows_path(phase, scenario)
    if not os.path.exists(p):
        return []
    return [r for r in map(json.loads, open(p)) if r["fp"] == FP]


def cmd_sweep(a):
    done = {(r["member"], r["arm"], r["n"]) for r in load_rows(a.phase, a.scenario)}
    ms = R.members("park" if a.scenario.startswith("park") else "pull", a.members)
    ns = [int(x) for x in a.ns.split(",")]
    arms = a.arms.split(",") if a.arms else ARMS
    todo = [(a.phase, a.scenario, m, arm, n, rep) for rep in range(a.reps) for m in ms for arm in arms for n in ns
            if (m["member"] + 1000 * rep, arm, n) not in done]
    t0 = time.time()
    k = 0
    with multiprocessing.Pool(a.procs) as pool, open(rows_path(a.phase, a.scenario), "a") as fh:
        it = pool.imap_unordered(job, todo, chunksize=2)
        try:
            for r in it:
                fh.write(json.dumps(r) + "\n")
                fh.flush()
                k += 1
                if time.time() - t0 > a.budget_s:
                    pool.terminate()
                    break
        except KeyboardInterrupt:
            pool.terminate()
    print(f"sweep {a.phase}/{a.scenario}: +{k}, left {len(todo) - k}, {time.time() - t0:.0f}s")


def cmd_one(a):
    ms = R.members("park" if a.scenario.startswith("park") else "pull", 1)
    r = job((a.phase, a.scenario, ms[0], a.arm, a.n, 0))
    print(json.dumps(r["row"], indent=1))


# ---------------------------------------- reporting
def table(phase, scenario, key="sound_prod_d"):
    by = collections.defaultdict(dict)
    for r in load_rows(phase, scenario):
        by[r["member"]][(r["arm"], r["n"])] = r["row"].get(key, float("nan"))
    return by


def summarize(phase, scenario, key="sound_prod_d"):
    """medians with 80% bands over members holding every cell. Win shares: N is chosen per arm on one half of the members
    and scored on the other, over many random halves, so "best N" is not flattered by a maximum on its own noise.
    best_n and the gaps are descriptive, over all members; a win share describes this ensemble, not a probability."""
    by = table(phase, scenario, key)
    need = {(a, n) for a in ARMS for n in SWEEP_N}
    by = {m: v for m, v in by.items() if need <= set(v) and all(math.isfinite(v[c]) for c in need)}
    cells = {c: [v[c] for v in by.values()] for c in need}
    med = {f"{a}|{n}": [round(float(np.percentile(v, q)), 2) for q in (10, 50, 90)] + [len(v)]
           for (a, n), v in sorted(cells.items())} if by else {}
    order = sorted(by)                   # member ids are not consecutive, so split on position
    wins = collections.Counter()
    splits = 41                          # one split carries selection noise of its own; shares are averaged over these
    best_n = {}
    half = (len(order) + 1) // 2
    for r in range(splits):
        pick = list(np.random.default_rng(r).permutation(len(order)))
        fit, hold = [by[order[i]] for i in pick[:half]], [by[order[i]] for i in pick[half:]]
        bn = {a: max(SWEEP_N, key=lambda n: float(np.median([v[(a, n)] for v in fit]))) for a in ARMS} if fit else {}
        wins.update(max(ARMS, key=lambda a: v[(a, bn[a])]) for v in hold)
    wins = {a: round(w / splits) for a, w in wins.items()}
    best_n = {a: max(SWEEP_N, key=lambda n: float(np.median([v[(a, n)] for v in by.values()]))) for a in ARMS} if by else {}
    atn = {str(n): dict(collections.Counter(max(ARMS, key=lambda a: v[(a, n)]) for v in by.values())) for n in SWEEP_N}
    every = list(by.values())
    base = max(ARMS, key=lambda a: float(np.median([v[(a, best_n[a])] for v in every]))) if every else ""
    gap = {a: [round(float(np.percentile([v[(a, best_n[a])] - v[(base, best_n[base])] for v in every], q)), 2)
               for q in (10, 50, 90)] for a in ARMS} if every else {}
    return {"cells": med, "best_n": best_n, "wins_oos": wins, "odd_members": len(order) - half, "win_at_n": atn,
            "leader": base, "gap_to_leader": gap}


def spearman(x, y):
    rx, ry = [np.argsort(np.argsort(v)).astype(float) for v in (x, y)]
    return float(np.corrcoef(rx, ry)[0, 1]) if rx.std() and ry.std() else 0.0


def cmd_tornado(a):
    """which parameters still drive the margin of each rival over v3.4, at each arm's cross-fitted N. Rank correlation
    over members; theta is the member's, the rest are redrawn from the member's uid as the sweep drew them."""
    res = {}
    for phase, sc in ((p, s) for p in ("prior", "post") for s in ("pull_unattended", "pull_present")):
        by = table(phase, sc)
        summ = summarize(phase, sc)
        if not summ["best_n"]:
            continue
        cells = {m: v for m, v in by.items() if all((x, n) in v for x in ARMS for n in SWEEP_N)}
        ms = {m["member"]: m for m in R.members("pull", 240)}
        mem = sorted(cells)
        par = collections.defaultdict(list)
        for m in mem:
            rp, tp, fo = draws(m, phase)
            for pre, d in (("th_", ms[m]["theta"]), ("fo_", fo), ("rp_", rp), ("tp_", tp)):
                for k, v in d.items():
                    if pre + k != "th_kappa":    # the pool's fo_kappa replaces it
                        par[pre + k].append(float(v))
        for rival in a.rivals.split(","):
            bn = summ["best_n"]
            mar = [cells[m][(rival, bn[rival])] - cells[m][("v3.4", bn["v3.4"])] for m in mem]
            rho = {k: spearman(np.array(v), np.array(mar)) for k, v in par.items() if np.ptp(v) > 0}
            top = sorted(rho.items(), key=lambda kv: -abs(kv[1]))[:8]
            res[f"{phase}/{sc}/{rival}"] = {"n": len(mem), "bestN": [bn[rival], bn["v3.4"]],
                                            "median_margin": round(float(np.median(mar)), 2),
                                            "top": [(k, round(r, 2)) for k, r in top]}
    print(json.dumps(res, indent=0))


def cmd_hold(a):
    """the relentless run predicted without it: arm A at N, unattended, blind check on every overlapping ticket"""
    rows = [r for r in load_rows("hold", "pull_unattended") if r["arm"] == "A"]
    out = {}
    by = collections.defaultdict(dict)
    for r in rows:
        by[r["member"]][r["n"]] = r["row"]
    for n in sorted({r["n"] for r in rows}):
        x = [v[n] for v in by.values() if n in v]
        q = lambda f: [round(float(np.percentile([f(y) for y in x], p)), 2) for p in (10, 50, 90)]
        out[n] = {"done_per_h": q(lambda y: y["done_d"] / 24), "sound_per_h": q(lambda y: y["sound_prod_d"] / 24),
                  "busy": q(lambda y: y["mean_busy"]), "checks_d": q(lambda y: y["fo_checks"] / 7),
                  "check_fail_share": q(lambda y: y["fo_check_fail"] / max(1, y["fo_checks"]))}
    el = []
    for v in by.values():
        if 2 in v and 4 in v and min(v[2]["done_d"], v[4]["done_d"], v[2]["mean_busy"], v[4]["mean_busy"]) > 0:
            dw = math.log(v[4]["mean_busy"] / v[2]["mean_busy"])
            if abs(dw) > 1e-6:                     # a member whose occupancy did not move has no elasticity
                el.append(math.log(v[4]["done_d"] / v[2]["done_d"]) / dw)
    out["elast_cap2to4"] = [round(float(np.percentile(el, p)), 2) for p in (10, 50, 90)]
    print(json.dumps(out, indent=0))


def cmd_flip(a):
    """model error the boxes do not cover: the census elasticity sits below the sim's. Cut the output of the v arms above
    N=2 by 2^-d, leaving Ralph and TP alone, and find the smallest d at which v3.4 loses the median lead."""
    out = {}
    for sc in ("pull_unattended", "pull_present"):
        by = table("post", sc)
        best = {x: max(float(np.median([v[(x, n)] for v in by.values() if (x, n) in v])) for n in SWEEP_N) for x in ARMS}
        rival = max((x for x in ARMS if x not in ("v2", "v3.0", "v3.4")), key=best.get)
        med = {(x, n): float(np.median([v[(x, n)] for v in by.values() if (x, n) in v])) for x in ("v2", "v3.0", "v3.4")
               for n in SWEEP_N}
        lead = max(med.values())
        cut = lambda d: max(m * 2 ** (-d * max(0.0, math.log2(n / 2))) for (x, n), m in med.items())
        d = next((i / 100 for i in range(301) if cut(i / 100) <= best[rival]), None)     # None: N<=2 alone still leads
        out[sc] = {"lead": round(lead, 1), "rival": rival, "rival_median": round(best[rival], 1), "flip_d": d}
    print(json.dumps(out))


def cmd_margins(a):
    """cross-arm facts the census can falsify: ITE per done and wall per done against the paired arena numbers,
    realised concurrency, and elasticity of output on realised workers"""
    out = {}
    for sc in ("pull_present", "pull_unattended"):
        rows = collections.defaultdict(dict)
        for r in load_rows("post", sc):
            rows[r["member"]][(r["arm"], r["n"])] = r["row"]
        for n in SWEEP_N:
            q = [v[("A", n)]["ite_week"] / max(1, v[("A", n)]["done_d"]) / (v[("v3.4", n)]["ite_week"] / max(1, v[("v3.4", n)]["done_d"]))
                 for v in rows.values() if ("A", n) in v and ("v3.4", n) in v and v[("v3.4", n)]["done_d"] > 0]
            out[f"{sc}|ITE_per_done_A_over_v34|N{n}"] = [round(float(np.percentile(q, p)), 2) for p in (10, 50, 90)]
        for arm in ("v3.4", "A", "TP+", "AB_build"):
            for n in SWEEP_N:
                x = [v[(arm, n)]["mean_busy"] for v in rows.values() if (arm, n) in v]
                out[f"{sc}|busy|{arm}|N{n}"] = [round(float(np.percentile(x, p)), 2) for p in (10, 50, 90)]
            for n1, n2 in ((1, 2), (2, 4), (4, 8)):
                e = [math.log(v[(arm, n2)]["done_d"] / v[(arm, n1)]["done_d"]) / math.log(v[(arm, n2)]["mean_busy"] / v[(arm, n1)]["mean_busy"])
                     for v in rows.values() if (arm, n1) in v and (arm, n2) in v and v[(arm, n1)]["done_d"] > 0
                     and v[(arm, n2)]["done_d"] > 0 and abs(math.log(v[(arm, n2)]["mean_busy"] / v[(arm, n1)]["mean_busy"])) > .05]
                out[f"{sc}|elast|{arm}|{n1}to{n2}"] = [round(float(np.percentile(e, p)), 2) for p in (10, 50, 90)] if e else []
    print(json.dumps(out, indent=0))


def cmd_report(a):
    out = {f"{p}/{s}": summarize(p, s) for p in PHASES for s in SCENARIOS if load_rows(p, s)}
    if a.json:
        json.dump(out, open(a.json, "w"), indent=1)
    for k, v in out.items():
        print(k, "odd members", v["odd_members"], "wins", v["wins_oos"], "best N", v["best_n"], "gap", v["gap_to_leader"])
        for arm in ARMS:
            print("  %-9s" % arm, "  ".join("%d:%s" % (n, v["cells"].get(f"{arm}|{n}", ["-"] * 3)[:3]) for n in SWEEP_N))


FP = fingerprint()


def main(argv=None):
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("sweep")
    p.add_argument("--phase", choices=PHASES, default="prior")
    p.add_argument("--scenario", choices=SCENARIOS, default="pull_present")
    p.add_argument("--members", type=int, default=40)
    p.add_argument("--reps", type=int, default=1)
    p.add_argument("--procs", type=int, default=4)
    p.add_argument("--budget-s", type=float, default=500)
    p.add_argument("--ns", default="1,2,4,8")
    p.add_argument("--arms", default="")
    p = sub.add_parser("report")
    p.add_argument("--json", default="")
    p = sub.add_parser("one")
    p.add_argument("--arm", default="A")
    p.add_argument("--n", type=int, default=2)
    p.add_argument("--phase", default="prior")
    p.add_argument("--scenario", default="pull_present")
    p = sub.add_parser("tornado")
    p.add_argument("--rivals", default="A,AB_build,TP+")
    sub.add_parser("hold")
    sub.add_parser("margins")
    sub.add_parser("flip")
    a = ap.parse_args(argv)
    {"sweep": cmd_sweep, "report": cmd_report, "one": cmd_one, "tornado": cmd_tornado, "hold": cmd_hold,
     "margins": cmd_margins, "flip": cmd_flip}[a.cmd](a)


if __name__ == "__main__":
    main()
