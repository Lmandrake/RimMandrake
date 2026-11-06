#!/usr/bin/env python3
"""selftest_relentless_exam_outcome.py - EXAM_SETTER_FIX_DEMANDS_ITS_OWN_MECHANISM.

Judged 2026-11-06: of 18 shadow exam reds on done items, REAL 2, EXAM_WRONG 16. The Setter (1) pinned a mechanism of its
own choosing (relentless_envcause classifying the cause lane-fixable) where the item asked only that the cause stop
stopping live proofs, (2) read a wrapper's trailing line after 'RESULT PASS: 0 failed' as red (CHECKER_REACH_FIX_SEEDS_
STILL_DARK), (3) built fixtures that were not the recorded incident (GAMEENV_FIX_HARNESS_09849AF1_ITEMS_WAIT ...).
Each shape is replayed here from the judged exam's own words and must be REFUSED by validate(); the outcome-shaped
rewrite of the same clause must pass; and the Setter brief carries the three rules.
"""
from __future__ import annotations

import os
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import relentless_exam as E             # noqa: E402

FAILS = []


def check(cond, what):
    print(("ok   " if cond else "FAIL ") + what)
    if not cond:
        FAILS.append(what)


# --- the recorded items (titles as the supervisor filed them; digest of the 2026-11-06 grading)
T_8643 = ("GAMEENV_FIX_PROOFSITE_87D091F9_ITEMS_WAIT  Game-lane environment cause (proof_or_site) no lane step can fix "
          "stops live proofs: site not prepared: <3>WSL (870506 - ) ERROR: UtilAcceptVsock:273: accept4 failed 110")
T_0984 = ("GAMEENV_FIX_HARNESS_09849AF1_ITEMS_WAIT  Game-lane environment cause (harness) no lane step can fix stops live "
          "proofs: idge client is active -- pid 42468 (rimbridge_client.py) jawa/running_mods 2026-11-06T15:06:16Z 6s ago. "
          "Take the bridge")
T_SEEDS = ("CHECKER_REACH_FIX_SEEDS_STILL_DARK  the seed compare adapter's reading must report RESULT PASS: 0 failed "
           "and exit 0 at a sha whose prover passes")
T_NAMED = "FOO_FIX_CLASSIFY_UNKNOWN  relentless_envcause.classify() must mark a UtilAcceptVsock drop as lane-fixable"


def clause(cid, says, argv=None, kind="behaviour"):
    return {"id": cid, "says": says, "kind": kind, "check": {"argv": argv or ["python3", ".exam/t.py"], "timeout_s": 60,
                                                             "red": {"exit": [1]}}, "break": {"kind": "base_red"}}


def codes(v, code):
    return [r for r in v["refusals"] if r["code"] == code]


def red_run(argv, patch, timeout):            # every check is an assertion red on base (base_red holds)
    return 1, "FAIL: not yet\n", False


def exam_of(item_text, *cl):
    return {"item": "X", "clauses": list(cl), "maps": {item_text.split("  ", 1)[1][:60]: [c["id"] for c in cl]}}


# (1) MECHANISM_PINNED: the 87D091F9 clause as the Setter wrote it, vs the outcome the item states
pinned = clause("c2", "When every launch of the site step is dropped by WSL interop (UtilAcceptVsock), the resulting row is "
                      "not classified by relentless_envcause as a route-once cause (harness/proof_call/proof_or_site/"
                      "missing_mod) that 'no lane step can fix'")
v = E.validate(exam_of(T_8643, pinned), red_run, T_8643, exam_files={"t.py": "x = 'UtilAcceptVsock:273: accept4 failed 110'"})
check(codes(v, "MECHANISM_PINNED") and "relentless_envcause" in codes(v, "MECHANISM_PINNED")[0]["why"] and not v["ok"],
      "87D091F9 shape: a clause demanding relentless_envcause classify the cause is refused (MECHANISM_PINNED)")
outcome = clause("c2", "A site step whose Windows launch WSL interop drops (UtilAcceptVsock:273: accept4 failed 110) no "
                       "longer stops live proofs: the proof runs to its own verdict and the bridge is released")
v = E.validate(exam_of(T_8643, outcome), red_run, T_8643, exam_files={"t.py": "x = 'UtilAcceptVsock:273: accept4 failed 110'"})
check(v["ok"], "87D091F9 rewritten as the item's outcome (any mechanism) validates: %s" % v["refusals"])
named = clause("c1", "relentless_envcause.classify() marks a UtilAcceptVsock drop lane-fixable")
v = E.validate(exam_of(T_NAMED, named), red_run, T_NAMED, exam_files={"t.py": "pass"})
check(not codes(v, "MECHANISM_PINNED"), "a mechanism the item's own text names may be pinned: %s" % v["refusals"])
check(E.pinned_names("go_to_main_menu lands after live_site.py --menu-dwell", T_0984) == ["go_to_main_menu", "live_site.py"],
      "pinned_names: code words absent from the item (09849AF1's go_to_main_menu, live_site.py) are named")
check(E.pinned_names("pid 42468 (rimbridge_client.py) jawa/running_mods no longer stops live proofs", T_0984) == [],
      "pinned_names: the item's own code words (rimbridge_client.py, running_mods) are not pins")
art = dict(clause("c9", "writes relentless_envcause.py"), kind="artifact")
check(not E.outcome_lint({"clauses": [art]}, "a file"), "an artifact clause is not linted for mechanism")

# (2) POSITIONAL_MATCH: the SEEDS_STILL_DARK reading, a trailing wrapper line after the verdict
reading = "ok   class all_red: doc == recomputed\nRESULT PASS: 0 failed\nseed compare exit=0 at c6c14a7fb007\n"
positional = "if out.strip().splitlines()[-1] != 'RESULT PASS: 0 failed':\n    sys.exit(1)\n"
ends = "if not reading.rstrip().endswith('RESULT PASS: 0 failed'):\n    sys.exit(1)\n"
contain = "if 'RESULT PASS: 0 failed' not in out.splitlines():\n    sys.exit(1)\n"
check(reading.strip().splitlines()[-1] != "RESULT PASS: 0 failed" and "RESULT PASS: 0 failed" in reading.splitlines(),
      "the recorded SEEDS reading passes by containment and reads red by position (the judged false red)")
seeds = exam_of(T_SEEDS, clause("c2", "the reading reports RESULT PASS: 0 failed and exit 0"))
for body, want, what in ((positional, True, "lines[-1]"), (ends, True, ".endswith on output"), (contain, False, "containment")):
    v = E.validate(seeds, red_run, T_SEEDS, exam_files={"test_seed.py": body})
    check(bool(codes(v, "POSITIONAL_MATCH")) == want, "SEEDS shape, %s: POSITIONAL_MATCH %s" % (what, "refused" if want else "not raised"))
check(not E.positional_matches({"t.py": "if path.endswith('.py') or text.endswith('.md') or body.endswith('\\n'):\n    pass\n"}),
      "a path's or helper's .endswith is not an output match")
check(not E.positional_matches({"fx.json": "out.splitlines()[-1]"}), "a fixture (data, not code) is not scanned for position")
check(E.positional_matches({"t.py": "last = out.strip().split('\\n')[-1]"}), "split('\\n')[-1] is a positional match too")
# The recorded lines, verbatim from the frozen exams: the output was split into a list first, then its last row compared.
REAL_SEEDS = """if not ls or ls[-1] != "RESULT PASS: 0 failed": fail("reading does not end 'RESULT PASS: 0 failed': %r" % ls[-3:])\n"""
REAL_PIT = """if lines[-1] != "FIXTURE_VERDICT: PASS":\n"""
check(E.positional_matches({"test_seed_compare_adapter.py": REAL_SEEDS}), "the frozen SEEDS exam's own line is POSITIONAL_MATCH")
check(E.positional_matches({"check_fixture_script.py": REAL_PIT}), "a last row compared to a verdict literal is POSITIONAL_MATCH")
for body, what in (("if lines[-1].startswith('RESULT PASS'):\n", "a last row's prefix"), ("if 'RESULT PASS' not in ls[-1]:\n", "a verdict sought only in the last row")):
    check(E.positional_matches({"t.py": body}), "%s is POSITIONAL_MATCH" % what)
for body, what in (("rec = json.loads(lines[-1])\n", "a last row parsed, not compared to a verdict"), ("if parts[-1] != 'x':\n", "a short literal"),
                   ("if 'RESULT PASS: 0 failed' not in ls:\n", "containment over the rows")):
    check(not E.positional_matches({"t.py": body}), "%s is not POSITIONAL_MATCH" % what)

# incident_texts: what is not the incident stays out of it
_short = "X  stops live proofs: the proof timed out tsn=1793968086378236492 | agent's reason: relentless supervisor"
check(not E.incident_texts(_short), "a history row's tsn and reason are not the incident's words (the incident is under 24 chars)")
_long = "X  stops live proofs: site not prepared: not ready at the main menu tsn=179 | agent's reason: relentless"
check(E.incident_texts(_long) == ["site not prepared: not ready at the main menu"], "the incident ends where the history row's tsn begins: %r" % E.incident_texts(_long))
check(not E.incident_texts("Done when: 'run_selftests.py --only selftest_ops_churn' is green"), "a quoted command is not an incident")

# (3) INCIDENT_NOT_REPLAYED: 09849AF1 fixture must carry the recorded incident text
c0984 = clause("c1", "A foreign client's call that ended 6s ago ('idge client is active -- pid 42468') no longer stops live proofs")
imagined = {"test_menu_site_foreign_call.py": "ROWS = [{'pid': 651423, 'tool': 'jawa/map_info', 'end': None}]\n"}
replayed = {"test_menu_site_foreign_call.py": "INCIDENT = 'idge client is active -- pid 42468 (rimbridge_client.py) "
                                              "jawa/running_mods 2026-11-06T15:06:16Z 6s ago'\n"}
v = E.validate(exam_of(T_0984, c0984), red_run, T_0984, exam_files=imagined)
check(codes(v, "INCIDENT_NOT_REPLAYED") and not v["ok"], "09849AF1 shape: an imagined fixture is refused (INCIDENT_NOT_REPLAYED)")
v = E.validate(exam_of(T_0984, c0984), red_run, T_0984, exam_files=replayed)
check(not codes(v, "INCIDENT_NOT_REPLAYED"), "09849AF1: a fixture carrying the recorded line validates: %s" % v["refusals"])
q = "FOO_FIX_X  the log said 'Could not resolve cross-reference to RM_Thing' and the load stopped"
check(E.incident_texts(q) and E.replays_incident(q, {"f.json": "{}"}), "a quoted incident (16+ chars) is owed by fixtures")
check(not E.incident_texts("the builder doesn't fix the upstream cause, and the supervisor can't tell the difference."),
      "contractions are not quotes")
check(not E.incident_texts('owner said "Ban it everywhere, every machine and project"'),
      "an owner's quoted sentence is not a recorded incident")
check(E.pinned_names(["not", "a", "string"], T_0984) == [], "a non-string says is no crash")
check(E.pinned_names("cli.py --list prints exit_code", "item: a tool clinic; exit code 0") == ["cli.py"],
      "a short stem is matched by word, not substring; a snake word the item spells with spaces is not a pin")
check(E.replays_incident("FOO_DOUBLE_RETURNS_TWICE: foo.double(n) must return 2*n", {}) is None,
      "an item with no recorded incident owes no replay")
v = E.validate(exam_of(T_0984, c0984), red_run, T_0984)
check(not codes(v, "INCIDENT_NOT_REPLAYED") and not codes(v, "POSITIONAL_MATCH"),
      "exam_files=None (no files read) skips the file lints")

# (4) read_exam_files: the Setter's files reach the lints from run_item
with tempfile.TemporaryDirectory() as d:
    os.makedirs(os.path.join(d, "fx"))
    with open(os.path.join(d, "fx", "incident.log"), "w") as f:
        f.write("idge client is active -- pid 42468 (rimbridge_client.py) jawa/running_mods\n")
    got = E.read_exam_files(d)
    check(list(got) == [os.path.join("fx", "incident.log")] and E.replays_incident(T_0984, got) is None,
          "read_exam_files: a nested fixture file is read and counts as the replay")
src = open(os.path.join(HERE, "relentless_exam.py"), encoding="utf-8").read()
check("exam_files=read_exam_files(files)" in src, "run_item hands the Setter's files to validate")

# (5) the brief tells the Setter all three rules before it writes
brief = E.setter_prompt("X", "t", "b", "e", "f")
for needle in ("ACCEPT ANY MECHANISM", "MECHANISM_PINNED", "REPLAY THE RECORDED INCIDENT", "INCIDENT_NOT_REPLAYED",
               "CONTAINMENT", "POSITIONAL_MATCH", "two different fixes"):
    check(needle in brief, "Setter brief carries %r" % needle)

print("%s: %d failed" % ("RESULT PASS" if not FAILS else "RESULT FAIL", len(FAILS)))
sys.exit(1 if FAILS else 0)
