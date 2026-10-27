#!/usr/bin/env python3
"""rimflow_v3_sim.py: a factory in a bottle. A discrete-event simulation of the RimFlow PROCESS (not the game, not
the mods): tickets with hidden true quality, two builder windows with helpers, the Dispatcher, the v3 roles, the owner
as a scarce attention server, the test rig, and three weekly token budgets. Item RIMFLOW_SIM_BUILD_FACTORY_IN_A_BOTTLE;
design rounds with GPT under D:\\ClaudeWork\\rimmandrake\\rimflow_sim\\gpt_round*.md; findings
design/RimMandrake/rimflow_v3_sim_findings_2026-10-27.md.

Honesty rules built in:
  * Every parameter in rimflow_v3_sim_params.json is CALIBRATED, CONFIG, DERIVED or ASSUMED. ASSUMED ones are prior
    ranges. `calibrate` draws parameter sets from the priors, runs each as today's v2, and keeps the sets whose output
    lands inside every target tolerance (ABC rejection). The kept ensemble is "baseline-summary-calibrated, conditional
    on the priors and the model structure"; it is NOT a validated predictor.
  * Experiments run over the kept ensemble with paired randomness and report the share of members in which a policy
    wins, plus which assumed parameters split the outcome. A role's BENEFIT is always an assumed scenario multiplier
    whose range includes no effect and harm.
  * Token quotas are DERIVED from each member's own v2 burn, so token results are relative to today's burn.

Randomness: every draw is u01(seed, field, lineage...) (splitmix64), keyed by the identity of the thing it decides
(ticket lineage, hour, seat stall number), so two policies on one seed see the same outside world (GPT r2 #11).

    rimflow_v3_sim.py calibrate --n 400 --start 0 [--out DIR]     ABC draws (chunk with --start for <5 min calls)
    rimflow_v3_sim.py validate [--seeds 3]                          re-run kept members on fresh seeds vs targets
    rimflow_v3_sim.py experiment NAME [--members N] [--start i]     NAME in EXPERIMENTS
    rimflow_v3_sim.py report                                        aggregate everything to results.json + report.md
    rimflow_v3_sim.py one --policy v3.0 [--seed 1]                  one run of the median member, metrics printed
Stdlib + numpy only. Offline; reads only the params file (and, for `calibrate --extract`, nothing else).
"""
import argparse
import collections
import heapq
import json
import math
import os
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
PARAMS = os.path.join(HERE, "rimflow_v3_sim_params.json")
OUT = os.environ.get("RM_RIMFLOW_SIM_OUT", "/mnt/d/ClaudeWork/rimmandrake/rimflow_sim")

HOUR, DAY = 3600, 86400
WEEK = 7 * DAY
WEEK_START_LOCAL_H = 13          # the week starts at the Wed 13:00 reset
ACCOUNTS = ("lukas", "steven", "system")
SEATS = ("FOUNDRY", "BENCH")
ROLE_ORDER = ("Conductor", "Operations", "Producer", "Arbiter", "Auditor", "Innovator")

# ---------------------------------------------------------------- keyed randomness
M64 = (1 << 64) - 1


def _sm(z):
    z = (z + 0x9E3779B97F4A7C15) & M64
    z = ((z ^ (z >> 30)) * 0xBF58476D1CE4E5B9) & M64
    z = ((z ^ (z >> 27)) * 0x94D049BB133111EB) & M64
    return z ^ (z >> 31)


def mix(*xs):
    h = 0x243F6A8885A308D3
    for x in xs:
        h = _sm(h ^ (int(x) & M64))
    return h


def u01(*xs):
    return (mix(*xs) >> 11) * (1.0 / (1 << 53))


def poisson(lam, *key):
    if lam <= 0:
        return 0
    u = u01(*key)
    k, p = 0, math.exp(-lam)
    c = p
    while u > c and k < 200:
        k += 1
        p *= lam / k
        c += p
    return k


def expo(mean, *key):
    return -math.log(1.0 - u01(*key)) * mean


def qsample(table, u):
    x = u * (len(table) - 1)
    i = min(int(x), len(table) - 2)
    return table[i] + (table[i + 1] - table[i]) * (x - i)


# field tags (any distinct ints)
(F_PRES, F_EXT, F_EXTN, F_CLS, F_ROUTE, F_PARK, F_CARD, F_QUICK, F_NHELP, F_HELP, F_DEF, F_BLIND, F_SELF, F_VER,
 F_VFAIL, F_FIX, F_DISC, F_LINK, F_CHILD, F_CHILDCLS, F_STALL, F_NOTICE, F_WATCH, F_SELFRES, F_RING, F_UNWORK, F_PING,
 F_OWNSERV, F_ARB, F_ARBFR, F_AUD, F_AUDS, F_RULE, F_THETA, F_INIT, F_ROLETIX) = range(1, 37)


# ---------------------------------------------------------------- parameters
def load_params(path=PARAMS):
    with open(path) as fh:
        return json.load(fh)


def draw_theta(P, seed, member, box=None):
    """One parameter set, uniform over the ASSUMED prior box (or a narrowed proposal box inside it), keyed by member.
    The priors are uniform, so rejection inside a sub-box samples the ABC posterior TRUNCATED to that box."""
    th = {}
    for i, (k, pr) in enumerate(sorted(P["priors"].items())):
        lo, hi = (box[k] if box and k in box else (pr["lo"], pr["hi"]))
        v = lo + (hi - lo) * u01(seed, F_THETA, member, i)
        th[k] = int(round(v)) if pr.get("int") else v
    return th


def policy_cfg(P, name, **over):
    base = dict(P["policies"]["_defaults"])
    if name in P["policies"]:
        base.update(P["policies"][name])
    else:
        raise KeyError(name)
    base["name"] = name
    base.update(over)
    return base


# ---------------------------------------------------------------- the model
class Ticket:
    __slots__ = ("key", "cls", "seat", "t_filed", "attempt", "defects", "pending", "accepted", "closed_t", "origin",
                 "quick", "nh")

    def __init__(self, key, cls, t, origin):
        self.key, self.cls, self.t_filed, self.origin = key, cls, t, origin
        self.seat = None
        self.attempt = 0
        self.defects = []          # each: [state, blind]  state 0 latent, 1 found/fixed
        self.pending = 0
        self.accepted = False
        self.closed_t = None
        self.quick = False
        self.nh = 1


class Seat:
    def __init__(self, name, cap):
        self.name = name
        self.cap = cap
        self.q_hi = collections.deque()      # repairs
        self.q_prod = collections.deque()
        self.q_proc = collections.deque()
        self.running = 0
        self.serial_busy = False
        self.stalled = False
        self.stall_n = 0
        self.stall_t = 0
        self.notice_sched = False
        self.blocked = False
        self.idle_since = None
        self.completions = 0
        self.launch_q = collections.deque()  # (ticket, helper index) waiting for a cap slot
        self.ring_fail = 0
        self.cooldown_until = 0
        self.rings = collections.deque()      # ring times (caps)

    def qlen(self):
        return len(self.q_hi) + len(self.q_prod) + len(self.q_proc) + len(self.launch_q)


class Sim:
    def __init__(self, P, theta, policy, seed, weeks=2, quotas=None, warm_weeks=0, rollout=None):
        self.P, self.th, self.pol, self.seed, self.weeks = P, theta, policy, seed, weeks
        self.fx = P["fixed"]
        self.quotas = quotas
        self.warm = warm_weeks             # policy switches on after the warm weeks (v2 before)
        self.rollout = rollout             # list of (day, role) activations, days counted from policy start
        self.T_end = weeks * WEEK
        self.ev = []
        self.seq = 0
        cap = policy.get("helper_cap") or theta["helper_cap_v2"]
        self.base_cap = int(theta["helper_cap_v2"])
        self.seats = {s: Seat(s, self.base_cap) for s in SEATS}
        self.pol_cap = int(cap)
        self.roles_on = {}                   # role -> activation time
        self.paused = set()
        self.throttle_k = 0
        self.throttle_last = -10 ** 9
        self.dispatcher_on = False
        self.mu_mult = 1.0
        self.rules = 0
        self.owner_q = collections.deque()
        self.parked = {n: collections.deque() for n in SEATS}   # only filled under STRUCTURE == "pull"
        self.arb_q = collections.deque()
        self.arb_busy = 0
        self.used = {a: 0.0 for a in ACCOUNTS}
        self.exhausted_at = {a: None for a in ACCOUNTS}
        self.all_blocked = False
        self.blocked_since = None
        self.hour_ite = collections.deque(maxlen=12)
        self.cur_hour_ite = 0.0
        self.recent_closed = collections.deque()   # (t, ticket) for the Auditor
        self.rings_day = collections.deque()
        self.snap128 = None
        wl = theta["acct_w_lukas"]
        self.w = {"lukas": wl, "steven": (1 - wl) / 2, "system": (1 - wl) / 2}
        pres = self.fx["owner_present_p_by_hour"]["value"]
        nh = weeks * 7 * 24
        self.present = [u01(seed, F_PRES, h) < min(1.0, pres[(h + WEEK_START_LOCAL_H) % 24] * theta["owner_presence_mult"])
                        for h in range(nh + 48)]
        self.m = [collections.defaultdict(float) for _ in range(weeks)]
        self.lists = [collections.defaultdict(list) for _ in range(weeks)]

    # ---- bookkeeping
    def wk(self, t):
        return min(int(t // WEEK), self.weeks - 1)

    def add(self, t, key, v=1.0):
        self.m[self.wk(t)][key] += v

    def push(self, t, kind, *payload):
        self.seq += 1
        heapq.heappush(self.ev, (t, self.seq, kind, payload))

    def is_present(self, t):
        return self.present[int(t // HOUR)]

    def role(self, r, t):
        """role active at t and not paused by the token throttle"""
        return r in self.roles_on and self.roles_on[r] <= t and r not in self.paused

    def charge(self, t, ite, what):
        if ite <= 0:
            return
        self.add(t, "ite", ite)
        self.add(t, "ite_" + what, ite)
        self.cur_hour_ite += ite
        live = [a for a in ACCOUNTS if self.quotas is None or self.used[a] < self.quotas[a]]
        if not live:
            live = list(ACCOUNTS)
        tot = sum(self.w[a] for a in live)
        for a in live:
            self.used[a] += ite * self.w[a] / tot
            if self.quotas is not None and self.exhausted_at[a] is None and self.used[a] >= self.quotas[a]:
                self.exhausted_at[a] = t
        if self.quotas is not None and not self.all_blocked and all(self.exhausted_at[a] is not None for a in ACCOUNTS):
            self.all_blocked = True
            self.blocked_since = t
            self.add(t, "all_exhausted_events")
            for s in self.seats.values():
                self.set_idle(s, t)

    # ---- idle-with-work accounting (time integral per seat)
    def set_idle(self, s, t):
        if s.idle_since is not None:
            self.add(s.idle_since, "idle_min_" + s.name, (t - s.idle_since) / 60.0)
            s.idle_since = None
        if (s.stalled or self.all_blocked) and s.qlen() > 0:
            s.idle_since = t

    # ---- tickets
    def file_ticket(self, t, key, cls, origin, linked=False):
        tk = Ticket(key, cls, t, origin)
        self.add(t, "filed")
        self.add(t, "filed_" + cls)
        if linked:
            self.add(t, "rework_filed")
        if origin in ("owner", "agent") and u01(self.seed, F_CARD, key) < self.th["p_owner_card"]:
            self.owner_q.append((t, tk, False, tk.key))
            return
        if origin in ("owner", "agent") and u01(self.seed, F_PARK, key) < self.th["p_park"]:
            self.add(t, "parked")
            if STRUCTURE == "pull":
                tk.seat = "FOUNDRY" if u01(self.seed, F_ROUTE, tk.key) < self.fx["foundry_share"]["value"] else "BENCH"
                tk.quick = u01(self.seed, F_QUICK, tk.key) < self.th["p_quick"]
                self.parked[tk.seat].append(tk)
            return
        self.enqueue(t, tk)

    def enqueue(self, t, tk, front=False):
        if tk.seat is None:
            tk.seat = "FOUNDRY" if u01(self.seed, F_ROUTE, tk.key) < self.fx["foundry_share"]["value"] else "BENCH"
            tk.quick = tk.cls != "rework" and u01(self.seed, F_QUICK, tk.key) < self.th["p_quick"]
        s = self.seats[tk.seat]
        if front:
            s.q_hi.append(tk)
        elif tk.cls == "process":
            s.q_proc.append(tk)
        else:
            s.q_prod.append(tk)
        if s.stalled:
            self.set_idle(s, t)
            if tk.origin == "owner" and self.is_present(t):
                self.resume(s, t, "owner_work")      # he typed the work into this window: not a nudge
            else:
                self.schedule_notice(s, t)
        else:
            self.try_work(s, t)

    def pop(self, s, t):
        if s.q_hi:
            return s.q_hi.popleft()
        if self.role("Producer", t):
            for q in (s.q_prod, s.q_proc):
                if q:
                    return q.popleft()
        if s.q_prod and s.q_proc:
            return (s.q_prod if s.q_prod[0].t_filed <= s.q_proc[0].t_filed else s.q_proc).popleft()
        if s.q_prod:
            return s.q_prod.popleft()
        if s.q_proc:
            return s.q_proc.popleft()
        return None

    # ---- the builder windows
    def cap(self, s, t):
        c = self.pol_cap if t >= self.warm * WEEK else self.base_cap
        if self.pol.get("throttle") == "helpers_first" and self.throttle_k > 0:
            c = 1
        return c

    def try_work(self, s, t):
        if s.stalled or s.serial_busy or self.all_blocked:
            return
        if s.launch_q and s.running < self.cap(s, t):
            tk, i = s.launch_q.popleft()
            s.serial_busy = True
            self.push(t + self.th["dispatch_min"] * 60, "launch", s.name, tk, i)
            return
        if s.launch_q:
            return                                    # waiting for a cap slot; a helper completion re-calls
        tk = self.pop(s, t)
        if tk is None and self.parked[s.name]:
            tk = self.parked[s.name].popleft()
            self.add(t, "pulled_from_backlog")
        if tk is None:
            if s.running == 0:
                self.stall(s, t, empty=True)
            return
        if tk.quick and tk.attempt == 0:
            s.serial_busy = True
            self.push(t + self.th["quick_min"] * 60, "quick_done", s.name, tk)
            return
        tk.nh = 1 + poisson(max(0.0, self.th["helpers_per_job"] - 1), self.seed, F_NHELP, tk.key, tk.attempt)
        tk.pending = tk.nh
        for i in range(tk.nh):
            s.launch_q.append((tk, i))
        self.try_work(s, t)

    def launch(self, t, s, tk, i):
        s.serial_busy = False
        u = u01(self.seed, F_HELP, tk.key, tk.attempt, i)
        ite = qsample(self.fx["helper_ite_q"][s.name], u)
        dur = qsample(self.fx["helper_dur_q"][s.name], u)
        if self.role("Operations", t):
            ite *= self.th["m_ops_waste"]
        self.charge(t, ite, "helpers")
        self.add(t, "helpers")
        s.running += 1
        self.push(t + dur, "helper_done", s.name, tk, s.running)
        self.try_work(s, t)

    def after_completion(self, s, t):
        s.completions += 1
        if s.running == 0 and not s.serial_busy and not s.launch_q:
            p = self.th["p_stall"] * (self.th["m_ops_stall"] if self.role("Operations", t) else 1.0)
            if u01(self.seed, F_STALL, SEATS.index(s.name), s.completions) < p:
                self.stall(s, t)
                return
        self.try_work(s, t)

    def stall(self, s, t, empty=False):
        if s.stalled:
            return
        s.stalled = True
        s.stall_n += 1
        s.stall_t = t
        s.notice_sched = False
        s.ring_fail = 0
        self.add(t, "stalls_" + s.name)
        self.push(t + expo(HOUR / max(self.th["r_self_h"], 1e-6), self.seed, F_SELFRES, SEATS.index(s.name), s.stall_n),
                  "resume", s.name, s.stall_n, "self")
        if s.qlen() > 0:
            self.schedule_notice(s, t)
        self.set_idle(s, t)

    def schedule_notice(self, s, t):
        """the owner notices a stalled window that has work, once he is present and watching it"""
        if s.notice_sched or not s.stalled or s.qlen() == 0:
            return
        s.notice_sched = True
        si = SEATS.index(s.name)
        tt, j = t, 0
        while tt < self.T_end + DAY and j < 400:
            h = int(tt // HOUR)
            if self.present[h] and u01(self.seed, F_WATCH, si, s.stall_n, h) < self.th["p_watch"]:
                cand = tt + expo(self.th["notice_min"] * 60, self.seed, F_NOTICE, si, s.stall_n, j)
                if int(cand // HOUR) == h or self.present[min(int(cand // HOUR), len(self.present) - 1)]:
                    self.push(cand, "resume", s.name, s.stall_n, "owner")
                    return
            tt = (h + 1) * HOUR
            j += 1

    def resume(self, s, t, cause):
        if not s.stalled:
            return
        s.stalled = False
        self.add(t, "resume_" + cause)
        if cause == "owner":
            self.add(t, "nudges")
            self.add(t, "owner_att_min", 1.0)
            self.conductor_msg(t)
        self.set_idle(s, t)
        self.try_work(s, t)

    def conductor_msg(self, t):
        if self.role("Conductor", t):
            self.charge(t, self.th["cond_ite_msg"], "conductor")

    # ---- finishing work
    def complete(self, t, s, tk):
        th = self.th
        mu = th["mu_proc"] if tk.cls == "process" else th["mu_prod"] * self.mu_mult
        if tk.attempt > 0:
            mu *= 0.3                                  # a repair can regress
        mu *= 1.0 + th["kappa"] * max(0, min(s.running, self.cap(s, t)) - 1 + (tk.nh - 1))
        n = poisson(mu, self.seed, F_DEF, tk.key, tk.attempt)
        for j in range(n):
            tk.defects.append([0, u01(self.seed, F_BLIND, tk.key, tk.attempt, j) < th["b_shared"]])
        for j, d in enumerate(tk.defects):
            if d[0] == 0 and not d[1] and u01(self.seed, F_SELF, tk.key, tk.attempt, j) < th["s_self"]:
                d[0] = 1
        if u01(self.seed, F_VER, tk.key, tk.attempt) < self.fx["p_verify"]["value"]:
            self.add(t, "verify_n")
            hit = [d for j, d in enumerate(tk.defects)
                   if d[0] == 0 and not d[1] and u01(self.seed, F_VFAIL, tk.key, tk.attempt, j) < th["s_rig"]]
            if hit or u01(self.seed, F_VFAIL, tk.key, tk.attempt, 99) < th["fr_rig"]:
                self.add(t, "verify_fail")
                self.repair(t, tk, hit)
                return
        if tk.cls != "process" and self.role_present("Arbiter", t):
            self.arb_q.append((t, tk))
            self.add(t, "arb_in")
            self.arb_start(t)
            return
        self.close(t, tk)

    def role_present(self, r, t):
        return r in self.roles_on and self.roles_on[r] <= t

    def repair(self, t, tk, hit):
        for j, d in enumerate(hit):
            if u01(self.seed, F_FIX, tk.key, tk.attempt, j) < self.th["p_fix"]:
                d[0] = 1
        tk.attempt += 1
        self.add(t, "repairs")
        self.enqueue(t, tk, front=True)

    def close(self, t, tk):
        th = self.th
        tk.closed_t = t
        self.add(t, "done")
        self.add(t, "done_" + tk.cls)
        self.lists[self.wk(t)]["lead_d"].append((t - tk.t_filed) / DAY)
        latent = [d for d in tk.defects if d[0] == 0]
        if tk.cls != "process" and not latent:
            self.add(t, "sound_prod")
        if tk.cls != "process" and tk.accepted:
            self.add(t, "accepted_prod")
        self.charge(t, self.fx["seat_ite_per_close"]["value"], "seat")
        self.add(t, "commits", th["commits_ledger"])
        self.add(t, "commits_proc", th["commits_ledger"])
        if tk.cls == "process":
            self.add(t, "commits", th["commits_proc"])
            self.add(t, "commits_proc", th["commits_proc"])
        else:
            self.add(t, "commits", th["commits_prod"])
        for j, d in enumerate(tk.defects):
            if d[0] == 0:
                self.push(t + expo(DAY / th["e_disc"], self.seed, F_DISC, tk.key, j), "disc", tk, j)
        if tk.cls != "process":
            self.recent_closed.append((t, tk))
        f = th["f_proc"] if tk.cls == "process" else th["f_prod"]
        if tk.cls == "process" and self.role("Producer", t):
            f *= th["m_prod_f"]
        for i in range(poisson(f, self.seed, F_CHILD, tk.key)):
            ck = mix(tk.key, F_CHILD, i)
            cls = "process" if u01(self.seed, F_CHILDCLS, ck) < th["p_proc_child"] else "product"
            self.file_ticket(t, ck, cls, "agent")

    def disc(self, t, tk, j):
        d = tk.defects[j]
        if d[0] != 0:
            return
        d[0] = 1
        self.add(t, "escapes")
        if tk.accepted:
            self.add(t, "escapes_post_accept")
        self.add(t, "escape_age_d", (t - tk.closed_t) / DAY)
        self.file_ticket(t, mix(tk.key, F_DISC, j), "rework", "discovery",
                         linked=u01(self.seed, F_LINK, tk.key, j) < self.th["p_link"])

    # ---- Arbiter on the rig
    def arb_start(self, t):
        n_rig = self.fx["n_rig"]["value"]
        while self.arb_busy < n_rig and self.arb_q:
            t0, tk = self.arb_q.popleft()
            self.arb_busy += 1
            self.charge(t, self.th["arb_ite"], "arbiter")
            dur = (self.th["arb_check_min"] + self.th["rule_check_min"] * self.rules) * 60
            self.add(t, "rig_min", dur / 60)
            self.push(t + dur, "arb_done", tk, len(self.arb_q))

    def arb_done(self, t, tk, qlen):
        th = self.th
        self.arb_busy -= 1
        sig = self.pol.get("arb_strict", 0.6)
        sens = th["arb_s_lo"] + (th["arb_s_hi"] - th["arb_s_lo"]) * sig
        if qlen > th["arb_batch_q"] or "Arbiter" in self.paused:
            sens *= th["arb_batch_gamma"]
            self.add(t, "arb_batched")
        if t - self.roles_on["Arbiter"] < WEEK:
            sens *= th["teeth"]
        hit = [d for j, d in enumerate(tk.defects)
               if d[0] == 0 and not d[1] and u01(self.seed, F_ARB, tk.key, tk.attempt, j) < sens]
        fr = u01(self.seed, F_ARBFR, tk.key, tk.attempt) < th["arb_fr_max"] * sig * sig
        self.add(t, "arb_verdicts")
        if hit or fr:
            self.add(t, "arb_reject")
            if fr and not hit:
                self.add(t, "arb_false_reject")
            self.repair(t, tk, hit)
        else:
            tk.accepted = True
            if any(d[0] == 0 for d in tk.defects):
                self.add(t, "arb_pass_defective")
            self.close(t, tk)
        self.arb_start(t)

    # ---- periodic
    def hour(self, t):
        th = self.th
        h = int(t // HOUR)
        present = self.present[h]
        self.hour_ite.append(self.cur_hour_ite)
        self.cur_hour_ite = 0.0
        self.charge(t, self.fx["background_ite_week"]["value"] / (7 * 24), "background")
        if present:
            self.add(t, "present_h")
            n = poisson(th["lam_ext_h"], self.seed, F_EXT, h)
            for i in range(n):
                k = mix(self.seed, F_EXTN, h, i)
                cls = "product" if u01(self.seed, F_CLS, k) < th["p_prod_ext"] else "process"
                self.add(t, "owner_att_min", 2.0)
                self.conductor_msg(t)
                self.file_ticket(t + i * 60, k, cls, "owner")
            lam = th["lam_status_h"] * (th["m_cond"] if self.role("Conductor", t) else 1.0)
            pings = poisson(lam, self.seed, F_PING, h)
            if pings:
                self.add(t, "nudges", pings)
                self.add(t, "pings", pings)
                self.add(t, "owner_att_min", pings)
                for _ in range(pings):
                    self.conductor_msg(t)
            keep = collections.deque()
            for item in self.owner_q:
                if u01(self.seed, F_OWNSERV, h, item[3]) >= th["q_card"]:
                    keep.append(item)
                    continue
                t0, tk, is_role, _ = item
                self.add(t, "cards_done")
                self.add(t, "owner_att_min", 3.0)
                self.lists[self.wk(t)]["resolve_d"].append((t - t0) / DAY)
                if not is_role:
                    tk.cls = "product"
                    self.enqueue(t, tk)
            self.owner_q = keep
        self.add(t, "cards_waiting_3d_h", sum(1 for x in self.owner_q if t - x[0] > 3 * DAY))
        self.throttle(t)
        if t >= self.warm * WEEK and self.pol.get("dispatcher") and not self.dispatcher_on:
            self.dispatcher_on = True
            self.push(t, "ring_tick")
        self.push(t + HOUR, "hour")

    def throttle(self, t):
        if self.quotas is None or self.pol.get("throttle") == "none":
            return
        rem = sum(max(0.0, self.quotas[a] - self.used[a]) for a in ACCOUNTS)
        burn = sum(self.hour_ite) / max(1, len(self.hour_ite))
        left_h = max(1.0, (WEEK - (t % WEEK)) / HOUR)
        R = rem / max(1.0, burn * left_h)
        self.add(t, "runway_h_below1", 1.0 if R < 1 else 0.0)
        order = self.P["fixed"]["throttle_order"]["value"]
        if self.pol.get("throttle") == "reverse":
            order = list(reversed(order))
        if t - self.throttle_last >= 6 * HOUR:
            if R < 1.0 and self.throttle_k < len(order) + 1:
                self.throttle_k += 1
                self.throttle_last = t
            elif R > 1.15 and self.throttle_k > 0:
                self.throttle_k -= 1
                self.throttle_last = t
        k = self.throttle_k - (1 if self.pol.get("throttle") == "helpers_first" else 0)
        self.paused = set(order[:max(0, k)])
        self.add(t, "throttle_steps_h", self.throttle_k)

    def day(self, t):
        th = self.th
        if self.role("Operations", t):
            self.charge(t, 2 * 60000 + 150000, "operations")
            self.add(t, "commits", 1)
            self.add(t, "commits_proc", 1)
        if self.role("Producer", t):
            self.charge(t, th["prod_ite_day"], "producer")
            self.add(t, "commits", 1)
            self.add(t, "commits_proc", 1)
        if self.role("Auditor", t):
            rate = self.pol.get("aud_rate", 0.1)
            cand = [tk for (tc, tk) in self.recent_closed if t - tc <= DAY]
            n = 0
            for tk in cand:
                if n >= self.pol.get("aud_max", self.fx["auditor_max_per_day"]["value"]):
                    self.add(t, "aud_overflow")
                    continue
                if u01(self.seed, F_AUDS, tk.key) >= rate:
                    continue
                n += 1
                self.charge(t, th["aud_ite"], "auditor")
                self.add(t, "audits")
                for j, d in enumerate(tk.defects):
                    if d[0] == 0 and not d[1] and u01(self.seed, F_AUD, tk.key, j) < th["s_aud"]:
                        d[0] = 1
                        self.add(t, "audit_found")
                        self.file_ticket(t, mix(tk.key, F_AUD, j), "rework", "audit")
                        if u01(self.seed, F_RULE, tk.key, j) < th["p_rule"]:
                            self.rules += 1
                            self.mu_mult *= (1 - th["rule_delta"])
        while self.recent_closed and t - self.recent_closed[0][0] > DAY:
            self.recent_closed.popleft()
        if self.role("Innovator", t) and int(t // DAY) % 7 == 0:
            self.charge(t, th["innov_ite_week"], "innovator")
            self.mu_mult *= th["m_innov"]
            for i in range(3):
                self.file_ticket(t, mix(self.seed, F_ROLETIX, 999, int(t // DAY), i), "process", "role")
        for r, t_on in self.roles_on.items():
            if t_on <= t < t_on + WEEK:
                n = poisson(th["role_cards_day"], self.seed, F_ROLETIX, ROLE_ORDER.index(r), int(t // DAY))
                for i in range(n):
                    self.owner_q.append((t, None, True, mix(F_ROLETIX, ROLE_ORDER.index(r), int(t // DAY), i)))
        self.push(t + DAY, "day")

    def activate(self, t, r):
        if r in self.roles_on:
            return
        self.roles_on[r] = t
        for i in range(int(self.th["role_build_tix"])):
            self.file_ticket(t + i, mix(self.seed, F_ROLETIX, ROLE_ORDER.index(r), i), "process", "role")

    def ring_tick(self, t):
        cfg = dict(self.fx["dispatcher"])
        if self.pol.get("wake_caps"):
            cfg.update(self.pol["wake_caps"])
        while self.rings_day and t - self.rings_day[0] > DAY:
            self.rings_day.popleft()
        for name in cfg["wake_seats"]:
            s = self.seats[name]
            while s.rings and t - s.rings[0] > DAY:
                s.rings.popleft()
            if not s.stalled or s.qlen() == 0 or self.all_blocked or t < s.cooldown_until:
                continue
            if t - s.stall_t < cfg["stall_after_s"]:
                continue
            last_h = sum(1 for x in s.rings if t - x <= HOUR)
            if last_h >= cfg["wakes_per_seat_hour"] or len(s.rings) >= cfg["wakes_per_seat_day"] \
                    or len(self.rings_day) >= cfg["wakes_per_day"]:
                self.add(t, "ring_capped")
                continue
            s.rings.append(t)
            self.rings_day.append(t)
            n = len(s.rings) + int(t // DAY) * 1000
            self.add(t, "rings")
            if u01(self.seed, F_RING, n) >= self.th["p_ring_ok"]:
                s.ring_fail += 1
            else:
                self.charge(t, self.th["c_wake_ite"], "wakes")
                if u01(self.seed, F_UNWORK, n) < self.th["p_unwork"]:
                    self.add(t, "woke_no_handoff")
                    s.ring_fail += 1
                    s.stall_t = t
                else:
                    self.add(t, "ring_ok")
                    self.resume(s, t, "ring")
                    continue
            if s.ring_fail > cfg["max_retries"]:
                s.cooldown_until = t + cfg["cooldown_s"]
                s.ring_fail = 0
                self.add(t, "ring_cooldowns")
        self.push(t + cfg["tick_s"], "ring_tick")

    def week_reset(self, t):
        w = int(t // WEEK) - 1
        if 0 <= w < self.weeks:
            # end-of-week stocks: a policy can look better by deferring closes past the window
            self.m[w]["arb_q_end"] = len(self.arb_q) + self.arb_busy
            self.m[w]["prod_q_end"] = sum(len(s.q_prod) for s in self.seats.values())
        if 0 <= w < self.weeks and self.quotas is not None:
            for a in ACCOUNTS:
                self.m[w]["left_" + a] = max(0.0, 1 - self.used[a] / self.quotas[a])
                ex = self.exhausted_at[a]
                self.m[w]["exh_h_" + a] = 0.0 if ex is None else (t - ex) / HOUR
            self.m[w]["pool_left"] = max(0.0, 1 - sum(self.used.values()) / sum(self.quotas.values()))
            self.m[w]["blocked_h"] = (t - self.blocked_since) / HOUR if self.all_blocked else 0.0
        for a in ACCOUNTS:
            self.used[a] = 0.0
            self.exhausted_at[a] = None
        if self.all_blocked:
            self.all_blocked = False
            for s in self.seats.values():
                self.set_idle(s, t)
                if s.stalled:
                    self.resume(s, t, "reset")
                else:
                    self.try_work(s, t)
        if t < self.T_end:
            self.push(t + WEEK, "week_reset")
            self.push(t + 128 * HOUR, "snap128")

    # ---- run
    def run(self):
        th = self.th
        for name, s in self.seats.items():
            for i in range(int(th["init_queue"])):
                k = mix(self.seed, F_INIT, SEATS.index(name), i)
                tk = Ticket(k, "product" if u01(self.seed, F_CLS, k) < th["p_prod_ext"] else "process", 0, "init")
                tk.seat = name
                tk.quick = u01(self.seed, F_QUICK, k) < th["p_quick"]
                (s.q_prod if tk.cls == "product" else s.q_proc).append(tk)
        self.push(0, "hour")
        self.push(0, "day")
        self.push(WEEK, "week_reset")
        self.push(128 * HOUR, "snap128")
        t0 = self.warm * WEEK
        acts = self.rollout if self.rollout is not None else [(0, r) for r in self.pol.get("roles", [])]
        for d, r in acts:
            self.push(t0 + d * DAY, "activate", r)
        for s in self.seats.values():
            self.push(0, "kick", s.name)
        while self.ev:
            t, _, kind, pl = heapq.heappop(self.ev)
            if t > self.T_end:
                break
            if kind == "helper_done":
                s = self.seats[pl[0]]
                tk = pl[1]
                s.running -= 1
                tk.pending -= 1
                if tk.pending == 0:
                    self.complete(t, s, tk)
                self.after_completion(s, t)
            elif kind == "launch":
                self.launch(t, self.seats[pl[0]], pl[1], pl[2])
            elif kind == "quick_done":
                s = self.seats[pl[0]]
                s.serial_busy = False
                self.complete(t, s, pl[1])
                self.after_completion(s, t)
            elif kind == "resume":
                s = self.seats[pl[0]]
                if s.stalled and s.stall_n == pl[1]:
                    if pl[2] == "owner" and s.qlen() == 0:
                        continue
                    self.resume(s, t, pl[2])
            elif kind == "disc":
                self.disc(t, pl[0], pl[1])
            elif kind == "arb_done":
                self.arb_done(t, pl[0], pl[1])
            elif kind == "hour":
                self.hour(t)
            elif kind == "day":
                self.day(t)
            elif kind == "ring_tick":
                self.ring_tick(t)
            elif kind == "activate":
                self.activate(t, pl[0])
            elif kind == "week_reset":
                self.week_reset(t)
            elif kind == "snap128":
                w = int(t // WEEK)
                if w < self.weeks:
                    self.m[w]["used128_total"] = sum(self.used.values())
                    for a in ACCOUNTS:
                        self.m[w]["used128_" + a] = self.used[a]
            elif kind == "kick":
                self.try_work(self.seats[pl[0]], t)
        for s in self.seats.values():
            self.set_idle(s, self.T_end)
        return self.summaries()

    def summaries(self):
        out = []
        for w in range(self.weeks):
            m = dict(self.m[w])
            L = self.lists[w]
            g = lambda k: m.get(k, 0.0)
            r = {k: v for k, v in m.items()}
            r["filed_d"] = g("filed") / 7
            r["done_d"] = g("done") / 7
            r["rework_share"] = g("rework_filed") / max(1, g("filed"))
            r["vfail_share"] = g("verify_fail") / max(1, g("verify_n"))
            r["nudges_d"] = g("nudges") / 7
            r["ite_week"] = g("ite")
            r["helpers_week"] = g("helpers")
            r["proc_share"] = g("commits_proc") / max(1e-9, g("commits"))
            rd = L.get("resolve_d", [])
            r["owner_resolve_med_d"] = float(np.median(rd)) if rd else float("nan")
            ld = L.get("lead_d", [])
            r["lead_p90_d"] = float(np.percentile(ld, 90)) if ld else float("nan")
            r["sound_prod_d"] = g("sound_prod") / 7
            r["accepted_prod_d"] = g("accepted_prod") / 7
            r["escapes_wk"] = g("escapes")
            r["idle_min_d_FOUNDRY"] = g("idle_min_FOUNDRY") / 7
            r["idle_min_d_BENCH"] = g("idle_min_BENCH") / 7
            r["owner_att_min_per_present_h"] = g("owner_att_min") / max(1, g("present_h"))
            r["cards_waiting_3d"] = g("cards_waiting_3d_h") / (7 * 24)
            r["rings_d"] = g("rings") / 7
            if self.quotas is not None:
                r["min_left_at_reset"] = min(m.get("left_" + a, 1.0) for a in ACCOUNTS)
                r["exh_h_max"] = max(m.get("exh_h_" + a, 0.0) for a in ACCOUNTS)
                r["pool_left"] = m.get("pool_left", 1.0)
                r["blocked_h"] = m.get("blocked_h", 0.0)
            out.append(r)
        return out


# ---------------------------------------------------------------- calibration (ABC rejection)
def discrepancy(P, r):
    worst, per = 0.0, {}
    for k, tg in P["targets"].items():
        v = r.get(k, float("nan"))
        if v != v:
            d = 9.0
        elif tg["kind"] == "rel":
            d = abs(v / tg["value"] - 1) / tg["tol"]
        else:
            d = abs(v - tg["value"]) / tg["tol"]
        per[k] = round(d, 3)
        worst = max(worst, d)
    return worst, per


def derive_quotas(P, wk):
    used = P["fixed"]["account_used_at_128h"]["value"]
    return {a: wk["used128_" + a] / used[a] for a in ACCOUNTS}


# Structural alternative (GPT r2: test alternative structures, not just parameters). "park": a parked ticket is never
# worked, so the factory is demand-limited and extra seat time only shortens lead time. "pull": an idle seat with an
# empty queue pulls the oldest parked ticket, so the factory is capacity-limited and extra seat time is extra output.
# Each structure has its own calibration (calib_members[_pull].jsonl); findings are reported under both.
STRUCTURE = "park"


def sfx():
    return "" if STRUCTURE == "park" else "_" + STRUCTURE


def run_v2_member(P, th, seed):
    sim = Sim(P, th, policy_cfg(P, "v2"), seed, weeks=2)
    res = sim.run()
    return res[1]


def cmd_calibrate(a):
    P = load_params()
    os.makedirs(a.out, exist_ok=True)
    path = os.path.join(a.out, a.file)
    box = json.load(open(a.box))["box"] if a.box else None
    done = set()
    if os.path.exists(path):
        for l in open(path):
            done.add(json.loads(l)["member"])
    t0 = time.time()
    with open(path, "a") as fh:
        for mbr in range(a.start, a.start + a.n):
            if mbr in done:
                continue
            if time.time() - t0 > a.budget_s:
                print("budget reached at member", mbr)
                break
            th = draw_theta(P, a.prior_seed, mbr, box)
            r = run_v2_member(P, th, seed=1000 + mbr)
            worst, per = discrepancy(P, r)
            rec = {"member": mbr, "stage": a.box or "prior", "theta": th, "worst": round(worst, 3), "per": per, "accepted": worst <= 1.0,
                   "summary": {k: r.get(k) for k in P["targets"]}, "quotas": derive_quotas(P, r)}
            fh.write(json.dumps(rec) + "\n")
    n = sum(1 for _ in open(path))
    acc = sum(1 for l in open(path) if json.loads(l)["accepted"])
    print(f"members {n}, accepted {acc}, elapsed {time.time() - t0:.0f}s")


def fit_score(m):
    return sum(min(d, 5.0) ** 2 for d in m["per"].values())


def cmd_narrow(a):
    """Shrink the proposal box toward the region the baseline targets favour. Uses only pilot draws; the box is
    clipped to the prior, so the final rejection step still samples the (truncated) posterior of the original prior."""
    P = load_params()
    ms = [json.loads(l) for l in open(os.path.join(a.out, a.src))]
    ms.sort(key=fit_score)
    top = ms[:max(10, int(len(ms) * a.top))]
    box = {}
    for k, pr in P["priors"].items():
        x = np.array([m["theta"][k] for m in top])
        lo, hi = np.percentile(x, 2.5), np.percentile(x, 97.5)
        w = (hi - lo) * a.widen + 0.02 * (pr["hi"] - pr["lo"])
        box[k] = [max(pr["lo"], float(lo - w)), min(pr["hi"], float(hi + w))]
    shr = {k: round((b[1] - b[0]) / (P["priors"][k]["hi"] - P["priors"][k]["lo"]), 2) for k, b in box.items()}
    json.dump({"src": a.src, "n_src": len(ms), "n_top": len(top), "box": box, "width_frac": shr},
              open(os.path.join(a.out, a.dst), "w"), indent=1)
    print("box from", len(top), "of", len(ms), "; narrowest:", sorted(shr.items(), key=lambda kv: kv[1])[:10])


def cmd_mcmc(a):
    """ABC-MCMC (Marjoram et al. 2003) over the uniform priors. Each chain starts at a good pilot draw and first
    DESCENDS (accept a move whose worst discrepancy does not exceed max(1, current)); once a chain is inside every
    tolerance it runs at epsilon = 1 and a member is recorded every --thin steps. Each step uses a fresh seed, so a
    member is accepted on the basis of one noisy run, never a chosen seed. Resumable: chain state in mcmc_state.json."""
    P = load_params()
    pri = P["priors"]
    keys = sorted(pri)
    st_path = os.path.join(a.out, f"mcmc_state{sfx()}.json")
    mem_path = os.path.join(a.out, a.file.replace(".jsonl", sfx() + ".jsonl"))
    if os.path.exists(st_path):
        state = json.load(open(st_path))
    else:
        if a.init_from_members:
            # start each chain from the last recorded state of one chain of another structure's ensemble; worst is
            # unknown under this structure, so the chain starts as "descending" (worst 99)
            last = {}
            for l in open(os.path.join(a.out, a.init_from_members)):
                m = json.loads(l)
                last[m.get("chain", 0)] = m
            pilot = list(last.values())
            for m in pilot:
                m["worst"] = 99.0
        else:
            pilot = sorted((json.loads(l) for l in open(os.path.join(a.out, a.src))), key=fit_score)
        state = {"chains": [{"theta": m["theta"], "worst": m["worst"], "step": 0, "acc": 0, "recorded": 0}
                            for m in pilot[:a.chains]]}
    if a.respawn:
        # chains still outside tolerance restart from the current state of a chain that is inside (population
        # restart). Used once in the 2026-10-27 calibration after 400 steps, when 26/40 chains were still descending.
        ins = [c for c in state["chains"] if c["worst"] <= a.respawn_below]
        for i, c in enumerate(state["chains"]):
            if c["worst"] > a.respawn_below and ins:
                src = ins[i % len(ins)]
                for k in ("theta", "worst", "per", "summary", "quotas"):
                    c[k] = json.loads(json.dumps(src[k]))
                c["respawned_from"] = state["chains"].index(src)
    t0 = time.time()
    with open(mem_path, "a") as fh:
        while time.time() - t0 < a.budget_s:
            moved = False
            for ci, ch in enumerate(state["chains"]):
                if ch["step"] >= a.steps:
                    continue
                moved = True
                ch["step"] += 1
                step = ch["step"]
                th = dict(ch["theta"])
                for i, k in enumerate(keys):
                    w = pri[k]["hi"] - pri[k]["lo"]
                    z = math.sqrt(-2 * math.log(1 - u01(a.prior_seed, 77, ci, step, i, 1))) * \
                        math.cos(2 * math.pi * u01(a.prior_seed, 77, ci, step, i, 2))
                    v = th[k] + a.sd * w * z
                    while v < pri[k]["lo"] or v > pri[k]["hi"]:
                        v = 2 * pri[k]["lo"] - v if v < pri[k]["lo"] else 2 * pri[k]["hi"] - v
                    th[k] = int(round(v)) if pri[k].get("int") else v
                r = run_v2_member(P, th, seed=int(mix(a.prior_seed, ci, step) % 10 ** 9))
                worst, per = discrepancy(P, r)
                if worst <= max(1.0, ch["worst"] + (a.slack if ch["worst"] > 1.0 else 0.0)):
                    ch["theta"], ch["worst"], ch["per"], ch["summary"] = th, worst, per, \
                        {k: r.get(k) for k in P["targets"]}
                    ch["quotas"] = derive_quotas(P, r)
                    ch["acc"] += 1
                if ch["worst"] <= 1.0 and step % a.thin == 0:
                    ch["recorded"] += 1
                    rec = {"member": ci * 100000 + step, "stage": "mcmc", "chain": ci, "theta": ch["theta"],
                           "worst": round(ch["worst"], 3), "per": ch["per"], "accepted": True,
                           "summary": ch["summary"], "quotas": ch["quotas"]}
                    fh.write(json.dumps(rec) + "\n")
            if not moved:
                break
    json.dump(state, open(st_path, "w"))
    inside = sum(1 for c in state["chains"] if c["worst"] <= 1)
    print(f"chains {len(state['chains'])}, inside tolerance {inside}, steps "
          f"{min(c['step'] for c in state['chains'])}, recorded {sum(c['recorded'] for c in state['chains'])}, "
          f"accept rate {sum(c['acc'] for c in state['chains']) / max(1, sum(c['step'] for c in state['chains'])):.2f}, "
          f"{time.time() - t0:.0f}s")


# Parameters today's v2 cannot see (they only describe v3 mechanisms). The baseline carries no information about
# them, so their posterior IS their prior: each member gets a fresh prior draw, keyed by member id, instead of the value
# the calibration chain happened to carry (which would fake a narrowing; GPT r2 #10).
V3_ONLY = ("arb_batch_gamma", "arb_batch_q", "arb_check_min", "arb_fr_max", "arb_ite", "arb_s_hi", "arb_s_lo",
           "aud_ite", "s_aud", "p_rule", "rule_delta", "rule_check_min", "m_ops_stall", "m_ops_waste", "m_prod_f",
           "prod_ite_day", "innov_ite_week", "m_innov", "m_cond", "cond_ite_msg", "role_build_tix", "role_cards_day",
           "c_wake_ite", "p_ring_ok", "p_unwork", "teeth")


def load_members(out, accepted=True, max_n=None, file=None):
    """Accepted ABC-MCMC states, de-duplicated (a chain that rejects a move records the same state again), spread
    evenly across the run and capped at max_n; v3-only parameters redrawn from the prior."""
    P = load_params()
    ms = [json.loads(l) for l in open(os.path.join(out, file or f"calib_members{sfx()}.jsonl"))]
    if not accepted:
        return ms
    seen, uniq = set(), []
    for m in ms:
        if not m["accepted"]:
            continue
        k = json.dumps(m["theta"], sort_keys=True)
        if k not in seen:
            seen.add(k)
            uniq.append(m)
    uniq.sort(key=lambda m: (m.get("chain", 0), m["member"]))
    if max_n and len(uniq) > max_n:
        idx = np.linspace(0, len(uniq) - 1, max_n).round().astype(int)
        uniq = [uniq[i] for i in sorted(set(idx))]
    keys = sorted(P["priors"])
    for m in uniq:
        th = dict(m["theta"])
        for k in V3_ONLY:
            pr = P["priors"][k]
            v = pr["lo"] + (pr["hi"] - pr["lo"]) * u01(4242, F_THETA, m["member"], keys.index(k))
            th[k] = int(round(v)) if pr.get("int") else v
        m["theta"] = th
    return uniq


def cmd_validate(a):
    """Re-run kept members as v2 on FRESH seeds (never the seed that accepted them) and report, per target, the share of
    runs inside tolerance and the ensemble spread. This is the honest check: acceptance used one lucky-or-not run."""
    P = load_params()
    ms = load_members(a.out, max_n=a.members)
    rows = []
    t0 = time.time()
    for m in ms:
        for sd in range(a.seeds):
            r = run_v2_member(P, m["theta"], seed=900000 + m["member"] * 7 + sd)
            worst, per = discrepancy(P, r)
            rows.append({"member": m["member"], "worst": worst, "per": per, "v": {k: r.get(k) for k in P["targets"]}})
    out = {"members": len(ms), "runs": len(rows), "all_inside": round(float(np.mean([r["worst"] <= 1 for r in rows])), 3),
           "targets": {}}
    for k, tg in P["targets"].items():
        v = np.array([r["v"][k] for r in rows], dtype=float)
        out["targets"][k] = {"target": tg["value"], "tol": tg["tol"], "kind": tg["kind"],
                             "inside": round(float(np.mean([r["per"][k] <= 1 for r in rows])), 3),
                             "p10_p50_p90": [round(float(x), 4) for x in np.nanpercentile(v, [10, 50, 90])]}
    json.dump(out, open(os.path.join(a.out, f"validation{sfx()}.json"), "w"), indent=1)
    print(json.dumps({k: (v["inside"], v["p10_p50_p90"]) for k, v in out["targets"].items()}))
    print("all-inside share", out["all_inside"], "members", len(ms), f"{time.time() - t0:.0f}s")


# ---------------------------------------------------------------- experiments
def _caps(h, d):
    return {"wakes_per_seat_hour": h, "wakes_per_seat_day": d, "wakes_per_day": max(80, d)}


EXPERIMENTS = {
    "validate": [("v2", {})],
    "versions": [("v2", {}), ("v3.0", {}), ("v3.1", {}), ("v3.2", {}), ("v3.3", {}), ("v3.4", {})],
    "versions_unlimited": [(v, {"_unlimited": True}) for v in ("v2", "v3.0", "v3.1", "v3.2", "v3.3", "v3.4")],
    "versions_q130": [(v, {"_quota_mult": 1.3}) for v in ("v2", "v3.0", "v3.1", "v3.2", "v3.3", "v3.4")],
    "rollout": [("v2", {}), ("three_wave", {"_rollout": [(0, "Conductor"), (0, "Operations"), (7, "Producer"),
                                                          (7, "Arbiter"), (14, "Auditor"), (14, "Innovator")]}),
                ("all_at_once", {"_rollout": [(0, r) for r in ROLE_ORDER]})],
    # the FIRST label of each experiment is its comparison base (today's setting)
    "helper_cap": [("v3.4", {"_label": "cap_today"})] + [("v3.4", {"helper_cap": c, "_label": f"cap{c}"})
                                                          for c in (1, 2, 4, 6)],
    "arbiter": [("v3.4", {"arb_strict": s, "_label": f"strict{s}"}) for s in (0.6, 0.0, 0.3, 0.9)],
    "auditor": [("v3.4", {"aud_rate": r, "_label": f"aud{r}"}) for r in (0.1, 0.0, 0.02, 0.3)],
    "wake_caps": [("v2", {"_label": "nodispatch"})] + [("v3.0", {"wake_caps": _caps(h, d), "_label": f"w{h}h{d}d"})
                                                       for h, d in ((1, 10), (3, 30), (6, 60), (30, 720))],
    "wake_caps_unlimited": [("v2", {"_label": "nodispatch", "_unlimited": True})]
    + [("v3.0", {"wake_caps": _caps(h, d), "_label": f"w{h}h{d}d", "_unlimited": True})
       for h, d in ((1, 10), (3, 30), (6, 60), (30, 720))],
    "throttle": [("v3.4", {"throttle": m, "_label": m}) for m in ("config", "none", "reverse", "helpers_first")],
    # one role at a time on top of v3.2 (versions add roles in bundles: v3.3 = Producer AND Arbiter)
    "isolate": [("v3.2", {})] + [("v3.2", {"_rollout": [(0, "Conductor"), (0, "Operations")] + [(0, r) for r in add],
                                           "_label": "+" + "+".join(add)})
                                 for add in (("Arbiter",), ("Producer",), ("Auditor",), ("Innovator",))],
    # the design caps the Auditor at 4 investigations/day; that cap, not the sample rate, decides what it can find
    "auditor_cap": [("v3.4", {"_label": "aud_cap4"})] + [("v3.4", {"aud_max": c, "aud_rate": r, "_label": f"aud_cap{c}_r{r}"})
                                                         for c, r in ((0, 0.1), (12, 0.1), (40, 0.3))],
}
EXPERIMENTS["isolate_unlimited"] = [(p, dict(o, _unlimited=True)) for p, o in EXPERIMENTS["isolate"]]


def run_policy(P, m, seed, pol_name, over, weeks=4, warm=1):
    over = dict(over)
    label = over.pop("_label", None) or pol_name
    rollout = over.pop("_rollout", None)
    qm = over.pop("_quota_mult", 1.0)
    quotas = None if over.pop("_unlimited", False) else {k: v * qm for k, v in m["quotas"].items()}
    pname = "v3.1" if rollout is not None else pol_name
    pol = policy_cfg(P, pname, **over)
    sim = Sim(P, m["theta"], pol, seed, weeks=weeks, quotas=quotas, warm_weeks=warm,
              rollout=rollout)
    res = sim.run()
    return label, res


HEAD = ["sound_prod_d", "accepted_prod_d", "done_d", "nudges_d", "escapes_wk", "pool_left", "blocked_h",
        "min_left_at_reset", "exh_h_max",
        "proc_share", "idle_min_d_FOUNDRY", "idle_min_d_BENCH", "ite_week", "rings_d", "owner_att_min_per_present_h",
        "cards_waiting_3d", "arb_pass_defective", "arb_verdicts", "arb_batched", "audits", "audit_found", "arb_q_end", "prod_q_end", "rework_share",
        "vfail_share", "filed_d", "helpers_week"]


def cmd_experiment(a):
    P = load_params()
    ms = load_members(a.out, max_n=a.pool)
    ms = ms[a.start:a.start + a.members]
    path = os.path.join(a.out, f"exp_{a.name}{sfx()}.jsonl")
    done = set()
    if os.path.exists(path):
        for l in open(path):
            r = json.loads(l)
            done.add((r["member"], r["seed"]))
    t0 = time.time()
    with open(path, "a") as fh:
        for m in ms:
            for sd in range(a.seeds):
                seed = 50000 + m["member"] * 97 + sd
                if (m["member"], seed) in done:
                    continue
                if time.time() - t0 > a.budget_s:
                    print("budget reached")
                    return
                rows = {}
                for pol_name, over in EXPERIMENTS[a.name]:
                    label, res = run_policy(P, m, seed, pol_name, over, weeks=a.weeks)
                    rows[label] = [{k: w.get(k) for k in HEAD} for w in res]
                fh.write(json.dumps({"member": m["member"], "seed": seed, "rows": rows}) + "\n")
    print(f"{a.name}: wrote through member slice {a.start}+{a.members}, {time.time() - t0:.0f}s")


# ---------------------------------------------------------------- report
def _wmean(rows, k, weeks):
    vals = [rows[w].get(k) for w in weeks if rows[w].get(k) is not None]
    vals = [v for v in vals if v == v]
    return float(np.mean(vals)) if vals else float("nan")


def summarize_experiment(P, out, name, members):
    path = os.path.join(out, f"exp_{name}{sfx()}.jsonl")
    if not os.path.exists(path):
        return None
    recs = [json.loads(l) for l in open(path)]
    labels = list(recs[0]["rows"].keys())
    weeks = None
    res = {"n_runs": len(recs), "labels": labels, "metrics": {}, "win_vs_first": {}, "splits": {}}
    by_m = {m["member"]: m for m in members}
    for k in HEAD:
        res["metrics"][k] = {}
        for lab in labels:
            nweeks = len(recs[0]["rows"][lab])
            weeks = list(range(1, nweeks))
            vals = np.array([_wmean(r["rows"][lab], k, weeks) for r in recs])
            vals = vals[~np.isnan(vals)]
            if len(vals):
                res["metrics"][k][lab] = [round(float(np.percentile(vals, q)), 4) for q in (10, 50, 90)]
    base = labels[0]
    for k in ("sound_prod_d", "nudges_d", "escapes_wk", "pool_left", "blocked_h", "idle_min_d_FOUNDRY",
              "idle_min_d_BENCH", "proc_share", "exh_h_max", "accepted_prod_d", "owner_att_min_per_present_h", "done_d"):
        res["win_vs_first"][k] = {}
        for lab in labels[1:]:
            d = np.array([_wmean(r["rows"][lab], k, weeks) - _wmean(r["rows"][base], k, weeks) for r in recs])
            d = d[~np.isnan(d)]
            if len(d):
                res["win_vs_first"][k][lab] = {"share_up": round(float(np.mean(d > 1e-9)), 3),
                                               "share_down": round(float(np.mean(d < -1e-9)), 3),
                                               "median_delta": round(float(np.median(d)), 4)}
    # which assumed parameters split the main effect (Spearman of theta vs delta), for the last label vs first
    for k in ("sound_prod_d", "escapes_wk", "pool_left", "nudges_d"):
        res["splits"][k] = {}
        for lab in labels[1:]:
            d = np.array([_wmean(r["rows"][lab], k, weeks) - _wmean(r["rows"][base], k, weeks) for r in recs])
            ok = ~np.isnan(d)
            if ok.sum() < 8:
                continue
            ths = [by_m[r["member"]]["theta"] for r in recs]
            cors = []
            rd = np.argsort(np.argsort(d[ok]))
            for p in ths[0]:
                x = np.array([th[p] for th in ths])[ok]
                if np.ptp(x) == 0:
                    continue
                rx = np.argsort(np.argsort(x))
                c = float(np.corrcoef(rx, rd)[0, 1])
                cors.append((abs(c), p, round(c, 2)))
            cors.sort(reverse=True)
            res["splits"][k][lab] = [(p, c) for _, p, c in cors[:4]]
    return res


def cmd_report(a):
    P = load_params()
    members = load_members(a.out, accepted=False)
    # unique accepted states with v3-only parameters redrawn: the SAME thetas the experiments ran (keyed by member id)
    acc = load_members(a.out)
    rep = {"structure": STRUCTURE, "calibration": {"recorded": len(members), "unique_accepted": len(acc)}}
    # which targets reject most
    fails = collections.Counter()
    for m in members:
        for k, d in m["per"].items():
            if d > 1:
                fails[k] += 1
    rep["calibration"]["rejections_by_target"] = dict(fails.most_common())
    # posterior vs prior: parameters the targets constrain
    post = {}
    for p, pr in P["priors"].items():
        if not acc:
            break
        if p in V3_ONLY:                     # v2 data says nothing about these; their spread is the prior by design
            continue
        x = np.array([m["theta"][p] for m in acc])
        w = pr["hi"] - pr["lo"]
        post[p] = {"lo": pr["lo"], "hi": pr["hi"], "post_p10": round(float(np.percentile(x, 10)), 4),
                   "post_p90": round(float(np.percentile(x, 90)), 4),
                   "shrink": round(float((np.percentile(x, 90) - np.percentile(x, 10)) / (0.8 * w)), 2) if w else None}
    rep["calibration"]["posterior"] = post
    rep["experiments"] = {}
    for name in EXPERIMENTS:
        s = summarize_experiment(P, a.out, name, acc)
        if s:
            rep["experiments"][name] = s
    with open(os.path.join(a.out, f"results{sfx()}.json"), "w") as fh:
        json.dump(rep, fh, indent=1)
    print("wrote", os.path.join(a.out, f"results{sfx()}.json"))


def cmd_one(a):
    P = load_params()
    th = {k: (pr["lo"] + pr["hi"]) / 2 for k, pr in P["priors"].items()}
    for k, pr in P["priors"].items():
        if pr.get("int"):
            th[k] = int(round(th[k]))
    if a.member is not None:
        m = [x for x in load_members(a.out) if x["member"] == a.member][0]
        th, quotas = m["theta"], m["quotas"]
    else:
        quotas = None
    t0 = time.time()
    sim = Sim(P, th, policy_cfg(P, a.policy), a.seed, weeks=a.weeks, quotas=quotas, warm_weeks=a.warm)
    res = sim.run()
    for w, r in enumerate(res):
        print("week", w, json.dumps({k: (round(v, 3) if isinstance(v, float) else v) for k, v in sorted(r.items())
                                     if k in P["targets"] or k in HEAD}))
    print(f"{time.time() - t0:.2f}s")


# ---------------------------------------------------------------- counterfactual (v3_vs_v2.py)
# What would v2 have done in a given real week? The calibrated v2 ensemble, re-run with the week's observed owner
# input: presence scaled by his active hours against the tag week, arrivals per present hour scaled by his messages per
# active hour against the tag week. The range is p5-p95 across members x seeds. It is trusted only while a backtest on
# held-out real v2 weeks (weeks the calibration never saw) covers enough (week, metric) cells; otherwise UNMEASURED.
CF_SEEDS = 2


def cf_inputs(week, ref_week):
    """-> (presence scale, arrival scale, why) from observed owner messages and active hours, or None if unmeasured"""
    g = lambda w, k: (w.get(k) or {}).get("v")
    mo, ho, mr, hr = g(week, "owner_msgs_wk"), g(week, "owner_active_h_wk"), g(ref_week, "owner_msgs_wk"), g(ref_week, "owner_active_h_wk")
    if not (mo and ho and mr and hr):
        return None
    pres = ho / hr
    arr = (mo / ho) / (mr / hr)
    return pres, arr, "owner messages %d in %d active h, against the tag week's %d in %d" % (mo, ho, mr, hr)


def cf_range(P, members, pres, arr, cmap, pct, seed0=700000):
    vals = {k: [] for k in cmap}
    for m in members:
        th = dict(m["theta"])
        th["owner_presence_mult"] = th["owner_presence_mult"] * pres
        th["lam_ext_h"] = th["lam_ext_h"] * arr
        for sd in range(CF_SEEDS):
            r = run_v2_member(P, th, seed=seed0 + m["member"] * 7 + sd)
            for k, (sk, mult) in cmap.items():
                v = r.get(sk, float("nan"))
                vals[k].append(v * mult if v == v else float("nan"))
    out = {}
    for k, v in vals.items():
        a = np.array(v, dtype=float)
        a = a[~np.isnan(a)]
        out[k] = [float(np.percentile(a, pct[0])), float(np.percentile(a, pct[1]))] if len(a) else None
    return out


def _cf_members(a):
    return load_members(a.out, max_n=a.members)


def cmd_backtest(a):
    """Held-out real v2 weeks: does the ensemble's p5-p95, fed each week's owner input, contain what v2 really did?"""
    P = load_params()
    v2 = json.load(open(a.v2))
    R = json.load(open(a.rules))
    cf, H = R["counterfactual"], R["v2_history"]
    ref_w = v2["weeks"][H["reference_week"]]
    ms = _cf_members(a)
    t0 = time.time()
    cells, weeks = [], {}
    for day in H["context_weeks"]:
        w = v2["weeks"][day]
        inp = cf_inputs(w, ref_w)
        if inp is None:
            weeks[day] = {"status": "UNMEASURED", "why": "owner messages or active hours unmeasured"}
            continue
        rng = cf_range(P, ms, inp[0], inp[1], cf["metrics"], cf["range_pct"])
        row = {}
        for k, r in rng.items():
            obs = (w.get(k) or {}).get("v")
            if r is None or obs is None:
                row[k] = {"observed": obs, "range": r, "inside": None}
                continue
            ins = r[0] <= obs <= r[1]
            row[k] = {"observed": obs, "range": [round(r[0], 4), round(r[1], 4)], "inside": ins}
            cells.append(ins)
        weeks[day] = {"presence_scale": round(inp[0], 3), "arrival_scale": round(inp[1], 3), "input": inp[2], "cells": row}
    cov = float(np.mean(cells)) if cells else None
    need = cf["backtest_min_coverage"]
    out = {"structure": STRUCTURE, "members": len(ms), "seeds": CF_SEEDS, "range_pct": cf["range_pct"],
           "coverage": None if cov is None else round(cov, 3), "cells": len(cells), "need": need,
           "status": "PASS" if cov is not None and cov >= need else "FAIL",
           "measured_utc": time.strftime("%Y-%m-%dT%H:%MZ", time.gmtime()), "weeks": weeks,
           "_why": "held-out weeks are the v2 weeks before the tag week; the calibration targets came from the tag week"}
    dst = os.path.join(os.path.dirname(os.path.abspath(a.v2)), f"backtest{sfx()}.json")
    json.dump(out, open(dst, "w"), indent=1)
    print("backtest", STRUCTURE, out["status"], "coverage", out["coverage"], "of", len(cells), "cells", f"{time.time() - t0:.0f}s", "->", dst)
    for day, w in weeks.items():
        for k, c in (w.get("cells") or {}).items():
            print(" ", day, k, c["observed"], c["range"], c["inside"])


def cmd_counterfactual(a):
    """v3_vs_v2.py hands one real week; write its v2 range, MEASURED only while this structure's backtest passed."""
    P = load_params()
    inp = json.load(open(a.input))
    cf = inp["rules"]
    bt_p = os.path.join(os.path.dirname(os.path.abspath(a.input)), f"backtest{sfx()}.json")
    out = {"status": "UNMEASURED", "structure": STRUCTURE}
    bt = json.load(open(bt_p)) if os.path.exists(bt_p) else None
    ref_w = inp["v2"].get(inp.get("reference_week", "")) or {}
    ci = cf_inputs(inp["week"], ref_w)
    if bt is None:
        out["why"] = "no backtest on held-out v2 weeks (%s)" % bt_p
    elif bt["status"] != "PASS":
        out["why"] = "backtest failed: coverage %s of %d cells, need %s" % (bt["coverage"], bt["cells"], bt["need"])
    elif ci is None:
        out["why"] = "the week's owner messages or active hours are unmeasured"
    else:
        ms = _cf_members(a)
        rng = cf_range(P, ms, ci[0], ci[1], cf["metrics"], cf["range_pct"])
        out = {"status": "MEASURED", "structure": STRUCTURE, "range": {k: r for k, r in rng.items() if r},
               "input": ci[2], "backtest_coverage": bt["coverage"], "members": len(ms), "seeds": CF_SEEDS}
    json.dump(out, open(a.dst, "w"), indent=1)
    print("counterfactual", out["status"], out.get("why", ""))


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--out", default=OUT)
    ap.add_argument("--structure", choices=("park", "pull"), default="park")
    sub = ap.add_subparsers(dest="cmd", required=True)
    c = sub.add_parser("calibrate")
    c.add_argument("--n", type=int, default=200)
    c.add_argument("--start", type=int, default=0)
    c.add_argument("--prior-seed", type=int, default=7)
    c.add_argument("--budget-s", type=float, default=270)
    c.add_argument("--box", help="proposal box json from `narrow` (default: the full prior)")
    c.add_argument("--file", default="calib_members.jsonl")
    mc = sub.add_parser("mcmc")
    mc.add_argument("--src", default="calib_pilot.jsonl")
    mc.add_argument("--file", default="calib_members.jsonl")
    mc.add_argument("--chains", type=int, default=40)
    mc.add_argument("--steps", type=int, default=600)
    mc.add_argument("--thin", type=int, default=10)
    mc.add_argument("--sd", type=float, default=0.04)
    mc.add_argument("--prior-seed", type=int, default=11)
    mc.add_argument("--budget-s", type=float, default=270)
    mc.add_argument("--respawn", action="store_true")
    mc.add_argument("--respawn-below", type=float, default=1.0,
                    help="chains above this worst discrepancy restart from one below it (pull calibration used 1.6)")
    mc.add_argument("--init-from-members", help="start chains from another ensemble's members file")
    mc.add_argument("--slack", type=float, default=0.0,
                    help="while descending, accept a move up to this much worse (noise tolerance)")
    nw = sub.add_parser("narrow", help="pilot stage: proposal box = widened p2.5-p97.5 of the best draws")
    nw.add_argument("--src", default="calib_pilot.jsonl")
    nw.add_argument("--top", type=float, default=0.05)
    nw.add_argument("--widen", type=float, default=0.25)
    nw.add_argument("--dst", default="calib_box.json")
    e = sub.add_parser("experiment")
    e.add_argument("name", choices=sorted(EXPERIMENTS))
    e.add_argument("--members", type=int, default=1000)
    e.add_argument("--start", type=int, default=0)
    e.add_argument("--pool", type=int, default=240, help="ensemble size drawn from the calibration")
    e.add_argument("--seeds", type=int, default=1)
    e.add_argument("--weeks", type=int, default=4)
    e.add_argument("--budget-s", type=float, default=270)
    sub.add_parser("report")
    v = sub.add_parser("validate")
    v.add_argument("--members", type=int, default=240)
    v.add_argument("--seeds", type=int, default=3)
    o = sub.add_parser("one")
    o.add_argument("--policy", default="v2")
    o.add_argument("--seed", type=int, default=1)
    o.add_argument("--weeks", type=int, default=2)
    o.add_argument("--warm", type=int, default=0)
    o.add_argument("--member", type=int)
    V3D = os.environ.get("RM_V3V2_DIR", "/mnt/d/ClaudeWork/rimmandrake/v3_vs_v2")
    bt = sub.add_parser("backtest", help="v3_vs_v2: the v2 ensemble against held-out real v2 weeks")
    bt.add_argument("--v2", default=os.path.join(V3D, "v2_weeks.json"))
    bt.add_argument("--rules", default=os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "v3_vs_v2_rules.json"))
    bt.add_argument("--members", type=int, default=240)
    cfp = sub.add_parser("counterfactual", help="v3_vs_v2: what v2 would have done in one real week")
    cfp.add_argument("--input", required=True)
    cfp.add_argument("--dst", required=True)
    cfp.add_argument("--members", type=int, default=240)
    a = ap.parse_args(argv)
    global STRUCTURE
    STRUCTURE = a.structure
    {"calibrate": cmd_calibrate, "narrow": cmd_narrow, "mcmc": cmd_mcmc, "validate": cmd_validate, "experiment": cmd_experiment, "report": cmd_report, "one": cmd_one,
     "backtest": cmd_backtest, "counterfactual": cmd_counterfactual}[a.cmd](a)


if __name__ == "__main__":
    main()
