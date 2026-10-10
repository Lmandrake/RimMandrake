# BRIDGE_TPS_CAPTURE_FIXES_1 — progress log (FOUNDRY, 2026-10-10)

Offline only: the game is UP under another seat's bridge. Nothing deployed. Deploy at next shutdown
(`python3 src/RimMandrake/bridgetools/build.py --apply` with the game closed).

Commits on origin/main: `df0071a87` (C# runtime), `ada3f32b8` (reader, selftests, watchdog observer),
`6721b216a` (doc rewrite, heartbeat fix).

## (3) window-semantics accumulator
Done. `JawaBenchTpsMath.FrameAccumulator`: prefix observes paused/mult before tick work, postfix reads ticks;
expected ticks integrated per interval over unpaused time; explained (long event) time excluded; unexplained
gaps never subtracted; mid-loop mult change and state change across a blocked gap count as ambiguous.
C1: selftest replays 9 synthetic engine traces (healthy, 40 % partial pause, 12x/6x flip, forced-normal
mid-loop, flip-flop → mixed, autosave 12 s → longevent, recovered 90 s stall → kept stall + incident,
stall while paused, half-speed). C# parity 49/49 lines identical (production .cs built via winbuild).

## (4) ordered bounded writer
Done. `JawaBenchTpsWriter`: seq at enqueue, one thread, 4,096-line bound (drop + count), retry on failure,
session-named 2 MB segments (rotation never moves or deletes), retention ≥ 7 days then 256 MB cap,
current session never pruned, shutdown drain.

## (2) stalls, heartbeat, watchdog
Done. 60 s discard removed; gaps > 2 s are incidents. `JawaBenchTpsWatchdog`: Root.Update heartbeat, phase
stack, silence thread (10 s, repeat 30 s), `hb_<session>.json`. `belt_watchdog.py` is the external observer:
`silent` / `frozen` / `exited-without-shutdown`, appended once to observer.jsonl.

## (7) tps_record.py queries
Done. `--at/--span/--since/--until/--tz/--session/--sessions`; row validation (malformed/invalid/future/
vanished counted); session+seq ordering; contiguous-fresh sustained; coverage (MISSING/STALE/ERROR) apart
from performance; per-target reporting. C2 covered in the selftest.

## (1) auto-start at load
Done, verified from decompiled RimBridgeServer.dll (installed workshop copy 3727949765):
`Root_Update_Patch` → `OnRuntimeReady` → `RimBridgeCapabilities.Initialize` → `DiscoverProviders` →
`BuildProviders` → `TryCreateInstance` → `Activator.CreateInstance` for any companion type with an INSTANCE
[Tool]. `jawa/tps_report` moved to `JawaBenchTpsTools` (instance tool, public ctor → `Install`). Chosen over a
RimMandrake [StaticConstructorOnStartup] because no single RimMandrake C# mod is on every list, while
`brrainz.rimbridgeserver` is. Side effect: JawaBenchInit's lazy installs now fire at load too.

## (5) coarse attribution
Done. `JawaBenchTpsProfiler`: DoSingleTick, tick lists by tickType, WorldTick, WorldPostTick, MapPreTick,
MapPostTick, MapComponentTick, GameComponentTick. Inclusive [n, ms, max] per window, exclusive `top`,
≤ 3 worst ticks ≥ 30 ms, calibrated `profEstMs` (lower bound).

## (6) incident context + Player.log archive
Done. Incident: gap split, quietPhase, prevSimS, gcDelta, save state, phase, ticks, speed, pause, focus,
heap, writer health. `context` every 60 s (maps/biome/pawns/things, heap, working set). Session manifest with
ordered mods + Harmony owners. Player-prev.log archived at start, Player.log at shutdown; markers in Player.log.

## owed live
- C3 (L1): record starts at load with NO bridge call (`session` line `startedBy: bridge-registration`);
  overhead on the full ~600-mod list (A/B with `"attribution": false`) stated.
- C4 (L2): kill the process and force a hang; record ends at the last heartbeat, observer reports it.

## Round 3 live (FOUNDRY bridge driver, 2026-10-10 08:25-08:50 PT, 26-mod minimal list)
- Deployed companion (`build.py --gm --apply`; without `--gm` it refuses, it would drop the GM tools). Game killed by PID first.
- C3 PARTIAL: launched via Steam, checked `JawaBench/tps` BEFORE any bridge call: `session` line (`startedBy: bridge-registration`), `marker start`, `log` (Player-prev archived), `menu` rows already on disk; heartbeat file live. Samples start with the first map (menu emits no windows). Ran Ultrafast ~90 s: median ~3.3k tps, ratio ~0.35 vs the 9000 target (minimal list, debug map).
- Overhead (minimal list only): profiler's own calibrated lower bound `profEstMs` ~6 ms per 5 s window (~0.14% of sim time). A/B attribution on/off was NOT clean: attribution=false run gave 2146 tps vs 3333 with it on, but each run is a different random debug map, so the difference is map noise, not overhead. FULL ~600-mod measurement STILL OWED (C3 not verified for that reason).
- C4 PASS: (a) taskkill /F mid-Ultrafast: last record seq 71 at 15:35:28.8Z, heartbeat 15:35:29.42Z, kill 15:35:29.67Z; last line parses; belt_watchdog wrote `exited-without-shutdown` to observer.jsonl once heartbeat aged > 15 s. (b) permanent hang = NtSuspendProcess (Transient/ntsuspend_20261010.ps1, staged D:\Luke\dev\_rmscratch\ntsuspend.ps1) for 70 s: belt_watchdog reported WARN `frozen` (running pid, heartbeat stopped), then taskkill: record ends at last heartbeat, observer reported exited-without-shutdown. (c) recovered 41 s freeze: kept as a stall incident (gapS 40.967 unexplained), not discarded.
- DEFECT FOUND + FIXED: incident rows carried `"kind":"incident"` then `"kind":"stall"` (duplicate key; GapFields emitted kind), so JSON readers saw kind=stall and `tps_record` reported "0 incidents" with gapMax 40967 ms. Removed `kind` from GapFields (C# + Python port; type field carries it), parity 49/49, redeployed, re-ran a 25 s freeze: 1 incident counted. Rows from the earlier build on disk keep the duplicate key.
- Left: game killed, live ModsConfig restored to the 67-mod list it had (copy in Transient/ModsConfig.live67_before_tps_20261010.xml).
