#!/usr/bin/env python3
"""tick_peak_accept.py: does the live Dispatch tick stay off its 1G memory limit, launching ticks included?
The outcome check of RIMMANDRAKE_SLIM_TICK_MEMORY_PAGE_BUILD_HITS_ONE_GIG_TICK_TOOK_FIVE_MIN. Reads the user journal of
rm-maturation-dispatch.service (systemd's own "Consumed" line per tick, and the tick's "launched N" line).

Holds (exit 0) when, over the last LOOK:
  - each of the newest LAUNCHES ticks that launched a helper run (one that takes a clone) peaked under LAUNCH_MB, and
  - none of the newest RECENT ticks reached LIMIT_MB, and
  - the median wall of those RECENT ticks is under WALL_S.
Exit 1: one of them does not hold. Exit 2: the journal could not be read, or holds too few ticks to say.
A certificate rerun is no helper launch: it takes its clone in its own unit (cert_rerun_unit)."""
import re
import statistics
import subprocess
import sys

UNIT = "rm-maturation-dispatch.service"
LOOK = "-24h"
LAUNCHES, LAUNCH_MB = 3, 900.0      # 2026-11-23/24: 9 of 11 launching ticks peaked at 1024 MB
RECENT, LIMIT_MB, WALL_S = 20, 1000.0, 120.0
CONSUMED = re.compile(r"^(\S+) .*Consumed .* CPU time over (.+?) wall clock time, (\S+) memory peak")
SPAN = {"d": 86400, "h": 3600, "min": 60, "s": 1, "ms": .001}


def mb(text):
    m = re.match(r"^([0-9.]+)([BKMGT])?$", text)
    return float(m.group(1)) * {"B": 1 / 1048576, "K": 1 / 1024, "M": 1, "G": 1024, "T": 1048576, None: 1 / 1048576}[m.group(2)]


def secs(text):
    return sum(float(n) * SPAN[u] for n, u in re.findall(r"([0-9.]+)(min|ms|d|h|s)", text))


def ticks(journal):
    """-> [(when, peak MB, wall s, took a helper's clone)] oldest first, one per tick whose Consumed line is there."""
    out, launched = [], False
    for ln in journal.splitlines():
        if ": Starting %s" % UNIT in ln:
            launched = False
        if re.search(r"\slaunch\s+launched\s", ln) and "rm-detached-" in ln:
            launched = True
        m = CONSUMED.match(ln)
        if m and UNIT in ln:
            out.append((m.group(1), mb(m.group(3)), secs(m.group(2)), launched))
            launched = False
    return out


def verdict(rows):
    """-> (exit code, [lines])."""
    launch, recent = [r for r in rows if r[3]][-LAUNCHES:], rows[-RECENT:]
    if len(launch) < LAUNCHES or len(recent) < RECENT:
        return 2, ["COULD NOT LOOK: %d launching ticks of %d wanted, %d ticks of %d" % (len(launch), LAUNCHES, len(recent), RECENT)]
    bad = ["launching tick %s peaked at %.0f MB (wall %.0f s)" % r[:3] for r in launch if r[1] >= LAUNCH_MB]
    bad += ["tick %s reached %.0f MB (wall %.0f s)" % r[:3] for r in recent if r[1] >= LIMIT_MB]
    med = statistics.median(r[2] for r in recent)
    if med >= WALL_S:
        bad.append("median wall of the newest %d ticks is %.0f s" % (RECENT, med))
    if bad:
        return 1, bad
    return 0, ["HOLDS: newest %d launching ticks %s MB; newest %d ticks peak %.0f MB at most, median wall %.0f s" % (
        LAUNCHES, ", ".join("%.0f" % r[1] for r in launch), RECENT, max(r[1] for r in recent), med)]


def main():
    try:
        r = subprocess.run(["journalctl", "--user", "-u", UNIT, "--since", LOOK, "--no-pager", "-o", "short-iso"],
                           capture_output=True, text=True, timeout=120, stdin=subprocess.DEVNULL, errors="replace")
    except (OSError, subprocess.SubprocessError) as e:
        print("COULD NOT LOOK: %s" % e)
        return 2
    if r.returncode:
        print("COULD NOT LOOK: journalctl exit %d: %s" % (r.returncode, r.stderr.strip()))
        return 2
    code, lines = verdict(ticks(r.stdout))
    print("\n".join(lines))
    return code


if __name__ == "__main__":
    sys.exit(main())
