#!/usr/bin/env python3
"""A remote host_guard take reads the far clone's own test-centre environment
(RIMMASTER_FIX_REMOTE_TAKE_HOLDS_LOCK_NOBODY_READS).

2026-11-07 13:21 PST: `RM_RUNNER_DIR='~/rm/gameb' rimflow bridge take --host stevedesktop.b` printed gen 1, but wrote
game b's lock under <RM_DATA_ROOT>/instances, while `host_guard.py status` with RM_INSTANCES_ROOT set read
`stevedesktop.b FREE`: the ssh command ran with whatever ~/.bashrc gave it, from ~/rm/runner's older env file.
Here the command remote_argv builds is run locally, ssh cut off, in a fake far clone whose host_guard.py prints the
environment it was given. No ssh, no game."""
import os
import shlex
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
FAILS = []


def check(ok, msg):
    print(("ok    " if ok else "FAIL  ") + msg)
    if not ok:
        FAILS.append(msg)


def fake_clone(root, env_line):
    os.makedirs(os.path.join(root, "src/RimMandrake/rimflow"))
    os.makedirs(os.path.join(root, "src/RimMandrake/Utils"))
    os.makedirs(os.path.join(root, "infrastructure/stevedesktop"))
    open(os.path.join(root, "src/RimMandrake/Utils/game_instance.py"), "w").close()
    with open(os.path.join(root, "src/RimMandrake/rimflow/host_guard.py"), "w") as f:
        f.write("import os, sys\nprint('ROOT=%s INST=%s ARGS=%s' % (os.environ.get('RM_INSTANCES_ROOT'), "
                "os.environ.get('RM_GAME_INSTANCE'), ' '.join(sys.argv[1:])))\n")
    with open(os.path.join(root, "infrastructure/stevedesktop/testcentre_env.sh"), "w") as f:
        f.write("export RM_DATA_ROOT=%s/data\n%s\n" % (root, env_line))


def run_far(clone, host, args, inherited_root=None):
    os.environ["RM_RUNNER_DIR"] = clone
    import importlib
    import host_guard
    importlib.reload(host_guard)
    argv = host_guard.remote_argv(host, args)
    check(argv[0] == "ssh", "remote_argv still goes over ssh: %s" % argv[:1])
    env = {k: v for k, v in os.environ.items() if k not in ("RM_INSTANCES_ROOT", "RM_GAME_INSTANCE")}
    if inherited_root:
        env["RM_INSTANCES_ROOT"] = inherited_root      # what a stale ~/.bashrc hands the ssh command
    r = subprocess.run(["bash", "-c", argv[-1]], capture_output=True, text=True, env=env, timeout=60)
    return r.returncode, (r.stdout + r.stderr).strip()


tmp = tempfile.mkdtemp(prefix="hg_remote_env_")
good = os.path.join(tmp, "gameb")
fake_clone(good, "export RM_INSTANCES_ROOT=%s/instances_right" % tmp)
rc, out = run_far(good, "stevedesktop.b", ["take", "--seat", "BENCH", "--for", "x y"])
check(rc == 0 and ("ROOT=%s/instances_right" % tmp) in out and "INST=b" in out and "ARGS=take --seat BENCH --for x y" in out,
      "the far command reads the far clone's own env file: the root its rw_game.sh and status read (%s)" % out)
rc, out = run_far(good, "stevedesktop.b", ["status"], inherited_root="%s/instances_stale_bashrc" % tmp)
check(rc == 0 and ("ROOT=%s/instances_right" % tmp) in out,
      "a stale root from the login shell does not win over the clone's env file (%s)" % out)

old = os.path.join(tmp, "runner_old")
fake_clone(old, "# older than game b: no RM_INSTANCES_ROOT here")
rc, out = run_far(old, "stevedesktop.b", ["take", "--seat", "BENCH", "--for", "x"])
check(rc == 2 and "RM_INSTANCES_ROOT" in out and "ROOT=" not in out,
      "a far clone whose env file sets no RM_INSTANCES_ROOT refuses by that name, takes nothing (rc %s: %s)" % (rc, out))
rc, out = run_far(old, "stevedesktop", ["status"])
check(rc == 0 and "INST=None" in out, "game a's take does not need the instances root (rc %s: %s)" % (rc, out))

none = os.path.join(tmp, "no_env")
fake_clone(none, "")
os.remove(os.path.join(none, "infrastructure/stevedesktop/testcentre_env.sh"))
rc, out = run_far(none, "stevedesktop.b", ["status"])
check(rc == 2 and "testcentre_env.sh" in out and "ROOT=" not in out,
      "a far clone with no env file refuses by its name (rc %s: %s)" % (rc, out))

print("%d failed" % len(FAILS))
sys.exit(1 if FAILS else 0)
