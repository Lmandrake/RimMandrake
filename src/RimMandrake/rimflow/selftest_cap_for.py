#!/usr/bin/env python3
"""selftest_cap_for.py: the promises of design/specs/2026-11-27-cap-for/boundary.md (each t_ function is one promise, by
name). Offline: fake run records in a temp folder (the shape detached_helper.finish writes: unit, item, model, tokens in
weighted_v2, cost_usd, out). Written before cap_for.py; seen failing on the base (the module absent).

    python3 src/RimMandrake/rimflow/selftest_cap_for.py

Each check prints its worst value, its limit and how many cases it read.
"""
import json
import os
import random
import re
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
for _p in (HERE, os.path.join(REPO, "src", "RimMandrake", "Utils"), os.path.join(REPO, "src", "RimMandrake")):
    if _p not in sys.path:
        sys.path.insert(0, _p)
sys.dont_write_bytecode = True
os.environ["RM_UNDER_SELFTEST"] = "1"
WT_PER_USD = 250_000        # role_launch.WT_PER_LIST_USD: 1e6 / Opus 5.5's 4 $/MTok input (checked in t_1)


def CF():
    import cap_for
    return cap_for


def p90_by_hand(xs):
    """The nearest-rank p90 of design/specs/2026-11-26-script-candidates/measure/rows.py (pct), written out again here
    so the test does not read the figure from the code under test."""
    xs = sorted(xs)
    return xs[min(len(xs) - 1, int(len(xs) * 0.9))]


_seq = [0]


def put(d, item, tokens=None, usd=None, model="opus", capped=False, unit=None):
    """One fake finished run record (and its out file) in folder d. tokens=None and usd given: a legacy record."""
    _seq[0] += 1
    unit = unit or "rm-detached-bench-%s-%d" % (item.lower().replace("_", "-")[:30], _seq[0])
    out = os.path.join(d, unit + ".out.json")
    rec = {"unit": unit, "item": item, "model": model, "status": "finished", "at": 1_800_000_000 + _seq[0] * 60,
           "budget_usd": 120.0, "out": out}
    if tokens is not None:
        rec.update(tokens=int(tokens), token_unit="weighted_v2", cost_usd=tokens / WT_PER_USD)
    elif usd is not None:
        rec.update(cost_usd=usd)
    with open(os.path.join(d, unit + ".json"), "w") as f:
        json.dump(rec, f)
    res = {"type": "result", "subtype": "error_max_budget_usd" if capped else "success"}
    with open(out, "w") as f:
        json.dump(res, f)
    return unit


def folder():
    return tempfile.mkdtemp(prefix="capfor_")


def run_cli(*args):
    p = subprocess.run([sys.executable, os.path.join(HERE, "cap_for.py")] + list(args), capture_output=True, text=True,
                       timeout=120)        # budget: danger=a hung child hangs the suite (hang guard, a run takes <2 s)
    return p.returncode, p.stdout + p.stderr


def t_the_cap_is_not_below_the_verbs_p90():
    cf = CF()
    import role_launch as RL
    assert float(RL.WT_PER_LIST_USD) == WT_PER_USD, "the test's rate %d is not role_launch's %s" % (
        WT_PER_USD, RL.WT_PER_LIST_USD)
    rng = random.Random(20261127)
    worst, cases = None, 0
    # the regimes: n from the floor to 60, three cost shapes (flat, long-tailed, one huge run), some legacy records
    # (cost_usd only), some runs ended at their cap, other verbs and the other model beside them
    for n in list(range(cf.FLOOR_RUNS, 61)):
        for shape in ("flat", "tail", "spike"):
            d = folder()
            costs = []
            for i in range(n):
                if shape == "flat":
                    t = rng.randint(2_000_000, 3_000_000)
                elif shape == "tail":
                    t = int(rng.lognormvariate(14.5, 1.0))
                else:
                    t = 40_000_000 if i == 0 else rng.randint(500_000, 900_000)
                costs.append(t)
                if i % 7 == 3:
                    put(d, "RIMMANDRAKE_FIX_THING_%d" % i, usd=t / WT_PER_USD)       # a legacy record: dollars only
                else:
                    put(d, "RIMMANDRAKE_FIX_THING_%d" % i, tokens=t, capped=(i % 11 == 5))
            for i in range(5):
                put(d, "RIMMANDRAKE_BUILD_OTHER_%d" % i, tokens=99_000_000)              # another verb: not read
                put(d, "RIMMANDRAKE_FIX_SONNET_%d" % i, tokens=99_000_000, model="sonnet")
            r = cf.cap_for("FIX", model="opus", records=d)
            want = p90_by_hand(costs)
            assert r["state"] == "MEASURED", (n, shape, r["line"])
            assert r["n"] == n, "read %s runs of FIX on opus, %d made (%s)" % (r["n"], n, r["line"])
            assert r["p90_wt"] == want, "p90 %s, by hand %s (n=%d %s)" % (r["p90_wt"], want, n, shape)
            assert r["cap_wt"] >= want, "cap %s below p90 %s (n=%d %s)" % (r["cap_wt"], want, n, shape)
            assert abs(r["cap_usd"] - RL.weighted_to_list_usd(r["cap_wt"])) < 1e-9, r
            ratio = r["cap_wt"] / want
            worst = ratio if worst is None else min(worst, ratio)
            cases += 1
    # the evidence's own case (G11): caps of 10 below a p90 of 12; the cap must now sit at or above the 12
    d = folder()
    for i, usd in enumerate([4, 6, 7, 8, 9, 10, 10, 11, 12, 12, 13]):
        put(d, "FIX_PLAIN_%d" % i, tokens=usd * WT_PER_USD, capped=(usd == 10))
    r = cf.cap_for("FIX", records=d)
    assert r["state"] == "MEASURED" and r["cap_usd"] >= 12, r["line"]
    assert r["capped_n"] == 2, "2 runs ended at their cap, read %s" % r["capped_n"]
    cases += 1
    print("   cap/p90: worst %.3f, limit >= 1.000 (the bar), cases %d" % (worst, cases))


def t_a_verb_with_no_record_reads_unmeasured_and_names_its_fallback():
    cf = CF()
    d = folder()
    pooled = []
    for i in range(30):
        t = 1_000_000 + i * 100_000
        pooled.append(t)
        put(d, "RIMMANDRAKE_READ_PAGE_%d" % i, tokens=t)
    r = cf.cap_for("TRIAGE", records=d)
    assert r["state"] == "UNMEASURED", r["line"]
    assert r["line"].startswith("UNMEASURED"), r["line"]
    assert "0 runs" in r["cause"] and str(cf.FLOOR_RUNS) in r["cause"], r["cause"]
    assert r["cap_wt"] == cf.P90_MULTIPLE * p90_by_hand(pooled), (r["cap_wt"], p90_by_hand(pooled))
    assert "fallback" in r["line"] and "every verb" in r["fallback_from"], r["line"]
    cases = 1
    # a verb with a few runs, dearer than the pool: the fallback never sits below its own runs' p90
    for k in range(1, cf.FLOOR_RUNS):
        dk = folder()
        for i, t in enumerate(pooled):
            put(dk, "RIMMANDRAKE_READ_PAGE_%d" % i, tokens=t)
        own = [20_000_000 + j * 1_000_000 for j in range(k)]
        for j, t in enumerate(own):
            put(dk, "RIMMANDRAKE_STAGE_X%d_%d" % (k, j), tokens=t)
        r = cf.cap_for("STAGE", records=dk)
        assert r["state"] == "UNMEASURED" and ("%d runs" % r["n"]) in r["cause"], r["line"]
        assert r["cap_wt"] >= max(r["p90_wt"] or 0, p90_by_hand(pooled + own)), r["line"]
        cases += 1
    # an empty folder: no runs at all, so no fallback number; the line says the launch must name its cap
    e = folder()
    rc, out = run_cli("FIX", "--records", e)
    assert rc == cf.EXIT_NO_NUMBER and "UNMEASURED" in out and "$" not in out, (rc, out)
    # a folder that cannot be read: COULD NOT LOOK, a non-zero exit, no number
    gone = os.path.join(e, "no_such_folder")
    rc, out = run_cli("FIX", "--records", gone)
    assert rc == cf.EXIT_COULD_NOT_LOOK and out.startswith("COULD NOT LOOK") and "$" not in out, (rc, out)
    assert not os.path.exists(gone), "looking made the folder"
    try:
        cf.cap_for("FIX", records=gone)
        raise AssertionError("cap_for on a missing folder returned a number")
    except cf.CouldNotLook:
        pass
    # an unreadable record file is counted on the line, never silently dropped
    put(d, "RIMMANDRAKE_READ_ZZ", tokens=1)
    with open(os.path.join(d, "rm-detached-bench-broken-1.json"), "w") as f:
        f.write("{not json")
    r = cf.cap_for("READ", records=d)
    assert "1 record file unreadable" in r["line"], r["line"]
    cases += 3
    print("   unmeasured / no number / could not look: worst - , limit every case right, cases %d" % cases)


def t_the_cap_line_names_danger_and_measured_need():
    cf = CF()
    d = folder()
    for i in range(12):
        put(d, "RIMMANDRAKE_JUDGE_ART_%d" % i, tokens=3_000_000 + i * 250_000)
    r = cf.cap_for("JUDGE", records=d)
    line = r["line"]
    need = {"the danger": "danger: a runaway run spends an account", "the p90": "p90 ", "the max": "max ",
            "the run count": "n=12", "the window": "window ", "the unit": "weighted_v2", "the list dollars": "$",
            "the multiple": "%dx p90" % cf.P90_MULTIPLE}
    missing = [k for k, v in need.items() if v not in line]
    assert not missing, "the cap line lacks %s: %s" % (missing, line)
    rc, out = run_cli("JUDGE", "--records", d)
    assert rc == 0 and out.strip() == line, (rc, out, line)
    src = open(os.path.join(HERE, "cap_for.py")).read()
    for name in ("FLOOR_RUNS", "P90_MULTIPLE"):
        m = re.search(r"^# budget: .*\n(?:# .*\n)*%s = " % name, src, re.M)
        assert m and "danger=" in m.group(0), "%s has no danger line above it" % name
    print("   cap line parts: worst missing %d, limit 0, cases %d" % (len(missing), len(need) + 3))


def t_the_cap_never_reaches_the_brief():
    cf = CF()
    import detached_helper as DH
    d = folder()
    for i in range(10):
        put(d, "RIMMANDRAKE_TRACE_SPEND_%d" % i, tokens=3_711_000 + i * 13_000)
    inner = ["claude", "-p", "--output-format", "json"]
    argv, r = cf.capped_argv("TRACE", inner, records=d)
    figs = {"%g" % r["cap_usd"], "%.2f" % r["cap_usd"], "%.1f" % r["cap_usd"], str(r["cap_wt"]),
            "{:,}".format(r["cap_wt"]), "%.1fM" % (r["cap_wt"] / 1e6)}
    i = argv.index("--cap-usd")
    assert os.path.basename(argv[1]) == "spend_watchdog.py" and argv[i + 1] == "%g" % r["cap_usd"], argv
    assert argv[argv.index("--") + 1:] == inner, "the claude argv was changed: %s" % argv
    # the brief a launch builds holds no form of the figure (footer, history, cards, command lines)
    clone = tempfile.mkdtemp(prefix="capfor_clone_")
    msg = DH.brief_message("Build the thing. Land it.", "RIMMANDRAKE_TRACE_SPEND_0", "BENCH", clone, max_s=3600)
    hits = sorted(f for f in figs if f in msg)
    assert not hits, "the brief holds the cap figure %s" % hits
    # cap_for builds no text a brief carries: its result has no brief or prompt field
    assert not ({"brief", "prompt", "message"} & set(r)), sorted(r)
    print("   cap figures in the brief: worst %d, limit 0, cases %d forms" % (len(hits), len(figs)))


def main():
    failed = 0
    tests = [t_the_cap_is_not_below_the_verbs_p90, t_a_verb_with_no_record_reads_unmeasured_and_names_its_fallback,
             t_the_cap_line_names_danger_and_measured_need, t_the_cap_never_reaches_the_brief]
    for t in tests:
        try:
            t()
            print("PASS", t.__name__)
        except Exception as e:  # noqa: BLE001 - a promise whose test cannot run is a FAIL, never a crash
            failed += 1
            print("FAIL", t.__name__, "%s: %s" % (type(e).__name__, str(e)[:400]))
    print("FAILED %d of %d" % (failed, len(tests)) if failed else "ALL PASS (%d)" % len(tests))
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
