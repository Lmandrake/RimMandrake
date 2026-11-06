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

## What the fault does to jobs (MEASURED, one stack)

A modcheck run that dies "exit 5, no sheet" is python.exe killed by an access violation in pure CPython code
(`ast.parse`), inside a fault window: `J20261103T233438Z-aa0482` in `F20261103T195921Z`. Since the 10-31 reboot, 1 of
42 in-window jobs crashed and 0 of 57 outside. Census: `infrastructure/state/evidence/MODCHECK_DIAGNOSE_EXIT_FIVE_NO_SHEET.md`.

A cold load can die in the mono JIT (`0xE0000001`, RaiseException under `mono_unity_jit_cleanup`) before the monitor
reads bad: 11-03 and 11-06, each 6-7 min before first_bad and outside the window as recorded, so ingest files a repair
item. Table and odds: `infrastructure/state/evidence/HARNESS_REPAIR_CAUSE_4F477502.md`.

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

**FALSIFIED (MEASURED 2026-11-04).** Three fault windows opened with the callers off
(`python3 src/RimMandrake/Utils/testq/fault_monitor.py report`):

| window | boot | onset | first bad | CPUs | hottest core at onset |
|---|---|---|---|---|---|
| F20261104T024513Z | 02:45:13Z (A/B began mid-boot) | 0.96 h | 03:43:02Z | 2 | UNMEASURED |
| F20261104T035722Z | 03:57:22Z, callers off from boot | 4.46 h | 08:25:14Z | 16 | 61 °C, vcore max 1.302 V |
| F20261104T083546Z | 08:35:46Z, callers off from boot | 0.88 h | 09:28:37Z | 16 | 56 °C, vcore max 1.315 V |

The first window opened on the boot where the A/B started, so state set before 03:40Z could explain it. The other two
opened on clean boots with the callers off. A read at 2026-11-04T10:00Z (boot 09:38:00Z) showed every caller still
Disabled and stopped, `cpuz154` and `CorsairLLAccess` not loaded, and no SCM start event for them since the disable
(`D:\ClaudeWork\rimmandrake\steve_diag\driver_ab\verify_g3.out`). Onsets with the callers off (4.46 h, 0.88 h) fall
inside the baseline range. **Software that calls these vendor drivers is not the cause.**

Not excluded: the System-start drivers `AsIO2`, `GLCKIO2`, `ene` and `MsIo64` stayed loaded, with no known caller
running. `iCUE.exe`, the user-mode app, kept running, but it reaches hardware only through the disabled services.
Heat at onset is ordinary (56–61 °C), so thermal runaway is not the trigger. **Hardware is the lead: the CPU or the
board/VRM.** Next discriminators: run at stock settings with XMP/MCE (multicore enhancement) off and a small negative
ratio or a fixed vcore, or swap the CPU.

Reverted 2026-11-04T10:00:58Z: original start modes restored, services running again
(`D:\ClaudeWork\rimmandrake\steve_diag\driver_ab\revert_g3b.out`). 🔴 `C:\SteveDesktop\diag\driver_ab_revert.ps1`
does nothing on Windows PowerShell 5 (the JSON array arrives as one object). Use `driver_ab\revert2.ps1` instead.
