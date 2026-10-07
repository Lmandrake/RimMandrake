#!/usr/bin/env python3
"""rimflow/reconcile.py — join the ledger with git before an item is offered as work.

Rimflow redesign STEP 1 (owner's build order, 2026-10-06: "In order, 1, 2, 3, 4" — git
check before `next` offers work comes first). Design: `design/RimMandrake/
rimflow_gpt_review_2026-10-07.md` §2 "Make `next` a guarded dispatcher".

WHAT IT DECIDES, PER OFFERED ITEM
=================================
    reconcile  commits on the published ref name the item (subject, `Closes:`,
               `Implemented:`) or are cited in its notes, and no `reconcile` event has
               judged them  ->  offer "RECONCILE <ID>: commits <shas>", not "build this"
    complete   the standing verdict is `complete` and nothing new arrived  ->  NOT
               offered as build work (it is still open: acceptance/close is separate,
               and step 2's `built` state is where it will live)
    partial    the standing verdict is `partial`  ->  offered, with its `remaining` line
    build      nothing in git, or every commit judged `unrelated`  ->  offered as before

⛔ A subject match is a TRIGGER, never an auto-close. Nothing in this module writes the
ledger or changes a state; `priority.rank()` stays pure and unchanged. This module only
re-reads its output.

🔑 "Standing verdict" = the LAST `complete`/`partial` verdict. `unrelated` only clears
the commits it names; it never revokes an earlier `complete`. A verdict covers exactly
the shas it lists, so a NEW commit naming the item re-triggers a reconcile.
"""
try:
    from . import gitindex
except ImportError:                                         # script invocation
    import os
    import sys
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from rimflow import gitindex                            # noqa: E402

KINDS = ("reconcile", "complete", "partial", "build")


class Assessment(object):
    __slots__ = ("item", "kind", "unjudged", "standing", "ref", "head")

    def __init__(self, item, kind, unjudged, standing, ref, head):
        self.item, self.kind, self.unjudged = item, kind, unjudged
        self.standing, self.ref, self.head = standing, ref, head

    def __repr__(self):
        return "<Assessment %s %s %s>" % (self.item.id, self.kind,
                                          [m.short for m in self.unjudged])


def _judged(sha, judged):
    return any(sha.startswith(j) or j.startswith(sha) for j in judged)


def evidence(item, index):
    """-> [gitindex.Match] on the published ref that link to `item`, oldest first:
    commits NAMING it since its creation, plus commits its notes cite."""
    if index is None:
        return []
    found = {}
    for m in index.matches(item.id, since=item.created_at):
        found[m.sha] = m
    for cited in getattr(item, "cited_shas", ()) or ():
        m = index.resolve(cited)
        if m is not None and m.sha not in found:
            found[m.sha] = m
    return sorted(found.values(), key=lambda m: (m.ts, m.sha))


def assess(item, index):
    """-> Assessment. Pure over (item, index); `index` None means "git unknown", which
    still honours recorded verdicts but never triggers a reconcile."""
    recs = list(getattr(item, "reconciles", ()) or ())
    judged = [s for r in recs for s in r.get("shas", ())]
    unjudged = [m for m in evidence(item, index) if not _judged(m.sha, judged)]
    standing = None
    for r in recs:
        if r.get("verdict") in ("complete", "partial"):
            standing = r
    ref = getattr(index, "ref", None)
    head = getattr(index, "head", None)
    if unjudged:
        kind = "reconcile"
    elif standing and standing["verdict"] == "complete":
        kind = "complete"
    elif standing:
        kind = "partial"
    else:
        kind = "build"
    return Assessment(item, kind, unjudged, standing, ref, head)


def guard(items, index):
    """-> (offers, skipped): `items` (already ranked) as Assessments, order kept.
    `skipped` holds the `complete` ones, which are not offered as build work."""
    offers, skipped = [], []
    for it in items:
        a = assess(it, index)
        (skipped if a.kind == "complete" else offers).append(a)
    return offers, skipped


# ---------------------------------------------------------------------------
# WORDS — shared by `next` and the rendered queue so the two cannot disagree
# ---------------------------------------------------------------------------
def shas(a):
    return " ".join(m.short for m in a.unjudged)


def command(a):
    return ('rimflow reconcile %s --verdict complete|partial|unrelated --sha %s '
            '--remaining "<what is left, one line>"' % (a.item.id, shas(a)))


def headline(a):
    return "RECONCILE %s: commits %s" % (a.item.id, shas(a))


def evidence_lines(a, limit=8):
    out = []
    for m in a.unjudged[:limit]:
        how = {"subject": "subject", "closes": "Closes:", "implemented": "Implemented:",
               "note": "cited in a note"}.get(m.how, m.how)
        out.append("%s  %s  [%s]  %s" % (m.short, m.ts, how, m.subject))
    if len(a.unjudged) > limit:
        out.append("... +%d more" % (len(a.unjudged) - limit))
    return out


def standing_line(a):
    s = a.standing
    if not s:
        return None
    line = "%s per reconcile %s by %s (%s)" % (s["verdict"].upper(), s["ts"], s["seat"],
                                                " ".join(s.get("shas", ())))
    if s.get("remaining"):
        line += " — remaining: %s" % s["remaining"]
    return line


def load_index(events_path=None, write_cache=True):
    """The one place `next` and render get the index; never raises."""
    return gitindex.for_ledger(events_path, write_cache=write_cache)
