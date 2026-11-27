#!/usr/bin/env python3
"""7-day figures of the two metronome units, for metronome_profile.md. Run on Archmagi:
    ssh mandrake@archmagi-wsl DAYS=7 python3 - < design/specs/2026-11-26-slow-actions/metronome_week.py
Reads (1) the user journal's `Consumed X CPU time over Y wall clock time` lines of rm-metronome and
rm-metronome-sense, (2) beats.jsonl's phase lines in the same window. Prints tables; writes nothing."""
import json, os, re, statistics as S, subprocess, time
from collections import defaultdict

DAYS = int(os.environ.get("DAYS", "7"))   # DAYS=4: only since sense ran apart (2026-11-22 10:27 PM)
since = time.time() - DAYS * 86400
J = subprocess.run(["journalctl", "--user", "--since", "%d days ago" % DAYS, "-o", "short-unix",
                    "-u", "rm-metronome.service", "-u", "rm-metronome-sense.service"],
                   capture_output=True, text=True).stdout.splitlines()


def dur(s):
    t = 0.0
    for v, u in re.findall(r"([\d.]+)(min|ms|us|s|h)", s):
        t += float(v) * {"h": 3600, "min": 60, "s": 1, "ms": 1e-3, "us": 1e-6}[u]
    return t


def q(xs, p):
    xs = sorted(xs)
    return xs[min(len(xs) - 1, int(p * len(xs)))] if xs else float("nan")


units = defaultdict(lambda: {"wall": [], "cpu": []})
for l in J:
    m = re.search(r"\]: (rm-metronome(?:-sense)?)\.service: Consumed (.*?) CPU time over (.*?) wall clock time", l)
    if m:
        units[m.group(1)]["cpu"].append(dur(m.group(2)))
        units[m.group(1)]["wall"].append(dur(m.group(3)))
print("journal lines read:", len(J))
print("unit | runs | wall median/p90/max s | CPU median/p90 s | wall h | CPU h")
for u, d in sorted(units.items()):
    w, c = d["wall"], d["cpu"]
    print("%s | %d | %.1f / %.1f / %.1f | %.2f / %.2f | %.1f | %.2f" % (
        u, len(w), S.median(w), q(w, .9), max(w), S.median(c), q(c, .9), sum(w) / 3600, sum(c) / 3600))

# beats.jsonl
B = "/mnt/d/ClaudeWork/rimmandrake/metronome/shadow/beats.jsonl"
ph = defaultdict(list)
exits = defaultdict(lambda: defaultdict(int))
beats = defaultdict(lambda: {"start": None, "end": None, "sum": 0.0})
fam_s = defaultdict(list)
n = 0
with open(B, encoding="utf-8", errors="replace") as f:
    for l in f:
        try:
            r = json.loads(l)
        except ValueError:
            continue
        st = r.get("start") or 0
        if st < since:
            continue
        n += 1
        key = ("apart:" if r.get("apart") else "") + str(r.get("phase"))
        s = r.get("seconds")
        exits[key][str(r.get("exit"))] += 1
        if isinstance(s, (int, float)) and r.get("exit") not in ("no_command", "deferred", "duplicate"):
            ph[key].append(s)
            if r.get("apart") and r.get("families"):
                fam_s[",".join(r["families"])].append(s)
        if not r.get("apart") and r.get("beat") is not None and isinstance(s, (int, float)):
            b = beats[r["beat"]]
            b["start"] = st if b["start"] is None else min(b["start"], st)
            b["end"] = max(b["end"] or 0, st + s)
            b["sum"] += s
print("\nbeats.jsonl lines in window:", n)
print("phase | runs | median / p90 / max s | total h | exits")
for k in sorted(ph):
    v = ph[k]
    print("%s | %d | %.2f / %.2f / %.2f | %.2f | %s" % (k, len(v), S.median(v), q(v, .9), max(v), sum(v) / 3600,
                                                      dict(exits[k])))
for k in sorted(set(exits) - set(ph)):
    print("%s | 0 timed | | | %s" % (k, dict(exits[k])))
spans = [b["end"] - b["start"] for b in beats.values() if b["start"]]
gaps = [b["end"] - b["start"] - b["sum"] for b in beats.values() if b["start"]]
print("\nbeats: %d; first phase start to last phase end median %.2f s p90 %.2f; of it between phases median %.3f s"
      % (len(spans), S.median(spans), q(spans, .9), S.median(gaps)))
print("\nsense families (apart), slowest median first:")
for k, v in sorted(fam_s.items(), key=lambda kv: -S.median(kv[1]))[:40]:
    print("  %-50s runs %4d median %.2f p90 %.2f max %.1f" % (k, len(v), S.median(v), q(v, .9), max(v)))
