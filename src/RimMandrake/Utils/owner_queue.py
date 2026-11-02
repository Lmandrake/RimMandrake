#!/usr/bin/env python3
"""owner_queue.py — the ONE answer to "what truly waits on the owner?", for Fleet Watch's "Needs you" and its mods.

FLEETWATCH_NEEDS_FIX_NOTHING_WHILE_MODS_WAIT: the board's header read "Nothing." while ten mods said "waits on you",
because the header came from a field nobody wrote and the mods from `needs == owner`. Both now come from is_his(), so
they cannot disagree, and the header carries the plain question he must answer for each.

An open item is his when the ledger routes it to him (needs=owner, or blocked with kind owner) AND, if Relentless
holds it, the hold is one only he can lift: an `owner_call` (a delegation_policy §2 line) or a `game` hold for a
flyer's flight (§2.6). Every other Relentless hold (proof_weak, spend, strikes, ...) is a tooling outcome — a harness
failure is never his — even though Relentless marks the item needs=owner (RELENTLESS_HOLD_FIX_TOOLING_ISNT_OWNERS).

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


def is_his(it, rs):
    return routed(it) and tooling_hold(rs) is None


def load_questions(path=QUESTIONS):
    try:
        with open(path) as f:
            q = json.load(f)
        return q if isinstance(q, dict) else {}
    except (OSError, ValueError):
        return {}


def needs_you(items, rel, questions=None):
    """-> {"count", "lines": [{"item", "q"}], "text"} for the board/needs doc, sorted by item id (stable hashes)."""
    questions = load_questions() if questions is None else questions
    lines = [{"item": iid, "q": (questions.get(iid) or it.title or iid).strip()}
             for iid, it in sorted(items.items()) if is_his(it, rel.get(iid))]
    text = "" if not lines else "%d %s: %s" % (len(lines), "thing" if len(lines) == 1 else "things",
                                               " · ".join(x["q"] for x in lines))
    return {"count": len(lines), "lines": lines, "text": text}


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
    world = fleet_mods.ledger()[1]
    rel = fleet_mods.relentless_states()
    if a.misrouted:
        for iid, kind in misrouted(world.items, rel):
            print("%s\t%s" % (iid, kind))
        return 0
    n = needs_you(world.items, rel)
    print("%d truly his" % n["count"])
    for x in n["lines"]:
        print("%s\t%s" % (x["item"], x["q"]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
