#!/usr/bin/env python3
"""Acceptance for RIMMANDRAKE_GUARD_CONTROL_COPY_RETAINED_RULES_ONE_WORD_REVERSES (parent finding 5), under the DESIGN
DECISION of 2026-11-18 on that item: nobody edits the exam's control copy by hand. A paraphrase of the removed leaf's
rule is stripped by the program, `exam_control(d, leaf, strip=[phrase, ...])` (CLI: `exam-control <dir> --leaf <id>
--strip "<phrase>"`, repeatable), in whole units only: every sheet.md line holding the phrase is dropped, every list
entry holding it is dropped, every other string value holding it becomes exactly "(removed)" (case and spacing aside);
a phrase found in a retained leaf's `id` or `experience` is refused. copy.json records the phrases under "strip", and
control_copy_errors regenerates the copy from the current tree plus that list and refuses any difference, so a hand
edit that reverses a retained rule ("must not climb" -> "must climb") cannot pass.
Red on base 25d20f71e0 and on b28e0d697 (watched)."""
import json
import os
import shutil
import sys
import tempfile

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, HERE)
import designer_stage as DS  # noqa: E402

FAILS = []
LEAF = "l_flood"
TREE = {"root": "a pit you climb out of",
        "advisory": ["Rain filling the pit is tuned later.", "Ladders are cheap."],
        "summary": "A pit. Rain filling the pit is its hazard.",
        "leaves": [
            {"id": "l_climb", "rule": "Pawns must not climb the north wall.",
             "experience": "A player sees pawns refuse the north wall.",
             "tier_reason": "Needs a live map; rain filling the pit is read there too.",
             "false_pass": ["The wall is absent", "Rain filling the pit hides the wall"]},
            {"id": "l_ladder", "rule": "A ladder lets a pawn climb out.",
             "experience": "A player sees a pawn leave by ladder.", "tier_reason": "Offline.", "false_pass": []},
            {"id": "l_flood", "rule": "The pit floods in rain.", "experience": "A player sees the pit flood in rain.",
             "tier_reason": "Live.", "false_pass": []}]}
SHEET = ("# Foo\n## does\n- [leaf:l_climb] no north wall\n- [leaf:l_ladder] ladder\n- [leaf:l_flood] flood\n"
         "## delegated\n- Rain  Filling the pit is checked by the weather seat.\n- Ladder cost is delegated.\n")
IDS = [x["id"] for x in TREE["leaves"]]
PHRASE = "rain filling the pit"


def check(name, ok, got=""):
    print("%s %s%s" % ("ok  " if ok else "FAIL", name, "" if ok else "  got: %s" % (got,)))
    if not ok:
        FAILS.append(name)


def fresh(tmp, name):
    d = os.path.join(tmp, name, "Foo")
    os.makedirs(d)
    with open(os.path.join(d, "tree.json"), "w") as f:
        json.dump(TREE, f)
    with open(os.path.join(d, "sheet.md"), "w") as f:
        f.write(SHEET)
    return d


def errors(d):
    try:
        return DS.control_copy_errors(d, LEAF, IDS)
    except Exception as e:      # a crash is not a refusal
        return "CRASH %s: %s" % (type(e).__name__, e)


def strip_copy(d, phrases):
    """-> (copy.json record, None) or (None, why): `why` is "Refused: ..." for a refusal, anything else is a defect."""
    try:
        return DS.exam_control(d, LEAF, strip=phrases), None
    except DS.Refused as e:
        return None, "Refused: %s" % e
    except Exception as e:
        return None, "%s: %s" % (type(e).__name__, e)


def control(d, name):
    with open(os.path.join(d, DS.CONTROL_DIR, name)) as f:
        return f.read()


def rewrite_tree(d, fn):
    p = os.path.join(d, DS.CONTROL_DIR, "tree.json")
    with open(p) as f:
        t = json.load(f)
    fn(t)
    with open(p, "w") as f:
        json.dump(t, f, indent=1, ensure_ascii=False)
        f.write("\n")


def leaf_of(t, lid):
    return [x for x in t["leaves"] if x["id"] == lid][0]


def main():
    tmp = tempfile.mkdtemp(prefix="control_copy_accept_")
    try:
        # 1. no strip: the generated copy passes; every hand edit of it is refused
        d = fresh(tmp, "plain")
        try:
            DS.exam_control(d, LEAF)
        except DS.Refused as e:
            print("UNMEASURED: exam-control refused on the fixture: %s" % e)
            return 2
        check("the generated copy passes", errors(d) == [], errors(d))
        rewrite_tree(d, lambda t: leaf_of(t, "l_climb").update(rule="Pawns must climb the north wall."))
        e = errors(d)
        check("a retained leaf's rule reversed by hand is refused", isinstance(e, list) and bool(e), e)

        d = fresh(tmp, "handsheet")
        DS.exam_control(d, LEAF)
        p = os.path.join(d, DS.CONTROL_DIR, "sheet.md")
        with open(p, "w") as f:
            f.write(control(d, "sheet.md").replace("- Ladder cost is delegated.\n", ""))
        e = errors(d)
        check("a sheet line deleted by hand is refused", isinstance(e, list) and bool(e), e)

        d = fresh(tmp, "handword")
        DS.exam_control(d, LEAF)
        with open(p.replace("handsheet", "handword"), "w") as f:
            f.write(control(d, "sheet.md").replace("no north wall", "north wall"))
        e = errors(d)
        check("one word deleted by hand from a sheet line is refused", isinstance(e, list) and bool(e), e)

        d = fresh(tmp, "handnonleaf")
        DS.exam_control(d, LEAF)
        rewrite_tree(d, lambda t: t.update(summary="A pit."))
        e = errors(d)
        check("a non-leaf tree value edited by hand is refused", isinstance(e, list) and bool(e), e)

        d = fresh(tmp, "handlist")
        DS.exam_control(d, LEAF)
        rewrite_tree(d, lambda t: t.update(advisory=t["advisory"][:1]))
        e = errors(d)
        check("a list entry dropped by hand is refused", isinstance(e, list) and bool(e), e)

        # 2. the program strips a paraphrase in whole units, records it, and that copy passes
        d = fresh(tmp, "strip")
        rec, why = strip_copy(d, [PHRASE])
        check("exam_control takes strip=[phrase]", rec is not None, why)
        if rec is not None:
            t = json.loads(control(d, "tree.json"))
            sheet = control(d, "sheet.md")
            check("copy.json records the phrase", json.loads(control(d, "copy.json")).get("strip") == [PHRASE],
                  control(d, "copy.json"))
            check("the sheet line holding the phrase is gone, spacing and case aside",
                  "weather seat" not in sheet and "Ladder cost is delegated." in sheet, sheet)
            check("the list entry holding the phrase is dropped", t.get("advisory") == ["Ladders are cheap."],
                  t.get("advisory"))
            check("a non-leaf string holding the phrase is exactly (removed)", t.get("summary") == "(removed)",
                  t.get("summary"))
            lc = leaf_of(t, "l_climb")
            check("a retained leaf's other field holding the phrase is exactly (removed)",
                  lc.get("tier_reason") == "(removed)", lc.get("tier_reason"))
            check("a retained leaf's list entry holding the phrase is dropped",
                  lc.get("false_pass") == ["The wall is absent"], lc.get("false_pass"))
            check("the retained rule and experience are untouched",
                  lc.get("rule") == TREE["leaves"][0]["rule"] and lc.get("experience") == TREE["leaves"][0]["experience"],
                  lc)
            check("the stripped copy passes", errors(d) == [], errors(d))
            rewrite_tree(d, lambda t: leaf_of(t, "l_climb").update(rule="Pawns must climb the north wall."))
            e = errors(d)
            check("a stripped copy with a retained rule reversed by hand is refused", isinstance(e, list) and bool(e), e)

        d = fresh(tmp, "striprec")
        rec, why = strip_copy(d, [PHRASE])
        if rec is not None:
            cp = os.path.join(d, DS.CONTROL_DIR, "copy.json")
            r = json.loads(control(d, "copy.json"))
            r["strip"] = []
            with open(cp, "w") as f:
                json.dump(r, f)
            e = errors(d)
            check("a strip the record no longer names is refused", isinstance(e, list) and bool(e), e)
        else:
            check("a strip the record no longer names is refused", False, why)

        # 3. strips the program must refuse
        for name, phrases in (("a phrase found in a retained leaf's experience", ["refuse the north wall"]),
                              ("a phrase found in a retained leaf's id", ["l_ladder"]),
                              ("an empty phrase", [""]), ("a blank phrase", ["   "]), ("a phrase that is not text", [7])):
            d = fresh(tmp, "refuse_%d" % len(name))
            rec, why = strip_copy(d, phrases)
            check("%s is refused" % name, rec is None and (why or "").startswith("Refused:"), why or rec)

        # 4. a phrase that matches nothing strips nothing and still passes
        d = fresh(tmp, "nomatch")
        rec, why = strip_copy(d, ["zebra crossing"])
        check("a phrase found nowhere leaves the generated copy, and it passes",
              rec is not None and errors(d) == [] and "Ladder cost is delegated." in control(d, "sheet.md"),
              why or errors(d))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    print("%s: %d failure(s)" % ("FAIL" if FAILS else "PASS", len(FAILS)))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
