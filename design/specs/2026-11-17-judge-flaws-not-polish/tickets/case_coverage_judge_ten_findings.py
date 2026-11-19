#!/usr/bin/env python3
"""Failing acceptance cases for RIMMANDRAKE_FIX_COVERAGE_JUDGE_TEN_FINDINGS_FIFTH_COUNT_CLEAN: the Codex full-file review
of coverage_judge.py, 2026-11-18 (raw: D:\\ClaudeWork\\rimmandrake\\conductor\\cr\\r_cj_fifth.txt). One case per finding
the fixer took as a bug; finding 1 (an `unfixed` report naming no slot blocks) is the settled rule 4 of
7_same_problem_rule.md ("A finding naming no slot but tagged `unfixed` ... is an unplaced repair report: it blocks"),
already cased in case_same_problem_identity.py ("Unplaced"), so it is ruled not a bug and has no case here.

Input kinds read: a covered look that errs after a refusal (the retry's baseline); a since whose quoted passage holds a
gap number; repeated and literal `#N` sheet headings; a failed round before the first real look; a measured call and an
unmeasured re-ask; a reader that times out, answers undecodable output, or whose measurement raises; a not_covered
answer naming no gap over a passing checklist; a gap that is not an object; tree.json unreadable at completion.
Judge and reader are stubbed: no model, no network, no real concept.
Run from the repo root:  python3 design/specs/2026-11-17-judge-flaws-not-polish/tickets/case_coverage_judge_ten_findings.py
Prints every wrong case, then: cases read, wrong count (worst), limit 0. Exit 1 when any case is wrong."""
import json
import os
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import case_same_problem_identity as SP  # noqa: E402  (its harness: concept, gap, row, answer, look1, repair)
from case_same_problem_identity import CJ, CT, DS  # noqa: E402

wrong, n = [], 0


def expect(name, ok, got=""):
    global n
    n += 1
    if not ok:
        wrong.append("%s: got %s" % (name, str(got)[:400]))


def raw(so, tokens=True, session="sess"):
    res = {"structured_output": so, "session_id": session}
    if tokens:
        # as `claude -p` writes it: modelUsage names the model, so the measure needs no model alias from the environment
        res["modelUsage"] = {"claude-opus-5-5": {"inputTokens": 10, "outputTokens": 2, "cacheReadInputTokens": 0,
                                                 "cacheCreationInputTokens": 0}}
    return json.dumps(res)


def safe_run(d, root, runner, **kw):
    try:
        return CJ.run(d, root, runner, **kw), None
    except Exception as e:  # noqa: BLE001 - a raise is the case's finding, not the case runner's crash
        return (None, None), "%s: %s" % (type(e).__name__, e)


def cases(root):
    full = [SP.row("inv_throw", True), SP.row("leaf_wall", True, "sc_wall")]

    # 2. a failed covered attempt keeps the retry's baseline (rule 6)
    d, rec1 = SP.look1(root, "Baseline")
    SP.repair(d, rec1)
    rec2, _ = CJ.run(d, root, SP.script([SP.answer("covered", [], [SP.row("inv_throw", True)], (("g1", True),))]),
                     now=2000000000, reader=None)
    pv = CJ.prior_verdict(d) or {}
    expect("2: a covered look that errs (a row missing) is not the retry's prior: j1's refusal is",
           rec2.get("error") and pv.get("judge") == rec1["judge"],
           (rec2.get("verdict"), rec2.get("error"), pv.get("judge"), rec1["judge"]))
    expect("2: the errored covered look stores j1 as its baseline",
           (rec2.get("baseline") or {}).get("judge") == rec1["judge"], sorted(rec2))

    # 3. a gap number inside a quoted passage names no slot
    d, rec1 = SP.look1(root, "QuotedNumber")
    passage = "the repair sets target g1 to fail"
    SP.repair(d, rec1, scenes=[{"id": "sc_throw", "asserts": "steel lands two cells out"},
                               {"id": "sc_wall", "asserts": "a wall east of the blast; %s first" % passage}])
    new = SP.gap(**dict(SP.THROW, new_since="changed", since="scene:sc_wall\n" + passage))
    rec2, _ = CJ.run(d, root, SP.script([SP.answer("not_covered", [new], full, (("g1", True),))]), now=2000000001,
                     reader=SP.reader_says(True))
    expect("3: g1 (repaired) closes though the new finding's quote holds 'g1'",
           [a.get("gid") for a in rec2.get("answered") or []] == ["g1"]
           and not any(g.get("carried") for g in rec2.get("gaps") or []),
           (rec2.get("answered"), [(g.get("what"), g.get("carried")) for g in rec2.get("gaps") or []]))
    expect("3: the new finding blocks as a repair-passage block and the fifth count sees it",
           len(CJ.repair_blocks(rec2)) == 1, (CJ.repair_blocks(rec2), [g.get("what") for g in rec2.get("gaps") or []]))

    # 4. sheet headings: a repeated heading and a literal `A#2` never share a key
    sheet = "# Foo\n## A\none\n## A\nhidden section\n## A#2\nliteral\n"
    ent = CJ.entries(None, read=lambda name: sheet if name == "sheet.md" else None)
    secs = [v for k, v in ent.items() if k.startswith("sheet:")]
    expect("4: every sheet section has its own key", any("hidden section" in v for v in secs)
           and any("literal" in v for v in secs), sorted(k for k in ent if k.startswith("sheet:")))
    h1 = CJ.entry_hashes(None, read=lambda name: sheet if name == "sheet.md" else None)
    h2 = CJ.entry_hashes(None, read=lambda name: sheet.replace("hidden section", "hidden section, edited")
                         if name == "sheet.md" else None)
    expect("4: editing the repeated section changes the entry hashes", h1 != h2, "same hashes")

    # 5. a failed attempt before the first real look does not make its findings late
    d = SP.concept(root, "FailedFirst")
    st = DS.load_state(d)
    st["coverage_rounds"] = [{"judge": "rm-coverage-judge-1", "at": "2026-01-01T00:00:00Z", "verdict": None,
                              "tokens": None, "gaps": 0, "ids": [], "late": [], "error": "the judge did not answer"}]
    DS.write_json(DS.state_path(d), st)
    rec, _ = CJ.run(d, root, SP.script([SP.answer("not_covered", [SP.gap()], [SP.row("inv_throw", True),
                                                                             SP.row("leaf_wall", False, "")], [])]),
                    reader=None)
    g = (rec.get("gaps") or [{}])[0]
    last = (DS.load_state(d).get("coverage_rounds") or [{}])[-1]
    expect("5: the first real look's gap is `first`, not late", g.get("new_since") == "first" and not rec.get("late"),
           (g.get("new_since"), rec.get("late")))
    expect("5: its round counts no new demand on unchanged material", last.get("new_on_unchanged") == 0,
           last.get("new_on_unchanged"))

    # 6. a measured call and an unmeasured re-ask: the unknown spend is kept
    d = SP.concept(root, "UnmeasuredRetry")
    so_short = {"verdict": "covered", "gaps": [], "reasons": "r", "checklist": [SP.row("inv_throw", True)]}
    so_full = {"verdict": "covered", "gaps": [], "reasons": "r", "checklist": [SP.row("inv_throw", True),
                                                                              SP.row("leaf_wall", True, "sc_throw")]}
    rec, _ = CJ.run(d, root, SP.script([raw(so_short), raw(so_full, tokens=False)]), reader=None)
    measured = rec.get("tokens")
    sp = CJ.spend(CJ.rounds(DS.load_state(d), d))
    expect("6: the re-ask ran unmeasured: spend is the measured call plus the p90 allowance",
           isinstance(measured, int) and sp == measured + CJ.JUDGE_P90_TOKENS, (measured, sp))

    # 7. a reader call that ran but cannot be measured is charged unmeasured
    items = [{"clause": ["inv_throw"], "criterion": ["x"], "what": "w"}]
    import role_launch as RL
    for label, runner, bad_measure in (
            ("times out", lambda *a: (_ for _ in ()).throw(subprocess.TimeoutExpired("claude", 1)), False),
            ("answers undecodable output", lambda *a: (0, "not json"), False),
            ("measurement raises", lambda *a: (0, raw({"grades": []})), True)):
        d = SP.concept(root, "Reader%d" % n)
        saved = RL.run_tokens
        if bad_measure:
            RL.run_tokens = lambda res, model=None: (_ for _ in ()).throw(RL.UnknownModel("case: unknown model"))
        try:
            CJ.llm_reader(d, root, "rm-coverage-judge-7", True, runner)(items)
        except Exception as e:  # noqa: BLE001
            expect("7: the reader that %s does not raise" % label, False, e)
        finally:
            RL.run_tokens = saved
        ch = (DS.load_state(d).get("budget") or {}).get("charges") or []
        expect("7: the reader that %s leaves an unmeasured charge" % label,
               any(c.get("ref") == "rm-coverage-judge-7-reader" and c.get("kind") == "unmeasured" for c in ch), ch)

    # 8. a not_covered answer naming no gap over a passing checklist is no refusal
    d = SP.concept(root, "EmptyRefusal")
    rec, _ = CJ.run(d, root, SP.script([SP.answer("not_covered", [], [SP.row("inv_throw", True),
                                                                      SP.row("leaf_wall", True)], [])]), reader=None)
    last = (DS.load_state(d).get("coverage_rounds") or [{}])[-1]
    expect("8: a refusal with no blocking gap is recorded malformed, with its reason, and not signed",
           rec.get("verdict") == "malformed" and last.get("verdict") == "malformed" and rec.get("malformed")
           and not rec.get("signed"), (rec.get("verdict"), last.get("verdict"), rec.get("malformed")))

    # 9. a gap that is not an object is a malformed answer, recorded, never a crash
    d = SP.concept(root, "NullGap")
    (rec, _m), err = safe_run(d, root, SP.script([raw({"verdict": "covered", "checklist": [], "gaps": [None],
                                                       "reasons": "", "repairs": []})]), reader=None)
    rs = DS.load_state(d).get("coverage_rounds") or []
    expect("9: gaps [null] does not raise", err is None, err)
    expect("9: gaps [null] is recorded as a failed round, not signed",
           rs and rs[-1].get("verdict") is None and (rec or {}).get("error") and not (rec or {}).get("signed"),
           (rs, rec and rec.get("error")))

    # 10. tree.json unreadable when the judge returns covered: the round is kept, nothing signed
    d = SP.concept(root, "TreeGone")
    answers = [raw({"verdict": "covered", "gaps": [], "reasons": "r",
                    "checklist": [SP.row("inv_throw", True), SP.row("leaf_wall", True)]})]

    def breaks_tree(argv, cwd, env, timeout):
        with open(os.path.join(d, "tree.json"), "w") as f:
            f.write("{")
        return 0, answers[0]
    (rec, _m), err = safe_run(d, root, breaks_tree, reader=None)
    rs = DS.load_state(d).get("coverage_rounds") or []
    expect("10: an unreadable tree at completion does not raise", err is None, err)
    expect("10: the round and the verdict are kept, with the error, not signed",
           rs and (rec or {}).get("error") and not (rec or {}).get("signed")
           and os.path.exists(os.path.join(d, CJ.VERDICT_FILE)), (len(rs), rec and rec.get("error")))

    controls(root)
    review_two(root)


def controls(root):
    """Codex's second look (2026-11-18): the controls a partial fix of each finding would fail."""
    full = [SP.row("inv_throw", True), SP.row("leaf_wall", True, "sc_throw")]
    # 2, control: a clean covered look is its own prior
    d = SP.concept(root, "CleanCovered")
    rec, _ = CJ.run(d, root, SP.script([raw({"verdict": "covered", "gaps": [], "reasons": "r", "checklist": full})]),
                    reader=None)
    expect("2 control: a covered look with no error is the next look's prior",
           rec.get("signed") and (CJ.prior_verdict(d) or {}).get("judge") == rec["judge"], rec.get("error"))
    # 3, the re-ask path: reopen_named reads the same slot rule
    slots = [dict(SP.gap(), gid="g1", carried=False)]
    new = SP.gap(**dict(SP.THROW, new_since="unfixed", since="scene:sc_wall\nthe repair sets target g1 to fail"))
    new["ids"] = ["inv_throw"]
    rec = {"verdict": "not_covered", "gaps": [new], "answered": [{"gid": "g1"}]}
    CJ.reopen_named(rec, [new], slots)
    expect("3 control: the re-ask's quoted 'g1' reopens nothing", rec["answered"] == [{"gid": "g1"}]
           and rec["gaps"] == [new], rec)
    rec = {"verdict": "not_covered", "gaps": [dict(new, since="g1")], "answered": [{"gid": "g1"}]}
    CJ.reopen_named(rec, list(rec["gaps"]), slots)
    expect("3 control: since 'g1' still names g1", rec["answered"] == [] and rec["gaps"][0].get("gid") == "g1", rec)
    # 4, reverse order: the literal `A#2` first, then two `A`s
    sheet = "## A#2\nliteral\n## A\none\n## A\nhidden section\n"
    ent = CJ.entries(None, read=lambda name: sheet if name == "sheet.md" else None)
    secs = [v for k, v in ent.items() if k.startswith("sheet:")]
    expect("4 control: literal `A#2` before two `A`s, every section kept", any("hidden section" in v for v in secs)
           and any("literal" in v for v in secs), sorted(ent))
    plain = CJ.entries(None, read=lambda name: "## A\none\n## B\ntwo\n## A\nthree\n" if name == "sheet.md" else None)
    expect("4 control: keys with no clash are unchanged", {"sheet:A", "sheet:B", "sheet:A#2"} <= set(plain), sorted(plain))
    # 5: a malformed and an errored-covered round before the first real look are no looks either
    d = SP.concept(root, "FailedKinds")
    st = DS.load_state(d)
    st["coverage_rounds"] = [{"judge": "rm-coverage-judge-1", "verdict": "malformed", "ids": ["inv_throw"]},
                             {"judge": "rm-coverage-judge-2", "verdict": "covered", "ids": [], "error": "not signed"}]
    DS.write_json(DS.state_path(d), st)
    expect("5 control: malformed and errored rounds give no earlier gaps", CJ.earlier_gaps(st, d) == [],
           CJ.earlier_gaps(st, d))
    st["coverage_rounds"].append({"judge": "rm-coverage-judge-3", "verdict": "not_covered", "ids": ["inv_throw"]})
    expect("5 control: a real refusal's ids are earlier gaps", CJ.earlier_gaps(st, d) == [{"ids": ["inv_throw"]}],
           CJ.earlier_gaps(st, d))
    # 6: two unmeasured calls; a judge that never launched spent 0; an old round with no count is one unknown call
    P = CJ.JUDGE_P90_TOKENS
    expect("6 control: two unmeasured calls are two allowances", CJ.spend([{"tokens": 20, "unmeasured_calls": 2}])
           == 20 + 2 * P, CJ.spend([{"tokens": 20, "unmeasured_calls": 2}]))
    expect("6 control: never launched (no token, no unmeasured call) spends 0",
           CJ.spend([{"tokens": None, "unmeasured_calls": 0}]) == 0)
    expect("6 control: an old round with no count and no token is one allowance", CJ.spend([{"tokens": None}]) == P)
    d = SP.concept(root, "NeverLaunched")

    def no_claude(argv, cwd, env, timeout):
        raise FileNotFoundError("claude")
    rec, _ = CJ.run(d, root, no_claude, reader=None)
    sp = CJ.spend(CJ.rounds(DS.load_state(d), d))
    ch = (DS.load_state(d).get("budget") or {}).get("charges") or []
    expect("6 control: a judge that never launched charges nothing and spends 0", sp == 0 and not ch, (sp, ch))
    d = SP.concept(root, "TimedOutJudge")

    def times_out(argv, cwd, env, timeout):
        raise subprocess.TimeoutExpired("claude", 1)
    CJ.run(d, root, times_out, reader=None)
    ch = (DS.load_state(d).get("budget") or {}).get("charges") or []
    # its round is void_system (RIMMANDRAKE_EXTEND_VOID_TO_JUDGE_DESIGNER_AND_PILOT_COUNTERS; owner 2026-11-18: "I will
    # not accept ANY system that pointlessly expends such statistical measurements based on failed system calls"): the
    # call is on the budget as unmeasured, and the caps' spend leaves the void round out
    st = DS.load_state(d)
    expect("6 control: a judge that timed out is charged unmeasured, its round void and out of the caps' spend",
           [c.get("kind") for c in ch] == ["unmeasured"] and CJ.spend(CJ.rounds(st, d)) == 0
           and [r.get("void_system") is not None for r in CJ.rounds(st, d, voids=True)] == [True], ch)
    # 7, controls: a measured reader is charged review; one that never launched is charged nothing
    items = [{"clause": ["inv_throw"], "criterion": ["x"], "what": "w"}]
    for label, runner, kinds in (("measured", lambda *a: (0, raw({"grades": [{}]})), ["review"]),
                                 ("never launched", lambda *a: (_ for _ in ()).throw(FileNotFoundError("claude")), [])):
        d = SP.concept(root, "ReaderCtl%d" % n)
        CJ.llm_reader(d, root, "rm-coverage-judge-7", True, runner)(items)
        ch = (DS.load_state(d).get("budget") or {}).get("charges") or []
        expect("7 control: a %s reader is charged %s" % (label, kinds or "nothing"), [c.get("kind") for c in ch] == kinds, ch)
    # 9: rows and nested elements
    for label, so in (("a row that is not an object", {"checklist": [None]}),
                      ("a part that is not an object", {"checklist": [{"id": "inv_throw", "parts": [None]}]}),
                      ("a part with no true/false ok", {"checklist": [{"id": "inv_throw", "parts": [{"what": "w"}]}]}),
                      ("a gap id that is not a string", {"gaps": [{"ids": [[]]}]})):
        d = SP.concept(root, "Shape%d" % n)
        body = dict({"verdict": "covered", "gaps": [], "reasons": "", "checklist": full}, **so)
        (rec, _m), err = safe_run(d, root, SP.script([raw(body)]), reader=None)
        expect("9 control: %s is recorded as a malformed answer, not signed" % label,
               err is None and (rec or {}).get("error") and not (rec or {}).get("signed"), (err, rec and rec.get("error")))
    # 10, control: a refusal needs no tree reread
    d = SP.concept(root, "TreeGoneRefusal")
    ans = [SP.answer("not_covered", [SP.gap()], [SP.row("inv_throw", True), SP.row("leaf_wall", False, "")], [])]

    def breaks_tree_refuses(argv, cwd, env, timeout):
        with open(os.path.join(d, "tree.json"), "w") as f:
            f.write("{")
        return 0, ans[0]
    (rec, _m), err = safe_run(d, root, breaks_tree_refuses, reader=None)
    rs = DS.load_state(d).get("coverage_rounds") or []
    # its criterion is a leaf of the unreadable tree, so the refusal record cannot be checked: malformed, kept
    expect("10 control: a refusal with the tree unreadable is recorded (malformed: its criterion is unreadable), "
           "never a raise", err is None and (rec or {}).get("verdict") == "malformed" and rs, (err, rec and rec.get("verdict")))


def review_two(root):
    """Flaws Codex found in the fix itself (2026-11-18, second look), each red before its repair."""
    # malformed records kept on file are no repair slots
    d, rec1 = SP.look1(root, "MalformedSlot")
    v = DS.read_json(os.path.join(d, CJ.VERDICT_FILE))
    bad = dict(SP.gap(**SP.THROW), gid="g2", malformed=["no would_pass"])
    v["gaps"] = list(v["gaps"]) + [bad]
    DS.write_json(os.path.join(d, CJ.VERDICT_FILE), v)
    SP.repair(d, rec1)
    rec2, _ = CJ.run(d, root, SP.script([SP.answer("covered", [], [SP.row("inv_throw", True),
                                                                   SP.row("leaf_wall", True, "sc_wall")],
                                                   (("g1", True),))]), now=2000000002, reader=None)
    expect("a malformed record on file is no slot: g1 repaired, the look is covered and signed",
           rec2.get("verdict") == "covered" and rec2.get("signed") and not rec2.get("gaps"),
           (rec2.get("verdict"), [g.get("gid") for g in rec2.get("gaps") or []]))
    expect("the malformed record stays as evidence", [g.get("gid") for g in rec2.get("prior_malformed") or []] == ["g2"],
           rec2.get("prior_malformed"))
    # a reader grade that is not an object is no second read, never a crash
    d = SP.concept(root, "NullGrade")
    reader = CJ.llm_reader(d, root, "rm-coverage-judge-8", False, lambda *a: (0, raw({"grades": [None]})))
    try:
        got = reader([{"clause": ["inv_throw"]}])
    except Exception as e:  # noqa: BLE001
        got = e
    expect("grades [null] is no second read", got is None, got)
    reader = CJ.llm_reader(d, root, "rm-coverage-judge-8", False, lambda *a: (0, json.dumps({"structured_output": "x"})))
    try:
        got = reader([{"clause": ["inv_throw"]}])
    except Exception as e:  # noqa: BLE001
        got = e
    expect("a structured_output that is not an object is no second read", got is None, got)
    # legacy charges: measured and unmeasured on one judge both count
    st = {"budget": {"charges": [{"ref": "rm-coverage-judge-5", "kind": "review", "tokens": 100, "at": "a"},
                                 {"ref": "rm-coverage-judge-5", "kind": "unmeasured", "tokens": 0, "at": "b"},
                                 {"ref": "rm-coverage-judge-5", "kind": "unmeasured", "tokens": 0, "at": "c"}]}}
    expect("a legacy judge's 100 measured and two unmeasured calls spend 100 + 2 p90",
           CJ.spend(CJ.rounds(st)) == 100 + 2 * CJ.JUDGE_P90_TOKENS, CJ.spend(CJ.rounds(st)))
    # an orphan reader charged before a release does not count after it; one charged after does
    st = {"budget": {"charges": [{"ref": "rm-coverage-judge-6-reader", "kind": "review", "tokens": 7,
                                  "at": "2026-01-01T00:00:00Z"},
                                 {"ref": "rm-coverage-judge-9-reader", "kind": "review", "tokens": 3,
                                  "at": "2026-01-03T00:00:00Z"}]},
          "coverage_releases": [{"at": "2026-01-02T00:00:00Z", "judges_at": []}]}
    rs = CJ.rounds(st)
    after = CJ.released_rounds(st, None, rs, st["coverage_releases"][-1])
    expect("an orphan reader before the release is not spend after it", CJ.spend(after) == 3, CJ.spend(after))
    expect("both orphan readers still count in the whole spend", CJ.spend(rs) == 10, CJ.spend(rs))
    # an unreadable exam is a plan error, never a raise
    d = SP.concept(root, "ExamGone")
    with open(os.path.join(d, "exam.json"), "w") as f:
        f.write("{")
    saved = DS.exam_errors
    DS.exam_errors = lambda ex, d, st, repo=None: []
    try:
        got = CJ.plan(d, root)
    except Exception as e:  # noqa: BLE001
        got = e
    finally:
        DS.exam_errors = saved
    expect("an unreadable exam.json is a plan error, not a raise", isinstance(got, tuple) and got[0] == "error", got)
    review_three(root)


def review_three(root):
    """Codex's third look (2026-11-18): flaws left in the repairs, each red before its fix."""
    slots = {"g1"}
    expect("a gap number in a cited entry key names no slot",
           CJ.named_slots({"since": "sheet:Notes g1\nsome changed passage here"}, slots) == set())
    expect("a bare slot number with a note after a newline still names it",
           CJ.named_slots({"since": "g1\nstill open: the wall scene has no wall"}, slots) == {"g1"})
    d = SP.concept(root, "EvidenceSeven")
    g = dict(SP.gap(), evidence=7)
    (rec, _m), err = safe_run(d, root, SP.script([SP.answer("not_covered", [g], [SP.row("inv_throw", True),
                                                                               SP.row("leaf_wall", False, "")], [])]),
                              reader=None)
    expect("a gap whose evidence is not a list is a malformed answer, never a raise",
           err is None and (rec or {}).get("error") and not (rec or {}).get("signed"), (err, rec and rec.get("error")))
    d, rec1 = SP.look1(root, "BadClaim")
    with open(os.path.join(d, CJ.FIXES_FILE), "w") as f:
        json.dump({"against": rec1["judge"], "claims": [{"gap": [], "evidence": "scenes.json"}]}, f)
    try:
        got = CJ.fix_claims(d, CJ.prior_verdict(d))
    except Exception as e:  # noqa: BLE001
        got = e
    expect("a claim whose gap is not a string is refused with a reason, never a raise",
           isinstance(got, tuple) and got[0] == [] and got[1], got)
    d = SP.concept(root, "EmptyRefusalUnchecked")
    rec, _ = CJ.run(d, root, SP.script([SP.answer("not_covered", [], [SP.row("inv_throw", True)], [])]), reader=None)
    expect("a gapless refusal with rows unchecked is malformed too",
           rec.get("verdict") == "malformed" and "leaf_wall" in " ".join(rec.get("malformed") or []),
           (rec.get("verdict"), rec.get("malformed")))
    st = {"coverage_rounds": [{"judge": "rm-coverage-judge-1", "verdict": "not_covered", "overturned": 0,
                               "new_on_unchanged": 0, "not_owner_said": 0, "repair_blocks": []},
                              {"judge": "rm-coverage-judge-2", "verdict": "covered", "error": "not signed: a row missing",
                               "overturned": 0, "new_on_unchanged": 0, "not_owner_said": 0, "repair_blocks": []}]}
    c = CJ.close_counts(st)
    expect("a covered word the program refused is not a look in the close counts", c["looks"] == 1, c)


def main():
    DS.owner_away = lambda: (False, "case: attended")
    CT.coverage_problem = lambda d, repo, tree: "no coverage signature"
    DS.exam_errors = lambda ex, d, st, repo=None: []
    CT.sign = lambda d, by, repo=None, **kw: []
    CJ.RC.status = lambda family: "CALIBRATED"
    CJ.NOT_COVERED_LIMIT = CJ.JUDGE_RUNS_MAX = CJ.MALFORMED_LIMIT = 10 ** 6
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


if __name__ == "__main__":
    sys.exit(main())
