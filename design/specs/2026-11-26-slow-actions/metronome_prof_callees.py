#!/usr/bin/env python3
"""The direct callees of one function in a cProfile file, by cumulative time, for metronome_profile.md:
python3 metronome_prof_callees.py <prof> <function name> [<file suffix>]"""
import pstats, sys
s = pstats.Stats(sys.argv[1])
fn, suf = sys.argv[2], (sys.argv[3] if len(sys.argv) > 3 else "")
for (f, ln, name), v in s.stats.items():
    if name == fn and f.endswith(suf):
        print("== %s:%d(%s) cum %.2f s" % (f.split("/")[-1], ln, name, v[3]))
        rows = []
        for callee, (cc, nc, tt, ct, callers) in s.stats.items():
            if (f, ln, name) in callers:
                c = callers[(f, ln, name)]
                rows.append((c[3], c[1], "%s:%d(%s)" % (callee[0].split("/")[-1], callee[1], callee[2])))
        for ct, nc, n in sorted(rows, reverse=True)[:18]:
            print("   %6.2f s cum %7d calls  %s" % (ct, nc, n))
