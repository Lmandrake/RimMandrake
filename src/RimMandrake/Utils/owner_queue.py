#!/usr/bin/env python3
"""owner_queue.py — the ONE answer to "what truly waits on the owner?", for RUNNING_NOW's "Needs you" and its mods.

FLEETWATCH_NEEDS_FIX_NOTHING_WHILE_MODS_WAIT: the board's header read "Nothing." while ten mods said "waits on you",
because the header came from a field nobody wrote and the mods from `needs == owner`. Both now come from is_his(), so
they cannot disagree, and the header carries the plain question he must answer for each.

An open item is his when the ledger routes it to him (needs=owner, or blocked with kind owner) AND, if Relentless
holds it, the hold is one only he can lift: an `owner_call` (a delegation_policy §2 line) or a `game` hold for a
flyer's flight (§2.6). Every other Relentless hold (proof_weak, spend, strikes, ...) is a tooling outcome — a harness
failure is never his. Relentless routes those to the seat, not the ledger's needs=owner (RELENTLESS_HOLD_FIX_TOOLING_ISNT_OWNERS);
they are the seat queue, read with --seat. Reading the hold here as well keeps a needs=owner another writer set from counting.

A Designer turn that closed waiting_owner is his too, until an OWNER event naming its item lands
(DESIGNER_TURNS_FIX_LEFT_ON_THE_DOORSTEP; designer_turns() reads designer_stage.pending_turns): its asks are the line.

A mod's first-touch pass item (<FOLDER>_DESIGN_FIRST_TOUCH, needs=owner) is his only to certify, so it is his only once
there is something to certify: an accepted result in its concept folder, or its waiting turn
(OWNER_QUEUE_FIX_FIRST_TOUCH_NEEDS_PASS: 43 of 53 rows had no Designer output). Until then the ledger is untouched, the item
stays open and needs_you() names it under "awaiting_designer". A concepts root that cannot be read keeps every row listed.

The list only names what he has not yet answered (RUNNING_PAGE_FIX_REVIEW_LEFTOVERS): an item leaves it when his own note
landed after the ledger last routed it to him, because his turn is over and the next move is ours. A later `needs owner`
event gives it back to him. It stays open; needs_you() lists it under "answered". Items sharing a leading word
(DRAWBRIDGE_...) fold into one row under `topics`, so one look is not asked five times.

The question per item lives in infrastructure/state/owner_questions.json ({item: one plain line}); an item with no
line there shows its ledger title.

    python3 src/RimMandrake/Utils/owner_queue.py            # the list, one line each
    python3 src/RimMandrake/Utils/owner_queue.py --misrouted  # routed to him but not his
    python3 src/RimMandrake/Utils/owner_queue.py --seat       # Relentless's tooling holds: the seat's to read and lift
"""
import argparse
import json
import os
import re
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "rimflow"))   # relentless_game, designer_stage
import first_touch  # noqa: E402  the pass item's suffix and its id for a concept folder
import relentless_game  # noqa: E402  the supervisor's own test of a flyer hold: two copies of it disagreed
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
QUESTIONS = os.path.join(REPO, "infrastructure", "state", "owner_questions.json")
HIS_HOLDS = ("owner_call",)
ACCEPTED_RESULT = re.compile(r"result\.(.+)\.json$")   # designer_stage.close_run's rename; bare result.json is not yet read
PASSES_TTL = 30     # s: the board asks once per item per refresh; a long-lived board must still see a new result
_passes_memo = {}


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
    if h.get("kind") in HIS_HOLDS or (h.get("kind") == "game" and relentless_game.flyer_hold(h.get("why"))):
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
    return False        # no routing event on record: nothing says his turn came, so nothing says it ended


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


def designer_turns(root=None):
    """-> {item or "DESIGNER_<MOD>": one plain line} for every Designer turn that waits on him
    (designer_stage.pending_turns: status waiting_owner, no OWNER event naming the concept's item since it closed).
    DESIGNER_TURNS_FIX_LEFT_ON_THE_DOORSTEP: FlowWorks turn 2 sat five hours in turn_02.md, on no list he reads.
    A folder or the whole root that cannot be read is a line too (DESIGNER_TURNS_UNMEASURED): never "nothing waits"."""
    try:
        import designer_stage as DS
        turns, bad = DS.pending_turns(root)
    except Exception as e:      # noqa: BLE001
        return {"DESIGNER_TURNS_UNMEASURED": "Designer turns UNMEASURED (%s): read designer_stage.py turns" % str(e)[:120]}
    out = {(t.get("item") or "DESIGNER_%s" % str(t["mod"]).upper()): DS.turn_line(t) for t in turns}
    if bad:
        out["DESIGNER_TURNS_UNMEASURED"] = "Designer turns UNMEASURED for %s" % "; ".join(bad)[:300]
    return out


def read_designer_passes(root):
    """-> {item ids whose concept folder holds an accepted Designer result}, or None when `root` cannot be read.
    A folder answers for the pass id of its own name and for the item its stage.json names. A stage.json that cannot
    be read leaves the name, and a folder that cannot be listed counts as a pass: either way the row stays on his list."""
    try:
        names = os.listdir(root)
    except OSError:
        return None
    out = set()
    for n in names:
        d = os.path.join(root, n)
        if n.startswith("_") or not os.path.isdir(d):
            continue
        try:
            found = [f for f in os.listdir(d) if ACCEPTED_RESULT.match(f) and not f.endswith(".rejected.json")]
        except OSError:
            found = True
        if not found:
            continue
        out.add(first_touch.pass_item_id(n))
        try:
            with open(os.path.join(d, "stage.json"), encoding="utf-8") as f:
                out.add(json.load(f).get("item"))
        except (OSError, ValueError, AttributeError, TypeError):
            pass
    return out


def designer_passes(root=None):
    """read_designer_passes on the Designer's own clone (where pending_turns reads), for PASSES_TTL seconds."""
    try:
        import designer_stage as DS
        root = root or DS.concepts_root()
    except Exception:       # noqa: BLE001  an unread answer keeps the rows listed
        return None
    at, got = _passes_memo.get(root, (None, None))
    if at is None or time.monotonic() - at > PASSES_TTL:
        got = read_designer_passes(root)
        _passes_memo[root] = (time.monotonic(), got)
    return got


def awaiting_designer(it, passes=None):
    """True for a first-touch pass item with no Designer pass to certify yet. An unread answer is False: it stays his."""
    iid = getattr(it, "id", None)
    if not iid or not iid.endswith(first_touch.SUFFIX):
        return False
    passes = designer_passes() if passes is None else passes
    return passes is not None and iid not in passes


def is_his(it, rs, evs=None, turns=None, passes=None):
    """evs: the ledger's events, when the caller has them: without them `answered` cannot be told and stays on the list.
    turns: designer_turns(); an item whose Designer turn waits on him is his whatever the ledger routes.
    passes: designer_passes(), read here when not given (only for a first-touch row)."""
    if turns and getattr(it, "id", None) in turns:
        return True
    return routed(it) and tooling_hold(rs) is None and not answered(it, evs) and not awaiting_designer(it, passes)


def needs_you(items, rel, questions=None, evs=None, turns=None, passes=None):
    """-> {"count", "lines": [{"item", "q"}], "topics", "answered", "awaiting_designer", "text"}, sorted by item id (stable hashes).
    turns: designer_turns() (None: not read here; the board and the CLI pass it). A waiting turn's line replaces the
    item's own question, and a turn whose item the ledger does not hold is its own line."""
    questions = load_questions() if questions is None else questions
    turns = turns or {}
    line = lambda iid, it: {"item": iid, "q": (turns.get(iid) or questions.get(iid) or it.title or iid).strip()}  # noqa: E731
    lines = [line(iid, it) for iid, it in sorted(items.items()) if is_his(it, rel.get(iid), evs, passes=passes)
             or iid in turns]
    lines += [{"item": iid, "q": q} for iid, q in sorted(turns.items()) if iid not in items]
    lines.sort(key=lambda x: x["item"])
    gone = [line(iid, it) for iid, it in sorted(items.items()) if iid not in turns and routed(it)
            and tooling_hold(rel.get(iid)) is None and answered(it, evs)]
    waiting = [line(iid, it) for iid, it in sorted(items.items()) if iid not in turns and routed(it)
               and tooling_hold(rel.get(iid)) is None and not answered(it, evs) and awaiting_designer(it, passes)]
    text = "" if not lines else "%d %s: %s" % (len(lines), "thing" if len(lines) == 1 else "things",
                                               " · ".join(x["q"] for x in lines))
    return {"count": len(lines), "lines": lines, "text": text, "topics": fold(lines), "answered": gone,
            "awaiting_designer": waiting}


def misrouted(items, rel):
    """[(item, hold kind)] routed to him by the ledger but held by Relentless for a tooling reason."""
    return [(iid, tooling_hold(rel.get(iid)).get("kind")) for iid, it in sorted(items.items())
            if routed(it) and tooling_hold(rel.get(iid)) is not None]


def seat_queue(rel):
    """[(item, hold kind, why)] every tooling hold, whatever the ledger says: the seat's queue. Lift: relentless.py unhold."""
    return [(iid, tooling_hold(rs).get("kind"), tooling_hold(rs).get("why") or "") for iid, rs in sorted(rel.items())
            if tooling_hold(rs) is not None]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--misrouted", action="store_true")
    ap.add_argument("--seat", action="store_true")
    a = ap.parse_args()
    sys.path.insert(0, HERE)
    import fleet_mods
    evs, world = fleet_mods.ledger()
    rel = fleet_mods.relentless_states(strict=True)     # a state it cannot read must fail, not drop that item's hold
    if a.seat:
        for iid, kind, why in seat_queue(rel):
            print("%s\t%s\t%s" % (iid, kind, why[:200]))
        return 0
    if a.misrouted:
        for iid, kind in misrouted(world.items, rel):
            print("%s\t%s" % (iid, kind))
        return 0
    n = needs_you(world.items, rel, evs=evs, turns=designer_turns())
    print("%d truly his" % n["count"])
    for x in n["lines"]:
        print("%s\t%s" % (x["item"], x["q"]))
    print("%d answered, the next move is ours" % len(n["answered"]))
    for x in n["answered"]:
        print("answered\t%s\t%s" % (x["item"], x["q"]))
    print("%d first touches open, waiting on their Designer pass before they are his" % len(n["awaiting_designer"]))
    for x in n["awaiting_designer"]:
        print("awaiting_designer\t%s" % x["item"])
    return 0


if __name__ == "__main__":
    sys.exit(main())
