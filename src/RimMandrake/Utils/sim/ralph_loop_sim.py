#!/usr/bin/env python3
"""ralph_loop_sim.py: the Ralph loop in the same bottle as v2 and v3. Item RALPH_LOOP_DESIGN_ONE_PROMPT_FOREVER;
design design/RimMandrake/ralph_loop_design_2026-10-29.md. A sibling of rimflow_v3_sim.py: it imports that model,
keeps its calibrated outside world (owner presence, arrivals, ticket classes, hidden defects, discovery, cards, token
quotas) and replaces only the factory.

Variants (all with no Dispatcher, no roles, no helpers, no orchestrating seat):
  A         one loop on Archmagi. A fresh context per iteration, one ticket per iteration, serial. Each iteration runs
            the ticket's v2 helper work back to back in one context (the SAME keyed draws v2's helpers got, so
            the work is paired), plus a restart and a stack load. It never stops on its own, so there are no
            keep-going nudges. Instead it can go off-track (a wasted iteration) or spiral (wasted iterations until it
            escapes by itself or the owner notices and steers it; a steer is counted as a nudge).
  AB_test   A, plus loop B on SteveDesktop that owns live tests: a product close waits for B's live run. A pass
            closes it as "tested" (accepted_prod: tested by a second loop, NOT judged blind). A fail sends it back to
            A as a repair.
  AB_build  two builder loops (Archmagi, SteveDesktop) on one shared plan. Tickets follow the world's seat route,
            an idle loop steals from the other, and an iteration can collide with the other loop's work.

Every Ralph parameter is ASSUMED with a range (RALPH_PRIORS). `ensemble` draws them per member from the range (keyed
by member id), `oat` sweeps each one from lo to hi with the others at their midpoints, and `report` writes
results.json and tables.md. Outputs go to RM_RALPH_SIM_OUT (default D:/ClaudeWork/rimmandrake/ralph_sim).
    ralph_loop_sim.py --structure park ensemble [--quota today|unlimited] [--members 240] [--budget-s 400]
    ralph_loop_sim.py --structure park oat [--members 40]
    ralph_loop_sim.py report
    ralph_loop_sim.py one --variant A [--member-idx 0]
Stdlib + numpy only. Offline.
"""
import argparse
import json
import os
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import rimflow_v3_sim as S  # noqa: E402

OUT = os.environ.get("RM_RALPH_SIM_OUT", "/mnt/d/ClaudeWork/rimmandrake/ralph_sim")
HOUR, DAY, WEEK = S.HOUR, S.DAY, S.WEEK

# keyed-randomness fields of our own, clear of rimflow_v3_sim's 1..36
(F_ROFF, F_RSPIRAL, F_RUNST, F_RDROP, F_BTEST, F_BHIT, F_BBLIND, F_BFR, F_BDUR, F_COLL, F_SPIN, F_RTHETA,
 F_RVER) = range(101, 114)

# name: (lo, hi, what it stands for). All ASSUMED: nothing in the v2 data measures them.
RALPH_PRIORS = {
    "r_restart_s": (30, 240, "wall seconds per iteration to start claude -p and read the stack (PROMPT, spec index, "
                             "plan, AGENT.md)"),
    "r_ctx_ite": (60e3, 300e3, "ITE of that per-iteration stack load"),
    "r_dur_mult": (0.7, 1.5, "wall time of one context doing a ticket's helper work in series, against the sum of "
                             "v2's helper wall times (no brief or handoff; but nothing runs in parallel)"),
    "r_ite_mult": (0.6, 1.2, "ITE of that work against the v2 helpers' ITE (no duplicated briefing; but one growing "
                             "context)"),
    "r_quick_ite": (50e3, 300e3, "ITE of a quick ticket's work on top of the stack load"),
    "r_mu_mult": (0.8, 1.6, "defects per ticket against v2: placeholder and duplicate implementations (Huntley's "
                            "'Achilles heel') against no handoff loss"),
    "r_bp": (0.0, 0.3, "extra share of visible defects caught because every iteration MUST pass selftests, "
                       "validate_patch and the build before it commits (combined with v2's s_self)"),
    "r_verify_mult": (0.6, 1.1, "share of v2's live-verify coverage loop A keeps (it holds the one bridge itself, "
                                "between builds)"),
    "r_p_off": (0.03, 0.20, "share of iterations that commit nothing useful (wrong item, unfinished, reverted)"),
    "r_p_spiral": (0.05, 0.40, "given an off-track iteration, the chance the loop locks into repeating it"),
    "r_unstick_h": (0.2, 2.0, "rate per hour at which a spiral ends by itself (a fresh context, plan regeneration)"),
    "r_status_mult": (0.3, 1.2, "his status questions against v2 (the plan file and git log are readable; nothing "
                                "reports to him)"),
    "r_proc_keep": (0.2, 0.7, "share of process-class tickets that still exist when there is no factory to maintain"),
    "r_ledger_commits": (0.0, 1.0, "bookkeeping commits per close (the plan update usually rides in the work commit)"),
    "r_bg_mult": (0.4, 1.0, "share of v2's background ITE (art-eval headless, hooks, timers) still running"),
    "b_test_min": (10, 45, "SteveDesktop wall minutes per live test job, including the load (lane B, AB_test)"),
    "b_test_ite": (100e3, 600e3, "ITE per live test job (lane B)"),
    "b_p_test": (0.5, 0.95, "share of product closes that B tests live"),
    "b_s_mult": (0.8, 1.3, "B's sensitivity against the calibrated rig sensitivity s_rig"),
    "b_blind": (0.0, 0.3, "chance that B's full-list live run sees a defect every shared check misses"),
    "b_collide": (0.0, 0.08, "AB_build: chance an iteration duplicates or breaks the other loop's work"),
}
VARIANTS = ("A", "AB_test", "AB_build")
V3_COMPARE = ("v2", "v3.0", "v3.4")
WORK = ["sound_prod_d", "accepted_prod_d", "escapes_wk", "defect_frac", "rework_share", "nudges_d", "steers_d",
        "cards_waiting_3d", "owner_resolve_med_d", "ite_week", "blocked_h", "proc_share", "done_d", "filed_d",
        "iters_d", "wasted_share", "prod_q_end", "b_q_end", "idle_min_d_FOUNDRY"]


def mid_rp():
    return {k: (lo + hi) / 2 for k, (lo, hi, _) in RALPH_PRIORS.items()}


def draw_rp(member, seed=777):
    keys = sorted(RALPH_PRIORS)
    return {k: RALPH_PRIORS[k][0] + (RALPH_PRIORS[k][1] - RALPH_PRIORS[k][0]) * S.u01(seed, F_RTHETA, member, i)
            for i, k in enumerate(keys)}


class RalphSim(S.Sim):
    def __init__(self, P, theta, variant, rp, seed, weeks=4, quotas=None):
        assert variant in VARIANTS, variant
        th = dict(theta)                      # never mutate the caller's member theta
        th["mu_prod"] *= rp["r_mu_mult"]
        th["mu_proc"] *= rp["r_mu_mult"]
        th["s_self"] = 1 - (1 - th["s_self"]) * (1 - rp["r_bp"])
        th["kappa"] = 0.0                     # one context at a time: no concurrency defects
        th["lam_status_h"] *= rp["r_status_mult"]
        th["commits_ledger"] = rp["r_ledger_commits"]
        super().__init__(P, th, S.policy_cfg(P, "v2"), seed, weeks=weeks, quotas=quotas, warm_weeks=0)
        fx = dict(self.fx)
        fx["seat_ite_per_close"] = {"value": 0.0}             # no orchestrating window: its cost is r_ctx_ite
        fx["background_ite_week"] = {"value": self.fx["background_ite_week"]["value"] * rp["r_bg_mult"]}
        fx["p_verify"] = {"value": self.fx["p_verify"]["value"] * rp["r_verify_mult"]}
        self.fx = fx
        self.variant, self.rp = variant, rp
        self.lanes = ("FOUNDRY", "BENCH") if variant == "AB_build" else ("FOUNDRY",)
        self.iter_n = {n: 0 for n in S.SEATS}
        self.off = {}                         # id(ticket) -> this iteration went off-track
        self.tested = set()                   # id(ticket) B has passed
        self.overlap = 0
        self.inflight = {n: 0 for n in S.SEATS}

    # ---- routing: the world's seat route picks the work's cost table; the lane is the loop that does it
    def lane(self, tk):
        return tk.seat if tk.seat in self.lanes else self.lanes[0]

    def file_ticket(self, t, key, cls, origin, linked=False):
        if cls == "process" and origin in ("owner", "agent") and \
                S.u01(self.seed, F_RDROP, key) >= self.rp["r_proc_keep"]:
            self.add(t, "proc_dropped")       # factory upkeep that has no factory to keep up
            return
        super().file_ticket(t, key, cls, origin, linked)

    def enqueue(self, t, tk, front=False):
        if tk.seat is None:
            tk.seat = "FOUNDRY" if S.u01(self.seed, S.F_ROUTE, tk.key) < self.fx["foundry_share"]["value"] else "BENCH"
            tk.quick = tk.cls != "rework" and S.u01(self.seed, S.F_QUICK, tk.key) < self.th["p_quick"]
        s = self.seats[self.lane(tk)]
        if front:
            s.q_hi.append(tk)
        elif tk.cls == "process":
            s.q_proc.append(tk)
        else:
            s.q_prod.append(tk)
        if s.stalled:
            self.set_idle(s, t)
            self.schedule_notice(s, t)
        self.try_work(s, t)

    def pull(self, s, t):
        """an empty lane takes the oldest parked ticket (pull structure; parked lists are empty under park), then the
        start-of-run queue of a window that has no loop (A, AB_test), then (AB_build) the other loop's work"""
        pools = [self.parked[s.name]] + [self.parked[n] for n in S.SEATS if n != s.name and n not in self.lanes]
        pools = [q for q in pools if q]
        if pools:
            q = min(pools, key=lambda q: q[0].t_filed)
            self.add(t, "pulled_from_backlog")
            return q.popleft()
        for n in S.SEATS:
            o = self.seats[n]
            if n != s.name:
                for q in (o.q_hi, o.q_prod, o.q_proc):
                    if q:
                        self.add(t, "stolen" if n in self.lanes else "inherited")
                        return q.popleft()
        return None

    # ---- the loop
    def iter_cost(self, tk):
        rp, th = self.rp, self.th
        dur, ite = rp["r_restart_s"], rp["r_ctx_ite"]
        if tk.quick and tk.attempt == 0:
            return dur + th["quick_min"] * 60 * rp["r_dur_mult"], ite + rp["r_quick_ite"]
        nh = 1 + S.poisson(max(0.0, th["helpers_per_job"] - 1), self.seed, S.F_NHELP, tk.key, tk.attempt)
        for i in range(nh):                  # the SAME keyed draws v2's helpers got for this ticket
            u = S.u01(self.seed, S.F_HELP, tk.key, tk.attempt, i)
            dur += S.qsample(self.fx["helper_dur_q"][tk.seat], u) * rp["r_dur_mult"]
            ite += S.qsample(self.fx["helper_ite_q"][tk.seat], u) * rp["r_ite_mult"]
        return dur, ite

    def try_work(self, s, t):
        if s.name not in self.lanes or s.serial_busy or self.all_blocked:
            return
        if s.stalled:                         # spiralling: it keeps iterating and keeps paying
            self.iter_n[s.name] += 1
            u = S.u01(self.seed, F_SPIN, S.SEATS.index(s.name), self.iter_n[s.name])
            dur = self.rp["r_restart_s"] + S.qsample(self.fx["helper_dur_q"][s.name], u) * self.rp["r_dur_mult"]
            ite = self.rp["r_ctx_ite"] + S.qsample(self.fx["helper_ite_q"][s.name], u) * self.rp["r_ite_mult"]
            self.begin(s, t, dur, ite, "launch", None, wasted=True)
            return
        tk = self.pop(s, t)
        if tk is None:
            tk = self.pull(s, t)
        if tk is None:
            return                            # the loop finds nothing to do; the next filing wakes it
        self.iter_n[s.name] += 1
        self.off[id(tk)] = S.u01(self.seed, F_ROFF, S.SEATS.index(s.name), self.iter_n[s.name]) < self.rp["r_p_off"]
        dur, ite = self.iter_cost(tk)
        self.begin(s, t, dur, ite, "quick_done", tk)

    def begin(self, s, t, dur, ite, kind, tk, wasted=False):
        self.inflight[s.name] += 1            # counted apart from serial_busy, so the selftest can see a broken gate
        if self.inflight[s.name] > 1:
            self.overlap += 1                 # a loop must never run two iterations at once
        s.serial_busy = True
        self.charge(t, ite, "ralph_iter")
        self.add(t, "iters")
        if wasted:
            self.add(t, "iters_wasted")
        self.push(t + dur, kind, s.name, tk, 0)

    def launch(self, t, s, tk, i):            # a spiral iteration finished: nothing to show for it
        self.inflight[s.name] -= 1
        s.serial_busy = False
        self.try_work(s, t)

    def after_completion(self, s, t):
        s.completions += 1
        self.try_work(s, t)

    def complete(self, t, s, tk):
        self.inflight[s.name] -= 1
        rp = self.rp
        if self.off.pop(id(tk), False):
            self.add(t, "iters_wasted")
            s.q_hi.appendleft(tk)             # still the top item
            if S.u01(self.seed, F_RSPIRAL, S.SEATS.index(s.name), self.iter_n[s.name]) < rp["r_p_spiral"]:
                self.spiral(s, t)
            return
        if self.variant == "AB_build":
            other = [n for n in self.lanes if n != s.name][0]
            if self.seats[other].serial_busy and S.u01(self.seed, F_COLL, S.SEATS.index(s.name), self.iter_n[s.name]) < rp["b_collide"]:
                self.add(t, "collisions")
                self.add(t, "iters_wasted")
                s.q_hi.appendleft(tk)
                return
        super().complete(t, s, tk)

    def spiral(self, s, t):
        s.stalled = True
        s.stall_n += 1
        s.stall_t = t
        s.notice_sched = False
        self.add(t, "spirals")
        self.push(t + S.expo(HOUR / self.rp["r_unstick_h"], self.seed, F_RUNST, S.SEATS.index(s.name), s.stall_n),
                  "resume", s.name, s.stall_n, "self")
        self.schedule_notice(s, t)            # the owner "sits on the loop" with v2's calibrated watching habit
        self.set_idle(s, t)

    def resume(self, s, t, cause):
        if s.stalled and cause == "owner":
            self.add(t, "steers")
            self.add(t, "owner_att_min", 4.0)  # he edits PROMPT.md or the plan, on top of base's 1 min
        super().resume(s, t, cause)

    # ---- lane B on SteveDesktop: live tests (AB_test), reusing the base model's rig events
    def close(self, t, tk):
        if self.variant == "AB_test" and tk.cls != "process" and id(tk) not in self.tested and tk.attempt < 3 \
                and S.u01(self.seed, F_BTEST, tk.key, tk.attempt) < self.rp["b_p_test"]:
            self.arb_q.append((t, tk))
            self.add(t, "b_in")
            self.arb_start(t)
            return
        super().close(t, tk)

    def arb_start(self, t):
        while self.arb_busy < 1 and self.arb_q:
            _, tk = self.arb_q.popleft()
            self.arb_busy += 1
            self.charge(t, self.rp["b_test_ite"], "ralph_b")
            dur = self.rp["b_test_min"] * 60 * (0.5 + S.u01(self.seed, F_BDUR, tk.key, tk.attempt)) \
                / (1 - self.rp["r_p_off"])
            self.add(t, "b_min", dur / 60)
            self.push(t + dur, "arb_done", tk, len(self.arb_q))

    def arb_done(self, t, tk, qlen):
        th, rp = self.th, self.rp
        self.arb_busy -= 1
        sens = min(0.98, th["s_rig"] * rp["b_s_mult"])
        hit = [d for j, d in enumerate(tk.defects) if d[0] == 0 and (
            (not d[1] and S.u01(self.seed, F_BHIT, tk.key, tk.attempt, j) < sens)
            or (d[1] and S.u01(self.seed, F_BBLIND, tk.key, tk.attempt, j) < rp["b_blind"]))]
        fr = S.u01(self.seed, F_BFR, tk.key, tk.attempt) < th["fr_rig"]
        self.add(t, "b_verdicts")
        if hit or fr:
            self.add(t, "b_reject")
            self.repair(t, tk, hit)
        else:
            self.tested.add(id(tk))
            tk.accepted = True                # tested live by a second loop; NOT an independent blind judge
            S.Sim.close(self, t, tk)
        self.arb_start(t)

    def summaries(self):
        out = super().summaries()
        for w, r in enumerate(out):
            m = self.m[w]
            r["iters_d"] = m.get("iters", 0.0) / 7
            r["wasted_share"] = m.get("iters_wasted", 0.0) / max(1.0, m.get("iters", 0.0))
            r["steers_d"] = m.get("steers", 0.0) / 7
            r["spirals_wk"] = m.get("spirals", 0.0)
            r["proc_dropped_d"] = m.get("proc_dropped", 0.0) / 7
            r["b_q_end"] = m.get("arb_q_end", 0.0)
            r["collisions_wk"] = m.get("collisions", 0.0)
        return out


# ---------------------------------------------------------------- running
def add_derived(r):
    r = dict(r)
    esc, snd = r.get("escapes_wk", 0.0) or 0.0, (r.get("sound_prod_d", 0.0) or 0.0) * 7
    r["defect_frac"] = esc / max(1.0, esc + snd)
    r.setdefault("steers_d", 0.0)
    r.setdefault("iters_d", 0.0)
    r.setdefault("wasted_share", 0.0)
    r.setdefault("b_q_end", 0.0)
    return r


def run_ralph(P, m, seed, variant, rp, weeks=4, unlimited=False):
    q = None if unlimited else dict(m["quotas"])
    return [add_derived(w) for w in RalphSim(P, m["theta"], variant, rp, seed, weeks=weeks, quotas=q).run()]


def run_v3(P, m, seed, pol, weeks=4, unlimited=False):
    _, res = S.run_policy(P, m, seed, pol, {"_unlimited": True} if unlimited else {}, weeks=weeks)
    out = [add_derived(w) for w in res]
    for w in out:
        w["b_q_end"] = 0.0
    return out


def wmean(rows, k):
    vals = [rows[w].get(k) for w in range(1, len(rows))]
    vals = [v for v in vals if v is not None and v == v]
    return float(np.mean(vals)) if vals else float("nan")


def compact(rows):
    return {k: round(wmean(rows, k), 5) for k in WORK}


def members(structure, n):
    S.STRUCTURE = structure
    return S.load_members(S.OUT, max_n=240)[:n]


def cmd_ensemble(a):
    P = S.load_params()
    ms = members(a.structure, a.members)
    path = os.path.join(a.out, f"ens_{a.structure}_{a.quota}.jsonl")
    done = {json.loads(l)["member"] for l in open(path)} if os.path.exists(path) else set()
    t0 = time.time()
    with open(path, "a") as fh:
        for m in ms:
            if m["member"] in done:
                continue
            if time.time() - t0 > a.budget_s:
                print("budget reached")
                break
            seed = 50000 + m["member"] * 97            # the seed rimflow_v3_sim's experiments used
            rp = draw_rp(m["member"])
            rows = {p: compact(run_v3(P, m, seed, p, unlimited=a.quota == "unlimited")) for p in V3_COMPARE}
            for v in VARIANTS:
                rows[v] = compact(run_ralph(P, m, seed, v, rp, unlimited=a.quota == "unlimited"))
            fh.write(json.dumps({"member": m["member"], "seed": seed, "rp": rp, "rows": rows}) + "\n")
    n = sum(1 for _ in open(path))
    print(f"ensemble {a.structure}/{a.quota}: {n} members on file, {time.time() - t0:.0f}s")


OAT_VARIANTS = ("A", "AB_test")
OAT_METRICS = ("sound_prod_d", "nudges_d", "ite_week", "escapes_wk")


def cmd_oat(a):
    """one-at-a-time: each Ralph parameter at lo and at hi, the rest at their midpoints, on the same members"""
    P = S.load_params()
    ms = members(a.structure, a.members)
    path = os.path.join(a.out, f"oat_{a.structure}.jsonl")
    done = {(r["member"], r["param"], r["end"]) for r in map(json.loads, open(path))} if os.path.exists(path) else set()
    t0 = time.time()
    jobs = [(m, "_mid", "mid") for m in ms] + [(m, p, e) for p in sorted(RALPH_PRIORS) for e in ("lo", "hi") for m in ms]
    with open(path, "a") as fh:
        for m, p, e in jobs:
            if (m["member"], p, e) in done:
                continue
            if time.time() - t0 > a.budget_s:
                print("budget reached")
                break
            rp = mid_rp()
            if p != "_mid":
                rp[p] = RALPH_PRIORS[p][0 if e == "lo" else 1]
            seed = 50000 + m["member"] * 97
            rows = {v: {k: round(wmean(run_ralph(P, m, seed, v, rp), k), 5) for k in OAT_METRICS} for v in OAT_VARIANTS}
            fh.write(json.dumps({"member": m["member"], "param": p, "end": e, "rows": rows}) + "\n")
    print(f"oat {a.structure}: {sum(1 for _ in open(path))} of {len(jobs)} rows, {time.time() - t0:.0f}s")


def pct(x):
    x = np.array([v for v in x if v == v], dtype=float)
    return [round(float(np.percentile(x, q)), 3) for q in (10, 50, 90)] if len(x) else None


def summarize_ensemble(path):
    recs = [json.loads(l) for l in open(path)]
    labels = list(recs[0]["rows"])
    res = {"n": len(recs), "levels": {}, "vs": {}, "splits": {}}
    for k in WORK:
        res["levels"][k] = {lab: pct([r["rows"][lab][k] for r in recs]) for lab in labels}
    for base in ("v2", "v3.4"):
        res["vs"][base] = {}
        for lab in VARIANTS:
            res["vs"][base][lab] = {}
            for k in WORK:
                d = np.array([r["rows"][lab][k] - r["rows"][base][k] for r in recs], dtype=float)
                d = d[~np.isnan(d)]
                if len(d):
                    res["vs"][base][lab][k] = {"median": round(float(np.median(d)), 4),
                                               "share_up": round(float(np.mean(d > 1e-9)), 3)}
    # which assumed Ralph parameters decide the Ralph-minus-v2 delta (Spearman over members)
    for lab in VARIANTS:
        res["splits"][lab] = {}
        for k in ("sound_prod_d", "nudges_d", "ite_week"):
            d = np.array([r["rows"][lab][k] - r["rows"]["v2"][k] for r in recs], dtype=float)
            ok = ~np.isnan(d)
            if ok.sum() < 8:
                continue
            rd = np.argsort(np.argsort(d[ok]))
            cors = []
            for p in sorted(RALPH_PRIORS):
                x = np.array([r["rp"][p] for r in recs])[ok]
                c = float(np.corrcoef(np.argsort(np.argsort(x)), rd)[0, 1])
                cors.append((abs(c), p, round(c, 2)))
            cors.sort(reverse=True)
            res["splits"][lab][k] = [(p, c) for _, p, c in cors[:5]]
    return res


def summarize_oat(path):
    recs = [json.loads(l) for l in open(path)]
    mid = {r["member"]: r["rows"] for r in recs if r["param"] == "_mid"}
    out = {}
    for v in OAT_VARIANTS:
        out[v] = {}
        for k in OAT_METRICS:
            out[v][k] = {"mid_median": round(float(np.median([x[v][k] for x in mid.values()])), 3), "swing": []}
            for p in sorted(RALPH_PRIORS):
                ends = {}
                for e in ("lo", "hi"):
                    d = [r["rows"][v][k] - mid[r["member"]][v][k] for r in recs
                         if r["param"] == p and r["end"] == e and r["member"] in mid]
                    ends[e] = round(float(np.median(d)), 3) if d else float("nan")
                out[v][k]["swing"].append((p, ends["lo"], ends["hi"], round(abs(ends["hi"] - ends["lo"]), 3)))
            out[v][k]["swing"].sort(key=lambda x: -x[3])
    return out


def fmt(v, k):
    if v is None:
        return "-"
    if k == "ite_week":
        return "/".join(f"{x / 1e9:.2f}" for x in v) + "G"
    return "/".join(f"{x:.3g}" for x in v)


def cmd_report(a):
    rep = {"ensemble": {}, "oat": {}}
    lines = ["# Ralph sim tables (p10/p50/p90 over members; weeks 1-3 of 4)", ""]
    for st in ("park", "pull"):
        for q in ("today", "unlimited"):
            p = os.path.join(a.out, f"ens_{st}_{q}.jsonl")
            if not os.path.exists(p):
                continue
            s = summarize_ensemble(p)
            rep["ensemble"][f"{st}_{q}"] = s
            labs = list(s["levels"]["sound_prod_d"])
            lines += [f"## {st}, quotas {q} (n={s['n']})", "", "| metric | " + " | ".join(labs) + " |",
                      "|---|" + "---|" * len(labs)]
            for k in WORK:
                lines.append(f"| {k} | " + " | ".join(fmt(s["levels"][k][lab], k) for lab in labs) + " |")
            lines += ["", "Paired median delta (share of members where it is higher):", "",
                      "| metric | " + " | ".join(f"{v}-{b}" for b in ("v2", "v3.4") for v in VARIANTS) + " |",
                      "|---|" + "---|" * (2 * len(VARIANTS))]
            for k in WORK:
                cells = []
                for b in ("v2", "v3.4"):
                    for v in VARIANTS:
                        c = s["vs"][b][v].get(k)
                        cells.append("-" if not c else f"{c['median']:.3g} ({c['share_up']:.0%})")
                lines.append(f"| {k} | " + " | ".join(cells) + " |")
            lines += ["", "Parameters that split Ralph-minus-v2 (Spearman, top 5):", ""]
            for v, d in s["splits"].items():
                for k, lst in d.items():
                    lines.append(f"- {v} {k}: " + ", ".join(f"{p} {c:+.2f}" for p, c in lst))
            lines.append("")
        p = os.path.join(a.out, f"oat_{st}.jsonl")
        if os.path.exists(p):
            o = summarize_oat(p)
            rep["oat"][st] = o
            lines += [f"## One-at-a-time swings, {st} (median delta from all-midpoints at lo / hi)", ""]
            for v, d in o.items():
                for k, x in d.items():
                    top = ", ".join(f"{pp} {lo:+.3g}/{hi:+.3g}" for pp, lo, hi, _ in x["swing"][:6])
                    lines.append(f"- {v} {k} (mid {x['mid_median']:.4g}): {top}")
            lines.append("")
    json.dump(rep, open(os.path.join(a.out, "results.json"), "w"), indent=1)
    open(os.path.join(a.out, "tables.md"), "w").write("\n".join(lines) + "\n")
    print("wrote", os.path.join(a.out, "results.json"), "and tables.md")


def cmd_one(a):
    P = S.load_params()
    m = members(a.structure, a.member_idx + 1)[a.member_idx]
    seed = 50000 + m["member"] * 97
    rows = run_v3(P, m, seed, a.variant) if a.variant in V3_COMPARE else run_ralph(P, m, seed, a.variant, mid_rp())
    print(json.dumps(compact(rows), indent=1))


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--out", default=OUT)
    ap.add_argument("--structure", choices=("park", "pull"), default="park")
    sub = ap.add_subparsers(dest="cmd", required=True)
    e = sub.add_parser("ensemble")
    e.add_argument("--quota", choices=("today", "unlimited"), default="today")
    e.add_argument("--members", type=int, default=240)
    e.add_argument("--budget-s", type=float, default=400)
    o = sub.add_parser("oat")
    o.add_argument("--members", type=int, default=40)
    o.add_argument("--budget-s", type=float, default=400)
    sub.add_parser("report")
    one = sub.add_parser("one")
    one.add_argument("--variant", default="A", choices=VARIANTS + V3_COMPARE)
    one.add_argument("--member-idx", type=int, default=0)
    a = ap.parse_args(argv)
    os.makedirs(a.out, exist_ok=True)
    {"ensemble": cmd_ensemble, "oat": cmd_oat, "report": cmd_report, "one": cmd_one}[a.cmd](a)


if __name__ == "__main__":
    main()
