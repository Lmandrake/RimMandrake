#!/usr/bin/env python3
"""Apply '<<<<<<< SEARCH / ======= / >>>>>>> REPLACE' blocks: apply_sr.py ANSWER.md FILE. Each search must match once."""
import re, sys
t = open(sys.argv[1], encoding="utf-8").read(); f = sys.argv[2]
s = open(f, encoding="utf-8", newline="").read(); crlf = "\r\n" in s; s = s.replace("\r\n", "\n")
bl = re.findall(r"<<<<<<< SEARCH\n(.*?)\n=======\n(.*?)\n>>>>>>> REPLACE", t, re.S)
for a, b in bl:
    n = s.count(a)
    if n != 1: sys.exit("FAIL %d matches: %r" % (n, a[:80]))
    s = s.replace(a, b)
if crlf: s = s.replace("\n", "\r\n")
open(f, "w", encoding="utf-8", newline="").write(s); print(len(bl), "applied")
