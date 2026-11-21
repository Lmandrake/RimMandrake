#!/usr/bin/env python3
"""The one test a his-words gate applies to a Conductor instruction.

Owner, 2026-10-30 (ledger CONDUCTOR_AUTHORITY_DECIDE_NO_ASKING_MOM): "Conductor should have authorization to command
agents with the user authority, period. No more "I need the user to confirm." That breaks the whole point of this
endeavor. Make that change everywhere."

A tool that takes his typed words as its authority also takes this ruling, cited by id, with the Conductor's text in
--why. Only the Conductor's rulings (RULINGS): another standing ruling or a bare agent reason grants nothing at such
a gate.
"""
RULING = "CONDUCTOR_AUTHORITY_DECIDE_NO_ASKING_MOM"
# The Conductor's own act (owner 2026-11-19, conductor_acts.RULING) carries the same authority at a his-words gate: a
# Conductor that cited it was refused here for citing the "wrong" one of its two rulings (owner 2026-11-20: "The system
# should not be refusing needed items."; RIMMANDRAKE_STOP_GATES_DEMANDING_OWNER_WORDS_HE_ALREADY_SPOKE).
RULINGS = (RULING, "RIMMANDRAKE_ENACT_CONDUCTOR_MAY_DO_ALL_BUT_FIVE_ACTS")
ROUTE = "--per-ruling %s --why \"<the Conductor's instruction>\"" % RULING


def carried(per_ruling, why):
    """True when the caller cites one of the Conductor's rulings and carries the Conductor's text."""
    return (per_ruling or "").strip() in RULINGS and bool((why or "").strip())


def words(owner_said, per_ruling, why):
    """The authority text a his-words gate records: his words, else the ruling and the Conductor's text, tagged so a
    reader never takes it for his own sentence; None when the caller has neither."""
    said = (owner_said or "").strip()
    if said:
        return said
    return "PER RULING %s: %s" % (per_ruling.strip(), why.strip()) if carried(per_ruling, why) else None
