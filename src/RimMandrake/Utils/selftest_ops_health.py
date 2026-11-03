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
import ops_watch as OW  # noqa: E402
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

ok("ops_watch: a limited pass writes no verdict", not (d / "ow" / "health.json").exists())
OW.run(now=NOW, rules=rules, filer=None)
got, why = H.read_verdict(NOW + 1, d / "ow" / "health.json")
st = json.loads((d / "ow" / "status.json").read_text())
ok("ops_watch: a full pass publishes health.json and its points",
   (d / "ow" / "health.json").exists() and st["points"]["health.spent_slis"]["m"] == "MEASURED"
   and st["points"]["health.drifted_slis"]["m"] == "MEASURED"
   and st["points"]["health.state"]["v"] in ("healthy", "degraded"), st["points"].get("health.state"))

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

print("selftest_ops_health: " + ("PASS" if not FAILS else "RED: %d failed: %s" % (len(FAILS), ", ".join(FAILS))))
sys.exit(1 if FAILS else 0)
