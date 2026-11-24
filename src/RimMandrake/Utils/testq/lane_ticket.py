"""One lane cause has one ticket; an incident has its own clock and ends by itself. Pure: no I/O, no clock.

cause_key(state, reason) -> a name-safe key. Job ids, numbers and times are dropped and the words are sorted, so the same
    stall with other jobs, times or mods in another order is one key. Another state or another cause is another key.
step(book, incident) -> (book, act). book is {key: {"item", "open", "incidents"}}; act is ("file", key) the first time a
    key is seen, ("note", item) for a return of the same cause, ("end", item) when incident["over"] is set. A return never
    files. Ending an incident never ends the ticket: the ticket waits on its cause.
unclaimed_s(book, key, now) -> seconds since the CURRENT incident began, never since the ticket was filed; None when no
    incident is open (or the key is unknown): None means "no open incident", never 0.
Boundary page: design/specs/2026-11-23-stevedesktop-work-to-code/lane_ticket_boundary.md
"""
import hashlib
import re

JOB = re.compile(r"\bJ\d{8}T\d{6}Z-\w+", re.I)


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
