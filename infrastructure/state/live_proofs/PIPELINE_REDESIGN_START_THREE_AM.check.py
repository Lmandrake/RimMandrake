#!/usr/bin/env python3
"""Was the owner's 03:00 PST 2026-11-06 pipeline redesign order carried out? Reads the run's own dated outputs.

usage: PIPELINE_REDESIGN_START_THREE_AM.check.py <redesign folder>
Exits 0 when the run started and went through its stages, 1 naming the first thing that does not hold.
The real start was 03:13 PST, 13 minutes late; the window below admits that and says so rather than claiming 03:00.
"""
import calendar
import os
import subprocess
import sys


def utc(hour, minute):
    return calendar.timegm((2026, 11, 6, hour, minute, 0))


START = utc(11, 0)                          # 03:00 PST, the owner's deadline
OUTPUTS = {                                 # stage output -> latest plausible write
    "stage0b_capture.md": utc(11, 45),
    "stage1_skeptical.md": utc(12, 0),
    "stage1_consolidation.md": utc(12, 0),
    "stage1_upgrade.md": utc(12, 0),
    "redesign.md": utc(13, 0),
    "gpt_review.md": utc(13, 0),
    "redesign_final.md": utc(13, 0),
}
LANDED = ("8c4317ede215", "ab77ccbdd679", "91579b440026", "df415f2e9e27",
          "d05b6069efcb", "41e6e23816e1", "0cb114132456")    # stage 4 packages, named in stage4_log.md


def problems(folder):
    for name, latest in OUTPUTS.items():
        path = os.path.join(folder, name)
        if not os.path.isfile(path):
            yield "missing stage output %s" % path
        elif os.path.getsize(path) < 1000:
            yield "stage output too small to be the stage's work: %s" % path
        elif not START <= os.path.getmtime(path) <= latest:
            yield "%s written outside its window (mtime %d, window %d..%d)" % (name, os.path.getmtime(path), START, latest)
    try:
        with open(os.path.join(folder, "PLAN.md"), encoding="utf-8") as f:
            plan = f.read()
        with open(os.path.join(folder, "stage4_log.md"), encoding="utf-8") as f:
            log = f.read()
    except OSError as e:
        yield "unreadable: %s" % e
        return
    for words in ("started 2026-11-06 03:13 PST", "stage 4 waves A-D LANDED"):
        if words not in plan:
            yield "PLAN.md STATE does not say %r" % words
    for sha in LANDED:
        if sha not in log:
            yield "stage4_log.md does not name %s" % sha
        r = subprocess.run(["git", "log", "-1", "--format=%ct", sha], capture_output=True, text=True)
        if r.returncode or not r.stdout.strip():
            yield "commit %s is not in the history: %s" % (sha, r.stderr.strip()[:120])
        elif not START <= int(r.stdout) <= utc(15, 30):
            yield "commit %s is dated outside the run" % sha


def main():
    if len(sys.argv) != 2:
        print(__doc__)
        return 2
    bad = list(problems(sys.argv[1]))
    for line in bad:
        print("FAIL", line)
    if not bad:
        print("PASS redesign run started and carried through: %d dated stage outputs, %d stage-4 commits in history"
              % (len(OUTPUTS), len(LANDED)))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
