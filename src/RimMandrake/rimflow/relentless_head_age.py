#!/usr/bin/env python3
"""relentless_head_age.py - is old, unplaced backlog leading the Relentless pool? Read-only.

FOUNDRY_QUEUE_CULL_CUTOVER_SEPTEMBER_BACKLOG (filed 2026-10-29): 691 unrowed cutover moves sorted oldest-first ahead of
the week's work (owner: "It' also going through VERY old tickets for some reason."). Among items nobody placed, the pool
still sorts oldest first so nothing starves (an old open item is owed work: PIT_SUPERDEEP_COLLAPSE_1 still owes its
acceptance); what keeps old backlog off the head is placement: Operations' system items, the priority list, a Test Pilot
bounce, a raise, this_deployment, a v1 row. This runs the real Effects.pool_order over the books and fails when an
unplaced item precedes a placed one, or the head is unplaced and filed before --before. Health comes from Operations'
ledger classifier (no verdict file read), as relentless_pool_why.py does by default.

  relentless_head_age.py [--before 2026-10-01] [--show 10]
exit 0: holds · 1: unplaced work ahead of placed work, or an unplaced old head · 2: the instrument cannot see
"""
import argparse
import json
import os
import shutil
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import relentless as R  # noqa: E402
import relentless_pool_why as P  # noqa: E402


def placed(it, plist, orders, first, bounce):
    """-> what placed `it` in the order, or None: the keys pool_order sorts on ahead of the filing date."""
    if it.id in first:
        return "system"
    if plist.position(it, orders) <= plist.MAX_ENTRIES:
        return "listed"
    if it.id in bounce:
        return "bounce"
    if it.raised is not None:
        return "raised"
    if it.this_deployment:
        return "this_deployment"
    if R.pkg("priority")._row_key(it)[0] == 0:     # an unparsable row sorts as no row, as pool_order sorts it
        return "row"
    return None


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--before", default="2026-10-01", help="ISO date: older than this is backlog")
    ap.add_argument("--show", type=int, default=10)
    a = ap.parse_args(argv)
    r = R.rules()
    tmp = tempfile.mkdtemp(prefix="head_age_")
    try:
        fx = R.Effects(r, R.Store(base=tmp))
        fx.books = P.REPO

        class _Refused:     # first_touch_hold files an owed pass through rimflow: a read-only probe files nothing
            returncode, stdout, stderr = 0, "", ""
        fx.rimflow = lambda *x, **k: _Refused()
        utils = os.path.join(os.path.dirname(HERE), "Utils")
        sys.path.insert(0, utils)
        import ops_health

        def fallback():
            with open(os.path.join(utils, "ops_watch_rules.json"), encoding="utf-8") as f:
                return ops_health.system_ids(fx.ledger_items()[1], json.load(f), P.REPO)
        fx._health = R.health_order(None, "ledger classifier (no verdict read)", fallback)
        order, w = fx.pool_order(r)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    plist = R.pkg("priority_list")
    orders = plist.order_map(plist.load(P.REPO)["entries"])
    old_open = sum(1 for it in w.items.values() if it.state in ("proposed", "ready")
                   and (it.created_at or "") < a.before)
    rows = [(n, w.items[i], placed(w.items[i], plist, orders, fx.first, fx.bounce)) for n, i in enumerate(order)]
    old = [(n, it, how) for n, it, how in rows if (it.created_at or "") < a.before]
    first_unplaced = next((n for n, _, how in rows if how is None), len(rows))
    jumped = [(n, it, how) for n, it, how in rows if how is not None and n > first_unplaced]
    print("pool %d · open proposed/ready filed before %s: %d · of them in the pool: %d (unplaced %d) · placed %d, "
          "all ahead of the first unplaced (place %d): %s" % (len(order), a.before, old_open, len(old),
          sum(1 for *_, how in old if how is None), sum(1 for *_, how in rows if how), first_unplaced, not jumped))
    for n, it, how in rows[:a.show]:
        print("  %3d %-50s %s %s" % (n, it.id, (it.created_at or "?")[:10], how or "unplaced"))
    for n, it, how in old:
        print("  old %3d %s %s %s" % (n, it.id, it.created_at, how or "unplaced"))
    for n, it, how in jumped:
        print("PLACED BEHIND UNPLACED  %3d %s (%s)" % (n, it.id, how))
    if not order or not old_open:
        print("UNMEASURED: an empty pool or no old open item means the probe cannot see the backlog")
        return 2
    head, how = rows[0][1], rows[0][2]
    head_bad = (head.created_at or "") < a.before and how is None
    if head_bad:
        print("HEAD IS OLD UNPLACED BACKLOG: %s" % head.id)
    return 1 if jumped or head_bad else 0


if __name__ == "__main__":
    sys.exit(main())
