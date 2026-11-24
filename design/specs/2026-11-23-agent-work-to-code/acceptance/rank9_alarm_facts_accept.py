#!/usr/bin/env python3
"""Acceptance for RIMMANDRAKE_GATHER_ALARM_FACTS_BY_PROGRAM_MOST_END_ACKED (rank 9 of one_page.md).

Contract: a new module src/RimMandrake/rimflow/incident_packet.py
  packet(metric, facts) -> {"text", "could_not_look": [str]}
      facts = {"definition": {"text", "source"} or None, "readings": [{"t", "v", "m"}] or None, "owner_of_cause": str or
      None, "last_acts": [{"ts", "text"}] or None, "now": epoch}. None is unreadable; [] was read and is empty.
      The text holds the definition with the code line it came from, the readings with their ages, the owner of the cause
      and the last acts. Its plan and trigger lines are blank: the agent writes them.
  answer(metric, facts, route) -> ("program"|"agent", why)
      route = {"route": "program", "band": {"min", "max"}, "max_age_s", "slow_rise": {"days", "share"}}. program only when
      the last reading is MEASURED, inside the band, younger than max_age_s, and the readings of the last `days` days do
      not rise by `share` of the band's width. Everything else is agent, with its cause.
  gather(metric, readers, deadline_s=20) -> facts      a reader that raises or hangs gives None for its part.
Expected when built: PASS 15/15."""
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _harness as H  # noqa: E402

IP = H.load("incident_packet")
NOW = 1795492604
DAY = 86400
RT = {"route": "program", "band": {"min": 0, "max": 10}, "max_age_s": 3600, "slow_rise": {"days": 7, "share": 0.5}}


def rd(vals, last_age=60, m="MEASURED"):
    n = len(vals)
    return [{"t": NOW - last_age - DAY * (n - 1 - i), "v": v, "m": m} for i, v in enumerate(vals)]


def facts(**k):
    f = {"definition": {"text": "count of x", "source": "src/RimMandrake/Utils/ops_watch.py:10"}, "readings": rd([3, 3, 3, 3]),
         "owner_of_cause": "Operations", "last_acts": [{"ts": "t1", "text": "acked: steady"}], "now": NOW}
    f.update(k)
    return f


def an(route=None, **k):
    return H.need(IP).answer("disk.x", facts(**k), RT if route is None else route)


def pk(**k):
    return H.need(IP).packet("disk.x", facts(**k))


H.check("steady, fresh and in band: the program answers", lambda: an()[0] == "program")
H.check("out of band: agent", lambda: an(readings=rd([3, 3, 11]))[0] == "agent")
H.check("a slow rise inside the band: agent, and the why says so", lambda: (
    lambda a: a[0] == "agent" and "rise" in a[1])(an(readings=rd([2, 3, 4, 5, 6, 7, 8]))))
H.check("not MEASURED: agent", lambda: an(readings=rd([3, 3], m="UNMEASURED"))[0] == "agent")
H.check("stale: an old last reading is agent", lambda: an(readings=rd([3, 3], last_age=7200))[0] == "agent")
H.check("unreadable and empty readings are agent, with two different causes", lambda: (
    lambda a, b: a[0] == b[0] == "agent" and "could not look" in a[1].lower() and a[1] != b[1]
    and "could not look" not in b[1].lower())(an(readings=None), an(readings=[])))
H.check("no band on the route: agent", lambda: an(route={"route": "program"})[0] == "agent")
H.check("a role route is never answered by the program", lambda: an(route=dict(RT, route="role"))[0] == "agent")
H.check("the packet holds the definition with its code line", lambda: "count of x" in pk()["text"]
        and "ops_watch.py:10" in pk()["text"])
H.check("the packet holds readings, owner and last acts", lambda: all(s in pk()["text"] for s in ("3", "Operations", "acked: steady")))
H.check("a part that could not be read is said; an empty part is not could not look", lambda: (
    lambda a, b: any("definition" in c for c in a["could_not_look"]) and "could not look" in a["text"].lower()
    and b["could_not_look"] == [])(pk(definition=None), pk(last_acts=[])))
H.check("the plan and the trigger stay blank for the agent", lambda: all(
    any(ln.strip().lower().rstrip() == w for ln in pk()["text"].splitlines()) for w in ("plan:", "trigger:")))
H.check("a past act's spend does not reach the agent", lambda: "$" not in pk(
    last_acts=[{"ts": "t", "text": "The run used $21.6 of the $30 budget. Acked."}])["text"])


def hung():
    g = H.need(IP).gather      # absent: fail at once, with no sleeping reader left behind
    t0 = time.time()
    f = g("disk.x", {"readings": lambda: time.sleep(8), "definition": lambda: {"text": "d", "source": "s"},
                     "last_acts": lambda: 1 / 0}, deadline_s=1)
    return f["readings"] is None and f["last_acts"] is None and f["definition"]["text"] == "d" and time.time() - t0 < 6


H.check("hung or raising readers give None for their part, inside the deadline", hung)
H.check("the page names its promises and the selftest runs at ./publish", lambda: H.page(
    "design/specs/2026-11-23-alarm-facts/boundary.md", "a-slow-rise-calls-the-agent", "could-not-look-calls-the-agent",
    "the-definition-comes-from-the-code") and H.listed("src/RimMandrake/rimflow/selftest_incident_packet.py"))
H.done(15)
