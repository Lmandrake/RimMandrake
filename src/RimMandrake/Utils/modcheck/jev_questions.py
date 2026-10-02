"""modcheck.jev_questions -- EVERY Jev question and threshold the northstar harness uses, in one file.

This is the human review surface (the ConsultJev rule: one file, nothing else defines a question or
compares against a constant). Design: design/RimMandrake/northstar_helpers_plan.md section 7 plus the
GPT review's additions (northstar_helpers_gpt_review.md section 4). Rules that shaped it:

  * Jev reads TEXT only (no screenshots), reads literally, cannot count or compare ticks. All counting,
    diffing and "since t0" filtering is done in code BEFORE Jev sees a field.
  * Never one question alone: every verdict question has a GUARD that cannot see the biasing input, and a
    guard runs in its OWN call with its own reduced state (a call shares one state across its questions,
    so a guard in the same call would see what it must not).
  * Confidence is a GATE, never a ranker. Jev never drives, never decides to stop time, never passes a
    component, never heals. It tags and flags, in SHADOW MODE, until each threshold below cites a sweep.

THRESHOLDS: every `T_*` is None == UNMEASURED. While None, jev_triage logs answers and ACTS ON NOTHING.
Set one only with the measurement beside it (consultjev docs/FINDINGS.md convention).
"""

MODEL = "jev-latest"

# ---- thresholds: None means UNMEASURED; nothing acts on a Jev answer until its threshold is set ---------
T_GATE = None            # minimum confidence for a choice verdict to be acted on at all
T_DESCRIBED = None       # DEF_IS_DESCRIBED noul floor
T_HURTS = None           # DEF_HURTS_DIRECTLY noul floor
T_PARAM_OR_TYPE = None   # MSG_NAMES_PARAM_OR_TYPE noul floor (guards 'harness_mistake')
T_OBSERVED_READBACK = None  # OBSERVED_IS_READBACK noul floor (guards the vacuous-test lint)
T_EXEMPT_WIDE = None     # EXEMPTION_COULD_BE_BROAD noul floor

# ---- rank 1: what does an UNKNOWN modded def do to colonists? (asked once per def, then cached) ----------
DEF_HARM = {
    "type": "choice",
    "instructions": "What does the thing described in `description` do to colonists on the map?",
    "criteria": {
        "injures_or_kills": "It directly damages, injures, sickens or kills pawns.",
        "hostile_arrival": "It brings hostile people, animals or machines onto the map.",
        "mood_or_mind": "It changes mood, causes mental breaks, or alters behaviour, without injury.",
        "environment": "It changes weather, temperature, terrain, light or plants, without directly hurting pawns.",
        "item_loss": "It destroys, steals, spoils or removes items.",
        "harmless": "It has no meaningful effect on pawns or items, e.g. a notification or flavour text.",
        "not_stated": "The description does not say what it does.",
    },
}
DEF_IS_DESCRIBED = {          # GUARD: never sees the harm options; sees only `description`
    "type": "noul",
    "instructions": "Does `description` say what this thing does in the game, rather than only naming it?",
    "criteria": {"true": "It states an effect.", "false": "It only names or labels the thing."},
}
DEF_HURTS_DIRECTLY = {        # second independent guard on the dangerous branch
    "type": "noul",
    "instructions": "Does `description` state that pawns can be hurt, sickened or killed?",
    "criteria": {"true": "It says pawns can be hurt, sickened or killed.", "false": "It does not say so."},
}

# ---- rank 2: why did this check FAIL? (post-run routing tag; reversible, visible, never a verdict) -------
FAIL_ROUTE = {
    "type": "choice",
    "instructions": "Why did the check in `failure_message` fail?",
    "criteria": {
        "mod_behaviour": "The game ran the check correctly and the mod's content or behaviour differed from what was expected.",
        "harness_mistake": "The test script asked the wrong question: a wrong parameter, a wrong type comparison, a truncated list, a wrong field name.",
        "bridge_tool": "A bridge tool refused, crashed, or returned a malformed result.",
        "outside_event": "Something unrelated to the mod (a raid, an animal, a fire, a death, a mental break) changed the state first.",
        "not_stated": "The message does not give enough to tell.",
    },
}
MSG_NAMES_PARAM_OR_TYPE = {   # GUARD for harness_mistake; sees only `failure_message`
    "type": "noul",
    "instructions": "Does `failure_message` mention a parameter, a field name, a data type, or a list limit?",
    "criteria": {"true": "It names one of those.", "false": "It does not."},
}

# ---- rank 3: what most likely harmed this pawn? (only when the code table in detectors returns 0 or 2+) --
CAUSE = {
    "type": "choice",
    "instructions": "What most likely harmed the pawn described in the state?",
    "criteria": {
        "fire": "Burns or heat injuries with fire nearby.",
        "animal_attack": "Bites or scratches with a wild animal nearby.",
        "raid_or_hostile_people": "Gunshot, cut or stab wounds with hostile people nearby.",
        "starvation_or_exposure": "Malnutrition, hypothermia, heatstroke or frostbite.",
        "mental_break_or_social_fight": "A mental state or a fight between colonists.",
        "disease_or_toxin": "An illness, infection or toxic exposure.",
        "test_action": "A deliberate test action listed in `test_actions`.",
        "not_stated": "The fields do not point to any cause.",
    },
}
GUARD_HEDIFF_IS_INJURY = {    # sees only `new_hediffs`
    "type": "noul",
    "instructions": "Is any entry in `new_hediffs` a physical wound?",
    "criteria": {"true": "At least one is a wound.", "false": "None is a wound."},
}
GUARD_THREAT_PRESENT = {      # sees only `letters_since_t0`
    "type": "noul",
    "instructions": "Does `letters_since_t0` mention an attack, raid or hunting animal?",
    "criteria": {"true": "A letter mentions one.", "false": "None does."},
}

# ---- GPT review additions (shadow-only lint over a VALIDATION SCRIPT, no game needed) ------------------
VACUOUS_TEST = {
    "type": "choice",
    "instructions": "How does `observed_assertion` relate to the behavior claimed in `test_intent` after `stimulus_summary`?",
    "criteria": {
        "directly_tests": "It reads back the very behavior the intent claims.",
        "reasonable_proxy": "It reads back something that closely implies the claimed behavior.",
        "setup_only": "It only confirms that the setup action was performed.",
        "tests_different_claim": "It reads back something unrelated to the claimed behavior.",
        "not_stated": "The fields do not say.",
    },
}
OBSERVED_IS_READBACK = {      # GUARD: sees only `observed_assertion`
    "type": "noul",
    "instructions": "Does `observed_assertion` describe a value or state read back from the game after an action, rather than only an action that was requested?",
    "criteria": {"true": "It is a read-back of game state.", "false": "It only restates an action that was requested."},
}
EXEMPTION_AUDIT = {
    "type": "choice",
    "instructions": "Why is `exemption` appropriate or inappropriate for `detector` during this test phase?",
    "criteria": {
        "necessary_subject": "The exemption covers exactly the thing the test causes.",
        "narrow_fixture": "The exemption covers one specific fixture and nothing else.",
        "overbroad_hides_related_harm": "The exemption could also hide harm unrelated to the test subject.",
        "unrelated_exemption": "The exemption has nothing to do with the test's subject.",
        "not_stated": "The fields do not say.",
    },
}
EXEMPTION_COULD_BE_BROAD = {  # GUARD: sees only `exemption`
    "type": "noul",
    "instructions": "Could this exemption match events or entities other than one explicitly identified test subject, definition, or bounded area?",
    "criteria": {"true": "It could match more than one explicit subject.", "false": "It names exactly one subject or area."},
}

BATTERIES = {
    "def_harm": {"DEF_HARM": DEF_HARM},
    "fail_route": {"FAIL_ROUTE": FAIL_ROUTE},
    "cause": {"CAUSE": CAUSE},
    "vacuous": {"VACUOUS_TEST": VACUOUS_TEST},
    "exemption": {"EXEMPTION_AUDIT": EXEMPTION_AUDIT},
}
# Guards run in their OWN calls, each with only the fields named here (blindness is the point).
GUARDS = {
    "def_harm": [("DEF_IS_DESCRIBED", DEF_IS_DESCRIBED, ("description",)),
                 ("DEF_HURTS_DIRECTLY", DEF_HURTS_DIRECTLY, ("description",))],
    "fail_route": [("MSG_NAMES_PARAM_OR_TYPE", MSG_NAMES_PARAM_OR_TYPE, ("failure_message",))],
    "cause": [("GUARD_HEDIFF_IS_INJURY", GUARD_HEDIFF_IS_INJURY, ("new_hediffs",)),
              ("GUARD_THREAT_PRESENT", GUARD_THREAT_PRESENT, ("letters_since_t0",))],
    "vacuous": [("OBSERVED_IS_READBACK", OBSERVED_IS_READBACK, ("observed_assertion",))],
    "exemption": [("EXEMPTION_COULD_BE_BROAD", EXEMPTION_COULD_BE_BROAD, ("exemption",))],
}

# What NOT to use Jev for (kept here so a reviewer sees the boundary beside the questions):
#   counting hostiles/colonists/items; tick or budget arithmetic; deciding to pause or stop; deciding a
#   component PASSes; judging a screenshot (it cannot see one); choosing which helper to run; matching a
#   log line to a namespace (substring); deciding whether a letter is new (fingerprint diff).
