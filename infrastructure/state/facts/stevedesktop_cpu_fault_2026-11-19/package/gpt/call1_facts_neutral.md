# SteveDesktop: the machine, what was changed, what was tested (facts only, no conclusions)

Times are UTC unless marked PST. "[measured]" = read from a log or instrument named in the package; "UNMEASURED" = nobody has read it.

## The machine
- CPU Intel Core i9-10900K (Comet Lake, CPUID A0655, 10 cores / 20 threads), microcode 0x100 (Intel's latest for this CPU).
- Board ASUS ROG STRIX Z490-G GAMING (WI-FI). BIOS 0607 (2020-05-29) until it was flashed to 3401 on about 2026-10-31/11-01.
  (ASUS release date of 3401: 2026-08-19 per the download page; Windows reports a BIOS date of 2026-05-26.)
- RAM 4 x 32 GB G.Skill F4-2666C18-32GTZN at 2666 MT/s, 1.2 V (no XMP applied). GPU RTX 2080 Ti. Windows 10 Pro 19045.
- Hyper-V is running (WSL2 / VirtualMachinePlatform with an Ubuntu guest that hosts agent processes). VBS reports status 2
  but no HVCI service. Vendor ring-0 drivers loaded: AsIO2, GLCKIO2, ene, MsIo64 (ASUS/Aura), cpuz154 and CorsairLLAccess
  (Corsair iCUE). PawnIO 2.2.0 driver + LibreHardwareMonitor-based sampler (stevetemp) installed 2026-11-04.
- PSU model, VRM temperature, ambient temperature: UNMEASURED.
- `bcdedit numproc 18` has been set since 2026-10-26 (drops logical CPUs 18-19 = one physical core) except boots where the BCD
  was rebuilt (11-03, one 20-CPU boot 10-31).
- Workload: until 2026-11-17 the machine ran a test lane of RimWorld game jobs (Unity/mono, many mods), dotnet and python
  tools, around the clock; since 2026-11-17 ~19:51Z no game jobs (lane paused for the soak).

## Firmware settings read from NVRAM on 2026-11-20 (UEFI variables, decoded with the 3401 setup forms)
`digest/uefi_cpu_settings_20261120.txt`. Ai Overclock Tuner Auto; ASUS MultiCore Enhancement "Disabled - Enforce All limits";
CPU Core/Cache Voltage **Offset Mode**, sign **+**, offset field raw value **20** (unit not decoded; ASUS steps are 0.005 V, which
would make it +0.100 V); CPU Load-line Calibration Auto; SVID Behavior Auto; AVX ratio offset Auto; HT on; all cores active;
Turbo Mode enabled in firmware. On BIOS 0607 (read 2026-10-31) Ai Overclock Tuner was "Manual" and MCE "Auto".
Windows power plan: PROCTHROTTLEMAX on AC = 99 (turbo off, ~3.6 GHz) since 2026-11-07T16:00Z; 100 before.

## Timeline of observations and changes
- 2026-10-26: Windows python pinned to logical CPU 18 hashed one buffer with sha256 to 60 distinct digests of 60; the other
  19 CPUs gave 1 of 60. openssl sha256 52/100 distinct, sha1 22, blake2b 8; md5 and a scalar sha256 stable; WSL python3 stable
  (WSL not pinned). Turbo off did not fix CPU 18. numproc 18 set.
- 2026-10-27 onward: Windows Application Error 1000 events across unrelated processes (dotnet, python, Defender MsMpEng,
  RimWorld, PowerShell, SearchApp), mostly 0xc0000005; RimWorld also 0xe0000001 (mono abort) and 0xc000001d (illegal
  instruction). `digest/winevents_digest.md` (Application log reaches back to 2026-10-25; System log only to 2026-10-31).
- 2026-10-31 (uptime 5 days): logical CPU 2 alone failed, repeatably: Prime95 FATAL "rounding 0.5, expected < 0.4" at 4K and
  128K FFT; stevecheck 669/849 and 367/548 rounds bad; sha256 60 distinct of 60. Its sibling CPU 3 and the other 16 clean.
  In-OS RAM walk 85 GB (CPU 2 excluded) 0 bad. After a reboot CPU 2 was clean; a 20-CPU boot was clean on all CPUs; 108 GB RAM
  walk 0 bad; Windows Memory Diagnostic basic pass: no errors. Raw logs: `raw/steve_logs/s2..s4*.log, sweep.log, chk.log`.
- ~2026-10-31/11-01: BIOS 0607 -> 3401 (microcode 0xC8 -> 0x100). Samsung 970 NVMe showed 432 bad-block events in 15 min with
  SMART "healthy"; cloned to a Kingston NV3 and removed 2026-11-02. POST took ~5 min after the flash.
- 2026-11-01 02:28Z: the 5-minute watch starts (watch2.ps1 + stevecheck; see "Instruments" below).
- 2026-11-03: one early-boot crash with no dump (first boot from the rebuilt BCD); System 6008 at 19:05Z.
- 2026-11-04 03:40Z-10:00Z: vendor-software A/B: AI Suite, iCUE services, Aura LightingService, CPUID cpuz154 and
  CorsairLLAccess stopped/unloaded (AsIO2/GLCKIO2/ene/MsIo64 stayed loaded, no caller). Three fault windows opened with them
  off (onsets 0.96 h on the boot where the A/B began, 4.46 h and 0.88 h on clean boots). Reverted 10:00Z.
- 2026-11-04 03:3xZ: temperature sampler deployed; from then CYCLE lines carry package/core temps and a vcore reading.
- 2026-11-06 02:55Z: case side removed (open-case from then on).
- 2026-11-06 to 11-07: onsets fell to 0.21-0.30 h on five consecutive boots.
- 2026-11-07 02:20-06:11Z: Windows Memory Diagnostic standard mix, all memory: no errors (event 1201).
- 2026-11-07 15:43Z: Kernel-Power 41 / 6008 (unexpected shutdown at 15:18Z).
- 2026-11-07 16:00Z: turbo off (PROCTHROTTLEMAX 99).
- 2026-11-12 onward: the machine is rebooted every 12 h between jobs; results counted even inside fault windows.
- 2026-11-15 08:57Z boot: lane idle from 13:59Z; first fault at 29.12 h uptime (2026-11-16 14:05Z) with 0 jobs inside.
- 2026-11-17 ~15:28Z (07:28 PST): a person set CPU Core/Cache Voltage to Offset Mode +0.100 V in BIOS; boot 15:32:58Z.
- 2026-11-17 18:52-19:17Z: 6 h Prime95 soak started, stopped by a STOP file written by an agent (32 steps, all PASS).
- 2026-11-17 19:40Z and 19:45Z: two bad watch cycles (CPU 8, then CPU 7), 4.13 h into the post-raise boot, while a RimWorld
  test job was in its deploy/load phase. Reboot 19:51Z.
- 2026-11-18 01:29Z: 72 h Prime95 soak started (task under SYSTEM; one deliberate reboot at 01:34Z; resumes after reboot);
  planned end 2026-11-21 01:29Z. Still running at the time of this package (2026-11-20 ~08:00Z, 54 h into boot 01:39:36Z).

## Instruments (source code is in the package)
- **The 5-minute watch** (`raw/tools_steve_cpu_retest/watch2.ps1`, checker `findings/steve_diag/Program.cs`): every 300 s,
  for each logical CPU in turn, `stevecheck core <cpu> 4` pins a thread to that CPU for 4 s, computes 8 references at start,
  then repeats them; a round differing from the run's own reference is "bad" and the run exits 1. A CYCLE line lists the CPUs
  that exited non-zero (`exits=` gives the codes; -1073741819 = the checker itself crashed with 0xc0000005). Each watcher
  start runs a CONTROL (injected fault must exit 1, clean run 0). The checker uses AVX2 integer ops, FMA/AVX double ops and
  .NET SHA-256; it has no scalar-only control. Per-mismatch detail goes to `watch-chk.log` (first 5 per run).
- **"Fault window"** (fault_monitor.py on another machine): from the first bad cycle of a boot to the end of that boot.
- **Temperature/vcore sampler** stevetemp (`raw/tools_steve_cpu_retest/stevetemp.cs`, LibreHardwareMonitorLib + PawnIO),
  500 ms samples while a cycle's checks run; during the soak the watch's sampler mostly returns "no_output" (the soak runs
  its own sampler). stevetemp opens only LibreHardwareMonitor's CPU hardware (`IsCpuEnabled`, no motherboard/SuperIO), so
  vcore_v is LHM's Intel-CPU "CPU Core" voltage, which we believe LHM derives from the CPU's own MSR, i.e. a VID request rather
  than the voltage the VRM delivers [guess ~75%]. Whether a BIOS offset would show in it is UNMEASURED.
- **The soak** (`raw/tools_steve_cpu_retest/steve_cpu_soak.ps1`): Prime95 pinned to one logical CPU for 45 s, each CPU in
  turn, then all-core 90 s; a step FAILs on a Prime95 error line, a WHEA event, or Prime95 dying before the step ends
  ("prime95_died_early"). CONTROL at each start: injected error and injected kill must both be seen.
- **WHEA**: zero WHEA-Logger events in the System log (which reaches back only to 2026-10-31).

## Numbers (all [measured], from the digests)
- Watch cycles by era: turbo on (to 11-07 16:00Z) 1,292 cycles / 426 bad; turbo off before the raise 2,857 / 1,533 bad;
  after the raise 770 / 2 bad (`digest/watch_era_sensors.txt`, `digest/watch_per_boot.tsv`).
- Sensor readings on watch cycles: vcore mean 1.312 V turbo on; 1.063 V turbo off pre-raise (idle boots ~1.026-1.029 V, with
  13% of cycles at >1.2 V); 1.026-1.031 V post-raise. Hottest core mean 57.9 / 44.2 / 42.7 C.
- Within the turbo-off pre-raise era: cycles with vcore <= 1.2 V were bad 51% of the time (1,273/2,487); cycles > 1.2 V
  70% (258/368).
- Soak (72 h run so far): 3,978 steps, 3 FAIL, all "prime95_died_early" (cpu 8, 6, 8), 0 Prime95 error lines, 0 WHEA; vcore
  0.979-1.035 V, hottest core 37-57 C (`digest/soak_digest.md`). No Application Error event for prime95.exe at those times.
- Application Error 1000 events per day: 3-42 per day 2026-10-25..11-16; 3 on 11-17 (all before the raise); 0 since the
  raise (2026-11-17 15:28Z to 2026-11-20 ~08:00Z). The machine ran no game jobs after 11-17 ~19:51Z.
- Test jobs: 1,328 results; INVALID 199 of 513 jobs that overlapped a fault window vs 76 of 815 that did not
  (`digest/testq_outcome_vs_window.txt`).
- Checker mismatch analysis: `digest/chk_mismatch_analysis.md`.
