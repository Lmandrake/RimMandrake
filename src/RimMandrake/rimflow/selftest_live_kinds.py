#!/usr/bin/env python3
"""selftest_live_kinds: the promises of design/specs/2026-11-23-live-kinds-exit-reader/boundary.md, one test per promise, each
named as the promise is. The reader is mutated in place on every run: each planted fault must turn at least one test red.
No game, no network, no real Conductor log; every file is in a temp root."""
import argparse
import copy
import json
import os
import shutil
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, HERE)
import selftest_wrong_check_fixed_in_sitting as S  # noqa: E402  its temp roots, rows and stubbed build match
import live_kinds as LK  # noqa: E402
import maturation_rescue as RES  # noqa: E402

M, MOD, row = S.M, S.MOD, S.row
OTHERS = [row("c2"), row("c3")]
SPOILED = "the carrier left for food: evidence/trace_c1.json, job Ingest at tick 1200"
EV = "colonists leave for food; needs frozen and the door locked; jobs still interrupt"
B = {"test_kind": "B", "tag_evidence": EV, "budget": 3}
XY = dict(B, x_of_y=[2, 4], budget=4)
N = [0]
M.BM.RR.relate = lambda root, mod, tests, last, **k: {"rows": {t: {"state": "untouched"} for t in tests}}


def table(**c1):
    tt = copy.deepcopy(S.TT6)
    tt["tests"]["c1"].update(c1)
    return tt


def o(word, verdict="UNMEASURED", **kw):
    if word == LK.ENVIRONMENT:
        kw.setdefault("spoiled_by", SPOILED)
    return row("c1", verdict, outcome=word, **kw)


def good(**kw):
    return o(LK.SUCCESS, "PASS", **kw)


env = lambda verdict="FAIL", **kw: o(LK.ENVIRONMENT, verdict, **kw)  # noqa: E731
miss = lambda **kw: o(LK.RANDOM_MISS, "FAIL", **kw)  # noqa: E731


def read(rows, tt=None, claims=None, **c1):
    """Visit 1's reading: rows of c1, and c2 and c3 passing."""
    N[0] += 1
    return S.ingame(rows + OTHERS, claims, name="k%d" % N[0], tt=tt or table(**c1))


def read2(first, second, **c1):
    """Visit 2's reading, and what visit 3 would run: visit 1 holds `first` and c2 and c3; visit 2 holds `second`."""
    N[0] += 1
    root = S.visit("k%d" % N[0], first + OTHERS, tt=table(**c1))
    v = "design/concepts/%s/version/in_game/visit_" % MOD
    shutil.copytree(os.path.join(root, v + "1"), os.path.join(root, v + "2"))
    S.put(root, v + "2/rows.jsonl", S.lines(second))
    tt = table(**c1)
    ex = M.read_ingame_exit(root, MOD, 2, tt)
    ex["next_run"] = M.ingame_to_run(root, MOD, 3, tt)[0]
    return ex


def cnt(ex, t="c1"):
    return ex["lines"][t]["count"]


def said(ex, *words):
    t = " ".join(ex["why"]).lower()
    return all(w.lower() in t for w in words)


# ---- the promises ----------------------------------------------------------------------------------------------------

# measured on 82aabab76b, the code before this change: (state/count/number of reasons) of c1's second row, over verdict
# PASS, FAIL, UNMEASURED by class none, MOD, HARNESS, SITE; after a first FAIL with no class, after a first FAIL classed
# MOD, and after any other first row (or none)
_CLEAN = " ".join(["met/pass/1"] * 4 + ["not_met/%s/2" % c for c in ("unclassed", "mod", "unhandled", "unhandled")] * 2)
GOLD = {("FAIL", None): " ".join(["not_met/unclassed/1"] * 4 + ["not_met/unclassed/3"] * 8),
        ("FAIL", "MOD"): " ".join(["not_met/mod/1"] * 4 + ["not_met/mod/3"] * 8)}
CELLS = [(v, c) for v in ("PASS", "FAIL", "UNMEASURED") for c in (None, "MOD", "HARNESS", "SITE")]


def t_old_rows_read_as_today():
    """The rows of the live visits carry no kind tag and no outcome word."""
    mk = lambda v, c: row("c1", v, **({"class": c} if c else {}))  # noqa: E731
    bad = []
    for a in [None] + CELLS:
        for extra in ({}, {"test_kind": "A"}, {"test_kind": ""}):       # the tag absent, A, blank: one reading
            got = " ".join("%s/%s/%d" % (e["state"], cnt(e), len(e["why"])) for b in CELLS for e in [
                read(([mk(*a)] if a else []) + [mk(*b)], **extra)])
            if got != GOLD.get(a, _CLEAN):
                bad.append((a, extra, got))
    ex = read2([row("c1", "FAIL", **{"class": "MOD"}), row("c1")], [row("c2")])
    carried = ex["state"] == "met" and ex["carried"] == ["c1", "c3"] and ex["next_run"] == []
    ex2 = read2([row("c1")], [row("c1", "UNMEASURED")])      # an old UNMEASURED row replaces a PASS, as it always did
    return (not bad and carried and cnt(ex2) == "unclassed" and ex2["next_run"] == ["c1"] and LK.reading(
        {}, [(1, row("c1")), (2, row("c1", "FAIL"))]) is None), (bad[:2], ex["why"], ex2["why"])


def t_absent_tag_is_kind_a():
    ex = read([row("c1")], test_kind="D")
    return (LK.kind({}) == LK.kind(None) == LK.kind({"test_kind": None}) == "A" and LK.kind({"test_kind": "b"}) == "B"
            and ex["state"] == "not_met" and said(ex, "c1", "test_kind", "'D'")), ex["why"]


def t_unknown_outcome_refused():
    a = read([row("c1", outcome="FLAKY")])
    under = read([row("c1", outcome="FLAKY"), good()])
    form = read([row("c1", outcome="mod_failure", forbidden=None), good()])
    nolist = read([row("c1", outcome="SUCCESS", forbidden={"lost": False})])
    blank = read([row("c1", outcome="")])
    return (cnt(a) == cnt(under) == cnt(nolist) == "refused" and said(a, "FLAKY", "ENVIRONMENT FAULT", "UNRESOLVED")
            and all(x["state"] == "not_met" for x in (a, under, nolist)) and cnt(form) == "mod"
            and blank["state"] == "met"), (a["why"], under["why"], form["why"], nolist["why"], blank["why"])


def t_success_needs_a_pass():
    ex = read([o(LK.SUCCESS, "FAIL")])
    return cnt(ex) == "refused" and ex["state"] == "not_met" and said(ex, "contradicts"), ex["why"]


def t_spoiled_run_speaks_for_nobody():
    outs = []
    for w in (env("FAIL"), env("UNMEASURED"), env("UNMEASURED", **{"class": "SITE"}), env("PASS"), o(LK.APPARATUS, "FAIL"),
              o(LK.NO_LOOK), o("environment_fault", spoiled_by=SPOILED)):
        outs += [read([w, good()]), read([good(), w]), read([row("c1"), w, w]), read2([good()], [w])]
    alone = read([env("PASS")])     # a PASS word on a spoiled run is no PASS
    hidden = read([row("c1", "FAIL"), env(), good()])       # it does not cancel a FAIL either
    return (all(x["state"] == "met" for x in outs) and outs[3]["next_run"] == [] and cnt(alone) == "spoiled"
            and cnt(hidden) == "unclassed"), ([x["why"] for x in outs if x["state"] != "met"], alone["why"], hidden["why"])


def t_last_run_spoiled_runs_again():
    ex = [read([w]) for w in (env("FAIL"), env("UNMEASURED"), o(LK.APPARATUS), o(LK.NO_LOOK))]
    wrong = {"class": "HARNESS", "unrepaired": "the probe the reading needs does not exist", "owner": "RIMMANDRAKE_MEND_W_X"}
    own = read([o(LK.APPARATUS, **wrong)], claims={"c1": "unmeasured"})
    bare = read([good(), o(LK.APPARATUS, **{"class": "HARNESS"})])
    two = read2([env()], [env()])
    return (all(x["state"] == "not_met" and cnt(x) == "spoiled" and said(x, "c1", "run that scene again")
                and not x["undecided_bars"] and not said(x, "with no class") for x in ex + [two])
            and two["next_run"] == ["c1"] and cnt(own) == "not_counted" and own["undecided_bars"] == ["b_one"]
            and cnt(bare) == "unhandled"), ([x["why"] for x in ex], own["why"], bare["why"], two["why"])


def t_environment_fault_needs_its_record():
    outs = [read([env(spoiled_by=x), good()]) for x in ("", None, [], "  ")]
    modc = read([env(**{"class": "MOD"}), good()])
    return (all(x["state"] == "not_met" and said(x, "c1", "UNRESOLVED", "spoiled_by") for x in outs)
            and cnt(modc) in ("unresolved", "mod") and said(modc, "UNRESOLVED")), ([x["why"] for x in outs], modc["why"])


def t_unresolved_holds_until_classed():
    un = lambda **kw: o(LK.UNRESOLVED, "FAIL", **kw)  # noqa: E731
    why = "the job trace shows the carrier left for food"
    held = [read([un(), good()]), read([good(), un()]), read2([un(), good()], [row("c2")]), read2([un(), good()], [good()]),
            read([un(classed={"outcome": LK.ENVIRONMENT, "why": "ok", "by": "x"}, spoiled_by=SPOILED), good()]),
            read([un(classed={"outcome": LK.ENVIRONMENT, "why": why, "by": ""}, spoiled_by=SPOILED), good()]),
            read([un(classed={"outcome": LK.UNRESOLVED, "why": why, "by": "x"}), good()]),
            read([un(classed={"outcome": LK.ENVIRONMENT, "why": why, "by": "x"}), good()])]       # no spoiled_by
    free = read([un(classed={"outcome": LK.ENVIRONMENT, "why": why, "by": "x"}, spoiled_by=SPOILED), good()])
    inrec = read([un(classed={"outcome": LK.ENVIRONMENT, "why": why, "by": "x", "spoiled_by": SPOILED}), good()])
    late = read([good(), un(classed={"outcome": LK.APPARATUS, "why": why, "by": "x"})])
    mod = read([un(classed={"outcome": LK.MOD_FAILURE, "why": why, "by": "x"}), good()])
    N[0] += 1
    root = S.visit("k%d" % N[0], [good()] + OTHERS)
    v = os.path.join(root, "design/concepts/%s/version/in_game/visit_" % MOD)
    shutil.copytree(v + "1", v + "2")
    os.remove(v + "1/rows.jsonl")
    absent = M.read_ingame_exit(root, MOD, 2)["state"]
    os.mkdir(v + "1/rows.jsonl")                # there, and cannot be read: an UNRESOLVED run may stand in it
    blind = M.read_ingame_exit(root, MOD, 2)
    if absent != "met" or blind["state"] != "not_met" or not said(blind, "visit_1/rows.jsonl", "cannot be read"):
        return False, (absent, blind["why"])
    return (all(x["state"] == "not_met" and cnt(x) == "unresolved" and said(x, "c1", "UNRESOLVED")
                and not x["undecided_bars"] for x in held)
            and free["state"] == inrec["state"] == late["state"] == "met" and cnt(mod) == "mod"), (
        [(cnt(x), x["why"]) for x in held if cnt(x) != "unresolved"], free["why"], inrec["why"], late["why"], mod["why"])


def t_forbidden_effect_is_mod_failure():
    f = {"forbidden": ["a pawn lost"]}
    outs = [read([env(**f), good()]), read([good(), env(**f)]), read([row("c1", **f)]), read([good(**f)]),
            read([o(LK.MOD_FAILURE, "FAIL"), good()]), read2([o(LK.MOD_FAILURE, "FAIL"), good()], [row("c2")]),
            read([env(), o(LK.NO_LOOK, forbidden="an exception")])]
    none = [read([good(forbidden=x)]) for x in ([], "", None, ["none"], "none")]
    rebuilt = read2([o(LK.MOD_FAILURE, "FAIL")], [good(mod_sha="0123456789")])     # a new visit on the fixed build
    fix = S.mod_fixed()
    fix[0] = dict(fix[0], outcome=LK.MOD_FAILURE)
    fix[1] = dict(fix[1], outcome=LK.SUCCESS)
    fixed = S.ingame(fix, reviews=S.review(), name="kfix")
    return (all(x["state"] == "not_met" and cnt(x) == "mod" for x in outs) and all(x["state"] == "met" for x in none)
            and cnt(rebuilt) == "pass" and fixed["state"] == "met"), (
        [(cnt(x), x["why"]) for x in outs if cnt(x) != "mod"], [x["why"] for x in none], rebuilt["why"], fixed["why"])


def t_random_miss_only_by_design():
    a = read([o(LK.RANDOM_MISS), good()])
    b = read([miss(), good()], **B)
    return (cnt(a) == cnt(b) == "refused" and said(a, "c1", "RANDOM MISS") and a["state"] == b["state"] == "not_met"), (
        a["why"], b["why"])


def t_kind_b_one_success():
    ok = [read([env(), good(), env()], **B), read([good()], **B), read([env(), env(), env(), good()], **B),
          read([row("c1")], **B), read2([env(), good()], [env()], **B), read2([good()], [row("c2")], **B)]
    bad = [read([o(LK.MOD_FAILURE, "FAIL"), good()], **B), read([good(), o(LK.MOD_FAILURE, "FAIL")], **B),
           read([o(LK.UNRESOLVED), good()], **B), read([row("c1", "FAIL"), good()], **B),
           read2([row("c1", "FAIL", **{"class": "MOD"})], [good()], **B)]
    newbuild = read2([good()], [row("c1", "FAIL", mod_sha="0123456789", **{"class": "MOD"})], **B)
    return (all(x["state"] == "met" and x["rows"]["c1"] == "PASS" for x in ok) and ok[4]["next_run"] == []
            and all(x["state"] == "not_met" for x in bad) and cnt(newbuild) == "mod"), (
        [x["why"] for x in ok if x["state"] != "met"], [x["why"] for x in bad], newbuild["why"])


def t_kind_b_x_of_y():
    g, m = good, miss
    met = [read(x, **XY) for x in ([g(), m(), g(), m()], [g(), g()], [env(), m(), g(), o(LK.NO_LOOK), g()])]
    no = [read(x, **XY) for x in ([g(), m(), m(), m()], [g(), m()], [m(), m(), m(), g(), g()])]
    return (all(x["state"] == "met" for x in met) and all(x["state"] == "not_met" for x in no)
            and [cnt(x) for x in no] == ["inconclusive", "spoiled", "inconclusive"]), (
        [x["why"] for x in met], [x["why"] for x in no])


def t_inconclusive_is_not_pass_or_fail():
    ex = read([env(), env(), env()], **B)
    two = read([env(), env(), o(LK.APPARATUS), o(LK.NO_LOOK)], **B)      # our own faults spend no budget
    nb = read2([env(), env()], [env(mod_sha="0123456789")], **B)        # a new build has its own budget
    again = read2([env(), env(), env()], [row("c2")], **B)
    # a SUCCESS on an earlier build does not end a later build's budget: the scene ran again on the new build, so the
    # new build's runs are the scene's runs (found by the fresh read, 2026-11-23: this read pass and re-ran without end)
    moved = read2([good()], [env(mod_sha="0123456789")] * 3, **B)
    left = read2([good()], [env(mod_sha="0123456789")], **B)
    return (ex["rows"]["c1"] == "INCONCLUSIVE" and cnt(ex) == "inconclusive" and ex["state"] == "not_met"
            and not ex["undecided_bars"] and said(ex, "Conductor decides") and cnt(two) == "spoiled"
            and said(two, "1 of 3 budgeted run(s) left") and cnt(nb) == "spoiled" and again["next_run"] == ["c1"]
            and cnt(moved) == "inconclusive" and moved["state"] == "not_met" and cnt(left) == "spoiled"
            and said(left, "2 of 3 budgeted run(s) left") and left["next_run"] == ["c1"]), (
        ex["why"], two["why"], nb["why"], cnt(moved), moved["why"], cnt(left), left["why"])


def t_tag_without_evidence_refused():
    bads = [dict(B, tag_evidence=""), dict(B, tag_evidence=None), dict(B, budget=None), dict(B, budget=0),
            dict(B, budget="3"), dict(B, budget=True), dict(XY, x_of_y=[3, 2]), dict(XY, x_of_y=[0, 2]),
            dict(XY, x_of_y="2 of 4"), {"x_of_y": [2, 4]}]
    got = [read([good()], **b) for b in bads]
    hunt = table()
    hunt["tests"]["h"] = {"kind": "live", "stage": "6", "command": "h", "test_kind": "C"}
    h = read([row("c1")], tt=hunt)
    ydef = read([good(), good()], **{k: v for k, v in XY.items() if k != "budget"})
    return (all(x["state"] == "not_met" and said(x, "c1", "tag") for x in got) and h["state"] == "not_met"
            and said(h, "check h", "tag_evidence") and ydef["state"] == "met"), (
        [(b, x["why"]) for b, x in zip(bads, got) if x["state"] == "met"], h["why"], ydef["why"])


def t_hunt_is_never_in_the_exit():
    tt = table()
    tt["tests"]["h"] = {"kind": "live", "stage": "6", "command": "h", "test_kind": "C", "tag_evidence": EV}
    out = read([row("c1"), row("h", "FAIL", **{"class": "MOD"})], tt=tt)
    esc = read([row("c1", "FAIL", **{"class": "MOD"})], test_kind="C", tag_evidence=EV)     # a tag is no way out
    beside = copy.deepcopy(tt)
    beside["bars"][0]["decides"] = ["c1", "h"]
    two = read([row("c1")], tt=beside)
    N[0] += 1
    root = S.visit("k%d" % N[0], [row("c1")] + OTHERS, tt=tt)
    run = [M.ingame_to_run(root, MOD, n, tt)[0] for n in (1, 2)]
    return (out["state"] == "met" and "h" not in out["lines"] and esc["state"] == "not_met" and said(esc, "b_one", "hunt")
            and two["state"] == "met" and run == [["c1", "c2", "c3"], []]), (out["why"], esc["why"], two["why"], run)


def t_per_scene_run_list():
    runs = [(read2(a, [row("c2")], **c1)["next_run"], want) for a, c1, want in (
        ([good()], {}, []), ([good(), env()], {}, []), ([env()], {}, ["c1"]), ([env(), env(), env()], B, ["c1"]),
        ([env(), good(), env()], B, []), ([good(), miss()], XY, ["c1"]), ([good(), good(), miss()], XY, []),
        ([o(LK.MOD_FAILURE, "FAIL")], {}, ["c1"]), ([good(), o(LK.UNRESOLVED, "FAIL")], {}, ["c1"]))]
    return all(a == b for a, b in runs), runs


def t_a_spoiled_fail_is_no_refused_bar():
    def rounds(rows, **c1):
        N[0] += 1
        root = S.visit("k%d" % N[0], rows + OTHERS, tt=table(**c1))
        errs = []
        runs, rr, _ = RES.read_ingame(root, MOD, table(**c1), None, errs)
        return rr[0]["refused"], sorted(r["result"] for r in runs if r["test"] == "c1")
    return (rounds([row("c1", "FAIL")]) == ({"b_one": ["c1 FAIL"]}, ["FAIL"]) and rounds([env("FAIL")]) == ({}, [])
            and rounds([miss()], **XY) == ({}, []) and rounds([env(forbidden=["a pawn lost"])])[0] != {}), (
        rounds([row("c1", "FAIL")]), rounds([env("FAIL")]))


def t_briefs_name_the_fields():
    N[0] += 1
    root = S.visit("k%d" % N[0], [env()] + OTHERS, tt=table(**B))
    drv = " ".join(M.ingame_brief_text(root, MOD)[0].split())
    stw = " ".join(S.MA.steward_brief(root, MOD, {"steward_kind": "exit_not_met", "stage": "in_game", "mod": MOD,
                                                  "why": "x", "decision": "steward"}).split())
    with open(os.path.join(HERE, "roles", "designer_scene_contract.md"), encoding="utf-8") as f:
        con = f.read()
    lacks = [("driver", w) for w in ("test_kind", "tag_evidence", "`budget`", "x_of_y", "spoiled_by", "`forbidden`",
                                     "`classed`", "hunt_open.py", "kind B: budget 3 run(s)") if w not in drv]
    lacks += [("steward", w) for w in ("to no earlier stage", "`spoiled`", "INCONCLUSIVE", "`classed`", "FOR THE CONDUCTOR")
              if w not in stw]
    lacks += [("contract", w) for w in ("test_kind", "tag_evidence", "budget", "x_of_y") if w not in con]
    return not lacks, lacks


def t_hunt_open_tells_both():
    import hunt_open as H
    d = tempfile.mkdtemp(prefix="hunt_")
    log = os.path.join(d, "log.md")
    seen = []

    class R:
        def __init__(self, rc):
            self.returncode, self.stdout, self.stderr = rc, "PUBLISHED abc\n", ""

    def runner(rc):
        def f(argv, **kw):
            seen.append(argv)
            return R(rc)
        return f
    full = ["RIMMANDRAKE_HUNT_WMOD_RAIDER_LIFTED_OUT_ONCE", "--what", "lifted once", "--why-it-matters", "a prisoner escapes",
            "--next-step", "order the rescue", "--cost", "one load"]
    old = os.environ.get("RM_CONDUCTOR_LOG")
    quiet = open(os.devnull, "w")
    out, sys.stdout = sys.stdout, quiet
    try:
        os.environ["RM_CONDUCTOR_LOG"] = log
        os.environ.pop("RM_HUNT_OPEN_NO_NOTE", None)
        blanks = [H.main(full[:i] + [" "] + full[i + 1:], runner(0)) for i in (0, 2, 4, 6, 8)]
        none = not os.path.exists(log) and not seen
        ok = H.main(full, runner(0))
        text = open(log, encoding="utf-8").read()
        noted = len(seen) == 1 and seen[0][2:4] == ["note", full[0]] and "HUNT OPENED: what happened: lifted once" in seen[0][5]
        failed = H.main(full, runner(4))
        os.environ["RM_CONDUCTOR_LOG"] = os.path.join(d, "no_such_dir", "log.md")
        n = len(seen)
        nolog = H.main(full, runner(0))
    finally:
        sys.stdout = out
        quiet.close()
        os.environ.pop("RM_CONDUCTOR_LOG") if old is None else os.environ.update(RM_CONDUCTOR_LOG=old)
    return (blanks == [2] * 5 and none and ok == 0 and text.count("HUNT OPENED") == 1 and "RAISE FIRST" in text
            and full[0] in text and noted and failed == 4 and nolog == 3 and len(seen) == n), (
        blanks, none, ok, text, noted, failed, nolog)


def t_budgeted_runs_repeat():
    sys.path.insert(0, os.path.join(REPO, "src", "RimMandrake", "Utils", "testq"))
    import testq as T
    import gaps
    root = tempfile.mkdtemp(prefix="tq_")
    tt = {"tests": {"b": dict(B, kind="live", stage="6", testq={"chains": ["kb"]}),
                    "h": {"kind": "live", "stage": "6", "test_kind": "C", "tag_evidence": EV, "testq": {"chains": ["kc"]}},
                    "n": dict(B, tag_evidence="", kind="live", stage="6", testq={"chains": ["noev"]}),
                    "a": {"kind": "live", "stage": "6", "testq": {"chains": ["ka"]}}}}
    S.put(root, "design/concepts/WM/version/test_table.json", tt)
    S.put(root, "design/concepts/Bad/version/test_table.json", "{")
    done = lambda n, c, v="v1", partial=False: [{"partial": partial, "chains": {c: ("PASS", [])}, "versions": {c: v}}] * n  # noqa: E731
    world = {"runs": [], "held": [], "pr": {"versions": {c: "v1" for c in ("kb", "kc", "noev", "ka")}}}
    keep = T.REPO, T.retest_stop, T.pilot_stop, gaps.settled, T.records, T.log
    T.log = lambda *a: None
    T.REPO, T.pilot_stop, T.records = root, lambda mod: {}, lambda *a: []
    T.retest_stop = lambda mod: {"kb", "kc", "noev", "ka"}
    gaps.settled = lambda mod, recs, *a, **k: world
    ask = lambda c, mod="WM": T.already_tested(argparse.Namespace(mod=mod, by="BENCH", retest_why=None),  # noqa: E731
                                              {"chains": c}, {"chains": c})
    try:
        world["runs"] = done(2, "kb") + done(9, "kc") + done(5, "kb", "v0") + done(5, "kb", partial=True)
        free = ask(["kb"]) is None and ask(["kc"]) is None and ask(["kb", "kc"]) is None
        refused = all(ask([c]) for c in ("noev", "ka")) and "ka" in ask(["kb", "ka"]) and "kb" not in ask(["kb", "ka"]).split(
            " already")[0]
        unread = bool(ask(["kb"], "Bad")) and bool(ask(["kb"], "NoTable"))
        world["runs"] = done(3, "kb")
        spent = bool(ask(["kb"]))
        world.update(runs=[], held=["kb", "kc"])
        held = bool(ask(["kb"])) and bool(ask(["kc"]))
    finally:
        T.REPO, T.retest_stop, T.pilot_stop, gaps.settled, T.records, T.log = keep
    return free and refused and unread and spent and held, (free, refused, unread, spent, held)


def run(tests, quiet=False):
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
        if quiet and fails:     # one red is enough for a planted fault
            return fails
    return fails


def _mutants():
    out, rd, sp = LK.outcome, LK.reading, LK.spoiled
    yield "an unknown word reads as an old row", LK, "outcome", lambda r, s=None: (
        (None, None) if out(r, s)[0] == LK.REFUSED else out(r, s))
    yield "ENVIRONMENT FAULT needs no record", LK, "outcome", lambda r, s=None: (
        (LK.ENVIRONMENT, None) if LK.norm(r.get("outcome")) == LK.ENVIRONMENT and out(r, s)[0] == LK.UNRESOLVED else out(r, s))
    yield "a forbidden effect is not read", LK, "_forbidden", lambda r: ([], None)
    yield "nothing is spoiled", LK, "spoiled", lambda r: False
    yield "every non-SUCCESS outcome is spoiled", LK, "spoiled", lambda r: out(r)[0] not in (None, LK.SUCCESS)
    yield "an old UNMEASURED row is spoiled", LK, "spoiled", lambda r: sp(r) or r.get("verdict") == "UNMEASURED"
    yield "the kinds are not read at all", LK, "reading", lambda s, r: None
    yield "an old row gets a reading", LK, "reading", lambda s, r: rd(s, r) or (rd(dict(s, test_kind="B", tag_evidence="x",
                                                                               budget=1), r) if r else None)
    yield "UNRESOLVED holds only the newest visit", LK, "reading", lambda s, r: rd(s, [x for x in r or [] if x[0] == max(
        y[0] for y in r)]) if r else None
    yield "a MOD FAILURE is left as its row says", LK, "as_old", lambda r: r
    yield "every build is one build", LK, "same_build", lambda a, b: True
    yield "no two rows share a build", LK, "same_build", lambda a, b: a is b
    def deciding_build(runs, last):
        d = None
        for _, r in runs:
            d = LK.later(d, r)
        return [r for _, r in runs if LK.same_build(r, d)]
    yield "a kind B scene's runs are its deciding row's build", LK, "build_runs", deciding_build
    yield "a tag needs no evidence", LK, "tag_flaws", lambda s: []
    yield "the table's flaws are not said", LK, "table_flaws", lambda tt: {}
    yield "x_of_y is not read", LK, "x_of_y", lambda s: None
    yield "a hunt is a required check", LK, "kind", lambda s: "A" if LK.norm((s or {}).get("test_kind")) == "C" else (
        LK.norm((s or {}).get("test_kind")) or "A")
    yield "a spoiled FAIL refuses a bar", LK, "no_verdict", lambda r: False
    yield "our own faults spend the budget", LK, "NO_BUDGET", ()
    yield "one word classes an UNRESOLVED run", LK, "WHY_WORDS", 1


def missed_mutants(tests):
    """-> the planted faults that turned no test red (each is put back after its run)."""
    missed = []
    for what, mod, attr, fake in _mutants():
        real = getattr(mod, attr)
        setattr(mod, attr, fake)
        try:
            if not run(tests, quiet=True):
                missed.append(what)
        finally:
            setattr(mod, attr, real)
    return missed


def main():
    tests = [t_old_rows_read_as_today, t_absent_tag_is_kind_a, t_unknown_outcome_refused,
             t_success_needs_a_pass, t_spoiled_run_speaks_for_nobody, t_last_run_spoiled_runs_again,
             t_environment_fault_needs_its_record, t_unresolved_holds_until_classed, t_forbidden_effect_is_mod_failure,
             t_random_miss_only_by_design, t_kind_b_one_success, t_kind_b_x_of_y,
             t_inconclusive_is_not_pass_or_fail, t_tag_without_evidence_refused, t_hunt_is_never_in_the_exit,
             t_per_scene_run_list, t_a_spoiled_fail_is_no_refused_bar, t_briefs_name_the_fields,
             t_hunt_open_tells_both, t_budgeted_runs_repeat]
    fails, missed = run(tests), []
    if not fails:
        missed = missed_mutants(tests)
        fails = run(tests, quiet=True)     # with nothing planted the suite is green again: the reds above were the plants'
    shutil.rmtree(S.TMP, ignore_errors=True)
    if fails or missed:
        print("FAIL selftest_live_kinds: %d test(s) red, %d planted fault(s) not caught%s" % (
            len(fails), len(missed), "".join("\n  - NOT CAUGHT: " + m for m in missed)))
        return 1
    print("PASS selftest_live_kinds: %d tests; every planted fault caught (%d)" % (len(tests), len(list(_mutants()))))
    return 0


if __name__ == "__main__":
    sys.exit(main())
