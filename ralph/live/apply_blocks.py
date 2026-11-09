#!/usr/bin/env python3
"""Apply SEARCH/REPLACE blocks from a GPT answer (round 4): python3 ralph/live/apply_blocks.py ANSWER.md [--dry]
Block: '<<<<<<< FILE path' / search / '=======' / replace / '>>>>>>>'. Each search must occur exactly once."""
import re, sys
t = open(sys.argv[1], encoding="utf-8").read()
dry = "--dry" in sys.argv
blocks = re.findall(r"<<<<<<< FILE (\S+)\n(.*?)\n=======\n(.*?)\n?>>>>>>>", t, re.S)
bad = 0
cache = {}
for f, a, b in blocks:
    s = cache.setdefault(f, open(f, encoding="utf-8").read())
    n = s.count(a)
    if n != 1:
        print("FAIL (%d matches) %s: %r" % (n, f, a[:80])); bad += 1; continue
    cache[f] = s.replace(a, b)
print("%d blocks, %d failed" % (len(blocks), bad))
if not dry and not bad:
    for f, s in cache.items():
        open(f, "w", encoding="utf-8", newline="").write(s)
    print("applied")
sys.exit(1 if bad else 0)
