#!/usr/bin/env python3
"""selftest_detached_helper.py — the detached launcher (CONDUCTOR_RESTART_REDESIGN_NEVER_FREEZE_HIM).

All in a temp state dir with a faked runner: no systemd unit, no claude, no clone, no rimflow write, no real log.
  refuse     an unknown item, a blind ledger read, a bad model, an empty brief, an out-of-range bound: nothing starts
  argv       role_launch's shape: systemd-run --user, claude_bounded.sh -p, the model, RuntimeMaxSec and the scope
             bound, spend_watchdog --cap-usd (never --max-budget-usd), ExecStopPost=finish, RM_DISPATCHER_STATE for the finish step, the brief footer
  record     a launch records the run; a systemd-run refusal marks it launch_failed
  same-second  a second launch of one item in the same second gets its own unit name; its failure never
             overwrites the first (running) run's record (DETACHED_LAUNCH_FIX_SAME_SECOND_CLOBBER)
  finish     a note on the item, the shard published from the clone, one Conductor log line, tokens read; once only
  killed     a run killed at its bound (no result JSON) still finishes, with the stderr tail
  guard      the real Conductor log is refused from a test process
  return     RIMMASTER_RELEASE_POOL_FROZEN_ITEMS_HOLD_CLONES (2026-11-07): the run's last step gives its pool <ITEM>.det
             clone back. Planted: a clean clone is landed, levelled and released; one with leftovers is bundled first and
             the item is told where; a bundle that fails keeps the clone; a --clone the caller gave, a path outside the
             pool, a busy clone, a clone another live run holds and a run not finished are never touched; once only;
             --all sweeps strays; the unit's third ExecStopPost starts it; and through the real Effects and git the
             commit and the dirty file leave in the bundle and the clone is gone
  hook       the spawn hook's drain refusal points at this launcher
  origin     an item filed only in a local shard (OWNER.jsonl from --owner-said, 2026-11-07) is refused with exit 2 before
             any clone or unit, naming the shard to publish; one fetch, then a search of the shards at origin/main; allowed
             when a `file` event's id or a `spawn` event's name is the item (a mention, a spawn's `from` and a longer id
             are not); a failed fetch is said only on a refusal; an unreadable git is a refusal, not a pass
  midreturn  RIMMANDRAKE_HOLD_DET_CLONE_UNTIL_RETURNED (2026-11-13/14, two runs lost, ~0.67 USD each): a launch whose
             <ITEM>.det is still being returned by the run before WAITS until the return lands, then makes a fresh clone;
             one still returning past the wait, one a live run holds, one whose run is dead (unit inactive, record
             'running') and one whose return kept it are REFUSED before any sync or unit, naming the command that passes;
             a dead run reads 'dead', never 'running', in status and never blocks a return; the ExecStopPost steps run
             when the clone is gone (WorkingDirectory=-), and finish records a run whose clone is gone
  whole      RIMMANDRAKE_KEEP_RUN_RESULT_WHOLE_FINISH_WRITES_OVER (2026-11-15: 238 of 248 result files began "FINISHED",
             dollars lost): out and err are append:, the finish step's line goes to <unit>.finish.log even when handed
             the result file at offset 0, the record and note carry measured dollars; recover_cost reads what survives
             of a written-over file (a total, else the whole modelUsage sum, else UNMEASURED); backfill-cost
  owed       RIMMANDRAKE_FLAG_DETACHED_SUCCESS_LEAVING_ITEM_OPEN (2026-11-15: a run fixed 17 Pyrelands gaps, exited 0, its
             item stayed `proposed`): the brief says claim at start, close or note `LEFT OPEN:` at the end; finish reads
             the item in the clone and, for a success with the item open and no such note since the run began, puts one
             plain line in the note, the Conductor log and the record; the status page lists it while the item stays open;
             a closed item, a LEFT OPEN note, a failed run and an unreadable ledger flag nothing
  gate       GATE_FIRST (RIMMANDRAKE_RUN_LAUNCH_CHECKS_FIVE_STEWARDS_HIT_GATES): the item's `## launch-checks` block, read
             from its prose or the spec of the event that filed it in the run's clone, runs before any unit: a must-fail
             that passes refuses (exit 2, nothing started, no record); --skip-launch-checks launches and is recorded;
             a check that cannot run launches with one "did not run" line on the output and the record
  timeout    RIMMANDRAKE_UNSTICK_DISPATCH_CLONE_PUBLISH_LINT_REFUSES_HEAD (2026-11-16: the tick's systemd-run passed its
             60 s, the launch raised, its record stayed "launching" with no unit and held the clone, so the next two
             launches were refused): a systemd-run that does not answer ends launch_failed when systemd reads no unit,
             holding nothing; running when the unit is up after all; never a traceback
  scopegone  RIMMANDRAKE_QUIET_CLEAN_FINISH_SCOPE_ALREADY_GONE: a scope systemd already collected reads clean; any
             other kill failure reads FAILED and the stop is still tried
"""
import json
import re
import os
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
TMP = tempfile.mkdtemp(prefix="selftest_detached_helper_")
os.environ["RM_DISPATCHER_STATE"] = os.path.join(TMP, "state")
os.environ["RM_CONDUCTOR_LOG"] = os.path.join(TMP, "conductor.md")
sys.path.insert(0, HERE)
import detached_helper as DH  # noqa: E402

FAILS = []
T0 = 1_800_000_000.0
KNOWN = {"SOME_ITEM_TO_BUILD"}
CLONE = os.path.join(TMP, "clone")
# a --clone that exists is one a unit can start in (RIMMANDRAKE_GUARD_HELPER_LAUNCH_ON_MISSING_CLONE_TWO_RUNS_DIED_UNSTARTED)

def brief_of(argv):
    """The brief a launch's systemd-run argv hands claude: the StandardInput file (every brief goes in on stdin)."""
    f = next((a[len("StandardInput=file:"):] for a in argv if a.startswith("StandardInput=file:")), "")
    return open(f, encoding="utf-8").read() if f and os.path.isfile(f) else ""

def _bounded(path):
    """Make `path` a clone a unit can start in: the claude_bounded.sh the unit's argv runs."""
    os.makedirs(os.path.join(path, "src", "RimMandrake", "Utils"), exist_ok=True)
    open(os.path.join(path, "src", "RimMandrake", "Utils", "claude_bounded.sh"), "w").close()


for _c in (CLONE, CLONE + "-other"):
    _bounded(_c)
os.makedirs(CLONE, exist_ok=True)        # a clone that stands: finish notes and publishes from it (a gone one is skipped)


def check(ok, msg):
    print(("PASS " if ok else "FAIL ") + msg)
    if not ok:
        FAILS.append(msg)


class R:
    def __init__(self, rc=0, out=""):
        self.returncode, self.stdout, self.stderr = rc, out, ""


GIT_CALLS = []     # the origin check's fetch and grep, kept apart from `calls` so each test's calls[0] stays systemd-run
ORIGIN = {"events": None, "fetch_rc": 0, "grep_rc": None}   # the fake origin/main: ledger event lines; None = KNOWN, filed


def origin_events():
    if ORIGIN["events"] is not None:
        return ORIGIN["events"]
    return [json.dumps({"seat": "BENCH", "event": "file", "id": i, "title": "t", "for": "BENCH"}, separators=(",", ":"))
            for i in sorted(KNOWN)]


def fake_origin_git(argv, kw):
    GIT_CALLS.append((argv, kw))
    if argv[:2] == ["git", "fetch"]:
        return R(ORIGIN["fetch_rc"], "")
    needle = argv[argv.index("-e") + 1]      # git grep -F: the lines that hold the id, as `git grep -h` prints them
    out = [ln for ln in origin_events() if needle in ln]
    return R(ORIGIN["grep_rc"] if ORIGIN["grep_rc"] is not None else (0 if out else 1), "\n".join(out))


def recorder(rc=0, out=""):
    calls = []

    def run(argv, **kw):
        if argv[:2] in (["git", "fetch"], ["git", "grep"]):
            return fake_origin_git(argv, kw)
        calls.append((argv, kw))
        return R(rc, out)
    return calls, run


def non_systemctl(calls):
    """finish's calls past its scope stop (the note, the publish)."""
    return [c for c in calls if c[0][0] != "systemctl"]


def test_refuse():
    calls, run = recorder()
    for args, word in (((("BENCH", "NOT_AN_ITEM", "b", "sonnet", 600, 5)), "not a ledger item"),
                       ((("BENCH", "SOME_ITEM_TO_BUILD", "b", "gpt", 600, 5)), "model"),
                       ((("BENCH", "SOME_ITEM_TO_BUILD", "  ", "sonnet", 600, 5)), "empty brief"),
                       ((("BENCH", "SOME_ITEM_TO_BUILD", "b", "sonnet", 30, 5)), "--max-s"),
                       ((("NOPE", "SOME_ITEM_TO_BUILD", "b", "sonnet", 600, 5)), "seat")):
        rc, text = DH.launch(*args, now=T0, runner=run, known=KNOWN, clone=CLONE)
        check(rc == 2 and word in text, "refuse: %s (%s)" % (word, text[:60]))
    rc, text = DH.launch("BENCH", "SOME_ITEM_TO_BUILD", "b", "sonnet", 600, 5, now=T0, runner=run, known=set(),
                         clone=CLONE)
    check(rc == 2 and "blind" in text, "refuse: a ledger read of 0 items is blind, not a pass")
    check(calls == [], "refuse: nothing was started")
    check(GIT_CALLS == [], "refuse: an item not on the local ledger never reaches git")


def test_launch_and_finish():
    calls, run = recorder()
    rc, text = DH.launch("BENCH", "SOME_ITEM_TO_BUILD", "Build the thing.", "opus", 1800, 12, now=T0, runner=run,
                         known=KNOWN, clone=CLONE)
    check(rc == 0 and "DETACHED rm-detached-bench-some-item-to-build-" in text, "launch: ok (%s)" % text[:70])
    argv = calls[0][0]
    j = " ".join(argv)
    check(argv[:3] == ["systemd-run", "--user", "--quiet"] and "claude_bounded.sh" in j, "argv: systemd-run + claude_bounded")
    check(argv[argv.index("--model") + 1] == "opus" and "-p" in argv[argv.index("--"):], "argv: the model, -p")
    check("RuntimeMaxSec=%d" % (1800 + DH.GRACE_S) in argv and "CLAUDE_SCOPE_RUNTIME_MAX=%d" % (1800 + DH.GRACE_S) in argv,
          "argv: wall time bounded twice (unit and scope)")
    check("--max-budget-usd" not in argv and argv[argv.index("--cap-usd") + 1] == "12",
          "argv: spend bounded from outside by spend_watchdog --cap-usd, never --max-budget-usd")
    calls2, run2 = recorder()
    rc2, _ = DH.launch("BENCH", "SOME_ITEM_TO_BUILD", "Build the thing.", "opus", DH.DEFAULT_MAX_S, 12, now=T0,
                       runner=run2, known=KNOWN, clone=CLONE)
    a2 = calls2[0][0]
    check(rc2 == 0 and DH.DEFAULT_MAX_S is None, "unbounded: the default is no limit")
    check(not any(x.startswith("RuntimeMaxSec=") or x.startswith("CLAUDE_SCOPE_RUNTIME_MAX") for x in a2),
          "unbounded: argv carries no RuntimeMaxSec and no scope bound")
    msg2 = brief_of(a2)
    check("no wall-time bound" in msg2 and "Wall-time bound" not in msg2, "unbounded: footer says no wall-time bound")
    check(a2[a2.index("--cap-usd") + 1] == "12", "unbounded: spend bound kept")
    check(DH.parse_max_s("none") is None and DH.parse_max_s("0") is None and DH.parse_max_s("900") == 900, "parse_max_s")
    check(any(a.startswith("ExecStopPost=/usr/bin/python3 ") and a.endswith("finish --unit " + argv[argv.index("--unit") + 1])
              for a in argv), "argv: ExecStopPost runs finish for this unit")
    check("RM_DISPATCHER_STATE=" + os.environ["RM_DISPATCHER_STATE"] in argv, "argv: the finish step finds the record")
    msg = brief_of(argv)
    check(msg.startswith("Build the thing.") and "cli.py note SOME_ITEM_TO_BUILD" in msg and "./publish" in msg,
          "argv: the brief carries the note-and-publish footer")
    unit = argv[argv.index("--unit") + 1]
    rec = DH.read_record(unit)
    check(rec and rec["status"] == "running" and rec["clone"] == CLONE, "record: the run is recorded running")
    src = (rec or {}).get("brief_src") or ""
    check(os.path.isfile(src) and open(src, encoding="utf-8").read() == "Build the thing.",
          "record: the brief as given is saved (brief_src), so a killed run can be relaunched (stop_resume)")
    with open(rec["out"], "w") as f:
        json.dump({"result": "Built it; sha abc123.", "usage": {"input_tokens": 10, "output_tokens": 5,
                   "cache_creation_input_tokens": 0, "cache_read_input_tokens": 0},
                   "modelUsage": {"claude-opus-5-5": {"inputTokens": 10, "outputTokens": 5, "cacheReadInputTokens": 0,
                                                      "cacheCreationInputTokens": 0}}}, f)   # as claude -p writes it
    fcalls, frun = recorder(out="PUBLISHED abcdef1234567")
    frun_calls = fcalls
    rc, text = DH.finish(unit, now=T0 + 600, env={"SERVICE_RESULT": "success", "EXIT_CODE": "exited",
                                                  "EXIT_STATUS": "0"}, runner=frun)
    fcalls = non_systemctl(fcalls)
    note = fcalls[0][0]
    check(note[2:4] == ["note", "SOME_ITEM_TO_BUILD"] and "--text" in note and fcalls[0][1].get("cwd") == CLONE,
          "finish: a note on the item, from the clone")
    nt = note[note.index("--text") + 1]
    check("success" in nt and "Built it" in nt and "600 s" in nt, "finish: the note says how it ended (%s)" % nt[:80])
    check(fcalls[1][0][0] == "./publish" and fcalls[1][0][-1] == "infrastructure/state/ledger/events/BENCH.jsonl",
          "finish: the seat shard is published")
    msg2 = brief_of(argv)
    check("OWNER.jsonl" in msg2, "argv: the footer says an OWNER-authority event's shard is published too")
    with open(os.environ["RM_CONDUCTOR_LOG"]) as f:
        log = f.read()
    check(log.count("DETACHED RUN ENDED") == 1 and "SOME_ITEM_TO_BUILD" in log, "finish: one Conductor log line")
    rec = DH.read_record(unit)
    check(rec["status"] == "finished" and isinstance(rec["tokens"], int) and "publish abcdef1234" in text,
          "finish: recorded finished with tokens and the publish sha (%s)" % text[-60:])
    n_before = len(frun_calls)
    rc, text = DH.finish(unit, now=T0 + 700, env={}, runner=frun)
    check(rc == 0 and "already" in text and len(frun_calls) == n_before, "finish: a second call changes nothing")


def test_killed_and_failed_launch():
    calls, run = recorder()
    DH.launch("BENCH", "SOME_ITEM_TO_BUILD", "b", "sonnet", 600, 5, now=T0 + 1, runner=run, known=KNOWN, clone=CLONE)
    unit = calls[0][0][calls[0][0].index("--unit") + 1]
    rec = DH.read_record(unit)
    with open(rec["err"], "w") as f:
        f.write("Terminated\n")
    fcalls, frun = recorder()
    rc, text = DH.finish(unit, now=T0 + 800, env={"SERVICE_RESULT": "timeout", "EXIT_CODE": "killed",
                                                  "EXIT_STATUS": "TERM"}, runner=frun)
    scope = "claude-seat-BENCH-%s.scope" % unit
    sysc = [c[0] for c in fcalls if c[0][0] == "systemctl"]
    check(["systemctl", "--user", "kill", "--signal=SIGKILL", scope] in sysc
          and ["systemctl", "--user", "stop", "--no-block", scope] in sysc,
          "killed: finish KILLs and stops the run's claude scope, where the orphan lived (%s)" % sysc[:2])
    first_other = next(i for i, c in enumerate(fcalls) if c[0][0] != "systemctl")
    check(all(c[0][0] == "systemctl" for c in fcalls[:first_other]) and first_other >= 2,
          "killed: the scope is stopped BEFORE the note and publish (ExecStopPost has TimeoutStopSec=30)")
    check(any(scope in s and "now" in s for s in DH.read_record(unit)["steps"]),
          "killed: the record says what the scope stop did and the scope's state after")
    margv = calls[0][0]
    check("CLAUDE_SCOPE_UNIT=claude-seat-BENCH-%s" % unit in margv,
          "launch and finish name the same scope")
    fcalls = non_systemctl(fcalls)
    nt = fcalls[0][0][fcalls[0][0].index("--text") + 1]
    with open(os.environ["RM_CONDUCTOR_LOG"]) as f:
        klog = [ln for ln in f.read().splitlines() if unit in ln and "DETACHED RUN ENDED" in ln]
    check(rc == 0 and "timeout" in nt and "Terminated" in nt and klog and "UNMEASURED" in klog[-1],
          "killed: a run killed at its bound still ends with a note; its tokens read UNMEASURED in the log line (%s)"
          % nt[:90])
    calls, run = recorder(rc=1, out="Failed to start transient service unit")
    rc, text = DH.launch("BENCH", "SOME_ITEM_TO_BUILD", "b", "sonnet", 600, 5, now=T0 + 2, runner=run, known=KNOWN,
                         clone=CLONE)
    unit = calls[0][0][calls[0][0].index("--unit") + 1]
    check(rc == 1 and DH.read_record(unit)["status"] == "launch_failed", "record: a refused systemd-run is launch_failed")


def test_same_second():
    calls, run = recorder()
    rc, _ = DH.launch("BENCH", "SOME_ITEM_TO_BUILD", "b", "opus", 600, 5, now=T0 + 50, runner=run, known=KNOWN,
                      clone=CLONE)
    first = calls[0][0][calls[0][0].index("--unit") + 1]
    before = DH.read_record(first)
    fcalls, frun = recorder(rc=1, out="Failed to start transient service unit: Unit already exists")
    rc2, text = DH.launch("BENCH", "SOME_ITEM_TO_BUILD", "b", "sonnet", 600, 5, now=T0 + 50, runner=frun,
                          known=KNOWN, clone=CLONE + "-other")
    second = fcalls[0][0][fcalls[0][0].index("--unit") + 1]
    check(rc == 0 and second != first, "same-second: the second launch gets its own unit name (%s vs %s)" % (second, first))
    after = DH.read_record(first)
    check(after == before and after["status"] == "running" and after["model"] == "opus" and after["clone"] == CLONE,
          "same-second: the running run's record is untouched (status, model, clone)")
    check(rc2 == 1 and DH.read_record(second)["status"] == "launch_failed", "same-second: the failure lands on its own record")
    third = DH.launch("BENCH", "SOME_ITEM_TO_BUILD", "b", "sonnet", 600, 5, now=T0 + 50, runner=run, known=KNOWN,
                      clone=CLONE)[1].split()[1]
    check(third not in (first, second), "same-second: a third gets a third name (%s)" % third)


def test_guard():
    try:
        DH.conductor_line("x", T0, path=DH.REAL_LOG)
        ok = False
    except RuntimeError:
        ok = True
    check(ok, "guard: the real Conductor log is refused from a test process")


POOL = os.path.join(TMP, "pool")
LAND_REL = os.path.join("src", "RimMandrake", "Utils", "conversations_land.py")


def det_clone(item, how=None, status="finished", unit=None, path=None, state=None):
    """A pool clone <pool>/clones/<ITEM>.det on disk (a stub tree) and the record of the run that used it."""
    path = path or os.path.join(POOL, "clones", item + ".det")
    os.makedirs(os.path.join(path, os.path.dirname(LAND_REL)), exist_ok=True)
    open(os.path.join(path, LAND_REL), "w").close()
    _bounded(path)
    unit = unit or "rm-detached-%s-%d" % (item.lower().replace("_", "-"), len(os.listdir(DH.runs_dir())))
    rec = {"seat": "BENCH", "item": item, "clone": path, "model": "sonnet", "max_s": 600, "budget_usd": 5.0, "at": T0,
           "state": os.environ["RM_DISPATCHER_STATE"], "status": status, "unit": unit,
           "out": os.path.join(TMP, unit + ".out"), "err": os.path.join(TMP, unit + ".err"),
           "clone_how": how if how is not None else "made " + path}
    DH.write_record(rec)
    return unit, path


def sh_runner(shard_dirty=False, others=()):
    """Records every call; `git status` on the shard says dirty or clean (`others`: more dirty shards, e.g. OWNER),
    ./publish prints a sha."""
    calls = []

    def run(argv, **kw):
        calls.append(list(argv))
        if argv[:3] == ["git", "status", "--porcelain"]:
            return R(0, (" M infrastructure/state/ledger/events/BENCH.jsonl\n" if shard_dirty else "")
                     + "".join(" M infrastructure/state/ledger/events/%s.jsonl\n" % o for o in others))
        if argv[0] == "./publish":
            return R(0, "PUBLISHED abcdef1234567")
        return R(0, "")
    return calls, run


def fake_evictor(bundle=None, kept=None, remove=True, raises=False):
    """Stands for evict_clone: runs `before` when there is a bundle (as Effects.remove_clone does), then removes the clone."""
    seen = []

    def ev(item, clone, before=None):
        seen.append((item, clone))
        if raises:
            raise RuntimeError("boom")
        if bundle and before:
            before(bundle)
        if remove and not kept:
            shutil.rmtree(clone)
        return bundle, kept
    return seen, ev


def not_busy(c):
    return False


def test_return():
    os.environ["RM_DETACHED_POOL"] = POOL
    try:
        _test_return()
    finally:
        os.environ.pop("RM_DETACHED_POOL", None)


def _test_return():
    # a clean clone: landed, shard clean, levelled, released; nothing to bundle
    unit, clone = det_clone("CLEAN_RUN")
    calls, run = sh_runner(shard_dirty=False)
    seen, ev = fake_evictor()
    rc, text = DH.return_clone(unit, now=T0 + 10, runner=run, evictor=ev, busy=not_busy)
    names = [c[0] if c[0] != "python3" else os.path.basename(c[1]) for c in calls]
    check(rc == 0 and text.startswith("RETURNED") and seen == [("CLEAN_RUN", clone)] and not os.path.exists(clone),
          "return: a clean finished .det clone is released (%s)" % text[:70])
    check(names[:1] == ["conversations_land.py"] and "./sync" in names and "./publish" not in names and names[-1] == "./sync",
          "return: its conversation records are landed first, a clean shard is not published (%s)" % names)
    check(DH.read_record(unit).get("returned") == T0 + 10, "return: the record says returned")
    n = len(calls)
    rc, text = DH.return_clone(unit, now=T0 + 20, runner=run, evictor=ev, busy=not_busy)
    check(rc == 0 and "already returned" in text and len(calls) == n and len(seen) == 1, "return: a second call changes nothing")

    # RIMMANDRAKE_RETRY_CARRY_ON_REFUSED_BY_DRAIN_FOUR_RUNS_STRANDED (2026-11-24 4:37 to 4:53 PM PST): the continuation
    # step wrote "waits for the account switch" into the record while the return step worked on its own old copy, and
    # the return's last write took the mark away: four runs were never started after the switch
    unit, clone = det_clone("WAITS_RUN")
    r0 = DH.read_record(unit)
    r0["continue_plan"] = {"act": "continue", "why": "as planned at finish"}
    DH.write_record(r0)
    calls, run0 = sh_runner(shard_dirty=False)

    def run_mid(argv, **kw):
        if argv[0] == "./sync":     # the continuation step's write lands while the return step works
            r = DH.read_record(unit)
            r["continue_waits"] = {"at": T0 + 11, "why": "refused: the account lukas is draining"}
            r["continue_plan"] = {"act": "continue", "why": "written during the return"}
            DH.write_record(r)
        return run0(argv, **kw)
    seen, ev = fake_evictor()
    rc, text = DH.return_clone(unit, now=T0 + 12, runner=run_mid, evictor=ev, busy=not_busy)
    got = DH.read_record(unit)
    check(rc == 0 and got.get("returned") == T0 + 12 and (got.get("continue_waits") or {}).get("at") == T0 + 11,
          "return: a mark that another step wrote into the record during the return is kept (%s)" % sorted(got))
    check(got["continue_plan"]["why"] == "written during the return" and got.get("return_steps"),
          "return: a field that the other step changed keeps its new value, beside the return's own fields")
    import left_open_continue as LOC
    import control as C
    pd = os.path.join(TMP, "plan_after_switch")
    os.makedirs(pd, exist_ok=True)
    with open(os.path.join(pd, "notice.json"), "w") as f:
        json.dump({"state": "none", "at": DH.iso(T0 + 300)}, f)
    with open(os.path.join(pd, "log.jsonl"), "w") as f:
        f.write(json.dumps({"do": "normal", "at": DH.iso(T0 + 300)}) + "\n")
    kicks = []

    class Ran:
        returncode, stdout, stderr, refused, why = 0, "", "", False, ""
    real, C.launch_unit = C.launch_unit, lambda argv, spec, **k: kicks.append(spec) or Ran()
    try:
        said = LOC.kick_waiting(T0 + 330, plan_dir=pd)
        check([k["unit"] for k in kicks if k["unit"].startswith(unit)] == [unit + "-continue"],
              "return: so the first timed pass after the switch starts the carry-on (%s)" % said)
        LOC.kick_waiting(T0 + 400, plan_dir=pd)
        check(len([k for k in kicks if k["unit"].startswith(unit)]) == 1, "return: and starts it once")
    finally:
        C.launch_unit = real

    # a dirty shard is published before the sync, and --no-publish-ledger leaves it for the bundle
    unit, clone = det_clone("DIRTY_SHARD")
    calls, run = sh_runner(shard_dirty=True)
    seen, ev = fake_evictor()
    DH.return_clone(unit, now=T0, runner=run, evictor=ev, busy=not_busy)
    pubs = [i for i, c in enumerate(calls) if c[0] == "./publish"]
    sync = [i for i, c in enumerate(calls) if c[0] == "./sync"]
    check(len(pubs) == 1 and calls[pubs[0]][-1].endswith("events/BENCH.jsonl") and pubs[0] < sync[0],
          "return: a shard the run left dirty is published, before the clone is levelled")
    # RIMMANDRAKE_PUBLISH_EVERY_DIRTY_SHARD_OWNER_FILES_WENT_UNSENT: a --per-ruling / --owner-said / --by-card event
    # lands in OWNER.jsonl, not the seat's shard; a return that published only the seat's shard bundled two file events
    unit, clone = det_clone("OWNER_SHARD")
    calls, run = sh_runner(shard_dirty=True, others=("OWNER",))
    seen, ev = fake_evictor()
    DH.return_clone(unit, now=T0, runner=run, evictor=ev, busy=not_busy)
    pubs = [c for c in calls if c[0] == "./publish"]
    check(len(pubs) == 1 and pubs[0][-2:] == ["infrastructure/state/ledger/events/BENCH.jsonl",
                                             "infrastructure/state/ledger/events/OWNER.jsonl"],
          "return: every dirty shard is published, the OWNER shard a --per-ruling filing wrote included (%s)" % pubs)
    unit, clone = det_clone("OWNER_ONLY")
    calls, run = sh_runner(shard_dirty=False, others=("OWNER",))
    seen, ev = fake_evictor()
    DH.return_clone(unit, now=T0, runner=run, evictor=ev, busy=not_busy)
    pubs = [c for c in calls if c[0] == "./publish"]
    check(len(pubs) == 1 and pubs[0][-1] == "infrastructure/state/ledger/events/OWNER.jsonl",
          "return: a dirty OWNER shard alone is published too (%s)" % pubs)
    check(DH.dirty_shards("/nonexistent/clone", "BENCH") == [], "dirty_shards: a clone git cannot read answers []")
    unit, clone = det_clone("OLD_RELEASE")
    calls, run = sh_runner(shard_dirty=True)
    seen, ev = fake_evictor(bundle="/store/orphans/bundles/OLD_RELEASE-1")
    rc, text = DH.return_clone(unit, now=T0, runner=run, evictor=ev, busy=not_busy, publish_ledger=False)
    check(all(c[0] not in ("./publish",) and c[:2] != ["git", "status"] and c[2:3] != ["note"] for c in calls) and len(seen) == 1,
          "return: with publish_ledger off nothing is published, not even the bundle note (its lines ride in the bundle)")
    check(rc == 0 and DH.read_record(unit).get("bundle") == "/store/orphans/bundles/OLD_RELEASE-1", "return: and the bundle is on the record")

    # leftovers: the order is land, sync, then eviction; the item is told where the bundle is, and that is published
    unit, clone = det_clone("LEFTOVERS")
    calls, run = sh_runner(shard_dirty=False)
    seen, ev = fake_evictor(bundle="/store/orphans/bundles/LEFTOVERS-1")
    rc, text = DH.return_clone(unit, now=T0 + 5, runner=run, evictor=ev, busy=not_busy)
    notes = [c for c in calls if len(c) > 3 and c[2:4] == ["note", "LEFTOVERS"]]
    check(rc == 0 and len(notes) == 1 and "/store/orphans/bundles/LEFTOVERS-1" in notes[0][notes[0].index("--text") + 1],
          "return: leftovers are bundled and the item gets a note naming the bundle")
    check(calls[-1][0] == "./publish" and calls[-1][-1].endswith("events/BENCH.jsonl"), "return: and that note is published")
    rec = DH.read_record(unit)
    check(rec.get("bundle") == "/store/orphans/bundles/LEFTOVERS-1" and rec.get("returned") == T0 + 5,
          "return: the record keeps the bundle path")
    with open(os.environ["RM_CONDUCTOR_LOG"]) as f:
        check("LEFTOVERS" in f.read() and "bundled at /store/orphans/bundles/LEFTOVERS-1" in open(os.environ["RM_CONDUCTOR_LOG"]).read(),
              "return: the Conductor log says where the leftovers went")

    # a bundle that cannot be made keeps the clone, loudly; an evictor that raises does too
    for what, kw in (("a failed bundle", dict(kept="the clone stayed: its bundle failed")), ("a raising evictor", dict(raises=True))):
        unit, clone = det_clone("KEEP_" + ("FAIL" if "failed" in what else "RAISE"))
        calls, run = sh_runner()
        seen, ev = fake_evictor(**kw)
        rc, text = DH.return_clone(unit, now=T0, runner=run, evictor=ev, busy=not_busy)
        check(rc == 1 and text.startswith("KEPT") and os.path.isdir(clone) and not DH.read_record(unit).get("returned"),
              "return: %s keeps the clone, exits 1 and does not mark it returned" % what)

    # never touched
    unit, clone = det_clone("GIVEN_CLONE", how="given /somewhere")
    calls, run = sh_runner()
    seen, ev = fake_evictor()
    rc, text = DH.return_clone(unit, now=T0, runner=run, evictor=ev, busy=not_busy)
    check(rc == 0 and "left alone" in text and seen == [] and calls == [] and os.path.isdir(clone),
          "return: a clone the caller gave with --clone is left alone")
    unit, clone = det_clone("ELSEWHERE", path=os.path.join(TMP, "not_the_pool", "ELSEWHERE.det"))
    seen, ev = fake_evictor()
    rc, text = DH.return_clone(unit, now=T0, runner=run, evictor=ev, busy=not_busy)
    check("left alone" in text and seen == [] and os.path.isdir(clone), "return: a path outside <pool>/clones/<ITEM>.det is left alone")
    unit, clone = det_clone("WRONG_NAME", path=os.path.join(POOL, "clones", "SOME_OTHER_ITEM.det"))
    seen, ev = fake_evictor()
    rc, text = DH.return_clone(unit, now=T0, runner=run, evictor=ev, busy=not_busy)
    check("left alone" in text and seen == [] and os.path.isdir(clone), "return: another item's .det clone is left alone")
    unit, clone = det_clone("BUSY_ONE")
    seen, ev = fake_evictor()
    calls, run = sh_runner()
    rc, text = DH.return_clone(unit, now=T0, runner=run, evictor=ev, busy=lambda c: c == clone)
    check(rc == 0 and "kept" in text and seen == [] and calls == [] and os.path.isdir(clone),
          "return: a clone a process works in is kept, and nothing is landed or synced into it")
    unit, clone = det_clone("STILL_GOING", status="running")
    seen, ev = fake_evictor()
    rc, text = DH.return_clone(unit, now=T0, runner=run, evictor=ev, busy=not_busy)
    check("kept" in text and "not finished" in text and seen == [] and os.path.isdir(clone), "return: a run not yet finished keeps its clone")
    unit, clone = det_clone("SHARED_CLONE")
    other, _ = det_clone("SHARED_CLONE", status="running", path=clone, unit="rm-detached-shared-clone-second")
    seen, ev = fake_evictor()
    rc, text = DH.return_clone(unit, now=T0, runner=run, evictor=ev, busy=not_busy)
    check("kept" in text and other in text and seen == [] and os.path.isdir(clone),
          "return: a clone another live run of the item holds is kept")
    unit, clone = det_clone("GONE_ALREADY")
    shutil.rmtree(clone)
    seen, ev = fake_evictor()
    rc, text = DH.return_clone(unit, now=T0, runner=run, evictor=ev, busy=not_busy)
    check(rc == 0 and "already gone" in text and DH.read_record(unit).get("returned") == T0, "return: a clone already gone is just recorded")

    # --all: strays only
    stray, sclone = det_clone("STRAY_ONE")
    given, gclone = det_clone("STRAY_GIVEN", how="given " + os.path.join(POOL, "clones", "STRAY_GIVEN.det"))
    fresh, fclone = det_clone("JUST_ENDED")
    rec = DH.read_record(fresh)
    rec["ended"] = T0 + 100000 - 600           # ended ten minutes before the sweep
    DH.write_record(rec)
    seen, ev = fake_evictor()
    calls, run = sh_runner()
    rc, text = DH.return_all(runner=run, evictor=ev, busy=not_busy, now=T0 + 100000)
    check(os.path.isdir(fclone) and ("JUST_ENDED", fclone) not in seen, "return --all: a run that ended ten minutes ago is not swept")
    check(("STRAY_ONE", sclone) in seen and ("STRAY_GIVEN", gclone) not in seen and os.path.isdir(gclone) and not os.path.exists(sclone)
          and "STRAY_GIVEN" not in text, "return --all: a finished run's stray .det clone goes back, a given clone is not even visited")

    # the unit starts it, last, in a unit of its own
    calls, run = recorder()
    rc, text = DH.launch("BENCH", "SOME_ITEM_TO_BUILD", "Build.", "sonnet", 600, 5, now=T0 + 99, runner=run, known=KNOWN, clone=CLONE)
    argv = calls[0][0]
    # control.py's own end receipt (launch_unit adds it: `control.py ended <run>`) is not one of the helper's steps
    rcpt = lambda a, verb: "control.py" in a and "-- %s " % verb in a     # its resolver: candidates, --, the verb
    posts = [a for a in argv if a.startswith("ExecStopPost=") and not rcpt(a, "ended")]
    check(any(a.startswith("ExecCondition=") and rcpt(a, "condition") for a in argv)
          and any(rcpt(a, "ended") for a in argv), "argv: control.py's start check and end receipt ride along")
    unit = argv[argv.index("--unit") + 1]
    check(len(posts) == 3 and posts[0].endswith("finish --unit " + unit) and "wrapup.py" in posts[1]
          and posts[2].startswith("ExecStopPost=-/usr/bin/systemd-run ") and "--no-block" in posts[2]
          and "detached_helper.py" in posts[2] and posts[2].endswith(" -- return --unit " + unit),
          "argv: the unit's third and last ExecStopPost starts the return step, detached from TimeoutStopSec=30 (%s)" % posts[-1][-90:])


def test_return_real_git():
    """Through the real Effects, Store and git: a finished run's .det clone with an unpushed commit and a dirty file leaves
    in a bundle that holds both, and a clean one leaves with none. Nothing in the real pool or store is touched."""
    pool = os.path.join(TMP, "realpool")
    os.makedirs(os.path.join(pool, "clones"))
    os.environ["RM_DETACHED_POOL"] = pool
    try:
        def git(c, *a):
            return subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@t", *a], cwd=c, check=True,
                                  capture_output=True, text=True).stdout
        o = os.path.join(pool, "o.git")
        git(pool, "init", "-q", "--bare", o, "-b", "main")
        names = {}
        for item in ("REAL_LEFTOVERS", "REAL_CLEAN"):
            c = os.path.join(pool, "clones", item + ".det")
            git(pool, "clone", "-q", o, c)
            with open(os.path.join(c, item + ".txt"), "w") as f:
                f.write("base\n")
            git(c, "add", item + ".txt")
            git(c, "commit", "-qm", "base")
            git(c, "push", "-q", "origin", "HEAD")
            unit = "rm-detached-%s-1" % item.lower().replace("_", "-")
            DH.write_record({"seat": "BENCH", "item": item, "clone": c, "model": "sonnet", "max_s": 600, "budget_usd": 5.0,
                             "at": T0, "state": os.environ["RM_DISPATCHER_STATE"], "status": "finished", "unit": unit,
                             "out": os.path.join(TMP, unit + ".out"), "err": os.path.join(TMP, unit + ".err"),
                             "clone_how": "made " + c})
            names[item] = (unit, c)
        unit, c = names["REAL_LEFTOVERS"]
        with open(os.path.join(c, "work.cs"), "w") as f:
            f.write("committed work\n")
        git(c, "add", "work.cs")
        git(c, "commit", "-qm", "work")
        with open(os.path.join(c, "dirty.cs"), "w") as f:
            f.write("not committed\n")
        calls, run = sh_runner()
        rc, text = DH.return_clone(unit, now=T0, runner=run, busy=not_busy)
        b = DH.read_record(unit).get("bundle")
        check(rc == 0 and b and not os.path.exists(c), "real: the dirty clone is released with a bundle (%s)" % text[:90])
        held = []
        if b and os.path.isdir(b):
            for f in os.listdir(b):
                if f.endswith(".tar"):
                    import tarfile
                    with tarfile.open(os.path.join(b, f)) as t:
                        held += t.getnames()
        check(b and os.path.exists(os.path.join(b, "commits.bundle")) and any(n.endswith("dirty.cs") for n in held),
              "real: the bundle holds the unpushed commit and the dirty file (%s)" % held)
        unit, c = names["REAL_CLEAN"]
        rc, text = DH.return_clone(unit, now=T0, runner=run, busy=not_busy)
        check(rc == 0 and not DH.read_record(unit).get("bundle") and not os.path.exists(c),
              "real: the clean clone is released with no bundle (%s)" % text[:90])
    finally:
        os.environ.pop("RM_DETACHED_POOL", None)


def shard_line(event, **kw):
    return json.dumps(dict({"seat": "BENCH", "event": event}, **kw))


def test_origin():
    """Run as a launched run (the refusal path), whoever runs this test: the Conductor's own launch repairs the
    refusal by publishing (selftest_never_refuse_conductor.py)."""
    real_unit = os.environ.get("RM_ROLE_UNIT")
    os.environ["RM_ROLE_UNIT"] = "rm-detached-selftest-origin-caller"
    try:
        _test_origin()
    finally:
        if real_unit is None:
            os.environ.pop("RM_ROLE_UNIT", None)
        else:
            os.environ["RM_ROLE_UNIT"] = real_unit


def _test_origin():
    """The item must be filed on origin/main before a clone is made or a unit starts. The fake origin holds the lines that
    `git grep` would print; the temp repo holds the working-tree shards the refusal names."""
    item = "SOME_ITEM_TO_BUILD"
    repo = os.path.join(TMP, "originrepo")
    events = os.path.join(repo, *DH.EVENTS_REL.split("/"))
    os.makedirs(events, exist_ok=True)
    with open(os.path.join(events, "OWNER.jsonl"), "w") as f:       # filed by --owner-said: only here
        f.write(shard_line("file", id=item, title="t", seat="OWNER") + "\n")
    with open(os.path.join(events, "BENCH.jsonl"), "w") as f:       # mentions it, files something else
        f.write(shard_line("note", id=item, text="x") + "\n" + shard_line("file", id="OTHER_ITEM_ELSEWHERE") + "\n")
    real_repo, real_pool = DH.REPO, os.environ.get("RM_DETACHED_POOL")
    DH.REPO, os.environ["RM_DETACHED_POOL"] = repo, os.path.join(TMP, "originpool")
    try:
        def launch(runner, known=None, clone=CLONE, it=item):
            return DH.launch("BENCH", it, "Build.", "sonnet", 600, 5, now=T0 + 300, runner=runner, known=known or {it},
                             clone=clone)

        def reset(**kw):
            GIT_CALLS.clear()
            ORIGIN.update(dict({"events": [], "fetch_rc": 0, "grep_rc": None}, **kw))

        runs_before = len(os.listdir(DH.runs_dir()))
        # refused: not on origin/main, filed only in OWNER.jsonl; with a clone given, and with none (take_clone not reached)
        for clone in (CLONE, None):
            reset()
            calls, run = recorder()
            rc, text = launch(run, clone=clone)
            check(rc == 2 and text == "refused: %s is not on origin/main; to pass, run in %s: ./publish -m \"ledger: %s filed\" "
                  "%s/OWNER.jsonl" % (item, repo, item, DH.EVENTS_REL),
                  "origin: refused, exit 2, one line naming the shard that holds the event (clone=%s): %s" % (bool(clone), text))
            check(calls == [] and len(os.listdir(DH.runs_dir())) == runs_before,
                  "origin: refused before any clone or unit, no record written (clone=%s)" % bool(clone))
        check([c[0][:2] for c in GIT_CALLS] == [["git", "fetch"]] + [["git", "grep"]] and GIT_CALLS[0][1].get("cwd") == repo,
              "origin: one fetch, then one search, in the repo")
        check(GIT_CALLS[1][0][-3:] == [DH.ORIGIN_REF, "--", DH.EVENTS_REL] and item in GIT_CALLS[1][0],
              "origin: the search is of every shard under the events dir at origin/main, for the id (%s)" % GIT_CALLS[1][0][-3:])
        # a lookalike on origin does not file it: a note that mentions it, a spawn whose `from` is it, a longer id
        reset(events=[shard_line("note", id=item, text="x"), shard_line("spawn", **{"from": item, "name": "CHILD_OF_IT", "for": "BENCH"}),
                      shard_line("file", id=item + "_TWO", title="t")])
        calls, run = recorder()
        rc, text = launch(run)
        check(rc == 2 and "is not on origin/main" in text and calls == [],
              "origin: a note, a spawn's `from` and a longer id are not the item (%s)" % text[:60])
        # a second shard holding it is named too
        with open(os.path.join(events, "RUNNER.jsonl"), "w") as f:
            f.write(shard_line("spawn", **{"from": "X", "name": item, "for": "BENCH"}) + "\n")
        reset()
        rc, text = launch(recorder()[1])
        check(rc == 2 and text.endswith('filed" %s/OWNER.jsonl %s/RUNNER.jsonl' % (DH.EVENTS_REL, DH.EVENTS_REL)),
              "origin: every local shard that holds it is named (%s)" % text[-70:])
        # nowhere locally either: said, not guessed
        reset()
        rc, text = launch(recorder()[1], known={"GHOST_ITEM_IN_NO_SHARD"}, it="GHOST_ITEM_IN_NO_SHARD")
        check(rc == 2 and "is not on origin/main; no local shard holds it either" in text, "origin: no shard holds it: %s" % text)
        # a failed fetch: said on a refusal (origin/main may be stale), not on a pass
        reset(fetch_rc=1)
        rc, text = launch(recorder()[1])
        check(rc == 2 and "fetch exit 1" in text and "may be stale" in text and text.count("\n") == 0,
              "origin: a failed fetch is named on the same refusal line (%s)" % text[-70:])
        reset(fetch_rc=1, events=[shard_line("file", id=item, title="t")])
        calls, run = recorder()
        rc, text = launch(run)
        check(rc == 0 and "fetch" not in text and calls and calls[0][0][0] == "systemd-run",
              "origin: the item found on origin/main is allowed even when the fetch failed (%s)" % text[:40])
        # an unreadable git is a refusal, not a pass
        reset(grep_rc=128)
        calls, run = recorder()
        rc, text = launch(run)
        check(rc == 2 and "cannot read origin/main" in text and calls == [], "origin: git grep failing is a refusal, not a pass (%s)" % text[:70])
        # allowed: filed on origin/main as a `file` event (compact and spaced JSON), one fetch then one search, the unit starts
        for line in (json.dumps({"seat": "OWNER", "event": "file", "id": item, "title": "t"}),
                     json.dumps({"seat": "OWNER", "event": "file", "id": item, "title": "t"}, separators=(",", ":"))):
            reset(events=[shard_line("note", id=item, text="x"), line])
            calls, run = recorder()
            rc, text = launch(run)
            check(rc == 0 and calls and calls[0][0][0] == "systemd-run" and "DETACHED " in text and
                  [c[0][:2] for c in GIT_CALLS] == [["git", "fetch"], ["git", "grep"]],
                  "origin: filed on origin/main -> allowed, the unit starts (%s)" % text[:40])
        # allowed: a `spawn` event carries the id in `name` (RUNNER spawns files nothing with an id)
        spawned = "SPAWNED_BY_RUNNER_FIX_X"
        reset(events=[shard_line("spawn", **{"from": item, "name": spawned, "for": "BENCH", "title": "t"})])
        calls, run = recorder()
        rc, text = launch(run, known={spawned}, it=spawned)
        check(rc == 0 and calls and calls[0][0][0] == "systemd-run" and ("--unit" in calls[0][0]),
              "origin: a spawn event whose name is the item files it -> allowed (%s)" % text[:40])
        reset(events=[shard_line("spawn", **{"from": spawned, "name": "CHILD_OF_SPAWNED", "for": "BENCH"})])
        rc, text = launch(recorder()[1], known={spawned}, it=spawned)
        check(rc == 2 and "is not on origin/main" in text, "origin: being only the `from` of a spawn does not file it")
    finally:
        DH.REPO = real_repo
        if real_pool is None:
            os.environ.pop("RM_DETACHED_POOL", None)
        else:
            os.environ["RM_DETACHED_POOL"] = real_pool
        ORIGIN.update({"events": None, "fetch_rc": 0, "grep_rc": None})


def units_runner(states, log=None):
    """Answers `systemctl --user show -p ActiveState` from `states` (unit -> state; absent = not-found) and the origin check;
    any other call (./sync, scratch_clone, systemd-run) is logged and succeeds."""
    log = [] if log is None else log

    def run(argv, **kw):
        if argv[:2] in (["git", "fetch"], ["git", "grep"]):
            return fake_origin_git(argv, kw)
        if argv[:3] == ["systemctl", "--user", "show"]:
            u = argv[-1]
            if states.get(u, "") is None:       # systemd says it has no such unit (a collected one)
                r = R(1, "")
                r.stderr = "Unit %s not found." % u
                return r
            if u in states:
                return R(0, states[u] + "\n") if "ActiveState" in argv else R(0, "loaded\n")
            return R(0, "inactive\n") if "ActiveState" in argv else R(0, "not-found\n")
        log.append((list(argv), kw))
        if argv and argv[0] == "python3" and "scratch_clone.py" in " ".join(argv):     # a fresh clone at --name
            os.makedirs(os.path.join(POOL, "clones", argv[argv.index("--name") + 1], ".git"), exist_ok=True)
            open(os.path.join(POOL, "clones", argv[argv.index("--name") + 1], "sync"), "w").close()
        return R(0, "")
    return log, run


def test_midreturn():
    os.environ["RM_DETACHED_POOL"] = POOL
    real_wait = getattr(DH, "RETURN_WAIT_S", None)
    try:
        _test_midreturn()
    finally:
        os.environ.pop("RM_DETACHED_POOL", None)
        if real_wait is not None:
            DH.RETURN_WAIT_S = real_wait


def keeping_returner(text):
    """Stands for return_clone when it keeps the clone again: records `text` as the run's steps, never `returned`."""
    seen = []

    def ret(unit, now=None, runner=None, root=None, **kw):
        seen.append(unit)
        rec = DH.read_record(unit, root)
        rec["return_steps"] = [text]
        DH.write_record(rec, root)
        return 1, text
    return seen, ret


def giving_returner():
    """Stands for return_clone when it gives the clone back: the clone goes and the record reads returned."""
    seen = []

    def ret(unit, now=None, runner=None, root=None, **kw):
        seen.append(unit)
        rec = DH.read_record(unit, root)
        if os.path.isdir(rec["clone"]):
            shutil.rmtree(rec["clone"])
        rec.update(returned=now or T0, return_steps=["bundle none (nothing left to bundle)"])
        DH.write_record(rec, root)
        return 0, "RETURNED %s: bundle none (nothing left to bundle)" % unit
    return seen, ret


def _kept_launch(item, states, returner, sleep=lambda s: None):
    """A launch of `item` with DH.CLONE_RETURNER standing in for return_clone, in the test pool."""
    real_pool, real_ret = os.environ.get("RM_DETACHED_POOL"), getattr(DH, "CLONE_RETURNER", None)
    os.environ["RM_DETACHED_POOL"] = POOL
    DH.CLONE_RETURNER = returner
    ORIGIN.update({"events": [json.dumps({"seat": "BENCH", "event": "file", "id": item, "title": "t"})]})
    log, run = units_runner(states)
    try:
        rc, text = _mr_launch(item, run, sleep)
    finally:
        DH.CLONE_RETURNER = real_ret
        ORIGIN.update({"events": None, "fetch_rc": 0, "grep_rc": None})
        if real_pool is None:
            os.environ.pop("RM_DETACHED_POOL", None)
        else:
            os.environ["RM_DETACHED_POOL"] = real_pool
    return rc, text, log


def t_a_kept_clone_is_returned_by_the_launch():
    """Boundary page design/specs/2026-11-21-launch-returns-a-kept-clone/boundary.md. Measured 2026-11-21 1:40 PM PST:
    four finished Pyrelands runs held RIMMANDRAKE_ROUTE_PYRELANDS_VISIT_THREE_FAILURES_BACK.det, each return had kept it
    ("a process is working in it": a sibling run was still in it), and the tick's launch was refused twice."""
    os.environ["RM_DETACHED_POOL"] = POOL
    try:
        item = "KEPT_CLONE_RETURNED_BY_LAUNCH"
        u1, clone = det_clone(item, status="finished")
        u2, _ = det_clone(item, status="finished", path=clone)
        os.makedirs(os.path.join(clone, ".git"), exist_ok=True)
    finally:
        os.environ.pop("RM_DETACHED_POOL", None)
    seen, ret = giving_returner()
    rc, text, log = _kept_launch(item, {}, ret)
    check(rc == 0 and sorted(seen) == sorted([u1, u2]) and len(_mr_starts(log)) == 1,
          "kept: the launch runs each kept holder's return itself, once, and goes on (rc %s, returned %s): %s"
          % (rc, seen, text[:160]))
    check(text.count("NOTE (form, repaired): ") >= 1 and u1 in text and u2 in text,
          "kept: the launch text carries one form NOTE naming each unit it returned: %s" % text[-300:])


def t_a_return_that_keeps_again_is_refused_with_its_reason():
    os.environ["RM_DETACHED_POOL"] = POOL
    try:
        item = "KEPT_CLONE_KEPT_AGAIN"
        unit, clone = det_clone(item, status="finished")
        os.makedirs(os.path.join(clone, ".git"), exist_ok=True)
    finally:
        os.environ.pop("RM_DETACHED_POOL", None)
    why = "kept %s: a process is working in it" % clone
    seen, ret = keeping_returner(why)
    rc, text, log = _kept_launch(item, {}, ret)
    check(rc == 2 and seen == [unit] and "return --unit " + unit in text and "--clone " + clone in text
          and "a process is working in it" in text and _mr_starts(log) == [] and _mr_syncs(log) == [],
          "kept: a return that keeps the clone again is refused once, naming return, --clone and its reason: %s" % text[:300])


def t_a_live_or_dead_holder_is_never_returned_by_the_launch():
    os.environ["RM_DETACHED_POOL"] = POOL
    try:
        item = "KEPT_CLONE_BESIDE_A_LIVE_RUN"
        kept, clone = det_clone(item, status="finished")
        live, _ = det_clone(item, status="running", path=clone)
        dead_item = "KEPT_CLONE_DEAD_RUN"
        dead, dclone = det_clone(dead_item, status="running")
        returning_item = "KEPT_CLONE_STILL_RETURNING"
        ret_unit, rclone = det_clone(returning_item, status="finished")
        for c in (clone, dclone, rclone):
            os.makedirs(os.path.join(c, ".git"), exist_ok=True)
    finally:
        os.environ.pop("RM_DETACHED_POOL", None)
    seen, ret = giving_returner()
    rc, text, log = _kept_launch(item, {live: "active"}, ret)
    check(rc == 2 and seen == [] and live in text and _mr_starts(log) == [],
          "kept: a live run beside a kept one: no return runs, refused at once: %s" % text[:160])
    rc, text, log = _kept_launch(dead_item, {}, ret)
    check(rc == 2 and seen == [] and "finish --unit " + dead in text and _mr_starts(log) == [],
          "kept: a dead run (finish never ran) is never returned by the launch: %s" % text[:160])
    real_wait = DH.RETURN_WAIT_S
    DH.RETURN_WAIT_S = 0
    try:
        rc, text, log = _kept_launch(returning_item, {ret_unit + "-return": "active"}, ret)
    finally:
        DH.RETURN_WAIT_S = real_wait
    check(rc == 2 and seen == [] and ret_unit + "-return" in text,
          "kept: a run still giving the clone back is waited for, never returned again: %s" % text[:160])


def t_a_kept_return_records_why():
    os.environ["RM_DETACHED_POOL"] = POOL
    try:
        # a long pool path, as at ./publish's checkout: the reason must survive the refusal's clip
        unit, clone = det_clone("KEPT_RETURN_RECORDS_WHY_BUSY_ON_A_LONG_POOL_PATH" + "_LONG" * 24)
        rc, text = DH.return_clone(unit, now=T0 + 10, runner=units_runner({})[1], evictor=fake_evictor()[1],
                                   busy=lambda c: True, scan=lambda u, since=None: ([], ""))
        rec = DH.read_record(unit)
        check("a process is working in it" in " ".join(rec.get("return_steps") or []) and not rec.get("returned"),
              "kept: a busy return writes its reason into return_steps, never returned: %s" % rec.get("return_steps"))
        held = DH.clone_holders(clone, units_runner({})[1], now=T0 + 20)
        check(held and "left no steps" not in held[0][2] and "a process is working in it" in held[0][2],
              "kept: the later refusal names why the return kept it: %s" % (held[0][2][:200] if held else held))
        unit, clone = det_clone("KEPT_RETURN_RECORDS_WHY_MATE")
        mate, _ = det_clone("KEPT_RETURN_RECORDS_WHY_MATE", status="running", path=clone)
        DH.return_clone(unit, now=T0 + 10, runner=units_runner({mate: "active"})[1], evictor=fake_evictor()[1],
                        busy=not_busy)
        rec = DH.read_record(unit)
        check(mate in " ".join(rec.get("return_steps") or []) and not rec.get("returned"),
              "kept: a return kept for a live mate names the mate in return_steps: %s" % rec.get("return_steps"))
    finally:
        os.environ.pop("RM_DETACHED_POOL", None)


def _mr_launch(item, run, sleep=None, clone=None):
    kw = {} if sleep is None else {"sleep": sleep}
    try:
        return DH.launch("BENCH", item, "Build.", "sonnet", None, 5, now=T0 + 900, runner=run, known={item}, clone=clone, **kw)
    except TypeError:               # a launch with no wait at all (the base): run its real path, so the race shows
        return DH.launch("BENCH", item, "Build.", "sonnet", None, 5, now=T0 + 900, runner=run, known={item}, clone=clone)


def _mr_starts(log):
    return [c for c in log if c[0][:1] == ["systemd-run"]]


def _mr_syncs(log):
    return [c for c in log if c[0][:1] == ["./sync"]]


def _test_midreturn():
    global ORIGIN
    # 1. the race as measured: the run before has FINISHED (Conductor log line written) and its return unit is still
    # bundling. Launch must wait, see the record returned and the clone gone, then make a fresh clone, never ./sync the old one.
    item = "RACE_ITEM_RETURNING"
    ORIGIN.update({"events": [json.dumps({"seat": "BENCH", "event": "file", "id": item, "title": "t"})]})
    unit, clone = det_clone(item, status="finished")
    os.makedirs(os.path.join(clone, ".git"), exist_ok=True)
    states = {unit: "inactive", unit + "-return": "active"}
    log, run = units_runner(states)
    slept = []

    def sleep(s):                   # the return lands while launch waits
        slept.append(s)
        if len(slept) == 2:
            shutil.rmtree(clone)
            rec = DH.read_record(unit)
            rec["returned"] = T0 + 905
            DH.write_record(rec)
            states[unit + "-return"] = "inactive"
    rc, text = _mr_launch(item, run, sleep)
    check(rc == 0 and len(slept) >= 2 and _mr_syncs(log) == [] and len(_mr_starts(log)) == 1 and "made " in text,
          "midreturn: a launch while the clone is being returned waits for the return, then makes a fresh clone "
          "(rc %s, slept %d, syncs %d): %s" % (rc, len(slept), len(_mr_syncs(log)), text[:120]))
    # 2. still returning when the wait runs out: refused before any sync or unit, naming the return unit and what passes
    item = "RACE_ITEM_STILL_RETURNING"
    ORIGIN.update({"events": [json.dumps({"seat": "BENCH", "event": "file", "id": item, "title": "t"})]})
    unit, clone = det_clone(item, status="finished")
    os.makedirs(os.path.join(clone, ".git"), exist_ok=True)
    log, run = units_runner({unit: "inactive", unit + "-return": "active"})
    DH.RETURN_WAIT_S = 30
    rc, text = _mr_launch(item, run, lambda s: None)
    check(rc == 2 and text.startswith("refused:") and unit + "-return" in text and "launch again" in text
          and _mr_syncs(log) == [] and _mr_starts(log) == [] and os.path.isdir(clone),
          "midreturn: a clone still returning after the wait is refused, nothing synced or started: %s" % text[:160])
    # 2b. the unit itself still deactivating (finish, wrapup and the return's start are its ExecStopPost) also waits
    log, run = units_runner({unit: "deactivating"})
    rc, text = _mr_launch(item, run, lambda s: None)
    check(rc == 2 and "deactivating" in text and _mr_starts(log) == [],
          "midreturn: a finished run whose unit is still in its stop steps holds the clone: %s" % text[:140])
    # 3. a live run holds it: refused at once (no waiting on a run that may last hours)
    item = "RACE_ITEM_LIVE_RUN"
    ORIGIN.update({"events": [json.dumps({"seat": "BENCH", "event": "file", "id": item, "title": "t"})]})
    unit, clone = det_clone(item, status="running")
    os.makedirs(os.path.join(clone, ".git"), exist_ok=True)
    log, run = units_runner({unit: "active"})
    slept = []
    rc, text = _mr_launch(item, run, slept.append)
    check(rc == 2 and unit in text and "running" in text and slept == [] and _mr_starts(log) == [] and _mr_syncs(log) == [],
          "midreturn: a clone a live run holds is refused at once: %s" % text[:140])
    # 4. a dead run (record 'running', unit gone: the 2026-11-14 stale records) is refused with the finish/return commands
    log, run = units_runner({})
    rc, text = _mr_launch(item, run, slept.append)
    check(rc == 2 and "finish --unit " + unit in text and "return --unit " + unit in text and _mr_starts(log) == [],
          "midreturn: a dead run's clone is refused, naming finish then return: %s" % text[:160])
    check(DH.live_status(DH.read_record(unit), runner=run, now=T0 + 900) == "dead"
          if hasattr(DH, "live_status") else False, "midreturn: a run whose unit is gone reads 'dead'")
    st = DH.status(runner=run)
    line = [ln for ln in st.splitlines() if unit in ln]
    check(line and "running" not in line[0].split("item")[0] and "dead" in line[0].lower(),
          "midreturn: status never reads 'running' for a run whose unit is gone: %s" % (line[0][:120] if line else st[:120]))
    log, run = units_runner({unit: None})
    check(DH.live_status(DH.read_record(unit), runner=run, now=T0 + 900) == "dead"
          if hasattr(DH, "live_status") else False, "midreturn: a run whose unit systemd no longer knows (not-found) reads 'dead'")
    # 4b. a fresh 'launching' record (systemd-run not yet returned) is not dead
    young = {"status": "launching", "unit": "rm-young", "at": T0 + 890}
    check(hasattr(DH, "live_status") and DH.live_status(young, runner=run, now=T0 + 900) == "launching",
          "midreturn: a record launching a few seconds ago is not called dead")
    # 4c. a dead run no longer blocks another run's return of the same clone
    mate, _ = det_clone(item, status="finished", path=clone)
    rc, text = DH.return_clone(mate, now=T0 + 950, runner=run, evictor=fake_evictor()[1], busy=not_busy)
    check(text.startswith("RETURNED") and unit not in text,
          "midreturn: a dead run's stale record does not keep another run's clone: %s" % text[:120])
    # 5. a clone its return KEPT (a bundle failed): refused, naming return --unit and the --clone escape
    item = "RACE_ITEM_KEPT"
    ORIGIN.update({"events": [json.dumps({"seat": "BENCH", "event": "file", "id": item, "title": "t"})]})
    unit, clone = det_clone(item, status="finished")
    os.makedirs(os.path.join(clone, ".git"), exist_ok=True)
    log, run = units_runner({})
    real_returner = getattr(DH, "CLONE_RETURNER", None)
    DH.CLONE_RETURNER = keeping_returner("KEPT %s: bundle failed" % unit)[1]   # the launcher's own return keeps it again
    try:
        rc, text = _mr_launch(item, run, lambda s: None)
    finally:
        DH.CLONE_RETURNER = real_returner
    check(rc == 2 and "return --unit " + unit in text and "--clone " + clone in text and _mr_starts(log) == [],
          "midreturn: a clone its return kept is refused, naming return and --clone: %s" % text[:160])
    rc, text = _mr_launch(item, run, lambda s: None, clone=clone)
    check(rc == 0 and len(_mr_starts(log)) == 1, "midreturn: --clone takes a kept clone as it stands: %s" % text[:80])
    # 5b. a returned record and an old finished one whose clone is gone do not block: the clone is simply reused
    item = "RACE_ITEM_CLEAR"
    ORIGIN.update({"events": [json.dumps({"seat": "BENCH", "event": "file", "id": item, "title": "t"})]})
    unit, clone = det_clone(item, status="finished")
    rec = DH.read_record(unit)
    rec["returned"] = T0
    DH.write_record(rec)
    os.makedirs(os.path.join(clone, ".git"), exist_ok=True)
    open(os.path.join(clone, "sync"), "w").close()   # a whole clone has its ./sync
    log, run = units_runner({})
    rc, text = _mr_launch(item, run, lambda s: None)
    check(rc == 0 and len(_mr_syncs(log)) == 1 and "reused " in text, "midreturn: a returned run's clone is reused: %s" % text[:80])
    # 6. the stop steps run when the clone is gone: the working directory carries systemd's '-' (missing is not fatal)
    argv = ([c for c in log if c[0][:1] == ["systemd-run"]] or [([], {})])[-1][0]
    check("--working-directory" not in argv and "WorkingDirectory=-" + clone in argv,
          "midreturn: the unit's WorkingDirectory is '-'-prefixed, so ExecStopPost survives a gone clone (measured: runs in /)")
    # 7. finish on a run whose clone is gone records it finished and logs it; no note is attempted in a missing dir
    unit, clone = det_clone("RACE_ITEM_GONE_FINISH", status="running")
    shutil.rmtree(clone)
    calls = []

    def frun(argv, **kw):
        if kw.get("cwd") and not os.path.isdir(kw["cwd"]):
            raise FileNotFoundError(kw["cwd"])
        calls.append(argv)
        return R(0, "")
    try:
        rc, text = DH.finish(unit, now=T0 + 999, env={}, runner=frun)
    except Exception as e:  # noqa: BLE001
        rc, text = 99, "raised %r" % e
    check(rc == 0 and DH.read_record(unit)["status"] == "finished" and "gone" in text,
          "midreturn: finish records a run whose clone is gone, and says so: %s" % text[:120])
    ORIGIN.update({"events": None, "fetch_rc": 0, "grep_rc": None})


def _claude_json(total=1.25, models=(("claude-opus-5-5", 1.0), ("claude-haiku-5-5", 0.25)), result="Built it."):
    """A claude -p result in the key order measured 2026-11-15 (total_cost_usd near the head, result near the end)."""
    d = {"duration_api_ms": 1, "stop_reason": "end_turn", "session_id": "s"}
    if total is not None:
        d["total_cost_usd"] = total
    d["usage"] = {"input_tokens": 10, "output_tokens": 5, "cache_creation_input_tokens": 0, "cache_read_input_tokens": 0}
    if models is not None:
        d["modelUsage"] = {m: {"inputTokens": 1, "outputTokens": 0, "cacheReadInputTokens": 0,
                               "cacheCreationInputTokens": 0, "costUSD": c} for m, c in models}
    d.update(is_error=False, subtype="success", result=result, type="result", uuid="u")
    return json.dumps(d)


def _overwrite_head(text, head):
    """What systemd's StandardOutput=file: did: a later writer starts at offset 0 and writes over the first bytes."""
    return head + text[len(head):] if len(head) < len(text) else head


def test_result_kept_whole():
    """RIMMANDRAKE_KEEP_RUN_RESULT_WHOLE_FINISH_WRITES_OVER (measured 2026-11-15: 238 of 248 result files began
    "FINISHED rm-detached-...", total_cost_usd gone)."""
    calls, run = recorder()
    DH.launch("BENCH", "SOME_ITEM_TO_BUILD", "b", "opus", 600, 15, now=T0 + 3, runner=run, known=KNOWN, clone=CLONE)
    argv = calls[0][0]
    unit = argv[argv.index("--unit") + 1]
    rec = DH.read_record(unit)
    check(not any(a.startswith(("StandardOutput=file:", "StandardError=file:")) for a in argv)
          and "StandardOutput=append:" + rec["out"] in argv and "StandardError=append:" + rec["err"] in argv,
          "whole: the unit's out and err are opened append:, never file: (a later writer cannot overwrite the head)")
    # the finish step's own line: run main's finish path in a child whose stdout and stderr are the result file opened
    # at offset 0 without O_APPEND, exactly as systemd's file: hands it to every ExecStopPost
    body = _claude_json()
    with open(rec["out"], "w") as f:
        f.write(body)
    child = ("import sys; sys.path.insert(0, %r); import detached_helper as DH\n"
             "DH.finish = lambda unit, **k: (0, 'FINISHED %%s: scope gone; note exit 0; ' %% unit + 'x' * 400)\n"
             "sys.exit(DH.main(['finish', '--unit', %r]))\n" % (HERE, unit))
    fd = os.open(rec["out"], os.O_WRONLY)
    try:
        p = subprocess.run([sys.executable, "-c", child], stdout=fd, stderr=fd, stdin=subprocess.DEVNULL, timeout=60,
                           env=dict(os.environ))
    finally:
        os.close(fd)
    with open(rec["out"]) as f:
        after = f.read()
    try:
        whole = json.loads(after) == json.loads(body)
    except ValueError:
        whole = False
    check(p.returncode == 0 and whole, "whole: the finish line never lands in the result file (it begins %r)" % after[:40])
    try:
        with open(DH.finish_log_path(unit)) as f:
            flog = f.read()
    except (AttributeError, OSError):
        flog = ""
    check("FINISHED " + unit in flog, "whole: the finish line goes to the run's own finish log instead")
    # the record carries the measured dollars and tokens, read before anything else touches the file
    fcalls, frun = recorder(out="PUBLISHED abcdef1234567")
    DH.finish(unit, now=T0 + 900, env={"SERVICE_RESULT": "success", "EXIT_CODE": "exited", "EXIT_STATUS": "0"},
              runner=frun)
    r2 = DH.read_record(unit)
    check(r2.get("cost_usd") == 1.25 and isinstance(r2.get("tokens"), int) and r2.get("token_unit") == "weighted_v2",
          "cost: finish records claude's total_cost_usd and the weighted_v2 tokens (%s, %s %s)"
          % (r2.get("cost_usd"), r2.get("tokens"), r2.get("token_unit")))
    # a result whose model is not in role_launch.MODEL_PRICES is UNMEASURED by name, never weighed as another model
    nop = os.path.join(TMP, "noprice.out")
    with open(nop, "w") as f:
        json.dump({"result": "x", "usage": {"input_tokens": 10, "output_tokens": 5, "cache_creation_input_tokens": 0,
                                            "cache_read_input_tokens": 0}}, f)
    nrec = {"out": nop, "err": nop + ".err", "model": "claude-nonesuch-9-9"}
    _, ntok, _ = DH.outcome(nrec, {"SERVICE_RESULT": "success"})
    check(ntok is None and "claude-nonesuch-9-9" in (nrec.get("unknown_model") or ""),
          "cost: a model not in the price table is UNMEASURED by name (%s, %r)" % (ntok, nrec.get("unknown_model")))
    nt = non_systemctl(fcalls)[0][0]
    nt = nt[nt.index("--text") + 1]
    # the owner, 2026-11-16 1:08 PM PST: "Please speak in terms of weighted tokens not money." The record keeps its
    # dollars; the Conductor log line says weighted tokens and no dollar figure (RIMMANDRAKE_ENACT_TOKENS_NOT_DOLLARS_
    # NO_LIVE_HOLD). The item note, which a resumed or continued run reads, carries no spend figure at all
    # (RIMMANDRAKE_HIDE_CAP_STOP_FROM_RESUMED_RUN_READER_TRIMMED)
    with open(os.environ["RM_CONDUCTOR_LOG"]) as f:
        clog = [ln for ln in f.read().splitlines() if unit in ln and "DETACHED RUN ENDED" in ln]
    check(clog and "weighted tokens" in clog[-1] and not re.search(r"USD|\$\s*\d", clog[-1]),
          "cost: the log line says weighted tokens, never a dollar figure (%s)" % (clog[-1][:160] if clog else "no line"))
    check("weighted tokens" not in nt and not re.search(r"USD|\$\s*\d", nt),
          "cost: the item note carries no spend figure (%s)" % nt[:160])
    # the pure readers
    check(DH.result_cost(json.loads(_claude_json(total=None))) == (1.25, "sum of modelUsage costUSD"),
          "cost: no total_cost_usd -> the sum of modelUsage costUSD (equal on the 10 whole files of 2026-11-15)")
    check(DH.result_cost(json.loads(_claude_json(total=None, models=None)))[0] is None
          and DH.result_cost(None)[0] is None and DH.result_cost({"total_cost_usd": True})[0] is None,
          "cost: no dollars in the result -> None (UNMEASURED), never 0")
    head = "FINISHED %s: scope ...; publish 88d758f130\n" % unit
    lost_total = _overwrite_head(_claude_json(), head[:120])
    check(DH.recover_cost(lost_total) == (1.25, "sum of modelUsage costUSD in the surviving tail"),
          "recover: total overwritten, modelUsage whole -> its sum (%s)" % (DH.recover_cost(lost_total),))
    lost_all = _overwrite_head(_claude_json(), head + "y" * (_claude_json().index('"is_error"') - len(head)))
    check(DH.recover_cost(lost_all)[0] is None and "UNMEASURED" in DH.recover_cost(lost_all)[1],
          "recover: total and modelUsage overwritten -> UNMEASURED, never one model's costUSD as the total")
    tail_total = 'FINISHED x\n', '"session_id":"s","total_cost_usd":2.5,"usage":{}}'
    check(DH.recover_cost("".join(tail_total)) == (2.5, "total_cost_usd in the surviving tail"),
          "recover: total_cost_usd survives -> it")
    sneaky = _overwrite_head(_claude_json(total=None, models=None, result='I saw "total_cost_usd": 9.0 here'), head[:60])
    check(DH.recover_cost(sneaky)[0] is None, "recover: a total_cost_usd quoted inside the result text is not a measurement")
    check(DH.recover_cost(_claude_json()) == (1.25, "total_cost_usd"), "recover: a whole file -> its total")
    # the backfill of runs finished before this: what survives is read back, the rest marked UNMEASURED, nothing guessed
    broot = os.path.join(TMP, "backfill")
    old = {"lost_total": lost_total, "lost_all": lost_all, "empty": ""}
    for name, body in list(old.items()) + [("recent", lost_total)]:
        out = os.path.join(broot, name + ".out.json")
        os.makedirs(broot, exist_ok=True)
        with open(out, "w") as f:
            f.write(body)
        DH.write_record({"unit": name, "status": "finished", "out": out,
                         "ended": T0 + (9000 if name == "recent" else 0)}, root=broot)
    rc, said = DH.backfill_cost(root=broot, now=T0 + 9100)
    check(rc == 0 and "1 measured, 2 UNMEASURED, 1 ended under an hour ago" in said
          and "cost_usd" not in DH.read_record("lost_total", root=broot),
          "backfill: a dry run counts and writes nothing (%s)" % said.splitlines()[0])
    DH.backfill_cost(apply=True, root=broot, now=T0 + 9100)
    got = {n: DH.read_record(n, root=broot).get("cost_usd") for n in list(old) + ["recent"]}
    check(got == {"lost_total": 1.25, "lost_all": "UNMEASURED", "empty": "UNMEASURED", "recent": None},
          "backfill: --apply writes the recovered dollars and UNMEASURED, and leaves a run that just ended (%s)" % got)


def scope_runner(kill_out, kill_rc=1, stop_out="", stop_rc=5, state="inactive"):
    said = []

    def run(argv, **kw):
        said.append(argv)
        if argv[:3] == ["systemctl", "--user", "kill"]:
            return R(kill_rc, kill_out)
        if argv[:3] == ["systemctl", "--user", "stop"]:
            return R(stop_rc, stop_out)
        if argv[:3] == ["systemctl", "--user", "show"]:
            return R(0, state)
        return R(0, "")
    return said, run


def test_scope_quiet_when_gone():
    """RIMMANDRAKE_QUIET_CLEAN_FINISH_SCOPE_ALREADY_GONE: claude left its scope and systemd collected it, so a clean
    finish read 'kill ... exit 1: Failed to kill unit ...: Unit ... not loaded.; stop ... exit 5' on every run."""
    sc = "claude-seat-BENCH-u.scope"
    _, run = scope_runner("Failed to kill unit %s: Unit %s not loaded." % (sc, sc), 1,
                          "Failed to stop %s: Unit %s not loaded." % (sc, sc), 5)
    line = DH.stop_scope("BENCH", "u", run)
    check("already gone" in line and "Failed" not in line and "exit" not in line and "FAILED" not in line,
          "scope: a scope systemd no longer has reads clean (%s)" % line)
    said, run = scope_runner("Failed to kill unit %s: Access denied" % sc, 1, "", 0, "active")
    line = DH.stop_scope("BENCH", "u", run)
    check("FAILED" in line and "Access denied" in line and any(a[:3] == ["systemctl", "--user", "stop"] for a in said),
          "scope: a kill that fails any other way stays loud, and the stop is still tried (%s)" % line[:90])
    said, run = scope_runner("", 0, "", 0, "inactive")
    line = DH.stop_scope("BENCH", "u", run)
    check("FAILED" not in line and "kill" in line and "inactive" in line,
          "scope: a scope that was still there is killed and said so (%s)" % line[:90])


def test_hook_points_here():
    hook = os.path.join(HERE, "..", "..", "..", ".claude", "hooks", "block_agent_over_slots.py")
    with open(hook, encoding="utf-8") as f:
        src = f.read()
    check("detached_helper.py launch" in src, "hook: the drain refusal names detached_helper.py launch")


def test_owed_close():
    """RIMMANDRAKE_FLAG_DETACHED_SUCCESS_LEAVING_ITEM_OPEN: a run that ends success with its item still open says so."""
    foot = DH.brief_message("b", "SOME_ITEM_TO_BUILD", "BENCH", "C")
    check("cli.py claim SOME_ITEM_TO_BUILD" in foot and "cli.py close SOME_ITEM_TO_BUILD --sha" in foot
          and DH.LEFT_OPEN in foot, "owed: the brief says claim at start, close or note LEFT OPEN: at the end")
    check("cli.py wait SOME_ITEM_TO_BUILD --until" in foot and "left_open_continue.py" in foot,
          "owed: the brief says to put a dated wait on an item whose left work is the owner's or the Conductor's "
          "(RIMMANDRAKE_TEACH_HELPER_WAIT_OWNERS_TURN_RELAUNCHED_FABLE)")
    ok_env = {"SERVICE_RESULT": "success", "EXIT_CODE": "exited", "EXIT_STATUS": "0"}

    def ended(state, notes, env=None, item="SOME_ITEM_TO_BUILD", unreadable=False, report=None, rest=None):
        unit, _ = det_clone(item, status="running", path=CLONE)
        with open(os.path.join(TMP, unit + ".out"), "w") as f:
            json.dump({"result": report or "Fixed 17 gaps; PUBLISHED abc.", "usage": {"input_tokens": 1, "output_tokens": 1}}, f)
        open(os.environ["RM_CONDUCTOR_LOG"], "w").close()
        calls, run = recorder(out="PUBLISHED abcdef1234567")
        seen = []

        def reader(clone, it):
            seen.append((clone, it))
            return None if unreadable else {"state": state, "notes": notes, "rest": dict(rest, unit=unit) if rest else {}}
        DH.finish(unit, now=T0 + 900, env=ok_env if env is None else env, runner=run, item_reader=reader)
        note = [c[0] for c in non_systemctl(calls) if c[0][2:4] == ["note", item]]
        with open(os.environ["RM_CONDUCTOR_LOG"]) as f:
            log = f.read()
        return unit, (note[0][note[0].index("--text") + 1] if note else ""), log, DH.read_record(unit), seen

    line = "item SOME_ITEM_TO_BUILD is still proposed: close it with its published sha or say what is left"
    unit, nt, log, rec, seen = ended("proposed", [])
    check(seen == [(CLONE, "SOME_ITEM_TO_BUILD")], "owed: finish reads the item in the run's clone (%s)" % seen)
    check(("run %s ended success; " % unit) + line in nt, "owed: the note names the open item (%s)" % nt[-160:])
    check(line in log and ("run %s ended success" % unit) in log, "owed: the Conductor log line names it (%s)" % log[-200:])
    check(line in (rec.get("owed_close") or ""), "owed: the record carries the line for the status page")
    for what, args in (("a closed item", ("done", [])),
                       ("a LEFT OPEN note since the start", ("claimed", [
                           {"event": "note", "id": "SOME_ITEM_TO_BUILD", "ts": DH.iso(T0 + 60),
                            "text": "LEFT OPEN: the live test is UNRUN (command in the item)"}])),
                       ("an unreadable ledger", ("proposed", [], None, "SOME_ITEM_TO_BUILD", True))):
        _, nt, log, rec, _ = ended(*args)
        check("is still" not in nt and "is still" not in log and not rec.get("owed_close"),
              "owed: %s flags nothing (%s)" % (what, nt[-120:]))
    _, nt, log, rec, _ = ended("proposed", [{"event": "note", "id": "SOME_ITEM_TO_BUILD", "ts": DH.iso(T0 - 3600),
                                             "text": "LEFT OPEN: an older run's note"}])
    check(rec.get("owed_close"), "owed: a LEFT OPEN note from before this run does not excuse it")
    _, nt, log, rec, _ = ended("proposed", [], env={"SERVICE_RESULT": "exit-code", "EXIT_CODE": "exited", "EXIT_STATUS": "1"})
    check(not rec.get("owed_close") and "is still" not in nt, "owed: a failed run is not flagged as an owed close")
    _, _, _, rec, _ = ended("proposed", [])

    class It:
        def __init__(self, state):
            self.state = state
    # page 2026-11-24-close-files-its-remainder: finish files the remainder that a closed run's report declares
    said = "I closed the item.\n\n- **Not built:** the boundary page.\n"
    _, nt, log, rd, _ = ended("done", [], report=said, rest={"linked": "", "name": "RIMMANDRAKE_FINISH_SOME_UNBUILT_PARTS", "held": []})
    check("Remainder filed: RIMMANDRAKE_FINISH_SOME_UNBUILT_PARTS" in nt and "remainder filed" in " ".join(rd["steps"]),
          "remainder: finish files it and the note and the record say so (%s | %s)" % (nt[-160:], rd["steps"]))
    _, nt, log, rd, _ = ended("done", [], report=said, rest={"linked": "RIMMANDRAKE_X_Y_Z", "name": "N", "held": []})
    check("emainder" not in nt, "remainder: a linked remainder files nothing (%s)" % nt[-160:])
    _, nt, log, rd, _ = ended("done", [], report=said)
    check("could not look" in nt and rd["status"] == "finished", "remainder: an unread ledger is said and the finish goes on")

    lines = DH.owed_lines([rec, dict(rec, unit="other", owed_close="")], {"SOME_ITEM_TO_BUILD": It("proposed")}, [])
    check(len(lines) == 1 and line in lines[0], "owed: the status page line stands while the item is open (%s)" % lines)
    check(DH.owed_lines([rec], {"SOME_ITEM_TO_BUILD": It("done")}, []) == [],
          "owed: the status page line goes once the item closes")
    check(DH.owed_lines([rec], {"SOME_ITEM_TO_BUILD": It("claimed")}, [
        {"event": "note", "id": "SOME_ITEM_TO_BUILD", "ts": DH.iso(T0 + 2000), "text": "LEFT OPEN: the live half"}]) == [],
        "owed: the status page line goes once a LEFT OPEN note names what is left")


def test_windows_path():
    """RIMMANDRAKE_GIVE_DETACHED_UNITS_WINDOWS_PATH_PYTHON_EXE_VANISHED: a unit started from a timer had no /mnt/c on PATH
    and no WSL_INTEROP, so python.exe, tasklist.exe and ./game 'did not exist' (FlowWorks visit 1, 2026-11-15)."""
    apps = "/mnt/c/Users/U/AppData/Local/Microsoft/WindowsApps"
    p = DH.unit_path("/usr/bin:/bin", "/home/u/.local/bin/claude", exists=lambda x: True, isdir=lambda x: True,
                     globber=lambda pat: [apps])
    parts = p.split(":")
    check(parts[:3] == ["/home/u/.local/bin", "/usr/bin", "/bin"], "winpath: claude's dir, then the launcher's PATH")
    check("/mnt/c/Windows/System32" in parts and apps in parts and
          "/mnt/c/Windows/System32/WindowsPowerShell/v1.0" in parts, "winpath: System32, PowerShell, WindowsApps added on WSL")
    p2 = DH.unit_path("/usr/bin:/mnt/c/Windows/System32", "/usr/bin/claude", exists=lambda x: True,
                      isdir=lambda x: True, globber=lambda pat: [])
    check(p2.split(":").count("/mnt/c/Windows/System32") == 1 and p2.split(":").count("/usr/bin") == 1,
          "winpath: a dir already on PATH is not added twice (%s)" % p2)
    p3 = DH.unit_path("/usr/bin:/bin", "/usr/local/bin/claude", exists=lambda x: False, isdir=lambda x: True,
                      globber=lambda pat: [apps])
    check(p3 == "/usr/local/bin:/usr/bin:/bin", "winpath: off WSL the PATH is unchanged (%s)" % p3)
    check(DH.unit_interop({}, exists=lambda x: x == DH.WSL_SOCKET) == DH.WSL_SOCKET,
          "interop: a launcher without WSL_INTEROP gives the unit the machine's socket")
    check(DH.unit_interop({"WSL_INTEROP": "/run/WSL/9_interop"}, exists=lambda x: True) == "/run/WSL/9_interop",
          "interop: a live inherited socket is kept")
    check(DH.unit_interop({"WSL_INTEROP": "/run/WSL/9_interop"}, exists=lambda x: False) is None,
          "interop: nothing alive, nothing set")
    calls, run = recorder()
    rc, _ = DH.launch("BENCH", "SOME_ITEM_TO_BUILD", "Build the thing.", "opus", 600, 5, now=T0, runner=run,
                      known=KNOWN, clone=CLONE)
    argv = calls[0][0]
    path = [a for a in argv if a.startswith("PATH=")]
    check(rc == 0 and len(path) == 1 and path[0][5:] == DH.unit_path(os.environ.get("PATH"), DH.claude_bin()),
          "argv: the unit's PATH is unit_path's")
    soc = DH.unit_interop()
    check(("WSL_INTEROP=" + soc in argv) if soc else not any(a.startswith("WSL_INTEROP=") for a in argv),
          "argv: WSL_INTEROP set exactly when a socket is alive")


def test_launch_checks():
    gclone = os.path.join(TMP, "gate_clone")
    items = os.path.join(gclone, "infrastructure", "state", "items")
    os.makedirs(items)
    _bounded(gclone)
    with open(os.path.join(items, "SOME_ITEM_TO_BUILD.md"), "w", encoding="utf-8") as fh:
        fh.write("## spec\nmust-pass: false (prose never refuses)\n\n## launch-checks\nmust-fail: echo still green; true\n")

    def go(t, **kw):
        calls, run = recorder()
        rc, text = DH.launch("BENCH", "SOME_ITEM_TO_BUILD", "Build.", "sonnet", 600, 5, now=T0 + t, runner=run, known=KNOWN,
                             clone=gclone, **kw)
        unit = text.split()[1] if text.startswith("DETACHED ") else None
        return rc, text, [c for c in calls if c[0][0] == "systemd-run"], DH.read_record(unit) if unit else None
    rc, text, units, rec = go(700)
    check(rc == 2 and text.startswith("refused: launch check") and "still green" in text and "already passes" in text
          and "smallest fix" in text and not units, "gate: a must-fail that passes refuses before any unit (%s)" % text[:60])
    rc, text, units, rec = go(701, skip_launch_checks="Conductor: rerun wanted anyway")
    check(rc == 0 and units and (rec or {}).get("launch_checks_skipped") == "Conductor: rerun wanted anyway",
          "gate: --skip-launch-checks launches and the why is on the record")
    os.remove(os.path.join(items, "SOME_ITEM_TO_BUILD.md"))
    ev = os.path.join(gclone, *DH.EVENTS_REL.split("/"))
    os.makedirs(ev)
    with open(os.path.join(ev, "RUNNER.jsonl"), "w", encoding="utf-8") as fh:
        fh.write(json.dumps({"event": "spawn", "from": "X", "for": "RELENTLESS", "name": "SOME_ITEM_TO_BUILD",
                             "spec": "## launch-checks\nmust-pass: /no/such/gate --to x\n"}) + "\n")
    rc, text, units, rec = go(702)
    check(rc == 0 and units and "launch check did not run" in text
          and len((rec or {}).get("launch_checks_did_not_run") or []) == 1,
          "gate: a check that cannot run (exit 127) launches, said on the output and the record")
    with open(os.path.join(ev, "RUNNER.jsonl"), "w", encoding="utf-8") as fh:
        fh.write(json.dumps({"event": "spawn", "from": "X", "for": "RELENTLESS", "name": "SOME_ITEM_TO_BUILD",
                             "spec": "## launch-checks\nmust-pass: echo 28 of 42 bars not runnable; false\n"}) + "\n")
    rc, text, units, rec = go(703)
    check(rc == 2 and "28 of 42" in text and not units, "gate: a spawn's --spec block is read from the clone's shard")


def timeout_runner(state):
    """systemd-run never answers (TimeoutExpired); systemctl show reads `state` for the unit; the origin check passes."""
    calls = []

    def run(argv, **kw):
        if argv[:2] in (["git", "fetch"], ["git", "grep"]):
            return fake_origin_git(argv, kw)
        calls.append((list(argv), kw))
        if argv and argv[0].endswith("systemd-run"):
            raise subprocess.TimeoutExpired(argv, kw.get("timeout") or 60)
        if argv[:3] == ["systemctl", "--user", "show"]:
            return R(0, state + "\n") if "ActiveState" in argv else R(0, ("not-found" if state == "inactive"
                                                                           else "loaded") + "\n")
        return R(0, "")
    return calls, run


def test_launch_timeout():
    for n, (state, want_rc, want_status) in enumerate((("inactive", 1, "launch_failed"), ("active", 0, "running"))):
        calls, run = timeout_runner(state)
        try:
            rc, text = DH.launch("BENCH", "SOME_ITEM_TO_BUILD", "b", "sonnet", 600, 5, now=T0 + 900 + n, runner=run,
                                 known=KNOWN, clone=CLONE)
        except Exception as e:  # noqa: BLE001
            check(False, "timeout: a systemd-run past its timeout raised %s out of launch" % type(e).__name__)
            continue
        unit = next(c[0][c[0].index("--unit") + 1] for c in calls if c[0][0].endswith("systemd-run"))
        rec = DH.read_record(unit)
        check(rc == want_rc and rec["status"] == want_status,
              "timeout: unit %s after a silent systemd-run -> rc %s, record %s (%s)" % (state, rc, rec["status"],
                                                                                      text[:90]))
        if state == "inactive":
            check("did not answer" in (rec.get("why") or ""), "timeout: the record says systemd-run did not answer")
            later = DH.clone_holders(CLONE, run, now=T0 + 900 + DH.LAUNCH_GRACE_S + 60)
            check(not any(h[0] == unit for h in later), "timeout: the failed launch holds no clone (%d other holder(s))" % len(later))


def test_long_brief():
    """2026-11-16: Gimme Some Slack's in-game brief (94.5 KB) plus its holder packet passed Linux's 128 KB cap on one
    argument, so systemd-run failed with E2BIG on every launch. A brief that long goes in by file on stdin."""
    calls, run = recorder()
    brief = "Long brief. " + "x" * 150000
    rc, text = DH.launch("BENCH", "SOME_ITEM_TO_BUILD", brief, "sonnet", 600, 5, now=T0 + 950, runner=run, known=KNOWN,
                         clone=CLONE)
    argv = next((c[0] for c in calls if c[0][0].endswith("systemd-run")), [])
    big = max((len(a.encode()) for a in argv), default=0)
    stdin = [a for a in argv if a.startswith("StandardInput=file:")]
    path = stdin[0][len("StandardInput=file:"):] if stdin else ""
    body = open(path, encoding="utf-8").read() if path and os.path.isfile(path) else ""
    check(rc == 0 and big < DH.ARG_BRIEF_MAX and stdin and brief in body,
          "longbrief: a 150 KB brief goes in by file on stdin, no argument over the cap (rc %s, biggest %d bytes, %s)"
          % (rc, big, stdin[:1]))

    def e2big(argv, **kw):
        if argv[:2] in (["git", "fetch"], ["git", "grep"]):
            return fake_origin_git(argv, kw)
        if argv and argv[0].endswith("systemd-run"):
            raise OSError(7, "Argument list too long")
        if argv[:3] == ["systemctl", "--user", "show"]:
            return R(0, "inactive\n") if "ActiveState" in argv else R(0, "not-found\n")
        return R(0, "")
    rc, text = DH.launch("BENCH", "SOME_ITEM_TO_BUILD", "b", "sonnet", 600, 5, now=T0 + 952, runner=e2big, known=KNOWN,
                         clone=CLONE)
    check(rc == 1 and "Argument list too long" in text and "did not answer" not in text,
          "longbrief: an exec failure is recorded with its own words, not as a silent systemd-run (%s)" % text[:120])


def t_a_brief_never_rides_in_a_wrappers_argv():
    """RIMMANDRAKE_STOP_KILLING_WORKING_JUDGE_AT_FORTY_FIVE_MIN (2026-11-23): the ExplosiveKnockback blind-cycle-6 judge
    ran `kill -TERM $(pgrep -f 'lane2/plant_faults[.]py' | head -1)` to stop its own background job. Its brief named
    lane2/plant_faults.py and the brief rode in spend_watchdog.py's argv, so pgrep matched the run's own main process;
    the unit sat 600 s in stop-sigterm and then killed the working judge. A brief of any length goes in by file on
    stdin: no argument the unit's processes carry holds a phrase of it."""
    calls, run = recorder()
    phrase = "Run them with `lane2/plant_faults.py`, then SUMMARY."
    rc, text = DH.launch("BENCH", "SOME_ITEM_TO_BUILD", "Short brief. " + phrase, "sonnet", 600, 5, now=T0 + 951,
                         runner=run, known=KNOWN, clone=CLONE)
    argv = next((c[0] for c in calls if c[0][0].endswith("systemd-run")), [])
    stdin = [a for a in argv if a.startswith("StandardInput=file:")]
    path = stdin[0][len("StandardInput=file:"):] if stdin else ""
    body = open(path, encoding="utf-8").read() if path and os.path.isfile(path) else ""
    leaked = [a[:60] for a in argv if "plant_faults" in a or "Short brief." in a]
    check(rc == 0 and stdin and phrase in body and not leaked,
          "argv: a short brief goes in by file on stdin and no argument carries it (rc %s, stdin %s, leaked %s)"
          % (rc, stdin[:1], leaked[:2]))


def test_resumed_part():
    """RIMMANDRAKE_COUNT_RESUMED_RUN_TOKENS_ONCE_SESSION_TOTAL_LOGGED (measured 2026-11-19: 26 of 26 resumed runs
    recorded their whole session): a resumed run's result reports the session so far; finish records its own part."""
    import role_launch as RL
    ok_env = {"SERVICE_RESULT": "success", "EXIT_CODE": "exited", "EXIT_STATUS": "0"}

    def result(sid, inp, out, usd, **kw):
        d = {"type": "result", "subtype": "success", "is_error": False, "result": "r", "session_id": sid,
             "total_cost_usd": usd, "modelUsage": {RL.REF_MODEL: {"inputTokens": inp, "outputTokens": out,
                                                                  "cacheReadInputTokens": 0,
                                                                  "cacheCreationInputTokens": 0, "costUSD": usd}}}
        d.update(kw)
        return d

    def run(name, at, res, resume=None, done=False, **extra):
        unit = "rm-detached-bench-resumed-part-%s" % name
        out = os.path.join(TMP, unit + ".out")
        with open(out, "w") as f:
            json.dump(res, f)
        rec = {"unit": unit, "out": out, "err": out + ".err", "model": RL.REF_MODEL, "at": T0 + at, "clone": CLONE,
               "seat": "BENCH", "item": "SOME_ITEM_TO_BUILD", "status": "finished" if done else "running"}
        if resume:
            rec["resume_session"] = resume
        rec.update(extra)
        DH.write_record(rec)
        if not done:
            DH.finish(unit, now=T0 + at + 100, env=ok_env, runner=recorder(out="PUBLISHED abcdef1234567")[1],
                      item_reader=lambda c, i: None)
        return DH.read_record(unit), RL.run_tokens(res, RL.REF_MODEL)

    # an earlier run recorded before the fix (no session fields: its result file is read), then two resumes of it
    a_res = result("sess-r", 1000, 100, 2.0)
    a, a_tok = run("a", 5000, a_res, done=True, tokens=RL.run_tokens(a_res), ended=T0 + 5090)
    b, b_tot = run("b", 5100, result("sess-r", 3000, 300, 5.0), resume="sess-r")
    check(b.get("tokens") == b_tot - a_tok and b.get("session_tokens") == b_tot and b.get("session") == "sess-r",
          "resumed: a resume records its own part (%s, want %d), the session total under its own name (%s)"
          % (b.get("tokens"), b_tot - a_tok, b.get("session_tokens")))
    check(abs((b.get("cost_usd") or 0) - 3.0) < 1e-9 and b.get("session_cost_usd") == 5.0,
          "resumed: its dollars are its own part too (%s of a 5.0 session)" % b.get("cost_usd"))
    c, c_tot = run("c", 5300, result("sess-r", 4000, 400, 6.5), resume="sess-r")
    check(c.get("tokens") == c_tot - b_tot, "resumed: a second resume subtracts the largest earlier session total "
          "(%s, want %d)" % (c.get("tokens"), c_tot - b_tot))
    # a resume the spend watchdog stopped: its figure is already its own turns (spend_watchdog measures from launch)
    w, w_tok = run("w", 5500, {"type": "result", "subtype": "error_max_budget_usd", "is_error": True, "session_id":
                               "sess-r", "stopped_by": "spend_watchdog", "total_cost_usd": 1.0,
                               "usage": {"input_tokens": 500, "output_tokens": 50, "cache_creation_input_tokens": 0,
                                         "cache_read_input_tokens": 0}}, resume="sess-r")
    check(w.get("tokens") == w_tok and w.get("session_tokens") == c_tot + w_tok,
          "resumed: a watchdog stop keeps its own figure; the session total adds it (%s, %s)"
          % (w.get("tokens"), w.get("session_tokens")))
    # a resume whose earlier total is unreadable: UNMEASURED with its cause, never the session total, never 0
    u, u_tot = run("u", 5700, result("sess-lost", 9000, 900, 9.0), resume="sess-lost")
    with open(os.environ["RM_CONDUCTOR_LOG"]) as f:
        line = [ln for ln in f.read().splitlines() if u["unit"] in ln][-1]
    check(u.get("tokens") is None and "sess-lost" in (u.get("tokens_why") or "") and u.get("session_tokens") == u_tot
          and u.get("cost_usd") == "UNMEASURED" and "UNMEASURED (" in line and "{:,}".format(u_tot) not in
          line.split("weighted tokens")[0], "resumed: an unreadable earlier total is UNMEASURED with its cause (%s; %s)"
          % (u.get("tokens_why"), line[:200]))
    # a run that does not resume is recorded exactly as before
    n, n_tot = run("n", 5900, result("sess-new", 700, 70, 1.5))
    check(n.get("tokens") == n_tot and n.get("cost_usd") == 1.5 and not n.get("tokens_why"),
          "resumed: a run that does not resume records its whole result (%s, want %d)" % (n.get("tokens"), n_tot))


def _skill_warnings(text):
    return [ln for ln in text.splitlines() if ln.startswith("WARNING:") and "skills/BY_WORK.md" in ln]


def t_a_brief_naming_no_skill_gets_one_warning():
    """Boundary page design/specs/2026-11-19-brief-skill-paths/boundary.md: most skills are not registered, so a brief
    that names no skill path hands the helper none (owner, 2026-11-19)."""
    for i, brief in enumerate(("Build the thing.", "Use the rimbridge skill.", "Map: skills/BY_WORK.md, pick one.")):
        calls, run = recorder()
        rc, text = DH.launch("BENCH", "SOME_ITEM_TO_BUILD", brief, "sonnet", 600, 5, now=T0 + 1300 + i, runner=run,
                             known=KNOWN, clone=CLONE)
        check(rc == 0 and len(_skill_warnings(text)) == 1 and text.rstrip().splitlines()[-1].startswith("WARNING:"),
              "skillwarn: a brief naming no skill path ends with one WARNING naming skills/BY_WORK.md (%r: rc %s, %r)"
              % (brief, rc, text[-160:]))


def t_a_brief_naming_a_skill_gets_no_warning():
    for i, brief in enumerate(("Read skills/rimbridge/SKILL.md first.",
                               "Read `~/dev/MandrakeWorkflows/skills/efficient-subagents/SKILL.md`.",
                               r"Read D:\Luke\dev\RimMandrake\skills\rimworld-modding\SKILL.md first.")):
        calls, run = recorder()
        rc, text = DH.launch("BENCH", "SOME_ITEM_TO_BUILD", brief, "sonnet", 600, 5, now=T0 + 1310 + i, runner=run,
                             known=KNOWN, clone=CLONE)
        check(rc == 0 and not _skill_warnings(text) and "WARNING: the brief names no skill" not in text,
              "skillwarn: a brief naming a skill path gets no WARNING (%r: rc %s)" % (brief, rc))


def t_the_warning_refuses_nothing():
    calls, run = recorder()
    rc, text = DH.launch("BENCH", "SOME_ITEM_TO_BUILD", "Build the thing.", "sonnet", 600, 5, now=T0 + 1320, runner=run,
                         known=KNOWN, clone=CLONE)
    check(rc == 0 and any(c[0][0].endswith("systemd-run") for c in calls),
          "skillwarn: a warned launch still starts its unit (rc %s)" % rc)
    rc, text = DH.launch("BENCH", "NOT_AN_ITEM", "Build the thing.", "sonnet", 600, 5, now=T0 + 1321, runner=run,
                         known=KNOWN, clone=CLONE)
    check(rc == 2 and not _skill_warnings(text) and text.startswith("refused:"),
          "skillwarn: a refused launch's text stays the gate's own, no warning added (%r)" % text[:100])


def _origin_repo(name, shards):
    """A temp repo whose working-tree ledger holds `shards` (file name -> event lines); -> its path."""
    repo = os.path.join(TMP, name)
    events = os.path.join(repo, *DH.EVENTS_REL.split("/"))
    os.makedirs(events, exist_ok=True)
    for n, lines in shards.items():
        with open(os.path.join(events, n), "w") as f:
            f.write("".join(ln + "\n" for ln in lines))
    return repo


def _origin_launch(repo, item, runner, seat="BENCH"):
    real_repo, real_pool = DH.REPO, os.environ.get("RM_DETACHED_POOL")
    real_unit = os.environ.get("RM_ROLE_UNIT")
    DH.REPO, os.environ["RM_DETACHED_POOL"] = repo, os.path.join(TMP, "originpool2")
    # the caller is a launched run: the refusal path (the Conductor's own launch publishes the shard itself, tested in
    # selftest_never_refuse_conductor.py), whoever runs this test
    os.environ["RM_ROLE_UNIT"] = "rm-detached-selftest-origin-caller"
    try:
        GIT_CALLS.clear()
        ORIGIN.update({"events": [], "fetch_rc": 0, "grep_rc": None})
        return DH.launch(seat, item, "Build.", "sonnet", 600, 5, now=T0 + 330, runner=runner, known={item}, clone=CLONE)
    finally:
        DH.REPO = real_repo
        if real_unit is None:
            os.environ.pop("RM_ROLE_UNIT", None)
        else:
            os.environ["RM_ROLE_UNIT"] = real_unit
        if real_pool is None:
            os.environ.pop("RM_DETACHED_POOL", None)
        else:
            os.environ["RM_DETACHED_POOL"] = real_pool
        ORIGIN.update({"events": None, "fetch_rc": 0, "grep_rc": None})


def t_an_unpublished_item_refusal_prints_the_publish_command():
    """Boundary page design/specs/2026-11-19-launch-unpublished-item/boundary.md: the refusal names the exact command
    (Crystallize 2026-W47 cluster 1: seven lessons, the refusal kept being met)."""
    item = "UNPUBLISHED_ITEM_FILED_BY_CARD"
    repo = _origin_repo("unpub1", {"OWNER.jsonl": [shard_line("file", id=item, title="t", seat="OWNER")],
                                   "BENCH.jsonl": [shard_line("spawn", **{"from": "X", "name": item, "for": "BENCH"})],
                                   "RUNNER.jsonl": [shard_line("note", id=item, text="mentions it only")]})
    rc, text = _origin_launch(repo, item, recorder()[1])
    want = 'to pass, run in %s: ./publish -m "ledger: %s filed" %s/BENCH.jsonl %s/OWNER.jsonl' % (
        repo, item, DH.EVENTS_REL, DH.EVENTS_REL)
    check(rc == 2 and text.count("\n") == 0 and text.endswith(want),
          "unpub: the refusal ends with the exact ./publish command for every shard that files it (%r)" % text)
    ORIGIN_FETCH = 1
    real = DH.REPO
    DH.REPO = repo
    try:
        GIT_CALLS.clear()
        ORIGIN.update({"events": [], "fetch_rc": ORIGIN_FETCH, "grep_rc": None})
        text = DH.origin_check(item, runner=recorder()[1], repo=repo, seat="BENCH")
    finally:
        DH.REPO = real
        ORIGIN.update({"events": None, "fetch_rc": 0, "grep_rc": None})
    check(text and want in text and text.index(want) < text.index("fetch exit 1") and text.count("\n") == 0,
          "unpub: a failed fetch is named after the command, on the same line (%r)" % text)


def t_an_unpublished_item_refusal_publishes_nothing():
    item = "UNPUBLISHED_ITEM_NO_AUTO_PUBLISH"
    repo = _origin_repo("unpub2", {"OWNER.jsonl": [shard_line("file", id=item, title="t", seat="OWNER")]})
    runs_before = len(os.listdir(DH.runs_dir()))
    calls, run = recorder()
    rc, text = _origin_launch(repo, item, run)
    git = [c[0][:2] for c in GIT_CALLS]
    check(rc == 2 and calls == [] and git == [["git", "fetch"], ["git", "grep"]]
          and len(os.listdir(DH.runs_dir())) == runs_before,
          "unpub: refused with one fetch and one search only; no commit, push, clone, unit or record (%s, %d calls)"
          % (git, len(calls)))


def t_an_item_filed_nowhere_here_names_where_to_publish():
    item = "ITEM_FILED_IN_ANOTHER_CLONE"
    repo = _origin_repo("unpub3", {"BENCH.jsonl": [shard_line("note", id=item, text="x")]})
    rc, text = _origin_launch(repo, item, recorder()[1], seat="STEVE")
    want = ('no local shard holds it either; to pass, run in the clone that filed it: ./publish -m "ledger: %s filed" '
            '%s/STEVE.jsonl %s/OWNER.jsonl' % (item, DH.EVENTS_REL, DH.EVENTS_REL))
    check(rc == 2 and text.count("\n") == 0 and text.endswith(want),
          "unpub: filed nowhere here -> the command for the clone that filed it, with the launch seat's shard (%r)" % text)


def _cli_launch(extra, records=()):
    """main(['launch', ...] + extra) with launch() stubbed (no clone, no unit, no model run): -> (rc, text, caps the
    stub was handed). `records` are run records written for this call, in their own state dir."""
    import contextlib
    import io
    real_launch, real_state = DH.launch, os.environ["RM_DISPATCHER_STATE"]
    os.environ["RM_DISPATCHER_STATE"] = tempfile.mkdtemp(prefix="cap_", dir=TMP)
    caps = []
    DH.launch = lambda *a, **k: caps.append(a[5]) or (0, "DETACHED stub")
    buf = io.StringIO()
    try:
        for r in records:
            DH.write_record(r)
        with contextlib.redirect_stdout(buf):
            try:
                rc = DH.main(["launch", "--seat", "BENCH", "--item", "SOME_ITEM_TO_BUILD", "--brief", "b"] + extra)
            except SystemExit as e:
                rc = e.code
    finally:
        DH.launch, os.environ["RM_DISPATCHER_STATE"] = real_launch, real_state
    return rc, buf.getvalue(), caps


def _cap_rec(name, at, budget, **kw):
    return dict({"unit": "rm-detached-bench-cap-%s" % name, "at": T0 + at, "budget_usd": budget, "seat": "BENCH",
                 "item": "SOME_ITEM_TO_BUILD", "status": "finished"}, **kw)


def t_a_launch_without_a_cap_is_refused():
    """Boundary page design/specs/2026-11-19-launch-spend-cap/boundary.md: no default level (four runs stopped by $15)."""
    rc, text, caps = _cli_launch([])
    check(rc == 2 and caps == [] and "--budget-usd <USD>" in text and "--budget-usd 0" in text,
          "cap: a launch with no --budget-usd and no --resume is refused before anything runs (rc %s, %s, %r)"
          % (rc, caps, text[:160]))


def t_an_explicit_cap_is_carried_unchanged():
    got = [_cli_launch(["--budget-usd", v])[::2] for v in ("0", "40")]
    check(got == [(0, [0.0]), (0, [40.0])], "cap: --budget-usd 0 and 40 reach the launch unchanged (%s)" % got)
    rc, text, caps = _cli_launch(["--budget-usd", "-1"])
    check(rc == 2 and caps == [], "cap: a negative cap is refused (rc %s, %r)" % (rc, text[:100]))


def t_a_resume_carries_the_earlier_cap():
    out = os.path.join(TMP, "cap-result.out")
    with open(out, "w") as f:
        json.dump({"type": "result", "session_id": "sess-capfile"}, f)
    recs = [_cap_rec("old", 10, 15.0, session="sess-cap"), _cap_rec("zero", 20, 0.0, resume_session="sess-cap"),
            _cap_rec("other", 30, 99.0, session="sess-other"), _cap_rec("file", 40, 33.0, out=out)]
    rc, text, caps = _cli_launch(["--resume", "sess-cap"], recs)
    check(rc == 0 and caps == [0.0] and "rm-detached-bench-cap-zero" in text,
          "cap: --resume carries the newest record's cap, 0 as 0, and names it (rc %s, %s, %r)" % (rc, caps, text[:200]))
    rc, text, caps = _cli_launch(["--resume", "sess-capfile"], recs)
    check(rc == 0 and caps == [33.0], "cap: a record read by its result file's session id carries its cap (%s)" % caps)


def t_a_resume_with_a_cap_takes_the_stated_cap():
    rc, text, caps = _cli_launch(["--resume", "sess-cap", "--budget-usd", "60"], [_cap_rec("old", 10, 15.0, session="sess-cap")])
    check(rc == 0 and caps == [60.0], "cap: --resume with --budget-usd takes the stated cap (%s)" % caps)


def t_a_resume_whose_earlier_cap_cannot_be_read_is_refused():
    for recs, why in (([], "no record"), ([_cap_rec("nocap", 10, None, session="sess-lost")], "no numeric budget_usd")):
        rc, text, caps = _cli_launch(["--resume", "sess-lost"], recs)
        check(rc == 2 and caps == [] and "sess-lost" in text and "--budget-usd" in text,
              "cap: a resume whose earlier cap cannot be read is refused, no number guessed (%s: rc %s, %r)"
              % (why, rc, text[:160]))


def t_an_offline_run_at_the_in_game_stage_names_no_game():
    """RIMMANDRAKE_FIX_OFFLINE_STEWARD_REFUSED_BY_GAME_A_WALK_HOLD (2026-11-21, 12:27 PM to 1:18 PM PST: eight launches of
    Pyrelands' offline steward run were refused by his walk hold on game a). Game a is stamped on an in-game run only:
    its RM_GAME_INSTANCE, else an item that names IN_GAME_ACCEPTANCE or IN_GAME_VISIT. A steward run at stage in_game
    names no game, so `pipe off game:a` does not refuse it; an in-game visit naming no game is still refused."""
    import control as C
    saved = os.environ.get("RM_CONTROL_DB")
    db = os.path.join(TMP, "control-game-stamp.db")
    os.environ["RM_CONTROL_DB"] = db
    try:
        C.init(db)
        C.switch("game:a", True, "his walk (test)", p=db)
        stage = {"RM_CONTROL_MOD": "Pyrelands", "RM_CONTROL_STAGE": "in_game"}
        for item, env, refused, what in (
                ("RIMMANDRAKE_ROUTE_PYRELANDS_VISIT_THREE_FAILURES_BACK", stage, False,
                 "a steward run at stage in_game, no game named"),
                ("RIMMANDRAKE_RUN_PYRELANDS_IN_GAME_VISIT_FOUR", stage, True,
                 "an in-game visit naming no game drives game a"),
                ("RIMMANDRAKE_RUN_PYRELANDS_IN_GAME_VISIT_FIVE", dict(stage, RM_GAME_INSTANCE="b"), False,
                 "an in-game visit on game b"),
                ("RIMMANDRAKE_RUN_PYRELANDS_IN_GAME_VISIT_SIX", dict(stage, RM_GAME_INSTANCE="a"), True,
                 "an in-game visit on game a")):
            KNOWN.add(item)     # filed on the fake origin/main
            calls, run = recorder()
            rc, text = DH.launch("BENCH", item, "Do the work.", "opus", None, 5, now=T0, runner=run, known={item},
                                 clone=CLONE, env=env)
            started = any(c[0][:1] == ["systemd-run"] for c in calls)
            ok = (rc == 2 and ("game:" + __import__("game_names").show("a")) in text and not started) if refused else (rc == 0 and started)
            check(ok, "game stamp: %s is %s while game a is held (rc %s: %s)" % (
                what, "refused" if refused else "launched", rc, " ".join(text.split())[:140]))
        C.switch("game:a", False, "walk over (test)", p=db)
    finally:
        KNOWN.intersection_update({"SOME_ITEM_TO_BUILD"})
        if saved is None:
            os.environ.pop("RM_CONTROL_DB", None)
        else:
            os.environ["RM_CONTROL_DB"] = saved


def t_a_launch_on_a_missing_clone_takes_a_pool_clone_instead():
    """Boundary page design/specs/2026-11-22-launch-missing-clone/boundary.md. Measured 2026-11-22: two runs given
    --clone <path the pool had taken back> started and died in one second (FileNotFoundError claude_bounded.sh) while the
    launch printed DETACHED."""
    item = "SOME_ITEM_TO_BUILD"
    gone = os.path.join(TMP, "pool-took-it-back", "clone")
    pool = os.path.join(TMP, "missingpool")
    os.makedirs(os.path.join(pool, "clones", item + ".det", ".git"), exist_ok=True)   # the pool clone a launch reuses
    open(os.path.join(pool, "clones", item + ".det", "sync"), "w").close()   # a whole clone has its ./sync (a half-made one is replaced)
    os.environ["RM_DETACHED_POOL"] = pool
    try:
        rc, text = DH.launch("BENCH", item, "Build.", "sonnet", 600, 5, now=T0 + 7, runner=recorder()[1], known=KNOWN,
                             clone=gone)
    finally:
        os.environ.pop("RM_DETACHED_POOL", None)
    check(not os.path.exists(gone), "missing clone: the launch never made the path it was given")
    check("--clone %s" % gone in text and text.count("NOTE (form, repaired): ") == 1
          and rc == 0 and "clone %s (reused" % os.path.join(pool, "clones", item + ".det") in text,
          "missing clone: no unit started in the missing path, one NOTE says the pool clone was taken (rc %s): %s"
          % (rc, text[:400]))


def main():
    test_refuse()
    t_a_launch_on_a_missing_clone_takes_a_pool_clone_instead()
    test_launch_and_finish()
    test_killed_and_failed_launch()
    test_same_second()
    test_guard()
    test_return()
    test_return_real_git()
    test_origin()
    test_midreturn()
    test_result_kept_whole()
    test_scope_quiet_when_gone()
    test_launch_timeout()
    test_long_brief()
    t_a_brief_never_rides_in_a_wrappers_argv()
    test_owed_close()
    test_hook_points_here()
    test_windows_path()
    test_launch_checks()
    test_resumed_part()
    t_a_brief_naming_no_skill_gets_one_warning()
    t_a_brief_naming_a_skill_gets_no_warning()
    t_the_warning_refuses_nothing()
    t_an_unpublished_item_refusal_prints_the_publish_command()
    t_an_unpublished_item_refusal_publishes_nothing()
    t_an_item_filed_nowhere_here_names_where_to_publish()
    t_a_launch_without_a_cap_is_refused()
    t_an_explicit_cap_is_carried_unchanged()
    t_a_resume_carries_the_earlier_cap()
    t_a_resume_with_a_cap_takes_the_stated_cap()
    t_a_resume_whose_earlier_cap_cannot_be_read_is_refused()
    t_an_offline_run_at_the_in_game_stage_names_no_game()
    t_a_kept_clone_is_returned_by_the_launch()
    t_a_return_that_keeps_again_is_refused_with_its_reason()
    t_a_live_or_dead_holder_is_never_returned_by_the_launch()
    t_a_kept_return_records_why()
    print("%s: %d failure(s)" % ("FAIL" if FAILS else "PASS", len(FAILS)))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
