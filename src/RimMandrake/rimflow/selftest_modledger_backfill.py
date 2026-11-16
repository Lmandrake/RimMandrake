#!/usr/bin/env python3
"""Selftest for modledger_backfill.py on a fixture concept folder (never the real ones).

    python3 src/RimMandrake/Utils/run_selftests.py --only modledger_backfill

Shadow mode: the backfill writes only the mod's ledger (every event BACKFILL, every one citing its old file), leaves
every old file byte for byte, is idempotent, turns a blind fault's smallest_fix into the finding's proposed fix, keeps
a FIXED fault open as claimed (no judge verdict), counts his words as answers, and `compare` names a stale journal.
Under the entry standard: every event passes `append`'s checks (a source that cannot is left out and reported, never
forced), an item repeating a fault mines nothing new, a live row with no mod sha is left out, and an old BACKFILL line
the plan no longer holds is deleted on the re-run while the lines it still holds are kept byte for byte.
"""
import hashlib
import re
import json
import os
import shutil
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import modledger as M                                            # noqa: E402
import modledger_backfill as B                                   # noqa: E402

FAIL = []
MOD = "FixtureMod"


def check(name, ok, detail=""):
    print(("ok    " if ok else "FAIL  ") + name + ("" if ok else "  " + str(detail)))
    if not ok:
        FAIL.append(name)


def w(path, obj):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(obj if isinstance(obj, str) else json.dumps(obj))


root = tempfile.mkdtemp(prefix="modledger_bf_")
c = os.path.join(root, "design", "concepts", MOD)
v = os.path.join(c, "version")
w(os.path.join(v, "VERSION.json"), {"mod": MOD, "version": "0.1.0", "state": "locked", "locked_on": "2026-11-13",
                                    "locked_by": "owner", "owner_words": "\"Lock it.\" (owner)", "bars_total": 2,
                                    "bars_met": 2})
w(os.path.join(v, "stage_record.json"), {"stage": "offline_build", "stage_label": "Offline build (Stage 3)",
                                         "since": "2026-11-15T17:50:11-08:00", "since_from": "advance",
                                         "moves": [{"from": "offline_build", "to": "in_game", "at": "x", "by": "C",
                                                    "why": "exit met"},
                                                   {"from": "in_game", "to": "offline_build", "at": "y", "by": "C",
                                                    "why": "visit failed"}]})
w(os.path.join(v, "locked_bars.json"), {"ids": ["bar_a", "bar_b"]})
w(os.path.join(v, "test_table.json"), {"made": "2026-11-14", "bars": [
    {"id": "bar_a", "kind": "experience", "source": "tree.json", "proves_at": "6", "decides": ["sc_a"],
     "offline_green_today": True},
    {"id": "bar_b", "kind": "inventory", "source": "record.json", "proves_at": "3", "decides": ["sc_b"],
     "offline_green_today": False}]})
w(os.path.join(v, "in_game", "visit_1", "rows.jsonl"),
  json.dumps({"test": "sc_a", "verdict": "FAIL", "mod_sha": "abc1234"}) + "\n" +
  json.dumps({"test": "sc_a", "verdict": "PASS", "mod_sha": "def5678", "command": "runner.py --scenes a"}) + "\n" +
  json.dumps({"test": "sc_b", "verdict": "PASS"}) + "\n")
w(os.path.join(v, "blind_challenge", "cycle_1", "lane2", "faults.json"), {"faults": [
    {"id": "RIMMANDRAKE_STOP_FIXTURE_RAY_AT_WALL_CELL", "class": "Problem", "bar": "bar_a", "criterion": "a thrown pawn stops at a wall",
     "evidence": ["row L1 FAIL"], "smallest_fix": "stop the ray at the first impassable cell", "status": "FIXED abc1234"},
    {"id": "RIMMANDRAKE_POINT_FIXTURE_FIX_AT_A_REFERENCE", "class": "Polish", "bar": "bar_b", "criterion": "short", "evidence": ["e"],
     "smallest_fix": "K-1", "status": "PENDING"}]})
w(os.path.join(c, "journal.md"), "# j\n\n## The mod as it stands\n\n- **Stage now:** Stage 3, offline build.\n"
  "- Every in-game scene is UNRUN (Stage 6).\n- **Waiting on:** not yet written for this stage.\n\n"
  "### His words on this mod (verbatim)\n\n- 2026-11-10: \"Throw it far.\"\n- 2026-11-12: \"Shelves are open,\n"
  "  period.\"\n\n### Oddities\n")
w(os.path.join(root, "infrastructure", "state", "items", "RIMMANDRAKE_FIX_FIXTUREMOD_THING_ONE.md"),
  "# RIMMANDRAKE_FIX_FIXTUREMOD_THING_ONE\n\nFixtureMod drops goods.\n\n## spec\n\nfile: Source/A.cs — keep the goods.\n\nAcceptance test: selftest_a.py exit 0\n")
os.makedirs(os.path.join(root, "design", "concepts", "OtherMod"))
w(os.path.join(root, "infrastructure", "state", "items", "RIMMANDRAKE_BACKFILL_OTHERMOD_LEDGER_LIKE_THE_FIRST.md"),
  "# RIMMANDRAKE_BACKFILL_OTHERMOD_LEDGER_LIKE_THE_FIRST\n\nFixtureMod was backfilled first; do OtherMod the same way.\n")
w(os.path.join(root, "infrastructure", "state", "items", "RIMMANDRAKE_FLING_FIXTUREMOD_STEP_TWO.md"),
  "# RIMMANDRAKE_FLING_FIXTUREMOD_STEP_TWO\n\nStep 2 of plan.md (FixtureMod Designer pass).\n")
w(os.path.join(root, "infrastructure", "state", "ledger", "events", "BENCH.jsonl"),
  json.dumps({"event": "file", "id": "RIMMANDRAKE_FLING_FIXTUREMOD_STEP_TWO", "title": "Goods fly 1.6x a person"}) + "\n")
w(os.path.join(root, "infrastructure", "state", "items", "RIMMANDRAKE_STOP_FIXTURE_RAY_AT_WALL_CELL.md"),
  "# RIMMANDRAKE_STOP_FIXTURE_RAY_AT_WALL_CELL\n\nFixtureMod's blast ray passes walls.\n")
w(os.path.join(root, "infrastructure", "state", "items", "RIMMANDRAKE_FIX_OTHER_MOD_THING.md"),
  "# RIMMANDRAKE_FIX_OTHER_MOD_THING\n\nNot ours.\n")
# closed tickets, a list-shaped red record, journal oddities, refuted causes (entry standard rule 10)
w(os.path.join(v, "blind_challenge", "cycle_2", "lane2", "faults.json"), {"faults": [
    {"id": "RIMMANDRAKE_RESET_FIXTURE_STATICS_CENSUS_CAUGHT", "class": "Problem", "bar": "bar_a",
     "criterion": "statics reset between games", "evidence": ["census FAIL"], "smallest_fix": "reset the statics at load",
     "status": "FIXED 1234abcd"}]})
w(os.path.join(v, "blind_challenge", "cycle_2", "lane2", "fixes.jsonl"), json.dumps(
    {"fault": "RIMMANDRAKE_RESET_FIXTURE_STATICS_CENSUS_CAUGHT",
     "red": [{"on": "aaaa111", "cmd": "selftest_census.py", "rc": 1}, {"on": "bbbb222", "cmd": "selftest_census.py", "rc": 1}],
     "green": {"on": "1234abcd", "cmd": "selftest_census.py", "rc": 0}, "sha": "1234abcd"}) + "\n")
IT = os.path.join(root, "infrastructure", "state", "items")
w(os.path.join(IT, "closed", "RIMMANDRAKE_FIX_FIXTUREMOD_CLOSED_BY_A_FIX.md"),
  "## spec\n\nfile: Source/B.cs: clamp the arc; never drop a refuted cause.\n\nAcceptance test: selftest_b.py exit 0\n")
w(os.path.join(IT, "RIMMANDRAKE_BACKFILL_FIXTUREMOD_LEDGER_IN_SHADOW.md"), "## spec\n\nBackfill FixtureMod's ledger.\n")
w(os.path.join(IT, "closed", "RIMMANDRAKE_READ_FIXTUREMOD_NO_DEFECT_AFTER_ALL.md"),
  "## spec\n\nfile: Source/C.cs: group the poles by kind.\n")
w(os.path.join(IT, "closed", "RIMMANDRAKE_DROP_FIXTUREMOD_FILED_TWICE.md"), "## spec\n\nfile: Source/D.cs: same as B.\n")
w(os.path.join(IT, "RIMMANDRAKE_BUILD_FIXTUREMOD_IMPLEMENTED_NOT_CLOSED.md"),
  "## spec\n\nfile: Source/E.cs: drain the right faction.\n")
w(os.path.join(IT, "closed", "RIMMANDRAKE_FIX_SLACKMASTER_POST_AS_RIGHT_TEAM.md"), "## spec\n\nPost as the right team.\n")
# FlowWorks' shapes: a close on a pre-landing sha ./publish rewrote, a spec holding a pasted traceback, a fault class
# under 'cls', a long card label, his words past the line cap in multibyte characters
w(os.path.join(IT, "closed", "RIMMANDRAKE_FIX_FIXTUREMOD_REBASED_PUMP_FIX.md"), "## spec\n\nFixtureMod: prime the pump.\n")
w(os.path.join(IT, "closed", "RIMMANDRAKE_FIX_FIXTUREMOD_FENCED_SPEC_PASTE.md"),
  "## spec\n\nFixtureMod: guard the null def.\nTraceback (most\nrecent call last): x\n```\n  at Verse.X()\n```\n\n"
  "## verify\n\n```\nselftest_b.py\n```\n")
w(os.path.join(v, "blind_challenge", "cycle_3", "lane2", "faults.json"), [
    {"id": "RIMMANDRAKE_TRIM_FIXTURE_VALVE_ON_EXACT_FIT", "cls": "Polish", "bar": "bar_b", "criterion": "an exact fit "
     "opens", "evidence": ["row L2 FAIL"], "smallest_fix": "compare with <= at the last cell", "status": "PENDING"}])
# two tickets whose subjects the mint check calls near-duplicates: kept apart on the first run, kept on the re-run
w(os.path.join(IT, "RIMMANDRAKE_FIX_FIXTUREMOD_PROOF_DRIVERS_EARLY_FALSE_PASS.md"),
  "## spec\n\nFixtureMod proof drivers pass early on a stale read.\n")
w(os.path.join(IT, "RIMMANDRAKE_FIX_FIXTUREMOD_PROOF_DRIVERS_LATE_FALSE_PASS.md"),
  "## spec\n\nFixtureMod proof drivers pass late on a stale read.\n")
B.landed_sha = lambda root_, sha: "abc7777" if sha == "beef123" else sha
EVL = [
    {"seat": "BENCH", "event": "file", "id": "FIXTUREMOD_OLD_TICKET_WITH_NO_FILE_1", "title": "ledger-only", "tsn": 9},
    {"seat": "BENCH", "event": "file", "id": "RIMMANDRAKE_FIX_FIXTUREMOD_CLOSED_BY_A_FIX", "title": "Arcs overshoot walls",
     "tsn": 10},
    {"seat": "BENCH", "event": "claim", "id": "RIMMANDRAKE_FIX_FIXTUREMOD_CLOSED_BY_A_FIX", "tsn": 11},
    {"seat": "BENCH", "event": "note", "id": "RIMMANDRAKE_FIX_FIXTUREMOD_CLOSED_BY_A_FIX", "tsn": 12,
     "text": "LIVE run at 5555eee: arc FAIL. False theory: the pool fix still breaks 20 ms (deployed DLL was stale, "
             "src/RimMandrake/FixtureMod/Source/B.cs untouched)."},
    {"seat": "CONDUCTOR", "event": "verify", "id": "RIMMANDRAKE_FIX_FIXTUREMOD_CLOSED_BY_A_FIX", "result": "pass",
     "config": "selftest_b.py (rc 0; rc 1 at 4444ddd)", "sha": "abcdef12", "tsn": 13},
    {"seat": "CONDUCTOR", "event": "close", "id": "RIMMANDRAKE_FIX_FIXTUREMOD_CLOSED_BY_A_FIX", "sha": "abcdef12",
     "why": "detached run: red-first record kept", "tsn": 14},
    {"seat": "OWNER", "event": "close", "id": "RIMMANDRAKE_READ_FIXTUREMOD_NO_DEFECT_AFTER_ALL", "sha": "abcdef34",
     "noCode": "GPT re-read of current code: no defect remains (both paths group by kind)", "tsn": 20},
    {"seat": "BENCH", "event": "drop", "id": "RIMMANDRAKE_DROP_FIXTUREMOD_FILED_TWICE", "reason": "duplicate of B",
     "tsn": 30},
    {"seat": "OWNER", "event": "implemented", "id": "RIMMANDRAKE_BUILD_FIXTUREMOD_IMPLEMENTED_NOT_CLOSED",
     "sha": "abcdef56", "criteria": [{"id": "A1", "text": "selftest: drain A, charge only A"}], "tsn": 40},
    {"seat": "BENCH", "event": "close", "id": "RIMMANDRAKE_FIX_SLACKMASTER_POST_AS_RIGHT_TEAM", "sha": "abcdef78",
     "tsn": 50}]
# tickets with no prose file at all (most tickets: their rimflow events are the whole record), a closed prose ticket
# that only mentions the mod in passing, and a mining ticket about the mod's ledger itself
LO, LP, LS, LX, LM, LG = ("RIMMANDRAKE_TRACE_FIXTUREMOD_LEDGER_ONLY_GAS", "RIMMANDRAKE_SHORTEN_LANE_READS_SHORT",
                          "RIMMANDRAKE_FIX_FIXTUREMOD_OLD_LANE_READING", "RIMMANDRAKE_ISOLATE_SELFTEST_FROM_PILOT",
                          "RIMMANDRAKE_MINE_FIXTUREMOD_TICKETS_INTO_IT", "RIMMANDRAKE_ADD_OTHERLIST_AFTER_FIXTURE")
w(os.path.join(IT, "closed", LG + ".md"), "# %s\n\nAdd OtherMod to the list. FixtureMod was added the day before.\n" % LG)
EVL += [
    {"seat": "BENCH", "event": "file", "id": LO, "title": "FixtureMod sc_gas FAIL: the chain stops at five of seventeen",
     "tsn": 60},
    {"seat": "BENCH", "event": "claim", "id": LO, "why": "detached run", "tsn": 61},
    {"seat": "BENCH", "event": "note", "id": LO, "text": "Started looking at the gas chain again.", "tsn": 62},
    {"seat": "BENCH", "event": "close", "id": LO, "sha": "abcdef90", "why": "the chain's step limit was 5; raised",
     "tsn": 63},
    {"seat": "BENCH", "event": "file", "id": LP, "title": "Polish, FixtureMod: the lane reads short", "tsn": 64},
    {"seat": "BENCH", "event": "file", "id": LS, "title": "FixtureMod: the old lane reading", "tsn": 65},
    {"seat": "BENCH", "event": "supersede", "id": LS, "by": LP, "why": "the polish ticket carries it", "tsn": 66},
    {"seat": "BENCH", "event": "file", "id": LX, "title": "selftest_x RED; FixtureMod is the pilot it broke on",
     "tsn": 67},
    {"seat": "BENCH", "event": "file", "id": LM, "title": "Mine FixtureMod's tickets into its mod ledger", "tsn": 68},
    {"seat": "BENCH", "event": "file", "id": LG, "title": "Add OtherMod to the full list", "tsn": 69},
    {"seat": "BENCH", "event": "close", "id": LG, "sha": "abcdef91", "why": "added", "tsn": 70},
    # two tickets whose titles look alike: the second is kept with --new-subject, and must stay kept on every re-run
    {"seat": "BENCH", "event": "file", "id": "RIMMANDRAKE_RUN_FIXTUREMOD_BLIND_CHALLENGE_CYCLE_ONE",
     "title": "FixtureMod 0.1.0: run the blind offline challenge cycle one by hand and record it", "tsn": 71},
    {"seat": "BENCH", "event": "file", "id": "RIMMANDRAKE_RUN_FIXTUREMOD_BLIND_CHALLENGE_CYCLE_TWO",
     "title": "FixtureMod 0.1.0: run the blind offline challenge cycle two by hand and record it", "tsn": 72}]
EVL += [
    {"seat": "BENCH", "event": "close", "id": "RIMMANDRAKE_FIX_FIXTUREMOD_REBASED_PUMP_FIX", "sha": "beef123",
     "reason": "pump primed", "tsn": 60},
    {"seat": "BENCH", "event": "close", "id": "RIMMANDRAKE_FIX_FIXTUREMOD_FENCED_SPEC_PASTE", "sha": "abcdef90",
     "tsn": 61},
    {"seat": "OWNER", "event": "note", "id": "RIMMANDRAKE_FIX_FIXTUREMOD_REBASED_PUMP_FIX", "tsn": 62,
     "byCard": "FixtureMod pump question → " + "prime it from the tank every dawn " * 12},
    {"seat": "OWNER", "event": "note", "id": "RIMMANDRAKE_FIX_FIXTUREMOD_FENCED_SPEC_PASTE", "tsn": 63,
     "ownerSaid": "Shelves — “never” — lost " * 24}]
with open(os.path.join(root, "infrastructure", "state", "ledger", "events", "BENCH.jsonl"), "a", encoding="utf-8") as fh:
    for e_ in EVL:
        fh.write(json.dumps(e_) + "\n")
w(os.path.join(root, "infrastructure", "state", "ledger", "events", "OWNER.jsonl"), json.dumps(
    {"seat": "OWNER", "event": "note", "id": "RIMMANDRAKE_READ_FIXTUREMOD_NO_DEFECT_AFTER_ALL",
     "ownerSaid": "Reopen it if it ever comes back, never file a new one.", "tsn": 21}) + "\n" + json.dumps(
    {"seat": "OWNER", "event": "note", "id": "RIMMANDRAKE_FIX_FIXTUREMOD_CLOSED_BY_A_FIX", "tsn": 22,
     "ownerSaid": " ".join("Arc number %d — keep it under the wall’s lip, always." % i for i in range(12))}) + "\n")
with open(os.path.join(c, "journal.md"), "a", encoding="utf-8") as fh:
    fh.write("\n1. **47, not 48.** `VERSION.json` says 47; the sum is 48 because one row is a leaf too. [measured]\n"
             "2. **The old shock name is a mirror.** `AerialSettings.fallenWireShock` is derived; the setting is\n"
             "   `shockReach`.\n\n### Questions for him\n\n1. Re-pin?\n")
# --- the independent judges' six rules (RIMMANDRAKE_FIX_MINER_JUDGE_FAILED_SLACK_EIGHT_OF_TWENTY) ---
# rule 1: state from the ticket's FINAL rimflow state; a bulk OWNER re-stamp never displaces the original fix sha
RS, RO, RC, RT, RF, RK, RL = ("RIMMANDRAKE_FIX_FIXTUREMOD_STUB_PASSED_LAST_WEEK",
                              "RIMMANDRAKE_FIX_FIXTUREMOD_BUILT_THEN_REOPENED",
                              "RIMMANDRAKE_TRACE_FIXTUREMOD_PIT_FETCH_PAST_LADDER",
                              "RIMMANDRAKE_FIX_FIXTUREMOD_WATER_STUB_CORRECTED",
                              "RIMMANDRAKE_FIX_FIXTUREMOD_THEFT_WRONG_VICTIM",
                              "RIMMANDRAKE_FIX_FIXTUREMOD_STOREROOM_COVER_INVALID",
                              "RIMMANDRAKE_FIX_FIXTUREMOD_LONG_SPEC_NEVER_CUT")
LONG = " ".join("Sentence %d says the pump primes from tank %d before the valve opens." % (i, i) for i in range(9))
w(os.path.join(IT, RS + ".md"), "## spec\n\nFixtureMod water stubs drop on deep water.\n")
w(os.path.join(IT, RO + ".md"), "## spec\n\nFixtureMod drains the wrong battery.\n")
w(os.path.join(IT, RT + ".md"), "## spec\n\nFixtureMod water stub reads twice.\n\n## evidence\n\n"
  "- T_GEOM is green (4513/4513) because it reads the 7 oracle scenes only.\n")
w(os.path.join(IT, RF + ".md"), "## spec\n\nfound-by: GPT review, verified by Opus.\n\nThe drain charges the wrong "
  "faction.\n\nFix: record which faction supplied each drained tick; charge each its own share.\n\n## criteria\n\n"
  "- A1 selftest_theft.py: drain A then switch to B; A is charged only A's share\n\n"
  "- Written by the Producer re-plan 2026-10-29.\n")
w(os.path.join(IT, RL + ".md"), "## spec\n\n" + LONG + "\n\nAcceptance test: " + LONG + "\n")
EV2 = [
    {"seat": "BENCH", "event": "file", "id": RS, "title": "FixtureMod water stubs drop on deep water", "tsn": 100},
    {"seat": "BENCH", "event": "implemented", "id": RS, "sha": "abcd0011", "tsn": 101,
     "criteria": [{"id": "A1", "text": "live: stubs stay on deep water"}]},
    {"seat": "CLAUDE_X", "event": "verify", "id": RS, "result": "pass", "sha": "abcd0b0b",
     "config": "proof_all.py --live --only matrix: PASS", "tsn": 102},
    {"seat": "OWNER", "event": "close", "id": RS, "sha": "abcd0b0b", "tsn": 103},
    {"seat": "BENCH", "event": "implemented", "id": RO, "sha": "abcd0022", "tsn": 110},
    {"seat": "OWNER", "event": "reassign", "id": RO, "to": "BENCH", "tsn": 111},
    # rule 2: ruled-out causes under any wording, from the notes, and traps
    {"seat": "BENCH", "event": "file", "id": RC, "title": "FixtureMod sc_pit FAIL: a hauler fetched the control stack "
     "past a raised ladder", "tsn": 120},
    {"seat": "BENCH", "event": "note", "id": RC, "tsn": 121, "text": "Ruled out by reading the source (base abcd0033): "
     "the ladder is placed right in src/RimMandrake/FixtureMod/Source/L.cs, so the masks are not stale."},
    {"seat": "BENCH", "event": "note", "id": RC, "tsn": 122, "text": "The stale DLL was not the cause: the deployed DLL "
     "matched abcd0033."},
    {"seat": "BENCH", "event": "note", "id": RC, "tsn": 123, "text": "The fault was in the test setup; FixtureMod itself "
     "behaved correctly (no escape bug in the mod)."},
    {"seat": "BENCH", "event": "close", "id": RC, "sha": "abcd0033", "tsn": 124,
     "why": "detached run: the test now lowers the control ladder first"},
    {"seat": "BENCH", "event": "note", "id": RT, "tsn": 130, "text": "Correction: the A1 live pass ran the DLL committed "
     "at abcd0044, not the older abcd0033 DLL."},
    {"seat": "RUNNER", "event": "note", "id": RT, "tsn": 131, "text": "relentless: game_fail at abcd0044 explained "
     "(PROOF): the binding has no site step, so the proof ran against whatever state the game was in."},
    {"seat": "BENCH", "event": "note", "id": RT, "tsn": 132, "text": "It turned out the wrapper exits 1 for both row FAIL "
     "and row never measured."},
    # rule 4: the accept a ledger-only ticket filed, the change a close names
    {"seat": "OWNER", "event": "file", "id": RK, "title": "FixtureMod sc_storeroom UNMEASURED: no stack plan ends on the "
     "covered pit cell", "why": "REAL MISS. Acceptance test: live, python.exe runner.py --scenes sc_storeroom,"
     "sc_storeroom_control --ticks 900 stages both and reads PASS or FAIL", "tsn": 140},
    {"seat": "BENCH", "event": "note", "id": RK, "tsn": 141, "text": "Fixed abcd0066. Cause [measured]: MassScale caps "
     "at 2 under ~17.5 kg, so every small log stack threw 3 cells, past the cover. Search now runs to CoverLogsMax=75."},
    {"seat": "BENCH", "event": "close", "id": RK, "sha": "abcd0066", "tsn": 142,
     "why": "detached run: cover-stack search fixed offline"},
    {"seat": "BENCH", "event": "close", "id": RL, "sha": "abcd0077", "tsn": 150, "why": "pump primed"},
    # rule 3: his words on lifecycle and fleet-wide events are never a decision about the mod
    {"seat": "OWNER", "event": "needs", "id": RK, "to": "owner", "tsn": 160,
     "ownerSaid": "You should work that item right now so we can keep going together."},
    {"seat": "OWNER", "event": "reassign", "id": RK, "to": "BENCH", "tsn": 161,
     "byCard": "What should happen to FOUNDRY? → Retire it (Recommended)"},
    {"seat": "OWNER", "event": "note", "id": RK, "tsn": 162, "text": "FROZEN STOP 2026-11-07: was checking",
     "ownerSaid": "Please have those Frozen items shut down their work."},
    {"seat": "OWNER", "event": "note", "id": RK, "tsn": 163, "ownerSaid": "Gas should chain through every vent."}]
EV2 += [{"seat": "OWNER", "event": "note", "id": RK, "tsn": 164, "ownerSaid": "We're staying interactive tonight, tokens "
         "too low."},
        {"seat": "OWNER", "event": "note", "id": "RIMMANDRAKE_DESIGN_SOME_PIPELINE_WHOLE_MOD", "tsn": 165,
         "text": "pipeline card; FixtureMod is a pilot", "ownerSaid": "(2) and we should track quota the same way."},
        {"seat": "OWNER", "event": "note", "id": "RIMMANDRAKE_MEASURE_SOME_COMPLETION_HOW_DONE", "tsn": 166,
         "ownerSaid": "Fixture Mod must score far above OtherMod on completion."}]
for i_, t_ in enumerate((RK, RC, RT)):
    EV2.append({"seat": "OWNER", "event": "note", "id": t_, "tsn": 170 + i_, "ownerSaid": "Stop all the lanes tonight."})
for i_ in range(4):     # the bulk re-stamp: one OWNER sha stamped on many tickets at once
    EV2.append({"seat": "OWNER", "event": "implemented", "id": "OTHERMOD_BULK_STAMP_%d" % i_, "sha": "abcd0b0b",
                "tsn": 180 + i_})
EV2.append({"seat": "OWNER", "event": "implemented", "id": RS, "sha": "abcd0b0b", "tsn": 190,
            "why": "re-pointed to abcd0b0b (current DLL, contains the fix)"})
for e_ in EV2:          # each seat's events in its own shard, as rimflow writes them
    with open(os.path.join(root, "infrastructure", "state", "ledger", "events", "%s.jsonl" % (
            "OWNER" if e_["seat"] == "OWNER" else "BENCH")), "a", encoding="utf-8") as fh:
        fh.write(json.dumps(e_) + "\n")
# rules 4 and 5: a blind fault's defect line, its would_pass, its comma-listed bars, and what its fix changed
w(os.path.join(v, "blind_challenge", "cycle_4", "lane2", "faults.json"), {"faults": [
    {"id": "RIMMANDRAKE_WIDEN_FIXTURE_SCAN_FIVE_SLIPPED", "class": "Problem", "bar": "bar_a, bar_b",
     "criterion": "tree oracle: an offline scan finds no hose", "would_pass": "every planted leftover NH1..NH5 turns "
     "T1 red by name, and the clean tree stays green",
     "evidence": ["lane2/planted.jsonl: NH1..NH5 each left T_NO_HOSE green",
                  "cause: the scan read a fixed tag list, never the element tag or xpath"],
     "smallest_fix": "read every element's text and tag; pin the five as mutants", "status": "FIXED abcd0055"}]})
w(os.path.join(v, "blind_challenge", "cycle_4", "lane2", "fixes.jsonl"), json.dumps(
    {"fault": "RIMMANDRAKE_WIDEN_FIXTURE_SCAN_FIVE_SLIPPED", "red": {"cmd": "check_nohose.py", "rc": 1},
     "green": {"cmd": "check_nohose.py", "rc": 0}, "sha": "abcd0055"}) + "\n")
# --- the round-2 judge's rulings (D:\ClaudeWork\rimmandrake\conductor\mining_samples\<Mod>_round2.judge.json): one
# fixture ticket per WRONG / NARRATION / MISSED ruling, read by the (faked) reader the way the real tickets were ---
J = {k: "RIMMANDRAKE_%s_FIXTUREMOD_%s" % tuple(v.split(":")) for k, v in dict(
    twin="TRACE:CACHE_KEY_TWICE", built="PROVE:DROWNING_IN_SHALLOWS", own="PROVE:GRAPH_SUSTAINED_CHANGE",
    nochange="PROBE:HIDDEN_CONDUIT_HOOKUP", boiler="FIX:TAP_MIXED_NET", order="ADVANCE:OFFLINE_BESIDE_PILOT",
    cycle="CHALLENGE:BLIND_RESTS_ON_ONE", unrun="BUILD:STAGE_THREE_SCENES", status="PROVE:HIDING_LOCKER",
    shove="DESIGN:FIRST_TOUCH", doc="SWEEP:WATER_SOLVERS", run5="FIX:STICKY_OFF_NEVER_FORMS",
    later="BUILD:MOAT_WITH_MANNERS", said="SUBMERGE:PIT_FITTINGS", subj="FIX:LATE_TOGGLE_STAYS_DRY").items()}
SUBJ = {"abcd1002": "lesson: live proof tracebacks must exit UNMEASURED",
        "abcd1005": "power tap picks its own-faction transmitter, guard stops futile re-queues",
        "abcd1016": "a late deep-swim toggle recomputes path costs"}
B.SUBJECT_OF = lambda root_, sha: SUBJ.get(sha)
LONG_SAID = ("Live game grid: Tar is not nearly dark enough (fix). It reads grey. It should be dark indeed by the vent. "
             "Ramp: slowly becomes immersed but invisible beneath the water (not transparent water, fix) but the cover "
             "line is good (pass). Items (raw steel, minified furniture) never become covered (fix). I'm not sure how to "
             "judge the swale (what is expected behavior here?). Sometimes water is transparent, sometimes it isn't. "
             "Sometimes items are cut off, sometimes they are not. Sometimes the colour gets paler, sometimes it does "
             "not. It's as though each case is independently set in these variables, badly (major fix). Shadows surround "
             "the deepest pit even though it's entirely filled, and shadows are shown outside the pit rather than "
             "inside (major fix). Planks over pit are correctly always shown on top (fix: please ensure they can only "
             "be placed where there are two sides adjacent to solid ground).")
EV3 = [{"seat": "BENCH", "event": "file", "id": J[k], "title": t, "why": w, "tsn": 300 + i} for i, (k, t, w) in enumerate((
    ("twin", "FixtureMod cords heap: the cache key may miss the block kind", ""),
    ("built", "FixtureMod: prove a rat-sized pawn drowns in the shallows", ""),
    ("own", "FixtureMod graph job: prove the sustained-change bound, de-flake the wall-clock gate",
     "FixtureGates.cs GraphWorker (1) always ends in a quiet map, so it never exercises sustained change. Also "
     "FixtureGates.cs GraphWorker (3) bounds wall-clock ms on a loaded machine, so it can flake"),
    ("nochange", "FixtureMod render checks: a hookup to a hidden conduit may print a visible cable (B13)", ""),
    ("boiler", "FixtureMod: power-tap connect guards disagree on mixed-faction nets", ""),
    ("order", "Maturation Pipeline: take FixtureMod 0.1.0 through the offline stages by hand", ""),
    ("cycle", "FixtureMod 0.1.0: blind challenge cycle 1", ""),
    ("unrun", "FixtureMod Stage 3: build the scene leaves for the open bars", ""),
    ("status", "FixtureMod: prove the hiding locker live", ""),
    ("shove", "FixtureMod Designer first touch", ""),
    ("doc", "FixtureMod: sweep the water solvers on big maps", ""),
    ("run5", "FixtureMod body classify: sticky off never forms", ""),
    ("later", "FixtureMod drawbridge: a moat with manners", ""),
    ("said", "FixtureMod: submerge pit fittings by level", ""),
    ("subj", "FixtureMod swim reapply: a late toggle stays dry", "")))]
EV3 += [
    {"seat": "BENCH", "event": "close", "id": J["twin"], "sha": "abcd1001", "reason": "A6 refuted offline "
     "(incremental == fresh); cord heaps fixed at the door cell", "tsn": 330},
    {"seat": "BENCH", "event": "implemented", "id": J["built"], "sha": "abcd1002", "tsn": 331,
     "why": "relentless: blind offline PASS; the game clauses stay owed",
     "criteria": [{"id": "A1", "text": "on a quicktest map a Jawa drafted mid-pool reads ProofDrown H=0.50"}]},
    {"seat": "BENCH", "event": "verify", "id": J["built"], "result": "fail", "sha": "abcd1002", "tsn": 332,
     "config": "relentless-live: python.exe jawa_shallows_proof.py --cell 120,120"},
    {"seat": "BENCH", "event": "verify", "id": J["built"], "result": "fail", "sha": "abcd1002", "tsn": 333,
     "config": "relentless-live: python.exe jawa_shallows_proof.py --cell 120,120"},
    {"seat": "BENCH", "event": "close", "id": J["own"], "sha": "abcd1003", "tsn": 334,
     "reason": "relentless: blind PASS at abcd1003: the gate takes the ms bound on the best of 3 attempts"},
    {"seat": "BENCH", "event": "note", "id": J["nochange"], "tsn": 335, "text": "Both findings PLAUSIBLE and both need "
     "the live game; no code change to drawing. Live row B13 added to validation.py."},
    {"seat": "BENCH", "event": "close", "id": J["nochange"], "sha": "abcd1004", "tsn": 336, "why": "the live pass on "
     "current code: proof_all core block B13_hidden_conduit_hookup_not_drawn PASS (printed [0,0], moved 0)"},
    {"seat": "BENCH", "event": "implemented", "id": J["boiler"], "sha": "abcd1005", "tsn": 337},
    {"seat": "BENCH", "event": "verify", "id": J["boiler"], "result": "pass", "sha": "abcd1005", "tsn": 338,
     "config": "min-15", "criterion": "A1", "level": "L2"},
    {"seat": "BENCH", "event": "close", "id": J["later"], "sha": "abcd1006", "tsn": 339, "why": "moat built"},
    {"seat": "BENCH", "event": "close", "id": J["subj"], "sha": "abcd1016", "tsn": 340},
    {"seat": "OWNER", "event": "note", "id": J["shove"], "tsn": 341, "ownerSaid": "Melee shove into a vent pit is a "
     "great idea, but it belongs in OtherMod, not here. Drop this recommendation from FixtureMod."},
    {"seat": "OWNER", "event": "note", "id": J["said"], "tsn": 342, "ownerSaid": LONG_SAID}]
for e_ in EV3:
    with open(os.path.join(root, "infrastructure", "state", "ledger", "events", "%s.jsonl" % (
            "OWNER" if e_["seat"] == "OWNER" else "BENCH")), "a", encoding="utf-8") as fh:
        fh.write(json.dumps(e_) + "\n")
READ_EXTRA = {
    J["twin"]: {"causes_refuted": [{"text": "A6 (cache key misses BlockKind) refuted offline: the incremental result "
                                            "equals the fresh result."}]},
    J["own"]: {"traps": [{"text": "GraphWorker (1) always ends in a quiet map, so it never exercises sustained change; "
                                  "GraphWorker (3) bounds wall-clock ms and can flake on a loaded machine.",
                          "where": "FixtureGates.cs GraphWorker (1) and (3)"}]},
    J["unrun"]: {"traps": [{"text": "Scenes sc_a and sc_b are recorded UNRUN in version/test_table.json; nothing has "
                                    "run in game, so runnable does not mean passing.", "where": "test_table.json"}]},
    J["status"]: {"traps": [
        {"text": "walk_storeroom_raid is still unwritten (validation.py::walk_storeroom_raid). It is held by "
                 "walk_bars_confirmed, which waits for --steward-confirms.", "where": "validation.py"},
        {"text": "The game copy still holds Patches/RM_Fixture_Closed.xml, which tags the lockers closed; deploy "
                 "first.", "where": "game copy Patches"},
        {"text": "The census reads a cached count, so a green census says nothing about this tick.", "where": "census"},
        {"text": "11 vs 7 was a harness defect: the census ran while shell 1's wave was still spreading.",
         "where": "census"}]},
    J["shove"]: {"traps": [{"text": "The melee shove into a vent pit contest is not part of this mod; it belongs to "
                                    "OtherMod.", "where": "design"}]},
    J["doc"]: {"traps": [{"text": "The decision doc once said the engine was only an agent recommendation; that text "
                                  "was false and removed. The owner chose local_inertial_frcap by card 2026-11-14.",
                          "where": "design/specs/water.md"}]},
    J["run5"]: {"traps": [{"text": "The modcheck run5 core replay PASSED S5 once after the run4 fail, but the ticket is "
                                   "not closed until validation_v2 --live --fresh-map passes it again. The run4 probe "
                                   "ran with sticky back ON, so it reflects the later setting.", "where": "run4"}]},
    J["later"]: {"causes_refuted": [
        {"text": "The live8 FAIL MOD on LOWER_ONLY_FROM_WINCH was later resolved: the belt run passed 12/12."},
        {"text": "Stale reachability masks: spawn and despawn bump the climb generation, so a stale mask lasts one "
                 "tick at most."}]},
    J["subj"]: {"changed": "Fixed in abcd1016; the record does not say how."}}
w(os.path.join(v, "test_table.json"), {"made": "2026-11-14", "tests": {"sc_b": {"command": "runner.py --scenes sc_b"}},
                                       "bars": json.load(open(os.path.join(v, "test_table.json")))["bars"]})
_states0 = getattr(B, "rimflow_states", None)       # the test stands in for rimflow's fold on one ticket
if _states0:
    B.rimflow_states = lambda root_, names, tev: dict(_states0(root_, names, tev), **{RO: "ready"})
before = {}
for d, _, fs in os.walk(c):
    for f in fs:
        p = os.path.join(d, f)
        before[p] = hashlib.sha256(open(p, "rb").read()).hexdigest()

# an old backfill line the standard now refuses, written before the re-run (a pasted log, an untyped ref)
M.append(root, MOD, "DISPATCH", "version.open", "version", body={"version": "0.1.0"}, version="0.1.0")
oldp = M.shard_path(root, MOD, "BACKFILL")
with open(oldp, "w", encoding="utf-8") as fh:
    fh.write(json.dumps({"id": M.derive_id("BACKFILL", "old1"), "key": "old1", "ts": "2026-11-15T20:00:00Z", "tsn": 1,
                         "mod": MOD, "version": "0.1.0", "writer": "BACKFILL", "run": None, "kind": "note",
                         "subject": "FAULT_ONE", "body": {"text": "fault status NOTED\n  at Verse.X.Y()"},
                         "evidence": ["see the log"]}) + "\n")
res = B.run(root, MOD)
check("backfill writes events", res["written"] > 0, res)
check("the re-run deletes the old line the standard refuses (delete on sight, not grandfathered)",
      res["deleted"] == 1 and not [e for e in M.read(root, MOD) if e.get("key") == "old1"], res)
check("nothing the plan holds is refused by the standard on the fixture", res["refused"] == [], res["refused"])
check("the report names what it left out on purpose", any("no mod sha" in n for n in res["notes"]) and
      any("repeat the blind fault" in n for n in res["notes"]) and any("derived per-bar" in n for n in res["notes"]),
      res["notes"])
check("the fixture holds a near-duplicate pair kept with --new-subject", len(res["near_duplicates"]) >= 1, res)
before_bytes = open(oldp, "rb").read()
res2 = B.run(root, MOD)
check("a second backfill writes nothing (idempotent)", res2["written"] == 0 and res2["already"] == res["written"]
      and res2["deleted"] == 0, res2)
res3 = B.run(root, MOD)
check("a third backfill writes and deletes nothing either: a line kept with --new-subject is one the plan holds",
      res3["written"] == 0 and res3["deleted"] == 0 and res3["refused"] == [], res3)
check("a re-run keeps the lines it still holds byte for byte", open(oldp, "rb").read() == before_bytes)
after = {p: hashlib.sha256(open(p, "rb").read()).hexdigest() for p in before}
check("shadow mode: every old file is unchanged byte for byte", after == before)
evs = M.read(root, MOD)
bevs = [e for e in evs if e["_shard"] == "BACKFILL"]


def cited(e):
    r = [x for x in e["evidence"] if x.startswith("path:")] or [""]
    return os.path.exists(os.path.join(root, re.sub(r"(#.*|:\d+)$", "", r[0][5:])))


def std_probs(e):
    return M.check_entry("BACKFILL", e["kind"], e["subject"], e["body"], e["evidence"], e.get("code_sha"),
                         e.get("authority"), root)


check("every backfilled event cites an existing old file (a typed path: ref)", bevs and all(cited(e) for e in bevs),
      [e["evidence"] for e in bevs if not cited(e)])
check("every backfilled event passes the standard's shape checks", all(not std_probs(e) for e in bevs),
      [(e["subject"], str(std_probs(e)[:1])) for e in bevs if std_probs(e)])
check("no derived per-bar test summary and no empty checkpoint are mined",
      not [e for e in bevs if e["kind"] in ("test.run", "session.checkpoint")], [e["kind"] for e in bevs])
st = M.reduce(evs)
check("stage and version come from the stage record and VERSION.json", st["stage"] == "offline_build" and
      st["version"] == "0.1.0", (st["stage"], st["version"]))
check("bars: two locked, bar_a's verdict from the last live row, on its sha", len(st["bars"]) == 2 and
      st["bars"]["bar:bar_a"]["verdict"] == "PASS" and [t["sha"] for t in st["tests"] if t["subject"] == "bar:bar_a"]
      == ["def5678"], (st["bars"], st["tests"]))
f1 = st["findings"].get("finding:RIMMANDRAKE_STOP_FIXTURE_RAY_AT_WALL_CELL") or {}
check("a FIXED fault stays open as claimed, its smallest_fix as the proposed fix, its criterion as accept",
      f1.get("status") == "claimed_fixed" and "impassable" in (f1.get("proposed_fix") or "") and
      "stops at a wall" in (f1.get("accept") or "") and f1.get("code_sha") == "abc1234", f1)
check("an item that only repeats a fault mines no second finding.open",
      len([e for e in bevs if e["kind"] == "finding.open" and
           e["subject"] == "finding:RIMMANDRAKE_STOP_FIXTURE_RAY_AT_WALL_CELL"]) == 1)
f2 = st["findings"].get("finding:RIMMANDRAKE_POINT_FIXTURE_FIX_AT_A_REFERENCE") or {}
check("a pointer-sized smallest_fix is kept and labelled, not padded", (f2.get("proposed_fix") or "").startswith("K-1 ")
      and "pointer" in f2["proposed_fix"], f2)
check("the item naming the mod is a finding with its spec as the fix, the other mod's is not",
      "file: Source/A.cs" in (st["findings"].get("finding:RIMMANDRAKE_FIX_FIXTUREMOD_THING_ONE") or {}).get(
          "proposed_fix", "") and "selftest_a.py" in (st["findings"]["finding:RIMMANDRAKE_FIX_FIXTUREMOD_THING_ONE"].get(
              "accept") or "") and "finding:RIMMANDRAKE_FIX_OTHER_MOD_THING" not in st["findings"], sorted(st["findings"]))
check("an item named for another mod that only cites this one is not mined",
      "finding:RIMMANDRAKE_BACKFILL_OTHERMOD_LEDGER_LIKE_THE_FIRST" not in st["findings"], sorted(st["findings"]))
check("an item's text is its filer's one-line title, not its boilerplate first paragraph",
      (st["findings"].get("finding:RIMMANDRAKE_FLING_FIXTUREMOD_STEP_TWO") or {}).get("text") == "Goods fly 1.6x a person",
      st["findings"].get("finding:RIMMANDRAKE_FLING_FIXTUREMOD_STEP_TWO"))
check("his words count as his answers, a wrapped bullet joined", any("Shelves are open, period." in a["answer"]
                                                                    for a in st["answers"].values()), st["answers"])
check("the views exist and the mod ledger lints clean", M.lint(root, MOD, None)[0] == [], M.lint(root, MOD, None)[0])
rows = {r[0]: r for r in B.compare(root, MOD)}
check("compare: the stage agrees with the stage record", rows["stage (version/stage_record.json)"][3])
check("compare: a journal claiming every scene UNRUN against live rows is a DIFF",
      rows["journal.md stands: in-game scenes"][3] is False, rows["journal.md stands: in-game scenes"])
_fx = rows["blind faults marked FIXED in faults.json"]
check("compare: the FIXED-faults row counts the blind faults, not every claimed ticket", _fx[1] == 3 and
      "3 claimed_fixed" in str(_fx[2]), _fx)
F = st["findings"]
lo = [e for e in bevs if "item:" + LO in e["evidence"]]
check("a ticket with no prose file is mined from its rimflow events: its title as the finding, its close as claimed "
      "fixed; its claim and narration never", sorted(e["kind"] for e in lo) == ["finding.claimed_fixed",
                                                                              "finding.open"] and
      (F.get("finding:" + LO) or {}).get("text", "").startswith("FixtureMod sc_gas FAIL") and
      (F.get("finding:" + LO) or {}).get("code_sha") == "abcdef90", [(e["kind"], e["body"]) for e in lo])
check("a ledger-only ticket cites the shard line its file event sits on first (the old file the oracle checks)",
      bool(lo) and all(e["evidence"][0].startswith("path:infrastructure/state/ledger/events/BENCH.jsonl:") for e in lo),
      [e["evidence"][0] for e in lo])
check("an open ledger-only ticket whose title leads with the mod is an open finding; a Polish title is polish",
      (F.get("finding:" + LP) or {}).get("status") == "open" and (F.get("finding:" + LP) or {}).get("class") == "polish",
      F.get("finding:" + LP))
check("a superseded ledger-only ticket mines nothing (never left looking open)", "finding:" + LS not in F, sorted(F))
check("a title that cites the mod mid-sentence, a mining ticket about its ledger, and a closed ticket that mentions it "
      "in passing are not its findings", not [t for t in (LX, LM, LG) if "finding:" + t in F],
      [t for t in (LX, LM, LG) if "finding:" + t in F])

txt, info = M.packet(root, MOD)
check("his words are printed once in the packet (his answers), not again under decisions",
      txt.count("Shelves are open, period.") == 1, txt.count("Shelves are open, period."))
check("the packet prints under budget and ends with what it left out", info["tokens"] <= info["budget"] and
      "## Left out" in txt, info)

F = st["findings"]
TEST = {e["subject"]: e["body"].get("test") or "" for e in bevs if e["kind"] == "finding.claimed_fixed"}
fc = F.get("finding:RIMMANDRAKE_FIX_FIXTUREMOD_CLOSED_BY_A_FIX") or {}
check("a list-shaped red record is read (its last red command and rc)",
      "selftest_census.py" in TEST.get("finding:RIMMANDRAKE_RESET_FIXTURE_STATICS_CENSUS_CAUGHT", ""), TEST)
check("a closed ticket is mined: its finding, and its close with a verify pass as verified on the close sha, the verify "
      "command named", fc.get("status") == "verified" and fc.get("code_sha") == "abcdef12" and "selftest_b.py" in
      " ".join(e["body"]["text"] for e in bevs if e["kind"] == "finding.verified" and
               e["subject"] == "finding:RIMMANDRAKE_FIX_FIXTUREMOD_CLOSED_BY_A_FIX") and
      "Source/B.cs" in (fc.get("proposed_fix") or "") and fc.get("text") == "Arcs overshoot walls", fc)
fw = F.get("finding:RIMMANDRAKE_READ_FIXTUREMOD_NO_DEFECT_AFTER_ALL") or {}
check("a close with no code is a withdrawal by reading, on its sha", fw.get("status") == "withdrawn" and
      fw.get("how_checked") == "reading", fw)
check("a closed ticket whose closing cannot be stated (a drop with no sha) mines nothing and is counted, never left "
      "looking open", "finding:RIMMANDRAKE_DROP_FIXTUREMOD_FILED_TWICE" not in F and
      any("closed tickets" in n and "no sha" in n for n in res["notes"]), res["notes"])
fi = F.get("finding:RIMMANDRAKE_BUILD_FIXTUREMOD_IMPLEMENTED_NOT_CLOSED") or {}
check("a live ticket marked implemented is claimed_fixed on that sha", fi.get("status") == "claimed_fixed" and
      fi.get("code_sha") == "abcdef56", fi)
check("a ticket with no item file is mined from its rimflow events (most tickets have none), and counted",
      (F.get("finding:FIXTUREMOD_OLD_TICKET_WITH_NO_FILE_1") or {}).get("text") == "ledger-only" and
      any(re.search(r"\b\d+ of them with no item file", n) for n in res["notes"]), res["notes"])
check("a pipeline ticket about the mod (a backfill) is not a finding in it",
      "finding:RIMMANDRAKE_BACKFILL_FIXTUREMOD_LEDGER_IN_SHADOW" not in F, sorted(F))
check("a closed ticket of another concept (SlackMaster) is not mined",
      "finding:RIMMANDRAKE_FIX_SLACKMASTER_POST_AS_RIGHT_TEAM" not in F, sorted(F))
mined_items = [e for e in bevs if any(r == "item:RIMMANDRAKE_FIX_FIXTUREMOD_CLOSED_BY_A_FIX" for r in e["evidence"])]
check("lifecycle is never mined: the claim and the verify make no event of their own",
      sorted(e["kind"] for e in mined_items) == ["cause.refuted", "decision", "finding.open", "finding.verified"],
      sorted(e["kind"] for e in mined_items))
cr = [e for e in bevs if e["kind"] == "cause.refuted" and
      e["body"]["finding"] == "finding:RIMMANDRAKE_FIX_FIXTUREMOD_CLOSED_BY_A_FIX"]
check("a 'False theory:' note is a refuted cause on its finding, with the sha and path it names",
      len(cr) == 1 and cr[0]["body"]["finding"] == "finding:RIMMANDRAKE_FIX_FIXTUREMOD_CLOSED_BY_A_FIX" and
      cr[0]["code_sha"] == "5555eee" and cr[0]["body"]["depends_on"] == ["src/RimMandrake/FixtureMod/Source/B.cs"]
      and "pool fix" in cr[0]["body"]["text"], [e["body"] for e in cr])
check("every mined ticket event cites item:<ticket>", all(any(r.startswith("item:") for r in e["evidence"])
      for e in bevs if e["kind"] in ("finding.claimed_fixed", "finding.withdrawn", "cause.refuted")))
tr = [e for e in bevs if e["kind"] == "trap.noted" and e["evidence"][0].startswith("path:design/")]
check("the journal's oddities are traps, one each, a wrapped line joined, the first backticked name as where",
      len(tr) == 2 and tr[1]["body"]["where"] == "AerialSettings.fallenWireShock" and "shockReach" in tr[1]["body"]["text"],
      [e["body"] for e in tr])
check("his long words that overflow the line are fitted to it (whole deciding sentences kept, no marker, the ref for "
      "the whole), not refused", any(e["kind"] == "decision" and (e["body"].get("said") or "").startswith("Arc number 0")
                                     and e["body"]["said"].endswith("always.") and "[…]" not in e["body"]["said"]
                                     for e in bevs), [e["body"] for e in bevs if e["kind"] == "decision"])
pump = F.get("finding:RIMMANDRAKE_FIX_FIXTUREMOD_REBASED_PUMP_FIX") or {}
check("a close on a pre-landing sha (rewritten by ./publish) is claimed on its landed twin, naming both",
      pump.get("status") == "claimed_fixed" and pump.get("code_sha") == "abc7777" and
      [e for e in bevs if e["kind"] == "finding.claimed_fixed" and "beef123" in e["body"]["text"] and
       "sha:abc7777" in e["evidence"]], pump)
fen = F.get("finding:RIMMANDRAKE_FIX_FIXTUREMOD_FENCED_SPEC_PASTE") or {}
check("a spec holding a pasted traceback mines its words, cut at the paste", fen.get("proposed_fix") ==
      "FixtureMod: guard the null def.", fen)
check("a fault's class under 'cls' is read", (F.get("finding:RIMMANDRAKE_TRIM_FIXTURE_VALVE_ON_EXACT_FIT") or {}).get(
    "class") == "polish", F.get("finding:RIMMANDRAKE_TRIM_FIXTURE_VALVE_ON_EXACT_FIT"))
check("his words on a closed ticket's ledger event become a decision on that finding",
      any(e["kind"] == "decision" and e["subject"] == "finding:RIMMANDRAKE_READ_FIXTUREMOD_NO_DEFECT_AFTER_ALL"
          for e in bevs), [(e["kind"], e["subject"]) for e in bevs if e["kind"] == "decision"])

# --- the independent judges' six rules (RIMMANDRAKE_FIX_MINER_JUDGE_FAILED_SLACK_EIGHT_OF_TWENTY) ---
def on(t, kinds=None):
    return [e for e in bevs if "item:" + t in e["evidence"] and (kinds is None or e["kind"] in kinds)]


TEXTS = ("text", "proposed_fix", "accept", "test")
fs = F.get("finding:" + RS) or {}
check("rule 1: a done ticket with a verify pass is verified, on the original fix sha, never the bulk re-stamp",
      fs.get("status") == "verified" and fs.get("code_sha") == "abcd0011" and
      not [e for e in on(RS) if "not closed" in json.dumps(e["body"])], (fs, [e["body"] for e in on(RS)]))
check("rule 1: a ticket implemented and then reopened (rimflow state ready) is open, with no claim of a fix",
      (F.get("finding:" + RO) or {}).get("status") == "open" and not on(RO, ("finding.claimed_fixed",)),
      [(e["kind"], e["body"]) for e in on(RO)])
CR = [e for e in bevs if e["kind"] in ("cause.refuted", "trap.noted") and any(r.startswith("item:") for r in e["evidence"])]
for t, phrase in ((RC, "ladder is placed right"), (RC, "stale DLL was not the cause"), (RC, "fault was in the test setup"),
                  (RT, "Correction: the A1"), (RT, "game_fail at"), (RT, "wrapper exits 1"),
                  (RT, "reads the 7 oracle scenes")):
    check("rule 2: '%s' is mined as a ruled-out cause or a trap citing its ticket" % phrase,
          any(phrase in e["body"]["text"] and "item:" + t in e["evidence"] for e in CR),
          [(e["kind"], e["body"]["text"][:80]) for e in on(t)])
DEC = [e for e in bevs if e["kind"] == "decision"]
for phrase in ("work that item right now", "What should happen to FOUNDRY", "Frozen items shut down",
               "Stop all the lanes tonight"):
    check("rule 3: his words on a needs/reassign/stop/fleet-wide event are no decision ('%s')" % phrase,
          not [e for e in DEC if phrase in json.dumps(e["body"], ensure_ascii=False)],
          [e["body"] for e in DEC if phrase in json.dumps(e["body"], ensure_ascii=False)])
check("rule 3: his words on another ticket that only cites the mod, and do not name it, are no decision",
      not [e for e in DEC if "track quota" in (e["body"].get("said") or "")], [e["body"] for e in DEC])
check("rule 3: his words on another ticket that name the mod stay a decision",
      any("score far above OtherMod" in (e["body"].get("said") or "") for e in DEC), [e["body"] for e in DEC])
check("rule 3: his words about the mod on a plain note stay a decision",
      any("chain through every vent" in (e["body"].get("said") or "") for e in DEC), [e["body"] for e in DEC])
FW = F.get("finding:RIMMANDRAKE_WIDEN_FIXTURE_SCAN_FIVE_SLIPPED") or {}
cw = on("RIMMANDRAKE_WIDEN_FIXTURE_SCAN_FIVE_SLIPPED", ("finding.claimed_fixed",))
check("rule 4: a blind fault's text is its defect line, its accept the would_pass",
      "fixed tag list" in (FW.get("text") or "") and "lane2/planted" not in (FW.get("text") or "") and
      "turns T1 red by name" in (FW.get("accept") or ""), FW)
check("rule 4: a fixed fault's claim says what changed, never 'fixed by the blind cycle's fixer'",
      cw and "element's text and tag" in cw[0]["body"]["text"] and "blind cycle's fixer" not in cw[0]["body"]["text"],
      [e["body"] for e in cw])
ff = F.get("finding:" + RF) or {}
check("rule 4: a ticket's proposed fix is its Fix: line and its accept its criterion, never found-by or Producer prose",
      (ff.get("proposed_fix") or "").startswith("record which faction") and "selftest_theft.py" in (ff.get("accept") or "")
      and not re.search(r"found-by|Producer", (ff.get("proposed_fix") or "") + (ff.get("accept") or "")), ff)
fk = F.get("finding:" + RK) or {}
ck = on(RK, ("finding.claimed_fixed", "finding.verified"))
check("rule 4: the acceptance test a ledger-only ticket filed is its accept",
      "runner.py --scenes sc_storeroom" in (fk.get("accept") or ""), fk)
check("rule 4: a close's claim names the cause it fixed, with no 'Closed at X by Y:' history",
      ck and "MassScale caps" in ck[0]["body"]["text"] and not ck[0]["body"]["text"].startswith("Closed at"),
      [e["body"] for e in ck])
check("rule 4: no proposed fix or claim anywhere is found-by provenance",
      not [e for e in bevs if re.match(r"(?i)\s*found[- ]by\b", e["body"].get("proposed_fix") or "") or
           "blind cycle's fixer" in (e["body"].get("text") or "")])
check("rule 5: comma-listed bars split into the locked bar ids", FW.get("bars") == ["bar_a", "bar_b"], FW)
cut = [(e["subject"], f) for e in bevs for f in TEXTS if "[…]" in str(e["body"].get(f) or "") or
       "[...]" in str(e["body"].get(f) or "")]
check("rule 6: no text, fix, accept or test is cut with a '[…]' marker", not cut, cut)
fl = F.get("finding:" + RL) or {}
check("rule 6: a long spec is fitted to whole sentences", (fl.get("proposed_fix") or "").endswith("valve opens.") and
      len(fl.get("proposed_fix") or "") <= 320, fl.get("proposed_fix"))

# an older mine of the same fact with other evidence: the re-run must keep the fact (the old line held, or the new one
# written), never delete the old and refuse the new as 'restates' (Gimme Some Slack lost 5 facts so, 2026-11-16)
t0 = tr[0]
M.delete(root, MOD, [t0["id"]])
M.append(root, MOD, "BACKFILL", t0["kind"], t0["subject"], body=t0["body"], version="0.1.0",
         evidence=["path:design/concepts/FixtureMod/journal.md"], views=False)
rs_ = B.run(root, MOD)
check("a re-mine keeps a fact an older mine wrote with other evidence (no 'restates' refusal, the fact still there)",
      not [r for r in rs_["refused"] if "restates" in r[2]] and
      [e for e in M.read(root, MOD) if e["subject"] == t0["subject"] and e["body"].get("text") == t0["body"]["text"]],
      rs_["refused"])

# the per-ticket reading (claude -p, faked here): its words replace the sentence rules', never its state; a bad bar or
# path is dropped; the dollar bound stops new batches; the committed readings carry a re-run without --read
import modledger_reader as R                                     # noqa: E402
CALLS = []


def fake_call(prompt, model, system=None):
    CALLS.append(prompt)
    ans = {}
    for n in re.findall(r"=== TICKET (\S+)", prompt):
        ans[n] = {"defect": "Reading: %s is wrong" % n, "proposed_fix": "Reading: change the thing", "accept":
                  "selftest_read.py exit 0", "class": "problem", "bars": ["bar_a", "not_a_bar"], "changed": None,
                  "causes_refuted": [{"text": "Reading: the DLL was not stale for %s" % n, "depends_on":
                                      ["src/RimMandrake/NoSuchMod/X.cs"]}],
                  "traps": [{"text": "Reading: T_GEOM reads seven scenes only (%s)" % n, "where": "T_GEOM"},
                            {"text": "Reading: helper notes sit on branch ralph (%s)" % n, "where": "branch ralph"}]}
        if n in READ_EXTRA:
            x_ = READ_EXTRA[n]
            ans[n] = dict(ans[n], **{k: (x_[k] + ans[n][k]) if isinstance(ans[n].get(k), list) else x_[k] for k in x_})
    for n, block in re.findall(r"=== KEEP (\S+)\n(.*?)(?=\n=== |\Z)", prompt, re.S):
        ans[n] = [int(i) for i, w in re.findall(r"^\[(\d+)\] (.*)$", block, re.M) if "branch ralph" not in w]
    for n, block in re.findall(r"=== OWNER WORDS (\S+)\n(.*?)(?=\n=== |\Z)", prompt, re.S):
        ans[n] = [int(i) for i, w in re.findall(r"^\[(\d+)\] (.*)$", block, re.M) if "vent" in w]
    return ans, 0.5


R.CALL = fake_call
_lines = lambda: {json.loads(l)["id"]: l for l in open(oldp, encoding="utf-8") if l.strip()}
pre_ = _lines()
rr = B.run(root, MOD, read=True, budget_usd=0.6)
rnote = [n for n in rr["notes"] if n.startswith("reader:")]
check("reader: the dollar bound stops new batches (one 0.50 batch under a 0.60 bound) and the spend is reported",
      len(CALLS) == 1 and rnote and "$0.50 spent" in rnote[0], (len(CALLS), rnote))
R.BATCH_CHARS_SAVED = R.BATCH_CHARS
CALLS.clear()
rr = B.run(root, MOD, read=True, budget_usd=100)
post_ = _lines()
check("reader: a line re-ordered after a re-read finding is a new id, never an old id changed in place (lint "
      "EDITED_IN_PLACE)", not [i for i in pre_ if i in post_ and pre_[i] != post_[i]],
      [i for i in pre_ if i in post_ and pre_[i] != post_[i]][:3])
evr = [e for e in M.read(root, MOD) if e["_shard"] == "BACKFILL"]
Fr = M.reduce(M.read(root, MOD))["findings"]
fr = Fr.get("finding:" + RC) or {}
check("reader: a read ticket's defect, fix, accept and bars come from its reading; a bar not locked is dropped",
      fr.get("text") == "Reading: %s is wrong" % RC and fr.get("accept") == "selftest_read.py exit 0" and
      fr.get("bars") == ["bar_a"], fr)
check("reader: a read ticket keeps its rimflow state and sha (a reading supplies words, never state)",
      fr.get("status") == "claimed_fixed" and fr.get("code_sha") == "abcd0033", (fr, rr["refused"]))
rc_ = [e for e in evr if "item:" + RC in e["evidence"] and e["kind"] in ("cause.refuted", "trap.noted")]
check("reader: its ruled-out causes and traps are mined, a path that does not exist dropped from depends_on",
      any(e["kind"] == "cause.refuted" and e["body"]["text"].startswith("Reading: the DLL") and
          "NoSuchMod" not in json.dumps(e["body"]["depends_on"]) for e in rc_) and
      any(e["kind"] == "trap.noted" and e["body"]["where"] == "T_GEOM" for e in rc_), [e["body"] for e in rc_])
check("reader: the readings are committed beside the miner, one per ticket, with the record hash",
      os.path.exists(B.readings_path(root, MOD)) and RC in B.load_readings(root, MOD) and
      B.load_readings(root, MOD)[RC].get("hash"), B.readings_path(root, MOD))
CALLS.clear()
rr2 = B.run(root, MOD)
check("reader: a re-run without --read keeps every read line (no call, nothing written or deleted)",
      not CALLS and rr2["written"] == 0 and rr2["deleted"] == 0, rr2)
TRr = [e["body"]["text"] for e in M.read(root, MOD) if e["_shard"] == "BACKFILL" and e["kind"] == "trap.noted"]
check("keep reading: a trap it finds would change nothing a holder does (agent-process trivia) is not mined; the "
      "instrument trap is", not [t for t in TRr if "branch ralph" in t] and [t for t in TRr if "T_GEOM reads" in t],
      [t for t in TRr if "Reading" in t][:4])
DECr = [e["body"].get("said") or "" for e in M.read(root, MOD) if e["_shard"] == "BACKFILL" and e["kind"] == "decision"]
check("owner reading: on a read ticket only his words it marks as a ruling about the mod stay decisions",
      any("chain through every vent" in x for x in DECr) and not any("staying interactive" in x for x in DECr), DECr)
# --- the round-2 judge's rulings, one check each (GSS = Gimme Some Slack, EK = Explosive Knockback, FW = FlowWorks) ---
ALL = [e for e in M.read(root, MOD) if e["_shard"] == "BACKFILL"]
Fj = M.reduce(M.read(root, MOD))["findings"]


def onj(k, kinds=None):
    return [e for e in ALL if "item:" + J[k] in e["evidence"] and (kinds is None or e["kind"] in kinds)]


def texts(k, kinds):
    return [e["body"].get("text") or "" for e in onj(k, kinds)]


cz = [t for t in texts("twin", ("cause.refuted",)) if t.startswith("A6")]
check("judge GSS 3 (rule 5): one ruled-out cause per hypothesis on a ticket: the regex 'A6 refuted' line beside the "
      "reading's A6 is not mined", len(cz) == 1 and "BlockKind" in cz[0], cz)
cb = onj("built", ("finding.claimed_fixed",))
check("judge GSS 96 (rule 4): a lifecycle reason ('relentless: …') is no fix text; a bookkeeping commit's subject is no "
      "fix either: the claim states the build and its failed live verifies, its test the command they ran",
      cb and not cb[-1]["body"]["text"].startswith("relentless") and "lesson:" not in cb[-1]["body"]["text"] and
      "FAIL 2 times" in cb[-1]["body"]["text"] and "jawa_shallows_proof.py" in cb[-1]["body"]["test"],
      [e["body"] for e in cb])
check("judge GSS 257 (rule 1): a trap restating the defect its ticket's fix removed is not mined",
      not [t for t in texts("own", ("trap.noted",)) if "GraphWorker" in t], texts("own", ("trap.noted",)))
fn = Fj.get("finding:" + J["nochange"]) or {}
check("judge GSS 259 (rule 3): done, 'no code change', closing rows PASS -> withdrawn after a test, never claimed fixed",
      fn.get("status") == "withdrawn" and fn.get("how_checked") == "test" and
      not onj("nochange", ("finding.claimed_fixed",)), fn)
tb = texts("boiler", ("finding.verified",))
check("judge GSS 321 (rule 4): 'the record names no change' gives way to the landed commit's subject, and the verify "
      "names its criterion and level, not only the mod list", tb and "own-faction transmitter" in tb[-1] and
      "names no change" not in tb[-1] and "A1 L2 PASS" in tb[-1], tb)
check("judge GSS 325: a pipeline work order ('Maturation Pipeline: take …') mines no finding",
      not onj("order", ("finding.open",)), [e["body"] for e in onj("order")])
check("judge GSS 331: a blind challenge cycle ticket mines no finding", not onj("cycle", ("finding.open",)),
      [e["body"] for e in onj("cycle")])
st_j = M.reduce(M.read(root, MOD))
lb_ = [t for t in st_j["tests"] if t["subject"] == "bar:bar_b" and t["kind"] == "live.run"]
check("judge EK 53 (rule 1): an UNRUN status line is no trap; the UNRUN scene of a bar with no live row becomes its "
      "live.run UNRUN with the scene's command, and a bar with live rows keeps them",
      not [t for t in texts("unrun", ("trap.noted",)) if "UNRUN" in t] and lb_ and lb_[-1].get("result") == "UNRUN" and
      st_j["bars"]["bar:bar_a"]["verdict"] == "PASS" and
      [e for e in ALL if e["kind"] == "live.run" and "runner.py --scenes sc_b" in e["body"]["command"]],
      (texts("unrun", ("trap.noted",)), lb_))
ts_ = texts("status", ("trap.noted",))
check("judge EK 54 (rule 1): 'still unwritten' and the 'It is held by …' sentence about it are no trap",
      not [t for t in ts_ if "walk_storeroom_raid" in t or "walk_bars_confirmed" in t], ts_)
check("judge EK 82 (rule 1): 'the game copy still holds …' is a deploy status, no trap",
      not [t for t in ts_ if "still holds" in t], ts_)
check("rule 1 control: an instrument trap and a past reading ('wave was still spreading') on the same ticket stay",
      [t for t in ts_ if "cached count" in t] and [t for t in ts_ if "wave was still spreading" in t], ts_)
check("judge EK 133: a trap restating his ruling on the same ticket is not mined (his words are the decision)",
      not [t for t in texts("shove", ("trap.noted",)) if "melee shove" in t.lower()] and
      [e for e in onj("shove", ("decision",)) if "Melee shove" in (e["body"].get("said") or "")],
      (texts("shove", ("trap.noted",)), [e["body"] for e in onj("shove", ("decision",))]))
check("judge FW 386: a doc correction already made and 'the owner chose … by card' are no trap",
      not [t for t in texts("doc", ("trap.noted",)) if "decision doc" in t or "owner chose" in t],
      texts("doc", ("trap.noted",)))
check("judge FW 690 (rule 1): a run result with a closing condition leaves the trap; only the probe-condition clause "
      "stays", "The run4 probe ran with sticky back ON, so it reflects the later setting." in
      texts("run5", ("trap.noted",)) and not [t for t in texts("run5", ("trap.noted",)) if "not closed until" in t],
      texts("run5", ("trap.noted",)))
cl_ = texts("later", ("cause.refuted",))
check("judge FW 74 (rule 2): 'later resolved' is a state change, never a ruled-out cause; a 'hypothesis: what refuted "
      "it' cause stays", not [t for t in cl_ if "later resolved" in t] and [t for t in cl_ if "Stale reachability" in t],
      cl_)
sd_ = [e["body"].get("said") or "" for e in onj("said", ("decision",))]
check("judge FW 13: his words past 600 chars keep his deciding sentences ('major fix', 'please ensure'), joined by "
      "' · ', never a leading cut with a marker", sd_ and "please ensure" in sd_[0] and "(major fix)" in sd_[0] and
      " · " in sd_[0] and "[…]" not in sd_[0] and len(sd_[0]) <= 600, sd_)
tsj = texts("subj", ("finding.claimed_fixed",))
check("judge FW 1028 (rule 4): a reading's 'the record does not say how' gives way to the landed commit's subject",
      tsj and tsj[-1].startswith("a late deep-swim toggle recomputes path costs"), tsj)
# rule 5: an earlier mining's line restating a fact in other words (a '[…]' cut) is replaced on the re-mine, not held
d0 = onj("shove", ("decision",))[0]
M.delete(root, MOD, [d0["id"]])
M.append(root, MOD, "BACKFILL", "decision", d0["subject"], body=dict(d0["body"], said=d0["body"]["said"] + " […]"),
         version="0.1.0", evidence=["path:design/concepts/FixtureMod/journal.md", "item:" + J["shove"]],
         authority={"owner_said": d0["body"]["said"] + " […]"}, views=False)
r5_ = B.run(root, MOD)
saids_ = [e["body"].get("said") for e in M.read(root, MOD) if e["_shard"] == "BACKFILL" and e["subject"] == d0["subject"]]
check("judge rule 5: a re-mine replaces an earlier mining's line that restates its fact in other words",
      d0["body"]["said"] in saids_ and not [x for x in saids_ if x and "[…]" in x] and not r5_["refused"],
      (saids_, r5_["refused"]))
subj_probs = [x for x in M.lint(root, MOD, None)[0] if "REFUSED subject" in str(x)]
check("re-mine: a subject whose old first line was deleted after the new lines were written still passes the "
      "duplicate-subject check (lint clean)", not subj_probs, subj_probs[:2])

# re-mine order (found re-mining the three pilots, 2026-11-16): an edited older stage move and a new one must leave the
# stage where the stage record says (ExplosiveKnockback read offline_build over its in_game), and a kept cause whose
# finding line is re-written must not sit before it (Gimme Some Slack lint REFUSED finding)
srp_ = os.path.join(v, "stage_record.json")
sr_ = json.load(open(srp_))
sr_["moves"][0]["why"] = "exit met, re-recorded"
sr_["moves"].append({"from": "offline_build", "to": "in_game", "at": "z", "by": "C", "why": "road back closed"})
sr_.update(stage="in_game", stage_label="In-game acceptance (Stage 6)", since="2026-11-16T01:18:11-08:00")
w(srp_, sr_)
fo_ = next(e for e in M.read(root, MOD) if e["_shard"] == "BACKFILL" and e["kind"] == "finding.open" and
           e["subject"] == "finding:RIMMANDRAKE_FIX_FIXTUREMOD_CLOSED_BY_A_FIX")
M.delete(root, MOD, [fo_["id"]])
M.append(root, MOD, "BACKFILL", "finding.open", fo_["subject"], body=dict(fo_["body"], text="Arcs overshoot walls, "
         "an earlier wording"), version="0.1.0", evidence=fo_["evidence"], views=False)
ro_ = B.run(root, MOD)
lint_ = M.lint(root, MOD, None)[0]
check("re-mine order: an edited older stage move and a new move leave the stage the stage record names",
      M.reduce(M.read(root, MOD))["stage"] == "in_game", (M.reduce(M.read(root, MOD))["stage"], ro_["refused"]))
check("re-mine order: a kept cause whose finding line was re-written is moved after it (lint has no REFUSED finding)",
      not [x for x in lint_ if "REFUSED finding" in str(x)] and not ro_["refused"],
      ([x for x in lint_ if "REFUSED finding" in str(x)][:2], ro_["refused"]))
ro2_ = B.run(root, MOD)
check("re-mine order: the repaired ledger is stable (the next run writes and deletes nothing)",
      ro2_["written"] == 0 and ro2_["deleted"] == 0 and not M.lint(root, MOD, None)[0], (ro2_, M.lint(root, MOD, None)[0]))

import modledger_sample as SMP                                   # noqa: E402
pop_, sm_ = SMP.draw(root, MOD, 7, 5)
check("sample: a seeded draw of ticket-mined entries, each with its ticket and the other entries mined from it",
      len(sm_) == 5 and sm_ == SMP.draw(root, MOD, 7, 5)[1] and all(x["source_tickets"] for x in sm_) and
      any(x["same_ticket_entries"] for x in sm_) and all(any(r.startswith("item:") for r in e["evidence"]) for e in pop_),
      [(x["kind"], x["source_tickets"]) for x in sm_])

_cr = tempfile.mkdtemp()
os.makedirs(os.path.join(_cr, "infrastructure", "state", "items", "closed"))
for _n, _d in (("OPEN_ONE.md", "items"), ("CLOSED_ONE.md", "items/closed")):
    open(os.path.join(_cr, "infrastructure", "state", _d, _n), "w").write("x\n")
_ok = lambda ref: M.cited_file_exists(_cr, ref)                  # noqa: E731
check("citation: an item file cited at items/ still resolves after the item closes and moves to items/closed/",
      _ok("path:infrastructure/state/items/OPEN_ONE.md") and _ok("path:infrastructure/state/items/CLOSED_ONE.md")
      and _ok("infrastructure/state/items/CLOSED_ONE.md#L3") and _ok("path:infrastructure/state/items/CLOSED_ONE.md:7")
      and not _ok("path:infrastructure/state/items/NEVER_FILED.md") and not _ok("path:infrastructure/state/other/CLOSED_ONE.md"))
shutil.rmtree(_cr, ignore_errors=True)

shutil.rmtree(root, ignore_errors=True)
print("selftest_modledger_backfill: %d failure%s" % (len(FAIL), "" if len(FAIL) == 1 else "s"))
sys.exit(1 if FAIL else 0)
