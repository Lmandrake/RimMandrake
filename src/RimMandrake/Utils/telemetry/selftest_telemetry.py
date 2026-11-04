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
  * A .1 backlog bigger than MAX_READ, read in the same pass as the live file, delivered a call's end before
    its start (bucket tool '?', then an unfinished call). Ordered sources stop at a partial file; an end
    that still comes first parks its row and the late start fills it.                              [order]
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
    for d in ("jb/tps/flight", "jb/tps/exc", "jb/health", "scratch", "art", "inbox/changes", "inbox/wsl", "mirror", "ops/series"):
        os.makedirs(j(tmp, d), exist_ok=True)
    c = {"root": tmp, "db": j(tmp, "events.db"), "raw": j(tmp, "raw"), "state": j(tmp, "state"),
         "inbox": j(tmp, "inbox"), "logs": j(tmp, "logs"), "archive": j(tmp, "arch", "telemetry_archive"),
         "jawabench": j(tmp, "jb"), "bridge_calls": j(tmp, "scratch", "bridge_calls.jsonl"),
         "artpipe": j(tmp, "art"), "mirror": j(tmp, "mirror"), "vm_url": "http://fake",
         "game_mods": j(tmp, "rw", "Mods"), "modsconfig": j(tmp, "ModsConfig.xml"), "dirs": {}, "volumes": {},
         "vhdx": j(tmp, "none.vhdx"), "ops_watch_series": j(tmp, "ops", "series")}
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
    check("[loads] deeply nested JSON is one bad row (None), not a RecursionError that stalls the file",
          loads(b"[" * 100000 + b"]" * 100000) is None)
    check("[parse_ts] a boolean is not a time", parse_ts(True) is None and parse_ts(1.5e9) == 1.5e9)
    check("[parse_ts] an integer past float range is None, not an OverflowError", parse_ts(10 ** 400) is None)
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
        # [rebuild] `telemetry rebuild` forgets cursors and re-reads: counts and raw copies must not double
        T.flush_raw(force=True)
        import cli
        cli.main(["rebuild", "--since", "7d"])
        T.pass_source(S["tps"])
        T.flush_raw(force=True)
        check("[rebuild] re-reading a file does not re-count exception signatures",
              con.execute("SELECT n FROM exc_sigs").fetchone()[0] == 5, con.execute("SELECT n FROM exc_sigs").fetchone()[0])
        with gzip.open(__import__("glob").glob(os.path.join(c["raw"], "tps", "*.gz"))[0], "rt") as f:
            n_raw = sum(1 for _ in f)
        check("[rebuild] re-reading a file does not re-append its raw copy", n_raw == 8, n_raw)

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
        check("[bridge] when calls stop, an idle pass closes the last open bucket",
              any(x["timestamps"] == [(tb + 60) * 1000] for x in a), [x["timestamps"] for x in a])
        check("[freshness] bridge rows advance the bridge source's freshness",
              abs((T.stats["bridge"]["last_row_ts"] or 0) - (tb + 60)) < 1, T.stats["bridge"])
        hb_ = int(time.time() // 10) * 10    # a bucket the wall clock is still inside: idle passes must not split it
        w(bc, [{"ev": "start", "cid": "h1", "tool": "jawa/h", "t": iso(hb_ + 1)},
               {"ev": "end", "cid": "h1", "ms": 3, "success": True, "t": iso(hb_ + 1)}])
        T.pass_source(S["bridge"])
        T.pass_source(S["bridge"])
        w(bc, [{"ev": "start", "cid": "h2", "tool": "jawa/h", "t": iso(hb_ + 4)},
               {"ev": "end", "cid": "h2", "ms": 5, "success": True, "t": iso(hb_ + 4)}])
        T.pass_source(S["bridge"])
        ingest.flush_bridge_buckets(ingest.Emit(con, sink, latest), force=True)
        sink.flush()
        hp = [x["values"] for x in vm.of("rm_bridge_calls") if x["metric"]["tool"] == "jawa/h"]
        check("[bridge] an idle pass leaves a bucket the clock is still inside open (one point, both calls)",
              hp == [[2.0]], hp)

        # unknown success (non-dict result) is NULL, not a failure; status decides
        w(bc, [{"ev": "start", "cid": "u1", "tool": "jawa/u", "t": iso(tb + 70)},
               {"ev": "end", "cid": "u1", "ms": 5, "status": "ok", "success": None, "t": iso(tb + 70)},
               {"ev": "start", "cid": "u2", "tool": "jawa/u", "t": iso(tb + 71)},
               {"ev": "end", "cid": "u2", "ms": 5, "status": "error", "success": None, "t": iso(tb + 71)}])
        T.pass_source(S["bridge"])
        import tcommon as _ing
        u = {r[0]: r[1] for r in con.execute("SELECT cid, success FROM bridge_calls WHERE cid IN ('u1','u2')")}
        check("[success] unknown stored NULL; failure judged by status",
              u == {"u1": None, "u2": None} and not _ing.bridge_failed(None, "ok") and _ing.bridge_failed(None, "error")
              and _ing.bridge_failed(0, "ok") and not _ing.bridge_failed(1, "ok"), u)

        # [order] a rotated .1 holding a backlog past MAX_READ: the starts sit in .1's unread tail, the ends in the live
        # file. Reading the live file in the same pass delivered each end first (tool '?', then an unfinished call).
        # The old .1 stays open until the new live file exists: ext4 would hand the freed inode to the new file and it
        # would inherit the dead file's cursor (a fixture artifact; NTFS file ids carry a reuse sequence number).
        with open(bc + ".1", "rb"):
            os.replace(bc, bc + ".1")
            w(bc + ".1", [{"ev": "start", "cid": f"o{i}", "tool": "jawa/o", "t": iso(tb + 80),
                                "script": "s" * 250} for i in range(10)])    # fat starts: the ends would outrun them
            time.sleep(0.02)
            w(bc, [{"ev": "end", "cid": f"o{i}", "ms": 2, "success": True, "t": iso(tb + 81)} for i in range(10)])
        mr0, ingest.MAX_READ = ingest.MAX_READ, 400
        try:
            for _ in range(30):     # one ~330-byte start per 400-byte read: 10 starts need 10 passes
                T.pass_source(S["bridge"])
        finally:
            ingest.MAX_READ = mr0
        ingest.flush_bridge_buckets(ingest.Emit(con, sink, latest), force=True)
        sink.flush()
        oc = con.execute("SELECT COUNT(*) FROM bridge_calls WHERE cid LIKE 'o%' AND tool='jawa/o' AND ts IS NOT NULL "
                         "AND ms IS NOT NULL").fetchone()[0]
        qn = [x for x in vm.of("rm_bridge_calls") if x["metric"]["tool"] == "?"]
        check("[order] a .1 backlog past MAX_READ drains before the live file: no call ends before it starts",
              oc == 10 and not qn, (oc, qn))
        # an end that still arrives first (no start yet) is parked in the row; its start fills tool and ts, never lost
        w(bc, [{"ev": "end", "cid": "p1", "ms": 4, "success": True, "t": iso(tb + 90)}])
        T.pass_source(S["bridge"])
        w(bc, [{"ev": "start", "cid": "p1", "tool": "jawa/p", "t": iso(tb + 89)}])
        T.pass_source(S["bridge"])
        p1 = con.execute("SELECT ts, ts_end, tool, ms FROM bridge_calls WHERE cid='p1'").fetchone()
        check("[order] an end before its start keeps the end; the late start fills tool and ts",
              p1 is not None and tuple(p1) == (float(tb + 89), float(tb + 90), "jawa/p", 4.0), p1 and tuple(p1))

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
        mr0, ingest.MAX_READ = ingest.MAX_READ, 128
        try:    # a row longer than one whole read must not stall the file; a measured 0 is a point, not None
            w(os.path.join(c["inbox"], "wsl", "wsl_long.jsonl"), [
                {"src": "wsl_host", "ts": time.time(), "pad": "x" * 300},
                {"src": "objstore", "ts": time.time(), "store_bytes": 0, "store_hardlinked_bytes": 7}])
            for _ in range(8):
                T.pass_source(S["wsl"])
        finally:
            ingest.MAX_READ = mr0
        sink.flush()
        ob = [x["values"] for x in vm.of("rm_objstore_bytes")]
        check("[tail] a row past MAX_READ is skipped, the next row still lands; store_bytes 0 stays 0", ob == [[0.0]], ob)

        # raw copies
        T.flush_raw(force=True)
        raws = {os.path.basename(os.path.dirname(p)) for p in __import__("glob").glob(os.path.join(c["raw"], "*", "*.gz"))}
        check("raw gzip copy per source", {"tps", "bridge", "changes", "wsl"} <= raws, raws)
        with gzip.open(__import__("glob").glob(os.path.join(c["raw"], "bridge", "*.gz"))[0], "rt") as f:
            check("raw bridge copy holds every line", sum(1 for _ in f) == 44)   # 12 + late 2 + u 4 + h 4 + order 22

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
        st_ids = [x["id"] for x in analysis.evaluate(lat, con, {}, None, now) if x["id"].startswith("stall")]
        check("only stalls >= 10 s alert", len(st_ids) == 1, st_ids)
        check("exception storm", "exc_storm:amber" in al)
        l2 = dict(lat, tps={"ts": now, "exc": 24, "dReal": 0.05})
        check("[storm] 24 errors in a 0.05 s window is not a storm",
              "exc_storm" not in {x["id"] for x in analysis.evaluate(l2, con, {}, None, now)})
        l2["tps"] = {"ts": now, "exc": 5, "dReal": 1.0}
        check("[storm] 5 errors is not a storm", "exc_storm" not in {x["id"] for x in analysis.evaluate(l2, con, {}, None, now)})
        l2["incidents"] = [{"ts": now - 60, "gapS": 11.0, "type": "stall"}]
        l2["bridge_holds"] = [(now - 55, 10890)]
        check("[stall] a freeze covered by a bridge main-thread hold is an epoch, not an alert",
              not any(x["id"].startswith("stall") for x in analysis.evaluate(l2, con, {}, None, now)))
        l2["bridge_holds"] = [(now - 55, 300)]
        check("[stall] a freeze with no bridge hold still alerts",
              any(x["id"].startswith("stall") for x in analysis.evaluate(l2, con, {}, None, now)))
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
        z = {"host": {"ts": now, "vols": {}, "mem": {"phys_avail": 0}}}
        check("[mem] zero bytes available is the reddest reading, not a missing one",
              "mem_low" in {x["id"] for x in analysis.evaluate(z, con, {}, None, now)})
        analysis.push_spark(z, now)
        check("[spark] zero available memory plots as 0", z["sparks"]["host_free_gb"][-1][1] == 0, z["sparks"])
        st_h = {"host": {"ts": now - 3600, "vols": {"C": {"free": 9 * GB}}, "mem": {"phys_avail": 8 * GB}}}
        analysis.push_spark(st_h, now)
        check("[spark] a host reading an hour old is a gap, not a fresh point",
              st_h["sparks"]["host_free_gb"][-1][1] is None and st_h["sparks"]["min_vol_free_gb"][-1][1] is None,
              st_h["sparks"])
        vl = {}
        f1 = analysis.evaluate(vl, con, {}, "URLError: down", now)
        f2 = analysis.evaluate(vl, con, {}, "URLError: down", now + 60)
        n_f = analysis.log_firings(con, f1, now) + analysis.log_firings(con, f2, now + 60)
        f3 = analysis.evaluate(vl, con, {}, None, now + 120)
        f4 = analysis.evaluate(vl, con, {}, "URLError: down", now + 180)
        check("[firing] one continuous VM outage logs one firing; a new outage after recovery is a new one",
              n_f == 1 and not f3 and f4[0]["since"] == now + 180, (n_f, f4))
        old_h = {"host": {"ts": now - 3600, "vols": {"C": {"free": 1 * GB, "total": 100 * GB}},
                          "mem": {"phys_avail": 0}}}
        ids_h = {x["id"] for x in analysis.evaluate(old_h, con, {}, None, now)}
        check("[host] an hour-old host sample raises blind:host, not disk/memory alerts from stale numbers",
              "blind:host" in ids_h and "mem_low" not in ids_h and not any(i.startswith("disk") for i in ids_h), ids_h)
        ws = {}
        analysis.evaluate(ws, con, {"wsl": {"last_row_ts": None}}, None, now)
        late = analysis.evaluate(ws, con, {"wsl": {"last_row_ts": None}}, None, now + analysis.RULES["wsl_blind_s"] + 5)
        check("[blind] an exporter that never wrote a usable row reads blind:wsl", "blind:wsl" in {x["id"] for x in late},
              late)

        # ---------------------------------------------------------------- test-state monitor (vitals rows)
        tv = os.path.join(c["jawabench"], "tps", "tps_x_sess_1_009.jsonl")
        vb = {"v": 2, "session": "abcdef0123456789", "kind": "vitals", "epoch": 0, "row": "r1", "curMap": 0}
        w(tv, [
            {**vb, "seq": 100, "utc": iso(now - 20), "ch": "heartbeat", "what": "arm", "tick": 1000},
            {**vb, "seq": 101, "utc": iso(now - 19), "ch": "pawns", "what": "rollup", "tick": 1000, "pawns": 4,
             "colonistsAlive": 3, "colonistsDowned": 0, "colonistsHostile": 0, "hostiles": 0, "critical": 1,
             "criticalAvailable": 1, "minColonistHealth": 1.0, "minColonistMoodMargin": None,
             "groups": {"humanlike|player": {"alive": 3, "downed": 0, "bleeding": 0, "mental": 0},
                        "animal|neutral": {"alive": 1, "downed": 0, "bleeding": 0, "mental": 0}}},
            {**vb, "seq": 102, "utc": iso(now - 18), "ch": "pawns", "what": "pawn", "pawn": {"id": 5}},
            {**vb, "seq": 103, "utc": iso(now - 17), "ch": "pawns", "what": "trigger",
             "trigger": {"seq": 1, "kind": "hostile_arrival", "severity": "threat", "subject": "Scyther", "detail": "arrived"}},
            {**vb, "seq": 104, "utc": iso(now - 16), "ch": "threats", "what": "threats", "structures": 2, "turrets": 1,
             "spawners": 0, "dormant": 1},
            {**vb, "seq": 105, "utc": iso(now - 15), "ch": "pawns", "what": "rollup", "tick": 1600, "pawns": 3,
             "colonistsAlive": 0, "colonistsHostile": 1, "hostiles": 2, "critical": 1, "criticalAvailable": 0,
             "minColonistHealth": None, "minColonistMoodMargin": None, "groups": {}},
            {**vb, "seq": 106, "utc": iso(now - 14), "ch": "heartbeat", "what": "heartbeat", "disc": 1, "discDeclared": 0,
             "triggers": 4, "modalMaxAgeS": 75.0, "rowsDropped": 0, "faults": 0,
             "meters": {"pawns": {"on": True, "calls": 3, "totalMs": 0.4}, "ui": {"on": True, "calls": 0, "totalMs": None}}},
        ])
        vm.lines.clear()
        T.pass_source(S["tps"])
        sink.flush()
        check("vitals rollup -> rm_game_pawns_* series", {"rm_game_pawns_colonists_alive", "rm_game_pawns_alive",
              "rm_game_pawns_hostile", "rm_game_threat_structures", "rm_game_clock_disc_total", "rm_game_modal_age_s",
              "rm_game_vitals_latched"} <= vm.names(), vm.names())
        check("vitals: n/a mood margin and null health are not emitted as 0",
              all(x["values"][0] != 0 for x in vm.of("rm_game_pawns_min_health")) and not vm.of("rm_game_pawns_min_mood_margin"))
        check("vitals: role and relationship are separate labels",
              {(x["metric"]["cls"], x["metric"]["rel"]) for x in vm.of("rm_game_pawns_alive")} == {("humanlike", "player"), ("animal", "neutral")})
        check("vitals: an UNMEASURED channel cost is not a 0 ms point",
              {x["metric"]["channel"] for x in vm.of("rm_game_vitals_cost_ms")} == {"pawns"})
        check("vitals: no row id on any series", not any("row" in x["metric"] for x in vm.lines))
        check("vitals: trigger lands as an event", con.execute("SELECT COUNT(*) FROM events WHERE kind='vitals_trigger'").fetchone()[0] == 1)
        va = {x["id"]: x["level"] for x in analysis.evaluate(latest, con, {}, None, now)}
        check("vitals alarms: colony dead red, colonist hostile red, hostiles amber, modal stuck amber",
              va.get("vitals:colony_dead") == "red" and va.get("vitals:colonist_hostile") == "red"
              and va.get("vitals:hostiles") == "amber" and va.get("vitals:modal_stuck") == "amber", va)
        quiet_v = {"vitals": {"ts": now, "colonistsAlive": 0, "had_colonists": False, "colonistsHostile": 0, "hostiles": 0}}
        check("vitals: a map that never had colonists is not 'colony dead'",
              not [x for x in analysis.evaluate(quiet_v, con, {}, None, now) if x["id"].startswith("vitals")])
        transient = {"vitals_triggers": [{"ts": now - 30, "kind": "colony_loss", "severity": "damage", "row": "r2",
                                          "detail": "alive colonists 0 on every map"}]}
        tv2 = {x["id"]: x["level"] for x in analysis.evaluate(transient, con, {}, None, now)}
        check("vitals: a latched colony loss alarms even after the rollup recovered", tv2.get("vitals:colony_dead") == "red", tv2)
        stale_v = {"vitals": {**latest["vitals"], "ts": now - 600}, "vitals_hb": {**latest["vitals_hb"], "ts": now - 600}}
        check("vitals: stale monitor rows raise no vitals alarm",
              not [x for x in analysis.evaluate(stale_v, con, {}, None, now) if x["id"].startswith("vitals")])

        # ---------------------------------------------------------------- ops_watch readings -> VM
        ow = os.path.join(c["ops_watch_series"], "disk.jsonl")
        n0 = len(vm.lines)
        w(ow, [{"t": now - 900, "family": "disk", "points": {
                   "disk.free_gb": {"v": 40.5, "m": "MEASURED"}, "disk.ok": {"v": True, "m": "MEASURED"},
                   "disk.gone": {"v": None, "m": "UNMEASURED"}, "disk.guess": {"v": 3, "m": "ESTIMATE"},
                   "disk.word": {"v": "fine", "m": "MEASURED"}, "disk.zero": {"v": 0, "m": "MEASURED"}}},
               {"t": "not a time", "points": {"disk.free_gb": {"v": 1, "m": "MEASURED"}}},
               {"t": float("inf"), "points": {"disk.free_gb": {"v": 1, "m": "MEASURED"}}},
               {"t": float("nan"), "points": {"disk.free_gb": {"v": 1, "m": "MEASURED"}}},
               {"t": 1e308, "points": {"disk.free_gb": {"v": 1, "m": "MEASURED"}}},
               {"t": 1e13, "points": {"disk.free_gb": {"v": 1, "m": "MEASURED"}}}],
          partial='{"t": %f, "points": {"disk.free_gb": {"v": 1' % now)
        T.pass_source(S["ops_watch"])
        sink.flush()
        got = vm.lines[n0:]
        rd = {x["metric"]["key"]: x for x in got if x["metric"]["__name__"] == "rm_ops_reading"}
        um = {x["metric"]["key"]: x["metric"]["m"] for x in got if x["metric"]["__name__"] == "rm_ops_unmeasured"}
        rows_ = [x for x in got if x["metric"]["__name__"] == "rm_ops_rows"]
        check("[ops_watch] MEASURED numbers become rm_ops_reading points, a measured 0 included",
              rd.get("disk.free_gb", {}).get("values") == [40.5] and rd.get("disk.zero", {}).get("values") == [0]
              and rd["disk.free_gb"]["metric"]["fam"] == "disk"
              and rd["disk.free_gb"]["timestamps"] == [int((now - 900) * 1000)], rd)
        check("[ops_watch] a boolean is 0/1 marked vt=bool", rd.get("disk.ok", {}).get("values") == [1.0]
              and rd["disk.ok"]["metric"].get("vt") == "bool", rd.get("disk.ok"))
        check("[ops_watch] UNMEASURED / ESTIMATE / text are blindness markers, never a value",
              set(rd) == {"disk.free_gb", "disk.ok", "disk.zero"}
              and um == {"disk.gone": "UNMEASURED", "disk.guess": "ESTIMATE", "disk.word": "TEXT"}, (sorted(rd), um))
        check("[ops_watch] one rm_ops_rows sample per good row; a bad, non-finite or huge time and a torn tail are "
              "skipped", [x["values"] for x in rows_] == [[6]], rows_)
        lr = (T.stats.get("ops_watch") or {}).get("last_row_ts")
        check("[ops_watch] a rejected time does not pin the source's freshness", lr is not None and abs(lr - (now - 900)) < 1,
              lr)
        bad_sink = store.VMSink(url="http://fake", spool_dir=os.path.join(c["state"], "spool_bad"), post=lambda b: None)
        bad_sink.add("rm_x", {}, 1.0, float("inf"))
        bad_sink.add("rm_x", {}, 2.0, now)
        check("[sink] a non-finite time is dropped at add, the rest of the batch still flushes",
              bad_sink.flush() == 1 and bad_sink.sent == 1, bad_sink.sent)
        w(os.path.join(c["ops_watch_series"], "net.jsonl"), [{"t": now, "family": "net", "points": None}])
        T.pass_source(S["ops_watch"])
        st_ow = T.stats["ops_watch"]
        check("[freshness] a row its parser rejected (points null) does not advance freshness",
              abs(st_ow["last_row_ts"] - (now - 900)) < 1 and st_ow.get("skipped", 0) >= 1, st_ow)
        inf_post = []
        inf_sink = store.VMSink(url="http://fake", spool_dir=os.path.join(c["state"], "spool_inf"),
                                post=lambda b: inf_post.append(b))
        inf_sink.add("rm_x", {}, float("inf"), now)
        inf_sink.add("rm_x", {}, float("-inf"), now)
        inf_sink.add("rm_x", {}, 5.0, now)
        check("[sink] +-inf values are dropped at add (VM would drop them from the batch, counted as sent)",
              inf_sink.flush() == 1 and b"Infinity" not in b"".join(inf_post), inf_post)
        inf_sink.add("rm_x", {}, 10 ** 400, now)
        inf_sink.add("rm_x", {}, 1.0, now + 3 * 86400)
        inf_sink.add("rm_x", {}, 1.0, 10 ** 400)
        check("[sink] an overflowing value or time and a time days ahead are refused at add, never raised or 'sent'",
              not inf_sink.points and inf_sink.dropped_ts == 2, (inf_sink.points, inf_sink.dropped_ts))
        rpvm = FakeVM()
        rp = store.VMSink(url="http://fake", spool_dir=os.path.join(c["state"], "spool_rp"), post=rpvm)
        rp._spool(b"{}\n")
        rpvm.down = True
        rp.flush()
        err_down = rp.last_error
        rpvm.down = False
        rp.flush()
        check("[spool] a failing replay is a VM error (blind:vm), cleared once the spool drains",
              err_down and "replay" in err_down and rp.last_error is None and not os.listdir(rp.spool_dir),
              (err_down, rp.last_error))
        rpvm.down = True
        rp.add("rm_x", {}, 1.0, now)
        rp.flush()
        rpvm.down = False
        rp.flush()      # nothing new queued: only the replay proves VM is back
        check("[spool] an empty flush whose replay drains clears the earlier transport error",
              rp.last_error is None and not os.listdir(rp.spool_dir), rp.last_error)
        sp = store.VMSink(url="http://fake", spool_dir=os.path.join(c["state"], "spool_many"), post=lambda b: None)
        for k in range(5):
            sp._spool(b"batch%d\n" % k)
        got_sp = sorted(os.listdir(sp.spool_dir))
        check("[spool] back-to-back spools never overwrite one another, and replay order is write order",
              len(got_sp) == 5 and [open(os.path.join(sp.spool_dir, x), "rb").read() for x in got_sp]
              == [b"batch%d\n" % k for k in range(5)], got_sp)
        flaky = FakeVM()
        flaky.down = True
        fs = store.VMSink(url="http://fake", spool_dir=os.path.join(c["state"], "spool_full"), post=flaky)

        def disk_full(body):
            raise OSError(28, "No space left on device")
        fs._spool = disk_full
        fs.add("rm_y", {}, 1.0, now)
        fs.flush()
        held = len(fs.points)
        flaky.down = False
        fs.flush()
        check("[spool] VM down and the spool unwritable: the batch stays queued and is sent on the next flush",
              held == 1 and fs.sent == 1 and [x["values"] for x in flaky.lines] == [[1.0]] and "spool" in
              (fs.last_error or "spool"), (held, fs.sent, flaky.lines))
        # ---------------------------------------------------------------- the VM read path (_get, vm_export)
        import subprocess
        import urllib.error
        import urllib.request
        body = (json.dumps({"metric": {"__name__": "rm_x"}, "timestamps": [3000, 1000, 9000, 2000, 4000, 4500],
                            "values": [3, 1, 9, None, "Infinity", "NaN"]}) + "\n").encode()
        calls = []
        saved = (urllib.request.urlopen, shutil.which, subprocess.run, store.IS_WIN)

        class _Done:
            def __init__(self, rc, out=b"", err=b""):
                self.returncode, self.stdout, self.stderr = rc, out, err

        def refuse(u, timeout=None):
            raise urllib.error.URLError(ConnectionRefusedError("refused"))
        try:
            store.IS_WIN = False
            urllib.request.urlopen = refuse
            shutil.which = lambda n: "/x/curl.exe" if n == "curl.exe" else None
            subprocess.run = lambda a, **k: calls.append(a) or _Done(0, body)
            ex = store.vm_export(["rm_x"], 1.0, 5.0, url="http://127.0.0.1:8428")
            check("[vm read] WSL: a refused local VM is read through curl.exe; export sorts, clips to [start,end], "
                  "drops nulls and +-Inf/NaN", calls and calls[0][0] == "/x/curl.exe" and "-f" in calls[0]
                  and ex == [({"__name__": "rm_x"}, [1.0, 3.0], [1.0, 3.0])], (calls, ex))
            # a systemd --user unit's PATH has no Windows dir: which() misses curl.exe, System32's copy is used
            calls.clear()
            shutil.which = lambda n: None
            saved_wc = store.WIN_CURL
            store.WIN_CURL = sys.executable           # any executable stands in for System32's curl.exe
            try:
                store.vm_export(["rm_x"], 1.0, 5.0, url="http://127.0.0.1:8428")
                fell = calls and calls[0][0] == sys.executable
                store.WIN_CURL = "/nonexistent/curl.exe"
                calls.clear()
                try:
                    store.vm_export(["rm_x"], 1.0, 5.0, url="http://127.0.0.1:8428")
                    gone = None
                except urllib.error.URLError as e:
                    gone = str(e)
            finally:
                store.WIN_CURL = saved_wc
                shutil.which = lambda n: "/x/curl.exe" if n == "curl.exe" else None
            check("[vm read] curl.exe off PATH (a systemd unit) is found at System32; absent there too, the refusal "
                  "is raised", fell and gone and not calls, (calls, gone))
            subprocess.run = lambda a, **k: _Done(22, b"", b"HTTP 400")
            try:
                store.vm_export(["rm_x"], 1.0, 5.0, url="http://127.0.0.1:8428")
                raised = None
            except OSError as e:
                raised = str(e)
            check("[vm read] curl.exe failing raises, never an empty answer", raised and "exit 22" in raised, raised)
            dup = (json.dumps({"metric": {"__name__": "rm_x"}, "timestamps": [2000, 2000, 1000],
                               "values": [1, "NaN", 7]}) + "\n").encode()
            subprocess.run = lambda a, **k: _Done(0, dup)
            try:
                ex2 = store.vm_export(["rm_x"], 1.0, 5.0, url="http://127.0.0.1:8428")
            except TypeError as e:
                ex2 = e
            check("[vm read] a duplicate time holding a number and a NaN string is dropped, not a TypeError",
                  ex2 == [({"__name__": "rm_x"}, [1.0, 2.0], [7.0, 1.0])], ex2)
            calls.clear()
            subprocess.run = lambda a, **k: calls.append(a) or _Done(0, body)
            try:
                store.vm_export(["rm_x"], 1.0, 5.0, url="http://10.0.0.9:8428")
                raised = None
            except urllib.error.URLError as e:
                raised = str(e)
            check("[vm read] a non-local VM is not retried through curl.exe", raised and not calls, (raised, calls))

            def http400(u, timeout=None):
                raise urllib.error.HTTPError(u, 400, "bad selector", {}, None)
            urllib.request.urlopen = http400
            try:
                store.vm_export(["rm_x"], 1.0, 5.0, url="http://127.0.0.1:8428")
                raised = None
            except urllib.error.HTTPError as e:
                raised = e.code
            check("[vm read] an HTTP error from VM is raised as is, not retried", raised == 400 and not calls,
                  (raised, calls))
            urllib.request.urlopen = refuse
            shutil.which = lambda n: None
            check("[vm read] VM unreachable: windows_from_vm is empty, so compare_windows reads UNMEASURED",
                  analysis.windows_from_vm("rm_x", 1.0, 5.0) == []
                  and analysis.compare_windows(analysis.windows_from_vm("rm_x", 1.0, 5.0), [18.0] * 80)["verdict"]
                  == "UNMEASURED")
        finally:
            urllib.request.urlopen, shutil.which, subprocess.run, store.IS_WIN = saved
        # ---------------------------------------------------------------- regression detector + sanity probe
        import random
        rnd = random.Random(7)
        quiet = [18 + rnd.gauss(0, 1.5) for _ in range(80)]
        quiet2 = [18 + rnd.gauss(0, 1.5) for _ in range(80)]
        rot = [93.6 + rnd.gauss(0, 5) for _ in range(80)]   # the Rot-map regression's scale (huge_footprints_perf.md)
        check("sanity probe: known non-regression reads NO_SHIFT", analysis.compare_windows(quiet, quiet2)["verdict"] == "NO_SHIFT")
        check("sanity probe: Rot-map-sized slowdown reads REGRESSION", analysis.compare_windows(quiet, rot)["verdict"] == "REGRESSION")
        check("too few windows reads UNMEASURED, never clean", analysis.compare_windows(quiet[:10], rot)["verdict"] == "UNMEASURED")
        try:   # `telemetry around --metric rm_game_ratio`: a ratio that FELL is the slowdown
            v_ratio = analysis.compare_windows(rot, quiet, metric="rm_game_ratio")["verdict"]
            v_tick = analysis.compare_windows(quiet, rot, metric="rm_game_tick_ms")["verdict"]
        except TypeError as e:
            v_ratio = v_tick = f"TypeError: {e}"
        check("[around] a falling speed ratio reads REGRESSION; a rising tick time still does",
              v_ratio == "REGRESSION" and v_tick == "REGRESSION", (v_ratio, v_tick))
        # proof flips
        pdir = os.path.join(c["mirror"], "src", "RimMandrake", "FlowWorks", "northstar")
        os.makedirs(pdir)
        for i, st in enumerate(("PASS", "FAIL")):
            with open(os.path.join(pdir, f"proof_2026101{i}T000000.json"), "w") as f:
                json.dump({"script": "proof_hose.py", "rows": [{"id": "R1", "status": st}, {"id": "R2", "status": "PASS"}]}, f)
        check("proof results ingested", ingest.ingest_proofs(con) == 2)
        p0 = os.path.join(pdir, "proof_20261010T000000.json")
        mt0 = os.path.getmtime(p0)
        with open(p0, "w") as f:
            json.dump({"script": "proof_hose.py", "rows": [{"id": "R1", "status": "FAIL"}]}, f)
        os.utime(p0, (mt0 + 0.5, mt0 + 0.5))
        check("[proof] a rewrite under a second later is re-ingested", ingest.ingest_proofs(con) == 1
              and con.execute("SELECT n_fail FROM proof_runs WHERE id LIKE '%20261010%'").fetchone()[0] == 1)
        os.utime(p0, (mt0 + 2, mt0 + 2))

        def no_open(*a, **k):
            raise PermissionError(13, "locked")
        ingest.open = no_open
        try:
            r_locked = ingest.ingest_proofs(con)
        finally:
            del ingest.open
        check("[proof] an unreadable proof is not checkpointed: the next pass reads it",
              r_locked == 0 and ingest.ingest_proofs(con) == 1, r_locked)
        with open(p0, "w") as f:
            json.dump({"script": "proof_hose.py", "aborted": True, "rows": []}, f)
        os.utime(p0, (mt0 + 3, mt0 + 3))
        ingest.ingest_proofs(con)
        check("[proof] an empty replacement removes the old verdict instead of leaving it standing",
              not con.execute("SELECT 1 FROM proof_runs WHERE id LIKE '%20261010%'").fetchone()
              and not con.execute("SELECT 1 FROM proof_rows WHERE run_id LIKE '%20261010%'").fetchone())

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
        again = os.path.join(c["raw"], "tps", "2026-01-01.jsonl.gz")
        with gzip.open(again, "wb") as f:
            f.write(b"y\n")
        os.utime(again, (now - 100 * 86400, now - 100 * 86400))
        analysis.retention(con, now)
        ad = os.path.join(c["archive"], "raw", "tps")
        check("[retention] a day archived twice keeps both parts (no overwrite)", sorted(os.listdir(ad))
              == ["2026-01-01.jsonl.gz", "2026-01-01~1.jsonl.gz"], os.listdir(ad))
        third = os.path.join(c["raw"], "tps", "2026-01-02.jsonl.gz")
        with gzip.open(third, "wb") as f:
            f.write(b"z\n")
        os.utime(third, (now - 100 * 86400, now - 100 * 86400))
        real_move = analysis.shutil.move

        def full_disk(*a, **k):
            raise OSError(28, "No space left on device")
        analysis.shutil.move = full_disk
        try:
            rep_f = analysis.retention(con, now)
        finally:
            analysis.shutil.move = real_move
        check("[retention] a full archive disk is reported, keeps the hot file, and the pass still prunes rows",
              "error" in rep_f and rep_f["moved"] == 0 and os.path.exists(third) and "bridge_rows" in rep_f, rep_f)

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
    check("[heartbeat] live: telemetryd heartbeat < 3 min", 0 <= time.time() - hb["at"] < 180, hb)
    al = json.load(open(os.path.join(st, "alerts.json")))
    check("live: alerts file < 3 min", 0 <= time.time() - al["at"] < 180, al.get("at"))
    code = ("import urllib.request as u\n"
            "for x in ('http://127.0.0.1:8428/health','http://127.0.0.1:3000/api/health'):\n"
            "  print(u.urlopen(x,timeout=5).status)")
    r = subprocess.run(["python.exe", "-c", code], capture_output=True, text=True, timeout=60)
    check("live: VictoriaMetrics and Grafana answer HTTP 200", r.stdout.split() == ["200", "200"], r.stdout + r.stderr)
    # a console a plugin child opens is owned by its conhost.exe (child of the console client), not by gpx_*
    ps = ("$re = 'grafana|gpx_|victoria-metrics'; "
          "$ids = @(Get-CimInstance Win32_Process | Where-Object { $_.Name -match $re } | ForEach-Object { $_.ProcessId }); "
          "$con = @(Get-CimInstance Win32_Process -Filter \"Name='conhost.exe'\" | "
          "Where-Object { $ids -contains $_.ParentProcessId } | ForEach-Object { [int]$_.ProcessId }); "
          "@(Get-Process | Where-Object { ($_.ProcessName -match $re -or $con -contains $_.Id) "
          "-and $_.MainWindowHandle -ne 0 }).Count")
    r = subprocess.run(["powershell.exe", "-NoProfile", "-Command", ps], capture_output=True, text=True, timeout=60)
    check("[windows] live: no telemetry process owns a visible window", r.stdout.strip() == "0", r.stdout + r.stderr)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
