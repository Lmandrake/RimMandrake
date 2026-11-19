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


def go(rec, got, states=None, gates=None, now=T0 + 700):
    """plan at finish, then the continuation unit's step."""
    del LAUNCHES[:]
    lane = (states or states_for(got.get("state")))(None, LOC.lane_tickets_of(rec))
    p = LOC.plan(rec, got, lane, now=now, gates=(gates or Gates()).as_dict())
    if p["act"] == "continue":
        rec = DH.read_record(rec["unit"])
        rec["continue_plan"] = p
        DH.write_record(rec)
        res = LOC.run(rec["unit"], now=now + 30, launch_fn=fake_launch, gates=(gates or Gates()).as_dict())
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
    r2 = LOC.run(rec["unit"], now=T0 + 800, launch_fn=fake_launch, gates=Gates().as_dict())
    check("H: a second continuation step launches nothing", not LAUNCHES and r2["act"] != "continued", str(r2))
    hand = make_run(at=T0 + 10)
    p = LOC.plan(hand, {"state": "claimed", "notes": [note(LEFT, T0 + 500)]}, {}, now=T0 + 700, gates=Gates().as_dict())
    rec2 = DH.read_record(hand["unit"])
    rec2["continue_plan"] = p
    DH.write_record(rec2)
    make_run(at=T0 + 650, status="running")     # the Conductor relaunched it by hand first
    del LAUNCHES[:]
    r3 = LOC.run(hand["unit"], now=T0 + 700, launch_fn=fake_launch, gates=Gates().as_dict())
    check("H: a hand relaunch already made means no continuation", not LAUNCHES and "already relaunched" in r3["why"],
          str(r3))
    old_note = make_run()
    p, _ = go(old_note, {"state": "claimed", "notes": [note(LEFT, T0 - 3600)]})
    check("A: a LEFT OPEN note older than the run's start is no reason", p["act"] == "none", str(p))
    nothing = make_run()
    p, _ = go(nothing, {"state": "claimed", "notes": []})
    check("A: open item with no note and no lane is not continued (finish flags it OWED)", p["act"] == "none", str(p))


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
    r = LOC.run(rec["unit"], now=T0 + 730, launch_fn=fake_launch, gates=Gates(held="HELD BY OWNER").as_dict())
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


def main():
    for t in (test_open_with_note, test_closed, test_lane, test_limit, test_capped, test_killed_voided, test_gates,
              test_finish_kicks, test_launch_records_opt_in, test_waiting):
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
