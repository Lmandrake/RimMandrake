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
                candidates valid for both reviewers; an always-reject reviewer scores 0; the bootstrap is reproducible;
                a match record whose key is not the current job's (other write-up, fixture or matcher) is ignored;
                an unproved mutant or a run without a critic fingerprint grades UNMEASURED
  seed          copies only byte-identical candidates; refuses another fingerprint, another set, a set whose content
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
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
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
    b1, b2 = M.boot([t3], list(t3), "reason", 400), M.boot([t3], list(t3), "reason", 400)
    d = M._disc(t3, list(t3), "reason")
    check("bootstrap is reproducible and brackets the point", b1 == b2 and b1[0] <= d <= b1[1], "%s %s" % (b1, d))
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
    rt = M.reviewer_table(doc, {}, {})
    check("reviewer_table labels tier A and unlabels tier B", rt["a"]["labelled"] and not rt["b"]["labelled"], str(rt))
    sc = {"detect": {"unproved": 0}, "reviewers": {"critic": {"run": "r", "critic_fingerprint": "fp", "invalid": 0, "candidates": 10, "matcher_decoy_hits": [0, 5],
                                   "rejects_without_valid_match": 1}},
          "paired": {"reason": {"ci95": [0.1, 0.4]}}}
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
    sc["paired"]["reason"]["ci95"] = [-0.1, 0.4]
    check("an interval spanning 0 is not a call", "spans 0" in M.decision(sc).get("call", ""))


def t_stale_match():
    doc = {"set_sha256": "S", "candidates": [
        {"cid": "o1", "role": "good"}, {"cid": "o2", "role": "good"},
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
    sc = M.score(doc, {"critic": ("r", recs, "fp")}, [good], proved, reps=50)
    check("a current match counts as a catch", sc["reviewers"]["critic"]["reason"]["catch"] == [1, 2]
          and sc["reviewers"]["critic"]["rejects_without_valid_match"] == 0, str(sc["reviewers"]["critic"]))
    sc = M.score(doc, {"critic": ("r", recs, "fp")}, [stale], proved, reps=50)
    check("a stale match (other write-up, fixture or matcher) is ignored",
          sc["reviewers"]["critic"]["rejects_without_valid_match"] == 1 and sc["verdict"]["grade"] == "UNMEASURED",
          str(sc["reviewers"]["critic"]))
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
    ok_set = {"cid": "m", "set_sha256": "S"}
    ok_heads = {"cid": "m", "set_sha256": "OLD", "heads": ["H0", "H1"]}
    bad = {"cid": "m", "set_sha256": "OLD", "heads": ["H0", "H9"]}
    check("latest accepts a proof on this set", "m" in M.latest([ok_set], doc))
    check("latest accepts a proof on exactly these heads", "m" in M.latest([ok_heads], doc))
    check("latest refuses a proof on other heads of another set", M.latest([bad], doc) == {})
    check("latest refuses an errored proof", M.latest([dict(ok_set, error="x")], doc) == {})


def main() -> int:
    root = Path(tempfile.mkdtemp(prefix="selftest_critic_mutants_"))
    try:
        t_mutate()
        t_commit(root)
        t_matcher()
        t_writeup()
        t_scoring()
        t_stale_match()
        t_seed(root)
        t_proofs()
    finally:
        shutil.rmtree(root, ignore_errors=True)
    print("%s: %d failed" % ("FAIL" if FAILS else "PASS", len(FAILS)))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
