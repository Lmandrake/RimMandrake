#!/usr/bin/env python3
"""Selftest for testpilot_sim.py (TESTPILOT_DESIGN_PROOF_BEFORE_RELOAD): the invariants that must hold before a
TestPilot-versus-zoo comparison means anything. Determinism; no item is accepted without the blind critic AND (for a
game change) a minimal live pass AND a full-list pass; the Archmagi pilot never starts a step while the owner plays;
every reload carries a written rule and the rule counts add up; TP+ never runs more than 2 critic rounds per phase;
switching a fault off removes it (no crash, no invalid run, no void verdict); the critic and the pilot are real
instruments (sensitivity 0 lets more defects escape than sensitivity 1); accepted_strict never exceeds what was done;
Ralph C and AB_test count 0 strict (no blind check, by definition); TP priors are ranges and the member draw stays in
them. Synthetic parameters (prior midpoints); no calibration file read; nothing written."""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import rimflow_v3_sim as S  # noqa: E402
import ralph_loop_sim as R  # noqa: E402
import testpilot_sim as T  # noqa: E402

FAILS = []


def check(name, ok, detail=""):
    print(("ok    " if ok else "FAIL  ") + name + ("" if ok else "  -- " + str(detail)))
    if not ok:
        FAILS.append(name)


P = S.load_params()
TH = {k: (int(round((pr["lo"] + pr["hi"]) / 2)) if pr.get("int") else (pr["lo"] + pr["hi"]) / 2)
      for k, pr in P["priors"].items()}
RP, TP = R.mid_rp(), T.mid_tp()
SEED, WEEKS = 50097, 3


class Probe(T.TPSim):
    """records every acceptance with the gates it passed, and every Archmagi step start"""
    def __init__(self, *a, **k):
        super().__init__(*a, **k)
        self.full_ok, self.bad_accept, self.a_starts = set(), [], []

    def passed(self, r, t, tk):
        if self.pilot[r]["full"]:
            self.full_ok.add(tk)
        return super().passed(r, t, tk)

    def final(self, t, tk):
        if tk not in self.crit_ok or (T.needs_test(self, tk) and (tk not in self.tested_min or tk not in self.full_ok)):
            self.bad_accept.append(tk.key)
        return super().final(t, tk)

    def guard(self, r, t, dur, tag):
        if r == "A":
            self.a_starts.append(t)
        return super().guard(r, t, dur, tag)


def run(v, tp=None, rp=None, cls=T.TPSim):
    sim = cls(P, TH, v, rp or RP, tp or TP, SEED, weeks=WEEKS)
    return sim, sim.run()


def tot(rows, k):
    return sum(w.get(k, 0.0) for w in rows[1:])


base = {v: run(v, cls=Probe) for v in T.TP_VARIANTS}
for v, (sim, rows) in base.items():
    _, again = run(v)
    check(f"{v}: deterministic on one seed", [w["accepted_strict_d"] for w in rows] ==
          [w["accepted_strict_d"] for w in again])
    check(f"{v}: no acceptance without critic + minimal pass + full-list pass", not sim.bad_accept and
          rows[-1]["tp_viol"] == 0, (sim.bad_accept[:3], sim.viol))
    check(f"{v}: accepts something", tot(rows, "accepted_strict_d") > 0)
    check(f"{v}: Archmagi never starts a step while the owner plays",
          not [t for t in sim.a_starts if sim.owner_busy[min(int(t // 3600), len(sim.owner_busy) - 1)]])
    rules = sum(w[k] for w in rows[1:] for k in w if k.startswith("reload_R") and k.endswith("_wk"))
    check(f"{v}: every reload has a written rule (rule counts sum to reloads)",
          abs(rules - tot(rows, "reloads_wk")) < 1e-9, (rules, tot(rows, "reloads_wk")))
    check(f"{v}: strict accepted <= done", all(w["accepted_strict_d"] <= w["done_d"] + 1e-9 for w in rows))
    check(f"{v}: sound_acc <= accepted_strict", all(w["sound_acc_d"] <= w["accepted_strict_d"] + 1e-9 for w in rows))
    check(f"{v}: pilot idle share in [0,1]", 0.0 <= rows[-1]["pilot_idle_share"] <= 1.0, rows[-1]["pilot_idle_share"])
check("TP+: critic rounds per phase <= 2", base["TP+"][1][-1]["max_rounds_phase"] <= 2,
      base["TP+"][1][-1]["max_rounds_phase"])
check("TP: critic rounds per phase <= 6 + the second review", base["TP"][1][-1]["max_rounds_phase"] <= 7,
      base["TP"][1][-1]["max_rounds_phase"])
check("TP: the long pilot hands off; TP+ never does",
      tot(base["TP"][1], "handoffs_wk") > 0 and tot(base["TP+"][1], "handoffs_wk") == 0)
check("TP+: batches the full list (fewer full loads than TP per accepted item)",
      tot(base["TP+"][1], "full_loads_wk") / max(1, tot(base["TP+"][1], "accepted_strict_d")) <
      tot(base["TP"][1], "full_loads_wk") / max(1, tot(base["TP"][1], "accepted_strict_d")))

for v in T.TP_VARIANTS:
    _, r0 = run(v, tp=dict(TP, p_crash=0.0, p_invalid=0.0, follow_ok=1.0))
    check(f"{v}: faults off -> no crash, no invalid, no void verdict",
          tot(r0, "crashes_wk") == 0 and tot(r0, "invalid_wk") == 0 and tot(r0, "void_counted_wk") == 0,
          (tot(r0, "crashes_wk"), tot(r0, "invalid_wk"), tot(r0, "void_counted_wk")))
    _, rhi = run(v, tp=dict(TP, p_invalid=0.3))
    check(f"{v}: invalid runs appear when p_invalid > 0", tot(rhi, "invalid_wk") > 0)
    _, blind = run(v, tp=dict(TP, crit_s=0.0), rp=dict(RP, b_s_mult=0.0))
    _, sharp = run(v, tp=dict(TP, crit_s=1.0))
    fb = tot(blind, "escapes_wk") / max(1.0, tot(blind, "accepted_strict_d"))
    fs = tot(sharp, "escapes_wk") / max(1.0, tot(sharp, "accepted_strict_d"))
    check(f"{v}: blind critic and pilot let more defects escape per accepted item than sharp ones", fb > fs, (fb, fs))

_, pp = run("TP+", tp=dict(TP, p_misjudge=1.0, canary_catch=0.0, follow_ok=0.0))
check("TP+: with the canary off and a pilot that never notices, void verdicts are counted",
      tot(pp, "void_counted_wk") > 0)

m = {"theta": TH, "quotas": None}
for v in ("C", "AB_test"):
    rows = T.zoo_rows(P, m, SEED, v, RP, unlimited=True)
    check(f"zoo {v}: strict = 0 (live test but no blind check)", all(w["accepted_strict_d"] == 0 for w in rows))
v34 = T.zoo_rows(P, m, SEED, "v3.4", RP, unlimited=True)
check("zoo v3.4: strict <= Arbiter-accepted", all(w["accepted_strict_d"] <= w["accepted_prod_d"] + 1e-9 for w in v34))

for k, (lo, hi, why) in T.TP_PRIORS.items():
    if not (lo < hi and why):
        check(f"prior {k}: lo < hi with a reason", False, (lo, hi))
d = T.draw_tp(7)
check("member draw inside every prior", all(T.TP_PRIORS[k][0] <= x <= T.TP_PRIORS[k][1] for k, x in d.items()))
bp, bc, bb = T.scenario("base")
check("scenario base is round 1 exactly", bp == T.TP_PRIORS and bc == T.BASE_CONST and bb is None)
gp, gc, _ = T.scenario("gpt")
check("scenario gpt overrides only the ranges it names, keeps reasons",
      gp["full_load_min"][:2] == (17, 30) and gp["crit_fr"] == T.TP_PRIORS["crit_fr"] and gp["full_load_min"][2]
      and gc["FULL_N"] == 2 and gc["K"] == 1)
check("gpt draw inside its own priors", all(gp[k][0] <= x <= gp[k][1] for k, x in T.draw_tp(7, priors=gp).items()))
q = T.scale_quotas({"a": 3e8, "b": 7e8}, 1.0)
check("scale_quotas keeps shares and hits the budget", abs(sum(q.values()) - 1e9) < 1 and abs(q["a"] / q["b"] - 3 / 7) < 1e-9)
gsim = T.TPSim(P, TH, "TP+", RP, dict(TP), SEED, weeks=2, quotas=None, const=gc)
check("TPSim carries its scenario constants", gsim.c["FULL_N"] == 2 and gsim.c["W_MIN"] == 2)
check("fingerprint is 12 hex chars", len(T.FP) == 12 and all(ch in "0123456789abcdef" for ch in T.FP))

print("FAILED: " + ", ".join(FAILS) if FAILS else "all checks passed")
sys.exit(1 if FAILS else 0)
