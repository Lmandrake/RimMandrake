#!/usr/bin/env python3
"""effort.py - the one table of the effort that every launch of ours states, and the steps of the stuck-worker ladder
(RIMMANDRAKE_PASS_EFFORT_ON_EVERY_LAUNCH_STEVEDESKTOP_RAN_MEDIUM; page design/specs/2026-11-25-effort-ladder/boundary.md).

Effort tells a model how hard to think on each step. The owner, by card 2026-11-25: "No medium anywhere" (the floor
is high, for every model and every kind of run); a stuck worker: "Effort up, then model up"; a Fable run on stuck work:
"High". Before this table no launcher passed --effort: each run took its machine's settings file, and in three days
SteveDesktop ran all 32 Opus runs at medium.

    effort.py level [--model M]     print the level a launch of M states (claude_bounded.sh reads it here)
    effort.py args [--model M]      print the argv words, `--effort <level>`

Every launch passes `effort_args(model)` (or `--effort` with `level(model)`); launch_permissions.py `effort_scan`
reads every launch in the tree and is red on one that does not.
"""
import argparse
import sys

LEVELS = ("low", "medium", "high", "xhigh", "max")     # the CLI's own order (claude --help, 2.1.326)
FLOOR = "high"
# The ladder stops at xhigh: the fleet rule says max effort rarely pays. Danger guarded by the ladder's end: a run that
# climbs without end on a fault that needs the owner (the step after the top model is the Conductor, never a launch).
TOP = "xhigh"
# The one table: model tier -> the level a launch of it states. Every value is at or over FLOOR.
EFFORT = {
    "default": "high",
    "sonnet": "high",
    "opus": "high",
    "fable": "high",
}
# The stuck-worker ladder's model steps: a tier -> the model the next fresh run asks for. Fable is asked for by its
# full name (the fleet rule; the CLI's bare "fable" once launched claude-fable-5-1). Fable has no next tier: its stuck
# run goes to the Conductor, and the fleet allows one Fable attempt on a ticket.
MODEL_UP = {"sonnet": "opus", "opus": "claude-fable-5-2"}


class UnderFloor(ValueError):
    """A level under the floor (low, medium) or a word that is no level."""


def tier(model):
    """-> sonnet | opus | fable for a model alias or id, else None."""
    low = str(model or "").lower()
    hits = [t for t in ("sonnet", "opus", "fable") if t in low]
    return hits[0] if len(hits) == 1 else None


def checked(lvl):
    """-> lvl when it is a level at or over the floor; raises UnderFloor by name."""
    if lvl not in LEVELS:
        raise UnderFloor("effort %r is no level of the CLI (%s)" % (lvl, ", ".join(LEVELS)))
    if LEVELS.index(lvl) < LEVELS.index(FLOOR):
        raise UnderFloor("effort %r is under the floor %r: the owner ruled \"No medium anywhere\" (card 2026-11-25)"
                         % (lvl, FLOOR))
    return lvl


def check_table(table=None):
    """-> [what is wrong] with the table: a level under the floor, or no default."""
    table = EFFORT if table is None else table
    bad = [] if "default" in table else ["the table has no default"]
    for k, v in sorted(table.items()):
        try:
            checked(v)
        except UnderFloor as e:
            bad.append("%s: %s" % (k, e))
    return bad


def level(model=None, lvl=None):
    """-> the level a launch of `model` states: `lvl` when given (checked), else the table's."""
    if lvl:
        return checked(lvl)
    return checked(EFFORT.get(tier(model) or "default", EFFORT["default"]))


def effort_args(model=None, lvl=None):
    """-> ["--effort", level]: the words every launch carries."""
    return ["--effort", level(model, lvl)]


def up(lvl):
    """-> the next level on the ladder, or None at TOP or over it."""
    i = LEVELS.index(checked(lvl))
    return LEVELS[i + 1] if i < LEVELS.index(TOP) else None


def model_up(model):
    """-> the model the next fresh run asks for, or None for the top tier (or a model of no tier)."""
    return MODEL_UP.get(tier(model))


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("cmd", choices=("level", "args", "check"))
    ap.add_argument("--model")
    a = ap.parse_args(argv)
    if a.cmd == "check":
        bad = check_table()
        print("\n".join(bad) if bad else "OK: every level is at or over %s" % FLOOR)
        return 1 if bad else 0
    print(level(a.model) if a.cmd == "level" else " ".join(effort_args(a.model)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
