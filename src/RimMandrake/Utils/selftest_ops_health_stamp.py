#!/usr/bin/env python3
"""ops_health: unusable health rules read UNMEASURED, never healthy, and every verdict names its inputs
(OPS_HEALTH_FIX_BROKEN_RULES_READ_HEALTHY, relentless_recovery_plan_2026-11-05 step 2, finding B1: verdict() set b={}
when the rules were unusable, so spent=[] gave state "healthy" and content_paused False — a broken instrument read green).

Three cases from the plan: unusable rules, missing ledger, pinned-input replay byte-identical; plus the ops_watch point
and its alarm, so the repair item is filed and Relentless can put it first. No network; the ledger is a fake world."""
import json
import os
import sys
import tempfile
import types
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
D = Path(tempfile.mkdtemp(prefix="ops_health_stamp_"))
os.environ["RM_OPS_WATCH_DIR"] = str(D / "ow")
import ops_health as H  # noqa: E402

FAILS = []
NOW = 1_800_000_000.0


def ok(what, cond, got=None):
    print(("PASS " if cond else "FAIL ") + what + ("" if cond else "  %r" % (got,)))
    if not cond:
        FAILS.append(what)


def M(v):
    return {"v": v, "m": "MEASURED", "unit": "reds"}


def item(i, kind="task", open_=True):
    return types.SimpleNamespace(id=i, kind=kind, open=open_, raised=None, created_at="2026-11-01", live_repeats=0, title="")


SLI = {"name": "reds", "key": "testing.nightly_news", "unit": "reds", "op": ">", "x": 25}
GOOD = {"health": {"slis": [SLI], "window_h": 48, "allowed_bad_h": 24, "max_gap_h": 1.0, "max_age_min": 45,
                   "system_words": ["relentless"], "system_prefixes": ["OPS_"]}}
BROKEN = {"health": dict(GOOD["health"], slis=[dict(SLI, op="~")], window_h=0)}     # two problems, named
ROOT = D / "root"
(ROOT / "src").mkdir(parents=True)
WORLD = types.SimpleNamespace(items={x.id: x for x in [
    item("RELENTLESS_LEASE_FIX_THING"), item(H.REPAIR_ALARM + "_FRESH_PAINT"), item("OPS_DISK_DRAIN_ABCD")]})
PTS = {"testing.nightly_news": M(84)}
HIST = {"testing": [{"t": NOW - 30 * 3600 + n * 900, "points": {"testing.nightly_news": M(84)}} for n in range(120)]}
STAMP = {"collector_sha": "a" * 40, "ledger": {"events": 3, "last_ts": "2026-11-05T04:52:00Z", "last_tsn": 7}}

# --- 1. unusable rules: UNMEASURED, never healthy, never degraded, the repair named
v = H.verdict(PTS, HIST, WORLD, BROKEN, str(ROOT), NOW, STAMP)
ok("unusable rules: state unmeasured (was healthy: b={} -> spent=[])", v["state"] == "unmeasured", v["state"])
ok("unusable rules: no budget read, content not paused, nothing spent", v["budget"] == {} and v["spent"] == []
   and v["content_paused"] is False, v)
ok("unusable rules: the why says UNMEASURED and names both problems", v["why"].startswith("UNMEASURED")
   and "op" in v["why"] and "window_h" in v["why"], v["why"])
ok("unusable rules: the repair is the open health-rules alarm item", v["repair"] == [H.REPAIR_ALARM + "_FRESH_PAINT"], v["repair"])
p = D / "u.json"
H.publish(PTS, HIST, WORLD, BROKEN, str(ROOT), NOW, path=p, stamp=STAMP)
got, why = H.read_verdict(NOW + 60, p)
ok("unusable rules: the published verdict reads back fresh as unmeasured (not dropped as malformed)",
   got is not None and got["state"] == "unmeasured" and "unmeasured" in why, why)
v = H.verdict(PTS, HIST, WORLD, GOOD, str(ROOT), NOW, STAMP)
ok("usable rules, same input: degraded, the budget read, no repair", v["state"] == "degraded" and v["spent"] == ["reds"]
   and v["repair"] == [], (v["state"], v["spent"], v["repair"]))
v = H.verdict({"testing.nightly_news": M(3)}, {}, WORLD, GOOD, str(ROOT), NOW, STAMP)
ok("usable rules, good input: healthy", v["state"] == "healthy" and v["repair"] == [], v["state"])

# --- 2. missing ledger: state from the budget, the items unknown, the stamp says no ledger
v = H.verdict(PTS, HIST, None, GOOD, str(ROOT), NOW, {"collector_sha": "a" * 40})
ok("missing ledger: system_items None, ledger stamp None, said", v["system_items"] is None and v["inputs"]["ledger"] is None
   and "no ledger" in v["why"] and v["state"] == "degraded", v)
v = H.verdict(PTS, HIST, None, BROKEN, str(ROOT), NOW, {"collector_sha": "a" * 40})
ok("missing ledger + unusable rules: unmeasured, no repair known, both said", v["state"] == "unmeasured" and v["repair"] == []
   and "no ledger" in v["why"] and v["why"].startswith("UNMEASURED"), v)
ok("ledger_mark: none for no ledger, the watermark for events", H.ledger_mark(None) is None and H.ledger_mark(
    [{"ts": "2026-11-05T04:00:00Z", "tsn": 5}, {"ts": "2026-11-05T04:52:00Z", "tsn": 9}, {"ts": "2026-11-05T01:00:00Z", "tsn": True}])
   == {"events": 3, "last_ts": "2026-11-05T04:52:00Z", "last_tsn": 9})

# --- 3. pinned-input replay: byte-identical; each input moves its own stamp
a, b = D / "a.json", D / "b.json"
H.publish(PTS, HIST, WORLD, GOOD, str(ROOT), NOW, path=a, stamp=STAMP)
H.publish(PTS, HIST, WORLD, json.loads(json.dumps(GOOD)), str(ROOT), NOW, path=b, stamp=dict(STAMP))
ok("replay: the same pinned inputs give a byte-identical health.json", a.read_bytes() == b.read_bytes())
va = json.loads(a.read_text())
ok("replay: the verdict names its inputs", va["inputs"] == {"rules_sha256": H.rules_sha256(GOOD), "collector_sha": "a" * 40,
                                                         "ledger": STAMP["ledger"]}, va.get("inputs"))
ok("replay: rules differing by one list entry differ in rules_sha256 (the 04:52Z not_system mismatch is visible)",
   H.rules_sha256(GOOD) != H.rules_sha256({"health": dict(GOOD["health"], not_system=["X"])}))
ok("replay: key order does not move rules_sha256", H.rules_sha256({"a": 1, "b": 2}) == H.rules_sha256({"b": 2, "a": 1}))
sha = H.collector_sha()
ok("collector_sha: this clone's git HEAD, 40 hex (or None if git cannot say)", sha is None or len(sha) == 40, sha)
v = H.verdict(PTS, HIST, WORLD, GOOD, str(ROOT), NOW)
ok("no stamp: collector measured here, ledger None", v["inputs"]["collector_sha"] == sha and v["inputs"]["ledger"] is None, v["inputs"])

# --- 4. ops_watch: the point, and the alarm that files the repair item
sys.path.insert(0, str(HERE))
import ops_watch as OW  # noqa: E402
ok("ops_watch is the one beside this test", Path(OW.__file__).resolve().parent == HERE, OW.__file__)
shipped = json.loads((HERE / "ops_watch_rules.json").read_text(encoding="utf-8"))
ok("shipped health rules are usable (this alarm should never fire on them)", H.sli_problems(H.conf(shipped)) == [],
   H.sli_problems(H.conf(shipped)))
tg = [t for t in shipped["targets"] if t.get("key") == "health.unmeasured"]
ok("shipped: health.unmeasured is an alarm named REPAIR_ALARM", len(tg) == 1 and tg[0].get("alarm") is True
   and tg[0].get("name") == H.REPAIR_ALARM, tg)
bad_rules = dict(shipped, health=dict(shipped["health"], window_h=0))
ev = [{"ts": "2026-11-05T04:52:00Z", "tsn": 11, "event": "note", "id": "X"}]
hp = OW.publish_health(PTS, {}, {"events": None}, bad_rules, NOW)
hj = json.loads((D / "ow" / "health.json").read_text())
ok("publish_health: unusable rules -> health.unmeasured MEASURED 1, health.state unmeasured, said",
   hp["health.unmeasured"]["m"] == "MEASURED" and hp["health.unmeasured"]["v"] == 1 and hp["health.state"]["v"] == "unmeasured"
   and "window_h" in hp["health.unmeasured"]["x"]["said"], hp.get("health.unmeasured"))
ok("publish_health: health.json says unmeasured and carries the stamp", hj["state"] == "unmeasured"
   and set(hj["inputs"]) == {"rules_sha256", "collector_sha", "ledger"} and hj["inputs"]["rules_sha256"] == H.rules_sha256(bad_rules), hj.get("inputs"))
filed = []
OW.run_alarms(hp, dict(shipped, targets=tg, ranges={}), NOW, set(), lambda todo, conf: filed.extend(todo) or {})
ok("alarm: unusable rules file the one repair item", [x["name"][:len(H.REPAIR_ALARM)] for x in filed] == [H.REPAIR_ALARM], filed)
(D / "ow" / "alarms.json").unlink(missing_ok=True)
filed.clear()
hp = OW.publish_health(PTS, {}, {"events": None}, shipped, NOW)
ok("publish_health: usable rules -> health.unmeasured MEASURED 0", hp["health.unmeasured"]["m"] == "MEASURED"
   and hp["health.unmeasured"]["v"] == 0 and hp["health.state"]["v"] in ("healthy", "degraded"), hp.get("health.unmeasured"))
OW.run_alarms(hp, dict(shipped, targets=tg, ranges={}), NOW + 900, set(), lambda todo, conf: filed.extend(todo) or {})
ok("alarm: usable rules file nothing", not filed, filed)
mark = H.ledger_mark(ev)
ok("publish_health stamps the ledger watermark of ctx events", mark == {"events": 1, "last_ts": "2026-11-05T04:52:00Z", "last_tsn": 11})
# through OW.publish_health itself (blind check GAP:DIFF): ctx events must reach health.json inputs.ledger. The replay is
# faked so the case needs no real ledger model; the stamp is what is under test, not the world.
_seen, _pc = [], sys.modules.get("pulse_core")
sys.modules["pulse_core"] = types.SimpleNamespace(_model=lambda: types.SimpleNamespace(replay=lambda e: _seen.append(e)))
try:
    (D / "ow" / "health.json").unlink(missing_ok=True)
    hp = OW.publish_health(PTS, {}, {"events": ev}, shipped, NOW)
    hj = json.loads((D / "ow" / "health.json").read_text())
finally:
    if _pc is None:
        sys.modules.pop("pulse_core", None)
    else:
        sys.modules["pulse_core"] = _pc
ok("publish_health: ctx events replayed and their watermark lands in health.json inputs.ledger",
   _seen == [ev] and hp["health.state"]["m"] == "MEASURED" and hj["inputs"]["ledger"] == mark == H.ledger_mark(ev),
   (hp.get("health.state"), hj.get("inputs")))

print("selftest_ops_health_stamp: " + ("PASS" if not FAILS else "RED: %d failed: %s" % (len(FAILS), ", ".join(FAILS))))
sys.exit(1 if FAILS else 0)
