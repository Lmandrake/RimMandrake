#!/usr/bin/env python3
"""Digest the SteveDesktop raw streams in ../raw into ../digest. Read-only on raw. Run: python3 -I make_digests.py <package dir>.

Eras (UTC): turbo off (PROCTHROTTLEMAX 99) from 2026-11-07T16:00Z; +0.100 V core offset from the boot 2026-11-17T15:32:58Z.
"""
import collections, csv, re, statistics, sys
from pathlib import Path

PKG = Path(sys.argv[1])
RAW, DIG = PKG / "raw", PKG / "digest"
DIG.mkdir(exist_ok=True)
TURBO_OFF = "2026-11-07 16:00:00"
RAISE = "2026-11-17 15:32:58"


def era(ts):
    return "1_turbo_on" if ts < TURBO_OFF else ("2_turbo_off_pre_raise" if ts < RAISE else "3_post_raise")


def stats(xs):
    if not xs:
        return "n=0"
    return "n=%d mean=%.3f min=%.3f max=%.3f" % (len(xs), statistics.mean(xs), min(xs), max(xs))


# ---------- watch.log (the 5-minute per-CPU SIMD check) ----------
cyc = re.compile(r"^(\S+ \S+)Z CYCLE uptime_h=([\d.]+) bad_cpus=\[([^\]]*)\] n_ok=(\d+)(.*)$")
boots, cur = [], None
bad_rows, per_hour = [], collections.defaultdict(lambda: [0, 0])
per_cpu = collections.defaultdict(collections.Counter)
era_v = collections.defaultdict(list); era_t = collections.defaultdict(list); era_c = collections.Counter(); era_b = collections.Counter()
for line in open(RAW / "steve_logs" / "watch.log", errors="replace"):
    line = line.rstrip("\n")
    if " WATCH START " in line:
        m = re.search(r"boot=(\S+ \S+)Z", line)
        b = m.group(1) if m else "?"
        if cur is None or cur["boot"] != b:
            cur = {"boot": b, "cycles": 0, "bad": 0, "first_bad_h": None, "cpus": collections.Counter(),
                   "vc": [], "tc": [], "last_h": 0.0, "controls": []}
            boots.append(cur)
        bad_rows.append(line)
        continue
    if " CONTROL " in line:
        if cur is not None:
            cur["controls"].append(line.split(" CONTROL ")[1])
        bad_rows.append(line)
        continue
    m = cyc.match(line)
    if not m or cur is None:
        continue
    ts, up, bad, rest = m.group(1), float(m.group(2)), m.group(3), m.group(5)
    cpus = [int(x) for x in bad.split(",") if x.strip()]
    e = era(ts)
    cur["cycles"] += 1; cur["last_h"] = up; era_c[e] += 1
    h = per_hour[ts[:13]]; h[0] += 1
    vm = re.search(r"vcore_v=([\d.]+)", rest); tm = re.search(r"core_max_c=(\d+)", rest)
    if vm:
        cur["vc"].append(float(vm.group(1))); era_v[e].append(float(vm.group(1)))
    if tm:
        cur["tc"].append(int(tm.group(1))); era_t[e].append(int(tm.group(1)))
    if cpus:
        cur["bad"] += 1; h[1] += 1; era_b[e] += 1
        if cur["first_bad_h"] is None:
            cur["first_bad_h"] = up
        for c in cpus:
            cur["cpus"][c] += 1; per_cpu[e][c] += 1
        bad_rows.append(line)

with open(DIG / "watch_per_boot.tsv", "w") as o:
    o.write("boot_utc\tera_at_boot\tcycles\tbad_cycles\tbad_share\tfirst_bad_uptime_h\tlast_uptime_h\tbad_cpus(cpu:cycles)\tvcore_v\tcore_max_c\tcontrol\n")
    for b in boots:
        o.write("%s\t%s\t%d\t%d\t%.3f\t%s\t%.2f\t%s\t%s\t%s\t%s\n" % (
            b["boot"], era(b["boot"]), b["cycles"], b["bad"], b["bad"] / b["cycles"] if b["cycles"] else 0,
            "%.2f" % b["first_bad_h"] if b["first_bad_h"] is not None else "none",
            b["last_h"], ",".join("%d:%d" % kv for kv in sorted(b["cpus"].items())), stats(b["vc"]), stats(b["tc"]),
            " | ".join(b["controls"]) or "none logged"))
with open(DIG / "watch_per_hour.tsv", "w") as o:
    o.write("hour_utc\tcycles\tbad_cycles\n")
    for k in sorted(per_hour):
        o.write("%s\t%d\t%d\n" % (k, *per_hour[k]))
with open(DIG / "watch_per_cpu_by_era.tsv", "w") as o:
    o.write("era\tcycles_in_era\tbad_cycles_in_era\t" + "\t".join("cpu%d" % c for c in range(20)) + "\n")
    for e in sorted(era_c):
        o.write("%s\t%d\t%d\t%s\n" % (e, era_c[e], era_b[e], "\t".join(str(per_cpu[e].get(c, 0)) for c in range(20))))
with open(DIG / "watch_bad_rows.log", "w") as o:
    o.write("# Every WATCH START, CONTROL and bad CYCLE line of watch.log, whole and in order (clean cycles omitted).\n")
    o.write("\n".join(bad_rows) + "\n")
with open(DIG / "watch_era_sensors.txt", "w") as o:
    o.write("# vcore and hottest-core readings carried on watch CYCLE lines, by era (cycles without a reading excluded)\n")
    for e in sorted(era_c):
        o.write("%s cycles=%d bad=%d | vcore_v %s | core_max_c %s\n" % (e, era_c[e], era_b[e], stats(era_v[e]), stats(era_t[e])))

# ---------- soak.log (Prime95 72 h soak) ----------
soak = (RAW / "steve_soak" / "soak.log").read_text(errors="replace").splitlines()
run = [l for l in soak if l >= "2026-11-18T01:2"]
step = re.compile(r"^(\S+) pass=(\d+) cpu=(-?\d+) (PASS|FAIL \S+) fatal=(\d+) whea=(\d+) alive=(\d+)(?: load=(-?\d+))?.*?(?:core_max_c=(\d+))?.*?(?:vcore_v=([\d.]+))?$")
steps = [step.match(l) for l in run]
steps = [m for m in steps if m]
fails = [m.group(0) for m in steps if m.group(4) != "PASS"]
other = [l for l in soak if not step.match(l)]
vc = [float(x.group(1)) for x in (re.search(r"vcore_v=([\d.]+)", m.group(0)) for m in steps) if x]
cm = [int(x.group(1)) for x in (re.search(r"core_max_c=(\d+)", m.group(0)) for m in steps) if x]
percpu = collections.Counter(m.group(3) for m in steps)
with open(DIG / "soak_digest.md", "w") as o:
    o.write("# Prime95 soak digest (run S20261118T012929Z and the earlier lines of soak.log)\n\n")
    o.write("Steps in the 72 h run: %d; FAIL steps: %d; steps per cpu (cpu=-1 is the all-core step): %s\n\n" % (
        len(steps), len(fails), dict(sorted(percpu.items(), key=lambda kv: int(kv[0])))))
    o.write("vcore_v over steps: %s\n\ncore_max_c over steps: %s\n\n" % (stats(vc), stats([float(x) for x in cm])))
    o.write("## Every FAIL step, whole\n\n" + "\n".join(fails) + "\n\n")
    o.write("## Every non-step line of soak.log (START, END, CONTROL, REBOOT, WAIT, PASS_COMPLETE excluded below), whole\n\n")
    o.write("\n".join(l for l in other if "PASS_COMPLETE" not in l) + "\n")

# ---------- Windows events ----------
ev = list(csv.DictReader(open(RAW / "winevents" / "events_20261020_now.csv", encoding="utf-8-sig")))
app = re.compile(r"Faulting application name: ([^,]+),.*?Faulting module name: ([^,]+),.*?Exception code: (0x[0-9a-fA-F]+)")
byday = collections.defaultdict(collections.Counter)
rows = []
for x in ev:
    if x["id"] == "1000" and x["provider"] == "Application Error":
        m = app.search(x["msg"])
        a, mod, code = (m.group(1), m.group(2), m.group(3)) if m else ("?", "?", "?")
        byday[x["utc"][:10]][a] += 1
        rows.append("%s\t%s\t%s\t%s\t%s" % (x["utc"], era(x["utc"].replace("T", " ").rstrip("Z")), a, mod, code))
with open(DIG / "winevents_app_crashes.tsv", "w") as o:
    o.write("utc\tera\tprocess\tfaulting_module\texception\n" + "\n".join(rows) + "\n")
with open(DIG / "winevents_digest.md", "w") as o:
    o.write("# Windows event digest, SteveDesktop, queried 2026-11-20 (System log reaches back only to 2026-10-31T18:02Z; Application to 2026-10-25T18:01Z)\n\n")
    c = collections.Counter((x["log"], x["provider"], x["id"]) for x in ev)
    o.write("## Counts by log/provider/id\n\n" + "\n".join("%d\t%s" % (v, k) for k, v in c.most_common()) + "\n\n")
    o.write("WHEA-Logger events: %d (any id).\n\n" % sum(1 for x in ev if "WHEA" in x["provider"]))
    o.write("## Unclean shutdowns and power events, whole\n\n")
    for x in ev:
        if x["id"] in ("41", "6008", "1001") and x["log"] == "System" or "WHEA" in x["provider"]:
            o.write("- %s %s %s %s\n" % (x["utc"], x["provider"], x["id"], x["msg"][:400]))
    o.write("\n## Application Error 1000 per day per process\n\n")
    for d in sorted(byday):
        o.write("- %s total=%d %s\n" % (d, sum(byday[d].values()), dict(byday[d].most_common())))
print("digests written to", DIG)
