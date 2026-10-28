#!/usr/bin/env python3
"""Monte Carlo: where would more testing pay, and which kind, on which lane (TESTING_BENCHMARK_MONTE_CARLO).

Reads the MEASURED census (testing_census.py -> census.json: 30 days of ledger, git, testq, nightly selftests,
reviews) plus the MEASURED mutmut pilot, and draws every ASSUMED parameter from a stated range. For each test kind
it estimates, per month: defects that would be caught EARLY (by the test, before review / live round / owner),
agent-minutes saved and spent, CPU-minutes, build wall-clock stolen from agents (pre-commit waiting), and Claude
tokens. Each kind is judged alone against the status quo (no overlap credit); the portfolio line assumes the kinds'
catches are independent, which overstates it.

Every parameter carries a label: MEASURED (read from census / pilot, with its source) or ASSUMED (lo..hi uniform).
A conclusion is ROBUST when it holds in >= 90% of draws.

Usage: testing_investment_sim.py [--census PATH] [--mutmut PATH] [--draws N] [--seed S] [--out PATH]
"""
import argparse
import json
import os
import random
import statistics
import sys

SCRATCH = "/mnt/d/ClaudeWork/rimmandrake/testing_sim"
AREAS = ("csharp", "xml", "python_tooling", "machinery")
LATE = ("review", "live", "owner")
EARLY = ("offline", "testq")

# ---- ASSUMED economics (agent-minutes are the common unit) ----
ECON = {
    "late_cost_review": (25, 60),   # agent-min: GPT/peer review finds it -> file, reopen, fix, re-review
    "late_cost_live": (40, 120),    # agent-min: a live round finds it -> triage MOD/SITE/HARNESS, fix, redeploy, re-run
    "late_cost_owner": (90, 300),   # agent-min equivalent incl. owner attention and trust
    "early_cost": (5, 20),          # agent-min: a test goes red at commit/nightly -> fix while context is warm
    "tok_per_agent_min": (50e3, 300e3),  # Claude tokens per agent-minute (mostly cached context re-sends)
}
# CPU minutes are not free in every lane: weight = agent-min displaced per CPU-min
LANE_CPU_WEIGHT = {
    "pre-commit": (0.0, 0.0),        # its cost is the wall clock, counted separately as stolen build time
    "nightly": (0.005, 0.03),        # longer nightly -> later red signal, more flake triage
    "idle-CPU": (0.0, 0.005),        # Archmagi / SteveDesktop idle hours
    "testq": (0.05, 0.25),           # SteveDesktop queue minutes displace other chains
    "pre-Arbiter": (0.02, 0.1),      # full-list round machine time
}

# ---- test kinds. eff = fraction of an area's LATE-found defects this kind would have caught early (ASSUMED) ----
# cost fields (per month): author = agent-min writing/triaging; cpu = CPU-min; wall_per_commit_s = seconds an agent
# waits per commit touching the area (pre-commit only). Ranges are lo..hi uniform.
KINDS = {
    "contracts_pydantic": {
        "lane": "pre-commit",
        "what": "static schema/contract checks on JSONL records, CLI args and def shapes (pydantic; modcheck for XML)",
        "eff": {"machinery": (0.05, 0.20), "python_tooling": (0.02, 0.08), "xml": (0.0, 0.03)},
        "author": (100, 300), "cpu": (5, 30), "wall_per_commit_s": (0.2, 1.5),
    },
    "red_first_defect_items": {
        "lane": "pre-commit",
        "what": "every DEFECT item ships a selftest seen RED for the reported reason before the fix (debug ladder rung 3)",
        "eff": {"machinery": (0.05, 0.15), "python_tooling": (0.05, 0.15), "csharp": (0.02, 0.08),
                "xml": (0.01, 0.05)},
        "author_per_item": (2, 15), "items": "defects", "cpu": (100, 600), "wall_per_commit_s": (0, 0),
        "wall_per_item_s": (5, 60),
    },
    "red_first_all_items": {
        "lane": "pre-commit",
        "what": "TDD everywhere: every BUILD item's acceptance artifact is a selftest seen RED first, then green",
        "eff": {"machinery": (0.15, 0.35), "python_tooling": (0.15, 0.35), "csharp": (0.04, 0.15),
                "xml": (0.02, 0.08)},
        "author_per_item": (2, 12), "items": "all", "cpu": (300, 1500), "wall_per_commit_s": (0, 0),
        "wall_per_item_s": (5, 60),
    },
    "hypothesis_property": {
        "lane": "nightly",
        "what": "property tests on parsers, ledger fold, sha/prefix matching, path classifiers",
        "eff": {"machinery": (0.03, 0.12), "python_tooling": (0.02, 0.08)},
        "author": (60, 240), "cpu": (150, 900), "wall_per_commit_s": (0, 0),
    },
    "mutation_mutmut": {
        "lane": "idle-CPU",
        "what": "mutmut on changed Python machinery files; survivors -> red-first tests (guides, does not catch)",
        "eff": {"machinery": (0.05, 0.20), "python_tooling": (0.02, 0.08)},
        "author": (150, 500), "cpu": None, "wall_per_commit_s": (0, 0),
    },
    "mutation_stryker_net": {
        "lane": "idle-CPU",
        "what": "Stryker.NET on mod C#; only kills where offline C# tests exist (FlowWorks), else all survive",
        "eff": {"csharp": (0.01, 0.06)},
        "author": (300, 900), "cpu": (3000, 15000), "wall_per_commit_s": (0, 0),
    },
    "northstar_bars": {
        "lane": "testq",
        "what": "write north-star bars for the ~80 DRAFT mods and run them as SteveDesktop chains",
        "eff": {"csharp": (0.05, 0.20), "xml": (0.05, 0.20)},
        "author": (300, 900), "cpu": (600, 1800), "wall_per_commit_s": (0, 0),
    },
    "testq_unmeasured_fix": {
        "lane": "testq",
        "what": "turn UNMEASURED testq rows into PASS/FAIL (harness work), retire dry filler chains",
        "eff": {"csharp": (0.02, 0.08), "xml": (0.02, 0.08), "machinery": (0.0, 0.04)},
        "author": (200, 600), "cpu": (0, 0), "wall_per_commit_s": (0, 0),
    },
    "archmagi_full_list": {
        "lane": "pre-Arbiter",
        "what": "more full-list rounds on Archmagi before the Arbiter (cold load ~25 min + ~0.7 h round)",
        "eff": {"csharp": (0.02, 0.08), "xml": (0.02, 0.08)},
        "author": (120, 480), "cpu": (300, 900), "wall_per_commit_s": (0, 0),
    },
}

MUTMUT_DEFAULT = {"mutants_per_line": 1293 / 923, "s_per_mutant": 0.58, "score": 888 / 1293,
                  "source": "pilot arbiter_tiers.py 2026-10-27 (MEASURED)"}
MUT_LINES_PER_MONTH = (8000, 40000)   # ASSUMED: changed Python machinery lines re-mutated per month (incremental)
MUT_S_PER_MUTANT_SCALE = (1.0, 8.0)   # ASSUMED: slower selftests than the pilot's 0.6 s one


def load_census(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def measured(census):
    """Monthly defects per area and the late/early channel mix, from the census. MEASURED, with the two
    redistributions (mod_unspecified -> csharp/xml by their ratio; unknown kind -> all areas by share) stated."""
    L = census["ledger"]
    kx = L["kind_x_channel"]
    days = census.get("days", 30)
    scale = 30.0 / days
    cells = {}
    for key, n in kx.items():
        kind, ch = key.split("|")
        cells.setdefault(kind, {}).setdefault(ch, 0)
        cells[kind][ch] += n
    mu = cells.pop("mod_unspecified", {})
    cs, xm = sum(cells.get("csharp", {}).values()), sum(cells.get("xml", {}).values())
    for ch, n in mu.items():
        cells.setdefault("csharp", {})[ch] = cells["csharp"].get(ch, 0) + n * cs / max(cs + xm, 1)
        cells.setdefault("xml", {})[ch] = cells["xml"].get(ch, 0) + n * xm / max(cs + xm, 1)
    unk = cells.pop("unknown", {})
    tot_known = sum(sum(cells.get(a, {}).values()) for a in AREAS)
    for a in AREAS:
        share = sum(cells.get(a, {}).values()) / max(tot_known, 1)
        for ch, n in unk.items():
            cells[a][ch] = cells[a].get(ch, 0) + n * share
    out = {}
    for a in AREAS:
        c = cells.get(a, {})
        known = sum(v for k, v in c.items() if k != "unknown")
        late = sum(c.get(k, 0) for k in LATE)
        late_frac = late / known if known else 0.0
        late_n = (late + c.get("unknown", 0) * late_frac) * scale
        mix = {k: c.get(k, 0) / late if late else 0 for k in LATE}
        out[a] = {"defects": sum(c.values()) * scale, "late": late_n, "late_frac": late_frac, "late_mix": mix,
                  "commits": census["git"]["commits_touching"].get(a, 0) * scale}
    return out


def u(rng, rr):
    lo, hi = rr
    return lo if lo == hi else rng.uniform(lo, hi)


def draw_one(rng, M, census, mut):
    econ = {k: u(rng, v) for k, v in ECON.items()}
    late_cost = {a: sum(M[a]["late_mix"][ch] * econ["late_cost_" + ch] for ch in LATE) for a in AREAS}
    items = census["ledger"]["items_filed"] * 30.0 / census.get("days", 30)
    defects_tot = sum(M[a]["defects"] for a in AREAS) or 1
    res = {}
    for k, spec in KINDS.items():
        caught, saved = 0.0, 0.0
        for a, rr in spec["eff"].items():
            e = u(rng, rr)
            c = M[a]["late"] * e
            caught += c
            saved += c * max(late_cost[a] - econ["early_cost"], 0)
        n_items = 0.0
        if "author_per_item" in spec:
            if spec["items"] == "defects":
                n_items = sum(M[a]["defects"] for a in spec["eff"])
            else:
                n_items = items * sum(M[a]["defects"] for a in spec["eff"]) / defects_tot
            author = n_items * u(rng, spec["author_per_item"])
        else:
            author = u(rng, spec["author"])
        if spec["cpu"] is None:   # mutmut: lines x mutants/line x s/mutant, pilot MEASURED, scale ASSUMED
            cpu = (u(rng, MUT_LINES_PER_MONTH) * mut["mutants_per_line"] * mut["s_per_mutant"]
                   * u(rng, MUT_S_PER_MUTANT_SCALE)) / 60.0
        else:
            cpu = u(rng, spec["cpu"])
        commits = sum(M[a]["commits"] for a in spec["eff"])
        wall = (commits * u(rng, spec["wall_per_commit_s"]) + n_items * u(rng, spec.get("wall_per_item_s", (0, 0))))/60.0
        cpu_cost = cpu * u(rng, LANE_CPU_WEIGHT[spec["lane"]])
        spent = author + wall + cpu_cost
        value_per_unit_eff = sum(M[a]["late"] * max(late_cost[a] - econ["early_cost"], 0) for a in spec["eff"])
        breakeven = spent / value_per_unit_eff if value_per_unit_eff else float("inf")
        res[k] = {"breakeven_eff": breakeven, "caught": caught, "saved": saved, "spent": spent, "net": saved - spent, "cpu_min": cpu,
                  "wall_stolen_min": wall, "author_min": author,
                  "tokens": author * econ["tok_per_agent_min"]}
    return res


def simulate(census, mut=None, draws=4000, seed=7):
    mut = mut or MUTMUT_DEFAULT
    M = measured(census)
    rng = random.Random(seed)
    runs = [draw_one(rng, M, census, mut) for _ in range(draws)]
    summary = {}
    for k in KINDS:
        col = {f: sorted(r[k][f] for r in runs) for f in runs[0][k]}
        q = lambda f, p: col[f][min(int(p * draws), draws - 1)]  # noqa: E731
        summary[k] = {"lane": KINDS[k]["lane"], "what": KINDS[k]["what"],
                      "p_net_positive": sum(1 for r in runs if r[k]["net"] > 0) / draws,
                      **{f: {"p10": round(q(f, .1), 4), "p50": round(q(f, .5), 4), "p90": round(q(f, .9), 4)}
                         for f in col}}
    ranks = {k: [] for k in KINDS}
    for r in runs:
        order = sorted(KINDS, key=lambda k: -r[k]["net"])
        for i, k in enumerate(order):
            ranks[k].append(i + 1)
    for k in KINDS:
        summary[k]["rank_p50"] = statistics.median(ranks[k])
        summary[k]["p_top3"] = sum(1 for x in ranks[k] if x <= 3) / draws
        spec = KINDS[k]
        wl = sum(M[a]["late"] for a in spec["eff"]) or 1
        eff_lo = sum(M[a]["late"] * rr[0] for a, rr in spec["eff"].items()) / wl
        summary[k]["eff_lo_weighted"] = round(eff_lo, 4)
        # ROBUST: pays in >= 90% of draws AND even the pessimistic assumed efficacy clears the p90 break-even,
        # so the verdict does not hinge on the efficacy guess
        summary[k]["robust"] = (summary[k]["p_net_positive"] >= 0.9
                                and summary[k]["breakeven_eff"]["p90"] <= eff_lo)
    port = []
    for r in runs:
        port.append(sum(r[k]["net"] for k in KINDS if summary[k]["robust"]))
    port.sort()
    return {"measured": {a: {kk: (round(v, 2) if isinstance(v, float) else v) for kk, v in M[a].items()}
                         for a in AREAS},
            "mutmut": mut, "draws": draws, "seed": seed, "kinds": summary,
            "ranking": sorted(KINDS, key=lambda k: (-summary[k]["p_net_positive"], summary[k]["rank_p50"])),
            "portfolio_robust_net_p50": round(port[len(port) // 2], 1),
            "labels": {"MEASURED": "census.json (ledger/git/testq/nightly, last 30 days) + mutmut pilot",
                       "ASSUMED": {"ECON": ECON, "LANE_CPU_WEIGHT": LANE_CPU_WEIGHT,
                                   "MUT_LINES_PER_MONTH": MUT_LINES_PER_MONTH,
                                   "MUT_S_PER_MUTANT_SCALE": MUT_S_PER_MUTANT_SCALE,
                                   "KINDS": {k: {f: v for f, v in s.items() if f not in ("what", "lane")}
                                             for k, s in KINDS.items()}}}}


def render(res):
    lines = ["kind                   lane         P(net>0) rank50 top3 breakeven-eff p50/p90 vs eff_lo  caught/mo p50"
             "  net agent-min p10/p50/p90   CPU-min p50  stolen-min p50  Mtok p50"]
    for k in res["ranking"]:
        s = res["kinds"][k]
        lines.append(f"{k:<22} {s['lane']:<12} {s['p_net_positive']:>7.2f} {s['rank_p50']:>6} {s['p_top3']:>5.2f}"
                     f" {s['breakeven_eff']['p50']:>8.3f}/{s['breakeven_eff']['p90']:.3f} vs {s['eff_lo_weighted']:.3f}"
                     f" {s['caught']['p50']:>13.1f} {s['net']['p10']:>9.0f}/{s['net']['p50']:.0f}/{s['net']['p90']:.0f}"
                     f" {s['cpu_min']['p50']:>12.0f} {s['wall_stolen_min']['p50']:>15.0f} "
                     f"{s['tokens']['p50'] / 1e6:>8.1f}" + ("  ROBUST" if s["robust"] else ""))
    lines.append(f"portfolio of ROBUST kinds, net agent-min/month p50 (independence; overstated): "
                 f"{res['portfolio_robust_net_p50']}")
    return "\n".join(lines)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--census", default=os.path.join(SCRATCH, "census.json"))
    ap.add_argument("--mutmut", default=os.path.join(SCRATCH, "mutmut", "summary.json"))
    ap.add_argument("--draws", type=int, default=4000)
    ap.add_argument("--seed", type=int, default=7)
    ap.add_argument("--out", default=os.path.join(SCRATCH, "sim_result.json"))
    a = ap.parse_args(argv)
    census = load_census(a.census)
    mut = dict(MUTMUT_DEFAULT)
    if os.path.exists(a.mutmut):
        with open(a.mutmut, encoding="utf-8") as f:
            m = json.load(f)
        n = m.get("killed", 0) + m.get("survived", 0)
        if n:
            mut["score"] = m["killed"] / n
    res = simulate(census, mut, a.draws, a.seed)
    if a.out:
        with open(a.out, "w", encoding="utf-8") as f:
            json.dump(res, f, indent=1)
    print(render(res))
    return 0


if __name__ == "__main__":
    sys.exit(main())
