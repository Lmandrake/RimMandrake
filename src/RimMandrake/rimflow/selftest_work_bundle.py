#!/usr/bin/env python3
"""selftest_work_bundle.py - work bundles (work_bundle.py and its hooks in the two pipelines).

Item RIMMANDRAKE_BATCH_ONE_MODS_OPEN_WORK_INTO_ONE_RUN_PIPELINE_SPLITS_PER_TICKET; page
design/specs/2026-11-24-work-bundles/boundary.md (each t_ function is one promise of it, by name). Offline: fake items,
injected runners and a throwaway store; nothing launches, closes or publishes. Written before the code of each part and
seen failing on the base (work_bundle.py absent).
"""
import json
import os
import sys
import tempfile
import time
import types

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
for _p in (HERE, os.path.join(REPO, "src", "RimMandrake", "Utils")):
    if _p not in sys.path:
        sys.path.insert(0, _p)
sys.dont_write_bytecode = True
os.environ["RM_UNDER_SELFTEST"] = "1"
TMP = tempfile.mkdtemp(prefix="selftest_work_bundle_")
os.environ["RM_WORK_BUNDLE_DIR"] = os.path.join(TMP, "store")
FAILS = []


def chk(fn, what):
    try:
        cond = fn()
    except Exception as e:  # noqa: BLE001
        cond, what = False, "%s (raised %s: %s)" % (what, type(e).__name__, str(e)[:300])
    print(("ok   " if cond else "FAIL ") + what)
    if not cond:
        FAILS.append(what)


def WB():
    import work_bundle
    return work_bundle


def item(iid, state="proposed", effect=None, home=None, title=None, **kw):
    x = types.SimpleNamespace(id=iid, state=state, effect=effect, title=title or iid.lower(),
                              home={"home": home, "group": "g", "flag": "LOOKS CURRENT"} if home else None,
                              blocked=False, blocked_reason=None, blocked_on=None, blocked_also=(), wait_until=None,
                              wait_reason=None, lease=None, owner=None, history=[], caused_by=None)
    for k, v in kw.items():
        setattr(x, k, v)
    return x


# ---- part 1: the reality sort ---------------------------------------------------------------------------------------

def t_sort_runs_each_members_test_and_closes_only_green():
    W = WB()
    items = {"A_FIXED": item("A_FIXED", effect="cmd:exit-0-check"),
             "B_REAL": item("B_REAL", effect="cmd:exit-1-check"),
             "C_SCRIPT": item("C_SCRIPT", created_at="2026-11-20T00:00:00Z"),
             "D_NONE": item("D_NONE"),
             "E_BLIND": item("E_BLIND", effect="cmd:exit-2-check"),
             "F_SCRIPT_RED": item("F_SCRIPT_RED")}
    prose = {"C_SCRIPT": "## verify\npython3 src/RimMandrake/rimflow/acceptance/c_accept.py\n",
             "F_SCRIPT_RED": "## criteria\n- python3 src/RimMandrake/rimflow/selftest_f.py passes\n",
             "D_NONE": "## verify\nlook at it in game\n"}
    ran = []

    def run_effect(text, root):
        ran.append(text)
        return {"cmd:exit-0-check": ("holds", "ok"), "cmd:exit-1-check": ("fails", "red"),
                "cmd:exit-2-check": ("unmeasured", "exit 2")}[text]

    def run_script(path, root):
        ran.append(path)
        return ("holds", "") if "c_accept" in path else ("fails", "FAIL 1")
    exists = lambda p: True  # noqa: E731
    rows = W.sort(list(items), items, lambda i: prose.get(i, ""), run_effect, run_script, root=REPO, exists=exists,
                  added_at=lambda p: W._ts("2026-11-20T00:10:00Z"))
    by = {r["id"]: r for r in rows}
    chk(lambda: by["A_FIXED"]["verdict"] == "holds" and by["C_SCRIPT"]["verdict"] == "holds",
        "sort: a green outcome check and a green named script read holds")
    chk(lambda: by["B_REAL"]["verdict"] == "fails" and by["F_SCRIPT_RED"]["verdict"] == "fails",
        "sort: a red check and a red named script read fails")
    chk(lambda: by["D_NONE"]["verdict"] == "no_test" and "D_NONE" not in str(ran),
        "sort: a ticket with no runnable test reads no_test and nothing runs for it")
    chk(lambda: by["E_BLIND"]["verdict"] == "unmeasured" and by["E_BLIND"]["why"],
        "sort: a check that exits 2 reads unmeasured, with why")
    chk(lambda: len(ran) == 5, "sort: each test runs once (%d runs)" % len(ran))
    closed = []
    out = W.sort_apply(rows, "abc1234", lambda iid, sha, ev: (closed.append((iid, sha, ev)), (0, "closed"))[1])
    chk(lambda: sorted(c[0] for c in closed) == ["A_FIXED", "C_SCRIPT"],
        "sort apply: only the green members close (%s)" % [c[0] for c in closed])
    chk(lambda: all(c[1] == "abc1234" and "abc1234" in c[2] for c in closed),
        "sort apply: the close names the commit the test ran on, in --sha and in the evidence")
    import inspect
    src = inspect.getsource(W.close_member)
    chk(lambda: '"--no-code"' in src and '"--sha"' not in src,
        "sort close: --no-code names the build (a ledger-only build is refused as --sha; measured 2026-11-24)")
    refused = W.sort_apply([{"id": "G", "verdict": "holds", "test": "cmd:x", "why": ""}], "abc1234",
                           lambda *a: (2, "close: G has not earned its close: guard this fix died 1 time(s)"))
    chk(lambda: not refused[0]["closed"] and "guard this fix died" in refused[0]["act"],
        "sort apply: a close a ticket's gate refuses is kept and reported with the gate's words")
    chk(lambda: {r["id"]: r["act"] for r in out}["D_NONE"] == "listed no test",
        "sort apply: a no-test member is listed `no test`, never closed")
    # a vacuous check is never green
    rows2 = W.sort(["V"], {"V": item("V", effect="cmd:true")}, lambda i: "", run_effect, run_script, root=REPO)
    chk(lambda: rows2[0]["verdict"] == "unmeasured", "sort: a vacuous check (cmd:true) reads unmeasured, not holds")
    # a test path that does not exist is no test
    rows3 = W.sort(["N"], {"N": item("N")}, lambda i: "## verify\npython3 src/nope/x_accept.py\n", run_effect,
                   run_script, root=REPO, exists=lambda p: False)
    chk(lambda: rows3[0]["verdict"] == "no_test", "sort: a named script that does not exist is no test")
    # measured 2026-11-24 on RIMMANDRAKE_KILL_LIVE_HOLDER_RESUME_AFTER_FIRST_SESSION: its verify reads "Acceptance test:
    # none, a live systemd run (its offline twin is `python3 .../selftest_holder_resume.py`, ALL PASS)"
    none = "## verify\nAcceptance test: none, a live run (its offline twin is `python3 src/x/selftest_y.py`, ALL PASS).\n"
    rows4 = W.sort(["K"], {"K": item("K")}, lambda i: none, run_effect, run_script, root=REPO, exists=exists)
    chk(lambda: rows4[0]["verdict"] == "no_test", "sort: `Acceptance test: none` is no test, whatever script it names")
    # a named script that was there before the ticket was filed, and passes, was never seen failing on it
    old = {"O": item("O", created_at="2026-11-20T00:00:00Z")}
    rows5 = W.sort(["O"], old, lambda i: "## verify\npython3 src/a/c_accept.py\n", run_effect, run_script, root=REPO,
                   exists=exists, added_at=lambda p: W._ts("2026-11-01T00:00:00Z"))
    chk(lambda: rows5[0]["verdict"] == "holds_unproven", "sort: a green script older than the ticket reads holds_unproven")
    out5 = W.sort_apply(rows5, "abc1234", lambda *a: closed.append(a) or (0, ""))
    chk(lambda: not out5[0].get("closed") and "never seen failing" in out5[0]["act"],
        "sort apply: holds_unproven is kept for the worker, never closed (%s)" % out5[0]["act"])
    rows6 = W.sort(["O"], old, lambda i: "## verify\npython3 src/a/c_accept.py\n", run_effect, run_script, root=REPO,
                   exists=exists, added_at=lambda p: W._ts("2026-11-20T00:30:00Z"))
    chk(lambda: rows6[0]["verdict"] == "holds", "sort: a green script added with the ticket reads holds")


def t_sort_dry_closes_nothing():
    W = WB()
    rows = [{"id": "A", "verdict": "holds", "test": "cmd:x", "why": "ok"}]
    closed = []
    out = W.sort_apply(rows, "abc1234", lambda *a: closed.append(a) or (0, ""), dry=True)
    chk(lambda: not closed and out[0]["act"].startswith("would close"), "sort --dry: closes nothing, says would close")


def t_members_are_one_system():
    W = WB()
    items = {"P1_LEDGER": item("P1_LEDGER", home="pipeline:ledger"),
             "P2_LEDGER": item("P2_LEDGER", home="pipeline:ledger"),
             "Q_BRIDGE": item("Q_BRIDGE", home="pipeline:bridge"),
             "M_FLOW": item("M_FLOW", home="mod:FlowWorks"),
             "N_NOHOME": item("N_NOHOME"),
             "Z_DONE": item("Z_DONE", state="done", home="pipeline:ledger")}
    mods = {"FlowWorks", "Pyrelands"}
    reading = lambda it: {"mod": "FlowWorks" if it.id == "M_FLOW" else None, "unreadable": None}  # noqa: E731
    sysname, ids, why = W.resolve("pipeline:ledger", items, mods, reading)
    chk(lambda: sysname == "pipeline:ledger" and ids == ["P1_LEDGER", "P2_LEDGER"],
        "resolve: a home takes its open tickets (%s %s %s)" % (sysname, ids, why))
    sysname, ids, why = W.resolve("FlowWorks", items, mods, reading)
    chk(lambda: sysname == "mod:FlowWorks" and ids == ["M_FLOW"], "resolve: a mod name takes the mod's tickets")
    sysname, ids, why = W.resolve(["P1_LEDGER", "Q_BRIDGE"], items, mods, reading)
    chk(lambda: sysname is None and "pipeline:ledger" in why and "pipeline:bridge" in why,
        "resolve: ids of two systems are refused, naming each system (%s)" % why)
    sysname, ids, why = W.resolve(["N_NOHOME"], items, mods, reading)
    chk(lambda: sysname == "item:N_NOHOME" and ids == ["N_NOHOME"], "resolve: a ticket with no home is item:<ID>")
    chk(lambda: W.system_of(items["M_FLOW"], reading) == "mod:FlowWorks",
        "system_of: a mod ticket's system is mod:<Mod>")


# ---- part 2: the record and the launcher ----------------------------------------------------------------------------

NOW = 1795600000.0


def t_ready_members_only():
    W = WB()
    items = {"OK": item("OK"),
             "LEASED": item("LEASED", state="doing", lease={"expires": "2099-01-01T00:00:00Z"}),
             "WAITS": item("WAITS", wait_until="2099-01-01T00:00:00Z", wait_reason="the owner's look"),
             "BLOCKED": item("BLOCKED", blocked=True, blocked_reason="needs X"),
             "REFUSED": item("REFUSED"), "HELD": item("HELD"),
             "PASSED_WAIT": item("PASSED_WAIT", wait_until="2020-01-01T00:00:00Z")}
    got = W.ready_split(list(items), items, NOW, refused=lambda i: "BUNDLE REFUSED: no way to prove it" if i == "REFUSED"
                        else None, held=lambda i: "HELD BY OWNER: X" if i == "HELD" else None,
                        leased=lambda it: it.id == "LEASED")
    ready, out = got
    chk(lambda: sorted(ready) == ["OK", "PASSED_WAIT"], "ready: only the free members are taken (%s)" % ready)
    chk(lambda: set(out) == {"LEASED", "WAITS", "BLOCKED", "REFUSED", "HELD"} and all(out.values()),
        "ready: each member left out is listed with its reason (%s)" % sorted(out))
    chk(lambda: "the owner's look" in out["WAITS"] and "no way to prove it" in out["REFUSED"],
        "ready: the reason quotes the wait and the refusal")
    evs = [{"id": "R1", "event": "file", "ts": "2026-11-20T00:00:00Z"},
           {"id": "R1", "event": "note", "ts": "2026-11-21T00:00:00Z", "text": "REFUSED BY BUNDLE: not this system"},
           {"id": "R2", "event": "note", "ts": "2026-11-21T00:00:00Z", "text": "BUNDLE REFUSED: cannot prove it"},
           {"id": "R2", "event": "home", "ts": "2026-11-22T00:00:00Z"},
           {"id": "R3", "event": "note", "ts": "2026-11-21T00:00:00Z", "text": "PROGRESS: x"}]
    rf = W.refusals(evs)
    chk(lambda: rf.get("R1") == "REFUSED BY BUNDLE: not this system" and "R2" not in rf and "R3" not in rf,
        "ready: a refusal stands until a later non-note event on the ticket (%s)" % rf)


def fake_launch(log, unit="rm-detached-bench-x-1"):
    def go(rec, brief):
        log.append((rec["id"], rec.get("state"), brief))
        return 0, "DETACHED %s" % unit, unit
    return go


def t_one_live_bundle_per_system():
    W = WB()
    items = {"A1": item("A1", home="pipeline:ledger", effect="cmd:x"), "A2": item("A2", home="pipeline:ledger")}
    log = []
    rc, rec = W.launch_bundle("pipeline:ledger", ["A1", "A2"], items, "a test", "workshop", now=NOW,
                              launcher=fake_launch(log))
    chk(lambda: rc == 0 and rec["state"] == "live" and rec["units"][0]["unit"] == "rm-detached-bench-x-1",
        "launch: a first bundle of a system launches (%s %s)" % (rc, rec.get("state")))
    rc2, why = W.launch_bundle("pipeline:ledger", ["A2"], items, "again", "workshop", now=NOW + 5,
                               launcher=fake_launch(log))
    chk(lambda: rc2 == 2 and rec["id"] in str(why) and len(log) == 1,
        "launch: a second bundle of a live system is refused, naming the live one (%s)" % why)
    W.store_write(dict(rec, state="ended"))
    rc3, rec3 = W.launch_bundle("pipeline:ledger", ["A2"], items, "after", "workshop", now=NOW + 60,
                                launcher=fake_launch(log, "rm-detached-bench-x-2"))
    chk(lambda: rc3 == 0 and rec3["id"] != rec["id"], "launch: after the bundle ended, the next one launches")
    W.store_write(dict(rec3, state="ended"))


def t_the_record_is_written_at_launch():
    W = WB()
    items = {"B1": item("B1", home="pipeline:judges"), "B2": item("B2", home="pipeline:judges")}
    seen = []

    def launcher(rec, brief):
        seen.append(W.store_read(rec["id"]))       # the record is on disk before the run starts
        return 0, "DETACHED u-9", "u-9"
    rc, rec = W.launch_bundle("pipeline:judges", ["B1", "B2"], items, "why", "workshop", now=NOW, launcher=launcher)
    on = W.store_read(rec["id"])
    chk(lambda: seen and seen[0] and seen[0]["members"] == ["B1", "B2"] and seen[0]["state"] == "launching",
        "record: written with its members before the run starts")
    chk(lambda: on["state"] == "live" and on["lead"] == "B1" and on["system"] == "pipeline:judges" and on["why"] == "why"
        and on["state_file"].startswith("infrastructure/bundles/") and on["units"][0]["unit"] == "u-9",
        "record: system, lead, why, state file and unit after the launch")
    W.store_write(dict(on, state="ended"))
    rc, bad = W.launch_bundle("pipeline:judges", ["B1"], items, "why", "workshop", now=NOW + 9,
                              launcher=lambda rec, brief: (1, "refused: pool full", None))
    on = W.store_read(bad["id"])
    chk(lambda: rc == 1 and on["state"] == "launch_failed" and "pool full" in on["launch_out"],
        "record: a launch that started nothing reads launch_failed with its output")
    chk(lambda: W.live_bundles() == {} or "pipeline:judges" not in W.live_bundles(),
        "record: a launch_failed bundle is not live")


def t_the_brief_names_every_member_and_the_role():
    W = WB()
    items = {"C1": item("C1", title="first thing", effect="cmd:python3 x_accept.py"), "C2": item("C2", title="second")}
    rec = W.new_record("pipeline:docs", ["C1", "C2"], "why", "workshop", NOW)
    b = W.brief(rec, items, {"C1": "cmd:python3 x_accept.py", "C2": None})
    chk(lambda: all(s in b for s in ("C1", "C2", "first thing", "second", "cmd:python3 x_accept.py",
                                     "roles/bundle_worker.md", rec["state_file"], rec["id"])),
        "brief: names each member, title, test, the role file, the state file and the bundle id")
    chk(lambda: "no test" in b, "brief: a member with no test says so")
    import re
    chk(lambda: not re.search(r"(?i)\b(usd|spend|budget|remainder)\b|\$\d|\bcap\b", b),
        "brief: states no spend, cap or remainder")


def t_the_lane_launches_one_bundle_per_system():
    W = WB()
    rows = [{"item": "L1", "decision": "launch", "model": "opus", "cap": 120, "run_n": 1},
            {"item": "L2", "decision": "launch", "model": "sonnet", "cap": 50, "run_n": 1},
            {"item": "L3", "decision": "slots_full", "why": "full"},
            {"item": "M1", "decision": "launch", "model": "opus", "cap": 120, "run_n": 1},
            {"item": "N1", "decision": "launch", "model": "opus", "cap": 120, "run_n": 1},
            {"item": "S1", "decision": "launch", "kind": "shape", "model": "opus", "cap": 120},
            {"item": "Q1", "decision": "launch", "model": "opus", "cap": 120, "run_n": 1},
            {"item": "H1", "decision": "launch", "model": "opus", "cap": 120, "run_n": 1, "host": "SteveDesktop"}]
    launches = ["L1", "L2", "M1", "N1", "S1", "Q1", "H1"]
    systems = {"L1": "pipeline:ledger", "L2": "pipeline:ledger", "L3": "pipeline:ledger", "M1": "pipeline:bridge",
               "N1": "item:N1", "S1": "pipeline:ledger", "Q1": "pipeline:docs", "H1": "pipeline:hooks"}
    live = {"pipeline:docs": "WB-pipeline-docs-1"}
    rows2, launches2 = W.group(rows, launches, systems, live)
    by = {r["item"]: r for r in rows2}
    chk(lambda: by["L1"]["decision"] == "launch" and by["L1"]["bundle"]["members"] == ["L1", "L2", "L3"],
        "group: the first launch row of a system leads, with every ready row of it (%s)" % by["L1"].get("bundle"))
    chk(lambda: by["L2"]["decision"] == "bundled" and by["L3"]["decision"] == "bundled" and "L1" in by["L2"]["why"],
        "group: the other launch rows and a slots_full row of the system read bundled, naming the lead")
    chk(lambda: by["M1"]["decision"] == "launch" and by["M1"]["bundle"]["members"] == ["M1"]
        and by["N1"]["bundle"]["system"] == "item:N1", "group: one bundle per system; a no-home ticket is a bundle of one")
    chk(lambda: by["S1"]["decision"] == "launch" and "bundle" not in by["S1"], "group: a Shape run is not bundled")
    chk(lambda: by["Q1"]["decision"] == "bundle_live" and "WB-pipeline-docs-1" in by["Q1"]["why"],
        "group: a ready row of a system with a live bundle reads bundle_live, naming it")
    chk(lambda: by["H1"]["decision"] == "slots_full" and "this machine" in by["H1"]["why"],
        "group: a bundle whose only room is another host waits for a local slot")
    chk(lambda: sorted(launches2) == ["L1", "M1", "N1", "S1"], "group: the launches are the leads and the Shape run")
    # in the lane tick: a member of a live bundle reads in_bundle and launches nothing
    import list_dispatch as LD
    facts = {"items": {"X": {"state": "proposed", "effect": "cmd:x", "verdict": "fails", "events": 1, "out": "red"}},
             "runs": {"X": {"live": [], "ended": [], "bundle": "WB-pipeline-ledger-1"}}, "recent": None}
    rws, ln = LD.decide({"enabled": True, "max_live": 2}, {}, facts, NOW)
    chk(lambda: rws[0]["decision"] == "in_bundle" and "WB-pipeline-ledger-1" in rws[0]["why"] and not ln,
        "lane: a member of a live bundle reads in_bundle and launches nothing (%s)" % rws[0])
    over = W.overlay({"Y": {"live": [], "ended": []}}, ["Y", "Z"],
                     {"WB-1": {"id": "WB-1", "state": "live", "members": ["Y", "Z"], "units": [{"unit": "u1"}]}},
                     live=lambda u: True)
    chk(lambda: over["Y"]["bundle"] == "WB-1" and over["Z"]["bundle"] == "WB-1",
        "overlay: every member of a live bundle carries its id")
    over2 = W.overlay({}, ["Y"], {"WB-1": {"id": "WB-1", "state": "ended", "members": ["Y"], "units": [{"unit": "u1"}]}},
                      live=lambda u: False)
    chk(lambda: "bundle" not in over2["Y"] and over2["Y"]["ended"] == ["u1"],
        "overlay: an ended bundle's units read ended on each member, so its own run count goes on")


# ---- part 3: the worker's context guard -----------------------------------------------------------------------------

def t_context_reads_the_own_session():
    W = WB()
    d = os.path.join(TMP, "ctx")
    os.makedirs(d, exist_ok=True)
    tr = os.path.join(d, "s.jsonl")
    with open(tr, "w") as f:
        f.write(json.dumps({"message": {"model": "claude-opus-5-5", "usage": {"input_tokens": 10,
                            "cache_read_input_tokens": 600000, "cache_creation_input_tokens": 0, "output_tokens": 5}}}) + "\n")
        f.write(json.dumps({"isSidechain": True, "message": {"model": "claude-opus-5-5", "usage": {"input_tokens": 1}}}) + "\n")
    outs = os.path.join(d, "runs")
    os.makedirs(outs, exist_ok=True)
    with open(os.path.join(outs, "a.out.json"), "w") as f:
        f.write('{"modelUsage":{"claude-opus-5-5":{"contextWindow":1000000,"canonicalModel":"claude-opus-5-5"}}}')
    r = W.context_reading(tr, outs)
    chk(lambda: r["tokens"] == 600015 and r["window"] == 1000000 and r["verdict"] == "SAVE AND RESTART",
        "context: over half of a measured window reads SAVE AND RESTART (%s)" % r)
    with open(tr, "a") as f:
        f.write(json.dumps({"message": {"model": "claude-opus-5-5", "usage": {"input_tokens": 200000}}}) + "\n")
    chk(lambda: W.context_reading(tr, outs)["verdict"] == "GO ON", "context: under half reads GO ON")
    r2 = W.context_reading(tr, os.path.join(d, "empty"))
    chk(lambda: r2["verdict"] == "UNMEASURED" and r2["window"] is None and r2["why"],
        "context: no window on record reads UNMEASURED with its cause, never a guessed window (%s)" % r2)
    r3 = W.context_reading(os.path.join(d, "none.jsonl"), outs)
    chk(lambda: r3["verdict"] == "UNMEASURED" and r3["tokens"] is None, "context: no transcript reads UNMEASURED")


def t_each_limit_names_its_danger():
    import re
    src = open(os.path.join(HERE, "work_bundle.py"), encoding="utf-8").read().splitlines()
    bad = []
    for n, line in enumerate(src):
        if re.match(r"^[A-Z][A-Z0-9_]*(?:_S|_MAX|_TOKENS|_MOST|_FRACTION)\s*=\s*[0-9]", line):
            near = " ".join(src[max(0, n - 4): n + 1])
            if "danger=" not in near and "class=" not in near:
                bad.append(line.strip())
    chk(lambda: not bad, "each number in work_bundle.py names its danger or its class (%s)" % bad)


def main():
    for t in [t_sort_runs_each_members_test_and_closes_only_green, t_sort_dry_closes_nothing, t_members_are_one_system,
              t_ready_members_only, t_one_live_bundle_per_system, t_the_record_is_written_at_launch,
              t_the_brief_names_every_member_and_the_role, t_the_lane_launches_one_bundle_per_system,
              t_context_reads_the_own_session,
              t_each_limit_names_its_danger]:
        print("-- %s" % t.__name__)
        try:
            t()
        except Exception as e:  # noqa: BLE001
            FAILS.append("%s raised %s: %s" % (t.__name__, type(e).__name__, e))
            print("FAIL %s raised %s: %s" % (t.__name__, type(e).__name__, e))
    print("selftest_work_bundle: %s (%d failed)" % ("FAIL" if FAILS else "PASS", len(FAILS)))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
