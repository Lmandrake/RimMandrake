#!/usr/bin/env python3
"""selftest_left_open_continue: a detached run that ends success with work left is continued by itself
(RIMMANDRAKE_CONTINUE_LEFT_OPEN_RUNS_WITHOUT_A_HAND_RELAUNCH, 2026-11-18: a four-ticket lane closed one ticket and
exited, a five-step split did step one and exited with a LEFT OPEN note, and the Conductor relaunched each by hand;
owner: "Why are you having to relaunch it?").

Hermetic: a temp run-record dir and conductor log; a fake launch, fake gates and a fake systemd runner. Cases:
  A  open item, LEFT OPEN note since the start   -> one continuation, same item and model, header quotes the note
  B  closed item, no lane                        -> none
  C  lane brief with open tickets                -> continuation listing them, on the first open ticket
  D  limit reached (3 today for the item)        -> alarm line with the fixed id, no launch
  E  run stopped by the spend watchdog, no opt-in -> none; with --continue-on-cap 1 -> one, then none (opt-in used)
  F  killed run, voided run                      -> none
  G  owner-held mod, paused pipeline, `pipe off` -> none
  H  a second pass                               -> launches nothing (continued_by stands)
  I  no spend, cap or dollar figure in any header; finish kicks the continuation unit only when one is owed;
     launch records --continue-on-cap and the chain fields from creation
"""
import json
import os
import re
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
TMP = tempfile.mkdtemp(prefix="selftest_left_open_continue_")
os.environ["RM_DISPATCHER_STATE"] = os.path.join(TMP, "state")
os.environ["RM_CONDUCTOR_LOG"] = os.path.join(TMP, "conductor.md")
os.environ.setdefault("RM_UNDER_SELFTEST", "1")
sys.path.insert(0, HERE)
import detached_helper as DH  # noqa: E402
_LIVE_DRAIN = DH.drain_refusal


def _drain_refusal(now, extra=None, resume_session=None, path=None):
    """The account gate reads only a test's own notice: the machine's live plan is never this test's input. On a
    follower machine (SteveDesktop) the live notice is old, and every continuation here read 'waits for the account
    switch' (26 FAILs, 2026-11-25)."""
    return _LIVE_DRAIN(now, extra, resume_session, path) if path is not None else None


DH.drain_refusal = _drain_refusal
import left_open_continue as LOC  # noqa: E402

FAILS = []
T0 = 1_800_000_000.0
STATE = os.environ["RM_DISPATCHER_STATE"]
LOG = os.environ["RM_CONDUCTOR_LOG"]
ITEM = "RIMMANDRAKE_SPLIT_FIVE_STEPS_DID_ONE"
LANE = ["RUN_SELFTESTS_FIX_STDERR_EATS_MARKER", "OPS_WATCH_FIX_BLIND_READINGS_STILL_ZERO",
        "DISPATCHER_FIX_INCIDENT_BELLS_OVERWRITE", "RIMMANDRAKE_FIX_SLOT_ALLOCATOR_OVERRIDE_AND_BURN_PICK"]
LANE_BRIEF = ("# Lane watchers: pipeline upgrade tickets\n\nYou build the tickets below, IN THIS ORDER.\n\n"
              + "".join("- `%s` (triage NEEDS SPLIT)\n" % t for t in LANE) + "\n## For EACH ticket\n1. decide.\n")
SPEND = re.compile(r"\$|usd|spend|spent|budget|cap\b|remain|weighted tokens", re.I)


def check(name, ok, detail=""):
    print(("PASS " if ok else "FAIL ") + name + (": " + detail if detail and not ok else ""))
    if not ok:
        FAILS.append(name)


N = [0]


def make_run(item=ITEM, brief="Do the five-step split of the code.", result="success (exited 0)", out=None,
             at=T0, model="opus", env=None, **extra):
    N[0] += 1
    unit = "rm-detached-bench-test-%d-%d" % (N[0], int(at))
    runs = DH.runs_dir()
    src = os.path.join(runs, unit + ".brief.src.md")
    with open(src, "w", encoding="utf-8") as f:
        f.write(brief)
    outp = os.path.join(runs, unit + ".out")
    with open(outp, "w", encoding="utf-8") as f:
        json.dump(out if out is not None else {"result": "did step one", "usage": {}}, f)
    rec = {"unit": unit, "seat": "BENCH", "item": item, "clone": os.path.join(TMP, "clones", item + ".det"),
           "clone_how": "reused", "model": model, "max_s": None, "budget_usd": 15.0, "at": at, "state": STATE,
           "status": "finished", "result": result, "ended": at + 600, "brief_src": src, "out": outp,
           "err": outp + ".err"}
    if env:
        rec["env"] = env
    rec.update(extra)
    DH.write_record(rec)
    return rec


def note(text, ts):
    return {"event": "note", "id": ITEM, "ts": DH.iso(ts), "text": text}


LEFT = "LEFT OPEN: steps 2-5 of the split (move dispatcher glue, rename the box, retire the shim, docs) are not done"


def states_for(item_state, lane_states=None):
    def reader(clone, ids):
        st = {ITEM: item_state}
        st.update(lane_states or {})
        return {i: st.get(i) for i in ids}
    return reader


class Gates(object):
    def __init__(self, paused=None, held=None, voided=(), blocked=None):
        self.p, self.h, self.v, self.b = paused, held, set(voided), blocked

    def as_dict(self):
        return {"paused": lambda mod: self.p, "held": lambda mod: self.h if mod else None,
                "voided": lambda unit: unit in self.v, "blocked": lambda spec: self.b}


LAUNCHES = []


def fake_launch(seat, item, brief, model, max_s, budget, **kw):
    LAUNCHES.append({"seat": seat, "item": item, "brief": brief, "model": model, "budget": budget, **kw})
    unit = "rm-detached-bench-cont-%d" % len(LAUNCHES)
    rec = {"unit": unit, "seat": seat, "item": item, "model": model, "at": kw.get("now") or T0, "state": STATE,
           "status": "running", "budget_usd": budget}
    rec.update(kw.get("extra") or {})
    DH.write_record(rec)
    return 0, "DETACHED %s\n  item %s" % (unit, item)


def open_reader(state="claimed", wait_until=None):
    """the step's recheck of its target: open, no wait, unless told otherwise."""
    return lambda target: {"state": state, "wait_until": wait_until, "notes": []}


def go(rec, got, states=None, gates=None, now=T0 + 700, reader=None):
    """plan at finish, then the continuation unit's step."""
    del LAUNCHES[:]
    lane = (states or states_for(got.get("state")))(None, LOC.lane_tickets_of(rec))
    p = LOC.plan(rec, got, lane, now=now, gates=(gates or Gates()).as_dict())
    if p["act"] == "continue":
        rec = DH.read_record(rec["unit"])
        rec["continue_plan"] = p
        DH.write_record(rec)
        res = LOC.run(rec["unit"], now=now + 30, launch_fn=fake_launch, gates=(gates or Gates()).as_dict(),
                      reader=reader or open_reader())
    elif p["act"] == "alarm":
        res = LOC.alarm(rec, p, now)
    else:
        res = p
    return p, res


def log_text():
    try:
        with open(LOG, encoding="utf-8") as f:
            return f.read()
    except OSError:
        return ""


def test_open_with_note():
    rec = make_run()
    p, res = go(rec, {"state": "claimed", "notes": [note(LEFT, T0 + 500)]})
    check("A: plan continues an open item with a LEFT OPEN note", p["act"] == "continue", str(p))
    check("A: exactly one launch", len(LAUNCHES) == 1, str(LAUNCHES))
    if LAUNCHES:
        L = LAUNCHES[0]
        check("A: same item, model and seat", (L["item"], L["model"], L["seat"]) == (ITEM, "opus", "BENCH"), str(L)[:300])
        check("A: header quotes the LEFT OPEN note", LEFT in L["brief"], L["brief"][:400])
        check("A: the original brief follows the header", "Do the five-step split of the code." in L["brief"])
        check("A: no spend figure in the header", not SPEND.search(L["brief"]), SPEND.search(L["brief"]) and
              L["brief"][max(0, SPEND.search(L["brief"]).start() - 60):SPEND.search(L["brief"]).end() + 60])
        x = L.get("extra") or {}
        check("A: the new run carries the chain from creation", x.get("continued_from") == rec["unit"]
              and x.get("continue_root_item") == ITEM and x.get("continue_n") == 1, str(x))
    old = DH.read_record(rec["unit"])
    check("A: the old record names its continuation", old.get("continued_by") == "rm-detached-bench-cont-1", str(old))
    check("A: a Conductor log line says so", "LEFT OPEN CONTINUE" in log_text() and rec["unit"] in log_text())
    # H: a second pass launches nothing
    del LAUNCHES[:]
    r2 = LOC.run(rec["unit"], now=T0 + 800, launch_fn=fake_launch, gates=Gates().as_dict(), reader=open_reader())
    check("H: a second continuation step launches nothing", not LAUNCHES and r2["act"] != "continued", str(r2))
    hand = make_run(at=T0 + 10)
    p = LOC.plan(hand, {"state": "claimed", "notes": [note(LEFT, T0 + 500)]}, {}, now=T0 + 700, gates=Gates().as_dict())
    rec2 = DH.read_record(hand["unit"])
    rec2["continue_plan"] = p
    DH.write_record(rec2)
    make_run(at=T0 + 650, status="running")     # the Conductor relaunched it by hand first
    del LAUNCHES[:]
    r3 = LOC.run(hand["unit"], now=T0 + 700, launch_fn=fake_launch, gates=Gates().as_dict(), reader=open_reader())
    check("H: a hand relaunch already made means no continuation", not LAUNCHES and "already relaunched" in r3["why"],
          str(r3))
    old_note = make_run()
    p, _ = go(old_note, {"state": "claimed", "notes": [note(LEFT, T0 - 3600)]})
    check("A: a LEFT OPEN note older than the run's start is no reason (the run is owed, the old note not quoted)",
          p.get("kind") == "owed" and not p.get("note"), str(p))


def test_closed():
    rec = make_run()
    p, _ = go(rec, {"state": "done", "notes": [note(LEFT, T0 + 500)]})
    check("B: a closed item is never continued", p["act"] == "none" and not LAUNCHES, str(p))


def test_lane():
    rec = make_run(item=LANE[0], brief=LANE_BRIEF)
    check("C: lane tickets are read off the brief", LOC.lane_tickets_of(rec) == LANE, str(LOC.lane_tickets_of(rec)))
    lane_states = {LANE[0]: "done", LANE[1]: "proposed", LANE[2]: "proposed", LANE[3]: "claimed"}
    p, _ = go(rec, {"state": "done", "notes": []}, states=states_for("done", lane_states))
    check("C: a lane with open tickets is continued", p["act"] == "continue" and len(LAUNCHES) == 1, str(p))
    if LAUNCHES:
        L = LAUNCHES[0]
        check("C: on the first open lane ticket", L["item"] == LANE[1], L["item"])
        check("C: the header lists every open ticket and not the closed one",
              all(t in L["brief"].split("---- the previous run's brief")[0] for t in LANE[1:])
              and LANE[0] not in L["brief"].split("Still open:")[1].split("\n")[0], L["brief"][:600])
    rec2 = make_run(item=LANE[0], brief=LANE_BRIEF)
    p, _ = go(rec2, {"state": "done", "notes": []}, states=states_for("done", {t: "done" for t in LANE}))
    check("C: a lane with every ticket closed is not continued", p["act"] == "none", str(p))
    plain = make_run(brief="Fix it. See also:\n- `OPS_WATCH_FIX_BLIND_READINGS_STILL_ZERO` for context\n")
    check("C: a bulleted id in a brief that is not a lane names no lane", LOC.lane_tickets_of(plain) == [],
          str(LOC.lane_tickets_of(plain)))


def test_limit():
    item = "RIMMANDRAKE_LIMIT_TEST_ITEM_LOOPS"
    for i in range(3):
        make_run(item=item, at=T0 - 3000 + i * 100, continued_from="x%d" % i, continue_root_item=item, continue_n=i + 1)
    rec = make_run(item=item, at=T0, continued_from="x2", continue_root_item=item, continue_n=3)
    open(LOG, "w").close()
    p, res = go(rec, {"state": "claimed", "notes": [dict(note(LEFT, T0 + 500), id=item)]})
    check("D: the fourth in a day is an alarm, not a launch", p["act"] == "alarm" and not LAUNCHES, str(p))
    check("D: the alarm line carries the fixed id", LOC.ALARM_ID in log_text() and item in log_text(), log_text()[-300:])
    # a-killed-continuation-spends-no-slot (failure_class): three continuations killed by a fleet stop are none of the three
    kitem = "RIMMANDRAKE_LIMIT_KILLED_ITEM_FLEET_STOP"
    for i in range(3):
        make_run(item=kitem, at=T0 - 3000 + i * 100, continued_from="k%d" % i, continue_root_item=kitem, continue_n=i + 1,
                 status="finished", result="killed: signal (exited 143)")
    p, _ = go(make_run(item=kitem, at=T0, continued_from="k2", continue_root_item=kitem, continue_n=3),
              {"state": "claimed", "notes": [dict(note(LEFT, T0 + 500), id=kitem)]})
    check("D: a-killed-continuation-spends-no-slot", p["act"] == "continue", str(p))
    old = make_run(item="RIMMANDRAKE_LIMIT_OLD_ITEM_DAY_LATER", at=T0)
    for i in range(3):
        make_run(item=old["item"], at=T0 - 90000 - i, continued_from="y", continue_root_item=old["item"])
    p, _ = go(old, {"state": "claimed", "notes": [dict(note(LEFT, T0 + 500), id=old["item"])]})
    check("D: continuations older than a day do not count", p["act"] == "continue", str(p))


def capped_out():
    return {"type": "result", "subtype": "error_max_budget_usd", "is_error": True, "session_id": "s-1",
            "stopped_by": "spend_watchdog", "result": "Stopped by spend_watchdog."}


CAP_ITEM = "RIMMANDRAKE_CAP_TEST_ITEM_STOPPED_MIDJOB"


def test_capped():
    rec = make_run(item=CAP_ITEM, result="exit-code/claude-error (exited 1)", out=capped_out())
    check("E: the watchdog stop is recognised", LOC.capped(rec), str(rec))
    p, _ = go(rec, {"state": "claimed", "notes": [note(LEFT, T0 + 500)]})
    check("E: a capped run without the opt-in is not continued", p["act"] == "none" and not LAUNCHES, str(p))
    rec = make_run(item=CAP_ITEM, result="exit-code/claude-error (exited 1)", out=capped_out(), continue_on_cap=1,
                   at=T0 + 20000)
    p, _ = go(rec, {"state": "claimed", "notes": []}, now=T0 + 20700)
    check("E: with --continue-on-cap 1 it is continued once", p["act"] == "continue" and len(LAUNCHES) == 1, str(p))
    if LAUNCHES:
        check("E: its header names no spend", not SPEND.search(LAUNCHES[0]["brief"]), LAUNCHES[0]["brief"][:400])
        x = LAUNCHES[0].get("extra") or {}
        check("E: the continuation carries the opt-in used", x.get("continue_on_cap") == 1
              and x.get("cap_continues_used") == 1, str(x))
        nxt = DH.read_record("rm-detached-bench-cont-1")
        nxt.update(result="exit-code/claude-error (exited 1)", status="finished", out=rec["out"], err=rec["err"],
                   brief_src=rec["brief_src"], clone=rec["clone"], ended=T0 + 900)
        DH.write_record(nxt)
        p, _ = go(nxt, {"state": "claimed", "notes": []}, now=T0 + 20950)
        check("E: a second cap stop with the opt-in spent is not continued", p["act"] == "none", str(p))
    failed = make_run(result="exit-code/claude-error (exited 1)")
    p, _ = go(failed, {"state": "claimed", "notes": [note(LEFT, T0 + 500)]})
    check("E: a failed run (not a cap stop) is not continued", p["act"] == "none", str(p))


def test_killed_voided():
    rec = make_run(result="killed: signal (killed TERM)", out={})
    p, _ = go(rec, {"state": "claimed", "notes": [note(LEFT, T0 + 500)]})
    check("F: a killed run is never continued, and says why", p["act"] == "none" and not LAUNCHES
          and p["why"].startswith("killed runs are never continued"), str(p))
    rec = make_run(result="killed: pipe stop --kill", out={}, continue_on_cap=3)
    p, _ = go(rec, {"state": "claimed", "notes": [note(LEFT, T0 + 500)]})
    check("F: a killed run is never continued, opt-in or not", p["act"] == "none" and p["why"].startswith("killed runs are never continued"), str(p))
    rec = make_run()
    p, _ = go(rec, {"state": "claimed", "notes": [note(LEFT, T0 + 500)]}, gates=Gates(voided=[rec["unit"]]))
    check("F: a voided run is never continued", p["act"] == "none" and not LAUNCHES, str(p))


def test_gates():
    env = {"RM_CONTROL_MOD": "Graffiti"}
    for what, g in (("an owner-held mod", Gates(held="HELD BY OWNER: Graffiti")),
                    ("a paused pipeline", Gates(paused="PIPELINE PAUSED (all): by hand")),
                    ("a `pipe off` switch", Gates(blocked="off by control: all"))):
        rec = make_run(env=env)
        p, _ = go(rec, {"state": "claimed", "notes": [note(LEFT, T0 + 500)]}, gates=g)
        check("G: %s is never continued" % what, p["act"] == "none" and not LAUNCHES, str(p))
    # a gate that turns on between finish and the continuation step stops it too
    rec = make_run(env=env)
    p = LOC.plan(rec, {"state": "claimed", "notes": [note(LEFT, T0 + 500)]}, {}, now=T0 + 700, gates=Gates().as_dict())
    rec = DH.read_record(rec["unit"])
    rec["continue_plan"] = p
    DH.write_record(rec)
    del LAUNCHES[:]
    r = LOC.run(rec["unit"], now=T0 + 730, launch_fn=fake_launch, gates=Gates(held="HELD BY OWNER").as_dict(), reader=open_reader())
    check("G: a hold set after finish stops the continuation step", not LAUNCHES and r["act"] == "none", str(r))
    def boom(mod):
        raise RuntimeError("store unreadable")
    g = Gates().as_dict()
    g["paused"] = boom
    rec = make_run(env=env)
    p = LOC.plan(rec, {"state": "claimed", "notes": [note(LEFT, T0 + 500)]}, {}, now=T0 + 700, gates=g)
    check("G: an unreadable gate is a named no, never a launch", p["act"] == "none" and "could not" in p["why"], str(p))


def test_finish_kicks():
    """finish computes the plan with the clone it has and starts the continuation unit only when one is owed."""
    calls = []

    class R(object):
        def __init__(self, out=""):
            self.returncode, self.stdout, self.stderr = 0, out, ""

    def runner(argv, **kw):
        calls.append(list(argv))
        return R("PUBLISHED abcdef1234567")
    clone = os.path.join(TMP, "clones", "finishclone")
    os.makedirs(clone, exist_ok=True)
    for got, want in ((({"state": "claimed", "notes": [note(LEFT, T0 + 500)]}), True),
                      (({"state": "done", "notes": [note(LEFT, T0 + 500)]}), False)):
        del calls[:]
        rec = make_run(status="running", clone=clone)
        rec["status"] = "running"
        rec.pop("result")
        DH.write_record(rec)
        kicked = []
        DH.finish(rec["unit"], now=T0 + 700, env={"SERVICE_RESULT": "success", "EXIT_CODE": "exited", "EXIT_STATUS": "0"},
                  runner=runner, item_reader=lambda c, i, g=got: g, waker=lambda *a: None,
                  continuer=lambda r, p: kicked.append((r["unit"], p["act"])) or "continue kicked")
        after = DH.read_record(rec["unit"])
        check("I: finish %s the continuation (%s)" % ("kicks" if want else "does not kick", got["state"]),
              bool(kicked) == want and (after.get("continue_plan", {}).get("act") == "continue") == want,
              "%s %s" % (kicked, after.get("continue_plan")))
    argv = LOC.kick_argv({"unit": "rm-detached-bench-x-1", "state": STATE, "seat": "BENCH", "clone": clone})
    check("I: the kick is its own --no-block unit running `run --unit`",
          "--no-block" in argv and "--unit" not in argv[:argv.index("--")] and argv[-3:] == ["run", "--unit",
                                                                                             "rm-detached-bench-x-1"],
          str(argv))
    scripts = argv[argv.index("-c") + 2:len(argv) - 1 - argv[::-1].index("--")]     # the resolver's own `--`
    check("I: the step never runs first from the run's own clone (its return deletes it)",
          scripts and not scripts[0].startswith(clone + "/"), str(scripts))


def test_launch_records_opt_in():
    calls = []

    class R(object):
        returncode, stdout, stderr = 0, "", ""

    def runner(argv, **kw):
        calls.append(argv)
        if argv[:2] == ["git", "grep"]:     # the origin check: the item is filed on origin/main
            r = R()
            r.stdout = json.dumps({"seat": "BENCH", "event": "file", "id": ITEM}, separators=(",", ":"))
            return r
        return R()
    clone = os.path.join(TMP, "clones", "launchclone")
    os.makedirs(clone, exist_ok=True)
    os.makedirs(os.path.join(clone, "src", "RimMandrake", "Utils"), exist_ok=True)   # a clone a unit can start in
    open(os.path.join(clone, "src", "RimMandrake", "Utils", "claude_bounded.sh"), "w").close()
    import role_launch
    import subprocess
    orig = role_launch.unit_state
    role_launch.unit_state = lambda unit, runner=subprocess.run: "not-found"
    try:
        rc, text = DH.launch("BENCH", ITEM, "Build it.", "opus", None, 5, now=T0 + 5000, runner=runner, known={ITEM},
                             clone=clone, skip_launch_checks="selftest", extra={"continue_on_cap": 2})
    finally:
        role_launch.unit_state = orig
    m = re.match(r"DETACHED (\S+)", text or "")
    rec = DH.read_record(m.group(1)) if m else {}
    check("I: launch records --continue-on-cap on the run", rc == 0 and rec.get("continue_on_cap") == 2, text[:300])
    out = []
    import io
    import contextlib
    try:
        with contextlib.redirect_stderr(io.StringIO()):
            DH.main(["launch", "--seat", "BENCH", "--item", "NOPE_NOT_AN_ITEM_HERE", "--brief", "b",
                     "--continue-on-cap", "x"])
    except SystemExit as e:
        out.append(e.code)
    check("I: --continue-on-cap takes a number", out == [2], str(out))


def test_waiting():
    """A LEFT OPEN item under a dated `rimflow wait` still ahead is not continued; past its date it is."""
    rec = make_run(at=T0 + 20)
    got = {"state": "doing", "notes": [note(LEFT, T0 + 500)], "wait_until": DH.iso(T0 + 3 * 86400)}
    p = LOC.plan(rec, got, {}, now=T0 + 700, gates=Gates().as_dict())
    check("W: a running wait plans no continuation", p["act"] == "none" and "wait" in p["why"], str(p))
    got["wait_until"] = DH.iso(T0 + 600)
    p = LOC.plan(make_run(at=T0 + 21), got, {}, now=T0 + 700, gates=Gates().as_dict())
    check("W: a wait past its date continues", p["act"] == "continue", str(p))


# ---------------------------------------------------------------- design/specs/2026-11-19-run-end-continue/boundary.md
OWED_ITEM = "RIMMANDRAKE_OWED_TEST_ITEM_LEFT_SILENT"


def t_an_owed_run_is_continued_to_close_or_say():
    rec = make_run(item=OWED_ITEM, at=T0 + 40000)
    p, _ = go(rec, {"state": "claimed", "notes": []}, now=T0 + 40700)
    check("an-owed-run-is-continued-to-close-or-say: planned", p["act"] == "continue" and p.get("kind") == "owed",
          str(p))
    check("an-owed-run-is-continued-to-close-or-say: one launch", len(LAUNCHES) == 1, str(LAUNCHES)[:300])
    if LAUNCHES:
        L = LAUNCHES[0]
        head = L["brief"].split("---- the previous run's brief")[0]
        check("an-owed-run-is-continued-to-close-or-say: the header asks for a close on its sha or a LEFT OPEN note",
              "--sha" in head and "LEFT OPEN:" in head and "nothing" in head.lower(), head)
        check("an-owed-run-is-continued-to-close-or-say: no spend in the header", not SPEND.search(head), head)
        check("an-owed-run-is-continued-to-close-or-say: the new run is of kind owed",
              (L.get("extra") or {}).get("continue_kind") == "owed", str(L.get("extra")))


def t_an_owed_continuation_that_ends_owed_again_is_an_alarm():
    rec = {"unit": "rm-detached-bench-owed-first"}
    again = make_run(item=OWED_ITEM + "_AGAIN", at=T0 + 41000, continued_from=rec["unit"], continue_kind="owed",
                     continue_root_item=OWED_ITEM + "_AGAIN", continue_n=1)
    open(LOG, "w").close()
    p, _ = go(again, {"state": "claimed", "notes": []}, now=T0 + 41700)
    check("an-owed-continuation-that-ends-owed-again-is-an-alarm", p["act"] == "alarm" and not LAUNCHES
          and LOC.ALARM_ID in log_text(), "%s | %s" % (p, log_text()[-200:]))


def t_a_left_open_in_the_result_counts_as_the_note():
    text = ("Did step one. Spend was about $6.3 of the $20 bound. LEFT OPEN: step 2 is not done. It used 2,298,311 "
            "weighted tokens. Then step 3 needs a live visit.")
    rec = make_run(item=OWED_ITEM + "_RES", at=T0 + 42000, out={"result": text, "usage": {}})
    check("a-left-open-in-the-result-counts-as-the-note: owed_close says nothing",
          DH.owed_close(rec, "claimed", []) == "", DH.owed_close(rec, "claimed", []))
    p, _ = go(rec, {"state": "claimed", "notes": []}, now=T0 + 42700)
    check("a-left-open-in-the-result-counts-as-the-note: continued, not as owed",
          p["act"] == "continue" and p.get("kind") != "owed", str(p))
    if LAUNCHES:
        head = LAUNCHES[0]["brief"].split("---- the previous run's brief")[0]
        check("a-left-open-in-the-result-counts-as-the-note: the header quotes it",
              "step 2 is not done" in head and "needs a live visit" in head, head)
        check("a-left-open-in-the-result-counts-as-the-note: without its spend sentences",
              "$" not in head and "weighted tokens" not in head and "Did step one" not in head, head)


def t_a_left_open_mention_inside_a_sentence_is_not_a_note():
    """RIMMANDRAKE_FIX_LEFT_OPEN_PARSE_READS_ITS_OWN_DENIAL: run ...-1795144073 wrote "(no `LEFT OPEN:` note; ...)" and
    was continued with the carry-on brief, quoting its own denial. Red on db268445c0 (3 of 6)."""
    cases = [
        ("stays `doing` (no `LEFT OPEN:` note; its summary is below).", ""),
        ("LEFT OPEN: rerun mutants\nstill owed\n\nbye", "LEFT OPEN: rerun mutants\nstill owed"),
        ("Done.\n\nLEFT OPEN: two tickets\n\nend", "LEFT OPEN: two tickets"),
        ("Done.\n**LEFT OPEN:** two tickets", "**LEFT OPEN:** two tickets"),
        ("mentions no `LEFT OPEN:` note.\n\nLEFT OPEN: real one", "LEFT OPEN: real one"),
        ("", ""),
    ]
    for text, want in cases:
        rec = make_run(item=OWED_ITEM + "_DENY", at=T0 + 42900, out={"result": text, "usage": {}})
        got = DH.result_left_open(rec)
        check("a-left-open-in-the-result-counts-as-the-note: %r -> %r" % (text[:30], want[:30]), got == want,
              repr(got[:80]))
    rec = make_run(item=OWED_ITEM + "_DENY", at=T0 + 42900,
                   out={"result": "Item stays `doing` (no `LEFT OPEN:` note; its summary is below).", "usage": {}})
    check("a-left-open-in-the-result-counts-as-the-note: a denial leaves the run owed",
          DH.owed_close(rec, "claimed", []) != "", "owed_close said nothing")


def _transcript(clone, sid, turns):
    """A session transcript in the shape claude writes: each turn's assistant text, then a stop_hook_summary."""
    cfg = os.path.join(TMP, "claude_cfg")
    d = os.path.join(cfg, "projects", re.sub(r"[^A-Za-z0-9]", "-", clone))
    os.makedirs(d, exist_ok=True)
    with open(os.path.join(d, sid + ".jsonl"), "w", encoding="utf-8") as f:
        for i, text in enumerate(turns):
            if i:
                f.write(json.dumps({"type": "user", "message": {"role": "user", "content": "<task-notification>"}})
                        + "\n")
            f.write(json.dumps({"type": "assistant", "isSidechain": False, "message": {"role": "assistant",
                    "content": [{"type": "tool_use", "name": "Bash", "input": {}}]}}) + "\n")
            f.write(json.dumps({"type": "assistant", "isSidechain": False, "message": {"role": "assistant",
                    "content": [{"type": "text", "text": text}]}}) + "\n")
            f.write(json.dumps({"type": "system", "subtype": "stop_hook_summary"}) + "\n")
    return cfg


def t_a_late_remark_keeps_the_report():
    """RIMMANDRAKE_KEEP_RUN_REPORT_WHEN_LATE_REMARK_FOLLOWS: two runs of 2026-11-19 (8:15 and 8:41 PM PST) wrote a full
    report, then a background watch ended and the run said one more line; out.json held only that line."""
    report = "Done: four items closed.\n\nLEFT OPEN: the in-game visit is owed."
    late = "The background wait loop was stopped at its time limit. It doesn't matter."
    item = OWED_ITEM + "_LATE"
    clone = os.path.join(TMP, "clones", item + ".det")
    cfg = _transcript(clone, "sess-late-1", [report, late])
    old = os.environ.get("CLAUDE_CONFIG_DIR")
    os.environ["CLAUDE_CONFIG_DIR"] = cfg
    try:
        rec = make_run(item=item, at=T0 + 43500, out={"result": late, "result_index": 1, "session_id": "sess-late-1",
                                                      "usage": {}})
        got = DH.run_report(rec) if hasattr(DH, "run_report") else ""
        check("a-late-remark-keeps-the-report: the report comes first, then the late line",
              got.startswith("Done: four items closed.") and got.rstrip().endswith("It doesn't matter."), repr(got))
        check("a-late-remark-keeps-the-report: its LEFT OPEN is read", DH.result_left_open(rec).startswith(
              "LEFT OPEN: the in-game visit is owed."), repr(DH.result_left_open(rec)))
        tail = DH.outcome(rec, {"SERVICE_RESULT": "success", "EXIT_CODE": "exited", "EXIT_STATUS": "0"})[2]
        check("a-late-remark-keeps-the-report: the ended line carries the report", "four items closed" in tail, tail)
        one = make_run(item=item, at=T0 + 43600, out={"result": "only turn", "session_id": "sess-none", "usage": {}})
        check("a-late-remark-keeps-the-report: a one-turn run reads its result as before",
              (DH.run_report(one) if hasattr(DH, "run_report") else "") == "only turn")
        lost = make_run(item=item, at=T0 + 43700, out={"result": late, "result_index": 1, "session_id": "sess-gone",
                                                       "usage": {}})
        got = DH.run_report(lost) if hasattr(DH, "run_report") else ""
        check("a-late-remark-keeps-the-report: an unreadable transcript says so beside the last result",
              late in got and "UNMEASURED" in got, repr(got))
    finally:
        if old is None:
            os.environ.pop("CLAUDE_CONFIG_DIR", None)
        else:
            os.environ["CLAUDE_CONFIG_DIR"] = old


def t_a_lane_ticket_under_a_running_wait_is_skipped():
    future, past = DH.iso(T0 + 9 * 86400), DH.iso(T0 - 600)
    rec = make_run(item=LANE[0], brief=LANE_BRIEF, at=T0 + 43000)
    lane_states = {LANE[0]: "done", LANE[1]: {"state": "proposed", "wait_until": future},
                   LANE[2]: {"state": "proposed", "wait_until": past}, LANE[3]: "claimed"}
    p, _ = go(rec, {"state": "done", "notes": []}, states=states_for("done", lane_states), now=T0 + 43700)
    check("a-lane-ticket-under-a-running-wait-is-skipped: the next unwaited ticket", p.get("target") == LANE[2], str(p))
    rec = make_run(item=LANE[0], brief=LANE_BRIEF, at=T0 + 44000)
    waiting = {LANE[0]: "done"}
    waiting.update({t: {"state": "proposed", "wait_until": future} for t in LANE[1:]})
    p, _ = go(rec, {"state": "done", "notes": []}, states=states_for("done", waiting), now=T0 + 44700)
    check("a-lane-ticket-under-a-running-wait-is-skipped: every one waits -> none", p["act"] == "none"
          and "wait" in p["why"] and not LAUNCHES, str(p))


def _planned(rec, got, lane=None, now=T0 + 700):
    p = LOC.plan(rec, got, lane or {}, now=now, gates=Gates().as_dict())
    r = DH.read_record(rec["unit"])
    r["continue_plan"] = p
    DH.write_record(r)
    del LAUNCHES[:]
    return p


def t_the_step_rereads_the_target_before_launch():
    for what, reader, want in (("closed since", open_reader("done"), "done"),
                               ("now waiting", open_reader("claimed", DH.iso(T0 + 9 * 86400)), "wait"),
                               ("unreadable", lambda t: None, "could not")):
        rec = make_run(at=T0 + 45000)
        _planned(rec, {"state": "claimed", "notes": [note(LEFT, T0 + 45500)]}, now=T0 + 45700)
        r = LOC.run(rec["unit"], now=T0 + 45730, launch_fn=fake_launch, gates=Gates().as_dict(), reader=reader)
        check("the-step-rereads-the-target-before-launch: %s" % what, not LAUNCHES and r["act"] == "none"
              and want in r["why"], str(r))


def t_launch_checks_are_skipped_only_for_the_same_item():
    rec = make_run(item=LANE[0], brief=LANE_BRIEF, at=T0 + 46000)
    lane_states = {LANE[0]: "done", LANE[1]: "proposed", LANE[2]: "proposed", LANE[3]: "claimed"}
    go(rec, {"state": "done", "notes": []}, states=states_for("done", lane_states), now=T0 + 46700)
    check("launch-checks-are-skipped-only-for-the-same-item: another ticket runs its checks",
          LAUNCHES and LAUNCHES[0]["item"] == LANE[1] and not LAUNCHES[0].get("skip_launch_checks"),
          str(LAUNCHES and LAUNCHES[0].get("skip_launch_checks")))
    rec = make_run(at=T0 + 47000)
    go(rec, {"state": "claimed", "notes": [note(LEFT, T0 + 47500)]}, now=T0 + 47700)
    check("launch-checks-are-skipped-only-for-the-same-item: its own item skips them",
          LAUNCHES and LAUNCHES[0].get("skip_launch_checks"), str(LAUNCHES[:1])[:200])


def t_an_open_lane_item_is_its_own_target():
    own = "RIMMANDRAKE_LANE_OWN_ITEM_STILL_OPEN"
    rec = make_run(item=own, brief=LANE_BRIEF, at=T0 + 48000)
    lane_states = {LANE[0]: "done", LANE[1]: "proposed", LANE[2]: "proposed", LANE[3]: "claimed"}
    p, _ = go(rec, {"state": "claimed", "notes": []}, states=states_for("claimed", lane_states), now=T0 + 48700)
    check("an-open-lane-item-is-its-own-target", p.get("target") == own and LAUNCHES
          and LANE[1] in LAUNCHES[0]["brief"].split("---- the previous run's brief")[0], str(p))


def t_a_refused_continuation_spends_no_daily_slot():
    item = "RIMMANDRAKE_REFUSED_SLOTS_TEST_ITEM_THREE"
    for i, st in enumerate(("refused", "launch_failed", "refused")):
        make_run(item=item, at=T0 + 49000 + i, continued_from="z%d" % i, continue_root_item=item, status=st)
    rec = make_run(item=item, at=T0 + 49100)
    p, _ = go(rec, {"state": "claimed", "notes": [dict(note(LEFT, T0 + 49500), id=item)]}, now=T0 + 49700)
    check("a-refused-continuation-spends-no-daily-slot", p["act"] == "continue", str(p))


def t_an_alarm_whose_log_write_failed_is_retried():
    rec = make_run(item="RIMMANDRAKE_ALARM_RETRY_TEST_ITEM_LOG_DOWN", at=T0 + 50000)
    p = {"unit": rec["unit"], "item": rec["item"], "act": "alarm", "why": "test"}
    orig = DH.conductor_line

    def down(*a, **k):
        raise OSError("disk full")
    DH.conductor_line = down
    try:
        r = LOC.alarm(rec, p, T0 + 50700)
    finally:
        DH.conductor_line = orig
    after = DH.read_record(rec["unit"])
    check("an-alarm-whose-log-write-failed-is-retried: no alarm mark", r["act"] == "alarm_failed"
          and not after.get("continue_alarm") and "disk full" in str(r), "%s %s" % (r, after.get("continue_alarm")))
    r = LOC.alarm(rec, p, T0 + 50800)
    check("an-alarm-whose-log-write-failed-is-retried: the next pass raises it", r["act"] == "alarmed"
          and DH.read_record(rec["unit"]).get("continue_alarm"), str(r))


def t_the_alarm_honours_the_run_root():
    rec = make_run(item="RIMMANDRAKE_ALARM_ROOT_TEST_ITEM_ELSEWHERE", at=T0 + 50050)
    p = {"unit": rec["unit"], "item": rec["item"], "act": "alarm", "why": "test"}
    root = tempfile.mkdtemp(prefix="loc_root_")
    rr = dict(rec, unit="rm-detached-bench-rootonly-1")
    DH.write_record(rr, root)
    LOC.alarm(rr, dict(p, unit=rr["unit"]), T0 + 50900, root=root)
    check("the-alarm-honours-the-run-root", (DH.read_record(rr["unit"], root) or {}).get("continue_alarm")
          and DH.read_record(rr["unit"]) is None
          and os.path.exists(os.path.join(DH.runs_dir(root), "left_open_continue.jsonl")), root)


def t_the_run_end_note_carries_no_spend_sentence():
    calls = []

    class R(object):
        returncode, stdout, stderr = 0, "PUBLISHED abcdef1234567", ""

    def runner(argv, **kw):
        calls.append(list(argv))
        return R()
    clone = os.path.join(TMP, "clones", "notespend")
    os.makedirs(clone, exist_ok=True)
    rec = make_run(status="running", clone=clone, at=T0 + 51000,
                   out={"result": "Visit 1 ran. Spend was about $21.6 of the $30 budget. Record at 99ff70d.", "usage": {}})
    rec.pop("result")
    DH.write_record(rec)
    DH.finish(rec["unit"], now=T0 + 51700, env={"SERVICE_RESULT": "success", "EXIT_CODE": "exited", "EXIT_STATUS": "0"},
              runner=runner, item_reader=lambda c, i: {"state": "done", "notes": []}, waker=lambda *a: None,
              continuer=lambda r, p: "none")
    notes = [a[a.index("--text") + 1] for a in calls if "note" in a and "--text" in a]
    check("the-run-end-note-carries-no-spend-sentence", notes and "Record at 99ff70d" in notes[0]
          and "$" not in notes[0] and "budget" not in notes[0], str(notes)[:300])


# ---- resume of the ended session (RIMMANDRAKE_LAUNCH_SIX_CONTEXT_KEEPING_CHANGES_FROM_THE_SCAN, report change 1)
PROJECTS = os.path.join(TMP, "projects")
SID = "11111111-2222-3333-4444-555555555555"


def resumable(**kw):
    """A run record on an item of its own (an earlier case's later run on ITEM would read as a relaunch)."""
    N[0] += 1
    kw.setdefault("item", "RIMMANDRAKE_RESUME_CASE_%d_OF_THE_SCAN" % N[0])
    return make_run(at=T0, **kw)


def plant_session(sid=SID, context=300000):
    """A transcript under the fake projects dir whose last main-thread turn read `context` tokens (None: no usage)."""
    d = os.path.join(PROJECTS, "-old-clone")
    os.makedirs(d, exist_ok=True)
    with open(os.path.join(d, sid + ".jsonl"), "w", encoding="utf-8") as f:
        f.write(json.dumps({"type": "user", "message": {"content": "brief"}}) + "\n")
        if context is not None:
            f.write(json.dumps({"type": "assistant", "message": {"usage": {
                "input_tokens": 10, "cache_creation_input_tokens": 0, "cache_read_input_tokens": context - 20,
                "output_tokens": 10}}}) + "\n")
            f.write(json.dumps({"type": "assistant", "isSidechain": True, "message": {"usage": {
                "input_tokens": 999999}}}) + "\n")


def clear_continuations():
    """Each case stands alone: the fake launches of earlier cases (same item, later start) would read as a relaunch."""
    import glob
    for f in glob.glob(os.path.join(DH.runs_dir(), "rm-detached-bench-cont-*.json")):
        os.remove(f)


def resume_go(rec, now):
    """plan at finish (gap 100 s), then the step at `now`, with the fake projects dir."""
    clear_continuations()
    del LAUNCHES[:]
    got = {"state": "claimed", "notes": [dict(note(LEFT, T0 + 300), id=rec["item"])]}
    p = LOC.plan(rec, got, {}, now=T0 + 700, gates=Gates().as_dict())
    rec = DH.read_record(rec["unit"])
    rec["continue_plan"] = p
    DH.write_record(rec)
    return LOC.run(rec["unit"], now=now, launch_fn=fake_launch, gates=Gates().as_dict(), reader=open_reader(),
                   projects=PROJECTS)


# the resume-or-fresh choice: selftest_continuation_progress.py (design/specs/2026-11-21-live-sitting-context-burn/boundary.md)


def t_a_blind_role_never_resumes():
    plant_session(context=100000)
    cases = [("blind_challenge stage", dict(env={"RM_CONTROL_MOD": "Pyrelands", "RM_CONTROL_STAGE": "blind_challenge"})),
             ("BLIND judge item", dict(item="RIMMANDRAKE_JUDGE_PYRELANDS_BLIND_CYCLE_TWO")),
             ("fresh reader brief", dict(brief="# Fresh read of the probe page\n\nYou are a detached reader for the Conductor.")),
             ("second reader brief", dict(brief="# Second reader: check the rewritten designs\n\nRead them.")),
             ("examiner brief", dict(brief="# Exam\n\nYou are the examiner of this design; you did not write it.")),
             ("challenger brief", dict(brief="# Challenge\n\nYou are a blind challenger of the Designer's draft.")),
             ("coverage judge brief", dict(brief="# Coverage\n\nYou are the coverage judge of FlowWorks.")),
             ("judge brief", dict(brief="# Label claims\n\nYou are a detached judge for the Conductor."))]
    for name, kw in cases:
        rec = resumable(session=SID, **kw)
        r = resume_go(rec, T0 + 660)
        L = LAUNCHES[-1] if LAUNCHES else {}
        ex = L.get("extra") or {}
        check("blind (%s): continued fresh" % name, r.get("act") == "continued" and not L.get("resume_session"),
              str((r, L.get("resume_session"))))
        check("blind (%s): why names the blind role" % name, "blind role" in str(ex.get("continue_fresh_why")), str(ex))
    # a builder whose brief only mentions a coverage judge as its subject is not a blind role
    rec = resumable(session=SID, brief="# Prove two coverage-judge faults\n\nYou are a detached builder. Fix the "
                                      "coverage judge's blind spot.")
    resume_go(rec, T0 + 660)
    check("a builder about the coverage judge still resumes", LAUNCHES and LAUNCHES[-1].get("resume_session") == SID,
          str(LAUNCHES[-1].get("extra") if LAUNCHES else None))


def main():
    for t in (test_open_with_note, test_closed, test_lane, test_limit, test_capped, test_killed_voided, test_gates,
              test_finish_kicks, test_launch_records_opt_in, test_waiting,
              t_an_owed_run_is_continued_to_close_or_say, t_an_owed_continuation_that_ends_owed_again_is_an_alarm,
              t_a_left_open_in_the_result_counts_as_the_note, t_a_left_open_mention_inside_a_sentence_is_not_a_note,
              t_a_late_remark_keeps_the_report,
              t_a_lane_ticket_under_a_running_wait_is_skipped,
              t_the_step_rereads_the_target_before_launch, t_launch_checks_are_skipped_only_for_the_same_item,
              t_an_open_lane_item_is_its_own_target, t_a_refused_continuation_spends_no_daily_slot,
              t_an_alarm_whose_log_write_failed_is_retried, t_the_alarm_honours_the_run_root,
              t_the_run_end_note_carries_no_spend_sentence, t_a_blind_role_never_resumes):
        try:
            t()
        except Exception as e:  # noqa: BLE001
            import traceback
            traceback.print_exc()
            check(t.__name__ + " raised", False, "%s: %s" % (type(e).__name__, e))
    print("selftest_left_open_continue: %s (%d failed)" % ("FAIL" if FAILS else "PASS", len(FAILS)))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
