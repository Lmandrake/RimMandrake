#!/usr/bin/env python3
"""relentless_pool_why.py - why each of Operations' system items is or is not in the Relentless pool. Read-only.

RELENTLESS_POOL_DIAGNOSE_SYSTEM_NEVER_ENROLS (2026-11-05): a probe found 74 system items outside the pool and only said
`not-in-pool`. This names, per item, every clause of the pool's own filters that keeps it out (`eligible`, the target,
the concept gate, the first-touch hold), and checks the naming against the real `Effects.pool_order`: an item out of the
pool with no clause, or in it with one, is UNEXPLAINED, and `--strict` exits 1 on it. Diagnosis by class:
design/RimMandrake/relentless_pool_why_2026-11-05.md.

The system ids are Operations' ledger classifier (ops_health.system_ids), the list `health_order` falls back to; `--verdict`
reads Operations' fresh verdict instead. Nothing is filed: the first-touch pass a held item owes is reported, never filed.

  relentless_pool_why.py [--strict] [--items] [--verdict]
"""
import argparse
import collections
import json
import os
import shutil
import sys
import tempfile
import time

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, HERE)
import relentless as R  # noqa: E402

PARKED_MARK = "PARKED by owner"


def reasons(it, w, r, now, refused=None, first_touch=None, words=()):
    """-> [clause, ...] keeping ledger item `it` out of the pool, [] when the pool's filters admit it. The clauses are
    pool_order's, in its order; `refused(id)` is the concept gate (asked of mods only, as pool_order does) and
    `first_touch(id)` the Designer hold; `words` the ids the other seat has said something about the books have not heard
    (Effects.seat_words; None: its tree is unreadable). Pure but for the two callables."""
    if it is None:
        return ["not_filed"]
    out = []
    if it.owner not in r["pool_seats"]:
        out.append("owner=%s" % it.owner)
    if it.state not in ("proposed", "ready"):
        out.append("state=%s" % it.state)
    if R.pkg("priority").block_holds(w, it, int(now)):
        out.append("parked_by_owner" if PARKED_MARK in (it.blocked_reason or "") else "blocked")
    if it.needs == "owner" or not (it.needs in r["pool_needs"] or it.needs in R.relentless_game.pool_needs(r)):
        out.append("needs=%s" % it.needs)
    if getattr(it, "kind", None) in r.get("pool_kinds_exclude", []):
        out.append("kind=%s" % it.kind)
    if R.pool_excluded(it.id, r):
        out.append("pool_excluded")
    if R.hand_check(it, r):
        out.append("hand_check")
    if getattr(it, "lease", None):
        out.append("lease")
    if it.owner == R.foreign_seat(r) and not R.foreign_ok(it, r):
        out.append("foreign")
    elif it.owner == R.foreign_seat(r) and (words is None or it.id in words):
        out.append("foreign_unpublished")
    if it.target not in (None, *(r.get("pool_targets") or ["v1"])):
        out.append("target=%s" % it.target)
    if not out and getattr(it, "kind", None) == "mod" and refused and refused(it.id):
        out.append("concept_refused")
    if not out and first_touch and first_touch(it.id):
        out.append("first_touch")
    return out


def primary(rs):
    """The class an item is tallied under: its first clause, with the value kept for state/owner/kind/needs."""
    return rs[0] if rs else "in_pool"


def survey(r=None, verdict=False, now=None):
    """-> (rows [(place, id, [clauses], in_pool, note)], why): every system item, against the real pool_order."""
    r = r or R.rules()
    now = time.time() if now is None else now
    tmp = tempfile.mkdtemp(prefix="pool_why_")      # Store makes its dirs: a throwaway one, removed at the end
    try:
        return _survey(r, verdict, now, R.Effects(r, R.Store(base=tmp)))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def _survey(r, verdict, now, fx):
    fx.books = REPO

    class _Refused:      # first_touch_hold files an owed pass through rimflow: a read-only survey files nothing
        returncode, stdout, stderr = 0, "", ""
    fx.rimflow = lambda *a, **k: _Refused()
    utils = os.path.join(os.path.dirname(HERE), "Utils")
    if utils not in sys.path:
        sys.path.insert(0, utils)
    import ops_health

    def fallback():
        with open(os.path.join(utils, "ops_watch_rules.json"), encoding="utf-8") as f:
            return ops_health.system_ids(fx.ledger_items()[1], json.load(f), REPO)
    v, vwhy = ops_health.read_verdict() if verdict else (None, "ledger classifier (no verdict read)")
    fx._health = R.health_order(v, vwhy, fallback)
    order, w = fx.pool_order(r)
    pool = set(order)
    words = fx.seat_words()

    def refused(i):     # the concept gate alone: fx.concept_refusal also answers the first-touch hold, named apart here
        return R.concept_refused(fx.books, i, getattr(w.items.get(i), "kind", None))
    rows = []
    for i, place in sorted(fx.first.items(), key=lambda kv: kv[1]):
        it = w.items.get(i)
        rs = reasons(it, w, r, now, refused, fx.first_touch_hold, words)
        note = ""
        if (not rs) != (i in pool):
            note = "UNEXPLAINED: %s" % ("out of the pool with no clause" if i not in pool else "in the pool despite " + ",".join(rs))
        elif "first_touch" in rs:
            note = fx.first_touch_hold(i) or ""
        elif "blocked" in rs or "parked_by_owner" in rs:
            note = (it.blocked_reason or "")[:100]
        rows.append((place, i, rs, i in pool, note))
    return rows, fx._health["why"]


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.strip().splitlines()[0])
    ap.add_argument("--strict", action="store_true", help="exit 1 when any item is UNEXPLAINED")
    ap.add_argument("--items", action="store_true", help="one line per system item")
    ap.add_argument("--verdict", action="store_true", help="Operations' fresh verdict names the system items")
    a = ap.parse_args(argv)
    rows, why = survey(verdict=a.verdict)
    tally = collections.Counter(primary(rs) for _, _, rs, _, _ in rows)
    bad = [x for x in rows if x[4].startswith("UNEXPLAINED")]
    print("system items: %d (%s); in pool %d; out %d; UNEXPLAINED %d" % (
        len(rows), why, sum(1 for x in rows if x[3]), sum(1 for x in rows if not x[3]), len(bad)))
    for k, n in tally.most_common():
        print("  %4d %s" % (n, k))
    for place, i, rs, inp, note in (rows if a.items else bad):
        print("%4d %s %s%s" % (place, i, "+".join(rs) or "in_pool", ("  | " + note) if note else ""))
    return 1 if a.strict and bad else 0


if __name__ == "__main__":
    sys.exit(main())
