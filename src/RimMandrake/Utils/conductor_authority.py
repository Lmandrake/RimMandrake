#!/usr/bin/env python3
"""The one test a his-words gate applies to a Conductor instruction.

Owner, 2026-10-30 (ledger CONDUCTOR_AUTHORITY_DECIDE_NO_ASKING_MOM): "Conductor should have authorization to command
agents with the user authority, period. No more "I need the user to confirm." That breaks the whole point of this
endeavor. Make that change everywhere."

A tool that takes his typed words as its authority also takes this ruling, cited by id, with the Conductor's text in
--why. Only this ruling: another standing ruling or a bare agent reason grants nothing at such a gate.
"""
RULING = "CONDUCTOR_AUTHORITY_DECIDE_NO_ASKING_MOM"
ROUTE = "--per-ruling %s --why \"<the Conductor's instruction>\"" % RULING


def carried(per_ruling, why):
    """True when the caller cites this ruling and carries the Conductor's text."""
    return (per_ruling or "").strip() == RULING and bool((why or "").strip())


def words(owner_said, per_ruling, why):
    """The authority text a his-words gate records: his words, else the ruling and the Conductor's text, tagged so a
    reader never takes it for his own sentence; None when the caller has neither."""
    said = (owner_said or "").strip()
    if said:
        return said
    return "PER RULING %s: %s" % (RULING, why.strip()) if carried(per_ruling, why) else None
