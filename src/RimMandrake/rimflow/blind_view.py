#!/usr/bin/env python3
"""blind_view.py — the queue and item notes as a token-blind role may read them (review W, L1 + L3).

The token-blind roles (every role but Operations; owner, 2026-10-27: only Operations is token-aware) must never read
a token, account, runway, quota, week, burn, cap or budget value. Titles, notes, block reasons and summaries are
written by hand and ledger events are append-only: a leaking note can never be edited away. So a blind role reads
the queue and an item through this view, never through raw `rimflow queue` / `rimflow show`.

A CLOSED type, not redaction (BLINDVIEW_BUILD_CLOSED_TYPE_LEAKPROOF): the page is a contracts.blind.BlindQueue or
BlindItemPage, built only by contracts.blind.project_queue / project_item and written by render_queue /
render_item behind a page guard that fails closed. Free text is never shown at all: an item is its id, state, kind,
needs, row, owner and BLOCKED flag; a note is its time, its seat, the known item ids and the shas it names, and
whether it starts with --prefix. (The old word-list redactor is gone: a phrasing nobody had thought of got through.)
An item about accounts by its id or kind (withheld()) is withheld whole: the queue counts it and names nothing, and
`show` prints only that it is withheld.

Usage:
  python3 src/RimMandrake/rimflow/blind_view.py queue BENCH
  python3 src/RimMandrake/rimflow/blind_view.py show <ID> [--last N] [--prefix "REPLAN REQUEST"]
"""
import argparse
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
if os.path.dirname(HERE) not in sys.path:
    sys.path.insert(0, os.path.dirname(HERE))

from contracts import blind_core as C  # noqa: E402  (stdlib only)

# an item whose kind has one of these parts is about accounts: withheld whole. Kept narrow on purpose: CAP, BURN,
# RUNWAY and BUDGET are ordinary game words in an ID (a wildlife cap, Burn weather, RM_RunwayBloom), and withholding
# hides real work from the Conductor; a kind is a classification, so there they do mean accounts.
WITHHELD_KIND_PARTS = C.WITHHELD_ID_PARTS | {"OPS", "OPERATIONS", "BUDGET", "BUDGETS", "RUNWAY", "BURN"}


def withheld(it):
    """Is this item about accounts? By its id or kind only: a title word is no guide, and a withheld item is work the
    Conductor cannot see."""
    if C.account_item_id(it.id or ""):
        return True
    return bool(set(re.split(r"[^A-Z]+", (it.kind or "").upper())) & WITHHELD_KIND_PARTS)


def _load():
    from rimflow import model
    evs = model.read()
    return evs, model.replay(evs)


def known_ids(world):
    return {i.id for i in world.items.values() if not withheld(i)}


def hidden_ids(world):
    return {i.id for i in world.items.values() if withheld(i)}


def queue_text(world, seat, target="v1", ctx=None):
    """-> the blind queue of one seat: the same sections, in the same order, as `rimflow queue <SEAT>`, as a
    contracts.blind.BlindQueue (ids, states, kinds, needs, rows; no text)."""
    from rimflow import render
    from contracts import blind as BL
    hide = hidden_ids(world)
    ranked, sections = render.view_sections(world, seat, target, ctx)
    groups = [("NEXT", ranked)] + [(t, items) for t, items, _n, _x in sections]
    n_hidden = {i.id for i in world.items.values() if i.owner == seat and i.open and i.id in hide}
    return BL.render_queue(BL.project_queue(seat, groups, frozenset(hide), n_hidden))


def show_text(evs, world, iid, last=10, prefix=None):
    """-> one item as a contracts.blind.BlindItemPage: its fields and its last `last` notes (only those starting
    `prefix`, if given) as references, never their text. A withheld item prints only that it is withheld."""
    from contracts import blind as BL
    it = world.items.get(iid)
    if it is None or C.item_id_problem(iid) == "grammar":
        return "no such item\n"
    notes = [evs[i] for i in it.history if evs[i].get("event") == "note"]
    others = [evs[i] for i in it.history if evs[i].get("event") != "note"]
    page = BL.project_item(it, notes, others, frozenset(hidden_ids(world)), frozenset(known_ids(world)), last, prefix)
    return BL.render_item(page)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    q = sub.add_parser("queue", help="a seat's queue, blind")
    q.add_argument("seat")
    s = sub.add_parser("show", help="one item's fields and note references, blind")
    s.add_argument("id")
    s.add_argument("--last", type=int, default=10, help="notes to list (0 = all; default 10)")
    s.add_argument("--prefix", help="only notes whose text starts with this (e.g. 'REPLAN REQUEST')")
    a = ap.parse_args(argv)
    evs, world = _load()
    if a.cmd == "queue":
        sys.stdout.write(queue_text(world, a.seat.upper()))
    else:
        sys.stdout.write(show_text(evs, world, a.id, a.last, a.prefix))
    return 0


if __name__ == "__main__":
    sys.exit(main())
