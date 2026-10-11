"""`telemetry` — the agent interface to recorded history (design §7). Runs under Windows python.exe
(the stores are Windows-side; WSL cannot reach Windows localhost under NAT), launched by the
`telemetry` shell wrapper on WSL.

Rule for agents: QUERY HISTORY BEFORE RE-MEASURING LIVE. Every block is headed by source and
freshness; absent data prints UNMEASURED (<why>), never 0.

  telemetry health                        every source: newest row, lag, rows, errors; stores; processes
  telemetry series [--grep tps]           series that exist, with newest value and age
  telemetry query <MetricsQL> [--since 1h] [--step 15s]
  telemetry at "15:02" [--span 2m]        every game/host series + events around a moment
  telemetry events [--kind deploy,incident] [--since 24h] [--grep X]
  telemetry around deploy:<event id> [--metric rm_game_tick_ms]   ON DEMAND before/after, matched by speed
                                          (same-mod-list versions vs a fixed debug save is the recommended use)
  telemetry runs [--mod GSS] [--last 10]  proof runs;  telemetry run <id> [--diff <id>]
  telemetry flight [--last N]             flight-recorder dumps (spike tick, stage split)
  telemetry exc [--since 1h] [--top 20]   exception signatures, counts, first-sight text
  telemetry bridge [--since 1h]           calls by tool, latency p50/p99/max, failures
  telemetry disk                          volumes, VHDX slack, top dirs, days-until-full
  telemetry mark "<why>"                  write an annotation
  telemetry events --kind alert_fired     every alarm that fired; grade one: telemetry label <id> tp|fp "why"
  telemetry tier test|campaign [--ttl 60] arm/disarm the in-game test tier (needs the bridge hold)
  telemetry rebuild [--since 7d]          forget cursors -> re-ingest raw JSONL (stores are caches)
  telemetry up | down                     run the supervisor now / stop the Windows processes
"""
from __future__ import annotations

import argparse
import gzip
import json
import os
import re
import statistics
import subprocess
import sys
import time
from datetime import datetime, timedelta

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import analysis  # noqa: E402
import store  # noqa: E402
from tcommon import CODE_DIR, cfg, iso, read_json  # noqa: E402

GB = 1 << 30


def dur(s: str) -> float:
    m = re.fullmatch(r"(\d+(?:\.\d+)?)([smhd])", s.strip())
    if not m:
        raise SystemExit(f"bad duration {s!r} (use 90s, 15m, 2h, 7d)")
    return float(m.group(1)) * {"s": 1, "m": 60, "h": 3600, "d": 86400}[m.group(2)]


def age(ts) -> str:
    if ts is None:
        return "never"
    a = time.time() - ts
    return f"{a:.0f}s" if a < 120 else f"{a / 60:.0f}m" if a < 7200 else f"{a / 3600:.1f}h" if a < 172800 else f"{a / 86400:.1f}d"


def db():
    p = cfg()["db"]
    if not os.path.exists(p):
        raise SystemExit(f"UNMEASURED (no events DB at {p}: telemetryd has never run — `telemetry up`)")
    return store.connect(p, readonly=True)


def vm_ok() -> str | None:
    try:
        store.vm_get("/health", timeout=3)
        return None
    except Exception as e:  # noqa: BLE001
        return f"{type(e).__name__}: {e}"


def http_ok(url: str) -> bool:
    import urllib.request
    try:
        with urllib.request.urlopen(url, timeout=3) as r:
            return r.status < 500
    except Exception:  # noqa: BLE001
        return False


# ------------------------------------------------------------------ verbs

def cmd_health(a) -> int:
    st = cfg()["state"]
    hb = read_json(os.path.join(st, "heartbeat.json"))
    sv = read_json(os.path.join(st, "supervise.json"))
    al = read_json(os.path.join(st, "alerts.json"), {}) or {}
    print(f"telemetry @ {cfg()['root']}")
    print(f"  telemetryd   heartbeat {age(hb and hb.get('at'))} ago" + (
        f" · code {hb['code']} · VM sent {hb['vm_sent']} spooled {hb['vm_spooled']}"
        f" · test tier {'ARMED' if hb.get('tier_armed') else 'off'}" if hb else " · UNMEASURED (no heartbeat)"))
    if sv:
        print(f"  supervisor   ran {age(sv['at'])} ago: " + " · ".join(f"{k} {v}" for k, v in sv["status"].items()))
    else:
        print("  supervisor   UNMEASURED (never ran: is the scheduled task RimMandrake\\Telemetry installed?)")
    e = vm_ok()
    print(f"  VictoriaMetrics {cfg()['vm_url']}: {'up' if not e else 'DOWN (' + e + ')'}")
    print(f"  Grafana {cfg()['grafana_url']}: {'up' if http_ok(cfg()['grafana_url'] + '/api/health') else 'DOWN'}")
    print(f"  pulse alerts file written {age(al.get('at'))} ago; {len(al.get('alerts', []))} alert(s) open")
    for x in al.get("alerts", []):
        print(f"    [{x['level']}] {x['text']}")
    print("  sources (newest row age · rows this daemon run · bad · files)")
    for name, s in sorted((al.get("sources") or {}).items()):
        err = f" · ERROR {s['error']}" if s.get("error") else ""
        print(f"    {name:<9} {age(s.get('last_row_ts')):>6} · {s.get('rows')} · {s.get('bad')} · {s.get('files')}{err}")
    con = db()
    n = con.execute("SELECT COUNT(*) FROM events").fetchone()[0]
    last = con.execute("SELECT MAX(ts) FROM events").fetchone()[0]
    print(f"  events DB    {n} events, newest {age(last)} ago · "
          f"{con.execute('SELECT COUNT(*) FROM bridge_calls').fetchone()[0]} bridge calls · "
          f"{con.execute('SELECT COUNT(*) FROM proof_runs').fetchone()[0]} proof runs")
    return 0


def cmd_series(a) -> int:
    try:
        names = json.loads(store.vm_get("/api/v1/label/__name__/values"))["data"]
    except Exception as e:  # noqa: BLE001
        print(f"UNMEASURED (VictoriaMetrics unreachable: {e})")
        return 1
    names = [n for n in names if not a.grep or re.search(a.grep, n)]
    print(f"VictoriaMetrics · {len(names)} series names" + (f" matching {a.grep!r}" if a.grep else ""))
    for n in names:
        try:
            r = store.vm_query(f"last_over_time({n}[30d])")["data"]["result"]
        except Exception:  # noqa: BLE001
            r = []
        if not r:
            print(f"  {n:<34} UNMEASURED (no point in 30 d)")
            continue
        newest = max(float(x["value"][0]) for x in r)
        v = r[0]["value"][1]
        print(f"  {n:<34} {len(r):>3} label sets · newest {age(newest):>5} ago · e.g. {v} {_labels(r[0]['metric'])}")
    return 0


def _labels(m: dict) -> str:
    return "{" + ",".join(f"{k}={v}" for k, v in m.items() if k != "__name__") + "}"


def cmd_query(a) -> int:
    end = time.time()
    try:
        d = store.vm_query(a.expr, end - dur(a.since), end, a.step)
    except Exception as e:  # noqa: BLE001
        print(f"UNMEASURED (VictoriaMetrics: {e})")
        return 1
    res = d["data"]["result"]
    print(f"VictoriaMetrics · {a.expr} · last {a.since} step {a.step} · {len(res)} series")
    if not res:
        print("  UNMEASURED (no points in range; check the name with `telemetry series --grep`)")
    for s in res[:a.limit]:
        vals = [float(v[1]) for v in s["values"]]
        print(f"  {_labels(s['metric'])}  n={len(vals)} min={min(vals):.4g} med={statistics.median(vals):.4g} "
              f"max={max(vals):.4g} last={vals[-1]:.4g} @ {iso(float(s['values'][-1][0]))[11:]}")
        if a.points:
            for t, v in s["values"][-a.points:]:
                print(f"     {iso(float(t))}  {v}")
    return 0


def parse_moment(s: str) -> float:
    s = s.strip()
    for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M", "%Y-%m-%dT%H:%M:%S"):
        try:
            return datetime.strptime(s, fmt).timestamp()
        except ValueError:
            pass
    for fmt in ("%H:%M:%S", "%H:%M"):
        try:
            t = datetime.strptime(s, fmt)
            d = datetime.now().replace(hour=t.hour, minute=t.minute, second=t.second, microsecond=0)
            if d > datetime.now():
                d -= timedelta(days=1)
            return d.timestamp()
        except ValueError:
            pass
    raise SystemExit(f"cannot read moment {s!r} (HH:MM, HH:MM:SS or YYYY-MM-DD HH:MM)")


AT_SERIES = ["rm_game_tps", "rm_game_ratio", "rm_game_tick_ms", "rm_game_worst_tick_ms", "rm_game_heap_mb",
             "rm_game_exc", "rm_game_gap_max_ms", "rm_game_bridge_main_ms", "rm_host_mem_avail_bytes",
             "rm_proc_cpu_cores"]


def cmd_at(a) -> int:
    t = parse_moment(a.moment)
    span = dur(a.span)
    print(f"around {iso(t)} ± {a.span}")
    err = vm_ok()
    for n in AT_SERIES:
        if err:
            print(f"  {n:<26} UNMEASURED (VictoriaMetrics down)")
            continue
        try:
            r = store.vm_query(n, t - span, t + span, "1s" if span <= 300 else "15s")["data"]["result"]
        except Exception as e:  # noqa: BLE001
            print(f"  {n:<26} UNMEASURED ({e})")
            continue
        if not r:
            print(f"  {n:<26} UNMEASURED (no points in window)")
            continue
        for s in r[:3]:
            vals = [float(v[1]) for v in s["values"]]
            print(f"  {n:<26} {_labels(s['metric'])} n={len(vals)} min={min(vals):.4g} max={max(vals):.4g} "
                  f"med={statistics.median(vals):.4g}")
    con = db()
    rows = con.execute("SELECT ts,kind,subject FROM events WHERE ts BETWEEN ? AND ? AND kind NOT IN "
                       "('art_job','art_queued','art_registered','art_validated','ledger') ORDER BY ts",
                       (t - span, t + span)).fetchall()
    print(f"  events ({len(rows)}):")
    for r in rows[:60]:
        print(f"    {iso(r['ts'])[11:]}  {r['kind']:<14} {str(r['subject'] or '')[:90]}")
    calls = con.execute("SELECT COUNT(*), AVG(ms), MAX(ms) FROM bridge_calls WHERE ts BETWEEN ? AND ?",
                        (t - span, t + span)).fetchone()
    print(f"  bridge calls: {calls[0]}" + (f", mean {calls[1]:.0f} ms, max {calls[2]:.0f} ms" if calls[0] else ""))
    return 0


def cmd_events(a) -> int:
    con = db()
    q = "SELECT id,ts,ts_end,kind,subject,seat,sha,detail FROM events WHERE ts>?"
    args: list = [time.time() - dur(a.since)]
    if a.kind:
        ks = a.kind.split(",")
        q += " AND kind IN (%s)" % ",".join("?" * len(ks))
        args += ks
    if a.grep:
        q += " AND (subject LIKE ? OR detail LIKE ?)"
        args += [f"%{a.grep}%"] * 2
    rows = con.execute(q + " ORDER BY ts DESC LIMIT ?", (*args, a.limit)).fetchall()
    print(f"events DB · last {a.since}" + (f" · kind {a.kind}" if a.kind else "") + f" · {len(rows)} shown")
    for r in reversed(rows):
        det = (r["detail"] or "")[:a.width]
        print(f"  #{r['id']:<7} {iso(r['ts'])}  {r['kind']:<14} {str(r['subject'] or '')[:60]:<60} "
              f"{r['sha'] or ''} {det if a.detail else ''}")
    return 0


def cmd_around(a) -> int:
    con = db()
    m = re.fullmatch(r"deploy:(\d+)", a.what)
    if not m:
        raise SystemExit("use deploy:<event id> (find ids with `telemetry events --kind deploy`)")
    d = con.execute("SELECT * FROM events WHERE id=?", (int(m.group(1)),)).fetchone()
    if not d:
        raise SystemExit("no such event")
    print(f"deploy #{d['id']} at {iso(d['ts'])}: {d['subject']}  (passive comparison; no cause is established)")
    if vm_ok():
        print("  UNMEASURED (VictoriaMetrics down)")
        return 1
    for mult in (1, 3, 6, 12):
        before = analysis.windows_from_vm(a.metric, d["ts"] - dur(a.span), d["ts"] - 60, mult)
        after = analysis.windows_from_vm(a.metric, d["ts"] + 120, d["ts"] + dur(a.span), mult)
        c = analysis.compare_windows(before, after)
        if c["verdict"] == "UNMEASURED":
            print(f"  x{mult:<3} UNMEASURED ({c['n_before']} windows before, {c['n_after']} after; "
                  f"need 30 each)")
        else:
            print(f"  x{mult:<3} {c['verdict']:<10} median {c['median_before']:.2f} -> {c['median_after']:.2f} "
                  f"({c['rel'] * 100:+.0f}%, threshold {c['threshold']:.2f}; n {c['n_before']}/{c['n_after']})")
    return 0


def cmd_runs(a) -> int:
    con = db()
    q = "SELECT * FROM proof_runs"
    args = []
    if a.mod:
        q += " WHERE mod LIKE ?"
        args.append(f"%{a.mod}%")
    rows = con.execute(q + " ORDER BY ts DESC LIMIT ?", (*args, a.last)).fetchall()
    print(f"proof runs (committed results in the mirror) · {len(rows)} shown")
    for r in rows:
        print(f"  {iso(r['ts'])}  {r['mod'] or '?':<16} pass {r['n_pass']:>3} fail {r['n_fail']:>3} "
              f"other {r['n_other']:>3}  {r['wall_s'] or '':>6}  {r['id']}")
    return 0


def cmd_run(a) -> int:
    con = db()
    rows = {r["row_id"]: r for r in con.execute("SELECT * FROM proof_rows WHERE run_id LIKE ?", (f"%{a.id}%",))}
    if not rows:
        print("UNMEASURED (no proof run matches)")
        return 1
    if a.diff:
        other = {r["row_id"]: r for r in con.execute("SELECT * FROM proof_rows WHERE run_id LIKE ?", (f"%{a.diff}%",))}
        for rid in sorted(set(rows) | set(other)):
            s1 = rows.get(rid, {"status": "-"})["status"]
            s2 = other.get(rid, {"status": "-"})["status"]
            if s1 != s2:
                print(f"  {rid:<60} {s1} -> {s2}")
        return 0
    for rid, r in rows.items():
        print(f"  {r['status']:<11} {rid:<60} {str(r['detail'])[:100]}")
    return 0


def cmd_flight(a) -> int:
    con = db()
    rows = con.execute("SELECT * FROM flight ORDER BY ts DESC LIMIT ?", (a.last,)).fetchall()
    if not rows:
        print("UNMEASURED (no flight dumps recorded: the in-game test tier was never armed, or nothing triggered)")
        return 0
    for r in rows:
        print(f"  {iso(r['ts'])}  trigger {r['trigger']:<10} ticks {r['tick_from']}..{r['tick_to']} "
              f"worst {(r['worst_us'] or 0) / 1000:.1f} ms  {r['file']}")
    if a.show:
        r = rows[0]
        p = os.path.join(cfg()["raw"], "flight", os.path.basename(r["file"] or ""))
        if not os.path.exists(p):
            p = os.path.join(cfg()["jawabench"], "tps", "flight", os.path.basename(r["file"] or ""))
        try:
            with gzip.open(p, "rt", encoding="utf-8") as f:
                lines = f.read().splitlines()
            print(f"  {p}: header {lines[0][:300]}")
            print(f"  {len(lines) - 1} tick lines; slowest 10:")
            ticks = [json.loads(x) for x in lines[1:]]
            key = (lambda t: t.get("durUs", 0)) if ticks and isinstance(ticks[0], dict) else (lambda t: t[1])
            for t in sorted(ticks, key=key, reverse=True)[:10]:
                print(f"     {json.dumps(t)[:200]}")
        except (OSError, ValueError, IndexError) as e:
            print(f"  cannot read dump ({e})")
    return 0


def cmd_exc(a) -> int:
    con = db()
    since = time.time() - dur(a.since)
    rows = con.execute("SELECT * FROM exc_sigs WHERE last_ts>? ORDER BY n DESC LIMIT ?", (since, a.top)).fetchall()
    sup = None
    if not vm_ok():
        try:
            r = store.vm_query(f"sum(sum_over_time(rm_game_exc_suppressed[{a.since}]))")["data"]["result"]
            sup = r[0]["value"][1] if r else None
        except Exception:  # noqa: BLE001
            pass
    print(f"exception signatures · last {a.since} · suppressed by the log cap: "
          f"{sup if sup is not None else 'UNMEASURED'}  (direct Debug.LogError after the cap stays invisible)")
    if not rows:
        print("  UNMEASURED (no signatures: test tier not armed, or the counter is off)")
    for r in rows:
        print(f"  {r['n']:>6}  {r['sig'][:120]}")
        if a.text and r["sample"]:
            print(f"          {r['sample'][:400]}")
    return 0


def cmd_bridge(a) -> int:
    con = db()
    since = time.time() - dur(a.since)
    rows = con.execute("SELECT tool, ms, success FROM bridge_calls WHERE ts>? AND ms IS NOT NULL", (since,)).fetchall()
    newest = con.execute("SELECT MAX(ts) FROM bridge_calls").fetchone()[0]
    print(f"bridge calls · last {a.since} · {len(rows)} completed · newest call {age(newest)} ago")
    if not rows:
        print("  UNMEASURED (no calls in window)")
        return 0
    by: dict = {}
    for r in rows:
        by.setdefault(r["tool"], []).append((r["ms"], r["success"]))
    allms = sorted(x[0] for v in by.values() for x in v)

    def pct(xs, p):
        return xs[min(len(xs) - 1, int(p * len(xs)))]
    print(f"  all: p50 {pct(allms, .5):.0f} ms · p99 {pct(allms, .99):.0f} ms · max {allms[-1]:.0f} ms · "
          f"{len(allms) / (dur(a.since) / 60):.1f}/min")
    for tool, v in sorted(by.items(), key=lambda kv: -sum(x[0] for x in kv[1]))[:a.top]:
        ms = sorted(x[0] for x in v)
        fails = sum(1 for x in v if not x[1])
        print(f"  {tool:<40} {len(v):>6} calls  p50 {pct(ms, .5):>6.0f}  p99 {pct(ms, .99):>7.0f}  "
              f"max {ms[-1]:>7.0f} ms  {fails} failed")
    return 0


def cmd_disk(a) -> int:
    import host
    print("volumes (measured now)")
    for letter, v in host.volumes().items():
        if not v:
            print(f"  {letter}:  UNMEASURED (not present)")
            continue
        slope = ""
        if not vm_ok():
            try:
                sel = f'rm_disk_free_bytes{{vol="{letter}"}}'
                first = store.vm_query(f"tfirst_over_time({sel}[24h])")["data"]["result"]
                span = time.time() - float(first[0]["value"][1]) if first else 0
                r = store.vm_query(f"deriv({sel}[24h])")["data"]["result"] if span >= 6 * 3600 else []
                d = float(r[0]["value"][1]) if r else None
                if span < 6 * 3600:
                    slope = f" · trend UNMEASURED ({span / 3600:.1f} h of samples, need 6)"
                elif d is not None and d < 0:
                    slope = f" · falling {-d * 86400 / GB:.1f} GB/day → full in {v['free'] / (-d * 86400):.0f} d"
                elif d is not None:
                    slope = " · not falling (24 h)"
            except Exception:  # noqa: BLE001
                pass
        print(f"  {letter}:  {v['free'] / GB:8.0f} GB free of {v['total'] / GB:6.0f} GB ({cfg()['volumes'][letter]}){slope}")
    vx = host.vhdx()
    if vx:
        print(f"  WSL VHDX {cfg()['vhdx']}: {vx['size'] / GB:.0f} GB logical, "
              f"{(vx['alloc'] or 0) / GB:.0f} GB allocated on disk")
    dirs = None
    try:
        for s in store.vm_query("last_over_time(rm_dir_bytes[2h])")["data"]["result"]:
            dirs = dirs or []
            dirs.append((s["metric"].get("dir"), float(s["value"][1])))
    except Exception:  # noqa: BLE001
        pass
    if dirs:
        print("  directories (hourly):")
        for n, b in sorted(dirs, key=lambda x: -x[1]):
            print(f"    {n:<12} {b / GB:8.1f} GB")
    else:
        print("  directories: UNMEASURED (no hourly sample yet)")
    return 0


def cmd_mark(a) -> int:
    from telemetry_emit import emit_change
    ok = emit_change("marker", a.why, detail={"why": a.why, "by": "telemetry mark"})
    print("marked" if ok else "NOT marked (telemetry root absent)")
    return 0 if ok else 1


def cmd_tier(a) -> int:
    """Arms the in-game tier through the bridge. Refuses without the bridge hold (CLAUDE.md: one driver)."""
    utils = os.path.dirname(CODE_DIR)
    sys.path.insert(0, utils)
    try:
        import rimbridge_client  # type: ignore
    except ImportError as e:
        print(f"cannot import rimbridge_client: {e}")
        return 1
    args = {"tier": a.tier, "ttl_min": a.ttl}
    try:
        h, port, tok = rimbridge_client.resolve_endpoint()
        with rimbridge_client.RimBridge(h, port, tok, client_name="telemetry tier") as c:
            r = c.call("jawa/telemetry_tier", args)
    except Exception as e:  # noqa: BLE001
        print(f"NOT armed: {type(e).__name__}: {e}  (is the game up with the P2 companion deployed?)")
        return 1
    print(json.dumps(r)[:600])
    from telemetry_emit import emit_change
    emit_change("marker", f"tier:{a.tier}", detail=args)
    return 0


def cmd_label(a) -> int:
    """Grade an `alert_fired` event so thresholds can be retuned (owner 2026-10-11)."""
    from telemetry_emit import emit_change
    ok = emit_change("alert_label", str(a.event), detail={"event": a.event, "label": a.label, "why": a.why})
    print(f"labelled #{a.event} {a.label}" if ok else "NOT labelled (telemetry root absent)")
    return 0 if ok else 1


def cmd_rebuild(a) -> int:
    con = store.connect()
    since = time.time() - dur(a.since)
    n = con.execute("DELETE FROM cursors WHERE mtime>=? OR src IN ('proof')", (since,)).rowcount
    con.commit()
    print(f"forgot {n} cursors newer than {a.since}; telemetryd re-reads those files on its next pass "
          "(inserts are idempotent on src_ref; VM points for the same timestamps overwrite in queries)")
    return 0


def cmd_up(a) -> int:
    import supervise
    return supervise.main(["--print", "--force"])


def cmd_down(a) -> int:
    import supervise
    return supervise.main(["stop"])


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="telemetry", description=__doc__.split("\n")[0])
    sp = ap.add_subparsers(dest="cmd", required=True)
    sp.add_parser("health").set_defaults(f=cmd_health)
    p = sp.add_parser("series"); p.add_argument("--grep"); p.set_defaults(f=cmd_series)  # noqa: E702
    p = sp.add_parser("query"); p.add_argument("expr"); p.add_argument("--since", default="1h")  # noqa: E702
    p.add_argument("--step", default="15s"); p.add_argument("--limit", type=int, default=20)  # noqa: E702
    p.add_argument("--points", type=int, default=0); p.set_defaults(f=cmd_query)  # noqa: E702
    p = sp.add_parser("at"); p.add_argument("moment"); p.add_argument("--span", default="2m")  # noqa: E702
    p.set_defaults(f=cmd_at)
    p = sp.add_parser("events"); p.add_argument("--kind"); p.add_argument("--since", default="24h")  # noqa: E702
    p.add_argument("--grep"); p.add_argument("--limit", type=int, default=60)  # noqa: E702
    p.add_argument("--detail", action="store_true"); p.add_argument("--width", type=int, default=160)  # noqa: E702
    p.set_defaults(f=cmd_events)
    p = sp.add_parser("around"); p.add_argument("what"); p.add_argument("--metric", default="rm_game_tick_ms")  # noqa: E702
    p.add_argument("--span", default="24h"); p.set_defaults(f=cmd_around)  # noqa: E702
    p = sp.add_parser("runs"); p.add_argument("--mod"); p.add_argument("--last", type=int, default=15)  # noqa: E702
    p.set_defaults(f=cmd_runs)
    p = sp.add_parser("run"); p.add_argument("id"); p.add_argument("--diff"); p.set_defaults(f=cmd_run)  # noqa: E702
    p = sp.add_parser("flight"); p.add_argument("--last", type=int, default=10)  # noqa: E702
    p.add_argument("--show", action="store_true"); p.set_defaults(f=cmd_flight)  # noqa: E702
    p = sp.add_parser("exc"); p.add_argument("--since", default="1h"); p.add_argument("--top", type=int, default=20)  # noqa: E702
    p.add_argument("--text", action="store_true"); p.set_defaults(f=cmd_exc)  # noqa: E702
    p = sp.add_parser("bridge"); p.add_argument("--since", default="1h"); p.add_argument("--top", type=int, default=15)  # noqa: E702
    p.set_defaults(f=cmd_bridge)
    sp.add_parser("disk").set_defaults(f=cmd_disk)
    p = sp.add_parser("mark"); p.add_argument("why"); p.set_defaults(f=cmd_mark)  # noqa: E702
    p = sp.add_parser("tier"); p.add_argument("tier", choices=["test", "campaign"])  # noqa: E702
    p.add_argument("--ttl", type=int, default=60); p.set_defaults(f=cmd_tier)  # noqa: E702
    p = sp.add_parser("label"); p.add_argument("event", type=int); p.add_argument("label", choices=["tp", "fp"])  # noqa: E702
    p.add_argument("why", nargs="?", default=""); p.set_defaults(f=cmd_label)  # noqa: E702
    p = sp.add_parser("rebuild"); p.add_argument("--since", default="7d"); p.set_defaults(f=cmd_rebuild)  # noqa: E702
    sp.add_parser("up").set_defaults(f=cmd_up)
    sp.add_parser("down").set_defaults(f=cmd_down)
    a = ap.parse_args(argv)
    return a.f(a)


if __name__ == "__main__":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except AttributeError:
        pass
    sys.exit(main())
