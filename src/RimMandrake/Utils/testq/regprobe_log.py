#!/usr/bin/env python3
"""regprobe_log.py - read SteveDesktop's register-probe log (RIMMANDRAKE_BUILD_STEVE_REGISTER_PROBE_SEES_UPPER_HALF_LOSS).

The probe is steve_cpu_retest/regprobe.c (task "SteveDiag Register Probe"); its log, C:\\SteveDesktop\\diag\\logs\\regprobe.log,
is mirrored to QHOME/regprobe.log by fault_monitor.py's tick and read here. Pure functions of the lines: no ssh.

Four answers stay apart, per boot and overall:
  fault       cycles with a wrong register (counted only under a passing CONTROL from a normal build)
  clean       cycles that looked at every CPU on every path and found nothing wrong (zero, measured)
  partial     nothing wrong, but some CPU or path could not be looked at (counted as looked-at for the CPUs it saw)
  unmeasured  the cycle could look at nothing
and two that never count as either way: unproven (the start's CONTROL failed or is missing: the instrument was not shown
able to see) and planted (a build=inject_* start: the RED build's faults are planted, never real).
verdict(): FAULT / CLEAN / UNMEASURED(<why>), one line; a missing or stale log is UNMEASURED, never CLEAN.
"""
import calendar
import re
import time

_TS = r"(\d{4}-\d\d-\d\d \d\d:\d\d:\d\d)Z"
LINE_RE = re.compile("^" + _TS + r" (RPSTART|RPCONTROL|RPFAULT|RPCYCLE) (.*)$")
KV_RE = re.compile(r"(\w+)=(\[[^\]]*\]|\d{4}-\d\d-\d\d \d\d:\d\d:\d\dZ|\S+)")     # boot= holds a space
RESULTS = ("fault", "clean", "partial", "unmeasured")
CLASSES = ("upper_half_loss", "lower_half_error", "sse_error", "scalar_error")
# budget: danger=a dead probe read as a live one; ends no work: a count of cycles, no time: the probe reads as not running
STALE_CYCLES = 3        # no cycle for this many cycle lengths: the probe is not running (one late cycle is not)


def epoch(ts):
    return calendar.timegm(time.strptime(ts, "%Y-%m-%d %H:%M:%S"))


def _near(a, b, slack=120):
    try:
        return abs(epoch(a) - epoch(b)) <= slack
    except ValueError:
        return False


def kv(rest):
    return {k: v for k, v in KV_RE.findall(rest)}


def blist(v):
    v = (v or "[]").strip("[]")
    return [x for x in v.split(",") if x]


def _boot():
    return {"boot": None, "starts": 0, "control_ok": None, "build": None, "cycle_s": None,
            "cycles": {r: 0 for r in RESULTS + ("unproven", "planted")}, "faults": [], "bad_cpus": {}, "classes": {},
            "first_fault": None, "last_cycle": None}


def analyse(lines):
    """-> {boots: [per boot dict], unparsed, last_cycle, last_start, cycle_s}. A boot is keyed by RPSTART's boot=; a cycle
    or fault before any start is unproven (nothing said which build made it or whether its control passed)."""
    boots, cur, unparsed, last_cycle, cycle_s = [], None, 0, None, None
    by_boot = {}
    for line in lines:
        line = line.rstrip("\r\n")
        m = LINE_RE.match(line)
        if not m:
            unparsed += bool(line.strip())
            continue
        t, kind, f = epoch(m.group(1)), m.group(2), kv(m.group(3))
        if kind == "RPSTART":
            b = f.get("boot", "").rstrip("Z")
            cur = by_boot.get(b)
            if cur is None and boots and boots[-1]["boot"] and _near(boots[-1]["boot"], b):
                cur = boots[-1]         # boot= is now minus the tick count: two starts of one boot can differ by a second
            if cur is None:
                cur = by_boot[b] = _boot()
                cur["boot"] = b
                boots.append(cur)
                unparsed = 0        # an older boot's torn line says nothing of the probe now
            cur["starts"] += 1
            cur["build"] = f.get("build")
            cur["control_ok"] = None           # each start must prove itself again
            try:
                cur["cycle_s"] = cycle_s = float(f.get("cycle", "300s").rstrip("s"))
            except ValueError:
                cur["cycle_s"] = None
            continue
        if cur is None:
            cur = _boot()
            boots.append(cur)
        if kind == "RPCONTROL":
            cur["control_ok"] = f.get("ok") == "1"
            continue
        counted = cur["build"] == "normal" and cur["control_ok"] is True
        if kind == "RPFAULT":
            if counted:
                cur["faults"].append(dict(f, at=m.group(1) + "Z"))
            continue
        # RPCYCLE
        last_cycle = cur["last_cycle"] = t
        res = f.get("result")
        if res not in RESULTS:
            unparsed += 1
            continue
        if cur["build"] not in (None, "normal"):
            cur["cycles"]["planted"] += 1
            continue
        if not counted:
            cur["cycles"]["unproven"] += 1
            continue
        cur["cycles"][res] += 1
        if res == "fault":
            cur["first_fault"] = cur["first_fault"] or m.group(1) + "Z"
            for item in blist(f.get("bad")):
                cpu, _, cls = item.partition(":")
                cur["bad_cpus"][cpu] = cur["bad_cpus"].get(cpu, 0) + 1
                for c in cls.split("+"):
                    cur["classes"][c] = cur["classes"].get(c, 0) + 1
    last_start = boots[-1] if boots else None
    return {"boots": boots, "unparsed": unparsed, "last_cycle": last_cycle, "last_start": last_start, "cycle_s": cycle_s}


def verdict(a, now=None):
    """-> (word, line): FAULT, CLEAN or UNMEASURED; the newest boot decides, older boots are history."""
    now = time.time() if now is None else now
    if not a["boots"]:
        return "UNMEASURED", "UNMEASURED(no probe line in the log: the probe is not installed or has never run)"
    b = a["boots"][-1]
    c = b["cycles"]
    if a["last_cycle"] is None:
        return "UNMEASURED", "UNMEASURED(the probe started but wrote no cycle yet)"
    age = now - a["last_cycle"]
    limit = STALE_CYCLES * (a["cycle_s"] or 300)
    if c["fault"]:
        return "FAULT", "FAULT %d of %d counted cycles this boot, first %s, classes %s, CPUs %s" % (
            c["fault"], c["fault"] + c["clean"] + c["partial"], b["first_fault"], _d(b["classes"]), _d(b["bad_cpus"]))
    if age > limit:
        return "UNMEASURED", "UNMEASURED(stale: the newest cycle is %d s old, over %d s: the probe is not running)" % (age, limit)
    if b["build"] not in (None, "normal"):
        return "UNMEASURED", "UNMEASURED(the newest start is build=%s: planted faults only)" % b["build"]
    if b["control_ok"] is not True:
        return "UNMEASURED", "UNMEASURED(the newest start's CONTROL %s: the instrument is unproven)" % (
            "failed" if b["control_ok"] is False else "is missing")
    if not (c["clean"] + c["partial"]):
        return "UNMEASURED", "UNMEASURED(no cycle of this boot could look: %d unmeasured)" % c["unmeasured"]
    return "CLEAN", "CLEAN 0 faults in %d counted cycles this boot (%d full, %d partial; %d could not look)" % (
        c["clean"] + c["partial"], c["clean"], c["partial"], c["unmeasured"])


def _d(d):
    return ",".join("%s:%d" % kv_ for kv_ in sorted(d.items(), key=lambda x: (len(x[0]), x[0]))) or "-"


def report_lines(lines, now=None):
    """The register-probe section of fault_monitor.py report."""
    a = analyse(lines)
    word, line = verdict(a, now)
    out = ["register probe (regprobe.log): " + line]
    if a["boots"]:
        out.append("%-21s %6s %5s %5s %7s %10s %8s %7s %-9s %s" % ("boot", "starts", "fault", "clean", "partial", "unmeasured",
                                                                    "unproven", "planted", "control", "classes / CPUs"))
    for b in a["boots"]:
        c = b["cycles"]
        out.append("%-21s %6d %5d %5d %7d %10d %8d %7d %-9s %s / %s" % (
            (b["boot"] or "(no start)") + "Z" * bool(b["boot"]), b["starts"], c["fault"], c["clean"], c["partial"],
            c["unmeasured"], c["unproven"], c["planted"], {True: "ok", False: "FAILED", None: "missing"}[b["control_ok"]],
            _d(b["classes"]), _d(b["bad_cpus"])))
    if a["unparsed"]:
        out.append("    %d probe lines not understood: the parser no longer reads the probe" % a["unparsed"])
    return word, out
