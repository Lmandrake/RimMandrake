---
name: telemetry
description: Query recorded history before re-measuring anything about the game, a live test, the bridge, host memory, disks or the art pipeline. Use when asked "was it slow at T", "what changed before it got slow", "is the disk filling", "how busy was the bridge"; when arming the in-game test tier for a speed-3 live test; when a TELEMETRY row fires in RimPulse; when adding a collector, series, event kind or alert rule; and before trusting a zero from any metric.
---

# Telemetry: recorded history for the game, the bridge and the host

Built by `TELEMETRY_BUILD_EVERY_TICK_ACCOUNTED`; design
`Transient/weekly_cleaning_2026-10-11/08_telemetry_deep_design.md` (owner picks: hybrid VictoriaMetrics + SQLite +
Grafana + RimPulse alerts, data on E:, 1 s test tier + flight recorder). Code: `src/RimMandrake/Utils/telemetry/`.

## The three laws

1. **Raw JSONL is the truth; the stores are caches.** `telemetry rebuild --since 7d` re-ingests.
2. **Stale or absent is UNMEASURED, never 0.** A paused window emits no TPS point; an unread working set is not 0 MB.
3. **No automatic mod blame.** A slow window is a lead for `jawa/map_comp_timing`, never a cause.

**Minimal on purpose** (owner, 2026-10-11): *"this is a tool that we're making available as an Operational
convenience for access when needed and alarms to reveal problems that might not yet be realized, NOT an elaborate
system to track everything ever known about telemetry as a function of everything else. Minimal is good, add
functionality as needed by debugging."* Every game series carries `mods` (loaded set), `modver` (order + versions)
and `build`; compare versions of the SAME mod list against a fixed debug save, on demand (`telemetry around`).
Alarms are coarse (very low memory or TPS, disk filling) and every firing is logged: grade it with
`telemetry label <id> tp|fp` and retune `analysis.RULES` until the noninformative ones are gone.

**Query history before re-measuring live.** A bridge call to read a number telemetry already holds is waste.

## Shape

```
producers (unchanged)                      Windows, E:\telemetry  (survives wsl --shutdown)
 JawaBench TPS record  C:\…\JawaBench\tps ─┐
 health_observer       C:\…\JawaBench\health┤   telemetryd (pythonw, kept alive by supervise.py,
 rimbridge_client      D:\…\_rmscratch\bridge_calls.jsonl ├─►  scheduled task "RimMandrake\Telemetry", 1 min)
 artpipe               D:\Luke\dev\_artpipe ┤     ├─► VictoriaMetrics 127.0.0.1:8428  (series, 2 y)
 deploy/winbuild/modset_builder → inbox\changes ┤ ├─► events.db SQLite WAL             (events, calls, proofs)
 WSL exporter (rm-telemetry-export.timer) → inbox\wsl ┘ ├─► raw\<src>\<day>.jsonl.gz   (90 d, then F:\telemetry_archive)
                                                        └─► state\alerts.json ──► RimPulse rows + 4 sparklines
 Grafana http://localhost:3000 (5 dashboards, anonymous viewer)      `telemetry` CLI (python.exe)
```

Everything runs on the Windows side **with no window** (see traps). WSL only exports its own sources and
watches the heartbeat (`rm-telemetry-health.timer`); it never reads `\\wsl.localhost` from Windows, because
touching that path boots the distro.

## Verbs

```
telemetry health                      every source's newest row and lag, stores, processes, open alerts
telemetry at "15:02" --span 2m        all game/host series + events around a moment
telemetry events --kind deploy,incident --since 24h
telemetry around deploy:<event id>    before/after tick ms per speed (≥30 windows each side, else UNMEASURED)
telemetry bridge --since 1h           calls by tool, p50/p99/max, failures
telemetry disk                        volumes, days-until-full, VHDX, directory sizes
telemetry flight --show · exc --text · runs · run <id> --diff <id> · series --grep · query '<MetricsQL>'
telemetry mark "<why>"                an annotation on every dashboard
telemetry tier test --ttl 60          arm the in-game test tier (hold the bridge first; needs the P2 companion)
telemetry up | down                   run the supervisor now / stop the Windows processes
```

Tools emit change events with `telemetry_emit.emit_change(kind, subject, sha=, detail=)` — it never raises.

## Arming the test tier for a live test

Hold the bridge (`rimflow bridge take`), `telemetry tier test --ttl 60`, run the test, `telemetry tier campaign`
(disarm also dumps the flight recorder). The campaign profile never runs the 1 s / per-tick tier (owner's 10 %
campaign budget, unmeasured until the MUST 17-style overhead run).

## Adding a series or source

Producer writes JSONL with its own timestamp → add a `Source` + parser in `ingest.py` (`make_sources()` is the
registry `telemetry health` prints) → a check in `selftest_telemetry.py` → a panel in
`grafana/build_dashboards.py` (re-run it; the selftest refuses stale JSON). Never write a store directly.
Alert thresholds live in `analysis.RULES`.

Traps (each measured): `references/traps.md`.
