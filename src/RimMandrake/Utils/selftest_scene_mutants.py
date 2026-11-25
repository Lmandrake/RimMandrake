#!/usr/bin/env python3
"""Offline acceptance of scene_mutants (RIMMANDRAKE_BUILD_MUTANTS_BY_OVERLAY_AUTHOR_DOES_NOT_CHOOSE). No game. Lists, verdicts and
traces are hand-made (traces in schema scene_trace_v1, design/specs/2026-11-23-bridge-v2/boundary.md §THE TRACE). The promises:
boundary.md §MUTANTS AND SHOWN BOTH WAYS; each test here has a promise's name. The 13 checks of the build order are the first 13;
the last three cover the list review, the kill itself and the history line.

Planted faults that turned this red, each seen 2026-11-25 (recorded on the item): the FEATURE_OFF rule removed from lint
(t_feature_off_mutant_is_refused); a witness compared by its last value only (t_red_with_unchanged_witness_reads_mutant_not_used);
the fixture hash not compared (t_both_runs_start_from_one_fixture_hash); the stamp rule removed from scene_verdicts.bar_refusal
(t_red_receipt_never_counts_as_pass)."""
import copy
import json
import os
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
for _p in (HERE, os.path.join(HERE, "..", "rimflow")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import scene_mutants as M  # noqa: E402
import scene_verdicts as SV  # noqa: E402

KB = "RimMandrake.ExplosiveKnockback.RimMandrakeExplosiveKnockbackSettings"
FIX = {"name": "RM_Stage_ExplosiveKnockback", "sha256": "ab" * 32}


def good_list():
    return {"schema": M.SCHEMA, "mod": "ExplosiveKnockback", "feature_switches": [KB + ".enabled"],
            "bars": {"carried_thing_own_arc": {"scenes": ["scene_pawn_arc_carried_thing"], "written_by": "UNIT_A",
                                               "reviewed_by": "UNIT_B", "review": "both mutants break the carried arc, not the throw"}},
            "mutants": [
                {"name": "light_limit_5", "bar": "carried_thing_own_arc", "kind": "live", "change": "value", "breaks": "success",
                 "apply": {"setting": KB + ".lightMassLimit", "value": "5"}, "witness": {"track": "steel_flyer"}},
                {"name": "carried_drops_in_hand", "bar": "carried_thing_own_arc", "kind": "compiled", "change": "branch",
                 "breaks": "success", "flag": "RM_MUTANT_CARRIED_STAYS", "witness": {"track": "steel_flyer"}},
                {"name": "carried_plant_wrong_cell", "bar": "carried_thing_own_arc", "kind": "live", "change": "target",
                 "breaks": "success", "apply": {"plant": "carried_plant_wrong_cell"}, "witness": {"track": "steel_cell"}},
            ]}


def trace(vals, track="steel_flyer", start=1000):
    rows = [{"rec": "open", "tick": start, "phase": "first", "rand": "42", "schema": "scene_trace_v1"}]
    for off, v in enumerate(vals):
        rows.append({"rec": "track", "tick": start + off, "phase": "end_of_tick", "name": track, "st": "ok", "v": v})
    rows.append({"rec": "end", "tick": start + len(vals), "phase": "end_of_tick", "state": "hit"})
    for i, r in enumerate(rows, 1):
        r["n"] = i
    return rows


def side(outcome="SUCCESS", exposure=True, counts=None, failed=None, vals=(0, 1, 1), fixture=FIX, track="steel_flyer"):
    return {"verdict": {"outcome": outcome, "failed": failed, "evidence": {"exposure": exposure},
                        "counts_for_bar": (outcome == "SUCCESS") if counts is None else counts},
            "fixture": dict(fixture) if fixture else None, "rows": trace(vals, track)}


def red(outcome="MOD FAILURE", cond="success", vals=(0, 0, 0), counts=False, **kw):
    return side(outcome, counts=counts, failed={"condition": cond, "tick": 1002, "observed": []} if outcome == "MOD FAILURE" else None,
                vals=vals, **kw)


LIVE = good_list()["mutants"][0]


def names(faults):
    return {f[0] for f in faults}


# ---- the 13 checks of the build order
def t_feature_off_mutant_is_refused():
    lst = good_list()
    assert M.lint(lst, None) == [], M.lint(lst, None)
    lst["mutants"][0]["apply"] = {"setting": KB + ".enabled", "value": "False"}
    assert "FEATURE_OFF" in names(M.lint(lst, None)), M.lint(lst, None)
    lst = good_list()
    lst["mutants"][0]["apply"] = {"setting": KB + ".lightMassLimit", "value": "0"}   # a wrong number, not the master switch
    assert M.lint(lst, None) == [], M.lint(lst, None)
    lst = good_list()
    del lst["feature_switches"]                                                      # no switch named: cannot tell, refused
    assert "NO_FEATURE_SWITCHES" in names(M.lint(lst, None))


def t_mutant_must_name_a_bar():
    lst = good_list()
    del lst["mutants"][0]["bar"]
    assert "NO_BAR" in names(M.lint(lst, None))
    lst = good_list()
    lst["mutants"][0]["bar"] = "no_such_bar"
    assert "UNKNOWN_BAR" in names(M.lint(lst, {"carried_thing_own_arc"}))


def t_draw_is_same_for_one_scene_and_build():
    lst = good_list()
    a = M.draw(lst, "ExplosiveKnockback", "scene_pawn_arc_carried_thing", "c0ffee" * 6)
    b = M.draw(copy.deepcopy(lst), "ExplosiveKnockback", "scene_pawn_arc_carried_thing", "c0ffee" * 6)
    assert a["name"] == b["name"]
    shuffled = copy.deepcopy(lst)
    shuffled["mutants"].reverse()                                      # the list's order does not steer the draw
    assert M.draw(shuffled, "ExplosiveKnockback", "scene_pawn_arc_carried_thing", "c0ffee" * 6)["name"] == a["name"]
    drawn = {M.draw(lst, "ExplosiveKnockback", "scene_pawn_arc_carried_thing", "%040x" % i)["name"] for i in range(60)}
    assert len(drawn) == 3, drawn                                       # over builds, every mutant is drawn


def t_scene_cannot_set_the_draw():
    lst = good_list()
    for src in ("MUTANT = 'light_limit_5'\n", "import scene\nscene.accept('x.py', 'light_limit_5')\n", "seed = 7\n"):
        try:
            M.draw(lst, "ExplosiveKnockback", "scene_pawn_arc_carried_thing", "c0ffee" * 6, scene_src=src)
        except M.Refused as e:
            assert e.name == "SCENE_SETS_DRAW", e
        else:
            raise AssertionError("a scene that sets its draw was not refused: %r" % src)
    ok = "import scene\nplanted = scene.plant() == 'light_limit_5'\n"
    M.draw(lst, "ExplosiveKnockback", "scene_pawn_arc_carried_thing", "c0ffee" * 6, scene_src=ok)
    import inspect
    assert set(inspect.signature(M.draw).parameters) == {"lst", "mod", "scene", "build", "scene_src"}


def t_red_receipt_never_counts_as_pass():
    clean = {"rec": "run", "run": "s:r", "scene": "x", "claim": "c", "build": "b", "outcome": "SUCCESS", "receipt": "h",
             "overlay": "none", "tainted": False, "arm": "reference", "build_kind": "RELEASE", "map_kind": "settlement", "stamps": []}
    assert SV.bar_refusal(clean) is None, SV.bar_refusal(clean)
    redline = dict(clean, stamps=["PLANTED light_limit_5"])
    assert SV.bar_refusal(redline).startswith("NOT COUNTED: a red run"), SV.bar_refusal(redline)
    r = M.judge_both_ways(LIVE, side(), red(counts=True))
    assert r["verdict"] == M.RED_COUNTED, r


def t_red_success_reads_mutant_not_killed():
    r = M.judge_both_ways(LIVE, side(), red("SUCCESS", vals=(0, 0, 0)))
    assert r["verdict"] == M.NOT_KILLED and "not killed" in r["why"], r


def t_red_without_exposure_proves_nothing():
    r = M.judge_both_ways(LIVE, side(), red(exposure=False))
    assert r["verdict"] == M.NO_EXPOSURE and "proves nothing" in r["why"], r


def t_red_with_unchanged_witness_reads_mutant_not_used():
    r = M.judge_both_ways(LIVE, side(vals=(0, 1, 1)), red(vals=(0, 1, 1)))
    assert r["verdict"] == M.NOT_USED and "not used" in r["why"], r
    r = M.judge_both_ways(LIVE, side(vals=(0, 1, 1)), red(vals=(1, 0, 1)))   # same last value, a different course: used
    assert r["verdict"] == M.KILLED, r
    r = M.judge_both_ways(LIVE, side(), red(track="other_track"))           # not in the red trace: could not look, never "used"
    assert r["verdict"] == M.WITNESS_UNREAD, r
    many = dict(LIVE, witness={"tracks": ["other_track", "steel_flyer"]})   # several tracks: any one that differs is the witness
    assert M.judge_both_ways(many, side(vals=(0, 1, 1)), red(vals=(0, 0, 1)))["verdict"] == M.KILLED
    assert M.judge_both_ways(many, side(vals=(0, 1, 1)), red(vals=(0, 1, 1)))["verdict"] == M.WITNESS_UNREAD


def t_bar_with_one_mutant_is_refused():
    lst = good_list()
    lst["mutants"] = lst["mutants"][:1]
    assert "ONE_MUTANT" in names(M.lint(lst, None))


def t_red_failing_on_another_condition_is_reported_so():
    r = M.judge_both_ways(LIVE, side(), red(cond="forbidden"))
    assert r["verdict"] == M.OTHER_CONDITION and "forbidden" in r["why"], r


def t_both_runs_start_from_one_fixture_hash():
    r = M.judge_both_ways(LIVE, side(), red(fixture={"name": FIX["name"], "sha256": "cd" * 32}))
    assert r["verdict"] == M.NOT_ONE_FIXTURE, r
    r = M.judge_both_ways(LIVE, side(fixture=None), red(fixture=None))        # a fresh map has no fixture: never one
    assert r["verdict"] == M.NOT_ONE_FIXTURE, r
    assert M.judge_both_ways(LIVE, side(), red())["verdict"] == M.KILLED


def t_compiled_mutant_needs_build_and_is_not_run_live():
    comp = good_list()["mutants"][1]
    try:
        M.launch_for(comp)
    except M.Refused as e:
        assert e.name == M.NEEDS_BUILD, e
    else:
        raise AssertionError("a compiled mutant was given a live launch")
    assert M.judge_both_ways(comp, None, None)["verdict"] == M.NEEDS_BUILD
    h = M.bar_history(good_list(), [])
    assert h["carried_thing_own_arc"]["mutants"]["carried_drops_in_hand"] == M.NEEDS_BUILD, h
    live = M.launch_for(LIVE)
    assert live["plant"] == "light_limit_5" and live["overlay"]["entries"] == [
        {"typeName": KB, "field": "lightMassLimit", "value": "5"}], live


def t_bar_killed_only_by_value_changes_says_so():
    lst = good_list()
    lines = [{"rec": "both_ways", "mutant": "light_limit_5", "verdict": M.KILLED}]
    b = M.bar_history(lst, lines)["carried_thing_own_arc"]
    assert b["note"] and b["note"].startswith("ONLY_VALUE_KILLS"), b
    lines.append({"rec": "both_ways", "mutant": "carried_plant_wrong_cell", "verdict": M.KILLED})
    assert M.bar_history(lst, lines)["carried_thing_own_arc"]["note"] is None
    assert M.bar_history(lst, [])["carried_thing_own_arc"]["note"] is None    # nothing killed: no claim either way


# ---- beyond the 13
def t_list_reviewed_by_the_scene_writer_is_refused():
    lst = good_list()
    lst["bars"]["carried_thing_own_arc"]["reviewed_by"] = "UNIT_A"
    assert "NOT_REVIEWED" in names(M.lint(lst, None))
    lst = good_list()
    lst["bars"]["carried_thing_own_arc"]["review"] = ""
    assert "NOT_REVIEWED" in names(M.lint(lst, None))


def t_killed_needs_the_named_condition_and_a_changed_witness():
    r = M.judge_both_ways(LIVE, side(), red())
    assert r["verdict"] == M.KILLED and r["why"].endswith("on success"), r
    assert M.judge_both_ways(LIVE, side("UNRESOLVED"), red())["verdict"] == M.GREEN_NOT_SUCCESS
    assert M.judge_both_ways(LIVE, side(), red("UNRESOLVED"))["verdict"] == M.RED_UNDECIDED


def t_both_receipts_are_in_the_scene_history():
    with tempfile.TemporaryDirectory() as root:
        g = dict(side(), run="s1:r1", receipt="g" * 64)
        rr = dict(red(), run="s2:r2", receipt="r" * 64)
        SV.add_run(root, "ExplosiveKnockback", {"run": "s1:r1", "scene": "scene_pawn_arc_carried_thing", "claim": "c", "build": "b",
                                                "outcome": "SUCCESS", "receipt": "g" * 64, "stamps": []})
        SV.add_run(root, "ExplosiveKnockback", {"run": "s2:r2", "scene": "scene_pawn_arc_carried_thing", "claim": "c", "build": "b",
                                                "outcome": "MOD FAILURE", "receipt": "r" * 64, "stamps": ["PLANTED light_limit_5"]})
        res = M.judge_both_ways(LIVE, g, rr)
        M.record(root, "ExplosiveKnockback", "scene_pawn_arc_carried_thing", "b", LIVE, res, g, rr)
        lines, _ = SV.read(root, "ExplosiveKnockback")
        bw = [x for x in lines if x.get("rec") == "both_ways"]
        assert len(bw) == 1 and bw[0]["green"]["receipt"] == "g" * 64 and bw[0]["red"]["receipt"] == "r" * 64, bw
        assert bw[0]["green"]["fixture"] == FIX and "rows" not in bw[0]["green"], bw
        assert [x["mutant"] for x in M.killed_proven(lines)] == ["light_limit_5"]
        forged = lines + [dict(bw[0], mutant="carried_plant_wrong_cell", red={"run": "s9:none", "receipt": "x"})]
        assert [x["mutant"] for x in M.killed_proven(forged)] == ["light_limit_5"]   # a line whose runs are not in the ledger
        s = SV.summary({}, lines, "scene_pawn_arc_carried_thing")                       # the verdict ledger still reads the file
        assert isinstance(s, dict), s


def t_a_kept_run_is_read_from_the_judge_verdict():
    """_side reads a scene_judge.Verdict as the judge makes it (live on ArchBig 2026-11-25: it read .failed, which the Verdict
    does not have, and both-ways crashed after the green run). A MOD FAILURE's first failed condition reaches the both-ways
    judgement, so KILLED can be read."""
    import scene_judge as SJ
    with tempfile.TemporaryDirectory() as d:
        with open(os.path.join(d, "run.json"), "w") as f:
            json.dump({"session": "scn_1", "fixture": FIX}, f)
        with open(os.path.join(d, "trace_run_1.jsonl"), "w") as f:
            f.write("\n".join(json.dumps(r) for r in trace((0, 1, 1))))
        v = SJ.Verdict("MOD FAILURE", 8, {"condition": "success", "tick": 1002, "observed": []}, {"exposure": True}, False,
                       {"entry": {"request": "run_1"}})
        got = M._side(d, v)
    assert got["run"] == "scn_1:run_1" and got["fixture"] == FIX, got
    assert got["verdict"]["outcome"] == "MOD FAILURE" and got["verdict"]["failed"] == {"condition": "success", "tick": 1002, "observed": []}, got
    assert got["verdict"]["counts_for_bar"] is False and got["rands"] == ["42"], got


CHECKS = (t_feature_off_mutant_is_refused, t_mutant_must_name_a_bar, t_draw_is_same_for_one_scene_and_build,
          t_scene_cannot_set_the_draw, t_red_receipt_never_counts_as_pass, t_red_success_reads_mutant_not_killed,
          t_red_without_exposure_proves_nothing, t_red_with_unchanged_witness_reads_mutant_not_used, t_bar_with_one_mutant_is_refused,
          t_red_failing_on_another_condition_is_reported_so, t_both_runs_start_from_one_fixture_hash,
          t_compiled_mutant_needs_build_and_is_not_run_live, t_bar_killed_only_by_value_changes_says_so,
          t_list_reviewed_by_the_scene_writer_is_refused, t_killed_needs_the_named_condition_and_a_changed_witness,
          t_both_receipts_are_in_the_scene_history, t_a_kept_run_is_read_from_the_judge_verdict)


def main():
    passed = 0
    for check in CHECKS:
        try:
            check()
        except Exception as e:  # noqa: BLE001 - a crash of a check is its failure, named
            print("FAIL %s: %s: %s" % (check.__name__, type(e).__name__, e))
        else:
            passed += 1
            print("PASS %s" % check.__name__)
    print("selftest_scene_mutants: %d checks passed of %d" % (passed, len(CHECKS)))
    return int(passed != len(CHECKS))


if __name__ == "__main__":
    raise SystemExit(main())
