#!/usr/bin/env python3
"""Selftest for testing_investment_sim.py and testing_census.py (TESTING_BENCHMARK_MONTE_CARLO).

The invariants the testing-investment Monte Carlo must hold before its ranking means anything:
- determinism per seed;
- the MEASURED redistribution conserves defects;
- every kind is wired to a known lane and known areas;
- zero efficacy means a pure loss (net = -spent), and the break-even efficacy really zeroes net;
- the census classifiers sort probe paths and texts the way the doc claims they do.
Uses a synthetic census, so it reads no scratch file and writes nothing."""
import os
import random
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import testing_census as C  # noqa: E402
import testing_investment_sim as S  # noqa: E402

FAILS = []


def check(name, ok, detail=""):
    print(("ok    " if ok else "FAIL  ") + name + ("" if ok else "  -- " + str(detail)))
    if not ok:
        FAILS.append(name)


CENSUS = {
    "days": 30,
    "git": {"commits_touching": {"csharp": 200, "xml": 100, "python_tooling": 300, "machinery": 100, "art": 50}},
    "ledger": {
        "items_filed": 400,
        "kind_x_channel": {
            "csharp|review": 40, "csharp|live": 10, "csharp|offline": 5, "csharp|unknown": 5,
            "xml|review": 10, "xml|offline": 2, "machinery|live": 20, "machinery|testq": 5, "machinery|owner": 2,
            "python_tooling|review": 8, "python_tooling|offline": 4, "mod_unspecified|review": 6,
            "unknown|review": 9, "art|live": 3,
        },
    },
}

# 1 determinism
a = S.simulate(CENSUS, draws=300, seed=11)
b = S.simulate(CENSUS, draws=300, seed=11)
c = S.simulate(CENSUS, draws=300, seed=12)
check("same seed -> identical result", a == b)
check("different seed -> different draws", a["kinds"] != c["kinds"])

# 2 conservation of MEASURED defects (art is out of scope, everything else lands in an area)
M = S.measured(CENSUS)
in_scope = sum(v for k, v in CENSUS["ledger"]["kind_x_channel"].items() if not k.startswith("art|"))
got = sum(M[x]["defects"] for x in S.AREAS)
check("redistribution conserves defects", abs(got - in_scope) < 1e-6, (got, in_scope))
for x in S.AREAS:
    check(f"{x}: late_frac in [0,1]", 0 <= M[x]["late_frac"] <= 1, M[x]["late_frac"])
    mix = sum(M[x]["late_mix"].values())
    check(f"{x}: late mix sums to 1 or 0", abs(mix - 1) < 1e-9 or mix == 0, mix)
    check(f"{x}: late <= defects", M[x]["late"] <= M[x]["defects"] + 1e-9)
check("mod_unspecified split csharp:xml by their ratio",
      # csharp 60 known + 6*60/72 = 5 from mod_unspecified; then unknown 9 * 65/117 = 5 -> 70
      abs(M["csharp"]["defects"] - 70) < 1e-6,
      M["csharp"]["defects"])

# 3 wiring
for k, spec in S.KINDS.items():
    check(f"{k}: lane known", spec["lane"] in S.LANE_CPU_WEIGHT, spec["lane"])
    check(f"{k}: areas known", set(spec["eff"]) <= set(S.AREAS), spec["eff"])
    check(f"{k}: ranges ordered", all(lo <= hi for lo, hi in spec["eff"].values()))
check("ranking covers every kind once", sorted(a["ranking"]) == sorted(S.KINDS))
check("ASSUMED labels carried in output", set(a["labels"]["ASSUMED"]["KINDS"]) == set(S.KINDS))

# 4 zero efficacy -> pure loss; break-even zeroes net
saved = {k: dict(v["eff"]) for k, v in S.KINDS.items()}
try:
    for k in S.KINDS:
        S.KINDS[k]["eff"] = {x: (0.0, 0.0) for x in saved[k]}
    r = S.draw_one(random.Random(3), M, CENSUS, S.MUTMUT_DEFAULT)
    check("zero eff -> net == -spent for every kind",
          all(abs(r[k]["net"] + r[k]["spent"]) < 1e-9 and r[k]["caught"] == 0 for k in S.KINDS))
    r0 = S.draw_one(random.Random(5), M, CENSUS, S.MUTMUT_DEFAULT)
    be = r0["contracts_pydantic"]["breakeven_eff"]
    S.KINDS["contracts_pydantic"]["eff"] = {x: (be, be) for x in saved["contracts_pydantic"]}
    r1 = S.draw_one(random.Random(5), M, CENSUS, S.MUTMUT_DEFAULT)
    check("break-even eff zeroes net", abs(r1["contracts_pydantic"]["net"]) < 1e-6 * max(1, r1["contracts_pydantic"]["spent"]),
          r1["contracts_pydantic"]["net"])
finally:
    for k in S.KINDS:
        S.KINDS[k]["eff"] = saved[k]

# 5 census classifier probes
check("path: .cs -> csharp", C.path_kind("src/RimMandrake/FlowWorks/Source/Pump.cs") == "csharp")
check("path: Defs xml -> xml", C.path_kind("src/RimMandrake/Cauldron/Defs/ThingDefs/X.xml") == "xml")
check("path: rimflow -> machinery", C.path_kind("src/RimMandrake/rimflow/arbiter_tiers.py") == "machinery")
check("path: Utils tool -> python_tooling", C.path_kind("src/RimMandrake/Utils/deploy_custom_mods.py") == "python_tooling")
check("path: ledger shard ignored", C.path_kind("infrastructure/state/ledger/events/BENCH.jsonl") is None)
check("selftest under a mod -> mod_selftest",
      C.selftest_kind("src/RimMandrake/FlowWorks/Tests/selftest_pump.py") == "mod_selftest")
check("selftest under Utils -> python_tooling",
      C.selftest_kind("src/RimMandrake/Utils/selftest_refresh.py") == "python_tooling")
check("selftest under rimflow -> machinery",
      C.selftest_kind("src/RimMandrake/rimflow/selftest_arbiter_tiers.py") == "machinery")
check("text: evidence path is not machinery", C.text_kind("Evidence D:\\ClaudeWork\\x.png") != "machinery")
check("text: harmony -> csharp", C.text_kind("HARMONY postfix NRE in tick") == "csharp")
check("channel: GPT review", C.channel_of("GPT review r3 found a fail-open") == "review")
check("channel: owner", C.channel_of("owner found the pump leaks") == "owner")
check("channel: testq", C.channel_of("testq run-12@stevedesktop FAIL") == "testq")
check("channel: live", C.channel_of("seen in Player.log on the live map") == "live")
check("channel: offline", C.channel_of("nightly selftest red") == "offline")
check("defect by intent", C.is_defect({"id": "PUMP_FIX_LEAK", "kind": "item"}))
check("build item is not a defect", not C.is_defect({"id": "PUMP_BUILD_HOSE", "kind": "item"}))

print(f"\n{'PASS' if not FAILS else 'FAIL'}: {len(FAILS)} failure(s)")
sys.exit(1 if FAILS else 0)
