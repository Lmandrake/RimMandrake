"""Cursor-tail every raw JSONL source into the two stores, and copy the raw bytes to E:.

Design §5: per-producer JSONL is the record of truth; telemetryd tails each by cursor, keeps a
gzipped raw copy (bridge_calls otherwise keeps ~10 h, design §1.2), writes numeric series to
VictoriaMetrics and rows to SQLite. Sources are a registry (SOURCES) so `telemetry health` and
the skill's sources reference are generated from the same list and cannot drift.

Cursor identity is the file id (st_ino; NTFS file index on Windows), so a rename-rotation
(bridge_calls.jsonl -> .1) is followed, not re-read. A file that shrank under its cursor is
re-read from 0 and counted in `resets`. Only complete lines ("\\n"-terminated) are consumed.
"""
from __future__ import annotations

import glob
import gzip
import json
import os
import re
import time

import store
from tcommon import bridge_failed, cfg, loads, parse_ts, utc_day

MAX_READ = 8 << 20          # per file per pass; a backlog drains over several passes
RAW_FLUSH_S = 60.0
RAW_FLUSH_BYTES = 1 << 20


# ================================================================== emit context

class Emit:
    """What a parser writes into: VM points, SQLite rows, and the live `latest` view."""

    def __init__(self, con, vm: store.VMSink, latest: dict):
        self.con, self.vm, self.latest = con, vm, latest
        self.rows = 0
        self.events = 0

    def point(self, name, labels, v, ts):
        self.vm.add(name, labels, v, ts)

    def event(self, ts, kind, subject=None, detail=None, src=None, src_ref=None, **kw):
        if store.add_event(self.con, ts, kind, subject, detail, src, src_ref, **kw):
            self.events += 1


# ================================================================== parsers

def _num(v):
    return v if isinstance(v, (int, float)) and not isinstance(v, bool) else None


SAMPLE_FIELDS = {  # TPS `sample` field -> series (emitted only when the window ticked, see below)
    "tps": "rm_game_tps", "tpsWall": "rm_game_tps_wall", "ratio": "rm_game_ratio",
    "tickMs": "rm_game_tick_ms", "simMs": "rm_game_sim_ms", "simMaxMs": "rm_game_sim_max_ms",
    "target": "rm_game_tps_target",
}
SAMPLE_ALWAYS = {
    "fps": "rm_game_fps", "gapMaxMs": "rm_game_gap_max_ms", "heapMB": "rm_game_heap_mb",
    "gc": "rm_game_gc_gen0", "mult": "rm_game_mult", "pausedFrac": "rm_game_paused_frac",
    "stallS": "rm_game_stall_s", "frames": "rm_game_frames", "dReal": "rm_game_window_s",
    "wq": "rm_game_writer_queue", "wdrop": "rm_game_writer_drop", "wdropCrit": "rm_game_writer_drop_crit",
    "werr": "rm_game_writer_err", "profEstMs": "rm_game_prof_est_ms",
}
TPS_EVENT_KINDS = {"incident", "silence", "resumed", "session", "game", "menu", "save", "marker", "log",
                   "shutdown", "shutdown-complete", "error", "awareness", "dropped", "flight", "tier"}


HIST_R = 16000 ** (1 / 26)


def hist_le(bucket: int, histv=1) -> str:
    """Upper edge in ms of a JawaBench tick-histogram bucket (histV 1: 28 buckets; 0 = under 0.25 ms,
    i = [0.25*R^(i-1), 0.25*R^i) for 1..26 with R = 16000^(1/26), 27 = 4 s and over)."""
    if histv != 1:
        return f"v{histv}:{bucket}"
    if bucket >= 27:
        return "+Inf"
    return f"{0.25 * HIST_R ** bucket:.3g}"


def parse_tps(r: dict, E: Emit, ref: str) -> None:
    ts = parse_ts(r.get("utc"))
    if ts is None:
        return
    k = r.get("kind")
    sess = (r.get("session") or "")[:8]
    if k == "session":
        # owner 2026-10-11: every stream is recorded relative to the mods loaded (modDigest) and their
        # version (the companion build). Kept per session in kv so a restart mid-session still tags.
        # modDigest = the loaded set (A); modOrderDigest = order + each mod's version (B); build = companion
        store.kv_set(E.con, "sess:" + sess, {"mods": r.get("modDigest"), "modver": r.get("modOrderDigest"),
                                             "build": r.get("build"), "nmods": r.get("mods")})
    ms = E.latest.setdefault("sessmods", {})
    if sess not in ms:
        ms[sess] = store.kv_get(E.con, "sess:" + sess, {}) or {}
    modlab = {"mods": ms[sess].get("mods"), "modver": ms[sess].get("modver"), "build": ms[sess].get("build")}
    if k == "sample":
        tier = r.get("tier") or "campaign"
        lab = {"tier": tier, "session": sess, **modlab}
        ticked = (r.get("dTicks") or 0) > 0
        # a window that ended paused reads mult 0; its speed is multMax. tickMs 0 = engine had no mean.
        mlab = {**lab, "mult": r.get("mult") or r.get("multMax")}
        for f, n in SAMPLE_FIELDS.items():
            v = _num(r.get(f))
            if ticked and v is not None and not (f == "tickMs" and v == 0):
                E.point(n, mlab, v, ts)
        for f, n in SAMPLE_ALWAYS.items():
            if _num(r.get(f)) is not None:
                E.point(n, lab, r[f], ts)
        E.point("rm_game_running", lab, 1 if r.get("state") == "run" else 0, ts)
        if ticked:
            for stage, v in (r.get("attr") or {}).items():
                if isinstance(v, list) and len(v) >= 3 and v[0]:
                    E.point("rm_game_stage_ms", {**lab, "stage": stage}, v[1] / v[0], ts)
                    E.point("rm_game_stage_max_ms", {**lab, "stage": stage}, v[2], ts)
            worst = [w.get("ms") for w in (r.get("worst") or []) if _num(w.get("ms")) is not None]
            if worst:
                E.point("rm_game_worst_tick_ms", lab, max(worst), ts)
        # P2 test-tier fields (JawaBench companion, design §3.2)
        h = r.get("hist")  # [[bucket, count], ...] sparse; bucket edges per histV (hist_le)
        if isinstance(h, list):
            for pair in h:
                if isinstance(pair, list) and len(pair) == 2:
                    E.point("rm_game_tick_hist", {**lab, "le": hist_le(int(pair[0]), r.get("histV", 1))}, pair[1], ts)
        exc = r.get("exc")
        if isinstance(exc, dict):
            E.point("rm_game_exc", lab, exc.get("n"), ts)
            E.point("rm_game_exc_suppressed", lab, exc.get("sup"), ts)
            for lv in ("e", "w", "m", "rep", "over"):
                if lv in exc:
                    E.point("rm_game_exc_by_level", {**lab, "level": lv}, exc[lv], ts)
            for sig_n in exc.get("top") or []:
                if isinstance(sig_n, list) and len(sig_n) >= 2:
                    E.con.execute(
                        "INSERT INTO exc_sigs(session,sig,first_ts,last_ts,n,sup,sample) VALUES(?,?,?,?,?,0,NULL) "
                        "ON CONFLICT(session,sig) DO UPDATE SET n=n+excluded.n, last_ts=excluded.last_ts",
                        (r.get("session"), str(sig_n[0])[:300], ts, ts, int(sig_n[1])))
        br = r.get("br")
        if isinstance(br, dict):
            E.point("rm_game_bridge_calls", lab, br.get("calls"), ts)
            E.point("rm_game_bridge_main_ms", lab, br.get("mainMs"), ts)
            E.point("rm_game_bridge_qmax_ms", lab, br.get("qMaxMs"), ts)
        E.latest["tps"] = {"ts": ts, "ratio": r.get("ratio"), "state": r.get("state"), "tier": tier,
                           "tps": r.get("tps"), "mult": r.get("mult"), "exc": (exc or {}).get("n"),
                           "dReal": r.get("dReal"), "session": r.get("session")}
        busy = ((br or {}).get("mainMs") or 0) / max((r.get("dReal") or 1) * 1000, 1)
        E.latest.setdefault("tps_hist", []).append((ts, r.get("ratio"), r.get("state"), r.get("mult"), busy))
        E.latest["tps_hist"] = E.latest["tps_hist"][-200:]
        return
    if k == "context":
        lab = {"session": sess, **modlab}
        for m in r.get("maps") or []:
            ml = {**lab, "map": str(m.get("id")), "biome": m.get("biome")}
            E.point("rm_game_pawns", ml, m.get("pawns"), ts)
            E.point("rm_game_things", ml, m.get("things"), ts)
        E.point("rm_game_maps", lab, r.get("mapCount"), ts)
        E.point("rm_game_world_pawns", lab, r.get("worldPawns"), ts)
        ws = _num(r.get("workingSetMB"))
        if ws:  # 0 means "not read", not zero memory
            E.point("rm_game_working_set_mb", lab, ws, ts)
        return
    if k == "mapcomp":
        E.con.execute("INSERT OR IGNORE INTO mapcomp(ts,session,type,mod,ms_per_tick,calls,max_ms,ticks,src_ref) "
                      "VALUES(?,?,?,?,?,?,?,?,?)",
                      (ts, r.get("session"), r.get("type"), r.get("mod"), r.get("msPerTick"), r.get("calls"),
                       r.get("maxMs"), r.get("ticks"), ref))
        E.event(ts, "mapcomp", r.get("type"), r, "tps", ref)
        return
    if k == "flight":
        fid = f"{r.get('session')}:{r.get('seq')}"
        E.con.execute("INSERT OR IGNORE INTO flight(id,ts,session,file,trigger,tick_from,tick_to,worst_us,detail) "
                      "VALUES(?,?,?,?,?,?,?,?,?)",
                      (fid, ts, r.get("session"), r.get("file"), r.get("trigger"), r.get("tickFrom"),
                       r.get("tickTo"), r.get("worstDurUs"), json.dumps(r)))
    if k:
        subject = r.get("why") or r.get("type") or r.get("save") or r.get("trigger") or sess
        if k == "incident":
            E.point("rm_game_incident_gap_s", {"session": sess, "type": r.get("type")}, r.get("gapS"), ts)
            E.latest.setdefault("incidents", []).append({"ts": ts, "gapS": r.get("gapS"), "type": r.get("type")})
            E.latest["incidents"] = E.latest["incidents"][-50:]
        if k == "marker" and str(r.get("why", "")).startswith("tier"):
            E.latest["tier_marker"] = {"ts": ts, "why": r.get("why")}
        E.event(ts, k if k != "game" else "game_loaded", str(subject)[:200] if subject else None,
                r, "tps", ref)


def parse_health(r: dict, E: Emit, ref: str) -> None:
    ts = parse_ts(r.get("utc"))
    if ts is None:
        return
    if r.get("kind") != "sample":
        E.event(ts, "health_" + str(r.get("kind")), (r.get("collector") or {}).get("id"),
                {k: v for k, v in r.items() if k != "sources"}, "health", ref)
        return
    src = r.get("sources") or {}

    def val(name):
        s = src.get(name) or {}
        return s.get("value") if s.get("status") == "ok" else None

    for p in (val("game.cpu") or {}).get("procs", []):
        E.point("rm_proc_cpu_cores", {"pid": p.get("pid")}, p.get("cores"), ts)
    for p in (val("game.mainthread") or {}).get("procs", []):
        E.point("rm_proc_mainthread_cores", {"pid": p.get("pid")}, p.get("cores"), ts)
        E.point("rm_proc_otherthreads_cores", {"pid": p.get("pid")}, p.get("otherThreadsCores"), ts)
    for p in (val("game.memory") or {}).get("procs", []):
        E.point("rm_proc_working_set_mb", {"pid": p.get("pid")}, p.get("workingSetMB"), ts)
        E.point("rm_proc_private_mb", {"pid": p.get("pid")}, p.get("privateMB"), ts)
    sm = val("sys.memory") or {}
    for f in ("availPhysMB", "memoryLoadPct", "commitTotalMB", "commitLimitMB", "commitHeadroomMB"):
        E.point("rm_obs_sys_" + re.sub(r"(?<!^)([A-Z])", r"_\1", f).lower(), {}, sm.get(f), ts)
    lg = val("log.growth") or {}
    E.point("rm_log_bytes_per_s", {}, lg.get("bytesPerS"), ts)
    E.point("rm_log_size_bytes", {}, lg.get("size"), ts)
    ms = val("log.milestones") or {}
    for m in ms.get("new") or []:
        E.event(ts, "log_milestone", m, None, "health", f"{ref}:{m}")
    hb = val("obs.heartbeat") or {}
    E.point("rm_obs_sample_ms", {}, hb.get("sampleMs"), ts)


_BRIDGE_OPEN: dict = {}   # (bucket_ts, tool) -> [count, ms_sum, ms_max, errors]
BRIDGE_BUCKET = 10


def _succ(v):
    """success flag -> 1/0, or None (NULL) when the client never knew (non-dict result). None is not failure."""
    return None if v is None else (1 if v else 0)


def parse_bridge(r: dict, E: Emit, ref: str) -> None:
    ts = parse_ts(r.get("t"))
    cid = r.get("cid")
    if ts is None or not cid:
        return
    ev = r.get("ev")
    if ev == "start":
        E.con.execute("INSERT OR IGNORE INTO bridge_calls(cid,ts,tool,mutating,script,seat,run,client) "
                      "VALUES(?,?,?,?,?,?,?,?)",
                      (cid, ts, r.get("tool"), 1 if r.get("mutating") else 0, r.get("script"), r.get("seat"),
                       r.get("run"), r.get("client")))
    elif ev == "end":
        E.con.execute("UPDATE bridge_calls SET ts_end=?, ms=?, status=?, success=? WHERE cid=?",
                      (ts, r.get("ms"), r.get("status"), _succ(r.get("success")), cid))
        row = E.con.execute("SELECT tool FROM bridge_calls WHERE cid=?", (cid,)).fetchone()
        tool = row[0] if row else "?"
        b = (int(ts // BRIDGE_BUCKET) * BRIDGE_BUCKET, tool)
        a = _BRIDGE_OPEN.setdefault(b, [0, 0.0, 0.0, 0])
        ms = _num(r.get("ms")) or 0.0
        a[0] += 1
        a[1] += ms
        a[2] = max(a[2], ms)
        a[3] += 1 if bridge_failed(_succ(r.get("success")), r.get("status")) else 0
        E.latest["bridge_last"] = ts
    elif ev == "reconciled":
        E.con.execute("UPDATE bridge_calls SET status=? WHERE cid=?", (f"reconciled:{r.get('as')}", cid))


def flush_bridge_buckets(E: Emit, force: bool = False) -> None:
    """Emit closed 10 s buckets once; an open bucket waits (one point per series per timestamp)."""
    horizon = (E.latest.get("bridge_last") or 0) - 2 * BRIDGE_BUCKET
    for (bts, tool) in sorted(list(_BRIDGE_OPEN)):
        if not force and bts > horizon:
            continue
        c, s, mx, err = _BRIDGE_OPEN.pop((bts, tool))
        lab = {"tool": tool}
        E.point("rm_bridge_calls", lab, c, bts)
        E.point("rm_bridge_ms_sum", lab, s, bts)
        E.point("rm_bridge_ms_max", lab, mx, bts)
        if err:
            E.point("rm_bridge_errors", lab, err, bts)


def parse_artpipe(r: dict, E: Emit, ref: str) -> None:
    ts = parse_ts(r.get("ts"))
    if ts is None:
        return
    if "elapsed_s" in r:
        lab = {"channel": r.get("channel"), "status": r.get("status")}
        E.point("rm_art_elapsed_s", lab, r.get("elapsed_s"), ts)
        E.point("rm_art_cost_usd", lab, r.get("cost_usd"), ts)
        E.event(ts, "art_job", r.get("id"), {k: r.get(k) for k in ("channel", "model", "status", "elapsed_s",
                                                                     "cost_usd", "daemon_attempts")}, "artpipe", ref)
    else:
        E.event(ts, "art_" + str(r.get("event") or "registry"), r.get("job_id") or r.get("target"),
                {k: r.get(k) for k in ("event", "job_id", "target", "verdict")}, "artpipe", ref)


CHANGE_KINDS = {"deploy", "build", "modlist", "proof_run", "proof_start", "proof_end", "marker", "canary"}


def parse_change(r: dict, E: Emit, ref: str) -> None:
    ts = parse_ts(r.get("ts"))
    if ts is None:
        return
    kind = str(r.get("kind") or "marker")
    E.event(ts, kind, r.get("subject"), r.get("detail") if "detail" in r else r, "changes", ref,
            ts_end=parse_ts(r.get("ts_end")), seat=r.get("seat"), sha=r.get("sha"))
    if kind in ("proof_end", "proof_run") and (r.get("detail") or {}).get("result"):
        E.latest.setdefault("proof_paths", []).append((r["detail"]["result"], ts))


_CG_SCOPE = re.compile(r"claude-seat-([A-Z]+)-\d+\.scope")


def parse_wsl(r: dict, E: Emit, ref: str) -> None:
    src = r.get("src")
    ts = parse_ts(r.get("ts")) or parse_ts(r.get("at"))
    if ts is None:
        return
    if src == "memwatch_sample":
        for name, cg in (r.get("cgroups") or {}).items():
            short = _CG_SCOPE.sub(lambda m: f"seat-{m.group(1)}", name)
            lab = {"cg": short}
            E.point("rm_cg_mem_bytes", lab, cg.get("current"), ts)
            E.point("rm_cg_swap_bytes", lab, cg.get("swap"), ts)
            E.point("rm_cg_shmem_bytes", lab, (cg.get("stat") or {}).get("shmem"), ts)
            E.point("rm_cg_psi_some", lab, (cg.get("psi") or {}).get("some_avg10"), ts)
            E.point("rm_cg_oom_kills", lab, (cg.get("events") or {}).get("oom_kill"), ts)
    elif src == "memwatch_event":
        E.event(ts, "oom" if "oom" in str(r.get("kind")) else "memwatch_" + str(r.get("kind")),
                r.get("cgroup"), {k: r.get(k) for k in ("kind", "seat", "delta", "total")}, "memwatch", ref)
    elif src == "objstore":
        E.point("rm_objstore_bytes", {}, r.get("store_bytes") or r.get("store_hardlinked_bytes"), ts)
        E.point("rm_wsl_disk_free_bytes", {"via": "objstore"}, r.get("disk_free_bytes"), ts)
    elif src == "wsl_host":
        for f in ("mem_total", "mem_avail", "swap_used", "disk_used", "disk_free", "disk_total"):
            E.point(f"rm_wsl_{f}_bytes", {}, r.get(f), ts)
        E.point("rm_wsl_load1", {}, r.get("load1"), ts)
        E.latest["wsl_host"] = {"ts": ts, **{k: r.get(k) for k in ("disk_used", "mem_avail", "mem_total")}}
    elif src == "pulse":
        m = r.get("m")
        if m in ("toast",):
            return
        E.event(ts, "pulse_" + str(m), r.get("id") or r.get("key"), r, "pulse", ref)
    elif src == "ledger":
        ev = r.get("event")
        kind = {"bridge": "bridge_hold", "game": "game_state"}.get(ev, "ledger")
        subj = r.get("id") or r.get("state")
        E.event(ts, kind, subj, {k: r.get(k) for k in ("event", "id", "state", "purpose", "seat", "sha",
                                                       "title", "reason", "ranBy") if r.get(k) is not None},
                "ledger", "ledger:" + str(r.get("_h")), seat=r.get("seat"), sha=r.get("sha"))
    elif src == "selftests":
        res = r.get("counts") or {}
        for st, n in res.items():
            E.point("rm_selftests", {"state": st}, n, ts)
        E.point("rm_selftests_wall_s", {}, r.get("wall"), ts)
        E.event(ts, "selftest_run", None, r, "selftests", ref)


# ================================================================== sources

class Source:
    def __init__(self, name, pattern_fn, parser, fast=False, archive=True, desc="", rate="", producer=""):
        self.name, self.pattern_fn, self.parser = name, pattern_fn, parser
        self.fast, self.archive, self.desc, self.rate, self.producer = fast, archive, desc, rate, producer

    def files(self) -> list[str]:
        out = []
        for p in self.pattern_fn():
            out.extend(glob.glob(p))
        return sorted(set(out), key=lambda p: (os.path.getmtime(p) if os.path.exists(p) else 0, p))


def _j(*a):
    return os.path.join(*a)


def make_sources() -> list[Source]:
    c = cfg()
    jb = c["jawabench"]
    return [
        Source("tps", lambda: [_j(jb, "tps", "tps_*.jsonl")], parse_tps, fast=True,
               desc="JawaBench TPS record: sample windows (5 s; 1 s test tier), context, incidents, flight refs",
               rate="5 s / 1 s armed", producer="JawaBenchTpsWriter.cs"),
        Source("health", lambda: [_j(jb, "health", "observer_*.jsonl")], parse_health,
               desc="health_observer.py: game CPU/main thread/memory, sys memory, log growth",
               rate="5 s game up, 30 s idle", producer="health_observer.py"),
        Source("bridge", lambda: [c["bridge_calls"], c["bridge_calls"] + ".1"], parse_bridge, fast=True,
               desc="rimbridge_client per-call evidence; per-call rows -> SQLite, 10 s aggregates -> VM",
               rate="per bridge call", producer="rimbridge_client.py _evidence"),
        Source("artpipe", lambda: [_j(c["artpipe"], "throughput.jsonl"), _j(c["artpipe"], "registry.jsonl")],
               parse_artpipe, desc="artpipe job throughput and registry verdicts", rate="per job",
               producer="artpipe/common.py, artreg.py"),
        Source("changes", lambda: [_j(c["inbox"], "changes", "*.jsonl")], parse_change,
               desc="deploy / build / modlist / proof_run events written by the tools themselves",
               rate="per action", producer="telemetry_emit.emit_change"),
        Source("wsl", lambda: [_j(c["inbox"], "wsl", "*.jsonl")], parse_wsl,
               desc="WSL-side exporter: memwatch, objstore, ledger, pulse metrics, selftests, WSL host",
               rate="1 min", producer="wsl_export.py (rm-telemetry-export.timer)"),
    ]


# ================================================================== tailing

class Tailer:
    def __init__(self, con, vm, latest):
        self.con, self.vm, self.latest = con, vm, latest
        self.raw_buf: dict[str, list[bytes]] = {}
        self.raw_bytes: dict[str, int] = {}
        self.raw_last_flush = time.time()
        self.stats: dict[str, dict] = {}

    def _file_key(self, st, path) -> str:
        ino = getattr(st, "st_ino", 0)
        return f"ino:{ino}" if ino else f"path:{path}"

    def pass_source(self, src: Source) -> int:
        E = Emit(self.con, self.vm, self.latest)
        n = 0
        stt = self.stats.setdefault(src.name, {"rows": 0, "bad": 0, "resets": 0, "files": 0, "last_row_ts": None,
                                               "last_pass": None, "error": None})
        try:
            files = src.files()
        except OSError as e:
            stt["error"] = str(e)
            return 0
        stt["files"] = len(files)
        for path in files:
            try:
                st = os.stat(path)
            except OSError:
                continue
            key = self._file_key(st, path)
            cur = self.con.execute("SELECT offset,size FROM cursors WHERE src=? AND key=?", (src.name, key)).fetchone()
            off = cur["offset"] if cur else 0
            if st.st_size < off:
                stt["resets"] += 1
                off = 0
            if st.st_size == off:
                continue
            try:
                with open(path, "rb") as f:
                    f.seek(off)
                    chunk = f.read(min(MAX_READ, st.st_size - off))
            except OSError as e:
                stt["error"] = str(e)
                continue
            end = chunk.rfind(b"\n")
            if end < 0:
                continue
            chunk = chunk[:end + 1]
            base = os.path.basename(path)
            pos = off
            for line in chunk.split(b"\n")[:-1]:
                ref = f"{src.name}:{base}:{pos}"
                pos += len(line) + 1
                if not line.strip():
                    continue
                r = loads(line)
                if not isinstance(r, dict):
                    stt["bad"] += 1
                    continue
                try:
                    src.parser(r, E, ref)
                except Exception as e:  # noqa: BLE001 — one bad row never stops a source
                    stt["bad"] += 1
                    stt["error"] = f"{type(e).__name__}: {e}"
                    continue
                n += 1
                t = parse_ts(r.get("utc") or r.get("t") or r.get("ts"))
                if t:
                    stt["last_row_ts"] = max(stt["last_row_ts"] or 0, t)
            if src.archive:
                self.raw_buf.setdefault(src.name, []).append(chunk)
                self.raw_bytes[src.name] = self.raw_bytes.get(src.name, 0) + len(chunk)
            self.con.execute("INSERT OR REPLACE INTO cursors(src,key,ino,offset,size,mtime) VALUES(?,?,?,?,?,?)",
                             (src.name, key, path, off + len(chunk), st.st_size, st.st_mtime))
        if src.name == "bridge":
            flush_bridge_buckets(E)
        stt["rows"] += n
        stt["last_pass"] = time.time()
        if n or E.events:
            self.con.commit()
        return n

    def flush_raw(self, force=False) -> None:
        if not self.raw_buf:
            return
        if not force and time.time() - self.raw_last_flush < RAW_FLUSH_S and \
                sum(self.raw_bytes.values()) < RAW_FLUSH_BYTES:
            return
        day = utc_day(time.time())
        for name, chunks in self.raw_buf.items():
            d = os.path.join(cfg()["raw"], name)
            os.makedirs(d, exist_ok=True)
            with gzip.open(os.path.join(d, f"{day}.jsonl.gz"), "ab") as g:   # one gzip member per flush
                for ch in chunks:
                    g.write(ch)
        self.raw_buf.clear()
        self.raw_bytes.clear()
        self.raw_last_flush = time.time()


def copy_side_files(con) -> int:
    """Flight dumps and first-sight exception files (P2) are capped and rotated in-game; keep a copy."""
    jb = cfg()["jawabench"]
    n = 0
    for sub, pat in (("flight", "flight_*.jsonl.gz"), ("exc", "exc_*.jsonl")):
        dst = os.path.join(cfg()["raw"], sub)
        for p in glob.glob(os.path.join(jb, "tps", sub, pat)):
            q = os.path.join(dst, os.path.basename(p))
            try:
                st = os.stat(p)
                if os.path.exists(q) and os.path.getsize(q) == st.st_size:
                    continue
                if sub == "flight" and time.time() - st.st_mtime < 5:
                    continue   # still being written
                os.makedirs(dst, exist_ok=True)
                with open(p, "rb") as a, open(q, "wb") as b:
                    b.write(a.read())
                n += 1
            except OSError:
                continue
        if sub == "exc":
            ingest_exc_files(con, dst)
    return n


def ingest_exc_files(con, d: str) -> None:
    for p in glob.glob(os.path.join(d, "exc_*.jsonl")):
        key = os.path.basename(p)
        cur = con.execute("SELECT offset FROM cursors WHERE src='exc' AND key=?", (key,)).fetchone()
        off = cur[0] if cur else 0
        with open(p, "rb") as f:
            f.seek(off)
            data = f.read()
        end = data.rfind(b"\n")
        if end < 0:
            continue
        for line in data[:end + 1].split(b"\n")[:-1]:
            r = loads(line)
            if not isinstance(r, dict):
                continue
            ts = parse_ts(r.get("utc")) or time.time()
            con.execute("INSERT INTO exc_sigs(session,sig,first_ts,last_ts,n,sup,sample) VALUES(?,?,?,?,0,0,?) "
                        "ON CONFLICT(session,sig) DO UPDATE SET sample=COALESCE(sample,excluded.sample)",
                        (r.get("session"), str(r.get("sig"))[:300], ts, ts,
                         json.dumps({k: r.get(k) for k in ("msg", "stack", "level", "asm") if r.get(k)})[:4096]))
        con.execute("INSERT OR REPLACE INTO cursors(src,key,ino,offset,size,mtime) VALUES('exc',?,?,?,0,0)",
                    (key, p, off + end + 1))
    con.commit()


# ================================================================== proof runs

def ingest_proofs(con, root: str | None = None) -> int:
    """Committed proof results (src/RimMandrake/*/northstar/*.json) -> proof_runs/proof_rows.
    Read from the mirror (origin/main); keyed by path + mtime so a rewrite re-ingests."""
    root = root or cfg()["mirror"]
    n = 0
    for p in glob.glob(os.path.join(root, "src", "RimMandrake", "*", "northstar", "*.json")):
        try:
            mt = os.path.getmtime(p)
        except OSError:
            continue
        rel = os.path.relpath(p, root).replace("\\", "/")
        cur = con.execute("SELECT mtime FROM cursors WHERE src='proof' AND key=?", (rel,)).fetchone()
        if cur and abs(cur[0] - mt) < 1:
            continue
        n += ingest_proof_file(con, p, rel, mt)
        con.execute("INSERT OR REPLACE INTO cursors(src,key,ino,offset,size,mtime) VALUES('proof',?,?,0,0,?)",
                    (rel, p, mt))
    con.commit()
    return n


def proof_rows_of(d: dict) -> list[tuple[str, str, str, str]]:
    rows = []
    for r in d.get("rows") or []:
        if isinstance(r, dict) and r.get("id"):
            det = r.get("detail")
            rows.append((str(r["id"]), str(r.get("status")), str(r.get("class") or r.get("cls") or ""),
                         json.dumps(det)[:2000] if not isinstance(det, str) else det[:2000]))
    for ch in d.get("chains") or []:
        if not isinstance(ch, dict):
            continue
        for comp in ch.get("components") or []:
            if isinstance(comp, dict) and comp.get("name"):
                rows.append((f"{ch.get('name')}/{comp['name']}", str(comp.get("verdict")), "chain",
                             str(comp.get("detail") or "")[:2000]))
    return rows


def ingest_proof_file(con, p: str, rel: str, mt: float) -> int:
    try:
        with open(p, encoding="utf-8") as f:
            d = json.load(f)
    except (OSError, ValueError):
        return 0
    if not isinstance(d, dict):
        return 0
    rows = proof_rows_of(d)
    if not rows:
        return 0
    m = re.search(r"(\d{8}T\d{6})", rel)
    ts = parse_ts(d.get("started")) or (parse_ts(m.group(1)[:4] + "-" + m.group(1)[4:6] + "-" + m.group(1)[6:8] + "T"
                                                 + m.group(1)[9:11] + ":" + m.group(1)[11:13] + ":" + m.group(1)[13:15])
                                        if m else None) or mt
    st = [r[1].upper() for r in rows]
    npass = sum(1 for s in st if s == "PASS")
    nfail = sum(1 for s in st if s == "FAIL")
    mod = rel.split("/")[2] if rel.count("/") >= 3 else None
    con.execute("INSERT OR REPLACE INTO proof_runs(id,ts,path,mod,script,wall_s,mod_hash,n_pass,n_fail,n_other,"
                "n_total,all_green,detail) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?)",
                (rel, ts, p, mod, d.get("script"), d.get("wall_s"), d.get("mod_hash"), npass, nfail,
                 len(st) - npass - nfail, len(st), 1 if d.get("all_green") or d.get("green") else 0,
                 json.dumps({k: d.get(k) for k in ("mode", "save", "refused", "aborted") if d.get(k)})))
    con.execute("DELETE FROM proof_rows WHERE run_id=?", (rel,))
    con.executemany("INSERT OR REPLACE INTO proof_rows(run_id,row_id,status,class,detail) VALUES(?,?,?,?,?)",
                    [(rel, *r) for r in rows])
    store.add_event(con, ts, "proof_run", mod, {"path": rel, "pass": npass, "fail": nfail, "total": len(st)},
                    "proof", "proof:" + rel + f":{int(mt)}")
    return 1
