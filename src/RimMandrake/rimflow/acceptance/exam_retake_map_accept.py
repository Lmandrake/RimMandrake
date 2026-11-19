#!/usr/bin/env python3
"""exam_retake_map_accept.py: the one acceptance test of the partial exam retake (item
RIMMANDRAKE_RETAKE_ONLY_TOUCHED_EXAM_SCENARIOS_CARD_ASKED_TWICE; his card 2026-11-18 4:29 PM PST, "Retake only what
changed"; the Conductor's ruling on it: the exam still runs first, only the scenarios a repair touched re-run, the whole
exam is retaken whenever the map cannot tell, and "looked, none touched", "whole", "partial" and "could not run" are
four distinct outcomes). No model call.

    python3 src/RimMandrake/rimflow/acceptance/exam_retake_map_accept.py      exit 0 when every check prints PASS

Two parts, merged from two tests that were written apart (item RIMMANDRAKE_RECONCILE_TWO_EXAM_RETAKE_TESTS_LEAF_VERSUS_FILE):
  THE MAP: the design run's leaf-level cases, each driven through exam_retake.record and exam_retake.plan on a real
    concept folder: a five-leaf tree and tagged sheet, a ten-scenario exam that passes its gate, two Readers whose
    answers name the leaves they relied on (READS, split between them), the map recorded, then the repair written.
    The design's {exam["reads"]} is exam_reads.json here; its mode "none" is exam_retake's none_touched.
  THE STAGE MACHINE: the builder's A1 to A6 of the item's criteria (carry, the gate re-checking a carry, the coverage
    judge still skipping a tree whose exam does not pass).
"""
import copy
import hashlib
import json
import os
import shutil
import sys
import tempfile

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, HERE)
import concept_tree as CT          # noqa: E402
import designer_stage as DS        # noqa: E402
import exam_retake as ER           # noqa: E402

FAILS, RUN = [], [0]


def check(name, ok, got=""):
    RUN[0] += 1
    print("%s  %s%s" % ("PASS" if ok else "FAIL", name, "" if ok else "  got: %s" % (got,)))
    if not ok:
        FAILS.append(name)


# ---------------------------------------------------------------- the map, leaf by leaf

IDS = ["l%d" % i for i in range(1, 6)]
TREE = {"subject": "Foo", "root_ref": "x", "advisory": ["tune later"],
        "leaves": [{"id": i, "experience": "A player sees %s happen." % i, "oracle_proposed": "read %s" % i} for i in IDS]}
SHEET = "# Foo\n\n## his words\n- He said build it.\n\n## does\n" + "".join(
    "- [leaf:%s] the %s line\n" % (i, i) for i in IDS) + "\n## delegated\n- Tuning is delegated.\n"
SCEN = [{"id": "s%d" % n, "text": "situation %d" % n, "expect": "accept: ok", "expect_source": src,
         "by": "challenger" if n >= 9 else "examiner"} for n, src in
        enumerate(["leaf:l1", "l1", "leaf:l2", "leaf:l3", "leaf:l3", "leaf:l4", "leaf:l4", "leaf:l5", "leaf:l5",
                   "OWNER:123"], 1)]
# every Reader answer names the leaf it relied on (designer_exam.md step 4), so no scenario's reads is empty: s7 names
# its own source, s10 (sourced on his words) relied on l2
READS = {"s1": ["l1"], "s2": ["l1", "l2"], "s3": ["l2"], "s4": ["l3"], "s5": ["l3"], "s6": ["l4"], "s7": ["l4"],
         "s8": ["l5"], "s9": ["l5", "l1"], "s10": ["l2"]}
MAP_READERS = ["agent:a3333333333333333", "agent:a4444444444444444"]
ALL = sorted(s["id"] for s in SCEN)
MODE = {ER.NONE_TOUCHED: "none", ER.PARTIAL: "partial", ER.WHOLE: "whole", ER.CANNOT_RUN: "cannot_run"}


def _snapshot(d):
    out = {}
    for name in sorted(os.listdir(d)):
        p = os.path.join(d, name)
        if os.path.isfile(p):
            with open(p, "rb") as f:
                out[name] = hashlib.sha256(f.read()).hexdigest()
    return out


def _write_inputs(d, tree, sheet):
    with open(os.path.join(d, "tree.json"), "w", encoding="utf-8") as f:
        json.dump(tree, f, indent=1)
    p = os.path.join(d, "sheet.md")
    if isinstance(sheet, str):
        with open(p, "w", encoding="utf-8") as f:
            f.write(sheet)
    elif os.path.exists(p):
        os.unlink(p)


def map_dir(root, old_tree, old_sheet):
    """A concept folder whose exam passes on old_tree/old_sheet, with the read map recorded from the Readers' answers.
    -> (repo, dir, record). When the old tree or sheet cannot be read, no exam can pass and record is its error."""
    rd = tempfile.mkdtemp(prefix="map_", dir=root)
    d = os.path.join(rd, "design", "concepts", "Foo")
    os.makedirs(d)
    os.makedirs(os.path.join(rd, os.path.dirname(CT.OWNER_SHARD)))
    with open(os.path.join(rd, CT.OWNER_SHARD), "w", encoding="utf-8") as f:   # OWNER:123, the source of s10
        f.write(json.dumps({"tsn": "123", "seat": "OWNER", "text": "He said build it."}) + "\n")
    _write_inputs(d, old_tree, old_sheet)
    put(d, "scenes.json", {"scenes": [], "showcases": []})
    st = {"stage": 5, "status": "open", "results": [], "history": []}
    put(d, "stage.json", st)
    sc = copy.deepcopy(SCEN)
    # the first Reader names a scenario's first leaf, the second its last: the map is the union of the two
    rv = {r: {sid: {"verdict": "accept", "leaf": READS[sid][:1] if k == 0 else READS[sid][-1:]} for sid in READS}
          for k, r in enumerate(MAP_READERS)}
    ex = {"author": "rm-role-designer-1", "examiner": "agent:ade4a89b3cdad9f61", "challenger": "agent:a0123456789abcdef",
          "inputs": {k: DS.input_hash(d, k) for k in ("tree", "sheet")}, "scenarios": sc,
          "scenarios_hash": CT.sha(sc), "readers": list(MAP_READERS), "reader_verdicts": rv,
          "score": {"right": 10, "total": 10}, "accept_where_reject_core": 0, "challenger_misses": []}
    try:
        DS.exam_control(d, "l1")
        ex["control"] = {"broken_leaf": "l1", "missed": True, "missed_ids": ["s1"]}
    except DS.Refused:
        ex["control"] = None
    put(d, "exam.json", ex)
    readable = isinstance(old_tree, dict) and isinstance(old_sheet, str)
    if readable:
        errs = DS.exam_errors(ex, d, st, rd)
        if errs:
            raise AssertionError("fixture: the base exam does not pass its gate: %s" % errs)
    rec = ER.record(d, repo=rd)
    if readable and "error" in rec:
        raise AssertionError("fixture: no read map recorded: %s" % rec["error"])
    return rd, d, rec


def plan(new_tree=TREE, new_sheet=SHEET, old_tree=TREE, old_sheet=SHEET, scenarios=None, mutate=None, root=None):
    """The exam taken on old_*, its map recorded, the repair written as new_*, `mutate(d)` applied to the exam's
    records, then exam_retake.plan. -> the plan in the design's terms: {mode, retake, carry, touched_leaves, why};
    a whole plan retakes every scenario of the set in force, so its retake is that set. `pure` says whether plan()
    left every file of the folder as it found them."""
    try:
        rd, d, rec = map_dir(root, old_tree, old_sheet)
        _write_inputs(d, new_tree, new_sheet)
        if mutate:
            mutate(d)
        before = _snapshot(d)
        p = ER.plan(d, scenarios=scenarios, repo=rd)
        pure = _snapshot(d) == before
    except Exception as e:
        return {"mode": "CRASH %s: %s" % (type(e).__name__, e)}
    mode = MODE.get(p.get("outcome"), "unknown outcome %r" % p.get("outcome"))
    retake, carry = sorted(p["retake"]), sorted(p["carry"])
    if mode == "whole":
        if retake or carry:
            mode = "whole that still lists scenarios (retake %r, carry %r)" % (retake, carry)
        retake = sorted(CT.txt(s.get("id")) for s in (scenarios if scenarios is not None else SCEN))
    return {"mode": mode, "retake": retake, "carry": carry, "touched_leaves": sorted(p["changed"]), "why": p["why"],
            "pure": pure, "record": rec}


def edit(leaf, **fields):
    t = copy.deepcopy(TREE)
    for x in t["leaves"]:
        if x["id"] == leaf:
            x.update(fields)
    return t


def partial(name, p, retake, leaves=None):
    carry = sorted(set(ALL) - set(retake))
    ok = (isinstance(p, dict) and p.get("mode") == "partial" and p.get("retake") == sorted(retake)
          and p.get("carry") == carry and (leaves is None or p.get("touched_leaves") == sorted(leaves)))
    check(name, ok, p)


def whole(name, p, *words):
    ok = (isinstance(p, dict) and p.get("mode") == "whole" and p.get("retake") == ALL and p.get("carry") == []
          and all(w.lower() in str(p.get("why")).lower() for w in words))
    check(name, ok, p)


def none(name, p):
    ok = (isinstance(p, dict) and p.get("mode") == "none" and p.get("retake") == [] and p.get("carry") == ALL
          and p.get("touched_leaves") == [] and "looked" in str(p.get("why")).lower())
    check(name, ok, p)


def cannot_run(name, p, *words):
    ok = (isinstance(p, dict) and p.get("mode") == "cannot_run" and p.get("retake") == [] and p.get("carry") == []
          and all(w.lower() in str(p.get("why")).lower() for w in words))
    check(name, ok, p)


def _edit_json(d, name, fn):
    p = os.path.join(d, name)
    with open(p, encoding="utf-8") as f:
        obj = json.load(f)
    obj = fn(obj)
    with open(p, "w", encoding="utf-8") as f:
        json.dump(obj, f, indent=1)


def _map_scenarios(fn):
    def mutate(d):
        def m(rec):
            rec["scenarios"] = fn(rec["scenarios"])
            return rec
        _edit_json(d, ER.READS_FILE, m)
    return mutate


def _exam(fn):
    return lambda d: _edit_json(d, "exam.json", fn)


def map_cases(root):
    def P(*a, **kw):
        return plan(*a, root=root, **kw)
    # A1: a repair to some leaves re-runs exactly the scenarios that read them
    t = edit("l3", oracle_proposed="read l3 twice")
    partial("map: one leaf's test field changed: the scenarios that read it, no other", P(t), ["s4", "s5"], ["l3"])
    t2 = edit("l3", oracle_proposed="x")
    for x in t2["leaves"]:
        if x["id"] == "l4":
            x["experience"] = "A player sees l4 happen twice."
    partial("map: two leaves changed: 4 of 10 retaken, 6 carried", P(t2), ["s4", "s5", "s6", "s7"], ["l3", "l4"])
    partial("map: a scenario is retaken for a leaf a Reader relied on that is not its source (s2, s9 read l1)",
            P(edit("l1", experience="A player sees l1 stop.")), ["s1", "s2", "s9"], ["l1"])
    partial("map: a changed sheet line tagged to a leaf touches that leaf",
            P(new_sheet=SHEET.replace("- [leaf:l5] the l5 line", "- [leaf:l5] the l5 line, reworded")),
            ["s8", "s9"], ["l5"])
    partial("map: a removed sheet line tagged to a leaf touches that leaf",
            P(new_sheet=SHEET.replace("- [leaf:l2] the l2 line\n", "")), ["s10", "s2", "s3"], ["l2"])
    partial("map: an added sheet line tagged to a leaf touches that leaf",
            P(new_sheet=SHEET.replace("\n## delegated", "- [leaf:l2] and another l2 line\n\n## delegated")),
            ["s10", "s2", "s3"], ["l2"])
    # A4: looked, none touched
    none("map: nothing changed: looked, none touched", P())
    none("map: blank lines and line-end spaces in the sheet are not a change",
         P(new_sheet=SHEET.replace("## does\n", "## does   \n\n\n")))
    tc = copy.deepcopy(TREE)
    tc["coverage"] = {"signed_by": "CoverageJudge"}
    none("map: the coverage judge's own signature on the tree is not a change", P(tc))
    # A5: a scenario whose own text changed, or a new one, is run
    sc = copy.deepcopy(SCEN)
    sc[9]["text"] = "situation 10, reworded"
    partial("map: a reworded scenario is retaken though no leaf changed", P(scenarios=sc), ["s10"], [])
    sc2 = copy.deepcopy(SCEN) + [{"id": "s11", "text": "new", "expect": "reject: no", "expect_source": "leaf:l1",
                                  "by": "examiner"}]
    p = P(scenarios=sc2)
    check("map: a new scenario is run; the ten old ones are carried", isinstance(p, dict) and p.get("mode") == "partial"
          and p.get("retake") == ["s11"] and p.get("carry") == ALL, p)
    sc3 = [s for s in copy.deepcopy(SCEN) if s["id"] != "s6"]
    p = P(edit("l3", oracle_proposed="z"), scenarios=sc3)
    check("map: a dropped scenario is neither retaken nor carried", isinstance(p, dict) and p.get("mode") == "partial"
          and p.get("retake") == ["s4", "s5"] and "s6" not in (p.get("carry") or ["s6"]), p)
    # A2: the map cannot tell -> the whole exam
    ta = copy.deepcopy(TREE)
    ta["leaves"].append({"id": "l6", "experience": "A player sees l6."})
    whole("map: a leaf added: whole exam", P(ta), "l6")
    tr = copy.deepcopy(TREE)
    tr["leaves"] = [x for x in tr["leaves"] if x["id"] != "l2"]
    whole("map: a leaf removed: whole exam, naming the leaf", P(tr), "l2", "removed")
    tn = copy.deepcopy(TREE)
    tn["advisory"] = ["tune sooner"]
    whole("map: tree content outside the leaves changed: whole exam", P(tn), "tree's own fields")
    whole("map: a sheet line with no leaf tag changed: whole exam",
          P(new_sheet=SHEET.replace("- Tuning is delegated.", "- Tuning and pacing are delegated.")))
    whole("map: two leaves' sheet lines swapped, no text changed: the order every scenario reads moved, whole exam",
          P(new_sheet=SHEET.replace("- [leaf:l3] the l3 line\n- [leaf:l4] the l4 line",
                                    "- [leaf:l4] the l4 line\n- [leaf:l3] the l3 line")), "reordered")
    whole("map: a sheet line tagged to something that is not a leaf of the tree: whole exam",
          P(new_sheet=SHEET.replace("\n## delegated", "- [leaf:zz] a stray line\n\n## delegated")))
    # A3: a missing or unreadable map -> whole, and it says why
    whole("map: no read map recorded: whole exam, said as a missing read map",
          P(edit("l3", red="r"), mutate=lambda d: os.unlink(os.path.join(d, ER.READS_FILE))), "no read map")
    whole("map: a scenario with no entry in the map: whole exam",
          P(edit("l1", red="r"), mutate=_map_scenarios(lambda s: {k: v for k, v in s.items() if k != "s4"})),
          "disagrees")

    def add_l99(s):
        s["s1"]["reads"] = s["s1"]["reads"] + ["l99"]
        return s
    whole("map: a map naming a leaf the exam's tree lacks: whole exam", P(edit("l3", red="r"), mutate=_map_scenarios(
        add_l99)), "never hashed")
    for name, bad in (("a map whose scenarios is a list", []), ("a map whose scenarios is text", "l1")):
        whole("map: %s: whole exam" % name, P(edit("l3", red="r"), mutate=_map_scenarios(lambda s, b=bad: b)))
    whole("map: an exam taken on another tree than the map's: whole exam",
          P(edit("l3", red="r"), mutate=_exam(lambda e: dict(e, inputs=dict(e["inputs"], tree="0" * 64)))),
          "another exam")
    whole("map: an exam with no inputs.tree: whole exam",
          P(edit("l3", red="r"), mutate=_exam(lambda e: dict(e, inputs={}))))
    for name, kw in (("the old tree is None", {"old_tree": None}), ("the old sheet is None", {"old_sheet": None})):
        p = P(**kw)
        whole("map: %s: no map was recorded, so whole, never 'none touched'" % name, p, "no read map")
    # the fourth outcome: the current tree or sheet cannot be read, so no retake, partial or whole, can run
    for name, kw in (("the new tree is None", {"new_tree": None}), ("the new tree is a list", {"new_tree": []}),
                     ("the new sheet is None", {"new_sheet": None}),
                     ("the new tree's leaves is not a list", {"new_tree": dict(TREE, leaves={})})):
        cannot_run("map: %s: could not run, never 'none touched'" % name, P(**kw), "cannot run")
    p = P(mutate=_exam(lambda e: []))
    check("map: an exam that is not a dict is whole with nothing to carry, never 'none touched'",
          isinstance(p, dict) and p.get("mode") == "whole" and p.get("carry") == [], p)
    # plan() is a look: it writes nothing (write_plan records it)
    t0, s0 = copy.deepcopy(TREE), copy.deepcopy(SCEN)
    p = P(edit("l3", red="r"), scenarios=SCEN)
    check("map: the plan changes none of its inputs", isinstance(p, dict) and p.get("pure") is True and TREE == t0
          and SCEN == s0, p)


# ---------------------------------------------------------------- the stage machine: A1 to A6 of the item's criteria

LEAVES = ["l%d" % i for i in range(10)]
READERS = ["agent:a973694af5dc4757a", "agent:acddc523961c33401"]
FRESH = ["agent:a1111111111111111", "agent:a2222222222222222"]


def case(name, fn, root):
    try:
        fn(fixture(root, name))
        check(name, True)
    except Exception as e:                     # an exception is a failed case, named, never a crash of the run
        check(name, False, "%s: %s" % (type(e).__name__, e))


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


# ---------------------------------------------------------------- the six cases through the stage machine

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
    # the gate refuses the carried answers once two sheet lines no answer was retaken for are swapped
    put(d, "sheet.md", sheet(lambda t: t.replace("- [leaf:l1] l1 happens\n- [leaf:l2] l2 happens",
                                                 "- [leaf:l2] l2 happens\n- [leaf:l1] l1 happens")))
    errs = DS.exam_errors(read(d, "exam.json"), d, read(d, "stage.json"), rd)
    need(any("carried" in e and "reordered" in e for e in errs), "a reordered sheet keeps the carried answers: %s" % errs)


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
    # a sheet edit no unit sees (trailing spaces) still moves the sheet hash the gate checks: none touched, yet the
    # standing exam fails its gate until `carry --fresh {}` restamps its inputs, and the plan says so
    p_sh = os.path.join(d, "sheet.md")
    lines = open(p_sh).read().split("\n")
    k = next(i for i, ln in enumerate(lines) if ln.strip())
    lines[k] += "   "
    open(p_sh, "w").write("\n".join(lines))
    p = ER.plan(d, repo=rd)
    need(p["outcome"] == ER.NONE_TOUCHED, "whitespace edit: outcome %r: %s" % (p["outcome"], p.get("why")))
    need("carry" in p["why"] and "--fresh" in p["why"], "the none-touched plan does not name the restamp: %r" % p["why"])
    st = read(d, "stage.json")
    need(any("another sheet" in e for e in DS.exam_errors(read(d, "exam.json"), d, st, rd)),
         "the stale sheet hash is not refused by the gate")
    f = os.path.join(d, "fresh_empty.json")
    open(f, "w").write("{}")
    ER.carry(d, f, repo=rd)
    errs = DS.exam_errors(read(d, "exam.json"), d, st, rd)
    need(errs == [], "carry --fresh {} did not restamp a none-touched exam: %s" % errs)


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
        map_cases(root)
        for name, fn in (("A1: two touched of ten are re-run, eight carried and marked", a1),
                         ("A2: an unread leaf, an every-read leaf, his words or a new leaf retakes the whole exam", a2),
                         ("A3: a missing or unreadable map retakes the whole exam, never 'nothing touched'", a3),
                         ("A4: nothing a scenario read changed: zero re-run, recorded as looked, none touched", a4),
                         ("A5: a scenario whose text changed is re-run, not carried", a5),
                         ("A6: the coverage judge still never looks at a tree whose exam has not passed", a6)):
            case(name, fn, root)
    finally:
        shutil.rmtree(root, ignore_errors=True)
    n = len(FAILS)
    print("%s: %d of %d checks pass" % ("FAIL" if n else "PASS", RUN[0] - n, RUN[0]))
    return 1 if n else 0


if __name__ == "__main__":
    sys.exit(main())
