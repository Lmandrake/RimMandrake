#!/usr/bin/env python3
"""Selftest for rimflow_v3_sim.py (RIMFLOW_SIM_BUILD_FACTORY_IN_A_BOTTLE): the invariants a process simulation must hold
before any of its comparisons mean anything. Determinism; paired outside world across policies; the Dispatcher never
rings BENCH and never exceeds its caps; v2 never rings and never "accepts"; acceptance only through the Arbiter; token
bookkeeping stays in range; the ABC discrepancy never lets one target cancel another; v3-only parameters are redrawn
from the prior, not inherited from a calibration chain. Synthetic parameter sets (prior midpoints); no calibration
file read, nothing written outside a temp dir."""
import json
import os
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import rimflow_v3_sim as S  # noqa: E402

FAILS = []


def check(name, ok, detail=""):
    print(("ok    " if ok else "FAIL  ") + name + ("" if ok else "  -- " + str(detail)))
    if not ok:
        FAILS.append(name)


P = S.load_params()


def mid_theta(**over):
    th = {}
    for k, pr in P["priors"].items():
        v = (pr["lo"] + pr["hi"]) / 2
        th[k] = int(round(v)) if pr.get("int") else v
    th.update(over)
    return th


class Probe(S.Sim):
    """records every ring and every owner-origin filing"""

    def __init__(self, *a, **k):
        super().__init__(*a, **k)
        self.ring_log = []
        self.owner_keys = []
        self.min_used = 0.0

    def ring_tick(self, t):
        super().ring_tick(t)
        for n, s in self.seats.items():
            if s.rings and s.rings[-1] == t:          # a ring is stamped with the tick time it happened at
                self.ring_log.append((t, n))

    def file_ticket(self, t, key, cls, origin, linked=False):
        if origin == "owner":
            self.owner_keys.append(key)
        super().file_ticket(t, key, cls, origin, linked)

    def charge(self, t, ite, what):
        super().charge(t, ite, what)
        self.min_used = min(self.min_used, min(self.used.values()))


def run(policy, seed=3, weeks=3, quotas=None, warm=1, th=None, cls=Probe, **over):
    sim = cls(P, th or mid_theta(), S.policy_cfg(P, policy, **over), seed, weeks=weeks, quotas=quotas,
              warm_weeks=warm)
    res = sim.run()
    return sim, res


# 1 keyed randomness
xs = [S.u01(1, 2, i) for i in range(20000)]
check("u01 in [0,1) and mean ~0.5", all(0 <= x < 1 for x in xs) and abs(sum(xs) / len(xs) - 0.5) < 0.01)
check("u01 keyed: same key same value, different key different", S.u01(5, 6, 7) == S.u01(5, 6, 7)
      and S.u01(5, 6, 7) != S.u01(5, 6, 8))
lam = 3.0
ps = [S.poisson(lam, 9, i) for i in range(20000)]
check("poisson mean ~lambda", abs(sum(ps) / len(ps) - lam) < 0.06, sum(ps) / len(ps))

# 2 determinism
_, r1 = run("v3.4", seed=11)
_, r2 = run("v3.4", seed=11)
check("same seed, same policy -> identical metrics", json.dumps(r1, sort_keys=True) == json.dumps(r2, sort_keys=True))
_, r3 = run("v3.4", seed=12)
check("different seed -> different metrics", json.dumps(r1, sort_keys=True) != json.dumps(r3, sort_keys=True))

# 3 v2 never rings, never accepts
s2, rv2 = run("v2", seed=4)
check("v2: zero rings", not s2.ring_log and all(w.get("rings_d", 0) == 0 for w in rv2), s2.ring_log[:3])
check("v2: zero protocol acceptances", all(w.get("accepted_prod_d", 0) == 0 for w in rv2))

# 4 Dispatcher: never BENCH, caps respected (tight caps to make them bind)
caps = {"wakes_per_seat_hour": 2, "wakes_per_seat_day": 5, "wakes_per_day": 6}
sd, _ = run("v3.0", seed=5, weeks=3, wake_caps=caps, th=mid_theta(p_stall=0.35, r_self_h=0.05, p_watch=0.4))
rings = sd.ring_log
check("Dispatcher rang at all (instrument can see)", len(rings) > 0)
check("Dispatcher never rings BENCH", all(n != "BENCH" for _, n in rings))
okh = all(sum(1 for u, n in rings if n == m and 0 <= t - u <= 3600) <= caps["wakes_per_seat_hour"] for t, m in rings)
okd = all(sum(1 for u, n in rings if n == m and 0 <= t - u <= 86400) <= caps["wakes_per_seat_day"] for t, m in rings)
okg = all(sum(1 for u, _ in rings if 0 <= t - u <= 86400) <= caps["wakes_per_day"] for t, _ in rings)
check("per-seat hourly cap held", okh)
check("per-seat daily cap held", okd)
check("global daily cap held", okg)
check("no ring before the policy switches on (warm week is v2)", all(t >= S.WEEK for t, _ in rings))

# 5 paired outside world: owner-origin arrivals are the same tickets under every policy
pa, _ = run("v2", seed=8)
pb, _ = run("v3.4", seed=8)
check("owner arrivals identical across v2 and v3.4 (paired seeds)",
      pa.owner_keys == pb.owner_keys and len(pa.owner_keys) > 100, (len(pa.owner_keys), len(pb.owner_keys)))

# 6 acceptance only via the Arbiter
s4, r4 = run("v3.4", seed=9)
acc = sum(w.get("accepted_prod_d", 0) for w in r4) * 7
verd = sum(w.get("arb_verdicts", 0) or 0 for w in r4)
check("v3.4 accepts something", acc > 0)
check("accepted <= Arbiter verdicts (no self-acceptance)", acc <= verd, (acc, verd))
s32, r32 = run("v3.2", seed=9)
check("without an Arbiter nothing is accepted", all(w.get("accepted_prod_d", 0) == 0 for w in r32))

# 7 tokens
q = {a: 6e8 for a in S.ACCOUNTS}
st, rt = run("v3.4", seed=10, quotas=q)
check("account usage never negative", st.min_used >= 0)
check("pool_left in [0,1] every week", all(0 <= w.get("pool_left", 1) <= 1 for w in rt))
check("tight quota blocks the seats (instrument can see)", any(w.get("blocked_h", 0) > 0 for w in rt))
_, ru = run("v3.4", seed=10, quotas=None)
check("unlimited tokens: never blocked", all(w.get("blocked_h", 0) == 0 for w in ru))

# 8 discrepancy: no cancellation
good = {k: tg["value"] for k, tg in P["targets"].items()}
w0, _ = S.discrepancy(P, good)
bad = dict(good)
k0 = next(iter(P["targets"]))
tg0 = P["targets"][k0]
bad[k0] = tg0["value"] * (1 + 2 * tg0["tol"]) if tg0["kind"] == "rel" else tg0["value"] + 2 * tg0["tol"]
w1, per = S.discrepancy(P, bad)
check("perfect summary -> worst 0", w0 == 0)
check("one target 2 tolerances off -> rejected despite 8 perfect", w1 > 1.9 and per[k0] > 1.9, w1)
nan = dict(good)
nan[k0] = float("nan")
check("an unmeasured target is a rejection, not a pass", S.discrepancy(P, nan)[0] > 1)

# 9 members: de-duplicated, v3-only params redrawn per member
with tempfile.TemporaryDirectory() as d:
    th = mid_theta()
    rows = [{"member": i, "chain": 0, "theta": th if i < 3 else mid_theta(lam_ext_h=5.0), "accepted": True,
             "worst": 0.5, "per": {}, "summary": {}, "quotas": q} for i in range(5)]
    with open(os.path.join(d, "calib_members.jsonl"), "w") as fh:
        for r in rows:
            fh.write(json.dumps(r) + "\n")
    ms = S.load_members(d)
    check("duplicate chain states collapse", len(ms) == 2, len(ms))
    ms2 = S.load_members(d)
    check("v3-only redraw is deterministic", [m["theta"] for m in ms] == [m["theta"] for m in ms2])
    check("v3-only params differ between members", ms[0]["theta"]["arb_s_hi"] != ms[1]["theta"]["arb_s_hi"])
    check("v2 params untouched", ms[1]["theta"]["lam_ext_h"] == 5.0)
    check("every V3_ONLY name is a real prior", all(k in P["priors"] for k in S.V3_ONLY))

# 10 every prior and fixed parameter carries a provenance status
bad_status = [k for k, v in P["fixed"].items() if "status" not in v]
check("every fixed parameter has a status", not bad_status, bad_status)
check("every prior is a range", all(pr["lo"] < pr["hi"] for pr in P["priors"].values()))

# 11 structure switch: pull works parked tickets, park never does
S.STRUCTURE = "pull"
sp, rp = run("v2", seed=6)
S.STRUCTURE = "park"
spk, rpk = run("v2", seed=6)
check("pull structure pulls from the backlog", sum(w.get("pulled_from_backlog", 0) or 0 for w in sp.m) > 0)
check("park structure never pulls", sum(w.get("pulled_from_backlog", 0) or 0 for w in spk.m) == 0)

print(f"\n{'FAIL' if FAILS else 'PASS'}: {len(FAILS)} failure(s)")
sys.exit(1 if FAILS else 0)
