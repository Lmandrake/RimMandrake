"""selftest_codex_review_fixes.py — the confirmed P1/High findings of the Codex code review of 2026-11-15
(RIMMANDRAKE_SCORE_CODEX_EXPERIMENT_FOUR_LANES_NO_CLAUDE; scorecard design/RimMandrake/codex_experiment_scorecard_2026-11-15.md).
One case per fixed finding, each named for its item; all offline, in temp dirs, with fakes for git, land.sh and systemd.

  held          maturation_autonomy.resolve: a Conductor hold (`held`) is never routed to a road-back fixer
  slots         resolve: a planned launch a road-back fixer replaces gives its slot back (max_live 1 deadlocked)
  shapes        version_locked and designer_state read a wrong-shaped JSON file as unreadable, never raise
  autolock      autolock_and_land: a failed landing restores VERSION.json and drops the delegated record
  seed          seed_and_land: a failed landing removes the local record, so the next tick seeds again
  lock          maturation_dispatch: `clear` waits for the tick's state lock (one writer at a time)
  unreadable    an unreadable state.json refuses (tick and clear), an absent one is empty
  spendland     land_spend: a git or land.sh timeout is a line in the reading, never a lost tick
  drivers       gather: a live in-game run on a non-advancing mod still counts as the one live-game driver
  killedspend   stage_spent counts the killed attempts a retry replaced; a never-started retry keeps them
  ceilingstop   only a ceiling stop (flag, or the legacy "USD ... spent at" form) lifts on a ceiling release
  deltaloose    coverage_judge.delta_merge keeps a changed/regression gap when a non-row entry changed
  exam          coverage_judge.entries sees exam.json
  headings      coverage_judge.entries keys a repeated `## ` sheet heading by occurrence
  signexpect    concept_tree.sign refuses a tree whose hash is not the one the judge read
  clonelock     detached_helper.launch rechecks, takes and reserves the clone under one lock per clone
  relaunch      launch never writes `running` over a record finish already wrote
  tmpname       write_record uses a temp name of its own per write
  scopefail     finish leaves a run retryable when its scope could not be stopped
  stoptimeout   the unit's TimeoutStopSec covers the finish step's own bounded work
  syncfail      take_clone refuses a reused clone whose ./sync failed
"""
import fcntl
import json
import os
import subprocess
import sys
import tempfile
import threading
import time

HERE = os.path.dirname(os.path.abspath(__file__))
TMP = tempfile.mkdtemp(prefix="selftest_codex_review_fixes_")
os.environ["RM_DISPATCHER_STATE"] = os.path.join(TMP, "state")
os.environ["RM_MATURATION_DISPATCH_DIR"] = os.path.join(TMP, "mstate")
os.environ["RM_CONDUCTOR_LOG"] = os.path.join(TMP, "conductor.md")
os.environ["RM_STAGE_LAND"] = "1"
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "Utils"))
import maturation_autonomy as AUT     # noqa: E402
import maturation_dispatch as MD      # noqa: E402
import coverage_judge as CJ           # noqa: E402
import concept_tree as CT             # noqa: E402
import detached_helper as DH          # noqa: E402

FAILS = []


def check(ok, msg):
    print(("PASS " if ok else "FAIL ") + msg)
    if not ok:
        FAILS.append(msg)


def case(fn):
    try:
        fn()
    except Exception as e:      # noqa: BLE001  a crash is a failed case, never a lost run
        check(False, "%s raised %s: %s" % (fn.__name__, type(e).__name__, e))
    return fn


class R:
    def __init__(self, rc=0, out="", err=""):
        self.returncode, self.stdout, self.stderr = rc, out, err


def concept(root, mod, files):
    d = os.path.join(root, "design", "concepts", mod)
    for rel, obj in files.items():
        p = os.path.join(d, rel)
        os.makedirs(os.path.dirname(p), exist_ok=True)
        with open(p, "w", encoding="utf-8") as f:
            f.write(obj if isinstance(obj, str) else json.dumps(obj))
    return d


CFG = {"max_live": 1, "fix_cap_tokens": 1_250_000, "steward_cap_tokens": 1_250_000, "launch_tries": 3}
FX = {"designer_state": lambda m: None, "version_locked": lambda m: False, "version_evidence": lambda m: [],
      "open_items": lambda ids: [{"id": "RIMMANDRAKE_FIX_SOMETHING_ROAD_BACK_OPEN"}]}


@case
def held():   # RIMMANDRAKE_HONOUR_CONDUCTOR_HOLD_ROAD_BACK_FIXER_IGNORED_IT
    st = {"mods": {"A": {"road_back": {"caused_by": "S1"}}}}
    rows = [{"mod": "A", "decision": "held", "stage": "offline_build", "why": "refused by hold"}]
    rows, launches = AUT.resolve(TMP, dict(CFG, max_live=2), st, {"A": {"live_units": [], "version": "0.1.0"}}, rows,
                                 [], 1000.0, FX)
    check(rows[0].get("decision") == "held" and "A" not in launches and rows[0].get("aut") != "fixer",
          "held: a Conductor hold is not routed to a road-back fixer (%s, %s)" % (rows[0].get("decision"), launches))


@case
def slots():  # RIMMANDRAKE_RETURN_SLOT_OF_REPLACED_LAUNCH_FIXER_NEVER_RAN
    st = {"mods": {"A": {"road_back": {"caused_by": "S1"}}}}
    rows = [{"mod": "A", "decision": "launch", "stage": "offline_build", "why": "build owed"}]
    rows, launches = AUT.resolve(TMP, CFG, st, {"A": {"live_units": [], "version": "0.1.0"}}, rows, ["A"], 1000.0, FX)
    check(launches == ["A"] and rows[0].get("aut") == "fixer",
          "slots: the fixer that replaced A's own build takes its slot at max_live 1 (%s, %s: %s)" % (
              launches, rows[0].get("decision"), str(rows[0].get("why"))[:80]))


@case
def shapes():  # RIMMANDRAKE_READ_WRONG_SHAPED_JSON_LIST_CRASHED_TICK
    root = tempfile.mkdtemp(dir=TMP)
    concept(root, "L", {"version/VERSION.json": ["0.1.0"], "stage.json": []})
    try:
        v = AUT.version_locked(root, "L")
    except Exception as e:      # noqa: BLE001
        v = "raised %s" % type(e).__name__
    check(v is False, "shapes: a list VERSION.json reads not locked (%s)" % v)
    try:
        s = AUT.designer_state(root, "L")
    except Exception as e:      # noqa: BLE001
        s = "raised %s" % type(e).__name__
    check(s is None, "shapes: a list stage.json reads unreadable (%r)" % (s,))


@case
def autolock():  # RIMMANDRAKE_RESTORE_VERSION_FILE_WHEN_AUTOLOCK_LANDING_FAILS
    root = tempfile.mkdtemp(dir=TMP)
    old = {"mod": "V", "version": "0.1.0", "state": "open"}
    d = concept(root, "V", {"stage.json": {"status": "locked", "stage": 5}, "tree.json": {"leaves": []},
                            "version/VERSION.json": old})

    def land(subject, paths):
        raise RuntimeError("land.sh exited 1: index.lock")
    try:
        AUT.autolock_and_land(root, "V", now=1_800_000_000.0, land=land)
        raised = False
    except RuntimeError:
        raised = True
    with open(os.path.join(d, "version", "VERSION.json"), encoding="utf-8") as f:
        now_v = json.load(f)
    dg = [os.path.join(dp, n) for dp, _, ns in os.walk(os.path.join(root, "infrastructure")) for n in ns]
    check(raised and now_v == old and not dg, "autolock: a failed landing raises, restores VERSION.json (%s) and leaves "
          "no delegated record (%d)" % (now_v.get("state"), len(dg)))


@case
def seed():  # RIMMANDRAKE_RETRY_SEED_LANDING_LOCAL_RECORD_KEPT_REFUSAL
    root = tempfile.mkdtemp(dir=TMP)
    d = concept(root, "S", {"stage.json": {}})
    rec = os.path.join(d, AUT.M.RECORD)
    orig_seed, orig_run = AUT.M.seed_mod, AUT.subprocess.run

    def fake_seed(r, m, **kw):
        os.makedirs(os.path.dirname(rec), exist_ok=True)
        with open(rec, "w", encoding="utf-8") as f:
            f.write("{}\n")
        return {}, True
    AUT.M.seed_mod = fake_seed
    AUT.subprocess.run = lambda *a, **k: R(1, "", "fatal: index.lock")
    try:
        try:
            AUT.seed_and_land(root, "S")
            raised = False
        except RuntimeError:
            raised = True
    finally:
        AUT.M.seed_mod, AUT.subprocess.run = orig_seed, orig_run
    check(raised and not os.path.exists(rec), "seed: a failed landing raises and removes the local record (exists %s)"
          % os.path.exists(rec))


@case
def lock():  # RIMMANDRAKE_LOCK_DISPATCH_STATE_CLEAR_LOST_TICK_WRITES
    d = MD.sdir()
    p = os.path.join(d, "state.json")
    with open(p, "w", encoding="utf-8") as f:
        json.dump({"mods": {"A": {"stopped": {"why": "run u ended"}}}}, f)
    lk = getattr(MD, "STATE_LOCK", "state.lock")
    fh = open(os.path.join(d, lk), "a+")
    fcntl.flock(fh, fcntl.LOCK_EX)
    out = {}
    t = threading.Thread(target=lambda: out.setdefault("rc", MD.main(["clear", "A", "--why", "selftest"])))
    t.start()
    time.sleep(0.6)
    with open(p, encoding="utf-8") as f:
        during = json.load(f)
    fcntl.flock(fh, fcntl.LOCK_UN)
    fh.close()
    t.join(10)
    with open(p, encoding="utf-8") as f:
        after = json.load(f)
    check("stopped" in during["mods"]["A"] and "stopped" not in after["mods"]["A"] and out.get("rc") == 0,
          "lock: clear waits for the held state lock, then clears (during %s, after %s)" % (
              sorted(during["mods"]["A"]), sorted(after["mods"]["A"])))


@case
def unreadable():  # RIMMANDRAKE_REFUSE_UNREADABLE_DISPATCH_STATE_RESET_STOPS
    d = MD.sdir()
    p = os.path.join(d, "state.json")
    with open(p, "w", encoding="utf-8") as f:
        f.write('{"mods": {"A": {"stopped"')
    rc = MD.main(["clear", "A", "--why", "selftest"])
    with open(p, encoding="utf-8") as f:
        kept = f.read()
    check(rc != 0 and kept.startswith('{"mods": {"A": {"stopped"'), "unreadable: clear refuses a truncated state.json "
          "and leaves it (rc %s)" % rc)
    try:
        MD.tick(TMP, {"advancing": []}, True, fx={"autonomy": False, "facts": lambda: {}}, page=False)
        ticked = "ran"
    except Exception as e:      # noqa: BLE001
        ticked = type(e).__name__
    with open(p, encoding="utf-8") as f:
        kept2 = f.read()
    check(ticked != "ran" and kept2 == kept, "unreadable: the tick refuses it too and writes nothing (%s)" % ticked)
    os.remove(p)
    check(MD.read_state(p) == {}, "unreadable: an absent state.json is an empty state")


@case
def spendland():  # RIMMANDRAKE_CATCH_SPEND_LANDING_TIMEOUT_TICK_LOST_LAUNCHES
    orig = MD.subprocess.run

    def boom(*a, **k):
        raise subprocess.TimeoutExpired(a[0], 300)
    MD.subprocess.run = boom
    try:
        got = MD.land_spend(TMP, ["x"])
    except Exception as e:      # noqa: BLE001
        got = "raised %s" % type(e).__name__
    finally:
        MD.subprocess.run = orig
    check(isinstance(got, str) and not got.startswith("raised") and "Timeout" in got,
          "spendland: a timeout is a reading line (%s)" % got)


@case
def drivers():  # RIMMANDRAKE_COUNT_EVERY_MOD_INGAME_DRIVER_NOT_ADVANCING_ONLY
    orig_g, orig_b = MD.MN.gather, MD.M.build_facts
    MD.MN.gather = lambda root, live=True: {"mods": [
        {"name": "A", "runs": []},
        {"name": "B", "runs": [{"unit": "rm-detached-b-1", "live": True, "item": "RIMMANDRAKE_B_IN_GAME_VISIT_ONE"}]}]}
    MD.M.build_facts = lambda root, mod: {"stage": "offline_build"}
    try:
        facts = MD.gather(TMP, {"advancing": ["A"]})
    finally:
        MD.MN.gather, MD.M.build_facts = orig_g, orig_b
    check("rm-detached-b-1" in MD.live_drivers(facts) if hasattr(MD, "live_drivers") else False,
          "drivers: B's live in-game run is a driver though B is not advancing (%s)" % (
              facts.get("A", {}).get("ingame_live_other")))


@case
def killedspend():  # RIMMANDRAKE_CHARGE_KILLED_ATTEMPTS_RETRY_DROPPED_DOLLARS
    f = {"box_runs": {}, "run_tokens": {"u1": 3_000_000, "u2": 250_000}}
    got = MD.stage_spent(f, "blind_challenge", [{"unit": "u2", "cap_tokens": 250_000, "killed_before": ["u1"]}])
    check(got == 3_250_000, "killedspend: a killed attempt's tokens stay charged (%s, want 3250000)" % got)
    s = {}
    row = {"retry_of": {"unit": None, "item": "I", "filed": True, "tries": 2, "killed_before": ["u1"]}, "cap": 250_000}
    ok, item, unit, text, entry = MD.launch_counted(
        {}, s, row, 1000.0, "blind_auto", {"cycle": 1}, lambda: "I", lambda i: (True, "filed"),
        lambda i: (True, "published"), lambda i: (1, "fatal: index.lock", None))
    check(entry.get("killed_before") == ["u1"], "killedspend: a never-started retry keeps killed_before (%s)" %
          entry.get("killed_before"))


@case
def ceilingstop():  # RIMMANDRAKE_MATCH_CEILING_STOP_BY_FLAG_NOT_SUBSTRING
    fn = getattr(MD, "ceiling_stop", None)
    check(fn is not None and fn({"why": "x", "ceiling": True}) and
          fn({"why": "USD 59.00 spent at the offline build plus the next run's USD 15 cap passes the 60 ceiling"}) and
          not fn({"why": "run u ended and refused bar(s) heat_ceiling_guard appeared that were not refused before"}),
          "ceilingstop: a progress stop naming a bar with 'ceiling' in it is not a ceiling stop")


@case
def deltaloose():  # RIMMANDRAKE_KEEP_GAPS_OPENED_BY_SHARED_MATERIAL_CHANGES
    dp = {"ids": [], "loose": True, "carried": [], "prior_checklist": []}
    rec = {"verdict": "not_covered", "checklist": [], "gaps": [
        {"ids": ["B"], "new_since": "regression", "since": "floor", "what": "floor change broke B"}]}
    out = CJ.delta_merge(rec, dp)
    check(len(out["gaps"]) == 1 and not out.get("dropped"), "deltaloose: a regression gap from a floor change is kept "
          "(%d kept, %d dropped)" % (len(out["gaps"]), len(out.get("dropped") or [])))
    rec = {"verdict": "not_covered", "checklist": [], "gaps": [{"ids": ["B"], "new_since": "first", "what": "x"}]}
    out = CJ.delta_merge(rec, dp)
    check(len(out.get("dropped") or []) == 1, "deltaloose: an untagged gap on unchanged material is still dropped")


@case
def exam():  # RIMMANDRAKE_HASH_EXAM_IN_DELTA_ENTRIES_CHANGE_UNSEEN
    d = concept(tempfile.mkdtemp(dir=TMP), "E", {"exam.json": {"passed": True}})
    check("exam" in CJ.entries(d), "exam: entries() carries exam.json (%s)" % sorted(CJ.entries(d)))


@case
def headings():  # RIMMANDRAKE_KEY_REPEATED_SHEET_HEADINGS_SECOND_HID_FIRST
    d = concept(tempfile.mkdtemp(dir=TMP), "H", {"sheet.md": "# T\n## Controls\none\n## Other\nx\n## Controls\ntwo\n"})
    e = CJ.entries(d)
    keys = sorted(k for k in e if k.startswith("sheet:Controls"))
    check(len(keys) == 2 and "one" in e[keys[0]] and "two" in e[keys[1]] and "sheet:Other" in e,
          "headings: two `## Controls` sections are two entries (%s)" % keys)


@case
def signexpect():  # RIMMANDRAKE_SIGN_ONLY_THE_JUDGED_TREE_HASH
    d = concept(tempfile.mkdtemp(dir=TMP), "G", {"tree.json": {"leaves": [], "title": "B"}})
    old = os.environ.get("RM_ROLE_UNIT")
    os.environ["RM_ROLE_UNIT"] = "rm-coverage-judge-1"
    try:
        errs = CT.sign(d, CT.SIGNER, TMP, expect="0" * 16)
    except TypeError as e:
        errs = ["no expect: %s" % e]
    finally:
        if old is None:
            os.environ.pop("RM_ROLE_UNIT", None)
        else:
            os.environ["RM_ROLE_UNIT"] = old
    check(any("not the tree the judge read" in e for e in errs), "signexpect: a tree whose hash is not the judged one is "
          "refused (%s)" % errs)


ITEM = "SOME_ITEM_TO_BUILD"
CLONE = os.path.join(TMP, "clone")
os.makedirs(os.path.join(CLONE, "src", "RimMandrake", "Utils"))   # a clone a unit can start in
open(os.path.join(CLONE, "src", "RimMandrake", "Utils", "claude_bounded.sh"), "w").close()


def fake(script=None):
    calls = []

    def run(argv, **kw):
        calls.append(argv)
        if argv[:2] == ["git", "fetch"]:
            return R(0)
        if argv[:2] == ["git", "grep"]:
            return R(0, json.dumps({"seat": "BENCH", "event": "file", "id": ITEM, "title": "t", "for": "BENCH"},
                                   separators=(",", ":")) + "\n")
        if script:
            return script(argv, kw)
        return R(0)
    return run, calls


@case
def clonelock():  # RIMMANDRAKE_LOCK_DET_CLONE_TAKE_TWO_LAUNCHES_ONE_CLONE
    seen = {}

    def script(argv, kw):
        if argv[0] == "systemd-run":
            fh = open(DH.clone_lock_path(CLONE), "a+")
            try:
                fcntl.flock(fh, fcntl.LOCK_EX | fcntl.LOCK_NB)
                seen["free"] = True
            except OSError:
                seen["free"] = False
            finally:
                fh.close()
        return R(0)
    run, _ = fake(script)
    try:
        rc, text = DH.launch("BENCH", ITEM, "b", "sonnet", 600, 5, now=1_800_000_100.0, runner=run, known={ITEM},
                             clone=CLONE)
    except AttributeError as e:
        rc, text = 9, "no lock: %s" % e
    check(rc == 0 and seen.get("free") is False, "clonelock: the clone lock is held from the holder check to the "
          "record (rc %s, lock free at systemd-run: %s)" % (rc, seen.get("free")))


@case
def relaunch():  # RIMMANDRAKE_KEEP_FINISHED_RECORD_LAUNCH_WROTE_RUNNING
    def script(argv, kw):
        if argv[0] == "systemd-run":
            unit = argv[argv.index("--unit") + 1]
            rec = DH.read_record(unit)
            rec.update(status="finished", result="error (exit 1)")
            DH.write_record(rec)
        return R(0)
    run, _ = fake(script)
    rc, text = DH.launch("BENCH", ITEM, "b", "sonnet", 600, 5, now=1_800_000_200.0, runner=run, known={ITEM},
                         clone=CLONE)
    unit = text.split()[1] if text.startswith("DETACHED") else None
    rec = DH.read_record(unit) if unit else {}
    check(rc == 0 and rec.get("status") == "finished", "relaunch: a record finish wrote first stays finished (%s)" %
          rec.get("status"))


@case
def tmpname():  # RIMMANDRAKE_UNIQUE_TEMP_PER_RECORD_WRITE_SHARED_TMP
    rec = {"unit": "rm-detached-bench-tmpname-1", "status": "x"}
    os.makedirs(DH.runs_dir(), exist_ok=True)
    blocker = DH.record_path(rec["unit"]) + ".tmp"
    os.makedirs(blocker, exist_ok=True)     # the shared name is taken (as by a second writer mid-write)
    try:
        DH.write_record(rec)
        ok = DH.read_record(rec["unit"]) == rec
    except OSError as e:
        ok = False
        print("  write_record: %s" % e)
    check(ok, "tmpname: a write never needs the one shared <record>.tmp name")


@case
def scopefail():  # RIMMANDRAKE_RETRY_FINISH_WHEN_SCOPE_STOP_FAILED_BILLING
    rec = {"seat": "BENCH", "item": ITEM, "clone": CLONE, "model": "sonnet", "max_s": 600, "budget_usd": 5.0,
           "at": 1_800_000_300.0, "state": DH.state_dir(), "status": "running", "clone_how": "given"}
    unit = DH.reserve_record(rec)
    orig = DH.stop_scope
    DH.stop_scope = lambda seat, u, runner=None: ("scope x.scope: FAILED systemctl kill exit 1: denied; FAILED systemctl "
                                                  "stop exit 1: denied; now active")
    try:
        run, _ = fake()
        rc, text = DH.finish(unit, now=1_800_000_400.0, env={}, runner=run, log_path=os.path.join(TMP, "c.md"),
                             item_reader=lambda c, i: {"state": "closed", "notes": []})
    finally:
        DH.stop_scope = orig
    check(rc != 0 and DH.read_record(unit).get("status") != "finished", "scopefail: a scope still active after a "
          "failed kill and stop leaves the run unfinished, to be finished again (rc %s, %s)" % (
              rc, DH.read_record(unit).get("status")))


@case
def stoptimeout():  # RIMMANDRAKE_COVER_FINISH_IN_TIMEOUTSTOPSEC_TEN_KILLED
    rec = {"clone": CLONE, "unit": "rm-detached-bench-x-1", "seat": "BENCH", "item": ITEM, "max_s": 600,
           "model": "sonnet", "budget_usd": 5.0, "out": "/tmp/o", "err": "/tmp/e", "state": DH.state_dir()}
    argv = DH.launch_argv(rec, "m", "/bin/claude")
    t = [a for a in argv if str(a).startswith("TimeoutStopSec=")]
    sec = int(t[0].split("=")[1]) if t else 0
    check(sec >= 120 + 300 + 60, "stoptimeout: TimeoutStopSec %d covers finish's note (120 s) and publish (300 s)" % sec)


@case
def syncfail():  # RIMMANDRAKE_REFUSE_STALE_DET_CLONE_WHEN_SYNC_FAILS
    pool = tempfile.mkdtemp(dir=TMP)
    os.environ["RM_DETACHED_POOL"] = pool
    try:
        os.makedirs(os.path.join(pool, "clones", ITEM + ".det", ".git"))
        try:
            DH.take_clone(ITEM, runner=lambda argv, **kw: R(1, "", "CONFLICT"))
            refused = False
        except RuntimeError:
            refused = True
    finally:
        os.environ.pop("RM_DETACHED_POOL", None)
    check(refused, "syncfail: a reused clone whose ./sync failed is refused")


print("%d failure(s)" % len(FAILS))
sys.exit(1 if FAILS else 0)
