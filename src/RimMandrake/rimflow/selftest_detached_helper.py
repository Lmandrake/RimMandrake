#!/usr/bin/env python3
"""selftest_detached_helper.py — the detached launcher (CONDUCTOR_RESTART_REDESIGN_NEVER_FREEZE_HIM).

All in a temp state dir with a faked runner: no systemd unit, no claude, no clone, no rimflow write, no real log.
  refuse     an unknown item, a blind ledger read, a bad model, an empty brief, an out-of-range bound: nothing starts
  argv       role_launch's shape: systemd-run --user, claude_bounded.sh -p, the model, RuntimeMaxSec and the scope
             bound, --max-budget-usd, ExecStopPost=finish, RM_DISPATCHER_STATE for the finish step, the brief footer
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
"""
import json
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


def check(ok, msg):
    print(("PASS " if ok else "FAIL ") + msg)
    if not ok:
        FAILS.append(msg)


class R:
    def __init__(self, rc=0, out=""):
        self.returncode, self.stdout, self.stderr = rc, out, ""


def recorder(rc=0, out=""):
    calls = []

    def run(argv, **kw):
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
                       ((("BENCH", "SOME_ITEM_TO_BUILD", "b", "sonnet", 99999, 5)), "--max-s"),
                       ((("NOPE", "SOME_ITEM_TO_BUILD", "b", "sonnet", 600, 5)), "seat")):
        rc, text = DH.launch(*args, now=T0, runner=run, known=KNOWN, clone=CLONE)
        check(rc == 2 and word in text, "refuse: %s (%s)" % (word, text[:60]))
    rc, text = DH.launch("BENCH", "SOME_ITEM_TO_BUILD", "b", "sonnet", 600, 5, now=T0, runner=run, known=set(),
                         clone=CLONE)
    check(rc == 2 and "blind" in text, "refuse: a ledger read of 0 items is blind, not a pass")
    check(calls == [], "refuse: nothing was started")


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
    check(argv[argv.index("--max-budget-usd") + 1] == "12", "argv: spend bounded by --max-budget-usd")
    check(any(a.startswith("ExecStopPost=/usr/bin/python3 ") and a.endswith("finish --unit " + argv[argv.index("--unit") + 1])
              for a in argv), "argv: ExecStopPost runs finish for this unit")
    check("RM_DISPATCHER_STATE=" + os.environ["RM_DISPATCHER_STATE"] in argv, "argv: the finish step finds the record")
    msg = argv[argv.index("-p", argv.index("--")) + 1]
    check(msg.startswith("Build the thing.") and "cli.py note SOME_ITEM_TO_BUILD" in msg and "./publish" in msg,
          "argv: the brief carries the note-and-publish footer")
    unit = argv[argv.index("--unit") + 1]
    rec = DH.read_record(unit)
    check(rec and rec["status"] == "running" and rec["clone"] == CLONE, "record: the run is recorded running")
    with open(rec["out"], "w") as f:
        json.dump({"result": "Built it; sha abc123.", "usage": {"input_tokens": 10, "output_tokens": 5,
                   "cache_creation_input_tokens": 0, "cache_read_input_tokens": 0}}, f)
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
    check(rc == 0 and "timeout" in nt and "UNMEASURED" in nt and "Terminated" in nt,
          "killed: a run killed at its bound still ends with a note (%s)" % nt[:90])
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
    unit = unit or "rm-detached-%s-%d" % (item.lower().replace("_", "-"), len(os.listdir(DH.runs_dir())))
    rec = {"seat": "BENCH", "item": item, "clone": path, "model": "sonnet", "max_s": 600, "budget_usd": 5.0, "at": T0,
           "state": os.environ["RM_DISPATCHER_STATE"], "status": status, "unit": unit,
           "out": os.path.join(TMP, unit + ".out"), "err": os.path.join(TMP, unit + ".err"),
           "clone_how": how if how is not None else "made " + path}
    DH.write_record(rec)
    return unit, path


def sh_runner(shard_dirty=False):
    """Records every call; `git status` on the shard says dirty or clean, ./publish prints a sha."""
    calls = []

    def run(argv, **kw):
        calls.append(list(argv))
        if argv[:3] == ["git", "status", "--porcelain"]:
            return R(0, " M infrastructure/state/ledger/events/BENCH.jsonl\n" if shard_dirty else "")
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

    # a dirty shard is published before the sync, and --no-publish-ledger leaves it for the bundle
    unit, clone = det_clone("DIRTY_SHARD")
    calls, run = sh_runner(shard_dirty=True)
    seen, ev = fake_evictor()
    DH.return_clone(unit, now=T0, runner=run, evictor=ev, busy=not_busy)
    pubs = [i for i, c in enumerate(calls) if c[0] == "./publish"]
    sync = [i for i, c in enumerate(calls) if c[0] == "./sync"]
    check(len(pubs) == 1 and calls[pubs[0]][-1].endswith("events/BENCH.jsonl") and pubs[0] < sync[0],
          "return: a shard the run left dirty is published, before the clone is levelled")
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
    posts = [a for a in argv if a.startswith("ExecStopPost=")]
    unit = argv[argv.index("--unit") + 1]
    check(len(posts) == 3 and posts[0].endswith("finish --unit " + unit) and "wrapup.py" in posts[1]
          and posts[2].startswith("ExecStopPost=-/usr/bin/systemd-run ") and "--no-block" in posts[2]
          and posts[2].endswith("detached_helper.py return --unit " + unit),
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


def test_hook_points_here():
    hook = os.path.join(HERE, "..", "..", "..", ".claude", "hooks", "block_agent_over_slots.py")
    with open(hook, encoding="utf-8") as f:
        src = f.read()
    check("detached_helper.py launch" in src, "hook: the drain refusal names detached_helper.py launch")


def main():
    test_refuse()
    test_launch_and_finish()
    test_killed_and_failed_launch()
    test_same_second()
    test_guard()
    test_return()
    test_return_real_git()
    test_hook_points_here()
    print("%s: %d failure(s)" % ("FAIL" if FAILS else "PASS", len(FAILS)))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
