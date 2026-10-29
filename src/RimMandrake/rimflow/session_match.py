"""ONE rule for "is this live session the seat/hold window called N". The title hook (.claude/hooks/set_session_title.py)
renames a seat window to "<N> ▶ <current queue item>", so a window is N or N + " ▶ " + anything. Nothing else
(no "AGENT BENCHX", no prefix without the separator) matches.

A seat may answer to more than one name (CONDUCTOR_RCNAME_RENAME_DISPATCHER_ALIAS): seat BENCH is SHOWN and launched as
"CONDUCTOR" (dispatcher_schedule seats.BENCH.session_name), and a window launched before the rename still carries
"AGENT BENCH" until its next relaunch (seats.BENCH.session_aliases). Every matcher takes the whole list: names_of(cfg)."""
import json
import os

TITLE_SEP = " ▶ "
SCHEDULE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "dispatcher_schedule.json")


def name_matches(name, n):
    """n is one name or a list/tuple of names (any of them)."""
    if isinstance(n, (list, tuple)):
        return any(name_matches(name, x) for x in n)
    return bool(n) and isinstance(name, str) and (name == n or name.startswith(n + TITLE_SEP))


def names_of(cfg):
    """-> every name a seat cfg answers to: session_name first (the one a launch uses), then session_aliases."""
    out = []
    for n in [(cfg or {}).get("session_name")] + list((cfg or {}).get("session_aliases") or []):
        if isinstance(n, str) and n and n not in out:
            out.append(n)
    return out


def seat_names(seat, sch=None):
    """-> the names of seat SEAT from the schedule (read from disk when sch is None); "AGENT <SEAT>" when the schedule
    is unreadable or has no entry, which is the pre-rename convention every other seat still uses."""
    if sch is None:
        try:
            with open(SCHEDULE, encoding="utf-8") as f:
                sch = json.load(f)
        except (OSError, ValueError):
            sch = {}
    names = names_of(((sch or {}).get("seats") or {}).get(seat))
    return names or ["AGENT " + seat]
