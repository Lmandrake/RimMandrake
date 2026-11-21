#!/usr/bin/env python3
"""selftest_detached_game_env.py -- a detached run launched for a named game (RM_GAME_INSTANCE=b) carries that game's whole
environment into its unit, WSLENV included, so a python.exe child (every bridge call) drives the same game.

Item RIMMANDRAKE_CARRY_WSLENV_INTO_B_RUNS_PROOF_HIT_A. The failure it guards (2026-11-20 9:43 PM
PST): the Dispatch step launched GimmeSomeSlack's visit for game b with RM_GAME_INSTANCE=b and nothing else; WSLENV was
empty, python.exe saw no instance, the bridge client fell back to port 5174, and proof_all loaded its calm site onto game a,
10 s after a FlowWorks judge run had taken game a's bridge.

Measured on Archmagi the same evening: WSLENV=NAME carries NAME into python.exe; WSLENV=NAME/u does NOT (python.exe read
None). So the name must be bare, as game_instance._WSLENV writes it.

    python3 src/RimMandrake/rimflow/selftest_detached_game_env.py      # exit 0 = every case PASS
"""
import os
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
TMP = tempfile.mkdtemp(prefix="selftest_detached_game_env_")
os.environ["RM_DISPATCHER_STATE"] = os.path.join(TMP, "state")
os.environ["RM_CONDUCTOR_LOG"] = os.path.join(TMP, "conductor.md")
os.environ["RM_INSTANCES_ROOT"] = os.path.join(TMP, "instances")     # game_instance's tokens go here, not the real root
os.environ.pop("RM_GAME_INSTANCE", None)
os.environ.pop("WSLENV", None)
sys.path.insert(0, HERE)
import detached_helper as DH  # noqa: E402

FAILS = []
CLONE = os.path.join(TMP, "clone")
os.makedirs(CLONE)


def check(ok, msg):
    print(("PASS " if ok else "FAIL ") + msg)
    if not ok:
        FAILS.append(msg)


def setenv(argv):
    """-> {KEY: VALUE} of every --setenv pair in a systemd-run argv (the last one of a key wins, as systemd reads it)."""
    out = {}
    for i, a in enumerate(argv[:-1]):
        if a == "--setenv":
            k, _, v = argv[i + 1].partition("=")
            out[k] = v
    return out


def argv_for(env):
    rec = {"clone": CLONE, "unit": "rm-detached-bench-x-1", "seat": "BENCH", "item": "SOME_ITEM", "max_s": 600,
           "model": "sonnet", "budget_usd": 0, "out": os.path.join(TMP, "o"), "err": os.path.join(TMP, "e"),
           "state": DH.state_dir(), "env": env}
    argv = DH.launch_argv(rec, "m", "/bin/claude")
    return argv[:argv.index("--")]          # systemd-run's own arguments; the command after "--" is claude's


def t_a_game_b_unit_carries_its_whole_environment():
    """game b: the unit carries b's port, token, folders and a WSLENV that names each, bare (no /u)."""
    e = setenv(argv_for({"RM_GAME_INSTANCE": "b", "RM_CONTROL_MOD": "GimmeSomeSlack"}))
    names = [n.split("/")[0] for n in (e.get("WSLENV") or "").split(":") if n]
    flags = {n.split("/")[0]: n for n in (e.get("WSLENV") or "").split(":") if n}
    check(e.get("RM_GAME_INSTANCE") == "b", "b: RM_GAME_INSTANCE=b kept (%r)" % e.get("RM_GAME_INSTANCE"))
    check("RM_GAME_INSTANCE" in names, "b: WSLENV names RM_GAME_INSTANCE, so python.exe sees it (WSLENV=%r)" % e.get("WSLENV"))
    check(flags.get("RM_GAME_INSTANCE") == "RM_GAME_INSTANCE",
          "b: RM_GAME_INSTANCE is bare in WSLENV (/u did not reach python.exe, measured) (%r)" % flags.get("RM_GAME_INSTANCE"))
    check(e.get("GABP_SERVER_PORT") == "5175", "b: GABP_SERVER_PORT is game b's 5175, never a's 5174 (%r)" % e.get("GABP_SERVER_PORT"))
    check("GABP_SERVER_PORT" in names and "GABP_TOKEN" in names and bool(e.get("GABP_TOKEN")),
          "b: the port and token cross into python.exe (WSLENV %r)" % e.get("WSLENV"))
    check(bool(e.get("RM_GAME_LOGDIR")) and "RM_GAME_LOGDIR" in names, "b: b's log folder is carried (%r)" % e.get("RM_GAME_LOGDIR"))
    check(e.get("RM_CONTROL_MOD") == "GimmeSomeSlack", "b: the run's other RM_ variables stay (%r)" % e.get("RM_CONTROL_MOD"))


def t_a_game_a_unit_gains_nothing():
    """game a, named or not: nothing of a named game is added (game a is today's game whatever the shell holds)."""
    for env, label in (({"RM_GAME_INSTANCE": "a"}, "a"), ({}, "none")):
        e = setenv(argv_for(env))
        check("GABP_SERVER_PORT" not in e and "GABP_TOKEN" not in e and "RM_GAME_LOGDIR" not in e,
              "%s: no named-game variable is added (%s)" % (label, sorted(k for k in e if k.startswith(("GABP_", "RM_GAME_")))))


def t_a_bad_game_name_is_refused():
    """a bad name is refused at launch, not carried as an unknown game."""
    try:
        argv_for({"RM_GAME_INSTANCE": "b c"})
        check(False, "bad name: 'b c' was carried into a unit")
    except ValueError:
        check(True, "bad name: 'b c' refused")


def main():
    t_a_game_b_unit_carries_its_whole_environment()
    t_a_game_a_unit_gains_nothing()
    t_a_bad_game_name_is_refused()
    print("%d FAIL" % len(FAILS) if FAILS else "all PASS")
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
