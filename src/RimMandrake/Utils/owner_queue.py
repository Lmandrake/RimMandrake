#!/usr/bin/env python3
"""owner_queue.py — the ONE answer to "what truly waits on the owner?", for Fleet Watch's "Needs you" and its mods.

FLEETWATCH_NEEDS_FIX_NOTHING_WHILE_MODS_WAIT: the board's header read "Nothing." while ten mods said "waits on you",
because the header came from a field nobody wrote and the mods from `needs == owner`. Both now come from is_his(), so
they cannot disagree, and the header carries the plain question he must answer for each.

An open item is his when the ledger routes it to him (needs=owner, or blocked with kind owner) AND, if Relentless
holds it, the hold is one only he can lift: an `owner_call` (a delegation_policy §2 line) or a `game` hold for a
flyer's flight (§2.6). Every other Relentless hold (proof_weak, spend, strikes, ...) is a tooling outcome — a harness
failure is never his — even though Relentless marks the item needs=owner (RELENTLESS_HOLD_FIX_TOOLING_ISNT_OWNERS).

The list only names what he has not yet answered (RUNNING_PAGE_FIX_REVIEW_LEFTOVERS): an item leaves it when his own note
landed after the ledger last routed it to him, because his turn is over and the next move is ours. A later `needs owner`
event gives it back to him. It stays open; needs_you() lists it under "answered". Items sharing a leading word
(DRAWBRIDGE_...) fold into one row under `topics`, so one look is not asked five times.

The question per item lives in infrastructure/state/owner_questions.json ({item: one plain line}); an item with no
line there shows its ledger title.

    python3 src/RimMandrake/Utils/owner_queue.py            # the list, one line each
    python3 src/RimMandrake/Utils/owner_queue.py --misrouted  # routed to him but not his
"""
import argparse
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
QUESTIONS = os.path.join(REPO, "infrastructure", "state", "owner_questions.json")
HIS_HOLDS = ("owner_call",)
FLYER = "flyer"  # relentless_game.FLYER's hold words name a flyer's flight; read, not imported (that module is busy)


def hold_of(rs):
    """Relentless's current hold as a dict, or None (the store keeps a dict; anything else is no hold)."""
    h = (rs or {}).get("hold")
    return h if isinstance(h, dict) else None


def routed(it):
    """The ledger sends it to him."""
    return bool(it is not None and it.open and (it.needs == "owner" or
                                                (getattr(it, "blocked", False) and getattr(it, "blocked_kind", None) == "owner")))


def tooling_hold(rs):
    """A Relentless hold that is not his to lift, or None."""
    h = hold_of(rs)
    if h is None or (rs or {}).get("status") != "held":
        return None
    if h.get("kind") in HIS_HOLDS or (h.get("kind") == "game" and FLYER in (h.get("why") or "").lower()):
        return None
    return h


def answered(it, evs):
    """True when an OWNER note follows the last event that routed the item to him. Unknown events: not answered."""
    if not evs:
        return False
    said = False
    for i in reversed(getattr(it, "history", None) or []):
        e = evs[i] if 0 <= i < len(evs) else {}
        if e.get("event") == "note" and e.get("seat") == "OWNER":
            said = True
        elif ((e.get("event") == "needs" and e.get("to") == "owner") or (e.get("event") == "file" and e.get("needs") == "owner")
              or (e.get("event") == "block" and e.get("kind") == "owner")):
            return said
    return said


def is_his(it, rs, evs=None):
    """evs: the ledger's events, when the caller has them: without them `answered` cannot be told and stays on the list."""
    return routed(it) and tooling_hold(rs) is None and not answered(it, evs)


def load_questions(path=QUESTIONS):
    try:
        with open(path) as f:
            q = json.load(f)
        return q if isinstance(q, dict) else {}
    except (OSError, ValueError):
        return {}


def topic(item):
    return item.split("_", 1)[0]


def fold(lines):
    """[{"item","q"}] -> [{"topic", "items", "q", "others"}]: one row per leading word, its first line the question."""
    out = {}
    for x in lines:
        t = out.setdefault(topic(x["item"]), {"topic": topic(x["item"]), "items": [], "q": x["q"], "others": []})
        t["items"].append(x["item"])
        if x["q"] != t["q"]:
            t["others"].append(x["q"])
    return sorted(out.values(), key=lambda t: t["items"][0])


def needs_you(items, rel, questions=None, evs=None):
    """-> {"count", "lines": [{"item", "q"}], "topics", "answered", "text"}, sorted by item id (stable hashes)."""
    questions = load_questions() if questions is None else questions
    line = lambda iid, it: {"item": iid, "q": (questions.get(iid) or it.title or iid).strip()}  # noqa: E731
    lines = [line(iid, it) for iid, it in sorted(items.items()) if is_his(it, rel.get(iid), evs)]
    gone = [line(iid, it) for iid, it in sorted(items.items()) if routed(it) and tooling_hold(rel.get(iid)) is None and answered(it, evs)]
    text = "" if not lines else "%d %s: %s" % (len(lines), "thing" if len(lines) == 1 else "things",
                                               " · ".join(x["q"] for x in lines))
    return {"count": len(lines), "lines": lines, "text": text, "topics": fold(lines), "answered": gone}


def misrouted(items, rel):
    """[(item, hold kind)] routed to him by the ledger but held by Relentless for a tooling reason."""
    return [(iid, tooling_hold(rel.get(iid)).get("kind")) for iid, it in sorted(items.items())
            if routed(it) and tooling_hold(rel.get(iid)) is not None]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--misrouted", action="store_true")
    a = ap.parse_args()
    sys.path.insert(0, HERE)
    import fleet_mods
    evs, world = fleet_mods.ledger()
    rel = fleet_mods.relentless_states()
    if a.misrouted:
        for iid, kind in misrouted(world.items, rel):
            print("%s\t%s" % (iid, kind))
        return 0
    n = needs_you(world.items, rel, evs=evs)
    print("%d truly his" % n["count"])
    for x in n["lines"]:
        print("%s\t%s" % (x["item"], x["q"]))
    print("%d answered, the next move is ours" % len(n["answered"]))
    for x in n["answered"]:
        print("answered\t%s\t%s" % (x["item"], x["q"]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
