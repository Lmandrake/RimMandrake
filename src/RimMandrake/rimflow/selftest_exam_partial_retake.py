#!/usr/bin/env python3
"""selftest_exam_partial_retake.py: after a coverage-judge refusal is repaired, only the exam scenarios the repair
touched are re-run (item RIMMANDRAKE_RETAKE_ONLY_TOUCHED_EXAM_SCENARIOS_CARD_ASKED_TWICE; his card 2026-11-18 4:29 PM
PST, "Retake only what changed"). Six cases, A1 to A6 of the item's criteria, on a fixed concept folder (ten leaves,
a tagged sheet, a passing ten-scenario exam with two Readers' leaf-per-scenario answers) and no model call.

    python3 src/RimMandrake/rimflow/selftest_exam_partial_retake.py      exit 0 when all six cases print PASS

The four outcomes are kept apart: scenarios retaken, answers carried forward, the whole exam retaken because the map
could not tell (A2, A3), and the retake could not run. "Looked, none touched" (A4) is its own outcome, never A3's.
On the base commit there is no exam_retake module, so every case fails (A1, A4 and A5 by construction: a retake
re-runs every scenario).
"""
import json
import os
import shutil
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import concept_tree as CT          # noqa: E402
import designer_stage as DS        # noqa: E402

try:
    import exam_retake as ER       # noqa: E402
except ImportError as e:           # the base: no partial retake exists, every case is red
    ER, MISSING = None, "no exam_retake module (%s): a retake re-runs every scenario" % e
else:
    MISSING = None

LEAVES = ["l%d" % i for i in range(10)]
READERS = ["agent:a973694af5dc4757a", "agent:acddc523961c33401"]
FRESH = ["agent:a1111111111111111", "agent:a2222222222222222"]
FAILS = []


def case(name, fn, root):
    try:
        if ER is None:
            raise AssertionError(MISSING)
        fn(fixture(root, name))
        print("PASS  %s" % name)
    except Exception as e:                     # an exception is a failed case, named, never a crash of the run
        print("FAIL  %s: %s: %s" % (name, type(e).__name__, e))
        FAILS.append(name)


def need(cond, what):
    if not cond:
        raise AssertionError(what)


def put(d, name, obj):
    with open(os.path.join(d, name), "w", encoding="utf-8") as f:
        if isinstance(obj, str):
            f.write(obj)
        else:
            json.dump(obj, f, indent=1)


def read(d, name):
    with open(os.path.join(d, name), encoding="utf-8") as f:
        return json.load(f)


def tree(extra=None):
    leaves = [{"id": x, "experience": "a colonist sees %s happen" % x, "red": "%s never happens" % x}
              for x in LEAVES + ["frame", "spare"]]
    t = {"subject": "Foo", "kind": "mod", "leaves": leaves, "coverage": {}}
    t.update(extra or {})
    return t


def sheet(edit=None):
    lines = ["# Foo: a test concept", "", "## his words", '- 2026-11-18: "make the pit fair"', "", "## does"]
    lines += ["- [leaf:%s] %s happens" % (x, x) for x in LEAVES + ["frame", "spare"]]
    text = "\n".join(lines) + "\n"
    return edit(text) if edit else text


def scenarios():
    return [{"id": "s%d" % i, "text": "a pawn meets case %d at the pit" % i, "expect": "reject: %s says no" % x,
             "expect_source": "leaf:%s" % x, "by": "challenger" if i >= 8 else "examiner"}
            for i, x in enumerate(LEAVES)]


def verdicts(sids, by_id=None):
    """Each Reader's answer per scenario, with the leaves it relied on: its own leaf and `frame`, which every scenario
    reads. `spare` is read by none."""
    return [{"id": s, "verdict": "reject", "leaf": ["l%s" % s[1:], "frame"]} for s in sids]


def control(d, sids_missed=("s0",)):
    DS.exam_control(d, "l0")
    return {"broken_leaf": "l0", "missed": True, "missed_ids": list(sids_missed)}


def fixture(root, name):
    """A stage-5 concept whose exam passes on its current tree, with the read map recorded at exam time."""
    rd = os.path.join(root, name.split(":")[0])
    d = os.path.join(rd, "design", "concepts", "Foo")
    os.makedirs(d)
    put(d, "tree.json", tree())
    put(d, "sheet.md", sheet())
    put(d, "scenes.json", {"scenes": [], "showcases": []})
    st = {"stage": 5, "status": "open", "results": [], "history": []}
    put(d, "stage.json", st)
    sc = scenarios()
    cur = DS.inputs(d, st, rd)
    ex = {"author": "rm-role-designer-1", "examiner": "agent:ade4a89b3cdad9f61", "challenger": "agent:a0123456789abcdef",
          "inputs": {"tree": cur["tree"], "sheet": cur["sheet"]}, "scenarios": sc, "scenarios_hash": CT.sha(sc),
          "readers": list(READERS), "reader_verdicts": {r: verdicts([s["id"] for s in sc]) for r in READERS},
          "score": {"right": 10, "total": 10}, "accept_where_reject_core": 0, "challenger_misses": [],
          "control": control(d)}
    put(d, "exam.json", ex)
    errs = DS.exam_errors(ex, d, st, rd)
    need(errs == [], "fixture: the base exam does not pass its gate: %s" % errs)
    rec = ER.record(d, repo=rd)
    need(isinstance(rec, dict) and os.path.isfile(os.path.join(d, ER.READS_FILE)), "fixture: no read map recorded: %r"
         % (rec,))
    return rd, d


def repair_leaves(d, ids):
    t = read(d, "tree.json")
    for x in t["leaves"]:
        if x["id"] in ids:
            x["red"] += " (repaired: the gap the judge named is closed)"
    put(d, "tree.json", t)


def fresh_file(d, sids, root):
    p = os.path.join(root, "fresh_%s.json" % "_".join(sids or ["none"]))
    put(os.path.dirname(p), os.path.basename(p), {
        "readers": FRESH, "reader_verdicts": {r: verdicts(sids) for r in FRESH}, "accept_where_reject_core": 0,
        "control": control(d), "inputs": {k: DS.input_hash(d, k) for k in ("tree", "sheet")},
        "scenarios_hash": CT.sha(scenarios())})
    return p


# ---------------------------------------------------------------- the six cases

def a1(fx):
    rd, d = fx
    old = read(d, "exam.json")
    repair_leaves(d, ["l3", "l7"])
    p = ER.plan(d, repo=rd)
    need(p["outcome"] == ER.PARTIAL, "outcome %r, not partial: %s" % (p["outcome"], p.get("why")))
    need(p["retake"] == ["s3", "s7"], "retake %r, not exactly s3 and s7" % p["retake"])
    need(sorted(p["carry"]) == sorted("s%d" % i for i in range(10) if i not in (3, 7)), "carry %r" % p["carry"])
    stale = fresh_file(d, ["s3", "s7"], rd)
    f = read(rd, os.path.basename(stale))
    f["inputs"] = dict(f["inputs"], tree="0" * 64)    # Readers shown another tree than the current one
    put(rd, os.path.basename(stale), f)
    try:
        ER.carry(d, stale, repo=rd)
        need(False, "fresh answers given on another tree were carried")
    except ER.Refused as e:
        need("could not run" in str(e) and read(d, ER.PLAN_FILE)["outcome"] == ER.CANNOT_RUN, str(e))
    new = ER.carry(d, fresh_file(d, ["s3", "s7"], rd), repo=rd)
    ex = read(d, "exam.json")
    car = ex.get("carried") or {}
    need(sorted(car) == sorted(p["carry"]), "exam.json carried %r, not the eight" % sorted(car))
    need(all(c["from"]["tree"] == old["inputs"]["tree"] and c["from"]["scenarios_hash"] == old["scenarios_hash"]
             for c in car.values()), "a carried answer does not name the exam it came from")
    need("s3" not in car and "s7" not in car, "a retaken scenario is marked carried")
    need(ex["retake"]["retaken"] == ["s3", "s7"] and ex["retake"]["outcome"] == ER.PARTIAL, ex.get("retake"))
    need(ex["score"] == {"right": 10, "total": 10}, "score %r" % ex["score"])
    errs = DS.exam_errors(ex, d, read(d, "stage.json"), rd)
    need(errs == [], "the carried exam does not pass its gate: %s" % errs)
    need(new["outcome"] == ER.PARTIAL, new)


def a2(fx):
    rd, d = fx
    repair_leaves(d, ["spare"])                         # a leaf no scenario's read record covers
    p = ER.plan(d, repo=rd)
    need(p["outcome"] == ER.WHOLE and "spare" in p["why"] and "no scenario" in p["why"], "unread leaf: %r" % p)
    put(d, "tree.json", tree())
    repair_leaves(d, ["frame"])                         # a leaf every scenario reads
    p = ER.plan(d, repo=rd)
    need(p["outcome"] == ER.WHOLE and "frame" in p["why"] and "every scenario" in p["why"], "every-read leaf: %r" % p)
    put(d, "tree.json", tree())
    put(d, "sheet.md", sheet(lambda t: t.replace("make the pit fair", "make the pit fair and deep")))
    p = ER.plan(d, repo=rd)                             # an untagged sheet line: his words, read by every scenario
    need(p["outcome"] == ER.WHOLE and "every scenario" in p["why"], "untagged sheet line: %r" % p)
    put(d, "sheet.md", sheet())
    t = tree()
    t["leaves"][2], t["leaves"][3] = t["leaves"][3], t["leaves"][2]
    put(d, "tree.json", t)                              # a reorder: "the earlier rule wins" reads every leaf's place
    p = ER.plan(d, repo=rd)
    need(p["outcome"] == ER.WHOLE and "every scenario" in p["why"], "leaf reorder: %r" % p)
    t = tree()
    t["leaves"].append({"id": "l_new", "experience": "a new leaf", "red": "none of it"})
    put(d, "tree.json", t)                              # a new leaf: no read record can cover it
    p = ER.plan(d, repo=rd)
    need(p["outcome"] == ER.WHOLE and "l_new" in p["why"], "new leaf: %r" % p)
    need(all(p2["retake"] == [] and p2["carry"] == [] for p2 in [p]), "a whole retake lists scenarios: %r" % p)
    refused = False
    try:
        ER.carry(d, fresh_file(d, ["s3"], rd), repo=rd)
    except ER.Refused as e:
        refused = "whole" in str(e)
    need(refused, "carry applied a partial retake where the map could not tell")


def a3(fx):
    rd, d = fx
    repair_leaves(d, ["l3"])
    good = read(d, ER.READS_FILE)
    thin = json.loads(json.dumps(good))
    thin["scenarios"]["s4"]["reads"] = ["l4"]          # the map forgot that s4 read `frame`
    put(d, ER.READS_FILE, thin)
    p = ER.plan(d, repo=rd)
    need(p["outcome"] == ER.WHOLE and "disagrees" in p["why"], "a thinned map: %r" % p)
    put(d, ER.READS_FILE, dict(good, exam=["bad"]))
    p = ER.plan(d, repo=rd)
    need(p["outcome"] == ER.WHOLE, "a map whose exam is no object: %r" % p)
    os.unlink(os.path.join(d, ER.READS_FILE))
    p = ER.plan(d, repo=rd)
    need(p["outcome"] == ER.WHOLE and "no read map" in p["why"], "missing map: %r" % p)
    need(p["outcome"] != ER.NONE_TOUCHED and p["retake"] == [] and p["carry"] == [], "missing map read as none: %r" % p)
    put(d, ER.READS_FILE, "{not json")
    p = ER.plan(d, repo=rd)
    need(p["outcome"] == ER.WHOLE and "cannot be read" in p["why"], "unreadable map: %r" % p)
    put(d, ER.READS_FILE, dict(good, exam=dict(good["exam"], tree="0" * 64)))
    p = ER.plan(d, repo=rd)
    need(p["outcome"] == ER.WHOLE and "another exam" in p["why"], "a map of another exam: %r" % p)
    with open(os.path.join(d, "tree.json"), "w") as f:  # the fourth outcome: the retake cannot run at all
        f.write("{broken")
    p = ER.plan(d, repo=rd)
    need(p["outcome"] == ER.CANNOT_RUN and "tree.json" in p["why"], "unreadable tree: %r" % p)


def a4(fx):
    rd, d = fx
    put(d, "scenes.json", {"scenes": [{"id": "moved"}], "showcases": []})   # the repair touched no exam input
    p = ER.plan(d, repo=rd)
    need(p["outcome"] == ER.NONE_TOUCHED, "outcome %r: %s" % (p["outcome"], p.get("why")))
    need(p["retake"] == [] and len(p["carry"]) == 10, "retake %r carry %r" % (p["retake"], p["carry"]))
    need(p["outcome"] not in (ER.WHOLE, ER.CANNOT_RUN) and "looked" in p["why"], "not recorded as looked: %r" % p)
    w = ER.write_plan(d, p)
    need(read(d, ER.PLAN_FILE)["outcome"] == ER.NONE_TOUCHED and w["outcome"] == ER.NONE_TOUCHED,
         "the none-touched look is not recorded on disk")


def a5(fx):
    rd, d = fx
    repair_leaves(d, ["l3"])
    sc = scenarios()
    sc[5] = dict(sc[5], text=sc[5]["text"] + " while it rains")       # the Examiner revised s5's text
    p = ER.plan(d, scenarios=sc, repo=rd)
    need(p["outcome"] == ER.PARTIAL and p["retake"] == ["s3", "s5"], "retake %r: %s" % (p["retake"], p.get("why")))
    need("s5" not in p["carry"], "a scenario whose text changed is carried")
    fp = fresh_file(d, ["s3", "s5"], rd)
    f = read(rd, os.path.basename(fp))
    f["scenarios"], f["scenarios_hash"] = sc, CT.sha(sc)
    put(rd, os.path.basename(fp), f)
    ER.carry(d, fp, repo=rd)
    ex = read(d, "exam.json")
    need("s5" not in ex["carried"] and ex["scenarios_hash"] == CT.sha(sc), "s5 carried or the set not refrozen")
    need(DS.exam_errors(ex, d, read(d, "stage.json"), rd) == [], DS.exam_errors(ex, d, read(d, "stage.json"), rd))
    # the gate, too, refuses a carried answer whose scenario was edited after the carry
    ex["scenarios"][1] = dict(ex["scenarios"][1], text="a changed situation")
    ex["scenarios_hash"] = CT.sha(ex["scenarios"])
    put(d, "exam.json", ex)
    errs = DS.exam_errors(ex, d, read(d, "stage.json"), rd)
    need(any("carried" in e and "s1" in e for e in errs), "the gate kept a stale carried answer: %s" % errs)


def a6(fx):
    rd, d = fx
    import maturation_autonomy as MA
    import coverage_judge as CJ
    need(MA.exam_gate(rd, "Foo")[0] == [], "the passing exam does not read clean: %s" % MA.exam_gate(rd, "Foo")[0])
    repair_leaves(d, ["l3", "l7"])
    errs, _ = MA.exam_gate(rd, "Foo")
    need(errs and any("another tree" in e for e in errs), "a repaired tree with the old exam passes the gate: %s" % errs)
    what, why = CJ.plan(d, repo=rd)
    need(what == "skip" and "the exam does not pass" in why, "the coverage judge would look: %s %s" % (what, why))
    ER.write_plan(d, ER.plan(d, repo=rd))               # a plan alone moves no gate
    need(MA.exam_gate(rd, "Foo")[0], "a retake plan alone made the exam pass")
    ER.carry(d, fresh_file(d, ["s3", "s7"], rd), repo=rd)
    need(MA.exam_gate(rd, "Foo")[0] == [], "the carried exam does not pass: %s" % MA.exam_gate(rd, "Foo")[0])
    repair_leaves(d, ["l2"])                            # a later edit to a leaf a carried answer read
    DS.exam_control(d, "l0")
    ex = read(d, "exam.json")
    ex["inputs"]["tree"] = DS.input_hash(d, "tree")     # even an exam re-pinned by hand to the new tree
    put(d, "exam.json", ex)
    errs, _ = MA.exam_gate(rd, "Foo")
    need(any("carried" in e and "s2" in e for e in errs), "a carried answer over a changed leaf passes: %s" % errs)
    what, why = CJ.plan(d, repo=rd)
    need(what == "skip" and "the exam does not pass" in why, "the coverage judge would look: %s %s" % (what, why))


def main():
    root = tempfile.mkdtemp(prefix="exam_retake_")
    try:
        for name, fn in (("A1: two touched of ten are re-run, eight carried and marked", a1),
                         ("A2: an unread leaf, an every-read leaf, his words or a new leaf retakes the whole exam", a2),
                         ("A3: a missing or unreadable map retakes the whole exam, never 'nothing touched'", a3),
                         ("A4: nothing a scenario read changed: zero re-run, recorded as looked, none touched", a4),
                         ("A5: a scenario whose text changed is re-run, not carried", a5),
                         ("A6: the coverage judge still never looks at a tree whose exam has not passed", a6)):
            case(name, fn, root)
    finally:
        shutil.rmtree(root, ignore_errors=True)
    print("%d of 6 cases pass" % (6 - len(FAILS)))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
