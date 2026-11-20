# SteveDesktop one-off per-core CPU load sweep, 2026-11-17 (17:28-17:55Z, boot 15:32:58Z = 7:32:58 AM PST)

Tool: src/RimMandrake/Utils/steve_cpu_retest/steve_cpu_sweep.py (no reboot, no state machine). Prime95 torture (FFT 8-128K) pinned to ONE logical CPU
for 60 s, stevetemp.exe sampling every 500 ms, WHEA-Logger events in the window, Prime95 liveness. Run in 4 chunks (foreground limit), merged.
Raw: D:\ClaudeWork\rimmandrake\steve_diag\retest\sweep_20261117.json (+ _allcore.json, _c1-_c4.json).

## Verdict
- 18 of 18 logical CPUs PASS: 0 Prime95 errors, 0 WHEA events, Prime95 alive and 60.0 cpu-s on every one. No fault, no reboot. [measured]
- The +0.100 V does NOT show under load in the vcore sensor: single pinned core 0.994-1.029 V (one core 1.001), all-18-thread load 0.995-0.998 V,
  idle 0.994-1.027 V before/after (BIOS-change boot idle was 1.033 V; earlier boots idle 1.032-1.037 V). Earlier-boot peaks of 1.315-1.325 V were not reproduced. [measured]
  The sensor reads ~1.0 V idle AND under full load, so it is not tracking the load voltage; whether the BIOS raise took effect is not decided by this sensor [guess ~65%].
- Heat is low: hottest core 46 C single-core, 52 C with all 18 threads (8 cores busy, 489 cpu-s in 60 s). Nothing thermal about a fault. [measured]
- A pass over 60 s per core is a weak test of an onset-time fault (the old onset needed days of uptime): this says "no fault in the first 2 h of this boot", not "fixed". [guess]

## Per-core (logical CPU: pinned core temp C / vcore V; all PASS)
0 45/1.020, 1 43/1.029, 2 45/1.028, 3 46/1.028, 4 44/1.024, 5 44/1.028, 6 42/1.028, 7 42/1.029, 8 44/1.029, 9 44/1.029, 10 42/1.028,
11 42/1.028, 12 43/1.029, 13 43/1.028, 14 43/1.029, 15 41/1.028, 16 42/1.001, 17 42/1.029. Logical CPUs pair on 9 physical cores.
Vcore idle at sweep start: 0.994-1.027 V (preflight 4 s samples). All-core 45 s: PASS, 0.995 V, 52 C.

## Incident conflict (measured 17:25Z)
Both are true. The steward's own state (testq/steward.json): IDLE_BY_RULE, jobs [], fault False, incident STEVE_LANE_UNSTICK_BRAKED_UNOWNED_EB2A level 3,
since 2026-11-15T04:20:03Z, 2943 min "unowned". That item is state ready but BLOCKED (owner BENCH, "BLOCKED: steward session ended ... diagnose item"), and
ops_watch steve_incident_unclaimed skips a BLOCKED item unless the lane is in a fault window, so it reads 0. Nothing in the queue (pending empty, running empty, lane not paused).
What stops a queued job: not the incident. The steward admits nothing ("pipeline tests only: nothing admissible, 35 mods"), so jobs only run if submitted by hand
or a mod becomes admissible. [guess ~70% that a hand-submitted job would run; not tested.] The incident item should be unblocked or closed (the world-start diagnose it waits on, and the BIOS visit, are past).
Prime95 left running: 0. Fault Watch task: Running, untouched.
