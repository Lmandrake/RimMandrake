#!/usr/bin/env python3
"""selftest_steve_cpu_retest.py - the retest controller's state machine with Steve, testq and the clock faked.
Proves: a running job holds the drain (no unmask); two quiet ticks unmask + reboot; a boot with 20 CPUs resumes the
lane and starts RUNNING; a fault file drains, restores numproc 18, reboots, and ends with the lane resumed; a clean
done.json leaves the machine unmasked; a boot that still shows 18 CPUs after the unmask restores the mask."""
import os, sys, tempfile, json, glob
tmp = tempfile.mkdtemp()
os.environ["STEVE_RETEST_HOME"] = os.path.join(tmp, "home")
os.environ["TESTQ_HOME"] = os.path.join(tmp, "q")
os.makedirs(os.path.join(tmp, "q", "running"))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import steve_cpu_retest as m

calls, F = [], {"boot": "100", "cpus": "18", "rimworld": "0", "numproc": "18"}
fault, done, busy = {}, {}, [False]


def fake_ps(script, timeout=90):
    if "bcdedit /deletevalue" in script:
        calls.append("unmask"); return 0, "NUMPROC_LEFT=0\n"
    if "bcdedit /set numproc 18" in script:
        calls.append("restore"); return 0, "NUMPROC=18\n"
    if script.startswith("shutdown"):
        calls.append("reboot"); return 0, ""
    if "armed.flag" in script and "Remove-Item" in script:
        return 0, ""
    return 0, ""


def fake_testq(*a):
    calls.append("testq " + a[0])
    if a[0] == "pause": open(os.path.join(tmp, "q", "paused.json"), "w").write("{}")
    if a[0] == "resume":
        try: os.remove(os.path.join(tmp, "q", "paused.json"))
        except OSError: pass
    return 0, ""


m.ps, m.testq = fake_ps, fake_testq
m.steve_facts = lambda: dict(F)
m.worker_busy = lambda: busy[0]
m.mirror_readings = lambda: []
m.steve_json = lambda n: fault if n == "fault.json" else done
st = lambda: m.load()["state"]
ok = []
def check(name, cond):
    ok.append(cond); print(("PASS " if cond else "FAIL ") + name)

m.cmd_arm()
open(os.path.join(tmp, "q", "running", "J1.json"), "w").write("{}")
m.tick(); m.tick()
check("running job holds the drain", st() == "DRAIN" and "unmask" not in calls)
os.remove(os.path.join(tmp, "q", "running", "J1.json"))
m.tick(); check("one quiet tick is not enough", st() == "DRAIN")
m.tick(); check("two quiet ticks unmask and reboot", st() == "WAIT_BOOT" and calls.count("unmask") == 1 and "reboot" in calls)
m.tick(); check("still the old boot: keep waiting", st() == "WAIT_BOOT")
F.update(boot=str(int(m.load()["reboot_t0"]) + 100), cpus="20", numproc="")
m.tick(); check("20 CPUs: lane resumed, RUNNING", st() == "RUNNING" and not m.lane_paused())
fault.update(event="cpu", cpu=18, bad=["chk"])
m.tick(); check("fault: lane paused, FAULT_DRAIN", st() == "FAULT_DRAIN" and m.lane_paused())
busy[0] = True; m.tick(); m.tick(); check("fault drain waits for the job", st() == "FAULT_DRAIN" and "restore" not in calls)
busy[0] = False; m.tick(); m.tick()
check("fault: numproc 18 restored and rebooted", st() == "WAIT_RESTORE" and "restore" in calls)
F.update(boot=str(int(m.load()["reboot_t0"]) + 100), cpus="18", numproc="18")
m.tick(); check("restore boot: lane resumed, END_FAULT", st() == "END_FAULT" and not m.lane_paused())

# clean path
import shutil; shutil.rmtree(os.environ["STEVE_RETEST_HOME"]); calls.clear(); fault.clear(); F.update(boot="100", cpus="18", numproc="18")
m.cmd_arm(); m.tick(); m.tick(); m.tick()
F.update(boot=str(int(m.load()["reboot_t0"]) + 100), cpus="20", numproc=""); m.tick()
done.update(verdict="CLEAN"); m.tick()
check("clean past onset: DONE_CLEAN, no restore", st() == "DONE_CLEAN" and "restore" not in calls)

# the unmask did not give 20 CPUs
shutil.rmtree(os.environ["STEVE_RETEST_HOME"]); calls.clear(); done.clear(); F.update(boot="100", cpus="18", numproc="18")
m.cmd_arm(); m.tick(); m.tick(); m.tick()
F.update(boot=str(int(m.load()["reboot_t0"]) + 100), cpus="18"); m.tick(); m.tick(); m.tick()
check("boot with 18 CPUs after unmask: mask restored", "restore" in calls)
sys.exit(0 if all(ok) else 1)
