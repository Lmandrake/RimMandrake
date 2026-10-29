#!/usr/bin/env python3
"""Selftest for ralph_loop_sim.py (RALPH_LOOP_DESIGN_ONE_PROMPT_FOREVER): the invariants that must hold before a
Ralph-versus-v2/v3 comparison means anything. Determinism; the outside world (owner presence, owner arrivals, hidden
defect draws) is the same as v2's on one seed; a loop never runs two iterations at once; no helper, ring or role ever
fires; loop A never "accepts" anything and AB_test accepts only through B's live test; with no off-track iterations
there are no spirals and no steers; dropped tickets are only process tickets; the member's theta is not mutated;
Ralph priors are ranges with lo < hi and the per-member draw stays inside them. Synthetic parameters (prior
midpoints); no calibration file read; nothing written."""
import copy
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import rimflow_v3_sim as S  # noqa: E402
import ralph_loop_sim as R  # noqa: E402

FAILS = []


def check(name, ok, detail=""):
    print(("ok    " if ok else "FAIL  ") + name + ("" if ok else "  -- " + str(detail)))
    if not ok:
        FAILS.append(name)


P = S.load_params()


def mid_theta():
    th = {}
    for k, pr in P["priors"].items():
        v = (pr["lo"] + pr["hi"]) / 2
        th[k] = int(round(v)) if pr.get("int") else v
    return th


class OwnerLog:
    def file_ticket(self, t, key, cls, origin, linked=False):
        if origin == "owner":
            self.owner_keys.append((round(t), key, cls))
        super().file_ticket(t, key, cls, origin, linked)


class V2Probe(OwnerLog, S.Sim):
    def __init__(self, *a, **k):
        super().__init__(*a, **k)
        self.owner_keys = []


class RProbe(OwnerLog, R.RalphSim):
    def __init__(self, *a, **k):
        super().__init__(*a, **k)
        self.owner_keys = []
        self.dropped_cls = []
        self.launched = 0

    def add(self, t, key, v=1.0):
        if key == "proc_dropped":
            self.dropped_cls.append(self._cls)
        if key in ("helpers", "rings"):
            self.launched += 1
        super().add(t, key, v)

    def file_ticket(self, t, key, cls, origin, linked=False):
        self._cls = cls
        super().file_ticket(t, key, cls, origin, linked)


TH = mid_theta()
TH_COPY = copy.deepcopy(TH)
RP = R.mid_rp()
SEED = 4321
WEEKS = 2

v2 = V2Probe(P, TH, S.policy_cfg(P, "v2"), SEED, weeks=WEEKS)
v2_res = v2.run()
runs = {}
for v in R.VARIANTS:
    sim = RProbe(P, TH, v, RP, SEED, weeks=WEEKS)
    runs[v] = (sim, sim.run())

check("theta not mutated by RalphSim", TH == TH_COPY)
again = R.RalphSim(P, TH, "A", RP, SEED, weeks=WEEKS).run()
check("deterministic: same seed, same result", again == runs["A"][1])
for v, (sim, res) in runs.items():
    check(f"{v}: owner presence identical to v2", sim.present == v2.present)
    check(f"{v}: owner arrivals identical to v2 (time, key, class)", sim.owner_keys == v2.owner_keys,
          (len(sim.owner_keys), len(v2.owner_keys)))
    check(f"{v}: no loop ever ran two iterations at once", sim.overlap == 0, sim.overlap)
    check(f"{v}: no helper launched, no Dispatcher ring", sim.launched == 0, sim.launched)
    check(f"{v}: no roles active", not sim.roles_on)
    check(f"{v}: only process tickets are dropped", set(sim.dropped_cls) <= {"process"}, set(sim.dropped_cls))
    check(f"{v}: does work (iterations and closes)", all(w["iters_d"] > 0 and w["done_d"] > 0 for w in res))
    check(f"{v}: shares in range", all(0 <= w["wasted_share"] <= 1 and 0 <= w["proc_share"] <= 1 for w in res))
    check(f"{v}: tokens charged", all(w["ite_week"] > 0 for w in res))
check("A never accepts", all(w["accepted_prod_d"] == 0 for w in runs["A"][1]))
check("AB_build never accepts", all(w["accepted_prod_d"] == 0 for w in runs["AB_build"][1]))
check("AB_test accepts, and only through B verdicts",
      sum(w["accepted_prod_d"] for w in runs["AB_test"][1]) > 0
      and all(w.get("b_verdicts", 0) >= w.get("accepted_prod", 0) for w in runs["AB_test"][1]))
check("AB_build: only it has two lanes", runs["AB_build"][0].lanes == ("FOUNDRY", "BENCH")
      and runs["A"][0].lanes == ("FOUNDRY",))

rp0 = dict(RP, r_p_off=0.0)
calm = R.RalphSim(P, TH, "A", rp0, SEED, weeks=WEEKS).run()
check("no off-track iterations -> no spirals, no steers, nothing wasted",
      all(w["spirals_wk"] == 0 and w["steers_d"] == 0 and w["wasted_share"] == 0 for w in calm))
check("A's only owner nudges are status pings and steers",
      all(abs(w["nudges_d"] * 7 - w.get("pings", 0) - w["steers_d"] * 7) < 1e-6 for w in runs["A"][1]))
rp_hi = dict(RP, r_p_off=0.5, r_p_spiral=1.0, r_unstick_h=0.05)
spin = R.RalphSim(P, TH, "A", rp_hi, SEED, weeks=WEEKS).run()
check("a loop that spirals and never unsticks by itself wastes more and is steered by the owner",
      sum(w["wasted_share"] for w in spin) > sum(w["wasted_share"] for w in runs["A"][1])
      and sum(w["steers_d"] for w in spin) > 0)

check("priors: lo < hi for every Ralph parameter", all(lo < hi for lo, hi, _ in R.RALPH_PRIORS.values()))
d = R.draw_rp(12345)
check("per-member draw inside the ranges",
      all({**R.RALPH_PRIORS, **R.SUB_PRIORS}[k][0] <= v <= {**R.RALPH_PRIORS, **R.SUB_PRIORS}[k][1] for k, v in d.items())
      and set(d) == set(R.RALPH_PRIORS) | set(R.SUB_PRIORS))
check("per-member draw is keyed (same member, same draw; other member, other draw)",
      R.draw_rp(12345) == d and R.draw_rp(12346) != d)

# ---- regression: id(ticket) reuse once made AB_test differ run to run inside one process
for v in ("AB_test", "C"):
    seq = [R.RalphSim(P, TH, v, RP, SEED, weeks=WEEKS).run() for _ in range(3)]
    check(f"{v}: deterministic across repeated runs in one process", seq[0] == seq[1] == seq[2])

# ---- required live tests: an item that needs a test never closes untested (instrumented at the base close)
_orig_close = S.Sim.close
untested = []


def _close(self, t, tk):
    if isinstance(self, R.RalphSim) and self.variant in ("AB_test", "C") and tk.cls != "process" \
            and S.u01(self.seed, R.F_BTEST, tk.key) < self.rp["b_p_test"] and tk not in self.tested:
        untested.append(tk.key)
    _orig_close(self, t, tk)


S.Sim.close = _close
try:
    hard = dict(RP, b_blind=0.3, b_s_mult=1.3)
    for v in ("AB_test", "C"):
        R.RalphSim(P, TH, v, hard, SEED, weeks=WEEKS).run()
finally:
    S.Sim.close = _orig_close
check("AB_test/C: no item that needs a live test closes untested", not untested, untested[:5])


# ---- variant C: the Archmagi runner and the owner's game, checked by an independent clock
class CProbe(R.RalphSim):
    def __init__(self, *a, **k):
        self.starts = {"A": [], "S": []}
        self.aborts = []
        super().__init__(*a, **k)

    def add(self, t, key, v=1.0):
        if key.startswith("c_tests_"):
            self.starts[key[-1]].append(t)
        elif key == "c_bumps":
            self.aborts.append(t)
        super().add(t, key, v)


def owner_holds(sim, rp, h):
    return sim.present[h] and S.u01(SEED, R.F_CPOK, h) >= rp["c_a_present_ok"]


for pok in (0.0, 0.5):
    rpc = dict(RP, c_a_present_ok=pok)
    c = CProbe(P, TH, "C", rpc, SEED, weeks=WEEKS)
    cres = c.run()
    bad = []
    for t in c.starts["A"]:
        h = int(t // 3600)
        if owner_holds(c, rpc, h) or (h > 0 and owner_holds(c, rpc, h - 1) and t - h * 3600 < 20 * 60):
            bad.append(t)
    check(f"C pok={pok}: Archmagi runner never starts while the owner holds the game or <20 min after", not bad,
          bad[:3])
    check(f"C pok={pok}: every bump is at the hour the owner takes the game",
          all(owner_holds(c, rpc, int(t // 3600)) and t % 3600 == 0 for t in c.aborts), c.aborts[:3])
    check(f"C pok={pok}: no runner ran two tests at once, no sim-side violation", c.r_overlap == 0 and c.c_viol == 0,
          (c.r_overlap, c.c_viol))
    check(f"C pok={pok}: both runners test", len(c.starts["A"]) > 0 and len(c.starts["S"]) > 0,
          (len(c.starts["A"]), len(c.starts["S"])))
    check(f"C pok={pok}: the owner's return bumps tests", len(c.aborts) > 0, len(c.aborts))
c0 = CProbe(P, TH, "C", dict(RP, c_invalid=0.0, c_cold_min=0.5), SEED, weeks=WEEKS)
c0res = c0.run()
check("C: no invalid runs when c_invalid = 0", all(w["c_invalid_wk"] == 0 for w in c0res))
c1 = R.RalphSim(P, TH, "C", dict(RP, c_invalid=0.3), SEED, weeks=WEEKS).run()
check("C: invalid runs re-run and appear when c_invalid > 0", sum(w["c_invalid_wk"] for w in c1) > 0)
check("C: two builder lanes", runs["C"][0].lanes == ("FOUNDRY", "BENCH"))
check("+sub: subagents speed A up (more iterations per day)",
      sum(w["iters_d"] for w in runs["A+sub"][1]) > sum(w["iters_d"] for w in runs["A"][1]))
# ---- regression: sound per G ITE once floored its denominator at 1 G (max(1.0, ite/1e9)) and hid sub-1G variants
syn = [dict(w, sound_prod_d=10.0, ite_week=0.5e9) for w in runs["A"][1]]
spg = R.compact(syn)["sound_per_gite"]
check("sound_per_gite = sound/day * 7 / (ITE/1e9), not floored at 1 G", abs(spg - 140.0) < 1e-6, spg)
check("fingerprint is 12 hex chars", len(R.FP) == 12 and all(ch in "0123456789abcdef" for ch in R.FP))

print("FAILED: " + ", ".join(FAILS) if FAILS else "all checks passed")
sys.exit(1 if FAILS else 0)
