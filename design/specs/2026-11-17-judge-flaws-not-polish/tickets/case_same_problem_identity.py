#!/usr/bin/env python3
"""Failing acceptance cases for the same-problem rule (design/specs/2026-11-17-judge-flaws-not-polish/
7_same_problem_rule.md), built in ticket RIMMANDRAKE_WRITE_JUDGE_FOUR_RULES_TWO_LOOK_LIMIT.

On the second look (the repair check) identity is the prior gap's rows, never the judge's wording: a prior gap is
repaired only when the judge's own rows on it are all ok and no finding calls it still open; an open prior gap blocks as
its first-look record; a finding on other rows is new and blocks only when it quotes a passage of an entry that changed,
is rated `problem` and a second reader confirms it; anything else new is advisory, for the owner's short list.
Plus the phantom round: a second reader's charge is not a judge round, and a release written before that fix grants no
extra look.

Input kinds read: a reworded open gap on the same rows; one citing other rows; an `unfixed` report naming no prior gap;
a new finding on a prior gap's rows (tagged new, rows ok) and one naming the prior gap; split and merged reports;
evidence order; a real repair; an id-less prior gap with and without its `rest` row; a new finding on changed material
quoted verbatim (key order as shown), paraphrased, unconfirmed, rated polish; a new finding on unchanged material
confirmed; a `covered` word over an open gap; the phantom reader round; a legacy release and a new one.
Judge and reader are stubbed: no model, no network, no real concept.
Run from the repo root:  python3 design/specs/2026-11-17-judge-flaws-not-polish/tickets/case_same_problem_identity.py
Prints every wrong case, then: cases read, wrong count (worst), limit 0. Exit 1 when any case is wrong."""
import json
import os
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, *[".."] * 4))
sys.path.insert(0, os.path.join(ROOT, "src", "RimMandrake", "rimflow"))
import concept_tree as CT  # noqa: E402
import coverage_judge as CJ  # noqa: E402
import designer_stage as DS  # noqa: E402

wrong, n = [], 0


def expect(name, ok, got=""):
    global n
    n += 1
    if not ok:
        wrong.append("%s: got %s" % (name, str(got)[:400]))


WALL = "no scene tests the wall stop"
SC_WALL = {"id": "sc_wall", "asserts": "steel stays west of the wall after the blast"}


def concept(root, name):
    d = os.path.join(root, "design", "concepts", name)
    os.makedirs(d, exist_ok=True)
    os.makedirs(os.path.join(root, os.path.dirname(CT.OWNER_SHARD)), exist_ok=True)
    files = {
        "stage.json": {"stage": 5, "status": "open", "item": "FOO_%s" % name.upper(),
                       "budget": {"cap": 4000000, "reserve": 60000, "spent": 0, "charges": []}},
        "record.json": {"inventory": [{"id": "inv_throw", "what": "an explosion throws loose items outward"}]},
        "tree.json": {"kind": "mod", "leaves": [{"id": "leaf_wall", "what": "a wall stops a thrown item"}]},
        "scenes.json": {"scenes": [{"id": "sc_throw", "asserts": "steel lands two cells out"}]},
    }
    for fn, obj in files.items():
        with open(os.path.join(d, fn), "w") as f:
            json.dump(obj, f)
    with open(os.path.join(d, "sheet.md"), "w") as f:
        f.write("# Foo\n\n## What it does\nA blast throws items; walls stop them.\n")
    return d


def row(i, ok, scene="sc_throw"):
    return {"id": i, "evidence": ["record.json", "tree.json", "scenes.json", "sheet.md"],
            "parts": [{"what": "the %s experience" % i, "scene": scene, "ok": ok}]}


def gap(**kw):
    g = {"what": WALL, "where": "tree.json leaf_wall", "return_to": 3, "ids": ["leaf_wall"], "new_since": "first",
         "bar_kind": "experience", "severity": "problem", "evidence": ["tree.json", "scenes.json"],
         "observed": "leaf_wall says a wall stops a thrown item; scenes.json has only sc_throw, which has no wall",
         "would_pass": "a scene sc_wall places a wall one cell east of a blast and asserts the steel stays west of it",
         "smallest_fix": {"what": "add scene sc_wall to scenes.json with a wall east of the blast and a stack assertion",
                          "attainable": "yes", "cost": "edit"},
         "criterion_verdict": "sound",
         "criterion_why": "The leaf names a behaviour a single staged blast can show, so a scene can pass it."}
    g.update(kw)
    return g


THROW = dict(what="the throw scene measures no distance", where="scenes.json sc_throw", ids=["inv_throw"],
             observed="inv_throw says items are thrown outward; sc_throw asserts steel lands two cells out",
             would_pass="sc_throw asserts the stack lands at least two cells from the blast centre",
             smallest_fix={"what": "add a distance assertion to sc_throw", "attainable": "yes", "cost": "edit"})


NO = object()   # an answer in the old form: no `repairs` key at all


def answer(verdict, gaps, rows, repairs=NO):
    so = {"verdict": verdict, "gaps": list(gaps), "reasons": "r", "checklist": list(rows)}
    if repairs is not NO:
        so["repairs"] = [{"gap": g, "repaired": ok, "evidence": "scenes.json sc_wall"} for g, ok in repairs]
    return json.dumps({"structured_output": so, "usage": {"input_tokens": 10, "output_tokens": 2,
                                                          "cache_read_input_tokens": 0,
                                                          "cache_creation_input_tokens": 0}, "session_id": "sess"})


def script(answers):
    def r(argv, cwd, env, timeout):
        return 0, answers.pop(0) if answers else last
    last = answers[-1]
    return r


def reader_says(serious):
    return lambda items: [{"criterion_verdict": "sound", "criterion_why": "The bar names an experience one staged "
                           "scene can show.", "bar_kind": "experience", "serious": serious} for _ in items]


def look1(root, name, first=None, rows1=None):
    d = concept(root, name)
    first = [gap()] if first is None else first
    rows1 = rows1 or [row("inv_throw", True), row("leaf_wall", False, "")]
    rec1, _ = CJ.run(d, root, script([answer("not_covered", first, rows1, [])]), reader=None)
    return d, rec1


def repair(d, rec1, claims=("g1",), scenes=None):
    with open(os.path.join(d, "scenes.json"), "w") as f:
        json.dump({"scenes": scenes or [{"id": "sc_throw", "asserts": "steel lands two cells out"}, SC_WALL]}, f)
    with open(os.path.join(d, CJ.FIXES_FILE), "w") as f:
        json.dump({"against": rec1["judge"], "claims": [{"gap": c, "evidence": "scenes.json sc_wall"}
                                                         for c in claims]}, f)


def look2(root, name, gaps2, rows2, verdict2="not_covered", repairs=(("g1", True),), first=None, rows1=None,
          reader=None, claims=("g1",)):
    """Look 1 refuses with `first` (default: the wall gap); the Designer adds sc_wall and claims `claims`; look 2
    answers gaps2/rows2 and its repairs slots. -> look 2's record."""
    d, rec1 = look1(root, name, first, rows1)
    repair(d, rec1, claims)
    rec2, _ = CJ.run(d, root, script([answer(verdict2, gaps2, rows2, repairs)]), now=2000000000, reader=reader)
    return rec2


def blocking(rec):
    return [g for g in rec.get("gaps") or [] if isinstance(g, dict) and not g.get("malformed")]


def whats(rec):
    return sorted(str(g.get("what")) for g in blocking(rec))


def short_list(rec):
    return [g for g in rec.get("advisory_gaps") or [] if g.get("short_list")]


OK2 = [row("inv_throw", True), row("leaf_wall", True, "sc_wall")]
BAD2 = [row("inv_throw", True), row("leaf_wall", False, "sc_wall")]
FALSE = (("g1", False),)


def main():
    DS.owner_away = lambda: (False, "case: attended")
    CT.coverage_problem = lambda d, repo, tree: "no coverage signature"
    DS.exam_errors = lambda ex, d, st, repo=None: []
    CT.sign = lambda d, by, repo=None, **kw: []
    CJ.RC.status = lambda family: "CALIBRATED"
    CJ.NOT_COVERED_LIMIT = CJ.JUDGE_RUNS_MAX = 10 ** 6
    CJ.JUDGE_SPEND_MAX = 10 ** 15
    env = {k: os.environ.get(k) for k in ("RM_REFUSAL_DIR", "RM_OPS_WATCH_DIR", "RM_DISPATCHER_STATE")}
    try:
        with tempfile.TemporaryDirectory() as root:
            os.makedirs(os.path.join(root, "ops"))
            os.environ.update(RM_REFUSAL_DIR=os.path.join(root, "refusals"), RM_OPS_WATCH_DIR=os.path.join(root, "ops"),
                              RM_DISPATCHER_STATE=os.path.join(root, "dispatcher"))
            cases(root)
    finally:
        for k, v in env.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v
    for w in wrong:
        print("WRONG", w)
    print("cases read %d; wrong %d (worst); limit 0" % (n, len(wrong)))
    return 1 if wrong else 0


def cases(root):
    # a real repair: slot true, rows ok, nothing found -> covered and signed
    r = look2(root, "Repaired", [], OK2, "covered")
    expect("a real repair (slot true, rows ok, no finding) is covered and signed", r.get("signed") and not blocking(r),
           (r.get("verdict"), r.get("error"), whats(r)))
    r = look2(root, "OldForm", [], OK2, "covered", repairs=NO)
    expect("an old-form answer (no repairs key) closes by its rows, as the 2026-11-17 fix does", r.get("signed"),
           (r.get("verdict"), whats(r)))
    r = look2(root, "NoSlot", [], OK2, "covered", repairs=())
    expect("a repairs list that skips g1 leaves g1 open", not r.get("signed") and whats(r) == [WALL],
           (r.get("verdict"), whats(r)))
    r = look2(root, "SlotTrueRowBad", [], BAD2, "covered")
    expect("slot true with a failing row on its ids: open", not r.get("signed") and whats(r) == [WALL], whats(r))

    # reworded, same rows: blocks as the first-look record, once
    re = gap(what="the wall is still untested", observed="sc_wall has no wall in its start; leaf_wall untested",
             new_since="unfixed")
    r = look2(root, "Reworded", [re], BAD2, repairs=FALSE)
    expect("a reworded open gap on the same rows blocks", r.get("verdict") == "not_covered" and not r.get("signed"),
           r.get("verdict"))
    expect("a reworded open gap blocks as its first-look record, not the new wording", whats(r) == [WALL], whats(r))
    expect("the reworded report is kept on the open gap as a second-look note",
           any(x.get("what") == "the wall is still untested" for g in blocking(r) for x in g.get("second_look") or []),
           blocking(r))
    r = look2(root, "Order", [dict(re, evidence=["scenes.json", "tree.json"])], BAD2, repairs=FALSE)
    expect("evidence order changes nothing", whats(r) == [WALL] and not r.get("signed"), whats(r))

    # the same open defect under other rows, g1's rows ok
    other = gap(what="the wall test is still missing", ids=["inv_throw"], where="scenes.json sc_throw",
                new_since="unfixed", since="g1", observed=THROW["observed"], would_pass=THROW["would_pass"],
                smallest_fix=THROW["smallest_fix"])
    r = look2(root, "OtherRowsFalse", [other], OK2, repairs=FALSE)
    expect("the same defect under other rows, slot false: g1 open, blocking as itself", whats(r) == [WALL]
           and not r.get("signed"), (r.get("verdict"), whats(r)))
    r = look2(root, "OtherRowsTrue", [other], OK2)
    expect("slot true but a finding names g1: g1 open (unsure = open)", whats(r) == [WALL] and not r.get("signed"),
           (r.get("verdict"), whats(r)))
    r = look2(root, "Unplaced", [dict(other, since="")], OK2)
    expect("an unfixed report naming no slot leaves the look unsigned", not r.get("signed")
           and r.get("verdict") == "not_covered", (r.get("verdict"), whats(r), r.get("error")))

    # a different new problem on the repaired slot's row (Codex critique, finding 1): the slot closes
    newrow = gap(what="the sheet says 'stops' where the tree says 'blocks'", where="sheet.md What it does",
                 new_since="late", late_why="the first look read the tree, not the sheet's verb",
                 observed="sheet.md says walls stop them; leaf_wall says a wall stops a thrown item",
                 evidence=["sheet.md", "tree.json"])
    r = look2(root, "NewOnRow", [newrow], OK2, reader=reader_says(True))
    expect("a new problem on a repaired slot's row, unchanged material: covered", r.get("signed"),
           (r.get("verdict"), whats(r), r.get("error")))
    expect("that finding is on his short list", any(g.get("what") == newrow["what"] for g in short_list(r)),
           r.get("advisory_gaps"))
    r = look2(root, "NamesG1", [dict(newrow, since="g1", new_since="unfixed")], OK2)
    expect("a finding that names g1 keeps g1 open, blocking as g1 only", whats(r) == [WALL] and not r.get("signed"),
           whats(r))

    # split and merged
    r = look2(root, "Split", [dict(re, what="no wall in sc_wall"), dict(re, what="no stack assertion in sc_wall")],
              BAD2, repairs=FALSE)
    expect("a split report keeps one refusal: the prior gap", whats(r) == [WALL], whats(r))
    two = [gap(), gap(**THROW)]
    r = look2(root, "Merged", [dict(re, ids=["leaf_wall", "inv_throw"])],
              [row("inv_throw", False), row("leaf_wall", False, "sc_wall")], first=two,
              rows1=[row("inv_throw", False), row("leaf_wall", False, "")], claims=("g1", "g2"),
              repairs=(("g1", False), ("g2", False)))
    expect("a merged report keeps both prior gaps open, as themselves", whats(r) == sorted([WALL, THROW["what"]]),
           whats(r))

    # failing parts on a row no slot owns, nothing else: advisory, covered
    r = look2(root, "StrayPart", [], [row("inv_throw", False), row("leaf_wall", True, "sc_wall")], "covered")
    expect("a failing part on a row no slot owns, with no quote: advisory, covered", r.get("signed"),
           (r.get("verdict"), whats(r)))

    # an id-less prior gap closes by its slot
    restgap = gap(ids=[], what="the sheet never says what a wall does to a throw", where="sheet.md")
    rows1 = [row("inv_throw", True), row("leaf_wall", True)]
    r = look2(root, "RestSlot", [], rows1, "covered", first=[restgap], rows1=rows1)
    expect("an id-less prior gap closes by its slot", r.get("signed"), (r.get("verdict"), whats(r)))
    r = look2(root, "RestOld", [], rows1, "covered", first=[restgap], rows1=rows1, repairs=NO)
    expect("an id-less prior gap in the old form stays open", not r.get("signed"), (r.get("verdict"), whats(r)))

    # a new finding on changed material: verbatim passage (key order as shown), problem, reader confirms -> blocks
    quote = json.dumps(SC_WALL, ensure_ascii=False)
    brk = gap(what="sc_wall's wall stands where the throw lands", where="scenes.json sc_wall", ids=["inv_throw"],
              new_since="changed", since="scene:sc_wall\n%s" % quote,
              observed="sc_wall asserts steel stays west of the wall; sc_throw lands it two cells out",
              would_pass=THROW["would_pass"], smallest_fix=THROW["smallest_fix"])
    r = look2(root, "Broke", [brk], OK2, reader=reader_says(True))
    expect("a confirmed problem quoting a changed passage verbatim blocks",
           brk["what"] in whats(r) and not r.get("signed"), (r.get("verdict"), whats(r), r.get("advisory_gaps")))
    r = look2(root, "BrokePara", [dict(brk, since="scene:sc_wall\nthe steel is meant to stay on the west side")], OK2,
              reader=reader_says(True))
    expect("a paraphrased passage is not a changed passage: advisory, covered", r.get("signed")
           and any(g.get("what") == brk["what"] for g in short_list(r)), (r.get("verdict"), whats(r)))
    r = look2(root, "BrokeUnconf", [brk], OK2, reader=reader_says(False))
    expect("an unconfirmed problem on changed material is advisory", r.get("signed") and not blocking(r),
           (r.get("verdict"), whats(r)))
    r = look2(root, "BrokePolish", [dict(brk, severity="polish")], OK2, reader=reader_says(True))
    expect("a polish finding on changed material is advisory", r.get("signed") and not blocking(r), whats(r))

    # a finding outside the delta's scope (only a leaf changed, the finding is on another row) quoting the changed leaf:
    # the scope never drops it (Codex build review 2026-11-18)
    d, rec1 = look1(root, "OutOfScope")
    with open(os.path.join(d, "tree.json"), "w") as f:
        json.dump({"kind": "mod", "leaves": [{"id": "leaf_wall", "what": "a wall stops a thrown item only when it is "
                                                                      "steel"}]}, f)
    with open(os.path.join(d, CJ.FIXES_FILE), "w") as f:
        json.dump({"against": rec1["judge"], "claims": [{"gap": "g1", "evidence": "tree.json leaf_wall"}]}, f)
    oos = dict(brk, what="the throw now lands wood through the wall", where="tree.json leaf_wall",
               since="leaf:leaf_wall\na wall stops a thrown item only when it is steel")
    r, _ = CJ.run(d, root, script([answer("not_covered", [oos], OK2, (("g1", True),))]), now=2000000000,
                  reader=reader_says(True))
    expect("a confirmed problem quoting a changed leaf blocks even outside the delta's rows",
           r.get("mode") == "delta" and oos["what"] in whats(r) and not r.get("signed"),
           (r.get("mode"), r.get("verdict"), whats(r), r.get("dropped")))

    # Codex build review 2026-11-18, findings 1, 2 and 4
    d, rec1 = look1(root, "Escaped")
    esc = {"id": "sc_wall", "asserts": 'the label reads "wall" after the blast'}
    repair(d, rec1, scenes=[{"id": "sc_throw", "asserts": "steel lands two cells out"}, esc])
    r, _ = CJ.run(d, root, script([answer("not_covered", [dict(brk, since="scene:sc_wall\n" + json.dumps(
        esc, ensure_ascii=False))], OK2, (("g1", True),))]), now=2000000000, reader=reader_says(True))
    expect("a passage quoted exactly as the prompt showed it, JSON escapes and all, is a changed passage",
           brk["what"] in whats(r) and not r.get("signed"), (r.get("verdict"), whats(r)))
    r = look2(root, "FirstOnRow", [dict(newrow, new_since="first")], OK2, reader=reader_says(True))
    expect("a finding tagged `first` on a repaired slot's row is new, not the slot: covered", r.get("signed")
           and any(g.get("what") == newrow["what"] for g in short_list(r)), (r.get("verdict"), whats(r)))
    for bad in (None, {}, "g1 repaired"):
        d, rec1 = look1(root, "BadRepairs%s" % type(bad).__name__)
        repair(d, rec1)
        so = json.loads(answer("covered", [], OK2))
        so["structured_output"]["repairs"] = bad
        r, _ = CJ.run(d, root, script([json.dumps(so)]), now=2000000000, reader=None)
        expect("a `repairs` value that is there but not a list (%r) answers no slot: g1 open" % (bad,),
               not r.get("signed") and whats(r) == [WALL], (r.get("verdict"), whats(r)))

    # an unchanged passage inside a changed entry (Codex critique, finding 3): advisory
    d, rec1 = look1(root, "SameInChanged")
    repair(d, rec1, scenes=[{"id": "sc_throw", "asserts": "steel lands two cells out", "seed": 7}, SC_WALL])
    same = dict(brk, what="sc_throw lands steel on the wall line", where="scenes.json sc_throw",
                since='scene:sc_throw\n"asserts": "steel lands two cells out"')
    r, _ = CJ.run(d, root, script([answer("not_covered", [same], OK2, (("g1", True),))]), now=2000000000,
                  reader=reader_says(True))
    expect("an unchanged passage in a changed entry is not a changed passage: advisory", r.get("signed"),
           (r.get("verdict"), whats(r)))

    # a new finding on unchanged material, problem, reader confirms -> advisory (the owner's trial)
    late = dict(brk, what="sc_throw never measures distance", where="scenes.json sc_throw", new_since="late",
                since="scene:sc_throw\nsteel lands two cells out", late_why="the first look missed it")
    r = look2(root, "Late", [late], OK2, reader=reader_says(True))
    expect("a confirmed problem on unchanged material is advisory, on his short list",
           r.get("signed") and any(g.get("what") == late["what"] for g in short_list(r)),
           (r.get("verdict"), whats(r), r.get("advisory_gaps")))

    # the verdict word never outranks an open slot
    r = look2(root, "WordCovered", [], BAD2, "covered", repairs=FALSE)
    expect("`covered` with an open slot is not_covered", r.get("verdict") == "not_covered" and not r.get("signed")
           and whats(r) == [WALL], (r.get("verdict"), whats(r)))

    # a broken record re-asked after the slots were read, coming back as g1 still open: g1 opens again (Codex build
    # review 2026-11-18)
    d, rec1 = look1(root, "Reask")
    repair(d, rec1)
    broken = dict(brk, ids=["inv_throw"], evidence=["sheet.md:1"], observed="the range reading is missing; nobody "
                  "measures distance", since="scene:sc_wall\n%s" % quote)
    fixed = dict(broken, new_since="unfixed", since="g1", evidence=["tree.json", "scenes.json"],
                 observed="leaf_wall says a wall stops a thrown item; sc_wall has no wall in its start")
    r, _ = CJ.run(d, root, script([answer("not_covered", [broken], OK2, (("g1", True),)),
                                   json.dumps({"structured_output": {"gaps": [fixed]}, "session_id": "sess"})]),
                  now=2000000000, reader=reader_says(True))
    expect("a re-asked record naming g1 reopens g1 and blocks as it, never as its own refusal",
           whats(r) == [WALL] and not r.get("signed") and not any(a.get("gid") == "g1" for a in r.get("answered") or []),
           (r.get("verdict"), whats(r), r.get("answered"), r.get("rows_reasked")))

    # a failed attempt keeps the baseline (Codex critique, finding 4)
    d, rec1 = look1(root, "Retry")
    repair(d, rec1)
    CJ.run(d, root, script(["not json"]), now=2000000000, reader=None)
    expect("a failed attempt keeps the last usable verdict as the baseline",
           (CJ.prior_verdict(d) or {}).get("judge") == rec1["judge"], (CJ.prior_verdict(d) or {}).get("judge"))
    r, _ = CJ.run(d, root, script([answer("not_covered", [re], BAD2, FALSE)]), now=2000000100, reader=None)
    expect("the retry checks the same slot: g1 open, blocking as itself", whats(r) == [WALL], whats(r))

    # the phantom reader round
    st = {"coverage_rounds": [{"judge": "rm-coverage-judge-100", "verdict": "not_covered", "at": "2026-01-01T00:00:10Z",
                               "tokens": 5}],
          "budget": {"charges": [{"ref": "rm-coverage-judge-100", "kind": "review", "tokens": 5, "at": "2026-01-01T00:00:09Z"},
                                 {"ref": "rm-coverage-judge-100-reader", "kind": "review", "tokens": 7,
                                  "at": "2026-01-01T00:00:11Z"}]}}
    rs = CJ.rounds(st)
    expect("a second reader's charge is not a judge round", len(rs) == 1, [x.get("judge") for x in rs])
    expect("its tokens count in the judge's spend, exactly", CJ.spend(rs) == 12, CJ.spend(rs))

    # a legacy release counted with a phantom round grants no extra look; a new release records its judges
    ch = [{"ref": "rm-coverage-judge-1-reader", "kind": "review", "tokens": 1, "at": "2026-01-01T00:00:01Z"}]
    st = {"coverage_rounds": [{"judge": "rm-coverage-judge-%d" % i, "verdict": "not_covered"} for i in (1, 2, 3)],
          "budget": {"charges": ch}, "coverage_releases": [{"rounds_at": 3, "granted_at": "t"}]}
    expect("a legacy release counted with a phantom: the released look's refusal stops", bool(CJ.stop_reason(st)),
           CJ.stop_reason(st))
    st["coverage_rounds"] = st["coverage_rounds"][:2]
    expect("a legacy release counted with a phantom: before its look, judging may go on", CJ.stop_reason(st) is None,
           CJ.stop_reason(st))
    d = concept(root, "Released")
    s = DS.load_state(d)
    s["coverage_rounds"] = [{"judge": "rm-coverage-judge-%d" % i, "verdict": "not_covered"} for i in (1, 2)]
    DS.write_json(DS.state_path(d), s)
    try:
        CJ.release(d, "case: one more look", item_state=lambda ids: {})
    except Exception as e:  # noqa: BLE001 - a refusal here is a case result, not a crash
        expect("a release is granted", False, e)
    rel = (DS.load_state(d).get("coverage_releases") or [{}])[-1]
    expect("a new release records the judges before it", rel.get("judges_at") == ["rm-coverage-judge-1",
                                                                                   "rm-coverage-judge-2"], rel)



if __name__ == "__main__":
    sys.exit(main())
