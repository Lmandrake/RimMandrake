#!/usr/bin/env python3
r"""game_health_check.py - the standing game health check (HEALTH_CHECK_MONITOR_MEMORY_TPS_OVER_TIME, owner C24).

The owner, C24 (design/RimMandrake/mod_audit/OWNER_RULINGS.md): "monitor the memory, TPS as a function of time to make
sure we don't get into dangerous territory. This should be a health check we monitor and maintain just like 'is the
game loadable right now?' and 'how many errors are we currently producing in the log?' When it goes worse, we should
take it seriously and have hard conversations or debug why."

One row per FULL-LIST game session (session row `mods` >= full_list_min_mods), read from the JawaBench TPS record
(<LocalLow>\JawaBench\tps\tps_<start>_<session>_<pid>_<seg>.jsonl, design/RimMandrake/tps_record.md):

  load   reached the menu, a game loaded, load seconds (context `upS` at the menu row; UNMEASURED before the field)
  end    clean shutdown, or ended without one (a newer session started, or no row for ended_after_min)
  mem    managed (Mono GC heap, `heapMB`), private bytes (`privateMB`), native (Unity allocators, `unityReservedMB`),
         GPU driver (`gfxMB`): each a curve per bucket_min of time since the first game load, its peak, and its growth
         per hour (Theil-Sen) over the in-game span
  tps    run-window ratio per bucket, median, decay first-vs-last window at the dominant speed, stalls, longest stall
  log    errors and warnings the companion counted (`logErr`/`logWarn`, always-on), and whether Verse.Log's cap hit

A source the record does not carry is UNMEASURED with its reason, never 0. The row's `breaches` are the limits in
game_health_thresholds.json it crossed; ops_watch's tps family reads the newest row and rings OPS_GAME_HEALTH_DEBUG
(a debug item) while it has any.

Each breach also carries an `attribution` (row["attribution"][key], plain sentences read from the same record), so an
alarm says what the session was doing when the limit fell (OPS_GAME_HEALTH_DEBUG_PXQI, 2026-11-04: an Operations dig
and a builder dig each re-derived these from raw rows): memory breaches name the largest map the session generated and
the growth AFTER the last map change (a bigger map is scale, growth on a fixed map set is a leak); an error-count
breach names the error classes MEASURED from the archived Player.log (session ee0fbaa8: the save loaded inside the
biggest jump was once called dead def names by assumption, which sent Operations away from 3476 chunk errors and 3200
Beer errors that were no such thing), the biggest scan-to-scan jump and the save loaded inside it, and how many were
already queued at the first read (the cold load); the lower bound says whether the queue was already full at the first read (load messages evicted) and the largest scan-to-scan
rise of Verse.Log's message count (>= the queue size proves an eviction between two scans). Attribution never
removes or softens a breach. `explain [--session ID]` re-reads a session from disk and prints it.

A finished session stays the newest row until the next full-list session, so once its breaches are debugged the alarm
would re-ring on the same numbers for good (session e50b27df re-opened this item 19 times). `debugged --session ID --item
ITEM --why "..."` writes (session, its current breach keys, item, why) into the COMMITTED game_health_debugged.json;
`latest` then carries `open_breaches` (breaches not debugged) and `debugged` ({key: "ITEM: why"}), and ops_watch counts
only the open ones. No limit changes: a key not debugged, and every other session, still rings.

    python3 src/RimMandrake/Utils/game_health_check.py record [--dry-run] [--json]   append new finished sessions
    python3 src/RimMandrake/Utils/game_health_check.py report [--last N] [--curve]   sessions over time (+ newest curve)
    python3 src/RimMandrake/Utils/game_health_check.py latest --json                 the newest recorded row (ops_watch)
    python3 src/RimMandrake/Utils/game_health_check.py debugged --session ID --item ITEM --why "..."
                                                                                     record a session's breaches as debugged
    python3 src/RimMandrake/Utils/game_health_check.py fields [--session ID]          live proof: exit 0 when the newest
                                                                                     session's context rows carry the
                                                                                     companion memory/log fields;
                                                                                     exit 2 UNMEASURED when the deployed
                                                                                     companion (or the session's writer)
                                                                                     serves none of them
History (outside git): $RM_GAME_HEALTH_DIR/history.jsonl, default D:\ClaudeWork\rimmandrake\game_health.
$RM_GAME_HEALTH_TPS_DIR overrides where `record` reads the TPS record, $RM_GAME_HEALTH_ACKS the debugged record (selftests).
"""
from __future__ import annotations

import argparse
import collections
import json
import math
import os
import re
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)
import tps_record as T  # noqa: E402

SCHEMA = 1
THRESHOLDS = os.path.join(HERE, "game_health_thresholds.json")
DEBUGGED = os.path.join(HERE, "game_health_debugged.json")
MEM_FIELDS = (("managed", "heapMB"), ("private", "privateMB"), ("native", "unityReservedMB"), ("gfx", "gfxMB"))
LIVE_FIELDS = ("privateMB", "unityReservedMB", "unityAllocMB", "logErr", "logWarn", "upS")


def history_dir():
    return os.environ.get("RM_GAME_HEALTH_DIR", "/mnt/d/ClaudeWork/rimmandrake/game_health")


def history_path():
    return os.path.join(history_dir(), "history.jsonl")


def load_rules(path=None):
    with open(path or THRESHOLDS) as fh:
        return json.load(fh)


def U(why):
    return {"m": "UNMEASURED", "why": why}


def is_m(x):
    return not (isinstance(x, dict) and x.get("m") == "UNMEASURED")


# ------------------------------------------------------------------ reading the record, one session at a time
def sessions_on_disk(directory):
    """{session: [paths in segment order]} from segment names alone (no file opened)."""
    out = {}
    for p in T.list_files(directory):
        m = T.SEGMENT_RE.match(os.path.basename(p))
        if m:
            out.setdefault(m.group(2), []).append(p)
    return out


def first_row(path):
    try:
        with open(path, "rb") as fh:
            ln = fh.readline()
        return T.loads_strict(ln.decode("utf-8"))
    except (OSError, ValueError, UnicodeDecodeError):
        return None


def read_session(paths):
    """Valid rows of one session in seq order, plus counts of what was refused (never silently dropped)."""
    rows, bad = [], 0
    for p in paths:
        try:
            fh = open(p, "rb")
        except OSError:
            bad += 1
            continue
        with fh:
            for raw in fh:
                if not raw.endswith(b"\n"):
                    bad += 1
                    continue
                try:
                    r = T.loads_strict(raw.decode("utf-8"))
                except (ValueError, UnicodeDecodeError):
                    bad += 1
                    continue
                if not T._valid(r):
                    bad += 1
                    continue
                r["_t"] = T._epoch(r["utc"])
                rows.append(r)
    rows.sort(key=lambda r: (r.get("seq") if isinstance(r.get("seq"), int) else 1 << 40, r["_t"]))
    return rows, bad


# ------------------------------------------------------------------ arithmetic
def median(xs):
    xs = sorted(xs)
    n = len(xs)
    if not n:
        return None
    return xs[n // 2] if n % 2 else (xs[n // 2 - 1] + xs[n // 2]) / 2.0


def theil_sen(pts, cap=300):
    """Median of pairwise slopes of (t, v); robust to one GC sawtooth outlier. None under 3 points."""
    if len(pts) < 3:
        return None
    if len(pts) > cap:
        step = len(pts) / float(cap)
        pts = [pts[int(i * step)] for i in range(cap)]
    s = [(b[1] - a[1]) / (b[0] - a[0]) for i, a in enumerate(pts) for b in pts[i + 1:] if b[0] > a[0]]
    return median(s)


def num(x):
    return T._num(x)


# ------------------------------------------------------------------ one session -> one row
def summarize(sess, rows, bad, rules, now=None, superseded=False):
    now = time.time() if now is None else now
    head = next((r for r in rows if r.get("kind") == "session"), {})
    kinds = {}
    for r in rows:
        kinds.setdefault(r.get("kind"), []).append(r)
    t_first, t_last = rows[0]["_t"], rows[-1]["_t"]
    shutdown = bool(kinds.get("shutdown") or kinds.get("shutdown-complete"))
    # a hang or a machine sleep can go quiet for a long time and recover, so silence alone ends a session only after
    # ended_after_min; a newer session on disk means this process is gone (GPT review 2026-11-02, P2)
    ended = shutdown or superseded or (now - t_last) > rules["ended_after_min"] * 60
    game_rows = kinds.get("game") or []
    t0 = game_rows[0]["_t"] if game_rows else None
    ctx = kinds.get("context") or []
    samples = kinds.get("sample") or []
    row = {"v": SCHEMA, "session": sess, "pid": head.get("pid"), "start": head.get("utc") or rows[0]["utc"],
           "end": rows[-1]["utc"], "durationMin": round((t_last - t_first) / 60.0, 1), "mods": head.get("mods"),
           "modDigest": head.get("modDigest"), "build": head.get("build"), "engine": head.get("engine"),
           "rows": len(rows), "badRows": bad, "finished": ended,
           "saves": sorted({r.get("save") for r in game_rows if r.get("save")})}
    m = {}
    # load
    m["load.reached_menu"] = bool(kinds.get("menu")) or bool(game_rows)
    m["load.game_loaded"] = bool(game_rows)
    ups = [(r["_t"], num(r.get("upS")), num(r.get("mono"))) for r in ctx if num(r.get("upS")) is not None]
    menu = kinds.get("menu")
    if ups and menu and ups[0][2] is not None and num(menu[0].get("mono")) is not None:
        # upS = seconds since process start at a context row; carry it back to the first menu row by mono
        m["load.seconds"] = round(ups[0][1] - (ups[0][2] - num(menu[0]["mono"])), 1)
    else:
        m["load.seconds"] = U("no context row carries upS (companion predates the field) or no menu row")
    m["end.clean"] = shutdown if ended else U("session still open")
    # memory curves
    min_span = rules["growth_min_span_min"] * 60
    bucket = rules["bucket_min"] * 60.0
    curves = {}
    for name, f in MEM_FIELDS:
        src = [(r["_t"], num(r.get(f))) for r in ctx + samples if num(r.get(f)) is not None]
        src = [(t, v) for t, v in src if v > 0]        # 0 means "not read" (Mono WorkingSet64, release gfx driver)
        if not src:
            why = "no row carries %s>0" % f + (" (a release player reads 0)" if f == "gfxMB" else
                                              " (companion predates the field)" if f != "heapMB" else "")
            m["mem.%s_peak_mb" % name] = U(why)
            m["mem.%s_growth_mb_per_h" % name] = U(why)
            continue
        m["mem.%s_peak_mb" % name] = round(max(v for _, v in src), 1)
        after = sorted((t, v) for t, v in src if t0 is not None and t >= t0)
        if len(after) >= 3 and after[-1][0] - after[0][0] >= min_span:     # the FIELD's own span, not the session's
            m["mem.%s_growth_mb_per_h" % name] = round(theil_sen(after) * 3600.0, 1)
        else:
            m["mem.%s_growth_mb_per_h" % name] = U("under %d min of in-game time" % rules["growth_min_span_min"])
        if t0 is not None:
            cb = {}
            for t, v in after:
                cb.setdefault(int((t - t0) // bucket), []).append(v)
            curves[name] = [[k * rules["bucket_min"], round(median(v), 1), round(max(v), 1)] for k, v in sorted(cb.items())]
    # tps
    run = [r for r in samples if r.get("state") == T.STATE_RUN and num(r.get("ratio")) is not None]
    allst = [i for i in kinds.get("incident") or [] if i.get("type") == "stall"]
    stalls = [i for i in allst if i.get("longEvent") is not True]     # a long event is the engine loading on purpose
    m["tps.stalls"] = len(stalls)
    m["tps.stall_max_s"] = round(max((num(i.get("unexplainedS")) or 0 for i in stalls), default=0.0), 2)
    m["tps.longevent_max_s"] = round(max((num(i.get("unexplainedS")) or 0 for i in allst if i not in stalls), default=0.0), 2)
    if run:
        mults = {}
        for r in run:
            mults[r.get("mult")] = mults.get(r.get("mult"), 0) + 1
        dom = max(mults, key=lambda k: (mults[k], k or 0))
        m["tps.ratio_median"] = round(median([r["ratio"] for r in run]), 3)
        m["tps.dominant_mult"] = dom
        d = [r for r in run if r.get("mult") == dom and t0 is not None and r["_t"] >= t0]
        w = rules["ratio_window_min"] * 60
        if d and d[-1]["_t"] - d[0]["_t"] >= 2 * w:
            a = median([r["ratio"] for r in d if r["_t"] - d[0]["_t"] <= w])
            b = median([r["ratio"] for r in d if d[-1]["_t"] - r["_t"] <= w])
            m["tps.ratio_first"], m["tps.ratio_last"] = round(a, 3), round(b, 3)
            m["tps.ratio_decay_pct"] = round((a - b) / a * 100.0, 1) if a > 0 else U("first-window ratio is 0")
        else:
            m["tps.ratio_decay_pct"] = U("under %d min of run windows at speed x%s" % (2 * rules["ratio_window_min"], dom))
        if t0 is not None:
            cb = {}
            for r in run:
                if r["_t"] >= t0:
                    cb.setdefault(int((r["_t"] - t0) // bucket), []).append(r)
            curves["ratio"] = [[k * rules["bucket_min"], round(median([r["ratio"] for r in v]), 3),
                                round(median([num(r.get("tps")) or 0 for r in v]), 1)] for k, v in sorted(cb.items())]
    else:
        for k in ("tps.ratio_median", "tps.ratio_decay_pct"):
            m[k] = U("no run window (never unpaused)")
    # log
    # the companion writes logErr/logWarn only once a queue scan has succeeded (null before: never a healthy zero)
    le = [(num(r.get("logErr")), num(r.get("logWarn"))) for r in ctx if num(r.get("logErr")) is not None]
    caps = [r.get("logCapReached") for r in ctx if isinstance(r.get("logCapReached"), bool)]
    m["log.cap_reached"] = any(caps) if caps else U("no context row carries a readable logCapReached")
    if le:
        m["log.errors"] = int(le[-1][0])
        m["log.warnings"] = int(le[-1][1] or 0)
        # entries evicted from Verse.Log's 1000-entry queue between two scans were never counted: the count is a floor
        m["log.errors_lower_bound"] = any(r.get("logErrLowerBound") is True for r in ctx)
        if t0 is not None:
            cb = {}
            for r in ctx:
                if num(r.get("logErr")) is not None and r["_t"] >= t0:
                    cb[int((r["_t"] - t0) // bucket)] = int(r["logErr"])
            curves["log_errors"] = [[k * rules["bucket_min"], v] for k, v in sorted(cb.items())]
    else:
        for k in ("log.errors", "log.warnings", "log.errors_lower_bound"):
            m[k] = U("no context row carries logErr (companion predates the always-on counter, or no log scan "
                     "succeeded)")
    row["metrics"] = m
    row["curves"] = curves
    row["curveAxis"] = "minutes since first game load; mem [min, median MB, max MB]; ratio [min, median ratio, median tps]"
    row["breaches"] = breaches(m, rules)
    logrow = (kinds.get("log") or [{}])[-1]
    if logrow.get("archived"):
        row["playerLog"] = logrow["archived"]
    row["attribution"] = attribute(row["breaches"], kinds, ctx, t0, m, row.get("playerLog"))
    row["unmeasured"] = sorted(k for k, v in m.items() if not is_m(v))
    return row


QUEUE_MAX = 1000      # Verse.LogMessageQueue.maxMessages (decompiled 1.6, JawaBenchSessionHealth.cs header)
REF_CELLS = 250 * 250  # the default map size, the unit the attribution states map area in


def _cells(r):
    tot, big = 0, None
    for mp in r.get("maps") or []:
        try:
            w, h = (int(x) for x in str(mp.get("size", "")).split("x"))
        except ValueError:
            continue
        tot += w * h
        if big is None or w * h > big[0]:
            big = (w * h, "%s %s" % (mp.get("size"), mp.get("biome")), mp.get("things"))
    return tot, big


def _hm(t):
    return time.strftime("%H:%MZ", time.gmtime(t))


LOG_FRAMES = ("  at ", "    - ", "(wrapper", "[Ref ", " [0x", "Subnode", "<li", "(Filename", "UnityEngine.")


def log_census(player_log, top=5):
    """Sentences counted from a session's archived Player.log: what the errors ARE, never assumed from what was running.
    The log does not mark which lines are errors, so the repeat list says it holds plain messages too."""
    if not player_log:
        return ["no archived log for this session: its error classes are UNMEASURED"]
    p = str(player_log)
    if not os.path.exists(p):
        p = p.replace("\\", "/")
        if len(p) > 2 and p[1] == ":":
            p = "/mnt/%s%s" % (p[0].lower(), p[2:])
    try:
        with open(p, errors="replace") as fh:
            lines = [ln.rstrip("\n") for ln in fh]
    except OSError as e:
        return ["archived log unreadable, its error classes are UNMEASURED: %s" % e]
    rep, exc = collections.Counter(), collections.Counter()
    refs = 0
    for ln in lines:
        if not ln.strip() or ln.startswith(LOG_FRAMES):
            continue
        k = re.sub(r"\d+", "#", ln[:70])
        rep[k] += 1
        refs += ln.startswith("Could not load reference")
        if "exception" in ln[:60].lower():
            exc[k] += 1
    show = lambda c: "; ".join("%dx %s" % (n, k) for k, n in c.most_common(top)) or "none"
    return ["archived log, most repeated lines (errors and plain messages alike): %s" % show(rep),
            "archived log, %d 'Could not load reference' lines (dead names in a save); exception lines: %s" % (
                refs, show(exc))]


def attribute(brs, kinds, ctx, t0, m, player_log=None):
    """{breach key: [sentence, ...]} from the record itself; empty when nothing breached. Read-only, no verdict."""
    out = {}
    keys = {b["key"] for b in brs}
    if not keys:
        return out
    tl = [(r["_t"],) + _cells(r) for r in ctx if r.get("maps")]
    mapset = []
    if tl:
        top = max(tl, key=lambda x: x[1])
        if top[2]:
            mapset.append("largest map set %.1fx a 250x250 map (biggest %s, %s things) from %s" % (
                top[1] / float(REF_CELLS), top[2][1], top[2][2], _hm(top[0])))
        changes = [tl[0]] + [b for a, b in zip(tl, tl[1:]) if b[1] != a[1]]
        if len(changes) > 1:
            mapset.append("map set changed %d times: %s" % (len(changes) - 1, ", ".join(
                "%s %.1fx" % (_hm(c[0]), c[1] / float(REF_CELLS)) for c in changes[1:][:8])))
    else:
        mapset.append("no context row lists maps: map size UNMEASURED")
    saves = ["%s %s" % (_hm(g["_t"]), g.get("save") or "(new game)") for g in kinds.get("game") or []]
    mapset.append("games loaded: %s" % (", ".join(saves[:8]) or "none"))
    for k in keys:             # every breach gets the session's context; the specific ones below add their own
        out[k] = list(mapset)
    if any(k.startswith("mem.") for k in keys):
        mem = [(r["_t"], num(r.get("heapMB")), num(r.get("privateMB"))) for r in ctx]
        s = list(mapset)
        if tl:
            last = changes[-1][0]
            for i, name in ((1, "managed"), (2, "private")):
                pts = [(t, x[i]) for x in mem for t in (x[0],) if t >= last and x[i] is not None and x[i] > 0]
                if len(pts) >= 3 and pts[-1][0] - pts[0][0] >= 1800:
                    s.append("%s growth after the last map change (%s, %.0f min): %.1f MB/h" % (
                        name, _hm(last), (pts[-1][0] - pts[0][0]) / 60.0, theil_sen(pts) * 3600.0))
                else:
                    s.append("%s growth after the last map change: UNMEASURED (under 30 min on that map set)" % name)
        for k in sorted(x for x in keys if x.startswith("mem.")):
            out[k] = s
    le = [r for r in ctx if num(r.get("logErr")) is not None]
    if "log.errors" in keys and le:
        s = out["log.errors"] + ["%d errors already counted at the first queue read (%s, after the cold load)" % (
            int(le[0]["logErr"]), _hm(le[0]["_t"]))]
        jumps = sorted(((int(b["logErr"]) - int(a["logErr"]), a, b) for a, b in zip(le, le[1:])),
                       key=lambda x: -x[0])
        if jumps and jumps[0][0] > 0:
            d, a, b = jumps[0]
            loads = [g for g in kinds.get("game") or [] if a["_t"] <= g["_t"] <= b["_t"]]
            tail = ""
            if loads:
                sv = loads[-1].get("save")
                tail = " while loading save %s" % sv if sv else " while a new game started (no save named)"
            s.append("biggest jump +%d between %s and %s%s" % (d, _hm(a["_t"]), _hm(b["_t"]), tail))
        if player_log:
            s.append("full log archived at shutdown: %s" % player_log)
        out["log.errors"] = log_census(player_log) + s       # first: ops_watch forwards the first 600 chars of the join
    if "log.cap_reached" in keys:
        out["log.cap_reached"] = log_census(player_log) + out["log.cap_reached"]
    if "log.errors_lower_bound" in keys and le:
        s = out["log.errors_lower_bound"]
        if le[0].get("logErrLowerBound") is True:
            s.append("the first queue read (%s) already found the %d-entry queue full: messages from the cold load "
                     "were evicted before any scan; the flag is sticky, so later evictions cannot be told from it" % (
                         _hm(le[0]["_t"]), QUEUE_MAX))
        else:
            fl = next((r for r in le if r.get("logErrLowerBound") is True), None)
            if fl:
                s.append("the flag first rose at %s, after the first read" % _hm(fl["_t"]))
        mc = [(r["_t"], num(r.get("logMsgs"))) for r in ctx if num(r.get("logMsgs")) is not None]
        rises = [(b[1] - a[1], b[0]) for a, b in zip(mc, mc[1:]) if b[1] >= a[1]]   # a drop is a count reset
        if rises:
            big = max(rises)
            s.append("largest scan-to-scan rise of Verse.Log's message count: %d at %s (%s)" % (
                int(big[0]), _hm(big[1]), "an eviction between two scans" if big[0] >= QUEUE_MAX else
                "under the queue size: no scan interval proves an eviction"))
            if big[0] >= QUEUE_MAX:
                s.append("which source wrote each rise: Utils/log_rise_census.py --session <id> --log <archived log> --record <tps dir>")
        else:
            s.append("no two context rows carry logMsgs: scan-to-scan eviction UNMEASURED")
        out["log.errors_lower_bound"] = s
    return out


OPS = {">": lambda a, b: a > b, ">=": lambda a, b: a >= b, "<": lambda a, b: a < b, "==": lambda a, b: a == b}


def breaches(m, rules):
    out = []
    for lim in rules["limits"]:
        v = m.get(lim["key"])
        if v is None or not is_m(v):
            continue
        if isinstance(lim["value"], bool) != isinstance(v, bool):
            continue
        if OPS[lim["op"]](v, lim["value"]):
            out.append({"key": lim["key"], "value": v, "op": lim["op"], "limit": lim["value"], "why": lim["why"]})
    return out


# ------------------------------------------------------------------ debugged sessions
def acks_path():
    return os.environ.get("RM_GAME_HEALTH_ACKS") or DEBUGGED


def load_acks(path=None):
    """The committed debugged record as a dict; a missing file is an empty record, a corrupt one raises (an unreadable
    record must not silently clear or keep an alarm)."""
    try:
        with open(path or acks_path()) as fh:
            d = json.load(fh)
    except FileNotFoundError:
        return {"debugged": []}
    if not isinstance(d, dict) or not isinstance(d.get("debugged", []), list):
        raise ValueError("%s: 'debugged' is not a list" % (path or acks_path()))
    d.setdefault("debugged", [])
    return d


def split_breaches(row, acks=None):
    """(open breaches, {key: "ITEM: why"}) for one history row against the debugged record. A record row matches the
    row's session by prefix (at least 8 characters, as explain prints) and debugs only the keys it names."""
    acks = load_acks() if acks is None else acks
    sid = str(row.get("session") or "")
    done = {}
    for a in acks.get("debugged") or []:
        s = str(a.get("session") or "") if isinstance(a, dict) else ""
        if len(s) >= 8 and sid.startswith(s):
            for k in a.get("keys") or []:
                done[k] = "%s: %s" % (a.get("item"), a.get("why"))
    brs = [b for b in row.get("breaches") or [] if isinstance(b, dict)]
    return [b for b in brs if b.get("key") not in done], {b["key"]: done[b["key"]] for b in brs if b.get("key") in done}


def debug_session(sid, item, why, path=None):
    """Append one record row for history session `sid` (prefix); 1 when the session is unknown or has no breach."""
    h = [r for r in read_history() if sid and str(r.get("session") or "").startswith(sid)]
    if len(h) != 1 or not h[0].get("breaches"):
        print("FAIL: session %s is %s" % (sid, "not in the history" if not h else "ambiguous" if len(h) > 1 else
                                          "without a breach"))
        return 1
    p = path or acks_path()
    d = load_acks(p)
    d["debugged"].append({"session": h[0]["session"], "keys": sorted(b["key"] for b in h[0]["breaches"]),
                          "item": item, "why": why, "at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())})
    with open(p + ".tmp", "w") as fh:
        json.dump(d, fh, indent=1, sort_keys=True)
        fh.write("\n")
    os.replace(p + ".tmp", p)
    print("debugged %s: %s (%s)" % (h[0]["session"][:8], ", ".join(d["debugged"][-1]["keys"]), p))
    return 0


# ------------------------------------------------------------------ history
def read_history(path=None):
    p = path or history_path()
    out = []
    try:
        with open(p) as fh:
            for ln in fh:
                try:
                    out.append(json.loads(ln))
                except ValueError:
                    continue
    except FileNotFoundError:
        pass
    return out


def record(directory=None, rules=None, path=None, dry_run=False, now=None):
    rules = rules or load_rules()
    directory = directory or os.environ.get("RM_GAME_HEALTH_TPS_DIR") or T.record_dir()
    p = path or history_path()
    if dry_run:
        return _record(directory, rules, p, True, now)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    import fcntl
    with open(p + ".lock", "a") as lk:          # two overlapping recorders must not both append a session
        fcntl.flock(lk, fcntl.LOCK_EX)
        return _record(directory, rules, p, False, now)


def _record(directory, rules, p, dry_run, now):
    known = {r.get("session") for r in read_history(p)}
    new, open_, skipped = [], [], 0
    order = sorted(sessions_on_disk(directory).items(), key=lambda kv: os.path.basename(kv[1][0]))
    for i, (sess, paths) in enumerate(order):
        if sess in known:
            continue
        h = first_row(paths[0])
        if not h or not isinstance(h.get("mods"), int) or h["mods"] < rules["full_list_min_mods"]:
            skipped += 1
            continue
        rows, bad = read_session(paths)
        if not rows:
            continue
        row = summarize(sess, rows, bad, rules, now, superseded=i < len(order) - 1)
        (new if row["finished"] else open_).append(row)
    if new and not dry_run:
        torn = False
        try:
            with open(p, "rb") as fh:
                fh.seek(0, 2)
                if fh.tell():
                    fh.seek(-1, 2)
                    torn = fh.read(1) != b"\n"
        except FileNotFoundError:
            pass
        with open(p, "a") as fh:
            if torn:
                fh.write("\n")                   # end an interrupted row so the next one is not glued to it
            for r in new:
                fh.write(json.dumps(r, sort_keys=True, allow_nan=False) + "\n")
    return {"dir": directory, "history": p, "dryRun": dry_run, "recorded": new,
            "open": open_, "notFullList": skipped, "known": len(known)}


def companion_dll():
    """The deployed JawaBench companion DLL ($RM_GAME_HEALTH_COMPANION_DLL overrides, selftests)."""
    env = os.environ.get("RM_GAME_HEALTH_COMPANION_DLL")
    if env:
        return env
    root = ("/mnt/c/Program Files (x86)/Steam/steamapps/common/RimWorld" if os.name != "nt"
            else r"C:\Program Files (x86)\Steam\steamapps\common\RimWorld")
    return os.path.join(root, "BridgeTools", "JawaBench", "JawaBench.BridgeTools.dll")


def companion_preflight(path=None):
    """None when the deployed companion serves the health fields (or the DLL cannot be read here: the session
    check then decides); else the reason the `fields` proof cannot ask. The probe is the UTF-16 string literal
    'privateMB' that JawaBenchSessionHealth.cs writes (the 2026-11-03 A1 FAIL ran on a DLL without it)."""
    path = path or companion_dll()
    try:
        with open(path, "rb") as f:
            blob = f.read()
    except OSError:
        return None
    if "privateMB".encode("utf-16-le") in blob:
        return None
    return ("deployed companion %s lacks JawaBenchSessionHealth (no 'privateMB' literal): it cannot serve the "
            "health fields; rebuild and deploy it (bridgetools/build.py --apply, game down)" % path)


def fmt(v):
    if isinstance(v, dict):
        return "UNMEASURED"
    return str(v)


def print_rows(rows):
    cols = ("mem.managed_peak_mb", "mem.managed_growth_mb_per_h", "mem.private_peak_mb", "mem.native_peak_mb",
            "tps.ratio_median", "tps.ratio_decay_pct", "tps.stall_max_s", "log.errors", "load.seconds")
    print("start                     mods  min   " + "  ".join(c.split(".", 1)[1] for c in cols) + "  breaches")
    for r in rows:
        m = r["metrics"]
        print("%-25s %4s %5s   %s  %s" % (r["start"], r.get("mods"), r.get("durationMin"),
                                          "  ".join(fmt(m.get(c)) for c in cols),
                                          ",".join(b["key"] for b in r["breaches"]) or "-"))


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    a = sub.add_parser("record")
    a.add_argument("--dry-run", action="store_true")
    a.add_argument("--json", action="store_true")
    a.add_argument("--dir")
    b = sub.add_parser("report")
    b.add_argument("--last", type=int, default=10)
    b.add_argument("--curve", action="store_true")
    c = sub.add_parser("latest")
    c.add_argument("--json", action="store_true")
    g = sub.add_parser("debugged")
    g.add_argument("--session", required=True)
    g.add_argument("--item", required=True)
    g.add_argument("--why", required=True)
    e = sub.add_parser("explain")
    e.add_argument("--session")
    e.add_argument("--dir")
    d = sub.add_parser("fields")
    d.add_argument("--session")
    d.add_argument("--dir")
    args = ap.parse_args(argv)
    if args.cmd == "record":
        res = record(directory=args.dir, dry_run=args.dry_run)
        if args.json:
            print(json.dumps(res, sort_keys=True))
        else:
            print("%s %d new full-list session(s), %d open, %d not full-list (history %s)" % (
                "would record" if args.dry_run else "recorded", len(res["recorded"]), len(res["open"]),
                res["notFullList"], res["history"]))
            print_rows(res["recorded"] + res["open"])
        return 0
    if args.cmd in ("report", "latest"):
        h = sorted(read_history(), key=lambda r: str(r.get("start")))   # a late-finalized session appends late
        if args.cmd == "latest":
            row = h[-1] if h else None
            if row is not None:
                try:
                    row["open_breaches"], row["debugged"] = split_breaches(row)
                except (OSError, ValueError) as e:   # an unreadable record debugs nothing: every breach still rings
                    row["open_breaches"], row["debugged"] = row.get("breaches") or [], {}
                    row["debuggedError"] = "%s: %s" % (type(e).__name__, str(e)[:200])
            print(json.dumps(row, sort_keys=True))
            return 0
        if not h:
            print("no full-list session recorded yet (%s)" % history_path())
            return 0
        print_rows(h[-args.last:])
        if args.curve:
            r = h[-1]
            print("\nnewest session %s, %s" % (r["session"][:8], r["curveAxis"]))
            for k, v in sorted(r["curves"].items()):
                print("  %-10s %s" % (k, " ".join("%s:%s" % (p[0], p[1]) for p in v)))
        return 0
    if args.cmd == "debugged":
        if not args.item.strip() or not args.why.strip() or len(args.session) < 8:
            print("FAIL: --item and --why must say something, --session at least 8 characters")
            return 2
        return debug_session(args.session, args.item.strip(), args.why.strip())
    if args.cmd == "explain":
        sess = sessions_on_disk(args.dir or os.environ.get("RM_GAME_HEALTH_TPS_DIR") or T.record_dir())
        h = sorted(read_history(), key=lambda r: str(r.get("start")))
        sid = args.session or (h[-1]["session"] if h else None)
        sid = next((s for s in sess if sid and s.startswith(sid)), None)
        if not sid:
            print("FAIL: session %s not on disk" % (args.session or "(newest recorded)"))
            return 1
        rows, bad = read_session(sess[sid])
        r = summarize(sid, rows, bad, load_rules(), superseded=True)
        print("session %s %s mods=%s breaches=%s" % (sid[:8], r["start"], r.get("mods"),
                                                    ",".join(b["key"] for b in r["breaches"]) or "-"))
        for k, v in sorted(r["attribution"].items()):
            print("  %s" % k)
            for x in v:
                print("    - %s" % x)
        still, done = split_breaches(r)
        print("  open: %s" % (",".join(b["key"] for b in still) or "-"))
        for k, v in sorted(done.items()):
            print("  debugged %s: %s" % (k, v))
        return 0
    if args.cmd == "fields":
        pre = companion_preflight()
        if pre:
            print("UNMEASURED: %s" % pre)
            return 2
        sess = sessions_on_disk(args.dir or T.record_dir())
        if not sess:
            print("FAIL: no TPS session on disk")
            return 1
        sid = args.session or max(sess, key=lambda s: os.path.basename(sess[s][0]))
        rows, _ = read_session(sess[sid])
        ctx = [r for r in rows if r.get("kind") == "context"]
        if not ctx:
            print("FAIL: session %s has no context row yet" % sid[:8])
            return 1
        last = ctx[-1]
        if not any(num(r.get(f)) is not None for r in ctx for f in LIVE_FIELDS):
            # no context row carries ANY health field: the companion that wrote this session predates
            # JawaBenchSessionHealth, so the proof cannot ask (HEALTHCHECK_COMPANION_VERIFY_STALE_DLL)
            print("UNMEASURED: session %s (context %s) was written by a companion that serves none of %s; "
                  "rebuild and deploy it (bridgetools/build.py --apply, game down) and play a new session"
                  % (sid[:8], last.get("utc"), list(LIVE_FIELDS)))
            return 2
        miss = [f for f in LIVE_FIELDS if num(last.get(f)) is None]
        zero = [f for f in ("privateMB", "unityReservedMB", "upS") if (num(last.get(f)) or 0) <= 0]
        print("session %s context %s: %s" % (sid[:8], last.get("utc"),
                                             " ".join("%s=%s" % (f, last.get(f)) for f in LIVE_FIELDS + ("gfxMB", "logEnabled"))))
        if miss or zero:
            print("FAIL: missing %s; zero %s" % (miss, zero))
            return 1
        print("PASS")
        return 0
    return 2


if __name__ == "__main__":
    sys.exit(main())
