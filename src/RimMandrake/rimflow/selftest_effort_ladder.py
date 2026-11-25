#!/usr/bin/env python3
"""selftest_effort_ladder: each promise of design/specs/2026-11-25-effort-ladder/boundary.md
(RIMMANDRAKE_PASS_EFFORT_ON_EVERY_LAUNCH_STEVEDESKTOP_RAN_MEDIUM). Owner by card 2026-11-25: "No medium anywhere";
"Effort up, then model up"; a Fable run on stuck work: "High".

Hermetic for the ladder (a temp run-record dir, a temp Conductor log, a fake launch, fake gates and a fake projects
dir); the tree check reads this repo as ./publish does.
"""
import json
import os
import re
import stat
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
UTILS = os.path.join(HERE, "..", "Utils")
TMP = tempfile.mkdtemp(prefix="selftest_effort_ladder_")
os.environ["RM_DISPATCHER_STATE"] = os.path.join(TMP, "state")
os.environ["RM_CONDUCTOR_LOG"] = os.path.join(TMP, "conductor.md")
os.environ.setdefault("RM_UNDER_SELFTEST", "1")
sys.path.insert(0, HERE)
sys.path.insert(1, UTILS)
import effort as EF  # noqa: E402
import launch_permissions as LP  # noqa: E402
import detached_helper as DH  # noqa: E402
import left_open_continue as LOC  # noqa: E402
import time_budget  # noqa: E402  the one hang-guard class (Utils/time_budget.py)

BAD = []
T0 = 1_800_000_000.0
STATE = os.environ["RM_DISPATCHER_STATE"]
LOG = os.environ["RM_CONDUCTOR_LOG"]
PROJECTS = os.path.join(TMP, "projects")
SID = "aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee"


def check(name, ok, got=""):
    print("%s %s%s" % ("PASS" if ok else "FAIL", name, "" if ok else "  got: %s" % (str(got)[:600],)))
    if not ok:
        BAD.append(name)


def raises(f):
    try:
        f()
    except EF.UnderFloor:
        return True
    return False


# ---------------------------------------------------------------- Part 1: the table and the reader
def t_one_table_floor_high():
    check("each model reads high", [EF.level(m) for m in ("sonnet", "opus", "claude-fable-5-2", "fable", None)]
          == ["high"] * 5)
    check("the table names every tier and a default, all at or over the floor",
          {"default", "sonnet", "opus", "fable"} <= set(EF.EFFORT) and not EF.check_table())
    check("a table with medium in it is refused by name", any("medium" in x for x in EF.check_table({"default": "high",
                                                                                                    "opus": "medium"})))
    check("a call at medium or low is refused", raises(lambda: EF.effort_args("opus", "medium"))
          and raises(lambda: EF.level(None, "low")) and raises(lambda: EF.level(None, "turbo")))
    check("the argv words", EF.effort_args("opus") == ["--effort", "high"] and EF.effort_args("x", "xhigh") ==
          ["--effort", "xhigh"])
    r = subprocess.run([sys.executable, os.path.join(HERE, "effort.py"), "level", "--model", "sonnet"],
                       capture_output=True, text=True, timeout=time_budget.CALL_S)
    check("the shell's door prints the level", r.returncode == 0 and r.stdout.strip() == "high", (r.returncode, r.stdout))
    check("the ladder's steps: high -> xhigh -> none; sonnet -> opus -> Fable 5.2 by its full name -> none",
          (EF.up("high"), EF.up("xhigh"), EF.model_up("sonnet"), EF.model_up("opus"), EF.model_up("claude-fable-5-2"))
          == ("xhigh", None, "opus", "claude-fable-5-2", None))


def pyv(src):
    return [v for _l, v in LP.Py(src, "x.py").effort_sites()]


def shv(src):
    return [v for _l, v in LP.shell_effort_sites(src)]


E, NE = "EFFORT", "NO EFFORT"


def t_a_launch_without_effort_is_red():
    F = LP.FLAG
    check("an argv with no --effort is red", pyv('run(["claude", "-p", q, "%s"])' % F) == [NE], pyv('run(["claude", "-p", q])'))
    check("an argv with it is green", pyv('run(["claude", "-p", q, "--effort", "high", "%s"])' % F) == [E])
    check("an argv that adds the table's words is green",
          pyv('import effort as EF\nrun(["claude", "-p", q, "%s"] + EF.effort_args("opus"))' % F) == [E]
          and pyv('def f(m):\n cmd = ["claude", "-p", q, "%s"]\n cmd += EF.effort_args(m)\n run(cmd)' % F) == [E])
    check("words added on one branch only are red",
          pyv('def f(a):\n cmd = ["claude", "-p", q]\n if a:\n  cmd += EF.effort_args(m)\n run(cmd)') == [NE])
    check("a command text with no --effort is red, with it green",
          pyv('exe = shutil.which("claude")\nc = "%s -p \\"$(cat %s)\\" ' + F + '" % (exe, b)') == [NE]
          and pyv('exe = shutil.which("claude")\nc = "%s -p \\"$(cat %s)\\" --effort %s ' + F + '" % (exe, b, EF.level())')
          == [E], (pyv('exe = shutil.which("claude")\nc = "%s -p \\"$(cat %s)\\" ' + F + '" % (exe, b)')))
    check("a shell line with no --effort is red, with it green",
          shv('claude -p "$x" %s\n' % F) == [NE] and shv('claude -p "$x" --effort "$(python3 e.py level)" %s\n' % F) == [E])
    check("auth, /usage and the remote-control server are not counted",
          pyv('run(["claude", "auth", "status"])\nrun(["claude", "-p", "/usage"])') == []
          and shv("claude_bounded.sh remote-control --name 'S' --permission-mode bypassPermissions\n") == [])
    check("exit: no effort 1, could not look 3, all good 0",
          (LP.effort_code([E, NE]), LP.effort_code([E, LP.BLIND]), LP.effort_code([E])) == (1, 3, 0))


ROWS = []


def t_every_launch_in_this_tree_states_effort():
    if not ROWS:
        ROWS.extend(LP.effort_scan())
    bad = ["%s:%s %s %s" % r for r in ROWS if r[2] not in (E, LP.EXCEPTION)]
    check("every launch in this repo states --effort (fix: add EF.effort_args(model) to the line named)", not bad, bad)
    seen = {p for p, _l, v, _w in ROWS if v == E}
    KNOWN = {"src/RimMandrake/" + x for x in ("rimflow/detached_helper.py", "rimflow/role_launch.py",
                                             "rimflow/modledger_reader.py", "rimflow/stop_rule_calibration.py",
                                             "Utils/guiding_prose.py")}
    check("the reader sees the launches the brief named (a reader gone blind is red)", KNOWN <= seen, KNOWN - seen)
    for p in sorted(seen):
        with open(os.path.join(LP.ROOT, p), encoding="utf-8") as f:
            mut = re.sub(r"\beffort_args\(", "other_args(", f.read()).replace("--effort", "--verbose")
        vs = [v for _l, v in (LP.Py(mut, p).effort_sites() if p.endswith(".py") else LP.shell_effort_sites(mut))]
        check("with --effort taken out, %s is red" % p, E not in vs and NE in vs, vs)


def t_the_detached_record_keeps_effort():
    rec = {"clone": TMP, "unit": "rm-detached-x", "seat": "BENCH", "item": "X", "model": "opus", "max_s": None,
           "budget_usd": 0.0, "out": "/dev/null", "err": "/dev/null", "state": STATE}
    argv = DH.launch_argv(dict(rec, effort="xhigh"), "go", "/bin/true")
    check("the run's command carries the record's effort", "--effort xhigh" in " ".join(argv), argv)
    check("a record with no effort takes the table's", "--effort high" in " ".join(DH.launch_argv(rec, "go", "/bin/true"))
          and DH.effort_of(rec) == "high")
    got = []
    real = DH.launch
    DH.launch = lambda *a, **k: (got.append(k) or (0, "DETACHED rm-detached-fake"))
    try:
        from contextlib import redirect_stdout
        import io
        with redirect_stdout(io.StringIO()):
            rc_ok = DH.main(["launch", "--seat", "BENCH", "--item", "X", "--brief", "b", "--budget-usd", "0",
                             "--effort", "xhigh"])
        with redirect_stdout(io.StringIO()) as o:
            rc_bad = DH.main(["launch", "--seat", "BENCH", "--item", "X", "--brief", "b", "--budget-usd", "0",
                              "--effort", "medium"])
    finally:
        DH.launch = real
    check("launch --effort xhigh reaches the record", rc_ok == 0 and got and (got[0].get("extra") or {}).get("effort")
          == "xhigh", got)
    check("launch --effort medium is refused before anything starts", rc_bad == 2 and len(got) == 1
          and "floor" in o.getvalue(), (rc_bad, o.getvalue()))


def t_the_one_launcher_adds_a_forgotten_effort():
    with tempfile.TemporaryDirectory() as d:
        for n, body in (("claude", '#!/bin/sh\nprintf "%s\\n" "$@"\n'), ("systemd-run", "#!/bin/sh\nexit 1\n"),
                        ("systemctl", "#!/bin/sh\nexit 0\n"), ("sleep", "#!/bin/sh\nexit 0\n")):
            with open(os.path.join(d, n), "w") as f:
                f.write(body)
            os.chmod(os.path.join(d, n), stat.S_IRWXU)

        def bounded(*a):
            r = subprocess.run(["bash", os.path.join(UTILS, "claude_bounded.sh"), *a], capture_output=True, text=True,
                               timeout=time_budget.CALL_S, stdin=subprocess.DEVNULL,
                               env=dict(os.environ, PATH=d + ":" + os.environ["PATH"], HOME=d, SEAT_TMP_ROOT=d + "/t",
                                        XDG_CONFIG_HOME=d + "/c"))
            return r.stdout.split("\n")[:-1]
        a = bounded("-p", "go now")
        check("claude_bounded adds the table's effort when the caller gave none", a[-4:] == ["--effort", "high", "-p", "go now"]
              or ("--effort" in a and a[a.index("--effort") + 1] == "high"), a)
        b = bounded("-p", "x", "--effort", "xhigh")
        check("claude_bounded leaves the caller's effort alone", b.count("--effort") == 1 and "xhigh" in b, b)
        c = bounded("-p", "x", "--effort=xhigh")
        check("the --effort=L form counts as given", "--effort" not in c and "--effort=xhigh" in c, c)
        for args in (("auth", "status"), ("remote-control", "--name", "S"), ("-p", "/usage"), ("update",)):
            got = bounded(*args)
            check("claude_bounded adds no effort to %s" % " ".join(args), "--effort" not in got, got)


# ---------------------------------------------------------------- Part 2: the ladder
LAUNCHES = []
N = [0]


def fake_launch(seat, item, brief, model, max_s, budget, **kw):
    LAUNCHES.append({"seat": seat, "item": item, "brief": brief, "model": model, **kw})
    unit = "rm-detached-bench-ladder-%d" % len(LAUNCHES)
    rec = {"unit": unit, "seat": seat, "item": item, "model": model, "at": kw.get("now") or T0, "state": STATE,
           "status": "running", "budget_usd": budget}
    rec.update(kw.get("extra") or {})
    DH.write_record(rec)
    return 0, "DETACHED %s\n  item %s" % (unit, item)


def gates():
    return {"paused": lambda m: None, "held": lambda m: None, "voided": lambda u: False, "blocked": lambda s: None}


def plant_session(context=60000):
    d = os.path.join(PROJECTS, "-old-clone")
    os.makedirs(d, exist_ok=True)
    with open(os.path.join(d, SID + ".jsonl"), "w", encoding="utf-8") as f:
        f.write(json.dumps({"type": "user", "message": {"content": "brief"}}) + "\n")
        f.write(json.dumps({"type": "assistant", "message": {"usage": {
            "input_tokens": 10, "cache_creation_input_tokens": 0, "cache_read_input_tokens": context - 20,
            "output_tokens": 10}}}) + "\n")


def make_run(model="opus", effort="high", **extra):
    N[0] += 1
    item = "RIMMANDRAKE_LADDER_CASE_%d_OF_THE_SELFTEST" % N[0]
    unit = "rm-detached-bench-ladder-src-%d" % N[0]
    runs = DH.runs_dir()
    src = os.path.join(runs, unit + ".brief.src.md")
    with open(src, "w", encoding="utf-8") as f:
        f.write("Fix the sprinkler selftest.")
    outp = os.path.join(runs, unit + ".out")
    with open(outp, "w", encoding="utf-8") as f:
        json.dump({"result": "did a part", "usage": {}}, f)
    rec = {"unit": unit, "seat": "BENCH", "item": item, "clone": os.path.join(TMP, "clones", item + ".det"),
           "clone_how": "reused", "model": model, "max_s": None, "budget_usd": 0.0, "at": T0, "state": STATE,
           "status": "finished", "result": "success (exited 0)", "ended": T0 + 600, "brief_src": src, "out": outp,
           "err": outp + ".err", "session": SID}
    if effort:
        rec["effort"] = effort
    rec.update(extra)
    DH.write_record(rec)
    return rec


STUCK = "LEFT OPEN: the fix did not hold: selftest_sprinkler_live still FAILS 2 of 9 after the patch; cause unknown"
OUTSIDE = "LEFT OPEN: the live part waits: ArchBig and ArchSmall are held by other runs at 3:23 PM PST"
PROG = ("PROGRESS: theory: the hold never unfogs | experiment: runner._hold_site with fog off | reading: still red | "
        "next: read src/RimMandrake/FlowWorks/runner.py")


def go(rec, text, extra_notes=(), now=T0 + 700):
    del LAUNCHES[:]
    notes = [{"event": "note", "id": rec["item"], "ts": DH.iso(T0 + 300), "text": t} for t in extra_notes]
    notes.append({"event": "note", "id": rec["item"], "ts": DH.iso(T0 + 500), "text": text})
    p = LOC.plan(rec, {"state": "claimed", "notes": notes}, {}, now=now, gates=gates())
    if p["act"] == "continue":
        r = DH.read_record(rec["unit"])
        r["continue_plan"] = p
        DH.write_record(r)
        res = LOC.run(rec["unit"], now=now + 30, launch_fn=fake_launch, gates=gates(),
                      reader=lambda t: {"state": "claimed", "notes": []}, projects=PROJECTS)
    elif p["act"] == "raise":
        res = LOC.raise_first(rec, p, now)
    else:
        res = p
    return p, res


def log_text():
    try:
        with open(LOG, encoding="utf-8") as f:
            return f.read()
    except OSError:
        return ""


def t_a_stuck_worker_climbs_effort_first():
    plant_session()
    p, res = go(make_run(), STUCK)
    L = LAUNCHES[-1] if LAUNCHES else {}
    x = L.get("extra") or {}
    check("a stuck run at high resumes its own session at xhigh, same model",
          res.get("act") == "continued" and L.get("resume_session") == SID and x.get("effort") == "xhigh"
          and L.get("model") == "opus" and x.get("ladder_step") == "effort", (res, L.get("resume_session"), x))
    check("the xhigh step asks for the note a higher model would start from",
          "PROGRESS:" in L.get("brief", "") and "theory" in L.get("brief", ""), L.get("brief", "")[:800])
    p, res = go(make_run(effort=None), STUCK)
    check("a run with no recorded effort counts as the table's high",
          ((LAUNCHES[-1] if LAUNCHES else {}).get("extra") or {}).get("effort") == "xhigh", LAUNCHES)
    for name, text, kw in (("a cause outside the work", OUTSIDE, {}),
                           ("a spend stop", STUCK, {"result": "exit-code/claude-error (exited 1)"})):
        rec = make_run(**kw)
        if kw:
            with open(rec["out"], "w", encoding="utf-8") as f:
                json.dump({"stopped_by": "spend_watchdog", "result": "Stopped by spend_watchdog."}, f)
            rec = DH.read_record(rec["unit"])
            rec["continue_on_cap"] = 1
            DH.write_record(rec)
        p, res = go(rec, text)
        L = LAUNCHES[-1] if LAUNCHES else {}
        check("%s is not stuck: it continues at the same effort" % name,
              res.get("act") == "continued" and (L.get("extra") or {}).get("effort") == "high"
              and not (L.get("extra") or {}).get("ladder_step") and L.get("model") == "opus", (p.get("why"), res, L.get("extra")))
    for name, kw in (("a blind role", {"env": {"RM_CONTROL_STAGE": "blind_challenge"}}), ("a model of no tier", {"model": None})):
        p, res = go(make_run(**kw), STUCK)
        L = LAUNCHES[-1] if LAUNCHES else {}
        check("%s does not climb: it continues as before" % name, p.get("act") == "continue" and not p.get("ladder")
              and not (L.get("extra") or {}).get("ladder_step"), (p.get("act"), p.get("ladder"), L.get("extra")))
    check("stuck_why reads the words", LOC.stuck_why(STUCK)[0] and not LOC.stuck_why(OUTSIDE)[0]
          and not LOC.stuck_why("LEFT OPEN: waits for the owner's walk")[0]
          and not LOC.stuck_why("LEFT OPEN: part 1 holds at 6d96cd1d9d; part 2 is next")[0])


def t_a_refused_set_down_is_stuck():
    import filing_gate as FG
    plant_session()
    rec = make_run()
    FG.record_refusal(rec["unit"], STATE, "RIMMANDRAKE_SET_DOWN_OF_THE_SELFTEST", "a set-down", "task", "no Tried: part")
    p, res = go(rec, OUTSIDE)
    x = ((LAUNCHES[-1] if LAUNCHES else {}).get("extra") or {})
    check("a run that ends with its set-down refused climbs, whatever its note says",
          x.get("ladder_step") == "effort" and x.get("effort") == "xhigh" and "refused" in str(x.get("ladder_why")),
          (p.get("why"), x))
    rec = make_run()
    FG.record_refusal(rec["unit"], STATE, "RIMMANDRAKE_SET_DOWN_OF_THE_SELFTEST", "a set-down", "task", "no Tried: part")
    FG.record_resolution(rec["unit"], STATE, "filed", "RIMMANDRAKE_SET_DOWN_OF_THE_SELFTEST")
    p, res = go(rec, OUTSIDE)
    x = ((LAUNCHES[-1] if LAUNCHES else {}).get("extra") or {})
    check("a refusal that the run resolved makes nothing stuck", not x.get("ladder_step") and x.get("effort") == "high", x)
    rec = make_run()
    os.makedirs(os.path.dirname(FG.refusals_path(rec["unit"], STATE)), exist_ok=True)
    with open(FG.refusals_path(rec["unit"], STATE), "w") as f:
        f.write("not json\n")
    check("an unreadable refusal record decides nothing", LOC.refused_why(rec)[0] is False
          and "could not" in LOC.refused_why(rec)[1], LOC.refused_why(rec))


def t_then_a_higher_model_fresh_from_the_note():
    plant_session()
    p, res = go(make_run(effort="xhigh"), STUCK, extra_notes=[PROG])
    L = LAUNCHES[-1] if LAUNCHES else {}
    x = L.get("extra") or {}
    check("a stuck Opus at xhigh starts fresh on Fable 5.2 by its full name, at high",
          res.get("act") == "continued" and not L.get("resume_session") and L.get("model") == "claude-fable-5-2"
          and x.get("effort") == "high" and x.get("ladder_step") == "model", (res, L.get("model"), x))
    check("the fresh brief carries the worker's progress record and says why it is fresh",
          PROG in L.get("brief", "") and "model" in str(x.get("continue_fresh_why")), (x, L.get("brief", "")[:600]))
    p, res = go(make_run(model="sonnet", effort="xhigh"), STUCK, extra_notes=[PROG])
    L = LAUNCHES[-1] if LAUNCHES else {}
    check("a stuck Sonnet at xhigh starts fresh on Opus at high",
          L.get("model") == "opus" and (L.get("extra") or {}).get("effort") == "high", (res, L.get("model")))


def t_then_the_conductor_raise_first():
    before = log_text()
    rec = make_run(model="claude-fable-5-2", effort="high")
    p, res = go(rec, STUCK, extra_notes=[PROG])
    new = log_text()[len(before):]
    check("a stuck Fable run launches nothing", not LAUNCHES and p.get("act") == "raise", (p, LAUNCHES))
    check("one RAISE FIRST line in the Conductor log, with the note", "RAISE FIRST" in new and STUCK in new
          and rec["item"] in new, new)
    again = LOC.raise_first(DH.read_record(rec["unit"]), p, T0 + 900)
    check("a second pass writes no second line", log_text().count(rec["item"] + " ") <= new.count(rec["item"] + " ")
          and again.get("act") == "none", (again, log_text()[len(before):]))
    p, res = go(make_run(model="fable", effort="xhigh"), STUCK)
    check("a Fable run at any effort goes to the Conductor", p.get("act") == "raise", p)


def t_a_ladder_step_spends_no_counted_run():
    plant_session()
    import maturation_hands as MH
    rec = make_run()
    for i in range(LOC.MAX_PER_DAY):    # three ladder steps today already on its chain
        DH.write_record({"unit": "rm-detached-bench-ladder-old-%d-%d" % (N[0], i), "seat": "BENCH", "item": rec["item"],
                         "model": "opus", "at": T0 - 3000 + i, "state": STATE, "status": "finished",
                         "continued_from": "x", "continue_root_item": rec["item"], "ladder_step": "effort"})
    p, res = go(rec, STUCK)
    check("ladder steps do not count against MAX_PER_DAY", res.get("act") == "continued", (p.get("why"), res))
    new = res.get("new")
    check("a ladder step reads as a program's launch, not a hand run", new and MH.continued_from(new) == rec["unit"],
          (new, MH.continued_from(new) if new else None))
    src = open(os.path.join(HERE, "left_open_continue.py"), encoding="utf-8").read()
    check("the ladder writes no verify and files nothing", not re.search(r"[\"']verify[\"']|cli\.py[\"']?,\s*[\"']file", src))


def main():
    for t in (t_one_table_floor_high, t_a_launch_without_effort_is_red, t_every_launch_in_this_tree_states_effort,
              t_the_detached_record_keeps_effort, t_the_one_launcher_adds_a_forgotten_effort,
              t_a_refused_set_down_is_stuck, t_a_stuck_worker_climbs_effort_first,
              t_then_a_higher_model_fresh_from_the_note,
              t_then_the_conductor_raise_first, t_a_ladder_step_spends_no_counted_run):
        try:
            t()
        except Exception as e:  # noqa: BLE001  a test that crashes is red, by name
            check("%s ran" % t.__name__, False, "%s: %s" % (type(e).__name__, e))
    print("%s: %d failed" % ("RED" if BAD else "GREEN", len(BAD)))
    return 1 if BAD else 0


if __name__ == "__main__":
    sys.exit(main())
