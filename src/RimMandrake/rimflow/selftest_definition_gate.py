#!/usr/bin/env python3
"""Selftest of the six-part definition gate in concept_tree.py (item RIMMANDRAKE_TOUGHEN_DESIGNER_ENTRY_GATE_VAGUE_
BUILDS_CHOKED). Page: design/specs/2026-11-26-six-part-definition-gate/boundary.md; each promise is a test of its own
name. Temp folders only; the repo's concepts are read by the acceptance test, not here."""
import copy
import json
import os
import shutil
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
os.environ.setdefault("RM_UNDER_SELFTEST", "1")
import concept_tree as CT  # noqa: E402
import selftest_concept_tree as SCT  # noqa: E402

FAILS = []
TMP = tempfile.mkdtemp(prefix="definition_gate_")


def check(ok, msg, got=None):
    print("%s %s%s" % ("ok  " if ok else "FAIL", msg, "" if ok or got is None else "  got: %s" % (got,)))
    if not ok:
        FAILS.append(msg)


def bar(bid, says, touches, **kw):
    b = {"id": bid, "says": says,
         "meant": {"intent": "the colony can live on the dunes", "source": "delegated: from the fixture",
                   "figurative": [{"word": "glow", "stands_for": "a visible light at play zoom",
                                   "accept": "a soft halo the player notices"}]},
         "accept": ["the player sees the lamp lit at dusk", "a colonist reads by its light at night"],
         "reject": ["the lamp is drawn but gives no light", "only the log says the lamp is lit"],
         "lazy": "the lamp is drawn but gives no light",
         "range": {"varies": "dusk and night, roofed and open", "left_out": "a map with no lamps"},
         "sees": {"instrument": "a bridge read of the cell's light", "start": "a fresh quicktest map",
                  "on": "every mechanic of the mod on", "control": "the same cell with the lamp unbuilt",
                  "reset": "discard the map"},
         "touches": touches, "live_only": False}
    b.update(kw)
    return b


def draft():
    return {"subject": "Demo", "kind": "mod", "root_ref": None,
            "leaves": [bar("lamp_glows", "A player sees the lamp glow at night.", ["lamp light"]),
                       bar("whole", "A player runs the whole colony through a season, with a reload mid-way and the "
                           "main work done in another order, and the lamps still light it.", ["lamp light"])],
            "whole": "whole", "checks": [], "rules": [],
            "meetings": [{"thing": "lamp light", "members": ["lamp_glows", "whole"], "holds_together": "argued",
                          "why": "both read the same light, and the whole bar only adds time"}]}


SHEET = "# Demo\n\n## his words\n\n- the fixture's words\n\n## does\n\n- [leaf:lamp_glows] the lamp glows\n" \
        "- [leaf:whole] the whole colony runs\n"


def concept(name, d_=None, sheet=SHEET):
    """A concept folder under TMP with the sheet and a tree written from the draft (through `write`)."""
    d = os.path.join(TMP, name)
    shutil.rmtree(d, ignore_errors=True)
    os.makedirs(d)
    with open(os.path.join(d, "sheet.md"), "w", encoding="utf-8") as f:
        f.write(sheet)
    errs = CT.write(d, d_ if d_ is not None else draft())
    return d, errs


def lint(d):
    return CT.lint(d)[0]


def edited(name, edit):
    """The good tree, edited in place after the write, then linted: the refusals that start `definition:`."""
    d, errs = concept(name)
    assert not errs, errs
    with open(os.path.join(d, "tree.json"), encoding="utf-8") as f:
        t = json.load(f)
    edit(t)
    with open(os.path.join(d, "tree.json"), "w", encoding="utf-8") as f:
        json.dump(t, f)
    return [e for e in lint(d) if e.startswith(CT.DEF)]


def first(t):
    return t["leaves"][0]


def t_six_part_tree_passes():
    d, errs = concept("good")
    check(not errs, "write takes a six-part draft", errs)
    check(not lint(d), "the six-part tree lints with no refusal", lint(d))
    check(CT.six_part(CT.load(d)), "the tree reads as six-part")


def t_every_part_is_required():
    for name, edit, want in (
            ("no_figurative", lambda t: first(t)["meant"].pop("figurative"), "meant.figurative"),
            ("no_range", lambda t: first(t).pop("range"), "range"),
            ("sees_control", lambda t: first(t)["sees"].update(control=""), "sees.control"),
            ("one_accept", lambda t: first(t).update(accept=[]), "accept"),
            ("lazy", lambda t: first(t).update(lazy="a build nobody pictured"), "lazy")):
        errs = edited(name, edit)
        check(any(want in e for e in errs), "a bar with no %s is refused, naming it" % want, errs[:3])
    for name, edit, want in (("id_list", lambda t: first(t).update(id=["a"]), "id"),
                             ("whole_text", lambda t: first(t).update(whole="yes"), "whole")):
        try:
            errs = edited(name, edit)
        except Exception as e:  # noqa: BLE001 - a crash is the failure this check catches
            errs = ["CRASH %s: %s" % (type(e).__name__, e)]
        check(any(want in e for e in errs) and not any(e.startswith("CRASH") for e in errs),
              "a malformed %s is refused, not a crash" % name, errs[:2])


def t_no_number_in_a_bar():
    errs = edited("number", lambda t: first(t).update(says="A player sees the lamp glow in 30% of nights."))
    check(any("pins a number" in e and "says" in e for e in errs), "a percentage in says is refused", errs[:3])
    errs = edited("number_reject", lambda t: first(t)["reject"].append("the lamp lights 3 cells"))
    check(any("pins a number" in e and "reject" in e for e in errs), "a digit in a reject picture is refused", errs[:3])


def t_one_whole_bar():
    errs = edited("no_whole", lambda t: t.update(whole="nothing_here"))
    check(any("whole" in e for e in errs), "a tree with no whole bar is refused", errs[:3])
    errs = edited("whole_no_reload", lambda t: t["leaves"][1].update(
        says="A player runs the colony through a season, with the main work done in another order."))
    check(any("lacks the reload" in e for e in errs), "a whole bar with no reload is refused, naming it", errs[:3])
    errs = edited("whole_no_order", lambda t: t["leaves"][1].update(
        says="A player runs the colony through a season, with a reload mid-way, and the lamps light it."))
    check(any("lacks the second order" in e for e in errs), "a whole bar with no second order is refused", errs[:3])
    plain = "A player runs the whole colony through a season, and the lamps light it."
    errs = edited("whole_words_in_reset", lambda t: (t["leaves"][1].update(says=plain), t["leaves"][1]["sees"].update(
        reset="reload the pre-test save"), t["leaves"][1]["range"].update(left_out="a changed order of the main work")))
    check(any("lacks the reload" in e for e in errs) and any("lacks the second order" in e for e in errs),
          "a reload in the reset step and an order in left_out do not make the whole bar", errs[:3])
    errs = edited("whole_negated", lambda t: t["leaves"][1].update(
        says="A player runs the colony with no reload, building a different base in order to see the lamps."))
    check(any("lacks the reload" in e for e in errs) and any("lacks the second order" in e for e in errs),
          "'no reload' and 'in order to' do not make the whole bar", errs[:3])


def t_shared_thing_has_a_meeting():
    errs = edited("no_meeting", lambda t: t.update(meetings=[]))
    check(any("lamp light" in e and "meeting" in e for e in errs), "a shared thing with no meeting is refused", errs[:3])


def t_one_kind_of_leaf():
    errs = edited("mixed", lambda t: t["leaves"].append(copy.deepcopy(SCT.leaf("old_one"))))
    check(any("old_one" in e and "six-part" in e for e in errs), "a leaf of the old kind in a six-part tree is refused",
          errs[:3])


def t_sheet_maps_every_bar():
    d, errs = concept("off_sheet", sheet=SHEET.replace("- [leaf:whole] the whole colony runs\n", ""))
    got = [e for e in lint(d) if e.startswith(CT.DEF)]
    check(any("whole is on no `## does` line" in e for e in got), "a bar on no does line is refused", got[:3])
    d, errs = concept("core_open", sheet=SHEET + "\n## open\n\n- [core] is the lamp a building?\n")
    got = [e for e in lint(d) if e.startswith(CT.DEF)]
    check(any("[core] line is still open" in e for e in got), "an open [core] line is refused", got[:3])


def t_new_mod_draft_is_six_part():
    old = SCT.draft()
    d = os.path.join(TMP, "old_kind")
    os.makedirs(d, exist_ok=True)
    errs = CT.write(d, copy.deepcopy(old), SCT_REPO)
    check(any(e.startswith(CT.DEF) and "six-part" in e for e in errs), "write refuses a mod draft of the old kind",
          errs[:2])
    check(not os.path.exists(os.path.join(d, "tree.json")), "and writes nothing")
    check(CT.write(d, copy.deepcopy(old), SCT_REPO, legacy=True) == [], "legacy=True still writes the old kind")
    d, errs = concept("new_six")
    check(not errs and not lint(d), "a six-part draft is written and lints clean", errs or lint(d))


def t_old_tree_unchanged():
    got = [e for e in CT.lint(SCT_D, SCT_REPO)[0]]
    check(not got, "a good tree of the old kind lints with no refusal", got[:3])


def main():
    global SCT_REPO, SCT_D
    SCT_REPO, SCT_D = SCT.stage(TMP)
    SCT.validate_walk(SCT_REPO)
    assert CT.write(SCT_D, SCT.draft(), SCT_REPO, legacy=True) == []
    try:
        t_six_part_tree_passes()
        t_every_part_is_required()
        t_no_number_in_a_bar()
        t_one_whole_bar()
        t_shared_thing_has_a_meeting()
        t_one_kind_of_leaf()
        t_sheet_maps_every_bar()
        t_new_mod_draft_is_six_part()
        t_old_tree_unchanged()
    finally:
        shutil.rmtree(TMP, ignore_errors=True)
    print("%s: %d failed" % ("PASS" if not FAILS else "FAIL", len(FAILS)))
    return 1 if FAILS else 0


SCT_REPO = SCT_D = None

if __name__ == "__main__":
    sys.exit(main())
