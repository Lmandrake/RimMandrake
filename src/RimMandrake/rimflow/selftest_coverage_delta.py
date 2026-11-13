#!/usr/bin/env python3
"""selftest_coverage_delta.py - the coverage judge re-judges only what changed (RIMMANDRAKE_REJUDGE_ONLY_CHANGED_GAPS,
owner fix D, OWNER.jsonl:1794527688430451936).

After round 1 the judge is shown only the gaps the Designer claims fixed in coverage_fixes.json (with its evidence) and
the entries whose hash changed; unclaimed gaps carry open; a new gap on unchanged material counts only tagged late with a
why; nothing claimed and nothing changed runs no judge; a prior verdict with no hashes gets a full judge. The claude call,
the signature and the exam are stubbed; every write goes to a temp dir, and the real alarm and told files are counted
before and after."""
import json
import os
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import concept_tree as CT  # noqa: E402
import coverage_judge as CJ  # noqa: E402
import designer_stage as DS  # noqa: E402
from selftest_coverage_judge import concept  # noqa: E402
from selftest_designer_park import real_marks  # noqa: E402

FAILS = []


def check(name, ok, got=""):
    print("%s %s%s" % ("ok  " if ok else "FAIL", name, "" if ok else "  got: %r" % (got,)))
    if not ok:
        FAILS.append(name)


class Judge:
    """Answers the next scripted verdict and keeps every prompt it was given."""

    def __init__(self):
        self.script, self.prompts = [], []

    def __call__(self, argv, cwd, env, timeout):
        self.prompts.append(argv[2])
        return 0, self.script.pop(0)


def answer(verdict, gaps=(), rows=()):
    return json.dumps({"structured_output": {"verdict": verdict, "gaps": [dict(g) for g in gaps], "reasons": "r",
                                             "checklist": [dict(r) for r in rows]},
                       "session_id": "s", "usage": {"input_tokens": 1000, "output_tokens": 0,
                                                    "cache_read_input_tokens": 0, "cache_creation_input_tokens": 0}})


def row(i, ok=True, scene="sc_a"):
    return {"id": i, "parts": [{"what": "part of %s" % i, "scene": scene, "ok": ok}]}


def gap(ids, what, tag="first", **kw):
    return dict({"what": what, "where": "record.json", "return_to": 3, "ids": list(ids), "new_since": tag}, **kw)


def write(d, name, obj):
    with open(os.path.join(d, name), "w") as f:
        if isinstance(obj, str):
            f.write(obj)
        else:
            json.dump(obj, f)


def edit(d, name, fn):
    with open(os.path.join(d, name)) as f:
        obj = json.load(f)
    fn(obj)
    write(d, name, obj)


def make(root):
    d = concept(root)
    write(d, "record.json", {"inventory": [{"id": i, "what": "capability %s" % i} for i in
                                           ("inv_a", "inv_b", "inv_c", "inv_e")]})
    write(d, "tree.json", {"kind": "mod", "leaves": [{"id": "leaf_d", "experience": "he sees d"}]})
    write(d, "scenes.json", {"scenes": [{"id": "sc_a", "expect": "a moves"}, {"id": "sc_b", "expect": "b moves"}],
                             "showcases": [], "coverage_rest": []})
    write(d, "sheet.md", "# Foo\n\n## Does\nthrows goods\n\n## Does not\nfly pawns\n")
    return d


def verdict(d):
    with open(os.path.join(d, CJ.VERDICT_FILE)) as f:
        return json.load(f)


def fixes(d, against, claims):
    write(d, CJ.FIXES_FILE, {"against": against, "claims": claims})


ALL_ROWS = [row("inv_a"), row("inv_b", scene="sc_b"), row("inv_c", scene="sc_b"), row("inv_e", scene="sc_b"),
            row("leaf_d", scene="sc_b")]


def main_walk(root):
    d, j = make(os.path.join(root, "walk")), Judge()
    repo = os.path.join(root, "walk")
    j.script.append(answer("not_covered", [gap(["inv_a"], "A IS BROKEN"), gap(["inv_b"], "B IS BROKEN"),
                                           gap(["leaf_d"], "D IS BROKEN")], ALL_ROWS))
    rec, _ = CJ.run(d, repo, j, now=1794000000)
    v = verdict(d)
    check("round 1 is a full judge and its verdict keeps a hash per entry and numbered gaps",
          v["mode"] == "full" and [g["gid"] for g in v["gaps"]] == ["g1", "g2", "g3"]
          and {"inv:inv_a", "leaf:leaf_d", "scene:sc_a", "sheet:Does", "floor"} <= set(v["hashes"])
          and "Read, in this order" in j.prompts[0], (v.get("mode"), v.get("gaps"), sorted(v.get("hashes") or {})))

    calls = len(j.prompts)
    what, why = CJ.plan(d, repo)
    rec, msg = CJ.run(d, repo, j, now=1794000100)
    check("nothing claimed and nothing changed: no judge runs and no round is recorded",
          what == "skip" and "nothing claimed" in why and rec is None and len(j.prompts) == calls
          and len(DS.load_state(d).get("coverage_rounds") or []) == 1, (what, why, msg))

    fixes(d, "rm-coverage-judge-1", [{"gap": "g1", "evidence": "x"}])
    what, why = CJ.plan(d, repo)
    check("a fixes file against another verdict claims nothing (stale), and says so",
          what == "skip" and "not the last verdict" in why, (what, why))

    fixes(d, v["judge"], [{"gap": "g1", "evidence": "sc_a now stages 10x10; see scenes.json sc_a"},
                          {"gap": "g9", "evidence": "y"}, {"gap": "g2", "evidence": "  "}])
    edit(d, "scenes.json", lambda s: s["scenes"][0].update(expect="a moves 10x10"))
    j.script.append(answer("not_covered", [gap(["inv_c"], "C NEW UNTAGGED", "unfixed"),
                                           gap(["inv_e"], "E MISSED", "late", late_why="the earlier judge never "
                                               "opened inv_e's impl_evidence"),
                                           gap(["inv_a"], "A STILL HALF", "unfixed")], [row("inv_a", ok=False)]))
    rec, _ = CJ.run(d, repo, j, now=1794000200)
    p = j.prompts[-1]
    v2 = verdict(d)
    check("round 2 is a delta: the prompt carries the claimed gap with its evidence and the changed scene whole",
          v2["mode"] == "delta" and "g1" in p and "sc_a now stages 10x10" in p and "a moves 10x10" in p
          and "scene:sc_a" in p, p[:300])
    check("the delta prompt does not carry unchanged entries or the unclaimed gaps' evidence, nor send him to the files",
          "capability inv_c" not in p and "he sees d" not in p and "Read, in this order" not in p
          and "throws goods" not in p, p)
    check("the delta checklist is owed only for the claimed and changed rows",
          "one row for each of these ids, none skipped: inv_a." in p, p[-400:])
    check("claims on an unknown gap or with no evidence are refused and recorded",
          len(v2.get("claims_refused") or []) == 2 and [c["gap"] for c in v2["claims"]] == ["g1"],
          v2.get("claims_refused"))
    whats = [g["what"] for g in v2["gaps"]]
    check("an untagged new gap on unchanged material is dropped; a late gap with its why counts",
          "C NEW UNTAGGED" not in whats and "E MISSED" in whats
          and [g["what"] for g in v2.get("dropped") or []] == ["C NEW UNTAGGED"], (whats, v2.get("dropped")))
    check("unclaimed gaps carry open, tagged unfixed; the still-open claim stays; gaps renumbered",
          "B IS BROKEN" in whats and "D IS BROKEN" in whats and "A STILL HALF" in whats
          and all(g.get("carried") for g in v2["gaps"] if g["what"] in ("B IS BROKEN", "D IS BROKEN"))
          and [g["gid"] for g in v2["gaps"]] == ["g%d" % k for k in range(1, len(v2["gaps"]) + 1)], v2["gaps"])
    ids = [r["id"] for r in v2["checklist"]]
    check("the merged checklist keeps every prior row it did not redo, and the redone row is the new one",
          sorted(ids) == sorted(r["id"] for r in ALL_ROWS)
          and next(r for r in v2["checklist"] if r["id"] == "inv_a")["parts"][0]["ok"] is False, v2["checklist"])
    check("the round's gap ids still name every open row", DS.load_state(d)["coverage_rounds"][-1]["ids"] == [
        "inv_a", "inv_b", "inv_e", "leaf_d"], DS.load_state(d)["coverage_rounds"][-1])


def covered_cases(root):
    d, j = make(os.path.join(root, "cov")), Judge()
    repo = os.path.join(root, "cov")
    j.script.append(answer("not_covered", [gap(["inv_b"], "B"), gap(["leaf_d"], "D")], ALL_ROWS))
    CJ.run(d, repo, j, now=1794100000)
    v = verdict(d)
    fixes(d, v["judge"], [{"gap": "g1", "evidence": "inv_b gains a scene"}])
    edit(d, "record.json", lambda r: r["inventory"][1].update(what="capability inv_b, now staged"))
    j.script.append(answer("covered", [gap([], "SHEET VAGUE", "unfixed")], [row("inv_b")]))
    rec, _ = CJ.run(d, repo, j, now=1794100100)
    check("a covered word with a gap still carried is not_covered, and does not sign; a row-less new gap when only "
          "rows changed is dropped",
          rec["verdict"] == "not_covered" and not rec["signed"] and [g["what"] for g in rec["gaps"]] == ["D"],
          (rec.get("verdict"), rec.get("gaps")))
    check("a changed inventory entry puts its row in the delta",
          "inv:inv_b" in j.prompts[-1] and "now staged" in j.prompts[-1], j.prompts[-1][-500:])

    d, j = make(os.path.join(root, "sign")), Judge()
    repo = os.path.join(root, "sign")
    j.script.append(answer("not_covered", [gap(["inv_a"], "A")], ALL_ROWS))
    CJ.run(d, repo, j, now=1794200000)
    fixes(d, verdict(d)["judge"], [{"gap": "g1", "evidence": "sc_a asserts the start now"}])
    j.script.append(answer("covered", [], [row("inv_a")]))
    rec, _ = CJ.run(d, repo, j, now=1794200100)
    check("every gap claimed and confirmed fixed: covered, signed, the whole checklist on file",
          rec["verdict"] == "covered" and rec["signed"] and rec["mode"] == "delta" and len(rec["checklist"]) == 5,
          (rec.get("verdict"), rec.get("signed"), rec.get("error")))


def fallbacks(root):
    d, j = make(os.path.join(root, "legacy")), Judge()
    repo = os.path.join(root, "legacy")
    write(d, CJ.VERDICT_FILE, {"judge": "rm-coverage-judge-1", "verdict": "not_covered",
                               "gaps": [{"what": "old", "ids": ["inv_a"]}], "checklist": ALL_ROWS})
    what, _ = CJ.plan(d, repo)
    j.script.append(answer("not_covered", [gap(["inv_a"], "old", "unfixed")], ALL_ROWS))
    rec, _ = CJ.run(d, repo, j, now=1794300000)
    check("a legacy verdict with no hashes gets a full judge, which leaves hashes for the next",
          what == "judge" and rec["mode"] == "full" and "Read, in this order" in j.prompts[-1] and rec.get("hashes"),
          (what, rec.get("mode")))
    for bad in ({"verdict": "covered"}, {"error": "the tree changed"}, {"unchecked": ["inv_a"]}):
        prior = dict(verdict(d), **bad)
        check("a prior verdict with %s gets a full judge" % sorted(bad), CJ.delta_plan(d, prior) is None)


def units(root):
    d = make(os.path.join(root, "units"))
    h0 = CJ.entry_hashes(d)
    edit(d, "tree.json", lambda t: t.update(coverage={"signed_by": "CoverageJudge", "tree": "abc"}))
    check("a signature stamp in tree.json is not a change", CJ.entry_hashes(d) == h0)
    write(d, "sheet.md", "# Foo\n\n## Does\nthrows goods far\n\n## Does not\nfly pawns\n")
    h1 = CJ.entry_hashes(d)
    check("a sheet edit changes only its own section",
          sorted(k for k in h0 if h0[k] != h1.get(k)) == ["sheet:Does"], sorted(k for k in h0 if h0[k] != h1.get(k)))
    check("entries read a commit through `read`",
          set(CJ.entries(d, lambda n: '{"inventory": [{"id": "z"}]}' if n == "record.json" else None)) == {
              "inv:z", "record:scope", "floor"})
    check("the schema lets a gap carry late_why",
          "late_why" in CJ.SCHEMA["properties"]["gaps"]["items"]["properties"])


def main():
    CJ.CONTRACT = False   # bare gaps test another rule; the refusal record is selftest_coverage_refusal_record
    DS.owner_away = lambda: (False, "selftest: attended")   # the real presence must not move this test
    saved = (CT.coverage_problem, CT.sign, DS.exam_errors)
    CT.coverage_problem = lambda d, repo, tree: "no coverage signature"
    CT.sign = lambda d, by, repo=None, **kw: []
    DS.exam_errors = lambda ex, d, st, repo=None: []
    env = {k: os.environ.get(k) for k in ("RM_REFUSAL_DIR", "RM_OPS_WATCH_DIR", "RM_DISPATCHER_STATE")}
    marks = real_marks()
    try:
        with tempfile.TemporaryDirectory() as root:
            ops = os.path.join(root, "ops")
            os.makedirs(ops)
            os.environ.update(RM_REFUSAL_DIR=os.path.join(root, "refusals"), RM_OPS_WATCH_DIR=ops,
                              RM_DISPATCHER_STATE=os.path.join(root, "dispatcher"))
            main_walk(root)
            covered_cases(root)
            fallbacks(root)
            units(root)
    finally:
        CT.coverage_problem, CT.sign, DS.exam_errors = saved
        for k, v in env.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v
    check("the real alarm and told files are untouched", real_marks() == marks, (marks, real_marks()))
    print("selftest_coverage_delta: %s" % ("FAIL (%d)" % len(FAILS) if FAILS else "PASS"))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
