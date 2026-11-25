#!/usr/bin/env python3
"""Count bridge order calls that waited on a paused game clock (item RIMMANDRAKE_STOP_FLOWWORKS_ORDERS_WAITING_OUT_A_PAUSED_CLOCK).

An order call (jawa/ordered_job, jawa/order_pawn) with waitTicks > 0 waits for GAME ticks. On a paused game no tick
comes, and the call sits until its time limit (15 s ordered_job, 30 s order_pawn). This reader joins each order call of
the named scripts in the bridge log (raw/bridge*/<utc day>.jsonl.gz) to the 5 s tick windows of the game that served it
(raw/tps*/ and the game's own tps_*.jsonl segments), and counts the calls over --min-s whose windows show 0 ticks.
Method: design/specs/2026-11-23-costly-test-acts/analysis.md section 1.

    python3 clock_still_waits.py --day 2026-11-23 [--game ArchSmall] [--limit 0]
    python3 clock_still_waits.py --since 2026-11-25T03:00 [--until ...]        local Pacific times
    python3 clock_still_waits.py --selftest

Exit: 0 paused waits <= --limit (measured); 1 over the limit; 2 could not look (no bridge record for a day of the window,
an unreadable record, or a long order call with no tick window of its game); 3 empty set (no order call of these scripts
in the window: no visit to read).
"""
from __future__ import annotations

import argparse
import glob
import gzip
import json
import os
import re
import sys
import tempfile
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

LOCAL = ZoneInfo("America/Los_Angeles")
TOOLS = ("jawa/ordered_job", "jawa/order_pawn")
SCRIPTS = ("concept_scenes.py", "extension_proof.py", "live_session.py")     # the FlowWorks callers the item names
SEG_T = re.compile(r"tps_(\d{8}T\d{6})Z_")
EX_OK, EX_OVER, EX_COULD_NOT_LOOK, EX_EMPTY = 0, 1, 2, 3


def ts(v):
    import tcommon
    return tcommon.parse_ts(v)


def local_time(text: str) -> float:
    dt = datetime.fromisoformat(text)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=LOCAL)
    return dt.timestamp()


def utc_days(t0: float, t1: float) -> list[str]:
    d = datetime.fromtimestamp(t0, timezone.utc).date()
    out = []
    while d <= datetime.fromtimestamp(t1, timezone.utc).date():
        out.append(d.isoformat())
        d += timedelta(days=1)
    return out


def jsonl(path: str):
    """Rows of a .jsonl or .jsonl.gz file. A torn line is skipped and counted; an unreadable file raises OSError."""
    op = gzip.open if path.endswith(".gz") else open
    rows, torn = [], 0
    with op(path, "rt", encoding="utf-8", errors="replace") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                rows.append(json.loads(line))
            except ValueError:
                torn += 1
    return rows, torn


def machine_of(dirname: str, home: str) -> str:
    _, _, rest = dirname.partition(".")
    return rest.split(".")[0] if rest else home


def order_calls(raw: str, days: list[str], t0: float, t1: float, scripts, home: str, game_of):
    """-> (calls, missing_days). A call: dict(tool, script, start, s, game). Missing days: no bridge file of that day."""
    starts, ends, seen_day = {}, {}, set()
    for d in sorted(glob.glob(os.path.join(raw, "bridge*"))):
        mach = machine_of(os.path.basename(d), home)
        for day in days:
            p = os.path.join(d, day + ".jsonl.gz")
            if not os.path.exists(p):
                continue
            seen_day.add(day)
            rows, _ = jsonl(p)
            for r in rows:
                if r.get("ev") == "start" and r.get("tool") in TOOLS and r.get("script") in scripts:
                    starts[r.get("cid")] = (r, mach)
                elif r.get("ev") == "end":
                    ends[r.get("cid")] = r
    calls = []
    for cid, (r, mach) in starts.items():
        t = ts(r.get("t"))
        e = ends.get(cid)
        if t is None or not (t0 <= t < t1) or e is None or not isinstance(e.get("ms"), (int, float)):
            continue
        calls.append({"tool": r["tool"], "script": r["script"], "start": t, "s": e["ms"] / 1000.0,
                      "game": game_of(mach, r.get("endpoint"))})
    return calls, [d for d in days if d not in seen_day]


def tick_windows(raw: str, key: str, home: str, days: list[str], t0: float, record_dir) -> list[tuple[float, float, int]]:
    """The game's 5 s sample windows (start, end, ticks), from the store's copy and the game's own segments, deduped."""
    rows = []
    d = os.path.join(raw, "tps" if key == home else "tps." + key)
    for day in days:
        p = os.path.join(d, day + ".jsonl.gz")
        if os.path.exists(p):
            rows += jsonl(p)[0]
    rd = record_dir(key) if record_dir else None
    if rd and os.path.isdir(os.path.join(rd, "tps")):
        lo = datetime.fromtimestamp(t0 - 2 * 86400, timezone.utc).strftime("%Y%m%dT%H%M%S")
        for p in glob.glob(os.path.join(rd, "tps", "tps_*.jsonl")):
            m = SEG_T.search(os.path.basename(p))
            if m and m.group(1) >= lo:
                rows += jsonl(p)[0]
    out, seen = [], set()
    for r in rows:
        if r.get("kind") != "sample" or not isinstance(r.get("dTicks"), (int, float)):
            continue
        k = (r.get("session"), r.get("seq"))
        if k in seen:
            continue
        seen.add(k)
        end, dr = ts(r.get("utc")), r.get("dReal")
        if end is None or not isinstance(dr, (int, float)) or dr <= 0:
            continue
        out.append((end - dr, end, int(r["dTicks"])))
    out.sort()
    return out


def ticks_during(start: float, end: float, wins) -> int | None:
    """Ticks in the windows that lie mostly inside [start, end] (the one that overlaps most, when none does). None: no
    window of the game overlaps the call (could not look)."""
    over = [(min(end, b) - max(start, a), b - a, n) for a, b, n in wins if b > start and a < end]
    if not over:
        return None
    inside = [n for o, w, n in over if o >= 0.5 * w]
    return sum(inside) if inside else max(over)[2]


def judge(raw, t0, t1, scripts, min_s, limit, games_filter, home, game_of, record_dir, out=print, today=None) -> int:
    days = utc_days(t0, t1)
    today = today or datetime.now(timezone.utc).date().isoformat()
    try:
        calls, missing = order_calls(raw, days, t0, t1, scripts, home, game_of)
    except OSError as e:
        out("could not look: a bridge record cannot be read: %s" % e)
        return EX_COULD_NOT_LOOK
    missing = [d for d in missing if d != today]       # today's file may not be exported yet: its calls are not read
    if missing:
        out("could not look: no bridge record for day(s) %s under %s" % (", ".join(missing), raw))
        return EX_COULD_NOT_LOOK
    if games_filter:
        calls = [c for c in calls if c["game"] in games_filter]
    if not calls:
        out("empty set: no order call by %s in the window (no visit to read); paused-clock waits 0" % ", ".join(scripts))
        return EX_EMPTY
    long_calls = [c for c in calls if c["s"] >= min_s]
    wins, paused, unknown = {}, [], []
    for c in long_calls:
        g = c["game"]
        if g not in wins:
            try:
                import games
                key = games.resolve(g)[1] if g else None
            except Exception:
                key = None
            try:
                wins[g] = tick_windows(raw, key, home, days, t0, record_dir) if key else []
            except OSError as e:
                out("could not look: a tick record of %s cannot be read: %s" % (g, e))
                return EX_COULD_NOT_LOOK
        n = ticks_during(c["start"], c["start"] + c["s"], wins[g])
        if n is None:
            unknown.append(c)
        elif n == 0:
            paused.append(c)
    secs = sum(c["s"] for c in paused)
    by = {}
    for c in paused:
        by[(c["script"], c["tool"])] = by.get((c["script"], c["tool"]), 0) + 1
    detail = "; ".join("%s %s %d" % (s, t.split("/")[1], n) for (s, t), n in sorted(by.items()))
    out("paused-clock order waits: %d calls, %.0f s (order calls read %d, over %g s %d, no tick window %d; limit %d)%s"
        % (len(paused), secs, len(calls), min_s, len(long_calls), len(unknown), limit, (" | " + detail) if detail else ""))
    if len(paused) > limit:
        return EX_OVER
    if unknown:
        out("could not look: %d long order call(s) have no tick window of their game, so the count may be low" % len(unknown))
        return EX_COULD_NOT_LOOK
    return EX_OK


def selftest() -> int:
    d = tempfile.mkdtemp(prefix="csw_")
    raw = os.path.join(d, "raw")
    os.makedirs(os.path.join(raw, "bridge"))
    os.makedirs(os.path.join(raw, "tps.archmagi.b"))
    t0 = datetime(2026, 11, 23, 22, 0, tzinfo=timezone.utc).timestamp()

    def iso(t):
        return datetime.fromtimestamp(t, timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"

    def write(path, rows):
        with gzip.open(path, "wt") as f:
            for r in rows:
                f.write((r if isinstance(r, str) else json.dumps(r)) + "\n")

    def call(cid, at, ms, tool="jawa/ordered_job", script="concept_scenes.py", port=5175):
        return [{"ev": "start", "cid": cid, "t": iso(t0 + at), "tool": tool, "script": script,
                 "endpoint": "127.0.0.1:%d" % port}, {"ev": "end", "cid": cid, "ms": ms}]

    def tps(ticking):          # 5 s windows over 0..600 s; ticking(i) -> ticks of window i
        return [{"kind": "sample", "session": "s1", "seq": i, "utc": iso(t0 + 5 * (i + 1)), "dReal": 5.0,
                 "dTicks": ticking(i)} for i in range(120)]

    import games
    home, game_of = "archmagi", games.game_of_endpoint
    ok = True

    def case(name, bridge, windows, want, **kw):
        nonlocal ok
        for p in glob.glob(os.path.join(raw, "*", "*")):
            os.remove(p)
        if bridge is not None:
            write(os.path.join(raw, "bridge", "2026-11-23.jsonl.gz"), bridge)
        if windows is not None:
            write(os.path.join(raw, "tps.archmagi.b", "2026-11-23.jsonl.gz"), windows)
        lines = []
        got = judge(raw, t0, t0 + kw.get("span", 3600), SCRIPTS, 3.0, 0, kw.get("games"), home, game_of, None, lines.append,
                    today=kw.get("today", "2026-11-30"))
        good = got == want
        ok &= good
        print("  case %-22s want %d got %d %s  | %s" % (name, want, got, "ok" if good else "WRONG", lines[-1][:110]))

    paused_all = tps(lambda i: 0)
    running = tps(lambda i: 300)
    case("planted_paused_wait", call("a", 100, 15000) + call("b", 200, 40), paused_all, EX_OVER)
    case("running_clock_wait", call("a", 100, 15000), running, EX_OK)
    case("short_calls_only", call("a", 100, 40) + call("b", 300, 900), paused_all, EX_OK)
    case("other_script_ignored", call("a", 100, 15000, script="gravship_scene.py"), paused_all, EX_EMPTY)
    case("empty_day", [], paused_all, EX_EMPTY)
    case("no_bridge_record", None, paused_all, EX_COULD_NOT_LOOK)
    case("no_tick_window", call("a", 100, 15000), [], EX_COULD_NOT_LOOK)
    case("torn_lines_survive", call("a", 100, 15000) + ["{torn"], paused_all, EX_OVER)
    case("edge_window_ticks", call("a", 102, 15000), tps(lambda i: 600 if i in (19, 23) else 0), EX_OVER)
    case("ticks_mid_call", call("a", 102, 15000), tps(lambda i: 600 if i == 21 else 0), EX_OK)
    case("today_not_exported", call("a", 100, 15000), paused_all, EX_OVER, today="2026-11-24", span=3 * 3600)
    case("past_day_missing", call("a", 100, 15000), paused_all, EX_COULD_NOT_LOOK, span=3 * 3600)
    case("other_game_filtered", call("a", 100, 15000, port=5174), paused_all, EX_EMPTY, games=["ArchSmall"])
    import shutil
    shutil.rmtree(d, ignore_errors=True)
    print("SELFTEST OK" if ok else "SELFTEST BROKEN")
    return 0 if ok else 1


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--day", help="a local (Pacific) day, YYYY-MM-DD")
    ap.add_argument("--since", help="local time: read from here (ISO); with no --until, to now")
    ap.add_argument("--until", help="local time: read to here (ISO)")
    ap.add_argument("--game", action="append", help="only calls served by this game (ArchBig, ArchSmall, ...)")
    ap.add_argument("--scripts", default=",".join(SCRIPTS), help="the calling scripts (default: the FlowWorks callers)")
    ap.add_argument("--min-s", type=float, default=3.0, help="a call shorter than this is not a wait (the study's line)")
    ap.add_argument("--limit", type=int, default=0, help="paused-clock waits allowed (default 0, our own rule)")
    ap.add_argument("--raw", help="the telemetry raw folder (default: the store's)")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args(argv)
    if a.selftest:
        return selftest()
    if bool(a.day) == bool(a.since):
        ap.error("give --day or --since")
    if a.day:
        t0 = local_time(a.day + "T00:00")
        t1 = local_time((datetime.fromisoformat(a.day) + timedelta(days=1)).date().isoformat() + "T00:00")
    else:
        t0 = local_time(a.since)
        t1 = local_time(a.until) if a.until else datetime.now(timezone.utc).timestamp()
    import games
    import tcommon
    raw = a.raw or tcommon.cfg()["raw"]
    if not os.path.isdir(raw):
        print("could not look: no telemetry raw folder at %s" % raw)
        return EX_COULD_NOT_LOOK
    gf = [games.resolve(g)[0] for g in a.game] if a.game else None
    return judge(raw, t0, t1, tuple(s for s in a.scripts.split(",") if s), a.min_s, a.limit, gf, games.home_key(),
                 games.game_of_endpoint, games.record_dir)


if __name__ == "__main__":
    sys.exit(main())
