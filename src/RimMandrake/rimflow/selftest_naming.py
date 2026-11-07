#!/usr/bin/env python3
"""Selftest: the PROJECT_VERB_INTENTION_TWIST item-id grammar (owner 2026-11-05; older doc design/RimMandrake/ticket_naming_2026-10-10.md).

New ids are minted in the new form; legacy `..._N` ids (and B58-style ids) stay valid
forever for everything that already exists; malformed and colliding names are refused
at mint time with a message that says why.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
from rimflow import model, gitindex                              # noqa: E402

PASS, FAIL = [], []

# Every example the design doc prints must actually pass the grammar — a doc whose
# examples the checker refuses teaches the wrong thing.
DOC_EXAMPLES = [
    "RIMMASTER_UNSTICK_BRIDGE_HANG_THIRD_TIME_LUCKY",
    "RIMMASTER_AUDIT_TIMERS_WATCHING_THE_WATCH",
    "RIMMASTER_PRUNE_ARTPIPE_QUEUE_182_AND_COUNTING",
    "RIMMASTER_FROBNICATE_ANYTHING_THE_VERB_IS_FREE",   # no word bank: any verb
    "PROJNOW_TIDY_SCRATCH_SHELF_ONCE_MORE",
]
OLD_FORMS = ["GREATBOLE_CORE_RESKIN_NOT_A_DRILL", "TPS_TIMERS_AUDIT_WATCHING_THE_WATCH",
             "SANDSTORM_WEATHER_TUNING_1", "DIRTY_CODE_REVIEW_LOOP_RESTART_10"]


def case(name, fn):
    try:
        fn()
        PASS.append(name)
        print("ok    %s" % name)
    except AssertionError as e:
        FAIL.append(name)
        print("FAIL  %s\n        %s" % (name, e))
    except Exception as e:                               # noqa: BLE001
        FAIL.append(name)
        print("FAIL  %s\n        unexpected %s: %s" % (name, type(e).__name__, e))


def t_new_style_accepted():
    for iid in DOC_EXAMPLES:
        probs = model.mint_problems(iid, set())
        assert probs == [], "%s refused: %s" % (iid, probs)


def t_parse_new_form_by_position():
    assert model.parse_name("RIMMASTER_UNSTICK_BRIDGE_HANG_THIRD_TIME_LUCKY") == (
        ["RIMMASTER"], "UNSTICK", ["BRIDGE", "HANG", "THIRD", "TIME", "LUCKY"])


def t_parse_old_form_still_reads():
    assert model.parse_name("GREATBOLE_CORE_RESKIN_NOT_A_DRILL") == (
        ["GREATBOLE", "CORE"], "RESKIN", ["NOT", "A", "DRILL"])


def t_old_forms_still_recognised_not_mintable():
    for iid in OLD_FORMS[:2]:
        assert model.is_named_id(iid), iid
        assert model.mint_problems(iid, set()), "%s mintable under the old grammar" % iid


def t_legacy_still_valid_for_existing_items():
    for iid in ("SANDSTORM_WEATHER_TUNING_1", "DIRTY_CODE_REVIEW_LOOP_RESTART_10", "B58"):
        assert model.ID_RE.match(iid), "%s no longer matches ID_RE: replay would break" % iid
        assert model.is_named_id(iid) or iid == "B58", "%s not recognised as an item id" % iid
    assert model.is_named_id("SANDSTORM_WEATHER_TUNING_1")


def t_legacy_form_refused_for_new_items():
    probs = model.mint_problems("SANDSTORM_WEATHER_TUNING_1", set())
    assert probs and any("_1" in p or "number" in p for p in probs), probs


def t_malformed_rejected():
    bad = {
        "rimmaster_audit_lowercase": "UPPER",
        "AUDIT_THE_TIMERS_WATCHING": "project",         # slot 1 not a registry Id
        "RIMMASTER_AUDIT_TIMERS": "words",               # 3 words
        "RIMMASTER_AUDIT_TIMERS_STUFF": "vague",
        "RIMMASTER_AUDIT_" + "VERYLONGWORD_" * 5 + "END": "long",
        "RIMMASTER_A_B_C_D_E_F_G_H_I": "words",            # 9+ words
        "RIMMASTER-AUDIT-DASHES-HERE": "UPPER",
        "RIMMASTER_AUDIT_TIMERS_42": "number",           # trailing bare digits
    }
    for iid, needle in bad.items():
        probs = model.mint_problems(iid, set())
        assert probs, "%s accepted but should be refused (%s)" % (iid, needle)
        assert any(needle.lower() in p.lower() for p in probs), (
            "%s refused but the reason does not mention %r: %s" % (iid, needle, probs))


def t_unreadable_registry_refuses_loudly():
    old = os.environ.get("LODESTAR_ROOT")
    os.environ["LODESTAR_ROOT"] = "/nonexistent/lodestar"
    try:
        probs = model.mint_problems("RIMMASTER_AUDIT_TIMERS_WATCHING_THE_WATCH", set())
        assert any("/nonexistent/lodestar" in p for p in probs), probs
    finally:
        if old is None:
            os.environ.pop("LODESTAR_ROOT")
        else:
            os.environ["LODESTAR_ROOT"] = old


def t_collision_rejected():
    known = {DOC_EXAMPLES[0]}
    probs = model.mint_problems(DOC_EXAMPLES[0], known)
    assert any("already exists" in p for p in probs), probs


def t_gitindex_sees_new_ids_not_constants():
    got = gitindex.ids_in("Fix MAX_FLIGHT_TIME for TPS_TIMERS_AUDIT_WATCHING_THE_WATCH "
                          "and SANDSTORM_WEATHER_TUNING_1 (CLAUDE_MD, ID_RE)")
    assert got == ["TPS_TIMERS_AUDIT_WATCHING_THE_WATCH", "SANDSTORM_WEATHER_TUNING_1"], got


def t_item_heading_recognises_new_ids():
    assert model.is_item_heading("TPS_TIMERS_AUDIT_WATCHING_THE_WATCH", [])
    assert not model.is_item_heading("The", [])


CASES = [(k[2:], v) for k, v in sorted(globals().items()) if k.startswith("t_")]

if __name__ == "__main__":
    for name, fn in CASES:
        case(name, fn)
    print("\n%d/%d passed" % (len(PASS), len(PASS) + len(FAIL)))
    sys.exit(1 if FAIL else 0)
