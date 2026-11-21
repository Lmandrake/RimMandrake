#!/usr/bin/env python3
"""principal.py — is the caller the owner or the Conductor window, and the one answer a gate of form gives them.

Owner, 2026-11-21 about 1:25 AM PST: "Great. So conductor is being refused by the pipeline. This will not stand." and,
the same night: "I don't want this pipeline turning into a complex expert system or tree of descriptions and specific
rules. Fix the principles. Generalize." Rules: root CLAUDE.md §His word and the Conductor's act are not refused, §A fault
of form is repaired where it is found. Item RIMMANDRAKE_NEVER_REFUSE_THE_CONDUCTOR_SEVEN_REFUSALS_ONE_NIGHT. Page:
design/specs/2026-11-21-never-refuse-the-conductor/boundary.md (selftest_never_refuse_conductor.py).

One rule, one place. A gate that is about to refuse an act for FORM (a name, a flag, a text shape, a missing paste, a
stale stamp, an order of steps a tool can do itself) calls `form(what, ...)` instead of refusing:

  * the caller is a PRINCIPAL (the owner, or the Conductor window) -> one NOTE line on stderr, the note on the event
    (`form_notes`), and the act goes on: `form` returns the note;
  * anyone else (a launched run: RM_ROLE_UNIT set; any other seat) -> the gate's ordinary refusal, unchanged.

The Conductor window is seat BENCH (typed BENCH or CONDUCTOR) with no RM_ROLE_UNIT. The owner is seat OWNER with no
RM_ROLE_UNIT. The seat is a mark, not authentication (as mod_owner_hold's was). A helper, role run, tick or detached run
gains NOTHING here. What still binds a principal is never routed through `form`: his five acts, his holds, his OWNER
bridge hold, a `./pipe` stop of his, the spend stop, the account order and leave lines, machine-safety brakes.
"""
import os
import sys

NOTE_HEAD = "NOTE (form, waived for the %s): "


def _canon(seat):
    s = str(seat or "").strip().upper()
    return "BENCH" if s == "CONDUCTOR" else s


def who(env=None, seat=None):
    """-> "conductor" | "owner" | None. `seat`: the seat a tool already resolved (rimflow's --seat); else the
    environment (RIMFLOW_SEAT, then AGENT_SEAT). Any RM_ROLE_UNIT -> None: a launched run is never a principal."""
    env = os.environ if env is None else env
    if (env.get("RM_ROLE_UNIT") or "").strip():
        return None
    s = _canon(seat or env.get("RIMFLOW_SEAT") or env.get("AGENT_SEAT"))
    return {"BENCH": "conductor", "OWNER": "owner"}.get(s)


def conductor_window(env=None, seat=None):
    """-> (ok, why): is this process the Conductor window? (mod_owner_hold.conductor_window answers through this.)"""
    env = os.environ if env is None else env
    if (env.get("RM_ROLE_UNIT") or "").strip():
        return False, "a launched run (RM_ROLE_UNIT=%s) is not the Conductor window" % env["RM_ROLE_UNIT"]
    s = _canon(seat or env.get("AGENT_SEAT") or env.get("RIMFLOW_SEAT"))
    if s != "BENCH":
        return False, "seat %s is not the Conductor's (BENCH)" % (s or "unset")
    return True, "the Conductor window"


def form(what, refusal=None, event=None, env=None, seat=None, stream=None, die=None, code=2):
    """The shared path of every refusal for form. -> the note (str) when the caller is a principal: the act goes on.
    Otherwise refuses as the gate always did: die(refusal) when given, else write refusal to stderr and SystemExit(code).
    `refusal=None` means "ask only": -> None for a non-principal, and the gate refuses its own way."""
    w = who(env, seat)
    if w:
        note = str(what).strip()
        print((NOTE_HEAD % ("Conductor" if w == "conductor" else "owner")) + note, file=stream or sys.stderr)
        if isinstance(event, dict):
            event.setdefault("form_notes", []).append(note)
        return note
    if refusal is None:
        return None
    if die is not None:
        die(refusal)
    sys.stderr.write(str(refusal).rstrip() + "\n")
    raise SystemExit(code)


if __name__ == "__main__":
    print(who() or "neither")
