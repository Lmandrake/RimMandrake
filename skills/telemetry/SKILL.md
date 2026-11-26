---
name: telemetry
description: Query recorded history before re-measuring anything about the game, a live test, the bridge, host memory, disks or the art pipeline. Use when asked "was it slow at T", "what changed before it got slow", "is the disk filling", "how busy was the bridge"; when arming the in-game test tier for a speed-3 live test; when a TELEMETRY row fires in RimPulse; when adding a collector, series, event kind or alert rule; and before trusting a zero from any metric.
---

# Telemetry: recorded history for the game, the bridge and the host

`TELEMETRY_BUILD_EVERY_TICK_ACCOUNTED` is the item that built telemetry. The code is in
`src/RimMandrake/Utils/telemetry/`. The design is in [references/history.md](references/history.md).

The owner picked these parts:

- a hybrid of VictoriaMetrics, SQLite, Grafana and alerts. RimPulse, which showed the alerts, is retired.
- the data on drive E:.
- a 1 s test tier and a flight recorder. §Arming the test tier says what they are.

## The three laws

1. **Raw JSONL is the truth; the stores are caches.** `telemetry rebuild --since 7d` makes telemetryd
   read the producers' files of that time again. telemetryd does not read `E:\telemetry\raw`. So a row in a producer file that
   is already gone does not come back.
2. **Stale or absent is UNMEASURED, never 0.** A paused window has no TPS point. A working set that nobody could read
   is not 0 MB.
3. **No automatic mod blame.** A slow window is a lead. Take the lead to `jawa/map_comp_timing`. A slow window is never
   a cause.

**Minimal on purpose** (owner, 2026-10-11): *"this is a tool that we're making available as an Operational
convenience for access when needed and alarms to reveal problems that might not yet be realized, NOT an elaborate
system to track everything ever known about telemetry as a function of everything else. Minimal is good, add
functionality as needed by debugging."*

- Every game series carries three labels:
  - `mods`: the set of loaded mods;
  - `modver`: the mod order and the mod versions;
  - `build`: the build of the JawaBench companion.
- Compare versions of the SAME mod list, against a fixed debug save. Compare on demand, with `telemetry around`.
  `telemetry around` filters by game speed, and by `--game`. Check yourself that both sides have the same `mods` label:
  `telemetry query` prints the labels.
- The alarms are coarse: very low memory or TPS, or a disk that fills. `analysis.RULES` (in `analysis.py`) holds the
  alarm thresholds.
- Telemetry logs each alarm that fires, as an `alert_fired` event.
- Grade each `alert_fired` event with `telemetry label <id> tp|fp`. The `<id>` is the number of the event in
  `telemetry events --kind alert_fired`. `tp` is a true alarm. `fp` is a false alarm.
- Retune `analysis.RULES` until the noninformative alarms are gone.

**Query history before re-measuring live.** A bridge call to read a number that telemetry already holds is waste.

## Two lessons on measures of our own process

- **The friction census `events.jsonl` truncates AskUserQuestion input at 300 chars.** The friction census of 2026-10-26
  counted the owner's messages and question cards. The cut loses the '(Recommended)' option and most
  options. To measure how often he agrees with a recommendation, extract the cards again from the transcripts. The
  extractor is `orch_record/delegation/extract_cards.py`, in the folder that
  `python3 src/RimMandrake/Utils/rmpaths.py` prints (the RimMandrake folder of the agent storage root).
- **A noise band built from week-to-week spread across a ramping period is trend, not noise.** The example is v2,
  the rimflow version of 2026-10. While v2 was ramping, v2 ran 267, 279 and 773 items done a week. A band from that
  spread would call a fourfold drop SAME.
- One reference week is a weak baseline, because its bands are wide. The band of `done_wk` (items done in a week) was
  1.25 on the log scale. The days ran 5..398 items done.

## Shape

```
producers                                  Windows, E:\telemetry  (survives wsl --shutdown)
 JawaBench TPS record  C:\…\JawaBench\tps ─┐
 (health observer: cut)                       ┤   telemetryd (pythonw, kept alive by supervise.py,
 rimbridge_client      <data root>\scratch\bridge_calls.jsonl ├─►  scheduled task "RimMandrake\Telemetry", 1 min)
 artpipe               D:\ClaudeWork\rimmandrake\artpipe ┤     ├─► VictoriaMetrics 127.0.0.1:8428  (series, 2 y)
 ops_watch             <data root>\ops_watch\series ─────┤     ├─► events.db SQLite WAL             (events, calls, proofs)
 deploy/winbuild/modset_builder → inbox\changes ┤              ├─► raw\<src>\<day>.jsonl.gz   (90 d, then F:\telemetry_archive)
 WSL exporter (rm-telemetry-export.timer) → inbox\wsl ┘        └─► state\alerts.json   (`telemetry health` shows it)
 Grafana http://localhost:3000 (5 dashboards, anonymous viewer)      `telemetry` CLI (python.exe)
```

- `<data root>` is the folder that `python3 src/RimMandrake/Utils/rmpaths.py` prints.
- **All four games are read** (ArchBig, ArchSmall, Steve1, Steve2; the list is `game_names.py`). A game on Archmagi is
  read from its own folder. A game on another machine is copied each minute by `rm-telemetry-pull.timer`
  (`telemetry/pull_games.py`) into `E:\telemetry\inbox\games\<machine>\`. Every game series, event and bridge call
  carries its `game`.
- Ask about one game with `--game Steve1` on `series`, `query`, `at`, `events`, `around`, `flight`, `exc` and `bridge`.
  Without `--game`, all games answer, each line labelled. `telemetry games` says which are up and how old each reading is.
- The exit codes differ: 2 no such game, 3 could not look at it (with the cause; rows held from before are shown with
  their age), 4 it has written no row yet, 0 a reading. A game that is down is a reading: it says `down` and the age.
- On a machine without the store (SteveDesktop), the same `telemetry` command asks Archmagi's store over ssh.
- Rows from before 2026-11-23 have no game. Game series without a label are ArchBig's. Bridge calls without one are
  either Archmagi game's.
- `rm_proc_*` and `rm_game_process_up` count any RimWorld process on Archmagi.
- Page: `design/specs/2026-11-23-telemetry-any-game/boundary.md`.
- No program carries an alarm out of telemetry. To see an open alarm, run `telemetry health`.
- The daemon, the stores, Grafana and the CLI run on the Windows side **with no window** (`references/traps.md`, "Visible windows").
- WSL does three things only. WSL exports its own sources, copies the other machines' game records, and
  `rm-telemetry-health.timer` watches the heartbeat.
- The Windows side never reads `\\wsl.localhost`, because a read of that path boots the distro.

## Verbs

```
telemetry games [Steve1]              each game: up or down, age of its newest row and of the last look at it
telemetry health                      every source's newest row and lag, stores, processes, open alerts
telemetry at "15:02" --span 2m        all game/host series + events around a moment
telemetry events --kind deploy,incident --since 24h
telemetry around deploy:<event id>    before/after tick ms per speed (≥30 windows each side, else UNMEASURED)
telemetry bridge --since 1h           calls by tool, p50/p99/max, failures
telemetry disk                        volumes, days-until-full, VHDX, directory sizes
telemetry flight --show · exc --text · runs · run <id> --diff <id> · series --grep · query '<MetricsQL>'
telemetry mark "<why>"                an annotation on every dashboard
telemetry tier test --ttl 60          arm the in-game test tier (hold the bridge first; needs the P2 companion,
                                      the JawaBench build that has the tool jawa/telemetry_tier)
telemetry up | down                   run the supervisor now / stop the Windows processes
```

To make a change event from a tool, call `telemetry_emit.emit_change(kind, subject, sha=, detail=)`. That call never
raises an error.

## Arming the test tier for a live test

The test tier makes the TPS record finer for one test. Its windows are 1 s in place of 5 s, and it reads each tick.
The reading of each tick needs `attribution` on in the companion's `tps_settings.json` (on by default).
The flight recorder is a part of the test tier. The flight recorder holds the last ticks in memory, and dumps them to
a file.

1. Hold the bridge (`rimflow bridge take`).
2. Arm the test tier: `telemetry tier test --ttl 60`.
3. Run the test.
4. Disarm the test tier: `telemetry tier campaign`. The disarm also dumps the flight recorder.

The companion never runs the 1 s / per-tick tier in its CAMPAIGN profile. The profile is CAMPAIGN when a save named in
`infrastructure/state/CANONICAL_SAVE.md` is loaded. `JawaBenchSafetyCore.cs` (`Effective`) holds the other cases. For
example, a loaded save that the companion cannot name makes the profile CAMPAIGN.

## Adding a series or source

1. Producer writes JSONL with its own timestamp in each row.
2. Add a `Source` and a parser in `ingest.py`. `make_sources()` there is the registry that `telemetry health` prints.
3. Add a check in `selftest_telemetry.py`.
4. Add a panel in `grafana/build_dashboards.py`, then run that file again. The selftest refuses stale JSON.

Never write a store directly. Alert thresholds live in `analysis.RULES`.

Traps (each measured): `references/traps.md`.
