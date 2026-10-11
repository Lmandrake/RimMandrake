#!/usr/bin/env python3
"""Selftest for the telemetry stack (TELEMETRY_BUILD_EVERY_TICK_ACCOUNTED). Offline and deterministic:
every check drives the real code against fixture streams in a temp dir, with a fake VictoriaMetrics.

  python3 src/RimMandrake/Utils/telemetry/selftest_telemetry.py          offline (run_selftests runs this)
  python3 src/RimMandrake/Utils/telemetry/selftest_telemetry.py --live   + the real stack on this machine:
        heartbeat fresh, VM and Grafana answering (via python.exe), alerts file current, no visible windows

Lessons written into this script (debug_process.md: a check for each, plus the false theories):
  * JawaBench `incident`/`awareness` rows repeat the `kind` key; json.loads keeps the LAST one and
    mis-files the row (an incident read as kind "stall"). The ingest keeps the first.            [kind]
  * bridge_calls rotates by rename (.jsonl -> .1). Cursors keyed by path re-read the renamed file;
    keyed by inode they follow it.                                                              [rotate]
  * A paused window has tps 0 and tickMs 0: those are "did not tick", not zero speed. Not emitted. [paused]
  * FALSE THEORY: "Grafana windows come from the browser". They came from DETACHED_PROCESS: a detached
    parent has no console, so each gpx_* plugin child opened its own visible console. --live checks
    that no telemetry process owns a window.                                                    [windows]
  * The Store python launcher's pid is not the interpreter's pid; supervise judges telemetryd by its
    own heartbeat, or it restarts it every minute.                                              [heartbeat]
"""
from __future__ import annotations

import gzip
import json
import os
import shutil
import sys
import tempfile
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
FAILS: list[str] = []
N = 0


def check(name, cond, detail=""):
    global N
    N += 1
    print(("PASS " if cond else "FAIL ") + name + ("" if cond else f"  -- {detail}"))
    if not cond:
        FAILS.append(name)


def setup():
    tmp = tempfile.mkdtemp(prefix="telemetry_selftest_")
    j = os.path.join
    for d in ("jb/tps/flight", "jb/tps/exc", "jb/health", "scratch", "art", "inbox/changes", "inbox/wsl", "mirror"):
        os.makedirs(j(tmp, d), exist_ok=True)
    c = {"root": tmp, "db": j(tmp, "events.db"), "raw": j(tmp, "raw"), "state": j(tmp, "state"),
         "inbox": j(tmp, "inbox"), "logs": j(tmp, "logs"), "archive": j(tmp, "arch", "telemetry_archive"),
         "jawabench": j(tmp, "jb"), "bridge_calls": j(tmp, "scratch", "bridge_calls.jsonl"),
         "artpipe": j(tmp, "art"), "mirror": j(tmp, "mirror"), "vm_url": "http://fake",
         "game_mods": j(tmp, "rw", "Mods"), "modsconfig": j(tmp, "ModsConfig.xml"), "dirs": {}, "volumes": {},
         "vhdx": j(tmp, "none.vhdx")}
    os.makedirs(j(tmp, "arch"), exist_ok=True)
    with open(j(tmp, "cfg.json"), "w") as f:
        json.dump(c, f)
    os.environ["TELEMETRY_CONFIG"] = j(tmp, "cfg.json")
    import tcommon
    tcommon.reset_cfg()
    return tmp, c


class FakeVM:
    def __init__(self):
        self.lines = []
        self.down = False

    def __call__(self, body: bytes):
        if self.down:
            raise ConnectionRefusedError("fake VM down")
        self.lines.extend(json.loads(x) for x in body.decode().splitlines() if x)

    def names(self):
        return {x["metric"]["__name__"] for x in self.lines}

    def of(self, name):
        return [x for x in self.lines if x["metric"]["__name__"] == name]


def iso(ts):
    return time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime(ts)) + ".000Z"


def w(path, rows, partial=None):
    with open(path, "a") as f:
        for r in rows:
            f.write((r if isinstance(r, str) else json.dumps(r)) + "\n")
        if partial:
            f.write(partial)


def main(argv) -> int:
    tmp, c = setup()
    import analysis
    import ingest
    import store
    from tcommon import loads, parse_ts
    try:
        # ---------------------------------------------------------------- parsing
        r = loads('{"seq":1,"kind":"incident","type":"stall","kind":"stall","gapS":41}')
        check("[kind] duplicate kind keeps the envelope's", r["kind"] == "incident" and r["kind_2"] == "stall", r)
        check("parse_ts Z / offset / epoch-ms", abs(parse_ts("2026-10-11T14:09:43-0700") - parse_ts("2026-10-11T21:09:43Z")) < 1
              and parse_ts(1791754000000) == 1791754000.0)

        # ---------------------------------------------------------------- ingest
        vm = FakeVM()
        sink = store.VMSink(url="http://fake", spool_dir=os.path.join(tmp, "spool"), post=vm)
        con = store.connect()
        latest: dict = {}
        T = ingest.Tailer(con, sink, latest)
        S = {s.name: s for s in ingest.make_sources()}
        t0 = time.time() - 600
        tps = os.path.join(c["jawabench"], "tps", "tps_x_sess_1_000.jsonl")
        base = {"v": 2, "session": "abcdef0123456789"}
        w(tps, [
            {**base, "seq": 1, "utc": iso(t0), "kind": "session", "pid": 1, "modDigest": "d1", "modOrderDigest": "o1",
             "build": "b1", "mods": 26},
            {**base, "seq": 2, "utc": iso(t0 + 5), "kind": "sample", "state": "paused", "dTicks": 0, "tps": 0, "tickMs": 0,
             "ratio": None, "mult": 0, "heapMB": 600, "fps": 60, "gc": 10},
            {**base, "seq": 3, "utc": iso(t0 + 6), "kind": "sample", "state": "run", "dTicks": 300, "tps": 60, "tickMs": 7,
             "ratio": 1.0, "mult": 1, "heapMB": 610, "gc": 12, "tier": "test",
             "attr": {"tick": [300, 2100, 30], "mapComp": [300, 600, 9]}, "worst": [{"ms": 31}, {"ms": 45}],
             "hist": [[1, 250], [4, 48], [27, 2]], "histV": 1,
             "exc": {"n": 7, "sup": 2, "e": 5, "w": 2, "m": 0, "rep": 0, "over": 0, "top": [["E:NRE at #", 5]]},
             "br": {"calls": 3, "mainMs": 4.5, "qMaxMs": 1.2}},
            '{"seq":4,"v":2,"utc":"%s","mono":1,"session":"abcdef0123456789","kind":"incident","type":"stall","kind":"stall","gapS":41}' % iso(t0 + 7),
            {**base, "seq": 5, "utc": iso(t0 + 8), "kind": "context", "maps": [{"id": 0, "biome": "Desert", "pawns": 9, "things": 100}],
             "mapCount": 1, "worldPawns": 4, "workingSetMB": 0},
            {**base, "seq": 6, "utc": iso(t0 + 9), "kind": "flight", "file": "flight_abc_6.jsonl.gz", "trigger": "tick>250ms",
             "tickFrom": 100, "tickTo": 8291, "worstDurUs": 512000},
            {**base, "seq": 7, "utc": iso(t0 + 10), "kind": "mapcomp", "type": "MapComponent_X", "mod": "HugeThings",
             "msPerTick": 70.1, "calls": 900, "maxMs": 120, "ticks": 900},
        ], partial='{"seq":8,"utc":"%s","kind":"sam' % iso(t0 + 11))
        T.pass_source(S["tps"])
        sink.flush()
        names = vm.names()
        check("every game series carries the mod set (A) and versions (B)", all(
            x["metric"].get("mods") == "d1" and x["metric"].get("modver") == "o1" for x in vm.of("rm_game_heap_mb")),
            vm.of("rm_game_heap_mb"))
        check("[paused] a paused window emits no tps/tick_ms point",
              len(vm.of("rm_game_tps")) == 1 and len(vm.of("rm_game_tick_ms")) == 1, vm.of("rm_game_tps"))
        check("sample -> stage, worst tick, heap, running", {"rm_game_stage_ms", "rm_game_worst_tick_ms", "rm_game_heap_mb",
                                                            "rm_game_running"} <= names, names)
        check("P2 fields -> hist / exc / bridge occupancy series",
              {"rm_game_tick_hist", "rm_game_exc", "rm_game_exc_suppressed", "rm_game_bridge_main_ms"} <= names, names)
        les = sorted(x["metric"]["le"] for x in vm.of("rm_game_tick_hist"))
        check("hist buckets -> ms upper edges (bucket 1 = 0.363 ms, 27 = +Inf)", les == ["+Inf", "0.363", "1.11"], les)
        check("context: workingSetMB 0 is not emitted (unread, not zero)", not vm.of("rm_game_working_set_mb"))
        kinds = {r[0] for r in con.execute("SELECT kind FROM events")}
        check("[kind] incident lands as an incident event", "incident" in kinds and "stall" not in kinds, kinds)
        check("flight + mapcomp tables", con.execute("SELECT COUNT(*) FROM flight").fetchone()[0] == 1
              and con.execute("SELECT ms_per_tick FROM mapcomp").fetchone()[0] == 70.1)
        check("exception signature counted", con.execute("SELECT n FROM exc_sigs").fetchone()[0] == 5)
        before = con.execute("SELECT COUNT(*) FROM events").fetchone()[0]
        w(tps, ['ple","session":"abcdef0123456789","state":"run","dTicks":10,"tps":50,"mult":1}'])
        T.pass_source(S["tps"])
        check("partial line waits, then the completed line is read once",
              T.stats["tps"]["bad"] == 0 and con.execute("SELECT COUNT(*) FROM events").fetchone()[0] == before)
        T.pass_source(S["tps"])
        check("idempotent re-pass reads nothing", T.stats["tps"]["rows"] == 8, T.stats["tps"])

        # bridge: rotation by rename, buckets
        bc = c["bridge_calls"]
        tb = int(t0 // 10) * 10 + 100
        rows = []
        for i in range(6):
            rows.append({"ev": "start", "cid": f"c{i}", "tool": "jawa/a" if i < 4 else "jawa/b", "t": iso(tb + i)})
            rows.append({"ev": "end", "cid": f"c{i}", "ms": 10 * (i + 1), "success": i != 5, "t": iso(tb + i)})
        w(bc, rows[:6])
        T.pass_source(S["bridge"])
        os.replace(bc, bc + ".1")
        w(bc + ".1", rows[6:8])
        w(bc, rows[8:] + [{"ev": "start", "cid": "late", "tool": "jawa/a", "t": iso(tb + 60)},
                          {"ev": "end", "cid": "late", "ms": 1, "success": True, "t": iso(tb + 60)}])
        T.pass_source(S["bridge"])
        T.pass_source(S["bridge"])
        n_calls = con.execute("SELECT COUNT(*) FROM bridge_calls WHERE ms IS NOT NULL").fetchone()[0]
        check("[rotate] every call read exactly once across the rename", n_calls == 7, n_calls)
        sink.flush()
        a = [x for x in vm.of("rm_bridge_calls") if x["metric"]["tool"] == "jawa/a"]
        check("bridge 10 s bucket: count / sum / max", a and a[0]["values"] == [4.0]
              and vm.of("rm_bridge_ms_max")[0]["values"][0] >= 40, a)
        check("bridge errors counted", sum(x["values"][0] for x in vm.of("rm_bridge_errors")) == 1)

        # changes inbox + emit helper
        import telemetry_emit
        ok = telemetry_emit.emit_change("deploy", "HugeThings", sha="abc123", detail={"mods": {"HugeThings": 3}})
        T.pass_source(S["changes"])
        d = con.execute("SELECT subject, sha FROM events WHERE kind='deploy'").fetchone()
        check("emit_change -> deploy event", ok and d and d[0] == "HugeThings" and d[1] == "abc123", d)

        # wsl inbox
        w(os.path.join(c["inbox"], "wsl", "wsl_x.jsonl"), [
            {"src": "memwatch_sample", "ts": "2026-10-11T14:09:43-0700", "cgroups": {
                "claude-seats.slice/claude-seat-BENCH-1130.scope": {"current": 5, "stat": {"shmem": 1}, "psi": {}, "events": {}}}},
            {"src": "ledger", "ts": "2026-10-11T20:00:00Z", "event": "bridge", "state": "taken", "seat": "BENCH", "_h": "aa"},
            {"src": "ledger", "ts": "2026-10-11T20:00:00Z", "event": "bridge", "state": "taken", "seat": "BENCH", "_h": "aa"},
            {"src": "wsl_host", "ts": time.time(), "disk_used": 300 << 30, "mem_avail": 1, "mem_total": 2},
        ])
        T.pass_source(S["wsl"])
        sink.flush()
        check("memwatch cgroup label drops the pid", any(x["metric"].get("cg") == "claude-seats.slice/seat-BENCH"
                                                         for x in vm.of("rm_cg_mem_bytes")))
        check("ledger rows dedupe by line hash", con.execute("SELECT COUNT(*) FROM events WHERE kind='bridge_hold'").fetchone()[0] == 1)

        # raw copies
        T.flush_raw(force=True)
        raws = {os.path.basename(os.path.dirname(p)) for p in __import__("glob").glob(os.path.join(c["raw"], "*", "*.gz"))}
        check("raw gzip copy per source", {"tps", "bridge", "changes", "wsl"} <= raws, raws)
        with gzip.open(__import__("glob").glob(os.path.join(c["raw"], "bridge", "*.gz"))[0], "rt") as f:
            check("raw bridge copy holds every line", sum(1 for _ in f) == 14)

        # VM spool
        vm.down = True
        sink.add("rm_x", {}, 1, time.time())
        sink.flush()
        check("VM down -> spooled, error recorded", sink.spooled == 1 and sink.last_error and os.listdir(sink.spool_dir))
        vm.down = False
        sink.flush()
        check("VM back -> spool replayed", not os.listdir(sink.spool_dir) and vm.of("rm_x"))

        # ---------------------------------------------------------------- alerts
        now = time.time()
        GB = 1 << 30
        lat = {"host": {"ts": now, "vols": {"C": {"free": 10 * GB, "total": 100 * GB}, "D": {"free": 40 * GB, "total": 1},
                                            "E": {"free": 2000 * GB, "total": 1}},
                        "vhdx": {"alloc": 900 * GB, "size": 1}, "mem": {"commit_total": 95, "commit_limit": 100}},
               "wsl_host": {"disk_used": 300 * GB},
               "tps_hist": [(now - 130 + i * 5, 0.2, "run", 1) for i in range(27)],
               "incidents": [{"ts": now - 60, "gapS": 41.0, "type": "stall"}, {"ts": now - 60, "gapS": 3.0, "type": "stall"}],
               "tps": {"ts": now, "exc": 600, "dReal": 1.0}, "game_running": True, "game_running_since": now - 3600}
        al = {x["id"].split(":")[0] + ":" + x["level"] for x in analysis.evaluate(lat, con, {"tps": {"last_row_ts": now - 300}}, None, now)}
        check("disk red < 20 GB, amber < 50 GB", {"disk:red", "disk:amber"} <= al, al)
        check("no empty-space / image-slack alert exists (owner: not a danger)", not any("slack" in x for x in al), al)
        check("commit > 90 %", "commit:amber" in al)
        lat["host"]["mem"]["phys_avail"] = 2 * GB
        check("extremely low memory -> red", "mem_low:red" in {x["id"] + ":" + x["level"] for x in analysis.evaluate(lat, con, {}, None, now)})
        check("TPS ratio low at normal speed for 2 min", "tps_low:amber" in al, al)
        check("only stalls >= 10 s alert", sum(1 for x in al if x.startswith("stall")) == 1, al)
        check("exception storm", "exc_storm:amber" in al)
        check("blind: game running, TPS record silent", "blind:amber" in al, al)
        lat["tps_hist"] = [(now - 130 + i * 5, 0.2, "run", 1, 0.5 if i % 3 else 0.0) for i in range(27)]
        check("bridge-busy windows are not judged (too few calm windows -> no TPS alarm)",
              "tps_low" not in {x["id"] for x in analysis.evaluate(lat, con, {}, None, now)})
        fired = analysis.evaluate(lat, con, {}, None, now)
        check("each alarm firing is logged once for labelling", analysis.log_firings(con, fired, now) == len(fired)
              and analysis.log_firings(con, fired, now) == 0)
        lat["tps_hist"] = [(now - 130 + i * 5, 0.05, "run", 6) for i in range(27)]
        al2 = {x["id"] for x in analysis.evaluate(lat, con, {}, None, now)}
        check("speed 3 (x6) CPU-bound ratio does not alert", "tps_low" not in al2)
        analysis.push_spark(lat, now)
        check("sparks carry four series", set(lat["sparks"]) == {"tps_ratio", "exc_per_s", "host_free_gb", "min_vol_free_gb"})

        # ---------------------------------------------------------------- regression detector + sanity probe
        import random
        rnd = random.Random(7)
        quiet = [18 + rnd.gauss(0, 1.5) for _ in range(80)]
        quiet2 = [18 + rnd.gauss(0, 1.5) for _ in range(80)]
        rot = [93.6 + rnd.gauss(0, 5) for _ in range(80)]   # the Rot-map regression's scale (huge_footprints_perf.md)
        check("sanity probe: known non-regression reads NO_SHIFT", analysis.compare_windows(quiet, quiet2)["verdict"] == "NO_SHIFT")
        check("sanity probe: Rot-map-sized slowdown reads REGRESSION", analysis.compare_windows(quiet, rot)["verdict"] == "REGRESSION")
        check("too few windows reads UNMEASURED, never clean", analysis.compare_windows(quiet[:10], rot)["verdict"] == "UNMEASURED")
        # proof flips
        pdir = os.path.join(c["mirror"], "src", "RimMandrake", "FlowWorks", "northstar")
        os.makedirs(pdir)
        for i, st in enumerate(("PASS", "FAIL")):
            with open(os.path.join(pdir, f"proof_2026101{i}T000000.json"), "w") as f:
                json.dump({"script": "proof_hose.py", "rows": [{"id": "R1", "status": st}, {"id": "R2", "status": "PASS"}]}, f)
        check("proof results ingested", ingest.ingest_proofs(con) == 2)

        # retention
        old = os.path.join(c["raw"], "tps", "2026-01-01.jsonl.gz")
        with gzip.open(old, "wb") as f:
            f.write(b"x\n")
        os.utime(old, (now - 100 * 86400, now - 100 * 86400))
        con.execute("INSERT INTO bridge_calls(cid, ts) VALUES('ancient', ?)", (now - 40 * 86400,))
        rep = analysis.retention(con, now)
        check("raw older than 90 d moves to the archive", rep["moved"] == 1 and os.path.exists(
            os.path.join(c["archive"], "raw", "tps", "2026-01-01.jsonl.gz")), rep)
        check("per-call bridge rows older than 30 d pruned", rep["bridge_rows"] == 1)

        # ---------------------------------------------------------------- RimPulse integration
        sys.path.insert(0, os.path.join(os.path.dirname(HERE), "pulse"))
        import pulse_core as pc
        t = {"at": now, "grafana": "http://localhost:3000", "alerts": [
            {"id": "disk:C", "level": "red", "text": "C: only 10 GB free", "since": now - 5},
            {"id": "stall:1", "level": "amber", "text": "game froze 41 s", "since": now - 5}], "tier_armed": True}
        rows = pc.classify_telemetry(t, {}, now)
        check("pulse: red alert -> red row, amber -> warn row, armed tier -> run row",
              [r["kind"] for r in rows] == ["red", "warn", "run"], [r["kind"] for r in rows])
        acked = pc.classify_telemetry(t, {rows[1]["incident"]: {"at": now}}, now)
        check("pulse: an ack holds for that incident", acked[1]["acked"])
        stale = pc.classify_telemetry({**t, "at": now - 900}, {}, now)
        check("pulse: stale alerts file -> one 'telemetry blind' row", len(stale) == 1 and "blind" in stale[0]["text"])
        check("pulse: absent file -> no row (not installed is not an alarm)", pc.classify_telemetry(None, {}, now) == [])
        strip = pc.build_strip(rows)
        check("pulse: warn pill names telemetry, not 'test kill'", any(p["kind"] == "warn" and "froze" in p["text"] for p in strip), strip)

        # ---------------------------------------------------------------- wsl exporter tail
        import wsl_export
        f = os.path.join(tmp, "mw.jsonl")
        st: dict = {}
        w(f, [{"a": 1}])
        r1 = wsl_export.tail(f, st, "k")
        w(f, [{"a": 2}])
        os.replace(f, f + ".1")
        w(f, [{"a": 3}])
        r2 = wsl_export.tail(f, st, "k")
        check("[rotate] exporter tail follows rename", [x["a"] for x in r1] == [1] and sorted(x["a"] for x in r2) == [2, 3], (r1, r2))

        # dashboards are generated, not hand-edited
        sys.path.insert(0, os.path.join(HERE, "grafana"))
        import build_dashboards
        check("Grafana dashboards match their generator", build_dashboards.main(["--check"]) == 0)
        for fn in os.listdir(build_dashboards.HERE):
            d = json.load(open(os.path.join(build_dashboards.HERE, fn)))
            uids = {p.get("datasource", {}).get("uid") for p in d["panels"] if p["type"] != "row"}
            check(f"{fn}: panels use only the two provisioned datasources", uids <= {"vm", "events"}, uids)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    if "--live" in argv:
        live()
    print(f"\n{'OK' if not FAILS else 'FAILED'}: {N - len(FAILS)}/{N} passed" + (f"; failing: {FAILS}" if FAILS else ""))
    return 1 if FAILS else 0


def live():
    """The real stack (only with --live; touches nothing, reads state and asks over HTTP)."""
    import subprocess
    st = "/mnt/e/telemetry/state"
    hb = json.load(open(os.path.join(st, "heartbeat.json")))
    check("[heartbeat] live: telemetryd heartbeat < 3 min", time.time() - hb["at"] < 180, hb)
    al = json.load(open(os.path.join(st, "alerts.json")))
    check("live: alerts file < 3 min", time.time() - al["at"] < 180)
    code = ("import urllib.request as u\n"
            "for x in ('http://127.0.0.1:8428/health','http://127.0.0.1:3000/api/health'):\n"
            "  print(u.urlopen(x,timeout=5).status)")
    r = subprocess.run(["python.exe", "-c", code], capture_output=True, text=True, timeout=60)
    check("live: VictoriaMetrics and Grafana answer HTTP 200", r.stdout.split() == ["200", "200"], r.stdout + r.stderr)
    ps = ("(Get-Process | Where-Object { $_.ProcessName -match 'grafana|gpx_|victoria-metrics' "
          "-and $_.MainWindowHandle -ne 0 }).Count")
    r = subprocess.run(["powershell.exe", "-NoProfile", "-Command", ps], capture_output=True, text=True, timeout=60)
    check("[windows] live: no telemetry process owns a visible window", r.stdout.strip() == "0", r.stdout + r.stderr)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
