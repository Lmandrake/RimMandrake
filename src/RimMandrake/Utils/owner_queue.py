#!/usr/bin/env python3
"""owner_queue.py — the ONE answer to "what truly waits on the owner?", for MATURATION_NOW's "Needs Mandrake" and the mods.

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

A mod's first-touch pass item (<FOLDER>_DESIGN_FIRST_TOUCH, needs=owner) is his (or the Conductor's) to certify, so it is listed only once
there is something to certify: an accepted result in its concept folder, or its waiting turn
(OWNER_QUEUE_FIX_FIRST_TOUCH_NEEDS_PASS: 43 of 53 rows had no Designer output). Until then the ledger is untouched, the item
stays open and needs_you() names it under "awaiting_designer". A concepts root that cannot be read keeps every row listed.
His own lock of the mod's Design Version (version/VERSION.json state locked, locked_by owner), or the Conductor window's
lock under the five-acts ruling (locked_by conductor, owner 2026-11-19, conductor_acts.lock_problem), is that certification
(RIMMANDRAKE_CERTIFY_FIRST_TOUCH_BY_OWNER_LOCK: Graffiti sat under Needs Mandrake after his "Lock as 0.1.0 now"); a
pipeline lock certifies nothing. needs_you() names such a row under "certified".

The list only names what he has not yet answered (RUNNING_PAGE_FIX_REVIEW_LEFTOVERS): an item leaves it when his own note
landed after the ledger last routed it to him, because his turn is over and the next move is ours. A later `needs owner`
event gives it back to him. It stays open; needs_you() lists it under "answered". Items sharing a leading word
(DRAWBRIDGE_...) fold into one row under `topics`, so one look is not asked five times.

An item whose turn has not come is not listed: a dated wait ahead, or a block on a ticket that is still open (`later`).
needs_you() names it under "later". (2026-11-23: an item waiting to 2026-12-05 sat under Needs Mandrake.)

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
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "rimflow"))   # run_store, designer_stage
import first_touch  # noqa: E402  the pass item's suffix and its id for a concept folder
import run_store  # noqa: E402  the store's own test of a flyer hold: two copies of it disagreed
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
QUESTIONS = os.path.join(REPO, "infrastructure", "state", "owner_questions.json")
HIS_HOLDS = ("owner_call",)
ACCEPTED_RESULT = re.compile(r"result\.(.+)\.json$")   # designer_stage.close_run's rename; bare result.json is not yet read
PASSES_TTL = 30     # s: the board asks once per item per refresh; a long-lived board must still see a new result
_passes_memo = {}
_certs_memo = {}


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
    if h.get("kind") in HIS_HOLDS or (h.get("kind") == "game" and run_store.flyer_hold(h.get("why"))):
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
        return {"DESIGNER_TURNS_UNMEASURED": "Designer turns UNMEASURED (%s): read designer_stage.py turns" % str(e)}
    out = {(t.get("item") or "DESIGNER_%s" % str(t["mod"]).upper()): DS.turn_line(t) for t in turns}
    if bad:
        out["DESIGNER_TURNS_UNMEASURED"] = "Designer turns UNMEASURED for %s" % "; ".join(bad)
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


def _conductor_lock_ok(v):
    """The Conductor window's lock certifies too (owner 2026-11-19, conductor_acts.lock_problem); an unread ledger is
    False, so the row stays his."""
    try:
        import concept_tree as CT
        import conductor_acts as CA
        return CA.lock_problem(v, CT.owner_events(CT.REPO)) is None
    except Exception:       # noqa: BLE001
        return False


def read_certified(root):
    """-> {first-touch pass ids whose concept folder holds a Design Version HE locked}, or None when `root` cannot be read.
    A folder answers for its own pass id and for its stage.json item when that is a first-touch row."""
    try:
        names = os.listdir(root)
    except OSError:
        return None
    out = set()
    for n in names:
        d = os.path.join(root, n)
        try:
            with open(os.path.join(d, "version", "VERSION.json"), encoding="utf-8") as f:
                v = json.load(f)
        except (OSError, ValueError):
            continue
        if not isinstance(v, dict) or v.get("state") != "locked" or v.get("locked_by") not in ("owner", "conductor"):
            continue
        if v.get("locked_by") == "conductor" and not _conductor_lock_ok(v):
            continue
        out.add(first_touch.pass_item_id(n))
        try:
            with open(os.path.join(d, "stage.json"), encoding="utf-8") as f:
                item = json.load(f).get("item")
        except (OSError, ValueError, AttributeError, TypeError):
            item = None
        if isinstance(item, str) and item.endswith(first_touch.SUFFIX):
            out.add(item)
    return out


def certified_ids(root=None):
    """read_certified on the same concepts root designer_passes reads, for PASSES_TTL seconds."""
    try:
        import designer_stage as DS
        root = root or DS.concepts_root()
    except Exception:       # noqa: BLE001  an unread answer keeps the rows listed
        return None
    at, got = _certs_memo.get(root, (None, None))
    if at is None or time.monotonic() - at > PASSES_TTL:
        got = read_certified(root)
        _certs_memo[root] = (time.monotonic(), got)
    return got


def certified(it, certs=None):
    """True for a first-touch pass item whose Design Version he locked. An unread answer is False: it stays his."""
    iid = getattr(it, "id", None)
    if not iid or not iid.endswith(first_touch.SUFFIX):
        return False
    certs = certified_ids() if certs is None else certs
    return certs is not None and iid in certs


def awaiting_designer(it, passes=None):
    """True for a first-touch pass item with no Designer pass to certify yet. An unread answer is False: it stays his."""
    iid = getattr(it, "id", None)
    if not iid or not iid.endswith(first_touch.SUFFIX):
        return False
    passes = designer_passes() if passes is None else passes
    return passes is not None and iid not in passes


def later(it, items=None, now=None):
    """-> True when the item's turn has not come: a dated wait ahead, or a block on a ticket that is still open. A date
    that cannot be read and a blocker that was never filed are False: the row stays on his list. items None: no block is
    read (the caller has no ledger)."""
    wu = _epoch(getattr(it, "wait_until", None)) if getattr(it, "wait_until", None) else None
    if wu is not None and wu > (time.time() if now is None else now):
        return True
    if not getattr(it, "blocked", False) or getattr(it, "blocked_kind", None) not in (None, "item"):
        return False
    ons = (getattr(it, "blocked_on", None),) + tuple(getattr(it, "blocked_also", None) or ())
    return any(b and b in (items or {}) and items[b].open for b in ons)


def is_his(it, rs, evs=None, turns=None, passes=None, certs=None, items=None, now=None):
    """evs: the ledger's events, when the caller has them: without them `answered` cannot be told and stays on the list.
    turns: designer_turns(); an item whose Designer turn waits on him is his whatever the ledger routes.
    passes: designer_passes(), read here when not given (only for a first-touch row); certs: certified_ids(), likewise."""
    if turns and getattr(it, "id", None) in turns:
        return True
    return routed(it) and tooling_hold(rs) is None and not answered(it, evs) and not awaiting_designer(it, passes) \
        and not certified(it, certs) and not later(it, items, now)


def needs_you(items, rel, questions=None, evs=None, turns=None, passes=None, certs=None, now=None):
    """-> {"count", "lines": [{"item", "q"}], "topics", "answered", "awaiting_designer", "certified", "later", "text"}, sorted by item id (stable hashes).
    turns: designer_turns() (None: not read here; the board and the CLI pass it). A waiting turn's line replaces the
    item's own question, and a turn whose item the ledger does not hold is its own line."""
    questions = load_questions() if questions is None else questions
    turns = turns or {}
    line = lambda iid, it: {"item": iid, "q": (turns.get(iid) or questions.get(iid) or it.title or iid).strip()}  # noqa: E731
    lines = [line(iid, it) for iid, it in sorted(items.items()) if is_his(it, rel.get(iid), evs, passes=passes,
             certs=certs, items=items, now=now) or iid in turns]
    lines += [{"item": iid, "q": q} for iid, q in sorted(turns.items()) if iid not in items]
    lines.sort(key=lambda x: x["item"])
    gone = [line(iid, it) for iid, it in sorted(items.items()) if iid not in turns and routed(it)
            and tooling_hold(rel.get(iid)) is None and answered(it, evs)]
    waiting = [line(iid, it) for iid, it in sorted(items.items()) if iid not in turns and routed(it)
               and tooling_hold(rel.get(iid)) is None and not answered(it, evs) and awaiting_designer(it, passes)]
    sealed = [line(iid, it) for iid, it in sorted(items.items()) if iid not in turns and routed(it)
              and tooling_hold(rel.get(iid)) is None and not answered(it, evs) and not awaiting_designer(it, passes)
              and certified(it, certs)]
    ahead = [line(iid, it) for iid, it in sorted(items.items()) if iid not in turns and later(it, items, now)
             and is_his(it, rel.get(iid), evs, passes=passes, certs=certs, items={}, now=float("inf"))]
    text = "" if not lines else "%d %s: %s" % (len(lines), "thing" if len(lines) == 1 else "things",
                                               " · ".join(x["q"] for x in lines))
    return {"count": len(lines), "lines": lines, "text": text, "topics": fold(lines), "answered": gone,
            "awaiting_designer": waiting, "certified": sealed, "later": ahead}


# ---- the owner's one view (design/specs/2026-11-23-owner-one-view/boundary.md) ------------------------------------
# A shared view is fresh while it is younger than this. Danger: a reader would show rows of a build that stopped.
# Evidence: Maturation Now writes the view each minute, and the live promise on view.json asks five minutes.
VIEW_FRESH_S = 300
UNM = "UNMEASURED"


def _days(t, now):
    """A whole-day age ('<1d', '3d'): no minutes, so two builds a minute apart print the same row (the pages' rule)."""
    if not isinstance(t, (int, float)):
        return UNM
    d = int(max(0, now - t) // 86400)
    return "<1d" if d < 1 else "%dd" % d


def _epoch(v):
    import datetime as dt
    try:
        t = dt.datetime.fromisoformat(str(v).replace("Z", "+00:00"))
    except ValueError:
        return None
    return (t if t.tzinfo else t.replace(tzinfo=dt.timezone.utc)).timestamp()


def ours(needs, items, now):
    """-> [{"item", "q", "age"}]: what he answered and is now ours to do (needs_you's "answered"), oldest first."""
    rows = []
    for x in (needs or {}).get("answered") or []:
        it = (items or {}).get(x["item"])
        t = _epoch(getattr(it, "created_at", None)) if it is not None else None
        rows.append({"item": x["item"], "q": x["q"], "age": _days(t, now), "_t": t if t is not None else 9e18})
    rows.sort(key=lambda r: (r["_t"], r["item"]))
    return [{k: v for k, v in r.items() if k != "_t"} for r in rows]


def _clip(s, n):
    s = " ".join(str(s or "").split())
    return s if len(s) <= n else s[:n - 1].rstrip() + "…"


def home_line(home):
    """'not filed anywhere: N (source n, ...; UNMEASURED: ...)', or UNMEASURED, never 0, when nothing could be read."""
    if not isinstance(home, dict):
        return "not filed anywhere: %s (no reading yet)" % UNM
    n = home.get("no_home")
    parts = ["%s %d" % kv for kv in (home.get("by_source") or {}).items()]
    unm = list(home.get("unmeasured") or [])
    tail = "; ".join(x for x in (", ".join(parts), ("%s: %s" % (UNM, ", ".join(unm))) if unm else "") if x)
    return "not filed anywhere: %s%s" % (UNM if n is None else n, (" (%s)" % tail) if tail else "")


def one_view(his, ours_rows, home, fmt="md"):
    """-> the block MATURATION_NOW shows (one-view-shows-his-ours-and-the-count): his rows, our rows oldest first with their
    age, and the count of needs not filed anywhere beside them. fmt "md": Markdown lines joined by newlines; "html": one
    line of HTML with no blank line in it (Typora)."""
    import html as H
    his, ours_rows = list(his or []), list(ours_rows or [])
    hl = home_line(home)
    if fmt == "html":
        e = H.escape
        rows = "".join("<div>• %s <span style=\"color:#98a1af;font-size:11px\">%s</span></div>" % (e(x["q"][:130]), e(x["item"]))  # cut-ok: compact dashboard display of the saved question
                       for x in his) or "<div>Nothing waits on you.</div>"
        tail = ""
        if ours_rows:
            tail = ('<div style="color:#98a1af;font-size:12px;margin-top:6px">%d you answered; the next move is ours, '
                    'oldest first: %s</div>' % (len(ours_rows), e(", ".join("%s (%s)" % (x["item"], x.get("age") or UNM)
                                                                           for x in ours_rows))))
        return ('<div style="font-weight:bold">NEEDS YOU, %d</div>%s%s<div style="font-size:12px;margin-top:6px">%s</div>'
                % (len(his), rows, tail, e(hl)))
    out = ["**Needs you (%d)** · %s" % (len(his), hl), ""]
    out += ["- %s (`%s`)" % (_clip(x["q"], 200), x["item"]) for x in his] or ["- Nothing waits on you."]
    if ours_rows:
        out += ["", "**You answered; the next move is ours (%d, oldest first)**" % len(ours_rows), ""]
        out += ["- %s (`%s`), %s" % (_clip(x["q"], 160), x["item"], x.get("age") or UNM)
                for x in ours_rows]
    return "\n".join(out)


def view_dir(create=True):
    d = os.environ.get("RM_OWNER_VIEW_DIR")
    if not d:
        import doorbell
        d = os.path.join(doorbell.state_dir(), "owner_view")
    if create:
        os.makedirs(d, exist_ok=True)
    return d


def view_path(create=True):
    return os.path.join(view_dir(create), "view.json")


def fresh_view(v, now, fresh_s=VIEW_FRESH_S):
    """-> v when it is a view younger than fresh_s, else None."""
    if not isinstance(v, dict) or not isinstance(v.get("at"), (int, float)) or not (0 <= now - v["at"] < fresh_s):
        return None
    return v


def test_refusal(path=None):
    """-> why a write to the shared owner-view files is refused, or None. A test process (test_process.under_test, the
    one definition) never writes the real ones: a selftest builds Maturation Now live, and its view would replace
    the real one. An explicit path or RM_OWNER_VIEW_DIR is a test's own place and is allowed."""
    if path or os.environ.get("RM_OWNER_VIEW_DIR"):
        return None
    import test_process
    return "a test process does not write the shared view (test_process.under_test)" if test_process.under_test() else None


def write_view(his, ours_rows, home, now, path=None):
    """The view Maturation Now built (its live promise reads this file). A write that fails is returned, not raised."""
    refused = test_refusal(path)
    if refused:
        return refused
    path = path or view_path()
    try:
        with open(path + ".tmp", "w", encoding="utf-8") as f:
            json.dump({"at": now, "his": his, "ours": ours_rows, "home": home}, f, indent=1, ensure_ascii=False)
        os.replace(path + ".tmp", path)
        return None
    except OSError as e:
        return "%s: %s" % (type(e).__name__, e)


def read_view(now, path=None, fresh_s=VIEW_FRESH_S):
    """-> the shared view while it is younger than fresh_s, else None."""
    try:
        with open(path or view_path(create=False), encoding="utf-8") as f:
            v = json.load(f)
    except (OSError, ValueError):
        return None
    return fresh_view(v, now, fresh_s)


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
            print("%s\t%s\t%s" % (iid, kind, why))
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
    print("%d first touches certified by his own version lock (close them)" % len(n["certified"]))
    for x in n["certified"]:
        print("certified\t%s" % x["item"])
    print("%d his later (a date ahead, or behind an open ticket)" % len(n["later"]))
    for x in n["later"]:
        print("later\t%s\t%s" % (x["item"], x["q"]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
