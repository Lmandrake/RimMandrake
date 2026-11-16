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
check("compare: the FIXED-faults row counts the blind faults, not every claimed ticket", _fx[1] == 2 and
      "2 claimed_fixed" in str(_fx[2]), _fx)
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
check("a closed ticket is mined: its finding, and its close as claimed_fixed on the close sha with the verify command",
      fc.get("status") == "claimed_fixed" and fc.get("code_sha") == "abcdef12" and "selftest_b.py" in TEST.get(
          "finding:RIMMANDRAKE_FIX_FIXTUREMOD_CLOSED_BY_A_FIX", "") and
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
      sorted(e["kind"] for e in mined_items) == ["cause.refuted", "decision", "finding.claimed_fixed", "finding.open"],
      sorted(e["kind"] for e in mined_items))
cr = [e for e in bevs if e["kind"] == "cause.refuted"]
check("a 'False theory:' note is a refuted cause on its finding, with the sha and path it names",
      len(cr) == 1 and cr[0]["body"]["finding"] == "finding:RIMMANDRAKE_FIX_FIXTUREMOD_CLOSED_BY_A_FIX" and
      cr[0]["code_sha"] == "5555eee" and cr[0]["body"]["depends_on"] == ["src/RimMandrake/FixtureMod/Source/B.cs"]
      and "pool fix" in cr[0]["body"]["text"], [e["body"] for e in cr])
check("every mined ticket event cites item:<ticket>", all(any(r.startswith("item:") for r in e["evidence"])
      for e in bevs if e["kind"] in ("finding.claimed_fixed", "finding.withdrawn", "cause.refuted")))
tr = [e for e in bevs if e["kind"] == "trap.noted"]
check("the journal's oddities are traps, one each, a wrapped line joined, the first backticked name as where",
      len(tr) == 2 and tr[1]["body"]["where"] == "AerialSettings.fallenWireShock" and "shockReach" in tr[1]["body"]["text"],
      [e["body"] for e in tr])
check("his long words that overflow the line are fitted to it (deciding sentences kept, the ref for the whole), not "
      "refused", any(e["kind"] == "decision" and "Arc number 0" in (e["body"].get("said") or "") and
                     e["body"]["said"].endswith("[…]") for e in bevs), [e["body"] for e in bevs if e["kind"] == "decision"])
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

shutil.rmtree(root, ignore_errors=True)
print("selftest_modledger_backfill: %d failure%s" % (len(FAIL), "" if len(FAIL) == 1 else "s"))
sys.exit(1 if FAIL else 0)
