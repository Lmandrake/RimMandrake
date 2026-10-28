#!/usr/bin/env python3
"""Mutation-hardening tests for v3_vs_v2.py (V3_VS_V2_HARDEN_MUTATION_SURVIVORS).

selftest_v3_vs_v2 + _props left 43.5% of the mutants alive. This file pins what decides the owner's rule (>= 4 of 7
primaries BETTER, no guard or veto primary WORSE): the classify band edges, kill_above, the tie in the WORSE rule, the
counterfactual range edges, the noise band's arithmetic (reference / _boot), standing, the week edges, settled's failure
flags and the pin text. Each check names the mutant family it kills. Synthetic data only; no real ledger, transcript
or repo."""
import copy
import datetime as dt
import json
import math
import os
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import v3_vs_v2 as V  # noqa: E402

FAILS = []
REACHED = []


def check(name, ok, detail=""):
    print(("ok    " if ok else "FAIL  ") + name + ("" if ok else "  -- " + str(detail)))
    if not ok:
        FAILS.append(name)


R = V.load_rules()
MET = {m["key"]: m for m in R["metrics"]}
pt = lambda v: {"v": v, "mark": "MEASURED"}  # noqa: E731

# ---------------------------------------------------------------- classify: edges of the verdict's atoms
mA = {"key": "a", "better": "lower", "scale": "abs", "group": "primary", "floor": 0.1}
mH = dict(mA, better="higher")
mN = dict(mA, better="none")
ref = {"a": {"x": 0.5, "band": 0.25, "value": 0.5}}
check("classify: |d| == band is SAME (edge inclusive)", V.classify(mA, pt(0.75), ref)[0] == "SAME" and V.classify(mA, pt(0.25), ref)[0] == "SAME")
check("classify: just past the band is decided", V.classify(mA, pt(0.76), ref)[0] == "WORSE" and V.classify(mA, pt(0.24), ref)[0] == "BETTER")
check("classify: higher-is-better flips the direction", V.classify(mH, pt(0.76), ref)[0] == "BETTER" and V.classify(mH, pt(0.24), ref)[0] == "WORSE")
check("classify: a report metric (better none) is never BETTER or WORSE", V.classify(mN, pt(9.0), ref)[0] == "SAME" and V.classify(mN, pt(-9.0), ref)[0] == "SAME")
c, z = V.classify(mA, pt(1.0), ref)
check("classify: z is d / band", c == "WORSE" and z == 2.0, (c, z))
c, z = V.classify(mA, pt(0.5), {"a": {"x": 0.5, "band": 0.0}})
check("classify: zero band, zero distance: SAME, z 0.0", c == "SAME" and z == 0.0, (c, z))
c, z = V.classify(mA, pt(0.9), {"a": {"x": 0.5, "band": 0.0}})
check("classify: zero band: any move is decided, z stays 0.0 (not None, not 1)", c == "WORSE" and z == 0.0, (c, z))
mK = dict(mA, group="guard", kill_above=0.5)
refK = {"a": {"x": 0.5, "band": 0.05, "value": 0.5}}
check("kill_above: exactly at the line is not past it", V.classify(mK, pt(0.5), refK)[0] == "SAME")
check("kill_above: past the line is WORSE even when the baseline was worse still", V.classify(mK, pt(0.51), {"a": {"x": 0.9, "band": 0.05}})[0] == "WORSE")
check("classify: no kill_above key, no kill", V.classify(mA, pt(0.51), {"a": {"x": 0.9, "band": 0.05}})[0] == "BETTER")
check("classify: log scale distance", V.classify(dict(mA, scale="log"), pt(100), {"a": {"x": math.log1p(100), "band": 0.1}})[0] == "SAME"
      and V.classify(dict(mA, scale="log"), pt(111), {"a": {"x": math.log1p(100), "band": 0.1}})[0] == "WORSE")

# ---------------------------------------------------------------- _x
check("_x log: log1p, floored at 0", V._x(0.5, "log") == math.log1p(0.5) and V._x(-3, "log") == 0.0 and V._x(0, "log") == 0.0)
check("_x abs: the float itself, negatives kept", V._x(-3, "abs") == -3.0 and V._x(7, "abs") == 7.0)

# ---------------------------------------------------------------- judge_week
REFV = {"done_wk": 800, "owner_wait_over_3d": 20, "already_ruled_wk": 4, "rework_share": 0.13, "close_no_level_share": 0.9,
        "verify_backlog": 500, "process_share": 0.6, "sub_ite_big_ctx_share": 0.3, "doing_live_lease_share": 0.5,
        "lapsed_open": 100, "contested_new_wk": 1, "ite_wk": 1.5e9, "ite_per_done": 2e6, "helpers_wk": 1000,
        "owner_msgs_wk": 400, "owner_active_h_wk": 80, "filed_wk": 1000, "net_wk": 200, "owner_resolve_med_d": 2.0,
        "vfail_share": 0.1, "seat_ite_share": 0.1, "all_ite_wk": 1.6e9}
REF = {k: {"value": v, "x": V._x(v, MET[k]["scale"]), "band": MET[k]["floor"], "context": []} for k, v in REFV.items()}


def week(**over):
    w = {k: pt(v) for k, v in REFV.items()}
    for k, v in over.items():
        w[k] = pt(v) if v is not None else V.U("blind")
    return w


def jw(w, cf=None):
    return V.judge_week(w, REF, R, cf)


# the WORSE rule: "at least 2 primaries WORSE and not outnumbered by BETTER": a tie is WORSE
j = jw(week(done_wk=200, verify_backlog=2000, rework_share=0.05, process_share=0.3))
check("WORSE rule: 2 WORSE vs 2 BETTER (a tie) is WORSE", j["verdict"] == "WORSE" and len(j["worse"]) == 2 and len(j["better"]) == 2, j["verdict"])
j = jw(week(done_wk=200, verify_backlog=2000, rework_share=0.05, process_share=0.3, close_no_level_share=0.5))
check("WORSE rule: 2 WORSE vs 3 BETTER is not WORSE", j["verdict"] == "NOT_SHOWN", j["verdict"])
j = jw(week(done_wk=200, verify_backlog=2000))
check("WORSE rule: 2 WORSE, none BETTER is WORSE", j["verdict"] == "WORSE")
# exactly 4 BETTER is SUPERIOR; the guard and veto stop it
SUP = dict(done_wk=2000, rework_share=0.05, verify_backlog=100, process_share=0.3)
check("SUPERIOR at exactly 4 BETTER", jw(week(**SUP))["verdict"] == "SUPERIOR")
for g, bad in (("lapsed_open", 900), ("contested_new_wk", 40), ("doing_live_lease_share", 0.0)):
    j = jw(week(**dict(SUP, **{g: bad})))
    check("guard %s WORSE stops SUPERIOR and is listed" % g, j["verdict"] != "SUPERIOR" and j["guard_worse"] == [g], (j["verdict"], j["guard_worse"]))
for v_, bad in (("rework_share", 0.5), ("owner_wait_over_3d", 200), ("already_ruled_wk", 100)):
    j = jw(week(**dict(SUP, **{v_: bad})))
    check("veto %s WORSE stops SUPERIOR" % v_, j["verdict"] != "SUPERIOR", (j["verdict"], j["worse"]))
j = jw(week(**dict(SUP, close_no_level_share=1.0)))
check("a non-veto primary WORSE does not stop SUPERIOR; it is listed in worse", j["verdict"] == "SUPERIOR" and j["worse"] == ["close_no_level_share"], j["worse"])
j = jw(week(**SUP))
check("judge_week lists the BETTER primaries", sorted(j["better"]) == sorted(SUP), j["better"])
_zv = next(v for v in range(1000, 3000) if round((math.log1p(v) - math.log1p(800)) / 0.1, 2) != round((math.log1p(v) - math.log1p(800)) / 0.1, 3))
check("per-metric bands are rounded to 2 places", jw(week(done_wk=_zv))["per"]["done_wk"]["bands"] == round((math.log1p(_zv) - math.log1p(800)) / 0.1, 2))
# counterfactual edges
cfr = lambda **k: {"status": "MEASURED", "range": {kk: list(vv) for kk, vv in k.items()}}  # noqa: E731
j = jw(week(**SUP), cfr(done_wk=(500, 2000)))
check("cf higher: v == p95 is inside the v2 range (not past)", j["per"]["done_wk"]["cf"] == "inside the v2 range" and j["per"]["done_wk"]["class_cf"] == "SAME", j["per"]["done_wk"])
j = jw(week(**SUP), cfr(done_wk=(500, 1999)))
check("cf higher: v above p95 is past the range; class stands", j["per"]["done_wk"]["cf"] == "past the v2 range" and "class_cf" not in j["per"]["done_wk"], j["per"]["done_wk"])
j = jw(week(**SUP), cfr(rework_share=(0.05, 0.2)))
check("cf lower: v == p5 is inside the v2 range", j["per"]["rework_share"]["cf"] == "inside the v2 range", j["per"]["rework_share"])
j = jw(week(**SUP), cfr(rework_share=(0.0501, 0.2)))
check("cf lower: v below p5 is past the range (compared with p5, not p95)", j["per"]["rework_share"]["cf"] == "past the v2 range", j["per"]["rework_share"])
j = jw(week(**SUP), cfr(rework_share=(0.01, 0.2)))
check("cf lower: v inside [p5, p95] is inside", j["per"]["rework_share"]["cf"] == "inside the v2 range")
j = jw(week(**SUP), cfr(rework_share=(0.01, 0.06)))
check("cf lower: p95 is not the edge for a lower-is-better metric", j["per"]["rework_share"]["cf"] == "inside the v2 range")
# cost
j = jw(week(ite_wk=1.0e9))
check("cost LOWER when ite_wk BETTER", j["cost"] == "LOWER", j["cost"])
j = jw(week(ite_per_done=1.0e6))
check("cost LOWER when only ite_per_done is BETTER", j["cost"] == "LOWER", j["cost"])
j = jw(week(ite_per_done=4.0e6))
check("cost HIGHER when only ite_per_done is WORSE", j["cost"] == "HIGHER", j["cost"])
j = jw(week(ite_wk=1.0e9, ite_per_done=4.0e6))
check("cost HIGHER beats LOWER", j["cost"] == "HIGHER")
check("cost SAME when both SAME", jw(week())["cost"] == "SAME")
j = jw(week(ite_wk=None, ite_per_done=None))
check("cost UNMEASURED when neither is measured", j["cost"] == "UNMEASURED" and j["verdict"] == "UNMEASURED", (j["cost"], j["verdict"]))
j = jw(week(ite_wk=1.5e9 * 1.23456789))
check("ite ratio rounds to 3 places", j["ite_ratio_to_v2"] == 1.235, j["ite_ratio_to_v2"])
check("measured count: 4 measured primaries is enough, 3 is not", jw(week(**SUP))["primary_measured"] == 7
      and jw(week(done_wk=2000, rework_share=0.05, owner_wait_over_3d=None, already_ruled_wk=None, close_no_level_share=None, verify_backlog=None))["verdict"] == "UNMEASURED"
      and jw(week(done_wk=2000, rework_share=0.05, owner_wait_over_3d=None, already_ruled_wk=None, close_no_level_share=None))["primary_measured"] == 4)
j = jw(week(done_wk=2000, rework_share=0.05, owner_wait_over_3d=None, already_ruled_wk=None, close_no_level_share=None))
check("four measured primaries (min_primary_measured) are judged, not UNMEASURED", j["verdict"] != "UNMEASURED", j["verdict"])

# ---------------------------------------------------------------- standing
h = lambda e, v, ratio=1.2, settled=True: {"end": e, "settled": settled, "verdict": v, "ite_ratio_to_v2": ratio}  # noqa: E731
s = V.standing([h("a", "NOT_SHOWN"), h("b", "WORSE"), h("c", "WORSE"), h("d", "NOT_SHOWN")], R)
check("standing: exactly 2 WORSE of 4 is WORSE", s["standing"] == "WORSE" and s["rule_reading"] == "WORSE", s)
s = V.standing([h("a", "SUPERIOR"), h("b", "WORSE"), h("c", "SUPERIOR"), h("d", "SUPERIOR")], R)
check("standing: one WORSE is not WORSE (and blocks SUPERIOR)", s["rule_reading"] == "NOT_SHOWN", s)
s = V.standing([h("a", "SUPERIOR"), h("b", "UNMEASURED"), h("c", "SUPERIOR"), h("d", "SUPERIOR"), h("e", "SUPERIOR")], R)
check("standing: UNMEASURED weeks are dropped before the last 4", s["weeks"] == ["a", "c", "d", "e"] and s["standing"] == "SUPERIOR", s)
s = V.standing([h("a", "WORSE"), h("b", "WORSE"), h("c", "NOT_SHOWN"), h("d", "NOT_SHOWN"), h("e", "SUPERIOR"), h("f", "SUPERIOR")], R)
check("standing: only the last 4 settled weeks count", s["weeks"] == ["c", "d", "e", "f"] and s["standing"] == "NOT_SHOWN", s)
s = V.standing([h("a", "SUPERIOR", 1.23456), h("b", "SUPERIOR", 1.23456), h("c", "SUPERIOR", 1.23456), h("d", "SUPERIOR", 1.23456)], R)
check("standing: cost median rounds to 3 places", s["cost_ratio_median"] == 1.235, s)
s = V.standing([h("a", "SUPERIOR", None), h("b", "SUPERIOR", 0), h("c", "SUPERIOR", 2.0), h("d", "SUPERIOR", 4.0)], R)
check("standing: weeks with no ratio are left out of the median", s["cost_ratio_median"] == 3.0, s)
s = V.standing([h("a", "SUPERIOR", None)], R)
check("standing: no ratios -> None", s["cost_ratio_median"] is None and s["standing"] == "PROVISIONAL")

# ---------------------------------------------------------------- reference: the noise band
days = [{"owner_wait_over_3d": pt(v)} for v in (10, 14, 30, 20, 26, 18, 22)]
v2 = {"weeks": {R["v2_history"]["reference_week"]: {"owner_wait_over_3d": pt(20), "done_wk": pt(800)},
                R["v2_history"]["context_weeks"][0]: {"owner_wait_over_3d": pt(11)},
                R["v2_history"]["context_weeks"][1]: {"owner_wait_over_3d": pt(12)}}, "days": days}
rf = V.reference(v2, R)["owner_wait_over_3d"]
xs = [math.log1p(v) for v in (10, 14, 30, 20, 26, 18, 22)]
sd = V.statistics.pstdev(xs)
want = max(R["band"]["z"] * sd * math.sqrt(2), MET["owner_wait_over_3d"]["floor"])
check("reference: stock band = z * sd * sqrt(2) of the 7 day readings", rf["band"] == want and rf["sd"] == sd and rf["band_from"] == "days", rf)
check("reference: band_from days only when the days' noise beats the floor", rf["band"] > MET["owner_wait_over_3d"]["floor"])
check("reference: value, x and the context weeks are the tag week's and the two before", rf["value"] == 20 and rf["x"] == math.log1p(20) and rf["context"] == [11, 12], rf)
flat = copy.deepcopy(v2)
flat["days"] = [{"owner_wait_over_3d": pt(20)}] * 7
rf = V.reference(flat, R)["owner_wait_over_3d"]
check("reference: identical days -> the floor binds (band_from floor, noise 0)", rf["band"] == MET["owner_wait_over_3d"]["floor"] and rf["band_from"] == "floor" and rf["sd"] == 0.0, rf)
few = copy.deepcopy(v2)
few["days"] = days[:4]
rf = V.reference(few, R)["owner_wait_over_3d"]
check("reference: too few days -> no sd, band is exactly the floor", rf["sd"] is None and rf["band"] == MET["owner_wait_over_3d"]["floor"] and rf["band_from"] == "floor", rf)
nodays = {"weeks": v2["weeks"]}
rf = V.reference(nodays, R)["owner_wait_over_3d"]
check("reference: no days key -> floor", rf["sd"] is None and rf["band_from"] == "floor", rf)
rf = V.reference(v2, R)["owner_resolve_med_d"]
check("reference: a metric with no tag-week point has no baseline and says why", rf["value"] is None and rf["x"] is None and rf["band"] is None
      and rf["why"] == "not measured" and rf["context"] == [None, None], rf)
v2w = copy.deepcopy(v2)
v2w["weeks"][R["v2_history"]["reference_week"]]["filed_wk"] = {"v": None, "why": "ledger blind"}
rf = V.reference(v2w, R)["filed_wk"]
check("reference: the unmeasured point's own why is kept", rf["why"] == "ledger blind" and rf["value"] is None, rf)
# a 'none' kind metric gets the floor even when days exist
v2n = copy.deepcopy(v2)
v2n["weeks"][R["v2_history"]["reference_week"]]["owner_resolve_med_d"] = pt(1.5)
v2n["days"] = [dict(d, owner_resolve_med_d=pt(v)) for d, v in zip(days, (1, 2, 3, 4, 5, 6, 7))]
rf = V.reference(v2n, R)["owner_resolve_med_d"]
check("reference: kind none has no day band", rf["sd"] is None and rf["band"] == MET["owner_resolve_med_d"]["floor"], rf)
# count metric: the band is from the resampled week sums (spec: seed fixed, 2000 resamples)
cdays = [{"done_wk": pt(v)} for v in (100, 120, 80, 110, 90, 105, 95)]
bt = V._boot(MET["done_wk"], cdays, R)
check("_boot count: 2000 resamples of the week sum, on the log scale", len(bt) == R["band"]["resamples"] and all(math.log1p(80 * 7) <= x <= math.log1p(120 * 7) for x in bt), (len(bt), min(bt), max(bt)))
import random  # noqa: E402
rng = random.Random(R["band"]["seed"])
vals = [100, 120, 80, 110, 90, 105, 95]
exp0 = math.log1p(sum(vals[rng.randrange(7)] for _ in range(7)))
check("_boot count: reproducible from the pinned seed", bt[0] == exp0, (bt[0], exp0))
zdays = [{"owner_msgs_wk": pt(0)} for _ in range(5)] + [{}, {}]
bz = V._boot(MET["owner_msgs_wk"], zdays, R)
check("_boot count: a quiet day (0 or unmeasured, inside a measured week) adds zero", bz and all(x == 0.0 for x in bz), bz and (min(bz), max(bz)))
five = [{"done_wk": pt(v)} for v in (1, 2, 3, 4, 5)] + [{}, {}]
check("_boot: 5 measured days are enough", V._boot(MET["done_wk"], five, R) is not None)
check("_boot: 4 measured days are not", V._boot(MET["done_wk"], five[:4] + [{}, {}, {}], R) is None)
sk = [{"owner_wait_over_3d": pt(v)} for v in (5, 6, 7, 8, 9)] + [{}, {}]
check("_boot stock: the measured days' readings on the log scale, in order",
      V._boot(MET["owner_wait_over_3d"], sk, R) == [math.log1p(v) for v in (5, 6, 7, 8, 9)])
ska = [{"doing_live_lease_share": pt(v)} for v in (0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7)]
check("_boot stock abs: the readings themselves", V._boot(MET["doing_live_lease_share"], ska, R) == [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7])
rd = [{"rework_share": {"v": 0.1, "num": 1, "den": 10}} for _ in range(7)]
br = V._boot(MET["rework_share"], rd, R)
check("_boot ratio: sum(num)/sum(den) of the resample", len(br) == R["band"]["resamples"] and all(abs(x - 0.1) < 1e-12 for x in br), (len(br), br[:2]))
rz = [{"rework_share": {"v": 0.0, "num": 0, "den": 10}} for _ in range(7)]
check("_boot ratio: zero numerators give zero", all(x == 0.0 for x in V._boot(MET["rework_share"], rz, R)))
rn = [{"rework_share": {"v": 0.0}} for _ in range(7)]
check("_boot ratio: no denominator at all -> no resample (empty), not zeros", V._boot(MET["rework_share"], rn, R) == [])
ru = [{"rework_share": {"v": 0.2, "num": 2, "den": 10}} for _ in range(3)] + [{"rework_share": {"v": 0.0, "num": 0, "den": 0}} for _ in range(4)]
check("_boot ratio: a day with den 0 adds nothing to the denominator", all(abs(x - 0.2) < 1e-12 for x in V._boot(MET["rework_share"], ru, R) if x is not None) )
check("_boot: an unknown kind has no band", V._boot(dict(MET["done_wk"], kind="none"), cdays, R) is None)

# ---------------------------------------------------------------- the pin text
TMP = tempfile.mkdtemp(prefix="selftest_v3v2mut_")
alt = os.path.join(TMP, "r.json")
open(alt, "w").write('{"a": 1}')
sha = V.rules_sha(alt)
saved = V.RULE_PINS
try:
    V.RULE_PINS = [("0" * 64, "2026-01-01", "first", True), ("1" * 64, "2026-01-02", "second", False), (sha, "2026-02-02", "third", False)]
    ok, txt = V.rules_status(alt)
    check("rules_status: matches the LAST pin; lists every late amendment's date", ok and txt == "rule sha256 %s, pinned 2026-02-02 (third); AMENDED AFTER v3 DATA EXISTED on 2026-01-02, 2026-02-02" % sha[:12], txt)
    V.RULE_PINS = [("0" * 64, "2026-01-01", "first", True), (sha, "2026-02-02", "third", True)]
    ok, txt = V.rules_status(alt)
    check("rules_status: no late amendment, no warning", ok and txt == "rule sha256 %s, pinned 2026-02-02 (third)" % sha[:12], txt)
    V.RULE_PINS = [(sha, "2026-01-01", "first", True), ("2" * 64, "2026-01-02", "second", True)]
    ok, txt = V.rules_status(alt)
    check("rules_status: only the last pin counts (an older pin's hash is refused)", not ok and txt.startswith("RULES CHANGED: v3_vs_v2_rules.json sha256 %s is not the pinned %s." % (sha, "2" * 64)), txt)
    check("rules_status: refusal says what to do", "Nothing is judged until a new pin and an amendment entry (date, reason, before or after v3 data) say why." in txt, txt)
finally:
    V.RULE_PINS = saved

# ---------------------------------------------------------------- the week's edges (local time)
loc = lambda y, mo, d, h=0, mi=0, s=0, us=0: dt.datetime(y, mo, d, h, mi, s, us).timestamp()  # noqa: E731
check("week_end: the day at the rule's hour, local", V.week_end("2026-10-26", R) == loc(2026, 10, 26, R["week"]["end_local_hour"]))
R9 = copy.deepcopy(R)
R9["week"]["end_local_hour"] = 9
check("week_end: follows the rule's hour", V.week_end("2026-10-26", R9) == loc(2026, 10, 26, 9))
hr = R["week"]["end_local_hour"]
check("last_week_end: exactly at the week's end counts as that week", V.last_week_end(loc(2026, 10, 26, hr), R) == "2026-10-26")
check("last_week_end: a second before the end is the previous week", V.last_week_end(loc(2026, 10, 26, hr - 1, 59, 59), R) == "2026-10-19")
check("last_week_end: past the end by a second/microsecond", V.last_week_end(loc(2026, 10, 26, hr, 0, 1), R) == "2026-10-26" and V.last_week_end(loc(2026, 10, 26, hr, 0, 0, 1), R) == "2026-10-26")
check("last_week_end: mid-week and Sunday night", V.last_week_end(loc(2026, 10, 29, 12), R) == "2026-10-26" and V.last_week_end(loc(2026, 11, 1, 23), R) == "2026-10-26")
check("last_week_end: Monday before the hour is still last week", V.last_week_end(loc(2026, 11, 2, 3), R) == "2026-10-26")
check("last_week_end: honours the rule's hour", V.last_week_end(loc(2026, 10, 26, 8), R9) == "2026-10-19" and V.last_week_end(loc(2026, 10, 26, 9), R9) == "2026-10-26")
R3 = copy.deepcopy(R)
R3["week"]["end_weekday"] = 2
check("last_week_end: honours the rule's weekday (Wednesday)", V.last_week_end(loc(2026, 10, 28, 12), R3) == "2026-10-28" and V.last_week_end(loc(2026, 10, 27, 12), R3) == "2026-10-21")

# ---------------------------------------------------------------- M / U
p = V.M(1.5)
check("M defaults: MEASURED, empty why, no num/den", p == {"v": 1.5, "mark": "MEASURED", "why": ""}, p)
p = V.M(0.5, mark="ESTIMATE", why="w", num=1, den=2)
check("M carries mark, why, num and den when den is given", p == {"v": 0.5, "mark": "ESTIMATE", "why": "w", "num": 1, "den": 2}, p)
check("M: den 0 still carries num/den (0 is a denominator, None is not)", V.M(0.0, num=0, den=0).get("den") == 0)
check("U is UNMEASURED with its reason", V.U("because") == {"v": None, "mark": "UNMEASURED", "why": "because"})

# ---------------------------------------------------------------- measure_windows / measure_weeks (stubs, no real data)
proj = os.path.join(TMP, "projects")
os.makedirs(proj)
repo = os.path.join(TMP, "repo")
env = dict(os.environ, GIT_AUTHOR_NAME="t", GIT_AUTHOR_EMAIL="t@t", GIT_COMMITTER_NAME="t", GIT_COMMITTER_EMAIL="t@t")
subprocess.run(["git", "init", "-q", repo], check=True, capture_output=True)
T0 = 1_800_000_000
os.makedirs(os.path.join(repo, "infrastructure"))
open(os.path.join(repo, "infrastructure", "x"), "w").write("1")
e = dict(env, GIT_AUTHOR_DATE="@%d +0000" % (T0 + 100), GIT_COMMITTER_DATE="@%d +0000" % (T0 + 100))
subprocess.run(["git", "-C", repo, "add", "infrastructure/x"], check=True, env=e, capture_output=True)
subprocess.run(["git", "-C", repo, "commit", "-q", "-m", "c"], check=True, env=e, capture_output=True)
win = (T0, T0 + 7 * 86400)
ev = []
out = V.measure_windows([win], R, events=ev, projects=proj, repo=repo)[0]
check("measure_windows: process_share comes from git in the window (1 of 1 process commit)", out["process_share"]["v"] == 1.0 and out["process_share"]["den"] == 1, out["process_share"])
check("measure_windows: no transcripts -> ite_per_done UNMEASURED with its reason", out["ite_per_done"]["v"] is None
      and out["ite_per_done"]["why"] == "token use or done unmeasured, or no item done", out["ite_per_done"])
real_tw, real_lw = V.transcript_weeks, V.ledger_week
try:
    V.transcript_weeks = lambda wins, rules, projects=None: [{"ite_wk": V.M(600.0)} for _ in wins]
    V.ledger_week = lambda events, lo, hi: {"done_wk": V.M(3.0), "seen_events": events}
    out = V.measure_windows([win], R, events=["E"], projects=proj, repo=repo)[0]
    check("measure_windows: ite_per_done = ite_wk / done_wk with num and den", out["ite_per_done"]["v"] == 200.0 and out["ite_per_done"]["num"] == 600.0 and out["ite_per_done"]["den"] == 3.0, out["ite_per_done"])
    check("measure_windows: events passed in are used (not re-read)", out["seen_events"] == ["E"])
    V.ledger_week = lambda events, lo, hi: {"done_wk": V.M(0.0)}
    out = V.measure_windows([win], R, events=[], projects=proj, repo=repo)[0]
    check("measure_windows: zero done -> ite_per_done UNMEASURED, never a division", out["ite_per_done"]["v"] is None)
    V.ledger_week = lambda events, lo, hi: {"done_wk": V.U("blind")}
    out = V.measure_windows([win], R, events=[], projects=proj, repo=repo)[0]
    check("measure_windows: ite_wk with done unmeasured -> UNMEASURED", out["ite_per_done"]["v"] is None)
    V.ledger_week = lambda events, lo, hi: {"done_wk": V.M(3.0)}
    V.transcript_weeks = lambda wins, rules, projects=None: [{"ite_wk": V.U("blind")} for _ in wins]
    out = V.measure_windows([win], R, events=[], projects=proj, repo=repo)[0]
    check("measure_windows: done without ite_wk -> UNMEASURED (and (ite or done) is not enough)", out["ite_per_done"]["v"] is None)
    V.transcript_weeks = lambda wins, rules, projects=None: [{"ite_wk": V.M(600.0)} for _ in wins]
    seen = []
    V.ledger_week = lambda events, lo, hi: (seen.append((lo, hi)), {"done_wk": V.M(3.0)})[1]
    ws = V.measure_weeks(["2026-10-26", "2026-11-02"], R, events=[], projects=proj, repo=repo)
    e1, e2 = V.week_end("2026-10-26", R), V.week_end("2026-11-02", R)
    check("measure_weeks: each Monday's window is the 7 days ending then, keyed by day", list(ws) == ["2026-10-26", "2026-11-02"]
          and seen == [(e1 - 7 * 86400, e1), (e2 - 7 * 86400, e2)], seen)
finally:
    V.transcript_weeks, V.ledger_week = real_tw, real_lw

# ---------------------------------------------------------------- settled: failure flags and the report line
bad = V.settled(T0, T0 + 7 * 86400, R, os.path.join(TMP, "no-such-repo"))
check("settled: a failing git log is (False, False) with its reason", bad[0] is False and bad[1] is False and bad[2].startswith("git log failed: ") and "fatal" in bad[2], bad)
R2 = copy.deepcopy(R)
R2["settled"]["config_paths"] = ["cfg/s.json"]
none = V.settled(T0 + 20 * 86400, T0 + 27 * 86400, R2, repo)
check("settled: no config commit at all is (False, False) with its reason", none == (False, False, "no commit to the v3 config before the week's end"), none)
os.makedirs(os.path.join(repo, "cfg"))


def commit(t, body):
    open(os.path.join(repo, "cfg", "s.json"), "w").write(body)
    e = dict(env, GIT_AUTHOR_DATE="@%d +0000" % t, GIT_COMMITTER_DATE="@%d +0000" % t)
    subprocess.run(["git", "-C", repo, "add", "cfg/s.json"], check=True, env=e, capture_output=True)
    subprocess.run(["git", "-C", repo, "commit", "-q", "-m", "c"], check=True, env=e, capture_output=True)


commit(T0, "not json at all")
st = V.settled(T0 + 20 * 86400, T0 + 27 * 86400, R2, repo)
check("settled: an unreadable schedule means no role is enabled (not live, not settled)", st[:2] == (False, False) and st[2].endswith("roles enabled then: none"), st)
R2n = copy.deepcopy(R2)
R2n["settled"]["need_role_enabled"] = False
check("settled: need_role_enabled False -> live without a role", V.settled(T0 + 20 * 86400, T0 + 27 * 86400, R2n, repo)[:2] == (True, True))
commit(T0 + 3600, json.dumps({"roles": [{"name": "Ops", "enabled": True}, {"name": "Off", "enabled": False}, {"name": "Aud", "enabled": True}]}))
st = V.settled(T0 + 20 * 86400, T0 + 27 * 86400, R2, repo)
sha1 = subprocess.run(["git", "-C", repo, "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()
lt = subprocess.run(["git", "-C", repo, "log", "-1", "--format=%ct"], capture_output=True, text=True).stdout.strip()
import time  # noqa: E402
want_why = "last v3 config commit %s at %s (%.1f d before the window); roles enabled then: Ops, Aud" % (
    sha1[:10], time.strftime("%Y-%m-%d %H:%M", time.localtime(int(lt))), (T0 + 20 * 86400 - int(lt)) / 86400)
check("settled: the report line names the 10-char sha, the commit time, the quiet days and the enabled roles", st == (True, True, want_why), (st, want_why))
q = V.settled(T0 + 3600 + 14 * 86400, T0 + 30 * 86400, R2, repo)
check("settled: exactly quiet_days since the commit is settled (edge inclusive)", q[:2] == (True, True), q)
q = V.settled(T0 + 3600 + 14 * 86400 - 1, T0 + 30 * 86400, R2, repo)
check("settled: a second short of quiet_days is not", q[:2] == (False, True), q)

# the roles are read from the FIRST config path (the dispatcher schedule), at the last commit to any of the paths
open(os.path.join(repo, "cfg", "other.json"), "w").write("{}")
e = dict(env, GIT_AUTHOR_DATE="@%d +0000" % (T0 + 40 * 86400), GIT_COMMITTER_DATE="@%d +0000" % (T0 + 40 * 86400))
subprocess.run(["git", "-C", repo, "add", "cfg/other.json"], check=True, env=e, capture_output=True)
subprocess.run(["git", "-C", repo, "commit", "-q", "-m", "o"], check=True, env=e, capture_output=True)
R2b = copy.deepcopy(R2)
R2b["settled"]["config_paths"] = ["cfg/s.json", "cfg/other.json"]
st = V.settled(T0 + 60 * 86400, T0 + 67 * 86400, R2b, repo)
check("settled: roles come from the first config path at the newest commit to any path", st[:2] == (True, True) and st[2].endswith("Ops, Aud"), st)

REACHED.append(1)
check("reached the end of the file", REACHED == [1])
print("FAILS: %d" % len(FAILS) if FAILS else "all ok")
sys.exit(1 if FAILS else 0)
