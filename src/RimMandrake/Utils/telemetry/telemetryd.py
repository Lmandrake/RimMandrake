"""telemetryd — the one ingest daemon (design §5). Windows-side, started and kept alive by supervise.py.

Loop (1 s tick):
  * sources marked fast (TPS record, bridge calls) every 1 s while the in-game test tier is armed,
    every 15 s otherwise; all others every 15 s
  * host sampler every 60 s (volumes, VHDX, memory/commit) — the owner's 1/min for external metrics
  * deploy/mod-list detector every 10 min; directory sizes hourly; proof results hourly
  * alert rules + sparklines every 15 s -> <state>/alerts.json (read by RimPulse)
  * retention daily (no per-deploy detectors: comparison is on demand, owner 2026-10-11)
  * heartbeat -> <state>/heartbeat.json every pass (rm-telemetry-health.timer watches it from WSL)

`--once` runs every stage once and exits (the selftest and `telemetry rebuild` use it).
"""
from __future__ import annotations

import argparse
import hashlib
import os
import sys
import time
import traceback

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import analysis  # noqa: E402
import host  # noqa: E402
import ingest  # noqa: E402
import store  # noqa: E402
from tcommon import CODE_DIR, cfg, now, write_json_atomic  # noqa: E402


def code_hash() -> str:
    h = hashlib.sha256()
    for f in sorted(os.listdir(CODE_DIR)):
        if f.endswith(".py"):
            with open(os.path.join(CODE_DIR, f), "rb") as fh:
                h.update(f.encode() + fh.read())
    return h.hexdigest()[:12]


class Daemon:
    def __init__(self, vm: store.VMSink | None = None):
        self.con = store.connect()
        self.vm = vm or store.VMSink()
        self.latest: dict = {}
        self.tailer = ingest.Tailer(self.con, self.vm, self.latest)
        self.sources = ingest.make_sources()
        self.due: dict[str, float] = {}
        self.change_fp = store.kv_get(self.con, "change_fp")
        self.code = code_hash()
        self.started = now()

    def tier_armed(self) -> bool:
        t = self.latest.get("tps") or {}
        return t.get("tier") == "test" and now() - t.get("ts", 0) < 30

    def every(self, key: str, period: float, t: float) -> bool:
        if t >= self.due.get(key, 0):
            self.due[key] = t + period
            return True
        return False

    def step(self, force: bool = False) -> None:
        t = now()
        c = cfg()
        fast = self.tier_armed()
        for s in self.sources:
            period = c["poll_fast_s"] if (s.fast and fast) else c["poll_slow_s"]
            if force or self.every("src:" + s.name, period, t):
                self.tailer.pass_source(s)
        if force or self.every("host", c["host_every_s"], t):
            E = ingest.Emit(self.con, self.vm, self.latest)
            host.sample_host(E, t)
            pids = host.process_pids({"rimworldwin64.exe"})
            running = bool(pids.get("rimworldwin64.exe"))
            if running and not self.latest.get("game_running"):
                self.latest["game_running_since"] = t
            self.latest["game_running"] = running if os.name == "nt" else None  # WSL: UNMEASURED
            if os.name == "nt":
                self.vm.add("rm_game_process_up", {}, 1 if running else 0, t)
            for name, st in self.tailer.stats.items():
                if st.get("last_row_ts"):
                    self.vm.add("rm_tel_source_lag_s", {"src": name}, t - st["last_row_ts"], t)
                self.vm.add("rm_tel_rows_total", {"src": name}, st["rows"], t)
                self.vm.add("rm_tel_bad_rows_total", {"src": name}, st["bad"], t)
            self.vm.add("rm_tel_vm_spooled_total", {}, self.vm.spooled, t)
            analysis.push_spark(self.latest, t)
        if force or self.every("changes", 600, t):
            E = ingest.Emit(self.con, self.vm, self.latest)
            self.change_fp = host.detect_changes(self.con, E, t, self.change_fp)
            store.kv_set(self.con, "change_fp", self.change_fp)
            self.con.commit()
            ingest.copy_side_files(self.con)
        if force or self.every("dirs", c["dirs_every_s"], t):
            host.sample_dirs(ingest.Emit(self.con, self.vm, self.latest), t)
        if force or self.every("proofs", 3600, t):
            ingest.ingest_proofs(self.con)
        for p, _ in self.latest.pop("proof_paths", []):
            full = p if os.path.isabs(p) else os.path.join(c["mirror"], p)
            if os.path.exists(full):
                ingest.ingest_proof_file(self.con, full, os.path.relpath(full, c["mirror"]).replace("\\", "/"),
                                         os.path.getmtime(full))
        if force or self.every("retention", 86400, t):
            analysis.retention(self.con, t)
        self.vm.flush()
        self.tailer.flush_raw(force=force)
        if force or self.every("alerts", 15, t):
            srcs = {k: {"last_row_ts": v.get("last_row_ts"), "rows": v.get("rows"), "bad": v.get("bad"),
                        "files": v.get("files"), "error": v.get("error")} for k, v in self.tailer.stats.items()}
            alerts = analysis.evaluate(self.latest, self.con, srcs, self.vm.last_error, t)
            analysis.log_firings(self.con, alerts, t)
            analysis.write_state(self.latest, alerts, srcs,
                                 {"tier_armed": fast, "game_running": self.latest.get("game_running"),
                                  "vm_error": self.vm.last_error, "code": self.code}, t)
        write_json_atomic(os.path.join(c["state"], "heartbeat.json"),
                          {"at": t, "pid": os.getpid(), "code": self.code, "started": self.started,
                           "tier_armed": fast, "vm_sent": self.vm.sent, "vm_spooled": self.vm.spooled,
                           "vm_error": self.vm.last_error})

    def run(self) -> None:
        log = os.path.join(cfg()["logs"], "telemetryd.log")
        os.makedirs(cfg()["logs"], exist_ok=True)
        errors = 0
        while True:
            try:
                self.step()
                errors = 0
            except Exception:  # noqa: BLE001 — log, back off, keep going; supervise restarts on exit
                errors += 1
                with open(log, "a", encoding="utf-8") as f:
                    f.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} step failed ({errors})\n{traceback.format_exc()}\n")
                if errors > 50:
                    raise
                time.sleep(min(30, errors * 2))
            time.sleep(0.5 if self.tier_armed() else 1.0)


_LOCK = None


def single_instance() -> bool:
    """SQLite has ONE writer (design §5): a second telemetryd exits instead of racing the first."""
    global _LOCK
    p = os.path.join(cfg()["state"], "telemetryd.lock")
    os.makedirs(cfg()["state"], exist_ok=True)
    _LOCK = open(p, "a+")
    try:
        if os.name == "nt":
            import msvcrt
            _LOCK.seek(0)
            msvcrt.locking(_LOCK.fileno(), msvcrt.LK_NBLCK, 1)
        else:
            import fcntl
            fcntl.flock(_LOCK.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        return True
    except OSError:
        return False


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--once", action="store_true", help="run every stage once and exit")
    a = ap.parse_args(argv)
    if not a.once and not single_instance():
        print("telemetryd already running (lock held); exiting")
        return 0
    d = Daemon()
    if a.once:
        d.step(force=True)
        ingest.flush_bridge_buckets(ingest.Emit(d.con, d.vm, d.latest), force=True)
        d.vm.flush()
        d.tailer.flush_raw(force=True)
        print(f"telemetryd --once: vm sent {d.vm.sent} spooled {d.vm.spooled}; "
              + ", ".join(f"{k} {v['rows']} rows/{v['bad']} bad" for k, v in d.tailer.stats.items()))
        return 0
    d.run()
    return 0


if __name__ == "__main__":
    sys.exit(main())
