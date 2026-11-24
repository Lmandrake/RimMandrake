#!/usr/bin/env python3
"""selftest_detached_reap: the return step ends what a finished run left running, and only that
(RIMMANDRAKE_REAP_SELFTEST_CHILD_ENDED_RUN_LEFT_HOLDING_CLONE; design/specs/2026-11-19-run-return-reap/boundary.md).

Real processes (`sleep`) in a temp pool clone; a fake git/publish runner and a fake evictor. Nothing outside the temp
dirs is touched, and every child it starts is killed at the end.
"""
import os
import shutil
import subprocess
import sys
import tempfile
import time

HERE = os.path.dirname(os.path.abspath(__file__))
TMP = tempfile.mkdtemp(prefix="selftest_detached_reap_")
os.environ["RM_DISPATCHER_STATE"] = os.path.join(TMP, "state")
os.environ["RM_DETACHED_POOL"] = os.path.join(TMP, "pool")
os.environ["RM_CONDUCTOR_LOG"] = os.path.join(TMP, "conductor.md")
os.environ.setdefault("RM_UNDER_SELFTEST", "1")
sys.path.insert(0, HERE)
import detached_helper as DH  # noqa: E402

FAILS = []
KIDS = []
N = [0]


def check(name, ok, detail=""):
    print(("PASS " if ok else "FAIL ") + name + (": " + str(detail)[:400] if detail and not ok else ""))
    if not ok:
        FAILS.append(name)


class R(object):
    returncode, stdout, stderr = 0, "", ""


def runner(argv, **kw):
    return R()


def evictor(item, clone, before=None):
    shutil.rmtree(clone, ignore_errors=True)
    return None, None


def run_with_child(marker_of=lambda unit: unit, env_clear=False):
    """-> (unit, clone, child): a finished run record and a sleeping child with its cwd in the run's clone."""
    N[0] += 1
    item = "RIMMANDRAKE_REAP_TEST_ITEM_%d" % N[0]
    clone = os.path.join(os.environ["RM_DETACHED_POOL"], "clones", item + ".det")
    os.makedirs(clone)
    now = time.time()
    unit = DH.unit_name("BENCH", item, now)
    rec = {"unit": unit, "seat": "BENCH", "item": item, "clone": clone, "clone_how": "made " + clone, "model": "opus",
           "at": now - 30, "state": os.environ["RM_DISPATCHER_STATE"], "status": "finished",
           "result": "success (exited 0)", "ended": now, "out": os.path.join(TMP, unit + ".out.json"),
           "err": os.path.join(TMP, unit + ".err")}
    DH.write_record(rec)
    env = {} if env_clear else dict(os.environ)
    env.pop("RM_ROLE_UNIT", None)
    m = marker_of(unit)
    if m:
        env["RM_ROLE_UNIT"] = m
    child = subprocess.Popen(["sleep", "300"], cwd=clone, env=env)
    KIDS.append(child)
    time.sleep(0.2)
    return unit, clone, child


def gone(child, wait=3.0):
    t = time.time() + wait
    while time.time() < t:
        if child.poll() is not None:
            return True
        time.sleep(0.05)
    return child.poll() is not None


def t_a_leftover_child_is_ended_and_the_clone_returned():
    unit, clone, child = run_with_child()
    rc, text = DH.return_clone(unit, runner=runner, evictor=evictor, publish_ledger=False)
    rec = DH.read_record(unit) or {}
    check("a-leftover-child-is-ended-and-the-clone-returned: the child is ended", gone(child), text)
    check("a-leftover-child-is-ended-and-the-clone-returned: the clone is returned",
          rc == 0 and rec.get("returned") and not os.path.isdir(clone), text)
    check("a-leftover-child-is-ended-and-the-clone-returned: the steps name the pid",
          str(child.pid) in " ".join(rec.get("return_steps") or []), str(rec.get("return_steps")))


def t_an_unmarked_process_in_the_clone_keeps_it():
    unit, clone, child = run_with_child(marker_of=lambda unit: None)
    rc, text = DH.return_clone(unit, runner=runner, evictor=evictor, publish_ledger=False)
    check("an-unmarked-process-in-the-clone-keeps-it", child.poll() is None and os.path.isdir(clone)
          and "a process is working in it" in text, text)


def t_another_units_marker_is_not_this_runs():
    for what, mk in (("a longer name", lambda u: u + "-2"), ("a prefix", lambda u: u[:-2])):
        unit, clone, child = run_with_child(marker_of=mk)
        rc, text = DH.return_clone(unit, runner=runner, evictor=evictor, publish_ledger=False)
        check("another-units-marker-is-not-this-runs: %s" % what, child.poll() is None and os.path.isdir(clone), text)


def t_a_blind_scan_kills_nothing():
    unit, clone, child = run_with_child()
    rc, text = DH.return_clone(unit, runner=runner, evictor=evictor, publish_ledger=False,
                               scan=lambda marker, since=None: ([child.pid], "pid 1 (uid 0) environ unreadable"))
    check("a-blind-scan-kills-nothing", child.poll() is None and os.path.isdir(clone) and "blind" in text
          and "a process is working in it" in text, text)


def t_role_launch_scan_rules_out_zombies():
    """A fake /proc: an unreadable environ (a directory there) on a zombie is ruled out; on a live or unknown-state
    process of this uid it is blind. Then the real /proc with a real zombie child (`true`, never waited on)."""
    import role_launch as RL
    def fake(states):
        root = tempfile.mkdtemp(prefix="proc_", dir=TMP)
        for n, state in states.items():
            os.makedirs(os.path.join(root, n, "environ"))       # open() on it raises IsADirectoryError (an OSError)
            if state is None:                                   # a stat that cannot be read (not "gone")
                os.makedirs(os.path.join(root, n, "stat"))
            else:
                with open(os.path.join(root, n, "stat"), "w") as f:
                    f.write("%s (python3) %s 1 1 1 0 -1 0 0 0 0 0 0 0 0 0 20 0 1 0 100 0 0\n" % (n, state))
        return root
    pids, blind = RL.scan_marked("rm-x", proc=fake({"4242": "Z"}))
    check("role-launch-scan-rules-out-zombies (a zombie is not blind)", blind is None and pids == [], blind)
    pids, blind = RL.scan_marked("rm-x", proc=fake({"4242": "S"}))
    check("role-launch-scan-rules-out-zombies (a live unreadable one is blind)", blind and "4242" in blind, blind)
    pids, blind = RL.scan_marked("rm-x", proc=fake({"4242": None}))
    check("role-launch-scan-rules-out-zombies (an unreadable state is blind)", blind and "4242" in blind, blind)
    z = subprocess.Popen(["true"])
    KIDS.append(z)
    time.sleep(0.5)
    with open("/proc/%d/stat" % z.pid, "rb") as f:
        st = f.read().rsplit(b")", 1)[1].split()[0]
    pids, blind = RL.scan_marked("no-such-unit-x", since=time.time() - 30)
    check("role-launch-scan-rules-out-zombies (a real zombie child, state %s)" % st.decode(), st == b"Z" and
          blind is None, blind)


def t_a_reused_det_clone_takes_the_seat_identity():
    src = os.path.join(TMP, "seatclone")
    subprocess.run(["git", "init", "-q", src], check=True)
    subprocess.run(["git", "-C", src, "config", "user.email", "seat+noreply@users.example"], check=True)
    item = "RIMMANDRAKE_REAP_TEST_IDENTITY_ITEM"
    dest = os.path.join(os.environ["RM_DETACHED_POOL"], "clones", item + ".det")
    subprocess.run(["git", "init", "-q", dest], check=True)
    open(os.path.join(dest, "sync"), "w").close()   # a whole clone has its ./sync (a half-made one is replaced)
    os.environ["RM_IDENTITY_FROM"] = src
    try:
        got, line = DH.take_clone(item, runner=runner)
    finally:
        del os.environ["RM_IDENTITY_FROM"]
    email = subprocess.run(["git", "-C", dest, "config", "--local", "--get", "user.email"], capture_output=True,
                           text=True).stdout.strip()
    check("a-reused-det-clone-takes-the-seat-identity", got == dest and email == "seat+noreply@users.example",
          "%s | %s" % (email, line))


def main():
    try:
        for t in (t_a_leftover_child_is_ended_and_the_clone_returned, t_an_unmarked_process_in_the_clone_keeps_it,
                  t_another_units_marker_is_not_this_runs, t_a_blind_scan_kills_nothing,
                  t_a_reused_det_clone_takes_the_seat_identity, t_role_launch_scan_rules_out_zombies):
            try:
                t()
            except Exception as e:  # noqa: BLE001
                import traceback
                traceback.print_exc()
                check(t.__name__ + " raised", False, "%s: %s" % (type(e).__name__, e))
    finally:
        for k in KIDS:
            if k.poll() is None:
                k.kill()
                k.wait()
    print("selftest_detached_reap: %s (%d failed)" % ("FAIL" if FAILS else "PASS", len(FAILS)))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
