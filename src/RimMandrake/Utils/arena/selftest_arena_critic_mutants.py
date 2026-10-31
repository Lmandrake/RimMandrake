#!/usr/bin/env python3
"""selftest_arena_critic_mutants.py - arena_critic_mutants.py, each criterion proven by FORCED FAILURE. Offline: no
model is called (a fake matcher call stands in), git runs only in a throwaway repo.

  mutate        the recorded edit is applied exactly once; a find that is absent, empty or occurs a different number
                of times than the fixture says refuses; nth picks the right occurrence
  commit        a mutant commit is deterministic (same tree + parent -> same sha) and refuses a path not in the head
  matcher       parse_identified takes one JSON answer, refuses out-of-range / bool / conflicting answers; match_one
                marks the true hit and a decoy hit, and an error or garbage answer is invalid, never a match
  writeup       a kept full answer is used whole (not an 800-char tail), verdict lines are stripped, the cap keeps the END
  scoring       discrimination = catch(mut) - reject(orig); reason mode counts an unmatched reject as a miss; a reject
                with no valid match drops out (and the grade is UNMEASURED); the paired restriction keeps only
                candidates valid for both reviewers; an always-reject reviewer scores 0; the interval is reproducible;
                a match record whose key is not the current job's (other write-up, fixture or matcher) is ignored;
                an unproved mutant, a run without a critic fingerprint or an undefined paired interval grades
                UNMEASURED; only tier A is labelled good (tier B and untiered are not); a reject awaiting its match is
                not a subgroup (by_kind / by_detect) miss
  small n       (CRITIC_CALIB_FIX_SMALL_N_INTERVAL, red against the old percentile bootstrap) 0/8 false rejects gives
                a non-zero-width interval; 4 discordant labelled originals are not a call; no discordance is still not
                a zero-width interval; a large consistent difference is still detected; intervals bracket the point
  exact pins    cp matches closed forms at k=0,1,n-1,n; MOVER pairs the right bounds; the paired box corners; sign_flip_p
                equals brute-force enumeration over originals (the small-n checks above prove only shape)
  near decoy    (CRITIC_DECOYS_WIDEN_SAME_ORIGINAL) a sibling mutant is the decoy; near hits gate the grade on their own
  equivalent    (CRITIC_MUTANTS_DELETE_EQUIVALENT_M30) an EQUIVALENT mutant (m30) never enters the catch term
  seed          run.json lists every source once; copies only byte-identical candidates; refuses another fingerprint, another set, a set whose content
                does not match its recorded sha, and a target run of another critic
  proofs        latest() accepts a proof made on this set OR on exactly this mutant's and original's heads, and
                nothing else
"""
from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import arena_judge as J  # noqa: E402
import arena_critic_calib as C  # noqa: E402
import arena_critic_mutants as M  # noqa: E402
import arena_tasks as A  # noqa: E402

FAILS: list[str] = []


def check(name: str, ok: bool, detail: str = "") -> None:
    print(("PASS " if ok else "FAIL ") + name + ("" if ok else "  -- " + detail))
    if not ok:
        FAILS.append(name)


def refuses(fn, *a, exc=(A.ArenaError, SystemExit)) -> bool:
    try:
        fn(*a)
    except exc:
        return True
    return False


def t_mutate():
    m = {"mid": "x", "path": "f.py", "find": "i < n", "replace": "i <= n"}
    check("mutate applies the edit once", M.mutate_text("if i < n:\n", m) == "if i <= n:\n")
    check("mutate refuses an absent find", refuses(M.mutate_text, "if j < n:\n", m))
    check("mutate refuses a find that occurs twice when the fixture says once",
          refuses(M.mutate_text, "i < n; i < n", m))
    check("mutate refuses an empty find", refuses(M.mutate_text, "abc", dict(m, find="")))
    two = dict(m, occurrences=2, nth=2)
    check("mutate nth=2 edits the second occurrence only", M.mutate_text("i < n; i < n", two) == "i < n; i <= n")
    for bad in (3, 0, -1, "2"):
        check("mutate refuses nth=%r with an ArenaError" % (bad,),
              refuses(M.mutate_text, "i < n; i < n", dict(two, nth=bad), exc=(A.ArenaError,)))


def t_commit(root: Path):
    repo = root / "repo"
    repo.mkdir()
    env = ["-c", "user.name=t", "-c", "user.email=t@invalid"]
    subprocess.run(["git", "init", "-q", str(repo)], check=True)
    (repo / "f.py").write_text("a = 1\n")
    subprocess.run(["git", "-C", str(repo), "add", "f.py"], check=True)
    subprocess.run(["git", "-C", str(repo), *env, "commit", "-qm", "base"], check=True)
    head = subprocess.run(["git", "-C", str(repo), "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()
    s1 = M.make_commit(repo, head, "f.py", b"a = 2\n")
    s2 = M.make_commit(repo, head, "f.py", b"a = 2\n")
    check("mutant commit is deterministic", s1 == s2 and len(s1) == 40, "%s %s" % (s1, s2))
    shown = subprocess.run(["git", "-C", str(repo), "show", s1 + ":f.py"], capture_output=True, text=True).stdout
    check("mutant commit carries the mutated file", shown == "a = 2\n", shown)
    check("mutant commit refuses a path not in the head", refuses(M.make_commit, repo, head, "nope.py", b"x"))


def t_matcher():
    check("parse_identified reads one answer", M.parse_identified('blah {"identified": [2, 1, 2]}', 2) == [1, 2])
    check("parse_identified empty list is a valid no-match", M.parse_identified('{"identified": []}', 2) == [])
    check("parse_identified refuses out of range", M.parse_identified('{"identified": [3]}', 2) is None)
    check("parse_identified refuses a bool", M.parse_identified('{"identified": [true]}', 2) is None)
    check("parse_identified refuses two different answers",
          M.parse_identified('{"identified": [1]} then {"identified": [2]}', 2) is None)
    check("parse_identified refuses no answer", M.parse_identified("I think number 1", 2) is None)
    job = {"key": "k", "run": "r", "cid": "c", "role": "mutant", "writeup": "w",
           "items": [("decoy", "m9", "other"), ("true", "m1", "the defect")]}
    seen = {}

    def fake(answer, meta=None):
        def call(prompt, timeout):
            seen["prompt"] = prompt
            return answer, meta or {"rc": 0}
        return call

    r = M.match_one(job, fake('{"identified": [2]}'))
    check("match_one: true defect identified -> true_hit, no decoy hit",
          r["valid"] and r["true_hit"] == ["m1"] and not r["decoy_hit"], str(r))
    check("match_one: the matcher's prompt carries no verdict, run or role",
          all(s not in seen["prompt"] for s in ('"r"', "mutant", "decoy", "m1")), seen["prompt"][-300:])
    r = M.match_one(job, fake('{"identified": [1]}'))
    check("match_one: decoy only -> decoy hit, no true hit", r["valid"] and r["decoy_hit"] and not r["true_hit"])
    r = M.match_one(job, fake('{"identified": [2]}', {"rc": 1, "is_error": True}))
    check("match_one: an errored call is invalid, never a match", r["valid"] is False and "true_hit" not in r)
    r = M.match_one(job, fake(None))
    check("match_one: a timed-out call is invalid", r["valid"] is False)


def t_writeup():
    long = "FINDING " + "x" * 3000 + " the guard is inverted at line 4\nVERDICT: reject\n"
    w = M.writeup_of({"reasons": ["short tail"], "meta": {"answer": long, "answer_tail": long[-800:]}})
    check("writeup uses the whole kept answer", "FINDING" in w and "inverted" in w and "short tail" not in w)
    check("writeup strips the verdict line", "VERDICT" not in w)
    w = M.writeup_of({"reasons": ["r1 found"], "meta": {"answer_tail": "tail text"}})
    check("writeup without a kept answer joins reasons and tail", "r1 found" in w and "tail text" in w, w)
    lng = "START the off-by-one in f.py " + "z" * 400
    w = M.writeup_of({"reasons": [lng], "meta": {"answer_tail": lng[-300:] + " VERDICT: reject"}})
    check("writeup keeps a long reason whose start precedes the tail", "START the off-by-one" in w, w[:80])
    huge = "HEAD" + "y" * (M.WRITEUP_MAX + 500) + "END"
    w = M.writeup_of({"meta": {"answer": huge}})
    check("writeup cap keeps the end", w.endswith("END") and "HEAD" not in w and len(w) == M.WRITEUP_MAX)


def tab_of(rows):
    """rows: {orig: (orig_verdict, [(verdict, hit)])}"""
    return {o: {"orig": ov, "orig_match": False,
                "muts": [("%s-m%d" % (o, i), v, h) for i, (v, h) in enumerate(ms)]} for o, (ov, ms) in rows.items()}


def t_review_fixes():
    w = M.writeup_of({"meta": {"answer": "VERDICT: reject \u2014 foo.py uses > for >=\n**VERDICT: FAIL**"}})
    check("a finding on the verdict line survives, the token does not", w.strip() == "foo.py uses > for >=", repr(w))
    w = M.writeup_of({"reasons": ['{"verdict":"reject","reasons":["x"]}']})
    check("compact verdict JSON is stripped", "reject" not in w, w)
    check("nth counts what occurrences counted", M.mutate_text(
        "aaa aa", {"mid": "m", "path": "p", "find": "aa", "replace": "X", "occurrences": 2, "nth": 2}) == "aaa X")


def t_scoring():
    t = tab_of({"o1": ("accept", [("reject", True), ("reject", False)]), "o2": ("reject", [("accept", False)])})
    check("verdict discrimination = 2/3 - 1/2", abs(M._disc(t, list(t), "verdict") - (2 / 3 - 1 / 2)) < 1e-9)
    check("reason discrimination counts an unmatched reject as a miss",
          abs(M._disc(t, list(t), "reason") - (1 / 3 - 1 / 2)) < 1e-9)
    t2 = tab_of({"o1": ("accept", [("reject", None), ("reject", True)])})
    check("reason mode drops a reject with no valid match", M._rates(t2, "reason")["catch"] == [1, 1])
    allrej = tab_of({"o%d" % i: ("reject", [("reject", True)]) for i in range(6)})
    check("an always-reject reviewer scores 0", M._disc(allrej, list(allrej), "reason") == 0)
    t3 = tab_of({"o%d" % i: ("accept" if i % 3 else "reject", [("reject", i % 2 == 0), (None, False)])
                 for i in range(12)})
    b1, b2 = M.interval([t3], "reason"), M.interval([t3], "reason")
    d = M._disc(t3, list(t3), "reason")
    check("the interval is reproducible and brackets the point", b1 == b2 and b1[0] <= d <= b1[1], "%s %s" % (b1, d))
    u = tab_of({"o1": ("accept", [("reject", True), ("reject", True)]), "o2": ("accept", [("accept", False)])})
    v = tab_of({"o1": ("accept", [(None, False), ("reject", True)]), "o2": (None, [("accept", False)])})
    ru = M.restrict(u, v)
    check("paired restriction keeps only candidates valid for both",
          ru["o2"]["orig"] is None and ru["o1"]["muts"][0][1] is None and ru["o1"]["muts"][1][1] == "reject", str(ru))
    # CRITIC_CALIB_REMEASURE_TIERB_AS_UNLABELLED: a tier-B original is unlabelled - its reject is not a false reject,
    # its mutants still count as labelled defects.
    tb = tab_of({"oA": ("accept", [("reject", True)]), "oB": ("reject", [("reject", True), ("accept", False)])})
    tb["oB"]["labelled"] = False
    r = M._rates(tb, "reason")
    check("an unlabelled (tier-B) reject is not a false reject; its mutants still count",
          r["false_reject"] == [0, 1] and r["unlabelled_reject"] == [1, 1] and r["catch"] == [2, 3], str(r))
    check("discrimination ignores the unlabelled original's verdict",
          abs(M._disc(tb, list(tb), "reason") - (2 / 3 - 0)) < 1e-9)
    tb["oB"]["orig"] = None
    check("an unlabelled original with no valid verdict still contributes its mutants",
          M._rates(tb, "reason")["catch"] == [2, 3])
    check("restrict carries the label", M.restrict(tb, tb)["oB"]["labelled"] is False)
    doc = {"candidates": [{"cid": "a", "role": "good", "tier": "A"}, {"cid": "b", "role": "good", "tier": "B"},
                          {"cid": "ma", "role": "mutant", "pair": "a", "mid": "m1"},
                          {"cid": "mb", "role": "mutant", "pair": "b", "mid": "m2"}]}
    doc["candidates"] += [{"cid": "n", "role": "good"}, {"cid": "mn", "role": "mutant", "pair": "n", "mid": "m3"}]
    rt = M.reviewer_table(doc, {}, {})
    check("reviewer_table labels tier A and unlabels tier B", rt["a"]["labelled"] and not rt["b"]["labelled"], str(rt))
    check("reviewer_table never labels an untiered original good", rt["n"]["labelled"] is False, str(rt))
    sc = {"detect": {"unproved": 0}, "reviewers": {"critic": {"run": "r", "critic_fingerprint": "fp", "invalid": 0, "candidates": 10, "matcher_decoy_hits": [0, 5],
                                   "rejects_without_valid_match": 1}},
          "paired": {"reason": {"ci95": [0.1, 0.4], "sign_flip_p": 0.01}}}
    check("a reject without a valid match grades UNMEASURED", M.decision(sc)["grade"] == "UNMEASURED")
    sc["reviewers"]["critic"]["rejects_without_valid_match"] = 0
    sc["reviewers"]["critic"]["matcher_decoy_hits"] = [2, 5]
    check("a matcher that hits decoys grades UNMEASURED", M.decision(sc)["grade"] == "UNMEASURED")
    sc["reviewers"]["critic"]["matcher_decoy_hits"] = [0, 5]
    check("a clean paired interval above 0 is MEASURED better", M.decision(sc).get("call", "").startswith(
        "critic discriminates better"), str(M.decision(sc)))
    sc["detect"]["unproved"] = 1
    check("a mutant without a proof grades UNMEASURED", M.decision(sc)["grade"] == "UNMEASURED")
    sc["detect"]["unproved"] = 0
    sc["reviewers"]["critic"]["critic_fingerprint"] = None
    check("a run without a critic fingerprint grades UNMEASURED", M.decision(sc)["grade"] == "UNMEASURED")
    sc["reviewers"]["critic"]["critic_fingerprint"] = "fp"
    sc["paired"]["reason"]["ci95"] = [None, None]
    check("an undefined paired interval grades UNMEASURED", M.decision(sc)["grade"] == "UNMEASURED")
    sc["paired"]["reason"]["ci95"] = [-0.1, 0.4]
    check("an interval spanning 0 is not a call", "spans 0" in M.decision(sc).get("call", ""))


def ci(tabs, mode):
    """The interval under test (one table: discrimination; two: the paired difference)."""
    return M.interval(tabs, mode)


def t_small_n():
    """CRITIC_CALIB_FIX_SMALL_N_INTERVAL: at 8 labelled originals the interval must stay honest."""
    # 0/8 false rejects, 16/16 catches: a percentile bootstrap returns [1.0, 1.0]
    z = tab_of({"o%d" % i: ("accept", [("reject", True), ("reject", True)]) for i in range(8)})
    lo, hi = ci([z], "reason")
    check("0/n false rejects gives a non-zero-width interval", lo is not None and hi - lo > 0.1, "%s %s" % (lo, hi))
    # paired: both catch every mutant; the baseline false-rejects 4 of 8 originals, the critic none -> 4 discordant
    a = tab_of({"o%d" % i: ("accept", [("reject", True), ("reject", True)]) for i in range(8)})
    b = tab_of({"o%d" % i: ("reject" if i < 4 else "accept", [("reject", True), ("reject", True)]) for i in range(8)})
    lo, hi = ci([a, b], "reason")
    check("4 discordant labelled originals are not called a difference", lo is not None and lo <= 0 <= hi,
          "%s %s" % (lo, hi))
    # identical reviewers, no discordance at all: still a non-zero-width interval around 0
    lo, hi = ci([a, a], "reason")
    check("no discordant pair still gives a non-zero-width interval", lo < 0 < hi, "%s %s" % (lo, hi))
    # a large, consistent difference is still detected: the interval is not uselessly wide
    big_a = tab_of({"o%d" % i: ("accept", [("reject", True)] * 3) for i in range(12)})
    big_b = tab_of({"o%d" % i: ("reject", [("accept", False)] * 3) for i in range(12)})
    lo, hi = ci([big_a, big_b], "reason")
    check("a large consistent difference is detected", lo is not None and lo > 0, "%s %s" % (lo, hi))
    # the interval brackets the point estimate
    t3 = tab_of({"o%d" % i: ("accept" if i % 3 else "reject", [("reject", i % 2 == 0), (None, False)])
                 for i in range(12)})
    d = M._disc(t3, list(t3), "reason")
    lo, hi = ci([t3], "reason")
    check("the interval brackets the point", lo <= d <= hi, "%s %s %s" % (lo, d, hi))
    lo, hi = ci([b, a], "reason")
    check("the paired interval brackets the paired point", lo <= -0.5 <= hi, "%s %s" % (lo, hi))


def t_exact_pins():
    """Independent check 2026-10-30: the small-n tests above prove only SHAPE (non-zero width, brackets the point), so a
    wrong tail alpha in cp, a swapped MOVER bound or a mis-weighted sign-flip passed them. Pin each primitive to a
    closed form or a brute-force enumeration."""
    import itertools
    import math
    near = lambda x, y: abs(x - y) < 1e-9   # noqa: E731
    for n in (2, 8, 31):
        check("cp(0,%d) upper = 1-(a/2)^(1/n)" % n, near(M.cp(0, n)[1], 1 - 0.025 ** (1 / n)) and M.cp(0, n)[0] == 0,
              str(M.cp(0, n)))
        check("cp(%d,%d) lower = (a/2)^(1/n)" % (n, n), near(M.cp(n, n)[0], 0.025 ** (1 / n)), str(M.cp(n, n)))
        check("cp(1,%d) lower = 1-(1-a/2)^(1/n)" % n, near(M.cp(1, n)[0], 1 - 0.975 ** (1 / n)), str(M.cp(1, n)))
        check("cp(%d,%d) upper = (1-a/2)^(1/n)" % (n - 1, n), near(M.cp(n - 1, n)[1], 0.975 ** (1 / n)),
              str(M.cp(n - 1, n)))
    lo, hi = M._mover(0.5, (0.3, 0.7), 0.2, (0.1, 0.4))
    check("MOVER uses t1's lower with t2's upper for the lower bound",
          near(lo, 0.3 - math.hypot(0.2, 0.2)) and near(hi, 0.3 + math.hypot(0.2, 0.1)), "%s %s" % (lo, hi))
    pt, (plo, phi) = M._paired_term(0, 1, 2)
    h = math.sqrt(0.9875)                    # cp(1,2,0.025) upper; direction cp(0,1,0.025) = [0, 0.9875]
    check("paired term box = exact 97.5% corners", near(pt, -0.5) and near(plo, -h) and near(phi, h * 0.975),
          "%s %s %s" % (pt, plo, phi))
    # sign-flip p against brute force over originals, with unequal cluster weights (catch and false-reject mixed)
    # weights matter here (nm=9, no=5): an unweighted sum of per-original differences gives 0.9375, not 1.0
    ra = {"o0": ("accept", [("reject", True)] * 4), "o4": ("accept", [("reject", True), ("accept", False)])}
    rb = {"o0": ("accept", [("accept", False)] * 4), "o4": ("accept", [("accept", False), ("accept", False)])}
    for o in ("o1", "o2", "o3"):
        ra[o], rb[o] = ("reject", [("accept", False)]), ("accept", [("accept", False)])
    a, b = tab_of(ra), tab_of(rb)
    nm, no = 9, 5
    ks = []
    for o in ra:
        dc = sum((x[0] == "reject" and x[1]) - (y[0] == "reject" and y[1]) for x, y in zip(ra[o][1], rb[o][1]))
        df = (ra[o][0] == "reject") - (rb[o][0] == "reject")
        ks.append(dc * no - df * nm)
    obs = abs(sum(ks))
    want = sum(abs(sum(s * k for s, k in zip(sg, ks))) >= obs
               for sg in itertools.product((1, -1), repeat=len(ks))) / 2 ** len(ks)
    got = M.sign_flip_p(a, b, "reason")
    check("sign_flip_p equals brute-force enumeration over originals", got is not None and near(got, want),
          "%s vs %s (ks %s)" % (got, want, ks))


def t_review_findings():
    """GPT review of CRITIC_CALIB_FIX_SMALL_N_INTERVAL (smalln/gpt.txt), each finding as a test."""
    # 1: the paired difference lives on [-2, 2]; clipping at 1 inverted the bounds
    a = tab_of({"o%d" % i: ("accept", [("reject", True)] * 4) for i in range(8)})
    b = tab_of({"o%d" % i: ("reject", [("accept", False)] * 4) for i in range(8)})
    lo, hi = ci([a, b], "reason")
    check("a maximal paired difference (2) is inside a non-inverted interval", lo <= 2.0 <= hi, "%s %s" % (lo, hi))
    # 2: catch and false-reject discordance move together within an original: 1 row one way, 7 the other
    ra = {"o0": ("accept", [("reject", True)])}
    rb = {"o0": ("reject", [("accept", False)])}
    for i in range(1, 8):
        ra["o%d" % i], rb["o%d" % i] = ("reject", [("accept", False)]), ("accept", [("reject", True)])
    a2, b2 = tab_of(ra), tab_of(rb)
    p = M.sign_flip_p(a2, b2, "reason")
    check("1-vs-7 correlated originals are not significant by the cluster test", p > 0.05, str(p))
    # 3: one original with 24 mutants carries the whole difference: one cluster is never a call
    rc = {"big": ("accept", [("reject", True)] * 24)}
    rd = {"big": ("accept", [("accept", False)] * 24)}
    for i in range(7):
        rc["s%d" % i] = rd["s%d" % i] = ("accept", [("accept", False)])
    p = M.sign_flip_p(tab_of(rc), tab_of(rd), "reason")
    check("a difference carried by one original is not significant", p > 0.5, str(p))
    # the cluster test can still detect: 12 originals all one way
    p = M.sign_flip_p(big_tabs()[0], big_tabs()[1], "reason")
    check("12 concordant originals are significant by the cluster test", p < 0.01, str(p))
    sc = {"detect": {"unproved": 0}, "reviewers": {}, "paired": {"reason": {"ci95": [0.1, 0.4], "sign_flip_p": 0.07}}}
    check("an interval above 0 with cluster p >= 0.05 is not a call", "better" not in M.decision(sc).get("call", ""),
          str(M.decision(sc)))
    # 4: an original's reject that names only the equivalent mutant does not count as naming its paired defect
    doc = {"candidates": [{"cid": "o", "role": "good", "tier": "A"},
                          {"cid": "m1c", "role": "mutant", "pair": "o", "mid": "m1"},
                          {"cid": "mqc", "role": "mutant", "pair": "o", "mid": "m30"}]}
    recs = {"o": {"verdict": "reject"}, "m1c": {"verdict": "accept"}, "mqc": {"verdict": "accept"}}
    rt = M.reviewer_table(doc, recs, {"o": {"true_hit": ["m30"]}})
    check("an original naming only the equivalent mutant is not orig_match", rt["o"]["orig_match"] is False, str(rt))


def t_equivalent_decoys():
    """GPT round 2: an equivalent mutant's own match job does not enter the matcher decoy-hit rate."""
    doc = {"set_sha256": "x", "candidates": [{"cid": "o", "role": "good", "tier": "A"},
           {"cid": "m1c", "role": "mutant", "pair": "o", "mid": "m1", "mutant_kind": "k", "mutant_defect": "d1"},
           {"cid": "mqc", "role": "mutant", "pair": "o", "mid": "m30", "mutant_kind": "k", "mutant_defect": "d30"},
           {"cid": "p", "role": "good", "tier": "A"},
           {"cid": "m2c", "role": "mutant", "pair": "p", "mid": "m2", "mutant_kind": "k", "mutant_defect": "d2"}]}
    recs = {c: {"cid": c, "verdict": "accept"} for c in ("o", "m1c", "p", "m2c")}
    recs["mqc"] = {"cid": "mqc", "verdict": "reject", "reasons": ["x"]}
    job = M.match_jobs(doc, {"r": recs})[0]
    rec = {"valid": True, "key": job["key"], "run": "r", "cid": "mqc", "true_hit": ["m30"], "decoy_hit": False}
    sc = M.score(doc, {"critic": ("r", recs, "fp")}, [rec], {})
    check("an equivalent mutant's match job is not in matcher_decoy_hits",
          sc["reviewers"]["critic"]["matcher_decoy_hits"] == [0, 0], str(sc["reviewers"]["critic"]["matcher_decoy_hits"]))


def t_near_decoy():
    """CRITIC_DECOYS_WIDEN_SAME_ORIGINAL: a sibling is the decoy, a job without one keeps its cross-original decoy."""
    doc = {"set_sha256": "x", "candidates": [{"cid": "o", "role": "good", "tier": "A"}, {"cid": "p", "role": "good", "tier": "A"},
           {"cid": "m1c", "role": "mutant", "pair": "o", "mid": "m1", "mutant_kind": "k", "mutant_defect": "d1"},
           {"cid": "m2c", "role": "mutant", "pair": "o", "mid": "m2", "mutant_kind": "k", "mutant_defect": "d2"},
           {"cid": "m3c", "role": "mutant", "pair": "p", "mid": "m3", "mutant_kind": "k", "mutant_defect": "d3"}]}
    recs = {c: {"cid": c, "verdict": "reject", "reasons": ["x"]} for c in ("o", "m1c", "m2c", "m3c")}
    recs["p"] = {"cid": "p", "verdict": "accept"}
    jobs = {j["cid"]: j for j in M.match_jobs(doc, {"r": recs})}
    decoy = lambda cid: [i[1] for i in jobs[cid]["items"] if i[0] == "decoy"]
    check("a mutant's decoys start with its sibling on the same original",
          jobs["m1c"]["near_mids"] == ["m2"] and jobs["m2c"]["near_mids"] == ["m1"] and "m2" in decoy("m1c"), str(jobs))
    check("a mutant without a sibling keeps cross-original decoys", sorted(decoy("m3c")) == ["m1", "m2"]
          and not jobs["m3c"]["near_decoy"] and jobs["m1c"]["near_decoy"], str(jobs["m3c"]))
    check("every job's list has one length, so the length never tells the role",
          {len(j["items"]) for j in jobs.values()} == {3}, str(jobs))
    check("an original's decoy never comes from its own mutants", decoy("o") == ["m3"] and not jobs["o"]["near_decoy"])
    recm = lambda cid, hit: {"valid": True, "key": jobs[cid]["key"], "run": "r", "cid": cid, "true_hit": [], "decoy_hit": hit,
                             "identified": jobs[cid]["near_mids"] if hit else []}
    sc = M.score(doc, {"critic": ("r", recs, "fp")}, [recm(c, c == "m1c") for c in jobs], {})
    blk = sc["reviewers"]["critic"]
    check("near-decoy hits are counted apart", blk["matcher_near_decoy_hits"] == [1, 2] and blk["matcher_decoy_hits"] == [1, 4],
          str(blk))
    fake = {"detect": {"unproved": 0}, "reviewers": {"critic": dict(blk, matcher_decoy_hits=[1, 40])}}
    v = M.decision(fake)
    check("a near-decoy rate over the limit is UNMEASURED however many easy decoys dilute it",
          v["grade"] == "UNMEASURED" and any("near-decoy" in w for w in v["why"]), str(v))
    # the far decoy of a job that also holds a near one is no near-decoy hit
    far = [i for i in decoy("m1c") if i != "m2"]
    r = dict(recm("m1c", True), identified=far)
    blk = M.score(doc, {"critic": ("r", recs, "fp")}, [r], {})["reviewers"]["critic"]
    check("a far-decoy hit in a near job is not a near-decoy hit", blk["matcher_near_decoy_hits"][0] == 0
          and blk["matcher_decoy_hits"][0] == 1, str(blk))
    # no decoy to draw: no job (never a crash), and the reject stays unmatched
    lone = {"set_sha256": "x", "candidates": [{"cid": "o", "role": "good", "tier": "A"},
            {"cid": "m1c", "role": "mutant", "pair": "o", "mid": "m1", "mutant_kind": "k", "mutant_defect": "d1"}]}
    check("a reject with no decoy to draw gets no job", M.match_jobs(lone, {"r": {"m1c": recs["m1c"]}}) == [])


def t_first_record_wins():
    """CRITIC_MATCHER_HARDEN_ROLE_AND_CONCURRENCY: a duplicate record never changes a judgment already made."""
    doc = {"set_sha256": "S", "candidates": [
        {"cid": "o1", "role": "good", "tier": "A"}, {"cid": "o2", "role": "good", "tier": "A"},
        {"cid": "m1", "role": "mutant", "pair": "o1", "mid": "m1", "mutant_kind": "k", "mutant_defect": "d1"},
        {"cid": "m2", "role": "mutant", "pair": "o2", "mid": "m2", "mutant_kind": "k", "mutant_defect": "d2"}]}
    recs = {"o1": {"cid": "o1", "verdict": "accept"}, "o2": {"cid": "o2", "verdict": "accept"},
            "m1": {"cid": "m1", "verdict": "reject", "reasons": ["x"]}, "m2": {"cid": "m2", "verdict": "accept"}}
    job = M.match_jobs(doc, {"r": recs})[0]
    first = {"key": job["key"], "run": "r", "cid": "m1", "valid": True, "true_hit": ["m1"], "decoy_hit": False, "identified": ["m1"]}
    second = dict(first, true_hit=[], identified=[])
    sc = M.score(doc, {"critic": ("r", recs, "fp")}, [first, second], {})
    sc2 = M.score(doc, {"critic": ("r", recs, "fp")}, [second, first], {})
    check("the first valid match record decides", sc["reviewers"]["critic"]["reason"]["catch"][0] == 1
          and sc2["reviewers"]["critic"]["reason"]["catch"][0] == 0, str(sc["reviewers"]["critic"]))


def t_truncated(root: Path):
    """CRITIC_MATCHER_FIX_TRUNCATED_FALSE_MISS: a cut reject with no match is unmeasured, never a miss."""
    doc = {"set_sha256": "S", "candidates": [
        {"cid": "o1", "role": "good", "tier": "A"}, {"cid": "o2", "role": "good", "tier": "A"},
        {"cid": "m1", "role": "mutant", "pair": "o1", "mid": "m1", "mutant_kind": "k", "mutant_defect": "d1"},
        {"cid": "m2", "role": "mutant", "pair": "o2", "mid": "m2", "mutant_kind": "k", "mutant_defect": "d2"}]}
    huge = {"meta": {"answer": "z" * (M.WRITEUP_MAX + 9)}}
    recs = {"o1": {"cid": "o1", "verdict": "accept"}, "o2": {"cid": "o2", "verdict": "accept"},
            "m1": dict(huge, cid="m1", verdict="reject"), "m2": {"cid": "m2", "verdict": "accept"}}
    job = M.match_jobs(doc, {"r": recs})[0]
    none = {"key": job["key"], "run": "r", "cid": "m1", "valid": True, "true_hit": [], "decoy_hit": False, "identified": []}
    proved = {"m1": {"detect": "read"}, "m2": {"detect": "read"}}
    sc = M.score(doc, {"critic": ("r", recs, "fp")}, [none], proved)
    blk = sc["reviewers"]["critic"]
    check("a cut reject with no match is counted", blk["truncated_unmatched"] == 1, str(blk))
    fake = {"detect": {"unproved": 0}, "reviewers": {"critic": dict(blk, rejects_without_valid_match=0)},
            "paired": {"x": 1}}
    v = M.decision(fake)
    check("a cut unmatched reject grades UNMEASURED", v["grade"] == "UNMEASURED"
          and any("write-up cut" in w for w in v["why"]), str(v))
    hit = dict(none, true_hit=["m1"], identified=["m1"])
    blk = M.score(doc, {"critic": ("r", recs, "fp")}, [hit], proved)["reviewers"]["critic"]
    check("a cut reject the matcher matched is a catch", blk["truncated_unmatched"] == 0, str(blk))
    # overlapping match runs refuse
    out = root / "lock" / "match.jsonl"
    out.parent.mkdir()
    with open(out.with_name(out.name + ".lock"), "w") as lk:
        M.fcntl.flock(lk, M.fcntl.LOCK_EX)
        check("a second match run refuses while the first holds the lock",
              refuses(M.match, doc, ["r"], 10.0, 1, None, out))


def t_review_round_two(root: Path):
    base = {"candidates": [{"cid": "c1", "role": "good"}]}
    check("build reads the adjudication's cids: a true defect is no original",
          refuses(M.build, {"mutants": [{"mid": "m1", "orig": "c1"}]}, base, Path("."),
                  {"cids": {"c1": {"finding": "true_defect", "evidence": "e"}}}))
    jobs = [{"key": k, "run": "r", "cid": k} for k in ("a", "b")]

    def one(j, call):
        if j["key"] == "a":
            raise J.JudgeUnavailable("gone")
        return {"key": "b", "run": "r", "cid": "b", "valid": True}
    keep = M.match_jobs, M.run_records, M.match_one
    M.match_jobs, M.run_records, M.match_one = lambda d, r: jobs, lambda r, d: {}, one
    out = root / "m2" / "match.jsonl"
    try:
        M.match({}, ["r"], 10 ** 4, 2, None, out)
    finally:
        M.match_jobs, M.run_records, M.match_one = keep
    recs = {r["key"]: r for r in C.read_results(out)}
    check("one failed match job leaves the others' answers on disk", recs["b"]["valid"] and not recs["a"]["valid"], str(recs))


def t_proof_output(root: Path):
    """CRITIC_MUTANT_PROOFS_HARDEN_STDOUT_CAP: a noisy proof neither blocks nor grows the harness."""
    real = C.sandbox_argv
    C.sandbox_argv = lambda argv, work, cwd, **k: argv
    try:
        t0 = time.time()
        rc, tail = M.run_in_sandbox(["python3", "-c", "import sys\nfor i in range(600): sys.stdout.write('x'*65536)\nprint('LAST')"],
                                    root, root, 60)
        check("a proof printing 39 MB ends with its real exit and tail", rc == 0 and tail.rstrip().endswith("LAST")
              and len(tail) <= 600 and time.time() - t0 < 50, "%s %r" % (rc, tail[-40:]))
        keep = bytearray()
        import io
        M._drain(io.BytesIO(b"a" * 300000 + b"Z"), keep)
        check("the harness holds only the kept tail", len(keep) == M.PROOF_OUTPUT_KEEP and keep.endswith(b"Z"), str(len(keep)))
        rc, _ = M.run_in_sandbox(["sh", "-c", "yes; sleep 60"], root, root, 2)
        check("a noisy proof past its timeout is killed as 124", rc == 124, str(rc))
    finally:
        C.sandbox_argv = real


def big_tabs():
    a = tab_of({"o%d" % i: ("accept", [("reject", True)] * 3) for i in range(12)})
    b = tab_of({"o%d" % i: ("reject", [("accept", False)] * 3) for i in range(12)})
    return a, b


def t_equivalent():
    """CRITIC_MUTANTS_DELETE_EQUIVALENT_M30: an equivalent mutant is not a labelled defect."""
    doc = {"candidates": [{"cid": "a", "role": "good", "tier": "A"},
                          {"cid": "ma", "role": "mutant", "pair": "a", "mid": "m1"},
                          {"cid": "mq", "role": "mutant", "pair": "a", "mid": "m30"}]}
    recs = {"a": {"verdict": "accept"}, "ma": {"verdict": "accept"}, "mq": {"verdict": "accept"}}
    rt = M.reviewer_table(doc, recs, {})
    check("an equivalent mutant (m30) is not in the catch term", [m[0] for m in rt["a"]["muts"]] == ["m1"], str(rt))


def t_stale_match():
    doc = {"set_sha256": "S", "candidates": [
        {"cid": "o1", "role": "good", "tier": "A"}, {"cid": "o2", "role": "good", "tier": "A"},
        {"cid": "m1", "role": "mutant", "pair": "o1", "mid": "m1", "mutant_kind": "k", "mutant_defect": "d1"},
        {"cid": "m2", "role": "mutant", "pair": "o2", "mid": "m2", "mutant_kind": "k", "mutant_defect": "d2"}]}
    recs = {"o1": {"cid": "o1", "verdict": "accept"}, "o2": {"cid": "o2", "verdict": "accept"},
            "m1": {"cid": "m1", "verdict": "reject", "reasons": ["the d1 defect"]},
            "m2": {"cid": "m2", "verdict": "accept"}}
    job = M.match_jobs(doc, {"r": recs})
    check("one match job per valid reject", [j["cid"] for j in job] == ["m1"], str(job))
    good = {"key": job[0]["key"], "run": "r", "cid": "m1", "valid": True, "true_hit": ["m1"], "decoy_hit": False}
    stale = dict(good, key="0" * 16)
    proved = {"m1": {"detect": "read"}, "m2": {"detect": "test"}}
    sc = M.score(doc, {"critic": ("r", recs, "fp")}, [good], proved)
    check("a current match counts as a catch", sc["reviewers"]["critic"]["reason"]["catch"] == [1, 2]
          and sc["reviewers"]["critic"]["rejects_without_valid_match"] == 0, str(sc["reviewers"]["critic"]))
    sc = M.score(doc, {"critic": ("r", recs, "fp")}, [stale], proved)
    check("a stale match (other write-up, fixture or matcher) is ignored",
          sc["reviewers"]["critic"]["rejects_without_valid_match"] == 1 and sc["verdict"]["grade"] == "UNMEASURED",
          str(sc["reviewers"]["critic"]))
    blk = sc["reviewers"]["critic"]
    check("a reject awaiting its match is not a subgroup miss",
          blk["by_kind"]["k"]["reason_catch"] == [0, 1] and blk["by_detect"]["read"]["reason_catch"] == [0, 0]
          and blk["by_detect"]["read"]["verdict_catch"] == [1, 1], str(blk["by_kind"]) + str(blk["by_detect"]))
    j2 = M.match_jobs(doc, {"r": dict(recs, m1=dict(recs["m1"], reasons=["another write-up"]))})
    check("a changed write-up changes the match key", j2[0]["key"] != job[0]["key"])


class FakeCritic:
    name = "fake"


def t_seed(root: Path):
    cands = [{"cid": "a", "head": "1"}, {"cid": "b", "head": "2"}, {"cid": "c", "head": "3"}]
    old = {"candidates": cands, "set_sha256": M.set_hash(cands)}
    new_cands = [cands[0], {"cid": "b", "head": "2-changed"}, {"cid": "d", "head": "4"}]
    doc = {"candidates": new_cands, "set_sha256": M.set_hash(new_cands)}
    src = root / "runs" / "src"
    src.mkdir(parents=True)
    (src / "run.json").write_text(json.dumps({"critic_fingerprint": "FP", "set_sha256": old["set_sha256"]}))
    (src / "results.jsonl").write_text("".join(json.dumps(r) + "\n" for r in (
        {"cid": "a", "verdict": "reject", "meta": {}}, {"cid": "b", "verdict": "accept", "meta": {}},
        {"cid": "c", "verdict": "accept", "meta": {}})))
    real = C.critic_fingerprint
    try:
        C.critic_fingerprint = lambda critic: "FP"
        out = M.seed(doc, FakeCritic(), "dst", "src", old, root / "runs")
        recs = C.read_results(root / "runs" / "dst" / "results.jsonl")
        check("seed copies only byte-identical candidates", out["seeded"] == 1 and [r["cid"] for r in recs] == ["a"],
              str(out))
        check("seed records the chain", recs[0]["meta"]["seeded_from"] == ["src"])
        out = M.seed(doc, FakeCritic(), "dst", "src", old, root / "runs")
        check("seed twice adds nothing", out["seeded"] == 0)
        dbad = root / "runs" / "dbad"
        dbad.mkdir()
        (dbad / "results.jsonl").write_text(json.dumps({"cid": "a", "verdict": "invalid", "meta": {}}) + "\n")
        check("seed refuses results with no run.json", refuses(M.seed, doc, FakeCritic(), "dbad", "src", old, root / "runs"))
        (dbad / "run.json").write_text(json.dumps({"critic_fingerprint": "FP", "set_sha256": doc["set_sha256"]}))
        out = M.seed(doc, FakeCritic(), "dbad", "src", old, root / "runs")
        check("seed fills a cid that holds only an invalid record", out["seeded"] == 1, str(out))
        src2 = root / "runs" / "src2"
        src2.mkdir()
        (src2 / "run.json").write_text((src / "run.json").read_text())
        (src2 / "results.jsonl").write_text("")
        M.seed(doc, FakeCritic(), "dst", "src2", old, root / "runs")
        M.seed(doc, FakeCritic(), "dst", "src2", old, root / "runs")
        dst_meta = json.loads((root / "runs" / "dst" / "run.json").read_text())
        check("run.json records every seed source once", dst_meta["seeded_from"] == ["src", "src2"], str(dst_meta))
        check("seed refuses a set whose content does not match its sha",
              refuses(M.seed, doc, FakeCritic(), "dst2", "src", dict(old, set_sha256="0" * 64), root / "runs"))
        other = [{"cid": "z"}]
        check("seed refuses a run made on another set",
              refuses(M.seed, doc, FakeCritic(), "dst2", "src", {"candidates": other, "set_sha256": M.set_hash(other)},
                      root / "runs"))
        C.critic_fingerprint = lambda critic: "OTHER"
        check("seed refuses another critic fingerprint",
              refuses(M.seed, doc, FakeCritic(), "dst3", "src", old, root / "runs"))
        (src / "run.json").write_text(json.dumps({"critic_fingerprint": "OTHER", "set_sha256": old["set_sha256"]}))
        check("seed refuses a target run of another critic",
              refuses(M.seed, doc, FakeCritic(), "dst", "src", old, root / "runs"))
    finally:
        C.critic_fingerprint = real


def t_proofs():
    doc = {"set_sha256": "S", "candidates": [{"cid": "o", "role": "good", "head": "H0"},
                                             {"cid": "m", "role": "mutant", "pair": "o", "head": "H1"}]}
    ok_set = {"cid": "m", "set_sha256": "S", "harness": M.proof_harness()}
    ok_heads = {"cid": "m", "set_sha256": "OLD", "heads": ["H0", "H1"], "harness": M.proof_harness()}
    bad = {"cid": "m", "set_sha256": "OLD", "heads": ["H0", "H9"], "harness": M.proof_harness()}
    check("latest accepts a proof on this set", "m" in M.latest([ok_set], doc))
    check("latest accepts a proof on exactly these heads", "m" in M.latest([ok_heads], doc))
    check("latest refuses a proof on other heads of another set", M.latest([bad], doc) == {})
    check("latest refuses an errored proof", M.latest([dict(ok_set, error="x")], doc) == {})
    check("latest refuses a proof of another harness", M.latest([dict(ok_set, harness="other")], doc) == {})


def main() -> int:
    root = Path(tempfile.mkdtemp(prefix="selftest_critic_mutants_"))
    try:
        t_mutate()
        t_commit(root)
        t_matcher()
        t_writeup()
        t_review_fixes()
        t_scoring()
        t_small_n()
        t_exact_pins()
        t_equivalent()
        t_review_findings()
        t_equivalent_decoys()
        t_near_decoy()
        t_first_record_wins()
        t_truncated(root)
        t_review_round_two(root)
        t_proof_output(root)
        t_stale_match()
        t_seed(root)
        t_proofs()
    finally:
        shutil.rmtree(root, ignore_errors=True)
    print("%s: %d failed" % ("FAIL" if FAILS else "PASS", len(FAILS)))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
