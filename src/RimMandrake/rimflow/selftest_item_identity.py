#!/usr/bin/env python3
"""The mod that an item names has one home (design/specs/2026-11-22-item-identity/boundary.md).

Item RIMMANDRAKE_GENERALIZE_PIPELINE_REPAIRS_INTO_FEW_PRINCIPLES, principle 2. The cases are the shapes on which the
three old readers disagreed on the 2026-11-22 ledger: a word of the mod's name (IMPERIAL), its initials (GSS), an
alias (HOSE), a title only, a tie.

    python3 src/RimMandrake/rimflow/selftest_item_identity.py        exit 0 all pass, 1 a promise is broken
"""
import importlib
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
UTILS = os.path.join(HERE, "..", "Utils")
sys.path[:0] = [HERE, UTILS]

MODS = ["GraffitiImperial", "GimmeSomeSlack", "FlowWorks", "Cauldron", "Pyrelands", "PyrelandsMechanics",
        "ExplosiveKnockback", "MandrakePatches"]
# (id, title, the one answer)
CASES = [
    ("IMPERIAL_CAST_BINDING_1", "", "GraffitiImperial"),
    ("RIMMANDRAKE_PROVE_GSS_SWITCHBOARD", "", "GimmeSomeSlack"),
    ("HOSE_LEAK_TWIST", "t", "FlowWorks"),
    ("FW_PUMP_DRAW", "", "FlowWorks"),
    ("FLOW_WORKS_PUMP_1", "", "FlowWorks"),
    ("ODD_THING_ONE", "Cauldron soup broken", "Cauldron"),
    ("RIMMANDRAKE_LAY_SLACK_X", "Gimme Some Slack: the 21 close-fitting poses", "GimmeSomeSlack"),
    ("PYRELANDS_FINISH", "", "Pyrelands"),
    ("RIMMANDRAKE_DESIGN_KNOCKBACK_FIRST_TOUCH", "", "ExplosiveKnockback"),
    ("ALPHA_FIX_ONE", "t", None),
    ("RIMMANDRAKE_ANSWER_HIS_CARD", "Needs Mandrake: answer the patches card", None),
    ("RIMMANDRAKE_FIX_PATCHES_LOAD", "", "MandrakePatches"),
]
READERS = ("maturation_now", "rimflow_metrics", "fleet_mods")


def _one():
    try:
        return importlib.import_module("item_identity")
    except ImportError as e:
        return e


def t_one_answer():
    one, bad = _one(), []
    if isinstance(one, Exception):
        return ["rimflow/item_identity.py is missing (%s)" % one]
    for name in READERS:
        mod = importlib.import_module(name)
        if getattr(mod, "item_mod", None) is not one.item_mod:
            bad.append("%s does not ask item_identity.item_mod" % name)
    for f in ("mod_by_name",):
        if hasattr(importlib.import_module("fleet_mods"), f):
            bad.append("fleet_mods still has its own %s" % f)
    return bad


def t_id_before_title():
    one = _one()
    if isinstance(one, Exception):
        return ["rimflow/item_identity.py is missing"]
    bad = ["%s (title %r) -> %r, not %r" % (i, t, one.item_mod(i, MODS, t), want)
           for i, t, want in CASES if one.item_mod(i, MODS, t) != want]
    if one.item_mod("PYRELANDS_FINISH", MODS, "Cauldron soup") != "Pyrelands":
        bad.append("a title overrode the id")
    if one.item_mod("RIMMANDRAKE_LAY_SLACK_X", MODS) is not None:
        bad.append("an id that names no mod, with no title, named one")
    return bad


def t_a_tie_names_none():
    one = _one()
    if isinstance(one, Exception):
        return ["rimflow/item_identity.py is missing"]
    got = one.item_mod("RIMMANDRAKE_FIX_IT", ["AlphaBetaGamma", "AlphaBetaGrove"], "ABG broke")
    return [] if got is None else ["two mods with the initials ABG gave %r" % got]


def t_one_alias_table():
    one = _one()
    if isinstance(one, Exception):
        return ["rimflow/item_identity.py is missing"]
    bad = [] if one.ALIASES.get("HOSE") == "FlowWorks" else ["ALIASES lacks HOSE -> FlowWorks"]
    for name in READERS:
        if "ALIASES" in vars(importlib.import_module(name)):
            bad.append("%s keeps its own ALIASES" % name)
    return bad


def main():
    tests = (t_one_answer, t_id_before_title, t_a_tie_names_none, t_one_alias_table)
    fails = 0
    for t in tests:
        bad = t()
        for b in bad:
            print("FAIL  %s: %s" % (t.__name__, b))
        if not bad:
            print("PASS  %s" % t.__name__)
        fails += bool(bad)
    print("%d of %d pass" % (len(tests) - fails, len(tests)))
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
