"""One lane cause has one ticket; an incident has its own clock and ends by itself. Pure: no I/O, no clock.

cause_key(state, reason) -> a name-safe key. Job ids, numbers and times are dropped and the words are sorted, so the same
    stall with other jobs, times or mods in another order is one key. Another state or another cause is another key.
step(book, incident) -> (book, act). book is {key: {"item", "open", "incidents"}}; act is ("file", key) the first time a
    key is seen, ("note", item) for a return of the same cause, ("end", item) when incident["over"] is set. A return never
    files. Ending an incident never ends the ticket: the ticket waits on its cause.
incidents(events) -> {"ended": [...], "live"} from the ticket's own ledger events (a steward block is one ended incident,
    a lift is a live one), or {"unreadable": why}. offer(inc, run_times) -> (word, why): a cause with two ended incidents
    and no live one is offered to the ticket lane for one Work run between incidents (list_dispatch.py).
unclaimed_s(book, key, now) -> seconds since the CURRENT incident began, never since the ticket was filed; None when no
    incident is open (or the key is unknown): None means "no open incident", never 0.
Boundary page: design/specs/2026-11-23-lane-cause-once/boundary.md
"""
import hashlib
import re

JOB = re.compile(r"\bJ\d{8}T\d{6}Z-\w+", re.I)
CAUSE_ITEM = re.compile(r"STEVE_LANE_UNSTICK_[A-Z]+_UNOWNED_([A-Z0-9]+_[A-Z]{6})(?:_R\d+)?")
WAIT = "steward: waiting for lane cause "


def cause_key(state, reason):
    words = sorted(set(re.findall(r"[a-z]+", JOB.sub(" ", str(reason)).lower())))
    n = int(hashlib.sha1((str(state) + "|" + " ".join(words)).encode()).hexdigest()[:10], 16)
    h = ""
    for _ in range(6):                          # letters only: a digit-bearing hash word is refused as an item name
        n, r = divmod(n, 26)
        h += chr(65 + r)
    st = re.sub(r"[^A-Z0-9]", "", str(state).upper()) or "STATE"
    return "%s_%s" % (st, h)


def step(book, incident):
    key = cause_key(incident.get("state", ""), incident.get("reason", ""))
    ent = book.get(key)
    first = ent is None
    if first:
        ent = book[key] = {"item": None, "open": None, "incidents": []}
    cur = ent["open"]
    began = incident.get("began")
    if incident.get("over") is not None:
        if cur is not None:
            cur["over"] = incident["over"]
        ent["open"] = None
        return book, ("end", ent["item"])
    if cur is None or cur["began"] != began:
        if cur is not None:
            cur["over"] = began                 # a new incident began without a recorded end: the old one ended then
        cur = {"began": began}
        ent["incidents"].append(cur)
        ent["open"] = cur
    return book, ("file", key) if first else ("note", ent["item"])


def unclaimed_s(book, key, now):
    ent = book.get(key)
    if not ent or ent.get("open") is None:
        return None
    return now - ent["open"]["began"]


# ---- the offer: a cause seen in two incidents gets one Work run between incidents ---------------------------------
# (item RIMMANDRAKE_OFFER_TWICE_SEEN_LANE_CAUSE_NOTHING_WORKS_IT) The record is the ticket's own ledger events: the
# steward blocks the ticket (WAIT) when an incident is proven over, and lifts the block when the cause returns. So one
# steward block is one ended incident, and a ticket whose last steward act is a lift has a live incident.
OFFER_AT = 2        # ended incidents of one cause before a Work run is offered; one ended incident is a single sighting


class Unreadable(ValueError):
    """An incident record that cannot be read: the offer says could not look, never zero incidents."""


def _epoch(ts):
    import calendar
    import time
    try:
        return calendar.timegm(time.strptime(str(ts), "%Y-%m-%dT%H:%M:%SZ"))
    except (TypeError, ValueError):
        raise Unreadable("an event time %r cannot be read" % (ts,))


def incidents(events):
    """The ledger events of ONE cause ticket, oldest first -> {"ended": [{"at", "ended", "alarm", "recovery"}], "live"}.
    "at" is the epoch of the steward's block that ended the incident. A record it cannot read -> {"unreadable": why}."""
    try:
        return _incidents(events)
    except Unreadable as e:
        return {"unreadable": str(e)}


def _incidents(events):
    if not isinstance(events, (list, tuple)):
        raise Unreadable("the ticket's events were not read")
    ended, live, alarm, recovery = [], True, None, None
    for ev in events:
        if not isinstance(ev, dict):
            raise Unreadable("an event is not a record")
        kind, text = ev.get("event"), str(ev.get("text") or "")
        if kind == "block" and str(ev.get("reason") or "").startswith(WAIT):
            ended.append({"at": _epoch(ev.get("ts")), "ended": ev["ts"], "alarm": alarm, "recovery": recovery})
            live, alarm, recovery = False, None, None
        elif kind == "unblock":
            _epoch(ev.get("ts"))
            live, alarm, recovery = True, None, None
        elif kind == "spawn":
            alarm = ev.get("title")
        elif kind == "note" and text.startswith("steward:"):
            if "proven again" in text:
                recovery = text
            elif alarm is None:
                alarm = text
    return {"ended": ended, "live": live}


def offer(inc, run_times):
    """-> (word, why). word: offer | blocked | live | spent | could_not_look. inc is incidents()'s result, or {"unreadable":
    why}; run_times the epoch launch times of the ticket's Work runs. A run that started after the latest ended incident
    spends the offer for the incidents so far; the next ended incident makes one more."""
    if "unreadable" in inc:
        return "could_not_look", str(inc["unreadable"])
    if inc["live"]:
        return "live", "an incident of this cause is live: the steward holds the ticket"
    n = len(inc["ended"])
    if n < OFFER_AT:
        return "blocked", "%d ended incident(s) of this cause; the steward waits for the next (a Work run is offered from %d)" % (n, OFFER_AT)
    last = inc["ended"][-1]["at"]
    if any(t > last for t in run_times):
        return "spent", "its Work run since the latest ended incident (%d ended) already ran; the next ended incident offers one more" % n
    return "offer", "this cause ended in %d incidents and no Work run is on it since the latest" % n
