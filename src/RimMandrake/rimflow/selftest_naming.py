#!/usr/bin/env python3
"""Selftest: the SUBJECT_INTENT_TWIST item-id grammar (design/RimMandrake/ticket_naming_2026-10-10.md).

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
    "TPS_TIMERS_AUDIT_WATCHING_THE_WATCH",
    "BRIDGE_HANG_UNSTICK_THIRD_TIME_LUCKY",
    "ARTPIPE_QUEUE_DRAIN_182_AND_COUNTING",
    "GREY_DEEP_ROSTER_CENSUS_READ_THE_LABELS",
    "OLD_NAME_GATES_EXCISE_SIXTEEN_DAYS_LATE",
    "FIREHAWK_WINGS_REWIRE_FLAPPING_NOT_JIGGLING",
    "MODSCONFIG_COUNT_FIX_LI_TAGS_LIED",
    "GREATBOLE_CORE_RESKIN_NOT_A_DRILL",
    "CHILL_DENSITY_RESCUE_FROM_ABSOLUTE_ZERO",
    "TICKET_NAMES_REDESIGN_NO_MORE_ONES",
    "FLYER_FLIGHT_VERIFY_BY_STATE_NOT_STARING",
    "SETTINGSKIT_TESTS_MEND_STILL_RED",
]


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


def t_parse_splits_on_first_intent_word():
    assert model.parse_name("GREATBOLE_CORE_RESKIN_NOT_A_DRILL") == (
        ["GREATBOLE", "CORE"], "RESKIN", ["NOT", "A", "DRILL"])


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
        "tps_timers_audit_lowercase": "UPPER",
        "TPS_TIMERS_WATCHING": "intent",              # no intent word
        "AUDIT_THE_TIMERS": "subject",                # intent first: no subject
        "TPS_TIMERS_AUDIT": "twist",                  # nothing after the intent
        "TPS_TIMERS_AUDIT_STUFF": "vague",            # banned filler twist
        "TPS_TIMERS_AUDIT_" + "VERYLONGWORD_" * 3 + "END": "long",
        "A_B_C_D_E_F_AUDIT_G": "words",
        "TPS-TIMERS-AUDIT-DASHES": "UPPER",
        "TPS_TIMERS_AUDIT_ÜBER": "UPPER",
    }
    for iid, needle in bad.items():
        probs = model.mint_problems(iid, set())
        assert probs, "%s accepted but should be refused (%s)" % (iid, needle)
        assert any(needle.lower() in p.lower() for p in probs), (
            "%s refused but the reason does not mention %r: %s" % (iid, needle, probs))


def t_collision_rejected():
    known = {"BRIDGE_HANG_UNSTICK_THIRD_TIME_LUCKY"}
    probs = model.mint_problems("BRIDGE_HANG_UNSTICK_THIRD_TIME_LUCKY", known)
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
