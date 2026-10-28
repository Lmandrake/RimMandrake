#!/usr/bin/env python3
"""CAST_ROSTERS_RESTORE_CUT_XENOTYPE_RACES: cast_to_xml.py must refuse a cast note whose race is a cut xenotype,
its cut list must equal the defcut selftest's, and no design/Jawa/bridge cast note may name one. Offline."""
import os, re, sys, tempfile, importlib.util
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
import cast_to_xml as c

def load(path):
    sp = importlib.util.spec_from_file_location("m", path); m = importlib.util.module_from_spec(sp); sp.loader.exec_module(m); return m

fails = []
def check(n, ok, d=""):
    print("%s  %s %s" % ("ok  " if ok else "FAIL", n, "" if ok else d))
    if not ok: fails.append(n)

defcut = load(os.path.join(ROOT, "src", "RimUtinni", "UtinniPatches", "selftest_xenotype_defcut.py"))
check("cut list equals defcut CUT", set(getattr(c, "CUT_XENOTYPES", ())) == set(defcut.CUT))

note = "**Test Person** · Hussar · f · 31\n`traits: Brawler`\nchildhood: x\nadult: y\n> hook\n"
with tempfile.TemporaryDirectory() as d:
    f = os.path.join(d, "INHABITED_CAST_X.md"); open(f, "w").write("## PLACE\n\n" + note)
    probs = []
    c.parse_file(f, "X", {}, {}, probs)
    check("generator flags a cut race", any("CUT xenotype" in p for p in probs), str(probs))
    open(f, "w").write("## PLACE\n\n" + note.replace("Hussar", "Echani"))
    probs = []
    c.parse_file(f, "X", {}, {}, probs)
    check("generator accepts a surviving race", not any("CUT xenotype" in p for p in probs), str(probs))

bad = []
bdir = os.path.join(ROOT, "design", "Jawa", "bridge")
for fn in sorted(os.listdir(bdir)):
    if fn.startswith("INHABITED_CAST_") and fn.endswith(".md"):
        for i, l in enumerate(open(os.path.join(bdir, fn), encoding="utf-8"), 1):
            m = c.ENTRY_RE.match(l.rstrip("\n"))
            if m and m.group("race").strip() in defcut.CUT: bad.append("%s:%d" % (fn, i))
check("no cast note names a cut race", not bad, str(bad))
print("FAILED" if fails else "ok"); sys.exit(1 if fails else 0)
