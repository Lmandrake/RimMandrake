#!/usr/bin/env python3
"""selftest_clone_mem_probe.py — clone_mem_probe.verdict(), the judge behind `clone_mem_probe.py --check`
(RELENTLESS_TICK_MEASURE_CLONE_MEMORY_PEAK). No clone is made: records are synthetic.

Proves: a page-cache peak held by git HOLDS; an anon-heavy peak, or a python top holder, or a non-git top holder is
CHANGED; too few samples or too small a peak is UNMEASURED (None), never a pass.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import clone_mem_probe as m  # noqa: E402

GB = 2**30


def rec(anon, file, top, samples=500, peak=None):
    cur = anon + file
    return {"samples": samples, "memory_peak": peak if peak is not None else cur, "peak_current": cur,
            "at_peak": {"anon": anon, "file": file, "t": 9.0}, "max_anon": anon, "top_rss": top,
            "mem_available_start": 14 * GB, "mem_available_min": 13 * GB, "mem_available_end": 14 * GB,
            "wall_s": 13.0, "rc": 0}


def main() -> int:
    cases = [
        ("page cache, git read-tree", rec(0.2 * GB, 3.0 * GB, {"git read-tree": 0.2 * GB, "python scratch_clone.py": 0.02 * GB}), True),
        ("anon-heavy", rec(2.0 * GB, 1.0 * GB, {"git read-tree": 2.0 * GB}), False),
        ("python holds anon", rec(0.2 * GB, 3.0 * GB, {"python scratch_clone.py": 0.3 * GB, "git read-tree": 0.1 * GB}), False),
        ("non-git holder", rec(0.2 * GB, 3.0 * GB, {"rsync": 0.3 * GB}), False),
        ("too few samples", rec(0.2 * GB, 3.0 * GB, {"git read-tree": 0.2 * GB}, samples=3), None),
        ("peak too small", rec(0.01 * GB, 0.05 * GB, {"git read-tree": 0.01 * GB}), None),
        ("no processes seen", rec(0.2 * GB, 3.0 * GB, {}), False),
    ]
    bad = 0
    for name, r, want in cases:
        got, line = m.verdict(r)
        ok = got is want
        bad += not ok
        print("%s %s: want %s got %s" % ("PASS" if ok else "FAIL", name, want, got))
    print("RESULT: %s" % ("PASS" if not bad else "FAIL (%d)" % bad))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
