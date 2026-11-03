#!/usr/bin/env python3
"""ops_health (PIPELINE_BUDGET_ENFORCE_HEAL_THYSELF) with planted series: the budget spends at allowed_bad_h and not an
hour before, a silent watcher spends nothing, UNMEASURED is neither bad nor good, the classifier keeps content out,
a died-once fix leads, a stale or foreign verdict reads as none, and the shipped rules block is usable and wired to an
alarm. No network; the ledger is a fake world."""
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
    return {"v": v, "m": "MEASURED"}


SLI = {"name": "reds", "key": "testing.nightly_news", "op": ">", "x": 25}
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

# --- ops_watch writes the verdict on a full pass and never on a limited one
os.environ["RM_OPS_WATCH_DIR"] = str(d / "ow")
import ops_watch as OW  # noqa: E402
for k in list(OW.COLLECTORS):
    OW.COLLECTORS[k] = (lambda now, rules, ctx: {})
OW.COLLECTORS["testing"] = lambda now, rules, ctx: {"testing.nightly_news": M(84)}
rules = dict(shipped, alarm={}, targets=[], ranges={})
OW.run(now=NOW, rules=rules, filer=None, families=["testing"])
ok("ops_watch: a limited pass writes no verdict", not (d / "ow" / "health.json").exists())
OW.run(now=NOW, rules=rules, filer=None)
got, why = H.read_verdict(NOW + 1, d / "ow" / "health.json")
st = json.loads((d / "ow" / "status.json").read_text())
ok("ops_watch: a full pass publishes health.json and its points",
   (d / "ow" / "health.json").exists() and st["points"]["health.spent_slis"]["m"] == "MEASURED"
   and st["points"]["health.state"]["v"] in ("healthy", "degraded"), st["points"].get("health.state"))

print("selftest_ops_health: " + ("PASS" if not FAILS else "RED: %d failed: %s" % (len(FAILS), ", ".join(FAILS))))
sys.exit(1 if FAILS else 0)
