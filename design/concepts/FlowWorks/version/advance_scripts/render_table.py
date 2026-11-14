#!/usr/bin/env python3
"""Throwaway (FlowWorks Stage 3 reconcile, 2026-11-14): recompute each bar's derived fields (proves_at, offline_green_today,
runnable today, held) from version/test_table.json and rewrite it and its read view test_table.md. The read-view code is
make_table.py's, unchanged; the derivation is make_table.py's lines 247-266."""
import json, os, datetime
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), *[".."] * 5))
os.chdir(ROOT)
C = "design/concepts/FlowWorks"
P = C + "/version/test_table.json"
table = json.load(open(P))
tests, bars, held = table["tests"], table["bars"], table["held_statements"]
ORDER = {"2": 0, "4-5": 1, "6": 2, "8": 3}
def runnable(t):
    r = t["runs_today"]
    return bool(r.get("ran")) or bool(r.get("entry_exists"))
def ok_today(t):
    r = t["runs_today"]
    return bool(r.get("ran")) and r.get("rc") == 0
for b in bars:
    dec, sup = b["decides"], b["supports"]
    offd = [t for t in dec if tests[t]["kind"] == "offline"]
    b.update({"proves_at": max((tests[t]["stage"] for t in dec), key=lambda s: ORDER[s]) if dec else None,
              "offline_decides": offd, "offline_green_today": bool(offd) and all(ok_today(tests[t]) for t in offd),
              "every_decider_runnable_today": bool(dec) and all(runnable(tests[t]) for t in dec),
              "any_test_runnable_today": any(runnable(tests[t]) for t in dec + sup if t in tests), "held": []})
bix = {b["id"]: b for b in bars}
for h in held:
    for x in h["bars"]:
        bix[x]["held"].append("%s#%s" % (h["tag"], h["row"]))
table["made"] = datetime.datetime.now().astimezone().isoformat(timespec="seconds")
json.dump(table, open(P, "w"), indent=1)
# ---------------------------------------------------------------- read view
def runs_word(b):
    return "all" if b["every_decider_runnable_today"] else ("some" if b["any_test_runnable_today"] else "none")
offl = [t for t in tests.values() if t["kind"] == "offline"]
offl_built = [t for t in offl if t["file"].startswith("src/")]
ran_ok = [t for t in offl_built if t["runs_today"].get("ran") and t["runs_today"].get("rc") == 0]
ran_red = [t for t in offl_built if t["runs_today"].get("ran") and t["runs_today"].get("rc") != 0]
live = [t for t in tests.values() if t["kind"].startswith("live")]
cnt = {
 "bars": len(bars),
 "with at least one test runnable today (an offline test that ran, or an in-game scene whose entry exists)": sum(b["any_test_runnable_today"] for b in bars),
 "with every deciding test runnable today": sum(b["every_decider_runnable_today"] for b in bars),
 "with an offline deciding test, all green today": sum(b["offline_green_today"] for b in bars),
 "with an offline deciding test that exists (built), green or red": sum(1 for b in bars if any(tests[t]["file"].startswith("src/") for t in b["offline_decides"])),
 "with no offline deciding test at all": sum(1 for b in bars if not b["offline_decides"]),
 "decided offline only (no game needed)": sum(1 for b in bars if b["decides"] and all(tests[t]["kind"] == "offline" for t in b["decides"])),
}
L = ["# FlowWorks 0.1.0: test-and-stage table", "",
     "Generated %s from `test_table.json` (the record; this is its read view). Stages: 2 preflight, 4-5 blind offline, 6 in-game, 8 his walk. A bar passes when every deciding test passes. Columns match Explosive Knockback's table." % table["made"], "",
     "## Counts (measured)", ""]
L += ["- %s: %d" % kv for kv in cnt.items()]
L += ["- in-game scenes: %d, entry exists %d, absent %d" % (len(live), sum(1 for t in live if t["runs_today"].get("entry_exists")), sum(1 for t in live if not t["runs_today"].get("entry_exists"))),
      "- offline tests: %d built (ran today: %d PASS, %d red), %d specified for Stage 3" % (len(offl_built), len(ran_ok), len(ran_red), len(offl) - len(offl_built)), "",
      "## Bars", "", "| bar | from | proves at | decides | supports | runnable today | offline green |", "|---|---|---|---|---|---|---|"]
for b in bars:
    L.append("| `%s` | %s | %s | %s | %s | %s | %s |" % (b["id"], b["source"].split(".")[0], b["proves_at"], ", ".join(b["decides"]) or "-",
             ", ".join(b["supports"]) or "-", runs_word(b), "yes" if b["offline_green_today"] else "no"))
L += ["", "## Tests", "", "| test | kind | stage | file | runs today |", "|---|---|---|---|---|"]
for k, t in tests.items():
    r = t["runs_today"]
    if r.get("ran"):
        rw = ("PASS" if r.get("rc") == 0 else "RED rc %s" % r.get("rc")) + (" (%s/%s cases ok)" % (r["ok"], r["cases"]) if "cases" in r else "") + (", %ss" % r["seconds"] if r.get("seconds") is not None else "")
    elif "entry_exists" in r:
        rw = "not run (offline only); entry %s" % ("exists" if r["entry_exists"] else "ABSENT")
    else:
        rw = "not run: " + r.get("why", "")
    L.append("| `%s` | %s | %s | `%s` | %s |" % (k, t["kind"], t["stage"], t["file"], rw))
L += ["", "## Held look statements placed (%d rows)" % len(held), "", "| row | bars | test | stage | kind |", "|---|---|---|---|---|"]
for h in held:
    L.append("| %s#%s | %s | %s | %s | %s |" % (h["tag"], h["row"], ", ".join(h["bars"]) or "-", h["test"].replace("|", "/"), h["stage"], h["kind"]))
L += ["", "## Judge corrections", "", table["corrections_note"] + ".", "", "## The settings sweep, moved offline", "", table["settings_move"], ""]
open(C + "/version/test_table.md", "w").write("\n".join(L))
print("\n".join(L[4:16]))
