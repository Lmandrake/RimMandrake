#!/usr/bin/env python3
"""Selftest for v3_vs_v2.py (V3_VERSUS_V2_MEASURE_PROVE_IT_PAYS).

Holds: the pre-registered rule cannot change silently (its hash is the last pin, every later pin is an amendment
entry, a changed byte is refused); the token arithmetic equals spend_census.scan_file on the same transcript; the
verdict rule as written (SUPERIOR / WORSE / NOT_SHOWN / UNMEASURED, a guard past its kill line, the counterfactual
lowering but never raising); standing is PROVISIONAL under four settled weeks; "settled" reads git history; the
Auditor's page has no token-blind word; an instrument that cannot see says UNMEASURED, never zero.
Synthetic data in a temp dir; reads no real ledger or transcript."""
import copy
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import v3_vs_v2 as V  # noqa: E402
import blind_view  # noqa: E402  (on the path through v3_vs_v2)

FAILS = []


def check(name, ok, detail=""):
    print(("ok    " if ok else "FAIL  ") + name + ("" if ok else "  -- " + str(detail)))
    if not ok:
        FAILS.append(name)


R = V.load_rules()
TMP = tempfile.mkdtemp(prefix="selftest_v3v2_")

# ---------------------------------------------------------------- 1. the rule cannot change silently
check("rule hash is the last pin", V.rules_sha() == V.RULE_PINS[-1][0], (V.rules_sha(), V.RULE_PINS[-1][0]))
check("every pin after the first is an amendment entry", len(R["amendments"]) == len(V.RULE_PINS) - 1,
      (len(R["amendments"]), len(V.RULE_PINS)))
check("pinned rule passes", V.rules_status()[0])
alt = os.path.join(TMP, "rules.json")
raw = open(V.RULES_PATH, "rb").read()
open(alt, "wb").write(raw.replace(b'"superior_min_better": 2', b'"superior_min_better": 1'))
ok, txt = V.rules_status(alt)
check("a changed threshold is refused", not ok and "RULES CHANGED" in txt, txt)
open(alt, "wb").write(raw + b"\n")
check("even a trailing newline is refused", not V.rules_status(alt)[0])
keys = [m["key"] for m in R["metrics"]]
check("metric keys unique", len(keys) == len(set(keys)))
check("every metric has a kind, group, direction, scale, floor",
      all(m.get("kind") in ("count", "ratio", "stock", "none") and m.get("group") in ("primary", "guard", "cost", "report")
          and m.get("better") in ("higher", "lower", "none") and m.get("scale") in ("log", "abs") and m.get("floor", 0) > 0
          for m in R["metrics"]))
check("ite_wk is a cost metric (the verdict needs it measured)", any(m["key"] == "ite_wk" and m["group"] == "cost" for m in R["metrics"]))

# ---------------------------------------------------------------- 2. token arithmetic = spend_census
proj = os.path.join(TMP, "projects")
bench = os.path.join(proj, "-home-mandrake-rm-bench")
os.makedirs(os.path.join(bench, "sess", "subagents"))
os.makedirs(os.path.join(proj, "-home-mandrake-elsewhere"))
T0 = 1_800_000_000  # a window [T0, T0 + 7 d)


def iso(t):
    import datetime as dt
    return dt.datetime.fromtimestamp(t, dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.000Z")


def call(mid, t, model="claude-opus-x", it=10, cr=200000, c5=300, c1=None, out=50, side=False):
    cc = {"ephemeral_5m_input_tokens": c5}
    if c1 is not None:
        cc["ephemeral_1h_input_tokens"] = c1
    return json.dumps({"type": "assistant", "isSidechain": side, "timestamp": iso(t),
                       "message": {"id": mid, "model": model, "usage": {"input_tokens": it, "cache_read_input_tokens": cr,
                                                                         "cache_creation": cc, "output_tokens": out}}})


def human(t, text):
    return json.dumps({"type": "user", "origin": {"kind": "human"}, "timestamp": iso(t), "message": {"content": text}})


seat = os.path.join(bench, "sess.jsonl")
helper = os.path.join(bench, "sess", "subagents", "agent-1.jsonl")
other = os.path.join(proj, "-home-mandrake-elsewhere", "x.jsonl")
open(seat, "w").write("\n".join([
    call("m1", T0 - 3 * 86400),                        # before the window: makes the window measurable, not counted
    call("m2", T0 + 3600, c1=1000),
    call("m2", T0 + 3601, c1=1000),                    # same message id: counted once
    call("m3", T0 + 7200, model="claude-sonnet-x", cr=5000, side=True),   # sidechain in a seat file: skipped
    call("m4", T0 + 9000, model="claude-haiku-x", cr=5000),
    human(T0 + 4000, "no, I already ruled on this"),
    human(T0 + 4100, "go ahead"),
    human(T0 + 30 * 3600, "thanks"),
]) + "\n")
open(helper, "w").write("\n".join([call("h1", T0 + 5000, side=True), call("h2", T0 + 5100, cr=1000, side=True)]) + "\n")
open(other, "w").write(call("o1", T0 + 6000) + "\n")
for p in (seat, helper, other):
    os.utime(p, (T0 + 8 * 86400, T0 + 8 * 86400))   # the scan skips files last written before the window
win = (T0, T0 + 7 * 86400)
tw = V.transcript_weeks([win], R, proj)[0]
want = {"all": 0.0, "fam": 0.0, "sub": 0.0, "big": 0.0}
seen = set()
for p, fam in ((seat, True), (helper, True), (other, False)):
    calls = V.S.scan_file(p, win[0], seen)[0]
    for c in calls:
        if not (win[0] <= c["t"] < win[1]):
            continue
        want["all"] += c["ite"]
        if fam:
            want["fam"] += c["ite"]
            if "/subagents/" in p:
                want["sub"] += c["ite"]
                want["big"] += c["ite"] if c["ctx"] > R["ctx_big"] else 0
close = lambda a, b: a is not None and abs(a - b) <= 1e-6 * max(1.0, abs(b))  # noqa: E731
check("ite_wk equals spend_census.scan_file", close(tw["ite_wk"]["v"], want["fam"]), (tw["ite_wk"], want))
check("all_ite_wk counts other families too", close(tw["all_ite_wk"]["v"], want["all"]) and want["all"] > want["fam"])
check("sub_ite_big_ctx_share as scan_file", close(tw["sub_ite_big_ctx_share"]["v"], want["big"] / want["sub"]))
check("helpers_wk counts helper transcripts", tw["helpers_wk"]["v"] == 1, tw["helpers_wk"])
check("owner messages, hours, already-ruled", (tw["owner_msgs_wk"]["v"], tw["owner_active_h_wk"]["v"], tw["already_ruled_wk"]["v"]) == (3, 2, 1),
      (tw["owner_msgs_wk"], tw["owner_active_h_wk"], tw["already_ruled_wk"]))
check("owner proxies are marked ESTIMATE", tw["owner_msgs_wk"]["mark"] == "ESTIMATE")

# ---------------------------------------------------------------- 3. UNMEASURED, never zero
early = V.transcript_weeks([(T0 - 30 * 86400, T0 - 23 * 86400)], R, proj)[0]
check("a window before the transcripts start is UNMEASURED", all(p["v"] is None and p["mark"] == "UNMEASURED" for p in early.values()), early)
quiet = V.transcript_weeks([(T0 + 2 * 86400, T0 + 3 * 86400)], R, proj)[0]
check("a window with no call is UNMEASURED, not zero spend", quiet["ite_wk"]["v"] is None and quiet["owner_msgs_wk"]["v"] is None, quiet)
lw = V.ledger_week([], T0, T0 + 7 * 86400)
check("no ledger: every ledger metric UNMEASURED", all(p["v"] is None for p in lw.values()))
check("classify(None) is UNMEASURED", V.classify(R["metrics"][0], None, {})[0] == "UNMEASURED")

# ---------------------------------------------------------------- 4. the verdict rule as written
MET = {m["key"]: m for m in R["metrics"]}
REFV = {"done_wk": 800, "owner_wait_over_3d": 20, "already_ruled_wk": 4, "rework_share": 0.13, "close_no_level_share": 0.9,
        "verify_backlog": 500, "process_share": 0.6, "sub_ite_big_ctx_share": 0.3, "doing_live_lease_share": 0.5,
        "lapsed_open": 100, "contested_new_wk": 1, "ite_wk": 1.5e9, "ite_per_done": 2e6, "helpers_wk": 1000,
        "owner_msgs_wk": 400, "owner_active_h_wk": 80, "filed_wk": 1000, "net_wk": 200, "owner_resolve_med_d": 2.0,
        "vfail_share": 0.1, "seat_ite_share": 0.1, "all_ite_wk": 1.6e9}
REF = {k: {"value": v, "x": V._x(v, MET[k]["scale"]), "band": MET[k]["floor"], "context": []} for k, v in REFV.items()}
pt = lambda v: {"v": v, "mark": "MEASURED"}  # noqa: E731


def week(**over):
    w = {k: pt(v) for k, v in REFV.items()}
    for k, v in over.items():
        w[k] = pt(v) if v is not None else V.U("blind")
    return w


def verdict(w, cf=None):
    return V.judge_week(w, REF, R, cf)


j = verdict(week())
check("identical week: NOT_SHOWN, cost SAME, ratio 1", (j["verdict"], j["cost"], j["ite_ratio_to_v2"]) == ("NOT_SHOWN", "SAME", 1.0), j["verdict"])
j = verdict(week(done_wk=2000, rework_share=0.05))
check("two primaries BETTER, none WORSE: SUPERIOR", j["verdict"] == "SUPERIOR", j)
j = verdict(week(done_wk=2000))
check("one primary BETTER: NOT_SHOWN", j["verdict"] == "NOT_SHOWN")
j = verdict(week(done_wk=200))
check("one primary WORSE, none BETTER: WORSE", j["verdict"] == "WORSE")
j = verdict(week(done_wk=2000, rework_share=0.05, verify_backlog=2000))
check("two BETTER and one WORSE: NOT_SHOWN", j["verdict"] == "NOT_SHOWN", j)
j = verdict(week(done_wk=200, verify_backlog=2000, rework_share=0.05))
check("two WORSE: WORSE even with one BETTER", j["verdict"] == "WORSE")
j = verdict(week(done_wk=2000, rework_share=0.05, sub_ite_big_ctx_share=0.6))
check("a guard past kill_above stops SUPERIOR", j["verdict"] == "NOT_SHOWN" and j["guard_worse"] == ["sub_ite_big_ctx_share"], j)
j = verdict(week(done_wk=2000, rework_share=0.05, owner_wait_over_3d=None, already_ruled_wk=None, close_no_level_share=None,
                 verify_backlog=None))
check("three primaries measured: UNMEASURED", j["verdict"] == "UNMEASURED", j["primary_measured"])
j = verdict(week(done_wk=2000, rework_share=0.05, ite_wk=None))
check("ite_wk unmeasured: UNMEASURED (no verdict without its cost)", j["verdict"] == "UNMEASURED")
j = verdict(week(done_wk=2000, rework_share=0.05, ite_wk=3e9))
check("cost HIGHER is stated beside SUPERIOR", (j["verdict"], j["cost"], j["ite_ratio_to_v2"]) == ("SUPERIOR", "HIGHER", 2.0), j["cost"])
w = week(done_wk=2000, rework_share=0.05)
j = verdict(w, {"status": "MEASURED", "range": {"done_wk": [500, 2500], "rework_share": [0.04, 0.2]}})
check("counterfactual: BETTER inside the v2 range is taken back", j["verdict"] == "NOT_SHOWN" and j["per"]["done_wk"].get("class_cf") == "SAME", j["per"]["done_wk"])
j = verdict(w, {"status": "MEASURED", "range": {"done_wk": [500, 1500], "rework_share": [0.08, 0.2]}})
check("counterfactual: BETTER past the range stands", j["verdict"] == "SUPERIOR" and j["counterfactual_used"])
j = verdict(week(done_wk=820), {"status": "MEASURED", "range": {"done_wk": [100, 200]}})
check("counterfactual never raises a SAME", j["per"]["done_wk"]["class"] == "SAME" and j["verdict"] == "NOT_SHOWN")
j = verdict(w, {"status": "UNMEASURED", "why": "backtest failed"})
check("an UNMEASURED counterfactual changes nothing", j["verdict"] == "SUPERIOR" and not j["counterfactual_used"])

# ---------------------------------------------------------------- 5. the band comes from the tag week's own days
m = dict(MET["done_wk"])
days = [{"done_wk": pt(v)} for v in (100, 100, 100, 100, 100, 100, 100)]
check("seven identical days: no noise, the floor binds", V.statistics.pstdev(V._boot(m, days, R)) == 0.0)
days = [{"done_wk": pt(v)} for v in (5, 63, 22, 107, 98, 80, 398)]
b1, b2 = V._boot(m, days, R), V._boot(m, days, R)
check("bootstrap is seeded (same band twice)", b1 == b2 and len(b1) == R["band"]["resamples"])
check("lumpy days give a band past the floor", V.statistics.pstdev(b1) * R["band"]["z"] * 2 ** 0.5 > m["floor"])
check("fewer than 5 measured days: no band", V._boot(m, days[:4] + [{}, {}, {}], R) is None)
rd = [{"rework_share": {"v": n / d, "num": n, "den": d}} for n, d in ((1, 10), (2, 10), (1, 20), (3, 10), (0, 10), (2, 20), (1, 10))]
rb = V._boot(MET["rework_share"], rd, R)
check("ratio band resamples numerators and denominators", rb and min(rb) >= 0 and max(rb) <= 0.3)
v2 = {"weeks": {R["v2_history"]["reference_week"]: {"done_wk": pt(773)}}, "days": days}
ref = V.reference(v2, R)
check("reference value is the tag week, band >= floor", ref["done_wk"]["value"] == 773 and ref["done_wk"]["band"] >= m["floor"])
check("a metric unmeasured in the tag week has no baseline", ref["rework_share"]["x"] is None
      and V.classify(MET["rework_share"], pt(0.1), ref)[0] == "NO_BASELINE")

# ---------------------------------------------------------------- 6. standing
h = lambda e, v: {"end": e, "settled": True, "verdict": v, "ite_ratio_to_v2": 1.2}  # noqa: E731
s = V.standing([h("a", "SUPERIOR"), h("b", "SUPERIOR"), h("c", "SUPERIOR")], R)
check("three settled weeks: PROVISIONAL", s["standing"] == "PROVISIONAL" and s["rule_reading"] == "SUPERIOR")
s = V.standing([h("a", "SUPERIOR"), h("b", "NOT_SHOWN"), h("c", "SUPERIOR"), h("d", "SUPERIOR")], R)
check("3 of 4 SUPERIOR, none WORSE: SUPERIOR", s["standing"] == "SUPERIOR" and s["cost_ratio_median"] == 1.2)
s = V.standing([h("a", "SUPERIOR"), h("b", "WORSE"), h("c", "SUPERIOR"), h("d", "SUPERIOR")], R)
check("one WORSE blocks SUPERIOR", s["standing"] == "NOT_SHOWN")
hist = [h("a", "SUPERIOR"), h("b", "SUPERIOR"), h("c", "SUPERIOR"), dict(h("d", "SUPERIOR"), settled=False)]
check("an unsettled week does not count", V.standing(hist, R)["standing"] == "PROVISIONAL")

# ---------------------------------------------------------------- 7. settled reads git history
repo = os.path.join(TMP, "repo")
os.makedirs(os.path.join(repo, "cfg"))
env = dict(os.environ, GIT_AUTHOR_NAME="t", GIT_AUTHOR_EMAIL="t@t", GIT_COMMITTER_NAME="t", GIT_COMMITTER_EMAIL="t@t")


def commit(t, enabled):
    open(os.path.join(repo, "cfg", "s.json"), "w").write(json.dumps({"roles": [{"name": "Operations", "enabled": enabled}], "rev": t}))
    e = dict(env, GIT_AUTHOR_DATE="@%d +0000" % t, GIT_COMMITTER_DATE="@%d +0000" % t)
    subprocess.run(["git", "-C", repo, "add", "cfg/s.json"], check=True, env=e, capture_output=True)
    subprocess.run(["git", "-C", repo, "commit", "-q", "-m", "c"], check=True, env=e, capture_output=True)


subprocess.run(["git", "init", "-q", repo], check=True, capture_output=True)
R2 = copy.deepcopy(R)
R2["settled"]["config_paths"] = ["cfg/s.json"]
D = 86400
commit(T0, False)
st = V.settled(T0 + 20 * D, T0 + 27 * D, R2, repo)
check("no role enabled: not live, not settled", st[:2] == (False, False), st)
commit(T0 + D, True)
st = V.settled(T0 + 10 * D, T0 + 17 * D, R2, repo)
check("enabled 9 days before the window: live, not settled", st[:2] == (False, True), st)
st = V.settled(T0 + 15 * D, T0 + 22 * D, R2, repo)
check("enabled 14+ days before the window: settled", st[:2] == (True, True), st)
commit(T0 + 30 * D, True)
st = V.settled(T0 + 15 * D, T0 + 22 * D, R2, repo)
check("a later config commit does not reach back", st[0], st)
st = V.settled(T0 + 35 * D, T0 + 42 * D, R2, repo)
check("a config change restarts the quiet clock", not st[0], st)

# ---------------------------------------------------------------- 8. the Auditor's page is token-blind
w = week(done_wk=2000, rework_share=0.05)
for k in ("ite_wk", "helpers_wk", "all_ite_wk"):
    w[k]["why"] = "tokens 1.5e9 for the account"
w["owner_msgs_wk"] = V.U("no human-origin message")
w["owner_resolve_med_d"] = V.U("no owner wait resolved in the week")
rec = {"end": "2026-11-30", "settled": False, "settled_why": "x", "rules": "rule sha256 x", "week": w,
       "judge": V.judge_week(w, REF, R, {"status": "MEASURED", "range": {"done_wk": [1, 2], "ite_wk": [1, 2], "helpers_wk": [1, 2]}}),
       "counterfactual": {"status": "MEASURED", "range": {"done_wk": [1, 2], "ite_wk": [1, 2], "helpers_wk": [1, 2]}},
       "standing": V.standing([], R)}
blind = V.render(rec, REF, R, blind=True)
ops = V.render(rec, REF, R)
words = lambda t: set(re.findall(r"[A-Za-z_][A-Za-z0-9_]*", t))  # noqa: E731
hits = sorted(x for x in words(blind) if blind_view.sensitive_word(x))
check("quality_blind.md has no token-blind word", not hits, hits)
check("the blind check can see (Operations' page trips it)", any(blind_view.sensitive_word(x) for x in words(ops)))
check("the blind page has no cost metric row", not any(("| %s |" % k) in blind for k in ("ite_wk", "ite_per_done", "helpers_wk", "all_ite_wk", "seat_ite_share", "sub_ite_big_ctx_share")))
check("blind_view.redact leaves the page unchanged", blind_view.redact(blind) == blind,
      [l for l, r in zip(blind.splitlines(), blind_view.redact(blind).splitlines()) if l != r][:3])
check("UNMEASURED is listed with its reason, never as 0", "owner messages: no human-origin message" in blind)
check("Operations' page says PROVISIONAL when not settled", "PROVISIONAL (not settled)" in ops)

shutil.rmtree(TMP, ignore_errors=True)
print("FAILS: %d" % len(FAILS) if FAILS else "all ok")
sys.exit(1 if FAILS else 0)
