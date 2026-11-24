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


def t_voided_run_speaks_for_nobody():
    """A row marked `void_system` (no trial is spent by a system failure) is no reading, whatever its class: FlowWorks visit 9
    read its sc_moat_raid from a run the host's shell budget had killed (class HARNESS, 2026-11-23)."""
    dead = o(LK.APPARATUS, **{"class": "HARNESS", "void_system": True})
    ok, bad = read([good(), dead]), read([o(LK.MOD_FAILURE, "FAIL", **{"class": "MOD"}), dead])
    return cnt(ok) == "pass" and cnt(bad) == "mod" and bad["rows"]["c1"] == "FAIL", (ok["why"], bad["rows"])


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
    failure = o(LK.MOD_FAILURE, "FAIL")
    sha = "0123456789"
    spoiled = env(mod_sha=sha)
    after_fix = read2([failure], [spoiled], **dict(B, budget=4))
    same_build = read2([dict(failure, mod_sha=sha)], [spoiled], **dict(B, budget=4))
    still_fails = read2([dict(failure, mod_sha=sha)], [good(mod_sha=sha)], **B)
    if not (cnt(after_fix) == "spoiled" and after_fix["rows"]["c1"] == "SPOILED"
            and said(after_fix, "3 of 4 budgeted run(s) left") and after_fix["next_run"] == ["c1"]
            and cnt(same_build) == "mod" and same_build["rows"]["c1"] == "FAIL" and cnt(still_fails) == "mod"):
        return False, "new build after old MOD FAILURE read %s/%s: %s; same-build failure read %s/%s, then %s" % (
            cnt(after_fix), after_fix["rows"]["c1"], after_fix["why"], cnt(same_build), same_build["rows"]["c1"],
            cnt(still_fails))
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


def t_brief_names_unclassed_runs():
    why = "the job trace shows the carrier left for food"
    un = lambda **kw: o(LK.UNRESOLVED, "UNMEASURED", evidence="ev/run_7.json", **kw)  # noqa: E731
    def brief(rows):            # visit 2's brief, after a visit 1 that holds `rows`
        N[0] += 1
        root = S.visit("k%d" % N[0], rows + OTHERS)
        keep = M.ingame_openings
        M.ingame_openings = lambda rec: {1: "2026-11-23T00:00:00-08:00", 2: "2026-11-24T00:00:00-08:00"}
        try:
            return " ".join(M.ingame_brief_text(root, MOD)[0].split())
        finally:
            M.ingame_openings = keep
    head = "## Earlier runs nobody classed"
    held = brief([un(), good()])
    bad = brief([o("SUCESS", "PASS"), good()])
    clear = [brief([good()]), brief([un(classed={"outcome": LK.APPARATUS, "why": why, "by": "x"}), good()]),
             brief([dict(un(), test="gone")])]
    part = held.split(head, 1)[-1].split("## ", 1)[0]
    return (head in held and all(w in part for w in ("`c1`", "visit 1", "ev/run_7.json", "`classed`", "CLASS OWED"))
            and head in bad and not any(head in x for x in clear)), (part[:600], head in bad, [head in x for x in clear])


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


SHORT = [good(), miss(), miss(), miss()]
CALL_WHY = "the yield is a guess against pawns that wander off"


def called(call, rows=None, why=CALL_WHY, xy=(2, 4), **kw):
    """SHORT (or rows), read on a scene that carries one recorded call."""
    c = dict({"call": call, "x_of_y": list(xy), "why": why, "by": "BENCH"}, **kw)
    return dict(XY, x_of_y_calls=[c])


def short_root(rows=None, **c1):
    N[0] += 1
    return S.visit("k%d" % N[0], (rows or SHORT) + OTHERS, tt=table(**(c1 or XY)))


def t_shortfall_escalates():
    import shortfall as SF
    root = short_root()
    tt = table(**XY)
    ex = M.read_ingame_exit(root, MOD, 1, tt)
    d = tempfile.mkdtemp(prefix="short_")
    log = os.path.join(d, "log.md")
    item = "RIMMANDRAKE_DRIVE_WMOD_IN_GAME_ACCEPTANCE_VISIT_ONE"
    facts = {MOD: {"stage": "in_game", "visit": 1, "exit": ex, "runs_seen": [
        {"unit": "u0", "item": "RIMMANDRAKE_FIX_WMOD_LATER", "at": 9.0}, {"unit": "u1", "item": item, "at": 5.0}]}}
    notes, bad = [], []

    def note(it, text):
        notes.append((it, text))
        return (not bad, "note refused" if bad else "ok")
    st, rd = {}, {}
    fx = {"conductor_log": log, "note": note, "holds": set()}
    SF.observe(facts, st, 1000.0, rd, fx)
    text = open(log, encoding="utf-8").read() if os.path.exists(log) else ""
    want = ("RAISE FIRST", MOD, "c1", "1 of", "2 of 4", EV, "Does the mod REQUIRE", "guess", "shortfall.py call %s c1 needed" % MOD,
            "shortfall.py call %s c1 guess" % MOD, item)
    lacks = [w for w in want if w not in text] + [w for w in want[1:] if not notes or w not in notes[0][1]]
    once = len(notes) == 1 and notes[0][0] == item and text.count("RAISE FIRST") == 1
    need = any("c1" in x and "2 of 4" in x for x in rd.get("needs_conductor") or [])
    rd2 = {}
    SF.observe(facts, st, 1060.0, rd2, fx)
    again = len(notes) == 1 and open(log, encoding="utf-8").read().count("RAISE FIRST") == 1 and bool(rd2.get("needs_conductor"))
    # a refused note is named and tried again after 10 minutes; the log line is not written twice
    bad.append(1)
    st3, rd3 = {}, {}
    SF.observe(facts, st3, 1000.0, rd3, fx)
    n = len(notes)
    SF.observe(facts, st3, 1060.0, {}, fx)
    quiet = len(notes) == n
    bad.clear()
    SF.observe(facts, st3, 1700.0, {}, fx)
    retried = len(notes) == n + 1 and "note refused" in json.dumps(rd3) and open(
        log, encoding="utf-8").read().count("RAISE FIRST") == 2
    nolog = {}
    SF.observe(facts, {}, 1000.0, nolog, dict(fx, conductor_log=os.path.join(d, "none", "log.md")))
    told = "FileNotFoundError" in json.dumps(nolog) and bool(nolog.get("needs_conductor"))
    held, n = {}, len(notes)
    SF.observe(facts, {}, 1000.0, held, dict(fx, holds={MOD}))
    noitem = {}
    SF.observe({MOD: dict(facts[MOD], runs_seen=[])}, {}, 1000.0, noitem, fx)
    quiet_held = not held.get("needs_conductor") and len(notes) == n and "no in-game run item" in json.dumps(noitem)
    # nothing is raised before the scene ends short, on a pass, on a scene held for another reason, or after the call
    none = [read([good(), miss()], **XY), read([good(), good()], **XY), read(SHORT + [o(LK.UNRESOLVED)], **XY),
            read([o(LK.MOD_FAILURE, "FAIL")] + SHORT, **XY), read([env()] * 3, **B), read(SHORT, **called("needed"))]
    spent = read([good(), env(), env(), env()], **XY)      # the budget ended first: short of X all the same
    return (not lacks and once and need and again and quiet and retried and told and quiet_held
            and all(x["shortfalls"] == [] for x in none) and [(x["test"], x["got"], x["valid"], x["x_of_y"]) for x in
                                                             ex["shortfalls"] + spent["shortfalls"]]
            == [("c1", 1, 4, [2, 4]), ("c1", 1, 1, [2, 4])]), (
        lacks, once, need, again, quiet, retried, told, quiet_held, [x["shortfalls"] for x in none], spent.get("shortfalls"))


def tick_asks():
    """-> (dry lines, applied lines, the second tick's lines, errors): the Dispatch tick itself, on one short scene."""
    import maturation_dispatch as MD
    d = tempfile.mkdtemp(prefix="short_tick_")
    root, log, notes = short_root(), os.path.join(d, "log.md"), []
    hold = os.path.join(d, "holds.json")
    S.put(d, "holds.json", {"holds": []})
    keep = {k: os.environ.get(k) for k in ("RM_MATURATION_DISPATCH_DIR", "RM_OWNER_HOLD_FILE")}
    os.environ.update(RM_MATURATION_DISPATCH_DIR=os.path.join(d, "st"), RM_OWNER_HOLD_FILE=hold)
    cfg = {"enabled": False, "advancing": [MOD], "cap_usd": 15, "max_live": 4, "stage_ceiling_usd": 100, "settle_s": 180,
           "ingame_enabled": True, "ingame_cap_usd": 30, "ingame_auto_runs_per_visit": 1, "launch_tries": 3}

    def facts():
        return {MOD: dict(M.ingame_facts(root, MOD), live_units=[], last_end=None, stage_runs={}, run_usd={}, runs_seen=[
            {"unit": "u1", "item": "RIMMANDRAKE_DRIVE_WMOD_IN_GAME_ACCEPTANCE_VISIT_ONE", "at": 5.0, "end": 6.0}])}

    fx = {"autonomy": False, "convergence": lambda r, rd: None, "facts": facts, "account": lambda: (True, "test"),
          "known": lambda: set(), "clone": lambda: (0, 0), "releases": lambda: ([], 0), "code": lambda: "code-T", "hands": {},
          "file": lambda *x, **k: (False, "none"), "launch": lambda *x, **k: (1, "none", None),
          "rescue": {"conductor_log": log + ".r", "holds": lambda: set(), "records": lambda m, c: []},
          "shortfall": {"conductor_log": log, "note": lambda it, t: (notes.append(it) or True, "ok")}}
    n, errs = [], []
    try:
        for apply, now in ((False, 1e6), (True, 1e6 + 60), (True, 1e6 + 120)):
            rd = MD.tick(root, cfg, apply, fx=fx, now=now, page=False)
            errs.append(rd.get("shortfall_error"))
            n.append((open(log, encoding="utf-8").read().count("RAISE FIRST") if os.path.exists(log) else 0, len(notes)))
    finally:
        for k, v in keep.items():
            os.environ.pop(k, None) if v is None else os.environ.update({k: v})
        shutil.rmtree(d, ignore_errors=True)
    return n, errs


def t_shortfall_escalates_from_the_tick():
    """The promise shortfall-escalates, by the program that the timer runs."""
    n, errs = tick_asks()
    return n == [(0, 0), (1, 1), (1, 1)] and errs == [None] * 3, (n, errs)


def t_shortfall_holds_until_call():
    ex = read(SHORT, **XY)
    later_ = read(SHORT + [good(), good(), good()], **XY)
    blanks = [read(SHORT, **called(**kw)) for kw in ({"call": ""}, {"call": "maybe"}, {"call": "needed", "why": "ok"},
                                                    {"call": "needed", "by": ""}, {"call": "needed", "xy": (3, 4)})]
    odd = read(SHORT, **dict(XY, x_of_y_calls="needed"))
    return (all(x["state"] == "not_met" and cnt(x) == "inconclusive" and x["rows"]["c1"] == "INCONCLUSIVE"
                and len(x["shortfalls"]) == 1 and said(x, "shortfall.py call") for x in [ex, later_, odd] + blanks)), (
        [(cnt(x), x["why"]) for x in [ex, later_, odd] + blanks if cnt(x) != "inconclusive"], ex["why"])


def t_call_needed_is_mod_failure():
    tag = called("needed")
    ex = read(SHORT, **tag)
    new = [read2(SHORT, [good(mod_sha="0123456789"), miss(mod_sha="0123456789")] + [miss(mod_sha="0123456789")] * 2, **tag),
           read2(SHORT, [good(mod_sha="0123456789")] * 2, **tag), read2(SHORT, [good(mod_sha="0123456789")], **tag)]
    return (ex["state"] == "not_met" and cnt(ex) == "mod" and ex["lines"]["c1"]["class"] == "MOD" and ex["rows"]["c1"] == "FAIL"
            and said(ex, "needs X of Y", "classed MOD") and ex["shortfalls"] == [] and [cnt(x) for x in new] == [
                "mod", "pass", "spoiled"] and new[1]["state"] == "met" and new[0]["next_run"] == ["c1"]), (
        cnt(ex), ex["why"], [(cnt(x), x["why"]) for x in new])


def t_call_guess_judges_again():
    tag = dict(called("guess", to=[1, 4]), x_of_y=[1, 4])
    ex, other = read(SHORT, **tag), read2(SHORT, [miss(mod_sha="0123456789")] * 4, **tag)
    return (ex["state"] == "met" and cnt(ex) == "pass" and cnt(other) == "inconclusive"
            and [x["x_of_y"] for x in other["shortfalls"]] == [[1, 4]]), (ex["why"], cnt(other), other["why"])


def t_conductor_records_the_call():
    import shortfall as SF
    item, calls = "RIMMANDRAKE_DRIVE_WMOD_IN_GAME_ACCEPTANCE_VISIT_ONE", []
    win, rc = {"AGENT_SEAT": "BENCH"}, {"publish": 0, "note": 0}

    class R:
        def __init__(self, code):
            self.returncode, self.stdout, self.stderr = code, "PUBLISHED abc\n" if code == 0 else "", "boom"

    def runner(argv, **kw):
        calls.append([str(x) for x in argv])
        return R(rc["note" if "note" in calls[-1] else "publish"])

    def go(root, *a, env=win, why=CALL_WHY, mod=MOD, scene="c1"):
        calls.clear()
        out, sys.stdout = sys.stdout, open(os.devnull, "w")
        try:
            return SF.main(["call", mod, scene] + list(a) + ["--item", item, "--why", why], root=root, runner=runner, env=env)
        finally:
            sys.stdout.close()
            sys.stdout = out

    def tab(root):
        with open(os.path.join(root, "design/concepts/%s/version/test_table.json" % MOD), encoding="utf-8") as f:
            return f.read()

    def after(root):
        tt = json.loads(tab(root))
        return M.read_ingame_exit(root, MOD, 1, tt), tt["tests"]["c1"]
    root = short_root()
    was = tab(root)
    refused = [go(root, "needed", env={"AGENT_SEAT": "BENCH", "RM_ROLE_UNIT": "rm-x"}), go(root, "needed", env={"AGENT_SEAT": "OPS"}),
               go(root, "needed", why="because yes"), go(root, "guess"), go(root, "guess", "--x", "2"),
               go(root, "guess", "--x", "0"), go(root, "guess", "--x", "3"), go(root, "guess", "--x", "1", "--y", "3"),
               go(root, "needed", "--x", "1"), go(root, "needed", scene="c2"), go(root, "needed", scene="nope")]
    clean = tab(root) == was and not calls
    none = go(short_root([good(), good()]), "needed")
    blind = short_root()
    os.remove(os.path.join(blind, "design/concepts/%s/version/in_game/visit_1/rows.jsonl" % MOD))
    os.mkdir(os.path.join(blind, "design/concepts/%s/version/in_game/visit_1/rows.jsonl" % MOD))
    could_not = [go(blind, "needed"), go(root, "needed", mod="NoSuchMod")]
    ok1 = go(root, "needed")
    argv = [list(x) for x in calls]
    ex, t = after(root)
    e = t["x_of_y_calls"][-1]
    wrote = (cnt(ex) == "mod" and t["x_of_y"] == [2, 4] and e["call"] == "needed" and (e["got"], e["valid"]) == (1, 4)
             and e["why"] == CALL_WHY and len(argv) == 2 and "publish" in argv[0][0] and argv[0][-1].endswith("test_table.json")
             and "note" in argv[1] and item in argv[1] and "--per-ruling" in argv[1] and "--publish" in argv[1])
    g = short_root()
    ok2 = go(g, "guess", "--x", "1")
    ex2, t2 = after(g)
    z = short_root([miss()] * 4)
    ok3, (ex3, t3) = go(z, "guess", "--x", "1", "--y", "8"), after(z)
    low = go(short_root([miss()] * 4), "guess", "--x", "1")
    rc["publish"] = 1
    f = short_root()
    failed = go(f, "guess", "--x", "1"), [x for x in calls if "note" in x], after(f)[1]["x_of_y"]
    rc.update(publish=0, note=1)
    failed2 = go(short_root(), "needed")
    return (refused == [2] * 11 and clean and none == 2 and could_not == [3, 3] and ok1 == 0 and wrote and ok2 == 0
            and ex2["state"] == "met" and t2["x_of_y"] == [1, 4] and t2["x_of_y_calls"][-1]["to"] == [1, 4] and ok3 == 0
            and cnt(ex3) == "spoiled" and t3["x_of_y"] == [1, 8] and t3["budget"] == 8 and low == 2
            and failed[0] == 4 and not failed[1] and failed[2] == [1, 4] and failed2 == 4), (
        refused, clean, none, could_not, ok1, wrote, argv, ok2, ex2["why"], ok3, cnt(ex3), t3, low, failed, failed2)


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
    yield "a call is not read", LK, "call_of", lambda spec: None
    yield "any entry is a call", LK, "call_of", lambda spec: ([c for c in (spec or {}).get("x_of_y_calls") or [] if isinstance(
        c, dict)] or [None])[-1]
    import shortfall as SF
    yield "a raised shortfall is raised again", SF, "seen", lambda st, key: {}
    yield "the Conductor window is not asked", SF, "may", lambda why, env: (True, "ok")
    yield "a new X that stays short is written", SF, "stays_short", lambda spec, runs: False
    yield "a brief names no unclassed run", M, "unclassed_lines", lambda *a: []
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
             t_success_needs_a_pass, t_spoiled_run_speaks_for_nobody, t_voided_run_speaks_for_nobody,
             t_last_run_spoiled_runs_again,
             t_environment_fault_needs_its_record, t_unresolved_holds_until_classed, t_forbidden_effect_is_mod_failure,
             t_random_miss_only_by_design, t_kind_b_one_success, t_kind_b_x_of_y,
             t_inconclusive_is_not_pass_or_fail, t_tag_without_evidence_refused, t_hunt_is_never_in_the_exit,
             t_per_scene_run_list, t_a_spoiled_fail_is_no_refused_bar, t_briefs_name_the_fields,
             t_brief_names_unclassed_runs, t_hunt_open_tells_both, t_budgeted_runs_repeat, t_shortfall_escalates,
             t_shortfall_escalates_from_the_tick, t_shortfall_holds_until_call,
             t_call_needed_is_mod_failure, t_call_guess_judges_again, t_conductor_records_the_call]
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
