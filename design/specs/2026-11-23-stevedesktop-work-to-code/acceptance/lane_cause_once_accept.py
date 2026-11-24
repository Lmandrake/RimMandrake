#!/usr/bin/env python3
"""Contract: one lane cause has one ticket; an incident has its own clock and ends with itself.

  src/RimMandrake/Utils/testq/lane_ticket.py (pure)
    cause_key(state, reason) -> a name-safe key: the same stall with other job ids, numbers, times, mod lists in another order is the
        same key; another state or another cause is another key.
    step(book, incident) -> (book, act): book {key: {"item", "open", "incidents": [...]}}. act is one of ("file", key) the first time;
        ("note", item) for a return of the same cause; ("end", item) when the incident is over (incident["over"]). A return never files.
        Ending an incident never ends the ticket: the ticket waits on its cause.
    unclaimed_s(book, key, now) -> seconds since the CURRENT incident began, never since the ticket was filed; None when none is open.
  ops_watch.steve_incident_unclaimed reads unclaimed_s. steward.py calls step.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _kit


def L():
    import lane_ticket
    return lane_ticket


def life():
    b, a1 = L().step({}, {"state": "BRAKED", "reason": "filler brake on FlowWorks", "began": 100})
    k = a1[1]
    b[k]["item"] = "IT"
    b, a2 = L().step(b, {"state": "BRAKED", "reason": "filler brake on FlowWorks", "began": 100, "over": 200})
    b, a3 = L().step(b, {"state": "BRAKED", "reason": "filler brake on FlowWorks", "began": 9000})
    return (a1[0], a2, a3, L().unclaimed_s(b, k, 9060)) == ("file", ("end", "IT"), ("note", "IT"), 60)


def wired(f, word):
    return word in open(os.path.join(_kit.REPO, "src/RimMandrake/Utils", f)).read()


key = lambda s, r: L().cause_key(s, r)  # noqa: E731
sys.exit(_kit.run([
    ("job ids and times do not change the key", lambda: key("BRAKED", "brake: J20261112T000000Z-aaaaaa at 10:01") == key("BRAKED", "brake: J20261115T000000Z-bbbbbb at 22:40")),
    ("the order of the mods does not change the key", lambda: key("BRAKED", "filler brake on A, B") == key("BRAKED", "filler brake on B, A")),
    ("another state is another key", lambda: key("BRAKED", "x") != key("PAUSED", "x")),
    ("another cause is another key", lambda: key("PAUSED", "red canary") != key("PAUSED", "runner pull failed")),
    ("a key is safe in an item name", lambda: key("BRAKED", "filler brake on A")[:1].isalpha() and key("BRAKED", "filler brake on A").replace("_", "").isalnum()),
    ("first files, over ends the incident, a return notes the same ticket with a fresh clock", life),
    ("the steward uses it", lambda: wired("testq/steward.py", "lane_ticket")),
    ("ops_watch ages the incident, not the ticket", lambda: wired("ops_watch.py", "unclaimed_s")),
]))
