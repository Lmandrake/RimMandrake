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
os.environ["RM_DISPATCHER_STATE"] = os.path.join(TMP, "dispatcher")     # run records and the Conductor log stay here
os.environ["RM_CONDUCTOR_LOG"] = os.path.join(TMP, "conductor.log")
os.makedirs(os.path.join(TMP, "dispatcher", "detached"), exist_ok=True)
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
    # a qualifier before the colon is still a refusal (the bundle of 2026-11-25 wrote "(the L4 level only)" four times
    # and was relaunched for members that each held their reason)
    q = "REFUSED BY BUNDLE (the L4 level only): A1 passes at L2; L4 is the owner level"
    rq = W.refusals([{"id": "Q1", "event": "note", "ts": "2026-11-21T00:00:00Z", "text": q}])
    chk(lambda: rq.get("Q1") == q and W.is_refusal(q) and W.is_refusal("bundle refused - x: y")
        and not W.is_refusal("REFUSED BY BUNDLER: x") and not W.is_refusal("PROGRESS: REFUSED BY BUNDLE: x"),
        "ready: a qualified refusal head is read as a refusal (%s)" % rq)
    chk(lambda: "is_refusal(" in W.READ_MEMBERS, "ready: the clone's member read uses the same refusal test")


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

    def boom(rec, brief):
        raise TimeoutError("the launch hung past its guard")
    try:
        W.launch_bundle("pipeline:art-pipeline", ["B3"], {"B3": item("B3")}, "why", "workshop", now=NOW + 20, launcher=boom)
    except TimeoutError:
        pass
    chk(lambda: "pipeline:art-pipeline" not in W.live_bundles(),
        "record: a launcher that raises leaves no live bundle behind, so the system is not blocked for good (%s)"
        % W.live_bundles())


def t_the_brief_names_every_member_and_the_role():
    W = WB()
    items = {"C1": item("C1", title="first thing", effect="cmd:python3 x_accept.py"), "C2": item("C2", title="second")}
    rec = W.new_record("pipeline:docs", ["C1", "C2"], "why", "workshop", NOW)
    b = W.brief(rec, items, {"C1": "cmd:python3 x_accept.py", "C2": None})
    chk(lambda: all(s in b for s in ("C1", "C2", "first thing", "second", "cmd:python3 x_accept.py",
                                     "roles/builder.md", rec["state_file"], rec["id"])),
        "brief: names each member, title, test, the role file, the state file and the bundle id")
    chk(lambda: "no test" in b, "brief: a member with no test says so")
    import re
    chk(lambda: not re.search(r"(?i)\b(usd|spend|budget|remainder)\b|\$\d|\bcap\b", b),
        "brief: states no spend, cap or remainder")


def t_the_brief_carries_the_polish_of_its_files():
    W = WB()
    root = tempfile.mkdtemp(prefix="wb-polish-")
    pol = os.path.join(root, "design", "concepts", "FlowWorks", "version", "polish.md")
    os.makedirs(os.path.dirname(pol))
    with open(pol, "w") as f:
        f.write("# Polish\n\n- `pump.py` reads the depth twice.\n- `valve.cs` logs one line too many.\n")
    items = {"C1": item("C1", title="first thing")}
    rec = W.new_record("mod:FlowWorks", ["C1"], "why", "workshop", NOW)
    b = W.brief(rec, items, {"C1": None}, root=root)
    chk(lambda: W.POLISH_RULE in b and "design/concepts/FlowWorks/version/polish.md" in b
        and "`pump.py` reads the depth twice." in b and "`valve.cs` logs one line too many." in b,
        "brief: a mod bundle carries the polish rule and the open lines of the mod's polish.md")
    note = W.holder_note(rec, items, {"C1": None}, root=root)
    chk(lambda: W.POLISH_RULE in note and "`pump.py` reads the depth twice." in note,
        "holder note: the mod's polish lines join the holder's brief too")
    rec2 = W.new_record("pipeline:docs", ["C1"], "why", "workshop", NOW)
    b2 = W.brief(rec2, items, {"C1": None}, root=root)
    chk(lambda: W.POLISH_RULE in b2 and "boundary page" in b2,
        "brief: a pipeline bundle carries the rule and points at the polish.md beside each changed file's page")
    # the polish rule's additions of 2026-11-25 (RIMMANDRAKE_MERGE_BUILDER_ROLES_INTO_ONE_THREE_FILES_DIFFER_BY_SETTINGS):
    # an old line is read now and a stale one deleted, and each polish change is its own `polish:` commit
    chk(lambda: "stale or wrong line is deleted, not done" in W.POLISH_RULE and "`polish:`" in W.POLISH_RULE,
        "brief: the polish rule says an old line is read first and each polish change is a `polish:` commit")


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
    chk(lambda: by["H1"]["decision"] == "launch" and by["H1"]["bundle"].get("host") == "SteveDesktop",
        "group: a lead whose only room is another host leads a bundle on that host (%s)" % by["H1"])
    chk(lambda: sorted(launches2) == ["H1", "L1", "M1", "N1", "S1"], "group: the launches are the leads and the Shape run")
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


# ---- part 4: restart and keep going ---------------------------------------------------------------------------------

def bundle_rec(W, members, at=NOW, units=None, outcomes=None, state="live"):
    rec = W.new_record("pipeline:ledger", members, "why", "workshop", at)
    rec.update(state=state, units=units or [{"unit": "u-first", "at": at, "kind": "launch", "ended_before": 0}],
               outcomes=outcomes or {})
    return W.store_write(rec)


def facts_of(**kw):
    """member facts as read_members returns them: {id: {state, wait_until, wait_ts, refusal, refusal_ts}}"""
    out = {}
    for i, f in kw.items():
        out[i] = dict({"state": "proposed", "wait_until": None, "wait_ts": None, "refusal": None, "refusal_ts": None}, **f)
    return out


def run_rec(W, rec, unit="u-first", result="success (exit 0)", kind=None):
    r = {"unit": unit, "item": rec["lead"], "seat": "BENCH", "at": NOW + 10, "result": result,
         "env": {W.ENV: rec["id"]}, "next_act_owner": "list_dispatch", "model": "opus"}
    if kind:
        r["continued_from"] = "u-first"
    return r


def t_outcomes_are_read_from_the_ledger():
    W = WB()
    rec = bundle_rec(W, ["O1", "O2", "O3", "O4", "O5", "O6"])
    rec["sort_closed"] = ["O6"]
    f = facts_of(O1={"state": "done"}, O2={"state": "dropped"},
                 O3={"refusal": "REFUSED BY BUNDLE: not this system", "refusal_ts": NOW + 5},
                 O4={"wait_until": "2099-01-01T00:00:00Z", "wait_ts": NOW + 6}, O5={}, O6={"state": "done"})
    o = W.outcomes(rec, f, NOW + 100)
    chk(lambda: [o[i]["outcome"] for i in rec["members"]] == ["fixed", "dropped", "refused", "waits", "open",
                                                             "already_fixed"], "outcomes: %s" % o)
    chk(lambda: "not this system" in o["O3"]["why"], "outcomes: a refusal keeps its reason")
    old = facts_of(O3={"refusal": "REFUSED BY BUNDLE: old", "refusal_ts": NOW - 50},
                   O4={"wait_until": "2099-01-01T00:00:00Z", "wait_ts": NOW - 50})
    o2 = W.outcomes(rec, old, NOW + 100)
    chk(lambda: o2["O3"]["outcome"] == "open" and o2["O4"]["outcome"] == "open",
        "outcomes: a refusal or wait from before the bundle began is no outcome of it")
    o3 = W.outcomes(rec, facts_of(O1={"state": "done", "close_ts": NOW - 50}), NOW + 100)
    chk(lambda: o3["O1"]["outcome"] == "already_fixed" and "before" in o3["O1"]["why"],
        "outcomes: a member closed done before the bundle began is no fix of it (%s)" % o3["O1"])
    chk(lambda: W.outcomes(rec, {"O1": None}, NOW)["O1"]["outcome"] == "unread",
        "outcomes: a member that could not be read is unread, never open or fixed")


def t_restart_until_each_member_has_an_outcome():
    W = WB()
    import left_open_continue as LOC
    rec = bundle_rec(W, ["P1", "P2", "P3"])
    f = facts_of(P1={"state": "done"}, P2={}, P3={})
    for res, what in (("success (exit 0)", "a success"), ("failed (exit 1)", "a death"),
                      ("killed by the spend watchdog at its cap", "a spend stop")):
        r = run_rec(W, rec, result=res)
        p = LOC.plan(r, {"state": "done", "notes": []}, f, now=NOW + 100, gates={k: (lambda a: None) for k in LOC.GATES})
        chk(lambda: p["act"] == "continue" and p["target"] == "P2" and p.get("bundle") == rec["id"],
            "restart: after %s with open members the bundle restarts on the first open one (%s)" % (what, p))
    r = run_rec(W, rec, result="killed: stopped by the Conductor (pipe stop --kill)")
    p = LOC.plan(r, {"state": "proposed", "notes": []}, f, now=NOW + 100, gates={k: (lambda a: None) for k in LOC.GATES})
    chk(lambda: p["act"] == "none" and "hand" in p["why"], "restart: a run stopped by hand is not restarted (%s)" % p)
    r = run_rec(W, rec, result="killed: signal (killed SIGKILL)")
    p = LOC.plan(r, {"state": "proposed", "notes": []}, f, now=NOW + 100, gates={k: (lambda a: None) for k in LOC.GATES})
    chk(lambda: p["act"] == "continue", "restart: a death by signal restarts (%s)" % p.get("why"))
    held = dict({k: (lambda a: None) for k in LOC.GATES}, held=lambda m: "HELD BY OWNER")
    r = run_rec(W, rec)
    r["env"]["RM_CONTROL_MOD"] = "FlowWorks"
    p = LOC.plan(r, {"state": "proposed", "notes": []}, f, now=NOW + 100, gates=held)
    chk(lambda: p["act"] == "none" and "HELD" in p["why"], "restart: an owner hold stops the restart")
    W.note_end(rec["id"], p["bundle_plan"], "u-first", NOW + 100, say=lambda line: None)
    chk(lambda: W.store_read(rec["id"])["state"] == "gated", "restart: a restart a gate refused leaves the bundle gated")
    over = W.overlay({}, ["P2"], {rec["id"]: W.store_read(rec["id"])}, live=lambda u: False)
    chk(lambda: over["P2"].get("bundle_resume") == rec["id"] and "bundle" not in over["P2"],
        "restart: a gated bundle's open member is the lane's again, with one more run owed")
    import list_dispatch as LD
    st = {"items": {"P2": {"attempts": [{"at": NOW, "unit": "u-first", "model": "opus", "cap": 120, "kind": "work"}]}}}
    facts = {"items": {"P2": {"state": "proposed", "effect": "cmd:x", "verdict": "fails", "events": 1, "out": "red"}},
             "runs": over, "recent": None}
    rws, ln = LD.decide({"enabled": True, "max_live": 2}, st, facts, NOW + 200)
    chk(lambda: rws[0]["decision"] == "launch", "restart: once the gate lifts the lane launches it again (%s)" % rws[0])
    rc, newer = W.launch_bundle(rec["system"], ["P2"], {"P2": item("P2")}, "again", "workshop", now=NOW + 300,
                                launcher=lambda r, b: (0, "DETACHED u-z", "u-z"))
    chk(lambda: rc == 0 and W.store_read(rec["id"])["state"] == "replaced",
        "restart: a new bundle of the system replaces the gated one (%s)" % W.store_read(rec["id"])["state"])
    W.store_write(dict(newer, state="ended"))
    sid, fresh, _ = LOC.resume_choice(run_rec(W, rec), {"target": "P2", "bundle": rec["id"]}, NOW)
    chk(lambda: sid is None and "state file" in str(fresh), "restart: always fresh, never a resume (%s)" % fresh)
    h = LOC.header(run_rec(W, rec), {"n": 2, "target": "P2", "bundle": rec["id"], "open_lane": ["P2", "P3"],
                                     "state_file": rec["state_file"]}, NOW)
    chk(lambda: rec["state_file"] in h and rec["id"] in h and "a day" not in h,
        "restart: the header names the state file and the bundle, and no daily count (%s)" % h[:200])


def t_finish_writes_the_bundles_end():
    """part of restart-until-each-member-has-an-outcome: finish's step plans from the clone's member read and writes the
    record before the kick"""
    W = WB()
    import left_open_continue as LOC
    import detached_helper as DH
    chk(lambda: DH.runs_dir().startswith(TMP), "finish test: the run records are the throwaway ones (%s)" % DH.runs_dir())
    rec = bundle_rec(W, ["F1", "F2"])
    r = run_rec(W, rec)
    DH.write_record(dict(r, status="finished"))
    kicked = []
    p, line = LOC.at_finish(r, {"state": "proposed", "notes": []}, TMP, NOW + 100,
                            continuer=lambda rr, q: kicked.append(q) or "continue kicked",
                            states_reader=lambda clone, ids: facts_of(F1={"state": "done"}, F2={}))
    on = W.store_read(rec["id"])
    chk(lambda: p["act"] == "continue" and kicked and on["state"] == "restarting" and on["outcomes"]["F1"]["outcome"] == "fixed",
        "finish: plans the restart, kicks it and writes the record restarting with outcomes (%s / %s)" % (line, on["state"]))
    chk(lambda: "bundle_plan" not in (DH.read_record(r["unit"]) or {}).get("continue_plan", {}) and
        (DH.read_record(r["unit"]) or {}).get("continue_plan", {}).get("bundle") == rec["id"],
        "finish: the run record's continue_plan names the bundle")
    p2, line2 = LOC.at_finish(r, {"state": "proposed", "notes": []}, TMP, NOW + 100,
                              continuer=lambda rr, q: "x", states_reader=lambda clone, ids: 1 / 0)
    chk(lambda: p2["act"] == "alarm" and "could not be read" in p2["why"],
        "finish: members that cannot be read raise an alarm, never a silent end (%s)" % line2)


def t_a_restart_that_ended_no_member_raises():
    W = WB()
    import left_open_continue as LOC
    units = [{"unit": "u-first", "at": NOW, "kind": "launch", "ended_before": 0},
             {"unit": "u-second", "at": NOW + 50, "kind": "restart", "ended_before": 1}]
    rec = bundle_rec(W, ["Q1", "Q2"], units=units)
    f = facts_of(Q1={"state": "done"}, Q2={})
    r = run_rec(W, rec, unit="u-second", kind="restart")
    p = LOC.plan(r, {"state": "proposed", "notes": []}, f, now=NOW + 100, gates={k: (lambda a: None) for k in LOC.GATES})
    chk(lambda: p["act"] == "alarm" and "Q2" in p["why"] and "u-second" in p["why"],
        "progress guard: a restart that ended no member raises, naming the open members and the unit (%s)" % p)
    f2 = facts_of(Q1={"state": "done"}, Q2={"refusal": "REFUSED BY BUNDLE: x", "refusal_ts": NOW + 60})
    p2 = LOC.plan(r, {"state": "proposed", "notes": []}, f2, now=NOW + 100, gates={k: (lambda a: None) for k in LOC.GATES})
    chk(lambda: p2["act"] == "none" and "every member" in p2["why"], "progress guard: a restart that ended one goes on")
    units1 = [{"unit": "u-first", "at": NOW, "kind": "launch", "ended_before": 0}]
    rec1 = bundle_rec(W, ["Q3", "Q4"], units=units1)
    p3 = LOC.plan(run_rec(W, rec1), {"state": "proposed", "notes": []}, facts_of(Q3={}, Q4={}), now=NOW + 100,
                  gates={k: (lambda a: None) for k in LOC.GATES})
    chk(lambda: p3["act"] == "continue", "progress guard: the first run that ended none is restarted once (%s)" % p3)
    import inspect
    chk(lambda: "bundle" in inspect.getsource(LOC.recheck), "progress guard: recheck reads the bundle rule")


def _step(LOC, unit, now, launch_fn, reader=lambda t: {"state": "proposed"}):
    """LOC.run as the continuation unit runs it, offline: no gate, no account end, the fake launch."""
    keep = LOC.account_end_wait
    LOC.account_end_wait = lambda now, plan_dir=None, **kw: None
    try:
        return LOC.run(unit, now=now, launch_fn=launch_fn, gates={k: (lambda a: None) for k in LOC.GATES},
                       log_path=os.path.join(TMP, "conductor.log"), reader=reader)
    finally:
        LOC.account_end_wait = keep


def t_the_real_restart_path_keeps_the_progress_guard():
    """part of a-restart-that-ended-no-member-raises, through the real path (finish -> the continuation step ->
    note_restart), not hand-built units: the restart's unit must carry the count that ended before it began."""
    W = WB()
    import left_open_continue as LOC
    import detached_helper as DH
    rec = bundle_rec(W, ["G1", "G2", "G3"], units=[{"unit": "u-g-first", "at": NOW, "kind": "launch", "ended_before": 0}])
    f = facts_of(G1={"state": "done"}, G2={}, G3={})
    r = run_rec(W, rec, unit="u-g-first")
    DH.write_record(dict(r, status="finished"))
    p, line = LOC.at_finish(r, {"state": "done", "notes": []}, TMP, NOW + 100, continuer=lambda rr, q: "continue kicked",
                            states_reader=lambda clone, ids: f)
    got = _step(LOC, "u-g-first", NOW + 150, lambda *a, **k: (0, "DETACHED u-g-second"))
    unit = next((u for u in W.store_read(rec["id"])["units"] if u["unit"] == "u-g-second"), {})
    chk(lambda: got["act"] == "continued" and unit.get("ended_before") == 1,
        "progress guard, real path: the restart's unit records the 1 member ended before it (%s / %s)" % (got, unit))
    r2 = run_rec(W, rec, unit="u-g-second", kind="restart")
    p2 = LOC.plan(r2, {"state": "proposed", "notes": []}, f, now=NOW + 300, gates={k: (lambda a: None) for k in LOC.GATES})
    chk(lambda: p2["act"] == "alarm", "progress guard, real path: that restart, ending none, raises (%s)" % p2.get("act"))


def t_a_restart_that_never_starts_leaves_the_bundle_gated():
    """part of restart-until-each-member-has-an-outcome: a restart refused after finish planned it (`pipe off
    family:left_open_continue` on the kick, the step's own recheck, a refused launch) must not leave the bundle
    `restarting`, a live state that holds every member out of the lane with no run."""
    W = WB()
    import left_open_continue as LOC
    import detached_helper as DH
    for tag, how in (("k", "kick"), ("c", "recheck"), ("l", "launch")):
        ids = ["H%s1" % tag, "H%s2" % tag]
        first = "u-h%s-first" % tag
        rec = bundle_rec(W, ids, units=[{"unit": first, "at": NOW, "kind": "launch", "ended_before": 0}])
        f = facts_of(**{ids[0]: {"state": "done"}, ids[1]: {}})
        r = run_rec(W, rec, unit=first)
        DH.write_record(dict(r, status="finished"))
        kick = "continue refused by control: pipe off family:left_open_continue" if how == "kick" else "continue kicked x"
        LOC.at_finish(r, {"state": "done", "notes": []}, TMP, NOW + 100, continuer=lambda rr, q: kick,
                      states_reader=lambda clone, ids_: f)
        if how == "recheck":
            _step(LOC, first, NOW + 150, lambda *a, **k: (0, "DETACHED u-never"), reader=lambda t: {"state": "done"})
        elif how == "launch":
            _step(LOC, first, NOW + 150, lambda *a, **k: (2, "refused: the clone pool is full"))
        st = W.store_read(rec["id"])["state"]
        chk(lambda: st == "gated", "restart never started (%s refused): the bundle reads gated, not %s" % (how, st))


def t_a_bundle_with_every_outcome_ends():
    W = WB()
    rec = bundle_rec(W, ["E1", "E2"])
    lines = []
    f = facts_of(E1={"state": "done"}, E2={"refusal": "REFUSED BY BUNDLE: needs the owner's flight test",
                                          "refusal_ts": NOW + 5})
    p = W.plan_restart(rec, f, run_rec(W, rec), NOW + 100)
    chk(lambda: p["act"] == "end", "end: every member has an outcome (%s)" % p)
    W.note_end(rec["id"], p, "u-first", NOW + 100, say=lines.append)
    on = W.store_read(rec["id"])
    chk(lambda: on["state"] == "ended" and on["outcomes"]["E2"]["outcome"] == "refused",
        "end: the record reads ended, with each outcome")
    chk(lambda: len(lines) == 2 and "E2" in lines[0] and "flight test" in lines[0],
        "end: each refusal goes to the Conductor log with its reason, once (%s)" % lines)
    chk(lambda: "ENDED" in lines[1] and rec["id"] in lines[1], "end: one line says the bundle ended (%s)" % lines[1:])
    W.note_end(rec["id"], p, "u-first", NOW + 200, say=lines.append)
    chk(lambda: len(lines) == 2, "end: a second end says nothing again")
    rec2 = bundle_rec(W, ["E3"])
    W.note_restart(rec2["id"], "u-new", NOW + 300, ended_before=0)
    on2 = W.store_read(rec2["id"])
    chk(lambda: on2["state"] == "live" and on2["restarts"] == 1 and on2["units"][-1]["unit"] == "u-new",
        "restart: the record takes the new unit and counts the restart")
    rec3 = bundle_rec(W, ["E4"], state="gated")
    W.note_restart(rec3["id"], "u-late", NOW + 300, ended_before=0)
    on3 = W.store_read(rec3["id"])
    chk(lambda: on3["state"] == "gated" and on3["units"][-1]["unit"] == "u-late" and on3["units"][-1].get("late"),
        "restart: a step that starts after the bundle was gated records its unit and leaves the state (%s)" % on3["state"])


def t_a_refused_member_is_stopped_with_its_reason():
    import list_dispatch as LD
    st = {"items": {"R9": {"attempts": [{"at": NOW, "unit": "u-b", "model": "opus", "cap": 120, "kind": "work"}]}}}
    facts = {"items": {"R9": {"state": "proposed", "effect": "cmd:x", "verdict": "fails", "events": 1, "out": "red"}},
             "runs": {"R9": {"live": [], "ended": ["u-b"], "bundle_refused": {"id": "WB-x", "why":
                                                                              "REFUSED BY BUNDLE: needs his flight test"}}},
             "recent": None}
    rws, ln = LD.decide({"enabled": True, "max_live": 2}, st, facts, NOW + 100)
    chk(lambda: rws[0]["decision"] == "stopped" and "needs his flight test" in rws[0]["why"]
        and "flight test" in rws[0]["need"]["why_not_recovered"] and not ln,
        "lane: a member its bundle refused reads stopped, and its Needs Conductor line quotes the refusal (%s)" % rws[0])
    st["items"]["R9"]["attempts"] = []      # what `list_dispatch.py clear R9` leaves (its attempts go under `cleared`)
    rws, ln = LD.decide({"enabled": True, "max_live": 2}, st, facts, NOW + 200)
    chk(lambda: rws[0]["decision"] != "stopped" and "R9" in ln,
        "lane: a refused member that the Conductor cleared may run again (%s)" % rws[0])


# ---- part 5: the live pass ------------------------------------------------------------------------------------------

def t_live_pass_takes_a_free_game_or_says_unrun():
    W = WB()
    rec = bundle_rec(W, ["V1"])
    asked, ran = [], []

    def query(g):
        asked.append(g)
        return {"ArchBig": (75, "ArchBig: held by rm-x for a visit"), "ArchSmall": (0, "ArchSmall: FREE")}[g]

    def runner(argv):
        ran.append(argv)
        return 0
    rc = W.live_pass(rec["id"], "the lamp scene", ["python3", "scene.py", "--x"], query=query, runner=runner, now=NOW)
    chk(lambda: rc == 0 and asked == ["ArchBig", "ArchSmall"] and ran and "ArchSmall" in ran[0] and "run" in ran[0]
        and ran[0][-3:] == ["python3", "scene.py", "--x"], "live: ArchBig held, so the check runs on ArchSmall under game_lock run (%s)" % ran)
    on = W.store_read(rec["id"])
    chk(lambda: on["live_runs"][-1]["game"] == "ArchSmall" and on["live_runs"][-1]["rc"] == 0,
        "live: the record keeps the game and the check's exit")
    ran.clear()
    rc2 = W.live_pass(rec["id"], "the lamp scene", ["python3", "scene.py"], query=lambda g: (
        {"ArchBig": 3, "ArchSmall": 2}[g], "%s: answer" % g), runner=runner, now=NOW)
    on = W.store_read(rec["id"])
    last = on["live_runs"][-1]
    chk(lambda: rc2 == 4 and not ran and last.get("unrun") and last["cmd"] == "python3 scene.py"
        and "ArchBig" in str(last["answers"]) and "ArchSmall" in str(last["answers"]),
        "live: no free game runs nothing and records UNRUN with the exact command and each game's answer (%s)" % last)
    # measured 2026-11-25: argparse.REMAINDER after the bundle id swallowed --for, so the real command line was refused
    o = W.parse(["live", "WB-x", "--for", "the lamp scene", "--", "python3", "-c", "print(1)"])
    chk(lambda: o.what == "the lamp scene" and o.cmd == ["python3", "-c", "print(1)"] and o.bundle == "WB-x",
        "live: the command line parses --for and the command after -- (%s)" % vars(o))


# ---- part 6: the Maturation Pipeline's road back is one bundle ------------------------------------------------------

def t_the_maturation_road_back_is_one_bundle():
    W = WB()
    items = {"MT_RED": item("MT_RED", home="mod:FlowWorks", effect="cmd:python3 x_accept.py"),
             "MT_NOTEST": item("MT_NOTEST", home="mod:FlowWorks"),
             "MT_WAITS": item("MT_WAITS", home="mod:FlowWorks", effect="cmd:y",
                              wait_until="2099-01-01T00:00:00Z"),
             "MT_ROAD": item("MT_ROAD", home="mod:FlowWorks", effect="cmd:z"),
             "OTHER_MOD": item("OTHER_MOD", home="mod:Pyrelands", effect="cmd:q")}
    def reading(it):
        h = (it.home or {}).get("home", "")
        return {"mod": h[4:] if h.startswith("mod:") else None}
    got = W.mod_members("FlowWorks", {"MT_ROAD"}, NOW, items=items, reading=reading, prose_of=lambda i: "",
                        refused={}, leased=lambda it: False)
    chk(lambda: got == ["MT_RED"], "maturation: a ready ticket of the mod with a test joins; no test, a wait, the road "
                                   "back's own and another mod's do not (%s)" % got)
    gated = W.store_write(dict(W.new_record("mod:FlowWorks", ["MT_OLD"], "why", "maturation", NOW - 900), state="gated"))
    rc, rec = W.holder_bundle("FlowWorks", "MT_ROAD", ["MT_ROAD"], ["MT_RED"], NOW)
    chk(lambda: W.store_read(gated["id"])["state"] == "replaced" and W.store_read(gated["id"])["replaced_by"] == rec["id"],
        "maturation: the holder's bundle carries on a gated bundle of its mod, which reads replaced")
    chk(lambda: rc == 0 and rec["system"] == "mod:FlowWorks" and rec["members"] == ["MT_ROAD", "MT_RED"]
        and rec["pipeline"] == "maturation" and W.store_read(rec["id"])["state"] == "launching",
        "maturation: the holder's road back and the joined tickets are one bundle of the mod (%s)" % rec.get("members"))
    rc2, why = W.holder_bundle("FlowWorks", "MT_ROAD", ["MT_ROAD"], [], NOW + 5)
    chk(lambda: rc2 == 2 and rec["id"] in why, "maturation: a mod with a live bundle launches no second (%s)" % why)
    note = W.holder_note(rec, items, {"MT_RED": "cmd:python3 x_accept.py"})
    chk(lambda: rec["id"] in note and rec["state_file"] in note and "roles/builder.md" in note and "MT_RED" in note
        and "write it after each group" in note and "a group is one member" in note and "work_bundle.py context" in note,
        "maturation: the holder's brief names the bundle, its state file, the role and each joined ticket")
    W.holder_launched(rec["id"], "rm-holder-9", NOW)
    chk(lambda: W.store_read(rec["id"])["state"] == "live" and W.store_read(rec["id"])["units"][0]["unit"] == "rm-holder-9",
        "maturation: the started holder is the bundle's run")
    W.holder_launched(rec["id"], None, NOW, "refused: off")
    chk(lambda: W.store_read(rec["id"])["state"] == "launch_failed", "maturation: a holder that never started fails the bundle")


# ---- part 7: the page ------------------------------------------------------------------------------------------------

def t_the_page_shows_each_live_bundle():
    W = WB()
    live = W.new_record("pipeline:docs", ["G1", "G2"], "why", "workshop", NOW)
    live.update(state="live", step="3 fix in order", restarts=2, units=[{"unit": "u-live", "at": NOW, "kind": "restart"}],
                outcomes={"G1": {"outcome": "fixed", "why": "closed done"}})
    dead = W.new_record("pipeline:hooks", ["H1"], "why", "workshop", NOW)
    dead.update(state="live", units=[{"unit": "u-dead", "at": NOW, "kind": "launch"}])
    ended = W.new_record("pipeline:ledger", ["J1"], "why", "workshop", NOW)
    ended.update(state="ended")
    page = W.page_rows(NOW + 60, bundles={b["id"]: b for b in (live, dead, ended)},
                       unit_live=lambda u: u == "u-live")
    ids = [r["id"] for r in page["rows"]]
    chk(lambda: page["state"] == "ok" and live["id"] in ids and dead["id"] in ids and ended["id"] not in ids,
        "page: one block per bundle that is not ended (%s)" % ids)
    r = next(x for x in page["rows"] if x["id"] == live["id"])
    chk(lambda: r["system"] == "pipeline:docs" and r["step"] == "3 fix in order" and r["restarts"] == 2
        and r["members"] == [("G1", "fixed"), ("G2", "no outcome yet")], "page: system, step, restarts, members (%s)" % r)
    d = next(x for x in page["rows"] if x["id"] == dead["id"])
    chk(lambda: "dead, no finish" in d["state"], "page: a live bundle whose unit is gone reads dead, no finish (%s)" % d)
    md, ht = "\n".join(W.page_md(page)), W.page_html(page)
    chk(lambda: all(x in md and x in ht for x in ("docs part of the pipeline", "1 of 2 tickets done", "3 fix in order",
                                                  "restarted 2 times", W.when(NOW))),
        "page: the markdown and the HTML both show the bundle by meaning (%s)" % md)
    # the owner, 2026-11-25: "summarize the meaningful outcome that a human needs to know, not lists of ticket names"
    import re
    mod = W.new_record("mod:ExplosiveKnockback", ["RIMMANDRAKE_BRUISE_KNOCKBACK_LANDING_ON_PAWN",
                                                  "RIMMANDRAKE_FLING_KNOCKBACK_CARRY_ON_OWN_ARC"], "why", "maturation", NOW)
    mod.update(state="live", step="live pass on RIMMANDRAKE_FLING_KNOCKBACK_CARRY_ON_OWN_ARC",
               units=[{"unit": "u-live", "at": NOW, "kind": "launch"}], raised={"why": "RIMMANDRAKE_X_Y_Z is stuck"},
               outcomes={"RIMMANDRAKE_BRUISE_KNOCKBACK_LANDING_ON_PAWN": {"outcome": "dropped"}})
    fails = [dict(W.new_record("mod:ExplosiveKnockback", ["RIMMANDRAKE_A_B_C"], "why", "maturation", NOW + i),
                  id="WB-mod-ExplosiveKnockback-2026112%d-180116" % i, state="launch_failed") for i in range(2)]
    pg = W.page_rows(NOW + 60, bundles={b["id"]: b for b in [live, dead, ended, mod] + fails},
                     unit_live=lambda u: u == "u-live")
    md2, ht2 = "\n".join(W.page_md(pg)), W.page_html(pg)
    tid = re.compile(r"\b[A-Z][A-Z0-9]+(?:_[A-Z0-9]+){2,}\b|\bWB-[A-Za-z0-9-]+|\d{4}-\d\d-\d\dT|\bUTC\b")
    chk(lambda: not tid.search(md2) and not tid.search(ht2), "page: no ticket name, bundle id or UTC stamp (%s)" %
        tid.findall(md2 + ht2)[:3])
    chk(lambda: "Explosive Knockback mod" in md2 and "1 of 2 tickets done" in md2 and "asked the Conductor" in md2,
        "page: a mod bundle reads by the mod's name, its tickets done and its call for help (%s)" % md2)
    live_lines = [x for x in md2.splitlines() if x.startswith("- **")]
    chk(lambda: len(live_lines) == 3, "page: one line per live bundle, none for an ended or failed one (%s)" % live_lines)
    chk(lambda: sum(1 for x in md2.splitlines() if "failed to launch" in x) == 1 and "2 failed to launch" in md2
        and "1 ended" in md2, "page: ended and failed launches are one count line (%s)" % md2)
    chk(lambda: all(len(x.split()) <= 40 for x in live_lines), "page: each bundle line is short (%s)" % live_lines)
    blind = W.page_rows(NOW, bundles=None, reader=lambda: 1 / 0)
    chk(lambda: blind["state"] == "unmeasured" and "UNMEASURED" in "\n".join(W.page_md(blind)) and
        "UNMEASURED" in W.page_html(blind), "page: a store that cannot be read is one UNMEASURED line, never empty")
    none = W.page_rows(NOW, bundles={})
    chk(lambda: "none" in "\n".join(W.page_md(none)), "page: no live bundle says none, looked")


def t_a_test_never_writes_the_real_store():
    """measured 2026-11-25: a holder selftest with no RM_WORK_BUNDLE_DIR wrote WB-mod-WreckedMachines into the real
    store, where it read as a live bundle"""
    W = WB()
    import subprocess as sp
    env = {k: v for k, v in os.environ.items() if k != "RM_WORK_BUNDLE_DIR"}
    env["RM_UNDER_SELFTEST"] = "1"
    r = sp.run([sys.executable, "-c", "import sys; sys.path.insert(0, %r); import work_bundle as W; W.store_dir()" % HERE],
               env=env, capture_output=True, text=True)
    chk(lambda: r.returncode != 0 and "RM_WORK_BUNDLE_DIR" in r.stderr, "store: a test process with no store of its own "
                                                                         "is refused by name (%s)" % r.stderr[-200:])


def t_the_conductor_ends_a_dead_bundle():
    """a-run-whose-finish-never-ran: the page names `work_bundle.py end` as the Conductor's way out"""
    W = WB()
    rec = bundle_rec(W, ["K1"])
    lines = []
    rc = W.end_bundle(rec["id"], "its unit died with finish never run", NOW + 10, say=lines.append)
    on = W.store_read(rec["id"])
    chk(lambda: rc == 0 and on["state"] == "ended" and on["ended_by_hand"]["why"] and lines and rec["id"] in lines[0],
        "end: the Conductor's end marks the bundle ended, with its reason, and says one line (%s)" % on.get("state"))
    chk(lambda: W.end_bundle("WB-none-such", "x", NOW, say=lines.append) == 2, "end: a bundle that does not exist is refused")
    rec2 = bundle_rec(W, ["K2"])
    lines2 = []
    W.end_bundle(rec2["id"], "by hand", NOW + 10, say=lines2.append, unit_live=lambda u: True)
    chk(lambda: W.store_read(rec2["id"]).get("unit_live_at_end") == "u-first" and "u-first" in lines2[0]
        and "still" in lines2[0], "end: a bundle ended while its unit is live says so, and records it (%s)" % lines2)
    o = W.parse(["end", rec["id"], "--why", "dead"])
    chk(lambda: o.verb == "end" and o.why == "dead", "end: the command line parses")


def t_five_tickets_two_fixed_one_run():
    """The item's acceptance (RIMMANDRAKE_BATCH_ONE_MODS_OPEN_WORK_INTO_ONE_RUN_PIPELINE_SPLITS_PER_TICKET): on five open
    tickets of one mod, two already fixed, the batch command closes the two with their commit and launches exactly one
    run whose brief lists the other three."""
    W = WB()
    ids = ["AC_ONE", "AC_TWO", "AC_THREE", "AC_FOUR", "AC_FIVE"]
    green = {"AC_TWO", "AC_FOUR"}
    items = {i: item(i, home="mod:Pyrelands", effect="cmd:check-%s" % i, title="ticket %s" % i) for i in ids}
    closed, launched = [], []

    def launcher(rec, text):
        launched.append(text)
        return 0, "DETACHED u-acc", "u-acc"
    got = W.bundle_command("mod:Pyrelands", ids, items, "acceptance", NOW + 900, prose_of=lambda i: "",
                           run_effect=lambda t, r: ("holds", "ok") if t[10:] in green else ("fails", "red"),
                           run_script_fn=lambda p, r: ("fails", ""), sha="abc1234",
                           closer=lambda i, sha, ev: closed.append((i, sha)) or (0, "closed"),
                           refused={}.get, held=lambda i: None, leased=lambda it: False, launcher=launcher)
    chk(lambda: sorted(closed) == [("AC_FOUR", "abc1234"), ("AC_TWO", "abc1234")],
        "acceptance: the two already fixed close, with the commit named (%s)" % closed)
    chk(lambda: len(launched) == 1 and all(i in launched[0] for i in ("AC_ONE", "AC_THREE", "AC_FIVE"))
        and not any(i in launched[0] for i in green), "acceptance: exactly one run, its brief lists the other three")
    chk(lambda: got["rc"] == 0 and got["rec"]["members"] == ["AC_ONE", "AC_THREE", "AC_FIVE"],
        "acceptance: the bundle's members are the three (%s)" % got.get("rec", {}).get("members"))
    W.store_write(dict(got["rec"], state="ended"))


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


def t_the_lane_bundles_a_home_not_a_ticket():
    """RIMMANDRAKE_BUNDLE_LIST_TICKETS_BY_HOME_TEN_OF_TWELVE_HELD_ONE: on 2026-11-25 ten of twelve bundles held one ticket.
    New tickets have no recorded home, and the lane's bundle took only the tick's launch rows."""
    W = WB()
    reading = lambda it: {"mod": None}  # noqa: E731
    items = {"P": item("P", home="pipeline:test-lane"), "C1": item("C1", caused_by="P"), "C2": item("C2", caused_by="P"),
             "G": item("G", caused_by="C1"), "Q": item("Q"), "S1": item("S1", caused_by="Q"),
             "S2": item("S2", caused_by="Q"), "MP": item("MP", home="mod:FlowWorks"), "MC": item("MC", caused_by="MP"),
             "LONE": item("LONE"), "GONE": item("GONE", caused_by="NOT_AN_ITEM")}
    sy = {i: W.system_of(x, reading, items) for i, x in items.items()}
    chk(lambda: sy["C1"] == sy["C2"] == "pipeline:test-lane",
        "system_of: a ticket with no home takes its parent's home (%s %s)" % (sy["C1"], sy["C2"]))
    chk(lambda: sy["G"] == "cause:C1", "system_of: one hop only; a grandchild is the cause of its own parent (%s)" % sy["G"])
    chk(lambda: sy["S1"] == sy["S2"] == "cause:Q",
        "system_of: siblings of a parent with no home share one system, cause:<parent> (%s %s)" % (sy["S1"], sy["S2"]))
    chk(lambda: sy["MC"] == "cause:MP", "system_of: a mod: home is never inherited (it is mod work) (%s)" % sy["MC"])
    chk(lambda: sy["LONE"] == "item:LONE" and sy["GONE"] == "item:GONE",
        "system_of: no home and no parent in the ledger is a bundle of one (%s %s)" % (sy["LONE"], sy["GONE"]))
    chk(lambda: W.system_of(items["C1"], reading) == "item:C1", "system_of: without the items, the old reading")
    s, ids, _w = W.resolve("pipeline:test-lane", items, ["FlowWorks"], reading)
    chk(lambda: s == "pipeline:test-lane" and ids == ["C1", "C2", "P"],
        "resolve: a home's hand bundle takes the children that inherit it (%s)" % ids)
    s, ids, _w = W.resolve("cause:Q", items, ["FlowWorks"], reading)
    chk(lambda: s == "cause:Q" and ids == ["S1", "S2"], "resolve: cause:<parent> is a target (%s %s)" % (s, ids))
    rows = [{"item": "L1", "decision": "launch", "model": "sonnet", "cap": 50, "run_n": 1},
            {"item": "V2", "decision": "launch", "model": "opus", "cap": 120, "run_n": 1}]
    systems = {"L1": "pipeline:test-lane", "V2": "pipeline:bridge"}
    join = {"J1": "pipeline:test-lane", "J0": "pipeline:test-lane", "J3": "item:J3", "K1": "pipeline:docs",
            "V1": "pipeline:bridge", "M1": "mod:FlowWorks"}
    rows2, launches2 = W.group(rows, ["L1", "V2"], systems, {"pipeline:bridge": "WB-pipeline-bridge-1"}, join)
    by = {r["item"]: r for r in rows2}
    chk(lambda: by["L1"].get("bundle", {}).get("members") == ["L1", "J0", "J1"],
        "group: the lead's bundle takes every ready ticket of its home, not only the tick's launch rows (%s)"
        % by["L1"].get("bundle"))
    chk(lambda: by["V2"]["decision"] == "bundle_live" and "bundle" not in by["V2"],
        "group: a home with a live bundle gets no second bundle")
    chk(lambda: launches2 == ["L1"] and set(by) == {"L1", "V2"},
        "group: one launch for the home; a joining ticket neither leads nor gets a row (%s)" % launches2)
    rows3, launches3 = W.group([{"item": "L1", "decision": "launch", "model": "sonnet", "cap": 50, "run_n": 1}], ["L1"],
                               {"L1": "pipeline:test-lane"}, {})
    chk(lambda: rows3[0]["bundle"]["members"] == ["L1"] and launches3 == ["L1"],
        "group: a home with one ready ticket still gets its run")


def t_a_bundle_on_another_machine_is_live_here():
    """A bundle that runs on another machine (SteveDesktop's own store) is live here by its ledger citations."""
    W = WB()
    iso = lambda t: time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(t))  # noqa: E731
    now = 1_800_000_000.0
    evs = [{"ts": iso(now - 3600), "event": "close", "id": "X1", "why": "work bundle WB-pipeline-test-lane-20261125-192031: fixed"},
           {"ts": iso(now - 7 * 3600), "event": "claim", "id": "X2", "why": "work bundle WB-pipeline-docs-20261125-010101"},
           {"ts": iso(now - 600), "event": "note", "id": "X3", "text": "PROGRESS: work bundle WB-pipeline-ledger-20261125-020202 step 3"},
           {"ts": iso(now - 60), "event": "note", "id": "X4", "why": "work bundle WB-cause-Q-20261125-030303"}]
    local = {"WB-pipeline-ledger-20261125-020202": {"id": "WB-pipeline-ledger-20261125-020202", "state": "ended",
                                                    "system": "pipeline:ledger"}}
    got = W.cited_live(evs, now, local, ["pipeline:test-lane", "pipeline:docs", "pipeline:ledger", "cause:Q", "item:Z"])
    chk(lambda: got == {"pipeline:test-lane": "WB-pipeline-test-lane-20261125-192031", "cause:Q": "WB-cause-Q-20261125-030303"},
        "cited_live: a bundle this store does not hold is live while the ledger cites it; a quiet one and a local "
        "ended one are not (%s)" % got)


def t_a_bundle_on_another_host_launches_there():
    """RIMMANDRAKE_SEND_LANE_BUNDLES_TO_STEVEDESKTOP_NONE_SINCE_ONE_AM: from 11:52 PM PST 2026-11-24 every lane Work run
    was a bundle, and group() sent a lead whose only room was SteveDesktop back to slots_full, so no lane run went
    there. A host lead launches the whole bundle ON the host (./sync, then ./pipe bundle, over ssh); this store keeps
    a marker that reads live until the host's own record ends, and then the members' attempts read ended."""
    W = WB()
    import list_dispatch as LD
    # group: the order of the rows does not decide which rows join (a slots_full row before its lead joins it)
    rows = [{"item": "H0", "decision": "slots_full", "why": "full"},
            {"item": "H1", "decision": "launch", "model": "opus", "cap": 120, "run_n": 1, "host": "SteveDesktop"},
            {"item": "H2", "decision": "launch", "model": "sonnet", "cap": 50, "run_n": 1}]
    systems = {"H0": "pipeline:hooks", "H1": "pipeline:hooks", "H2": "pipeline:hooks"}
    rows2, launches2 = W.group(rows, ["H1", "H2"], systems, {})
    by = {r["item"]: r for r in rows2}
    chk(lambda: by["H1"].get("bundle") == {"system": "pipeline:hooks", "members": ["H1", "H0", "H2"], "host": "SteveDesktop"}
        and by["H0"]["decision"] == "bundled" and launches2 == ["H1"],
        "group: a host lead leads; a slots_full row before it joins it (%s %s)" % (by["H1"].get("bundle"), by["H0"]))
    # execute: the host lead launches through ssh; the host's sort left H0 out
    bid = "WB-pipeline-hooks-20261125-210000"
    seen, during = [], []

    def runner(argv, **kw):
        import fcntl
        seen.append(argv)
        f = open(os.path.join(os.path.dirname(W.store_dir()), "launch.lock"), "w")
        try:        # the store lock is free while the host works: a local finish is never held by a remote sort
            fcntl.flock(f, fcntl.LOCK_EX | fcntl.LOCK_NB)
            during.append(("lock free", W.live_bundles().get("pipeline:hooks")))
        except OSError:
            during.append(("lock held", None))
        finally:
            f.close()
        return types.SimpleNamespace(returncode=0, stderr="", stdout=(
            "SYNCED abc -> def\nleft out: H0  it is under another live lease (BENCH)\n"
            "BUNDLE %s of pipeline:hooks launched: rm-detached-hooks-1; 2 member(s): H1, H2\n" % bid))
    st = {"items": {}}
    items = {i: {"state": "proposed", "effect": "cmd:x", "verdict": "fails", "events": 1, "out": "red"} for i in systems}
    LD.execute({"enabled": True, "seat": "BENCH"}, st, rows2, launches2, {"items": items}, NOW,
               fx={"launch": lambda *a, **k: (9, "a local launch was made", None), "remote": runner})
    cmd = seen[0][-1] if seen else ""
    chk(lambda: len(seen) == 1 and "mandrake@stevedesktop-wsl" in seen[0] and "cd ~/rm/bench && { ./sync || " in cmd
        and cmd.index("./sync") < cmd.index("./pipe bundle H1 H0 H2 --why"), "execute: the host lead's bundle is launched on the host after ./sync (%s)" % seen)
    chk(lambda: during and during[0][0] == "lock free" and during[0][1] and during[0][1] != bid,
        "launch_remote: during the ssh the store lock is free and a placeholder holds the system (%s)" % during)
    ph = [r for r in W.all_bundles().values() if r.get("replaced_by") == bid]
    chk(lambda: len(ph) == 1 and ph[0]["state"] == "replaced", "launch_remote: the placeholder reads replaced (%s)" % ph)
    chk(lambda: by["H0"]["decision"] == "host_left_out" and "lease" in by["H0"]["why"],
        "execute: a bundled row the host left out says so, with the host's reason (%s)" % by["H0"])
    rec = W.store_read(bid)
    chk(lambda: rec and rec["host"] == "SteveDesktop" and rec["state"] == "live" and rec["members"] == ["H1", "H2"]
        and rec["units"][0]["unit"] == "rm-detached-hooks-1",
        "execute: this store keeps a marker of the remote bundle, with the members the host took (%s)" % rec)
    att = {i: (st["items"].get(i) or {}).get("attempts") for i in systems}
    chk(lambda: att["H1"][0]["unit"] == att["H2"][0]["unit"] == "rm-detached-hooks-1" and not att["H0"]
        and by["H1"]["decision"] == "launched",
        "execute: each member the host took gets the bundle's attempt; one it left out gets none (%s)" % att)
    # the minutes before the worker's first ledger act: the marker is live, the members read in_bundle
    runs = W.overlay({}, list(systems), W.all_bundles(), live=lambda u: None is W.store_read("no-such"))
    chk(lambda: runs["H1"].get("bundle") == bid and "bundle" not in runs.get("H0", {}),
        "overlay: a member of a live remote bundle carries its id (%s)" % runs)
    chk(lambda: W.live_bundles().get("pipeline:hooks") == bid, "live_bundles: the remote marker holds its system")
    # the host cannot be read: live until the quiet bound, then ended
    W.refresh_remote(W.all_bundles(), NOW + 600, read=lambda r: (None, "ssh: no route"), events=lambda: [])
    chk(lambda: W.store_read(bid)["state"] == "live", "refresh_remote: a host that cannot be read keeps the bundle live")
    # the host's record ends: the marker takes its state, outcomes and units; each member's attempt reads ended
    host = dict(rec, state="ended", outcomes={"H1": {"outcome": "fixed"}, "H2": {"outcome": "refused", "why": "x"}},
                units=[{"unit": "rm-detached-hooks-1", "kind": "launch"}, {"unit": "rm-detached-hooks-2", "kind": "restart"}])
    W.refresh_remote(W.all_bundles(), NOW + 3600, read=lambda r: (host, None), events=lambda: [])
    after = W.store_read(bid)
    chk(lambda: after["state"] == "ended" and after["host"] == "SteveDesktop" and len(after["units"]) == 2,
        "refresh_remote: the host's end is copied into the marker (%s)" % after)
    runs = W.overlay({}, list(systems), W.all_bundles(), live=lambda u: True)
    chk(lambda: "rm-detached-hooks-1" in runs["H1"]["ended"] and "bundle" not in runs["H1"]
        and runs["H2"].get("bundle_refused", {}).get("id") == bid,
        "overlay: after the remote end each member's attempt reads ended, though no local record exists (%s)" % runs)
    st["items"]["H1"]["attempts"][0]["next"] = "LEFT OPEN: x"
    rws, _ln = LD.decide({"enabled": True, "max_live": 2}, st, {"items": {"H1": items["H1"]}, "runs": runs, "recent": None},
                         NOW + 3700)
    chk(lambda: rws[0]["decision"] != "unseen", "lane: a member of an ended remote bundle never reads unseen (%s)" % rws[0])
    # a marker the host never reports: ended once no ledger event cites it for REMOTE_QUIET_S
    W.store_write(dict(rec, id=bid + "q", state="live", at=NOW))
    W.refresh_remote({bid + "q": W.store_read(bid + "q")}, NOW + W.REMOTE_QUIET_S - 60, read=lambda r: (None, "down"),
                     events=lambda: [{"ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(NOW + 100)),
                                      "why": "work bundle %sq" % bid}])
    chk(lambda: W.store_read(bid + "q")["state"] == "live", "refresh_remote: a cited remote bundle stays live")
    W.refresh_remote({bid + "q": W.store_read(bid + "q")}, NOW + 100 + W.REMOTE_QUIET_S + 60,
                     read=lambda r: (None, "down"), events=lambda: [])
    q = W.store_read(bid + "q")
    chk(lambda: q["state"] == "ended" and "quiet" in q.get("ended_why", ""),
        "refresh_remote: a remote bundle that nobody can read or cite for REMOTE_QUIET_S reads ended (%s)" % q)
    # the page: a live remote bundle is never read "dead, no finish" by a local unit check
    W.store_write(dict(rec, id=bid + "p", state="live"))
    pg = W.page_rows(NOW, bundles={bid + "p": W.store_read(bid + "p")}, unit_live=lambda u: False)
    chk(lambda: "dead" not in pg["rows"][0]["state"] and "SteveDesktop" in pg["rows"][0]["state"],
        "page: a live remote bundle reads live on its host (%s)" % pg["rows"])
    # a host refusal (a live bundle of the system there) leaves no marker and no spent attempt
    st2 = {"items": {}}
    rows3, l3 = W.group([{"item": "H1", "decision": "launch", "model": "opus", "cap": 120, "run_n": 1,
                                 "host": "SteveDesktop"}], ["H1"], {"H1": "pipeline:other"}, {})
    LD.execute({"enabled": True}, st2, rows3, l3, {"items": items}, NOW, fx={"remote": lambda a, **k: types.SimpleNamespace(
        returncode=2, stderr="", stdout="REFUSED: pipeline:other already has a live bundle, WB-pipeline-other-1\n")})
    chk(lambda: rows3[0]["decision"] == "bundle_live" and not st2["items"].get("H1", {}).get("attempts")
        and not W.live_bundles().get("pipeline:other"),
        "execute: a host that refuses (its own live bundle) is bundle_live, with no attempt or hold (%s %s)" % (rows3[0], st2))
    rows4, l4 = W.group([{"item": "H1", "decision": "launch", "model": "opus", "cap": 120, "run_n": 1,
                          "host": "SteveDesktop"}], ["H1"], {"H1": "pipeline:third"}, {})
    LD.execute({"enabled": True}, st2, rows4, l4, {"items": items}, NOW, fx={"remote": lambda a, **k: types.SimpleNamespace(
        returncode=0, stderr="", stdout="sort: H1  closed\nNO BUNDLE: pipeline:third has no ready member (1 closed by the "
                                        "sort, 0 left out)\n")})
    chk(lambda: rows4[0]["decision"] == "no_bundle" and not st2["items"].get("H1", {}).get("attempts"),
        "execute: a host whose sort closed every member launched nothing, and no attempt is spent (%s)" % rows4[0])

    def boom(a, **k):
        raise OSError("ssh: connect refused")
    rc5, got5 = W.launch_remote("SteveDesktop", "pipeline:fourth", ["H1"], "why", "workshop", now=NOW, runner=boom)
    chk(lambda: rc5 == 1 and "connect refused" in got5["launch_out"] and not W.live_bundles().get("pipeline:fourth"),
        "launch_remote: an ssh that raises leaves no live placeholder (%s)" % got5)


def main():
    for t in [t_sort_runs_each_members_test_and_closes_only_green, t_sort_dry_closes_nothing, t_members_are_one_system,
              t_ready_members_only, t_one_live_bundle_per_system, t_the_record_is_written_at_launch,
              t_the_brief_names_every_member_and_the_role, t_the_brief_carries_the_polish_of_its_files, t_the_lane_launches_one_bundle_per_system,
              t_the_lane_bundles_a_home_not_a_ticket, t_a_bundle_on_another_machine_is_live_here,
              t_a_bundle_on_another_host_launches_there,
              t_context_reads_the_own_session, t_outcomes_are_read_from_the_ledger,
              t_restart_until_each_member_has_an_outcome, t_finish_writes_the_bundles_end,
              t_a_restart_that_ended_no_member_raises, t_the_real_restart_path_keeps_the_progress_guard,
              t_a_restart_that_never_starts_leaves_the_bundle_gated,
              t_a_bundle_with_every_outcome_ends, t_a_refused_member_is_stopped_with_its_reason,
              t_live_pass_takes_a_free_game_or_says_unrun, t_the_page_shows_each_live_bundle,
              t_the_maturation_road_back_is_one_bundle, t_a_test_never_writes_the_real_store,
              t_the_conductor_ends_a_dead_bundle, t_five_tickets_two_fixed_one_run,
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
