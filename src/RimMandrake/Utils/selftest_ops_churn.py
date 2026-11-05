#!/usr/bin/env python3
"""selftest_ops_churn.py — OPS_CHURN_MEASURE_RETURNS_ARE_NOT_PROGRESS: Operations sees churn and owns its alarms.

On 2026-11-04 47 Relentless items had churned (one at gen 20, ~157M weighted tokens) on broken tests read as broken work,
and no reading said so. Each check fails on the code before the change:

1. rl_churn counts an item in churn by returns OR a repeated failure class, only with a failure inside the window; a
   blocked row or a finish is not a failure.
2. rl_churn's returned tokens: spend runs whose (item, gen) failed, placed in time by the gen's start row. x.by_end splits
   that spend by the gen's failed ending and lane, so an alarm reads its shared cause off the point. 2b: a gen is
   returned only when its LAST ending (a gen-less `done` row belongs to the gen open when it was written) is a failure.
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
   and run_alarms files it.

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
    cfg8 = dict(CFG, item_bands=rules["relentless"]["item_bands"], churn_item_stuck_stages=["game", "checking"],
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
    ok("PARKED_ITEM" not in ci, "8: a gen that started and ended before the window is no spend in it (a parked item)",
       ci.get("PARKED_ITEM"))
    ok("PUT_DOWN_ITEM" not in ci, "8: a blocked item's window spend is flat, not 'spend rising'", ci.get("PUT_DOWN_ITEM"))
    ok(ci.get("OLDGEN_ITEM", {}).get("v") == 1, "8: a gen started before the window that still burns is rising spend", ci.get("OLDGEN_ITEM"))
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
    shutil.rmtree(TMP, ignore_errors=True)
    print("%d failed" % len(FAILS) if FAILS else "ALL PASS")
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
