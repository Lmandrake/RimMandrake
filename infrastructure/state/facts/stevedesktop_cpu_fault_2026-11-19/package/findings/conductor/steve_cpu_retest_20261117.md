# SteveDesktop CPU load retest after the +0.100 V raise (2026-11-17)

Verdict: NOT RUN. The existing tool cannot do what was asked, and starting it would break the rules.

## Why not
- src/RimMandrake/Utils/steve_cpu_retest/ is the Oct 31 "unmask retest" for the two masked cores 18 and 19. It reboots Steve to
  remove the numproc=18 mask, then waits through a 144 h (6 day) onset window with quick checks every 20 min and full sweeps
  at 0.2/12/24/48/72/96/120/144 h of uptime. Far over the 90 min limit, and it needs reboots (drain, bcdedit, restart).
- Its last state is END_FAULT (CPU 17 faulted 2026-11-01 07:10Z, mask restored). No retest ran since the 7:32 AM boot.
- retest.ps1 has no stand-alone "sweep the 18 cores now" mode (only -SelfTest, which tests CPU 0 only). A one-off sweep would be
  new tooling, not the existing tool. It also does not sample vcore.
- Steward: IDLE_BY_RULE (nothing admissible; an unowned incident since 2026-11-15 blocks the lane). Fault watch task is Running; untouched.

## Before vs after (fault_monitor.py heat, measured)
Boot 2026-11-17 07:32:58 PST (15:32Z): 18 logical CPUs, 20 cycles, 1.63 h uptime, clean, no fault window opened.
Idle vcore this boot 1.033 V; earlier idle boots 1.032-1.037 V (11-12 22:26Z 1.037, 11-14 21:45Z 1.032, 11-15 00:17Z 1.035).
Earlier load boots read 1.315-1.325 V (max). This boot has no load sample (coremax 45 C, pkgmax 45 C), so the +0.100 V
offset is NOT yet visible at idle and untested under load. The per-core pass/fail table cannot be produced: there is no per-core load data after the boot.

| Core | before (last load boot 11-15) | after (11-17 boot) |
|---|---|---|
| 0-17 | fault-monitor window F20261115T085753Z, 231 bad cycles, cores 0-17 all implicated | no per-core load run; 20 clean idle cycles |

## What would unblock a real load check
- A one-off per-core sweep (about 70 s per core, ~21 min for 18 cores) plus a vcore sample under load needs a small new mode in retest.ps1
  (or a standalone driver) that skips the reboot state machine; and the steward incident must be cleared or the lane paused by hand.
- Or: let the lane run its first RimWorld job; fault_monitor heat then shows vcore under load for this boot (expect ~1.42 V if +0.1 holds).
