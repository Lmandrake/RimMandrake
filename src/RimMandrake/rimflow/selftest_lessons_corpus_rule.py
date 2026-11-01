#!/usr/bin/env python3
"""Lessons are a corpus, not a queue (LESSONS_RETIRE_INBOX_AS_QUEUE, risk response T7, owner ruling D3(a) 2026-11-01).

The owner's 2026-10-29 answer "The Auditor once a week." made the Auditor fold 40 lessons a pass and carry the duty
until no lesson file was older than 14 days. Intake measured ~626 a week, so the queue could never drain. The ruling
retires it: the files stay as a searchable corpus, a lesson earns work only when its class recurs (findings fold,
the Auditor's repeat check, RO5; AU3 is the measure), and the Auditor's random slice runs first in each pass.

  L1 no role file, the dispatcher schedule or the operating requirements still states the fold quota, the 14-day
     inbox rule, the inbox count as a reading, or a lessons fold the Arbiter's pass waits on.
  L2 the Auditor role says lessons are a corpus, not owed work, and promotion goes through recurrence (RO5, AU3).
  L3 the Auditor role puts the random slice first, before the mandatory re-checks (step 2).
  L4 the lessons stay in the tree: lessons.py still reads infrastructure/state/lessons/ (no archive-out).
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
ROLES = os.path.join(HERE, "roles")
FAILS = []

# Phrases that state the retired queue as owed work. Each was a live line before the ruling landed.
RETIRED = [
    r"until 40 are folded",
    r"40[- ]a[- ]pass",
    r"40\s*/\s*week",
    r"no file older than 14 days",
    r"inbox count before and after",
    r"Lessons\s*(→|->|to)\s*skills",
    r"Monday lessons fold",
    r"lessons to skills",
]


def check(cond, msg):
    print(("PASS " if cond else "FAIL ") + msg)
    if not cond:
        FAILS.append(msg)


def read(path):
    with open(path, encoding="utf-8") as f:
        return f.read()


def main():
    targets = [os.path.join(ROLES, n) for n in sorted(os.listdir(ROLES)) if n.endswith(".md")]
    targets += [os.path.join(HERE, "dispatcher_schedule.json"),
                os.path.join(REPO, "design", "RimMandrake", "operating_requirements_2026-11-01.md")]
    check(len(targets) >= 4 and all(os.path.isfile(t) for t in targets),
          "L0 the instrument sees the role files, the schedule and the requirements (%d files)" % len(targets))
    hits = []
    for t in targets:
        for i, line in enumerate(read(t).splitlines(), 1):
            for pat in RETIRED:
                if re.search(pat, line, re.I):
                    hits.append("%s:%d %s" % (os.path.relpath(t, REPO), i, pat))
    check(not hits, "L1 no file states the retired lessons queue as owed work" + ("" if not hits else ": " + "; ".join(hits)))
    # Sanity probe: the same scan does see a planted line (a blind scan would pass L1 on anything).
    planted = "  last pass, then the oldest files until 40 are folded in all; carry until no file older than 14 days"
    check(any(re.search(p, planted, re.I) for p in RETIRED), "L1 probe: the scan flags a planted quota line")

    aud = read(os.path.join(ROLES, "auditor.md"))
    check(re.search(r"corpus, not a queue", aud) is not None and "RO5" in aud and "AU3" in aud
          and re.search(r"recur", aud) is not None,
          "L2 auditor.md: lessons are a corpus, promotion only on recurrence (RO5, AU3)")
    m = re.search(r"random slice runs first in each pass, before mandatory work", aud)
    step2 = aud.find("2. **Mandatory, every one:**")
    check(m is not None and 0 <= m.start() < step2,
          "L3 auditor.md: the random slice runs first, stated before the mandatory step 2")
    check(re.search(r"worked where they sit in that list", aud) is None,
          "L3 auditor.md: the random picks are no longer worked inside the ranked list")

    lp = read(os.path.join(REPO, "src", "RimMandrake", "Utils", "lessons.py"))
    check("infrastructure/state/lessons" in lp or "state\" / \"lessons" in lp or "'lessons'" in lp
          or '"lessons"' in lp, "L4 lessons.py still reads the lessons folder in the tree")
    print("selftest_lessons_corpus_rule: %s (%d fail)" % ("FAIL" if FAILS else "PASS", len(FAILS)))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
