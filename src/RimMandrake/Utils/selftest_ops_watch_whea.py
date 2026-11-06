#!/usr/bin/env python3
"""selftest_ops_watch_whea.py -- the WHEA count of ops_watch's disk family (DDRIVE_PCIE_MONITOR_CORRECTED_FOR_NOW).

Archmagi's D: NVMe logs WHEA-Logger 17 (corrected PCIe AER). Each case plants the collector's raw lines
(EV|id|level|iso, then END|n: what WHEA_PS prints) in a file RM_OPS_WHEA_EVENTS names, runs the real
`ops_watch.py run --family disk` CLI into a temp dir, and reads what the pass wrote. Nothing is filed: alarms.json
holds a crossing as PENDING. The lines come from the shipped rules. No Windows program runs."""
import json
import os
import subprocess
import sys
import tempfile
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import ops_watch as OW  # noqa: E402

TMP = Path(tempfile.mkdtemp(prefix="selftest_ops_whea_"))
FAILS = []
COR, SEV, BLIND = "disk.whea_corrected_24h", "disk.whea_severe_24h", "disk.whea_blind"
RULES = json.loads((HERE / "ops_watch_rules.json").read_text(encoding="utf-8"))
TG = {t["key"]: t for t in RULES["targets"] if isinstance(t, dict) and str(t.get("key", "")).startswith("disk.whea")}
ENV = {"RM_POOL_ROOT": str(TMP / "pool"), "RM_SCRATCH_ROOT": str(TMP / "scratch"), "RM_OBJSTORE_STATE": str(TMP / "objstore"),
       "RM_SESSION_GLOB": str(TMP / "none/*"), "RM_OPS_DISKS": "root=/"}
(TMP / "pool").mkdir()
(TMP / "scratch").mkdir()
NOW = time.time()


def check(name, cond, detail=""):
    print(("PASS  " if cond else "FAIL  ") + name + ("" if cond else "  %s" % str(detail)[:400]))
    if not cond:
        FAILS.append(name)


def ev(i, level=3, age_h=1.0):
    # the 7-digit fraction Windows' ToString('o') really prints (measured 2026-11-06: 2026-11-06T04:20:28.8832041Z)
    t = NOW - age_h * 3600
    return "EV|%d|%d|%s.8832041Z" % (i, level, time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime(t)))


def lines(*evs):
    return list(evs) + ["END|%d" % len(evs)]


def cli_pass(name, body):
    """body: a list of lines, raw text, or None (no file)."""
    d = TMP / name
    d.mkdir()
    (d / "runs.jsonl").write_text("")
    f = d / "whea.txt"
    if body is not None:
        f.write_text(body if isinstance(body, str) else "\r\n".join(body) + "\r\n", encoding="utf-8")
    ops = d / "ops"
    env = {**os.environ, **ENV, "RM_SCRATCH_REAP_RUNS": str(d / "runs.jsonl"), "RM_OPS_WATCH_DIR": str(ops),
           "RM_OPS_WHEA_EVENTS": str(f)}
    r = subprocess.run([sys.executable, str(HERE / "ops_watch.py"), "run", "--family", "disk"], env=env, capture_output=True,
                       text=True, timeout=120)
    assert r.returncode == 0, r.stderr[-600:]
    dg = json.loads((ops / "digest.json").read_text())
    return dg["kpis"], json.loads((ops / "alarms.json").read_text())


def alarm(alarms, key):
    return [a for k, a in alarms.items() if key in k and isinstance(a, dict)]


# The rules: the item's lines, as filed.
check("three WHEA targets, all alarms", set(TG) == {COR, SEV, BLIND} and all(t.get("alarm") is True for t in TG.values()), TG)
check("corrected alarms over 30 a day", TG[COR]["op"] == ">" and TG[COR]["value"] == 30, TG.get(COR))
check("severe and blind alarm on any one", TG[SEV]["value"] == 0 and TG[BLIND]["value"] == 0, TG)
import pulse_core as PC  # noqa: E402
for k, t in TG.items():
    # the filer mints base + "_" + a 4-letter twist; a base one word or 5 chars too long reads "no mintable alarm name"
    n = "%s_%s" % (t["name"], OW.alarm_twist(t["name"]))
    check("%s's item name mints as filed (%s)" % (k, n), not PC._model().mint_problems(n, set()), PC._model().mint_problems(n, set()))
check("the query asks the WHEA-Logger provider for WHEA_DAYS days and survives zero events",
      "Microsoft-Windows-WHEA-Logger" in OW.WHEA_PS and "NoMatchingEventsFound" in OW.WHEA_PS
      and "AddDays(-8)" in OW.WHEA_PS % OW.WHEA_DAYS, OW.WHEA_PS)
check("the shell is an absolute path (a systemd unit has no /mnt/c on PATH)", OW.POWERSHELL.startswith("/mnt/c/"), OW.POWERSHELL)

# Sanity probe: a quiet week reads its real count and alarms nothing, so the alarms below are the fault.
# The old twelve sit 24.5 h and up: ev() floors to the second then adds .883 s, and the subprocess reads its own later
# clock, so an event planted at exactly 24 h fell either side of the window (blind check, 2026-11-06: 5 of 6 runs read 6).
quiet = lines(*[ev(17, age_h=h) for h in (1, 5, 9, 20, 23.5)], *[ev(17, age_h=24.5 + 3 * i) for i in range(12)])
k, al = cli_pass("quiet", quiet)
check("a quiet day reads 5 corrected, MEASURED", k[COR]["m"] == "MEASURED" and k[COR]["v"] == 5, k[COR])
check("a quiet day: no severe, not blind", k[SEV]["v"] == 0 and k[BLIND]["v"] == 0, (k[SEV], k[BLIND]))
check("a quiet day alarms nothing", not alarm(al, "disk.whea"), al)
os.environ["RM_OPS_WHEA_EVENTS"] = str(TMP / "quiet" / "whea.txt")
pt = OW.whea_reading(NOW)[COR]["x"]
check("the 8-day curve rides on the reading (17 events by UTC day)", sum(pt["by_day_utc"].values()) == 17, pt)
del os.environ["RM_OPS_WHEA_EVENTS"]

# The window edge, at one fixed clock (in-process, so no subprocess drift): 23.9 h in, 24.1 h out, a 5-min-future row in.
(TMP / "edge").mkdir()
(TMP / "edge" / "whea.txt").write_text("\r\n".join(lines(ev(17, age_h=23.9), ev(17, age_h=24.1), ev(17, age_h=-0.05))) + "\r\n")
os.environ["RM_OPS_WHEA_EVENTS"] = str(TMP / "edge" / "whea.txt")
eg = OW.whea_reading(NOW)[COR]
check("the 24 h edge: 23.9 h and a clock-skewed future row count, 24.1 h does not", eg["v"] == 2, eg)
del os.environ["RM_OPS_WHEA_EVENTS"]

k, al = cli_pass("none", ["END|0"])
check("Windows saying zero reads a measured 0", k[COR]["m"] == "MEASURED" and k[COR]["v"] == 0 and k[BLIND]["v"] == 0, k[COR])

# The line's edge: 30 is the owner's day, 31 is the alarm.
k, al = cli_pass("thirty", lines(*[ev(17, age_h=0.5 + i * 0.7) for i in range(30)]))
check("30 in 24 h: no alarm", k[COR]["v"] == 30 and not alarm(al, COR), (k[COR], al))
k, al = cli_pass("thirty_one", lines(*[ev(17, age_h=0.5 + i * 0.7) for i in range(31)]))
a = alarm(al, COR)
check("31 in 24 h: the corrected alarm, under its fixed item", k[COR]["v"] == 31 and a and TG[COR]["name"] in json.dumps(a), al)
check("31 corrected is not severe", not alarm(al, SEV), al)

# Severe: fatal ids, a CPU machine check, or a Level Error, each on its own.
for name, row in (("fatal18", ev(18, level=2)), ("fatal20", ev(20, level=1)), ("mce19", ev(19, level=3)),
                  ("level_error17", ev(17, level=2))):
    k, al = cli_pass(name, lines(ev(17), row))
    a = alarm(al, SEV)
    check("%s: severe 1, its alarm raised under its fixed item" % name, k[SEV]["v"] == 1 and a and TG[SEV]["name"] in json.dumps(a), al)
    check("%s: not also counted corrected" % name, k[COR]["v"] == 1, k[COR])
k, al = cli_pass("old_fatal", lines(ev(18, level=2, age_h=30)))
check("a fatal error 30 h old is outside the 24 h window", k[SEV]["v"] == 0 and not alarm(al, SEV), k[SEV])

# Every way of not seeing: UNMEASURED and the blind alarm, never a measured zero.
for name, body, says in (("missing", None, "No such file"), ("empty", "", "no END"),
                         ("err", ["ERR|Access is denied"], "Access is denied"), ("no_end", [ev(17)], "no END"),
                         ("end_disagrees", [ev(17), "END|3"], "END says"), ("torn_row", ["EV|17|3", "END|1"], "unreadable"),
                         ("bad_time", ["EV|17|3|yesterday", "END|1"], "unreadable"), ("junk", ["Get-WinEvent : oops", "END|0"], "unexpected")):
    k, al = cli_pass("blind_" + name, body)
    check("%s: reads UNMEASURED" % name, k[COR]["m"] == "UNMEASURED" and k[SEV]["m"] == "UNMEASURED"
          and says in (k[COR].get("why") or ""), k[COR])
    check("%s: the blind alarm stands under its own item" % name, k[BLIND]["v"] == 1 and TG[BLIND]["name"] in json.dumps(alarm(al, BLIND)), al)
    check("%s: no false corrected or severe alarm" % name, not alarm(al, COR) and not alarm(al, SEV), al)

# A host with no Windows (no powershell.exe) reads blind, never zero.
saved = OW.POWERSHELL
OW.POWERSHELL = str(TMP / "no_such_powershell.exe")
r = OW.whea_reading(NOW)
OW.POWERSHELL = saved
check("no powershell: blind with the reason", r[BLIND]["v"] == 1 and r[COR]["m"] == "UNMEASURED" and "no " in r[COR]["why"], r)

print("selftest_ops_watch_whea: %s (%d failed)" % ("FAIL" if FAILS else "PASS", len(FAILS)))
sys.exit(1 if FAILS else 0)
