#!/usr/bin/env python3
"""selftest_wrong_check_fixed_in_sitting: the promises of design/specs/2026-11-20-wrong-check-fixed-in-sitting/boundary.md,
one test per promise, each named as the promise is. The owner's ruling of 2026-11-20 (item
RIMMANDRAKE_ENACT_WRONG_CHECK_FIXED_IN_SITTING_NOT_RETURNED): a failed or unmeasured line is classed (mod, check or scene
wrong); a wrong check is repaired in the sitting and counts only when it is seen FAIL on a plant and PASS on the real
build, or it is set aside; only a mod-wrong line or an undecided bar sends the mod back.

The reader is mutated in place on every run: each planted fault below must turn at least one test red, and the real
reader must stay green. No game, no network; every file is in a temp root."""
import json
import os
import shutil
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
TMP = tempfile.mkdtemp(prefix="wrong_check_")
os.environ["RM_DISPATCHER_STATE"] = os.path.join(TMP, "_dispatcher")
import maturation as M  # noqa: E402
import maturation_autonomy as MA  # noqa: E402
import probe_result as PR  # noqa: E402

# the build match is selftest_maturation.py's; here every row is on the walk build
M.BM.check_visit = lambda root, mod, n, tt, savegame: {"read": True, "rerun": [], "rows": {}, "walk_why": []}

MOD = "WMod"
SHA = "65926ef481"
TT6 = {"version": "0.1.0",
       "tests": {"c1": {"kind": "live", "stage": "6", "command": "python3 c1.py"},
                 "c2": {"kind": "live", "stage": "6", "command": "python3 c2.py"},
                 "c3": {"kind": "live", "stage": "6", "command": "python3 c3.py"}},
       "bars": [{"id": "b_one", "proves_at": "6", "decides": ["c1"]},
                {"id": "b_two", "proves_at": "6", "decides": ["c2", "c3"]}]}
PLANT = {"plant": "FlowRate forced to 0 in the scene", "command": "python3 c1.py --plant zero", "verdict": "FAIL",
         "evidence": "visit_1/evidence/c1_planted.json"}


def put(root, rel, data):
    p = os.path.join(root, rel)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "w", encoding="utf-8") as f:
        f.write(data if isinstance(data, str) else json.dumps(data))
    return p


def lines(rows):
    return "".join(json.dumps(r) + "\n" for r in rows)


def row(test, verdict="PASS", **kw):
    r = {"test": test, "verdict": verdict, "site_checked": True, "site": {"open_sky": True}, "game": "archmagi",
         "mod_sha": SHA, "command": "python3 %s.py" % test}
    r.update(kw)
    return r


def visit(name, rows, claims=None, reviews=None, tt=None):
    """A fresh root with WMod at in_game, visit 1 holding rows; claims ({test: pass|fail|unmeasured}) default to each
    test's last row."""
    root = os.path.join(TMP, name)
    shutil.rmtree(root, ignore_errors=True)
    c = "design/concepts/%s/" % MOD
    v = c + "version/in_game/visit_1/"
    put(root, c + "version/test_table.json", tt or TT6)
    put(root, c + "version/VERSION.json", {"version": "0.1.0"})
    if reviews is not None:
        put(root, v + "fix_reviews.jsonl", lines(reviews))
    put(root, c + "version/stage_record.json", {"mod": MOD, "version": "0.1.0", "stage": "in_game",
                                                 "moves": [{"from": "blind_challenge", "to": "in_game",
                                                            "at": "2026-11-20T10:00:00Z"}]})
    last = {}
    for r in rows:
        last[r["test"]] = r["verdict"].lower()
    claims = dict(last, **(claims or {}))
    save = put(root, "saves/w.rws", "<?xml version=\"1.0\"?><savegame><meta/></savegame>")
    put(root, v + "SUMMARY.md", "# visit 1\n\n## Exit\n```\ningame_rows: {%s}\nstrange_open: 0\nsavegame: %s\n"
        "exit_met: true\n```\n" % (", ".join("%s: %s" % kv for kv in sorted(claims.items())), save))
    put(root, v + "rows.jsonl", lines(rows))
    put(root, v + "strange.jsonl", "")
    return root


def ingame(rows, claims=None, name="v", reviews=None, tt=None):
    return M.read_ingame_exit(visit(name, rows, claims, reviews, tt), MOD, 1)


ALL_PASS = [row("c1"), row("c2"), row("c3")]


def repaired(test="c1", cls="HARNESS", planted=PLANT, commit="abc1234def", owner=None):
    rp = {"class": cls, "commit": commit}
    if planted is not None:
        rp["planted"] = planted
    return [row(test, "FAIL", **{"class": cls}), row(test, "PASS", repair=rp, **({"owner": owner} if owner else {}))]


FIXER, READER = "rm-detached-bench-drive-wmod-visit-one-1", "rm-detached-bench-route-wmod-visit-one-2"
MOD_FIX = {"commit": "def5678abc", "red": {"cmd": "python3 tests/flow.py", "rc": 1, "on": "abc1234def"},
           "green": {"cmd": "python3 tests/flow.py", "rc": 0, "on": "def5678abc"}}


def mod_fixed(fix=MOD_FIX):
    return [row("c1", "FAIL", **{"class": "MOD", "mod_sha": "abc1234def", "unit": FIXER}),
            row("c1", mod_fix=fix, unit=FIXER, mod_sha="def5678abc"), row("c2", mod_sha="def5678abc"),
            row("c3", mod_sha="def5678abc")]


def review(reader=READER, verdict="sound", fix="def5678abc"):
    return [{"fix": fix, "reader": reader, "verdict": verdict, "why": "the diff touches only the flow sum, and the "
             "before/after test reads it"}]


# ---- the promises ----------------------------------------------------------------------------------------------------

def t_all_pass_met():
    ex = ingame(ALL_PASS)
    return ex["state"] == "met" and all(ex["lines"][t]["count"] == "pass" for t in ("c1", "c2", "c3")), ex["why"]


def t_mod_wrong_not_met():
    ex = ingame([row("c1", "FAIL", **{"class": "MOD"}), row("c2"), row("c3")])
    ex2 = ingame([row("c1", "FAIL", **{"class": "MOD"}), row("c1"), row("c2"), row("c3")], name="v2")
    return (ex["state"] == "not_met" and ex["lines"]["c1"]["count"] == "mod" and ex2["state"] == "not_met"
            and ex2["lines"]["c1"]["count"] == "mod"), (ex["why"], ex2["why"])


def t_check_wrong_repaired_counts():
    ex = ingame(repaired() + [row("c2"), row("c3")])
    ln = ex["lines"]["c1"]
    return (ex["state"] == "met" and ln["count"] == "pass" and ln["class"] == "HARNESS"
            and (ln.get("repair") or {}).get("commit") == "abc1234def"
            and (ln.get("repair") or {}).get("planted", {}).get("verdict") == "FAIL"
            and ln.get("real") == "PASS"), (ex["why"], ln)


def t_repair_without_planted_not_pass():
    outs = []
    for name, planted in (("noplant", None), ("planted_pass", dict(PLANT, verdict="PASS")),
                          ("planted_noplant", dict(PLANT, plant="")), ("no_commit", PLANT)):
        ex = ingame(repaired(planted=planted, commit="" if name == "no_commit" else "abc1234def",
                             owner="RIMMANDRAKE_MEND_WMOD_FLOW_CHECK_NO_PLANT_YET")
                    + [row("c2"), row("c3")], claims={"c1": "unmeasured"}, name=name)
        outs.append((name, ex["state"], ex["lines"]["c1"]["count"], ex.get("undecided_bars")))
    return all(s == "not_met" and c == "not_counted" and u == ["b_one"] for _, s, c, u in outs), outs


def t_needless_check_is_removed():
    needless = [row("c1"), row("c2"), row("c3", "FAIL", **{"class": "HARNESS", "set_aside":
                                                          "c3 reads the wrong cell; c2 decides b_two on its own"})]
    left = ingame(needless)
    tt = json.loads(json.dumps(TT6))
    del tt["tests"]["c3"]
    tt["bars"][1]["decides"] = ["c2"]
    gone = ingame(needless, tt=tt, name="v2")
    return (left["state"] == "not_met" and left["lines"]["c3"]["count"] == "needless"
            and any("c3" in w and "remove it from the test table" in w for w in left["why"])
            and gone["state"] == "met"), (left["why"], gone["why"])


def t_not_counted_needs_owner():
    owned = ingame([row("c1", "FAIL", **{"class": "HARNESS", "unrepaired": "the fix is not known: the probe has no "
                                         "hook on the flow sum", "owner": "RIMMANDRAKE_MEND_WMOD_FLOW_PROBE_HOOK"}),
                    row("c2"), row("c3")])
    bare = ingame([row("c1", "FAIL", **{"class": "HARNESS", "unrepaired": "the fix is not known: the probe has no "
                                        "hook on the flow sum"}), row("c2"), row("c3")], name="v2")
    return (owned["lines"]["c1"]["count"] == "not_counted" and owned.get("undecided_bars") == ["b_one"]
            and owned["state"] == "not_met" and bare["lines"]["c1"]["count"] == "unhandled"
            and bare["state"] == "not_met"), (owned["why"], bare["why"])


def t_mod_fixed_in_sitting_counts():
    good = ingame(mod_fixed(), reviews=review(), name="mf_good")
    none_ = ingame(mod_fixed(), name="mf_none")
    unsound = ingame(mod_fixed(), reviews=review(verdict="unsound"), name="mf_unsound")
    own = ingame(mod_fixed(), reviews=review(reader=FIXER), name="mf_own")
    nored = ingame(mod_fixed(dict(MOD_FIX, red={"cmd": "python3 tests/flow.py", "rc": 0})), reviews=review(),
                   name="mf_nored")
    owed = all(x["state"] == "not_met" and x.get("fix_readers_owed") for x in (none_, unsound, own))
    return (good["state"] == "met" and good["lines"]["c1"]["count"] == "pass" and good["lines"]["c1"].get("mod_fix")
            and owed and nored["lines"]["c1"]["count"] == "mod"), (good["why"], none_["why"], own["why"], nored["why"])


def t_one_build_is_the_last_rows():
    ex = ingame(mod_fixed(), reviews=review(), name="ob")
    mixed = ingame(mod_fixed()[:2] + [row("c2", mod_sha="abc1234def"), row("c3", mod_sha="def5678abc")],
                   reviews=review(), name="ob2")
    return (not any("more than one build" in w for w in ex["why"])
            and any("more than one build" in w for w in mixed["why"])), (ex["why"], mixed["why"])


def t_scene_wrong_same_as_check():
    rep = ingame(repaired(cls="SITE") + [row("c2"), row("c3")])
    nop = ingame(repaired(cls="SITE", planted=None, owner="RIMMANDRAKE_STAGE_WMOD_SCENE_NO_PLANT_YET")
                 + [row("c2"), row("c3")], claims={"c1": "unmeasured"}, name="v2")
    needless = ingame([row("c1"), row("c2"), row("c3", "UNMEASURED", **{"class": "SITE"})], name="v3")
    return (rep["state"] == "met" and nop["state"] == "not_met" and nop["lines"]["c1"]["count"] == "not_counted"
            and needless["lines"]["c3"]["count"] == "needless"), (rep["why"], nop["why"], needless["why"])


def t_unclassed_not_silent():
    ex = ingame([row("c1", "UNMEASURED"), row("c2"), row("c3")])
    ex2 = ingame([row("c1", "FAIL"), row("c2"), row("c3")], name="v2")
    return (ex["state"] == "not_met" and ex["lines"]["c1"]["count"] == "unclassed"
            and ex2["state"] == "not_met" and ex2["lines"]["c1"]["count"] == "unclassed"), (ex["why"], ex2["why"])


def t_wrong_unhandled_not_silent():
    ex = ingame([row("c1", "FAIL", **{"class": "HARNESS"}), row("c2"), row("c3")])
    return (ex["state"] == "not_met" and ex["lines"]["c1"]["count"] == "unhandled"
            and any("c1" in w and "repaired" in w and "owner" in w for w in ex["why"])), ex["why"]


def t_mix_reads_each_line():
    tt = json.loads(json.dumps(TT6))
    rows = repaired("c1") + [row("c2", "FAIL", **{"class": "MOD"}), row("c3", "FAIL", **{"class": "SITE"})]
    ex = ingame(rows, name="mix")
    got = {t: ex["lines"][t]["count"] for t in tt["tests"]}
    return (ex["state"] == "not_met" and got == {"c1": "pass", "c2": "mod", "c3": "needless"}
            and not ex.get("undecided_bars")
            and sum("in-game check c2" in w for w in ex["why"]) >= 1
            and not any("in-game check c1" in w for w in ex["why"])), (got, ex["why"])


# ---- the blind cycle -------------------------------------------------------------------------------------------------

TTB = {"version": "0.1.0", "tests": {"t1": {"command": "python3 t1.py"}},
       "bars": [{"id": "b_off", "proves_at": "4-5", "decides": ["t1"]}]}


def cycle(name, against="check", plant="t1 run on a copy with the flow set to 0", touched=("tests/t1.py",),
          unit="rm-blind-judge-wmod-1", reviews=None, judge_true=True):
    root = os.path.join(TMP, name)
    shutil.rmtree(root, ignore_errors=True)
    c = "design/concepts/%s/" % MOD
    cy = c + "version/blind_challenge/cycle_1/"
    put(root, c + "version/test_table.json", TTB)
    put(root, c + "version/VERSION.json", {"version": "0.1.0"})
    put(root, c + "version/stage_record.json", {"mod": MOD, "version": "0.1.0", "stage": "blind_challenge",
                                                 "moves": [{"from": "offline_build", "to": "blind_challenge",
                                                            "at": "2026-11-20T09:00:00Z"}]})
    put(root, cy + "SUMMARY.md", "# cycle 1\n\n## Exit\noffline_bars: {b_off: green}\nproblems_open: 0\n"
        "exit_met: %s\n" % ("true" if judge_true else "false"))
    if reviews is not None:
        put(root, cy + "lane2/fix_reviews.jsonl", lines(reviews))
    put(root, cy + "lane2/reruns.jsonl", lines([{"test": "t1", "command": "python3 t1.py", "rc": 0, "result": "PASS"}]))
    fault = {"id": "CHK_A", "class": "Problem", "status": "FIXED abc1234"}
    if against:
        fault["against"] = against
    put(root, cy + "lane2/faults.json", {"faults": [fault]})
    fx = {"fault": "CHK_A", "sha": "abc1234", "red": {"cmd": "python3 t1.py --plant zero", "rc": [1]},
          "green": {"cmd": "python3 t1.py", "rc": [0]}}
    if plant:
        fx["plant"] = plant
    if unit:
        fx["unit"] = unit
    put(root, cy + "lane2/fixes.jsonl", lines([fx]))
    put(root, cy + "lane1/lane1_rows.jsonl", lines([{"id": "L_ok", "verdict": "PASS"}]))
    put(root, cy + "tests_edited.json", {"edited": [{"path": "tests/t1.py", "what": "reads the right cell"}]})
    put(root, cy + "lane2/planted_results.jsonl", lines([{"baseline": True}, {"id": "PF", "caught": True,
                                                                              "tree_clean_after": True}]))
    return root, list(touched)


def blind(name, **kw):
    root, touched = cycle(name, **kw)
    real = M._commit_paths
    M._commit_paths = lambda r, sha: PR.value(touched)
    try:
        return M.read_exit(root, MOD, 1)
    finally:
        M._commit_paths = real


def t_blind_check_repair_owes_no_judge():
    good = blind("b_good")
    as_mod = blind("b_mod", against="mod")
    unset = blind("b_unset", against=None)
    noplant = blind("b_noplant", plant="")
    touched = blind("b_touch", touched=("tests/t1.py", "src/WMod/Source/Flow.cs"))
    root, _ = cycle("b_blind")
    blindgit = M.read_exit(root, MOD, 1)       # the temp root is no git repo: git cannot look
    owed = [x["state"] == "not_met" and x["checks"].get("fix_reader_owed") == ["CHK_A"]
            for x in (as_mod, unset, noplant, touched, blindgit)]
    owed.append("COULD NOT LOOK" in str(blindgit["checks"].get("mod_fixes_why", {}).get("CHK_A")))
    return (good["state"] == "met" and good["checks"].get("check_repairs") == ["CHK_A"] and all(owed)), (
        good["why"], [x["why"][:1] for x in (as_mod, unset, noplant, touched)])


BLIND_REVIEW = [{"fault": "CHK_A", "reader": "rm-steward-wmod-cycle-one-2", "verdict": "sound",
                 "why": "the fix changes the flow sum only, and t1 reads it red before and green after"}]


def t_blind_mod_fix_owes_one_fresh_reader():
    good = blind("bm_good", against="mod", reviews=BLIND_REVIEW)
    judge_false = blind("bm_false", against="mod", reviews=BLIND_REVIEW, judge_true=False)
    none_ = blind("bm_none", against="mod")
    unsound = blind("bm_unsound", against="mod", reviews=[dict(BLIND_REVIEW[0], verdict="unsound")])
    own = blind("bm_own", against="mod", reviews=[dict(BLIND_REVIEW[0], reader="rm-blind-judge-wmod-1")])
    nounit = blind("bm_nounit", against="mod", reviews=BLIND_REVIEW, unit=None)
    owed = all(x["state"] == "not_met" and x["checks"].get("fix_reader_owed") == ["CHK_A"]
               for x in (none_, unsound, own, nounit))
    return (good["state"] == "met" and judge_false["state"] == "met" and owed), (
        good["why"], judge_false["why"], [x["why"][:1] for x in (none_, unsound, own, nounit)])


# ---- the briefs ------------------------------------------------------------------------------------------------------

BRIEF_PINS = ("mod wrong", "check wrong", "scene wrong", "Test 1", "Test 2", "FAIL on a planted fault",
              "never sends the mod back", "remove it from the test table", "fix it in the sitting",
              "one fresh reader", "maturation.py red-seen")
# the free game rule rides only the briefs whose fix can need the game; the offline-stage fixer keeps its ban
FREE_GAME = ("in-game driver", "blind judge", "live fixer")


def t_briefs_carry_the_rule():
    root = visit("briefs", ALL_PASS)
    texts = {"in-game driver": M.ingame_brief_text(root, MOD)[0],
             "blind judge": M.blind_brief_text(root, MOD)[0],
             "steward (router)": MA.steward_brief(root, MOD, {"steward_kind": "exit_not_met", "stage": "in_game",
                                                              "mod": MOD, "why": "x", "decision": "steward"}),
             "fixer": MA.fixer_brief("RIMMANDRAKE_FIX_SELFTEST_LINE_ONE_OF_ONE", MOD, 1.0),
             "live fixer": MA.fixer_brief("RIMMANDRAKE_FIX_SELFTEST_LINE_ONE_OF_ONE", MOD, 1.0, live=True)}
    flat = {k: " ".join(v.split()) for k, v in texts.items()}
    lacks = ["%s lacks %r" % (k, p) for k, v in flat.items() for p in BRIEF_PINS if p not in v]
    lacks += ["%s lacks the free game rule" % k for k in FREE_GAME if "bridge take --idle-ok" not in flat[k]]
    lacks += ["the offline fixer brief lost its game ban, or gained the free game rule"
              for v in [flat["fixer"]] if "Never take the bridge or a game." not in v or "bridge take --idle-ok" in v]
    stale = ["%s still says %r" % (k, s) for k, v in flat.items()
             for s in ("a check you judge wrong is a note to the Conductor", "File EACH failed or UNMEASURED line",
                       "A failed or UNMEASURED line is filed as a NAMED item", "set it aside", "set_aside",
                       "new blind judge is owed", "Do not fix the mod in the sitting") if s in v]
    import maturation_dispatch as MD
    builders = {"offline builder": M.brief_text(root, MOD)[0],
                "certificate builder": MD.cert_brief(MOD, {"T_ONE": "RIMMANDRAKE_GREEN_WMOD_T_ONE_RED_DECIDER_ONLY"}, 1.0, {"T_ONE": ["b_one"]})}
    lacks += ["%s lacks the red-seen line" % k for k, v in builders.items() if "maturation.py red-seen" not in v]
    return not lacks and not stale, lacks + stale


def run(tests, quiet=False):
    fails = []
    for fn in tests:
        name = fn.__name__[2:].replace("_", "-")
        try:
            good, got = fn()
        except Exception as e:  # noqa: BLE001 - a test that raises is a failure by name, never a pass
            good, got = False, "%s: %s" % (type(e).__name__, e)
        if not quiet:
            print("%s  %s%s" % ("PASS" if good else "FAIL", name, "" if good else "  got: %r" % (got,)))
        if not good:
            fails.append(name)
    return fails


# the planted faults: each replaces one part of the reader with a wrong one and must turn a test red
def _mutants():
    real_shown, real_class, real_repair = M.repair_shown, M.line_class, M.check_repair
    yield "a repair counts with no planted reading", "repair_shown", lambda r: None
    yield "a HARNESS line counts as a pass", "line_class", lambda r, earlier, tt=None: (
        "pass" if str(r.get("class", "")).upper() == "HARNESS" else real_class(r, earlier, tt))
    yield "an unclassed line is not counted", "line_class", lambda r, earlier, tt=None: (
        "not_counted" if not r.get("class") and r.get("verdict") != "PASS" else real_class(r, earlier, tt))
    yield "every blind Problem is a check repair", "check_repair", lambda root, x, fx, edited: (True, None)
    yield "no blind Problem is a check repair", "check_repair", lambda root, x, fx, edited: (False, "planted")
    yield "a mod fix counts with no red run", "mod_fix_shown", lambda r: None
    yield "every fix review is sound", "review_sound", lambda reviews, key, maker: (True, None)
    del real_shown, real_repair


def missed_mutants(tests):
    """-> the planted faults that turned no test red (each is put back after its run)."""
    missed = []
    for what, attr, fake in _mutants():
        real = M.__dict__[attr]
        setattr(M, attr, fake)
        try:
            if not run(tests, quiet=True):
                missed.append(what)
        finally:
            setattr(M, attr, real)
    return missed


def main():
    tests = [t_all_pass_met, t_mod_wrong_not_met, t_check_wrong_repaired_counts, t_repair_without_planted_not_pass,
             t_needless_check_is_removed, t_not_counted_needs_owner, t_mod_fixed_in_sitting_counts,
             t_one_build_is_the_last_rows, t_scene_wrong_same_as_check, t_unclassed_not_silent,
             t_wrong_unhandled_not_silent, t_mix_reads_each_line, t_blind_check_repair_owes_no_judge,
             t_blind_mod_fix_owes_one_fresh_reader, t_briefs_carry_the_rule]
    fails = run(tests)
    missed = missed_mutants(tests) if not fails else []
    shutil.rmtree(TMP, ignore_errors=True)
    if fails or missed:
        print("FAIL selftest_wrong_check_fixed_in_sitting: %d test(s) red, %d planted fault(s) not caught%s" % (
            len(fails), len(missed), "".join("\n  - NOT CAUGHT: " + m for m in missed)))
        return 1
    print("PASS selftest_wrong_check_fixed_in_sitting: %d tests; every planted fault caught" % len(tests))
    return 0


if __name__ == "__main__":
    sys.exit(main())
