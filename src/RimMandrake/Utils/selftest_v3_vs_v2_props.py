#!/usr/bin/env python3
"""Property tests (Hypothesis) for v3_vs_v2.judge_week -- the weekly v3-versus-v2 verdict.

Run through the REAL classify() with the pinned rules (v3_vs_v2_rules.json) and with generated verdict thresholds:
  P1 improving one metric's value in its better direction never lowers the verdict (WORSE < NOT_SHOWN < SUPERIOR);
     it may only lift UNMEASURED by measuring nothing new -- so UNMEASURED stays UNMEASURED.
  P2 a veto primary that reads WORSE always blocks SUPERIOR; so does any guard that reads WORSE.
  P3 a counterfactual can only take BETTER back: the verdict with a MEASURED counterfactual is never higher.
  P4 UNMEASURED exactly when fewer than min_primary_measured primaries are measured or ite_wk is not.
Deterministic (derandomize, no example database): the same examples every run. Needs hypothesis (pinned in
infrastructure/stevedesktop/mutation_requirements.txt). MUTANTS_HUNT_ON_IDLE_STEVE.
"""
import copy
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import v3_vs_v2 as V  # noqa: E402
try:
    from hypothesis import given, settings, strategies as st, HealthCheck  # noqa: E402
except ImportError:                    # pinned in infrastructure/stevedesktop/mutation_requirements.txt
    print("hypothesis is not installed: UNMEASURED, not a pass or a fail")
    sys.exit(0)

RULES = V.load_rules()
METRICS = RULES["metrics"]
KEYS = [m["key"] for m in METRICS]
PRIMARY = [m["key"] for m in METRICS if m["group"] == "primary"]
GUARD = [m["key"] for m in METRICS if m["group"] == "guard"]
RANK = {"WORSE": 0, "NOT_SHOWN": 1, "SUPERIOR": 2}
SET = settings(max_examples=300, derandomize=True, database=None, deadline=None,
               suppress_health_check=[HealthCheck.too_slow])
FAILS = []
SEEN = {}          # verdicts the generator reached -- a property over only UNMEASURED weeks proves nothing


def check(cond, msg):
    print(("ok    " if cond else "FAIL  ") + msg)
    if not cond:
        FAILS.append(msg)


val = st.floats(min_value=0.0, max_value=200.0, allow_nan=False, allow_infinity=False)


@st.composite
def case(draw, rules_strategy=False):
    rules = copy.deepcopy(RULES)
    if rules_strategy:
        n = len(PRIMARY)
        rules["verdict"]["min_primary_measured"] = draw(st.integers(1, n))
        rules["verdict"]["superior_min_better"] = draw(st.integers(1, n))
        rules["verdict"]["worse_min_worse"] = draw(st.integers(1, n))
        rules["verdict"]["superior_veto"] = draw(st.lists(st.sampled_from(PRIMARY), unique=True, max_size=n))
    ref, week = {}, {}
    for m in METRICS:
        k = m["key"]
        if draw(st.integers(0, 9)) > 0:          # mostly baselined
            x = V._x(draw(val), m["scale"])
            ref[k] = {"x": x, "band": draw(st.floats(0.0, 2.0)), "value": draw(st.floats(0.1, 100.0))}
        if draw(st.integers(0, 9)) > 0:          # mostly measured
            week[k] = {"v": draw(val)}
    return rules, ref, week


def verdict(week, ref, rules, cf=None):
    v = V.judge_week(week, ref, rules, cf)["verdict"]
    SEEN[v] = SEEN.get(v, 0) + 1
    return v


def improve(m, v, step):
    return v + step if m["better"] == "higher" else max(0.0, v - step)


@SET
@given(case(), st.sampled_from(PRIMARY + GUARD), st.floats(0.01, 100.0))
def p1(c, key, step):
    rules, ref, week = c
    m = next(x for x in METRICS if x["key"] == key)
    if key not in week or m["better"] == "none":
        return
    before = verdict(week, ref, rules)
    w2 = copy.deepcopy(week)
    w2[key]["v"] = improve(m, w2[key]["v"], step)
    after = verdict(w2, ref, rules)
    if before == "UNMEASURED" or after == "UNMEASURED":
        assert before == after, (key, before, after)
    else:
        assert RANK[after] >= RANK[before], (key, week[key], w2[key], before, after)


@SET
@given(case(rules_strategy=True), st.floats(0.01, 100.0))
def p1_any_rules(c, step):
    rules, ref, week = c
    for key in PRIMARY:
        m = next(x for x in METRICS if x["key"] == key)
        if key not in week:
            continue
        before = verdict(week, ref, rules)
        w2 = copy.deepcopy(week)
        w2[key]["v"] = improve(m, w2[key]["v"], step)
        after = verdict(w2, ref, rules)
        if "UNMEASURED" not in (before, after):
            assert RANK[after] >= RANK[before], (key, before, after, rules["verdict"])


@SET
@given(case(rules_strategy=True))
def p2(c):
    rules, ref, week = c
    r = V.judge_week(week, ref, rules)
    vetoed = [k for k in r["worse"] if k in rules["verdict"]["superior_veto"]]
    if vetoed or r["guard_worse"]:
        assert r["verdict"] != "SUPERIOR", (vetoed, r["guard_worse"])


@SET
@given(case(), st.dictionaries(st.sampled_from(PRIMARY), st.tuples(val, val), max_size=len(PRIMARY)))
def p3(c, ranges):
    rules, ref, week = c
    cf = {"status": "MEASURED", "range": {k: [min(a, b), max(a, b)] for k, (a, b) in ranges.items()}}
    plain, with_cf = verdict(week, ref, rules), verdict(week, ref, rules, cf)
    if "UNMEASURED" in (plain, with_cf):
        assert plain == with_cf
    else:
        assert RANK[with_cf] <= RANK[plain], (plain, with_cf)


@SET
@given(case(rules_strategy=True))
def p4(c):
    rules, ref, week = c
    r = V.judge_week(week, ref, rules)
    measured = [k for k in PRIMARY if r["per"][k]["class"] in ("BETTER", "SAME", "WORSE")]
    ite = r["per"]["ite_wk"]["class"] in ("BETTER", "SAME", "WORSE")
    want = len(measured) < rules["verdict"]["min_primary_measured"] or not ite
    assert (r["verdict"] == "UNMEASURED") == want, (len(measured), ite, r["verdict"])


def run(fn, label):
    try:
        fn()
        check(True, label)
    except AssertionError as e:
        check(False, "%s -- falsified: %s" % (label, str(e)[:400]))


def main():
    run(p1, "P1 improving one primary/guard value never lowers the verdict (pinned rules)")
    run(p1_any_rules, "P1 ... under generated verdict thresholds and veto lists")
    run(p2, "P2 a veto primary or a guard reading WORSE always blocks SUPERIOR")
    run(p3, "P3 a MEASURED counterfactual never raises the verdict")
    run(p4, "P4 UNMEASURED iff < min_primary_measured primaries measured or ite_wk unmeasured")
    check(all(SEEN.get(v, 0) >= 20 for v in ("UNMEASURED", "WORSE", "NOT_SHOWN", "SUPERIOR")),
          "the generator reaches every verdict (>= 20 each): %s" % sorted(SEEN.items()))
    print("%d failure(s)" % len(FAILS))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
