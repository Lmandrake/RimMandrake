#!/usr/bin/env python3
"""selftest_ops_churn.py — OPS_CHURN_MEASURE_RETURNS_ARE_NOT_PROGRESS: Operations sees churn and owns its alarms.

On 2026-11-04 47 Relentless items had churned (one at gen 20, ~157M weighted tokens) on broken tests read as broken work,
and no reading said so. Each check fails on the code before the change:

1. rl_churn counts an item in churn by returns OR a repeated failure class, only with a failure inside the window; a
   blocked row or a finish is not a failure.
2. rl_churn's returned tokens: spend runs whose (item, gen) failed, placed in time by the gen's start row. x.by_end splits
   that spend by the gen's failed ending and lane, so an alarm reads its shared cause off the point. 2b: a gen is
   returned only when its LAST ending (a gen-less `done` row belongs to the gen open when it was written) is a failure.
   2c: under the shipped rules, the supervisor's reach/env bookkeeping rows (reach_repaired ...) are no failed attempt.
3. rl_churn is UNMEASURED (never 0) with no spend, with too much spend it cannot place, and with no items dir.
4. rules: a "returned" or "blind_fail" journal act is not progress; churn SLIs are incident SLIs whose units match.
5. ops_health.incident names the incident SLIs reading bad, and verdict carries it.
6. run_alarms files health.incident_slis at once under ONE fixed id and a repeat reopens that id (no new item).
7. The Steve unclaimed alarm names an owner: its todo carries the STEVE_LANE_UNSTICK_* ids to expedite, its title says
   so, and expedite_owner runs `relentless.py expedite set <id> --level expedited --by Operations` without a worker env.
8. CHURN_WATCH_BUILD_NAMES_EVERY_BOUNCER: one relentless.churn_item.<ID> reading per item that is bouncing, whose spend
   rises with nothing landed, or that is stuck in game/checking; the same-class repeat is windowed to a failure inside
   the window (B7: old A,A + new B is not churn); a held item no longer churning reads 0, and UNMEASURED when only the
   unread spend could still name it; new ones are capped per pass; the wildcard rule mints one fixed OPS_ name per item
   and run_alarms files it. A put-down item (blocked or held) gets none: nothing spends while it waits.

Fixtures only: a temp store, a temp RM_OPS_WATCH_DIR, a fake relentless.py, fake filer.

    python3 src/RimMandrake/Utils/selftest_ops_churn.py [--ops-watch <ops_watch.py to replay, e.g. a pre-fix copy>]
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
if "--ops-watch" in sys.argv:  # replay an instance: run these checks against another ops_watch.py (rimflow guard --instance)
    import types  # its source runs as if it sat in this Utils dir, so its HERE, rules and siblings are the real ones
    OW = types.ModuleType("ops_watch")
    OW.__file__ = str(Path(__file__).resolve().parent / "ops_watch.py")
    sys.modules["ops_watch"] = OW
    exec(compile(Path(sys.argv[sys.argv.index("--ops-watch") + 1]).read_text(), OW.__file__, "exec"), OW.__dict__)
else:
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
    ok(pct["x"].get("by_end") == ["harness/work 30.0%", "evidence/check 10.0%"],
       "2: by_end names the returned spend per ending class and lane, largest first (OPS_CHURN_DIAGNOSE_RETURNED_WORK_IWIV)",
       pct["x"].get("by_end"))
    # 2b: a gen whose LAST ending is an acceptance was not returned, whatever failed on the way (the
    # OPS_CHURN_DIAGNOSE_RETURNED_WORK_IWIV gen-1 shape: two UNMEASURED checks, a reach repair, then a gen-less `done`;
    # nothing went back to a worker). The 2026-11-05 reading counted 9.8 of its 66.2 points from such gens.
    s = TMP / "s1b"
    t1 = NOW - 2 * HOUR
    item(s, "E_ITEM", 0, [{"gen": 1, "at": iso(t1), "start": marker("E_ITEM", 1)},
                          {"gen": 1, "at": iso(t1 + 60), "end": "finish"},
                          {"gen": 1, "at": iso(t1 + 70), "end": "unmeasured"},
                          {"gen": 1, "at": iso(t1 + 80), "end": "unmeasured"},
                          {"gen": 1, "at": iso(t1 + 90), "end": "reach_adopted"},
                          {"gen": 1, "at": iso(t1 + 95), "end": "reach_repaired"},
                          {"at": iso(t1 + 99), "end": "done", "sha": "abc"}])
    item(s, "F_ITEM", 1, [{"gen": 1, "at": iso(t1), "start": marker("F_ITEM", 1)},
                          {"gen": 1, "at": iso(t1 + 60), "end": "finish"},
                          {"gen": 1, "at": iso(t1 + 70), "end": "blind_fail"}])
    runs = {marker("E_ITEM", 1): 500, marker("E_ITEM", 1, "check"): 300, marker("F_ITEM", 1): 200}
    (s / ("spend-%s.json" % time.strftime("%Y%m%d", time.gmtime(NOW)))).write_text(json.dumps({"runs": runs}))
    p = OW.rl_churn(s, NOW, CFG)
    pct = p["relentless.returned_tokens_pct"]
    ok(pct.get("m") == "MEASURED" and pct["x"]["returned"] == 200 and pct["v"] == 20.0
       and pct["x"]["by_end"] == ["blind_fail/work 20.0%"],
       "2b: a gen that ended done is not returned (its earlier unmeasured/reach rows sent nothing back); one ending in a "
       "failure is (OPS_CHURN_DIAGNOSE_RETURNED_WORK_IWIV)", pct)
    # 2c: the supervisor's own bookkeeping rows are no failed attempt (OPS_CHURN_DIAGNOSE_RETURNED_WORK_IWIV gen 5): the
    # reach repair's probe passing (reach_repaired), its waiter released (reach_waiter_released), the move to the repair
    # (reach_adopted), a hold before a re-check (reach_held) and an environment routed to a fixer with no builder
    # (game_env_route). Read under the SHIPPED rules, they made 'unmeasured failed it 4 times' out of two blind checks
    # and a passed probe, and put 6 of 50 items in churn on 2026-11-05.
    rules_cfg = json.loads((Path(OW.__file__).parent / "ops_watch_rules.json").read_text())["relentless"]
    s = TMP / "s1c"
    t1 = NOW - 2 * HOUR
    item(s, "G_ITEM", 0, [{"gen": 1, "at": iso(t1), "start": marker("G_ITEM", 1)},
                          {"gen": 1, "at": iso(t1 + 60), "end": "finish"},
                          {"gen": 1, "at": iso(t1 + 70), "end": "unmeasured"},
                          {"gen": 1, "at": iso(t1 + 80), "end": "reach_adopted"},
                          {"gen": 1, "at": iso(t1 + 90), "end": "reach_repaired"},
                          {"gen": 1, "at": iso(t1 + 95), "end": "reach_waiter_released"},
                          {"gen": 1, "at": iso(t1 + 96), "end": "reach_waiter_released"},
                          {"gen": 1, "at": iso(t1 + 97), "end": "reach_held"},
                          {"gen": 1, "at": iso(t1 + 98), "end": "game_env_route"},
                          {"gen": 1, "at": iso(t1 + 99), "end": "game_env_route"}])
    (s / ("spend-%s.json" % time.strftime("%Y%m%d", time.gmtime(NOW)))).write_text(
        json.dumps({"runs": {marker("G_ITEM", 1): 700, marker("G_ITEM", 1, "check"): 300}}))
    p = OW.rl_churn(s, NOW, rules_cfg)
    ci, pct = p["relentless.churn_items"], p["relentless.returned_tokens_pct"]
    ok(ci.get("v") == 0 and pct.get("m") == "MEASURED" and pct["x"]["returned"] == 0
       and {"reach_adopted", "reach_repaired", "reach_waiter_released", "reach_held", "game_env_route"}
       <= set(rules_cfg["churn_not_fail_ends"]),
       "2c: reach/env bookkeeping ends are no failed attempt under the shipped rules: a repeated bookkeeping row is not churn and "
       "a gen whose last row is game_env_route sent nothing back", (ci, pct.get("x"), rules_cfg["churn_not_fail_ends"]))
    # 2d: a wait whose blocker ended (relentless_attrib.resume writes end=released) is no failed attempt
    # (OPS_CHURN_DIAGNOSE_PLANET_VBIW_HJEC): PLANET_ATMOSPHERE_CLOUD_COST_1, 6 returns all > 12 h old, rang
    # 'bouncing: 6 returns' off a 13:30Z released row alone. A real failure in the window still speaks.
    s = TMP / "s1d"
    t0, t1 = NOW - 50 * HOUR, NOW - 1 * HOUR
    item(s, "R_ITEM", 6, [{"gen": 1, "at": iso(t0), "start": marker("R_ITEM", 1)},
                          {"gen": 1, "at": iso(t0 + 60), "end": "proof_weak"},
                          {"gen": 3, "at": iso(t0 + 120), "end": "game_proof_unmeasured"},
                          {"gen": 3, "at": iso(t1), "end": "released"},
                          {"gen": 3, "at": iso(t1 + 60), "end": "game_env_route"},
                          {"gen": 3, "at": iso(t1 + 120), "end": "released"}])
    p = OW.rl_churn(s, NOW, rules_cfg)
    ok(p["relentless.churn_items"].get("v") == 0 and "released" in rules_cfg["churn_not_fail_ends"],
       "2d: a released wait-resume row is no failed attempt: old returns stay spent", (p["relentless.churn_items"],
                                                                                      rules_cfg["churn_not_fail_ends"]))
    s = TMP / "s1e"
    item(s, "R_ITEM", 6, [{"gen": 1, "at": iso(t0), "start": marker("R_ITEM", 1)},
                          {"gen": 3, "at": iso(t1), "end": "released"},
                          {"gen": 5, "at": iso(t1 + 60), "end": "blind_fail"}])
    p = OW.rl_churn(s, NOW, rules_cfg)
    ok(p["relentless.churn_items"].get("v") == 1, "2d: a real failure after a release still bounces", p["relentless.churn_items"])
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
    # 5b RELAPSE_CHURN_FIX_DIED_TWICE: churn-20261104075956 closed and relapsed twice in 24 h because infra_share (budget
    # spent, 39 of 48 h bad) swung over its < 40 line for 1-2.5 h on an 8-10 h cycle (7.5 .. 65, 2026-11-06). Each dip read
    # sane and closed the incident. A point back over its line is not recovery while that SLI's budget is spent: HELD.
    sli = {"name": "infra_share", "key": "relentless.live_measured_pct", "unit": "%", "op": "<", "x": 40, "incident": True}
    hc5 = {"slis": [sli], "window_h": 48, "allowed_bad_h": 24, "max_gap_h": 1.0}
    flap = [{"t": NOW - (48 - i * 0.25) * HOUR, "points": {"relentless.live_measured_pct": {
        "m": "MEASURED", "unit": "%", "v": 52.5 if (i * 0.25) % 9 >= 7 else 15.0}}} for i in range(192)]
    b5 = OH.budget({"relentless.live_measured_pct": {"m": "MEASURED", "unit": "%", "v": 52.5}}, {"relentless": flap}, hc5, NOW)
    inc5 = OH.incident(b5, hc5)
    ok(b5["infra_share"]["now"] == "ok" and b5["infra_share"]["spent"] and inc5.get("held") == ["infra_share"]
       and inc5["bad"] == [] and "held" in inc5["cause"],
       "5b: a spent incident SLI reading ok for one dip is HELD, named in the cause", (b5["infra_share"], inc5))
    real = OH.publish
    try:
        OH.publish = lambda *a, **k: {"spent": ["infra_share"], "system_items": [], "why": "w", "state": "degraded",
                                      "drifted": [], "incident": inc5, "recurring_unguarded": []}
        pt5 = OW.publish_health({}, {}, {}, {}, NOW)["health.incident_slis"]
    finally:
        OH.publish = real
    ok(pt5.get("m") == "MEASURED" and pt5.get("v") == 1 and "infra_share" in pt5.get("x", {}).get("cause", ""),
       "5b: health.incident_slis stays > 0 while it is held, so the incident cannot close on the dip", pt5)
    calm = [dict(r, points={"relentless.live_measured_pct": {"m": "MEASURED", "unit": "%", "v": 52.5}}) for r in flap]
    inc6 = OH.incident(OH.budget({"relentless.live_measured_pct": {"m": "MEASURED", "unit": "%", "v": 52.5}},
                                 {"relentless": calm}, hc5, NOW), hc5)
    ok(inc6.get("held") == [] and inc6["bad"] == [] and inc6["cause"] == "none",
       "5b: an SLI inside its budget and ok now is neither bad nor held: the incident closes", inc6)
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
    sys.path.insert(0, str(Path(OW.__file__).resolve().parent.parent / "rimflow"))
    import incident as IN
    rt = IN.route_of(IN.load_table(), "health.incident_slis") or {}
    ok(rt.get("cause") not in (None, "work_belt") and rt.get("reader") == "Operations",
       "6: its own cause, so an old open work_belt incident cannot swallow its Conductor line", rt)
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
    # 8
    t1, old = NOW - 2 * HOUR, NOW - 40 * HOUR
    a_a_b = [(old, "harness"), (old + 60, "harness"), (t1, "evidence")]
    ok(not OW.in_churn({"returns": 0}, a_a_b, NOW, CFG) and OW.churn_why({"returns": 0}, a_a_b, NOW, CFG) == [],
       "8: B7, an old A,A and a new B is not a same-class repeat", OW.churn_why({"returns": 0}, a_a_b, NOW, CFG))
    ok(OW.in_churn({"returns": 0}, a_a_b + [(t1 + 9, "harness")], NOW, CFG), "8: a class failing again inside the window is", None)
    # OPS_CHURN_DIAGNOSE_STILLSAND_WDMI_CRMC: STILLSAND_DUNE_GALE_LIVE_1, 3 returns of 3 causes, blind PASS after the last
    sg = {"returns": 3, "status": "game", "check": {"verdict": "PASS", "verdict_at": t1 + 3600}}
    sg_f = [(old, "blind_fail"), (old + 60, "proof_rework"), (t1, "game_fail")]
    ok(OW.churn_why(sg, sg_f, NOW, CFG) == [], "8: a blind PASS after the last failure is no bounce", OW.churn_why(sg, sg_f, NOW, CFG))
    ok(OW.churn_why(dict(sg, check={"verdict": "FAIL", "verdict_at": t1 + 3600}), sg_f, NOW, CFG) == ["3 returns"],
       "8: a FAIL verdict does not end the bounce", None)
    ok(OW.churn_why(sg, sg_f + [(t1 + 3700, "game_fail")], NOW, CFG)[:1] == ["3 returns"],
       "8: a failure after the PASS bounces again", OW.churn_why(sg, sg_f + [(t1 + 3700, "game_fail")], NOW, CFG))
    # OPS_CHURN_DIAGNOSE_ART_XODX_FYLS: ART_OVERRIDE_FAMILY_SCRIPT_1, returns 4, game_env_fix at 06:13Z and 08:17Z (a stale
    # 'mandrake' remedy from the pre-d262af07 envcause parser), held, then unheld by the Conductor at 15:40Z with the cause
    # removed; at 15:55Z it re-rang 'bouncing: 4 returns; game_env_fix failed it 2 times' off the failures the unhold resolved
    art = {"returns": 4, "status": "game"}
    art_f = [(NOW - 9.7 * HOUR, "game_env_fix"), (NOW - 7.6 * HOUR, "game_env_fix")]
    art_rows = [{"at": iso(NOW - 9.7 * HOUR), "end": "game_env_fix", "gen": 9}, {"at": iso(NOW - 7.6 * HOUR), "end": "game_env_fix", "gen": 9},
                {"at": iso(NOW - 0.25 * HOUR), "end": "unhold", "to": "game"}]
    def why_r(fails, r):      # the pre-fix churn_why takes no resume time: it fails here, never crashes the run
        try:
            return OW.churn_why(art, fails, NOW, CFG, 0, r), OW.in_churn(art, fails, NOW, CFG, 0, r)
        except TypeError as e:
            return ["TypeError: %s" % e], True
    art_r = OW.attempts_resumed(art_rows) if hasattr(OW, "attempts_resumed") else None
    ok(art_r is not None and abs(art_r - (NOW - 0.25 * HOUR)) < 2, "8: the latest unhold row is the resume time", art_r)
    ok(why_r(art_f, art_r) == ([], False), "8: an unhold after the last failure is no bounce (ART_OVERRIDE_FAMILY_SCRIPT_1)",
       why_r(art_f, art_r))
    # game_env_fix is a churn env end (OPS_CHURN_DIAGNOSE_WEEPINGSTONE_BENK_YIMV): the lane's own fix spends the returns
    # before it, and only the env class repeating inside the window (after the unhold) speaks
    ok(why_r(art_f + [(NOW - 60, "game_env_fix")], art_r)[0] == [],
       "8: one lane fix after the unhold is no bounce", why_r(art_f + [(NOW - 60, "game_env_fix")], art_r))
    two_after = art_f + [(NOW - 600, "game_env_fix"), (NOW - 60, "game_env_fix")]
    ok(why_r(two_after, art_r)[0] == ["game_env_fix failed it 2 times"],
       "8: two lane fixes after the unhold bounce", why_r(two_after, art_r))
    ok(OW.churn_why(art, art_f, NOW, CFG) == ["game_env_fix failed it 2 times"], "8: no unhold, still a bounce",
       OW.churn_why(art, art_f, NOW, CFG))
    # 8w OPS_CHURN_DIAGNOSE_WEEPINGSTONE_BENK_YIMV: WEEPINGSTONES_HANDLER_VANISHES_1, returns 3 (gen 1 blind_fail, gen 3
    # proof_weak 2026-11-03, gen 5 game_fail 2026-11-04), gen 7 blind PASS, game_env_route 11-05 14:52Z, unhold 20:29Z,
    # then ONE game_env_fix 11-06 07:17Z (the lane restaging Biomes, not in the running load): it rang 'bouncing: 3
    # returns'. Read under the SHIPPED rules, as ops_watch reads it.
    ship = json.loads((Path(OW.__file__).parent / "ops_watch_rules.json").read_text())["relentless"]
    ws_rows = [{"gen": 1, "at": iso(NOW - 68 * HOUR), "end": "blind_fail"}, {"gen": 3, "at": iso(NOW - 67.5 * HOUR), "end": "proof_weak"},
               {"gen": 5, "at": iso(NOW - 29 * HOUR), "end": "game_fail"}, {"gen": 7, "at": iso(NOW - 22 * HOUR), "end": "finish"},
               {"gen": 7, "at": iso(NOW - 16.4 * HOUR), "end": "game_env_route"}, {"at": iso(NOW - 10.8 * HOUR), "end": "unhold", "to": "game"},
               {"gen": 7, "at": iso(NOW - 0.2 * HOUR), "end": "game_env_fix"}]
    ok_ends = set(ship["churn_not_fail_ends"])
    ws_f = [f for f in (OW.attempt_failed(r, ok_ends) for r in ws_rows) if f]
    ws = {"returns": 3, "status": "game"}
    ws_r = OW.attempts_resumed(ws_rows)
    ok(OW.churn_why(ws, ws_f, NOW, ship, 0, ws_r) == [] and not OW.in_churn(ws, ws_f, NOW, ship, 0, ws_r),
       "8w: one lane env fix in the game phase spends three old returns (WEEPINGSTONES_HANDLER_VANISHES_1)",
       (ws_f, OW.churn_why(ws, ws_f, NOW, ship, 0, ws_r)))
    ws_f2 = ws_f + [(NOW - 60, "game_env_fix")]
    ok(OW.churn_why(ws, ws_f2, NOW, ship, 0, ws_r) == ["game_env_fix failed it 2 times"],
       "8w: the lane fixing it twice inside the window still speaks", OW.churn_why(ws, ws_f2, NOW, ship, 0, ws_r))
    ok(OW.churn_why(ws, ws_f + [(NOW - 60, "game_fail")], NOW, ship, 0, ws_r)[:1] == ["3 returns"],
       "8w: a real game_fail after the lane fix bounces with its history", OW.churn_why(ws, ws_f + [(NOW - 60, "game_fail")], NOW, ship, 0, ws_r))
    # 8h OPS_CHURN_DIAGNOSE_HEAVY_ZWWY_NYJN: HEAVY_TEXTURES_MEASURE_REAL_VRAM, returns 3 (gen 1 game_unmeasured 11-03, gen 3
    # unmeasured + game_stale_build 11-05 23:49Z), unhold 11-05 20:29Z, gen 5 blind PASS 11-06 00:14Z, then ONE game_stage
    # 13:55Z (the stager's companion exact-hash gate, fixed by 4ca2cfb99d at 14:27Z): it rang 'bouncing: 3 returns' at
    # 14:16Z. A stager stop is a game-phase ending (entered only through a blind PASS) that blames the stager, not the work.
    hv_rows = [{"gen": 1, "at": iso(NOW - 66 * HOUR), "end": "game_unmeasured"}, {"gen": 3, "at": iso(NOW - 37 * HOUR), "end": "unmeasured"},
               {"gen": 3, "at": iso(NOW - 34.5 * HOUR), "end": "game_env_route"}, {"at": iso(NOW - 20.6 * HOUR), "end": "unhold", "to": "game"},
               {"gen": 3, "at": iso(NOW - 17.2 * HOUR), "end": "game_stale_build"}, {"gen": 5, "at": iso(NOW - 17 * HOUR), "end": "finish"},
               {"gen": 5, "at": iso(NOW - 0.35 * HOUR), "end": "game_stage"}]
    hv_f = [f for f in (OW.attempt_failed(r, ok_ends) for r in hv_rows) if f]
    hv = {"returns": 3, "status": "queued", "check": {"verdict": "PASS", "verdict_at": NOW - 16.8 * HOUR}}
    hv_r = OW.attempts_resumed(hv_rows)
    ok(len(hv_f) == 4 and OW.churn_why(hv, hv_f, NOW, ship, 0, hv_r) == [],
       "8h: one stager stop after a blind PASS spends three old returns (HEAVY_TEXTURES_MEASURE_REAL_VRAM)",
       (hv_f, OW.churn_why(hv, hv_f, NOW, ship, 0, hv_r)))
    ok("game_stage" in ship["churn_env_ends"] and "game_stage" in OW.CHURN_ENV_ENDS, "8h: game_stage is a shipped churn env end")
    hv_f2 = hv_f + [(NOW - 60, "game_stage")]
    ok(OW.churn_why(hv, hv_f2, NOW, ship, 0, hv_r) == ["game_stage failed it 2 times"],
       "8h: the stager stopping twice inside the window still speaks", OW.churn_why(hv, hv_f2, NOW, ship, 0, hv_r))
    ok(OW.churn_why(hv, hv_f + [(NOW - 60, "game_fail")], NOW, ship, 0, hv_r)[:1] == ["3 returns"],
       "8h: a real game_fail after the stager stop bounces with its history",
       OW.churn_why(hv, hv_f + [(NOW - 60, "game_fail")], NOW, ship, 0, hv_r))
    # 8s OPS_CHURN_DIAGNOSE_WORLD_AVST_JRDU: WORLD_DECALS_BUILD_ATLAS_PIPELINE_ONCE, blind PASS on gen 7 (10:55Z), then at
    # 18:11Z a game_stale_build (WORLD_WATER_REDRAW_SEAS_THAT_READ_DEEP rebuilt the shared DLL and edited RM_WorldLook.cs),
    # re-finished on HEAD at 18:21Z; at 18:29:49Z, its gen-9 check in flight (state.json's check now that one, the gen-7
    # PASS gone), it re-rang 'bouncing: 4 returns' off three returns the PASS had spent. A stale build is written only in
    # the game phase, entered only through a blind PASS: it proves that PASS and is no failure of the item's work.
    wd = {"returns": 4, "status": "checking", "check": {"at": NOW - 6 * 60}}
    wd_f = [(NOW - 61 * HOUR, "proof_weak"), (NOW - 61 * HOUR + 600, "proof_rework"), (NOW - 8.8 * HOUR, "proof_found_defect"),
            (NOW - 0.3 * HOUR, "game_stale_build")]
    ok(OW.churn_why(wd, wd_f, NOW, CFG) == [] and not OW.in_churn(wd, wd_f, NOW, CFG),
       "8s: a stale build after a PASS spends the returns before it (WORLD_DECALS_BUILD_ATLAS_PIPELINE_ONCE)",
       OW.churn_why(wd, wd_f, NOW, CFG))
    ok(OW.churn_why(dict(wd, returns=5), wd_f + [(NOW - 60, "game_fail")], NOW, CFG)[:1] == ["5 returns"],
       "8s: a real failure after the stale build bounces with its history",
       OW.churn_why(dict(wd, returns=5), wd_f + [(NOW - 60, "game_fail")], NOW, CFG))
    two = [(NOW - 3 * HOUR, "game_stale_build"), (NOW - 0.3 * HOUR, "game_stale_build")]
    ok(OW.churn_why({"returns": 2}, two, NOW, CFG) == ["game_stale_build failed it 2 times"],
       "8s: two stale builds in the window still read a same-class repeat (the SUMP_TAR_FIRE_NETWORK_1 signal)",
       OW.churn_why({"returns": 2}, two, NOW, CFG))
    # OPS_CHURN_DIAGNOSE_SUMP_GSVT_SSCT, 19:07Z: three stale builds in the window (11:07Z, 15:35Z, 18:16Z), each a
    # supervisor carry defect fixed since; a `recarried` row (the supervisor sent the returned build back to its game step,
    # no worker) spends them, as an unhold does; a stale build after it still speaks
    three = [(NOW - 8 * HOUR, "game_stale_build"), (NOW - 3.5 * HOUR, "game_stale_build"), (NOW - 0.9 * HOUR, "game_stale_build")]
    rc = OW.attempts_resumed([{"at": iso(NOW - 0.2 * HOUR), "gen": 10, "routed": "recarried", "to": "game"}])
    ok(rc is not None and abs(rc - (NOW - 0.2 * HOUR)) < 2, "8s: a recarried row is a resume time", rc)
    ok(OW.churn_why({"returns": 5, "status": "game"}, three, NOW, CFG, 0, rc) == [],
       "8s: stale builds before a recarry are spent (SUMP_TAR_FIRE_NETWORK_1)", OW.churn_why({"returns": 5}, three, NOW, CFG, 0, rc))
    after = three + [(NOW - 0.1 * HOUR, "game_stale_build"), (NOW - 0.05 * HOUR, "game_stale_build")]
    ok(OW.churn_why({"returns": 7}, after, NOW, CFG, 0, rc) == ["game_stale_build failed it 2 times"],
       "8s: two stale builds after the recarry still speak", OW.churn_why({"returns": 7}, after, NOW, CFG, 0, rc))
    cfg8 =dict(CFG, item_bands=rules["relentless"]["item_bands"], churn_item_stuck_stages=["game", "checking"],
                churn_item_new_per_pass=5)
    s8 = TMP / "s8"
    def st8(name, state, rows):
        d = s8 / "items" / name
        d.mkdir(parents=True)
        (d / "state.json").write_text(json.dumps(state))
        (d / "attempts.jsonl").write_text("".join(json.dumps(r) + "\n" for r in rows))
    st8("BOUNCE_ITEM", {"status": "queued", "returns": 3, "gen": 4, "spent": 2e6},
        [{"gen": 4, "at": iso(t1), "start": marker("BOUNCE_ITEM", 4)}, {"gen": 4, "at": iso(t1 + 60), "end": "harness"}])
    st8("SPEND_ITEM", {"status": "running", "returns": 0, "gen": 1, "spent": 7e6},
        [{"gen": 1, "at": iso(t1), "start": marker("SPEND_ITEM", 1)}])
    st8("STUCK_ITEM", {"status": "game", "returns": 0, "gen": 1, "spent": 1e6, "game": {"entered_at": NOW - 8 * 86400}}, [])
    st8("CALM_ITEM", {"status": "checking", "returns": 0, "gen": 1, "spent": 9e6, "check": {"at": NOW - 600}},
        [{"gen": 1, "at": iso(old), "start": marker("CALM_ITEM", 1)}])
    st8("LANDED_ITEM", {"status": "done", "returns": 5, "gen": 6, "spent": 9e6},
        [{"gen": 6, "at": iso(t1), "start": marker("LANDED_ITEM", 6)}, {"gen": 6, "at": iso(t1 + 5), "end": "harness"},
         {"gen": 6, "at": iso(t1 + 6), "end": "harness"}])
    runs = {marker("SPEND_ITEM", 1): 400000, marker("BOUNCE_ITEM", 4): 1000, marker("LANDED_ITEM", 6): 5000,
            marker("OLDGEN_ITEM", 1): 9000, marker("PARKED_ITEM", 13): 365432, marker("PUT_DOWN_ITEM", 1): 9869198}
    # OPS_CHURN_DIAGNOSE_PIPELINE_NIZE_JOZV: PIPELINE_RENAME_WORKERS_NOW_SWAPPABLE, its gen started in the window and
    # blocked on reach since, spent nothing after: a put-down item is sent no run, so its window spend is not rising
    st8("PUT_DOWN_ITEM", {"status": "blocked", "returns": 0, "gen": 1, "spent": 10.45e6, "wait": {"kind": "reach"}},
        [{"gen": 1, "at": iso(t1), "start": marker("PUT_DOWN_ITEM", 1)},
         {"gen": 1, "at": iso(t1 + 50), "end": "reach_adopted"}])
    # OPS_CHURN_DIAGNOSE_BRIDGE_GRXX_AYXK: BRIDGE_STALL_DIAGNOSTIC_1, blocked a day, its gen started AND ended before the
    # window, but its run sits in a day file the window reaches: no spend in the window, so not 'spend rising'
    st8("PARKED_ITEM", {"status": "blocked", "returns": 0, "gen": 13, "spent": 7.3e6},
        [{"gen": 13, "at": iso(old), "start": marker("PARKED_ITEM", 13)},
         {"gen": 13, "at": iso(old + 400), "end": "blocked", "kind": "item", "class": "blocked_by_predecessor"}])
    st8("OLDGEN_ITEM", {"status": "running", "returns": 0, "gen": 1, "spent": 8e6},
        [{"gen": 1, "at": iso(old), "start": marker("OLDGEN_ITEM", 1)}])
    # OPS_CHURN_DIAGNOSE_OPS_LPTI_ESRT: OPS_CHURN_DIAGNOSE_SUMP_GSVT_SSCT, closed 16:33Z and 18:59Z, rang 'bouncing:
    # bad_candidate failed it 2 times' at 19:36Z, its gen-11 candidate in check, off a gen-3 failure before the first
    # close and a gen-9 one: a done row spends the life before it, a reopened item counts fresh
    reo = [{"gen": 3, "at": iso(NOW - 3.3 * HOUR), "start": marker("REOPENED_ITEM", 3)},
           {"gen": 3, "at": iso(NOW - 3.2 * HOUR), "end": "bad_candidate"},
           {"at": iso(NOW - 3 * HOUR), "end": "done", "sha": "a"},
           {"gen": 9, "at": iso(NOW - 0.6 * HOUR), "start": marker("REOPENED_ITEM", 9)},
           {"gen": 9, "at": iso(NOW - 0.4 * HOUR), "end": "bad_candidate"},
           {"gen": 11, "at": iso(NOW - 0.4 * HOUR), "start": marker("REOPENED_ITEM", 11)},
           {"gen": 11, "at": iso(NOW - 0.2 * HOUR), "end": "finish", "sha": "b"}]
    st8("REOPENED_ITEM", {"status": "checking", "returns": 1, "gen": 11, "spent": 1e5, "check": {"at": NOW - 600}}, reo)
    rf = [(NOW - 3.2 * HOUR, "bad_candidate"), (NOW - 0.4 * HOUR, "bad_candidate")]
    ok(OW.churn_why({"returns": 1}, rf, NOW, CFG) == ["bad_candidate failed it 2 times"],
       "8r: across all rows the two failures read a repeat (the pre-fix 19:36Z reading)", OW.churn_why({"returns": 1}, rf, NOW, CFG))
    ok(hasattr(OW, "fails_since_close") and OW.fails_since_close(rf, reo) == rf[1:],
       "8r: a done row spends the failures before it", OW.fails_since_close(rf, reo) if hasattr(OW, "fails_since_close") else None)
    ok(hasattr(OW, "fails_since_close") and OW.fails_since_close(rf, reo[:2] + reo[3:]) == rf,
       "8r: no done row, every failure stands", None)
    reo_after = rf + [(NOW - 0.1 * HOUR, "bad_candidate")]
    ok(hasattr(OW, "fails_since_close") and OW.churn_why({"returns": 2}, OW.fails_since_close(reo_after, reo), NOW, CFG)
       == ["bad_candidate failed it 2 times"], "8r: two failures after the close still repeat", None)
    (s8 / ("spend-%s.json" % time.strftime("%Y%m%d", time.gmtime(NOW)))).write_text(json.dumps({"runs": runs}))
    (TMP / "ops" / "alarms.json").write_text(json.dumps({"CHURN_ITEM:relentless.churn_item.CALM_ITEM": {"state": "OPEN"}}))
    p8 = OW.rl_churn(s8, NOW, cfg8)
    ci = {k[len(OW.CHURN_ITEM_PREFIX):]: v for k, v in p8.items() if k.startswith(OW.CHURN_ITEM_PREFIX)}
    ok(set(ci) == {"BOUNCE_ITEM", "SPEND_ITEM", "STUCK_ITEM", "CALM_ITEM", "OLDGEN_ITEM"}, "8: one reading per churning or held item, none for a landed one", sorted(ci))
    ok(ci.get("BOUNCE_ITEM", {}).get("v") == 1 and "bouncing: 3 returns" in ci["BOUNCE_ITEM"]["x"]["said"],
       "8: a bouncer is named with its returns", ci.get("BOUNCE_ITEM"))
    ok(ci.get("SPEND_ITEM", {}).get("v") == 1 and "spend rising" in ci["SPEND_ITEM"]["x"]["said"],
       "8: spend at the hot band, rising in the window, nothing landed", ci.get("SPEND_ITEM"))
    ok(ci.get("STUCK_ITEM", {}).get("v") == 1 and "stuck: game" in ci["STUCK_ITEM"]["x"]["said"],
       "8: a game item past its hot age band is stuck", ci.get("STUCK_ITEM"))
    ok(ci.get("CALM_ITEM", {}).get("v") == 0 and ci["CALM_ITEM"].get("m") == "MEASURED",
       "8: a held item no longer churning reads 0 (clears); high lifetime spend alone is not rising", ci.get("CALM_ITEM"))
    ok("REOPENED_ITEM" not in ci, "8r: a reopened item counts no failure from before its close (SUMP_GSVT 19:36Z)",
       ci.get("REOPENED_ITEM"))
    ok("PARKED_ITEM" not in ci, "8: a gen that started and ended before the window is no spend in it (a parked item)",
       ci.get("PARKED_ITEM"))
    ok("PUT_DOWN_ITEM" not in ci, "8: a blocked item's window spend is flat, not 'spend rising'", ci.get("PUT_DOWN_ITEM"))
    ok(ci.get("OLDGEN_ITEM", {}).get("v") == 1, "8: a gen started before the window that still burns is rising spend", ci.get("OLDGEN_ITEM"))
    # OPS_CHURN_DIAGNOSE_JAM_VPZP_ECXS: JAM_CLASS_BUILD_OPS_DETECTOR_PER_CLASS, blocked on a reach ticket with 4
    # 'unmeasured' inside the window and its spend hot, read bouncing + spend rising: a put-down item spends nothing
    jam = {"returns": 0, "gen": 1, "spent": 11.1e6}
    unm = [(t1 + i, "unmeasured") for i in range(4)]
    pd = OW.churn_item_points({"PD_BLOCKED": (dict(jam, status="blocked", wait={"kind": "reach"}), unm, 9e6),
                               "PD_HELD": (dict(jam, status="held"), unm, 9e6),
                               "PD_LIVE": (dict(jam, status="candidate"), unm, 9e6)}, NOW, cfg8, True, set())
    ok(set(pd) == {OW.CHURN_ITEM_PREFIX + "PD_LIVE"}, "8: a blocked or held item gets no churn reading", sorted(pd))
    said = pd.get(OW.CHURN_ITEM_PREFIX + "PD_LIVE", {}).get("x", {}).get("said", "")
    ok("bouncing: unmeasured failed it 4 times" in said and "spend rising" in said,
       "8: the same item, picked up again, reads bouncing and spend rising", said)
    # OPS_CHURN_DIAGNOSE_OLLOPOM_JLHV_AJHK: OLLOPOM_BEAUTY_VERIFY_DEPLOYED_NOT_SEEN, offline-green and in the game phase
    # (put down: one live user at a time) from 10:05Z, re-rang 'spend rising: 8.1M, 325k in the last 24h' off its 09:54Z
    # gen-2 work run: the game phase sends no work or check run, so its window spend is flat; 'stuck: game' still speaks
    gw = {"returns": 0, "gen": 2, "spent": 8.1e6, "status": "game", "game": {"entered_at": NOW - 7200, "phase": "prove"},
          "put_down": {"on": "one live user at a time: showing X holds the game phase", "at": NOW - 60}}
    pg = OW.churn_item_points({"GAME_WAIT": (gw, [], 325e3)}, NOW, cfg8, True, {"GAME_WAIT"})
    ok(pg.get(OW.CHURN_ITEM_PREFIX + "GAME_WAIT", {}).get("v") == 0,
       "8: a game-phase item's window spend is not 'spend rising'; its held alarm clears", pg)
    pdh = OW.churn_item_points({"PD_BLOCKED": (dict(jam, status="blocked"), unm, 9e6)}, NOW, cfg8, True, {"PD_BLOCKED"})
    ok(pdh.get(OW.CHURN_ITEM_PREFIX + "PD_BLOCKED", {}).get("v") == 0, "8: a held alarm on a put-down item reads 0 (clears)", pdh)
    # OPS_CHURN_DIAGNOSE_NIGHTLY_SCRM_GZGX: NIGHTLY_COP_FIX_RED_CYGHVG_QCWJ, quarantine-held (status held) after two
    # UNMEASURED checks at gen 9, was filed 'unmeasured failed it 2 times' by the code before the JAM fix; its alarm clears
    unm2 = [(t1, "unmeasured"), (t1 + 1, "unmeasured")]
    pdq = OW.churn_item_points({"PD_QUAR": (dict(jam, status="held", gen=9, spent=5.2e6, hold={"kind": "quarantine"}),
                                            unm2, 0)}, NOW, cfg8, True, {"PD_QUAR"})
    ok(pdq.get(OW.CHURN_ITEM_PREFIX + "PD_QUAR", {}).get("v") == 0, "8: a held alarm on a quarantine-held item reads 0", pdq)
    p8b = OW.rl_churn(s8, NOW, dict(cfg8, churn_item_new_per_pass=1))
    ok(sorted(k for k in p8b if k.startswith(OW.CHURN_ITEM_PREFIX)) == [OW.CHURN_ITEM_PREFIX + "CALM_ITEM", OW.CHURN_ITEM_PREFIX + "OLDGEN_ITEM"],
       "8: new items are capped per pass, largest spend first; held ones always read", sorted(p8b))
    full = OW.churn_item_points({"NEW_ITEM": ({"status": "queued", "returns": 3, "spent": 1}, [(t1, "x")], 0)}, NOW,
                                dict(cfg8, churn_item_max_open=2), True, {"H1_ITEM", "H2_ITEM"})
    ok(OW.CHURN_ITEM_PREFIX + "NEW_ITEM" not in full and full.get(OW.CHURN_ITEM_PREFIX + "H1_ITEM", {}).get("v") == 0,
       "8: no new item past churn_item_max_open held", sorted(full))
    odd = OW.churn_item_points({"T_ITEM": (None, [], 0), "L_ITEM": ({"status": ["x"], "returns": 3}, [(t1, "x")], 0)},
                               NOW, cfg8, True, {"T_ITEM"})
    ok(odd.get(OW.CHURN_ITEM_PREFIX + "T_ITEM", {}).get("m") == "UNMEASURED" and OW.CHURN_ITEM_PREFIX + "L_ITEM" in odd,
       "8: a torn held state holds; an odd status never crashes the reading", odd)
    ok(OW.churn_item_points({"N_ITEM": ({"status": "queued", "returns": 3}, [(t1, "x")], 0)}, NOW, cfg8, True,
                            OW.held_churn_items(["torn"])) == {}, "8: alarms.json unreadable: nothing new files", None)
    held = OW.churn_item_points({"CALM_ITEM": ({"status": "running", "spent": 9e6}, [], 0)}, NOW, cfg8, False, {"CALM_ITEM"})
    ok(held[OW.CHURN_ITEM_PREFIX + "CALM_ITEM"].get("m") == "UNMEASURED", "8: spend unread, a held item holds", held)
    tg8 = next(t for t in rules["targets"] if t.get("key") == "relentless.churn_item.*")
    import pulse_core as pc
    names = {}
    for n in ("ATMOSBASE_PROOF_FIX_UNLIT_LEAVES_DARK_LAMP", "ATMOSBASE_BUILD_OTHER_THING", "BUILD_CHURN_WATCH_THING", "B58_X_FIX_Y"):
        k = OW.CHURN_ITEM_PREFIX + n
        pt8 = OW.M(1, OW.CHURN_ITEM_UNIT, subject=OW.churn_subject(n))
        names[n] = OW.alarm_prefix(tg8, "CHURN_ITEM", k, {}, "CHURN_ITEM:" + k, pt8)
        ok(names[n] == OW.alarm_prefix(tg8, "CHURN_ITEM", k, {}, "CHURN_ITEM:" + k, pt8) and names[n].startswith("OPS_CHURN_DIAGNOSE_")
           and not pc._model().mint_problems(names[n], set()), "8: %s mints one fixed OPS_ name" % n, names[n])
    ok(len(set(names.values())) == len(names), "8: two items sharing a first word never share an alarm", names)
    (TMP / "ops" / "alarms.json").unlink()
    sent.clear()
    r8 = {"alarms": {"clear_passes": 1}, "targets": [tg8]}
    OW.run_alarms({OW.CHURN_ITEM_PREFIX + "BOUNCE_ITEM": ci["BOUNCE_ITEM"]}, r8, NOW, set(), filer)
    a8 = sent[-1][0] if sent else {}
    ok(a8.get("name", "").startswith("OPS_CHURN_DIAGNOSE_BOUNCE_") and "BOUNCE_ITEM" in a8.get("title", ""),
       "8: run_alarms files the item's own OPS_ alarm, its title naming the item", a8)
    ok(OW.held_churn_items() == {"BOUNCE_ITEM"}, "8: alarms.json now holds it, so its next calm pass reads 0", OW.held_churn_items())
    # 9 PUT_DOWN_ENDS (OPS_CHURN_DIAGNOSE_HORRORS_XSDJ_RKYR): HORRORS_RAIDING_FACTION_1, 3 returns, every real failure
    # older than the window, read 'bouncing: 3 returns' because a Conductor `hold` ending (relentless.hold: "No strike, no
    # failed approach") counted as a failed attempt inside it. The SHIPPED ends list decides.
    ends = rules["relentless"]["churn_not_fail_ends"]
    cfg9 = dict(CFG, churn_not_fail_ends=ends)
    old9 = NOW - 30 * HOUR
    for end in ("hold", "conductor_hold", "game_fail"):
        s9 = TMP / ("s9_" + end)
        nm = "H9_ITEM"
        d = s9 / "items" / nm
        d.mkdir(parents=True)
        (d / "state.json").write_text(json.dumps({"status": "queued", "returns": 3, "gen": 6, "spent": 1}))
        rows = [{"gen": 5, "at": iso(old9), "start": marker(nm, 5)}, {"gen": 5, "at": iso(old9 + 60), "end": "game_fail"},
                {"gen": 6, "at": iso(NOW - 4 * HOUR), "end": end, "said": "x"}]
        (d / "attempts.jsonl").write_text("".join(json.dumps(r) + "\n" for r in rows))
        (TMP / "ops" / "alarms.json").write_text("{}")
        p9 = OW.rl_churn(s9, NOW, cfg9)
        hit = OW.CHURN_ITEM_PREFIX + nm in p9
        if end == "game_fail":
            ok(hit and "bouncing: 3 returns" in p9[OW.CHURN_ITEM_PREFIX + nm]["x"]["said"],
               "9: a real failure in the window still reads bouncing", p9.get(OW.CHURN_ITEM_PREFIX + nm))
        else:
            ok(end in ends and not hit and p9["relentless.churn_items"].get("v") == 0,
               "9: a '%s' ending is a put-down, not a failure: no churn" % end, (end in ends, sorted(p9)))
    # 9a OPS_CHURN_DIAGNOSE_ENGINE_QCHQ_AUUY: ENGINE_REVIEW_FIX_LEFTOVERS_STILL_WARM's real rows at the 20:36Z alarm, one
    # proof_weak and two account change-overs (relentless.account_lost: no strike, no return), rang 'bouncing: account_lost
    # failed it 2 times'. The account's act is no bounce; real failures beside it still speak; its spend stays visible.
    a9 = {"gen": 1, "at": iso(NOW - 4 * HOUR), "end": "account_lost", "detail": "account change-over closed every Claude process"}
    b9 = {"gen": 5, "at": iso(NOW - 2 * HOUR), "end": "account_lost", "detail": "account change-over closed every Claude process"}
    def case9a(tag, returns, rows):
        s = TMP / ("s9a_" + tag)
        d = s / "items" / "A9_ITEM"
        d.mkdir(parents=True)
        (d / "state.json").write_text(json.dumps({"status": "running", "returns": returns, "gen": 7, "spent": 1}))
        (d / "attempts.jsonl").write_text("".join(json.dumps(r) + "\n" for r in rows))
        (TMP / "ops" / "alarms.json").write_text("{}")
        return s, OW.rl_churn(s, NOW, cfg9)
    fin9 = {"gen": 3, "at": iso(NOW - 3.5 * HOUR), "end": "finish", "sha": "a2bbb67"}
    weak9 = {"gen": 3, "at": iso(NOW - 3 * HOUR), "end": "proof_weak", "sha": "a2bbb67"}
    _, pa = case9a("real", 1, [{"gen": 1, "at": iso(NOW - 5 * HOUR), "start": marker("A9_ITEM", 1)}, a9,
                               {"gen": 3, "at": iso(NOW - 4 * HOUR), "start": marker("A9_ITEM", 3)}, fin9, weak9,
                               {"gen": 5, "at": iso(NOW - 3 * HOUR), "start": marker("A9_ITEM", 5)}, b9,
                               {"gen": 7, "at": iso(NOW - 2 * HOUR), "start": marker("A9_ITEM", 7)}])
    ok(OW.CHURN_ITEM_PREFIX + "A9_ITEM" not in pa and pa["relentless.churn_items"].get("v") == 0,
       "9a: two account_lost change-overs and one proof_weak (the real instance) read no bouncing", pa.get(OW.CHURN_ITEM_PREFIX + "A9_ITEM"))
    _, pa2 = case9a("old", 3, [dict(a9), dict(b9)])
    ok(OW.CHURN_ITEM_PREFIX + "A9_ITEM" not in pa2 and pa2["relentless.churn_items"].get("v") == 0,
       "9a: an account_lost in the window does not wake old returns", pa2.get(OW.CHURN_ITEM_PREFIX + "A9_ITEM"))
    _, pa3 = case9a("real_same", 1, [a9, dict(weak9), dict(weak9, gen=5, at=iso(NOW - HOUR)), b9])
    said = (pa3.get(OW.CHURN_ITEM_PREFIX + "A9_ITEM") or {}).get("x", {}).get("said", "")
    ok("proof_weak failed it 2 times" in said and "account_lost" not in said,
       "9a: a real class repeating beside account_lost rows still reads bouncing, naming only the real class", said)
    s9a, _ = case9a("spend", 0, [{"gen": 1, "at": iso(NOW - 5 * HOUR), "start": marker("A9_ITEM", 1)}, a9])
    (s9a / ("spend-%s.json" % time.strftime("%Y%m%d", time.gmtime(NOW)))).write_text(json.dumps({"runs": {marker("A9_ITEM", 1): 1000}}))
    pa4 = OW.rl_churn(s9a, NOW, cfg9)
    ok(any("account_lost/work" in str(e) for e in pa4["relentless.returned_tokens_pct"].get("x", {}).get("by_end", [])),
       "9a: the tokens the account burnt stay in returned_tokens by_end", pa4["relentless.returned_tokens_pct"])
    # 9b OPS_CHURN_DIAGNOSE_REACH_DJVU_YHJL: REACH_GATE_HARDEN_PARENS_HIDE_THE_TOOL's real rows, read while gen 5 ran and
    # again after it finished: two account change-overs and nothing else. It rang the same 'account_lost failed it 2 times'.
    reach_rows = [{"gen": 1, "at": iso(NOW - 5 * HOUR), "start": marker("A9_ITEM", 1), "approach": "build"}, a9,
                  {"gen": 3, "at": iso(NOW - 4 * HOUR), "start": marker("A9_ITEM", 3), "approach": "build"}, b9,
                  {"gen": 5, "at": iso(NOW - 2 * HOUR), "start": marker("A9_ITEM", 5), "approach": "build"}]
    for tag, rows in (("reach_running", reach_rows),
                      ("reach_finished", reach_rows + [{"gen": 5, "at": iso(NOW - HOUR), "end": "finish", "sha": "bc2ca7e"}])):
        _, pb = case9a(tag, 0, rows)
        ok(OW.CHURN_ITEM_PREFIX + "A9_ITEM" not in pb and pb["relentless.churn_items"].get("v") == 0,
           "9b: REACH_GATE's two account change-overs read no bouncing (%s)" % tag, pb.get(OW.CHURN_ITEM_PREFIX + "A9_ITEM"))
    # 9c OPS_CHURN_DIAGNOSE_STAGER_PAYJ_FNOF: STAGER_SNAG_REWIRE_BUILDER_WOKEN_FOR_HARNESS's real rows, 16 minutes apart:
    # two different real defects the blind check caught, each fixed. This alarm is TRUE, not a miscount: it rings on the
    # candidate still in check, and only the blind PASS (or a landing) ends it.
    stager_rows = [{"gen": 1, "at": iso(NOW - 1.0 * HOUR), "start": marker("A9_ITEM", 1), "approach": "build"},
                   {"gen": 1, "at": iso(NOW - 0.9 * HOUR), "end": "finish", "sha": "07051af"},
                   {"gen": 1, "at": iso(NOW - 0.8 * HOUR), "end": "blind_fail", "approach_next": "build"},
                   {"gen": 3, "at": iso(NOW - 0.8 * HOUR), "start": marker("A9_ITEM", 3), "approach": "build"},
                   {"gen": 3, "at": iso(NOW - 0.7 * HOUR), "end": "finish", "sha": "937e677"},
                   {"gen": 3, "at": iso(NOW - 0.5 * HOUR), "end": "blind_fail", "approach_next": "redesign"},
                   {"gen": 5, "at": iso(NOW - 0.4 * HOUR), "start": marker("A9_ITEM", 5), "approach": "redesign"},
                   {"gen": 5, "at": iso(NOW - 0.2 * HOUR), "end": "finish", "sha": "0a5961f"}]
    s9c, pc = case9a("stager", 2, stager_rows)
    said = (pc.get(OW.CHURN_ITEM_PREFIX + "A9_ITEM") or {}).get("x", {}).get("said", "")
    ok("blind_fail failed it 2 times" in said and "returns" not in said,
       "9c: STAGER's two blind fails ring bouncing with its third candidate still in check", said)
    (s9c / "items" / "A9_ITEM" / "state.json").write_text(json.dumps(
        {"status": "game", "returns": 2, "gen": 5, "spent": 1, "check": {"verdict": "PASS", "verdict_at": NOW - 0.1 * HOUR}}))
    pc2 = OW.rl_churn(s9c, NOW, cfg9)
    ok(OW.CHURN_ITEM_PREFIX + "A9_ITEM" not in pc2 and pc2["relentless.churn_items"].get("v") == 0,
       "9c: the blind PASS after those fails ends the bounce", pc2.get(OW.CHURN_ITEM_PREFIX + "A9_ITEM"))
    # 9w OPS_CHURN_DIAGNOSE_OPS_GCNF_SOGA: OPS_METRONOME_MIGRATE_CLOCKS_FENCED cuts one clock a day by design and read
    # 'bouncing: 5 returns; waiting_for_sample failed it 5 times' off five `snag --wait-hours` endings (wait=true rows).
    # A wait is time, not work: no failed attempt, no bounce, and its gen's spend is no returned work. The same rows
    # without wait=true still read churn (the instrument can see).
    for waited in (True, False):
        sw = TMP / ("s9w_%s" % waited)
        nm = "W9_ITEM"
        d = sw / "items" / nm
        d.mkdir(parents=True)
        (d / "state.json").write_text(json.dumps({"status": "queued", "returns": 5, "gen": 6, "spent": 1}))
        rows = []
        for g in range(1, 6):
            t = NOW - (6 - g) * HOUR
            rows += [{"gen": g, "at": iso(t), "start": marker(nm, g)},
                     dict({"gen": g, "at": iso(t + 60), "end": "waiting_for_sample", "approach_next": "build"},
                          **({"wait": True} if waited else {}))]
        (d / "attempts.jsonl").write_text("".join(json.dumps(r) + "\n" for r in rows))
        day = time.strftime("%Y%m%d", time.gmtime(NOW))
        (sw / ("spend-%s.json" % day)).write_text(json.dumps({"spent": 500, "runs": {marker(nm, 5): 500}}))
        (TMP / "ops" / "alarms.json").write_text("{}")
        pw = OW.rl_churn(sw, NOW, cfg9)
        hit = OW.CHURN_ITEM_PREFIX + nm in pw
        ret = pw["relentless.returned_tokens_day"].get("v")
        if waited:
            ok(not hit and pw["relentless.churn_items"].get("v") == 0 and ret == 0,
               "9w: five wait=true endings are no churn and no returned tokens", (sorted(pw), ret))
            ok(not OW.attempt_failed(rows[1], ends) and OW.attempt_waited(rows[1]), "9w: a wait row is waited, not failed")
            ok(not OW.in_churn({"returns": 5}, [(NOW - 60, "harness")], NOW, cfg9, waits=4),
               "9w: one real failure plus four waits is 1 return, not a bounce")
        else:
            said = (pw.get(OW.CHURN_ITEM_PREFIX + nm) or {}).get("x", {}).get("said", "")
            ok(hit and "5 returns" in said and ret == 500, "9w: the same rows without wait=true still read churn",
               (said, ret))
    # 9s OPS_CHURN_DIAGNOSE_OPS_GCNF_SOGA, reopened 20:17Z: OPS_METRONOME_MIGRATE_CLOCKS_FENCED, its bounce cleared by 9w,
    # re-rang 'spend rising: 6.1M weighted, 4782k in the last 24h, nothing landed' off gens 19..25, each a planned
    # one-clock-a-day `snag --wait-hours` ending (wait=true) that cut and published its clock. A wait gen's spend is time,
    # not work, as its return is: it is no rising spend. The same spend on a gen whose last ending is no wait still reads
    # 'spend rising' (the instrument can see).
    cfg9s = dict(cfg9, item_bands=rules["relentless"]["item_bands"])
    for waited in (True, False):
        ss = TMP / ("s9s_%s" % waited)
        nm = "METRONOME_SHAPE_ITEM"
        d = ss / "items" / nm
        d.mkdir(parents=True)
        (d / "state.json").write_text(json.dumps({"status": "queued", "returns": 7, "gen": 26, "spent": 6072431,
                                                  "failures": {"waiting_for_sample": 7}}))
        rows, runs = [], {}
        for i, g in enumerate((19, 21, 23, 25)):
            t = NOW - (18 - 5 * i) * HOUR
            last = g == 25 and not waited
            rows += [{"gen": g, "at": iso(t), "start": marker(nm, g)},
                     dict({"gen": g, "at": iso(t + 600), "end": "harness" if last else "waiting_for_sample",
                           "approach_next": "build"}, **({} if last else {"wait": True}))]
            runs[marker(nm, g)] = 1195500
        (d / "attempts.jsonl").write_text("".join(json.dumps(r) + "\n" for r in rows))
        day = time.strftime("%Y%m%d", time.gmtime(NOW))
        (ss / ("spend-%s.json" % day)).write_text(json.dumps({"spent": sum(runs.values()), "runs": runs}))
        (TMP / "ops" / "alarms.json").write_text(json.dumps({OW.CHURN_ITEM_TAG + ":" + OW.CHURN_ITEM_PREFIX + nm: {}}))
        ps = OW.rl_churn(ss, NOW, cfg9s)
        got = ps.get(OW.CHURN_ITEM_PREFIX + nm) or {}
        said = (got.get("x") or {}).get("said", "")
        if waited:
            ok(got.get("v") == 0 and got.get("m") == "MEASURED" and "spend rising" not in said,
               "9s: four wait=true gens past the hot spent band are no rising spend; the held alarm reads 0", got)
        else:
            ok(got.get("v", 0) >= 1 and "spend rising" in said,
               "9s: the same spend with its last gen no wait still reads 'spend rising'", got)
    # 9n OPS_CHURN_DIAGNOSE_NIGHTLY_WHTT_GXBQ: NIGHTLY_SELFTESTS_DRAIN_THIRTEEN_RED_NIGHTS waits for two green nightlies
    # (one sweep a day) and read 'bouncing: 6 returns; wait_two_nights failed it 6 times', filed 11:38Z by the pre-9w
    # code: gen 1's ending predates the wait flag (no wait key, 34 h old, outside the window), gens 3..11 are five
    # wait=true endings, returns 6, its alarm held. Five waits off six returns is 1; the one real failure is out of the
    # window: the held alarm reads 0 and clears.
    sn = TMP / "s9n"
    nm = "NIGHTLY_SHAPE_ITEM"
    d = sn / "items" / nm
    d.mkdir(parents=True)
    (d / "state.json").write_text(json.dumps({"status": "queued", "returns": 6, "gen": 12, "spent": 3.9e6,
                                              "failures": {"wait_two_nights": 6}}))
    rows = [{"gen": 1, "at": iso(NOW - 35 * HOUR), "start": marker(nm, 1)},
            {"gen": 1, "at": iso(NOW - 34 * HOUR), "end": "wait_two_nights", "approach_next": "build"}]
    for i, g in enumerate((3, 5, 7, 9, 11)):
        t = NOW - (28 - 6 * i) * HOUR
        rows += [{"gen": g, "at": iso(t), "start": marker(nm, g)},
                 {"gen": g, "at": iso(t + 60), "end": "wait_two_nights", "approach_next": "build", "wait": True}]
    (d / "attempts.jsonl").write_text("".join(json.dumps(r) + "\n" for r in rows))
    day = time.strftime("%Y%m%d", time.gmtime(NOW))
    (sn / ("spend-%s.json" % day)).write_text(json.dumps({"spent": 700, "runs": {marker(nm, 11): 700}}))
    (TMP / "ops" / "alarms.json").write_text(json.dumps({OW.CHURN_ITEM_TAG + ":" + OW.CHURN_ITEM_PREFIX + nm: {}}))
    pn = OW.rl_churn(sn, NOW, cfg9)
    got = pn.get(OW.CHURN_ITEM_PREFIX + nm) or {}
    ok(got.get("v") == 0 and got.get("m") == "MEASURED" and pn["relentless.churn_items"].get("v") == 0,
       "9n: one legacy unflagged wait plus five wait=true endings, alarm held, reads 0 (clears)", got)
    # 9g OPS_CHURN_DIAGNOSE_PACK_HMAO_RAYY: PACK_ANIMALS_RESTORE_EMPTY_SADDLES read 'game_fail failed it 2 times' off ONE
    # A5 fail: relentless_attrib.withhold writes a `gated` row (withheld until attributed: no strike, no return) and the
    # attribution writes the real row for the same gen. The gated row is no failed attempt. Without `gated` the same two
    # rows still count twice (the instrument can see).
    for gated in (True, False):
        sg = TMP / ("s9g_%s" % gated)
        nm = "G9_ITEM"
        d = sg / "items" / nm
        d.mkdir(parents=True)
        (d / "state.json").write_text(json.dumps({"status": "queued", "returns": 1, "gen": 5, "spent": 1}))
        t = NOW - HOUR
        rows = [{"gen": 4, "at": iso(t), "start": marker(nm, 4)},
                dict({"gen": 4, "at": iso(t + 60), "end": "game_fail", "sha": "a" * 40},
                     **({"gated": "attribution"} if gated else {})),
                {"gen": 4, "at": iso(t + 600), "end": "game_fail", "approach_next": "build"}]
        (d / "attempts.jsonl").write_text("".join(json.dumps(r) + "\n" for r in rows))
        (TMP / "ops" / "alarms.json").write_text("{}")
        pg = OW.rl_churn(sg, NOW, cfg9)
        said = (pg.get(OW.CHURN_ITEM_PREFIX + nm) or {}).get("x", {}).get("said", "")
        if gated:
            ok(OW.CHURN_ITEM_PREFIX + nm not in pg and not OW.attempt_failed(rows[1], ends),
               "9g: a gated (withheld) row plus its attributed row is one game_fail, no churn", (sorted(pg), said))
        else:
            ok("game_fail failed it 2 times" in said, "9g: the same rows without gated still count twice", said)
    # 9f OPS_CHURN_DIAGNOSE_WARSCAR_WWRK_FJER: WARSCAR_HOSPICE_DESERTERS_1 read 'spend rising: 11.8M weighted, 944k ...,
    # nothing landed' at 21:39Z while its gen 3 (a proof repair, `finish` at 21:19Z) sat in its blind check. A gen whose
    # last ending is finish landed: its spend is no rising spend. The same spend with a later failed ending for that gen
    # (the check sent it back) still reads 'spend rising' (the instrument can see).
    for landed in (True, False):
        sf = TMP / ("s9f_%s" % landed)
        nm = "WARSCAR_SHAPE_ITEM"
        d = sf / "items" / nm
        d.mkdir(parents=True)
        (d / "state.json").write_text(json.dumps({"status": "checking", "returns": 0, "gen": 3, "spent": 11.8e6}))
        t = NOW - 2 * HOUR
        rows = [{"gen": 3, "at": iso(t), "start": marker(nm, 3)},
                {"gen": 3, "at": iso(t + 600), "end": "finish", "sha": "d" * 40}]
        if not landed:
            rows.append({"gen": 3, "at": iso(t + 1800), "end": "check_fail", "approach_next": "build"})
        (d / "attempts.jsonl").write_text("".join(json.dumps(r) + "\n" for r in rows))
        day = time.strftime("%Y%m%d", time.gmtime(NOW))
        (sf / ("spend-%s.json" % day)).write_text(json.dumps({"spent": 944000, "runs": {marker(nm, 3): 944000}}))
        (TMP / "ops" / "alarms.json").write_text(json.dumps({OW.CHURN_ITEM_TAG + ":" + OW.CHURN_ITEM_PREFIX + nm: {}}))
        pf = OW.rl_churn(sf, NOW, cfg9s)
        got = pf.get(OW.CHURN_ITEM_PREFIX + nm) or {}
        said = (got.get("x") or {}).get("said", "")
        if landed:
            ok(got.get("v") == 0 and got.get("m") == "MEASURED" and "spend rising" not in said,
               "9f: a finished gen in its check, past the hot spent band, is no rising spend; the held alarm reads 0", got)
        else:
            ok("spend rising" in said, "9f: the same gen sent back by its check still reads 'spend rising'", got)
    # 9u OPS_CHURN_DIAGNOSE_NIGHTLY_ZNGK_SBPI: NIGHTLY_COP_FIX_RED_AQJSGV_CFVH rang 'unmeasured failed it 2 times' off ONE
    # candidate (ec3e5f14) the Judge could not reach, checked blind, reach-repaired, checked blind again, then sent back
    # (proof_owed). One candidate blind twice is the reach repair's churn, not the item's: it counts once. The same rows
    # with the second blind check at a NEW sha still count twice (the instrument can see).
    for same in (True, False):
        su = TMP / ("s9u_%s" % same)
        nm = "U9_ITEM"
        d = su / "items" / nm
        d.mkdir(parents=True)
        (d / "state.json").write_text(json.dumps({"status": "queued", "returns": 1, "gen": 1, "spent": 1}))
        t = NOW - 3 * HOUR
        a, b = "e" * 40, ("e" if same else "f") * 40
        rows = [{"gen": 1, "at": iso(t), "start": marker(nm, 1)},
                {"gen": 1, "at": iso(t + 60), "end": "finish", "sha": a},
                {"gen": 1, "at": iso(t + 600), "end": "unmeasured", "said": "UNMEASURED", "sha": a},
                {"gen": 1, "at": iso(t + 3600), "end": "reach_waiter_released", "sha": a},
                {"gen": 1, "at": iso(t + 4000), "end": "unmeasured", "said": "UNMEASURED", "sha": b},
                {"gen": 1, "at": iso(t + 7000), "end": "proof_owed", "sha": b}]
        (d / "attempts.jsonl").write_text("".join(json.dumps(r) + "\n" for r in rows))
        (TMP / "ops" / "alarms.json").write_text("{}")
        pu = OW.rl_churn(su, NOW, cfg9)
        said = (pu.get(OW.CHURN_ITEM_PREFIX + nm) or {}).get("x", {}).get("said", "")
        if same:
            ok(OW.CHURN_ITEM_PREFIX + nm not in pu and pu["relentless.churn_items"].get("v") == 0,
               "9u: one candidate checked blind twice (a reach repair between) is one unmeasured, no churn", (sorted(pu), said))
        else:
            ok("unmeasured failed it 2 times" in said, "9u: blind checks of two different candidates still count twice", said)
    shutil.rmtree(TMP, ignore_errors=True)
    print("%d failed" % len(FAILS) if FAILS else "ALL PASS")
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
