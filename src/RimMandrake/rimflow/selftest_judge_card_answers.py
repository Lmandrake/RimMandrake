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
import subprocess
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
            # The owner's trial of 2026-11-17 (7_same_problem_rule.md rule 4): on the check of the repairs a new
            # finding on unchanged material is advisory however serious; one that quotes a passage a repair changed
            # blocks when it is a `problem` the reader confirms. It was "a confirmed late gap blocks" (card 2026-11-16).
            for n, (serious, want, changed) in enumerate(((True, False, False), (False, False, False),
                                                          (None, False, False), (True, True, True),
                                                          (False, False, True))):
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
                if changed:   # the repair rewrote sc_throw's claim, and the finding quotes the new words
                    with open(os.path.join(d, "scenes.json"), "w") as f:
                        json.dump({"scenes": [{"id": "sc_throw", "asserts": "steel lands one cell out"}]}, f)
                    late.update(new_since="changed", since='scene:sc_throw\n"asserts": "steel lands one cell out"',
                                observed="sc_throw asserts steel lands one cell out; the wall is one cell out")
                reader = None if serious is None else (lambda s: lambda items: [
                    {"criterion_verdict": "sound", "criterion_why": "a fair bar", "bar_kind": "experience",
                     "serious": s} for _ in items])(serious)
                rec2, _ = CJ.run(d, root, B.script([B.answer("not_covered", [late], rows=B.ROWS_ALL_OK)]),
                                 reader=reader)
                blocking = [g for g in rec2.get("gaps") or [] if g.get("ids") == ["inv_throw"]]
                label = {True: "a reader confirming it", False: "a reader not confirming it",
                         None: "no model reader"}[serious]
                label += " on %s material" % ("changed" if changed else "unchanged")
                check("run: a serious new gap with %s %s" % (label, "blocks" if want else "is advisory"),
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
        # the recalibration's three cases (RIMMANDRAKE_RECALIBRATE_JUDGE_THEN_RESTAMP_PYRELANDS_ONCE) and the late case
        # under the same-problem rule (7_same_problem_rule.md rule 4: the new gap quotes a passage a repair changed)
        for cid, exp in (("good_pyrelands_look8", "pass"), ("bad_fire_never_touched", "refuse"),
                         ("good_one_kind_enough", "pass")):
            check("calibration: planted case %s expects %s" % (cid, exp), planted.get(cid) == exp, planted)
        import coverage_judge as CJ
        prior = CJ.prior_verdict(late_d) or {}
        red = '"expect": "at 1 PM the first lantern holds 0 oil and its cells still read at least 50% within 2 cells"'
        check("calibration: the late case's prior holds the renderings from before the repair, and its red is a "
              "changed passage", CJ.changed_passage({"since": "scene:sc_oil_out\n" + red}, prior.get("entry_text"),
                                                    CJ.entry_texts(late_d)) is not None, sorted(prior)[:12])
        pyr_d = staged.get("good_pyrelands_look8", (None, root))[1]
        pv = CJ.prior_verdict(pyr_d) or {}
        dp = CJ.delta_plan(pyr_d, pv) if pv else None
        check("calibration: the Pyrelands case is look 8's input (look 7's refusal on file), judged as a delta "
              "carrying its three gaps", pv.get("judge") == "rm-coverage-judge-1794938280" and dp is not None
              and len(dp["claimed_gaps"]) + len(dp["carried"]) == 3, (pv.get("judge"), dp and len(dp["carried"])))
        fire_d = staged.get("bad_fire_never_touched", (None, root))[1]
        sc = json.load(open(os.path.join(fire_d, "scenes.json"), encoding="utf-8"))
        check("calibration: the fire case's only straw scene never puts the lantern on straw",
              any(x["id"] == "sc_straw_safe" and "no straw anywhere" in " ".join(x["start"]) for x in sc["scenes"]))
        # judge() reads a later look as run() does: the slot decides (a stubbed model, no spend)
        rep_d = staged["good_round2_repaired"][1]
        rows = [{"id": i, "evidence": ["scenes.json", "tree.json", "record.json", "sheet.md", "floor.json",
                                       "exam.json"], "parts": [{"what": i, "scene": "sc_light", "ok": True}]}
                for i in ("inv_light", "inv_oil", "light", "oil_out")]
        saved = CC.subprocess.run
        try:
            for repaired, want in ((True, "pass"), (False, "refuse")):
                out = json.dumps({"structured_output": {"verdict": "covered", "gaps": [], "reasons": "r",
                                                        "checklist": rows, "repairs": [
                                                            {"gap": "g1", "repaired": repaired, "evidence": "x"}]}})
                CC.subprocess.run = lambda *a, **k: subprocess.CompletedProcess(a, 0, out, "")
                got, det = CC.judge(root, rep_d, CC.ROUTE["good_round2_repaired"], reader=None)
                check("calibration judge: the repaired case with g1 answered %s reads %s" % (repaired, want),
                      got == want, (got, det))
            # a well-formed refusal on the bad scene case refuses; an answer missing an owed row is no pass
            bad_d = staged["bad_scene_no_control"][1]
            ev = ["scenes.json", "tree.json", "record.json", "sheet.md", "floor.json", "exam.json"]
            brows = [{"id": i, "evidence": ev, "parts": [{"what": i, "scene": "sc_light",
                                                          "ok": i not in ("light", "inv_light")}]}
                     for i in ("inv_light", "inv_oil", "light", "oil_out")]
            bgap = {"what": "sc_light has no control and no asserted start", "where": "scenes.json sc_light",
                    "return_to": 3, "ids": ["light", "inv_light"], "new_since": "first", "bar_kind": "experience",
                    "severity": "problem", "evidence": ["scenes.json", "tree.json"],
                    "observed": "sc_light has no control; its start is 'quicktest map'",
                    "would_pass": "sc_light asserts a dark lamp-free room at midnight and a 0-oil control stays dark",
                    "smallest_fix": {"what": "add a control and an asserted start to sc_light", "attainable": "yes",
                                     "cost": "edit"}, "criterion_verdict": "sound",
                    "criterion_why": "A lit room is checkable against a dark control in one scene.",
                    "promise": "A lantern should light the room around it", "owner_said": True}
            for name, rows_, want in (("a well-formed refusal", brows, "refuse"),
                                      ("an answer missing an owed row", brows[:2], "incomplete")):
                out = json.dumps({"structured_output": {"verdict": "not_covered", "gaps": [bgap], "reasons": "r",
                                                        "checklist": rows_, "repairs": []}})
                CC.subprocess.run = lambda *a, **k: subprocess.CompletedProcess(a, 0, out, "")
                got, det = CC.judge(root, bad_d, CC.ROUTE["bad_scene_no_control"], reader=lambda items: [
                    {"criterion_verdict": "sound", "criterion_why": "The bar names an experience one staged scene can "
                     "show.", "bar_kind": "experience", "serious": False} for _ in items])
                check("calibration judge: %s on the bad scene case reads %s" % (name, want),
                      str(got).startswith(want), (got, det.get("malformed")))
            # a broken record is re-asked once in the same session, as run() does; the fixed answer counts
            broken = dict(bgap, evidence=["sheet.md:99"], observed="nothing measured here")
            outs = [json.dumps({"structured_output": {"verdict": "not_covered", "gaps": [g_], "reasons": "r",
                                                      "checklist": brows, "repairs": []}, "session_id": "s1"})
                    for g_ in (broken, bgap)]
            calls = []

            def two(argv, *a, **k):
                calls.append(argv)
                return subprocess.CompletedProcess(argv, 0, outs[min(len(calls), 2) - 1], "")
            CC.subprocess.run = two
            got, det = CC.judge(root, bad_d, CC.ROUTE["bad_scene_no_control"], reader=lambda items: [
                {"criterion_verdict": "sound", "criterion_why": "The bar names an experience one staged scene can "
                 "show.", "bar_kind": "experience", "serious": False} for _ in items])
            check("calibration judge: a broken record is re-asked once in the same session, and its fix counts",
                  got == "refuse" and len(calls) == 2 and "--resume" in calls[1] and det.get("reasked"),
                  (got, len(calls), det.get("malformed")))
        finally:
            CC.subprocess.run = saved


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
