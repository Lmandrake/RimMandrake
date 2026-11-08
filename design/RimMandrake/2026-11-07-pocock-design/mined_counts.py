"""Counts for a mined live-bug census (06-mined-live-bugs.md): python3 mined_counts.py [06-mined-live-bugs.tsv]

Columns: id mod fix symptom loc(CALLER|KERNEL|XML|HARNESS) class(WIRING|DESIGN) ev(L = the record names the live sighting,
I = fixed in a live pass, sighting not written) catch(yes|partly|no: a scenario at the fix's location could have caught it
before play, had someone written it) scenario cost."""
import collections
import csv
import os
import sys

path = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(os.path.abspath(__file__)), "06-mined-live-bugs.tsv")
rows = list(csv.DictReader(open(path), delimiter="\t"))
bad = [r["id"] for r in rows if None in r.values() or len(r) != 10]
if bad:
    sys.exit("malformed rows: %s" % bad)


def tally(sel, key):
    return dict(sorted(collections.Counter(r[key] for r in sel).items()))


for label, sel in (("all", rows), ("live sighting written (L)", [r for r in rows if r["ev"] == "L"])):
    print("%s: %d" % (label, len(sel)))
    for k in ("mod", "loc", "class", "catch"):
        print("  by %-5s %s" % (k, tally(sel, k)))
    c = [r for r in sel if r["loc"] == "CALLER"]
    print("  CALLER: %d (%d%%); CALLER and WIRING: %d; CALLER, WIRING, catch=yes: %d" % (
        len(c), round(100 * len(c) / max(1, len(sel))), sum(r["class"] == "WIRING" for r in c),
        sum(r["class"] == "WIRING" and r["catch"] == "yes" for r in c)))
