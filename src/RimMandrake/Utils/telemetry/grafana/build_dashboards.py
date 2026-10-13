#!/usr/bin/env python3
"""Generate the five provisioned Grafana dashboards (design §8) as JSON files beside this script.

Edit HERE, re-run, commit the JSON: dashboards are provisioned read-only (allowUiUpdates false),
so a UI edit is lost by design. `python3 build_dashboards.py --check` exits 1 when the committed
JSON is stale against this generator (the selftest runs it).

Datasources (provisioning/datasources/telemetry.yaml): uid `vm` = VictoriaMetrics (Prometheus
API), uid `events` = the SQLite events DB through frser-sqlite-datasource (times are unix
SECONDS; `$__from`/`$__to` are milliseconds, hence the /1000.0).
"""
from __future__ import annotations

import json
import os
import sys

HERE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "dashboards")
VM = {"type": "prometheus", "uid": "vm"}
EV = {"type": "frser-sqlite-datasource", "uid": "events"}
RANGE = "ts >= $__from/1000.0 AND ts <= $__to/1000.0"


def sql_target(q, ref="A", time_cols=("time",), qtype="table"):
    return {"refId": ref, "datasource": EV, "queryText": q, "rawQueryText": q, "queryType": qtype,
            "timeColumns": list(time_cols)}


def prom(expr, legend="", ref="A", interval=""):
    t = {"refId": ref, "datasource": VM, "expr": expr, "legendFormat": legend, "range": True}
    if interval:
        t["interval"] = interval
    return t


class Board:
    def __init__(self, uid, title, refresh="5s", time_from="now-1h", tags=()):
        self.d = {"uid": uid, "title": title, "tags": ["rimmandrake", "telemetry", *tags], "timezone": "browser",
                  "schemaVersion": 39, "version": 1, "refresh": refresh, "editable": False,
                  "time": {"from": time_from, "to": "now"}, "panels": [],
                  "annotations": {"list": []}, "templating": {"list": []},
                  "links": [{"title": "Telemetry", "type": "dashboards", "tags": ["telemetry"], "asDropdown": True}]}
        self.y = 0
        self.x = 0
        self.id = 1

    def annotate(self, name, kinds, color, enable=True):
        ks = ",".join(f"'{k}'" for k in kinds)
        q = (f"SELECT ts AS time, ts_end AS timeEnd, kind || ': ' || COALESCE(subject,'') AS text, kind AS tags "
             f"FROM events WHERE kind IN ({ks}) AND {RANGE} ORDER BY ts LIMIT 500")
        self.d["annotations"]["list"].append({
            "name": name, "datasource": EV, "enable": enable, "iconColor": color,
            "target": sql_target(q, time_cols=("time", "timeEnd"))})
        return self

    def row(self, title):
        self._newline()
        self.d["panels"].append({"type": "row", "title": title, "id": self.id, "collapsed": False,
                                 "gridPos": {"x": 0, "y": self.y, "w": 24, "h": 1}, "panels": []})
        self.id += 1
        self.y += 1
        return self

    def _newline(self):
        if self.x:
            self.y += self._h
            self.x = 0

    def panel(self, title, targets, kind="timeseries", w=12, h=8, unit=None, desc="", stack=False,
              legend_right=False, extra=None):
        if self.x + w > 24:
            self._newline()
        p = {"type": kind, "title": title, "id": self.id, "description": desc,
             "gridPos": {"x": self.x, "y": self.y, "w": w, "h": h},
             "datasource": targets[0]["datasource"], "targets": targets,
             "fieldConfig": {"defaults": {"custom": {}}, "overrides": []}, "options": {}}
        if unit:
            p["fieldConfig"]["defaults"]["unit"] = unit
        if kind == "timeseries":
            p["fieldConfig"]["defaults"]["custom"] = {"lineWidth": 1, "fillOpacity": 10 if not stack else 60,
                                                      "showPoints": "never", "spanNulls": False,
                                                      "stacking": {"mode": "normal" if stack else "none"}}
            p["options"] = {"legend": {"displayMode": "list", "placement": "right" if legend_right else "bottom"},
                            "tooltip": {"mode": "multi", "sort": "desc"}}
        if extra:
            for k, v in extra.items():
                p[k] = v
        self.d["panels"].append(p)
        self.id += 1
        self.x += w
        self._h = h
        if self.x >= 24:
            self._newline()
        return self

    def write(self, name):
        os.makedirs(HERE, exist_ok=True)
        return name, json.dumps(self.d, indent=1, sort_keys=True) + "\n"


EVENTS_TABLE = ("SELECT datetime(ts,'unixepoch','localtime') AS at, kind, subject, seat, sha, "
                "substr(detail,1,300) AS detail FROM events WHERE kind IN ({kinds}) AND " + RANGE +
                " ORDER BY ts DESC LIMIT 300")


def ev_table(kinds):
    return EVENTS_TABLE.format(kinds=",".join(f"'{k}'" for k in kinds))


def live_test():
    b = Board("rm-live-test", "Live test (game, 1 s while armed)", refresh="5s", time_from="now-30m", tags=("game",))
    b.annotate("markers", ["marker", "tier"], "blue").annotate("incidents", ["incident", "silence"], "red")
    b.annotate("flight dumps", ["flight"], "purple").annotate("deploys", ["deploy", "build", "modlist"], "orange")
    b.annotate("bridge holds", ["bridge_hold"], "green", enable=False)
    b.row("Speed")
    b.panel("TPS (ticks per real second)", [prom("rm_game_tps", "{{tier}} x{{mult}}")], w=8, desc=
            "Only windows that ticked. Judge ratio, not raw TPS: 170 TPS is healthy at speed 3 and dire at speed 4.")
    b.panel("Ratio to target speed", [prom("rm_game_ratio", "{{tier}} x{{mult}}")], w=8, unit="percentunit")
    b.panel("Tick ms (engine mean) and worst tick", [prom("rm_game_tick_ms", "mean x{{mult}}"),
                                                    prom("rm_game_worst_tick_ms", "worst tick", "B")], w=8, unit="ms")
    hist = prom("sum by (le) (rm_game_tick_hist)", "{{le}}")
    hist["format"] = "heatmap"
    b.panel("Tick-duration histogram (test tier)", [hist], kind="heatmap",
            w=12, h=9, desc="Per-window bucket counts from the in-game flight recorder tier (histV 1). "
                            "Empty = tier not armed: UNMEASURED, not zero.",
            extra={"options": {"calculate": False, "yAxis": {"unit": "ms"}, "cellGap": 1,
                               "color": {"mode": "scheme", "scheme": "Oranges"}}})
    b.panel("Stage split, ms per tick", [prom("rm_game_stage_ms", "{{stage}}")], w=12, h=9, unit="ms", stack=True,
            legend_right=True)
    b.row("Errors, bridge, memory")
    b.panel("Exceptions per window (and suppressed by the 10k log cap)",
            [prom("rm_game_exc", "logged"), prom("rm_game_exc_suppressed", "suppressed by cap", "B")], w=8)
    b.panel("Bridge on the main thread", [prom("rm_game_bridge_calls", "calls/window"),
                                          prom("rm_game_bridge_main_ms", "main-thread ms", "B"),
                                          prom("rm_game_bridge_qmax_ms", "queue max ms", "C")], w=8)
    b.panel("Heap MB and gen-0 GCs per minute", [prom("rm_game_heap_mb", "heap MB"),
                                                 prom("rate(rm_game_gc_gen0[1m])*60", "GC/min", "B")], w=8)
    b.panel("Pawns per map", [prom("rm_game_pawns", "map {{map}} {{biome}}")], w=8)
    b.panel("Things per map", [prom("rm_game_things", "map {{map}} {{biome}}")], w=8)
    b.panel("Frame gap max ms / FPS", [prom("rm_game_gap_max_ms", "gap max ms"), prom("rm_game_fps", "fps", "B")], w=8)
    b.row("Test-state monitor (jawa/vitals, while armed)")
    b.panel("Colonists alive / downed / hostile, hostiles on map",
            [prom("rm_game_pawns_colonists_alive", "colonists alive"), prom("rm_game_pawns_colonists_downed", "downed", "B"),
             prom("rm_game_pawns_colonists_hostile", "colonists hostile", "C"), prom("rm_game_pawns_hostile", "hostiles", "D")],
            w=8, desc="From the vitals monitor's rollup rows. Empty = monitor not armed: UNMEASURED, not zero.")
    b.panel("Min colonist health / mood margin", [prom("rm_game_pawns_min_health", "min health"),
                                                  prom("rm_game_pawns_min_mood_margin", "min mood - break threshold", "B")], w=8)
    b.panel("Hostile structures, modal age, clock jumps",
            [prom("rm_game_threat_structures", "{{kind}}"), prom("rm_game_modal_age_s", "modal age s", "B"),
             prom("rm_game_clock_disc_total", "clock discontinuities", "C")], w=8)
    b.panel("Monitor triggers", [sql_target(ev_table(["vitals_trigger", "vitals_tomb", "vitals_advance", "vitals_arm",
                                                      "vitals_disarm"]))], kind="table", w=24)
    b.row("Recent incidents and flight dumps")
    b.panel("Flight dumps", [sql_target("SELECT datetime(ts,'unixepoch','localtime') AS at, trigger, tick_from, "
                                        "tick_to, worst_us/1000.0 AS worst_ms, file FROM flight WHERE " + RANGE +
                                        " ORDER BY ts DESC LIMIT 100")], kind="table", w=12)
    b.panel("Incidents / silences", [sql_target(ev_table(["incident", "silence", "resumed", "marker"]))],
            kind="table", w=12)
    return b.write("live_test.json")


def host_disk():
    b = Board("rm-host-disk", "Host and disk", refresh="1m", time_from="now-7d", tags=("host",))
    b.annotate("OOM", ["oom"], "red").annotate("retention", ["retention"], "gray", enable=False)
    b.row("Disks")
    b.panel("Free space per volume", [prom("rm_disk_free_bytes", "{{vol}}: ({{role}})")], w=12, unit="bytes")
    b.panel("WSL disk image: file, allocated, WSL used", [prom("rm_vhdx_size_bytes", "VHDX logical"),
                                                          prom("rm_vhdx_alloc_bytes", "VHDX allocated", "B"),
                                                          prom("rm_wsl_disk_used_bytes", "WSL used", "C")],
            w=12, unit="bytes", desc="Allocated minus WSL used = slack a compaction would return.")
    b.panel("Days until full (linear, 24 h slope)",
            [prom("rm_disk_free_bytes / clamp_min(-deriv(rm_disk_free_bytes[24h]), 1) / 86400", "{{vol}}")],
            w=12, unit="d", desc="Only meaningful while free space is falling; a rising volume reads huge.")
    b.panel("Directory sizes (hourly)", [prom("rm_dir_bytes", "{{dir}}")], w=12, unit="bytes")
    b.row("Memory")
    b.panel("Windows memory", [prom("rm_host_mem_avail_bytes", "available"),
                               prom("rm_host_commit_total_bytes", "commit", "B"),
                               prom("rm_host_commit_limit_bytes", "commit limit", "C")], w=12, unit="bytes")
    b.panel("WSL cgroups (memwatch)", [prom("rm_cg_mem_bytes", "{{cg}}")], w=12, unit="bytes", legend_right=True)
    b.panel("WSL memory", [prom("rm_wsl_mem_avail_bytes", "available"), prom("rm_wsl_mem_total_bytes", "total", "B"),
                           prom("rm_wsl_swap_used_bytes", "swap used", "C")], w=12, unit="bytes")
    b.panel("Game process (health observer)", [prom("rm_proc_working_set_mb", "working set {{pid}}"),
                                               prom("rm_proc_cpu_cores", "cores {{pid}}", "B")], w=12)
    b.panel("OOM and memwatch events", [sql_target(ev_table(["oom", "memwatch_shmem", "memwatch_oom_kill"]))],
            kind="table", w=24)
    return b.write("host_disk.json")


def bridge():
    b = Board("rm-bridge", "Bridge", refresh="30s", time_from="now-6h", tags=("bridge",))
    b.annotate("bridge holds", ["bridge_hold"], "green").annotate("proof runs", ["proof_run"], "purple")
    b.annotate("game state", ["game_state"], "blue")
    b.panel("Calls per minute by tool (top 10)",
            [prom("topk(10, sum by (tool) (sum_over_time(rm_bridge_calls[1m])))", "{{tool}}", interval="1m")],
            w=12, stack=True, legend_right=True)
    b.panel("Mean and max latency", [prom("sum(sum_over_time(rm_bridge_ms_sum[1m])) / "
                                          "sum(sum_over_time(rm_bridge_calls[1m]))", "mean ms", interval="1m"),
                                     prom("max(max_over_time(rm_bridge_ms_max[1m]))", "max ms", "B", interval="1m")],
            w=12, unit="ms")
    b.panel("Errors per minute", [prom("sum(sum_over_time(rm_bridge_errors[1m]))", "errors", interval="1m")], w=12)
    b.panel("Slowest tools (p50 / p99 from per-call rows)",
            [sql_target("SELECT tool, COUNT(*) AS calls, ROUND(AVG(ms),1) AS mean_ms, MAX(ms) AS max_ms, "
                        "SUM(CASE WHEN success=0 THEN 1 ELSE 0 END) AS failed FROM bridge_calls WHERE " + RANGE +
                        " AND ms IS NOT NULL GROUP BY tool ORDER BY mean_ms*calls DESC LIMIT 25")], kind="table", w=12)
    b.panel("Proof runs", [sql_target("SELECT datetime(ts,'unixepoch','localtime') AS at, mod, n_pass, n_fail, "
                                      "n_other, wall_s, path FROM proof_runs WHERE " + RANGE +
                                      " ORDER BY ts DESC LIMIT 100")], kind="table", w=24)
    return b.write("bridge.json")


def changes():
    b = Board("rm-changes", "Changes", refresh="1m", time_from="now-7d", tags=("changes",))
    b.annotate("deploys", ["deploy"], "orange").annotate("builds", ["build"], "yellow")
    b.annotate("mod list", ["modlist"], "blue").annotate("alarms", ["alert_fired"], "red")
    b.panel("Tick ms by speed and mod set (only windows that ticked)",
            [prom("rm_game_tick_ms", "x{{mult}} mods {{mods}} ver {{modver}} build {{build}}")],
            w=12, unit="ms")
    b.panel("Stage cost, ms per tick (median over 10 min)",
            [prom("quantile_over_time(0.5, rm_game_stage_ms[10m])", "{{stage}}", interval="1m")], w=12, unit="ms",
            legend_right=True)
    b.panel("Deploys, builds, mod-list changes", [sql_target(ev_table(["deploy", "build", "modlist"]))],
            kind="table", w=12)
    b.panel("Alarms fired (grade each: telemetry label <id> tp|fp)",
            [sql_target(ev_table(["alert_fired", "alert_label"]))], kind="table", w=12,
            desc="Coarse alarms only. Version comparison is on demand (telemetry around), never per deploy.")
    b.panel("Per-component timing (persisted map_comp_timing)",
            [sql_target("SELECT datetime(ts,'unixepoch','localtime') AS at, type, mod, ms_per_tick, calls, max_ms "
                        "FROM mapcomp WHERE " + RANGE + " ORDER BY ts DESC, ms_per_tick DESC LIMIT 200")],
            kind="table", w=24)
    return b.write("changes.json")


def pipeline():
    b = Board("rm-pipeline", "Pipeline and telemetry health", refresh="1m", time_from="now-24h", tags=("pipeline",))
    b.annotate("selftest runs", ["selftest_run"], "green", enable=False)
    b.panel("Art jobs: elapsed seconds", [prom("rm_art_elapsed_s", "{{channel}} {{status}}")], w=12, unit="s")
    b.panel("Art jobs per hour", [prom("sum by (status) (count_over_time(rm_art_elapsed_s[1h]))", "{{status}}",
                                       interval="10m")], w=12)
    b.panel("Selftests (last run)", [prom("rm_selftests", "{{state}}")], w=12)
    b.panel("Telemetry: source lag (s since newest row)", [prom("rm_tel_source_lag_s", "{{src}}")], w=12, unit="s",
            desc="Lag grows when a producer is quiet (no game, no bridge) — that is silence, not failure. "
                 "RimPulse raises 'telemetry blind' only when the producer should be talking.")
    b.panel("Telemetry: rows ingested", [prom("rm_tel_rows_total", "{{src}}")], w=12)
    b.panel("Telemetry: bad rows / VM spool", [prom("rm_tel_bad_rows_total", "bad {{src}}"),
                                               prom("rm_tel_vm_spooled_total", "spooled points", "B")], w=12)
    b.panel("Recent ledger events", [sql_target(ev_table(["ledger", "bridge_hold", "game_state"]))],
            kind="table", w=24)
    return b.write("pipeline.json")


BUILDERS = [live_test, host_disk, bridge, changes, pipeline]


def main(argv=None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    stale = []
    for f in BUILDERS:
        name, text = f()
        p = os.path.join(HERE, name)
        old = open(p, encoding="utf-8").read() if os.path.exists(p) else None
        if old != text:
            stale.append(name)
            if "--check" not in argv:
                with open(p, "w", encoding="utf-8") as fh:
                    fh.write(text)
    if "--check" in argv:
        print("dashboards " + ("STALE: " + ", ".join(stale) if stale else "current"))
        return 1 if stale else 0
    print(f"wrote {len(stale)} of {len(BUILDERS)} dashboards")
    return 0


if __name__ == "__main__":
    sys.exit(main())
