"""Test helper: a fixture schedule for dispatcher.load_schedule, which refuses a missing required key
(SCHEDULE_HARDEN_FAIL_CLOSED_NO_DEFAULTS). A test states only the keys it is about; the rest of the required keys
are taken from the shipped dispatcher_schedule.json, so the production loader still has no default of its own."""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import dispatcher as D  # noqa: E402

# The values the fixtures were written against (the retired production defaults), pinned here so each test keeps its
# meaning whatever the shipped schedule says. A test overrides what it is about; it never reads the shipped file.
FIXTURE_VALUES = {"tick_s": 120, "stall_after_s": 240, "verify_s": 300, "handoff_s": 600, "max_retries": 2,
                  "cooldown_s": 3600, "dead_after_s": 600, "recover_verify_s": 300,
                  "ledger_notes": True, "publish": True, "tick_budget_s": 420}
FIXTURE_CAPS = {"wakes_per_seat_hour": 3, "wakes_per_seat_day": 30, "wakes_per_day": 80}


def fill(s):
    for k, v in FIXTURE_VALUES.items():
        s.setdefault(k, v)
    s["caps"] = dict(FIXTURE_CAPS, **(s.get("caps") or {}))
    return s
