#!/usr/bin/env python3
"""Offline selftest: judge_cli stages captures under agent storage and preflights free space.

NSJUDGE_TMPDIR_FIX_TMPFS_FULL_OF_MUTANTS: claude_runner staged each capture in tempfile.mkdtemp
(/tmp, an 18G tmpfs 97% full of workers' mutation copies) and died ENOSPC. Proves: (1) the stage
dir is <RM_DATA_ROOT>/scratch/nsjudge, not tempfile's default dir; (2) the claude subprocess runs
with that stage as cwd and the stage is removed after; (3) too little free space refuses with an
ENOSPC preflight reason, without copying or calling claude; (4) an unset data root fails by name.
No network, no `claude`.
"""
import atexit, os, shutil, sys, tempfile, types  # noqa: E401

tempfile.tempdir = os.environ["TMPDIR"] = tempfile.mkdtemp(prefix="st_judge_stage_")
atexit.register(shutil.rmtree, tempfile.tempdir, True)
_ROOT = tempfile.mkdtemp(prefix="rmroot_")
os.environ["RM_DATA_ROOT"] = _ROOT

_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(_HERE))
from northstar_driver import judge_cli as J  # noqa: E402
import rmpaths  # noqa: E402

fails = []


def check(cond, what):
    print(("ok   " if cond else "FAIL ") + what)
    if not cond:
        fails.append(what)


shot = os.path.join(tempfile.mkdtemp(), "cap.png")
with open(shot, "wb") as f:
    f.write(b"\x89PNG\r\n\x1a\n" + b"\0" * 64)

root = J.stage_root()
check(os.path.realpath(root) == os.path.realpath(os.path.join(_ROOT, "scratch", "nsjudge")),
      "stage root is <RM_DATA_ROOT>/scratch/nsjudge (%s)" % root)
check(os.path.isdir(root), "stage root is created")
check(not os.path.realpath(root).startswith(os.path.realpath(os.path.join(tempfile.gettempdir(), "nsjudge"))),
      "stage root is not tempfile's default dir")

seen = {}


def fake_run(cmd, timeout, cwd=None):
    seen["cwd"] = cwd
    seen["shot_there"] = any(n.startswith("shot") for n in os.listdir(cwd))
    return types.SimpleNamespace(returncode=0, stdout='{"result":"YES"}', stderr="")


real_run, real_du = J.harness_run.run, J.shutil.disk_usage
J.harness_run.run = fake_run
try:
    ok, raw = J.claude_runner("opus", 5)(lambda p: "look at " + p, shot)
    check(ok and raw == '{"result":"YES"}', "runner returns the subprocess output")
    cwd = seen.get("cwd") or ""
    check(os.path.dirname(cwd) == root and os.path.basename(cwd).startswith("nsjudge_"),
          "claude runs with cwd under the stage root (%s)" % cwd)
    check(seen.get("shot_there") is True, "the capture is copied into that cwd")
    check(not os.path.exists(cwd), "the per-call stage dir is removed afterwards")

    seen.clear()
    J.shutil.disk_usage = lambda p: types.SimpleNamespace(total=18 << 30, used=(18 << 30) - (100 << 20),
                                                         free=100 << 20)
    ok, raw = J.claude_runner("opus", 5)(lambda p: "look at " + p, shot)
    check(ok is False and raw.startswith("ENOSPC preflight") and "100 MiB free" in raw,
          "low free space refuses before copying: %r" % raw)
    check("cwd" not in seen, "claude is never called when the preflight refuses")
    check(os.listdir(root) == [], "nothing is left staged after a refusal")
    check(not J.is_throttle(ok, raw), "an ENOSPC refusal is not mistaken for throttling")
finally:
    J.harness_run.run, J.shutil.disk_usage = real_run, real_du

check(J.stage_problem(root, shot, min_free=0) is None, "a stage with room passes the preflight")
check("preflight failed" in (J.stage_problem(root, shot + ".missing") or ""), "an unreadable image is a refusal")

saved = {k: os.environ.pop(k, None) for k in ("RM_DATA_ROOT", "AGENT_STORAGE_ROOT")}
real_as = rmpaths.AGENT_STORAGE
rmpaths.AGENT_STORAGE = os.path.join(_ROOT, "no_such_agent_storage.py")
try:
    try:
        J.stage_root()
        check(False, "unset data root fails by name")
    except rmpaths.RmDataRootUnset as e:
        check("RM_DATA_ROOT" in str(e), "unset data root fails by name: %s" % e)
finally:
    rmpaths.AGENT_STORAGE = real_as
    os.environ.update({k: v for k, v in saved.items() if v is not None})

shutil.rmtree(_ROOT, True)
print("RESULT: %s (%d failed)" % ("PASS" if not fails else "FAIL", len(fails)))
sys.exit(1 if fails else 0)
