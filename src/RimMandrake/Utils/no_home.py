#!/usr/bin/env python3
"""no_home.py: the count of needs not filed anywhere, shown beside the owner's one view. No model, no tokens.

Item RIMMANDRAKE_BUILD_ONE_OWNER_VIEW_NO_HOME_COUNT_BESIDE, step 3 of
design/specs/2026-11-22-coordination-every-agent-must-use/plan.md (§Capture). Page
design/specs/2026-11-23-owner-one-view/boundary.md; selftest selftest_owner_one_view.py; acceptance
src/RimMandrake/rimflow/acceptance/step3_one_view_accept.py.

    count(sources) -> {"no_home": int or None, "by_source": {name: int}, "unmeasured": [name], "names": {name: [..]}}
    unanswered_cards(asked, answered) -> the asked ids with no answer, in the order asked
    reading(evs, items, records, now) -> count() over the live sources, shared through one file for TTL_S

    python3 src/RimMandrake/Utils/no_home.py          the reading now (fresh count, written to the shared file)

The sources: his typed words with no home (probe_his_words.py's rule), ended runs with no later act, and cards he was
asked and did not answer (each one is a need with no home until it is filed). Words typed on the other machines are a
source no program reads yet: it is named UNMEASURED, never 0.
"""
import datetime as dt
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
for _p in (HERE, os.path.join(os.path.dirname(HERE), "rimflow")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

# The window each source looks back over. Danger: an older window counts history from before the List Pipeline as
# today's needs (the run records and transcripts reach back months). Evidence: the plan's measurement reads "your typed
# messages with no home in 3 days", and the probe of 2026-11-22 used the same 3 days.
WINDOW_S = 3 * 86400
# A count younger than this is shared, not recounted. Danger: both pages build every minute, and recounting on every
# build doubles a load the pages carry each minute. Evidence: the count took 6.8 s live on 2026-11-23 (the transcript
# scan is about 5 s, probe_results.md); its sources move on the scale of minutes to hours.
# budget: danger=both pages recount on every build; ends no work: the count is made again
TTL_S = 300
# Names kept per source for the view. Danger: a long list of chat messages buries his block (the owner asked for a
# dense, readable page, 2026-11-23). Evidence: 48 typed messages read NO HOME in 3 days on 2026-11-23.
NAMES_SHOWN = 5
CLOSED = ("done", "dropped", "superseded")
ELSEWHERE = "words typed on SteveDesktop, the Desktop, the Laptop or another window"


def count(sources):
    """-> the count over {name: callable -> list of needs with no home} (count-sums-the-readable-sources)."""
    by, unm, names = {}, [], {}
    for name, fn in (sources or {}).items():
        try:
            got = fn()
            if got is None:
                raise ValueError("the source answered nothing at all")      # no answer is not an empty answer
            got = list(got)
        except Exception:   # noqa: BLE001 - a source that cannot be read is named, never a zero
            unm.append(name)
            continue
        by[name] = len(got)
        names[name] = [str(x) for x in got[:NAMES_SHOWN]]
    return {"no_home": sum(by.values()) if by else None, "by_source": by, "unmeasured": unm, "names": names}


def unanswered_cards(asked, answered):
    """-> the asked card ids with no answer, in the order asked (an-unanswered-card-is-a-need)."""
    answered = set(answered or ())
    seen, out = set(), []
    for c in asked or []:
        if c not in answered and c not in seen:
            seen.add(c)
            out.append(c)
    return out


def _epoch(v):
    """list_pipeline.epoch: unix time from a number or an ISO text, or None (unknown)."""
    import list_pipeline as LP
    return LP.epoch(v)


def _g(o, k):
    return o.get(k) if isinstance(o, dict) else getattr(o, k, None)


def last_act(evs):
    """list_pipeline.last_act: the one rule for a later act (a program's note about a run's end is not one)."""
    import list_pipeline as LP
    return LP.last_act(evs)


def left_open_notes(evs):
    """-> {item id: [times of its notes that start LEFT OPEN:]} (the run's own next act; left_open_continue reads it)."""
    out = {}
    for e in evs or []:
        if isinstance(e, dict) and e.get("event") == "note" and str(e.get("text") or "").lstrip().startswith("LEFT OPEN:"):
            t = _epoch(e.get("ts"))
            if t is not None:
                out.setdefault(e.get("id"), []).append(t)
    return out


def ended_runs(records, items, last_event, now, window=WINDOW_S, left_open=None):
    """-> "<unit> on <item>" for each run that ended in the window, newest per item, on an item that is open, has no
    outcome check, and has no ledger act after the run ended (an-ended-run-with-no-later-act-is-a-need). A run whose
    item waits (a dated wait or a block: the List Pipeline's Waiting stage) or that left a LEFT OPEN: note since it
    began gave its end a home; so did a Maturation Pipeline stage run (RM_CONTROL_STAGE), read by the Dispatch tick."""
    by = {}
    for r in records or []:
        by.setdefault(r.get("item"), []).append(r)
    newest = {}
    for iid, rs in by.items():
        if any((r.get("live_state") or r.get("status")) in ("running", "launching") for r in rs):
            continue        # a live run is on it: its end is not here yet
        ended = [r for r in rs if _epoch(r.get("ended")) is not None]
        if ended:
            newest[iid] = max(ended, key=lambda r: _epoch(r.get("ended")))
    out = []
    for iid, r in sorted(newest.items(), key=lambda kv: str(kv[0])):
        if not isinstance(r, dict) or iid not in (items or {}):
            continue
        it, end = items[iid], _epoch(r.get("ended"))
        if _g(it, "state") in CLOSED or _g(it, "effect") or now - end > window:
            continue
        if (last_event or {}).get(iid, 0) > end:
            continue
        if _g(it, "wait_until") or _g(it, "blocked"):
            continue
        if (r.get("env") or {}).get("RM_CONTROL_STAGE"):
            continue        # a Maturation Pipeline stage run: the Dispatch tick reads its end, the mod card shows it
        began = _epoch(r.get("at"))
        if began is None:
            began = 0       # a run whose start cannot be read: any LEFT OPEN: note on the item gives it a home
        if any(t >= began for t in (left_open or {}).get(iid, [])):
            continue
        out.append("%s on %s" % (r.get("unit"), iid))
    return out


def _pac(t):
    from zoneinfo import ZoneInfo
    if t is None:
        return "UNMEASURED"
    x = dt.datetime.fromtimestamp(t, ZoneInfo("America/Los_Angeles"))
    return "%s %s %s" % (x.strftime("%a %b %d"), x.strftime("%I:%M %p").lstrip("0"), x.strftime("%Z"))


def _iso(t):
    return dt.datetime.fromtimestamp(t, dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def sources(evs, items, records, now, window=WINDOW_S):
    """-> {name: callable}: the live sources. A source whose store is None raises, so it is named unmeasured."""
    import probe_his_words as P
    since, until = _iso(now - window), _iso(now)

    def need(x, what):
        if x is None:
            raise OSError("%s could not be read" % what)
        return x

    def typed():
        need(evs, "the ledger")
        return ["%s: %s" % (_pac(_epoch(r["ts"])), " ".join(r["text"].split())[:90])
                for r in P.no_home_rows(since, until, evs)]

    def runs():
        return ended_runs(need(records, "the run records"), need(items, "the ledger"), last_act(evs), now, window,
                          left_open_notes(evs))

    def cards():
        c = P.cards(since, until)
        return ["%s: %s" % (cid, c["text"].get(cid, "")) for cid in
                unanswered_cards([x for x in c["asked"] if x not in c["on_screen"]], c["answered"])]

    def elsewhere():
        raise OSError("no program reads them yet")

    return {"typed words": typed, "ended runs with no later act": runs, "cards asked, not answered": cards,
            ELSEWHERE: elsewhere}


def state_path(create=True):
    """The shared reading, beside owner_queue's view.json."""
    import owner_queue
    return os.path.join(owner_queue.view_dir(create), "no_home.json")


def fresh(r, now, max_age):
    """-> r when it is a reading younger than max_age, else None."""
    if not isinstance(r, dict) or not isinstance(r.get("at"), (int, float)) or not (0 <= now - r["at"] < max_age):
        return None
    return r


def reading(evs, items, records, now=None, path=None, ttl=TTL_S, fresh=False):
    """-> count() plus "at", from the shared file while it is younger than ttl, else counted now and written
    (the-reading-is-shared-and-cached). A file that cannot be written leaves the count as it is, with "write_failed"."""
    now = time.time() if now is None else now
    import owner_queue
    refused = owner_queue.test_refusal(path)
    path = path or state_path(create=not refused)
    if not fresh:
        try:
            with open(path, encoding="utf-8") as f:
                r = json.load(f)
            if isinstance(r, dict) and 0 <= now - float(r.get("at") or 0) < ttl:
                return r
        except (OSError, ValueError):
            pass
    r = count(sources(evs, items, records, now))
    r["at"] = now
    r["window_s"] = WINDOW_S
    if refused:
        r["write_failed"] = refused
        return r
    try:
        with open(path + ".tmp", "w", encoding="utf-8") as f:
            json.dump(r, f, indent=1, ensure_ascii=False)
        os.replace(path + ".tmp", path)
    except OSError as e:
        r["write_failed"] = "%s: %s" % (type(e).__name__, e)
    return r


def last(now, max_age, path=None):
    """-> the shared reading while it is younger than max_age, else None. Reads only; never counts."""
    try:
        with open(path or state_path(create=False), encoding="utf-8") as f:
            r = json.load(f)
    except (OSError, ValueError):
        return None
    return fresh(r, now, max_age)


def main():
    import fleet_mods
    try:
        evs, world = fleet_mods.ledger()
        items = world.items
    except Exception as e:  # noqa: BLE001
        print("could not read the ledger: %s" % e, file=sys.stderr)
        evs = items = None
    try:
        import detached_helper as DH
        recs = [dict(r, live_state=DH.live_status(r) if r.get("status") in ("running", "launching") else r.get("status"))
                for r in DH.all_records()]
    except Exception as e:  # noqa: BLE001
        print("could not read the run records: %s" % e, file=sys.stderr)
        recs = None
    r = reading(evs, items, recs, fresh=True)
    print(json.dumps(r, indent=1, ensure_ascii=False))
    return 0 if r["no_home"] is not None else 2


if __name__ == "__main__":
    sys.exit(main())
