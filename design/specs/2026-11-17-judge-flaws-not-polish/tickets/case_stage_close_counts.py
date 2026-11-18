#!/usr/bin/env python3
"""Failing acceptance cases for ticket RIMMANDRAKE_PRINT_JUDGE_COUNTS_WHEN_COVERAGE_CLOSES (owner by card 2026-11-17,
design/specs/2026-11-17-judge-flaws-not-polish/6_proposed_ruling_plain.md, "How it is built" step 5).

Four counts are printed when a mod's coverage stage closes (signed covered, or stopped): looks used; refusals and how
many were overturned; new demands on unchanged material; refusals citing a number or line the owner did not say.
Contract:
  SCHEMA: every gap carries `promise` (string: the owner's promise it rests on, quoted) and `owner_said` (boolean: every
    number and line the refusal binds on is in the owner's words), both required.
  record_round adds three integers to each stage.json coverage_rounds row:
    `new_on_unchanged` = gaps in gaps + advisory_gaps tagged `late`, plus len(rec["dropped"]);
    `overturned` = gaps in gaps + advisory_gaps with late_confirmed False, or whose criterion_verdict is flawed or
      unattainable while their judge_criterion_verdict is neither (the second reader overturned the judge);
    `not_owner_said` = blocking gaps (rec["gaps"]) with owner_said False.
  close_counts(st, d=None) -> {"looks", "refusals", "overturned", "new_on_unchanged", "not_owner_said"}: looks = rounds
    whose verdict is covered or not_covered; refusals = not_covered rounds; the other three summed over rounds (a round
    with no field counts 0). The owner's own overturns are not in the program's reach: close_line says so.
  close_line(counts) -> one line naming all four counts and "owner overturns: not counted"; run() appends it to its
    message when the verdict signs or judging stops.
Input kinds read: the schema; a round with each kind of gap (late, dropped, reader-overturned, late unconfirmed, a judge
confession, owner_said true/false/missing); a stage of a covered first look, of refusal then covered, of two refusals
(stopped), and of a malformed round between.
Run from the repo root:  python3 design/specs/2026-11-17-judge-flaws-not-polish/tickets/case_stage_close_counts.py
Prints every wrong case, then: cases read, wrong count (worst), limit 0. Exit 1 when any case is wrong."""
import os
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, *[".."] * 4))
sys.path.insert(0, os.path.join(ROOT, "src", "RimMandrake", "rimflow"))
import coverage_judge as CJ  # noqa: E402
import designer_stage as DS  # noqa: E402

wrong, n = [], 0


def expect(name, ok, got=""):
    global n
    n += 1
    if not ok:
        wrong.append("%s: got %s" % (name, got))


item = (CJ.SCHEMA.get("properties", {}).get("gaps", {}).get("items") or {})
props, req = item.get("properties") or {}, set(item.get("required") or [])
expect("schema: gap `promise` is a required string", (props.get("promise") or {}).get("type") == "string"
       and "promise" in req, (props.get("promise"), "promise" in req))
expect("schema: gap `owner_said` is a required boolean", (props.get("owner_said") or {}).get("type") == "boolean"
       and "owner_said" in req, (props.get("owner_said"), "owner_said" in req))


def g(**kw):
    return dict({"what": "w", "ids": ["a"], "new_since": "first", "severity": "problem", "owner_said": True}, **kw)


rec = {"judge": "j2", "at": "2026-11-17T00:00:00Z", "verdict": "not_covered", "tree": "t", "tokens": 1,
       "gaps": [g(owner_said=False), g(), g(new_since="late", miss_of="j1", late_confirmed=True),
                g(criterion_verdict="flawed", judge_criterion_verdict="sound"), g(owner_said=None)],
       "advisory_gaps": [g(new_since="late", miss_of="j1", late_confirmed=False),
                         g(criterion_verdict="unattainable", judge_criterion_verdict="unattainable")],
       "dropped": [g(), g()], "late": ["a"]}
with tempfile.TemporaryDirectory() as root:
    d = os.path.join(root, "X")
    os.makedirs(d)
    # record_round appends to the concept's stage.json, which every judged concept has (fixture fixed 2026-11-18: the
    # case first ran on a folder without one, so record_round could only raise; the assertions are unchanged)
    DS.write_json(os.path.join(d, "stage.json"), {"stage": 5, "status": "open", "item": "X_ITEM"})
    try:
        row = CJ.record_round(d, rec)["coverage_rounds"][-1]
    except Exception as e:   # noqa: BLE001 - a crash is a wrong case, not a stop
        row = {"crash": repr(e)}
for k, want in (("new_on_unchanged", 4), ("overturned", 2), ("not_owner_said", 1)):
    expect("record_round: %s" % k, row.get(k) == want, (row.get(k), "want %d" % want))

cc = getattr(CJ, "close_counts", None)
cl = getattr(CJ, "close_line", None)
expect("close_counts exists", callable(cc), "missing")
expect("close_line exists", callable(cl), "missing")


def stage(*rows):
    return {"coverage_rounds": [dict({"judge": "j%d" % i}, **r) for i, r in enumerate(rows)]}


CASES = (
    ("covered first look", stage({"verdict": "covered"}),
     {"looks": 1, "refusals": 0, "overturned": 0, "new_on_unchanged": 0, "not_owner_said": 0}),
    ("refusal then covered", stage({"verdict": "not_covered", "overturned": 1, "not_owner_said": 2},
                                   {"verdict": "covered", "new_on_unchanged": 1}),
     {"looks": 2, "refusals": 1, "overturned": 1, "new_on_unchanged": 1, "not_owner_said": 2}),
    ("two refusals, stopped", stage({"verdict": "not_covered", "not_owner_said": 1},
                                    {"verdict": "not_covered", "new_on_unchanged": 3, "not_owner_said": 1}),
     {"looks": 2, "refusals": 2, "overturned": 0, "new_on_unchanged": 3, "not_owner_said": 2}),
    ("a malformed round is not a look", stage({"verdict": "not_covered"}, {"verdict": "malformed"},
                                              {"verdict": "covered"}),
     {"looks": 2, "refusals": 1, "overturned": 0, "new_on_unchanged": 0, "not_owner_said": 0}),
)
for name, st, want in CASES:
    got = None
    if callable(cc):
        try:
            got = cc(st)
        except Exception as e:   # noqa: BLE001
            got = repr(e)
    expect("close_counts: %s" % name, isinstance(got, dict) and all(got.get(k) == v for k, v in want.items()),
           (got, want))
if callable(cl) and callable(cc):
    line = str(cl(cc(CASES[1][1])))
    for word in ("looks 2", "refusals 1", "overturned 1", "new demands on unchanged material 1",
                 "not in the owner's words 2", "owner overturns: not counted"):
        expect("close_line names %r" % word, word in line, line)

# Codex review 2026-11-18 (7d_codex_counts_review.md): what could not be measured is never a measured 0
rec2 = {"judge": "j3", "at": "2026-11-17T00:00:00Z", "verdict": "not_covered", "tree": "t", "tokens": 1,
        "gaps": [g(owner_said=None), g(new_since="unfixed", unplaced=True)],
        "advisory_gaps": [g(new_since="late", miss_of="j1", late_confirmed=False, criterion_by="program"),
                          g(new_since="late", miss_of="j1", passage="no_baseline"),
                          g(new_since="late", miss_of="j1", passage="unchanged")],
        "dropped": [g(names_slot=["g1"])]}
with tempfile.TemporaryDirectory() as root:
    d = os.path.join(root, "Y")
    os.makedirs(d)
    DS.write_json(os.path.join(d, "stage.json"), {"stage": 5, "status": "open", "item": "Y_ITEM"})
    try:
        row2 = CJ.record_round(d, rec2)["coverage_rounds"][-1]
    except Exception as e:   # noqa: BLE001
        row2 = {"crash": repr(e)}
for k, want in (("owner_said_unmeasured", 1), ("not_owner_said", 0), ("unplaced", 1), ("overturned", 0),
                ("new_on_unchanged", 2), ("new_unsettled", 1)):
    expect("record_round, unmeasured kinds: %s" % k, row2.get(k) == want, (row2.get(k), "want %d" % want))
if callable(cc):
    got = cc(stage({"verdict": "covered", "overturned": None, "new_on_unchanged": None, "not_owner_said": None}))
    expect("close_counts: null counts are an uncounted look, not zeros", got.get("uncounted_looks") == 1, got)
    st_l = {"coverage_rounds": [{"judge": "rm-coverage-judge-9", "verdict": "covered", "overturned": 0,
                                 "new_on_unchanged": 0, "not_owner_said": 0}],
            "budget": {"charges": [{"ref": "rm-coverage-judge-1", "kind": "review", "tokens": 3, "at": "a"}]}}
    got = cc(st_l)
    expect("close_counts: a legacy judge from the charges is a look, uncounted", got.get("looks") == 2
           and got.get("uncounted_looks") == 1, got)
if callable(cl):
    line = str(cl({"looks": 1, "refusals": 0, "overturned": 0, "new_on_unchanged": 0, "not_owner_said": 0,
                   "owner_said_unmeasured": 2, "uncounted_looks": 0}))
    expect("close_line names an unanswered owner_said as UNMEASURED", "UNMEASURED" in line, line)
# The fifth count (owner, 2026-11-17 ~6:50 PM PST, note on this ticket; RIMMANDRAKE_COUNT_REPAIR_PASSAGE_BLOCKS_FIFTH_
# MISSED_AT_CLOSE): second-look blocks raised on a repaired passage, per mod, each listed with the changed passage it quotes and
# the promise it says is not kept. A block is a gap in `gaps` (blocking), tagged late, carrying `repair_passage`; an
# advisory one, a late one quoting no repair, or one carried from an earlier round is not.
rec3 = {"judge": "j4", "at": "2026-11-17T00:00:00Z", "verdict": "not_covered", "tree": "t", "tokens": 1,
        "gaps": [g(gid="g7", new_since="late", miss_of="j3", late_confirmed=True, promise="walls stand in a storm",
                   repair_passage={"entry": "scene:sc_wall", "passage": "the wall holds under wind 3"}),
                 g(gid="g8", new_since="late", miss_of="j3", late_confirmed=True),
                 g(gid="g9", new_since="late", carried=True, promise="p",
                   repair_passage={"entry": "scene:sc_old", "passage": "an old repair"}),
                 g(gid="g10")],
        "advisory_gaps": [g(gid="g11", new_since="late", miss_of="j3", late_confirmed=False, promise="q",
                            repair_passage={"entry": "sheet:Wind", "passage": "wind bends"})]}
with tempfile.TemporaryDirectory() as root:
    d = os.path.join(root, "Z")
    os.makedirs(d)
    DS.write_json(os.path.join(d, "stage.json"), {"stage": 5, "status": "open", "item": "Z_ITEM"})
    try:
        row3 = CJ.record_round(d, rec3)["coverage_rounds"][-1]
    except Exception as e:   # noqa: BLE001
        row3 = {"crash": repr(e)}
rb = row3.get("repair_blocks")
expect("record_round: repair_blocks lists the one blocking late gap quoting a repaired passage",
       isinstance(rb, list) and len(rb) == 1 and rb[0].get("gid") == "g7", rb)
expect("record_round: a repair block keeps the passage it quotes and the promise",
       isinstance(rb, list) and rb and rb[0].get("passage") == "the wall holds under wind 3"
       and rb[0].get("entry") == "scene:sc_wall" and rb[0].get("promise") == "walls stand in a storm", rb)
rec4 = dict(rec3, judge="j5", gaps=[g(gid="g1")], advisory_gaps=[])
with tempfile.TemporaryDirectory() as root:
    d = os.path.join(root, "W")
    os.makedirs(d)
    DS.write_json(os.path.join(d, "stage.json"), {"stage": 5, "status": "open", "item": "W_ITEM"})
    try:
        row4 = CJ.record_round(d, rec4)["coverage_rounds"][-1]
    except Exception as e:   # noqa: BLE001
        row4 = {"crash": repr(e)}
expect("record_round: a round with no repair block records [] (looked, none), not a missing key",
       row4.get("repair_blocks") == [], row4.get("repair_blocks"))
if callable(cc):
    blk = {"gid": "g7", "entry": "scene:sc_wall", "passage": "the wall holds under wind 3",
           "promise": "walls stand in a storm"}
    st5 = stage({"verdict": "not_covered", "overturned": 0, "new_on_unchanged": 0, "not_owner_said": 0},
                {"verdict": "not_covered", "overturned": 0, "new_on_unchanged": 0, "not_owner_said": 0,
                 "repair_blocks": [blk]},
                {"verdict": "covered", "overturned": 0, "new_on_unchanged": 0, "not_owner_said": 0,
                 "repair_blocks": []})
    got = cc(st5)
    expect("close_counts: repair_blocks sums the recorded blocks", got.get("repair_blocks") == 1, got)
    expect("close_counts: a look recorded before the fifth count began is UNMEASURED for it, not 0",
           got.get("repair_blocks_unmeasured") == 1, got)
    if callable(cl):
        line = str(cl(got))
        for word in ("second-look blocks on a repaired passage 1", "the wall holds under wind 3",
                     "walls stand in a storm", "scene:sc_wall"):
            expect("close_line names %r" % word, word in line, line)
        expect("close_line names the fifth count's unmeasured looks", "UNMEASURED" in line, line)
for w in wrong:
    print("WRONG", w)
print("cases read %d; wrong %d (worst); limit 0" % (n, len(wrong)))
sys.exit(1 if wrong else 0)
