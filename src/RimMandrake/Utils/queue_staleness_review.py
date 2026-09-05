#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""queue_staleness_review.py — surfaces `doing`/`blocked` items rotting silently.

    python3 src/RimMandrake/Utils/queue_staleness_review.py                # human report
    python3 src/RimMandrake/Utils/queue_staleness_review.py --json         # machine-readable
    python3 src/RimMandrake/Utils/queue_staleness_review.py --blocked-days 2 --doing-days 5

⭐ WHY THIS EXISTS. `QUEUE_HEALTH_CHECK_1` (infrastructure/state/items/QUEUE_HEALTH_CHECK_1.md)
was a ONE-OFF hand-run census: 20 `doing` items, three read as multi-day-stale "by the
clock alone", each one hand-verified against its item file and commit history before being
cleared. Its own closing line named the gap: *"A fuller pass ... is real remaining scope if
the daily staleness review (QUEUE_DAILY_STALENESS_REVIEW_1) picks it up as a recurring job
rather than a one-off."* This is that job, made runnable instead of re-typed by hand.

🔑 THIS TOOL IS READ-ONLY. It replays the ledger and prints; it never appends an event,
never touches `infrastructure/state/queue/*.md`, never mutates anything. It answers
"what's stuck", `rimflow` verbs answer "unstick it".

WHY 3 DAYS FOR BLOCKED, 7 FOR DOING (owner-facing default, both are --flags)
=============================================================================
Not arbitrary — read off the one hand-run precedent this tool replaces:
  - `QUEUE_HEALTH_CHECK_1` treated 3-4 days idle on a `doing` item as "worth a look",
    and on inspection every one of those was a DELIBERATE park (DROID_SYSTEM_BUILD_1,
    JAWA_PATCHES_SPLIT_1) or had real open scope still on file (LIVESTOCK_STARTER_TRIO_1).
    So 3-4 days idle is NORMAL for `doing` — a seat legitimately juggles several open
    items — and a 7-day (one full week) threshold gives a doing item a fair run before
    this tool calls it out, without waiting so long that a truly abandoned item rots
    for a month.
  - `blocked` gets the SHORTER threshold (3 days) because blocked means "something is
    WRONG and someone must act" (render.py's own section header for it) — not "waiting
    is fine", the way `needs`/WAITING ON A WINDOW is. A blocked item costs nothing to
    leave stale for an hour; leaving it stale for a week means the thing that broke it
    sat unaddressed for a week.
These are `--blocked-days`/`--doing-days` flags, not constants, because the owner is the
one who gets to say the cadence is wrong.

WHAT #4 ("mis-tagged needs/for") ACTUALLY CHECKS, AND WHAT IT DOES NOT
========================================================================
🔴 The `for OWNER should appear in queue/HUMAN.md` idea in this item's own title turned
out to be a WRONG premise on inspection, not a stretch goal — `infrastructure/state/queue/
HUMAN.md`'s own header says it plainly: *"Owner DECISIONS are items and do live in the
ledger... those are tracked, counted on the board, and closed with a trailer. This file is
for everything that is not shaped like an item."* An item filed `--for OWNER` is worked via
`rimflow next --seat OWNER`, never via HUMAN.md — HUMAN.md is hand-written prose for things
that are NOT items at all. So "for OWNER never in HUMAN.md" is not a defect and this tool
does not check for it; asserting otherwise would be exactly the "flagging a wrong thing"
mistake the rest of this codebase's own lesson file warns about.

✅ Two mis-tags ARE cheaply and honestly derivable from the ledger alone, and this tool
checks both:
  1. **`for` names a RETIRED seat.** `model.SEATS` keeps DECIDE/BUILD/CHECK/REP listed
     "so the ledger's history replays and legacy items keep their owners" (model.py's own
     comment) — those four seats do not operate any more (redesign #4, 2026-08-27). An
     open `doing`/`blocked` item still owned by one of them is orphaned: no live window
     will ever see it in `rimflow next`, because ranking is keyed on `item.owner` and
     nobody occupies that seat. This is checked unconditionally (not gated on the idle
     threshold) because it is true the instant the seat retires, not after N days.
  2. **`needs` names a window-condition that has DEMONSTRABLY opened since the item went
     idle.** `needs: bridge` means "waiting for the bridge to be free"; `needs: game-up`
     means "waiting for the game to come up" — both are ledger-visible events (`bridge`
     released, `game` UP). If an item has sat idle past its threshold while that exact
     window opened `--mistag-min` times or more in the meantime, the `needs` tag is very
     likely stale (the item was never actually picked up when its stated blocker cleared)
     and worth a human glance, not a full re-verify.

⛔ **`needs: offline`, `deploy`, `harvest`, `owner` are NOT checked here.** Each would need
a real signal this ledger does not cheaply carry (a deploy actually ran; a harvest actually
completed; "offline" has no satisfying event at all — it just means "no window needed").
Inventing a proxy for those would be exactly the fabricated derivation this project's own
doctrine forbids (`CLAUDE.md` "never guess a defName..."; `measuring-large-artifacts`
applies the same rule to instruments in general) — left as an honest gap, not implemented.

Reuses `rimflow.model` for ALL ledger reading/replay — no ledger parsing is
reimplemented here. See `src/RimMandrake/rimflow/model.py` for the event schema and
`render.py`'s `view_sections()` for the state-bucketing convention this mirrors
(IN PROGRESS = state=="doing", BLOCKED = item.blocked and item.open).
"""
import argparse
import json
import os
import sys
from datetime import datetime, timezone

REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                    "..", "..", ".."))
sys.path.insert(0, os.path.join(REPO, "src", "RimMandrake"))
from rimflow import model                                            # noqa: E402

# render.py's own bucketing convention: IN PROGRESS is `state == "doing"`,
# BLOCKED is `item.blocked` (a flag, independent of state — see model.py's NEEDS
# comment: "blocked is NOT a state"). An item can in principle be both; here it is
# bucketed as "blocked" when the flag is set, because that is the more urgent of
# the two facts about it ("something is WRONG" outranks "still being worked").
DEFAULT_BLOCKED_DAYS = 3.0
DEFAULT_DOING_DAYS = 7.0
DEFAULT_MISTAG_MIN = 2      # how many bridge-free / game-UP events "many times" means

# model.py: "BENCH and FOUNDRY are the live windows (redesign #4, 2026-08-27). The
# four retired seats stay listed so the ledger's history replays and legacy items
# keep their owners." Those four are exactly the seats this tool flags as orphaned.
RETIRED_SEATS = tuple(s for s in model.SEATS if s not in ("BENCH", "FOUNDRY", "OWNER"))


def _parse_ts(ts):
    return datetime.strptime(ts, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)


def last_event_ts(item, events):
    """The timestamp of this item's OWN most recent event — not when it was filed."""
    idx = item.history[-1] if item.history else item.created_index
    return events[idx]["ts"]


def _events_since(events, verb, state, since_ts):
    """Itemless `verb` events (bridge/game) with the given `state`, after `since_ts`."""
    return [ev for ev in events
            if ev.get("event") == verb and ev.get("state") == state
            and ev.get("ts", "") > since_ts]


def collect(world, events, blocked_days, doing_days, mistag_min, now=None):
    """-> rows, one per open `doing`/`blocked` item, newest-idle first.

    Pure function of an already-replayed `world` and its `events` list, so it is
    testable without touching the real ledger — see selftest_queue_staleness_review.py.
    """
    now = now or datetime.now(timezone.utc)
    rows = []
    for item in world.items.values():
        # Found live, 2026-09-05: `item.blocked` is a persistent flag a later
        # `drop`/`close` does NOT clear (by design - it is provenance, not state -
        # see Item.__repr__ appending " BLOCKED" regardless of state). Checking
        # it alone flagged three ALREADY-DROPPED items (REFMATCH_THRESHOLDS_
        # CALIBRATE_1, B55, FINAL_WORLD_PREP_1) as if they still needed a human,
        # months after they were correctly closed. render.py's own view_sections()
        # convention (this module's docstring already quotes it) is
        # `item.blocked and item.open` - `item.open` is what was missing here.
        if not (item.state == "doing" or (item.blocked and item.open)):
            continue
        bucket = "blocked" if item.blocked else "doing"
        threshold = blocked_days if bucket == "blocked" else doing_days
        last_ts = last_event_ts(item, events)
        days_idle = (now - _parse_ts(last_ts)).total_seconds() / 86400.0
        stale = days_idle >= threshold

        mistags = []
        if item.owner in RETIRED_SEATS:
            mistags.append("for=%s is a RETIRED seat (%s) — no live window will ever "
                           "see this in `rimflow next`" % (item.owner, item.owner))
        if stale and item.needs == "bridge":
            freed = _events_since(events, "bridge", "released", last_ts)
            if len(freed) >= mistag_min:
                mistags.append(
                    "needs=bridge idle %.1fd, but the bridge went free %d time(s) "
                    "since — the tag may be stale, not the blocker" % (days_idle, len(freed)))
        if stale and item.needs == "game-up":
            ups = _events_since(events, "game", "UP", last_ts)
            if len(ups) >= mistag_min:
                mistags.append(
                    "needs=game-up idle %.1fd, but the game went UP %d time(s) "
                    "since — the tag may be stale, not the blocker" % (days_idle, len(ups)))

        rows.append({
            "id": item.id, "title": item.title, "bucket": bucket, "owner": item.owner,
            "needs": item.needs, "last_event": last_ts,
            "days_idle": round(days_idle, 1), "threshold_days": threshold,
            "stale": stale, "blocked_reason": item.blocked_reason if item.blocked else None,
            "mistags": mistags,
        })
    rows.sort(key=lambda r: -r["days_idle"])
    return rows


def _fmt_row(r):
    bits = ["for=%s" % r["owner"], "needs=%s" % r["needs"]]
    if r["blocked_reason"]:
        bits.append("blocked: %s" % r["blocked_reason"])
    return "  %-42s %6.1fd idle  %s" % (r["id"], r["days_idle"], "  ".join(bits))


def render_report(rows, blocked_days, doing_days, mistag_min, as_of):
    L = []
    L.append("QUEUE STALENESS REVIEW — thresholds: blocked >%.1fd, doing >%.1fd "
             "(mis-tag min %d events)" % (blocked_days, doing_days, mistag_min))
    L.append("as-of: %s" % as_of)
    L.append("")

    stale_blocked = [r for r in rows if r["bucket"] == "blocked" and r["stale"]]
    stale_doing = [r for r in rows if r["bucket"] == "doing" and r["stale"]]
    mistagged = [r for r in rows if r["mistags"]]

    L.append("STALE BLOCKED (idle past %.1fd) — something is WRONG:" % blocked_days)
    L += [_fmt_row(r) for r in stale_blocked] or ["  none"]
    L.append("")

    L.append("STALE DOING (idle past %.1fd):" % doing_days)
    L += [_fmt_row(r) for r in stale_doing] or ["  none"]
    L.append("")

    L.append("MIS-TAGGED needs/for (machine-derivable only — see docstring):")
    for r in mistagged:
        for m in r["mistags"]:
            L.append("  %-42s %s" % (r["id"], m))
    if not mistagged:
        L.append("  none")
    L.append("")

    n_doing = sum(1 for r in rows if r["bucket"] == "doing")
    n_blocked = sum(1 for r in rows if r["bucket"] == "blocked")
    L.append("%d open doing/blocked items checked (%d doing, %d blocked); "
             "%d stale; %d mis-tagged"
             % (len(rows), n_doing, n_blocked, len(stale_blocked) + len(stale_doing),
                len(mistagged)))
    return "\n".join(L)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--blocked-days", type=float, default=DEFAULT_BLOCKED_DAYS,
                    help="flag a blocked item idle past this many days (default %.1f)"
                         % DEFAULT_BLOCKED_DAYS)
    ap.add_argument("--doing-days", type=float, default=DEFAULT_DOING_DAYS,
                    help="flag a doing item idle past this many days (default %.1f)"
                         % DEFAULT_DOING_DAYS)
    ap.add_argument("--mistag-min", type=int, default=DEFAULT_MISTAG_MIN,
                    help="how many bridge-free/game-UP events since idle counts as "
                         "'demonstrably available' (default %d)" % DEFAULT_MISTAG_MIN)
    ap.add_argument("--json", action="store_true", help="machine-readable")
    a = ap.parse_args(argv)

    events = model.read()
    world = model.replay(events)
    rows = collect(world, events, a.blocked_days, a.doing_days, a.mistag_min)

    from rimflow import render as rimflow_render
    as_of = rimflow_render.as_of(events) or "empty ledger"

    if a.json:
        json.dump({"as_of": as_of, "blocked_days": a.blocked_days,
                   "doing_days": a.doing_days, "mistag_min": a.mistag_min,
                   "rows": rows}, sys.stdout, indent=1, ensure_ascii=False)
        print()
        return 0

    print(render_report(rows, a.blocked_days, a.doing_days, a.mistag_min, as_of))
    # ⛔ Always 0. This reports; it never gates — see the module docstring.
    return 0


if __name__ == "__main__":
    sys.exit(main())
