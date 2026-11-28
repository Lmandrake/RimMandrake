#!/usr/bin/env python3
"""selftest_scratch_reap_unit_priority.py: the hourly expiry is never starved to a 3 h silence by CPU load
(OPS_SCRATCH_EXPIRY_RESTORE_YAQA, third outage, 2026-11-28).

The failure (Archmagi, 2026-11-27 8:00 PM PST on): rm-scratch-reap.service ran 1.5 h and counting. Its borrower `find`
had 44 s of CPU and 242 s waiting in the run queue (/proc/<pid>/schedstat) at load 38 on 14 CPUs. The unit ran at
Nice=19 beside the other services of app.slice, so every one of them outranked it. Last clean run 6:01 PM, so
disk.scratch_ok_age_h passed its 3 h line. The expiry is the root disk's backstop; it may be slow, not starved.

Proves, on the repo copy of the unit and on the installed copy when one exists:
(1) the unit sets Nice no higher than 5 (Nice=19 weighs 15 against 1024 at Nice=0);
(2) the installed unit, when present, carries the same Nice as the repo copy."""
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
F = []


def ck(c, w):
    print(("PASS " if c else "FAIL ") + w)
    if not c:
        F.append(w)


def nice(p: Path):
    m = re.search(r"^Nice=(-?\d+)\s*$", p.read_text(), re.M)
    return int(m.group(1)) if m else 0


repo = HERE / "systemd" / "rm-scratch-reap.service"
n = nice(repo)
ck(n <= 5, f"(1) repo unit Nice={n}, at most 5")
inst = Path.home() / ".config/systemd/user/rm-scratch-reap.service"
if inst.exists():
    ck(nice(inst) == n, f"(2) installed unit Nice={nice(inst)} equals the repo copy's {n}")
sys.exit(1 if F else 0)
