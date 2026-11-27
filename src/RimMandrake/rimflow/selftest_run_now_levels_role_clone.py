#!/usr/bin/env python3
"""selftest_run_now_levels_role_clone.py: a run-now on a concept that is on origin/main but not yet in the Designer's
own clone levels that clone first, instead of refusing "no stage.json".

The failure (2026-11-26, item RIMMANDRAKE_READY_PIPELINE_FOR_WRECKED_MACHINES_HE_HOLDS_GO): WreckedMachines was admitted
and landed (643b9425cc), and `role_launch.py run-now --role Designer --concept design/concepts/WreckedMachines` said
"REFUSED: --concept design/concepts/WreckedMachines has no stage.json (designer_stage.py init it first)". run-now reads
the concept in the role clone /home/mandrake/rm/roles/Designer, which stood at a commit of 2026-11-21: only a Designer
unit's own first step (`./sync`) levels that clone, so a concept admitted after the last run can never start.

No unit, sync or git command runs here: the leveller and the runner are fakes; the role clone root is a temp dir.

    python3 src/RimMandrake/rimflow/selftest_run_now_levels_role_clone.py      exit 0 when every check passes
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
TMP = tempfile.mkdtemp(prefix="selftest-run-now-level-")
os.environ["RM_ROLE_CLONE_ROOT"] = os.path.join(TMP, "roles")
os.environ.setdefault("RM_UNDER_SELFTEST", "1")
import role_clones as RC    # noqa: E402
import role_launch as RL    # noqa: E402

RC.ROOT = os.environ["RM_ROLE_CLONE_ROOT"]
FAILS = []
CONCEPT = "design/concepts/NewMod"


def check(ok, msg):
    print("%s  %s" % ("PASS" if ok else "FAIL", msg))
    if not ok:
        FAILS.append(msg)


def schedule():
    sch = json.load(open(os.path.join(HERE, "dispatcher_schedule.json"), encoding="utf-8"))
    row = next(r for r in sch["roles"] if isinstance(r, dict) and r.get("stage_machine") == "designer_stage")
    clone = os.path.join(RC.ROOT, "Designer")
    if os.path.isdir(clone):
        shutil.rmtree(clone)
    os.makedirs(os.path.join(clone, ".git"))
    return {"roles": [dict(row, clone=clone)]}, row["name"], clone


def stage_json(clone):
    return os.path.join(clone, CONCEPT, "stage.json")


def ask(sch, name, **kw):
    try:
        return RL.run_now_request(sch, {"role": name, "by": "BENCH", "why": "selftest", "concept": CONCEPT}, 1.0,
                                  **kw), None
    except (ValueError, TypeError) as e:
        return None, "%s: %s" % (type(e).__name__, e)


def t_a_concept_only_on_origin_levels_the_clone_then_runs():
    sch, name, clone = schedule()
    seen = []

    def bring(c):       # the real one runs ./sync in the clone; this one lands the concept as a sync would
        seen.append(c)
        os.makedirs(os.path.dirname(stage_json(c)), exist_ok=True)
        open(stage_json(c), "w").write("{}")
        return True, "levelled"
    req, err = ask(sch, name, bring=bring)
    check(err is None and req and req.get("concept") == os.path.join(clone, CONCEPT),
          "a concept absent from the stale role clone is accepted once the clone is levelled: %r %r" % (req, err))
    check(seen == [clone], "the leveller is called once, on the role's own clone: %r" % seen)


def t_a_failed_level_is_refused_with_its_cause():
    sch, name, clone = schedule()
    req, err = ask(sch, name, bring=lambda c: (False, "seat_sync REFUSED: 2 dirty files overlap"))
    check(req is None and err and err.startswith("ValueError") and "seat_sync REFUSED: 2 dirty files overlap" in err
          and "stage.json" in err, "a level that fails is refused, naming the leveller's cause: %r" % err)
    req, err = ask(sch, name, bring=lambda c: (True, "levelled, but origin has no such concept"))
    check(req is None and err and "stage.json" in err and "origin/main" in err,
          "a concept that is on origin nowhere is still refused 'no stage.json': %r" % err)


def t_a_concept_in_the_clone_never_levels():
    sch, name, clone = schedule()
    os.makedirs(os.path.dirname(stage_json(clone)), exist_ok=True)
    open(stage_json(clone), "w").write("{}")
    seen = []
    req, err = ask(sch, name, bring=lambda c: seen.append(c) or (True, ""))
    check(err is None and not seen, "a concept the clone already holds is taken as it is, with no level: %r %r" % (
        seen, err))


def t_the_level_waits_while_a_run_is_live_in_the_clone():
    sch, name, clone = schedule()
    calls = []
    was = RC.sync
    RC.sync = lambda c, **k: calls.append(c) or (True, "synced")
    try:
        live = RL.level_for_concept({"roles": {name: {"runs": [{"unit": "rm-role-designer-9", "state": "running"}]}}},
                                    name)
        ok, why = live(clone)
        check(ok is False and "rm-role-designer-9" in why and not calls,
              "a live run in the clone holds the level, naming the run: %r %r" % (why, calls))
        idle = RL.level_for_concept({"roles": {name: {"runs": [{"unit": "rm-role-designer-8", "state": "done"}]}}},
                                    name)
        ok, why = idle(clone)
        check(ok is True and calls == [clone], "with no live run the clone is synced: %r %r" % (why, calls))
    finally:
        RC.sync = was


def t_sync_runs_seat_sync_on_the_clone():
    clone = os.path.join(RC.ROOT, "Designer")
    got = []

    def runner(argv, **kw):
        got.append(argv)
        return subprocess.CompletedProcess(argv, got and len(got) - 1, "out", "err")
    ok, why = RC.sync(clone, runner=runner)
    a = got[0] if got else []
    check(ok is True and any(str(x).endswith("seat_sync.py") for x in a) and "--repo" in a and clone in a,
          "sync runs seat_sync.py --repo <clone>: %r" % (a,))

    def bad(argv, **kw):
        return subprocess.CompletedProcess(argv, 1, "", "REFUSED: local commit abc is NOT on origin/main")
    ok, why = RC.sync(clone, runner=bad)
    check(ok is False and "NOT on origin/main" in why, "a refused sync is a failure carrying its words: %r" % why)


def main():
    tests = (t_a_concept_only_on_origin_levels_the_clone_then_runs, t_a_failed_level_is_refused_with_its_cause,
             t_a_concept_in_the_clone_never_levels, t_the_level_waits_while_a_run_is_live_in_the_clone,
             t_sync_runs_seat_sync_on_the_clone)
    try:
        for t in tests:
            try:
                t()
            except Exception as e:  # noqa: BLE001  a crash is a failure, named
                check(False, "%s crashed: %s: %s" % (t.__name__, type(e).__name__, e))
    finally:
        shutil.rmtree(TMP, ignore_errors=True)
    print("%d tests, %d failed check(s)" % (len(tests), len(FAILS)))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
