#!/usr/bin/env python3
"""list_pipeline.py: the List Pipeline's one stage function. No model, no tokens, no reads of its own.

Item RIMMANDRAKE_BUILD_ONE_OWNER_VIEW_NO_HOME_COUNT_BESIDE, step 3 of
design/specs/2026-11-22-coordination-every-agent-must-use/plan.md (§The stages, §The six questions). Page
design/specs/2026-11-23-list-stage-view/boundary.md; selftest selftest_list_pipeline.py; acceptance
acceptance/step3b_stage_view_accept.py.

One function decides an item's stage, and the tick (list_dispatch.tick) and the page (maturation_nonmod.section) both
call it, so the launcher and the page cannot disagree:

    stage_of(item, now) -> {"stage", "why", "resumes", "promise"}
    facts(ledger item, runs, lane row, ...) -> the plain item dict stage_of reads
    six(items, now) -> {"doing", "next", "closed", "open_why", "escalated", "review", "counts"}

The Shape stage (plan step 4, list_shape.py) plugs in through the item's `shape` parts: facts() reads their route
(list_shape.first_route), and the lane's row carries the same route; stage_of reads it as a plain fact.
"""
import datetime as dt

STAGES = ("shape", "waiting", "ready", "work", "verify", "closed", "trouble", "review", "conflict", "unmeasured")
CLOSED = ("done", "dropped", "superseded")
# A lane reading older than this is not current. Danger: a dead rm-list-dispatch.timer leaves every verdict silently
# old. Evidence: the timer beats every 10 min (OnUnitActiveSec=10min); three missed beats is a stopped timer, the same
# rule as the red dispatcher's reading (maturation_nonmod.RED_STALE_S).
# budget: danger=a dead rm-list-dispatch.timer leaves every verdict silently old; ends no work: the lane reading says that it is
# budget: old
LANE_STALE_S = 1800

# who moves an item on from each stage, today (each-stage-says-program-or-by-hand)
MOVED_BY = {
    "shape": ("program", "list_dispatch launches one Shape run on an item due for Shape (list_shape.due: named with "
                         "`rimflow shape <ID> --enter`, or filed since Shape went live and past its grace); an older item "
                         "waits until someone names it"),
    "waiting": ("program", "list_dispatch resumes it when the item it waits on closes or its date comes; a date runs the "
                           "check, never a launch"),
    "ready": ("program", "list_dispatch launches one helper when a slot and every gate are free"),
    "work": ("program", "one detached helper run (list_dispatch launch), or a seat that claimed it"),
    "verify": ("program", "list_dispatch runs the check against main on its next tick and closes the item when it holds"),
    "closed": ("program", "an operational item's promise is rechecked for good by rm-deadman"),
    "trouble": ("by hand", "the Conductor reads the report and does the smallest act it names"),
    "review": ("by hand", "the owner answers, looks or picks"),
    "conflict": ("by hand", "the Conductor reads which fact is wrong and corrects it"),
    "unmeasured": ("by hand", "the check or the lane's reading could not be read: repair the reader"),
}

# list_dispatch decisions taken before the item's check ran (lane-row-to-verdict)
_NOT_RUN = ("disabled", "pipeline_paused", "off", "adopt", "would_adopt", "adopted", "adopt_refused", "adopt_too_heavy",
            "no_effect", "not_found", "closed")
_HOLDS = ("close", "would_close", "closed_by_check", "close_refused")


def g(o, k, default=None):
    """A field of a ledger item (model.Item) or of a dict."""
    if isinstance(o, dict):
        return o.get(k, default)
    return getattr(o, k, default)


def epoch(v):
    """unix time from a number or an ISO text, or None."""
    if v is None or isinstance(v, bool):
        return None
    if isinstance(v, (int, float)):
        return float(v)
    try:
        t = dt.datetime.fromisoformat(str(v).replace("Z", "+00:00"))
    except ValueError:
        return None
    return (t if t.tzinfo else t.replace(tzinfo=dt.timezone.utc)).timestamp()


def _r(stage, why, resumes=None, promise=None):
    return {"stage": stage, "why": why, "resumes": resumes, "promise": promise}


def _note(item):
    n = str(item.get("note") or "").strip()
    return (" (%s)" % n) if n else ""


def stage_of(item, now):
    """-> {"stage", "why", "resumes", "promise"} (one-stage-per-item-from-one-rule). Pure; never raises on a missing key."""
    item = item if isinstance(item, dict) else {}
    state, eff, verdict = item.get("state"), item.get("effect"), item.get("verdict")
    run, route, waits = item.get("run"), item.get("route"), item.get("waits")
    promise = item.get("promise") if item.get("promise") in ("kept", "dead") else None
    if state in CLOSED:
        if state == "done" and verdict == "fails":
            return _r("conflict", "the item is closed done, and its check fails" + _note(item), promise=promise)
        return _r("closed", "the item is %s%s" % (state, "; its check holds" if verdict == "holds" else ""),
                  promise=promise)
    if item.get("stopped"):
        return _r("trouble", "stopped: %s" % (item.get("note") or "its run ended and nothing moved it on"))
    if run == "live_work":
        return _r("work", "a Work run is live on it" + _note(item))
    if run == "live_shape":
        return _r("shape", "a run is live on it and it has no outcome check yet" + _note(item))
    if isinstance(route, dict) and route.get("who"):
        who, ask, res = route.get("who"), route.get("ask") or "-", route.get("resumes") or None
        if who == "owner":
            return _r("review", "routed to the owner: %s" % ask, res)
        if who == "review":
            return _r("review", "ready for his look: %s" % ask, res)
        if who == "conductor":
            return _r("waiting", "routed to the Conductor: %s" % ask, res)      # a question, not a broken run (six: asked)
        return _r("waiting", "routed to %s: %s" % (who, ask), res)
    until = epoch((waits or {}).get("until")) if isinstance(waits, dict) else None
    if isinstance(waits, dict) and (until is None or until > now):
        return _r("waiting", "it waits on %s" % (waits.get("on") or "a named event"), waits.get("resumes") or None)
    due = isinstance(waits, dict) and until is not None and until <= now
    if not eff:
        return _r("shape", ("its wait came due and it has no outcome check" if due else
                            "no outcome check and no route") + _note(item))
    if verdict == "holds":
        return _r("verify", "its check holds; the tick closes it" + _note(item))
    if verdict not in ("fails", None):
        return _r("unmeasured", "its check could not be read: %s%s" % (verdict, _note(item)))
    if due and verdict == "fails":
        return _r("shape", "its wait came due and the check still fails: a date never launches old work, so Shape "
                           "looks at it again")
    if run == "ended" or verdict is None:
        return _r("verify", ("its run ended; the check runs on the next tick" if run == "ended" else
                             "its check has not been run yet") + _note(item))
    return _r("ready", "its check fails and it waits on nothing" + _note(item))


def is_machine_act(e):
    """A ledger event a program wrote about a run's end (detached_helper.finish's note): not a later act on the item."""
    return (e.get("event") == "note" and str(e.get("text") or "").startswith("DETACHED run")) or \
        e.get("why") == "detached run ended"


def last_act(evs):
    """-> {item id: the time of its last ledger event that is not a program's note about a run's end}."""
    out = {}
    for e in evs or []:
        if not isinstance(e, dict) or not e.get("id") or is_machine_act(e):
            continue
        t = epoch(e.get("ts"))
        if t is not None and t > out.get(e["id"], 0):
            out[e["id"]] = t
    return out


def lane_verdict(decision, has_effect=True):
    """A list_dispatch row's decision -> the check's verdict (lane-row-to-verdict)."""
    if not has_effect or decision is None or decision in _NOT_RUN:
        return None
    if decision in _HOLDS:
        return "holds"
    if decision == "blind":
        return "unmeasured"
    return "fails"


def _run_state(r):
    return r.get("live_state") or r.get("status")


def facts(it, runs=(), lane_row=None, lane_at=None, lane_cause=None, his=False, ready_note=None, last_event=None,
          end_kind=None, open_ids=None, now=None, age_from=None):
    """-> the plain item dict stage_of reads, from one ledger item and what is known about it.
    runs: its detached-run records, oldest first; lane_row: list_dispatch's reading row ({decision, why}) or None;
    lane_at: that reading's time, None when unreadable (lane_cause says why); his: owner_queue.is_his; ready_note: the
    note text that says it is ready to show, or None; last_event: the time of its last ledger event; end_kind: the class
    of its newest ended run (maturation_nonmod.run_end: stopped, capped, refused, left open, said nothing);
    open_ids: the ids of open items (None: every named item counts as open)."""
    now = 0.0 if now is None else now
    eff = g(it, "effect")
    if not eff:
        eff = None                      # an empty check text is no check
    d = {"state": g(it, "state"), "effect": eff, "verdict": None, "route": None, "waits": None, "run": None,
         "stopped": False, "promise": None, "note": None}
    if g(it, "live"):
        d["promise"] = "dead" if g(it, "live_broken") else "kept"
    filed = epoch(g(it, "created_at"))
    d["age_h"] = round(max(0.0, now - filed) / 3600.0, 1) if filed is not None else None
    runs = [r for r in (runs or []) if isinstance(r, dict)]
    live = [r for r in runs if _run_state(r) in ("running", "launching")]
    newest_end = None
    if live:
        d["run"] = "live_work" if eff else "live_shape"
        d["note"] = "%s since %s" % (live[-1].get("unit"), _clock(live[-1].get("at")))
    elif runs:
        newest_end = epoch(runs[-1].get("ended")) or epoch(runs[-1].get("at"))
    # the check's verdict, from the tick's row
    if eff:
        if lane_at is None:
            d["verdict"], d["note"] = "unmeasured", "the lane's reading could not be read: %s" % (lane_cause or "not read")
        elif now - lane_at > LANE_STALE_S:
            d["verdict"] = "unmeasured"
            d["note"] = "the lane's reading is %d min old: rm-list-dispatch.timer may have stopped" % ((now - lane_at) // 60)
        elif lane_row is None:
            d["verdict"], d["note"] = None, "the lane's last tick did not list it"
        else:
            dec = lane_row.get("decision")
            d["verdict"] = lane_verdict(dec)
            if dec == "stopped":
                d["stopped"], d["note"] = True, lane_row.get("why") or "the lane stopped on it"
            elif dec in ("claimed",) and not live:
                d["run"], d["note"] = "live_work", lane_row.get("why")
            elif not live:
                d["note"] = "the lane: %s: %s" % (dec, _clip(lane_row.get("why"), 140))
            if newest_end is not None and not live and newest_end > lane_at:
                d["verdict"], d["run"] = None, "ended"         # a run end the tick has not read yet
    elif newest_end is not None and end_kind in ("stopped", "capped", "refused") and (
            last_event is None or last_event <= newest_end):
        d["stopped"] = True
        d["note"] = "its last run (%s) was %s at %s and nothing on the ledger followed" % (
            runs[-1].get("unit"), end_kind, _clock(newest_end))
    elif newest_end is not None and end_kind:
        d["note"] = "its last run %s" % ("left it open" if end_kind == "left open" else "ended and said nothing")
    # what it waits on
    wu = epoch(g(it, "wait_until"))
    if g(it, "wait_until") and wu is None:
        d["waits"] = {"on": "a wait date that cannot be read (%r)" % g(it, "wait_until"), "resumes": "a readable date",
                      "until": None}
    elif wu is not None:
        d["waits"] = {"on": "a date: %s" % _clip(g(it, "wait_reason") or "no reason given", 90),
                      "resumes": "the date %s" % _clock(wu), "until": wu}
    elif g(it, "blocked"):
        on = g(it, "blocked_on")
        kind = g(it, "blocked_kind") or ("item" if on else None)     # priority.block_kind
        if kind == "item" and on:
            if open_ids is None or on in open_ids:
                d["waits"] = {"on": str(on), "resumes": "%s closes" % on, "until": None}
        elif kind == "owner" and his:
            pass        # routed to him below
        else:
            d["waits"] = {"on": "%s: %s" % ("the owner's block (he answered; ours to lift)" if kind == "owner" else
                                            "a %s block" % (kind or "unnamed"),
                                            _clip(g(it, "blocked_reason") or "no reason given", 80)),
                          "resumes": "the block is lifted", "until": epoch(g(it, "blocked_until"))}
    shaped_route = _shape_route(it)
    if shaped_route:
        d["route"] = shaped_route          # the Shape stage's split (list_shape.first_route): the route it wrote
    elif his:
        d["route"] = {"who": "owner", "ask": _clip(g(it, "title") or "his answer", 120), "resumes": "his answer"}
    elif ready_note:
        d["route"] = {"who": "review", "ask": _clip(ready_note, 120), "resumes": "his look"}
    if age_from is not None:
        d["age_h"] = age_from
    return d


def _shape_route(it):
    """The route the Shape stage wrote on the item (its `shape` parts, list_shape.first_route), or None."""
    sh = g(it, "shape")
    parts = sh.get("parts") if isinstance(sh, dict) else None
    if not parts:
        return None
    import list_shape
    return list_shape.first_route(parts)


def _clip(s, n):
    s = " ".join(str(s or "").split())
    return s if len(s) <= n else s[:n - 1].rstrip() + "…"


def _clock(t):
    t = epoch(t)
    if t is None:
        return "UNMEASURED"
    from zoneinfo import ZoneInfo
    x = dt.datetime.fromtimestamp(t, ZoneInfo("America/Los_Angeles"))
    return "%s %s, %s%d" % (x.strftime("%I:%M %p").lstrip("0"), x.strftime("%Z"), x.strftime("%a %b "), x.day)


REASONS = {"shape": "no outcome check yet (Shape)", "ready": "ready: a failing check, waiting for a slot",
           "work": "a run is live on it", "verify": "its check runs on the next tick (Verify)", "trouble": "in trouble",
           "conflict": "facts disagree", "unmeasured": "its check could not be read"}


def reason(item, st):
    """The one open-and-why group of an item at stage st["stage"]."""
    s = st["stage"]
    if s == "waiting":
        w, r = item.get("waits"), item.get("route")
        if isinstance(r, dict) and r.get("who"):
            return "routed to %s" % r.get("who")
        return "waiting on %s" % ((w or {}).get("on") or "a named event")
    if s == "review":
        return "routed to the owner" if (item.get("route") or {}).get("who") == "owner" else "ready for his look"
    return REASONS.get(s, s)


def six(items, now, stage=None):
    """-> the six answers over {id: item} (six-answers-from-the-stages). Rows keep the order given. stage: the stage
    function (stage_of; a caller may pass its own reference to the same function)."""
    stage = stage or stage_of
    out = {"doing": [], "next": [], "closed": [], "open_why": {}, "escalated": [], "asked": [], "review": [],
           "counts": {}}
    for iid, it in (items or {}).items():
        it = it if isinstance(it, dict) else {}
        st = stage(it, now)
        row = {"item": iid, "stage": st["stage"], "why": st["why"], "resumes": st["resumes"],
               "promise": st["promise"], "age_h": it.get("age_h")}
        out["counts"][st["stage"]] = out["counts"].get(st["stage"], 0) + 1
        if st["stage"] == "closed":
            out["closed"].append(row)
            continue
        if str(it.get("run") or "").startswith("live"):
            out["doing"].append(row)
        if st["stage"] == "ready":
            out["next"].append(row)
        if st["stage"] in ("trouble", "conflict"):
            out["escalated"].append(row)
        if st["stage"] == "waiting" and isinstance(it.get("route"), dict) and it["route"].get("who") == "conductor":
            out["asked"].append(row)
        if st["stage"] == "review":
            out["review"].append(row)
        k = reason(it, st)
        grp = out["open_why"].setdefault(k, {"count": 0, "oldest": None, "age_h": None, "items": [], "stage": st["stage"]})
        grp["count"] += 1
        grp["items"].append(iid)
        a = it.get("age_h")
        if isinstance(a, (int, float)) and (grp["age_h"] is None or a > grp["age_h"]):
            grp["oldest"], grp["age_h"] = iid, a
        elif grp["oldest"] is None and grp["age_h"] is None:
            grp["oldest"] = iid
    return out
