#!/usr/bin/env python3
"""blind_view.py — the queue and item notes as a token-blind role may read them (review W, L1 + L3).

The token-blind roles (Conductor, Producer, Arbiter, Auditor, Innovator: every role whose schedule entry is not
`token_aware: true`) must never read a token, account, runway, quota, week, burn, cap or budget value (owner,
2026-10-27). Code routes are guarded, but titles and notes are written by hand, and ledger events are append-only:
a leaking note can never be edited away. So a blind role reads the queue and an item's notes through this view,
never through raw `rimflow queue` / `rimflow show`.

Allow-list, never a word denylist (lesson of 2026-10-27): the view prints only fields it knows are safe — id, state,
kind, needs, row, owner, a BLOCKED flag, event verbs and their times. Free text (titles, notes, block reasons, the
one-line spec summary) passes only through redact(): any upper-case id naming accounts, any number that sits within NEAR_TOKENS words of an account,
token, quota, cap, budget, runway, burn, spend, usage, limit or week word, any number with a k / M / % / tokens /
$ unit, and any number of 10,000 or more is replaced with "[…]". Dates, clock times and hex shas pass.
An item about accounts by its id or kind (withheld()) is withheld whole: the queue counts it and names nothing, `show`
prints only that it is withheld, and its id is redacted out of any other item's free text.

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

MASK = "[…]"
NEAR_TOKENS = 8                      # words either side of a sensitive word in which a number is redacted
BIG_NUMBER = 10000                   # a bare number this large is a token count until proved otherwise
# a word part (split at _ . - and case) that makes a number near it sensitive; matched as a prefix of the part
SENSITIVE_PREFIXES = ("account", "token", "quota", "budget", "runway", "burn", "spend", "spent", "usage", "limit",
                      "week", "pct", "percent", "economy")
SENSITIVE_WORDS = {"cap", "caps", "capped", "capping", "capx"}
# an item whose id starts with one of these, or whose id or kind has one of these parts, is about accounts: withheld
# whole. Kept narrow on purpose: CAP, BURN, RUNWAY and BUDGET are ordinary game words here (a wildlife cap, Burn
# weather, RM_RunwayBloom, a frame budget), and withholding hides real work from the Conductor; their numbers are
# redacted near the word anyway.
WITHHELD_ID_PREFIXES = ("OPS_", "OPERATIONS_")
WITHHELD_ID_PARTS = {"ACCOUNT", "ACCOUNTS", "TOKEN", "TOKENS", "QUOTA", "QUOTAS", "SPEND"}
WITHHELD_KIND_PARTS = WITHHELD_ID_PARTS | {"OPS", "OPERATIONS", "BUDGET", "BUDGETS", "RUNWAY", "BURN"}

_TOKEN_RE = re.compile(
    r"(?P<date>\d{4}-\d{2}-\d{2}(?:[T ]\d{2}:\d{2}(?::\d{2})?(?:\.\d+)?Z?)?)"
    r"|(?P<time>\b\d{1,2}:\d{2}(?::\d{2})?Z?\b)"
    r"|(?P<unit>\$\s?\d+(?:[.,]\d+)*(?:\s?[kKM])?|\d+(?:[.,]\d+)*(?:\s?(?:[kKM]|%|pct|percent|tokens?|tok))(?![A-Za-z0-9]))"
    r"|(?P<word>[A-Za-z0-9_]*[A-Za-z_][A-Za-z0-9_]*)"
    r"|(?P<num>\d+(?:[.,]\d+)*)")


def _parts(word):
    """`daily_token_cap` -> [daily, token, cap]; `sessionWeekPct` -> [session, week, pct]."""
    out = []
    for p in re.split(r"[_\d]+", word):
        out += [q.lower() for q in re.findall(r"[A-Z]?[a-z]+|[A-Z]+(?![a-z])", p)]
    return out


def sensitive_word(word):
    return any(p in SENSITIVE_WORDS or p.startswith(SENSITIVE_PREFIXES) for p in _parts(word))


_ID_FRAGMENT_RE = re.compile(r"_[A-Z0-9]{3,6}")


def _account_id(word):
    """An item id (or an alarm-id fragment like `_C01D`) that names accounts, even one not in this world (closed,
    or in another clone): an upper-case id that withheld() would withhold by id, or a bare `_XXXX` id suffix."""
    if _ID_FRAGMENT_RE.fullmatch(word):
        return True
    return "_" in word and word.upper() == word and _account_item_id(word)


def _account_item_id(iid):
    return iid.upper().startswith(WITHHELD_ID_PREFIXES) or bool(set(re.split(r"[^A-Z]+", iid.upper()))
                                                                 & WITHHELD_ID_PARTS)


def _number(s):
    try:
        return float(s.replace(",", ""))
    except ValueError:
        return None


def redact(text, hide_ids=()):
    """Pure. Free text -> the same text with every account/cap number replaced by MASK, and every id in hide_ids
    (items withheld from blind roles) replaced by MASK. None -> ""."""
    if not text:
        return ""
    text = str(text)
    toks = [m for m in _TOKEN_RE.finditer(text)]
    hot = [i for i, m in enumerate(toks) if m.lastgroup == "word" and sensitive_word(m.group())]
    cut = []
    for i, m in enumerate(toks):
        g = m.lastgroup
        if g == "unit":
            cut.append(m.span())
        elif g == "num":
            v = _number(m.group())
            if (v is not None and v >= BIG_NUMBER) or any(abs(i - h) <= NEAR_TOKENS for h in hot):
                cut.append(m.span())
        elif g == "word" and (m.group() in hide_ids or _account_id(m.group())):
            cut.append(m.span())
    out, pos = [], 0
    for a, b in cut:
        out.append(text[pos:a])
        out.append(MASK)
        pos = b
    out.append(text[pos:])
    return "".join(out)


def withheld(it):
    """Is this item about accounts? By its id or kind only: a title word is no guide ("accounted for", "quotas" of a
    review), and a withheld item is work the Conductor cannot see. Its title's numbers are redacted either way."""
    if _account_item_id(it.id or ""):
        return True
    return bool(set(re.split(r"[^A-Z]+", (it.kind or "").upper())) & WITHHELD_KIND_PARTS)


def _load():
    from rimflow import model
    evs = model.read()
    return evs, model.replay(evs)


def hidden_ids(world):
    return {i.id for i in world.items.values() if withheld(i)}


def queue_text(world, seat, target="v1", ctx=None, summaries=True):
    """-> the blind queue of one seat: the same sections, in the same order, as `rimflow queue <SEAT>`, with
    allow-listed fields only and redacted free text."""
    from rimflow import render
    hide = hidden_ids(world)
    ranked, sections = render.view_sections(world, seat, target, ctx)
    n_hidden = len({i.id for i in world.items.values() if i.owner == seat and i.open and i.id in hide})
    out = ["# %s queue, blind view" % seat,
           "Ids, states, kinds and needs. Titles, notes and reasons are redacted: a number about accounts or caps "
           "reads %s. %d open item(s) about accounts are withheld (Operations' alone)." % (MASK, n_hidden), ""]

    def item(it):
        lines = ["## %s %s" % (it.id, redact(it.title, hide)),
                 "state: %s%s   kind: %s   needs: %s   row: %s" % (
                     it.state, " (BLOCKED)" if it.blocked else "", it.kind or "task", it.needs,
                     it.row if it.row not in (None, "") else "unassigned")]
        if it.blocked:
            lines.append("blocked: %s" % redact(it.blocked_reason or "unexplained", hide))
        if summaries:
            lines.append("summary: %s" % redact(render.summary(it.id), hide))
        return lines + [""]
    groups = [("NEXT", ranked)] + [(t, items) for t, items, _n, _x in sections]
    for title, items in groups:
        items = [i for i in items if i.id not in hide]
        if not items:
            continue
        out.append("# %s (%d)" % (title, len(items)))
        out.append("")
        for it in items:
            out += item(it)
    return "\n".join(out) + "\n"


def show_text(evs, world, iid, last=10, prefix=None):
    """-> one item's allow-listed fields and its last `last` notes (only those starting `prefix`, if given),
    free text redacted. A withheld item prints that it is withheld and nothing else."""
    it = world.items.get(iid)
    if it is None:
        return "%s: no such item\n" % iid
    hide = hidden_ids(world)
    if iid in hide:
        return "%s: withheld from the blind view (an item about accounts: Operations' alone)\n" % iid
    out = ["%s   state %s%s   kind %s   owner %s   needs %s" % (
        it.id, it.state, " (BLOCKED)" if it.blocked else "", it.kind or "task", it.owner, it.needs),
        "title: %s" % redact(it.title, hide)]
    if it.blocked:
        out.append("blocked: %s" % redact(it.blocked_reason or "unexplained", hide))
    if it.closed_sha:
        out.append("closed at %s" % it.closed_sha)
    if it.superseded_by:
        out.append("superseded by %s" % (MASK if it.superseded_by in hide else it.superseded_by))
    notes = [evs[i] for i in it.history if evs[i].get("event") == "note"]
    if prefix:
        notes = [e for e in notes if (e.get("text") or "").lstrip().startswith(prefix)]
    shown = notes[-last:] if last else notes
    out.append("--- notes: last %d of %d%s (redacted) ---" % (len(shown), len(notes),
                                                              " starting %r" % prefix if prefix else ""))
    for e in shown:
        out.append("%s %s: %s" % (e.get("ts"), e.get("seat"), redact(e.get("text"), hide)))
    others = [evs[i] for i in it.history if evs[i].get("event") != "note"]
    out.append("--- other events: %d (verb, time, seat only) ---" % len(others))
    for e in others[-last:] if last else others:
        out.append("%s %s %s" % (e.get("ts"), e.get("event"), e.get("seat")))
    return "\n".join(out) + "\n"


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    q = sub.add_parser("queue", help="a seat's queue, blind")
    q.add_argument("seat")
    s = sub.add_parser("show", help="one item's fields and notes, blind")
    s.add_argument("id")
    s.add_argument("--last", type=int, default=10, help="notes to print (0 = all; default 10)")
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
