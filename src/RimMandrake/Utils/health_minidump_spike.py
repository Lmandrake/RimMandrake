#!/usr/bin/env python3
"""The utility spike health_minidump.py owed before any automatic use (GPT review 1.9;
MINIDUMP_PROVE_SPIKE_BEFORE_THE_KILL). Three verbs:

    python.exe src\\RimMandrake\\Utils\\health_minidump_spike.py run <dir>     Windows python: run every case
    python3   src/RimMandrake/Utils/health_minidump_spike.py verify <dir>     anywhere: re-read the dumps OFFLINE
    python3   src/RimMandrake/Utils/health_minidump_spike.py live [<dir>]     live clause A1: dump the running game

`run` starts a stand-in target (Windows python) whose MAIN thread blocks forever in kernel32 WaitForSingleObject
while a heartbeat thread loops on kernel32 Sleep and stamps a file, so "the target still runs" is a counter that moves.
Cases, each in its own sub-folder (retention never eats another case's evidence):
  normal_<mode>_<MB>   one capture() per mode (snapshot, direct) on a 64 MB and a 1024 MB target: duration, the
                       target's suspension, size, heartbeat after
  kill_<mode>          a dumper whose write is slowed by a callback hook is killed mid-write; does the target's
                       heartbeat move during the write and after the kill? (the strand hazard)
  orphan               a later capture in kill_snapshot's folder must report the killed dumper's file as a partial
  cancel               a capture cancelled at its CancelCallback must report failed + .partial
Copies of ntdll/kernelbase/kernel32 go to <dir>/pe so `verify` can name frames by export without Windows.
`verify` exits 0 only when every case's claim holds in the files themselves; spike.json is what `run` saw.
"""
import json
import os
import shutil
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import health_minidump as D  # noqa: E402
import minidump_read as R    # noqa: E402

TARGET = r'''
import ctypes, json, os, sys, threading
k = ctypes.WinDLL("kernel32")
k.CreateEventW.restype = ctypes.c_void_p
k.WaitForSingleObject.argtypes = [ctypes.c_void_p, ctypes.c_ulong]
out, mb = sys.argv[1], int(sys.argv[2])
blob = bytearray(mb * 1024 * 1024)
for i in range(0, len(blob), 4096):
    blob[i] = 1                       # commit every page: a working set the size of the ask
hb = os.path.join(out, "heartbeat.txt")
ids = {}
def beat():
    ids["heartbeat"] = threading.get_native_id()
    n = 0
    while True:
        n += 1
        try:
            with open(hb + ".tmp", "w") as f:
                f.write(str(n))
            os.replace(hb + ".tmp", hb)
        except OSError:
            pass                      # the reader had it open (WinError 5/32): skip this stamp, keep beating
        k.Sleep(50)
t = threading.Thread(target=beat, daemon=True)
t.start()
while "heartbeat" not in ids:
    k.Sleep(5)
ids["main"] = k.GetCurrentThreadId()
ids["pid"] = os.getpid()
with open(os.path.join(out, "target.json"), "w") as f:
    json.dump(ids, f)
k.WaitForSingleObject(k.CreateEventW(None, True, False, None), 0xFFFFFFFF)   # the deliberately blocked main thread
'''

DUMPER = r'''
import sys, time
sys.path.insert(0, sys.argv[1])
import health_minidump as D
D.capture(int(sys.argv[2]), sys.argv[3], sys.argv[4], mode=sys.argv[5], hook=lambda t: time.sleep(0.25))
'''


def _hb(d):
    try:
        return int(open(os.path.join(d, "heartbeat.txt")).read().strip() or 0)
    except (OSError, ValueError):
        return None


def _moves(d, secs=1.0):
    a = _hb(d)
    time.sleep(secs)
    b = _hb(d)
    return a is not None and b is not None and b > a


LIVE = []                                  # every target started; run() kills the stragglers whatever happens


class Target:
    def __init__(self, d, mb):
        os.makedirs(d, exist_ok=True)
        self.d = d
        self.p = subprocess.Popen([sys.executable, "-c", TARGET, d, str(mb)])
        LIVE.append(self.p)
        t0 = time.time()
        while not os.path.exists(os.path.join(d, "target.json")):
            if time.time() - t0 > 60 or self.p.poll() is not None:
                raise RuntimeError("target did not start")
            time.sleep(0.1)
        time.sleep(0.3)
        self.ids = json.load(open(os.path.join(d, "target.json")))

    def stop(self):
        self.p.kill()
        self.p.wait()


def run(out):
    try:
        return _run(out)
    finally:
        for p in LIVE:
            if p.poll() is None:
                p.kill()


def _run(out):
    if os.name != "nt":
        print("run needs Windows python (python.exe)")
        return 2
    os.makedirs(out, exist_ok=True)
    pe = os.path.join(out, "pe")
    os.makedirs(pe, exist_ok=True)
    for n in ("ntdll.dll", "kernelbase.dll", "kernel32.dll"):
        shutil.copy(os.path.join(os.environ["SystemRoot"], "System32", n), os.path.join(pe, n))
    spike = {"startedUtc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "python": sys.version,
             "defaultMode": D.MODE, "cases": {}}

    def save():
        with open(os.path.join(out, "spike.json"), "w") as f:
            json.dump(spike, f, indent=1)

    # kill cases first: their orphans must age past ORPHAN_AGE_S before the orphan case looks
    for mode in ("snapshot", "direct"):
        d = os.path.join(out, "kill_" + mode)
        t = Target(d, 64)
        c = {"ids": t.ids, "mode": mode}
        dumper = subprocess.Popen([sys.executable, "-c", DUMPER, HERE, str(t.ids["pid"]), "kill-" + mode, d, mode])
        time.sleep(1.0)
        c["dumperAliveAtKill"] = dumper.poll() is None
        c["heartbeatMovesDuringWrite"] = _moves(d, 1.0)
        dumper.kill()
        dumper.wait()
        time.sleep(0.5)
        c["heartbeatMovesAfterKill"] = _moves(d, 3.0)
        c["files"] = sorted(os.listdir(d))
        t.stop()
        spike["cases"]["kill_" + mode] = c
        save()
    time.sleep(D.ORPHAN_AGE_S + 2)
    d = os.path.join(out, "kill_snapshot")
    t = Target(os.path.join(out, "orphan_target"), 64)
    rec = D.capture(t.ids["pid"], "after-kill", d)
    t.stop()
    spike["cases"]["orphan"] = {"record": rec, "files": sorted(os.listdir(d))}
    save()

    d = os.path.join(out, "cancel")
    t = Target(d, 64)
    rec = D.capture(t.ids["pid"], "cancel", d, hook=lambda typ: "cancel")
    spike["cases"]["cancel"] = {"record": rec, "heartbeatMovesAfter": _moves(d), "files": sorted(os.listdir(d))}
    t.stop()
    save()

    for mode in ("snapshot", "direct"):
        for mb in (64, 1024):
            d = os.path.join(out, "normal_%s_%d" % (mode, mb))
            t = Target(d, mb)
            rec = D.capture(t.ids["pid"], "normal", d, mode=mode)
            spike["cases"]["normal_%s_%d" % (mode, mb)] = {"ids": t.ids, "record": rec, "heartbeatMovesAfter": _moves(d)}
            t.stop()
            save()
    spike["finishedUtc"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    save()
    print(json.dumps({k: (v.get("record", v).get("status") if isinstance(v.get("record", v), dict) else None)
                      for k, v in spike["cases"].items()}))
    return 0


# ------------------------------------------------------------------------------------------------- verify
def _local(out, winpath):
    """A path `run` recorded (Windows) -> the same file under `out` here (verify may run from WSL)."""
    rel = winpath.replace("\\", "/").split("/")[-2:]
    return os.path.join(out, *rel)


def read_blocked(out, rec, ids):
    """Offline read of one dump: the main and heartbeat threads' top frames and the main thread's stack scan."""
    p = _local(out, rec["path"])
    d = R.read(p)
    pe = os.path.join(out, "pe")
    sym = R.Symbolizer(d, [os.path.join(pe, n) for n in sorted(os.listdir(pe))])
    th = {t["tid"]: t for t in d["threads"]}
    main, beat = th.get(ids["main"]), th.get(ids["heartbeat"])
    return {"file": p, "sizeOnDisk": os.path.getsize(p), "threads": len(d["threads"]), "modules": len(d["modules"]),
            "peRejected": sym.rejected,
            "mainTop": main and sym.name(main["rip"]), "heartbeatTop": beat and sym.name(beat["rip"]),
            "mainScan": main and R.stack_scan(main, sym, 24)}


def verify(out):
    spike = json.load(open(os.path.join(out, "spike.json")))
    cases, rows, ok = spike["cases"], [], True

    def row(name, good, detail):
        nonlocal ok
        ok = ok and bool(good)
        rows.append({"check": name, "pass": bool(good), "detail": detail})

    row("default_mode_is_snapshot", D.MODE == "snapshot" and spike.get("defaultMode") == "snapshot", D.MODE)
    for mode in ("snapshot", "direct"):
        for mb in (64, 1024):
            k = "normal_%s_%d" % (mode, mb)
            c = cases.get(k, {})
            rec = c.get("record", {})
            if rec.get("status") != "ok":
                row(k + "_ok", False, rec)
                continue
            if rec.get("fallbackFrom"):
                rows.append({"check": k + "_snapshot_fell_back", "pass": None,
                             "detail": {"pssError": rec.get("pssError"), "mode": rec.get("mode")}})
            r = read_blocked(out, rec, c["ids"])
            row(k + "_identifies_blocked_main_thread",
                "NtWaitForSingleObject" in (r["mainTop"] or "") and any("WaitForSingleObject" in f and "KERNELBASE" in f.upper() for f in r["mainScan"] or []),
                {"mainTop": r["mainTop"], "scan": (r["mainScan"] or [])[:6], "peRejected": r["peRejected"]})
            # the heartbeat sleeps (NtDelayExecution) or is caught stamping its file (NtSetInformationFile, measured):
            # either way a NAMED ntdll frame that is not the main thread's wait
            hb = r["heartbeatTop"] or ""
            row(k + "_tells_threads_apart", hb.lower().startswith("ntdll.dll!") and "WaitForSingleObject" not in hb, hb)
            row(k + "_measured", rec.get("durationMs", 0) > 0 and rec.get("suspendedMs") is not None
                and rec.get("sizeBytes") == r["sizeOnDisk"],
                {"durationMs": rec.get("durationMs"), "suspendedMs": rec.get("suspendedMs"), "sizeBytes": rec.get("sizeBytes"),
                 "workingSetBytes": rec.get("workingSetBytes")})
            row(k + "_target_runs_after", c.get("heartbeatMovesAfter") is True, c.get("heartbeatMovesAfter"))
    ks = cases.get("kill_snapshot", {})
    row("snapshot_killed_dumper_strands_nothing", ks.get("dumperAliveAtKill") is True and ks.get("heartbeatMovesDuringWrite") is True
        and any(D.OURS.match(n) for n in ks.get("files", []))          # the dumper had started its file when killed
        and ks.get("heartbeatMovesAfterKill") is True, {k: ks.get(k) for k in ("dumperAliveAtKill", "heartbeatMovesDuringWrite", "heartbeatMovesAfterKill")})
    kd = cases.get("kill_direct", {})
    rows.append({"check": "direct_control_measured", "pass": None,
                 "detail": {k: kd.get(k) for k in ("dumperAliveAtKill", "heartbeatMovesDuringWrite", "heartbeatMovesAfterKill")}})
    o = cases.get("orphan", {}).get("record", {})
    row("orphan_reported_as_partial", any(n.endswith(".partial") for n in o.get("orphans", []))
        and all(os.path.exists(os.path.join(out, "kill_snapshot", n)) for n in o.get("orphans", [])), o.get("orphans"))
    cr = cases.get("cancel", {}).get("record", {})
    cp = cr.get("path", "")
    row("cancelled_dump_reported_partial", cr.get("status") == "failed" and "0x800704c7" in cr.get("reason", "")
        and cp.endswith(".partial")
        and os.path.exists(_local(out, cp)) and os.path.exists(_local(out, cp[:-len(".partial")] + ".json"))
        and cases["cancel"].get("heartbeatMovesAfter") is True, {"status": cr.get("status"), "reason": cr.get("reason")})
    try:
        with open(os.path.join(out, "verify.json"), "w") as f:
            json.dump(rows, f, indent=1)
    except OSError:
        pass                      # a read-only mount (the checker's box): the printed rows are the verdict
    for r in rows:
        print("%-5s %s  %s" % ({True: "PASS", False: "FAIL", None: "INFO"}[r["pass"]], r["check"], json.dumps(r["detail"])))
    print("VERIFY %s (%d checks)" % ("PASS" if ok else "FAIL", sum(1 for r in rows if r["pass"] is not None)))
    return 0 if ok else 1


# --------------------------------------------------------------------------------------------- live A1
def live(out=None):
    """Live clause A1: one snapshot-mode dump of the running RimWorld through health_minidump.py (Windows python),
    then the game must still be alive and the dump readable offline. 0 holds, 1 does not, 2 UNMEASURED."""
    out = out or "/mnt/d/ClaudeWork/rimmandrake/minidump_spike/live"
    os.makedirs(out, exist_ok=True)
    win = subprocess.run(["wslpath", "-w", out], capture_output=True, text=True, timeout=30).stdout.strip()
    inc = "spike-live-" + time.strftime("%Y%m%dT%H%M%SZ", time.gmtime())
    try:
        tool = subprocess.run(["wslpath", "-w", os.path.join(HERE, "health_minidump.py")], capture_output=True, text=True,
                              timeout=30).stdout.strip()
        p = subprocess.run(["python.exe", tool, "--before-kill", "--incident", inc, "--dir", win],
                           capture_output=True, text=True, timeout=180)
    except (OSError, subprocess.TimeoutExpired) as e:
        print("UNMEASURED: python.exe health_minidump.py did not run: %s" % e)
        return 2
    lines = [x for x in p.stdout.splitlines() if x.startswith("{")]
    rec = json.loads(lines[-1]) if lines else {}
    if rec.get("status") == "refused" and "processes" in rec.get("reason", ""):
        print("UNMEASURED: %s" % rec["reason"])
        return 2
    if rec.get("status") != "ok":
        print("FAIL: %s" % json.dumps(rec))
        return 1
    time.sleep(2)
    alive = subprocess.run(["tasklist.exe", "/FI", "PID eq %d" % rec["pid"], "/FO", "CSV", "/NH"],
                           capture_output=True, text=True, timeout=30).stdout
    d = R.read(os.path.join(out, rec["path"].replace("\\", "/").split("/")[-1]))   # live() dumps straight into out
    res = {"durationMs": rec.get("durationMs"), "suspendedMs": rec.get("suspendedMs"), "sizeBytes": rec.get("sizeBytes"),
           "workingSetBytes": rec.get("workingSetBytes"), "threads": len(d["threads"]), "modules": len(d["modules"]),
           "alive": D.GAME_EXE.lower() in alive.lower()}
    with open(os.path.join(out, inc + ".result.json"), "w") as f:
        json.dump(res, f, indent=1)
    good = res["alive"] and res["threads"] > 0 and any(m["name"].lower() == D.GAME_EXE.lower() for m in d["modules"])
    print(("PASS " if good else "FAIL ") + json.dumps(res))
    return 0 if good else 1


def main(argv=None):
    a = (argv if argv is not None else sys.argv[1:])
    if not a or a[0] not in ("run", "verify", "live"):
        print(__doc__)
        return 2
    if a[0] == "run":
        return run(a[1])
    if a[0] == "verify":
        return verify(a[1])
    return live(a[1] if len(a) > 1 else None)


if __name__ == "__main__":
    sys.exit(main())
