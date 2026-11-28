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


def t_a_run_is_on_its_recorded_stage():
    """A recorded stage decides; prose that names other stages (a journal heading in the run's time, its own notes)
    places nothing. A run with no recorded stage is on no stage."""
    import datetime as dt
    mn = importlib.import_module("maturation_now")
    now = 1_800_000_000.0
    rec = {"unit": "u1", "item": "RIMMANDRAKE_FIX_FOOMOD_X", "model": "opus", "at": now - 3000, "ended": now - 2000,
           "status": "finished", "result": "success (exited 0)", "out": "/nonexistent"}
    staged = dict(rec, unit="u2", env={"RM_CONTROL_MOD": "FooMod", "RM_CONTROL_STAGE": "in_game"})
    hand = dict(rec, unit="u3")
    hist = [(dt.datetime.fromtimestamp(now - 4000, dt.timezone.utc), "Stage 1 finished"),
            (dt.datetime.fromtimestamp(now - 2500, dt.timezone.utc), "Stage 3 begins")]
    notes = [{"id": "RIMMANDRAKE_FIX_FOOMOD_X", "role_unit": u, "text": "Stages 4 and 5 next"} for u in ("u2", "u3")]
    got = mn.runs_for_mods(["FooMod"], [staged, hand], notes, {"FooMod": {"history": hist}}, now,
                           spend=lambda r: ("UNMEASURED", None, "UNMEASURED"))["FooMod"]
    by = {r["unit"]: r["stages"] for r in got}
    bad = []
    if by.get("u2") != ["6"]:
        bad.append("a run launched at in_game is placed on %r, not ['6']" % by.get("u2"))
    if by.get("u3") != []:
        bad.append("a run with no recorded stage is placed on %r from prose, not on none" % by.get("u3"))
    if hasattr(mn, "stages_named") and "stages_named(" in open(mn.__file__).read().split("def runs_for_mods", 1)[1] \
            .split("\ndef ", 1)[0]:
        bad.append("runs_for_mods still reads stages from prose (stages_named)")
    return bad


def t_a_run_is_placed_by_its_record_or_its_id_never_its_title():
    """RIMMANDRAKE_FIX_PASSED_MOD_BADGE_HELPER_WAS_TOOL_REPAIR: a title that names a mod (the example of a pipeline-tool
    fault) places no run, and a run that the ticket lane launched is on no mod, whatever its record's RM_CONTROL_MOD says."""
    mn = importlib.import_module("maturation_now")
    now = 1_800_000_000.0
    base = {"unit": "u1", "item": "RIMMANDRAKE_FIX_HAND_ACT_CLOCK", "model": "opus", "at": now - 600, "status": "running",
            "live_state": "running", "out": "/nonexistent"}
    spend = lambda r: ("UNMEASURED", None, "UNMEASURED")      # noqa: E731
    title = {"RIMMANDRAKE_FIX_HAND_ACT_CLOCK": "the ExplosiveKnockback pass read as UTC"}
    cases = {"no record, title only": dict(base),
             "lane launch, word tie recorded": dict(base, next_act_owner="list_dispatch",
                                                    env={"RM_CONTROL_MOD": "ExplosiveKnockback"})}
    bad = []
    for what, rec in cases.items():
        got = mn.runs_for_mods(["ExplosiveKnockback"], [rec], [], {}, now, spend=spend, titles=title)["ExplosiveKnockback"]
        if got:
            bad.append("%s: the run is placed on ExplosiveKnockback" % what)
    own = dict(base, item="RIMMANDRAKE_ADVANCE_X", next_act_owner="maturation_dispatch",
               env={"RM_CONTROL_MOD": "ExplosiveKnockback", "RM_CONTROL_STAGE": "offline_build"})
    if not mn.runs_for_mods(["ExplosiveKnockback"], [own], [], {}, now, spend=spend)["ExplosiveKnockback"]:
        bad.append("a run of a mod's own stage is not placed on the mod")
    return bad


def t_a_badge_of_a_mod_with_no_live_run_names_the_next_step_and_who_takes_it():
    """RIMMANDRAKE_NAME_WHAT_A_WAITING_MOD_WAITS_FOR_PASSED_READ_STUCK: the badge of a mod with no live run is never the bare
    word 'waiting'. Passed, no scope page: rests (calm, not the orange of a wait); a page and no answer: the owner, naming
    the page; a build stage: the tick's reason; an unreadable reason: could not look. A hold reads held."""
    mn = importlib.import_module("maturation_now")

    def word(column, rest=None, waits="UNMEASURED (not given)", held=False):
        m = {"name": "FooMod", "column": column, "held": held, "runs": [], "waits_on": waits, "rest": rest}
        m["status"], m["status_what"] = mn.badge_of(m)
        return m, mn.status_word(m), mn.status_word(m, short=True)

    bad = []
    m, w, s = word("passed", {"pages": [], "answer": "", "err": None})
    if not (m["status"] == "rests" and "no scope page" in w and s != "waiting"
            and mn.STATUS["rests"][0] != mn.STATUS["waiting"][0]):
        bad.append("passed, no scope page: %r %r %r" % (m["status"], w, s))
    m, w, s = word("passed", {"pages": ["scope_proposal_0.3.0.md"], "answer": "", "err": None})
    if not (m["status"] == "waiting" and "owner" in w and "scope_proposal_0.3.0.md" in w):
        bad.append("passed, a page and no answer: %r %r" % (m["status"], w))
    m, w, s = word("3", None, "waiting: waiting, says the Dispatch tick (x): needs the card answered")
    if not (m["status"] == "waiting" and "needs the card answered" in w and s != "waiting"):
        bad.append("build stage: %r %r %r" % (m["status"], w, s))
    m, w, s = word("3", None, "UNMEASURED (mod_next: boom)")
    if "could not look" not in w or "mod_next" not in w:
        bad.append("unreadable reason: %r" % w)
    m, w, s = word("3", None, "held: x", held=True)
    if not (m["status"] == "held" and w == "held"):
        bad.append("held: %r %r" % (m["status"], w))
    return bad


def main():
    tests = (t_one_answer, t_id_before_title, t_a_tie_names_none, t_one_alias_table, t_a_run_is_on_its_recorded_stage,
             t_a_run_is_placed_by_its_record_or_its_id_never_its_title,
             t_a_badge_of_a_mod_with_no_live_run_names_the_next_step_and_who_takes_it)
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
