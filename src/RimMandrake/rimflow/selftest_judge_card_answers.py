#!/usr/bin/env python3
"""selftest_judge_card_answers.py - the judge prompt changes the owner answered by card on 2026-11-16 11:36 PM PST
(RIMMANDRAKE_LAND_JUDGE_PROMPT_CALLS_FOUR_ANSWERED_BY_CARD; D:\\ClaudeWork\\rimmandrake\\conductor\\
role_prompt_upgrades_20261116.md section 7, GPT's reply gpt_review_judge_prompts_20261116.md).

- Point 26, "Only if a second reader agrees": a late gap (new at a later look on unchanged material, after a refusing
  look) blocks only when the judge calls it a serious Problem (`severity` `problem`) AND the second reader confirms it
  (`serious`). Five cases: serious+confirmed blocks, serious+unconfirmed and minor+confirmed are advisory, a round-1
  `problem` gap blocks and a round-1 `polish` gap does not (that last pair replaced "a round-1 gap blocks whatever its
  severity" when the owner's card of 2026-11-17 named it a bug; see the case text). A program reader (no model)
  confirms nothing.
- Point 14, "Open search in round 1 only": the first verdict's prompt hunts for gaps the artifacts do not cite; a later
  look (full re-judge or delta) only checks that named gaps were repaired and no change opened one.
- The texts landed in GPT's words: J2 coverage line plus "Hunt parameter regimes and regions, not examples.", J4
  completion condition, J6 experience/number split, point 26's prompt sentence, J3 FAIL text in both checker prompts and
  lane 1's FAIL/UNSETTLED rows, J1's `measurement:` rewording, point 27's two art-brief fixes.
- The calibration's planted cases go both ways and include routing, a mixed experience-and-number row and a serious late
  gap; a refusal routed the wrong way does not count as the planted refusal.
No network, no model: the claude calls are stubbed."""
import json
import os
import re
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, HERE)

FAILS = []


def check(name, ok, got=""):
    print("%s %s%s" % ("ok  " if ok else "FAIL", name, "" if ok else "  got: %r" % (str(got)[:400],)))
    if not ok:
        FAILS.append(name)


def src(rel):
    """A source file flattened, with adjacent Python string literals joined ("a "\n "b" reads "a b")."""
    with open(os.path.join(REPO, rel), encoding="utf-8") as f:
        return re.sub(r'" "', "", " ".join(f.read().split()))


def flat(s):
    return " ".join(str(s).split())


def late_gap(**kw):
    g = {"what": "sc_oil_out passes on a lantern still lit at zero oil", "where": "scenes.json sc_oil_out",
         "ids": ["oil_out"], "return_to": 3, "new_since": "late", "miss_of": "rm-coverage-judge-1",
         "late_why": "round 1 passed oil_out without reading sc_oil_out's expect", "bar_kind": "experience",
         "severity": "problem"}
    g.update(kw)
    return g


def gate_cases():
    import bar_rule as BR
    cases = (("serious + confirmed blocks", late_gap(late_confirmed=True), True),
             ("serious + unconfirmed is advisory", late_gap(late_confirmed=False), False),
             ("minor + confirmed is advisory", late_gap(severity="polish", late_confirmed=True), False),
             # Was "a round-1 gap blocks whatever its severity" (our reading of the 2026-11-16 card's point 26, which
             # answered only late gaps). The owner's card of 2026-11-17 ("the judge refuses flaws, not polish",
             # design/specs/2026-11-17-judge-flaws-not-polish/6_proposed_ruling_plain.md, "Two bugs fixed", first bug)
             # names that a bug: a finding the judge itself rated polish blocks on no look. A round-1 problem still
             # blocks (item RIMMANDRAKE_UNBLOCK_POLISH_GAPS_EVERY_LOOK_NOT_LATE_ONLY).
             ("round-1 problem gap blocks",
              late_gap(new_since="first", miss_of=None, severity="problem"), True),
             ("round-1 polish gap does not block (owner by card 2026-11-17)",
              late_gap(new_since="first", miss_of=None, severity="polish"), False),
             ("a late gap with no severity is advisory", late_gap(severity=None, late_confirmed=True), False))
    for name, g, want in cases:
        b, why = BR.blocks(g)
        check("late-gap rule: %s" % name, b is want, (b, why))


def reader_cases():
    import coverage_judge as CJ
    gp = CJ.SCHEMA["properties"]["gaps"]["items"]
    check("judge schema: every gap carries `severity` (problem | polish)",
          "severity" in gp["required"] and gp["properties"].get("severity", {}).get("enum") == ["problem", "polish"],
          gp["properties"].get("severity"))
    rp = CJ.READER_SCHEMA["properties"]["grades"]["items"]
    check("reader schema: every grade carries `serious`", "serious" in rp["required"], rp["required"])
    crit = {"oil_out": "leaf oil_out", "light": "leaf light"}
    for name, reader, want in (("a reader confirming it", lambda items: [
            {"criterion_verdict": "sound", "criterion_why": "w", "bar_kind": "experience", "serious": True}
            for _ in items], True),
            ("a reader not confirming it", lambda items: [
                {"criterion_verdict": "sound", "criterion_why": "w", "bar_kind": "experience", "serious": False}
                for _ in items], False),
            ("the program reader (no model)", None, False)):
        rec = {"gaps": [late_gap(criterion_verdict="sound"), dict(late_gap(), new_since="first", miss_of=None,
                                                                   ids=["light"])]}
        CJ.second_read(rec, crit, reader)
        g = rec["gaps"][0]
        check("second read: %s sets late_confirmed %s" % (name, want), g.get("late_confirmed") is want, g)
        check("second read: %s leaves a round-1 gap without late_confirmed" % name,
              "late_confirmed" not in rec["gaps"][1], rec["gaps"][1])
    items = CJ.reader_items({"gaps": [late_gap()]}, crit)[1]
    check("reader items: a late gap is shown as late with its why", items and items[0].get("late") is True
          and items[0].get("late_why"), items)
    check("reader prompt: asks whether a late refusal is a serious Problem a player would reject",
          "serious" in CJ.reader_prompt(items) and "player would reject" in CJ.reader_prompt(items))


def run_cases():
    import selftest_bar_rule_tuning_numbers as B
    import concept_tree as CT
    import coverage_judge as CJ
    import designer_stage as DS
    DS.owner_away = lambda: (False, "selftest: attended")
    CT.coverage_problem = lambda d, repo, tree: "no coverage signature"
    DS.exam_errors = lambda ex, d, st, repo=None: []
    CT.sign = lambda d, by, repo=None, **kw: []
    CJ.NOT_COVERED_LIMIT = CJ.JUDGE_RUNS_MAX = 10 ** 6
    CJ.JUDGE_SPEND_MAX = 10 ** 15
    real_status, CJ.RC.status = CJ.RC.status, (lambda family: "CALIBRATED")
    env = {k: os.environ.get(k) for k in ("RM_REFUSAL_DIR", "RM_OPS_WATCH_DIR", "RM_DISPATCHER_STATE")}
    try:
        with tempfile.TemporaryDirectory() as root:
            ops = os.path.join(root, "ops")
            os.makedirs(ops)
            os.environ.update(RM_REFUSAL_DIR=os.path.join(root, "refusals"), RM_OPS_WATCH_DIR=ops,
                              RM_DISPATCHER_STATE=os.path.join(root, "dispatcher"))
            d = B.concept(root, "Late0")
            text1 = flat(CJ.prompt(d, root, ["inv_throw"], False, 1))
            text2 = flat(CJ.prompt(d, root, ["inv_throw"], True, 2))
            open_line = "Look for gaps the artifacts do not cite"
            check("round 1: the open search is in the first verdict's prompt", open_line in text1, text1[:300])
            check("round 2: a full re-judge's prompt has no open search", open_line not in text2, text2[:300])
            check("round 2: a full re-judge only checks that named gaps were repaired",
                  "only check that each gap an earlier verdict named was repaired" in text2, text2[-900:])
            for n, (serious, want) in enumerate(((True, True), (False, False), (None, False))):
                d = B.concept(root, "Late%d" % (n + 1))
                rec, _ = CJ.run(d, root, B.script([B.answer("not_covered", [B.true_gap()])]), reader=None)
                with open(os.path.join(d, CJ.FIXES_FILE), "w") as f:
                    json.dump({"against": rec["judge"], "claims": [{"gap": "g1", "evidence": "scenes.json sc_wall"}]}, f)
                dp = CJ.delta_plan(d, CJ.prior_verdict(d))
                if n == 0:
                    check("round 2: the delta prompt has no open search",
                          dp is not None and open_line not in flat(CJ.delta_prompt(d, root, dp, 2)), dp)
                late = B.true_gap(ids=["inv_throw"], what="the throw lands items inside the wall", new_since="late",
                                  late_why="the earlier pass did not read sc_throw's landing claim",
                                  where="scenes.json sc_throw", severity="problem",
                                  observed="sc_throw asserts steel lands two cells out; the wall is one cell out",
                                  would_pass="sc_throw asserts the stack lands outside the wall")
                reader = None if serious is None else (lambda s: lambda items: [
                    {"criterion_verdict": "sound", "criterion_why": "a fair bar", "bar_kind": "experience",
                     "serious": s} for _ in items])(serious)
                rec2, _ = CJ.run(d, root, B.script([B.answer("not_covered", [late], rows=B.ROWS_ALL_OK)]),
                                 reader=reader)
                blocking = [g for g in rec2.get("gaps") or [] if g.get("ids") == ["inv_throw"]]
                label = {True: "a reader confirming it", False: "a reader not confirming it",
                         None: "no model reader"}[serious]
                check("run: a serious late gap with %s %s" % (label, "blocks" if want else "is advisory"),
                      bool(blocking) is want and (want or any(a.get("ids") == ["inv_throw"]
                                                              for a in rec2.get("advisory_gaps") or [])),
                      (rec2.get("verdict"), rec2.get("gaps"), rec2.get("advisory_gaps")))
    finally:
        CJ.RC.status = real_status
        for k, v in env.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v


def text_cases():
    import coverage_judge as CJ
    import bar_rule as BR
    with tempfile.TemporaryDirectory() as root:
        d = os.path.join(root, "design", "concepts", "X")
        os.makedirs(d)
        p1 = flat(CJ.prompt(d, root, ["a"], False, 1))
        p2 = flat(CJ.prompt(d, root, ["a"], True, 2))
    for name, want in (
            ("J2 coverage line, GPT's words", "Judge the situations exercised and alternatives ruled out, rather than "
             "the number of seeds or scenes."),
            ("J2 regimes line", "Hunt parameter regimes and regions, not examples."),
            ("J4 completion condition, GPT's words", "Finish when each required capability, leaf and claim has been "
             "assessed, every failed assessment has a refusal record, and every remaining assessment has supporting "
             "evidence. Return `covered` when that review leaves no blocking gap."),
            ("J6 experience/number split, GPT's words", "Separate each row's stated player-facing experiences from its "
             "tuning data. Assess coverage of every stated experience."),
            ("J6 unspecified intent", "`intended experience unspecified in source`")):
        check("coverage prompt: %s" % name, want in p1 and want in p2, p1[:200])
    check("coverage prompt: the old 'Answer `covered` only when you found no gap.' is gone",
          "Answer `covered` only when you found no gap." not in p1)
    check("coverage prompt: point 26 sentence, GPT's words", "Tag a newly discovered gap on unchanged material `late` "
          "and explain the earlier miss. The program determines its blocking status from the recorded history." in p2,
          p2[:300])
    check("coverage prompt: the late rule says serious and second-reader-confirmed",
          "second reader" in p2 and "`severity` `problem`" in p2 and "stored as advisory: it blocks nothing" not in p2)
    check("coverage prompt: round 1 no longer says a later find 'never blocks'", "never blocks" not in p1)
    check("bar_rule docstring: the late rule is serious and confirmed", "late_confirmed" in (BR.__doc__ or ""))
    fail = ("For each defect, state what you ran and saw, the attainable command result or observation that would "
            "satisfy its clause, and the smallest product fix, proof repair, environment repair or clarification "
            "needed to reach it")
    rel_src, wall_src = src("src/RimMandrake/rimflow/relentless.py"), src("src/RimMandrake/rimflow/relentless_wall.py")
    check("J3: the unwalled checker's FAIL line is GPT's", fail in rel_src and "so the next worker can fix it" not in
          rel_src)
    check("J3: the walled checker's FAIL line is GPT's", fail in wall_src and "so the next worker can fix it" not in
          wall_src)
    import relentless_wall as RW
    rule = flat(" ".join(RW.RULE))
    check("J1: the checker's measurement cause is GPT's rewording", "'measurement:' the proof or contract is wrong. "
          "This includes demonstrated incompatible acceptance demands. Quote the demands, explain the incompatibility, "
          "and state the clarification needed to make passing attainable." in rule, rule[1500:2300])
    mat = src("src/RimMandrake/rimflow/maturation.py")
    check("J3: lane 1 FAIL and UNSETTLED rows carry a path, GPT's words",
          "A FAIL row names the violated bar, the reproducing case and the attainable result that would pass it. An "
          "UNSETTLED row states what remains undecided and the specific case, evidence or instrument that would settle "
          "it." in mat and "A row you cannot decide is UNSETTLED, with its reason." not in mat)
    art = src("design/RimMandrake/art_judge_brief.md")
    check("point 27: checklist step 2 applies E3, GPT's words", "2. Owner-kept? Apply E3. Flag concerns in the report. "
          "Any replacement follows its authorized art-eval regen route, shadow-sheet notice and one-click revert." in art)
    check("point 27: the north-from-south example is a rear-view redraw",
          "Redraw north.png as a rear view of the same subject, preserving its proportions, palette and scale." in art
          and "turned 180 degrees" not in art)


def calibration_cases():
    import coverage_calibration as CC
    planted = {c["id"]: c["expect"] for c in CC.planted()}
    for cid, exp in (("bad_conflict_routing", "refuse"), ("bad_mixed_row", "refuse"), ("bad_late_serious", "refuse"),
                     ("good_round2_repaired", "pass"), ("good_lanterns", "pass"), ("good_lanterns_tuning", "pass")):
        check("calibration: planted case %s expects %s" % (cid, exp), planted.get(cid) == exp, planted)
    sound = {"criterion_verdict": "sound", "new_since": "first"}
    flawed = {"criterion_verdict": "flawed", "new_since": "first"}
    late_ok = {"criterion_verdict": "sound", "new_since": "late", "late_confirmed": True}
    for name, route, gaps, want in (
            ("no blocking gap is a pass", "designer", [], "pass"),
            ("a criteria-routed refusal on the conflict case", ("criteria", "owner"), [flawed], "refuse"),
            ("a refusal sent to his answer (return_to 2) on the conflict case", ("criteria", "owner"),
             [dict(sound, return_to=2)], "refuse"),
            ("a Designer-routed refusal on the conflict case is misrouted", ("criteria", "owner"),
             [dict(sound, return_to=3)], "misrouted"),
            ("a his-answer refusal on a bad scene case is misrouted", "designer", [dict(sound, return_to=2)],
             "misrouted"),
            ("a judge confessing the criterion flawed routes to criteria", "criteria",
             [dict(sound, judge_criterion_verdict="unattainable")], "refuse"),
            ("a Designer-routed refusal on a bad scene case", "designer", [sound], "refuse"),
            ("a criteria-only refusal on a bad scene case is misrouted", "designer", [flawed], "misrouted"),
            ("a confirmed late gap on the late case", "late", [late_ok], "refuse"),
            ("an unfixed gap instead of the late one is misrouted", "late", [sound], "misrouted"),
            ("any blocking gap on a pass case is a refusal", None, [sound], "refuse")):
        got = CC.outcome(route, gaps)
        check("calibration outcome: %s" % name, got == want if want != "misrouted" else got.startswith("refuse, "
                                                                                                      "misrouted"), got)
    with tempfile.TemporaryDirectory() as root:
        staged = {cid: (exp, d) for cid, exp, d in CC.stage(root)}
        late_d = staged.get("bad_late_serious", (None, root))[1]
        check("calibration: the late case stages a prior refusing verdict",
              os.path.exists(os.path.join(late_d, "coverage_verdict.json")))
        mixed_d = staged.get("bad_mixed_row", (None, root))[1]
        try:
            rec = json.load(open(os.path.join(mixed_d, "record.json"), encoding="utf-8"))
        except OSError:
            rec = {}
        conf_d = staged.get("bad_conflict_routing", (None, root))[1]
        try:
            sheet = open(os.path.join(conf_d, "sheet.md"), encoding="utf-8").read()
        except OSError:
            sheet = ""
        check("calibration: the conflict case puts both demands in his words (no precedence settles it)",
              "OWNER:3" in sheet and "OWNER:1" in sheet, sheet[:300])
        check("calibration: the mixed row pins numbers beside an uncovered experience",
              any(r.get("id") == "inv_refuel" for r in rec.get("inventory") or []), rec.get("inventory"))


def main():
    for f in (gate_cases, reader_cases, run_cases, text_cases, calibration_cases):
        try:
            f()
        except Exception as e:  # noqa: BLE001 - the pre-fix code lacks the names; that is a failure, not a crash
            check("%s ran" % f.__name__, False, "%s: %s" % (type(e).__name__, e))
    print("%s: %d failure(s)" % ("FAIL" if FAILS else "PASS", len(FAILS)))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
