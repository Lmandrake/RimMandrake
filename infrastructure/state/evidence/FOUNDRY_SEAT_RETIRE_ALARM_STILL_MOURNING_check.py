#!/usr/bin/env python3
"""FOUNDRY_SEAT_RETIRE_ALARM_STILL_MOURNING: the item's runtime done-when, read from rows copied into the repo.

The live journals (D:\\ClaudeWork\\rimmandrake\\dispatcher\\journal.jsonl, ...\\ops_watch\\told.jsonl) are not visible
to a blind checker, so their deciding rows were copied beside this file (..._rows.jsonl, 2026-11-04 04:30Z).
Exit 0 when: the dispatcher journal kept writing rows after the last dead:FOUNDRY (so the alarm stopped, the
journal did not), and incident seats-20261102012009's last event is closed.
"""
import json
import os
import sys

ROWS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "FOUNDRY_SEAT_RETIRE_ALARM_STILL_MOURNING_rows.jsonl")


def main():
    rows = {r["what"]: r for r in (json.loads(x) for x in open(ROWS) if x.strip())}
    s, last, latest, inc = rows["summary"], rows["last dead:FOUNDRY"], rows["latest row"], rows[
        "seats-20261102012009 last event"]
    ok = [
        (s["dead_FOUNDRY_rows"] > 0, "the journal copy can see dead:FOUNDRY at all (%d rows)" % s["dead_FOUNDRY_rows"]),
        (last["kind"] == "dead:FOUNDRY", "last dead:FOUNDRY at %s" % last["at"]),
        (s["rows_after_last_dead"] > 100 and latest["at"] > last["at"] and latest.get("kind") != "dead:FOUNDRY",
         "%d journal rows after it, none dead:FOUNDRY, latest %s" % (s["rows_after_last_dead"], latest["at"])),
        (inc["id"] == "seats-20261102012009" and inc["ev"] == "closed", "incident %s: %s at %s" % (
            inc["id"], inc["ev"], inc["at"])),
    ]
    for good, msg in ok:
        print(("ok    " if good else "FAIL  ") + msg)
    return 0 if all(g for g, _ in ok) else 1


if __name__ == "__main__":
    sys.exit(main())
