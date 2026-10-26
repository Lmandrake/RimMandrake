#!/usr/bin/env python3
"""The eviction generator must refuse to write a patch that drops the shipped evictions."""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import biome_wildbiomes_evictions as g

fails = []
def check(name, cond):
    if not cond:
        fails.append(name)

check("0 vs 2018 refused", g.shrink_guard(0, 2018) is not None)
check("0 vs 2018 accepted with flag", g.shrink_guard(0, 2018, True) is None)
check("same count passes", g.shrink_guard(2018, 2018) is None)
check("small drift passes", g.shrink_guard(2000, 2018) is None)
check("big growth refused", g.shrink_guard(4000, 2018) is not None)
check("no shipped file passes", g.shrink_guard(0, None) is None)
n = g.shipped_op_count()
check("shipped file is counted (instrument sees)", n is not None and n > 100)
if fails:
    print("FAIL:", fails); sys.exit(1)
print("PASS selftest_biome_evictions_guard")
