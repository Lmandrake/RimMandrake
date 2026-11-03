#!/usr/bin/env python3
"""selftest_landmark_rename_save.py - the offline landmark rename and its check, on a synthetic save.

Proves: the reader pairs keys with values in order and unescapes names; a stale row (wrong old name,
wrong def) refuses the whole run; apply changes only the named <name> text, escapes it, and is
idempotent; check_text sees a duplicate and a missing Gaping Doom. LANDMARK_NAMING_PASS_1.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import landmark_rename_save as R  # noqa: E402
import landmark_names_check as C  # noqa: E402

SAVE = """<savegame><world><landmarks>
\t<landmarks>
\t\t<keys>
\t\t\t<li>2403,0</li>
\t\t\t<li>10,0</li>
\t\t\t<li>11,0</li>
\t\t</keys>
\t\t<values>
\t\t\t<li>
\t\t\t\t<def>RUT_GapingDoom</def>
\t\t\t\t<name>Asonistia City</name>
\t\t\t</li>
\t\t\t<li>
\t\t\t\t<def>Cavern</def>
\t\t\t\t<name>Earl's Caves &amp; Co</name>
\t\t\t</li>
\t\t\t<li>
\t\t\t\t<def>Cavern</def>
\t\t\t\t<name>Earl's Caves &amp; Co</name>
\t\t\t</li>
\t\t</values>
\t</landmarks>
</landmarks></world></savegame>
"""
RENAMES = [{"tile": 2403, "def": "RUT_GapingDoom", "old": "Asonistia City", "new": "The Gaping Doom"},
           {"tile": 11, "def": "Cavern", "old": "Earl's Caves & Co", "new": "Mould & Spore"}]
fails = []


def ok(cond, what):
    if not cond:
        fails.append(what)


ok(R._xml_text("&#65;&quot;&apos;") == "A\"'", "numeric and quote references decode")
two = SAVE.replace("<li>10,0</li>", "<li>2403,1</li>").replace("<def>Cavern</def>\n\t\t\t\t<name>Earl", "<def>RUT_GapingDoom</def>\n\t\t\t\t<name>Earl", 1)
f, _ = C.check_text(two.replace("Asonistia City", "The Gaping Doom"), [])
ok(any("2403" in x for x in f), "a second Gaping Doom on another layer fails the check")
rows = R.read_landmarks(SAVE)
ok([(r["tile"], r["def"], r["name"]) for r in rows] ==
   [(2403, "RUT_GapingDoom", "Asonistia City"), (10, "Cavern", "Earl's Caves & Co"),
    (11, "Cavern", "Earl's Caves & Co")], "reader pairs keys/values and unescapes")
f, n = C.check_text(SAVE, RENAMES)
ok(n == 3 and any("held by 2" in x for x in f) and any("2403" in x for x in f), "check sees dup and Doom")
for bad in ({"old": "Nope"}, {"def": "Ruins"}, {"tile": 99}, {"new": "X\u0000Y"}, {"new": " "}):
    row = dict(RENAMES[1], **bad)
    try:
        R.plan(SAVE, [RENAMES[0], row])
        ok(False, f"stale row {bad} must refuse")
    except ValueError:
        pass
new = R.apply(SAVE, R.plan(SAVE, RENAMES))
ok("<name>Mould &amp; Spore</name>" in new, "new name escaped")
diff = [(a, b) for a, b in zip(SAVE.splitlines(), new.splitlines()) if a != b]
ok(len(diff) == 2 and len(SAVE.splitlines()) == len(new.splitlines()), "only two lines change")
ok(R.plan(new, RENAMES) == [], "idempotent: nothing left to do")
f, n = C.check_text(new, RENAMES)
ok(f == [], f"check passes after apply: {f}")
import json, tempfile  # noqa: E401,E402
with tempfile.TemporaryDirectory() as d:
    good, stale, js = (os.path.join(d, n) for n in ("good.rws", "stale.rws", "r.json"))
    open(good, "w").write(SAVE)
    open(stale, "w").write(SAVE.replace("Asonistia City", "Changed"))
    json.dump({"renames": RENAMES}, open(js, "w"))
    rc = R.main(["--renames", js, "--save", good, "--save", stale, "--apply", "--tag", "t"])
    ok(rc == 2 and open(good).read() == SAVE and not os.path.exists(good + ".bak-pre-t"),
       "a stale second save refuses the run before the first is written")
    rc = R.main(["--renames", js, "--save", good, "--apply", "--tag", "t"])
    ok(rc == 0 and C.check_text(open(good).read(), RENAMES)[0] == [] and open(good + ".bak-pre-t").read() == SAVE,
       "apply writes the save and a byte-exact backup")
try:
    R.read_landmarks(SAVE.replace("<name>Asonistia City</name>", "<!--<name>Asonistia City</name>--><name>X</name>"))
    ok(False, "a comment inside a value must refuse")
except ValueError:
    pass
print("FAIL: " + "; ".join(fails) if fails else "PASS selftest_landmark_rename_save")
sys.exit(1 if fails else 0)
