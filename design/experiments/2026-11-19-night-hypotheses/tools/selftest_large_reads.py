#!/usr/bin/env python3
"""Planted sessions for large_reads.analyse. Exit 0 when all 4 pass. Seen red on 2026-11-19: before a 30-run had to
be unique within its read, case A read 400 of 400 lines used (a shared phrase matched every line)."""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "..", "..", "..", "src", "RimMandrake", "rimflow"))
import large_reads as L, role_launch as RL

lines = ["line number %03d says something quite distinctive about topic %d here" % (i, i) for i in range(400)]
lines[10] = "def compute_widget_total(alpha):  # short"
text = "\n".join("%6d\t%s" % (i + 1, l) for i, l in enumerate(lines))
u = {"cache_creation_input_tokens": 9000, "cache_read_input_tokens": 1000, "input_tokens": 5}


def run(after, before=()):
    ev = [("in", "brief"), ("req", "claude-opus-5-5", u)] + [("out", o) for o in before] + [
        ("read", dict(path="/x/design/a.md", partial=False, text=text, chars=len(text))),
        ("req", "claude-opus-5-5", u)] + [("out", o) for o in after] + [("req", "claude-opus-5-5", u)]
    return L.analyse(ev, "brief", 20000, RL)[0][0]["used_lines"]


cases = [("quote of line 5 and a new name from line 11", run(["old_string: line number 005 says something quite "
                                                              "distinctive about topic 5", "I will call compute_widget_total"]), 2),
         ("quote made only before the read", run([], ["line number 007 says something quite distinctive about topic 7 here"]), 0),
         ("name already seen before the read", run(["compute_widget_total again"], ["compute_widget_total first"]), 0),
         ("nothing later", run(["ok"]), 0)]
bad = [(n, got, want) for n, got, want in cases if got != want]
for n, got, want in cases:
    print("%-4s %s: %d used lines (want %d)" % ("ok" if got == want else "FAIL", n, got, want))
print("VERDICT %s: %d of %d" % ("PASS" if not bad else "FAIL", len(cases) - len(bad), len(cases)))
sys.exit(1 if bad else 0)
