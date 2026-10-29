#!/usr/bin/env python3
"""testpilot_sim.py: the owner's three-agent proposal (Foundry + TestPilot + Conductor) in the same bottle as the zoo.
Item TESTPILOT_DESIGN_PROOF_BEFORE_RELOAD; design design/RimMandrake/testpilot_design_opus_2026-10-29.md.

A sibling of ralph_loop_sim.py (imported, never edited: another helper owns it). It keeps the calibrated outside
world of rimflow_v3_sim.py (owner presence, arrivals, ticket classes, hidden defects, discovery, quotas) and Ralph
variant C+sub's builders (two Ralph builder loops split by area, bounded subagents), and replaces C's live runners
with two TestPilots plus a blind critic gate.

Variants
  TP    the proposal as he wrote it. Builder output goes to a blind critic; ping-pong until the critic passes (no
        round limit is stated: we cap at 6, then the Conductor simplifies it, an owner-visible escalation). The pilot
        may refuse the evidence: it writes a test plan and a SECOND critic reviews plan + code. Live: one game per
        machine (SteveDesktop always; Archmagi unless the owner is playing), many tests per load, harness faults
        hot-fixed in session (savegame edit / bridge restage), mod fixes built by pilot subagents while testing goes on
        (no independent review of the fix), the pilot judges whether follow-on tests are still valid after a failure,
        reload only when no valid live test remains (or the session is dead). The pilot is one long-lived context
        (sharpness decays, each call re-sends a growing context) until it hands off at a context limit. The full-list
        clash check runs once per item, one full-list load each.
  TP+   the improved design (doc section 3). Critic cap 2 rounds, then one automatic simplify/split pass, then 2 more,
        then park to the Conductor. One review: the plan is written from the spec while the item is built and the
        critic reviews plan + code together. Every fix gets a blind diff check. Every test is a fresh pilot pass
        (Ralph: one test plan per pass; the session lives in a file, the game stays up); a no-LLM canary runs between
        tests, so a poisoned session is caught by the script, not by the pilot's judgment. Written reload rule R1-R3
        (doc 3.4). The full-list check is batched: one full-list load covers every item waiting for it.

Metrics added to the zoo's: accepted_strict_d (owner's definition: an independent blind check AND, if the item is a
game change, a live test), sound_acc_d (accepted_strict with no latent defect at close), reloads_per_acc,
live_prod_min_d (valid test minutes), game_busy_min_d, pilot_idle_share, crit_rounds_mean, escalations_wk.
For zoo members: v2/v3.0 have neither gate on one item (strict 0); v3.4's Arbiter is a blind check, so its strict
count is Arbiter-accepted items that are not game changes; Ralph AB_test/C live-test by a second loop with no blind
check (strict 0; their accepted_prod_d is "accepted_any").

Every new parameter is ASSUMED with a range (TP_PRIORS) except where a measurement is named.
    testpilot_sim.py ensemble [--members 120] [--budget-s 480]
    testpilot_sim.py oat [--members 12] [--budget-s 480]
    testpilot_sim.py report
    testpilot_sim.py one --variant TP+ [--member-idx 0]
Outputs go to RM_TP_SIM_OUT (default D:/ClaudeWork/rimmandrake/testpilot/opus/sim). Stdlib + numpy only. Offline.
"""
import argparse
import collections
import hashlib
import json
import os
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import rimflow_v3_sim as S  # noqa: E402
import ralph_loop_sim as R  # noqa: E402

OUT = os.environ.get("RM_TP_SIM_OUT", "/mnt/d/ClaudeWork/rimmandrake/testpilot/opus/sim")
HOUR, DAY, WEEK = S.HOUR, S.DAY, S.WEEK
(F_BIG, F_CRIT, F_CRITFR, F_PLAY, F_TDUR, F_CRASH, F_INV, F_HOT, F_THIT, F_TBLIND, F_TFR, F_FOLLOW, F_MISJ, F_VOID,
 F_CAT, F_FIX, F_FIXREG, F_FIXCRIT, F_CS, F_THETA) = range(201, 221)

# name: (lo, hi, what). All ASSUMED unless the text names a measurement.
TP_PRIORS = {
    "crit_s": (0.3, 0.7, "blind critic sensitivity to a defect visible to shared checks (one round)"),
    "crit_fr": (0.05, 0.25, "critic reject with no real defect (taste, a 'new P1') on a small item"),
    "crit_fr_big": (0.3, 0.7, "the same on a large multi-purpose item; today's goodbye/findings-fold did not converge "
                              "in 3-4 rounds (brief, lessons)"),
    "p_big": (0.1, 0.3, "share of product items that are large/multi-purpose (fixed per item)"),
    "crit_ite": (80e3, 250e3, "ITE per critic round (fresh blind context reads spec, diff, evidence)"),
    "crit_min": (5, 20, "wall minutes per critic round"),
    "crit2_mult": (0.2, 0.6, "TP: second review (plan + code) sensitivity against crit_s, on what the first missed"),
    "plan_ite": (50e3, 200e3, "ITE to write one item's test plan"),
    "plan_min": (5, 20, "TP: wall minutes from critic pass to an approved plan (written after the critic)"),
    "reload_min": (1.5, 5.0, "minimal-list reload: close, deploy, 22 s load (load-round SKILL:14), quicktest colony "
                             "5-30 s (debug-testing SKILL:10,30), canary, bridge reconnect"),
    "build_min": (1.0, 4.0, "extra minutes when the deploy set holds a C# DLL (winbuild; DLL only in the shutdown "
                            "window, rimworld-deploy SKILL:195)"),
    "p_cs": (0.2, 0.5, "share of items/fixes that touch C#"),
    "full_load_min": (15, 30, "owner's full list load (brief: about 15 min; load-round SKILL:14 says ~25)"),
    "test_min": (3, 15, "wall minutes per item's live test plan inside a loaded session"),
    "clash_min": (2, 6, "TP+: per-item clash check inside a batched full-list session"),
    "test_ite": (40e3, 200e3, "ITE per live test (bridge calls, screenshots, log reads)"),
    "pass_stack_ite": (30e3, 120e3, "TP+: stack load of a fresh pilot pass (session file, plan, AGENTS.md)"),
    "ctx_growth": (0.02, 0.10, "TP: per-test growth of the long pilot's per-call ITE (it re-sends its context)"),
    "ctx_decay": (0.0, 0.02, "TP: per-test loss of the long pilot's sensitivity since its last handoff"),
    "handoff_n": (15, 40, "TP: tests before the long pilot's context forces a handoff"),
    "handoff_min": (3, 10, "TP: wall minutes for that handoff (the game stays up)"),
    "p_crash": (0.005, 0.04, "a test crashes or menu-drops the game (debug-testing SKILL:98: a map-gen crash kills "
                             "the whole process)"),
    "p_invalid": (0.05, 0.15, "a test is void for HARNESS/SITE reasons (testq day one: 10 INVALID of 109 = 0.09, "
                              "as_built 2.15; harness SKILL:12-18 eleven of twelve findings were harness/site)"),
    "p_hot_ok": (0.5, 0.9, "a void test is rescued in session by a hot harness/site fix (savegame edit, restage)"),
    "hot_min": (3, 12, "minutes for that in-session harness/site fix"),
    "follow_ok": (0.6, 0.95, "after a MOD failure the session is still a valid place for the next item's test"),
    "p_misjudge": (0.05, 0.3, "the pilot misses that its session is poisoned and keeps testing"),
    "canary_catch": (0.7, 0.95, "TP+: share of poisoned sessions the no-LLM canary between tests catches"),
    "canary_min": (0.3, 1.5, "TP+: canary minutes per test"),
    "void_pass": (0.2, 0.6, "a test run in an unnoticed poisoned session reads PASS (else FAIL)"),
    "p_cat": (0.01, 0.05, "a live failure is a catastrophic spec mismatch: back to Foundry via the Conductor"),
    "fix_min": (10, 40, "wall minutes for a pilot subagent to build a fix (gate run included)"),
    "fix_ite": (100e3, 400e3, "ITE of that fix"),
    "fresh_bonus": (0.0, 0.15, "extra fix success because the context is fresh and the game is up for live probes"),
    "fixcrit_ite": (30e3, 90e3, "TP+: blind diff check of a fix"),
    "play": (0.0, 0.2, "share of owner-present hours he is PLAYING on Archmagi (owner 2026-10-29: 'I don't play right "
                       "now')"),
    "esc_min": (3, 10, "owner minutes a Conductor escalation costs him (he sees it on the loop)"),
}
# design constants (not uncertain: they are the rules being compared)
CAP = {"TP": 6, "TP+": 2}         # critic rounds before escalation (TP) / simplify (TP+)
BATCH_MAX = 10                    # items loaded into one minimal session
LIVE_FAILS_PARK = 3               # live failures before an item is parked with its evidence (as Ralph C)
TPP_K, TPP_W_MIN = 2, 45          # TP+ rule R3: >= K deployables and the oldest waited >= W minutes
TPP_FULL_N, TPP_FULL_WAIT_H = 4, 6  # TP+ batched full list: >= N items or the oldest waited >= H hours
# Round 2: GPT's independent design (/mnt/d/ClaudeWork/rimmandrake/testpilot/gpt_design.md) gives its own parameters.
# A scenario overrides prior RANGES (then drawn the same keyed way) and TP+ constants; the base scenario is round 1.
SCENARIOS = {
    "base": {},
    "gpt": {"priors": {"full_load_min": (17, 30),    # Q13 FULL excursion 22 (17-30): swap, load, restore
                       "reload_min": (1.0, 5.0),     # Q12 minimal restart 2 (1-5)
                       "pass_stack_ite": (8e3, 20e3)},  # P08 startup context 12k
            "const": {"K": 1, "W_MIN": 2, "AGE_MIN": 2,  # I-R04: a sealed repair ready and the P12 2-min drain expired
                      "FULL_N": 2, "FULL_WAIT_H": 0.5}},  # P13: FULL batch of 2 or the oldest waited 30 min
    "gpt_guard": {"priors": "gpt", "const": {"K": 1, "W_MIN": 2, "AGE_MIN": 45, "FULL_N": 2, "FULL_WAIT_H": 0.5}},
    "gpt_1G": {"priors": "gpt", "const": "gpt", "budget_g": 1.0},   # C51: weekly budget 1.0G instead of ~1.9G
}
BASE_CONST = {"K": TPP_K, "W_MIN": TPP_W_MIN, "AGE_MIN": TPP_W_MIN, "FULL_N": TPP_FULL_N,
              "FULL_WAIT_H": TPP_FULL_WAIT_H}


def scenario(name):
    sc = SCENARIOS[name]
    pri = sc.get("priors", {})
    pri = SCENARIOS[pri]["priors"] if isinstance(pri, str) else pri
    con = sc.get("const", {})
    con = SCENARIOS[con]["const"] if isinstance(con, str) else con
    priors = {k: ((pri[k][0], pri[k][1], v[2]) if k in pri else v) for k, v in TP_PRIORS.items()}
    return priors, dict(BASE_CONST, **con), sc.get("budget_g")


def scale_quotas(q, budget_g):
    if budget_g is None or q is None:
        return q
    tot = sum(q.values())
    return {k: v * budget_g * 1e9 / tot for k, v in q.items()}


TP_VARIANTS = ("TP", "TP+")
ZOO = ("v2", "v3.4", "A", "AB_test", "C", "C+sub")
ALL = ZOO + TP_VARIANTS
METRICS = ["accepted_strict_d", "sound_acc_d", "accepted_prod_d", "sound_prod_d", "escapes_wk", "ite_week",
           "nudges_d", "owner_min_wk", "reloads_per_acc", "live_prod_min_d", "game_busy_min_d", "pilot_idle_share",
           "crit_rounds_mean", "escalations_wk", "b_parked_wk", "crashes_wk", "prod_q_end", "done_d"]


def fingerprint():
    h = hashlib.sha1(R.FP.encode())
    h.update(open(os.path.join(HERE, "testpilot_sim.py"), "rb").read().split(b"# " + b"=" * 40 + b" reporting")[0])
    return h.hexdigest()[:12]


def mid_tp(priors=None):
    return {k: (lo + hi) / 2 for k, (lo, hi, _) in (priors or TP_PRIORS).items()}


def draw_tp(member, seed=919, priors=None):
    return {k: lo + (hi - lo) * S.u01(seed, F_THETA, member, i)
            for i, (k, (lo, hi, _)) in enumerate(sorted((priors or TP_PRIORS).items()))}


def needs_test(sim, tk):
    """a game change that needs a live test: the SAME keyed item property Ralph AB_test/C use"""
    return tk.cls != "process" and S.u01(sim.seed, R.F_BTEST, tk.key) < sim.rp["b_p_test"]


class V3Strict(S.Sim):
    """v2/v3.x unchanged; counts the owner's accepted_strict on top (Arbiter blind check and no live test needed)."""
    def __init__(self, *a, rp=None, **k):
        self.rp = rp
        super().__init__(*a, **k)

    def close(self, t, tk):
        latent = any(d[0] == 0 for d in tk.defects)
        super().close(t, tk)
        if tk.cls != "process" and tk.accepted and not needs_test(self, tk):
            self.add(t, "acc_strict")
            if not latent:
                self.add(t, "sound_acc")


class TPSim(R.RalphSim):
    def __init__(self, P, theta, variant, rp, tp, seed, weeks=4, quotas=None, const=None):
        assert variant in TP_VARIANTS, variant
        super().__init__(P, theta, "C+sub", rp, seed, weeks=weeks, quotas=quotas)
        self.tpv, self.tp, self.plus = variant, tp, variant == "TP+"
        self.c = dict(BASE_CONST, **(const or {}))
        self.rounds = collections.Counter()     # critic rounds in the current phase (objects, never id())
        self.rounds_total = collections.Counter()
        self.simplified = set()
        self.crit_ok, self.tested_min, self.live_fails = set(), set(), collections.Counter()
        self.ready = collections.deque()        # (t_ready, tk): deployable, waiting for a minimal load
        self.full_q = collections.deque()       # (t, tk): passed minimal, waiting for the full-list check
        self.pilot = {r: {"state": "idle", "batch": collections.deque(), "sid": 0, "full": False, "n": 0,
                          "poison": False, "hidden": False, "cur": None, "t_idle": 0.0,
                          "run": 0, "t_up": 0.0} for r in ("S", "A")}
        self.idle_s = {"S": 0.0, "A": 0.0}
        self.avail_s = {"S": 0.0, "A": 0.0}
        self.viol = collections.Counter()       # invariant breaches; the selftest demands all zero
        self.max_rounds_phase = 0
        play = tp["play"]
        self.owner_busy = [self.present[h] and S.u01(seed, F_PLAY, h) < play for h in range(len(self.present))]

    # ---------------- gates before the game
    def big(self, tk):
        return tk not in self.simplified and S.u01(self.seed, F_BIG, tk.key) < self.tp["p_big"]

    def close(self, t, tk):
        if tk.cls == "process":
            return S.Sim.close(self, t, tk)
        if tk not in self.crit_ok:
            ite = self.tp["crit_ite"] * (1.25 if self.plus else 1.0)       # TP+: the critic reads the plan too
            self.charge(t, ite, "tp_crit")
            if self.plus:
                self.charge(t, self.tp["plan_ite"], "tp_plan")
            self.push(t + self.tp["crit_min"] * 60, "arb_done", tk, ("TP", "crit", 1))
            return
        if needs_test(self, tk) and tk not in self.tested_min:
            self.ready.append((t, tk))
            self.pump_all(t)
            return
        self.final(t, tk)

    def final(self, t, tk):
        if not tk.accepted:
            if tk not in self.crit_ok or (needs_test(self, tk) and tk not in self.tested_min):
                self.viol["accept_without_gates"] += 1
        tk.accepted = True
        latent = any(d[0] == 0 for d in tk.defects)
        S.Sim.close(self, t, tk)
        self.add(t, "acc_strict")
        if not latent:
            self.add(t, "sound_acc")

    def review(self, t, tk, sens, key):
        hit = [d for j, d in enumerate(tk.defects)
               if d[0] == 0 and not d[1] and S.u01(self.seed, F_CRIT, tk.key, tk.attempt, key, j) < sens]
        fr_p = self.tp["crit_fr_big"] if self.big(tk) else self.tp["crit_fr"]
        fr = S.u01(self.seed, F_CRITFR, tk.key, tk.attempt, key) < fr_p
        return hit, fr

    def crit_done(self, t, tk, stage):
        tp = self.tp
        sens = tp["crit_s"] if stage == 1 else tp["crit_s"] * tp["crit2_mult"]
        hit, fr = self.review(t, tk, sens, stage)
        self.rounds[tk] += 1
        self.rounds_total[tk] += 1
        self.add(t, "crit_rounds")
        self.max_rounds_phase = max(self.max_rounds_phase, self.rounds[tk])
        if not hit and not fr:
            if stage == 1 and not self.plus and needs_test(self, tk):      # TP: the pilot writes a plan, 2nd review
                self.charge(t, tp["plan_ite"] + tp["crit_ite"], "tp_plan")
                self.push(t + (tp["plan_min"] + tp["crit_min"]) * 60, "arb_done", tk, ("TP", "crit", 2))
                return
            self.add(t, "crit_pass")
            self.crit_ok.add(tk)
            self.rounds[tk] = 0
            self.close(t, tk)
            return
        self.add(t, "crit_reject")
        if self.rounds[tk] >= CAP[self.tpv]:
            self.rounds[tk] = 0
            if self.plus and tk not in self.simplified:                  # automatic simplify/split, no owner
                self.simplified.add(tk)
                self.add(t, "simplified")
            elif self.plus:                                              # did not converge after simplifying
                self.add(t, "b_parked")
                self.add(t, "escalations")
                self.add(t, "owner_att_min", tp["esc_min"])
                return
            else:                                                        # TP: the Conductor simplifies it
                self.simplified.add(tk)
                self.add(t, "escalations")
                self.add(t, "owner_att_min", tp["esc_min"])
                self.add(t, "nudges")
        self.repair(t, tk, hit)                                          # back to the builder lane, at the front

    # ---------------- the pilots
    def avail(self, r, t):
        return r == "S" or self.avail_a(t)

    def pump_all(self, t):
        for r in ("S", "A"):
            self.pump(r, t)

    def full_due(self, t):
        if not self.full_q:
            return False
        if not self.plus:
            return True
        return len(self.full_q) >= self.c["FULL_N"] or t - self.full_q[0][0] >= self.c["FULL_WAIT_H"] * HOUR

    def set_state(self, r, t, st):
        p = self.pilot[r]
        if p["state"] in ("idle", "up") and st not in ("idle", "up"):
            self.idle_s[r] += t - p["t_idle"]
        if st in ("idle", "up") and p["state"] not in ("idle", "up"):
            p["t_idle"] = t
        p["state"] = st

    def pump(self, r, t):
        p = self.pilot[r]
        if p["state"] not in ("idle", "up"):
            return
        if not self.avail(r, t):
            if r == "A" and not self.ra_wake:
                nt = self.next_avail_a(t)
                if nt is not None:
                    self.ra_wake = True
                    self.push(nt, "arb_done", None, ("TP", "wake", r))
            return
        if p["state"] == "up" and p["poison"]:
            return self.reload(r, t, "R1_session_dead")
        if p["state"] == "up" and self.plus and not p["full"] and p["batch"] and len(self.ready) >= self.c["K"] \
                and t - self.ready[0][0] >= self.c["W_MIN"] * 60 and t - p["t_up"] >= self.c["AGE_MIN"] * 60:
            return self.reload(r, t, "R3_deployables_waiting")
        if p["state"] == "up" and p["batch"]:
            return self.start_test(r, t)
        if self.full_due(t):
            return self.reload(r, t, "R2_no_valid_test" if p["state"] == "up" else "R0_cold", full=True)
        if self.ready:
            return self.reload(r, t, "R2_no_valid_test" if p["state"] == "up" else "R0_cold")
        if self.plus and self.full_q:                                    # the oldest-wait trigger, when it comes due
            wait = self.full_q[0][0] + self.c["FULL_WAIT_H"] * HOUR
            self.push(max(t + 60, wait), "arb_done", None, ("TP", "poke", r))

    def reload(self, r, t, rule, full=False):
        p, tp = self.pilot[r], self.tp
        for tk in reversed(p["batch"]):                                  # nothing in the old batch is lost
            (self.full_q if p["full"] else self.ready).appendleft((t, tk))
        p["batch"].clear()
        src = self.full_q if full else self.ready
        n = (1 if not self.plus else 30) if full else BATCH_MAX
        while src and len(p["batch"]) < n:
            p["batch"].append(src.popleft()[1])
        p["sid"] += 1
        p["full"], p["poison"], p["hidden"] = full, False, False
        self.add(t, "reloads")
        self.add(t, "reload_" + rule)
        if full:
            dur = tp["full_load_min"] * 60
            self.add(t, "full_loads")
        else:
            dur = tp["reload_min"] * 60
            if any(S.u01(self.seed, F_CS, tk.key, tk.attempt) < tp["p_cs"] for tk in p["batch"]):
                dur += tp["build_min"] * 60
        self.set_state(r, t, "loading")
        self.add(t, "game_busy_min", dur / 60)
        self.guard(r, t, dur, ("TP", "loaded", r, p["sid"]))

    def guard(self, r, t, dur, tag):
        """Archmagi: if the owner sits down to play before this step ends, the pilot yields and loses the session"""
        if r == "A":
            if self.owner_busy[min(int(t // HOUR), len(self.owner_busy) - 1)]:
                self.viol["archmagi_while_playing"] += 1
            tb = self.first_busy_after(t)
            if tb is not None and tb < t + dur:
                self.push(tb, "arb_done", None, ("TP", "yield", r, self.pilot[r]["sid"]))
                return
        self.push(t + dur, "arb_done", None, tag)

    def start_test(self, r, t):
        p, tp = self.pilot[r], self.tp
        tk = p["batch"].popleft()
        p["cur"] = tk
        p["run"] += 1                                                    # a re-run after a hot fix is a new draw
        u = S.u01(self.seed, F_TDUR, tk.key, tk.attempt, p["sid"])
        dur = ((tp["clash_min"] if (p["full"] and self.plus) else tp["test_min"]) * (0.5 + u)) * 60
        if self.plus:
            dur += tp["canary_min"] * 60 + self.rp["r_restart_s"]
            self.charge(t, tp["test_ite"] + tp["pass_stack_ite"], "tp_pilot")
        else:
            self.charge(t, tp["test_ite"] * (1 + tp["ctx_growth"] * p["n"]), "tp_pilot")
            p["n"] += 1
            if p["n"] >= tp["handoff_n"]:
                p["n"] = 0
                dur += tp["handoff_min"] * 60
                self.add(t, "handoffs")
        self.set_state(r, t, "testing")
        self.add(t, "game_busy_min", dur / 60)
        self.guard(r, t, dur, ("TP", "tested", r, p["sid"], dur))

    def test_done(self, r, t, sid, dur):
        p, tp = self.pilot[r], self.tp
        tk = p["cur"]
        p["cur"] = None
        self.set_state(r, t, "up")
        key = (tk.key, tk.attempt, sid, p["run"])
        if S.u01(self.seed, F_CRASH, *key) < tp["p_crash"]:              # the game is gone: void, not failed
            self.add(t, "crashes")
            (self.full_q if p["full"] else self.ready).appendleft((t, tk))
            p["poison"] = True
            return self.pump(r, t)
        if S.u01(self.seed, F_INV, *key) < tp["p_invalid"]:              # HARNESS/SITE: void
            self.add(t, "invalid")
            if S.u01(self.seed, F_HOT, *key) < tp["p_hot_ok"]:           # hot fix in session, then re-run
                self.add(t, "hot_fixes")
                self.add(t, "game_busy_min", tp["hot_min"])
                p["batch"].appendleft(tk)
                self.set_state(r, t, "testing")
                return self.guard(r, t, tp["hot_min"] * 60, ("TP", "hot", r, sid))
            (self.full_q if p["full"] else self.ready).appendleft((t, tk))
            p["poison"] = True
            return self.pump(r, t)
        if p["hidden"]:                                                  # an unnoticed poisoned session
            self.add(t, "void_counted")
            if S.u01(self.seed, F_VOID, *key) < tp["void_pass"]:
                return self.passed(r, t, tk)
            return self.failed(r, t, tk, [])
        self.add(t, "live_prod_min", dur / 60)
        sens = min(0.98, self.th["s_rig"] * self.rp["b_s_mult"])
        if not self.plus:
            sens *= max(0.5, 1 - tp["ctx_decay"] * p["n"])
        if p["full"]:      # the full list adds what only the real load order shows (Ralph b_blind)
            hit = [d for j, d in enumerate(tk.defects) if d[0] == 0 and d[1]
                   and S.u01(self.seed, F_TBLIND, *key, j) < self.rp["b_blind"]]
        else:
            hit = [d for j, d in enumerate(tk.defects) if d[0] == 0 and not d[1]
                   and S.u01(self.seed, F_THIT, *key, j) < sens]
        fr = S.u01(self.seed, F_TFR, *key) < self.th["fr_rig"]
        if hit or fr:
            return self.failed(r, t, tk, hit)
        return self.passed(r, t, tk)

    def passed(self, r, t, tk):
        p = self.pilot[r]
        self.add(t, "live_pass")
        if p["full"]:
            self.final(t, tk)
        else:
            self.tested_min.add(tk)
            self.full_q.append((t, tk))
        self.pump(r, t)

    def failed(self, r, t, tk, hit):
        p, tp = self.pilot[r], self.tp
        self.add(t, "live_fail")
        self.live_fails[tk] += 1
        self.tested_min.discard(tk)                                      # a source change voids the old PASS
        key = (tk.key, tk.attempt, p["sid"], p["run"])
        if self.live_fails[tk] >= LIVE_FAILS_PARK:
            self.add(t, "b_parked")
        elif S.u01(self.seed, F_CAT, *key) < tp["p_cat"]:
            self.add(t, "escalations")
            self.add(t, "owner_att_min", tp["esc_min"])
            self.crit_ok.discard(tk)
            self.repair(t, tk, hit)
        else:
            self.charge(t, tp["fix_ite"], "tp_fix")
            self.push(t + tp["fix_min"] * 60, "arb_done", tk, ("TP", "fix", hit, 1))
        if S.u01(self.seed, F_FOLLOW, *key) >= tp["follow_ok"]:          # the session is poisoned
            miss = tp["p_misjudge"] * ((1 - tp["canary_catch"]) if self.plus else 1.0)
            if S.u01(self.seed, F_MISJ, *key) < miss:
                p["hidden"] = True
            else:
                p["poison"] = True
        self.pump(r, t)

    def fix_done(self, t, tk, hit, n):
        tp, th = self.tp, self.th
        pf = min(0.98, th["p_fix"] + tp["fresh_bonus"])
        for j, d in enumerate(hit):
            if S.u01(self.seed, F_FIX, tk.key, tk.attempt, j) < pf:
                d[0] = 1
        tk.attempt += 1
        self.add(t, "fixes")
        mu = th["mu_prod"] * self.mu_mult * 0.3                          # a repair can regress (base model)
        for j in range(S.poisson(mu, self.seed, F_FIXREG, tk.key, tk.attempt)):
            tk.defects.append([0, S.u01(self.seed, F_FIXREG, tk.key, tk.attempt, j, 1) < th["b_shared"]])
        for j, d in enumerate(tk.defects):
            if d[0] == 0 and not d[1] and S.u01(self.seed, S.F_SELF, tk.key, tk.attempt, j) < th["s_self"]:
                d[0] = 1
        if self.plus:                                                    # blind diff check of the fix
            self.charge(t, tp["fixcrit_ite"], "tp_crit")
            h2 = [d for j, d in enumerate(tk.defects) if d[0] == 0 and not d[1]
                  and S.u01(self.seed, F_FIXCRIT, tk.key, tk.attempt, j) < tp["crit_s"]]
            if h2 and n < 2:
                self.charge(t, tp["fix_ite"], "tp_fix")
                self.push(t + tp["fix_min"] * 60, "arb_done", tk, ("TP", "fix", h2, n + 1))
                return
        self.ready.append((t, tk))
        self.pump_all(t)

    def arb_done(self, t, tk, tag):
        if not (isinstance(tag, tuple) and tag and tag[0] == "TP"):
            return super().arb_done(t, tk, tag)
        kind = tag[1]
        if kind == "crit":
            return self.crit_done(t, tk, tag[2])
        if kind == "fix":
            return self.fix_done(t, tk, tag[2], tag[3])
        if kind == "wake":
            self.ra_wake = False
            return self.pump(tag[2], t)
        if kind == "poke":
            return self.pump(tag[2], t)
        r = tag[2]
        p = self.pilot[r]
        if tag[3] != p["sid"]:
            return                                                       # an event of a session already lost
        if kind == "yield":                                              # the owner sat down to play on Archmagi
            self.add(t, "c_bumps")
            if p["cur"] is not None:
                p["batch"].appendleft(p["cur"])
                p["cur"] = None
            for tk2 in reversed(p["batch"]):
                (self.full_q if p["full"] else self.ready).appendleft((t, tk2))
            p["batch"].clear()
            p["sid"] += 1
            self.set_state(r, t, "idle")
            return self.pump(r, t)
        if kind == "loaded":
            p["t_up"] = t
            self.set_state(r, t, "up")
            return self.pump(r, t)
        if kind == "hot":
            self.set_state(r, t, "up")
            return self.pump(r, t)
        if kind == "tested":
            return self.test_done(r, t, tag[3], tag[4])

    def summaries(self):
        out = super().summaries()
        T = self.T_end
        for r in ("S", "A"):
            if self.pilot[r]["state"] in ("idle", "up"):
                self.idle_s[r] += T - self.pilot[r]["t_idle"]
        for w, row in enumerate(out):
            m = self.m[w]
            acc = m.get("acc_strict", 0.0)
            row["accepted_strict_d"] = acc / 7
            row["sound_acc_d"] = m.get("sound_acc", 0.0) / 7
            row["reloads_per_acc"] = m.get("reloads", 0.0) / max(1.0, acc)
            row["live_prod_min_d"] = m.get("live_prod_min", 0.0) / 7
            row["game_busy_min_d"] = m.get("game_busy_min", 0.0) / 7
            row["crit_rounds_mean"] = m.get("crit_rounds", 0.0) / max(1.0, m.get("crit_pass", 0.0))
            row["escalations_wk"] = m.get("escalations", 0.0)
            row["crashes_wk"] = m.get("crashes", 0.0)
            for k in ("reloads", "full_loads", "handoffs", "hot_fixes", "invalid", "void_counted", "simplified",
                      "live_fail", "live_pass", "fixes", "c_bumps"):
                row[k + "_wk"] = m.get(k, 0.0)
            for k in [k for k in m if k.startswith("reload_R")]:
                row[k + "_wk"] = m[k]
        busy_total = (self.T_end) * 2
        idle = (self.idle_s["S"] + self.idle_s["A"]) / busy_total
        for row in out:
            row["pilot_idle_share"] = idle
            row["tp_viol"] = sum(self.viol.values())
            row["max_rounds_phase"] = self.max_rounds_phase
        return out


# ---------------------------------------------------------------- running
def zoo_rows(P, m, seed, v, rp, unlimited=False, budget_g=None):
    q = None if unlimited else scale_quotas(dict(m["quotas"]), budget_g)
    if v in ("v2", "v3.0", "v3.4"):
        sim = V3Strict(P, m["theta"], S.policy_cfg(P, v), seed, weeks=4, quotas=q, warm_weeks=1, rp=rp)
        rows = sim.run()
        for w, r in enumerate(rows):
            mm = sim.m[w]
            r["accepted_strict_d"] = mm.get("acc_strict", 0.0) / 7
            r["sound_acc_d"] = mm.get("sound_acc", 0.0) / 7
            r["owner_min_wk"] = mm.get("owner_att_min", 0.0)
        return [R.add_derived(r) for r in rows]
    sim = R.RalphSim(P, m["theta"], v, rp, seed, weeks=4, quotas=q)
    rows = [R.add_derived(r) for r in sim.run()]
    for w, r in enumerate(rows):
        mm = sim.m[w]
        r["accepted_strict_d"], r["sound_acc_d"] = 0.0, 0.0
        loads = mm.get("c_tests_S", 0.0) + mm.get("c_tests_A", 0.0) + (mm.get("b_verdicts", 0.0) if v == "AB_test" else 0)
        r["reloads_per_acc"] = loads / max(1.0, mm.get("accepted_prod", 0.0)) if loads else float("nan")
        r["game_busy_min_d"] = mm.get("b_min", 0.0) / 7
    return rows


def tp_rows(P, m, seed, v, rp, tp, unlimited=False, const=None, budget_g=None):
    q = None if unlimited else scale_quotas(dict(m["quotas"]), budget_g)
    return [R.add_derived(r) for r in TPSim(P, m["theta"], v, rp, tp, seed, weeks=4, quotas=q, const=const).run()]


def compact(rows):
    return {k: round(R.wmean(rows, k), 5) for k in METRICS}


FP = fingerprint()


def cmd_ensemble(a):
    P = S.load_params()
    ms = R.members("park", a.members)
    os.makedirs(a.out, exist_ok=True)
    path = ens_path(a)
    priors, const, budget_g = scenario(a.scenario)
    done = fresh_done(path)
    t0 = time.time()
    with open(path, "a") as fh:
        for m in ms:
            if m["member"] in done:
                continue
            if time.time() - t0 > a.budget_s:
                print("budget reached")
                break
            seed = 50000 + m["member"] * 97
            rp, tp = R.draw_rp(m["member"]), draw_tp(m["member"], priors=priors)
            rows = {v: compact(zoo_rows(P, m, seed, v, rp, budget_g=budget_g)) for v in ZOO}
            for v in TP_VARIANTS:
                rows[v] = compact(tp_rows(P, m, seed, v, rp, tp, const=const, budget_g=budget_g))
            fh.write(json.dumps({"member": m["member"], "fp": FP, "tp": tp, "rows": rows}) + "\n")
    print(f"ensemble: {sum(1 for _ in open(path))} members on file, {time.time() - t0:.0f}s")


def ens_path(a):
    return os.path.join(a.out, "ens_park_today.jsonl" if a.scenario == "base" else f"ens_park_today_{a.scenario}.jsonl")


def fresh_done(path, key=lambda r: r["member"]):
    if not os.path.exists(path):
        return set()
    recs = [json.loads(line) for line in open(path)]
    if any(r.get("fp") != FP for r in recs):
        os.replace(path, path + f".stale_{int(time.time())}")
        print(f"{path}: rows from another fingerprint moved aside")
        return set()
    return {key(r) for r in recs}


OAT_METRICS = ("accepted_strict_d", "sound_acc_d", "ite_week", "reloads_per_acc", "pilot_idle_share")


def cmd_oat(a):
    P = S.load_params()
    ms = R.members("park", a.members)
    os.makedirs(a.out, exist_ok=True)
    path = os.path.join(a.out, "oat_park.jsonl")
    done = fresh_done(path, lambda r: (r["member"], r["param"], r["end"]))
    jobs = [(m, "_mid", "mid") for m in ms] + [(m, p, e) for p in sorted(TP_PRIORS) for e in ("lo", "hi") for m in ms]
    t0 = time.time()
    with open(path, "a") as fh:
        for m, p, e in jobs:
            if (m["member"], p, e) in done:
                continue
            if time.time() - t0 > a.budget_s:
                print("budget reached")
                break
            tp = mid_tp()
            if p != "_mid":
                tp[p] = TP_PRIORS[p][0 if e == "lo" else 1]
            seed = 50000 + m["member"] * 97
            rows = {v: {k: round(R.wmean(tp_rows(P, m, seed, v, R.mid_rp(), tp), k), 5) for k in OAT_METRICS}
                    for v in TP_VARIANTS}
            fh.write(json.dumps({"member": m["member"], "param": p, "end": e, "fp": FP, "rows": rows}) + "\n")
    print(f"oat: {sum(1 for _ in open(path))} of {len(jobs)} rows, {time.time() - t0:.0f}s")


# ======================================== reporting (outside the fingerprint)
def load_fresh(path):
    recs = [json.loads(line) for line in open(path)]
    bad = sum(r.get("fp") != FP for r in recs)
    if bad:
        raise SystemExit(f"{path}: {bad} rows from another fingerprint than {FP}; rerun, do not mix")
    return recs


def q3(vals):
    vals = [v for v in vals if v == v]
    if not vals:
        return "n/a"
    p = np.percentile(vals, [10, 50, 90])
    f = (lambda x: f"{x / 1e9:.2f}G") if max(abs(x) for x in vals) > 1e6 else (lambda x: f"{x:.3g}")
    return "/".join(f(x) for x in p)


def cmd_report(a):
    recs = load_fresh(ens_path(a))
    sfx = "" if a.scenario == "base" else f"_{a.scenario}"
    lines = [f"# TestPilot sim, scenario {a.scenario} (p10/p50/p90 over {len(recs)} members; weeks 2-4 of 4; park, "
             f"quotas today; fp {FP})", "",
             "| metric | " + " | ".join(ALL) + " |", "|---|" + "---|" * len(ALL)]
    res = {"fp": FP, "n": len(recs), "p50": {}, "paired": {}}
    for k in METRICS:
        lines.append(f"| {k} | " + " | ".join(q3([r["rows"][v][k] for r in recs]) for v in ALL) + " |")
        res["p50"][k] = {v: float(np.nanmedian([r["rows"][v][k] for r in recs])) for v in ALL}
    lines += ["", "Paired: share of members where the row variant beats the column on accepted_strict_d / sound_prod_d"
              " / sound_acc_d", "", "| | " + " | ".join(ALL) + " |", "|---|" + "---|" * len(ALL)]
    for v in TP_VARIANTS:
        cells = []
        for w in ALL:
            sh = [float(np.mean([r["rows"][v][k] > r["rows"][w][k] for r in recs]))
                  for k in ("accepted_strict_d", "sound_prod_d", "sound_acc_d")]
            cells.append("/".join(f"{x:.2f}" for x in sh))
            res["paired"][f"{v}>{w}"] = sh
        lines.append(f"| {v} | " + " | ".join(cells) + " |")
    op = os.path.join(a.out, "oat_park.jsonl")
    ostale = os.path.exists(op) and any(json.loads(x).get("fp") != FP for x in open(op))
    if ostale:
        lines += ["", f"One-at-a-time: {op} is from another fingerprint; not shown (rerun `oat`)."]
    if a.scenario == "base" and os.path.exists(op) and not ostale:
        orecs = load_fresh(op)
        mid = {r["member"]: r["rows"] for r in orecs if r["param"] == "_mid"}
        lines += ["", "One-at-a-time (median delta from all-midpoints, lo / hi), TP+ and TP", "",
                  "| param | " + " | ".join(f"{v} {k}" for v in TP_VARIANTS for k in OAT_METRICS[:3]) + " |",
                  "|---|" + "---|" * (2 * 3)]
        swing = []
        for p in sorted(TP_PRIORS):
            cells, big = [], 0.0
            for v in TP_VARIANTS:
                for k in OAT_METRICS[:3]:
                    d = {}
                    for e in ("lo", "hi"):
                        xs = [r["rows"][v][k] - mid[r["member"]][v][k] for r in orecs
                              if r["param"] == p and r["end"] == e and r["member"] in mid]
                        d[e] = float(np.median(xs)) if xs else float("nan")
                    if k == "accepted_strict_d" and v == "TP+":
                        big = abs(d["hi"] - d["lo"])
                    f = (lambda x: f"{x / 1e6:+.0f}M") if k == "ite_week" else (lambda x: f"{x:+.2f}")
                    cells.append(f"{f(d['lo'])} / {f(d['hi'])}")
            swing.append((big, p, cells))
        for big, p, cells in sorted(swing, reverse=True):
            lines.append(f"| {p} | " + " | ".join(cells) + " |")
        res["oat_top"] = [(p, b) for b, p, _ in sorted(swing, reverse=True)[:8]]
    open(os.path.join(a.out, f"tables{sfx}.md"), "w").write("\n".join(lines) + "\n")
    json.dump(res, open(os.path.join(a.out, f"results{sfx}.json"), "w"), indent=1)
    print(os.path.join(a.out, f"tables{sfx}.md"))


def cmd_one(a):
    P = S.load_params()
    m = R.members("park", a.member_idx + 1)[a.member_idx]
    seed = 50000 + m["member"] * 97
    if a.variant in TP_VARIANTS:
        rows = tp_rows(P, m, seed, a.variant, R.mid_rp(), mid_tp())
    else:
        rows = zoo_rows(P, m, seed, a.variant, R.mid_rp())
    print(json.dumps(compact(rows), indent=1))
    extra = {k: R.wmean(rows, k) for k in rows[-1] if k.endswith("_wk") and k.startswith(("reload", "full", "hand",
             "hot", "invalid", "void", "simpl", "live", "fixes", "c_bumps"))}
    print(json.dumps({k: round(v, 2) for k, v in sorted(extra.items())}, indent=1))
    print("tp_viol", rows[-1].get("tp_viol"), "max_rounds_phase", rows[-1].get("max_rounds_phase"))


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--out", default=OUT)
    sub = ap.add_subparsers(dest="cmd", required=True)
    e = sub.add_parser("ensemble")
    e.add_argument("--members", type=int, default=120)
    e.add_argument("--budget-s", type=float, default=480)
    e.add_argument("--scenario", default="base", choices=sorted(SCENARIOS))
    o = sub.add_parser("oat")
    o.add_argument("--members", type=int, default=12)
    o.add_argument("--budget-s", type=float, default=480)
    rpt = sub.add_parser("report")
    rpt.add_argument("--scenario", default="base", choices=sorted(SCENARIOS))
    one = sub.add_parser("one")
    one.add_argument("--variant", default="TP+", choices=ALL)
    one.add_argument("--member-idx", type=int, default=0)
    a = ap.parse_args(argv)
    {"ensemble": cmd_ensemble, "oat": cmd_oat, "report": cmd_report, "one": cmd_one}[a.cmd](a)


if __name__ == "__main__":
    main()
