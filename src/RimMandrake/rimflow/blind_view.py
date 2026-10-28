#!/usr/bin/env python3
"""blind_view.py — the queue and item notes as a token-blind role may read them (review W, L1 + L3).

The token-blind roles (every role but Operations; owner, 2026-10-27: only Operations is token-aware) must never read
a token, account, runway, quota, week, burn, cap or budget value. Titles, notes, block reasons and summaries are
written by hand and ledger events are append-only: a leaking note can never be edited away. So a blind role reads
the queue and an item through this view, never through raw `rimflow queue` / `rimflow show`.

A CLOSED type, not redaction (BLINDVIEW_BUILD_CLOSED_TYPE_LEAKPROOF): the page is a contracts.blind.BlindQueue or
BlindItemPage, built only by contracts.blind.project_queue / project_item and written by render_queue /
render_item through the allowlist Page (contracts.blind_core.Page): every token on the page is a template word, a
code-defined enum label, a ledger item id, a registered seat name or a number of a declared measure, and a final
whole-page gate refuses the page otherwise (fails closed). Free text is never shown at all: an item is its id, state,
kind, needs, row, owner and BLOCKED flag; a note is its time, its seat, the known item ids, a handle E<n> for each sha
it names, and whether it starts with --prefix. Shas never print raw: the E<n> -> sha map is stored under
HANDLES_DIR (Operations' scratch), keyed by the page's sha256. (The old word-list redactor is gone: a phrasing nobody had thought of got through.)
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

# Where a page's handle map (E<n> -> sha / evidence path) is kept: Operations' scratch, not the page.
HANDLES_DIR = os.environ.get("RIMFLOW_BLIND_HANDLES", "/mnt/d/ClaudeWork/rimmandrake/ops_watch/blind_handles")

_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))    # the clone: the sha resolver's repo

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
    ids = BL.Identity(known=frozenset(known_ids(world)), hidden=frozenset(hide))
    return BL.render_queue(BL.project_queue(seat, groups, ids, n_hidden))


def show_text(evs, world, iid, last=10, prefix=None):
    """-> one item as a contracts.blind.BlindItemPage: its fields and its last `last` notes (only those in the closed
    category `prefix`, one of contracts.blind.NOTE_CATEGORIES, if given) as references, never their text; a sha shows
    only when it resolves to a commit of this repo. A withheld item prints only that it is withheld."""
    from contracts import blind as BL
    it = world.items.get(iid)
    if it is None or C.item_id_problem(iid) == "grammar":
        return "no such item\n"
    notes = [evs[i] for i in it.history if evs[i].get("event") == "note"]
    others = [evs[i] for i in it.history if evs[i].get("event") != "note"]
    ids = BL.Identity(known=frozenset(known_ids(world)), hidden=frozenset(hidden_ids(world)))
    page = BL.project_item(it, notes, others, ids, last, category=prefix, resolve=C.git_resolver(_ROOT))
    return BL.render_item(page)


class _Parser(argparse.ArgumentParser):
    """argparse's own error text quotes the bad value (invalid choice: '<value>'): a blind tool's diagnostics are
    fixed text only."""
    def error(self, message):
        self.exit(2, "blind_view: bad arguments (see --help)\n")


def main(argv=None):
    """Every failure prints fixed text: an exception's message can quote record text (pydantic's input_value)."""
    try:
        return _main(argv)
    except SystemExit:
        raise
    except Exception:  # noqa: BLE001 - nothing of the error reaches a blind reader
        sys.stderr.write("blind_view: page refused\n")
        return 2


def _main(argv=None):
    ap = _Parser(description=__doc__.split("\n\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    q = sub.add_parser("queue", help="a seat's queue, blind")
    q.add_argument("seat")
    s = sub.add_parser("show", help="one item's fields and note references, blind")
    s.add_argument("id")
    s.add_argument("--last", type=int, default=10, help="notes to list (0 = all; default 10)")
    s.add_argument("--prefix", choices=("REPLAN REQUEST", "CUT LIST", "CUT DECISION", "CUT APPLIED", "CUT"),
                   help="only notes of this closed category (a free-text prefix would be a count oracle)")
    a = ap.parse_args(argv)
    evs, world = _load()
    text = queue_text(world, a.seat.upper()) if a.cmd == "queue" else show_text(evs, world, a.id, a.last, a.prefix)
    handles = getattr(text, "handles", {})
    if handles:                                      # the map goes to Operations' scratch, never to stdout
        try:
            C.store_handles(text, handles, HANDLES_DIR)
        except OSError:
            sys.stderr.write("blind_view: handle map not stored\n")
    sys.stdout.write(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
