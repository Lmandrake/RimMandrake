#!/usr/bin/env python3
"""selftest_ops_churn.py — OPS_CHURN_MEASURE_RETURNS_ARE_NOT_PROGRESS: Operations sees churn and owns its alarms.

On 2026-11-04 47 Relentless items had churned (one at gen 20, ~157M weighted tokens) on broken tests read as broken work,
and no reading said so. Each check fails on the code before the change:

1. rl_churn counts an item in churn by returns OR a repeated failure class, only with a failure inside the window; a
   blocked row or a finish is not a failure.
2. rl_churn's returned tokens: spend runs whose (item, gen) failed, placed in time by the gen's start row.
3. rl_churn is UNMEASURED (never 0) with no spend, with too much spend it cannot place, and with no items dir.
4. rules: a "returned" or "blind_fail" journal act is not progress; churn SLIs are incident SLIs whose units match.
5. ops_health.incident names the incident SLIs reading bad, and verdict carries it.
6. run_alarms files health.incident_slis at once under ONE fixed id and a repeat reopens that id (no new item).
7. The Steve unclaimed alarm names an owner: its todo carries the STEVE_LANE_UNSTICK_* ids to expedite, its title says
   so, and expedite_owner runs `relentless.py expedite set <id> --level expedited --by Operations` without a worker env.

Fixtures only: a temp store, a temp RM_OPS_WATCH_DIR, a fake relentless.py, fake filer.

    python3 src/RimMandrake/Utils/selftest_ops_churn.py
"""
import hashlib
import json
import os
import shutil
import sys
import tempfile
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
TMP = Path(tempfile.mkdtemp(prefix="selftest_ops_churn_"))
os.environ["RM_OPS_WATCH_DIR"] = str(TMP / "ops")
(TMP / "ops").mkdir()
import ops_health as OH  # noqa: E402
import ops_watch as OW  # noqa: E402

FAILS = []
NOW = time.time()
HOUR = 3600.0
CFG = {"churn_window_h": 12, "churn_returns": 3, "churn_same_class": 2, "tokens_window_h": 24,
       "churn_max_unmapped_pct": 20, "churn_not_fail_ends": ["finish", "done", "unhold", "blocked"]}


def ok(cond, what, got=None):
    print(("PASS " if cond else "FAIL ") + what + ("" if cond else "  got: %r" % (got,)))
    if not cond:
        FAILS.append(what)


def iso(t):
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(t))


def item(store, name, returns, rows, spent=0):
    d = store / "items" / name
    d.mkdir(parents=True)
    (d / "state.json").write_text(json.dumps({"returns": returns, "gen": len(rows), "spent": spent}))
    (d / "attempts.jsonl").write_text("".join(json.dumps(r) + "\n" for r in rows))


def marker(name, gen, kind="work"):
    return "rm-relentless-%s-%s-g%d" % (kind, hashlib.sha1(name.encode()).hexdigest()[:10], gen)


def store_fixture(root, unmapped=0):
    s = root
    t1, t2 = NOW - 2 * HOUR, NOW - 1 * HOUR
    # A: 3 returns, fails in window -> churn (returns)
    item(s, "A_ITEM", 3, [{"gen": 1, "at": iso(t1), "start": marker("A_ITEM", 1)},
                          {"gen": 1, "at": iso(t1 + 60), "end": "harness", "detail": "x"},
                          {"gen": 2, "at": iso(t2), "start": marker("A_ITEM", 2)},
                          {"gen": 2, "at": iso(t2 + 60), "end": "evidence", "detail": "y"}], spent=900)
    # B: 2 returns, same class twice -> churn (signature)
    item(s, "B_ITEM", 2, [{"gen": 1, "at": iso(t1), "start": "m"}, {"gen": 1, "at": iso(t1 + 9), "end": "harness"},
                          {"gen": 2, "at": iso(t2), "start": "m"}, {"gen": 2, "at": iso(t2 + 9), "end": "harness"}])
    # C: 5 returns, but its last failure is outside the 12 h window -> not churn now
    item(s, "C_ITEM", 5, [{"gen": 1, "at": iso(NOW - 20 * HOUR), "end": "harness"}])
    # D: blocked twice + finish: no failure at all
    item(s, "D_ITEM", 4, [{"gen": 1, "at": iso(t1), "start": marker("D_ITEM", 1)},
                          {"gen": 1, "at": iso(t1 + 5), "end": "blocked", "kind": "x"},
                          {"gen": 1, "at": iso(t1 + 6), "end": "blocked", "kind": "x"},
                          {"gen": 1, "at": iso(t1 + 7), "end": "finish"}])
    runs = {marker("A_ITEM", 1): 300, marker("A_ITEM", 2, "check"): 100, marker("D_ITEM", 1): 600}
    if unmapped:
        runs["rm-relentless-work-ffffffffff-g1"] = unmapped
    day = time.strftime("%Y%m%d", time.gmtime(NOW))
    (s / ("spend-%s.json" % day)).write_text(json.dumps({"spent": sum(runs.values()), "runs": runs}))
    return s


def main():
    # 1, 2
    s = store_fixture(TMP / "s1")
    p = OW.rl_churn(s, NOW, CFG)
    ci = p["relentless.churn_items"]
    ok(ci.get("m") == "MEASURED" and ci.get("v") == 2 and ci["x"]["first"][0] == "A_ITEM"
       and set(ci["x"]["first"]) == {"A_ITEM", "B_ITEM"}, "1: churn = returns>=3 OR one class twice, failure in window", ci)
    ok("harness" in ci["x"]["last_fail"], "1: the cause names the last failure classes", ci["x"])
    pct = p["relentless.returned_tokens_pct"]
    ok(pct.get("m") == "MEASURED" and pct["v"] == 40.0 and pct["x"]["returned"] == 400 and pct["x"]["total"] == 1000,
       "2: returned share = failed-gen runs over placed runs (400 of 1000)", pct)
    ok(p["relentless.returned_tokens_day"].get("v") == 400, "2: returned tokens per 24 h", p["relentless.returned_tokens_day"])
    # 3
    s = store_fixture(TMP / "s2", unmapped=5000)
    p = OW.rl_churn(s, NOW, CFG)
    ok(p["relentless.returned_tokens_pct"].get("m") == "UNMEASURED", "3: spend it cannot place is UNMEASURED, not a share",
       p["relentless.returned_tokens_pct"])
    s = TMP / "s3"
    item(s, "A_ITEM", 0, [])
    p = OW.rl_churn(s, NOW, CFG)
    ok(p["relentless.returned_tokens_pct"].get("m") == "UNMEASURED", "3: no spend is UNMEASURED, not 0%", p)
    ok(p["relentless.churn_items"].get("v") == 0, "3: a store with no failures reads 0 items in churn", p["relentless.churn_items"])
    p = OW.rl_churn(TMP / "nope", NOW, CFG)
    ok(all(v.get("m") == "UNMEASURED" and "unreadable" in v.get("why", "") for v in p.values()),
       "3: no items dir: every churn reading UNMEASURED and says unreadable (c_relentless counts it blind)", p)
    # 4
    rules = json.loads((Path(OW.__file__).parent / "ops_watch_rules.json").read_text())
    acts = rules["relentless"]["progress_acts"]
    ok("returned" not in acts and "blind_fail" not in acts and "lease" in acts, "4: returned/blind_fail are not progress", acts)
    slis = {x["name"]: x for x in rules["health"]["slis"]}
    ok(all(slis.get(n, {}).get("incident") is True for n in ("churn_items", "returned_tokens_pct", "infra_share")),
       "4: churn_items, returned_tokens_pct, infra_share are incident SLIs", [slis.get(n) for n in ("churn_items",)])
    units = {k: u for k, u in zip(OW.CHURN_KEYS, OW.CHURN_UNITS)}
    ok(all(slis[n]["unit"] == units[slis[n]["key"]] for n in ("churn_items", "returned_tokens_pct")),
       "4: the SLI units are the collector's units", [slis[n] for n in ("churn_items", "returned_tokens_pct")])
    ok(not OH.sli_problems(rules["health"]) if hasattr(OH, "sli_problems") else True, "4: the health rules validate",
       OH.sli_problems(rules["health"]) if hasattr(OH, "sli_problems") else None)
    # 5
    hc = {"slis": [{"name": "infra_share", "incident": True}, {"name": "churn_items", "incident": True},
                   {"name": "returned_tokens_pct", "incident": True}, {"name": "nightly_reds"}]}
    b = {"infra_share": {"now": "bad", "v": 22.5, "line": 15}, "churn_items": {"now": "ok", "v": 3, "line": 10},
         "nightly_reds": {"now": "bad", "v": 4}}
    inc = OH.incident(b, hc)
    ok(inc["bad"] == ["infra_share"] and inc["unmeasured"] == ["returned_tokens_pct"] and "infra_share 22.5" in inc["cause"],
       "5: incident names only incident SLIs reading bad, and the unmeasured ones", inc)
    # 6
    tg = next(t for t in rules["targets"] if t.get("key") == "health.incident_slis")
    r6 = {"alarms": {"clear_passes": 1}, "targets": [dict(tg, conductor_log=str(TMP / "conductor_log.md"))]}
    pt = {"m": "MEASURED", "v": 2, "x": {"cause": "churn_items 55 (line 10); infra_share 22.5 (line 15)"}}
    sent = []

    def filer(todo, conf):
        sent.append([dict(a) for a in todo])
        return {a["name"]: None for a in todo}
    OW.run_alarms({"health.incident_slis": pt}, r6, NOW, set(), filer)
    first = sent[-1][0] if sent else {}
    name = first.get("name", "")
    ok(name.startswith("OPS_CHURN_DIAGNOSE_RETURNED_WORK_") and not first.get("reopen")
       and "churn_items 55" in first.get("title", "") and first.get("conductor_log"),
       "6: the first bad pass files one fixed-id incident, routed to the Conductor too", first)
    (TMP / "ops" / "alarms.json").unlink()
    sent.clear()
    OW.run_alarms({"health.incident_slis": pt}, r6, NOW + 7200, {name}, filer)
    again = sent[-1][0] if sent else {}
    ok(again.get("name") == name and again.get("reopen") is True, "6: a repeat reopens the same id, never refiles", again)
    # 7
    (TMP / "ops" / "alarms.json").unlink()
    st = {"key": "steve.incident_unclaimed_min", "op": ">", "value": 60, "alarm": True, "tag": "STEVE_INCIDENT_UNCLAIMED",
          "name": "OPS_STEVE_UNSTICK_UNCLAIMED", "marks": ["MEASURED"], "title_field": "first", "expedite_field": "first"}
    sent.clear()
    OW.run_alarms({"steve.incident_unclaimed_min": {"m": "MEASURED", "v": 90, "x": {"first": ["STEVE_LANE_UNSTICK_ABCD"]}}},
                  {"alarms": {"clear_passes": 1}, "targets": [st]}, NOW, set(), filer)
    a = sent[-1][0] if sent else {}
    ok(a.get("expedite") == ["STEVE_LANE_UNSTICK_ABCD"] and "owner: Relentless, STEVE_LANE_UNSTICK_ABCD expedited" in a.get("title", ""),
       "7: the unclaimed-incident alarm carries its owner (the incident item, expedited)", a)
    ok(OW.target_problem(dict(st, expedite_field=3)) is not None, "7: a bad expedite_field is a bad target", None)
    clone = TMP / "clone"
    (clone / "src/RimMandrake/rimflow").mkdir(parents=True)
    rec = TMP / "rec.json"
    (clone / "src/RimMandrake/rimflow/relentless.py").write_text(
        "import json, os, sys\nopen(%r, 'w').write(json.dumps({'argv': sys.argv[1:], 'gen': os.environ.get('RELENTLESS_GEN')}))\n"
        "sys.exit(3 if 'BAD' in sys.argv[3] else 0)\n" % str(rec))
    os.environ["RELENTLESS_GEN"] = "4"
    out = OW.expedite_owner(["STEVE_LANE_UNSTICK_ABCD"], {"clone": str(clone)}, "why")
    got = json.loads(rec.read_text())
    ok(out == {"STEVE_LANE_UNSTICK_ABCD": None} and got["argv"][:7] == ["expedite", "set", "STEVE_LANE_UNSTICK_ABCD", "--level",
                                                                     "expedited", "--by", "Operations"] and got["gen"] is None,
       "7: expedite_owner runs relentless expedite set --by Operations, worker env stripped", (out, got))
    out = OW.expedite_owner(["BAD_ITEM"], {"clone": str(clone)}, "why")
    ok(str(out.get("BAD_ITEM", "")).startswith("exit 3"), "7: a refusal is said per id, never raised", out)
    del os.environ["RELENTLESS_GEN"]
    ok(OW.expedite_of(st, {"x": {"first": ["x; rm -rf", "OK_ID"]}}) == ["OK_ID"], "7: only item-shaped ids are expedited", None)
    shutil.rmtree(TMP, ignore_errors=True)
    print("%d failed" % len(FAILS) if FAILS else "ALL PASS")
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
