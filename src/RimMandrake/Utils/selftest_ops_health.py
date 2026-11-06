#!/usr/bin/env python3
"""ops_health (PIPELINE_BUDGET_ENFORCE_HEAL_THYSELF) with planted series: the budget spends at allowed_bad_h and not an
hour before, a silent watcher spends nothing, UNMEASURED is neither bad nor good, the classifier keeps content out,
a died-once fix leads, a stale or foreign verdict reads as none, the shipped rules block is usable and wired to an alarm,
and an SLI cannot go blind when its point changes meaning (OPS_ERROR_BUDGET_DIAGNOSE_CIRG). No network; the ledger is a fake world."""
import json
import os
import sys
import tempfile
import types
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import ops_health as H  # noqa: E402

FAILS = []
H_ = H.HOUR


def ok(what, cond, got=None):
    print(("PASS " if cond else "FAIL ") + what + ("" if cond else "  %r" % (got,)))
    if not cond:
        FAILS.append(what)


def M(v):
    return {"v": v, "m": "MEASURED", "unit": "reds"}


SLI = {"name": "reds", "key": "testing.nightly_news", "unit": "reds", "op": ">", "x": 25}
RULES = {"health": {"slis": [SLI], "window_h": 48, "allowed_bad_h": 24, "max_gap_h": 1.0, "max_age_min": 45,
                    "system_words": ["relentless", "ops", "selftest"], "system_prefixes": ["OPS_"],
                    "content_words": ["redraw"], "content_kinds": ["mod", "art"]}}
NOW = 1_800_000_000.0


def series(hours_bad, hours_ok=0, step_h=0.25, v_bad=84, v_ok=3):
    """records every step_h: hours_ok of good readings, then hours_bad of bad ones ending now."""
    recs, t = [], NOW - (hours_bad + hours_ok) * H_
    while t < NOW - 1e-6:
        bad = t >= NOW - hours_bad * H_
        recs.append({"t": t, "points": {"testing.nightly_news": M(v_bad if bad else v_ok)}})
        t += step_h * H_
    return {"testing": recs}


# --- the budget
c = H.conf(RULES)
b = H.budget({"testing.nightly_news": M(84)}, series(23.5, 20), c, NOW)["reds"]
ok("budget: 23.5 h bad of 24 allowed is not spent", not b["spent"] and 23.4 < b["bad_h"] < 23.6, b)
b = H.budget({"testing.nightly_news": M(84)}, series(24.25, 20), c, NOW)["reds"]
ok("budget: 24.25 h bad spends it", b["spent"] and b["now"] == "bad", b)
b = H.budget({"testing.nightly_news": M(3)}, series(30, 0, v_bad=3), c, NOW)["reds"]
ok("budget: a good reading is 0 h bad", not b["spent"] and b["bad_h"] == 0 and b["now"] == "ok", b)
b = H.budget({"testing.nightly_news": M(84)}, series(60), c, NOW)["reds"]
ok("budget: only the 48 h window counts", abs(b["bad_h"] - 48) < 0.01, b)
# a watcher that measured twice, 30 h apart: each sample holds max_gap_h, never the gap
gap = {"testing": [{"t": NOW - 30 * H_, "points": {"testing.nightly_news": M(84)}}]}
b = H.budget({"testing.nightly_news": M(84)}, gap, c, NOW)["reds"]
ok("budget: silence between passes spends nothing (1 h per lone sample)", abs(b["bad_h"] - 1.0) < 0.01 and not b["spent"], b)
unm = series(30)
for r in unm["testing"]:
    r["points"]["testing.nightly_news"] = {"v": None, "m": "UNMEASURED", "why": "blind"}
b = H.budget({"testing.nightly_news": {"v": None, "m": "UNMEASURED", "why": "blind"}}, unm, c, NOW)["reds"]
ok("budget: UNMEASURED is neither bad nor measured, and says why",
   b["bad_h"] == 0 and b["measured_h"] == 0 and b["now"] == "UNMEASURED" and b.get("why") == "blind", b)
ok("budget: a bool or NaN value is no reading", H.bad_of({"m": "MEASURED", "v": True}, SLI) is None
   and H.bad_of({"m": "MEASURED", "v": float("nan")}, SLI) is None)
ok("rules: a bad SLI or window is refused by name",
   len(H.sli_problems(H.conf({"health": {"slis": [{"name": "x", "key": "k", "op": "~", "x": 1}], "window_h": 0}}))) == 2)


# --- the classifier
def item(i, kind="task", open_=True, raised=None, created="2026-11-01", repeats=0, title=""):
    return types.SimpleNamespace(id=i, kind=kind, open=open_, raised=raised, created_at=created, live_repeats=repeats, title=title)


root = Path(tempfile.mkdtemp(prefix="ops_health_"))
(root / "src" / "RimMandrake" / "FlowWorks" / "About").mkdir(parents=True)
(root / "src" / "RimMandrake" / "FlowWorks" / "About" / "About.xml").write_text("<ModMetaData/>")
world = types.SimpleNamespace(items={x.id: x for x in [
    item("RELENTLESS_LEASE_FIX_THING", created="2026-11-02"),
    item("OPS_DISK_DRAIN_ABCD", created="2026-11-03"),
    item("RELENTLESS_OLD_FIX_RAISED", created="2026-11-03", raised="x"),
    item("RELENTLESS_DIED_FIX_ONCE", created="2026-11-03", repeats=1),
    item("FLOWWORKS_SELFTEST_FIX_PIPE"),                 # names a game mod: content
    item("CREATURE_FIX_TAIL", title="relentless ops selftest"),   # system words in the title only: content
    item("RELENTLESS_ART_REDRAW_TWO"),                   # a content word vetoes
    item("SELFTEST_MOD_KIND", kind="mod"),               # a content kind
    item("RELENTLESS_CLOSED_FIX", open_=False),
]})
ids = H.system_ids(world, RULES, root)
ok("classifier: system items in order (died-once, alarm, raised, oldest), content kept out",
   ids == ["RELENTLESS_DIED_FIX_ONCE", "OPS_DISK_DRAIN_ABCD", "RELENTLESS_OLD_FIX_RAISED", "RELENTLESS_LEASE_FIX_THING"], ids)

# --- publish and read
d = Path(tempfile.mkdtemp(prefix="ops_health_v_"))
p = d / "health.json"
v = H.publish({"testing.nightly_news": M(84)}, series(30), world, RULES, root, NOW, path=p)
ok("verdict: a spent SLI reads degraded, content paused, names it",
   v["state"] == "degraded" and v["content_paused"] and v["spent"] == ["reds"] and "reds" in v["why"], v)
ok("verdict: a spent SLI with no scope is published as scope all (a global pause, DEGRADED_PAUSE_FIX_STOPS_ONLY_WHAT_BROKE)",
   v["spent_scope"] == {"reds": "all"}, v.get("spent_scope"))
ok("verdict: the died-once fix is listed as owing a guard test",
   [x["id"] for x in v["recurring"]] == ["RELENTLESS_DIED_FIX_ONCE"] and "guard test" in v["recurring"][0]["owes"], v["recurring"])
got, why = H.read_verdict(NOW + 60, p)
ok("read: a fresh verdict comes back whole", got and got["system_items"] == ids and why.startswith("fresh"), why)
got, why = H.read_verdict(NOW + 46 * 60, p)
ok("read: older than max_age_min is stale, none", got is None and "stale" in why, why)
got, why = H.read_verdict(NOW, d / "absent.json")
ok("read: a missing file is none, said", got is None and "no health verdict" in why, why)
(d / "foreign.json").write_text(json.dumps({"schema": "x", "t": NOW, "state": "healthy", "system_items": []}))
ok("read: a foreign schema is none", H.read_verdict(NOW, d / "foreign.json")[0] is None)
(d / "torn.json").write_text("{\"schema\": ")
ok("read: a torn file is none, said", H.read_verdict(NOW, d / "torn.json")[1].startswith("health verdict unreadable"))
v = H.publish({"testing.nightly_news": M(3)}, series(0, 30, v_ok=3), None, RULES, root, NOW, path=p)
ok("verdict: healthy with no ledger says system_items unknown (None, so the reader falls back)",
   v["state"] == "healthy" and v["system_items"] is None and "unknown" in v["why"], v)
got = H.read_verdict(NOW, p)[0]
ok("read: such a verdict still comes back (its state stands; the reader asks the classifier for the items)",
   got is not None and got["system_items"] is None and got["state"] == "healthy", got)

# --- the shipped rules: usable, and the spent budget files a repair item
shipped = json.loads((HERE / "ops_watch_rules.json").read_text(encoding="utf-8"))
sc = H.conf(shipped)
ok("shipped: the health block passes its own check", not H.sli_problems(sc) and len(sc["slis"]) >= 4, H.sli_problems(sc))
ok("shipped: every design SLI is present or said UNMEASURED",
   {"infra_share", "nightly_reds", "tmp_headroom"} <= {s["name"] for s in sc["slis"]} and "infra_tokens_day" in sc["unmeasured_slis"])
tg = [t for t in shipped["targets"] if t.get("key") == "health.spent_slis"]
ok("shipped: a spent budget is an alarm with one fixed item name",
   len(tg) == 1 and tg[0].get("alarm") is True and tg[0].get("name") == "OPS_ERROR_BUDGET_DIAGNOSE", tg)

# --- an SLI cannot go blind under a redefined point (OPS_ERROR_BUDGET_DIAGNOSE_CIRG): 1ff82747f3 narrowed
# testing.nightly_news to the list's own faults, 3 minutes after the SLI was written on it; 84 reds then read 0, "ok"
OLD_UNIT, NEW_UNIT = "nightly reds not on the known-red list, and entries past their age", "nightly reds no known-red entry parks"
NARROW = "known-red list entries past their age, and bad entries"
PT = lambda v, u: {"v": v, "m": "MEASURED", "unit": u}  # noqa: E731
blind = {"name": "reds", "key": "testing.nightly_news", "unit": OLD_UNIT, "op": ">", "x": 25}
cb = dict(H.conf(RULES), slis=[blind])
b = H.budget({"testing.nightly_news": PT(0, NARROW)}, {}, cb, NOW)["reds"]
ok("drift: the very SLI that went blind now reads UNMEASURED, not ok", b["now"] == "UNMEASURED" and b.get("drifted") and NARROW in b["why"], b)
hist = {"testing": [{"t": NOW - h * H_, "points": {"testing.nightly_news": PT(0, NARROW)}} for h in range(30)]}
b = H.budget({"testing.nightly_news": PT(84, NARROW)}, hist, cb, NOW)["reds"]
ok("drift: another unit neither spends nor earns", b["bad_h"] == 0 and b["measured_h"] == 0 and not b["spent"], b)
ok("drift: an SLI with no unit is refused", any("unit" in p for p in H.sli_problems(dict(cb, slis=[{"name": "n", "key": "k", "op": ">", "x": 1}]))))
ok("drift: a bad was is refused", H.sli_problems(dict(cb, slis=[dict(blind, was=[{"key": "k"}])])))
dv = H.verdict({"testing.nightly_news": PT(0, NARROW)}, {}, None, dict(RULES, health=dict(RULES["health"], slis=[blind])), root, NOW)
ok("drift: the verdict names it", dv["drifted"] == ["reds"] and "reds" in dv["why"], dv)
moved = dict(next(s for s in sc["slis"] if s["name"] == "nightly_reds"), name="moved")
cm = dict(sc, slis=[moved])
past = [{"t": NOW - h * H_, "points": {"testing.nightly_news": PT(84, OLD_UNIT)}} for h in range(26, 2, -1)]
past += [{"t": NOW - h * H_, "points": {"testing.nightly_news": PT(0, NARROW), "testing.nightly_unparked_reds": PT(84, NEW_UNIT)}} for h in (2, 1)]
b = H.budget({"testing.nightly_news": PT(0, NARROW), "testing.nightly_unparked_reds": PT(84, NEW_UNIT)}, {"testing": past}, cm, NOW)["moved"]
ok("was: the old key's bad hours still count, the new key carries on", b["now"] == "bad" and b["spent"] and 25 < b["bad_h"] < 27, b)
b = H.budget({"testing.nightly_unparked_reds": PT(3, NEW_UNIT)}, {"testing": [{"t": NOW - h * H_, "points": {"testing.nightly_news": PT(84, NARROW)}} for h in range(30)]}, cm, NOW)["moved"]
ok("was: the old key in a third unit counts for nothing", b["bad_h"] == 0 and not b["spent"], b)

b = H.budget({"testing.nightly_news": M(84)}, {"testing": [{"t": NOW, "points": {"testing.nightly_news": M(84)}}]}, c, NOW)["reds"]
ok("tie: a series record stamped this very pass does not crash the verdict", b["now"] == "bad", b)

# the class: every shipped SLI's key and unit are ones ops_watch can emit (a literal, %s a wildcard); rename either and this fails
import ast  # noqa: E402
import re  # noqa: E402
src_lits = [n.value for n in ast.walk(ast.parse((HERE / "ops_watch.py").read_text(encoding="utf-8")))
            if isinstance(n, ast.Constant) and isinstance(n.value, str)]
pats = [re.compile(re.escape(x).replace(re.escape("%s"), ".+")) for x in src_lits if len(x) < 120]
for s_ in sc["slis"]:
    ok("emitted: %s key %s" % (s_["name"], s_["key"]), any(p.fullmatch(s_["key"]) for p in pats))
    ok("emitted: %s unit %r" % (s_["name"], s_["unit"]), any(p.fullmatch(s_["unit"]) for p in pats))
tg = [t for t in shipped["targets"] if t.get("key") == "health.drifted_slis"]
ok("shipped: a drifted SLI is an alarm with one fixed item name",
   len(tg) == 1 and tg[0].get("alarm") is True and tg[0].get("name") == "OPS_SLI_DRIFT_DIAGNOSE", tg)

# --- ops_watch writes the verdict on a full pass and never on a limited one
os.environ["RM_OPS_WATCH_DIR"] = str(d / "ow")
# rimflow/model.py (pulled in by ops_health.subject_words) puts the REAL clone's Utils first on sys.path; in the mutant copy
# that imported the unmutated ops_watch and every ops_watch mutant stayed green. HERE first again, then import.
sys.path.insert(0, str(HERE))
import ops_watch as OW  # noqa: E402
ok("ops_watch is the one beside this test (a mutant copy proves its own copy)", Path(OW.__file__).resolve().parent == HERE, OW.__file__)
ok("ops_health is the one beside this test too", Path(H.__file__).resolve().parent == HERE, H.__file__)
REAL_COLLECTORS = dict(OW.COLLECTORS)   # the shipped family table, before the stubs below
for k in list(OW.COLLECTORS):
    OW.COLLECTORS[k] = (lambda now, rules, ctx: {})
OW.COLLECTORS["testing"] = lambda now, rules, ctx: {"testing.nightly_news": M(84)}
rules = dict(shipped, alarm={}, targets=[], ranges={})
OW.run(now=NOW, rules=rules, filer=None, families=["testing"])
# the real collector on the night that went blind: list faults 0, unparked 84 -> the shipped SLI reads bad
import known_reds as KR  # noqa: E402
real_measure = KR.measure
KR.measure = lambda *a, **k: {"night": "n", "news": ["red, not listed: t%d" % i for i in range(84)], "reds": ["t%d" % i for i in range(84)],
                              "listed": [], "unlisted": ["t%d" % i for i in range(84)], "expired": [], "cured": [],
                              "cop": {"groups": [], "overdue": [], "overdue_said": "", "detail_read": False}}
night = OW.nightly_news(NOW, {"open_ids": set()})
KR.measure = real_measure
ok("collector: list faults read 0 while 84 reds stand", night["testing.nightly_news"]["v"] == 0 and night["testing.nightly_unparked_reds"]["v"] == 84, night)
b = H.budget(night, {}, sc, NOW)["nightly_reds"]
ok("collector: the shipped nightly_reds SLI sees the 84", b["now"] == "bad" and b["v"] == 84, b)

# --- every shipped SLI against the REAL collector of its family, by equality on key and unit, fed from fixtures. The
# literal scan above cannot pin a unit: ops_watch holds the literal '%s%s', which matches anything.
fx = Path(tempfile.mkdtemp(prefix="ops_health_fx_"))
for var in ("RM_OPS_DISKS", "RM_POOL_MAX_BYTES", "RM_POOL_MAX_CLONES"):   # the shipped mounts and caps, whatever this shell set
    os.environ.pop(var, None)
(fx / "pool").mkdir()
os.environ.update(RM_POOL_ROOT=str(fx / "pool"), RM_OBJSTORE_STATE=str(fx / "state"), RM_SCRATCH_ROOT=str(fx / "scratch"),
                  RM_SESSION_GLOB=str(fx / "none" / "*"), RM_POOL_STATE_GLOB=str(fx / "none" / "*"),
                  RM_SCRATCH_REAP_RUNS=str(fx / "reap" / "runs.jsonl"), RM_TESTING_METRICS_DIR=str(fx / "metrics"),
                  RELENTLESS_ROOT=str(fx / "belt"))
(fx / "belt" / "live").mkdir(parents=True)
(fx / "belt" / "store").mkdir()
# the churn SLIs (OPS_CHURN_MEASURE_RETURNS_ARE_NOT_PROGRESS) read items/ and spend-*.json: one item returned 3 times
_it = fx / "belt" / "store" / "items" / "FX_ITEM"
_it.mkdir(parents=True)
(_it / "state.json").write_text(json.dumps({"returns": 3, "gen": 2, "spent": 100}))
_mk = "rm-relentless-work-%s-g1" % __import__("hashlib").sha1(b"FX_ITEM").hexdigest()[:10]
(_it / "attempts.jsonl").write_text(json.dumps({"gen": 1, "at": OW.iso(NOW - 3600), "start": _mk}) + "\n"
                                    + json.dumps({"gen": 1, "at": OW.iso(NOW - 3000), "end": "harness"}) + "\n")
(fx / "belt" / "store" / ("spend-%s.json" % time.strftime("%Y%m%d", time.gmtime(NOW)))).write_text(json.dumps({"runs": {_mk: 100}}))
(fx / "belt" / "live" / "runs.jsonl").write_text("".join(
    json.dumps({"at": OW.iso(NOW - 60 * i), "outcome": "PASS" if i % 2 else "INFRA", "why": "fixture"}) + "\n" for i in range(20)))
KR.measure = lambda *a, **k: {"night": "n", "news": [], "reds": ["t%d" % i for i in range(84)], "listed": [],
                              "unlisted": ["t%d" % i for i in range(84)], "expired": [], "cured": [],
                              "cop": {"groups": [], "overdue": [], "overdue_said": "", "detail_read": False}}
emitted = {}
for fam, c_ in (("testing", {"steve_jobs": [], "steve_jobs_bad": [], "open_ids": set()}), ("disk", {}), ("relentless", {})):
    emitted.update(REAL_COLLECTORS[fam](NOW, shipped, c_))
KR.measure = real_measure
ok("real collectors: the five shipped SLIs are the ones walked here",
   {s_["name"] for s_ in sc["slis"]} >= {"infra_share", "nightly_reds", "tmp_headroom", "root_headroom", "pool_headroom"})
for s_ in sc["slis"]:
    pt = emitted.get(s_["key"]) or {}
    ok("real collector: %s key %s reads MEASURED" % (s_["name"], s_["key"]), pt.get("m") == "MEASURED", pt)
    ok("real collector: %s unit is exactly %r" % (s_["name"], s_["unit"]), pt.get("unit") == s_["unit"], pt)
    b = H.budget(emitted, {}, sc, NOW)[s_["name"]]
    ok("real collector: %s judged, not drifted" % s_["name"], b["now"] in ("ok", "bad") and not b.get("drifted"), b)
ok("real collector: nightly_reds still reads the 84, live_measured_pct its 50%",
   emitted["testing.nightly_unparked_reds"]["v"] == 84 and emitted["relentless.live_measured_pct"]["v"] == 50.0, emitted["relentless.live_measured_pct"])

# --- the was unit is what the old collector really wrote: the real series around the redefinition, and that commit's parent
was_ = next(s_ for s_ in sc["slis"] if s_["name"] == "nightly_reds")["was"][0]
REAL = [json.loads(x) for x in (HERE / "testdata" / "ops_health_nightly_series.jsonl").read_text(encoding="utf-8").splitlines()]
REAL_T = REAL[-1]["t"]      # the 2026-11-03 22:37Z pass whose health.json read nightly_reds bad_h=28.25 v=84, now=bad, spent
old_units = {r["points"]["testing.nightly_news"].get("unit") for r in REAL if r["points"].get("testing.nightly_news", {}).get("m") == "MEASURED"}
ok("was: its unit is the one the real series holds before the redefinition, its successor differs",
   old_units == {was_["unit"], NARROW} and was_["key"] == "testing.nightly_news" and was_["unit"] != emitted["testing.nightly_news"]["unit"], old_units)
import subprocess  # noqa: E402
git = subprocess.run(["git", "-C", str(HERE.parents[2]), "show", "1ff82747f3^:src/RimMandrake/Utils/ops_watch.py"], capture_output=True, text=True, errors="replace")
if git.returncode:      # a wall with no object store: said, and not a pass; the series row above still pins it
    print("UNMEASURED was: the parent of 1ff82747f3 is unreadable here: %s" % git.stderr.strip()[:120])
else:
    ok("was: its unit is what c_testing wrote at the parent of the redefinition", 'M(len(v["news"]), "%s"' % was_["unit"] in git.stdout)
# the same parent, readable with no object store: the committed blob of ops_watch.py at 1ff82747f3^, gzipped. Its git blob
# hash is pinned here; where git can read the object, the pin must equal what git holds there, so the copy is that commit's.
import gzip  # noqa: E402
import hashlib  # noqa: E402
PARENT_BLOB = "f61eb588b1f9d273cc3130913b085ea4d7170e75"
pb = gzip.decompress((HERE / "testdata" / "ops_watch_at_1ff82747f3_parent.py.gz").read_bytes())
ok("was: the committed parent copy is byte-for-byte the pinned blob", hashlib.sha1(b"blob %d\0" % len(pb) + pb).hexdigest() == PARENT_BLOB)
ok("was: its unit is what c_testing wrote in that committed parent copy", 'M(len(v["news"]), "%s"' % was_["unit"] in pb.decode("utf-8"))
gp = subprocess.run(["git", "-C", str(HERE.parents[2]), "rev-parse", "1ff82747f3^:src/RimMandrake/Utils/ops_watch.py"], capture_output=True, text=True, errors="replace")
if gp.returncode:
    print("UNMEASURED was: git cannot confirm the pinned blob here (the copy's own hash still holds): %s" % gp.stderr.strip()[:120])
else:
    ok("was: the pinned blob is what git holds at 1ff82747f3^", gp.stdout.strip() == PARENT_BLOB, gp.stdout.strip())

# --- replay of that real series: history before the redefinition still counts, and the new point carries on
newest = REAL[-1]["points"]
b = H.budget(newest, {"testing": REAL[:-1]}, sc, REAL_T)["nightly_reds"]
ok("replay: the real series under the shipped rules matches the live verdict (bad, v=84, 28.25 h, spent)",
   b["now"] == "bad" and b["v"] == 84 and b["bad_h"] == 28.25 and b["spent"], b)
pre = [r for r in REAL[:-1] if "testing.nightly_unparked_reds" not in r["points"]]
b = H.budget(newest, {"testing": pre}, sc, REAL_T)["nightly_reds"]
ok("replay: the hours before the redefinition alone spend it", b["spent"] and b["bad_h"] > 24, b)
b = H.budget(newest, {"testing": REAL[:-1]}, dict(sc, slis=[dict(blind, name="prefix")]), REAL_T)["prefix"]
ok("replay: the SLI as it stood before this fix cannot read ok on 0", b["now"] == "UNMEASURED" and b.get("drifted"), b)

# --- publish_health itself, with SLIs drifted: the point counts them and names them, and health.json agrees
ow_rules = dict(shipped)
drift_pts = dict(emitted)
drift_pts["testing.nightly_unparked_reds"] = PT(84, "a unit nobody wrote")
hp = OW.publish_health(drift_pts, {}, {}, ow_rules, NOW)["health.drifted_slis"]
ok("publish_health: one drifted SLI reads MEASURED 1 and names it",
   hp["m"] == "MEASURED" and hp["v"] == 1 and hp["x"]["said"] == "nightly_reds", hp)
hj = json.loads((d / "ow" / "health.json").read_text())
ok("publish_health: health.json says drifted, UNMEASURED, 0 h",
   hj["drifted"] == ["nightly_reds"] and hj["budget"]["nightly_reds"]["now"] == "UNMEASURED" and hj["budget"]["nightly_reds"]["bad_h"] == 0, hj["budget"]["nightly_reds"])
drift_pts["relentless.live_measured_pct"] = PT(50.0, "share")
hp = OW.publish_health(drift_pts, {}, {}, ow_rules, NOW)["health.drifted_slis"]
ok("publish_health: two drifted SLIs read 2, each named", hp["v"] == 2 and hp["x"]["said"] == "infra_share, nightly_reds", hp)
hp = OW.publish_health(emitted, {}, {}, ow_rules, NOW)["health.drifted_slis"]
ok("publish_health: none drifted reads MEASURED 0, nothing named", hp["m"] == "MEASURED" and hp["v"] == 0 and not hp["x"]["said"], hp)
real_publish = H.publish


def _no_verdict(*a, **k):
    raise OSError("disk full")


H.publish = _no_verdict
hf = OW.publish_health(emitted, {}, {}, ow_rules, NOW)
H.publish = real_publish
ok("publish_health: a failed verdict reads all five UNMEASURED, said",
   sorted(hf) == ["health.drifted_slis", "health.incident_slis", "health.spent_slis", "health.state", "health.unmeasured"]
   and all(p["m"] == "UNMEASURED" and "health verdict not written" in p["why"] and "disk full" in p["why"] for p in hf.values()), hf)
# and the point reaches the alarm with its one fixed name
drift_tg = [t for t in shipped["targets"] if t.get("key") == "health.drifted_slis"]
filed = []
hp = OW.publish_health(drift_pts, {}, {}, ow_rules, NOW)
st_ = OW.run_alarms(hp, dict(shipped, targets=drift_tg, ranges={}), NOW, set(), lambda todo, conf: filed.extend(todo) or {})
ok("alarm: drifted SLIs file the one fixed item", [a["name"][:len("OPS_SLI_DRIFT_DIAGNOSE")] for a in filed] == ["OPS_SLI_DRIFT_DIAGNOSE"], (filed, st_))
filed.clear()
(d / "ow" / "alarms.json").unlink(missing_ok=True)
st_ = OW.run_alarms(OW.publish_health(emitted, {}, {}, ow_rules, NOW), dict(shipped, targets=drift_tg, ranges={}), NOW + 900, set(), lambda todo, conf: filed.extend(todo) or {})
ok("alarm: none drifted files nothing", not filed, filed)
(d / "ow" / "health.json").unlink()
(d / "ow" / "alarms.json").unlink(missing_ok=True)

ok("ops_watch: a limited pass writes no verdict", not (d / "ow" / "health.json").exists())
OW.run(now=NOW, rules=rules, filer=None)
got, why = H.read_verdict(NOW + 1, d / "ow" / "health.json")
st = json.loads((d / "ow" / "status.json").read_text())
ok("ops_watch: a full pass publishes health.json and its points",
   (d / "ow" / "health.json").exists() and st["points"]["health.spent_slis"]["m"] == "MEASURED"
   and st["points"]["health.drifted_slis"]["m"] == "MEASURED"
   and st["points"]["health.state"]["v"] in ("healthy", "degraded"), st["points"].get("health.state"))

# --- the production path: a full OW.run() whose collectors emit a drifted SLI reaches the alarm through run() itself, with
# a recording filer; run_alarms is not called by hand here (blind check at 5b5ea883: a filter between publish_health and
# run_alarms inside run() stayed green while only the hand-wired call above was pinned)
def _fam_of(pts, fam):
    return {k: v for k, v in pts.items() if k.split(".")[0] == fam}


def full_run(pts, t):
    for k in list(OW.COLLECTORS):
        OW.COLLECTORS[k] = (lambda now, rules, ctx, _k=k: _fam_of(pts, _k))
    (d / "ow" / "alarms.json").unlink(missing_ok=True)
    got = []
    OW.run(now=t, rules=dict(shipped, targets=drift_tg, ranges={}), filer=lambda todo, conf: got.extend(todo) or {})
    return got, json.loads((d / "ow" / "status.json").read_text())


drift_one = dict(emitted)
drift_one["testing.nightly_unparked_reds"] = PT(84, "a unit nobody wrote")
got_f, st = full_run(drift_one, NOW + 1800)
ok("run(): a drifted SLI in the collectors' points reads health.drifted_slis MEASURED 1 in status.json",
   st["points"]["health.drifted_slis"]["m"] == "MEASURED" and st["points"]["health.drifted_slis"]["v"] == 1
   and st["points"]["health.drifted_slis"]["x"]["said"] == "nightly_reds", st["points"].get("health.drifted_slis"))
ok("run(): health.json from that pass names the drift and reads the SLI UNMEASURED",
   json.loads((d / "ow" / "health.json").read_text()).get("drifted") == ["nightly_reds"])
ok("run(): the pass itself files the one fixed drift item through its filer",
   [a["name"][:len("OPS_SLI_DRIFT_DIAGNOSE")] for a in got_f] == ["OPS_SLI_DRIFT_DIAGNOSE"], got_f)
got_f, st = full_run(dict(emitted), NOW + 3600)
ok("run(): the same pass with the right unit reads 0 drifted and files nothing",
   st["points"]["health.drifted_slis"]["v"] == 0 and not got_f, (st["points"].get("health.drifted_slis"), got_f))

# the hand order: named beats words both ways, a family takes its new members, a closed name holds no place
hand = {"health": dict(RULES["health"], system_rank=["GARDEN_FIX_NOW", "NIGHT_RED_*", "OPS_B"], not_system=["SELFTEST_OF_A_MOD"])}
hw = types.SimpleNamespace(items={x.id: x for x in [item("OPS_A", repeats=3), item("OPS_B"), item("NIGHT_RED_Z"), item("NIGHT_RED_A"),
                                                    item("GARDEN_FIX_NOW", kind="mod"), item("SELFTEST_OF_A_MOD"), item("TULIP_RESKIN"),
                                                    item("NIGHT_RED_SHUT", open_=False)]})
got = H.system_ids(hw, hand, root)
ok("rank: the hand order leads, even over a repeat and a content kind", got[:2] == ["GARDEN_FIX_NOW", "NIGHT_RED_A"] and got[3] == "OPS_B", got)
ok("rank: a family holds its new members, a closed one is gone", "NIGHT_RED_Z" in got[:3] and "NIGHT_RED_SHUT" not in got, got)
ok("rank: the unranked follow by the classifier", got[4:] == ["OPS_A"], got)
ok("rank: not_system beats the word that matched", "SELFTEST_OF_A_MOD" not in got and "TULIP_RESKIN" not in got, got)

# an exact not_system id beats a family glob; an exact system_rank id still beats not_system
glob = {"health": dict(RULES["health"], system_rank=["SELFTEST_*", "BOTH_NAMED"], not_system=["SELFTEST_SOURCE_POLISH", "BOTH_NAMED"])}
gw = types.SimpleNamespace(items={x.id: x for x in [item("SELFTEST_SOURCE_POLISH"), item("SELFTEST_RED_NEW"), item("BOTH_NAMED")]})
got = H.system_ids(gw, glob, root)
ok("rank: an exact not_system id beats a family glob", "SELFTEST_SOURCE_POLISH" not in got and "SELFTEST_RED_NEW" in got, got)
ok("rank: an exact system_rank id still beats not_system", "BOTH_NAMED" in got, got)

# ISSYSTEM_WORDS_FIX_PIPELINE_READ_AS_CONTENT: the shipped word lists must read real pipeline ids as system and game content as not
_sc = H.conf(shipped)
_sm = H.mod_names(root)
_it = lambda i: types.SimpleNamespace(id=i, kind="task", open=True)
for _i in ["CLOSE_GATE_ENFORCE_DONE_IS_EARNED", "BENCHSHARD_DIAGNOSE_SAME_EVENTS_NEW_ORDER", "BREAKER_SELFTEST_FIX_ONE_RED_IN_THIRTEEN",
           "STAGING_REWIRE_PYTHON_NOT_AN_LLM", "ACCOUNT_SWITCH_FIX_HAND_STEP_BEFORE_MONDAY", "RA_S06_GUARD_ENFORCE_SEEN_RED_TWICE",
           "ART_CHECKS_FIX_OUTLINE_SEVEN_FLAGGED", "TELEMETRY_TAILER_FIX_RAW_CURSOR_EARLY", "WRAPUP_DEBTS_FIX_RELAUNCH_ALREADY_PAID"]:
    ok("is_system: pipeline id %s reads as system" % _i, H.is_system(_it(_i), _sc, _sm))
for _i in ["ARTEVAL_INSTALL_DEPLOY_HELD_BIOMES", "SMALL_PUMP_HOSE_FIX_LAYS_UNCONNECTED", "SUSPENSION_BRIDGE_BUILD_POSTS_AT_BOTH_ENDS", "WORLD_MOUNTAINS_REDRAW_PEAKS_NOT_FIELDS",
           "ARIDSHRUBLAND_TITAN_POPULATE_FORTY_NO_GIANT"]:
    ok("is_system: content id %s stays content" % _i, not H.is_system(_it(_i), _sc, _sm))

print("selftest_ops_health: " + ("PASS" if not FAILS else "RED: %d failed: %s" % (len(FAILS), ", ".join(FAILS))))
sys.exit(1 if FAILS else 0)
