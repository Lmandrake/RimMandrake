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
# ---- one-off per-core sweep (steve_cpu_sweep.py): result parsing and the refuse / yield decisions, offline ----
import steve_cpu_sweep as sw
HEAT = "pkg_c=40/78 core_max_c=71 hot_core=3 cores_max_c=[60,71,65] samples=100 vcore_v=1.412"
def core_line(cpu, fatal=0, whea=0, alive=1, cpusec=58, heat=HEAT):
    return "noise\nSWEEPCORE cpu=%d alive=%d cpusec=%d fatal=%d whea=%d heat=%s\n" % (cpu, alive, cpusec, fatal, whea, heat)
PRE_OK = "PRE n=18 p95=1 temp=1 rimworld=0 p95run=0 boot=1000 vcore_idle=1.033"
cs = [sw.core_result(sw.parse_core(core_line(i)), i) for i in range(18)]
r = sw.summarize(cs, idle_vcore=1.033, stopped=None)
check("sweep: 18 clean cores -> PASS, 18 read, vcore max 1.412", r["verdict"] == "PASS" and r["n_read"] == 18 and r["vcore_load_max"] == 1.412)
check("sweep: the one plain-language line names verdict and vcore", "PASS" in r["line"] and "1.412" in r["line"] and "1.033" in r["line"])
cs2 = list(cs); cs2[7] = sw.core_result(sw.parse_core(core_line(7, fatal=2)), 7)
r2 = sw.summarize(cs2, 1.033, None)
check("sweep: one core with a Prime95 error -> FAIL naming core 7 only", r2["verdict"] == "FAIL" and r2["failed"] == [7])
cs3 = list(cs); cs3[4] = sw.core_result(sw.parse_core(core_line(4, whea=1)), 4); cs3[9] = sw.core_result(sw.parse_core(core_line(9, alive=0, cpusec=12)), 9)
r3 = sw.summarize(cs3, 1.033, None)
check("sweep: WHEA in the window and a dead worker both fail their cores", r3["failed"] == [4, 9])
nos = sw.core_result(sw.parse_core(core_line(2, heat="heat=UNMEASURED(no_cpu_temperature_sensor)")), 2)
check("sweep: no sensor reading is UNMEASURED, never 0", nos["vcore"] is None and nos["core_max_c"] is None and nos["status"] == "PASS")
r4 = sw.summarize([nos] * 3, None, None)
check("sweep: no vcore anywhere -> vcore UNMEASURED in result and line", r4["vcore_load_max"] is None and "UNMEASURED" in r4["line"] and r4["verdict"] == "PASS_UNMEASURED_HEAT")
check("sweep: a garbled core answer fails that core as NO_ANSWER, not PASS", sw.core_result(sw.parse_core("garbage"), 5)["status"] == "FAIL")
check("sweep: Prime95 missing refuses to start", sw.decide_start(sw.parse_pre(PRE_OK.replace("p95=1", "p95=0")), [], False)[0] is False)
check("sweep: stevetemp missing still starts (heat UNMEASURED)", sw.decide_start(sw.parse_pre(PRE_OK.replace("temp=1", "temp=0")), [], False)[0] is True)
check("sweep: clean idle Steve starts", sw.decide_start(sw.parse_pre(PRE_OK), [], False) == (True, "idle"))
check("sweep: a testq job running at start refuses", sw.decide_start(sw.parse_pre(PRE_OK), ["J1.json"], False)[0] is False)
check("sweep: worker busy or unknown at start refuses", sw.decide_start(sw.parse_pre(PRE_OK), [], True)[0] is False and sw.decide_start(sw.parse_pre(PRE_OK), [], None)[0] is False)
check("sweep: RimWorld or a stray Prime95 at start refuses", sw.decide_start(sw.parse_pre(PRE_OK.replace("rimworld=0", "rimworld=1")), [], False)[0] is False and sw.decide_start(sw.parse_pre(PRE_OK.replace("p95run=0", "p95run=1")), [], False)[0] is False)
check("sweep: unreachable Steve refuses", sw.decide_start(sw.parse_pre(""), [], False)[0] is False)
check("sweep: job arriving mid-sweep yields", sw.decide_continue(["J2.json"], False, 0, "1000", "1000")[0] is False and sw.decide_continue([], True, 0, "1000", "1000")[0] is False)
check("sweep: quiet lane continues; a changed boot stops", sw.decide_continue([], False, 0, "1000", "1000")[0] is True and sw.decide_continue([], False, 0, "1000", "2000")[0] is False)
ry = sw.summarize(cs[:5], 1.033, "yielded: job J2 arrived")
check("sweep: a yielded sweep is YIELDED, 5 read, never PASS", ry["verdict"] == "YIELDED" and ry["n_read"] == 5)
sys.exit(0 if all(ok) else 1)
