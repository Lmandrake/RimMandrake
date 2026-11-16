#!/usr/bin/env python3
"""Acceptance test for RIMMANDRAKE_CHECK_DESIGNER_RESULT_BEFORE_EXIT_EIGHT_REJECTED (spec:
design/specs/2026-11-15-cheap-guards-at-every-door.md, guard RESULT_BEFORE_EXIT). Written by the filing seat; the
builder does not edit it (a clause believed wrong goes to the Conductor).

    python3 src/RimMandrake/rimflow/acceptance/guard_designer_result_accept.py     # exit 0 and "PASS 12/12" when built

THE CONTRACT IT FIXES
1. `.claude/hooks/role_result_before_stop.py`, a Stop hook, registered in `.claude/settings.json`.
   env RM_DESIGNER_DIR   the concept folder of this stage-machine run (role_launch sets it); unset = not such a run:
                         exit 0, print nothing.
   env RM_ROLE_UNIT      the run's unit name (keys the block counter).
   env RM_DESIGNER_CHECK_CMD  the check command, the folder appended (default:
                         `python3 src/RimMandrake/rimflow/designer_stage.py check`); exit 0 = result.json acceptable.
   env RM_STOP_BLOCKS_DIR     where the per-unit block counter lives (default: the system temp dir).
   check fails, fewer than 2 blocks so far -> stdout one JSON object {"decision": "block", "reason": <the check's own
                         output and the command to rerun>}, exit 0.
   check fails a third time -> no block; stderr says "letting the run end" (the launcher's close still rejects it).
   check passes          -> no block.
   check cannot run (exit 126/127, missing interpreter, timeout) -> no block; stderr says "did not run".
2. `designer_stage.source_errors(src, where, repo, owner_ev, on_origin=None)`: a repo path missing in `repo` is asked
   of `on_origin(path)` (default: `git cat-file -e origin/main:<path>` in `repo`): True = it exists, no error;
   False = the old "does not exist" error; None = the old error plus "origin/main could not be read".
"""
import json
import os
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
RIMFLOW = os.path.dirname(HERE)
REPO = os.path.abspath(os.path.join(RIMFLOW, "..", "..", ".."))
sys.path.insert(0, RIMFLOW)
HOOK = os.path.join(REPO, ".claude", "hooks", "role_result_before_stop.py")
RESULTS = []


def check(ok, what):
    RESULTS.append(bool(ok))
    print(("ok    " if ok else "FAIL  ") + what)


def hook(env_extra, unset=()):
    env = dict(os.environ)
    for k in ("RM_DESIGNER_DIR", "RM_ROLE_UNIT", "RM_DESIGNER_CHECK_CMD", "RM_STOP_BLOCKS_DIR") + tuple(unset):
        env.pop(k, None)
    env.update(env_extra)
    try:
        r = subprocess.run([sys.executable, HOOK], input=json.dumps({"hook_event_name": "Stop"}), capture_output=True,
                           text=True, timeout=60, env=env, cwd=REPO)
    except Exception as e:  # noqa: BLE001
        return None, "", repr(e)
    return r.returncode, r.stdout.strip(), r.stderr


def blocked(out):
    try:
        d = json.loads(out)
    except Exception:  # noqa: BLE001
        return None
    return d if isinstance(d, dict) and d.get("decision") == "block" else None


def main():
    check(os.path.isfile(HOOK), "the hook file exists")
    try:
        reg = open(os.path.join(REPO, ".claude", "settings.json"), encoding="utf-8").read()
    except OSError:
        reg = ""
    check("role_result_before_stop.py" in reg, "the hook is registered in .claude/settings.json")
    rc, out, err = hook({})
    check(rc == 0 and out == "", "no RM_DESIGNER_DIR: exit 0 and silent (not a stage-machine run)")
    with tempfile.TemporaryDirectory() as tmp:
        d = os.path.join(tmp, "concept")
        os.makedirs(d)
        bad = os.path.join(tmp, "bad.sh")
        good = os.path.join(tmp, "good.sh")
        with open(bad, "w") as f:
            f.write("#!/bin/sh\necho 'no result.json (a closing message is not a result)'\nexit 1\n")
        with open(good, "w") as f:
            f.write("#!/bin/sh\necho accepted\nexit 0\n")
        os.chmod(bad, 0o755)
        os.chmod(good, 0o755)
        base = {"RM_DESIGNER_DIR": d, "RM_STOP_BLOCKS_DIR": tmp}
        e1 = dict(base, RM_ROLE_UNIT="rm-role-designer-1", RM_DESIGNER_CHECK_CMD=bad)
        rc, out, err = hook(e1)
        b = blocked(out)
        check(rc == 0 and b and "no result.json" in str(b.get("reason")), "a failing check blocks, with the check's words")
        rc, out, err = hook(e1)
        check(rc == 0 and blocked(out), "the second failing stop blocks again")
        rc, out, err = hook(e1)
        check(rc == 0 and not blocked(out) and "letting the run end" in err, "the third lets the run end and says so")
        rc, out, err = hook(dict(base, RM_ROLE_UNIT="rm-role-designer-2", RM_DESIGNER_CHECK_CMD=bad))
        check(rc == 0 and blocked(out), "the counter is per unit: another run's first failing stop blocks")
        rc, out, err = hook(dict(base, RM_ROLE_UNIT="rm-role-designer-3", RM_DESIGNER_CHECK_CMD=good))
        check(rc == 0 and not blocked(out), "a passing check does not block")
        rc, out, err = hook(dict(base, RM_ROLE_UNIT="rm-role-designer-4",
                                 RM_DESIGNER_CHECK_CMD=os.path.join(tmp, "no_such_checker")))
        check(rc == 0 and not blocked(out) and "did not run" in err, "a check that cannot run never blocks; it says so")
        # 2. a source path that origin/main holds is not a missing source
        try:
            import designer_stage as DS
            errs_on = DS.source_errors("design/x/only_on_origin.md", "asks[a]", tmp, None, on_origin=lambda p: True)
            errs_off = DS.source_errors("design/x/nowhere.md", "asks[a]", tmp, None, on_origin=lambda p: False)
            errs_blind = DS.source_errors("design/x/nowhere.md", "asks[a]", tmp, None, on_origin=lambda p: None)
        except Exception as e:  # noqa: BLE001
            errs_on = errs_off = errs_blind = ["raised %r" % e]
        check(errs_on == [], "a path missing in the clone but on origin/main is no error (%s)" % errs_on)
        check(len(errs_off) == 1 and "does not exist" in errs_off[0], "a path on neither still reads does not exist")
        check(len(errs_blind) == 1 and "could not be read" in errs_blind[0], "an unreadable origin says so in the error")
    n = sum(RESULTS)
    print("%s %d/%d" % ("PASS" if n == len(RESULTS) else "FAIL", n, len(RESULTS)))
    return 0 if n == len(RESULTS) else 1


if __name__ == "__main__":
    sys.exit(main())
