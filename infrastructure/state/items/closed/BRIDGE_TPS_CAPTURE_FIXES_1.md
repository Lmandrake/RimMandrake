# BRIDGE_TPS_CAPTURE_FIXES_1 — make the TPS record actually answer "was it slow at 3pm, and why"

## spec
Merged must-do list from the Opus and GPT reviews of BRIDGE_TPS_REGULAR_REPORT_1 (read both reports in Transient/).
1. Start automatically at game load (always-loaded mod hook / verified companion registration), not on a bridge call; write session-start, game-change, menu, shutdown and sampler-failure events.
2. Keep long stalls: drop the 60 s discard, record recovered stalls as incidents; main-thread heartbeat + last-phase, a watchdog thread that logs silence; belt_watchdog.py becomes an external periodic observer (PID/exit, heartbeat age). Never subtract unexplained stalls from the denominator.
3. Window semantics: accumulate expected ticks over time at the known multiplier (observe state before tick work), record wall duration, paused duration, multiplier transitions, raw wall TPS; mark ambiguous transitions.
4. Dependable disk: one ordered bounded writer, sequence numbers + error counters, per-session file names, >=7 days retention with a byte cap, rotation that cannot destroy history.
5. Coarse continuous attribution: time DoSingleTick, tick-list categories, world/map ticks, components; counts/total/max and bounded worst-tick records; separate save/long-event time.
6. Incident context at stall time (phase, ticks, speed, pause/focus/save status, GC delta, writer health), session metadata (save, build, mod manifest), archive Player.log per session.
7. tps_record.py: --at/--since/--until/--tz, explicit session selection, row validation; sustained warning needs contiguous fresh windows; belt_watchdog distinguishes stale/missing coverage from performance.
SHOULD: targeted mod attribution on low ratio; external hang diagnostics. SKIP: always-on per-method/per-pawn instrumentation.

## criteria
- C1 (L0) trace-testable accumulator selftest covers partial pauses, multiplier changes, autosave, a recovered 90 s stall.
- C2 (L0) reader selftest covers --at/--tz, concurrent rotation, future timestamps, stale coverage.
- C3 (L2) passes only on the record FILES (never a bridge answer alone), with `selftest_tps_record.py` green, per
  design/RimMandrake/tps_record.md "Acceptance" items 1-2: autostart with no bridge client / no tps_report / no
  bridge-enabled watchdog probe (`startedBy: bridge-registration`, `install.sampler: complete`, menu heartbeats,
  windows; new game and save load each with their own `game` seq and `save` label); and the controlled interruption
  matrix - 2-10 s hitches and 40/90 s blocks each ONE strictly-parsed `incident` (no duplicate keys) with the right
  gapS, blocked phase, local time with offset and game id, inside a window whose [monoStart, monoEnd] holds the gap
  and its tick work (simShare <= 1); a save is a longevent; permanent hang + kill leaves silence rows, a heartbeat
  whose mainBeatUtc stops while watchdogUtc advances, and a persisted exited-without-shutdown observer row; forced
  kills near sample/segment boundaries leave no replayed or glued rows.
- C4 (L3) on the full ~600-mod list, per the doc's "Acceptance" items 3-5: environmental discrimination (focus, sleep,
  CPU/disk competition, two processes - qualified labels, no cross-process retention); overhead from three separately
  restarted configurations (sampler off / no attribution / full) with limits declared first; and an overnight
  reconstruction (`--at` next morning returns game, local time with offset, interval, duration, ratios, attribution
  validity, map identity, linked archived log). Rewritten 2026-10-10 after the second GPT review: the previous C3/C4
  could pass with incidents mis-keyed, replayed rows, misplaced long ticks and unpersisted observer findings
  (BRIDGE_TPS_REVIEW2_FIXES_1).

## verify
The next morning, `tps_record.py --at <yesterday 15:00> --tz America/Los_Angeles` returns a bounded timeline with ratios and incidents.
