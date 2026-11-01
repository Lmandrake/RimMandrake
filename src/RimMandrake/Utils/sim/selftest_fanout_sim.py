#!/usr/bin/env python3
"""Selftest for fanout_sim.py (ARCH_SIM_MEASURE_FANOUT_EQUAL_TERMS). What must hold before the sweep means anything:
with kappa 0 Ralph A at N=1 is RalphSim A (the pool generalises the serial loop); determinism; no arm ever exceeds N
workers, and a broken gate is seen (mutation probe, because a check that reads the gate cannot fail); every arm can
run on the pool; with zero contention costs Ralph fan-out helps; a certain merge conflict costs work; a fair check
fires only on overlapping tickets and only in arms without their own check; unattended means no owner; the member's
theta is not mutated. Synthetic parameters (prior midpoints); no calibration file read; nothing written."""
import copy
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import rimflow_v3_sim as S  # noqa: E402
import ralph_loop_sim as R  # noqa: E402
import testpilot_sim as TP  # noqa: E402
import fanout_sim as F  # noqa: E402

FAILS = []


def check(name, ok, detail=""):
    print(("ok    " if ok else "FAIL  ") + name + ("" if ok else "  -- " + str(detail)))
    if not ok:
        FAILS.append(name)


P = S.load_params()
S.STRUCTURE = "pull"


def mid_theta():
    th = {}
    for k, pr in P["priors"].items():
        v = (pr["lo"] + pr["hi"]) / 2
        th[k] = int(round(v)) if pr.get("int") else v
    return th


TH = mid_theta()
RP = R.mid_rp()
TPP = TP.mid_tp()
FO = {k: (lo + hi) / 2 for k, (lo, hi, _) in F.FO_PRIORS.items()}
M = {"member": 3, "theta": TH, "quotas": None}
SEED = 777


def run(arm, n, fo=None, unattended=False, cls=None):
    fo = dict(fo or FO)
    if arm in ("v2", "v3.0", "v3.4"):
        sim = F.FanV3(P, TH, S.policy_cfg(P, arm), RP, SEED, n, fo, weeks=3, unattended=unattended)
    elif arm in ("TP", "TP+"):
        sim = F.FanTP(P, TH, arm, dict(RP, r_par=1.0, r_par_ite=1.0), TPP, SEED, n, fo, weeks=3, unattended=unattended)
    else:
        sim = (cls or F.FanRalph)(P, TH, arm, dict(RP), SEED, n, fo, weeks=3, unattended=unattended)
    rows = sim.run()
    return sim, rows


# ---- identity: N=1 is the serial loop
base = R.RalphSim(P, TH, "A", dict(RP, r_par=1.0, r_par_ite=1.0), SEED, weeks=3).run()
sim1, r1 = run("A", 1, dict(FO, kappa=0.0))
for k in ("sound_prod_d", "done_d", "escapes_wk"):
    check(f"A at N=1 equals serial A: {k}", all(abs(a[k] - b[k]) < 1e-6 * max(1, abs(a[k])) for a, b in zip(base, r1)),
          [(a[k], b[k]) for a, b in zip(base, r1)])
# units charge as they start, so ITE can cross a week end against the serial loop's lump; the total cannot move
ib, i1 = sum(x["ite_week"] for x in base), sum(x["ite_week"] for x in r1)
check("A at N=1 spends what serial A spends", abs(ib - i1) < 1e-6 * ib, (ib, i1))
check("N=1 pays no fan-out cost", sim1.m[1].get("fo_conflicts", 0) == 0 and sim1.m[1].get("fo_checks", 0) == 0)

# ---- determinism and the world
a, ra = run("A", 4)
b, rb = run("A", 4)
check("deterministic", ra == rb)
th0 = copy.deepcopy(TH)
for arm in F.ARMS:
    for n in (1, 2, 4):
        s, rows = run(arm, n)
        check(f"{arm} N={n} stays inside the pool and does work", s.peak <= n and sum(r["done_d"] for r in rows) > 0,
              (s.peak, n))
        if n == 4:
            check(f"{arm} N=4 reaches beyond one worker", s.peak >= 2, s.peak)
check("member theta not mutated", TH == th0)


s, _ = run("v3.4", 2)
check("reservations count against the pool", s.fo_used() <= 2, s.fo_used())
s0, _ = run("v3.4", 4)
check("an Arbiter verdict takes a slot", s0.m[1].get("arb_verdicts", 0) > 0 or sum(m.get("arb_verdicts", 0) for m in s0.m) > 0)

# ---- mutation probe: break the gate and the instrument must see it
class Unbounded(F.FanRalph):
    def __init__(self, *a, **k):
        super().__init__(*a, **k)
        self.N = 10 ** 6


s, _ = run("A", 2, cls=Unbounded)
check("mutation probe: an ungated pool breaks the peak check", s.peak > 2, s.peak)

# ---- effects have the right sign
free = dict(FO, kappa=0.0, c_merge=0.0, m_ite=0.0, land_s=0.0, rig_min=0.0, w_ite=0.0, chk_fr=0.0, chk_ite=0.0,
            chk_min=0.0, chk_s=0.0, slow=0.0)
s1, r1f = run("A", 1, free)
s4, r4f = run("A", 4, free)
d1, d4 = sum(r["done_d"] for r in r1f[1:]), sum(r["done_d"] for r in r4f[1:])
check("free fan-out raises Ralph throughput", d4 > d1 * 1.2, (d1, d4))

certain = dict(free, c_merge=1.0, x_area=1.0, m_redo=1.0)
s, r = run("A", 4, certain)
check("a certain conflict is paid", sum(m.get("fo_conflicts", 0) for m in s.m) > 0 and
      sum(x["done_d"] for x in r[1:]) < d4, (sum(m.get("fo_conflicts", 0) for m in s.m), d4))

none = dict(FO, c_merge=0.0)
s, _ = run("A", 4, none)
check("no chance, no conflict", sum(m.get("fo_conflicts", 0) for m in s.m) == 0)

s, _ = run("A", 4)
check("an arm with no check of its own pays the fair check", sum(m.get("fo_checks", 0) for m in s.m) > 0)
s, _ = run("TP+", 4)
check("TP+ has its own check", sum(m.get("fo_checks", 0) for m in s.m[1:]) == 0)


class SpyV(F.FanV3):
    seen = set()

    def fo_check_done(self, t, tk):
        if t >= self.T_end / 2:          # clear of checks started in the warm week
            SpyV.seen.add(tk.cls)
        super().fo_check_done(t, tk)


# v3.4's Arbiter joins after the warm week; the fair check covers only tickets it did not pass, which are process tickets
SpyV(P, TH, S.policy_cfg(P, "v3.4"), RP, SEED, 4, dict(FO), weeks=3).run()
check("v3.4's Arbiter holds its product tickets", "product" not in SpyV.seen, SpyV.seen)
s, _ = run("v3.4", 4)
check("v3.4 before its Arbiter pays the fair check", s.m[0].get("fo_checks", 0) > 0)

hot = dict(free, kappa=2.0, k_sat=7.0, c_ref=0.0)
cold = dict(free, kappa=2.0, k_sat=7.0, c_ref=4.0)
s0, r0 = run("A", 4, free)
s2, r2 = run("A", 4, hot)
s3, r3 = run("A", 4, cold)
esc = lambda rows: sum(x["escapes_wk"] for x in rows)
check("kappa adds defects with no reference", esc(r2) > esc(r0), (esc(r2), esc(r0)))
check("a higher reference lowers them: kappa is centred", esc(r3) < esc(r2), (esc(r3), esc(r2)))
s1c, _ = run("A", 1, dict(FO, kappa=0.3, c_ref=1.5))
s1a, _ = run("A", 1, dict(FO, kappa=0.0))
check("N=1 sits at or below the calibrated rate", sum(m.get("defects", 0) for m in s1c.m) <= sum(m.get("defects", 0) for m in s1a.m))
sc, _ = run("v2", 1, dict(FO, chk_all=1.0))
check("the equal-check contract reaches N=1", sum(m.get("fo_checks", 0) for m in sc.m) > 0)
s, _ = run("A", 4)
check("occupancy integral is bounded by N", 0 < s.area <= 4 * s.T_end * 1.001, s.area / s.T_end)

g = run("A", 2)[0]
g.fo_tick(0)
tk = object()
g.fo_over, g.live, g.busy = set(), __import__("collections").Counter(), 0
g.fo_take(g.T_end, tk)
g.fo_take(g.T_end)
check("overlap is seen the moment a second worker starts", tk in g.fo_over)

# ---- third review: a redo pays the rebase wall time, a spiral does not need an idle pool, process tickets are checked
fast, slow_ = dict(certain, m_s=0.0), dict(certain, m_s=4 * 3600.0)
df, ds = [sum(x["done_d"] for x in run("A", 4, f)[1][1:]) for f in (fast, slow_)]
check("a redo pays m_s", ds < df, (ds, df))

class Spy(F.FanRalph):
    seen = set()

    def fo_check_done(self, t, tk):
        Spy.seen.add(tk.cls)
        super().fo_check_done(t, tk)


run("A", 4, dict(FO, chk_all=1.0), cls=Spy)
check("a process ticket pays the fair check too", "process" in Spy.seen, Spy.seen)

g = run("AB_build", 4)[0]
lane = g.seats[sorted(g.lanes)[0]]
g.jobs.clear()
g.unit_q.clear()
g.fo_spin.clear()
g.busy, lane.stalled, lane.serial_busy = 1, True, False
g.N = g.fo_used() + 2
w0 = g.m[0].get("iters_wasted", 0)
g.try_work(lane, 0.0)
check("a spiral runs beside other work", g.m[0].get("iters_wasted", 0) == w0 + 1, g.m[0].get("iters_wasted", 0) - w0)
g.try_work(lane, 0.0)
check("one lane spirals one worker at a time", g.m[0].get("iters_wasted", 0) == w0 + 1, g.m[0].get("iters_wasted", 0) - w0)

# ---- fourth review: machine slowdown reaches every kind of worker, not only ordinary units
g = run("A", 4)[0]
g.fo_tick(0)
g.fo.update(slow=0.05)
g.N, g.busy, g.all_blocked = 10, 7, False
g.ev, g.jobs = [], __import__("collections").deque([(600.0, ("check", None), 0.0, "")])
g.fo_pump(1000.0)
ends = [e[0] for e in g.ev]
check("a queued check slows with the pool", ends and abs(ends[0] - (1000.0 + 600.0 * 1.2)) < 1e-6, ends)

s, _ = run("A", 4, unattended=True)
check("unattended has no owner", not any(s.present) and sum(m.get("nudges", 0) for m in s.m) == 0)
sa = sum(x["done_d"] for x in run("A", 1, unattended=True)[1][1:])
class Dry(F.FanRalph):
    def __init__(self, *a, **k):
        super().__init__(*a, **k)
        self.fo_stocked = False


sd = sum(x["done_d"] for x in run("A", 1, unattended=True, cls=Dry)[1][1:])
check("the unattended stock is what keeps work flowing", sa > 3 * sd, (sa, sd))

lo = F.draw_fo(5, "post")
check("posterior draws stay in their box", all(F.POSTERIOR["fo"][k][0] <= lo[k] <= F.POSTERIOR["fo"][k][1]
                                               for k in F.POSTERIOR["fo"]))

print("selftest_fanout_sim:", "FAIL " + str(FAILS) if FAILS else "PASS")
sys.exit(1 if FAILS else 0)
