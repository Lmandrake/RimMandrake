#!/usr/bin/env python3
"""Acceptance for the MAP in RIMMANDRAKE_RETAKE_ONLY_TOUCHED_EXAM_SCENARIOS_CARD_ASKED_TWICE (DESIGN DECISION 2026-11-18
on that item; his card of 2026-11-18, "Retake only what changed"). The map's unit is the LEAF, not the file: every
Reader is handed the whole tree.json and sheet.md, so a file-level map would call every repair "touches everything".

  designer_stage.exam_retake_plan(old_tree, new_tree, old_sheet, new_sheet, exam, scenarios=None) -> dict, pure:
    mode            "none" (looked, none touched) | "partial" | "whole" (the map cannot tell)
    retake, carry   sorted scenario ids; whole = every scenario retaken, none carried
    touched_leaves  sorted leaf ids the repair changed
    why             plain words; for "whole", the reason the map could not tell
  old_tree/old_sheet: what the exam was taken on. new_*: after the repair. Sheets are text.
  exam["reads"] = {scenario id: [leaf ids its Readers said they relied on]}, written when the exam is scored; a
  scenario's `expect_source` leaf always counts as read too.
  A leaf is touched when concept_tree.leaf_hash differs, or a sheet line tagged `[leaf:<id>]` was added, removed or
  changed. A scenario is retaken when it read a touched leaf, or its own text is new or changed (`scenarios`).
  WHOLE, never a guess: a leaf added or removed; any tree content outside `leaves` (and outside `coverage`) changed;
  a sheet line with no leaf tag changed; `reads` missing, lacking a scenario, or naming a leaf the old tree lacks; a
  tree, sheet or exam that is not readable (None or the wrong type); the exam's inputs.tree is not old_tree's hash.
  Blank lines and line-end spaces in the sheet are not a change. Files a Reader never sees (scenes.json, record.json,
  floor) are not inputs: a repair to them alone is mode "none".
Red on b4c47bd15 (watched)."""
import copy
import os
import sys

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, HERE)
import concept_tree as CT  # noqa: E402
import designer_stage as DS  # noqa: E402

FAILS = []
IDS = ["l%d" % i for i in range(1, 6)]
TREE = {"subject": "Foo", "root_ref": "x", "advisory": ["tune later"],
        "leaves": [{"id": i, "experience": "A player sees %s happen." % i, "oracle_proposed": "read %s" % i} for i in IDS]}
SHEET = "# Foo\n\n## his words\n- He said build it.\n\n## does\n" + "".join(
    "- [leaf:%s] the %s line\n" % (i, i) for i in IDS) + "\n## delegated\n- Tuning is delegated.\n"
SCEN = [{"id": "s%d" % n, "text": "situation %d" % n, "expect": "accept: ok", "expect_source": src} for n, src in
        enumerate(["leaf:l1", "l1", "leaf:l2", "leaf:l3", "leaf:l3", "leaf:l4", "leaf:l4", "leaf:l5", "leaf:l5",
                   "OWNER:123"], 1)]
READS = {"s1": ["l1"], "s2": ["l1", "l2"], "s3": ["l2"], "s4": ["l3"], "s5": ["l3"], "s6": ["l4"], "s7": [],
         "s8": ["l5"], "s9": ["l5", "l1"], "s10": []}
ALL = sorted(s["id"] for s in SCEN)


def check(name, ok, got=""):
    print("%s %s%s" % ("ok  " if ok else "FAIL", name, "" if ok else "  got: %s" % (got,)))
    if not ok:
        FAILS.append(name)


def exam(**over):
    e = {"inputs": {"tree": CT.tree_hash(TREE)}, "scenarios": copy.deepcopy(SCEN), "reads": copy.deepcopy(READS)}
    e.update(over)
    return e


def plan(new_tree=TREE, new_sheet=SHEET, ex=None, old_tree=TREE, old_sheet=SHEET, **kw):
    fn = getattr(DS, "exam_retake_plan", None)
    if not callable(fn):
        return {"mode": "no exam_retake_plan"}
    try:
        return fn(old_tree, new_tree, old_sheet, new_sheet, exam() if ex is None else ex, **kw)
    except Exception as e:
        return {"mode": "CRASH %s: %s" % (type(e).__name__, e)}


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
          and p.get("touched_leaves") == [] and "none touched" in str(p.get("why")).lower())
    check(name, ok, p)


def main():
    # A1: a repair to two leaves re-runs exactly the scenarios that read them
    t = edit("l3", oracle_proposed="read l3 twice")
    partial("one leaf's test field changed: the scenarios that read it, no other", plan(t), ["s4", "s5"], ["l3"])
    t2 = edit("l3", oracle_proposed="x")
    for x in t2["leaves"]:
        if x["id"] == "l4":
            x["experience"] = "A player sees l4 happen twice."
    partial("two leaves changed: 4 of 10 retaken, 6 carried", plan(t2), ["s4", "s5", "s6", "s7"], ["l3", "l4"])
    partial("a scenario is retaken for a leaf a Reader relied on that is not its source (s2, s9 read l1)",
            plan(edit("l1", experience="A player sees l1 stop.")), ["s1", "s2", "s9"], ["l1"])
    partial("a scenario with empty reads is still tied to its expect_source (s7 -> l4)",
            plan(edit("l4", oracle_proposed="y")), ["s6", "s7"], ["l4"])
    partial("a changed sheet line tagged to a leaf touches that leaf",
            plan(new_sheet=SHEET.replace("- [leaf:l5] the l5 line", "- [leaf:l5] the l5 line, reworded")),
            ["s8", "s9"], ["l5"])
    partial("a removed sheet line tagged to a leaf touches that leaf",
            plan(new_sheet=SHEET.replace("- [leaf:l2] the l2 line\n", "")), ["s2", "s3"], ["l2"])
    partial("an added sheet line tagged to a leaf touches that leaf",
            plan(new_sheet=SHEET.replace("\n## delegated", "- [leaf:l2] and another l2 line\n\n## delegated")),
            ["s2", "s3"], ["l2"])
    # A4: looked, none touched
    none("nothing changed: none touched", plan())
    none("blank lines and line-end spaces in the sheet are not a change",
         plan(new_sheet=SHEET.replace("## does\n", "## does   \n\n\n")))
    tc = copy.deepcopy(TREE)
    tc["coverage"] = {"signed_by": "CoverageJudge"}
    none("the coverage judge's own signature on the tree is not a change", plan(tc))
    # A5: a scenario whose own text changed, or a new one, is run
    sc = copy.deepcopy(SCEN)
    sc[9]["text"] = "situation 10, reworded"
    partial("a reworded scenario is retaken though no leaf changed", plan(scenarios=sc), ["s10"], [])
    sc2 = copy.deepcopy(SCEN) + [{"id": "s11", "text": "new", "expect": "reject: no", "expect_source": "leaf:l1"}]
    p = plan(scenarios=sc2)
    check("a new scenario is run; the ten old ones are carried", isinstance(p, dict) and p.get("mode") == "partial"
          and p.get("retake") == ["s11"] and p.get("carry") == ALL, p)
    sc3 = [s for s in copy.deepcopy(SCEN) if s["id"] != "s6"]
    p = plan(edit("l3", oracle_proposed="z"), scenarios=sc3)
    check("a dropped scenario is neither retaken nor carried", isinstance(p, dict) and p.get("mode") == "partial"
          and p.get("retake") == ["s4", "s5"] and "s6" not in (p.get("carry") or ["s6"]), p)
    # A2: the map cannot tell -> the whole exam
    ta = copy.deepcopy(TREE)
    ta["leaves"].append({"id": "l6", "experience": "A player sees l6."})
    whole("a leaf added: whole exam", plan(ta), "l6")
    tr = copy.deepcopy(TREE)
    tr["leaves"] = [x for x in tr["leaves"] if x["id"] != "l2"]
    whole("a leaf removed: whole exam", plan(tr), "l2")
    tn = copy.deepcopy(TREE)
    tn["advisory"] = ["tune sooner"]
    whole("tree content outside the leaves changed: whole exam", plan(tn), "advisory")
    whole("a sheet line with no leaf tag changed: whole exam",
          plan(new_sheet=SHEET.replace("- Tuning is delegated.", "- Tuning and pacing are delegated.")))
    whole("a sheet line tagged to something that is not a leaf of the tree: whole exam",
          plan(new_sheet=SHEET.replace("\n## delegated", "- [leaf:zz] a stray line\n\n## delegated")))
    # A3: a missing or unreadable map -> whole, and it says why
    e = exam()
    del e["reads"]
    whole("no reads record in the exam: whole exam, said as a missing read record", plan(edit("l3", red="r"), ex=e),
          "read")
    e = exam()
    del e["reads"]["s4"]
    whole("a scenario with no entry in reads: whole exam", plan(edit("l1", red="r"), ex=e), "s4")
    e = exam()
    e["reads"]["s1"] = ["l1", "l99"]
    whole("reads naming a leaf the exam's tree lacks: whole exam", plan(edit("l3", red="r"), ex=e), "l99")
    for name, bad in (("reads that is a list", []), ("reads that is text", "l1")):
        whole("%s: whole exam" % name, plan(edit("l3", red="r"), ex=exam(reads=bad)))
    whole("an exam taken on another tree than old_tree: whole exam",
          plan(edit("l3", red="r"), ex=exam(inputs={"tree": "0" * 64})), "tree")
    whole("an exam with no inputs.tree: whole exam", plan(edit("l3", red="r"), ex=exam(inputs={})))
    for name, kw in (("the new tree is None", {"new_tree": None}), ("the old tree is None", {"old_tree": None}),
                     ("the new tree is a list", {"new_tree": []}), ("the new sheet is None", {"new_sheet": None}),
                     ("the old sheet is None", {"old_sheet": None}),
                     ("the new tree's leaves is not a list", {"new_tree": dict(TREE, leaves={})})):
        p = plan(**kw)
        whole("%s: whole exam, never 'none touched'" % name, p)
    p = plan(ex=[])
    check("an exam that is not a dict is whole with nothing to carry, never 'none touched'",
          isinstance(p, dict) and p.get("mode") == "whole" and p.get("carry") == [], p)
    # the function is pure
    t0, s0, e0 = copy.deepcopy(TREE), SHEET, exam()
    e1 = copy.deepcopy(e0)
    plan(edit("l3", red="r"), ex=e1)
    check("the plan changes none of its inputs", TREE == t0 and e1 == e0)
    print("%s: %d failure(s)" % ("FAIL" if FAILS else "PASS", len(FAILS)))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
