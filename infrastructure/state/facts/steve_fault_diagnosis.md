# SteveDesktop's uptime SIMD fault: what is measured, what is not

Item `STEVE_CRASHES_DIAGNOSE_DEFENDER_FALLS_TOO`. Machine: i9-10900K, ROG STRIX Z490-G, 4×32 GB F4-2666C18.
Live instrument: `python3 src/RimMandrake/Utils/testq/fault_monitor.py report` (timer `rm-steve-fault.timer`,
state `D:\ClaudeWork\rimmandrake\testq\fault_state.json`). Raw evidence: `D:\ClaudeWork\rimmandrake\steve_diag\`.

## The RAM test: done, clean (MEASURED 2026-10-31)

- Windows Memory Diagnostic, Basic, 1 pass: no errors (events 1101/1201, 18:57Z).
- In-OS RAM walks: 85 GB (faulty CPU 2 excluded) 0 bad; 108 GB on a fresh 20-CPU boot 0 bad.
- No WHEA events. RAM is clean within that coverage; it is not the fault's cause on present evidence.

## The fault's shape (MEASURED)

- Wrong SIMD results (Prime95 rounding, `stevecheck`, sha256 distinct digests) on a logical CPU, acquired
  during uptime, held until a reboot, cleared by every reboot so far.
- 10-26 it was CPU 18; 10-31 CPU 2 under `numproc 18`; so masking a core cures nothing.
- After the BIOS 3401 flash (new microcode) onsets came SOONER: 3.30, 0.88, 2.88 h into a boot (fault_monitor
  windows F20261101T035219Z, F20261101T164245Z, F20261103T195921Z), against ~5 days once before the flash. Inside a
  window the bad CPU wanders cycle to cycle, with clean cycles between, until the reboot.
- So old microcode is ruled out as the sole cause, and "one dead core" does not fit.

## Hypothesis under test: vendor software holding CPU state

A fault that persists until reboot and spans many cores fits a machine-wide setting that a reboot resets (MSRs,
voltage/ratio offsets, SMBus/IO writes) better than a marginal core. Steve runs several ring-0 MSR/IO drivers and
their callers: ASUS AI Suite (`asComSvc`, `AsIO2`), Corsair iCUE (`CorsairService`, `CpuIdRemote64` via the
CPUID `cpuz154` driver, `CorsairLLAccess`), Aura `LightingService` (`GLCKIO2`, `ene`), `MsIo64`.

**A/B started 2026-11-04T03:40:20Z** (boot 02:45:13Z, clean at that time): the callers above were set Disabled and
stopped; `cpuz154` and `CorsairLLAccess` unloaded. Kernel drivers with System start stay loaded but have no caller.
The only Corsair device is a keyboard (no AIO), so cooling falls back to BIOS fan curves. Original start modes:
`C:\SteveDesktop\diag\driver_ab_original.json`; revert: `C:\SteveDesktop\diag\driver_ab_revert.ps1`.

Reading it: baseline onsets on BIOS 3401 are all ≤ 3.3 h. A fault window opening after 03:40:20Z falsifies the
vendor-software hypothesis (hardware stays the lead: CPU or VRM/board). 12 h or more of clean uptime with the
callers off is evidence for it.

## Result

PENDING (the A/B is running).
