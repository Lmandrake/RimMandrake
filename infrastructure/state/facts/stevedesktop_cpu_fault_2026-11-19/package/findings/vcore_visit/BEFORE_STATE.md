# SteveDesktop before any core-voltage change — measured 2026-11-15 ~20:20Z (12:20 PST)
Item STEVE_LANE_UNSTICK_BRAKED_UNOWNED_EB2A. Machine reached over `ssh stevedesktop` (user stevedesktop\sjlewis, admin=True).
- CPU: Intel Core i9-10900K (Comet Lake), board ASUS ROG STRIX Z490-G GAMING (WI-FI), BIOS 3401 (2026-05-26), microcode 0x100 (both latest; ../efa_20261115/hw2.txt, hw3.txt).
- Windows 10 Pro 19045. PROCTHROTTLEMAX AC=99 (turbo off since 2026-11-07 16:00Z), bcdedit numproc 18 (../efa_20261115/pcfg.txt).
- Core voltage offset: UNMEASURED (no tuning tool installed: no Intel XTU, no ASUS AI Suite, no ThrottleStop; probe1.out). BIOS value unknown, assumed Auto.
- Hypervisor PRESENT: WSL2 (VirtualMachinePlatform + Ubuntu, running) hosts the `seat-server` remote-control tmux and the `seat-runner` (SteveDesktop-Run). VBS status 2 but no security service (HVCI) running (probe2.out, probe3.out).
- Current boot 2026-11-15T08:57:53Z; fault_monitor phase PASSIVE, clean through 2026-11-15T20:15:31Z (11.3 h, lane paused, idle).
- fault_monitor report (fm_report_before.txt): 39 fault windows on record; 9 with first-bad after turbo-off (2026-11-07T16:00Z);
  last first-bad cycle 2026-11-15T05:19:23Z (window F20261115T051134Z, CPU 2). Since 2026-11-12T16:00Z: 8 windows in ~3.2 days (~2.5/day),
  onsets 0.13-0.88 h of uptime. (The 19:50Z item note said 12 windows since turbo-off; this count is first-bad >= 2026-11-07T16:00Z.)
- Test lane: PAUSED by hand since 2026-11-15T13:59:38Z.
