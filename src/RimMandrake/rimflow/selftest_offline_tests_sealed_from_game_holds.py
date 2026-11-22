#!/usr/bin/env python3
"""Class guard: an offline pipeline test gives the same verdict whether or not a game is held
(RIMMANDRAKE_SEAL_PILOT_GUARD_TEST_FROM_THE_LIVE_GAME, reopened 2026-11-22).

An offline test that is not named selftest* is not a test process to control.db_path(), so it reads the LIVE control
store. guard_pilot_launch_live_run_accept.py did, through pick_game's default per-game hold, and went red at the
./publish door every time the owner's walk held ArchBig (`./pipe off game:ArchBig`).

For every offline test in pipeline_tests.json (live_excluded left out) whose file name does not start with selftest,
this runs it twice, with RM_CONTROL_DB on a store of its own: once empty, once with every game held. The two exit codes
must agree. A test that cannot be started is a FAIL with its cause, never a pass.

    python3 src/RimMandrake/rimflow/selftest_offline_tests_sealed_from_game_holds.py              (exit 0 = PASS)
    python3 ... --rev <git rev>     check the tests as they were at that rev (the instance: 98972d03bf~1 is red)
"""
import json
import os
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, HERE)
import control as C     # noqa: E402

GAMES = ("a", "b")


def offline_tests():
    d = json.load(open(os.path.join(REPO, "src/RimMandrake/Utils/pipeline_tests.json")))
    live = set(d.get("live_excluded") or {})
    return [(t["test"], list(t.get("args") or [])) for t in d["tests"]
            if t["test"] not in live and not os.path.basename(t["test"]).startswith("selftest")]


def store(held):
    p = os.path.join(tempfile.mkdtemp(prefix="sealed_holds_"), "control.db")
    C.init(p)
    for g in GAMES if held else ():
        C.switch("game:" + g, True, "planted hold (selftest_offline_tests_sealed_from_game_holds)", p=p)
    if held and not all(C.game_held(g, p=p) for g in GAMES):
        raise SystemExit("FAIL  the planted store holds no game: the instrument cannot see (%s)" % p)
    if not held and any(C.game_held(g, p=p) for g in GAMES):
        raise SystemExit("FAIL  the empty store holds a game (%s)" % p)
    return p


def run(path, args, db):
    env = dict(os.environ, RM_CONTROL_DB=db)
    try:
        r = subprocess.run([sys.executable, path] + args, cwd=REPO, env=env, capture_output=True, text=True, timeout=600)
    except subprocess.TimeoutExpired:      # hang guard, far above the ~4 s the slowest of these takes alone
        return None, "timed out"
    return r.returncode, (r.stdout + r.stderr).strip().splitlines()[-1:] or [""]


def main(argv):
    rev = argv[argv.index("--rev") + 1] if "--rev" in argv else None
    free, held = store(False), store(True)
    res, temps = [], []
    try:
        for test, args in offline_tests():
            path = os.path.join(REPO, test)
            if rev:
                try:
                    body = subprocess.run(["git", "show", "%s:%s" % (rev, test)], cwd=REPO, capture_output=True,
                                          text=True, check=True).stdout
                except subprocess.CalledProcessError:
                    continue        # the test did not exist at that rev
                path = os.path.join(os.path.dirname(path), "_rev_" + os.path.basename(test))
                open(path, "w").write(body)
                temps.append(path)
            a, ta = run(path, args, free)
            b, tb = run(path, args, held)
            ok = a is not None and a == b
            res.append(ok)
            print(("PASS  " if ok else "FAIL  ") + "%s: rc %s with no hold, %s with every game held" % (test, a, b)
                  + ("" if ok else "  last line held: %s" % tb))
    finally:
        for t in temps:
            os.remove(t)
    if not res:
        print("FAIL  no offline test was found to check: the instrument cannot see")
        return 1
    print("PASS %d/%d" % (sum(res), len(res)) if all(res) else "FAIL %d of %d" % (res.count(False), len(res)))
    return 0 if all(res) else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
