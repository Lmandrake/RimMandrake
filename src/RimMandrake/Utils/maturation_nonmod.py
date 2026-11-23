#!/usr/bin/env python3
"""maturation_nonmod.py: the "Pipeline for work that is not mod work" section of MATURATION_NOW. No model, no tokens.

Item RIMMANDRAKE_SHOW_NON_MOD_PIPELINE_ON_MATURATION_PAGE_AS_IT_IS_TODAY. Boundary page (the promises, each tested):
design/specs/2026-11-22-non-mod-pipeline-section/boundary.md. Tests: selftest_maturation_nonmod.py.

The owner, 2026-11-22 10:47 PM PST: show "the smaller copy of the pipeline" that works everything that is not mod work,
"as its own pipeline, with whatever modules/stages it has within it, along with what's running and why". Today there
is no formal second pipeline, so this section draws the path as it is: filed on the ledger; launched by one of three
programs (red_dispatch, left_open_continue, stop_resume) or by the Conductor's hand; run; ended; read and acted on by
the Conductor's hand. It draws no stage that does not exist.

maturation_now.gather calls read_stores (the red dispatcher, alarms, games, showings; the ledger and run records come
from its own live_facts, read once) and safe_section; maturation_now.build places markdown() / html_block() directly
under "Pipeline now". A store it cannot read is "could not look" and its counts read UNMEASURED, never 0.
"""

import datetime as dt
import html
import json
import os
import re
import sys
from zoneinfo import ZoneInfo

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(REPO, "src", "RimMandrake", "rimflow"))
from item_identity import named_mod  # noqa: E402  the one rule for the mod an item names

PAC = ZoneInfo("America/Los_Angeles")
UNM = "UNMEASURED"
TITLE = "Pipeline for work that is not mod work"
OPEN_STATES = ("proposed", "ready", "doing", "built", "validated")     # model.OPEN_STATES
CLOSED_VERBS = ("close", "drop", "supersede")
ROWS = 12            # rows shown per list before "and N more"; the heading always carries the full count
RED_STALE_S = 1800   # a red reading older than this is not current: rm-red-dispatch.timer ticks every 10 min
DAY = 86400
SHOWINGS = "/mnt/d/ClaudeWork/rimmandrake/showings"
NATIVE_SHOWINGS = r"D:\ClaudeWork\rimmandrake\showings"
READY_RE = re.compile(r"READY TO SHOW|(?i:(?<!no )keeper save|pick image)")   # "no keeper save" is not a look
LEFT_RE = re.compile(r"^\s*LEFT OPEN:")
NEXT_RE = re.compile(r"\bNEXT:")

# the red dispatcher's decisions on an item it has not launched, in words (red_dispatch.decide)
RED_WAIT = {"launch": "launches at its next tick", "slots_full": "waits for a free red-fix slot",
            "night_cap": "waits for tomorrow night (tonight's launch cap is spent)",
            "held": "held: no fixer runs until a mod passes its Design Version (the nightly hold)",
            "account_hold": "waits for an account the Dispatcher picks", "disabled": "waits: red_dispatch is off",
            "no_cap": "waits: no spend cap is set for its model", "pipeline_paused": "waits: the pipeline is paused"}

RULE = ("An item is mod work when its id or title names a mod on this page (the rule the mod cards use, "
        "item_identity.named_mod) or a run on it recorded its mod; a name that ties between two mods is \"could not "
        "class\"; every other item is work that is not mod work.")

CANNOT = [
    "UNMEASURED: work promised in conversation and never filed on the ledger. No store holds it.",
    "UNMEASURED: a run launched by a program that marks nothing on its record is counted here as the Conductor's hand. "
    "Only the red dispatcher, left_open_continue and stop_resume mark their launches.",
    "UNMEASURED: a wait written only in a note (no `rimflow wait` or `block`) counts as waiting on the Conductor's hand.",
    "UNMEASURED: whether the Conductor window read a run's result. Only its acts (close, note, relaunch) are recorded.",
    "UNMEASURED: owed work written only in the Conductor log or a handoff. No program reads those back.",
]


# ---- small readers ----------------------------------------------------------------------------------------------

def g(o, k, default=None):
    """A field of a ledger item (model.Item) or of a test's dict."""
    if isinstance(o, dict):
        return o.get(k, default)
    return getattr(o, k, default)


def utc(s):
    if isinstance(s, (int, float)) and not isinstance(s, bool):
        return float(s)
    try:
        t = dt.datetime.fromisoformat(str(s).replace("Z", "+00:00"))
    except ValueError:
        return None
    return (t if t.tzinfo else t.replace(tzinfo=dt.timezone.utc)).timestamp()


def pac(t):
    """unix time -> '10:48 PM PST, Sun Nov 22' (or UNMEASURED)."""
    if not isinstance(t, (int, float)):
        return UNM
    x = dt.datetime.fromtimestamp(t, PAC)
    return "%s %s, %s%d" % (x.strftime("%I:%M %p").lstrip("0"), x.strftime("%Z"), x.strftime("%a %b "), x.day)


def age(t, now):
    """A filing's age as its Pacific date and whole days ('filed Sun Nov 14, 8 days'): no "minutes ago", so two builds
    a minute apart print the same row (the page's rule)."""
    if not isinstance(t, (int, float)):
        return "filed " + UNM
    d = int(max(0, now - t) // DAY)
    x = dt.datetime.fromtimestamp(t, PAC)
    return "filed %s%d, %s" % (x.strftime("%a %b "), x.day, "under a day" if d < 1 else "%d day%s" % (d, "" if d == 1 else "s"))


def game_line(r):
    """One game's state from game_lock.query: its name, state, holder and since when (clock time, never an age)."""
    import game_names  # noqa: E402
    try:
        n = game_names.show(r.get("game"))
    except Exception:   # noqa: BLE001  an unknown key prints as it is
        n = str(r.get("game"))
    st = str(r.get("state") or UNM)
    if st == "UNKNOWN":
        return "%s: could not look (%s)" % (n, r.get("cause"))
    who = (" by %s since %s, for: %s" % (r["seat"], r.get("since_local"), clip(r.get("purpose") or "?", 60))
           if r.get("seat") and st != "FREE" else "")
    return "%s %s%s" % (n, st.replace("_", " "), who)


def clip(s, n=110):
    s = " ".join(str(s or "").split())
    return s if len(s) <= n else s[:n - 1].rstrip() + "…"


def named(iid, title):
    """'<title in plain words> (`ID`)': never a bare id."""
    t = clip(title) if str(title or "").strip() else "(no title on the ledger)"
    return "%s (`%s`)" % (t, iid)


def classify(iid, title, mods, run_mods):
    """-> 'mod' | 'nonmod' | 'unclassed' (mod-or-not-by-one-rule)."""
    hit, mod = named_mod([w for w in str(iid or "").upper().split("_") if w], mods)
    if not hit:
        hit, mod = named_mod(re.findall(r"[A-Z0-9]+", str(title or "").upper()), mods, words_too=False)
    if hit:
        return "mod" if mod else "unclassed"
    return "mod" if iid in run_mods else "nonmod"


def launcher(rec, red_units):
    """Who launched a run (launcher-from-records)."""
    if rec.get("continued_from"):
        return "left_open_continue (program), continuing %s" % rec["continued_from"]
    if rec.get("resumed_from"):
        return "stop_resume (program), resuming %s" % rec["resumed_from"]
    if red_units is None:
        return UNM + " (the red dispatcher's state cannot be read)"
    if rec.get("unit") in red_units:
        return "the red dispatcher (program, rm-red-dispatch.timer)"
    return "the Conductor's hand (detached_helper.py launch)"


def is_live(rec):
    return (rec.get("live_state") or rec.get("status")) in ("running", "launching")


def run_end(rec, notes, spend):
    """-> (class, words) for an ended run on an open item (escalated-from-run-ends)."""
    st = rec.get("live_state") or rec.get("status")
    res = str(rec.get("result") or "")
    if st in ("refused", "launch_failed"):
        return "refused", "its launch was %s%s" % ("refused" if st == "refused" else "not started",
                                                  (": " + clip(rec.get("why"), 90)) if rec.get("why") else "")
    if st == "dead":
        return "stopped", "its unit died and its finish never ran"
    if res.startswith("success"):
        at = rec.get("at") or 0
        # a LEFT OPEN: note by anyone, or a NEXT: line the run wrote itself (a program's note about the run, such as
        # the clone-return note's "NEXT: restore it from that bundle", is not the run leaving work open)
        said = [n for n in notes if (utc(n.get("ts")) or 0) >= at and (
            LEFT_RE.search(str(n.get("text") or "")) or
            (n.get("role_unit") == rec.get("unit") and NEXT_RE.search(str(n.get("text") or ""))))]
        if said:
            return "left open", "left open: " + clip(said[-1].get("text"), 120)
        return "said nothing", "ended success and said nothing; the item is still open (no LEFT OPEN: note)"
    over = spend(rec)[2] if spend else UNM
    if over is True:
        return "capped", "stopped over its spend cap (%s)" % (res or "no result")
    if res.startswith("timeout"):
        return "stopped", "killed at its time limit"
    if "claude-error" in res:
        return "stopped", "ended in a model error"
    if res.startswith("unknown") or res.startswith("killed"):
        return "stopped", "killed or ended with no exit status (%s)" % res
    return "stopped", ("ended: " + res) if res else "ended, its result UNMEASURED"


# ---- the stores ---------------------------------------------------------------------------------------------------

def read_stores(lf, mods):
    """-> the inputs of section(): the ledger and run records from maturation_now.live_facts (`lf`: `_evs`, `_items`,
    `records`, `errors`), plus the red dispatcher, alarms, games and showings read here. Each store that cannot be read
    is None, its cause in `causes`."""
    s = {"mods": list(mods), "evs": lf.get("_evs"), "items": lf.get("_items"), "records": lf.get("records"),
         "causes": {}}
    if s["items"] is None:
        s["causes"]["the ledger"] = next((e for e in lf.get("errors") or [] if e.startswith("ledger")), "not read")
    if s["records"] is None:
        s["causes"]["the run records"] = next((e for e in lf.get("errors") or [] if e.startswith("run records")),
                                              "not read")
    try:
        import red_dispatch as RD  # noqa: E402
        d = RD.sdir()
        for key, name in (("red_reading", "reading.json"), ("red_state", "state.json")):
            try:
                with open(os.path.join(d, name), encoding="utf-8") as f:
                    s[key] = json.load(f)
            except (OSError, ValueError) as e:
                s[key] = None
                s["causes"]["the red dispatcher's %s" % name] = "%s: %s" % (e.__class__.__name__, e)
    except Exception as e:      # noqa: BLE001  no state dir: both stay unread, named
        s["red_reading"] = s["red_state"] = None
        s["causes"]["the red dispatcher"] = "%s: %s" % (e.__class__.__name__, e)
    try:
        import ops_watch as OW  # noqa: E402
        with open(os.path.join(str(OW.ops_dir()), "alarms.json"), encoding="utf-8") as f:
            s["alarms"] = json.load(f)
    except Exception as e:      # noqa: BLE001
        s["alarms"] = None
        s["causes"]["the alarms (ops_watch alarms.json)"] = "%s: %s" % (e.__class__.__name__, e)
    try:
        import game_lock  # noqa: E402
        s["games"] = [game_line(r) for r in game_lock.query_all()]
    except Exception as e:      # noqa: BLE001
        s["games"] = None
        s["causes"]["the game locks"] = "%s: %s" % (e.__class__.__name__, e)
    try:
        s["showings"] = sorted(os.listdir(SHOWINGS))
    except OSError as e:
        s["showings"] = None
        s["causes"]["the showings folder"] = "%s: %s" % (e.__class__.__name__, e)
    return s


def off_stores(why):
    return {"mods": [], "evs": None, "items": None, "records": None, "red_reading": None, "red_state": None,
            "alarms": None, "games": None, "showings": None, "causes": {"every store": why}}


# ---- the section --------------------------------------------------------------------------------------------------

def safe_section(s, now, spend=None):
    """section(), or a "failed" section naming the cause (four-answers-differ)."""
    try:
        return section(s, now, spend)
    except Exception as e:      # noqa: BLE001
        return {"state": "failed", "cause": "%s: %s" % (e.__class__.__name__, e), "causes": dict(s.get("causes") or {}),
                "cannot": list(CANNOT)}


def section(s, now, spend=None):
    items, evs, recs = s.get("items"), s.get("evs"), s.get("records")
    causes = dict(s.get("causes") or {})
    out = {"state": "ok", "causes": causes, "rule": RULE, "cannot": list(CANNOT), "now": now}
    if items is None:
        out["state"] = "blind"
        return out
    mods = s.get("mods") or []
    notes = {}
    for e in evs or []:
        if isinstance(e, dict) and e.get("event") == "note":
            notes.setdefault(e.get("id"), []).append(e)
    byitem, run_mods = {}, set()
    for r in recs or []:
        byitem.setdefault(r.get("item"), []).append(r)
        if (r.get("env") or {}).get("RM_CONTROL_MOD"):
            run_mods.add(r.get("item"))
    for v in byitem.values():
        v.sort(key=lambda r: r.get("at") or 0)
    red_state = s.get("red_state")
    red_units = None if red_state is None else {
        a.get("unit") for v in (red_state.get("items") or {}).values() for a in (v.get("attempts") or [])}
    rr = s.get("red_reading")
    red_age = None if not isinstance(rr, dict) else now - float(rr.get("at") or 0)
    red_cur = isinstance(rr, dict) and red_age <= RED_STALE_S
    red_items = (rr.get("items") or {}) if red_cur else {}

    klass, unclassed = {}, []
    for iid, it in items.items():
        if g(it, "state") in OPEN_STATES:
            k = classify(iid, g(it, "title"), mods, run_mods)
            klass[iid] = k
            if k == "unclassed":
                unclassed.append(iid)
    open_nm = sorted((i for i, k in klass.items() if k == "nonmod"), key=lambda i: (utc(g(items[i], "created_at")) or 0, i))
    out["unclassed"] = len(unclassed)
    out["unclassed_ids"] = sorted(unclassed)[:ROWS]
    out["open_total"] = len(open_nm)

    def title(i):
        return g(items.get(i), "title") if i in items else ""

    # each open non-mod item sits at one place (steps-as-they-are)
    place = {}
    for i in open_nm:
        it, rs = items[i], byitem.get(i, [])
        if recs is not None and any(is_live(r) for r in rs):
            place[i] = "runs"
        elif g(it, "wait_until"):
            place[i] = "date"
        elif g(it, "blocked"):
            place[i] = "item" if g(it, "blocked_kind") == "item" and g(it, "blocked_on") else "other"
        elif recs is None:
            place[i] = UNM
        elif (red_items.get(i) or {}).get("decision") in RED_WAIT:
            place[i] = "red"
        elif rs and (rs[-1].get("live_state") or rs[-1].get("status")) == "dead":
            place[i] = "ends"
        elif rs:
            place[i] = "acted"
        else:
            place[i] = "filed"
    cnt = {}
    for p in place.values():
        cnt[p] = cnt.get(p, 0) + 1

    def c(k, needs_runs=True):
        return UNM if (needs_runs and recs is None) else cnt.get(k, 0)

    red_word = ("could not look: %s" % causes.get("the red dispatcher's reading.json", causes.get("the red dispatcher", "")))\
        if rr is None else (("its reading is %d min old: not current" % (red_age // 60)) if not red_cur else None)
    out["steps"] = [
        {"n": 1, "step": "Filed on the ledger", "who": "program",
         "how": "rimflow (`cli.py file`), called by a run, an alarm (ops_watch) or the Conductor",
         "sits": c("filed"), "sits_words": "filed, never launched: no program launches these; they wait for the "
                                            "Conductor's hand"},
        {"n": 2, "step": "Launched", "who": "program in three cases; else by the Conductor's hand",
         "how": "the red dispatcher (rm-red-dispatch.timer: one capped fixer per nightly test failure); "
                "left_open_continue (a run that ended with a LEFT OPEN: note); stop_resume (a run a fleet stop killed). "
                "No program launches any other non-mod item: the Conductor window does, with detached_helper.py launch",
         "sits": (UNM if (recs is None or rr is None or not red_cur) else cnt.get("red", 0)),
         "sits_words": "waiting for the red dispatcher" + (" (%s)" % red_word if red_word else "")},
        {"n": 3, "step": "Runs", "who": "program", "how": "its own systemd unit (rm-detached-*)",
         "sits": c("runs"), "sits_words": "a run is live on it"},
        {"n": 4, "step": "Ends", "who": "program",
         "how": "detached_helper's finish writes the result file and a \"DETACHED RUN ENDED\" line in the Conductor log",
         "sits": c("ends"), "sits_words": "its unit died and its finish never ran"},
        {"n": 5, "step": "Read and acted on", "who": "by the Conductor's hand",
         "how": "no program reads a run's result: the Conductor window closes the item, relaunches it or leaves it",
         "sits": c("acted"), "sits_words": "a run ended and the item is still open"},
    ]
    out["parked"] = [("waiting on a date", cnt.get("date", 0)), ("blocked on another item", cnt.get("item", 0)),
                     ("held or blocked on something else", cnt.get("other", 0))]
    out["unplaced"] = cnt.get(UNM, 0)
    al = s.get("alarms")
    out["alarms"] = UNM if al is None else sorted(
        (str(v.get("item")), str(v.get("cause") or k)) for k, v in al.items()
        if isinstance(v, dict) and v.get("state") == "OPEN" and v.get("item"))

    # doing now
    if recs is None:
        out["doing"] = UNM
    else:
        rows = []
        for i in open_nm:
            for r in byitem.get(i, []):
                if is_live(r):
                    rows.append({"at": r.get("at"), "what": named(i, title(i)), "who": launcher(r, red_units),
                                 "since": pac(r.get("at")), "why": cause_line(i, items, evs), "unit": r.get("unit")})
        rows.sort(key=lambda x: (x["at"] or 0, x["unit"] or ""))
        out["doing"] = rows

    # next
    nx = []
    if rr is None:
        nx.append("The red dispatcher: could not look (%s)." % red_word.split(": ", 1)[-1])
    elif not red_cur:
        nx.append("The red dispatcher: its reading is %d min old (rm-red-dispatch.timer may have stopped); its rows "
                  "are not current." % (red_age // 60))
    else:
        w = [(i, x) for i, x in sorted(red_items.items()) if (x or {}).get("decision") in RED_WAIT]
        if not w:
            nx.append("The red dispatcher: no red item waits for a launch (its reading at %s lists %d red item%s)."
                      % (pac(float(rr.get("at") or 0)), len(red_items), "" if len(red_items) == 1 else "s"))
        for i, x in w:
            nx.append("The red dispatcher: %s %s." % (named(i, title(i)), RED_WAIT[x["decision"]]))
    if recs is None:
        nx.append("Continuations (left_open_continue): UNMEASURED, the run records cannot be read.")
    else:
        pend = [r for r in recs if isinstance(r.get("continue_plan"), dict) and r["continue_plan"].get("act") == "continue"
                and not r.get("continued_by") and not r.get("continue_refused")
                and (now - (r.get("ended") or 0)) < DAY and klass.get(r["continue_plan"].get("target") or r.get("item")) == "nonmod"]
        if not pend:
            nx.append("Continuations (left_open_continue): none planned and not yet launched in the last 24 h.")
        for r in sorted(pend, key=lambda r: r.get("ended") or 0):
            t = r["continue_plan"].get("target") or r.get("item")
            nx.append("left_open_continue continues %s on %s, planned %s; it waits for the run's clone to be given back."
                      % (r.get("unit"), named(t, title(t)), pac(r.get("ended"))))
    live = [i for i in open_nm if place.get(i) == "other" and g(items[i], "blocked_kind") == "live"]
    if live:
        games = s.get("games")
        gw = ("the games now: " + "; ".join(games)) if games else ("the games: could not look (%s)"
                                                                    % causes.get("the game locks", "not read"))
        nx.append("%d item%s wait%s on a live game (the item does not record which): %s. %s."
                  % (len(live), "" if len(live) == 1 else "s", "s" if len(live) == 1 else "",
                     "; ".join(named(i, title(i)) for i in live[:3]) + (" and %d more" % (len(live) - 3) if len(live) > 3 else ""), gw))
    if recs is None:
        nx.append("The Conductor's hand: UNMEASURED, the run records cannot be read.")
    else:
        hand = [i for i in open_nm if place.get(i) in ("filed", "acted", "ends")]
        if hand:
            o = hand[0]
            nx.append("The Conductor's hand: %d item%s wait%s for it and no program will launch them; the oldest is %s, "
                      "%s." % (len(hand), "" if len(hand) == 1 else "s", "s" if len(hand) == 1 else "",
                               named(o, title(o)), age(utc(g(items[o], "created_at")), now)))
        else:
            nx.append("The Conductor's hand: 0 items wait for it.")
    out["next"] = nx

    # closed in the last 24 h (an item open again now does not count)
    last = {}
    for e in evs or []:
        if isinstance(e, dict) and e.get("event") in CLOSED_VERBS:
            t = utc(e.get("ts"))
            if t is not None and now - DAY <= t <= now:
                last[e.get("id")] = (t, e.get("event"))
    cl = []
    for i, (t, verb) in last.items():
        it = items.get(i)
        if it is None or g(it, "state") in OPEN_STATES:
            continue
        if classify(i, g(it, "title"), mods, run_mods) == "nonmod":
            cl.append({"at": t, "verb": verb, "what": named(i, g(it, "title")), "when": pac(t)})
    cl.sort(key=lambda x: (-x["at"], x["what"]))
    by = {}
    for x in cl:
        by[x["verb"]] = by.get(x["verb"], 0) + 1
    out["closed"] = {"count": len(cl) if evs is not None else UNM, "by": by, "rows": cl}

    # open and why (no run on it)
    reasons = [("hand", "Waiting on the Conductor's hand"), ("red", "Waiting on the red dispatcher"),
               ("date", "Waiting on a date"), ("item", "Blocked on another item"),
               ("other", "Held or blocked on something else")]
    op = {}
    for key, head in reasons:
        keys = ("filed", "acted", "ends") if key == "hand" else (key,)
        if recs is None and key in ("hand", "red"):
            op[key] = {"head": head, "count": UNM, "rows": []}
            continue
        rows = []
        for i in open_nm:
            if place.get(i) not in keys:
                continue
            it = items[i]
            a = age(utc(g(it, "created_at")), now)
            if key == "date":
                wu = utc(g(it, "wait_until"))
                late = wu is not None and wu < now
                why = "%s until %s: %s" % ("LATE, waited" if late else "waits", pac(wu), clip(g(it, "wait_reason"), 90))
            elif key == "item":
                b = g(it, "blocked_on")
                why = "blocked on %s" % named(b, title(b))
            elif key == "other":
                why = "%s: %s" % ("held for the owner" if g(it, "blocked_kind") == "owner" else
                                  "blocked, kind %s" % (g(it, "blocked_kind") or "not named"),
                                  clip(g(it, "blocked_reason"), 90))
            elif key == "red":
                why = "the red dispatcher: " + RED_WAIT[red_items[i]["decision"]]
            else:
                rs = byitem.get(i, [])
                why = ("never launched" if not rs else "its last run ended %s" % pac(rs[-1].get("ended") or rs[-1].get("at")))
                if g(it, "kind") == "owed":
                    why += "; an owed item of the Conductor's"
            rows.append({"what": named(i, g(it, "title")), "age": a, "why": why})
        op[key] = {"head": head, "count": len(rows), "rows": rows}
    out["open"] = op

    # escalated for help
    if recs is None:
        out["escalated"] = UNM
    else:
        esc = []
        for i in open_nm:
            if place.get(i) not in ("acted", "ends"):
                continue
            r = byitem[i][-1]
            k, words = run_end(r, notes.get(i, []), spend)
            esc.append({"at": r.get("ended") or r.get("at") or 0, "what": named(i, title(i)), "kind": k,
                        "words": words, "when": pac(r.get("ended") or r.get("at"))})
        seen = {x["what"] for x in esc}
        for i, x in sorted(red_items.items()):
            if (x or {}).get("decision") == "stopped" and klass.get(i) == "nonmod" and named(i, title(i)) not in seen:
                esc.append({"at": float(rr.get("at") or 0), "what": named(i, title(i)), "kind": "red stopped",
                            "words": "the red dispatcher stopped on it: " + clip(x.get("why"), 110),
                            "when": pac(float(rr.get("at") or 0))})
        esc.sort(key=lambda x: (-x["at"], x["what"]))
        out["escalated"] = esc

    # ready for his review
    shows = s.get("showings")
    rd = []
    for i in open_nm:
        hit = [n for n in notes.get(i, []) if READY_RE.search(str(n.get("text") or ""))]
        if hit:
            n = hit[-1]
            where = ("%s\\%s" % (NATIVE_SHOWINGS, i)) if shows and i in shows else (
                "showings folder: could not look" if shows is None else "no showings folder by its name")
            rd.append({"at": utc(n.get("ts")) or 0, "what": named(i, title(i)), "when": pac(utc(n.get("ts"))),
                       "note": clip(n.get("text"), 140), "where": where})
    rd.sort(key=lambda x: (-x["at"], x["what"]))
    out["ready"] = rd
    return out


def cause_line(i, items, evs):
    """The filing's reason, else the title of the item that caused it, else 'no cause on the ledger'."""
    for e in reversed(evs or []):
        if isinstance(e, dict) and e.get("event") == "file" and e.get("id") == i:
            if e.get("why"):
                return clip(e["why"], 140)
            break
    cb = g(items.get(i), "caused_by")
    if cb:
        cb = cb[0] if isinstance(cb, (list, tuple)) and cb else cb
        return "caused by " + named(cb, g(items.get(cb), "title") if cb in items else "")
    return "no cause on the ledger"


# ---- render ---------------------------------------------------------------------------------------------------------

def _n(v):
    return UNM if v == UNM else str(v)


def _capped(rows, fmt):
    lines = [fmt(x) for x in rows[:ROWS]]
    if len(rows) > ROWS:
        lines.append("… and %d more" % (len(rows) - ROWS))
    return lines


def blocks(sec):
    """-> [(heading, [lines])]: the one content both renderers draw."""
    if sec.get("state") == "failed":
        return [("Failed", ["FAILED: the section could not be built (%s). No list below is an answer." % sec["cause"]])]
    looked = ["Could not look: %s (%s)." % (k, v) for k, v in sorted((sec.get("causes") or {}).items())]
    if sec.get("state") == "blind":
        return [("Could not look", looked + ["Every count of this section is UNMEASURED."]),
                ("What this section cannot see", sec["cannot"])]
    out = []
    head = ["Today there is no formal second pipeline: this is the path non-mod work takes now. %s" % sec["rule"],
            "Open items that are not mod work: %s. Could not class: %s%s." % (
                sec["open_total"], sec["unclassed"],
                (" (%s)" % ", ".join("`%s`" % x for x in sec["unclassed_ids"])) if sec["unclassed"] else "")]
    out.append(("", head + looked))
    st = ["%d. **%s**: %s. %s. Sitting here: **%s** (%s)." % (x["n"], x["step"], x["who"], x["how"], _n(x["sits"]),
                                                              x["sits_words"]) for x in sec["steps"]]
    st.append("Parked off the steps: " + "; ".join("%s **%s**" % (k, v) for k, v in sec["parked"]) + "."
              + (" Not placed (the run records cannot be read): %d." % sec["unplaced"] if sec["unplaced"] else ""))
    al = sec["alarms"]
    st.append("Alarms (ops_watch, program) file their one fixed item or reopen it; they launch nothing. Open alarms on "
              "items: " + (UNM if al == UNM else ("%d (%s)" % (len(al), ", ".join("`%s`" % i for i, _ in al)) if al
                                                   else "0")) + ".")
    out.append(("Steps today", st))
    d = sec["doing"]
    out.append(("Doing now (%s)" % (UNM if d == UNM else len(d)),
                [UNM + ": the run records cannot be read."] if d == UNM else
                (_capped(d, lambda x: "%s. Launched by %s, since %s. Why: %s" % (x["what"], x["who"], x["since"], x["why"]))
                 or ["none (looked: the run records; no run is live on a non-mod item)"])))
    out.append(("Next", sec["next"]))
    c = sec["closed"]
    out.append(("Closed in the last 24 h (%s%s)" % (_n(c["count"]), (": " + ", ".join(
        "%d %s" % (v, {"close": "closed", "drop": "dropped", "supersede": "superseded"}[k]) for k, v in sorted(c["by"].items())))
        if c["by"] else ""), (_capped(c["rows"], lambda x: "%s, %s %s" % (x["what"], x["verb"], x["when"]))
                              or ["none (looked: the ledger's close, drop and supersede events)"])))
    for key in ("hand", "red", "date", "item", "other"):
        o = sec["open"][key]
        out.append(("Open and why: %s (%s)" % (o["head"], _n(o["count"])),
                    [UNM + ": the run records cannot be read."] if o["count"] == UNM else
                    (_capped(o["rows"], lambda x: "%s, %s: %s" % (x["what"], x["age"], x["why"]))
                     or ["none (looked: the ledger)"])))
    e = sec["escalated"]
    if e == UNM:
        out.append(("Escalated for help (UNMEASURED)", [UNM + ": the run records cannot be read."]))
    else:
        by = {}
        for x in e:
            by[x["kind"]] = by.get(x["kind"], 0) + 1
        out.append(("Escalated for help (%d%s)" % (len(e), (": " + ", ".join("%d %s" % (v, k) for k, v in sorted(by.items())))
                                                 if by else ""),
                    _capped(e, lambda x: "%s: %s (%s)" % (x["what"], x["words"], x["when"]))
                    or ["none (looked: the run records and the red dispatcher's reading)"]))
    r = sec["ready"]
    out.append(("Ready for his review (%d)" % len(r),
                _capped(r, lambda x: "%s, %s: \"%s\" Where: %s" % (x["what"], x["when"], x["note"], x["where"]))
                or ["none (looked: the notes of open non-mod items for READY TO SHOW, keeper save, pick image)"]))
    out.append(("What this section cannot see", sec["cannot"]))
    return out


def _md_cell(s):
    return str(s).replace("\n", " ")


def markdown(sec):
    out = ["## %s" % TITLE, ""]
    for h, lines in blocks(sec):
        if h:
            out += ["**%s**" % h, ""]
        out += ["- " + _md_cell(x) for x in lines] + [""]
    return out


def _inline(s):
    s = html.escape(str(s), quote=False)
    s = re.sub(r"\*\*([^*]+)\*\*", r"<b>\1</b>", s)
    return re.sub(r"`([^`]+)`", r"<code>\1</code>", s)


def html_block(sec, colour="#e8eaee"):
    parts = ['<h2 style="color:%s">%s</h2>' % (colour, html.escape(TITLE))]
    for h, lines in blocks(sec):
        if h:
            parts.append('<h3 style="font-size:14px;margin:12px 0 4px">%s</h3>' % html.escape(h))
        parts.append("<ul>%s</ul>" % "".join("<li>%s</li>" % _inline(x) for x in lines))
    return "".join(parts)
