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
      all(R.RALPH_PRIORS[k][0] <= v <= R.RALPH_PRIORS[k][1] for k, v in d.items()) and set(d) == set(R.RALPH_PRIORS))
check("per-member draw is keyed (same member, same draw; other member, other draw)",
      R.draw_rp(12345) == d and R.draw_rp(12346) != d)

print("FAILED: " + ", ".join(FAILS) if FAILS else "all checks passed")
sys.exit(1 if FAILS else 0)
