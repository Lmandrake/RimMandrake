#!/usr/bin/env python3
"""Which limit fired for each kernel OOM kill, and what died (HARNESS_OOM_MEASURE_NINETEEN_QUIET_KILLS).

memwatch reports `oom_kill +1 in rm-harness.slice` because cgroup v2 counters are hierarchical and a
short test's scope is gone before the next one-minute sample. That reads as the slice running out; the
kernel line names the cgroup whose limit really fired (oom_memcg=). This tool reads those lines.

  oom_attribution.py                    read the kernel and user journals of this boot
  oom_attribution.py --since 2026-11-03 same, from a date
  oom_attribution.py --extract OUT      also write the lines it used to OUT (journals decay; an extract does not)
  oom_attribution.py --kern FILE        classify a saved extract

Classes, by the cgroup that hit its limit:
  planted_fixture  a harness scope whose Started line names bomb.py: selftest_run_selftests.py proves the cap works
  harness_test     any other per-test scope in rm-harness.slice
  seat_tool_tmpfs  a seat's claude-code-bash cap, more than half of it shmem (files in a tmpfs /tmp)
  seat_tool_anon   a seat's claude-code-bash cap, mostly anonymous memory (a process grew)
  seat_other       a seat scope's own cap
  SLICE            a slice's own limit: rm-harness.slice or claude-seats.slice (the budget question)
  HOST             no memcg constraint: the whole VM ran out

Exit: 0 classified; 2 no kill line was found, which means UNMEASURED and never "no kills".
"""
import argparse
import collections
import re
import subprocess
import sys

KILL_RE = re.compile(r"oom-kill:constraint=(?P<constraint>\w+).*?(?:oom_memcg=(?P<memcg>[^,]*),)?task_memcg=(?P<task_memcg>[^,]*),task=(?P<task>[^,]*),pid=(?P<pid>\d+)")
LIMIT_RE = re.compile(r"memory: usage (\d+)kB, limit (\d+)kB")
STAT_RE = re.compile(r"kernel: (anon|shmem) (\d+)\s*$")
KILLED_RE = re.compile(r"Killed process (\d+) \(([^)]*)\).*?anon-rss:(\d+)kB, file-rss:(\d+)kB, shmem-rss:(\d+)kB")
STARTED_RE = re.compile(r"Started (rm-harness-\d+-\d+\.scope)\b(.*)")
KEEP = ("oom-kill:", "memory: usage", "Killed process")
SEAT_RE = re.compile(r"(?:^|/)(claude-seat-[^/]+)\.scope")
SLICES = ("rm-harness.slice", "claude-seats.slice")


def classify(kill, bombs):
    """Pure. kill: dict with constraint, memcg, usage_kb, shmem, anon. bombs: harness scope names seen running bomb.py."""
    if kill.get("constraint") != "CONSTRAINT_MEMCG" or not kill.get("memcg"):
        return "HOST"
    tail = kill["memcg"].rstrip("/").rsplit("/", 1)[-1]
    if tail in SLICES:
        return "SLICE"
    if tail.startswith("rm-harness-"):
        return "planted_fixture" if tail in bombs else "harness_test"
    if tail == "claude-code-bash":
        return "seat_tool_tmpfs" if kill.get("shmem", 0) > kill.get("usage_kb", 0) * 1024 / 2 else "seat_tool_anon"
    if tail.startswith("claude-seat-"):
        return "seat_other"
    return "other:" + tail


def parse(lines):
    """Pure. Journal lines -> (kills, bombs). A kill takes the limit and stat lines printed just before it."""
    kills, bombs, limit, stat = [], set(), None, {}
    for ln in lines:
        s = STARTED_RE.search(ln)
        if s:
            if "bomb.py" in s.group(2):
                bombs.add(s.group(1))
            continue
        m = LIMIT_RE.search(ln)
        if m and "swap" not in ln:
            limit, stat = (int(m.group(1)), int(m.group(2))), {}
            continue
        m = STAT_RE.search(ln)
        if m and limit and m.group(1) not in stat:
            stat[m.group(1)] = int(m.group(2))
            continue
        m = KILL_RE.search(ln)
        if m:
            kills.append({"at": ln[:19], "constraint": m.group("constraint"), "memcg": m.group("memcg"),
                          "task": m.group("task"), "pid": int(m.group("pid")),
                          "usage_kb": limit[0] if limit else None, "limit_kb": limit[1] if limit else None,
                          "anon": stat.get("anon", 0), "shmem": stat.get("shmem", 0)})
            limit, stat = None, {}
            continue
        m = KILLED_RE.search(ln)
        if m and kills and kills[-1]["pid"] == int(m.group(1)):
            kills[-1]["rss_anon_kb"] = int(m.group(3))
    for k in kills:
        k["class"] = classify(k, bombs)
    return kills, bombs


def keep_line(ln):
    """Pure. The lines an extract must hold: kills, limits, the anon/shmem stat rows, a harness scope starting."""
    return any(x in ln for x in KEEP) or bool(STAT_RE.search(ln)) or ("Started rm-harness-" in ln and "bomb.py" in ln)


def journal(args, since):
    cmd = ["journalctl", "--no-pager", "-o", "short-iso"] + args + (["--since", since] if since else ["-b"])
    return subprocess.run(cmd, capture_output=True, text=True, errors="replace", timeout=120).stdout.splitlines()


def report(kills):
    """Pure. Printable lines; the SLICE and HOST counts are always named, zero included."""
    out = []
    for k in kills:
        seat = SEAT_RE.search(k["memcg"] or "")
        where = seat.group(1).replace("claude-seat-BENCH-", "") if seat else (k["memcg"] or "(whole host)").rsplit("/", 1)[-1]
        out.append("%s  %-16s limit=%s MB  anon=%d MB shmem=%d MB  killed %s  in %s" % (
            k["at"], k["class"], (k["limit_kb"] or 0) // 1024, k["anon"] >> 20, k["shmem"] >> 20, k["task"], where))
    n = collections.Counter(k["class"] for k in kills)
    out.append("kills: %d  " % len(kills) + "  ".join("%s=%d" % kv for kv in sorted(n.items())))
    out.append("slice-limit kills: %d  whole-host kills: %d" % (n["SLICE"], n["HOST"]))
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--kern", help="classify this saved extract instead of the journals")
    ap.add_argument("--since", help="journal start (default: this boot)")
    ap.add_argument("--extract", help="write the lines used to this file")
    a = ap.parse_args(argv)
    if a.kern:
        with open(a.kern, errors="replace") as f:
            lines = f.read().splitlines()
    else:
        lines = journal(["-k"], a.since) + journal(["--user"], a.since)
    if a.extract:
        with open(a.extract, "w") as f:
            f.writelines(ln + "\n" for ln in lines if keep_line(ln))
    kills, _ = parse(lines)
    if not kills:
        print("UNMEASURED: no oom-kill line in the input; this does not say there were no kills", file=sys.stderr)
        return 2
    print("\n".join(report(kills)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
