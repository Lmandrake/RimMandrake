#!/usr/bin/env python3
"""bridge_hours: hours the bridge lock was held, from ledger `bridge` events (FOUNDRY_THROUGHPUT_MEASURE_V2_GAP).

The measure behind design/RimMandrake/foundry_management_analysis_2026-11-01.md: 14.6 h a day in the best v2 week,
2.5 h a day in early v3. A hold is cut at CAP_S so one forgotten lock cannot read as a day of driving. A held lock is
still not proof of driving; this reads the lane's occupancy, nothing finer.
"""
import datetime as dt

CAP_S = 6 * 3600


def _epoch(ts):
    """-> seconds, or None for a timestamp that will not parse: one bad line must not cost the reading."""
    try:
        return dt.datetime.fromisoformat(ts.replace("Z", "+00:00")).timestamp()
    except (ValueError, AttributeError, TypeError, OSError, OverflowError):
        return None


def held_hours(events, now, span_s, cap_s=CAP_S):
    """-> hours of (now - span_s, now] under a hold. `events` is any iterable of ledger events; only `bridge` ones with
    state `taken` or `released` count, sorted here by ts with ties left in the order given (pass `model.read()` order, which
    settles same-second events; never sort on the state word, `released` would precede `taken`). A take during a hold ends that hold and starts the next, and a
    hold still open at the end runs to `now`. Pure (tested)."""
    rows = [(_epoch(e.get("ts")), e["state"]) for e in events
            if e.get("event") == "bridge" and e.get("state") in ("taken", "released")]
    rows = sorted((r for r in rows if r[0] is not None), key=lambda r: r[0])
    start, total, begin = None, 0.0, now - span_s

    def add(a, b):
        return max(0.0, min(b, a + cap_s, now) - max(a, begin))

    for t, state in rows:
        if t > now:
            break
        if start is not None:
            total += add(start, t)
        start = t if state == "taken" else None
    if start is not None:
        total += add(start, now)
    return round(total / 3600.0, 2)
