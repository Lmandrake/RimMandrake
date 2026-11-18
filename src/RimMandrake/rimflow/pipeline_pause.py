#!/usr/bin/env python3
"""pipeline_pause.py: the pipeline's one pause switch, a file no one edits by hand. No model, no tokens.

Item RIMMANDRAKE_ADD_PAUSE_ALL_AND_UP_NEXT_HOLD_LEAKED. The owner, 2026-11-18 ~10:27 AM PST: "I think we may need to have
Dispatch have a "pause all pipeline items" setting we can easily toggle (non-code-editing) for situations like this. We
really don't want work starting (or failing to start) when we expect otherwise."

The verbs live on maturation_dispatch.py (`pause`, `resume`, `next`) and `rimflow pipeline pause|resume|next`; this
module is the store every launch path reads (census: design/RimMandrake/pipeline_launch_paths_census_2026-11-18.md):
the Dispatch tick (every layer), the Dispatcher's pipeline roles (Designer, DesignerCodex: role_launch.owner_held and
the launch point) and red_dispatch.

The file is <maturation dispatch state dir>/pause.json (RM_PIPELINE_PAUSE_FILE overrides):
    {"all": ENTRY or null, "mods": {"<Mod>": ENTRY}, "history": [ {"act", "scope", "at", "by", "why", ...} ]}
    ENTRY = {"why", "by", "at" (epoch), "until" (epoch or null), "until_release" (bool)}
Absent means nothing is paused. A file that cannot be read or has the wrong shape means EVERYTHING is paused: a pause
that cannot be proved lifted is never read as running (the owner's four answers: an unreadable store is "could not
look", never "empty"). An entry whose `until` has passed is inactive at once (so a forecast with a moving clock sees it
end); the next applying tick moves it to history as "resumed by itself" and says so (expire).
"""
import contextlib
import datetime as dt
import fcntl
import json
import math
import os
import re
import time

HERE = os.path.dirname(os.path.abspath(__file__))
SAID_S = 86400      # an automatic resume is said on the status line this long


class Unreadable(Exception):
    pass


def path():
    p = os.environ.get("RM_PIPELINE_PAUSE_FILE")
    if p:
        return p
    import maturation_dispatch as MD     # noqa: E402  (late: maturation_dispatch imports this module)
    return os.path.join(MD.sdir(), "pause.json")


def key(mod):
    """design/concepts/Graffiti, Graffiti/ -> Graffiti (mod_owner_hold's key, so a concept path and a mod name agree)."""
    return os.path.basename(os.path.normpath(str(mod or "")))


def _num(v):
    return isinstance(v, (int, float)) and not isinstance(v, bool) and math.isfinite(v)


def _entry_ok(e):
    return (isinstance(e, dict) and isinstance(e.get("why"), str) and e["why"].strip() != "" and _num(e.get("at"))
            and (e.get("until") is None or _num(e["until"])))


def load(p=None):
    """-> the store ({"all": None, "mods": {}, "history": []} when absent). Raises Unreadable on a torn or misshapen file."""
    p = p or path()
    try:        # only a file that is not there is "nothing paused"; any other failure to read is Unreadable
        with open(p, encoding="utf-8") as f:
            d = json.load(f)
    except FileNotFoundError:
        return {"all": None, "mods": {}, "history": []}
    except (OSError, ValueError) as e:
        raise Unreadable("%s: %s: %s" % (p, type(e).__name__, e))
    if not isinstance(d, dict) or set(d) != {"all", "mods", "history"} or not isinstance(d["mods"], dict) \
            or not isinstance(d["history"], list) or not all(isinstance(h, dict) for h in d["history"]):
        raise Unreadable("%s: not a pause store (want exactly all, mods and history, history a list of records)" % p)
    bad = ([] if d.get("all") is None or _entry_ok(d["all"]) else ["all"]) + [
        m for m, e in (d.get("mods") or {}).items() if not _entry_ok(e)]
    if bad:
        raise Unreadable("%s: malformed pause entry for %s (each needs a why, an at, and an until that is a time or null)"
                         % (p, ", ".join(bad)))
    return {"all": d.get("all"), "mods": dict(d.get("mods") or {}), "history": list(d.get("history") or [])}


def _write(p, d):
    os.makedirs(os.path.dirname(p) or ".", exist_ok=True)
    tmp = "%s.tmp.%d" % (p, os.getpid())
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(d, f, indent=1, sort_keys=True)
    os.replace(tmp, p)


@contextlib.contextmanager
def _lock(p):
    os.makedirs(os.path.dirname(p) or ".", exist_ok=True)
    with open(p + ".lock", "a") as lf:
        fcntl.flock(lf, fcntl.LOCK_EX)
        try:
            yield
        finally:
            fcntl.flock(lf, fcntl.LOCK_UN)


def live(e, now):
    return bool(e) and (e.get("until") is None or now < float(e["until"]))


def state(now=None, p=None):
    """-> {"all": entry|None, "mods": {mod: entry}, "error": str|None, "said": [recent automatic resumes]}: the entries in
    force at `now`. Never raises: an unreadable store is returned as error, and reason() reads it as paused."""
    now = time.time() if now is None else now
    try:
        d = load(p)
    except Unreadable as e:
        return {"all": None, "mods": {}, "error": str(e), "said": []}
    return {"all": d["all"] if live(d["all"], now) else None,
            "mods": {m: e for m, e in d["mods"].items() if live(e, now)}, "error": None,
            "said": [h for h in d["history"] if h.get("act") == "auto_resume" and now - float(h.get("at") or 0) < SAID_S]}


def reason(st, mod=None):
    """-> why `mod` (None: the whole pipeline) may not start anything under the state `st`, or None."""
    if st.get("error"):
        return "PIPELINE PAUSED: the pause state cannot be read (%s), so nothing starts until it can" % st["error"]
    if st.get("all"):
        return "PIPELINE PAUSED (all): %s" % line(st["all"])
    e = (st.get("mods") or {}).get(key(mod)) if mod else None
    return "PIPELINE PAUSED (%s): %s" % (key(mod), line(e)) if e else None


def blocks(mod=None, now=None, p=None):
    return reason(state(now, p), mod)


def pac(t):
    return dt.datetime.fromtimestamp(float(t)).strftime("%Y-%m-%d %-I:%M %p")


def line(e):
    return "%s; by %s since %s; %s" % (e.get("why"), e.get("by") or "?", pac(e["at"]),
                                       "until %s, then resumes by itself" % pac(e["until"]) if e.get("until")
                                       else "until released (`maturation_dispatch.py resume%s --why ...`)" % (
                                           " %s" % e["mod"] if e.get("mod") else ""))


REL = re.compile(r"^\+?(\d+(?:\.\d+)?)\s*(m|min|h|hr|d)$")


def parse_until(text, now=None):
    """'+90m' '+2h' '+1d' | 'HH:MM' (this machine's local clock, the next such time) | an ISO date-time (naive = local)
    | an epoch -> epoch. Raises ValueError on anything else or on a time not in the future."""
    now = time.time() if now is None else now
    s = str(text or "").strip().lower()
    m = REL.match(s)
    if m:
        t = now + float(m.group(1)) * {"m": 60, "min": 60, "h": 3600, "hr": 3600, "d": 86400}[m.group(2)]
    elif re.match(r"^\d{1,2}:\d{2}$", s):
        hh, mm = (int(x) for x in s.split(":"))
        base = dt.datetime.fromtimestamp(now)
        cand = base.replace(hour=hh, minute=mm, second=0, microsecond=0)
        if cand.timestamp() <= now:
            cand += dt.timedelta(days=1)
        t = cand.timestamp()
    elif re.match(r"^\d{9,11}(\.\d+)?$", s):
        t = float(s)
    else:
        try:
            x = dt.datetime.fromisoformat(str(text).strip())
        except ValueError:
            raise ValueError("--until %r: give +90m, +2h, HH:MM (local), an ISO date-time or an epoch" % text)
        t = x.timestamp()
    if t <= now:
        raise ValueError("--until %r is not in the future (%s)" % (text, pac(t)))
    return t


def pause(mod, why, by, until=None, now=None, p=None):
    """Pause `mod` (None: the whole pipeline). -> the entry written. A second pause on the same scope replaces it."""
    now = time.time() if now is None else now
    if not str(why or "").strip():
        raise ValueError("--why is empty")
    p = p or path()
    with _lock(p):
        try:
            d = load(p)
        except Unreadable as err:
            # a torn store reads as everything paused: only a pause of everything may replace it (its bytes kept
            # beside it); a one-mod pause over it would un-pause every other mod
            if mod:
                raise Unreadable("%s; a pause of one mod would lift the pause this reads as on every other mod: pause "
                                 "the whole pipeline (no MOD) to replace it" % err)
            if os.path.exists(p):
                os.replace(p, "%s.unreadable.%d" % (p, int(now)))
            d = {"all": None, "mods": {}, "history": []}
        e = {"why": why.strip(), "by": by, "at": now, "until": until, "until_release": until is None}
        if mod:
            e["mod"] = key(mod)
            d["mods"][key(mod)] = e
        else:
            d["all"] = e
        d["history"].append(dict(e, act="pause", scope=key(mod) if mod else "all"))
        _write(p, d)
    return e


def resume(mod, why, by, now=None, p=None):
    """Lift the pause on `mod` (None: the whole pipeline). -> the entry lifted, or None when none stood."""
    now = time.time() if now is None else now
    p = p or path()
    with _lock(p):
        d = load(p)     # an unreadable store refuses: resuming over bytes nobody can read would guess
        was = d["mods"].pop(key(mod), None) if mod else d.get("all")
        if not mod:
            d["all"] = None
        d["history"].append({"act": "resume", "scope": key(mod) if mod else "all", "at": now, "by": by,
                             "why": str(why or "").strip(), "was": was})
        _write(p, d)
    return was


def note(rec, p=None):
    """Append one record to the store's history (--stop-live's stopped runs, owed their voiding)."""
    p = p or path()
    with _lock(p):
        d = load(p)
        d["history"].append(rec)
        _write(p, d)


def expire(now=None, p=None):
    """Move every entry whose until has passed to history as an automatic resume. -> one line per resume (said)."""
    now = time.time() if now is None else now
    p = p or path()
    try:
        d = load(p)
    except Unreadable:
        return []
    gone = ([("all", d["all"])] if d["all"] and not live(d["all"], now) else []) + [
        (m, e) for m, e in d["mods"].items() if not live(e, now)]
    if not gone:
        return []
    said = []
    with _lock(p):
        d = load(p)
        for scope, e in gone:
            if scope == "all":
                if d["all"] and not live(d["all"], now):
                    d["all"] = None
                else:
                    continue
            elif scope in d["mods"] and not live(d["mods"][scope], now):
                d["mods"].pop(scope)
            else:
                continue
            txt = "RESUMED BY ITSELF %s (%s): the pause until %s ended (it was: %s, by %s)" % (
                scope, pac(now), pac(e["until"]), e.get("why"), e.get("by"))
            d["history"].append({"act": "auto_resume", "scope": scope, "at": now, "by": "maturation_dispatch tick",
                                 "why": txt, "was": e})
            said.append(txt)
        _write(p, d)
    return said


def summary(st, now=None):
    """-> the reading's pipeline_pause block: {"all", "mods", "error", "said"} with a line per entry."""
    return {"all": line(st["all"]) if st.get("all") else None,
            "mods": {m: line(e) for m, e in (st.get("mods") or {}).items()},
            "error": st.get("error"), "said": [h.get("why") for h in st.get("said") or []]}


def status_lines(st):
    out = []
    if st.get("error"):
        out.append("PIPELINE PAUSED: the pause state cannot be read (%s); nothing starts until it can" % st["error"])
    if st.get("all"):
        out.append("PIPELINE PAUSED (all): %s" % line(st["all"]))
    for m, e in sorted((st.get("mods") or {}).items()):
        out.append("PAUSED %s: %s" % (m, line(e)))
    for h in st.get("said") or []:
        out.append(str(h.get("why")))
    return out
