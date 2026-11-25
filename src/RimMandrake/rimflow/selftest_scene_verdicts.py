#!/usr/bin/env python3
"""selftest_scene_verdicts: the promises of design/specs/2026-11-23-scene-verdicts/boundary.md, one test per promise, each
named as the promise is. The ledger is mutated in place on every run: each planted fault must turn at least one test red.
No game; every file is in a temp root.

    python3 selftest_scene_verdicts.py            every test, then the planted faults
    python3 selftest_scene_verdicts.py <name>...  only the named tests (dashes or underscores), no plants"""
import json
import os
import shutil
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import live_kinds as LK  # noqa: E402
import scene_verdicts as SV  # noqa: E402

TMP = tempfile.mkdtemp(prefix="scene_verdicts_")
MOD = "WMod"
EV = "the target's own choice of path; tried: a calm profile and one cast member; a path choice still draws"
B = {"kind": "live", "stage": "6", "test_kind": "B", "tag_evidence": EV, "budget": 3}
A = {"kind": "live", "stage": "6"}
N = [0]


def run(outcome, **kw):
    N[0] += 1
    line = {"rec": "run", "run": "r%d" % N[0], "scene": "c1", "claim": "plan1", "build": "b1", "outcome": outcome,
            "receipt": "h%d" % N[0], "overlay": "none", "tainted": False, "arm": SV.REFERENCE, "build_kind": "RELEASE",
            "map_kind": "settlement", "at": "2026-11-24T00:00:00Z"}
    if outcome == LK.ENVIRONMENT:
        line["spoiled_by"] = "a wild boar walked onto the station: trace row 40, tap animal_enter"
    line.update(kw)
    return line


def cls(r, outcome, how="classed", **kw):
    return dict({"rec": "class", "run": r["run"], "outcome": outcome, "how": how, "by": "BENCH",
                 "why": "the trace shows the door opened by the raider, not the mod"}, **kw)


def v(spec, *lines, **kw):
    return SV.summary(spec, list(lines), "c1", **kw)


def root():
    N[0] += 1
    r = os.path.join(TMP, "root%d" % N[0])
    os.makedirs(r)
    return r


# ---- the promises ----------------------------------------------------------------------------------------------------

def t_kind_a_one_success_passes():
    s = v(A, run(LK.SUCCESS))
    return s["state"] == SV.READ and s["verdict"] == "PASS" and s["counted"] == 1, s


def t_kind_a_one_mod_failure_fails():
    s, two = v(A, run(LK.MOD_FAILURE)), v(A, run(LK.MOD_FAILURE), run(LK.SUCCESS))
    seen = v(A, run(LK.SUCCESS, forbidden=["a pawn was deleted"]), run(LK.SUCCESS))   # a forbidden effect is a MOD FAILURE
    return s["verdict"] == two["verdict"] == seen["verdict"] == "FAIL", (s, two, seen)


def t_kind_b_one_success_passes():
    s = v(B, run(LK.ENVIRONMENT), run(LK.SUCCESS))
    return s["verdict"] == "PASS" and s["counted"] == 2, s


def t_kind_b_mod_failure_blocks_the_pass():
    s = v(B, run(LK.SUCCESS), run(LK.MOD_FAILURE), run(LK.SUCCESS))
    return s["verdict"] == "FAIL", s


def t_kind_b_unresolved_blocks_the_pass():
    s = v(B, run(LK.UNRESOLVED), run(LK.SUCCESS))
    return s["verdict"] == "HELD" and any("UNRESOLVED" in w for w in s["why"]), s


def t_spent_budget_is_inconclusive():
    s = v(B, *[run(LK.ENVIRONMENT) for _ in range(3)])
    left = v(B, run(LK.ENVIRONMENT), run(LK.APPARATUS), run(LK.NO_LOOK))  # our faults spend no trial
    return s["verdict"] == "INCONCLUSIVE" and left["verdict"] == "NO VALID RUN", (s, left)


def t_x_of_y_short_is_held_for_the_conductor():
    xy = dict(B, x_of_y=[2, 3], budget=3)
    short = v(xy, run(LK.SUCCESS), run(LK.RANDOM_MISS), run(LK.RANDOM_MISS))
    enough = v(xy, run(LK.SUCCESS), run(LK.RANDOM_MISS), run(LK.SUCCESS))
    return (short["verdict"] == "SHORT" and short["short"]["got"] == 1 and enough["verdict"] == "PASS"), (short, enough)


def t_unresolved_holds_until_classed():
    r = root()
    u, g = run(LK.UNRESOLVED), run(LK.SUCCESS)
    SV.add_run(r, MOD, u)
    SV.add_run(r, MOD, g)
    held = SV.read_summary(r, MOD, B, "c1")
    try:
        SV.add_class(r, MOD, u["run"], LK.ENVIRONMENT, "too short", "BENCH")
        short_why = False
    except SV.Refused:
        short_why = True
    SV.add_class(r, MOD, u["run"], LK.ENVIRONMENT, "the trace shows a wild boar on the station at tick 40", "BENCH",
                 spoiled_by="a wild boar: trace row 40")
    after = SV.read_summary(r, MOD, B, "c1")
    return held["verdict"] == "HELD" and short_why and after["verdict"] == "PASS", (held, after)


def t_reclassification_keeps_the_history():
    r = root()
    u = run(LK.UNRESOLVED)
    SV.add_run(r, MOD, u)
    SV.add_class(r, MOD, u["run"], LK.MOD_FAILURE, "the trace shows the mod's patch threw at tick 12", "BENCH")
    lines, _ = SV.read(r, MOD)
    first = dict(lines[0])
    first.pop("at")
    want = dict(u)
    want.pop("at")
    h = SV.history(lines)[u["run"]]
    return (len(lines) == 2 and first == want and [o["outcome"] for o in h["outcomes"]] == [LK.UNRESOLVED, LK.MOD_FAILURE]
            and h["now"] == LK.MOD_FAILURE), (lines, h)


def t_a_replay_is_not_a_sample():
    first = run(LK.ENVIRONMENT)
    s = v(B, first, run(LK.SUCCESS, replay_of=first["run"]))
    same = v(B, first, run(LK.SUCCESS, receipt=first["receipt"]))
    g = run(LK.SUCCESS)
    moved = v(A, g, run(LK.SUCCESS, claim="plan2", receipt=g["receipt"]), claim="plan2")   # a new claim, an old receipt
    other = run(LK.SUCCESS, scene="c2", claim="plan9")
    scene = v(A, other, run(LK.SUCCESS, receipt=other["receipt"]))      # another scene's receipt, filed again under c1
    return (s["verdict"] == "NO VALID RUN" and s["counted"] == 1 and "REPLAY" in s["runs"][1]["reads"]
            and same["verdict"] == "NO VALID RUN" and moved["state"] == scene["state"] == SV.ZERO), (s, same, moved, scene)


def t_a_cluster_counts_as_one():
    xy = dict(B, x_of_y=[2, 2], budget=2)
    s = v(xy, run(LK.SUCCESS, cluster="k1"), run(LK.SUCCESS, cluster="k1"))
    two = v(xy, run(LK.SUCCESS, cluster="k1"), run(LK.SUCCESS, cluster="k2"))
    bad = v(B, run(LK.SUCCESS, cluster="k3"), run(LK.MOD_FAILURE, cluster="k3"))
    seen = v(A, run(LK.SUCCESS, cluster="k4"), run(LK.SUCCESS, cluster="k4", forbidden=["a pawn was deleted"]))
    unproven = v(B, run(LK.SUCCESS, cluster="k5"), run(LK.ENVIRONMENT, cluster="k5", spoiled_by=None))
    return (s["counted"] == 1 and s["verdict"] != "PASS" and two["verdict"] == "PASS" and bad["verdict"] == "FAIL"
            and seen["verdict"] == "FAIL" and unproven["verdict"] == "HELD"), (s, two, bad, seen, unproven)


def t_a_stamped_run_reads_tuned():
    s = v(A, run(LK.SUCCESS, overlay="tune:FlowRate=3"))
    return s["state"] == SV.ZERO and s["verdict"] is None and s["runs"][0]["reads"].startswith("TUNED"), s


def t_the_taint_mark_counts_for_nothing():
    s = v(A, run(LK.SUCCESS, overlay="none", tainted=True))
    unknown = v(A, run(LK.SUCCESS, overlay="none", tainted=None))
    return (s["state"] == SV.ZERO and s["runs"][0]["reads"].startswith("TUNED") and unknown["state"] == SV.ZERO), (
        s, unknown)


def t_a_planted_run_counts_for_nothing():
    red = v(A, run(LK.SUCCESS, stamps=["PLANTED light_limit_5"]))      # a red run of scene.py both-ways, every other mark clean
    explored = v(A, run(LK.SUCCESS, stamps=["EXPLORED"]))
    clean = v(A, run(LK.SUCCESS, stamps=[]))
    return (red["state"] == SV.ZERO and red["runs"][0]["reads"].startswith("NOT COUNTED: a red run") and explored["state"] == SV.ZERO
            and clean["verdict"] == "PASS"), (red, explored, clean)


def t_an_uncompared_arm_counts_for_nothing():
    s = v(A, run(LK.SUCCESS, arm="STEP", compared=False))
    done = v(A, run(LK.SUCCESS, arm="STEP", compared=True))
    return s["state"] == SV.ZERO and "not compared" in s["runs"][0]["reads"] and done["verdict"] == "PASS", (s, done)


def t_a_proof_build_or_a_map_the_bar_refuses_counts_for_nothing():
    proof = v(A, run(LK.SUCCESS, build_kind="PROOF"))
    pocket = v(A, run(LK.SUCCESS, map_kind="pocket"))
    allowed = v(dict(A, map_kinds=["pocket"]), run(LK.SUCCESS, map_kind="pocket"))
    no_map = v(dict(A, map_kinds=[]), run(LK.SUCCESS))     # an empty list accepts no map; only an absent one defaults
    return (proof["state"] == pocket["state"] == no_map["state"] == SV.ZERO and allowed["verdict"] == "PASS"), (
        proof, pocket, allowed, no_map)


def t_an_untouched_change_keeps_the_verdict():
    g = run(LK.SUCCESS, build="b1")
    kept = v(A, g, build="b2", relation=lambda s, old, new: True)
    touched = v(A, g, build="b2", relation=lambda s, old, new: False)
    unknown = v(A, g, build="b2", relation=lambda s, old, new: None)
    return (kept["verdict"] == "PASS" and touched["state"] == unknown["state"] == SV.ZERO), (kept, touched, unknown)


def t_a_serious_unresolved_opens_a_hunt_notice():
    parts = {"what": "the raider was lifted out once", "why_it_matters": "a prisoner escapes in play",
             "next_step": "order the rescue by hand", "cost": "one load"}
    s = v(B, run(LK.UNRESOLVED, serious=True, hunt=parts))
    quiet = v(B, run(LK.UNRESOLVED))
    again = v(B, run(LK.UNRESOLVED, symptom="lifted out"), run(LK.UNRESOLVED, symptom="lifted out"))
    n = s["hunts"][0] if s["hunts"] else {}
    return (len(s["hunts"]) == 1 and all(n.get(k) == parts[k] for k in SV.HUNT_PARTS) and n["missing"] == []
            and n["text"].startswith("FOR THE CONDUCTOR:") and "hunt_open.py" in n["command"][1] and quiet["hunts"] == []
            and len(again["hunts"]) == 1 and set(again["hunts"][0]["missing"]) == set(SV.HUNT_PARTS)), (s, quiet, again)


def t_zero_none_could_not_look_and_failed_are_four_answers():
    none = v(A)
    zero = v(A, run(LK.SUCCESS, overlay="tune:x"))
    r = root()
    os.makedirs(os.path.dirname(SV.path(r, MOD)))
    with open(SV.path(r, MOD), "w") as f:
        f.write("{not json\n")
    blind = SV.read_summary(r, MOD, A, "c1")
    failed = v({"test_kind": "B"}, run(LK.SUCCESS))
    states = [x["state"] for x in (none, zero, blind, failed)]
    return (states == [SV.NONE, SV.ZERO, SV.NO_LOOK, SV.FAILED] and len({SV.EXIT[s] for s in states}) == 4
            and all(x["verdict"] is None for x in (none, zero, blind, failed))), states


def t_a_rejudged_run_shows_both_outcomes():
    g = run(LK.SUCCESS)
    s = v(A, g, cls(g, LK.MOD_FAILURE, how="rejudged"))
    row = s["runs"][0]
    return ([o["outcome"] for o in row["outcomes"]] == [LK.SUCCESS, LK.MOD_FAILURE] and row["outcomes"][1]["how"] ==
            "rejudged" and s["verdict"] == "FAIL"), s


def t_a_line_without_identity_is_refused():
    r = root()
    bad = dict(run(LK.SUCCESS))
    bad.pop("receipt")
    try:
        SV.add_run(r, MOD, bad)
        return False, "written"
    except SV.Refused as e:
        refused = "receipt" in str(e)
    g = run(LK.SUCCESS)
    SV.add_run(r, MOD, g)
    try:
        SV.add_run(r, MOD, g)
        twice = False
    except SV.Refused:
        twice = True
    return refused and twice and len(SV.read(r, MOD)[0]) == 1, SV.read(r, MOD)


def t_exit_holds_a_pass_the_ledger_refuses():
    """The Stage 6 exit (maturation.read_ingame_exit) counts c1 `pass` from its visit rows; a tuned run in the ledger
    takes that pass away, an UNRESOLVED run holds it, a clean SUCCESS leaves it, and a check with no ledger line is not
    touched."""
    import selftest_wrong_check_fixed_in_sitting as S
    M = S.M
    M.BM.RR.relate = lambda root, mod, tests, last, **k: {"rows": {t: {"state": "untouched"} for t in tests}}
    out = {}
    for name, lines in (("clean", [run(LK.SUCCESS, build=S.SHA)]),
                        ("tuned", [run(LK.SUCCESS, build=S.SHA, overlay="tune:FlowRate=3")]),
                        ("tainted", [run(LK.SUCCESS, build=S.SHA, tainted=True)]),
                        ("held", [run(LK.UNRESOLVED, build=S.SHA), run(LK.SUCCESS, build=S.SHA)]),
                        ("none", None)):
        N[0] += 1
        r = S.visit("sv%d" % N[0], S.ALL_PASS)
        if lines is not None:
            S.put(r, "design/concepts/%s/%s" % (S.MOD, SV.FILE), S.lines(lines))
        ex = M.read_ingame_exit(r, S.MOD, 1)
        out[name] = (ex["state"], ex["lines"]["c1"]["count"], ex["lines"]["c2"]["count"])
    return (out["clean"] == out["none"] == ("met", "pass", "pass") and out["tuned"][:2] == ("not_met", "spoiled")
            and out["tainted"][:2] == ("not_met", "spoiled") and out["held"][:2] == ("not_met", "unresolved")
            and all(o[2] == "pass" for o in out.values())), out




def check(tests, quiet=False):
    fails = []
    for fn in tests:
        name = fn.__name__[2:].replace("_", "-")
        try:
            ok, got = fn()
        except Exception as e:  # noqa: BLE001  a test that raises is a failure by name, never a pass
            ok, got = False, "%s: %s" % (type(e).__name__, e)
        if not quiet:
            print("%s  %s%s" % ("PASS" if ok else "FAIL", name, "" if ok else "  got: %r" % (got,)))
        if not ok:
            fails.append(name)
        if quiet and fails:
            return fails
    return fails


def _mutants():
    """The plants: each is a wrong ledger that some test must turn red."""
    br, hist = SV.bar_refusal, SV.history

    def stamp_only(line, spec=None):         # the ticket's plant: checks the overlay stamp and not the taint mark
        return br(dict(line, tainted=False), spec)
    yield "the overlay stamp is checked and the taint mark is not", SV, "bar_refusal", stamp_only
    yield "every receipt counts", SV, "bar_refusal", lambda line, spec=None: None
    yield "a planted or stamped run counts", SV, "bar_refusal", lambda line, spec=None: br(dict(line, stamps=[]), spec)
    yield "an arm counts uncompared", SV, "bar_refusal", lambda line, spec=None: br(dict(line, compared=True), spec)
    yield "a PROOF build counts", SV, "bar_refusal", lambda line, spec=None: br(dict(line, build_kind="RELEASE"), spec)
    yield "any map kind counts", SV, "bar_refusal", lambda line, spec=None: br(dict(line, map_kind="settlement"),
                                                                                dict(spec or {}, map_kinds=None))
    real_reading = LK.reading

    def b_pass_over_unresolved(spec, runs):  # the ticket's plant: a kind B pass with an UNRESOLVED run standing
        k = real_reading(spec, runs)
        if k and k["count"] == "unresolved" and any(r.get("outcome") == LK.SUCCESS for _, r in runs):
            k = dict(k, count="pass", passes=True)
        return k
    yield "a kind B pass stands over an UNRESOLVED run", LK, "reading", b_pass_over_unresolved
    yield "a cluster folds the written words, not the read ones", SV, "_fold", lambda members, scene, build, spec: \
        SV._row(members[0], scene, build, next(w for w in SV.CLUSTER_ORDER if w in [m["now"] for m in members]))
    yield "a cluster reads its best copy", SV, "CLUSTER_ORDER", (LK.SUCCESS,) + SV.CLUSTER_ORDER

    def overwrite(lines):                    # a class line replaces the history instead of adding to it
        h = hist(lines)
        for x in h.values():
            x["outcomes"] = x["outcomes"][-1:]
        return h
    yield "a reclassification overwrites", SV, "history", overwrite
    yield "a class line is ignored", SV, "history", lambda lines: hist([x for x in lines if x.get("rec") == "run"])
    yield "no hunt opens", SV, "hunts", lambda runs: []
    yield "every UNRESOLVED opens a hunt", SV, "hunts", lambda runs: [{"run": h["line"]["run"], "missing": []}
                                                                       for h in runs if h["now"] == LK.UNRESOLVED]
    yield "zero reads as none", SV, "ZERO", SV.NONE
    yield "the exit does not read the ledger", SV, "exit_veto", lambda *a, **k: ({}, [])


def missed_mutants(tests):
    missed = []
    for what, mod, attr, fake in _mutants():
        real = getattr(mod, attr)
        setattr(mod, attr, fake)
        try:
            if not check(tests, quiet=True):
                missed.append(what)
        finally:
            setattr(mod, attr, real)
    return missed


def main(argv):
    TESTS = [t_kind_a_one_success_passes, t_kind_a_one_mod_failure_fails, t_kind_b_one_success_passes,
             t_kind_b_mod_failure_blocks_the_pass, t_kind_b_unresolved_blocks_the_pass, t_spent_budget_is_inconclusive,
             t_x_of_y_short_is_held_for_the_conductor, t_unresolved_holds_until_classed, t_reclassification_keeps_the_history,
             t_a_replay_is_not_a_sample, t_a_cluster_counts_as_one, t_a_stamped_run_reads_tuned, t_a_planted_run_counts_for_nothing,
             t_the_taint_mark_counts_for_nothing, t_an_uncompared_arm_counts_for_nothing,
             t_a_proof_build_or_a_map_the_bar_refuses_counts_for_nothing, t_an_untouched_change_keeps_the_verdict,
             t_a_serious_unresolved_opens_a_hunt_notice, t_zero_none_could_not_look_and_failed_are_four_answers,
             t_a_rejudged_run_shows_both_outcomes, t_a_line_without_identity_is_refused, t_exit_holds_a_pass_the_ledger_refuses]
    names = {a.replace("-", "_") for a in argv}
    tests = [t for t in TESTS if not names or t.__name__[2:] in names]
    if names and len(tests) != len(names):
        print("FAIL selftest_scene_verdicts: no test named %s" % ", ".join(sorted(names - {t.__name__[2:] for t in TESTS})))
        return 2
    fails, missed = check(tests), []
    if not fails and not names:
        missed = missed_mutants(tests)
        fails = check(tests, quiet=True)
    shutil.rmtree(TMP, ignore_errors=True)
    if fails or missed:
        print("FAIL selftest_scene_verdicts: %d test(s) red, %d planted fault(s) not caught%s" % (
            len(fails), len(missed), "".join("\n  - NOT CAUGHT: " + m for m in missed)))
        return 1
    print("PASS selftest_scene_verdicts: %d checks passed%s" % (
        len(tests), "" if names else "; every planted fault caught (%d)" % len(list(_mutants()))))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
